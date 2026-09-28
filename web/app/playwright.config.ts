/* Teste ponta a ponta (TAREFA_FRONT_TS, Etapa 5): o build servido pelo servidor local (mesmo caminho do jogo),
   com o HTML antigo na mesma origem para conferir a assinatura. Usa o Chrome instalado (sem baixar navegador). */
import { defineConfig } from "@playwright/test";

const PORTA = 8799;
export default defineConfig({
  testDir: "e2e",
  timeout: 240_000,
  expect: { timeout: 60_000 },
  fullyParallel: true,
  workers: 3,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR" },
  webServer: {
    command: `"../../.venv/Scripts/python.exe" ../../servidor/servidor_local.py --porta ${PORTA} --provedor nenhum`,
    url: `http://127.0.0.1:${PORTA}/v1/web/dist/`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
