const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, statCard, makeFooter, slideCapa,
  makeSlidePrioridadeGrupoEstrategico,
} = require("./lib.js");

const footer = makeFooter("Email");
const slidePrioridadeGrupoEstrategico = makeSlidePrioridadeGrupoEstrategico(footer);

function tabelaCrm(s, { x, y, w, titulo, linhas, total }) {
  const headerFill = NAVY;
  const totalFill = "D6E6F5";
  const cols = [titulo, "Home", "Auth", "Ofer.", "Acordo"];
  const labelW = w - 3.3, stageW = 0.825;
  const colW = [labelW, stageW, stageW, stageW, stageW];
  const rows = [];
  rows.push(cols.map((c, i) => ({
    text: c,
    options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 10, align: i === 0 ? "left" : "right" },
  })));
  linhas.forEach((linha, i) => {
    const bg = i % 2 === 0 ? WHITE : CARDBG;
    rows.push(linha.map((v, j) => ({
      text: String(v),
      options: { fill: { color: bg }, color: j === 0 ? INK : NAVY, bold: j === 0, fontSize: 10.5, align: j === 0 ? "left" : "right" },
    })));
  });
  rows.push(total.map((v, j) => ({
    text: String(v),
    options: { fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 10.5, align: j === 0 ? "left" : "right" },
  })));
  s.addTable(rows, {
    x, y, w, colW, rowH: 0.34,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri", autoPage: false, valign: "middle",
  });
}

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "CAPÍTULO 4 · CANAL",
  titulo: "EMAIL",
  subtitulo: "Resultados Casas Bahia — jornada completa do envio ao acordo",
  periodo: "Período analisado: julho  ·  Fornecedor: Salesforce Journey Builder",
  etapas: ["Envio", "Entrega", "Abertura", "Clique", "Home", "Auth", "Oferta", "Acordo"],
});

