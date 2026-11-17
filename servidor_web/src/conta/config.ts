/* A configuração da conta pelo ambiente (nada de chave no repositório):
     DIGILAB_BANCO            o arquivo SQLite (padrão servidor_web/dados/conta.sqlite, fora do git); ":memory:" para não gravar
     DIGILAB_URL_API          o endereço público deste servidor (padrão http://127.0.0.1:<porta>); o callback é <URL_API>/auth/callback
     DIGILAB_URL_JOGO         para onde o login devolve o jogador (padrão local: <URL_API>/dev/conta, a página de teste); a origem dele é
                              a única do CORS (RC-6: o jogo no domínio, a API em api.)
     DIGILAB_CONVIDADOS       a lista de convidados (convidados.ts); soma com a tabela
     DIGILAB_PROVEDOR_FALSO   "1" liga, "0" desliga o provedor falso; por padrão, ligado só no local
     DIGILAB_MARCO_RANQUEADA  o marco do Tamer que abre o pedido da semente ranqueada (MMO4): o padrão é o 10, o primeiro Mega (MMO-13); no
                              ambiente do beta, o 7 (BT0-1, D-CONTA-76). Só os marcos do registro do Tamer (MARCOS_DO_TAMER)
     GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET   os apps OAuth (sem elas, o provedor fica desligado)
   "Local" é a API em http:// num endereço de loopback (127.0.0.1, localhost, [::1]). Fora do local, a API tem de ser https://, o cookie
   leva Secure, e o provedor falso não liga (levanta). */
import { fileURLToPath } from "node:url";
import { MARCO_MEGA } from "../../../web/app/src/tamer.ts";
import { abrirBanco, type Banco } from "./banco.ts";
import { Convidados, lerListaAmbiente } from "./convidados.ts";
import { ProvedorFalso, provedoresReais, type Buscar, type NomeProvedor, type Provedor } from "./provedores.ts";

export const BANCO_PADRAO = fileURLToPath(new URL("../../dados/conta.sqlite", import.meta.url));
/** os termos e a privacidade ainda não existem (são da CN6): a versão é a do rascunho; o aceite grava esta versão */
export const VERSAO_TERMOS = "rascunho-2026-11";
export const VERSAO_PRIVACIDADE = "rascunho-2026-11";
/** o convidado padrão do provedor falso no local, quando DIGILAB_CONVIDADOS está vazia */
export const CONVIDADO_FALSO_PADRAO = "falso:ana";
/** os marcos que o registro do Tamer cumpre sozinho (web/app/src/nivel.ts, marcosDoTamer: as medalhas 5, 7 e 8, o título 9 e o Mega 10):
    só eles podem abrir o pedido da semente, porque o servidor os lê do envio conferido */
export const MARCOS_DO_TAMER: readonly number[] = [5, 7, 8, 9, MARCO_MEGA];

export interface ConfigConta {
  banco: Banco;
  provedores: ReadonlyMap<NomeProvedor, Provedor>;
  convidados: Convidados;
  urlApi: string;
  urlJogo: string;
  origemJogo: string;
  local: boolean;
  cookieSeguro: boolean;
  versaoTermos: string;
  versaoPrivacidade: string;
  agora: () => number;
  /** o marco do Tamer que abre o pedido da semente ranqueada (MMO4) */
  marcoRanqueada: number;
}

const LOOPBACK = new Set(["127.0.0.1", "localhost", "[::1]"]);

export function ehLocal(urlApi: string): boolean {
  const u = new URL(urlApi);
  return u.protocol === "http:" && LOOPBACK.has(u.hostname);
}

export interface OpcoesConfig {
  porta: number;
  ambiente?: Record<string, string | undefined>;
  banco?: Banco;
  buscar?: Buscar;
  agora?: () => number;
}

export function configDoAmbiente({ porta, ambiente = process.env, banco, buscar, agora = Date.now }: OpcoesConfig): ConfigConta {
  const urlApi = (ambiente.DIGILAB_URL_API?.trim() || `http://127.0.0.1:${porta}`).replace(/\/+$/, "");
  const local = ehLocal(urlApi);
  if (!local && new URL(urlApi).protocol !== "https:") throw new Error(`DIGILAB_URL_API fora do local precisa de https://: ${urlApi}`);
  const urlJogo = ambiente.DIGILAB_URL_JOGO?.trim() || (local ? `${urlApi}/dev/conta` : "");
  if (!urlJogo) throw new Error("fora do local, DIGILAB_URL_JOGO é obrigatória (a origem do CORS)");
  const origemJogo = new URL(urlJogo).origin;
  if (!local && !origemJogo.startsWith("https://")) throw new Error(`DIGILAB_URL_JOGO fora do local precisa de https://: ${urlJogo}`);

  const chaveFalso = ambiente.DIGILAB_PROVEDOR_FALSO?.trim();
  if (chaveFalso !== undefined && chaveFalso !== "" && chaveFalso !== "0" && chaveFalso !== "1")
    throw new Error(`DIGILAB_PROVEDOR_FALSO é "0" ou "1": ${chaveFalso}`);
  const falso = chaveFalso === "1" || ((chaveFalso === undefined || chaveFalso === "") && local);
  if (falso && !local) throw new Error("o provedor falso só liga no local (DIGILAB_URL_API em http://127.0.0.1)");

  const lista = lerListaAmbiente(ambiente.DIGILAB_CONVIDADOS);
  if (falso && lista.size === 0) lista.add(CONVIDADO_FALSO_PADRAO);

  const textoMarco = ambiente.DIGILAB_MARCO_RANQUEADA?.trim();
  const marcoRanqueada = textoMarco ? Number(textoMarco) : MARCO_MEGA;
  if (!MARCOS_DO_TAMER.includes(marcoRanqueada))
    throw new Error(`DIGILAB_MARCO_RANQUEADA é um dos marcos do Tamer (${MARCOS_DO_TAMER.join(", ")}): ${textoMarco}`);

  const b = banco ?? abrirBanco(ambiente.DIGILAB_BANCO?.trim() || BANCO_PADRAO);
  const provedores = new Map<NomeProvedor, Provedor>();
  for (const p of provedoresReais(ambiente, buscar)) provedores.set(p.nome, p);
  if (falso) provedores.set("falso", new ProvedorFalso(urlApi, agora));
  return { banco: b, provedores, convidados: new Convidados(b, lista), urlApi, urlJogo, origemJogo, local, cookieSeguro: !local,
    versaoTermos: VERSAO_TERMOS, versaoPrivacidade: VERSAO_PRIVACIDADE, agora, marcoRanqueada };
}
