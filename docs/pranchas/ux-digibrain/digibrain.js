/* Prancha D1: o DigiBrain "scan holografico" (direcao A). So desenho; nenhum codigo do jogo e nenhum numero copiado a mao: tudo o que
   aparece sai do dados.json (Motor.reproduzir(4242, log, 13).digibrain(), gravado por dados_digibrain.mts) ou da estrutura do cerebro A
   (os nomes das entradas, regras e acoes, na ordem do motor). Os textos sao os do painel de hoje (DigiBrain.tsx e MapaPesos.tsx), citados
   em cada tabela. As posicoes dos pontos sao so desenho (a forma de cerebro e uma metafora; a tela diz isso). */
"use strict";

/* o caminho dos dados (ao lado, docs/pranchas/ux-digibrain/dados.json) */
const DADOS = "dados.json";
/* opcional: a url de uma captura da ilha, para o fundo atras do modo scan a 1920 (fora do git); null = a cor neutra */
const FUNDO_ILHA = null;

/* ---------------------------------------------------------------- a estrutura do cerebro A (so os nomes, na ordem do motor) */
const ENTRADAS_LOBOS = ["vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "ticks_sem_cuidado"]; // motor/lobos.ts:42-43
const REGRAS_LOBOS = ["sono_exaustao", "sono_continuar", "sono_noite", "pedido_necessidade", "abandono", "fome_moderada", "tempo_livre"]; // motor/lobos.ts:38-39
const ACOES_LOBOS = ["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"]; // motor/lobos.ts:34

/* ---------------------------------------------------------------- os textos de hoje */
const TXT_ENTRADA = { vies: "viés", fome: "comida", higiene: "higiene", energia: "energia", humor: "humor", saude: "saúde", sujeira: "sujeira",
  dormindo: "dormindo", hora: "hora", ticks_sem_cuidado: "sem cuidado", tedio: "tédio", curiosidade: "curiosidade", solidao: "solidão",
  estresse: "estresse", dor: "dor", susto: "susto", vontade: "vontade", conforto: "conforto" };                       // MapaPesos.tsx:9-13
const TXT_REGRA = { sono_exaustao: "exausto", sono_continuar: "sono", sono_noite: "noite", pedido_necessidade: "precisando", abandono: "sem cuidado",
  fome_moderada: "fome", tempo_livre: "tempo livre" };                                                                  // MapaPesos.tsx:14-17
const TXT_ACAO = { ocioso: "à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar" }; // MapaPesos.tsx:18-20
const REGRA_TXT = { sono_exaustao: "Exausto", sono_continuar: "Ainda com sono", sono_noite: "De noite", pedido_necessidade: "Precisando de você",
  abandono: "Sem cuidado há muito tempo", fome_moderada: "Com fome", tempo_livre: "Tempo livre" };                     // DigiBrain.tsx:15-18
const ACAO_INF = { ocioso: "ficar à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar" }; // DigiBrain.tsx:20-22
const ACAO_CURTA = TXT_ACAO;                                                                                            // DigiBrain.tsx:24-26 (iguais)
const ENTRADA_TXT = { fome: "comida", higiene: "higiene", energia: "energia", humor: "humor", saude: "saúde", sujeira: "sujeira", dormindo: "dormindo",
  hora: "hora do dia", ticks_sem_cuidado: "tempo sem cuidado", tedio: "tédio", solidao: "solidão", estresse: "estresse", dor: "dor", susto: "susto" }; // DigiBrain.tsx:28-31
const LOBO_TXT = [["impulsos", "Impulsos"], ["decisao", "Aprendido"], ["corpo", "Corpo"], ["memoria_emocao", "Memória e emoção"], ["piso", "Piso"]]; // DigiBrain.tsx:33
const COM_SINAL = new Set(["decisao", "corpo"]);                                                                        // DigiBrain.tsx:34
const NOME_PET = { ocioso: "à toa", dormir: "dormindo", comer: "comendo", brincar: "brincando", chamar_atencao: "chamando você", explorar: "explorando", emburrar: "emburrado" }; // motor/nomes.ts:18
const EMOCAO_NOME = { raiva: "raiva", tristeza: "tristeza", incomodo: "incômodo", ferido: "ferido", desdem: "desdém", vergonha: "vergonha", euforia: "euforia",
  indiferenca: "indiferença", orgulho: "orgulho", ternura: "ternura", timidez: "timidez", alegria: "alegria" };          // EMOCAO_TXT[nome][0], motor/expressao.ts:16-21
const TPD = 1440;                                                                                                       // motor/constantes.ts:11
const hhmm = t => { const m = t % TPD; return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); }; // TelaPet.tsx:51
const pct = (v, casas, sinal) => (sinal && v > 0 ? "+" : "") +
  (v * 100).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }).replace("-", "−") + "%"; // DigiBrain.tsx:36-37
