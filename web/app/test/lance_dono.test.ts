/* O lance do dono no motor TS (docs/TAREFA_V3_BOLA_BRINCAR.md, BB2; o porte da BB1 do Python).
   - G-PAR do lance: as vidas do Python com o sono que segura e o lance ligados (test/gabaritos/digibrain_modular_lance_dono.json.gz, de
     experiments/exportar_gabarito_digibrain_modular.py --lance), rodadas pelo laco do TS (MotorCorpoMundo com o DigiBrain da chave do
     laboratorio, a CONFIG_SONO_SEGURA_LIGADA e a CONFIG_LANCE_DONO_LIGADA), decisao a decisao iguais ao Python: a acao, o motivo (com o
     `lance`) e a assinatura de cada modulo; no fim, a assinatura final, o sha256 do estado interno, os lances e as rolagens da bola.
   - a falha alta quando o motor e o cerebro divergem na chave;
   - as versoes (BB-7, D-BB2-1): a v30 (a v27 com o lance, o ovo de um pet) e a v31 (a v29 com ele, o grupo do brasao);
   - a medida no motor do jogo: o G-BB-1 e o G-BB-2 com o roteiro da BB1, na v30 com o modular, sementes 101, 202 e 303 (a tabela no console);
   - o replay da v30 e do grupo v31, e os grupos v28 e v29 sem o lance. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import {
  CMU_MVP, TPD, VERSAO_GRUPO, VERSAO_PET, VERSAO_V27, VERSAO_V28, VERSAO_V29, VERSAO_V30, VERSAO_V31, VERSAO_V32, VERSOES_PET, ehCerebroTrocavel, ehDoGrupo,
  ehLutaLp6, ehLutaPoc, ehLutaV23, nasceComLance, nasceComMemoriaLonga, nasceComSonoSegura, nasceComTv, nasceNaGrande,
} from "../motor/constantes.ts";
import { LUTA_V23, LUTA_V29, tabelaLuta } from "../motor/luta_poc.ts";
import { Motor } from "../motor/motor.ts";
import { GrupoDoJogo } from "../motor/grupo_jogo.ts";
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
               lanceLaco: ConfigLanceDono | null = CONFIG_LANCE_DONO_LIGADA) {
  const cerebro = new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, CONFIG_SONO_SEGURA_LIGADA, undefined, lanceCerebro);
  const assinaturas: Record<string, string>[] = [];
  const agir = cerebro.agir.bind(cerebro);
  cerebro.agir = (obs, rng) => {
    const a = agir(obs, rng);
    assinaturas.push(Object.fromEntries(ASSINADOS.map(n => [n, assinar(cerebro[n].estadoInterno())])));
    return a;
  };
  const m = new MotorCorpoMundo(cerebro, semente, CCO_CORPO_V11, estadoNascimentoPy(0),
    { paridade: true, cfgMundo: CMU_MVP, digibrain: true, ...(lanceLaco === null ? {} : { lance: lanceLaco }) });
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

describe("a chave divergente entre o laco e o cerebro falha alto", () => {
  const log = g.vidas[0]!.log;
  test("o laco com o lance e o modular sem ele: o gancho recusa o convite", () => {
    expect(() => viver(101, log, CONFIG_LANCE_DONO, CONFIG_LANCE_DONO_LIGADA)).toThrow(/exige a ConfigLanceDono ligada no cerebro/);
  });
  test("o modular com o lance e o laco sem ele: a decisao sem o gancho", () => {
    expect(() => viver(101, log, CONFIG_LANCE_DONO_LIGADA, null)).toThrow(/sem o gancho bola_do_dono/);
  });
  test("o gancho duas vezes antes da mesma decisao", () => {
    const c = new DigiBrain(CONFIG_DIGIBRAIN_LAB, INATOS_MODULAR, false, CONFIG_SONO_SEGURA_LIGADA, undefined, CONFIG_LANCE_DONO_LIGADA);
    c.bolaDoDono(false);
    expect(() => c.bolaDoDono(true)).toThrow(/duas vezes/);
  });
  test("desligado nos dois, nem o fluxo nem o registro nem o campo do motivo", () => {
    const r = viver(101, log, CONFIG_LANCE_DONO, null);
    expect([r.motor.lance, r.motor.mundo.lances, r.motor.mundo.comum.rngLance]).toEqual([null, null, null]);
    expect("lances" in r.motor.mundo.resumo()).toBe(false);
    expect(r.cerebro.motivos.some(m => "lance" in m)).toBe(false);
    expect(() => r.motor.conviteAtivo()).toThrow(/sem a ConfigLanceDono/);
  });
});

// ================================================================== o jogo: a v30, a v31 e as versoes de antes
/** o roteiro do dono que brinca da BB1 (tests/gabarito_lance_dono.py): a vida anda de 30 em 30 ticks; a cada 6 h de jogo a racao no comedouro e
 *  a cada 2 h o Brincar. As horas contam do nascimento (o tick de nascimento do jogo nao e 0) */
