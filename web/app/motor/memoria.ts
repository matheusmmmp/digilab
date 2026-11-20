/* Memorias do pet. Funcoes puras dos eventos que chegam a politica; o replay reconstroi.
   - Memoria: memoria curta dos pets v1 (espelho de digilab/memoria.py, ConfigMemoria)
   - MemoriaEspacos: pets v2+ (espelho de digilab/memoria_espacos.py; adendo DF, Parte 1): 4 espacos de
     curto prazo e 2 de longo, uma memoria por categoria, a mais forte vence; depois de 12 h a memoria
     tenta o longo prazo; a cada 4 h ACORDADO tudo e relembrado. Sem rng. */
import { CEM, CME, FATORES_ESPACOS, TEMP_NEUTRO, TICK_INICIAL, type CategoriaMemoria } from "./constantes.ts";
import type { AcaoDono, EixoTemperamento, Temperamento } from "./tipos.ts";

type Necessidade = "fome" | "higiene";

/* emocao filtrada pelo temperamento (adendo DF 2.1, espelho de emocao.py): regra vale se polo*eixo >
   limiar; vence o eixo de maior modulo; senao a padrao. Somente leitura. */
type RegraEmocao = [EixoTemperamento, "+" | "-", string, number];
export const EMOCOES: Record<CategoriaMemoria, { regras: RegraEmocao[]; padrao: [string, number] }> = {
  demora: { regras: [["rancor", "+", "raiva", -.9], ["sensibilidade", "+", "tristeza", -.7]], padrao: ["incomodo", -.4] },
  bronca: { regras: [["rancor", "+", "raiva", -.8], ["sensibilidade", "-", "ferido", -.9], ["teimosia", "+", "desdem", -.2]], padrao: ["vergonha", -.5] },
  elogio: { regras: [["sensibilidade", "+", "euforia", .9], ["teimosia", "+", "indiferenca", .1]], padrao: ["orgulho", .6] },
  carinho: { regras: [["sensibilidade", "+", "ternura", .8], ["curiosidade", "-", "timidez", .3]], padrao: ["alegria", .5] },
};
export interface Emocao { nome: string; valencia: number; eixo: EixoTemperamento | null }
export function emocaoDe(cat: CategoriaMemoria, temp: Temperamento): Emocao {
  const e = EMOCOES[cat]; if (!e) throw new Error("categoria sem emoção: " + cat);
  let melhor: [number, number, EixoTemperamento, string, number] | null = null;
  e.regras.forEach(([eixo, polo, nome, val], i) => {
    const v = temp[eixo];
    if ((polo === "+" ? v : -v) > CEM.limiarEixo && (!melhor || Math.abs(v) > melhor[0] || (Math.abs(v) === melhor[0] && i < melhor[1]))) melhor = [Math.abs(v), i, eixo, nome, val];
  });
  const m = melhor as [number, number, EixoTemperamento, string, number] | null;
  return m ? { nome: m[3], valencia: m[4], eixo: m[2] } : { nome: e.padrao[0], valencia: e.padrao[1], eixo: null };
}

/** interface comum das duas memorias, do ponto de vista do bandit */
export interface MemoriaPolitica {
  nDono: number;
  pedido(v: number[], tick: number): void;
  expirar(tick: number): void;
  acaoDono(a: AcaoDono, tick: number): void;
  feat(tick: number): number[];
  refs(tick: number): Record<string, number | null>;
  assinatura(): unknown[];
  avancar?(tick: number, dormindo?: boolean): void;
}

export interface Lembranca { cat: CategoriaMemoria; int: number; criada: number; relembrada: number; ref: number | null; emocao: string }
type ResultadoInsercao = "entrou" | "substituiu" | "descartada";

export function inserirMemoria(esp: Lembranca[], nova: Lembranca, n: number): [Lembranca[], ResultadoInsercao] {
  const i = esp.findIndex(m => m.cat === nova.cat);
  if (i >= 0) {
    if (nova.int >= esp[i].int) { const r = esp.slice(); r[i] = nova; return [r, "substituiu"]; }
    return [esp.slice(), "descartada"];
  }
  if (esp.length < n) return [[...esp, nova], "entrou"];
  let k = 0;
  for (let j = 1; j < esp.length; j++) if (esp[j].int < esp[k].int || (esp[j].int === esp[k].int && esp[j].criada < esp[k].criada)) k = j;
  if (nova.int >= esp[k].int) { const r = esp.slice(); r[k] = nova; return [r, "substituiu"]; }
  return [esp.slice(), "descartada"];
}
export const CATEGORIA_DA_ACAO: Partial<Record<AcaoDono, CategoriaMemoria>> = { repreender: "bronca", elogiar: "elogio", acariciar: "carinho", brincar: "carinho" };

export interface EmocaoLembrada extends Emocao { tick: number; cat: CategoriaMemoria; ref: number | null }

