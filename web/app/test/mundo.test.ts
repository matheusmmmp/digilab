/* O mundo fisico em TS (docs/TAREFA_V2_MUNDO_FISICO.md, etapa 5; o G-PAR da secao 10): motor/mundo.ts reproduz, numero a numero, o
   gabarito exportado de digilab/mundo.py (experiments/exportar_gabarito_mundo.py): a config, os sorteios do random.Random do Python,
   derivar_semente, a conta inteira (deslocamento, distancia, cheiro e direcao), os eventos deixar_comida e deixar_bola do log e 4 vidas
   inteiras gravadas, rejogadas decisao a decisao (percepcao, candidatos, alvo, ocorrido, estado e percepcao depois), com o resumo do mundo
   e os proximos sorteios de cada fluxo no fim. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { C, CMU, LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO, type ConfigMundo } from "../motor/constantes.ts";
import {
  DIR16, Mundo, RandomPy, alvoPonto, cheiroEm, derivarSemente, deslocar, direcaoDoCheiro, distancia, divArred, eventoDeixarBola,
  eventoDeixarComida, lerDeixarBola, lerDeixarComida, passoAte, regiaoDe, type AcaoComAlvo, type AlvoMundo, type EstadoNoMundo,
  type EventoMundo, type FonteCheiro,
} from "../motor/mundo.ts";

type Rec = Record<string, unknown>;
interface OpDecisao {
  op: "decisao"; tick: number; fome_antes: number; percepcao: Rec; acao: string; estado: EstadoNoMundo; regra: string | null;
  com_gancho: boolean; candidatos: Rec[] | null; ocorrido: (Rec & { alvo: AlvoMundo | null; u: number }) | null; depois: EstadoNoMundo;
  percepcao_depois: Rec;
}
type Op = OpDecisao | { op: "deixar_comida"; tick: number; tipo: string; x: number; y: number } | { op: "deixar_bola"; tick: number; x: number; y: number };
interface Vida {
  nome: string; semente: number; efeito: Record<string, number>; layout: string; mult_queda: number; traco: Op[]; resumo: Rec;
  proximos: Record<string, { random: number[]; randrange16: number[] }>; decisoes: number;
}
const G = JSON.parse(readFileSync(new URL("./gabaritos/mundo_python.json", import.meta.url), "utf8")) as {
  versao: number;
  config: { mundo: Rec; afastado: Rec; estado: { ganho_alimentar: number; prob_sujeira_pos_refeicao: number; sujeira_maxima: number; intervalo_decisao_ticks: number } };
  grade: {
    sequencias: Record<string, Record<string, number[]>>;
    derivadas: { rotulos: (string | number)[]; valor: string }[];
    contas: { div_arred: number[][]; distancia: number[][]; passo_ate: [number, number, number, number, number, number[]][];
      deslocar: [number, number, number, number, number[]][]; regiao_de: number[][]; cheiro: [number, number, number[][], number][];
      direcao: [number, number, number[][], number[]][] };
    eventos: Rec[];
  };
  vidas: Vida[];
};

/** o JSON do Python: tuplas viram listas; o resto e igual */
const comoJson = (v: unknown): unknown => JSON.parse(JSON.stringify(v));

/** inteiro do JSON (rotulo grande vem como texto) */
const rotulo = (r: string | number): string | number | bigint => (typeof r === "string" && /^[0-9]+$/.test(r) ? BigInt(r) : r);

