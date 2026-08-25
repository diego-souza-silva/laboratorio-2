const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, statCard, makeFooter, slideCapa, celulaEtapa,
} = require("./lib.js");

const footer = makeFooter("Email · Fraseologia");

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "FRASEOLOGIA · CANAL",
  titulo: "EMAIL",
  subtitulo: "Qual assunto de e-mail gera mais abertura e clique — sem cruzamento com CRM",
  periodo: "Base: 16 assuntos, 37.730 envios (Salesforce Journey Builder, julho)",
  etapas: ["Assunto", "Envio", "Entrega", "Abertura", "Clique"],
});

// =====================================================================
// SLIDE 2 — DESTAQUES E NOTA METODOLÓGICA
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Melhores assuntos de e-mail", {
    x: 0.7, y: 0.5, w: 11, h: 0.6, fontFace: "Cambria", fontSize: 26, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Entre os assuntos com volume relevante (≥ 100 envios) — ranking completo nos próximos slides", {
    x: 0.7, y: 1.08, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  statCard(s, 0.7, 1.7, 3.85, 1.7, {
    icon: "icon_eye_1E2761.png", value: "3,49%", valueSize: 26, valueColor: GREEN,
    label: "Melhor abertura: \"Iniciativa do Governo Federal\" (43 de 1.231 entregues)",
  });
  statCard(s, 4.75, 1.7, 3.85, 1.7, {
    icon: "icon_click_1E2761.png", value: "36,36%", valueSize: 26, valueColor: GREEN,
    label: "Melhor CTOR: \"Sua conta foi atualizada\" (8 cliques em 22 aberturas)",
  });
  statCard(s, 8.8, 1.7, 3.85, 1.7, {
    icon: "icon_send_1E2761.png", value: "7.121", valueSize: 26,
    label: "Mais enviado: \"Seu recomeço está aqui\" (18,9% do total de envios)",
  });

  s.addShape("roundRect", {
    x: 0.7, y: 3.65, w: 11.95, h: 1.1, rectRadius: 0.1,
    fill: { color: CARDBG }, line: { color: LINE, width: 1 },
  });
  s.addText([
    { text: "Por que não tem Acordo/CRM aqui?  ", options: { bold: true, color: NAVY } },
    { text: "O relatório de e-mail (Salesforce Journey Builder) é agregado por assunto/dia — não tem telefone nem e-mail por linha, então não há como cruzar com o log de CRM nem abrir por Prioridade/Grupo Estratégico neste nível. Isso é diferente do capítulo Email, que cruza uma base separada (campanhas avulsas, por e-mail do destinatário) com o CRM por telefone.", options: { color: INK } },
  ], {
    x: 1.0, y: 3.8, w: 11.35, h: 0.85, fontFace: "Calibri", fontSize: 12, valign: "top", margin: 0, lineSpacing: 16,
  });

  s.addShape("roundRect", {
    x: 0.7, y: 4.95, w: 11.95, h: 0.85, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 0.92, y: 5.12, w: 0.32, h: 0.32 });
  s.addText([
    { text: "Cuidado com amostra pequena:  ", options: { bold: true, color: "B5541A" } },
    { text: "\"Reduzimos o seu débito\" (23,5% de abertura) e \"Ação GOV.BR: Desenrola Brasil\" tiveram só 17–19 envios cada — 1 abertura a mais ou a menos já muda dezenas de pontos percentuais. Não são recomendação de assunto, são ruído estatístico.", options: { color: "6B4632" } },
  ], {
    x: 1.35, y: 4.95, w: 11.1, h: 0.85, fontFace: "Calibri", fontSize: 12, valign: "middle", margin: 0,
  });

  footer(s, pres, "Abertura = Aberturas únicas ÷ Entregues. CTOR (click-to-open) = Cliques ÷ Aberturas. \"Volume relevante\" = ≥ 100 envios, para excluir os 3 assuntos-teste com < 20 envios da leitura de destaque.");
}

// =====================================================================
// SLIDES 3-4 — RANKING COMPLETO POR TAXA DE ABERTURA (8 assuntos por slide —
// 16 linhas com célula de 2 linhas numa tabela só estoura a altura nominal
// e sobrepõe o rodapé, ver armadilha de rowH no CLAUDE.md)
// =====================================================================
const headerFill = NAVY, totalFill = "D6E6F5", noiseFill = "FDEDE4";
const labelW = 4.6, colW = [labelW, 1.5, 1.5, 2.2, 2.15];
const cabecalho = ["ASSUNTO", "ENVIOS", "ENTREGUES", "ABERTURAS", "CLIQUES (CTOR)"];

