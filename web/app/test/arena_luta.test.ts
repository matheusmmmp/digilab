// A luta da POC no motor (docs/TAREFA_V3_LUTA_POC.md, LP1): o replay bit a bit (a mesma semente da a mesma luta, evento a evento e ate a
// posicao final), os fluxos de sorteio separados, os 8 mapas da POC ate o fim, a entrada que falha alto e a fidelidade contra a POC
// (test/gabaritos/arena_poc_1x1.json, gravado por scripts/arena_fidelidade.ts a partir do porte do efb2ded).
import { expect, test } from "vitest";
import { readFileSync } from "node:fs";
import {
  CENAS, ERRO_MIRA_POC, FORMAS_ARENA, IDS_CENA, LIMITE_MS, configLuta, criarLuta, formaArena, lutar, passo, rodarAteOFim, sementeArena, sorteiosPorFluxo,
  type EntradaLuta, type Evento, type IdCena, type Luta, type Sorteios, type Stats,
} from "../motor/arena/index.ts";
import { DIGIMON_DA_FORMA, LUGARES_V6, NPC } from "../motor/index.ts";

const ST: Stats = { hp: 900, atk: 100, def: 50, vel: 70, cad: 2000, crit: 10, hcd: 8, hpot: 2, esquiva: 0, atordoa: 0, erro: 18 };
const entrada = (cena: IdCena, semente: number, a = "cirro_crianca_arisco", b = "brasa_crianca_sereno", sa: Stats = ST, sb: Stats = ST): EntradaLuta =>
  ({ cena, semente, a: { forma: a, stats: sa }, b: { forma: b, stats: sb } });

/** a luta inteira com todos os eventos e o estado final que importa (em todos os bits) */
function jogar(e: EntradaLuta, r: Sorteios = sorteiosPorFluxo(e.semente)) {
  const L = criarLuta(configLuta(e), r), ev: Evento[] = [];
  const res = rodarAteOFim(L, x => { ev.push(...x); });
  const fim = (L: Luta) => [L.a, L.b].map(u => [u.hp, u.x, u.y, u.estado, u.recarga, u.recSk, u.dano, u.golpes]);
  return { ev, res, fim: fim(L) };
}

test("a tabela tem as 60 formas do jogo, com o Digimon do catalogo, e os 10 rivais da Campanha (LP2)", () => {
  const npcs = LUGARES_V6.flatMap(L => L.rivais);
  expect(Object.keys(FORMAS_ARENA).sort()).toEqual([...Object.keys(DIGIMON_DA_FORMA), ...npcs].sort());
  for (const [k, f] of Object.entries(FORMAS_ARENA)) {
    expect(f.nome, k).toBe(DIGIMON_DA_FORMA[k]?.[0] ?? NPC[k]!.nome);
    expect(f.msGolpe, k).toBeGreaterThan(0);
    expect(f.golpe.t, k).toBeGreaterThan(0);
  }
  /* o Gabumon nao tem projetil nos dados do jogo (a LP-8 e da LP3); o Agumon tem */
  expect(FORMAS_ARENA.cirro_crianca_arisco.golpe.proj).toBeNull();
  expect(FORMAS_ARENA.brasa_crianca_sereno.golpe.proj?.vel).toBe(30);
  expect(() => formaArena("ninguem")).toThrow(/ninguem/);
});

test("replay bit a bit: a mesma entrada da a mesma luta, nos 8 mapas; outra semente, outra luta", () => {
  for (const id of IDS_CENA) {
    const a = jogar(entrada(id, 101)), b = jogar(entrada(id, 101));
    expect(a.ev.length, id).toBeGreaterThan(10);
    expect(b).toEqual(a);
    expect(Object.is(a.fim[0][1], b.fim[0][1])).toBe(true);
  }
  expect(jogar(entrada("caverna", 202)).ev).not.toEqual(jogar(entrada("caverna", 303)).ev);
});

