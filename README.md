# Dashboard Executivo de Funil SMS — Casas Bahia

Dashboard executivo em Dash + Plotly para acompanhar a jornada de SMS
(Disparado → Enviado → Entregue → Falhou) das campanhas Kolmeya da operação Casas Bahia.

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
- `data/raw/` — CSVs de origem (base de disparo e log de resultado por campanha, + log de CRM).

## Atualização diária — onde colocar os arquivos novos

Todos os arquivos ficam em `data/raw/`. As campanhas em escopo são **descobertas
automaticamente**: não precisa editar nenhum código, nem trocar nada em `data_processing.py`.

Para cada campanha/dia novo, coloque o par de arquivos com o nome da UTM exata:

- `data/raw/{utm}_disparo.csv` — base enviada à plataforma Kolmeya (telefone;FRASE) = **Disparado**.
- `data/raw/{utm}_log.csv` — log de resultado da Kolmeya (job;phone;status;mensagem;criacao) = **Enviado/Entregue/Falhou**.

Ex.: para a campanha de amanhã `20260728-abandonocarrinhodia28-kolmeya`, os arquivos
seriam `20260728-abandonocarrinhodia28-kolmeya_disparo.csv` e
`20260728-abandonocarrinhodia28-kolmeya_log.csv`. Toda UTM que tiver esse par completo em
`data/raw/` aparece automaticamente no filtro "Campanha (UTM)" e em todos os gráficos —
o histórico **acumula** (dias antigos não somem, o filtro de Data/Hora que já existe serve
para comparar/isolar cada dia).

Os outros dois arquivos são **snapshots que se sobrescrevem** (sempre o mais recente):

- `data/raw/base_segmentacao_grupo_ab.csv` — substitua pela versão mais nova da base de
  clientes (usada no cruzamento do grupo_ab).
- `data/raw/LOG_CB_LABORATORIO_crm.csv` — substitua pelo log de CRM mais recente.

> Depois de copiar os arquivos, reinicie o app (`python app.py`) para ele reprocessar tudo.
> Se "arquivos enviados" que você mencionou for um 3º arquivo diferente do log de
> resultado (job;phone;status;mensagem;criacao), me manda um exemplo que eu incluo esse
> cruzamento também — hoje o pipeline só reconhece esses dois arquivos por campanha.

## Fontes de dados e escopo (exemplo do primeiro carregamento)

Cada campanha tem um par de arquivos em `data/raw/`:

- `{utm}_disparo.csv` — base enviada à plataforma Kolmeya (telefone;FRASE) = **Disparado**.
- `{utm}_log.csv` — log de resultado da Kolmeya (job;phone;status;mensagem;criacao).

Modelo do funil: todo telefone do log de resultado existe na base de disparo (validado,
sem duplicatas). **Enviado** = qualquer telefone com status retornado pela operadora;
dentro dele, **Entregue** (`status=entregue`) e **Falhou** (`status=nao entregue`) são
subconjuntos, e `status=enviado` (ainda em trânsito) conta como Enviado mas não é
exibido como uma etapa própria do funil.

A campanha `20260727-CBtopofunildia27-salesforce` foi removida do escopo por não ter
arquivo de disparo/log enviado. `LOG_CB_LABORATORIO_crm.csv` é um log de CRM (não é log
de SMS) usado só na aba auxiliar "Conversão Pós-SMS", com o funil Home → Autenticação →
Oferta → Acordo. Não há coluna de operadora (Claro/Vivo/TIM/Oi) em nenhum arquivo, então
essa seção não foi incluída.

## Segmentação por Grupo AB

`data/raw/base_segmentacao_grupo_ab.csv` é a base de clientes (uma linha por CPF, com
colunas `FONE_1`..`FONE_4` e `grupo_ab`). Como os logs de SMS só têm telefone (não têm
CPF), o cruzamento é feito por telefone: as colunas `FONE_1`..`FONE_4` são explodidas em
formato longo e viram um mapa `telefone -> grupo_ab` (equivalente ao PROCX/VLOOKUP manual
"doc por doc"), aplicado depois a cada evento de SMS. Telefones que não aparecem na base
viram `Não Classificado`. Isso alimenta o filtro global "Grupo AB" e a aba "Funil por
Grupo AB" (volume, taxa de entrega e tabela executiva por `P1_MAXIMA`, `P2_ALTA`,
`P3_MEDIA`, `P4_BAIXA`).
