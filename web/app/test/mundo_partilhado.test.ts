/* CO2b (docs/TAREFA_V3_COOPERACAO.md): o mundo partilhado separado da parte de cada pet em motor/mundo.ts, sem mudar o jogo de hoje.
   - o G2 de um pet so: o pet sobre um MundoPartilhado dado (a semente do pet, a entrada 0) e o pet dono do proprio mundo dao a mesma
     vida, decisao a decisao, nas 4 vidas do gabarito do mundo (mundo_python.json); o mundo.test.ts e o coop_etapa0.test.ts (o G-HOJE)
     continuam conferindo a vida de hoje contra o Python;
   - a atualizacao do mundo e idempotente por tick e nao volta no tempo (o Mundo.atualizar do Python);
   - dois pets no mesmo MundoPartilhado: a comida que um come sai do chao do outro, e o relogio do pet que entra depois anda com a entrada;
   - o que a parte do pet recusa: a entrada sem o mundo dado, fora de um inicio de dia, outra ConfigMundo e o contrato da P4 no grupo. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CMU, LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO, TPD, type ConfigMundo } from "../motor/constantes.ts";
import { CONFIG_CONTRATO } from "../motor/contrato.ts";
import { Mundo, MundoPartilhado, alvo, type AlvoMundo, type EstadoNoMundo } from "../motor/mundo.ts";

type Rec = Record<string, unknown>;
type Op = { op: "decisao"; tick: number; fome_antes: number; acao: string; estado: EstadoNoMundo; regra: string | null; com_gancho: boolean;
            ocorrido: (Rec & { alvo: AlvoMundo | null }) | null }
  | { op: "deixar_comida"; tick: number; tipo: string; x: number; y: number } | { op: "deixar_bola"; tick: number; x: number; y: number };
interface Vida { nome: string; semente: number; efeito: Record<string, number>; layout: string; mult_queda: number; traco: Op[]; resumo: Rec }
const G = JSON.parse(readFileSync(new URL("./gabaritos/mundo_python.json", import.meta.url), "utf8")) as { vidas: Vida[] };
const comoJson = (v: unknown): unknown => JSON.parse(JSON.stringify(v));
const configDaVida = (v: Vida): ConfigMundo =>
  ({ ...CMU, layout: v.layout === "afastado" ? LAYOUT_MUNDO_AFASTADO : LAYOUT_MUNDO_PADRAO, mult_queda: v.mult_queda });

/** rejoga o traco de uma vida do gabarito; o alvo das decisoes com gancho e o gravado (o cerebro aleatorio do Python) */
function rejogar(m: Mundo, v: Vida): unknown[] {
  const saida: unknown[] = [];
  for (const op of v.traco) {
    if (op.op === "deixar_comida") { m.deixarComida(op.tick, op.tipo, op.x, op.y); continue; }
    if (op.op === "deixar_bola") { m.deixarBola(op.tick, op.x, op.y); continue; }
    saida.push(comoJson(m.antesDaDecisao(op.tick, op.fome_antes)));
    const gravado = op.ocorrido?.alvo ?? null;
    const escolher = op.com_gancho && gravado ? () => ({ ...gravado }) : null;
    saida.push(comoJson(m.consequencia(op.tick, op.acao, op.estado, escolher, op.regra)));
  }
  return saida;
}

describe("o G2 de um pet so", () => {
  for (const v of G.vidas) {
    test(`${v.nome}: o pet sobre um MundoPartilhado dado e o pet dono do proprio mundo dao a mesma vida`, () => {
      const cm = configDaVida(v);
      const sozinho = new Mundo({ semente: v.semente, cfg: cm, efeitoFrutas: v.efeito });
      const comum = new MundoPartilhado(cm, v.semente);
      const noComum = new Mundo({ semente: v.semente, cfg: cm, efeitoFrutas: v.efeito, partilhado: comum, entrada: 0 });
      expect(rejogar(noComum, v)).toEqual(rejogar(sozinho, v));
      expect(comoJson(noComum.resumo())).toEqual(comoJson(sozinho.resumo()));
      expect(comoJson(sozinho.resumo())).toEqual(v.resumo);
      expect(noComum.comum).toBe(comum);
      expect(sozinho.comum.semente).toBe(v.semente);
    });
  }

  test("os atributos de antes leem do mundo partilhado", () => {
    const m = new Mundo({ semente: 11 });
    expect(m.comidas).toBe(m.comum.comidas);
    expect(m.arvores).toBe(m.comum.arvores);
    expect(m.quedas).toBe(m.comum.quedas);
    expect(m.rolagens).toBe(m.comum.rolagens);
    expect(m.rngArvores).toBe(m.comum.rngArvores);
    expect(m.bola).toBe(m.comum.bola);
    expect(m.pet).toEqual(m.comum.ninho);
    expect(m.pet).not.toBe(m.comum.ninho);           // a posicao e do pet: mover o pet nao move o ninho
  });
});

