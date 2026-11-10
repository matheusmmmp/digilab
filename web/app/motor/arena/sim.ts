/* A simulacao da luta da POC, sem DOM (docs/TAREFA_V3_LUTA_POC.md, LP1): porte de web/app/arena/sim.ts do commit efb2ded (que e o porte do
   arena.html, sha256 f3be1160...91fbeb, na mesma ordem de contas e de sorteios). Passo de tempo fixo (PASSO_MS); os sorteios vem de
   Sorteios (um fluxo por uso no jogo, sequencia unica so na medicao); a saida sao eventos com tipo.
   As quatro mudancas da secao 3.2 e nada mais:
   1. a aritmetica da D-7: Math.hypot -> dist (Math.sqrt(dx*dx + dy*dy)), Math.sin -> seno (polinomio fixo), sem Math.pow (o fatorRitmo
      vem pronto na tabela, `fr`) e sem Math.random;
   2. os dados do Digimon vem da tabela do git (formas.ts) e os numeros do lutador chegam prontos (Stats);
   3. so 1 contra 1, os dois lados pela IA: sairam o modo jogador, a entrada, as equipes e as trocas;
   4. nada daqui toca no pet, no log nem no save (a LP2 liga). */
import { ACAO, DIFIC, ELIPSE, EQ, PASSO_MS, PX_POR_UNIDADE } from "./constantes.ts";
import { dist, seno } from "./aritmetica.ts";
import { CENAS, iniciarCena } from "./cenas.ts";
import { bloqueio, colidir, dentroArena, evento, lutador, mudar, obstaculoEm, outro, prender, ref } from "./nucleo.ts";
import type { Atributo, ConfigLuta, Evento, GolpeBase, Lado, Luta, Lutador, Sorteios } from "./tipos.ts";

const def = (L: Luta) => CENAS[L.cena.id];
const dific = (L: Luta) => DIFIC[L.cfg.dific];

/** triangulo de atributos (o classico; o jogo nao traz a regra): chave vence valor */
export const VENCE: Partial<Record<Atributo, Atributo>> = { Vaccine: "Virus", Virus: "Data", Data: "Vaccine" };
export function multAtr(a: Atributo, b: Atributo, forca: number): number {
  if (VENCE[a] === b) return forca;
  if (VENCE[b] === a) return 1 / forca;
  return 1;
}
const mult = (L: Luta, a: Lutador, b: Lutador) => multAtr(a.atr, b.atr, L.cfg.forca);

function conferirStats(l: Lado, cfg: ConfigLuta): void {
  const s = cfg[l].stats;
  for (const k of ["hp", "atk", "def", "vel", "cad", "crit", "hcd", "hpot", "esquiva", "atordoa", "erro"] as const)
    if (typeof s[k] !== "number" || !Number.isFinite(s[k])) throw new Error(`arena: stat ${k} do lado ${l} nao e numero (${String(s[k])})`);
  if (s.hp < 1) throw new Error(`arena: vida do lado ${l} menor que 1 (${s.hp})`);
  const v0 = cfg[l].vida0;
  if (v0 !== undefined && !(Number.isInteger(v0) && v0 >= 1 && v0 <= s.hp)) throw new Error(`arena: vida inicial do lado ${l} fora de [1, ${s.hp}] (${v0})`);
}

