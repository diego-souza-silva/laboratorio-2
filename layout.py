"""Layout Dash/Bootstrap do dashboard executivo (tema escuro, estilo Power BI)."""
from __future__ import annotations

import calendar as calendar_mod
import datetime as dt

from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc

from data_processing import (
    GRUPO_AB_ORDEM, GRUPO_ESTRATEGICO_ORDEM,
    STATUS_FUNIL_ORDEM, agregar_email_salesforce_por_jornada, calcular_funil_email_salesforce,
    calcular_kpis_email_salesforce, campanhas_escopo, carregar_anotacoes_calendario, carregar_dados_airys,
    carregar_dados_email_salesforce, carregar_dados_rcs, carregar_dados_sms, carregar_dados_whatsapp_mensagem,
    extremos_data_hora, resumo_campanhas_por_dia,
)
from charts import (
    CORES, GRUPO_AB_LABEL, GRUPO_ESTRATEGICO_LABEL, formatar_tabela_email_salesforce,
    grafico_funil, grafico_volume_email_por_jornada, nome_curto,
)
from utils import formatar_numero, formatar_percentual

STATUS_LABEL = {
    "Entregue": "Entregue",
    "Pendente": "Pendente (em trânsito)",
    "Falhou": "Falhou",
    "Nao Processado": "Não Processado",
}


def _cartao_kpi(id_valor: str, titulo: str, icone: str, cor: str, id_titulo: str | None = None) -> dbc.Card:
    """`id_titulo`, quando informado, permite que um callback troque o rótulo do
    cartão (ex.: "Home vs Entrega" -> "Home vs Lido" dependendo do canal ativo)."""
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi {icone}", style={"color": cor, "fontSize": "1.6rem"}),
                html.Span(titulo, className="kpi-titulo", id=id_titulo) if id_titulo else
                html.Span(titulo, className="kpi-titulo"),
            ], className="kpi-cabecalho"),
            html.H3(id=id_valor, className="kpi-valor", style={"color": cor}),
        ]),
        className="cartao-kpi shadow-sm",
    )


def _cartao_kpi_estatico(valor: str, titulo: str, icone: str, cor: str) -> dbc.Card:
    """Igual `_cartao_kpi`, mas com o valor já calculado no momento em que o layout é
    montado, sem passar por callback — usado no bloco de Email (Salesforce), cujos
    dados vêm de um relatório já agregado pela plataforma (sem telefone/timestamp por
    destinatário) e por isso não respondem aos filtros globais do dashboard."""
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi {icone}", style={"color": cor, "fontSize": "1.6rem"}),
                html.Span(titulo, className="kpi-titulo"),
            ], className="kpi-cabecalho"),
            html.H3(valor, className="kpi-valor", style={"color": cor}),
        ]),
        className="cartao-kpi shadow-sm",
    )


