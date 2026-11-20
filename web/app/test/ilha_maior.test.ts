/* A ida para a ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG4; a IG-7 do Matheus: "deslocados junto com o lar"): o evento
   `mudar_ilha` para um destino de outro tamanho. O espelho do tests/test_ilha_maior.py.
     - os destinos (ILHAS_MAIORES) e as regras da ida no Mundo: tudo anda o deslocamento do ninho, o que cai em celula fechada vai para
       a terra, uma vez so, so a partir do mundo do produto de hoje;
     - o G-PAR do laco: o TS refaz o gabarito do Python (test/gabaritos/ilha_maior_python.json, experiments/exportar_gabarito_ilha_maior.py)
       decisao a decisao e bit a bit no Node, nos tres caminhos dos pets do jogo: o v21 direto, o v22 (que nasceu na agua, dormindo na
       ida) e o v21 que ja tinha passado para a agua. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { CMU_GRANDE, CMU_MVP, CMU_MVP_AGUA } from "../motor/constantes.ts";
import { CONFIG_CONTRATO_AGUA, bloqueioEm } from "../motor/contrato.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { estadoNascimentoPy } from "../motor/motor_corpo.ts";
import { Memoria } from "../motor/digibrain/mem.ts";
import { ILHAS_DE_TROCA, ILHAS_MAIORES, Mundo, noMapa, regiaoDe, solidosDaAgua } from "../motor/mundo.ts";
import { LacoGravado, cerebroDa, json, ler, type Rec, type Vida } from "./laco_gravado.ts";

const { texto, g: G } = ler("./gabaritos/ilha_maior_python.json");
const SHA = "13953907c6fab5b3144db69f69339fdaf91494402c56cfc7bf00d46387e5ade8";
type VidaIda = Vida & {
  comeco: { mundo: "mvp" | "mvp_agua"; contrato: boolean; trocas: [number, string][]; dormindo: boolean };
  ida: { exatos: number; tirados: number; comidas: number }; conferido: { cruzou_pela_ponte: number; posicoes_do_pet: number };
};
const VIDAS = G.vidas as VidaIda[];
const CFG = G.config as unknown as { mundo_mvp: Rec; mundo_agua: Rec; mundo_grande: Rec; contrato: Rec };
const SUB = CMU_GRANDE.sub, DX = (CMU_GRANDE.layout.ninho[0] - CMU_MVP.layout.ninho[0]) * SUB, DY = (CMU_GRANDE.layout.ninho[1] - CMU_MVP.layout.ninho[1]) * SUB;
const SOB_O_CARRO: [number, number] = [(31 - 16) * SUB + SUB / 2, (21 - 15) * SUB + SUB / 2];

describe("a ida para a ilha grande no Mundo", () => {
  test("o destino e a ilha grande, a partir do mundo do produto de hoje", () => {
    expect(Object.keys(ILHAS_DE_TROCA)).toEqual(["mvp_agua", "grande"]);
    expect(Object.keys(ILHAS_MAIORES)).toEqual(["grande"]);
    const M = ILHAS_MAIORES.grande;
    expect([M.celulas_x, M.celulas_y]).toEqual([128, 60]);
    expect(M.origens).toEqual([CMU_MVP.layout, CMU_MVP_AGUA.layout]);
    expect(ILHAS_DE_TROCA.grande.layout).toBe(CMU_GRANDE.layout);
    expect(ILHAS_DE_TROCA.grande.contrato).toBe(CONFIG_CONTRATO_AGUA);
    expect([DX, DY]).toEqual([16 * SUB, 15 * SUB]);
  });

  test("tudo anda o deslocamento do ninho; o que cai em celula fechada vai para a terra", () => {
    const m = new Mundo({ semente: 101, cfg: CMU_MVP });
    m.deixarComida(0, "racao", 300, 240);
    m.deixarComida(0, "racao", ...SOB_O_CARRO);
    const ids = [...m.comidas.keys()], bola = m.bolaEm(0), pet: [number, number] = [m.pet[0], m.pet[1]];
    const reg = m.mudarIlha(0, "grande") as unknown as Rec;
    expect(json(m.cm)).toEqual(json(CMU_GRANDE));
    expect(m.trocaIlha).toBeNull();
    expect(reg).toBe(m.trocaMaior);
    expect([reg.de, reg.para, reg.deslocamento]).toEqual(["mvp", "grande", [DX, DY]]);
    expect(m.comedouro).toEqual([CMU_GRANDE.layout.comedouro[0] * SUB + SUB / 2, CMU_GRANDE.layout.comedouro[1] * SUB + SUB / 2]);
    const c = [...m.comidas.values()];
    expect([c[0].x, c[0].y]).toEqual([300 + DX, 240 + DY]);
    expect([c[1].x, c[1].y]).not.toEqual([SOB_O_CARRO[0] + DX, SOB_O_CARRO[1] + DY]);
    for (const k of c) expect(m.seca(k.x, k.y)).toBe(true);
    expect((reg.comidas as { id: number }[]).map(k => k.id)).toEqual(ids);
    expect((reg.bola as { de: number[] }).de).toEqual(bola);
    expect(m.seca(...m.bolaEm(0))).toBe(true);
    expect(m.pet).toEqual([pet[0] + DX, pet[1] + DY]);               /* o ninho de la vai para o ninho de ca */
    expect(bloqueioEm(m.pet[0], m.pet[1], CONFIG_CONTRATO_AGUA.r_pet, solidosDaAgua(CMU_GRANDE))).toBeNull();
    expect(Object.keys(m.resumo())).toContain("troca_maior");
    expect(Object.keys(m.resumo())).not.toContain("troca_ilha");
    /* a vida segue no mapa grande: a racao alem do mapa de antes vale */
    m.deixarComida(10, "racao", 1800, 700);
  });

  test("a ida vale uma vez, so a partir do mundo do produto, e pode vir depois da agua", () => {
    const m = new Mundo({ semente: 101, cfg: CMU_MVP });
    m.mudarIlha(0, "grande");
    expect(() => m.mudarIlha(5, "grande")).toThrow(/uma vez/);
    expect(() => m.mudarIlha(5, "mvp_agua")).toThrow();
    expect(() => new Mundo({ semente: 101, cfg: CMU_GRANDE, contrato: CONFIG_CONTRATO_AGUA }).mudarIlha(0, "grande")).toThrow(/nao recebe/);
    expect(() => new Mundo({ semente: 101, cfg: CMU_MVP }).mudarIlha(0, "ilha_grande")).toThrow(/desconhecida/);
    /* o pet v21 que ja tinha passado para a agua, e o v22, que nasceu nela com o controlador */
    const a = new Mundo({ semente: 101, cfg: CMU_MVP });
    a.mudarIlha(0, "mvp_agua");
    a.mudarIlha(7, "grande");
    expect([a.trocaIlha !== null, a.trocaMaior !== null, a.cm.layout.nome]).toEqual([true, true, "grande"]);
    const b = new Mundo({ semente: 101, cfg: CMU_MVP_AGUA, contrato: CONFIG_CONTRATO_AGUA });
    b.mudarIlha(0, "grande");
    expect([b.trocaIlha, b.cm.celulas_x, b.contratoDecisoes.length, b.orientacao]).toEqual([null, 128, 0, 0]);
  });
});

