/* Os quadros do GIF do empurrao (docs/TAREFA_V3_LUTA_EMPURRAO.md, etapa 5): uma luta de um Rookie v18 na Arena, com os clipes do UP, gravada
   quadro a quadro do canvas do palco, para o Matheus aprovar antes do PR de codigo. So roda com DIGILAB_GIF_EMPURRAO=<pasta> (os PNG vao para
   la; o GIF sai deles por fora). Sem a variavel, o teste e pulado: nao e uma referencia das capturas. */
import { expect, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const PASTA = process.env.DIGILAB_GIF_EMPURRAO ?? "";
const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* o Rookie v18 (o mesmo registro do Rookie v13 de e2e/luta_layout.spec.ts, na versao do empurrao) */
const SAVE = { semente: 101, versao: 18, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
const SEGUNDOS = Number(process.env.DIGILAB_GIF_SEGUNDOS ?? 40), INTERVALO_MS = 60;
/* o rival: o card adulto de indice DIGILAB_GIF_RIVAL na ordem de RIVAIS_ADULTOS (6 = o vigia, que prepara o pesado de perto e derruba
   muito; o bot padrao da Arena so troca golpes rapidos com o Rookie, e o empurrao nao aparece) */
const RIVAL = Number(process.env.DIGILAB_GIF_RIVAL ?? 6);

test("os quadros do GIF do empurrao (v18)", async ({ page }) => {
  test.skip(!PASTA, "so com DIGILAB_GIF_EMPURRAO=<pasta>");
  test.setTimeout((SEGUNDOS + 120) * 1000);
  mkdirSync(PASTA, { recursive: true });
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE), JSON.stringify(TAMER)] as const);
  await page.goto(`${APP}?clipes_up=1#/lutar/arena`);
  if (RIVAL >= 2) await page.locator(".rivais-mais").click();
  await page.locator(".rival-card--adulto").nth(RIVAL).click();
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
  const cv = page.locator(".arena-cv");
  await expect(cv).toBeVisible();
  const fim = Date.now() + SEGUNDOS * 1000;
  for (let i = 0; Date.now() < fim; i++) {
    await cv.screenshot({ path: join(PASTA, `q${String(i).padStart(4, "0")}.png`) });
    await page.waitForTimeout(INTERVALO_MS);
  }
});
