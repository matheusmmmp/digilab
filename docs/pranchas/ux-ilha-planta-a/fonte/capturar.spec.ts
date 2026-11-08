/* Copiado para web/app/e2e_capturas/ so na hora de rodar (playwright.capturas.config.ts) e apagado depois: as capturas da planta A na
   ilha 3D (docs/pranchas/ux-ilha-planta-a/), o antes e o depois, a 1920 x 950 e a 390 x 844, nas peles Vidro e Militar (xcom).
   O rotulo (CAP_ROTULO: antes ou depois) escolhe a pasta: D:\Trab\digilab\capturas_ux_ilha_planta_a\<rotulo>\. O save e o "dia" da bola
   (e2e_capturas/saves_bola.json), com o relogio parado. A camera de desenvolvimento (?cameradev=1, cameraDev.ts) leva a vista a cada
   ponto da planta; a primeira cena e a da tela Pet, seguindo o pet. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, unknown> = JSON.parse(readFileSync(new URL("./saves_bola.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const ROTULO = process.env.CAP_ROTULO ?? "antes";
const SAIDA = join("D:\\Trab\\digilab\\capturas_ux_ilha_planta_a", ROTULO);
/* as cenas: o nome, o ponto olhado (celulas) e a orbita; null e a camera do jogo, atras do pet */
const CENAS: { nome: string; alvo: [number, number] | null; orbita?: { zoom?: number; giro?: number; inclina?: number } }[] = [
  { nome: "1_inicio", alvo: null },
  { nome: "2_praca", alvo: [31, 17] },
  { nome: "3_portao", alvo: [31, 3], orbita: { zoom: 1.2 } },
  { nome: "4_barraca", alvo: [45, 12], orbita: { zoom: 1.2 } },
  { nome: "5_cais", alvo: [36, 26], orbita: { zoom: 1.2 } },
  { nome: "6_nordeste", alvo: [57, 2], orbita: { zoom: 1.3 } },
  { nome: "7_lar", alvo: [9, 14], orbita: { zoom: 1.4 } },
  { nome: "8_alto", alvo: [31, 12], orbita: { zoom: 2.4, inclina: 0.45 } },
];

for (const pele of ["vidro", "xcom"]) for (const [w, h] of [[1920, 950], [390, 844]] as const) {
  const nomePele = pele === "xcom" ? "militar" : "vidro";
  test(`planta A (${ROTULO}) ${nomePele} ${w}`, async ({ browser }) => {
    test.setTimeout(240_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1, colorScheme: "light" });
    await ctx.addInitScript(() => {
      const orig = window.setInterval.bind(window);
      (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
    });
    const page: Page = await ctx.newPage();
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(e.message));
    await page.goto("/Assets/digilab_atlas_up.json");
    await page.evaluate(([chave, s]) => {
      localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
      localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
      localStorage.setItem(chave, s);
    }, [CHAVE, JSON.stringify(SAVES.dia)] as const);
    await page.goto(APP + `?cameradev=1&pele=${pele}#/pet`);
    await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
    await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
    await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 30_000 });
    await page.waitForTimeout(1500);
    mkdirSync(SAIDA, { recursive: true });
    for (const c of CENAS) {
      if (c.alvo) await page.evaluate(([a, o]) => (window as any).__camera.ir(a, o), [c.alvo, c.orbita ?? {}] as const);
      await page.mouse.move(2, h - 2);
      await page.waitForTimeout(900);
      await page.screenshot({ path: join(SAIDA, `${c.nome}_${w}_${nomePele}.png`) });
    }
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
