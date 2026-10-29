/* Simulacao da arena em tempo real, sem DOM (docs/TAREFA_V2_UP_ARENA.md, secao 10.4): porte do arena.html (sha256 f3be1160...91fbeb),
   na mesma ordem de contas e de sorteios, para a paridade com o prototipo (P1). Passo de tempo fixo (PASSO_MS); os sorteios vem de
   Sorteios (um fluxo por uso no jogo, sequencia unica so na medicao); a entrada do jogador e evento; a saida sao eventos com tipo.
   Nada daqui toca no motor do pet, no log nem no save. */
import { ACAO, DIFIC, ELIPSE, ENTRADA, EQ, PASSO_MS, PX_POR_UNIDADE, TROCA_ESPERA } from "./constantes.ts";
import { CENAS, iniciarCena } from "./cenas.ts";
import { GOLPE_GENERICO, duracaoTag, fatorRitmo, multAtr, statusDoJogo, tagDe } from "./dados.ts";
import { ativo, bloqueio, colidir, dentroArena, evento, mudar, obstaculoEm, outro, prender, ref, vivos } from "./nucleo.ts";
import type { ConfigLuta, DadosArena, Entrada, Evento, GolpeBase, Lado, Luta, Lutador, Sorteios, Stats } from "./tipos.ts";

export { ativo, outro, vivos } from "./nucleo.ts";

const def = (L: Luta) => CENAS[L.cena.id];
const dific = (L: Luta) => DIFIC[L.cfg.dific];
const mult = (L: Luta, a: Lutador | { atr: Lutador["atr"] }, b: { atr: Lutador["atr"] }) => multAtr(a.atr, b.atr, L.cfg.forca);

/** status de um membro: os genericos da tela e, com a fonte "jogo" e registro no jogo, vida, ataque, defesa, critico, esquiva e
    atordoamento da tabela do jogo no nivel */
export function statsDoMembro(cfg: ConfigLuta, dados: DadosArena, l: Lado, n: string): Stats {
  const c = cfg[l], gen = c.generico;
  const j = c.fonte === "jogo" ? statusDoJogo(dados, n, c.nivel, cfg.ritmo) : null;
  return j ? { ...gen, ...j, origem: "jogo" } : { ...gen, esquiva: 0, atordoa: 0, origem: "genérico" };
}

function criarLutador(L: Luta, n: string, lado: Lado, slot: number): Lutador {
  const A = L.dados.atlas.d[n];
  if (!A) throw new Error(`arena: ${n} nao esta no atlas`);
  const g = L.dados.golpes[n] || GOLPE_GENERICO, sk = g.skill || g, st = statsDoMembro(L.cfg, L.dados, lado, n);
  const tsk = tagDe(A, sk.anim), atk = tagDe(A, g.anim);
  /* a ordem dos sorteios e a do literal do prototipo: recSk, recarga, fase */
  const recSk = ACAO.recSkIni + L.r.ia() * ACAO.recSkVar, recarga = ACAO.recargaIni + L.r.ia() * ACAO.recargaVar, fase = L.r.ia() * 6.28;
  return {
    n, lado, slot, A, g, sk, propria: !!g.skill, usandoHab: false, st, atr: L.dados.atributos[n],
    x: 0, y: 0, hp: st.hp, viraEsq: lado === "b", estado: "idle", t: 0,
    recarga, recSk, golpeDado: false,
    msAtk: A.f.slice(atk[1], atk[2] + 1).reduce((s, f) => s + f[2], 0),
    msSk: A.f.slice(tsk[1], tsk[2] + 1).reduce((s, f) => s + f[2], 0),
    alcance: g.proj ? ACAO.alcanceDist : EQ.alcanceCorpo, raio: EQ.raio, alvo: null, fase,
    morto: false, dano: 0, golpes: 0, mira: null, dash: 0, dashCd: 0, dashDir: [0, 0], reacao: 0, desvioDir: [0, 0],
    entrada: 0, atordoado: 0, caiuEm: 0, foraAte: 0, escondido: false, naRuna: 0, buffAte: 0, bloq: 0, ladoDesvio: 0,
    acDano: 0, ultAmb: 0, ultNum: 0, decisao: "",
  };
}

function ligarAlvos(L: Luta): void { const a = ativo(L, "a"), b = ativo(L, "b"); a.alvo = b; b.alvo = a; }

