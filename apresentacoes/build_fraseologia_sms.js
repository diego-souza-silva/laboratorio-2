const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, makeFooter, slideCapa, makeSlideTabelaFrases, celulaEtapa,
} = require("./lib.js");

const footer = makeFooter("SMS · Fraseologia");
const slideTabelaFrases = makeSlideTabelaFrases(footer);

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "FRASEOLOGIA · CANAL",
  titulo: "SMS",
  subtitulo: "Qual texto de SMS converte melhor, e para qual Prioridade e Grupo Estratégico",
  periodo: "Base: 24 famílias de frase (variações de nome personalizadas agrupadas) · 92.406 SMS disparados",
  etapas: ["Frase", "Disparo", "Home", "Auth", "Oferta", "Acordo"],
});

// =====================================================================
// SLIDE 2 — FRASEOLOGIA POR PRIORIDADE
// =====================================================================
slideTabelaFrases(pres, {
  titulo: "Fraseologia por Prioridade",
  subtitulo: "As 12 frases de maior volume — Acordos gerados por cada uma, abertos por Prioridade (contagem e % da frase)",
  colGrupoLabel: "PRIORIDADE",
  colunas: ["P1", "P2", "P3", "P4", "NC"],
  linhas: [
    ["Feche o mês com mais tranquilidade!...", [1, "33%"], [0, "0%"], [1, "33%"], [1, "33%"], [0, "0%"], 3],
    ["Casas Bahia: não deixe essa oportunidade...", [1, "11%"], [2, "22%"], [3, "33%"], [0, "0%"], [3, "33%"], 9],
    ["Uma nova oportunidade foi liberada...", [3, "75%"], [1, "25%"], [0, "0%"], [0, "0%"], [0, "0%"], 4],
    ["ÚLTIMA OPORTUNIDADE! Sua condição especial...", [0, "0%"], [1, "100%"], [0, "0%"], [0, "0%"], [0, "0%"], 1],
    ["Só hoje! Aproveite a oportunidade...", [0, "0%"], [2, "67%"], [1, "33%"], [0, "0%"], [0, "0%"], 3],
    ["Casas Bahia: negocie de forma rápida!...", [0, "0%"], [4, "100%"], [0, "0%"], [0, "0%"], [0, "0%"], 4],
    ["OFERTA RELÂMPAGO! Sua condição foi atualizada...", [6, "86%"], [0, "0%"], [0, "0%"], [0, "0%"], [1, "14%"], 7],
    ["ATENÇÃO: PRAZO LIMITADO! Consulte hoje...", [1, "50%"], [0, "0%"], [1, "50%"], [0, "0%"], [0, "0%"], 2],
    ["Kitei: Sua oportunidade continua disponível (90% OFF)...", [8, "89%"], [1, "11%"], [0, "0%"], [0, "0%"], [0, "0%"], 9],
    ["EVITE OUTRAS MEDIDAS DE COBRANÇA!...", [8, "67%"], [1, "8%"], [0, "0%"], [0, "0%"], [3, "25%"], 12],
    ["OFERTA SURPRESA! Aproveite hoje...", [6, "86%"], [0, "0%"], [1, "14%"], [0, "0%"], [0, "0%"], 7],
    ["Kitei: Notamos seu interesse!...", [3, "100%"], [0, "0%"], [0, "0%"], [0, "0%"], [0, "0%"], 3],
  ],
  totalLinha: ["Top 12 frases", [37, "58%"], [12, "19%"], [7, "11%"], [1, "2%"], [7, "11%"], 64],
  footerTexto: "Célula = Acordos gerados por essa frase naquela Prioridade, e % sobre o total de Acordos da própria frase (não do canal). P1 domina a maioria das frases — mesmo padrão do canal como um todo. Base cobre 64 dos 101 Acordos de SMS (frases fora do Top 12 somam 18 Acordos; 19 sem frase mapeada).",
});

