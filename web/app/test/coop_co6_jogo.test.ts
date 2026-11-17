/* A CO6 no grupo do jogo (docs/ESPEC_V3_COOPERACAO_CO6.md, 2.3 e 2.4): o M-SENS do modular le a reputacao e o peso dos deveres da percepcao
   social, e o painel do DigiBrain os mostra em palavras, sem numero (D-MM-8, CO6-7).
   - a chave fica DESLIGADA nos grupos de antes da v37 (D-CO6c-1): o estado do cerebro nao tem a chave `social`; a v37 a liga ("Sim, juntas",
     Matheus, 2026-11-12, com a CO7);
   - ligada na v36 pelo parametro (so nos testes), o G-SEM-DECISAO-CO6 no jogo: os dois pets vivem igual a CO6 desligada (o mesmo registro e os mesmos motivos de
     cada decisao); o M-SENS guarda o que a percepcao trouxe, que e a reputacao e o k da Cooperacao do grupo;
   - o texto do painel: confia, ainda nao confia, desconfia; sente o dever pouco, medio ou muito; nenhum algarismo. */
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test } from "vitest";
import { GrupoDoJogo, TPD, VERSAO_GRUPO, VERSAO_V36 } from "../motor/index.ts";
import { ComOIrmao, textoConfianca, textoDever } from "../src/componentes/DigiBrainLab.tsx";

function viver(co6: boolean): GrupoDoJogo {
  const g = new GrupoDoJogo(202, VERSAO_V36, true, co6);
  for (const i of g.ids) g.agir(i, m => m.trocarCerebro("modular"));     // o ovo escolhe o modular (src/cerebro.ts, o padrao dos ovos novos)
  for (let k = 0; k < (3 * TPD) / 15; k++) {
    g.avancar(15);
    if (k % 8 === 0) g.agir(k % 16 === 0 ? "A" : "B", m => m.observar("alimentar"));
  }
  return g;
}
const LIGADA = viver(true), DESLIGADA = viver(false);

describe("a CO6 no grupo do jogo", () => {
  test("desligada nos grupos de antes (v36), ligada no de hoje (v37), e o cerebro so ganha a chave social com ela", () => {
    expect(new GrupoDoJogo(101, VERSAO_V36).grupo.coop!.cfg.co6).toBe(false);
    expect(VERSAO_GRUPO).toBe(39);
    expect(new GrupoDoJogo(101, VERSAO_GRUPO).grupo.coop!.cfg.co6).toBe(true);
    for (const m of Object.values(DESLIGADA.motores)) {
      expect(m.lab).not.toBeNull();
      expect(m.lab!.sens.social).toBeNull();
      expect("social" in m.lab!.estadoInterno()).toBe(false);
    }
    expect(() => new GrupoDoJogo(101, VERSAO_V36, false, true)).toThrow(/medida/);
  });

  test("o G-SEM-DECISAO-CO6 no jogo: o mesmo registro e os mesmos motivos, decisao a decisao", () => {
    expect(JSON.stringify(LIGADA.log)).toBe(JSON.stringify(DESLIGADA.log));
    for (const i of Object.keys(LIGADA.motores)) {
      const a = LIGADA.motores[i]!.lab!, b = DESLIGADA.motores[i]!.lab!;
      expect(a.motivos.length).toBeGreaterThan(100);
      expect(JSON.stringify(a.motivos)).toBe(JSON.stringify(b.motivos));
      const { social: _s, ...resto } = a.estadoInterno();
      expect(JSON.stringify(resto)).toBe(JSON.stringify(b.estadoInterno()));
    }
  });

  test("o M-SENS leu a reputacao do irmao e o proprio k, os da Cooperacao do grupo", () => {
    const c = LIGADA.grupo.coop!;
    for (const [i, m] of Object.entries(LIGADA.motores)) {
      const s = m.lab!.sens.social!, outro = i === "A" ? "B" : "A";
      expect(Object.keys(s.reputacao)).toEqual([outro]);
      expect(s.peso_dever).toBeGreaterThanOrEqual(0);
      expect(s.peso_dever).toBeLessThanOrEqual(c.tetoK(4 * TPD));
      expect(m.lab!.estadoInterno()["social"]).toEqual({ reputacao: s.reputacao, peso_dever: s.peso_dever });
    }
    const passos = LIGADA.grupo.coop!.resumo(LIGADA.grupo.idsPresentes(), LIGADA.grupo.tick)["peso_dever"] as Record<string, number>;
    expect(Object.keys(passos).sort()).toEqual(["A", "B"]);
  });
});

describe("o painel, em palavras", () => {
  test("a confianca e o dever, sem numero", () => {
    expect([textoConfianca(12), textoConfianca(0), textoConfianca(-3)]).toEqual(["Confia no irmão", "Ainda não confia no irmão", "Desconfia do irmão"]);
    expect([0, 255, 256, 511, 512, 1024].map(k => textoDever(k, 1024)))
      .toEqual(["Sente o dever: pouco", "Sente o dever: pouco", "Sente o dever: médio", "Sente o dever: médio", "Sente o dever: muito", "Sente o dever: muito"]);
    expect(() => textoDever(1025, 1024)).toThrow();
    expect(() => textoConfianca(0.5)).toThrow();
  });

  test("a secao Com o irmao no HTML, com o que o cerebro do pet leu", () => {
    for (const m of Object.values(LIGADA.motores)) {
      const html = renderToStaticMarkup(h(ComOIrmao, { social: m.lab!.sens.social!, S: m.lab!.sens.S }));
      expect(html).toContain("Com o irmão");
      expect(html).toContain("Sente o dever:");
      expect(/\d/.test(html.replace(/<[^>]*>/g, ""))).toBe(false);
    }
  });
});