def _tabela_estatica(registros: list[dict], colunas: list[str]):
    if not registros:
        return html.P("Nenhum dado disponível.", className="text-muted")
    return dash_table.DataTable(
        data=registros,
        columns=[{"name": nome, "id": nome} for nome in colunas],
        sort_action="native",
        filter_action="native",
        page_size=15,
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


def _linha_kpis() -> html.Div:
    cartoes_sms = [
        ("kpi-disparado", "Total Disparado", "bi-send-fill", "#8B93B8"),
        ("kpi-enviado", "Total Enviado", "bi-send-check-fill", "#3DA9FC"),
        ("kpi-entregue", "Total Entregue", "bi-check-circle-fill", "#2ECC71"),
        ("kpi-falhado", "Total Falhado", "bi-x-circle-fill", "#FF5C5C"),
        ("kpi-taxa-envio", "Taxa de Envio", "bi-graph-up", "#3DA9FC"),
        ("kpi-taxa-entrega", "Taxa de Entrega", "bi-graph-up-arrow", "#2ECC71"),
        ("kpi-taxa-falha", "Taxa de Falha", "bi-graph-down", "#FF5C5C"),
    ]
    cartoes_whatsapp_otima = [
        ("kpi-whatsapp-disparado", "Total Disparado (Ótima)", "bi-send-fill", "#8B93B8"),
        ("kpi-whatsapp-entregue", "Entregue (não lido)", "bi-check-circle-fill", "#2ECC71"),
        ("kpi-whatsapp-lido", "Lido", "bi-eye-fill", "#2ECC71"),
        ("kpi-whatsapp-enviado", "Pendente", "bi-send-check-fill", "#F5A623"),
        ("kpi-whatsapp-nao-entregue", "Não Entregue", "bi-x-circle-fill", "#FF5C5C"),
        ("kpi-whatsapp-nao-enviado", "Não Enviado", "bi-dash-circle-fill", "#8B93B8"),
    ]
    cartoes_whatsapp_airys = [
        ("kpi-airys-disparado", "Total Disparado (Airys)", "bi-send-fill", "#8B93B8"),
        ("kpi-airys-entregue", "Entregue", "bi-check-circle-fill", "#2ECC71"),
        ("kpi-airys-lido", "Lido", "bi-eye-fill", "#2ECC71"),
        ("kpi-airys-enviado", "Pendente sem Recibo", "bi-send-check-fill", "#F5A623"),
        ("kpi-airys-nao-entregue", "Falhou ou Rejeitado", "bi-x-circle-fill", "#FF5C5C"),
        ("kpi-airys-respondeu", "Respondeu após Envio", "bi-reply-fill", "#3DA9FC"),
    ]
    cartoes_rcs = [
        ("kpi-rcs-disparado", "Total Disparado", "bi-send-fill", "#8B93B8"),
        ("kpi-rcs-enviado", "Total Enviado", "bi-send-check-fill", "#3DA9FC"),
        ("kpi-rcs-entregue", "Total Entregue", "bi-check-circle-fill", "#2ECC71"),
        ("kpi-rcs-falhado", "Total Falhado", "bi-x-circle-fill", "#FF5C5C"),
        ("kpi-rcs-taxa-envio", "Taxa de Envio", "bi-graph-up", "#3DA9FC"),
        ("kpi-rcs-taxa-entrega", "Taxa de Entrega", "bi-graph-up-arrow", "#2ECC71"),
        ("kpi-rcs-taxa-falha", "Taxa de Falha", "bi-graph-down", "#FF5C5C"),
    ]
    return html.Div([
        html.Span("Todos os Canais", className="rotulo-filtro"),
        dbc.Row(
            [
                dbc.Col(_cartao_kpi(
                    "kpi-clientes-unicos", "Clientes Únicos (Disparados)", "bi-people-fill", "#3DA9FC",
                ), xs=12, sm=6, md=4, lg=3),
                dbc.Col(_cartao_kpi(
                    "kpi-spin", "SPIN (Disparos ÷ Clientes Únicos)", "bi-arrow-repeat", "#F5A623",
                ), xs=12, sm=6, md=4, lg=3),
            ],
            className="g-3 mb-3",
        ),
        html.Span("SMS (Kolmeya)", className="rotulo-filtro"),
        dbc.Row(
            [dbc.Col(_cartao_kpi(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes_sms],
            className="g-3 mb-3",
        ),
        html.Span("WhatsApp — Ótima", className="rotulo-filtro"),
        dbc.Row(
            [dbc.Col(_cartao_kpi(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes_whatsapp_otima],
            className="g-3 mb-3",
        ),
        html.Span("WhatsApp — Airys", className="rotulo-filtro"),
        dbc.Row(
            [dbc.Col(_cartao_kpi(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes_whatsapp_airys],
            className="g-3 mb-3",
        ),
        html.Span("RCS (Ótima)", className="rotulo-filtro"),
        dbc.Row(
            [dbc.Col(_cartao_kpi(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes_rcs],
            className="g-3 mb-3",
        ),
    ])


def _painel_filtros() -> dbc.Card:
    campanhas = campanhas_escopo()
    df = carregar_dados_sms()
    data_min, data_max, hora_min, hora_max = extremos_data_hora(
        df, carregar_dados_whatsapp_mensagem(), carregar_dados_airys(),
        carregar_dados_rcs(),
    )

    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Campanha (UTM)", className="rotulo-filtro"),
                    dcc.Dropdown(
                        id="filtro-utm",
                        options=[{"label": nome_curto(u), "value": u} for u in campanhas],
                        value=campanhas, multi=True, placeholder="Todas as campanhas",
                        className="dash-dropdown-escuro",
                    ),
                ], md=4),
                dbc.Col([
                    html.Label("Período", className="rotulo-filtro"),
                    dcc.DatePickerRange(
                        id="filtro-data",
                        min_date_allowed=data_min, max_date_allowed=data_max,
                        start_date=data_min, end_date=data_max,
                        display_format="DD/MM/YYYY", className="w-100",
                    ),
                ], md=3),
                dbc.Col([
                    html.Label("Hora (0h–23h)", className="rotulo-filtro"),
                    dcc.RangeSlider(
                        id="filtro-hora", min=0, max=23, step=1, value=[hora_min, hora_max],
                        marks={h: str(h) for h in range(0, 24, 3)},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ], md=3),
                dbc.Col([
                    html.Label("Status", className="rotulo-filtro"),
                    dcc.Dropdown(
                        id="filtro-status",
                        options=[{"label": STATUS_LABEL[s], "value": s} for s in STATUS_FUNIL_ORDEM],
                        value=STATUS_FUNIL_ORDEM, multi=True, placeholder="Todos os status",
                        className="dash-dropdown-escuro",
                    ),
                ], md=2),
            ], className="g-3 align-items-end"),
            dbc.Row([
                dbc.Col([
                    html.Label("Prioridade (segmentação de propensão)", className="rotulo-filtro"),
                    dcc.Dropdown(
                        id="filtro-grupo-ab",
                        options=[{"label": GRUPO_AB_LABEL.get(g, g), "value": g} for g in GRUPO_AB_ORDEM],
                        value=GRUPO_AB_ORDEM, multi=True, placeholder="Todos os grupos",
                        className="dash-dropdown-escuro",
                    ),
                ], md=6),
                dbc.Col([
                    html.Label("Grupo Estratégico", className="rotulo-filtro"),
                    dcc.Dropdown(
                        id="filtro-grupo-estrategico",
                        options=[
                            {"label": GRUPO_ESTRATEGICO_LABEL.get(g, g), "value": g}
                            for g in GRUPO_ESTRATEGICO_ORDEM
                        ],
                        value=GRUPO_ESTRATEGICO_ORDEM, multi=True, placeholder="Todos os grupos",
                        className="dash-dropdown-escuro",
                    ),
                ], md=6),
            ], className="g-3 align-items-end mt-1"),
            html.P(
                "Números de disparo sem confirmação de horário na plataforma (\"Não Processado\") "
                "são mantidos em todos os filtros de Data/Hora, já que não têm um momento de "
                "envio conhecido para serem excluídos com precisão.",
                className="legenda-registros mt-2 mb-0",
            ),
        ]),
        className="cartao-filtros shadow-sm mb-3",
    )


def _grafico_card(titulo: str, id_grafico: str, altura: str = "360px") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(dcc.Graph(id=id_grafico, config={"displayModeBar": False}, style={"height": altura})),
        className="cartao-grafico shadow-sm h-100",
    )


def _bloco_funil_detalhe(titulo_funil: str, id_funil: str, titulo_detalhe: str, id_detalhe: str) -> dbc.Row:
    return dbc.Row([
        dbc.Col(_grafico_card(titulo_funil, id_funil), md=7),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6(titulo_detalhe, className="mb-3"),
                    html.Div(id=id_detalhe),
                ]),
                className="cartao-grafico shadow-sm h-100",
            ),
            md=5,
        ),
    ], className="g-3 mb-3")


