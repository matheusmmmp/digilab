/* As marcas da fala do Rookie na tela (so exibicao; o texto vem das tabelas de expressao do motor e nao muda). A fala do Rookie
   e "[acao] [:causa:]": a tela troca a causa pelo icone do fator (ou por uma etiqueta, sem o atlas ou sem icone) e a acao por uma
   etiqueta, e nunca mostra as marcas cruas. Aqui ficam tambem o icone de cada fator e o rotulo da acao do motivo no painel
   "Por que ele disse isso" (as acoes do treino nao sao acoes do pet, NOME_PET nao as tem). */
import { FATORES_TXT, NOME_PET, type AcaoPet, type Motor } from "../motor/index.ts";

export type ParteFala = { tipo: "texto"; txt: string } | { tipo: "acao"; txt: string } | { tipo: "causa"; txt: string; fator: string | null };

/** quebra a fala do Rookie em texto, acao ("[x]") e causa ("[:x:]"); a causa traz o fator dono do marcador, quando ha um */
export function partesFala(txt: string): ParteFala[] {
  const partes: ParteFala[] = [];
  let ult = 0;
  for (const m of txt.matchAll(/\[:(.+?):\]|\[([^\]]+)\]/g)) {
    if (m.index! > ult) partes.push({ tipo: "texto", txt: txt.slice(ult, m.index) });
    if (m[1] !== undefined) {
      const marc = m[1];
      partes.push({ tipo: "causa", txt: marc, fator: Object.keys(FATORES_TXT).find(k => FATORES_TXT[k].marcador === marc) ?? null });
    } else partes.push({ tipo: "acao", txt: m[2] });
    ult = m.index! + m[0].length;
  }
  if (ult < txt.length) partes.push({ tipo: "texto", txt: txt.slice(ult) });
  return partes;
}

/** o icone de cada fator, no balao e no painel do porque: uma peca do atlas, ou "tempo" (a ampulheta da demora) */
export const ICONE_FATOR: Record<string, string> = {
  fome: "emoji_carne", necessidade_fome: "emoji_carne", elogio: "emoji_joinha", elogios: "emoji_joinha", carinho: "emoji_coracao",
  bronca: "emoji_exclam", repreensoes: "emoji_exclam", fadiga_treino: "treino_saco",
  demora: "tempo", latencia_fome: "tempo", latencia_higiene: "tempo", tempo_sem_cuidado: "tempo",
};

/** o que o pet fez, no motivo que nao e uma acao do pet (o treino: o dono treinou mesmo com o pedido de pausa, ou forcou) */
export const ACAO_MOTIVO: Record<string, string> = {
  treinar_cansado: "treinou sem a pausa que pediu", forcar_treino: "treinou além do limite", enrolar: "enrolou no treino",
};
/** o rotulo do painel "Por que ele disse isso": a acao do motivo do treino, senao o que o pet faz agora */
export function rotuloAcaoFala(m: Motor): string {
  const mot = m.motivo;
  if (mot && mot.origem === "vida" && !(mot.acao in NOME_PET)) {
    const r = ACAO_MOTIVO[mot.acao];
    if (!r) throw new Error("acao de motivo sem rotulo na tela: " + mot.acao);
    return r;
  }
  return NOME_PET[m.acao as AcaoPet];
}
