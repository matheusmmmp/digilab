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