function criarLutador(L: Luta, lado: Lado): Lutador {
  const { forma, stats, vida0 } = L.cfg[lado];
  const g = forma.golpe, sk = forma.habilidade || g, st = { ...stats };
  /* a ordem dos sorteios e a do literal do prototipo: recSk, recarga, fase */
  const recSk = ACAO.recSkIni + L.r.ia() * ACAO.recSkVar, recarga = ACAO.recargaIni + L.r.ia() * ACAO.recargaVar, fase = L.r.ia() * 6.28;
  return {
    n: forma.digimon, lado, g, sk, propria: !!forma.habilidade, usandoHab: false, st, atr: forma.atributo,
    x: 0, y: 0, hp: vida0 ?? st.hp, viraEsq: lado === "b", estado: "idle", t: 0,
    recarga, recSk, golpeDado: false,
    msAtk: forma.msGolpe, msSk: forma.msHabilidade,
    alcance: g.proj ? ACAO.alcanceDist : EQ.alcanceCorpo, raio: EQ.raio, alvo: null, fase,
    morto: false, dano: 0, golpes: 0, mira: null, dash: 0, dashCd: 0, dashDir: [0, 0], reacao: 0, desvioDir: [0, 0],
    atordoado: 0, caiuEm: 0, foraAte: 0, escondido: false, naRuna: 0, buffAte: 0, bloq: 0, ladoDesvio: 0, esperaTiro: 0,
    acDano: 0, ultAmb: 0, ultNum: 0, decisao: "",
  };
}

/** uma luta nova: monta o lado a e depois o b, poe os dois em campo e confere a colisao inicial */
export function criarLuta(cfg: ConfigLuta, r: Sorteios): Luta {
  conferirStats("a", cfg); conferirStats("b", cfg);
  if (!CENAS[cfg.cena]) throw new Error(`arena: mapa desconhecido ${String(cfg.cena)}`);
  if (!DIFIC[cfg.dific]) throw new Error(`arena: dificuldade desconhecida ${String(cfg.dific)}`);
  const L = { cfg, r, cena: iniciarCena(cfg.cena), projeteis: [], relogio: 0, fim: false, vencedor: null, eventos: [] } as unknown as Luta;
  L.a = criarLutador(L, "a");
  L.b = criarLutador(L, "b");
  L.a.x = ELIPSE.cx - ACAO.entradaX; L.a.y = ELIPSE.cy + ACAO.entradaY;
  L.b.x = ELIPSE.cx + ACAO.entradaX; L.b.y = ELIPSE.cy + ACAO.entradaY;
  L.a.alvo = L.b; L.b.alvo = L.a; colidir(L, L.a); colidir(L, L.b);
  evento(L, { tipo: "inicio", a: L.a.n, b: L.b.n });
  return L;
}

function aplicarDano(L: Luta, at: Lutador, alvo: Lutador, dados: GolpeBase | null, hab: boolean): void {
  if (alvo.morto) return;
  dados = dados || at.g;
  if (L.r.combate() * 100 < (alvo.st.esquiva || 0)) { evento(L, { tipo: "esquiva", at: ref(at), alvo: ref(alvo), x: alvo.x, y: alvo.y }); return; }
  const crit = L.r.combate() * 100 < at.st.crit, m = mult(L, at, alvo);
  const runa = at.buffAte > L.relogio ? 1.3 : 1;
  let d = at.st.atk * (100 / (100 + alvo.st.def)) * (1 - EQ.variacao + L.r.combate() * 2 * EQ.variacao) * (crit ? 1.5 : 1) * m * (hab ? at.st.hpot : 1) * runa
    * (dados.proj ? EQ.danoDist : EQ.danoCorpo) * dados.fr;
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
    const ex = alvo.x - at.x, ey = alvo.y - at.y, dd = dist(ex, ey) || 1;
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
    const dx = u.mira![0] - sx, dy = u.mira![1] - py, d = dist(dx, dy) || 1;
    const vel = dados.proj.vel * PX_POR_UNIDADE * L.cfg.pvel * (def(L).projVel?.(L.cena) ?? 1);
    L.projeteis.push({ de: u, dados, hab, x: sx, y: py, altura: EQ.peito, vx: dx / d * vel, vy: dy / d * vel, resta: Math.max(u.alcance, ACAO.alcanceDist) * 1.8,
      t: 0, esq: dx < 0, fim: false, decidido: new Set() });
    return;
  }
  const alc = EQ.alcanceCorpo;
  const dx = o.x - u.x, d2 = dist(dx, o.y - u.y), frente = (dx < 0) === u.viraEsq;
  if (!o.morto && d2 <= alc + o.raio && frente) aplicarDano(L, u, o, dados, hab);
  else evento(L, { tipo: "golpe_ar", u: ref(u) });
}

