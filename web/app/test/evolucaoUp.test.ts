// A cena oficial de evolucao (TAREFA_V2_UP_EVOLUCAO): o mapa forma -> cena, a sequencia Summon + revelacao, o pet no osso e o clipe
// Evol que segue no Idle, com dados sinteticos (sem quadro nem PNG da Bandai).
import { expect, test } from "vitest";
import type { AtlasOk, SpriteUp } from "../src/atlas.ts";
import {
  CENA_EVOLUCAO_UP, centroDoCorpo, escolherCena, lugarDigimon, quadroDigimon, sequencia, type MapaEvolucao, type QuadroCena,
} from "../src/evolucaoUp.ts";

const q = (digimon: QuadroCena["digimon"], clipe: QuadroCena["clipe"], clipe_ms: number | null, camadas = ["bk"]): QuadroCena =>
  ({ camadas, pedacos: camadas.map((_, i) => [i * 10, 10] as [number, number]), osso: [0, 0, 1, 1], digimon, clipe, clipe_ms });
const mapa = (): MapaEvolucao => ({
  versao: 1, w: 650, h: 500, fps: 30, camera: [1300, 1000], escala_digimon: 4.2,
  cenas: {
    adventure: { quadros: [q(null, null, null), q("antes", "Idle", 0, ["bk", "t01a"])], revela_s: 1 },
    zero2: { quadros: [q(null, null, null)], revela_s: 1 }, tamers: { quadros: [q(null, null, null)], revela_s: 1 },
    tamers_mega: { quadros: [q("antes", "Idle", 500)], revela_s: 1 }, jogress: { quadros: [q(null, null, null)], revela_s: 1 },
    dramon: { quadros: [q(null, null, null)], revela_s: 1 },
  },
  revelacao: { quadros: [q("herda", null, null), q("herda", null, null), q("depois", "Evol", 0, ["bk", "t00n", "t03a"])] },
  formas: { forma_a: { digimon: "Agumon", cena: "adventure", bgm: "4002" }, forma_m: { digimon: "Gallantmon", cena: "tamers_mega", bgm: "4005" } },
  sem_cena: [{ forma: "forma_s", digimon: "Seadramon", evol: false }],
});

test("a chave nasce desligada", () => {
  expect(CENA_EVOLUCAO_UP).toBe(false);
});

test("escolherCena: a cena e a musica da linha; sem linha, o Evol do atlas; sem Evol, a Revelacao de hoje", () => {
  const m = mapa();
  expect(escolherCena(m, "forma_a", true)).toEqual({ tipo: "cena", cena: "adventure", bgm: "4002" });
  expect(escolherCena(m, "forma_m", false)).toEqual({ tipo: "cena", cena: "tamers_mega", bgm: "4005" });
  expect(escolherCena(m, "forma_x", true)).toEqual({ tipo: "evol" });
  expect(escolherCena(m, "forma_s", false)).toEqual({ tipo: "hoje" });
});

test("escolherCena: forma que pede cena inexistente falha alto", () => {
  const m = mapa();
  m.formas.forma_a.cena = "nenhuma" as never;
  expect(() => escolherCena(m, "forma_a", true)).toThrow(/nao existe/);
});

test("sequencia: a Summon, depois a revelacao; o 'herda' continua o Digimon e o clipe da Summon", () => {
  const s = sequencia(mapa(), "tamers_mega");
  expect(s.map(p => p.pacote)).toEqual(["tamers_mega", "revelacao", "revelacao", "revelacao"]);
  expect(s[3].pedacos).toEqual([[0, 10], [10, 10], [20, 10]]);
  expect(s.map(p => [p.digimon, p.clipe, p.clipe_ms])).toEqual([["antes", "Idle", 500], ["antes", "Idle", 533], ["antes", "Idle", 567], ["depois", "Evol", 0]]);
  expect(s[3].camadas).toEqual(["bk", "t00n", "t03a"]);
  const a = sequencia(mapa(), "zero2");
  expect(a[1].digimon).toBeNull();                       /* a Summon terminou sem Digimon: a revelacao herda o nada */
});