def _aba_funil_sms() -> html.Div:
    return html.Div([
        html.Span("SMS (Kolmeya)", className="rotulo-filtro"),
        _bloco_funil_detalhe("Funil Geral", "grafico-funil", "Detalhe por Etapa", "tabela-funil-detalhe"),

        dbc.Row([
            dbc.Col(_grafico_card("Evolução por Hora", "grafico-evolucao-horaria"), md=6),
            dbc.Col(_grafico_card("Evolução Diária", "grafico-evolucao-diaria"), md=6),
        ], className="g-3 mb-3"),

        dbc.Row([
            dbc.Col(_grafico_card("Volume por Campanha", "grafico-volume-utm"), md=6),
            dbc.Col(_grafico_card("Status dos SMS", "grafico-status-sms"), md=6),
        ], className="g-3 mb-3"),

        dbc.Row([
            dbc.Col(_grafico_card("Ranking de Campanhas", "grafico-ranking-campanhas"), md=6),
            dbc.Col(_grafico_card("Taxa de Entrega por Campanha", "grafico-taxa-entrega"), md=6),
        ], className="g-3 mb-3"),

        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva por Campanha", className="mb-3"),
                html.Div(id="tabela-executiva-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("WhatsApp — Ótima", className="rotulo-filtro"),
        _bloco_funil_detalhe(
            "Funil de WhatsApp (Ótima)", "grafico-funil-whatsapp",
            "Detalhe por Etapa (Ótima)", "tabela-funil-whatsapp-detalhe",
        ),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva de WhatsApp por Campanha (Ótima)", className="mb-3"),
                html.Div(id="tabela-whatsapp-campanha-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("WhatsApp — Airys", className="rotulo-filtro"),
        _bloco_funil_detalhe(
            "Funil de WhatsApp (Airys)", "grafico-funil-airys",
            "Detalhe por Etapa (Airys)", "tabela-funil-airys-detalhe",
        ),
        dbc.Row([
            dbc.Col(_grafico_card("Resultado da Resposta (Airys)", "grafico-resultado-resposta-airys"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva de WhatsApp por Campanha (Airys)", className="mb-3"),
                html.Div(id="tabela-airys-campanha-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("RCS (Ótima)", className="rotulo-filtro"),
        _bloco_funil_detalhe(
            "Funil de RCS", "grafico-funil-rcs", "Detalhe por Etapa (RCS)", "tabela-funil-rcs-detalhe",
        ),
        dbc.Row([
            dbc.Col(_grafico_card("Evolução por Hora (RCS)", "grafico-evolucao-horaria-rcs"), md=6),
            dbc.Col(_grafico_card("Evolução Diária (RCS)", "grafico-evolucao-diaria-rcs"), md=6),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Volume por Campanha (RCS)", "grafico-volume-utm-rcs"), md=6),
            dbc.Col(_grafico_card("Status do RCS", "grafico-status-rcs"), md=6),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Ranking de Campanhas (RCS)", "grafico-ranking-campanhas-rcs"), md=6),
            dbc.Col(_grafico_card("Taxa de Entrega por Campanha (RCS)", "grafico-taxa-entrega-rcs"), md=6),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva por Campanha (RCS)", className="mb-3"),
                html.Div(id="tabela-executiva-rcs-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Div(bloco_email_salesforce(), id="bloco-email-salesforce-container"),
    ])


def bloco_email_salesforce() -> html.Div:
    """Bloco de e-mail (Salesforce Journey Builder) na aba Funil Geral. Diferente dos
    outros blocos, o conteúdo não responde aos filtros globais de campanha/data/hora/
    grupo_ab (o export vem já agregado por e-mail/dia pela própria plataforma, sem
    telefone/timestamp por destinatário)."""
    df = carregar_dados_email_salesforce()
    kpis = calcular_kpis_email_salesforce(df)
    etapas = calcular_funil_email_salesforce(kpis)
    agregado_jornada = agregar_email_salesforce_por_jornada(df)

    cartoes = [
        (formatar_numero(kpis["envios"]), "Total Envios", "bi-send-fill", "#8B93B8"),
        (formatar_numero(kpis["entregues"]), "Total Entregues", "bi-check-circle-fill", "#2ECC71"),
        (formatar_percentual(kpis["taxa_entrega"]), "Taxa de Entrega", "bi-graph-up-arrow", "#2ECC71"),
        (formatar_percentual(kpis["taxa_bounce"]), "Taxa de Bounce", "bi-x-circle-fill", "#FF5C5C"),
        (formatar_numero(kpis["aberturas"]), "Total Aberturas", "bi-envelope-open-fill", "#F5A623"),
        (formatar_percentual(kpis["taxa_abertura"]), "Taxa de Abertura", "bi-eye-fill", "#F5A623"),
        (formatar_numero(kpis["cliques"]), "Total Cliques", "bi-cursor-fill", "#3DA9FC"),
        (formatar_percentual(kpis["taxa_ctr"]), "CTR", "bi-graph-up", "#3DA9FC"),
        (formatar_percentual(kpis["taxa_ctor"]), "CTOR", "bi-bullseye", "#3DA9FC"),
        (f"{kpis['eficiencia']:.3f}%".replace(".", ","), "Eficiência", "bi-lightning-fill", "#2ECC71"),
    ]

    return html.Div([
        html.Span("Email (Salesforce)", className="rotulo-filtro"),
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "Seção baseada no relatório \"Main Metrics\" do Salesforce Journey "
                "Builder (ARQUIVOS DE RETORNO EMAIL SALESFORCE/) — já vem agregado por "
                "e-mail/dia pela própria plataforma, sem telefone nem horário por "
                "destinatário, então não responde aos filtros globais de campanha, "
                "período, hora ou grupo acima.",
            ],
            color="info", className="mb-3",
        ),
        dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                html.B("Ponto de atenção: "),
                "\"Total Envios\" conta eventos de envio, não clientes únicos. Cada "
                "Jornada dispara uma sequência automática de e-mails pro mesmo cliente "
                "em dias diferentes (o sufixo \"-d1/-d2/-d3/-d4\" no nome do e-mail é o "
                "1º/2º/3º/4º envio da sequência, não um cliente novo) — por isso a "
                "Jornada \"3k\" (nome sugere ~3 mil clientes) soma 11.831 Envios, quase "
                "4x mais. Confirmado nos dados: cada partição da jornada mantém o "
                "mesmo volume (~1.000) do d1 ao d4, caindo só pelos poucos que "
                "descadastraram/bounceram no caminho — é o mesmo público recebendo "
                "vários e-mails, não um público 4x maior. Por isso os volumes aqui não "
                "são comparáveis aos das campanhas avulsas de e-mail em ARQUIVOS PARA "
                "DISPAROS/ (disparo único pra uma lista fixa).",
            ],
            color="warning", className="mb-3",
        ),
        dbc.Row(
            [dbc.Col(_cartao_kpi_estatico(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes],
            className="g-3 mb-3",
        ),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(
                        figure=grafico_funil(
                            etapas, cores=[CORES["disparado"], CORES["entregue"], "#F5A623", "#3DA9FC"],
                            titulo="Funil de Envio (Email Salesforce)",
                        ),
                        config={"displayModeBar": False}, style={"height": "360px"},
                    )),
                    className="cartao-grafico shadow-sm h-100",
                ), md=7,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(
                        figure=grafico_volume_email_por_jornada(agregado_jornada),
                        config={"displayModeBar": False}, style={"height": "360px"},
                    )),
                    className="cartao-grafico shadow-sm h-100",
                ), md=5,
            ),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva por E-mail (Salesforce)", className="mb-3"),
                _tabela_estatica(
                    formatar_tabela_email_salesforce(df),
                    ["Jornada", "E-mail", "Assunto", "Envios", "% envios", "Entregues", "Entrega",
                     "Bounce", "Aberturas", "Abertura", "Cliques", "CTR", "CTOR", "Eficiência"],
                ),
            ]),
            className="cartao-grafico shadow-sm",
        ),
    ])


