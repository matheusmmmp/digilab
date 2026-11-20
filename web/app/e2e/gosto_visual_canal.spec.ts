/* Mudar de canal na TV do dono (GOSTO_VISUAL, 2026-11-12; docs/registro/2026-11.md, D-GV-CANAL-1 a 8): o pet de exemplo do primeiro
   acesso (a v35, com a TV no cérebro). A captura real precisaria do seletor do Chrome; aqui o getDisplayMedia é trocado por uma fonte falsa
   (um canvas de uma cor só, com um quadrado andando, pelo captureStream), uma cor diferente a cada chamada. Confere: "Mostrar minha tela"
   liga o canal 1; "+ Canal" põe o 2 sem desligar; "Canal ▸" alterna; o "st" fica só com a fonte "tela", sem a TV desligada no meio; a
   fonte encerrada sai; "+ Vídeo" abre um vídeo deste computador (gerado pelo ffmpeg, quando ele existe); e, no celular, nada de canal.
   As capturas de tela vão para DIGILAB_CAPTURAS (canal_*.png), quando a variável existe. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const CAPTURAS = process.env.DIGILAB_CAPTURAS ?? null;

async function abrir(browser: Browser, largura: number, altura: number) {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: altura } });
  /* a fonte falsa do seletor: cada chamada é uma "tela" de outra cor; window.__fontes guarda os fluxos para o teste encerrar um */
  await ctx.addInitScript(() => {
    const cores = ["#d33", "#36f", "#2b5"];
    let k = 0;
    const md = navigator.mediaDevices as MediaDevices | undefined;
    if (!md) return;
    md.getDisplayMedia = async () => {
      const cor = cores[k++ % cores.length]!, c = document.createElement("canvas");
      c.width = 160; c.height = 90;
      const g = c.getContext("2d")!;
      let t = 0;
      const desenhar = () => { g.fillStyle = cor; g.fillRect(0, 0, 160, 90); g.fillStyle = "#fff"; g.fillRect((t++ * 7) % 160, 30, 20, 20); };
      desenhar(); setInterval(desenhar, 100);
      const s = c.captureStream(10);
      const w = window as unknown as { __fontes?: MediaStream[] };
      (w.__fontes ??= []).push(s);
      return s;
    };
  });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(chave => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
  }, CHAVE);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
  return { ctx, page, erros };
}
const sts = (page: Page) => page.evaluate(() => (JSON.parse((window as any).__digilab.registro()).log as unknown[][]).filter(e => e[1] === "st").map(e => e[2] as string));
const capturar = async (page: Page, nome: string) => { if (CAPTURAS) await page.screenshot({ path: join(CAPTURAS, nome) }); };
/** um vídeo curto de teste (o testsrc com um seno), ou null sem o ffmpeg */
function videoDeTeste(): string | null {
  const saida = test.info().outputPath("canal_teste.webm");
  try {
    execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=160x90:rate=10", "-f", "lavfi", "-i", "sine=frequency=440",
      "-t", "4", "-c:v", "libvpx", "-c:a", "libopus", saida]);
    return saida;
  } catch { return null; }
}

