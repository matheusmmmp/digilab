/* M-PLAST, a plasticidade: o espelho de digilab/digibrain/plast.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.3, 2.4 e 4.8; LM2). Duas regras locais,
   inteiras, multiplicadas pelo `g_apr` do M-AFETO: P1 (o modelo do desfecho e o incentivo, o "querer") e P2 (o habito hebbiano de tres fatores,
   creditado por opcao). Sem rng. A aritmetica e a do Python (`divArred`, `mul`). */
import { leituraReceptor, sinalCorpo, type PercepcaoCorpoLobos } from "../lobos.ts";
import { clamp, divArred, mul, raizInteira } from "./_comum.ts";
import { CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTOS_DIGIBRAIN, INATOS_MODULAR } from "./constantes.ts";
import type { PlastImpulso } from "./impulso.ts";
import type { CorpoModular } from "./sens.ts";

export const CLASSES_DESFECHO = ["racao", "a", "b", "c", "podre", "bola"] as const;

export type InatosPlast = typeof INATOS_MODULAR;
/** o que o M-PLAST le da ConfigDigibrain */
export interface ConfigDigibrainPlast { p1: boolean; p2: boolean }

/** a opcao que acabou (o que o M-ESTADO entrega ao P2): so os campos que o P2 le */
export interface OpcaoCredito { chave: readonly unknown[]; e: readonly number[]; r: number; g_apr: number }
export interface RegistroP1 { regra: "P1"; classe: string; antes: number[]; depois: number[]; abs: number }
export interface RegistroP2 { regra: "P2"; b: string; r_n: number; abs: number }

/** valor_previsto (lobos.py): o `sinal_corpo` dos receptores de agora para os previstos (a leitura de agora mais o delta, cortada em [0, S]).
 *  Inteiro; os pesos dos drives sao todos 1 (o Python sem `pesos_drives`). */
function valorPrevisto(pc: CorpoModular, delta: Record<string, number>, drives: readonly string[], ganho: number, S: number): number {
  const novos: Record<string, number> = {};
  for (const [r, v] of Object.entries(delta)) {
    if (v !== 0) novos[r] = Math.max(0, Math.min(S, leituraReceptor(pc as PercepcaoCorpoLobos, r, S) + v));
  }
  if (Object.keys(novos).length === 0) return 0;
  const pesos = Object.fromEntries(drives.map(d => [d, 1]));
  return sinalCorpo(pc as PercepcaoCorpoLobos, { ...pc, ...novos } as PercepcaoCorpoLobos, drives, ganho, S, pesos);
}

export class Plasticidade implements PlastImpulso {
  p: InatosPlast;
  cd: ConfigDigibrainPlast;
  S: number;
  receptores: string[] | null = null;
  desfecho: Record<string, number[]> | null = null;
  andar = 0;
  H: Record<string, number[]>;
  consumos: Record<string, number>;
  amostras_andar = 0;
  creditos = 0;

  constructor(cfgDigibrain: ConfigDigibrainPlast, inatosOuNulo: InatosPlast | null = null) {
    this.p = inatosOuNulo ?? INATOS_MODULAR;
    this.cd = cfgDigibrain;
    this.S = this.p.escala;
    this.H = Object.fromEntries(COMPORTAMENTOS_DIGIBRAIN.map(b => [b, new Array<number>(CARACTERISTICAS_DIGIBRAIN.length).fill(0)]));
    this.consumos = Object.fromEntries(CLASSES_DESFECHO.map(c => [c, 0]));
  }

  montar(receptores: readonly string[]): void {
    if (this.receptores === null) {
      this.receptores = [...receptores];
      this.desfecho = Object.fromEntries(CLASSES_DESFECHO.map(c => [c, new Array<number>(receptores.length).fill(0)]));
    } else if (receptores.length !== this.receptores.length || receptores.some((r, i) => r !== this.receptores![i])) {
      throw new Error(`M-PLAST: receptores ${JSON.stringify(receptores)}, montado com ${JSON.stringify(this.receptores)}`);
    }
  }

  // ------------------------------------------------------------ o que vai ao M-IMPULSO
  /** o incentivo da classe, antes da proximidade: clamp(div_arred(c_G x valor_previsto, S_V), 0, G_max). Sem o P1, 0. */
  incentivo(pc: CorpoModular, classe: string, drives: readonly string[]): number {
    if (!this.cd.p1) return 0;
    const p = this.p;
    const dt = this.desfecho?.[classe];
    if (dt === undefined) throw new Error(`M-PLAST: classe ${classe} (ou o M-PLAST sem montar)`);
    const delta = Object.fromEntries(this.receptores!.map((r, i) => [r, dt[i]!]));
    const v = valorPrevisto(pc, delta, drives, p.ganho_r, this.S);
    return clamp(divArred(p.c_g * v, p.s_v), 0, p.g_max_incentivo);
  }

