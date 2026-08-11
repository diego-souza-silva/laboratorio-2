"""Construção dos gráficos Plotly do dashboard (tema escuro, estilo executivo)."""
from __future__ import annotations

import re

import pandas as pd
import plotly.graph_objects as go

from data_processing import (
    CANAL_CUSTO_LABEL, ETAPAS_CRM, ETAPAS_CRM_LABEL, FORNECEDOR_CUSTO_LABEL, GRUPO_AB_ORDEM,
    GRUPO_ESTRATEGICO_ORDEM, SITUACOES_WHATSAPP,
)
from utils import formatar_numero, formatar_percentual, taxa

CORES = {
    "disparado": "#8B93B8",
    "enviado": "#3DA9FC",
    "entregue": "#2ECC71",
    "falhou": "#FF5C5C",
    "pendente": "#F5A623",
}

# Funil combinado (Disparo + CRM): continua as cores do funil de entrega direto nas
# cores do funil de negociação (Home=cinza, Autenticação=azul, Oferta=laranja, Acordo=verde).
CORES_FUNIL_COMBINADO_SMS = ["#8B93B8", "#3DA9FC", "#2ECC71", "#8B93B8", "#3DA9FC", "#F5A623", "#2ECC71"]
CORES_FUNIL_COMBINADO_WHATSAPP = [
    "#8B93B8", "#3DA9FC", "#2ECC71", "#0FA968", "#8B93B8", "#3DA9FC", "#F5A623", "#2ECC71",
]

FUNDO_PAPEL = "rgba(0,0,0,0)"
FUNDO_PLOT = "rgba(0,0,0,0)"
COR_FONTE = "#E5E9F0"
COR_GRADE = "rgba(255,255,255,0.08)"

NOME_LEGIVEL_SLUG = {
    "abandonocarrinho": "Abandono Carrinho",
    "engajado": "Engajado",
    "topofunil": "Topo de Funil",
    "cadastrado": "Cadastrado",
}

_PADRAO_UTM_DIA = re.compile(r"^\d{4}(\d{2})(\d{2})-(.+?)dia\d+-\w+$", re.IGNORECASE)
_PADRAO_UTM_SIMPLES = re.compile(r"^\d{4}(\d{2})(\d{2})-(.+)-(\w+)$", re.IGNORECASE)

GRUPO_AB_LABEL = {
    "P1_MAXIMA": "P1 · Máxima",
    "P2_ALTA": "P2 · Alta",
    "P3_MEDIA": "P3 · Média",
    "P4_BAIXA": "P4 · Baixa",
    "Não Classificado": "Não Classificado",
}

GRUPO_ESTRATEGICO_LABEL = {
    "2_ABANDONO_CARRINHO": "Abandono Carrinho",
    "3_CADASTRADO": "Cadastrado",
    "4_ENGAJADO": "Engajado",
    "5_TOPO_FUNIL": "Topo de Funil",
    "Não Classificado": "Não Classificado",
}


def nome_curto(utm: str) -> str:
    """Rótulo legível para uma UTM. Reconhece o padrão AAAAMMDD-{slug}diaDD-{plataforma}
    e, como fallback, AAAAMMDD-{slug}-{plataforma} (independente da data), então novas
    campanhas diárias de qualquer canal já saem com nome bonito sem precisar editar
    código — só a data muda no rótulo."""
    match_dia = _PADRAO_UTM_DIA.match(utm)
    if match_dia:
        mes, dia, slug = match_dia.groups()
        rotulo = NOME_LEGIVEL_SLUG.get(slug.lower(), slug)
        return f"{rotulo} ({dia}/{mes})"

    match_simples = _PADRAO_UTM_SIMPLES.match(utm)
    if match_simples:
        mes, dia, slug, plataforma = match_simples.groups()
        rotulo = NOME_LEGIVEL_SLUG.get(slug.lower(), slug)
        return f"{rotulo} ({dia}/{mes}, {plataforma})"

    return utm


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