/** uma luta nova: monta as equipes (a e depois b), poe os primeiros em campo e confere a colisao inicial */
export function criarLuta(cfg: ConfigLuta, dados: DadosArena, r: Sorteios): Luta {
  for (const l of ["a", "b"] as const) {
    if (cfg[l].equipe.length < 1 || cfg[l].equipe.length > 3) throw new Error(`arena: a equipe ${l} tem ${cfg[l].equipe.length} Digimon (de 1 a 3)`);
    for (const n of cfg[l].equipe) if (!dados.atlas.d[n]) throw new Error(`arena: ${n} nao esta no atlas`);
  }
  const L: Luta = {
    cfg, dados, r, cena: iniciarCena(cfg.cena), eq: { a: [], b: [] }, ativo: { a: 0, b: 0 }, trocaCd: { a: 0, b: 0 },
    projeteis: [], relogio: 0, fim: false, vencedor: null,
    querAtacar: false, querHab: false, mover: [0, 0], mouse: null, investida: false, eventos: [],
  };
  L.eq.a = cfg.a.equipe.map((n, i) => criarLutador(L, n, "a", i));
  L.eq.b = cfg.b.equipe.map((n, i) => criarLutador(L, n, "b", i));
  L.eq.a[0].x = ELIPSE.cx - ACAO.entradaX; L.eq.a[0].y = ELIPSE.cy + ACAO.entradaY;
  L.eq.b[0].x = ELIPSE.cx + ACAO.entradaX; L.eq.b[0].y = ELIPSE.cy + ACAO.entradaY;
  ligarAlvos(L); colidir(L, L.eq.a[0]); colidir(L, L.eq.b[0]);
  evento(L, { tipo: "inicio", a: [...cfg.a.equipe], b: [...cfg.b.equipe] });
  return L;
}

/** troca: voluntaria (espera TROCA_ESPERA) ou forcada quando o ativo cai */
export function trocar(L: Luta, l: Lado, slot: number, forcada: boolean): boolean {
  const sai = ativo(L, l), entra = L.eq[l][slot];
  if (!entra || entra === sai || entra.morto) return false;
  if (!forcada) {
    if (L.trocaCd[l] > 0 || sai.estado === "attack" || sai.estado === "stun" || sai.morto || L.fim) return false;
    L.trocaCd[l] = TROCA_ESPERA;
  }
  entra.x = sai.morto ? (l === "a" ? ELIPSE.cx - ACAO.entradaX : ELIPSE.cx + ACAO.entradaX) : sai.x;
  entra.y = sai.morto ? ELIPSE.cy + ACAO.entradaY : sai.y;
  entra.estado = "idle"; entra.t = 0; entra.entrada = ENTRADA; entra.dash = 0; entra.reacao = 0;
  entra.recarga = Math.max(entra.recarga, ACAO.recargaTroca);
  L.ativo[l] = slot; ligarAlvos(L);
  evento(L, { tipo: "troca", lado: l, sai: ref(sai), entra: ref(entra), forcada, x: entra.x, y: entra.y });
  return true;
}

