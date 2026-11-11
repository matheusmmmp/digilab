/* GOSTO_VISUAL, P1f: a paridade do gosto visual com o Python (docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 1.2, 8 e 9). O gabarito e o
   test/gabaritos/gosto_visual.json.gz (experiments/exportar_gosto_visual.py; o tests/test_gabarito_gosto_visual_web.py confere que ele sai
   igual de uma execucao nova). Confere, bit a bit no Node:
     - as constantes (os canais, a ConfigTela, a ConfigTV, a ConfigOlhar e a ConfigDigibrain da vida, a do laboratorio com o `olhar`);
     - o genoma da visao (rng propria `visao-ovo`), a grade da TV do jogo (rng propria `tv-programas`) e o ResumoTela (GV-15);
     - o grafo do corpo com o orgao da tela;
     - as vidas (a TV do jogo e o modo livre gravado, 3 sementes cada): o laco do TS rejoga o log do Python e confere, decisao a decisao, a
       acao, o motivo, a assinatura de cada modulo e os estimulos do corpo; no fim, o estado interno do cerebro, o corpo, as novidades da tela
       e o registro da TV;
     - a chave desligada: sem a opcao `tela`, o laco nao aceita os eventos novos, e o DigiBrain sem o `olhar` recusa os ganchos. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP } from "../motor/constantes.ts";
import { CCO_CORPO_V11, Corpo, grafoDoCorpo, taxasDe } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_DIGIBRAIN_LAB_OLHAR, CONFIG_OLHAR, INATOS_MODULAR } from "../motor/digibrain/constantes.ts";
import { genomaVisao, genomaVisaoVazio } from "../motor/digibrain/genoma_visao.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { CANAIS_TELA, CONFIG_TELA, CONFIG_TELA_LIGADA, CONFIG_TV, ResumoTela, TV, type ConfigTV } from "../motor/tv.ts";
import { assinar, conferir } from "./digibrain_modular_gabarito.ts";

const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;
type Dict = Record<string, any>;
interface Vida {
  fonte: "grade" | "evento"; semente: number; dias: number; olhares: number; assistir: number; agrados: number;
  decisoes: { k: number; acao: string; assinatura: Record<string, string>; motivo: Dict; estimulos: unknown[][] }[];
  log: EventoCorpo[]; log_sha256: string; estado: string; assinatura_final: Record<string, string>; corpo: Dict; novidades_tela: number[]; tv: Dict;
}
const gab = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/gosto_visual.json.gz", import.meta.url))).toString("utf8")) as Dict & { vidas: Vida[] };

/** o `repr` do float do Python no JSON (o `u` do sorteio), como no gabarito da fala */
function floatPy(x: number): string {
  if (x !== 0 && Math.abs(x) < 1e-4) {
    const [m, e] = x.toExponential().split("e");
    const n = Number(e);
    return `${m}e${n < 0 ? "-" : "+"}${String(Math.abs(n)).padStart(2, "0")}`;
  }
  return String(x);
}
function textoPy(v: unknown, chave = ""): string {
  if (v === null || typeof v === "boolean") return String(v === null ? "null" : v);
  if (typeof v === "string") return JSON.stringify(v);
  if (typeof v === "number") return Number.isInteger(v) && chave !== "u" ? String(v) : floatPy(v);
  if (Array.isArray(v)) return `[${v.map(x => textoPy(x)).join(",")}]`;
  const o = v as Record<string, unknown>;
  return `{${Object.keys(o).sort().map(k => `${JSON.stringify(k)}:${textoPy(o[k], k)}`).join(",")}}`;
}
const sha = (t: string): string => createHash("sha256").update(t, "utf8").digest("hex");
const cfgTv = (fonte: "grade" | "evento"): ConfigTV => ({ ...CONFIG_TV, ligada: true, fonte });

function viver(g: Vida) {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB_OLHAR, INATOS_MODULAR, false,
                                { semente: g.semente, cfgOlhar: { ...CONFIG_OLHAR, agrado_no_corpo: g.fonte === "evento" } });
  const assinaturas: Record<string, string>[] = [], estimulos: unknown[][][] = [];
  const agir = cerebro.agir.bind(cerebro), cons = cerebro.consequenciaCorpo.bind(cerebro);
  cerebro.agir = (obs, rng) => {
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  cerebro.consequenciaCorpo = (acao, ocorrido, obs) => { estimulos.push(ocorrido.estimulos.map(e => [...e])); cons(acao, ocorrido, obs); };
  const m = new MotorCorpoMundo(cerebro, g.semente, CCO_CORPO_V11, estadoNascimentoPy(0),
                                { paridade: true, cfgMundo: CMU_MVP, digibrain: true, tela: { tela: CONFIG_TELA_LIGADA, tv: cfgTv(g.fonte) } });
  for (const e of g.log) m.aplicarEvento(e);
  return { m, cerebro, assinaturas, estimulos };
}

