/* Camada 2 — instinto (distribuicao exata) e bandit linear com Thompson sampling (espelho de
   policies/bandit.py + memoria + temperamento). O registro da decisao e somente leitura (motivo). */
import { ACOES_PET, C, CB, CDJ, CTP, FATORES_ESPACOS, FATORES_MEMORIA, NF, TEMP_NEUTRO, TICK_INICIAL, VERSAO_PET } from "./constantes.ts";
import { eNoite } from "./estado.ts";
import { Memoria, MemoriaEspacos, type MemoriaPolitica } from "./memoria.ts";
import type { Rng } from "./rng.ts";
import type { AcaoDono, AcaoPet, Desejo, Observacao, Temperamento } from "./tipos.ts";

export type Dist = Record<AcaoPet, number>;

export function distInstinto(obs: Observacao): Dist {
  const [fome, higiene, energia, humor, , , dormindo, hora] = obs.v;
  const d = Object.fromEntries(ACOES_PET.map(a => [a, 0])) as Dist;
  const um = (a: AcaoPet): Dist => { d[a] = 1; return d; };
  if (energia < .25) return um("dormir");
  if (dormindo > .5 && energia < .85) return um("dormir");
  if (eNoite(Math.floor(hora * 1440)) && energia < .55) return um("dormir");
  if (fome < .25 || higiene < .25) return um("chamar_atencao");
  if (obs.tdc > C.janelaAtencao) return um(humor < .35 ? "emburrar" : "chamar_atencao");
  if (fome < .45) { d.comer = .5; d.chamar_atencao = .5; return d; }
  const p: Partial<Dist> = { ocioso: 3, explorar: 2 + 2 * energia, brincar: 1 + 3 * humor, chamar_atencao: 1 };
  const tot = Object.values(p).reduce((s, w) => s + w, 0);
  for (const k in p) d[k as AcaoPet] = p[k as AcaoPet]! / tot;
  return d;
}

export function features(obs: Observacao): number[] {
  const [f, h, en, hu, s, su, dm, hora] = obs.v; const ang = 2 * Math.PI * hora;
  return [1, f, h, en, hu, s, su, dm, Math.sin(ang), Math.cos(ang), Math.min(1, obs.tdc / CB.escalaTdc)];
}
export function matvec(M: number[][], v: number[]): number[] { return M.map(l => l.reduce((s, x, j) => s + x * v[j], 0)); }
export function cholesky(M: number[][]): number[][] {
  const n = M.length, L = M.map(() => new Array<number>(n).fill(0));
  for (let i = 0; i < n; i++) for (let j = 0; j <= i; j++) {
    let s = M[i][j]; for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k];
    if (i === j) { if (s <= 0) throw new Error("matriz nao positiva definida"); L[i][j] = Math.sqrt(s); } else L[i][j] = s / L[j][j];
  }
  return L;
}
export class Braco {
  Ainv: number[][] = Array.from({ length: NF }, (_, i) => Array.from({ length: NF }, (_, j) => i === j ? 1 / CB.lambda : 0));
  b: number[] = new Array<number>(NF).fill(0);
  n = 0;
  private _t: number[] | null = null;
  private _L: number[][] | null = null;
  theta(): number[] { return this._t ??= matvec(this.Ainv, this.b); }
  chol(): number[][] { return this._L ??= cholesky(this.Ainv); }
  atualizar(x: number[], r: number): void {
    const Ax = matvec(this.Ainv, x); const den = 1 + x.reduce((s, xi, i) => s + xi * Ax[i], 0);
    for (let i = 0; i < NF; i++) for (let j = 0; j < NF; j++) this.Ainv[i][j] -= Ax[i] * Ax[j] / den;
    for (let i = 0; i < NF; i++) this.b[i] += r * x[i];
    this.n++; this._t = null; this._L = null;
  }
}

