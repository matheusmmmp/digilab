/* LUTA_POC, LP3 (docs/TAREFA_V3_LUTA_POC.md, secoes 3.3a e 5.1): a tela da luta da POC e so vista. Os testes da LUTA_EFEITOS (E1 a E5),
   portados do palco 1D para o palco 2D: o estado visual e o mesmo para a mesma luta, passo a passo; cada efeito sai do evento equivalente da
   simulacao da POC; e a tela nao muda o resultado. Mais: o palco refaz as lutas do motor (Arena, Campanha com a serie da Cidadela, Liga,
   Torre e Salao) com a mesma entrada e chega ao mesmo fim; o projetil nosso da LP-8 (desde a LP3b, o tiro de verdade da simulacao). */
import { describe, expect, test } from "vitest";
import {
  ACAO_POC, FORMAS_ARENA, GOLPES_DA_POC, IDS_CENA, LIMITE_POC_MS, Motor, RIVAL_LIGA, RIVAL_SALAO, configLutaPoc, criarLutaPoc, passoPoc, sorteiosPoc, statsRivalArena,
  type EntradaLutaPoc, type LutaPoc,
} from "../motor/index.ts";
import { lutar as lutarArena } from "../motor/arena/luta.ts";
import { IMPACTO } from "../src/telas/lutar/palcoTR/efeitosTR.ts";
import { CHAO } from "../src/telas/lutar/palcoTR/chaoTR.ts";
import {
  CAMERA_POC, aplicarEventosPoc, barraDoPasso, claraoPoc, consumirPausaPoc, nivelDaDistanciaPoc, passoDe, preparoDaHabilidade, puloDoEmpurrao,
  tremidaPoc, visualNovoPoc, PREFABS_LP8, type VisualPoc,
} from "../src/telas/lutar/palcoPoc/visualPoc.ts";
import { ladoDesenho, lutasDoResultado } from "../src/lutaPocTela.ts";
import { petDosTorneios, treinarMuito } from "./lp2b_torneios.ts";

const ent = (cena: EntradaLutaPoc["cena"], a: string, b: string, semente: number): EntradaLutaPoc =>
  ({ cena, semente, a: { forma: a, stats: statsRivalArena(a) }, b: { forma: b, stats: statsRivalArena(b) } });

/** refaz a luta como o palco (lutaPocTela.ts) e devolve, a cada passo, a marca dos efeitos; com `ver` false, so a luta */
function assistir(e: EntradaLutaPoc, ver = true, aoPasso?: (v: VisualPoc, L: LutaPoc) => void) {
  const L = criarLutaPoc(configLutaPoc(e), sorteiosPoc(e.semente)); L.eventos = [];
  const v = visualNovoPoc(), formas = [ladoDesenho(e.a.forma).forma, ladoDesenho(e.b.forma).forma] as const, marcas: string[] = [];
  let pausa = 0;
  while (!L.fim && L.relogio < LIMITE_POC_MS) {
    const ev = passoPoc(L);
    if (!ver) continue;
    aplicarEventosPoc(v, L, ev, formas); pausa += consumirPausaPoc(v, false);
    const p = passoDe(L);
    marcas.push(JSON.stringify([p, tremidaPoc(v, p), [claraoPoc(v, p, 0), claraoPoc(v, p, 1)], v.numeros.map(n => [n.txt, n.forte]), v.voos.map(o => [o.de, o.nosso, o.pts.length, o.tFim]),
      v.marcas.map(m => m.m.tipo), v.cam, v.koEm]));
    aoPasso?.(v, L);
  }
  return { L, v, marcas, pausa };
}

const LUTAS: [EntradaLutaPoc["cena"], string, string, number][] = [
  ["floresta", "cirro_crianca_arisco", "brasa_crianca_sereno", 101],
  ["ringue", "brasa_adulto_furioso", "cirro_adulto_furioso", 108],
  ["castelo", "cirro_adolescente_guardiao", "brasa_adolescente_colosso", 106],
];

describe("so vista: a mesma luta, os mesmos efeitos, o mesmo fim", () => {
  for (const [cena, a, b, s] of LUTAS) test(`${cena}: ${a} x ${b}`, () => {
    const x = assistir(ent(cena, a, b, s)), y = assistir(ent(cena, a, b, s)), sem = assistir(ent(cena, a, b, s), false), r = lutarArena(ent(cena, a, b, s));
    expect(x.marcas).toEqual(y.marcas);
    for (const L of [x.L, sem.L]) { expect(L.vencedor).toBe(r.vencedor); expect(L.relogio).toBe(r.relogio); expect(L.a.hp).toBe(r.vidaA); expect(L.b.hp).toBe(r.vidaB); }
    expect(x.pausa).toBeGreaterThan(0);
  });
  test("os 8 mapas desenham do comeco ao fim sem erro, com o fim da luta sem tela", () => {
    for (const [i, cena] of IDS_CENA.entries()) {
      const e = ent(cena, "brasa_adolescente_brigao", "limo_adolescente_cacador", 201 + i), x = assistir(e), r = lutarArena(e);
      expect([x.L.vencedor, x.L.relogio]).toEqual([r.vencedor, r.relogio]);
    }
  });
});