describe("config", () => {
  test("a ConfigMundo e os layouts sao os do Python, campo a campo", () => {
    expect(comoJson(CMU)).toEqual(G.config.mundo);
    expect(comoJson(LAYOUT_MUNDO_PADRAO)).toEqual(G.config.mundo.layout);
    expect(comoJson(LAYOUT_MUNDO_AFASTADO)).toEqual(G.config.afastado);
  });
  test("os numeros do estado que o mundo usa sao os da Config", () => {
    expect([C.ganhoAlim, C.probSujRef, C.sujMax, C.intervalo]).toEqual([G.config.estado.ganho_alimentar,
      G.config.estado.prob_sujeira_pos_refeicao, G.config.estado.sujeira_maxima, G.config.estado.intervalo_decisao_ticks]);
  });
  test("DIR16 e a tabela do Python e tem o comprimento 1024 arredondado", () => {
    expect(DIR16.length).toBe(16);
    for (const [i, [cx, cy]] of DIR16.entries()) {
      const a = (i * 22.5 * Math.PI) / 180;
      expect([cx, cy]).toEqual([Math.round(1024 * Math.cos(a)) + 0, -Math.round(1024 * Math.sin(a)) + 0]);
    }
  });
});

describe("os sorteios do Python", () => {
  test("random.Random(semente): random, randrange e randint, em sementes de 0 a 64 bits", () => {
    const seq = G.grade.sequencias;
    expect(Object.keys(seq).length).toBe(8);
    for (const [s, esperado] of Object.entries(seq)) {
      const r = new RandomPy(BigInt(s));
      const obtido = {
        random: Array.from({ length: 8 }, () => r.random()),
        randrange16: Array.from({ length: 8 }, () => r.randrange(16)),
        randint13: Array.from({ length: 8 }, () => r.randint(1, 3)),
        randrange33: Array.from({ length: 8 }, () => r.randrange(33)),
        randint_longe: Array.from({ length: 8 }, () => r.randint(320, 480)),
        randrange65536: Array.from({ length: 8 }, () => r.randrange(1 << 16)),
        randint310: Array.from({ length: 8 }, () => r.randint(3, 10)),
      };
      expect(obtido, `semente ${s}`).toEqual(esperado);
    }
  });
  test("a semente negativa e a do valor absoluto, como no CPython", () => {
    expect(new RandomPy(-101).random()).toBe(new RandomPy(101).random());
  });
  test("derivar_semente: sha256 de 'rotulo|rotulo' e os 8 primeiros bytes", () => {
    for (const d of G.grade.derivadas) expect(String(derivarSemente(...d.rotulos.map(rotulo))), JSON.stringify(d.rotulos)).toBe(d.valor);
  });
});

describe("a conta inteira", () => {
  const c = G.grade.contas;
  test("div_arred e distancia", () => {
    for (const [n, d, r] of c.div_arred) expect(divArred(n, d), `${n}/${d}`).toBe(r);
    for (const [dx, dy, d] of c.distancia) expect(distancia(dx, dy), `${dx},${dy}`).toBe(d);
    expect(() => divArred(1, 0)).toThrow();
  });
  test("passo_ate, deslocar e regiao_de", () => {
    for (const [x, y, tx, ty, alc, r] of c.passo_ate) expect(passoAte(x, y, tx, ty, alc), JSON.stringify([x, y, tx, ty, alc])).toEqual(r);
    for (const [x, y, d, comp, r] of c.deslocar) expect(deslocar(x, y, d, comp), JSON.stringify([x, y, d, comp])).toEqual(r);
    for (const [x, r] of c.regiao_de) expect(regiaoDe(x)).toBe(r);
  });
  test("o cheiro e a direcao do cheiro", () => {
    let comGradiente = 0;
    for (const [x, y, fontes, r] of c.cheiro) expect(cheiroEm(x, y, fontes as unknown as FonteCheiro[])).toBe(r);
    for (const [x, y, fontes, r] of c.direcao) {
      expect(direcaoDoCheiro(x, y, fontes as unknown as FonteCheiro[]), JSON.stringify([x, y, fontes])).toEqual(r);
      if (r[1]) comGradiente++;
    }
    expect(comGradiente).toBeGreaterThan(20);
  });
});

