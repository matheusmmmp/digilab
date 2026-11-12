/* G-PAR do sono que segura (docs/TAREFA_V3_SONO_SEGURA.md): as vidas do Python com a ConfigSonoSegura ligada
   (test/gabaritos/digibrain_modular_sono_segura.json.gz, de experiments/exportar_gabarito_digibrain_modular.py --sono), rodadas pelo laco do TS
   (MotorCorpoMundo com o DigiBrain da chave do laboratorio e a CONFIG_SONO_SEGURA_LIGADA), decisao a decisao iguais ao Python: a acao, o motivo
   e a assinatura de cada modulo; no fim, a assinatura final e o sha256 do estado interno. O reflexo com a histerese, caso a caso; e a v27 do jogo,
   o ovo que nasce com a chave ligada. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP, VERSAO_PET, VERSAO_V25, VERSAO_V27, nasceComSonoSegura } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import { Arbitragem } from "../motor/digibrain/arb.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_SONO_SEGURA, CONFIG_SONO_SEGURA_LIGADA, INATOS_MODULAR, type ConfigSonoSegura } from "../motor/digibrain/constantes.ts";
import { Motor } from "../motor/motor.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { assinar, conferir } from "./digibrain_modular_gabarito.ts";

const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;
interface DecisaoLeve { k: number; assinatura: Record<string, string>; motivo: Record<string, any> }
interface VidaSono {
  dono: string; lugar: string; semente: number; log: EventoCorpo[]; decisoes: DecisaoLeve[]; estado: string; assinatura_final: Record<string, string>;
  difere_de_hoje: boolean; cochilos: number; reflexos: number;
}
const g = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/digibrain_modular_sono_segura.json.gz", import.meta.url))).toString("utf8")) as
  { config_sono_segura: ConfigSonoSegura; vidas: VidaSono[] };

/** o `repr` do float do Python (o `u` do sorteio) e o `_texto` do exportador, como no digibrain_modular_vida.test.ts */
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

function viver(semente: number, log: readonly EventoCorpo[], sono: ConfigSonoSegura) {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, sono);
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

describe("G-PAR-VIDA do sono que segura", () => {
  test("a CONFIG_SONO_SEGURA e a do Python (desligada por padrao; lambda_acordar acima de 0,9 S)", () => {
    expect(CONFIG_SONO_SEGURA_LIGADA).toEqual(g.config_sono_segura);
    expect(CONFIG_SONO_SEGURA).toEqual({ ...g.config_sono_segura, ligada: false });
    expect(CONFIG_SONO_SEGURA.lambda_acordar / INATOS_MODULAR.escala).toBeGreaterThan(0.9);
    expect(g.vidas.length).toBe(3);
    expect(g.vidas.every(v => v.difere_de_hoje)).toBe(true);
  });
  g.vidas.forEach(v => {
    test(`${v.lugar}/${v.dono}/${v.semente}: cada decisao (acao, motivo, assinatura) e o estado interno no fim`, () => {
      const r = viver(v.semente, v.log, CONFIG_SONO_SEGURA_LIGADA);
      expect(r.cerebro.motivos.length).toBe(v.decisoes.length);
      v.decisoes.forEach((d, k) => {
        conferir(`${v.dono} k=${k} acao`, r.cerebro.motivos[k]!["acao"], d.motivo["acao"]);
        conferir(`${v.dono} k=${k} motivo`, r.cerebro.motivos[k], d.motivo);
        conferir(`${v.dono} k=${k} assinatura`, r.assinaturas[k], d.assinatura);
      });
      conferir("assinatura final", Object.fromEntries(ASSINADOS.map(n => [n, assinar(r.cerebro[n].estadoInterno())])), v.assinatura_final);
      expect(sha(textoPy(r.cerebro.estadoInterno())), "estado interno no fim").toBe(v.estado);
      /* sem a chave, o mesmo log da outra vida */
      expect(sha(textoPy(viver(v.semente, v.log, CONFIG_SONO_SEGURA).cerebro.estadoInterno()))).not.toBe(v.estado);
    });
  });
});

describe("o reflexo do sono com a histerese (o espelho do tests/test_sono_segura.py)", () => {
  const S = INATOS_MODULAR.escala, URG = INATOS_MODULAR.urgencia_lambda;
  const sens = (energia: number, dormindo: boolean) => ({ leitura: { energia }, contexto: { noite: 0, dormindo: dormindo ? S : 0, sem_cuidado: 0 } });
  test("desligado, o de hoje", () => {
    const a = new Arbitragem(null, true, false);
    expect([a.reflexo(sens(255, false)), a.reflexo(sens(256, true)), a.reflexo(sens(900, true), { fome: 0 })]).toEqual([true, false, false]);
  });
  test("ligado: segura ate passar de 90 %, salvo a fome urgente", () => {
    const a = new Arbitragem(null, true, false, CONFIG_SONO_SEGURA_LIGADA);
    const calmo = { fome: URG }, urgente = { fome: URG + 1 };
    expect([a.reflexo(sens(255, false), calmo), a.reflexo(sens(255, true), urgente), a.reflexo(sens(256, false), calmo),
      a.reflexo(sens(921, true), calmo), a.reflexo(sens(922, true), calmo), a.reflexo(sens(600, true), urgente)])
      .toEqual([true, true, false, true, false, false]);
    expect(() => a.reflexo(sens(600, true))).toThrow(/urgencia da fome/);
  });
});

describe("a v27: o ovo novo de um pet so nasce com o sono que segura", () => {
  test("a versao e o modular dela", () => {
    expect(VERSAO_PET).toBe(33);
    expect([nasceComSonoSegura(VERSAO_V27), nasceComSonoSegura(VERSAO_V25)]).toEqual([true, false]);
    const novo = new Motor(101), antigo = new Motor(101, VERSAO_V25);
    for (const m of [novo, antigo]) { m.trocarCerebro("modular"); m.avancar(15); }
    expect(novo.modular?.arb.sono.ligada).toBe(true);
    expect(antigo.modular?.arb.sono.ligada).toBe(false);
  });
});
