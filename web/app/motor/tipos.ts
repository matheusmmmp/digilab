/* Tipos do motor: acoes, formas, estagios, especies e eventos do registro. Os ids sao os do save e do
   log (sem acentos); os nomes de tela (Digimon, brasoes, niveis) ficam em catalogo.ts. */

export type AcaoPet = "ocioso" | "dormir" | "comer" | "brincar" | "chamar_atencao" | "explorar" | "emburrar";
export type AcaoDono = "alimentar" | "limpar" | "brincar" | "acariciar" | "elogiar" | "repreender"
  | "petisco" | "levar_ao_banheiro" | "tratar_lesao";          /* as 3 ultimas: so pets v4 (educacao-v1) */
export type TracoCombate = "golpe" | "bloqueio" | "agarrao" | "finta" | "carga";
export type EixoTemperamento = "curiosidade" | "teimosia" | "sensibilidade" | "rancor";
export type Temperamento = Readonly<Record<EixoTemperamento, number>>;

export type Especie = "brasa" | "cirro" | "ferrugem" | "limo";
export type Estagio = "bebe" | "crianca" | "adolescente" | "adulto";
export type EstagioTreino = "crianca" | "adolescente" | "adulto";
export type Ramo = "sereno" | "arisco";
export type Linha = "brigao" | "guardiao" | "cacador" | "colosso";
export type FormaAdultaNormal = "duelista" | "furioso" | "espelho" | "muralha" | "sentinela" | "emboscador" | "vigia" | "tita";
export type FormaSombria = "devastador" | "bastiao_rachado" | "predador" | "colosso_partido";
export type FormaAdulta = FormaAdultaNormal | FormaSombria;
export type EixoCarater = "impetuoso" | "paciente" | "atento" | "resistente";
export type Carater = Record<EixoCarater, number>;
export type Stat = "vigor" | "folego" | "recuperacao" | "forca" | "mira" | "guarda";
export type Stats = Record<Stat, number>;

/** forma do pet: trava em cada evolucao (ramo na crianca, linha no adolescente, forma no adulto) */
export interface Forma {
  esp: Especie;
  est: Estagio;
  ramo?: Ramo;
  linha?: Linha;
  adulta?: FormaAdulta;
  /** pets v5: o Ultimate que virou Mega (mesma forma, estagio adulto; so aparece depois da evolucao) */
  mega?: true;
}
/** forma ou ovo (so para rotulos de tela) */
export interface FormaOuOvo extends Omit<Forma, "est"> { est: Estagio | "ovo" }

export type Exercicio = "levantar_pedra" | "corrida" | "alvo" | "esquiva" | "meditar" | "resistencia";
export type OpGambit = "travar" | "destravar" | "vetar" | "liberar";
export type Chamado = "fome" | "higiene" | "carinho";

/** evento do registro: [tick, tipo, valor]. So isto e salvo; o estado vem do replay. */
export type EventoTempo = [tick: number, tipo: "t", n: number];
export type EventoDono = [tick: number, tipo: "d", acao: AcaoDono];
export type EventoLuta = [tick: number, tipo: "l", luta: { r: string; s: number }];
export type EventoGambit = [tick: number, tipo: "g", gambit: { op: OpGambit; k: string }];
export type EventoTreino = [tick: number, tipo: "tr", exercicio: Exercicio];
/** heranca (pets v4): um genitor visto no cruzamento. h = impressao do registro dele (hashSemente do JSON) */
export interface PaiOrigem { h: number; esp: Especie; temp: Temperamento; est: Estagio; ger?: number }   /* ger: geracao do pai (so tela) */
export interface Origem { pais: [PaiOrigem, PaiOrigem]; s: number; quem: string }
/** so como PRIMEIRO evento do registro de um filho */
export type EventoOrigem = [tick: number, tipo: "o", origem: Origem];
/** ritmo dos estagios (pets v4): rapida = 3/12/18 h (o de sempre); classica = 6/24/36 h (v-pets) */
export type Ritmo = "rapida" | "classica";
/** so no comeco do registro (antes de qualquer outro evento, menos outra config) */
export type EventoConfig = [tick: number, tipo: "c", config: { dur: Ritmo }];
export type EventoRegistro = EventoTempo | EventoDono | EventoLuta | EventoGambit | EventoTreino | EventoOrigem | EventoConfig;

export type VersaoPet = 1 | 2 | 3 | 4 | 5;

/** estado de vida (camada 1) */
export interface EstadoVida {
  tick: number; fome: number; higiene: number; energia: number; humor: number; saude: number;
  sujeira: number; dormindo: boolean; ultimoCuidado: number; totalCuidados: number;
}
/** observacao da politica: vetor de 8 posicoes + tempo desde o ultimo cuidado */
export interface Observacao { v: number[]; tdc: number }

/** desejo do pet (espelho de desejo.py) */
export interface Desejo {
  tick: number; tipo: "necessidade" | "vontade"; alvo: string; causa?: string; intensidade: number;
}

/** motivo de uma decisao (somente leitura; espelho de motivo.py) */
export interface MotivoVida {
  origem: "vida"; tick: number; acao: string; fatores: string[]; refsOrd: number[]; intensidade: number;
  exploracao: boolean; humor: number; valorDecidiu: boolean; recusa?: { acaoDono: string; p: number };
}
export interface MotivoCombate {
  origem: "combate"; turno: number; acao: string; fatores: string[]; refs: number[]; exploracao: boolean; regra: number | string;
}
export type Motivo = MotivoVida | MotivoCombate;

/** item do historico (somente leitura, ultimos 300) */
export interface ItemHistorico { t: number; quem: string; a: string }
