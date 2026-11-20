// O atlas de clipes de verdade (D:\Trab\digilab\Assets, fora do git, sprites do Digimon UP) no juntarClipes, depois do Comer dos 60
// (docs/TAREFA_V3_SPRITES_ACOES.md, secao 3.3, passo 4; missao M2). Pula com aviso quando o Assets nao existe (CI, outra maquina).
import { expect, test } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { juntarClipes, type AtlasClipes, type AtlasUp } from "../src/atlas.ts";

const ASSETS = new URL("../../../../Assets/", import.meta.url);
const CLIPES = new URL("digilab_atlas_up_clipes.json", ASSETS), BASE = new URL("digilab_atlas_up.json", ASSETS);
const tem = existsSync(CLIPES) && existsSync(BASE);
if (!tem) console.warn("atlas_acoes_real: sem o Assets, teste pulado");

test.skipIf(!tem)("o atlas real passa no juntarClipes: as formas com Comer e Comer_objeto casando, os NPCs e os bots sem", () => {
  const c = JSON.parse(readFileSync(CLIPES, "utf8")) as AtlasClipes & { prova_parcial?: boolean };
  const base = JSON.parse(readFileSync(BASE, "utf8")) as AtlasUp;
  expect(c.prova_parcial).toBeUndefined();
  const j = juntarClipes(base, c);
  const chaves = Object.keys(c.sprites), formas = chaves.filter(k => !k.startsWith("npc_") && !k.startsWith("bot_"));
  expect(formas.length).toBe(60);
  for (const k of formas) {
    const cl = j.sprites[k].clipes!;
    expect(cl.Comer?.loop, k).toBe(true);
    expect(cl.Comer_objeto?.ms, k).toEqual(cl.Comer!.ms);
  }
  for (const k of chaves.filter(k => !formas.includes(k))) expect(j.sprites[k].clipes?.Comer, k).toBeUndefined();
});
