/* O lance do dono no motor TS (docs/TAREFA_V3_BOLA_BRINCAR.md, BB2; o porte da BB1 do Python).
   - G-PAR do lance: as vidas do Python com o sono que segura e o lance ligados (test/gabaritos/digibrain_modular_lance_dono.json.gz, de
     experiments/exportar_gabarito_digibrain_modular.py --lance), rodadas pelo laco do TS (MotorCorpoMundo com o DigiBrain da chave do
     laboratorio, a CONFIG_SONO_SEGURA_LIGADA e a CONFIG_LANCE_DONO_LIGADA), decisao a decisao iguais ao Python: a acao, o motivo (com o
     `lance`) e a assinatura de cada modulo; no fim, a assinatura final, o sha256 do estado interno, os lances e as rolagens da bola.
   - a falha alta quando o motor e o cerebro divergem na chave. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import {
  CONFIG_DIGIBRAIN_LAB, CONFIG_LANCE_DONO, CONFIG_LANCE_DONO_LIGADA, CONFIG_SONO_SEGURA_LIGADA, INATOS_MODULAR, validarLanceDono,
  type ConfigLanceDono, type ConfigSonoSegura,
} from "../motor/digibrain/constantes.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { assinar, conferir } from "./digibrain_modular_gabarito.ts";

const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;
interface DecisaoLeve { k: number; assinatura: Record<string, string>; motivo: Record<string, any> }
interface VidaLance {
  dono: string; lugar: string; semente: number; log: EventoCorpo[]; decisoes: DecisaoLeve[]; estado: string; assinatura_final: Record<string, string>;
  difere_de_hoje: boolean; lances: Record<string, unknown>[]; rolagens: Record<string, unknown>[]; convites: number;
}
const g = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/digibrain_modular_lance_dono.json.gz", import.meta.url))).toString("utf8")) as
  { config_lance_dono: ConfigLanceDono; config_sono_segura: ConfigSonoSegura; ganchos: string[]; vidas: VidaLance[] };

/** o `repr` do float do Python (o `u` do sorteio) e o `_texto` do exportador, como no digibrain_modular_sono_segura.test.ts */
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

/** a vida do laboratorio pelo laco do TS: `lanceCerebro` e `lanceLaco` separados, para a falha alta da chave divergente */
function viver(semente: number, log: readonly EventoCorpo[], lanceCerebro: ConfigLanceDono = CONFIG_LANCE_DONO_LIGADA,
               lanceLaco: ConfigLanceDono | undefined = CONFIG_LANCE_DONO_LIGADA) {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, CONFIG_SONO_SEGURA_LIGADA, undefined, lanceCerebro);
  const assinaturas: Record<string, string>[] = [];
  const agir = cerebro.agir.bind(cerebro);
  cerebro.agir = (obs, rng) => {
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  const m = new MotorCorpoMundo(cerebro, semente, CCO_CORPO_V11, estadoNascimentoPy(0),
    { paridade: true, cfgMundo: CMU_MVP, digibrain: true, ...(lanceLaco === undefined ? {} : { lance: lanceLaco }) });
  for (const e of log) m.aplicarEvento(e);
  return { cerebro, assinaturas, motor: m };
}

describe("G-PAR do lance do dono (G-BB-3, a paridade com o Python)", () => {
  test("a CONFIG_LANCE_DONO e a do Python (desligada por padrao), e o gabarito exercita a chave", () => {
    expect(CONFIG_LANCE_DONO_LIGADA).toEqual(g.config_lance_dono);
    expect(CONFIG_LANCE_DONO).toEqual({ ...g.config_lance_dono, ligada: false });
    expect(CONFIG_SONO_SEGURA_LIGADA).toEqual(g.config_sono_segura);
    expect(CONFIG_LANCE_DONO.w_bola_do_dono).toBe(4 * INATOS_MODULAR.escala);
    expect(g.ganchos).toContain("bola_do_dono");
    expect(g.vidas.length).toBe(3);
    for (const v of g.vidas) expect([v.difere_de_hoje, v.lances.length > 0, v.convites > 0]).toEqual([true, true, true]);
    expect(() => validarLanceDono({ ...CONFIG_LANCE_DONO, lance_min_celulas: 4 })).toThrow(/lance_min_celulas/);
    expect(() => validarLanceDono({ ...CONFIG_LANCE_DONO, janela_convite_ticks: 0 })).toThrow(/inteiro positivo/);
  });
  g.vidas.forEach(v => {
    test(`${v.lugar}/${v.dono}/${v.semente}: cada decisao (acao, motivo, assinatura), o estado interno, os lances e as rolagens`, () => {
      const r = viver(v.semente, v.log);
      expect(r.cerebro.motivos.length).toBe(v.decisoes.length);
      v.decisoes.forEach((d, k) => {
        conferir(`${v.dono} k=${k} acao`, r.cerebro.motivos[k]!["acao"], d.motivo["acao"]);
        conferir(`${v.dono} k=${k} motivo`, r.cerebro.motivos[k], d.motivo);
        conferir(`${v.dono} k=${k} assinatura`, r.assinaturas[k], d.assinatura);
      });
      conferir("assinatura final", Object.fromEntries(ASSINADOS.map(n => [n, assinar(r.cerebro[n].estadoInterno())])), v.assinatura_final);
      expect(sha(textoPy(r.cerebro.estadoInterno())), "estado interno no fim").toBe(v.estado);
      conferir("lances", r.motor.mundo.lances, v.lances);
      conferir("rolagens", r.motor.mundo.rolagens, v.rolagens);
      expect(r.cerebro.motivos.filter(m => m["lance"]["bola_do_dono"]).length).toBe(v.convites);
    });
  });
});
