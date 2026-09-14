# CLAUDE.md

Contexto para sessões futuras do Claude Code neste repositório. Para o dashboard
em si (como rodar, estrutura de pastas de dados, rotina diária), ver `README.md`
— este arquivo cobre o que não está lá: o sistema de apresentações `.pptx` e as
decisões/armadilhas de metodologia de dados descobertas ao longo do projeto.

## Sistema de apresentações (`apresentacoes/`)

Scripts Node.js (pptxgenjs) que geram decks `.pptx` de resultados por canal a
partir dos mesmos dados que o dashboard usa (`data_processing.py`, via
`python3 -c "import data_processing as dp; ..."` para extrair os números antes
de hard-codar nos scripts — **os scripts não importam Python em tempo de
execução**, os valores são calculados uma vez e escritos como literais no JS).

### Como rodar

```bash
cd apresentacoes
npm install          # instala pptxgenjs, react, react-dom, react-icons, sharp
node build_sms.js            # gera casas_bahia_sms.pptx (23 slides)
node build_whatsapp.js       # gera casas_bahia_whatsapp.pptx (10 slides)
node build_rcs.js            # gera casas_bahia_rcs.pptx (8 slides)
node build_email.js          # gera casas_bahia_email.pptx (7 slides)
node build_consolidado.js    # gera casas_bahia_consolidado.pptx (10 slides)
node build_fraseologia_sms.js
node build_fraseologia_whatsapp.js
node build_fraseologia_rcs.js
node build_fraseologia_email.js
```

Os `.pptx` gerados **não são versionados** (`.gitignore`) — são entregues ao
usuário via `SendUserFile` a cada rodada e regenerados sob demanda. Para
validar visualmente depois de gerar, use a skill `pptx` deste projeto
(`validate.py` + `soffice.py --convert-to pdf` + `pdftoppm` + `Read` de cada
slide) — é assim que todo overflow de tabela/card foi pego durante o
desenvolvimento.

### Arquitetura

- **`lib.js`** — paleta de cores e componentes reutilizáveis entre decks:
  `newPres`, `statCard`, `makeFooter` (rodapé parametrizado por canal),
  `slideCapa`, `tabelaDinamica` (mini-pivot 3 colunas: label/Clientes/%),
  `makeSlidePrioridadeGrupoEstrategico` (duas `tabelaDinamica` lado a lado),
  `makeSlideFunilCompleto` (funil em barras, N etapas dinâmicas),
  `makeSlideFunilSegmentado` (tabela funil × Prioridade/Grupo Estratégico,
  células de duas linhas via `celulaEtapa`), `slideInvestimentoTotal` (tabela
  de custo por canal + Lemit), `makeSlideTabelaFrases` (pivot Frase/Mensagem ×
  grupo, usado nos decks de fraseologia).
- **`build_sms.js`** — o único standalone (não usa `lib.js`; define suas
  próprias versões das funções acima). Foi o primeiro deck construído nesta
  série; os demais reusam `lib.js` para não duplicar o padrão visual.
- **`build_whatsapp.js`, `build_rcs.js`, `build_email.js`** — um deck por
  canal: capa, volumetria, Prioridade/Grupo Estratégico, funil completo
  (+ funil por fornecedor no WhatsApp), funil segmentado por Prioridade/GE,
  custo do canal, visão executiva.
- **`build_consolidado.js`** — visão única somando SMS+WhatsApp+RCS
  deduplicados por telefone (Email entra à parte, ver seção Email abaixo),
  com comparativo "qual canal performou melhor".
- **`build_fraseologia_*.js`** — qual frase/mensagem-modelo converte melhor,
  por canal, aberto por Prioridade e Grupo Estratégico + funil de frases.
- **Ícones** (`icon_<nome>_<cor>.png`) — gerados uma vez via `react-icons/fi`
  + `sharp` (rasterizados a partir do SVG do Feather Icons). Para gerar um
  ícone novo: `ReactDOMServer.renderToStaticMarkup(<Icon size={256}
  color="#XXXXXX"/>)` → `sharp(Buffer.from(svg), {density: 384}).png()`.
  **Nunca** desmonte/remonte a tag `<svg>` manualmente — ela carrega
  `stroke="currentColor"` e o `viewBox` reais; passar o SVG bruto pro `sharp`
  é o que funciona.