const num = v => (v > 0 ? "+" : "") + v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).replace("-", "−"); // DigiBrain.tsx:38

/* ---------------------------------------------------------------- falhar alto */
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
function falhar(msg) {
  if (!document.querySelector(".erro-prancha")) document.body.insertAdjacentHTML("beforeend", `<p class="erro-prancha">${esc(msg)}</p>`);
  throw new Error(msg);
}
function txt(tabela, k, onde) { const v = tabela[k]; if (v === undefined) falhar(`${onde}: "${k}" sem texto`); return v; }

/* ---------------------------------------------------------------- os parametros */
const q = new URLSearchParams(location.search);
function opcao(nome, validos, padrao) {
  const v = q.get(nome) ?? padrao;
  if (!validos.includes(v)) falhar(`?${nome}=${v} desconhecido (${validos.join(", ")})`);
  return v;
}
if (window.__erroPele) falhar(window.__erroPele);
const ESTADO = opcao("estado", ["com_escolha", "uma_opcao", "sem_decisao", "replay", "mudou", "com_aprendido", "save_e2e"], "com_escolha");
const LARGURA = opcao("largura", ["1920", "390"], "1920");
if (ESTADO === "replay" && q.has("selo")) falhar("o replay tem sempre o selo replay; tire o ?selo");
const SELO = ESTADO === "replay" ? "replay" : opcao("selo", ["vivo", "pausado"], "vivo");
const NOTAS = q.has("notas"), TEXTO = q.has("texto"), ROLAR = q.has("rolar");
const REDUZIR = q.has("reduzir") || matchMedia("(prefers-reduced-motion: reduce)").matches;
const CHAVE = ESTADO === "replay" ? "com_escolha" : ESTADO;   // o replay e o com_escolha com o selo "replay" (seloDigiBrain.ts)
const MOVEL = LARGURA === "390";

const ic = nome => `<i data-lucide="${nome}" aria-hidden="true"></i>`;
const nota = (t, cls = "") => `<span class="nota ${cls}">${t}</span>`;
const f = v => Math.round(v * 10) / 10;

/* ---------------------------------------------------------------- a geometria do desenho (unidades do viewBox 1000 x 620; so desenho)
   A frente do cerebro fica a esquerda. Percepcao atras (um arco, as entradas na ordem do motor e os receptores do corpo no fim, embaixo),
   impulsos no meio (as regras de cima para baixo, na ordem em que o instinto as testa), decisao na frente (as acoes na ordem de ACOES_LOBOS).
   Memoria e emocao e a regiao de baixo, sem nenhum ponto: o lobo nao tem pesos. */