def grafico_funil(
    etapas: list[dict], cores: list[str] | None = None,
    titulo: str | None = None, altura: int = 360, textposition: str = "inside",
    modo_percentual: str = "base",
) -> go.Figure:
    """`modo_percentual="base"` (padrão, usado na aba Funil Geral) mostra o % de cada
    etapa sobre a etapa inicial do funil; `modo_percentual="etapa"` (usado na aba
    Conversão Pós-Contato) mostra o % sobre a etapa imediatamente anterior — mais
    representativo da conversão entre estágios do que da base total."""
    nomes = [e["etapa"] for e in etapas]
    valores = [e["quantidade"] for e in etapas]
    if modo_percentual == "etapa":
        textos = [
            f"<b>{formatar_numero(e['quantidade'])}</b><br>"
            f"{formatar_percentual(e['conversao'])} da etapa anterior"
            for e in etapas
        ]
    else:
        textos = [
            f"<b>{formatar_numero(e['quantidade'])}</b><br>"
            f"{formatar_percentual(e['percentual_base'])} da base"
            for e in etapas
        ]
    cores = cores or [CORES["disparado"], CORES["enviado"], CORES["entregue"], CORES["falhou"]]

    fig = go.Figure(
        go.Funnel(
            y=nomes,
            x=valores,
            text=textos,
            textposition=textposition,
            textinfo="text",
            marker=dict(color=cores, line=dict(color="#0F1420", width=1)),
            connector=dict(line=dict(color=COR_GRADE, width=1)),
            customdata=[[e["conversao"], e["perda"]] for e in etapas],
            hovertemplate="<b>%{y}</b><br>Quantidade: %{x:,}<br>Conversão vs etapa anterior: "
            "%{customdata[0]:.1f}%<br>Perda vs etapa anterior: %{customdata[1]:.1f}%<extra></extra>",
        )
    )
    return _layout_base(fig, titulo, altura=altura)


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


def grafico_status_sms(kpis: dict, titulo: str = "Status dos SMS") -> go.Figure:
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
    return _layout_base(fig, titulo)


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


def _texto_valor_percentual(valores: pd.Series, base: pd.Series) -> list[str]:
    return [
        f"{formatar_numero(v)} ({formatar_percentual(taxa(v, b))})"
        for v, b in zip(valores, base)
    ]


def grafico_volume_grupo_ab(df: pd.DataFrame, crm_agregado: pd.DataFrame | None = None) -> go.Figure:
    """Horizontal, um grupo de barras por grupo_ab. `crm_agregado` (opcional, formato
    de `agregar_crm_por_grupo_ab`) acrescenta o funil de negociação (Home/Autenticação/
    Oferta/Acordo) como barras extras dentro do mesmo gráfico, lado a lado com
    Disparado/Enviado/Entregue/Falhou. Cada barra mostra o volume e o percentual em
    relação à etapa anterior (Enviado/Disparado, Entregue/Enviado, Falhou/Enviado,
    Home/Entregue, Autenticação/Home, Oferta/Autenticação, Acordo/Oferta)."""
    if df.empty:
        return _layout_base(go.Figure(), "Volume por Grupo AB (sem dados no período)")

    ordem = [g for g in GRUPO_AB_ORDEM if g in df["grupo_ab"].unique()]
    agrupado = df.groupby("grupo_ab")[["disparado", "enviado", "entregue", "falhou"]].sum().reindex(ordem)

    fig = go.Figure()
    n_series = 4
    for coluna, rotulo, chave_cor, base in [
        ("disparado", "Disparado", "disparado", None),
        ("enviado", "Enviado", "enviado", agrupado["disparado"]),
        ("entregue", "Entregue", "entregue", agrupado["enviado"]),
        ("falhou", "Falhou", "falhou", agrupado["enviado"]),
    ]:
        valores = agrupado[coluna]
        textos = [formatar_numero(v) for v in valores] if base is None else _texto_valor_percentual(valores, base)
        fig.add_trace(go.Bar(
            y=agrupado.index, x=valores, name=rotulo, marker_color=CORES[chave_cor],
            orientation="h", text=textos, textposition="outside",
        ))

    if crm_agregado is not None and not crm_agregado.empty:
        n_series = 8
        cores_etapa = {"home": "#8B93B8", "auth": "#3DA9FC", "oferta": "#F5A623", "acordo": "#2ECC71"}
        crm_alinhado = crm_agregado.set_index("grupo_ab").reindex(ordem).fillna(0)
        bases_etapa = {
            "home": agrupado["entregue"], "auth": crm_alinhado["home"],
            "oferta": crm_alinhado["auth"], "acordo": crm_alinhado["oferta"],
        }
        for etapa in ETAPAS_CRM:
            valores = crm_alinhado[etapa]
            fig.add_trace(go.Bar(
                y=agrupado.index, x=valores, name=ETAPAS_CRM_LABEL[etapa],
                marker_color=cores_etapa[etapa], marker_pattern_shape="/", orientation="h",
                text=_texto_valor_percentual(valores, bases_etapa[etapa]), textposition="outside",
            ))

    fig.update_layout(barmode="group")
    altura = max(380, 34 * n_series * len(agrupado) + 100)
    return _layout_base(fig, "Volume por Grupo AB (Segmentação de Propensão)", altura=altura)


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


