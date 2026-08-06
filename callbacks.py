"""Callback único que liga os filtros globais a KPIs, funil, gráficos e tabelas."""
from __future__ import annotations

import datetime as dt

import pandas as pd
from dash import Input, Output, State, ctx, dash_table, html

import charts
from data_processing import (
    CAMPANHAS_ESCOPO, agregar_crm_por_campanha, agregar_crm_por_grupo_ab,
    agregar_crm_por_grupo_estrategico, agregar_por_campanha, agregar_por_grupo_ab,
    agregar_por_grupo_estrategico, agregar_frase_com_crm, agregar_mensagem_whatsapp_com_crm,
    agregar_resultado_resposta_airys, agregar_whatsapp_por_campanha, agregar_whatsapp_por_grupo_ab,
    agregar_whatsapp_por_grupo_estrategico, calcular_funil, calcular_funil_combinado_email_salesforce,
    calcular_funil_combinado_sms, calcular_funil_combinado_whatsapp, calcular_funil_whatsapp,
    calcular_kpis, calcular_kpis_email_salesforce, calcular_kpis_resposta_airys,
    calcular_kpis_whatsapp, canal_da_campanha, carregar_dados_airys, carregar_dados_crm,
    carregar_dados_email_salesforce, carregar_dados_rcs, carregar_dados_rcs_estilo_sms,
    carregar_dados_sms, carregar_dados_whatsapp_mensagem, filtrar_dados, filtrar_dados_whatsapp,
    fornecedor_da_campanha, montar_pivot_crm, montar_tabela_frase_com_grupo,
    montar_tabela_grupo_estrategico_com_ab, montar_tabela_mensagem_com_grupo,
    salvar_diario_estrategia, total_disparado_campanhas,
)
from utils import formatar_numero, formatar_percentual, taxa

CANAL_LABEL_FUNIL = {
    "sms": "Pós-SMS", "whatsapp": "Pós-WhatsApp", "rcs": "Pós-RCS", "email": "Pós-Email",
}

UTMS_WHATSAPP_OTIMA = [
    u for u in CAMPANHAS_ESCOPO if canal_da_campanha(u) == "whatsapp" and fornecedor_da_campanha(u) == "otima"
]
UTMS_WHATSAPP_AIRYS = [
    u for u in CAMPANHAS_ESCOPO if canal_da_campanha(u) == "whatsapp" and fornecedor_da_campanha(u) == "airys"
]
UTMS_SMS = [u for u in CAMPANHAS_ESCOPO if canal_da_campanha(u) == "sms"]
UTMS_RCS = [u for u in CAMPANHAS_ESCOPO if canal_da_campanha(u) == "rcs"]

# Estático (não depende de nenhum filtro): o relatório de e-mail do Salesforce Journey
# Builder já vem agregado pela própria plataforma, sem telefone/timestamp por
# destinatário — ver docstring de `carregar_dados_email_salesforce`.
_KPIS_EMAIL_SALESFORCE = calcular_kpis_email_salesforce(carregar_dados_email_salesforce())

COLUNAS_TABELA_EXECUTIVA = [
    "UTM", "Total Disparado", "Total Enviado", "Total Entregue", "Total Falhado",
    "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
]

COLUNAS_TABELA_WHATSAPP_CAMPANHA = [
    "UTM", "Total", "Entregue (não lido)", "Lido", "Pendente", "Não Entregue", "Não Enviado",
    "Taxa de Entrega", "Taxa de Leitura", "Taxa de Falha",
]

COLUNAS_TABELA_GRUPO_AB = [
    "Grupo AB", "Total Disparado", "Total Enviado", "Total Entregue", "Total Falhado",
    "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
]

COLUNAS_TABELA_WHATSAPP_GRUPO_AB = [
    "Grupo AB", "Total", "Entregue (não lido)", "Lido", "Pendente", "Não Entregue", "Não Enviado",
    "Taxa de Entrega", "Taxa de Leitura", "Taxa de Falha",
]

COLUNAS_TABELA_WHATSAPP_GRUPO_ESTRATEGICO = [
    "Grupo Estratégico", "Total", "Entregue (não lido)", "Lido", "Pendente", "Não Entregue", "Não Enviado",
    "Taxa de Entrega", "Taxa de Leitura", "Taxa de Falha",
]

COLUNAS_TABELA_FRASE = [
    "Frase (modelo)", "Campanha(s)", "Total Disparado", "Total Enviado", "Total Entregue",
    "Total Falhado", "Taxa de Envio", "Taxa de Entrega", "Taxa de Falha",
    "Home", "Autenticação", "Oferta", "Acordo (resultado final)",
]

