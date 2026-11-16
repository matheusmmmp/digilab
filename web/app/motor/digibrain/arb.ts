/* M-ARB, a arbitragem: o espelho de digilab/digibrain/arb.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.7 e 7; PE-5; LM2). O reflexo do sono, os
   pesos, o sorteio proporcional (uma `rng.random()` com dois candidatos ou mais, a unica rng do cerebro) e as sondas "quem decidiu" (a C4, M4:
   `sem_lembranca`). As facetas (`sem_faceta`) e a escolha segurada (a C3, `segurar`) ficam fora do laboratorio (LAB-1): ligadas, falham alto.
   A guarda da fome urgente no brincar (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, EQ-7; `escolher(..., semBrincar = true)`, que o M-ADAPT passa
   so com a ConfigEquilibrioCuidado.guarda_fome_brincar e a fome urgente): o peso 0 nas unidades do brincar, no sorteio e nas sondas.
   O sono que segura (docs/TAREFA_V3_SONO_SEGURA.md; `sono` com a chave ligada): o reflexo tambem vale com o pet dormindo (o `contexto.dormindo`
   do M-SENS) e a energia abaixo de `lambda_acordar`, salvo a fome urgente (acima do `urgencia_lambda`). Desligado, o reflexo de hoje. */
import { ajustarDever, situacaoDever, type ConfigDever, type SensDever, type SituacaoDever } from "./dever.ts";
import { chaveJson, mul, phi } from "./_comum.ts";
import { CONFIG_SONO_SEGURA, INATOS_MODULAR, type ConfigSonoSegura } from "./constantes.ts";
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
  /** a CO7 (so com `ligarDever`): a situacao, as chaves removidas pelo escudo, as que reprovaram e quantas aprovaram; null sem outro pet */
  dever?: (SituacaoDever & { removidas: unknown[]; reprovadas: unknown[]; aprovadas: number }) | null;
}

export class Arbitragem {
  p: InatosArb;
  sondas: Record<string, readonly string[]>;
  decidiu: Record<string, string>;
  S: number;
  sorteios = 0;
  reflexos = 0;
  nada_a_fazer = 0;

  readonly sono: ConfigSonoSegura;

  constructor(inatosOuNulo: InatosArb | null = null, autobio = false, facetas = false, sono: ConfigSonoSegura = CONFIG_SONO_SEGURA) {
    this.p = inatosOuNulo ?? INATOS_MODULAR;
    this.sono = sono;
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

  /** a guarda da fome urgente no brincar (EQ-7): o peso 0 nas unidades do brincar */
  private static semBrincar(unidades: readonly UnidadeImpulso[], w: number[]): number[] {
    return w.map((x, i) => (unidades[i]!.acao === "brincar" ? 0 : x));
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

  /** o reflexo do sono: a leitura da energia abaixo de `lambda_sono` (sem rng); com o sono que segura, tambem o pet dormindo com a energia
   *  abaixo de `lambda_acordar` e sem a fome urgente (as `urgencias` do M-AFETO da decisao, so lidas com a chave ligada) */
  reflexo(sens: Pick<SaidaSens, "leitura"> & { contexto?: SaidaSens["contexto"] }, urgencias: Record<string, number> | null = null): boolean {
    const energia = sens.leitura["energia"];
    if (energia === undefined || energia === null) throw new Error("M-ARB: o reflexo do sono le a energia, e ela nao esta na percepcao do corpo");
    if (energia < this.p.lambda_sono) return true;
    if (!this.sono.ligada) return false;
    const fome = urgencias?.["fome"];
    if (fome === undefined) throw new Error("M-ARB: o sono que segura le a urgencia da fome, e ela nao veio do M-AFETO");
    if (sens.contexto === undefined) throw new Error("M-ARB: o sono que segura le o dormindo do contexto do M-SENS");
    return sens.contexto.dormindo > 0 && energia < this.sono.lambda_acordar && fome <= this.p.urgencia_lambda;
  }

  /** a CO7: o escudo e o peso da universalizacao (motor/digibrain/dever.ts) sobre os pesos, antes do sorteio e em cada sonda */
  ligarDever(cfg: ConfigDever): void { this.dever = cfg; }
  dever: ConfigDever | null = null;

  escolher(unidades: readonly UnidadeImpulso[], afeto: Pick<LeituraAfeto, "g_exp"> & Partial<Pick<LeituraAfeto, "urgencias">>,
    sens: Pick<SaidaSens, "leitura"> & Partial<SaidaSens>, rng: RngPolitica,
    reflexoOuNulo: boolean | null = null, segurar: unknown = null, semBrincar = false): SaidaArb {
    const p = this.p;
    if (segurar !== null) throw new Error("M-ARB: a escolha segurada (redecidir_evento) fica fora do laboratorio");
    const reflexo = reflexoOuNulo ?? this.reflexo(sens);
    if (typeof semBrincar !== "boolean") throw new Error(`M-ARB: sem_brincar e bool: ${String(semBrincar)}`);
    let w = this.pesos(unidades.map(x => x.a), afeto.g_exp);
    let sit: SituacaoDever | null = null, reg: ReturnType<typeof ajustarDever>[1] | null = null;
    const chaves = unidades.map(x => x.chave as readonly unknown[]);
    if (this.dever !== null && sens.social !== undefined && sens.social !== null) {    // a CO7: o escudo e a universalizacao, antes de tudo
      sit = situacaoDever(sens as SensDever, afeto.urgencias!, this.dever, this.S);
      [w, reg] = ajustarDever(chaves, w, sit);
    }
    if (semBrincar) w = Arbitragem.semBrincar(unidades, w);   // a guarda da fome urgente no brincar (EQ-7), depois da CO7 (D-EQ2-2)
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
      let ws = this.pesos(ativ, gExp);
      if (sit !== null) ws = ajustarDever(chaves, ws, sit)[0];   // a CO7: a sonda com o mesmo escudo e a mesma universalizacao
      const j = this.escolher_(unidades, semBrincar ? Arbitragem.semBrincar(unidades, ws) : ws, u);
      sondas[nome] = chaveJson(unidades[j]!.chave);
      sondas[this.decidiu[nome]!] = j !== i;
    }
    const out: SaidaArb = { indice: i, unidade: unidades[i]!, u, reflexo, nada_a_fazer: !reflexo && w.every(x => x === 0), pesos: w, sondas, segurada: false, fora: false };
    if (this.dever !== null)                           // a CO7: desligada, nenhum campo novo
      out.dever = sit === null ? null : { ...sit, removidas: reg!.removidas.map(j => chaveJson(unidades[j]!.chave)),
                                          reprovadas: reg!.reprovadas.map(j => chaveJson(unidades[j]!.chave)), aprovadas: reg!.aprovadas };
    return out;
  }

  estadoInterno(): Record<string, number> {
    return { sorteios: this.sorteios, reflexos: this.reflexos, nada_a_fazer: this.nada_a_fazer };
  }
}
