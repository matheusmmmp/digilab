/* A config do Vite só da página do WORLD-POC-01a (docs/TAREFA_V2_WORLD_POC_01.md, etapa E0), fora do build do app: o
   `npm run build` do jogo não a lê, e esta não lê nada do app. A página sai em web/dist_poc/ (não versionado).

     npm run poc          # a página no modo dev
     npm run poc:build    # o build da página, em web/dist_poc/ */
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const AQUI = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  root: AQUI,
  base: "./",
  build: {
    outDir: fileURLToPath(new URL("../../dist_poc/", import.meta.url)),
    emptyOutDir: true,
    sourcemap: false,
    target: "es2022",
    rollupOptions: { input: fileURLToPath(new URL("./mundo3d.html", import.meta.url)) },
  },
});