describe("E1, o impacto", () => {
  test("cada dano vira impacto, numero e pausa; a tremida e inteira e ate o maximo; o clarao dura IMPACTO.clarao passos", () => {
    let impactos = 0;
    assistir(ent(...LUTAS[1]), true, (v, L) => {
      const p = passoDe(L);
      impactos += v.impactos.filter(i => i.t0 === p).length;
      const t = tremidaPoc(v, p); for (const n of [t.x, t.y]) { expect(Number.isInteger(n)).toBe(true); expect(Math.abs(n)).toBeLessThanOrEqual(IMPACTO.tremidaMaxPx); }
    });
    expect(impactos).toBeGreaterThan(0);
    const v = visualNovoPoc(); v.impactos.push({ lado: 0, t0: 100, frac: 1, forte: true, crit: false, hab: true, x: 0, y: 0, dir: 1, de: 1 });
    expect(claraoPoc(v, 100, 0)).toBe(true); expect(claraoPoc(v, 100 + IMPACTO.clarao, 0)).toBe(false); expect(claraoPoc(v, 100, 1)).toBe(false);
    v.pausaMs = 70; expect(consumirPausaPoc(v, true)).toBe(0); expect(v.pausaMs).toBe(0);
  });
  test("o numero forte (maior e amarelo) e o critico e a habilidade", () => {
    const fortes: boolean[] = [];
    assistir(ent(...LUTAS[1]), true, v => { for (const i of v.impactos) fortes.push(i.forte === (i.crit || i.hab || i.frac >= IMPACTO.fracaoPesado)); });
    expect(fortes.length).toBeGreaterThan(0); expect(fortes.every(Boolean)).toBe(true);
  });
  test("o empurrao grande (o Ringue) poe o arrasto e o pulo, que volta ao chao", () => {
    let arrastos = 0, pulou = false;
    assistir(ent(...LUTAS[1]), true, (v, L) => { const p = passoDe(L); arrastos += v.marcas.filter(m => m.m.tipo === "arrasto" && m.m.t0 === p).length; if (puloDoEmpurrao(v, 0, p) > 0 || puloDoEmpurrao(v, 1, p) > 0) pulou = true; });
    expect(arrastos).toBeGreaterThan(0); expect(pulou).toBe(true);
    expect(ACAO_POC.empurrao).toBeGreaterThan(0);
  });
});

describe("E2, os projeteis e a LP-8", () => {
  test("cada projetil da simulacao vira um voo, com a cabeca a cada passo, e fecha quando sai", () => {
    let vistos = 0;
    assistir(ent("campo", "brasa_crianca_sereno", "limo_crianca_arisco", 303), true, (v, L) => {
      for (const pr of L.projeteis) { const o = v.voos.find(x => !x.nosso && x.tFim === null && x.pts[x.pts.length - 1].x === pr.x && x.pts[x.pts.length - 1].y === pr.y); expect(o).toBeDefined(); vistos++; }
    });
    expect(vistos).toBeGreaterThan(0);
  });
  test("o projetil nosso (LP-8, no nucleo desde a LP3b): as cinco formas atiram o proprio efeito de acerto, e o voo e o da simulacao", () => {
    expect([...PREFABS_LP8].sort()).toEqual(Object.values(GOLPES_DA_POC).flatMap(g => g.hits.map(h => h.prefab)).sort());
    expect(PREFABS_LP8.size).toBe(5);
    for (const [forma, g] of Object.entries(GOLPES_DA_POC)) {
      const prefab = g.hits[0].prefab;
      let vistos = 0, acertos = 0;
      for (const s of [101, 102, 103]) {
        assistir(ent("campo", forma, "brasa_crianca_sereno", s), true, (v, L) => {
          const p = passoDe(L);
          /* cada tiro do lado azul na simulacao e um voo nosso, com a cabeca no projetil */
          for (const pr of L.projeteis.filter(x => x.de.lado === "a")) {
            const o = v.voos.find(x => x.tFim === null && x.de === 0 && x.pts[x.pts.length - 1].x === pr.x && x.pts[x.pts.length - 1].y === pr.y);
            expect(o?.nosso).toBe(true); expect(o?.prefab).toBe(prefab); vistos++;
          }
          /* o acerto: o voo fecha no passo do dano */
          for (const o of v.voos.filter(x => x.nosso && x.acertou && x.tFim === p)) { acertos++; expect(v.impactos.some(i => i.t0 === p && i.de === 0)).toBe(true); }
        });
        if (acertos) break;
      }
      expect(vistos, forma).toBeGreaterThan(0);
      expect(acertos, forma).toBeGreaterThan(0);
    }
  });
  test("so os Digimon da lista ganham o projetil nosso (o Agumon tem o do jogo)", () => {
    const x = assistir(ent("campo", "brasa_crianca_sereno", "limo_crianca_arisco", 303));
    expect(x.v.voos.length).toBeGreaterThan(0);
    expect(x.v.voos.every(o => !o.nosso)).toBe(true);
    expect(FORMAS_ARENA.brasa_crianca_sereno.golpe.proj?.prefab).not.toMatch(/_Hit$/);
  });
});

