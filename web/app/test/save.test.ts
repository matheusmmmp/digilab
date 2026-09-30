// Save e rotas do app (TAREFA_FRONT_TS, Etapa 3): mesma chave e mesmo formato do digilab_sprites.html; um save
// de hoje abre igual (pets v1, v2 e v3, e o save antigo sem versao = v1); save que nao abre falha alto.
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { Motor, VERSAO_PET } from "../motor/index.ts";
import { CHAVE, CHAVE_ABA, gravarSave, lerSave, petExemplo, textoSave, type Armazenamento } from "../src/save.ts";
import { enderecoDaRota, gravarAbaLembrada, lerAbaLembrada, rotaDoEndereco } from "../src/rotas.ts";

const armaz = (dados: Record<string, string> = {}): Armazenamento & { dados: Record<string, string> } =>
  ({ dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } });
const vida = (arq: string) => JSON.parse(readFileSync(new URL(`./gabaritos/${arq}`, import.meta.url), "utf8")).vidas[0];

describe("save", () => {
  test("a chave e a do HTML", () => {
    expect(CHAVE).toBe("digilab-web-v21-sprites");
    expect(CHAVE_ABA).toBe("digilab-web-v21-sprites-aba");
  });
  for (const arq of ["vidas_v1_atencioso.json", "vidas_v2_exigente.json", "vidas_v3_relapso.json"]) {
    test(`abre um save de hoje igual: ${arq}`, () => {
      const v = vida(arq), a = armaz({ [CHAVE]: JSON.stringify({ semente: v.semente, log: v.log, versao: v.versao }) });
      const l = lerSave(a);
      if (l.tipo !== "ok") throw new Error("nao abriu: " + JSON.stringify(l));
      expect(l.motor.assinatura()).toBe(v.assinaturaFinal);
      expect(l.motor.versao).toBe(v.versao);
      /* gravar de volta da o mesmo texto (mesma ordem de campos) */
      gravarSave(a, l.motor);
      expect(JSON.parse(a.dados[CHAVE])).toEqual({ semente: v.semente, log: v.log, versao: v.versao });
    });
  }
  test("save sem versao e pet v1 (de antes do porte)", () => {
    const v = vida("vidas_v1_relapso.json"), l = lerSave(armaz({ [CHAVE]: JSON.stringify({ semente: v.semente, log: v.log }) }));
    if (l.tipo !== "ok") throw new Error("nao abriu");
    expect(l.motor.versao).toBe(1);
    expect(l.motor.assinatura()).toBe(v.assinaturaFinal);
  });
  test("sem save: vazio; save null: vazio", () => {
    expect(lerSave(armaz()).tipo).toBe("vazio");
    expect(lerSave(armaz({ [CHAVE]: "null" })).tipo).toBe("vazio");
  });
  test("save que nao abre falha alto (nao vira pet de exemplo em silencio)", () => {
    for (const bruto of ["{", JSON.stringify({ semente: 1.5, log: [] }), JSON.stringify({ semente: 1, log: [[480, "x", 1]] }),
      JSON.stringify({ semente: 1, log: [[999, "t", 1]] }), JSON.stringify({ semente: 1, log: [], versao: 10 })]) {
      const l = lerSave(armaz({ [CHAVE]: bruto }));
      expect(l.tipo, bruto).toBe("erro");
      if (l.tipo === "erro") expect(l.bruto).toBe(bruto);
    }
  });
  test("texto do save: {semente, log, versao}", () => {
    const m = new Motor(7); m.avancar(30); m.observar("alimentar");
    expect(textoSave(m)).toBe(JSON.stringify({ semente: 7, log: [[480, "t", 30], [510, "d", "alimentar"]], versao: VERSAO_PET }));
  });
  test("pet de exemplo e o do HTML (semente 20260924, meio dia)", () => {
    const m = petExemplo();
    expect(m.semente).toBe(20260924);
    expect(m.e.tick).toBe(480 + 45 + 60 + 30 + 120 + 90 + 60 + 45 + 30);
    expect(m.log.filter(e => e[1] === "d")).toHaveLength(7);
  });
});

describe("rotas", () => {
  test("endereco", () => {
    expect(rotaDoEndereco("#/crescer/treinar")).toEqual({ destino: "crescer", aba: "treinar" });
    expect(rotaDoEndereco("#/lutar")).toEqual({ destino: "lutar", aba: "arena" });
    expect(rotaDoEndereco("#/lutar/treinar")).toBeNull();
    expect(rotaDoEndereco("#/xyz")).toBeNull();
    expect(rotaDoEndereco("")).toBeNull();
    expect(enderecoDaRota({ destino: "diario", aba: "catalogo" })).toBe("#/diario/catalogo");
  });
  test("aba lembrada no formato do HTML (e o formato antigo, so a aba)", () => {
    const a = armaz();
    gravarAbaLembrada(a, { destino: "lutar", aba: "campanha" });
    expect(a.dados[CHAVE_ABA]).toBe("lutar/campanha");
    expect(lerAbaLembrada(a)).toEqual({ destino: "lutar", aba: "campanha" });
    expect(lerAbaLembrada(armaz({ [CHAVE_ABA]: "evolucao" }))).toEqual({ destino: "crescer", aba: "evolucao" });
    expect(lerAbaLembrada(armaz({ [CHAVE_ABA]: "lixo" }))).toBeNull();
  });
});
