/* O G-PAR-GRUPO na ilha com agua (docs/TAREFA_V3_COOPERACAO.md, etapa CO4a): os pets do jogo nascem no `mvp_agua`, e no grupo cada um anda
   pelo controlador do contrato (CONFIG_CONTRATO_AGUA), contra a agua do mundo partilhado. O motor/grupo.ts repete o digilab/grupo.py nesse
   mundo, bit a bit no Node, nas 3 vidas de experiments/exportar_gabarito_grupo_agua.py (grupo_agua_python.json.gz), rejogadas do registro com
   o engine e o cerebro trocados pelo traco: em cada decisao, a percepcao, a social, os candidatos, o ocorrido (com o registro do contrato), o
   estado e o `_tick_social`; no fim, as vezes, os contatos, as disputas, o mundo e o fisico e o social de cada pet. No grupo, o cone e as
   paredes do contrato seguem recusados. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP_AGUA } from "../motor/constantes.ts";
import { CONFIG_CONTRATO_AGUA } from "../motor/contrato.ts";
import {
  Grupo, RegistroGrupo, reproduzirGrupo, type CabecalhoGrupo, type EstadoNoMundo, type EventoGrupo, type PetDoGrupo, type PortaDaDecisao,
  type ResultadoNoGrupo,
} from "../motor/index.ts";

type Rec = Record<string, unknown>;
function lerGz(nome: string): unknown {
  const texto = gunzipSync(readFileSync(new URL(`./gabaritos/${nome}`, import.meta.url))).toString("utf8");
  return JSON.parse(texto.replace(/([:[,])(-?\d{16,})(?=[,\]}])/g, '$1"$2"'));
}
const comoJson = (v: unknown): unknown => JSON.parse(JSON.stringify(v, (_k, x) => (typeof x === "bigint" ? x.toString() : x)));
const inteiro = (v: unknown): number | bigint => (typeof v === "string" ? BigInt(v) : (v as number));
const semRngs = (o: Rec): Rec => { const { rngs: _r, ...resto } = o; return resto; };

interface OpDecisao {
  op: "decisao"; tick: number; tick_mundo: number; fome_antes: number; percepcao: Rec; social: Rec | null; acao: string; estado: EstadoNoMundo;
  regra: string | null; com_gancho: boolean; candidatos: Rec[] | null; ocorrido: Rec | null; depois: EstadoNoMundo; percepcao_depois: Rec;
  tick_social: Rec | null;
}
type Op = OpDecisao | { op: "deixar_comida" | "deixar_bola"; tick: number };
interface Vida {
  semente: number; corpo: string; cerebros: string[]; registro: { cabecalho: Rec; eventos: EventoGrupo[] }; tracos: Record<string, Op[]>;
  resumo: { tick: number; mundo: Rec; ordens: unknown[]; contatos: unknown[]; disputas: unknown[];
            pets: Record<string, { fisico: Rec; social: Rec; entrada: number; log: string }> };
}
const G = lerGz("grupo_agua_python.json.gz") as { layout: string; vidas: Vida[] };

class PetDoTraco implements PetDoGrupo {
  private k = 0;
  private readonly ops: OpDecisao[];
  readonly nome: string;
  constructor(nome: string, traco: Op[]) {
    this.nome = nome;
    this.ops = traco.filter((o): o is OpDecisao => o.op === "decisao");
  }
  get consumidas(): number { return this.k; }
  get total(): number { return this.ops.length; }
  decideEm(t: number): boolean {
    const op = this.ops[this.k];
    if (op !== undefined && op.tick < t) throw new Error(`${this.nome}: a decisao do tick ${op.tick} ficou para tras (tick ${t})`);
    return op !== undefined && op.tick === t;
  }
  decidir(t: number, porta: PortaDaDecisao) {
    const op = this.ops[this.k], onde = `${this.nome}, decisao ${this.k} (tick ${t})`;
    const { mundo, social } = porta.antes(op.fome_antes);
    expect(comoJson(mundo), `percepcao, ${onde}`).toEqual(op.percepcao);
    expect(comoJson(social), `percepcao social, ${onde}`).toEqual(op.social);
    expect(op.com_gancho, onde).toBe(false);
    return { acao: op.acao, estado: op.estado, regra: op.regra };
  }
  depois(t: number, r: ResultadoNoGrupo): void {
    const op = this.ops[this.k++], onde = `${this.nome}, decisao ${this.k - 1} (tick ${t})`;
    expect(r.tickMundo, `tick do mundo, ${onde}`).toBe(op.tick_mundo);
    expect(comoJson(r.candidatos), `candidatos, ${onde}`).toEqual(op.candidatos);
    expect(comoJson(r.ocorrido), `ocorrido, ${onde}`).toEqual(op.ocorrido);
    expect(r.estado, `estado depois, ${onde}`).toEqual(op.depois);
    expect(comoJson(r.percepcaoDepois), `percepcao depois, ${onde}`).toEqual(op.percepcao_depois);
    expect(comoJson(r.tickSocial), `tick social, ${onde}`).toEqual(op.tick_social);
  }
}

function registroDe(v: Vida): RegistroGrupo {
  const c = v.registro.cabecalho as { versao: number; semente: unknown; ids: string[]; layout: string; pets: Record<string, Rec> };
  const pets = Object.fromEntries(Object.entries(c.pets).map(([i, p]) =>
    [i, { semente: inteiro(p.semente), entrada: p.entrada as number, cerebro: p.cerebro as string, dono: p.dono as string }]));
  return new RegistroGrupo({ versao: c.versao, semente: inteiro(c.semente), ids: c.ids, layout: c.layout, pets } as CabecalhoGrupo, v.registro.eventos);
}

describe("o G-PAR-GRUPO na ilha com agua", () => {
  test("o gabarito tem as 3 vidas no mvp_agua, com o controlador andando", () => {
    expect(G.layout).toBe("mvp_agua");
    expect(G.layout).toBe(CMU_MVP_AGUA.layout.nome);
    expect(G.vidas.length).toBe(3);
    const comContrato = G.vidas.flatMap(v => Object.values(v.tracos).flat())
      .filter(o => o.op === "decisao" && (o as OpDecisao).ocorrido !== null && "contrato" in (o as OpDecisao).ocorrido!).length;
    expect(comContrato).toBeGreaterThan(200);
  });

  for (const v of G.vidas) {
    test(`vida ${v.semente} (${v.cerebros.join(" + ")}, corpo ${v.corpo}): decisao a decisao e o resumo`, () => {
      const pets = Object.fromEntries(Object.entries(v.tracos).map(([i, tr]) => [i, new PetDoTraco(`${v.semente}/${i}`, tr)]));
      const registro = registroDe(v);
      const g = reproduzirGrupo(registro, Object.fromEntries(Object.keys(pets).map(i => [i, () => ({ pet: pets[i], opcoes: { contrato: CONFIG_CONTRATO_AGUA } })])),
                                CMU_MVP_AGUA);
      for (const p of Object.values(pets)) expect(p.consumidas, p.nome).toBe(p.total);
      const r = v.resumo;
      expect(g.tick).toBe(r.tick);
      expect(comoJson(g.ordens)).toEqual(r.ordens);
      expect(comoJson(g.contatos)).toEqual(r.contatos);
      expect(comoJson(g.disputas)).toEqual(r.disputas);
      expect(comoJson(g.comum.resumo())).toEqual(semRngs(r.mundo));
      for (const [i, pr] of Object.entries(r.pets)) {
        const m = g.mundoDe(i);
        expect(comoJson(m.resumo()), `fisico de ${i}`).toEqual(semRngs(pr.fisico));
        expect(comoJson(m.resumoSocial()), `social de ${i}`).toEqual(pr.social);
        expect(g.registro.projecao(i)).toEqual(pr.log.split("\n").filter(l => l.trim()).map(l => JSON.parse(l)));
      }
      expect(g.registro.paraJsonl()).toBe(registro.paraJsonl());
    });
  }

  test("no grupo, o cone e as paredes do contrato seguem recusados", () => {
    for (const contrato of [{ ...CONFIG_CONTRATO_AGUA, sensores: true }, { ...CONFIG_CONTRATO_AGUA, paredes: true }]) {
      const g = new Grupo(CMU_MVP_AGUA, 101);
      const nada: PetDoGrupo = { decideEm: () => false, decidir: () => { throw new Error("nao decide"); } };
      expect(() => g.entrar("A", nada, "x", "y", { contrato })).toThrow(/so o controlador/);
    }
  });
});
