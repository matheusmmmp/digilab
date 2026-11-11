/* O sacudir a arvore (docs/TAREFA_V3_ARVORE_SACODE.md, S2): o porte do S1 do Python para o motor em TS, sem tela e sem versao de pet
   (D-AS-S2-1). O espelho do tests/test_arvore_sacode.py.
     - o formato do log (eventoSacudirArvore, lerSacudirArvore): os mesmos casos do Python;
     - o mundo da ilha (CMU_ILHA) e a ConfigSacudir: os do gabarito, campo a campo;
     - o G-PAR do laco: o TS refaz o gabarito do Python (test/gabaritos/arvore_sacode_python.json,
       experiments/exportar_gabarito_arvore_sacode.py) decisao a decisao e bit a bit no Node, pelo laco gravado (test/laco_gravado.ts), com
       as chaves dos ovos do gabarito ligadas: o log, os registros do mundo (quedas, sacudidas, consumos), o estado a cada decisao, o
       corpo e o estado no fim, os proximos sorteios de cada fluxo e o estado do fluxo `arvore-sacode`;
     - o laco: o sacudir nao e cuidado (AS-1), vale dormindo, o id fora do layout e a chave desligada falham alto, a queda natural nao muda,
       e o evento refaz no replay;
     - o Motor do jogo: nenhuma versao de pet tem o "sa" (VERSOES_COM_SACUDIR vazia): o sacudirArvore e o replay falham alto. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import {
  CMU, CMU_ILHA, CMU_MVP, CONFIG_SACUDIR, CONFIG_SACUDIR_LIGADA, LAYOUT_MUNDO_MVP, VERSOES_COM_SACUDIR, VERSOES_PET, validarSacudir,
  type ConfigSacudir,
} from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { Motor } from "../motor/motor.ts";
import { estadoNascimentoPy, type EventoCorpo } from "../motor/motor_corpo.ts";
import { MotorCorpoMundo, type OpcoesLacoMundo } from "../motor/motor_corpo_mundo.ts";
import { MundoPartilhado, eventoSacudirArvore, lerSacudirArvore } from "../motor/mundo.ts";
import type { EventoRegistro } from "../motor/tipos.ts";
import { LacoGravado, cerebroDa, json, ler, type Rec, type Vida } from "./laco_gravado.ts";

const { texto, g: G } = ler("./gabaritos/arvore_sacode_python.json");
const SHA = "be3d5ebc7363fb2ee819b8acf9c37649b85a00d5176bacd7448550c9a69ecefb";
type Proximos = { random: number[]; randrange16: number[] };
type VidaSacode = Vida & {
  dormindo_em: number[]; sacudidas: number; caidas: number; frutas_comidas: number; no_galho_fim: Record<string, number>;
  proximos_sacode: Proximos;
};
const VIDAS = G.vidas as VidaSacode[];
const CONFIG = G.config as unknown as { mundo: Rec; sacudir: Rec; roteiro: Rec };
/** as chaves dos ovos do gabarito (D-AS-S1-6): a decisao na comida, a bola no golpe, o sacudir e a fruta como comida */
const CHAVES: OpcoesLacoMundo = { cfgMundo: CMU_ILHA, decidirNaComida: true, bolaNoGolpe: true, sacudir: CONFIG_SACUDIR_LIGADA, frutaComoComida: true };
const proximos = (r: { random(): number; randrange(n: number): number }): Proximos =>
  ({ random: [r.random(), r.random(), r.random()], randrange16: [r.randrange(1 << 16), r.randrange(1 << 16), r.randrange(1 << 16)] });

describe("o formato do log do sacudir (os casos do Python)", () => {
  test("o id e de letras e digitos ASCII, de 1 a 16", () => {
    expect(eventoSacudirArvore(9, "J1")).toEqual({ tick: 9, tipo: "sacudir_arvore", valor: "J1" });
    expect(lerSacudirArvore({ tipo: "sacudir_arvore", valor: "M6" })).toBe("M6");
    expect(eventoSacudirArvore(9, "A".repeat(16)).valor).toBe("A".repeat(16));
    for (const v of ["", " J1", "J1 ", "J-1", "J|1", "J1\n", "á", "A".repeat(17), 1, null, true, undefined]) {
      expect(() => eventoSacudirArvore(9, v), JSON.stringify(v)).toThrow(/sacudir_arvore/);
      expect(() => lerSacudirArvore({ tipo: "sacudir_arvore", valor: v }), JSON.stringify(v)).toThrow(/sacudir_arvore/);
    }
    expect(() => lerSacudirArvore({ tipo: "deixar_bola", valor: "1|1" })).toThrow(/nao e sacudir_arvore/);
  });
});

