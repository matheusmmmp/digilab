// A LP6-1 (docs/PLANO_LP6_SEGUNDO_GOLPE.md): o golpe de apoio e a elipse por estagio no nucleo da luta, cada um atras da sua chave da
// entrada. Aqui: a tabela das formas (o apoio gerado, do tipo que falta), o replay bit a bit com as chaves ligadas, cada regra do apoio
// (quando sai, a recarga, o dano, o recuo, a esquiva, o tiro fraco) e a escala da elipse. A luta com as chaves desligadas igual a de antes
// fica em arena_lp6_gabarito.test.ts.
import { expect, test } from "vitest";
import { readFileSync } from "node:fs";
import {
  ACAO, APOIO_LP6, APOIO_TABELA, ARENA_POR_ESTAGIO_LP6, CENAS, ELIPSE, EQ, FORMAS_ARENA, IDS_CENA, PASSO_MS, configLuta, conferirApoio,
  conferirArenaPorEstagio, criarLuta, dist, fatorElipse, iniciarCena, passo, rodarAteOFim, sorteiosPorFluxo,
  type EntradaLuta, type Evento, type IdCena, type Luta, type Sorteios, type Stats,
} from "../motor/arena/index.ts";
import { LUTA_V23, esquivaDaTabela, statsRivalArena } from "../motor/luta_poc.ts";
import { lutasDoGabaritoLp6, resumoLutaLp6 } from "./arena_lp6_lutas.ts";

const ST: Stats = { hp: 900, atk: 100, def: 50, vel: 70, cad: 2000, crit: 0, hcd: 8, hpot: 2, esquiva: 0, atordoa: 0, erro: 18 };
const TIRO = LUTA_V23.tiro!;
const SETE = ["limo_adolescente_guardiao", "limo_adulto_espelho", "npc_v5_myotismon", "npc_v5_machinedramon", "npc_v5_piedmon", "limo_adulto_emboscador", "npc_v5_puppetmon"];
/** sorteios fixos em 0,5: sem esquiva nem critico, a variacao do dano em 1, a mira sem erro e o desvio do tiro (0,45) nunca */
const FIXO: Sorteios = { ia: () => 0.5, combate: () => 0.5, cena: () => 0.5, visual: () => 0.5 };
const AGUMON = "brasa_crianca_sereno", VEEMON = "ferrugem_crianca_arisco";   // Vaccine x Free: sem vantagem de atributo

function entrada(cena: IdCena, a: string, b: string, extra: Partial<EntradaLuta> = {}, semente = 101): EntradaLuta {
  return { cena, semente, a: { forma: a, stats: ST }, b: { forma: b, stats: ST }, tiro: TIRO, apoio: APOIO_LP6, ...extra };
}
/** roda passo a passo, chamando `cada` com os eventos e a luta depois de cada passo */
function rodar(L: Luta, cada: (ev: Evento[], L: Luta) => void): void {
  cada(L.eventos, L); L.eventos = [];
  while (!L.fim && L.relogio < 120_000) cada(passo(L), L);
}
const d = (L: Luta) => dist(L.b.x - L.a.x, L.b.y - L.a.y);