const todasLinhas = [
  ["Reduzimos o seu débito", "17", "17", [4, "23,53%"], [0, "—"], true],
  ["Sua conta pode ser bloqueada a qualquer momento", "19", "19", [2, "10,53%"], [1, "CTOR 50,00%"], true],
  ["Iniciativa do Governo Federal", "1.310", "1.231", [43, "3,49%"], [6, "CTOR 13,95%"], false],
  ["⚠️ Valor em abatimento", "1.261", "1.185", [38, "3,21%"], [0, "—"], false],
  ["Retome a sua renegociação e pare de acumular juros", "1.136", "1.065", [21, "1,97%"], [1, "CTOR 4,76%"], false],
  ["Sua conta foi atualizada", "1.340", "1.254", [22, "1,75%"], [8, "CTOR 36,36%"], false],
  ["Seu recomeço está aqui, %%Firstname%%", "7.121", "6.713", [86, "1,28%"], [15, "CTOR 17,44%"], false],
  ["É pegar ou largar 🚨🚨🚨", "1.100", "1.041", [9, "0,86%"], [1, "CTOR 11,11%"], false],
  ["Tem algo te esperando ⏳⏳", "1.104", "1.043", [5, "0,48%"], [0, "—"], false],
  ["Sua nova condição ainda está esperando", "6.991", "6.607", [22, "0,33%"], [1, "CTOR 4,55%"], false],
  ["Conheça a história da Ana Paula", "1.263", "1.186", [3, "0,25%"], [0, "—"], false],
  ["Só falta o seu SIM, %%FirstName%% 😉", "6.972", "6.595", [9, "0,14%"], [1, "CTOR 11,11%"], false],
  ["%%firstname%%, milhares já limparam o nome. Falta você ⭐", "6.970", "6.592", [6, "0,09%"], [2, "CTOR 33,33%"], false],
  ["Ficou alguma dúvida no caminho?", "1.090", "1.031", [0, "0,00%"], [1, "—"], false],
  ["Ação GOV.BR: Desenrola Brasil", "19", "19", [0, "0,00%"], [0, "—"], true],
  ["Já sabe qual seu Score? 👀👀", "17", "17", [0, "0,00%"], [0, "—"], true],
];
const totalGeral = ["Total (16 assuntos)", "37.730", "35.615", [270, "0,76%"], [37, "CTOR 13,70%"]];

function slideRanking({ titulo, subtitulo, linhas, comTotal, footerTexto }) {
  const s = pres.addSlide();
  s.addText(titulo, {
    x: 0.7, y: 0.45, w: 11, h: 0.55, fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, margin: 0,
  });
  s.addText(subtitulo, {
    x: 0.7, y: 1.0, w: 11.5, h: 0.35, fontFace: "Calibri", fontSize: 12.5, color: MUTED, margin: 0,
  });

  const startY = 1.5;
  const availH = 7.0 - startY;
  const totalRows = linhas.length + 1 + (comTotal ? 1 : 0);
  const rowH = Math.min(0.5, availH / totalRows);
  const fontSize = rowH >= 0.45 ? 10.5 : (rowH >= 0.36 ? 9.5 : 8.5);

  const rows = [];
  rows.push(cabecalho.map((c, i) => ({
    text: c,
    options: { fill: { color: headerFill }, color: WHITE, bold: true, fontSize, align: i === 0 ? "left" : "right" },
  })));
  linhas.forEach((linha, i) => {
    const [nome, envios, entregues, aberturas, cliques, ruido] = linha;
    const bg = ruido ? noiseFill : (i % 2 === 0 ? WHITE : CARDBG);
    const cor = ruido ? "B5541A" : INK;
    rows.push([
      { text: nome, options: { fill: { color: bg }, color: cor, bold: false, fontSize, align: "left" } },
      { text: envios, options: { fill: { color: bg }, color: cor, fontSize, align: "right" } },
      { text: entregues, options: { fill: { color: bg }, color: cor, fontSize, align: "right" } },
      celulaEtapa(aberturas, { fill: { color: bg }, color: cor, bold: true, fontSize, align: "right" }),
      celulaEtapa(cliques, { fill: { color: bg }, color: cor, fontSize, align: "right" }),
    ]);
  });
  if (comTotal) {
    rows.push(totalGeral.map((valor, j) => celulaEtapa(valor, {
      fill: { color: totalFill }, color: NAVY, bold: true, fontSize, align: j === 0 ? "left" : "right",
    })));
  }

  s.addTable(rows, {
    x: 0.7, y: startY, w: 11.95, colW, rowH,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri", autoPage: false, valign: "middle",
  });

  footer(s, pres, footerTexto);
}

slideRanking({
  titulo: "Ranking dos assuntos (1 a 8)",
  subtitulo: "Os 16 assuntos do período, ordenados por taxa de abertura (Aberturas ÷ Entregues) — continua no próximo slide",
  linhas: todasLinhas.slice(0, 8),
  comTotal: false,
  footerTexto: "Linhas em laranja = amostra mínima (< 20 envios), leitura só ilustrativa. Abertura = Aberturas ÷ Entregues; CTOR = Cliques ÷ Aberturas (\"—\" quando não há abertura registrada).",
});

slideRanking({
  titulo: "Ranking dos assuntos (9 a 16)",
  subtitulo: "Continuação — mesmo ordenamento por taxa de abertura",
  linhas: todasLinhas.slice(8),
  comTotal: true,
  footerTexto: "Linhas em laranja = amostra mínima (< 20 envios), leitura só ilustrativa. Total bate com a volumetria do capítulo Email (37.730 envios, 0,76% de abertura sobre entregues, 13,7% de CTOR).",
});

pres.writeFile({ fileName: "casas_bahia_fraseologia_email.pptx" }).then(() => console.log("done"));
