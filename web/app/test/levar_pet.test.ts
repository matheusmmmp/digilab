/* O levar pet (docs/TAREFA_V3_PEGAR_PET.md, P1; os pets v19): o dono pega o pet e o solta noutro lugar do mapa. O espelho do
   tests/test_levar_pet.py do Python.
     - o formato do log (eventoLevarPet, lerLevarPet): os mesmos casos do Python;
     - o G-PAR do laco: o TS refaz o gabarito do Python (test/gabaritos/levar_pet_python.json, experiments/exportar_gabarito_levar_pet.py)
       decisao a decisao e bit a bit no Node, pelo laco gravado do MVP (test/laco_gravado.ts), e recusa em cada tick de `dormindo_em`;
     - o "lp" do Motor: da v19 em diante (desde a LP4 da LUTA_POC so a v21 abre); vai ao registro e refaz no replay bit a bit; so a posicao muda (PP-1), fora do mapa cai na borda (PP-4),
       o pendente se perde; dormindo falha alto (PP-2), e o registro invalido tambem. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { CMU_MVP, VERSAO_PET, VERSAO_PET_LAB, VERSAO_V19, VERSOES_PET, ehCerebroTrocavel } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { Motor } from "../motor/motor.ts";
import { estadoNascimentoPy } from "../motor/motor_corpo.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { eventoLevarPet, lerLevarPet, noMapa } from "../motor/mundo.ts";
import type { EventoRegistro } from "../motor/tipos.ts";
import { LacoGravado, cerebroDa, json, ler, type Rec, type Vida } from "./laco_gravado.ts";

const { texto, g: G } = ler("./gabaritos/levar_pet_python.json");
const SHA = "f494c2539ad843086c1f7714070e230ffd3429be9d67a0db801d7fb7de5be957";
type VidaLevar = Vida & { levadas: number; dormindo_em: number[] };
const VIDAS = G.vidas as VidaLevar[];

describe("o formato do log do levar pet (os casos do Python)", () => {
  test("o ponto solto e inteiro e com sinal; fora do mapa vale no evento", () => {
    expect(eventoLevarPet(9, 10, 20)).toEqual({ tick: 9, tipo: "levar_pet", valor: "10|20" });
    expect(eventoLevarPet(9, -40, 99999).valor).toBe("-40|99999");
    expect(eventoLevarPet(9, -0, 0).valor).toBe("0|0");
    for (const [x, y] of [[1.5, 0], [0, NaN], ["1", 0], [true, 0], [2 ** 53, 0], [0, -(2 ** 53)]] as unknown[][])
      expect(() => eventoLevarPet(9, x, y), `${String(x)}, ${String(y)}`).toThrow(/levar_pet/);
    expect(eventoLevarPet(9, 2 ** 53 - 1, -(2 ** 53 - 1)).valor).toBe(`${2 ** 53 - 1}|${-(2 ** 53 - 1)}`);
  });
  test("a leitura aceita so a forma canonica", () => {
    expect(lerLevarPet({ tick: 0, tipo: "levar_pet", valor: "-40|7" })).toEqual([-40, 7]);
    expect(lerLevarPet({ tick: 0, tipo: "levar_pet", valor: "0|0" })).toEqual([0, 0]);
    for (const v of ["07|1", "-0|1", "+1|1", "1.0|1", "1|", "|1", "1|2|3", "a|1", " 1|1", "1|1 ", "--1|1", "9007199254740992|0"])
      expect(() => lerLevarPet({ tick: 0, tipo: "levar_pet", valor: v }), v).toThrow();
    expect(() => lerLevarPet({ tick: 0, tipo: "deixar_bola", valor: "1|1" })).toThrow(/nao e levar_pet/);
  });
});

describe("G-PAR do levar pet: o laco do TS = o Python, decisao a decisao", () => {
  test("o gabarito: duas sementes no mundo do produto, com levadas dentro e fora do mapa e recusas com o pet dormindo", () => {
    expect(createHash("sha256").update(texto).digest("hex")).toBe(SHA);
    expect(json(CMU_MVP)).toEqual(G.config.mundo);
    expect(VIDAS.map(v => v.semente)).toEqual([101, 202]);
    for (const v of VIDAS) { expect(v.levadas).toBeGreaterThan(10); expect(v.dormindo_em.length).toBeGreaterThan(0); }
  });

  for (const vida of VIDAS) {
    test(`${vida.nome}: cada decisao, o log, o mundo e o corpo no fim; a recusa em cada tick dormindo`, () => {
      const c = cerebroDa(vida);
      const m = new LacoGravado(c.politica, vida.semente, CCO_CORPO_V11, estadoNascimentoPy(0),
                                { regra: c.regra, paridade: true, cfgMundo: CMU_MVP, decidirNaComida: true });
      const recusar = new Set(vida.dormindo_em);
      for (const e of vida.log) {
        /* o roteiro tentou levar logo antes do avanco do tick: o pet dormia, o motor recusou e nada foi ao log */
        if (e.tipo === "avanco" && recusar.delete(e.tick)) {
          const n = m.log.length, antes = JSON.stringify(m.mundo.resumo());
          expect(m.estado.dormindo).toBe(true);
          expect(() => m.levarPet(0, 0)).toThrow(/dormindo/);
          expect(m.log.length).toBe(n);
          expect(JSON.stringify(m.mundo.resumo())).toBe(antes);
        }
        m.aplicarEvento(e);
      }
      expect(recusar.size).toBe(0);
      expect(m.traco.length).toBe(vida.traco.length);
      for (let i = 0; i < vida.traco.length; i++) {
        const esperado = vida.traco[i] as Rec, obtido = m.traco[i];
        if (JSON.stringify(obtido) === JSON.stringify(esperado)) continue;
        for (const k of Object.keys(esperado)) expect(obtido[k], `traco[${i}] (${esperado.op} no tick ${esperado.tick}): ${k}`).toEqual(esperado[k]);
      }
      expect(m.log).toEqual(vida.log);
      expect(json(m.mundo.resumo())).toEqual(vida.resumo);
      expect({ q: { ...m.corpo.q }, receptores: m.corpo.receptores() }).toEqual(vida.corpo_fim);
      const e = m.estado;
      expect({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira, tick: e.tick }).toEqual(vida.estado_fim);
      /* cada levada cai em noMapa do ponto pedido (PP-4), e ha levadas fora do mapa */
      const levadas = m.mundo.levadas;
      expect(levadas.length).toBe(vida.levadas);
      for (const l of levadas) expect(l.para).toEqual(noMapa(l.pedido[0], l.pedido[1], CMU_MVP));
      expect(levadas.some(l => l.para[0] !== l.pedido[0] || l.para[1] !== l.pedido[1])).toBe(true);
    });
  }
});

