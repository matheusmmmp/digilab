// A LP6-3 (docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 8; o desvio D-LP6-3-4; "Regra e grade", Matheus, 2026-11-11): o atirador bate e recua.
// Depois do apoio de perto, quem atira recua sem atacar ate o alvo ficar na distMin do tiro, no maximo pela espera do tiro; se o tempo acaba
// antes (encurralado), a espera ja vale como cumprida e ele atira. Com as chaves desligadas, nada muda (arena_lp6_gabarito.test.ts).
import { expect, test } from "vitest";
import { APOIO_LP6, IDS_CENA, PASSO_MS, RECUO_APOIO_SEM_TIRO_MS, configLuta, criarLuta, dist, passo, sorteiosPorFluxo, type EntradaLuta, type Evento, type IdCena, type Luta, type Sorteios, type Stats } from "../motor/arena/index.ts";
import { LUTA_V23 } from "../motor/luta_poc.ts";

const ST: Stats = { hp: 900, atk: 100, def: 50, vel: 70, cad: 2000, crit: 0, hcd: 8, hpot: 2, esquiva: 0, atordoa: 0, erro: 18 };
const TIRO = LUTA_V23.tiro!;
const FIXO: Sorteios = { ia: () => 0.5, combate: () => 0.5, cena: () => 0.5, visual: () => 0.5 };
const AGUMON = "brasa_crianca_sereno", VEEMON = "ferrugem_crianca_arisco";
const entrada = (cena: IdCena, a: string, b: string, extra: Partial<EntradaLuta> = {}, semente = 101): EntradaLuta =>
  ({ cena, semente, a: { forma: a, stats: ST }, b: { forma: b, stats: ST }, tiro: TIRO, apoio: APOIO_LP6, ...extra });
const d = (L: Luta) => dist(L.b.x - L.a.x, L.b.y - L.a.y);

/** roda a luta e confere cada recuo de A depois do apoio de perto; devolve quantos recuos houve e quantos passos de recuo */
function conferirRecuos(L: Luta): { recuos: number; passos: number; afasta: number } {
  /* `afasta`: a soma, nos passos de recuo, do deslocamento de A na direcao do alvo (negativa: para longe). Passo a passo, a borda da elipse,
     os obstaculos e a guia do mapa podem desviar o rumo; a soma confere a direcao do recuo */
  let recuos = 0, passos = 0, usava = false, afasta = 0;
  while (!L.fim && L.relogio < 120_000) {
    const antes = { rec: L.a.recuoAp, ax: L.a.x, ay: L.a.y, bx: L.b.x, by: L.b.y, d: d(L), estado: L.a.estado };
    const ev: Evento[] = passo(L);
    /* o fim do apoio de perto liga o recuo pela espera do tiro */
    if (usava && !L.a.usandoApoio && L.a.estado !== "attack") { expect(L.a.recuoAp).toBe(TIRO.esperaMax); recuos++; }
    /* num passo de recuo (que nao terminou), A nao comeca ataque nenhum e anda para longe do alvo */
    if (antes.rec > 0 && L.a.recuoAp > 0 && antes.estado === "idle" || antes.rec > 0 && L.a.recuoAp > 0 && antes.estado === "run") {
      passos++;
      for (const e of ev) if ((e.tipo === "apoio" || e.tipo === "habilidade") && e.u.lado === "a") throw new Error(`atacou no recuo: ${e.tipo}`);
      expect(L.a.estado === "attack" && L.a.t <= PASSO_MS).toBe(false);
      if (L.a.estado === "run" && L.a.dash <= 0) afasta += ((L.a.x - antes.ax) * (antes.bx - antes.ax) + (L.a.y - antes.ay) * (antes.by - antes.ay)) / (antes.d || 1);
    }
    usava = L.a.usandoApoio;
  }
  return { recuos, passos, afasta };
}

