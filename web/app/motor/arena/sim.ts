/* A simulacao da luta da POC, sem DOM (docs/TAREFA_V3_LUTA_POC.md, LP1): porte de web/app/arena/sim.ts do commit efb2ded (que e o porte do
   arena.html, sha256 f3be1160...91fbeb, na mesma ordem de contas e de sorteios). Passo de tempo fixo (PASSO_MS); os sorteios vem de
   Sorteios (um fluxo por uso no jogo, sequencia unica so na medicao); a saida sao eventos com tipo.
   As quatro mudancas da secao 3.2 e nada mais:
   1. a aritmetica da D-7: Math.hypot -> dist (Math.sqrt(dx*dx + dy*dy)), Math.sin -> seno (polinomio fixo), sem Math.pow (o fatorRitmo
      vem pronto na tabela, `fr`) e sem Math.random;
   2. os dados do Digimon vem da tabela do git (formas.ts) e os numeros do lutador chegam prontos (Stats);
   3. so 1 contra 1, os dois lados pela IA: sairam o modo jogador, a entrada, as equipes e as trocas;
   4. nada daqui toca no pet, no log nem no save (a LP2 liga).
   LP6-1 (docs/PLANO_LP6_SEGUNDO_GOLPE.md), cada um atras da sua chave da entrada, desligada: o golpe de apoio (`apoio`) e a elipse pelo
   estagio dos dois (`arenaPorEstagio`). Sem as chaves, a luta sai byte a byte igual (test/arena_lp6_gabarito.test.ts). */
import { ACAO, DIFIC, ELIPSE, EQ, ORDEM_ESTAGIOS, PASSO_MS, PX_POR_UNIDADE, RECUO_APOIO_SEM_TIRO_MS, type Apoio, type ArenaPorEstagio } from "./constantes.ts";
import { dist, seno } from "./aritmetica.ts";
import { CENAS, iniciarCena } from "./cenas.ts";
import { bloqueio, colidir, dentroArena, evento, lutador, mudar, obstaculoEm, outro, prender, ref } from "./nucleo.ts";
import type { Atributo, ConfigLuta, DadosForma, Elipse, Evento, GolpeBase, Lado, Luta, Lutador, Sorteios } from "./tipos.ts";

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
  for (const k of ["perc", "agil"] as const) if (s[k] !== undefined && !(typeof s[k] === "number" && Number.isFinite(s[k]) && s[k]! > 0)) throw new Error(`arena: ${k} do lado ${l} invalida (${String(s[k])})`);
  const v0 = cfg[l].vida0;
  if (v0 !== undefined && !(Number.isInteger(v0) && v0 >= 1 && v0 <= s.hp)) throw new Error(`arena: vida inicial do lado ${l} fora de [1, ${s.hp}] (${v0})`);
}

/** o fator da elipse pelo maior estagio dos dois (LP6-1, secao 4a): o do Ultimate, o do Mega ou 1 (In-Training, Rookie e Champion) */
const indiceEstagio = (f: DadosForma): number => {
  const k = (ORDEM_ESTAGIOS as readonly string[]).indexOf(f.estagio);
  if (k < 0) throw new Error(`arena: estagio desconhecido ${String(f.estagio)} (${f.digimon})`);
  return k;
};
/** o apoio vale nesta luta? (LP6-3, D-LP6-3-7): sem o `desde`, sempre; com ele, se o maior estagio dos dois e pelo menos o dele */
export const apoioNaLuta = (a: DadosForma, b: DadosForma, ap: Apoio): boolean =>
  ap.desde === undefined || Math.max(indiceEstagio(a), indiceEstagio(b)) >= (ORDEM_ESTAGIOS as readonly string[]).indexOf(ap.desde);
export function fatorElipse(a: DadosForma, b: DadosForma, F: ArenaPorEstagio): number {
  const m = ORDEM_ESTAGIOS[Math.max(indiceEstagio(a), indiceEstagio(b))];
  return m === "Mega" ? F.Mega : m === "Ultimate" ? F.Ultimate : 1;
}