describe("os eventos do log", () => {
  test("deixar_comida, deixar_bola e a leitura: os mesmos validos e os mesmos invalidos", () => {
    for (const e of G.grade.eventos) {
      const rodar = (): unknown => {
        const a = e.args as unknown[];
        if (e.fn === "deixar_comida") return comoJson(eventoDeixarComida(a[0] as number, a[1] as string, a[2], a[3]));
        if (e.fn === "deixar_bola") return comoJson(eventoDeixarBola(a[0] as number, a[1], a[2]));
        const ev: EventoMundo = { tick: 0, tipo: e.fn === "ler_deixar_comida" ? "deixar_comida" : "deixar_bola", valor: e.valor as string };
        return e.fn === "ler_deixar_comida" ? lerDeixarComida(ev) : lerDeixarBola(ev);
      };
      const a = (e.args ?? []) as unknown[];
      if (e.ok) expect(rodar(), JSON.stringify(e)).toEqual(e.evento ?? e.lido);
      else if (e.float && a.slice(2).every(Number.isInteger)) {
        /* 3.0 do Python: no JS e o mesmo numero que 3 e o TS aceita, com o mesmo texto no log ("3|4"); a unica diferenca, da lingua */
        expect(rodar, JSON.stringify(e)).not.toThrow();
      } else expect(rodar, JSON.stringify(e)).toThrow();
    }
    expect(G.grade.eventos.filter(e => e.float && !e.ok).length).toBe(2);
  });
});

/* o cerebro aleatorio do gabarito (CerebroAleatorio.escolher_alvo), o mesmo em TS */
function escolherAleatorio(acao: AcaoComAlvo, cands: AlvoMundo[], _p: unknown, u: number): AlvoMundo | null {
  const k = u % (cands.length + 2);
  if (k < cands.length) return cands[k];
  if (k === cands.length && acao === "explorar") return alvoPonto((u * 7) % 1024, (u * 13) % 480);
  return null;
}

function configDaVida(v: Vida): ConfigMundo {
  const layout = v.layout === "afastado" ? LAYOUT_MUNDO_AFASTADO : LAYOUT_MUNDO_PADRAO;
  return { ...CMU, layout, mult_queda: v.mult_queda };
}

describe("4 vidas inteiras gravadas no Python, rejogadas no mundo em TS", () => {
  test("o gabarito tem as 4 vidas, com os dois gestos do dono, decisoes com e sem gancho, consumos, a podre, rolagens e o layout afastado", () => {
    expect(G.versao).toBe(1);
    expect(G.vidas.map(v => v.nome)).toEqual(["instinto_atencioso_perto", "aleatorio_aleatorio_longe", "lobos_relapso_comedouro_afastado",
      "aleatorio_atencioso_perto_bola"]);
    const ops = G.vidas.flatMap(v => v.traco);
    expect(ops.some(o => o.op === "deixar_comida") && ops.some(o => o.op === "deixar_bola")).toBe(true);
    const dec = ops.filter((o): o is OpDecisao => o.op === "decisao");
    expect(dec.some(o => o.com_gancho) && dec.some(o => !o.com_gancho)).toBe(true);
    const r = G.vidas.map(v => v.resumo as { consumos: Rec[]; rolagens: Rec[]; quedas: Rec[]; visitas: Rec[] });
    expect(r.every(x => x.quedas.length > 0)).toBe(true);
    expect(r.some(x => x.consumos.some(c => c.como === "achou"))).toBe(true);
    expect(r.some(x => x.consumos.some(c => c.situacao === "podre"))).toBe(true);
    expect(r.some(x => x.rolagens.length > 0) && r.some(x => x.visitas.length > 0)).toBe(true);
    expect(G.vidas.some(v => v.layout === "afastado")).toBe(true);
  });

  for (const v of G.vidas) {
    test(`${v.nome}: decisao a decisao, o resumo e os proximos sorteios`, () => {
      const m = new Mundo({ semente: v.semente, cfg: configDaVida(v), efeitoFrutas: v.efeito });
      let decisoes = 0;
      for (const [i, op] of v.traco.entries()) {
        const onde = `${v.nome}, op ${i} (tick ${op.tick})`;
        if (op.op === "deixar_comida") { m.deixarComida(op.tick, op.tipo, op.x, op.y); continue; }
        if (op.op === "deixar_bola") { m.deixarBola(op.tick, op.x, op.y); continue; }
        decisoes++;
        expect(comoJson(m.antesDaDecisao(op.tick, op.fome_antes)), `percepcao, ${onde}`).toEqual(op.percepcao);
        let escolhido: AlvoMundo | null | undefined;
        const escolher = op.com_gancho
          ? (a: AcaoComAlvo, cs: AlvoMundo[], p: unknown, u: number) => (escolhido = escolherAleatorio(a, cs, p, u))
          : null;
        const { estado, ocorrido } = m.consequencia(op.tick, op.acao, op.estado, escolher, op.regra);
        expect(comoJson(m.ultimosCandidatos), `candidatos, ${onde}`).toEqual(op.candidatos);
        expect(comoJson(ocorrido), `ocorrido, ${onde}`).toEqual(op.ocorrido);
        if (op.com_gancho && escolhido) expect(comoJson(escolhido)).toEqual(op.ocorrido!.alvo);
        expect(estado, `estado depois, ${onde}`).toEqual(op.depois);
        expect(comoJson(m.perceber(op.tick)), `percepcao depois, ${onde}`).toEqual(op.percepcao_depois);
      }
      expect(decisoes).toBe(v.decisoes);
      expect(comoJson(m.resumo())).toEqual(v.resumo);
      const fluxos = { arvores: m.rngArvores, bola: m.rngBola, sujeira: m.rngSujeira, alvo: m.rngAlvo };
      for (const [nome, r] of Object.entries(fluxos)) {
        expect({ random: [r.random(), r.random(), r.random()], randrange16: [r.randrange(1 << 16), r.randrange(1 << 16), r.randrange(1 << 16)] },
          `fluxo ${nome}`).toEqual(v.proximos[nome]);
      }
    });
  }
});

