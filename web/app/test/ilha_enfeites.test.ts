/* Os enfeites da ilha (docs/TAREFA_V3_MUNDO_ENFEITES.md). E-G0: os objetos da grade de hoje nao mudam, item a item, contra o gabarito
   gravado antes dos enfeites (scripts/gabarito_ilha_objetos.ts, test/gabaritos/ilha_objetos.json). */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";

const GABARITO: Record<string, unknown[]> = JSON.parse(readFileSync(join(__dirname, "gabaritos", "ilha_objetos.json"), "utf8"));

describe("os enfeites da ilha", () => {
  for (const cm of [CMU_MVP, CMU]) test(`E-G0: os objetos de hoje nao mudam (layout ${cm.layout.nome})`, () => {
    expect(JSON.parse(JSON.stringify(ilhaDe(cm).objetos))).toEqual(GABARITO[cm.layout.nome]);
  });
});
