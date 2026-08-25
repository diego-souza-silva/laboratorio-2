const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, statCard, makeFooter, slideCapa,
  makeSlideFunilCompleto, slideInvestimentoTotal,
  makeSlidePrioridadeGrupoEstrategico, makeSlideFunilSegmentado,
} = require("./lib.js");

const footer = makeFooter("Consolidado");
const slideFunilCompleto = makeSlideFunilCompleto(footer);
const slidePrioridadeGrupoEstrategico = makeSlidePrioridadeGrupoEstrategico(footer);
const slideFunilSegmentado = makeSlideFunilSegmentado(footer);

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "VISÃO CONSOLIDADA",
  titulo: "TODOS OS CANAIS",
  subtitulo: "Resultados Casas Bahia — SMS, WhatsApp e RCS somados, sem separação por canal",
  periodo: "Período analisado: 25/07 a 15/08  ·  Clientes únicos contados uma só vez, mesmo quando tocados por mais de um canal",
  etapas: ["Disparo", "Entrega", "Home", "Auth", "Oferta", "Acordo"],
});

// =====================================================================
// SLIDE 2 — VOLUMETRIA CONSOLIDADA (SMS + WhatsApp + RCS)
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Volumetria consolidada", {
    x: 0.7, y: 0.5, w: 10, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("SMS + WhatsApp + RCS somados — clientes únicos deduplicados por telefone entre canais", {
    x: 0.7, y: 1.08, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  const cw4 = 2.875, gx4 = 0.15, x04 = 0.7, cardY = 1.7, cardH = 1.75;
  statCard(s, x04 + 0 * (cw4 + gx4), cardY, cw4, cardH, {
    icon: "icon_send_1E2761.png", value: "35.290", valueSize: 28,
    label: "Clientes únicos disparados",
  });
  statCard(s, x04 + 1 * (cw4 + gx4), cardY, cw4, cardH, {
    icon: "icon_mail_1E2761.png", value: "32.715", valueSize: 28,
    label: "Clientes únicos com envio confirmado",
  });
  statCard(s, x04 + 2 * (cw4 + gx4), cardY, cw4, cardH, {
    icon: "icon_check_1E2761.png", value: "27.903", valueSize: 28,
    label: "Clientes únicos com entrega confirmada",
  });
  statCard(s, x04 + 3 * (cw4 + gx4), cardY, cw4, cardH, {
    icon: "icon_percent_1E2761.png", value: "3,07", valueSize: 28,
    label: "SPIN geral — disparos por cliente único",
  });

  s.addText("Como os canais se sobrepõem", {
    x: 0.7, y: 3.7, w: 8, h: 0.35, fontFace: "Calibri", fontSize: 15, bold: true, color: NAVY, margin: 0,
  });

  const linhas = [
    ["SMS — base disparada", "34.264 clientes únicos"],
    ["RCS — base disparada", "8.372 clientes únicos"],
    ["WhatsApp — base disparada", "7.611 clientes únicos"],
    ["Soma simples dos 3 canais", "50.247 (com duplicidade entre canais)"],
    ["União real (deduplicada)", "35.290 clientes únicos — 14.957 registros de sobreposição removidos"],
  ];
  let ly = 4.1;
  const rowH = 0.4;
  linhas.forEach(([nome, valor], i) => {
    const destaque = i === linhas.length - 1;
    s.addShape("roundRect", {
      x: 0.7, y: ly, w: 11.95, h: rowH, rectRadius: 0.05,
      fill: { color: destaque ? "EAF6EF" : CARDBG }, line: { color: destaque ? GREEN : LINE, width: 1 },
    });
    s.addText(nome, { x: 1.0, y: ly, w: 6.5, h: rowH, fontFace: "Calibri", fontSize: 12, bold: destaque, color: INK, valign: "middle", margin: 0 });
    s.addText(valor, { x: 7.6, y: ly, w: 4.9, h: rowH, fontFace: "Calibri", fontSize: 12, bold: true, color: destaque ? "1D7A45" : NAVY, valign: "middle", margin: 0 });
    ly += rowH + 0.06;
  });

  s.addText("SPIN geral = 108.389 eventos de disparo (todos os canais com telefone, incluindo reenvios) ÷ 35.290 clientes únicos. Email tem base própria (por e-mail) — ver próximo slide.", {
    x: 0.7, y: ly + 0.06, w: 11.95, h: 0.4, fontFace: "Calibri", fontSize: 10.5, italic: true, color: MUTED, margin: 0,
  });

  footer(s, pres, "\"Clientes únicos\" aqui = deduplicados por telefone entre SMS, WhatsApp e RCS. Email não usa telefone como identificador — entra em slide próprio a seguir.");
}

// =====================================================================
// SLIDE 3 — VOLUMETRIA DO EMAIL (base própria, por e-mail)
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Volumetria do Email — base própria", {
    x: 0.7, y: 0.5, w: 10.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Email não é deduplicado por telefone com os outros canais — duas fontes próprias, mostradas à parte", {
    x: 0.7, y: 1.06, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 13.5, color: MUTED, margin: 0,
  });

  s.addText("Fonte 1 — Salesforce Journey Builder (relatório agregado, sem linha por destinatário)", {
    x: 0.7, y: 1.6, w: 11.5, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, margin: 0,
  });
  const cw4 = 2.875, gx4 = 0.15, x04 = 0.7;
  statCard(s, x04 + 0 * (cw4 + gx4), 1.95, cw4, 1.4, {
    icon: "icon_send_1E2761.png", value: "37.730", valueSize: 22, label: "Envios",
  });
  statCard(s, x04 + 1 * (cw4 + gx4), 1.95, cw4, 1.4, {
    icon: "icon_check_1E2761.png", value: "35.615", valueSize: 22, label: "Entregues (94,4%)",
  });
  statCard(s, x04 + 2 * (cw4 + gx4), 1.95, cw4, 1.4, {
    icon: "icon_eye_1E2761.png", value: "270", valueSize: 22, label: "Aberturas (0,76% do entregue)",
  });
  statCard(s, x04 + 3 * (cw4 + gx4), 1.95, cw4, 1.4, {
    icon: "icon_click_1E2761.png", value: "37", valueSize: 22, label: "Cliques (0,10% do entregue)",
  });

  s.addText("Fonte 2 — Campanhas avulsas de e-mail do CRM (arquivo de disparo, com Prioridade/Grupo Estratégico)", {
    x: 0.7, y: 3.6, w: 11.5, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, margin: 0,
  });
  statCard(s, 0.7, 3.95, 3.85, 1.4, {
    icon: "icon_send_1E2761.png", value: "5.535", valueSize: 26, label: "Destinatários únicos (por e-mail)",
  });
  statCard(s, 4.75, 3.95, 3.85, 1.4, {
    icon: "icon_home_1E2761.png", value: "11", valueSize: 26, label: "Ações de Home (CRM, por telefone)",
  });
  statCard(s, 8.8, 3.95, 3.85, 1.4, {
    icon: "icon_award_2F9E6E.png", value: "5", valueSize: 26, valueColor: GREEN, label: "Acordos gerados (CRM, por telefone)",
  });

  s.addShape("roundRect", {
    x: 0.7, y: 5.5, w: 11.95, h: 0.95, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 0.92, y: 5.65, w: 0.32, h: 0.32 });
  s.addText([
    { text: "Nenhuma das duas bases de Email entra na volumetria consolidada (35.290) do slide anterior:  ", options: { bold: true, color: "B5541A" } },
    { text: "a Fonte 1 não tem telefone por destinatário; a Fonte 2 identifica por e-mail, não por telefone — não dá pra deduplicar com SMS/WhatsApp/RCS sem inventar um cruzamento que os dados não sustentam.", options: { color: "6B4632" } },
  ], {
    x: 1.35, y: 5.5, w: 11.1, h: 0.95, fontFace: "Calibri", fontSize: 11.5, valign: "middle", margin: 0,
  });

  footer(s, pres, "Detalhamento completo (Prioridade/Grupo Estratégico, funil e taxas) no capítulo Email. Sem custo unitário confirmado — Email não entra no investimento total do período.");
}

