// O gabarito das vidas v13 (COMBATE-TR, etapa R2b): gravado num commit proprio, antes de tirar do motor os ramos das versoes v1-v12 (D-9).
// Cada vida de test/gabaritos/v13_vidas_ts.json (scripts/gerar_gabarito_vidas_v13.ts) se refaz pelo registro, e o sha256 da assinatura do
// Motor confere a cada evento, bit a bit. Se a remocao mudar uma vida de hoje, este teste para tudo.
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { Motor, type EventoRegistro } from "../motor/index.ts";

const GAB = JSON.parse(readFileSync(new URL("./gabaritos/v13_vidas_ts.json", import.meta.url), "utf8")) as {
  versao_pet: number; vidas: { nome: string; semente: number; log: EventoRegistro[]; assinaturas: string[] }[];
};
const sha = (x: string): string => createHash("sha256").update(x).digest("hex");

describe("as vidas v13 de hoje se refazem iguais", () => {
  test("o gabarito e das vidas v13 e cobre os eventos do pet v13", () => {
    expect(GAB.versao_pet).toBe(13);
    const tipos = new Set(GAB.vidas.flatMap(v => v.log.map(ev => ev[1])));
    for (const t of ["c", "o", "t", "d", "u", "dc", "l", "tr", "i", "g", "k"]) expect(tipos.has(t as EventoRegistro[1]), t).toBe(true);
  });
  for (const v of GAB.vidas) test(`${v.nome}: a assinatura a cada evento`, () => {
    const m = new Motor(v.semente);
    v.log.forEach((ev, i) => {
      m.aplicarEvento(ev);
      expect(sha(m.assinatura()), `${v.nome}, evento ${i}: ${JSON.stringify(ev)}`).toBe(v.assinaturas[i]);
    });
  });
});
