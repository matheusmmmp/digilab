/* As capturas das reacoes de rosto na ilha com o atlas de clipes de verdade (docs/TAREFA_V3_SPRITES_REACOES.md, R-rosto-jogo), para o Matheus aprovar.
   So roda com DIGILAB_CAPTURAS_ROSTO=1 e grava fora do git (sao quadros do UP), em DIGILAB_CAPTURAS_ROSTO_PASTA (padrao:
   D:\Trab\digilab\remaster\geracao\reacoes\rosto\capturas_jogo). O pet e o do save "ocioso" (saves_cena.json), com o relogio do jogo parado. As reacoes saem
   do que o dono faz pela tela, como no jogo: o Tapa (Triste), dois Tapas (Medo) e o Carinho. Para ver o Digimon de cada captura, a rota troca, so aqui, o
   sprite de todas as formas do atlas de clipes pelo dele (o atlas no disco nao muda). Por Digimon, reacao e largura: a tela inteira e dois recortes em
   volta do pet, um logo depois do aparecimento do quadro e outro um pouco depois (o movimento de 1 texel). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_cena.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAIDA = process.env.DIGILAB_CAPTURAS_ROSTO_PASTA ?? "D:\\Trab\\digilab\\remaster\\geracao\\reacoes\\rosto\\capturas_jogo";
const ATLAS_CLIPES = join(REPO, "..", "Assets", "digilab_atlas_up_clipes.json");
const TELAS: [number, number][] = [[390, 844], [1280, 800]];
const DIGIMON = ["Agumon", "Gabumon"];
/* a reacao, e o que o dono faz para chegar nela (o rotulo do botao da tela do Pet) */
const REACOES: { reacao: string; acoes: string[] }[] = [
  { reacao: "Triste", acoes: ["Tapa"] },
  { reacao: "Medo", acoes: ["Tapa", "Tapa"] },
  { reacao: "Carinho", acoes: ["Carinho"] },
];
test.skip(!process.env.DIGILAB_CAPTURAS_ROSTO, "so com DIGILAB_CAPTURAS_ROSTO=1");

type SpriteClipes = { digimon: string; clipes: Record<string, unknown> };
const ehForma = (k: string) => !k.startsWith("npc_") && !k.startsWith("bot_");

async function agir(page: Page, rotulo: string): Promise<void> {
  const bt = page.getByRole("button", { name: new RegExp(`^${rotulo}`) }).first();
  if (!(await bt.isVisible())) await page.getByRole("button", { name: /^Mais/ }).click();
  await page.getByRole("button", { name: new RegExp(`^${rotulo}`) }).first().click();
}

for (const [w, h] of TELAS) {
  for (const digimon of DIGIMON) {
    for (const { reacao, acoes } of REACOES) {
      test(`captura: ${reacao} do ${digimon} em ${w} px`, async ({ browser }) => {
        test.setTimeout(120_000);
        const real = JSON.parse(readFileSync(ATLAS_CLIPES, "utf8")) as { sprites: Record<string, SpriteClipes> };
        const alvo = Object.values(real.sprites).find(s => s.digimon === digimon);
        if (!alvo) throw new Error("Digimon fora do atlas de clipes: " + digimon);
        if (!alvo.clipes[reacao]) throw new Error(`o atlas de clipes nao tem ${reacao} do ${digimon}`);
        const trocado = { ...real, sprites: Object.fromEntries(Object.entries(real.sprites).map(([k, s]) => [k, ehForma(k) ? alvo : s])) };
        const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1 });
        await ctx.route(/\/Assets\/digilab_atlas_up_clipes\.json/, r => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(trocado) }));
        /* o relogio do jogo parado (src/tempo.ts, o unico setInterval de 100 ms): o motor fica onde esta */
        await ctx.addInitScript(() => {
          const orig = window.setInterval.bind(window);
          (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
        });
        const page: Page = await ctx.newPage();
        await page.goto("/Assets/digilab_atlas_up.json");
        await page.evaluate(([chave, s]) => {
          localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
          localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
          localStorage.setItem(chave, s);
        }, [CHAVE, JSON.stringify(SAVES.ocioso)] as const);
        await page.goto(APP + "#/pet/estado");
        await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
        const lerRosto = () => page.evaluate(() => (window as any).__digilab.reacaoRosto());
        expect(await lerRosto(), "sem a acao do dono, sem reacao").toBeNull();
        for (const a of acoes) await agir(page, a);
        await expect.poll(lerRosto, { timeout: 15_000, message: `o clipe ${reacao} no corpo` }).toBe(reacao);
        mkdirSync(SAIDA, { recursive: true });
        const nome = `${digimon}_${reacao}_${w}`;
        await page.screenshot({ path: join(SAIDA, `${nome}.png`) });
        const ret = await page.evaluate(() => (window as any).__digilab.cena().ret as { x: number; y: number; w: number; h: number });
        const cena = (await page.locator(".pet-cena").boundingBox())!, folga = Math.max(ret.w, ret.h) * 0.6;
        const clip = { x: Math.max(0, cena.x + ret.x - folga), y: Math.max(0, cena.y + ret.y - folga), width: ret.w + 2 * folga, height: ret.h + 2 * folga };
        for (let i = 0; i < 2; i++) {
          expect(await lerRosto()).toBe(reacao);
          await page.screenshot({ path: join(SAIDA, `${nome}_recorte_${i + 1}.png`), clip, scale: "css" });
          await page.waitForTimeout(500);
        }
        writeFileSync(join(SAIDA, `${nome}.txt`), `o pet do save "ocioso" (saves_cena.json) com os quadros de ${digimon} em todas as formas; acoes do dono: ${acoes.join(", ")}; ${w} x ${h} px; relogio parado\n`);
        await ctx.close();
      });
    }
  }
}