test("canais, no desktop: + Canal sem desligar, Canal ▸ alterna, o st só com a fonte tela, a fonte encerrada sai e + Vídeo vira canal", async ({ browser }) => {
  test.setTimeout(240_000);
  const { ctx, page, erros } = await abrir(browser, 1440, 900);
  await page.locator(".pet-hud [data-painel-pet='tv'] button").click();
  const painel = page.getByTestId("painel-tv"), passando = painel.getByTestId("tv-passando"), canal = painel.locator("[data-tv-canal]");
  await expect(painel.getByRole("button", { name: "Abrir um vídeo" })).toBeVisible();
  await painel.getByRole("button", { name: "Mostrar minha tela" }).click();
  await expect(passando).toHaveText("Passando: a sua tela");
  await expect(canal).toHaveCount(0);                                     // um canal só: o Canal ▸ não aparece
  await expect(page.getByTestId("tv-selo")).toBeVisible();
  await painel.getByRole("button", { name: "Canal", exact: true }).click();
  await expect(passando).toHaveText("Passando: a sua tela, canal 2 de 2");
  await expect(canal).toBeVisible();
  await canal.click();
  await expect(passando).toHaveText("Passando: a sua tela, canal 1 de 2");
  await expect(page.getByTestId("tv-anuncio")).toContainText("O pet está vendo a sua tela, canal 1 de 2.");
  await page.waitForTimeout(11_000);
  await canal.click();
  await expect(passando).toHaveText("Passando: a sua tela, canal 2 de 2");
  await page.waitForTimeout(11_000);
  const st = await sts(page);
  expect(st.length).toBeGreaterThan(0);
  expect(st.every(v => /^tela(\|([0-9]|1[0-5])){7}$/.test(v))).toBe(true);   // a troca não desligou a TV no cérebro
  /* a fonte do canal 1 encerrada por fora (o dono parou de compartilhar): sai, e a TV segue no outro */
  await page.evaluate(() => { (window as any).__fontes[0].getVideoTracks()[0].dispatchEvent(new Event("ended")); });
  await expect(passando).toHaveText("Passando: a sua tela");
  await expect(canal).toHaveCount(0);
  await expect(painel.getByRole("button", { name: "Parar" })).toBeVisible();
  /* "+ Vídeo": um vídeo deste computador vira um canal pelo mesmo caminho */
  const arq = videoDeTeste();
  if (arq) {
    await painel.getByTestId("tv-arquivo").setInputFiles(arq);
    await expect(passando).toHaveText("Passando: um vídeo seu, canal 2 de 2", { timeout: 15_000 });
    await expect(page.getByTestId("tv-selo")).toContainText("Vendo um vídeo seu");
    await page.waitForTimeout(2500);
    await capturar(page, "canal_desktop_video.png");
    await canal.click();
    await expect(passando).toHaveText("Passando: a sua tela, canal 1 de 2");
    await painel.getByRole("button", { name: "Canal", exact: true }).click();
    await expect(passando).toHaveText("Passando: a sua tela, canal 3 de 3");
    await expect(painel).toContainText("Com 3 canais, o novo toma o lugar do canal de agora.");
  } else {
    await painel.getByRole("button", { name: "Canal", exact: true }).click();
    await expect(passando).toHaveText("Passando: a sua tela, canal 2 de 2");
  }
  await page.waitForTimeout(1500);
  await capturar(page, "canal_desktop.png");
  await painel.getByRole("button", { name: "Parar" }).click();
  await expect(painel.getByRole("button", { name: "Ligar a TV" })).toBeVisible();
  await expect(page.getByTestId("tv-selo")).toHaveCount(0);
  const fim = await sts(page);
  expect(fim.at(-1)).toBe("tela|desligada");
  expect(fim.filter(v => v === "tela|desligada").length).toBe(1);        // desligada só no Parar
  expect(erros).toEqual([]);
  await ctx.close();
});

test("canais, no celular: sem a captura, nem o Canal ▸ nem o + Canal aparecem", async ({ browser }) => {
  test.setTimeout(120_000);
  const { ctx, page, erros } = await abrir(browser, 390, 844);
  await page.locator(".mm-retrato").click();
  await page.locator("#leque-pet").getByRole("button", { name: "TV", exact: true }).click();
  const painel = page.getByTestId("painel-tv");
  await painel.getByRole("button", { name: "Ligar a TV" }).click();
  await expect(painel.getByTestId("tv-reacao")).not.toHaveText("Ligando…", { timeout: 15_000 });
  await expect(painel.locator("[data-tv-canal]")).toHaveCount(0);
  await page.waitForTimeout(800);
  await capturar(page, "canal_celular.png");
  await painel.getByRole("button", { name: "Mais" }).click();
  await expect(painel.getByTestId("tv-passando")).toContainText("a TV do jogo");
  await expect(painel.locator("[data-tv-canal], [data-tv-mais-canal], [data-tv-mais-video]")).toHaveCount(0);
  await expect(painel.getByRole("button", { name: "Abrir um vídeo" })).toHaveCount(0);
  expect(erros).toEqual([]);
  await ctx.close();
});

test("canais, na janela estreita: com dois canais escolhidos no desktop, a folha recolhida mostra o Canal ▸", async ({ browser }) => {
  test.setTimeout(120_000);
  const { ctx, page, erros } = await abrir(browser, 1440, 900);
  await page.locator(".pet-hud [data-painel-pet='tv'] button").click();
  const painel = page.getByTestId("painel-tv");
  await painel.getByRole("button", { name: "Mostrar minha tela" }).click();
  await painel.getByRole("button", { name: "Canal", exact: true }).click();
  await expect(painel.getByTestId("tv-passando")).toHaveText("Passando: a sua tela, canal 2 de 2");
  await page.keyboard.press("Escape");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator(".mm-retrato").click();
  await page.locator("#leque-pet").getByRole("button", { name: "TV", exact: true }).click();
  await expect(painel).toHaveClass(/tvp--recolhida/);
  const canal = painel.locator("[data-tv-canal]");
  await expect(canal).toBeVisible();
  await canal.click();
  await expect(page.getByTestId("tv-anuncio")).toContainText("canal 1 de 2");
  await page.waitForTimeout(800);
  await capturar(page, "canal_celular_dois_canais.png");
  expect(erros).toEqual([]);
  await ctx.close();
});
