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
- `ARQUIVOS PARA DISPAROS/`, `ARQUIVOS DE RETORNO/`, `ARQUIVOS DE RETORNO WHATSAPP/`,
  `ARQUIVOS LOG/`, `ARQUIVO DA BASE INTEIRA/` — pastas de dados na raiz do projeto (ao
  lado de `app.py`), descritas abaixo.
- `ANOTACOES_CALENDARIO.json` — anotações livres por dia, editáveis direto na aba
  "Calendário de Estratégia" do dashboard (botão "Salvar Anotações" grava aqui). Cada
  dia do calendário também mostra automaticamente as campanhas de fato disparadas
  naquela data (Grupo Estratégico, volume, canal e fornecedor), sem precisar editar
  nada — vem direto de `ARQUIVOS PARA DISPAROS/`.

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

### `ARQUIVOS DE RETORNO WHATSAPP/`
Relatório de entrega do WhatsApp (Otima/Airys), com colunas `Destino` (telefone),
`Mensagem` e `Situação` (Entregue/Lido/Enviado/Não Entregue/Não Enviado) por
destinatário. Todo `.csv` desta pasta é lido e concatenado, deduplicado pelo
`Identificador` (UUID único por envio). Diferente do retorno da Kolmeya, o vínculo com a
campanha não é por job — é por telefone: ao selecionar uma campanha no filtro "Campanha
(UTM)" da aba **Funil Geral**, os cartões "WHATSAPP" (Entregue/Lido/Enviado/Não
Entregue/Não Enviado, logo abaixo dos cartões "SMS") já trazem o resultado de quem
recebeu aquela campanha — só quando a UTM selecionada é de fato uma campanha de
WhatsApp (sufixo `-otima`/`-airys` no nome do arquivo; ver `canal_da_campanha` em
`data_processing.py`), pra não misturar com telefones de campanhas de outro canal que
por acaso se repitam na base. O cruzamento de telefone usa a coluna `SMS_WHATS` do
arquivo de disparo (com DDI, específica do envio de WhatsApp/SMS) contra o `Destino` do
retorno — não a coluna `telefone` genérica — já que `SMS_WHATS` é a que de fato
identifica o número usado no disparo (ver `telefones_das_campanhas`); no arquivo da
Otima as duas colunas trazem o mesmo número, mas o código usa a coluna certa mesmo
assim, caso um arquivo futuro traga números diferentes entre elas. Cada envio tem a
saudação personalizada com o primeiro
nome do cliente (ex.: "Oi, FABIANA!"), então na seção "Resultado por Mensagem
(WhatsApp)" da aba "Conversão Pós-Contato (CRM)" — visível exclusivamente na sub-aba
Pós-WhatsApp — as mensagens são agrupadas pelo texto-modelo (sem o nome), mesmo
princípio do "Resultado por Frase (SMS)", e cruzadas por telefone com o log de CRM para
mostrar o resultado final (Home/Autenticação/Oferta/Acordo) de quem recebeu cada
mensagem.

### `ARQUIVOS LOG/`
Log(s) de CRM (negociação: home/auth/oferta/acordo), usado só na aba auxiliar "Conversão
Pós-Contato" — não participa do funil de envio/entrega. Todo `.csv` desta pasta é lido e
concatenado (dá pra ir empilhando um export por dia), deduplicado por uma chave composta
(doc + campanha + ação + data) já que exports diferentes podem ter esquema de colunas
diferente. A aba é **restrita às campanhas cadastradas em `ARQUIVOS PARA DISPAROS/`**
(o log em si traz dezenas de outras campanhas de teste/outras operações, que ficam de
fora) e tem 3 sub-abas fixas — Pós-SMS / Pós-WhatsApp / Pós-Email — definidas pela coluna
`Utm Medium` de cada linha do log.

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

Na aba **Funil Geral**, abaixo do funil de SMS tem o **Funil de WhatsApp** (Disparado →
Enviado → Entregue → Lido), montado a partir da contagem de status finais do retorno
Otima/Airys: Enviado exclui quem falhou antes de sair (Não Enviado), e Entregue soma quem
só foi entregue com quem já leu (Lido é um estágio mais avançado de Entregue). Segue a
mesma campanha selecionada no filtro "Campanha (UTM)" — ver `canal_da_campanha` acima.

