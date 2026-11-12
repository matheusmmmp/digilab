/* EQUILIBRIO_CUIDADO, E0 (docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md): a bancada roda e grava o artefato num caso pequeno, 1 semente de
   teste (101) e 1 dia, nas duas versoes; a semente fora das faixas falha alto. Nao roda o retrato (o e0_rodar.ts). */
import { describe, expect, test } from "vitest";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { TPD, VERSAO_GRUPO, VERSAO_PET } from "../motor/constantes.ts";
import { vida } from "../scripts/equilibrio_cuidado/e0.ts";

const SCRIPT = fileURLToPath(new URL("../scripts/equilibrio_cuidado/e0.ts", import.meta.url));

describe("a bancada do E0", () => {
  test("o script grava o JSON de uma vida (o pet, o atento, a semente 101, 1 dia)", () => {
    const pasta = mkdtempSync(join(tmpdir(), "e0-")), saida = join(pasta, "vida.json");
    try {
      execFileSync(process.execPath, [SCRIPT, "--versao", "pet", "--dono", "atento", "--semente", "101", "--dias", "1", "--teste", "--saida", saida]);
      const r = JSON.parse(readFileSync(saida, "utf8"));
      expect([r.versao, r.numero_versao, r.dono, r.semente, r.dias]).toEqual(["pet", VERSAO_PET, "atento", 101, 1]);
      expect(r.pets).toHaveLength(1);
      const p = r.pets[0];
      expect(p.celulas.reduce((a: number, c: { minutos: number }) => a + c.minutos, 0)).toBe(TPD);
      expect(p.celulas[0].estagio).toBe("In-Training");
      expect(p.saude_fim_do_dia).toHaveLength(1);
      expect(p.morte).toBeNull();
      expect(r.tamer.bits_total).toBeGreaterThan(0);
    } finally { rmSync(pasta, { recursive: true, force: true }); }
  }, 120_000);
  test("o grupo tem os dois pets, e a vida e determinista", () => {
    const a = vida("grupo", "medio", 202, 1, true), b = vida("grupo", "medio", 202, 1, true);
    expect(a.numero_versao).toBe(VERSAO_GRUPO);
    expect(a.pets.map(p => p.ident)).toEqual(["A", "B"]);
    expect(JSON.stringify(a)).toBe(JSON.stringify(b));
  }, 120_000);
  test("a semente fora da faixa falha alto", () => {
    expect(() => vida("pet", "atento", 101)).toThrow(/calibracao/);
    expect(() => vida("pet", "atento", 94101)).toThrow(/calibracao/);
    expect(() => vida("pet", "atento", 93101, 1, true)).toThrow(/teste/);
  });
});
