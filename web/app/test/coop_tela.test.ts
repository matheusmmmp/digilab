/* A cooperacao na tela (docs/TAREFA_V3_COOPERACAO.md, etapa CO5): sem numero (D-MM-8).
   - o icone de cada ato na ilha e o texto dele em Ultimas acoes, do ponto de vista do pet em foco;
   - o gesto do irmao depois da luta: o resultado e a reputacao (D-CO5-2), sem sorteio;
   - a medida ligada no jogo (o GrupoDoJogo) so mede: o grupo com ela da a mesma vida que um grupo sem ela (o G-SEM-DECISAO no jogo). */
import { describe, expect, test } from "vitest";
import { CONFIG_GRUPO_LIGADA, Grupo, GrupoDoJogo, TPD, VERSAO_V25, gestoDepoisDaLuta } from "../motor/index.ts";
import { iconeDoAto, textoDoAto } from "../src/telas/pet/AtosDoIrmao.tsx";

describe("os atos na tela", () => {
  test("o icone: o coracao para deixar e encostar, a comida riscada so para pegar a de quem tinha fome", () => {
    expect(iconeDoAto({ ato: "contencao", sinal: 1 })).toBe("coracao");
    expect(iconeDoAto({ ato: "encostar", sinal: 1 })).toBe("coracao");
    expect(iconeDoAto({ ato: "disputa", sinal: -1 })).toBe("comida_riscada");
    expect(iconeDoAto({ ato: "disputa", sinal: 0 })).toBeNull();
  });

  test("o texto, do ponto de vista do pet em foco, sem nome e sem numero", () => {
    const a = { ato: "contencao" as const, sinal: 1, autor: "A", alvo: "B" };
    expect(textoDoAto(a, "A")).toBe("deixou a comida para o irmão");
    expect(textoDoAto(a, "B")).toBe("o irmão deixou a comida para ele");
    expect(textoDoAto({ ato: "disputa", sinal: -1, autor: "B", alvo: "A" }, "A")).toBe("o irmão pegou a comida dele, quando estava com fome");
    expect(textoDoAto({ ato: "disputa", sinal: 0, autor: "A", alvo: "B" }, "A")).toBe("pegou a comida que o irmão queria");
    expect(textoDoAto({ ato: "encostar", sinal: 1, autor: "A", alvo: "B" }, "A")).toBe("encostou no irmão, que estava emburrado");
    expect(textoDoAto(a, "C")).toBeNull();
    for (const t of [textoDoAto(a, "A")!, textoDoAto(a, "B")!]) expect(/\d/.test(t)).toBe(false);
  });
});

describe("o gesto do irmao depois da luta", () => {
  test("a reputacao negativa provoca; senao, comemora a vitoria e consola a derrota e o empate", () => {
    expect([gestoDepoisDaLuta(0, true), gestoDepoisDaLuta(0, false), gestoDepoisDaLuta(0, null)]).toEqual(["comemora", "consola", "consola"]);
    expect([gestoDepoisDaLuta(5, true), gestoDepoisDaLuta(-1, true), gestoDepoisDaLuta(-1, false)]).toEqual(["comemora", "provoca", "provoca"]);
  });

  test("no grupo do jogo, pela reputacao de agora", () => {
    const g = new GrupoDoJogo(101, VERSAO_V25);
    expect(g.grupo.coop).not.toBeNull();
    expect(g.gestoDoIrmao("A", false)).toEqual({ irmao: "B", gesto: "consola" });
    expect(g.gestoDoIrmao("B", true)).toEqual({ irmao: "A", gesto: "comemora" });
    expect(() => g.gestoDoIrmao("C", true)).toThrow(/fora do grupo/);
  });
});

describe("a medida ligada no jogo so mede", () => {
  test("o G-SEM-DECISAO no jogo: com a medida e sem ela, os dois pets vivem igual (a mesma assinatura)", () => {
    const viver = (medir: boolean) => {
      const h = new GrupoDoJogo(202, VERSAO_V25, medir);
      for (let k = 0; k < (2 * TPD) / 15; k++) { h.avancar(15); if (k % 8 === 0) h.agir(k % 16 === 0 ? "A" : "B", m => m.observar("alimentar")); }
      return h;
    };
    const g = viver(true), sem = viver(false);
    expect(sem.grupo.coop).toBeNull();
    expect(g.assinatura()).toBe(sem.assinatura());
    expect(JSON.stringify(g.log)).toBe(JSON.stringify(sem.log));
    const r = GrupoDoJogo.reproduzir(202, VERSAO_V25, g.log);
    expect(r.assinatura()).toBe(g.assinatura());
    expect(g.grupo.coop!.atos.length).toBe(r.grupo.coop!.atos.length);
    /* a medida nao entra na assinatura nem no registro: ela e derivada (o G-SEM-DECISAO do motor esta no test/cooperacao.test.ts) */
    expect(JSON.stringify(g.log)).not.toContain("contencao");
    expect(new Grupo(g.grupo.cm, 1, CONFIG_GRUPO_LIGADA).coop).toBeNull();
  });
});
