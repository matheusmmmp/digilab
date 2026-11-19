/* As recompensas e o mural no jogo (MMO7): o cliente (src/cais/premios.ts) contra um servidor falso com as rotas de
   servidor_web/src/premios/premios.ts, as tacas da temporada na tabela da vista (trancas.ts), o lugar delas perto do cais
   (ilha/premiosConta.ts) e o arquivo da taca (docs/objetos3d/cartoon/trofeu.py, public/enfeites/trofeu/). Sem DOM e sem rede. */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CMU, CMU_MVP } from "../motor/index.ts";
import { desligarCais, ligarCais } from "../src/cais/cais.ts";
import { abrirMural, buscarTacas, diaCurto, estadoMural, fecharMural, lerMural, lerPremios } from "../src/cais/premios.ts";
import { ilhaDe } from "../src/telas/pet/ilha/grade.ts";
import { PREMIOS_MODELOS } from "../src/telas/pet/ilha/modelos.ts";
import { TACAS, TACAS_NA_ILHA, pontosDasTacas, temporadasNaIlha } from "../src/telas/pet/ilha/premiosConta.ts";
import { TACAS_DA_CONTA, definirTacas } from "../src/trancas.ts";

const API = "http://api.teste";
const PREMIOS = {
  titulo_atual: [{ semana: "2026-11-16", numero: 47, estagio: "Rookie", texto: "Campeão Rookie da semana 47", congelou_em: "2026-11-23T04:00:00.000Z", no_perfil_ate: "2026-11-30T04:00:00.000Z" }],
  titulos: [{ semana: "2026-11-16", numero: 47, estagio: "Rookie", texto: "Campeão Rookie da semana 47", congelou_em: "2026-11-23T04:00:00.000Z", no_perfil_ate: "2026-11-30T04:00:00.000Z" }],
  selos: { total: 2, lista: [{ dia: "2026-11-18", posicao: 1, vitorias: 4 }, { dia: "2026-11-17", posicao: 3, vitorias: 2 }] },
  enfeites: [{ temporada: 2, de: "2026-11-30", ate: "2026-12-21", melhor: { semana: "2026-11-30", estagio: "Mega", posicao: 4 } },
    { temporada: 1, de: "2026-11-02", ate: "2026-11-23", melhor: { semana: "2026-11-16", estagio: "Rookie", posicao: 1 } }],
  recordes: { torre: { valor: 7, visto_em: "2026-11-18T15:00:00.000Z" }, fabrica: null, salao: { valor: 2, visto_em: "2026-11-18T15:00:00.000Z" } },
  respeito: { conferido: 140, titulos: 100, selos: 40, como: "..." },
  temporada_atual: 2,
};
const MURAL = {
  recordes: { torre: [{ posicao: 1, apelido: "Agumon#1001", valor: 12, visto_em: "x", voce: false }, { posicao: 2, apelido: "Gabumon#1002", valor: 7, visto_em: "x", voce: true }],
    fabrica: [], salao: [{ posicao: 1, apelido: "Gabumon#1002", valor: 2, visto_em: "x", voce: true }] },
  total: { torre: 2, fabrica: 0, salao: 1 },
  titulos: [{ semana: "2026-11-16", numero: 47, estagio: "Rookie", texto: "Campeão Rookie da semana 47", apelido: "Gabumon#1002", voce: true }],
};

function servidor() {
  const s = { sessao: true, fora: false, pedidos: [] as string[] };
  const json = (status: number, corpo: unknown): Response => new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });
  ligarCais({ api: API, agora: () => Date.parse("2026-11-25T15:00:00Z"), buscar: async (url: string) => {
    if (s.fora) throw new TypeError("fetch failed");
    const c = url.slice(API.length);
    s.pedidos.push(c);
    if (!s.sessao) return json(401, { erro: "sem sessão" });
    if (c === "/premios") return json(200, PREMIOS);
    if (c === "/mural") return json(200, MURAL);
    return json(404, { erro: "rota desconhecida" });
  } });
  return s;
}
afterEach(() => { fecharMural(); desligarCais(); definirTacas([]); vi.restoreAllMocks(); });

describe("as respostas do servidor", () => {
  it("os prêmios: o título no perfil, os selos, as taças, os recordes e o Respeito", () => {
    const p = lerPremios(PREMIOS);
    expect(p.tituloAtual[0]).toMatchObject({ texto: "Campeão Rookie da semana 47", noPerfilAte: Date.parse("2026-11-30T04:00:00.000Z") });
    expect(p.selos.map(x => x.dia)).toEqual(["2026-11-18", "2026-11-17"]);
    expect(p.enfeites.map(e => e.temporada)).toEqual([2, 1]);
    expect(p.recordes).toEqual({ torre: 7, fabrica: null, salao: 2 });
    expect(p.respeito).toBe(140);
  });
  it("o mural: as três instalações e os campeões", () => {
    const m = lerMural(MURAL);
    expect(m.recordes.torre[1]).toEqual({ posicao: 2, apelido: "Gabumon#1002", valor: 7, voce: true });
    expect(m.total).toEqual({ torre: 2, fabrica: 0, salao: 1 });
    expect(m.titulos[0]).toMatchObject({ estagio: "Rookie", voce: true });
  });
  it("a resposta que o jogo não entende falha alto", () => {
    expect(() => lerPremios({ ...PREMIOS, respeito: {} })).toThrow(/respeito/);
    expect(() => lerMural({ ...MURAL, recordes: { torre: [] } })).toThrow();
  });
  it("o dia curto", () => { expect(diaCurto("2026-11-08")).toBe("08/11"); });
});

