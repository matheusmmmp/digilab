/* Confianca de combate e desgaste por rival repetido (MVP M1; espelho fiel de digilab/confianca.py: mesmas
   formulas, mesma ordem de operacoes; paridade conferida em test/confianca.test.ts contra o gabarito do Python).
   Um ESTADO derivado das lutas que ja estao no registro (evento "l"): nenhum evento novo, o replay recalcula.
   Sem rng. So os pets v5 usam (docs/DESIGN_MVP_M1_CONFIANCA.md, tudo PROPOSTO em CCF). */
import { CCF } from "./constantes.ts";

export type EstadoConfianca = "confiante" | "inseguro" | "entediado" | "neutro";
export const ESTADOS_CONFIANCA: readonly EstadoConfianca[] = ["confiante", "inseguro", "entediado", "neutro"];
export interface LutaConfianca { tick: number; rival: string; sinal: -1 | 0 | 1; novidade: number; c: number }
export interface VistaConfianca { estado: EstadoConfianca; desde: number | null; c: number; lutas: number[] }
type Cfg = typeof CCF;

/** novidade de enfrentar um rival com contador de encontros `mAntes` (1 no primeiro encontro) */
export function novidade(mAntes: number, lam: number): number {
  if (mAntes < 0) throw new Error("contador de encontros negativo: " + mAntes);
  return Math.exp(-lam * mAntes);
}
/** contador de encontros do rival depois de mais uma luta, `dt` minutos depois da anterior contra ele */
export function atualizarEncontros(m: number, dt: number, tau: number): number {
  if (dt < 0) throw new Error("dt negativo: " + dt);
  return m * Math.exp(-dt / tau) + 1;
}
/** a confianca decai para 0 com o tempo de jogo sem lutar */
export function decairConfianca(c: number, dt: number, tau: number): number {
  if (dt < 0) throw new Error("dt negativo: " + dt);
  return c * Math.exp(-dt / tau);
}
/** confianca depois de uma luta `dt` minutos depois da ultima (sinal +1 vitoria, -1 derrota, 0 empate) */
export function atualizarConfianca(c: number, dt: number, sinal: number, nov: number, sensibilidade: number, cfg: Cfg = CCF): number {
  if (sinal !== -1 && sinal !== 0 && sinal !== 1) throw new Error("sinal da luta inválido: " + sinal);
  if (!(sensibilidade >= -1 && sensibilidade <= 1)) throw new Error("sensibilidade fora de [-1, 1]: " + sensibilidade);
  c = decairConfianca(c, dt, cfg.tauConf);
  const eta = sinal < 0 ? cfg.eta * (1 + cfg.kSens * sensibilidade) : cfg.eta;
  return Math.max(-1, Math.min(1, c + eta * nov * sinal));
}
/** termo da inseguranca no epsilon do lutador do pet: kappa * max(0, -c) */
export function epsilonConfianca(c: number, kappa: number): number {
  if (!(c >= -1 && c <= 1)) throw new Error("confiança fora de [-1, 1]: " + c);
  return kappa * Math.max(0, -c);
}
/** faixa bruta (sem histerese): confiante e inseguro pela confianca; entediado pelas ultimas n lutas */
export function faixa(c: number, novidades: readonly number[], cfg: Cfg = CCF): EstadoConfianca {
  if (c >= cfg.limiarFrase) return "confiante";
  if (c <= -cfg.limiarFrase) return "inseguro";
  if (novidades.length >= cfg.nTedio && novidades.slice(-cfg.nTedio).every(n => n <= cfg.limiarTedio)) return "entediado";
  return "neutro";
}
/** primeiro tick em que |c| decaido fica abaixo do limiar da frase (null se ja esta abaixo) */
export function tickSaidaFaixa(tick: number, c: number, cfg: Cfg = CCF): number | null {
  if (Math.abs(c) < cfg.limiarFrase) return null;
  return tick + Math.ceil(cfg.tauConf * Math.log(Math.abs(c) / cfg.limiarFrase));
}

/** contadores de encontros por rival (com o ultimo tick de cada um), a confianca `c` e o tick da ultima luta;
    `historico` guarda cada luta (tick, rival, sinal, novidade, c depois): e o que as frases citam */
