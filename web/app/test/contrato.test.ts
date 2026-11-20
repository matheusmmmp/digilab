/* A G-PAR-CONTRATO (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 4, etapa 2): o motor/contrato.ts e o motor/mundo.ts com a ConfigContrato
   reproduzem, numero a numero, o gabarito exportado do Python (experiments/exportar_gabarito_contrato.py): a config, as contas do
   contrato em casos sorteados (o setor, o cone, a oclusao, o bloqueio, o deslize, os bigodes, a grade, o A*, o controlador e o empurrao)
   e 7 vidas inteiras com as chaves, rejogadas decisao a decisao com o cerebro de teste dos dois lados (a percepcao com a orientacao, os
   candidatos, o alvo, o ocorrido com o registro do contrato, o estado e a percepcao depois), com o resumo e os proximos sorteios no fim.
   A falha mostra o primeiro campo que diverge (R-P2). E o G2 do jogo: com a chave explicita desligada, o mundo e o de hoje. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CMU, LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO, type ConfigMundo } from "../motor/constantes.ts";
import {
  CONFIG_CONTRATO, CONFIG_CONTRATO_LIGADO, bigodes, bloqueioEm, caminho, comComprimento, controlar, empurrar, grade, livreMaisPerto, mover,
  noCone, passoBola, relativo, setorDe, solido, tapado, validarContrato, visivel, type CategoriaSolido, type Circulo, type ConfigContrato,
  type Solido,
} from "../motor/contrato.ts";
import { Mundo, alvoPonto, type AcaoComAlvo, type AlvoMundo, type EstadoNoMundo } from "../motor/mundo.ts";

type Rec = Record<string, unknown>;
type SolidoJson = [number, number, number, number, CategoriaSolido, boolean, boolean];
interface OpDecisao {
  op: "decisao"; tick: number; fome_antes: number; percepcao: Rec; acao: string; estado: EstadoNoMundo; regra: string | null;
  com_gancho: boolean; candidatos: Rec[] | null; ocorrido: (Rec & { alvo: AlvoMundo | null }) | null; depois: EstadoNoMundo; percepcao_depois: Rec;
}
type Op = OpDecisao | { op: "deixar_comida"; tick: number; tipo: string; x: number; y: number } | { op: "deixar_bola"; tick: number; x: number; y: number };
interface Vida {
  nome: string; semente: number; efeito: Record<string, number>; layout: string; mult_queda: number; contrato: ConfigContrato; cerebro: string;
  traco: Op[]; resumo: Rec; proximos: Record<string, { random: number[]; randrange16: number[] }>; decisoes: number;
}
const G = JSON.parse(readFileSync(new URL("./gabaritos/contrato_python.json", import.meta.url), "utf8")) as {
  versao: number;
  config: { desligada: Rec; ligada: Rec };
  grade: Record<string, unknown[]>;
  vidas: Vida[];
};
const GM = JSON.parse(readFileSync(new URL("./gabaritos/mundo_python.json", import.meta.url), "utf8")) as { vidas: (Vida & { contrato?: never })[] };

const comoJson = (v: unknown): unknown => JSON.parse(JSON.stringify(v));
const sol = (s: SolidoJson[]): Solido[] => s.map(q => solido(q[0], q[1], q[2], q[3], q[4], q[5], q[6]));

/** o primeiro caminho em que os dois valores divergem (R-P2: a falha mostra o campo), ou null */
function primeiraDivergencia(a: unknown, b: unknown, cam = "$"): string | null {
  if (Object.is(a, b)) return null;
  if (typeof a !== typeof b || a === null || b === null || typeof a !== "object") return `${cam}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`;
  if (Array.isArray(a) !== Array.isArray(b)) return `${cam}: lista e objeto`;
  const ka = Object.keys(a as object), kb = Object.keys(b as object);
  for (const k of [...new Set([...ka, ...kb])].sort()) {
    const d = primeiraDivergencia((a as Rec)[k], (b as Rec)[k], `${cam}.${k}`);
    if (d) return d;
  }
  return null;
}

