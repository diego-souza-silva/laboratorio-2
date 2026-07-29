"""Carga, limpeza e padronização dos dados de SMS da operação Casas Bahia.

Fontes — 4 pastas na raiz do projeto, ao lado de app.py (as mesmas pastas usadas pela
operação no dia a dia; basta soltar arquivo novo dentro e reiniciar o app):
  - `ARQUIVOS PARA DISPAROS/{utm}.csv` -> base enviada à plataforma (telefone;FRASE) =
    "Disparado". O nome do arquivo (sem extensão) é a própria UTM da campanha.
  - `ARQUIVOS DE RETORNO/*.csv` -> retorno da Kolmeya/Otima/etc (job;phone;status;
    mensagem;criacao) = status de Enviado/Entregue/Falhou. Vêm nomeados por número de
    job, não por UTM, então cada arquivo é ligado à campanha de disparo com maior
    sobreposição de telefones (função `vincular_retornos_a_campanhas`).
  - `ARQUIVOS LOG/*.csv` -> log(s) de CRM (home/auth/oferta/acordo); todos os arquivos
    da pasta são concatenados. Usado só na aba de conversão pós-SMS, não participa do
    funil de envio/entrega.
  - `ARQUIVO DA BASE INTEIRA/*.csv` -> snapshot da base de clientes p/ cruzamento do grupo_ab.

Cada telefone do arquivo de retorno sempre existe na base de disparo correspondente
(validado empiricamente, sem duplicatas), então o funil é modelado como:
  Disparado (base) -> Enviado (qualquer status retornado pela operadora) -> Entregue / Falhou
  (subconjuntos de Enviado; "enviado" cru vira "Pendente", ainda sem confirmação).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils import normalizar_frase, normalizar_telefone, parse_data_pt_br, taxa

RAIZ_PROJETO = Path(__file__).parent
DIR_DISPARO = RAIZ_PROJETO / "ARQUIVOS PARA DISPAROS"
DIR_RETORNO = RAIZ_PROJETO / "ARQUIVOS DE RETORNO"
DIR_LOG_CRM = RAIZ_PROJETO / "ARQUIVOS LOG"
DIR_BASE_GRUPO_AB = RAIZ_PROJETO / "ARQUIVO DA BASE INTEIRA"
ARQUIVO_DIARIO_ESTRATEGIA = RAIZ_PROJETO / "DIARIO_ESTRATEGIA.md"

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

NAO_CLASSIFICADO = "Não Classificado"
GRUPO_AB_ORDEM = ["P1_MAXIMA", "P2_ALTA", "P3_MEDIA", "P4_BAIXA", NAO_CLASSIFICADO]
GRUPO_ESTRATEGICO_ORDEM = [
    "2_ABANDONO_CARRINHO", "3_CADASTRADO", "4_ENGAJADO", "5_TOPO_FUNIL", NAO_CLASSIFICADO,
]

UTM_MEDIUM_ORDEM = ["whatsapp", "sms", "email"]

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


def _preparar_disparo(disparo: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Identifica se o disparo é por telefone (SMS/WhatsApp) ou por e-mail (ex.:
    Salesforce), normaliza o identificador e remove duplicatas. Retorna o tipo
    ("telefone"/"email") para decidir depois como tentar ligar o retorno."""
    disparo = disparo.copy()
    if "telefone" in disparo.columns:
        disparo["identificador_norm"] = disparo["telefone"].apply(normalizar_telefone)
        tipo = "telefone"
    elif "email" in disparo.columns:
        disparo["identificador_norm"] = disparo["email"].fillna("").str.strip().str.lower()
        tipo = "email"
    else:
        disparo["identificador_norm"] = ""
        tipo = "desconhecido"

    disparo["telefone_norm"] = disparo["identificador_norm"] if tipo == "telefone" else ""
    disparo = disparo[disparo["identificador_norm"] != ""].drop_duplicates("identificador_norm")
    return disparo, tipo