const PASSO = 30, BRINCAR_A_CADA = 120, RACAO_A_CADA = 360, DIAS = 3;
function roteiroJogo(m: Motor, dias = DIAS): Motor {
  for (let i = 1; i <= dias * TPD / PASSO; i++) {
    m.avancar(PASSO);
    const t = i * PASSO;
    if (t % RACAO_A_CADA === 0) m.deixarComida("racao", ...m.mundo!.comedouro);
    if (t % BRINCAR_A_CADA === 0) m.observar("brincar");
  }
  return m;
}
const laco = (m: Motor): MotorCorpoMundo => m.v11!.laco as MotorCorpoMundo;

interface LinhaMedida {
  semente: number; lances: number; elegiveis: number; chutes: number; recusas: number; comReflexo: number; comFome: number;
  decReflexo: number; decFome: number; chutesReflexo: number; chutesFome: number;
}
/** a medida da BB1 (tests/test_lance_dono.py, `medida`) no motor do jogo: os lances com decisao depois deles; os elegiveis (a primeira decisao
 *  do lance, no mesmo tick, sem o reflexo do sono e sem a fome urgente); os chutes na janela (uma rolagem da bola entre o lance e o fim da
 *  janela) e as recusas; e, nas decisoes da janela com o reflexo ou a fome urgente, quantas sao e quantas chutam (o G-BB-2) */
function medir(m: Motor): Omit<LinhaMedida, "semente"> {
  const c = m.modular!, ticks = laco(m).acoesPet.map(([t]) => t), rol = m.mundo!.rolagens.map(r => r["tick"] as number);
  if (c.motivos.length !== ticks.length) throw new Error("o modular nao decidiu a vida inteira");
  const janela = CONFIG_LANCE_DONO_LIGADA.janela_convite_ticks;
  const l = { lances: 0, elegiveis: 0, chutes: 0, recusas: 0, comReflexo: 0, comFome: 0, decReflexo: 0, decFome: 0, chutesReflexo: 0, chutesFome: 0 };
  for (const lance of m.mundo!.lances!) {
    const t = lance.tick, k = ticks.indexOf(t);
    if (k < 0) continue;                                 // o ultimo Brincar da vida, sem decisao depois
    const mo = c.motivos[k]!;
    if (!mo["lance"]["convite"]) throw new Error(`a decisao do lance (tick ${t}) sem o convite`);
    l.lances++;
    const chutou = rol.some(r => t <= r && r < t + janela);
    if (mo["reflexo"]) l.comReflexo++;
    else if (mo["lance"]["fome_urgente"]) l.comFome++;
    else { l.elegiveis++; if (chutou) l.chutes++; else l.recusas++; }
  }
  ticks.forEach((t, k) => {
    const mo = c.motivos[k]!;
    if (!mo["lance"]["convite"] || !(mo["reflexo"] || mo["lance"]["fome_urgente"])) return;
    if (mo["reflexo"]) l.decReflexo++; else l.decFome++;
    if (rol.includes(t)) { if (mo["reflexo"]) l.chutesReflexo++; else l.chutesFome++; }
  });
  return l;
}
const vidaV30 = new Map<number, Motor>();
function v30(semente: number): Motor {
  if (!vidaV30.has(semente)) {
    const m = new Motor(semente, VERSAO_V30);
    m.trocarCerebro("modular");
    vidaV30.set(semente, roteiroJogo(m));
  }
  return vidaV30.get(semente)!;
}