function andar(L: Luta, u: Lutador, mx: number, my: number, vel: number, dt: number): void {
  const p = vel * (def(L).mov?.(L.cena, u) ?? 1) * dt / 1000;
  u.x += mx * p; u.y += my * p * ACAO.eixoY; prender(L, u); colidir(L, u);
}

function desviar(L: Luta, u: Lutador, dt: number): void {
  const cfg = dific(L);
  for (const p of L.projeteis) {
    if (p.de.lado === u.lado || p.decidido.has(u)) continue;
    const rx = u.x - p.x, ry = (u.y - EQ.peito) - p.y, vindo = rx * p.vx + ry * p.vy > 0;
    if (!vindo || dist(rx, ry) > 260) continue;
    p.decidido.add(u);
    if (L.r.ia() < cfg.desvio) {
      const v = dist(p.vx, p.vy) || 1, lado = L.r.ia() < 0.5 ? 1 : -1;
      u.reacao = cfg.reacao; u.desvioDir = [-p.vy / v * lado, p.vx / v * lado];
    }
  }
  if (u.reacao > 0) { u.reacao -= dt; if (u.reacao <= 0) { u.dash = ACAO.desvioCpuMs; u.dashDir = u.desvioDir; } }
}

/* A IA da POC pensa em trocar quando o lutador esta com pouca vida ou em desvantagem de atributo, uma vez por situacao, e tira um sorteio
   do fluxo "ia" para isso. No 1 contra 1 nao ha banco e a troca nunca acontece, mas o sorteio fica: e a mesma sequencia da POC 1 contra 1
   (a luta do pet do #448), o que deixa a fidelidade bit a bit conferivel (scripts/arena_fidelidade.ts). */
function sorteioDaTroca(L: Luta, u: Lutador): void {
  const inimigo = u.alvo!;
  if (inimigo.morto) return;
  const ruim = mult(L, u, inimigo) < 1 || mult(L, inimigo, u) > 1;
  const fraco = u.hp / u.st.hp <= 0.3;
  const chave = `${inimigo.n}|${fraco}|${ruim}`;
  if ((!fraco && !ruim) || u.decisao === chave) return;
  u.decisao = chave;
  L.r.ia();
}

