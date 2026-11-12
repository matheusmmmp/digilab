/* O enjoo da imagem (GOSTO_VISUAL; D-GV-ENJOO-CER no docs/registro/2026-11.md): a paridade com o Python, bit a bit no Node. O gabarito e o
   test/gabaritos/gosto_visual_enjoo.json.gz (experiments/exportar_gosto_visual.py; o tests/test_gabarito_gosto_visual_web.py confere que ele
   sai igual de uma execucao nova). Confere:
     - a ConfigEnjooTela (a ligada do gabarito e a desligada por padrao) e a falha alto;
     - as vidas com a chave ligada no corpo e no cerebro (a TV do jogo, o modo livre gravado e a imagem parada, 3 sementes cada): o laco do
       TS rejoga o log do Python e confere, decisao a decisao, a acao, o motivo (com o enjoo lido, o agrado efetivo e o termo `enjoo`), a
       assinatura de cada modulo e os estimulos do corpo; no fim, o estado interno do cerebro, o corpo (com a memoria dos prototipos), as
       novidades da tela e o registro da TV;
     - a chave desligada: nenhum campo novo no corpo nem no cerebro (o gosto_visual.json.gz de antes e conferido pelo
       gosto_visual_paridade.test.ts, que nao mudou). */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP } from "../motor/constantes.ts";
import { CCO_CORPO_V11, Corpo } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_DIGIBRAIN_LAB_OLHAR, CONFIG_OLHAR, CONFIG_SONO_SEGURA, INATOS_MODULAR } from "../motor/digibrain/constantes.ts";
import { CONFIG_ENJOO_TELA, CONFIG_ENJOO_TELA_LIGADA, RECEPTOR_ENJOO_TELA, conferirConfigEnjooTela } from "../motor/enjoo_tela.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { CONFIG_TELA_LIGADA, CONFIG_TV, type ConfigTV } from "../motor/tv.ts";
import { assinar, conferir } from "./digibrain_modular_gabarito.ts";

const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;
type Dict = Record<string, any>;
interface Vida {
  fonte: "grade" | "evento"; semente: number; imagem?: number[]; dias: number; olhares: number;
  decisoes: { k: number; acao: string; assinatura: Record<string, string>; motivo: Dict; estimulos: unknown[][] }[];
  log: EventoCorpo[]; estado: string; assinatura_final: Record<string, string>; corpo: Dict; novidades_tela: number[]; tv: Dict;
}
const gab = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/gosto_visual_enjoo.json.gz", import.meta.url))).toString("utf8")) as Dict & { vidas: Vida[] };

/** o `repr` do float do Python no JSON, como no gosto_visual_paridade.test.ts */
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
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB_OLHAR, INATOS_MODULAR, false, CONFIG_SONO_SEGURA,
                                { semente: g.semente, cfgOlhar: { ...CONFIG_OLHAR, agrado_no_corpo: g.fonte === "evento" }, cfgEnjooTela: CONFIG_ENJOO_TELA_LIGADA });
  const assinaturas: Record<string, string>[] = [], estimulos: unknown[][][] = [];
  const agir = cerebro.agir.bind(cerebro), cons = cerebro.consequenciaCorpo.bind(cerebro);
  cerebro.agir = (obs, rng) => {
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  cerebro.consequenciaCorpo = (acao, ocorrido, obs) => { estimulos.push(ocorrido.estimulos.map(e => [...e])); cons(acao, ocorrido, obs); };
  const m = new MotorCorpoMundo(cerebro, g.semente, CCO_CORPO_V11, estadoNascimentoPy(0), {
    paridade: true, cfgMundo: CMU_MVP, digibrain: true, tela: { tela: CONFIG_TELA_LIGADA, tv: cfgTv(g.fonte), enjoo: CONFIG_ENJOO_TELA_LIGADA } });
  for (const e of g.log) m.aplicarEvento(e);
  return { m, cerebro, assinaturas, estimulos };
}