const VB = "0 0 1000 620";
function posicoes(receptores) {
  const ent = [...ENTRADAS_LOBOS, ...receptores], n = ent.length;
  const pe = new Map(ent.map((e, i) => { const a = (-75 + 150 * i / (n - 1)) * Math.PI / 180; return [e, [650 + 200 * Math.cos(a), 280 + 190 * Math.sin(a)]]; }));
  const pr = new Map(REGRAS_LOBOS.map((r, i) => [r, [480 + 26 * Math.sin(Math.PI * i / 6), 128 + 44 * i]]));
  const pa = new Map(ACOES_LOBOS.map((a, i) => [a, [285 - 85 * Math.sin(Math.PI * i / 6), 150 + 42 * i]]));
  return { ent, pe, pr, pa };
}
const SILHUETA = "M120 330C100 210 220 80 420 62C600 45 820 90 890 220C935 300 900 390 820 420C760 440 700 430 650 445C600 470 540 500 470 488C380 475 330 430 250 430C170 430 130 390 120 330Z";
const CEREBELO = "M650 445C655 505 760 535 825 505C865 485 860 440 820 420C760 440 700 430 650 445Z";
const DIVISAS = ["M380 66C360 180 372 300 345 410", "M612 54C592 170 602 300 592 420", "M300 432C360 392 540 388 640 446"];
/* as regioes: o lobo (o mesmo id de lobo_decisivo e do data-lobo de hoje), o rotulo e onde ele fica */
const REGIOES = [["decisao", "decisão", 250, 34], ["impulsos", "impulsos", 490, 30], ["percepcao", "percepção", 760, 40], ["memoria_emocao", "memória e emoção · sem pesos", 460, 526]];

