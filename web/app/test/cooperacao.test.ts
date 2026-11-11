/* O G-PAR-COOP e o G-SEM-DECISAO no TS (docs/TAREFA_V3_COOPERACAO.md, etapa CO3): motor/cooperacao.ts repete digilab/cooperacao.py, bit a bit
   no Node, contra o gabarito de experiments/exportar_gabarito_cooperacao.py (cooperacao_python.json.gz):
   - as chamadas sinteticas (a disputa "anti", a podre, o encostar sem testemunha, a repeticao e a janela nova) dao o mesmo resumo;
   - as 7 vidas de dois pets (as 5 da CO1 e 2 com o cerebro aleatorio, que segue o outro) rejogadas do registro do grupo, com o engine e o
     cerebro trocados pelo traco gravado no Python, dao os mesmos atos, a mesma pontuacao e a mesma reputacao;
   - o G-SEM-DECISAO: com a medida ligada, cada decisao do traco sai igual (a percepcao, os candidatos, o ocorrido, o estado), e o resumo do
     grupo, sem a chave `cooperacao`, e o mesmo da medida desligada. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CCOOP, CMU, LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO, type ConfigMundo } from "../motor/constantes.ts";
import {
  CONFIG_COOPERACAO, CONFIG_COOPERACAO_LIGADA, ContaCoop, Cooperacao, RegistroGrupo, decair, ganhoDaRefeicao, reproduzirGrupo,
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
interface Vida {
  semente: number; layout: string; cerebros: string[]; tick: number; registro: { cabecalho: Rec; eventos: EventoGrupo[] };
  tracos: Record<string, Op[]>; ordens: unknown[]; contatos: unknown[]; disputas: unknown[]; cooperacao: Rec;
}
type Chamada = { f: "decisao"; tick: number; ident: string; maduras: number[]; outros: string[]; fome: number; consumo: ConsumoCoop | null; pos: Record<string, [number, number]> }
  | { f: "fim"; tick: number; disputas: { vencedor: string; perdedor: string; comida: number }[]; contatos: { pets: string[]; tipos: Record<string, string> }[];
      acoes: Record<string, string>; pos: Record<string, [number, number]> };
const G = lerGz("cooperacao_python.json.gz") as { vidas: Vida[]; sinteticos: { chamadas: Chamada[]; raios: Record<string, number>; resumo: Rec } };

const configDaVida = (v: Vida): ConfigMundo => ({ ...CMU, layout: v.layout === "afastado" ? LAYOUT_MUNDO_AFASTADO : LAYOUT_MUNDO_PADRAO });

function registroDe(v: Vida): RegistroGrupo {
  const c = v.registro.cabecalho as { versao: number; semente: unknown; ids: string[]; layout: string; pets: Record<string, Rec> };
  const pets = Object.fromEntries(Object.entries(c.pets).map(([i, p]) =>
    [i, { semente: inteiro(p.semente), entrada: p.entrada as number, cerebro: p.cerebro as string, dono: p.dono as string }]));
  return new RegistroGrupo({ versao: c.versao, semente: inteiro(c.semente), ids: c.ids, layout: c.layout, pets } as CabecalhoGrupo, v.registro.eventos);
}

/** o engine e o cerebro de um pet trocados pelo traco do Python; com o gancho do alvo (o cerebro aleatorio), devolve o alvo gravado */
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
    const gravado = op.ocorrido?.alvo ?? null;
    return { acao: op.acao, estado: op.estado, regra: op.regra, escolher: op.com_gancho && gravado ? () => ({ ...gravado }) : null };
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

function rejogar(v: Vida, ligada: boolean) {
  const pets = Object.fromEntries(Object.entries(v.tracos).map(([i, tr]) => [i, new PetDoTraco(`${v.semente}/${v.cerebros.join("+")}/${i}`, tr)]));
  const g = reproduzirGrupo(registroDe(v), Object.fromEntries(Object.keys(pets).map(i => [i, () => ({ pet: pets[i] })])), configDaVida(v),
                            undefined, ligada ? CONFIG_COOPERACAO_LIGADA : CONFIG_COOPERACAO);
  for (const p of Object.values(pets)) expect(p.consumidas, p.nome).toBe(p.total);
  return g;
}

