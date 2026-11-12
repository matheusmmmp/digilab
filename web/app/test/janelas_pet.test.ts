/* As janelas da tela do pet, etapa JN1 (docs/PLANO_UX_JANELAS.md): o cadastro, o "exibir" por janela e a migracao da chave unica de antes.
   So preferencia de tela: nada aqui toca o motor, o registro ou o save. */
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, test } from "vitest";
import { DA_CHAVE_ANTIGA, IDS_JANELA, JANELAS, esquecerJanelas, exibirJanela, janelasDoGravado, quantasAMostra } from "../src/janelasPet.ts";
import { CHAVE } from "../src/save.ts";

const fonte = (c: string): string => readFileSync(new URL("../" + c, import.meta.url), "utf8");

describe("janelas do pet: o que esta gravado vira o estado", () => {
  test("sem nada gravado, as seis janelas ficam à mostra (o jogo de hoje)", () => {
    const j = janelasDoGravado(null, null);
    expect(IDS_JANELA.every(id => j[id])).toBe(true);
    expect(quantasAMostra(j)).toBe(6);
  });
  test('a chave única de antes desligada esconde as quatro janelas dela e deixa o Agora e o Minimapa', () => {
    const j = janelasDoGravado(null, "0");
    for (const id of DA_CHAVE_ANTIGA) expect(j[id]).toBe(false);
    expect(j.agora).toBe(true);
    expect(j.minimapa).toBe(true);
    expect(DA_CHAVE_ANTIGA).toEqual(["estado", "evolucao", "acoes", "digibrain"]);
  });
  test("a chave única de antes ligada não esconde nada", () => {
    expect(quantasAMostra(janelasDoGravado(null, "1"))).toBe(6);
  });
  test("a chave nova vence a antiga, e uma janela que falta nela fica à mostra", () => {
    const j = janelasDoGravado(JSON.stringify({ v: 1, exibir: { evolucao: false } }), "0");
    expect(j.evolucao).toBe(false);
    expect(j.estado).toBe(true);
    expect(quantasAMostra(j)).toBe(5);
  });
  test("um texto ilegível, de outra versão ou de outro formato vale como nada gravado", () => {
    for (const t of ["{", "null", "[]", JSON.stringify({ v: 2, exibir: { estado: false } }), JSON.stringify({ v: 1, exibir: { estado: "nao" } })])
      expect(quantasAMostra(janelasDoGravado(t, null))).toBe(6);
    /* e, sem a chave nova legivel, a antiga ainda vale */
    expect(quantasAMostra(janelasDoGravado("{", "0"))).toBe(2);
  });
});

describe("janelas do pet: exibir grava no navegador", () => {
  const guardado = new Map<string, string>();
  beforeEach(() => {
    guardado.clear();
    (globalThis as { localStorage?: unknown }).localStorage = {
      getItem: (k: string) => guardado.get(k) ?? null, setItem: (k: string, v: string) => { guardado.set(k, v); }, removeItem: (k: string) => { guardado.delete(k); },
    };
    esquecerJanelas();
  });
  test("esconder uma janela grava a versão 1 com as seis, fora da chave do save", () => {
    exibirJanela("acoes", false);
    const o = JSON.parse(guardado.get(CHAVE + "-janelas")!);
    expect(o.v).toBe(1);
    expect(Object.keys(o.exibir).sort()).toEqual([...IDS_JANELA].sort());
    expect(o.exibir.acoes).toBe(false);
    expect(guardado.has(CHAVE)).toBe(false);
  });
  test("a primeira mudança depois da chave antiga desligada guarda as quatro escondidas, menos a que foi ligada", () => {
    guardado.set(CHAVE + "-detalhes-pet", "0");
    esquecerJanelas();
    exibirJanela("digibrain", true);
    const e = JSON.parse(guardado.get(CHAVE + "-janelas")!).exibir;
    expect(e).toMatchObject({ estado: false, evolucao: false, acoes: false, digibrain: true, agora: true, minimapa: true });
  });
});

describe("janelas do pet: o cadastro e quem o lê", () => {
  test("cada janela tem nome e resumo", () => {
    for (const id of IDS_JANELA) { expect(JANELAS[id].nome.length).toBeGreaterThan(0); expect(JANELAS[id].resumo.length).toBeGreaterThan(0); }
  });
  test("a tela do pet e os Ajustes leem o cadastro, e a chave única de antes saiu do código", () => {
    const tela = fonte("src/telas/pet/TelaPet.tsx"), cfg = fonte("src/telas/config/TelaConfig.tsx"), hud = fonte("src/hudPet.ts");
    expect(tela).toContain('import { useJanelas } from "../../janelasPet.ts";');
    expect(cfg).toContain("{IDS_JANELA.map(id => (");
    for (const t of [tela, cfg, hud]) { expect(t).not.toContain("useDetalhesPet"); expect(t).not.toContain("ligarDetalhesPet"); }
    /* o Agora e o Minimapa tambem obedecem */
    expect(tela).toContain("{largo && !atual && jn.minimapa && <Minimapa");
    expect(tela).toContain("{topo && largo && jn.agora && createPortal(<LinhaAgora");
  });
  test("o módulo não toca o motor nem o registro", () => {
    const t = fonte("src/janelasPet.ts");
    expect(t).not.toMatch(/from "\.\.\/motor|mudarMotor|agir\(/);
  });
});