// =====================================================================
// SLIDE 2 — VOLUMETRIA
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Volumetria do envio", {
    x: 0.7, y: 0.5, w: 9, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Métricas do relatório Salesforce Journey Builder — não há linha por telefone, só totais do período", {
    x: 0.7, y: 1.08, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  statCard(s, 0.7, 1.7, 3.85, 1.7, {
    icon: "icon_send_1E2761.png", value: "37.730", valueSize: 32,
    label: "E-mails enviados no total",
  });
  statCard(s, 4.75, 1.7, 3.85, 1.7, {
    icon: "icon_check_1E2761.png", value: "35.615", valueSize: 32,
    label: "E-mails entregues (94,4% do enviado)",
  });
  statCard(s, 8.8, 1.7, 3.85, 1.7, {
    icon: "icon_eye_1E2761.png", value: "270", valueSize: 32,
    label: "Aberturas (0,76% do entregue)",
  });

  s.addText("Jornada de engajamento", {
    x: 0.7, y: 3.6, w: 6, h: 0.35, fontFace: "Calibri", fontSize: 15, bold: true, color: NAVY, margin: 0,
  });

  const linhas = [
    ["Envios", "37.730", "100% do envio"],
    ["Entregues", "35.615", "94,4% do envio"],
    ["Aberturas", "270", "0,76% do entregue"],
    ["Cliques", "37", "13,7% da abertura / 0,10% do entregue"],
  ];
  let ly = 4.3;
  const rowH = 0.48;
  linhas.forEach(([nome, valor, pct]) => {
    s.addShape("roundRect", {
      x: 0.7, y: ly, w: 11.95, h: rowH, rectRadius: 0.06,
      fill: { color: CARDBG }, line: { color: LINE, width: 1 },
    });
    s.addText(nome, { x: 1.0, y: ly, w: 2.5, h: rowH, fontFace: "Calibri", fontSize: 13, bold: true, color: INK, valign: "middle", margin: 0 });
    s.addText(valor, { x: 3.5, y: ly, w: 2.0, h: rowH, fontFace: "Calibri", fontSize: 16, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(pct, { x: 5.6, y: ly, w: 6.5, h: rowH, fontFace: "Calibri", fontSize: 11.5, color: MUTED, valign: "middle", margin: 0 });
    ly += rowH + 0.1;
  });

  footer(s, pres, "Base: relatório Salesforce Journey Builder, julho — sem linha por telefone, por isso sem quebra por mês para este canal. A base de Prioridade/Grupo Estratégico (próximo slide) vem de um sistema diferente: as campanhas avulsas de e-mail do CRM.");
}

// =====================================================================
// SLIDE 3 — PRIORIDADE E GRUPO ESTRATÉGICO (campanhas avulsas de e-mail do CRM)
// =====================================================================
slidePrioridadeGrupoEstrategico(pres, {
  titulo: "Base de disparo por Prioridade e Grupo Estratégico",
  subtitulo: "Composição dos 5.535 destinatários únicos das campanhas avulsas de e-mail do CRM — base diferente do Salesforce Journey Builder",
  linhasPrioridade: [
    ["P1 · Máxima", "2.148", "38,8%"],
    ["P2 · Alta", "1.282", "23,2%"],
    ["P3 · Média", "1.062", "19,2%"],
    ["P4 · Baixa", "1.043", "18,8%"],
  ],
  linhasGE: [
    ["Abandono Carrinho", "1.139", "20,6%"],
    ["Cadastrado", "19", "0,3%"],
    ["Engajado", "1.342", "24,2%"],
    ["Topo de Funil", "3.035", "54,8%"],
  ],
  total: "5.535",
  footerTexto: "Base: 5 campanhas avulsas de e-mail (ARQUIVOS PARA DISPAROS), identificadas por endereço de e-mail — sistema diferente do relatório agregado Salesforce Journey Builder do slide anterior (37.730 envios), que não tem linha por destinatário. Os dois não são comparáveis nem somáveis.",
});

// =====================================================================
// SLIDE 4 — AÇÕES DE CRM POR PRIORIDADE E GRUPO ESTRATÉGICO
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Ações de CRM por Prioridade e Grupo Estratégico", {
    x: 0.7, y: 0.5, w: 12.4, h: 0.55, fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Home/Auth/Oferta/Acordo do e-mail, abertos por Prioridade e Grupo Estratégico do próprio log de CRM", {
    x: 0.7, y: 1.1, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  tabelaCrm(s, {
    x: 0.7, y: 1.75, w: 5.6, titulo: "PRIORIDADE",
    linhas: [
      ["P1 · Máxima", 3, 2, 2, 2],
      ["P2 · Alta", 1, 1, 1, 0],
      ["P3 · Média", 1, 0, 0, 0],
      ["P4 · Baixa", 0, 0, 0, 0],
      ["Não Classificado*", 6, 3, 2, 3],
    ],
    total: ["Total Geral", 11, 6, 5, 5],
  });
  tabelaCrm(s, {
    x: 6.75, y: 1.75, w: 5.9, titulo: "GRUPO ESTRATÉGICO",
    linhas: [
      ["Abandono Carrinho", 1, 1, 1, 0],
      ["Cadastrado", 0, 0, 0, 0],
      ["Engajado", 2, 2, 2, 2],
      ["Topo de Funil", 2, 0, 0, 0],
      ["Não Classificado*", 6, 3, 2, 3],
    ],
    total: ["Total Geral", 11, 6, 5, 5],
  });

  s.addShape("roundRect", {
    x: 0.7, y: 4.75, w: 11.95, h: 0.9, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 0.92, y: 4.9, w: 0.32, h: 0.32 });
  s.addText([
    { text: "Não é o mesmo destinatário da tabela de disparo acima:  ", options: { bold: true, color: "B5541A" } },
    { text: "estas ações vêm do log de CRM (telefone), enquanto a base de disparo do slide anterior é por e-mail — os dois sistemas não se cruzam por identificador comum. *Não Classificado = ação de CRM cujo telefone não foi associado a uma Prioridade/Grupo do e-mail.", options: { color: "6B4632" } },
  ], {
    x: 1.35, y: 4.75, w: 11.1, h: 0.9, fontFace: "Calibri", fontSize: 11.5, valign: "middle", margin: 0,
  });

  footer(s, pres, "Volume muito baixo (5 a 11 clientes no total por etapa) — leia com cautela, cada cliente já muda vários pontos percentuais. Mesma base de CRM usada no funil combinado do slide seguinte.");
}

