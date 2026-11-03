/* G-PAR-VIDA (LM4): as vidas inteiras do gabarito do DigiBrain modular, rodadas pelo laco do TS (MotorCorpoMundo com a chave do laboratorio) com o
   M-ADAPT (motor/digibrain/adapt.ts), decisao a decisao iguais ao Python: a acao, o motivo (o `cerebro.motivos[k]` ao fim da vida, com a
   consequencia) e a assinatura do estado de cada modulo logo depois do `agir`. O dono nao e refeito: o laco rejoga o log do motor do Python
   (digibrain_modular_logs.json.gz, as oito vidas da LM0; e o log de cada vida de digibrain_modular_fins.json.gz), como o G-PAR do laco com o mundo
   (mvp_mundo.test.ts). No fim da vida: o sha256 do estado interno inteiro do cerebro, o do Python. As seis vidas dos fins (`sumiu` e `desistiu`
   do M-ESTADO, que as oito da LM0 nao tem) rodam com os valores do proprio arquivo (a de `desistiu` com `n_desiste_cheiro = 2`). */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR } from "../motor/digibrain/constantes.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { assinar, conferir, vidasModular } from "./digibrain_modular_gabarito.ts";

const lerGz = <T>(rel: string): T => JSON.parse(gunzipSync(readFileSync(new URL(`./gabaritos/${rel}`, import.meta.url))).toString("utf8")) as T;
const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;

interface DecisaoLeve { k: number; assinatura: Record<string, string>; motivo: Record<string, any>; acao?: string }
interface VidaLog { dono: string; lugar: string; semente: number; log: EventoCorpo[]; log_sha256: string }
interface VidaFins extends VidaLog { inatos: Record<string, number>; decisoes: DecisaoLeve[]; fins: string[]; estado: string }

/** o `repr` do float do Python no JSON (o `u` do sorteio): a notacao cientifica abaixo de 1e-4, com o expoente de dois digitos */
function floatPy(x: number): string {
  if (x !== 0 && Math.abs(x) < 1e-4) {
    const [m, e] = x.toExponential().split("e");
    const n = Number(e);
    return `${m}e${n < 0 ? "-" : "+"}${String(Math.abs(n)).padStart(2, "0")}`;
  }
  return String(x);
}
/** o `_texto` do exportador (json.dumps sort_keys, separators) para o estado interno inteiro: so o `u` e float */
function textoPy(v: unknown, chave = ""): string {
  if (v === null || typeof v === "boolean") return String(v === null ? "null" : v);
  if (typeof v === "string") return JSON.stringify(v);
  if (typeof v === "number") return Number.isInteger(v) && chave !== "u" ? String(v) : floatPy(v) + (chave === "u" && Number.isInteger(v) ? "" : "");
  if (Array.isArray(v)) return `[${v.map(x => textoPy(x)).join(",")}]`;
  const o = v as Record<string, unknown>;
  return `{${Object.keys(o).sort().map(k => `${JSON.stringify(k)}:${textoPy(o[k], k)}`).join(",")}}`;
}
const sha = (t: string): string => createHash("sha256").update(t, "utf8").digest("hex");

interface Vivida { cerebro: DigiBrain; assinaturas: Record<string, string>[]; m: MotorCorpoMundo }
/** a vida no laco do TS: o log do Python aplicado a um MotorCorpoMundo com o DigiBrain e a chave do laboratorio ligada */
function viver(semente: number, log: readonly EventoCorpo[], inatos: typeof INATOS_MODULAR = INATOS_MODULAR): Vivida {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB, inatos);
  const assinaturas: Record<string, string>[] = [];
  const agir = cerebro.agir.bind(cerebro);
  cerebro.agir = (obs, rng) => {                         // a assinatura do estado depois do `agir`, como o Gravador do exportador
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  const m = new MotorCorpoMundo(cerebro, semente, CCO_CORPO_V11, estadoNascimentoPy(0), { paridade: true, cfgMundo: CMU_MVP, digibrain: true });
  for (const e of log) m.aplicarEvento(e);
  return { cerebro, assinaturas, m };
}

