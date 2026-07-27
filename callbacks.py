"""Callback único que liga os filtros globais a KPIs, funil, gráficos e tabelas."""
from __future__ import annotations

import pandas as pd
from dash import Input, Output, ctx, dash_table, html

import charts
from data_processing import (
    agregar_crm_por_campanha, agregar_por_campanha, agregar_por_grupo_ab, calcular_funil,
    calcular_kpis, carregar_dados_crm, carregar_dados_sms, filtrar_dados,
)
from utils import formatar_numero, formatar_percentual

COLUNAS_TABELA_EXECUTIVA = [
    "UTM", "Total Disparado", "Total Enviado", "Total Entregue", "Total Falhado",
    "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
]

COLUNAS_TABELA_GRUPO_AB = [
    "Grupo AB", "Total Disparado", "Total Enviado", "Total Entregue", "Total Falhado",
    "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
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


def registrar_callbacks(app):
    @app.callback(
        Output("painel-tab-sms", "style"),
        Output("painel-tab-grupo", "style"),
        Output("painel-tab-crm", "style"),
        Output("btn-tab-sms", "className"),
        Output("btn-tab-grupo", "className"),
        Output("btn-tab-crm", "className"),
        Input("btn-tab-sms", "n_clicks"),
        Input("btn-tab-grupo", "n_clicks"),
        Input("btn-tab-crm", "n_clicks"),
    )
    def alternar_aba(_n_sms, _n_grupo, _n_crm):
        oculto, visivel = {"display": "none"}, {"display": "block"}
        inativo, ativo = "aba-botao", "aba-botao aba-ativa"
        if ctx.triggered_id == "btn-tab-grupo":
            return oculto, visivel, oculto, inativo, ativo, inativo
        if ctx.triggered_id == "btn-tab-crm":
            return oculto, oculto, visivel, inativo, inativo, ativo
        return visivel, oculto, oculto, ativo, inativo, inativo

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
        Output("kpi-crm-home", "children"),
        Output("kpi-crm-auth", "children"),
        Output("kpi-crm-oferta", "children"),
        Output("kpi-crm-acordo", "children"),
        Output("grafico-funil-crm", "figure"),
        Output("grafico-crm-campanha", "figure"),
        Input("filtro-utm", "value"),
        Input("filtro-data", "start_date"),
        Input("filtro-data", "end_date"),
        Input("filtro-hora", "value"),
        Input("filtro-status", "value"),
        Input("filtro-grupo-ab", "value"),
    )
    def atualizar_dashboard(utms, data_ini, data_fim, faixa_hora, status, grupos_ab):
        df_completo = carregar_dados_sms()

        data_ini_dt = pd.to_datetime(data_ini).date() if data_ini else None
        data_fim_dt = pd.to_datetime(data_fim).date() if data_fim else None
        hora_ini, hora_fim = (faixa_hora or [0, 23])[:2]

        filtrado = filtrar_dados(
            df_completo, utms=utms, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, status=status, grupos_ab=grupos_ab,
        )

        kpis = calcular_kpis(filtrado)
        etapas = calcular_funil(filtrado)
        agregado = agregar_por_campanha(filtrado) if not filtrado.empty else agregar_por_campanha(df_completo.iloc[0:0])
        agregado_grupo_ab = (
            agregar_por_grupo_ab(filtrado) if not filtrado.empty else agregar_por_grupo_ab(df_completo.iloc[0:0])
        )

        legenda = (
            f"{formatar_numero(len(filtrado))} registros no filtro "
            f"(de {formatar_numero(len(df_completo))} totais)"
        )

        crm_completo = carregar_dados_crm()
        crm_filtrado = crm_completo[crm_completo["utm_campaign"].isin(utms)] if utms else crm_completo
        crm_agregado = agregar_crm_por_campanha(crm_filtrado) if not crm_filtrado.empty else crm_completo.iloc[0:0]
        totais_crm = crm_agregado[["home", "auth", "oferta", "acordo"]].sum() if not crm_agregado.empty else {
            "home": 0, "auth": 0, "oferta": 0, "acordo": 0,
        }

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
            formatar_numero(totais_crm["home"]),
            formatar_numero(totais_crm["auth"]),
            formatar_numero(totais_crm["oferta"]),
            formatar_numero(totais_crm["acordo"]),
            charts.grafico_funil_crm(crm_agregado),
            charts.grafico_crm_por_campanha(crm_agregado),
        )