// =====================================================================
// SLIDE 4 — PRIORIDADE E GRUPO ESTRATÉGICO CONSOLIDADOS
// =====================================================================
slidePrioridadeGrupoEstrategico(pres, {
  titulo: "Base consolidada por Prioridade e Grupo Estratégico",
  subtitulo: "Composição dos 35.290 clientes únicos disparados (SMS + WhatsApp + RCS, deduplicados por telefone)",
  linhasPrioridade: [
    ["P1 · Máxima", "7.887", "22,3%"],
    ["P2 · Alta", "8.626", "24,4%"],
    ["P3 · Média", "7.091", "20,1%"],
    ["P4 · Baixa", "6.564", "18,6%"],
    ["Não Classificado", "5.122", "14,5%"],
  ],
  linhasGE: [
    ["Abandono Carrinho", "4.224", "12,0%"],
    ["Cadastrado", "26", "0,1%"],
    ["Engajado", "4.916", "13,9%"],
    ["Topo de Funil", "20.993", "59,5%"],
    ["Não Classificado", "5.131", "14,5%"],
  ],
  total: "35.290",
  footerTexto: "Base: telefone único, com prioridade/grupo do primeiro canal em que o cliente aparece. Email tem base e Prioridade próprias (ver slide anterior e capítulo Email) — não incluído aqui.",
});

