/* G-PAR do M-PLAST (LM2, P1 e P2): `plast.montar`, `plast.consequencia_p1` e `plast.creditar` do gabarito da LM0, mais o `habito` e o `incentivo`
   que o impulso pede (digibrain_modular_leituras_plast.json.gz, a leitura da LM1), refeitos aqui no lugar em que o impulso os chamou, com o
   estado de agora do M-PLAST. A assinatura do estado (sha256 do `estado_interno`) e conferida ao fim de cada decisao. */
import { describe, expect, test } from "vitest";
import { CONFIG_DIGIBRAIN_LAB } from "../motor/digibrain/constantes.ts";
import { Plasticidade } from "../motor/digibrain/plast.ts";
import { assinar, conferir, entrada, leiturasPlast, vidasModular } from "./digibrain_modular_gabarito.ts";

describe("G-PAR plast", () => {
  test("montar, consequencia_p1, creditar, habito e incentivo iguais ao Python, e a assinatura igual ao fim de cada decisao", () => {
    const lp = leiturasPlast();
    const n = { montar: 0, p1: 0, creditar: 0, habito: 0, incentivo: 0 };
    let p1Consumo = 0, habitoNaoZero = 0, incentivoNaoZero = 0, creditoNaoZero = 0, andar = 0;
    vidasModular().forEach((v, iv) => {
      const lv = lp[iv]!;
      expect([lv.lugar, lv.dono, lv.semente]).toEqual([v.lugar, v.dono, v.semente]);
      const plast = new Plasticidade(CONFIG_DIGIBRAIN_LAB);
      for (const d of v.decisoes) {
        const leituras = [...lv.decisoes[d.k]!.chamadas];
        for (const c of d.chamadas) {
          const onde = `${v.lugar}/${v.dono}/${v.semente} k=${d.k} ${c.m}`;
          if (c.m === "impulso.unidades") {               // o impulso pergunta ao M-PLAST, no estado de agora
            for (const x of leituras.splice(0)) {
              const o = `${onde} ${x.m}`;
              if (x.m === "plast.habito") {
                conferir(o, plast.habito(x.e[0] as string, x.e[1] as number[]), x.s);
                n.habito++;
                if (x.s !== 0) habitoNaoZero++;
              } else if (x.m === "plast.incentivo") {
                conferir(o, plast.incentivo(x.e[0] as any, x.e[1] as string, x.e[2] as string[]), x.s);
                n.incentivo++;
                if (x.s !== 0) incentivoNaoZero++;
              } else {
                throw new Error(`${o}: leitura nao conferida`);
              }
            }
          }
          if (!c.m.startsWith("plast.")) continue;
          if (c.m === "plast.montar") {
            plast.montar(entrada(d, c, 0));
            n.montar++;
          } else if (c.m === "plast.consequencia_p1") {
            const r = plast.consequenciaP1(entrada(d, c, 0), entrada(d, c, 1), entrada(d, c, 2), entrada(d, c, 3), entrada(d, c, 4), entrada(d, c, 5), entrada(d, c, 6));
            conferir(onde, r, c.s);
            n.p1++;
            if (r !== null) p1Consumo++;
          } else if (c.m === "plast.creditar") {
            const r = plast.creditar(entrada(d, c, 0));
            conferir(onde, r, c.s);
            n.creditar++;
            if (r !== null && r.abs !== 0) creditoNaoZero++;
          } else {
            throw new Error(`${onde}: chamada nao conferida`);
          }
        }
        if (leituras.length) throw new Error(`${v.lugar}/${v.dono}/${v.semente} k=${d.k}: ${leituras.length} leituras do M-PLAST fora do impulso.unidades`);
        conferir(`${v.lugar}/${v.dono}/${v.semente} k=${d.k} assinatura do plast`, assinar(plast.estadoInterno()), d.assinatura["plast"]);
      }
      if (plast.andar !== 0) andar++;
    });
    console.log(`G-PAR plast: ${n.montar + n.p1 + n.creditar + n.habito + n.incentivo} chamadas conferidas (montar ${n.montar}, consequencia_p1 ${n.p1} com consumo ${p1Consumo}, `
      + `creditar ${n.creditar} com mudanca ${creditoNaoZero}, habito ${n.habito} nao nulo ${habitoNaoZero}, incentivo ${n.incentivo} nao nulo ${incentivoNaoZero}; vidas com andar ${andar})`);
    expect(n.montar + n.p1 + n.creditar + n.habito + n.incentivo).toBeGreaterThan(0);
    expect(n.montar).toBe(8 * 384);
    for (const x of [n.p1, n.creditar, n.habito, n.incentivo, p1Consumo, habitoNaoZero, incentivoNaoZero, creditoNaoZero, andar]) expect(x).toBeGreaterThan(0);
  });

  test("sem o P1 e sem o P2 o incentivo e o habito sao 0", () => {
    const p = new Plasticidade({ p1: false, p2: false });
    expect(p.incentivo({}, "racao", [])).toBe(0);
    expect(p.habito("comer", [1024])).toBe(0);
    expect(p.consequenciaP1("comer", null, [], [], [0, 0], [0, 0], 1024)).toBeNull();
    expect(p.creditar({ chave: ["comer", null, null], e: [], r: 0, g_apr: 0 })).toBeNull();
  });
});
