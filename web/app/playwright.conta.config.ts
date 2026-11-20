/* O e2e das telas que so existem com o servidor no build (a chave VITE_DIGILAB_API): hoje, o cais (MMO5, docs/TAREFA_V3_MMO.md). Separado
   do e2e do jogo (playwright.config.ts, pasta e2e/), que roda o build sem a chave e nao muda.

     npm run e2e:conta    # monta web/dist_conta/ com a chave e roda os specs de e2e_conta/

   O build sai em web/dist_conta/ (nao versionado), servido pelo servidor local como o de sempre. O servidor_web nao sobe: cada spec
   responde as rotas dele com `page.route` (o servidor falso), na mesma origem da pagina. Usa o Chrome instalado. */
import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { APP, PORTA, REPO } from "./e2e_conta/comum.ts";

const PY_LOCAL = resolve(REPO, ".venv/Scripts/python.exe");
const PYTHON = process.env.DIGILAB_PYTHON ?? (existsSync(PY_LOCAL) ? PY_LOCAL : "python");

export default defineConfig({
  testDir: "e2e_conta",
  globalSetup: "./e2e_conta/montar.ts",
  timeout: 240_000,
  expect: { timeout: 60_000 },
  fullyParallel: true,
  workers: 3,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${PORTA}`, channel: "chrome", headless: true, locale: "pt-BR" },
  webServer: {
    command: `"${PYTHON}" ../../servidor/servidor_local.py --porta ${PORTA} --provedor nenhum`,
    /* a pagina do build so existe depois da montagem; o servidor esta de pe quando serve o atlas */
    url: `http://127.0.0.1:${PORTA}/Assets/digilab_atlas_up.json`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
