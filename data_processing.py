"""Carga, limpeza e padronização dos dados de SMS da operação Casas Bahia.

Fontes, todas em data/raw/ (nas mesmas pastas usadas pela operação no dia a dia):
  - `ARQUIVOS PARA DISPAROS/{utm}.csv` -> base enviada à plataforma (telefone;FRASE) =
    "Disparado". O nome do arquivo (sem extensão) é a própria UTM da campanha.
  - `ARQUIVOS DE RETORNO/*.csv` -> retorno da Kolmeya/Otima/etc (job;phone;status;
    mensagem;criacao) = status de Enviado/Entregue/Falhou. Vêm nomeados por número de
    job, não por UTM, então cada arquivo é ligado à campanha de disparo com maior
    sobreposição de telefones (função `vincular_retornos_a_campanhas`).
  - `ARQUIVOS LOG/*.csv` -> log(s) de CRM (home/auth/oferta/acordo); todos os arquivos
    da pasta são concatenados. Usado só na aba de conversão pós-SMS, não participa do
    funil de envio/entrega.
  - `base_segmentacao_grupo_ab.csv` -> snapshot da base de clientes p/ cruzamento do grupo_ab.

Cada telefone do arquivo de retorno sempre existe na base de disparo correspondente
(validado empiricamente, sem duplicatas), então o funil é modelado como:
  Disparado (base) -> Enviado (qualquer status retornado pela operadora) -> Entregue / Falhou
  (subconjuntos de Enviado; "enviado" cru vira "Pendente", ainda sem confirmação).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils import normalizar_telefone, parse_data_pt_br, taxa

RAW_DIR = Path(__file__).parent / "data" / "raw"
DIR_DISPARO = RAW_DIR / "ARQUIVOS PARA DISPAROS"
DIR_RETORNO = RAW_DIR / "ARQUIVOS DE RETORNO"
DIR_LOG_CRM = RAW_DIR / "ARQUIVOS LOG"

LIMIAR_VINCULO_RETORNO = 0.8


def descobrir_campanhas() -> dict[str, Path]:
    """Descobre automaticamente as campanhas em escopo: toda arquivo em
    `ARQUIVOS PARA DISPAROS/` vira uma campanha, usando o nome do arquivo (sem
    extensão) como UTM. Basta soltar o arquivo novo na pasta e reiniciar o app —
    não precisa editar código nem renomear nada."""
    return {caminho.stem: caminho for caminho in sorted(DIR_DISPARO.glob("*.csv"))}


def _telefones_do_arquivo(caminho: Path, coluna: str) -> set[str]:
    df = ler_csv_auto(caminho)
    if coluna not in df.columns:
        return set()
    telefones = {normalizar_telefone(v) for v in df[coluna]}
    telefones.discard("")
    return telefones


def vincular_retornos_a_campanhas(
    campanhas: dict[str, Path], limiar: float = LIMIAR_VINCULO_RETORNO
) -> dict[str, Path]:
    """Liga cada arquivo de `ARQUIVOS DE RETORNO/` (nomeado por job, não por UTM) à
    campanha de disparo com maior fração de telefones em comum. Uma campanha sem
    retorno ainda vinculado (ex.: disparo de hoje, resultado ainda não voltou) fica
    sem entrada no dicionário — os eventos dela entram como "Não Processado"."""
    telefones_disparo = {utm: _telefones_do_arquivo(caminho, "telefone") for utm, caminho in campanhas.items()}

    vinculo: dict[str, Path] = {}
    for retorno_path in sorted(DIR_RETORNO.glob("*.csv")):
        telefones_retorno = _telefones_do_arquivo(retorno_path, "phone")
        if not telefones_retorno:
            continue

        melhor_utm, melhor_taxa = None, 0.0
        for utm, tel_disparo in telefones_disparo.items():
            if not tel_disparo:
                continue
            sobreposicao = len(telefones_retorno & tel_disparo) / len(telefones_retorno)
            if sobreposicao > melhor_taxa:
                melhor_utm, melhor_taxa = utm, sobreposicao

        if melhor_utm is not None and melhor_taxa >= limiar:
            vinculo[melhor_utm] = retorno_path

    return vinculo


CAMPANHAS_ESCOPO = list(descobrir_campanhas().keys())

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
ETAPAS_CRM_NUMERO = {
    "home": "1º Home",
    "auth": "2º Autenticação",
    "oferta": "3º Oferta Apresentada",
    "acordo": "4º Acordo Gerado",
}

ARQUIVO_GRUPO_AB = RAW_DIR / "base_segmentacao_grupo_ab.csv"
NAO_CLASSIFICADO = "Não Classificado"
GRUPO_AB_ORDEM = ["P1_MAXIMA", "P2_ALTA", "P3_MEDIA", "P4_BAIXA", NAO_CLASSIFICADO]

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


def _carregar_campanha(utm: str, disparo_path: Path, retorno_path: Path | None) -> pd.DataFrame:
    disparo = ler_csv_auto(disparo_path)
    disparo["telefone_norm"] = disparo["telefone"].apply(normalizar_telefone)
    disparo = disparo[disparo["telefone_norm"] != ""].drop_duplicates("telefone_norm")

    if retorno_path is not None:
        retorno = ler_csv_auto(retorno_path)
        retorno["telefone_norm"] = retorno["phone"].apply(normalizar_telefone)
        retorno["status_raw"] = retorno["status"].str.strip().str.lower()
        retorno["timestamp"] = pd.to_datetime(retorno["criacao"], errors="coerce")
        retorno = retorno[retorno["telefone_norm"] != ""].drop_duplicates("telefone_norm")
        eventos = disparo[["telefone_norm"]].merge(
            retorno[["telefone_norm", "status_raw", "timestamp", "mensagem"]],
            on="telefone_norm", how="left",
        )
    else:
        eventos = disparo[["telefone_norm"]].copy()
        eventos["status_raw"] = None
        eventos["timestamp"] = pd.NaT
        eventos["mensagem"] = None

    eventos["utm_campaign"] = utm
    eventos["status_raw"] = eventos["status_raw"].fillna("nao_processado")
    return eventos


def carregar_mapa_grupo_ab(forcar_reload: bool = False) -> dict:
    """Monta o mapa telefone -> grupo_ab a partir da base de segmentação (equivalente ao
    PROCX manual: explode as colunas FONE_1..FONE_4 e associa cada telefone ao grupo_ab
    da linha do cliente)."""
    if not forcar_reload and "grupo_ab_mapa" in _cache:
        return _cache["grupo_ab_mapa"]

    base = ler_csv_auto(ARQUIVO_GRUPO_AB)
    colunas_fone = [c for c in base.columns if c.startswith("fone_")]

    partes = [base[[coluna, "grupo_ab"]].rename(columns={coluna: "fone"}) for coluna in colunas_fone]
    longo = pd.concat(partes, ignore_index=True)
    longo["fone_norm"] = longo["fone"].apply(normalizar_telefone)
    longo = longo[longo["fone_norm"] != ""].drop_duplicates("fone_norm", keep="first")

    mapa = dict(zip(longo["fone_norm"], longo["grupo_ab"]))
    _cache["grupo_ab_mapa"] = mapa
    return mapa


def carregar_dados_sms(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega e unifica os eventos de todas as campanhas descobertas em ARQUIVOS PARA
    DISPAROS/, ligando cada uma ao seu arquivo de retorno por sobreposição de telefones
    (processamento único, cacheado)."""
    if not forcar_reload and "sms" in _cache:
        return _cache["sms"]

    campanhas = descobrir_campanhas()
    vinculos = vincular_retornos_a_campanhas(campanhas)
    df = pd.concat(
        [_carregar_campanha(utm, caminho, vinculos.get(utm)) for utm, caminho in campanhas.items()],
        ignore_index=True,
    )
    df["status_funil"] = df["status_raw"].map(_STATUS_MAPA).fillna("Outro")
    df["disparado"] = 1
    df["enviado"] = (df["status_raw"] != "nao_processado").astype(int)
    df["entregue"] = (df["status_raw"] == "entregue").astype(int)
    df["falhou"] = (df["status_raw"] == "nao entregue").astype(int)
    df["pendente"] = (df["status_raw"] == "enviado").astype(int)
    df["data"] = df["timestamp"].dt.date
    df["hora"] = df["timestamp"].dt.hour

    mapa_grupo_ab = carregar_mapa_grupo_ab(forcar_reload)
    df["grupo_ab"] = df["telefone_norm"].map(mapa_grupo_ab).fillna(NAO_CLASSIFICADO)

    _cache["sms"] = df
    return df