function conferirVida(nome: string, v: Vivida, decisoes: readonly DecisaoLeve[]): void {
  expect(v.cerebro.motivos.length, `${nome}: decisoes`).toBe(decisoes.length);
  expect(v.assinaturas.length).toBe(decisoes.length);
  decisoes.forEach((d, k) => {
    conferir(`${nome} k=${k} acao`, v.cerebro.motivos[k]!["acao"], d.motivo["acao"]);
    conferir(`${nome} k=${k} motivo`, v.cerebro.motivos[k], d.motivo);
    conferir(`${nome} k=${k} assinatura`, v.assinaturas[k], d.assinatura);
  });
}

describe("G-PAR-VIDA: as oito vidas do gabarito da LM0 no laco do TS com o modular", () => {
  const logs = lerGz<{ vidas: VidaLog[] }>("digibrain_modular_logs.json.gz").vidas;
  const vidas = vidasModular();
  test("o gabarito: oito vidas de 384 decisoes e os logs na mesma ordem, com o sha256 do Python", () => {
    expect(logs.length).toBe(8);
    expect(vidas.length).toBe(8);
    logs.forEach((l, i) => {
      expect([l.dono, l.lugar, l.semente]).toEqual([vidas[i]!.dono, vidas[i]!.lugar, vidas[i]!.semente]);
      expect(l.log_sha256).toBe((vidas[i] as any).log);
    });
  });
  let total = 0;
  vidas.forEach((g, i) => {
    test(`${g.lugar}/${g.dono}/${g.semente}: cada decisao (acao, motivo, assinatura) e o estado interno no fim`, () => {
      const v = viver(g.semente, logs[i]!.log);
      conferirVida(`${g.lugar}/${g.dono}/${g.semente}`, v, g.decisoes as unknown as DecisaoLeve[]);
      expect(sha(textoPy(v.cerebro.estadoInterno())), "estado interno no fim").toBe((g as any).estado);
      const final = Object.fromEntries(ASSINADOS.map(n => [n, assinar(v.cerebro[n].estadoInterno())]));
      conferir("assinatura final", final, (g as any).assinatura_final);
      total += g.decisoes.length;
    });
  });
  test("a soma: 3 072 decisoes conferidas", () => { expect(total).toBe(3072); });
});

describe("G-PAR-VIDA: as vidas dos fins sumiu e desistiu do M-ESTADO", () => {
  const fins = lerGz<{ vidas: VidaFins[] }>("digibrain_modular_fins.json.gz").vidas;
  const vistos = new Set<string>();
  fins.forEach(g => {
    test(`${g.lugar}/${g.dono}/${g.semente} (${JSON.stringify(g.inatos)}): cada decisao e o estado interno no fim`, () => {
      const inatos = { ...INATOS_MODULAR, ...g.inatos } as unknown as typeof INATOS_MODULAR;
      const v = viver(g.semente, g.log, inatos);
      conferirVida(`${g.lugar}/${g.dono}/${g.semente}`, v, g.decisoes);
      expect(sha(textoPy(v.cerebro.estadoInterno())), "estado interno no fim").toBe(g.estado);
      const motivos = new Set(v.cerebro.motivos.flatMap(m => (m["fins"] as { motivo: string }[]).map(f => f.motivo)));
      expect([...motivos].sort()).toEqual(g.fins);
      motivos.forEach(f => vistos.add(f));
    });
  });
  test("os dois fins que a LM2 deixou sem G-PAR aparecem nas vidas conferidas", () => {
    expect(vistos.has("sumiu")).toBe(true);
    expect(vistos.has("desistiu")).toBe(true);
    expect(fins.reduce((n, v) => n + v.decisoes.length, 0)).toBe(2304);
  });
});
