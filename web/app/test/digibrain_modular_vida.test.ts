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
import { CCO_CORPO_V11, CONFIG_LUTA_CORPO_LIGADA } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { CONFIG_DIGIBRAIN_LAB, D_MAX_ILHA_GRANDE, INATOS_MODULAR } from "../motor/digibrain/constantes.ts";
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

interface Vivida { cerebro: DigiBrain; assinaturas: Record<string, string>[]; m: MotorCorpoMundo; dores: { tick: number; vida_perdida_s: number; dor_antes: number; dor_depois: number }[] }
/** a vida no laco do TS: o log do Python aplicado a um MotorCorpoMundo com o DigiBrain e a chave do laboratorio ligada */
function viver(semente: number, log: readonly EventoCorpo[], inatos: typeof INATOS_MODULAR = INATOS_MODULAR, luta = false, antesDe?: (c: DigiBrain, k: number) => void): Vivida {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB, inatos, luta);
  let decisao = 0;                                       // (IG6) `antesDe`: chamado logo antes de cada decisao, com o numero dela
  const assinaturas: Record<string, string>[] = [];
  const agir = cerebro.agir.bind(cerebro);
  cerebro.agir = (obs, rng) => {                         // a assinatura do estado depois do `agir`, como o Gravador do exportador
    antesDe?.(cerebro, decisao++);
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  const m = new MotorCorpoMundo(cerebro, semente, CCO_CORPO_V11, estadoNascimentoPy(0), { paridade: true, cfgMundo: CMU_MVP, digibrain: true });
  const dores: Vivida["dores"] = [];
  if (luta) {                                            // a ponte da luta (PE3): a dor no corpo e o resumo ao modular; a dor de cada resumo, antes e depois
    m.corpo.luta = CONFIG_LUTA_CORPO_LIGADA;
    const original = m.corpo.estimuloLuta.bind(m.corpo);
    m.corpo.estimuloLuta = (v: number) => { const antes = m.corpo.q["dor"]!; original(v); dores.push({ tick: m.estado.tick, vida_perdida_s: v, dor_antes: antes, dor_depois: m.corpo.q["dor"]! }); };
  }
  for (const e of log) m.aplicarEvento(e);
  return { cerebro, assinaturas, m, dores };
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

interface VidaLuta extends VidaLog { decisoes: DecisaoLeve[]; estado: string; dores: Vivida["dores"]; episodios_luta: number; assinatura_final: Record<string, string> }
describe("G-PAR-VIDA (PE3 da ponte da luta): o corpo e o M-MEM com o resumo da luta, `lt`, nas vidas do Python", () => {
  const vidas = lerGz<{ vidas: VidaLuta[] }>("digibrain_modular_luta.json.gz").vidas;
  vidas.forEach(g => {
    test(`${g.lugar}/${g.dono}/${g.semente}: a dor de cada resumo, cada decisao (acao, motivo com as lutas, assinatura) e o estado interno no fim`, () => {
      expect(g.log.filter(e => e.tipo === "lt").length).toBe(6);
      const v = viver(g.semente, g.log, INATOS_MODULAR, true);
      conferir(`${g.lugar} dores`, v.dores, g.dores);
      conferirVida(`${g.lugar}/${g.dono}/${g.semente}`, v, g.decisoes);
      expect(sha(textoPy(v.cerebro.estadoInterno())), "estado interno no fim").toBe(g.estado);
      const final = Object.fromEntries(ASSINADOS.map(n => [n, assinar(v.cerebro[n].estadoInterno())]));
      conferir("assinatura final", final, g.assinatura_final);
      const eps = v.cerebro.mem.guardados().filter(e => e.origem === "luta");
      expect(eps.length).toBe(g.episodios_luta);
      expect(eps.length).toBeGreaterThanOrEqual(2);
      expect(eps.every(e => e.outro === e.classe && e.acao[0] === "lutar" && e.dono.length === 0)).toBe(true);
    });
  });
  test("a vida de hoje: sem a chave o resumo da luta levanta erro (o corpo e o DigiBrain)", () => {
    const g = vidas[0]!;
    expect(() => viver(g.semente, g.log, INATOS_MODULAR, false)).toThrow(/ConfigLutaCorpo/);
    const c = new DigiBrain();
    expect(() => c.receberLuta("muralha", -1, 400, 30)).toThrow(/luta_memoria/);
  });
});

/* IG6 da ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12.16): o G-PAR do M-MEM com o alcance da memoria de 128 celulas (o `d_max` de
   2 048, D_MAX_ILHA_GRANDE). O arquivo e o digibrain_modular_alcance.json.gz (experiments/exportar_gabarito_digibrain_modular.py --alcance),
   no molde do dos fins: vidas nascidas com o alcance novo. O Python confere que cada uma difere da mesma vida com o alcance de hoje */
describe("G-PAR-VIDA: as vidas com a memoria de 128 celulas (IG6)", () => {
  type VidaAlcance = VidaFins & { difere_de_hoje: boolean; troca_na_decisao?: number; difere_do_ovo?: boolean };
  const todas = lerGz<{ vidas: VidaAlcance[] }>("digibrain_modular_alcance.json.gz").vidas;
  const vidas = todas.filter(v => v.troca_na_decisao === undefined), noMeio = todas.filter(v => v.troca_na_decisao !== undefined);
  test("o arquivo: tres vidas que nascem com o d_max da ilha grande e duas que o recebem no meio, todas diferentes das de hoje", () => {
    expect(D_MAX_ILHA_GRANDE).toBe(2 * INATOS_MODULAR.d_max);
    expect(vidas.map(v => [v.inatos, v.difere_de_hoje])).toEqual([[{ d_max: D_MAX_ILHA_GRANDE }, true], [{ d_max: D_MAX_ILHA_GRANDE }, true], [{ d_max: D_MAX_ILHA_GRANDE }, true]]);
    expect(noMeio.map(v => [v.inatos, v.troca_na_decisao, v.difere_de_hoje])).toEqual([[{}, 150, true], [{}, 1, true]]);
    expect(noMeio[0].difere_do_ovo).toBe(true);          /* a troca na decisao 150 da outra vida que a de quem nasceu com o alcance */
    expect(todas.reduce((n, v) => n + v.decisoes.length, 0)).toBe(1920);
  });
  /* a troca no meio da vida (o evento "ma" dos pets vivos do jogo; o DigiBrain.alcance_da_memoria do Python): a vida nasce com o alcance
     de hoje e o recebe logo antes da decisao `troca_na_decisao` */
  noMeio.forEach(g => {
    test(`${g.lugar}/${g.dono}/${g.semente}, a troca antes da decisao ${g.troca_na_decisao}: cada decisao e o estado interno no fim`, () => {
      const v = viver(g.semente, g.log, INATOS_MODULAR, false, (c, k) => { if (k === g.troca_na_decisao) c.alcanceDaMemoria(D_MAX_ILHA_GRANDE); });
      conferirVida(`${g.lugar}/${g.dono}/${g.semente}`, v, g.decisoes);
      expect(sha(textoPy(v.cerebro.estadoInterno())), "estado interno no fim").toBe(g.estado);
      expect([v.cerebro.inatos.d_max, v.cerebro.mem.p.d_max]).toEqual([D_MAX_ILHA_GRANDE, D_MAX_ILHA_GRANDE]);
      /* sem a troca, a vida e outra */
      expect(sha(textoPy(viver(g.semente, g.log, INATOS_MODULAR).cerebro.estadoInterno()))).not.toBe(g.estado);
    });
  });
  vidas.forEach(g => {
    test(`${g.lugar}/${g.dono}/${g.semente} (${JSON.stringify(g.inatos)}): cada decisao e o estado interno no fim`, () => {
      const inatos = { ...INATOS_MODULAR, ...g.inatos } as unknown as typeof INATOS_MODULAR;
      const v = viver(g.semente, g.log, inatos);
      conferirVida(`${g.lugar}/${g.dono}/${g.semente}`, v, g.decisoes);
      expect(sha(textoPy(v.cerebro.estadoInterno())), "estado interno no fim").toBe(g.estado);
      /* a mesma vida com o alcance de hoje da outro estado: o arquivo exercita mesmo o d_max */
      expect(sha(textoPy(viver(g.semente, g.log, INATOS_MODULAR).cerebro.estadoInterno()))).not.toBe(g.estado);
      /* e o alcance trocado no meio da vida (o `alcanceDaMemoria` logo no comeco) da a mesma vida de quem nasceu com ele */
      const meio = viver(g.semente, g.log, INATOS_MODULAR, false, (c, k) => { if (k === 0) c.alcanceDaMemoria(D_MAX_ILHA_GRANDE); });
      expect(sha(textoPy(meio.cerebro.estadoInterno()))).toBe(g.estado);
    });
  });
});
