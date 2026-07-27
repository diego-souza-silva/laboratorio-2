"""Layout Dash/Bootstrap do dashboard executivo (tema escuro, estilo Power BI)."""
from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc

from data_processing import (
    CAMPANHAS_ESCOPO, STATUS_FUNIL_ORDEM, carregar_dados_sms, extremos_data_hora,
)
from charts import nome_curto

STATUS_LABEL = {
    "Entregue": "Entregue",
    "Pendente": "Pendente (em trânsito)",
    "Falhou": "Falhou",
    "Nao Processado": "Não Processado",
}


def _cartao_kpi(id_valor: str, titulo: str, icone: str, cor: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi {icone}", style={"color": cor, "fontSize": "1.6rem"}),
                html.Span(titulo, className="kpi-titulo"),
            ], className="kpi-cabecalho"),
            html.H3(id=id_valor, className="kpi-valor", style={"color": cor}),
        ]),
        className="cartao-kpi shadow-sm",
    )


def _linha_kpis() -> dbc.Row:
    cartoes = [
        ("kpi-disparado", "Total Disparado", "bi-send-fill", "#8B93B8"),
        ("kpi-enviado", "Total Enviado", "bi-paper-plane-fill", "#3DA9FC"),
        ("kpi-entregue", "Total Entregue", "bi-check-circle-fill", "#2ECC71"),
        ("kpi-falhado", "Total Falhado", "bi-x-circle-fill", "#FF5C5C"),
        ("kpi-taxa-envio", "Taxa de Envio", "bi-graph-up", "#3DA9FC"),
        ("kpi-taxa-entrega", "Taxa de Entrega", "bi-graph-up-arrow", "#2ECC71"),
        ("kpi-taxa-falha", "Taxa de Falha", "bi-graph-down", "#FF5C5C"),
    ]
    return dbc.Row(
        [dbc.Col(_cartao_kpi(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes],
        className="g-3 mb-3",
    )


def _painel_filtros() -> dbc.Card:
    df = carregar_dados_sms()
    data_min, data_max, hora_min, hora_max = extremos_data_hora(df)

    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Campanha (UTM)", className="rotulo-filtro"),
                    dcc.Dropdown(
                        id="filtro-utm",
                        options=[{"label": nome_curto(u), "value": u} for u in CAMPANHAS_ESCOPO],
                        value=CAMPANHAS_ESCOPO, multi=True, placeholder="Todas as campanhas",
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


def _aba_funil_sms() -> html.Div:
    return html.Div([
        dbc.Row([
            dbc.Col(_grafico_card("Funil de SMS", "grafico-funil"), md=7),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6("Detalhe por Etapa", className="mb-3"),
                        html.Div(id="tabela-funil-detalhe"),
                    ]),
                    className="cartao-grafico shadow-sm h-100",
                ),
                md=5,
            ),
        ], className="g-3 mb-3"),

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
            className="cartao-grafico shadow-sm mb-3",
        ),
    ])


def _aba_conversao_crm() -> html.Div:
    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "Seção auxiliar baseada no log de CRM (negociação), não no log de envio de SMS. "
                "Mostra o que aconteceu depois do clique: Home → Autenticação → Oferta → Acordo.",
            ],
            color="info", className="mb-3",
        ),
        dbc.Row([
            dbc.Col(_cartao_kpi("kpi-crm-home", "Home", "bi-house-door-fill", "#8B93B8"), md=3),
            dbc.Col(_cartao_kpi("kpi-crm-auth", "Autenticação", "bi-shield-lock-fill", "#3DA9FC"), md=3),
            dbc.Col(_cartao_kpi("kpi-crm-oferta", "Oferta Apresentada", "bi-tag-fill", "#F5A623"), md=3),
            dbc.Col(_cartao_kpi("kpi-crm-acordo", "Acordo Gerado", "bi-file-earmark-check-fill", "#2ECC71"), md=3),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Funil de Conversão Pós-SMS", "grafico-funil-crm"), md=6),
            dbc.Col(_grafico_card("Ações de CRM por Campanha", "grafico-crm-campanha"), md=6),
        ], className="g-3"),
    ])


def criar_layout() -> html.Div:
    return dbc.Container(
        [
            html.Div([
                html.Div([
                    html.I(className="bi bi-graph-up-arrow", style={"fontSize": "2rem", "color": "#3DA9FC"}),
                    html.Div([
                        html.H2("Dashboard Executivo de Funil SMS", className="titulo-principal"),
                        html.P("Casas Bahia · Disparo → Envio → Entrega (base Kolmeya)", className="subtitulo"),
                    ], className="ms-3"),
                ], className="d-flex align-items-center"),
                html.Div(id="legenda-filtros", className="legenda-registros"),
            ], className="cabecalho-dashboard d-flex justify-content-between align-items-center flex-wrap"),

            _painel_filtros(),
            _linha_kpis(),

            html.Div([
                html.Button("Funil de SMS", id="btn-tab-sms", n_clicks=0,
                            className="aba-botao aba-ativa"),
                html.Button("Conversão Pós-SMS (CRM)", id="btn-tab-crm", n_clicks=0,
                            className="aba-botao"),
            ], className="barra-abas"),

            html.Div(_aba_funil_sms(), id="painel-tab-sms"),
            html.Div(_aba_conversao_crm(), id="painel-tab-crm", style={"display": "none"}),
        ],
        fluid=True,
        className="container-dashboard",
    )
