// O painel da TV do gosto visual (docs/PLANO_UX_GOSTO_VISUAL.md, etapa 1; src/gostoVisual/PainelTv.tsx, leituraGosto.ts, sessaoTv.ts).
// Sem DOM (vitest em node). Cobre: as três origens separadas por linha (UX-GV-5), a lista curta, a frase para o leitor de tela, o motivo
// da reação (PR-3), a sessão (ligar, sentir, o carinho do jogo lido, parar) e o que o painel mostra desligado e ligado (UX-GV-4, 6 e 7).
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { TV } from "../src/gostoVisual/estadoTv.ts";
import { COMPONENTES, estadoInicial, inatoDaSemente, passo, type EstadoGosto, type Sentido } from "../src/gostoVisual/gosto.ts";
import {
  IMAGEM, LINHAS_CURTAS, descricaoDaLinha, fraseDaReacao, linhasDoGosto, linhasMarcadas, motivoDaReacao, nascencaDifere, picos,
} from "../src/gostoVisual/leituraGosto.ts";
import { FRASE_PRIVACIDADE, PainelTv, passandoEmPalavras } from "../src/gostoVisual/PainelTv.tsx";
import { ligarTvJogo, pararTv, sessaoTv, usarPet } from "../src/gostoVisual/sessaoTv.ts";
import { registrarAcaoDono } from "../src/telas/pet/reacao.ts";

const SEMENTE = 101;
const todo = (x: number): Sentido => ({ visao: { cor: x, brilho: x, movimento: x, complexidade: x }, som: { volume: x, variacao: x, timbre: x } });

