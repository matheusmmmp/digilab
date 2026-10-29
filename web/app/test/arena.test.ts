// Arena em tempo real (docs/TAREFA_V2_UP_ARENA.md): determinismo por semente, fluxos separados, entrada do jogador como evento,
// conferencia dos dados que falha alto e os recuos explicitos (P4). Dados SINTETICOS versionados (sem nada da Bandai); a paridade com o
// prototipo nos dados reais fica no fim, e so roda com Assets/arena_up presente (o script scripts/medir_arena.ts faz a rodada inteira).
import { expect, test } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import {
  IDS_CENA, LIMITE_MS, STATS_PADRAO, conferirDados, configCpu, criarLuta, lutarAteOFim, medirArenas, passo, sementeArena,
  sorteiosPorFluxo, sorteioUnico, tagDe, type ConfigLuta, type DadosArena, type Entrada, type Evento, type Sorteios,
} from "../arena/index.ts";
import { criarRng } from "../motor/rng.ts";

const SINT = JSON.parse(readFileSync(new URL("./arena_sintetico.json", import.meta.url), "utf8")) as DadosArena;
const EQ_A = ["Alfa", "Beta", "Gama"], EQ_B = ["Delta", "Alfa", "Beta"];

/** a luta inteira, com as entradas do jogador por passo; devolve os eventos e o estado final que importa */
function jogar(cfg: ConfigLuta, r: Sorteios, entradas: Map<number, Entrada[]> = new Map()) {
  const L = criarLuta(cfg, SINT, r), ev: Evento[] = [...L.eventos];
  L.eventos = [];
  for (let k = 0; !L.fim && L.relogio < LIMITE_MS; k++) ev.push(...passo(L, entradas.get(k) ?? []));
  return { ev, vencedor: L.vencedor, relogio: L.relogio, hp: (["a", "b"] as const).map(l => L.eq[l].map(u => [u.hp, Math.round(u.x * 1e6), Math.round(u.y * 1e6)])) };
}

test("dados sinteticos: a conferencia passa e lista os recuos (tag, sem golpe, sem status)", () => {
  const rec = conferirDados(SINT);
  expect(rec.tag).toEqual([{ n: "Delta", anim: "Skill_1", usa: "Attack_1" }]);
  expect(rec.semGolpe).toEqual(["Gama"]);
  expect(rec.semStatus).toEqual(["Gama"]);
});

test("dados com falta falham alto", () => {
  const sem = (f: (d: DadosArena) => void) => { const d = structuredClone(SINT); f(d); return () => conferirDados(d); };
  expect(sem(d => { delete (d.atributos as Record<string, string>).Beta; })).toThrow(/Beta: sem atributo/);
  expect(sem(d => { (d.golpes.Alfa as { t: unknown }).t = "x"; })).toThrow(/Alfa: instante do golpe/);
  expect(sem(d => { d.atlas.d.Alfa.t = []; })).toThrow(/Alfa: atlas sem quadros/);
  expect(sem(d => { d.golpes.Zeta = d.golpes.Alfa; })).toThrow(/Zeta: golpe sem atlas/);
  expect(sem(d => { for (const s of Object.values(d.status)) s.estagio = "Champion"; })).toThrow(/Rookie/);
  expect(() => criarLuta(configCpu("campo", ["Alfa", "Alfa", "Ninguem"], EQ_B), SINT, sorteiosPorFluxo(1))).toThrow(/Ninguem/);
});

test("tagDe: o recuo da Skill_1 e a primeira tag (Attack_1); a de mesmo nome quando existe", () => {
  expect(tagDe(SINT.atlas.d.Delta, "Skill_1")[0]).toBe("Attack_1");
  expect(tagDe(SINT.atlas.d.Delta, "Die")[0]).toBe("Die");
});

test("determinismo: a mesma semente da a mesma luta, em todas as arenas; outra semente, outra luta", () => {
  for (const id of IDS_CENA) {
    const cfg = configCpu(id, EQ_A, EQ_B);
    const a = jogar(cfg, sorteiosPorFluxo(101)), b = jogar(cfg, sorteiosPorFluxo(101));
    expect(a.ev.length, id).toBeGreaterThan(10);
    expect(b).toEqual(a);
    expect(a.ev.at(-1)?.tipo === "fim" || a.relogio >= LIMITE_MS, id).toBe(true);
  }
  const cfg = configCpu("caverna", EQ_A, EQ_B);
  expect(jogar(cfg, sorteiosPorFluxo(202)).ev).not.toEqual(jogar(cfg, sorteiosPorFluxo(303)).ev);
});