def _carregar_campanha(utm: str, disparo_path: Path, retorno_path: Path | None) -> pd.DataFrame:
    disparo_bruto = ler_csv_auto(disparo_path)
    disparo, tipo_identificador = _preparar_disparo(disparo_bruto)

    # Alguns disparos (Airys/Otima/Salesforce) já vêm com grupo_ab/grupo_estrategico
    # embutidos na própria base — mais confiável do que recalcular pelo cruzamento de
    # telefone, então tem prioridade sobre o mapa da base de segmentação.
    grupo_ab_arquivo = None
    if "grupo_ab" in disparo.columns:
        grupo_ab_arquivo = disparo[["identificador_norm", "grupo_ab"]].rename(
            columns={"grupo_ab": "grupo_ab_arquivo"}
        )
        grupo_ab_arquivo["grupo_ab_arquivo"] = grupo_ab_arquivo["grupo_ab_arquivo"].str.upper()

    grupo_estrategico_arquivo = None
    if "grupo_estrategico" in disparo.columns:
        grupo_estrategico_arquivo = disparo[["identificador_norm", "grupo_estrategico"]].rename(
            columns={"grupo_estrategico": "grupo_estrategico_arquivo"}
        )
        grupo_estrategico_arquivo["grupo_estrategico_arquivo"] = (
            grupo_estrategico_arquivo["grupo_estrategico_arquivo"].str.upper()
        )

    # A frase do SMS (com link único por cliente) vem do próprio arquivo de disparo,
    # disponível pra 100% das linhas — diferente da "mensagem" do retorno, que só
    # existe pra quem já tem status confirmado.
    frase_disparo = None
    if "frase" in disparo.columns:
        frase_disparo = disparo[["identificador_norm", "frase"]].rename(
            columns={"frase": "frase_disparo"}
        )

    if retorno_path is not None and tipo_identificador == "telefone":
        retorno = ler_csv_auto(retorno_path)
        retorno["telefone_norm"] = retorno["phone"].apply(normalizar_telefone)
        retorno["status_raw"] = retorno["status"].str.strip().str.lower()
        retorno["timestamp"] = pd.to_datetime(retorno["criacao"], errors="coerce")
        retorno = retorno[retorno["telefone_norm"] != ""].drop_duplicates("telefone_norm")
        eventos = disparo[["identificador_norm", "telefone_norm"]].merge(
            retorno[["telefone_norm", "status_raw", "timestamp", "mensagem"]],
            on="telefone_norm", how="left",
        )
    else:
        eventos = disparo[["identificador_norm", "telefone_norm"]].copy()
        eventos["status_raw"] = None
        eventos["timestamp"] = pd.NaT
        eventos["mensagem"] = None

    if grupo_ab_arquivo is not None:
        eventos = eventos.merge(grupo_ab_arquivo, on="identificador_norm", how="left")
    else:
        eventos["grupo_ab_arquivo"] = None

    if grupo_estrategico_arquivo is not None:
        eventos = eventos.merge(grupo_estrategico_arquivo, on="identificador_norm", how="left")
    else:
        eventos["grupo_estrategico_arquivo"] = None

    if frase_disparo is not None:
        eventos = eventos.merge(frase_disparo, on="identificador_norm", how="left")
    else:
        eventos["frase_disparo"] = None

    eventos["utm_campaign"] = utm
    eventos["status_raw"] = eventos["status_raw"].fillna("nao_processado")
    return eventos


def _carregar_base_segmentacao(forcar_reload: bool = False) -> pd.DataFrame:
    """Lê e cacheia a base de clientes em `ARQUIVO DA BASE INTEIRA/` (todo `.csv` da
    pasta, deduplicado por CPF mantendo a linha mais recente). Fonte compartilhada
    pelos mapas de grupo_ab e grupo_estrategico, pra não ler o arquivo duas vezes."""
    if not forcar_reload and "base_segmentacao" in _cache:
        return _cache["base_segmentacao"]

    arquivos = sorted(DIR_BASE_GRUPO_AB.glob("*.csv"))
    if not arquivos:
        base = pd.DataFrame()
    else:
        base = pd.concat([ler_csv_auto(a) for a in arquivos], ignore_index=True)
        if "cpf" in base.columns:
            base = base.drop_duplicates("cpf", keep="last")

    _cache["base_segmentacao"] = base
    return base


def _montar_mapa_telefone(base: pd.DataFrame, coluna_valor: str) -> dict:
    if base.empty or coluna_valor not in base.columns:
        return {}
    colunas_fone = [c for c in base.columns if c.startswith("fone_")]
    partes = [base[[coluna, coluna_valor]].rename(columns={coluna: "fone"}) for coluna in colunas_fone]
    longo = pd.concat(partes, ignore_index=True)
    longo["fone_norm"] = longo["fone"].apply(normalizar_telefone)
    longo = longo[longo["fone_norm"] != ""].drop_duplicates("fone_norm", keep="first")
    return dict(zip(longo["fone_norm"], longo[coluna_valor]))


