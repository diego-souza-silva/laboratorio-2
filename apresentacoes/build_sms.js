const pptxgen = require("pptxgenjs");

// ---------- paleta ----------
const NAVY = "1E2761";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const ORANGE = "E8622C"; // alerta / gargalo
const GREEN = "2F9E6E";  // positivo / acordo
const INK = "1C2B39";
const MUTED = "6B7A8D";
const CARDBG = "F7F9FC";
const LINE = "E2E8F0";

function newPres() {
  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  return p;
}

function statCard(slide, x, y, w, h, opts) {
  slide.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.bg || CARDBG },
    line: { color: LINE, width: 1 },
    shadow: { type: "outer", color: "1E2761", opacity: 0.08, blur: 6, offset: 2, angle: 90 },
  });
  if (opts.icon) {
    slide.addImage({ path: opts.icon, x: x + 0.22, y: y + 0.2, w: 0.34, h: 0.34 });
  }
  slide.addText(opts.value, {
    x: x + 0.22, y: y + (opts.icon ? 0.55 : 0.2), w: w - 0.44, h: h - 0.9,
    fontFace: "Calibri", fontSize: opts.valueSize || 30, bold: true,
    color: opts.valueColor || NAVY, align: "left", valign: "top", margin: 0,
  });
  slide.addText(opts.label, {
    x: x + 0.22, y: y + h - 0.42, w: w - 0.44, h: 0.34,
    fontFace: "Calibri", fontSize: 11, color: MUTED, align: "left", valign: "top", margin: 0,
  });
}

