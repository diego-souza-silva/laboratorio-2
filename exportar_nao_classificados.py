"""Exporta os clientes 'Não Classificado' (grupo_ab) de todos os canais, com o motivo.
Rodar de dentro da raiz do projeto: python3 exportar_nao_classificados.py
"""
import pandas as pd
import data_processing as dp
from utils import normalizar_telefone

NAO = dp.NAO_CLASSIFICADO

base = dp._carregar_base_segmentacao()
colunas_fone = [c for c in base.columns if c.startswith("fone_")]
todos_tel = set()
for c in colunas_fone:
    todos_tel |= set(base[c].apply(normalizar_telefone))
todos_tel.discard("")


def motivo(tel: str) -> str:
    if not tel:
        return "Telefone inválido/vazio após normalização"
    if tel not in todos_tel:
        return "Telefone não encontrado na base de clientes (ARQUIVO DA BASE INTEIRA)"
    return "Telefone está na base, mas sem grupo_ab/grupo_estrategico preenchido na linha"


UTMS_SMS = [u for u in dp.CAMPANHAS_ESCOPO if dp.canal_da_campanha(u) == "sms"]

df_sms = dp.carregar_dados_sms()
df_sms = df_sms[df_sms["utm_campaign"].isin(UTMS_SMS)]
df_rcs = dp.carregar_dados_rcs_estilo_sms()
df_wpp = dp.carregar_dados_whatsapp_mensagem()
df_airys = dp.carregar_dados_airys()

registros = []
fontes = [
    ("SMS", "Kolmeya", df_sms, "utm_campaign"),
    ("RCS", "Ótima", df_rcs, "utm_campaign"),
    ("WhatsApp", "Ótima", df_wpp, "campanha"),
    ("WhatsApp", "Airys", df_airys, "campanha"),
]
for canal, fornecedor, df, coluna_campanha in fontes:
    nc = df[df["grupo_ab"] == NAO].copy()
    if nc.empty:
        continue
    coluna_campanha_real = coluna_campanha if coluna_campanha in nc.columns else None
    for tel, grupo in nc.groupby("telefone_norm"):
        campanhas = sorted(grupo[coluna_campanha_real].dropna().unique().tolist()) if coluna_campanha_real else []
        registros.append({
            "telefone": tel,
            "canal": canal,
            "fornecedor": fornecedor,
            "campanha(s)": "; ".join(campanhas),
            "qtd_disparos": len(grupo),
            "motivo": motivo(tel),
        })

df_final = pd.DataFrame(registros).sort_values(["canal", "fornecedor", "telefone"]).reset_index(drop=True)
df_final.to_csv("nao_classificados.csv", index=False, sep=";", encoding="utf-8-sig")
print(f"{len(df_final)} linhas ({df_final['telefone'].nunique()} telefones únicos) salvas em nao_classificados.csv")
print(df_final["motivo"].value_counts())
