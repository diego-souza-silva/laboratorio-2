const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, makeFooter, slideCapa, makeSlideTabelaFrases, celulaEtapa,
} = require("./lib.js");

const footer = makeFooter("WhatsApp · Fraseologia");
const slideTabelaFrases = makeSlideTabelaFrases(footer);

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "FRASEOLOGIA · CANAL",
  titulo: "WHATSAPP",
  subtitulo: "Qual mensagem de WhatsApp converte melhor, e para qual Prioridade e Grupo Estratégico",
  periodo: "Base: 4 modelos de mensagem Ötima (3.777 disparos) · Airys usa 1 template opaco (\"cb_topo_cpf_registrado_v1\"), sem texto decodificável",
  etapas: ["Mensagem", "Disparo", "Home", "Auth", "Oferta", "Acordo"],
});

// =====================================================================
// SLIDE 2 — FRASEOLOGIA POR PRIORIDADE
// =====================================================================
slideTabelaFrases(pres, {
  titulo: "Fraseologia por Prioridade",
  subtitulo: "Os 4 modelos de mensagem Ötima — Acordos gerados por cada um, abertos por Prioridade (contagem e % da mensagem)",
  colGrupoLabel: "PRIORIDADE",
  colunas: ["P1", "P2", "P3", "P4", "NC"],
  linhas: [
    ["Msg 1 — Contrato com parcela em aberto", [0, "0%"], [2, "15%"], [5, "38%"], [1, "8%"], [5, "38%"], 13],
    ["Msg 2 — Atualização da sua conta", [4, "50%"], [0, "0%"], [0, "0%"], [0, "0%"], [4, "50%"], 8],
    ["Msg 3 — Negociação com etapa pendente", [3, "60%"], [0, "0%"], [0, "0%"], [0, "0%"], [2, "40%"], 5],
    ["Msg 4 — Alteração no saldo da conta", [0, "—"], [0, "—"], [0, "—"], [0, "—"], [0, "—"], 0],
  ],
  totalLinha: ["Total (4 mensagens)", [7, "27%"], [2, "8%"], [5, "19%"], [1, "4%"], [11, "42%"], 26],
  footerTexto: "Célula = Acordos gerados por essa mensagem naquela Prioridade, e % sobre o total de Acordos da própria mensagem. Msg 4 teve só 7 disparos (praticamente um teste) e não gerou Acordo. Total de 26 Acordos aqui é menor que os 30 do capítulo WhatsApp Ötima — 4 telefones não têm mensagem-modelo mapeada no retorno.",
});

// =====================================================================
// SLIDE 3 — FRASEOLOGIA POR GRUPO ESTRATÉGICO
// =====================================================================
slideTabelaFrases(pres, {
  titulo: "Fraseologia por Grupo Estratégico",
  subtitulo: "Os mesmos 4 modelos — Acordos gerados por cada um, abertos por Grupo Estratégico (contagem e % da mensagem)",
  colGrupoLabel: "GRUPO ESTRATÉGICO",
  colunas: ["Aband.", "Cadastr.", "Engaj.", "Topo", "NC"],
  linhas: [
    ["Msg 1 — Contrato com parcela em aberto", [0, "0%"], [0, "0%"], [4, "31%"], [4, "31%"], [5, "38%"], 13],
    ["Msg 2 — Atualização da sua conta", [0, "0%"], [0, "0%"], [4, "50%"], [0, "0%"], [4, "50%"], 8],
    ["Msg 3 — Negociação com etapa pendente", [1, "20%"], [0, "0%"], [1, "20%"], [1, "20%"], [2, "40%"], 5],
    ["Msg 4 — Alteração no saldo da conta", [0, "—"], [0, "—"], [0, "—"], [0, "—"], [0, "—"], 0],
  ],
  totalLinha: ["Total (4 mensagens)", [1, "4%"], [0, "0%"], [9, "35%"], [5, "19%"], [11, "42%"], 26],
  footerTexto: "Célula = Acordos gerados por essa mensagem naquele Grupo Estratégico, e % sobre o total de Acordos da própria mensagem. Engajado responde melhor às Msg 1 e Msg 2 — mesmo padrão de \"quem já teve contato prévio converte mais\" visto no SMS.",
});

