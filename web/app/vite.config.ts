/// <reference types="vitest/config" />
/* Vite + Preact (TAREFA_FRONT_TS, Etapa 3). O build sai em web/dist/ (nao versionado) com caminhos relativos,
   para o servidor_local.py servir em /v1/web/dist/. O atlas do Digimon UP fica FORA do repositorio
   (D:/Trab/digilab/Assets): a pagina pede ../../../Assets/digilab_atlas_up.json, que no servidor local cai em
   /Assets/ e no modo dev e servido por este config (so os dois arquivos do atlas). */
import { createReadStream, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";
import preact from "@preact/preset-vite";

const ASSETS = fileURLToPath(new URL("../../../Assets/", import.meta.url));
const ATLAS: Record<string, string> = { "/Assets/digilab_atlas_up.json": "application/json", "/Assets/digilab_atlas_up.png": "image/png" };

/** dev: serve so o atlas (nada mais da pasta Assets) */
function atlasDev(): Plugin {
  return {
    name: "digilab-atlas-dev",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const caminho = (req.url || "").split("?")[0];
        const tipo = ATLAS[caminho];
        if (!tipo) return next();
        const arq = ASSETS + caminho.slice("/Assets/".length);
        if (!existsSync(arq)) { res.statusCode = 404; res.end("atlas nao encontrado: " + arq); return; }
        res.setHeader("Content-Type", tipo);
        res.setHeader("Cache-Control", "no-cache");
        createReadStream(arq).pipe(res);
      });
    },
  };
}

export default defineConfig({
  base: "./",
  plugins: [preact(), atlasDev()],
  build: { outDir: "../dist", emptyOutDir: true, sourcemap: false, target: "es2022" },
  /* fala por LLM: o servidor local (python servidor/servidor_local.py) responde /api/fala */
  server: { proxy: { "/api": "http://127.0.0.1:8765" } },
  test: {
    include: ["test/**/*.test.{mjs,ts}"],
    environment: "node",
    testTimeout: 180_000,
    hookTimeout: 180_000,
  },
});