  /** o termo do habito do comportamento b: sum_j mul(H[b,j], z_j). Sem o P2, 0. */
  habito(b: string, z: readonly number[]): number {
    if (!this.cd.p2) return 0;
    let total = 0;
    this.H[b]!.forEach((h, j) => { if (h) total += mul(h, z[j]!, this.S); });
    return total;
  }

  // ------------------------------------------------------------ P1
  private passo(valor: number, alvo: number, gApr: number): number {
    return valor + mul(mul(gApr, this.p.eta_d, this.S), alvo - valor, this.S);
  }

  /** P1 na consequencia de comer (o andar e o consumo) ou de brincar com a bola (o consumo). `classe` = o que foi consumido (null: nada). */
  consequenciaP1(acao: string, classe: string | null, l0: readonly number[], l1: readonly number[], pos0: readonly [number, number],
    pos1: readonly [number, number], gApr: number): RegistroP1 | null {
    if (!this.cd.p1) return null;
    const S = this.S;
    const d = raizInteira((pos1[0] - pos0[0]) * (pos1[0] - pos0[0]) + (pos1[1] - pos0[1]) * (pos1[1] - pos0[1]));
    const ie = this.receptores!.indexOf("energia");
    if (acao === "comer" && d > 0 && ie >= 0) {
      const amostra = divArred((l1[ie]! - l0[ie]!) * S, d);
      this.andar = this.passo(this.andar, amostra, gApr);
      this.amostras_andar += 1;
    }
    if (classe === null) return null;
    const delta = l1.map((b, i) => b - l0[i]!);
    if (ie >= 0) delta[ie]! -= divArred(this.andar * d, S);
    return this.consumo(classe, delta, gApr);
  }

  /** um consumo percebido da classe: o desfecho anda em direcao a `delta` (os receptores, na ordem do layout) */
  consumo(classe: string, delta: readonly number[], gApr: number): RegistroP1 {
    if (!(CLASSES_DESFECHO as readonly string[]).includes(classe)) throw new Error(`M-PLAST: classe ${classe}`);
    if (delta.length !== this.receptores!.length || delta.some(v => !Number.isInteger(v))) {
      throw new Error(`M-PLAST: delta ${JSON.stringify(delta)} fora do layout ${JSON.stringify(this.receptores)}`);
    }
    const dt = this.desfecho![classe]!;
    const antes = [...dt];
    delta.forEach((v, i) => { dt[i] = clamp(this.passo(dt[i]!, v, gApr), -this.S, this.S); });
    this.consumos[classe]! += 1;
    return { regra: "P1", classe, antes, depois: [...dt], abs: dt.reduce((s, b, i) => s + Math.abs(b - antes[i]!), 0) };
  }

  // ------------------------------------------------------------ P2
  /** P2 numa opcao que acabou: so a linha do comportamento dela. Devolve o registro (null sem o P2). */
  creditar(op: OpcaoCredito): RegistroP2 | null {
    if (!this.cd.p2) return null;
    const p = this.p, S = this.S;
    const b = op.chave[0] as string;
    const rN = op.r;
    const passo = mul(op.g_apr, p.eta_h, S);
    const linha = this.H[b]!;
    const antes = [...linha];
    op.e.forEach((e, j) => {
      if (e === 0) return;
      linha[j] = clamp(linha[j]! + mul(passo, mul(rN, e, S), S), -p.h_max, p.h_max);
    });
    this.creditos += 1;
    return { regra: "P2", b, r_n: rN, abs: linha.reduce((s, x, j) => s + Math.abs(x - antes[j]!), 0) };
  }

  // ------------------------------------------------------------ leituras
  desfechoZero(): boolean {
    return this.andar === 0 && (this.desfecho === null || Object.values(this.desfecho).every(dt => dt.every(v => v === 0)));
  }
  habitoZero(): boolean { return Object.values(this.H).every(l => l.every(v => v === 0)); }
  /** (quantos H em +-H_max, quantos H) */
  noTeto(): [number, number] {
    const vs = Object.values(this.H).flat();
    return [vs.filter(v => Math.abs(v) === this.p.h_max).length, vs.length];
  }

  estadoInterno(): Record<string, unknown> {
    return { receptores: this.receptores === null ? null : [...this.receptores], desfecho: this.desfecho, andar: this.andar,
      H: Object.fromEntries(Object.entries(this.H).map(([b, v]) => [b, [...v]])), consumos: { ...this.consumos },
      amostras_andar: this.amostras_andar, creditos: this.creditos };
  }
}
