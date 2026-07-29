"""Callback único que liga os filtros globais a KPIs, funil, gráficos e tabelas."""
from __future__ import annotations

import datetime as dt

import pandas as pd
from dash import Input, Output, State, ctx, dash_table, html

import charts
from data_processing import (
    CAMPANHAS_ESCOPO, agregar_crm_por_campanha, agregar_crm_por_grupo_ab,
    agregar_por_campanha, agregar_por_frase, agregar_por_grupo_ab,
    agregar_por_grupo_estrategico, calcular_funil, calcular_kpis, carregar_dados_crm,
    carregar_dados_sms, filtrar_dados, montar_pivot_crm, salvar_diario_estrategia,
)
from utils import formatar_numero, formatar_percentual

CANAL_LABEL_FUNIL = {"sms": "Pós-SMS", "whatsapp": "Pós-WhatsApp", "email": "Pós-Email"}

COLUNAS_TABELA_EXECUTIVA = [
    "UTM", "Total Disparado", "Total Enviado", "Total Entregue", "Total Falhado",
    "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
]

COLUNAS_TABELA_GRUPO_AB = [
    "Grupo AB", "Total Disparado", "Total Enviado", "Total Entregue", "Total Falhado",
    "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
]

COLUNAS_TABELA_GRUPO_ESTRATEGICO = [
    "Grupo Estratégico", "Total Disparado", "Total Enviado", "Total Entregue", "Total Falhado",
    "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
]

COLUNAS_TABELA_FRASE = [
    "Frase (modelo)", "Campanha(s)", "Total Disparado", "Total Enviado", "Total Entregue",
    "Total Falhado", "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
]


def _tabela_funil_html(etapas: list[dict]) -> list:
    cabecalho = html.Div([
        html.Div("Etapa"), html.Div("Quantidade"), html.Div("% da Base"),
        html.Div("Conversão"), html.Div("Perda"),
    ], className="tabela-funil-linha tabela-funil-cabecalho")

    linhas = [cabecalho]
    for etapa in etapas:
        linhas.append(html.Div([
            html.Div(etapa["etapa"]),
            html.Div(formatar_numero(etapa["quantidade"])),
            html.Div(formatar_percentual(etapa["percentual_base"])),
            html.Div(formatar_percentual(etapa["conversao"]), className="tabela-funil-conversao"),
            html.Div(formatar_percentual(etapa["perda"]), className="tabela-funil-perda"),
        ], className="tabela-funil-linha"))
    return linhas


def _tabela_component(registros: list[dict], colunas: list[str]):
    if not registros:
        return html.P("Nenhum dado para os filtros selecionados.", className="text-muted")

    return dash_table.DataTable(
        data=registros,
        columns=[{"name": nome, "id": nome} for nome in colunas],
        sort_action="native",
        style_as_list_view=True,
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#101623", "color": "#8B93A7", "fontWeight": "600",
            "textTransform": "uppercase", "fontSize": "0.72rem", "border": "none",
        },
        style_cell={
            "backgroundColor": "#151B26", "color": "#E5E9F0", "border": "none",
            "padding": "10px 12px", "fontSize": "0.85rem",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#121722"},
        ],
    )


def _tabela_pivot_crm_component(colunas_utm: list[str], linhas: list[dict]):
    if not linhas:
        return html.P("Nenhum dado para os filtros selecionados.", className="text-muted")

    colunas = (
        [{"name": "Ação / Grupo AB", "id": "rotulo"}]
        + [{"name": charts.nome_curto(u), "id": u} for u in colunas_utm]
        + [{"name": "Total Geral", "id": "Total Geral"}]
    )

    registros = []
    indices_destaque = []
    indice_total_geral = None
    for i, linha in enumerate(linhas):
        rotulo = linha["rotulo"]
        if linha["nivel"] == "detalhe":
            rotulo = "     " + charts.GRUPO_AB_LABEL.get(rotulo, rotulo)
        else:
            indices_destaque.append(i)
        if linha["nivel"] == "total_geral":
            indice_total_geral = i

        registro = {"rotulo": rotulo}
        for u in colunas_utm:
            registro[u] = formatar_numero(linha.get(u, 0))
        registro["Total Geral"] = formatar_numero(linha["Total Geral"])
        registros.append(registro)

    style_data_conditional = [{"if": {"row_index": "odd"}, "backgroundColor": "#121722"}]
    style_data_conditional += [
        {"if": {"row_index": i}, "backgroundColor": "#1E2735", "fontWeight": "700"}
        for i in indices_destaque
    ]
    if indice_total_geral is not None:
        style_data_conditional.append(
            {"if": {"row_index": indice_total_geral}, "backgroundColor": "#22304a", "fontWeight": "700"}
        )

    return dash_table.DataTable(
        data=registros,
        columns=colunas,
        style_as_list_view=True,
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#101623", "color": "#8B93A7", "fontWeight": "600",
            "textTransform": "uppercase", "fontSize": "0.72rem", "border": "none",
        },
        style_cell={
            "backgroundColor": "#151B26", "color": "#E5E9F0", "border": "none",
            "padding": "8px 12px", "fontSize": "0.83rem",
        },
        style_cell_conditional=[{"if": {"column_id": "rotulo"}, "textAlign": "left"}],
        style_data_conditional=style_data_conditional,
    )