// =====================================================================
// SLIDE 5 — FUNIL (Envio → Entrega → Abertura → Clique → CRM)
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Funil completo — Envio até Acordo", {
    x: 0.7, y: 0.45, w: 11, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Métricas de e-mail (Salesforce) + ações de CRM (Home/Auth/Oferta/Acordo) — ver nota sobre cruzamento", {
    x: 0.7, y: 1.0, w: 11.5, h: 0.35, fontFace: "Calibri", fontSize: 13, color: MUTED, margin: 0,
  });

  const etapas = [
    { nome: "Envio", icon: "send", valor: 37730, pctBase: "100%", conv: "–", drop: null },
    { nome: "Entrega", icon: "check", valor: 35615, pctBase: "94,4%", conv: "94,4%", drop: "5,6%" },
    { nome: "Abertura", icon: "eye", valor: 270, pctBase: "0,72%", conv: "0,76%", drop: "99,2%", gargalo: true },
    { nome: "Clique", icon: "click", valor: 37, pctBase: "0,10%", conv: "13,7%", drop: "86,3%" },
    { nome: "Home", icon: "home", valor: 11, pctBase: "0,03%", conv: "29,7%", drop: "70,3%" },
    { nome: "Auth", icon: "shield", valor: 6, pctBase: "0,02%", conv: "54,5%", drop: "45,5%" },
    { nome: "Oferta", icon: "tag", valor: 5, pctBase: "0,01%", conv: "83,3%", drop: "16,7%" },
    { nome: "Acordo", icon: "award", valor: 5, pctBase: "0,01%", conv: "100%", drop: "0,0%" },
  ];

  const top = 1.4, drawW = 6.0, labelW = 2.05, leftX = 0.7;
  const areaH = 6.05 - top, gapY = 0.09;
  const barH = Math.min(0.5, (areaH - (etapas.length - 1) * gapY) / etapas.length - 0.01);
  const maxVal = etapas[0].valor;
  const minBarW = 0.55;

  etapas.forEach((e, i) => {
    const y = top + i * (barH + gapY);
    const isGargalo = !!e.gargalo;
    const w = Math.max(minBarW, (e.valor / maxVal) * drawW);

    s.addImage({ path: `icon_${e.icon}_1E2761.png`, x: leftX, y: y + barH / 2 - 0.16, w: 0.32, h: 0.32 });
    s.addText(e.nome, {
      x: leftX + 0.4, y, w: labelW - 0.4, h: barH, fontFace: "Calibri", fontSize: 13.5,
      bold: true, color: INK, valign: "middle", margin: 0,
    });

    s.addShape("roundRect", {
      x: leftX + labelW, y, w: w, h: barH, rectRadius: 0.06,
      fill: { color: isGargalo ? ORANGE : (i === etapas.length - 1 ? GREEN : NAVY) },
      line: { type: "none" },
    });
    s.addText(e.valor.toLocaleString("pt-BR"), {
      x: leftX + labelW + 0.12, y, w: Math.max(w - 0.2, 0.4), h: barH,
      fontFace: "Calibri", fontSize: 13, bold: true, color: WHITE, valign: "middle", margin: 0,
    });

    s.addText(`${e.pctBase} do envio`, {
      x: leftX + labelW + w + 0.15, y, w: 1.7, h: barH, fontFace: "Calibri", fontSize: 11,
      color: MUTED, valign: "middle", margin: 0,
    });

    if (e.drop != null) {
      const semPerda = e.drop === "0,0%";
      s.addText([
        { text: `conv. ${e.conv}  `, options: { color: MUTED } },
        semPerda
          ? { text: "sem perda", options: { color: MUTED } }
          : { text: `drop -${e.drop}`, options: { color: isGargalo ? ORANGE : "#B5541A", bold: isGargalo } },
      ], {
        x: leftX + labelW + w + 1.85, y, w: 2.3, h: barH, fontFace: "Calibri", fontSize: 11,
        valign: "middle", margin: 0,
      });
    }
  });

  const calloutY = top + etapas.length * (barH + gapY) + 0.1;
  s.addShape("roundRect", {
    x: 0.7, y: calloutY, w: 11.95, h: 0.62, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 0.92, y: calloutY + 0.15, w: 0.32, h: 0.32 });
  s.addText([
    { text: "Atenção — Home/Auth/Oferta/Acordo não são necessariamente os mesmos destinatários do envio:  ", options: { bold: true, color: "B5541A" } },
    { text: "o relatório de e-mail (Salesforce Journey Builder) não cruza por telefone com o log de CRM das campanhas avulsas — são dois programas de e-mail diferentes.", options: { color: "6B4632" } },
  ], {
    x: 1.35, y: calloutY, w: 11.1, h: 0.62, fontFace: "Calibri", fontSize: 11.5, valign: "middle", margin: 0,
  });

  footer(s, pres, "% do envio = etapa ÷ 37.730 e-mails enviados. Envio/Entrega/Abertura/Clique vêm do Salesforce; Home/Auth/Oferta/Acordo vêm do log de CRM por ação — ver alerta acima sobre cruzamento.");
}

