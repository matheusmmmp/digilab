/* LUTA_POC, LP6-4: os gabaritos das versoes que lutam pela tabela da v23 (a v24 a v28), gravados antes da versao da LP6 entrar (a regra da
   mecanica nova): as vidas e os torneios da LP2 (o Rookie) e a vida que chega ao Ultimate e ao Mega e luta neles (test/lp6_4_luta_alta.ts,
   a luta que a LP6 muda), com o replay. A v26 e a v28 (o grupo com o sono que segura, #861) so existem no grupo, por isso so tem a vida alta (o primeiro pet do grupo). */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { Motor } from "../motor/index.ts";
import { DIAS_V21, SEMENTES_V21, VARIANTES_V21, gabaritoVidas, gravarV21, viverV21, type VidaV21 } from "./lp2_v21.ts";
import { SEMENTES_LP2B, gabaritoTorneios, gravarTorneios, viverTorneios, type VidaTorneios } from "./lp2b_torneios.ts";
import { SEMENTES_ALTA, gabaritoAlta, gravarAlta, reproduzirAlta, viverAlta, type VidaAlta } from "./lp6_4_luta_alta.ts";

const ler = <T>(f: string): T => JSON.parse(readFileSync(new URL(f, import.meta.url), "utf8")) as T;

for (const versao of [24, 25, 27]) {
  const gab = ler<{ vidas: VidaV21[] }>(gabaritoVidas(versao));
  describe(`a vida da LP2 na v${versao}, byte a byte (LP6-4)`, () => {
    for (const v of VARIANTES_V21) for (const s of SEMENTES_V21) {
      test(`v${versao} ${v} @${s}`, () => {
        const { m, log, res } = viverV21(v, s, DIAS_V21, true, versao);
        expect(m.versao).toBe(versao);
        expect(gravarV21(v, s, m, log, res)).toEqual(gab.vidas.find(x => x.variante === v && x.semente === s));
        expect(Motor.reproduzir(s, log, versao).assinatura()).toBe(m.assinatura());
      });
    }
  });
  const gabT = ler<{ vidas: VidaTorneios[] }>(gabaritoTorneios(versao));
  describe(`os torneios da LP2b na v${versao}, byte a byte (LP6-4; a Torre e de Megas)`, () => {
    for (const s of SEMENTES_LP2B) {
      test(`v${versao} @${s}`, () => {
        const { m, log, res } = viverTorneios(s, versao);
        expect(gravarTorneios(s, m, log, res)).toEqual(gabT.vidas.find(x => x.semente === s));
        expect(Motor.reproduzir(s, log, versao).assinatura()).toBe(m.assinatura());
      });
    }
  });
}

for (const versao of [24, 25, 26, 27, 28]) {
  const gab = ler<{ vidas: VidaAlta[] }>(gabaritoAlta(versao));
  describe(`a vida que luta no Ultimate e no Mega na v${versao}, byte a byte (LP6-4)`, () => {
    test("a forma do gabarito: 3 sementes, todas no Mega, com lutas no Ultimate e no Mega", () => {
      expect(gab.vidas.map(x => x.semente)).toEqual([...SEMENTES_ALTA]);
      for (const x of gab.vidas) { expect(x.estagio).toBe("mega"); expect(x.ult).toBeGreaterThan(0); expect(x.mega).toBeGreaterThan(0); }
    });
    for (const s of SEMENTES_ALTA) {
      test(`v${versao} @${s}: a vida sai igual ao gabarito, e o replay da a mesma assinatura`, () => {
        const x = viverAlta(s, versao);
        expect(x.v.m.versao).toBe(versao);
        const g = gravarAlta(s, x);
        expect(g).toEqual(gab.vidas.find(y => y.semente === s));
        expect(reproduzirAlta(x)).toBe(g.assinatura);
      });
    }
  });
}
