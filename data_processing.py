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

import base64
import json
import re
from pathlib import Path

import pandas as pd

from utils import normalizar_frase, normalizar_mensagem_whatsapp, normalizar_telefone, parse_data_pt_br, taxa

RAIZ_PROJETO = Path(__file__).parent

LIMIAR_VINCULO_RETORNO = 0.8

_DIR_DISPARO = RAIZ_PROJETO / "ARQUIVOS PARA DISPAROS"
_DIR_RETORNO = RAIZ_PROJETO / "ARQUIVOS DE RETORNO"
_DIR_RETORNO_WHATSAPP = RAIZ_PROJETO / "ARQUIVOS DE RETORNO WHATSAPP"
_DIR_RETORNO_WHATSAPP_AIRYS = RAIZ_PROJETO / "ARQUIVOS DE RETORNO WHATSAPP AIRYS"
_DIR_RETORNO_RCS = RAIZ_PROJETO / "ARQUIVOS DE RETORNO RCS"
_DIR_RETORNO_EMAIL_SALESFORCE = RAIZ_PROJETO / "ARQUIVOS DE RETORNO EMAIL SALESFORCE"
_DIR_LOG_CRM = RAIZ_PROJETO / "ARQUIVOS LOG"
_DIR_BASE_GRUPO_AB = RAIZ_PROJETO / "ARQUIVO DA BASE INTEIRA"
_ARQUIVO_ANOTACOES_CALENDARIO = RAIZ_PROJETO / "ANOTACOES_CALENDARIO.json"


def descobrir_campanhas() -> dict[str, Path]:
    """Descobre automaticamente as campanhas em escopo: todo arquivo em
    `ARQUIVOS PARA DISPAROS/` vira uma campanha, usando o nome do
    arquivo (sem extensão) como UTM. Basta soltar o arquivo novo na pasta e reiniciar o
    app — não precisa editar código nem renomear nada. Pasta ainda inexistente (nenhum
    arquivo entregue) volta um dicionário vazio, não erro."""
    if not _DIR_DISPARO.exists():
        return {}
    return {caminho.stem: caminho for caminho in sorted(_DIR_DISPARO.glob("*.csv"))}


def campanhas_escopo() -> list[str]:
    """Lista de UTMs em escopo, na ordem descoberta em disco — substitui a antiga
    constante `CAMPANHAS_ESCOPO` (fixa, calculada uma vez só no import)."""
    return list(descobrir_campanhas().keys())


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
    arquivos_retorno = sorted(_DIR_RETORNO.glob("*.csv")) if _DIR_RETORNO.exists() else []
    for retorno_path in arquivos_retorno:
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

UTM_MEDIUM_ORDEM = ["whatsapp", "sms", "rcs", "email"]

_CANAL_POR_FORNECEDOR = {
    "kolmeya": "sms",
    "otima": "whatsapp",
    "airys": "whatsapp",
    "salesforce": "email",
}


def canal_da_campanha(utm: str) -> str:
    """Infere o canal (sms/whatsapp/rcs/email) de uma UTM. RCS é identificado pelo
    token "RCS" em qualquer parte do nome (ex.: "...topofunildia4RCS-otima") — checado
    antes do sufixo de fornecedor, já que RCS hoje usa a mesma plataforma/sufixo do
    WhatsApp Otima ("-otima"). Sem esse token, cai no sufixo da plataforma no nome do
    arquivo de disparo (ex.: "...-kolmeya" -> sms, "...-otima"/"...-airys" -> whatsapp,
    "...-salesforce" -> email). Usado pra restringir o cruzamento de telefone do
    retorno de WhatsApp/RCS só às campanhas do canal certo — sem isso, uma campanha de
    outro canal que por coincidência compartilhe telefones (mesma base de clientes)
    apareceria com resultado que não é dela."""
    if not utm:
        return "desconhecido"
    if "rcs" in utm.lower():
        return "rcs"
    fornecedor = utm.rsplit("-", 1)[-1].lower()
    return _CANAL_POR_FORNECEDOR.get(fornecedor, "desconhecido")


def fornecedor_da_campanha(utm: str) -> str:
    """Fornecedor/plataforma bruta de uma UTM (sufixo do nome do arquivo de disparo,
    ex.: "kolmeya"/"otima"/"airys"/"salesforce") — usado pra distinguir WhatsApp Ótima
    de WhatsApp Airys dentro do mesmo canal "whatsapp" (`canal_da_campanha` agrupa os
    dois porque CRM/filtros globais tratam WhatsApp como um canal só; a tabela por
    campanha de cada provedor precisa da distinção fina pra não misturar retorno de um
    provedor com UTM do outro quando os dois compartilham cliente/telefone)."""
    if not utm:
        return "desconhecido"
    return utm.rsplit("-", 1)[-1].lower()


# Palavra-chave no nome da campanha/UTM -> código de Grupo Estratégico. Usado só como
# último recurso (`_grupo_estrategico_pelo_nome_campanha`) pra disparo por e-mail sem
# coluna "grupo_estrategico" própria e sem telefone pra cruzar com a base de
# segmentação (ver `_preparar_disparo` — telefone_norm fica vazio nesse caso). Mesma
# inferência que já era feita manualmente nos decks .pptx de fraseologia de Email (ver
# CLAUDE.md, seção "Email tem duas identidades") — checar antes "abandonocarrinho" que
# "cadastrado"/"engajado"/"topofunil" não é ambíguo: os quatro nomes não se sobrepõem.
_PALAVRA_GRUPO_ESTRATEGICO_NO_NOME = [
    ("abandonocarrinho", "2_ABANDONO_CARRINHO"),
    ("cadastrado", "3_CADASTRADO"),
    ("engajado", "4_ENGAJADO"),
    ("topofunil", "5_TOPO_FUNIL"),
]


def _grupo_estrategico_pelo_nome_campanha(utm: str) -> str | None:
    """Infere o Grupo Estratégico pelo nome da campanha/UTM — `None` se nenhuma
    palavra-chave bater (fica em Não Classificado, sem inventar)."""
    utm_lower = (utm or "").lower()
    for palavra, grupo in _PALAVRA_GRUPO_ESTRATEGICO_NO_NOME:
        if palavra in utm_lower:
            return grupo
    return None


SITUACOES_WHATSAPP = ["Entregue", "Lido", "Enviado", "Nao Entregue", "Nao Enviado"]
_SITUACAO_WHATSAPP_MAPA = {
    "entregue": "Entregue",
    "lido": "Lido",
    "enviado": "Enviado",
    "não entregue": "Nao Entregue",
    "nao entregue": "Nao Entregue",
    "não enviado": "Nao Enviado",
    "nao enviado": "Nao Enviado",
    # "Indisponível" é status específico do RCS: dispositivo/app do destinatário não
    # tem suporte a RCS disponível no momento do envio, então a mensagem não chega —
    # mesma família de "Não Entregue" (tentativa que falhou, não falta de envio).
    "indisponível": "Nao Entregue",
    "indisponivel": "Nao Entregue",
}

_cache: dict = {}
_cache_telefones_campanha: dict = {}

# Nomes possíveis da coluna de propensão ("Grupo AB", agora renomeada pro negócio pra
# "Prioridade") nos arquivos de origem — testados nessa ordem. Arquivos novos já vêm
# com o nome novo; arquivos antigos (e os que ainda não foram atualizados) continuam
# com "grupo_ab". `ler_csv_auto` sempre baixa pra minúsculo, então aqui já é só
# minúsculo/snake_case.
_NOMES_COLUNA_PRIORIDADE = ["prioridade", "grupo_ab"]


