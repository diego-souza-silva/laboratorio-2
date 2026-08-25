const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, statCard, makeFooter, tabelaDinamica,
  makeSlidePrioridadeGrupoEstrategico, makeSlideFunilCompleto, slideCapa,
  makeSlideFunilSegmentado, slideInvestimentoTotal,
} = require("./lib.js");

const footer = makeFooter("WhatsApp");
const slidePrioridadeGrupoEstrategico = makeSlidePrioridadeGrupoEstrategico(footer);
const slideFunilCompleto = makeSlideFunilCompleto(footer);
const slideFunilSegmentado = makeSlideFunilSegmentado(footer);

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "CAPÍTULO 2 · CANAL",
  titulo: "WHATSAPP",
  subtitulo: "Resultados Casas Bahia — jornada completa do disparo ao acordo",
  periodo: "Período analisado: 28/07 (Ötima) e 29/07 (Airys)  ·  Fornecedores: Ötima e Airys",
  etapas: ["Disparo", "Entrega", "Lido", "Home", "Auth", "Oferta", "Acordo"],
});

// =====================================================================
// SLIDE 2 — VOLUMETRIA
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Volumetria do disparo", {
    x: 0.7, y: 0.5, w: 9, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Dois fornecedores distintos, cada um com sua própria janela de disparo — Ötima e Airys somados", {
    x: 0.7, y: 1.08, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  statCard(s, 0.7, 1.7, 3.85, 1.7, {
    icon: "icon_send_1E2761.png", value: "7.611", valueSize: 34,
    label: "WhatsApp disparados no total (Ötima + Airys)",
  });
  statCard(s, 4.75, 1.7, 3.85, 1.7, {
    icon: "icon_check_1E2761.png", value: "3.783", valueSize: 34,
    label: "Clientes únicos com entrega confirmada",
  });
  statCard(s, 8.8, 1.7, 3.85, 1.7, {
    icon: "icon_eye_1E2761.png", value: "2.401", valueSize: 34,
    label: "Clientes únicos que leram a mensagem",
  });

  s.addText("Jornada de entrega por fornecedor", {
    x: 0.7, y: 3.6, w: 6, h: 0.35, fontFace: "Calibri", fontSize: 15, bold: true, color: NAVY, margin: 0,
  });

  const linhas = [
    ["Ötima — Disparo", "3.807", "100% da base Ötima", ""],
    ["Ötima — Enviado", "3.651", "95,9% da base Ötima", ""],
    ["Ötima — Entregue", "3.105", "81,6% da base Ötima", ""],
    ["Ötima — Lido", "1.953", "51,3% da base Ötima", ""],
    ["Airys — Disparo", "3.804", "100% da base Airys", ""],
    ["Airys — Enviado", "707", "18,6% da base Airys", ""],
    ["Airys — Entregue", "678", "17,8% da base Airys", ""],
    ["Airys — Lido", "448", "11,8% da base Airys", ""],
  ];
  let ly = 4.0;
  const rowH = 0.29;
  linhas.forEach(([nome, valor, pct]) => {
    s.addShape("roundRect", {
      x: 0.7, y: ly, w: 11.95, h: rowH, rectRadius: 0.04,
      fill: { color: CARDBG }, line: { color: LINE, width: 1 },
    });
    s.addText(nome, { x: 1.0, y: ly, w: 3.2, h: rowH, fontFace: "Calibri", fontSize: 11, bold: true, color: INK, valign: "middle", margin: 0 });
    s.addText(valor, { x: 4.3, y: ly, w: 1.6, h: rowH, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(pct, { x: 6.0, y: ly, w: 4.0, h: rowH, fontFace: "Calibri", fontSize: 10.5, color: MUTED, valign: "middle", margin: 0 });
    ly += rowH + 0.045;
  });

  footer(s, pres, "Ötima e Airys são fornecedores/APIs distintos de WhatsApp, cada um com seu próprio arquivo de disparo e retorno — por isso a leitura é aberta por fornecedor antes de somar. Airys: só 707 dos 3.804 disparados têm retorno casado ao telefone da campanha (18,6%) — maior gargalo do canal.");
}

// =====================================================================
// SLIDE 3 — PRIORIDADE E GRUPO ESTRATÉGICO (base real do disparo)
// =====================================================================
slidePrioridadeGrupoEstrategico(pres, {
  titulo: "Base de disparo por Prioridade e Grupo Estratégico",
  subtitulo: "Composição dos 7.611 clientes únicos disparados via WhatsApp (Ötima + Airys) — base real do arquivo de disparo",
  linhasPrioridade: [
    ["P1 · Máxima", "1.485", "19,5%"],
    ["P2 · Alta", "2.004", "26,3%"],
    ["P3 · Média", "2.087", "27,4%"],
    ["P4 · Baixa", "2.035", "26,7%"],
  ],
  linhasGE: [
    ["Abandono Carrinho", "811", "10,7%"],
    ["Cadastrado", "7", "0,1%"],
    ["Engajado", "864", "11,4%"],
    ["Topo de Funil", "5.929", "77,9%"],
  ],
  total: "7.611",
  footerTexto: "Prioridade e Grupo Estratégico vêm do próprio arquivo de disparo (mesma base usada no funil) — cobertura de 100% dos 7.611 clientes únicos disparados.",
});

// =====================================================================
// SLIDE 4 — FUNIL COMPLETO CONSOLIDADO (8 etapas, com Lido)
// =====================================================================
slideFunilCompleto(pres, {
  titulo: "Funil completo — Disparo até Acordo",
  subtitulo: "Clientes únicos por etapa (Ötima + Airys) — % sobre a base de disparo e conversão etapa a etapa",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 7611, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 4358, pctDisparo: "57,3%", conv: "57,3%", drop: "42,7%", gargalo: true },
    { nome: "Entrega", icon: "check", valor: 3783, pctDisparo: "49,7%", conv: "86,8%", drop: "13,2%" },
    { nome: "Lido", icon: "eye", valor: 2401, pctDisparo: "31,5%", conv: "63,5%", drop: "36,5%" },
    { nome: "Home", icon: "home", valor: 191, pctDisparo: "2,51%", conv: "8,0%", drop: "92,0%" },
    { nome: "Auth", icon: "shield", valor: 174, pctDisparo: "2,29%", conv: "91,1%", drop: "8,9%" },
    { nome: "Oferta", icon: "tag", valor: 154, pctDisparo: "2,02%", conv: "88,5%", drop: "11,5%" },
    { nome: "Acordo", icon: "award", valor: 31, pctDisparo: "0,41%", conv: "20,1%", drop: "79,9%" },
  ],
  gargaloTitulo: "Maior gargalo: Disparo → Enviado",
  gargaloTexto: "— 42,7% dos disparos não confirmam envio, puxado quase todo pelo Airys (só 18,6% de sua base tem retorno casado ao telefone).",
  footerTexto: "% do disparo = etapa ÷ 7.611 clientes únicos disparados (Ötima + Airys). Conversão/drop calculados sobre a etapa anterior.",
});

