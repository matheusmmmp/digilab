// O scan do DigiBrain no pet do laboratorio (src/componentes/ScanDigiBrainLab.tsx; pedido do Matheus de 2026-11-11). Sem DOM (vitest em node):
// renderToStaticMarkup. Cobre: os 7 modulos sempre no desenho, um fio por barra (a parte do modulo na escolhida), o tracejado de quem puxou
// contra, uma opcao escolhida, a chance de cada opcao desenhada, o teto de opcoes no desenho com a escolhida sempre dentro, e o pulso so quando pedido.
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test } from "vitest";
import { ORDEM_TERMOS, type LeituraLab } from "../motor/index.ts";
import { Motor } from "../motor/motor.ts";
import { TPD } from "../motor/constantes.ts";
import { petDeTeste } from "../motor/pet_lab.ts";
import { MapaLab, OPCOES_NO_DESENHO, opcoesDoDesenho } from "../src/componentes/ScanDigiBrainLab.tsx";

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
const contar = (s: string, re: RegExp): number => (s.match(re) ?? []).length;
const LS = leituras(101, 40);

describe("o mapa do modular no scan", () => {
  test("o pet de teste tem decisoes com barras", () => {
    expect(LS.length).toBeGreaterThan(10);
    expect(LS.some(l => l.barras.length > 0)).toBe(true);
  });
  for (const movel of [false, true]) {
    test(`as contagens de cada decisao (${movel ? "390" : "1920"} px)`, () => {
      for (const l of LS) {
        const s = renderToStaticMarkup(h(MapaLab, { l, movel, movendo: false })), ops = opcoesDoDesenho(l);
        expect(s).toContain(`data-n="${l.k}"`);
        const acesas = s.match(/<g class="mp-acesas">(.*?)<\/g>/)![1]!;
        expect(contar(acesas, /<path /g)).toBe(l.barras.length);
        expect(contar(acesas, /class="mp-neg"/g)).toBe(l.barras.filter(b => b.permil < 0).length);
        for (const t of ORDEM_TERMOS) expect(s).toContain(`class="mp-no${l.barras.some(b => b.termo === t) ? " mp-lit mp-caminho" : ""}" data-termo="${t}"`);
        expect(contar(s, /class="mp-no mp-cand mp-esc" data-opcao=/g)).toBe(1);
        expect(contar(s, /class="mp-no mp-cand[^"]*" data-opcao=/g)).toBe(ops.length);
        expect(contar(s, /class="mp-pct"/g)).toBe(ops.length + l.barras.length);
        expect(s).not.toContain("mp-pulso");
      }
    });
  }
  test("o pulso: um ponto por barra, so quando pedido", () => {
    const l = LS.find(x => x.barras.length > 0)!;
    const s = renderToStaticMarkup(h(MapaLab, { l, movel: false, movendo: true }));
    expect(contar(s.match(/<g class="mp-pulso"[^>]*>(.*?)<\/g>/)![1]!, /<path /g)).toBe(l.barras.length);
  });
  test("o teto de opcoes no desenho: as de maior chance e a escolhida sempre dentro, na ordem da leitura", () => {
    const base = LS[0]!;
    const chances = Array.from({ length: 10 }, (_, i) => ({ chave: ["explorar", "vagar", i] as never, permil: 100 - i, escolhida: i === 9 }));
    const l: LeituraLab = { ...base, chances };
    const ops = opcoesDoDesenho(l);
    expect(ops.length).toBe(OPCOES_NO_DESENHO);
    expect(ops.some(c => c.escolhida)).toBe(true);
    expect(ops.map(c => c.permil)).toEqual([100, 99, 98, 97, 96, 95, 91]);
  });
  test("falha alto sem a opcao escolhida", () => {
    const l: LeituraLab = { ...LS[0]!, chances: LS[0]!.chances.map(c => ({ ...c, escolhida: false })) };
    expect(() => renderToStaticMarkup(h(MapaLab, { l, movel: false, movendo: false }))).toThrow(/escolhida/);
  });
});
