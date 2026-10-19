/* O e2e só da página do WORLD-POC-01a (docs/TAREFA_V2_WORLD_POC_01.md, etapas E3 e E4): o build da página (npm run poc:build), servido
   pelo `vite preview` na porta 8800, no Chrome instalado. Separado do e2e do jogo (playwright.config.ts, pasta e2e/), que não muda.

     npm run poc:e2e    # o build da página e este e2e; grava as medidas em artifacts_v2_world_poc/ */
import { defineConfig } from "@playwright/test";

const PORTA = Number(process.env.DIGILAB_PORTA_POC ?? 8800);
export default defineConfig({
  testDir: "e2e_poc",
  timeout: 120_000,
  expect: { timeout: 30_000 },
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR", viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 1 },
  webServer: {
    command: `npx vite preview --config poc/vite.config.ts --port ${PORTA} --strictPort --host 127.0.0.1`,
    url: `http://127.0.0.1:${PORTA}/mundo3d.html`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
