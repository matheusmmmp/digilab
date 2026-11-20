/* Monta o build do jogo COM a chave do servidor (VITE_DIGILAB_API), em web/dist_conta/, antes dos specs desta pasta. O build de sempre
   (web/dist/, sem a chave) e o e2e do jogo nao mudam. */
import { build } from "vite";
import { API, PASTA_BUILD, PASTA_BUILD_NUVEM } from "./comum.ts";

export default async function montar(): Promise<void> {
  process.env.VITE_DIGILAB_API = API;
  /* o marco do cais fica o do jogo (o 10): a variavel do beta nao entra neste build */
  delete process.env.VITE_DIGILAB_MARCO_RANQUEADA;
  await build({ logLevel: "warn", build: { outDir: `../${PASTA_BUILD}`, emptyOutDir: true } });
  /* o save na nuvem (CN3): o mesmo build com a chave dela, noutra pasta */
  process.env.VITE_DIGILAB_NUVEM = "1";
  try { await build({ logLevel: "warn", build: { outDir: `../${PASTA_BUILD_NUVEM}`, emptyOutDir: true } }); } finally { delete process.env.VITE_DIGILAB_NUVEM; }
}