describe("a leitura do gosto", () => {
  test("uma linha por componente, com a nascença, o de tanto ver e o do carinho separados, e o hoje como a soma limitada", () => {
    const ina = inatoDaSemente(SEMENTE), e: EstadoGosto = estadoInicial();
    e.exposicao.cor = 0.2; e.carinho.cor = 0.1; e.carinho.volume = -2;
    const ls = linhasDoGosto(ina, e);
    expect(ls.map(l => l.k)).toEqual([...COMPONENTES]);
    const cor = ls[0]!, vol = ls.find(l => l.k === "volume")!;
    expect(cor.nascenca).toBe(ina.otimo.cor); expect(cor.deVer).toBe(0.2); expect(cor.doCarinho).toBe(0.1);
    expect(cor.hoje).toBeCloseTo(Math.min(1, ina.otimo.cor + 0.3), 12);
    expect(vol.hoje).toBe(0);
    expect(cor.baixo).toBe("cores suaves"); expect(cor.alto).toBe("cores vivas");
  });
  test("a lista curta: os dois da frase e depois o que mais mudou, na ordem de sempre, até o limite", () => {
    const ina = inatoDaSemente(SEMENTE), e = estadoInicial();
    const semMudar = linhasMarcadas(linhasDoGosto(ina, e));
    expect(semMudar.length).toBe(2);
    const longe = [...COMPONENTES].sort((a, b) => Math.abs(ina.otimo[b] - 0.5) - Math.abs(ina.otimo[a] - 0.5) || COMPONENTES.indexOf(a) - COMPONENTES.indexOf(b));
    expect(semMudar.map(l => l.k).sort()).toEqual(longe.slice(0, 2).sort());
    const fora = COMPONENTES.filter(k => !longe.slice(0, 2).includes(k));
    e.exposicao[fora[0]!] = 0.01; e.carinho[fora[1]!] = 0.2; e.exposicao[fora[2]!] = 0.1;
    const com = linhasMarcadas(linhasDoGosto(ina, e));
    expect(com.length).toBe(LINHAS_CURTAS);
    expect(com.map(l => l.k)).toContain(fora[1]);
    expect(com.map(l => COMPONENTES.indexOf(l.k))).toEqual([...com.map(l => COMPONENTES.indexOf(l.k))].sort((a, b) => a - b));
  });
  test("a frase do leitor de tela diz a nascença, o hoje e de onde veio a mudança, sem número", () => {
    const ina = inatoDaSemente(SEMENTE), e = estadoInicial();
    const igual = descricaoDaLinha(linhasDoGosto(ina, e)[0]!);
    expect(igual).toMatch(/^cor: de nascença, /); expect(igual).toContain("hoje, quase igual");
    e.exposicao.cor = 0.2; e.carinho.cor = 0.1;
    const mudou = descricaoDaLinha(linhasDoGosto(ina, e)[0]!);
    expect(mudou).toContain("mudou de tanto ver e com o carinho");
    expect(mudou).not.toMatch(/\d/);
  });
  test("a segunda linha (de nascença) só existe quando o gosto em palavras mudou", () => {
    const ina = inatoDaSemente(SEMENTE), e = estadoInicial();
    expect(nascencaDifere(ina, e)).toBe(false);
    for (const k of COMPONENTES) e.carinho[k] = ina.otimo[k] < 0.5 ? 0.3 : -0.3;
    for (const k of COMPONENTES) e.exposicao[k] = ina.otimo[k] < 0.5 ? 0.25 : -0.25;
    expect(nascencaDifere(ina, e)).toBe(true);
  });
  test("o motivo da reação: o componente que mais pesou, o que mais atrapalhou e o lado do excesso; olhando e distraído não têm", () => {
    const ina = inatoDaSemente(SEMENTE), e = estadoInicial();
    /* um segundo com a cor no alvo exato e o resto no extremo oposto do alvo */
    const s: Sentido = { visao: { cor: ina.otimo.cor, brilho: ina.otimo.brilho < 0.5 ? 1 : 0, movimento: ina.otimo.movimento < 0.5 ? 1 : 0,
      complexidade: ina.otimo.complexidade < 0.5 ? 1 : 0 }, som: null };
    expect(picos(ina, e, s).map(p => p.k)).toEqual([...IMAGEM]);
    expect(motivoDaReacao(ina, e, s, "adorando")).toBe("tem as cores de que ele gosta");
    const pior = [...picos(ina, e, s)].sort((a, b) => a.pico - b.pico)[0]!;
    const nao = motivoDaReacao(ina, e, s, "nao_gosta")!;
    expect(nao).toMatch(/demais para ele$/);
    expect(nao.includes("demais")).toBe(true);
    expect(pior.k).not.toBe("cor");
    expect(motivoDaReacao(ina, e, s, "enjoou")).toBe("já viu muito disso");
    expect(motivoDaReacao(ina, e, s, "curioso")).toBe("é novo para ele");
    expect(motivoDaReacao(ina, e, s, "olhando")).toBeNull();
    expect(motivoDaReacao(ina, e, s, "distraido")).toBeNull();
    expect(fraseDaReacao(ina, e, s, "adorando")).toBe("Está adorando: tem as cores de que ele gosta.");
    expect(fraseDaReacao(ina, e, null, "olhando")).toBe("Está assistindo.");
  });
  test("o excesso tem lado: acima do alvo é demais para cima, abaixo é demais para baixo", () => {
    const ina = inatoDaSemente(SEMENTE), e = estadoInicial();
    const so = (cor: number): Sentido => ({ visao: { cor, brilho: ina.otimo.brilho, movimento: ina.otimo.movimento, complexidade: ina.otimo.complexidade }, som: null });
    expect(motivoDaReacao(ina, e, so(1), "nao_gosta")).toBe("as cores são vivas demais para ele");
    expect(motivoDaReacao(ina, e, so(0), "nao_gosta")).toBe("as cores são suaves demais para ele");
  });
});

