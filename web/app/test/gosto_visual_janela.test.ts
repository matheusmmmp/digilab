// A etapa 3 do código do PLANO_UX_GOSTO_VISUAL (a janela pequena nova), sem DOM (vitest em node). Cobre: a vista da janela (o selo só
// na tela do dono, o programa na TV do jogo, o balão em palavras fora do elemento que espelha o pet, a linha do gosto, o Carinho e o Parar,
// e nada das barras nem do porquê); a raiz da janela levando a pele da página; e, pela fonte, que o hospedeiro usa o Carinho do jogo, que
// o Esc fecha a janela sem parar a TV, que o balão segue o mínimo de tempo do sinal e que as classes do cartão do P0 saíram.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test } from "vitest";
import { estadoInicial, inatoDaSemente, type Reacao } from "../src/gostoVisual/gosto.ts";
import { JanelaDaTv, type VistaJanela } from "../src/gostoVisual/JanelaTv.tsx";
import { ALTURA_JANELA, LARGURA_JANELA, levarRaiz } from "../src/gostoVisual/janelaPequena.ts";
import { PALAVRA_REACAO } from "../src/gostoVisual/leituraGosto.ts";

const fonte = (rel: string): string => readFileSync(join(import.meta.dirname, "..", rel), "utf8");
const vista = (m: Partial<VistaJanela> = {}): VistaJanela => ({
  sprite: null, reacao: "adorando", inato: inatoDaSemente(101), estado: estadoInicial(), origem: "jogo", programa: "desenho colorido", temSom: true,
  nome: "Agumon", dito: "Está adorando.", erro: null, ...m,
});
const html = (m: Partial<VistaJanela> = {}): string => renderToStaticMarkup(h(JanelaDaTv, { v: vista(m), carinho: () => {}, parar: () => {} }));

