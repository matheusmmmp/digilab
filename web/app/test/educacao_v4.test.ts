/* Pets v4 (educacao-v1, espelho de digilab/educacao.py): travessuras com janela, disciplina, lesoes, morte e a
   qualificacao por vitorias para chegar a adulto. Os pets v1-v3 seguem nos gabaritos de paridade. */
import { describe, expect, test } from "vitest";
import { CAT, CED, CLE, DUR_EVO, TICK_INICIAL } from "../motor/constantes.ts";
import { Motor, PetMorto, type Janela } from "../motor/motor.ts";
import { lutadorPet } from "../motor/gambits_pet.ts";

const INI_CRIANCA = TICK_INICIAL + DUR_EVO.bebe;
const INI_ADOL = INI_CRIANCA + DUR_EVO.crianca;

/** dono simples: cuida abaixo de 0,5 e responde a janela como o atencioso (bronca na manha) */
function viver(m: Motor, ate: number, lutar = false): void {
  let k = 0;
  while (m.e.tick < ate && !m.morte) {
    m.avancar(15);
    if (m.morte) break;
    const j = m.janelaAberta();
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    if (j) {
      if (j.tipo === "aviso") m.observar("levar_ao_banheiro");
      else {
        const nec = j.pedido === "fome" ? m.e.fome : j.pedido === "higiene" ? m.e.higiene : m.e.humor;
        m.observar(nec < CED.limiarReal ? (j.pedido === "fome" ? "alimentar" : j.pedido === "higiene" ? "limpar" : "acariciar") : "repreender");
      }
    }
    if (m.e.fome < .5) m.observar("alimentar");
    if (m.e.higiene < .5) m.observar("limpar");
    if (lutar && m.estagioAtual === "adolescente" && k++ % 4 === 0) m.lutar("aleatorio", 9000 + k);
  }
}

const abrir = (m: Motor, j: Omit<Janela, "inicio" | "prazo">) => { m.edu.janela = { ...j, inicio: m.e.tick, prazo: m.e.tick + CED.janela }; };

describe("pets v4", () => {
  test("acoes novas: so no v4", () => {
    expect(() => new Motor(11, 3).observar("petisco")).toThrow();
    const m = new Motor(11, 4); m.avancar(15); m.observar("petisco");
    expect(m.log.at(-1)).toEqual([TICK_INICIAL + 15, "d", "petisco"]);
  });

  test("vida com janelas e lutas rejoga bit a bit", () => {
    const m = new Motor(4242, 4);
    viver(m, INI_ADOL + 600, true);
    expect(m.janelasFechadas.length).toBeGreaterThan(0);
    expect(Math.min(...m.janelasFechadas.map(j => j.inicio))).toBeGreaterThanOrEqual(INI_CRIANCA);
    const r = Motor.reproduzir(m.semente, m.log, 4);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.janelasFechadas).toEqual(m.janelasFechadas);
  });

  test("chamado falso: bronca educa, petisco cede, refeicao recusada", () => {
    const m = new Motor(7, 4); m.avancar(15);
    abrir(m, { tipo: "chamado", pedido: "fome", falso: true });
    const fome = m.e.fome;
    m.observar("alimentar");
    expect(m.e.fome).toBe(fome); expect(m.edu.janela).not.toBeNull();
    m.observar("repreender");
    expect(m.edu.janela).toBeNull(); expect(m.edu.disciplina).toBe(CED.passo); expect(m.edu.acertos).toBe(1);
    abrir(m, { tipo: "chamado", pedido: "fome", falso: true });
    m.observar("petisco");
    expect(m.edu.petiscos).toBe(1); expect(m.edu.acertos).toBe(0);
    expect(m.fracaoFalso()).toBeCloseTo(CED.fracaoFalsoBase * (1 - CED.passo / 100) + CED.reforcoPetisco);
  });

  test("aviso ignorado suja; falso ignorado derruba a disciplina", () => {
    const m = new Motor(8, 4); m.avancar(15);
    abrir(m, { tipo: "aviso", pedido: "banheiro", falso: false });
    const suj = m.e.sujeira;
    m.avancar(CED.janela + 16);
    expect(m.e.sujeira).toBeGreaterThanOrEqual(Math.min(5, suj + 1));
    m.edu.disciplina = 50;
    abrir(m, { tipo: "chamado", pedido: "carinho", falso: true });
    m.avancar(CED.janela + 16);
    expect(m.edu.disciplina).toBe(50 - CED.passo);
  });

  test("lesao sem tratar mata; depois nada funciona", () => {
    const m = new Motor(9, 4); m.avancar(15);
    m.lesionadoDesde = m.e.tick;
    m.avancar(CLE.horasMorte * 60);
    expect(m.morte?.causa).toBe("lesao_sem_tratar");
    expect(() => m.observar("alimentar")).toThrow(PetMorto);
    expect(() => m.lutar("aleatorio", 1)).toThrow(PetMorto);
  });

  test("adulto so com a taxa de vitoria; disciplina no epsilon", () => {
    const m = new Motor(10, 4);
    m.avancar(INI_ADOL - TICK_INICIAL + 30);
    expect(m.estagioAtual).toBe("adolescente");
    m.sparring = CAT.sparring; m.lutas = { lutas: 10, vitorias: 7, derrotas: 3, empates: 0, lesoes: 0, tratadas: 0 };
    m.avancar(DUR_EVO.adolescente);
    expect(m.estagioAtual).toBe("adolescente");                 /* 0,7 < 0,8: continua adolescente */
    m.lutas.vitorias = 8;
    m.avancar(15);
    expect(m.estagioAtual).toBe("adulto");
    const eps = (d: number) => { m.edu.disciplina = d; return lutadorPet(m, "x").estilo.eps; };
    expect(eps(0) - eps(100)).toBeCloseTo(CED.deltaEps);
  });

  test("v3 nao muda: sem janela, sem lesao, sem gate de taxa", () => {
    const m = new Motor(4242, 3);
    viver(m, INI_ADOL + 200, true);
    expect(m.janelaAberta()).toBeNull();
    expect(Motor.reproduzir(4242, m.log, 3).assinatura()).toBe(m.assinatura());
  });
});