function aplicarDano(L: Luta, at: Lutador, alvo: Lutador, dados: GolpeBase | null, hab: boolean): void {
  if (alvo.morto) return;
  dados = dados || at.g;
  if (L.r.combate() * 100 < (alvo.st.esquiva || 0)) { evento(L, { tipo: "esquiva", at: ref(at), alvo: ref(alvo), x: alvo.x, y: alvo.y }); return; }
  const crit = L.r.combate() * 100 < at.st.crit, m = mult(L, at, alvo);
  const runa = at.buffAte > L.relogio ? 1.3 : 1;
  let d = at.st.atk * (100 / (100 + alvo.st.def)) * (1 - EQ.variacao + L.r.combate() * 2 * EQ.variacao) * (crit ? 1.5 : 1) * m * (hab ? at.st.hpot : 1) * runa
    * (dados.proj ? EQ.danoDist : EQ.danoCorpo) * fatorRitmo(dados);
  d = Math.max(1, Math.round(d));
  const antes = alvo.hp;
  alvo.hp = Math.max(0, alvo.hp - d); at.dano += d; at.golpes++;
  /* o deslocamento do numero de dano: so visual, mas no prototipo sai do mesmo sorteio (fica no fluxo "visual") */
  const dx = (L.r.visual() - 0.5) * 16;
  const hits = dados.hits.length ? dados.hits : [{ prefab: "Fx_Battle_Hit_A_Normal", atraso: 0 }];
  evento(L, { tipo: "dano", at: ref(at), alvo: ref(alvo), valor: d, perda: antes - alvo.hp, crit, mult: m, hab, resta: alvo.hp, x: alvo.x, y: alvo.y, dx, hits, espelho: at.x > alvo.x });
  if (alvo.hp <= 0) {
    alvo.morto = true; mudar(alvo, "die"); alvo.caiuEm = L.relogio;
    evento(L, { tipo: "queda", u: ref(alvo), motivo: null });
  } else if (L.r.combate() * 100 < (at.st.atordoa || 0)) {
    mudar(alvo, "stun"); alvo.atordoado = ACAO.atordoaLongo; alvo.dash = 0; alvo.usandoHab = false;
    evento(L, { tipo: "atordoado", at: ref(at), alvo: ref(alvo) });
  } else if (alvo.estado !== "attack") {
    mudar(alvo, "stun"); alvo.atordoado = ACAO.atordoaCurto; alvo.dash = 0;
  }
  // empurrao: no ringue, mais forte, e na direcao do golpe, o que pode jogar para fora
  if (!alvo.morto) {
    const c = def(L), emp = c.empurrao ? (hab ? c.empurraoHab! : c.empurrao) : 1;
    const ex = alvo.x - at.x, ey = alvo.y - at.y, dd = Math.hypot(ex, ey) || 1;
    alvo.x += ex / dd * ACAO.empurrao * emp; alvo.y += ey / dd * ACAO.empurrao * emp * 0.5; prender(L, alvo); colidir(L, alvo);
  }
}

function iniciarAtaque(L: Luta, u: Lutador, mira: [number, number], hab: boolean): void {
  u.estado = "attack"; u.t = 0; u.golpeDado = false; u.mira = mira; u.viraEsq = mira[0] < u.x; u.usandoHab = !!hab;
  if (hab) {
    u.recSk = u.st.hcd * 1000;
    evento(L, { tipo: "habilidade", u: ref(u), propria: u.propria, anim: u.sk.anim, x: u.x, y: u.y });
  }
}
const dadosDe = (u: Lutador): GolpeBase => u.usandoHab ? u.sk : u.g;
const peito = (u: Lutador): [number, number] => [u.x, u.y - EQ.peito];

function soltarGolpe(L: Luta, u: Lutador): void {
  const o = u.alvo!, dados = dadosDe(u), hab = u.usandoHab;
  if (dados.proj) {
    const [px, py] = peito(u), sx = px + (u.viraEsq ? -1 : 1) * EQ.raio;
    const dx = u.mira![0] - sx, dy = u.mira![1] - py, d = Math.hypot(dx, dy) || 1;
    const vel = dados.proj.vel * PX_POR_UNIDADE * L.cfg.pvel * (def(L).projVel?.(L.cena) ?? 1);
    L.projeteis.push({ de: u, dados, hab, x: sx, y: py, altura: EQ.peito, vx: dx / d * vel, vy: dy / d * vel, resta: Math.max(u.alcance, ACAO.alcanceDist) * 1.8,
      t: 0, esq: dx < 0, fim: false, decidido: new Set() });
    return;
  }
  const alc = EQ.alcanceCorpo;
  const dx = o.x - u.x, dist = Math.hypot(dx, o.y - u.y), frente = (dx < 0) === u.viraEsq;
  if (!o.morto && dist <= alc + o.raio && frente) aplicarDano(L, u, o, dados, hab);
  else evento(L, { tipo: "golpe_ar", u: ref(u) });
}

function andar(L: Luta, u: Lutador, mx: number, my: number, vel: number, dt: number): void {
  const p = vel * (def(L).mov?.(L.cena, u) ?? 1) * dt / 1000;
  u.x += mx * p; u.y += my * p * ACAO.eixoY; prender(L, u); colidir(L, u);
}

