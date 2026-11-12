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
  /* o mapa do Animal Crossing (mapa_ac.html): os clipes (Idle e Run) do pet */
  "/Assets/digilab_atlas_up_clipes.json": "application/json",
  "/Assets/digilab_atlas_up_clipes.png": "image/png",
};
/* a demo do Cassette Beasts (cassette.html) lê de Assets/kits3d/cassette_beasts/ as texturas .webp e o mapa em .json, extraídos do jogo
   do Matheus pelas ferramentas de D:/Trab/digilab/extrair_cb (não se redistribui; fora do repositório, como o resto dos kits).
   os kits 3D do mapa_ac (Kenney Nature Kit, Quaternius Stylized Nature MegaKit Standard, KayKit Forest Nature Pack FREE, CC0) e do campo
   lateral (RPG Tiny Fantasy Forest PBR, da Dungeon Mason, Unity Asset Store EULA: não se redistribui), baixados em Assets/kits3d/ e fora
   do repositório: só modelos e texturas, sem ".." no caminho */
const KITS_ROTA = /^\/Assets\/kits3d\/(?!.*\.\.)[A-Za-z0-9_ ./()-]+\.(gltf|glb|bin|png|fbx|webp|json)$/;
const TIPO_KIT: Record<string, string> = { gltf: "model/gltf+json", glb: "model/gltf-binary", bin: "application/octet-stream", png: "image/png",
  fbx: "application/octet-stream", webp: "image/webp", json: "application/json" };

function atlasDev(): Plugin {
  return {
    name: "digilab-poc-atlas-dev",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const caminho = decodeURIComponent((req.url || "").split("?")[0]);
        const tipo = ATLAS[caminho] ?? (KITS_ROTA.test(caminho) ? TIPO_KIT[caminho.split(".").pop()!] : undefined);
        if (!tipo) return next();
        const arq = ASSETS + caminho.slice("/Assets/".length);
        if (!existsSync(arq)) { res.statusCode = 404; res.end("asset nao encontrado"); return; }
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
    rollupOptions: { input: [fileURLToPath(new URL("./mundo3d.html", import.meta.url)), fileURLToPath(new URL("./index.html", import.meta.url)),
      fileURLToPath(new URL("./mapa_ac.html", import.meta.url)),
      fileURLToPath(new URL("./lateral.html", import.meta.url)), fileURLToPath(new URL("./floresta.html", import.meta.url)),
      fileURLToPath(new URL("./voxel.html", import.meta.url)), fileURLToPath(new URL("./cassette.html", import.meta.url))] },
  },
  preview: { port: 8800, strictPort: true },
});