describe("a janela pequena: só o pet, a reação, uma linha e dois botões (seção 7.3)", () => {
  test("na TV do jogo diz o programa, e não mostra o selo da captura", () => {
    const t = html();
    expect(t).toContain("Passando: a TV do jogo, desenho colorido");
    expect(t).not.toContain("janela-tv-selo");
    expect(html({ programa: null })).toContain("Passando: a TV do jogo<");
  });
  test("na tela do dono mostra o selo, e sem som a frase do gosto fica só com a imagem", () => {
    const t = html({ origem: "tela", programa: null, temSom: false });
    expect(t).toContain("Vendo a sua tela");
    expect(t).not.toContain("janela-tv-passando");
    const gosto = (s: string) => /data-testid="janela-tv-gosto">([^<]*)</.exec(s)![1]!;
    expect(gosto(t)).toMatch(/^Gosta mais de: .+\.$/);
    expect(gosto(t)).not.toMatch(/som|música|ritmo/i);
    expect(gosto(html({ origem: "tela", programa: null, temSom: true }))).toMatch(/^Gosta mais de: .+\.$/);
  });
  test("o balão diz a reação em palavras e fica fora do elemento que espelha o pet (o problema 4)", () => {
    for (const r of Object.keys(PALAVRA_REACAO) as Reacao[]) {
      const t = html({ reacao: r });
      expect(t).toContain(`data-testid="janela-tv-balao">${PALAVRA_REACAO[r]}</span><span class="jtv-pet jtv-pet--${r}">`);
    }
    /* antes da primeira leitura: sem balão e sem pose */
    const vazio = html({ reacao: null });
    expect(vazio).not.toContain("janela-tv-balao");
    expect(vazio).toContain('<span class="jtv-pet">');
    /* só o pet vira; nenhuma regra desvira o balão, porque ele não vira */
    const css = fonte("src/estilo/gosto_visual.css");
    expect(css).toContain(".jtv-pet--enjoou, .jtv-pet--nao_gosta{ transform:scaleX(-1) }");
    expect(css).not.toMatch(/jtv-balao[^{]*\{[^}]*scaleX/);
  });
  test("o balão é desenho; o leitor de tela ouve a região de status", () => {
    const t = html({ dito: "Não curtiu: a imagem é clara demais para ele." });
    expect(t).toMatch(/class="jtv-balao" aria-hidden="true"/);
    expect(t).toContain('role="status" data-testid="janela-tv-status">Não curtiu: a imagem é clara demais para ele.</p>');
  });
  test("dois botões, Carinho e Parar; sem barras, sem o porquê e sem contagem de carinhos", () => {
    const t = html();
    expect(t.match(/<button /g)).toHaveLength(2);
    expect(t).toMatch(/data-janela-tv-carinho=""[^>]*>.*Carinho<\/button>/);
    expect(t).toMatch(/Parar<\/button>/);
    expect(t).not.toMatch(/Por quê|De nascença|tvp-|gv-|carinhos|Assistiram/);
  });
  test("o pet tem o nome da forma como texto alternativo, com e sem o quadro", () => {
    expect(html({ sprite: "data:image/png;base64,AA" })).toContain('<img class="dl-pix jtv-sprite" src="data:image/png;base64,AA" alt="Agumon"/>');
    expect(html()).toContain('role="img" aria-label="Agumon"');
  });
  test("o erro aparece como alerta", () => {
    expect(html({ erro: "o sprite do pet não desenhou" })).toContain('role="alert" data-testid="janela-tv-erro">o sprite do pet não desenhou</p>');
    expect(html()).not.toContain("janela-tv-erro");
  });
});

describe("a janela flutuante", () => {
  test("360 × 620, e a raiz leva a língua, as classes e a pele da página", () => {
    expect([LARGURA_JANELA, ALTURA_JANELA]).toEqual([360, 620]);
    const para = { lang: "", className: "", dataset: {} as Record<string, string | undefined> };
    levarRaiz({ lang: "pt-BR", className: "dark", dataset: { pele: "vidro", tema: "escuro", vazio: undefined } }, para);
    expect(para).toEqual({ lang: "pt-BR", className: "dark", dataset: { pele: "vidro", tema: "escuro" } });
    expect(fonte("src/gostoVisual/janelaPequena.ts")).toContain("levarRaiz(document.documentElement, jan.document.documentElement);");
  });
  test("sempre escura e sem rolagem: só tokens da pele dos menus, e nenhuma cor nova", () => {
    const css = fonte("src/estilo/gosto_visual.css"), jtv = css.slice(css.indexOf("/* ---- A janela pequena"), css.indexOf("/* ---- O painel da TV"));
    expect(jtv).toContain("overflow:hidden");
    expect(jtv).not.toMatch(/#[0-9a-fA-F]{3,8}\b|rgba?\(|--dl-/);
    expect(jtv).toMatch(/\.jtv-bts button\{ min-height:48px/);
    expect(jtv).toContain("@media (prefers-reduced-motion:reduce)");
  });
  test("o hospedeiro: o Carinho é o do jogo, o Esc fecha a janela sem parar a TV, e o balão segue o mínimo do sinal", () => {
    const g = fonte("src/gostoVisual/GostoVisual.tsx");
    expect(g).toContain('carinho={() => { agir("acariciar"); }} parar={pararTv}');
    expect(g).toContain('if (e.key === "Escape") { e.preventDefault(); fecharJanelaDaTv(); }');
    expect(g).toContain("useRef(new FilaSinal()).current.passo(");
    expect(g).toContain('querySelector<HTMLElement>("[data-janela-tv-carinho]")?.focus()');
    /* parar a TV fecha a janela; fechar a janela não para a TV (o plano, 3.3) */
    expect(g).toContain("useEffect(() => { if (s.origem === null) fecharJanelaDaTv(); }, [s.origem]);");
    expect(fonte("src/gostoVisual/janelaPequena.ts")).not.toMatch(/pararTv|desligarTv/);
  });
  test("a vista e as classes do cartão do P0 saíram", () => {
    expect(fonte("src/gostoVisual/GostoVisual.tsx")).not.toMatch(/PetAssistindo\(|gv-/);
    expect(fonte("src/estilo/gosto_visual.css")).not.toMatch(/\.gv-/);
    expect(fonte("src/gostoVisual/PainelTv.tsx")).not.toMatch(/gv-/);
  });
});
