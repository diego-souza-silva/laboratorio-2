const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, statCard, makeFooter, tabelaDinamica,
  makeSlidePrioridadeGrupoEstrategico, makeSlideFunilCompleto, slideCapa,
  makeSlideFunilSegmentado, slideInvestimentoTotal,
} = require("./lib.js");

const footer = makeFooter("RCS");
const slidePrioridadeGrupoEstrategico = makeSlidePrioridadeGrupoEstrategico(footer);
const slideFunilCompleto = makeSlideFunilCompleto(footer);
const slideFunilSegmentado = makeSlideFunilSegmentado(footer);

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "CAPÍTULO 3 · CANAL",
  titulo: "RCS",
  subtitulo: "Resultados Casas Bahia — jornada completa do disparo ao acordo",
  periodo: "Período analisado: 04/08  ·  Fornecedor: Ötima",
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
  s.addText("Disparos totais x clientes únicos — sem duplicidade inflando o volume", {
    x: 0.7, y: 1.08, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  statCard(s, 0.7, 1.75, 3.85, 2.05, {
    icon: "icon_send_1E2761.png", value: "8.372", valueSize: 40,
    label: "RCS disparados no total (eventos)",
  });
  statCard(s, 4.75, 1.75, 3.85, 2.05, {
    icon: "icon_check_1E2761.png", value: "8.372", valueSize: 40,
    label: "Clientes únicos disparados (telefones distintos)",
  });
  statCard(s, 8.8, 1.75, 3.85, 2.05, {
    icon: "icon_percent_1E2761.png", value: "1,00", valueSize: 40,
    label: "SPIN — disparos por cliente único",
  });

  s.addText("Jornada de entrega", {
    x: 0.7, y: 4.05, w: 6, h: 0.4, fontFace: "Calibri", fontSize: 16, bold: true, color: NAVY, margin: 0,
  });

  const linhas = [
    ["Enviado", "8.372", "100% dos disparos", "8.372 clientes únicos"],
    ["Entregue", "5.533", "66,1% dos disparos", "5.533 clientes únicos"],
    ["Lido", "390", "4,7% dos disparos", "390 clientes únicos"],
  ];
  let ly = 4.55;
  linhas.forEach(([nome, valor, pct, uni]) => {
    s.addShape("roundRect", {
      x: 0.7, y: ly, w: 11.95, h: 0.72, rectRadius: 0.06,
      fill: { color: CARDBG }, line: { color: LINE, width: 1 },
    });
    s.addText(nome, { x: 1.0, y: ly, w: 2.3, h: 0.72, fontFace: "Calibri", fontSize: 14, bold: true, color: INK, valign: "middle", margin: 0 });
    s.addText(valor, { x: 3.3, y: ly, w: 2.0, h: 0.72, fontFace: "Calibri", fontSize: 18, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(pct, { x: 5.5, y: ly, w: 3.2, h: 0.72, fontFace: "Calibri", fontSize: 13, color: MUTED, valign: "middle", margin: 0 });
    s.addText(uni, { x: 8.9, y: ly, w: 3.5, h: 0.72, fontFace: "Calibri", fontSize: 13, color: MUTED, valign: "middle", margin: 0 });
    ly += 0.87;
  });

  footer(s, pres, "Base: campanhas RCS/Ötima disparadas em 04/08 · disparo/retorno próprios (Ötima) · sem cruzamento de CRM nesta etapa.");
}

// =====================================================================
// SLIDE 3 — PRIORIDADE E GRUPO ESTRATÉGICO (base real do disparo)
// =====================================================================
slidePrioridadeGrupoEstrategico(pres, {
  titulo: "Base de disparo por Prioridade e Grupo Estratégico",
  subtitulo: "Composição dos 8.372 clientes únicos disparados via RCS — base real do arquivo de disparo",
  linhasPrioridade: [
    ["P1 · Máxima", "16", "0,2%"],
    ["P2 · Alta", "3.309", "39,5%"],
    ["P3 · Média", "2.887", "34,5%"],
    ["P4 · Baixa", "2.160", "25,8%"],
  ],
  linhasGE: [
    ["Abandono Carrinho", "53", "0,6%"],
    ["Engajado", "133", "1,6%"],
    ["Topo de Funil", "8.144", "97,3%"],
    ["Não Classificado", "42", "0,5%"],
  ],
  total: "8.372",
  footerTexto: "Prioridade e Grupo Estratégico vêm do próprio arquivo de disparo (mesma base usada no funil) — cobertura de 100% dos 8.372 clientes únicos disparados.",
});

// =====================================================================
// SLIDE 4 — FUNIL COMPLETO (8 etapas, com Lido)
// =====================================================================
slideFunilCompleto(pres, {
  titulo: "Funil completo — Disparo até Acordo",
  subtitulo: "Clientes únicos por etapa — % sobre a base de disparo e conversão etapa a etapa",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 8372, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 8372, pctDisparo: "100%", conv: "100%", drop: "0,0%" },
    { nome: "Entrega", icon: "check", valor: 5533, pctDisparo: "66,1%", conv: "66,1%", drop: "33,9%", gargalo: true },
    { nome: "Lido", icon: "eye", valor: 390, pctDisparo: "4,7%", conv: "7,0%", drop: "93,0%" },
    { nome: "Home", icon: "home", valor: 2, pctDisparo: "0,02%", conv: "0,5%", drop: "99,5%" },
    { nome: "Auth", icon: "shield", valor: 2, pctDisparo: "0,02%", conv: "100%", drop: "0,0%" },
    { nome: "Oferta", icon: "tag", valor: 2, pctDisparo: "0,02%", conv: "100%", drop: "0,0%" },
    { nome: "Acordo", icon: "award", valor: 4, pctDisparo: "0,05%", conv: "200%", drop: "-100%" },
  ],
  gargaloTitulo: "Maior gargalo: Entrega → Lido",
  gargaloTexto: "— 93,0% das entregas não geram leitura confirmada; Acordo (4) > Oferta (2) porque a ação de CRM não é estritamente sequencial por cliente na janela analisada.",
  footerTexto: "% do disparo = etapa ÷ 8.372 clientes únicos disparados. Conversão/drop calculados sobre a etapa anterior. Enviado = Disparo porque o RCS Ötima confirma envio para 100% da base neste recorte.",
});

// =====================================================================
// SLIDE 5 — FUNIL SEGMENTADO POR PRIORIDADE
// =====================================================================
slideFunilSegmentado(pres, {
  titulo: "Funil completo por Prioridade",
  subtitulo: "As mesmas 8 etapas do funil geral, abertas por Prioridade — clientes únicos e % etapa a etapa",
  colunaLabel: "PRIORIDADE",
  colunasEtapas: ["Disparo", "Enviado", "Entrega", "Lido", "Home", "Auth", "Oferta", "Acordo"],
  linhas: [
    ["P1 · Máxima", "16", ["16", "100%"], ["7", "44%"], ["0", "0%"], ["0", "—"], ["0", "—"], ["0", "—"], ["0", "—"], "0,00%"],
    ["P2 · Alta", "3.309", ["3.309", "100%"], ["2.383", "72%"], ["169", "7%"], ["0", "0%"], ["0", "—"], ["0", "—"], ["2", "—"], "0,06%"],
    ["P3 · Média", "2.887", ["2.887", "100%"], ["1.889", "65%"], ["131", "7%"], ["1", "1%"], ["1", "100%"], ["1", "100%"], ["0", "0%"], "0,00%"],
    ["P4 · Baixa", "2.160", ["2.160", "100%"], ["1.254", "58%"], ["90", "7%"], ["0", "0%"], ["0", "—"], ["0", "—"], ["2", "—"], "0,09%"],
    ["Não Classificado*", "—", ["—", "—"], ["—", "—"], ["—", "—"], ["1", "—"], ["1", "100%"], ["1", "100%"], ["0", "0%"], "—"],
  ],
  total: ["Total Geral", "8.372", ["8.372", "100%"], ["5.533", "66%"], ["390", "7%"], ["2", "1%"], ["2", "100%"], ["2", "100%"], ["4", "200%"], "0,05%"],
  insightTitulo: "Volume de CRM é baixo demais para conclusão estatística:",
  insightTexto: "só 2 clientes chegam à Home no total — os 4 acordos vêm de P2 e P4, sem nenhum Home/Auth/Oferta associado nessas prioridades (ação de CRM não sequencial na janela).",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo. *Não Classificado = ação de CRM cujo telefone não foi associado a uma Prioridade do arquivo de disparo (volume residual).",
});

// =====================================================================
// SLIDE 6 — FUNIL SEGMENTADO POR GRUPO ESTRATÉGICO
// =====================================================================
slideFunilSegmentado(pres, {
  titulo: "Funil completo por Grupo Estratégico",
  subtitulo: "As mesmas 8 etapas do funil geral, abertas por Grupo Estratégico — clientes únicos e % etapa a etapa",
  colunaLabel: "GRUPO ESTRATÉGICO",
  colunasEtapas: ["Disparo", "Enviado", "Entrega", "Lido", "Home", "Auth", "Oferta", "Acordo"],
  linhas: [
    ["Abandono Carrinho", "53", ["53", "100%"], ["40", "75%"], ["12", "30%"], ["0", "0%"], ["0", "—"], ["0", "—"], ["0", "—"], "0,00%"],
    ["Engajado", "133", ["133", "100%"], ["88", "66%"], ["8", "9%"], ["0", "0%"], ["0", "—"], ["0", "—"], ["1", "—"], "0,75%"],
    ["Topo de Funil", "8.144", ["8.144", "100%"], ["5.373", "66%"], ["365", "7%"], ["1", "0%"], ["1", "100%"], ["1", "100%"], ["3", "300%"], "0,04%"],
    ["Não Classificado", "42", ["42", "100%"], ["32", "76%"], ["5", "16%"], ["1", "20%"], ["1", "100%"], ["1", "100%"], ["0", "0%"], "0,00%"],
  ],
  total: ["Total Geral", "8.372", ["8.372", "100%"], ["5.533", "66%"], ["390", "7%"], ["2", "1%"], ["2", "100%"], ["2", "100%"], ["4", "200%"], "0,05%"],
  insightTitulo: "Engajado converte melhor, mas com volume mínimo:",
  insightTexto: "0,75% de Disparo→Acordo (1 acordo em 133 disparos) — Topo de Funil concentra 97,3% da base e responde pela maior parte do resultado bruto.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo.",
});

// =====================================================================
// SLIDE 7 — CUSTO DO CANAL
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Custo do canal RCS", {
    x: 0.7, y: 0.5, w: 9, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Base de cobrança Ötima: por RCS Disparado — R$ 0,0900 / unidade", {
    x: 0.7, y: 1.08, w: 10, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  s.addShape("roundRect", {
    x: 0.7, y: 1.5, w: 11.95, h: 0.65, rectRadius: 0.08,
    fill: { color: CARDBG }, line: { color: LINE, width: 1 },
  });
  s.addText([
    { text: "8.372", options: { bold: true, color: NAVY, fontSize: 16 } },
    { text: "  RCS disparados   ×   ", options: { color: MUTED, fontSize: 12 } },
    { text: "R$ 0,0900", options: { bold: true, color: NAVY, fontSize: 16 } },
    { text: "  custo unitário   =   ", options: { color: MUTED, fontSize: 12 } },
    { text: "R$ 753,48", options: { bold: true, color: GREEN, fontSize: 18 } },
  ], {
    x: 1.0, y: 1.5, w: 11.4, h: 0.65, fontFace: "Calibri", valign: "middle", align: "left", margin: 0,
  });

  statCard(s, 0.7, 2.25, 3.85, 1.3, {
    icon: "icon_dollar_1E2761.png", value: "R$ 753,48", valueSize: 19,
    label: "Custo total do RCS",
  });
  statCard(s, 4.75, 2.25, 3.85, 1.3, {
    icon: "icon_percent_E8622C.png", value: "9,6%", valueSize: 23, valueColor: ORANGE,
    label: "Participação do RCS no investimento total do período",
  });
  statCard(s, 8.8, 2.25, 3.85, 1.3, {
    icon: "icon_award_2F9E6E.png", value: "R$ 188,37", valueSize: 20, valueColor: GREEN,
    label: "Custo médio por Acordo gerado via RCS",
  });

  s.addText("Custo por resultado (custo total RCS ÷ volume da etapa)", {
    x: 0.7, y: 3.7, w: 8, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, margin: 0,
  });

  const custos = [
    ["Por cliente disparado", "R$ 0,09"],
    ["Por cliente entregue", "R$ 0,14"],
    ["Por chegada na Home", "R$ 376,74"],
    ["Por Oferta apresentada", "R$ 376,74"],
    ["Por Acordo fechado", "R$ 188,37"],
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
      x: x + 0.15, y: cy + 0.1, w: cw - 0.3, h: 0.42, fontFace: "Calibri", fontSize: 14, bold: true,
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

  footer(s, pres, "Custo unitário confirmado: R$ 0,0900 por RCS disparado (cobrança Ötima independe de entrega/leitura). Email ainda sem custo unitário confirmado — não entra no investimento total conhecido.");
}

// =====================================================================
// SLIDE 8 — VISÃO EXECUTIVA
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Visão executiva — RCS", {
    x: 0.7, y: 0.5, w: 9, h: 0.55, fontFace: "Cambria", fontSize: 28, bold: true, color: WHITE, margin: 0,
  });
  s.addText("O que essa análise já responde", {
    x: 0.7, y: 1.05, w: 9, h: 0.35, fontFace: "Calibri", fontSize: 13, color: ICE, margin: 0,
  });

  const perguntas = [
    ["Clientes impactados", "8.372 clientes únicos"],
    ["RCS entregues", "5.533 (66,1%)"],
    ["Taxa de entrega", "66,1% dos disparos"],
    ["Taxa de leitura", "4,7% dos disparos"],
    ["Conversão Home → Auth", "100%  (2 de 2, volume muito baixo)"],
    ["Conversão Auth → Oferta", "100%  (2 de 2, volume muito baixo)"],
    ["Conversão Oferta → Acordo", "200%  (4 acordos sobre 2 ofertas — não sequencial)"],
    ["Conversão total Disparo → Acordo", "0,05%"],
    ["Acordos gerados", "4"],
    ["Custo total do RCS", "R$ 753,48"],
    ["Custo médio por Acordo", "R$ 188,37"],
    ["Maior gargalo", "Entrega → Lido (-93,0%)"],
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
      x: x + 0.2, y: y + 0.14, w: cw - 0.4, h: 0.4, fontFace: "Calibri", fontSize: 11,
      color: isGargalo ? "FDEDE4" : ICE, align: "left", valign: "top", margin: 0,
    });
    s.addText(resposta, {
      x: x + 0.2, y: y + 0.5, w: cw - 0.4, h: 0.55, fontFace: "Calibri", fontSize: 14, bold: true,
      color: WHITE, align: "left", valign: "top", margin: 0,
    });
  });

  s.addText("Nota: volume de CRM (Home/Auth/Oferta/Acordo) é muito baixo (≤4 clientes por etapa) — leia os percentuais com cautela, um único cliente já muda vários pontos percentuais. RCS foi disparado em uma única data (04/08), sem recorte mensal possível.", {
    x: 0.7, y: 6.85, w: 11.9, h: 0.5, fontFace: "Calibri", fontSize: 11.5, italic: true,
    color: "8FA3D9", margin: 0,
  });
}

pres.writeFile({ fileName: "casas_bahia_rcs.pptx" }).then(() => console.log("done"));