describe("heranca (pets v4)", () => {
  const adulto = (s: number) => {
    const m = new Motor(s, 3);
    m.avancar(INI_ADOL - TICK_INICIAL + 15);
    m.sparring = CAT.sparring;
    m.avancar(DUR_EVO.adolescente);
    expect(m.estagioAtual).toBe("adulto");
    return m;
  };
  test("filho herda temperamento e especie; replay pelo evento de origem", () => {
    const p = adulto(501), q = adulto(502);
    const f = Motor.cruzar(p, q, 777, 99, "teste");
    expect(f.log[0][1]).toBe("o");
    expect([p.especie, q.especie]).toContain(f.especie);
    for (const e of Object.keys(f.temp) as (keyof typeof f.temp)[]) {
      expect(Math.abs(f.temp[e] - (p.temp[e] + q.temp[e]) / 2)).toBeLessThan(.6);
    }
    f.avancar(600); f.observar("alimentar"); f.avancar(300);
    const r = Motor.reproduzir(777, f.log, f.versao);     /* o filho nasce na versao atual */
    expect(r.assinatura()).toBe(f.assinatura());
    expect(r.temp).toEqual(f.temp); expect(r.especie).toBe(f.especie);
    expect(Motor.cruzar(p, q, 777, 99, "teste").temp).toEqual(f.temp);   /* deterministico */
  });
  test("so adultos vivos cruzam; origem so no comeco", () => {
    const p = adulto(503), jovem = new Motor(504, 4);
    expect(() => Motor.cruzar(p, jovem, 1, 1, "x")).toThrow();
    const f = new Motor(9, 4); f.avancar(15);
    expect(() => f.registrarOrigem({ pais: [{ h: 1, esp: "brasa", temp: p.temp, est: "adulto" }, { h: 2, esp: "limo", temp: p.temp, est: "adulto" }], s: 1, quem: "x" })).toThrow();
  });
});

test("experiencia de combate: vitorias baixam o epsilon, com teto, e nao zeram ao evoluir", () => {
  const m = new Motor(12, 4); m.avancar(15);
  m.edu.disciplina = 100;
  const base = lutadorPet(m, "x").estilo.eps;
  m.vitoriasVida = 10;
  expect(base - lutadorPet(m, "x").estilo.eps).toBeCloseTo(10 * CLE.expPorVitoria);
  m.vitoriasVida = 100000;
  expect(lutadorPet(m, "x").estilo.eps).toBeGreaterThanOrEqual(0);
  expect(base - lutadorPet(m, "x").estilo.eps).toBeLessThanOrEqual(CLE.expMax + 1e-12);
});

describe("ritmo classico (6/24/36 h)", () => {
  test("evolui no ritmo escolhido e o replay le do evento de config", () => {
    const m = new Motor(21, 4); m.configurar("classica");
    expect(m.log[0]).toEqual([TICK_INICIAL, "c", { dur: "classica" }]);
    m.avancar(DUR_EVO.bebe + 30);
    expect(m.estagioAtual).toBe("bebe");                          /* no rapido ja seria Rookie */
    m.avancar(360 - DUR_EVO.bebe);
    expect(m.estagioAtual).toBe("crianca");
    expect(Motor.reproduzir(21, m.log, 4).assinatura()).toBe(m.assinatura());
  });
  test("so no comeco, so v4; a origem pode vir depois da config", () => {
    const m = new Motor(22, 4); m.avancar(15);
    expect(() => m.configurar("classica")).toThrow();
    expect(() => new Motor(23, 3).configurar("classica")).toThrow();
    const f = new Motor(24, 4); f.configurar("classica");
    const t = f.temp;
    f.registrarOrigem({ pais: [{ h: 1, esp: "brasa", temp: t, est: "adulto" }, { h: 2, esp: "limo", temp: t, est: "adulto" }], s: 5, quem: "x" });
    expect(Motor.reproduzir(24, f.log, 4).assinatura()).toBe(f.assinatura());
  });
});