// =====================================================================
// SLIDE 3 — FRASEOLOGIA POR GRUPO ESTRATÉGICO
// =====================================================================
slideTabelaFrases(pres, {
  titulo: "Fraseologia por Grupo Estratégico",
  subtitulo: "As mesmas 12 frases — Acordos gerados por cada uma, abertos por Grupo Estratégico (contagem e % da frase)",
  colGrupoLabel: "GRUPO ESTRATÉGICO",
  colunas: ["Aband.", "Cadastr.", "Engaj.", "Topo", "NC"],
  linhas: [
    ["Feche o mês com mais tranquilidade!...", [0, "0%"], [0, "0%"], [0, "0%"], [3, "100%"], [0, "0%"], 3],
    ["Casas Bahia: não deixe essa oportunidade...", [0, "0%"], [0, "0%"], [0, "0%"], [6, "67%"], [3, "33%"], 9],
    ["Uma nova oportunidade foi liberada...", [0, "0%"], [0, "0%"], [2, "50%"], [2, "50%"], [0, "0%"], 4],
    ["ÚLTIMA OPORTUNIDADE! Sua condição especial...", [0, "0%"], [0, "0%"], [0, "0%"], [1, "100%"], [0, "0%"], 1],
    ["Só hoje! Aproveite a oportunidade...", [0, "0%"], [0, "0%"], [0, "0%"], [3, "100%"], [0, "0%"], 3],
    ["Casas Bahia: negocie de forma rápida!...", [0, "0%"], [0, "0%"], [2, "50%"], [2, "50%"], [0, "0%"], 4],
    ["OFERTA RELÂMPAGO! Sua condição foi atualizada...", [5, "71%"], [0, "0%"], [1, "14%"], [0, "0%"], [1, "14%"], 7],
    ["ATENÇÃO: PRAZO LIMITADO! Consulte hoje...", [0, "0%"], [0, "0%"], [0, "0%"], [2, "100%"], [0, "0%"], 2],
    ["Kitei: Sua oportunidade continua disponível (90% OFF)...", [0, "0%"], [0, "0%"], [7, "78%"], [2, "22%"], [0, "0%"], 9],
    ["EVITE OUTRAS MEDIDAS DE COBRANÇA!...", [0, "0%"], [0, "0%"], [7, "58%"], [2, "17%"], [3, "25%"], 12],
    ["OFERTA SURPRESA! Aproveite hoje...", [6, "86%"], [0, "0%"], [1, "14%"], [0, "0%"], [0, "0%"], 7],
    ["Kitei: Notamos seu interesse!...", [0, "0%"], [0, "0%"], [2, "67%"], [1, "33%"], [0, "0%"], 3],
  ],
  totalLinha: ["Top 12 frases", [11, "17%"], [0, "0%"], [22, "34%"], [24, "38%"], [7, "11%"], 64],
  footerTexto: "Célula = Acordos gerados por essa frase naquele Grupo Estratégico, e % sobre o total de Acordos da própria frase. \"OFERTA RELÂMPAGO\" e \"OFERTA SURPRESA\" performam melhor em Abandono de Carrinho; as demais concentram em Topo de Funil e Engajado.",
});

