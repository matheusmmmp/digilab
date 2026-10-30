/* Vinculo (espelho de digilab/vinculo.py). A obediencia dos pets v2-v10 (espelho de obediencia.py) saiu com o descarte 6 (COMBATE-TR,
   etapa R2b; D-9).
   Vinculo: media movel em [0, 1] de atendimento (pedido atendido rapido), coerencia (mesmo sinal de
   feedback para a mesma acao) e vontades respeitadas. Guarda o ordinal da acao do dono que por ultimo o
   derrubou. Obediencia: so acoes de cuidado; feedback sempre chega.
   Variante B (pets v10, `porSituacao`; espelho de ConfigVinculoSituacao ligada; docs/PLANO_ANALISE_V2_VINCULO.md): o pedido nao
   abre (o atendimento sai) e a coerencia agrupa o historico por (acao do pet, situacao do pet), com a situacao lida da observacao
   com que o pet decidiu a acao atual. Desejo, ajustes, pausa e teto iguais. Paridade com o Python: test/vinculo.test.ts. */
import { CME, CVB, CVI, TPD } from "./constantes.ts";
import { eNoite } from "./estado.ts";
import type { AcaoDono, AcaoPet, Desejo, Observacao } from "./tipos.ts";

const ATENDE_VONTADE: Partial<Record<string, AcaoDono>> = { comer: "alimentar", brincar: "brincar", chamar_atencao: "acariciar" };
/* petisco, banheiro e tratar (pets v4) atendem como cuidado, como no Python (CUIDADOS_QUE_ATENDEM) */
const CUIDADOS: readonly AcaoDono[] = ["alimentar", "limpar", "brincar", "acariciar", "petisco", "levar_ao_banheiro", "tratar_lesao"];

/** variante B: tres bits da situacao do pet (necessidade baixa, cansado, noite), a mesma conta de vinculo.situacao_de */
export function situacaoDe(v: number[]): string {
  const bits = [Math.min(v[0], v[1]) < CVB.limNec, v[2] < CVB.limEnergia, eNoite(Math.round(v[7] * TPD))];
  return bits.map(b => b ? "1" : "0").join("");
}

export class Vinculo {
  valor = CVI.inicial;
  pedidos: number[] = [];
  feedbacks: Record<string, [number, number][]> = {};
  vontades: [number, AcaoDono][] = [];
  n = 0;
  ultRefBaixa: number | null = null;
  teto = 1;
  /** variante B: a situacao em que o pet decidiu a acao atual (chave da coerencia junto com a acao) */
  situacao: string | null = null;
  readonly porSituacao: boolean;
  constructor(porSituacao = false) { this.porSituacao = porSituacao; }
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
    if (this.porSituacao) this.situacao = situacaoDe(obs.v);
    else if (acao === "chamar_atencao" && Math.min(obs.v[0], obs.v[1]) < CME.limiarPedido) this.pedidos.push(tick);
    if (desejo && desejo.tipo === "vontade" && ATENDE_VONTADE[desejo.alvo]) this.vontades.push([tick, ATENDE_VONTADE[desejo.alvo]!]);
  }
  acaoDono(a: AcaoDono, tick: number, acaoPet: AcaoPet | null, ref: number | null): void {
    this.expirar(tick);
    if (CUIDADOS.includes(a) && this.pedidos.length) {
      for (const t of this.pedidos) this._amostra(1 - (tick - t) / CVI.janelaLat, CVI.pesoAtend, ref);
      this.pedidos = [];
    }
    if ((a === "elogiar" || a === "repreender") && acaoPet) {
      const chave = this.porSituacao ? `${acaoPet}|${this.situacao}` : acaoPet;   /* B: por (acao, situacao em que o pet a decidiu) */
      const sinal = a === "elogiar" ? 1 : -1, hist = (this.feedbacks[chave] || []).filter(([t]) => tick - t <= CVI.janelaCoer);
      if (hist.length) this._amostra(hist.filter(([, s]) => s === sinal).length / hist.length, CVI.pesoCoer, ref);
      this.feedbacks[chave] = [...hist, [tick, sinal]];
    }
    const at = this.vontades.filter(v => v[1] === a);
    if (at.length) { this.vontades = this.vontades.filter(v => v[1] !== a); for (const _ of at) this._amostra(1, CVI.pesoDesejo, ref); }
  }
  assinatura(): unknown[] {
    const base = [this.valor, this.pedidos, this.feedbacks, this.vontades, this.n, this.ultRefBaixa, this.teto];
    return this.porSituacao ? [...base, this.situacao] : base;    /* v1-v9: a assinatura de sempre */
  }
}
