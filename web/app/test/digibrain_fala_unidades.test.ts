/* DC3d da CONVERSA_PET: a paridade da subchave `fala_unidades` (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1 e o adendo 1, A1.1). As vidas do
   gabarito (test/gabaritos/digibrain_fala_unidades.json.gz, experiments/exportar_gabarito_fala_unidades.py): o laboratorio com a fala_unidades
   ligada (o LAB+F da DC3), no comedouro, os donos atencioso e relapso, cada um ignorando e atendendo a fala, sementes 101 a 505, 3 dias. O laco
   do TS (MotorCorpoMundo com a chave do laboratorio) rejoga o log do Python com o DigiBrain da CONFIG_DIGIBRAIN_LAB_FALA e confere, decisao a
   decisao, a acao, o motivo (com a consequencia: o r_n da fala e o do corpo da decisao seguinte) e a assinatura de cada modulo; no fim, o sha256
   do estado interno inteiro. As constantes da fala sao conferidas folha a folha. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { linhaDaOpcao } from "../motor/digibrain/plast.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_DIGIBRAIN_LAB_FALA, CONFIG_FALA_UNIDADES, CONTEUDOS_FALA, TERMO_DO_CONTEUDO } from "../motor/digibrain/constantes.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { assinar, conferir } from "./digibrain_modular_gabarito.ts";

const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;
interface DecisaoLeve { k: number; acao: string; assinatura: Record<string, string>; motivo: Record<string, any> }
interface VidaFala {
  dono: string; modo: string; lugar: string; semente: number; dias: number; decisoes: DecisaoLeve[]; falas: Record<string, number>;
  atendimentos: number | null; log: EventoCorpo[]; log_sha256: string; estado: string; assinatura_final: Record<string, string>;
}
const gab = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/digibrain_fala_unidades.json.gz", import.meta.url))).toString("utf8")) as {
  versao: number; braco: string; config_digibrain: Record<string, unknown>; conteudos_fala: string[]; termo_do_conteudo: string[][];
  config_fala_unidades: Record<string, number>; vidas: VidaFala[];
};

/** o `repr` do float do Python no JSON (o `u` do sorteio), como no G-PAR-VIDA do modular */
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

function viver(semente: number, log: readonly EventoCorpo[]): { cerebro: DigiBrain; assinaturas: Record<string, string>[] } {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB_FALA);
  const assinaturas: Record<string, string>[] = [];
  const agir = cerebro.agir.bind(cerebro);
  cerebro.agir = (obs, rng) => {
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  const m = new MotorCorpoMundo(cerebro, semente, CCO_CORPO_V11, estadoNascimentoPy(0), { paridade: true, cfgMundo: CMU_MVP, digibrain: true });
  for (const e of log) m.aplicarEvento(e);
  return { cerebro, assinaturas };
}

describe("DC3d: as constantes da fala_unidades sao as do Python", () => {
  test("a ConfigDigibrain da vida e a do laboratorio com a fala_unidades ligada; os conteudos, os termos e o ganho_conteudo", () => {
    expect(gab.versao).toBe(1);
    expect(gab.braco).toBe("LAB+F");
    expect(JSON.parse(JSON.stringify(CONFIG_DIGIBRAIN_LAB_FALA))).toEqual(gab.config_digibrain);
    expect({ ...CONFIG_DIGIBRAIN_LAB, fala_unidades: true }).toEqual(gab.config_digibrain);
    expect(CONFIG_DIGIBRAIN_LAB.fala_unidades).toBe(false);
    expect([...CONTEUDOS_FALA]).toEqual(gab.conteudos_fala);
    expect(TERMO_DO_CONTEUDO.map(t => [...t])).toEqual(gab.termo_do_conteudo);
    expect({ ...CONFIG_FALA_UNIDADES }).toEqual(gab.config_fala_unidades);
  });
  test("a linha de H da opcao: a do comportamento; com a fala_unidades, a do conteudo; fala sem conteudo falha alto", () => {
    expect(linhaDaOpcao(["chamar_atencao", null, null], false)).toBe("chamar_atencao");
    expect(linhaDaOpcao(["chamar_atencao", "higiene", null], true)).toBe("chamar_atencao/higiene");
    expect(linhaDaOpcao(["comer", "comida", 3], true)).toBe("comer");
    expect(() => linhaDaOpcao(["chamar_atencao", null, null], true)).toThrow(/sem conteudo/);
  });
});

describe("DC3d: as vidas com a fala_unidades no laco do TS, iguais ao Python", () => {
  test("o gabarito: 20 vidas (2 donos x ignora/atende x 5 sementes) de 288 decisoes, com falas dos tres conteudos", () => {
    expect(gab.vidas.length).toBe(20);
    expect(gab.vidas.every(v => v.decisoes.length === 288)).toBe(true);
    for (const c of CONTEUDOS_FALA) expect(gab.vidas.some(v => v.falas[c]! > 0), c).toBe(true);
    expect(gab.vidas.filter(v => v.modo === "atende").every(v => v.atendimentos! > 0)).toBe(true);
  });
  let total = 0, falas = 0;
  gab.vidas.forEach(g => {
    test(`${g.dono}/${g.modo}/${g.semente}: cada decisao (acao, motivo, assinatura) e o estado interno no fim`, () => {
      const v = viver(g.semente, g.log);
      expect(v.cerebro.motivos.length).toBe(g.decisoes.length);
      g.decisoes.forEach((d, k) => {
        conferir(`k=${k} acao`, v.cerebro.motivos[k]!["acao"], d.acao);
        conferir(`k=${k} motivo`, v.cerebro.motivos[k], d.motivo);
        conferir(`k=${k} assinatura`, v.assinaturas[k], d.assinatura);
      });
      expect(sha(textoPy(v.cerebro.estadoInterno())), "estado interno no fim").toBe(g.estado);
      conferir("assinatura final", Object.fromEntries(ASSINADOS.map(n => [n, assinar(v.cerebro[n].estadoInterno())])), g.assinatura_final);
      /* as unidades de fala: tres no lugar do chamar, a escolha com o conteudo e as tres linhas de H no lugar da do chamar */
      const ms = v.cerebro.motivos;
      expect(ms.every(m => (m["unidades"] as { chave: unknown[] }[]).filter(u => u.chave[0] === "chamar_atencao").map(u => u.chave[1]).join() === CONTEUDOS_FALA.join())).toBe(true);
      const daFala = ms.filter(m => m["acao"] === "chamar_atencao");
      expect(daFala.every(m => (CONTEUDOS_FALA as readonly unknown[]).includes((m["escolha"] as unknown[])[1]))).toBe(true);
      expect(Object.keys(v.cerebro.plast.H).filter(b => b.startsWith("chamar_atencao"))).toEqual(CONTEUDOS_FALA.map(c => `chamar_atencao/${c}`));
      total += g.decisoes.length; falas += daFala.length;
    });
  });
  test("a soma: 5 760 decisoes conferidas, com as falas", () => { expect(total).toBe(5760); expect(falas).toBeGreaterThan(0); });
});
