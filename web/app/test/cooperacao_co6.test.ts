/* O G-PAR-CO6 (docs/ESPEC_V3_COOPERACAO_CO6.md, secao 4): o peso dos deveres k e a reputacao do motor/cooperacao.ts e a percepcao da CO6 do
   motor/grupo.ts repetem o Python, bit a bit no Node, contra o gabarito de experiments/exportar_gabarito_co6_par.py (co6_python.json.gz):
   - as chamadas sinteticas: o k e a reputacao de cada pet depois de cada tick (o passo, o decaimento e o teto por estagio);
   - as 7 vidas da CO3 rejogadas do registro com o traco do Python e a CO6 ligada: o k de cada presente no fim de cada tick, a reputacao e o
     peso dos deveres de cada percepcao social e o resumo da cooperacao; e o G-SEM-DECISAO-CO6: cada decisao do traco sai igual (a
     percepcao de hoje, os candidatos, o ocorrido, o estado), e o resumo do grupo sem a cooperacao e o da CO6 desligada. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CCOOP, CMU, LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO, type ConfigMundo } from "../motor/constantes.ts";
import {
  CONFIG_COOPERACAO, CONFIG_COOPERACAO_CO6, CONFIG_COOPERACAO_LIGADA, Cooperacao, RegistroGrupo, estagioDaIdade, reproduzirGrupo,
  type AlvoMundo, type CabecalhoGrupo, type ConsumoCoop, type EstadoNoMundo, type EventoGrupo, type PetDoGrupo, type PortaDaDecisao,
  type ResultadoNoGrupo,
} from "../motor/index.ts";

type Rec = Record<string, unknown>;
function lerGz(nome: string): unknown {
  const texto = gunzipSync(readFileSync(new URL(`./gabaritos/${nome}`, import.meta.url))).toString("utf8");
  return JSON.parse(texto.replace(/([:[,])(-?\d{16,})(?=[,\]}])/g, '$1"$2"'));
}
const comoJson = (v: unknown): unknown => JSON.parse(JSON.stringify(v, (_k, x) => (typeof x === "bigint" ? x.toString() : x)));
const inteiro = (v: unknown): number | bigint => (typeof v === "string" ? BigInt(v) : (v as number));

interface OpDecisao {
  op: "decisao"; tick: number; tick_mundo: number; fome_antes: number; percepcao: Rec; social: Rec | null; acao: string; estado: EstadoNoMundo;
  regra: string | null; com_gancho: boolean; candidatos: Rec[] | null; ocorrido: (Rec & { alvo: AlvoMundo | null }) | null;
  depois: EstadoNoMundo; percepcao_depois: Rec; tick_social: Rec | null;
}
type Op = OpDecisao | { op: "deixar_comida" | "deixar_bola"; tick: number };
interface VidaCo3 {
  semente: number; layout: string; cerebros: string[]; tick: number; registro: { cabecalho: Rec; eventos: EventoGrupo[] };
  tracos: Record<string, Op[]>;
}
interface VidaCo6 {
  semente: number; layout: string; cerebros: string[]; k: [number, Record<string, number>][];
  percepcao: Record<string, [number, [string, number][], number][]>; cooperacao: Rec;
}
type Chamada = { f: "decisao"; tick: number; ident: string; maduras: number[]; outros: string[]; fome: number; consumo: ConsumoCoop | null; pos: Record<string, [number, number]> }
  | { f: "fim"; tick: number; disputas: { vencedor: string; perdedor: string; comida: number }[]; contatos: { pets: string[]; tipos: Record<string, string> }[];
      acoes: Record<string, string>; pos: Record<string, [number, number]> }
  | { f: "k"; de: number; ate: number; pos: Record<string, [number, number]>; nasceu: Record<string, number> };
const CO3 = lerGz("cooperacao_python.json.gz") as { vidas: VidaCo3[] };
const G = lerGz("co6_python.json.gz") as {
  vidas: VidaCo6[]; sinteticos: { chamadas: Chamada[]; raios: Record<string, number>; serie: number[][]; resumo: Rec };
};

const configDaVida = (v: VidaCo3): ConfigMundo => ({ ...CMU, layout: v.layout === "afastado" ? LAYOUT_MUNDO_AFASTADO : LAYOUT_MUNDO_PADRAO });

function registroDe(v: VidaCo3): RegistroGrupo {
  const c = v.registro.cabecalho as { versao: number; semente: unknown; ids: string[]; layout: string; pets: Record<string, Rec> };
  const pets = Object.fromEntries(Object.entries(c.pets).map(([i, p]) =>
    [i, { semente: inteiro(p.semente), entrada: p.entrada as number, cerebro: p.cerebro as string, dono: p.dono as string }]));
  return new RegistroGrupo({ versao: c.versao, semente: inteiro(c.semente), ids: c.ids, layout: c.layout, pets } as CabecalhoGrupo, v.registro.eventos);
}

/** o engine e o cerebro de um pet trocados pelo traco do Python (o da CO3); a percepcao da CO6 vai para `co6` */
class PetDoTraco implements PetDoGrupo {
  private k = 0;
  private readonly ops: OpDecisao[];
  readonly co6: [number, [string, number][], number][] = [];
  readonly nome: string;
  private readonly comCo6: boolean;
  constructor(nome: string, traco: Op[], comCo6: boolean) {
    this.nome = nome;
    this.comCo6 = comCo6;
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
    const op = this.ops[this.k]!, onde = `${this.nome}, decisao ${this.k} (tick ${t})`;
    const { mundo, social } = porta.antes(op.fome_antes);
    expect(comoJson(mundo), `percepcao, ${onde}`).toEqual(op.percepcao);
    if (social === null) expect(op.social, `percepcao social, ${onde}`).toBeNull();
    else {
      const { reputacao, peso_dever, ...hoje } = social;
      expect(comoJson(hoje), `percepcao social, ${onde}`).toEqual(op.social);
      if (this.comCo6) this.co6.push([op.tick_mundo, reputacao!, peso_dever!]);
      else expect(reputacao === undefined && peso_dever === undefined, `sem a CO6, nenhum campo novo, ${onde}`).toBe(true);
    }
    const gravado = op.ocorrido?.alvo ?? null;
    return { acao: op.acao, estado: op.estado, regra: op.regra, escolher: op.com_gancho && gravado ? () => ({ ...gravado }) : null };
  }
  depois(t: number, r: ResultadoNoGrupo): void {
    const op = this.ops[this.k++]!, onde = `${this.nome}, decisao ${this.k - 1} (tick ${t})`;
    expect(r.tickMundo, `tick do mundo, ${onde}`).toBe(op.tick_mundo);
    expect(comoJson(r.candidatos), `candidatos, ${onde}`).toEqual(op.candidatos);
    expect(comoJson(r.ocorrido), `ocorrido, ${onde}`).toEqual(op.ocorrido);
    expect(r.estado, `estado depois, ${onde}`).toEqual(op.depois);
    expect(comoJson(r.percepcaoDepois), `percepcao depois, ${onde}`).toEqual(op.percepcao_depois);
    expect(comoJson(r.tickSocial), `tick social, ${onde}`).toEqual(op.tick_social);
  }
}

