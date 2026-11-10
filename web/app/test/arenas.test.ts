/* Arenas com lideres (docs/DESIGN_MEDALHAS_ARENAS.md, secao 3; medalhas parte 2; so no jogo): a tabela das medalhas e das arenas e a arena
   da luta (o lider tem a dele, o desafiante nao). Desde a LP4 da LUTA_POC as regras das arenas do combate por turnos (Torre: contra-golpe;
   Floresta: muda de padrao no turno 10; Lago: sem travas nem vetos) sairam com ele; da regra fica so a serie da Cidadela, que a luta da POC
   joga (LP2, decisao 5; test/luta_poc_pet.test.ts confere a serie e o mapa de cada lugar). */
import { describe, expect, test } from "vitest";
import { ARENAS, ARENA_POR_ID, CAMPANHA_V5, CAMPANHA_V6, LUGARES_V6, MEDALHAS, NPC, arenaDaLuta, arenaDoLider } from "../motor/index.ts";
import { Motor } from "../motor/motor.ts";

const MYOTISMON = "npc_v5_myotismon", YOUKOMON = "npc_v6_youkomon", MARINBULLMON = "npc_v6_marinbullmon", GUARDROMON = "npc_tier2_carcereiro";

describe("a tabela das medalhas e das arenas (pet v21)", () => {
  test("seis arenas na ordem do nivel; a 3a medalha vem do lider da Floresta e a 5a do lider do Lago", () => {
    expect(LUGARES_V6.map(L => L.nome)).toEqual(["Campina", "Torre de pedra", "Floresta", "Cidadela", "Lago", "Montanha Espiral"]);
    expect(LUGARES_V6.map(L => L.sugerido)).toEqual(["Rookie", "Champion", "Champion", "Ultimate", "Ultimate", "Mega"]);
    expect(MEDALHAS.map(md => [md.id, NPC[md.lider]!.nome, LUGARES_V6[md.lugar].nome])).toEqual([
      ["campina", "Gazimon", "Campina"], ["torre", "Guardromon", "Torre de pedra"], ["floresta", "Youkomon", "Floresta"],
      ["cidadela", "Myotismon", "Cidadela"], ["lago", "MarinBullmon", "Lago"], ["espiral", "Piedmon", "Montanha Espiral"]]);
    for (const md of MEDALHAS) {
      expect(md).not.toHaveProperty("provisoria");
      expect(LUGARES_V6[md.lugar].rivais).toContain(md.lider);
      const ar = ARENA_POR_ID[md.id];
      expect([ar.lider, ar.lugar]).toEqual([md.lider, md.lugar]);
    }
    expect(ARENAS.map(a => a.regra)).toEqual(["nenhuma", "paciencia", "leitura", "resistencia", "vinculo", "chefe"]);
  });
  test("os NPCs de antes continuam como desafiantes, com as mesmas chaves (o replay dos v6 ja salvos acha todos)", () => {
    const v6 = CAMPANHA_V6.map(c => c.k);
    for (const c of CAMPANHA_V5) expect(v6).toContain(c.k);
    expect(LUGARES_V6[1].rivais.map(k => NPC[k]!.nome)).toEqual(["Tortomon", "Guardromon", "Devidramon"]);
    expect(LUGARES_V6[5].rivais.map(k => NPC[k]!.nome)).toEqual(["Puppetmon", "Machinedramon", "Piedmon"]);
    const m = new Motor(1);
    expect(Object.keys(m.campanha)).toEqual(v6);
    expect(m.lugares).toBe(LUGARES_V6);
    expect(m.lugarDe(MYOTISMON)).toBe(3);
  });
  test("os lideres novos estao no atlas do jogo (sprites do Digimon UP) e nao sao formas de pet", () => {
    /* a chave do NPC e a do atlas (catalogo_sprites_up.json, fora do repo): aqui so o que o motor garante */
    expect(NPC[YOUKOMON]).toMatchObject({ nome: "Youkomon", est: "adolescente", estilo: "arena:floresta" });
    expect(NPC[MARINBULLMON]).toMatchObject({ nome: "MarinBullmon", est: "adulto" });
  });
});

describe("a arena da luta", () => {
  test("o lider tem a arena dele; os desafiantes lutam sem arena; so a Cidadela tem a serie (3 lutas)", () => {
    for (const a of ARENAS) { expect(arenaDaLuta(a.lider, 21)).toBe(a); expect(arenaDoLider(a.lider)).toBe(a); }
    expect(arenaDaLuta("npc_tier2_sentinela", 21)).toBeNull();
    const m = new Motor(3);
    expect(m.arenaDe(GUARDROMON)!.id).toBe("torre");
    expect(ARENAS.filter(a => (a.lutas ?? 1) > 1).map(a => [a.id, a.lutas])).toEqual([["cidadela", 3]]);
    for (const a of ARENAS) expect(Object.keys(a).sort()).not.toContain("fator");
  });
});