// =====================================================================
// SLIDE 5 — FUNIL SEGMENTADO POR PRIORIDADE
// =====================================================================
slideFunilSegmentado(pres, {
  titulo: "Funil completo por Prioridade",
  subtitulo: "Todos os canais somados, abertos por Prioridade — clientes únicos e % etapa a etapa",
  colunaLabel: "PRIORIDADE",
  colunasEtapas: ["Disparo", "Enviado", "Entrega", "Home", "Auth", "Oferta", "Acordo"],
  linhas: [
    ["P1 · Máxima", "7.887", ["7.388", "94%"], ["6.724", "91%"], ["101", "2%"], ["88", "87%"], ["84", "95%"], ["24", "29%"], "0,30%"],
    ["P2 · Alta", "8.626", ["8.222", "95%"], ["7.354", "89%"], ["28", "0%"], ["24", "86%"], ["20", "83%"], ["8", "40%"], "0,09%"],
    ["P3 · Média", "7.091", ["6.532", "92%"], ["5.315", "81%"], ["32", "1%"], ["31", "97%"], ["28", "90%"], ["7", "25%"], "0,10%"],
    ["P4 · Baixa", "6.564", ["5.810", "89%"], ["4.351", "75%"], ["23", "1%"], ["23", "100%"], ["20", "87%"], ["4", "20%"], "0,06%"],
    ["Não Classificado", "5.122", ["4.763", "93%"], ["4.159", "87%"], ["92", "2%"], ["73", "79%"], ["64", "88%"], ["28", "44%"], "0,55%"],
  ],
  total: ["Total Geral", "35.290", ["32.715", "93%"], ["27.903", "85%"], ["276", "1%"], ["239", "87%"], ["216", "90%"], ["71", "33%"], "0,20%"],
  insightTitulo: "P1 · Máxima converte melhor entre as classificadas:",
  insightTexto: "0,30% de Disparo→Acordo contra 0,06%-0,10% em P2-P4 — mesmo padrão de todos os canais individuais. \"Não Classificado\" puxa a média por incluir o Email (ver nota).",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo. Home/Auth/Oferta/Acordo somam ações de CRM de todos os canais (incl. Email) — por isso \"Não Classificado\" inclui clientes de e-mail sem Prioridade nesta base de disparo.",
});

// =====================================================================
// SLIDE 6 — FUNIL SEGMENTADO POR GRUPO ESTRATÉGICO
// =====================================================================
slideFunilSegmentado(pres, {
  titulo: "Funil completo por Grupo Estratégico",
  subtitulo: "Todos os canais somados, abertos por Grupo Estratégico — clientes únicos e % etapa a etapa",
  colunaLabel: "GRUPO ESTRATÉGICO",
  colunasEtapas: ["Disparo", "Enviado", "Entrega", "Home", "Auth", "Oferta", "Acordo"],
  linhas: [
    ["Abandono Carrinho", "4.224", ["3.906", "92%"], ["3.539", "91%"], ["98", "3%"], ["93", "95%"], ["91", "98%"], ["7", "8%"], "0,17%"],
    ["Cadastrado", "26", ["23", "88%"], ["19", "83%"], ["1", "5%"], ["1", "100%"], ["1", "100%"], ["1", "100%"], "3,85%"],
    ["Engajado", "4.916", ["4.659", "95%"], ["4.231", "91%"], ["50", "1%"], ["44", "88%"], ["35", "80%"], ["20", "57%"], "0,41%"],
    ["Topo de Funil", "20.993", ["19.355", "92%"], ["15.947", "82%"], ["35", "0%"], ["28", "80%"], ["25", "89%"], ["15", "60%"], "0,07%"],
    ["Não Classificado", "5.131", ["4.772", "93%"], ["4.167", "87%"], ["92", "2%"], ["73", "79%"], ["64", "88%"], ["28", "44%"], "0,55%"],
  ],
  total: ["Total Geral", "35.290", ["32.715", "93%"], ["27.903", "85%"], ["276", "1%"], ["239", "87%"], ["216", "90%"], ["71", "33%"], "0,20%"],
  insightTitulo: "Engajado converte muito acima da média:",
  insightTexto: "0,41% de Disparo→Acordo — cliente que já teve algum engajamento prévio responde bem melhor em todos os canais, confirmando o padrão visto por canal.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo. Home/Auth/Oferta/Acordo somam ações de CRM de todos os canais (incl. Email).",
});

