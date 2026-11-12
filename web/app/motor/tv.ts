/* A TV do mundo e o orgao da tela, o lado do mundo (GOSTO_VISUAL, P1f; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 1, 2 e 8): o espelho de
   digilab/tv.py, dos eventos `trocar_canal` e `sentido_tela` de digilab/events.py e das configs `ConfigTela` e `ConfigTV` de
   digilab/config.py. Componente puro: nao sabe de pet nem de corpo. O laco com o corpo e o mundo (motor_corpo_mundo.ts) e dono de uma `TV`
   quando as duas chaves vem ligadas (`OpcoesLacoMundo.tela`); desligadas (o padrao, todo pet de hoje), nada daqui roda.

   A fonte "grade" (a TV do jogo): a rng propria `tv-programas` (derivarSemente com a semente do mundo) sorteia os perfis e, na ordem do
   tempo, a grade (o programa, a duracao e as cenas). A fonte "evento" (o modo livre gravado): o ultimo `sentido_tela` ate o tick.
   `ResumoTela` e o resumo do GV-15 do lado de quem grava (o P0): a media de 10 amostras em 16 niveis, o evento so na mudanca.
   O gabarito e o test/gabaritos/gosto_visual.json.gz (experiments/exportar_gosto_visual.py). Todos os numeros sao PROPOSTOS, SEM FONTE. */
import { RandomPy, derivarSemente, divArred } from "./mundo.ts";

/** os sete canais da tela (4 da visao, 3 do som), na ordem do evento `sentido_tela` (config.CANAIS_TELA) */
export const CANAIS_TELA = ["cor", "brilho", "movimento", "complexidade", "volume", "variacao", "timbre"] as const;
export type CanalTela = typeof CANAIS_TELA[number];
export const N_CANAIS_TELA = 7;
export const NIVEL_MAX_TELA = 15;
export const FONTES_SENTIDO_TELA = ["tela", "tv"] as const;
export const FONTES_TV = ["grade", "evento"] as const;
export const TIPO_TROCAR_CANAL = "trocar_canal";
export const TIPO_SENTIDO_TELA = "sentido_tela";
/** o id da TV nas linhas da classe `tela` (`verTela`) e no `olhandoTela` */
export const ID_TV = 1;
/** o canal do susto e os do estresse (GV-17) e a atividade do tedio (GV-21), os de corpo.py */
export const CANAL_SUSTO_TELA: CanalTela = "volume";
export const CANAIS_ESTRESSE_TELA: readonly CanalTela[] = ["movimento", "volume"];
export const ATIVIDADE_TELA = "assistir";
export const RECEPTOR_NOVIDADE_TELA = "novidade_tela";
export const RECEPTORES_TELA = [...CANAIS_TELA.map(c => `tela_${c}`), RECEPTOR_NOVIDADE_TELA] as const;

export class TVSemChave extends Error {}

// ================================================================== as configs (config.py)
/** a ConfigTela (o orgao da tela no corpo, P1b) */
export interface ConfigTela {
  readonly ligada: boolean; readonly limiar: number; readonly meia_saturacao: number; readonly meia_vida_adaptacao: number;
  readonly k_adaptacao: number; readonly teto_intensidade: number; readonly tedio_assistir: number; readonly ganho_humor_agrado: number;
  readonly estresse_corte: number; readonly estresse_divisor: number; readonly salto_volume: number; readonly susto_salto: number;
  readonly corte_novidade: number;
}
export const CONFIG_TELA: ConfigTela = {
  ligada: false, limiar: 15000, meia_saturacao: 450000, meia_vida_adaptacao: 60, k_adaptacao: 753, teto_intensidade: 450000,
  tedio_assistir: 45000, ganho_humor_agrado: 4500, estresse_corte: 337500, estresse_divisor: 256, salto_volume: 225000, susto_salto: 90000,
  corte_novidade: 512,
};
export const CONFIG_TELA_LIGADA: ConfigTela = { ...CONFIG_TELA, ligada: true };

/** o __post_init__ da ConfigTela (com o `_conferir_orgao` do Python): falha alto */
export function conferirConfigTela(c: ConfigTela): ConfigTela {
  if (typeof c.ligada !== "boolean") throw new Error(`ConfigTela.ligada e bool: ${String(c.ligada)}`);
  for (const campo of ["limiar", "meia_saturacao", "meia_vida_adaptacao", "k_adaptacao", "teto_intensidade"] as const) {
    if (!Number.isInteger(c[campo]) || c[campo] <= 0) throw new Error(`ConfigTela.${campo} tem de ser inteiro positivo: ${c[campo]}`);
  }
  for (const campo of ["tedio_assistir", "ganho_humor_agrado", "estresse_corte", "estresse_divisor", "salto_volume", "susto_salto",
    "corte_novidade"] as const) {
    if (!Number.isInteger(c[campo]) || c[campo] <= 0) throw new Error(`ConfigTela.${campo} tem de ser inteiro positivo: ${c[campo]}`);
  }
  if (c.estresse_divisor < 2) throw new Error(`ConfigTela.estresse_divisor tem de passar de 1: ${c.estresse_divisor}`);
  for (const campo of ["estresse_corte", "salto_volume"] as const) {
    if (c[campo] >= c.teto_intensidade) throw new Error(`ConfigTela.${campo} tem de ficar abaixo do teto_intensidade (${c.teto_intensidade})`);
  }
  return c;
}