describe("as versoes (BB-7): a v30 e a v27 com o lance, a v31 e a v29 com ele", () => {
  test("o ovo de um pet nasce v32 (a TV, sem o lance; D-BB2-6) e o do brasao choca o grupo v31; os predicados", () => {
    expect([VERSAO_PET, VERSAO_GRUPO]).toEqual([VERSAO_V32, VERSAO_V31]);
    expect(VERSOES_PET.slice(-3)).toEqual([30, 31, 32]);
    for (const v of [21, 22, 23, 24, 25, 26, 27, 28, 29, 32]) expect(nasceComLance(v), `v${v}`).toBe(false);
    expect([nasceComTv(30), nasceComTv(31), nasceComTv(32)]).toEqual([false, false, true]);
    expect([nasceComLance(30), nasceComLance(31), ehDoGrupo(30), ehDoGrupo(31)]).toEqual([true, true, false, true]);
    for (const v of [30, 31]) {
      expect([ehCerebroTrocavel(v), ehLutaPoc(v), ehLutaV23(v), nasceNaGrande(v), nasceComMemoriaLonga(v), nasceComSonoSegura(v)], `v${v}`)
        .toEqual([true, true, true, true, true, true]);
    }
    expect([ehLutaLp6(30), ehLutaLp6(31)]).toEqual([false, true]);
    expect(tabelaLuta(30)).toBe(LUTA_V23);
    expect(tabelaLuta(31)).toBe(LUTA_V29);
  });
  test("a v30 nasce com o lance no laco e no modular; a v27, sem", () => {
    const novo = new Motor(101, VERSAO_V30), antigo = new Motor(101, VERSAO_V27);
    for (const m of [novo, antigo]) { m.trocarCerebro("modular"); m.avancar(15); m.observar("brincar"); m.avancar(1); }
    expect([laco(novo).lance, novo.modular!.cl.ligada, novo.mundo!.lances!.length]).toEqual([CONFIG_LANCE_DONO_LIGADA, true, 1]);
    expect([laco(antigo).lance, antigo.modular!.cl.ligada, antigo.mundo!.lances]).toEqual([null, false, null]);
    expect(novo.modular!.ultimoMotivo!["lance"]["convite"]).toBe(true);
    expect("lance" in antigo.modular!.ultimoMotivo!).toBe(false);
  });
  test("BB-3: o modular da v30 decide no tick do Brincar; BB-6: com o cerebro A, so a bola se mexe", () => {
    for (const cerebro of ["modular", "a"] as const) {
      const m = new Motor(202, VERSAO_V30);
      m.trocarCerebro(cerebro);
      m.avancar(20);
      const t = m.e.tick, antes = laco(m).proximaDecisao, bola = m.mundo!.bolaEm(t);
      expect(antes).toBeGreaterThan(t);
      m.observar("brincar");
      expect(m.mundo!.lances!.length).toBe(1);
      expect(m.mundo!.bolaEm(t)).not.toEqual(bola);
      expect(laco(m).proximaDecisao, cerebro).toBe(cerebro === "modular" ? t : antes);
      expect(laco(m).conviteAtivo()).toBe(true);
    }
  });
});

