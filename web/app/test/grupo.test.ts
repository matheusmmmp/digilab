/* O G-PAR-GRUPO (docs/TAREFA_V3_COOPERACAO.md, etapa CO2c): o motor/grupo.ts repete o digilab/grupo.py, bit a bit no Node.
   - a ConfigGrupo do TS e a do digilab/config.py;
   - a vez sorteada (DP-2): os 8 casos do gabarito da CO1 (grupo_python.json.gz, `ordem`), 40 sorteios cada;
   - as 5 vidas de dois pets da CO1, rejogadas do registro do grupo (reproduzirGrupo), com o engine, o corpo e o cerebro de cada pet
     trocados pelo traco da CO2a (grupo_traco_python.json.gz): em cada decisao, a percepcao do mundo e a social, os candidatos, o ocorrido,
     o estado depois, a percepcao depois e o `_tick_social`; no fim, as vezes sorteadas, os contatos, as disputas, o mundo partilhado, o
     fisico e o social de cada pet, o relogio e a projecao de cada pet (o log de hoje dele). So as rngs ficam fora (o getstate do Python);
     os sorteios delas sao conferidos pelo que sai de cada decisao;
   - o replay falha alto: evento desconhecido, fora do tick, de pet que nao entrou, e o registro refeito diferente do lido. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU, LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO, type ConfigMundo } from "../motor/constantes.ts";
import {
  CONFIG_GRUPO_LIGADA, Grupo, RandomPy, RegistroDivergente, RegistroGrupo, derivarSemente, jsonPython, reproduzirGrupo,
  type CabecalhoGrupo, type EstadoNoMundo, type EventoGrupo, type PetDoGrupo, type PortaDaDecisao, type ResultadoNoGrupo,
} from "../motor/index.ts";

type Rec = Record<string, unknown>;

/** o JSON do Python: os inteiros grandes (as sementes de 64 bits) chegam como texto, para virar bigint sem perder digito */
function lerGz(nome: string): unknown {
  const texto = gunzipSync(readFileSync(new URL(`./gabaritos/${nome}`, import.meta.url))).toString("utf8");
  return JSON.parse(texto.replace(/([:[,])(-?\d{16,})(?=[,\]}])/g, '$1"$2"'));
}
const comoJson = (v: unknown): unknown => JSON.parse(JSON.stringify(v, (_k, x) => (typeof x === "bigint" ? x.toString() : x)));
const inteiro = (v: unknown): number | bigint => (typeof v === "string" ? BigInt(v) : (v as number));

interface OpDecisao {
  op: "decisao"; tick: number; tick_mundo: number; fome_antes: number; percepcao: Rec; social: Rec | null; acao: string;
  estado: EstadoNoMundo; regra: string | null; com_gancho: boolean; candidatos: Rec[] | null; ocorrido: Rec | null; depois: EstadoNoMundo;
  percepcao_depois: Rec; tick_social: Rec | null;
}
type Op = OpDecisao | { op: "deixar_comida"; tick: number; tipo: string; x: number; y: number } | { op: "deixar_bola"; tick: number; x: number; y: number };
interface VidaGrupo {
  semente: number; layout: string; corpo: string; dias: number; entrada_b_dias: number; n_contatos: number; n_disputas: number; n_ordens: number;
  registro: { cabecalho: Rec; eventos: EventoGrupo[] };
  resumo: { tick: number; mundo: Rec; ordens: unknown[]; contatos: unknown[]; disputas: unknown[]; pets: Record<string, { fisico: Rec; social: Rec; entrada: number; log: string }> };
}
const G = lerGz("grupo_python.json.gz") as { ordem: { semente: unknown; ids: string[]; semente_fluxo: string; ordens: string[][] }[]; vidas: VidaGrupo[] };
const T = lerGz("grupo_traco_python.json.gz") as { vidas: { semente: number; tracos: Record<string, Op[]>; n_decisoes: Record<string, number> }[] };

const configDaVida = (v: VidaGrupo): ConfigMundo => (v.layout === "afastado" ? { ...CMU, layout: LAYOUT_MUNDO_AFASTADO } : { ...CMU, layout: LAYOUT_MUNDO_PADRAO });

