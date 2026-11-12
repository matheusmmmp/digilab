/* As duas regras do E1 da rodada de equilibrio do cuidado no motor TS (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, EQ-7; a ConfigEquilibrioCuidado).
   - G-PAR: as vidas do Python com o sono que segura, o lance e as duas regras ligadas (test/gabaritos/digibrain_modular_equilibrio_cuidado.json.gz,
     de experiments/exportar_gabarito_digibrain_modular.py --equilibrio), rodadas pelo laco do TS, decisao a decisao iguais ao Python: a acao,
     o motivo (com o `equilibrio`) e a assinatura de cada modulo; no fim, a assinatura final e o sha256 do estado interno. O pet e "bebe" nas
     primeiras `k_bebe` decisoes, como no exportador;
   - a falha alta do gancho e da config;
   - o ajuste do E1 no Motor do jogo (motor/equilibrio_e1.ts): desligado, os pets de hoje; ligado, o modular com as regras e os numeros. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { CMU_MVP, VERSAO_PET } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { DigiBrain } from "../motor/digibrain/adapt.ts";
import {
  CONFIG_DIGIBRAIN_LAB, CONFIG_EQUILIBRIO_CUIDADO, CONFIG_LANCE_DONO_LIGADA, CONFIG_SONO_SEGURA_LIGADA, INATOS_MODULAR, validarEquilibrioCuidado,
  type ConfigEquilibrioCuidado, type ConfigLanceDono, type ConfigSonoSegura,
} from "../motor/digibrain/constantes.ts";
import { AJUSTE_E1_DESLIGADO, AJUSTE_E1_PROPOSTO, inatosComAjuste, validarAjusteE1, type AjusteEquilibrioE1 } from "../motor/equilibrio_e1.ts";
import { Motor } from "../motor/motor.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { assinar, conferir } from "./digibrain_modular_gabarito.ts";

const ASSINADOS = ["sens", "afeto", "estado", "mem", "arb", "plast"] as const;
interface DecisaoLeve { k: number; assinatura: Record<string, string>; motivo: Record<string, any> }
interface VidaEq {
  dono: string; lugar: string; semente: number; log: EventoCorpo[]; decisoes: DecisaoLeve[]; estado: string; assinatura_final: Record<string, string>;
  difere_de_hoje: boolean; bebes: number; guardas: number;
}
const g = JSON.parse(gunzipSync(readFileSync(new URL("./gabaritos/digibrain_modular_equilibrio_cuidado.json.gz", import.meta.url))).toString("utf8")) as
  { config_lance_dono: ConfigLanceDono; config_sono_segura: ConfigSonoSegura; config_equilibrio_cuidado: ConfigEquilibrioCuidado; k_bebe: number;
    inatos_e1: { urgencia_lambda: number; vies_brincar: number }; vidas: VidaEq[] };
/** os inatos das vidas do gabarito: os do E1 (o urgencia_lambda e o vies do brincar propostos) */
const INATOS_E1 = inatosComAjuste(INATOS_MODULAR, AJUSTE_E1_PROPOSTO);

/** o `repr` do float do Python e o `_texto` do exportador, como no lance_dono.test.ts */
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

/** a vida do laboratorio pelo laco do TS, com o gancho do bebe antes de cada decisao (o pet e bebe nas primeiras `kBebe`) */
function viver(semente: number, log: readonly EventoCorpo[], ceq: ConfigEquilibrioCuidado, kBebe: number | null) {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_E1, false, CONFIG_SONO_SEGURA_LIGADA, undefined, CONFIG_LANCE_DONO_LIGADA, ceq);
  const assinaturas: Record<string, string>[] = [];
  const agir = cerebro.agir.bind(cerebro);
  cerebro.agir = (obs, rng) => {
    if (kBebe !== null) cerebro.estagioBebe(cerebro.k < kBebe);
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  const m = new MotorCorpoMundo(cerebro, semente, CCO_CORPO_V11, estadoNascimentoPy(0),
    { paridade: true, cfgMundo: CMU_MVP, digibrain: true, lance: CONFIG_LANCE_DONO_LIGADA });
  for (const e of log) m.aplicarEvento(e);
  return { cerebro, assinaturas };
}

describe("G-PAR das regras do E1 (a paridade com o Python)", () => {
  test("a config e a do Python, e o gabarito exercita as duas regras", () => {
    expect(g.config_equilibrio_cuidado).toEqual({ ...CONFIG_EQUILIBRIO_CUIDADO, guarda_fome_brincar: true, comer_bebe: true });
    expect(g.config_equilibrio_cuidado).toEqual(AJUSTE_E1_PROPOSTO.cerebro);
    expect(g.inatos_e1).toEqual({ urgencia_lambda: AJUSTE_E1_PROPOSTO.urgencia_lambda, vies_brincar: AJUSTE_E1_PROPOSTO.vies_brincar });
    expect(CONFIG_LANCE_DONO_LIGADA).toEqual(g.config_lance_dono);
    expect(CONFIG_SONO_SEGURA_LIGADA).toEqual(g.config_sono_segura);
    expect(g.vidas.length).toBe(3);
    for (const v of g.vidas) expect([v.difere_de_hoje, v.bebes]).toEqual([true, g.k_bebe]);
    expect(g.vidas.reduce((a, v) => a + v.guardas, 0)).toBeGreaterThan(0);
  });
  g.vidas.forEach(v => {
    test(`${v.lugar}/${v.dono}/${v.semente}: cada decisao (acao, motivo, assinatura) e o estado interno no fim`, () => {
      const r = viver(v.semente, v.log, g.config_equilibrio_cuidado, g.k_bebe);
      expect(r.cerebro.motivos.length).toBe(v.decisoes.length);
      v.decisoes.forEach((d, k) => {
        conferir(`${v.dono} k=${k} acao`, r.cerebro.motivos[k]!["acao"], d.motivo["acao"]);
        conferir(`${v.dono} k=${k} motivo`, r.cerebro.motivos[k], d.motivo);
        conferir(`${v.dono} k=${k} assinatura`, r.assinaturas[k], d.assinatura);
      });
      conferir("assinatura final", Object.fromEntries(ASSINADOS.map(n => [n, assinar(r.cerebro[n].estadoInterno())])), v.assinatura_final);
      expect(sha(textoPy(r.cerebro.estadoInterno())), "estado interno no fim").toBe(v.estado);
      expect(r.cerebro.motivos.filter(m => m["equilibrio"]["fome_urgente_sem_brincar"]).length).toBe(v.guardas);
      /* com a guarda, nenhuma decisao com a fome urgente brinca */
      expect(r.cerebro.motivos.filter(m => m["equilibrio"]["fome_urgente_sem_brincar"] && m["acao"] === "brincar")).toEqual([]);
    });
  });
});

