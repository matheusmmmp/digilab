/* Os fundos reais da prancha ux-ilha-a (docs/pranchas/ux-ilha-a/LEIA.md, "Refazer"). Temporario: copiado para web/app/e2e/_cap_ilha_a.spec.ts so na hora de
   rodar, e apagado depois. Tira quadros da Tela Pet com a projecao (cenaPara) da tigela, da bola e do pet e a leitura do DigiBrain em cada um. */
import { expect, test } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const OUT = "D:/Trab/digilab/capturas_ux_ilha_aprovar/prancha_a/fundo";
const VERSAO = Number(process.env.CAP_VERSAO ?? 17);
const SAVE = JSON.parse(readFileSync(fileURLToPath(new URL(process.env.CAP_SAVE ?? "./_save_ilha_a.json", import.meta.url)), "utf8"));

for (const pele of ["vidro", "xcom"]) for (const larg of [1920, 390]) {
  test(`fundo ${pele} ${larg}`, async ({ browser }) => {
    test.setTimeout(200_000);
    mkdirSync(OUT, { recursive: true });
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: larg, height: larg >= 1100 ? 950 : 844 },
      deviceScaleFactor: 1, isMobile: larg < 900, hasTouch: larg < 900 });
    const page = await ctx.newPage();
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(e.message));
    await page.goto("/Assets/digilab_atlas_up.json");
    await page.evaluate(([chave, s]) => {
      localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
      localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
      localStorage.setItem(chave, s);
    }, [CHAVE, JSON.stringify(SAVE)] as const);
    await page.goto(APP + `?pele=${pele}#/pet/estado`);
    await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
    await page.waitForTimeout(Number(process.env.CAP_ESPERA ?? 600));
    const quadros: unknown[] = [];
    let dedo: number[] | null = null;
    /* CAP_PEGAR: segura o pet (o arrasto que comeca no sprite, PegarPet.tsx) e o leva para cima e para a direita, sem soltar */
    if (process.env.CAP_PEGAR) {
      const c = await page.evaluate(() => (window as any).__digilab.cena());
      const cena = (await page.locator(".pet-cena").boundingBox())!;
      const px = cena.x + c.ret.x + c.ret.w / 2, py = cena.y + c.ret.y + c.ret.h * 0.6;
      const [dx, dy] = larg >= 1100 ? [230, -150] : [70, -80];
      await page.mouse.move(px, py); await page.mouse.down();
      await page.mouse.move(px + dx, py + dy, { steps: 20 }); dedo = [Math.round(px + dx), Math.round(py + dy)];
      await page.waitForTimeout(500);
    }
    for (let i = 0; i < Number(process.env.CAP_N ?? 36); i++) {
      const nome = `${process.env.CAP_PREF ?? "q"}${String(i).padStart(2, "0")}_${pele}_${larg}`;
      const dados = await page.evaluate(() => {
        const d = (window as any).__digilab, m = d.mundo(), c = d.cena();
        if (!m) return null;
        const cena = document.querySelector(".pet-cena")!.getBoundingClientRect();
        const p = (x: number, y: number) => { const r = d.cenaPara(x, y); return r && [Math.round(cena.x + r[0]), Math.round(cena.y + r[1])]; };
        const db = d.digibrain();
        return { tick: d.tick(), acao: m.acao, pet: m.pet, petTela: c ? p(c.pet[0], c.pet[1]) : null, petMotorTela: p(m.pet[0], m.pet[1]), ret: c?.ret, cenaRet: [cena.x, cena.y, cena.width, cena.height],
          comedouro: m.comedouro, comedouroTela: p(m.comedouro[0], m.comedouro[1]), bola: m.bola, bolaTela: p(m.bola[0], m.bola[1]),
          comidas: m.comidas, lugares: m.lugares, fome: m.fome, petNaMao: d.petNaMao ? d.petNaMao() : null, dormindo: null,
          decisao: db?.decisao ? { acao: db.decisao.acao, chances: db.decisao.chances, regra: db.decisao.regra } : null, aprendido: db?.aprendido ?? null };
      });
      await page.screenshot({ path: `${OUT}/${nome}.png` });
      quadros.push({ nome, dedo, ...dados as object });
      await page.waitForTimeout(Number(process.env.CAP_PASSO ?? 150));
    }
    writeFileSync(`${OUT}/${process.env.CAP_PREF ?? "q"}quadros_${pele}_${larg}.json`, JSON.stringify({ save: SAVE, erros, quadros }, null, 1));
    await ctx.close();
  });
}
