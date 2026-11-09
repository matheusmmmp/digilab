/* As capturas da LP3 (docs/TAREFA_V3_LUTA_POC.md, secao 5.1): no servidor de desenvolvimento do Vite, com a chave ligada por parametro e as
   lutas montadas direto no nucleo (?luta_poc=1&palco_poc=...). So roda com DIGILAB_CAPTURAS_LP3=<pasta>. */
import { defineConfig } from "@playwright/test";

const PORTA = Number(process.env.DIGILAB_PORTA_LP3 ?? 5233);
export default defineConfig({
  testDir: ".",
  testMatch: /luta_poc_lp3(_jogo)?\.spec\.ts$/,
  timeout: 300_000,
  fullyParallel: true,
  expect: { timeout: 60_000 },
  workers: Number(process.env.DIGILAB_WORKERS_LP3 ?? 4),
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR" },
  webServer: { command: `npx vite --port ${PORTA} --strictPort --host 127.0.0.1`, url: `http://127.0.0.1:${PORTA}/`, reuseExistingServer: true, timeout: 120_000, cwd: ".." },
});