Logo abaixo da "Tabela Executiva por Campanha" (SMS) tem a **Tabela Executiva de
WhatsApp por Campanha**, com o mesmo detalhamento (Entregue (não lido)/Lido/
Pendente/Não Entregue/Não Enviado) por campanha de WhatsApp — só lista campanhas com
retorno já recebido (uma campanha de WhatsApp sem arquivo em `ARQUIVOS DE RETORNO
WHATSAPP/` ainda não aparece aqui, em vez de mostrar uma linha zerada enganosa).

## Segmentação por Grupo AB e Grupo Estratégico

`ARQUIVO DA BASE INTEIRA/` tem a base de clientes (uma linha por CPF, com colunas
`FONE_1`..`FONE_4`, `grupo_ab` e `grupo_estrategico`). Como os arquivos de SMS só têm
telefone (não têm CPF), o cruzamento é feito por telefone: as colunas `FONE_1`..`FONE_4`
são explodidas em formato longo e viram mapas `telefone -> grupo_ab` e
`telefone -> grupo_estrategico` (equivalente ao PROCX/VLOOKUP manual "doc por doc"),
aplicados depois a cada evento de SMS e a cada linha do log de CRM. Quando o próprio
arquivo de disparo já traz uma dessas colunas (caso de Airys/Otima/Salesforce), o valor do
arquivo tem prioridade sobre o cruzamento. Telefones não encontrados em nenhum dos dois
viram `Não Classificado`.

- **Grupo AB** (`P1_MAXIMA`..`P4_BAIXA`) — segmentação de propensão. Filtro global "Grupo
  AB", aba "Funil por Grupo AB" e coluna na tabela dinâmica de Conversão Pós-Contato.
- **Grupo Estratégico** (`2_ABANDONO_CARRINHO`, `3_CADASTRADO`, `4_ENGAJADO`,
  `5_TOPO_FUNIL`) — categorização de funil do cliente na base, independente de qual
  campanha/UTM ele recebeu. Filtro global "Grupo Estratégico" e aba própria "Funil por
  Grupo Estratégico".

Nas duas abas, abaixo do bloco de SMS tem também o **Resultado de WhatsApp** por
grupo_ab/grupo_estrategico (Entregue/Lido/Enviado/Não Entregue/Não Enviado), na mesma
lógica de vínculo por telefone usada no Funil de WhatsApp da aba Funil Geral — aparece
ao selecionar uma campanha de WhatsApp no filtro "Campanha (UTM)".

## Resultado por Frase (SMS)

Cada SMS enviado tem um link único por cliente (ex.: `.../8knbP2`), então agrupar pelo
texto bruto criaria um grupo por linha. A aba "Resultado por Frase (SMS)" substitui o link
por um marcador fixo (`{link}`) antes de agrupar, comparando o desempenho de cada
texto-modelo de mensagem — mesmo que ele seja reutilizado em campanhas diferentes. Só
considera campanhas cujo arquivo de disparo tem a frase (`ARQUIVOS PARA DISPAROS/{utm}.csv`
com coluna `frase`), ou seja, hoje é específico do canal SMS/Kolmeya.

Tanto essa tabela quanto a de "Resultado por Mensagem (WhatsApp)" têm duas tabelas
extras logo abaixo — "Resultado por Frase/Mensagem × Grupo AB" e "× Grupo Estratégico"
— com o grupo_ab/grupo_estrategico aninhado dentro de cada frase/mensagem (mesmo
padrão de subtotal + detalhe usado no Funil por Grupo Estratégico), pra deixar o
resultado qualitativo: mostra não só a taxa de entrega, mas qual segmento de cliente
converteu melhor (Home/Autenticação/Oferta/Acordo) em cada texto.

## Funil de Conversão combinado (aba CRM)

O gráfico "Funil de Conversão" na aba "Conversão Pós-Contato (CRM)" (sub-abas Pós-SMS e
Pós-WhatsApp) é ponta a ponta: continua o funil de entrega (Disparado → Enviado →
Entregue, e no WhatsApp também Lido) direto no funil de negociação (Home →
Autenticação → Oferta → Acordo), na campanha selecionada no filtro "Campanha (UTM) —
CRM" da própria aba (não no filtro global do Funil Geral). Como a base de disparo é
sempre muito maior que quem de fato negocia, as etapas de CRM aparecem como barras bem
finas — os números ficam escritos do lado de fora de cada barra pra não ficarem
ilegíveis. A sub-aba Pós-Email mantém o funil só de CRM (sem etapas de entrega), já que
não há arquivo de retorno para esse canal ainda.