function footer(slide, pres, text) {
  slide.addText(text, {
    x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: "Calibri", fontSize: 9,
    color: MUTED, align: "left", margin: 0,
  });
  slide.addText("Casas Bahia · Canal SMS", {
    x: 11.0, y: 7.12, w: 2.3, h: 0.3, fontFace: "Calibri", fontSize: 9,
    color: MUTED, align: "right", margin: 0,
  });
}

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("CAPÍTULO 1 · CANAL", {
    x: 0.9, y: 1.55, w: 6, h: 0.4, fontFace: "Calibri", fontSize: 14,
    color: ICE, bold: true, charSpacing: 3, margin: 0,
  });
  s.addText("SMS", {
    x: 0.85, y: 1.9, w: 8, h: 1.3, fontFace: "Cambria", fontSize: 64,
    color: WHITE, bold: true, margin: 0,
  });
  s.addText("Resultados Casas Bahia — jornada completa do disparo ao acordo", {
    x: 0.9, y: 3.15, w: 8.5, h: 0.6, fontFace: "Calibri", fontSize: 18,
    color: ICE, margin: 0,
  });
  s.addText("Período analisado: 25/07 a 15/08  ·  Fornecedor: Kolmeya  ·  30 campanhas", {
    x: 0.9, y: 3.75, w: 8.5, h: 0.4, fontFace: "Calibri", fontSize: 13,
    color: "8FA3D9", margin: 0,
  });

  // faixa de etapas do funil como motivo visual
  const etapas = ["Disparo", "Entrega", "Home", "Auth", "Oferta", "Acordo"];
  const startX = 0.9, gap = 1.95, boxW = 1.65, y = 5.35;
  etapas.forEach((et, i) => {
    const x = startX + i * gap;
    s.addShape("roundRect", {
      x, y, w: boxW, h: 0.62, rectRadius: 0.31,
      fill: { color: i === etapas.length - 1 ? GREEN : "2A3572" },
      line: { type: "none" },
    });
    s.addText(et, {
      x, y, w: boxW, h: 0.62, fontFace: "Calibri", fontSize: 12.5, bold: true,
      color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    if (i < etapas.length - 1) {
      s.addText("›", {
        x: x + boxW, y: y - 0.03, w: gap - boxW, h: 0.62, fontFace: "Arial",
        fontSize: 20, color: "6E7DC2", align: "center", valign: "middle", margin: 0,
      });
    }
  });

  s.addText("Dash de Resultados por Carteiras · Carteira: Casas Bahia", {
    x: 0.9, y: 6.85, w: 8, h: 0.3, fontFace: "Calibri", fontSize: 10,
    color: "6E7DC2", margin: 0,
  });
}

// =====================================================================
// SLIDE 2 — VOLUMETRIA (função reutilizável — consolidado + por mês)
// =====================================================================
function slideVolumetria(pres, { titulo, subtitulo, disparado, unicos, spin, linhas, footerTexto }) {
  const s = pres.addSlide();
  s.addText(titulo, {
    x: 0.7, y: 0.5, w: 9, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText(subtitulo, {
    x: 0.7, y: 1.08, w: 10, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  // duas colunas grandes: disparos totais vs clientes unicos
  statCard(s, 0.7, 1.75, 3.85, 2.05, {
    icon: "icon_send_1E2761.png", value: disparado, valueSize: 40,
    label: "SMS disparados no total (eventos)",
  });
  statCard(s, 4.75, 1.75, 3.85, 2.05, {
    icon: "icon_check_1E2761.png", value: unicos, valueSize: 40,
    label: "Clientes únicos disparados (telefones distintos)",
  });
  statCard(s, 8.8, 1.75, 3.85, 2.05, {
    icon: "icon_percent_1E2761.png", value: spin, valueSize: 40,
    label: "SPIN — disparos por cliente único",
  });

  s.addText("Jornada de entrega", {
    x: 0.7, y: 4.05, w: 6, h: 0.4, fontFace: "Calibri", fontSize: 16, bold: true, color: NAVY, margin: 0,
  });

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

  footer(s, pres, footerTexto);
}

slideVolumetria(pres, {
  titulo: "Volumetria do disparo",
  subtitulo: "Disparos totais x clientes únicos — sem duplicidade inflando o volume",
  disparado: "92.406", unicos: "34.264", spin: "2,70",
  linhas: [
    ["Enviado", "81.232", "87,9% dos disparos", "31.089 clientes únicos"],
    ["Entregue", "70.985", "76,8% dos disparos", "26.370 clientes únicos"],
    ["Falhou", "4.271", "4,6% dos disparos", "—"],
  ],
  footerTexto: "Base: 30 campanhas SMS/Kolmeya · disparo/retorno próprios (Kolmeya) · sem cruzamento de CRM nesta etapa.",
});

slideVolumetria(pres, {
  titulo: "Volumetria do disparo — Julho",
  subtitulo: "Mesma leitura do consolidado, restrita a 25/07–31/07 (data pela campanha)",
  disparado: "8.024", unicos: "8.007", spin: "1,00",
  linhas: [
    ["Enviado", "7.456", "92,9% dos disparos", "7.442 clientes únicos"],
    ["Entregue", "6.141", "76,5% dos disparos", "6.127 clientes únicos"],
    ["Falhou", "836", "10,4% dos disparos", "—"],
  ],
  footerTexto: "Base: 4 campanhas SMS/Kolmeya de julho · disparo/retorno próprios (Kolmeya) · sem cruzamento de CRM nesta etapa.",
});

slideVolumetria(pres, {
  titulo: "Volumetria do disparo — Agosto",
  subtitulo: "Mesma leitura do consolidado, restrita a 01/08–15/08 (data pela campanha)",
  disparado: "84.382", unicos: "31.991", spin: "2,64",
  linhas: [
    ["Enviado", "73.776", "87,4% dos disparos", "28.494 clientes únicos"],
    ["Entregue", "64.844", "76,8% dos disparos", "24.471 clientes únicos"],
    ["Falhou", "3.435", "4,1% dos disparos", "—"],
  ],
  footerTexto: "Base: 26 campanhas SMS/Kolmeya de agosto · disparo/retorno próprios (Kolmeya) · sem cruzamento de CRM nesta etapa.",
});

// =====================================================================
// SLIDE 2B — PRIORIDADE E GRUPO ESTRATÉGICO (tabela dinâmica, estilo planilha)
// =====================================================================
function tabelaDinamica(s, { x, y, w, titulo, linhas, total }) {
  const headerFill = NAVY;
  const totalFill = "D6E6F5";
  const rows = [];

  rows.push([
    { text: titulo, options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 12, align: "left" } },
    { text: "Clientes", options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 12, align: "right" } },
    { text: "%", options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 12, align: "right" } },
  ]);

  linhas.forEach(([nome, valor, pct], i) => {
    const bg = i % 2 === 0 ? WHITE : CARDBG;
    rows.push([
      { text: nome, options: { fill: { color: bg }, color: INK, fontSize: 11.5, align: "left" } },
      { text: valor, options: { fill: { color: bg }, color: INK, fontSize: 11.5, align: "right" } },
      { text: pct, options: { fill: { color: bg }, color: MUTED, fontSize: 11.5, align: "right" } },
    ]);
  });

  rows.push([
    { text: "Total Geral", options: { fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 11.5, align: "left" } },
    { text: total, options: { fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 11.5, align: "right" } },
    { text: "100%", options: { fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 11.5, align: "right" } },
  ]);

  s.addTable(rows, {
    x, y, w,
    colW: [w - 2.0, 1.15, 0.85],
    rowH: 0.36,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri",
    autoPage: false,
    valign: "middle",
  });
}

function slidePrioridadeGrupoEstrategico(pres, { titulo, subtitulo, linhasPrioridade, linhasGE, total, footerTexto }) {
  const s = pres.addSlide();
  s.addText(titulo, {
    x: 0.7, y: 0.5, w: 12.4, h: 0.55, fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, margin: 0,
  });
  s.addText(subtitulo, {
    x: 0.7, y: 1.1, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  tabelaDinamica(s, { x: 0.7, y: 1.75, w: 5.6, titulo: "PRIORIDADE", linhas: linhasPrioridade, total });
  tabelaDinamica(s, { x: 6.75, y: 1.75, w: 5.9, titulo: "GRUPO ESTRATÉGICO", linhas: linhasGE, total });

  footer(s, pres, footerTexto);
}

slidePrioridadeGrupoEstrategico(pres, {
  titulo: "Base de disparo por Prioridade e Grupo Estratégico",
  subtitulo: "Composição dos 34.264 clientes únicos disparados via SMS — mesma base do funil",
  linhasPrioridade: [
    ["P1 · Máxima", "7.884", "23,0%"],
    ["P2 · Alta", "8.009", "23,4%"],
    ["P3 · Média", "6.729", "19,6%"],
    ["P4 · Baixa", "6.461", "18,9%"],
    ["Não Classificado", "5.181", "15,1%"],
  ],
  linhasGE: [
    ["Abandono Carrinho", "4.227", "12,3%"],
    ["Cadastrado", "26", "0,1%"],
    ["Engajado", "4.933", "14,4%"],
    ["Topo de Funil", "19.897", "58,1%"],
    ["Não Classificado", "5.181", "15,1%"],
  ],
  total: "34.264",
  footerTexto: "Prioridade = segmentação de propensão (antigo \"Grupo AB\"). Grupo Estratégico = origem/audiência do disparo. \"Clientes\" = telefones únicos (a base não traz CPF; contagem equivalente por telefone).",
});

slidePrioridadeGrupoEstrategico(pres, {
  titulo: "Base de disparo por Prioridade e Grupo Estratégico — Julho",
  subtitulo: "Composição dos 8.007 clientes únicos disparados via SMS em julho (data pela campanha)",
  linhasPrioridade: [
    ["P1 · Máxima", "1.462", "18,3%"],
    ["P2 · Alta", "1.516", "18,9%"],
    ["P3 · Média", "1.496", "18,7%"],
    ["P4 · Baixa", "1.467", "18,3%"],
    ["Não Classificado", "2.066", "25,8%"],
  ],
  linhasGE: [
    ["Abandono Carrinho", "860", "10,7%"],
    ["Cadastrado", "5", "0,1%"],
    ["Engajado", "882", "11,0%"],
    ["Topo de Funil", "4.194", "52,4%"],
    ["Não Classificado", "2.066", "25,8%"],
  ],
  total: "8.007",
  footerTexto: "Prioridade = segmentação de propensão (antigo \"Grupo AB\"). Grupo Estratégico = origem/audiência do disparo. \"Clientes\" = telefones únicos disparados em julho.",
});

slidePrioridadeGrupoEstrategico(pres, {
  titulo: "Base de disparo por Prioridade e Grupo Estratégico — Agosto",
  subtitulo: "Composição dos 31.991 clientes únicos disparados via SMS em agosto (data pela campanha)",
  linhasPrioridade: [
    ["P1 · Máxima", "7.684", "24,0%"],
    ["P2 · Alta", "7.745", "24,2%"],
    ["P3 · Média", "6.508", "20,3%"],
    ["P4 · Baixa", "6.328", "19,8%"],
    ["Não Classificado", "3.726", "11,6%"],
  ],
  linhasGE: [
    ["Abandono Carrinho", "4.095", "12,8%"],
    ["Cadastrado", "24", "0,1%"],
    ["Engajado", "4.825", "15,1%"],
    ["Topo de Funil", "19.321", "60,4%"],
    ["Não Classificado", "3.726", "11,6%"],
  ],
  total: "31.991",
  footerTexto: "Prioridade = segmentação de propensão (antigo \"Grupo AB\"). Grupo Estratégico = origem/audiência do disparo. \"Clientes\" = telefones únicos disparados em agosto.",
});

// =====================================================================
// SLIDE(S) — FUNIL SEGMENTADO (mesmas 7 etapas do funil completo, uma linha
// por categoria de Prioridade ou Grupo Estratégico — tabela, não barra, pra
// caber as 5 categorias × 7 etapas numa leitura só)
// =====================================================================
// Célula de etapa: valor grande (conversão da etapa anterior embaixo, menor) —
// `valor` é um array [numero, percentual] pra colunas com % etapa a etapa, ou uma
// string simples pras colunas que não têm (Disparo = base 100%, % Conv. = já é %).
function celulaEtapa(valor, opts) {
  if (!Array.isArray(valor)) {
    return { text: String(valor), options: { ...opts } };
  }
  const [numero, pctEtapa] = valor;
  return {
    text: [
      { text: String(numero), options: { breakLine: true } },
      { text: pctEtapa, options: { fontSize: (opts.fontSize || 11.5) - 2.5, color: MUTED, bold: false } },
    ],
    options: { ...opts },
  };
}

function slideFunilSegmentado(pres, { titulo, subtitulo, colunaLabel, linhas, total, insightTitulo, insightTexto, footerTexto }) {
  const s = pres.addSlide();
  s.addText(titulo, {
    x: 0.7, y: 0.45, w: 12.4, h: 0.55, fontFace: "Cambria", fontSize: 24, bold: true, color: NAVY, margin: 0,
  });
  s.addText(subtitulo, {
    x: 0.7, y: 1.02, w: 11.5, h: 0.35, fontFace: "Calibri", fontSize: 13, color: MUTED, margin: 0,
  });

  const headerFill = NAVY;
  const totalFill = "D6E6F5";
  const cols = [colunaLabel, "Disparo", "Enviado", "Entrega", "Home", "Auth", "Oferta", "Acordo", "% Conv."];
  const colW = [2.35, 1.15, 1.15, 1.15, 1.05, 1.05, 1.05, 1.15, 1.85];
  const rowH = 0.5;

  const rows = [];
  rows.push(cols.map((c, i) => ({
    text: c,
    options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 11.5, align: i === 0 ? "left" : "right" },
  })));

  linhas.forEach((linha, i) => {
    const bg = i % 2 === 0 ? WHITE : CARDBG;
    rows.push(linha.map((valor, j) => celulaEtapa(valor, {
      fill: { color: bg },
      color: j === 0 ? INK : (j === 8 ? "1D7A45" : INK),
      bold: j === 0 || j === 8,
      fontSize: 11.5,
      align: j === 0 ? "left" : "right",
    })));
  });

  rows.push(total.map((valor, j) => celulaEtapa(valor, {
    fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 11.5,
    align: j === 0 ? "left" : "right",
  })));

  s.addTable(rows, {
    x: 0.7, y: 1.5, w: 11.95, colW, rowH,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri", autoPage: false, valign: "middle",
  });

  const calloutY = 1.5 + (rows.length) * rowH + 0.15;
  s.addShape("roundRect", {
    x: 0.7, y: calloutY, w: 11.95, h: 0.58, rectRadius: 0.08,
    fill: { color: "EAF6EF" }, line: { color: GREEN, width: 1 },
  });
  s.addImage({ path: "icon_award_2F9E6E.png", x: 0.92, y: calloutY + 0.13, w: 0.32, h: 0.32 });
  s.addText([
    { text: `${insightTitulo}  `, options: { bold: true, color: "1D7A45" } },
    { text: insightTexto, options: { color: "2F5741" } },
  ], {
    x: 1.35, y: calloutY, w: 11.1, h: 0.58, fontFace: "Calibri", fontSize: 12.5, valign: "middle", margin: 0,
  });

  footer(s, pres, footerTexto);
}

slideFunilSegmentado(pres, {
  titulo: "Funil completo por Prioridade",
  subtitulo: "As mesmas 7 etapas do funil geral, abertas por Prioridade — clientes únicos e % de conversão etapa a etapa",
  colunaLabel: "PRIORIDADE",
  linhas: [
    ["P1 · Máxima", "7.884", ["7.343","93%"], ["6.593","90%"], ["38","1%"], ["31","82%"], ["31","100%"], ["14","45%"], "0,18%"],
    ["P2 · Alta", "8.009", ["7.330","92%"], ["6.564","90%"], ["8","0%"], ["6","75%"], ["5","83%"], ["3","60%"], "0,04%"],
    ["P3 · Média", "6.729", ["6.099","91%"], ["4.930","81%"], ["3","0%"], ["3","100%"], ["3","100%"], ["4","133%"], "0,06%"],
    ["P4 · Baixa", "6.461", ["5.545","86%"], ["4.164","75%"], ["3","0%"], ["3","100%"], ["2","67%"], ["1","50%"], "0,02%"],
    ["Não Classificado", "5.181", ["4.772","92%"], ["4.119","86%"], ["29","1%"], ["23","79%"], ["22","96%"], ["11","50%"], "0,21%"],
  ],
  total: ["Total Geral", "34.264", ["31.089","91%"], ["26.370","85%"], ["81","0%"], ["66","81%"], ["63","95%"], ["33","52%"], "0,10%"],
  insightTitulo: "P1 · Máxima converte melhor que P2-P4:",
  insightTexto: "0,18% de Disparo→Acordo contra 0,02%-0,06% nas demais prioridades — a segmentação de propensão está funcionando.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo (jornada completa). Mesma base do funil consolidado (25/07–15/08).",
});

slideFunilSegmentado(pres, {
  titulo: "Funil completo por Prioridade — Julho",
  subtitulo: "As mesmas 7 etapas, restritas a julho — clientes únicos e % de conversão etapa a etapa (data pela campanha)",
  colunaLabel: "PRIORIDADE",
  linhas: [
    ["P1 · Máxima", "1.462", ["1.368","94%"], ["1.169","85%"], ["9","1%"], ["8","89%"], ["8","100%"], ["6","75%"], "0,41%"],
    ["P2 · Alta", "1.516", ["1.424","94%"], ["1.222","86%"], ["1","0%"], ["1","100%"], ["0","0%"], ["1","—"], "0,07%"],
    ["P3 · Média", "1.496", ["1.402","94%"], ["1.111","79%"], ["0","0%"], ["0","—"], ["0","—"], ["0","—"], "0,00%"],
    ["P4 · Baixa", "1.467", ["1.325","90%"], ["1.000","75%"], ["1","0%"], ["1","100%"], ["1","100%"], ["0","0%"], "0,00%"],
    ["Não Classificado", "2.066", ["1.923","93%"], ["1.625","85%"], ["18","1%"], ["17","94%"], ["16","94%"], ["4","25%"], "0,19%"],
  ],
  total: ["Total Geral", "8.007", ["7.442","93%"], ["6.127","82%"], ["29","0%"], ["27","93%"], ["25","93%"], ["11","44%"], "0,14%"],
  insightTitulo: "Em julho, P1 · Máxima disparou na conversão:",
  insightTexto: "0,41% de Disparo→Acordo — P2, P3 e P4 praticamente não geraram acordo nesse mês.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo (jornada completa). Base: 4 campanhas de julho.",
});

slideFunilSegmentado(pres, {
  titulo: "Funil completo por Prioridade — Agosto",
  subtitulo: "As mesmas 7 etapas, restritas a agosto — clientes únicos e % de conversão etapa a etapa (data pela campanha)",
  colunaLabel: "PRIORIDADE",
  linhas: [
    ["P1 · Máxima", "7.684", ["7.085","92%"], ["6.415","91%"], ["29","0%"], ["23","79%"], ["23","100%"], ["8","35%"], "0,10%"],
    ["P2 · Alta", "7.745", ["7.010","91%"], ["6.322","90%"], ["7","0%"], ["5","71%"], ["5","100%"], ["2","40%"], "0,03%"],
    ["P3 · Média", "6.508", ["5.759","88%"], ["4.728","82%"], ["3","0%"], ["3","100%"], ["3","100%"], ["4","133%"], "0,06%"],
    ["P4 · Baixa", "6.328", ["5.274","83%"], ["4.052","77%"], ["2","0%"], ["2","100%"], ["1","50%"], ["1","100%"], "0,02%"],
    ["Não Classificado", "3.726", ["3.366","90%"], ["2.954","88%"], ["13","0%"], ["7","54%"], ["7","100%"], ["7","100%"], "0,19%"],
  ],
  total: ["Total Geral", "31.991", ["28.494","89%"], ["24.471","86%"], ["54","0%"], ["40","74%"], ["39","98%"], ["22","56%"], "0,07%"],
  insightTitulo: "Em agosto, Não Classificado lidera a conversão:",
  insightTexto: "0,19% — mesmo assim, P1 · Máxima segue acima de P2, P3 e P4, confirmando o padrão do mês anterior.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo (jornada completa). Base: 26 campanhas de agosto.",
});

slideFunilSegmentado(pres, {
  titulo: "Funil completo por Grupo Estratégico",
  subtitulo: "As mesmas 7 etapas do funil geral, abertas por Grupo Estratégico — clientes únicos e % de conversão etapa a etapa",
  colunaLabel: "GRUPO ESTRATÉGICO",
  linhas: [
    ["Abandono Carrinho", "4.227", ["3.886","92%"], ["3.467","89%"], ["14","0%"], ["12","86%"], ["12","100%"], ["6","50%"], "0,14%"],
    ["Cadastrado", "26", ["23","88%"], ["19","83%"], ["1","5%"], ["1","100%"], ["1","100%"], ["1","100%"], "3,85%"],
    ["Engajado", "4.933", ["4.642","94%"], ["4.172","90%"], ["21","1%"], ["17","81%"], ["16","94%"], ["6","38%"], "0,12%"],
    ["Topo de Funil", "19.897", ["17.766","89%"], ["14.593","82%"], ["16","0%"], ["13","81%"], ["12","92%"], ["9","75%"], "0,05%"],
    ["Não Classificado", "5.181", ["4.772","92%"], ["4.119","86%"], ["29","1%"], ["23","79%"], ["22","96%"], ["11","50%"], "0,21%"],
  ],
  total: ["Total Geral", "34.264", ["31.089","91%"], ["26.370","85%"], ["81","0%"], ["66","81%"], ["63","95%"], ["33","52%"], "0,10%"],
  insightTitulo: "Cadastrado converte muito acima da média:",
  insightTexto: "3,85% de Disparo→Acordo contra ~0,05%-0,21% nos demais grupos — volume pequeno (26 disparos) mas taxa muito mais alta.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo (jornada completa). Mesma base do funil consolidado (25/07–15/08).",
});

slideFunilSegmentado(pres, {
  titulo: "Funil completo por Grupo Estratégico — Julho",
  subtitulo: "As mesmas 7 etapas, restritas a julho — clientes únicos e % de conversão etapa a etapa (data pela campanha)",
  colunaLabel: "GRUPO ESTRATÉGICO",
  linhas: [
    ["Abandono Carrinho", "860", ["805","94%"], ["676","84%"], ["2","0%"], ["2","100%"], ["2","100%"], ["1","50%"], "0,12%"],
    ["Cadastrado", "5", ["5","100%"], ["4","80%"], ["0","0%"], ["0","—"], ["0","—"], ["0","—"], "0,00%"],
    ["Engajado", "882", ["831","94%"], ["715","86%"], ["5","1%"], ["5","100%"], ["4","80%"], ["3","75%"], "0,34%"],
    ["Topo de Funil", "4.194", ["3.878","92%"], ["3.107","80%"], ["4","0%"], ["3","75%"], ["3","100%"], ["3","100%"], "0,07%"],
    ["Não Classificado", "2.066", ["1.923","93%"], ["1.625","85%"], ["18","1%"], ["17","94%"], ["16","94%"], ["4","25%"], "0,19%"],
  ],
  total: ["Total Geral", "8.007", ["7.442","93%"], ["6.127","82%"], ["29","0%"], ["27","93%"], ["25","93%"], ["11","44%"], "0,14%"],
  insightTitulo: "Em julho, Engajado converte melhor:",
  insightTexto: "0,34% de Disparo→Acordo — Cadastrado teve volume baixo demais (5 disparos) pra gerar acordo no mês.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo (jornada completa). Base: 4 campanhas de julho.",
});

slideFunilSegmentado(pres, {
  titulo: "Funil completo por Grupo Estratégico — Agosto",
  subtitulo: "As mesmas 7 etapas, restritas a agosto — clientes únicos e % de conversão etapa a etapa (data pela campanha)",
  colunaLabel: "GRUPO ESTRATÉGICO",
  linhas: [
    ["Abandono Carrinho", "4.095", ["3.713","91%"], ["3.347","90%"], ["12","0%"], ["10","83%"], ["10","100%"], ["5","50%"], "0,12%"],
    ["Cadastrado", "24", ["21","88%"], ["18","86%"], ["1","6%"], ["1","100%"], ["1","100%"], ["1","100%"], "4,17%"],
    ["Engajado", "4.825", ["4.500","93%"], ["4.077","91%"], ["16","0%"], ["12","75%"], ["12","100%"], ["3","25%"], "0,06%"],
    ["Topo de Funil", "19.321", ["16.894","87%"], ["14.075","83%"], ["12","0%"], ["10","83%"], ["9","90%"], ["6","67%"], "0,03%"],
    ["Não Classificado", "3.726", ["3.366","90%"], ["2.954","88%"], ["13","0%"], ["7","54%"], ["7","100%"], ["7","100%"], "0,19%"],
  ],
  total: ["Total Geral", "31.991", ["28.494","89%"], ["24.471","86%"], ["54","0%"], ["40","74%"], ["39","98%"], ["22","56%"], "0,07%"],
  insightTitulo: "Em agosto, Cadastrado dispara na conversão:",
  insightTexto: "4,17% de Disparo→Acordo (1 acordo em só 24 disparos) — volume pequeno, mas confirma o padrão de julho.",
  footerTexto: "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo (jornada completa). Base: 26 campanhas de agosto.",
});

// =====================================================================
// SLIDE(S) — FUNIL COMPLETO (função reutilizável — uma métrica por slide:
// clientes únicos OU eventos brutos, nunca as duas juntas no mesmo slide)
// =====================================================================
function slideFunilCompleto(pres, { titulo, subtitulo, etapas, gargaloTitulo, gargaloTexto, footerTexto }) {
  const s = pres.addSlide();
  s.addText(titulo, {
    x: 0.7, y: 0.45, w: 11, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, margin: 0,
  });
  s.addText(subtitulo, {
    x: 0.7, y: 1.0, w: 11, h: 0.35, fontFace: "Calibri", fontSize: 13, color: MUTED, margin: 0,
  });

  // largura da barra calibrada pro PIOR caso (ratio 100%: em julho/agosto "Enviado"
  // fica igual a "Disparo", já que dentro de um mês fechado não sobra nenhuma linha
  // ainda "não processada") — reservando espaço pro texto de conversão/drop à
  // direita, pra nenhuma barra intermediária empurrar esse texto pra fora do slide.
  const top = 1.4, drawW = 6.0, barH = 0.5, gapY = 0.1, labelW = 2.05, leftX = 0.7;
  const maxVal = etapas[0].valor;
  const minBarW = 0.55;

  etapas.forEach((e, i) => {
    const y = top + i * (barH + gapY);
    const isGargalo = !!e.gargalo;
    const w = Math.max(minBarW, (e.valor / maxVal) * drawW);

    // icone + nome
    s.addImage({ path: `icon_${e.icon}_1E2761.png`, x: leftX, y: y + 0.09, w: 0.32, h: 0.32 });
    s.addText(e.nome, {
      x: leftX + 0.4, y, w: labelW - 0.4, h: barH, fontFace: "Calibri", fontSize: 13.5,
      bold: true, color: INK, valign: "middle", margin: 0,
    });

    // barra
    s.addShape("roundRect", {
      x: leftX + labelW, y, w: w, h: barH, rectRadius: 0.06,
      fill: { color: isGargalo ? ORANGE : (i === etapas.length - 1 ? GREEN : NAVY) },
      line: { type: "none" },
    });
    s.addText(e.valor.toLocaleString("pt-BR"), {
      x: leftX + labelW + 0.12, y, w: Math.max(w - 0.2, 0.4), h: barH,
      fontFace: "Calibri", fontSize: 13, bold: true, color: WHITE, valign: "middle", margin: 0,
    });

    // % do disparo, fora da barra
    s.addText(`${e.pctDisparo} do disparo`, {
      x: leftX + labelW + w + 0.15, y, w: 1.7, h: barH, fontFace: "Calibri", fontSize: 11,
      color: MUTED, valign: "middle", margin: 0,
    });

    // conversão/drop — quando a métrica é "eventos", uma etapa pode ter MAIS
    // linhas que a anterior (ex.: Oferta > Auth: um cliente já autenticado antes
    // recebe uma nova oferta sem gerar novo evento de auth na janela) — nesse
    // caso mostra "alta +X%" em vez de "drop -X%". Drop zero (Enviado = Disparo
    // em julho/agosto, onde não sobra nenhuma linha "não processada" no mês
    // fechado) mostra "sem perda" em vez do estranho "drop -0,0%".
    if (e.drop != null) {
      const semPerda = e.drop === "0,0%";
      const alta = !semPerda && e.drop.startsWith("-");
      s.addText([
        { text: `conv. ${e.conv}  `, options: { color: MUTED } },
        semPerda
          ? { text: "sem perda", options: { color: MUTED } }
          : alta
          ? { text: `alta +${e.drop.slice(1)}`, options: { color: "1D7A45", bold: false } }
          : { text: `drop -${e.drop}`, options: { color: isGargalo ? ORANGE : "#B5541A", bold: isGargalo } },
      ], {
        x: leftX + labelW + w + 1.85, y, w: 2.3, h: barH, fontFace: "Calibri", fontSize: 11,
        valign: "middle", margin: 0,
      });
    }
  });

  // callout de gargalo
  const calloutY = top + etapas.length * (barH + gapY) + 0.1;
  const calloutH = 0.58;
  s.addShape("roundRect", {
    x: 0.7, y: calloutY, w: 11.95, h: calloutH, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 0.92, y: calloutY + 0.13, w: 0.32, h: 0.32 });
  s.addText([
    { text: `${gargaloTitulo}  `, options: { bold: true, color: "B5541A" } },
    { text: gargaloTexto, options: { color: "6B4632" } },
  ], {
    x: 1.35, y: calloutY, w: 11.1, h: calloutH, fontFace: "Calibri", fontSize: 12.5,
    valign: "middle", margin: 0,
  });

  footer(s, pres, footerTexto);
}

// ---- clientes únicos (3 slides) ----
slideFunilCompleto(pres, {
  titulo: "Funil completo — Disparo até Acordo",
  subtitulo: "Clientes únicos por etapa — % sobre a base de disparo e conversão etapa a etapa",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 34264, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 31089, pctDisparo: "90,7%", conv: "90,7%", drop: "9,3%" },
    { nome: "Entrega", icon: "check", valor: 26370, pctDisparo: "77,0%", conv: "84,8%", drop: "15,2%" },
    { nome: "Home", icon: "home", valor: 81, pctDisparo: "0,24%", conv: "0,31%", drop: "99,7%", gargalo: true },
    { nome: "Auth", icon: "shield", valor: 66, pctDisparo: "0,19%", conv: "81,5%", drop: "18,5%" },
    { nome: "Oferta", icon: "tag", valor: 63, pctDisparo: "0,18%", conv: "95,5%", drop: "4,5%" },
    { nome: "Acordo", icon: "award", valor: 33, pctDisparo: "0,10%", conv: "52,4%", drop: "47,6%" },
  ],
  gargaloTitulo: "Maior gargalo: Entrega → Home",
  gargaloTexto: "— 99,7% dos clientes que recebem o SMS não avançam para negociação no CRM.",
  footerTexto: "% do disparo = etapa ÷ 34.264 clientes únicos disparados. Conversão/drop calculados sobre a etapa anterior.",
});

slideFunilCompleto(pres, {
  titulo: "Funil completo — Julho",
  subtitulo: "Mesma leitura do consolidado, restrita a 25/07–31/07 — clientes únicos por etapa",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 8007, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 7442, pctDisparo: "92,9%", conv: "92,9%", drop: "7,1%" },
    { nome: "Entrega", icon: "check", valor: 6127, pctDisparo: "76,5%", conv: "82,3%", drop: "17,7%" },
    { nome: "Home", icon: "home", valor: 29, pctDisparo: "0,36%", conv: "0,47%", drop: "99,5%", gargalo: true },
    { nome: "Auth", icon: "shield", valor: 27, pctDisparo: "0,34%", conv: "93,1%", drop: "6,9%" },
    { nome: "Oferta", icon: "tag", valor: 25, pctDisparo: "0,31%", conv: "92,6%", drop: "7,4%" },
    { nome: "Acordo", icon: "award", valor: 11, pctDisparo: "0,14%", conv: "44,0%", drop: "56,0%" },
  ],
  gargaloTitulo: "Maior gargalo em julho: Entrega → Home",
  gargaloTexto: "— 99,5% dos clientes entregues não avançam para negociação no CRM.",
  footerTexto: "% do disparo = etapa ÷ 8.007 clientes únicos disparados em julho (data pela campanha, não pelo retorno).",
});