### Armadilhas de pptxgenjs (já resolvidas, não repetir)

- **`rowH` de `addTable` é um mínimo, não um valor fixo.** Células de duas
  linhas (padrão `celulaEtapa`: número + `%` menor embaixo) precisam de
  `rowH` generoso — se o conteúdo não couber, o LibreOffice/PowerPoint
  cresce a linha além do nominal, e qualquer elemento posicionado
  logicamente depois (callout, rodapé) passa a sobrepor. Fórmula segura usada
  em `makeSlideTabelaFrases`: `rowH = min(0.5, (7.0 − startY) / nLinhas)`,
  com fonte proporcional (`rowH ≥ 0.45 → 10.5pt`, `≥ 0.36 → 9.5pt`, senão
  `8.5pt`). Para tabelas de N linhas fixas, sempre teste com o maior N real
  antes de cravar `rowH`.
- **`statCard(slide, x, y, w, h, opts)` precisa de `h ≥ ~1.3`** para
  `valueSize` até ~24pt sem o valor sobrepor o label — a função reserva
  `h − 0.9` de altura pro número e `h − 0.42` pro label; com `h` menor que
  isso o texto do valor invade a área do label. Não reduzir `h` abaixo de
  1.3 só pra economizar espaço vertical; reduzir `valueSize` primeiro.
- Sempre rodar a skill `pptx` (validate + render + `Read` de cada slide) após
  qualquer mudança de layout — os dois bugs acima só aparecem no render, não
  no `validate.py`.

## Metodologia de dados — decisões e armadilhas

Isto documenta bugs reais encontrados e corrigidos ao construir os decks —
releia antes de confiar em qualquer número nesta área do projeto sem
reconferir contra `data_processing.py`.

### "Enviado" nunca pode ser maior que period-bucket errado (SMS)
O campo `data`/mês de uma linha de SMS vem do **timestamp do arquivo de
retorno** (`retorno["criacao"]`), não da data real de disparo. Uma campanha
sem retorno ainda casado fica com `data=NaT` e some de qualquer filtro por
mês — inflando artificialmente a taxa de conversão de um mês fechado (chegou
a parecer que "Enviado" = "Disparado" dentro do mês). Para recortes
mensais, use a data embutida no nome do arquivo/UTM da campanha
(`^(\d{4})(\d{2})(\d{2})`), não o campo `data` derivado do retorno —
`utms_no_periodo()` já faz isso pra selecionar as campanhas certas.

**Mas isso não bastava**: `filtrar_dados()`/`filtrar_dados_whatsapp()`
aplicavam esse mesmo `data_ini`/`data_fim` de novo, linha a linha, mesmo
depois de já restringir por `utms` — e uma linha `data=NaT` (retorno ainda
não confirmado pelo fornecedor, ex. "Não Processado" no Kolmeya) era
descartada por "estar fora do período", mesmo pertencendo à própria
campanha já confirmada por UTM. Sintoma real (SMS de setembro, campanha
única): arquivo de disparo tinha 4.722 telefones únicos, mas "Disparado"
no dashboard/deck mostrava 4.251 — os 471 ainda sem status do Kolmeya
sumiam do KPI, e Taxa de Envio aparecia 100,0% (quando o real é 90,0%).
Corrigido: quando `utms` é passado, uma linha `data=NaT` não é mais
excluída só por isso (a campanha dela já está confirmada no período);
sem `utms` (filtro só por data), a exclusão de NaT continua — é o que
evita campanha antiga vazando pra qualquer mês.