test("a tabela: toda forma tem o golpe de apoio do tipo que falta, gerado pelo script (o instante, o clipe, o tiro de 20 e o fr do golpe)", () => {
  expect(Object.keys(FORMAS_ARENA).length).toBe(70);
  let atiram = 0, perto = 0;
  for (const [k, f] of Object.entries(FORMAS_ARENA)) {
    const ap = f.apoio!;
    expect(ap, k).toBeTruthy();
    expect(!ap.proj, k).toBe(!!f.golpe.proj);
    if (f.golpe.proj) atiram++; else { perto++; expect(ap.proj, k).toEqual({ prefab: null, vel: APOIO_TABELA.vel, tipo: "Guide" }); }
    expect(ap.anim, k).toBe(f.golpe.anim);
    expect(ap.t, k).toBe(f.golpe.t * APOIO_TABELA.ritmo);
    expect(ap.fr, k).toBe(f.golpe.fr);
    expect(ap.hits, k).toEqual([{ prefab: "Fx_Battle_Hit_A_Normal", atraso: 0 }]);
    expect(Math.abs(f.msApoio! - f.msGolpe * APOIO_TABELA.ritmo), k).toBeLessThanOrEqual(0.5);
    expect(Number.isInteger(f.msApoio), k).toBe(true);
  }
  expect(atiram + perto).toBe(70);
  /* os 7 com habilidade propria tambem ganham o apoio (decisao 2) */
  for (const k of SETE) { expect(FORMAS_ARENA[k].habilidade, k).not.toBeNull(); expect(FORMAS_ARENA[k].apoio, k).toBeTruthy(); }
  expect(Object.values(FORMAS_ARENA).filter(f => f.habilidade).length).toBe(7);
  /* o gerador usa os mesmos numeros do APOIO_TABELA */
  const py = readFileSync(new URL("../../../tools/gerar_tabela_arena.py", import.meta.url), "utf8");
  expect(Number(py.match(/^RITMO_APOIO = ([\d.]+)$/m)![1])).toBe(APOIO_TABELA.ritmo);
  expect(Number(py.match(/^VEL_APOIO = ([\d.]+)$/m)![1])).toBe(APOIO_TABELA.vel);
  expect(py).toMatch(/"apoio": ap, "msApoio": ms_ap/);
});

test("replay bit a bit com as duas chaves ligadas, nos 8 mapas; outra semente, outra luta; a v23 com as chaves muda a luta", () => {
  const T = LUTA_V23, esq = esquivaDaTabela(T)!;
  const e = (cena: IdCena, s: number): EntradaLuta => ({ cena, semente: s, a: { forma: "limo_adulto_emboscador", stats: statsRivalArena("limo_adulto_emboscador", T) },
    b: { forma: "brasa_adulto_furioso", stats: statsRivalArena("brasa_adulto_furioso", T) }, tiro: T.tiro!, esquiva: esq, apoio: APOIO_LP6, arenaPorEstagio: ARENA_POR_ESTAGIO_LP6 });
  for (const id of IDS_CENA) {
    const a = resumoLutaLp6(e(id, 101)), b = resumoLutaLp6(e(id, 101));
    expect(b, id).toEqual(a);
    expect(a.eventos, id).toBeGreaterThan(10);
  }
  expect(resumoLutaLp6(e("caverna", 202)).sha).not.toBe(resumoLutaLp6(e("caverna", 303)).sha);
  const sem = resumoLutaLp6({ ...e("campo", 101), apoio: undefined, arenaPorEstagio: undefined });
  expect(resumoLutaLp6(e("campo", 101)).sha).not.toBe(sem.sha);
});

test("so a elipse ligada, com o maior estagio ate o Champion (fator 1): a luta e byte a byte a do gabarito", () => {
  const gab = JSON.parse(readFileSync(new URL("./gabaritos/arena_lp6_v23.json", import.meta.url), "utf8")) as { lutas: { id: string; sha: string }[] };
  const sha = new Map(gab.lutas.map(l => [l.id, l.sha]));
  let n = 0;
  for (const l of lutasDoGabaritoLp6()) {
    const f = fatorElipse(FORMAS_ARENA[l.entrada.a.forma], FORMAS_ARENA[l.entrada.b.forma], ARENA_POR_ESTAGIO_LP6);
    if (f !== 1) continue;
    n++;
    expect(resumoLutaLp6({ ...l.entrada, arenaPorEstagio: ARENA_POR_ESTAGIO_LP6 }).sha, l.id).toBe(sha.get(l.id));
  }
  expect(n).toBeGreaterThan(100);
});