export class ConfiancaCombate {
  cfg: Cfg;
  encontros: Record<string, number> = {};
  ultimoTick: Record<string, number> = {};
  c = 0;
  tickC: number | null = null;
  historico: LutaConfianca[] = [];
  constructor(cfg: Cfg = CCF) { this.cfg = cfg; }
  private _encontrosEm(rival: string, tick: number): number {
    if (!(rival in this.encontros)) return 0;
    return this.encontros[rival] * Math.exp(-(tick - this.ultimoTick[rival]) / this.cfg.tauHab);
  }
  /** novidade que uma luta contra `rival` no tick teria (sem registrar) */
  novidadeDe(rival: string, tick: number): number { return novidade(this._encontrosEm(rival, tick), this.cfg.lambda); }
  /** a confianca no tick (decaida desde a ultima luta), sem mudar o estado */
  valor(tick: number): number {
    if (this.tickC === null) return this.c;
    return decairConfianca(this.c, tick - this.tickC, this.cfg.tauConf);
  }
  /** uma luta: novidade pelo contador do rival, confianca decaida e empurrada */
  registrar(tick: number, rival: string, sinal: -1 | 0 | 1, sensibilidade: number): { novidade: number; c: number } {
    if (this.tickC !== null && tick < this.tickC) throw new Error(`luta no tick ${tick} antes da última (${this.tickC})`);
    const mAntes = this._encontrosEm(rival, tick), nov = novidade(mAntes, this.cfg.lambda);
    const dt = this.tickC === null ? 0 : tick - this.tickC;
    this.c = atualizarConfianca(this.c, dt, sinal, nov, sensibilidade, this.cfg);
    this.tickC = tick;
    this.encontros[rival] = mAntes + 1;
    this.ultimoTick[rival] = tick;
    this.historico.push({ tick, rival, sinal, novidade: nov, c: this.c });
    return { novidade: nov, c: this.c };
  }
  /** [inicio, fim, faixa] das faixas brutas ate `tick`, com as iguais juntadas (espelho de _intervalos) */
  private _intervalos(tick: number): [number, number, EstadoConfianca][] {
    const cfg = this.cfg, h = this.historico, brutos: [number, EstadoConfianca][] = [];
    h.forEach((x, i) => {
      const novs = h.slice(Math.max(0, i + 1 - cfg.nTedio), i + 1).map(y => y.novidade);
      const fim = i + 1 < h.length ? h[i + 1].tick : tick, f = faixa(x.c, novs, cfg);
      brutos.push([x.tick, f]);
      if (f === "confiante" || f === "inseguro") {
        const sai = tickSaidaFaixa(x.tick, x.c, cfg);
        if (sai !== null && sai < fim) brutos.push([sai, faixa(0, novs, cfg)]);
      }
    });
    const saida: [number, number, EstadoConfianca][] = [];
    brutos.forEach(([ini, f], k) => {
      const fim = k + 1 < brutos.length ? brutos[k + 1][0] : tick;
      if (fim <= ini) return;
      const u = saida[saida.length - 1];
      if (u && u[2] === f) u[1] = fim; else saida.push([ini, fim, f]);
    });
    return saida;
  }
  /** a frase de estado mostrada no tick, com histerese: {estado, desde, c, lutas (ticks das lutas da causa)} */
  estado(tick: number): VistaConfianca {
    if (this.tickC !== null && tick < this.tickC) throw new Error(`tick ${tick} antes da última luta (${this.tickC})`);
    let mostrada: EstadoConfianca = "neutro", desde: number | null = null;
    for (const [ini, fim, f] of this._intervalos(tick)) {
      if (f !== mostrada && fim - ini >= this.cfg.histerese) { mostrada = f; desde = ini + this.cfg.histerese; }
    }
    return { estado: mostrada, desde, c: this.valor(tick), lutas: this._causa(mostrada) };
  }
  /** ticks das lutas do registro que puseram o pet no estado (da mais recente a mais antiga) */
  private _causa(estado: EstadoConfianca): number[] {
    const h = this.historico;
    if (estado === "entediado") return h.slice(-this.cfg.nTedio).reverse().map(x => x.tick);
    if (estado === "neutro") return [];
    const sinal = estado === "confiante" ? 1 : -1, lutas: number[] = [];
    for (let i = h.length - 1; i >= 0; i--) {
      if (h[i].c * sinal <= 0) break;
      if (h[i].sinal === sinal) lutas.push(h[i].tick);
    }
    return lutas;
  }
  assinatura(): unknown[] { return [this.c, this.tickC, this.encontros, this.ultimoTick, this.historico.length]; }
}
