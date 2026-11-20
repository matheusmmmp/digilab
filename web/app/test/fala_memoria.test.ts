/* A paridade da fidelidade da fala com a memoria autobiografica (C4, M6, MA-8): o TS = o Python (test/gabaritos/fala_memoria_python.json,
   experiments/exportar_gabarito_fala_memoria.py), caso a caso. O T-ME-6 no jogo: a fala que alega lembranca, causa por memoria ou
   mudanca de faceta sem o registro e marcada. Nenhuma LLM. */
import { describe, expect, test } from "vitest";
import { conferirFalaMemoria, type FatoFala } from "../src/falaMemoria.ts";
import { readFileSync } from "node:fs";

interface Caso { nome: string; fatos: FatoFala[]; fala: string; alegacoes: unknown[] }
const casos = (JSON.parse(readFileSync(new URL("./gabaritos/fala_memoria_python.json", import.meta.url), "utf8")) as { casos: Caso[] }).casos;

describe("fala com memoria: o TS confere como o Python", () => {
  for (const c of casos) test(c.nome, () => expect(conferirFalaMemoria(c.fala, c.fatos)).toEqual(c.alegacoes));
  test("as tres lacunas: sem o registro, a alegacao fica sem fato", () => {
    const semFato = (n: string) => casos.find(c => c.nome === n)!.alegacoes.map(a => (a as { sustentada: boolean }).sustentada);
    expect(semFato("lacuna1_lembranca_sem_registro")).toEqual([false]);
    expect(semFato("lacuna2_causa_sem_sonda")).toEqual([false]);
    expect(semFato("lacuna3_faceta_sem_registro")).toEqual([false]);
    expect(semFato("a_v11_faceta_nao_confere")).toEqual([false]);
    expect(semFato("a_v11_causa_sem_sonda")).toEqual([false]);
    expect(semFato("a_v11_lembranca_com_fato_m")).toEqual([true]);
    expect(semFato("a_v11_negacao_nao_alega")).toEqual([]);
  });
});