describe("a atualizacao do mundo", () => {
  test("e idempotente por tick e falha alto num tick para tras", () => {
    const a = new MundoPartilhado(CMU, 7), b = new MundoPartilhado(CMU, 7);
    a.atualizar(3 * TPD);
    a.atualizar(3 * TPD);
    b.atualizar(3 * TPD);
    expect(comoJson(a.resumo())).toEqual(comoJson(b.resumo()));
    expect(a.tickAtualizado).toBe(3 * TPD);
    expect(a.quedas.length).toBeGreaterThan(0);
    expect(() => a.atualizar(3 * TPD - 1)).toThrow(/nao volta no tempo/);
  });
});

describe("dois pets no mesmo MundoPartilhado", () => {
  test("a comida que um come sai do chao do outro, e os registros do mundo sao um so", () => {
    const comum = new MundoPartilhado(CMU, 101);
    const a = new Mundo({ semente: 101, partilhado: comum });
    const b = new Mundo({ semente: 202, partilhado: comum });
    const [nx, ny] = comum.ninho;
    a.deixarComida(10, "racao", nx, ny);
    const e: EstadoNoMundo = { fome: 0.3, energia: 0.9, humor: 0.5, sujeira: 0 };
    a.antesDaDecisao(15, e.fome);
    expect(a.perceber(15).vistos.map(x => x[0])).toEqual(b.perceber(15).vistos.map(x => x[0]));
    const id = [...comum.comidas.keys()][0];
    const ra = a.consequencia(15, "comer", e);
    expect((ra.ocorrido!.comeu as { id: number }).id).toBe(id);
    b.antesDaDecisao(15, e.fome);                       // o segundo na vez percebe o mundo como ficou
    expect(b.comidas.has(id)).toBe(false);
    expect(b.perceber(15).vistos.some(x => x[0] === id)).toBe(false);
    expect(b.candidatos("comer", 0, 15).some(c => c.tipo === "comida" && c.id === id)).toBe(false);
    expect(a.consumos.length).toBe(1);
    expect(b.consumos.length).toBe(0);
    expect(a.deixadas.length).toBe(1);
    expect(b.deixadas.length).toBe(0);
    expect(a.quedas).toBe(b.quedas);
  });

  test("o pet que entra depois tem o relogio dele, e os registros do mundo fisico usam o do mundo", () => {
    const comum = new MundoPartilhado(CMU, 303);
    const b = new Mundo({ semente: 404, partilhado: comum, entrada: TPD });
    expect(b.tm(5)).toBe(TPD + 5);
    b.antesDaDecisao(0, 0.5);
    expect(comum.tickAtualizado).toBe(TPD);
    const [nx, ny] = comum.ninho;
    b.deixarComida(0, "a", nx, ny);
    expect(b.deixadas[0].tick).toBe(TPD);
    expect([...comum.comidas.values()].at(-1)!.tick_posta).toBe(TPD);
    b.consequencia(0, "explorar", { fome: 0.5, energia: 0.9, humor: 0.5, sujeira: 0 });
    expect(b.decisoes[0].tick).toBe(TPD);
    expect(b.situacao({ tipo: "a", tick_posta: TPD }, 0)).toBe("madura");
  });
});

describe("o que a parte do pet recusa", () => {
  test("a entrada sem o mundo dado ou fora de um inicio de dia, outra ConfigMundo e o contrato da P4 no grupo", () => {
    const comum = new MundoPartilhado(CMU, 1);
    expect(() => new Mundo({ semente: 1, entrada: TPD })).toThrow(/entrada so com/);
    expect(() => new Mundo({ semente: 1, partilhado: comum, entrada: 5 })).toThrow(/inicio de dia/);
    expect(() => new Mundo({ semente: 1, partilhado: comum, entrada: -TPD })).toThrow(/inicio de dia/);
    expect(() => new Mundo({ semente: 1, partilhado: comum, cfg: { ...CMU, mult_queda: CMU.mult_queda * 2 } })).toThrow(/mesma ConfigMundo/);
    expect(() => new Mundo({ semente: 1, partilhado: comum, contrato: { ...CONFIG_CONTRATO, ligada: true, paredes: true } }))
      .toThrow(/um pet, fora do grupo/);
    expect(() => new MundoPartilhado({ ...CMU, ligada: false }, 1)).toThrow();
    expect(() => comum.retirarComida(99)).toThrow(/fora do chao/);
    expect(alvo("ponto", 1, 2)).toEqual({ tipo: "ponto", x: 1, y: 2, id: null, de: null });
  });
});