describe("P1f: as constantes do gosto visual sao as do Python", () => {
  test("os canais, a ConfigTela, a ConfigTV, a ConfigOlhar e a ConfigDigibrain da vida (o laboratorio com o olhar)", () => {
    expect(gab.versao).toBe(1);
    expect([...CANAIS_TELA]).toEqual(gab.canais);
    expect({ ...CONFIG_TELA_LIGADA }).toEqual(gab.config_tela);
    expect(JSON.parse(JSON.stringify(cfgTv("grade")))).toEqual(gab.config_tv);
    expect(JSON.parse(JSON.stringify(CONFIG_OLHAR))).toEqual(gab.config_olhar);
    expect({ ...CONFIG_DIGIBRAIN_LAB_OLHAR }).toEqual(gab.config_digibrain);
    expect(CONFIG_TELA.ligada).toBe(false);
    expect(CONFIG_TV.ligada).toBe(false);
    expect("olhar" in CONFIG_DIGIBRAIN_LAB).toBe(false);             // a config de hoje sem o campo: as constantes do modular nao mudam
  });
  test("o genoma da visao (visao-ovo) das sementes dos testes e o vazio", () => {
    for (const [s, gv] of Object.entries(gab.genomas)) expect(genomaVisao(Number(s))).toEqual(gv);
    expect(genomaVisaoVazio()).toEqual(gab.genoma_vazio);
  });
  test("a grade da TV do jogo (tv-programas): os perfis, o que passa, a troca de canal e a grade sorteada", () => {
    for (const gr of gab.grades) {
      const tv = new TV(cfgTv("grade"), gr.semente, 0, 0);
      expect(tv.programas).toEqual(gr.programas);
      for (const [t, p, v] of gr.em) { expect(tv.programaEm(t)).toBe(p); expect(CANAIS_TELA.map(c => tv.em(t)![c])).toEqual(v); }
      expect(tv.trocarCanal((tv.programaEm(200)! + 1) % 4, 200)).toEqual(gr.troca);
      for (const [t, p, v] of gr.depois) { expect(tv.programaEm(t)).toBe(p); expect(CANAIS_TELA.map(c => tv.em(t)![c])).toEqual(v); }
      expect(tv.grade.map(s => ({ inicio: s.inicio, fim: s.fim, programa: s.programa }))).toEqual(gr.grade);
    }
  });
  test("o ResumoTela (GV-15): a media de 10 amostras em 16 niveis, o evento so na mudanca", () => {
    const r = new ResumoTela(gab.resumo.fonte, gab.resumo.janela), eventos: [number, string][] = [];
    (gab.resumo.amostras as number[][]).forEach((v, i) => { const e = r.amostra(v); if (e !== null) eventos.push([i, e]); });
    expect(eventos).toEqual(gab.resumo.eventos);
    expect(eventos.length).toBeGreaterThan(3);
  });
  test("o grafo do corpo com a tela: os quimicos, os emissores, os orgaos e a soma", () => {
    const g = grafoDoCorpo(CCO_CORPO_V11, taxasDe(CCO_CORPO_V11), true, CONFIG_TELA_LIGADA);
    expect(g.quimicos).toEqual(gab.grafo.quimicos);
    expect(g.emissores).toEqual((gab.grafo.emissores as Dict[]).map(({ destino, ...e }) => { expect(destino).toBe("corpo"); return e; }));
    expect(g.orgaos).toEqual(gab.grafo.orgaos);
    expect(g.somas).toEqual(gab.grafo.somas);
    expect(() => new Corpo(Corpo.deEstado(estadoNascimentoPy(0), { cc: CCO_CORPO_V11, comMundo: false }).q, { cc: CCO_CORPO_V11, tela: CONFIG_TELA_LIGADA }))
      .toThrow(/mundo fisico/);
  });
});

