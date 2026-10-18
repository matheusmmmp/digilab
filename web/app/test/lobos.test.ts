/* O cerebro A em TS, sem aprender (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 2; o gate G-PAR-L0): motor/lobos.ts reproduz, decisao a
   decisao, a secao l0 do gabarito do Python (test/gabaritos/lobos_python.json, de experiments/exportar_gabarito_lobos.py): a regra,
   os candidatos, as contribuicoes por lobo, os pesos efetivos, o u, a acao e o lobo decisivo, bit a bit no Node. E confere que a
   decisao e a do instinto do TS (distInstinto, bandit.ts): os mesmos candidatos, as mesmas probabilidades e a mesma acao com o mesmo u.

   A observacao de cada decisao sai da percepcao gravada: o Estado.vetor sao as entradas 1 a 8, e o tempo sem cuidado volta de
   min(1, tdc / 480) (inteiro abaixo de 480; com 1.0, qualquer tdc >= 480 da a mesma percepcao e a mesma regra). O teste confere que a
   percepcao refeita e a gravada, bit a bit, antes de comparar o resto. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { distInstinto } from "../motor/bandit.ts";
import { CLB } from "../motor/constantes.ts";
import {
  ACOES_LOBOS, CerebroA, ENTRADAS_LOBOS, REGRAS_LOBOS, agirInstinto, impulsos, percepcao, sortear, tabelaPrior, type MotivoLobos,
  type RngInstinto,
} from "../motor/lobos.ts";
import type { AcaoPet, Observacao } from "../motor/tipos.ts";

interface VidaL0 { dono: string; semente: number; motivos: MotivoLobos[] }
const G = JSON.parse(readFileSync(new URL("./gabaritos/lobos_python.json", import.meta.url), "utf8")) as {
  versao: number; config: { lobos: Record<string, unknown> }; l0: VidaL0[];
};

/** a observacao da decisao, refeita da percepcao gravada */
function observacaoDe(m: MotivoLobos): Observacao {
  const p = m.percepcao;
  const t = p.ticks_sem_cuidado;
  return { v: ENTRADAS_LOBOS.slice(1, 9).map(e => p[e]), tdc: t >= 1 ? CLB.escalaTdc : Math.round(t * CLB.escalaTdc) };
}

/** a rng que devolve o u gravado, uma vez so; sem u gravado, qualquer chamada falha */
function rngDoGabarito(u: number | null) {
  const r = { chamadas: 0, random() { r.chamadas += 1; if (u === null || r.chamadas > 1) throw new Error("rng chamada sem u gravado"); return u; } };
  return r;
}

/** o random.Random do Python visto pelo instinto, com o u gravado: random() devolve u e choices(k=1) sorteia com ele */
function rngInstinto(u: number | null): RngInstinto & { chamadas: number; pesos: number[] | null } {
  const base = rngDoGabarito(u);
  const r = {
    pesos: null as number[] | null,
    get chamadas() { return base.chamadas; },
    random: () => base.random(),
    choices: (pop: readonly AcaoPet[], pesos: readonly number[]) => { r.pesos = [...pesos]; return pop[sortear(pesos, base.random())]; },
  };
  return r;
}

