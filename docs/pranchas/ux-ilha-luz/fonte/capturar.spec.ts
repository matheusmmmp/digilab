/* Copiado para web/app/e2e_capturas/luz.spec.ts so na hora de rodar (playwright.capturas.config.ts) e apagado depois: as capturas da
   prancha da hierarquia de luz (docs/pranchas/ux-ilha-luz/). Vem do capturar.spec.ts da planta A, com o mapa (CAP_MAPA: ilha ou digital)
   e a proposta (CAP_LUZ: a, b, c ou vazio para hoje) no endereco, 4 s de espera (o atlas do pet) e um erro de shader no console falhando
   o teste. A pasta: D:\Trab\digilab\capturas_ux_ilha_luz\<CAP_ROTULO>\. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, unknown> = JSON.parse(readFileSync(new URL("./saves_bola.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const ROTULO = process.env.CAP_ROTULO ?? "hoje", MAPA = process.env.CAP_MAPA ?? "ilha", LUZ = process.env.CAP_LUZ ?? "";
const SAIDA = join("D:\\Trab\\digilab\\capturas_ux_ilha_luz", ROTULO);
/* as cenas: o nome, o ponto olhado (celulas) e a orbita; null e a camera do jogo, atras do pet */
const CENAS: { nome: string; alvo: [number, number] | null; orbita?: { zoom?: number; giro?: number; inclina?: number } }[] = [
  { nome: "1_inicio", alvo: null },
  { nome: "2_praca", alvo: [31, 17] },
  { nome: "3_portao", alvo: [31, 3], orbita: { zoom: 1.2 } },
  { nome: "4_barraca", alvo: [45, 12], orbita: { zoom: 1.2 } },
  { nome: "5_cais", alvo: [36, 26], orbita: { zoom: 1.2 } },
  { nome: "6_nordeste", alvo: [57, 2], orbita: { zoom: 1.3 } },
  { nome: "6a_carro_oeste", alvo: [-2, 22], orbita: { zoom: 1.3, giro: Math.PI / 2 } },
  { nome: "6b_geladeira_cais", alvo: [42, 27], orbita: { zoom: 1.3 } },
  { nome: "6c_trilho_leste", alvo: [62, 23], orbita: { zoom: 1.3, giro: -Math.PI / 2 } },
  { nome: "7_lar", alvo: [9, 14], orbita: { zoom: 1.4 } },
  { nome: "8_alto", alvo: [31, 12], orbita: { zoom: 2.4, inclina: 0.45 } },
  /* o fim da ilha: o zoom mais longe (ZOOM_MAX, orbita.ts) e a camera girada para cada lado, rente ao chao e de cima */
  { nome: "9_longe", alvo: [31, 15], orbita: { zoom: 2.4, giro: 0, inclina: 0 } },
  { nome: "10_girada_oeste", alvo: [6, 14], orbita: { zoom: 2.4, giro: Math.PI / 2, inclina: -0.25 } },
  { nome: "11_girada_sul", alvo: [31, 4], orbita: { zoom: 2.4, giro: Math.PI, inclina: -0.25 } },
  { nome: "12_girada_leste", alvo: [58, 15], orbita: { zoom: 2.4, giro: -Math.PI / 2, inclina: -0.25 } },
  { nome: "13_quina_alta", alvo: [62, -6], orbita: { zoom: 2.4, giro: -Math.PI * 0.75, inclina: 0.6 } },
];
const SO = process.env.CAP_CENAS?.split(",");

for (const pele of ["vidro", "xcom"]) for (const [w, h] of [[1920, 950], [390, 844]] as const) {
  const nomePele = pele === "xcom" ? "militar" : "vidro";
  test(`luz (${ROTULO}) ${nomePele} ${w}`, async ({ browser }) => {
    test.setTimeout(240_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1, colorScheme: "light" });
    await ctx.addInitScript(() => {
      const orig = window.setInterval.bind(window);
      (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
    });
    const page: Page = await ctx.newPage();
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(e.message));
    page.on("console", m => { if (/Shader Error|WebGLProgram/.test(m.text())) erros.push(m.text().slice(0, 300)); });
    await page.goto("/Assets/digilab_atlas_up.json");
    await page.evaluate(([chave, s]) => {
      localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
      localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
      localStorage.setItem(chave, s);
    }, [CHAVE, JSON.stringify(SAVES.dia)] as const);
    await page.goto(APP + `?cameradev=1&mapa=${MAPA}${LUZ ? "&luz=" + LUZ : ""}&pele=${pele}#/pet`);
    const PELES = process.env.CAP_PELES?.split(",");
    if (PELES && !PELES.includes(nomePele)) { await ctx.close(); return; }
    await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
    await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
    await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 30_000 });
    await page.waitForTimeout(4000);
    mkdirSync(SAIDA, { recursive: true });
    for (const c of CENAS.filter(c => !SO || SO.includes(c.nome))) {
      if (c.alvo) await page.evaluate(([a, o]) => (window as any).__camera.ir(a, o), [c.alvo, c.orbita ?? {}] as const);
      await page.mouse.move(2, h - 2);
      await page.waitForTimeout(900);
      await page.screenshot({ path: join(SAIDA, `${c.nome}_${w}_${nomePele}.png`) });
    }
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