export class MemoriaEspacos implements MemoriaPolitica {
  temp: Temperamento;
  emocoes: EmocaoLembrada[] = [];
  nEmocoes = 0;
  fatorTau: Partial<Record<CategoriaMemoria, number>>;
  curto: Lembranca[] = [];
  longo: Lembranca[] = [];
  nDono = 0;
  pend: Record<Necessidade, number[]> = { fome: [], higiene: [] };
  acordado = 0;
  tick = TICK_INICIAL;
  dormindo = false;
  relembrancas = 0;
  ultRel: number | null = null;
  cont = { entrou: 0, substituiu: 0, descartada: 0, promovida: 0, esquecida: 0 };
  constructor(fatorTau: Partial<Record<CategoriaMemoria, number>> = {}, temp: Temperamento = TEMP_NEUTRO) {
    this.temp = temp; this.fatorTau = fatorTau;
  }
  /** processa o tempo ate `tick` com o sono ANTERIOR; `dormindo`, se dado, vale dali em diante */
  avancar(tick: number, dormindo?: boolean): void {
    if (tick < this.tick) throw new Error(`memória: tempo voltou (${tick} < ${this.tick})`);
    let t = this.tick;
    while (t < tick) {
      let fim = tick;
      if (!this.dormindo) fim = Math.min(fim, t + (CME.relembrar - this.acordado % CME.relembrar));
      for (const m of this.curto) if (m.criada + CME.dCurto > t) fim = Math.min(fim, m.criada + CME.dCurto);
      if (!this.dormindo) this.acordado += fim - t;
      t = fim;
      this._promover(t);
      if (!this.dormindo && this.acordado > 0 && this.acordado % CME.relembrar === 0) this._relembrar(t);
    }
    this.tick = tick;
    if (dormindo !== undefined) this.dormindo = dormindo;
  }
  private _promover(tick: number): void {
    const vencidas = this.curto.filter(m => m.criada + CME.dCurto <= tick).sort((a, b) => a.criada - b.criada || (a.cat < b.cat ? -1 : 1));
    for (const m of vencidas) {
      this.curto = this.curto.filter(x => x !== m);
      let r: ResultadoInsercao; [this.longo, r] = inserirMemoria(this.longo, m, CME.nLongo);
      this.cont[r !== "descartada" ? "promovida" : "esquecida"]++;
    }
  }
  private _relembrar(tick: number): void {
    if (this.ultRel === tick) return;
    this.ultRel = tick; this.relembrancas++;
    this.curto = this.curto.map(m => ({ ...m, relembrada: tick })); this.longo = this.longo.map(m => ({ ...m, relembrada: tick }));
  }
  lembrar(cat: CategoriaMemoria, int: number, tick: number, ref: number | null): void {
    if (!(cat in CME.intensidade)) throw new Error("categoria de memória desconhecida: " + cat);
    if (!(int > 0 && int <= 1)) throw new Error("intensidade fora de (0, 1]: " + int);
    this.avancar(tick);
    const em = emocaoDe(cat, this.temp);
    this.emocoes.push({ tick, cat, ref, ...em }); this.nEmocoes++; if (this.emocoes.length > 30) this.emocoes.shift();
    let r: ResultadoInsercao; [this.curto, r] = inserirMemoria(this.curto, { cat, int, criada: tick, relembrada: tick, ref, emocao: em.nome }, CME.nCurto);
    this.cont[r]++;
  }
  pedido(v: number[], tick: number): void {
    const [fome, hig] = v; const [nec, val]: [Necessidade, number] = fome <= hig ? ["fome", fome] : ["higiene", hig];
    if (val < CME.limiarPedido) this.pend[nec].push(tick);
  }
  expirar(tick: number): void {
    for (const nec of ["fome", "higiene"] as const) {
      const perdidos = this.pend[nec].filter(t => tick - t > CME.janela);
      if (perdidos.length) {
        this.pend[nec] = this.pend[nec].filter(t => tick - t <= CME.janela);
        this.lembrar("demora", 1, Math.max(tick, this.tick), null);   /* pedido perdido: demora maxima */
      }
    }
  }
  acaoDono(a: AcaoDono, tick: number): void {
    this.nDono++; this.expirar(tick);
    const nec = a === "alimentar" ? "fome" : a === "limpar" ? "higiene" : null;
    if (nec && this.pend[nec].length) {
      const lat = tick - this.pend[nec][0]; this.pend[nec] = [];
      if (lat > 0) this.lembrar("demora", Math.min(1, lat / CME.janela), tick, this.nDono);
    }
    const cat = CATEGORIA_DA_ACAO[a];
    if (cat) this.lembrar(cat, CME.intensidade[cat] as number, tick, this.nDono);
    this.avancar(tick);
  }
  tau(cat: CategoriaMemoria): number { return CME.tau * (this.fatorTau[cat] ?? 1); }
  ativacao(m: Lembranca, tick: number): number { return m.int * Math.exp(-Math.max(0, tick - m.relembrada) / this.tau(m.cat)); }
  feat(tick: number): number[] { const todas = [...this.curto, ...this.longo]; return FATORES_ESPACOS.map(c => Math.min(1, todas.filter(m => m.cat === c).reduce((s, m) => s + this.ativacao(m, tick), 0))); }
  refs(tick: number): Record<string, number | null> {
    const out: Record<string, number | null> = {}, todas = [...this.curto, ...this.longo];
    for (const c of FATORES_ESPACOS) {
      let best: Lembranca | null = null;
      for (const m of todas.filter(x => x.cat === c)) if (!best || this.ativacao(m, tick) > this.ativacao(best, tick) || (this.ativacao(m, tick) === this.ativacao(best, tick) && m.criada > best.criada)) best = m;
      out[c] = best ? best.ref : null;
    }
    return out;
  }
  assinatura(): unknown[] { return [this.curto, this.longo, this.nDono, this.pend, this.acordado, this.tick, this.dormindo, this.relembrancas, this.cont, this.nEmocoes]; }
}
