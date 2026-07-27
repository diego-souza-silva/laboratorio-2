"""Carga, limpeza e padronização dos dados de SMS da operação Casas Bahia.

Fontes (todas em data/raw/):
  - `{utm}_disparo.csv`  -> base enviada à plataforma Kolmeya (telefone;FRASE) = "Disparado".
  - `{utm}_log.csv`      -> log de resultado da Kolmeya (job;phone;status;mensagem;criacao).
  - `LOG_CB_LABORATORIO_crm.csv` -> log de CRM (home/auth/oferta/acordo), usado só na aba de
    conversão pós-SMS; não participa do funil de envio/entrega.

Cada telefone do log de resultado sempre existe na base de disparo (validado empiricamente,
sem duplicatas), então o funil é modelado como:
  Disparado (base) -> Enviado (qualquer status retornado pela operadora) -> Entregue / Falhou
  (subconjuntos de Enviado; "enviado" cru vira "Pendente", ainda sem confirmação).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils import normalizar_telefone, parse_data_pt_br, taxa

RAW_DIR = Path(__file__).parent / "data" / "raw"

CAMPANHAS_ESCOPO = [
    "20260725-abandonocarrinhodia25-kolmeya",
    "20260725-engajadodia25-kolmeya",
    "20260725-topofunildia25-kolmeya",
    "20260725-cadastradodia25-kolmeya",
]

STATUS_FUNIL_ORDEM = ["Entregue", "Pendente", "Falhou", "Nao Processado"]

_STATUS_MAPA = {
    "entregue": "Entregue",
    "nao entregue": "Falhou",
    "enviado": "Pendente",
    "nao_processado": "Nao Processado",
}

ETAPAS_CRM = ["home", "auth", "oferta", "acordo"]
ETAPAS_CRM_LABEL = {
    "home": "Home",
    "auth": "Autenticação",
    "oferta": "Oferta Apresentada",
    "acordo": "Acordo Gerado",
}

_cache: dict[str, pd.DataFrame] = {}


def _detectar_encoding(caminho: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            with open(caminho, encoding=enc) as f:
                f.read()
            return enc
        except UnicodeDecodeError:
            continue
    return "latin1"


def _detectar_separador(caminho: Path, encoding: str) -> str:
    with open(caminho, encoding=encoding, errors="replace") as f:
        primeira_linha = f.readline()
    return ";" if primeira_linha.count(";") >= primeira_linha.count(",") else ","


def ler_csv_auto(caminho: Path) -> pd.DataFrame:
    """Lê um CSV detectando encoding e separador automaticamente; colunas viram lowercase/strip."""
    encoding = _detectar_encoding(caminho)
    separador = _detectar_separador(caminho, encoding)
    df = pd.read_csv(
        caminho, sep=separador, encoding=encoding, dtype=str, engine="python",
        keep_default_na=False, na_values=[""],
    )
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def _carregar_campanha(utm: str) -> pd.DataFrame:
    disparo = ler_csv_auto(RAW_DIR / f"{utm}_disparo.csv")
    disparo["telefone_norm"] = disparo["telefone"].apply(normalizar_telefone)
    disparo = disparo[disparo["telefone_norm"] != ""].drop_duplicates("telefone_norm")

    log = ler_csv_auto(RAW_DIR / f"{utm}_log.csv")
    log["telefone_norm"] = log["phone"].apply(normalizar_telefone)
    log["status_raw"] = log["status"].str.strip().str.lower()
    log["timestamp"] = pd.to_datetime(log["criacao"], errors="coerce")
    log = log[log["telefone_norm"] != ""].drop_duplicates("telefone_norm")

    eventos = disparo[["telefone_norm"]].merge(
        log[["telefone_norm", "status_raw", "timestamp", "mensagem"]],
        on="telefone_norm", how="left",
    )
    eventos["utm_campaign"] = utm
    eventos["status_raw"] = eventos["status_raw"].fillna("nao_processado")
    return eventos


def carregar_dados_sms(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega e unifica os eventos das 4 campanhas Kolmeya (processamento único, cacheado)."""
    if not forcar_reload and "sms" in _cache:
        return _cache["sms"]

    df = pd.concat([_carregar_campanha(utm) for utm in CAMPANHAS_ESCOPO], ignore_index=True)
    df["status_funil"] = df["status_raw"].map(_STATUS_MAPA).fillna("Outro")
    df["disparado"] = 1
    df["enviado"] = (df["status_raw"] != "nao_processado").astype(int)
    df["entregue"] = (df["status_raw"] == "entregue").astype(int)
    df["falhou"] = (df["status_raw"] == "nao entregue").astype(int)
    df["pendente"] = (df["status_raw"] == "enviado").astype(int)
    df["data"] = df["timestamp"].dt.date
    df["hora"] = df["timestamp"].dt.hour

    _cache["sms"] = df
    return df