// =====================================================================
// SLIDE 4 — CUSTO DO CANAL (não calculável)
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Custo do canal Email", {
    x: 0.7, y: 0.5, w: 9, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Custo unitário do e-mail (Salesforce Journey Builder) não confirmado até o momento", {
    x: 0.7, y: 1.08, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  s.addShape("roundRect", {
    x: 0.7, y: 1.75, w: 11.95, h: 1.95, rectRadius: 0.1,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1.5 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 1.05, y: 2.0, w: 0.5, h: 0.5 });
  s.addText("Não é possível calcular o custo do canal Email", {
    x: 1.8, y: 1.97, w: 10.5, h: 0.45, fontFace: "Cambria", fontSize: 18, bold: true, color: "B5541A", margin: 0,
  });
  s.addText(
    "Diferente de SMS, RCS e WhatsApp (Ötima/Airys), o custo unitário do envio de e-mail via Salesforce Journey Builder ainda não foi confirmado pelo negócio. " +
    "Para não distorcer a análise, nenhum valor de custo foi estimado ou inventado para este canal — o e-mail fica de fora do \"Investimento total do período\" (R$ 7.887,49) " +
    "usado nos demais capítulos até que essa informação seja formalizada.",
    {
      x: 1.05, y: 2.55, w: 11.2, h: 1.1, fontFace: "Calibri", fontSize: 12.5, color: "6B4632", valign: "top", margin: 0, lineSpacing: 18,
    }
  );

  s.addText("Investimento total do período (todos os canais)", {
    x: 0.7, y: 3.95, w: 8, h: 0.32, fontFace: "Calibri", fontSize: 13.5, bold: true, color: NAVY, margin: 0,
  });
  {
    const linhasInv = [
      ["SMS (Kolmeya)", "R$ 5.036,38", "63,9%"],
      ["RCS (Ötima)", "R$ 753,48", "9,6%"],
      ["WhatsApp (Ötima + Airys)", "R$ 246,59", "3,1%"],
      ["Lemit — enriquecimento de dados (julho)", "R$ 1.851,04", "23,5%"],
    ];
    const ix = 0.7, iy = 4.3, iw = 8.05;
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

  footer(s, pres, "Nenhum valor de custo foi inventado ou estimado para o Email. Assim que o valor unitário for confirmado pelo negócio, este slide passa a ter os mesmos indicadores dos demais canais.");
}

// =====================================================================
// SLIDE 5 — VISÃO EXECUTIVA
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Visão executiva — Email", {
    x: 0.7, y: 0.5, w: 9, h: 0.55, fontFace: "Cambria", fontSize: 28, bold: true, color: WHITE, margin: 0,
  });
  s.addText("O que essa análise já responde", {
    x: 0.7, y: 1.05, w: 9, h: 0.35, fontFace: "Calibri", fontSize: 13, color: ICE, margin: 0,
  });

  const perguntas = [
    ["E-mails enviados", "37.730"],
    ["E-mails entregues", "35.615 (94,4%)"],
    ["Taxa de entrega", "94,4% do envio"],
    ["Taxa de abertura", "0,76% do entregue"],
    ["Taxa de clique", "0,10% do entregue (13,7% da abertura)"],
    ["Ações de Home (CRM)", "11"],
    ["Ações de Auth (CRM)", "6"],
    ["Ofertas apresentadas (CRM)", "5"],
    ["Acordos gerados (CRM)", "5"],
    ["Custo total do Email", "Não calculável — unitário não confirmado"],
    ["Prioridade / Grupo Estratégico", "Disponível — base de e-mails avulsos do CRM (5.535 destinatários)"],
    ["Quebra mensal (Jul x Ago)", "Não aplicável — dado concentrado em julho"],
  ];

  const cols = 3, rows = 4, cw = 3.85, ch = 1.15, x0 = 0.7, y0 = 1.6, gx = 0.15, gy = 0.15;
  perguntas.forEach(([pergunta, resposta], i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
    const isAlerta = resposta.startsWith("Não");
    s.addShape("roundRect", {
      x, y, w: cw, h: ch, rectRadius: 0.08,
      fill: { color: isAlerta ? ORANGE : "2A3572" },
      line: { type: "none" },
    });
    s.addText(pergunta, {
      x: x + 0.2, y: y + 0.14, w: cw - 0.4, h: 0.4, fontFace: "Calibri", fontSize: 11,
      color: isAlerta ? "FDEDE4" : ICE, align: "left", valign: "top", margin: 0,
    });
    s.addText(resposta, {
      x: x + 0.2, y: y + 0.5, w: cw - 0.4, h: 0.6, fontFace: "Calibri", fontSize: 13, bold: true,
      color: WHITE, align: "left", valign: "top", margin: 0,
    });
  });

  s.addText("Indicadores marcados em laranja não puderam ser calculados com os dados disponíveis — não foram estimados nem inventados, conforme diretriz da análise.", {
    x: 0.7, y: 6.85, w: 11.9, h: 0.5, fontFace: "Calibri", fontSize: 11.5, italic: true,
    color: "8FA3D9", margin: 0,
  });
}

pres.writeFile({ fileName: "casas_bahia_email.pptx" }).then(() => console.log("done"));
