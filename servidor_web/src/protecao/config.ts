/* A configuração da proteção (CN4) pelo ambiente; nada de chave no repositório:
     DIGILAB_SEGREDO_ASSETS     o segredo do HMAC das URLs dos assets (pelo menos 32 caracteres). Sem ele, as URLs assinadas ficam
                                desligadas (as rotas /assets/* respondem 503 e dizem por quê)
     DIGILAB_URL_ASSETS         a base dos assets (na CN5, o R2 atrás da Cloudflare); no local, o padrão é <URL_API>/assets
     DIGILAB_VALIDADE_ASSETS_S  quanto uma URL assinada vale, em segundos (padrão VALIDADE_ASSETS_S)
     DIGILAB_DIR_ASSETS         só no local: a pasta que o GET /assets/* serve depois de conferir a assinatura (padrão: web/app/public)
     TURNSTILE_SECRET_KEY, TURNSTILE_SITE_KEY   o Turnstile; fora do local, sem eles o servidor não sobe, a não ser com DIGILAB_TURNSTILE=0
     DIGILAB_TURNSTILE          "0" desliga, "1" liga (pede as duas chaves); por padrão, ligado quando há o segredo
     DIGILAB_COTA_FALA_DIA      as falas pela LLM por conta por dia de Brasília (padrão COTA_FALA_DIA)
     DIGILAB_FALA_SO_COM_CONTA  "1": a fala sem a sessão é só template; "0": a fala sem a sessão segue o teto total, como na CN1. Padrão:
                                "1" fora do local, "0" no local (o npm run dev do jogo fala sem entrar) */
import { fileURLToPath } from "node:url";
import { TurnstileCloudflare, type Buscar, type Turnstile } from "./turnstile.ts";

/* os números (PROPOSTOS, SEM FONTE) */
/** a cota de falas pela LLM por conta por dia: o número da seção 6 do plano */
export const COTA_FALA_DIA = 30;
/** a vida de uma URL assinada: o bastante para carregar a tela, curta para não virar um link fixo */
export const VALIDADE_ASSETS_S = 600;
/** quantos caminhos um pedido assina */
export const CAMINHOS_POR_PEDIDO = 64;
/** quantos caminhos uma conta ou um visitante assina por hora: o jogo inteiro pede umas centenas; um robô que raspa pede milhares */
export const ASSINATURAS_POR_HORA = 2000;
/** a vida do cookie do visitante que passou pelo Turnstile */
export const DURACAO_VISITANTE_MS = 24 * 3600_000;
export const TAMANHO_MINIMO_SEGREDO = 32;

export const DIR_ASSETS_PADRAO = fileURLToPath(new URL("../../../web/app/public", import.meta.url));

export interface ConfigProtecao {
  /** null: as URLs assinadas desligadas, com o motivo em `motivoAssets` */
  segredoAssets: string | null;
  motivoAssets: string;
  urlAssets: string;
  validadeAssetsS: number;
  /** a pasta servida pelo GET /assets/* no local; null fora do local (lá, quem serve é a borda) */
  dirAssets: string | null;
  /** null: o Turnstile desligado */
  turnstile: Turnstile | null;
  cotaFalaDia: number;
  falaSoComConta: boolean;
}

const chave01 = (nome: string, v: string | undefined): boolean | undefined => {
  const t = v?.trim();
  if (t === undefined || t === "") return undefined;
  if (t !== "0" && t !== "1") throw new Error(`${nome} é "0" ou "1": ${t}`);
  return t === "1";
};

const inteiroPositivo = (nome: string, v: string | undefined, padrao: number): number => {
  const t = v?.trim();
  if (t === undefined || t === "") return padrao;
  const n = Number(t);
  if (!Number.isInteger(n) || n < 0) throw new Error(`${nome} é um inteiro >= 0: ${t}`);
  return n;
};

export function protecaoDoAmbiente(ambiente: Record<string, string | undefined>, local: boolean, urlApi: string,
  buscarTurnstile?: Buscar): ConfigProtecao {
  const segredo = ambiente.DIGILAB_SEGREDO_ASSETS?.trim() ?? "";
  if (segredo !== "" && segredo.length < TAMANHO_MINIMO_SEGREDO)
    throw new Error(`DIGILAB_SEGREDO_ASSETS precisa de pelo menos ${TAMANHO_MINIMO_SEGREDO} caracteres`);
  const urlAssets = (ambiente.DIGILAB_URL_ASSETS?.trim() || (local ? `${urlApi}/assets` : "")).replace(/\/+$/, "");
  if (segredo !== "" && urlAssets === "") throw new Error("fora do local, as URLs assinadas pedem DIGILAB_URL_ASSETS");
  if (urlAssets !== "" && !local && !urlAssets.startsWith("https://")) throw new Error(`DIGILAB_URL_ASSETS fora do local precisa de https://: ${urlAssets}`);
  const validade = inteiroPositivo("DIGILAB_VALIDADE_ASSETS_S", ambiente.DIGILAB_VALIDADE_ASSETS_S, VALIDADE_ASSETS_S);
  if (validade === 0) throw new Error("DIGILAB_VALIDADE_ASSETS_S precisa ser maior que 0");
  if (!local && ambiente.DIGILAB_DIR_ASSETS?.trim()) throw new Error("DIGILAB_DIR_ASSETS é só do local (fora dele, a borda serve os assets)");

  const segredoTs = ambiente.TURNSTILE_SECRET_KEY?.trim() ?? "", siteTs = ambiente.TURNSTILE_SITE_KEY?.trim() ?? "";
  const ligarTs = chave01("DIGILAB_TURNSTILE", ambiente.DIGILAB_TURNSTILE);
  let turnstile: Turnstile | null = null;
  if (ligarTs === true || (ligarTs === undefined && segredoTs !== "")) turnstile = new TurnstileCloudflare(segredoTs, siteTs, buscarTurnstile);
  else if (ligarTs === undefined && !local)
    throw new Error("fora do local, o Turnstile pede TURNSTILE_SECRET_KEY e TURNSTILE_SITE_KEY (ou DIGILAB_TURNSTILE=0 para desligar de propósito)");

  return {
    segredoAssets: segredo === "" ? null : segredo,
    motivoAssets: segredo === "" ? "sem DIGILAB_SEGREDO_ASSETS no ambiente" : "",
    urlAssets,
    validadeAssetsS: validade,
    dirAssets: local ? (ambiente.DIGILAB_DIR_ASSETS?.trim() || DIR_ASSETS_PADRAO) : null,
    turnstile,
    cotaFalaDia: inteiroPositivo("DIGILAB_COTA_FALA_DIA", ambiente.DIGILAB_COTA_FALA_DIA, COTA_FALA_DIA),
    falaSoComConta: chave01("DIGILAB_FALA_SO_COM_CONTA", ambiente.DIGILAB_FALA_SO_COM_CONTA) ?? !local,
  };
}