def carregar_dados_crm(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega o log de CRM (aba de conversão pós-SMS), filtrado às campanhas em escopo."""
    if not forcar_reload and "crm" in _cache:
        return _cache["crm"]

    df = ler_csv_auto(RAW_DIR / "LOG_CB_LABORATORIO_crm.csv")
    coluna_utm = "utm campaign" if "utm campaign" in df.columns else "utm"
    df = df[df[coluna_utm].isin(CAMPANHAS_ESCOPO)].copy()
    df = df.rename(columns={coluna_utm: "utm_campaign"})
    df["timestamp"] = df["data"].apply(parse_data_pt_br)
    df["acao_norm"] = df["acao"].str.strip().str.lower()
    df = df[df["acao_norm"].isin(ETAPAS_CRM)]

    _cache["crm"] = df
    return df


def filtrar_dados(
    df: pd.DataFrame,
    utms: list[str] | None = None,
    data_ini=None,
    data_fim=None,
    hora_ini: int | None = None,
    hora_fim: int | None = None,
    status: list[str] | None = None,
) -> pd.DataFrame:
    """Aplica os filtros globais do dashboard sobre o dataframe de eventos de SMS."""
    filtrado = df
    if utms:
        filtrado = filtrado[filtrado["utm_campaign"].isin(utms)]
    if status:
        filtrado = filtrado[filtrado["status_funil"].isin(status)]
    if data_ini is not None and data_fim is not None:
        no_periodo = filtrado["data"].isna() | (
            (filtrado["data"] >= data_ini) & (filtrado["data"] <= data_fim)
        )
        filtrado = filtrado[no_periodo]
    if hora_ini is not None and hora_fim is not None:
        na_janela = filtrado["hora"].isna() | (
            (filtrado["hora"] >= hora_ini) & (filtrado["hora"] <= hora_fim)
        )
        filtrado = filtrado[na_janela]
    return filtrado


def calcular_kpis(df: pd.DataFrame) -> dict:
    disparado = int(df["disparado"].sum())
    enviado = int(df["enviado"].sum())
    entregue = int(df["entregue"].sum())
    falhou = int(df["falhou"].sum())
    return {
        "disparado": disparado,
        "enviado": enviado,
        "entregue": entregue,
        "falhou": falhou,
        "taxa_envio": taxa(enviado, disparado),
        "taxa_entrega": taxa(entregue, enviado),
        "taxa_falha": taxa(falhou, enviado),
    }


def calcular_funil(df: pd.DataFrame) -> list[dict]:
    """Monta as 4 etapas do funil (Disparado -> Enviado -> Entregue -> Falhou) com
    quantidade, % sobre a base, conversão e perda em relação à etapa anterior."""
    kpis = calcular_kpis(df)
    etapas = [
        ("Disparado", kpis["disparado"]),
        ("Enviado", kpis["enviado"]),
        ("Entregue", kpis["entregue"]),
        ("Falhou", kpis["falhou"]),
    ]
    base = etapas[0][1] or 1
    resultado = []
    anterior = None
    for nome, valor in etapas:
        percentual_base = taxa(valor, base)
        if anterior is None:
            conversao = 100.0
            perda = 0.0
        else:
            conversao = taxa(valor, anterior)
            perda = 100.0 - conversao
        resultado.append({
            "etapa": nome,
            "quantidade": valor,
            "percentual_base": percentual_base,
            "conversao": conversao,
            "perda": perda,
        })
        anterior = valor
    return resultado


def agregar_por_campanha(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela executiva por UTM, ordenada da maior para a menor volumetria disparada."""
    agrupado = df.groupby("utm_campaign").agg(
        total_disparado=("disparado", "sum"),
        total_enviado=("enviado", "sum"),
        total_entregue=("entregue", "sum"),
        total_falhado=("falhou", "sum"),
    ).reset_index()

    agrupado["taxa_envio"] = agrupado.apply(
        lambda r: taxa(r["total_enviado"], r["total_disparado"]), axis=1
    )
    agrupado["taxa_entrega"] = agrupado.apply(
        lambda r: taxa(r["total_entregue"], r["total_enviado"]), axis=1
    )
    agrupado["taxa_falha"] = agrupado.apply(
        lambda r: taxa(r["total_falhado"], r["total_enviado"]), axis=1
    )
    return agrupado.sort_values("total_disparado", ascending=False).reset_index(drop=True)


def agregar_crm_por_campanha(df: pd.DataFrame) -> pd.DataFrame:
    """Conta ações de CRM (home/auth/oferta/acordo) por campanha, na ordem do funil de conversão."""
    contagem = (
        df.groupby(["utm_campaign", "acao_norm"]).size().rename("quantidade").reset_index()
    )
    tabela = contagem.pivot(index="utm_campaign", columns="acao_norm", values="quantidade").fillna(0)
    for etapa in ETAPAS_CRM:
        if etapa not in tabela.columns:
            tabela[etapa] = 0
    return tabela[ETAPAS_CRM].astype(int).reset_index()


def extremos_data_hora(df: pd.DataFrame) -> tuple:
    validas = df.dropna(subset=["timestamp"])
    if validas.empty:
        hoje = pd.Timestamp.now().date()
        return hoje, hoje, 0, 23
    return validas["data"].min(), validas["data"].max(), 0, 23
