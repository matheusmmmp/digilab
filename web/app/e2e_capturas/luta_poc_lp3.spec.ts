/* As capturas da LP3, a tela da luta da POC (docs/TAREFA_V3_LUTA_POC.md, secoes 3.3, 3.3a e 5.1): uma luta montada em cada um dos 8 mapas,
   no desktop (1920 x 950) e no celular (390 x 844, 3 px por px de CSS), com as fotos dos momentos (o projetil em voo, o projetil nosso da
   LP-8, o acerto, a regra do mapa, o nocaute e o resultado) e um .txt com o que o palco desenhou em cada uma (os data-* do canvas).
   Roda com: npx playwright test -c e2e_capturas/luta_poc_lp3.config.ts, com DIGILAB_CAPTURAS_LP3=<pasta>. Nao e referencia das capturas. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_LP3 ?? "";
const CHAVE = "digilab-web-v21-sprites";
type Momento = [nome: string, cond: string];
/** a condicao de cada momento e avaliada a cada quadro sobre `d` (o dataset do canvas) e `r` (o resultado na tela) */
const BASE: Momento[] = [
  ["1_voo", "+d.projeteisDesenho > 0 || +d.nossos > 0"],
  ["2_acerto", "+d.impactos > 0 && +d.numeros > 0"],
];
const FIM: Momento[] = [["8_ko", "d.koPronto === '1'"], ["9_resultado", "!!r"]];
const LUTAS: { id: string; q: string; regra?: Momento[] }[] = [
  { id: "floresta_gabumon_agumon", q: "floresta,cirro_crianca_arisco,brasa_crianca_sereno,101", regra: [["0_nosso_gabumon", "+d.nossos > 0 && +d.projeteisMeio > 0"]] },
  { id: "campo_greymon_garurumon", q: "campo,brasa_adolescente_brigao,cirro_adolescente_brigao,103", regra: [["0_nosso_garurumon", "+d.nossos > 0"]] },
  { id: "coliseu_seraphimon_slashangemon", q: "coliseu,cirro_adulto_muralha,ferrugem_adulto_muralha,111", regra: [["5_regra_fecha", "+d.passo >= 2800"]] },
  { id: "praia_seadramon_ikkakumon", q: "praia,limo_adolescente_cacador,limo_adolescente_colosso,104", regra: [["5_regra_mare", "+d.passo >= 520 && +d.passo <= 640"]] },
  { id: "deserto_kabuterimon_birdramon", q: "deserto,ferrugem_adolescente_colosso,brasa_adolescente_cacador,105", regra: [["5_regra_tempestade", "+d.passo >= 780 && +d.passo <= 1100"]] },
  { id: "castelo_angemon_growlmon", q: "castelo,cirro_adolescente_guardiao,brasa_adolescente_colosso,106", regra: [["0_nosso_angemon", "+d.nossos > 0"], ["3_preparo_habilidade", "+d.telegrafiasMeio > 0"]] },
  { id: "caverna_togemon_kyubimon", q: "caverna,limo_adolescente_guardiao,brasa_adolescente_guardiao,107", regra: [["5_regra_erupcao", "+d.passo >= 390 && +d.passo <= 420"]] },
  { id: "ringue_wargreymon_metalgarurumon", q: "ringue,brasa_adulto_furioso,cirro_adulto_furioso,108", regra: [["0_nosso_metalgarurumon", "+d.nossos > 0"], ["4_empurrao", "+d.marcas > 0 && +d.poeiras > 0"], ["6_zoom", "+d.zoom > 1.2"]] },
];
const TELAS: { nome: string; w: number; h: number; dpr: number }[] = [
  { nome: "1920", w: 1920, h: 950, dpr: 1 },
  { nome: "390", w: 390, h: 844, dpr: 3 },
].filter(t => !process.env.DIGILAB_LP3_TELA || process.env.DIGILAB_LP3_TELA === t.nome);
const PELES = (process.env.DIGILAB_LP3_PELES ?? "vidro").split(",");
const FILTRO = process.env.DIGILAB_LP3_LUTA ?? "";