/** confere e, na falha, diz o primeiro campo que diverge */
function igual(obtido: unknown, esperado: unknown, onde: string): void {
  const d = primeiraDivergencia(comoJson(obtido), esperado);
  expect(d, `${onde}: ${d}`).toBeNull();
}

describe("config", () => {
  test("a ConfigContrato desligada e a ligada sao as do Python, campo a campo", () => {
    igual(CONFIG_CONTRATO, G.config.desligada, "desligada");
    igual(CONFIG_CONTRATO_LIGADO, G.config.ligada, "ligada");
  });
  test("as mesmas falhas altas", () => {
    for (const ruim of [{ sensores: 1 }, { cos_meio_cone: 0 }, { cos_meio_cone: 1025 }, { r_pet: 0 }, { ticks_bloqueado: 0 },
                        { lado_tronco: 0 }, { raio_bigode: -1 }, { cos_meio_cone: 512.5 }])
      expect(() => validarContrato({ ...CONFIG_CONTRATO, ...ruim } as ConfigContrato), JSON.stringify(ruim)).toThrow();
    expect(() => solido(0, 0, 0, 5, "parede", true, true)).toThrow();
    expect(() => solido(0, 0, 5, 5, "muro" as CategoriaSolido, true, true)).toThrow();
  });
});

describe("as contas do contrato, nos casos sorteados do Python", () => {
  const g = G.grade;
  test("o setor, o relativo, o comprimento e o cone", () => {
    for (const [dx, dy, r] of g.setor_de as number[][]) expect(setorDe(dx, dy), `${dx},${dy}`).toBe(r);
    for (const [s, o, r] of g.relativo as number[][]) expect(relativo(s, o)).toBe(r);
    for (const [dx, dy, c, r] of g.com_comprimento as [number, number, number, number[]][]) expect(comComprimento(dx, dy, c)).toEqual(r);
    for (const [dx, dy, o, cos, r] of g.no_cone as [number, number, number, number, boolean][]) expect(noCone(dx, dy, o, cos), `${dx},${dy},${o},${cos}`).toBe(r);
    expect(() => comComprimento(0, 0, 5)).toThrow();
  });
  test("a oclusao e a visao", () => {
    let tapados = 0;
    for (const [x0, y0, x1, y1, s, r] of g.tapado as [number, number, number, number, SolidoJson[], boolean][]) {
      expect(tapado(x0, y0, x1, y1, sol(s)), JSON.stringify([x0, y0, x1, y1, s])).toBe(r);
      if (r) tapados++;
    }
    expect(tapados).toBeGreaterThan(10);
    for (const [x0, y0, x1, y1, o, raio, cos, s, r] of g.visivel as [number, number, number, number, number, number, number, SolidoJson[], boolean][])
      expect(visivel(x0, y0, x1, y1, o, raio, cos, sol(s))).toBe(r);
  });
  test("o bloqueio, o movimento com o deslize e os bigodes", () => {
    for (const [x, y, r, s, c, b] of g.bloqueio_em as [number, number, number, SolidoJson[], number[][], unknown][])
      expect(bloqueioEm(x, y, r, sol(s), c as unknown as Circulo[])).toEqual(b);
    for (const [x, y, r, vx, vy, s, c, res] of g.mover as [number, number, number, number, number, SolidoJson[], number[][], unknown][])
      expect(mover(x, y, r, vx, vy, sol(s), c as unknown as Circulo[]), JSON.stringify([x, y, r, vx, vy])).toEqual(res);
    for (const [x, y, r, o, s, raio, res] of g.bigodes as [number, number, number, number, SolidoJson[], number, number[]][])
      expect(bigodes(x, y, r, o, sol(s), raio)).toEqual(res);
  });
  test("a grade, o A* (com e sem caminho) e a celula livre mais perto", () => {
    for (const [cx, cy, sub, r, s, res] of g.grade as [number, number, number, number, SolidoJson[], boolean[]][])
      expect([...grade(cx, cy, sub, r, sol(s))]).toEqual(res);
    let sem = 0;
    for (const [gg, cx, cy, de, para, res] of g.caminho as [boolean[], number, number, [number, number], [number, number], unknown][]) {
      expect(caminho(gg, cx, cy, de, para), JSON.stringify([cx, cy, de, para])).toEqual(res);
      if (res === null) sem++;
    }
    expect(sem).toBeGreaterThanOrEqual(10);
    for (const [gg, cx, c, res] of g.livre_mais_perto as [boolean[], number, [number, number], number[]][]) expect(livreMaisPerto(gg, cx, c)).toEqual(res);
  });
  test("o controlador: chega, para pela hora, bloqueia e encosta", () => {
    const casos = g.controlar as { args: number[]; solidos: SolidoJson[]; cx_n: number; cy_n: number; sub: number; ticks_bloqueado: number;
                                    orientacao: number; andar: Rec }[];
    const por = new Set<string>();
    let contatos = 0;
    for (const [i, c] of casos.entries()) {
      const [x0, y0, tx, ty, raio, ticks, vel, r] = c.args;
      const a = controlar(x0, y0, tx, ty, raio, ticks, vel, r, sol(c.solidos), c.cx_n, c.cy_n, c.sub, c.ticks_bloqueado, c.orientacao);
      igual(a, c.andar, `controlar, caso ${i}`);
      por.add(a.parou_por);
      if (a.contatos.length) contatos++;
    }
    expect([...por].sort()).toEqual(["bloqueado", "chegou", "hora"]);
    expect(contatos).toBeGreaterThanOrEqual(10);
  });
  test("o empurrao da bola (portado; o mundo nao o usa)", () => {
    for (const [px, py, bx, by, r] of g.empurrar as number[][]) expect(empurrar(px, py, bx, by)).toEqual(r as unknown as number[]);
    for (const [x, y, r, vx, vy, s, res] of g.passo_bola as [number, number, number, number, number, SolidoJson[], number[]][])
      expect(passoBola(x, y, r, vx, vy, sol(s)), JSON.stringify([x, y, vx, vy])).toEqual(res);
  });
});

