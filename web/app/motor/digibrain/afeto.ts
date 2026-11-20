/* M-AFETO, os afetos e os moduladores: o espelho de digilab/digibrain/afeto.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.3; LM1).
   Na decisao (`ler`): a urgencia de cada receptor, o g_apr e o g_exp. Na consequencia: o sinal homeostatico do A, a valencia V e a excitacao
   E (forma I). Aritmetica inteira, sem rng. */
import { culpaInveja, type ConfigDever } from "./dever.ts";
import { contribuicoesCorpo, faltaReceptor, sinalCorpo, type PercepcaoCorpoLobos } from "../lobos.ts";
import { clamp, divArred, ganhoDeTau, integrar, mul } from "./_comum.ts";
import { INATOS_MODULAR } from "./constantes.ts";
import type { CorpoModular, SaidaSens } from "./sens.ts";

export const EXCITANTES = ["dor", "susto", "estresse"] as const;

/** o que o M-AFETO le da ConfigDigibrain (controle_g_apr, modula_g_apr e g_apr_constante; os controles de pesquisa ficam fora do laboratorio) */
export interface ConfigDigibrainAfeto { controle_g_apr: string; modula_g_apr: boolean; g_apr_constante: number }
export type InatosAfeto = typeof INATOS_MODULAR;
export interface ConfigAfeto { intervalo_decisao_ticks: number }

export interface LeituraAfeto {
  urgencias: Record<string, number>; V: number; E: number; e_usada: number | null; g_apr: number; g_exp: number;
  /** a CO7 (so com `ligarDever`): o que a decisao tirou da valencia */
  culpa?: number; inveja?: number;
}
export interface UltimoAfeto { r: number; r_n: number; canais: Record<string, number>; V: number; E: number }

/** os pesos w_d do A sem `pesos_drives`: todos 1 */
const pesosUm = (drives: readonly string[]): Record<string, number> => Object.fromEntries(drives.map(d => [d, 1]));

/** o r separado por drive, na ordem de `drives`: f_d = div_arred(ganho x (c_1 + ... + c_d), S) - div_arred(ganho x (c_1 + ... + c_(d-1)), S).
 *  A soma e o `sinal_corpo` (a soma telescopa). */
export function canaisDoSinal(antes: CorpoModular, depois: CorpoModular, drives: readonly string[], ganho: number, S: number): Record<string, number> {
  const canais: Record<string, number> = {};
  let acumulado = 0, anterior = 0;
  const contribuicoes = contribuicoesCorpo(antes as PercepcaoCorpoLobos, depois as PercepcaoCorpoLobos, drives, S, pesosUm(drives));
  for (const [d, c] of Object.entries(contribuicoes)) {
    acumulado += c;
    const parcial = divArred(ganho * acumulado, S);
    canais[d] = parcial - anterior;
    anterior = parcial;
  }
  return canais;
}

/** o M-AFETO */
export class Afeto {
  p: InatosAfeto;
  cd: ConfigDigibrainAfeto;
  S: number;
  kV: number;
  kE: number;
  doadora: readonly number[] | null;
  V = 0;
  E = 0;
  decisoes = 0;
  serie_e: number[] = [];
  ultimo: UltimoAfeto | null = null;

  constructor(cfg: ConfigAfeto, cfgDigibrain: ConfigDigibrainAfeto, inatos: InatosAfeto = INATOS_MODULAR, serieEDoadora: readonly number[] | null = null) {
    this.p = inatos;
    this.cd = cfgDigibrain;
    this.S = inatos.escala;
    const delta = cfg.intervalo_decisao_ticks;
    this.kV = ganhoDeTau(inatos.tau_v, delta, this.S);
    this.kE = ganhoDeTau(inatos.tau_e, delta, this.S);
    const embaralhado = this.cd.controle_g_apr === "embaralhado";
    if (embaralhado !== (serieEDoadora !== null)) throw new Error("a serie E da vida doadora vem so com o controle embaralhado (e e obrigatoria nele)");
    if (serieEDoadora !== null && serieEDoadora.some(e => !Number.isInteger(e) || e < 0 || e > this.S)) throw new Error("a serie E da vida doadora: inteiros em [0, S]");
    this.doadora = serieEDoadora === null ? null : [...serieEDoadora];
  }

  urgencia(falta: number): number {
    const p = this.p, S = this.S;
    return clamp(mul(p.urgencia_a, falta, S) + mul(p.urgencia_b, Math.max(0, falta - p.urgencia_lambda), S), 0, S);
  }

  /** o g_apr modulado por uma excitacao e */
  gAprDe(e: number): number {
    const p = this.p;
    return clamp(p.g0 + mul(p.beta_e, e, this.S), p.g_min, p.g_max);
  }