/** registro somente leitura da ultima decisao (motivo) */
export interface Decisao {
  x: number[]; acao: AcaoPet; amostras: Record<AcaoPet, number[]>; logPrior: Dist; gumbel: Dist; refsMem: Record<string, number | null>;
}

/** a necessidade de sempre (espelho de desejo._necessidade): a mais baixa abaixo do limiar, ou null. Os pets v2 a v10 (Bandit.desejo) e
    os v11 (desejoLobos) */
export function necessidade(obs: Observacao, tick: number): Desejo | null {
  const nec = ([["fome", 0, "comer"], ["higiene", 1, "limpar"], ["energia", 2, "dormir"], ["humor", 3, "brincar"]] as const)
    .map(([n, i, alvo]) => [obs.v[i], n, alvo] as const).filter(([v]) => v < CDJ.limiarNecessidade)
    .sort((a, b) => a[0] - b[0] || (a[1] < b[1] ? -1 : 1));
  if (!nec.length) return null;
  const [v, n, alvo] = nec[0];
  return { tick, tipo: "necessidade", alvo, causa: n, intensidade: (CDJ.limiarNecessidade - v) / CDJ.limiarNecessidade };
}

export class Bandit {
  bracos: Record<AcaoPet, Braco>;
  ultima: [number[], AcaoPet] | null = null;
  pendentes: [number, number[]][] = [];
  rec = { elogio: 0, repreensao: 0, atendido: 0, ignorado: 0 };
  k: { var: number; elogio: number; repr: number };
  v2: boolean;
  fatMem: readonly string[];
  mem: MemoriaPolitica;
  tUlt = TICK_INICIAL;
  ultDecisao: Decisao | null = null;
  constructor(temp: Temperamento = TEMP_NEUTRO, versao: number = VERSAO_PET) {
    this.bracos = Object.fromEntries(ACOES_PET.map(a => [a, new Braco()])) as Record<AcaoPet, Braco>;
    /* o temperamento muda so a escala com que a recompensa e usada (espelho de PoliticaBanditPersonalidade) */
    this.k = {
      var: CB.var * Math.exp(CTP.kCuriosidade * temp.curiosidade), elogio: CB.elogio * (1 + CTP.kSensibilidade * temp.sensibilidade),
      repr: CB.repr * (1 - CTP.kTeimosia * temp.teimosia) * (1 - CTP.kSensibilidade * temp.sensibilidade),
    };
    const fr = Math.exp(CTP.kRancor * temp.rancor);
    /* v2: memoria por espacos (rancor escala demora e bronca); v1: memoria curta antiga */
    this.v2 = versao >= 2; this.fatMem = this.v2 ? FATORES_ESPACOS : FATORES_MEMORIA;
    this.mem = this.v2 ? new MemoriaEspacos({ demora: fr, bronca: fr }, temp) : new Memoria(fr);
  }
  /** features do bandit v1 + memoria (tick = desde o ultimo cuidado + tick desse cuidado) */
  fx(obs: Observacao): number[] { return features(obs).concat(this.mem.feat(obs.tdc + this.tUlt)); }
  prior(obs: Observacao): Dist { const p = distInstinto(obs); const o = {} as Dist; for (const a of ACOES_PET) o[a] = (1 - CB.piso) * p[a] + CB.piso / ACOES_PET.length; return o; }
  agir(obs: Observacao, rng: Rng): AcaoPet {
    const x = this.fx(obs), p0 = this.prior(obs), esc = Math.sqrt(this.k.var);
    let melhor: AcaoPet | null = null, ms = -Infinity;
    const amostras = {} as Record<AcaoPet, number[]>, logPrior = {} as Dist, gumbel = {} as Dist;
    for (const a of ACOES_PET) {
      const br = this.bracos[a], th = br.theta(), L = br.chol();
      const z = Array.from({ length: NF }, () => rng.gauss());
      const Lz = matvec(L, z);
      let val = 0; for (let i = 0; i < NF; i++) val += (th[i] + esc * Lz[i]) * x[i];
      let u = rng.random(); while (u <= 0) u = rng.random();
      const gb = -Math.log(-Math.log(u));
      amostras[a] = th.map((t, i) => t + esc * Lz[i]); logPrior[a] = Math.log(p0[a]); gumbel[a] = gb;
      const s = Math.log(p0[a]) + val + gb;
      if (s > ms) { ms = s; melhor = a; }
    }
    /* registro somente leitura do que decidiu (motivo); nao muda a decisao */
    this.ultDecisao = { x, acao: melhor as AcaoPet, amostras, logPrior, gumbel, refsMem: this.mem.refs(obs.tdc + this.tUlt) };
    return melhor as AcaoPet;
  }
  /** desejo (espelho de desejo.py): necessidade abaixo do limiar; senao a vontade = acao de maior media
      da posterior (theta^ . x, sem prior e sem amostra) se a margem passar o limiar. Sem rng. */
  desejo(obs: Observacao, tick: number): Desejo | null {
    const nec = necessidade(obs, tick);
    if (nec) return nec;
    const x = this.fx(obs);
    const m = ACOES_PET.map((a, i) => [this.bracos[a].theta().reduce((s, t, j) => s + t * x[j], 0), -i, a] as const).sort((p, q) => q[0] - p[0] || q[1] - p[1]);
    const margem = m[0][0] - m[1][0];
    return margem < CDJ.limiarVontade ? null : { tick, tipo: "vontade", alvo: m[0][2], intensidade: Math.min(1, margem) };
  }
  /** distribuicao da politica media (theta^), para inspecao */
  media(obs: Observacao): Dist {
    const x = this.fx(obs), p0 = this.prior(obs); const s = {} as Dist;
    for (const a of ACOES_PET) { const th = this.bracos[a].theta(); s[a] = Math.log(p0[a]) + th.reduce((acc, t, i) => acc + t * x[i], 0); }
    const m = Math.max(...Object.values(s)); let tot = 0; for (const a in s) { s[a as AcaoPet] = Math.exp(s[a as AcaoPet] - m); tot += s[a as AcaoPet]; }
    for (const a in s) s[a as AcaoPet] /= tot; return s;
  }
  observar(obs: Observacao, acao: AcaoPet, tick: number): void {
    this.expirar(tick);
    const x = this.fx(obs); this.ultima = [x, acao];
    if (acao === "chamar_atencao") this.pendentes.push([tick, x]);
    if (this.v2) this.mem.avancar!(tick, obs.v[6] >= .5);
    this.mem.expirar(tick);
    if (acao === "chamar_atencao") this.mem.pedido(obs.v, tick);
  }
  receberAcaoDono(acao: AcaoDono, tick: number): void {
    this.tUlt = tick;
    this.expirar(tick);
    if (acao === "elogiar" || acao === "repreender") {
      if (!this.ultima) return;
      const [x, a] = this.ultima;
      if (acao === "elogiar") { this.bracos[a].atualizar(x, this.k.elogio); this.rec.elogio++; }
      else { this.bracos[a].atualizar(x, this.k.repr); this.rec.repreensao++; }
    } else {
      for (const [tp, x] of this.pendentes) { this.bracos.chamar_atencao.atualizar(x, 1 - (tick - tp) / CB.janela); this.rec.atendido++; }
      this.pendentes = [];
    }
    this.mem.acaoDono(acao, tick);
  }
  expirar(tick: number): void {
    const vivos: [number, number[]][] = [];
    for (const [tp, x] of this.pendentes) {
      if (tick - tp > CB.janela) { this.bracos.chamar_atencao.atualizar(x, CB.ignorado); this.rec.ignorado++; }
      else vivos.push([tp, x]);
    }
    this.pendentes = vivos;
  }
  assinatura(): string { return JSON.stringify([ACOES_PET.map(a => [this.bracos[a].b, this.bracos[a].n]), this.rec, this.pendentes.length, this.mem.assinatura()]); }
}