test("o apoio de perto de quem atira: sai abaixo da distMin e ao alcance de perto, na espera do tiro; recarga propria; 0,6 do dano", () => {
  const L = criarLuta(configLuta(entrada("campo", AGUMON, VEEMON)), FIXO);
  expect(L.a.ap?.proj).toBeNull();
  const inicios: { t: number; d: number; espera: number }[] = [], danos: Evento[] = [];
  let antes = { d: d(L), espera: 0 };
  rodar(L, (ev, L2) => {
    for (const e of ev) {
      if (e.tipo === "apoio" && e.u.lado === "a") { expect(e.perto).toBe(true); inicios.push({ t: L2.relogio, d: antes.d, espera: L2.a.esperaTiro }); }
      if (e.tipo === "dano" && e.at.lado === "a") danos.push(e);
    }
    antes = { d: d(L2), espera: L2.a.esperaTiro };
  });
  expect(inicios.length).toBeGreaterThan(1);
  for (const i of inicios) {
    expect(i.d).toBeLessThan(TIRO.distMin);
    expect(i.d).toBeLessThanOrEqual(EQ.alcanceCorpo + EQ.raio * 0.8 + EQ.investida * 0.8 + 3);   // o alcance de perto, com o passo de folga
    expect(i.espera).toBeGreaterThan(0);   // na espera do tiro (D-LP5-12): interrompe a espera
  }
  /* a recarga propria: 2 vezes o ciclo do ataque entre dois apoios */
  for (let k = 1; k < inicios.length; k++) expect(inicios[k].t - inicios[k - 1].t).toBeGreaterThanOrEqual(APOIO_LP6.recarga * ST.cad);
  /* o dano: o do golpe principal (o tiro: danoProj do `tiro` e o fr do golpe) vezes 0,6; com os sorteios fixos, sem variacao nem critico */
  const g = FORMAS_ARENA[AGUMON].golpe, base = ST.atk * (100 / (100 + ST.def)) * 1 * 1 * 1 * 1 * 1;
  const comApoio = danos.filter(e => e.tipo === "dano" && e.apoio), semApoio = danos.filter(e => e.tipo === "dano" && !e.apoio && !e.hab);
  expect(comApoio.length).toBeGreaterThan(0);
  for (const e of comApoio) if (e.tipo === "dano") expect(e.valor).toBe(Math.max(1, Math.round(base * TIRO.danoProj * g.fr * APOIO_LP6.dano)));
  for (const e of semApoio) if (e.tipo === "dano") { expect(e.valor).toBe(Math.max(1, Math.round(base * TIRO.danoProj * g.fr))); expect("apoio" in e).toBe(false); }
});

test("o apoio de perto nao troca o recuo: de volta ao idle, com o alvo perto, quem atira se afasta", () => {
  const L = criarLuta(configLuta(entrada("campo", AGUMON, VEEMON)), FIXO);
  let fimApoio = 0, conferidos = 0, antes: [number, number, number, number] = [L.a.x, L.a.y, L.b.x, L.b.y], usava = false;
  rodar(L, (_ev, L2) => {
    if (usava && !L2.a.usandoApoio) fimApoio = L2.relogio;
    /* o primeiro passo andando depois do apoio, com o alvo abaixo da distMin e nenhum dos dois atacando nem pulando */
    if (fimApoio && L2.relogio === fimApoio + PASSO_MS && L2.a.estado === "run" && L2.a.dash <= 0 && L2.b.estado !== "attack") {
      const [ax, ay, bx, by] = antes, dd = dist(bx - ax, by - ay);
      if (dd < TIRO.distMin) { expect((L2.a.x - ax) * (bx - ax) + (L2.a.y - ay) * (by - ay)).toBeLessThan(0); conferidos++; }
    }
    usava = L2.a.usandoApoio; antes = [L2.a.x, L2.a.y, L2.b.x, L2.b.y];
  });
  expect(conferidos).toBeGreaterThan(0);
});

