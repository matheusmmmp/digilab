/* M-ARB, a arbitragem: o espelho de digilab/digibrain/arb.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.7 e 7; PE-5; LM2). O reflexo do sono, os
   pesos, o sorteio proporcional (uma `rng.random()` com dois candidatos ou mais, a unica rng do cerebro) e as sondas "quem decidiu" (a C4, M4:
   `sem_lembranca`). As facetas (`sem_faceta`) e a escolha segurada (a C3, `segurar`) ficam fora do laboratorio (LAB-1): ligadas, falham alto. */
import { chaveJson, mul, phi } from "./_comum.ts";
import { INATOS_MODULAR } from "./constantes.ts";
import type { LeituraAfeto } from "./afeto.ts";
import type { SaidaSens } from "./sens.ts";
import type { UnidadeImpulso } from "./impulso.ts";

export type InatosArb = typeof INATOS_MODULAR;

const SONDAS_BASE: Record<string, readonly string[]> = {
  sem_incentivo: ["incentivo"], sem_habito: ["habito"], sem_memoria: ["memoria"], sem_persistencia: ["persistencia"],
  sem_afeto: [], so_inato: ["incentivo", "habito", "memoria", "persistencia"],
};
const DECIDIU_BASE: Record<string, string> = {
  sem_incentivo: "incentivo_decidiu", sem_habito: "habito_decidiu", sem_memoria: "memoria_decidiu",
  sem_persistencia: "persistencia_decidiu", sem_afeto: "afeto_decidiu", so_inato: "aprendido_decidiu",
};

/** a rng de politica como o M-ARB a usa (o `random.Random` do Python: so `random()`) */
export interface RngPolitica { random(): number }

/** o indice sorteado: a primeira soma acumulada que passa de min(int(u x T), T - 1) */
export function sortearInteiro(pesos: readonly number[], u: number): number {
  const total = pesos.reduce((s, x) => s + x, 0);
  if (total <= 0) throw new Error(`M-ARB: soma dos pesos nao positiva: ${JSON.stringify(pesos)}`);
  const alvo = Math.min(Math.trunc(u * total), total - 1);
  let acumulado = 0;
  for (let i = 0; i < pesos.length; i++) {
    acumulado += pesos[i]!;
    if (acumulado > alvo) return i;
  }
  throw new Error("M-ARB: o sorteio passou do fim");
}

export interface SaidaArb {
  indice: number; unidade: UnidadeImpulso; u: number | null; reflexo: boolean; nada_a_fazer: boolean; pesos: number[];
  sondas: Record<string, unknown>; segurada: boolean; fora: boolean;
}

export class Arbitragem {
  p: InatosArb;
  sondas: Record<string, readonly string[]>;
  decidiu: Record<string, string>;
  S: number;
  sorteios = 0;
  reflexos = 0;
  nada_a_fazer = 0;

  constructor(inatosOuNulo: InatosArb | null = null, autobio = false, facetas = false) {
    this.p = inatosOuNulo ?? INATOS_MODULAR;
    if (facetas) throw new Error("M-ARB: a facetas_mem fica fora do laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, secao 3)");
    this.sondas = SONDAS_BASE;
    this.decidiu = DECIDIU_BASE;
    if (autobio) {                                  // a C4, M4 (6.1): sem_memoria tira tambem a lembranca; sem_lembranca tira so ela
      this.sondas = {
        ...Object.fromEntries(Object.entries(SONDAS_BASE).map(([n, t]) => [n, n === "sem_memoria" || n === "so_inato" ? [...t, "lembranca"] : t])),
        sem_lembranca: ["lembranca"],
      };
      this.decidiu = { ...DECIDIU_BASE, sem_lembranca: "lembranca_decidiu" };
    }
    this.S = this.p.escala;
  }

  pesos(ativacoes: readonly number[], gExp: number): number[] {
    const extra = mul(gExp, this.p.epsilon, this.S);
    return ativacoes.map(a => (a > 0 ? a + extra : 0));
  }

  private static ocioso(unidades: readonly UnidadeImpulso[]): number {
    const i = unidades.findIndex(u => u.acao === "ocioso");
    if (i < 0) throw new Error("M-ARB: sem a unidade ocioso");
    return i;
  }

  private escolher_(unidades: readonly UnidadeImpulso[], w: readonly number[], u: number | null): number {
    const positivos = w.flatMap((x, i) => (x > 0 ? [i] : []));
    if (!positivos.length) return Arbitragem.ocioso(unidades);
    if (positivos.length === 1) return positivos[0]!;
    if (u === null) return positivos.reduce((m, i) => (w[i]! > w[m]! ? i : m));   // o maior peso; o primeiro no empate
    return sortearInteiro(w, u);
  }

  /** o reflexo do sono: a leitura da energia abaixo de `lambda_sono` (sem rng) */
  reflexo(sens: Pick<SaidaSens, "leitura">): boolean {
    const energia = sens.leitura["energia"];
    if (energia === undefined || energia === null) throw new Error("M-ARB: o reflexo do sono le a energia, e ela nao esta na percepcao do corpo");
    return energia < this.p.lambda_sono;
  }

  escolher(unidades: readonly UnidadeImpulso[], afeto: Pick<LeituraAfeto, "g_exp">, sens: Pick<SaidaSens, "leitura">, rng: RngPolitica,
    reflexoOuNulo: boolean | null = null, segurar: unknown = null): SaidaArb {
    const p = this.p;
    if (segurar !== null) throw new Error("M-ARB: a escolha segurada (redecidir_evento) fica fora do laboratorio");
    const reflexo = reflexoOuNulo ?? this.reflexo(sens);
    const w = this.pesos(unidades.map(x => x.a), afeto.g_exp);
    let i: number;
    let u: number | null;
    if (reflexo) {
      i = unidades.findIndex(x => x.acao === "dormir");
      if (i < 0) throw new Error("M-ARB: sem a unidade dormir");
      u = null;
      this.reflexos += 1;
    } else {
      const nPos = w.filter(x => x > 0).length;
      u = nPos >= 2 ? rng.random() : null;
      if (u !== null) this.sorteios += 1;
      if (nPos === 0) this.nada_a_fazer += 1;
      i = this.escolher_(unidades, w, u);
    }
    const sondas: Record<string, unknown> = {};
    for (const [nome, tirar] of Object.entries(this.sondas)) {
      if (reflexo) {
        sondas[nome] = chaveJson(unidades[i]!.chave);
        sondas[this.decidiu[nome]!] = false;
        continue;
      }
      const ativ = unidades.map(x => {
        if (tirar.includes("memoria") && x.tipo === "ponto") return 0;
        let soma = x.soma;
        for (const t of tirar) {
          const v = x.termos[t];
          if (v === undefined) throw new Error(`M-ARB: o termo ${t} nao esta na unidade`);
          soma -= v;
        }
        return phi(soma, p.a_max);
      });
      const gExp = nome === "sem_afeto" ? p.e0 : afeto.g_exp;
      const j = this.escolher_(unidades, this.pesos(ativ, gExp), u);
      sondas[nome] = chaveJson(unidades[j]!.chave);
      sondas[this.decidiu[nome]!] = j !== i;
    }
    return { indice: i, unidade: unidades[i]!, u, reflexo, nada_a_fazer: !reflexo && w.every(x => x === 0), pesos: w, sondas, segurada: false, fora: false };
  }

  estadoInterno(): Record<string, number> {
    return { sorteios: this.sorteios, reflexos: this.reflexos, nada_a_fazer: this.nada_a_fazer };
  }
}