// =====================================================================
// SLIDE 7 — FUNIL COMPLETO CONSOLIDADO
// =====================================================================
slideFunilCompleto(pres, {
  titulo: "Funil completo — Todos os canais",
  subtitulo: "Clientes únicos por etapa (SMS + WhatsApp + RCS no disparo; +Email a partir de Home) — % sobre a base de disparo",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 35290, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 32715, pctDisparo: "92,7%", conv: "92,7%", drop: "7,3%" },
    { nome: "Entrega", icon: "check", valor: 27903, pctDisparo: "79,1%", conv: "85,3%", drop: "14,7%" },
    { nome: "Home", icon: "home", valor: 276, pctDisparo: "0,78%", conv: "1,0%", drop: "99,0%", gargalo: true },
    { nome: "Auth", icon: "shield", valor: 239, pctDisparo: "0,68%", conv: "86,6%", drop: "13,4%" },
    { nome: "Oferta", icon: "tag", valor: 216, pctDisparo: "0,61%", conv: "90,4%", drop: "9,6%" },
    { nome: "Acordo", icon: "award", valor: 71, pctDisparo: "0,20%", conv: "32,9%", drop: "67,1%" },
  ],
  gargaloTitulo: "Maior gargalo: Entrega → Home",
  gargaloTexto: "— 99,0% dos clientes que recebem alguma mensagem (SMS, WhatsApp ou RCS) não avançam para negociação no CRM, em nenhum canal.",
  footerTexto: "% do disparo = etapa ÷ 35.290 clientes únicos disparados (SMS+WhatsApp+RCS, deduplicados por telefone). Home/Auth/Oferta/Acordo somam ações de CRM de todos os canais, incluindo Email, também deduplicadas por telefone — por isso o total é menor que a soma dos capítulos por canal (um mesmo cliente pode aparecer em mais de um canal).",
});