slideFunilCompleto(pres, {
  titulo: "Funil completo — Agosto",
  subtitulo: "Mesma leitura do consolidado, restrita a 01/08–15/08 — clientes únicos por etapa",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 31991, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 28494, pctDisparo: "89,1%", conv: "89,1%", drop: "10,9%" },
    { nome: "Entrega", icon: "check", valor: 24471, pctDisparo: "76,5%", conv: "85,9%", drop: "14,1%" },
    { nome: "Home", icon: "home", valor: 54, pctDisparo: "0,17%", conv: "0,22%", drop: "99,8%", gargalo: true },
    { nome: "Auth", icon: "shield", valor: 40, pctDisparo: "0,13%", conv: "74,1%", drop: "25,9%" },
    { nome: "Oferta", icon: "tag", valor: 39, pctDisparo: "0,12%", conv: "97,5%", drop: "2,5%" },
    { nome: "Acordo", icon: "award", valor: 22, pctDisparo: "0,07%", conv: "56,4%", drop: "43,6%" },
  ],
  gargaloTitulo: "Maior gargalo em agosto: Entrega → Home",
  gargaloTexto: "— 99,8% dos clientes entregues não avançam para negociação no CRM (pior que julho).",
  footerTexto: "% do disparo = etapa ÷ 31.991 clientes únicos disparados em agosto (data pela campanha, não pelo retorno).",
});

