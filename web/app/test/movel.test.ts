// A tela Pet no celular (M1 do mobile minimo; docs/PROPOSTAS_V3_UX_TELA_PET.md, "Mobile minimo"). Sem DOM (vitest em node): renderToStaticMarkup.
// Cobre: o icone do agora (o nome acessivel e o da linha de hoje, o tracejado ciano so no "aprendido", o "?" sem decisao, so desenho sem o botao), o icone
// de cada acao do pet (o tsc ja acusa uma acao nova; aqui, que sao sete e distintos onde importa), o estado do leque (um por vez, o segundo toque fecha)
// e o tempo do toque longo (PROPOSTO, SEM FONTE, M1-9).
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { afterEach, describe, expect, test, vi } from "vitest";
import { SEGURAR_MS, Segurador, alternarLeque, fecharLeque, lerLeque, mudarLeque } from "../src/movel.ts";
import { BotaoMovel } from "../src/componentes/BotaoMovel.tsx";
import { AgoraIconeVista, ICONE_AGORA, rotuloAgora, type VistaAgora } from "../src/telas/pet/LinhaAgora.tsx";

const vista = (caso: VistaAgora["caso"]): VistaAgora => ({ caso, acao: "brincando", regra: "Tempo livre", semEle: caso === "aprendido" ? "à toa" : null });
const agora = (v: VistaAgora, abrir = true): string => renderToStaticMarkup(h(AgoraIconeVista, { v, icone: ICONE_AGORA.brincar, aoAbrir: abrir ? () => {} : undefined }));

describe("o icone do agora no celular", () => {
  test("o nome acessivel e o da linha de hoje, e nenhum texto fixo na tela", () => {
    for (const caso of ["aprendido", "instinto", "uma", "sem", "modular"] as const) {
      const s = agora(vista(caso));
      expect(s).toContain(`aria-label="${rotuloAgora(vista(caso), true)}"`);
      expect(s).not.toMatch(/>agora</i);
    }
  });
  test("o caso vai no data-caso (o ciano tracejado e so do 'aprendido', por CSS) e o '?' so aparece sem decisao", () => {
    expect(agora(vista("aprendido"))).toContain('data-caso="aprendido"');
    expect(agora(vista("instinto"))).toContain('data-caso="instinto"');
    expect(agora(vista("sem"))).toContain("mm-agora-q");
    expect(agora(vista("instinto"))).not.toContain("mm-agora-q");
  });
  test("sem o botao (detalhes do pet desligados, M1-11) e so desenho, sem toque, com o texto lido da linha", () => {
    const s = agora(vista("uma"), false);
    expect(s).not.toContain("<button");
    expect(s).toContain('role="img"');
    expect(s).toContain(`aria-label="${rotuloAgora(vista("uma"), false)}"`);
  });
  test("cada acao do pet tem o seu icone, e a dormindo e a lua (nao a xicara)", () => {
    expect(Object.keys(ICONE_AGORA).sort()).toEqual(["brincar", "chamar_atencao", "comer", "dormir", "emburrar", "explorar", "ir_tv", "ocioso"]);   // o ir_tv: a v33 (D-GV-TVJOGO-3)
    expect(ICONE_AGORA.dormir).not.toBe(ICONE_AGORA.ocioso);
  });
});

describe("o leque (o retrato e o Mais): um por vez", () => {
  afterEach(() => mudarLeque(null));
  test("abrir um fecha o outro; o segundo toque no mesmo fecha", () => {
    expect(lerLeque()).toBeNull();
    alternarLeque("paineis"); expect(lerLeque()).toBe("paineis");
    alternarLeque("mais"); expect(lerLeque()).toBe("mais");
    alternarLeque("mais"); expect(lerLeque()).toBeNull();
  });
  test("fechar o Mais nao derruba o leque do retrato", () => {
    alternarLeque("paineis");
    fecharLeque("mais"); expect(lerLeque()).toBe("paineis");
    fecharLeque("paineis"); expect(lerLeque()).toBeNull();
  });
});

describe("o botao so de icone", () => {
  test("o toque longo e de 500 ms (PROPOSTO, SEM FONTE, M1-9)", () => { expect(SEGURAR_MS).toBe(500); });
  test("sem aria-label o nome vai em sr-only; com aria-label (o nome de hoje) nao se repete; o balao so existe ao segurar", () => {
    const sem = renderToStaticMarkup(h(BotaoMovel, { rotulo: "Carinho", className: "mm-bt" }));
    expect(sem).toContain('<span class="sr-only">Carinho</span>');
    expect(sem).not.toContain("mm-rotulo");
    const com = renderToStaticMarkup(h(BotaoMovel, { rotulo: "Alimentar", "aria-label": "Alimentar (reserva: põe a ração no comedouro)" }));
    expect(com).not.toContain("sr-only");
  });
});

describe("o toque longo (Segurador)", () => {
  test("so o dedo arma o balao; segurar mais de 500 ms mostra o nome, e a acao do botao nao e suprimida nem adiada", () => {
    vi.useFakeTimers();
    try {
      const estados: boolean[] = [], seg = new Segurador(v => estados.push(v));
      seg.baixo("mouse"); vi.advanceTimersByTime(2000);
      expect(seg.segurando).toBe(false);
      seg.baixo("pen"); vi.advanceTimersByTime(2000);
      expect(seg.segurando).toBe(false);
      seg.baixo("touch"); vi.advanceTimersByTime(SEGURAR_MS - 1);
      expect(seg.segurando).toBe(false);
      vi.advanceTimersByTime(1);
      expect(seg.segurando).toBe(true);
      seg.parar();
      expect(seg.segurando).toBe(false);
      expect(estados).toEqual([true, false]);
    } finally { vi.useRealTimers(); }
  });
  test("o clique de um toque longo sai igual: o botao nao tem onClickCapture nem preventDefault de clique (so o menu de contexto, fora do mouse)", () => {
    let acionou = 0;
    const s = renderToStaticMarkup(h(BotaoMovel, { rotulo: "Brincar", onClick: () => { acionou++; } }));
    expect(s).toContain("<button");
    const fonte = readFileSync(new URL("../src/componentes/BotaoMovel.tsx", import.meta.url), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    expect(fonte).not.toMatch(/onClickCapture|stopPropagation|suprimir/);
    expect(fonte.match(/preventDefault/g)?.length).toBe(1);
    expect(fonte).toMatch(/onContextMenu: \(e[^)]*\) => \{ if \(tipo\.current !== "mouse"\) e\.preventDefault\(\); \}/);
    expect(acionou).toBe(0);
  });
});
