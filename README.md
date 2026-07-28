# Dashboard Executivo de Funil SMS — Casas Bahia

Dashboard executivo em Dash + Plotly para acompanhar a jornada de SMS
(Disparado → Enviado → Entregue → Falhou) das campanhas Kolmeya/Otima da operação Casas Bahia.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

O navegador abre automaticamente em `http://127.0.0.1:8051/`.

## Estrutura

- `app.py` — ponto de entrada (monta o app Dash e sobe o servidor).
- `data_processing.py` — carga, limpeza e padronização dos CSVs; cálculo de KPIs/funil/agregações.
- `charts.py` — construção dos gráficos Plotly (tema escuro).
- `layout.py` — layout Dash/Bootstrap (filtros, cards de KPI, abas, tabela).
- `callbacks.py` — callback que liga os filtros a todos os componentes.
- `utils.py` — parsing de datas em português, normalização de telefone, formatação.
- `ARQUIVOS PARA DISPAROS/`, `ARQUIVOS DE RETORNO/`, `ARQUIVOS LOG/`, `ARQUIVO DA BASE INTEIRA/`
  — pastas de dados na raiz do projeto (ao lado de `app.py`), descritas abaixo.

## Rotina de atualização diária

1. Copie os arquivos novos do dia para dentro das pastas correspondentes (na raiz do
   projeto, ex.: `C:\Users\diego.souza\FUNIL LABORATORIO\dashboardcasasbahia\ARQUIVOS PARA DISPAROS\`).
   Não precisa apagar os arquivos de dias anteriores — o histórico acumula sozinho.
2. Se o dashboard já estiver rodando, feche com `Ctrl+C` no terminal.
3. Rode `python app.py` de novo. O navegador abre sozinho já com os dados atualizados.

Nenhum passo exige editar código — campanhas novas, retornos novos e atualização da base
de grupo_ab são todos descobertos automaticamente pelas 4 pastas abaixo.

### `ARQUIVOS PARA DISPAROS/`
Um arquivo por campanha = base enviada à plataforma = **Disparado**. O nome do arquivo
(sem `.csv`) **é** a UTM da campanha — ex.: `20260728-abandonocarrinhodia28-kolmeya.csv`.
Toda campanha nova aparece sozinha no filtro "Campanha (UTM)" assim que o arquivo é
colocado aqui, para qualquer canal:

- **SMS/WhatsApp** (Kolmeya, Airys, Otima): identificador é a coluna `telefone`.
- **E-mail** (Salesforce): identificador é a coluna `email` (não precisa de `telefone`).

Se o arquivo já trouxer uma coluna `grupo_ab` (caso de Airys/Otima/Salesforce), ela é
usada diretamente em vez de recalcular pelo cruzamento de telefone com
`ARQUIVO DA BASE INTEIRA/`.

### `ARQUIVOS DE RETORNO/`
Retorno da Kolmeya ou outro canal por **telefone** (job;phone;status;mensagem;criacao) =
confirmação de **Enviado/Entregue/Falhou**. Esses arquivos vêm nomeados por número de job
(`export-full_...`), não pela UTM — por isso o app **liga cada retorno à campanha
automaticamente**, comparando os telefones do retorno com os telefones de cada arquivo de
`ARQUIVOS PARA DISPAROS/` e escolhendo a campanha com maior sobreposição (≥ 80%). Não
precisa renomear nada, só soltar o arquivo original aqui. Se o disparo de hoje ainda não
tiver retorno (resultado ainda não voltou), a campanha aparece com tudo em "Não
Processado" até o arquivo de retorno chegar — isso vale também para campanhas de
WhatsApp/e-mail cujo retorno ainda não foi enviado (o vínculo automático hoje só cobre
retorno por telefone; retorno por e-mail ainda não é suportado).

### `ARQUIVOS LOG/`
Log(s) de CRM (negociação: home/auth/oferta/acordo), usado só na aba auxiliar "Conversão
Pós-SMS" — não participa do funil de envio/entrega. Todo `.csv` desta pasta é lido e
concatenado (dá pra ir empilhando um export por dia), deduplicado por uma chave composta
(doc + campanha + ação + data) já que exports diferentes podem ter esquema de colunas
diferente. **Essa aba não fica restrita às 4 campanhas de SMS**: mostra todas as
campanhas/canais que aparecerem no log (SMS, WhatsApp, e-mail — Kolmeya, Otima, Airys,
Salesforce etc.), com filtro próprio de UTM e de Canal (coluna `Utm Medium`).

### `ARQUIVO DA BASE INTEIRA/`
Base de clientes usada no cruzamento do grupo_ab (qualquer nome de arquivo `.csv`). É
tratada como **snapshot**: se colocar uma versão nova, pode deixar a antiga ali também —
a deduplicação por `CPF` é automática (mantendo a linha mais recente), então não precisa
apagar nada manualmente.

## Modelo do funil

Todo telefone de um arquivo de retorno existe na base de disparo correspondente (validado,
sem duplicatas). **Enviado** = qualquer telefone com status retornado pela operadora;
dentro dele, **Entregue** (`status=entregue`) e **Falhou** (`status=nao entregue`) são
subconjuntos, e `status=enviado` (ainda em trânsito) conta como Enviado mas não é exibido
como uma etapa própria do funil. O histórico **acumula**: campanhas de dias diferentes
convivem lado a lado, e o filtro de Data/Hora serve para comparar ou isolar cada dia.

Não há coluna de operadora (Claro/Vivo/TIM/Oi) em nenhum arquivo, então essa seção não foi
incluída no dashboard.

## Segmentação por Grupo AB

`ARQUIVO DA BASE INTEIRA/` tem a base de clientes (uma linha por CPF, com colunas
`FONE_1`..`FONE_4` e `grupo_ab`). Como os arquivos de SMS só têm telefone (não têm CPF), o
cruzamento é feito por telefone: as colunas `FONE_1`..`FONE_4` são explodidas em formato
longo e viram um mapa `telefone -> grupo_ab` (equivalente ao PROCX/VLOOKUP manual "doc por
doc"), aplicado depois a cada evento de SMS e a cada linha do log de CRM. Telefones que não
aparecem na base viram `Não Classificado`. Isso alimenta o filtro global "Grupo AB", a aba
"Funil por Grupo AB" (volume, taxa de entrega e tabela executiva por `P1_MAXIMA`,
`P2_ALTA`, `P3_MEDIA`, `P4_BAIXA`) e a tabela dinâmica Ação × Campanha × Grupo AB na aba de
Conversão Pós-SMS.