def carregar_mapa_grupo_ab(forcar_reload: bool = False) -> dict:
    """Monta o mapa telefone -> grupo_ab a partir da base de segmentação (equivalente
    ao PROCX manual: explode as colunas FONE_1..FONE_4 e associa cada telefone ao
    grupo_ab da linha do cliente)."""
    if not forcar_reload and "grupo_ab_mapa" in _cache:
        return _cache["grupo_ab_mapa"]
    mapa = _montar_mapa_telefone(_carregar_base_segmentacao(forcar_reload), "grupo_ab")
    _cache["grupo_ab_mapa"] = mapa
    return mapa


def carregar_mapa_grupo_estrategico(forcar_reload: bool = False) -> dict:
    """Monta o mapa telefone -> grupo_estrategico (2_ABANDONO_CARRINHO, 3_CADASTRADO,
    4_ENGAJADO, 5_TOPO_FUNIL) a partir da mesma base de segmentação, pelo mesmo
    cruzamento por telefone usado no grupo_ab."""
    if not forcar_reload and "grupo_estrategico_mapa" in _cache:
        return _cache["grupo_estrategico_mapa"]
    mapa = _montar_mapa_telefone(_carregar_base_segmentacao(forcar_reload), "grupo_estrategico")
    _cache["grupo_estrategico_mapa"] = mapa
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
    grupo_ab_telefone = df["telefone_norm"].map(mapa_grupo_ab)
    df["grupo_ab"] = df["grupo_ab_arquivo"].combine_first(grupo_ab_telefone).fillna(NAO_CLASSIFICADO)
    df = df.drop(columns="grupo_ab_arquivo")

    mapa_grupo_estrategico = carregar_mapa_grupo_estrategico(forcar_reload)
    grupo_estrategico_telefone = df["telefone_norm"].map(mapa_grupo_estrategico)
    df["grupo_estrategico"] = (
        df["grupo_estrategico_arquivo"].combine_first(grupo_estrategico_telefone).fillna(NAO_CLASSIFICADO)
    )
    df = df.drop(columns="grupo_estrategico_arquivo")

    df["frase"] = df["frase_disparo"].combine_first(df["mensagem"])
    df["frase_norm"] = df["frase"].apply(normalizar_frase)
    df = df.drop(columns="frase_disparo")

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
    """Carrega o(s) log(s) de CRM (aba de conversão pós-contato) de ARQUIVOS LOG/ — todo
    arquivo da pasta é lido e concatenado, e filtrado às campanhas cadastradas em
    ARQUIVOS PARA DISPAROS/ (CAMPANHAS_ESCOPO) — o log em si cobre dezenas de campanhas
    de teste/outras operações que não interessam aqui. Deduplica por uma chave composta
    (doc + utm campaign + acao + data), já que exports diferentes podem ter esquema de
    colunas diferente (misturar deduplicação por `id` com linhas sem essa coluna faz o
    pandas tratar todo NaN como duplicata entre si, descartando quase tudo)."""
    if not forcar_reload and "crm" in _cache:
        return _cache["crm"]

    arquivos = sorted(DIR_LOG_CRM.glob("*.csv"))
    partes = [ler_csv_auto(caminho) for caminho in arquivos]
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if df.empty:
        _cache["crm"] = df
        return df

    # Chave composta (não usa `id`: exports mais antigos e mais novos têm esquemas
    # diferentes, e misturar `id` com linhas sem essa coluna faz o pandas tratar todo
    # NaN como duplicata entre si, descartando quase tudo do arquivo sem `id`).
    chave = [c for c in ["doc", "utm campaign", "acao", "data"] if c in df.columns]
    if chave:
        df = df.drop_duplicates(chave)

    coluna_utm = "utm campaign" if "utm campaign" in df.columns else "utm"
    df = df[df[coluna_utm].isin(CAMPANHAS_ESCOPO)].copy()
    df = df.rename(columns={coluna_utm: "utm_campaign"})
    df["timestamp"] = df["data"].apply(parse_data_pt_br)
    df["acao_norm"] = df["acao"].str.strip().str.lower()
    df = df[df["acao_norm"].isin(ETAPAS_CRM)]
    df["utm_medium"] = df["utm medium"].fillna("").str.strip().str.lower() if "utm medium" in df.columns else ""

    mapa_grupo_ab = carregar_mapa_grupo_ab(forcar_reload)
    df["telefone_norm"] = df["mobile"].apply(_normalizar_telefone_com_ddi)
    df["grupo_ab"] = df["telefone_norm"].map(mapa_grupo_ab).fillna(NAO_CLASSIFICADO)

    mapa_grupo_estrategico = carregar_mapa_grupo_estrategico(forcar_reload)
    df["grupo_estrategico"] = df["telefone_norm"].map(mapa_grupo_estrategico).fillna(NAO_CLASSIFICADO)

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
    grupos_estrategicos: list[str] | None = None,
) -> pd.DataFrame:
    """Aplica os filtros globais do dashboard sobre o dataframe de eventos de SMS."""
    filtrado = df
    if utms:
        filtrado = filtrado[filtrado["utm_campaign"].isin(utms)]
    if status:
        filtrado = filtrado[filtrado["status_funil"].isin(status)]
    if grupos_ab:
        filtrado = filtrado[filtrado["grupo_ab"].isin(grupos_ab)]
    if grupos_estrategicos:
        filtrado = filtrado[filtrado["grupo_estrategico"].isin(grupos_estrategicos)]
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