def _aba_grupo_ab() -> html.Div:
    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "Segmentação de propensão (grupo_ab) trazida da base de clientes via "
                "cruzamento por telefone (equivalente ao PROCX manual). Telefones não "
                "encontrados na base aparecem como \"Não Classificado\".",
            ],
            color="info", className="mb-3",
        ),
        html.Span("SMS (Kolmeya)", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(_grafico_card("Volume por Prioridade", "grafico-volume-grupo-ab", altura="1500px"), md=12),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Taxa de Entrega por Prioridade", "grafico-taxa-entrega-grupo-ab"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva por Prioridade", className="mb-3"),
                html.Div(id="tabela-grupo-ab-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),
        dbc.Card(
            dbc.CardBody([
                html.H6("Home / Autenticação / Oferta / Acordo por Prioridade (SMS)", className="mb-3"),
                html.Div(id="tabela-crm-grupo-ab-sms-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("WhatsApp — Ótima", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(_grafico_card("Resultado de WhatsApp por Prioridade (Ótima)", "grafico-whatsapp-grupo-ab"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva de WhatsApp por Prioridade (Ótima)", className="mb-3"),
                html.Div(id="tabela-whatsapp-grupo-ab-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),
        dbc.Card(
            dbc.CardBody([
                html.H6("Home / Autenticação / Oferta / Acordo por Prioridade (WhatsApp Ótima)", className="mb-3"),
                html.Div(id="tabela-crm-grupo-ab-whatsapp-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("WhatsApp — Airys", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(_grafico_card("Resultado de WhatsApp por Prioridade (Airys)", "grafico-airys-grupo-ab"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva de WhatsApp por Prioridade (Airys)", className="mb-3"),
                html.Div(id="tabela-airys-grupo-ab-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),
        dbc.Card(
            dbc.CardBody([
                html.H6("Home / Autenticação / Oferta / Acordo por Prioridade (WhatsApp Airys)", className="mb-3"),
                html.Div(id="tabela-crm-grupo-ab-airys-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("RCS (Ótima)", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(_grafico_card("Volume por Prioridade (RCS)", "grafico-volume-grupo-ab-rcs", altura="1500px"), md=12),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Taxa de Entrega por Prioridade (RCS)", "grafico-taxa-entrega-grupo-ab-rcs"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva por Prioridade (RCS)", className="mb-3"),
                html.Div(id="tabela-grupo-ab-rcs-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),
        dbc.Card(
            dbc.CardBody([
                html.H6("Home / Autenticação / Oferta / Acordo por Prioridade (RCS)", className="mb-3"),
                html.Div(id="tabela-crm-grupo-ab-rcs-container"),
            ]),
            className="cartao-grafico shadow-sm",
        ),
    ])


def _aba_grupo_estrategico() -> html.Div:
    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "Grupo Estratégico (Abandono Carrinho / Cadastrado / Engajado / Topo de "
                "Funil) trazido da base de clientes via cruzamento por telefone, ou direto "
                "do arquivo de disparo quando ele já traz essa coluna. Telefones não "
                "encontrados na base aparecem como \"Não Classificado\".",
            ],
            color="info", className="mb-3",
        ),
        html.Span("SMS (Kolmeya)", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(_grafico_card("Volume por Grupo Estratégico", "grafico-volume-grupo-estrategico"), md=6),
            dbc.Col(_grafico_card("Taxa de Entrega por Grupo Estratégico", "grafico-taxa-entrega-grupo-estrategico"), md=6),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Grupo Estratégico × Prioridade (detalhado)", className="mb-3"),
                html.Div(id="tabela-grupo-estrategico-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("WhatsApp — Ótima", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(
                _grafico_card("Resultado de WhatsApp por Grupo Estratégico (Ótima)", "grafico-whatsapp-grupo-estrategico"),
                md=12,
            ),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva de WhatsApp por Grupo Estratégico (Ótima)", className="mb-3"),
                html.Div(id="tabela-whatsapp-grupo-estrategico-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("WhatsApp — Airys", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(
                _grafico_card("Resultado de WhatsApp por Grupo Estratégico (Airys)", "grafico-airys-grupo-estrategico"),
                md=12,
            ),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva de WhatsApp por Grupo Estratégico (Airys)", className="mb-3"),
                html.Div(id="tabela-airys-grupo-estrategico-container"),
            ]),
            className="cartao-grafico shadow-sm mb-4",
        ),

        html.Span("RCS (Ótima)", className="rotulo-filtro"),
        dbc.Row([
            dbc.Col(_grafico_card("Volume por Grupo Estratégico (RCS)", "grafico-volume-grupo-estrategico-rcs"), md=6),
            dbc.Col(
                _grafico_card("Taxa de Entrega por Grupo Estratégico (RCS)", "grafico-taxa-entrega-grupo-estrategico-rcs"),
                md=6,
            ),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Grupo Estratégico × Prioridade (RCS, detalhado)", className="mb-3"),
                html.Div(id="tabela-grupo-estrategico-rcs-container"),
            ]),
            className="cartao-grafico shadow-sm",
        ),
    ])


def _aba_conversao_crm() -> html.Div:
    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-question-circle-fill me-2"),
                html.B("O que é \"Não Classificado\"? "),
                "É o cliente cujo telefone não foi encontrado na base de segmentação "
                "(ARQUIVO DA BASE INTEIRA) usada para calcular o grupo_ab (P1 Máxima a "
                "P4 Baixa). Isso não quer dizer que o disparo não aconteceu — no SMS e no "
                "RCS, por exemplo, praticamente todo \"Não Classificado\" é um cliente que "
                "de fato recebeu o disparo, só não tem propensão cadastrada/cruzada. Já no "
                "WhatsApp Airys esse grupo tende a ser maior porque o telefone do retorno "
                "é reconstruído a partir de outro campo do arquivo (não vem direto), e "
                "às vezes não bate exatamente com o telefone do disparo original.",
            ],
            color="warning", className="mb-3",
        ),
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "Seção auxiliar baseada no log de CRM (negociação), não no log de envio. "
                "Restrita às campanhas cadastradas em ARQUIVOS PARA DISPAROS/. Escolha o "
                "canal abaixo (Pós-SMS/Pós-WhatsApp/Pós-RCS/Pós-Email) — mostra o que "
                "aconteceu depois do clique: Home → Autenticação → Oferta → Acordo.",
            ],
            color="info", className="mb-3",
        ),
        html.Div([
            html.Button("Pós-SMS", id="btn-canal-sms", n_clicks=0, className="aba-botao aba-ativa"),
            html.Button("Pós-WhatsApp", id="btn-canal-whatsapp", n_clicks=0, className="aba-botao"),
            html.Button("Pós-RCS", id="btn-canal-rcs", n_clicks=0, className="aba-botao"),
            html.Button("Pós-Email", id="btn-canal-email", n_clicks=0, className="aba-botao"),
        ], className="barra-abas mb-3"),
        dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        html.Label("Campanha (UTM) — CRM", className="rotulo-filtro"),
                        dcc.Dropdown(
                            id="filtro-utm-crm",
                            options=[{"label": nome_curto(u), "value": u} for u in campanhas_escopo()],
                            value=campanhas_escopo(), multi=True, placeholder="Todas as campanhas",
                            className="dash-dropdown-escuro",
                        ),
                    ], md=12),
                ], className="g-3 align-items-end"),
            ),
            className="cartao-filtros shadow-sm mb-3",
        ),
        dbc.Row([
            dbc.Col(_cartao_kpi("kpi-crm-home", "Home", "bi-house-door-fill", "#8B93B8"), xs=12, sm=6, md=4, lg=True),
            dbc.Col(
                _cartao_kpi("kpi-crm-auth", "Autenticação", "bi-shield-lock-fill", "#3DA9FC"),
                xs=12, sm=6, md=4, lg=True,
            ),
            dbc.Col(
                _cartao_kpi("kpi-crm-oferta", "Oferta Apresentada", "bi-tag-fill", "#F5A623"),
                xs=12, sm=6, md=4, lg=True,
            ),
            dbc.Col(
                _cartao_kpi("kpi-crm-acordo", "Acordo Gerado", "bi-file-earmark-check-fill", "#2ECC71"),
                xs=12, sm=6, md=4, lg=True,
            ),
            dbc.Col(
                _cartao_kpi("kpi-crm-taxa-entrega", "Taxa de Entrega", "bi-graph-up-arrow", "#2ECC71"),
                xs=12, sm=6, md=4, lg=True,
            ),
            dbc.Col(
                _cartao_kpi(
                    "kpi-crm-home-vs-etapa", "Home vs Entrega", "bi-signpost-split-fill", "#3DA9FC",
                    id_titulo="kpi-crm-home-vs-etapa-titulo",
                ),
                xs=12, sm=6, md=4, lg=True,
            ),
            dbc.Col(
                _cartao_kpi(
                    "kpi-crm-home-vs-lido-airys", "Home vs Lido — Airys", "bi-signpost-split-fill", "#F5A623",
                ),
                xs=12, sm=6, md=4, lg=True, id="col-kpi-home-vs-lido-airys", style={"display": "none"},
            ),
        ], className="g-3 mb-3"),
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "O funil abaixo é ponta a ponta: continua o funil de entrega (Disparado → "
                "Enviado → Entregue, e no WhatsApp também Lido) direto no funil de "
                "negociação (Home → Autenticação → Oferta → Acordo), na mesma campanha "
                "selecionada no filtro \"Campanha (UTM) — CRM\" acima.",
            ],
            color="info", className="mb-3",
        ),
        html.Div(
            dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle-fill me-2"),
                    html.B("Ponto de atenção: "),
                    "os passos \"Envios → Entregues → Aberturas → Cliques\" abaixo vêm "
                    "do relatório do Salesforce Journey Builder (aba Funil Geral), que é "
                    "um programa de e-mail separado das campanhas avulsas por trás do "
                    "\"Home → Autenticação → Oferta → Acordo\" — os dois lados NÃO são "
                    "cruzados por telefone, então esse funil é uma referência lado a "
                    "lado (volume de e-mail do período todo + resultado de negociação "
                    "da campanha selecionada), não um funil rigoroso onde cada etapa é "
                    "um subconjunto direto da anterior.",
                ],
                color="warning", className="mb-3",
            ),
            id="alerta-funil-crm-email",
            style={"display": "none"},
        ),
        dbc.Row([
            dbc.Col(_grafico_card("Funil de Conversão", "grafico-funil-crm", altura="620px"), md=12),
        ], className="g-3 mb-3"),
        html.Div(
            dbc.Row([
                dbc.Col(
                    _grafico_card("Funil de Conversão (Airys)", "grafico-funil-crm-airys", altura="620px"),
                    md=12,
                ),
            ], className="g-3 mb-3"),
            id="bloco-funil-crm-airys",
            style={"display": "none"},
        ),
        dbc.Row([
            dbc.Col(_grafico_card("Ações de CRM por Prioridade", "grafico-crm-grupo-ab"), md=6),
            dbc.Col(_grafico_card("Ações de CRM por Grupo Estratégico", "grafico-crm-grupo-estrategico"), md=6),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Ações de CRM por Campanha", "grafico-crm-campanha"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Ação × Campanha × Prioridade (detalhado)", className="mb-3"),
                html.Div(id="tabela-crm-pivot-container"),
            ]),
            className="cartao-grafico shadow-sm mb-3",
        ),
        dbc.Card(
            dbc.CardBody([
                html.H6("Ação × Campanha × Grupo Estratégico (detalhado)", className="mb-3"),
                html.Div(id="tabela-crm-pivot-estrategico-container"),
            ]),
            className="cartao-grafico shadow-sm mb-3",
        ),
        html.Div(
            [
                dbc.Alert(
                    [
                        html.I(className="bi bi-chat-left-text-fill me-2"),
                        "Resultado por frase de SMS: cada envio tem um link único por cliente, então "
                        "as mensagens são agrupadas pelo texto-modelo (sem o link). Abaixo tem tanto a "
                        "taxa de entrega (log de envio) quanto o resultado final no CRM — Home → "
                        "Autenticação → Oferta → Acordo — cruzado por telefone com o canal selecionado "
                        "acima.",
                    ],
                    color="secondary", className="mb-3",
                ),
                dbc.Row([
                    dbc.Col(_grafico_card("Taxa de Entrega por Frase (SMS)", "grafico-taxa-entrega-frase", altura="420px"), md=6),
                    dbc.Col(_grafico_card("Resultado de CRM por Frase (SMS)", "grafico-crm-frase", altura="420px"), md=6),
                ], className="g-3 mb-3"),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Tabela Executiva por Frase (SMS) — com resultado final", className="mb-3"),
                        html.Div(id="tabela-frase-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Alert(
                    [
                        html.I(className="bi bi-bar-chart-fill me-2"),
                        "Resultado qualitativo por frase: o mesmo resultado de CRM acima, agora "
                        "com o grupo_ab/grupo_estrategico aninhado dentro de cada frase — mostra "
                        "qual segmento converte melhor em cada mensagem.",
                    ],
                    color="secondary", className="mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Frase × Prioridade", className="mb-3"),
                        html.Div(id="tabela-frase-grupo-ab-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Frase × Grupo Estratégico", className="mb-3"),
                        html.Div(id="tabela-frase-grupo-estrategico-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
            ],
            id="secao-frase-sms",
        ),
        html.Div(
            [
                dbc.Alert(
                    [
                        html.I(className="bi bi-whatsapp me-2"),
                        "Resultado por mensagem de WhatsApp (retorno Otima): cada envio tem a "
                        "saudação personalizada com o primeiro nome do cliente, então as "
                        "mensagens são agrupadas pelo texto-modelo (sem o nome). Mostra o status "
                        "final de cada envio (Entregue/Lido/Enviado/Não Entregue/Não Enviado) e "
                        "o resultado final no CRM (Home/Autenticação/Oferta/Acordo), cruzado por "
                        "telefone.",
                    ],
                    color="secondary", className="mb-3",
                ),
                dbc.Row([
                    dbc.Col(
                        _grafico_card(
                            "Status de Entrega por Mensagem (WhatsApp)",
                            "grafico-status-mensagem-whatsapp", altura="420px",
                        ), md=6,
                    ),
                    dbc.Col(
                        _grafico_card(
                            "Resultado de CRM por Mensagem (WhatsApp)",
                            "grafico-crm-mensagem-whatsapp", altura="420px",
                        ), md=6,
                    ),
                ], className="g-3 mb-3"),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Tabela Executiva por Mensagem (WhatsApp) — com resultado final", className="mb-3"),
                        html.Div(id="tabela-mensagem-whatsapp-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Alert(
                    [
                        html.I(className="bi bi-bar-chart-fill me-2"),
                        "Resultado qualitativo por mensagem: o mesmo resultado de CRM acima, agora "
                        "com o grupo_ab/grupo_estrategico aninhado dentro de cada mensagem — mostra "
                        "qual segmento converte melhor em cada mensagem.",
                    ],
                    color="secondary", className="mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Mensagem × Prioridade", className="mb-3"),
                        html.Div(id="tabela-mensagem-whatsapp-grupo-ab-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Mensagem × Grupo Estratégico", className="mb-3"),
                        html.Div(id="tabela-mensagem-whatsapp-grupo-estrategico-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-4",
                ),

                dbc.Alert(
                    [
                        html.I(className="bi bi-whatsapp me-2"),
                        "Resultado por template do WhatsApp AIRYS (retorno Airys): mesmo "
                        "processamento acima, aplicado ao provedor Airys — status final de "
                        "cada envio e o resultado final no CRM, cruzado por telefone.",
                    ],
                    color="secondary", className="mb-3",
                ),
                dbc.Row([
                    dbc.Col(
                        _grafico_card(
                            "Status de Entrega por Template (Airys)",
                            "grafico-status-mensagem-airys", altura="420px",
                        ), md=6,
                    ),
                    dbc.Col(
                        _grafico_card(
                            "Resultado de CRM por Template (Airys)",
                            "grafico-crm-mensagem-airys", altura="420px",
                        ), md=6,
                    ),
                ], className="g-3 mb-3"),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Tabela Executiva por Template (Airys) — com resultado final", className="mb-3"),
                        html.Div(id="tabela-mensagem-airys-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Template × Prioridade (Airys)", className="mb-3"),
                        html.Div(id="tabela-mensagem-airys-grupo-ab-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Template × Grupo Estratégico (Airys)", className="mb-3"),
                        html.Div(id="tabela-mensagem-airys-grupo-estrategico-container"),
                    ]),
                    className="cartao-grafico shadow-sm",
                ),
            ],
            id="secao-mensagem-whatsapp",
            style={"display": "none"},
        ),
        html.Div(
            [
                dbc.Alert(
                    [
                        html.I(className="bi bi-broadcast me-2"),
                        "Resultado por mensagem de RCS (retorno Ótima): mesmo processamento "
                        "usado no WhatsApp — status final de cada envio (Entregue/Lido/"
                        "Enviado/Não Entregue/Não Enviado) e o resultado final no CRM "
                        "(Home/Autenticação/Oferta/Acordo), cruzado por telefone.",
                    ],
                    color="secondary", className="mb-3",
                ),
                dbc.Row([
                    dbc.Col(
                        _grafico_card(
                            "Status de Entrega por Mensagem (RCS)",
                            "grafico-status-mensagem-rcs", altura="420px",
                        ), md=6,
                    ),
                    dbc.Col(
                        _grafico_card(
                            "Resultado de CRM por Mensagem (RCS)",
                            "grafico-crm-mensagem-rcs", altura="420px",
                        ), md=6,
                    ),
                ], className="g-3 mb-3"),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Tabela Executiva por Mensagem (RCS) — com resultado final", className="mb-3"),
                        html.Div(id="tabela-mensagem-rcs-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Mensagem × Prioridade (RCS)", className="mb-3"),
                        html.Div(id="tabela-mensagem-rcs-grupo-ab-container"),
                    ]),
                    className="cartao-grafico shadow-sm mb-3",
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Resultado por Mensagem × Grupo Estratégico (RCS)", className="mb-3"),
                        html.Div(id="tabela-mensagem-rcs-grupo-estrategico-container"),
                    ]),
                    className="cartao-grafico shadow-sm",
                ),
            ],
            id="secao-mensagem-rcs",
            style={"display": "none"},
        ),
    ])


