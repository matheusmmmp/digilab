/* Prancha D1b: o DigiBrain como modal pequeno, so o mapa dos pesos. So desenho; nenhum codigo do jogo e nenhum numero copiado a mao:
   tudo o que aparece sai do dados.json (Motor.reproduzir(4242, log, 13).digibrain(), gravado por dados_digibrain.mts) ou da estrutura do
   cerebro A (os nomes das entradas, regras e acoes, na ordem do motor). A geometria do desenho e a da prancha do scan (digibrain.js),
   com o viewBox recortado na silhueta. Os textos dos nos sao os do MapaPesos.tsx de hoje. */
"use strict";

const DADOS = "dados.json";
/* o fundo: a Tela Pet do mesmo pet v11, sem painel, capturada do jogo (fora do git, e2e_capturas/_fundo_modal.spec.ts temporario) */
const FUNDO = (pele, largura) => `/capturas_ux_digibrain_aprovar/modal/fundo/pet_${pele === "xcom" ? "militar" : "vidro"}_${largura}.png`;

/* ---------------------------------------------------------------- a estrutura do cerebro A (so os nomes, na ordem do motor) */
const ENTRADAS_LOBOS = ["vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "ticks_sem_cuidado"]; // motor/lobos.ts:42-43
const REGRAS_LOBOS = ["sono_exaustao", "sono_continuar", "sono_noite", "pedido_necessidade", "abandono", "fome_moderada", "tempo_livre"]; // motor/lobos.ts:38-39
const ACOES_LOBOS = ["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"]; // motor/lobos.ts:34
const TXT_ENTRADA = { vies: "viés", fome: "comida", higiene: "higiene", energia: "energia", humor: "humor", saude: "saúde", sujeira: "sujeira",
  dormindo: "dormindo", hora: "hora", ticks_sem_cuidado: "sem cuidado", tedio: "tédio", curiosidade: "curiosidade", solidao: "solidão",
  estresse: "estresse", dor: "dor", susto: "susto", vontade: "vontade", conforto: "conforto" };                       // MapaPesos.tsx:9-13
const TXT_REGRA = { sono_exaustao: "exausto", sono_continuar: "sono", sono_noite: "noite", pedido_necessidade: "precisando", abandono: "sem cuidado",
  fome_moderada: "fome", tempo_livre: "tempo livre" };                                                                  // MapaPesos.tsx:14-17
const TXT_ACAO = { ocioso: "à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar" }; // MapaPesos.tsx:18-20

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
const PELE = document.documentElement.dataset.pele;
const ESTADO = opcao("estado", ["com_escolha", "uma_opcao", "sem_decisao", "replay", "mudou", "com_aprendido", "save_e2e"], "com_escolha");
const LARGURA = opcao("largura", ["1920", "390"], "1920");
const LUGAR = opcao("lugar", ["direita", "centro"], "direita");
if (LARGURA === "390" && q.has("lugar")) falhar("o ?lugar e so da 1920");
if (ESTADO === "replay" && q.has("selo")) falhar("o replay tem sempre o selo replay; tire o ?selo");
const SELO = ESTADO === "replay" ? "replay" : opcao("selo", ["vivo", "pausado"], "vivo");
const DICA = q.has("dica"), TEXTO = q.has("texto"), SEM_FUNDO = q.get("fundo") === "0";
const REDUZIR = q.has("reduzir") || matchMedia("(prefers-reduced-motion: reduce)").matches;
const CHAVE = ESTADO === "replay" ? "com_escolha" : ESTADO;   // o replay e o com_escolha com o selo "replay" (seloDigiBrain.ts)
const MOVEL = LARGURA === "390";

const ic = nome => `<i data-lucide="${nome}" aria-hidden="true"></i>`;
const f = v => Math.round(v * 10) / 10;

/* ---------------------------------------------------------------- a geometria (a da prancha do scan; so desenho)
   O viewBox e recortado na silhueta (x 90 a 970, y 16 a 568), para o desenho encher o modal. */
const VB = "90 16 880 552";
function posicoes(receptores) {
  const ent = [...ENTRADAS_LOBOS, ...receptores], n = ent.length;
  const pe = new Map(ent.map((e, i) => { const a = (-75 + 150 * i / (n - 1)) * Math.PI / 180; return [e, [650 + 200 * Math.cos(a), 280 + 190 * Math.sin(a)]]; }));
  const pr = new Map(REGRAS_LOBOS.map((r, i) => [r, [480 + 26 * Math.sin(Math.PI * i / 6), 128 + 44 * i]]));
  const pa = new Map(ACOES_LOBOS.map((a, i) => [a, [285 - 85 * Math.sin(Math.PI * i / 6), 150 + 42 * i]]));
  return { ent, pe, pr, pa };
}
const SILHUETA = "M120 330C100 210 220 80 420 62C600 45 820 90 890 220C935 300 900 390 820 420C760 440 700 430 650 445C600 470 540 500 470 488C380 475 330 430 250 430C170 430 130 390 120 330Z";
const CEREBELO = "M650 445C655 505 760 535 825 505C865 485 860 440 820 420C760 440 700 430 650 445Z";
const DIVISAS = ["M380 66C360 180 372 300 345 410", "M612 54C592 170 602 300 592 420"];
/* tres rotulos de regiao, curtos (o "pesou mais" e a regiao sem pesos da memoria saem do modal) */
const REGIOES = [["acoes", "ações", 250, 36], ["regras", "regras", 490, 36], ["percepcao", "percepção", 760, 36]];

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
  const K = MOVEL ? 2.2 : 1.1, R = MOVEL ? 1.8 : 1;
  const rotulo = ac && d
    ? `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Nesta decisão: regra ${TXT_REGRA[ac.regra]}, escolheu ${TXT_ACAO[ac.acao]} com ${Math.round(chance.get(ac.acao) * 100)}% de chance.`
    : `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Ainda sem decisão.`;            // o rotulo de hoje, MapaPesos.tsx:43-45

  const regioes = REGIOES.map(([id, nome, x, y]) => `<text class="mp-reg-t" data-regiao="${id}" x="${x}" y="${y}" text-anchor="middle">${nome}</text>`).join("") +
    (mapa.receptores.length ? '<text class="mp-sub" x="757" y="556" text-anchor="middle">receptores do corpo</text>' : "");

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
      /* a 390 o rotulo da regra vai para baixo do ponto, senao bate no da acao ao lado */
      `<text x="${f(x)}" y="${f(MOVEL ? y + 34 * R : y - 14 * R)}" text-anchor="middle">${TXT_REGRA[r]}</text></g>`);
  });
  ACOES_LOBOS.forEach(a => {
    const [x, y] = pa.get(a), c = chance.get(a), escolhida = ac !== null && a === ac.acao;
    /* a 1920 o rotulo fica a esquerda do ponto e a chance embaixo dele (como no scan); a 390, a direita, na mesma linha */
    const p = c === undefined ? "" : MOVEL ? `<tspan class="mp-pct"> ${Math.round(c * 100)}%</tspan>`
      : `</text><text class="mp-pct" x="${f(x - 14)}" y="${f(y + 22)}" text-anchor="end">${Math.round(c * 100)}%`;
    nos.push(`<g class="mp-no${c !== undefined ? " mp-cand" : ""}${escolhida ? " mp-esc" : ""}" data-acao="${a}">` +
      `<circle cx="${f(x)}" cy="${f(y)}" r="${f(R * (escolhida ? 10 : c !== undefined ? 8 : 6.5))}"/>` +
      `<text x="${f(MOVEL ? x + 14 * R : x - 14)}" y="${f(y + 5 * R)}" text-anchor="${MOVEL ? "start" : "end"}">${TXT_ACAO[a]}${p}</text></g>`);
  });

  return `<svg class="mp" viewBox="${VB}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${esc(rotulo)}" data-n="${ac ? ac.n : ""}">
<defs><pattern id="db-malha" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><path class="mp-malha" d="M0 0H16M0 0V16"/></pattern></defs>
<g class="mp-desenho" aria-hidden="true"><path class="mp-silhueta" d="${SILHUETA}"/><path class="mp-silhueta" d="${CEREBELO}"/>
<g class="mp-divisas">${DIVISAS.map(p => `<path d="${p}"/>`).join("")}</g></g>
<g aria-hidden="true">${regioes}</g>
<g class="mp-pesos${ac ? " mp-pesos--fundo" : ""}">${pesos}</g>${acesas}${pulso}
<g class="mp-nos">${nos.join("")}</g></svg>`;
}

