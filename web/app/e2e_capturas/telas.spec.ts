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
/* a Exploracao de um pet v6 (docs/TAREFA_V2_EXPLORACAO.md): o save das arenas do e2e (a Cidadela e o proximo desafio) e o Tamer com as 3
   primeiras medalhas: seis ilhas, vencidas, abertas e trancadas, e a Fronteira trancada */
const SAVE_ARENAS = JSON.parse(readFileSync(new URL("../e2e/save_arenas.json", import.meta.url), "utf8"));
const TAMER_3 = { versao: 1, log: ["campina", "torre", "floresta"].map((id, i) =>
  ["medalha", { id, n: i + 1, quando: 1 + i, pet: SAVE_ARENAS.semente, forma: "DinoBeemon", tick: 900 + i }]) };
const TELAS: [string, string, object, object?][] = [
  ["pet-estado", "#/pet/estado", SAVES.v3], ["crescer-treinar", "#/crescer/treinar", SAVES.v3], ["crescer-aprend", "#/crescer/aprend", SAVES.v3],
  ["crescer-evolucao", "#/crescer/evolucao", SAVES.v3], ["crescer-itens", "#/crescer/itens", SAVES.v3], ["lutar-arena", "#/lutar/arena", SAVES.v3],
  ["lutar-campanha", "#/lutar/campanha", SAVES.v3], ["lutar-fronteira", "#/lutar/fronteira", SAVES.v3], ["lutar-medalhas", "#/lutar/medalhas", SAVES.v3],
  ["diario-registro", "#/diario/registro", SAVES.v3], ["diario-catalogo", "#/diario/catalogo", SAVES.v3], ["diario-cenarios", "#/diario/cenarios", SAVES.v3],
  ["conversar", "#/conversar/chat", SAVES.v3], ["config", "#/config", SAVES.v3], ["pet-v11", "#/pet/estado", SAVE_V11],
  ["lutar-exploracao-v6", "#/lutar/campanha", SAVE_ARENAS, TAMER_3],
];

/** semeia o save por uma página da mesma origem que não é o app (como em e2e/jogo.spec.ts) */
async function semear(page: Page, save: object, tamer: object = { versao: 1, log: [] }): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "5"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(save), JSON.stringify(tamer)] as const);
}

/* as larguras: 390 e 1280; DIGILAB_CAPTURAS_LARGURAS="360" (por exemplo) troca a lista, com a altura do celular abaixo de 1100 px */
const LARGURAS = (process.env.DIGILAB_CAPTURAS_LARGURAS ?? "390,1280").split(",").map(Number);
for (const [largura, altura] of LARGURAS.map(l => [l, l >= 1100 ? 800 : l === 390 ? 844 : 800])) {
  for (const [nome, rota, save, tamer] of TELAS) {
    test(`${nome} em ${largura} px`, async ({ page }) => {
      await page.setViewportSize({ width: largura, height: altura });
      await semear(page, save, tamer);
      const T0 = new Date("2026-10-19T12:00:00Z").getTime();
      await page.clock.install({ time: T0 });
      await page.clock.pauseAt(T0 + 1000);           /* parado desde antes de abrir: o tempo do jogo só anda com runFor */
      const erros: string[] = [];
      page.on("pageerror", e => erros.push(e.message));
      /* DIGILAB_CAPTURAS_RESERVA=1: sem o atlas e sem a decoracao do UP (so locais), para capturas que vao para o repositorio ou para o
         PR; os avisos de "nao carregou" ficam escondidos so na captura */
      const reserva = process.env.DIGILAB_CAPTURAS_RESERVA === "1";
      if (reserva) await page.route(/\/Assets\/(digilab_atlas_up|digilab_decoracao_up|decoracao_up\/)/, r => r.abort());
      await page.goto(APP + rota);
      if (reserva) await page.addStyleTag({ content: ".app > .aviso{display:none}" });
      await page.evaluate(() => document.fonts.ready);
      /* a tela Pet: a cena 3D chega por import dinamico (tempo real, fora do relogio falso); so depois dela o relogio anda, senao o
         numero de quadros desenhados antes da captura varia */
      await page.waitForFunction(() => !document.querySelector(".pet-cena") || !!document.querySelector(".pet-cena .cena-sala")
        || (document.querySelector<HTMLCanvasElement>(".pet-cena .cena3d canvas")?.width ?? 0) > 0);
      /* a Exploracao: o mapa 3D tambem chega por import dinamico; espera ele desenhar (ou a tela cair no mapa 2D) */
      await page.waitForFunction(() => !document.querySelector(".camp-tela--expl") || !!document.querySelector(".mapa-expl[data-pronto]"));
      await page.clock.runFor(1000);
      await page.waitForLoadState("networkidle");
      /* toda imagem decodificada antes da captura */
      await page.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => undefined))));
      /* refaz o layout e a pintura da página inteira, com as fontes e as imagens já prontas: sem isso o texto de um select
         ou um ícone pequeno às vezes fica como foi pintado antes de a fonte ou a imagem chegarem */
      await page.evaluate(() => { const h = document.documentElement; h.style.display = "none"; void h.offsetHeight; h.style.display = ""; void h.offsetHeight; });
      await expect(page).toHaveScreenshot(`${nome}_${largura}.png`, { fullPage: true, animations: "disabled", caret: "hide", threshold: 0, maxDiffPixels: 0 });
      expect(erros).toEqual([]);
    });
  }
}
