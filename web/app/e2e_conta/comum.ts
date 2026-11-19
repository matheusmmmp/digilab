/* O que a configuracao (playwright.conta.config.ts), a montagem do build (montar.ts) e os specs desta pasta dividem: a porta, a pasta do
   build com a chave do servidor e o endereco do servidor falso. O servidor falso nao existe como processo: e o `page.route` de cada
   spec, na MESMA origem da pagina (sem CORS). Nenhum endereco de servidor de verdade e nenhuma chave entram aqui. */
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

/** DIGILAB_PORTA_E2E_CONTA: outra porta quando a 8801 esta ocupada (o e2e do jogo usa a 8799 e o da POC, a 8800) */
export const PORTA = Number(process.env.DIGILAB_PORTA_E2E_CONTA ?? 8801);
export const REPO = fileURLToPath(new URL("../../..", import.meta.url));
export const PREFIXO = "/" + basename(REPO);
/** a pasta do build com a chave, ao lado de web/dist (nao versionada) */
export const PASTA_BUILD = "dist_conta";
export const APP = `${PREFIXO}/web/${PASTA_BUILD}/`;
/** o endereco que o build recebe em VITE_DIGILAB_API: um caminho da propria origem, que so o `page.route` responde */
export const CAMINHO_API = "/api_falsa";
export const API = `http://127.0.0.1:${PORTA}${CAMINHO_API}`;
