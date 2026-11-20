/* Nome na tela de cada rival pela chave do registro (a luta "l" guarda so a chave): NPC da campanha e lider pelo nome dele,
   bot adulto pelo Digimon da forma, bot classico pelo Digimon dele, Liga e instalacoes da Fronteira pelo nome. Usado pela
   voz propria (os fatos da historia falam do rival pelo nome) e pela tela da luta. */
import { FORMAS_AD, NOME_BOT, NPC, RIVAL_LIGA, RIVAL_SALAO, ehInstalacao, formaDaChave, formaRival, instalacaoDe, naTabela, nomeForma, type FormaAdultaNormal } from "../motor/index.ts";

export const DIGIMON_BOT: Record<string, string> = { aleatorio: "Kuramon", agressivo: "Monochromon", tartaruga: "Golemon", atirador: "Tankmon", contragolpe: "Leomon", adaptativo: "Devimon", oraculo: "Jijimon" };

export function nomeRivalTela(k: string): string {
  if (NPC[k]) return NPC[k].nome;
  if ((FORMAS_AD as readonly string[]).includes(k)) return nomeForma(formaRival(k as FormaAdultaNormal));
  /* o rival da Arena da luta da POC: uma forma da tabela (LP2-4) */
  if (naTabela(k)) return nomeForma(formaDaChave(k));
  if (k === RIVAL_LIGA) return "a Liga dos Líderes";
  if (k === RIVAL_SALAO) return "o Salão";
  if (ehInstalacao(k)) return instalacaoDe(k).nome;
  return DIGIMON_BOT[k] || NOME_BOT[k] || k;
}