function svgMapa(mapa, d, varredura) {
  const { ent, pe, pr, pa } = posicoes(mapa.receptores);
  for (const a of mapa.arestas) {
    if (!pe.has(a.entrada)) falhar(`entrada fora do mapa: ${a.entrada}`);
    if (!pr.has(a.regra)) falhar(`regra fora do mapa: ${a.regra}`);
    if (!pa.has(a.acao)) falhar(`ação fora do mapa: ${a.acao}`);
  }
  const ac = mapa.acesas;
  const curva = (e, r, a) => {
    const [x1, y1] = pe.get(e), [x2, y2] = pr.get(r), [x3, y3] = pa.get(a);
    return `M${f(x1)} ${f(y1)}C${f(x1 - 110)} ${f(y1)} ${f(x2 + 90)} ${f(y2)} ${f(x2)} ${f(y2)}C${f(x2 - 90)} ${f(y2)} ${f(x3 + 90)} ${f(y3)} ${f(x3)} ${f(y3)}`;
  };
  const top = new Set(d ? d.percepcao.map(p => p.entrada) : []);
  const chance = new Map(d ? d.chances.map(c => [c.acao, c.chance]) : []);
  const dest = ac ? ac.lobo_decisivo : null;
  /* a espessura de hoje (MapaPesos.tsx:62, :68) vezes a escala do desenho; os raios idem */
  const K = MOVEL ? 2.6 : 1.1, R = MOVEL ? 2 : 1;
  const rotulo = ac && d
    ? `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Nesta decisão: regra ${TXT_REGRA[ac.regra]}, escolheu ${TXT_ACAO[ac.acao]} com ${Math.round(chance.get(ac.acao) * 100)}% de chance.`
    : `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Ainda sem decisão.`;            // o rotulo de hoje, MapaPesos.tsx:43-45

  const regioes = REGIOES.map(([lobo, nome, x, y]) =>
    `<g class="mp-reg mp-reg--${lobo}${dest === lobo ? " mp-dest" : ""}" data-lobo="${lobo}"><text x="${x}" y="${y}" text-anchor="middle">${nome}` +
    `${dest === lobo ? '<tspan class="mp-mais-peso"> · pesou mais</tspan>' : ""}</text></g>`).join("") +
    (mapa.receptores.length ? '<text class="mp-sub" x="757" y="566" text-anchor="middle">receptores do corpo</text>' : "");

  const pesos = mapa.arestas.map(a => {
    const cls = a.aprendido > 0 ? "mp-mais" : a.aprendido < 0 ? "mp-menos" : "mp-prior";
    const op = a.aprendido === 0 ? "" : ` stroke-opacity="${f(0.35 + 0.65 * Math.sqrt(Math.abs(a.aprendido)))}"`;
    const tr = a.w < 0 ? ` stroke-dasharray="${f(6 * K)} ${f(4 * K)}"` : "";
    return `<path class="${cls}" d="${curva(a.entrada, a.regra, a.acao)}" stroke-width="${f(K * (0.4 + a.espessura * 1.4))}"${op}${tr}/>`;
  }).join("");
  const acesas = ac ? `<g class="mp-acesas">${ac.arestas.map(x => {
    if (!pe.has(x.entrada)) falhar(`aresta acesa fora do mapa: ${x.entrada}`);
    return `<path${x.termo < 0 ? ' class="mp-neg"' : ""} d="${curva(x.entrada, ac.regra, ac.acao)}" stroke-width="${f(K * (0.6 + 3 * x.forca))}" stroke-opacity="${f(0.35 + 0.65 * x.forca)}"${x.termo < 0 ? ` stroke-dasharray="${f(6 * K)} ${f(4 * K)}"` : ""}/>`;
  }).join("")}</g>` : "";
  /* o pulso, parado num quadro: um ponto em cada aresta acesa, no mesmo ponto do caminho (so com a varredura) */
  const pulso = ac && varredura ? `<g class="mp-pulso" aria-hidden="true">${ac.arestas.map(x =>
    `<path pathLength="1" d="${curva(x.entrada, ac.regra, ac.acao)}" stroke-width="${f(7 * R)}"/>`).join("")}</g>` : "";

  const nos = [];
  ent.forEach((e, i) => {
    const [x, y] = pe.get(e), lit = top.has(e), corpo = i >= ENTRADAS_LOBOS.length;
    nos.push(`<g class="mp-no${corpo ? " mp-corpo" : ""}${lit ? " mp-lit" : ""}" data-entrada="${e}"><circle cx="${f(x)}" cy="${f(y)}" r="${f(R * (lit ? 7 : 5))}"/>` +
      `<text x="${f(x + 12 * R)}" y="${f(y + 5 * R)}">${txt(TXT_ENTRADA, e, "entrada")}</text></g>`);
  });
  REGRAS_LOBOS.forEach(r => {
    const [x, y] = pr.get(r), lit = ac !== null && r === ac.regra;
    nos.push(`<g class="mp-no${lit ? " mp-lit" : ""}" data-regra="${r}"><circle cx="${f(x)}" cy="${f(y)}" r="${f(R * (lit ? 9 : 6.5))}"/>` +
      `<text x="${f(x)}" y="${f(y - 14 * R)}" text-anchor="middle">${TXT_REGRA[r]}</text></g>`);
  });
  ACOES_LOBOS.forEach(a => {
    const [x, y] = pa.get(a), c = chance.get(a), escolhida = ac !== null && a === ac.acao;
    const p = c === undefined ? "" : MOVEL ? `<tspan class="mp-pct"> ${Math.round(c * 100)}%</tspan>`
      : `</text><text class="mp-pct" x="${f(x - 14)}" y="${f(y + 22)}" text-anchor="end">${Math.round(c * 100)}%`;
    nos.push(`<g class="mp-no${c !== undefined ? " mp-cand" : ""}${escolhida ? " mp-esc" : ""}" data-acao="${a}">` +
      `<circle cx="${f(x)}" cy="${f(y)}" r="${f(R * (escolhida ? 10 : c !== undefined ? 8 : 6.5))}"/>` +
      /* a 390 o rotulo vai para dentro (a direita do ponto), senao sai da moldura */
      `<text x="${f(MOVEL ? x + 14 * R : x - 14)}" y="${f(y + 5 * R)}" text-anchor="${MOVEL ? "start" : "end"}">${TXT_ACAO[a]}${p}</text></g>`);
  });

  return `<svg class="mp" viewBox="${VB}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${esc(rotulo)}" data-n="${ac ? ac.n : ""}">
<defs><pattern id="db-malha" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><path class="mp-malha" d="M0 0H16M0 0V16"/></pattern></defs>
<g class="mp-desenho" aria-hidden="true"><path class="mp-silhueta" d="${SILHUETA}"/><path class="mp-silhueta" d="${CEREBELO}"/>
<g class="mp-divisas">${DIVISAS.map(p => `<path d="${p}"/>`).join("")}</g></g>
${regioes}
<g class="mp-pesos${ac ? " mp-pesos--fundo" : ""}">${pesos}</g>${acesas}${pulso}
<g class="mp-nos">${nos.join("")}</g></svg>`;
}

