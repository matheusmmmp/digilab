/* Voz propria no jogo (DESIGN_VOZ_PROPRIA, parte 4): o extrator da historia e a mentira dos pets v5 conferidos contra o
   Python (gabaritos/voz_python.json, de experiments/exportar_gabaritos_voz.py). As rngs sao outras (MT x mulberry32): a
   paridade e das regras (fatos, textos, ordem, formulas, desfechos), nao das vidas. */
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { CMEN, VERSAO_PET } from "../motor/constantes.ts";
import { escolherAssunto, extrair, registroDoMotor, selecionar, type FatoHistoria, type RegistroVida } from "../motor/historia.ts";
import { Motor } from "../motor/motor.ts";

interface CasoHistoria { pet: string; corte: number | null; registro: RegistroVida; fatos: FatoHistoria[]; selecao: string[];
  citados: string[][]; selecao_com_citados: string[]; assuntos: string[][] }
const G = JSON.parse(readFileSync(new URL("./gabaritos/voz_python.json", import.meta.url), "utf-8")) as {
  historia: CasoHistoria[];
  mentira: { grade: { sombria: boolean; sobrecarga: number; disciplina: number; impunes: number; acertos: number; h: number; p: number; mostrada: number }[];
    desfechos: { falso: boolean; acao: string; aberta: boolean; desfecho: string | null; disciplina: number; impunes: number; acertos: number; bronca_injusta: number }[] };
};

function igualDados(a: Record<string, unknown>, b: Record<string, unknown>, rotulo: string): void {
  expect(Object.keys(a).sort(), rotulo).toEqual(Object.keys(b).sort());
  for (const k of Object.keys(b)) {
    if (typeof b[k] === "number" && !Number.isInteger(b[k])) expect(a[k] as number, `${rotulo}.${k}`).toBeCloseTo(b[k] as number, 12);
    else expect(a[k], `${rotulo}.${k}`).toEqual(b[k]);
  }
}

describe("historia.ts = digilab/historia.py", () => {
  test.each(G.historia.map(c => [`${c.pet} corte ${c.corte}`, c] as const))("%s", (_, c) => {
    const fatos = extrair(c.registro);
    expect(fatos.map(f => [f.tipo, f.regra, f.chave, f.texto, f.tick])).toEqual(c.fatos.map(f => [f.tipo, f.regra, f.chave, f.texto, f.tick]));
    fatos.forEach((f, i) => igualDados(f.dados, c.fatos[i].dados, f.chave));
    expect(selecionar(fatos).map(f => f.chave)).toEqual(c.selecao);
    expect(selecionar(fatos, c.citados).map(f => f.chave)).toEqual(c.selecao_com_citados);
    const dados: string[][] = [];
    for (let k = 0; k < 5; k++) { const a = escolherAssunto(fatos, dados); dados.push(a ? [a.chave] : []); }
    expect(dados).toEqual(c.assuntos);
  });
  test("os gabaritos tem de tudo um pouco", () => {
    const regras = new Set(G.historia.flatMap(c => c.fatos.map(f => f.regra)));
    for (const r of ["evolucao", "ausencia", "sequencia", "periodo", "gosto", "desgosto", "demora", "periodo_dono", "primeira_vitoria"])
      expect(regras.has(r), r).toBe(true);
  });
});

function motorV5(): Motor { const m = new Motor(4242, 5); m.avancar(200); return m; }

