/* G-PAR do M-ESTADO (LM2): `estado.contexto`, `estado.escolhida` e `estado.consequencia` do gabarito da LM0, na ordem de cada vida (a intencao, o
   compromisso, a frustracao, a DX-4 com a busca e a opcao composta). O estado antes e depois e conferido pela assinatura (o sha256 do
   `estado_interno`) que o gabarito grava ao fim de cada decisao: o TS refaz a vida, decisao a decisao, e a assinatura tem de ser a mesma. */
import { describe, expect, test } from "vitest";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_MODULAR_MUNDO } from "../motor/digibrain/constantes.ts";
import { EstadoDinamico } from "../motor/digibrain/estado.ts";
import { assinar, conferir, entrada, vidasModular } from "./digibrain_modular_gabarito.ts";

/** a chave da persistencia no Python (`str` da tupla) em JSON: ('comer', 'cheiro', None) -> ["comer","cheiro",null] */
const chaveDoPython = (t: string): string => JSON.stringify(JSON.parse(t.replace(/'/g, '"').replace(/None/g, "null").replace(/\(/g, "[").replace(/\)/g, "]")));

describe("G-PAR estado", () => {
  test("contexto, escolhida e consequencia iguais ao Python, e a assinatura do estado igual ao fim de cada decisao", () => {
    const n = { contexto: 0, escolhida: 0, consequencia: 0, assinaturas: 0 };
    const fins = new Set<string>();
    let composta = 0, comPersistencia = 0, comCredito = 0, guardada = 0, fComF = 0;
    for (const v of vidasModular()) {
      const estado = new EstadoDinamico(CONFIG_MODULAR_MUNDO, CONFIG_DIGIBRAIN_LAB);
      for (const d of v.decisoes) {
        for (const c of d.chamadas) {
          if (!c.m.startsWith("estado.")) continue;
          const onde = `${v.lugar}/${v.dono}/${v.semente} k=${d.k} ${c.m}`;
          if (c.m === "estado.contexto") {
            const s = estado.contexto();
            const esperado = c.s as any;
            const persistencia = Object.fromEntries(Object.entries(esperado.persistencia as Record<string, number>).map(([k, h]) => [chaveDoPython(k), h]));
            conferir(onde, s, { ...esperado, persistencia });
            n.contexto++;
            if (Object.keys(s.persistencia).length) comPersistencia++;
            if (s.F !== 0) fComF++;
          } else if (c.m === "estado.escolhida") {
            const saida = estado.escolhida(entrada(d, c, 0), entrada(d, c, 1), entrada(d, c, 2), entrada(d, c, 3), entrada(d, c, 4));
            conferir(onde, saida, c.s);
            n.escolhida++;
            for (const f of saida) fins.add(f.motivo);
            if (estado.I?.composta) composta++;
          } else if (c.m === "estado.consequencia") {
            const saida = estado.consequencia(entrada(d, c, 0), entrada(d, c, 1), entrada(d, c, 2));
            conferir(onde, saida, c.s);
            n.consequencia++;
            for (const f of saida) fins.add(f.motivo);
            if (saida.some(f => f.credito === false)) comCredito++;
            if (estado.guardada !== null) guardada++;
          } else {
            throw new Error(`${onde}: chamada nao conferida`);
          }
        }
        conferir(`${v.lugar}/${v.dono}/${v.semente} k=${d.k} assinatura do estado`, assinar(estado.estadoInterno()), d.assinatura["estado"]);
        n.assinaturas++;
      }
    }
    console.log(`G-PAR estado: ${n.contexto + n.escolhida + n.consequencia} chamadas conferidas (contexto ${n.contexto}, escolhida ${n.escolhida}, consequencia ${n.consequencia}), `
      + `${n.assinaturas} assinaturas; fins ${[...fins].sort().join(",")}; persistencia ${comPersistencia}, F>0 ${fComF}, achou/credito ${comCredito}, composta ${composta}, guardada ${guardada}`);
    expect(n.contexto + n.escolhida + n.consequencia).toBeGreaterThan(0);
    expect(n.contexto).toBe(8 * 384);
    expect(n.escolhida).toBe(8 * 384);
    expect(n.consequencia).toBe(8 * 383);
    for (const x of [comPersistencia, fComF, comCredito, composta, guardada]) expect(x).toBeGreaterThan(0);
    for (const m of ["meta", "trocou", "achou", "unica"]) expect(fins.has(m)).toBe(true);
  });

  test("as subchaves de fora do laboratorio falham alto", () => {
    for (const k of ["credito_corrida", "intencao_suspensa", "redecidir_evento"] as const) {
      expect(() => new EstadoDinamico(CONFIG_MODULAR_MUNDO, { ...CONFIG_DIGIBRAIN_LAB, [k]: true })).toThrow(new RegExp(k));
    }
    const e = new EstadoDinamico(CONFIG_MODULAR_MUNDO, CONFIG_DIGIBRAIN_LAB);
    expect(() => e.cuidarSuspensa()).toThrow(/intencao_suspensa/);
    expect(() => e.eventos()).toThrow(/redecidir_evento/);
    expect(() => e.registrarRedecisao()).toThrow(/redecidir_evento/);
  });
});