### Prioridade/Grupo Estratégico: sempre a partir do arquivo de disparo
`carregar_dados_sms()` retorna o disparo de **todos os canais**
(SMS/WhatsApp/RCS/Email), com `telefone_norm` + `grupo_ab` +
`grupo_estrategico` corretos por linha. **Essa é a fonte de verdade** para
composição de Prioridade/GE — nunca derive a composição a partir de uma
tabela de retorno ou de um cross-tab de CRM, que podem ter cobertura parcial
(no WhatsApp, um cross-tab baseado em retorno chegou a mostrar só 4.619 de
7.611 disparados, com uma distribuição de Prioridade completamente diferente
da real — bug encontrado e corrigido nesta sessão).

### Duas metodologias de cruzamento com CRM — ambas corretas, números diferentes
1. **Escopo por campanha** (`crm[crm.utm_campaign.isin(utms_do_canal)]`,
   dedup por telefone) — usada nos decks por canal (`build_whatsapp.js`,
   `build_rcs.js`, etc.) e no consolidado. Bate com os totais "oficiais" de
   cada capítulo.
2. **Cross-tab irrestrito por telefone** (join `telefone_norm` contra o log
   de CRM inteiro, sem filtrar por UTM) — é o que as funções nativas do app
   fazem (`agregar_frase_com_crm`, `agregar_mensagem_whatsapp_com_crm`,
   `_contagem_crm_por_texto`), usado nos decks de **fraseologia**. Produz
   totais de Acordo **diferentes** (geralmente maiores) do que a metodologia
   1 pro mesmo canal — ex.: RCS mostra 18 Acordos na visão por fraseologia
   contra 4 no capítulo RCS. **Isso não é inconsistência a corrigir**, é
   diferença de escopo documentada no rodapé de cada slide afetado.

### CRM log: Mobile vazio em ~47% das linhas — recuperado via CPF, exceto "Home"
O export do log de CRM (`ARQUIVOS LOG/`) vem com a coluna `Mobile` vazia em
quase metade de todas as linhas (47% do total; por `utm_medium`: email 87%,
rcs 96%, sms 64%, whatsapp 36% — varia muito por campanha, 13%–100%). Sem
telefone, a linha nunca casa com nenhum cruzamento (escopo da campanha ou
cross-tab irrestrito), mesmo que a ação tenha de fato acontecido — subestimando
Home/Autenticação/Oferta mesmo dentro do escopo oficial de uma campanha.

`carregar_dados_crm()` recupera a maior parte dessas linhas cruzando o `doc`
(CPF, com a mesma armadilha de notação científica do telefone — `1.682820e+10`
— tratada em `_normalizar_cpf`) contra um mapa CPF→telefone combinando
JEKINS (`cpf`+`telefone`) e `ARQUIVO DA BASE INTEIRA/` (`cpf`+`fone_1..fone_4`)
— `_mapa_cpf_telefone()`. Reduz o Mobile vazio de 47% para 25% no log inteiro.

**Mas isso não resolve "Home" igualmente**: quando o Mobile de uma linha
`home` vem vazio, o `doc` também vem vazio em ~100% dos casos (evento
pré-autenticação — o CRM ainda não identificou o cliente) — nada pra
recuperar. Já `auth`/`oferta`/`acordo` (pós-autenticação) quase sempre têm
Mobile **ou** Doc, então a recuperação por CPF eleva bastante esses totais
sem mexer em Home. Verificado no escopo-campanha (`crm[utm_campaign.isin(...)
& telefone_norm.isin(telefones_das_campanhas(...))]`, antes → depois do fix):

| Canal    | Home      | Auth        | Oferta      | Acordo   |
|----------|-----------|-------------|-------------|----------|
| SMS      | 175 → 175 | 138 → 321   | 136 → 345   | 40 → 40  |
| WhatsApp | 1523→1523 | 1487 → 2195 | 1309 → 1918 | 123→123  |
| RCS      | 2 → 2     | 2 → 44      | 2 → 43      | 4 → 4    |

Ou seja: o funil pode parecer "invertido" (Auth/Oferta > Home) num recorte
qualquer — **isso não é bug nem funil real invertido**, é o piso de Home
(subcontagem estrutural do export) ficando visivelmente menor que
Auth/Oferta (quase completos). Sempre que Home aparecer num funil de CRM,
deixar essa ressalva explícita — nunca apresentar Home como número completo
ou comparar Home vs. Auth como se fosse um funil sequencial estrito.