  /** a CO7 (4; CO7-6): a culpa e a inveja tiram da valencia da decisao (o V que o M-IMPULSO le), sem mexer no V guardado nem no corpo */
  ligarDever(cfg: ConfigDever): void { this.dever = cfg; }
  dever: ConfigDever | null = null;

  ler(sens: Pick<SaidaSens, "falta"> & Partial<SaidaSens>): LeituraAfeto {
    const p = this.p, S = this.S, cd = this.cd;
    const falta = sens.falta;
    const urg: Record<string, number> = {};
    for (const [r, f] of Object.entries(falta)) urg[r] = this.urgencia(f);
    let eUsada: number | null = null;
    let gApr: number;
    if (cd.controle_g_apr === "constante") {
      gApr = cd.g_apr_constante;
    } else if (cd.modula_g_apr) {
      if (cd.controle_g_apr === "embaralhado") {
        if (this.decisoes >= this.doadora!.length) throw new Error(`M-AFETO: a serie E da vida doadora tem ${this.doadora!.length} decisoes; esta e a ${this.decisoes + 1}`);
        eUsada = this.doadora![this.decisoes]!;
      } else {
        eUsada = this.E;
      }
      gApr = this.gAprDe(eUsada);
    } else {
      gApr = p.g0;
    }
    const maxUrg = Math.max(...Object.values(urg));
    const gExp = clamp(p.e0 + mul(p.beta_t, falta["tedio"] ?? 0, S) - mul(p.beta_u, maxUrg, S), 0, p.e_max);
    this.serie_e.push(this.E);
    this.decisoes += 1;
    const out: LeituraAfeto = { urgencias: urg, V: this.V, E: this.E, e_usada: eUsada, g_apr: gApr, g_exp: gExp };
    if (this.dever !== null) {                         // a CO7: a culpa e a inveja so na valencia desta decisao (desligada, a de hoje)
      const [culpa, inveja] = culpaInveja({ social: sens.social ?? null, leitura: sens.leitura! }, this.dever);
      out.V = clamp(this.V - culpa - inveja, -S, S);
      out.culpa = culpa;
      out.inveja = inveja;
    }
    return out;
  }

  drives(receptores: readonly string[]): string[] {
    return receptores.filter(r => !(this.p.fora_do_r as readonly string[]).includes(r));
  }

  /** `gostoVisual` (GOSTO_VISUAL, P1f; so na opcao de olhar, com a subchave `olhar`): o termo pronto soma ao r e entra nos canais */
  consequencia(pcAntes: CorpoModular, pcDepois: CorpoModular, receptores: readonly string[], gostoVisual: number | null = null): UltimoAfeto {
    const p = this.p, S = this.S;
    const drives = this.drives(receptores);
    const antes = pcAntes as PercepcaoCorpoLobos, depois = pcDepois as PercepcaoCorpoLobos;
    let r = sinalCorpo(antes, depois, drives, p.ganho_r, S, pesosUm(drives));
    const canais = canaisDoSinal(pcAntes, pcDepois, drives, p.ganho_r, S);
    if (gostoVisual !== null) {
      if (!Number.isInteger(gostoVisual)) throw new Error(`M-AFETO: gosto_visual e inteiro: ${gostoVisual}`);
      r += gostoVisual;
      canais["gosto_visual"] = gostoVisual;
    }
    const rN = clamp(divArred(r, p.r_norm), -S, S);
    this.V = integrar(this.V, rN, this.kV, S);
    const exc = Math.max(Math.abs(rN), ...EXCITANTES.filter(x => receptores.includes(x)).map(x => faltaReceptor(depois, x, S)));
    this.E = integrar(this.E, exc, this.kE, S);
    this.ultimo = { r, r_n: rN, canais, V: this.V, E: this.E };
    return this.ultimo;
  }

  /** a variacao do corpo da luta (ponte da luta, PE3; espelho de `Afeto.sigma_luta`): o mesmo r e r_n da `consequencia`, SEM mexer em V nem em E */
  sigmaLuta(pcAntes: CorpoModular, pcDepois: CorpoModular, receptores: readonly string[]): { r: number; r_n: number } {
    const p = this.p, S = this.S;
    const drives = this.drives(receptores);
    const r = sinalCorpo(pcAntes as PercepcaoCorpoLobos, pcDepois as PercepcaoCorpoLobos, drives, p.ganho_r, S, pesosUm(drives));
    return { r, r_n: clamp(divArred(r, p.r_norm), -S, S) };
  }

  estadoInterno(): { V: number; E: number; decisoes: number; ultimo: UltimoAfeto | null } {
    return { V: this.V, E: this.E, decisoes: this.decisoes, ultimo: this.ultimo };
  }
}
