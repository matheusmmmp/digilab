/* Motivo (espelho de digilab/motivo.py). Somente leitura: nao muda decisao.
   Fator so se a contribuicao e positiva, >= limiar e o termo aprendido MUDOU a escolha (sem ele,
   log-prior + Gumbel daria outra acao). */
import { FATORES_MEMORIA } from "./constantes.ts";

export const FATOR_BASE = ["habito", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "hora", "tempo_sem_cuidado"];
export const FATOR_DA_FEATURE = [...FATOR_BASE, ...FATORES_MEMORIA];

/** as condicoes da linguagem de gambits do combate por turnos (combate.ts, que saiu na LUTA_POC, LP4): a fala ainda tem um texto para
    cada uma (expressao.FATORES_TXT, a fala da luta dos pets v2-v12), e a tabela confere que nenhuma fica sem texto */
export const CONDICOES_FALA: readonly string[] = [
  "sempre", "distancia_eh", "hp_proprio_abaixo", "guts_proprio_abaixo", "guts_proprio_acima", "oponente_preparando", "oponente_hp_abaixo",
  "oponente_guts_abaixo", "oponente_repete", "oponente_frequente", "turno_execucao", "oponente_vai_preparar", "executando_pesado",
];