// =====================================================================
// SLIDE 4 — FUNIL DE FRASES
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Funil de frases", {
    x: 0.7, y: 0.45, w: 12.4, h: 0.55, fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, margin: 0,
  });
  s.addText([
    { text: "Top 12 frases por volume — Disparo até Acordo, com % de conversão etapa a etapa.  ", options: { color: MUTED } },
    { text: "Melhor conversão: \"EVITE OUTRAS MEDIDAS DE COBRANÇA!\" (0,27%, quase o dobro da média do canal).", options: { color: "1D7A45", bold: true } },
  ], {
    x: 0.7, y: 1.0, w: 11.9, h: 0.45, fontFace: "Calibri", fontSize: 12, valign: "top", margin: 0,
  });

  const headerFill = NAVY, totalFill = "D6E6F5", destaqueFill = "EAF6EF";
  const cols = ["Frase", "Disparo", "Home", "Auth", "Oferta", "Acordo", "% Conv."];
  const colW = [4.4, 1.35, 1.05, 1.05, 1.05, 1.1, 1.35];
  // celula = [numero, "% sobre a etapa anterior"]; Disparo e % Conv. ficam como texto simples.
  const linhas = [
    ["Feche o mês com mais tranquilidade!...", "14.274", [18, "0%"], [18, "100%"], [18, "100%"], [3, "17%"], "0,02%"],
    ["Casas Bahia: não deixe essa oportunidade...", "12.693", [31, "0%"], [28, "90%"], [27, "96%"], [9, "33%"], "0,07%"],
    ["Uma nova oportunidade foi liberada...", "6.578", [37, "1%"], [34, "92%"], [34, "100%"], [4, "12%"], "0,06%"],
    ["ÚLTIMA OPORTUNIDADE! Sua condição especial...", "6.051", [9, "0%"], [9, "100%"], [9, "100%"], [1, "11%"], "0,02%"],
    ["Só hoje! Aproveite a oportunidade...", "5.743", [5, "0%"], [5, "100%"], [4, "80%"], [3, "75%"], "0,05%"],
    ["Casas Bahia: negocie de forma rápida!...", "5.733", [7, "0%"], [7, "100%"], [5, "71%"], [4, "80%"], "0,07%"],
    ["OFERTA RELÂMPAGO! Sua condição foi atualizada...", "5.352", [33, "1%"], [29, "88%"], [29, "100%"], [7, "24%"], "0,13%"],
    ["ATENÇÃO: PRAZO LIMITADO! Consulte hoje...", "5.278", [15, "0%"], [15, "100%"], [15, "100%"], [2, "13%"], "0,04%"],
    ["Kitei: Sua oportunidade continua disponível (90% OFF)...", "4.655", [46, "1%"], [43, "93%"], [43, "100%"], [9, "21%"], "0,19%"],
    ["EVITE OUTRAS MEDIDAS DE COBRANÇA!...", "4.491", [48, "1%"], [46, "96%"], [46, "100%"], [12, "26%"], "0,27%"],
    ["OFERTA SURPRESA! Aproveite hoje...", "3.675", [36, "1%"], [33, "92%"], [33, "100%"], [7, "21%"], "0,19%"],
    ["Kitei: Notamos seu interesse!...", "3.160", [28, "1%"], [25, "89%"], [25, "100%"], [3, "12%"], "0,09%"],
  ];
  const melhorConv = "EVITE OUTRAS MEDIDAS DE COBRANÇA!...";
  const fontSize4 = 10;
  const rows = [];
  rows.push(cols.map((c, i) => ({
    text: c,
    options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize: fontSize4, align: i === 0 ? "left" : "right" },
  })));
  linhas.forEach((linha, i) => {
    const destaque = linha[0] === melhorConv;
    const bg = destaque ? destaqueFill : (i % 2 === 0 ? WHITE : CARDBG);
    rows.push(linha.map((valor, j) => celulaEtapa(valor, {
      fill: { color: bg },
      color: j === 0 ? INK : (j === 6 && destaque ? "1D7A45" : NAVY),
      bold: j === 0 || (destaque && j === 6),
      fontSize: fontSize4,
      align: j === 0 ? "left" : "right",
    })));
  });
  rows.push(["Total (Top 12)", "77.683", [313, "0%"], [292, "93%"], [288, "99%"], [64, "22%"], "0,08%"].map((valor, j) => celulaEtapa(valor, {
    fill: { color: totalFill }, color: NAVY, bold: true, fontSize: fontSize4, align: j === 0 ? "left" : "right",
  })));
  const rowH4 = 0.395;
  const startY4 = 1.48;
  s.addTable(rows, {
    x: 0.7, y: startY4, w: 11.95, colW, rowH: rowH4,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri", autoPage: false, valign: "middle",
  });

  footer(s, pres, "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo. Total do canal (24 frases): Disparo 92.406, Home 490, Auth 450, Oferta 446, Acordo 101, Conv. 0,11% — as 12 frases fora do Top 12 somam 14.723 disparos e 37 Acordos.");
}

pres.writeFile({ fileName: "casas_bahia_fraseologia_sms.pptx" }).then(() => console.log("done"));