describe("o mundo da ilha e a ConfigSacudir", () => {
  test("o CMU_ILHA e o do gabarito, campo a campo: o MVP com J1, J2 e J3 na casa", () => {
    expect(json(CMU_ILHA)).toEqual(CONFIG.mundo);
    expect(json({ ...CMU_ILHA, layout: LAYOUT_MUNDO_MVP })).toEqual(json(CMU_MVP));
    expect(CMU_MVP.layout.arvores).toEqual([]);                   // o mundo dos pets de hoje nao muda
    expect(CMU_ILHA.layout.arvores.every(([, x]) => x <= 15)).toBe(true);
  });
  test("a ConfigSacudir e a do Python, e a invalida falha alto", () => {
    expect(json(CONFIG_SACUDIR_LIGADA)).toEqual(CONFIG.sacudir);
    expect(CONFIG_SACUDIR).toEqual({ ...CONFIG_SACUDIR_LIGADA, ligada: false });
    for (const ruim of [{ ligada: 1 }, { galho_max: 0 }, { galho_max: 2.5 }, { recarga_galho_min: 0 }, { recarga_galho_min: true }])
      expect(() => validarSacudir({ ...CONFIG_SACUDIR_LIGADA, ...ruim } as unknown as ConfigSacudir), JSON.stringify(ruim)).toThrow(/ConfigSacudir/);
  });
});

describe("G-PAR do sacudir: o laco do TS = o Python, decisao a decisao", () => {
  test("o gabarito: duas sementes no mundo da ilha, com os tres motivos, sacudidas dormindo e frutas comidas", () => {
    expect(createHash("sha256").update(texto).digest("hex")).toBe(SHA);
    expect(VIDAS.map(v => v.semente)).toEqual([202, 505]);
    for (const v of VIDAS) {
      expect(v.dormindo_em.length).toBeGreaterThan(0);
      expect(v.frutas_comidas).toBeGreaterThan(0);
      expect(new Set((v.resumo.sacudidas as Rec[]).map(s => s.motivo))).toEqual(new Set(["caiu", "galho_vazio", "chao_cheio"]));
    }
  });

  for (const vida of VIDAS) {
    test(`${vida.nome}: cada decisao, o log, o mundo, o fluxo arvore-sacode e o corpo no fim`, () => {
      const c = cerebroDa(vida);
      const m = new LacoGravado(c.politica, vida.semente, CCO_CORPO_V11, estadoNascimentoPy(0), { regra: c.regra, paridade: true, ...CHAVES });
      const dormindo = new Set(vida.dormindo_em);
      for (const e of vida.log) {
        /* o roteiro sacode tambem com o pet dormindo (AS-1): nos ticks de `dormindo_em`, o pet dorme quando a sacudida chega */
        if (e.tipo === "sacudir_arvore" && dormindo.delete(e.tick)) expect(m.estado.dormindo, `tick ${e.tick}`).toBe(true);
        m.aplicarEvento(e);
      }
      expect(dormindo.size).toBe(0);
      expect(m.traco.length).toBe(vida.traco.length);
      for (let i = 0; i < vida.traco.length; i++) {
        const esperado = vida.traco[i], obtido = m.traco[i];
        if (JSON.stringify(obtido) === JSON.stringify(esperado)) continue;
        /* a primeira divergencia, campo a campo */
        for (const k of Object.keys(esperado)) expect(obtido[k], `traco[${i}] (${String(esperado.op)} no tick ${String(esperado.tick)}): ${k}`).toEqual(esperado[k]);
        expect(obtido, `traco[${i}]`).toEqual(esperado);
      }
      expect(m.log).toEqual(vida.log);
      const { rng_sacode: rngSacode, ...resumo } = vida.resumo as Rec & { rng_sacode: [number, number[], null] };
      const obtido = json(m.mundo.resumo()) as Rec;
      for (const k of ["quedas", "sacudidas", "galhos", "consumos", "comidas", "sumidas"]) expect(obtido[k], k).toEqual(resumo[k]);
      expect(obtido).toEqual(resumo);
      const mu = m.mundo, comum = mu.comum;
      expect(rngSacode[0]).toBe(3);
      expect(comum.rngSacode!.estado()).toEqual(rngSacode[1]);
      expect({ q: { ...m.corpo.q }, receptores: m.corpo.receptores() }).toEqual(vida.corpo_fim);
      const e = m.estado;
      expect({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira, tick: e.tick }).toEqual(vida.estado_fim);
      expect(mu.decisoes.length).toBe(vida.decisoes);
      expect(mu.noGalho(e.tick)).toEqual(vida.no_galho_fim);
      expect(m.estadoDict().sacudir).toEqual({ no_galho: vida.no_galho_fim, sacudidas: vida.sacudidas });
      const sac = mu.sacudidas!;
      expect([sac.length, sac.filter(s => s.motivo === "caiu").length]).toEqual([vida.sacudidas, vida.caidas]);
      expect((mu.consumos as { tipo: string }[]).filter(k => ["a", "b", "c"].includes(k.tipo)).length).toBe(vida.frutas_comidas);
      for (const [fluxo, r] of [["arvores", mu.rngArvores], ["bola", mu.rngBola], ["sujeira", mu.rngSujeira], ["alvo", mu.rngAlvo]] as const)
        expect(proximos(r), `proximos de ${fluxo}`).toEqual(vida.proximos[fluxo]);
      expect(proximos(comum.rngSacode!)).toEqual(vida.proximos_sacode);
    });
  }
});

