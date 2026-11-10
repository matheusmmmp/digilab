// Save e rotas do app (TAREFA_FRONT_TS, Etapa 3): mesma chave e mesmo formato do digilab_sprites.html; um save
// de hoje (a v21, desde a LP4 da LUTA_POC) abre igual; o save de antes (v1-v19, e o sem versao = v1) e o que nao abre falham alto.
import { describe, expect, test } from "vitest";
import { Motor, VERSAO_PET } from "../motor/index.ts";
import { CHAVE, CHAVE_ABA, gravarSave, lerSave, petExemplo, textoSave, type Armazenamento } from "../src/save.ts";
import { enderecoDaRota, gravarAbaLembrada, lerAbaLembrada, rotaDoEndereco } from "../src/rotas.ts";

const armaz = (dados: Record<string, string> = {}): Armazenamento & { dados: Record<string, string> } =>
  ({ dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } });
/** uma vida v21 curta com uma luta na Arena (o gabarito das vidas v13 saiu com elas na LP4) */
function vidaV21(semente: number): Motor {
  const m = new Motor(semente);
  m.liberar(1);
  for (let p = 0; p < 40 && !m.morte; p++) {
    m.avancar(30);
    if (p % 3 === 0) m.observar("acariciar");
    if (m.e.fome < .6) m.observar("alimentar");
    if (m.estagioAtual === "crianca" && p % 9 === 0) { const rv = m.rivaisArenaPoc(); m.lutarPoc(rv[p % rv.length], 1000 + p, "campo"); }
  }
  return m;
}

describe("save", () => {
  test("a chave e a do HTML", () => {
    expect(CHAVE).toBe("digilab-web-v21-sprites");
    expect(CHAVE_ABA).toBe("digilab-web-v21-sprites-aba");
  });
  for (const semente of [1301, 1302, 1303]) {
    test(`abre um save de hoje igual: a vida v21 ${semente}`, () => {
      const m = vidaV21(semente), log = JSON.parse(JSON.stringify(m.log)) as unknown[];
      expect(log.some(ev => (ev as unknown[])[1] === "l")).toBe(true);
      const a = armaz({ [CHAVE]: JSON.stringify({ semente, log, versao: VERSAO_PET }) });
      const l = lerSave(a);
      if (l.tipo !== "ok") throw new Error("nao abriu: " + JSON.stringify(l));
      expect(l.motor.assinatura()).toBe(m.assinatura());
      expect(l.motor.versao).toBe(21);
      /* gravar de volta da o mesmo texto (mesma ordem de campos) */
      gravarSave(a, l.motor);
      expect(JSON.parse(a.dados[CHAVE])).toEqual({ semente, log, versao: 21 });
    });
  }
  test("o save de antes da luta da POC (v1-v19, e o sem versao = v1) nao abre: erro, nunca um pet de exemplo em silencio", () => {
    for (const s of [{ semente: 1, log: [] }, { semente: 1, log: [], versao: 6 }, { semente: 1, log: [], versao: 12 }, { semente: 1, log: [], versao: 13 },
      { semente: 1, log: [], versao: 19 }]) {
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
      JSON.stringify({ semente: 1, log: [[999, "t", 1]] }), JSON.stringify({ semente: 1, log: [], versao: 20 })]) {
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
