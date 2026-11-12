/* O decodificador `dec-v4` (a fala do assistir, docs/futuro/fala_do_assistir.md, FA-2 a FA-4) em TS contra o Python: a ConfigFalaAssistir folha
   a folha e a saida bit a bit (gabaritos/decodificador_v4_python.json.gz, de experiments/exportar_decodificador_v4.py) em tres conjuntos:
     - toda decisao das vidas de um pet so dos gabaritos do enjoo e da TV no jogo (os motivos ficam la; o laco do TS os refaz nos testes deles);
     - os pares (anterior, motivo) das vidas curtas da GV3b nas sementes dos testes;
     - os casos sinteticos (os sinais do assistir trocados num motivo de verdade), que passam por todo ramo da conta.
   O dec-v1 e o dec-v2 seguem no decodificador.test.ts, com o gabarito deles intacto. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CATALOGO_ASSISTIR, decodificar, decodificarV4, VERSAO_DECODIFICADOR_V4, type ConceitosDecV4 } from "../motor/index.ts";
import { CONFIG_FALA_ASSISTIR } from "../motor/digibrain/constantes.ts";
import { conferir } from "./digibrain_modular_gabarito.ts";

type Dict = Record<string, any>;
const lerGz = (rel: string): any => JSON.parse(gunzipSync(readFileSync(new URL(`./gabaritos/${rel}`, import.meta.url))).toString("utf8"));
const gab = lerGz("decodificador_v4_python.json.gz") as {
  catalogo_assistir: string[]; config_fala_assistir: Dict;
  gabaritos: { arquivo: string; vida: number; decisoes: ConceitosDecV4[] }[];
  vidas: { semente: number; dono: string; pares: { anterior: Dict | null; motivo: Dict; dec: ConceitosDecV4 }[] }[];
  sinteticos: { base: Dict; anterior: Dict; casos: { sinais: Dict; dec: ConceitosDecV4 }[] };
};
const S = 1024;
const clone = <T>(x: T): T => JSON.parse(JSON.stringify(x)) as T;

describe("dec-v4: paridade com o Python", () => {
  test("a config e o catalogo", () => {
    expect(clone(CONFIG_FALA_ASSISTIR)).toEqual(gab.config_fala_assistir);
    expect([...CATALOGO_ASSISTIR]).toEqual(gab.catalogo_assistir);
    expect(VERSAO_DECODIFICADOR_V4).toBe("dec-v4");
  });
  test("toda decisao das vidas dos gabaritos do enjoo e da TV no jogo", () => {
    const cache: Record<string, Dict> = {};
    let n = 0, olhando = 0;
    for (const g of gab.gabaritos) {
      const arq = (cache[g.arquivo] ??= lerGz(g.arquivo));
      const ms = (arq["vidas"][g.vida]["decisoes"] as Dict[]).map(d => d["motivo"] as Dict);
      expect(ms.length).toBe(g.decisoes.length);
      ms.forEach((m, k) => {
        const r = decodificarV4(m, k ? ms[k - 1]! : null, S);
        conferir(`${g.arquivo} vida ${g.vida} k=${k}`, r, g.decisoes[k]);
        if (r.assistir !== null) olhando++;
        n++;
      });
    }
    expect(n).toBeGreaterThan(3000);
    expect(olhando).toBeGreaterThan(20);
  });
  test("os pares das vidas curtas da GV3b", () => {
    let n = 0;
    for (const v of gab.vidas) for (const p of v.pares) { conferir(`${v.semente}/${v.dono} k=${p.motivo["k"]}`, decodificarV4(p.motivo, p.anterior, S), p.dec); n++; }
    expect(n).toBeGreaterThan(100);
  });
  test("os casos sinteticos (todo ramo da conta) e todas as intencoes", () => {
    const { base, anterior, casos } = gab.sinteticos;
    const vistas = new Set<string>();
    for (const c of casos) {
      const m = clone(base), a = clone(anterior), s = c.sinais;
      m["olhar"]["agrado"] = s["agrado"]; m["olhar"]["agrado_efetivo"] = s["agrado_efetivo"]; m["olhar"]["enjoo"] = s["enjoo"];
      m["afeto"]["urgencias"]["tedio"] = s["tedio"]; m["afeto"]["urgencias"]["susto"] = s["susto"]; a["afeto"]["urgencias"]["susto"] = s["susto_anterior"];
      m["gestos"] = s["tapa"] ? [["tapa", 0]] : [];
      const r = decodificarV4(m, a, S);
      conferir(`sintetico ${JSON.stringify(s)}`, r, c.dec);
      vistas.add(String(r.assistir!.intencao));
    }
    expect([...vistas].sort()).toEqual(["chato", "gostei", "null", "o_que_e", "susto"]);
  });
});

describe("dec-v4: so le e falha alto", () => {
  const p = gab.vidas.flatMap(v => v.pares).find(x => x.motivo["olhar"]["olhava"] !== null && x.anterior !== null)!;
  test("nao muda o motivo", () => {
    const m = clone(p.motivo), a = clone(p.anterior);
    decodificarV4(m, a, S);
    expect(m).toEqual(p.motivo);
    expect(a).toEqual(p.anterior);
  });
  test("sem o olhar com o enjoo, sem o anterior certo, ou com o olhar no dec-v1", () => {
    const sem = clone(p.motivo); delete sem["olhar"];
    expect(() => decodificarV4(sem, p.anterior, S)).toThrow(/pede o motivo com o olhar/);
    const semEnjoo = clone(p.motivo); delete semEnjoo["olhar"]["enjoo"];
    expect(() => decodificarV4(semEnjoo, p.anterior, S)).toThrow(/olhar com o enjoo/);
    expect(() => decodificarV4(p.motivo, null, S)).toThrow(/pede o motivo anterior/);
    const ant = clone(p.anterior!); ant["k"] = (ant["k"] as number) - 1;
    expect(() => decodificarV4(p.motivo, ant, S)).toThrow(/motivo anterior e o da decisao/);
    const comOlhar = gab.vidas.flatMap(v => v.pares).find(x => (x.motivo["unidades"] as Dict[]).some(u => u["chave"][0] === "olhar"))!;
    expect(() => decodificar(comOlhar.motivo, S)).toThrow(/comportamento desconhecido/);
  });
});
