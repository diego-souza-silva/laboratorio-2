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

## Fontes de dados e escopo

Apenas as 4 campanhas Kolmeya abaixo entram no funil de SMS:

- `20260725-abandonocarrinhodia25-kolmeya`
- `20260725-engajadodia25-kolmeya`
- `20260725-topofunildia25-kolmeya`
- `20260725-cadastradodia25-kolmeya`

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