// ---- eventos brutos, sem dedupe (3 slides separados) ----
slideFunilCompleto(pres, {
  titulo: "Funil completo (eventos brutos) — Consolidado",
  subtitulo: "Mesmo funil do início, agora contando toda linha/ação bruta — sem deduplicar por cliente",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 92406, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 81232, pctDisparo: "87,9%", conv: "87,9%", drop: "12,1%" },
    { nome: "Entrega", icon: "check", valor: 70985, pctDisparo: "76,8%", conv: "87,4%", drop: "12,6%" },
    { nome: "Home", icon: "home", valor: 781, pctDisparo: "0,85%", conv: "1,1%", drop: "98,9%", gargalo: true },
    { nome: "Auth", icon: "shield", valor: 326, pctDisparo: "0,35%", conv: "41,7%", drop: "58,3%" },
    { nome: "Oferta", icon: "tag", valor: 337, pctDisparo: "0,36%", conv: "103,4%", drop: "-3,4%" },
    { nome: "Acordo", icon: "award", valor: 39, pctDisparo: "0,04%", conv: "11,6%", drop: "88,4%" },
  ],
  gargaloTitulo: "Maior gargalo: Entrega → Home",
  gargaloTexto: "— 98,9% das entregas não geram nenhuma ação de Home no CRM.",
  footerTexto: "Eventos brutos = toda linha do log (um cliente pode gerar mais de uma por etapa) — não deduplicado por telefone. Oferta > Auth acontece porque um cliente já autenticado antes pode receber nova oferta sem novo evento de auth na janela.",
});

