/* A viagem da camera e os atalhos do lugar (L2 de "Lugares da ilha"): so vista, sem motor. O progresso anda a 1/VIAGEM_MS, o corte seco vale com a
   viagem desligada, clicar/Esc pula, e os efeitos curtos dos itens cobrem todos os itens. */
import { readFileSync } from "node:fs";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { ITENS } from "../motor/index.ts";
import { LIVRE, andar, irPara, seguirPet, zerarCamera } from "../src/telas/pet/cameraLivre.ts";
import { toqueIgnorado } from "../src/telas/pet/ToquePet.tsx";
import { atalhoDaTecla } from "../src/atalhosLugar.ts";
import { efeitoCurto, nomeCurto } from "../src/telas/crescer/TelaItens.tsx";
import { PAINEL_MS, VIAGEM, VIAGEM_MS, entrarLugar, lugarAtual, escolherViagem, lugarAberto, pularViagem, progressoViagem, sairLugar, viagemLigada, viajando, zerarViagem } from "../src/viagem.ts";

describe("viagem da camera", () => {
  beforeEach(() => { zerarViagem(); escolherViagem(true); });
  afterEach(() => { zerarViagem(); escolherViagem(true); });

  it("as duracoes sao as da proposta", () => { expect(VIAGEM_MS).toBe(700); expect(PAINEL_MS).toBe(180); });
  it("vai de 0 a 1 em VIAGEM_MS e volta", () => {
    entrarLugar(1000);
    expect(lugarAberto()).toBe(true);
    expect(progressoViagem(1000)).toBe(0);
    expect(progressoViagem(1350)).toBeCloseTo(0.5, 6);
    expect(viajando(1350)).toBe(true);
    expect(progressoViagem(1000 + VIAGEM_MS)).toBe(1);
    expect(progressoViagem(5000)).toBe(1);
    expect(viajando(5000)).toBe(false);
    sairLugar(6000);
    expect(progressoViagem(6350)).toBeCloseTo(0.5, 6);
    expect(progressoViagem(7000)).toBe(0);
  });
  it("sair no meio volta do ponto em que estava", () => {
    entrarLugar(0); sairLugar(210);
    expect(progressoViagem(210)).toBeCloseTo(0.3, 6);
    expect(progressoViagem(420)).toBe(0);
  });
  it("clicar ou Esc pula para o fim", () => {
    entrarLugar(0); pularViagem(100);
    expect(progressoViagem(100)).toBe(1);
    expect(viajando(100)).toBe(false);
  });
  it("com a viagem desligada, o corte e seco", () => {
    escolherViagem(false);
    expect(viagemLigada()).toBe(false);
    entrarLugar(0);
    expect(progressoViagem(0)).toBe(1);
    sairLugar(10);
    expect(progressoViagem(10)).toBe(0);
  });
});

describe("viagem com os tres lugares (L3)", () => {
  beforeEach(() => { zerarViagem(); escolherViagem(true); });
  afterEach(() => { zerarViagem(); escolherViagem(true); });

  it("o saco e o padrao e nada muda para ele", () => {
    entrarLugar(0);
    expect(lugarAtual()).toBe("saco");
    expect(progressoViagem(VIAGEM_MS)).toBe(1);
    expect(VIAGEM.origem).toBeNull();
  });
  it.each(["portao", "barraca"] as const)("%s: vai de 0 a 1 em VIAGEM_MS e volta", l => {
    entrarLugar(1000, l);
    expect(lugarAberto()).toBe(true);
    expect(lugarAtual()).toBe(l);
    expect(progressoViagem(1350)).toBeCloseTo(0.5, 6);
    expect(progressoViagem(1000 + VIAGEM_MS)).toBe(1);
    sairLugar(3000);
    expect(progressoViagem(3000 + VIAGEM_MS)).toBe(0);
    expect(lugarAberto()).toBe(false);
  });
  it("a troca direta parte do lugar de antes (a origem) e nao passa pela ilha", () => {
    entrarLugar(0, "portao");
    pularViagem(10);
    entrarLugar(100, "barraca");
    expect(lugarAtual()).toBe("barraca");
    expect(VIAGEM.origem).toBe("portao");
    expect(progressoViagem(100)).toBeGreaterThan(0);
    expect(progressoViagem(100 + VIAGEM_MS)).toBe(1);
    sairLugar(2000);
    expect(VIAGEM.origem).toBeNull();
  });
  it("trocar para o mesmo lugar nao faz nada", () => {
    entrarLugar(0, "portao"); pularViagem(10);
    entrarLugar(20, "portao");
    expect(progressoViagem(20)).toBe(1);
    expect(VIAGEM.origem).toBeNull();
  });
  it("com a viagem desligada, a troca tambem e um corte seco", () => {
    escolherViagem(false);
    entrarLugar(0, "portao");
    entrarLugar(5, "barraca");
    expect(progressoViagem(5)).toBe(1);
  });
});

