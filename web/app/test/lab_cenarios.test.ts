// Laboratorio > Cenarios (2026-11-07): os pets do cenario nascem na versao de hoje (VERSAO_PET), e nao na v5 do treinarPet do motor,
// que nao abre mais (D-LE-E2-9). Sem DOM (vitest em node):
//   - cada cenario pronto monta os dois pets vivos na versao de hoje; o A vira o pet ativo e o save dele reabre (lerSave) com o mesmo
//     registro; o B fica para a comparacao;
//   - a luta monta: desde a LP4 da LUTA_POC, a luta da POC A x B (os numeros dos 6 stats de cada um) roda no nucleo;
//   - o pet de antes fica guardado para voltar; a escada de exemplo (sem tratar a lesao) nao muda: o mesmo pet de antes da opcao.
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { Motor, VERSAO_PET, lutarNucleoPoc, sorteiosPoc } from "../motor/index.ts";
import { iniciarJogo, jogoAtual } from "../src/jogo.ts";
import { CHAVE, lerSave, textoSave, type Armazenamento } from "../src/save.ts";
import { ESCADA, petDaReceita } from "../src/pets.ts";
import { CHAVE_ANTERIOR } from "../src/telas/pet/MeusPets.tsx";
import { CENARIOS, montarCenario, resumoPet } from "../src/telas/diario/TelaCenarios.tsx";

let dados: Record<string, string>;
const armaz = (): Armazenamento => ({ getItem: k => (k in dados ? dados[k]! : null), setItem(k, v) { dados[k] = v; } });
beforeEach(() => {
  dados = {};
  vi.stubGlobal("localStorage", { getItem: (k: string) => (k in dados ? dados[k]! : null), setItem: (k: string, v: string) => { dados[k] = v; }, removeItem: (k: string) => { delete dados[k]; } });
});
afterEach(() => { vi.unstubAllGlobals(); });

describe("os Cenarios do Lab", () => {
  test.each(CENARIOS.map(c => [c.id, c] as const))("%s: os dois pets na versao de hoje, o A abre e a luta monta", (_id, cen) => {
    const hoje = new Motor(555); hoje.avancar(300); hoje.observar("alimentar");
    dados[CHAVE] = textoSave(hoje);
    iniciarJogo(armaz());
    const { A, B } = montarCenario(cen, 1);
    for (const m of [A, B]) { expect(m.versao).toBe(VERSAO_PET); expect(m.morte).toBeNull(); }
    /* o A e o pet ativo e o save dele reabre, com o mesmo registro */
    expect(jogoAtual().motor).toBe(A);
    const lido = lerSave(armaz());
    expect(lido.tipo).toBe("ok");
    if (lido.tipo !== "ok") return;
    expect(lido.motor.versao).toBe(VERSAO_PET);
    expect(textoSave(lido.motor)).toBe(textoSave(A));
    /* o pet de antes ficou guardado para voltar */
    expect(dados[CHAVE_ANTERIOR]).toBe(textoSave(hoje));
    /* a luta da POC A x B, no Campo de treino, com os numeros de cada um (a tela roda 100 delas) */
    const r = lutarNucleoPoc({ cena: "campo", semente: 7, a: { forma: A.formaLutaPoc, stats: A.statsLutaPoc() }, b: { forma: B.formaLutaPoc, stats: B.statsLutaPoc() } }, sorteiosPoc(7));
    expect(r.passos).toBeGreaterThan(0);
    /* a tabela lado a lado sai dos dois pets */
    for (const [m, l] of [[A, cen.a], [B, cen.b]] as const) expect(resumoPet(m, l).total).toBeGreaterThanOrEqual(0);
  }, 120_000);

  test("mesma semente, mesmo cenario", () => {
    iniciarJogo(armaz());
    const a1 = textoSave(montarCenario(CENARIOS[1], 3).A), a2 = textoSave(montarCenario(CENARIOS[1], 3).A);
    expect(a1).toBe(a2);
  }, 120_000);

  test("o dono simulado trata a lesao: sem isso o pet de varios dias morre da lesao do sparring", () => {
    /* a semente 4243: na v23 (a luta da rodada de equilibrio, LP5-5) o pet da 4242 ja nao morre da lesao em 5 dias */
    const r = { dono: "atencioso" as const, dias: 5, porDia: 16, treinoDia: 0, semente: 4243 };
    expect(() => petDaReceita(r)).toThrow(/lesão/);
    const m = petDaReceita(r, true);
    expect(m.morte).toBeNull();
    expect(m.log.some(e => e[1] === "d" && e[2] === "tratar_lesao")).toBe(true);
  }, 120_000);

  test("a escada de exemplo nao muda: sem a opcao, o pet sai o mesmo de sempre", () => {
    /* a receita mais forte (treino, sparring): sem lesao tratada nenhum evento tratar_lesao entra no registro */
    const m = petDaReceita(ESCADA[5]);
    expect(m.log.some(e => e[1] === "d" && e[2] === "tratar_lesao")).toBe(false);
  }, 120_000);
});
