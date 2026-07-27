"""Entry point do Dashboard Executivo de Funil SMS — Casas Bahia.

Uso:
    python app.py
"""
from __future__ import annotations

import threading
import webbrowser

import dash
import dash_bootstrap_components as dbc

from callbacks import registrar_callbacks
from layout import criar_layout

FONT_AWESOME_ICONS = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css"
HOST = "127.0.0.1"
PORT = 8051

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, FONT_AWESOME_ICONS],
    title="Casas Bahia · Funil SMS",
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = criar_layout()
registrar_callbacks(app)


def _abrir_navegador():
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    threading.Timer(1.2, _abrir_navegador).start()
    app.run(host=HOST, port=PORT, debug=False)