test("depois do apoio de perto, quem atira recua sem atacar, para longe do alvo (sorteios fixos e de verdade, 8 mapas)", () => {
  const c = conferirRecuos(criarLuta(configLuta(entrada("campo", AGUMON, VEEMON)), FIXO));
  expect(c.recuos).toBeGreaterThan(0);
  expect(c.passos).toBeGreaterThan(0);
  expect(c.afasta).toBeLessThan(0);
  let recuos = 0, afasta = 0;
  for (const cena of IDS_CENA) for (const s of [101, 202]) { const r = conferirRecuos(criarLuta(configLuta(entrada(cena, AGUMON, VEEMON, {}, s)), sorteiosPorFluxo(s))); recuos += r.recuos; afasta += r.afasta; }
  expect(recuos).toBeGreaterThan(0);
  expect(afasta).toBeLessThan(0);
});

test("o recuo acaba na distMin do tiro; encurralado, acaba pelo tempo e a espera do tiro vale como cumprida", () => {
  const L = criarLuta(configLuta(entrada("campo", AGUMON, VEEMON)), FIXO);
  /* longe: o recuo acaba no primeiro passo, e a espera do tiro nao muda */
  L.a.recuoAp = 500; L.a.x = L.b.x - (TIRO.distMin + 20); L.a.y = L.b.y;
  passo(L);
  expect(L.a.recuoAp).toBe(0);
  /* perto e no ultimo passo do tempo: acaba pelo tempo, e a espera do tiro fica cumprida */
  const M = criarLuta(configLuta(entrada("campo", AGUMON, VEEMON)), FIXO);
  M.a.recuoAp = PASSO_MS; M.a.x = M.b.x - 40; M.a.y = M.b.y; M.a.recarga = 99_999;
  passo(M);
  expect(M.a.recuoAp).toBe(0);
  expect(M.a.esperaTiro).toBeGreaterThanOrEqual(TIRO.esperaMax);
  /* perto e com tempo: recua, e a espera do tiro recomeca do zero */
  const N = criarLuta(configLuta(entrada("campo", AGUMON, VEEMON)), FIXO);
  N.a.recuoAp = 1000; N.a.x = N.b.x - 40; N.a.y = N.b.y; N.a.esperaTiro = 1400;
  passo(N);
  expect(N.a.recuoAp).toBe(1000 - PASSO_MS);
  expect(N.a.esperaTiro).toBe(0);
  expect(N.a.estado).not.toBe("attack");
});

test("so quem atira recua pelo apoio; o tiro fraco de quem bate de perto nao; sem o `tiro`, o recuo dura o RECUO_APOIO_SEM_TIRO_MS", () => {
  const L = criarLuta(configLuta(entrada("campo", VEEMON, AGUMON)), FIXO);
  let apoiosA = 0;
  while (!L.fim && L.relogio < 120_000) { for (const e of passo(L)) if (e.tipo === "apoio" && e.u.lado === "a") { expect(e.perto).toBe(false); apoiosA++; } expect(L.a.recuoAp).toBe(0); }
  expect(apoiosA).toBeGreaterThan(0);
  const { tiro: _t, ...semTiro } = entrada("campo", AGUMON, VEEMON);
  const M = criarLuta(configLuta(semTiro as EntradaLuta), FIXO);
  let visto = false, usava = false;
  while (!M.fim && M.relogio < 120_000 && !visto) { passo(M); if (usava && !M.a.usandoApoio && M.a.estado !== "attack") { expect(M.a.recuoAp).toBe(RECUO_APOIO_SEM_TIRO_MS); visto = true; } usava = M.a.usandoApoio; }
  expect(visto).toBe(true);
});

test("com as chaves desligadas, o recuo do apoio nunca liga", () => {
  const { apoio: _a, ...sem } = entrada("campo", AGUMON, VEEMON);
  const L = criarLuta(configLuta(sem as EntradaLuta), sorteiosPorFluxo(101));
  while (!L.fim && L.relogio < 120_000) { passo(L); expect(L.a.recuoAp).toBe(0); expect(L.b.recuoAp).toBe(0); }
});