describe("G-PAR-L0: o cerebro A sem aprender = o gabarito do Python, decisao a decisao", () => {
  test("o gabarito e o esperado: versao 1, duas vidas L0 com 288 decisoes, a ConfigLobos do L0 = CLB", () => {
    expect(G.versao).toBe(1);
    expect(G.l0.map(v => [v.dono, v.semente, v.motivos.length])).toEqual([["atencioso", 101, 288], ["aleatorio", 202, 288]]);
    const cl = G.config.lobos;
    expect([cl.bits_ponto_fixo, cl.escala_ticks_desde_cuidado, cl.maximo_pesos]).toEqual([CLB.bits, CLB.escalaTdc, CLB.maxPesos]);
  });

  test("as duas vidas juntas passam por todas as regras do instinto", () => {
    const vistas = new Set(G.l0.flatMap(v => v.motivos.map(m => m.regra)));
    expect([...vistas].sort()).toEqual([...REGRAS_LOBOS].sort());
  });

  for (const vida of G.l0) {
    test(`${vida.dono} ${vida.semente}: percepcao, regra, candidatos, contribuicoes, pesos, u, acao e lobo decisivo`, () => {
      const cerebro = new CerebroA();
      for (const m of vida.motivos) {
        const obs = observacaoDe(m);
        const x = percepcao(obs);
        x.forEach((xj, j) => expect(Object.is(xj, m.percepcao[ENTRADAS_LOBOS[j]]), `decisao ${m.n}, ${ENTRADAS_LOBOS[j]}`).toBe(true));
        const rng = rngDoGabarito(m.u);
        const acao = cerebro.agir(obs, rng);
        expect(rng.chamadas, `decisao ${m.n}: chamadas da rng`).toBe(m.u === null ? 0 : 1);
        expect(acao).toBe(m.acao);
        expect(cerebro.ultimaRegra).toBe(m.regra);
        /* toStrictEqual compara os numeros com Object.is: bit a bit, e o -0 contaria */
        expect(cerebro.ultimoMotivo, `decisao ${m.n}`).toStrictEqual(m);
      }
      expect(cerebro.motivos.length).toBe(vida.motivos.length);
      /* sem aprender, os pesos nunca saem do prior */
      expect(cerebro.pesos).toStrictEqual(tabelaPrior(cerebro.escala));
    });

    test(`${vida.dono} ${vida.semente}: a decisao e a do instinto do TS (distInstinto e o sorteio com o mesmo u)`, () => {
      for (const m of vida.motivos) {
        const obs = observacaoDe(m);
        const d = distInstinto(obs);
        const suporte = ACOES_LOBOS.filter(a => d[a] > 0);
        expect([...m.candidatos].sort(), `decisao ${m.n}: candidatos`).toEqual(suporte.sort());
        /* as probabilidades da politica: o peso efetivo sobre o total, na ordem dos candidatos (a de random.choices) */
        let total = 0;
        m.candidatos.forEach((a, i) => { total = i === 0 ? m.pesos[a]! : total + m.pesos[a]!; });
        for (const a of m.candidatos) expect(Object.is(m.pesos[a]! / total, d[a]), `decisao ${m.n}: p(${a})`).toBe(true);
        const rng = rngInstinto(m.u);
        const inst = agirInstinto(obs, rng);
        expect([inst.acao, inst.regra, rng.chamadas]).toEqual([m.acao, m.regra, m.u === null ? 0 : 1]);
        /* no tempo livre, os pesos que o instinto passa ao choices sao os pesos efetivos do cerebro, bit a bit */
        if (rng.pesos) expect(rng.pesos, `decisao ${m.n}: pesos do instinto`).toStrictEqual(m.candidatos.map(a => m.pesos[a]));
      }
    });
  }

  test("controle negativo: um peso mexido no ultimo bit e pego", () => {
    const m = G.l0[0].motivos.find(mm => mm.regra === "tempo_livre")!;
    const cerebro = new CerebroA();
    cerebro.agir(observacaoDe(m), rngDoGabarito(m.u));
    const errado = structuredClone(m);
    errado.pesos.brincar = errado.pesos.brincar! + Number.EPSILON * 4;
    expect(cerebro.ultimoMotivo).not.toStrictEqual(errado);
  });
});

