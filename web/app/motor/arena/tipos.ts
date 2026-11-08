/* Tipos da luta da POC no motor (docs/TAREFA_V3_LUTA_POC.md, LP1): porte de web/app/arena/tipos.ts do commit efb2ded, so 1 contra 1,
   sem jogador e sem equipes. Os dados do Digimon vem da tabela do git (formas.ts, a LP-2); os numeros do lutador vem prontos (Stats, a
   LP-3: na LP2 saem dos 6 stats do pet). */
import type { Dificuldade } from "./constantes.ts";

export type Lado = "a" | "b";
export type IdCena = "campo" | "coliseu" | "floresta" | "praia" | "deserto" | "castelo" | "caverna" | "ringue";
export type Atributo = "Vaccine" | "Virus" | "Data" | "Free" | "None" | "Unknown";

// ---------- os dados do Digimon (formas.ts) ----------
export interface Projetil { prefab: string | null; vel: number; tipo: string | null }
export interface Impacto { prefab: string; atraso: number }
/** um golpe: a animacao, o instante do golpe (s), o projetil, os impactos e o fator de ritmo ja calculado (fatorRitmo da POC) */
export interface GolpeBase { anim: string; t: number; proj: Projetil | null; hits: Impacto[]; fr: number }
/** o que a simulacao le do Digimon de uma forma: atributo, golpe, habilidade e a duracao (ms) dos clipes */
export interface DadosForma {
  digimon: string; nome: string; estagio: string; atributo: Atributo; generico: boolean;
  golpe: GolpeBase; habilidade: GolpeBase | null; msGolpe: number; msHabilidade: number;
}

// ---------- configuracao de uma luta ----------
/** os numeros do lutador (os Stats da POC): vida, ataque, defesa, movimento (px/s), ciclo do ataque (ms), critico (%), recarga da
    habilidade (s), forca da habilidade (x), esquiva (%) e atordoamento (%) */
export interface Stats { hp: number; atk: number; def: number; vel: number; cad: number; crit: number; hcd: number; hpot: number; esquiva: number; atordoa: number }
export interface LadoLuta { forma: DadosForma; stats: Stats }
export interface ConfigLuta {
  cena: IdCena;
  dific: Dificuldade;
  forca: number;      // vantagem de atributo
  pvel: number;       // velocidade dos projeteis em relacao ao jogo
  a: LadoLuta;        // o lado azul (o pet, na LP2)
  b: LadoLuta;
}

// ---------- estado ----------
export type EstadoLutador = "idle" | "run" | "attack" | "stun" | "die";
export interface Lutador {
  n: string; lado: Lado;
  g: GolpeBase; sk: GolpeBase; propria: boolean; usandoHab: boolean;
  st: Stats; atr: Atributo;
  x: number; y: number; hp: number; viraEsq: boolean;
  estado: EstadoLutador; t: number;
  recarga: number; recSk: number; golpeDado: boolean;
  msAtk: number; msSk: number; alcance: number; raio: number;
  alvo: Lutador | null; fase: number;
  morto: boolean; dano: number; golpes: number;
  mira: [number, number] | null;
  dash: number; dashCd: number; dashDir: [number, number]; reacao: number; desvioDir: [number, number];
  atordoado: number; caiuEm: number; foraAte: number;
  escondido: boolean; naRuna: number; buffAte: number; bloq: number; ladoDesvio: number;
  acDano: number; ultAmb: number; ultNum: number;
  /** a ultima situacao em que a IA da POC pensou em trocar (o sorteio dela fica; ver sim.ts, sorteioDaTroca) */
  decisao: string;
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

// ---------- saida da simulacao ----------
export interface Ref { lado: Lado; n: string }
export type Evento =
  | { tipo: "inicio"; a: string; b: string }
  | { tipo: "dano"; at: Ref; alvo: Ref; valor: number; perda: number; crit: boolean; mult: number; hab: boolean; resta: number; x: number; y: number; dx: number; hits: Impacto[]; espelho: boolean }
  | { tipo: "esquiva"; at: Ref; alvo: Ref; x: number; y: number }
  | { tipo: "atordoado"; at: Ref; alvo: Ref }
  | { tipo: "queda"; u: Ref; motivo: string | null }
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
  | { tipo: "fim"; vencedor: Lado | null; relogio: number };

/** os sorteios da simulacao, um por uso: ia, combate, cena e o visual (posicao do numero de dano, que a simulacao so repassa) */
export interface Sorteios { ia(): number; combate(): number; cena(): number; visual(): number }

export interface Luta {
  cfg: ConfigLuta; r: Sorteios;
  cena: EstadoCena; a: Lutador; b: Lutador;
  projeteis: ProjetilVoo[]; relogio: number; fim: boolean; vencedor: Lado | null;
  /** eventos do passo em andamento (passo() devolve e limpa) */
  eventos: Evento[];
}