function controlarJogador(L: Luta, u: Lutador, dt: number): void {
  const [mx, my] = L.mover, m = Math.hypot(mx, my);
  if (u.dash > 0) { u.dash -= dt; andar(L, u, u.dashDir[0], u.dashDir[1], ACAO.investidaJogador, dt); mudar(u, "run"); return; }
  if (L.investida && u.dashCd <= 0 && m) { u.dash = ACAO.investidaJogadorMs; u.dashCd = ACAO.investidaRecargaMs; u.dashDir = [mx / m, my / m]; L.investida = false; return; }
  const mira = (): [number, number] => L.mouse || [u.alvo!.x, u.alvo!.y - EQ.peito];
  if (L.querHab && u.recSk <= 0) { L.querHab = false; L.querAtacar = false; iniciarAtaque(L, u, mira(), true); return; }
  if (L.querAtacar && u.recarga <= 0) { L.querAtacar = false; iniciarAtaque(L, u, mira(), false); return; }
  L.querAtacar = false; L.querHab = false;
  const recua = mx * (u.alvo!.x - u.x) + my * (u.alvo!.y - u.y) < 0;
  if (m) { andar(L, u, mx / m, my / m, u.st.vel * (recua ? EQ.recuo : 1), dt); if (mx) u.viraEsq = mx < 0; mudar(u, "run"); }
  else { if (L.mouse) u.viraEsq = L.mouse[0] < u.x; mudar(u, "idle"); }
}

function desviar(L: Luta, u: Lutador, dt: number): void {
  const cfg = dific(L);
  for (const p of L.projeteis) {
    if (p.de.lado === u.lado || p.decidido.has(u)) continue;
    const rx = u.x - p.x, ry = (u.y - EQ.peito) - p.y, vindo = rx * p.vx + ry * p.vy > 0;
    if (!vindo || Math.hypot(rx, ry) > 260) continue;
    p.decidido.add(u);
    if (L.r.ia() < cfg.desvio) {
      const v = Math.hypot(p.vx, p.vy) || 1, lado = L.r.ia() < 0.5 ? 1 : -1;
      u.reacao = cfg.reacao; u.desvioDir = [-p.vy / v * lado, p.vx / v * lado];
    }
  }
  if (u.reacao > 0) { u.reacao -= dt; if (u.reacao <= 0) { u.dash = ACAO.desvioCpuMs; u.dashDir = u.desvioDir; } }
}

/* CPU troca em dois casos: o ativo esta com pouca vida, ou em desvantagem de atributo com alguem no banco com vantagem; decide uma vez
   por situacao */
function cpuTroca(L: Luta, l: Lado): void {
  const u = ativo(L, l), inimigo = ativo(L, outro(l));
  if (L.trocaCd[l] > 0 || inimigo.morto) return;
  const ruim = mult(L, u, inimigo) < 1 || mult(L, inimigo, u) > 1;
  const fraco = u.hp / u.st.hp <= 0.3;
  const chave = `${inimigo.n}|${fraco}|${ruim}`;
  if ((!fraco && !ruim) || u.decisao === chave) return;
  u.decisao = chave;
  if (L.r.ia() > dific(L).troca) return;
  const nota = (x: Lutador) => mult(L, x, inimigo) * 2 - mult(L, inimigo, x) + x.hp / x.st.hp;
  const banco = L.eq[l].filter(x => !x.morto && x !== u && x.hp / x.st.hp > 0.4 && (fraco || mult(L, x, inimigo) > 1))
    .sort((p, q) => nota(q) - nota(p));
  if (banco.length && nota(banco[0]) > nota(u)) trocar(L, l, banco[0].slot, false);
}