MESES_LABEL = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
_DIAS_SEMANA_LABEL = [
    "Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado",
]


def montar_grade_calendario(ano: int, mes: int) -> html.Div:
    """Monta a grade do mês (semana começando no domingo) — cada dia mostra as
    campanhas de fato disparadas naquela data (`resumo_campanhas_por_dia`, direto de
    ARQUIVOS PARA DISPAROS/) e uma `dcc.Textarea` de anotação livre, já carregada com o
    texto salvo (`carregar_anotacoes_calendario`). O id da textarea usa pattern-matching
    (`{"type": "anotacao-calendario-dia", "data": <iso>}`) pro callback de salvar
    conseguir ler todas de uma vez, independente de quantos dias o mês tem."""
    resumo = resumo_campanhas_por_dia()
    anotacoes = carregar_anotacoes_calendario()
    semanas = calendar_mod.Calendar(firstweekday=6).monthdayscalendar(ano, mes)

    cabecalho = html.Div(
        [html.Div(d.upper(), className="calendario-dia-semana-label") for d in _DIAS_SEMANA_LABEL],
        className="calendario-grid calendario-cabecalho",
    )

    linhas = [cabecalho]
    for semana in semanas:
        celulas = []
        for dia in semana:
            if dia == 0:
                celulas.append(html.Div(className="calendario-dia calendario-dia-fora"))
                continue
            data_iso = f"{ano:04d}-{mes:02d}-{dia:02d}"
            campanhas_dia = resumo.get(data_iso, [])

            filhos = [html.Div(str(dia), className="calendario-dia-numero")]
            if campanhas_dia:
                blocos = []
                for c in campanhas_dia:
                    grupo_label = GRUPO_ESTRATEGICO_LABEL.get(c["grupo_estrategico"], c["grupo_estrategico"])
                    bloco = [
                        html.Div(f"{grupo_label} ({dia:02d}/{mes:02d})", className="calendario-campanha-titulo"),
                        html.Div(
                            f"{formatar_numero(c['volume'])} disparos · {c['fornecedor']} ({c['canal']})",
                            className="calendario-campanha-info",
                        ),
                    ]
                    if c.get("frase"):
                        trecho = c["frase"] if len(c["frase"]) <= 110 else c["frase"][:107] + "..."
                        bloco.append(html.Div(trecho, className="calendario-campanha-frase"))
                    blocos.append(html.Div(bloco, className="calendario-campanha"))
                filhos.append(html.Div(blocos, className="calendario-campanhas-lista"))

            filhos.append(dcc.Textarea(
                id={"type": "anotacao-calendario-dia", "data": data_iso},
                value=anotacoes.get(data_iso, ""),
                placeholder="Anotação do dia...",
                className="calendario-anotacao",
            ))

            classe = "calendario-dia" + (" calendario-dia-com-campanha" if campanhas_dia else "")
            celulas.append(html.Div(filhos, className=classe))
        linhas.append(html.Div(celulas, className="calendario-grid"))

    return html.Div(linhas, className="calendario-mes")


