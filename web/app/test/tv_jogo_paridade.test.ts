/* GOSTO_VISUAL, a TV no jogo (as decisoes A, B e D da captura ligada ao cerebro; docs/registro/2026-11.md, D-GV-TVJOGO): a paridade com o
   Python. O gabarito e o test/gabaritos/tv_jogo.json.gz (experiments/exportar_tv_jogo.py; o tests/test_gabarito_tv_jogo_web.py confere que
   ele sai igual de uma execucao nova). Confere, bit a bit no Node:
     - as vidas de um pet so (3 sementes, 3 dias): o laboratorio com o olhar, a ConfigTVJogo ligada (a TV desligada das 20 h as 23 h) e o
       DigiBrain com o ir ate a TV; o laco do TS rejoga o log do Python e confere, decisao a decisao, a acao (o "ir_tv" incluido), o motivo,
       a assinatura de cada modulo e os estimulos do corpo; no fim, o cerebro, o corpo, as decisoes do mundo e o registro da TV;
     - as vidas do grupo (2 sementes, 2 dias): a TV do mundo comum, dois lacos com o mesmo laboratorio; o Grupo do TS rejoga o registro do
       grupo do Python e confere, de cada pet, a acao e o motivo de cada decisao, o cerebro, o corpo, a posicao e as decisoes do mundo, e a TV;
     - a chave desligada: sem a ConfigTVJogo, o laco recusa a TV desligada e o "ir_tv", e o DigiBrain sem o ir ate a TV recusa a linha longe. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { CONFIG_DIGIBRAIN_LAB_OLHAR, CONFIG_OLHAR, CONFIG_SONO_SEGURA, INATOS_MODULAR } from "../motor/digibrain/constantes.ts";
import { CONFIG_GRUPO_LIGADA, Grupo } from "../motor/grupo.ts";
import { sementeDoSegundoJogo } from "../motor/grupo_jogo.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { lerDeixarComida, type Mundo, type OpcoesMundo } from "../motor/mundo.ts";
import { CONFIG_TELA_LIGADA, CONFIG_TV, CONFIG_TVJOGO, CONFIG_TVJOGO_LIGADA, type ConfigTV } from "../motor/tv.ts";
import { assinar, conferir } from "./digibrain_modular_gabarito.ts";

const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;
type Dict = Record<string, any>;
interface Vida {
  semente: number; dias: number; ir_tv: number; olhares: number;
  decisoes: { k: number; acao: string; assinatura: Record<string, string>; motivo: Dict; estimulos: unknown[][] }[];
  log: EventoCorpo[]; estado: string; assinatura_final: Record<string, string>; corpo: Dict; decisoes_mundo: Dict[]; tv: Dict;
}
interface PetGrupo { semente: number; acoes: string[]; motivos_sha256: string[]; estado: string; corpo: Dict; pet: [number, number]; decisoes_mundo: Dict[] }
interface VidaGrupo {
  semente: number; dias: number; cabecalho: Dict; pets: Record<string, PetGrupo>; tv: Dict; contatos: number;
  registro: { tick: number; tipo: string; valor: string | number; destino: string; pet: string | null; origem: string | null }[];
}
const gab = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/tv_jogo.json.gz", import.meta.url))).toString("utf8")) as
  { versao: number; config_tv_jogo: Dict; vidas: Vida[]; grupos: VidaGrupo[] };

/** o `repr` do float do Python no JSON (o `u` do sorteio), como no gabarito do gosto visual */
function floatPy(x: number): string {
  if (x !== 0 && Math.abs(x) < 1e-4) {
    const [m, e] = x.toExponential().split("e");
    const n = Number(e);
    return `${m}e${n < 0 ? "-" : "+"}${String(Math.abs(n)).padStart(2, "0")}`;
  }
  return String(x);
}
function textoPy(v: unknown, chave = ""): string {
  if (v === null || v === undefined || typeof v === "boolean") return String(v === null || v === undefined ? "null" : v);
  if (typeof v === "string") return JSON.stringify(v);
  if (typeof v === "number") return Number.isInteger(v) && chave !== "u" ? String(v) : floatPy(v);
  if (Array.isArray(v)) return `[${v.map(x => textoPy(x)).join(",")}]`;
  const o = v as Record<string, unknown>;
  return `{${Object.keys(o).sort().map(k => `${JSON.stringify(k)}:${textoPy(o[k], k)}`).join(",")}}`;
}
const sha = (t: string): string => createHash("sha256").update(t, "utf8").digest("hex");
const CTV: ConfigTV = { ...CONFIG_TV, ligada: true, fonte: "evento" };
const cerebro = (s: number): DigiBrain => new DigiBrain(CONFIG_DIGIBRAIN_LAB_OLHAR, INATOS_MODULAR, false, CONFIG_SONO_SEGURA,
                                                         { semente: s, cfgOlhar: { ...CONFIG_OLHAR, agrado_no_corpo: true }, irAteTv: true });