describe("a medida no motor do jogo (o roteiro da BB1, a v30 com o modular, 3 dias)", () => {
  /* G-BB-2 no jogo (D-BB2-3): com o reflexo do sono, nenhum chute; com a fome urgente, o convite vale 0, mas o pet ainda pode escolher o
     brincar sozinho com a bola perto: 1 chute em 43 decisoes da janela com a fome urgente (a semente 303, tick 3720). O Python (o mundo do
     laboratorio) deu 0 em 276. O teste fixa o numero medido, para uma mudanca aparecer */
  test("G-BB-1 (pelo menos 8 chutes em 10 lances elegiveis) e G-BB-2 (com o reflexo, nenhum chute; com a fome urgente, o medido)", () => {
    const linhas: LinhaMedida[] = [101, 202, 303].map(s => ({ semente: s, ...medir(v30(s)) }));
    console.log(["semente | lances | elegiveis | chutes na janela | recusas | lance com reflexo | lance com fome urgente | decisoes com reflexo | com fome urgente | chutes com reflexo | chutes com fome urgente",
      ...linhas.map(l => [l.semente, l.lances, l.elegiveis, l.chutes, l.recusas, l.comReflexo, l.comFome, l.decReflexo, l.decFome, l.chutesReflexo, l.chutesFome].join(" | "))].join("\n"));
    const chutes = linhas.reduce((a, l) => a + l.chutes, 0), elegiveis = linhas.reduce((a, l) => a + l.elegiveis, 0);
    console.log(`G-BB-1: ${chutes}/${elegiveis} = ${(chutes / elegiveis).toFixed(3)}`);
    expect(elegiveis).toBeGreaterThan(20);
    expect(chutes / elegiveis).toBeGreaterThanOrEqual(0.8);
    expect(linhas.map(l => l.chutesReflexo)).toEqual([0, 0, 0]);
    expect(linhas.map(l => l.chutesFome)).toEqual([0, 0, 1]);
  }, 600_000);
});

describe("o replay (G-BB-3 no jogo) e o grupo", () => {
  test("Motor.reproduzir refaz a vida v30 com os lances", () => {
    const m = v30(101), r = Motor.reproduzir(101, m.log, VERSAO_V30);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.mundo!.lances).toEqual(m.mundo!.lances);
    expect(r.modular!.motivos).toEqual(m.modular!.motivos);
  }, 600_000);
  test("o grupo v31: cada pet joga e recebe o lance dele no mundo de todos, e o replay o refaz", () => {
    const gr = new GrupoDoJogo(101, VERSAO_V31);
    for (const i of gr.ids) gr.agir(i, m => m.trocarCerebro("modular"));
    for (let p = 1; p <= TPD / PASSO; p++) {
      gr.avancar(PASSO);
      if ((p * PASSO) % BRINCAR_A_CADA === 0) for (const i of gr.ids) gr.agir(i, m => m.observar("brincar"));
    }
    const [a, b] = gr.ids.map(i => gr.motor(i));
    expect(a!.mundo!.comum).toBe(b!.mundo!.comum);
    const lances = a!.mundo!.lances!;
    expect(lances.length).toBe(2 * (TPD / BRINCAR_A_CADA));
    for (const m of [a!, b!]) {
      expect(laco(m).lance).toEqual(CONFIG_LANCE_DONO_LIGADA);
      expect(m.modular!.motivos.some(mo => mo["lance"]["bola_do_dono"] > 0)).toBe(true);
    }
    const r = GrupoDoJogo.reproduzir(gr.semente, VERSAO_V31, gr.log);
    expect(r.assinatura()).toBe(gr.assinatura());
    expect(r.motor(gr.ids[0]!).mundo!.lances).toEqual(lances);
  }, 600_000);
  test("o grupo v28 e o v29 seguem sem o lance: o Brincar nao mexe a bola", () => {
    for (const v of [VERSAO_V28, VERSAO_V29]) {
      const gr = new GrupoDoJogo(202, v);
      for (const i of gr.ids) gr.agir(i, m => m.trocarCerebro("modular"));
      gr.avancar(20);
      const i0 = gr.ids[0]!, bola = gr.motor(i0).mundo!.bolaEm(gr.motor(i0).e.tick);
      gr.agir(i0, m => m.observar("brincar"));
      const m = gr.motor(i0);
      expect([laco(m).lance, m.mundo!.lances, m.mundo!.comum.rngLance], `v${v}`).toEqual([null, null, null]);
      expect(m.mundo!.bolaEm(m.e.tick)).toEqual(bola);
      expect(m.modular!.cl.ligada).toBe(false);
    }
  });
});