function registroDe(v: VidaGrupo): RegistroGrupo {
  const c = v.registro.cabecalho as { versao: number; semente: unknown; ids: string[]; layout: string; pets: Record<string, Rec> };
  const pets = Object.fromEntries(Object.entries(c.pets).map(([i, p]) =>
    [i, { semente: inteiro(p.semente), entrada: p.entrada as number, cerebro: p.cerebro as string, dono: p.dono as string }]));
  const cab: CabecalhoGrupo = { versao: c.versao, semente: inteiro(c.semente), ids: c.ids, layout: c.layout, pets };
  return new RegistroGrupo(cab, v.registro.eventos);
}

/** o engine, o corpo e o cerebro de um pet trocados pelo traco gravado no Python: decide quando o Python decidiu, com a acao e o estado
    dele, e confere tudo o que o grupo e o mundo em TS dao contra o que o Python deu */
class PetDoTraco implements PetDoGrupo {
  private k = 0;
  private readonly ops: OpDecisao[];
  readonly deixadas: Op[];
  readonly nome: string;
  constructor(nome: string, traco: Op[]) {
    this.nome = nome;
    this.ops = traco.filter((o): o is OpDecisao => o.op === "decisao");
    this.deixadas = traco.filter(o => o.op !== "decisao");
  }

  get consumidas(): number { return this.k; }

  decideEm(tickPet: number): boolean {
    const op = this.ops[this.k];
    if (op !== undefined && op.tick < tickPet) throw new Error(`${this.nome}: a decisao do tick ${op.tick} ficou para tras (tick ${tickPet})`);
    return op !== undefined && op.tick === tickPet;
  }

  decidir(tickPet: number, porta: PortaDaDecisao) {
    const op = this.ops[this.k], onde = `${this.nome}, decisao ${this.k} (tick ${tickPet})`;
    const { mundo, social } = porta.antes(op.fome_antes);
    expect(comoJson(mundo), `percepcao, ${onde}`).toEqual(op.percepcao);
    expect(comoJson(social), `percepcao social, ${onde}`).toEqual(op.social);
    expect(op.com_gancho, `o gancho do alvo, ${onde}`).toBe(false);
    return { acao: op.acao, estado: op.estado, regra: op.regra };
  }

  depois(tickPet: number, r: ResultadoNoGrupo): void {
    const op = this.ops[this.k++], onde = `${this.nome}, decisao ${this.k - 1} (tick ${tickPet})`;
    expect(r.tickMundo, `tick do mundo, ${onde}`).toBe(op.tick_mundo);
    expect(comoJson(r.candidatos), `candidatos, ${onde}`).toEqual(op.candidatos);
    expect(comoJson(r.ocorrido), `ocorrido, ${onde}`).toEqual(op.ocorrido);
    expect(r.estado, `estado depois, ${onde}`).toEqual(op.depois);
    expect(comoJson(r.percepcaoDepois), `percepcao depois, ${onde}`).toEqual(op.percepcao_depois);
    expect(comoJson(r.tickSocial), `tick social, ${onde}`).toEqual(op.tick_social);
  }
}

const semRngs = (o: Rec): Rec => { const { rngs: _r, ...resto } = o; return resto; };

describe("a ConfigGrupo e a vez sorteada", () => {
  test("a ConfigGrupo do TS e a do digilab/config.py", () => {
    const py = readFileSync(new URL("../../../digilab/config.py", import.meta.url), "utf8");
    const bloco = py.slice(py.indexOf("class ConfigGrupo"), py.indexOf("CONFIG_GRUPO_LIGADA ="));
    const campo = (nome: string) => bloco.match(new RegExp(`\\n    ${nome}: [a-z]+ = ([^#\\n]+)`))![1].trim();
    expect(campo("ids")).toBe(`(${CONFIG_GRUPO_LIGADA.ids.map(i => `"${i}"`).join(", ")})`);
    expect(Number(campo("orcamento_por_dia"))).toBe(CONFIG_GRUPO_LIGADA.orcamento_por_dia);
    expect(Number(campo("raio_toque_celulas"))).toBe(CONFIG_GRUPO_LIGADA.raio_toque_celulas);
  });

  test("os 8 casos da vez (DP-2): o fluxo mundo-ordem e o Fisher-Yates do random.shuffle", () => {
    expect(G.ordem.length).toBe(8);
    for (const c of G.ordem) {
      const s = inteiro(c.semente);
      expect(String(derivarSemente("mundo-ordem", s)), `semente ${String(s)}`).toBe(String(c.semente_fluxo));
      const rng = new RandomPy(derivarSemente("mundo-ordem", s));
      const ordens = c.ordens.map(() => {
        const o = [...c.ids];
        for (let k = o.length - 1; k > 0; k--) { const j = rng.randrange(k + 1); [o[k], o[j]] = [o[j], o[k]]; }
        return o;
      });
      expect(ordens, `semente ${String(s)}, ids ${c.ids}`).toEqual(c.ordens);
    }
  });
});