slideFunilCompleto(pres, {
  titulo: "Funil completo (eventos brutos) — Julho",
  subtitulo: "Mesmo recorte de julho, agora contando toda linha/ação bruta — sem deduplicar por cliente",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 8024, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 7456, pctDisparo: "92,9%", conv: "92,9%", drop: "7,1%" },
    { nome: "Entrega", icon: "check", valor: 6141, pctDisparo: "76,5%", conv: "82,4%", drop: "17,6%" },
    { nome: "Home", icon: "home", valor: 128, pctDisparo: "1,60%", conv: "2,1%", drop: "97,9%", gargalo: true },
    { nome: "Auth", icon: "shield", valor: 98, pctDisparo: "1,22%", conv: "76,6%", drop: "23,4%" },
    { nome: "Oferta", icon: "tag", valor: 100, pctDisparo: "1,25%", conv: "102,0%", drop: "-2,0%" },
    { nome: "Acordo", icon: "award", valor: 12, pctDisparo: "0,15%", conv: "12,0%", drop: "88,0%" },
  ],
  gargaloTitulo: "Maior gargalo em julho: Entrega → Home",
  gargaloTexto: "— 97,9% das entregas não geram nenhuma ação de Home no CRM.",
  footerTexto: "Eventos brutos = toda linha do log em julho, não deduplicado por telefone. Disparo pela data da campanha (não do retorno).",
});