### Funil de CRM sempre em clientes únicos, nunca em eventos brutos
`agregar_crm_por_campanha/grupo_ab/grupo_estrategico/medium`,
`_contagem_crm_por_texto` (Fraseologia) e `montar_pivot_crm` contavam
**linhas** do log (eventos), não `telefone_norm.nunique()`. Uma mesma ação
pode ser registrada mais de uma vez pro mesmo cliente — ex.: "Oferta
Apresentada" reapresentada em várias ligações, um telefone chegou a ter 10
linhas de Oferta sozinho — o que produzia números como Oferta (34 eventos)
> Autenticação (23 eventos) num recorte de SMS, parecendo um funil
invertido de novo (diferente do piso do Home acima: aqui o cliente único
bate — 15 telefones com Oferta, **todos** também com Autenticação, de 19
com Autenticação). Corrigido: toda contagem de CRM no projeto agora é por
cliente único (`contagem_crm_unicos()` para os totais do funil combinado,
que soma direto sobre o escopo já filtrado — nunca soma
`agregar_crm_por_campanha` campanha a campanha, que contaria de novo um
telefone que recebeu mais de uma campanha).

### Dedup do log de CRM: `doc` vazio colapsa clientes diferentes no mesmo minuto
A chave de deduplicação (`doc, utm campaign, acao, data`) tem a mesma
armadilha documentada acima pra `id`: evento "home" nunca tem `doc`
preenchido, e `data` só tem granularidade de minuto — duas linhas de
clientes **diferentes** que visitaram no mesmo minuto colapsavam em uma só
"duplicata". Achado real: a campanha de SMS de setembro tinha 78 linhas de
Home no log bruto, 12 descartadas como duplicata só por `doc=NaN` + mesmo
minuto — só 4 de fato repetiam **IP** também (duplicata real/replay do
pixel); as outras 8 eram clientes diferentes com IPs diferentes no mesmo
minuto. `ip` (presente em ~100% das linhas sem `doc`) entrou na chave —
78→74 linhas de Home nessa campanha, contra os 66 de antes do fix.

**Isso não torna Home identificável por telefone.** Conferido por exaustão —
**todas** as ~20 colunas do log foram olhadas linha a linha nessas 74 (não só
`mobile`/`doc`): `telefone`, `celular`, `email`, `nome`, `url`, `link
pagamento`, `pagamento link`, `boleto`, `id cliente` vêm **todas vazias**.
O que sobra preenchido é só: `ip`, `data`/`timestamp` (granularidade de
minuto), as UTMs da campanha (`utm source/medium/campaign/content/kwd/group`
— constantes, iguais pra linha inteira, não identificam pessoa), `utm cus`
(um client ID estilo Google Analytics, formato `<random>.<timestamp>`, não é
telefone codificado) e `canal` = **"portal"**. Esse último campo é a
explicação arquitetural: o evento "home" é capturado pelo pixel do **site**
quando a página carrega, não pelo clique no link único do SMS/WhatsApp —
nem esse link aparece em nenhuma coluna do log. Ou seja, o sistema
literalmente ainda não sabe quem é o cliente nesse instante (antes de
CPF/login), não é falta de exportar um campo que existe em algum lugar. A
pergunta "por que não busca no JEKINS?" já foi verificada à exaustão: não há
nenhum campo em comum entre essas linhas e o JEKINS (que só tem
cpf/telefone/nome/email — nada bate com ip/utm_cus). O piso de Home
continua valendo (seção acima) — o fix de dedup só corrige a contagem bruta
de eventos, não a identificação.

### WhatsApp Airys: gap de casamento de telefone
O arquivo de retorno bruto da Airys tem 845 telefones únicos, mas só 707
batem com o escopo de disparo da própria campanha Airys (`telefones_das_campanhas`)
— os outros 138 são ruído fora de escopo. Sempre use
`filtrar_dados_whatsapp(df, utms=...)` (que já faz esse
casamento) antes de tirar qualquer número "% do disparo" da Airys, nunca o
arquivo bruto direto.