def _aba_calendario() -> html.Div:
    resumo = resumo_campanhas_por_dia()
    if resumo:
        ultima_data = max(resumo.keys())
        ano_inicial, mes_inicial = int(ultima_data[:4]), int(ultima_data[5:7])
    else:
        hoje = dt.date.today()
        ano_inicial, mes_inicial = hoje.year, hoje.month

    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-calendar3 me-2"),
                "Calendário de estratégia: cada dia mostra automaticamente as campanhas "
                "de fato disparadas naquela data (Grupo Estratégico, volume, canal e "
                "fornecedor, direto de ARQUIVOS PARA DISPAROS/) e um campo livre pra "
                "anotar o que foi feito ou planejado. Escreva à vontade e clique em "
                "\"Salvar Anotações\" — o texto fica gravado em ANOTACOES_CALENDARIO.json "
                "e continua aqui mesmo depois de reiniciar o dashboard.",
            ],
            color="info", className="mb-3",
        ),
        html.Div([
            dbc.Button("‹", id="btn-calendario-mes-anterior", color="secondary", size="sm", className="me-2"),
            html.Span(
                id="calendario-mes-label",
                style={"minWidth": "170px", "textAlign": "center", "display": "inline-block"},
                className="fw-bold",
            ),
            dbc.Button("›", id="btn-calendario-mes-seguinte", color="secondary", size="sm", className="ms-2"),
            html.Div(style={"flex": "1"}),
            dbc.Button("Salvar Anotações", id="btn-salvar-calendario", color="primary"),
            html.Span(id="status-salvar-calendario", className="legenda-registros ms-3"),
        ], className="d-flex align-items-center mb-3"),
        dcc.Store(id="calendario-ano-mes", data={"ano": ano_inicial, "mes": mes_inicial}),
        html.Div(id="calendario-grid-container"),
    ])