/** um laco do A do v11 com as chaves do gabarito; `recebidas` conta os gestos que chegam ao cerebro */
function laco(semente: number, opcoes: OpcoesLacoMundo = CHAVES): { m: MotorCorpoMundo; recebidas: string[] } {
  const c = cerebroDa({ cerebro: "a_v11" } as Vida), recebidas: string[] = [];
  const politica = { ...c.politica, receberAcaoDono: (a: string, t: number) => { recebidas.push(a); c.politica.receberAcaoDono(a, t); } };
  return { m: new MotorCorpoMundo(politica, semente, CCO_CORPO_V11, estadoNascimentoPy(0), { regra: c.regra, ...opcoes }), recebidas };
}

describe("o sacudir no laco (MotorCorpoMundo)", () => {
  test("nao e cuidado (AS-1): so o mundo muda; o evento vai ao log", () => {
    for (const s of [101, 202, 303]) {
      const { m, recebidas } = laco(s);
      m.avancar(200);
      const estado = JSON.stringify(m.estado), q = JSON.stringify(m.corpo.q), dec = m.mundo.decisoes.length, n = m.log.length;
      const comidas = m.mundo.comidas.size;
      m.sacudirArvore("J2");
      expect(m.log.slice(n)).toEqual([{ tick: m.estado.tick, tipo: "sacudir_arvore", valor: "J2" }]);
      expect([JSON.stringify(m.estado), JSON.stringify(m.corpo.q), m.mundo.decisoes.length, recebidas]).toEqual([estado, q, dec, []]);
      expect(m.mundo.comidas.size).toBe(comidas + 1);
      expect(m.mundo.sacudidas!.at(-1)!.motivo).toBe("caiu");
    }
  });

  test("o galho esvazia, repoe uma fruta a cada recarga_galho_min e o fluxo so anda quando cai fruta", () => {
    const { m } = laco(101);
    m.avancar(30);
    const r = m.mundo.comum.rngSacode!;
    const e0 = JSON.stringify(r.estado());
    for (let i = 0; i < 4; i++) m.sacudirArvore("J1");
    expect(m.mundo.sacudidas!.map(s => [s.no_galho_antes, s.motivo])).toEqual([[3, "caiu"], [2, "caiu"], [1, "caiu"], [0, "galho_vazio"]]);
    const e1 = JSON.stringify(r.estado());
    expect(e1).not.toBe(e0);
    m.sacudirArvore("J1");                                       // o galho vazio nao sorteia
    expect(JSON.stringify(r.estado())).toBe(e1);
    expect(m.mundo.noGalho(m.estado.tick)).toEqual({ J1: 0, J2: 3, J3: 3 });
    m.avancar(240);
    expect(m.mundo.noGalho(m.estado.tick).J1).toBe(1);
    m.avancar(480);
    expect(m.mundo.noGalho(m.estado.tick).J1).toBe(3);
  });

  test("vale com o pet dormindo", () => {
    const { m } = laco(101);
    for (let i = 0; i < 400 && !m.estado.dormindo; i++) m.avancar(7);
    expect(m.estado.dormindo).toBe(true);
    m.sacudirArvore("J3");
    expect(m.mundo.sacudidas!.length).toBe(1);
  });

  test("o id fora do layout e a chave desligada falham alto, antes do log", () => {
    const { m } = laco(101);
    m.avancar(15);
    const n = m.log.length, antes = JSON.stringify(m.mundo.resumo());
    for (const id of ["M6", "J4", "j1"]) expect(() => m.sacudirArvore(id), id).toThrow(/nao existe no layout/);
    expect(() => m.sacudirArvore("J 1")).toThrow(/sacudir_arvore/);
    expect([m.log.length, JSON.stringify(m.mundo.resumo())]).toEqual([n, antes]);
    /* desligada: no mundo da pesquisa, o sacudir falha alto e nada muda; o mundo da ilha nem existe sem o sacudir (as arvores na casa) */
    const { m: d } = laco(101, { cfgMundo: CMU });
    d.avancar(15);
    expect(() => d.sacudirArvore("J1")).toThrow(/ConfigSacudir/);
    expect(d.log.length).toBe(1);
    expect(() => laco(101, { cfgMundo: CMU_ILHA })).toThrow(/fora do jardim e da mata/);
    expect(() => laco(101, { ...CHAVES, frutaComoComida: 1 as unknown as boolean })).toThrow(/frutaComoComida/);
  });

  test("desligado, nenhuma chave nova no resumo nem no estado", () => {
    const { m } = laco(101, { cfgMundo: CMU_MVP, decidirNaComida: true });
    m.avancar(300);
    expect(m.mundo.sacudidas).toBeNull();
    expect(Object.keys(m.mundo.resumo())).not.toContain("galhos");
    expect(Object.keys(m.mundo.resumo())).not.toContain("sacudidas");
    expect(Object.keys(m.estadoDict())).not.toContain("sacudir");
    expect(m.mundo.comum.rngSacode).toBeNull();
  });

  test("a queda natural nao muda com as sacudidas (o fluxo mundo-arvores)", () => {
    const com = new MundoPartilhado(CMU, 202), sem = new MundoPartilhado(CMU, 202);
    com.ligarSacudir(CONFIG_SACUDIR_LIGADA);
    const ids = CMU.layout.arvores.map(a => a[0]);
    for (let t = 1; t <= 3 * 1440; t += 37) {
      com.atualizar(t); sem.atualizar(t);
      com.sacudir(ids[t % ids.length], t);
    }
    expect(com.sacudidas!.filter(s => s.motivo === "caiu").length).toBeGreaterThan(10);
    expect(com.quedas.map(q => [q.tick, q.arvore, q.sorteadas, q.pontos])).toEqual(sem.quedas.map(q => [q.tick, q.arvore, q.sorteadas, q.pontos]));
    expect(com.rngArvores.estado()).toEqual(sem.rngArvores.estado());
    expect(com.rngBola.estado()).toEqual(sem.rngBola.estado());
  });

  test("o evento refaz no replay, bit a bit", () => {
    for (const s of [101, 303]) {
      const { m } = laco(s);
      for (let i = 0; i < 40; i++) {
        m.avancar(53);
        if (i % 5 === 0) m.deixarComida("racao", 200, 200);
        m.sacudirArvore(["J1", "J2", "J3"][i % 3]);
      }
      const { m: r } = laco(s);
      for (const e of m.log as EventoCorpo[]) r.aplicarEvento(e);
      expect(r.log).toEqual(m.log);
      expect(JSON.stringify(r.mundo.resumo())).toBe(JSON.stringify(m.mundo.resumo()));
      expect(JSON.stringify(r.estadoDict())).toBe(JSON.stringify(m.estadoDict()));
      expect(r.mundo.comum.rngSacode!.estado()).toEqual(m.mundo.comum.rngSacode!.estado());
    }
  });
});

describe("o sacudir no Motor do jogo: nenhuma versao o tem (D-AS-S2-1)", () => {
  test("todas as versoes de hoje recusam o sacudirArvore e o \"sa\" no replay, antes do registro", () => {
    expect(VERSOES_COM_SACUDIR).toEqual([]);
    for (const v of VERSOES_PET) {
      const m = new Motor(101, v);
      m.avancar(60);
      const n = m.log.length, a = m.assinatura();
      expect(() => m.sacudirArvore("J1"), `v${v}`).toThrow(/nenhum pet sacode/);
      expect([m.log.length, m.assinatura()]).toEqual([n, a]);
      expect(() => Motor.reproduzir(101, [...m.log, [m.e.tick, "sa", { arvore: "J1" }]], v), `v${v}`).toThrow(/nenhum pet sacode/);
      expect(() => m.sacudirArvore("J-1")).toThrow(/sacudir_arvore/);
      for (const ruim of [{ arvore: "J1", x: 1 }, { arvore: 1 }, null, ["J1"], {}])
        expect(() => Motor.reproduzir(101, [...m.log, [m.e.tick, "sa", ruim] as unknown as EventoRegistro], v), JSON.stringify(ruim)).toThrow();
    }
  });
});