// =====================================================================
// SLIDE 5 — FUNIL COMPLETO SÓ ÖTIMA
// =====================================================================
slideFunilCompleto(pres, {
  titulo: "Funil completo — WhatsApp Ötima",
  subtitulo: "Só o fornecedor Ötima — clientes únicos por etapa, % sobre a base de disparo Ötima",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 3807, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 3651, pctDisparo: "95,9%", conv: "95,9%", drop: "4,1%" },
    { nome: "Entrega", icon: "check", valor: 3105, pctDisparo: "81,6%", conv: "85,0%", drop: "15,0%" },
    { nome: "Lido", icon: "eye", valor: 1953, pctDisparo: "51,3%", conv: "62,9%", drop: "37,1%", gargalo: true },
    { nome: "Home", icon: "home", valor: 191, pctDisparo: "5,02%", conv: "9,8%", drop: "90,2%" },
    { nome: "Auth", icon: "shield", valor: 174, pctDisparo: "4,57%", conv: "91,1%", drop: "8,9%" },
    { nome: "Oferta", icon: "tag", valor: 154, pctDisparo: "4,05%", conv: "88,5%", drop: "11,5%" },
    { nome: "Acordo", icon: "award", valor: 30, pctDisparo: "0,79%", conv: "19,5%", drop: "80,5%" },
  ],
  gargaloTitulo: "Maior gargalo na Ötima: Lido → Home",
  gargaloTexto: "— 90,2% de quem leu a mensagem não avança para negociação no CRM. Praticamente todo o resultado de CRM do canal WhatsApp vem da Ötima.",
  footerTexto: "% do disparo = etapa ÷ 3.807 clientes únicos disparados via Ötima. Conversão/drop calculados sobre a etapa anterior.",
});