describe("P1f: as vidas com a TV no laco do TS, iguais ao Python", () => {
  test("o gabarito: 6 vidas (grade e evento x 3 sementes) de 288 decisoes, todas com o olhar, o assistir e, no evento, o agrado no corpo", () => {
    expect(gab.vidas.length).toBe(6);
    for (const v of gab.vidas) {
      expect(v.decisoes.length).toBe(288);
      expect(v.olhares).toBeGreaterThan(0);
      expect(v.assistir).toBe(v.olhares);
      expect(v.agrados).toBe(v.fonte === "evento" ? v.olhares : 0);
    }
  });
  let total = 0, olhares = 0;
  for (const g of gab.vidas) {
    test(`${g.fonte}/${g.semente}: cada decisao (acao, motivo, assinatura, estimulos) e o fim (cerebro, corpo, TV)`, () => {
      const v = viver(g);
      expect(v.m.log).toEqual(g.log);
      expect(v.cerebro.motivos.length).toBe(g.decisoes.length);
      g.decisoes.forEach((d, k) => {
        conferir(`k=${k} acao`, v.cerebro.motivos[k]!["acao"], d.acao);
        conferir(`k=${k} estimulos`, v.estimulos[k], d.estimulos);
        conferir(`k=${k} motivo`, v.cerebro.motivos[k], d.motivo);
        conferir(`k=${k} assinatura`, v.assinaturas[k], d.assinatura);
      });
      expect(sha(textoPy(v.cerebro.estadoInterno())), "estado interno no fim").toBe(g.estado);
      conferir("assinatura final", Object.fromEntries(ASSINADOS.map(n => [n, assinar(v.cerebro[n].estadoInterno())])), g.assinatura_final);
      conferir("corpo", v.m.corpo.paraDict(), g.corpo);
      conferir("novidades da tela", v.m.novidadesTela, g.novidades_tela);
      conferir("TV", v.m.tv!.resumo(), g.tv);
      total += g.decisoes.length;
      olhares += v.cerebro.motivos.filter(x => x["olhar"]["olha"] !== null).length;
    });
  }
  test("a soma: 1 728 decisoes conferidas, com o olhar", () => { expect(total).toBe(1728); expect(olhares).toBeGreaterThan(0); });
});

describe("P1f: desligado, nada muda", () => {
  test("sem a opcao `tela`, o laco recusa os eventos da TV; o DigiBrain sem o olhar recusa os ganchos e nao tem campo novo", () => {
    const c = new DigiBrain(CONFIG_DIGIBRAIN_LAB);
    const m = new MotorCorpoMundo(c, 101, CCO_CORPO_V11, estadoNascimentoPy(0), { paridade: true, cfgMundo: CMU_MVP, digibrain: true });
    expect(m.tv).toBeNull();
    expect(() => m.aplicarEvento({ tick: 0, tipo: "trocar_canal", valor: "1" })).toThrow(/TV/);
    expect(() => m.aplicarEvento({ tick: 0, tipo: "sentido_tela", valor: "tv|1|1|1|1|1|1|1" })).toThrow(/TV/);
    expect(() => c.olhandoTela()).toThrow(/olhar/);
    expect(() => c.verTela([])).toThrow(/olhar/);
    expect(() => c.agradoTela({})).toThrow(/olhar/);
    expect("olhar" in c.estadoInterno()).toBe(false);
    expect(Object.keys(m.corpo.q).some(q => q.startsWith("adaptacao_tela"))).toBe(false);
    expect(() => new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, { semente: 1 })).toThrow(/subchave olhar/);
  });
  test("a TV e o orgao da tela vao juntos, ligados e com um pet so; eventos mal formados falham alto", () => {
    const c = new DigiBrain(CONFIG_DIGIBRAIN_LAB_OLHAR, INATOS_MODULAR, false, { semente: 101 });
    const op = { paridade: true, cfgMundo: CMU_MVP, digibrain: true };
    expect(() => new MotorCorpoMundo(c, 101, CCO_CORPO_V11, estadoNascimentoPy(0), { ...op, tela: { tela: CONFIG_TELA, tv: cfgTv("grade") } })).toThrow(/juntos/);
    expect(() => new MotorCorpoMundo(c, 101, CCO_CORPO_V11, estadoNascimentoPy(0), { ...op, tela: { tela: CONFIG_TELA_LIGADA, tv: { ...cfgTv("grade"), escala: 9 } } })).toThrow(/escala/);
    const m = new MotorCorpoMundo(c, 101, CCO_CORPO_V11, estadoNascimentoPy(0), { ...op, tela: { tela: CONFIG_TELA_LIGADA, tv: cfgTv("grade") } });
    expect(() => m.aplicarEvento({ tick: 0, tipo: "sentido_tela", valor: "tv|1|1|1|1|1|1|1" })).toThrow(/fonte/);
    expect(() => m.aplicarEvento({ tick: 0, tipo: "trocar_canal", valor: "01" })).toThrow(/malformado/);
    expect(() => m.aplicarEvento({ tick: 0, tipo: "trocar_canal", valor: "4" })).toThrow(/nao existe/);
    expect(() => m.ilhaDoDono("ilha_agua")).toThrow();
  });
});