function atualizar(L: Luta, u: Lutador, dt: number): void {
  u.t += dt;
  if (u.morto) return;
  const o = u.alvo!, dx = o.x - u.x, dy = o.y - u.y, dist = Math.hypot(dx, dy);
  u.recarga -= dt; u.dashCd -= dt; u.recSk -= dt;
  if (u.foraAte) return;   // caiu do ringue: espera voltar ao centro
  if (u.entrada > 0) { u.entrada -= dt; mudar(u, "idle"); if (!o.morto) u.viraEsq = dx < 0; return; }
  if (u.estado === "stun") { u.atordoado -= dt; if (u.atordoado <= 0) mudar(u, "idle"); return; }
  if (u.estado === "attack") {
    const dg = dadosDe(u);
    if (!dg.proj && !u.golpeDado && !o.morto && EQ.investida > 0) {
      const ix = o.x - u.x, iy = o.y - u.y, id = Math.hypot(ix, iy) || 1;
      if (id > EQ.alcanceCorpo * 0.6 + o.raio) andar(L, u, ix / id, iy / id / ACAO.eixoY, EQ.investida / Math.max(0.15, dg.t), dt);
      u.viraEsq = ix < 0;
    }
    if (!u.golpeDado && u.t >= dg.t * 1000) { u.golpeDado = true; if (!o.morto) soltarGolpe(L, u); }
    if (u.t >= (u.usandoHab ? u.msSk : u.msAtk)) { mudar(u, "idle"); u.recarga = Math.max(ACAO.recargaMin, u.st.cad - u.msAtk); u.usandoHab = false; }
    return;
  }
  if (o.morto) { mudar(u, "idle"); return; }
  if (L.cfg.jogador && u.lado === "a") { controlarJogador(L, u, dt); return; }
  cpuTroca(L, u.lado); if (ativo(L, u.lado) !== u) return;
  u.viraEsq = dx < 0;
  desviar(L, u, dt);
  if (u.dash > 0) { u.dash -= dt; andar(L, u, u.dashDir[0], u.dashDir[1], ACAO.desvioCpu, dt); mudar(u, "run"); return; }
  // mira: erro da dificuldade, maior se o alvo esta numa moita ou se a arena atrapalha (tempestade)
  const e = dific(L).erro * (o.escondido ? 4 : 1) * (def(L).erro?.(L.cena) ?? 1);
  const mira = (): [number, number] => [o.x + (L.r.ia() - 0.5) * 2 * e, o.y - EQ.peito + (L.r.ia() - 0.5) * e];
  // pilar quebravel no caminho nao impede atirar (o tiro abre caminho); arvore ou rocha sim, e o lutador contorna
  const ob = bloqueio(L, u, o), livre = !ob || ob.hp !== undefined;
  u.bloq = ob && !livre ? u.bloq + dt : 0;
  const alcHab = u.sk.proj ? ACAO.alcanceDist : EQ.alcanceCorpo;
  // corpo a corpo conta o corpo do alvo: sem isso, dois grandes se empurram para fora do alcance
  const folga = (p: unknown) => p ? 0 : o.raio * 0.8 + EQ.investida * 0.8;
  if (u.recSk <= 0 && dist <= alcHab + folga(u.sk.proj) && (livre || !u.sk.proj)) { iniciarAtaque(L, u, mira(), true); return; }
  if (dist <= u.alcance + folga(u.g.proj) && u.recarga <= 0 && (livre || !u.g.proj)) { iniciarAtaque(L, u, mira(), false); return; }
  let mx = 0, my = 0;
  if (!livre) {
    // contorna andando de lado; os dois lados desviam para o mesmo lado do mundo e trocam juntos a cada 4 s
    u.ladoDesvio = (u.lado === "a" ? 1 : -1) * (Math.floor(L.relogio / 4000) % 2 ? -1 : 1);
    const avanco = dist > u.alcance * 0.9 ? 0.6 : 0.3;
    mx = -dy / dist * u.ladoDesvio * 1.3 + dx / dist * avanco; my = dx / dist * u.ladoDesvio * 1.3 + dy / dist * avanco;
  } else {
    u.ladoDesvio = 0;
    if (dist > u.alcance * 0.9) { mx = dx / dist; my = dy / dist; }
    else if (u.g.proj && dist < u.alcance * 0.5) { mx = -dx / dist; my = -dy / dist; }
    else { u.fase += dt / 700; mx = -dy / dist * Math.sin(u.fase) * 0.6; my = dx / dist * Math.sin(u.fase) * 0.6; }
  }
  // regras da arena: fugir de perigos, buscar vantagens; obstaculos proximos empurram o rumo
  const [gx, gy] = def(L).guia?.(L.cena, L, u) ?? [0, 0]; mx += gx; my += gy;
  for (const ob2 of L.cena.obst) {
    if (ob2.hp !== undefined && ob2.hp <= 0) continue;
    const ox = u.x - ob2.x, oy = (u.y - ob2.y) / 0.6, od = Math.hypot(ox, oy);
    if (od < ob2.r + u.raio + 12) { mx += ox / (od || 1) * 0.9; my += oy / (od || 1) * 0.9 * 0.6; }
  }
  const m = Math.hypot(mx, my);
  const recua = mx * dx + my * dy < 0;
  if (m > 0.15) { andar(L, u, mx / Math.max(1, m), my / Math.max(1, m), u.st.vel * (recua ? EQ.recuo : 1), dt); mudar(u, "run"); } else mudar(u, "idle");
}

