/* As capturas do conserto dos Cenarios do Lab (2026-11-07): no servidor de desenvolvimento do Vite. Monta o cenario pela tela, roda as
   100 lutas e abre a luta em tempo real contra o rival fixo. So roda com DIGILAB_CAPTURAS_LAB=<pasta>. */
import { defineConfig } from "@playwright/test";

const PORTA = Number(process.env.DIGILAB_PORTA_LAB ?? 5178);
export default defineConfig({
  testDir: ".",
  testMatch: /lab_cenarios\.spec\.ts$/,
  timeout: 240_000,
  expect: { timeout: 60_000 },
  workers: 2,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR", deviceScaleFactor: 1 },
  webServer: { command: `npx vite --port ${PORTA} --strictPort --host 127.0.0.1`, url: `http://127.0.0.1:${PORTA}/`, reuseExistingServer: false, timeout: 120_000, cwd: ".." },
});