describe("o G-PAR-GRUPO: as 5 vidas de dois pets da CO1, rejogadas do registro com o traco da CO2a", () => {
  test("o gabarito tem as 5 vidas, as duas disputas, a entrada atrasada, o comedouro comum e o layout afastado", () => {
    expect(G.vidas.map(v => v.semente)).toEqual([101, 202, 303, 404, 505]);
    expect(T.vidas.map(v => v.semente)).toEqual([101, 202, 303, 404, 505]);
    expect(G.vidas.reduce((n, v) => n + v.n_disputas, 0)).toBe(2);
    expect(G.vidas.some(v => v.entrada_b_dias > 0) && G.vidas.some(v => v.layout === "afastado") && G.vidas.some(v => v.corpo !== "sem")).toBe(true);
  });

  G.vidas.forEach((v, n) => {
    test(`vida ${v.semente} (${v.layout}, corpo ${v.corpo}, B entra no dia ${v.entrada_b_dias})`, () => {
      const t = T.vidas[n];
      const pets: Record<string, PetDoTraco> = Object.fromEntries(Object.entries(t.tracos).map(([i, tr]) => [i, new PetDoTraco(`${v.semente}/${i}`, tr)]));
      const registro = registroDe(v);
      const g = reproduzirGrupo(registro, Object.fromEntries(Object.keys(pets).map(i => [i, () => ({ pet: pets[i] })])), configDaVida(v));
      for (const [i, p] of Object.entries(pets)) expect(p.consumidas, `decisoes do pet ${i}`).toBe(t.n_decisoes[i]);
      const r = v.resumo;
      expect(g.tick).toBe(r.tick);
      expect(comoJson(g.ordens)).toEqual(r.ordens);
      expect(comoJson(g.contatos)).toEqual(r.contatos);
      expect(comoJson(g.disputas)).toEqual(r.disputas);
      expect([g.ordens.length, g.contatos.length, g.disputas.length]).toEqual([v.n_ordens, v.n_contatos, v.n_disputas]);
      expect(comoJson(g.comum.resumo())).toEqual(semRngs(r.mundo));
      for (const [i, pr] of Object.entries(r.pets)) {
        const m = g.mundoDe(i);
        expect(m.entrada, `entrada de ${i}`).toBe(pr.entrada);
        expect(comoJson(m.resumo()), `fisico de ${i}`).toEqual(semRngs(pr.fisico));
        expect(comoJson(m.resumoSocial()), `social de ${i}`).toEqual(pr.social);
        // a projecao do registro e o log de hoje do pet (o G1 do grupo no Python)
        expect(g.registro.projecao(i), `projecao de ${i}`).toEqual(pr.log.split("\n").filter(l => l.trim()).map(l => JSON.parse(l)));
        // o que o dono deixou no mundo pelo pet: o mesmo do traco, no relogio do pet
        const doRegistro = registro.eventos.filter(e => e.pet === i && (e.tipo === "deixar_comida" || e.tipo === "deixar_bola"));
        expect(doRegistro.map(e => [e.tick - pr.entrada, e.tipo])).toEqual(pets[i].deixadas.map(o => [o.tick, o.op]));
      }
      expect(g.registro.paraJsonl()).toBe(registro.paraJsonl());
    });
  });
});

