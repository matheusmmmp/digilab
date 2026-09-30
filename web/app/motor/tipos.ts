/* Tipos do motor: acoes, formas, estagios, especies e eventos do registro. Os ids sao os do save e do
   log (sem acentos); os nomes de tela (Digimon, brasoes, niveis) ficam em catalogo.ts. */

export type AcaoPet = "ocioso" | "dormir" | "comer" | "brincar" | "chamar_atencao" | "explorar" | "emburrar";
export type AcaoDono = "alimentar" | "limpar" | "brincar" | "acariciar" | "elogiar" | "repreender"
  | "petisco" | "levar_ao_banheiro" | "tratar_lesao";          /* as 3 ultimas: so pets v4 (educacao-v1) */
export type TracoCombate = "golpe" | "bloqueio" | "agarrao" | "finta" | "carga";
export type EixoTemperamento = "curiosidade" | "teimosia" | "sensibilidade" | "rancor";
export type Temperamento = Readonly<Record<EixoTemperamento, number>>;

export type Especie = "brasa" | "cirro" | "ferrugem" | "limo";
export type Estagio = "bebe" | "crianca" | "adolescente" | "adulto" | "mega";
/** estagios de antes da evolucao canonica: as tabelas de constantes conferidas contra o HTML e o Python sao por eles; o
    Mega (pets v5, so no jogo) tem as suas em CMG */
export type EstagioBase = Exclude<Estagio, "mega">;
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
/** pets v7: fala espontanea disparada por um gatilho (reencontro, marco...). So o gatilho vai para o registro; se ela
    e mentira sai da rng da mentira (o replay sorteia de novo, igual) */
export type EventoFala = [tick: number, tipo: "fl", gatilho: string];
/** pets v6: o Tamer tem n medalhas a partir deste tick (o motor do pet nunca le o Tamer por fora; o replay le este evento) */
export type EventoLiberacao = [tick: number, tipo: "u", liberacao: { n: number }];
/** pets v6 (itens, medalhas parte 3): o dono equipa ou desequipa um chip do Tamer (motor/itens.ts). O motor confere vagas, tipo e
    estagio; o inventario e do Tamer e o app confere antes de gravar */
export type OpItem = "equipar" | "desequipar";
export type EventoItem = [tick: number, tipo: "i", item: { op: OpItem; id: string }];
/** pets v6: a carta do Tamer vale para a luta seguinte; o proximo evento do registro tem de ser a luta ("l") */
export type EventoCarta = [tick: number, tipo: "k", carta: { id: string }];
/** pets v6 (Fronteira, medalhas parte 4b): o Tamer venceu a Liga dos Lideres, e as instalacoes da Fronteira abrem para este pet a partir
    deste tick (como o "u" das medalhas: o motor do pet nunca le o Tamer por fora; o replay le este evento). Um por pet */
export type EventoFronteira = [tick: number, tipo: "f", fronteira: { campeao: true }];
export type EventoRegistro = EventoTempo | EventoDono | EventoLuta | EventoGambit | EventoTreino | EventoOrigem | EventoConfig | EventoLiberacao
  | EventoItem | EventoCarta | EventoFronteira | EventoFala;

export type VersaoPet = 1 | 2 | 3 | 4 | 5 | 6 | 7;

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