def registrar_callbacks(app):
    ABAS = ["sms", "grupo", "grupo-estrategico", "frases", "crm", "diario"]

    @app.callback(
        [Output(f"painel-tab-{aba}", "style") for aba in ABAS],
        [Output(f"btn-tab-{aba}", "className") for aba in ABAS],
        [Input(f"btn-tab-{aba}", "n_clicks") for aba in ABAS],
    )
    def alternar_aba(*_cliques):
        oculto, visivel = {"display": "none"}, {"display": "block"}
        inativo, ativo = "aba-botao", "aba-botao aba-ativa"
        aba_ativa = "sms"
        if ctx.triggered_id:
            aba_ativa = ctx.triggered_id.replace("btn-tab-", "")
        estilos = [visivel if aba == aba_ativa else oculto for aba in ABAS]
        classes = [ativo if aba == aba_ativa else inativo for aba in ABAS]
        return (*estilos, *classes)

    @app.callback(
        Output("status-salvar-diario", "children"),
        Input("btn-salvar-diario", "n_clicks"),
        State("editor-diario", "value"),
        prevent_initial_call=True,
    )
    def salvar_diario(_n_clicks, conteudo):
        salvar_diario_estrategia(conteudo)
        agora = dt.datetime.now().strftime("%H:%M:%S")
        return f"Salvo às {agora}"

    @app.callback(
        Output("canal-crm-ativo", "data"),
        Output("btn-canal-sms", "className"),
        Output("btn-canal-whatsapp", "className"),
        Output("btn-canal-email", "className"),
        Input("btn-canal-sms", "n_clicks"),
        Input("btn-canal-whatsapp", "n_clicks"),
        Input("btn-canal-email", "n_clicks"),
    )
    def alternar_canal_crm(_n_sms, _n_whatsapp, _n_email):
        inativo, ativo = "aba-botao", "aba-botao aba-ativa"
        if ctx.triggered_id == "btn-canal-whatsapp":
            return "whatsapp", inativo, ativo, inativo
        if ctx.triggered_id == "btn-canal-email":
            return "email", inativo, inativo, ativo
        return "sms", ativo, inativo, inativo

    @app.callback(
        Output("kpi-disparado", "children"),
        Output("kpi-enviado", "children"),
        Output("kpi-entregue", "children"),
        Output("kpi-falhado", "children"),
        Output("kpi-taxa-envio", "children"),
        Output("kpi-taxa-entrega", "children"),
        Output("kpi-taxa-falha", "children"),
        Output("legenda-filtros", "children"),
        Output("grafico-funil", "figure"),
        Output("tabela-funil-detalhe", "children"),
        Output("grafico-evolucao-horaria", "figure"),
        Output("grafico-evolucao-diaria", "figure"),
        Output("grafico-volume-utm", "figure"),
        Output("grafico-status-sms", "figure"),
        Output("grafico-ranking-campanhas", "figure"),
        Output("grafico-taxa-entrega", "figure"),
        Output("tabela-executiva-container", "children"),
        Output("grafico-volume-grupo-ab", "figure"),
        Output("grafico-taxa-entrega-grupo-ab", "figure"),
        Output("tabela-grupo-ab-container", "children"),
        Output("grafico-volume-grupo-estrategico", "figure"),
        Output("grafico-taxa-entrega-grupo-estrategico", "figure"),
        Output("tabela-grupo-estrategico-container", "children"),
        Output("grafico-taxa-entrega-frase", "figure"),
        Output("tabela-frase-container", "children"),
        Output("kpi-crm-home", "children"),
        Output("kpi-crm-auth", "children"),
        Output("kpi-crm-oferta", "children"),
        Output("kpi-crm-acordo", "children"),
        Output("grafico-funil-crm", "figure"),
        Output("grafico-crm-campanha", "figure"),
        Output("grafico-crm-grupo-ab", "figure"),
        Output("tabela-crm-pivot-container", "children"),
        Input("filtro-utm", "value"),
        Input("filtro-data", "start_date"),
        Input("filtro-data", "end_date"),
        Input("filtro-hora", "value"),
        Input("filtro-status", "value"),
        Input("filtro-grupo-ab", "value"),
        Input("filtro-grupo-estrategico", "value"),
        Input("filtro-utm-crm", "value"),
        Input("canal-crm-ativo", "data"),
    )
    def atualizar_dashboard(
        utms, data_ini, data_fim, faixa_hora, status, grupos_ab, grupos_estrategicos,
        utms_crm, canal_crm,
    ):
        df_completo = carregar_dados_sms()

        data_ini_dt = pd.to_datetime(data_ini).date() if data_ini else None
        data_fim_dt = pd.to_datetime(data_fim).date() if data_fim else None
        hora_ini, hora_fim = (faixa_hora or [0, 23])[:2]

        filtrado = filtrar_dados(
            df_completo, utms=utms, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, status=status, grupos_ab=grupos_ab,
            grupos_estrategicos=grupos_estrategicos,
        )

        kpis = calcular_kpis(filtrado)
        etapas = calcular_funil(filtrado)
        agregado = agregar_por_campanha(filtrado) if not filtrado.empty else agregar_por_campanha(df_completo.iloc[0:0])
        agregado_grupo_ab = (
            agregar_por_grupo_ab(filtrado) if not filtrado.empty else agregar_por_grupo_ab(df_completo.iloc[0:0])
        )
        agregado_grupo_estrategico = (
            agregar_por_grupo_estrategico(filtrado) if not filtrado.empty
            else agregar_por_grupo_estrategico(df_completo.iloc[0:0])
        )
        agregado_frase = (
            agregar_por_frase(filtrado) if not filtrado.empty else agregar_por_frase(df_completo.iloc[0:0])
        )

        legenda = (
            f"{formatar_numero(len(filtrado))} registros no filtro "
            f"(de {formatar_numero(len(df_completo))} totais)"
        )

        crm_completo = carregar_dados_crm()
        canal_crm = canal_crm or "sms"
        crm_filtrado = crm_completo[crm_completo["utm_medium"] == canal_crm] if not crm_completo.empty else crm_completo
        if utms_crm:
            crm_filtrado = crm_filtrado[crm_filtrado["utm_campaign"].isin(utms_crm)]
        if grupos_ab:
            crm_filtrado = crm_filtrado[crm_filtrado["grupo_ab"].isin(grupos_ab)]
        crm_agregado = agregar_crm_por_campanha(crm_filtrado) if not crm_filtrado.empty else crm_completo.iloc[0:0]
        crm_agregado_grupo_ab = (
            agregar_crm_por_grupo_ab(crm_filtrado) if not crm_filtrado.empty else crm_completo.iloc[0:0]
        )
        totais_crm = crm_agregado[["home", "auth", "oferta", "acordo"]].sum() if not crm_agregado.empty else {
            "home": 0, "auth": 0, "oferta": 0, "acordo": 0,
        }
        colunas_pivot, linhas_pivot = montar_pivot_crm(crm_filtrado, CAMPANHAS_ESCOPO)

        return (
            formatar_numero(kpis["disparado"]),
            formatar_numero(kpis["enviado"]),
            formatar_numero(kpis["entregue"]),
            formatar_numero(kpis["falhou"]),
            formatar_percentual(kpis["taxa_envio"]),
            formatar_percentual(kpis["taxa_entrega"]),
            formatar_percentual(kpis["taxa_falha"]),
            legenda,
            charts.grafico_funil(etapas),
            _tabela_funil_html(etapas),
            charts.grafico_evolucao_horaria(filtrado),
            charts.grafico_evolucao_diaria(filtrado),
            charts.grafico_volume_utm(filtrado),
            charts.grafico_status_sms(kpis),
            charts.grafico_ranking_campanhas(agregado),
            charts.grafico_taxa_entrega_campanha(agregado),
            _tabela_component(charts.formatar_tabela_executiva(agregado), COLUNAS_TABELA_EXECUTIVA),
            charts.grafico_volume_grupo_ab(filtrado),
            charts.grafico_taxa_entrega_grupo_ab(agregado_grupo_ab),
            _tabela_component(charts.formatar_tabela_grupo_ab(agregado_grupo_ab), COLUNAS_TABELA_GRUPO_AB),
            charts.grafico_volume_grupo_estrategico(filtrado),
            charts.grafico_taxa_entrega_grupo_estrategico(agregado_grupo_estrategico),
            _tabela_component(
                charts.formatar_tabela_grupo_estrategico(agregado_grupo_estrategico),
                COLUNAS_TABELA_GRUPO_ESTRATEGICO,
            ),
            charts.grafico_taxa_entrega_frase(agregado_frase),
            _tabela_component(charts.formatar_tabela_frase(agregado_frase), COLUNAS_TABELA_FRASE),
            formatar_numero(totais_crm["home"]),
            formatar_numero(totais_crm["auth"]),
            formatar_numero(totais_crm["oferta"]),
            formatar_numero(totais_crm["acordo"]),
            charts.grafico_funil_crm(crm_agregado, CANAL_LABEL_FUNIL.get(canal_crm, "Pós-Contato")),
            charts.grafico_crm_por_campanha(crm_agregado),
            charts.grafico_crm_por_grupo_ab(crm_agregado_grupo_ab),
            _tabela_pivot_crm_component(colunas_pivot, linhas_pivot),
        )
