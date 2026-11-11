// O scan do DigiBrain no pet do cerebro modular (src/componentes/ScanDigiBrainLab.tsx; pedidos do Matheus de 2026-11-11). Sem DOM (vitest em
// node): renderToStaticMarkup. O desenho e a rede viva do scan do A (uma ilustracao; test/scan_digibrain.test.ts a cobre). Aqui: o que a
// faixa do modular le do motor (a onda, um pico por modulo que contribuiu, e a escolha de agora com a chance) e a falha alta.
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test } from "vitest";
import { ORDEM_TERMOS, type LeituraLab } from "../motor/index.ts";
import { Motor } from "../motor/motor.ts";
import { TPD } from "../motor/constantes.ts";
import { petDeTeste } from "../motor/pet_lab.ts";
import { rotuloUnidade } from "../src/componentes/DigiBrainLab.tsx";
import { pontosDaOnda } from "../src/componentes/ScanDigiBrain.tsx";
import { FaixaLab, escolhaDoModular, picosDoModular } from "../src/componentes/ScanDigiBrainLab.tsx";

function leituras(semente: number, n: number): LeituraLab[] {
  const m: Motor = petDeTeste(semente), fora: LeituraLab[] = [];
  for (let p = 0; p < Math.round(2 * TPD / 30); p++) {
    m.avancar(30);
    const mu = m.mundo!;
    if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
    if (p % 5 === 0) m.observar("acariciar");
  }
  for (let i = 0; i < 300 && fora.length < n; i++) { m.avancar(15); const l = m.leituraLab(); if (l && !fora.some(x => x.k === l.k)) fora.push(l); }
  return fora;
}
const LS = leituras(101, 40);

describe("a faixa do modular no scan", () => {
  test("o pet de teste tem decisoes com barras, a favor e contra", () => {
    expect(LS.length).toBeGreaterThan(10);
    expect(LS.some(l => l.barras.length > 0)).toBe(true);
  });
  test("a onda: um pico por modulo que contribuiu, com o sinal dele, e o maior com a altura inteira", () => {
    for (const l of LS) {
      const picos = picosDoModular(l);
      expect(picos.map(p => p.entrada)).toEqual(l.barras.map(b => b.termo));
      for (const [i, p] of picos.entries()) {
        expect(Math.sign(p.altura)).toBe(Math.sign(l.barras[i]!.permil));
        expect(Math.abs(p.altura)).toBeLessThanOrEqual(1);
      }
      if (picos.length) expect(Math.max(...picos.map(p => Math.abs(p.altura)))).toBe(1);
      /* os pontos: a base, tres por pico e o fim, na ordem dos modulos do motor */
      expect(pontosDaOnda(ORDEM_TERMOS, picos).split(" ").length).toBe(2 + 3 * picos.length);
    }
  });
  test("a escolha de agora: a acao da unidade escolhida e a chance dela", () => {
    for (const l of LS) {
      const e = escolhaDoModular(l), esc = l.chances.find(c => c.escolhida)!;
      expect(e.inteiro).toBe(rotuloUnidade(esc.chave));
      expect(e.curto).toBe(rotuloUnidade([esc.chave[0], null, null]));
      expect(e.chance).toBe(esc.permil === null ? "única" : Math.round(esc.permil / 10) + "%");
    }
  });
  test("a faixa em HTML: o numero da decisao, o rotulo \"escolha\", o tom neutro e nenhum estado inventado", () => {
    const l = LS.find(x => x.barras.length > 0)!, s = renderToStaticMarkup(h(FaixaLab, { l })), e = escolhaDoModular(l);
    expect(s).toContain(`data-n="${l.k}"`);
    expect(s).toContain('data-tom="neutro"');
    expect(s).toContain(">escolha<");
    expect(s).toContain(e.curto);
    expect(s).toContain(`<span class="scan-estado-pct">${e.chance}</span>`);
    expect(s).not.toMatch(/estado atual|calmo/i);
  });
  test("falha alto sem a opcao escolhida", () => {
    const l: LeituraLab = { ...LS[0]!, chances: LS[0]!.chances.map(c => ({ ...c, escolhida: false })) };
    expect(() => renderToStaticMarkup(h(FaixaLab, { l }))).toThrow(/escolhida/);
  });
});
