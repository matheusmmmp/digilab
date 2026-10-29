// Arena em tempo real com o pet (docs/TAREFA_V2_UP_ARENA.md, secao 12; correcao do Matheus, 2026-10-29): a forma do pet vira o Digimon do
// atlas da arena, o rival do mesmo estagio sai da semente da luta, e a luta e 1 contra 1 pela IA. Sem pet valido, o motivo (nada de
// Digimon aleatorio). Dados SINTETICOS versionados; o mapeamento das 60 formas nos dados reais so roda com Assets/arena_up presente.
import { expect, test } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { configCpu, criarLuta, lutarAteOFim, rivaisDoEstagio, sortearRival, sorteiosPorFluxo, type DadosArena } from "../arena/index.ts";
import { digimonNaArena, petNaArena } from "../src/arenaTempoReal.ts";
import { DIGIMON_DA_FORMA, chaveSprite, type Forma } from "../motor/index.ts";

const SINT = JSON.parse(readFileSync(new URL("./arena_sintetico.json", import.meta.url), "utf8")) as DadosArena;
const KABUTERIMON: Forma = { esp: "ferrugem", est: "adolescente", linha: "colosso" } as Forma;

test("pet: a forma vira o Digimon do atlas da arena, com o estagio do status do jogo", () => {
  expect(chaveSprite(KABUTERIMON)).toBe("ferrugem_adolescente_colosso");
  expect(petNaArena(KABUTERIMON, SINT)).toEqual({ ok: true, nome: "Kabuterimon", tela: "Kabuterimon", estagio: "Champion" });
});

test("pet sem luta: ovo, Digimon fora do atlas ou sem status proprio dao o motivo, nunca um Digimon aleatorio", () => {
  expect(petNaArena(null, SINT)).toEqual({ ok: false, motivo: "o pet ainda é um Digi-Egg" });
  const agumon = { esp: "brasa", est: "crianca", ramo: "sereno" } as Forma;
  expect(petNaArena(agumon, SINT)).toEqual({ ok: false, motivo: "Agumon não está no atlas da arena" });
  const semStatus = structuredClone(SINT); delete semStatus.status.Kabuterimon;
  expect(petNaArena(KABUTERIMON, semStatus)).toEqual({ ok: false, motivo: "Kabuterimon não tem status próprio no jogo (status.json)" });
});

test("rival: do mesmo estagio, sem o proprio pet, sorteado pela semente (o mesmo para a mesma semente)", () => {
  expect(rivaisDoEstagio(SINT, "Champion", "Kabuterimon")).toEqual(["Delta"]);
  expect(rivaisDoEstagio(SINT, "Rookie", "Alfa")).toEqual(["Beta"]);
  const cand = ["A", "B", "C", "D", "E"];
  const r = [1, 2, 3, 4, 5, 6, 7, 8].map(s => sortearRival(cand, s));
  expect([1, 2, 3, 4, 5, 6, 7, 8].map(s => sortearRival(cand, s))).toEqual(r);
  expect(new Set(r).size).toBeGreaterThan(1);
  expect(() => sortearRival([], 1)).toThrow(/nenhum rival/);
});

test("1 contra 1 pela IA: a luta termina, e a mesma semente da a mesma luta", () => {
  const cfg = configCpu("coliseu", ["Kabuterimon"], ["Delta"]);
  const a = lutarAteOFim(cfg, SINT, sorteiosPorFluxo(303)), b = lutarAteOFim(cfg, SINT, sorteiosPorFluxo(303));
  expect(a.fim).toBe(true);
  expect(b).toEqual(a);
  expect(() => criarLuta(configCpu("campo", [], ["Delta"]), SINT, sorteiosPorFluxo(1))).toThrow(/de 1 a 3/);
  expect(() => criarLuta(configCpu("campo", ["Alfa", "Alfa", "Alfa", "Alfa"], ["Delta"]), SINT, sorteiosPorFluxo(1))).toThrow(/de 1 a 3/);
});

const REAIS = new URL("../../../../Assets/arena_up/dados/", import.meta.url);
test.skipIf(!existsSync(REAIS))("dados reais: as 60 formas do DigiLab, quais lutam (com o apelido Ankylomon -> Ankiromon) e quais nao", () => {
  const ler = (n: string) => JSON.parse(readFileSync(new URL(n + ".json", REAIS), "utf8"));
  const d = { status: ler("status"), golpes: ler("golpes"), atributos: ler("atributos"), atlas: ler("atlas") } as DadosArena;
  const nao: string[] = [];
  let lutam = 0;
  for (const [nome] of Object.values(DIGIMON_DA_FORMA)) {
    const p = digimonNaArena(nome, d);
    if (p.ok) { lutam++; expect(rivaisDoEstagio(d, p.estagio, p.nome).length, nome).toBeGreaterThan(5); } else nao.push(p.motivo);
  }
  expect(nao.sort()).toEqual(["Ankylomon não tem status próprio no jogo (status.json)", "DemiVeemon não tem status próprio no jogo (status.json)",
    "WarGrowlmon não tem status próprio no jogo (status.json)"]);
  expect(lutam).toBe(57);
  expect(petNaArena({ esp: "ferrugem", est: "crianca", ramo: "arisco" } as Forma, d)).toMatchObject({ ok: true, nome: "Veemon", estagio: "Rookie" });
});