describe("a memoria de lugar do DigiBrain modular anda com o mundo", () => {
  test("o Memoria.deslocar: o mesmo caso fixo do tests/test_ilha_maior.py (os mesmos episodios, os mesmos pontos de saida)", () => {
    const mundo = new Mundo({ semente: 101, cfg: CMU_GRANDE, contrato: CONFIG_CONTRATO_AGUA });
    const cd = { memoria_autobio: true, controle_mem: "rel", facetas_mem: false } as unknown as ConstructorParameters<typeof Memoria>[2];
    const mem = new Memoria({ sub: SUB }, null, cd);
    type E = Record<string, unknown>;
    (mem.episodios as unknown as E[]).push({ id: 0, ponto: [300, 240], lugar: [18, 15], regiao: 1, r: 5 });
    (mem.recente as unknown as E[]).push({ id: 1, ponto: [248, 104], lugar: [15, 6], regiao: 0, sigma: 7 });
    (mem.duradoura as unknown as E[]).push({ id: 2, ponto: [1000, 470], lugar: [62, 29], regiao: 3, sigma: -3 });
    const n = mem.deslocar(DX, DY, (x, y) => mundo.emTerra(...noMapa(x, y, CMU_GRANDE)), x => regiaoDe(x, CMU_GRANDE));
    expect(n).toBe(3);
    expect(mem.episodios).toEqual([{ id: 0, ponto: [556, 480], lugar: [34, 30], regiao: 1, r: 5 }]);          /* em terra livre: so o deslocamento */
    expect(mem.recente).toEqual([{ id: 1, ponto: [504, 328], lugar: [31, 20], regiao: 0, sigma: 7 }]);        /* em cima do carro: para a terra */
    expect(mem.duradoura).toEqual([{ id: 2, ponto: [1256, 710], lugar: [78, 44], regiao: 2, sigma: -3 }]);    /* da mata de la ao campo de ca */
    expect(mundo.seca(504, 344)).toBe(false);
    const sem = new Memoria({ sub: SUB }, null, { ...cd, memoria_autobio: false } as typeof cd);
    expect(sem.deslocar(DX, DY, (x, y) => [x, y], () => 0)).toBe(0);
  });
});

