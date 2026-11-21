/// <reference types="vitest/config" />
/* Vite + React (TAREFA_FRONT_TS, Etapa 3; React no lugar do Preact desde TAREFA_V2_FRONT_REACT). O build sai em web/dist/ (nao versionado) com caminhos relativos,
   para o servidor_local.py servir em /v1/web/dist/. O atlas do Digimon UP fica FORA do repositorio
   (D:/Trab/digilab/Assets): a pagina pede ../../../Assets/digilab_atlas_up_pecas.json e digilab_atlas_up_clipes.json, que no servidor local cai em
   /Assets/ e no modo dev e servido por este config (so os arquivos do atlas e da decoracao listada em decoracao_nomes.json, nada mais). */
import { createReadStream, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { tipoDoAssetPublico } from "./scripts/assets_publicos.ts";
import { AVISO_AUTORIA } from "./scripts/autoria.ts";

const ASSETS = fileURLToPath(new URL("../../../Assets/", import.meta.url));
/* o atlas, a decoracao listada, os sons, os cenarios da luta e a cena de evolucao: a lista do que se publica (scripts/assets_publicos.ts) */

/* os mapas do habitat que nao se redistribuem (src/habitat.ts, so no dev): o kit Tiny Fantasy Forest (Unity Asset Store EULA) e os assets
   do Cassette Beasts extraidos pelas ferramentas de D:/Trab/digilab/extrair_cb; so modelos, texturas e o json, sem ".." no caminho */
const KITS_DEV_ROTA = /^\/Assets\/kits3d\/(tiny_fantasy_forest|cassette_beasts)\/(?!.*\.\.)[A-Za-z0-9_ ./()-]+\.(fbx|png|webp|json)$/;
const TIPO_KIT: Record<string, string> = { fbx: "application/octet-stream", png: "image/png", webp: "image/webp", json: "application/json" };

/** dev: serve so o atlas, a decoracao listada, os sons, os cenarios da luta, a cena de evolucao e os kits dos mapas do dev (nada mais da pasta Assets) */
function atlasDev(): Plugin {
  return {
    name: "digilab-atlas-dev",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        let caminho = (req.url || "").split("?")[0];
        try { caminho = decodeURIComponent(caminho); } catch { return next(); }
        const tipo = tipoDoAssetPublico(caminho) ?? (KITS_DEV_ROTA.test(caminho) ? TIPO_KIT[caminho.split(".").pop()!] : undefined);
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

/** PI2 (docs/PLANO_V3_CONTA_PROTECAO.md, PI-4): o aviso de autoria no topo de cada JS do build, posto depois da minificacao (o
    scripts/conferir_build.ts confere, no "npm run build"); o build continua sem source map */
function avisoAutoria(): Plugin {
  return {
    name: "digilab-aviso-autoria",
    apply: "build",
    generateBundle(_opcoes, pacote) {
      for (const peca of Object.values(pacote)) {
        if (peca.type === "chunk" && !peca.code.startsWith(AVISO_AUTORIA)) peca.code = AVISO_AUTORIA + "\n" + peca.code;
      }
    },
  };
}

export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss(), atlasDev(), avisoAutoria()],
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
