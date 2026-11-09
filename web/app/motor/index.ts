/* Motor do jogo web em TypeScript (TAREFA_FRONT_TS, Etapa 2). Sem DOM: a interface importa daqui, o motor
   nunca importa da interface. A fala (expressao.ts) so monta texto a partir do motivo; nunca decide nada. */
export * from "./tipos.ts";
export * from "./rng.ts";
export * from "./constantes.ts";
export * from "./estado.ts";
export * from "./memoria.ts";
export * from "./bandit.ts";
export * from "./vinculo.ts";
export * from "./treino.ts";
export * from "./nomes.ts";
export * from "./catalogo.ts";
export * from "./combate.ts";
export * from "./bots.ts";
export * from "./medalhas.ts";
export * from "./arenas.ts";
export * from "./itens.ts";
export * from "./liga.ts";
export * from "./instalacoes.ts";
export * from "./fabrica.ts";
export * from "./salao.ts";
export * from "./carater.ts";
export * from "./confianca.ts";
export * from "./gambits_pet.ts";
export * from "./motivo.ts";
export * from "./expressao.ts";
export * from "./motor.ts";
export * from "./donos.ts";
export * from "./mundo.ts";
export * from "./contrato.ts";
export * from "./corpo.ts";
export * from "./lobos.ts";
export * from "./motor_corpo.ts";
export * from "./motor_corpo_mundo.ts";
export * from "./digibrain.ts";
export * from "./combate_tr/index.ts";
export * from "./pet_lab.ts";
export { decodificar, decodificarV2, episodioDec, desfechoDoEpisodio, CATALOGO_CONCEITOS, CLASSES_EPISODIO_DEC, DESFECHOS, VERSAO_DECODIFICADOR, VERSAO_DECODIFICADOR_V2, type Conceito, type ConceitosDec, type EpisodioDec, type NomeConceito } from "./digibrain/decodificador.ts";
export { CONTEUDOS_FALA, type ConteudoFala } from "./digibrain/constantes.ts";
export { ORDEM_TERMOS, type BarraLab, type ChanceLab, type LeituraLab, type SondaLab, type TermoLab } from "./digibrain/leitura.ts";
/* a luta da POC (LUTA_POC, LP2): o mapeamento dos stats e os rivais; do nucleo, so a chave, os mapas e a tabela (os outros nomes dele, como
   Stats e ResultadoLuta, sao de motor/arena/ e colidiriam com os do motor) */
export * from "./luta_poc.ts";
export { CENAS, ERRO_MIRA_POC, FORMAS_ARENA, IDS_CENA, LUTA_POC_LIGADA, type IdCena } from "./arena/index.ts";
