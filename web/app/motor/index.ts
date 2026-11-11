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
export * from "./motivo.ts";
export * from "./expressao.ts";
export * from "./motor.ts";
export * from "./donos.ts";
export * from "./mundo.ts";
export * from "./grupo.ts";
export * from "./contrato.ts";
export * from "./corpo.ts";
export * from "./lobos.ts";
export * from "./motor_corpo.ts";
export * from "./motor_corpo_mundo.ts";
export * from "./digibrain.ts";
export * from "./pet_lab.ts";
export { decodificar, decodificarV2, episodioDec, desfechoDoEpisodio, CATALOGO_CONCEITOS, CLASSES_EPISODIO_DEC, DESFECHOS, VERSAO_DECODIFICADOR, VERSAO_DECODIFICADOR_V2, type Conceito, type ConceitosDec, type EpisodioDec, type NomeConceito } from "./digibrain/decodificador.ts";
export { CONTEUDOS_FALA, type ConteudoFala } from "./digibrain/constantes.ts";
export { ORDEM_TERMOS, resultadoAnterior, type BarraLab, type ChanceLab, type LeituraLab, type ResultadoLab, type SondaLab, type TermoLab } from "./digibrain/leitura.ts";
/* a luta da POC (LUTA_POC, LP2): o mapeamento dos stats e os rivais; do nucleo, so a chave, os mapas e a tabela (os outros nomes dele, como
   Stats e ResultadoLuta, sao de motor/arena/ e colidiriam com os do motor) */
export * from "./luta_poc.ts";
export { APOIO_LP6, ARENA_POR_ESTAGIO_LP6, CENAS, ERRO_MIRA_POC, FORMAS_ARENA, GOLPES_DA_POC, IDS_CENA, LUTA_POC_LIGADA, TIRO_V21 as TIRO_POC_V21, type Esquiva as EsquivaPoc, type IdCena, type Tiro as TiroPoc } from "./arena/index.ts";
/* a tela da luta da POC (LUTA_POC, LP3): o palco refaz a luta passo a passo com a mesma entrada e so le o estado; com nomes proprios, para
   nao colidir com os do motor */
export {
  ACAO as ACAO_POC, ELIPSE as ELIPSE_POC, EQ as EQ_POC, LIMITE_MS as LIMITE_POC_MS, MUNDO as MUNDO_POC, PASSO_MS as PASSO_POC_MS,
  configLuta as configLutaPoc, criarLuta as criarLutaPoc, lutar as lutarNucleoPoc, passo as passoPoc, sorteiosPorFluxo as sorteiosPoc,
  type DadosForma as DadosFormaPoc, type EntradaLuta as EntradaLutaPoc, type Evento as EventoPoc, type Luta as LutaPoc,
  type Lutador as LutadorPoc, type ProjetilVoo as ProjetilPoc, type Stats as StatsPoc,
} from "./arena/index.ts";
/* MITOLOGIA, E0: as lendas como funcao pura do pet refeito do log (docs/TAREFA_V3_MITOLOGIA.md) */
export {
  CMIT, LENDA_CONTADA, LENDA_DO_MACACO, NOME_ORACULO, detalheNoTick, falaDoOraculo, hybrisDe, lendas, variadaDe,
  type AtividadeLenda, type EventoLenda, type FontesLenda,
} from "./lendas.ts";
/* MITOLOGIA, E1: os sinais dos cinco deuses, o Myotismon, a pedra, as pegadas, o dia raro e o enigma */
export {
  CMIT_E1, DEUSES, ENIGMA, FALA_DIA_RARO, FALA_PEDRA, FALA_PEGADAS, FALA_PESSEGO, NOME_DEUS, SINAL_DEUS, diaDeVida, myotismonNoTick,
  myotismonJaApareceu, pedraAchadaDe, pedraEm, pegadasDe, sinaisDe, sinaisNoTick, tickDoDiaRaro, type Deus, type FontesE1, type SinalDeus,
} from "./lendas_e1.ts";
