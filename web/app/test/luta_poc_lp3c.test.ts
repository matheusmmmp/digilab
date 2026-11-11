/* LUTA_POC, LP3c: o desenho do tiro, da camera e do fim da luta em tempo real, sem mudar nenhum resultado do motor ("Desenho agora, motor
   na LP5", decisao do Matheus). O voo guarda a fracao do caminho ate o acerto (o desenho leva a cabeca da frente do sprite a borda do alvo),
   o tiro que nasce e acerta no mesmo passo ganha um voo, a tela anda devagar perto de um tiro (os passos e o fim sao os mesmos) e o Die
   segura o ultimo quadro com corpo. */
import { describe, expect, test } from "vitest";
import { LIMITE_POC_MS, configLutaPoc, criarLutaPoc, passoPoc, sorteiosPoc, statsRivalArena, type EntradaLutaPoc, type LutadorPoc } from "../motor/index.ts";
import { lutar as lutarArena } from "../motor/arena/luta.ts";
import { RITMO_TIRO, aplicarEventosPoc, passoDe, passosDoTiro, visualNovoPoc, type VooPoc } from "../src/telas/lutar/palcoPoc/visualPoc.ts";
import { clipeDoLutador, origemDoSprite, quadroComCorpo, type CorpoSprite } from "../src/telas/lutar/palcoPoc/desenhoPoc.ts";
import { ladoDesenho } from "../src/lutaPocTela.ts";
import type { Quadro } from "../src/atlas.ts";

const ent = (cena: EntradaLutaPoc["cena"], a: string, b: string, semente: number): EntradaLutaPoc =>
  ({ cena, semente, a: { forma: a, stats: statsRivalArena(a) }, b: { forma: b, stats: statsRivalArena(b) } });

/** refaz a luta como o palco, com os passos por quadro da tela (base, e o ritmo dos tiros); devolve a luta, o visual e os voos todos */
function assistir(e: EntradaLutaPoc, base = 3) {
  const L = criarLutaPoc(configLutaPoc(e), sorteiosPoc(e.semente)); L.eventos = [];
  const v = visualNovoPoc(), formas = [ladoDesenho(e.a.forma).forma, ladoDesenho(e.b.forma).forma] as const, voos = new Set<VooPoc>();
  let quadros = 0, lentos = 0;
  while (!L.fim && L.relogio < LIMITE_POC_MS) {
    const n = passosDoTiro(L, base); quadros++; if (n < base) lentos++;
    for (let q = 0; q < n && !L.fim && L.relogio < LIMITE_POC_MS; q++) { aplicarEventosPoc(v, L, passoPoc(L), formas); for (const o of v.voos) voos.add(o); }
  }
  return { L, v, voos: [...voos], quadros, lentos };
}

const LUTAS: [EntradaLutaPoc["cena"], string, string, number][] = [
  ["campo", "cirro_crianca_arisco", "ferrugem_crianca_arisco", 1],          /* Gabumon x Veemon */
  ["coliseu", "cirro_adolescente_brigao", "cirro_adolescente_colosso", 1], /* Garurumon x Gatomon */
  ["praia", "ferrugem_adolescente_cacador", "brasa_adolescente_brigao", 1], /* Gargomon x Greymon */
  ["campo", "brasa_crianca_sereno", "cirro_crianca_arisco", 1],           /* Agumon x Gabumon */
  ["ringue", "brasa_adulto_furioso", "ferrugem_adulto_muralha", 1],       /* WarGreymon x SlashAngemon */
];

describe("o ritmo dos tiros so muda a tela", () => {
  for (const [cena, a, b, s] of LUTAS) test(`${cena}: ${a} x ${b}`, () => {
    const r = lutarArena(ent(cena, a, b, s)), x = assistir(ent(cena, a, b, s)), y = assistir(ent(cena, a, b, s), 6);
    for (const L of [x.L, y.L]) { expect(L.vencedor).toBe(r.vencedor); expect(L.relogio).toBe(r.relogio); expect(L.a.hp).toBe(r.vidaA); expect(L.b.hp).toBe(r.vidaB); }
    /* a tela anda devagar em volta dos tiros, mas nao a luta inteira */
    expect(x.lentos).toBeGreaterThan(0);
    expect(x.lentos).toBeLessThan(x.quadros);
  });
  test("perto de um tiro, no maximo RITMO_TIRO.lentos passos por quadro; longe, a base", () => {
    const L = criarLutaPoc(configLutaPoc(ent("campo", "cirro_crianca_arisco", "ferrugem_crianca_arisco", 1)), sorteiosPoc(1));
    expect(passosDoTiro(L, 3)).toBe(3);
    let viu = false;
    while (!L.fim && L.relogio < LIMITE_POC_MS && !viu) { passoPoc(L); if (L.projeteis.length || passosDoTiro(L, 3) < 3) viu = true; }
    expect(viu).toBe(true);
    expect(passosDoTiro(L, 3)).toBeLessThanOrEqual(RITMO_TIRO.lentos);
  });
});