function criarLutador(L: Luta, lado: Lado): Lutador {
  const { forma, stats, vida0 } = L.cfg[lado];
  /* o golpe de apoio (LP6-1): so com a chave; a forma tem de trazer o apoio, do tipo que falta ao golpe, e o clipe dele */
  if (L.cfg.apoio && !(forma.apoio && typeof forma.msApoio === "number" && forma.msApoio > 0 && !forma.apoio.proj === !!forma.golpe.proj))
    throw new Error(`arena: a forma ${forma.digimon} nao tem o golpe de apoio do tipo que falta (motor/arena/formas.ts)`);
  /* o apoio pelo estagio (LP6-3, D-LP6-3-7): abaixo do `desde`, os dois lutam sem ele, como sem a chave */
  const ap = L.cfg.apoio && apoioNaLuta(L.cfg.a.forma, L.cfg.b.forma, L.cfg.apoio) ? forma.apoio! : null;
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
    atordoado: 0, caiuEm: 0, foraAte: 0, escondido: false, naRuna: 0, buffAte: 0, bloq: 0, ladoDesvio: 0, esperaTiro: 0, nAtaque: 0, leuAtaque: -1, contraPend: false,
    ap, msAp: ap ? forma.msApoio! : 0, recAp: 0, usandoApoio: false, longeMs: 0, recuoAp: 0,
    acDano: 0, ultAmb: 0, ultNum: 0, decisao: "",
  };
}

/** uma luta nova: monta o lado a e depois o b, poe os dois em campo e confere a colisao inicial */
export function criarLuta(cfg: ConfigLuta, r: Sorteios): Luta {
  conferirStats("a", cfg); conferirStats("b", cfg);
  if (!CENAS[cfg.cena]) throw new Error(`arena: mapa desconhecido ${String(cfg.cena)}`);
  if (!DIFIC[cfg.dific]) throw new Error(`arena: dificuldade desconhecida ${String(cfg.dific)}`);
  /* a elipse pelo estagio dos dois (LP6-1): sem a chave, a ELIPSE de sempre (o mesmo objeto) e o fator 1 */
  const esc = cfg.arenaPorEstagio ? fatorElipse(cfg.a.forma, cfg.b.forma, cfg.arenaPorEstagio) : 1;
  const el: Elipse = esc === 1 ? ELIPSE : { cx: ELIPSE.cx, cy: ELIPSE.cy, rx: ELIPSE.rx * esc, ry: ELIPSE.ry * esc };
  const L = { cfg, r, cena: iniciarCena(cfg.cena, esc), el, esc, projeteis: [], relogio: 0, fim: false, vencedor: null, eventos: [] } as unknown as Luta;
  L.a = criarLutador(L, "a");
  L.b = criarLutador(L, "b");
  /* os pontos de inicio escalam com a elipse (x 1 e exato: sem a chave, os de sempre) */
  L.a.x = el.cx - ACAO.entradaX * esc; L.a.y = el.cy + ACAO.entradaY * esc;
  L.b.x = el.cx + ACAO.entradaX * esc; L.b.y = el.cy + ACAO.entradaY * esc;
  L.a.alvo = L.b; L.b.alvo = L.a; colidir(L, L.a); colidir(L, L.b);
  evento(L, { tipo: "inicio", a: L.a.n, b: L.b.n });
  return L;
}

