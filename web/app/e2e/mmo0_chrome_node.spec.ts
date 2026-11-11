/* MMO0 (docs/PLANO_V3_MMO.md, secao 12): a guarda da medida Chrome x Node. Duas vidas roteirizadas (scripts/mmo0/vida.ts) gravadas no
   Chrome do e2e e conferidas no Node (scripts/mmo0/conferir.ts). A medida inteira, com as 20 vidas, e o scripts/medir_mmo0.ts.
   O que a guarda exige e o que a medida achou (scripts/medicoes/mmo0_chrome_node.json): o Node aceita o registro do Chrome, cada luta da o
   mesmo resultado, o Node grava o mesmo registro e o que difere na assinatura e so numero, no ultimo bit. A assinatura igual nao e
   exigida: o Chrome e o Node diferem no ultimo bit de exp e log (web/app/CLAUDE.md). */
import { expect, test } from "@playwright/test";
import { empacotar } from "../scripts/mmo0/empacotar.ts";
import { conferir } from "../scripts/mmo0/conferir.ts";
import type { Vida } from "../scripts/mmo0/vida.ts";

/** o teto da diferenca relativa de um numero da assinatura: o ultimo bit e da ordem de 1e-16 (PROPOSTO, SEM FONTE) */
const TETO_ULTIMO_BIT = 1e-12;

let pacote = "";
test.beforeAll(async () => { pacote = await empacotar(); });

for (const [semente, cerebro] of [[101, "modular"], [111, "a"]] as const) {
  test(`MMO0: a vida ${semente} (${cerebro}) gravada no Chrome reproduz no Node com as mesmas lutas`, async ({ page }) => {
    test.setTimeout(180_000);
    await page.goto("about:blank");
    await page.addScriptTag({ path: pacote });
    const v = await page.evaluate(([s, c]) => (globalThis as unknown as { MMO0: { viver: (s: number, c: string) => unknown } }).MMO0.viver(s, c),
      [semente, cerebro] as const) as Vida;
    const r = conferir(v);
    expect(r.lutas).toBeGreaterThan(0);
    expect(r.erro).toBeNull();
    expect(r.aceito).toBe(true);
    expect(r.lutasDiferentes).toBe(0);
    expect(r.mesmoRegistro).toBe(true);
    expect(r.assinaturaNaoNumericos).toBe(0);
    expect(r.assinaturaMaiorDiferencaRelativa).toBeLessThan(TETO_ULTIMO_BIT);
  });
}
