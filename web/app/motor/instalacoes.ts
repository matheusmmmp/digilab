/* As instalacoes da Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4b; so no jogo e so nos pets v6). Depois
   do titulo da Liga, a Fronteira abre duas instalacoes que usam o pet do jogador, para rejogar por recorde, nunca por forca:
   - Torre de Batalha: uma sequencia de lutas contra Megas sorteados (os bots canonicos das 8 formas adultas, de especies variadas, na
     escala dos pets v6), sem cura entre elas (a vida e o guts do pet passam de uma para a outra, como na Liga); perdeu, acabou. Os chips
     equipados valem e as cartas nao (como na Liga); o limite de turnos e do desafiado, o rival. Recorde: a maior sequencia de vitorias;
   - Palacio: a mesma sequencia, mas o pet decide sozinho: as travas, os vetos e as regras dos chips de regra nao valem (a lista que ele
     faria sem o dono, GambitsPet.listaPalacio, a do Lago sem os chips). Os chips de stat valem (sao treino, nao decisao). Recorde: a maior
     sequencia.
   A forca dos rivais: o Mega na escala dos pets v6, sem treino, vezes FATOR_INSTALACAO = 1, o mesmo da Liga (motor/liga.ts). SEM calibracao
   (decisao do Matheus: sem rodada de equilibrio nesta parte); test/conferir_instalacoes.mjs so confere que as duas sao jogaveis.

   Registro e replay: a tentativa inteira e UM evento de luta "l" do registro do pet, com o rival = o id da instalacao e a semente da
   tentativa, que sai do registro do pet: sementeTentativa(semente do pet, instalacao, numero da tentativa dele nela). O motor confere a
   semente na hora de lutar e no replay (outra semente falha alto): ninguem escolhe os rivais. Os rivais de cada luta sao sorteados dessa
   semente (rivalInstalacao); as lutas 2 em diante usam as sementes derivadas da serie (arenas.sementeDaSerie). A entrada pede o titulo do
   Tamer, que o pet conhece pelo evento "f" (Motor.abrirFronteira; o motor nunca le o Tamer). O recorde vai para o registro do Tamer
   (src/tamer.ts, evento "recorde"). Nenhuma instalacao da item, treino ou stat: o pet sai delas como entrou, fora o que toda luta ja faz
   (aprender regras de combate, contar lutas e vitorias, lesao na derrota). */
import { copiarGambits, gambitsAdulto } from "./bots.ts";
import { ESCALA, caraterCanonico, perfilDe } from "./catalogo.ts";
import { CV, ESPECIES, FORMAS_AD, LINHA_DA_FORMA, VERSAO_PET } from "./constantes.ts";
import type { Lutador, RegrasLuta } from "./combate.ts";
import { VERSAO_LIGA } from "./liga.ts";
import { nomeForma } from "./nomes.ts";
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
  /** "sequencia": a lista do pet como ela esta (chips valem); "sozinho": o pet decide sozinho (sem travas, vetos nem chips de regra) */
  regra: "sequencia" | "sozinho";
  /** a regra em uma frase, na tela */
  frase: string;
}
export const INSTALACOES: readonly Instalacao[] = [
  { id: "torre_batalha", nome: "Torre de Batalha", regra: "sequencia",
    frase: "Megas sorteados, um depois do outro, sem cura entre as lutas. Os chips valem, as cartas não. Perdeu, acabou." },
  { id: "palacio", nome: "Palácio", regra: "sozinho",
    frase: "A mesma sequência, mas o pet decide sozinho: as suas travas, os vetos e os chips de regra não valem." },
];
export const INSTALACAO_POR_ID: Readonly<Record<string, Instalacao>> = Object.fromEntries(INSTALACOES.map(x => [x.id, x]));
/** o rival do evento de luta e uma instalacao */
export const ehInstalacao = (r: string): r is IdInstalacao => Object.hasOwn(INSTALACAO_POR_ID, r);
export function instalacaoDe(id: string): Instalacao {
  const x = ehInstalacao(id) ? INSTALACAO_POR_ID[id] : undefined;
  if (!x) throw new Error("instalação da Fronteira desconhecida: " + JSON.stringify(id));
  return x;
}
/** o fator de rival dos Megas das instalacoes: 1, o da Liga (sem calibracao) */
export const FATOR_INSTALACAO = 1;
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
/** o lutador do rival da luta k: o Mega com a tecnica da linha, a passiva da forma, o carater canonico e a lista canonica dele sob as
    regras da luta; epsilon dos bots canonicos. Com a escala ligada (o app): E = vida do Mega na escala dos pets x
    fator, sem treino (como os Megas da Liga) */
export function rivalInstalacao(s: number, k: number, R: RegrasLuta, fator: number = FATOR_INSTALACAO): Lutador {
  const f = formaRivalInstalacao(s, k), adulta = f.adulta as (typeof FORMAS_AD)[number];
  const p = perfilDe(f, caraterCanonico(adulta), 1, null, true, VERSAO_PET);
  const cond = ESCALA.ligada ? { ...p, escala: p.escala! * fator } : p;
  return { nome: "Rival " + nomeForma(f), estilo: { nome: `fronteira:${adulta}`, gambits: copiarGambits(gambitsAdulto(adulta, R)), eps: CV.eps }, cond };
}
