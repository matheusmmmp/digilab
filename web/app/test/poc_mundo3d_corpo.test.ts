/* Os gates do PR 1 do WORLD-POC-02 (docs/TAREFA_V2_WORLD_POC_02.md, seção 4): o corpo químico do jogo no mundo do POC.
     G-POC01-IGUAL  com a chave do corpo desligada (o padrão), o POC-01a byte a byte: os hashes das sementes do e2e do POC-01a
                    (artifacts_v2_world_poc/e2e.json, M5_chrome_node). Este teste entra num commit antes do corpo. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { Simulacao } from "../poc/mundo3d/simulacao.ts";

const E2E_POC01 = JSON.parse(readFileSync(new URL("../../../artifacts_v2_world_poc/e2e.json", import.meta.url), "utf8")) as {
  M5_chrome_node: { semente: number; ticks: number; hash: string }[];
};

describe("G-POC01-IGUAL: com o corpo desligado, o POC-01a byte a byte", () => {
  test("os casos do e2e do POC-01a: três sementes", () => {
    expect(E2E_POC01.M5_chrome_node.map(c => c.semente)).toEqual([101, 202, 303]);
  });
  for (const c of E2E_POC01.M5_chrome_node) {
    test(`semente ${c.semente}, ${c.ticks} ticks: o hash do POC-01a`, () => {
      const padrao = new Simulacao(c.semente);
      padrao.avancar(c.ticks);
      expect(padrao.hash()).toBe(c.hash);
      const desligado = new Simulacao(c.semente, undefined, { corpo: false });
      desligado.avancar(c.ticks);
      expect(desligado.hash()).toBe(c.hash);
      expect(JSON.stringify(desligado.registros)).toBe(JSON.stringify(padrao.registros));
    });
  }
});

/* ------------------------------------------------------------------ E1 e E2: o corpo químico no POC
     G-CORPO-IGUAL     o corpo do POC é o corpo.ts sem cópia: as chamadas gravadas, refeitas num Corpo solto, dão a mesma química
     G-CONSEQUENCIA    comer, andar e a bola mudam o corpo pelos estímulos certos; o contato não chama o corpo
     G-CONTRATO-CORPO  a Observação traz só os receptores, sem química e sem posição absoluta
     G-LACO            o Gate B: a cadeia completa do contrato, na comida e na bola, com a falta menor depois
     G-DET             a mesma semente dá a mesma vida, e o replay a refaz (no Node; o Chrome está no e2e da página) */
import { CCO_V11, CMU } from "../motor/constantes.ts";
import { Corpo, configCorpo } from "../motor/corpo.ts";
import { contribuicoesCorpo } from "../motor/lobos.ts";
import { DRIVES_CONSEQUENCIA, ESTADO_INICIAL_POC, criarCorpoPoc, type ChamadaCorpo } from "../poc/mundo3d/corpo_poc.ts";
import { LIMIARES_CORPO } from "../poc/mundo3d/cerebro.ts";
import { reproduzir } from "../poc/mundo3d/simulacao.ts";

const S = 1024;
const TICKS = 3000;
const vidaComCorpo = (semente = 101, ticks = TICKS) => {
  const s = new Simulacao(semente, undefined, { corpo: true });
  s.avancar(ticks);
  return s;
};
const VIDA = vidaComCorpo();

/** refaz as chamadas num Corpo solto, com a conta escrita aqui de novo (não pelo `aplicar` do POC) */
function refazer(chamadas: readonly ChamadaCorpo[]): Corpo {
  const c = Corpo.deEstado({ ...ESTADO_INICIAL_POC }, { cc: configCorpo(CCO_V11) });
  for (const ch of chamadas) {
    if (ch.t === "passo") c.passo({ tick: ch.tick, dormindo: ch.dormindo, sujeira: ch.sujeira });
    else if (ch.t === "consumo") c.estimuloConsumoMundo("racao", "madura", CMU);
    else if (ch.t === "bola") { c.estimuloBola(CMU.ganho_humor_bola); c.atividade("bola"); }
    else if (ch.t === "andar") c.estimuloAndar(ch.deslocamento, CMU.custo_energia_por_subunidade);
    else throw new Error(`chamada desconhecida: ${JSON.stringify(ch)}`);
  }
  return c;
}

