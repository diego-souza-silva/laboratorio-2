"""Construção dos gráficos Plotly do dashboard (tema escuro, estilo executivo)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from data_processing import ETAPAS_CRM, ETAPAS_CRM_LABEL, GRUPO_AB_ORDEM
from utils import formatar_numero, formatar_percentual

CORES = {
    "disparado": "#8B93B8",
    "enviado": "#3DA9FC",
    "entregue": "#2ECC71",
    "falhou": "#FF5C5C",
    "pendente": "#F5A623",
}

FUNDO_PAPEL = "rgba(0,0,0,0)"
FUNDO_PLOT = "rgba(0,0,0,0)"
COR_FONTE = "#E5E9F0"
COR_GRADE = "rgba(255,255,255,0.08)"

NOME_CURTO_UTM = {
    "20260725-abandonocarrinhodia25-kolmeya": "Abandono Carrinho",
    "20260725-engajadodia25-kolmeya": "Engajado",
    "20260725-topofunildia25-kolmeya": "Topo de Funil",
    "20260725-cadastradodia25-kolmeya": "Cadastrado",
}

GRUPO_AB_LABEL = {
    "P1_MAXIMA": "P1 · Máxima",
    "P2_ALTA": "P2 · Alta",
    "P3_MEDIA": "P3 · Média",
    "P4_BAIXA": "P4 · Baixa",
    "Não Classificado": "Não Classificado",
}


def nome_curto(utm: str) -> str:
    return NOME_CURTO_UTM.get(utm, utm)


def _layout_base(fig: go.Figure, titulo: str | None = None, altura: int = 340) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=FUNDO_PAPEL,
        plot_bgcolor=FUNDO_PLOT,
        font=dict(color=COR_FONTE, family="Inter, Segoe UI, sans-serif", size=12),
        title=dict(text=titulo, font=dict(size=15, color=COR_FONTE)) if titulo else None,
        margin=dict(l=10, r=10, t=45 if titulo else 15, b=10),
        height=altura,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#1E2430", font_color=COR_FONTE, bordercolor=COR_GRADE),
    )
    fig.update_xaxes(gridcolor=COR_GRADE, zeroline=False)
    fig.update_yaxes(gridcolor=COR_GRADE, zeroline=False)
    return fig


def grafico_funil(etapas: list[dict]) -> go.Figure:
    nomes = [e["etapa"] for e in etapas]
    valores = [e["quantidade"] for e in etapas]
    textos = [
        f"<b>{formatar_numero(e['quantidade'])}</b><br>"
        f"{formatar_percentual(e['percentual_base'])} da base"
        for e in etapas
    ]
    cores = [CORES["disparado"], CORES["enviado"], CORES["entregue"], CORES["falhou"]]

    fig = go.Figure(
        go.Funnel(
            y=nomes,
            x=valores,
            text=textos,
            textposition="inside",
            textinfo="text",
            marker=dict(color=cores, line=dict(color="#0F1420", width=1)),
            connector=dict(line=dict(color=COR_GRADE, width=1)),
            customdata=[[e["conversao"], e["perda"]] for e in etapas],
            hovertemplate="<b>%{y}</b><br>Quantidade: %{x:,}<br>Conversão vs etapa anterior: "
            "%{customdata[0]:.1f}%<br>Perda vs etapa anterior: %{customdata[1]:.1f}%<extra></extra>",
        )
    )
    return _layout_base(fig, altura=360)


def grafico_evolucao_horaria(df: pd.DataFrame) -> go.Figure:
    validos = df.dropna(subset=["timestamp"])
    if validos.empty:
        return _layout_base(go.Figure(), "Evolução por Hora (sem dados no período)")

    serie = (
        validos[validos["enviado"] == 1]
        .set_index("timestamp")
        .resample("h")["enviado"]
        .sum()
    )
    fig = go.Figure(
        go.Scatter(
            x=serie.index, y=serie.values, mode="lines+markers",
            line=dict(color=CORES["enviado"], width=2.5, shape="spline"),
            marker=dict(size=5),
            fill="tozeroy", fillcolor="rgba(61,169,252,0.12)",
            hovertemplate="%{x|%d/%m %Hh}<br>Enviados: %{y:,}<extra></extra>",
        )
    )
    return _layout_base(fig, "Evolução por Hora — Quantidade Enviada")


def grafico_evolucao_diaria(df: pd.DataFrame) -> go.Figure:
    validos = df.dropna(subset=["data"])
    if validos.empty:
        return _layout_base(go.Figure(), "Evolução Diária (sem dados no período)")

    agrupado = validos.groupby("data")[["enviado", "entregue", "falhou"]].sum().reset_index()
    fig = go.Figure()
    for coluna, rotulo in [("enviado", "Enviado"), ("entregue", "Entregue"), ("falhou", "Falhou")]:
        fig.add_trace(go.Bar(
            x=agrupado["data"], y=agrupado[coluna], name=rotulo,
            marker_color=CORES[coluna],
        ))
    fig.update_layout(barmode="group")
    return _layout_base(fig, "Evolução Diária")


def grafico_volume_utm(df: pd.DataFrame) -> go.Figure:
    agrupado = df.groupby("utm_campaign")[["disparado", "enviado", "entregue", "falhou"]].sum()
    agrupado = agrupado.reindex(df.groupby("utm_campaign")["disparado"].sum().sort_values(ascending=False).index)
    rotulos = [nome_curto(u) for u in agrupado.index]

    fig = go.Figure()
    for coluna, rotulo, chave_cor in [
        ("disparado", "Disparado", "disparado"), ("enviado", "Enviado", "enviado"),
        ("entregue", "Entregue", "entregue"), ("falhou", "Falhou", "falhou"),
    ]:
        fig.add_trace(go.Bar(x=rotulos, y=agrupado[coluna], name=rotulo, marker_color=CORES[chave_cor]))
    fig.update_layout(barmode="group")
    return _layout_base(fig, "Volume por Campanha (UTM)")


def grafico_status_sms(kpis: dict) -> go.Figure:
    categorias = ["Disparado", "Enviado", "Entregue", "Falhou"]
    valores = [kpis["disparado"], kpis["enviado"], kpis["entregue"], kpis["falhou"]]
    cores = [CORES["disparado"], CORES["enviado"], CORES["entregue"], CORES["falhou"]]

    fig = go.Figure(
        go.Bar(
            x=categorias, y=valores, marker_color=cores,
            text=[formatar_numero(v) for v in valores], textposition="outside",
            hovertemplate="%{x}: %{y:,}<extra></extra>",
        )
    )
    fig.update_yaxes(range=[0, max(valores) * 1.18 if valores else 1])
    return _layout_base(fig, "Status dos SMS")


def grafico_ranking_campanhas(agregado: pd.DataFrame) -> go.Figure:
    ordenado = agregado.sort_values("total_disparado", ascending=True)
    rotulos = [nome_curto(u) for u in ordenado["utm_campaign"]]

    fig = go.Figure(
        go.Bar(
            y=rotulos, x=ordenado["total_disparado"], orientation="h",
            marker_color=CORES["disparado"],
            text=[formatar_numero(v) for v in ordenado["total_disparado"]],
            textposition="outside",
            hovertemplate="%{y}<br>Disparado: %{x:,}<extra></extra>",
        )
    )
    return _layout_base(fig, "Ranking de Campanhas por Volume")


def grafico_taxa_entrega_campanha(agregado: pd.DataFrame) -> go.Figure:
    ordenado = agregado.sort_values("taxa_entrega", ascending=True)
    rotulos = [nome_curto(u) for u in ordenado["utm_campaign"]]

    fig = go.Figure(
        go.Bar(
            y=rotulos, x=ordenado["taxa_entrega"], orientation="h",
            marker_color=CORES["entregue"],
            text=[formatar_percentual(v) for v in ordenado["taxa_entrega"]],
            textposition="outside",
            hovertemplate="%{y}<br>Taxa de Entrega: %{x:.1f}%<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, 100])
    return _layout_base(fig, "Taxa de Entrega por Campanha")


def grafico_volume_grupo_ab(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _layout_base(go.Figure(), "Volume por Grupo AB (sem dados no período)")

    ordem = [g for g in GRUPO_AB_ORDEM if g in df["grupo_ab"].unique()]
    agrupado = df.groupby("grupo_ab")[["disparado", "enviado", "entregue", "falhou"]].sum().reindex(ordem)

    fig = go.Figure()
    for coluna, rotulo, chave_cor in [
        ("disparado", "Disparado", "disparado"), ("enviado", "Enviado", "enviado"),
        ("entregue", "Entregue", "entregue"), ("falhou", "Falhou", "falhou"),
    ]:
        fig.add_trace(go.Bar(x=agrupado.index, y=agrupado[coluna], name=rotulo, marker_color=CORES[chave_cor]))
    fig.update_layout(barmode="group")
    return _layout_base(fig, "Volume por Grupo AB (Segmentação de Propensão)")


def grafico_taxa_entrega_grupo_ab(agregado: pd.DataFrame) -> go.Figure:
    if agregado.empty:
        return _layout_base(go.Figure(), "Taxa de Entrega por Grupo AB (sem dados no período)")

    ordenado = agregado.iloc[::-1]
    fig = go.Figure(
        go.Bar(
            y=ordenado["grupo_ab"], x=ordenado["taxa_entrega"], orientation="h",
            marker_color=CORES["entregue"],
            text=[formatar_percentual(v) for v in ordenado["taxa_entrega"]],
            textposition="outside",
            hovertemplate="%{y}<br>Taxa de Entrega: %{x:.1f}%<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, 100])
    return _layout_base(fig, "Taxa de Entrega por Grupo AB")


def formatar_tabela_grupo_ab(agregado: pd.DataFrame) -> list[dict]:
    registros = []
    for _, linha in agregado.iterrows():
        registros.append({
            "Grupo AB": linha["grupo_ab"],
            "Total Disparado": formatar_numero(linha["total_disparado"]),
            "Total Enviado": formatar_numero(linha["total_enviado"]),
            "Total Entregue": formatar_numero(linha["total_entregue"]),
            "Total Falhado": formatar_numero(linha["total_falhado"]),
            "Taxa de Envio": formatar_percentual(linha["taxa_envio"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        })
    return registros


def grafico_funil_crm(crm_agregado: pd.DataFrame) -> go.Figure:
    if crm_agregado.empty:
        return _layout_base(go.Figure(), "Conversão pós-SMS (sem dados no período)")

    totais = crm_agregado[ETAPAS_CRM].sum()
    rotulos = [ETAPAS_CRM_LABEL[e] for e in ETAPAS_CRM]

    fig = go.Figure(
        go.Funnel(
            y=rotulos, x=totais.values,
            textinfo="value+percent initial",
            marker=dict(color=["#8B93B8", "#3DA9FC", "#F5A623", "#2ECC71"]),
            connector=dict(line=dict(color=COR_GRADE, width=1)),
        )
    )
    return _layout_base(fig, "Funil de Conversão Pós-SMS (CRM)", altura=360)


def grafico_crm_por_campanha(crm_agregado: pd.DataFrame) -> go.Figure:
    if crm_agregado.empty:
        return _layout_base(go.Figure(), "Conversão por Campanha (sem dados no período)")

    rotulos = [nome_curto(u) for u in crm_agregado["utm_campaign"]]
    fig = go.Figure()
    cores_etapa = {"home": "#8B93B8", "auth": "#3DA9FC", "oferta": "#F5A623", "acordo": "#2ECC71"}
    for etapa in ETAPAS_CRM:
        fig.add_trace(go.Bar(
            x=rotulos, y=crm_agregado[etapa], name=ETAPAS_CRM_LABEL[etapa],
            marker_color=cores_etapa[etapa],
        ))
    fig.update_layout(barmode="group")
    return _layout_base(fig, "Ações de CRM por Campanha")


def grafico_crm_por_grupo_ab(crm_agregado: pd.DataFrame) -> go.Figure:
    if crm_agregado.empty:
        return _layout_base(go.Figure(), "Conversão por Grupo AB (sem dados no período)")

    ordem = [g for g in GRUPO_AB_ORDEM if g in crm_agregado["grupo_ab"].values]
    crm_agregado = crm_agregado.set_index("grupo_ab").reindex(ordem).reset_index()

    fig = go.Figure()
    cores_etapa = {"home": "#8B93B8", "auth": "#3DA9FC", "oferta": "#F5A623", "acordo": "#2ECC71"}
    for etapa in ETAPAS_CRM:
        fig.add_trace(go.Bar(
            x=crm_agregado["grupo_ab"], y=crm_agregado[etapa], name=ETAPAS_CRM_LABEL[etapa],
            marker_color=cores_etapa[etapa],
        ))
    fig.update_layout(barmode="group")
    return _layout_base(fig, "Ações de CRM por Grupo AB")


def formatar_tabela_executiva(agregado: pd.DataFrame) -> list[dict]:
    registros = []
    for _, linha in agregado.iterrows():
        registros.append({
            "UTM": nome_curto(linha["utm_campaign"]),
            "Total Disparado": formatar_numero(linha["total_disparado"]),
            "Total Enviado": formatar_numero(linha["total_enviado"]),
            "Total Entregue": formatar_numero(linha["total_entregue"]),
            "Total Falhado": formatar_numero(linha["total_falhado"]),
            "Taxa de Envio": formatar_percentual(linha["taxa_envio"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        })
    return registros