/* ---------------------------------------------------------------- o mapa em texto: o mesmo mapa, em lista e tabela */
function mapaTexto(mapa, d) {
  const ac = mapa.acesas;
  const cab = d && ac
    ? `<p>Nesta decisão: a regra <b>${REGRA_TXT[d.regra]}</b> e a ação <b>${ACAO_CURTA[d.acao]}</b>. Os pesos acesos, do mais forte para o mais fraco:</p>
<ol class="db-texto-acesas">${[...ac.arestas].sort((p, r) => r.forca - p.forca).map(x =>
      `<li>${txt(TXT_ENTRADA, x.entrada, "entrada")} · ${x.termo < 0 ? "contra" : "a favor"} · força <em>${pct(x.forca, 0, false)}</em></li>`).join("")}</ol>`
    : "<p>Ainda sem decisão: nada aceso.</p>";
  const linhas = mapa.arestas.map(a => {
    const marca = (a.aprendido > 0 ? "aprendeu a mais" : a.aprendido < 0 ? "aprendeu a menos" : "instinto") + (a.w < 0 ? " · negativo" : "");
    return `<tr><td>${TXT_REGRA[a.regra]}</td><td>${TXT_ACAO[a.acao]}</td><td>${txt(TXT_ENTRADA, a.entrada, "entrada")}</td><td>${a.w}</td><td>${a.w0}</td><td>${marca}</td></tr>`;
  }).join("");
  return `${cab}<table><caption>Os ${mapa.arestas.length} pesos, por regra (inteiros do motor)</caption>
<thead><tr><th scope="col">regra</th><th scope="col">ação</th><th scope="col">entrada</th><th scope="col">peso</th><th scope="col">no instinto</th><th scope="col">marca</th></tr></thead>
<tbody>${linhas}</tbody></table>`;
}

