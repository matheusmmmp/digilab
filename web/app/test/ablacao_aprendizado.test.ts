/* EVIDENCIA A2 (docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md): o harness da ablacao do aprendizado. So sementes de teste (101...505) e vidas
   curtas: o braco B zera o aprendido antes de cada leitura do impulso e nenhuma unidade o le; o A le; as vidas sao deterministas; a faixa e o
   tipo desconhecido falham alto; o script grava o JSON. Nao roda a run. */
import { describe, expect, test } from "vitest";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { VERSAO_PET } from "../motor/constantes.ts";
import { DONOS, grupoDoTipo, nascer, paraOJogo, sementesDe, todas, vida, zerarAntesDeCadaDecisao } from "../scripts/ablacao_aprendizado.ts";

const SCRIPT = fileURLToPath(new URL("../scripts/ablacao_aprendizado.ts", import.meta.url));

describe("o harness da A2", () => {
  test("o ovo e o do jogo, com o modular e o P1 e o P2 ligados", () => {
    const m = nascer(101);
    expect(m.versao).toBe(VERSAO_PET);
    expect(m.cerebroAtual).toBe("modular");
  });
  test("o braco B: o involucro zera o H, o desfecho e o andar antes de cada leitura, no lugar", () => {
    const m = nascer(202);
    const H = m.lab!.plast.H;
    const z = zerarAntesDeCadaDecisao(m);
    m.avancar(300);
    expect(z.leituras()).toBe(m.lab!.motivos.length);
    expect(m.lab!.plast.H).toBe(H);                                        // o mesmo objeto: zerado no lugar, nao trocado
    for (const mo of m.lab!.motivos as { unidades: { termos: Record<string, number> }[] }[])
      for (const u of mo.unidades) { expect(u.termos["incentivo"] ?? 0).toBe(0); expect(u.termos["habito"] ?? 0).toBe(0); }
  });
  test("as vidas de 1 dia: B sem aprendido em unidade nenhuma, A com, e cada uma igual em duas execucoes (a vida confere)", () => {
    const vs = todas([101], 1);
    expect(vs).toHaveLength(DONOS.length * 2);
    for (const v of vs) {
      expect(v.decisoes).toBeGreaterThan(0);
      if (v.braco === "B") { expect(v.unidades_com_aprendido).toBe(0); expect(v.leituras_zeradas).toBe(v.decisoes); }
      else expect(v.leituras_zeradas).toBeNull();
    }
    expect(vs.some(v => v.braco === "A" && v.unidades_com_aprendido > 0)).toBe(true);
    expect(vida(101, "relapso", "B", 1)).toEqual(vs.find(v => v.dono === "relapso" && v.braco === "B"));
  }, 120_000);
  test("os tres donos dao vidas diferentes (o retorno vira acariciar e tapa, AB-2b)", () => {
    expect(paraOJogo("elogiar")).toBe("acariciar");
    expect(paraOJogo("repreender")).toBe("tapa");
    expect(paraOJogo("limpar")).toBe("limpar");
    const logs = DONOS.map(d => vida(303, d, "A", 1).log_sha256);
    expect(new Set(logs).size).toBe(DONOS.length);
  }, 120_000);
  test("a faixa e o tipo desconhecido falham alto", () => {
    expect(sementesDe(98101, 200, false)).toHaveLength(200);
    expect(() => sementesDe(98400, 200, false)).toThrow(/fora da faixa/);
    expect(() => sementesDe(101, 2, false)).toThrow(/fora da faixa/);
    expect(() => sementesDe(98101, 1, true)).toThrow(/fora da faixa/);
    expect(grupoDoTipo(null)).toBe("sem_objeto");
    expect(grupoDoTipo("racao")).toBe("comida");
    expect(() => grupoDoTipo("tela")).toThrow(/desconhecido/);
  });
  test("o script grava o JSON (semente 101, 1 dia)", () => {
    const pasta = mkdtempSync(join(tmpdir(), "a2-")), saida = join(pasta, "medidas.json");
    try {
      execFileSync(process.execPath, [SCRIPT, "--primeira", "101", "--k", "1", "--dias", "1", "--teste", "--saida", saida]);
      const r = JSON.parse(readFileSync(saida, "utf8"));
      expect([r.versao_pet, r.dias, r.teste, r.node]).toEqual([VERSAO_PET, 1, true, process.version]);
      expect(r.vidas).toHaveLength(DONOS.length * 2);
    } finally { rmSync(pasta, { recursive: true, force: true }); }
  }, 120_000);
});