describe("G-CORPO-IGUAL: o corpo do POC é o corpo.ts", () => {
  test("as chamadas da vida, refeitas num Corpo solto, dão a mesma química, a mesma digestão e o mesmo metabolismo", () => {
    expect(VIDA.chamadasCorpo.filter(c => c.t === "passo").length).toBe(TICKS);
    expect(JSON.stringify(refazer(VIDA.chamadasCorpo).paraDict())).toBe(JSON.stringify(VIDA.corpo!.paraDict()));
  });

  test("controle negativo: sem uma das comidas, a química sai outra", () => {
    const i = VIDA.chamadasCorpo.findIndex(c => c.t === "consumo");
    expect(i).toBeGreaterThan(0);
    const sem = VIDA.chamadasCorpo.filter((_, j) => j !== i);
    expect(JSON.stringify(refazer(sem).paraDict())).not.toBe(JSON.stringify(VIDA.corpo!.paraDict()));
  });

  test("o corpo nasce do estado inicial com a CCO_V11 (o corpo do v11, com o metabolismo)", () => {
    const c = criarCorpoPoc();
    expect(c.cc.metabolismo && c.cc.digestao && c.cc.drives_novos).toBe(true);
    expect(JSON.stringify(c.paraDict())).toBe(JSON.stringify(refazer([]).paraDict()));
  });
});

describe("G-CONSEQUENCIA: as consequências do mundo viram os estímulos que o corpo já tem", () => {
  const q = (c: Corpo, n: string) => c.q[n];

  test("comer põe a comida no estômago, e a digestão a tira da falta de fome (na hora, com o que resta da taxa do tick)", () => {
    const c = criarCorpoPoc();
    const f0 = q(c, "fome"), d0 = c.digerido_total;
    c.estimuloConsumoMundo("racao", "madura", CMU);
    expect(c.digerido_total).toBeGreaterThan(d0);       // passou pelo estômago e foi digerida
    expect(q(c, "fome")).toBeLessThan(f0);
    /* e no laço: toda decisão que comeu termina com a falta de fome menor */
    const comeu = VIDA.registros.filter(r => r.fisico.comeu > 0);
    expect(comeu.length).toBeGreaterThan(0);
    for (const r of comeu) expect(r.consequencia!.fome, `decisao ${r.n}`).toBeGreaterThan(0);
  });

  test("andar sobe o cansaço e tira do combustível, na proporção do caminho", () => {
    const delta = (d: number) => {
      const c = criarCorpoPoc(), k0 = q(c, "cansaco"), b0 = q(c, "combustivel");
      c.estimuloAndar(d, CMU.custo_energia_por_subunidade);
      return [q(c, "cansaco") - k0, b0 - q(c, "combustivel")];
    };
    const [k1, b1] = delta(120), [k2, b2] = delta(240);
    expect(k1).toBeGreaterThan(0);
    expect(b1).toBeGreaterThan(0);
    expect(k2).toBe(2 * k1);
    expect(Math.abs(b2 - 2 * b1)).toBeLessThanOrEqual(1);   // o gasto do metabolismo é arredondado uma vez por chamada
  });

  test("o empurrão na bola tira do tédio e da tristeza, uma vez por decisão (CP-5)", () => {
    const c = criarCorpoPoc();
    for (let t = 0; t < 120; t++) c.passo({ tick: t, dormindo: false, sujeira: 0 });
    const td = q(c, "tedio"), tr = q(c, "tristeza");
    c.estimuloBola(CMU.ganho_humor_bola);
    c.atividade("bola");
    expect(q(c, "tedio")).toBeLessThan(td);
    expect(q(c, "tristeza")).toBeLessThan(tr);
    const comEmpurrao = VIDA.registros.filter(r => r.fisico.empurroes > 0).length;
    expect(VIDA.chamadasCorpo.filter(ch => ch.t === "bola").length).toBeGreaterThanOrEqual(comEmpurrao);
    expect(VIDA.chamadasCorpo.filter(ch => ch.t === "bola").length).toBeLessThanOrEqual(comEmpurrao + 1);   // a decisão ainda aberta
  });

  test("o contato não chama o corpo (CP-1): só os quatro estímulos, e há contato no registro", () => {
    expect(new Set(VIDA.chamadasCorpo.map(c => c.t))).toEqual(new Set(["passo", "consumo", "bola", "andar"]));
    expect(VIDA.registros.some(r => r.fisico.contatos.length > 0)).toBe(true);
  });

  test("a consequência do registro é a conta do contribuicoesCorpo do lobos.ts, com os pesos 1", () => {
    const pesos = Object.fromEntries(DRIVES_CONSEQUENCIA.map(d => [d, 1]));
    for (const r of VIDA.registros) {
      expect(r.consequencia, `decisao ${r.n}`).toStrictEqual(contribuicoesCorpo(r.corpo_antes, r.corpo_depois, DRIVES_CONSEQUENCIA, S, pesos));
    }
  });
});

