/* MMO1: confere um save pela conta dos pontos (src/ranking/pontos.ts), como o servidor fara (MMO3). Le o save exportado do jogo
   ({semente, log, versao}) e a lista das sementes entregues (um JSON: [{semente, indice, hora}], hora em ms UTC) e imprime as lutas
   ranqueadas e as linhas das tabelas da semana. Sem servidor e sem tela.
     node scripts/conferir_ranking.ts --save meu_pet.json --entregues sementes.json */
import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";
import type { EventoRegistro } from "../motor/index.ts";
import { linhasDaSemana, lutasRanqueadas, type SementeEntregue } from "../src/ranking/pontos.ts";

const { values } = parseArgs({ options: { save: { type: "string" }, entregues: { type: "string" } } });
if (!values.save || !values.entregues) throw new Error("uso: node scripts/conferir_ranking.ts --save F --entregues G");
const save = JSON.parse(readFileSync(values.save, "utf-8")) as { semente: unknown; log: unknown; versao: unknown };
if (!Number.isInteger(save.semente) || !Number.isInteger(save.versao) || !Array.isArray(save.log))
  throw new Error(`save inválido: precisa de {semente, log, versao} (${values.save})`);
const entregues = JSON.parse(readFileSync(values.entregues, "utf-8")) as SementeEntregue[];
if (!Array.isArray(entregues)) throw new Error(`a lista das sementes entregues não é uma lista (${values.entregues})`);

const lutas = lutasRanqueadas(save.semente as number, save.versao as number, save.log as EventoRegistro[], entregues);
console.log(JSON.stringify({ lutas, semanas: linhasDaSemana(lutas) }, null, 1));