describe("a config e a conta", () => {
  test("o CCOOP e a ConfigCooperacao do Python (o constantes.test.mjs confere tambem)", () => {
    const py = (JSON.parse(readFileSync(new URL("./gabaritos/constantes_python.json", import.meta.url), "utf8")) as Record<string, Rec>).ConfigCooperacao;
    expect([CCOOP.escala, CCOOP.pisoFome, CCOOP.meiaVida, CCOOP.kMeiaVida, CCOOP.janelaNovidade])
      .toEqual([py.escala, py.piso_fome, py.meia_vida_pontuacao, py.k_meia_vida_pontuacao, py.janela_novidade]);
    expect(py.ligada).toBe(false);
    expect(CONFIG_COOPERACAO.ligada).toBe(false);
  });

  test("a conta: a repeticao, a janela nova, a meia-vida com o sinal e o que ela recusa", () => {
    expect(decair(-1000, 10, 32)).toBe(-decair(1000, 10, 32));
    expect(() => decair(1, -1, 32)).toThrow();
    const c = new ContaCoop(CONFIG_COOPERACAO_LIGADA);
    expect(c.somar(0, "contencao", "B", 1000).slice(1)).toEqual([1000, 1000]);
    expect(c.somar(10, "contencao", "B", 1000).slice(0, 2)).toEqual([1, 500]);
    expect(c.somar(1440, "contencao", "B", 1000).slice(0, 2)).toEqual([0, 1000]);
    expect(ganhoDaRefeicao({ id: 1, fome_antes: .5, fome_depois: .5, humor_antes: .5, humor_depois: .2 }, 1024)).toBe(0);
    expect(() => new Cooperacao(CONFIG_COOPERACAO)).toThrow(/ligada/);
    const k = new Cooperacao(CONFIG_COOPERACAO_LIGADA);
    expect(() => k.fimDoTick(5, [{ vencedor: "A", perdedor: "B", comida: 3 }], [], { A: "comer", B: "comer" }, { A: [0, 0], B: [1, 0] }, { A: 96, B: 96 }))
      .toThrow(/sem a refeicao/);
  });
});

describe("o G-PAR-COOP", () => {
  test("as chamadas sinteticas: a disputa anti, a podre, o encostar sem testemunha, a repeticao e a janela nova", () => {
    const s = G.sinteticos, c = new Cooperacao(CONFIG_COOPERACAO_LIGADA);
    for (const ch of s.chamadas) {
      if (ch.f === "decisao") c.decisao(ch.tick, ch.ident, ch.maduras, ch.outros, ch.fome, ch.consumo, ch.pos, s.raios);
      else c.fimDoTick(ch.tick, ch.disputas, ch.contatos, ch.acoes, ch.pos, s.raios);
    }
    expect(comoJson(c.resumo(["A", "B"], 2 * 1440 + 100))).toEqual(s.resumo);
    const atos = (s.resumo.atos as { sinal: number }[]);
    expect(new Set(atos.map(a => a.sinal))).toEqual(new Set([-1, 0, 1]));
  });

  test("o gabarito tem as 7 vidas, com os tres atos", () => {
    expect(G.vidas.length).toBe(7);
    const atos = G.vidas.flatMap(v => (v.cooperacao.atos as { ato: string }[]).map(a => a.ato));
    expect(new Set(atos)).toEqual(new Set(["disputa", "contencao", "encostar"]));
    expect(G.vidas.some(v => v.cerebros.includes("aleatorio"))).toBe(true);
  });

  for (const v of G.vidas) {
    test(`vida ${v.semente} (${v.cerebros.join(" + ")}): os atos, a pontuacao e a reputacao; e o G-SEM-DECISAO`, () => {
      const ligada = rejogar(v, true), desligada = rejogar(v, false);
      expect(comoJson(ligada.coop!.resumo(ligada.idsPresentes(), ligada.tick))).toEqual(v.cooperacao);
      expect(ligada.tick).toBe(v.tick);
      expect(comoJson(ligada.contatos)).toEqual(v.contatos);
      expect(comoJson(ligada.disputas)).toEqual(v.disputas);
      expect(desligada.coop).toBeNull();
      const { cooperacao: _c, ...semCoop } = ligada.resumo();
      expect(comoJson(semCoop)).toEqual(comoJson(desligada.resumo()));
      expect("cooperacao" in desligada.resumo()).toBe(false);
    });
  }
});
