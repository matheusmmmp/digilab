/* A leitura do gabarito do DigiBrain modular (LM0, experiments/exportar_gabarito_digibrain_modular.py) para os G-PAR da LM1 a LM4:
   os .json.gz das vidas, a resolucao dos `$ref` (a saida de uma chamada anterior da mesma decisao) e a comparacao estrita (inclusive -0). */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";

export interface Chamada { m: string; e: unknown[]; s: unknown; rng_antes?: string[]; rng_depois?: string[] }
export interface DecisaoGab { k: number; chamadas: Chamada[]; assinatura: Record<string, string>; motivo: unknown }
export interface VidaGab { dono: string; lugar: string; semente: number; dias: number; decisoes: DecisaoGab[] }
export interface LeituraPlast { m: string; e: unknown[]; s: number }
export interface VidaLeituras { dono: string; lugar: string; semente: number; decisoes: { k: number; chamadas: LeituraPlast[] }[] }

const aqui = (rel: string): URL => new URL(`./gabaritos/${rel}`, import.meta.url);
const lerGz = <T>(rel: string): T => JSON.parse(gunzipSync(readFileSync(aqui(rel))).toString("utf8")) as T;

export const LUGARES = ["longe_fixo", "comedouro"] as const;
let cacheVidas: VidaGab[] | null = null;
let cacheLeituras: VidaLeituras[] | null = null;

/** as oito vidas, na ordem do gabarito (longe_fixo, depois comedouro) */
export function vidasModular(): VidaGab[] {
  cacheVidas ??= LUGARES.flatMap(l => lerGz<{ vidas: VidaGab[] }>(`digibrain_modular_${l}.json.gz`).vidas);
  return cacheVidas;
}
/** as leituras do M-PLAST dentro do impulso (habito e incentivo), na mesma ordem das vidas */
export function leiturasPlast(): VidaLeituras[] {
  cacheLeituras ??= lerGz<{ vidas: VidaLeituras[] }>("digibrain_modular_leituras_plast.json.gz").vidas;
  return cacheLeituras;
}
export function constantesModular(): Record<string, any> {
  return JSON.parse(readFileSync(aqui("digibrain_modular_constantes.json"), "utf8")) as Record<string, any>;
}

/** a entrada `i` da chamada, com os `$ref` trocados pela saida da chamada anterior da decisao (o rotulo `modulo.metodo`, ou
 *  `modulo.metodo[i]` para o elemento de uma tupla) */
export function entrada(d: DecisaoGab, c: Chamada, i: number): any {
  const v = c.e[i] as any;
  if (v !== null && typeof v === "object" && !Array.isArray(v) && "$ref" in v) {
    const rotulo = v["$ref"] as string;
    const m = /^(.*?)(?:\[(\d+)\])?$/.exec(rotulo)!;
    const origem = d.chamadas.find(x => x.m === m[1]);
    if (!origem) throw new Error(`$ref ${rotulo}: sem a chamada ${m[1]} na decisao ${d.k}`);
    return m[2] === undefined ? origem.s : (origem.s as unknown[])[Number(m[2])];
  }
  return v;
}

/** igual, estrito (distingue -0), com a mensagem curta */
export function conferir(onde: string, obtido: unknown, esperado: unknown): void {
  try {
    assert.deepStrictEqual(obtido, esperado);
  } catch (e) {
    const ord = (_: string, v: unknown) => (v && typeof v === "object" && !Array.isArray(v) ? Object.fromEntries(Object.entries(v).sort(([x], [y]) => (x < y ? -1 : 1))) : v);
    const a = JSON.stringify(obtido, ord), b = JSON.stringify(esperado, ord);
    let i = 0;
    while (i < a.length && a[i] === b[i]) i++;
    throw new Error(`${onde}: difere perto do caractere ${i}\n  TS:     ...${a.slice(Math.max(0, i - 80), i + 120)}\n  Python: ...${b.slice(Math.max(0, i - 80), i + 120)}`);
  }
}