describe("G-CONTRATO-CORPO: a Observação traz só os receptores", () => {
  test("o corpo da Observação são as chaves de Corpo.receptores(), sem química, e nenhuma posição absoluta", () => {
    const receptores = Object.keys(criarCorpoPoc().receptores()).sort();
    for (const r of VIDA.registros) {
      expect(Object.keys(r.observacao.corpo).sort()).toEqual(receptores);
      expect(Object.keys(r.observacao.corpo)).not.toContain("alimento");
      expect(Object.keys(r.observacao.corpo)).not.toContain("combustivel");
    }
    const chaves = (o: unknown): string[] => o && typeof o === "object" ? Object.entries(o).flatMap(([k, v]) => [k, ...chaves(v)]) : [];
    expect(VIDA.registros.flatMap(r => chaves(r.observacao)).filter(k => ["x", "y", "pos", "posicao", "id"].includes(k))).toEqual([]);
  });
});

describe("G-LACO (o Gate B): a cadeia completa do contrato com o corpo de verdade", () => {
  test("na comida: a falta de fome alta, a comida vista, consumir, chegar, comer e a falta menor depois", () => {
    const r = VIDA.registros.find(x => S - x.corpo_antes.fome >= LIMIARES_CORPO.fome && x.intencao.tipo === "consumir"
      && x.observacao.vistos.some(v => v.categoria === "comida" && v.ref === x.intencao.ref)
      && x.executada.parou_por === "chegou" && x.fisico.comeu > 0 && x.consequencia!.fome > 0);
    expect(r, "nenhuma decisão fecha a cadeia da comida").toBeDefined();
    expect(S - r!.corpo_depois.fome).toBeLessThan(S - r!.corpo_antes.fome);
  });

  test("na bola: o tédio alto, a bola vista, empurrar, andar até ela, a bola andar e o tédio menor depois", () => {
    const r = VIDA.registros.find(x => x.corpo_antes.tedio >= LIMIARES_CORPO.tedio && x.intencao.tipo === "empurrar"
      && x.observacao.vistos.some(v => v.categoria === "bola" && v.ref === x.intencao.ref)
      && x.executada.distancia > 0 && x.fisico.empurroes > 0
      && (x.fisico.bola_de[0] !== x.fisico.bola_para[0] || x.fisico.bola_de[1] !== x.fisico.bola_para[1]) && x.consequencia!.tedio > 0);
    expect(r, "nenhuma decisão fecha a cadeia da bola").toBeDefined();
    expect(r!.corpo_depois.tedio).toBeLessThan(r!.corpo_antes.tedio);
  });
});

describe("G-DET com o corpo", () => {
  test("a mesma semente dá o mesmo estado (com o corpo) e os mesmos registros, e o replay refaz a vida", () => {
    const b = vidaComCorpo();
    expect(b.hash()).toBe(VIDA.hash());
    expect(JSON.stringify(b.registros)).toBe(JSON.stringify(VIDA.registros));
    const r = reproduzir(101, VIDA.log, undefined, { corpo: true });
    expect(r.hash()).toBe(VIDA.hash());
    expect(JSON.stringify(r.corpo!.paraDict())).toBe(JSON.stringify(VIDA.corpo!.paraDict()));
  });

  test("controle negativo: outra semente dá outra vida, e o corpo ligado não é o POC-01a", () => {
    expect(vidaComCorpo(202).hash()).not.toBe(VIDA.hash());
    const sem = new Simulacao(101);
    sem.avancar(TICKS);
    expect(sem.hash()).not.toBe(VIDA.hash());
  });
});