test("fluxos: cada uso tem a sua semente; mexer num fluxo nao muda os outros", () => {
  const sementes = ["ia", "combate", "cena", "visual"].map(f => sementeArena(101, f));
  expect(new Set(sementes).size).toBe(4);
  for (const s of sementes) expect(Number.isInteger(s) && s >= 0 && s < 2 ** 32).toBe(true);
  /* o fluxo visual so desloca o numero de dano: troca-lo nao muda nada da luta, so o dx dos eventos de dano */
  const cfg = configCpu("castelo", EQ_A, EQ_B), r1 = sorteiosPorFluxo(404), r2 = { ...sorteiosPorFluxo(404), visual: () => 0.5 };
  const a = jogar(cfg, r1), b = jogar(cfg, r2);
  const semDx = (ev: Evento[]) => ev.map(e => e.tipo === "dano" ? { ...e, dx: 0 } : e);
  expect(semDx(b.ev)).toEqual(semDx(a.ev));
  expect(b.ev.filter(e => e.tipo === "dano").every(e => e.tipo === "dano" && e.dx === 0)).toBe(true);
});

test("sequencia unica: o mesmo gerador para todos os usos, como o Math.random do prototipo", () => {
  const g1 = criarRng(1007), g2 = criarRng(1007), r = sorteioUnico(g1);
  expect([r.ia(), r.combate(), r.cena(), r.visual()]).toEqual([g2.random(), g2.random(), g2.random(), g2.random()]);
});

test("jogador: a entrada e evento por passo; os mesmos eventos refazem a mesma luta", () => {
  const cfg: ConfigLuta = { ...configCpu("floresta", EQ_A, EQ_B), jogador: true };
  const entradas = new Map<number, Entrada[]>([
    [0, [{ tipo: "mover", mx: 1, my: 0 }]], [40, [{ tipo: "mira", x: 300, y: 150 }, { tipo: "atacar" }]], [60, [{ tipo: "investida", ligada: true }]],
    [90, [{ tipo: "habilidade" }, { tipo: "mover", mx: 0, my: -1 }]], [300, [{ tipo: "trocar", slot: 1 }]], [400, [{ tipo: "sem_mira" }, { tipo: "mover", mx: 0, my: 0 }]],
  ]);
  for (let k = 500; k < 15000; k += 37) entradas.set(k, [{ tipo: "atacar" }, { tipo: "mover", mx: k % 3 === 0 ? 1 : -1, my: 0 }]);
  const a = jogar(cfg, sorteiosPorFluxo(505), entradas), b = jogar(cfg, sorteiosPorFluxo(505), entradas);
  expect(b).toEqual(a);
  expect(a.ev.some(e => e.tipo === "troca" && e.lado === "a" && !e.forcada)).toBe(true);
  expect(jogar(cfg, sorteiosPorFluxo(505)).ev).not.toEqual(a.ev);
  /* luta CPU x CPU nao aceita entrada */
  expect(() => passo(criarLuta(configCpu("campo", EQ_A, EQ_B), SINT, sorteiosPorFluxo(1)), [{ tipo: "atacar" }])).toThrow(/CPU x CPU/);
});

test("status: genericos sem registro no jogo; do jogo com o nivel e o ritmo", () => {
  const L = criarLuta({ ...configCpu("campo", EQ_A, EQ_B), a: { equipe: ["Alfa", "Beta", "Gama"], fonte: "jogo", nivel: 1, generico: { ...STATS_PADRAO } } }, SINT, sorteiosPorFluxo(1));
  const [alfa, , gama] = L.eq.a;
  expect(gama.st.origem).toBe("genérico");
  expect(gama.st.hp).toBe(STATS_PADRAO.hp);
  expect(alfa.st.origem).toBe("jogo");
  expect(alfa.st.hp).toBe(Math.round(5500 / 6));                    /* Alfa e a referencia Rookie: a base dele, vida / 6 */
});

const REAIS = new URL("../../../../Assets/arena_up/dados/", import.meta.url);
test.skipIf(!existsSync(REAIS))("paridade com o prototipo (dados reais): o campo na semente 42 e o do arena.html", () => {
  const ler = (n: string) => JSON.parse(readFileSync(new URL(n + ".json", REAIS), "utf8"));
  const d = { status: ler("status"), golpes: ler("golpes"), atributos: ler("atributos"), atlas: ler("atlas") } as DadosArena;
  conferirDados(d);
  const r = medirArenas(d, ["campo"], 10, 42, "unico").campo;
  expect([r.azul, r.dur]).toEqual(["11/20", 92]);                     /* scripts/arena_gabarito_prototipo.json */
  expect(lutarAteOFim(configCpu("ringue", ["Agumon", "Gabumon", "Patamon"], ["Devimon", "Gomamon", "Palmon"]), d, sorteiosPorFluxo(7)).fim).toBe(true);
});
