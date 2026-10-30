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
/* a Evolucao (docs/TAREFA_V2_EVOLUCAO.md): o pet v11 do e2e que vira Champion quando o relogio anda (o momento, em tela cheia: so a janela,
   sem a pagina inteira por baixo) e a aba com o pet v6 das arenas */
const SAVE_EVO = JSON.parse(readFileSync(new URL("../e2e/save_evolucao.json", import.meta.url), "utf8"));
const TAMER_1 = { versao: 1, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: SAVE_EVO.semente, forma: "Agumon", tick: 490 }]] };
const SO_JANELA = new Set(["evolucao-momento"]);
/* o Treinar (docs/TAREFA_V2_TREINO.md): o Palmon v11 que pede pausa e o que so pode Forcar (e2e/gerar_save_treino.mjs) */
const SAVE_TR_PAUSA = JSON.parse(readFileSync(new URL("../e2e/save_treino_pausa.json", import.meta.url), "utf8"));
const SAVE_TR_FORCAR = JSON.parse(readFileSync(new URL("../e2e/save_treino_forcar.json", import.meta.url), "utf8"));
/* o mundo no jogo (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2): o Gomamon v12 do e2e do mundo, com a racao no comedouro */
const SAVE_MUNDO = JSON.parse(readFileSync(new URL("../e2e/save_mundo.json", import.meta.url), "utf8"));
const TELAS: [string, string, object, object?][] = [
  ["pet-estado", "#/pet/estado", SAVES.champion], ["crescer-treinar", "#/crescer/treinar", SAVES.champion], ["crescer-aprend", "#/crescer/aprend", SAVES.champion],
  ["crescer-evolucao", "#/crescer/evolucao", SAVES.champion], ["crescer-itens", "#/crescer/itens", SAVES.champion], ["lutar-arena", "#/lutar/arena", SAVES.champion],
  ["lutar-campanha", "#/lutar/campanha", SAVES.champion], ["lutar-fronteira", "#/lutar/fronteira", SAVES.champion], ["lutar-medalhas", "#/lutar/medalhas", SAVES.champion],
  ["diario-registro", "#/diario/registro", SAVES.champion], ["diario-catalogo", "#/diario/catalogo", SAVES.champion], ["diario-cenarios", "#/diario/cenarios", SAVES.champion],
  ["conversar", "#/conversar/chat", SAVES.champion], ["config", "#/config", SAVES.champion], ["pet-v11", "#/pet/estado", SAVE_V11],
  ["lutar-exploracao-v6", "#/lutar/campanha", SAVE_ARENAS, TAMER_3],
  ["evolucao-momento", "#/crescer/evolucao", SAVE_EVO, TAMER_1], ["crescer-evolucao-v6", "#/crescer/evolucao", SAVE_ARENAS, TAMER_3],
  ["treino-pausa", "#/crescer/treinar", SAVE_TR_PAUSA], ["treino-forcar", "#/crescer/treinar", SAVE_TR_FORCAR],
  ["pet-v12", "#/pet/estado", SAVE_MUNDO],
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

/* a largura: so o monitor do Matheus, 1920 x 950 (D10, docs/TAREFA_V2_LAYOUT_HABITAT.md); DIGILAB_CAPTURAS_LARGURAS="390,1280" (por exemplo) troca a lista,
   com a altura do celular abaixo de 1100 px e 800 px entre 1100 e 1899 */
const LARGURAS = (process.env.DIGILAB_CAPTURAS_LARGURAS ?? "1920").split(",").map(Number);
/* a pele dos menus (docs/TAREFA_V2_TEMA_MENUS.md): ?pele= no endereco, sem gravar; o padrao do portao e o Militar, o das referencias
   de antes da pele Holografica; DIGILAB_CAPTURAS_PELE=vidro captura o Holografico, com "vidro" no nome do arquivo */
const PELE = process.env.DIGILAB_CAPTURAS_PELE ?? "xcom";
if (PELE !== "xcom" && PELE !== "vidro") throw new Error(`DIGILAB_CAPTURAS_PELE invalida: ${PELE}`);
const SUFIXO_PELE = PELE === "xcom" ? "" : `_${PELE}`;
for (const [largura, altura] of LARGURAS.map(l => [l, l >= 1900 ? 950 : l >= 1100 ? 800 : l === 390 ? 844 : 800])) {
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
      /* o momento da evolucao com movimento reduzido: o anel do Digivice (decoracao local) gira sem parar, e duas fotos seguidas da mesma
         pagina variavam 2 pixels na borda dele */
      if (SO_JANELA.has(nome)) await page.emulateMedia({ reducedMotion: "reduce" });
      if (reserva) await page.route(/\/Assets\/(digilab_atlas_up|digilab_decoracao_up|decoracao_up\/)/, r => r.abort());
      await page.goto(`${APP}?pele=${PELE}${rota}`);
      /* os avisos ficam em .avisos desde a M7 do layout (docs/TAREFA_V2_LAYOUT_HABITAT.md) */
      if (reserva) await page.addStyleTag({ content: ".app > .aviso, .avisos > .aviso{display:none}" });
      await page.evaluate(() => document.fonts.ready);
      /* a tela Pet: a cena 3D chega por import dinamico (tempo real, fora do relogio falso); so depois dela o relogio anda, senao o
         numero de quadros desenhados antes da captura varia */
      await page.waitForFunction(() => !document.querySelector(".pet-cena") || !!document.querySelector(".pet-cena .cena-sala")
        || (document.querySelector<HTMLCanvasElement>(".pet-cena .cena3d canvas")?.width ?? 0) > 0);
      /* a Exploracao: o mapa 3D tambem chega por import dinamico; espera ele desenhar (ou a tela cair no mapa 2D) */
      await page.waitForFunction(() => !document.querySelector(".camp-tela--expl") || !!document.querySelector(".mapa-expl[data-pronto]"));
      await page.clock.runFor(1000);
      /* o momento da evolucao: o pet evolui enquanto o relogio anda, e a revelacao abre */
      if (SO_JANELA.has(nome)) await page.locator("dialog.revelacao[open]").waitFor();
      await page.waitForLoadState("networkidle");
      /* toda imagem decodificada antes da captura */
      await page.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => undefined))));
      /* refaz o layout e a pintura da página inteira, com as fontes e as imagens já prontas: sem isso o texto de um select
         ou um ícone pequeno às vezes fica como foi pintado antes de a fonte ou a imagem chegarem */
      await page.evaluate(() => { const h = document.documentElement; h.style.display = "none"; void h.offsetHeight; h.style.display = ""; void h.offsetHeight; });
      await expect(page).toHaveScreenshot(`${nome}${SUFIXO_PELE}_${largura}.png`, { fullPage: !SO_JANELA.has(nome), animations: "disabled", caret: "hide", threshold: 0, maxDiffPixels: 0 });
      expect(erros).toEqual([]);
    });
  }
}