test("a esquiva (D-LP5-14) le o apoio de perto como le o golpe de perto", () => {
  const esquiva = { kChance: 0, kReacao: 0, kDash: 0, chanceMax: 1, pertoChance: 1, pertoReacao: 100, contraMs: 0 };
  /* quem le pula para tras (a reacao e o pulo); um lutador ocupado (atacando, atordoado ou ja pulando) nao le, como no golpe de perto */
  /* nos 8 mapas: com o recuo depois do apoio (D-LP6-3-4), a luta fixa do campo nao tem um apoio que o outro esteja livre para ler */
  const lidosCom = (pertoChance: number) => {
    let lidos = 0, apoios = 0;
    for (const cena of IDS_CENA) {
      const L = criarLuta(configLuta(entrada(cena, AGUMON, VEEMON, { esquiva: { ...esquiva, pertoChance } })), FIXO);
      let nAp = -1;
      rodar(L, (ev, L2) => {
        for (const e of ev) if (e.tipo === "apoio" && e.u.lado === "a") { apoios++; nAp = L2.a.nAtaque; }
        if (nAp >= 0 && L2.b.leuAtaque === nAp) {
          /* lido na preparacao do apoio, e o pulo vem da leitura */
          expect(L2.a.usandoApoio && !L2.a.golpeDado).toBe(true);
          if (pertoChance > 0) expect(L2.b.reacao > 0 || L2.b.dash > 0).toBe(true);
          lidos++; nAp = -1;
        }
      });
    }
    return { lidos, apoios };
  };
  const com = lidosCom(1);
  expect(com.apoios).toBeGreaterThan(0);
  expect(com.lidos).toBeGreaterThan(0);
  expect(com.lidos).toBeLessThanOrEqual(com.apoios);
  expect(lidosCom(0).lidos).toBe(0);
  /* sem a chave do apoio, a mesma luta nao tem o evento */
  const sem = criarLuta(configLuta({ ...entrada("campo", AGUMON, VEEMON, { esquiva }), apoio: undefined }), FIXO);
  let algum = false; rodar(sem, ev => { if (ev.some(e => e.tipo === "apoio")) algum = true; });
  expect(algum).toBe(false);
});

test("o tiro fraco de quem bate de perto: sai com o alvo alem do alcance por longeMs, a 20 do Guide, com 0,6 do dano de perto", () => {
  const L = criarLuta(configLuta(entrada("campo", AGUMON, VEEMON)), FIXO);
  expect(L.b.ap?.proj?.vel).toBe(APOIO_TABELA.vel);
  const alcanceB = L.b.alcance + L.a.raio * 0.8 + EQ.investida * 0.8;
  let longe = 0, tiros = 0, voos = 0;
  const danos: number[] = [];
  rodar(L, (ev, L2) => {
    for (const e of ev) {
      if (e.tipo === "apoio" && e.u.lado === "b") {
        expect(e.perto).toBe(false); tiros++;
        expect(longe).toBeGreaterThanOrEqual(APOIO_LP6.longeMs - PASSO_MS);   // o alvo ficou alem do alcance pelo tempo todo
        expect(d(L2)).toBeLessThanOrEqual(ACAO.alcanceDist + 5);
      }
      if (e.tipo === "dano" && e.at.lado === "b" && e.apoio) danos.push(e.valor);
    }
    if (L2.projeteis.some(p => p.de === L2.b && p.dados === L2.b.ap && p.t === PASSO_MS)) voos++;
    longe = d(L2) > alcanceB ? longe + PASSO_MS : 0;
  });
  expect(tiros).toBeGreaterThan(0);
  expect(voos).toBe(tiros);
  /* o dano: o tipo do golpe principal (de perto: EQ.danoCorpo) e o fr dele, vezes 0,6 */
  const g = FORMAS_ARENA[VEEMON].golpe, esperado = Math.max(1, Math.round(ST.atk * (100 / (100 + ST.def)) * EQ.danoCorpo * g.fr * APOIO_LP6.dano));
  expect(danos.length).toBeGreaterThan(0);
  for (const v of danos) expect(v).toBe(esperado);
});

test("a chave do apoio com uma forma sem apoio, ou numeros fora da faixa, falha alto", () => {
  const f = { ...FORMAS_ARENA[AGUMON] }; delete (f as { apoio?: unknown }).apoio;
  const cfg = configLuta(entrada("campo", AGUMON, VEEMON));
  expect(() => criarLuta({ ...cfg, a: { ...cfg.a, forma: f } }, FIXO)).toThrow(/apoio/);
  expect(() => conferirApoio({ dano: 0, recarga: 2, longeMs: 1500 })).toThrow(/apoio/);
  expect(() => conferirApoio({ dano: 0.6, recarga: Number.NaN, longeMs: 1500 })).toThrow(/apoio/);
  expect(() => conferirArenaPorEstagio({ Ultimate: 1.3, Mega: 1.15 })).toThrow(/elipse/);
  expect(() => conferirArenaPorEstagio({ Ultimate: 0.9, Mega: 1.3 })).toThrow(/elipse/);
  expect(() => iniciarCena("campo", 0.5)).toThrow(/fator/);
});