def _aba_custos() -> html.Div:
    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-currency-dollar me-2"),
                html.B("Como o custo é calculado: "),
                "Custo = Quantidade tarifada × custo unitário do fornecedor — cada "
                "fornecedor cobra por uma etapa diferente do funil (a coluna \"Base de "
                "Cobrança\" da tabela mostra qual). Custos unitários confirmados: "
                "Kolmeya SMS R$ 0,0620 (por enviado), Ótima SMS R$ 0,0500 (por enviado), "
                "Ótima RCS R$ 0,0900 (por disparado), Ótima WhatsApp R$ 0,0685 (por "
                "entregue). WhatsApp Airys e Email (Salesforce, que roda sobre um saldo "
                "pré-pago) ainda não têm custo unitário informado — aparecem na tabela "
                "com o volume, sem inventar um valor.",
            ],
            color="info", className="mb-3",
        ),
        dbc.Row([
            dbc.Col(
                _cartao_kpi("kpi-custo-total", "Custo Total do Período", "bi-cash-stack", "#2ECC71"),
                xs=12, sm=6, md=4, lg=3,
            ),
            dbc.Col(
                _cartao_kpi("kpi-custo-sms", "Custo SMS", "bi-chat-dots-fill", "#3DA9FC"),
                xs=12, sm=6, md=4, lg=3,
            ),
            dbc.Col(
                _cartao_kpi("kpi-custo-rcs", "Custo RCS", "bi-broadcast", "#F5A623"),
                xs=12, sm=6, md=4, lg=3,
            ),
            dbc.Col(
                _cartao_kpi("kpi-custo-whatsapp", "Custo WhatsApp", "bi-whatsapp", "#2ECC71"),
                xs=12, sm=6, md=4, lg=3,
            ),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Custo por Dia e Canal", "grafico-custos-dia"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Custo por Dia, Canal e Fornecedor", className="mb-3"),
                html.Div(id="tabela-custos-container"),
            ]),
            className="cartao-grafico shadow-sm",
        ),
    ])