slideFunilCompleto(pres, {
  titulo: "Funil completo (eventos brutos) — Agosto",
  subtitulo: "Mesmo recorte de agosto, agora contando toda linha/ação bruta — sem deduplicar por cliente",
  etapas: [
    { nome: "Disparo", icon: "send", valor: 84382, pctDisparo: "100%", conv: "–", drop: null },
    { nome: "Enviado", icon: "mail", valor: 73776, pctDisparo: "87,4%", conv: "87,4%", drop: "12,6%" },
    { nome: "Entrega", icon: "check", valor: 64844, pctDisparo: "76,9%", conv: "87,9%", drop: "12,1%" },
    { nome: "Home", icon: "home", valor: 653, pctDisparo: "0,77%", conv: "1,0%", drop: "99,0%", gargalo: true },
    { nome: "Auth", icon: "shield", valor: 228, pctDisparo: "0,27%", conv: "34,9%", drop: "65,1%" },
    { nome: "Oferta", icon: "tag", valor: 237, pctDisparo: "0,28%", conv: "103,9%", drop: "-3,9%" },
    { nome: "Acordo", icon: "award", valor: 27, pctDisparo: "0,03%", conv: "11,4%", drop: "88,6%" },
  ],
  gargaloTitulo: "Maior gargalo em agosto: Entrega → Home",
  gargaloTexto: "— 99,0% das entregas não geram nenhuma ação de Home no CRM.",
  footerTexto: "Eventos brutos = toda linha do log em agosto, não deduplicado por telefone. Disparo pela data da campanha (não do retorno).",
});

