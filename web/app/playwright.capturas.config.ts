/* Capturas das telas (docs/TAREFA_V2_FRONT_REACT.md, gate "o jogo sai igual"): o mesmo servidor do e2e, outra pasta de testes.
   As referências ficam fora do repositório, em DIGILAB_CAPTURAS (padrão: ../../artifacts_v2_front_react/capturas/). */
import { defineConfig } from "@playwright/test";
import base from "./playwright.config.ts";

const PASTA = process.env.DIGILAB_CAPTURAS ?? "../../artifacts_v2_front_react/capturas";
export default defineConfig({
  ...base,
  testDir: "e2e_capturas",
  fullyParallel: true,
  retries: 0,
  workers: 3,
  snapshotPathTemplate: `${PASTA}/{arg}{ext}`,
  use: { ...base.use, colorScheme: "light", deviceScaleFactor: 1 },
});