/** a ConfigTV (a TV no mundo, P1c) */
export interface ConfigTV {
  readonly ligada: boolean; readonly fonte: typeof FONTES_TV[number]; readonly celula: readonly [number, number]; readonly escala: number;
  readonly n_programas: number; readonly programa_min_ticks: number; readonly programa_max_ticks: number; readonly cena_ticks: number;
  readonly variacao: number; readonly janela_resumo_s: number;
}
export const CONFIG_TV: ConfigTV = {
  ligada: false, fonte: "grade", celula: [4, 10], escala: 450000, n_programas: 4, programa_min_ticks: 30, programa_max_ticks: 90,
  cena_ticks: 5, variacao: 27000, janela_resumo_s: 10,
};

/** a TV do jogo no cerebro (a v31; D-GV-CEREBRO-2 e 3): a fonte "evento" (o modo livre gravado: o que a captura da tela ou a TV do P0
    passa entra no registro pelo evento "st") e a celula logo ao sul da TV da ilha grande: o marco do #814 (PLANTA_ILHA_GRANDE.marcos.tv,
    busca 0) fica na celula (96, 17), que o mapa fecha (nao e seca), e a TV do motor pede uma celula seca (falha alto, como o Python).
    Nada daqui e do Python: a pesquisa usa a CONFIG_TV. PROPOSTO, SEM FONTE */
export const CONFIG_TV_JOGO: ConfigTV = { ...CONFIG_TV, ligada: true, fonte: "evento", celula: [96, 18] };
/** a celula para onde o dono leva o pet para assistir (o gesto "levar o pet", v19; o painel da TV): duas celulas ao sul da TV do motor, perto
    da almofada do cantinho e dentro do raio da visao (6 celulas). PROPOSTO, SEM FONTE */
export const CELULA_PERTO_DA_TV_JOGO: readonly [number, number] = [96, 20];

/** o __post_init__ da ConfigTV: falha alto */
export function conferirConfigTV(c: ConfigTV): ConfigTV {
  if (typeof c.ligada !== "boolean") throw new Error(`ConfigTV.ligada e bool: ${String(c.ligada)}`);
  if (!(FONTES_TV as readonly string[]).includes(c.fonte)) throw new Error(`ConfigTV.fonte em ${FONTES_TV}: ${c.fonte}`);
  if (c.celula.length !== 2 || c.celula.some(v => !Number.isInteger(v) || v < 0)) throw new Error(`ConfigTV.celula: ${JSON.stringify(c.celula)}`);
  for (const campo of ["escala", "n_programas", "programa_min_ticks", "programa_max_ticks", "cena_ticks", "janela_resumo_s"] as const) {
    if (!Number.isInteger(c[campo]) || c[campo] <= 0) throw new Error(`ConfigTV.${campo} tem de ser inteiro positivo: ${c[campo]}`);
  }
  if (c.n_programas < 2) throw new Error(`ConfigTV.n_programas >= 2: ${c.n_programas}`);
  if (c.programa_min_ticks > c.programa_max_ticks) throw new Error("ConfigTV.programa_min_ticks > programa_max_ticks");
  if (!Number.isInteger(c.variacao) || c.variacao < 0 || c.variacao >= c.escala) throw new Error(`ConfigTV.variacao em [0, escala): ${c.variacao}`);
  return c;
}

// ================================================================== os eventos (events.py)
export type NiveisTela = readonly number[];

function naturalCanonico(texto: string): number {
  if (!/^[0-9]+$/.test(texto) || (texto.length > 1 && texto[0] === "0")) throw new Error(`inteiro malformado no log: ${JSON.stringify(texto)}`);
  return Number(texto);
}

function niveisTela(niveis: readonly unknown[]): number[] {
  if (!Array.isArray(niveis) || niveis.length !== N_CANAIS_TELA) throw new Error(`sentido_tela com ${N_CANAIS_TELA} niveis: ${JSON.stringify(niveis)}`);
  for (const n of niveis) {
    if (typeof n !== "number" || !Number.isInteger(n) || n < 0 || n > NIVEL_MAX_TELA) throw new Error(`nivel do sentido_tela fora de 0 a ${NIVEL_MAX_TELA}: ${String(n)}`);
  }
  return [...niveis] as number[];
}

