/* O gabarito da luta da v23 antes da LP6 (docs/PLANO_LP6_SEGUNDO_GOLPE.md, LP6-1): com as chaves do golpe de apoio e da arena por estagio
   desligadas, a luta tem de sair byte a byte igual a de hoje. Este script grava, ANTES da mudanca e num commit proprio, o resumo de um
   conjunto de lutas do nucleo (motor/arena/): os 8 mapas, pares de formas de todos os estagios (de longe e de perto, os 7 com habilidade
   propria entre eles), duas sementes de teste e as duas tabelas da luta (a v21, sem o tiro e a esquiva, e a v23, com eles). Cada luta vira
   o sha256 do JSON dos eventos e do estado final dos dois lutadores (o JSON do Number e o menor texto que volta ao mesmo float, entao o
   hash confere bit a bit). O teste test/arena_lp6_gabarito.test.ts refaz as mesmas lutas e compara.
     node scripts/arena_gabarito_lp6.ts       # grava test/gabaritos/arena_lp6_v23.json */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { lutasDoGabaritoLp6, resumoLutaLp6 } from "../test/arena_lp6_lutas.ts";

const saida = fileURLToPath(new URL("../test/gabaritos/arena_lp6_v23.json", import.meta.url));
const lutas = lutasDoGabaritoLp6().map(l => ({ id: l.id, ...resumoLutaLp6(l.entrada) }));
writeFileSync(saida, JSON.stringify({ origem: "scripts/arena_gabarito_lp6.ts, antes da LP6-1 (a luta da v23 e da v21)", lutas }, null, 1) + "\n", "utf8");
console.log(`gravado ${saida}: ${lutas.length} lutas`);
