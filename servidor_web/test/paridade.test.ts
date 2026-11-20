/* Paridade com o Python: os casos de test/gabarito_fala.json saem de servidor/fala_llm.py e digilab/expressao.py
   (python tools/gerar_catalogo_fala_web.py). Mesmo motivo, mesmo template e mesmo pedido a LLM, byte a byte; o que o Python recusa, o
   servidor novo recusa. */
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { CATALOGO, FalaReprovada, PedidoInvalido, montarPedido, motivoDeDict, template, validarMoldura } from "../src/catalogo.ts";

interface CasoMotivo { motivo: unknown; estagio: string; humor: number | null; erro: boolean; template?: string; pedido?: string | null }
const G: { motivos: CasoMotivo[]; molduras: { parte: string; ok: boolean; limpa?: string }[] } =
  JSON.parse(readFileSync(new URL("./gabarito_fala.json", import.meta.url), "utf8"));

function responder(c: CasoMotivo): { template: string; pedido: string | null } {
  const m = motivoDeDict(c.motivo);
  if (!CATALOGO.estagios.includes(c.estagio)) throw new PedidoInvalido("estagio desconhecido");
  const tpl = template(m, c.estagio, c.humor);
  return { template: tpl, pedido: CATALOGO.estagios_llm.includes(c.estagio) ? montarPedido(m, c.estagio, c.humor) : null };
}

describe("paridade com o Python", () => {
  it("o gabarito tem casos dos dois lados (aceitos e recusados)", () => {
    expect(G.motivos.filter(c => c.erro).length).toBeGreaterThan(50);
    expect(G.motivos.filter(c => !c.erro).length).toBeGreaterThan(500);
  });

  it("cada motivo: o mesmo template e o mesmo pedido, ou a mesma recusa", () => {
    const divergentes: string[] = [];
    for (const c of G.motivos) {
      let obtido: { template: string; pedido: string | null } | "erro";
      try { obtido = responder(c); } catch (err) {
        if (!(err instanceof PedidoInvalido)) throw err;
        obtido = "erro";
      }
      const esperado = c.erro ? "erro" : { template: c.template, pedido: c.pedido };
      if (JSON.stringify(obtido) !== JSON.stringify(esperado))
        divergentes.push(`${JSON.stringify([c.motivo, c.estagio, c.humor])}: ${JSON.stringify(obtido)} != ${JSON.stringify(esperado)}`);
    }
    expect(divergentes.slice(0, 5)).toEqual([]);
  });

  it("cada moldura: a mesma decisao e o mesmo texto limpo", () => {
    for (const c of G.molduras) {
      if (c.ok) expect(validarMoldura(c.parte, "")[0], c.parte).toBe(c.limpa);
      else expect(() => validarMoldura(c.parte, ""), c.parte).toThrow(FalaReprovada);
    }
  });
});
