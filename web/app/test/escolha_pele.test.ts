/* T2 do tema dos menus (docs/TAREFA_V2_TEMA_MENUS.md §5): os cartoes da pele em Ajustes > Aparencia. Sem DOM (vitest em node):
   renderToStaticMarkup e leitura do CSS; o <html> e o localStorage sao objetos simples. As setas e a troca na tela ficam no e2e. */
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { EscolhaPele, PELES, resumoAparencia } from "../src/telas/config/EscolhaPele.tsx";
import { escolherPele } from "../src/pele.ts";

const css = readFileSync(new URL("../src/estilo/menus_config.css", import.meta.url), "utf8");
const tela = readFileSync(new URL("../src/telas/config/TelaConfig.tsx", import.meta.url), "utf8");
const html = { dataset: {} as Record<string, string> };

beforeEach(() => {
  const guardado: Record<string, string> = {};
  vi.stubGlobal("document", { documentElement: html });
  vi.stubGlobal("localStorage", { getItem: (k: string) => guardado[k] ?? null, setItem: (k: string, v: string) => { guardado[k] = v; } });
});
afterEach(() => { vi.unstubAllGlobals(); });

describe("EscolhaPele", () => {
  it("radiogroup rotulado, um radio por pele, so o escolhido na ordem de Tab, sem XCOM na tela", () => {
    escolherPele("vidro");
    const s = renderToStaticMarkup(h(EscolhaPele));
    expect(s).toContain('<h3 class="mc-sec" id="cfg-pele">Pele dos menus</h3>');
    expect(s).toContain('role="radiogroup" aria-labelledby="cfg-pele"');
    expect(s.match(/role="radio"/g)).toHaveLength(PELES.length);
    expect(s).toMatch(/role="radio" aria-checked="true" tabindex="0" class="[^"]*mc-opcao--pele-vidro"/);
    expect(s).toMatch(/role="radio" aria-checked="false" tabindex="-1" class="[^"]*mc-opcao--pele-xcom"/);
    expect(s).toContain("<b>Holográfico</b>");
    expect(s).toContain("<b>Militar</b>");
    expect(s.replace(/class="[^"]*"/g, "")).not.toMatch(/xcom/i);
  });
  it("escolher a Militar marca o cartao dela e muda o data-pele na hora", () => {
    escolherPele("xcom");
    expect(html.dataset.pele).toBe("xcom");
    expect(renderToStaticMarkup(h(EscolhaPele))).toMatch(/aria-checked="true" tabindex="0" class="[^"]*mc-opcao--pele-xcom"/);
    escolherPele("vidro");
  });
  it("o resumo de Aparencia mostra a pele e o tema", () => {
    expect(resumoAparencia("vidro", "sistema")).toBe("pele Holográfico · tema do sistema");
    expect(resumoAparencia("xcom", "escuro")).toBe("pele Militar · tema escuro");
    expect(tela).toContain("resumo={resumoAparencia(pele, tema)}");
  });
  it("a previa e so CSS (sem imagem), uma por pele, e a secao vem antes do Tema do habitat", () => {
    for (const p of PELES) expect(css).toContain(`.mc-opcao--pele-${p} .mc-pele-prev{`);
    const bloco = css.slice(css.indexOf(".mc-pele-prev"), css.indexOf("/* interruptor"));
    expect(bloco).not.toMatch(/url\(/);
    expect(tela.indexOf("<EscolhaPele />")).toBeGreaterThan(0);
    expect(tela.indexOf("<EscolhaPele />")).toBeLessThan(tela.indexOf("Tema do habitat"));
  });
});