/** o pet v19 do jogo, acordado, num tick com o destino pendente (o pet anda para algum lugar) */
function acordado(semente: number): Motor {
  const m = new Motor(semente, 21);
  m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
  m.avancar(300);
  for (let i = 0; i < 200 && m.e.dormindo; i++) m.avancar(7);
  if (m.e.dormindo) throw new Error("o pet nao acordou");
  return m;
}
/** a assinatura do Motor sem o mundo (o ultimo item, e a posicao do pet no estado do laco, o `mundo` do estadoDict): o que o levar pet
    nao pode mudar (PP-1) */
const semMundo = (m: Motor): unknown => {
  const a = (JSON.parse(m.assinatura()) as unknown[]).slice(0, -1);
  const v11 = a[a.length - 1] as [string, unknown, Record<string, unknown>, number];
  if (v11[0] !== "v11" || !("mundo" in v11[2])) throw new Error("a assinatura mudou de forma");
  delete v11[2].mundo;
  return a;
};

describe("o levar pet no Motor (o evento lp, pets v19)", () => {
  test("o ovo novo (a v21) tem o levar pet da v19 e o cerebro trocavel", () => {
    expect(VERSAO_PET).toBe(32);
    expect(VERSAO_V19).toBe(19);
    expect(VERSOES_PET).toEqual([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]);   // a v26: os dois pets (CO4c)
    const m = new Motor(101, 21);
    expect(m.versao).toBe(21);
    expect(ehCerebroTrocavel(21)).toBe(true);
    expect(m.mundo!.bolaNoGolpe).toBe(true);
    expect(m.v11!.laco).toBeInstanceOf(MotorCorpoMundo);
  });

  test("so a posicao muda (PP-1): o pet cai onde foi solto, o pendente se perde, e nada mais muda", () => {
    for (const s of [101, 202, 303]) {
      const m = acordado(s), antes = semMundo(m), t = m.e.tick, n = m.log.length, hist = m.historico.length, nDono = m.nDono;
      const laco = m.v11!.laco as MotorCorpoMundo, q = JSON.stringify(laco.corpo.q), dec = m.mundo!.decisoes.length;
      m.levarPet(321, 123);
      expect(m.mundo!.pet).toEqual([321, 123]);
      expect((m.mundo!.resumo() as { pendente: unknown }).pendente).toBeNull();
      expect(m.log.slice(n)).toEqual([[t, "lp", { x: 321, y: 123 }]]);
      expect(semMundo(m)).toEqual(antes);
      expect([m.e.tick, m.historico.length, m.nDono, JSON.stringify(laco.corpo.q), m.mundo!.decisoes.length]).toEqual([t, hist, nDono, q, dec]);
      expect(m.mundo!.levadas).toEqual([{ tick: t, de: m.mundo!.levadas[0].de, pedido: [321, 123], para: [321, 123] }]);
    }
  });

  test("fora do mapa, o pet cai na borda mais proxima (PP-4); o registro guarda o ponto pedido", () => {
    const m = acordado(101), max = [CMU_MVP.celulas_x * CMU_MVP.sub - 1, CMU_MVP.celulas_y * CMU_MVP.sub - 1];
    expect(max).toEqual([1023, 479]);
    for (const [x, y, px, py] of [[-50, 9000, 0, 479], [5000, -3, 1023, 0], [-1, 240, 0, 240], [1024, 480, 1023, 479], [0, 0, 0, 0]]) {
      m.levarPet(x, y);
      expect(m.mundo!.pet, `${x}, ${y}`).toEqual([px, py]);
      expect(m.log[m.log.length - 1]).toEqual([m.e.tick, "lp", { x, y }]);
    }
  });

  test("vai ao registro e refaz no replay bit a bit, com o pet andando de onde caiu", () => {
    for (const s of [101, 202]) {
      const m = acordado(s);
      const pontos = [[100, 100], [-20, 300], [900, 9999], [512, 240]];
      for (const [x, y] of pontos) {
        if (!m.e.dormindo) m.levarPet(x, y);
        m.avancar(45);
      }
      expect(m.log.filter(e => e[1] === "lp").length).toBeGreaterThan(0);
      const r = Motor.reproduzir(s, m.log, 21);
      expect(r.assinatura()).toBe(m.assinatura());
      expect(r.mundo!.levadas).toEqual(m.mundo!.levadas);
    }
  });

  test("o pet dormindo nao e pego (PP-2): falha alto e nada vai ao registro", () => {
    const m = new Motor(101, 21);
    m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
    for (let i = 0; i < 2000 && !m.e.dormindo; i++) m.avancar(7);
    expect(m.e.dormindo).toBe(true);
    const n = m.log.length, a = m.assinatura();
    expect(() => m.levarPet(10, 10)).toThrow(/dormindo/);
    expect(m.log.length).toBe(n);
    expect(m.assinatura()).toBe(a);
    /* no replay, um "lp" com o pet dormindo tambem falha */
    expect(() => Motor.reproduzir(101, [...m.log, [m.e.tick, "lp", { x: 10, y: 10 }]], 21)).toThrow(/dormindo/);
  });

  test("antes da v19 o evento nao existe (so o pet de teste v16 abre, das de antes), e o registro invalido falha alto", () => {
    for (const v of [VERSAO_PET_LAB]) {
      const m = new Motor(101, v);
      m.avancar(60);
      expect(() => m.levarPet(10, 10), `v${v}`).toThrow(/v19/);
      expect(() => Motor.reproduzir(101, [...m.log, [m.e.tick, "lp", { x: 10, y: 10 }]], v), `v${v}`).toThrow(/v19/);
    }
    const m = acordado(101), t = m.e.tick;
    for (const ruim of [{ x: 1 }, { x: 1, y: 2, z: 3 }, { x: 1.5, y: 2 }, { x: "1", y: 2 }, null, [1, 2]])
      expect(() => Motor.reproduzir(101, [...m.log, [t, "lp", ruim] as unknown as EventoRegistro], 21), JSON.stringify(ruim)).toThrow();
    expect(() => m.levarPet(1.5, 2)).toThrow(/levar_pet/);
  });
});