// =====================================================================
// SLIDE 8 — QUAL CANAL PERFORMOU MELHOR
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Qual canal performou melhor?", {
    x: 0.7, y: 0.5, w: 10.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Comparativo lado a lado — disparo, entrega, conversão e custo por Acordo", {
    x: 0.7, y: 1.06, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  const headerFill = NAVY, totalFill = "D6E6F5", destaqueFill = "EAF6EF";
  const cols = ["Canal", "Disparo", "Entrega", "% Entrega", "Acordo", "% Conv.", "Custo/Acordo"];
  const colW = [2.2, 1.6, 1.6, 1.55, 1.4, 1.5, 2.1];
  const linhas = [
    ["SMS", "34.264", "26.370", "76,9%", "33", "0,10%", "R$ 152,62"],
    ["RCS", "8.372", "5.533", "66,1%", "4", "0,05%", "R$ 188,37"],
    ["WhatsApp", "7.611", "3.783", "49,7%", "31", "0,41%", "R$ 7,95"],
    ["Email*", "5.535", "—", "—", "5", "—", "—"],
  ];
  const rows = [];
  rows.push(cols.map((c, i) => ({
    text: c,
    options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 12, align: i === 0 ? "left" : "right" },
  })));
  linhas.forEach((linha, i) => {
    const destaque = linha[0] === "WhatsApp";
    const bg = destaque ? destaqueFill : (i % 2 === 0 ? WHITE : CARDBG);
    rows.push(linha.map((v, j) => ({
      text: v,
      options: {
        fill: { color: bg },
        color: j === 0 ? INK : (j === 5 && destaque ? "1D7A45" : (j === 6 && destaque ? "1D7A45" : NAVY)),
        bold: j === 0 || (destaque && (j === 5 || j === 6)),
        fontSize: 12, align: j === 0 ? "left" : "right",
      },
    })));
  });
  s.addTable(rows, {
    x: 0.7, y: 1.7, w: 11.95, colW, rowH: 0.52,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri", autoPage: false, valign: "middle",
  });

  const calloutY = 1.7 + rows.length * 0.52 + 0.2;
  s.addShape("roundRect", {
    x: 0.7, y: calloutY, w: 11.95, h: 1.05, rectRadius: 0.08,
    fill: { color: "EAF6EF" }, line: { color: GREEN, width: 1.5 },
  });
  s.addImage({ path: "icon_award_2F9E6E.png", x: 0.95, y: calloutY + 0.2, w: 0.4, h: 0.4 });
  s.addText([
    { text: "WhatsApp performou melhor, apesar do menor volume e da pior entrega:  ", options: { bold: true, color: "1D7A45", fontSize: 13.5 } },
    { text: "0,41% de conversão Disparo→Acordo — 4x a do SMS e 8x a do RCS — com o menor custo por Acordo de todos os canais (R$ 7,95, contra R$ 152,62 do SMS e R$ 188,37 do RCS). Quem chega até o WhatsApp negocia muito mais.", options: { color: "2F5741", fontSize: 12.5 } },
  ], {
    x: 1.5, y: calloutY, w: 10.9, h: 1.05, fontFace: "Calibri", valign: "middle", margin: 0,
  });

  s.addText("*Email: \"Disparo\" = base da campanha avulsa (5.535, por e-mail); Acordo = ação de CRM (por telefone) — os dois não são o mesmo destinatário, por isso % Entrega/% Conv./Custo não são calculáveis de forma comparável aos demais canais.", {
    x: 0.7, y: calloutY + 1.2, w: 11.95, h: 0.4, fontFace: "Calibri", fontSize: 10.5, italic: true, color: MUTED, margin: 0,
  });

  footer(s, pres, "% Conv. = Acordo ÷ Disparo (jornada completa). Custo/Acordo = custo direto do canal ÷ Acordos gerados por ele (sem Lemit).");
}

// =====================================================================
// SLIDE 9 — CUSTO CONSOLIDADO
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Custo consolidado — Todos os canais", {
    x: 0.7, y: 0.5, w: 10, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Custo direto de disparo (SMS + RCS + WhatsApp) x investimento total do período", {
    x: 0.7, y: 1.06, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  statCard(s, 0.7, 1.6, 3.85, 1.3, {
    icon: "icon_dollar_1E2761.png", value: "R$ 6.036,45", valueSize: 19,
    label: "Custo direto de disparo (SMS + RCS + WhatsApp)",
  });
  statCard(s, 4.75, 1.6, 3.85, 1.3, {
    icon: "icon_award_2F9E6E.png", value: "R$ 85,02", valueSize: 22, valueColor: GREEN,
    label: "Custo médio por Acordo — só canais de disparo",
  });
  statCard(s, 8.8, 1.6, 3.85, 1.3, {
    icon: "icon_award_2F9E6E.png", value: "R$ 111,09", valueSize: 22, valueColor: ORANGE,
    label: "Custo médio por Acordo — com investimento total (+Lemit)",
  });

  s.addText("Custo por resultado (custo direto de disparo ÷ volume da etapa)", {
    x: 0.7, y: 3.05, w: 10, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, margin: 0,
  });

  const custos = [
    ["Por cliente disparado", "R$ 0,17"],
    ["Por cliente entregue", "R$ 0,22"],
    ["Por chegada na Home", "R$ 21,87"],
    ["Por Oferta apresentada", "R$ 27,95"],
    ["Por Acordo fechado", "R$ 85,02"],
  ];
  const cw = 2.31, cx0 = 0.7, cy = 3.4, ch = 0.8;
  custos.forEach(([label, valor], i) => {
    const x = cx0 + i * cw;
    const destaque = i === custos.length - 1;
    s.addShape("roundRect", {
      x: x + 0.05, y: cy, w: cw - 0.1, h: ch, rectRadius: 0.08,
      fill: { color: destaque ? NAVY : CARDBG },
      line: { color: destaque ? NAVY : LINE, width: 1 },
    });
    s.addText(valor, {
      x: x + 0.15, y: cy + 0.1, w: cw - 0.3, h: 0.42, fontFace: "Calibri", fontSize: 15, bold: true,
      color: destaque ? WHITE : NAVY, align: "left", valign: "top", margin: 0,
    });
    s.addText(label, {
      x: x + 0.15, y: cy + 0.52, w: cw - 0.3, h: 0.32, fontFace: "Calibri", fontSize: 9, valign: "top",
      color: destaque ? ICE : MUTED, align: "left", margin: 0,
    });
  });

  s.addText("Investimento total do período (todos os canais)", {
    x: 0.7, y: 4.5, w: 8, h: 0.3, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, margin: 0,
  });
  slideInvestimentoTotal(s, {
    x: 0.7, y: 4.83, w: 8.05,
    linhas: [
      ["SMS (Kolmeya)", "R$ 5.036,38", "63,9%"],
      ["RCS (Ötima)", "R$ 753,48", "9,6%"],
      ["WhatsApp (Ötima + Airys)", "R$ 246,59", "3,1%"],
      ["Lemit — enriquecimento de dados (julho)", "R$ 1.851,04", "23,5%"],
    ],
    total: "R$ 7.887,49",
  });

  footer(s, pres, "Custo por resultado calculado sobre o custo direto de disparo (R$ 6.036,45) — Lemit é investimento de enriquecimento de dados, não de disparo, por isso é somado à parte no custo por Acordo \"com investimento total\". Email sem custo unitário confirmado, não entra em nenhuma linha desta página.");
}