def criar_layout() -> html.Div:
    return dbc.Container(
        [
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("CASAS", className="logo-casas-bahia logo-casas-bahia-azul"),
                        html.Span("BAHIA", className="logo-casas-bahia logo-casas-bahia-vermelho"),
                    ], className="logo-casas-bahia-container"),
                    html.Div([
                        html.H2("Dash de Resultados — Casas Bahia", className="titulo-principal"),
                        html.P("Disparo → Envio → Entrega", className="subtitulo"),
                    ], className="ms-3"),
                ], className="d-flex align-items-center"),
                html.Div(id="legenda-filtros", className="legenda-registros"),
            ], className="cabecalho-dashboard d-flex justify-content-between align-items-center flex-wrap"),

            _painel_filtros(),
            _linha_kpis(),

            html.Div([
                html.Button("Funil Geral", id="btn-tab-sms", n_clicks=0,
                            className="aba-botao aba-ativa"),
                html.Button("Funil por Prioridade", id="btn-tab-grupo", n_clicks=0,
                            className="aba-botao"),
                html.Button("Funil por Grupo Estratégico", id="btn-tab-grupo-estrategico", n_clicks=0,
                            className="aba-botao"),
                html.Button("Conversão Pós-Contato (CRM)", id="btn-tab-crm", n_clicks=0,
                            className="aba-botao"),
                html.Button("Custos", id="btn-tab-custos", n_clicks=0,
                            className="aba-botao"),
                html.Button("Calendário de Estratégia", id="btn-tab-calendario", n_clicks=0,
                            className="aba-botao"),
            ], className="barra-abas"),

            html.Div(_aba_funil_sms(), id="painel-tab-sms"),
            html.Div(_aba_grupo_ab(), id="painel-tab-grupo", style={"display": "none"}),
            html.Div(_aba_grupo_estrategico(), id="painel-tab-grupo-estrategico", style={"display": "none"}),
            html.Div(_aba_conversao_crm(), id="painel-tab-crm", style={"display": "none"}),
            html.Div(_aba_custos(), id="painel-tab-custos", style={"display": "none"}),
            html.Div(_aba_calendario(), id="painel-tab-calendario", style={"display": "none"}),
            dcc.Store(id="canal-crm-ativo", data="sms"),
        ],
        fluid=True,
        className="container-dashboard",
    )
