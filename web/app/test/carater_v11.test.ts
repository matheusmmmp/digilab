/* O carater dos pets v11 (PW-4 opcao (b); docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 15) contra test/gabaritos/carater_v11_python.json
   (experiments/exportar_gabarito_carater_v11.py), bit a bit no Node: as sondas com os receptores do corpo, a distribuicao do cerebro
   recem-nascido, e nas quatro vidas v11 do gabarito dos lobos, com o cerebro rejogado pelo laco do corpo ate o fim da crianca e ate o
   fim do adolescente (o corte do avanco de evolucao.politica_no_tick), a distribuicao, o bruto, o carater, a linha e a forma adulta.
   E tambem: medir o carater nao muda o cerebro, e as constantes sao as da calibracao. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCP, CCP_V11, DESLOC_CARATER_V11 } from "../motor/constantes.ts";
import { brutoV11, caraterV11, distBaseV11, distCerebroV11, formaAdultaDe, linhaDoCarater, sondasCaraterV11 } from "../motor/carater.ts";
import { MotorCorpo, type EventoCorpo } from "../motor/motor_corpo.ts";
import { bracoV11 } from "../motor/pet_v11.ts";

interface Momento { quando: "adolescente" | "adulto"; tick: number; dist: Record<string, number>[]; bruto: Record<string, number>;
  carater: Record<string, number>; linha?: string; forma?: string }
const ler = (nome: string) => JSON.parse(readFileSync(new URL(`./gabaritos/${nome}`, import.meta.url), "utf8"));
const G = ler("carater_v11_python.json") as {
  versao: number; escala: number; desloc: Record<string, Record<string, number>>; ccp: Record<string, number>;
  sondas: { vetor: number[]; ticks_desde_cuidado: number; corpo: Record<string, number> }[]; dist_base: Record<string, number>[];
  vidas: { dono: string; semente: number; momentos: Momento[] }[];
};
const L = ler("lobos_python.json") as { v11: { dono: string; semente: number; log: EventoCorpo[] }[] };
const ordenado = <T>(d: Record<string, T>) => Object.fromEntries(Object.keys(d).sort().map(k => [k, d[k]]));

/** o cerebro da vida no tick (evolucao.politica_no_tick: o log ate o tick, cortando o avanco que o atravessa) */
function cerebroNoTick(log: EventoCorpo[], semente: number, tick: number) {
  const braco = bracoV11(), motor = new MotorCorpo(braco, semente);
  for (const e of log) {
    if (e.tick >= tick) break;
    if (e.tipo === "avanco") motor.aplicarEvento({ ...e, valor: Math.min(e.valor as number, tick - e.tick) });
    else motor.aplicarEvento(e);
  }
  return braco.cerebro;
}

describe("o carater do v11 = o Python, bit a bit", () => {
  test("as constantes sao as da calibracao e as sondas sao as do Python", () => {
    expect(G.versao).toBe(1);
    expect([G.escala, G.desloc]).toStrictEqual([CCP_V11.escala, { adolescente: ordenado(DESLOC_CARATER_V11.adolescente), adulto: ordenado(DESLOC_CARATER_V11.adulto) }]
      .map(x => JSON.parse(JSON.stringify(x))));
    expect([G.ccp.estados, G.ccp.amostras, G.ccp.semente]).toEqual([CCP.nEstados, CCP.amostras, CCP.semente]);
    expect(sondasCaraterV11().map(o => ({ vetor: o.v, ticks_desde_cuidado: o.tdc, corpo: ordenado(o.corpo!) }))).toStrictEqual(G.sondas);
    expect(distBaseV11().map(ordenado)).toStrictEqual(G.dist_base);
  });

  G.vidas.forEach((vida, i) => {
    test(`${vida.dono}: o carater no fim da crianca e do adolescente, a linha e a forma`, () => {
      expect([L.v11[i].dono, L.v11[i].semente]).toEqual([vida.dono, vida.semente]);
      let linha: ReturnType<typeof linhaDoCarater> | null = null;
      for (const m of vida.momentos) {
        const c = cerebroNoTick(L.v11[i].log, vida.semente, m.tick);
        expect(distCerebroV11(c).map(ordenado)).toStrictEqual(m.dist);
        expect(ordenado(brutoV11(c))).toStrictEqual(ordenado(m.bruto));
        const car = caraterV11(c, m.quando);
        expect(ordenado(car)).toStrictEqual(ordenado(m.carater));
        if (m.quando === "adolescente") { linha = linhaDoCarater(car); expect(linha).toBe(m.linha); }
        else expect(formaAdultaDe(linha!, car)).toBe(m.forma);
      }
    });
  });

  test("medir o carater nao muda o cerebro", () => {
    const c = cerebroNoTick(L.v11[0].log, L.v11[0].semente, 1980);
    const antes = JSON.stringify(c.estadoInterno()), motivos = c.motivos.length;
    caraterV11(c, "adulto");
    expect([JSON.stringify(c.estadoInterno()), c.motivos.length]).toEqual([antes, motivos]);
  });
});
