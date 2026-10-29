/// <reference types="vitest/config" />
/* Vite + React (TAREFA_FRONT_TS, Etapa 3; React no lugar do Preact desde TAREFA_V2_FRONT_REACT). O build sai em web/dist/ (nao versionado) com caminhos relativos,
   para o servidor_local.py servir em /v1/web/dist/. O atlas do Digimon UP fica FORA do repositorio
   (D:/Trab/digilab/Assets): a pagina pede ../../../Assets/digilab_atlas_up.json (e, com a chave CLIPES_UP, digilab_atlas_up_clipes.json), que no servidor local cai em
   /Assets/ e no modo dev e servido por este config (so os arquivos do atlas e da decoracao listada em decoracao_nomes.json, nada mais). */
import { createReadStream, existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const ASSETS = fileURLToPath(new URL("../../../Assets/", import.meta.url));
/* decoracao do Digimon UP (Assets/gerar_decoracao_up.py): o JSON e so os PNGs da lista do repositorio */
const DECORACAO: string[] = JSON.parse(readFileSync(new URL("./decoracao_nomes.json", import.meta.url), "utf8")).pecas;
const ATLAS: Record<string, string> = {
  "/Assets/digilab_atlas_up.json": "application/json", "/Assets/digilab_atlas_up.png": "image/png",
  "/Assets/digilab_atlas_up_clipes.json": "application/json", "/Assets/digilab_atlas_up_clipes.png": "image/png",
  "/Assets/digilab_decoracao_up.json": "application/json",
  ...Object.fromEntries(DECORACAO.map(n => [`/Assets/decoracao_up/${n}.png`, "image/png"])),
};

/* sons do Digimon UP (Assets/gerar_sons_up.py, src/som.ts): o mapa.json e so os MP3 dentro de Assets/sons/ (nome simples, nada de caminho) */
const SOM_ROTA = /^\/Assets\/sons\/(mapa\.json|[A-Za-z0-9_]+\.mp3)$/;

/** dev: serve so o atlas e a decoracao listada (nada mais da pasta Assets) */
function atlasDev(): Plugin {
  return {
    name: "digilab-atlas-dev",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const caminho = (req.url || "").split("?")[0];
        const tipo = ATLAS[caminho] ?? (SOM_ROTA.test(caminho) ? (caminho.endsWith(".json") ? "application/json" : "audio/mpeg") : undefined);
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
  plugins: [react(), tailwindcss(), atlasDev()],
  /* "@/" = src/, o alias dos componentes no estilo shadcn (components.json) */
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
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
