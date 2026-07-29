"""Funções utilitárias reutilizáveis: parsing de datas, telefones e formatação."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}

_DATA_PT_RE = re.compile(
    r"(?P<mes>[a-zçã]+)\s+(?P<dia>\d{1,2}),\s*(?P<ano>\d{4}),\s*(?P<hora>\d{1,2}):(?P<min>\d{2})\s*(?P<ampm>AM|PM)",
    re.IGNORECASE,
)

_LINK_RE = re.compile(r"https?://\S+")


def normalizar_frase(mensagem) -> str:
    """Reduz a frase de SMS ao seu texto-modelo: cada envio tem um link curto único por
    cliente (ex.: .../8knbP2), então sem isso cada linha viraria um grupo próprio.
    Substitui o link por um marcador fixo pra agrupar por modelo de mensagem."""
    if not isinstance(mensagem, str) or not mensagem.strip():
        return ""
    return _LINK_RE.sub("{link}", mensagem).strip()


def strip_accents(texto: str) -> str:
    if not isinstance(texto, str):
        return texto
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


def parse_data_pt_br(valor: str) -> pd.Timestamp:
    """Converte datas no formato 'julho 24, 2026, 7:32 PM' (sem depender de locale do SO)."""
    if not isinstance(valor, str) or not valor.strip():
        return pd.NaT
    m = _DATA_PT_RE.match(valor.strip())
    if not m:
        return pd.to_datetime(valor, errors="coerce")
    mes_nome = strip_accents(m.group("mes").lower())
    mes = MESES_PT.get(mes_nome)
    if mes is None:
        return pd.NaT
    hora = int(m.group("hora")) % 12
    if m.group("ampm").upper() == "PM":
        hora += 12
    try:
        return pd.Timestamp(
            year=int(m.group("ano")), month=mes, day=int(m.group("dia")),
            hour=hora, minute=int(m.group("min")),
        )
    except ValueError:
        return pd.NaT


def normalizar_telefone(valor) -> str:
    """Mantém apenas dígitos e remove telefones claramente inválidos."""
    if pd.isna(valor):
        return ""
    digitos = re.sub(r"\D", "", str(valor))
    if len(digitos) < 10 or len(digitos) > 13:
        return ""
    return digitos


def formatar_numero(valor: float) -> str:
    if valor is None or pd.isna(valor):
        return "0"
    return f"{int(valor):,}".replace(",", ".")


def formatar_percentual(valor: float, casas: int = 1) -> str:
    if valor is None or pd.isna(valor):
        return "0,0%"
    texto = f"{valor:.{casas}f}%"
    return texto.replace(".", ",")


def taxa(numerador: float, denominador: float) -> float:
    if not denominador:
        return 0.0
    return (numerador / denominador) * 100