test("a elipse por estagio: o fator pelo maior dos dois, e as zonas, os obstaculos, a area segura, a mare e o inicio escalam; os corpos nao", () => {
  const F = ARENA_POR_ESTAGIO_LP6, fe = (a: string, b: string) => fatorElipse(FORMAS_ARENA[a], FORMAS_ARENA[b], F);
  expect(fe("brasa_bebe", AGUMON)).toBe(1);
  expect(fe(AGUMON, "brasa_adolescente_brigao")).toBe(1);
  expect(fe("brasa_adulto_duelista", AGUMON)).toBe(1.15);
  expect(fe(AGUMON, "brasa_adulto_furioso")).toBe(1.3);
  expect(fe("npc_v5_myotismon", "npc_v5_piedmon")).toBe(1.3);
  expect(() => fatorElipse({ ...FORMAS_ARENA[AGUMON], estagio: "Armor" }, FORMAS_ARENA[AGUMON], F)).toThrow(/estagio/);

  const MEGA = "brasa_adulto_furioso", e = (cena: IdCena) => entrada(cena, MEGA, "limo_adulto_furioso", { arenaPorEstagio: F, apoio: undefined });
  for (const id of IDS_CENA) {
    const L = criarLuta(configLuta(e(id)), sorteiosPorFluxo(101)), k = F.Mega;
    expect(L.esc, id).toBe(k);
    expect(L.el, id).toEqual({ cx: ELIPSE.cx, cy: ELIPSE.cy, rx: ELIPSE.rx * k, ry: ELIPSE.ry * k });
    /* os pontos de inicio */
    expect([L.a.x, L.b.x], id).toEqual([ELIPSE.cx - ACAO.entradaX * k, ELIPSE.cx + ACAO.entradaX * k]);
    /* os obstaculos e as zonas, pelo centro da elipse */
    const c = CENAS[id];
    (c.obst ?? []).forEach(([x, y, r], i) => expect(L.cena.obst[i], id).toMatchObject({ x: ELIPSE.cx + (x - ELIPSE.cx) * k, y: ELIPSE.cy + (y - ELIPSE.cy) * k, r: r * k }));
    (c.zonas ?? []).forEach(([, x, y, rx, ry], i) => expect(L.cena.zonas[i], id).toMatchObject({ x: ELIPSE.cx + (x - ELIPSE.cx) * k, y: ELIPSE.cy + (y - ELIPSE.cy) * k, rx: rx * k, ry: ry * k }));
    /* os corpos, o alcance e a velocidade nao mudam */
    expect([L.a.raio, L.b.raio, L.a.alcance, L.b.alcance, L.a.st.vel], id).toEqual([EQ.raio, EQ.raio, ACAO.alcanceDist, EQ.alcanceCorpo, ST.vel]);
    const res = rodarAteOFim(L);
    expect(res.relogio, id).toBeGreaterThan(0);
  }
  /* a mare: a linha da agua escala pela elipse (a mesma fase, no relogio 0) */
  const P = criarLuta(configLuta(e("praia")), sorteiosPorFluxo(101)), P1 = criarLuta(configLuta({ ...e("praia"), arenaPorEstagio: undefined }), sorteiosPorFluxo(101));
  passo(P); passo(P1);
  expect(P.cena.linha - P.el.cy).toBeCloseTo((P1.cena.linha - ELIPSE.cy) * F.Mega, 9);
  /* a area segura do Coliseu e a cerca seguem a elipse maior: um lutador a 1,2 rx do centro esta dentro da arena nova */
  const C = criarLuta(configLuta(e("coliseu")), sorteiosPorFluxo(101));
  C.a.x = ELIPSE.cx + ELIPSE.rx * 1.2 - 20; C.a.y = ELIPSE.cy;
  const xAntes = C.a.x; passo(C);
  expect(Math.abs(C.a.x - xAntes)).toBeLessThan(5);   // a cerca nao puxa de volta (na elipse de sempre puxaria para 430)
  const C1 = criarLuta(configLuta({ ...e("coliseu"), arenaPorEstagio: undefined }), sorteiosPorFluxo(101));
  C1.a.x = ELIPSE.cx + ELIPSE.rx * 1.2 - 20; C1.a.y = ELIPSE.cy; passo(C1);
  expect(C1.a.x).toBeLessThanOrEqual(ELIPSE.cx + ELIPSE.rx - 20 + 1e-9);
});