function rejogar(v: VidaCo3, co6: boolean) {
  const pets = Object.fromEntries(Object.entries(v.tracos).map(([i, tr]) => [i, new PetDoTraco(`${v.semente}/${v.cerebros.join("+")}/${i}`, tr, co6)]));
  const serie: [number, Record<string, number>][] = [];
  const original = Cooperacao.prototype.fimDoTickK;
  Cooperacao.prototype.fimDoTickK = function (this: Cooperacao, tick, posicoes, raios, idades) {
    original.call(this, tick, posicoes, raios, idades);
    serie.push([tick, Object.fromEntries(Object.keys(posicoes).sort().map(i => [i, this.pesoDever(i)]))]);
  };
  try {
    const g = reproduzirGrupo(registroDe(v), Object.fromEntries(Object.keys(pets).map(i => [i, () => ({ pet: pets[i]! })])), configDaVida(v),
                              undefined, co6 ? CONFIG_COOPERACAO_CO6 : CONFIG_COOPERACAO_LIGADA);
    for (const p of Object.values(pets)) expect(p.consumidas, p.nome).toBe(p.total);
    return { g, pets, serie };
  } finally {
    Cooperacao.prototype.fimDoTickK = original;
  }
}

describe("a config e o estagio", () => {
  test("o CCOOP da CO6 e a ConfigCooperacao e a ConfigExpressao do Python", () => {
    const py = JSON.parse(readFileSync(new URL("./gabaritos/constantes_python.json", import.meta.url), "utf8")) as Record<string, Rec>;
    const cc = py.ConfigCooperacao!, ce = py.ConfigExpressao!;
    expect([CCOOP.kPasso, CCOOP.kTetoBebe, CCOOP.kTetoCrianca, CCOOP.kTetoAdolescente, CCOOP.kTetoAdulto])
      .toEqual([cc.k_passo, cc.k_teto_bebe, cc.k_teto_crianca, cc.k_teto_adolescente, cc.k_teto_adulto]);
    expect([CCOOP.diasFimBebe, CCOOP.diasFimCrianca, CCOOP.diasFimAdolescente]).toEqual([ce.dias_fim_bebe, ce.dias_fim_crianca, ce.dias_fim_adolescente]);
    expect(cc.co6).toBe(false);
    expect(CONFIG_COOPERACAO.co6).toBe(false);
    expect(CONFIG_COOPERACAO_LIGADA.co6).toBe(false);
    expect(() => new Cooperacao({ ...CONFIG_COOPERACAO, co6: true })).toThrow(/ligada/);
    expect(() => new Cooperacao({ ...CONFIG_COOPERACAO_CO6, kTetoCrianca: 600 })).toThrow(/kTeto/);
    expect(() => new Cooperacao(CONFIG_COOPERACAO_LIGADA).pesoDever("A")).toThrow(/co6/);
    expect([0, 1439, 1440, 4320, 10080].map(i => estagioDaIdade(i, CONFIG_COOPERACAO_CO6))).toEqual(["bebe", "bebe", "crianca", "adolescente", "adulto"]);
  });
});

