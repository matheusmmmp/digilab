/* As capturas e os quadros do GIF da E4, as posturas como efeito (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 4): o Gabumon (cirro, o Rookie
   v18 das capturas da E3) contra os rivais da lista (DIGILAB_E4_RIVAIS), em 390 e 1280 px, nas peles vidro e militar (xcom). Para cada uma, o
   palco parado na primeira vez que a luta mostra cada efeito (o escudo, o escudo aceso, a imagem fantasma, a aura, o contra-golpe, o clarao
   do contra-golpe, a pele dura) e cada icone (data-posturas); a lista do que saiu fica no .txt. Em cada largura e pele, grava tambem os quadros
   da tela para o GIF, da primeira postura ate DIGILAB_E4_GIF_S segundos depois. Mais dois modos:
   - a sonda (DIGILAB_E4_SONDA=1): joga, sem desenhar, a primeira luta do Gabumon contra cada rival e anota as posturas e os efeitos de cada
     lado (sonda.txt), para escolher as lutas que mostram tudo;
   - a folha dos icones: os oito icones em escala 6, com o nome, nas duas peles (icones_<pele>.png).
   Roda com: npx playwright test -c e2e_capturas/luta_efeitos_e4.config.ts, com DIGILAB_CAPTURAS_E4=<pasta>. Nao e referencia das capturas. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_E4 ?? "";
const CHAVE = "digilab-web-v21-sprites";
const GABUMON = { semente: 101, versao: 18, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
const PARES = (process.env.DIGILAB_E4_RIVAIS ?? "espelho").split(",").map(r => ({ nome: "gabumon_" + r, rival: r }));
/* os GIFs so das lutas desta lista (DIGILAB_E4_GIF_RIVAIS; por padrao todas as da lista acima) */
const PARES_GIF = process.env.DIGILAB_E4_GIF_RIVAIS ? process.env.DIGILAB_E4_GIF_RIVAIS.split(",").map(r => ({ nome: "gabumon_" + r, rival: r })) : PARES;
const SONDA = !!process.env.DIGILAB_E4_SONDA, SO_1280 = !!process.env.DIGILAB_E4_SO_1280, GIF_S = Number(process.env.DIGILAB_E4_GIF_S ?? 8);
const PELES = SO_1280 ? ["vidro"] : ["vidro", "xcom"];
const LARGURAS = (SO_1280 ? [[1280, 720]] : [[390, 844], [1280, 720]]) as [number, number][];