describe("o registro do grupo e o replay", () => {
  const v = G.vidas[0];
  const fabricas = () => Object.fromEntries(Object.keys(T.vidas[0].tracos).map(i => [i, () => ({ pet: new PetDoTraco(i, T.vidas[0].tracos[i]) })]));

  test("o JSONL e o do Python: as chaves em ordem, sem espaco, o bigint inteiro e o nao-ASCII escapado", () => {
    const r = registroDe(G.vidas[3]);
    const linhas = r.paraJsonl().split("\n");
    expect(linhas.at(-1)).toBe("");
    expect(linhas[1]).toBe('{"destino":"grupo","origem":null,"pet":"A","tick":0,"tipo":"entrada","valor":"A"}');
    expect(linhas[0]).toContain(`"semente":${String(registroDe(G.vidas[3]).cabecalho.pets.B.semente)}`);
    expect(String(r.cabecalho.pets.B.semente)).toBe("1972500660511810415");
    expect(jsonPython({ b: "ç", a: [1, null, true] })).toBe('{"a":[1,null,true],"b":"\\u00e7"}');
    expect(() => jsonPython(0.5)).toThrow();
  });

  test("falha alto: o registro refeito diferente do lido, evento fora do tick, desconhecido e de pet que nao entrou", () => {
    const base = registroDe(v);
    const com = (f: (e: EventoGrupo[]) => EventoGrupo[]) => new RegistroGrupo(base.cabecalho, f(base.eventos.map(e => ({ ...e }))));
    const cm = configDaVida(v);
    const aval = base.eventos.findIndex(e => e.tipo === "acao_usuario");
    expect(() => reproduzirGrupo(com(es => { es[aval] = { ...es[aval], origem: "dono:B" }; return es; }), fabricas(), cm)).toThrow(RegistroDivergente);
    expect(() => reproduzirGrupo(com(es => { es[1] = { ...es[1], tick: 7 }; return es; }), fabricas(), cm)).toThrow(/fora|tick 7/);
    expect(() => reproduzirGrupo(com(es => [...es.slice(0, 2), { ...es[1], tipo: "sacudir" as EventoGrupo["tipo"] }]), fabricas(), cm)).toThrow(/desconhecido/);
    expect(() => reproduzirGrupo(com(es => [es[0], { tick: 0, tipo: "acao_usuario", valor: "elogiar", destino: "pet:B", pet: "B", origem: "dono" }]), fabricas(), cm))
      .toThrow(/nao entrou/);
    expect(() => reproduzirGrupo(new RegistroGrupo({ ...base.cabecalho, versao: 2 }, base.eventos), fabricas(), cm)).toThrow(/versao/);
    expect(() => reproduzirGrupo(new RegistroGrupo({ ...base.cabecalho, sentidos: {} } as CabecalhoGrupo, base.eventos), fabricas(), cm)).toThrow(/sentidos/);
  });

  test("o grupo recusa: o pet fora dos ids, repetido, fora do inicio de dia, a acao do dono desconhecida e a ConfigGrupo invalida", () => {
    const g = new Grupo(CMU, 101);
    const nada: PetDoGrupo = { decideEm: () => false, decidir: () => { throw new Error("nao decide"); } };
    expect(() => g.entrar("C", nada, "x", "y")).toThrow(/fora do grupo/);
    g.entrar("A", nada, "x", "y");
    expect(() => g.entrar("A", nada, "x", "y")).toThrow(/ja entrou/);
    g.avancar(15);
    expect(() => g.entrar("B", nada, "x", "y")).toThrow(/inicio de dia/);
    expect(() => g.acaoDono("A", "voar")).toThrow(/desconhecida/);
    expect(() => g.acaoDono("B", "elogiar")).toThrow(/nao entrou/);
    expect(() => new Grupo(CMU, 1, { ...CONFIG_GRUPO_LIGADA, ligada: false })).toThrow(/ligada/);
    expect(() => new Grupo(CMU, 1, { ...CONFIG_GRUPO_LIGADA, ids: ["B", "A"] })).toThrow(/em ordem/);
    expect(() => new Grupo(CMU, 1, { ...CONFIG_GRUPO_LIGADA, ids: ["A", "B", "C"] })).toThrow(/dois pets/);
    const sem: PetDoGrupo = { decideEm: () => true, decidir: () => ({ acao: "dormir", estado: { fome: 1, energia: 1, humor: 1, sujeira: 0 }, regra: null }) };
    const g2 = new Grupo(CMU, 101);
    g2.entrar("A", sem, "x", "y");
    expect(() => g2.avancar(1)).toThrow(/sem perceber/);
  });
});