/* ---------------------------------------------------------------- a tela */
function desenhar(dados) {
  const est = dados.estados && dados.estados[CHAVE];
  if (!est) falhar(`o dados.json não tem o estado ${CHAVE}`);
  const db = est.db;
  if (!db) falhar("db nulo: o pet do estado não é v11");
  const d = db.decisao, mapa = db.mapa, ac = mapa.acesas;
  if ((d === null) !== (ac === null)) falhar("a decisão e as arestas acesas fora de par");
  if (ac && (ac.n !== d.n || ac.acao !== d.acao || ac.regra !== d.regra)) falhar("o mapa e a leitura de decisões diferentes");   // MapaPesos.tsx:39
  const varredura = d !== null && SELO === "vivo" && !REDUZIR;
  const mudou = d !== null && d.quem_decidiu.mudou;
  const nPontos = ENTRADAS_LOBOS.length + mapa.receptores.length + REGRAS_LOBOS.length + ACOES_LOBOS.length;

  const selo = `<span class="db-selo db-selo--${SELO}"><i aria-hidden="true"></i>${SELO === "vivo" ? "ao vivo" : SELO}</span>`;
  const topo = `<header class="scan-topo">
<h2 class="scan-tit" id="db-titulo">DigiBrain <small>mapa dos pesos</small></h2>${selo}
<button type="button" class="hx-btn fechar" aria-label="Fechar DigiBrain">${ic("x")}<kbd aria-hidden="true">Esc</kbd></button>
${nota(`selo: estadoSelo (src/seloDigiBrain.ts), do app e não do dados.json; a prancha usa ?selo=vivo|pausado, e o replay força "replay". Fonte dos dados: ${esc(dados.fonte)}; estado ${CHAVE}, log de ${est.log.length} eventos`, "n-topo")}
</header>`;

  const agora = `<section class="cx ladrilho db-agora sec-agora${mudou ? " db-agora--aprendido" : ""}" aria-labelledby="db-agora">
<h3 class="db-sec" id="db-agora">Agora</h3>${mudou ? '<span class="tag-aprendido">aprendido</span>' : ""}
${d ? `<b>${txt(REGRA_TXT, d.regra, "regra")}: decidiu ${txt(ACAO_INF, d.acao, "ação")}</b><small>${!d.quem_decidiu.escolha ? "Nesta situação só havia uma opção."
    : d.quem_decidiu.mudou ? `Sem o aprendido, teria decidido ${txt(ACAO_INF, d.quem_decidiu.acao_instinto, "ação")}.` : "O instinto sozinho faria o mesmo."}</small>`
    : "<small>Ainda não decidiu nada.</small>"}
${nota("decisao.regra, .acao e .quem_decidiu (escolha, mudou, acao_instinto): leituraDecisao, motor/digibrain.ts:14-35; os textos de DigiBrain.tsx:79-82")}
</section>`;

  const lobos = d ? `<section class="cx ladrilho sec-lobos" aria-labelledby="db-lobos">
<h3 class="db-sec" id="db-lobos">O peso de cada lobo nesta escolha</h3>
<ul class="db-barras">${LOBO_TXT.filter(([l]) => l !== "piso" || d.barras.piso !== 0).map(([l, nome]) => {
    const v = d.barras[l];
    if (typeof v !== "number") falhar(`barras.${l} ausente`);
    return `<li data-lobo="${l}"><span>${nome}</span><span class="db-trilho db-trilho--sinal"><b class="${v < 0 ? "neg" : ""}" style="width:${Math.min(50, Math.abs(v) * 50)}%"></b></span>` +
      `<em>${pct(v, l === "impulsos" ? 0 : 1, COM_SINAL.has(l))}</em></li>`;
  }).join("")}</ul>
<span class="db-emo">${est.emocao ? `emoção de hoje: ${txt(EMOCAO_NOME, est.emocao, "emoção")} · da memória do pet` : "nenhuma emoção na memória do pet ainda"}</span>
${nota("decisao.barras (digibrain.ts:17): o eixo no zero, o cheio de um lado é 100%; o piso só quando não é 0. A emoção: a última de pol.mem.emocoes (DigiBrain.tsx:65), EMOCAO_TXT (motor/expressao.ts:16)")}
</section>` : "";

  const perc = d ? `<section class="cx ladrilho sec-perc" aria-labelledby="db-perc">
<h3 class="db-sec" id="db-perc">O que mais pesou</h3>
${d.percepcao.length ? `<ul class="db-chips">${d.percepcao.map(p => `<li>${ENTRADA_TXT[p.entrada] ?? p.entrada} ${p.entrada === "dormindo" ? (p.x ? "sim" : "não") : pct(p.x, 0, false)} ` +
    `<span class="${p.termo > 0 ? "db-favor" : "db-contra"}">${p.termo > 0 ? "a favor" : "contra"}</span></li>`).join("")}</ul>`
    : '<p class="db-vazio">Nada do que ele lê pesou nesta regra.</p>'}
${nota("decisao.percepcao: a entrada, o x e o sinal do termo, as 3 de maior |w·x| sem o viés (digibrain.ts:23; N_PERCEPCAO, :9)")}
</section>` : "";

  const opc = d ? `<section class="cx ladrilho sec-opc" aria-labelledby="db-opc">
<h3 class="db-sec" id="db-opc">As opções e a chance de cada uma</h3>
<ul class="db-opcoes">${d.chances.map(c => `<li class="${c.acao === d.acao ? "esc" : ""}"><span>${txt(ACAO_CURTA, c.acao, "ação")}${c.acao === d.acao ? "<small> · escolhida</small>" : ""}</span>` +
    `<span class="db-trilho"><b style="width:${c.chance * 100}%"></b></span><em>${pct(c.chance, 0, false)}</em></li>`).join("")}</ul>
${nota("decisao.chances, na ordem do sorteio: o peso efetivo / a soma (digibrain.ts:19); a escolhida é decisao.acao")}
</section>` : "";

  const apr = `<section class="cx ladrilho sec-apr" aria-labelledby="db-apr">
<h3 class="db-sec" id="db-apr">O que aprendeu desde que nasceu</h3>
${db.aprendido.length ? `<ul class="db-aprendeu">${db.aprendido.map(a => `<li><span>${a.desvio > 0 ? "mais" : "menos"} ${txt(ACAO_CURTA, a.acao, "ação")} do que o instinto</span><em>${num(a.desvio)}</em></li>`).join("")}</ul>`
    : '<p class="db-vazio">Ainda igual ao instinto.</p>'}
${nota("Motor.digibrain().aprendido: leituraAprendido(desvioAprendido(observacaoAgora())), motor/motor.ts:329 e digibrain.ts:87; a marca do aprendido (guia 3)")}
</section>`;

  const ult = `<section class="cx ladrilho sec-ult" aria-labelledby="db-ult">
<h3 class="db-sec" id="db-ult">Últimas ações</h3>
${est.ultimas.length ? `<ol class="db-ultimas">${est.ultimas.map(h => `<li><span class="hora">${hhmm(h.t)}</span>${txt(NOME_PET, h.a, "ação do histórico")}</li>`).join("")}</ol>`
    : '<p class="db-vazio">Nenhuma ação ainda.</p>'}
${nota("m.historico, quem = pet, as 5 últimas (DigiBrain.tsx:74); a hora é hhmm(t), TelaPet.tsx:51")}
</section>`;

  const legenda = `<ul class="mp-leg">
<li><i class="leg leg-prior"></i>instinto</li><li><i class="leg leg-mais"></i>aprendeu a mais</li><li><i class="leg leg-menos"></i>aprendeu a menos</li>
<li><i class="leg leg-aceso"></i>esta decisão</li><li><i class="leg leg-neg"></i>peso negativo</li>${mapa.receptores.length ? '<li><i class="leg leg-corpo"></i>receptor do corpo</li>' : ""}</ul>`;
  const centro = `<section class="centro" aria-labelledby="db-mapa">
<div class="moldura">
<h3 class="moldura-tit" id="db-mapa">Mapa dos pesos <small>${nPontos} pontos · ${mapa.arestas.length} pesos</small></h3>
<div class="mapa-caixa">${svgMapa(mapa, d, varredura)}</div>
${varredura ? '<div class="varredura" aria-hidden="true"></div>' : ""}
${nota("pontos: ENTRADAS_LOBOS + mapa.receptores, REGRAS_LOBOS e ACOES_LOBOS (motor/lobos.ts:34-43), na ordem do motor; contagem: os três + mapa.arestas.length", "n-tl")}
${nota("fios: mapa.arestas (mapaPesos, digibrain.ts:107-140), entrada → regra → ação (CN-2); espessura = aresta.espessura (√|w|/S); cor = o sinal de aresta.aprendido; tracejado = w < 0", "n-tr")}
${nota(ac ? `acesas: mapa.acesas.arestas (mapaDecisao, digibrain.ts:101), espessura = forca; a regra, as candidatas (decisao.chances) e as 3 de decisao.percepcao acesas; "pesou mais" = mapa.acesas.lobo_decisivo (${ac.lobo_decisivo})` : "sem decisão: mapa.acesas = null, nada aceso", "n-bl")}
${nota(varredura ? "parado num quadro: a varredura e o pulso só passam numa decisão nova (mapa.acesas.n muda); o giro lento da câmera não aparece. As posições e a silhueta são só desenho" : "sem varredura nem pulso: " + (d === null ? "sem decisão" : SELO === "replay" ? "no replay (decidido)" : SELO === "pausado" ? "pausado, nenhuma decisão nova" : "reduzir movimento") + ". As posições e a silhueta são só desenho", "n-br")}
</div>
<div class="rodape-mapa">${legenda}
<p class="mp-nota">Cada ponto é uma entrada, uma regra ou uma ação do pet; cada fio é um peso, da entrada à ação, passando pela regra. A espessura é o tamanho do peso. A forma de cérebro e as regiões são só o desenho.</p>
<button type="button" class="hx-btn db-texto-bt" aria-expanded="${TEXTO}" aria-controls="db-texto">${ic("list")}O mapa em texto</button></div>
<section class="cx db-texto" id="db-texto" aria-labelledby="db-texto-tit"${TEXTO ? "" : " hidden"}><h3 class="db-sec" id="db-texto-tit">O mapa em texto</h3>${mapaTexto(mapa, d)}</section>
</section>`;

  const tela = document.getElementById("tela");
  tela.className = "tela " + (MOVEL ? "tela--390" : "tela--1920") + (NOTAS ? " notas" : "");
  tela.innerHTML = `${MOVEL ? "" : `<div class="ilha" aria-hidden="true"${FUNDO_ILHA ? ` style="background-image:url('${FUNDO_ILHA}')"` : ""}><span>a ilha 3D continua por baixo do modo scan</span></div>`}
<div class="scan digibrain" id="pet-painel" role="dialog" aria-modal="true" aria-labelledby="db-titulo">${topo}
<div class="corpo"><div class="col col-esq">${agora}${lobos}${perc}</div>${centro}<div class="col col-dir">${opc}${apr}${ult}</div></div></div>`;

  if (!window.lucide) falhar("os ícones (lucide) não carregaram");
  lucide.createIcons();
  const bt = tela.querySelector(".db-texto-bt"), painel = tela.querySelector("#db-texto");
  bt.addEventListener("click", () => { const abrir = painel.hidden; painel.hidden = !abrir; bt.setAttribute("aria-expanded", String(abrir)); });
  /* fechar (o botao e o Esc): na prancha so mostra a ilha por baixo */
  const fechar = () => tela.classList.add("fechado");
  tela.querySelector(".fechar").addEventListener("click", fechar);
  addEventListener("keydown", e => { if (e.key === "Escape") fechar(); });
  /* a caixa do "pesou mais", medida depois das fontes */
  document.fonts.ready.then(() => {
    for (const t of tela.querySelectorAll(".mp-dest text")) {
      const b = t.getBBox(), r = document.createElementNS("http://www.w3.org/2000/svg", "rect"), m = MOVEL ? 10 : 6;
      r.setAttribute("class", "mp-dest-caixa");
      for (const [k, v] of [["x", b.x - m], ["y", b.y - m / 2], ["width", b.width + 2 * m], ["height", b.height + m]]) r.setAttribute(k, String(f(v)));
      t.before(r);
    }
    if (ROLAR && MOVEL) { const c = tela.querySelector(".corpo"); c.scrollTop = c.scrollHeight; }
    else if (TEXTO && MOVEL) painel.scrollIntoView({ block: "start" });   /* a 390, o mapa em texto aberto fica no alto da folha */
  });
}

fetch(DADOS)
  .then(r => { if (!r.ok) falhar(`dados.json: HTTP ${r.status} em ${DADOS}`); return r.json(); })
  .then(desenhar)
  .catch(e => falhar("a prancha não desenhou: " + e.message));