def grafico_volume_grupo_estrategico(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _layout_base(go.Figure(), "Volume por Grupo Estratégico (sem dados no período)")

    ordem = [g for g in GRUPO_ESTRATEGICO_ORDEM if g in df["grupo_estrategico"].unique()]
    agrupado = df.groupby("grupo_estrategico")[["disparado", "enviado", "entregue", "falhou"]].sum().reindex(ordem)
    rotulos = [GRUPO_ESTRATEGICO_LABEL.get(g, g) for g in agrupado.index]

    fig = go.Figure()
    for coluna, rotulo, chave_cor in [
        ("disparado", "Disparado", "disparado"), ("enviado", "Enviado", "enviado"),
        ("entregue", "Entregue", "entregue"), ("falhou", "Falhou", "falhou"),
    ]:
        fig.add_trace(go.Bar(x=rotulos, y=agrupado[coluna], name=rotulo, marker_color=CORES[chave_cor]))
    fig.update_layout(barmode="group")
    return _layout_base(fig, "Volume por Grupo Estratégico")


def grafico_taxa_entrega_grupo_estrategico(agregado: pd.DataFrame) -> go.Figure:
    if agregado.empty:
        return _layout_base(go.Figure(), "Taxa de Entrega por Grupo Estratégico (sem dados no período)")

    ordenado = agregado.iloc[::-1]
    rotulos = [GRUPO_ESTRATEGICO_LABEL.get(g, g) for g in ordenado["grupo_estrategico"]]
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
    return _layout_base(fig, "Taxa de Entrega por Grupo Estratégico")


def formatar_tabela_grupo_estrategico(agregado: pd.DataFrame) -> list[dict]:
    registros = []
    for _, linha in agregado.iterrows():
        registros.append({
            "Grupo Estratégico": GRUPO_ESTRATEGICO_LABEL.get(linha["grupo_estrategico"], linha["grupo_estrategico"]),
            "Total Disparado": formatar_numero(linha["total_disparado"]),
            "Total Enviado": formatar_numero(linha["total_enviado"]),
            "Total Entregue": formatar_numero(linha["total_entregue"]),
            "Total Falhado": formatar_numero(linha["total_falhado"]),
            "Taxa de Envio": formatar_percentual(linha["taxa_envio"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        })
    return registros


def _truncar_frase(frase: str, limite: int = 90) -> str:
    if not isinstance(frase, str):
        return ""
    return frase if len(frase) <= limite else frase[: limite - 1].rstrip() + "…"


def grafico_taxa_entrega_frase(agregado: pd.DataFrame) -> go.Figure:
    if agregado.empty:
        return _layout_base(go.Figure(), "Taxa de Entrega por Frase (sem dados no período)")

    ordenado = agregado.sort_values("taxa_entrega")
    rotulos = [_truncar_frase(f, 55) for f in ordenado["frase_norm"]]
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
    altura = max(280, 70 * len(ordenado))
    return _layout_base(fig, "Taxa de Entrega por Frase (SMS)", altura=altura)


def _valor_com_percentual(valor, base) -> str:
    """Formata "quantidade (percentual)" — percentual em relação a `base` (a etapa
    anterior); `base=None` mostra 100% (etapa inicial de uma sequência)."""
    numero = formatar_numero(valor)
    percentual = formatar_percentual(100.0 if base is None else taxa(valor, base))
    return f"{numero} ({percentual})"


def formatar_tabela_frase(agregado: pd.DataFrame) -> list[dict]:
    tem_crm = "acordo" in agregado.columns
    registros = []
    for _, linha in agregado.iterrows():
        campanhas = linha.get("campanhas") or []
        registro = {
            "Frase (modelo)": _truncar_frase(linha["frase_norm"], 140),
            "Campanha(s)": ", ".join(nome_curto(u) for u in campanhas),
            "Total Disparado": formatar_numero(linha["total_disparado"]),
            "Total Enviado": formatar_numero(linha["total_enviado"]),
            "Total Entregue": formatar_numero(linha["total_entregue"]),
            "Total Falhado": formatar_numero(linha["total_falhado"]),
            "Taxa de Envio": formatar_percentual(linha["taxa_envio"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        }
        if tem_crm:
            home, auth, oferta = linha["home"], linha["auth"], linha["oferta"]
            registro["Home"] = _valor_com_percentual(home, linha["total_entregue"])
            registro["Autenticação"] = _valor_com_percentual(auth, home)
            registro["Oferta"] = _valor_com_percentual(oferta, auth)
            registro["Acordo (resultado final)"] = _valor_com_percentual(linha["acordo"], oferta)
        registros.append(registro)
    return registros


_NOMES_SITUACAO_WHATSAPP = {
    "Entregue": "Entregue (não lido)", "Lido": "Lido", "Enviado": "Pendente",
    "Nao Entregue": "Não Entregue", "Nao Enviado": "Não Enviado",
}
_CORES_SITUACAO_WHATSAPP = {
    "Entregue": CORES["entregue"], "Lido": "#2ECC71", "Enviado": CORES["pendente"],
    "Nao Entregue": CORES["falhou"], "Nao Enviado": "#8B93B8",
}

_CORES_RESULTADO_RESPOSTA_AIRYS = {
    "Respondeu": "#3DA9FC",
    "Interesse em Negociação": "#2ECC71",
    "Opt-out Confirmado": "#F5A623",
    "Negativo / Reclamação": "#FF5C5C",
    "Sem Resposta na Janela": "#8B93B8",
    "Sem Retorno": "#8B93B8",
}


def grafico_resultado_resposta_airys(agregado: pd.DataFrame) -> go.Figure:
    if agregado.empty:
        return _layout_base(go.Figure(), "Resultado da Resposta (sem dados no período)")

    ordenado = agregado.sort_values("quantidade", ascending=True)
    cores = [_CORES_RESULTADO_RESPOSTA_AIRYS.get(r, "#8B93B8") for r in ordenado["resultado_resposta_norm"]]
    fig = go.Figure(
        go.Bar(
            y=ordenado["resultado_resposta_norm"], x=ordenado["quantidade"], orientation="h",
            marker_color=cores,
            text=[formatar_numero(v) for v in ordenado["quantidade"]], textposition="outside",
            hovertemplate="%{y}: %{x:,}<extra></extra>",
        )
    )
    altura = max(280, 60 * len(ordenado))
    return _layout_base(fig, "Resultado da Resposta (Airys)", altura=altura)


def grafico_status_mensagem_whatsapp(agregado: pd.DataFrame, rotulo_canal: str = "WhatsApp") -> go.Figure:
    if agregado.empty:
        return _layout_base(go.Figure(), "Status de Entrega por Mensagem (sem dados no período)")

    ordenado = agregado.sort_values("taxa_entrega")
    rotulos = [_truncar_frase(m, 55) for m in ordenado["mensagem_norm"]]
    fig = go.Figure()
    for status in SITUACOES_WHATSAPP:
        fig.add_trace(go.Bar(
            y=rotulos, x=ordenado[status], name=_NOMES_SITUACAO_WHATSAPP[status],
            orientation="h", marker_color=_CORES_SITUACAO_WHATSAPP[status],
        ))
    fig.update_layout(barmode="stack")
    altura = max(280, 70 * len(ordenado))
    return _layout_base(fig, f"Status de Entrega por Mensagem ({rotulo_canal})", altura=altura)


def grafico_crm_por_mensagem_whatsapp(agregado: pd.DataFrame, rotulo_canal: str = "WhatsApp") -> go.Figure:
    tem_crm = "acordo" in agregado.columns
    if agregado.empty or not tem_crm:
        return _layout_base(go.Figure(), "Resultado de CRM por Mensagem (sem dados no período)")

    ordenado = agregado.sort_values("acordo")
    rotulos = [_truncar_frase(m, 55) for m in ordenado["mensagem_norm"]]
    fig = go.Figure()
    cores_etapa = {"home": "#8B93B8", "auth": "#3DA9FC", "oferta": "#F5A623", "acordo": "#2ECC71"}
    for etapa in ETAPAS_CRM:
        fig.add_trace(go.Bar(
            y=rotulos, x=ordenado[etapa], name=ETAPAS_CRM_LABEL[etapa],
            orientation="h", marker_color=cores_etapa[etapa],
        ))
    fig.update_layout(barmode="group")
    altura = max(280, 70 * len(ordenado))
    return _layout_base(fig, f"Resultado de CRM por Mensagem ({rotulo_canal})", altura=altura)


def formatar_tabela_mensagem_whatsapp(agregado: pd.DataFrame) -> list[dict]:
    tem_crm = "acordo" in agregado.columns
    registros = []
    for _, linha in agregado.iterrows():
        registro = {
            "Mensagem (modelo)": _truncar_frase(linha["mensagem_norm"], 140),
            "Total": formatar_numero(linha["total"]),
            "Entregue (não lido)": formatar_numero(linha["Entregue"]),
            "Lido": formatar_numero(linha["Lido"]),
            "Pendente": formatar_numero(linha["Enviado"]),
            "Não Entregue": formatar_numero(linha["Nao Entregue"]),
            "Não Enviado": formatar_numero(linha["Nao Enviado"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Leitura": formatar_percentual(linha["taxa_leitura"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        }
        if tem_crm:
            home, auth, oferta = linha["home"], linha["auth"], linha["oferta"]
            base_home = linha["Lido"] if linha["Lido"] else linha["Entregue"]
            registro["Home"] = _valor_com_percentual(home, base_home)
            registro["Autenticação"] = _valor_com_percentual(auth, home)
            registro["Oferta"] = _valor_com_percentual(oferta, auth)
            registro["Acordo (resultado final)"] = _valor_com_percentual(linha["acordo"], oferta)
        registros.append(registro)
    return registros


def grafico_whatsapp_por_grupo_ab(agregado: pd.DataFrame, crm_agregado: pd.DataFrame | None = None) -> go.Figure:
    """`crm_agregado` (opcional, formato de `agregar_crm_por_grupo_ab`) acrescenta o
    funil de negociação (Home/Autenticação/Oferta/Acordo) como barras extras ao lado da
    pilha de status — todo mundo no mesmo `offsetgroup` continua empilhado normalmente,
    e cada etapa nova ganha seu próprio grupo, aparecendo ao lado."""
    if agregado.empty:
        return _layout_base(go.Figure(), "Resultado de WhatsApp por Grupo AB (sem dados no período)")

    rotulos = [GRUPO_AB_LABEL.get(g, g) for g in agregado["grupo_ab"]]
    fig = go.Figure()
    for status in SITUACOES_WHATSAPP:
        fig.add_trace(go.Bar(
            x=rotulos, y=agregado[status], name=_NOMES_SITUACAO_WHATSAPP[status],
            marker_color=_CORES_SITUACAO_WHATSAPP[status], offsetgroup="status",
        ))

    if crm_agregado is not None and not crm_agregado.empty:
        cores_etapa = {"home": "#8B93B8", "auth": "#3DA9FC", "oferta": "#F5A623", "acordo": "#2ECC71"}
        crm_alinhado = crm_agregado.set_index("grupo_ab").reindex(agregado["grupo_ab"]).fillna(0)
        for etapa in ETAPAS_CRM:
            fig.add_trace(go.Bar(
                x=rotulos, y=crm_alinhado[etapa], name=ETAPAS_CRM_LABEL[etapa],
                marker_color=cores_etapa[etapa], marker_pattern_shape="/", offsetgroup=etapa,
            ))

    fig.update_layout(barmode="group")
    return _layout_base(fig, "Resultado de WhatsApp por Grupo AB")


def grafico_whatsapp_por_grupo_estrategico(agregado: pd.DataFrame) -> go.Figure:
    if agregado.empty:
        return _layout_base(go.Figure(), "Resultado de WhatsApp por Grupo Estratégico (sem dados no período)")

    rotulos = [GRUPO_ESTRATEGICO_LABEL.get(g, g) for g in agregado["grupo_estrategico"]]
    fig = go.Figure()
    for status in SITUACOES_WHATSAPP:
        fig.add_trace(go.Bar(
            x=rotulos, y=agregado[status], name=_NOMES_SITUACAO_WHATSAPP[status],
            marker_color=_CORES_SITUACAO_WHATSAPP[status],
        ))
    fig.update_layout(barmode="stack")
    return _layout_base(fig, "Resultado de WhatsApp por Grupo Estratégico")


def formatar_tabela_whatsapp_grupo_ab(agregado: pd.DataFrame) -> list[dict]:
    registros = []
    for _, linha in agregado.iterrows():
        registros.append({
            "Grupo AB": linha["grupo_ab"],
            "Total": formatar_numero(linha["total"]),
            "Entregue (não lido)": formatar_numero(linha["Entregue"]),
            "Lido": formatar_numero(linha["Lido"]),
            "Pendente": formatar_numero(linha["Enviado"]),
            "Não Entregue": formatar_numero(linha["Nao Entregue"]),
            "Não Enviado": formatar_numero(linha["Nao Enviado"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Leitura": formatar_percentual(linha["taxa_leitura"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        })
    return registros


def formatar_tabela_whatsapp_grupo_estrategico(agregado: pd.DataFrame) -> list[dict]:
    registros = []
    for _, linha in agregado.iterrows():
        registros.append({
            "Grupo Estratégico": GRUPO_ESTRATEGICO_LABEL.get(linha["grupo_estrategico"], linha["grupo_estrategico"]),
            "Total": formatar_numero(linha["total"]),
            "Entregue (não lido)": formatar_numero(linha["Entregue"]),
            "Lido": formatar_numero(linha["Lido"]),
            "Pendente": formatar_numero(linha["Enviado"]),
            "Não Entregue": formatar_numero(linha["Nao Entregue"]),
            "Não Enviado": formatar_numero(linha["Nao Enviado"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Leitura": formatar_percentual(linha["taxa_leitura"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        })
    return registros


def formatar_tabela_whatsapp_campanha(agregado: pd.DataFrame) -> list[dict]:
    registros = []
    for _, linha in agregado.iterrows():
        registros.append({
            "UTM": nome_curto(linha["utm_campaign"]),
            "Total": formatar_numero(linha["total"]),
            "Entregue (não lido)": formatar_numero(linha["Entregue"]),
            "Lido": formatar_numero(linha["Lido"]),
            "Pendente": formatar_numero(linha["Enviado"]),
            "Não Entregue": formatar_numero(linha["Nao Entregue"]),
            "Não Enviado": formatar_numero(linha["Nao Enviado"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Leitura": formatar_percentual(linha["taxa_leitura"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        })
    return registros


def grafico_funil_crm(crm_agregado: pd.DataFrame, rotulo_canal: str = "Pós-Contato") -> go.Figure:
    if crm_agregado.empty:
        return _layout_base(go.Figure(), f"Conversão {rotulo_canal} (sem dados no período)")

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
    return _layout_base(fig, f"Funil de Conversão {rotulo_canal}", altura=360)


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


def grafico_crm_por_grupo_ab(crm_agregado: pd.DataFrame, titulo: str = "Ações de CRM por Grupo AB") -> go.Figure:
    if crm_agregado.empty:
        return _layout_base(go.Figure(), f"{titulo} (sem dados no período)")

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
    return _layout_base(fig, titulo)


def formatar_tabela_crm_grupo_ab(crm_agregado: pd.DataFrame) -> list[dict]:
    """Tabela simples Grupo AB -> Home/Autenticação/Oferta/Acordo, reutilizada pelos
    blocos por canal (SMS/WhatsApp Ótima/Airys/RCS) da aba Funil por Grupo AB."""
    registros = []
    for _, linha in crm_agregado.iterrows():
        home, auth, oferta = linha["home"], linha["auth"], linha["oferta"]
        registros.append({
            "Grupo AB": GRUPO_AB_LABEL.get(linha["grupo_ab"], linha["grupo_ab"]),
            "Home": _valor_com_percentual(home, None),
            "Autenticação": _valor_com_percentual(auth, home),
            "Oferta": _valor_com_percentual(oferta, auth),
            "Acordo": _valor_com_percentual(linha["acordo"], oferta),
        })
    return registros


def grafico_crm_por_grupo_estrategico(crm_agregado: pd.DataFrame) -> go.Figure:
    if crm_agregado.empty:
        return _layout_base(go.Figure(), "Conversão por Grupo Estratégico (sem dados no período)")

    ordem = [g for g in GRUPO_ESTRATEGICO_ORDEM if g in crm_agregado["grupo_estrategico"].values]
    crm_agregado = crm_agregado.set_index("grupo_estrategico").reindex(ordem).reset_index()
    rotulos = [GRUPO_ESTRATEGICO_LABEL.get(g, g) for g in crm_agregado["grupo_estrategico"]]

    fig = go.Figure()
    cores_etapa = {"home": "#8B93B8", "auth": "#3DA9FC", "oferta": "#F5A623", "acordo": "#2ECC71"}
    for etapa in ETAPAS_CRM:
        fig.add_trace(go.Bar(
            x=rotulos, y=crm_agregado[etapa], name=ETAPAS_CRM_LABEL[etapa],
            marker_color=cores_etapa[etapa],
        ))
    fig.update_layout(barmode="group")
    return _layout_base(fig, "Ações de CRM por Grupo Estratégico")


def grafico_crm_por_frase(agregado: pd.DataFrame) -> go.Figure:
    """Home/Autenticação/Oferta/Acordo (log de CRM) por frase-modelo de SMS — mesma
    frase da Taxa de Entrega, mas mostrando o resultado da negociação, não a entrega."""
    tem_crm = "acordo" in agregado.columns
    if agregado.empty or not tem_crm:
        return _layout_base(go.Figure(), "Resultado de CRM por Frase (sem dados no período)")

    ordenado = agregado.sort_values("acordo")
    rotulos = [_truncar_frase(f, 55) for f in ordenado["frase_norm"]]
    fig = go.Figure()
    cores_etapa = {"home": "#8B93B8", "auth": "#3DA9FC", "oferta": "#F5A623", "acordo": "#2ECC71"}
    for etapa in ETAPAS_CRM:
        fig.add_trace(go.Bar(
            y=rotulos, x=ordenado[etapa], name=ETAPAS_CRM_LABEL[etapa],
            orientation="h", marker_color=cores_etapa[etapa],
        ))
    fig.update_layout(barmode="group")
    altura = max(280, 70 * len(ordenado))
    return _layout_base(fig, "Resultado de CRM por Frase (SMS)", altura=altura)


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


def grafico_volume_email_por_jornada(agregado: pd.DataFrame) -> go.Figure:
    if agregado.empty:
        return _layout_base(go.Figure(), "Volume por Jornada (sem dados)")

    ordenado = agregado.sort_values("Envios", ascending=True)
    rotulos = [j.replace("Casas Bahia - Laboratório - ", "") for j in ordenado["Jornada"]]
    fig = go.Figure(
        go.Bar(
            y=rotulos, x=ordenado["Envios"], orientation="h",
            marker_color=CORES["disparado"],
            text=[formatar_numero(v) for v in ordenado["Envios"]], textposition="outside",
            hovertemplate="%{y}<br>Envios: %{x:,}<extra></extra>",
        )
    )
    return _layout_base(fig, "Volume de Envios por Jornada")


def formatar_tabela_email_salesforce(df: pd.DataFrame) -> list[dict]:
    registros = []
    for _, linha in df.iterrows():
        registros.append({
            "Jornada": linha["Jornada"].replace("Casas Bahia - Laboratório - ", ""),
            "E-mail": linha["E-mail"],
            "Assunto": _truncar_frase(linha["Assunto"], 60),
            "Envios": formatar_numero(linha["Envios"]),
            "% envios": formatar_percentual(linha["% envios"]),
            "Entregues": formatar_numero(linha["Entregues"]),
            "Entrega": formatar_percentual(linha["Entrega"]),
            "Bounce": formatar_percentual(linha["Bounce"]),
            "Aberturas": formatar_numero(linha["Aberturas"]),
            "Abertura": formatar_percentual(linha["Abertura"]),
            "Cliques": formatar_numero(linha["Cliques"]),
            "CTR": formatar_percentual(linha["CTR"]),
            "CTOR": formatar_percentual(linha["CTOR"]),
            "Eficiência": f"{linha['Eficiência']:.3f}%".replace(".", ","),
        })
    return registros


def formatar_reais(valor: float | None, casas: int = 2) -> str:
    if valor is None:
        return "Não informado"
    texto = f"{valor:,.{casas}f}"
    texto = texto.replace(",", "§").replace(".", ",").replace("§", ".")
    return f"R$ {texto}"


def formatar_tabela_custos(linhas: list[dict]) -> list[dict]:
    registros = []
    for linha in linhas:
        registros.append({
            "Data": linha["data"].strftime("%d/%m/%Y") if linha["data"] else "Período completo (sem data por envio)",
            "Canal": CANAL_CUSTO_LABEL.get(linha["canal"], linha["canal"]),
            "Fornecedor": FORNECEDOR_CUSTO_LABEL.get(linha["fornecedor"], linha["fornecedor"]),
            "Quantidade Enviada": formatar_numero(linha["quantidade_enviada"]),
            "Custo Unitário": formatar_reais(linha["custo_unitario"], casas=4),
            "Custo Total": formatar_reais(linha["custo_total"]),
        })
    return registros


def grafico_custos_por_dia(linhas: list[dict]) -> go.Figure:
    """Custo total por dia, empilhado por canal — só entram linhas com custo unitário
    definido (SMS/RCS hoje); WhatsApp e Email aparecem só na tabela, com o volume."""
    com_custo = [l for l in linhas if l["custo_total"] is not None and l["data"] is not None]
    if not com_custo:
        return _layout_base(go.Figure(), "Custo por Dia e Canal (sem custo definido no período)")

    df = pd.DataFrame(com_custo)
    cores_canal = {"sms": CORES["disparado"], "rcs": CORES["entregue"], "whatsapp": CORES["enviado"]}
    fig = go.Figure()
    for canal in df["canal"].unique():
        sub = df[df["canal"] == canal].groupby("data")["custo_total"].sum().sort_index()
        fig.add_trace(go.Bar(
            x=sub.index, y=sub.values, name=CANAL_CUSTO_LABEL.get(canal, canal),
            marker_color=cores_canal.get(canal, "#8B93B8"),
            hovertemplate="%{x|%d/%m}<br>R$ %{y:,.2f}<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    return _layout_base(fig, "Custo por Dia e Canal")
