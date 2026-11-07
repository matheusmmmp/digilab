/* Prancha ux-ilha-a ("Objetos que falam"): desenha cada estado por cima da captura real do jogo. So desenho; nenhum codigo do jogo.
   Os numeros vem de dados.json (gerar_dados.py, dos quadros reais). Os deslocamentos abaixo (do ponto no chao ate o topo do objeto, a curva
   do fio, o lugar do cartao) sao de desenho: PROPOSTO, SEM FONTE. Falha alto: estado, pele ou largura desconhecidos, dado ou icone faltando. */
(async () => {
  const P = new URLSearchParams(location.search);
  const tela = document.getElementById("tela");
  const falhar = msg => { tela.className = "tela tela--1920"; tela.innerHTML = `<div class="erro">${msg}</div>`; throw new Error(msg); };
  if (window.__erroPele) falhar(window.__erroPele);
  const ESTADOS = ["nada_tocado", "etiqueta_aberta", "fio_toque_pet", "indo_tigela", "toque_arvore"];
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
  const centroBola = [D.bola[0], D.bola[1] + (G ? -28 : -13)], centroTigela = [D.tigela[0], D.tigela[1] + (G ? -20 : -9)];
  const r = D.pet_ret, pe = [r.x + r.w / 2, r.y + r.h];
  const pct = c => Math.round(c * 100) + " %";
  const num = x => (x < 0 ? "−" : "+") + Math.abs(x).toFixed(2).replace(".", ",");
  const NOME_ACAO = { comer: "Comer", brincar: "Brincar", dormir: "Dormir", explorar: "Explorar", ocioso: "Descansar", chamar_atencao: "Chamar" };

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

  /* o fio da intencao, do pe do pet ao alvo, numa curva que contorna o sprite (o fio nunca passa por cima do pet) */
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "fios"); tela.appendChild(svg);
  const sv = (tag, attrs) => { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const k in attrs) e.setAttribute(k, attrs[k]); svg.appendChild(e); return e; };
  function fio(alvo, raioAlvo) {
    const s = [pe[0] + r.w * (G ? 0.42 : 0.5), pe[1] - (G ? 10 : 6)];
    const acima = alvo[1] < s[1] - 20 && Math.abs(alvo[0] - pe[0]) < r.w * 0.6;
    const c = acima ? [s[0] + (G ? 150 : 46), (s[1] + alvo[1]) / 2] : [(s[0] + alvo[0]) / 2, Math.min(s[1], alvo[1]) - (G ? 70 : 34)];
    /* o fim encosta no anel do alvo, do lado da curva */
    const dx = c[0] - alvo[0], dy = c[1] - alvo[1], n = Math.hypot(dx, dy);
    const e = [alvo[0] + dx / n * raioAlvo, alvo[1] + dy / n * raioAlvo];
    const d = `M${s[0]},${s[1]} Q${c[0]},${c[1]} ${e[0]},${e[1]}`;
    sv("path", { d, class: "fio-sombra" }); sv("path", { d, class: "fio" });
    sv("circle", { cx: alvo[0], cy: alvo[1], r: raioAlvo, class: "anel" });
    sv("circle", { cx: s[0], cy: s[1], r: G ? 4 : 3, class: "anel" });
    return { s, c, e };
  }
  /* o toque no pet: um anel no chao, aos pes (nada por cima do sprite) */
  function toqueNoChao() {
    sv("ellipse", { cx: pe[0], cy: pe[1] - (G ? 4 : 2), rx: G ? 78 : 30, ry: G ? 18 : 7, class: "toque" });
    sv("ellipse", { cx: pe[0], cy: pe[1] - (G ? 4 : 2), rx: G ? 104 : 40, ry: G ? 26 : 10, class: "toque-2" });
  }
  function toque(x, y) {
    sv("circle", { cx: x, cy: y, r: G ? 26 : 16, class: "toque" });
    sv("circle", { cx: x, cy: y, r: G ? 40 : 24, class: "toque-2" });
  }

  /* os selos dos lugares: o progresso a vista (o saco: os treinos do dia no registro e se ja pode treinar; a barraca: o ponto de novo) */
  function selosDosLugares() {
    const m = D.mao;
    if (m.saco) {
      selo(`${ic("dumbbell")}<b>${D.treinos_hoje}</b><span>hoje</span><span class="ok"><i data-lucide="check"></i></span>`, m.saco[0], m.saco[1]);
      nota(m.saco[0] + (G ? 62 : 44), m.saco[1] - (G ? 30 : 26), `Saco: <b>${D.treinos_hoje}</b> treinos hoje = os eventos "tr" do registro no dia do jogo; o visto = TreinoPet.podeTocar(tick)
        (motor/treino.ts). <em>Sem a fadiga no selo (fica no Treinar).</em>`);
    }
    if (m.barraca) {
      selo(`${ic("book-open")}<span class="ponto"></span>`, m.barraca[0], m.barraca[1]);
      nota(m.barraca[0] + (G ? 34 : 26), m.barraca[1] - (G ? 30 : 26), `Barraca: o ponto de "diário novo". LACUNA: o jogo não guarda o que o dono já leu (pergunta I1-5).`, true);
    }
  }

  const aprBola = D.aprendido.brincar, aprComer = D.aprendido.comer;
  const linhaBola = aprBola === undefined ? { cls: "sem", icone: "minus", texto: "Nada novo sobre brincar" }
    : { cls: "aprendeu", icone: aprBola < 0 ? "trending-down" : "trending-up", texto: aprBola < 0 ? "Brinca menos" : "Brinca mais" };
  const linhaTigela = aprComer === undefined ? { cls: "sem", icone: "minus", texto: "Nada novo sobre comer" }
    : { cls: "aprendeu", icone: aprComer < 0 ? "trending-down" : "trending-up", texto: aprComer < 0 ? "Come menos" : "Come mais" };
  const fonteApr = acao => `${acao === "brincar" ? "Bola" : "Tigela"}: a linha do que aprendeu = Motor.digibrain().aprendido ("menos" e "mais": comparado ao que nasceu, o desvio aprendido da ação
    ${acao}${D.aprendido[acao] === undefined ? ", fora das 3 maiores agora: \"nada novo\"" : ` = ${num(D.aprendido[acao])}`}). <em>A ação vira objeto pela vista
    (comer → tigela, brincar → bola). O paladar (gosto por fruta) ainda não existe no TS: LACUNA.</em>`;

  /* ---------------------------------------------------------------- os estados */
  if (estado === "nada_tocado") {
    selosDosLugares();
    nota(tigela[0], tigela[1] - (G ? 8 : 4), "Tigela, bola, ninho: sem etiqueta enquanto nada é tocado. A etiqueta aparece no hover (desktop), no toque, ou quando o objeto é o alvo atual.");
  }

  if (estado === "etiqueta_aberta") {
    selosDosLugares();
    const lado = G ? "dir" : "baixo";
    cartao({ icone: "soup", nome: "Tigela", numero: D.racao_madura, unidade: D.racao_madura === 1 ? "ração" : "rações", linha: linhaTigela,
      gesto: { icone: "soup", texto: "Servir ração" }, lado,
      x: G ? D.tigela[0] + 78 : D.tigela[0], y: G ? centroTigela[1] : D.tigela[1] + 10 });
    if (G) { const p = el("", "ponta", 0, 0); p.style.cssText = `left:${D.tigela[0] + 52}px;top:${centroTigela[1] - 1}px;width:26px;height:2px;transform:none`; }
    else ponta(D.tigela[0], D.tigela[1] - 2, D.tigela[1] + 10);
    /* a bola, so com o hover (desktop): a etiqueta curta */
    if (G) etiqueta(`${ic("circle-dot")}<span>Bola</span>`, D.bola[0], bola[1]);
    nota(G ? D.tigela[0] + 70 : D.tigela[0] - 92, G ? centroTigela[1] - 70 : D.tigela[1] + 30, `Tigela: <b>${D.racao_madura}</b> ração madura = Motor.mundo.comidas na tigela, com situacao(c, tick)
      (motor/mundo.ts). <em>Podre: ${D.racao_podre}.</em>`);
    nota(G ? D.tigela[0] + 70 : D.tigela[0] - 92, G ? centroTigela[1] + 66 : D.tigela[1] + 132, `"Servir ração" = o mesmo Motor.observar("alimentar") do botão Alimentar (a ração no comedouro,
      um evento "dc"). A barra de baixo continua igual.`);
    nota(G ? D.tigela[0] + 70 : D.tigela[0] - 92, G ? centroTigela[1] + 18 : D.tigela[1] + 92, fonteApr("comer"));
    if (G) nota(D.bola[0] + 52, bola[1] - 34, "Bola: a etiqueta curta do hover (só desktop; no celular só o toque abre).");
  }

  if (estado === "fio_toque_pet") {
    selosDosLugares();
    toqueNoChao();
    fio(centroBola, G ? 40 : 18);
    let chip, ap;
    if (G) {
      chip = etiqueta(`${ic("circle-dot")}<span>${NOME_ACAO[D.acao]}</span><b>${pct(D.chance)}</b>`, D.bola[0], centroBola[1] - 40, "chance");
      ap = el(`${ic(linhaBola.icone)}<span>${linhaBola.texto}</span>`, "caixa etq " + linhaBola.cls, D.bola[0], 0);
      ap.style.top = (parseFloat(chip.style.top) - 40) + "px";
    } else {
      /* no celular o balao do pet fica logo acima da bola: as etiquetas vao para a direita dela */
      const x0 = D.bola[0] + 26, y0 = centroBola[1];
      const p = el("", "ponta", 0, 0); p.style.cssText = `left:${D.bola[0] + 18}px;top:${y0 - 1}px;width:8px;height:2px;transform:none`;
      chip = el(`${ic("circle-dot")}<span>${NOME_ACAO[D.acao]}</span><b>${pct(D.chance)}</b>`, "caixa etq chance", x0, y0);
      chip.style.transform = "translate(0, -50%)";
      ap = el(`${ic(linhaBola.icone)}<span>${linhaBola.texto}</span>`, "caixa etq " + linhaBola.cls, x0, y0 + 18);
      ap.style.transform = "none";
    }
    nota(pe[0] - (G ? 104 : 46), pe[1] - (G ? 4 : 2), `Toque no pet: hoje já é o carinho (um evento "d" acariciar). O fio só é vista: não entra no registro (pergunta I1-1).`);
    nota(D.bola[0] + (G ? 110 : 66), centroBola[1] - (G ? 64 : 34), `Fio e chance: o alvo = o candidato que o mundo escolheu (Mundo.ultimosCandidatos e o alvo pendente);
      a chance = Motor.digibrain().decisao.chances da ação escolhida (<b>${NOME_ACAO[D.acao].toLowerCase()} ${pct(D.chance)}</b>, regra ${D.regra}).
      <em>O alvo pendente é privado no Mundo TS: pede um getter só de leitura (pergunta I1-2).</em>`);
    nota(G ? D.bola[0] + 150 : D.bola[0] + 20, G ? parseFloat(ap.style.top) - 4 : parseFloat(ap.style.top) + 14, fonteApr("brincar"));
  }

  if (estado === "indo_tigela") {
    selosDosLugares();
    fio(centroTigela, G ? 52 : 22);
    etiqueta(`${ic("soup")}<span>${NOME_ACAO[D.acao]}</span><b>${pct(D.chance)}</b>`, D.tigela[0], centroTigela[1] - (G ? 52 : 22), "chance");
    nota(D.tigela[0] + (G ? 110 : 50), centroTigela[1] - (G ? 90 : 50), `O pet vai até um objeto: o fio aparece sozinho enquanto a ação com alvo dura (ACOES_COM_ALVO: comer, explorar, brincar)
      e some ao chegar. Chance = decisao.chances (<b>${NOME_ACAO[D.acao].toLowerCase()} ${pct(D.chance)}</b>, regra ${D.regra}).`);
    nota(D.tigela[0] - (G ? 70 : 34), centroTigela[1] + (G ? 34 : 18), `O alvo atual ganha a etiqueta: aqui a chance no lugar do nome (<b>${D.racao_madura}</b> rações maduras na tigela, no toque).
      <em>Outro momento real: a semente 6521 à noite (de dia, nas sementes testadas, o pet não estava longe da tigela com fome).</em>`);
  }

  if (estado === "toque_arvore") {
    selosDosLugares();
    const t = D.mao.arvore;
    toque(t[0], t[1]);
    cartao({ icone: "tree-deciduous", nome: "Árvore", linha: { cls: "sem", icone: "minus", texto: "Sem frutas nesta ilha" }, lado: G ? "baixo" : "cima",
      x: t[0], y: G ? t[1] + 44 : t[1] - 30 });
    if (G) ponta(t[0], t[1] + 28, t[1] + 44); else ponta(t[0], t[1] - 30, t[1] - 18);
    nota(G ? t[0] + 170 : t[0] + 110, G ? t[1] + 70 : t[1] - 104, `Árvore: LACUNA. O jogo roda o mundo CMU_MVP, sem árvores (só a ração do jogador; motor/motor.ts). As frutas,
      a queda e a recarga só existem no Python (digilab/frutas.py, mundo.py) e não há gesto de sacudir em nenhum dos dois. O toque só diz o nome (pergunta I1-3).`, true);
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