export function valorTrocarCanal(programa: number): string {
  if (!Number.isInteger(programa) || programa < 0) throw new Error(`trocar_canal com programa invalido: ${programa}`);
  return String(programa);
}
export function lerTrocarCanal(valor: unknown): number {
  if (typeof valor !== "string") throw new Error(`trocar_canal malformado: ${JSON.stringify(valor)}`);
  return naturalCanonico(valor);
}
export function valorSentidoTela(fonte: string, niveis: readonly number[]): string {
  if (!(FONTES_SENTIDO_TELA as readonly string[]).includes(fonte)) throw new Error(`fonte do sentido_tela em ${FONTES_SENTIDO_TELA}: ${fonte}`);
  return [fonte, ...niveisTela(niveis).map(String)].join("|");
}
export function lerSentidoTela(valor: unknown): [string, number[]] {
  if (typeof valor !== "string") throw new Error(`sentido_tela malformado: ${JSON.stringify(valor)}`);
  const partes = valor.split("|");
  if (partes.length !== 1 + N_CANAIS_TELA || !(FONTES_SENTIDO_TELA as readonly string[]).includes(partes[0]!)) {
    throw new Error(`sentido_tela malformado: ${JSON.stringify(valor)}`);
  }
  return [partes[0]!, niveisTela(partes.slice(1).map(naturalCanonico))];
}

/** os sete niveis do evento na escala do corpo: div_arred(n x escala, 15) */
export function intensidadesDosNiveis(niveis: readonly number[], escala: number): Record<CanalTela, number> {
  return Object.fromEntries(CANAIS_TELA.map((c, i) => [c, divArred(niveis[i]! * escala, NIVEL_MAX_TELA)])) as Record<CanalTela, number>;
}

// ================================================================== a TV (tv.TV)
interface Segmento { inicio: number; fim: number; programa: number; cenas: number[][] }

export class TV {
  readonly cfg: ConfigTV;
  readonly x: number;
  readonly y: number;
  readonly trocasCanal: { tick: number; programa: number; antes: number | null; ate: number }[] = [];
  readonly sentidos: { tick: number; fonte: string; niveis: number[] }[] = [];
  private sentido: [string, number[]] | null = null;
  private readonly rng: RandomPy | null = null;
  readonly programas: number[][] = [];
  readonly grade: Segmento[] = [];
  private readonly inicios: number[] = [];
  private dono: { segmento: number; programa: number } | null = null;

  constructor(cfg: ConfigTV, semente: number | bigint, x: number, y: number) {
    if (!cfg.ligada) throw new TVSemChave("a TV precisa da ConfigTV ligada");
    this.cfg = conferirConfigTV(cfg);
    this.x = x;
    this.y = y;
    if (cfg.fonte === "grade") {
      const r = this.rng = new RandomPy(derivarSemente("tv-programas", semente));
      for (let p = 0; p < cfg.n_programas; p++) this.programas.push(CANAIS_TELA.map(() => r.randint(0, cfg.escala)));
    }
  }

  private estender(tick: number): void {
    const cfg = this.cfg, r = this.rng!, g = this.grade;
    while (!g.length || g[g.length - 1]!.fim <= tick) {
      const inicio = g.length ? g[g.length - 1]!.fim : 0;
      const n = cfg.n_programas;
      const p = !g.length ? r.randrange(n) : (g[g.length - 1]!.programa + 1 + r.randrange(n - 1)) % n;
      const dur = r.randint(cfg.programa_min_ticks, cfg.programa_max_ticks);
      const v = cfg.variacao, nCenas = Math.ceil(dur / cfg.cena_ticks);
      const cenas: number[][] = [];
      for (let k = 0; k < nCenas; k++) cenas.push(CANAIS_TELA.map(() => r.randint(-v, v)));
      g.push({ inicio, fim: inicio + dur, programa: p, cenas });
      this.inicios.push(inicio);
    }
  }

  private segmento(tick: number): number {
    if (!Number.isInteger(tick) || tick < 0) throw new Error(`tick da TV inteiro >= 0: ${tick}`);
    this.estender(tick);
    let lo = 0, hi = this.inicios.length;          // bisect_right(inicios, tick) - 1
    while (lo < hi) { const m = (lo + hi) >> 1; if (this.inicios[m]! <= tick) lo = m + 1; else hi = m; }
    return lo - 1;
  }

  /** o programa que passa no tick; null fora da fonte "grade" */
  programaEm(tick: number): number | null {
    if (this.cfg.fonte !== "grade") return null;
    const i = this.segmento(tick), d = this.dono;
    return d !== null && d.segmento === i ? d.programa : this.grade[i]!.programa;
  }

