/* P4, etapa 0 (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 4): o gabarito do lado TS do que a P4 vai tocar, gravado com o codigo da main
   ANTES de qualquer mudanca. O G2 do TS:
     - os gabaritos do Python que o mundo.test.ts e o lobos_v11.test.ts leem (o G-PAR do mundo e do v11) ficam com o sha256 de hoje: com
       eles fixos e esses testes passando, o mundo.ts e o lobos.ts do v11 saem iguais;
     - o POC-01a: os hashes das tres sementes do e2e (artifacts_v2_world_poc/e2e.json), refeitos aqui;
     - o POC-02: os hashes das mesmas sementes com o corpo ligado, 3000 ticks.
   Com GRAVAR_P4=1, grava test/gabaritos/p4_etapa0_ts.json (so com o codigo de antes); sem, confere. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { Simulacao } from "../poc/mundo3d/simulacao.ts";

const ARQUIVO = new URL("./gabaritos/p4_etapa0_ts.json", import.meta.url);
const PINADOS = ["./gabaritos/mundo_python.json", "./gabaritos/lobos_python.json"];
const SEMENTES = [101, 202, 303];
const TICKS_POC02 = 3000;
const E2E_POC01 = JSON.parse(readFileSync(new URL("../../../artifacts_v2_world_poc/e2e.json", import.meta.url), "utf8")) as {
  M5_chrome_node: { semente: number; ticks: number; hash: string }[];
};

interface Gabarito {
  arquivos: Record<string, string>;
  poc01a: { semente: number; ticks: number; hash: string }[];
  poc02: { semente: number; ticks: number; hash: string }[];
}

const sha = (rel: string): string => createHash("sha256").update(readFileSync(new URL(rel, import.meta.url))).digest("hex");

function poc(semente: number, ticks: number, corpo: boolean): string {
  const s = new Simulacao(semente, undefined, { corpo });
  s.avancar(ticks);
  return s.hash();
}

function gerar(): Gabarito {
  return {
    arquivos: Object.fromEntries(PINADOS.map(p => [p, sha(p)])),
    poc01a: E2E_POC01.M5_chrome_node.map(c => ({ semente: c.semente, ticks: c.ticks, hash: poc(c.semente, c.ticks, false) })),
    poc02: SEMENTES.map(s => ({ semente: s, ticks: TICKS_POC02, hash: poc(s, TICKS_POC02, true) })),
  };
}

if (process.env.GRAVAR_P4 === "1") {
  writeFileSync(ARQUIVO, JSON.stringify(gerar(), null, 1) + "\n", "utf8");
}

const G = JSON.parse(readFileSync(ARQUIVO, "utf8")) as Gabarito;

describe("G2 da P4 (etapa 0): o lado TS de hoje", () => {
  test("os gabaritos do Python que o G-PAR do mundo e do v11 leem continuam os de hoje", () => {
    expect(Object.keys(G.arquivos)).toEqual(PINADOS);
    for (const p of PINADOS) expect(sha(p), p).toBe(G.arquivos[p]);
  });
  test("o POC-01a: as tres sementes do e2e, com o hash do e2e", () => {
    expect(G.poc01a.map(c => c.semente)).toEqual(SEMENTES);
    expect(G.poc01a).toEqual(E2E_POC01.M5_chrome_node.map(c => ({ semente: c.semente, ticks: c.ticks, hash: c.hash })));
  });
  for (const c of G.poc01a) {
    test(`POC-01a, semente ${c.semente}: ${c.ticks} ticks`, () => {
      expect(poc(c.semente, c.ticks, false)).toBe(c.hash);
    });
  }
  for (const c of G.poc02) {
    test(`POC-02 (o corpo ligado), semente ${c.semente}: ${c.ticks} ticks`, () => {
      expect(poc(c.semente, c.ticks, true)).toBe(c.hash);
    });
  }
});