def agregar_por_grupo_estrategico(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela por grupo_estrategico (2_ABANDONO_CARRINHO, 3_CADASTRADO, 4_ENGAJADO,
    5_TOPO_FUNIL), ordenada pela numeração do próprio grupo."""
    agrupado = _agregar_por(df, "grupo_estrategico")
    agrupado["ordem"] = agrupado["grupo_estrategico"].apply(
        lambda g: GRUPO_ESTRATEGICO_ORDEM.index(g) if g in GRUPO_ESTRATEGICO_ORDEM else len(GRUPO_ESTRATEGICO_ORDEM)
    )
    return agrupado.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def montar_tabela_grupo_estrategico_com_ab(df: pd.DataFrame) -> list[dict]:
    """Monta a tabela Grupo Estratégico (subtotal) > Grupo AB (detalhe), com as mesmas
    métricas do resto do dashboard (Disparado/Enviado/Entregue/Falhado/taxas) — mostra o
    grupo_ab por dentro de cada grupo_estrategico."""
    if df.empty:
        return []

    linhas = []
    ordem_ge = [
        g for g in GRUPO_ESTRATEGICO_ORDEM
        if g in df["grupo_estrategico"].unique()
    ]
    for ge in ordem_ge:
        sub_ge = df[df["grupo_estrategico"] == ge]
        subtotal = agregar_por_grupo_ab(sub_ge)
        if subtotal.empty:
            continue

        totais = subtotal[["total_disparado", "total_enviado", "total_entregue", "total_falhado"]].sum()
        linhas.append({
            "rotulo": ge, "nivel": "subtotal",
            "total_disparado": int(totais["total_disparado"]),
            "total_enviado": int(totais["total_enviado"]),
            "total_entregue": int(totais["total_entregue"]),
            "total_falhado": int(totais["total_falhado"]),
            "taxa_envio": taxa(totais["total_enviado"], totais["total_disparado"]),
            "taxa_entrega": taxa(totais["total_entregue"], totais["total_enviado"]),
            "taxa_falha": taxa(totais["total_falhado"], totais["total_enviado"]),
        })
        for _, linha in subtotal.iterrows():
            linhas.append({
                "rotulo": linha["grupo_ab"], "nivel": "detalhe",
                "total_disparado": int(linha["total_disparado"]),
                "total_enviado": int(linha["total_enviado"]),
                "total_entregue": int(linha["total_entregue"]),
                "total_falhado": int(linha["total_falhado"]),
                "taxa_envio": linha["taxa_envio"],
                "taxa_entrega": linha["taxa_entrega"],
                "taxa_falha": linha["taxa_falha"],
            })

    return linhas


def agregar_por_frase(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela por frase de SMS (modelo de mensagem, sem o link único de cada cliente),
    ordenada da maior para a menor volumetria disparada. Só considera linhas com frase
    conhecida (campanhas de SMS com o texto no arquivo de disparo ou no retorno)."""
    validas = df[df["frase_norm"] != ""]
    if validas.empty:
        return _agregar_por(validas, "frase_norm")

    agrupado = _agregar_por(validas, "frase_norm")
    campanhas_por_frase = (
        validas.groupby("frase_norm")["utm_campaign"]
        .agg(lambda s: sorted(set(s)))
        .rename("campanhas")
        .reset_index()
    )
    agrupado = agrupado.merge(campanhas_por_frase, on="frase_norm", how="left")
    return agrupado.sort_values("total_disparado", ascending=False).reset_index(drop=True)


def agregar_frase_com_crm(df_sms: pd.DataFrame, df_crm: pd.DataFrame) -> pd.DataFrame:
    """Tabela por frase de SMS incluindo o resultado final no CRM (home/auth/oferta/
    acordo): para cada frase, cruza os telefones que a receberam com o log de CRM e
    conta quantos avançaram em cada etapa da negociação — sobretudo quantos viraram
    acordo."""
    base = agregar_por_frase(df_sms)
    for etapa in ETAPAS_CRM:
        base[etapa] = 0
    if base.empty or df_crm.empty:
        return base

    validas = df_sms[df_sms["frase_norm"] != ""]
    telefones_por_frase = validas.groupby("frase_norm")["telefone_norm"].apply(set)

    for i, linha in base.iterrows():
        telefones = telefones_por_frase.get(linha["frase_norm"], set())
        if not telefones:
            continue
        sub_crm = df_crm[df_crm["telefone_norm"].isin(telefones)]
        contagem = sub_crm["acao_norm"].value_counts()
        for etapa in ETAPAS_CRM:
            base.at[i, etapa] = int(contagem.get(etapa, 0))

    return base


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


def agregar_crm_por_grupo_estrategico(df: pd.DataFrame) -> pd.DataFrame:
    """Conta ações de CRM (home/auth/oferta/acordo) por grupo_estrategico, ordenado pela numeração do grupo."""
    tabela = _agregar_crm_por(df, "grupo_estrategico")
    tabela["ordem"] = tabela["grupo_estrategico"].apply(
        lambda g: GRUPO_ESTRATEGICO_ORDEM.index(g) if g in GRUPO_ESTRATEGICO_ORDEM else len(GRUPO_ESTRATEGICO_ORDEM)
    )
    return tabela.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def agregar_crm_por_medium(df: pd.DataFrame) -> pd.DataFrame:
    """Conta ações de CRM (home/auth/oferta/acordo) por canal de origem (utm_medium:
    whatsapp/sms/email), na ordem de volume esperado."""
    tabela = _agregar_crm_por(df, "utm_medium")
    tabela["ordem"] = tabela["utm_medium"].apply(
        lambda m: UTM_MEDIUM_ORDEM.index(m) if m in UTM_MEDIUM_ORDEM else len(UTM_MEDIUM_ORDEM)
    )
    return tabela.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def montar_pivot_crm(
    df: pd.DataFrame, utms_ordem: list[str], coluna_grupo: str = "grupo_ab"
) -> tuple[list[str], list[dict]]:
    """Tabela dinâmica Ação (com subtotal) > Grupo AB/Grupo Estratégico, colunas = UTM +
    Total Geral, igual ao pivot manual (Ação nas linhas, UTM nas colunas, grupo como
    sub-nível). `coluna_grupo` escolhe a dimensão do sub-nível ("grupo_ab" ou
    "grupo_estrategico")."""
    if df.empty:
        return [], []

    utms_presentes = [u for u in utms_ordem if u in df["utm_campaign"].unique()]
    ordem_map = GRUPO_AB_ORDEM if coluna_grupo == "grupo_ab" else GRUPO_ESTRATEGICO_ORDEM

    def ordem_grupo(g):
        return ordem_map.index(g) if g in ordem_map else len(ordem_map)

    linhas = []
    totais_coluna = {u: 0 for u in utms_presentes}
    total_geral = 0

    for etapa in ETAPAS_CRM:
        sub = df[df["acao_norm"] == etapa]
        if sub.empty:
            continue

        pivot = sub.pivot_table(
            index=coluna_grupo, columns="utm_campaign", values="acao_norm",
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


def ler_diario_estrategia() -> str:
    """Lê o diário de estratégia (arquivo Markdown editável direto pela aba do
    dashboard). Se o arquivo ainda não existir, retorna um texto inicial vazio."""
    if ARQUIVO_DIARIO_ESTRATEGIA.exists():
        return ARQUIVO_DIARIO_ESTRATEGIA.read_text(encoding="utf-8")
    return "# Diário de Estratégia\n\n"


def salvar_diario_estrategia(conteudo: str) -> None:
    """Grava o texto editado na aba do dashboard de volta em DIARIO_ESTRATEGIA.md."""
    ARQUIVO_DIARIO_ESTRATEGIA.write_text(conteudo or "", encoding="utf-8")