test("sequencia: 'herda' na Summon, cena vazia e camadas sem pedaco falham alto", () => {
  const m = mapa();
  m.revelacao.quadros[0].pedacos = [];
  expect(() => sequencia(m, "zero2")).toThrow(/nao casam/);
  m.revelacao.quadros[0].pedacos = [[0, 10]];
  m.cenas.zero2.quadros = [q("herda", null, null)];
  expect(() => sequencia(m, "zero2")).toThrow(/herda/);
  m.cenas.zero2.quadros = [];
  expect(() => sequencia(m, "zero2")).toThrow(/sem quadros/);
});

test("lugarDigimon: o centro do corpo no osso, na escala do osso (fora da escala inteira, decisao 3)", () => {
  const m = mapa();
  /* osso no centro da camera: (650, 500) em mundo -> (325, 250) em pixel; escala 4,2 * 1,2 * 0,5 = 2,52 */
  const l = lugarDigimon(m, [0, 0, 1.2, 1.2], [10, 20]);
  expect(l.escala).toBeCloseTo(2.52, 10);
  expect(l.x).toBeCloseTo(325 - 10 * 2.52, 10);
  expect(l.y).toBeCloseTo(250 - 20 * 2.52, 10);
  /* y para cima na camera, para baixo no pixel */
  expect(lugarDigimon(m, [100, -40, 1, 1], [0, 0])).toEqual({ x: 375, y: 270, escala: 2.1 });
});

const img = {} as HTMLImageElement, imgClipes = {} as HTMLImageElement;
const sprite: SpriteUp = {
  caixa: [40, 30], quadros: [[0, 0, 10, 10, 5, 4]],
  clipes: {
    Idle: { quadros: [[1, 0, 10, 10, 5, 4], [2, 0, 10, 10, 5, 4]], ms: [100, 100], loop: true },
    Evol: { quadros: [[3, 0, 12, 12, 4, 3], [4, 0, 12, 12, 4, 3]], ms: [200, 300], loop: false },
  },
};
const atlas = (s: SpriteUp, comClipes = true): AtlasOk =>
  ({ tipo: "ok", dados: { atlas: "a.png", ms_por_quadro: 120, sprites: { f: s }, pecas: {} }, img, imgClipes: comClipes ? imgClipes : undefined });

test("quadroDigimon: o Evol nao repete e segue no Idle, como no prototipo", () => {
  const a = atlas(sprite);
  expect(quadroDigimon(a, "f", "Evol", 0).quadro[0]).toBe(3);
  expect(quadroDigimon(a, "f", "Evol", 250).quadro[0]).toBe(4);
  expect(quadroDigimon(a, "f", "Evol", 500).quadro[0]).toBe(1);     /* fim do Evol (500 ms): Idle do comeco */
  expect(quadroDigimon(a, "f", "Evol", 650).quadro[0]).toBe(2);
  expect(quadroDigimon(a, "f", "Idle", 150).img).toBe(imgClipes);
});

test("quadroDigimon: sem Evol, o Idle; sem o atlas de clipes, o Idle do atlas atual a ms_por_quadro", () => {
  const semEvol: SpriteUp = { ...sprite, clipes: { Idle: sprite.clipes!.Idle } };
  expect(quadroDigimon(atlas(semEvol), "f", "Evol", 0).quadro[0]).toBe(1);
  const semClipes: SpriteUp = { caixa: [40, 30], quadros: [[7, 0, 10, 10, 5, 4], [8, 0, 10, 10, 5, 4]] };
  const r = quadroDigimon(atlas(semClipes, false), "f", "Evol", 130);
  expect([r.quadro[0], r.img]).toEqual([8, img]);
  expect(() => quadroDigimon(atlas(semClipes), "x", "Idle", 0)).toThrow(/desconhecido/);
});

test("centroDoCorpo: o centro do primeiro quadro desenhavel do Idle, dentro da caixa", () => {
  expect(centroDoCorpo(atlas(sprite), "f")).toEqual([10, 9]);
  const vazio: SpriteUp = { caixa: [4, 4], quadros: [[0, 0, 0, 0, 0, 0], [0, 0, 2, 2, 1, 1]] };
  expect(centroDoCorpo(atlas(vazio, false), "f")).toEqual([2, 2]);
});