### Email tem duas identidades que não se cruzam
- **Fonte 1 — Salesforce Journey Builder**: relatório agregado (Envios/
  Entregues/Aberturas/Cliques), sem telefone nem e-mail por linha. Não dá pra
  segmentar por Prioridade/GE nem cruzar com CRM.
- **Fonte 2 — campanhas avulsas de e-mail** (`ARQUIVOS PARA DISPAROS/`,
  identificadas por e-mail em `identificador_norm`): têm `grupo_ab` por
  linha (mas não `grupo_estrategico` — é preciso inferir pelo nome da
  campanha, ex. `...abandonocarrinho...` → Abandono Carrinho). As ações de
  CRM associadas são casadas por **telefone**, não por e-mail — ou seja, o
  destinatário do disparo (e-mail) e o cliente que gerou a ação de CRM
  (telefone) não são necessariamente a mesma pessoa rastreável ponta a
  ponta. Nunca junte as duas fontes como se fossem um funil único de
  destinatário — sempre com o alerta explícito nos slides.
- **`build_fraseologia_email.js` usa ranking de Assunto, não Acordo.** Como a
  Fonte 1 (única usada nesse deck) não tem destinatário por linha, não existe
  cruzamento com CRM possível neste nível — diferente de SMS/WhatsApp/RCS, cuja
  fraseologia mede Acordos por frase. O deck de Email ranqueia os 16 assuntos
  do período por taxa de abertura (Aberturas ÷ Entregues) e CTOR (Cliques ÷
  Aberturas), com nota de cautela nos assuntos de amostra mínima (< 20 envios).

### Deduplicação entre canais (visão consolidada)
SMS + WhatsApp + RCS usam `telefone_norm` como chave e **se sobrepõem**: somar
os três totais ingenuamente infla a base (50.247 vs. 35.290 clientes únicos
reais — 14.957 registros de sobreposição). Email nunca entra
nessa deduplicação (chave diferente, ver acima).

### Custos confirmados (`CUSTO_CONFIG_POR_CANAL_FORNECEDOR` em `data_processing.py`)
```python
("sms", "kolmeya"):    {"custo_unitario": 0.0620, "base": "enviado"}
("sms", "otima"):      {"custo_unitario": 0.0500, "base": "enviado"}
("rcs", "otima"):      {"custo_unitario": 0.0900, "base": "disparado"}
("whatsapp", "otima"): {"custo_unitario": 0.0685, "base": "entregue"}
("whatsapp", "airys"): {"custo_unitario": 0.0500, "base": "entregue"}
```
Email **não tem** custo unitário confirmado — nunca inventar um valor; os
decks mostram explicitamente "não calculável". Lemit (enriquecimento de
dados, julho) é investimento fixo de R$ 1.851,04, **fora** do custo direto de
disparo — some à parte no "investimento total do período"
(R$ 7.887,49 = SMS R$ 5.036,38 + RCS R$ 753,48 + WhatsApp R$ 246,59 + Lemit
R$ 1.851,04).

## Princípios gerais deste projeto (reforçados durante a sessão)

- **Nunca inventar métrica ou valor que não possa ser obtido pelos dados.**
  Quando um indicador não é calculável (ex.: custo do Email), deixe isso
  explícito no material em vez de estimar.
- O usuário verifica números com frequência e sempre que questiona algo
  ("os números tão certos?", "o enviado nunca é igual o disparado?") a
  pergunta revelou um bug real, não um alarme falso — trate ceticismo do
  usuário sobre um número como sinal pra reconferir a partir dos dados brutos,
  não só reexplicar o número existente.
- "Eventos brutos" (pode contar o mesmo cliente mais de uma vez) e "clientes
  únicos" (deduplicado por telefone) são conceitos que nunca devem se
  misturar na mesma célula/coluna sem rótulo explícito de qual é qual.