describe("mentira (pets v5) = digilab/educacao.py", () => {
  test("grade de honestidade, chance e honestidade mostrada", () => {
    for (const g of G.mentira.grade) {
      const m = motorV5();
      m.sombria = g.sombria; m.treino.sobrecarga = g.sobrecarga; m.edu.disciplina = g.disciplina;
      m.men = { impunes: g.impunes, acertos: g.acertos };
      const r = JSON.stringify(g);
      expect(m.honestidade(), r).toBeCloseTo(g.h, 12);
      expect(m.chanceMentira(), r).toBeCloseTo(g.p, 12);
      expect(m.honestidadeMostrada(), r).toBeCloseTo(g.mostrada, 12);
    }
  });
  test("desfechos da janela de fala", () => {
    const acao = { bronca: "repreender", petisco: "petisco", elogio: "elogiar", carinho: "acariciar" } as const;
    for (const d of G.mentira.desfechos) {
      const m = motorV5(), t = m.e.tick;
      m.edu.disciplina = 25; m.men = { impunes: 1, acertos: 1 };
      m.edu.janela = { tipo: "fala", pedido: "estado", inicio: t, prazo: t + CMEN.janela, falso: d.falso, contradiz: d.falso, gatilho: "teste", h: .5, p: .5 };
      if (d.acao === "prazo") { m.avancar(40); m.observar("acariciar"); } else m.observar(acao[d.acao as keyof typeof acao]);
      const r = JSON.stringify(d), falas = m.janelasFechadas.filter(j => j.tipo === "fala");
      expect(m.edu.janela !== null, r).toBe(d.aberta);
      expect(falas.length ? falas[falas.length - 1].desfecho : null, r).toBe(d.desfecho);
      expect([m.edu.disciplina, m.men.impunes, m.men.acertos, m.edu.contagem.broncas_injustas ?? 0], r)
        .toEqual([d.disciplina, d.impunes, d.acertos, d.bronca_injusta]);
    }
  });
});

describe("evento f (pets v5)", () => {
  test("a fala entra no registro, rejoga igual e sorteia sempre duas vezes", () => {
    expect(VERSAO_PET).toBe(5);
    const m = new Motor(777, 5);
    m.avancar(400);
    m.treino.sobrecarga = 100; m.sombria = true;
    const abertas: unknown[] = [];
    for (let k = 0; k < 20 && !abertas.some(Boolean); k++) { abertas.push(m.falar(k % 2 ? "marco" : "reencontro")); m.avancar(45); }
    expect(m.log.filter(e => e[1] === "f").length).toBe(abertas.length);
    expect(abertas.some(Boolean)).toBe(true);                     /* dormindo ou com outra janela aberta, nao abre */
    const r = Motor.reproduzir(777, m.log, 5);
    /* a sobrecarga e a forma sombria postas a mao nao estao no registro: confere so o sorteio e as contagens */
    expect(r.edu.contagem.falas).toBe(m.edu.contagem.falas);
    expect(() => new Motor(777, 4).falar("reencontro")).toThrow();
    expect(() => m.falar("Não Pode")).toThrow();
  });
  test("pet sem sobrecarga e nao sombrio nunca mente; o registro da historia sai do motor", () => {
    const m = new Motor(99, 5);
    for (let i = 0; i < 40; i++) { m.avancar(120); m.falar("reencontro"); if (m.janelaAberta()) m.observar("elogiar"); }
    expect(m.edu.contagem.mentiras ?? 0).toBe(0);
    expect(m.honestidadeMostrada()).toBe(1);
    const reg = registroDoMotor(m);
    expect(reg.acoesPet.length).toBeGreaterThan(0);
    expect(reg.acoesDono.every(([t, a]) => typeof t === "number" && typeof a === "string")).toBe(true);
    expect(extrair(reg).some(f => f.regra === "evolucao")).toBe(true);
  });
});

describe("moldes da mentira = digilab_fala_livre/mentira.py", () => {
  test("historia e estado", async () => {
    const { mentiraDeEstado, mentiraDeHistoria } = await import("../motor/mentira.ts");
    const M = G.mentira as unknown as { moldes_historia: { regra: string; dados: Record<string, unknown>; falsa: string | null }[];
      moldes_estado: { estado: Record<string, number>; verdade: string; falsa: string; molde: string }[] };
    expect(M.moldes_historia.length).toBeGreaterThan(20);
    for (const x of M.moldes_historia) expect(mentiraDeHistoria(x.regra, x.dados), x.regra).toBe(x.falsa);
    for (const x of M.moldes_estado) expect(mentiraDeEstado(x.estado)).toEqual({ verdade: x.verdade, falsa: x.falsa, molde: x.molde });
  });
});
