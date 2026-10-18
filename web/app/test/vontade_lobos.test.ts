/* A vontade do cerebro A (PW-3; docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 12) contra a secao `vontade` de test/gabaritos/lobos_python.json,
   bit a bit no Node:
     - em cada decisao das quatro vidas v11, o desejo e o desvio de cada acao, antes de o cerebro decidir (as vidas rodam pelo laco do corpo
       em TS, motor/motor_corpo.ts, com um espiao que so le);
     - a grade: as 32 sondas com os receptores do corpo, contra o cerebro do fim de cada vida.
   E tambem: a vontade nao muda a vida (o laco com e sem o espiao da o mesmo fim), e o recem-nascido nao tem vontade. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CDJ } from "../motor/constantes.ts";
import { desejoLobos, type ObservacaoLobos } from "../motor/lobos.ts";
import { MotorCorpo, type EventoCorpo, type PoliticaCorpo } from "../motor/motor_corpo.ts";
import { bracoV11 } from "../motor/pet_v11.ts";
import type { Desejo } from "../motor/tipos.ts";

interface DesejoPy { alvo: string; intensidade: number; tipo: string }
interface DecisaoPy { k: number; desejo: DesejoPy | null; desvio: Record<string, number> }
interface SondaPy { vetor: number[]; ticks_desde_cuidado: number; corpo: Record<string, number>; desejo: DesejoPy | null; desvio: Record<string, number> }
interface Vontade {
  regra: string; limiar_vontade: number; limiar_necessidade: number;
  vidas: { dono: string; semente: number; decisoes: DecisaoPy[]; grade: SondaPy[] }[];
}
const G = JSON.parse(readFileSync(new URL("./gabaritos/lobos_python.json", import.meta.url), "utf8")) as {
  vontade: Vontade; v11: { dono: string; semente: number; log: EventoCorpo[] }[];
};
const V = G.vontade;

const paraPy = (d: Desejo | null): DesejoPy | null => d && { alvo: d.alvo, intensidade: d.intensidade, tipo: d.tipo };
/** o desvio com as chaves em ordem (o gabarito sai com sort_keys) */
const ordenado = (d: Record<string, number | undefined>) => Object.fromEntries(Object.keys(d).sort().map(k => [k, d[k]]));

function viver(log: EventoCorpo[], semente: number, espiar: boolean) {
  const braco = bracoV11();
  const decisoes: DecisaoPy[] = [];
  let motor: MotorCorpo | null = null;
  const politica: PoliticaCorpo = {
    agir(o, rng) {
      if (espiar) {
        decisoes.push({ k: decisoes.length, desejo: paraPy(desejoLobos(o, braco.cerebro, motor!.estado.tick)),
          desvio: ordenado(braco.cerebro.desvioAprendido(o)) as Record<string, number> });
      }
      return braco.agir(o, rng);
    },
    observar: t => braco.observar(t),
    consequenciaCorpo: (a, oc, d) => braco.consequenciaCorpo(a, oc, d),
    receberAcaoDono: (a, t) => braco.receberAcaoDono(a, t),
    mudancaNoCorpo: (a, d) => braco.mudancaNoCorpo(a, d),
  };
  motor = new MotorCorpo(politica, semente);
  for (const e of log) motor.aplicarEvento(e);
  return { motor, braco, decisoes };
}

describe("a vontade do cerebro A = o Python (PW-3), bit a bit", () => {
  test("a secao e a do v11, com as margens de hoje", () => {
    expect([V.regra, V.limiar_vontade, V.limiar_necessidade]).toEqual(["tempo_livre", CDJ.limiarVontade, CDJ.limiarNecessidade]);
    expect(V.vidas.map(v => [v.dono, v.semente])).toEqual(G.v11.map(v => [v.dono, v.semente]));
  });

  V.vidas.forEach((vida, i) => {
    test(`${vida.dono}: o desejo e o desvio de cada decisao, e a grade no fim`, () => {
      const { braco, decisoes } = viver(G.v11[i].log, vida.semente, true);
      expect(decisoes.length).toBe(vida.decisoes.length);
      expect(decisoes).toStrictEqual(vida.decisoes);
      const grade = vida.grade.map(s => {
        const o: ObservacaoLobos = { v: [...s.vetor], tdc: s.ticks_desde_cuidado, corpo: s.corpo };
        return { ...s, desejo: paraPy(desejoLobos(o, braco.cerebro, 0)), desvio: ordenado(braco.cerebro.desvioAprendido(o)) };
      });
      expect(grade).toStrictEqual(vida.grade);
    });
  });

  test("a vontade e pura: o laco com o espiao da a mesma vida", () => {
    const v = G.v11[0];
    const a = viver(v.log, v.semente, true), b = viver(v.log, v.semente, false);
    expect(a.motor.estadoDict()).toStrictEqual(b.motor.estadoDict());
    expect(a.braco.cerebro.estadoInterno()).toStrictEqual(b.braco.cerebro.estadoInterno());
  });

  test("o recem-nascido nao tem vontade: todo desvio e 0 e, sem necessidade, o desejo e null", () => {
    const s = V.vidas[0].grade.find(x => x.desejo === null || x.desejo.tipo === "vontade")!;
    const o: ObservacaoLobos = { v: [...s.vetor], tdc: s.ticks_desde_cuidado, corpo: s.corpo };
    const c = bracoV11().cerebro;
    expect(Object.values(c.desvioAprendido(o)).every(d => d === 0)).toBe(true);
    expect(desejoLobos(o, c, 0)).toBeNull();
  });
});