describe("a falha alta", () => {
  const log = g.vidas[0]!.log;
  test("o modular com o bebe e sem o gancho", () => {
    expect(() => viver(101, log, { ...CONFIG_EQUILIBRIO_CUIDADO, comer_bebe: true }, null)).toThrow(/sem o gancho estagio_bebe/);
  });
  test("o gancho sem a regra, ou duas vezes", () => {
    const c = new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, CONFIG_SONO_SEGURA_LIGADA, undefined, CONFIG_LANCE_DONO_LIGADA);
    expect(() => c.estagioBebe(true)).toThrow(/comer_bebe ligada/);
    const d = new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, CONFIG_SONO_SEGURA_LIGADA, undefined, CONFIG_LANCE_DONO_LIGADA,
      { ...CONFIG_EQUILIBRIO_CUIDADO, comer_bebe: true });
    d.estagioBebe(true);
    expect(() => d.estagioBebe(false)).toThrow(/duas vezes/);
  });
  test("a config e o ajuste com campos errados", () => {
    expect(() => validarEquilibrioCuidado({ ...CONFIG_EQUILIBRIO_CUIDADO, w_comer_bebe: 0 })).toThrow(/inteiro positivo/);
    expect(() => validarAjusteE1({ ...AJUSTE_E1_DESLIGADO, lambda_acordar: 100 })).toThrow(/lambda_acordar/);
    expect(() => validarAjusteE1({ ...AJUSTE_E1_DESLIGADO, vies_brincar: 0.5 })).toThrow(/inteiro/);
  });
  test("desligada, o motivo nao ganha campo", () => {
    const r = viver(101, log.slice(0, 200), CONFIG_EQUILIBRIO_CUIDADO, null);
    expect(r.cerebro.motivos.every(m => !("equilibrio" in m))).toBe(true);
  });
});

describe("o ajuste do E1 no Motor do jogo (so a bancada)", () => {
  const ligado: AjusteEquilibrioE1 = {
    cerebro: { ...CONFIG_EQUILIBRIO_CUIDADO, guarda_fome_brincar: true, comer_bebe: true }, lambda_acordar: 900, urgencia_lambda: 600,
    vies_brincar: 0, w_bola_do_dono: 2048,
  };
  const novo = (aj: AjusteEquilibrioE1 | null) => {
    const m = new Motor(101, VERSAO_PET);
    if (aj !== null) m.ligarEquilibrioE1(aj);
    m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
    m.trocarCerebro("modular");
    m.avancar(240);
    return m;
  };
  test("desligado, o pet de hoje (o registro e o estado do cerebro)", () => {
    const hoje = novo(null), comAjusteVazio = new Motor(101, VERSAO_PET);
    comAjusteVazio.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
    comAjusteVazio.trocarCerebro("modular");
    comAjusteVazio.avancar(240);
    expect(JSON.stringify(comAjusteVazio.log)).toBe(JSON.stringify(hoje.log));
    expect(hoje.equilibrioE1).toBe(AJUSTE_E1_DESLIGADO);
    expect(hoje.modular!.ceq).toBe(CONFIG_EQUILIBRIO_CUIDADO);
  });
  test("ligado, o modular com as regras e os numeros; o registro nao muda de forma", () => {
    const m = novo(ligado), c = m.modular!;
    expect(c.ceq).toEqual(ligado.cerebro);
    expect([c.arb.sono.lambda_acordar, c.inatos.urgencia_lambda, c.cl.w_bola_do_dono]).toEqual([900, 600, 2048]);
    expect(c.inatos.w0.find(([b]) => b === "brincar")![1].find(([k]) => k === "vies")![1]).toBe(0);
    expect(c.motivos.slice(0, 5).every(mo => mo["equilibrio"]["bebe"] === INATOS_MODULAR.escala)).toBe(true);   // o ovo nasce bebe
    expect(m.log.some(e => (e as unknown[])[1] === "e1")).toBe(false);
  });
  test("so antes do modular e so nos pets de cerebro trocavel", () => {
    const m = novo(null);
    expect(() => m.ligarEquilibrioE1(ligado)).toThrow(/antes da primeira troca/);
    expect(() => new Motor(101, 16).ligarEquilibrioE1(ligado)).toThrow(/cerebro trocavel/);
  });
});
