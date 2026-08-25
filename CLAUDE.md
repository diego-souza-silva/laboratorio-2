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

## Metodologia de dados — decisões e armadilhas (todas as carteiras)

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
(`^(\d{4})(\d{2})(\d{2})`), não o campo `data` derivado do retorno.

### Prioridade/Grupo Estratégico: sempre a partir do arquivo de disparo
`carregar_dados_sms(carteira)` retorna o disparo de **todos os canais**
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

### WhatsApp Airys: gap de casamento de telefone
O arquivo de retorno bruto da Airys tem 845 telefones únicos, mas só 707
batem com o escopo de disparo da própria campanha Airys (`telefones_das_campanhas`)
— os outros 138 são ruído fora de escopo. Sempre use
`filtrar_dados_whatsapp(df, utms=..., carteira=...)` (que já faz esse
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

### Deduplicação entre canais (visão consolidada)
SMS + WhatsApp + RCS usam `telefone_norm` como chave e **se sobrepõem**: somar
os três totais ingenuamente infla a base (50.247 vs. 35.290 clientes únicos
reais nesta carteira — 14.957 registros de sobreposição). Email nunca entra
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