describe("o G-PAR-CO6", () => {
  test("as chamadas sinteticas: o passo, o decaimento e o teto por estagio, tick a tick", () => {
    const s = G.sinteticos, c = new Cooperacao(CONFIG_COOPERACAO_CO6), serie: number[][] = [];
    for (const ch of s.chamadas) {
      if (ch.f === "decisao") c.decisao(ch.tick, ch.ident, ch.maduras, ch.outros, ch.fome, ch.consumo, ch.pos, s.raios);
      else if (ch.f === "fim") c.fimDoTick(ch.tick, ch.disputas, ch.contatos, ch.acoes, ch.pos, s.raios);
      else for (let t = ch.de; t < ch.ate; t++) {
        c.fimDoTickK(t, ch.pos, s.raios, Object.fromEntries(Object.entries(ch.nasceu).map(([i, n]) => [i, t - n])));
        serie.push([t, c.pesoDever("A"), c.pesoDever("B"), c.reputacao("A", "B", t), c.reputacao("B", "A", t)]);
      }
    }
    expect(serie).toEqual(s.serie);
    expect(comoJson(c.resumo(["A", "B"], 1900))).toEqual(s.resumo);
    expect(new Set(s.serie.map(x => x[1]))).toContain(256);         // o teto da crianca foi tocado
  });

  test("o gabarito tem as 7 vidas da CO3, na mesma ordem", () => {
    expect(G.vidas.map(v => [v.semente, v.cerebros])).toEqual(CO3.vidas.map(v => [v.semente, v.cerebros]));
  });

  for (const [n, v] of CO3.vidas.entries()) {
    test(`vida ${v.semente} (${v.cerebros.join(" + ")}): o k tick a tick, a percepcao da CO6 e o G-SEM-DECISAO-CO6`, () => {
      const gv = G.vidas[n]!;
      const ligada = rejogar(v, true), desligada = rejogar(v, false);
      expect(ligada.serie).toEqual(gv.k);
      for (const [i, p] of Object.entries(ligada.pets)) expect(p.co6, `percepcao da CO6 de ${i}`).toEqual(gv.percepcao[i]);
      expect(comoJson(ligada.g.coop!.resumo(ligada.g.idsPresentes(), ligada.g.tick))).toEqual(gv.cooperacao);
      expect(desligada.serie).toEqual([]);
      const { cooperacao: _a, ...semCoop } = ligada.g.resumo();
      const { cooperacao: _b, ...semCoopDesligada } = desligada.g.resumo();
      expect(comoJson(semCoop)).toEqual(comoJson(semCoopDesligada));
    });
  }
});
