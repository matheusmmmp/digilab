/* Tipos da luta da POC no motor (docs/TAREFA_V3_LUTA_POC.md, LP1): porte de web/app/arena/tipos.ts do commit efb2ded, so 1 contra 1,
   sem jogador e sem equipes. Os dados do Digimon vem da tabela do git (formas.ts, a LP-2); os numeros do lutador vem prontos (Stats, a
   LP-3: na LP2 saem dos 6 stats do pet). */
import type { Apoio, ArenaPorEstagio, Dificuldade, Esquiva, Tiro } from "./constantes.ts";

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
  /** o golpe de apoio, do tipo que falta ao golpe, e a duracao (ms) do clipe dele (LP6-1; so com o `apoio` da luta). A tabela do git tem
      os dois em toda forma; uma forma sem eles com a chave ligada falha alto */
  apoio?: GolpeBase; msApoio?: number;
}

// ---------- configuracao de uma luta ----------
/** os numeros do lutador (os Stats da POC): vida, ataque, defesa, movimento (px/s), ciclo do ataque (ms), critico (%), recarga da
    habilidade (s), forca da habilidade (x), esquiva (%), atordoamento (%) e o erro de mira (px; era da dificuldade na POC, e do lutador
    desde a LP2, decisao 2) */
export interface Stats { hp: number; atk: number; def: number; vel: number; cad: number; crit: number; hcd: number; hpot: number; esquiva: number; atordoa: number; erro: number;
  /** a perspicacia e a agilidade da esquiva (D-LP5-14; so com a `esquiva` da entrada; sem elas, 1) */
  perc?: number; agil?: number }
/** um lado: o Digimon, os numeros e, numa serie sem cura (a Cidadela, LP2), a vida com que ele entra (sem ela, a vida cheia) */
export interface LadoLuta { forma: DadosForma; stats: Stats; vida0?: number }
export interface ConfigLuta {
  cena: IdCena;
  dific: Dificuldade;
  forca: number;      // vantagem de atributo
  pvel: number;       // velocidade dos projeteis em relacao ao jogo
  a: LadoLuta;        // o lado azul (o pet, na LP2)
  b: LadoLuta;
  /** a distancia do tiro (D-LP5-12); sem ela, a luta da POC */
  tiro?: Tiro;
  /** a esquiva pela perspicacia e pela velocidade (D-LP5-14); sem ela, a luta da POC */
  esquiva?: Esquiva;
  /** o golpe de apoio (LP6-1); sem ele, a luta sem apoio */
  apoio?: Apoio;
  /** a elipse pelo estagio dos dois (LP6-1, secao 4a do plano); sem ela, a elipse de sempre */
  arenaPorEstagio?: ArenaPorEstagio;
  /** a N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4): o projetil de quem ja caiu some no ar; sem ela, ele ainda acerta */
  tiroDoMorto?: true;
  /** a N3: o teto (px) do pulo da esquiva; sem ele, o pulo sem teto */
  puloMax?: number;
  /** a N3: no Ringue, o limite (fracao do raio) do recuo e do pulo; sem ele, eles nao olham a borda */
  bordaRingue?: number;
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
  /** ms abaixo da distancia minima do tiro (D-LP5-12; so com o `tiro` da entrada) */
  esperaTiro: number;
  /** a esquiva (D-LP5-14): os ataques comecados, o ultimo ataque do alvo ja lido e o contra-ataque pendente */
  nAtaque: number; leuAtaque: number; contraPend: boolean;
  /** o golpe de apoio (LP6-1; null sem o `apoio` da entrada): os dados, o clipe (ms), a recarga (ms), se o ataque em curso e o apoio e ha
      quanto tempo (ms) o alvo esta alem do alcance de perto (o tiro fraco de quem bate de perto) */
  ap: GolpeBase | null; msAp: number; recAp: number; usandoApoio: boolean; longeMs: number;
  /** o recuo depois do apoio de perto de quem atira (LP6-3, D-LP6-3-4): quanto tempo (ms) ainda resta dele; 0 = sem recuo */
  recuoAp: number;
  acDano: number; ultAmb: number; ultNum: number;
  /** a ultima situacao em que a IA da POC pensou em trocar (o sorteio dela fica; ver sim.ts, sorteioDaTroca) */
  decisao: string;
}
export interface Obstaculo { x: number; y: number; r: number; img: string; hp: number | undefined; max: number | undefined }
export interface Zona { tipo: string; x: number; y: number; rx: number; ry: number }
/** a elipse da arena de uma luta (a ELIPSE de constantes.ts, ou ela escalada pelo estagio, LP6-1) */
export interface Elipse { cx: number; cy: number; rx: number; ry: number }
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
  | { tipo: "dano"; at: Ref; alvo: Ref; valor: number; perda: number; crit: boolean; mult: number; hab: boolean; resta: number; x: number; y: number; dx: number; hits: Impacto[]; espelho: boolean;
      /** o golpe de apoio (LP6-1): so aparece quando e ele */
      apoio?: true }
  | { tipo: "esquiva"; at: Ref; alvo: Ref; x: number; y: number }
  | { tipo: "atordoado"; at: Ref; alvo: Ref }
  | { tipo: "queda"; u: Ref; motivo: string | null }
  | { tipo: "habilidade"; u: Ref; propria: boolean; anim: string; x: number; y: number }
  /** o golpe de apoio comeca (LP6-1): `perto`, o golpe de perto de quem atira; senao, o tiro fraco de quem bate de perto */
  | { tipo: "apoio"; u: Ref; perto: boolean; anim: string; x: number; y: number }
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
  /** a elipse desta luta e o fator dela sobre a ELIPSE (1 sem a `arenaPorEstagio`; LP6-1) */
  el: Elipse; esc: number;
  projeteis: ProjetilVoo[]; relogio: number; fim: boolean; vencedor: Lado | null;
  /** eventos do passo em andamento (passo() devolve e limpa) */
  eventos: Evento[];
}