  /** o que a TV passa no tick, um inteiro em [0, escala] por canal; null com a TV desligada (a fonte "evento" antes do primeiro evento) */
  em(tick: number): Record<CanalTela, number> | null {
    const cfg = this.cfg;
    if (cfg.fonte === "evento") return this.sentido === null ? null : intensidadesDosNiveis(this.sentido[1], cfg.escala);
    const i = this.segmento(tick), seg = this.grade[i]!, d = this.dono;
    const perfil = this.programas[d !== null && d.segmento === i ? d.programa : seg.programa]!;
    const cena = seg.cenas[Math.floor((tick - seg.inicio) / cfg.cena_ticks)]!;
    return Object.fromEntries(CANAIS_TELA.map((c, k) => [c, Math.min(cfg.escala, Math.max(0, perfil[k]! + cena[k]!))])) as Record<CanalTela, number>;
  }

  trocarCanal(programa: number, tick: number): { tick: number; programa: number; antes: number | null; ate: number } {
    if (this.cfg.fonte !== "grade") throw new TVSemChave(`trocar_canal com a fonte ${this.cfg.fonte}: o canal so existe na TV do jogo`);
    if (!Number.isInteger(programa) || programa < 0 || programa >= this.cfg.n_programas) {
      throw new Error(`trocar_canal para um programa que nao existe (0 a ${this.cfg.n_programas - 1}): ${programa}`);
    }
    const antes = this.programaEm(tick);
    const i = this.segmento(tick);
    this.dono = { segmento: i, programa };
    const reg = { tick, programa, antes, ate: this.grade[i]!.fim };
    this.trocasCanal.push(reg);
    return reg;
  }

  sentir(fonte: string, niveis: readonly number[], tick: number): void {
    if (this.cfg.fonte !== "evento") throw new TVSemChave(`sentido_tela com a fonte ${this.cfg.fonte}: o modo livre gravado e a fonte "evento"`);
    if (!(FONTES_SENTIDO_TELA as readonly string[]).includes(fonte)) throw new Error(`fonte do sentido_tela em ${FONTES_SENTIDO_TELA}: ${fonte}`);
    this.sentido = [fonte, [...niveis]];
    this.sentidos.push({ tick, fonte, niveis: [...niveis] });
  }

  resumo(): Record<string, unknown> {
    return { x: this.x, y: this.y, fonte: this.cfg.fonte, trocas_canal: this.trocasCanal.map(t => ({ ...t })),
             sentidos: this.sentidos.map(s => ({ ...s, niveis: [...s.niveis] })) };
  }
}

// ================================================================== o resumo do GV-15 (quem grava o evento)
/** a media de uma janela de amostras em [0, 1] num dos 16 niveis: floor(media x 15 + 1/2) */
export function nivelDaMedia(amostras: readonly number[]): number {
  if (!amostras.length) throw new Error("janela da tela sem amostras");
  let soma = 0;
  for (const a of amostras) {
    if (typeof a !== "number" || !(a >= 0 && a <= 1)) throw new Error(`amostra da tela fora de [0, 1]: ${a}`);
    soma += a;
  }
  return Math.min(NIVEL_MAX_TELA, Math.floor(soma / amostras.length * NIVEL_MAX_TELA + 0.5));
}

/** GV-15: um vetor por segundo real (sete numeros em [0, 1]); a cada `janela` vetores, a media em 16 niveis; o evento so na mudanca */
export class ResumoTela {
  readonly fonte: string;
  readonly janela: number;
  private amostras: number[][] = [];
  ultimo: number[] | null = null;

  constructor(fonte: string, janela: number = CONFIG_TV.janela_resumo_s) {
    if (!(FONTES_SENTIDO_TELA as readonly string[]).includes(fonte)) throw new Error(`fonte do sentido_tela em ${FONTES_SENTIDO_TELA}: ${fonte}`);
    if (!Number.isInteger(janela) || janela < 1) throw new Error(`janela do resumo inteira >= 1: ${janela}`);
    this.fonte = fonte;
    this.janela = janela;
  }

  /** a amostra; devolve o valor do evento `sentido_tela` (`fonte|n1|...|n7`) quando a janela fecha com niveis novos, senao null */
  amostra(vetor: readonly number[]): string | null {
    if (vetor.length !== N_CANAIS_TELA) throw new Error(`o vetor da tela tem ${N_CANAIS_TELA} canais, veio ${vetor.length}`);
    this.amostras.push([...vetor]);
    if (this.amostras.length < this.janela) return null;
    const niveis = CANAIS_TELA.map((_, k) => nivelDaMedia(this.amostras.map(a => a[k]!)));
    this.amostras = [];
    if (this.ultimo !== null && niveis.join() === this.ultimo.join()) return null;
    this.ultimo = niveis;
    return valorSentidoTela(this.fonte, niveis);
  }
}
