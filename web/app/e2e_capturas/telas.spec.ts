/* Capturas das telas para o gate "o jogo sai igual" (docs/TAREFA_V2_FRONT_REACT.md): cada aba, as Configurações e o Pet de um
   pet v11, em 390 e 1280 px, comparadas pixel a pixel com a referência. A referência sai do build de antes da mudança
   (npm run capturas -- --update-snapshots); o build de depois compara com ela (npm run capturas). O relógio da página é falso e
   pausado (page.clock.pauseAt), para o tempo do jogo e as animações não mexerem entre uma captura e outra. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; log: unknown[]; versao?: number }> = JSON.parse(readFileSync(new URL("../e2e/saves.json", import.meta.url), "utf8"));
const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* o mesmo pet v11 do teste do DigiBrain (e2e/jogo.spec.ts) */
const SAVE_V11 = { semente: 4242, versao: 11, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "d", "alimentar"], [840, "t", 60]] };
const TELAS: [string, string, object][] = [
  ["pet-estado", "#/pet/estado", SAVES.v3], ["crescer-treinar", "#/crescer/treinar", SAVES.v3], ["crescer-aprend", "#/crescer/aprend", SAVES.v3],
  ["crescer-evolucao", "#/crescer/evolucao", SAVES.v3], ["crescer-itens", "#/crescer/itens", SAVES.v3], ["lutar-arena", "#/lutar/arena", SAVES.v3],
  ["lutar-campanha", "#/lutar/campanha", SAVES.v3], ["lutar-fronteira", "#/lutar/fronteira", SAVES.v3], ["lutar-medalhas", "#/lutar/medalhas", SAVES.v3],
  ["diario-registro", "#/diario/registro", SAVES.v3], ["diario-catalogo", "#/diario/catalogo", SAVES.v3], ["diario-cenarios", "#/diario/cenarios", SAVES.v3],
  ["conversar", "#/conversar/chat", SAVES.v3], ["config", "#/config", SAVES.v3], ["pet-v11", "#/pet/estado", SAVE_V11],
];

/** semeia o save por uma página da mesma origem que não é o app (como em e2e/jogo.spec.ts) */
async function semear(page: Page, save: object): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "5"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(save)] as const);
}

for (const [largura, altura] of [[390, 844], [1280, 800]]) {
  for (const [nome, rota, save] of TELAS) {
    test(`${nome} em ${largura} px`, async ({ page }) => {
      await page.setViewportSize({ width: largura, height: altura });
      await semear(page, save);
      const T0 = new Date("2026-10-19T12:00:00Z").getTime();
      await page.clock.install({ time: T0 });
      await page.clock.pauseAt(T0 + 1000);           /* parado desde antes de abrir: o tempo do jogo só anda com runFor */
      const erros: string[] = [];
      page.on("pageerror", e => erros.push(e.message));
      await page.goto(APP + rota);
      await page.evaluate(() => document.fonts.ready);
      await page.clock.runFor(1000);
      await page.waitForLoadState("networkidle");
      await expect(page).toHaveScreenshot(`${nome}_${largura}.png`, { fullPage: true, animations: "disabled", caret: "hide", threshold: 0, maxDiffPixels: 4 });   /* 4 px: o ruído medido entre duas rodadas do mesmo build (2 px no Pet de 390) */
      expect(erros).toEqual([]);
    });
  }
}