COLUNAS_TABELA_MENSAGEM_WHATSAPP = [
    "Mensagem (modelo)", "Total", "Entregue (não lido)", "Lido", "Pendente", "Não Entregue", "Não Enviado",
    "Taxa de Entrega", "Taxa de Leitura", "Taxa de Falha",
    "Home", "Autenticação", "Oferta", "Acordo (resultado final)",
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


def _tabela_pivot_crm_component(
    colunas_utm: list[str], linhas: list[dict],
    titulo_coluna: str = "Ação / Grupo AB", mapa_label: dict | None = None,
):
    if not linhas:
        return html.P("Nenhum dado para os filtros selecionados.", className="text-muted")

    mapa_label = mapa_label if mapa_label is not None else charts.GRUPO_AB_LABEL
    colunas = (
        [{"name": titulo_coluna, "id": "rotulo"}]
        + [{"name": charts.nome_curto(u), "id": u} for u in colunas_utm]
        + [{"name": "Total Geral", "id": "Total Geral"}]
    )

    registros = []
    indices_destaque = []
    indice_total_geral = None
    for i, linha in enumerate(linhas):
        rotulo = linha["rotulo"]
        if linha["nivel"] == "detalhe":
            rotulo = "     " + mapa_label.get(rotulo, rotulo)
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


def _tabela_grupo_estrategico_ab_component(linhas: list[dict]):
    if not linhas:
        return html.P("Nenhum dado para os filtros selecionados.", className="text-muted")

    colunas = [
        {"name": "Grupo Estratégico / Grupo AB", "id": "rotulo"},
        {"name": "Total Disparado", "id": "Total Disparado"},
        {"name": "Total Enviado", "id": "Total Enviado"},
        {"name": "Total Entregue", "id": "Total Entregue"},
        {"name": "Total Falhado", "id": "Total Falhado"},
        {"name": "Taxa de Envio", "id": "Taxa de Envio"},
        {"name": "Taxa de Entrega", "id": "Taxa de Entrega"},
        {"name": "Taxa de Falha", "id": "Taxa de Falha"},
    ]

    registros = []
    indices_destaque = []
    for i, linha in enumerate(linhas):
        rotulo = linha["rotulo"]
        if linha["nivel"] == "detalhe":
            rotulo = "     " + charts.GRUPO_AB_LABEL.get(rotulo, rotulo)
        else:
            rotulo = charts.GRUPO_ESTRATEGICO_LABEL.get(rotulo, rotulo)
            indices_destaque.append(i)

        registros.append({
            "rotulo": rotulo,
            "Total Disparado": formatar_numero(linha["total_disparado"]),
            "Total Enviado": formatar_numero(linha["total_enviado"]),
            "Total Entregue": formatar_numero(linha["total_entregue"]),
            "Total Falhado": formatar_numero(linha["total_falhado"]),
            "Taxa de Envio": formatar_percentual(linha["taxa_envio"]),
            "Taxa de Entrega": formatar_percentual(linha["taxa_entrega"]),
            "Taxa de Falha": formatar_percentual(linha["taxa_falha"]),
        })

    style_data_conditional = [{"if": {"row_index": "odd"}, "backgroundColor": "#121722"}]
    style_data_conditional += [
        {"if": {"row_index": i}, "backgroundColor": "#1E2735", "fontWeight": "700"}
        for i in indices_destaque
    ]

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


def _valor_com_percentual_etapa(valor: int, anterior: int | None) -> str:
    """Formata "quantidade (percentual)" — percentual é a conversão em relação à etapa
    anterior da mesma linha (Home é a etapa-base, sempre 100%), consistente com a
    lógica de funil etapa-a-etapa usada na aba Conversão Pós-Contato."""
    numero = formatar_numero(valor)
    percentual = formatar_percentual(100.0 if anterior is None else taxa(valor, anterior))
    return f"{numero} ({percentual})"


def _tabela_texto_grupo_component(linhas: list[dict], mapa_label: dict, titulo_coluna: str):
    if not linhas:
        return html.P("Nenhum dado para os filtros selecionados.", className="text-muted")

    colunas = [
        {"name": titulo_coluna, "id": "rotulo"},
        {"name": "Home", "id": "Home"},
        {"name": "Autenticação", "id": "Autenticação"},
        {"name": "Oferta", "id": "Oferta"},
        {"name": "Acordo (resultado final)", "id": "Acordo (resultado final)"},
    ]

    registros = []
    indices_destaque = []
    for i, linha in enumerate(linhas):
        rotulo = linha["rotulo"]
        if linha["nivel"] == "detalhe":
            rotulo = "     " + mapa_label.get(rotulo, rotulo)
        else:
            rotulo = rotulo if len(rotulo) <= 90 else rotulo[:89].rstrip() + "…"
            indices_destaque.append(i)

        home, auth, oferta, acordo = linha["home"], linha["auth"], linha["oferta"], linha["acordo"]
        registros.append({
            "rotulo": rotulo,
            "Home": _valor_com_percentual_etapa(home, None),
            "Autenticação": _valor_com_percentual_etapa(auth, home),
            "Oferta": _valor_com_percentual_etapa(oferta, auth),
            "Acordo (resultado final)": _valor_com_percentual_etapa(acordo, oferta),
        })

    style_data_conditional = [{"if": {"row_index": "odd"}, "backgroundColor": "#121722"}]
    style_data_conditional += [
        {"if": {"row_index": i}, "backgroundColor": "#1E2735", "fontWeight": "700"}
        for i in indices_destaque
    ]

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
    ABAS = ["sms", "grupo", "grupo-estrategico", "crm", "diario"]

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
        Output("btn-canal-rcs", "className"),
        Output("btn-canal-email", "className"),
        Output("secao-frase-sms", "style"),
        Output("secao-mensagem-whatsapp", "style"),
        Output("secao-mensagem-rcs", "style"),
        Output("bloco-funil-crm-airys", "style"),
        Output("alerta-funil-crm-email", "style"),
        Input("btn-canal-sms", "n_clicks"),
        Input("btn-canal-whatsapp", "n_clicks"),
        Input("btn-canal-rcs", "n_clicks"),
        Input("btn-canal-email", "n_clicks"),
    )
    def alternar_canal_crm(_n_sms, _n_whatsapp, _n_rcs, _n_email):
        inativo, ativo = "aba-botao", "aba-botao aba-ativa"
        oculto, visivel = {"display": "none"}, {"display": "block"}
        if ctx.triggered_id == "btn-canal-whatsapp":
            return "whatsapp", inativo, ativo, inativo, inativo, oculto, visivel, oculto, visivel, oculto
        if ctx.triggered_id == "btn-canal-rcs":
            return "rcs", inativo, inativo, ativo, inativo, oculto, oculto, visivel, oculto, oculto
        if ctx.triggered_id == "btn-canal-email":
            return "email", inativo, inativo, inativo, ativo, oculto, oculto, oculto, oculto, visivel
        return "sms", ativo, inativo, inativo, inativo, visivel, oculto, oculto, oculto, oculto

    @app.callback(
        Output("kpi-disparado", "children"),
        Output("kpi-enviado", "children"),
        Output("kpi-entregue", "children"),
        Output("kpi-falhado", "children"),
        Output("kpi-taxa-envio", "children"),
        Output("kpi-taxa-entrega", "children"),
        Output("kpi-taxa-falha", "children"),
        Output("kpi-whatsapp-disparado", "children"),
        Output("kpi-whatsapp-entregue", "children"),
        Output("kpi-whatsapp-lido", "children"),
        Output("kpi-whatsapp-enviado", "children"),
        Output("kpi-whatsapp-nao-entregue", "children"),
        Output("kpi-whatsapp-nao-enviado", "children"),
        Output("kpi-airys-disparado", "children"),
        Output("kpi-airys-entregue", "children"),
        Output("kpi-airys-lido", "children"),
        Output("kpi-airys-enviado", "children"),
        Output("kpi-airys-nao-entregue", "children"),
        Output("kpi-airys-respondeu", "children"),
        Output("kpi-rcs-disparado", "children"),
        Output("kpi-rcs-enviado", "children"),
        Output("kpi-rcs-entregue", "children"),
        Output("kpi-rcs-falhado", "children"),
        Output("kpi-rcs-taxa-envio", "children"),
        Output("kpi-rcs-taxa-entrega", "children"),
        Output("kpi-rcs-taxa-falha", "children"),
        Output("legenda-filtros", "children"),
        Output("grafico-funil", "figure"),
        Output("tabela-funil-detalhe", "children"),
        Output("grafico-funil-whatsapp", "figure"),
        Output("tabela-funil-whatsapp-detalhe", "children"),
        Output("grafico-evolucao-horaria", "figure"),
        Output("grafico-evolucao-diaria", "figure"),
        Output("grafico-volume-utm", "figure"),
        Output("grafico-status-sms", "figure"),
        Output("grafico-ranking-campanhas", "figure"),
        Output("grafico-taxa-entrega", "figure"),
        Output("tabela-executiva-container", "children"),
        Output("tabela-whatsapp-campanha-container", "children"),
        Output("grafico-funil-airys", "figure"),
        Output("tabela-funil-airys-detalhe", "children"),
        Output("grafico-resultado-resposta-airys", "figure"),
        Output("tabela-airys-campanha-container", "children"),
        Output("grafico-funil-rcs", "figure"),
        Output("tabela-funil-rcs-detalhe", "children"),
        Output("grafico-evolucao-horaria-rcs", "figure"),
        Output("grafico-evolucao-diaria-rcs", "figure"),
        Output("grafico-volume-utm-rcs", "figure"),
        Output("grafico-status-rcs", "figure"),
        Output("grafico-ranking-campanhas-rcs", "figure"),
        Output("grafico-taxa-entrega-rcs", "figure"),
        Output("tabela-executiva-rcs-container", "children"),
        Output("grafico-volume-grupo-ab", "figure"),
        Output("grafico-taxa-entrega-grupo-ab", "figure"),
        Output("tabela-grupo-ab-container", "children"),
        Output("grafico-whatsapp-grupo-ab", "figure"),
        Output("tabela-whatsapp-grupo-ab-container", "children"),
        Output("grafico-airys-grupo-ab", "figure"),
        Output("tabela-airys-grupo-ab-container", "children"),
        Output("grafico-volume-grupo-ab-rcs", "figure"),
        Output("grafico-taxa-entrega-grupo-ab-rcs", "figure"),
        Output("tabela-grupo-ab-rcs-container", "children"),
        Output("grafico-volume-grupo-estrategico", "figure"),
        Output("grafico-taxa-entrega-grupo-estrategico", "figure"),
        Output("tabela-grupo-estrategico-container", "children"),
        Output("grafico-whatsapp-grupo-estrategico", "figure"),
        Output("tabela-whatsapp-grupo-estrategico-container", "children"),
        Output("grafico-airys-grupo-estrategico", "figure"),
        Output("tabela-airys-grupo-estrategico-container", "children"),
        Output("grafico-volume-grupo-estrategico-rcs", "figure"),
        Output("grafico-taxa-entrega-grupo-estrategico-rcs", "figure"),
        Output("tabela-grupo-estrategico-rcs-container", "children"),
        Output("grafico-taxa-entrega-frase", "figure"),
        Output("grafico-crm-frase", "figure"),
        Output("tabela-frase-container", "children"),
        Output("tabela-frase-grupo-ab-container", "children"),
        Output("tabela-frase-grupo-estrategico-container", "children"),
        Output("grafico-status-mensagem-whatsapp", "figure"),
        Output("grafico-crm-mensagem-whatsapp", "figure"),
        Output("tabela-mensagem-whatsapp-container", "children"),
        Output("tabela-mensagem-whatsapp-grupo-ab-container", "children"),
        Output("tabela-mensagem-whatsapp-grupo-estrategico-container", "children"),
        Output("grafico-status-mensagem-airys", "figure"),
        Output("grafico-crm-mensagem-airys", "figure"),
        Output("tabela-mensagem-airys-container", "children"),
        Output("tabela-mensagem-airys-grupo-ab-container", "children"),
        Output("tabela-mensagem-airys-grupo-estrategico-container", "children"),
        Output("grafico-status-mensagem-rcs", "figure"),
        Output("grafico-crm-mensagem-rcs", "figure"),
        Output("tabela-mensagem-rcs-container", "children"),
        Output("tabela-mensagem-rcs-grupo-ab-container", "children"),
        Output("tabela-mensagem-rcs-grupo-estrategico-container", "children"),
        Output("kpi-crm-home", "children"),
        Output("kpi-crm-auth", "children"),
        Output("kpi-crm-oferta", "children"),
        Output("kpi-crm-acordo", "children"),
        Output("grafico-funil-crm", "figure"),
        Output("grafico-funil-crm-airys", "figure"),
        Output("grafico-crm-campanha", "figure"),
        Output("grafico-crm-grupo-ab", "figure"),
        Output("grafico-crm-grupo-estrategico", "figure"),
        Output("tabela-crm-pivot-container", "children"),
        Output("tabela-crm-pivot-estrategico-container", "children"),
        Output("kpi-clientes-unicos", "children"),
        Output("tabela-crm-grupo-ab-sms-container", "children"),
        Output("tabela-crm-grupo-ab-whatsapp-container", "children"),
        Output("tabela-crm-grupo-ab-airys-container", "children"),
        Output("tabela-crm-grupo-ab-rcs-container", "children"),
        Output("kpi-crm-taxa-entrega", "children"),
        Output("kpi-crm-home-vs-etapa", "children"),
        Output("kpi-crm-home-vs-etapa-titulo", "children"),
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
        # `carregar_dados_sms()` descobre TODO arquivo de ARQUIVOS PARA DISPAROS/,
        # de qualquer canal (SMS/WhatsApp/Airys/RCS/Email) — restringe aqui às
        # campanhas de fato SMS/Kolmeya, já que esse é o bloco "SMS (Kolmeya)" do
        # dashboard (senão o Total Disparado soma o disparo de todos os canais juntos).
        df_completo = carregar_dados_sms()
        df_completo = df_completo[df_completo["utm_campaign"].isin(UTMS_SMS)]

        data_ini_dt = pd.to_datetime(data_ini).date() if data_ini else None
        data_fim_dt = pd.to_datetime(data_fim).date() if data_fim else None
        hora_ini, hora_fim = (faixa_hora or [0, 23])[:2]

        filtrado = filtrar_dados(
            df_completo, utms=utms, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, status=status, grupos_ab=grupos_ab,
            grupos_estrategicos=grupos_estrategicos,
        )

        whatsapp_completo = carregar_dados_whatsapp_mensagem()
        whatsapp_filtrado = filtrar_dados_whatsapp(
            whatsapp_completo, utms=utms, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
            grupos_estrategicos=grupos_estrategicos,
        )
        kpis_whatsapp = calcular_kpis_whatsapp(whatsapp_filtrado)
        etapas_whatsapp = calcular_funil_whatsapp(kpis_whatsapp)
        agregado_whatsapp_grupo_ab = agregar_whatsapp_por_grupo_ab(whatsapp_filtrado)
        agregado_whatsapp_grupo_estrategico = agregar_whatsapp_por_grupo_estrategico(whatsapp_filtrado)

        whatsapp_filtrado_sem_utm = filtrar_dados_whatsapp(
            whatsapp_completo, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
            grupos_estrategicos=grupos_estrategicos,
        )
        utms_otima_selecionadas = [u for u in (utms or CAMPANHAS_ESCOPO) if u in UTMS_WHATSAPP_OTIMA]
        agregado_whatsapp_campanha = agregar_whatsapp_por_campanha(
            whatsapp_filtrado_sem_utm, utms_otima_selecionadas,
        )
        total_whatsapp_disparado = total_disparado_campanhas(utms_otima_selecionadas)

        airys_completo = carregar_dados_airys()
        airys_filtrado = filtrar_dados_whatsapp(
            airys_completo, utms=utms, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
            grupos_estrategicos=grupos_estrategicos,
        )
        kpis_airys = calcular_kpis_whatsapp(airys_filtrado)
        kpis_resposta_airys = calcular_kpis_resposta_airys(airys_filtrado)
        etapas_airys = calcular_funil_whatsapp(kpis_airys)
        agregado_resultado_resposta_airys = agregar_resultado_resposta_airys(airys_filtrado)
        agregado_airys_grupo_ab = agregar_whatsapp_por_grupo_ab(airys_filtrado)
        agregado_airys_grupo_estrategico = agregar_whatsapp_por_grupo_estrategico(airys_filtrado)

        airys_filtrado_sem_utm = filtrar_dados_whatsapp(
            airys_completo, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
            grupos_estrategicos=grupos_estrategicos,
        )
        utms_airys_selecionadas = [u for u in (utms or CAMPANHAS_ESCOPO) if u in UTMS_WHATSAPP_AIRYS]
        agregado_airys_campanha = agregar_whatsapp_por_campanha(
            airys_filtrado_sem_utm, utms_airys_selecionadas,
        )
        total_airys_disparado = total_disparado_campanhas(utms_airys_selecionadas)

        rcs_sms = carregar_dados_rcs_estilo_sms()
        rcs_sms_filtrado = filtrar_dados(
            rcs_sms, utms=utms, data_ini=data_ini_dt, data_fim=data_fim_dt,
            hora_ini=hora_ini, hora_fim=hora_fim, status=status, grupos_ab=grupos_ab,
            grupos_estrategicos=grupos_estrategicos,
        )
        kpis_rcs = calcular_kpis(rcs_sms_filtrado)
        etapas_rcs = calcular_funil(rcs_sms_filtrado)
        agregado_rcs = (
            agregar_por_campanha(rcs_sms_filtrado) if not rcs_sms_filtrado.empty
            else agregar_por_campanha(rcs_sms.iloc[0:0])
        )
        agregado_grupo_ab_rcs = (
            agregar_por_grupo_ab(rcs_sms_filtrado) if not rcs_sms_filtrado.empty
            else agregar_por_grupo_ab(rcs_sms.iloc[0:0])
        )
        agregado_grupo_estrategico_rcs = (
            agregar_por_grupo_estrategico(rcs_sms_filtrado) if not rcs_sms_filtrado.empty
            else agregar_por_grupo_estrategico(rcs_sms.iloc[0:0])
        )
        linhas_grupo_estrategico_ab_rcs = montar_tabela_grupo_estrategico_com_ab(rcs_sms_filtrado)

        rcs_completo = carregar_dados_rcs()

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
        linhas_grupo_estrategico_ab = montar_tabela_grupo_estrategico_com_ab(filtrado)

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
        if grupos_estrategicos:
            crm_filtrado = crm_filtrado[crm_filtrado["grupo_estrategico"].isin(grupos_estrategicos)]
        crm_agregado = agregar_crm_por_campanha(crm_filtrado) if not crm_filtrado.empty else crm_completo.iloc[0:0]
        crm_agregado_grupo_ab = (
            agregar_crm_por_grupo_ab(crm_filtrado) if not crm_filtrado.empty else crm_completo.iloc[0:0]
        )
        crm_agregado_grupo_estrategico = (
            agregar_crm_por_grupo_estrategico(crm_filtrado) if not crm_filtrado.empty else crm_completo.iloc[0:0]
        )
        agregado_frase = agregar_frase_com_crm(filtrado, crm_filtrado)
        agregado_mensagem_whatsapp = agregar_mensagem_whatsapp_com_crm(whatsapp_completo, crm_filtrado)
        agregado_mensagem_airys = agregar_mensagem_whatsapp_com_crm(airys_completo, crm_filtrado)
        agregado_mensagem_rcs = agregar_mensagem_whatsapp_com_crm(rcs_completo, crm_filtrado)
        totais_crm = crm_agregado[["home", "auth", "oferta", "acordo"]].sum() if not crm_agregado.empty else {
            "home": 0, "auth": 0, "oferta": 0, "acordo": 0,
        }
        colunas_pivot, linhas_pivot = montar_pivot_crm(crm_filtrado, CAMPANHAS_ESCOPO, "grupo_ab")
        colunas_pivot_ge, linhas_pivot_ge = montar_pivot_crm(crm_filtrado, CAMPANHAS_ESCOPO, "grupo_estrategico")

        # Funil combinado (Disparo + CRM), na aba Conversão Pós-Contato: continua o
        # funil de entrega direto no funil de negociação, na mesma campanha (UTM) da
        # aba CRM (utms_crm) — não a campanha do filtro global do Funil Geral.
        titulo_funil_crm = f"Funil de Conversão {CANAL_LABEL_FUNIL.get(canal_crm, 'Pós-Contato')}"
        grafico_funil_crm_airys = charts.grafico_funil_crm(pd.DataFrame(), "Airys")
        if canal_crm == "sms":
            filtrado_crm_sms = filtrar_dados(
                df_completo, utms=utms_crm, data_ini=data_ini_dt, data_fim=data_fim_dt,
                hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
                grupos_estrategicos=grupos_estrategicos,
            )
            kpis_crm_sms = calcular_kpis(filtrado_crm_sms)
            grafico_funil_crm_combinado = charts.grafico_funil(
                calcular_funil_combinado_sms(kpis_crm_sms, totais_crm),
                cores=charts.CORES_FUNIL_COMBINADO_SMS, titulo=titulo_funil_crm, altura=560,
                textposition="outside", modo_percentual="etapa",
            )
            taxa_entrega_crm = kpis_crm_sms["taxa_entrega"]
            home_vs_etapa_titulo = "Home vs Entrega"
            home_vs_etapa_valor = taxa(totais_crm["home"], kpis_crm_sms["entregue"])
        elif canal_crm == "whatsapp":
            # Ótima e Airys têm cada um seu próprio retorno (whatsapp_completo é só
            # Ótima, airys_completo é só Airys), seu próprio Total Disparado (o
            # retorno não cobre 100% do disparo — ver total_disparado_campanhas) e seu
            # próprio resultado de CRM, então viram dois funis separados em vez de um
            # combinado (que ficava com o "Disparado" errado e misturava os provedores).
            utms_crm_efetivas = utms_crm or CAMPANHAS_ESCOPO
            utms_crm_otima = [u for u in utms_crm_efetivas if u in UTMS_WHATSAPP_OTIMA]
            utms_crm_airys = [u for u in utms_crm_efetivas if u in UTMS_WHATSAPP_AIRYS]

            whatsapp_filtrado_crm = filtrar_dados_whatsapp(
                whatsapp_completo, utms=utms_crm_otima, data_ini=data_ini_dt, data_fim=data_fim_dt,
                hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
                grupos_estrategicos=grupos_estrategicos,
            )
            crm_filtrado_otima = crm_filtrado[crm_filtrado["utm_campaign"].isin(utms_crm_otima)]
            crm_agregado_otima_funil = agregar_crm_por_campanha(crm_filtrado_otima) if not crm_filtrado_otima.empty else crm_filtrado_otima
            totais_crm_otima = (
                crm_agregado_otima_funil[["home", "auth", "oferta", "acordo"]].sum()
                if not crm_agregado_otima_funil.empty else {"home": 0, "auth": 0, "oferta": 0, "acordo": 0}
            )
            kpis_whatsapp_otima_crm = calcular_kpis_whatsapp(whatsapp_filtrado_crm)
            grafico_funil_crm_combinado = charts.grafico_funil(
                calcular_funil_combinado_whatsapp(
                    kpis_whatsapp_otima_crm, totais_crm_otima,
                    total_disparado=total_disparado_campanhas(utms_crm_otima),
                ),
                cores=charts.CORES_FUNIL_COMBINADO_WHATSAPP, titulo=f"{titulo_funil_crm} (Ótima)", altura=560,
                textposition="outside", modo_percentual="etapa",
            )

            airys_filtrado_crm = filtrar_dados_whatsapp(
                airys_completo, utms=utms_crm_airys, data_ini=data_ini_dt, data_fim=data_fim_dt,
                hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
                grupos_estrategicos=grupos_estrategicos,
            )
            crm_filtrado_airys = crm_filtrado[crm_filtrado["utm_campaign"].isin(utms_crm_airys)]
            crm_agregado_airys_funil = agregar_crm_por_campanha(crm_filtrado_airys) if not crm_filtrado_airys.empty else crm_filtrado_airys
            totais_crm_airys = (
                crm_agregado_airys_funil[["home", "auth", "oferta", "acordo"]].sum()
                if not crm_agregado_airys_funil.empty else {"home": 0, "auth": 0, "oferta": 0, "acordo": 0}
            )
            kpis_whatsapp_airys_crm = calcular_kpis_whatsapp(airys_filtrado_crm)
            grafico_funil_crm_airys = charts.grafico_funil(
                calcular_funil_combinado_whatsapp(
                    kpis_whatsapp_airys_crm, totais_crm_airys,
                    total_disparado=total_disparado_campanhas(utms_crm_airys),
                ),
                cores=charts.CORES_FUNIL_COMBINADO_WHATSAPP, titulo=f"{titulo_funil_crm} (Airys)", altura=560,
                textposition="outside", modo_percentual="etapa",
            )
            entregue_otima = kpis_whatsapp_otima_crm["Entregue"] + kpis_whatsapp_otima_crm["Lido"]
            enviado_otima = (
                entregue_otima + kpis_whatsapp_otima_crm["Enviado"] + kpis_whatsapp_otima_crm["Nao Entregue"]
            )
            entregue_airys = kpis_whatsapp_airys_crm["Entregue"] + kpis_whatsapp_airys_crm["Lido"]
            enviado_airys = (
                entregue_airys + kpis_whatsapp_airys_crm["Enviado"] + kpis_whatsapp_airys_crm["Nao Entregue"]
            )
            entregue_crm_total = entregue_otima + entregue_airys
            taxa_entrega_crm = taxa(entregue_crm_total, enviado_otima + enviado_airys)
            lido_crm_total = kpis_whatsapp_otima_crm["Lido"] + kpis_whatsapp_airys_crm["Lido"]
            home_vs_etapa_titulo = "Home vs Lido"
            home_vs_etapa_valor = taxa(totais_crm["home"], lido_crm_total)
        elif canal_crm == "rcs":
            # O retorno de RCS segue o mesmo formato Otima-schema do WhatsApp Ótima (ver
            # `_carregar_retorno_estilo_otima`), então também distingue "Lido" de
            # "Entregue" — usa o mesmo pipeline estilo WhatsApp (não o estilo SMS) pra
            # aproveitar essa etapa extra no funil, igual já é feito pro WhatsApp.
            utms_crm_rcs = [u for u in (utms_crm or CAMPANHAS_ESCOPO) if u in UTMS_RCS]
            rcs_filtrado_crm = filtrar_dados_whatsapp(
                rcs_completo, utms=utms_crm_rcs, data_ini=data_ini_dt, data_fim=data_fim_dt,
                hora_ini=hora_ini, hora_fim=hora_fim, grupos_ab=grupos_ab,
                grupos_estrategicos=grupos_estrategicos, canal="rcs",
            )
            kpis_crm_rcs = calcular_kpis_whatsapp(rcs_filtrado_crm)
            grafico_funil_crm_combinado = charts.grafico_funil(
                calcular_funil_combinado_whatsapp(
                    kpis_crm_rcs, totais_crm, total_disparado=total_disparado_campanhas(utms_crm_rcs),
                ),
                cores=charts.CORES_FUNIL_COMBINADO_WHATSAPP, titulo=titulo_funil_crm, altura=560,
                textposition="outside", modo_percentual="etapa",
            )
            entregue_crm_total = kpis_crm_rcs["Entregue"] + kpis_crm_rcs["Lido"]
            enviado_crm_total = entregue_crm_total + kpis_crm_rcs["Enviado"] + kpis_crm_rcs["Nao Entregue"]
            taxa_entrega_crm = taxa(entregue_crm_total, enviado_crm_total)
            lido_crm_total = kpis_crm_rcs["Lido"]
            if lido_crm_total > 0:
                home_vs_etapa_titulo = "Home vs Lido"
                home_vs_etapa_valor = taxa(totais_crm["home"], lido_crm_total)
            else:
                home_vs_etapa_titulo = "Home vs Entrega"
                home_vs_etapa_valor = taxa(totais_crm["home"], entregue_crm_total)
        elif canal_crm == "email":
            # O relatório de e-mail (Salesforce Journey Builder) não cruza por
            # telefone com o log de CRM das campanhas avulsas — são dois programas de
            # e-mail diferentes (ver alerta na UI). Envios/Entregues/Aberturas/Cliques
            # aqui são o total estático do relatório, não filtrado por utms_crm.
            grafico_funil_crm_combinado = charts.grafico_funil(
                calcular_funil_combinado_email_salesforce(_KPIS_EMAIL_SALESFORCE, totais_crm),
                cores=charts.CORES_FUNIL_COMBINADO_SMS, titulo=titulo_funil_crm, altura=560,
                textposition="outside", modo_percentual="etapa",
            )
            taxa_entrega_crm = _KPIS_EMAIL_SALESFORCE["taxa_entrega"]
            home_vs_etapa_titulo = "Home vs Aberturas"
            home_vs_etapa_valor = taxa(totais_crm["home"], _KPIS_EMAIL_SALESFORCE["aberturas"])
        else:
            grafico_funil_crm_combinado = charts.grafico_funil_crm(crm_agregado, CANAL_LABEL_FUNIL.get(canal_crm, "Pós-Contato"))
            taxa_entrega_crm = 0.0
            home_vs_etapa_titulo = "Home vs Entrega"
            home_vs_etapa_valor = 0.0

        # Clientes únicos que receberam disparo em qualquer canal (SMS/WhatsApp
        # Ótima/Airys/RCS), respeitando os filtros globais — telefone deduplicado, sem
        # contar o mesmo cliente mais de uma vez mesmo que tenha recebido vários disparos.
        clientes_unicos_disparados = pd.concat(
            [
                filtrado["telefone_norm"], whatsapp_filtrado["telefone_norm"],
                airys_filtrado["telefone_norm"], rcs_sms_filtrado["telefone_norm"],
            ],
            ignore_index=True,
        ).nunique()

        # Funil de negociação (Home/Autenticação/Oferta/Acordo) por Grupo AB, um por
        # canal, na aba Funil por Grupo AB — usa os filtros globais (utms/grupos_ab/
        # grupos_estrategicos), não o filtro de UTM específico da aba CRM.
        def _crm_filtrado_canal(utm_medium: str, utms_permitidas: list[str]) -> pd.DataFrame:
            if crm_completo.empty:
                return crm_completo
            utms_efetivas = [u for u in (utms or CAMPANHAS_ESCOPO) if u in utms_permitidas]
            sub = crm_completo[
                (crm_completo["utm_medium"] == utm_medium) & (crm_completo["utm_campaign"].isin(utms_efetivas))
            ]
            if grupos_ab:
                sub = sub[sub["grupo_ab"].isin(grupos_ab)]
            if grupos_estrategicos:
                sub = sub[sub["grupo_estrategico"].isin(grupos_estrategicos)]
            return sub

        def _agregado_crm_grupo_ab_canal(utm_medium: str, utms_permitidas: list[str]) -> pd.DataFrame:
            sub = _crm_filtrado_canal(utm_medium, utms_permitidas)
            return agregar_crm_por_grupo_ab(sub) if not sub.empty else crm_completo.iloc[0:0]

        crm_grupo_ab_sms = _agregado_crm_grupo_ab_canal("sms", UTMS_SMS)
        crm_grupo_ab_otima = _agregado_crm_grupo_ab_canal("whatsapp", UTMS_WHATSAPP_OTIMA)
        crm_grupo_ab_airys = _agregado_crm_grupo_ab_canal("whatsapp", UTMS_WHATSAPP_AIRYS)
        crm_grupo_ab_rcs = _agregado_crm_grupo_ab_canal("rcs", UTMS_RCS)

        linhas_frase_grupo_ab = montar_tabela_frase_com_grupo(filtrado, crm_filtrado, "grupo_ab")
        linhas_frase_grupo_estrategico = montar_tabela_frase_com_grupo(filtrado, crm_filtrado, "grupo_estrategico")
        linhas_mensagem_grupo_ab = montar_tabela_mensagem_com_grupo(whatsapp_completo, crm_filtrado, "grupo_ab")
        linhas_mensagem_grupo_estrategico = montar_tabela_mensagem_com_grupo(
            whatsapp_completo, crm_filtrado, "grupo_estrategico"
        )
        linhas_mensagem_airys_grupo_ab = montar_tabela_mensagem_com_grupo(airys_completo, crm_filtrado, "grupo_ab")
        linhas_mensagem_airys_grupo_estrategico = montar_tabela_mensagem_com_grupo(
            airys_completo, crm_filtrado, "grupo_estrategico"
        )
        linhas_mensagem_rcs_grupo_ab = montar_tabela_mensagem_com_grupo(rcs_completo, crm_filtrado, "grupo_ab")
        linhas_mensagem_rcs_grupo_estrategico = montar_tabela_mensagem_com_grupo(
            rcs_completo, crm_filtrado, "grupo_estrategico"
        )

        return (
            formatar_numero(kpis["disparado"]),
            formatar_numero(kpis["enviado"]),
            formatar_numero(kpis["entregue"]),
            formatar_numero(kpis["falhou"]),
            formatar_percentual(kpis["taxa_envio"]),
            formatar_percentual(kpis["taxa_entrega"]),
            formatar_percentual(kpis["taxa_falha"]),
            formatar_numero(total_whatsapp_disparado),
            formatar_numero(kpis_whatsapp["Entregue"]),
            formatar_numero(kpis_whatsapp["Lido"]),
            formatar_numero(kpis_whatsapp["Enviado"]),
            formatar_numero(kpis_whatsapp["Nao Entregue"]),
            formatar_numero(kpis_whatsapp["Nao Enviado"]),
            formatar_numero(total_airys_disparado),
            formatar_numero(kpis_airys["Entregue"]),
            formatar_numero(kpis_airys["Lido"]),
            formatar_numero(kpis_airys["Enviado"]),
            formatar_numero(kpis_airys["Nao Entregue"]),
            formatar_numero(kpis_resposta_airys["respondeu"]),
            formatar_numero(kpis_rcs["disparado"]),
            formatar_numero(kpis_rcs["enviado"]),
            formatar_numero(kpis_rcs["entregue"]),
            formatar_numero(kpis_rcs["falhou"]),
            formatar_percentual(kpis_rcs["taxa_envio"]),
            formatar_percentual(kpis_rcs["taxa_entrega"]),
            formatar_percentual(kpis_rcs["taxa_falha"]),
            legenda,
            charts.grafico_funil(etapas),
            _tabela_funil_html(etapas),
            charts.grafico_funil(etapas_whatsapp, cores=["#8B93B8", "#3DA9FC", "#2ECC71", "#0FA968"]),
            _tabela_funil_html(etapas_whatsapp),
            charts.grafico_evolucao_horaria(filtrado),
            charts.grafico_evolucao_diaria(filtrado),
            charts.grafico_volume_utm(filtrado),
            charts.grafico_status_sms(kpis),
            charts.grafico_ranking_campanhas(agregado),
            charts.grafico_taxa_entrega_campanha(agregado),
            _tabela_component(charts.formatar_tabela_executiva(agregado), COLUNAS_TABELA_EXECUTIVA),
            _tabela_component(
                charts.formatar_tabela_whatsapp_campanha(agregado_whatsapp_campanha),
                COLUNAS_TABELA_WHATSAPP_CAMPANHA,
            ),
            charts.grafico_funil(etapas_airys, cores=["#8B93B8", "#3DA9FC", "#2ECC71", "#0FA968"]),
            _tabela_funil_html(etapas_airys),
            charts.grafico_resultado_resposta_airys(agregado_resultado_resposta_airys),
            _tabela_component(
                charts.formatar_tabela_whatsapp_campanha(agregado_airys_campanha),
                COLUNAS_TABELA_WHATSAPP_CAMPANHA,
            ),
            charts.grafico_funil(etapas_rcs),
            _tabela_funil_html(etapas_rcs),
            charts.grafico_evolucao_horaria(rcs_sms_filtrado),
            charts.grafico_evolucao_diaria(rcs_sms_filtrado),
            charts.grafico_volume_utm(rcs_sms_filtrado),
            charts.grafico_status_sms(kpis_rcs, titulo="Status do RCS"),
            charts.grafico_ranking_campanhas(agregado_rcs),
            charts.grafico_taxa_entrega_campanha(agregado_rcs),
            _tabela_component(charts.formatar_tabela_executiva(agregado_rcs), COLUNAS_TABELA_EXECUTIVA),
            charts.grafico_volume_grupo_ab(filtrado, crm_grupo_ab_sms),
            charts.grafico_taxa_entrega_grupo_ab(agregado_grupo_ab),
            _tabela_component(charts.formatar_tabela_grupo_ab(agregado_grupo_ab), COLUNAS_TABELA_GRUPO_AB),
            charts.grafico_whatsapp_por_grupo_ab(agregado_whatsapp_grupo_ab, crm_grupo_ab_otima),
            _tabela_component(
                charts.formatar_tabela_whatsapp_grupo_ab(agregado_whatsapp_grupo_ab),
                COLUNAS_TABELA_WHATSAPP_GRUPO_AB,
            ),
            charts.grafico_whatsapp_por_grupo_ab(agregado_airys_grupo_ab, crm_grupo_ab_airys),
            _tabela_component(
                charts.formatar_tabela_whatsapp_grupo_ab(agregado_airys_grupo_ab),
                COLUNAS_TABELA_WHATSAPP_GRUPO_AB,
            ),
            charts.grafico_volume_grupo_ab(rcs_sms_filtrado, crm_grupo_ab_rcs),
            charts.grafico_taxa_entrega_grupo_ab(agregado_grupo_ab_rcs),
            _tabela_component(charts.formatar_tabela_grupo_ab(agregado_grupo_ab_rcs), COLUNAS_TABELA_GRUPO_AB),
            charts.grafico_volume_grupo_estrategico(filtrado),
            charts.grafico_taxa_entrega_grupo_estrategico(agregado_grupo_estrategico),
            _tabela_grupo_estrategico_ab_component(linhas_grupo_estrategico_ab),
            charts.grafico_whatsapp_por_grupo_estrategico(agregado_whatsapp_grupo_estrategico),
            _tabela_component(
                charts.formatar_tabela_whatsapp_grupo_estrategico(agregado_whatsapp_grupo_estrategico),
                COLUNAS_TABELA_WHATSAPP_GRUPO_ESTRATEGICO,
            ),
            charts.grafico_whatsapp_por_grupo_estrategico(agregado_airys_grupo_estrategico),
            _tabela_component(
                charts.formatar_tabela_whatsapp_grupo_estrategico(agregado_airys_grupo_estrategico),
                COLUNAS_TABELA_WHATSAPP_GRUPO_ESTRATEGICO,
            ),
            charts.grafico_volume_grupo_estrategico(rcs_sms_filtrado),
            charts.grafico_taxa_entrega_grupo_estrategico(agregado_grupo_estrategico_rcs),
            _tabela_grupo_estrategico_ab_component(linhas_grupo_estrategico_ab_rcs),
            charts.grafico_taxa_entrega_frase(agregado_frase),
            charts.grafico_crm_por_frase(agregado_frase),
            _tabela_component(charts.formatar_tabela_frase(agregado_frase), COLUNAS_TABELA_FRASE),
            _tabela_texto_grupo_component(
                linhas_frase_grupo_ab, charts.GRUPO_AB_LABEL, "Frase (modelo) / Grupo AB",
            ),
            _tabela_texto_grupo_component(
                linhas_frase_grupo_estrategico, charts.GRUPO_ESTRATEGICO_LABEL,
                "Frase (modelo) / Grupo Estratégico",
            ),
            charts.grafico_status_mensagem_whatsapp(agregado_mensagem_whatsapp),
            charts.grafico_crm_por_mensagem_whatsapp(agregado_mensagem_whatsapp),
            _tabela_component(
                charts.formatar_tabela_mensagem_whatsapp(agregado_mensagem_whatsapp),
                COLUNAS_TABELA_MENSAGEM_WHATSAPP,
            ),
            _tabela_texto_grupo_component(
                linhas_mensagem_grupo_ab, charts.GRUPO_AB_LABEL, "Mensagem (modelo) / Grupo AB",
            ),
            _tabela_texto_grupo_component(
                linhas_mensagem_grupo_estrategico, charts.GRUPO_ESTRATEGICO_LABEL,
                "Mensagem (modelo) / Grupo Estratégico",
            ),
            charts.grafico_status_mensagem_whatsapp(agregado_mensagem_airys, rotulo_canal="Airys"),
            charts.grafico_crm_por_mensagem_whatsapp(agregado_mensagem_airys, rotulo_canal="Airys"),
            _tabela_component(
                charts.formatar_tabela_mensagem_whatsapp(agregado_mensagem_airys),
                COLUNAS_TABELA_MENSAGEM_WHATSAPP,
            ),
            _tabela_texto_grupo_component(
                linhas_mensagem_airys_grupo_ab, charts.GRUPO_AB_LABEL, "Template (modelo) / Grupo AB",
            ),
            _tabela_texto_grupo_component(
                linhas_mensagem_airys_grupo_estrategico, charts.GRUPO_ESTRATEGICO_LABEL,
                "Template (modelo) / Grupo Estratégico",
            ),
            charts.grafico_status_mensagem_whatsapp(agregado_mensagem_rcs, rotulo_canal="RCS"),
            charts.grafico_crm_por_mensagem_whatsapp(agregado_mensagem_rcs, rotulo_canal="RCS"),
            _tabela_component(
                charts.formatar_tabela_mensagem_whatsapp(agregado_mensagem_rcs),
                COLUNAS_TABELA_MENSAGEM_WHATSAPP,
            ),
            _tabela_texto_grupo_component(
                linhas_mensagem_rcs_grupo_ab, charts.GRUPO_AB_LABEL, "Mensagem (modelo) / Grupo AB",
            ),
            _tabela_texto_grupo_component(
                linhas_mensagem_rcs_grupo_estrategico, charts.GRUPO_ESTRATEGICO_LABEL,
                "Mensagem (modelo) / Grupo Estratégico",
            ),
            formatar_numero(totais_crm["home"]),
            formatar_numero(totais_crm["auth"]),
            formatar_numero(totais_crm["oferta"]),
            formatar_numero(totais_crm["acordo"]),
            grafico_funil_crm_combinado,
            grafico_funil_crm_airys,
            charts.grafico_crm_por_campanha(crm_agregado),
            charts.grafico_crm_por_grupo_ab(crm_agregado_grupo_ab),
            charts.grafico_crm_por_grupo_estrategico(crm_agregado_grupo_estrategico),
            _tabela_pivot_crm_component(colunas_pivot, linhas_pivot),
            _tabela_pivot_crm_component(
                colunas_pivot_ge, linhas_pivot_ge,
                titulo_coluna="Ação / Grupo Estratégico", mapa_label=charts.GRUPO_ESTRATEGICO_LABEL,
            ),
            formatar_numero(clientes_unicos_disparados),
            _tabela_component(
                charts.formatar_tabela_crm_grupo_ab(crm_grupo_ab_sms),
                ["Grupo AB", "Home", "Autenticação", "Oferta", "Acordo"],
            ),
            _tabela_component(
                charts.formatar_tabela_crm_grupo_ab(crm_grupo_ab_otima),
                ["Grupo AB", "Home", "Autenticação", "Oferta", "Acordo"],
            ),
            _tabela_component(
                charts.formatar_tabela_crm_grupo_ab(crm_grupo_ab_airys),
                ["Grupo AB", "Home", "Autenticação", "Oferta", "Acordo"],
            ),
            _tabela_component(
                charts.formatar_tabela_crm_grupo_ab(crm_grupo_ab_rcs),
                ["Grupo AB", "Home", "Autenticação", "Oferta", "Acordo"],
            ),
            formatar_percentual(taxa_entrega_crm),
            formatar_percentual(home_vs_etapa_valor),
            home_vs_etapa_titulo,
        )