/* ---------------------------------------------------------------- o mapa em texto (o mesmo da prancha do scan, sem mudar) */
function mapaTexto(mapa, d) {
  const ac = mapa.acesas;
  const cab = d && ac
    ? `<p>Nesta decisão: a regra <b>${TXT_REGRA[d.regra]}</b> e a ação <b>${TXT_ACAO[d.acao]}</b>. Os pesos acesos, do mais forte para o mais fraco:</p>
<ol class="db-texto-acesas">${[...ac.arestas].sort((p, r) => r.forca - p.forca).map(x =>
      `<li>${txt(TXT_ENTRADA, x.entrada, "entrada")} · ${x.termo < 0 ? "contra" : "a favor"} · força <em>${Math.round(x.forca * 100)}%</em></li>`).join("")}</ol>`
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

  /* o selo vira so a forma (o ponto, as duas barras, o triangulo), com a dica e o nome acessivel */
  const SELO_TXT = { vivo: "ao vivo", pausado: "pausado", replay: "replay: uma decisão do passado" };
  const selo = `<span class="db-selo dm-selo db-selo--${SELO}" role="img" aria-label="${SELO_TXT[SELO]}" title="${SELO_TXT[SELO]}"><i aria-hidden="true"></i></span>`;
  /* a dica do "i": a forma e desenho, e a legenda curta que saiu do rodape */
  const dica = `<div class="dm-dica cx" id="dm-dica" role="tooltip"${DICA ? "" : " hidden"}>
<p>A forma de cérebro é só desenho. Cada ponto é o que o pet sente, uma regra ou uma ação; cada fio é um peso.</p>
<ul class="mp-leg"><li><i class="leg leg-aceso"></i>esta decisão</li><li><i class="leg leg-mais"></i>aprendeu a mais</li><li><i class="leg leg-menos"></i>aprendeu a menos</li>
<li><i class="leg leg-neg"></i>peso negativo</li>${mapa.receptores.length ? '<li><i class="leg leg-corpo"></i>receptor do corpo</li>' : ""}</ul></div>`;

  const modal = `<div class="dm cx${MOVEL ? " dm--folha" : " dm--" + LUGAR}" id="pet-painel" role="dialog" aria-modal="true" aria-labelledby="dm-tit">
${MOVEL ? '<span class="dm-alca" aria-hidden="true"></span>' : ""}
<header class="dm-topo">
<h2 class="dm-tit" id="dm-tit">DigiBrain</h2>${selo}
<button type="button" class="dm-ic dm-info" aria-label="O que é este desenho" aria-describedby="dm-dica" aria-expanded="${DICA}">${ic("info")}</button>
<button type="button" class="dm-ic dm-texto-bt" aria-label="O mapa em texto" aria-pressed="${TEXTO}">${ic("list")}</button>
<button type="button" class="dm-ic dm-fechar" aria-label="Fechar DigiBrain (Esc)">${ic("x")}</button>
</header>${dica}
<div class="dm-mapa">${TEXTO ? `<section class="db-texto dm-texto" aria-label="O mapa em texto">${mapaTexto(mapa, d)}</section>`
    : svgMapa(mapa, d, varredura) + (varredura ? '<div class="varredura dm-varredura" aria-hidden="true"></div>' : "")}</div>
</div>`;

  const tela = document.getElementById("tela");
  tela.className = "tela " + (MOVEL ? "tela--390" : "tela--1920");
  const fundo = SEM_FUNDO ? "" : ` style="background-image:url('${FUNDO(PELE, LARGURA)}')"`;
  tela.innerHTML = `<div class="ilha dm-ilha" aria-hidden="true"${fundo}></div><div class="dm-veu" aria-hidden="true"></div>${modal}`;

  if (!window.lucide) falhar("os ícones (lucide) não carregaram");
  lucide.createIcons();
  const fechar = () => tela.classList.add("fechado");
  tela.querySelector(".dm-fechar").addEventListener("click", fechar);
  tela.querySelector(".dm-veu").addEventListener("click", fechar);
  addEventListener("keydown", e => { if (e.key === "Escape") fechar(); });
  if (!SEM_FUNDO) {
    const img = new Image();
    img.onerror = () => falhar(`o fundo não carregou: ${FUNDO(PELE, LARGURA)} (rode e2e_capturas/_fundo_modal.spec.ts, ou ?fundo=0)`);
    img.src = FUNDO(PELE, LARGURA);
  }
}

fetch(DADOS)
  .then(r => { if (!r.ok) falhar(`dados.json: HTTP ${r.status} em ${DADOS}`); return r.json(); })
  .then(desenhar)
  .catch(e => falhar("a prancha não desenhou: " + e.message));