describe("o enjoo: a config e a do Python", () => {
  test("a ConfigEnjooTela ligada do gabarito, a desligada por padrao e a falha alto", () => {
    expect(gab.versao).toBe(1);
    expect({ ...CONFIG_ENJOO_TELA_LIGADA }).toEqual(gab.config_enjoo_tela);
    expect(CONFIG_ENJOO_TELA.ligada).toBe(false);
    for (const ruim of [{ prototipos: 0 }, { w_enjoo: 2000 }, { saturacao_exposicao: 1024 }, { tau_enjoo_lembrado: 14 }, { ligada: 1 }]) {
      expect(() => conferirConfigEnjooTela({ ...CONFIG_ENJOO_TELA, ...ruim } as never)).toThrow(/ConfigEnjooTela/);
    }
    const q = Corpo.deEstado(estadoNascimentoPy(0), { cc: CCO_CORPO_V11, comMundo: true }).q;
    expect(() => new Corpo(q, { cc: CCO_CORPO_V11, comMundo: true, enjoo: CONFIG_ENJOO_TELA_LIGADA })).toThrow(/ConfigTela/);
    const qt = Corpo.deEstado(estadoNascimentoPy(0), { cc: CCO_CORPO_V11, comMundo: true, tela: CONFIG_TELA_LIGADA }).q;
    expect(() => new Corpo(qt, { cc: CCO_CORPO_V11, comMundo: true, tela: CONFIG_TELA_LIGADA, enjoo: { ...CONFIG_ENJOO_TELA_LIGADA, k_enjoo: 2961 } }))
      .toThrow(/k_enjoo/);
    expect(() => new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, CONFIG_SONO_SEGURA, { cfgEnjooTela: CONFIG_ENJOO_TELA_LIGADA }))
      .toThrow(/subchave olhar/);
  });
});

describe("o enjoo: as vidas com a chave ligada no laco do TS, iguais ao Python", () => {
  test("o gabarito: 9 vidas (grade, evento e a imagem parada x 3 sementes) de 288 decisoes, todas com o olhar", () => {
    expect(gab.vidas.length).toBe(9);
    expect(gab.vidas.filter(v => v.imagem !== undefined).length).toBe(3);
    for (const v of gab.vidas) { expect(v.decisoes.length).toBe(288); expect(v.olhares).toBeGreaterThan(0); }
  });
  let total = 0, lidos = 0;
  for (const g of gab.vidas) {
    test(`${g.fonte}${g.imagem ? "/parada" : ""}/${g.semente}: cada decisao (acao, motivo, assinatura, estimulos) e o fim (cerebro, corpo, TV)`, () => {
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
      expect(g.corpo["tela"]["memoria"].length).toBeGreaterThan(0);
      total += g.decisoes.length;
      lidos += v.cerebro.motivos.filter(x => x["olhar"]["enjoo"] !== null).length;
    });
  }
  test("a soma: 2 592 decisoes conferidas, com o enjoo lido", () => { expect(total).toBe(2592); expect(lidos).toBeGreaterThan(0); });
});

describe("o enjoo: desligado, nada muda", () => {
  test("sem a opcao enjoo, o corpo nao tem a memoria nem o receptor, e o cerebro nao tem o termo nem o estado", () => {
    const c = new DigiBrain(CONFIG_DIGIBRAIN_LAB_OLHAR, INATOS_MODULAR, false, CONFIG_SONO_SEGURA, { semente: 101 });
    const m = new MotorCorpoMundo(c, 101, CCO_CORPO_V11, estadoNascimentoPy(0), {
      paridade: true, cfgMundo: CMU_MVP, digibrain: true, tela: { tela: CONFIG_TELA_LIGADA, tv: cfgTv("grade") } });
    m.avancar(240);
    expect(Object.keys(m.corpo.paraDict()["tela"] as Dict).sort()).toEqual(["estimulo", "sentido"]);
    expect(RECEPTOR_ENJOO_TELA in m.corpo.receptores()).toBe(false);
    expect("enjoo_tv" in (c.estadoInterno()["olhar"] as Dict)).toBe(false);
    expect(c.motivos.every(x => !("enjoo" in x["olhar"]) && x["unidades"].every((u: Dict) => !("enjoo" in u["termos"])))).toBe(true);
  });
});