// =====================================================================
// SLIDE 4 — FUNIL DE MENSAGENS
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("Funil de mensagens", {
    x: 0.7, y: 0.45, w: 12.4, h: 0.55, fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, margin: 0,
  });
  s.addText([
    { text: "Os 4 modelos Ötima — Disparo até Acordo, com % de conversão etapa a etapa.  ", options: { color: MUTED } },
    { text: "Melhor conversão: Msg 2 \"Atualização da sua conta\" (1,30%).", options: { color: "1D7A45", bold: true } },
  ], {
    x: 0.7, y: 1.0, w: 11.9, h: 0.45, fontFace: "Calibri", fontSize: 12, valign: "top", margin: 0,
  });

  const headerFill = NAVY, totalFill = "D6E6F5", destaqueFill = "EAF6EF";
  const cols = ["Mensagem", "Disparo", "Home", "Auth", "Oferta", "Acordo", "% Conv."];
  const colW = [4.4, 1.35, 1.05, 1.05, 1.05, 1.1, 1.35];
  const linhas = [
    ["Msg 1 — Contrato com parcela em aberto", "2.567", [114, "4%"], [112, "98%"], [103, "92%"], [13, "13%"], "0,51%"],
    ["Msg 2 — Atualização da sua conta", "614", [48, "8%"], [48, "100%"], [42, "88%"], [8, "19%"], "1,30%"],
    ["Msg 3 — Negociação com etapa pendente", "589", [105, "18%"], [87, "83%"], [84, "97%"], [5, "6%"], "0,85%"],
    ["Msg 4 — Alteração no saldo da conta", "7", [0, "0%"], [0, "—"], [0, "—"], [0, "—"], "0,00%"],
  ];
  const melhorConv = "Msg 2 — Atualização da sua conta";
  const fontSize4 = 11;
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
  rows.push(["Total (4 mensagens)", "3.777", [267, "7%"], [247, "93%"], [229, "93%"], [26, "11%"], "0,69%"].map((valor, j) => celulaEtapa(valor, {
    fill: { color: totalFill }, color: NAVY, bold: true, fontSize: fontSize4, align: j === 0 ? "left" : "right",
  })));
  s.addTable(rows, {
    x: 0.7, y: 1.55, w: 11.95, colW, rowH: 0.55,
    border: { type: "solid", color: LINE, pt: 0.75 },
    fontFace: "Calibri", autoPage: false, valign: "middle",
  });

  s.addShape("roundRect", {
    x: 0.7, y: 5.05, w: 11.95, h: 0.85, rectRadius: 0.08,
    fill: { color: "FDEDE4" }, line: { color: ORANGE, width: 1 },
  });
  s.addImage({ path: "icon_alert_E8622C.png", x: 0.92, y: 5.22, w: 0.32, h: 0.32 });
  s.addText([
    { text: "Airys não entra nesta tabela:  ", options: { bold: true, color: "B5541A" } },
    { text: "usa 1 template opaco (\"cb_topo_cpf_registrado_v1\", sem texto decodificável no retorno). Volumetria própria: 707 disparados, 1 Home, 1 Auth, 1 Oferta, 1 Acordo — ver capítulo WhatsApp.", options: { color: "6B4632" } },
  ], {
    x: 1.35, y: 5.05, w: 11.1, h: 0.85, fontFace: "Calibri", fontSize: 12, valign: "middle", margin: 0,
  });

  footer(s, pres, "% embaixo de cada valor = conversão sobre a etapa anterior. % Conv. = Acordo ÷ Disparo. Total (Ötima, 4 mensagens) cobre 26 dos 30 Acordos do capítulo WhatsApp Ötima — 4 telefones sem mensagem-modelo mapeada.");
}

pres.writeFile({ fileName: "casas_bahia_fraseologia_whatsapp.pptx" }).then(() => console.log("done"));
