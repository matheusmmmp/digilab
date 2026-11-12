/* O gabarito da luta antes da N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4; D-N-5, "As 4 (Recommended)", Matheus,
   2026-11-12): com as chaves forcaAtr, tiroDoMorto, puloMax e bordaRingue desligadas, a luta das 3 tabelas que as versoes vivas usam (a
   v21 a v36) tem de sair byte a byte igual. Este script grava, ANTES das chaves e num commit proprio, o resumo das lutas de
   test/luta_nucleo_n3_lutas.ts e a tabela de cada versao viva. O teste test/luta_nucleo_n3_gabarito.test.ts refaz e compara.
     node scripts/arena_gabarito_n3.ts       # grava test/gabaritos/luta_nucleo_n3.json */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { VERSOES_PET } from "../motor/constantes.ts";
import { tabelaLuta } from "../motor/luta_poc.ts";
import { resumoLutaLp6 } from "../test/arena_lp6_lutas.ts";
import { lutasDoGabaritoN3 } from "../test/luta_nucleo_n3_lutas.ts";

const saida = fileURLToPath(new URL("../test/gabaritos/luta_nucleo_n3.json", import.meta.url));
const lutas = lutasDoGabaritoN3().map(l => ({ id: l.id, ...resumoLutaLp6(l.entrada) }));
const versoes = Object.fromEntries(VERSOES_PET.map(v => [String(v), tabelaLuta(v).versao]));
writeFileSync(saida, JSON.stringify({ origem: "scripts/arena_gabarito_n3.ts, antes das chaves da N3 (as tabelas v21, v23 e v29)", versoes, lutas }, null, 1) + "\n", "utf8");
console.log(`gravado ${saida}: ${lutas.length} lutas, versoes ${JSON.stringify(versoes)}`);