// =====================================================================
// SLIDE 4 — CUSTOS
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Custo do canal SMS", {
    x: 0.7, y: 0.5, w: 9, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Base de cobrança Kolmeya: por SMS Enviado — R$ 0,0620 / unidade", {
    x: 0.7, y: 1.08, w: 10, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  // formula
  s.addShape("roundRect", {
    x: 0.7, y: 1.5, w: 11.95, h: 0.65, rectRadius: 0.08,
    fill: { color: CARDBG }, line: { color: LINE, width: 1 },
  });
  s.addText([
    { text: "81.232", options: { bold: true, color: NAVY, fontSize: 16 } },
    { text: "  SMS enviados   ×   ", options: { color: MUTED, fontSize: 12 } },
    { text: "R$ 0,0620", options: { bold: true, color: NAVY, fontSize: 16 } },
    { text: "  custo unitário   =   ", options: { color: MUTED, fontSize: 12 } },
    { text: "R$ 5.036,38", options: { bold: true, color: GREEN, fontSize: 18 } },
  ], {
    x: 1.0, y: 1.5, w: 11.4, h: 0.65, fontFace: "Calibri", valign: "middle", align: "left", margin: 0,
  });

  statCard(s, 0.7, 2.25, 3.85, 1.3, {
    icon: "icon_dollar_1E2761.png", value: "R$ 7.887,49", valueSize: 18,
    label: "Investimento total do período (todos os canais + Lemit)",
  });
  statCard(s, 4.75, 2.25, 3.85, 1.3, {
    icon: "icon_percent_E8622C.png", value: "63,9%", valueSize: 23, valueColor: ORANGE,
    label: "Participação do SMS no investimento total",
  });
  statCard(s, 8.8, 2.25, 3.85, 1.3, {
    icon: "icon_award_2F9E6E.png", value: "R$ 152,62", valueSize: 20, valueColor: GREEN,
    label: "Custo médio por Acordo gerado via SMS",
  });

  s.addText("Custo por resultado (custo total SMS ÷ volume da etapa)", {
    x: 0.7, y: 3.7, w: 8, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, margin: 0,
  });

  const custos = [
    ["Por cliente disparado", "R$ 0,15"],
    ["Por cliente entregue", "R$ 0,19"],
    ["Por chegada na Home", "R$ 62,18"],
    ["Por Oferta apresentada", "R$ 79,94"],
    ["Por Acordo fechado", "R$ 152,62"],
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
  {
    const linhasInv = [
      ["SMS (Kolmeya)", "R$ 5.036,38", "63,9%"],
      ["RCS (Ötima)", "R$ 753,48", "9,6%"],
      ["WhatsApp (Ötima + Airys)", "R$ 246,59", "3,1%"],
      ["Lemit — enriquecimento de dados (julho)", "R$ 1.851,04", "23,5%"],
    ];
    const ix = 0.7, iy = 5.28, iw = 8.05;
    const rows = [];
    rows.push([
      { text: "INVESTIMENTO NO PERÍODO", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: 11.5, align: "left" } },
      { text: "Valor", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: 11.5, align: "right" } },
      { text: "%", options: { fill: { color: NAVY }, color: WHITE, bold: true, fontSize: 11.5, align: "right" } },
    ]);
    linhasInv.forEach(([nome, valor, pct], i) => {
      const bg = i % 2 === 0 ? WHITE : CARDBG;
      rows.push([
        { text: nome, options: { fill: { color: bg }, color: INK, fontSize: 11, align: "left" } },
        { text: valor, options: { fill: { color: bg }, color: INK, fontSize: 11, align: "right" } },
        { text: pct, options: { fill: { color: bg }, color: MUTED, fontSize: 11, align: "right" } },
      ]);
    });
    rows.push([
      { text: "Total do período", options: { fill: { color: "D6E6F5" }, color: NAVY, bold: true, fontSize: 11.5, align: "left" } },
      { text: "R$ 7.887,49", options: { fill: { color: "D6E6F5" }, color: NAVY, bold: true, fontSize: 11.5, align: "right" } },
      { text: "100%", options: { fill: { color: "D6E6F5" }, color: NAVY, bold: true, fontSize: 11.5, align: "right" } },
    ]);
    s.addTable(rows, {
      x: ix, y: iy, w: iw, colW: [iw - 2.2, 1.35, 0.85], rowH: 0.29,
      border: { type: "solid", color: LINE, pt: 0.75 },
      fontFace: "Calibri", autoPage: false, valign: "middle",
    });
  }

  footer(s, pres, "Email ainda sem custo unitário confirmado — não entra no investimento total conhecido.");
}