// =====================================================================
// SLIDE 6 — FUNIL COMPLETO SÓ AIRYS
// =====================================================================
slideFunilCompleto(pres, {
  titulo: "Funil completo — WhatsApp Airys",
  subtitulo: "Só o fornecedor Airys — clientes únicos por etapa, % sobre a base de disparo Airys",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 3804, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 707, pctDisparo: "18,6%", conv: "18,6%", drop: "81,4%", gargalo: true },
    { nome: "Entrega", icon: "check", valor: 678, pctDisparo: "17,8%", conv: "95,9%", drop: "4,1%" },
    { nome: "Lido", icon: "eye", valor: 448, pctDisparo: "11,8%", conv: "66,1%", drop: "33,9%" },
    { nome: "Home", icon: "home", valor: 1, pctDisparo: "0,03%", conv: "0,2%", drop: "99,8%" },
    { nome: "Auth", icon: "shield", valor: 1, pctDisparo: "0,03%", conv: "100%", drop: "0,0%" },
    { nome: "Oferta", icon: "tag", valor: 1, pctDisparo: "0,03%", conv: "100%", drop: "0,0%" },
    { nome: "Acordo", icon: "award", valor: 1, pctDisparo: "0,03%", conv: "100%", drop: "0,0%" },
  ],
  gargaloTitulo: "Maior gargalo na Airys: Disparo → Enviado",
  gargaloTexto: "— 81,4% dos disparos não têm retorno casado ao telefone da campanha; dos 707 que têm, o resultado de CRM é praticamente nulo (1 cliente até Acordo).",
  footerTexto: "% do disparo = etapa ÷ 3.804 clientes únicos disparados via Airys. Conversão/drop calculados sobre a etapa anterior.",
});

// =====================================================================
// SLIDE 7 — FUNIL SEGMENTADO POR PRIORIDADE
// =====================================================================
slideFunilSegmentado(pres, {
  titulo: "Funil completo por Prioridade",
  subtitulo: "As mesmas 8 etapas do funil geral (Ötima + Airys), abertas por Prioridade — clientes únicos e % etapa a etapa",
  colunaLabel: "PRIORIDADE",
  colunasEtapas: ["Disparo", "Enviado", "Entrega", "Lido", "Home", "Auth", "Oferta", "Acordo"],
  linhas: [
    ["P1 · Máxima", "1.485", ["1.027", "69%"], ["959", "93%"], ["572", "60%"], ["65", "11%"], ["60", "92%"], ["56", "93%"], ["9", "16%"], "0,61%"],
    ["P2 · Alta", "2.004", ["1.559", "78%"], ["1.434", "92%"], ["917", "64%"], ["19", "2%"], ["17", "89%"], ["14", "82%"], ["4", "29%"], "0,20%"],
    ["P3 · Média", "2.087", ["925", "44%"], ["764", "83%"], ["502", "66%"], ["27", "5%"], ["27", "100%"], ["24", "89%"], ["3", "12%"], "0,14%"],
    ["P4 · Baixa", "2.035", ["847", "42%"], ["626", "74%"], ["410", "65%"], ["20", "5%"], ["20", "100%"], ["18", "90%"], ["1", "6%"], "0,05%"],
    ["Não Classificado*", "—", ["—", "—"], ["—", "—"], ["—", "—"], ["60", "—"], ["50", "83%"], ["42", "84%"], ["14", "33%"], "—"],
  ],
  total: ["Total Geral", "7.611", ["4.358", "57%"], ["3.783", "87%"], ["2.401", "63%"], ["191", "8%"], ["174", "91%"], ["154", "89%"], ["31", "20%"], "0,41%"],
  insightTitulo: "P1 · Máxima converte melhor:",
  insightTexto: "0,61% de Disparo→Acordo contra 0,05%-0,20% nas demais prioridades classificadas — mesmo padrão observado no SMS.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo. *Não Classificado = ações de CRM cujo telefone não foi associado a uma Prioridade do arquivo de disparo (volume residual, sem Disparo/Enviado/Entrega/Lido correspondente nesta base).",
});