function atualizar(L: Luta, u: Lutador, dt: number): void {
  u.t += dt;
  if (u.morto) return;
  const o = u.alvo!, dx = o.x - u.x, dy = o.y - u.y, d = dist(dx, dy);
  u.recarga -= dt; u.dashCd -= dt; u.recSk -= dt;
  if (u.foraAte) return;   // caiu do ringue: espera voltar ao centro
  if (u.estado === "stun") { u.atordoado -= dt; if (u.atordoado <= 0) mudar(u, "idle"); return; }
  if (u.estado === "attack") {
    const dg = dadosDe(u);
    if (!dg.proj && !u.golpeDado && !o.morto && EQ.investida > 0) {
      const ix = o.x - u.x, iy = o.y - u.y, id = dist(ix, iy) || 1;
      if (id > EQ.alcanceCorpo * 0.6 + o.raio) andar(L, u, ix / id, iy / id / ACAO.eixoY, EQ.investida / Math.max(0.15, dg.t), dt);
      u.viraEsq = ix < 0;
    }
    /* a distancia do tiro (D-LP5-12): na preparacao do tiro, se afasta do alvo que esta perto */
    const T = L.cfg.tiro;
    if (T && T.recuaNaPrep > 0 && dg.proj && !u.golpeDado && !o.morto) {
      const ix = o.x - u.x, iy = o.y - u.y, id = dist(ix, iy) || 1;
      if (id < Math.max(T.distMin, u.alcance * T.recuaAbaixo)) andar(L, u, -ix / id, -iy / id, u.st.vel * T.recuaNaPrep, dt);
    }
    if (!u.golpeDado && u.t >= dg.t * 1000) { u.golpeDado = true; if (!o.morto) soltarGolpe(L, u); }
    if (u.t >= (u.usandoHab ? u.msSk : u.msAtk)) { mudar(u, "idle"); u.recarga = Math.max(ACAO.recargaMin, u.st.cad - u.msAtk); u.usandoHab = false; }
    return;
  }
  if (o.morto) { mudar(u, "idle"); return; }
  sorteioDaTroca(L, u);
  u.viraEsq = dx < 0;
  desviar(L, u, dt);
  if (u.dash > 0) { u.dash -= dt; andar(L, u, u.dashDir[0], u.dashDir[1], ACAO.desvioCpu, dt); mudar(u, "run"); return; }
  // mira: o erro de mira do lutador (LP2; na POC, o da dificuldade), maior se o alvo esta numa moita ou se a arena atrapalha (tempestade)
  const e = u.st.erro * (o.escondido ? 4 : 1) * (def(L).erro?.(L.cena) ?? 1);
  const mira = (): [number, number] => [o.x + (L.r.ia() - 0.5) * 2 * e, o.y - EQ.peito + (L.r.ia() - 0.5) * e];
  // pilar quebravel no caminho nao impede atirar (o tiro abre caminho); arvore ou rocha sim, e o lutador contorna
  const ob = bloqueio(L, u, o), livre = !ob || ob.hp !== undefined;
  u.bloq = ob && !livre ? u.bloq + dt : 0;
  const alcHab = u.sk.proj ? ACAO.alcanceDist : EQ.alcanceCorpo;
  // corpo a corpo conta o corpo do alvo: sem isso, dois grandes se empurram para fora do alcance
  const folga = (p: unknown) => p ? 0 : o.raio * 0.8 + EQ.investida * 0.8;
  /* a distancia do tiro (D-LP5-12): abaixo da distMin o tiro de projetil espera ate o esperaMax; sem o `tiro`, a luta da POC */
  const T = L.cfg.tiro;
  let perto = false;
  if (T && T.distMin > 0 && (u.g.proj || u.sk.proj) && d < T.distMin) { u.esperaTiro += dt; perto = u.esperaTiro < T.esperaMax; } else u.esperaTiro = 0;
  if (u.recSk <= 0 && d <= alcHab + folga(u.sk.proj) && (livre || !u.sk.proj) && !(perto && u.sk.proj)) { iniciarAtaque(L, u, mira(), true); return; }
  if (d <= u.alcance + folga(u.g.proj) && u.recarga <= 0 && (livre || !u.g.proj) && !(perto && u.g.proj)) { iniciarAtaque(L, u, mira(), false); return; }
  let mx = 0, my = 0;
  if (!livre) {
    // contorna andando de lado; os dois lados desviam para o mesmo lado do mundo e trocam juntos a cada 4 s
    u.ladoDesvio = (u.lado === "a" ? 1 : -1) * (Math.floor(L.relogio / 4000) % 2 ? -1 : 1);
    const avanco = d > u.alcance * 0.9 ? 0.6 : 0.3;
    mx = -dy / d * u.ladoDesvio * 1.3 + dx / d * avanco; my = dx / d * u.ladoDesvio * 1.3 + dy / d * avanco;
  } else {
    u.ladoDesvio = 0;
    if (d > u.alcance * 0.9) { mx = dx / d; my = dy / d; }
    else if (u.g.proj && d < (T ? Math.max(T.distMin, u.alcance * T.recuaAbaixo) : u.alcance * 0.5)) { mx = -dx / d; my = -dy / d; }
    else { u.fase += dt / 700; mx = -dy / d * seno(u.fase) * 0.6; my = dx / d * seno(u.fase) * 0.6; }
  }
  // regras da arena: fugir de perigos, buscar vantagens; obstaculos proximos empurram o rumo
  const [gx, gy] = def(L).guia?.(L.cena, L, u) ?? [0, 0]; mx += gx; my += gy;
  for (const ob2 of L.cena.obst) {
    if (ob2.hp !== undefined && ob2.hp <= 0) continue;
    const ox = u.x - ob2.x, oy = (u.y - ob2.y) / 0.6, od = dist(ox, oy);
    if (od < ob2.r + u.raio + 12) { mx += ox / (od || 1) * 0.9; my += oy / (od || 1) * 0.9 * 0.6; }
  }
  const m = dist(mx, my);
  const recua = mx * dx + my * dy < 0;
  const vRecuo = T && u.g.proj ? T.recuo : EQ.recuo;
  if (m > 0.15) { andar(L, u, mx / Math.max(1, m), my / Math.max(1, m), u.st.vel * (recua ? vRecuo : 1), dt); mudar(u, "run"); } else mudar(u, "idle");
}

