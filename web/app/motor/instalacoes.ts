/* As instalacoes da Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4b; so no jogo). Depois do titulo da
   Liga, a Fronteira abre a Torre de Batalha: uma sequencia de lutas contra Megas sorteados (as 8 formas adultas, de especies variadas), sem
   cura entre elas (a vida do pet passa de uma para a outra, como na Liga); perdeu, acabou. Recorde: a maior sequencia de vitorias. Na luta da
   POC (LUTA_POC, LP2b; LP4) cada rival luta com o perfil canonico do Mega pelo mapeamento da LP2-2, no Ringue (MAPA_TORRE, PROPOSTO), ate o
   teto de LUTAS_MAX_INSTALACAO. O Palacio juntou-se a Torre (LP-5): a diferenca dele era o pet decidir sem as regras do dono, e na luta
   nova todo pet decide sozinho; ele fica na tabela porque o registro do Tamer guarda os recordes dele.

   Registro e replay: a tentativa inteira e UM evento de luta "l" do registro do pet, com o rival = o id da instalacao e a semente da
   tentativa, que sai do registro do pet: sementeTentativa(semente do pet, instalacao, numero da tentativa dele nela). O motor confere a
   semente na hora de lutar e no replay (outra semente falha alto): ninguem escolhe os rivais. Os rivais de cada luta sao sorteados dessa
   semente (formaRivalInstalacao). A entrada pede o titulo do Tamer, que o pet conhece pelo evento "f" (Motor.abrirFronteira; o motor nunca
   le o Tamer). O recorde vai para o registro do Tamer (src/tamer.ts, evento "recorde"). */
import { ESPECIES, FORMAS_AD, LINHA_DA_FORMA } from "./constantes.ts";
import { VERSAO_LIGA } from "./liga.ts";
import { criarRng, hashSemente } from "./rng.ts";
import type { Forma } from "./tipos.ts";

/** versao de pet em que as instalacoes existem (a da Liga) */
export const VERSAO_INSTALACOES = VERSAO_LIGA;
export type IdInstalacao = "torre_batalha" | "palacio";
export interface Instalacao {
  /** o id: a chave do rival no evento de luta "l" e da instalacao no evento "recorde" do Tamer */
  id: IdInstalacao;
  /** o nome na tela */
  nome: string;
  /** "sequencia": a Torre; "sozinho": o Palacio de antes, que se juntou a Torre (LP-5) */
  regra: "sequencia" | "sozinho";
  /** a regra em uma frase, na tela */
  frase: string;
}
export const INSTALACOES: readonly Instalacao[] = [
  { id: "torre_batalha", nome: "Torre de Batalha", regra: "sequencia",
    frase: "Megas sorteados, um depois do outro, sem cura entre as lutas. Perdeu, acabou." },
  { id: "palacio", nome: "Palácio", regra: "sozinho",
    frase: "O Palácio juntou-se à Torre de Batalha: na luta nova todo pet decide sozinho." },
];
export const INSTALACAO_POR_ID: Readonly<Record<string, Instalacao>> = Object.fromEntries(INSTALACOES.map(x => [x.id, x]));
/** o rival do evento de luta e uma instalacao */
export const ehInstalacao = (r: string): r is IdInstalacao => Object.hasOwn(INSTALACAO_POR_ID, r);
export function instalacaoDe(id: string): Instalacao {
  const x = ehInstalacao(id) ? INSTALACAO_POR_ID[id] : undefined;
  if (!x) throw new Error("instalação da Fronteira desconhecida: " + JSON.stringify(id));
  return x;
}
/** o teto de lutas de uma tentativa: quem vence todas termina a sequencia com esse recorde (a tentativa e um evento so e precisa acabar).
    Na conferencia (test/conferir_instalacoes.mjs) nenhum pet de referencia chegou perto dele */
export const LUTAS_MAX_INSTALACAO = 100;

/** a semente da tentativa n (1 = a primeira) do pet na instalacao: sai do registro do pet (a semente dele e quantas tentativas ele ja fez
    ali), e o motor confere */
export const sementeTentativa = (pet: number, inst: IdInstalacao, n: number): number => {
  if (!Number.isInteger(n) || n < 1) throw new Error("número de tentativa inválido: " + n);
  return hashSemente("fronteira", inst, pet, n);
};
/** o Mega do rival da luta k (0 = a primeira) da tentativa de semente s: uma das 8 formas adultas, numa das 4 especies, sorteadas de uma
    rng propria da luta (ramo sereno, como os bots canonicos da bateria) */
export function formaRivalInstalacao(s: number, k: number): Forma {
  if (!Number.isInteger(k) || k < 0) throw new Error("luta da instalação inválida: " + k);
  const r = criarRng(hashSemente("fronteira-rival", s, k)), adulta = FORMAS_AD[r.int(FORMAS_AD.length)], esp = ESPECIES[r.int(ESPECIES.length)];
  return { esp, est: "mega", ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta };
}