async function semear(page: Page): Promise<void> {
  /* o save e semeado por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele por cima ao fechar) */
  await page.goto("/motor/index.ts");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(GABUMON), JSON.stringify(TAMER)] as const);
}
async function abrirLuta(page: Page, pele: string, rival: string): Promise<void> {
  await semear(page);
  await page.goto(`/?pele=${pele}&clipes_up=1#/lutar/arena`);
  await expect(page.locator(".lutar-grande")).toBeVisible();
  await page.evaluate(async (k) => { (await import("/src/luta.ts" as string)).escolherRival(k); }, rival);
  await page.evaluate(async () => { (window as unknown as { __luta: unknown }).__luta = (await import("/src/luta.ts" as string)).LUTA; });
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
}
/** o que se procura no palco: os efeitos (campos do canvas) e os icones (data-posturas) */
/* a imagem fantasma conta aberta (o primeiro passo da esquiva ainda tem as copias junto do corpo) */
const EFEITOS = ["escudos", "escudosAcesos", "fantasmasAbertos", "auras", "contras", "claroes", "peles"] as const;
const ICONES = ["defender", "esquivar", "carregar", "contra_golpe", "preparar_pesado", "pesado_pronto", "marcar", "pele_dura"] as const;
type Alvo = typeof EFEITOS[number] | `icone_${typeof ICONES[number]}`;
/** espera o canvas mostrar o primeiro dos alvos e para a luta no mesmo quadro; null se a luta acabou antes */
async function pararQuando(page: Page, alvos: Alvo[]): Promise<Alvo | null> {
  const h = await page.waitForFunction((as) => {
    const cv = document.querySelector(".arena-cv") as HTMLElement | null;
    if (!location.hash.endsWith("/luta")) return "fim";
    if (!cv) return false;
    const post = (cv.dataset.posturas ?? "").split(",");
    const a = as.find(a => a.startsWith("icone_") ? post.includes(a.slice(6)) : Number(cv.dataset[a] ?? 0) > 0);
    if (!a) return false;
    (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = true; return a;
  }, alvos, { timeout: 150_000, polling: "raf" }).catch(() => null);
  const v = await h?.jsonValue();
  return v && v !== "fim" ? v as Alvo : null;
}
const seguir = (page: Page) => page.evaluate(() => { (window as unknown as { __luta: { pausado: boolean } }).__luta.pausado = false; });

test.describe("capturas da E4", () => {
  test.skip(!PASTA, "so com DIGILAB_CAPTURAS_E4");

  test("sonda: as posturas da primeira luta contra cada rival", async ({ page }) => {
    test.skip(!SONDA, "so com DIGILAB_E4_SONDA");
    test.setTimeout(600_000);
    mkdirSync(PASTA, { recursive: true });
    await semear(page);
    await page.goto(`/?clipes_up=1#/lutar/arena`);
    const rivais = process.env.DIGILAB_E4_RIVAIS ? PARES.map(p => p.rival)
      : await page.evaluate(async () => { const M = await import("/motor/index.ts" as string); return [...Object.keys(M.BOTS_V2), ...Object.keys(M.BOTS_V21)]; });
    const linhas: string[] = [];
    for (const k of rivais) {
      await semear(page); await page.goto(`/?clipes_up=1#/lutar/arena`);
      await expect(page.locator(".lutar-grande")).toBeVisible();
      const r = await page.evaluate(async (k) => {
        const M = await import("/motor/index.ts" as string), J = await import("/src/jogo.ts" as string);
        const E = await import("/src/telas/lutar/palcoTR/efeitosTR.ts" as string), P = await import("/src/telas/lutar/palcoTR/posturasTR.ts" as string);
        const m = J.jogoAtual().motor;
        let res; try { res = m.lutar(k, M.hashSemente("luta", m.semente, m.log.length), null).res; } catch (e) { return "erro: " + String(e); }
        const en = res.tr.entrada, sim = M.criarLutaTR(en.A, en.B, en.semente, { ...en.o, eventos: true }), v = E.visualNovoTR(), vis = new Set<string>();
        let lidos = 0, fim = null;
        while (!fim) {
          fim = M.passoTR(sim); const ev = sim.eventos.slice(lidos); E.aplicarEventosTR(v, sim, ev); lidos = sim.eventos.length;
          sim.S.L.forEach((l: unknown, i: number) => {
            const p = P.posturaDoLado(l); if (p) vis.add(`${p}${i}`);
            const ef = P.efeitoDaPostura(l, i, sim.S.passo, v.batidas, false);
            if (ef.escudo?.aceso) vis.add(`ESCUDO_ACESO${i}`); if (ef.contra?.clarao) vis.add(`CLARAO${i}`); if (ef.pele) vis.add(`PELE${i}`);
          });
        }
        return `${[...vis].length} ${[...vis].sort().join(",")} | ${res.tr.passos} passos, ${res.tr.fim}`;
      }, k);
      linhas.push(`${k}: ${r}`);
    }
    writeFileSync(join(PASTA, "sonda.txt"), linhas.join("\n") + "\n");
  });

  for (const pele of ["vidro", "xcom"]) test(`folha dos icones: ${pele}`, async ({ page }) => {
    test.skip(SONDA, "so fora da sonda");
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: 720, height: 260 });
    await page.goto(`/?pele=${pele}#/lutar/arena`);
    await page.evaluate(async () => {
      const P = await import("/src/telas/lutar/palcoTR/posturasTR.ts" as string);
      document.body.innerHTML = ""; document.body.style.background = "#0b1a44"; document.body.style.margin = "0";
      const cv = document.createElement("canvas"); cv.width = 720; cv.height = 260; cv.id = "folha"; document.body.appendChild(cv);
      const cx = cv.getContext("2d")!; cx.imageSmoothingEnabled = false; cx.fillStyle = "#0b1a44"; cx.fillRect(0, 0, 720, 260);
      const u = 6;
      (P.POSTURAS_TR as string[]).forEach((p, k) => {
        const x0 = 20 + (k % 4) * 175, y0 = 20 + Math.floor(k / 4) * 120;
        for (const lado of [0, 1]) for (const px of P.pixelsDoIcone(p, "cirro", lado)) {
          cx.globalAlpha = px.alfa; cx.fillStyle = px.cor; cx.fillRect(x0 + lado * 70 + (px.dx + 1) * u, y0 + (px.dy + 1) * u, u, u);
        }
        cx.globalAlpha = 1; cx.fillStyle = "#fff"; cx.font = "14px system-ui"; cx.fillText(P.NOME_POSTURA[p], x0, y0 + 76);
      });
    });
    await page.locator("#folha").screenshot({ path: join(PASTA, `icones_${pele === "xcom" ? "militar" : "vidro"}.png`) });
  });

  for (const par of PARES) for (const pele of PELES) for (const [w, h] of LARGURAS) test(`${par.nome}: ${pele} ${w}`, async ({ page }) => {
    test.skip(SONDA, "so fora da sonda");
    test.setTimeout(400_000);
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele, par.rival);
    const nome = `luta_e4_${par.nome}_${w}_${pele === "xcom" ? "militar" : "vidro"}`, feitas: string[] = [];
    const faltam: Alvo[] = [...EFEITOS, ...ICONES.map(i => `icone_${i}` as Alvo)];
    while (faltam.length) {
      const c = await pararQuando(page, faltam); if (!c) break;
      await page.waitForTimeout(150);
      /* o que mais saiu no mesmo quadro tambem conta (uma foto pode mostrar varias posturas) */
      const junto = await page.evaluate((as) => {
        const cv = document.querySelector(".arena-cv") as HTMLElement, post = (cv.dataset.posturas ?? "").split(",");
        return as.filter(a => a.startsWith("icone_") ? post.includes(a.slice(6)) : Number(cv.dataset[a] ?? 0) > 0);
      }, faltam);
      const titulos = await page.locator(".luta-postura:not([hidden])").evaluateAll(els => els.map(e => e.getAttribute("title")));
      await page.screenshot({ path: join(PASTA, `${nome}_${c}.png`) });
      feitas.push(`${c}: ${junto.join(" ")} | title: ${titulos.join(" / ")}`);
      for (const j of junto) faltam.splice(faltam.indexOf(j), 1);
      await seguir(page);
    }
    writeFileSync(join(PASTA, `${nome}.txt`), feitas.join("\n") + "\n" + (faltam.length ? `nao saiu: ${faltam.join(" ")}\n` : ""));
    expect(feitas.length).toBeGreaterThan(0);
  });

  for (const par of PARES_GIF) for (const pele of PELES) for (const [w, h] of LARGURAS) test(`${par.nome}: quadros do GIF ${pele} ${w}`, async ({ page }) => {
    test.skip(SONDA, "so fora da sonda");
    test.setTimeout(300_000);
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele, par.rival);
    const nome = `luta_e4_${par.nome}_${w}_${pele === "xcom" ? "militar" : "vidro"}_gif`, cdp = await page.context().newCDPSession(page);
    let n = 0, gravando = false;
    cdp.on("Page.screencastFrame", async (ev: { data: string; sessionId: number }) => {
      if (gravando) writeFileSync(join(PASTA, `${nome}_f${String(n++).padStart(4, "0")}.jpg`), Buffer.from(ev.data, "base64"));
      await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }).catch(() => undefined);
    });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, everyNthFrame: 1 });
    await page.waitForFunction(() => ((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset.posturas ?? ",") !== ",", null, { timeout: 120_000, polling: "raf" });
    gravando = true;
    await page.waitForTimeout(GIF_S * 1000);
    gravando = false;
    await cdp.send("Page.stopScreencast");
    expect(n).toBeGreaterThan(20);
  });
});