describe("o que o mundo recusa", () => {
  test("alvo fora dos candidatos, ponto fora do mapa e ponto fora do explorar falham alto", () => {
    const novo = () => { const m = new Mundo({ semente: 11 }); m.antesDaDecisao(15, 0.5); return m; };
    const e: EstadoNoMundo = { fome: 0.5, energia: 0.8, humor: 0.5, sujeira: 0 };
    expect(() => novo().consequencia(15, "explorar", e, () => ({ tipo: "casa", x: 1, y: 1, id: null, de: null }))).toThrow(/candidatos/);
    expect(() => novo().consequencia(15, "explorar", e, () => alvoPonto(1024, 0))).toThrow(/fora do mapa/);
    expect(() => novo().consequencia(15, "explorar", e, () => alvoPonto(1.5, 0))).toThrow(/nao inteiro/);
    expect(() => novo().consequencia(15, "comer", e, () => alvoPonto(10, 10))).toThrow(/candidatos/);
    expect(novo().consequencia(15, "explorar", e, () => alvoPonto(300, 200)).ocorrido!.alvo).toEqual(alvoPonto(300, 200));
  });
  test("o mundo desligado, uma fruta sem efeito e o deixar fora do mapa falham alto", () => {
    expect(() => new Mundo({ semente: 1, cfg: { ...CMU, ligada: false } })).toThrow();
    expect(() => new Mundo({ semente: 1, efeitoFrutas: { a: 0, b: 0 } })).toThrow();
    const m = new Mundo({ semente: 1 });
    expect(() => m.deixarComida(0, "racao", 1024, 0)).toThrow();
    expect(() => m.deixarComida(0, "pizza", 1, 0)).toThrow();
    expect(() => m.deixarBola(0, 0, 480)).toThrow();
  });
  test("acao sem alvo so registra e limpa o pendente, sem sortear o u", () => {
    const m = new Mundo({ semente: 11 });
    const antes = new RandomPy(derivarSemente("alvo", 11)).randrange(1 << 16);
    m.antesDaDecisao(15, 0.5);
    const r = m.consequencia(15, "dormir", { fome: 0.5, energia: 0.8, humor: 0.5, sujeira: 0 });
    expect(r.ocorrido).toBeNull();
    expect(m.rngAlvo.randrange(1 << 16)).toBe(antes);
  });
});