/** um passo de PASSO_MS: a regra da arena, os dois lutadores, os corpos, os projeteis e o fim. Devolve os eventos do passo. */
export function passo(L: Luta): Evento[] {
  const dt = PASSO_MS;
  L.relogio += dt;
  def(L).tick?.(L.cena, L, dt);
  atualizar(L, L.a, dt); atualizar(L, L.b, dt);
  // corpos nao se sobrepoem
  const A1 = L.a, B1 = L.b;
  if (!A1.morto && !B1.morto) {
    const dx = B1.x - A1.x, dy = (B1.y - A1.y) / 0.7, d = dist(dx, dy) || 0.01, min = (A1.raio + B1.raio) * 0.9;
    if (d < min) { const k = (min - d) / 2 / d; A1.x -= dx * k; A1.y -= dy * k * 0.7; B1.x += dx * k; B1.y += dy * k * 0.7; prender(L, A1); prender(L, B1); }
  }
  // projeteis em linha reta: acertam o inimigo que cruzarem, somem ao passar do alcance
  for (const pr of L.projeteis) {
    const n = Math.max(1, Math.ceil(dist(pr.vx, pr.vy) * dt / 1000 / 6));
    pr.t += dt;
    for (let k = 0; k < n && !pr.fim; k++) {
      const sx = pr.vx * dt / 1000 / n, sy = pr.vy * dt / 1000 / n;
      pr.x += sx; pr.y += sy; pr.resta -= dist(sx, sy);
      const o = lutador(L, outro(pr.de.lado));
      const ob = obstaculoEm(L, pr.x, pr.y + pr.altura);
      if (ob) {
        pr.fim = true;
        if (ob.hp !== undefined) { ob.hp--; evento(L, { tipo: "pilar", u: ref(pr.de), quebrou: ob.hp <= 0 }); }
        else evento(L, { tipo: "tiro_bloqueado", u: ref(pr.de), obst: ob.img });
      }
      else if (!o.morto && !o.foraAte && dist(o.x - pr.x, (o.y - EQ.peito) - pr.y) <= o.raio + 6) { pr.fim = true; aplicarDano(L, pr.de, o, pr.dados, pr.hab); }
      else if (pr.resta <= 0 || !dentroArena(pr.x, pr.y + 30)) { pr.fim = true; evento(L, { tipo: "tiro_errou", u: ref(pr.de) }); }
    }
  }
  L.projeteis = L.projeteis.filter(pr => !pr.fim);
  if (!L.fim && (L.a.morto || L.b.morto) && L.projeteis.length === 0) {
    L.fim = true; L.vencedor = !L.a.morto ? "a" : !L.b.morto ? "b" : null;
    evento(L, { tipo: "fim", vencedor: L.vencedor, relogio: L.relogio });
  }
  const ev = L.eventos; L.eventos = [];
  return ev;
}
