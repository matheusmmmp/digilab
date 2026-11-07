/* As capturas da E2 (docs/TAREFA_V3_LUTA_EFEITOS.md, secao 4): no servidor de desenvolvimento do Vite, e nao no build, porque o Agumon contra o
   Gabumon precisa de um rival que a Arena nao oferece (um Rookie como rival fixo) e o teste o monta pelos modulos do app (luta.ts). Os
   Cenarios do Lab, que fariam isso pela tela, criam pets na versao 5, que nao abre mais. So roda com DIGILAB_CAPTURAS_E2=<pasta>. */
import { defineConfig } from "@playwright/test";

const PORTA = Number(process.env.DIGILAB_PORTA_E2 ?? 5179);
export default defineConfig({
  testDir: ".",
  testMatch: /luta_efeitos_e2\.spec\.ts$/,
  timeout: 240_000,
  expect: { timeout: 60_000 },
  workers: 2,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR", deviceScaleFactor: 1 },
  webServer: { command: `npx vite --port ${PORTA} --strictPort --host 127.0.0.1`, url: `http://127.0.0.1:${PORTA}/`, reuseExistingServer: false, timeout: 120_000, cwd: ".." },
});