test("os 8 mapas da POC rodam ate o fim, cada um com a regra dele aparecendo", () => {
  expect(IDS_CENA).toEqual(["campo", "coliseu", "floresta", "praia", "deserto", "castelo", "caverna", "ringue"]);
  /* o Gabumon (corpo a corpo) contra o Agumon (projetil), os dois tanques, para a luta durar e as regras de tempo (o Coliseu aos 30 s,
     a tempestade aos 12 s) aparecerem */
  const tanque: Stats = { ...ST, hp: 6000, atk: 60 };
  const regra: Record<IdCena, (ev: Evento[]) => boolean> = {
    campo: () => true,
    coliseu: ev => ev.some(e => e.tipo === "arena_fecha"),
    floresta: ev => ev.some(e => e.tipo === "tiro_bloqueado"),
    praia: () => true,
    deserto: ev => ev.some(e => e.tipo === "tempestade"),
    castelo: ev => ev.some(e => e.tipo === "pilar" || e.tipo === "runa"),
    caverna: ev => ev.some(e => e.tipo === "ambiente"),
    ringue: ev => ev.some(e => e.tipo === "queda_ringue"),
  };
  for (const id of IDS_CENA) {
    expect(CENAS[id].nome.length, id).toBeGreaterThan(3);
    const { ev, res } = jogar(entrada(id, 404, "cirro_crianca_arisco", "brasa_crianca_sereno", tanque, tanque));
    expect(res.fim, id).toBe(true);
    expect(res.relogio, id).toBeLessThan(LIMITE_MS);
    expect(ev.at(-1)?.tipo, id).toBe("fim");
    expect(regra[id](ev), id).toBe(true);
  }
});

test("fluxos: cada uso tem a sua semente; o fluxo visual so mexe no deslocamento do numero de dano", () => {
  const sementes = ["ia", "combate", "cena", "visual"].map(f => sementeArena(101, f));
  expect(new Set(sementes).size).toBe(4);
  const e = entrada("castelo", 404);
  const a = jogar(e), b = jogar(e, { ...sorteiosPorFluxo(404), visual: () => 0.5 });
  const semDx = (ev: Evento[]) => ev.map(x => x.tipo === "dano" ? { ...x, dx: 0 } : x);
  expect(semDx(b.ev)).toEqual(semDx(a.ev));
  expect(b.fim).toEqual(a.fim);
});

test("a entrada falha alto: stat que nao e numero, vida menor que 1, mapa desconhecido", () => {
  expect(() => lutar(entrada("campo", 1, undefined, undefined, { ...ST, atk: Number.NaN }))).toThrow(/atk/);
  expect(() => lutar(entrada("campo", 1, undefined, undefined, { ...ST, hp: 0 }))).toThrow(/vida/);
  expect(() => lutar(entrada("lua" as IdCena, 1))).toThrow(/mapa/);
  expect(() => criarLuta({ ...configLuta(entrada("campo", 1)), dific: "impossivel" as never }, sorteiosPorFluxo(1))).toThrow(/dificuldade/);
});

test("passo devolve e limpa os eventos; a luta comeca pelo evento de inicio", () => {
  const L = criarLuta(configLuta(entrada("campo", 7)), sorteiosPorFluxo(7));
  expect(L.eventos).toEqual([{ tipo: "inicio", a: "Gabumon", b: "Agumon" }]);
  L.eventos = [];
  passo(L);
  expect(L.eventos).toEqual([]);
});

interface LutaGab { cena: IdCena; a: string; b: string; semente: number; vencedor: "a" | "b" | null; fim: boolean; relogio: number; vidaA: number; vidaB: number }
test("fidelidade: o nucleo novo da o mesmo resultado que a POC (efb2ded) 1 contra 1 nas 60 formas e nos 8 mapas", () => {
  const gab = JSON.parse(readFileSync(new URL("./gabaritos/arena_poc_1x1.json", import.meta.url), "utf8")) as { stats: Omit<Stats, "erro">; lutas: LutaGab[] };
  /* o gabarito e da POC, em que o erro de mira era o da dificuldade "normal" (18 px); desde a LP2 ele e do lutador */
  const st: Stats = { ...gab.stats, erro: ERRO_MIRA_POC.normal };
  expect(gab.lutas.length).toBe(480);
  const dif: string[] = [];
  for (const g of gab.lutas) {
    const r = lutar(entrada(g.cena, g.semente, g.a, g.b, st, st));
    const obtido = { vencedor: r.vencedor, fim: r.fim, relogio: r.relogio, vidaA: r.vidaA, vidaB: r.vidaB };
    const esperado = { vencedor: g.vencedor, fim: g.fim, relogio: g.relogio, vidaA: g.vidaA, vidaB: g.vidaB };
    if (JSON.stringify(obtido) !== JSON.stringify(esperado)) dif.push(`${g.cena} ${g.a} x ${g.b} (${g.semente}): ${JSON.stringify(esperado)} -> ${JSON.stringify(obtido)}`);
  }
  /* scripts/arena_fidelidade.ts mediu, nos dados do jogo e no harness inteiro: o mesmo resultado em 3276 de 3276 lutas; a aritmetica muda
     so os ultimos bits das posicoes. Se este teste falhar, rode o script e registre a diferenca em distribuicao antes de mexer aqui */
  expect(dif).toEqual([]);
});
