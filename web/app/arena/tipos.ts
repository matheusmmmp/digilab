/* Tipos da arena em tempo real (docs/TAREFA_V2_UP_ARENA.md, secao 10.4). Os dados do jogo vem de Assets/arena_up/dados (fora do git). */
import type { Dificuldade, StatsGenericos } from "./constantes.ts";

export type Lado = "a" | "b";
export type IdCena = "campo" | "coliseu" | "floresta" | "praia" | "deserto" | "castelo" | "caverna" | "ringue";

// ---------- dados do jogo (status.json, golpes.json, atributos.json, atlas.json) ----------
export interface StatusJogo {
  tipo: string;
  estagio?: string;
  chave?: number;
  estimado?: boolean;
  base: { HP: number; Attack: number; Defense: number; CriticalRate: number; EvadeRate: number; StunRate: number; MoveSpeed?: number };
  nivel: { HP: number; Attack: number; Defense: number };
}
export interface Projetil { prefab: string | null; vel: number; tipo?: string }
export interface Impacto { prefab: string; atraso: number }
/** o golpe de um Digimon (do script de batalha do jogo): animacao, instante do golpe (s), projetil e impactos */
export interface GolpeBase { anim: string; t: number; proj: Projetil | null; hits: Impacto[] }
export interface Golpe extends GolpeBase { skill: GolpeBase | null }
/** [x, y, ms] de cada quadro na prancha; [nome, primeiro, ultimo] de cada tag */
export interface AtlasDigimon { w: number; h: number; sw: number; sh: number; f: [number, number, number][]; t: [string, number, number][]; th: [number, number] }
export interface AtlasArena { tam: number; w: number; h: number; d: Record<string, AtlasDigimon> }
export type Atributo = "Vaccine" | "Virus" | "Data" | "Free" | "None" | "Unknown";

export interface DadosArena {
  status: Record<string, StatusJogo>;
  golpes: Record<string, Golpe>;
  atributos: Record<string, Atributo>;
  atlas: AtlasArena;
}

// ---------- configuracao de uma luta ----------
export type FonteStats = "jogo" | "generico";
export interface ConfigLado { equipe: [string, string, string]; fonte: FonteStats; nivel: number; generico: StatsGenericos }
export interface ConfigLuta {
  cena: IdCena;
  dific: Dificuldade;
  forca: number;      // vantagem de atributo
  ritmo: number;      // vida do jogo dividida por isto
  pvel: number;       // velocidade dos projeteis em relacao ao jogo
  jogador: boolean;   // a equipe azul ("a") e do jogador
  a: ConfigLado;
  b: ConfigLado;
}

// ---------- estado ----------
export interface Stats { hp: number; atk: number; def: number; vel: number; cad: number; crit: number; hcd: number; hpot: number; esquiva: number; atordoa: number; origem: "jogo" | "genérico" }
export type EstadoLutador = "idle" | "run" | "attack" | "stun" | "die";
export interface Lutador {
  n: string; lado: Lado; slot: number;
  A: AtlasDigimon; g: GolpeBase; sk: GolpeBase; propria: boolean; usandoHab: boolean;
  st: Stats; atr: Atributo;
  x: number; y: number; hp: number; viraEsq: boolean;
  estado: EstadoLutador; t: number;
  recarga: number; recSk: number; golpeDado: boolean;
  msAtk: number; msSk: number; alcance: number; raio: number;
  alvo: Lutador | null; fase: number;
  morto: boolean; dano: number; golpes: number;
  mira: [number, number] | null;
  dash: number; dashCd: number; dashDir: [number, number]; reacao: number; desvioDir: [number, number];
  entrada: number; atordoado: number; caiuEm: number; foraAte: number;
  escondido: boolean; naRuna: number; buffAte: number; bloq: number; ladoDesvio: number;
  acDano: number; ultAmb: number; ultNum: number; decisao: string;
}
export interface Obstaculo { x: number; y: number; r: number; img: string; hp: number | undefined; max: number | undefined }
export interface Zona { tipo: string; x: number; y: number; rx: number; ry: number }
export interface Erupcao { x: number; y: number; t: number; explodiu: boolean }
export interface EstadoCena {
  id: IdCena; obst: Obstaculo[]; zonas: Zona[]; seguro: number;
  avisou: boolean; linha: number; tempestade: boolean; runaCd: number; prox: number | undefined; erupcoes: Erupcao[];
}
export interface ProjetilVoo {
  de: Lutador; dados: GolpeBase; hab: boolean; x: number; y: number; altura: number; vx: number; vy: number; resta: number;
  t: number; esq: boolean; fim: boolean; decidido: Set<Lutador>;
}

// ---------- entrada do jogador e saida da simulacao ----------
export type Entrada =
  | { tipo: "mover"; mx: -1 | 0 | 1; my: -1 | 0 | 1 }
  | { tipo: "mira"; x: number; y: number } | { tipo: "sem_mira" }
  | { tipo: "atacar" } | { tipo: "habilidade" }
  | { tipo: "investida"; ligada: boolean }
  | { tipo: "trocar"; slot: number };

export interface Ref { lado: Lado; slot: number; n: string }
export type Evento =
  | { tipo: "inicio"; a: string[]; b: string[] }
  | { tipo: "dano"; at: Ref; alvo: Ref; valor: number; perda: number; crit: boolean; mult: number; hab: boolean; resta: number; x: number; y: number; dx: number; hits: Impacto[]; espelho: boolean }
  | { tipo: "esquiva"; at: Ref; alvo: Ref; x: number; y: number }
  | { tipo: "atordoado"; at: Ref; alvo: Ref }
  | { tipo: "queda"; u: Ref; motivo: string | null }
  | { tipo: "troca"; lado: Lado; sai: Ref; entra: Ref; forcada: boolean; x: number; y: number }
  | { tipo: "habilidade"; u: Ref; propria: boolean; anim: string; x: number; y: number }
  | { tipo: "golpe_ar"; u: Ref }
  | { tipo: "tiro_bloqueado"; u: Ref; obst: string }
  | { tipo: "pilar"; u: Ref; quebrou: boolean }
  | { tipo: "tiro_errou"; u: Ref }
  | { tipo: "runa"; u: Ref; x: number; y: number }
  | { tipo: "arena_fecha" }
  | { tipo: "tempestade" }
  | { tipo: "queda_ringue"; u: Ref }
  | { tipo: "ambiente"; u: Ref; perda: number; motivo: string; mostrar: { valor: number; x: number; y: number } | null }
  | { tipo: "fim"; vencedor: Lado | null; vivos: number; relogio: number };

/** os sorteios da simulacao, um por uso (secao 10.4): ia, combate, cena e o visual (posicao do numero de dano, que a simulacao so repassa) */
export interface Sorteios { ia(): number; combate(): number; cena(): number; visual(): number }

export interface Luta {
  cfg: ConfigLuta; dados: DadosArena; r: Sorteios;
  cena: EstadoCena; eq: Record<Lado, Lutador[]>; ativo: Record<Lado, number>; trocaCd: Record<Lado, number>;
  projeteis: ProjetilVoo[]; relogio: number; fim: boolean; vencedor: Lado | null;
  /** entrada do jogador (so com cfg.jogador) */
  querAtacar: boolean; querHab: boolean; mover: [number, number]; mouse: [number, number] | null; investida: boolean;
  /** eventos do passo em andamento (passo() devolve e limpa) */
  eventos: Evento[];
}