def _normalizar_telefone_com_ddi(valor) -> str:
    """Telefones do log de CRM vêm com DDI 55 (13 dígitos); remove o DDI para
    ficar no mesmo formato (DDD+numero, 10-11 dígitos) usado no restante da base."""
    digitos = normalizar_telefone(valor)
    if len(digitos) == 13 and digitos.startswith("55"):
        return digitos[2:]
    return digitos


def carregar_dados_crm(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega o(s) log(s) de CRM (aba de conversão pós-SMS) de ARQUIVOS LOG/ — todo
    arquivo da pasta é lido e concatenado, deduplicado por `id` quando a coluna existe
    (permite ir empilhando um export novo por dia sem duplicar linhas repetidas)."""
    if not forcar_reload and "crm" in _cache:
        return _cache["crm"]

    arquivos = sorted(DIR_LOG_CRM.glob("*.csv"))
    partes = [ler_csv_auto(caminho) for caminho in arquivos]
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if df.empty:
        _cache["crm"] = df
        return df
    if "id" in df.columns:
        df = df.drop_duplicates("id")

    coluna_utm = "utm campaign" if "utm campaign" in df.columns else "utm"
    df = df[df[coluna_utm].isin(CAMPANHAS_ESCOPO)].copy()
    df = df.rename(columns={coluna_utm: "utm_campaign"})
    df["timestamp"] = df["data"].apply(parse_data_pt_br)
    df["acao_norm"] = df["acao"].str.strip().str.lower()
    df = df[df["acao_norm"].isin(ETAPAS_CRM)]

    mapa_grupo_ab = carregar_mapa_grupo_ab(forcar_reload)
    df["telefone_norm"] = df["mobile"].apply(_normalizar_telefone_com_ddi)
    df["grupo_ab"] = df["telefone_norm"].map(mapa_grupo_ab).fillna(NAO_CLASSIFICADO)

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
    grupos_ab: list[str] | None = None,
) -> pd.DataFrame:
    """Aplica os filtros globais do dashboard sobre o dataframe de eventos de SMS."""
    filtrado = df
    if utms:
        filtrado = filtrado[filtrado["utm_campaign"].isin(utms)]
    if status:
        filtrado = filtrado[filtrado["status_funil"].isin(status)]
    if grupos_ab:
        filtrado = filtrado[filtrado["grupo_ab"].isin(grupos_ab)]
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


def _agregar_por(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    agrupado = df.groupby(coluna).agg(
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
    return agrupado


def agregar_por_campanha(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela executiva por UTM, ordenada da maior para a menor volumetria disparada."""
    agrupado = _agregar_por(df, "utm_campaign")
    return agrupado.sort_values("total_disparado", ascending=False).reset_index(drop=True)


def agregar_por_grupo_ab(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela por grupo_ab (segmentação de propensão), ordenada por prioridade
    P1_MAXIMA -> P4_BAIXA -> Não Classificado (equivalente ao PROCX manual)."""
    agrupado = _agregar_por(df, "grupo_ab")
    agrupado["ordem"] = agrupado["grupo_ab"].apply(
        lambda g: GRUPO_AB_ORDEM.index(g) if g in GRUPO_AB_ORDEM else len(GRUPO_AB_ORDEM)
    )
    return agrupado.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def _agregar_crm_por(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    contagem = df.groupby([coluna, "acao_norm"]).size().rename("quantidade").reset_index()
    tabela = contagem.pivot(index=coluna, columns="acao_norm", values="quantidade").fillna(0)
    for etapa in ETAPAS_CRM:
        if etapa not in tabela.columns:
            tabela[etapa] = 0
    return tabela[ETAPAS_CRM].astype(int).reset_index()


def agregar_crm_por_campanha(df: pd.DataFrame) -> pd.DataFrame:
    """Conta ações de CRM (home/auth/oferta/acordo) por campanha, na ordem do funil de conversão."""
    return _agregar_crm_por(df, "utm_campaign")


def agregar_crm_por_grupo_ab(df: pd.DataFrame) -> pd.DataFrame:
    """Conta ações de CRM (home/auth/oferta/acordo) por grupo_ab, ordenado por prioridade."""
    tabela = _agregar_crm_por(df, "grupo_ab")
    tabela["ordem"] = tabela["grupo_ab"].apply(
        lambda g: GRUPO_AB_ORDEM.index(g) if g in GRUPO_AB_ORDEM else len(GRUPO_AB_ORDEM)
    )
    return tabela.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def montar_pivot_crm(df: pd.DataFrame, utms_ordem: list[str]) -> tuple[list[str], list[dict]]:
    """Tabela dinâmica Ação (com subtotal) > Grupo AB, colunas = UTM + Total Geral,
    igual ao pivot manual (Ação nas linhas, UTM nas colunas, grupo_ab como sub-nível)."""
    if df.empty:
        return [], []

    utms_presentes = [u for u in utms_ordem if u in df["utm_campaign"].unique()]

    def ordem_grupo(g):
        return GRUPO_AB_ORDEM.index(g) if g in GRUPO_AB_ORDEM else len(GRUPO_AB_ORDEM)

    linhas = []
    totais_coluna = {u: 0 for u in utms_presentes}
    total_geral = 0

    for etapa in ETAPAS_CRM:
        sub = df[df["acao_norm"] == etapa]
        if sub.empty:
            continue

        pivot = sub.pivot_table(
            index="grupo_ab", columns="utm_campaign", values="acao_norm",
            aggfunc="count", fill_value=0,
        ).reindex(columns=utms_presentes, fill_value=0)

        subtotal = pivot.sum(axis=0)
        subtotal_geral = int(subtotal.sum())

        linha_subtotal = {"rotulo": ETAPAS_CRM_NUMERO[etapa], "nivel": "subtotal"}
        for u in utms_presentes:
            linha_subtotal[u] = int(subtotal[u])
            totais_coluna[u] += int(subtotal[u])
        linha_subtotal["Total Geral"] = subtotal_geral
        total_geral += subtotal_geral
        linhas.append(linha_subtotal)

        for grupo in sorted(pivot.index, key=ordem_grupo):
            linha = {"rotulo": grupo, "nivel": "detalhe"}
            total_linha = 0
            for u in utms_presentes:
                valor = int(pivot.loc[grupo, u])
                linha[u] = valor
                total_linha += valor
            linha["Total Geral"] = total_linha
            linhas.append(linha)

    linha_total_geral = {"rotulo": "Total Geral", "nivel": "total_geral"}
    for u in utms_presentes:
        linha_total_geral[u] = totais_coluna[u]
    linha_total_geral["Total Geral"] = total_geral
    linhas.append(linha_total_geral)

    return utms_presentes, linhas


def extremos_data_hora(df: pd.DataFrame) -> tuple:
    validas = df.dropna(subset=["timestamp"])
    if validas.empty:
        hoje = pd.Timestamp.now().date()
        return hoje, hoje, 0, 23
    return validas["data"].min(), validas["data"].max(), 0, 23