describe("o nucleo dos lobos", () => {
  test("sortear = random.choices(k=1): bisect_right sobre a cumulativa, ate o ultimo indice", () => {
    expect(sortear([1, 1], 0)).toBe(0);
    expect(sortear([1, 1], 0.4999999999999999)).toBe(0);
    expect(sortear([1, 1], 0.5)).toBe(1);                       // u * total = 1 = cumulativa[0]: bisect_right passa adiante
    expect(sortear([3, 0, 1], 0.75)).toBe(2);                   // o peso zero nunca e sorteado
    expect(sortear([1, 2], 1 - 1e-16)).toBe(1);
    expect(() => sortear([0, 0], 0.5)).toThrow();
  });

  test("impulsos: regra determinista com um candidato, fome moderada com os dois lados, tempo livre com a populacao", () => {
    const obs = (fome: number, energia: number, tdc = 0, dormindo = 0, hora = 0.5): Observacao =>
      ({ v: [fome, 0.9, energia, 0.5, 1, 0, dormindo, hora], tdc });
    expect(impulsos(obs(0.9, 0.2))).toEqual({ regra: "sono_exaustao", candidatos: ["dormir"] });
    expect(impulsos(obs(0.9, 0.8, 0, 1))).toEqual({ regra: "sono_continuar", candidatos: ["dormir"] });
    expect(impulsos(obs(0.2, 0.9))).toEqual({ regra: "pedido_necessidade", candidatos: ["chamar_atencao"] });
    expect(impulsos(obs(0.9, 0.9, 241))).toEqual({ regra: "abandono", candidatos: ["chamar_atencao"] });
    expect(impulsos(obs(0.4, 0.9))).toEqual({ regra: "fome_moderada", candidatos: ["comer", "chamar_atencao"] });
    expect(impulsos(obs(0.9, 0.9))).toEqual({ regra: "tempo_livre", candidatos: ["ocioso", "explorar", "brincar", "chamar_atencao"] });
  });

  test("agirInstinto = distInstinto numa grade de observacoes (o suporte e as regras deterministas)", () => {
    const grade = [0, 0.2, 0.249, 0.25, 0.3, 0.449, 0.45, 0.54, 0.55, 0.84, 0.85, 1];
    let n = 0;
    for (const fome of grade) for (const energia of grade) for (const humor of [0.2, 0.35, 0.8]) for (const dormindo of [0, 1])
      for (const hora of [0, 0.3, 0.6, 0.95]) for (const tdc of [0, 240, 241, 600]) {
        const o: Observacao = { v: [fome, 0.9, energia, humor, 1, 0, dormindo, hora], tdc };
        const d = distInstinto(o);
        const { candidatos } = impulsos(o);
        expect([...candidatos].sort()).toEqual(ACOES_LOBOS.filter(a => d[a] > 0).sort());
        if (candidatos.length === 1) expect(d[candidatos[0] as AcaoPet]).toBe(1);
        n++;
      }
    expect(n).toBe(grade.length ** 2 * 3 * 2 * 4 * 4);
  });

  test("a tabela: sete regras x sete acoes x dez entradas, no prior inteiro (o vies 3 do ocioso = 3 S)", () => {
    const c = new CerebroA();
    expect(c.escala).toBe(1024);
    expect(c.nPesos()).toBe(7 * 7 * 10);
    expect(c.prior.tempo_livre.ocioso[0]).toBe(3 * 1024);
    expect(c.prior.tempo_livre.explorar).toEqual([2048, 0, 0, 2048, 0, 0, 0, 0, 0, 0]);
    expect(c.prior.sono_noite.comer.every(w => w === 0)).toBe(true);
  });

  test("o aprendizado e a etapa 3: ligado, falha alto", () => {
    expect(() => new CerebroA({ ...CLB, aprendizadoLigado: true })).toThrow(/etapa 3/);
    expect(() => new CerebroA({ ...CLB, aprendizadoLigado: false, maxPesos: 490 })).toThrow(/teto/);
  });

  test("nenhuma funcao transcendental no nucleo (Math.exp, Math.log)", () => {
    const fonte = readFileSync(new URL("../motor/lobos.ts", import.meta.url), "utf8").replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, "");
    expect(fonte).not.toMatch(/Math\.(exp|log|expm1|log1p|log2|log10|pow|sin|cos|tan|sqrt)\b/);
  });
});