describe("a sessão da TV e o painel", () => {
  const guardado = new Map<string, string>();
  beforeEach(() => {
    guardado.clear();
    vi.stubGlobal("localStorage", { getItem: (k: string) => guardado.get(k) ?? null, setItem: (k: string, v: string) => { guardado.set(k, v); } });
    vi.useFakeTimers();
  });
  afterEach(() => { pararTv(); vi.useRealTimers(); vi.unstubAllGlobals(); });

  test("desligado: Ligar a TV primeiro, a frase do gosto e o tempo; sem contagem de carinhos e sem botão de carinho", () => {
    usarPet(SEMENTE);
    const html = renderToStaticMarkup(h(PainelTv, { nome: "Agumon", movel: false }));
    expect(html).toContain("Ligar a TV");
    expect(html).toContain("Do que o Agumon gosta");
    expect(html).toContain("Gosta mais de: ");
    expect(html).toContain("Assistiram juntos: 0 s");
    expect(html).toContain("Por quê");
    expect(html).not.toContain("O que está passando");   /* só com a TV ligada */
    expect(html).not.toContain("Parar");
    expect(html.toLowerCase()).not.toContain("carinhos");
    expect(html).not.toMatch(/Fazer carinho/);
    /* em node não há captura: "Mostrar minha tela" e a frase da privacidade não aparecem (nenhum botão que falha) */
    expect(html).not.toContain("Mostrar minha tela");
    expect(html).not.toContain(FRASE_PRIVACIDADE);
  });
  test("ligar a TV do jogo: a ilha recebe o estado, o painel mostra o que passa e a reação, e Parar volta ao começo", () => {
    usarPet(SEMENTE);
    ligarTvJogo();
    expect(sessaoTv().origem).toBe("jogo"); expect(TV.ligada).toBe(true); expect(TV.origem).toBe("jogo");
    vi.advanceTimersByTime(3100);
    const s = sessaoTv();
    expect(s.estado.segundosJuntos).toBe(3); expect(s.leitura).not.toBeNull(); expect(s.programa).not.toBeNull();
    expect(passandoEmPalavras(s)).toBe(`a TV do jogo, ${s.programa}`);
    expect(TV.reacao).toBe(s.leitura!.reacao);
    const html = renderToStaticMarkup(h(PainelTv, { nome: "Agumon", movel: false }));
    expect(html).toContain(`Passando: a TV do jogo, ${s.programa}`);
    expect(html).toContain("Parar");
    expect(html).toContain("O que está passando");
    expect(html).toContain("Assistiram juntos: 3 s");
    expect(html).not.toContain("Ligar a TV");
    expect([...guardado.keys()]).toEqual([`digilab-gosto-visual-p0:${SEMENTE}`]);
    pararTv();
    expect(sessaoTv().origem).toBeNull(); expect(TV.ligada).toBe(false); expect(sessaoTv().leitura).toBeNull();
    expect(sessaoTv().estado.segundosJuntos).toBe(3);   /* o aprendido fica */
  });
  test("o carinho é o do jogo: um carinho durante a TV vira a origem 'do carinho' no segundo seguinte; o de antes de ligar não conta", () => {
    usarPet(SEMENTE);
    registrarAcaoDono("acariciar", 1000, 0);   /* antes de ligar */
    ligarTvJogo();
    vi.advanceTimersByTime(2100);
    expect(sessaoTv().estado.carinhos).toBe(0); expect(sessaoTv().carinhosVistos).toBe(0);
    registrarAcaoDono("acariciar", 5000, 0);
    vi.advanceTimersByTime(1000);
    expect(sessaoTv().estado.carinhos).toBe(1); expect(sessaoTv().carinhosVistos).toBe(1);
    expect(COMPONENTES.some(k => sessaoTv().estado.carinho[k] !== 0)).toBe(true);
    vi.advanceTimersByTime(3000);
    expect(sessaoTv().estado.carinhos).toBe(1);   /* um carinho conta uma vez */
  });
  test("a folha do celular, recolhida: a reação ou o botão de ligar, o gosto e o Mais; sem o porquê", () => {
    usarPet(SEMENTE);
    const html = renderToStaticMarkup(h(PainelTv, { nome: "Agumon", movel: true }));
    expect(html).toContain("tvp--recolhida");
    expect(html).toContain("Ligar a TV"); expect(html).toContain("Gosta mais de: "); expect(html).toContain("Mais");
    expect(html).not.toContain("Por quê"); expect(html).not.toContain("Janela pequena");
  });
  test("o mesmo passo do gosto: a sessão não muda a conta do protótipo", () => {
    usarPet(202);   /* outro pet: a sessão guarda o aprendido do pet anterior, e este começa do zero */
    ligarTvJogo();
    vi.advanceTimersByTime(1100);
    const s = sessaoTv(), esperado = passo(inatoDaSemente(202), estadoInicial(), s.sentido!, false);
    expect(s.estado).toEqual(esperado.estado); expect(s.leitura).toEqual(esperado.leitura);
  });
});

describe("as fronteiras da etapa 1", () => {
  const src = join(import.meta.dirname, "..", "src");
  test("a sessão só lê o carinho (reacao.ts, só vista): nada do motor, do log nem do save", () => {
    const t = readFileSync(join(src, "gostoVisual", "sessaoTv.ts"), "utf8");
    expect(t).toContain("ultimoCarinhoEm");
    expect(t).not.toMatch(/mudarMotor|aplicarEvento|trocarMotor|useJogo|from "\.\.\/save\.ts"|from "\.\.\/acoes\.ts"/);
  });
  test("a tela Pet só mostra a TV atrás da chave", () => {
    const t = readFileSync(join(src, "telas", "pet", "TelaPet.tsx"), "utf8");
    expect(t).toContain('id === "tv" ? vivo && gostoVisualLigado()');
    expect(t).toContain('{tem("tv") && <LinhaTv');
  });
});