// =====================================================================
// SLIDE 5 — FUNIL POR MÊS (JULHO x AGOSTO)
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Funil por mês — Julho x Agosto", {
    x: 0.7, y: 0.45, w: 10.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Mesma leitura do slide anterior, aberta por mês — clientes únicos dentro de cada mês", {
    x: 0.7, y: 1.0, w: 11, h: 0.35, fontFace: "Calibri", fontSize: 13, color: MUTED, margin: 0,
  });

  const meses = [
    {
      nome: "JULHO", periodo: "25/07 – 31/07", x: 0.7,
      etapas: [
        { nome: "Disparo", valor: 8007, pctDisparo: "100%" },
        { nome: "Enviado", valor: 7442, pctDisparo: "92,9%" },
        { nome: "Entrega", valor: 6127, pctDisparo: "76,5%" },
        { nome: "Home", valor: 29, pctDisparo: "0,36%", gargalo: true },
        { nome: "Auth", valor: 27, pctDisparo: "0,34%" },
        { nome: "Oferta", valor: 25, pctDisparo: "0,31%" },
        { nome: "Acordo", valor: 11, pctDisparo: "0,14%", final: true },
      ],
    },
    {
      nome: "AGOSTO", periodo: "01/08 – 15/08", x: 6.85,
      etapas: [
        { nome: "Disparo", valor: 31991, pctDisparo: "100%" },
        { nome: "Enviado", valor: 28494, pctDisparo: "89,1%" },
        { nome: "Entrega", valor: 24471, pctDisparo: "76,5%" },
        { nome: "Home", valor: 54, pctDisparo: "0,17%", gargalo: true },
        { nome: "Auth", valor: 40, pctDisparo: "0,13%" },
        { nome: "Oferta", valor: 39, pctDisparo: "0,12%" },
        { nome: "Acordo", valor: 22, pctDisparo: "0,07%", final: true },
      ],
    },
  ];

  const colW = 5.75, top = 1.4, rowH = 0.48, gapY = 0.07;
  meses.forEach((mes) => {
    s.addShape("roundRect", {
      x: mes.x, y: top, w: colW, h: 0.5, rectRadius: 0.06,
      fill: { color: NAVY }, line: { type: "none" },
    });
    s.addText([
      { text: mes.nome + "  ", options: { bold: true, color: WHITE, fontSize: 15 } },
      { text: mes.periodo, options: { color: ICE, fontSize: 11 } },
    ], {
      x: mes.x + 0.2, y: top, w: colW - 0.4, h: 0.5, fontFace: "Calibri", valign: "middle", margin: 0,
    });

    let ry = top + 0.6;
    mes.etapas.forEach((e) => {
      const bg = e.gargalo ? "FDEDE4" : (e.final ? "EAF6EF" : CARDBG);
      const border = e.gargalo ? ORANGE : (e.final ? GREEN : LINE);
      s.addShape("roundRect", {
        x: mes.x, y: ry, w: colW, h: rowH, rectRadius: 0.05,
        fill: { color: bg }, line: { color: border, width: 1 },
      });
      s.addText(e.nome, {
        x: mes.x + 0.2, y: ry, w: 1.6, h: rowH, fontFace: "Calibri", fontSize: 12,
        bold: true, color: INK, valign: "middle", margin: 0,
      });
      s.addText(e.valor.toLocaleString("pt-BR"), {
        x: mes.x + 1.75, y: ry, w: 1.6, h: rowH, fontFace: "Calibri", fontSize: 14,
        bold: true, color: e.gargalo ? "B5541A" : NAVY, valign: "middle", margin: 0,
      });
      s.addText(`${e.pctDisparo} do disparo`, {
        x: mes.x + 3.35, y: ry, w: colW - 3.55, h: rowH, fontFace: "Calibri", fontSize: 10.5,
        color: MUTED, align: "right", valign: "middle", margin: 0,
      });
      ry += rowH + gapY;
    });
  });

  s.addShape("roundRect", {
    x: 0.7, y: 5.95, w: 11.95, h: 0.58, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_trenddown_E8622C.png", x: 0.92, y: 6.08, w: 0.32, h: 0.32 });
  s.addText([
    { text: "Gargalo piorou de julho pra agosto:  ", options: { bold: true, color: "B5541A" } },
    { text: "conversão Entrega → Home caiu de 0,47% para 0,22% conforme o volume disparado cresceu ~4x.", options: { color: "6B4632" } },
  ], {
    x: 1.35, y: 5.95, w: 11.1, h: 0.58, fontFace: "Calibri", fontSize: 12.5, valign: "middle", margin: 0,
  });

  footer(s, pres, "Mês = data da campanha (arquivo de disparo), não do retorno. Clientes únicos contados dentro de cada mês — por isso a soma Julho+Agosto não bate com o consolidado (clientes repetidos entre os dois meses).");
}

// =====================================================================
// SLIDE 6 — CUSTO POR MÊS (JULHO x AGOSTO)
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Custo por mês — Julho x Agosto", {
    x: 0.7, y: 0.5, w: 10, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Mesma base de cobrança Kolmeya (R$ 0,0620 por SMS Enviado), aberta por mês", {
    x: 0.7, y: 1.08, w: 10.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  const meses = [
    { nome: "JULHO", x: 0.7, enviados: "7.456", custo: "R$ 462,27", pctTotal: "9,2% do custo SMS do período", acordos: "11", custoAcordo: "R$ 42,02" },
    { nome: "AGOSTO", x: 6.85, enviados: "73.776", custo: "R$ 4.574,11", pctTotal: "90,8% do custo SMS do período", acordos: "22", custoAcordo: "R$ 207,91" },
  ];

  const colW = 5.75, top = 1.75;
  meses.forEach((mes) => {
    s.addShape("roundRect", {
      x: mes.x, y: top, w: colW, h: 3.35, rectRadius: 0.1,
      fill: { color: CARDBG }, line: { color: LINE, width: 1 },
      shadow: { type: "outer", color: "1E2761", opacity: 0.08, blur: 6, offset: 2, angle: 90 },
    });
    s.addText(mes.nome, {
      x: mes.x + 0.3, y: top + 0.22, w: colW - 0.6, h: 0.4, fontFace: "Calibri", fontSize: 15,
      bold: true, color: NAVY, charSpacing: 2, margin: 0,
    });
    s.addText([
      { text: mes.enviados, options: { bold: true, color: NAVY, fontSize: 22 } },
      { text: "  SMS enviados", options: { color: MUTED, fontSize: 13 } },
    ], {
      x: mes.x + 0.3, y: top + 0.65, w: colW - 0.6, h: 0.4, fontFace: "Calibri", valign: "middle", margin: 0,
    });
    s.addText(mes.custo, {
      x: mes.x + 0.3, y: top + 1.1, w: colW - 0.6, h: 0.6, fontFace: "Calibri", fontSize: 32,
      bold: true, color: GREEN, valign: "middle", margin: 0,
    });
    s.addText(mes.pctTotal, {
      x: mes.x + 0.3, y: top + 1.68, w: colW - 0.6, h: 0.3, fontFace: "Calibri", fontSize: 11,
      color: MUTED, margin: 0,
    });

    s.addShape("line", {
      x: mes.x + 0.3, y: top + 2.08, w: colW - 0.6, h: 0, line: { color: LINE, width: 1 },
    });

    s.addText([
      { text: mes.acordos, options: { bold: true, color: NAVY, fontSize: 20 } },
      { text: "  acordos gerados", options: { color: MUTED, fontSize: 13 } },
    ], {
      x: mes.x + 0.3, y: top + 2.2, w: colW - 0.6, h: 0.4, fontFace: "Calibri", valign: "middle", margin: 0,
    });
    s.addText("Custo médio por Acordo", {
      x: mes.x + 0.3, y: top + 2.65, w: colW - 0.6, h: 0.3, fontFace: "Calibri", fontSize: 11.5,
      color: MUTED, margin: 0,
    });
    s.addText(mes.custoAcordo, {
      x: mes.x + 0.3, y: top + 2.9, w: colW - 0.6, h: 0.5, fontFace: "Calibri", fontSize: 26,
      bold: true, color: ORANGE, margin: 0,
    });
  });

  s.addShape("roundRect", {
    x: 0.7, y: 5.35, w: 11.95, h: 0.62, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 0.92, y: 5.49, w: 0.32, h: 0.32 });
  s.addText([
    { text: "Custo por Acordo quase quintuplicou:  ", options: { bold: true, color: "B5541A" } },
    { text: "R$ 42,02 em julho → R$ 207,91 em agosto — o volume de disparo cresceu ~4x mas o gargalo de engajamento (slide anterior) piorou.", options: { color: "6B4632" } },
  ], {
    x: 1.35, y: 5.35, w: 11.1, h: 0.62, fontFace: "Calibri", fontSize: 13, valign: "middle", margin: 0,
  });

  footer(s, pres, "Custo SMS por mês = SMS enviados no mês × R$ 0,0620. % sobre o custo SMS total do período (R$ 5.036,38).");
}

// =====================================================================
// SLIDE 7 — VISÃO EXECUTIVA
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Visão executiva — SMS", {
    x: 0.7, y: 0.5, w: 9, h: 0.55, fontFace: "Cambria", fontSize: 28, bold: true, color: WHITE, margin: 0,
  });
  s.addText("O que essa análise já responde", {
    x: 0.7, y: 1.05, w: 9, h: 0.35, fontFace: "Calibri", fontSize: 13, color: ICE, margin: 0,
  });

  const perguntas = [
    ["Clientes impactados", "34.264 clientes únicos"],
    ["SMS entregues", "70.985 (76,8%)"],
    ["Taxa de entrega", "76,8% dos disparos"],
    ["Conversão Home → Auth", "81,5%"],
    ["Conversão Auth → Oferta", "95,5%"],
    ["Conversão Oferta → Acordo", "52,4%"],
    ["Conversão total Disparo → Acordo", "0,10%"],
    ["Acordos gerados", "33"],
    ["Custo total do SMS", "R$ 5.036,38"],
    ["% do investimento total", "63,9%"],
    ["Custo médio por Acordo", "R$ 152,62"],
    ["Maior gargalo", "Entrega → Home (-99,7%)"],
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
      x: x + 0.2, y: y + 0.5, w: cw - 0.4, h: 0.55, fontFace: "Calibri", fontSize: 17.5, bold: true,
      color: WHITE, align: "left", valign: "top", margin: 0,
    });
  });

  s.addText("Próximo passo: aplicar a mesma leitura (funil + custo) para WhatsApp e RCS.", {
    x: 0.7, y: 6.95, w: 11.5, h: 0.35, fontFace: "Calibri", fontSize: 12, italic: true,
    color: "8FA3D9", margin: 0,
  });
}

pres.writeFile({ fileName: "casas_bahia_sms.pptx" }).then(() => console.log("done"));