describe("G-PAR da ida para a ilha grande: o laco do TS = o Python, decisao a decisao", () => {
  test("o gabarito: os tres caminhos dos pets do jogo", () => {
    expect(createHash("sha256").update(texto).digest("hex")).toBe(SHA);
    expect(json(CMU_MVP)).toEqual(CFG.mundo_mvp);
    expect(json(CMU_MVP_AGUA)).toEqual(CFG.mundo_agua);
    expect(json(CMU_GRANDE)).toEqual(CFG.mundo_grande);
    expect(json(CONFIG_CONTRATO_AGUA)).toEqual(CFG.contrato);
    expect(VIDAS.map(v => [v.comeco.mundo, v.comeco.contrato, v.comeco.trocas.map(t => t[1]), v.comeco.dormindo])).toEqual([
      ["mvp", false, ["grande"], false], ["mvp_agua", true, ["grande"], true], ["mvp", false, ["mvp_agua", "grande"], false]]);
    for (const v of VIDAS) {
      expect(v.ida.exatos).toBeGreaterThan(0);
      expect(v.ida.tirados).toBeGreaterThan(0);
      expect(v.conferido.cruzou_pela_ponte).toBeGreaterThan(0);
    }
  });

  for (const vida of VIDAS) {
    test(`${vida.nome}: cada decisao, o log, o mundo e o corpo no fim`, () => {
      const c = cerebroDa(vida);
      const m = new LacoGravado(c.politica, vida.semente, CCO_CORPO_V11, estadoNascimentoPy(0),
                                { regra: c.regra, paridade: true, cfgMundo: vida.comeco.mundo === "mvp" ? CMU_MVP : CMU_MVP_AGUA, decidirNaComida: true,
                                  bolaNoGolpe: true, ...(vida.comeco.contrato ? { contrato: CONFIG_CONTRATO_AGUA } : {}) });
      for (const e of vida.log) m.aplicarEvento(e);
      expect(m.traco.length).toBe(vida.traco.length);
      for (let i = 0; i < vida.traco.length; i++) {
        const esperado = vida.traco[i] as Rec, obtido = m.traco[i];
        if (JSON.stringify(obtido) === JSON.stringify(esperado)) continue;
        for (const k of Object.keys(esperado)) expect(obtido[k], `traco[${i}] (${esperado.op} no tick ${esperado.tick}): ${k}`).toEqual(esperado[k]);
      }
      expect(m.log).toEqual(vida.log);
      expect(m.log.filter(e => e.tipo === "mudar_ilha").map(e => e.valor)).toEqual(vida.comeco.trocas.map(t => t[1]));
      expect(json(m.mundo.resumo())).toEqual(vida.resumo);
      expect({ q: { ...m.corpo.q }, receptores: m.corpo.receptores() }).toEqual(vida.corpo_fim);
      const e = m.estado;
      expect({ fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira, tick: e.tick }).toEqual(vida.estado_fim);
      expect(m.mundo.decisoes.length).toBe(vida.decisoes);
      for (const [fluxo, rg] of [["arvores", m.mundo.rngArvores], ["bola", m.mundo.rngBola], ["sujeira", m.mundo.rngSujeira], ["alvo", m.mundo.rngAlvo]] as const) {
        const prox = { random: [rg.random(), rg.random(), rg.random()], randrange16: [rg.randrange(1 << 16), rg.randrange(1 << 16), rg.randrange(1 << 16)] };
        expect(prox, `proximos de ${fluxo}`).toEqual(vida.proximos[fluxo]);
      }
      /* do lado do TS: o mundo do fim e a ilha grande, e nada ficou em celula fechada */
      const w = m.mundo, r = CONFIG_CONTRATO_AGUA.r_pet, solidos = solidosDaAgua(CMU_GRANDE);
      expect(json(w.cm)).toEqual(json(CMU_GRANDE));
      expect(w.trocaMaior!.deslocamento).toEqual([DX, DY]);
      for (const cm of w.comidas.values()) expect(w.seca(cm.x, cm.y)).toBe(true);
      let pontos = 0;
      for (const d of w.contratoDecisoes) for (const [x, y] of d.trajetoria ?? []) { pontos++; expect(bloqueioEm(x, y, r, solidos), `${x}, ${y}`).toBeNull(); }
      expect(pontos).toBeGreaterThan(50);
    });
  }
});
