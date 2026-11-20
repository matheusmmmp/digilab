/* A config do Vite só da página do WORLD-POC-01a (docs/TAREFA_V2_WORLD_POC_01.md), fora do build do app: o `npm run build` do jogo não
   a lê, e esta não lê nada do app. A página sai em web/dist_poc/ (não versionado).

     npm run poc            # a página no modo dev (com o atlas do Digimon UP, se ele existir em D:/Trab/digilab/Assets)
     npm run poc:build      # o build da página, em web/dist_poc/ (sem o atlas: o sprite de reserva)
     npm run poc:preview    # serve o build na porta 8800; com -- --host, na rede local (a M3 no celular)

   O atlas (W-6) fica fora do repositório e só é servido no dev, pelos dois arquivos dele, nada mais da pasta Assets. */
import { createReadStream, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";

const AQUI = fileURLToPath(new URL(".", import.meta.url));
const ASSETS = fileURLToPath(new URL("../../../../Assets/", import.meta.url));
const ATLAS: Record<string, string> = {
  "/Assets/digilab_atlas_up.json": "application/json",
  "/Assets/digilab_atlas_up.png": "image/png",
};

function atlasDev(): Plugin {
  return {
    name: "digilab-poc-atlas-dev",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const caminho = (req.url || "").split("?")[0];
        const tipo = ATLAS[caminho];
        if (!tipo) return next();
        const arq = ASSETS + caminho.slice("/Assets/".length);
        if (!existsSync(arq)) { res.statusCode = 404; res.end("atlas nao encontrado"); return; }
        res.setHeader("Content-Type", tipo);
        res.setHeader("Cache-Control", "no-cache");
        createReadStream(arq).pipe(res);
      });
    },
  };
}

export default defineConfig({
  root: AQUI,
  base: "./",
  plugins: [atlasDev()],
  build: {
    outDir: fileURLToPath(new URL("../../dist_poc/", import.meta.url)),
    emptyOutDir: true,
    sourcemap: false,
    target: "es2022",
    /* a página e a raiz que leva a ela (o endereço "Network" do Vite é a raiz; o celular da M3 entra por ele) */
    rollupOptions: { input: [fileURLToPath(new URL("./mundo3d.html", import.meta.url)), fileURLToPath(new URL("./index.html", import.meta.url))] },
  },
  preview: { port: 8800, strictPort: true },
});
