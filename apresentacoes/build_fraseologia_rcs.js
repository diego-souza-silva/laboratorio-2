const {
  NAVY, ICE, WHITE, ORANGE, GREEN, INK, MUTED, CARDBG, LINE,
  newPres, statCard, makeFooter, slideCapa, tabelaDinamica,
} = require("./lib.js");

const footer = makeFooter("RCS · Fraseologia");

const pres = newPres();
pres.defineSlideMaster({ title: "MASTER", background: { color: WHITE } });

// =====================================================================
// SLIDE 1 — CAPA
// =====================================================================
slideCapa(pres, {
  capitulo: "FRASEOLOGIA · CANAL",
  titulo: "RCS",
  subtitulo: "Sem variação de texto neste período — um único modelo de mensagem",
  periodo: "Base: 1 modelo de mensagem, 8.372 disparos (04/08)",
  etapas: ["Mensagem", "Disparo", "Home", "Auth", "Oferta", "Acordo"],
});

// =====================================================================
// SLIDE 2 — SEM VARIAÇÃO DE FRASE (nota + Prioridade/GE do único texto)
// =====================================================================
{
  const s = pres.addSlide();
  s.addText("RCS teve um único texto-modelo no período", {
    x: 0.7, y: 0.5, w: 11, h: 0.6, fontFace: "Cambria", fontSize: 26, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Sem A/B de frase para comparar — os 8.372 disparos usaram o mesmo texto", {
    x: 0.7, y: 1.08, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 14, color: MUTED, margin: 0,
  });

  s.addShape("roundRect", {
    x: 0.7, y: 1.55, w: 11.95, h: 1.15, rectRadius: 0.1,
    fill: { color: CARDBG }, line: { color: LINE, width: 1 },
  });
  s.addText(
    "\"{nome}, sua oferta exclusiva está disponível! A Kitei, parceira oficial das Casas Bahia, liberou uma condição especial " +
    "para você colocar sua pendência em dia. É rápido: faça sua simulação em menos de 2 minutos e veja quanto você pode " +
    "economizar na negociação. Acesse hoje o Portal Kitei e confira sua oferta!\"",
    { x: 1.0, y: 1.68, w: 11.35, h: 0.9, fontFace: "Calibri", fontSize: 12, italic: true, color: INK, valign: "top", margin: 0, lineSpacing: 16 }
  );

  statCard(s, 0.7, 2.85, 3.85, 1.3, {
    icon: "icon_send_1E2761.png", value: "8.372", valueSize: 19, label: "Disparados com este texto",
  });
  statCard(s, 4.75, 2.85, 3.85, 1.3, {
    icon: "icon_home_1E2761.png", value: "65", valueSize: 19, label: "Ações de Home geradas",
  });
  statCard(s, 8.8, 2.85, 3.85, 1.3, {
    icon: "icon_award_2F9E6E.png", value: "18", valueSize: 19, valueColor: GREEN, label: "Acordos gerados (0,22% de conversão)",
  });

  tabelaDinamica(s, {
    x: 0.7, y: 4.3, w: 5.6, titulo: "ACORDOS POR PRIORIDADE",
    linhas: [
      ["P1 · Máxima", "0", "0%"],
      ["P2 · Alta", "9", "50%"],
      ["P3 · Média", "7", "39%"],
      ["P4 · Baixa", "2", "11%"],
      ["Não Classificado", "0", "0%"],
    ],
    total: "18",
  });
  tabelaDinamica(s, {
    x: 6.75, y: 4.3, w: 5.9, titulo: "ACORDOS POR GRUPO ESTRATÉGICO",
    linhas: [
      ["Abandono Carrinho", "0", "0%"],
      ["Cadastrado", "0", "0%"],
      ["Engajado", "8", "44%"],
      ["Topo de Funil", "10", "56%"],
      ["Não Classificado", "0", "0%"],
    ],
    total: "18",
  });

  footer(s, pres, "Números de CRM aqui vêm do cruzamento por telefone (log de CRM inteiro), por isso 18 Acordos — acima dos 4 do capítulo RCS, que usa o cruzamento restrito à campanha (utm). Ver nota metodológica no capítulo RCS sobre essa diferença de escopo.");
}

pres.writeFile({ fileName: "casas_bahia_fraseologia_rcs.pptx" }).then(() => console.log("done"));