function aplicarDano(L: Luta, at: Lutador, alvo: Lutador, dados: GolpeBase | null, hab: boolean): void {
  if (alvo.morto) return;
  dados = dados || at.g;
  /* o golpe de apoio (LP6-1): o tipo de dano e o `fr` do golpe principal, vezes a fracao do apoio */
  const apoio = at.ap !== null && dados === at.ap, base = apoio ? at.g : dados;
  if (L.r.combate() * 100 < (alvo.st.esquiva || 0)) { evento(L, { tipo: "esquiva", at: ref(at), alvo: ref(alvo), x: alvo.x, y: alvo.y }); return; }
  const crit = L.r.combate() * 100 < at.st.crit, m = mult(L, at, alvo);
  const runa = at.buffAte > L.relogio ? 1.3 : 1;
  let d = at.st.atk * (100 / (100 + alvo.st.def)) * (1 - EQ.variacao + L.r.combate() * 2 * EQ.variacao) * (crit ? 1.5 : 1) * m * (hab ? at.st.hpot : 1) * runa
    * (base.proj ? (L.cfg.tiro ? L.cfg.tiro.danoProj : EQ.danoDist) : EQ.danoCorpo) * base.fr;
  if (apoio) d *= L.cfg.apoio!.dano;
  d = Math.max(1, Math.round(d));
  const antes = alvo.hp;
  alvo.hp = Math.max(0, alvo.hp - d); at.dano += d; at.golpes++;
  /* o deslocamento do numero de dano: so visual, mas no prototipo sai do mesmo sorteio (fica no fluxo "visual") */
  const dx = (L.r.visual() - 0.5) * 16;
  const hits = dados.hits.length ? dados.hits : [{ prefab: "Fx_Battle_Hit_A_Normal", atraso: 0 }];
  evento(L, { tipo: "dano", at: ref(at), alvo: ref(alvo), valor: d, perda: antes - alvo.hp, crit, mult: m, hab, resta: alvo.hp, x: alvo.x, y: alvo.y, dx, hits, espelho: at.x > alvo.x, ...(apoio ? { apoio: true as const } : {}) });
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

function iniciarAtaque(L: Luta, u: Lutador, mira: [number, number], hab: boolean, apoio = false): void {
  u.estado = "attack"; u.t = 0; u.golpeDado = false; u.mira = mira; u.viraEsq = mira[0] < u.x; u.usandoHab = !!hab; u.nAtaque++;
  if (apoio) {
    /* o golpe de apoio (LP6-1): a recarga propria, contada do comeco, em vezes o ciclo do ataque */
    u.usandoApoio = true; u.recAp = L.cfg.apoio!.recarga * u.st.cad;
    evento(L, { tipo: "apoio", u: ref(u), perto: !u.ap!.proj, anim: u.ap!.anim, x: u.x, y: u.y });
  }
  if (hab) {
    u.recSk = u.st.hcd * 1000;
    evento(L, { tipo: "habilidade", u: ref(u), propria: u.propria, anim: u.sk.anim, x: u.x, y: u.y });
  }
}
/* o golpe em curso: o apoio (LP6-1), a habilidade ou o golpe. A esquiva (D-LP5-14) le por aqui: o apoio de perto e lido como o golpe de perto */
const dadosDe = (u: Lutador): GolpeBase => u.usandoApoio ? u.ap! : u.usandoHab ? u.sk : u.g;
const peito = (u: Lutador): [number, number] => [u.x, u.y - EQ.peito];

function soltarGolpe(L: Luta, u: Lutador): void {
  const o = u.alvo!, dados = dadosDe(u), hab = u.usandoHab;
  if (dados.proj) {
    const [px, py] = peito(u), sx = px + (u.viraEsq ? -1 : 1) * EQ.raio;
    const dx = u.mira![0] - sx, dy = u.mira![1] - py, d = dist(dx, dy) || 1;
    const vel = dados.proj.vel * PX_POR_UNIDADE * L.cfg.pvel * (L.cfg.tiro ? L.cfg.tiro.velProj : 1) * (def(L).projVel?.(L.cena) ?? 1);
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

/** a esquiva (D-LP5-14): o fator de um lutador pela perspicacia ou pela agilidade x (1 = o neutro), com o peso k; linear, sem `**` (a
    aritmetica do nucleo), e pelo menos 0,1 */
const fatorEsq = (x: number, k: number): number => Math.max(0.1, 1 + k * (x - 1));
/** a duracao do pulo da esquiva em ms, nos passos que ele anda (o dash conta o ACAO.desvioCpuMs de PASSO_MS em PASSO_MS) */
export const MS_DO_PULO = Math.ceil(ACAO.desvioCpuMs / PASSO_MS) * PASSO_MS;
function desviar(L: Luta, u: Lutador, dt: number): void {
  const cfg = dific(L), E = L.cfg.esquiva;
  /* a esquiva (D-LP5-14): a perspicacia sobe a chance e encurta a reacao; sem a `esquiva`, a da POC */
  const perc = E ? u.st.perc ?? 1 : 1, chance = E ? Math.min(E.chanceMax, cfg.desvio * fatorEsq(perc, E.kChance)) : cfg.desvio, reacao = E ? cfg.reacao / fatorEsq(perc, E.kReacao) : cfg.reacao;
  for (const p of L.projeteis) {
    if (p.de.lado === u.lado || p.decidido.has(u)) continue;
    const rx = u.x - p.x, ry = (u.y - EQ.peito) - p.y, vindo = rx * p.vx + ry * p.vy > 0;
    if (!vindo || dist(rx, ry) > 260) continue;
    p.decidido.add(u);
    if (L.r.ia() < chance) {
      const v = dist(p.vx, p.vy) || 1, lado = L.r.ia() < 0.5 ? 1 : -1;
      u.reacao = reacao; u.desvioDir = [-p.vy / v * lado, p.vx / v * lado];
    }
  }
  /* o golpe de perto do outro (D-LP5-14): lido uma vez por ataque, na preparacao e ao alcance; quem le pula para tras */
  const o = u.alvo;
  if (E && E.pertoChance > 0 && o && !o.morto && o.estado === "attack" && !o.golpeDado && !dadosDe(o).proj && u.leuAtaque !== o.nAtaque && u.reacao <= 0 && u.dash <= 0) {
    const ox = u.x - o.x, oy = u.y - o.y, od = dist(ox, oy) || 1;
    if (od <= EQ.alcanceCorpo + u.raio + EQ.investida) {
      u.leuAtaque = o.nAtaque;
      if (L.r.ia() < Math.min(E.chanceMax, E.pertoChance * fatorEsq(perc, E.kChance))) { u.reacao = E.pertoReacao / fatorEsq(perc, E.kReacao); u.desvioDir = [ox / od, oy / od]; u.contraPend = E.contraMs > 0; }
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
  if (u.ap) u.recAp -= dt;
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
    if (u.usandoApoio) {
      /* o fim do apoio (LP6-1): a recarga do golpe segue a dela, com o minimo de sempre */
      if (u.t >= u.msAp) {
        mudar(u, "idle"); u.recarga = Math.max(ACAO.recargaMin, u.recarga); u.usandoApoio = false;
        /* o atirador bate e recua (LP6-3, D-LP6-3-4), so com o `recua` do apoio (D-LP6-3-7): o recuo ate a distancia do tiro, no maximo a
           espera dele */
        if (!u.ap!.proj && L.cfg.apoio!.recua) u.recuoAp = L.cfg.tiro ? L.cfg.tiro.esperaMax : RECUO_APOIO_SEM_TIRO_MS;
      }
    } else if (u.t >= (u.usandoHab ? u.msSk : u.msAtk)) { mudar(u, "idle"); u.recarga = Math.max(ACAO.recargaMin, u.st.cad - u.msAtk); u.usandoHab = false; }
    return;
  }
  if (o.morto) { mudar(u, "idle"); return; }
  sorteioDaTroca(L, u);
  u.viraEsq = dx < 0;
  desviar(L, u, dt);
  if (u.dash > 0) {
    const Es = L.cfg.esquiva;
    const vPulo = Es ? ACAO.desvioCpu * fatorEsq(u.st.agil ?? 1, Es.kDash) : ACAO.desvioCpu;
    /* o teto do pulo (N3, a chave puloMax): a velocidade ate o teto / a duracao do pulo em passos; sem a chave, a de sempre */
    u.dash -= dt; andar(L, u, u.dashDir[0], u.dashDir[1], L.cfg.puloMax !== undefined ? Math.min(vPulo, L.cfg.puloMax * 1000 / MS_DO_PULO) : vPulo, dt); mudar(u, "run");
    if (Es && u.dash <= 0 && u.contraPend) { u.contraPend = false; u.recarga = Math.min(u.recarga, Es.contraMs); }
    return;
  }
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
  /* o recuo depois do apoio de perto (LP6-3, D-LP6-3-4): sem atacar, ate o alvo ficar na distancia do tiro (a mesma do apoio); se o tempo
     acaba antes (encurralado), a espera do tiro ja vale como cumprida e ele atira */
  let recuando = false;
  if (u.recuoAp > 0) {
    u.recuoAp -= dt;
    const lim = T && T.distMin > 0 ? T.distMin : u.alcance * (T ? T.recuaAbaixo : 0.5);
    if (d >= lim) u.recuoAp = 0;
    else if (u.recuoAp <= 0) { u.recuoAp = 0; if (T) u.esperaTiro = T.esperaMax; }
    else { recuando = true; u.esperaTiro = 0; }
  }
  let perto = false;
  if (!recuando) {
    if (T && T.distMin > 0 && (u.g.proj || u.sk.proj) && d < T.distMin) { u.esperaTiro += dt; perto = u.esperaTiro < T.esperaMax; } else u.esperaTiro = 0;
    if (u.recSk <= 0 && d <= alcHab + folga(u.sk.proj) && (livre || !u.sk.proj) && !(perto && u.sk.proj)) { iniciarAtaque(L, u, mira(), true); return; }
    /* o golpe de apoio (LP6-1), pela distancia e com a recarga propria */
    const ap = u.ap;
    if (ap && !ap.proj) {
      /* quem atira: o golpe de perto com o alvo abaixo da distMin do tiro (sem o `tiro`, a do recuo da POC) e ao alcance de perto. Sai
         durante a espera do tiro (D-LP5-12) e nao troca o recuo: o atirador bate e, de volta ao idle, recua ate a distMin (D-LP6-3-4) */
      const limite = T && T.distMin > 0 ? T.distMin : u.alcance * (T ? T.recuaAbaixo : 0.5);
      if (u.recAp <= 0 && d < limite && d <= EQ.alcanceCorpo + folga(null)) { iniciarAtaque(L, u, mira(), false, true); return; }
    } else if (ap) {
      /* quem bate de perto: o tiro fraco quando o alvo fica alem do alcance de perto por um tempo (ele foge ou se esconde), ao alcance do
         tiro e sem arvore ou rocha no caminho */
      if (d > u.alcance + folga(u.g.proj)) u.longeMs += dt; else u.longeMs = 0;
      if (u.recAp <= 0 && u.longeMs >= L.cfg.apoio!.longeMs && d <= ACAO.alcanceDist && livre) { u.longeMs = 0; iniciarAtaque(L, u, mira(), false, true); return; }
    }
    if (d <= u.alcance + folga(u.g.proj) && u.recarga <= 0 && (livre || !u.g.proj) && !(perto && u.g.proj)) { iniciarAtaque(L, u, mira(), false); return; }
  }
  let mx = 0, my = 0;
  if (recuando) { u.ladoDesvio = 0; mx = -dx / d; my = -dy / d; }
  else if (!livre) {
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
    /* o tiro de quem caiu (N3, a chave tiroDoMorto): some no ar, sem dano; sem a chave, ele segue e ainda acerta */
    if (L.cfg.tiroDoMorto && pr.de.morto) { pr.fim = true; evento(L, { tipo: "tiro_errou", u: ref(pr.de) }); continue; }
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
      else if (pr.resta <= 0 || !dentroArena(L, pr.x, pr.y + 30)) { pr.fim = true; evento(L, { tipo: "tiro_errou", u: ref(pr.de) }); }
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