/* os cerebros de teste do gabarito (o CerebroAleatorio do exportar_gabarito_mundo.py e o CerebroBorda do exportar_gabarito_contrato.py) */
function escolherAleatorio(acao: AcaoComAlvo, cands: AlvoMundo[], _p: unknown, u: number): AlvoMundo | null {
  const k = u % (cands.length + 2);
  if (k < cands.length) return cands[k];
  if (k === cands.length && acao === "explorar") return alvoPonto((u * 7) % 1024, (u * 13) % 480);
  return null;
}

function escolherBorda(acao: AcaoComAlvo, cands: AlvoMundo[], p: unknown, u: number): AlvoMundo | null {
  if (acao === "explorar") {
    const cont = cands.find(c => c.tipo === "continuar");
    if (cont) return cont;
    const k = u % 4;
    if (k === 0) return alvoPonto(0, (u * 13) % 480);
    if (k === 1) return alvoPonto(1023, (u * 13) % 480);
    return alvoPonto((u * 7) % 1024, k === 2 ? 0 : 479);
  }
  return escolherAleatorio(acao, cands, p, u);
}

function configDaVida(v: { layout: string; mult_queda: number }): ConfigMundo {
  return { ...CMU, layout: v.layout === "afastado" ? LAYOUT_MUNDO_AFASTADO : LAYOUT_MUNDO_PADRAO, mult_queda: v.mult_queda };
}

