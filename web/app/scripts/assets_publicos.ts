/* Os assets de fora do repositório que o jogo pede e que se publicam (CN5): o atlas, a decoração listada em decoracao_nomes.json, os sons,
   os cenários da luta e a cena da evolução. É a mesma lista que o dev do Vite serve (vite.config.ts) e a que o
   scripts/publicar_assets.ts manda ao R2. Os kits do habitat que não se redistribuem (o Tiny Fantasy Forest, pela EULA da Unity Asset
   Store, e o Cassette Beasts) ficam FORA: são só do dev. */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

/* decoracao do Digimon UP (Assets/gerar_decoracao_up.py): o JSON e so os PNGs da lista do repositorio */
const DECORACAO: string[] = JSON.parse(readFileSync(new URL("../decoracao_nomes.json", import.meta.url), "utf8")).pecas;
const ATLAS: Record<string, string> = {
  "/Assets/digilab_atlas_up_pecas.json": "application/json", "/Assets/digilab_atlas_up_pecas.png": "image/png",
  "/Assets/digilab_atlas_up_clipes.json": "application/json", "/Assets/digilab_atlas_up_clipes.png": "image/png",
  "/Assets/digilab_decoracao_up.json": "application/json",
  ...Object.fromEntries(DECORACAO.map(n => [`/Assets/decoracao_up/${n}.png`, "image/png"])),
};
/* sons do Digimon UP (Assets/gerar_sons_up.py, src/som.ts): o mapa.json e so os MP3 dentro de Assets/sons/ (nome simples, nada de caminho) */
const SOM_ROTA = /^\/Assets\/sons\/(mapa\.json|[A-Za-z0-9_]+\.mp3)$/;
/* os cenarios da luta em tempo real (Assets/gerar_arena_up.py, src/telas/lutar/palcoTR/cenasTR.ts): so os PNG/JPG de mapas/ (nome simples) */
const ARENA_ROTA = /^\/Assets\/arena_up\/(mapas\/[a-z0-9_]+\.(png|jpg)|efeitos\/[A-Za-z0-9_]+\.png|dados\/efeitos\.json)$/;
const TIPO_ARENA: Record<string, string> = { png: "image/png", jpg: "image/jpeg", json: "application/json" };
/* cena de evolucao (Assets/gerar_evolucao_up.py, src/evolucaoUp.ts): o mapa.json e os pacotes de nome simples de pacotes/ */
const EVOLUCAO_ROTA = /^\/Assets\/evolucao_up\/(mapa\.json|pacotes\/[a-z0-9_]+\.bin)$/;

/** o tipo do asset publicável pelo caminho da página ("/Assets/..."), ou undefined se ele não se publica */
export function tipoDoAssetPublico(caminho: string): string | undefined {
  return ATLAS[caminho] ?? (SOM_ROTA.test(caminho) ? (caminho.endsWith(".json") ? "application/json" : "audio/mpeg")
    : ARENA_ROTA.test(caminho) ? TIPO_ARENA[caminho.split(".").pop()!]
    : EVOLUCAO_ROTA.test(caminho) ? (caminho.endsWith(".json") ? "application/json" : "application/octet-stream")
    : undefined);
}

export interface AssetPublico { chave: string; arquivo: string; tipo: string; bytes: number }

/** os arquivos publicáveis que existem em `raiz` (a pasta Assets), em ordem: a chave no R2 é o caminho sem o "/Assets/" */
export function listarAssetsPublicos(raiz: string): AssetPublico[] {
  const achados: AssetPublico[] = [];
  const andar = (rel: string) => {
    for (const nome of readdirSync(join(raiz, rel))) {
      const r = rel === "" ? nome : `${rel}/${nome}`;
      const arq = join(raiz, r);
      const st = statSync(arq);
      if (st.isDirectory()) {
        /* só desce nas pastas que têm o que se publica (nada de kits3d, remaster, extratores) */
        if (["decoracao_up", "sons", "arena_up", "arena_up/mapas", "arena_up/efeitos", "arena_up/dados", "evolucao_up", "evolucao_up/pacotes"].includes(r)) andar(r);
        continue;
      }
      const tipo = tipoDoAssetPublico(`/Assets/${r}`);
      if (tipo) achados.push({ chave: r, arquivo: arq, tipo, bytes: st.size });
    }
  };
  andar("");
  return achados.sort((a, b) => (a.chave < b.chave ? -1 : a.chave > b.chave ? 1 : 0));
}

/** os arquivos da lista fixa (o atlas e a decoração listada) que faltam em `raiz`: o envio para se faltar algum */
export function faltandoNaLista(raiz: string, achados: AssetPublico[]): string[] {
  const tem = new Set(achados.map(a => a.chave));
  return Object.keys(ATLAS).map(c => c.slice("/Assets/".length)).filter(c => !tem.has(c));
}