def _coluna_prioridade(df: pd.DataFrame) -> str | None:
    """Acha o nome real da coluna de propensão num dataframe já carregado (colunas em
    minúsculo) — "prioridade" nos arquivos novos, "grupo_ab" nos antigos. `None` se
    nenhuma das duas existir."""
    for nome in _NOMES_COLUNA_PRIORIDADE:
        if nome in df.columns:
            return nome
    return None


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
    # Arquivos de disparo por e-mail vêm ora com a coluna "email", ora "email_1"
    # (mesma origem/fornecedor, exportação varia) — sem esse fallback, um arquivo com
    # "email_1" caía no "desconhecido" e todo o disparo sumia (identificador_norm vazio
    # em 100% das linhas), zerando o volume da campanha inteira. Bug real encontrado
    # em 20260730-CBtopofunildia30-salesforce.csv (3.035 linhas descartadas).
    coluna_email = "email" if "email" in disparo.columns else ("email_1" if "email_1" in disparo.columns else None)
    if "telefone" in disparo.columns:
        disparo["identificador_norm"] = disparo["telefone"].apply(normalizar_telefone)
        tipo = "telefone"
    elif coluna_email:
        disparo["identificador_norm"] = disparo[coluna_email].fillna("").str.strip().str.lower()
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

    # Alguns disparos (Airys/Otima/Salesforce) já vêm com a propensão (Prioridade,
    # antigo "grupo_ab")/grupo_estrategico embutidos na própria base — mais confiável
    # do que recalcular pelo cruzamento de telefone, então tem prioridade sobre o mapa
    # da base de segmentação. `_coluna_prioridade` aceita tanto o nome novo
    # ("prioridade") quanto o antigo ("grupo_ab"), já que nem todo arquivo foi
    # atualizado pro nome novo ainda.
    grupo_ab_arquivo = None
    coluna_prioridade_disparo = _coluna_prioridade(disparo)
    if coluna_prioridade_disparo:
        grupo_ab_arquivo = disparo[["identificador_norm", coluna_prioridade_disparo]].rename(
            columns={coluna_prioridade_disparo: "grupo_ab_arquivo"}
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
    elif tipo_identificador == "email":
        # Disparo por e-mail nunca cruza por telefone (telefone_norm fica vazio, ver
        # `_preparar_disparo`), então sem a coluna própria essas linhas ficariam 100%
        # Não Classificado — último recurso: inferir pelo nome da campanha/UTM.
        grupo_inferido = _grupo_estrategico_pelo_nome_campanha(utm)
        if grupo_inferido:
            grupo_estrategico_arquivo = disparo[["identificador_norm"]].copy()
            grupo_estrategico_arquivo["grupo_estrategico_arquivo"] = grupo_inferido

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
    chave = "base_segmentacao"
    if not forcar_reload and chave in _cache:
        return _cache[chave]

    arquivos = sorted(_DIR_BASE_GRUPO_AB.glob("*.csv")) if _DIR_BASE_GRUPO_AB.exists() else []
    if not arquivos:
        base = pd.DataFrame()
    else:
        base = pd.concat([ler_csv_auto(a) for a in arquivos], ignore_index=True)
        if "cpf" in base.columns:
            base = base.drop_duplicates("cpf", keep="last")

    _cache[chave] = base
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
    """Monta o mapa telefone -> propensão (Prioridade, antigo "grupo_ab") a partir da
    base de segmentação (equivalente ao PROCX manual: explode as colunas
    FONE_1..FONE_4 e associa cada telefone ao valor da linha do cliente). Aceita tanto
    a coluna "prioridade" (arquivos novos) quanto "grupo_ab" (antigos) — ver
    `_coluna_prioridade`."""
    chave = "grupo_ab_mapa"
    if not forcar_reload and chave in _cache:
        return _cache[chave]
    base = _carregar_base_segmentacao(forcar_reload)
    coluna = _coluna_prioridade(base) or "grupo_ab"
    mapa = _montar_mapa_telefone(base, coluna)
    _cache[chave] = mapa
    return mapa


def carregar_mapa_grupo_estrategico(forcar_reload: bool = False) -> dict:
    """Monta o mapa telefone -> grupo_estrategico (2_ABANDONO_CARRINHO, 3_CADASTRADO,
    4_ENGAJADO, 5_TOPO_FUNIL) a partir da mesma base de segmentação, pelo mesmo
    cruzamento por telefone usado no grupo_ab."""
    chave = "grupo_estrategico_mapa"
    if not forcar_reload and chave in _cache:
        return _cache[chave]
    mapa = _montar_mapa_telefone(_carregar_base_segmentacao(forcar_reload), "grupo_estrategico")
    _cache[chave] = mapa
    return mapa


_COLUNAS_VAZIAS_SMS = [
    "identificador_norm", "telefone_norm", "status_raw", "timestamp", "mensagem", "utm_campaign",
    "status_funil", "disparado", "enviado", "entregue", "falhou", "pendente", "data", "hora",
    "grupo_ab", "grupo_estrategico", "frase", "frase_norm",
]


def carregar_dados_sms(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega e unifica os eventos de todas as campanhas descobertas em ARQUIVOS PARA
    DISPAROS/, ligando cada uma ao seu arquivo de retorno por sobreposição
    de telefones (processamento único, cacheado). Nenhuma campanha ainda
    (pasta vazia/inexistente) volta um dataframe vazio, não erro."""
    chave = "sms"
    if not forcar_reload and chave in _cache:
        return _cache[chave]

    campanhas = descobrir_campanhas()
    if not campanhas:
        df = pd.DataFrame(columns=_COLUNAS_VAZIAS_SMS)
        _cache[chave] = df
        return df

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

    _cache[chave] = df
    return df


def _normalizar_telefone_com_ddi(valor) -> str:
    """Telefones do log de CRM vêm com DDI 55 (13 dígitos); remove o DDI para
    ficar no mesmo formato (DDD+numero, 10-11 dígitos) usado no restante da base."""
    digitos = normalizar_telefone(valor)
    if len(digitos) == 13 and digitos.startswith("55"):
        return digitos[2:]
    return digitos


def _utm_sem_token_rcs(utm: str) -> str:
    """UTM sem o token "RCS" (case-insensitive) e em minúsculas — usado pra casar a
    UTM do log de CRM com a UTM do arquivo de disparo mesmo quando só um dos dois
    carrega o token "RCS" no nome. Na prática, a plataforma às vezes gera o link de
    tracking com a UTM "crua" do disparo original (sem "RCS"), mesmo quando renomeamos
    nosso arquivo de disparo pra incluir "RCS" (convenção usada em `canal_da_campanha`
    pra identificar o canal só pelo nome do arquivo) — sem essa normalização, o
    cruzamento por igualdade exata perde 100% do resultado de CRM dessas campanhas."""
    if not isinstance(utm, str):
        return ""
    return re.sub(r"rcs", "", utm, flags=re.IGNORECASE).strip().lower()


def carregar_dados_crm(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega o(s) log(s) de CRM (aba de conversão pós-contato) de ARQUIVOS LOG/ —
    todo arquivo da pasta é lido e concatenado, e filtrado às campanhas
    cadastradas em ARQUIVOS PARA DISPAROS/ (`campanhas_escopo`) — o log em si cobre
    dezenas de campanhas de teste/outras operações que não interessam aqui. Deduplica
    por uma chave composta (doc + utm campaign + acao + data), já que exports
    diferentes podem ter esquema de colunas diferente (misturar deduplicação por `id`
    com linhas sem essa coluna faz o pandas tratar todo NaN como duplicata entre si,
    descartando quase tudo)."""
    chave_cache = "crm"
    if not forcar_reload and chave_cache in _cache:
        return _cache[chave_cache]

    arquivos = sorted(_DIR_LOG_CRM.glob("*.csv")) if _DIR_LOG_CRM.exists() else []
    partes = [ler_csv_auto(caminho) for caminho in arquivos]
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if df.empty:
        _cache[chave_cache] = df
        return df

    # Chave composta (não usa `id`: exports mais antigos e mais novos têm esquemas
    # diferentes, e misturar `id` com linhas sem essa coluna faz o pandas tratar todo
    # NaN como duplicata entre si, descartando quase tudo do arquivo sem `id`).
    chave = [c for c in ["doc", "utm campaign", "acao", "data"] if c in df.columns]
    if chave:
        df = df.drop_duplicates(chave)

    coluna_utm = "utm campaign" if "utm campaign" in df.columns else "utm"
    mapa_utm_sem_rcs = {_utm_sem_token_rcs(u): u for u in campanhas_escopo()}
    df["utm_campaign"] = df[coluna_utm].apply(_utm_sem_token_rcs).map(mapa_utm_sem_rcs)
    df = df[df["utm_campaign"].notna()].copy()
    df["timestamp"] = df["data"].apply(parse_data_pt_br)
    df["acao_norm"] = df["acao"].str.strip().str.lower()
    df = df[df["acao_norm"].isin(ETAPAS_CRM)]
    df["utm_medium"] = df["utm medium"].fillna("").str.strip().str.lower() if "utm medium" in df.columns else ""

    mapa_grupo_ab = carregar_mapa_grupo_ab(forcar_reload)
    df["telefone_norm"] = df["mobile"].apply(_normalizar_telefone_com_ddi)
    df["grupo_ab"] = df["telefone_norm"].map(mapa_grupo_ab).fillna(NAO_CLASSIFICADO)

    mapa_grupo_estrategico = carregar_mapa_grupo_estrategico(forcar_reload)
    df["grupo_estrategico"] = df["telefone_norm"].map(mapa_grupo_estrategico).fillna(NAO_CLASSIFICADO)

    _cache[chave_cache] = df
    return df


_COLUNAS_VAZIAS_OTIMA = [
    "telefone_norm", "situacao_norm", "mensagem_norm", "timestamp", "data", "hora",
    "grupo_ab", "grupo_estrategico",
]


def _carregar_retorno_estilo_otima(
    pasta: Path, cache_key: str, forcar_reload: bool = False,
) -> pd.DataFrame:
    """Carrega retorno por destinatário no formato Otima (Destino/Mensagem/Situação/
    Identificador) de qualquer pasta — reutilizado tanto pelo WhatsApp Otima quanto
    pelo RCS, que usam exatamente o mesmo formato de exportação (RCS roda na mesma
    plataforma). Usado nos cartões de KPI (contagem simples de Entregue/Lido/Enviado/
    Não Entregue/Não Enviado, sem participar do funil de Disparo/Envio/Entrega que é
    específico do SMS/Kolmeya) e na seção "Resultado por Mensagem" da aba Conversão
    Pós-Contato (CRM)."""
    chave = cache_key
    if not forcar_reload and chave in _cache:
        return _cache[chave]

    arquivos = sorted(pasta.glob("*.csv")) if pasta.exists() else []
    partes = [ler_csv_auto(caminho) for caminho in arquivos]
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if df.empty:
        df = pd.DataFrame(columns=_COLUNAS_VAZIAS_OTIMA)
        _cache[chave] = df
        return df

    if "identificador" in df.columns:
        df = df.drop_duplicates("identificador")

    df["telefone_norm"] = df["destino"].apply(_normalizar_telefone_com_ddi)
    df["situacao_norm"] = (
        df["situação"].str.strip().str.lower().map(_SITUACAO_WHATSAPP_MAPA).fillna("Outro")
    )
    df["mensagem_norm"] = df["mensagem"].apply(normalizar_mensagem_whatsapp)
    df = df[df["telefone_norm"] != ""]

    # "mixed": o retorno do WhatsApp Otima não traz segundos ("28/07/2026 13:25"), mas o
    # do RCS traz ("04/08/2026 08:21:53") — um formato fixo faz um dos dois cair 100% em
    # NaT (já que os dois passam por esse mesmo carregador, ver docstring da função).
    df["timestamp"] = pd.to_datetime(df["data envio"], format="mixed", dayfirst=True, errors="coerce")
    df["data"] = df["timestamp"].dt.date
    df["hora"] = df["timestamp"].dt.hour

    mapa_grupo_ab = carregar_mapa_grupo_ab(forcar_reload)
    df["grupo_ab"] = df["telefone_norm"].map(mapa_grupo_ab).fillna(NAO_CLASSIFICADO)
    mapa_grupo_estrategico = carregar_mapa_grupo_estrategico(forcar_reload)
    df["grupo_estrategico"] = df["telefone_norm"].map(mapa_grupo_estrategico).fillna(NAO_CLASSIFICADO)

    _cache[chave] = df
    return df


def carregar_dados_whatsapp_mensagem(forcar_reload: bool = False) -> pd.DataFrame:
    """Retorno de WhatsApp Otima em `ARQUIVOS DE RETORNO WHATSAPP/` — ver
    `_carregar_retorno_estilo_otima`."""
    return _carregar_retorno_estilo_otima(
        _DIR_RETORNO_WHATSAPP, "whatsapp_mensagem", forcar_reload,
    )


def carregar_dados_rcs(forcar_reload: bool = False) -> pd.DataFrame:
    """Retorno de RCS em `ARQUIVOS DE RETORNO RCS/` — mesma plataforma/formato do
    WhatsApp Otima, ver `_carregar_retorno_estilo_otima`."""
    return _carregar_retorno_estilo_otima(_DIR_RETORNO_RCS, "rcs_mensagem", forcar_reload)


_STATUS_FUNIL_A_PARTIR_DE_SITUACAO = {
    "Entregue": "Entregue",
    "Lido": "Entregue",
    "Enviado": "Pendente",
    "Nao Entregue": "Falhou",
    "Nao Enviado": "Nao Processado",
}


def _converter_estilo_sms(
    df: pd.DataFrame, canal: str, cache_key: str, forcar_reload: bool = False,
) -> pd.DataFrame:
    """Converte um retorno com granularidade por destinatário (formato WhatsApp/RCS —
    telefone_norm/situacao_norm) pro mesmo formato linha-a-linha do SMS/Kolmeya
    (disparado/enviado/entregue/falhou como flags 0/1 por linha, status_funil,
    utm_campaign), cruzando cada campanha do canal escolhido por telefone (o retorno
    não traz a UTM da campanha). Isso permite reaproveitar toda a pipeline de
    agregação/gráficos/tabelas já feita pro SMS (`calcular_kpis`, `calcular_funil`,
    `agregar_por_campanha`, `agregar_por_grupo_ab`,
    `montar_tabela_grupo_estrategico_com_ab`, `filtrar_dados`, ...) em qualquer canal
    que siga esse mesmo formato de retorno — hoje usado pelo RCS, que roda na mesma
    plataforma do WhatsApp Otima mas deve se comportar exatamente como o SMS."""
    colunas_vazias = [
        "telefone_norm", "utm_campaign", "situacao_norm", "grupo_ab", "grupo_estrategico",
        "mensagem_norm", "disparado", "enviado", "entregue", "falhou", "status_funil",
        "timestamp", "data", "hora",
    ]
    chave = cache_key
    if not forcar_reload and chave in _cache:
        return _cache[chave]

    utms_canal = [u for u in campanhas_escopo() if canal_da_campanha(u) == canal]
    partes = []
    if not df.empty and utms_canal:
        for utm in utms_canal:
            telefones = telefones_das_campanhas([utm])
            sub = df[df["telefone_norm"].isin(telefones)].copy()
            if sub.empty:
                continue
            sub["utm_campaign"] = utm
            partes.append(sub)

    if not partes:
        resultado = pd.DataFrame(columns=colunas_vazias)
        _cache[chave] = resultado
        return resultado

    resultado = pd.concat(partes, ignore_index=True)
    # `pd.concat` de vários pedaços às vezes reconverte a coluna "data" (que era
    # datetime.date por linha, dtype "object") pra datetime64 — o que quebra a
    # comparação com os `date` do filtro de Período em `filtrar_dados`. Recalcula
    # direto do timestamp pra garantir o mesmo dtype "object" usado pelo SMS.
    resultado["data"] = resultado["timestamp"].dt.date
    resultado["hora"] = resultado["timestamp"].dt.hour
    resultado["disparado"] = 1
    resultado["enviado"] = resultado["situacao_norm"].isin(
        ["Entregue", "Lido", "Enviado", "Nao Entregue"]
    ).astype(int)
    resultado["entregue"] = resultado["situacao_norm"].isin(["Entregue", "Lido"]).astype(int)
    resultado["falhou"] = (resultado["situacao_norm"] == "Nao Entregue").astype(int)
    resultado["status_funil"] = (
        resultado["situacao_norm"].map(_STATUS_FUNIL_A_PARTIR_DE_SITUACAO).fillna("Nao Processado")
    )
    _cache[chave] = resultado
    return resultado


def carregar_dados_rcs_estilo_sms(forcar_reload: bool = False) -> pd.DataFrame:
    """RCS convertido pro formato linha-a-linha do SMS — ver `_converter_estilo_sms`.
    Usado na aba Funil Geral e nas abas Grupo AB/Grupo Estratégico, que já são 100%
    genéricas em relação ao formato desse dataframe."""
    return _converter_estilo_sms(
        carregar_dados_rcs(forcar_reload), "rcs", "rcs_estilo_sms", forcar_reload,
    )


_STATUS_ATUAL_AIRYS_LABEL = {
    "read": "Lido",
    "delivered": "Entregue",
    "sent": "Enviado",
    "failed": "Falhou",
    "rejected": "Rejeitado",
}

_RESULTADO_RESPOSTA_AIRYS_LABEL = {
    "sem_resposta_na_janela": "Sem Resposta na Janela",
    "respondeu": "Respondeu",
    "interesse_negociacao": "Interesse em Negociação",
    "opt_out_confirmado": "Opt-out Confirmado",
    "negativo_reclamacao": "Negativo / Reclamação",
}


def _extrair_telefone_wamid(wamid) -> str:
    """O `numero_whatsapp` do export do Airys vem truncado (notação científica gerada
    ao salvar em Excel, ex.: "5,53186E+11"), então o telefone real é extraído
    decodificando o `provider_message_id` (formato "wamid.<base64>"), que embute o
    número completo sem perda de precisão."""
    if not isinstance(wamid, str) or not wamid.startswith("wamid."):
        return ""
    corpo = wamid[len("wamid."):]
    corpo += "=" * (-len(corpo) % 4)
    try:
        decodificado = base64.b64decode(corpo).decode("latin1", errors="ignore")
    except Exception:
        return ""
    encontrado = re.search(r"\d{10,13}", decodificado)
    return encontrado.group(0) if encontrado else ""


def _reconstruir_telefone_airys(bruto: str, telefones_conhecidos: dict) -> str:
    """Normaliza o telefone decodificado do wamid pro mesmo formato usado no resto do
    app (DDD + 9 dígitos, sem DDI). O wamid às vezes embute o número no formato antigo,
    de 12 dígitos (DDI 55 + DDD + 8 dígitos, sem o "9" que a Anatel passou a exigir nos
    celulares) — ex.: "553186492355" em vez de "5531986492355"/"31986492355". Sem tratar
    esse caso, `_normalizar_telefone_com_ddi` (que só tira o DDI quando o total dá 13
    dígitos) deixava esses números com DDI e sem o 9º dígito, o que nunca batia com a
    base de segmentação nem com o arquivo de disparo — inflando artificialmente o
    "Não Classificado" do Airys (validado: sobe de 47% para 80% de casamento com a
    base). Testa as duas leituras possíveis (com e sem o "9" reinserido) contra os
    telefones conhecidos da base e fica com a que bate; na ausência de um match,
    assume o formato moderno (com o "9"), que é o padrão atual da telefonia móvel."""
    sem_ddi = bruto[2:] if bruto.startswith("55") and len(bruto) in (12, 13) else bruto
    if len(sem_ddi) != 10:
        return sem_ddi
    candidatos = [sem_ddi[:2] + "9" + sem_ddi[2:], sem_ddi]
    for candidato in candidatos:
        if candidato in telefones_conhecidos:
            return candidato
    return candidatos[0]


_COLUNAS_VAZIAS_AIRYS = [
    *_COLUNAS_VAZIAS_OTIMA, "status_atual_label", "respondeu_apos_envio", "resultado_resposta_norm",
]


def carregar_dados_airys(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega o retorno do Airys (AirysChat + Meta Graph API) em `ARQUIVOS DE RETORNO
    WHATSAPP AIRYS/` — granularidade por destinatário/mensagem, com status detalhado
    (Entregue/Lido/Enviado/Falhou ou Rejeitado), resposta do cliente (Respondeu após
    Envio, Resultado da Resposta) e template. O telefone vem de decodificar o
    `provider_message_id` (ver `_extrair_telefone_wamid`) — a coluna `numero_whatsapp`
    do export vem truncada. O status é traduzido pro mesmo vocabulário usado no
    WhatsApp Otima (Entregue/Lido/Enviado/Não Entregue/Não Enviado), reaproveitando
    toda a agregação/gráficos/tabelas já feitos pra esse formato."""
    chave = "airys"
    if not forcar_reload and chave in _cache:
        return _cache[chave]

    arquivos = sorted(_DIR_RETORNO_WHATSAPP_AIRYS.glob("*.csv")) if _DIR_RETORNO_WHATSAPP_AIRYS.exists() else []
    partes = [ler_csv_auto(caminho) for caminho in arquivos]
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if df.empty:
        df = pd.DataFrame(columns=_COLUNAS_VAZIAS_AIRYS)
        _cache[chave] = df
        return df

    if "provider_message_id" in df.columns:
        df = df.drop_duplicates("provider_message_id")

    mapa_grupo_ab = carregar_mapa_grupo_ab(forcar_reload)
    df["telefone_norm"] = (
        df["provider_message_id"].apply(_extrair_telefone_wamid)
        .apply(lambda t: _reconstruir_telefone_airys(t, mapa_grupo_ab) if t else "")
    )
    df = df[df["telefone_norm"] != ""]

    status_norm = df["status_atual"].fillna("").str.strip().str.lower()
    df["status_atual_label"] = status_norm.map(_STATUS_ATUAL_AIRYS_LABEL).fillna("Não Enviado")
    df["situacao_norm"] = status_norm.map(
        {"read": "Lido", "delivered": "Entregue", "sent": "Enviado"}
    ).fillna("Nao Enviado")
    falhou = df["falhou_ou_rejeitado"].fillna("").str.strip().str.lower() == "sim"
    df.loc[falhou, "situacao_norm"] = "Nao Entregue"
    df.loc[falhou, "status_atual_label"] = "Falhou ou Rejeitado"

    df["mensagem_norm"] = df["template_nome"].fillna("(sem template)")
    df.loc[df["mensagem_norm"].astype(str).str.strip() == "", "mensagem_norm"] = "(sem template)"

    df["respondeu_apos_envio"] = df["respondeu_apos_envio"].fillna("").str.strip().str.lower() == "sim"
    resultado_norm = df["resultado_resposta"].fillna("").str.strip()
    df["resultado_resposta_norm"] = resultado_norm.apply(
        lambda v: _RESULTADO_RESPOSTA_AIRYS_LABEL.get(v, v) if v else "Sem Retorno"
    )

    df["timestamp"] = pd.to_datetime(df["enviado_em_brt"], errors="coerce")
    df["data"] = df["timestamp"].dt.date
    df["hora"] = df["timestamp"].dt.hour

    df["grupo_ab"] = df["telefone_norm"].map(mapa_grupo_ab).fillna(NAO_CLASSIFICADO)
    mapa_grupo_estrategico = carregar_mapa_grupo_estrategico(forcar_reload)
    df["grupo_estrategico"] = df["telefone_norm"].map(mapa_grupo_estrategico).fillna(NAO_CLASSIFICADO)

    _cache[chave] = df
    return df


def calcular_kpis_resposta_airys(df: pd.DataFrame) -> dict:
    """Quantos clientes responderam após o envio, no retorno do Airys."""
    if df.empty:
        return {"respondeu": 0, "total": 0}
    return {"respondeu": int(df["respondeu_apos_envio"].sum()), "total": len(df)}


def agregar_resultado_resposta_airys(df: pd.DataFrame) -> pd.DataFrame:
    """Contagem por resultado da resposta (Sem Resposta na Janela/Respondeu/Interesse
    em Negociação/Opt-out Confirmado/Negativo-Reclamação/...) do retorno do Airys."""
    if df.empty:
        return pd.DataFrame(columns=["resultado_resposta_norm", "quantidade"])
    contagem = df["resultado_resposta_norm"].value_counts().reset_index()
    contagem.columns = ["resultado_resposta_norm", "quantidade"]
    return contagem


_METRICAS_EMAIL_SALESFORCE = [
    "Email Sends", "Email Deliveries", "Email Delivery Rate", "Email Total Opens",
    "Email Unique Opens", "Email Open Rate", "Email Total Clicks", "Email Unique Clicks",
    "Email Click Rate", "Email Click To Open Rate", "Email Bounces", "Email Bounces - Soft",
    "Email Bounces - Hard", "Email Bounce Rate", "Email Unique Unsubscribes",
    "Email Unsubscribe Rate",
]


def _parse_outline_email_salesforce(caminho: Path) -> pd.DataFrame:
    """Reconstrói o export "Main Metrics" (outline do Salesforce Journey Builder) numa
    linha por e-mail/dia. O export original vem "achatado": cada e-mail some espalhado
    em 5 linhas (Activity Name / Job ID / Journey Name / Content Name / Subject), cada
    uma preenchendo só a sua própria coluna de rótulo — mas repetindo os MESMOS valores
    de métrica (Sends/Deliveries/Opens/...) nas 5 linhas, já que descrevem o mesmo
    envio. Linhas com "Journey ID" preenchido são subtotais por jornada (ou o total
    geral, na última linha) — servem só pra saber a qual jornada os blocos seguintes
    pertencem, não viram linha própria na tabela final."""
    df = pd.read_excel(caminho)
    df.columns = [str(c).strip() for c in df.columns]

    jornada_atual = None
    linhas = []
    i, n = 0, len(df)
    while i < n:
        linha = df.iloc[i]
        if pd.notna(linha.get("Journey ID")):
            jornada_atual = linha.get("Journey ID")
            i += 1
            continue
        bloco = df.iloc[i:i + 5]
        if len(bloco) < 5:
            break
        registro = {
            "journey_id": jornada_atual,
            "activity_name": bloco.iloc[0].get("Journey Activity Name"),
            "job_id": bloco.iloc[1].get("Email Job ID"),
            "journey_name": bloco.iloc[2].get("Journey Name"),
            "content_name": bloco.iloc[3].get("Email Content Name"),
            "subject": bloco.iloc[4].get("Email Subject"),
        }
        for coluna in _METRICAS_EMAIL_SALESFORCE:
            if coluna not in bloco.columns:
                registro[coluna] = None
                continue
            valores = bloco[coluna].dropna().unique()
            registro[coluna] = valores[0] if len(valores) else None
        # Se não achou um Job ID de verdade nesse bloco, os 5 linhas não são um e-mail
        # (ex.: linha "Total" no fim do arquivo) — descarta em vez de virar lixo na tabela.
        if pd.isna(registro["job_id"]):
            i += 1
            continue
        linhas.append(registro)
        i += 5

    return pd.DataFrame(linhas)


def carregar_dados_email_salesforce(forcar_reload: bool = False) -> pd.DataFrame:
    """Carrega o(s) export(s) "Main Metrics" do Salesforce Journey Builder em
    ARQUIVOS DE RETORNO EMAIL SALESFORCE/*.xlsx (todo arquivo da pasta é somado) —
    métricas de engajamento por e-mail/dia (Envios/Entregues/Aberturas/Cliques/Bounce),
    bem diferentes do resto do dashboard (aqui não tem telefone nem timestamp por
    destinatário, é um relatório já agregado pela própria plataforma), então essa
    seção não responde aos filtros globais de campanha/data/hora/grupo_ab."""
    chave = "email_salesforce"
    if not forcar_reload and chave in _cache:
        return _cache[chave]

    arquivos = sorted(_DIR_RETORNO_EMAIL_SALESFORCE.glob("*.xlsx")) if _DIR_RETORNO_EMAIL_SALESFORCE.exists() else []
    partes = [_parse_outline_email_salesforce(caminho) for caminho in arquivos]
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if df.empty:
        _cache[chave] = df
        return df

    total_envios = df["Email Sends"].sum()
    df["Jornada"] = df["journey_name"]
    df["E-mail"] = df["activity_name"]
    df["Assunto"] = df["subject"]
    df["Envios"] = df["Email Sends"].astype(int)
    df["% envios"] = (df["Email Sends"] / total_envios * 100) if total_envios else 0.0
    df["Entregues"] = df["Email Deliveries"].astype(int)
    df["Entrega"] = df["Email Delivery Rate"] * 100
    df["Bounce"] = df["Email Bounce Rate"] * 100
    df["Aberturas"] = df["Email Unique Opens"].astype(int)
    df["Abertura"] = df["Email Open Rate"] * 100
    df["Cliques"] = df["Email Unique Clicks"].astype(int)
    df["CTR"] = df["Email Click Rate"] * 100
    df["CTOR"] = df["Email Click To Open Rate"] * 100
    df["Eficiência"] = df["Entrega"] * df["Abertura"] * df["CTOR"] / 10_000

    df = df.sort_values(["Jornada", "Envios"], ascending=[True, False]).reset_index(drop=True)
    _cache[chave] = df
    return df


def calcular_kpis_email_salesforce(df: pd.DataFrame) -> dict:
    """KPIs gerais (linha "Total Geral") do e-mail Salesforce, mesmas fórmulas usadas
    linha a linha em `carregar_dados_email_salesforce` — Entrega/Abertura/CTR/CTOR
    recalculados sobre os totais somados, não a média das taxas de cada e-mail."""
    vazio = {
        "envios": 0, "entregues": 0, "taxa_entrega": 0.0, "bounces": 0, "taxa_bounce": 0.0,
        "aberturas": 0, "taxa_abertura": 0.0, "cliques": 0, "taxa_ctr": 0.0, "taxa_ctor": 0.0,
        "eficiencia": 0.0,
    }
    if df.empty:
        return vazio

    envios = int(df["Envios"].sum())
    entregues = int(df["Entregues"].sum())
    aberturas = int(df["Aberturas"].sum())
    cliques = int(df["Cliques"].sum())
    bounces = int(df["Email Bounces"].sum())
    taxa_entrega = taxa(entregues, envios)
    taxa_abertura = taxa(aberturas, entregues)
    taxa_ctr = taxa(cliques, entregues)
    taxa_ctor = taxa(cliques, aberturas)
    return {
        "envios": envios,
        "entregues": entregues,
        "taxa_entrega": taxa_entrega,
        "bounces": bounces,
        "taxa_bounce": taxa(bounces, envios),
        "aberturas": aberturas,
        "taxa_abertura": taxa_abertura,
        "cliques": cliques,
        "taxa_ctr": taxa_ctr,
        "taxa_ctor": taxa_ctor,
        "eficiencia": taxa_entrega * taxa_abertura * taxa_ctor / 10_000,
    }


def agregar_email_salesforce_por_jornada(df: pd.DataFrame) -> pd.DataFrame:
    """Soma Envios/Entregues/Aberturas/Cliques por Jornada, ordenada da maior pra
    menor volumetria — usado no gráfico de volume por jornada."""
    if df.empty:
        return pd.DataFrame(columns=["Jornada", "Envios", "Entregues", "Aberturas", "Cliques"])
    agrupado = df.groupby("Jornada", as_index=False)[["Envios", "Entregues", "Aberturas", "Cliques"]].sum()
    return agrupado.sort_values("Envios", ascending=False).reset_index(drop=True)


def telefones_das_campanhas(utms: list[str]) -> set[str]:
    """Telefones (normalizados) das campanhas selecionadas, direto do arquivo de
    disparo — usado para ligar o retorno de canais sem vínculo automático por job (ex.:
    WhatsApp Otima/Airys) à campanha certa, pelo mesmo cruzamento de telefone usado no
    resto do dashboard. O retorno do Otima não traz a UTM da campanha, só o nome
    interno do fornecedor. Prioriza a coluna `sms_whats` (com DDI, específica do envio
    de WhatsApp/SMS) sobre `telefone` quando o arquivo de disparo tiver as duas — no
    arquivo da Otima elas são idênticas, mas `sms_whats` é a coluna certa caso um
    arquivo futuro traga números diferentes entre as duas. Cacheado por campanha — não
    só o resultado final da união: essa função é chamada campanha a
    campanha em vários pontos do dashboard (tabela por campanha de WhatsApp/Airys/RCS)
    a cada atualização de filtro, e sem cache reabriria e reparseria o CSV de disparo
    do zero em cada chamada — com várias campanhas isso é o principal gargalo de
    performance do callback."""
    campanhas = descobrir_campanhas()
    telefones: set[str] = set()
    for utm in utms:
        chave = utm
        if chave in _cache_telefones_campanha:
            telefones |= _cache_telefones_campanha[chave]
            continue
        caminho = campanhas.get(utm)
        if caminho is None:
            continue
        df = ler_csv_auto(caminho)
        if "sms_whats" in df.columns:
            telefones_utm = {_normalizar_telefone_com_ddi(v) for v in df["sms_whats"]}
        elif "telefone" in df.columns:
            telefones_utm = {normalizar_telefone(v) for v in df["telefone"]}
        else:
            telefones_utm = set()
        telefones_utm.discard("")
        _cache_telefones_campanha[chave] = telefones_utm
        telefones |= telefones_utm
    telefones.discard("")
    return telefones


def total_disparado_campanhas(utms: list[str]) -> int:
    """Total de disparos (telefones únicos no arquivo de disparo) das campanhas
    selecionadas — usado como "Total Disparado" de canais cujo retorno é só por
    destinatário (WhatsApp Ótima/Airys), já que o retorno nem sempre cobre 100% do que
    foi de fato disparado (o Airys, por exemplo, só retornou status pra uma fração da
    lista de disparo: 968 de 3804). Somado campanha a campanha (em vez de uma união
    global) pra não subcontar caso o mesmo telefone apareça em mais de uma campanha."""
    return sum(len(telefones_das_campanhas([utm])) for utm in utms)


def filtrar_dados_whatsapp(
    df: pd.DataFrame,
    utms: list[str] | None = None,
    data_ini=None,
    data_fim=None,
    hora_ini: int | None = None,
    hora_fim: int | None = None,
    grupos_ab: list[str] | None = None,
    grupos_estrategicos: list[str] | None = None,
    canal: str = "whatsapp",
) -> pd.DataFrame:
    """Aplica os filtros globais (campanha/período/hora/grupo_ab/grupo_estratégico)
    sobre um retorno com granularidade por destinatário (WhatsApp ou RCS), restringindo
    aos telefones das campanhas do canal selecionado (campanhas de outro canal são
    ignoradas, mesmo se selecionadas junto — ver `canal_da_campanha`). `canal` escolhe
    qual canal filtrar ("whatsapp"/"rcs"), reutilizável pra qualquer canal que siga
    esse mesmo formato de retorno."""
    if df.empty:
        return df
    filtrado = df
    if utms:
        utms_canal = [u for u in utms if canal_da_campanha(u) == canal]
        if not utms_canal:
            return df.iloc[0:0]
        filtrado = filtrado[filtrado["telefone_norm"].isin(telefones_das_campanhas(utms_canal))]
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


def calcular_kpis_whatsapp(df: pd.DataFrame) -> dict:
    """Contagem simples por status final (Entregue/Lido/Enviado/Não Entregue/Não
    Enviado) do retorno de WhatsApp, pros cartões de KPI da aba Funil Geral."""
    if df.empty:
        return {status: 0 for status in SITUACOES_WHATSAPP}
    contagem = df["situacao_norm"].value_counts()
    return {status: int(contagem.get(status, 0)) for status in SITUACOES_WHATSAPP}


def _agregar_whatsapp_por(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Contagem de status finais do WhatsApp (Entregue/Lido/Enviado/Não Entregue/Não
    Enviado) agrupada por uma coluna (grupo_ab ou grupo_estrategico), com as mesmas
    taxas de entrega/leitura/falha usadas no "Resultado por Mensagem"."""
    colunas_vazias = [coluna, *SITUACOES_WHATSAPP, "total", "taxa_entrega", "taxa_leitura", "taxa_falha"]
    if df.empty:
        return pd.DataFrame(columns=colunas_vazias)

    contagem = df.groupby([coluna, "situacao_norm"]).size().unstack(fill_value=0)
    for status in SITUACOES_WHATSAPP:
        if status not in contagem.columns:
            contagem[status] = 0
    contagem = contagem[SITUACOES_WHATSAPP].reset_index()

    contagem["total"] = contagem[SITUACOES_WHATSAPP].sum(axis=1)
    contagem["taxa_entrega"] = contagem.apply(
        lambda r: taxa(r["Entregue"] + r["Lido"], r["total"]), axis=1
    )
    contagem["taxa_leitura"] = contagem.apply(lambda r: taxa(r["Lido"], r["total"]), axis=1)
    contagem["taxa_falha"] = contagem.apply(
        lambda r: taxa(r["Nao Entregue"] + r["Nao Enviado"], r["total"]), axis=1
    )
    return contagem


def agregar_whatsapp_por_grupo_ab(df: pd.DataFrame) -> pd.DataFrame:
    """Resultado de WhatsApp (Entregue/Lido/Enviado/Não Entregue/Não Enviado) por
    grupo_ab, ordenado por prioridade P1_MAXIMA -> P4_BAIXA -> Não Classificado."""
    agrupado = _agregar_whatsapp_por(df, "grupo_ab")
    if agrupado.empty:
        return agrupado
    agrupado["ordem"] = agrupado["grupo_ab"].apply(
        lambda g: GRUPO_AB_ORDEM.index(g) if g in GRUPO_AB_ORDEM else len(GRUPO_AB_ORDEM)
    )
    return agrupado.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def agregar_whatsapp_por_grupo_estrategico(df: pd.DataFrame) -> pd.DataFrame:
    """Resultado de WhatsApp (Entregue/Lido/Enviado/Não Entregue/Não Enviado) por
    grupo_estrategico, ordenado pela numeração do próprio grupo."""
    agrupado = _agregar_whatsapp_por(df, "grupo_estrategico")
    if agrupado.empty:
        return agrupado
    agrupado["ordem"] = agrupado["grupo_estrategico"].apply(
        lambda g: GRUPO_ESTRATEGICO_ORDEM.index(g) if g in GRUPO_ESTRATEGICO_ORDEM else len(GRUPO_ESTRATEGICO_ORDEM)
    )
    return agrupado.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def agregar_whatsapp_por_campanha(
    df: pd.DataFrame, utms: list[str], canal: str = "whatsapp",
) -> pd.DataFrame:
    """Resultado de WhatsApp/RCS (Entregue/Lido/Enviado/Não Entregue/Não Enviado) por
    campanha, cruzando por telefone — o retorno do Otima não traz a UTM da campanha, só
    o nome interno do fornecedor (mesmo princípio de `telefones_das_campanhas`). Só
    considera as UTMs que são de fato do canal escolhido (ver `canal_da_campanha`),
    ordenado da maior para a menor volumetria."""
    colunas_vazias = ["utm_campaign", *SITUACOES_WHATSAPP, "total", "taxa_entrega", "taxa_leitura", "taxa_falha"]
    utms_canal = [u for u in utms if canal_da_campanha(u) == canal]
    if df.empty or not utms_canal:
        return pd.DataFrame(columns=colunas_vazias)

    linhas = []
    for utm in utms_canal:
        telefones = telefones_das_campanhas([utm])
        sub = df[df["telefone_norm"].isin(telefones)]
        if sub.empty:
            continue
        agregado = _agregar_whatsapp_por(sub.assign(utm_campaign=utm), "utm_campaign")
        linhas.append(agregado)

    if not linhas:
        return pd.DataFrame(columns=colunas_vazias)
    return pd.concat(linhas, ignore_index=True).sort_values("total", ascending=False).reset_index(drop=True)


def agregar_mensagem_whatsapp(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela por mensagem-modelo de WhatsApp (sem a saudação personalizada), com a
    contagem de cada status final (Entregue/Lido/Enviado/Não Entregue/Não Enviado) e
    as taxas de entrega/leitura/falha, ordenada da maior para a menor volumetria."""
    colunas_vazias = ["mensagem_norm", *SITUACOES_WHATSAPP, "total", "taxa_entrega", "taxa_leitura", "taxa_falha"]
    if df.empty:
        return pd.DataFrame(columns=colunas_vazias)

    validas = df[df["mensagem_norm"] != ""]
    if validas.empty:
        return pd.DataFrame(columns=colunas_vazias)

    contagem = validas.groupby(["mensagem_norm", "situacao_norm"]).size().unstack(fill_value=0)
    for status in SITUACOES_WHATSAPP:
        if status not in contagem.columns:
            contagem[status] = 0
    contagem = contagem[SITUACOES_WHATSAPP].reset_index()

    contagem["total"] = contagem[SITUACOES_WHATSAPP].sum(axis=1)
    contagem["taxa_entrega"] = contagem.apply(
        lambda r: taxa(r["Entregue"] + r["Lido"], r["total"]), axis=1
    )
    contagem["taxa_leitura"] = contagem.apply(lambda r: taxa(r["Lido"], r["total"]), axis=1)
    contagem["taxa_falha"] = contagem.apply(
        lambda r: taxa(r["Nao Entregue"] + r["Nao Enviado"], r["total"]), axis=1
    )
    return contagem.sort_values("total", ascending=False).reset_index(drop=True)


def agregar_mensagem_whatsapp_com_crm(df_whatsapp: pd.DataFrame, df_crm: pd.DataFrame) -> pd.DataFrame:
    """Tabela por mensagem-modelo de WhatsApp incluindo o resultado final no CRM
    (home/auth/oferta/acordo), cruzado por telefone — mesmo princípio usado para a
    frase de SMS (`agregar_frase_com_crm`)."""
    base = agregar_mensagem_whatsapp(df_whatsapp)
    for etapa in ETAPAS_CRM:
        base[etapa] = 0
    if base.empty or df_crm.empty:
        return base

    contagem = _contagem_crm_por_texto(df_whatsapp, "mensagem_norm", df_crm)
    if contagem.empty:
        return base
    base = base.drop(columns=ETAPAS_CRM).merge(contagem, on="mensagem_norm", how="left")
    for etapa in ETAPAS_CRM:
        base[etapa] = base[etapa].fillna(0).astype(int)
    return base


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


def _montar_funil(etapas: list[tuple[str, int]]) -> list[dict]:
    """Monta a lista de etapas de um funil (quantidade, % sobre a base, conversão e
    perda em relação à etapa anterior) a partir de uma sequência (nome, valor) já em
    ordem decrescente esperada — reutilizado por todos os funis do dashboard."""
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


def calcular_funil_a_partir_de_kpis(kpis: dict) -> list[dict]:
    """Monta as 4 etapas do funil (Disparado -> Enviado -> Entregue -> Falhou) a partir
    de um dict de KPIs já no formato de `calcular_kpis` — usado por `calcular_funil`."""
    return _montar_funil([
        ("Disparado", kpis["disparado"]),
        ("Enviado", kpis["enviado"]),
        ("Entregue", kpis["entregue"]),
        ("Falhou", kpis["falhou"]),
    ])


def calcular_funil(df: pd.DataFrame) -> list[dict]:
    """Monta as 4 etapas do funil (Disparado -> Enviado -> Entregue -> Falhou)."""
    return calcular_funil_a_partir_de_kpis(calcular_kpis(df))


def calcular_funil_email_salesforce(kpis_email: dict) -> list[dict]:
    """Monta as 4 etapas do funil de e-mail (Envios -> Entregues -> Aberturas ->
    Cliques) a partir de `calcular_kpis_email_salesforce` — sem "Falhou" como no SMS,
    já que aqui o equivalente (Bounce) já aparece como KPI/taxa à parte."""
    return _montar_funil([
        ("Envios", kpis_email["envios"]),
        ("Entregues", kpis_email["entregues"]),
        ("Aberturas", kpis_email["aberturas"]),
        ("Cliques", kpis_email["cliques"]),
    ])


def calcular_funil_whatsapp(kpis_whatsapp: dict) -> list[dict]:
    """Monta o funil de WhatsApp (Disparado -> Enviado -> Entregue -> Lido) a partir da
    contagem de status finais (Entregue/Lido/Enviado/Não Entregue/Não Enviado), que são
    mutuamente exclusivos por natureza (cada envio termina em só um status): Enviado
    exclui quem falhou antes de sair (Não Enviado); Entregue soma quem só foi entregue
    com quem já leu (Lido é um estágio mais avançado de quem foi entregue)."""
    entregue = kpis_whatsapp["Entregue"]
    lido = kpis_whatsapp["Lido"]
    enviado_status = kpis_whatsapp["Enviado"]
    nao_entregue = kpis_whatsapp["Nao Entregue"]
    nao_enviado = kpis_whatsapp["Nao Enviado"]

    return _montar_funil([
        ("Disparado", entregue + lido + enviado_status + nao_entregue + nao_enviado),
        ("Enviado", entregue + lido + enviado_status + nao_entregue),
        ("Entregue", entregue + lido),
        ("Lido", lido),
    ])


def calcular_funil_combinado_sms(kpis: dict, totais_crm: dict) -> list[dict]:
    """Funil combinado Disparo + CRM do SMS: continua o funil de entrega (Disparado ->
    Enviado -> Entregue) direto para o funil de negociação (Home -> Autenticação ->
    Oferta -> Acordo), numa visão única ponta a ponta."""
    return _montar_funil([
        ("Disparado", kpis["disparado"]),
        ("Enviado", kpis["enviado"]),
        ("Entregue", kpis["entregue"]),
        ("Home", totais_crm["home"]),
        ("Autenticação", totais_crm["auth"]),
        ("Oferta Apresentada", totais_crm["oferta"]),
        ("Acordo Gerado", totais_crm["acordo"]),
    ])


def calcular_funil_combinado_whatsapp(
    kpis_whatsapp: dict, totais_crm: dict, total_disparado: int | None = None,
) -> list[dict]:
    """Funil combinado Disparo + CRM do WhatsApp: continua o funil de entrega
    (Disparado -> Enviado -> Entregue -> Lido) direto para o funil de negociação
    (Home -> Autenticação -> Oferta -> Acordo), numa visão única ponta a ponta.
    `total_disparado`, quando informado, substitui a soma dos status do retorno como
    valor de "Disparado" — o retorno por destinatário (Otima/Airys) às vezes só cobre
    uma fração de quem foi de fato disparado (a API do Airys, por exemplo, só devolveu
    status pra 968 de 3804 disparos), então a soma dos status do retorno subestima o
    "Disparado" real; ver `total_disparado_campanhas`."""
    entregue = kpis_whatsapp["Entregue"]
    lido = kpis_whatsapp["Lido"]
    enviado_status = kpis_whatsapp["Enviado"]
    nao_entregue = kpis_whatsapp["Nao Entregue"]
    nao_enviado = kpis_whatsapp["Nao Enviado"]
    disparado = (
        total_disparado if total_disparado is not None
        else entregue + lido + enviado_status + nao_entregue + nao_enviado
    )

    return _montar_funil([
        ("Disparado", disparado),
        ("Enviado", entregue + lido + enviado_status + nao_entregue),
        ("Entregue", entregue + lido),
        ("Lido", lido),
        ("Home", totais_crm["home"]),
        ("Autenticação", totais_crm["auth"]),
        ("Oferta Apresentada", totais_crm["oferta"]),
        ("Acordo Gerado", totais_crm["acordo"]),
    ])


def calcular_funil_combinado_email_salesforce(kpis_email: dict, totais_crm: dict) -> list[dict]:
    """Funil combinado Envio + CRM do e-mail: continua o funil de engajamento (Envios
    -> Entregues -> Aberturas -> Cliques, do relatório do Salesforce Journey Builder)
    direto pro funil de negociação (Home -> Autenticação -> Oferta -> Acordo, do log de
    CRM das campanhas avulsas em ARQUIVOS PARA DISPAROS/). Diferente dos outros canais,
    os dois lados NÃO são cruzados por telefone — são fontes de e-mail diferentes (a
    Jornada do Salesforce roda separada das campanhas avulsas de e-mail), então essa
    visão é uma referência lado a lado do "volume de e-mail" com o "resultado de
    negociação do período", não um funil rigoroso onde cada etapa é subconjunto direto
    da anterior."""
    return _montar_funil([
        ("Envios", kpis_email["envios"]),
        ("Entregues", kpis_email["entregues"]),
        ("Aberturas", kpis_email["aberturas"]),
        ("Cliques", kpis_email["cliques"]),
        ("Home", totais_crm["home"]),
        ("Autenticação", totais_crm["auth"]),
        ("Oferta Apresentada", totais_crm["oferta"]),
        ("Acordo Gerado", totais_crm["acordo"]),
    ])


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


def _contagem_crm_por_texto(df_origem: pd.DataFrame, coluna_texto: str, df_crm: pd.DataFrame) -> pd.DataFrame:
    """Contagem de ações de CRM (home/auth/oferta/acordo) por texto-modelo (frase de
    SMS ou mensagem de WhatsApp/Airys/RCS), cruzando telefone com o log de CRM numa
    única junção + groupby vetorizados — evita repetir um `isin()` + `value_counts()`
    por linha de `base` (um `for _, linha in base.iterrows(): df_crm[...isin...]`),
    que fica caro com pandas quando chamado várias vezes por atualização do dashboard
    (frase de SMS + mensagem de WhatsApp Ótima/Airys/RCS, cada uma com sua própria
    tabela texto×grupo_ab e texto×grupo_estratégico)."""
    colunas = [coluna_texto, *ETAPAS_CRM]
    if df_crm.empty:
        return pd.DataFrame(columns=colunas)
    validas = df_origem[df_origem[coluna_texto] != ""]
    telefone_texto = validas[["telefone_norm", coluna_texto]].drop_duplicates()
    cruzado = df_crm[["telefone_norm", "acao_norm"]].merge(telefone_texto, on="telefone_norm", how="inner")
    if cruzado.empty:
        return pd.DataFrame(columns=colunas)
    contagem = cruzado.groupby([coluna_texto, "acao_norm"]).size().unstack(fill_value=0)
    for etapa in ETAPAS_CRM:
        if etapa not in contagem.columns:
            contagem[etapa] = 0
    return contagem[ETAPAS_CRM].reset_index()


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

    contagem = _contagem_crm_por_texto(df_sms, "frase_norm", df_crm)
    if contagem.empty:
        return base
    base = base.drop(columns=ETAPAS_CRM).merge(contagem, on="frase_norm", how="left")
    for etapa in ETAPAS_CRM:
        base[etapa] = base[etapa].fillna(0).astype(int)
    return base


def _montar_tabela_texto_com_grupo(
    base: pd.DataFrame, coluna_texto: str, df_origem: pd.DataFrame, df_crm: pd.DataFrame, coluna_grupo: str,
) -> list[dict]:
    """Monta a tabela Texto (frase/mensagem, subtotal) > Grupo AB/Grupo Estratégico
    (detalhe) do resultado de CRM (Home/Autenticação/Oferta/Acordo) — mostra o
    grupo_ab/grupo_estrategico por dentro de cada frase/mensagem, pra saber qual
    segmento converte melhor em cada texto (resultado qualitativo, não só a taxa de
    entrega). Reutilizado tanto pra frase de SMS quanto pra mensagem de WhatsApp."""
    if base.empty:
        return []

    ordem = GRUPO_AB_ORDEM if coluna_grupo == "grupo_ab" else GRUPO_ESTRATEGICO_ORDEM
    validas = df_origem[df_origem[coluna_texto] != ""]

    # Uma única junção telefone->CRM + groupby (em vez de um isin()/value_counts() por
    # combinação texto×grupo em loop) — ver docstring de `_contagem_crm_por_texto`.
    contagem_detalhe = pd.DataFrame(columns=[coluna_texto, coluna_grupo, *ETAPAS_CRM])
    if not df_crm.empty:
        telefone_textos = validas[["telefone_norm", coluna_texto, coluna_grupo]].drop_duplicates(
            ["telefone_norm", coluna_texto]
        )
        cruzado = df_crm[["telefone_norm", "acao_norm"]].merge(telefone_textos, on="telefone_norm", how="inner")
        if not cruzado.empty:
            agrupado = cruzado.groupby([coluna_texto, coluna_grupo, "acao_norm"]).size().unstack(fill_value=0)
            for etapa in ETAPAS_CRM:
                if etapa not in agrupado.columns:
                    agrupado[etapa] = 0
            contagem_detalhe = agrupado[ETAPAS_CRM].reset_index()

    linhas = []
    for _, linha in base.iterrows():
        texto = linha[coluna_texto]
        linhas.append({
            "rotulo": texto, "nivel": "subtotal",
            "home": int(linha["home"]), "auth": int(linha["auth"]),
            "oferta": int(linha["oferta"]), "acordo": int(linha["acordo"]),
        })

        sub = contagem_detalhe[contagem_detalhe[coluna_texto] == texto].set_index(coluna_grupo)
        for grupo in ordem:
            if grupo not in sub.index:
                continue
            linha_grupo = sub.loc[grupo]
            linhas.append({
                "rotulo": grupo, "nivel": "detalhe",
                "home": int(linha_grupo["home"]), "auth": int(linha_grupo["auth"]),
                "oferta": int(linha_grupo["oferta"]), "acordo": int(linha_grupo["acordo"]),
            })

    return linhas


def montar_tabela_frase_com_grupo(df_sms: pd.DataFrame, df_crm: pd.DataFrame, coluna_grupo: str) -> list[dict]:
    """Resultado de CRM por frase de SMS, com o grupo_ab/grupo_estrategico aninhado
    dentro de cada frase (coluna_grupo escolhe qual das duas dimensões)."""
    base = agregar_frase_com_crm(df_sms, df_crm)
    return _montar_tabela_texto_com_grupo(base, "frase_norm", df_sms, df_crm, coluna_grupo)


def montar_tabela_mensagem_com_grupo(df_whatsapp: pd.DataFrame, df_crm: pd.DataFrame, coluna_grupo: str) -> list[dict]:
    """Resultado de CRM por mensagem de WhatsApp, com o grupo_ab/grupo_estrategico
    aninhado dentro de cada mensagem (coluna_grupo escolhe qual das duas dimensões)."""
    base = agregar_mensagem_whatsapp_com_crm(df_whatsapp, df_crm)
    return _montar_tabela_texto_com_grupo(base, "mensagem_norm", df_whatsapp, df_crm, coluna_grupo)


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
    subtotal_anterior = None
    total_por_grupo_anterior: dict = {}

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
        linha_subtotal["percentual"] = (
            100.0 if subtotal_anterior is None else taxa(subtotal_geral, subtotal_anterior)
        )
        total_geral += subtotal_geral
        linhas.append(linha_subtotal)

        total_por_grupo_atual: dict = {}
        for grupo in sorted(pivot.index, key=ordem_grupo):
            linha = {"rotulo": grupo, "nivel": "detalhe"}
            total_linha = 0
            for u in utms_presentes:
                valor = int(pivot.loc[grupo, u])
                linha[u] = valor
                total_linha += valor
            linha["Total Geral"] = total_linha
            base_grupo = total_por_grupo_anterior.get(grupo)
            linha["percentual"] = 100.0 if base_grupo is None else taxa(total_linha, base_grupo)
            total_por_grupo_atual[grupo] = total_linha
            linhas.append(linha)

        subtotal_anterior = subtotal_geral
        total_por_grupo_anterior = total_por_grupo_atual

    linha_total_geral = {"rotulo": "Total Geral", "nivel": "total_geral"}
    for u in utms_presentes:
        linha_total_geral[u] = totais_coluna[u]
    linha_total_geral["Total Geral"] = total_geral
    linha_total_geral["percentual"] = None
    linhas.append(linha_total_geral)

    return utms_presentes, linhas


def extremos_data_hora(*dfs: pd.DataFrame) -> tuple:
    """Data mínima/máxima entre um ou mais dataframes de eventos (ex.: SMS + retorno de
    WhatsApp), usada como intervalo padrão do filtro de Período — pra o período inicial
    já cobrir todos os canais, não só o SMS/Kolmeya."""
    datas = [df.dropna(subset=["timestamp"])["data"] for df in dfs if not df.empty]
    todas = pd.concat(datas, ignore_index=True) if datas else pd.Series(dtype="object")
    if todas.empty:
        hoje = pd.Timestamp.now().date()
        return hoje, hoje, 0, 23
    return todas.min(), todas.max(), 0, 23


# ---------------------------------------------------------------------------
# Custos de disparo
# ---------------------------------------------------------------------------
# Regra de cobrança por (canal, fornecedor) — só os que têm valor confirmado pelo
# negócio. Ausente do dict = custo não informado (ex.: WhatsApp Airys, Email/
# Salesforce, que roda sobre um saldo pré-pago em vez de custo por envio) — nesse
# caso NÃO se estima nem se inventa um valor, fica marcado como tal na tela.
# `base` escolhe qual quantidade é tarifada — cada fornecedor cobra por uma etapa
# diferente do funil, não sempre "enviado":
#   - "enviado": Kolmeya (SMS) e Ótima (SMS, hoje sem volume real).
#   - "disparado": Ótima (RCS) — cobra pela tentativa de disparo, não pelo envio
#     confirmado.
#   - "entregue": Ótima (WhatsApp) — só cobra o que foi de fato entregue.
CUSTO_CONFIG_POR_CANAL_FORNECEDOR = {
    ("sms", "kolmeya"): {"custo_unitario": 0.0620, "base": "enviado"},
    ("sms", "otima"): {"custo_unitario": 0.0500, "base": "enviado"},
    ("rcs", "otima"): {"custo_unitario": 0.0900, "base": "disparado"},
    ("whatsapp", "otima"): {"custo_unitario": 0.0685, "base": "entregue"},
    ("whatsapp", "airys"): {"custo_unitario": 0.0500, "base": "entregue"},
}

CANAL_CUSTO_LABEL = {"sms": "SMS", "rcs": "RCS", "whatsapp": "WhatsApp", "email": "Email"}
FORNECEDOR_CUSTO_LABEL = {
    "kolmeya": "Kolmeya", "otima": "Ótima", "airys": "Airys", "salesforce": "Salesforce",
}
BASE_COBRANCA_LABEL = {"disparado": "Disparado", "enviado": "Enviado", "entregue": "Entregue"}


def _linhas_custo_por_dia_evento(df: pd.DataFrame, canal: str) -> list[dict]:
    """Quantidade por dia e fornecedor, a partir de um df já filtrado e restrito a um
    canal com as flags 0/1 `disparado`/`enviado`/`entregue` (SMS/RCS, formato estilo
    SMS) — soma as três, e cada linha escolhe qual delas usar conforme a regra de
    cobrança do fornecedor (`CUSTO_CONFIG_POR_CANAL_FORNECEDOR`)."""
    if df.empty:
        return []
    d = df.copy()
    d["fornecedor"] = d["utm_campaign"].apply(fornecedor_da_campanha)
    agrupado = d.groupby(["data", "fornecedor"])[["disparado", "enviado", "entregue"]].sum()
    linhas = []
    for (data, fornecedor), linha in agrupado.iterrows():
        linhas.append(_montar_linha_custo(data, canal, fornecedor, linha))
    return [l for l in linhas if l]


def _linhas_custo_por_dia_status(df: pd.DataFrame, canal: str, fornecedor: str) -> list[dict]:
    """Igual `_linhas_custo_por_dia_evento`, mas pro formato de retorno com granularidade
    por destinatário (WhatsApp/Airys) — "enviado" é qualquer status diferente de "Não
    Enviado", "entregue" é Entregue+Lido (mesma regra usada em `calcular_funil_whatsapp`
    e no cálculo de "Home vs Lido"). Esses dataframes não têm coluna `utm_campaign` (só
    "campanha"/"campaign_titulo" no formato bruto do retorno), então o fornecedor vem
    fixo por chamada — cada df já é de um fornecedor só (whatsapp_completo é só Ótima,
    airys_completo é só Airys)."""
    if df.empty:
        return []
    d = df.copy()
    d["enviado"] = (d["situacao_norm"] != "Nao Enviado").astype(int)
    d["entregue"] = d["situacao_norm"].isin(["Entregue", "Lido"]).astype(int)
    d["disparado"] = 1
    agrupado = d.groupby("data")[["disparado", "enviado", "entregue"]].sum()
    linhas = [_montar_linha_custo(data, canal, fornecedor, linha) for data, linha in agrupado.iterrows()]
    return [l for l in linhas if l]


def _montar_linha_custo(data, canal: str, fornecedor: str, quantidades) -> dict | None:
    config = CUSTO_CONFIG_POR_CANAL_FORNECEDOR.get((canal, fornecedor))
    base = config["base"] if config else "enviado"
    quantidade = int(quantidades[base])
    if quantidade <= 0:
        return None
    custo_unitario = config["custo_unitario"] if config else None
    return {
        "data": data, "canal": canal, "fornecedor": fornecedor, "base_cobranca": base,
        "quantidade": quantidade, "custo_unitario": custo_unitario,
        "custo_total": (quantidade * custo_unitario) if custo_unitario is not None else None,
    }


def calcular_custos_disparo(
    df_sms: pd.DataFrame, df_rcs: pd.DataFrame, df_whatsapp_otima: pd.DataFrame,
    df_whatsapp_airys: pd.DataFrame, envios_email: int,
) -> list[dict]:
    """Monta a tabela de custo por dia/canal/fornecedor — CUSTO = quantidade tarifada ×
    custo unitário do fornecedor. A quantidade tarifada depende da regra de cobrança de
    cada fornecedor (`CUSTO_CONFIG_POR_CANAL_FORNECEDOR`: Kolmeya cobra por enviado,
    Ótima RCS por disparado, Ótima WhatsApp por entregue) — nunca lido, respondido,
    clique ou acordo. Cada df já deve vir filtrado pelos filtros globais do dashboard.
    O e-mail (Salesforce) entra como uma única linha sem data, já que o relatório não
    tem granularidade por dia/destinatário — ver `carregar_dados_email_salesforce`."""
    linhas = []
    linhas += _linhas_custo_por_dia_evento(df_sms, "sms")
    linhas += _linhas_custo_por_dia_evento(df_rcs, "rcs")
    linhas += _linhas_custo_por_dia_status(df_whatsapp_otima, "whatsapp", "otima")
    linhas += _linhas_custo_por_dia_status(df_whatsapp_airys, "whatsapp", "airys")
    if envios_email:
        linhas.append({
            "data": None, "canal": "email", "fornecedor": "salesforce", "base_cobranca": "enviado",
            "quantidade": int(envios_email), "custo_unitario": None, "custo_total": None,
        })
    linhas.sort(key=lambda l: (l["data"] is None, l["data"], l["canal"], l["fornecedor"]))
    return linhas


def calcular_custo_total_por_canal(linhas_custo: list[dict]) -> dict:
    """Soma o custo total (só linhas com custo unitário definido) por canal."""
    totais = {}
    for linha in linhas_custo:
        if linha["custo_total"] is None:
            continue
        totais[linha["canal"]] = totais.get(linha["canal"], 0.0) + linha["custo_total"]
    return totais


# ---------------------------------------------------------------------------
# Jornada de Cobrança
# ---------------------------------------------------------------------------
# Calendário de Estratégia — substitui o Diário e a Jornada de Cobrança antigos.
# Cada dia do mês mostra as campanhas de fato disparadas naquela data (derivadas
# direto de ARQUIVOS PARA DISPAROS/, mesma fonte de verdade do resto do app — nunca
# reescritas à mão) + uma anotação livre editável, persistida em
# ANOTACOES_CALENDARIO.json (chave = data ISO "AAAA-MM-DD").
_PADRAO_DATA_UTM = re.compile(r"^(\d{4})(\d{2})(\d{2})")


def resumo_campanhas_por_dia() -> dict[str, list[dict]]:
    """Agrupa toda campanha descoberta em ARQUIVOS PARA DISPAROS/ pela data embutida no
    nome do arquivo (`^(\\d{4})(\\d{2})(\\d{2})`, mesmo padrão usado nos decks .pptx —
    ver CLAUDE.md) — não pelo campo `data` do retorno, que fica NaT pra campanha ainda
    sem retorno casado. Canal/fornecedor vêm de `canal_da_campanha`/`fornecedor_da_campanha`;
    volume e Grupo Estratégico predominante vêm do próprio disparo (`carregar_dados_sms`,
    a fonte de verdade de composição por grupo — nunca um cross-tab de retorno/CRM)."""
    campanhas = descobrir_campanhas()
    if not campanhas:
        return {}
    df = carregar_dados_sms()

    resultado: dict[str, list[dict]] = {}
    for utm in campanhas:
        m = _PADRAO_DATA_UTM.match(utm)
        if not m:
            continue
        data_iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        sub = df[df["utm_campaign"] == utm] if not df.empty else df
        volume = len(sub)
        grupo = NAO_CLASSIFICADO
        frase = None
        if volume:
            contagem_grupo = sub["grupo_estrategico"].value_counts()
            if not contagem_grupo.empty:
                grupo = contagem_grupo.index[0]
            if "frase" in sub.columns:
                validas = sub["frase"].dropna()
                validas = validas[validas.astype(str).str.strip() != ""]
                if not validas.empty:
                    frase = validas.iloc[0]
        resultado.setdefault(data_iso, []).append({
            "utm": utm,
            "canal": CANAL_CUSTO_LABEL.get(canal_da_campanha(utm), "Desconhecido"),
            "fornecedor": FORNECEDOR_CUSTO_LABEL.get(fornecedor_da_campanha(utm), fornecedor_da_campanha(utm)),
            "grupo_estrategico": grupo,
            "volume": volume,
            "frase": frase,
        })

    for lista in resultado.values():
        lista.sort(key=lambda c: c["utm"])
    return resultado


def carregar_anotacoes_calendario() -> dict[str, str]:
    """Anotações livres por dia do Calendário de Estratégia (chave = data ISO), lidas
    de ANOTACOES_CALENDARIO.json. Arquivo ainda não existente = sem anotações."""
    if not _ARQUIVO_ANOTACOES_CALENDARIO.exists():
        return {}
    try:
        return json.loads(_ARQUIVO_ANOTACOES_CALENDARIO.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def salvar_anotacoes_calendario(anotacoes: dict[str, str]) -> None:
    """Mescla `anotacoes` (data ISO -> texto) nas já salvas e grava de volta em
    ANOTACOES_CALENDARIO.json — mescla em vez de sobrescrever pra não apagar
    anotações de outros meses que não estavam na tela no momento de salvar."""
    atuais = carregar_anotacoes_calendario()
    atuais.update(anotacoes)
    atuais = {data: texto for data, texto in atuais.items() if (texto or "").strip()}
    _ARQUIVO_ANOTACOES_CALENDARIO.parent.mkdir(parents=True, exist_ok=True)
    _ARQUIVO_ANOTACOES_CALENDARIO.write_text(
        json.dumps(atuais, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8",
    )
