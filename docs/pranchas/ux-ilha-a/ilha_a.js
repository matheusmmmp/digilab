/* Prancha ux-ilha-a ("Objetos que falam"), rodada 2: desenha cada estado por cima da captura real do jogo. So desenho; nenhum codigo do jogo.
   Rodada 2 (Matheus, 2026-11-07): sem fio nenhum; clicar no pet e carinho e segurar o pega e leva (a PEGAR_PET, ja no jogo); tocar na
   arvore a sacode e cai uma fruta (pede motor novo). Os numeros vem de dados.json (gerar_dados.py, dos quadros reais). Os deslocamentos
   abaixo (do ponto no chao ate o topo do objeto, o lugar do cartao, o tremor da arvore) sao de desenho: PROPOSTO, SEM FONTE.
   Falha alto: estado, pele ou largura desconhecidos, dado ou icone faltando. */
(async () => {
  const P = new URLSearchParams(location.search);
  const tela = document.getElementById("tela");
  const falhar = msg => { tela.className = "tela tela--1920"; tela.innerHTML = `<div class="erro">${msg}</div>`; throw new Error(msg); };
  if (window.__erroPele) falhar(window.__erroPele);
  const ESTADOS = ["nada_tocado", "etiqueta_aberta", "segurar_pet", "indo_tigela", "toque_arvore"];
  const estado = P.get("estado") ?? "nada_tocado", pele = document.documentElement.dataset.pele, larg = Number(P.get("largura") ?? 1920);
  if (!ESTADOS.includes(estado)) falhar("estado desconhecido: " + estado);
  if (larg !== 1920 && larg !== 390) falhar("largura desconhecida: " + larg + " (1920 ou 390)");
  const notas = P.has("notas");
  const resp = await fetch("dados.json");
  if (!resp.ok) falhar("dados.json nao carregou (" + resp.status + "): rode python gerar_dados.py e sirva por http");
  const D = (await resp.json()).estados[`${estado}|${pele}|${larg}`];
  if (!D) falhar(`dados.json sem ${estado}|${pele}|${larg}`);
  const G = larg === 1920;
  tela.className = `tela tela--${larg}`;
  tela.style.backgroundImage = `url("/capturas_ux_ilha_aprovar/prancha_a/fundo/${D.fundo}")`;

  /* o topo visivel de cada objeto, a partir do ponto no chao que o motor projeta (cenaPara) */
  const TOPO = G ? { tigela: -46, bola: -58 } : { tigela: -20, bola: -26 };
  const tigela = [D.tigela[0], D.tigela[1] + TOPO.tigela], bola = [D.bola[0], D.bola[1] + TOPO.bola];
  const centroTigela = [D.tigela[0], D.tigela[1] + (G ? -20 : -9)];

  const el = (html, cls, x, y) => {
    const d = document.createElement("div");
    d.className = cls; d.innerHTML = html; d.style.left = x + "px"; d.style.top = y + "px";
    tela.appendChild(d); return d;
  };
  const ic = n => `<span class="ic"><i data-lucide="${n}"></i></span>`;
  /* a etiqueta curta presa ao topo do objeto por uma ponta */
  const ponta = (x, y0, y1) => { const p = el("", "ponta", x, y0); p.style.height = (y1 - y0) + "px"; };
  const etiqueta = (html, x, yTopo, extra = "", alt = G ? 18 : 12) => { ponta(x, yTopo - alt, yTopo); return el(html, "caixa etq " + extra, x, yTopo - alt); };
  /* o selo nao sai da tela: se passa da borda, desliza para dentro (a ponta continua no lugar) */
  const selo = (html, x, y) => {
    const d = el(html, "caixa selo", x, y), w = d.offsetWidth;
    if (x - w / 2 < 6) d.style.left = (6 + w / 2) + "px";
    if (x + w / 2 > larg - 6) d.style.left = (larg - 6 - w / 2) + "px";
    return d;
  };
  const listaNotas = [];
  const nota = (x, y, texto, lacuna = false) => {
    listaNotas.push({ texto, lacuna });
    if (notas) el(String(listaNotas.length), "nota" + (lacuna ? " lacuna" : ""), x, y);
  };

  /* o cartao do toque: o canto que encosta no objeto fica em (x, y); lado = "dir" | "baixo" | "cima" */
  function cartao({ icone, nome, numero, unidade, linha, gesto, lado, x, y }) {
    const c = el(`<div class="cartao-topo">${ic(icone)}<span class="cartao-nome">${nome}</span>`
      + (numero !== undefined ? `<span class="cartao-num"><b>${numero}</b>${unidade ?? ""}</span>` : "")
      + `<span class="fechar"${numero === undefined ? ' style="margin-left:auto"' : ""}><i data-lucide="x"></i></span></div>`
      + (linha ? `<div class="cartao-linha ${linha.cls}">${ic(linha.icone)}<span>${linha.texto}</span></div>` : "")
      + (gesto ? `<div class="gesto">${ic(gesto.icone)}<span>${gesto.texto}</span></div>` : ""), "caixa cartao", 0, 0);
    const w = c.offsetWidth, h = c.offsetHeight;
    if (lado === "dir") { c.style.left = x + "px"; c.style.top = (y - h / 2) + "px"; }
    else if (lado === "baixo") { c.style.left = Math.min(Math.max(8, x - w / 2), larg - w - 8) + "px"; c.style.top = y + "px"; }
    else { c.style.left = Math.min(Math.max(8, x - w / 2), larg - w - 8) + "px"; c.style.top = (y - h) + "px"; }
    return c;
  }

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "fios"); tela.appendChild(svg);
  const sv = (tag, attrs) => { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const k in attrs) e.setAttribute(k, attrs[k]); svg.appendChild(e); return e; };
  function toque(x, y) {
    sv("circle", { cx: x, cy: y, r: G ? 26 : 16, class: "toque" });
    sv("circle", { cx: x, cy: y, r: G ? 40 : 24, class: "toque-2" });
  }

  /* os selos dos lugares: o progresso a vista (o saco: os treinos do dia no registro e se ja pode treinar; a barraca: o ponto de novo) */
  function selosDosLugares() {
    const m = D.mao;
    if (m.saco) {
      selo(`${ic("dumbbell")}<b>${D.treinos_hoje}</b><span>hoje</span><span class="ok"><i data-lucide="check"></i></span>`, m.saco[0], m.saco[1]);
      nota(m.saco[0] + (G ? 62 : 44), m.saco[1] - (G ? 30 : 26), `Saco: <b>${D.treinos_hoje}</b> treinos hoje = os eventos "tr" do registro no dia do jogo; o visto =
        TreinoPet.podeTocar(tick) (motor/treino.ts). <em>Sem a fadiga no selo (fica no Treinar). I1-7 DECIDIDA.</em>`);
    }
    if (m.barraca) {
      selo(`${ic("book-open")}<span class="ponto"></span>`, m.barraca[0], m.barraca[1]);
      nota(m.barraca[0] + (G ? 34 : 26), m.barraca[1] - (G ? 30 : 26), `Barraca: o ponto de "diário novo". O jogo não guarda o que o dono já leu: a marca da última
        abertura fica só na vista (localStorage), fora do save. I1-5 DECIDIDA.`);
    }
  }

  const aprComer = D.aprendido.comer;
  const linhaTigela = aprComer === undefined ? { cls: "sem", icone: "minus", texto: "Nada novo sobre comer" }
    : { cls: "aprendeu", icone: aprComer < 0 ? "trending-down" : "trending-up", texto: aprComer < 0 ? "Come menos" : "Come mais" };

  /* ---------------------------------------------------------------- os estados */
  if (estado === "nada_tocado") {
    selosDosLugares();
    nota(tigela[0], tigela[1] - (G ? 8 : 4), "Tigela, bola, ninho, árvores: sem etiqueta enquanto nada é tocado. A etiqueta aparece no hover (desktop), no toque, ou quando o objeto é o alvo atual. I1-4 DECIDIDA.");
  }

  if (estado === "etiqueta_aberta") {
    selosDosLugares();
    cartao({ icone: "soup", nome: "Tigela", numero: D.racao_madura, unidade: D.racao_madura === 1 ? "ração" : "rações", linha: linhaTigela,
      gesto: { icone: "soup", texto: "Servir ração" }, lado: G ? "dir" : "baixo",
      x: G ? D.tigela[0] + 78 : D.tigela[0], y: G ? centroTigela[1] : D.tigela[1] + 10 });
    if (G) { const p = el("", "ponta", 0, 0); p.style.cssText = `left:${D.tigela[0] + 52}px;top:${centroTigela[1] - 1}px;width:26px;height:2px;transform:none`; }
    else ponta(D.tigela[0], D.tigela[1] - 2, D.tigela[1] + 10);
    /* a bola, so com o hover (desktop): a etiqueta curta */
    if (G) etiqueta(`${ic("circle-dot")}<span>Bola</span>`, D.bola[0], bola[1]);
    const nx = G ? D.tigela[0] + 70 : D.tigela[0] - 92;
    nota(nx, G ? centroTigela[1] - 70 : D.tigela[1] + 30, `Tigela: <b>${D.racao_madura}</b> ração madura = Motor.mundo.comidas na tigela, com situacao(c, tick)
      (motor/mundo.ts). <em>Podre: ${D.racao_podre}.</em>`);
    nota(nx, G ? centroTigela[1] + 18 : D.tigela[1] + 92, `A linha do que aprendeu = Motor.digibrain().aprendido, o desvio aprendido da ação comer
      (fora das 3 maiores agora: "nada novo"). A vista liga a ação ao objeto (comer → tigela, brincar → bola). I1-8 DECIDIDA.`);
    nota(nx, G ? centroTigela[1] + 66 : D.tigela[1] + 132, `"Servir ração" = o mesmo Motor.observar("alimentar") do botão Alimentar (a ração no comedouro,
      um evento "dc"). A barra de baixo continua igual. I1-9 DECIDIDA.`);
    if (G) nota(D.bola[0] + 52, bola[1] - 34, "Bola: a etiqueta curta do hover (só desktop; no celular só o toque abre).");
  }

  if (estado === "segurar_pet") {
    /* o pet na mao e o desenho do jogo (PEGAR_PET P2): suspenso, balancando, com a sombra onde vai cair. A prancha so marca o dedo */
    selosDosLugares();
    if (!D.mao_ponteiro || !D.pet_na_mao) falhar("o quadro do segurar_pet nao tem o pet na mao (petNaMao) nem o ponto do dedo");
    const [mx, my] = D.mao_ponteiro, r = D.pet_ret;
    /* o icone de agarrar fica ao lado do sprite, na altura do dedo: nada por cima do pet */
    const dedo = el(`${ic("grab")}`, "caixa selo dedo", r.x + r.w + (G ? 10 : 6), my);
    dedo.style.transform = "translate(0, -50%)";
    nota(r.x + r.w + (G ? 64 : 44), my - (G ? 24 : 20), `Clicar no pet = carinho (um evento "d" acariciar, ToquePet.tsx). Segurar e arrastar = pegar o pet e soltar onde
      quiser no mapa (Motor.levarPet, o evento "lp"; PEGAR_PET P1 #673 e P2 #674, já no jogo). O desenho do pet na mão é o de hoje: a prancha não
      muda nada aqui. I1-1 DECIDIDA.`);
    nota(r.x - (G ? 20 : 10), r.y + r.h * 0.4, `Sem fio: o pet não mostra para onde ia. O que o cérebro escolheu fica no DigiBrain
      (o campo pequeno). I1-2 e I1-10 caíram junto com o fio.`);
  }

  if (estado === "indo_tigela") {
    selosDosLugares();
    /* o alvo atual ganha a etiqueta curta (sem fio e sem chance) */
    etiqueta(`${ic("soup")}<b>${D.racao_madura}</b><span>${D.racao_madura === 1 ? "ração" : "rações"}</span>`, D.tigela[0], tigela[1], "etq--alvo");
    nota(D.tigela[0] + (G ? 90 : 40), tigela[1] - (G ? 40 : 26), `O pet vai até a tigela (decisão comer, regra ${D.regra}): sem fio. A tigela, o alvo atual,
      mostra a etiqueta curta (<b>${D.racao_madura}</b> rações maduras). Saber que o alvo é a tigela: o tipo do alvo pendente da percepção
      (alvo_pendente = "comida") e a ração na tigela; no CMU_MVP a comida só vem do dono. <em>Outro momento real: a semente 6521 à noite.</em>`);
  }

  if (estado === "toque_arvore") {
    selosDosLugares();
    const t = D.mao.arvore, f = D.mao.fruta;
    toque(t[0], t[1]);
    /* o sacudir: tracos curtos dos dois lados da copa */
    const a = G ? 46 : 22, b = G ? 16 : 8;
    for (const s of [-1, 1]) for (const k of [0, 1]) {
      const x = t[0] + s * (a + k * (G ? 14 : 7)), y = t[1] - (G ? 14 : 7) + k * (G ? 22 : 11);
      sv("path", { d: `M${x},${y - b} q${s * (G ? 8 : 4)},${b} 0,${2 * b}`, class: "sacode" });
    }
    /* a queda: um tracejado curto da copa ate a fruta no chao, e a fruta (o modelo de hoje da vista, itens.ts, aqui so a silhueta) */
    sv("path", { d: `M${f[0]},${t[1] + (G ? 24 : 12)} L${f[0]},${f[1] - (G ? 18 : 9)}`, class: "queda" });
    sv("circle", { cx: f[0], cy: f[1], r: G ? 11 : 6, class: "fruta" });
    etiqueta(`${ic("cherry")}<span>Fruta</span>`, f[0], f[1] - (G ? 14 : 8));
    nota(t[0] + (G ? 60 : 34), t[1] - (G ? 30 : 22), `Tocar na árvore a sacode e cai uma fruta (I1-3, DECIDIDA). PEDE MOTOR NOVO: o jogo roda o mundo CMU_MVP, sem frutas
      no TS (motor/motor.ts); o Python tem as frutas (digilab/frutas.py, mundo.py), mas não o gesto de sacudir. É uma tarefa própria: Python,
      depois o TS com paridade, versão de pet nova e chave desligada (PERGUNTAS.md, I1-3).`, true);
    nota(f[0] + (G ? 60 : 36), f[1] + (G ? 6 : 4), `A fruta no chão seria a fruta de hoje da vista (ilha/itens.ts, as cores a, b e c); aqui só a silhueta. Quantas
      frutas a árvore tem, a recarga e qual fruta cai saem do motor novo.`, true);
  }

  /* a legenda das notas */
  if (notas) {
    document.body.classList.add("com-notas");
    const lg = el(`<h2>Fonte no motor · ${estado.replace(/_/g, " ")}</h2><ol>${listaNotas.map((n, i) =>
      `<li class="${n.lacuna ? "lacuna" : ""}"><span class="nota${n.lacuna ? " lacuna" : ""}">${i + 1}</span><span>${n.texto}</span></li>`).join("")}</ol>`, "caixa legenda", 0, 0);
    /* a legenda fica fora da tela do jogo, a direita, para nao cobrir o desenho */
    document.body.appendChild(lg);
    lg.style.left = (larg + 12) + "px"; lg.style.top = "12px";
  }

  lucide.createIcons();
  const faltando = document.querySelectorAll("i[data-lucide]");
  if (faltando.length) falhar("ícone que o lucide não tem: " + [...faltando].map(i => i.dataset.lucide).join(", "));
  document.body.dataset.pronto = "1";
})();
