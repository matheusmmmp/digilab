/* As capturas da P2 de pegar o pet (docs/TAREFA_V3_PEGAR_PET.md): no servidor de desenvolvimento do Vite (o atlas de clipes com
   ?clipes_up=1). So roda com DIGILAB_CAPTURAS_PP2=<pasta>. */
import { defineConfig } from "@playwright/test";

const PORTA = Number(process.env.DIGILAB_PORTA_PP2 ?? 5183);
export default defineConfig({
  testDir: ".",
  testMatch: /pegar_pet_p2\.spec\.ts$/,
  timeout: 240_000,
  expect: { timeout: 60_000 },
  workers: 2,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR", deviceScaleFactor: 1 },
  webServer: { command: `npx vite --port ${PORTA} --strictPort --host 127.0.0.1`, url: `http://127.0.0.1:${PORTA}/`, reuseExistingServer: false, timeout: 120_000, cwd: ".." },
});
