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

function makeFooter(channelLabel) {
  return function footer(slide, pres, text) {
    slide.addText(text, {
      x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: "Calibri", fontSize: 9,
      color: MUTED, align: "left", margin: 0,
    });
    slide.addText(`Casas Bahia · Canal ${channelLabel}`, {
      x: 11.0, y: 7.12, w: 2.3, h: 0.3, fontFace: "Calibri", fontSize: 9,
      color: MUTED, align: "right", margin: 0,
    });
  };
}

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

function makeSlidePrioridadeGrupoEstrategico(footer) {
  return function slidePrioridadeGrupoEstrategico(pres, { titulo, subtitulo, linhasPrioridade, linhasGE, total, footerTexto }) {
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
  };
}

function makeSlideFunilCompleto(footer) {
  return function slideFunilCompleto(pres, { titulo, subtitulo, etapas, gargaloTitulo, gargaloTexto, footerTexto }) {
    const s = pres.addSlide();
    s.addText(titulo, {
      x: 0.7, y: 0.45, w: 11, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: NAVY, margin: 0,
    });
    s.addText(subtitulo, {
      x: 0.7, y: 1.0, w: 11, h: 0.35, fontFace: "Calibri", fontSize: 13, color: MUTED, margin: 0,
    });

    // altura de linha calibrada dinamicamente pro numero de etapas caber sem
    // estourar o slide (8 etapas com Lido precisam de barras mais baixas que
    // as 7 etapas do funil de SMS)
    const nEtapas = etapas.length;
    const top = 1.4;
    const areaH = 6.05 - top; // ate pouco antes do callout
    const gapY = 0.1;
    const barH = Math.min(0.5, (areaH - (nEtapas - 1) * gapY) / nEtapas - 0.01);
    const drawW = 6.0, labelW = 2.05, leftX = 0.7;
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

      s.addText(`${e.pctDisparo} do disparo`, {
        x: leftX + labelW + w + 0.15, y, w: 1.7, h: barH, fontFace: "Calibri", fontSize: 11,
        color: MUTED, valign: "middle", margin: 0,
      });

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
  };
}

