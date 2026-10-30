/* O laco gravado do G-PAR do laco com o mundo (o MotorMundoCorpoGravado do exportador, do lado do TS) e a leitura dos gabaritos: o
   test/mvp_mundo.test.ts (os gabaritos do MVP) e o test/decisao_na_comida.test.ts (a chave decidirNaComida) usam os dois. Nao muda nada
   da vida: so grava o traco do mundo e o corpo em cada decisao. */
import { readFileSync } from "node:fs";
import { type ConfigMundo } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { type BracoConsequencia } from "../motor/lobos.ts";
import { MotorCorpoMundo, type OcorridoMundo, type OpcoesLacoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo, type PoliticaCorpo } from "../motor/motor_corpo.ts";
import { type PercepcaoMundo } from "../motor/mundo.ts";
import { bracoV11 } from "../motor/pet_v11.ts";
import type { AcaoPet } from "../motor/tipos.ts";

export type Rec = Record<string, unknown>;
export interface Vida {
  nome: string; cerebro: "a_v11" | "instinto"; dono: string; lugar: string; semente: number; dias: number; log: EventoCorpo[]; traco: Rec[];
  resumo: Rec; corpo_fim: Rec; estado_fim: Rec; proximos: Record<string, { random: number[]; randrange16: number[] }>; decisoes: number;
}
export interface Gabarito {
  versao: number; config: { corpo: Rec; braco: string; dias: number; intervalo_decisao_ticks: number; mundo?: Rec }; vidas: Vida[];
}
export const ler = (rel: string): { texto: Buffer; g: Gabarito } => {
  const texto = readFileSync(new URL(rel, import.meta.url));
  return { texto, g: JSON.parse(texto.toString("utf8")) as Gabarito };
};
export const json = (v: unknown): unknown => JSON.parse(JSON.stringify(v));

const percepcao = (p: PercepcaoMundo): Rec => ({ x: p.x, y: p.y, regiao: p.regiao, vistos: p.vistos.map((v) => [...v]), cheiro: p.cheiro,
  direcao_cheiro: p.direcao_cheiro, alvo_pendente: p.alvo_pendente });
const estadoMundo = (e: { fome: number; energia: number; humor: number; sujeira: number }): Rec =>
  ({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira });

/** o MotorMundoCorpoGravado do exportador, do lado do TS: grava o traco do mundo e o corpo em cada decisao; nao muda nada da vida */
export class LacoGravado extends MotorCorpoMundo {
  readonly traco: Rec[] = [];
  private op: Rec | null = null;
  private corpoAgora(): Rec { return { q: { ...this.corpo.q }, receptores: { ...this.corpo.receptores() } }; }

  protected override antesDaDecisao(): PercepcaoMundo {
    const p = super.antesDaDecisao();
    this.op = { op: "decisao", tick: this.estado.tick, fome_antes: this.estado.fome, percepcao: percepcao(p), corpo_antes: this.corpoAgora() };
    return p;
  }

  protected override consequenciaDoMundo(acao: AcaoPet): OcorridoMundo | null {
    const op = this.op!;
    Object.assign(op, { acao, estado: estadoMundo(this.estado), com_gancho: false });
    const ocorrido = super.consequenciaDoMundo(acao);
    const regs = this.mundo.decisoes;
    Object.assign(op, { regra: regs[regs.length - 1].regra, candidatos: this.mundo.ultimosCandidatos, ocorrido,
                        depois: estadoMundo(this.estado), percepcao_depois: percepcao(this.mundo.perceber(this.estado.tick)) });
    return ocorrido;
  }

  protected override consequencia(acao: AcaoPet): OcorridoMundo | null {
    const ocorrido = super.consequencia(acao);
    const op = this.op!;
    this.op = null;
    op.corpo_depois = { ...this.corpoAgora(), estimulos: this.estimulos.map((s) => [...s]) };
    this.traco.push(json(op) as Rec);                     // o retrato da decisao, sem referencias que o motor mude depois
    return ocorrido;
  }

  override comidaDoDono(tipo: string, x: number, y: number): void {
    this.traco.push({ op: "deixar_comida", tick: this.estado.tick, tipo, x, y });
    super.comidaDoDono(tipo, x, y);
  }
}

/** o cerebro da vida: o braco do v11 (as vidas do A) ou as acoes gravadas (a do instinto do mundo, que o TS nao tem) */
export function cerebroDa(vida: Vida): { politica: PoliticaCorpo; regra: () => string | null; braco: BracoConsequencia | null } {
  if (vida.cerebro === "a_v11") {
    const braco = bracoV11();
    return {
      braco, regra: () => braco.cerebro.ultimaRegra,
      politica: {
        agir: (o, rng) => braco.agir(o, rng), observar: (t) => braco.observar(t),
        consequenciaCorpo: (a, oc, d) => braco.consequenciaCorpo(a, oc, d), receberAcaoDono: (a, t) => braco.receberAcaoDono(a, t),
        mudancaNoCorpo: (a, d) => braco.mudancaNoCorpo(a, d),
      },
    };
  }
  const gravadas = vida.traco.filter((o) => o.op === "decisao") as { acao: AcaoPet; regra: string | null }[];
  let k = 0, regra: string | null = null;
  return {
    braco: null, regra: () => regra,
    politica: {
      agir() { const d = gravadas[k++]; regra = d.regra; return d.acao; },
      observar() {}, consequenciaCorpo() {}, receberAcaoDono() {}, mudancaNoCorpo() {},
    },
  };
}

export function viver(vida: Vida, cm: ConfigMundo, opcoes: OpcoesLacoMundo = {}) {
  const c = cerebroDa(vida);
  const m = new LacoGravado(c.politica, vida.semente, CCO_CORPO_V11, estadoNascimentoPy(0),
                            { regra: c.regra, paridade: true, cfgMundo: cm, ...opcoes });
  for (const e of vida.log) m.aplicarEvento(e);
  return { m, braco: c.braco };
}