// =====================================================================
// SLIDE 8 — FUNIL SEGMENTADO POR GRUPO ESTRATÉGICO
// =====================================================================
slideFunilSegmentado(pres, {
  titulo: "Funil completo por Grupo Estratégico",
  subtitulo: "As mesmas 8 etapas do funil geral (Ötima + Airys), abertas por Grupo Estratégico — clientes únicos e % etapa a etapa",
  colunaLabel: "GRUPO ESTRATÉGICO",
  colunasEtapas: ["Disparo", "Enviado", "Entrega", "Lido", "Home", "Auth", "Oferta", "Acordo"],
  linhas: [
    ["Abandono Carrinho", "811", ["563", "69%"], ["515", "91%"], ["309", "60%"], ["84", "27%"], ["81", "96%"], ["79", "98%"], ["1", "1%"], "0,12%"],
    ["Cadastrado", "7", ["0", "0%"], ["0", "—"], ["0", "—"], ["0", "—"], ["0", "—"], ["0", "—"], ["0", "—"], "0,00%"],
    ["Engajado", "864", ["591", "68%"], ["557", "94%"], ["339", "61%"], ["30", "9%"], ["28", "93%"], ["20", "71%"], ["12", "60%"], "1,39%"],
    ["Topo de Funil", "5.929", ["3.204", "54%"], ["2.711", "85%"], ["1.753", "65%"], ["17", "1%"], ["15", "88%"], ["13", "87%"], ["4", "31%"], "0,07%"],
    ["Não Classificado*", "—", ["—", "—"], ["—", "—"], ["—", "—"], ["60", "—"], ["50", "83%"], ["42", "84%"], ["14", "33%"], "—"],
  ],
  total: ["Total Geral", "7.611", ["4.358", "57%"], ["3.783", "87%"], ["2.401", "63%"], ["191", "8%"], ["174", "91%"], ["154", "89%"], ["31", "20%"], "0,41%"],
  insightTitulo: "Engajado converte muito acima da média:",
  insightTexto: "1,39% de Disparo→Acordo contra 0,00%-0,12% nos demais grupos classificados — o público que já teve engajamento prévio responde muito melhor.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo. *Não Classificado = ações de CRM cujo telefone não foi associado a um Grupo Estratégico do arquivo de disparo (volume residual, sem Disparo/Enviado/Entrega/Lido correspondente nesta base).",
});

// =====================================================================
// SLIDE 9 — CUSTO DO CANAL
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Custo do canal WhatsApp", {
    x: 0.7, y: 0.5, w: 9, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Bases de cobrança distintas por fornecedor — ambos cobram por mensagem ENTREGUE", {
    x: 0.7, y: 1.08, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  s.addShape("roundRect", {
    x: 0.7, y: 1.5, w: 5.85, h: 0.65, rectRadius: 0.08,
    fill: { color: CARDBG }, line: { color: LINE, width: 1 },
  });
  s.addText([
    { text: "3.105", options: { bold: true, color: NAVY, fontSize: 13.5 } },
    { text: " entregues Ötima × ", options: { color: MUTED, fontSize: 10.5 } },
    { text: "R$ 0,0685", options: { bold: true, color: NAVY, fontSize: 13.5 } },
    { text: " = ", options: { color: MUTED, fontSize: 10.5 } },
    { text: "R$ 212,69", options: { bold: true, color: GREEN, fontSize: 15 } },
  ], { x: 0.9, y: 1.5, w: 5.5, h: 0.65, fontFace: "Calibri", valign: "middle", margin: 0 });

  s.addShape("roundRect", {
    x: 6.8, y: 1.5, w: 5.85, h: 0.65, rectRadius: 0.08,
    fill: { color: CARDBG }, line: { color: LINE, width: 1 },
  });
  s.addText([
    { text: "678", options: { bold: true, color: NAVY, fontSize: 13.5 } },
    { text: " entregues Airys × ", options: { color: MUTED, fontSize: 10.5 } },
    { text: "R$ 0,0500", options: { bold: true, color: NAVY, fontSize: 13.5 } },
    { text: " = ", options: { color: MUTED, fontSize: 10.5 } },
    { text: "R$ 33,90", options: { bold: true, color: GREEN, fontSize: 15 } },
  ], { x: 7.0, y: 1.5, w: 5.5, h: 0.65, fontFace: "Calibri", valign: "middle", margin: 0 });

  statCard(s, 0.7, 2.25, 3.85, 1.3, {
    icon: "icon_dollar_1E2761.png", value: "R$ 246,59", valueSize: 19,
    label: "Custo total WhatsApp (Ötima + Airys, cobrado por entregue)",
  });
  statCard(s, 4.75, 2.25, 3.85, 1.3, {
    icon: "icon_percent_E8622C.png", value: "3,1%", valueSize: 23, valueColor: ORANGE,
    label: "Participação do WhatsApp no investimento total do período",
  });
  statCard(s, 8.8, 2.25, 3.85, 1.3, {
    icon: "icon_award_2F9E6E.png", value: "R$ 7,95", valueSize: 21, valueColor: GREEN,
    label: "Custo médio por Acordo gerado via WhatsApp",
  });

  s.addText("Custo por resultado (custo total WhatsApp ÷ volume da etapa)", {
    x: 0.7, y: 3.7, w: 10, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, margin: 0,
  });

  const custos = [
    ["Por cliente disparado", "R$ 0,03"],
    ["Por cliente entregue", "R$ 0,07"],
    ["Por chegada na Home", "R$ 1,29"],
    ["Por Oferta apresentada", "R$ 1,60"],
    ["Por Acordo fechado", "R$ 7,95"],
  ];
  const cw = 2.31, cx0 = 0.7, cy = 4.05, ch = 0.8;
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
    x: 0.7, y: 4.95, w: 8, h: 0.3, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, margin: 0,
  });
  slideInvestimentoTotal(s, {
    x: 0.7, y: 5.28, w: 8.05,
    linhas: [
      ["SMS (Kolmeya)", "R$ 5.036,38", "63,9%"],
      ["RCS (Ötima)", "R$ 753,48", "9,6%"],
      ["WhatsApp (Ötima + Airys)", "R$ 246,59", "3,1%"],
      ["Lemit — enriquecimento de dados (julho)", "R$ 1.851,04", "23,5%"],
    ],
    total: "R$ 7.887,49",
  });

  footer(s, pres, "Email ainda sem custo unitário confirmado — não entra no investimento total conhecido.");
}

