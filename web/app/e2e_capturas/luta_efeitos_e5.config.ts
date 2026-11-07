/* As capturas da E5 (docs/TAREFA_V3_LUTA_EFEITOS.md, secao 4): no servidor de desenvolvimento do Vite, como as da E2 a E4, para escolher o
   rival pelos modulos do app (luta.ts). So roda com DIGILAB_CAPTURAS_E5=<pasta>. */
import { defineConfig } from "@playwright/test";

const PORTA = Number(process.env.DIGILAB_PORTA_E5 ?? 5183);
export default defineConfig({
  testDir: ".",
  testMatch: /luta_efeitos_e5\.spec\.ts$/,
  timeout: 240_000,
  expect: { timeout: 60_000 },
  workers: 2,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR", deviceScaleFactor: 1 },
  webServer: { command: `npx vite --port ${PORTA} --strictPort --host 127.0.0.1`, url: `http://127.0.0.1:${PORTA}/`, reuseExistingServer: false, timeout: 120_000, cwd: ".." },
});