const OPCOES = { paridade: true, cfgMundo: CMU_MVP, digibrain: true, tela: { tela: CONFIG_TELA_LIGADA, tv: CTV, tvJogo: CONFIG_TVJOGO_LIGADA } };
/** as decisoes do mundo no formato do Python (o alvo so pelo tipo, como o registro) */
const decisoesDo = (m: MotorCorpoMundo): unknown => JSON.parse(JSON.stringify(m.mundo.decisoes));

function viver(g: Vida) {
  const c = cerebro(g.semente);
  const assinaturas: Record<string, string>[] = [], estimulos: unknown[][][] = [];
  const agir = c.agir.bind(c), cons = c.consequenciaCorpo.bind(c);
  c.agir = (obs, rng) => { const a = agir(obs, rng); assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(c[n].estadoInterno())]))); return a; };
  c.consequenciaCorpo = (acao, ocorrido, obs) => { estimulos.push(ocorrido.estimulos.map(e => [...e])); cons(acao, ocorrido, obs); };
  const m = new MotorCorpoMundo(c, g.semente, CCO_CORPO_V11, estadoNascimentoPy(0), OPCOES);
  for (const e of g.log) m.aplicarEvento(e);
  return { m, c, assinaturas, estimulos };
}

describe("a TV no jogo: as vidas de um pet so, iguais ao Python", () => {
  test("o gabarito: 3 vidas de 288 decisoes, com o ir ate a TV, o olhar e a TV desligada", () => {
    expect(gab.versao).toBe(1);
    expect(gab.config_tv_jogo).toEqual({ ...CONFIG_TVJOGO_LIGADA });
    expect(gab.vidas.length).toBe(3);
    for (const v of gab.vidas) {
      expect(v.decisoes.length).toBe(288);
      expect(v.ir_tv).toBeGreaterThan(0);
      expect(v.olhares).toBeGreaterThan(0);
      expect(v.log.filter(e => e.tipo === "sentido_tela" && e.valor === "tv|desligada").length).toBe(3);
    }
  });
  for (const g of gab.vidas) {
    test(`${g.semente}: cada decisao (acao, motivo, assinatura, estimulos) e o fim (cerebro, corpo, mundo, TV)`, () => {
      const v = viver(g);
      expect(v.m.log).toEqual(g.log);
      expect(v.c.motivos.length).toBe(g.decisoes.length);
      g.decisoes.forEach((d, k) => {
        conferir(`k=${k} acao`, v.c.motivos[k]!["acao"], d.acao);
        conferir(`k=${k} estimulos`, v.estimulos[k], d.estimulos);
        conferir(`k=${k} motivo`, v.c.motivos[k], d.motivo);
        conferir(`k=${k} assinatura`, v.assinaturas[k], d.assinatura);
      });
      expect(sha(textoPy(v.c.estadoInterno())), "estado interno no fim").toBe(g.estado);
      conferir("corpo", v.m.corpo.paraDict(), g.corpo);
      conferir("decisoes do mundo", decisoesDo(v.m), g.decisoes_mundo);
      conferir("TV", v.m.tv!.resumo(), g.tv);
    });
  }
});

/** o laco do corpo com o mundo como membro do Grupo (o com_corpo(MotorMundo) do Python dentro do grupo) */
function lacoNoGrupo(s: number) {
  let laco: MotorCorpoMundo | null = null;
  const criar = (parte: (op: OpcoesMundo) => Mundo) => {
    laco = new MotorCorpoMundo(cerebro(s), s, CCO_CORPO_V11, estadoNascimentoPy(0), { ...OPCOES, parteDoMundo: parte });
    const l = laco;
    return { decideNoProximoTick: () => l.decideNoProximoPasso(), umTickNoGrupo: () => { l.passo(); }, get acao() { return l.acaoAtual as string; } };
  };
  return { criar, laco: () => laco! };
}

