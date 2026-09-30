/* Teste ponta a ponta (TAREFA_FRONT_TS, Etapa 5): o build servido pelo servidor local (mesmo caminho do jogo),
   com o HTML antigo na mesma origem para conferir a assinatura. Usa o Chrome instalado (sem baixar navegador). */
import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";
import { basename, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// o servidor serve a pasta-mae com o nome da pasta do repositorio como prefixo (/v1 ou o da worktree);
// o Python e o do .venv do repositorio, ou DIGILAB_PYTHON (worktrees sem .venv)
const REPO = fileURLToPath(new URL("../..", import.meta.url));
const PREFIXO = "/" + basename(REPO);
const PY_LOCAL = resolve(REPO, ".venv/Scripts/python.exe");
const PYTHON = process.env.DIGILAB_PYTHON ?? (existsSync(PY_LOCAL) ? PY_LOCAL : "python");

// DIGILAB_PORTA_E2E: outra porta quando um e2e de outra worktree ja ocupa a 8799
const PORTA = Number(process.env.DIGILAB_PORTA_E2E ?? 8799);
export default defineConfig({
  testDir: "e2e",
  timeout: 240_000,
  expect: { timeout: 60_000 },
  fullyParallel: true,
  workers: 3,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR" },
  webServer: {
    command: `"${PYTHON}" ../../servidor/servidor_local.py --porta ${PORTA} --provedor nenhum`,
    url: `http://127.0.0.1:${PORTA}${PREFIXO}/web/dist/`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