// =====================================================================
// SLIDE 10 — VISÃO EXECUTIVA
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Visão executiva — WhatsApp", {
    x: 0.7, y: 0.5, w: 9, h: 0.55, fontFace: "Cambria", fontSize: 28, bold: true, color: WHITE, margin: 0,
  });
  s.addText("O que essa análise já responde", {
    x: 0.7, y: 1.05, w: 9, h: 0.35, fontFace: "Calibri", fontSize: 13, color: ICE, margin: 0,
  });

  const perguntas = [
    ["Clientes disparados", "7.611 (Ötima + Airys)"],
    ["WhatsApp entregues", "3.783 (49,7%)"],
    ["Taxa de entrega", "49,7% dos disparos"],
    ["Taxa de leitura", "31,5% dos disparos (63,5% dos entregues)"],
    ["Conversão Home → Auth", "91,1%"],
    ["Conversão Auth → Oferta", "88,5%"],
    ["Conversão Oferta → Acordo", "20,1%"],
    ["Conversão total Disparo → Acordo", "0,41%"],
    ["Acordos gerados", "31"],
    ["Custo total do WhatsApp", "R$ 246,59"],
    ["Custo médio por Acordo", "R$ 7,95"],
    ["Maior gargalo", "Disparo → Enviado (-42,7%, quase todo Airys)"],
  ];

  const cols = 3, rows = 4, cw = 3.85, ch = 1.15, x0 = 0.7, y0 = 1.6, gx = 0.15, gy = 0.15;
  perguntas.forEach(([pergunta, resposta], i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
    const isGargalo = pergunta === "Maior gargalo";
    s.addShape("roundRect", {
      x, y, w: cw, h: ch, rectRadius: 0.08,
      fill: { color: isGargalo ? ORANGE : "2A3572" },
      line: { type: "none" },
    });
    s.addText(pergunta, {
      x: x + 0.2, y: y + 0.14, w: cw - 0.4, h: 0.4, fontFace: "Calibri", fontSize: 11.5,
      color: isGargalo ? "FDEDE4" : ICE, align: "left", valign: "top", margin: 0,
    });
    s.addText(resposta, {
      x: x + 0.2, y: y + 0.5, w: cw - 0.4, h: 0.55, fontFace: "Calibri", fontSize: 15, bold: true,
      color: WHITE, align: "left", valign: "top", margin: 0,
    });
  });

  s.addText("Nota: WhatsApp foi disparado em uma única janela (28-29/07) neste recorte — não há dado de agosto para abrir por mês, ao contrário do SMS.", {
    x: 0.7, y: 6.95, w: 11.9, h: 0.35, fontFace: "Calibri", fontSize: 12, italic: true,
    color: "8FA3D9", margin: 0,
  });
}

pres.writeFile({ fileName: "casas_bahia_whatsapp.pptx" }).then(() => console.log("done"));