describe("a TV no grupo (a decisao B): o Grupo do TS rejoga o registro do Python", () => {
  for (const vg of gab.grupos) {
    test(`grupo ${vg.semente}: os dois pets (a acao e o motivo de cada decisao, o cerebro, o corpo, a posicao), o mundo e a TV do mundo comum`, () => {
      const g = new Grupo(CMU_MVP, vg.semente, CONFIG_GRUPO_LIGADA, { sementeDoSegundo: sementeDoSegundoJogo, tv: CTV, tvJogo: CONFIG_TVJOGO_LIGADA });
      expect(JSON.parse(JSON.stringify(g.registro.cabecalho))["tv"]).toEqual(vg.cabecalho["tv"]);
      expect(JSON.parse(JSON.stringify(g.registro.cabecalho))["tv_jogo"]).toEqual(vg.cabecalho["tv_jogo"]);
      const lacos: Record<string, () => MotorCorpoMundo> = {};
      for (const e of vg.registro) {
        expect(e.tick, JSON.stringify(e)).toBe(g.tick);
        if (e.tipo === "entrada") {
          const s = Number(g.sementes[e.valor as string]);
          expect(s).toBe(vg.pets[e.valor as string]!.semente);
          const { criar, laco } = lacoNoGrupo(s);
          g.entrarMotor(e.valor as string, 0, criar, "modular", "gabarito");
          lacos[e.valor as string] = laco;
        } else if (e.tipo === "avanco") g.avancar(e.valor as number);
        else if (e.tipo === "deixar_comida") lacos[e.pet!]!().deixarComida(...lerDeixarComida({ tick: e.tick, tipo: "deixar_comida", valor: String(e.valor) }));
        else if (e.tipo === "sentido_tela") { expect([e.destino, e.pet]).toEqual(["mundo", null]); g.sentidoTela(String(e.valor)); }
        else throw new Error(`evento inesperado: ${JSON.stringify(e)}`);
      }
      for (const [i, p] of Object.entries(vg.pets)) {
        const l = lacos[i]!(), c = l.politica as DigiBrain;
        conferir(`${i} acoes`, c.motivos.map(x => x["acao"]), p.acoes);
        conferir(`${i} motivos`, c.motivos.map(x => sha(textoPy(x))), p.motivos_sha256);
        expect(sha(textoPy(c.estadoInterno())), `${i} estado interno`).toBe(p.estado);
        conferir(`${i} corpo`, l.corpo.paraDict(), p.corpo);
        expect([...l.mundo.pet]).toEqual(p.pet);
        conferir(`${i} decisoes do mundo`, decisoesDo(l), p.decisoes_mundo);
        expect(p.acoes).toContain("ir_tv");
      }
      conferir("TV do mundo comum", g.comum.tv!.resumo(), vg.tv);
      expect(g.contatos.length).toBe(vg.contatos);
    });
  }
});

describe("a TV no jogo: desligada, nada muda", () => {
  test("sem a ConfigTVJogo, o laco recusa a TV desligada e o ir_tv; o DigiBrain sem o ir ate a TV recusa a linha longe", () => {
    const c = new DigiBrain(CONFIG_DIGIBRAIN_LAB_OLHAR, INATOS_MODULAR, false, CONFIG_SONO_SEGURA, { semente: 101 });
    const m = new MotorCorpoMundo(c, 101, CCO_CORPO_V11, estadoNascimentoPy(0), { ...OPCOES, tela: { tela: CONFIG_TELA_LIGADA, tv: CTV } });
    expect(m.tvJogo).toEqual(CONFIG_TVJOGO);
    expect(() => m.aplicarEvento({ tick: 0, tipo: "sentido_tela", valor: "tv|desligada" })).toThrow(/desligar/);
    expect(m.mundo.alvoTv).toBeNull();
    expect(() => m.mundo.consequencia(0, "ir_tv", { fome: 0, energia: 1, humor: 1, sujeira: 0 })).toThrow(/ir_ate_tv/);
    expect(() => c.verTela([[1, 900, 0, 900]])).not.toThrow();
    expect(() => c.agir({ ...m.observacao(), mundo: m.mundo.perceber(0) } as never, null as never)).toThrow(/fora do raio/);
  });
});