async function semear(page: Page): Promise<void> {
  /* sem pet ativo nem boas-vindas: so a luta montada (o save e semeado por uma pagina da mesma origem que nao e o app) */
  await page.goto("/motor/index.ts");
  await page.evaluate((chave) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-descarte", "7");
    localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
  }, CHAVE);
}

for (const t of TELAS) for (const pele of PELES) for (const l of LUTAS.filter(x => !FILTRO || x.id.includes(FILTRO))) {
  test(`LP3 ${l.id} ${t.nome} ${pele}`, async ({ browser }) => {
    test.skip(!PASTA, "so com DIGILAB_CAPTURAS_LP3");
    mkdirSync(PASTA, { recursive: true });
    const ctx = await browser.newContext({ viewport: { width: t.w, height: t.h }, deviceScaleFactor: t.dpr });
    const page = await ctx.newPage();
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(String(e)));
    await semear(page);
    await page.goto(`/?luta_poc=1&pele=${pele}&palco_poc=${l.q}`);
    await expect(page.getByTestId("poc-canvas")).toBeVisible();
    /* DIGILAB_LP3_GIF=<trecho do id>: grava os quadros da tela (o screencast do Chrome) da luta inteira, para o GIF */
    const gif = !!process.env.DIGILAB_LP3_GIF && l.id.includes(process.env.DIGILAB_LP3_GIF);
    let gravando = gif, nq = 0;
    if (gif) {
      mkdirSync(join(PASTA, "quadros"), { recursive: true });
      const cdp = await page.context().newCDPSession(page);
      cdp.on("Page.screencastFrame", async (ev: { data: string; sessionId: number }) => {
        if (gravando) writeFileSync(join(PASTA, "quadros", `${l.id}_${t.nome}_${pele}_f${String(nq++).padStart(4, "0")}.jpg`), Buffer.from(ev.data, "base64"));
        await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }).catch(() => undefined);
      });
      await cdp.send("Page.startScreencast", { format: "jpeg", quality: 88, everyNthFrame: 1 });
    }
    const momentos = [...(l.regra ?? []), ...BASE, ...FIM].sort((a, b) => a[0].localeCompare(b[0]));
    const nomePele = pele === "xcom" ? "militar" : "vidro", txt: string[] = [];
    const feitos = new Set<string>();
    /* espera cada momento (na ordem de chegada, qualquer que seja), ate o resultado */
    while (feitos.size < momentos.length) {
      const prox = await page.waitForFunction((ms: [string, string][]) => {
        const cv = document.querySelector("[data-testid=poc-canvas]") as HTMLElement | null; if (!cv) return null;
        const d = cv.dataset, r = document.querySelector("[data-testid=poc-resultado]");
        const w = window as unknown as { __feitos?: string[] };
        for (const [n, c] of ms) if (!(w.__feitos ?? []).includes(n) && new Function("d", "r", `return (${c})`)(d, r)) { (w.__feitos ??= []).push(n); return n; }
        return r && (w.__feitos ?? []).includes("9_resultado") ? "fim" : null;
      }, momentos, { timeout: 200_000, polling: "raf" });
      const n = await prox.jsonValue() as string;
      if (n === "fim") break;
      feitos.add(n);
      const arq = `lp3_${l.id}_${t.nome}_${nomePele}_${n}.png`;
      await page.screenshot({ path: join(PASTA, arq) });
      const d = await page.getByTestId("poc-canvas").evaluate(el => JSON.stringify((el as HTMLElement).dataset));
      txt.push(`${arq}: ${d}`);
      if (n === "9_resultado") break;
    }
    gravando = false;
    for (const [n] of momentos) if (!feitos.has(n)) txt.push(`(sem o momento ${n} nesta luta)`);
    writeFileSync(join(PASTA, `lp3_${l.id}_${t.nome}_${nomePele}.txt`), txt.join("\n") + (erros.length ? "\nERROS:\n" + erros.join("\n") : "") + "\n");
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