// =====================================================================
// SLIDE 10 — VISÃO EXECUTIVA
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Visão executiva — Todos os canais", {
    x: 0.7, y: 0.5, w: 10.5, h: 0.55, fontFace: "Cambria", fontSize: 26, bold: true, color: WHITE, margin: 0,
  });
  s.addText("O que essa análise já responde, olhando o marketing como um todo — sem separar por canal", {
    x: 0.7, y: 1.05, w: 11, h: 0.35, fontFace: "Calibri", fontSize: 12.5, color: ICE, margin: 0,
  });

  const perguntas = [
    ["Clientes únicos impactados", "35.290 (SMS + WhatsApp + RCS)"],
    ["SPIN geral", "3,07 disparos por cliente único"],
    ["Taxa de entrega", "79,1% dos disparos"],
    ["Conversão total Disparo → Acordo", "0,20%"],
    ["Acordos gerados (todos os canais)", "71"],
    ["Canal com melhor conversão", "WhatsApp — 0,41% (4x o SMS)"],
    ["Canal com menor custo por Acordo", "WhatsApp — R$ 7,95"],
    ["Email — destinatários (base própria)", "5.535 (e-mail) / 37.730 (Salesforce)"],
    ["Investimento total do período", "R$ 7.887,49"],
    ["Custo médio por Acordo (direto)", "R$ 85,02"],
    ["Custo médio por Acordo (c/ Lemit)", "R$ 111,09"],
    ["Maior gargalo", "Entrega → Home (-99,0%)"],
  ];

  const cols = 3, rows = 4, cw = 3.85, ch = 1.15, x0 = 0.7, y0 = 1.55, gx = 0.15, gy = 0.15;
  perguntas.forEach(([pergunta, resposta], i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
    const isGargalo = pergunta === "Maior gargalo";
    const isDestaque = pergunta.startsWith("Canal com");
    s.addShape("roundRect", {
      x, y, w: cw, h: ch, rectRadius: 0.08,
      fill: { color: isGargalo ? ORANGE : (isDestaque ? "1D7A45" : "2A3572") },
      line: { type: "none" },
    });
    s.addText(pergunta, {
      x: x + 0.2, y: y + 0.14, w: cw - 0.4, h: 0.4, fontFace: "Calibri", fontSize: 11,
      color: isGargalo ? "FDEDE4" : ICE, align: "left", valign: "top", margin: 0,
    });
    s.addText(resposta, {
      x: x + 0.2, y: y + 0.5, w: cw - 0.4, h: 0.55, fontFace: "Calibri", fontSize: 13.5, bold: true,
      color: WHITE, align: "left", valign: "top", margin: 0,
    });
  });

  s.addText("Nota: \"clientes únicos\" nesta visão são deduplicados por telefone entre SMS, WhatsApp e RCS. Email usa base própria (por e-mail para disparo, por telefone para CRM) e não é deduplicado com os demais — ver slides dedicados.", {
    x: 0.7, y: 6.85, w: 11.9, h: 0.5, fontFace: "Calibri", fontSize: 11, italic: true,
    color: "8FA3D9", margin: 0,
  });
}

pres.writeFile({ fileName: "casas_bahia_consolidado.pptx" }).then(() => console.log("done"));
