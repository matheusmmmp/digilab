// Save e rotas do app (TAREFA_FRONT_TS, Etapa 3): mesma chave e mesmo formato do digilab_sprites.html; um save
// de hoje abre igual (as vidas v13 do gabarito); o save de antes (v1-v12, e o sem versao = v1) e o que nao abre falham alto.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { Motor, VERSAO_PET } from "../motor/index.ts";
import { CHAVE, CHAVE_ABA, gravarSave, lerSave, petExemplo, textoSave, type Armazenamento } from "../src/save.ts";
import { enderecoDaRota, gravarAbaLembrada, lerAbaLembrada, rotaDoEndereco } from "../src/rotas.ts";

const armaz = (dados: Record<string, string> = {}): Armazenamento & { dados: Record<string, string> } =>
  ({ dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } });
const VIDAS_V13 = JSON.parse(readFileSync(new URL("./gabaritos/v13_vidas_ts.json", import.meta.url), "utf8")).vidas as
  { nome: string; semente: number; log: unknown[]; assinaturas: string[] }[];
const sha = (x: string): string => createHash("sha256").update(x).digest("hex");

describe("save", () => {
  test("a chave e a do HTML", () => {
    expect(CHAVE).toBe("digilab-web-v21-sprites");
    expect(CHAVE_ABA).toBe("digilab-web-v21-sprites-aba");
  });
  for (const v of VIDAS_V13.slice(0, 3)) {
    test(`abre um save de hoje igual: ${v.nome}`, () => {
      const a = armaz({ [CHAVE]: JSON.stringify({ semente: v.semente, log: v.log, versao: 13 }) });
      const l = lerSave(a);
      if (l.tipo !== "ok") throw new Error("nao abriu: " + JSON.stringify(l));
      expect(sha(l.motor.assinatura())).toBe(v.assinaturas[v.assinaturas.length - 1]);
      expect(l.motor.versao).toBe(13);
      /* gravar de volta da o mesmo texto (mesma ordem de campos) */
      gravarSave(a, l.motor);
      expect(JSON.parse(a.dados[CHAVE])).toEqual({ semente: v.semente, log: v.log, versao: 13 });
    });
  }
  test("o save de antes da luta em tempo real (v1-v12, e o sem versao = v1) nao abre: erro, nunca um pet de exemplo em silencio", () => {
    for (const s of [{ semente: 1, log: [] }, { semente: 1, log: [], versao: 6 }, { semente: 1, log: [], versao: 12 }]) {
      const bruto = JSON.stringify(s), l = lerSave(armaz({ [CHAVE]: bruto }));
      expect(l.tipo, bruto).toBe("erro");
    }
  });
  test("sem save: vazio; save null: vazio", () => {
    expect(lerSave(armaz()).tipo).toBe("vazio");
    expect(lerSave(armaz({ [CHAVE]: "null" })).tipo).toBe("vazio");
  });
  test("save que nao abre falha alto (nao vira pet de exemplo em silencio)", () => {
    for (const bruto of ["{", JSON.stringify({ semente: 1.5, log: [] }), JSON.stringify({ semente: 1, log: [[480, "x", 1]] }),
      JSON.stringify({ semente: 1, log: [[999, "t", 1]] }), JSON.stringify({ semente: 1, log: [], versao: 16 })]) {
      const l = lerSave(armaz({ [CHAVE]: bruto }));
      expect(l.tipo, bruto).toBe("erro");
      if (l.tipo === "erro") expect(l.bruto).toBe(bruto);
    }
  });
  test("texto do save: {semente, log, versao}", () => {
    /* os v12: o botao Alimentar poe a racao no comedouro (o evento "dc") */
    const m = new Motor(7); m.avancar(30); m.observar("alimentar");
    const [x, y] = m.mundo!.comedouro;
    expect(textoSave(m)).toBe(JSON.stringify({ semente: 7, log: [[480, "t", 30], [510, "dc", { tipo: "racao", x, y }]], versao: VERSAO_PET }));
  });
  test("pet de exemplo e o do HTML (semente 20260924, meio dia)", () => {
    const m = petExemplo();
    expect(m.semente).toBe(20260924);
    expect(m.e.tick).toBe(480 + 45 + 60 + 30 + 120 + 90 + 60 + 45 + 30);
    expect(m.log.filter(e => e[1] === "d" || e[1] === "dc")).toHaveLength(7);           /* os v12: o alimentar vira o "dc" */
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