describe("abrir o mural", () => {
  it("busca os prêmios e o mural, com a sessão, e põe as taças na ilha", async () => {
    const s = servidor(), v0 = TACAS_DA_CONTA.versao;
    await abrirMural();
    const e = estadoMural()!;
    expect(e.passo).toBe("pronto");
    expect(s.pedidos).toEqual(["/premios", "/mural"]);
    expect(TACAS_DA_CONTA.temporadas).toEqual([2, 1]);
    expect(TACAS_DA_CONTA.versao).toBe(v0 + 1);
    fecharMural();
    expect(estadoMural()).toBeNull();
  });
  it("sem a conta, o estado da conta; sem resposta, o da rede, e as taças ficam como estavam", async () => {
    const s = servidor();
    s.sessao = false;
    await abrirMural();
    expect(estadoMural()!.passo).toBe("sem_conta");
    s.sessao = true; s.fora = true;
    await abrirMural();
    expect(estadoMural()!.passo).toBe("sem_resposta");
    expect(TACAS_DA_CONTA.temporadas).toEqual([]);
  });
  it("buscarTacas só lê os prêmios e não abre o mural; com o cais desligado, nada", async () => {
    await buscarTacas();
    expect(TACAS_DA_CONTA.temporadas).toEqual([]);
    const s = servidor();
    await buscarTacas();
    expect(s.pedidos).toEqual(["/premios"]);
    expect(estadoMural()).toBeNull();
    expect(TACAS_DA_CONTA.temporadas).toEqual([2, 1]);
  });
  it("a lista das taças só muda a versão quando muda", () => {
    const v = TACAS_DA_CONTA.versao;
    expect(definirTacas([1, 2, 2])).toBe(true);
    expect(definirTacas([2, 1])).toBe(false);
    expect(TACAS_DA_CONTA.versao).toBe(v + 1);
  });
});

describe("as taças na ilha", () => {
  it("as temporadas mais novas, até o teto", () => {
    expect(temporadasNaIlha([1, 3, 2, 5, 4, 4])).toEqual([5, 4, 3, 2].slice(0, TACAS_NA_ILHA));
  });
  for (const cm of [CMU_MVP, CMU]) it(`perto do cais, em terra plana, longe do resto (layout ${cm.layout.nome})`, () => {
    const ilha = ilhaDe(cm), cais = ilha.lugares.find(l => l.nome === "cais");
    const pts = pontosDasTacas(ilha, TACAS_NA_ILHA);
    if (!cais) { expect(pts).toEqual([]); return; }
    expect(pts).toHaveLength(TACAS_NA_ILHA);
    expect(pontosDasTacas(ilha, TACAS_NA_ILHA)).toEqual(pts);   // a mesma ilha dá os mesmos pontos
    expect(pontosDasTacas(ilha, 0)).toEqual([]);
    for (const [x, z] of pts) {
      const d = Math.hypot(x - cais.x, z - cais.z), c = ilha.cel(Math.floor(x), Math.floor(z))!;
      expect(d).toBeGreaterThanOrEqual(TACAS.deCais.min); expect(d).toBeLessThanOrEqual(TACAS.deCais.max);
      expect(c.tipo).not.toBe("agua");
      for (const o of [...ilha.objetos, ...ilha.extras, ...ilha.enfeites]) expect(Math.hypot(o.x - x, o.z - z)).toBeGreaterThanOrEqual(TACAS.folga);
    }
    for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++)
      expect(Math.hypot(pts[i]![0] - pts[j]![0], pts[i]![1] - pts[j]![1])).toBeGreaterThanOrEqual(TACAS.entreTacas);
  });
});

describe("o arquivo da taça", () => {
  const APP = join(__dirname, ".."), f = join(APP, "public", "enfeites", PREMIOS_MODELOS.trofeu.arquivos[0]), dir = join(f, "..");
  it("feita à mão por script, sem IA, validada, sem arquivo sobrando e no teto dos marcos", () => {
    const g = JSON.parse(readFileSync(f, "utf8")) as { asset: { extras?: { gerado_por_ia?: boolean; gerador?: string } }; buffers: { uri: string }[];
      images?: { uri: string }[]; meshes: { primitives: { indices?: number }[] }[]; accessors: { count: number }[] };
    expect(g.asset.extras?.gerado_por_ia).toBe(false);
    expect(g.asset.extras?.gerador).toContain("docs/objetos3d/cartoon/trofeu.py");
    let tri = 0;
    for (const me of g.meshes) for (const p of me.primitives) tri += g.accessors[p.indices!]!.count / 3;
    expect(tri).toBeLessThanOrEqual(2414);
    const usados = [f, ...g.buffers.map(b => join(dir, b.uri)), ...(g.images ?? []).map(i => join(dir, i.uri))];
    for (const u of usados) expect(existsSync(u), u).toBe(true);
    expect(usados.reduce((s, u) => s + statSync(u).size, 0)).toBeLessThanOrEqual(300 * 1024);
    expect(readdirSync(dir).map(a => join(dir, a)).filter(a => !usados.includes(a) && !/License\.txt$/.test(a))).toEqual([]);
    expect(readFileSync(join(dir, "License.txt"), "utf8")).toMatch(/feito a mao por script/);
    const v = JSON.parse(readFileSync(join(APP, "..", "..", "docs", "enfeites", "trofeu", "validacao.json"), "utf8")) as { issues: { numErrors: number; numWarnings: number } };
    expect(v.issues.numErrors).toBe(0); expect(v.issues.numWarnings).toBe(0);
  });
});