describe("atalhos do lugar", () => {
  it("C, L, D, 1 a 4 e Esc (L e D sao da L3)", () => {
    expect(atalhoDaTecla("KeyC")).toBe("c");
    expect(atalhoDaTecla("KeyL")).toBe("l");
    expect(atalhoDaTecla("KeyD")).toBe("d");
    expect(atalhoDaTecla("Escape")).toBe("esc");
    expect([1, 2, 3, 4].map(n => atalhoDaTecla("Digit" + n))).toEqual(["1", "2", "3", "4"]);
    expect(atalhoDaTecla("KeyX")).toBeNull();
  });
});

describe("efeitos curtos dos itens", () => {
  it("todo item tem nome curto e efeito de 2 a 4 palavras", () => {
    for (const it of ITENS) {
      const palavras = efeitoCurto(it).match(/[\p{L}\p{N}]+(?:[-'’][\p{L}\p{N}]+)*/gu) ?? [];
      expect(palavras.length, it.id).toBeGreaterThanOrEqual(2);
      expect(palavras.length, it.id).toBeLessThanOrEqual(4);
      expect(nomeCurto(it).length, it.id).toBeGreaterThan(0);
    }
  });
  it("os chips de stat saem dos pontos do motor", () => {
    const forca = ITENS.find(i => i.id === "chip_forca")!;
    expect(efeitoCurto(forca)).toBe("+1 força +1 vigor");
    expect(efeitoCurto(ITENS.find(i => i.id === "carta_folego")!)).toBe("+20 guts");
  });
});

describe("o lugar aberto fica so vista (R1, C1)", () => {
  beforeEach(() => { zerarViagem(); zerarCamera(); });
  afterEach(() => { zerarViagem(); zerarCamera(); });
  it("com o lugar aberto o toque no pet e ignorado", () => {
    expect(toqueIgnorado()).toBe(false);
    entrarLugar(0);
    expect(toqueIgnorado()).toBe(true);
    sairLugar(1);
    expect(toqueIgnorado()).toBe(false);
  });
  it("com o lugar aberto a camera nao solta (andar, irPara e seguirPet)", () => {
    const lim = { x0: 0, z0: 0, x1: 10, z1: 10 };
    entrarLugar(0);
    andar(1, 0, [0, 1], lim); irPara(3, 3, 0); seguirPet(0);
    expect(LIVRE.solta).toBe(false);
    sairLugar(1);
    andar(1, 0, [0, 1], lim);
    expect(LIVRE.solta).toBe(true);
  });
});

describe("contraste das pecas apagadas do lugar (A9)", () => {
  const css = readFileSync(new URL("../src/estilo/lugar.css", import.meta.url), "utf8");
  it("falta, trancada e fechado usam --hx-sec no texto e --hx-borda-topo na borda, sem opacity (os dois ja passam 4,5:1 e 3:1 no hx_pele)", () => {
    for (const sel of [".it2--falta .it2{", ".evl-selo--falta{", ".evl-no--fechado{", ".it2-vaga--trancada{"]) {
      const i = css.indexOf(sel); expect(i, sel).toBeGreaterThanOrEqual(0);
      expect(css.slice(i, css.indexOf("}", i)), sel).not.toContain("opacity");
    }
    expect(css).toContain(".it2--falta .it2{ border-style:dashed; border-color:var(--hx-borda-topo)");
    expect(css).toContain(".evl-no--fechado{ border-style:dotted; border-color:var(--hx-borda-topo); color:var(--hx-sec)");
  });
});
