/// <reference types="vitest/config" />
/* Vite + Preact (TAREFA_FRONT_TS, Etapa 3). O build sai em web/dist/ (nao versionado) com caminhos relativos,
   para o servidor_local.py servir em /v1/web/dist/. O atlas do Digimon UP fica FORA do repositorio
   (D:/Trab/digilab/Assets): a pagina pede ../../../Assets/digilab_atlas_up.json, que no servidor local cai em
   /Assets/ e no modo dev e servido por este config (so os arquivos do atlas e da decoracao listada em decoracao_nomes.json, nada mais). */
import { createReadStream, existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";
import preact from "@preact/preset-vite";

const ASSETS = fileURLToPath(new URL("../../../Assets/", import.meta.url));
/* decoracao do Digimon UP (Assets/gerar_decoracao_up.py): o JSON e so os PNGs da lista do repositorio */
const DECORACAO: string[] = JSON.parse(readFileSync(new URL("./decoracao_nomes.json", import.meta.url), "utf8")).pecas;
const ATLAS: Record<string, string> = {
  "/Assets/digilab_atlas_up.json": "application/json", "/Assets/digilab_atlas_up.png": "image/png",
  "/Assets/digilab_decoracao_up.json": "application/json",
  ...Object.fromEntries(DECORACAO.map(n => [`/Assets/decoracao_up/${n}.png`, "image/png"])),
};

/** dev: serve so o atlas e a decoracao listada (nada mais da pasta Assets) */
function atlasDev(): Plugin {
  return {
    name: "digilab-atlas-dev",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const caminho = (req.url || "").split("?")[0];
        const tipo = ATLAS[caminho];
        if (!tipo) return next();
        const arq = ASSETS + caminho.slice("/Assets/".length);
        if (!existsSync(arq)) { res.statusCode = 404; res.end("asset nao encontrado: " + arq); return; }
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
