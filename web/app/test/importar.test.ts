/* importar pet: o arquivo .digilab e o proprio save; so entra se o replay abrir */
import { expect, test } from "vitest";
import { Motor } from "../motor/index.ts";
import { lerArquivo, nomeArquivo } from "../src/importar.ts";
import { textoSave } from "../src/save.ts";

test("arquivo valido: o replay abre e da o mesmo pet", () => {
  const m = new Motor(31, 4); m.avancar(200); m.observar("alimentar");
  const l = lerArquivo(textoSave(m), "x.digilab");
  expect(l.m.assinatura()).toBe(m.assinatura());
  expect(nomeArquivo(m)).toMatch(/^[a-z0-9-]+-D1\.digilab$/);
});

test("arquivo invalido falha alto com o motivo", () => {
  expect(() => lerArquivo("{", "a")).toThrow(/JSON/);
  expect(() => lerArquivo(JSON.stringify({ semente: 1.5, log: [] }), "a")).toThrow(/semente/);
  expect(() => lerArquivo(JSON.stringify({ semente: 1, log: [[999, "t", 1]], versao: 4 }), "a")).toThrow(/replay/);
});
