/* Capturas do laboratorio do modular (docs/TAREFA_V3_LAB_MODULAR.md, LM5b): so rodam com DIGILAB_CAPTURAS_LAB=<pasta> (sem ela, ficam de fora do
   portao de capturas, que compara com referencias). Em 390 e 1280 px, nas peles Vidro (Sci-fi) e Militar, em claro e escuro, com o atlas e a
   ilha 3D de verdade e o relogio parado:
     ajustes_vazio, ajustes_vivo, ajustes_descartar (Ajustes > Laboratorio), pet (a tela Pet com o selo), painel (o DigiBrain do modular).
   O pet de hoje e o pet de teste (uma vida de 3 dias, a racao posta, como test/pet_lab.test.ts) sao semeados no localStorage. */
import { test, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";
import { Motor, TPD, petDeTeste } from "../motor/index.ts";
import { textoSave } from "../src/save.ts";

const PASTA = process.env.DIGILAB_CAPTURAS_LAB ?? "";
const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";

function petDeHoje(): string {
  const m = new Motor(9090); m.avancar(600); m.observar("acariciar"); m.avancar(120);
  return textoSave(m);
}
/** o pet de teste com 3 dias de vida (a racao perto e longe, limpeza e carinho), para o painel ter o que mostrar */
function petDeTesteVivo(): string {
  const m = petDeTeste(202);
  for (let p = 0; p < Math.round(3 * TPD / 30); p++) {
    m.avancar(30);
    const mu = m.mundo!;
    if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + (p % 4 === 0 ? 300 : 24))), mu.pet[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
    if (p % 5 === 0) m.observar("acariciar");
  }
  /* segue ate a ultima decisao ter lembranca, intencao em curso e varias barras (o painel mostra tudo); sem achar, fica onde parou */
  for (let i = 0; i < 1500; i++) {
    const l = m.leituraLab();
    if (l && l.lembranca && l.intencao && l.barras.length >= 3 && !l.reflexo) break;
    m.avancar(15);
  }
  return textoSave(m);
}

async function semear(page: Page, comPet: boolean): Promise<void> {
  const hoje = petDeHoje(), teste = comPet ? petDeTesteVivo() : null;
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, h, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, h!); localStorage.setItem(chave + "-lab-ligado", "1");
    if (t) localStorage.setItem(chave + "-lab", t);
  }, [CHAVE, hoje, teste] as const);
}
async function abrir(page: Page, pele: string, tema: string, rota: string): Promise<void> {
  await page.goto("about:blank");
  await page.goto(`${APP}?pele=${pele}&tema=${tema}${rota}`);
  await page.addStyleTag({ content: ".app > .aviso, .avisos > .aviso{display:none}" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => !document.querySelector(".pet-cena") || !!document.querySelector(".pet-cena .cena-sala") || !!document.querySelector(".pet-cena .cena3d[data-pronto]"));
  await page.clock.runFor(1000);
  await page.waitForTimeout(500);
}
async function foto(page: Page, nome: string): Promise<void> {
  await page.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => undefined))));
  await page.screenshot({ path: join(PASTA, nome + ".png"), animations: "disabled", caret: "hide" });
}

test.describe("laboratorio do modular", () => {
  test.skip(!PASTA, "so roda com DIGILAB_CAPTURAS_LAB=<pasta>");
  test.beforeAll(() => { if (PASTA) mkdirSync(PASTA, { recursive: true }); });
  for (const [larg, alt] of [[390, 844], [1280, 800]] as const) {
    for (const pele of ["vidro", "xcom"] as const) {
      for (const tema of ["claro", "escuro"] as const) {
        test(`${larg} ${pele} ${tema}`, async ({ page }) => {
          const sufixo = `${larg}_${pele === "xcom" ? "militar" : "vidro"}_${tema}`;
          await page.setViewportSize({ width: larg, height: alt });
          await page.clock.install({ time: new Date("2026-11-03T12:00:00") });

          await semear(page, false);
          await abrir(page, pele, tema, "#/config/laboratorio");
          await foto(page, "ajustes_vazio_" + sufixo);

          await semear(page, true);
          await abrir(page, pele, tema, "#/config/laboratorio");
          await foto(page, "ajustes_vivo_" + sufixo);
          await page.getByRole("button", { name: "Descartar", exact: true }).click();
          await page.waitForTimeout(300);
          await foto(page, "ajustes_descartar_" + sufixo);
          await page.getByRole("button", { name: "Cancelar" }).click();

          await page.getByRole("button", { name: "Abrir", exact: true }).click();
          await page.clock.runFor(1000);
          await page.waitForFunction(() => !!document.querySelector(".pet-cena .cena3d[data-pronto]") || !document.querySelector(".pet-cena"));
          await page.waitForTimeout(500);
          await foto(page, "pet_" + sufixo);
          if (larg < 900) await page.getByRole("button", { name: "Painéis do pet", exact: true }).click();     /* o DigiBrain mora no leque do retrato (< 900 px) */
          await page.getByRole("button", { name: "DigiBrain", exact: true }).click();
          await page.waitForTimeout(400);
          await foto(page, "painel_" + sufixo);
        });
      }
    }
  }
});
