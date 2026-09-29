/* Vinculo (espelho de digilab/vinculo.py) e obediencia (espelho de obediencia.py).
   Vinculo: media movel em [0, 1] de atendimento (pedido atendido rapido), coerencia (mesmo sinal de
   feedback para a mesma acao) e vontades respeitadas. Guarda o ordinal da acao do dono que por ultimo o
   derrubou. Obediencia: so acoes de cuidado; feedback sempre chega. */
import { CME, COB, CVI } from "./constantes.ts";
import type { AcaoDono, AcaoPet, Desejo, Observacao } from "./tipos.ts";

const ATENDE_VONTADE: Partial<Record<string, AcaoDono>> = { comer: "alimentar", brincar: "brincar", chamar_atencao: "acariciar" };
/* petisco, banheiro e tratar (pets v4) atendem como cuidado, como no Python (CUIDADOS_QUE_ATENDEM) */
const CUIDADOS: readonly AcaoDono[] = ["alimentar", "limpar", "brincar", "acariciar", "petisco", "levar_ao_banheiro", "tratar_lesao"];

export class Vinculo {
  valor = CVI.inicial;
  pedidos: number[] = [];
  feedbacks: Record<string, [number, number][]> = {};
  vontades: [number, AcaoDono][] = [];
  n = 0;
  ultRefBaixa: number | null = null;
  teto = 1;
  ajustar(delta: number, ref: number | null): void { const antes = this.valor; this.valor = Math.min(this.teto, Math.max(0, this.valor + delta)); if (this.valor < antes) this.ultRefBaixa = ref; this.n++; }
  limitar(teto: number): void { this.teto = teto; this.valor = Math.min(this.valor, teto); }
  _amostra(amostra: number, peso: number, ref: number | null): void {
    const antes = this.valor;
    this.valor = Math.min(this.teto, Math.max(0, this.valor + CVI.alfa * peso * (amostra - this.valor)));
    if (this.valor < antes) this.ultRefBaixa = ref;
    this.n++;
  }
  expirar(tick: number): void {
    const vivos: number[] = [];
    for (const t of this.pedidos) { if (tick - t > CVI.janelaLat) this._amostra(0, CVI.pesoAtend, null); else vivos.push(t); }
    this.pedidos = vivos;
    const vivas: [number, AcaoDono][] = [];
    for (const v of this.vontades) { if (tick - v[0] > CVI.janelaDesejo) this._amostra(0, CVI.pesoDesejo, null); else vivas.push(v); }
    this.vontades = vivas;
  }
  decisao(obs: Observacao, acao: AcaoPet, tick: number, desejo: Desejo | null): void {
    this.expirar(tick);
    if (acao === "chamar_atencao" && Math.min(obs.v[0], obs.v[1]) < CME.limiarPedido) this.pedidos.push(tick);
    if (desejo && desejo.tipo === "vontade" && ATENDE_VONTADE[desejo.alvo]) this.vontades.push([tick, ATENDE_VONTADE[desejo.alvo]!]);
  }
  acaoDono(a: AcaoDono, tick: number, acaoPet: AcaoPet | null, ref: number | null): void {
    this.expirar(tick);
    if (CUIDADOS.includes(a) && this.pedidos.length) {
      for (const t of this.pedidos) this._amostra(1 - (tick - t) / CVI.janelaLat, CVI.pesoAtend, ref);
      this.pedidos = [];
    }
    if ((a === "elogiar" || a === "repreender") && acaoPet) {
      const sinal = a === "elogiar" ? 1 : -1, hist = (this.feedbacks[acaoPet] || []).filter(([t]) => tick - t <= CVI.janelaCoer);
      if (hist.length) this._amostra(hist.filter(([, s]) => s === sinal).length / hist.length, CVI.pesoCoer, ref);
      this.feedbacks[acaoPet] = [...hist, [tick, sinal]];
    }
    const at = this.vontades.filter(v => v[1] === a);
    if (at.length) { this.vontades = this.vontades.filter(v => v[1] !== a); for (const _ of at) this._amostra(1, CVI.pesoDesejo, ref); }
  }
  assinatura(): unknown[] { return [this.valor, this.pedidos, this.feedbacks, this.vontades, this.n, this.ultRefBaixa, this.teto]; }
}

const ATENDE_NECESSIDADE: Partial<Record<string, string>> = { alimentar: "fome", limpar: "higiene", brincar: "humor", acariciar: "humor" };
/** conflito entre o pedido do dono e a necessidade mais urgente do pet: [intensidade, necessidade] */
export function conflitoDono(v: number[], a: string): [number, string | null] {
  const urg = ([["fome", 0], ["higiene", 1], ["energia", 2], ["humor", 3]] as const).map(([n, i]) => [v[i], n] as const).filter(([x]) => x < COB.limiarConflito)
    .sort((x, y) => x[0] - y[0] || (x[1] < y[1] ? -1 : 1));
  if (!urg.length || ATENDE_NECESSIDADE[a] === urg[0][1]) return [0, null];
  return [(COB.limiarConflito - urg[0][0]) / COB.limiarConflito, urg[0][1]];
}
/** p = logistica(b0 + b_v vinculo - b_t teimosia - b_c conflito) e a contribuicao de cada termo */
export function termosObediencia(vinculo: number, teimosia: number, conf: number, nec: string | null): [number, Record<string, number>] {
  const z = COB.b0 + COB.bVinculo * vinculo - COB.bTeimosia * teimosia - COB.bConflito * conf;
  const contrib: Record<string, number> = { vinculo_baixo: COB.bVinculo * (vinculo - CVI.inicial), teimosia: -COB.bTeimosia * teimosia };
  if (nec) contrib["necessidade_" + nec] = -COB.bConflito * conf;
  return [1 / (1 + Math.exp(-z)), contrib];
}
