"""Layout Dash/Bootstrap do dashboard executivo (tema escuro, estilo Power BI)."""
from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc

from data_processing import (
    CAMPANHAS_ESCOPO, GRUPO_AB_ORDEM, GRUPO_ESTRATEGICO_ORDEM, STATUS_FUNIL_ORDEM,
    carregar_dados_sms, carregar_dados_whatsapp_mensagem, extremos_data_hora,
    ler_diario_estrategia,
)
from charts import GRUPO_AB_LABEL, GRUPO_ESTRATEGICO_LABEL, nome_curto

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


def _linha_kpis() -> html.Div:
    cartoes_sms = [
        ("kpi-disparado", "Total Disparado", "bi-send-fill", "#8B93B8"),
        ("kpi-enviado", "Total Enviado", "bi-paper-plane-fill", "#3DA9FC"),
        ("kpi-entregue", "Total Entregue", "bi-check-circle-fill", "#2ECC71"),
        ("kpi-falhado", "Total Falhado", "bi-x-circle-fill", "#FF5C5C"),
        ("kpi-taxa-envio", "Taxa de Envio", "bi-graph-up", "#3DA9FC"),
        ("kpi-taxa-entrega", "Taxa de Entrega", "bi-graph-up-arrow", "#2ECC71"),
        ("kpi-taxa-falha", "Taxa de Falha", "bi-graph-down", "#FF5C5C"),
    ]
    cartoes_whatsapp = [
        ("kpi-whatsapp-entregue", "Entregue", "bi-check-circle-fill", "#2ECC71"),
        ("kpi-whatsapp-lido", "Lido", "bi-eye-fill", "#2ECC71"),
        ("kpi-whatsapp-enviado", "Enviado", "bi-paper-plane-fill", "#F5A623"),
        ("kpi-whatsapp-nao-entregue", "Não Entregue", "bi-x-circle-fill", "#FF5C5C"),
        ("kpi-whatsapp-nao-enviado", "Não Enviado", "bi-dash-circle-fill", "#8B93B8"),
    ]
    return html.Div([
        html.Span("SMS (Kolmeya)", className="rotulo-filtro"),
        dbc.Row(
            [dbc.Col(_cartao_kpi(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes_sms],
            className="g-3 mb-3",
        ),
        html.Span("WhatsApp (Otima/Airys)", className="rotulo-filtro"),
        dbc.Row(
            [dbc.Col(_cartao_kpi(*c), xs=12, sm=6, md=4, lg=True) for c in cartoes_whatsapp],
            className="g-3 mb-3",
        ),
    ])


def _painel_filtros() -> dbc.Card:
    df = carregar_dados_sms()
    data_min, data_max, hora_min, hora_max = extremos_data_hora(df, carregar_dados_whatsapp_mensagem())

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
            dbc.Row([
                dbc.Col([
                    html.Label("Grupo AB (segmentação de propensão)", className="rotulo-filtro"),
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


def _aba_funil_sms() -> html.Div:
    return html.Div([
        dbc.Row([
            dbc.Col(_grafico_card("Funil Geral", "grafico-funil"), md=7),
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
        dbc.Row([
            dbc.Col(_grafico_card("Volume por Grupo AB", "grafico-volume-grupo-ab"), md=6),
            dbc.Col(_grafico_card("Taxa de Entrega por Grupo AB", "grafico-taxa-entrega-grupo-ab"), md=6),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Tabela Executiva por Grupo AB", className="mb-3"),
                html.Div(id="tabela-grupo-ab-container"),
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
        dbc.Row([
            dbc.Col(_grafico_card("Volume por Grupo Estratégico", "grafico-volume-grupo-estrategico"), md=6),
            dbc.Col(_grafico_card("Taxa de Entrega por Grupo Estratégico", "grafico-taxa-entrega-grupo-estrategico"), md=6),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Grupo Estratégico × Grupo AB (detalhado)", className="mb-3"),
                html.Div(id="tabela-grupo-estrategico-container"),
            ]),
            className="cartao-grafico shadow-sm",
        ),
    ])


def _aba_conversao_crm() -> html.Div:
    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "Seção auxiliar baseada no log de CRM (negociação), não no log de envio. "
                "Restrita às campanhas cadastradas em ARQUIVOS PARA DISPAROS/. Escolha o "
                "canal abaixo (Pós-SMS/Pós-WhatsApp/Pós-Email) — mostra o que aconteceu "
                "depois do clique: Home → Autenticação → Oferta → Acordo.",
            ],
            color="info", className="mb-3",
        ),
        html.Div([
            html.Button("Pós-SMS", id="btn-canal-sms", n_clicks=0, className="aba-botao aba-ativa"),
            html.Button("Pós-WhatsApp", id="btn-canal-whatsapp", n_clicks=0, className="aba-botao"),
            html.Button("Pós-Email", id="btn-canal-email", n_clicks=0, className="aba-botao"),
        ], className="barra-abas mb-3"),
        dbc.Card(
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        html.Label("Campanha (UTM) — CRM", className="rotulo-filtro"),
                        dcc.Dropdown(
                            id="filtro-utm-crm",
                            options=[{"label": nome_curto(u), "value": u} for u in CAMPANHAS_ESCOPO],
                            value=CAMPANHAS_ESCOPO, multi=True, placeholder="Todas as campanhas",
                            className="dash-dropdown-escuro",
                        ),
                    ], md=12),
                ], className="g-3 align-items-end"),
            ),
            className="cartao-filtros shadow-sm mb-3",
        ),
        dbc.Row([
            dbc.Col(_cartao_kpi("kpi-crm-home", "Home", "bi-house-door-fill", "#8B93B8"), md=3),
            dbc.Col(_cartao_kpi("kpi-crm-auth", "Autenticação", "bi-shield-lock-fill", "#3DA9FC"), md=3),
            dbc.Col(_cartao_kpi("kpi-crm-oferta", "Oferta Apresentada", "bi-tag-fill", "#F5A623"), md=3),
            dbc.Col(_cartao_kpi("kpi-crm-acordo", "Acordo Gerado", "bi-file-earmark-check-fill", "#2ECC71"), md=3),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Funil de Conversão", "grafico-funil-crm"), md=4),
            dbc.Col(_grafico_card("Ações de CRM por Grupo AB", "grafico-crm-grupo-ab"), md=4),
            dbc.Col(_grafico_card("Ações de CRM por Grupo Estratégico", "grafico-crm-grupo-estrategico"), md=4),
        ], className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(_grafico_card("Ações de CRM por Campanha", "grafico-crm-campanha"), md=12),
        ], className="g-3 mb-3"),
        dbc.Card(
            dbc.CardBody([
                html.H6("Ação × Campanha × Grupo AB (detalhado)", className="mb-3"),
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
        dbc.Alert(
            [
                html.I(className="bi bi-chat-left-text-fill me-2"),
                "Resultado por frase de SMS: cada envio tem um link único por cliente, então "
                "as mensagens são agrupadas pelo texto-modelo (sem o link). Abaixo tem tanto a "
                "taxa de entrega (log de envio) quanto o resultado final no CRM — Home → "
                "Autenticação → Oferta → Acordo — cruzado por telefone com o canal selecionado "
                "acima. Deixe em \"Pós-SMS\" para ver o resultado de quem recebeu cada frase.",
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
                    className="cartao-grafico shadow-sm",
                ),
            ],
            id="secao-mensagem-whatsapp",
            style={"display": "none"},
        ),
    ])


def _aba_diario() -> html.Div:
    return html.Div([
        dbc.Alert(
            [
                html.I(className="bi bi-journal-text me-2"),
                "Bloco de notas livre para registrar a estratégia e as decisões de cada "
                "dia. Escreva à vontade e clique em \"Salvar\" — o texto fica gravado em "
                "DIARIO_ESTRATEGIA.md, na pasta do projeto, e continua aqui mesmo depois "
                "de reiniciar o dashboard.",
            ],
            color="info", className="mb-3",
        ),
        dbc.Card(
            dbc.CardBody([
                dcc.Textarea(
                    id="editor-diario",
                    value=ler_diario_estrategia(),
                    className="editor-diario",
                    style={"width": "100%", "height": "560px"},
                ),
                html.Div([
                    dbc.Button("Salvar", id="btn-salvar-diario", color="primary", className="mt-3"),
                    html.Span(id="status-salvar-diario", className="legenda-registros ms-3"),
                ], className="d-flex align-items-center"),
            ]),
            className="cartao-grafico shadow-sm",
        ),
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
                html.Button("Funil Geral", id="btn-tab-sms", n_clicks=0,
                            className="aba-botao aba-ativa"),
                html.Button("Funil por Grupo AB", id="btn-tab-grupo", n_clicks=0,
                            className="aba-botao"),
                html.Button("Funil por Grupo Estratégico", id="btn-tab-grupo-estrategico", n_clicks=0,
                            className="aba-botao"),
                html.Button("Conversão Pós-Contato (CRM)", id="btn-tab-crm", n_clicks=0,
                            className="aba-botao"),
                html.Button("Diário / Estratégia", id="btn-tab-diario", n_clicks=0,
                            className="aba-botao"),
            ], className="barra-abas"),

            html.Div(_aba_funil_sms(), id="painel-tab-sms"),
            html.Div(_aba_grupo_ab(), id="painel-tab-grupo", style={"display": "none"}),
            html.Div(_aba_grupo_estrategico(), id="painel-tab-grupo-estrategico", style={"display": "none"}),
            html.Div(_aba_conversao_crm(), id="painel-tab-crm", style={"display": "none"}),
            html.Div(_aba_diario(), id="painel-tab-diario", style={"display": "none"}),
            dcc.Store(id="canal-crm-ativo", data="sms"),
        ],
        fluid=True,
        className="container-dashboard",
    )