function slideCapa(pres, { capitulo, titulo, subtitulo, periodo, etapas }) {
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText(capitulo, {
    x: 0.9, y: 1.55, w: 6, h: 0.4, fontFace: "Calibri", fontSize: 14,
    color: ICE, bold: true, charSpacing: 3, margin: 0,
  });
  s.addText(titulo, {
    x: 0.85, y: 1.9, w: 8, h: 1.3, fontFace: "Cambria", fontSize: 64,
    color: WHITE, bold: true, margin: 0,
  });
  s.addText(subtitulo, {
    x: 0.9, y: 3.15, w: 8.5, h: 0.6, fontFace: "Calibri", fontSize: 18,
    color: ICE, margin: 0,
  });
  s.addText(periodo, {
    x: 0.9, y: 3.75, w: 10.5, h: 0.4, fontFace: "Calibri", fontSize: 13,
    color: "8FA3D9", margin: 0,
  });

  const n = etapas.length;
  const startX = 0.9, totalW = 11.5, boxW = Math.min(1.65, totalW / n - 0.3);
  const gap = totalW / n;
  const y = 5.35;
  etapas.forEach((et, i) => {
    const x = startX + i * gap;
    s.addShape("roundRect", {
      x, y, w: boxW, h: 0.62, rectRadius: 0.31,
      fill: { color: i === etapas.length - 1 ? GREEN : "2A3572" },
      line: { type: "none" },
    });
    s.addText(et, {
      x, y, w: boxW, h: 0.62, fontFace: "Calibri", fontSize: 11.5, bold: true,
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

function celulaEtapa(valor, opts) {
  if (!Array.isArray(valor)) {
    return { text: String(valor), options: { ...opts } };
  }
  const [numero, pctEtapa] = valor;
  return {
    text: [
      { text: String(numero), options: { breakLine: true } },
      { text: pctEtapa, options: { fontSize: (opts.fontSize || 10.5) - 2.3, color: MUTED, bold: false } },
    ],
    options: { ...opts },
  };
}

function makeSlideFunilSegmentado(footer) {
  return function slideFunilSegmentado(pres, {
    titulo, subtitulo, colunaLabel, colunasEtapas, linhas, total,
    insightTitulo, insightTexto, footerTexto,
  }) {
    const s = pres.addSlide();
    s.addText(titulo, {
      x: 0.7, y: 0.45, w: 12.4, h: 0.55, fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, margin: 0,
    });
    s.addText(subtitulo, {
      x: 0.7, y: 1.02, w: 11.9, h: 0.35, fontFace: "Calibri", fontSize: 12.5, color: MUTED, margin: 0,
    });

    const headerFill = NAVY;
    const totalFill = "D6E6F5";
    const nEtapas = colunasEtapas.length;
    const cols = [colunaLabel, ...colunasEtapas, "% Conv."];
    const labelW = 1.9, convW = 1.85;
    const stageW = (11.95 - labelW - convW) / nEtapas;
    const colW = [labelW, ...Array(nEtapas).fill(stageW), convW];
    const rowH = 0.5;
    const fontSize = nEtapas >= 8 ? 10.5 : 11.5;

    const rows = [];
    rows.push(cols.map((c, i) => ({
      text: c,
      options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize, align: i === 0 ? "left" : "right" },
    })));

    linhas.forEach((linha, i) => {
      const bg = i % 2 === 0 ? WHITE : CARDBG;
      rows.push(linha.map((valor, j) => celulaEtapa(valor, {
        fill: { color: bg },
        color: j === 0 ? INK : (j === linha.length - 1 ? "1D7A45" : INK),
        bold: j === 0 || j === linha.length - 1,
        fontSize,
        align: j === 0 ? "left" : "right",
      })));
    });

    rows.push(total.map((valor, j) => celulaEtapa(valor, {
      fill: { color: totalFill }, color: NAVY, bold: true, fontSize,
      align: j === 0 ? "left" : "right",
    })));

    s.addTable(rows, {
      x: 0.7, y: 1.5, w: 11.95, colW, rowH,
      border: { type: "solid", color: LINE, pt: 0.75 },
      fontFace: "Calibri", autoPage: false, valign: "middle",
    });

    const calloutY = 1.5 + rows.length * rowH + 0.15;
    s.addShape("roundRect", {
      x: 0.7, y: calloutY, w: 11.95, h: 0.58, rectRadius: 0.08,
      fill: { color: "EAF6EF" }, line: { color: GREEN, width: 1 },
    });
    s.addImage({ path: "icon_award_2F9E6E.png", x: 0.92, y: calloutY + 0.13, w: 0.32, h: 0.32 });
    s.addText([
      { text: `${insightTitulo}  `, options: { bold: true, color: "1D7A45" } },
      { text: insightTexto, options: { color: "2F5741" } },
    ], {
      x: 1.35, y: calloutY, w: 11.1, h: 0.58, fontFace: "Calibri", fontSize: 12, valign: "middle", margin: 0,
    });

    footer(s, pres, footerTexto);
  };
}

function slideInvestimentoTotal(s, { x, y, w, linhas, total }) {
  const headerFill = NAVY;
  const totalFill = "D6E6F5";
  const rows = [];
  rows.push([
    { text: "INVESTIMENTO NO PERÍODO", options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 11.5, align: "left" } },
    { text: "Valor", options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 11.5, align: "right" } },
    { text: "%", options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: 11.5, align: "right" } },
  ]);
  linhas.forEach(([nome, valor, pct], i) => {
    const bg = i % 2 === 0 ? WHITE : CARDBG;
    rows.push([
      { text: nome, options: { fill: { color: bg }, color: INK, fontSize: 11, align: "left" } },
      { text: valor, options: { fill: { color: bg }, color: INK, fontSize: 11, align: "right" } },
      { text: pct, options: { fill: { color: bg }, color: MUTED, fontSize: 11, align: "right" } },
    ]);
  });
  rows.push([
    { text: "Total do período", options: { fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 11.5, align: "left" } },
    { text: total, options: { fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 11.5, align: "right" } },
    { text: "100%", options: { fill: { color: totalFill }, color: NAVY, bold: true, fontSize: 11.5, align: "right" } },
  ]);
  s.addTable(rows, {
    x, y, w, colW: [w - 2.2, 1.35, 0.85], rowH: 0.29,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri", autoPage: false, valign: "middle",
  });
}

// Tabela: Frase/Mensagem (linhas) x Grupo (colunas), célula = [contagem, %] —
// reusada pelas decks de fraseologia (frase de SMS ou mensagem de WhatsApp/RCS
// cruzada com Prioridade ou Grupo Estratégico).
function makeSlideTabelaFrases(footer) {
  return function slideTabelaFrases(pres, {
    titulo, subtitulo, colGrupoLabel, colunas, linhas, totalLinha, footerTexto,
  }) {
    const s = pres.addSlide();
    s.addText(titulo, {
      x: 0.7, y: 0.45, w: 12.4, h: 0.55, fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, margin: 0,
    });
    s.addText(subtitulo, {
      x: 0.7, y: 1.02, w: 11.9, h: 0.5, fontFace: "Calibri", fontSize: 12.5, color: MUTED, margin: 0,
    });

    const headerFill = NAVY, totalFill = "D6E6F5";
    const nCols = colunas.length;
    const labelW = 4.05, totalW = 1.4;
    const groupW = (11.95 - labelW - totalW) / nCols;
    const colW = [labelW, ...Array(nCols).fill(groupW), totalW];
    const startY = 1.42;
    const availH = 7.0 - startY;
    const totalRows = linhas.length + 2;
    const rowH = Math.min(0.5, availH / totalRows);
    const fontSize = rowH >= 0.45 ? 10.5 : (rowH >= 0.36 ? 9.5 : 8.5);

    const cabecalho = ["FRASE / MENSAGEM", ...colunas, "Total"];
    const rows = [];
    rows.push(cabecalho.map((c, i) => ({
      text: c,
      options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: fontSize - 0.5, align: i === 0 ? "left" : "right" },
    })));

    linhas.forEach((linha, i) => {
      const bg = i % 2 === 0 ? WHITE : CARDBG;
      rows.push(linha.map((valor, j) => celulaEtapa(valor, {
        fill: { color: bg },
        color: j === 0 ? INK : (j === linha.length - 1 ? "1D7A45" : INK),
        bold: j === 0 || j === linha.length - 1,
        fontSize,
        align: j === 0 ? "left" : "right",
      })));
    });

    rows.push(totalLinha.map((valor, j) => celulaEtapa(valor, {
      fill: { color: totalFill }, color: NAVY, bold: true, fontSize,
      align: j === 0 ? "left" : "right",
    })));

    s.addTable(rows, {
      x: 0.7, y: startY, w: 11.95, colW, rowH,
      border: { type: "solid", color: LINE, pt: 0.75 },
      fontFace: "Calibri", autoPage: false, valign: "middle",
    });

    footer(s, pres, footerTexto);
  };
}

module.exports = {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, statCard, makeFooter, tabelaDinamica, celulaEtapa,
  makeSlidePrioridadeGrupoEstrategico, makeSlideFunilCompleto, slideCapa,
  makeSlideFunilSegmentado, slideInvestimentoTotal, makeSlideTabelaFrases,
};