describe("E3, a telegrafia e o chao", () => {
  test("a elipse da habilidade fecha de 0 a 1 do inicio do ataque ao golpe; o acerto da habilidade deixa a cratera e a onda", () => {
    let vistos = 0, crateras = 0;
    const ultimo = [-1, -1];
    assistir(ent(...LUTAS[2]), true, (v, L) => {
      [L.a, L.b].forEach((u, i) => {
        const pr = preparoDaHabilidade(u);
        if (!pr) { ultimo[i] = -1; return; }
        vistos++; expect(pr.f).toBeGreaterThanOrEqual(ultimo[i]); expect(pr.f).toBeLessThanOrEqual(1); ultimo[i] = pr.f;
      });
      crateras += v.marcas.filter(m => m.m.tipo === "cratera" && m.m.t0 === passoDe(L)).length;
    });
    expect(vistos).toBeGreaterThan(0); expect(crateras).toBeGreaterThan(0);
    expect(CHAO.durMarca).toBeGreaterThan(0);
  });
});

describe("E4, o desvio e a aura", () => {
  test("o desvio (o dash da POC) acontece e guarda as posicoes de antes para a imagem fantasma; a aura vem com a habilidade pronta", () => {
    let dash = 0, pronta = 0;
    assistir(ent("coliseu", "cirro_adulto_muralha", "ferrugem_adulto_muralha", 111), true, (v, L) => {
      for (const [i, u] of [L.a, L.b].entries()) { if (u.dash > 0) { dash++; expect(v.hist[i].length).toBeGreaterThan(3); } if (u.recSk <= 0) pronta++; }
    });
    expect(dash).toBeGreaterThan(0); expect(pronta).toBeGreaterThan(0);
  });
});

describe("E5, a barra, o nocaute e a camera", () => {
  test("a barra guarda o dano atrasado; o nocaute marca o passo; a camera tem histerese", () => {
    const x = assistir(ent(...LUTAS[0]));
    const k = x.v.koEm.findIndex(n => n !== null);
    expect(k).toBeGreaterThanOrEqual(0);
    const fim = passoDe(x.L), b = barraDoPasso(x.v.vidas[k], fim);
    expect(b).not.toBeNull(); expect(b!.hp).toBeLessThanOrEqual(0);
    const [l1, l2] = CAMERA_POC.limiares, h = CAMERA_POC.histerese;
    expect(nivelDaDistanciaPoc(l1 - 1, 0)).toBe(0); expect(nivelDaDistanciaPoc(l1 - h - 1, 0)).toBe(1);
    expect(nivelDaDistanciaPoc(l1 + 1, 1)).toBe(1); expect(nivelDaDistanciaPoc(l1 + h + 1, 1)).toBe(0);
    expect(nivelDaDistanciaPoc(l2 - h - 1, 1)).toBe(2);
  });
});

describe("o palco refaz as lutas do motor (a mesma entrada, o mesmo fim)", () => {
  const confere = (r: ReturnType<Motor["lutarPoc"]>) => {
    const lutas = lutasDoResultado(r);
    expect(lutas.length).toBe(r.serie.length);
    for (const l of lutas) {
      const x = assistir(l.entrada, false);
      expect({ vencedor: x.L.vencedor, relogio: x.L.relogio, passos: passoDe(x.L) }).toEqual({ vencedor: l.esperado!.vencedor, relogio: l.esperado!.relogio, passos: l.esperado!.passos });
    }
    return lutas;
  };
  test("a Arena, a Liga (6 lutas sem cura), a Torre e o Salao de um pet v21 treinado", () => {
    const m = petDosTorneios(101); treinarMuito(m, 1500);
    const tratar = () => { if (m.lesionadoDesde !== null) m.observar("tratar_lesao"); m.avancar(30); };
    const arena = confere(m.lutarPoc(m.rivaisArenaPoc()[0], 4242, "praia")); expect(arena[0].rotulo).toBe(""); tratar();
    const liga = confere(m.lutarPoc(RIVAL_LIGA, 7001, null)); expect(liga[0].rotulo).toBe("Luta 1 de 6");
    if (liga.length > 1) expect(liga[1].entrada.a.vida0).toBeDefined();
    tratar();
    const torre = confere(m.lutarPoc("torre_batalha", m.sementeInstalacao("torre_batalha"), null)); expect(torre[0].rotulo).toBe("vitória 1"); tratar();
    confere(m.lutarPoc(RIVAL_SALAO, m.sementeSalao(), null));
  });
});