/** aplica uma entrada do jogador (so com cfg.jogador; a CPU nunca le entrada) */
export function aplicarEntrada(L: Luta, e: Entrada): void {
  if (!L.cfg.jogador) throw new Error("arena: entrada do jogador numa luta CPU x CPU");
  switch (e.tipo) {
    case "mover": L.mover = [e.mx, e.my]; break;
    case "mira": L.mouse = [e.x, e.y]; break;
    case "sem_mira": L.mouse = null; break;
    case "atacar": L.querAtacar = true; break;
    case "habilidade": L.querHab = true; break;
    case "investida": L.investida = e.ligada; break;
    case "trocar": trocar(L, "a", e.slot, false); break;
  }
}

/** um passo de PASSO_MS: as entradas do jogador, a regra da arena, os dois ativos, os corpos, os projeteis, as trocas e o fim.
    Devolve os eventos do passo. */
export function passo(L: Luta, entradas: readonly Entrada[] = []): Evento[] {
  const dt = PASSO_MS;
  for (const e of entradas) aplicarEntrada(L, e);
  L.relogio += dt;
  L.trocaCd.a -= dt; L.trocaCd.b -= dt;
  def(L).tick?.(L.cena, L, dt);
  const [p, q] = [ativo(L, "a"), ativo(L, "b")];
  atualizar(L, p, dt); atualizar(L, q, dt);
  // corpos nao se sobrepoem
  const A1 = ativo(L, "a"), B1 = ativo(L, "b");
  if (!A1.morto && !B1.morto) {
    const dx = B1.x - A1.x, dy = (B1.y - A1.y) / 0.7, d = Math.hypot(dx, dy) || 0.01, min = (A1.raio + B1.raio) * 0.9;
    if (d < min) { const k = (min - d) / 2 / d; A1.x -= dx * k; A1.y -= dy * k * 0.7; B1.x += dx * k; B1.y += dy * k * 0.7; prender(L, A1); prender(L, B1); }
  }
  // projeteis em linha reta: acertam o ativo inimigo que cruzarem, somem ao passar do alcance
  for (const pr of L.projeteis) {
    const n = Math.max(1, Math.ceil(Math.hypot(pr.vx, pr.vy) * dt / 1000 / 6));
    pr.t += dt;
    for (let k = 0; k < n && !pr.fim; k++) {
      const sx = pr.vx * dt / 1000 / n, sy = pr.vy * dt / 1000 / n;
      pr.x += sx; pr.y += sy; pr.resta -= Math.hypot(sx, sy);
      const o = ativo(L, outro(pr.de.lado));
      const ob = obstaculoEm(L, pr.x, pr.y + pr.altura);
      if (ob) {
        pr.fim = true;
        if (ob.hp !== undefined) { ob.hp--; evento(L, { tipo: "pilar", u: ref(pr.de), quebrou: ob.hp <= 0 }); }
        else evento(L, { tipo: "tiro_bloqueado", u: ref(pr.de), obst: ob.img });
      }
      else if (!o.morto && o.entrada <= 0 && !o.foraAte && Math.hypot(o.x - pr.x, (o.y - EQ.peito) - pr.y) <= o.raio + 6) { pr.fim = true; aplicarDano(L, pr.de, o, pr.dados, pr.hab); }
      else if (pr.resta <= 0 || !dentroArena(pr.x, pr.y + 30)) { pr.fim = true; evento(L, { tipo: "tiro_errou", u: ref(pr.de) }); }
    }
  }
  L.projeteis = L.projeteis.filter(pr => !pr.fim);
  // quem caiu sai depois da animacao de queda; entra o proximo de pe
  for (const l of ["a", "b"] as const) {
    const u = ativo(L, l);
    if (u.morto && !L.fim && L.relogio - u.caiuEm > Math.min(1200, duracaoTag(u.A, "Die") + 200)) {
      const prox = L.eq[l].find(x => !x.morto);
      if (prox) trocar(L, l, prox.slot, true);
    }
  }
  if (!L.fim) {
    const ra = vivos(L, "a").length, rb = vivos(L, "b").length;
    if ((ra === 0 || rb === 0) && L.projeteis.length === 0) {
      L.fim = true; L.vencedor = ra ? "a" : rb ? "b" : null;
      evento(L, { tipo: "fim", vencedor: L.vencedor, vivos: L.vencedor ? vivos(L, L.vencedor).length : 0, relogio: L.relogio });
    }
  }
  const ev = L.eventos; L.eventos = [];
  return ev;
}