describe("o voo no desenho: a fracao ate o acerto", () => {
  test("cada voo tem um alvo e uma fracao por ponto; a fracao nunca desce, comeca em 0 e o acerto termina em 1", () => {
    let acertos = 0, sinteticos = 0;
    for (const [cena, a, b, s] of LUTAS) for (const o of assistir(ent(cena, a, b, s)).voos) {
      expect(o.alvos.length).toBe(o.pts.length);
      expect(o.f.length).toBe(o.pts.length);
      expect(o.f[0]).toBe(0);
      for (let j = 1; j < o.f.length; j++) { expect(o.f[j]).toBeGreaterThanOrEqual(o.f[j - 1]); expect(o.f[j]).toBeLessThanOrEqual(1); }
      if (o.acertou) { acertos++; expect(o.f[o.f.length - 1]).toBe(1); }
      if (o.sintetico) { sinteticos++; expect(o.tFim).toBe(o.t0 + 1); expect(o.acertou).toBe(true); }
    }
    expect(acertos).toBeGreaterThan(0);
    expect(sinteticos).toBeGreaterThanOrEqual(0);
  });
  test("todo dano de golpe com projetil tem um voo que acaba no passo dele (o tiro que nasce e acerta no mesmo passo tambem)", () => {
    for (const [cena, a, b, s] of LUTAS) {
      const L = criarLutaPoc(configLutaPoc(ent(cena, a, b, s)), sorteiosPoc(s)); L.eventos = [];
      const v = visualNovoPoc(), formas = [ladoDesenho(a).forma, ladoDesenho(b).forma] as const;
      while (!L.fim && L.relogio < LIMITE_POC_MS) {
        const ev = passoPoc(L); aplicarEventosPoc(v, L, ev, formas);
        const t = passoDe(L);
        for (const e of ev) if (e.tipo === "dano") {
          const at: LutadorPoc = e.at.lado === "a" ? L.a : L.b, dados = e.hab ? at.sk : at.g;
          if (!dados.proj) continue;
          expect(v.voos.some(o => o.de === (e.at.lado === "a" ? 0 : 1) && o.tFim === t && o.acertou), `${cena} ${a} x ${b} p${t}`).toBe(true);
        }
      }
    }
  });
});

describe("o sprite pelo corpo e o fim da luta", () => {
  const corpo: CorpoSprite = { cx: 60, meia: 20, topo: 10, pes: 70, caixa: 100, topoMax: 4 };
  test("a caixa e posta pelo meio do corpo e pela linha dos pes; o espelho vira em volta da caixa", () => {
    expect(origemDoSprite(corpo, 500, 300, 3, false)).toEqual({ x: 500 - 60 * 3, y: 300 - 70 * 3 });
    /* espelhado, o meio do corpo fica em caixa - cx dentro da caixa: o meio continua em X */
    const o = origemDoSprite(corpo, 500, 300, 3, true);
    expect(o.x + (corpo.caixa - corpo.cx) * 3).toBe(500);
  });
  test("o Die segura o ultimo quadro com corpo (o vazio do fim volta ao anterior)", () => {
    const q = (w: number): Quadro => [0, 0, w, w, 0, 0];
    const die = [q(10), q(9), q(8), q(0)];
    expect(quadroComCorpo(die, 3)).toBe(2);
    expect(quadroComCorpo(die, 9)).toBe(2);
    expect(quadroComCorpo(die, 1)).toBe(1);
  });
  test("acabada a luta, quem ficou de pe vai para o Idle; o derrotado fica no Die", () => {
    const L = criarLutaPoc(configLutaPoc(ent("campo", "cirro_crianca_arisco", "ferrugem_crianca_arisco", 1)), sorteiosPoc(1));
    while (!L.fim && L.relogio < LIMITE_POC_MS) passoPoc(L);
    const venc = L.vencedor === "a" ? L.a : L.b, perd = L.vencedor === "a" ? L.b : L.a;
    expect(clipeDoLutador(venc, 96, true)).toEqual({ clipe: "Idle", t: 96 });
    expect(clipeDoLutador(perd, 96, true).clipe).toBe("Die");
    /* durante a luta, o clipe e o do estado */
    expect(clipeDoLutador({ ...venc, estado: "attack", t: 40 }, 0, false)).toEqual({ clipe: "Attack_1", t: 40 });
  });
});
