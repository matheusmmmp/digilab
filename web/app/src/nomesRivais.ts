/* Nome na tela de cada rival pela chave do registro (a luta "l" guarda so a chave): NPC da campanha e lider pelo nome dele,
   bot adulto pelo Digimon da forma, bot classico pelo Digimon dele, Liga e instalacoes da Fronteira pelo nome. Usado pela
   voz propria (os fatos da historia falam do rival pelo nome) e pela tela da luta. */
import { BOTS_V21, NOME_BOT, NPC, RIVAL_LIGA, RIVAL_SALAO, ehInstalacao, formaRival, instalacaoDe, nomeForma, type FormaAdultaNormal } from "../motor/index.ts";

export const DIGIMON_BOT: Record<string, string> = { aleatorio: "Kuramon", agressivo: "Monochromon", tartaruga: "Golemon", atirador: "Tankmon", contragolpe: "Leomon", adaptativo: "Devimon", oraculo: "Jijimon" };

export function nomeRivalTela(k: string): string {
  if (NPC[k]) return NPC[k].nome;
  if (BOTS_V21[k as FormaAdultaNormal]) return nomeForma(formaRival(k as FormaAdultaNormal));
  if (k === RIVAL_LIGA) return "a Liga dos Líderes";
  if (k === RIVAL_SALAO) return "o Salão";
  if (ehInstalacao(k)) return instalacaoDe(k).nome;
  return DIGIMON_BOT[k] || NOME_BOT[k] || k;
}