/** rejoga o traco do Python no mundo em TS e confere tudo, op a op */
function rejogar(v: Vida, contrato: ConfigContrato | undefined): void {
  const m = new Mundo({ semente: v.semente, cfg: configDaVida(v), efeitoFrutas: v.efeito, ...(contrato ? { contrato } : {}) });
  const gancho = v.cerebro === "borda" ? escolherBorda : escolherAleatorio;
  let decisoes = 0;
  for (const [i, op] of v.traco.entries()) {
    const onde = `${v.nome}, op ${i} (tick ${op.tick})`;
    if (op.op === "deixar_comida") { m.deixarComida(op.tick, op.tipo, op.x, op.y); continue; }
    if (op.op === "deixar_bola") { m.deixarBola(op.tick, op.x, op.y); continue; }
    decisoes++;
    igual(m.antesDaDecisao(op.tick, op.fome_antes), op.percepcao, `percepcao, ${onde}`);
    const escolher = op.com_gancho ? gancho : null;
    const { estado, ocorrido } = m.consequencia(op.tick, op.acao, op.estado, escolher, op.regra);
    igual(m.ultimosCandidatos, op.candidatos, `candidatos, ${onde}`);
    igual(ocorrido, op.ocorrido, `ocorrido, ${onde}`);
    igual(estado, op.depois, `estado depois, ${onde}`);
    igual(m.perceber(op.tick), op.percepcao_depois, `percepcao depois, ${onde}`);
  }
  expect(decisoes).toBe(v.decisoes);
  igual(m.resumo(), v.resumo, `${v.nome}, resumo`);
  const fluxos = { arvores: m.rngArvores, bola: m.rngBola, sujeira: m.rngSujeira, alvo: m.rngAlvo };
  for (const [nome, r] of Object.entries(fluxos))
    igual({ random: [r.random(), r.random(), r.random()], randrange16: [r.randrange(1 << 16), r.randrange(1 << 16), r.randrange(1 << 16)] },
      v.proximos[nome], `${v.nome}, fluxo ${nome}`);
}

describe("7 vidas com o contrato, gravadas no Python e rejogadas no mundo em TS", () => {
  test("o gabarito tem as chaves juntas e separadas, as paredes, os tres cerebros de teste e os dois layouts", () => {
    expect(G.versao).toBe(1);
    expect(G.vidas.length).toBe(7);
    const chaves = G.vidas.map(v => `${v.contrato.sensores}|${v.contrato.controlador}|${v.contrato.paredes}`);
    expect(new Set(chaves)).toEqual(new Set(["true|true|false", "true|true|true", "true|false|false", "false|true|false"]));
    expect(new Set(G.vidas.map(v => v.cerebro))).toEqual(new Set(["instinto_bola", "aleatorio", "lobos", "borda"]));
    expect(G.vidas.some(v => v.layout === "afastado")).toBe(true);
    const regs = G.vidas.flatMap(v => (v.resumo.contrato_decisoes ?? []) as { parou_por: string; obstaculos: number[]; trajetoria: unknown }[]);
    expect(new Set(regs.map(r => r.parou_por))).toEqual(new Set(["chegou", "hora"]));
    expect(regs.some(r => Math.min(...r.obstaculos) < 32)).toBe(true);            // os bigodes contra as paredes
    expect(regs.some(r => r.trajetoria === null) && regs.some(r => r.trajetoria !== null)).toBe(true);
    const comOrientacao = G.vidas.flatMap(v => v.traco).filter((o): o is OpDecisao => o.op === "decisao" && "orientacao" in o.percepcao);
    expect(new Set(comOrientacao.map(o => o.percepcao.orientacao)).size).toBeGreaterThan(8);
  });

  for (const v of G.vidas) test(`${v.nome}: decisao a decisao, o resumo e os proximos sorteios`, () => rejogar(v, v.contrato));
});

describe("o G2 do jogo: a chave desligada", () => {
  test("com a ConfigContrato explicita desligada, as vidas do gabarito do mundo saem iguais (e sem os campos do contrato)", () => {
    for (const v of GM.vidas) {
      const cerebro = v.nome.startsWith("aleatorio") ? "aleatorio" : "outro";
      rejogar({ ...v, cerebro } as Vida, CONFIG_CONTRATO);
      expect("orientacao" in (v.resumo as Rec)).toBe(false);
    }
  });
  test("o mundo sem a opcao do contrato nao monta solidos nem registra", () => {
    const m = new Mundo({ semente: 11 });
    expect(m.cct).toEqual(CONFIG_CONTRATO);
    m.antesDaDecisao(15, 0.5);
    const r = m.consequencia(15, "explorar", { fome: 0.5, energia: 0.8, humor: 0.5, sujeira: 0 });
    expect(r.ocorrido!.contrato).toBeUndefined();
    expect("orientacao" in m.perceber(15)).toBe(false);
    expect(m.contratoDecisoes).toEqual([]);
  });
});
