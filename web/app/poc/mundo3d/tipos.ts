/* O contrato sensório-motor do WORLD-POC-01a (docs/futuro/mundo_3d.md, seção 4): o que o cérebro recebe (a Observação) e o que ele
   devolve (a Intenção). É o único arquivo que o cérebro importa (a G-CONTRATO confere). Nada aqui é posição absoluta: toda distância e
   direção é relativa ao pet e já passou pelo sensor. Os nomes dos campos são os do documento, em snake_case como os registros do motor. */

/** as categorias do que o pet percebe */
export type Categoria = "comida" | "bola" | "parede" | "obstaculo";

/** um objeto visto: `ref` é um rótulo desta Observação (válido enquanto o objeto é visto), não o id do motor; `setor` é relativo à
 *  orientação do pet (0 = em frente, 4 = à esquerda... em 16 setores) */
export interface Visto { ref: number; categoria: Categoria; distancia: number; setor: number }

/** o que encostou no círculo do pet desde a última decisão */
export interface Contato { categoria: Categoria; setor: number }

/** por que o controlador parou de executar a Intenção anterior */
export type ParouPor = "chegou" | "bloqueado" | "sumiu" | "hora" | "descansou";

/** o que o pet percebeu da ação anterior (o resultado filtrado; a verdade inteira fica no registro do motor) */
export interface ResultadoPercebido {
  parou_por: ParouPor;
  comeu: boolean;
  empurrou: boolean;
  /** quanto a distância percebida até a bola mudou na ação (positivo = a bola se afastou); null se a bola não foi vista no começo e no fim */
  bola_afastou: number | null;
}

/** o corpo de brinquedo do POC-01a, na escala inteira [0, 1024] */
export interface CorpoPoc { fome: number; tedio: number }

/** a escala S dos receptores do corpo químico (a `escala_receptor` do corpo, a S do cérebro A) */
export const ESCALA_RECEPTOR = 1024;

export interface Observacao {
  vistos: Visto[];
  /** a distância livre em cada um dos 8 setores (0 = em frente, de dois em dois setores de 16), até o raio do bigode */
  obstaculos: number[];
  contato: Contato[];
  resultado: ResultadoPercebido | null;
  /** o corpo que o pet sente: com a chave do corpo desligada (o POC-01a), o de brinquedo (`CorpoPoc`); ligada (o POC-02), os receptores
   *  do corpo químico, `Corpo.receptores()`, inteiros em [0, S]. Nunca a química */
  corpo: Readonly<Record<string, number>>;
}

export type TipoIntencao = "aproximar" | "investigar" | "tocar" | "empurrar" | "consumir" | "descansar" | "afastar";

/** a Intenção: o tipo e o alvo, por `ref` de um objeto visto ou por um setor relativo (de 16) */
export interface Intencao { tipo: TipoIntencao; ref?: number; setor?: number }

/** a rng que o cérebro recebe (a rng da política, separada da do ambiente) */
export interface RngPolitica { inteiro(n: number): number }

/** um cérebro: lê só a Observação e devolve só a Intenção */
export interface Cerebro { decidir(obs: Observacao, rng: RngPolitica): Intencao }
