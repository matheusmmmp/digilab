/* O cerebro A aprendendo, o pet v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 3; o gate G-PAR-L1): motor/lobos.ts reproduz, decisao
   a decisao, as quatro vidas da secao v11 do gabarito do Python (test/gabaritos/lobos_python.json, de
   experiments/exportar_gabarito_lobos.py), bit a bit no Node.

   O que se rejoga sao os `ganchos` de cada vida: cada chamada que o motor do Python fez ao cerebro, na ordem, com o que ela levou (a
   observacao com os receptores do corpo, a transicao da decisao, o ocorrido do gancho do corpo, a acao do dono e o tick, o antes e o
   depois do carinho). O exportador os grava num replay do log com a politica embrulhada e confere que esse replay e a vida. O laco do
   motor com o corpo nao roda aqui: o corpo do v11 (com o metabolismo) ja existe no corpo.ts (a etapa 4 do metabolismo; a paridade dele
   esta em test/metabolismo.test.ts), mas o Motor com o corpo por tick e da etapa 4 do W-PORTE.

   Em cada decisao, depois do gancho do corpo, o motivo inteiro e o do Python (toStrictEqual, que compara os numeros por Object.is): a
   regra, os candidatos, a percepcao e a do corpo, as contribuicoes por lobo, os pesos efetivos, o u, a acao, o lobo decisivo, o
   aprendido, o aprendido do corpo e o sinal_corpo. No fim: os pesos, os pesos do corpo, o resumo do aprendizado, a memoria e emocao e
   os canais. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CLB, CLB_V11 } from "../motor/constantes.ts";
import {
  BracoConsequencia, CerebroA, arred, atualizarPesos, contribuicoesCorpo, sinalCorpo, sinalCorpoCanais, tabelaPrior,
  type MotivoLobos, type ObservacaoLobos, type OcorridoCorpo, type PesosDaRegra,
} from "../motor/lobos.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Gancho = [string, ...unknown[]];
interface VidaV11 {
  dono: string; semente: number; gestos: Record<string, number>; log: { tipo: string; valor: unknown }[]; motivos: MotivoLobos[];
  pesos: unknown; pesos_prior: unknown; pesos_corpo: unknown; aprendizado: Record<string, unknown>; corpo: unknown;
  memoria_emocao: unknown; canais: unknown; ganchos: Gancho[];
}
interface ConfigV11 {
  lobos: Record<string, unknown>; consequencia: Record<string, unknown> & { pesos_drives_corpo: [string, number][] };
  corpo: Record<string, unknown>; receptores: string[];
}
const G = JSON.parse(readFileSync(new URL("./gabaritos/lobos_python.json", import.meta.url), "utf8")) as {
  versao: number; braco: string; config_v11: ConfigV11; v11: VidaV11[];
};
const CV = G.config_v11;

/** a ConfigConsequencia do v11 pela constante */
const CC_V11 = { drives: CLB_V11.drives, ganho: CLB_V11.ganho, canais: CLB_V11.canais, pesosDrivesCorpo: CLB_V11.pesosDrivesCorpo };

/** o pet v11: o cerebro A com o aprendiz e o corpo do gabarito, atras do braco da consequencia */
function bracoV11(mudancas: Partial<typeof CLB_V11> = {}): BracoConsequencia {
  const p = { ...CLB_V11, ...mudancas };
  const co = CV.corpo as { ligada: boolean; drives_novos: boolean; gestos: boolean; banheiro: boolean; escala_receptor: number };
  const cerebro = new CerebroA({
    aprendizadoLigado: true, ...CLB, aprendiz: { passo: p.passo, teto: p.teto, piso: p.piso, recompensaTapa: p.recompensaTapa },
    corpo: { ligada: co.ligada, drives_novos: co.drives_novos, gestos: co.gestos, banheiro: co.banheiro, escala_receptor: co.escala_receptor },
  });
  return new BracoConsequencia(cerebro, CC_V11);
}

const obsDe = (v: unknown, tdc: unknown, corpo: unknown): ObservacaoLobos =>
  ({ v: v as number[], tdc: tdc as number, corpo: Object.fromEntries(CV.receptores.map((r, i) => [r, (corpo as number[])[i]])) });

/** a rng que devolve o u gravado, uma vez so; sem u gravado, qualquer chamada falha */
function rngDoGabarito(u: number | null) {
  const r = { chamadas: 0, random() { r.chamadas += 1; if (u === null || r.chamadas > 1) throw new Error("rng chamada sem u gravado"); return u; } };
  return r;
}

/** rejoga os ganchos da vida no braco, conferindo cada motivo depois do gancho do corpo da decisao */
function rejogar(vida: VidaV11, braco: BracoConsequencia, ganchos: Gancho[] = vida.ganchos): void {
  let n = 0;
  for (const g of ganchos) {
    switch (g[0]) {
      case "agir": {
        const m = vida.motivos[n];
        const rng = rngDoGabarito(m.u);
        const acao = braco.agir(obsDe(g[1], g[2], g[3]), rng);
        expect(rng.chamadas, `decisao ${n}: chamadas da rng`).toBe(m.u === null ? 0 : 1);
        expect(acao, `decisao ${n}`).toBe(m.acao);
        n += 1;
        break;
      }
      case "observar":
        braco.observar({ acao: g[1] as AcaoPet, observacao: obsDe(g[2], g[3], g[4]), observacaoSeguinte: obsDe(g[5], g[6], g[7]) });
        break;
      case "consequencia_corpo":
        braco.consequenciaCorpo(g[1] as AcaoPet, g[2] as OcorridoCorpo, obsDe(g[3], g[4], g[5]));
        expect(braco.cerebro.ultimoMotivo, `decisao ${n - 1}`).toStrictEqual(vida.motivos[n - 1]);
        break;
      case "dono":
        braco.receberAcaoDono(g[1] as string, g[2] as number);
        break;
      case "carinho":
        braco.mudancaNoCorpo(obsDe(g[1], g[2], g[3]), obsDe(g[4], g[5], g[6]));
        break;
      default:
        throw new Error(`gancho desconhecido: ${g[0]}`);
    }
  }
  expect(n).toBe(vida.motivos.length);
}

describe("G-PAR-L1: o cerebro A aprendendo (o pet v11) = o gabarito do Python, decisao a decisao", () => {
  test("o gabarito e o esperado: o braco P1-c-tapa, quatro vidas de 288 decisoes, os receptores do corpo do v11", () => {
    expect(G.versao).toBe(1);
    expect(G.braco).toBe("P1-c-tapa");
    expect(G.v11.map(v => [v.dono, v.semente, v.motivos.length])).toEqual(
      [["atencioso", 101, 288], ["relapso", 202, 288], ["aleatorio", 303, 288], ["incoerente", 404, 288]]);
    expect(CV.receptores).toEqual(["fome", "higiene", "energia", "humor", "saude", "tedio", "solidao", "estresse", "dor", "susto"]);
  });

  test("o ponto do v11 e o do gabarito (CLB_V11), sem chave que o TS nao tenha", () => {
    const cl = CV.lobos, cc = CV.consequencia, co = CV.corpo;
    expect([cl.aprendizado_ligado, cl.bits_ponto_fixo, cl.escala_ticks_desde_cuidado, cl.maximo_pesos]).toEqual([true, CLB.bits, CLB.escalaTdc, CLB.maxPesos]);
    expect([cl.passo, cl.teto, cl.piso_peso, cl.recompensa_tapa]).toEqual([CLB_V11.passo, CLB_V11.teto, CLB_V11.piso, CLB_V11.recompensaTapa]);
    expect([cc.drives, cc.ganho, cc.canais_ligados]).toEqual([CLB_V11.drives, CLB_V11.ganho, CLB_V11.canais]);
    expect(Object.fromEntries(cc.pesos_drives_corpo)).toEqual(CLB_V11.pesosDrivesCorpo);
    /* as chaves que o cerebro TS nao portou: desligadas no v11 */
    expect([cl.traco_decisoes, cl.memoria_ligada, cl.w0_info, cl.w0_pedido, cl.alvo_aprendido, cl.entradas_sociais, cl.modelo_outros,
      cl.presenca_fruta_mundo, cl.g_plano, cl.paladar, cc.pesos_janela]).toEqual([0, false, 0, 0, false, false, false, false, 0, false, false]);
    expect([co.ligada, co.drives_novos, co.gestos, co.banheiro, co.paladar, co.escala_receptor]).toEqual([true, true, true, false, false, 1024]);
    /* o metabolismo esta ligado nas vidas: o laco do corpo nao roda em TS nesta etapa (so os ganchos; o Motor e da etapa 4) */
    expect(co.metabolismo).toBe(true);
  });

  for (const vida of G.v11) {
    test(`${vida.dono} ${vida.semente}: os ganchos sao os do log (288 decisoes, os carinhos e as acoes do dono)`, () => {
      const conta = (t: string) => vida.ganchos.filter(g => g[0] === t).length;
      expect([conta("agir"), conta("observar"), conta("consequencia_corpo")]).toEqual([288, 288, 288]);
      /* o carinho do log (o do dono e o elogio trocado pelo DonoComGestos) chega so pelo corpo; o tapa, pelo receber_acao_dono */
      const noLog = (valor: string) => vida.log.filter(e => e.tipo === "acao_usuario" && e.valor === valor).length;
      expect(conta("carinho")).toBe(noLog("acariciar"));
      expect(conta("carinho")).toBeGreaterThanOrEqual(vida.gestos.acariciar);
      expect(vida.ganchos.filter(g => g[0] === "dono" && g[1] === "tapa").length).toBe(noLog("tapa"));
      expect(noLog("tapa")).toBe(vida.gestos.tapa);
      expect(conta("carinho") + conta("dono")).toBe(vida.log.filter(e => e.tipo === "acao_usuario").length);
      expect(vida.log.some(e => e.valor === "elogiar" || e.valor === "repreender")).toBe(false);
    });

    test(`${vida.dono} ${vida.semente}: cada motivo, e no fim os pesos, os pesos do corpo, o aprendizado, a memoria e os canais`, () => {
      const braco = bracoV11();
      rejogar(vida, braco);
      const interno = braco.cerebro.estadoInterno();
      expect(interno.pesos).toStrictEqual(vida.pesos);
      expect(interno.pesos_prior).toStrictEqual(vida.pesos_prior);
      expect(interno.pesos_corpo).toStrictEqual(vida.pesos_corpo);
      expect(interno.aprendizado).toStrictEqual(vida.aprendizado);
      expect(interno.memoria_emocao).toStrictEqual(vida.memoria_emocao);
      expect(interno.canais).toStrictEqual(vida.canais);
      expect(interno.corpo).toStrictEqual(vida.corpo);
      expect(interno.n_decisoes).toBe(vida.motivos.length);
      /* o cerebro aprendeu de verdade: os pesos sairam do prior */
      expect(interno.pesos).not.toStrictEqual(interno.pesos_prior);
    });
  }

  test("as quatro vidas juntas tem carinho e tapa creditados e passam por mais de tres regras", () => {
    const tapas = G.v11.reduce((s, v) => s + (v.aprendizado.recompensas as Record<string, number>).tapa, 0);
    const carinhos = G.v11.reduce((s, v) => s + (v.aprendizado.recompensas as Record<string, number>).carinho, 0);
    expect(tapas).toBeGreaterThan(0);
    expect(carinhos).toBeGreaterThan(0);
    /* as regras vistas nas decisoes */
    expect(new Set(G.v11.flatMap(v => v.motivos.map(m => m.regra))).size).toBeGreaterThan(3);
  });

  test("controle negativo: um receptor mexido em 1 num gancho do corpo e pego", () => {
    const vida = G.v11[0];
    const ganchos = structuredClone(vida.ganchos);
    const i = ganchos.findIndex(g => g[0] === "consequencia_corpo" && (g[5] as number[])[5] > 0);
    (ganchos[i][5] as number[])[5] -= 1;                       // o tedio depois da decisao
    expect(() => rejogar(vida, bracoV11(), ganchos)).toThrow();
  });

  test("controle negativo: o tapa com outra recompensa e pego", () => {
    expect(() => rejogar(G.v11[0], bracoV11({ recompensaTapa: -0.5 }))).toThrow();
  });
});

describe("a aritmetica do aprendizado", () => {
  test("arred: meio longe do zero, sem o -0", () => {
    expect([arred(0.5), arred(1.5), arred(2.5), arred(-0.5), arred(-1.5), arred(0.4)]).toEqual([1, 2, 3, -1, -2, 0]);
    /* como o int(x + 0.5) do Python: o maior double abaixo de 0,5 mais 0,5 arredonda para 1.0 */
    expect(arred(0.49999999999999994)).toBe(1);
    expect(Object.is(arred(-0.4), 0)).toBe(true);
    expect(() => arred(NaN)).toThrow();
  });

  test("atualizarPesos: o passo da regra da L1 e o corte em prior +- teto", () => {
    const prior = tabelaPrior(1024).tempo_livre;
    const pesos = Object.fromEntries(Object.entries(prior).map(([a, v]) => [a, [...v]])) as PesosDaRegra;
    const registro = { candidatos: ["ocioso", "brincar"] as AcaoPet[], acao: "brincar" as AcaoPet, X: [1024, 0, 0, 0, 512, 0, 0, 0, 0, 0],
      P: { ocioso: 512, brincar: 512 }, W: { ocioso: 3072, brincar: 2560 } };
    /* dw = div_arred(f passo X (S 1[a=a*] - P), S S W): brincar com X=1024, f=1024, passo=512: 1024*512*1024*512 / (1024*1024*2560) */
    expect(atualizarPesos(pesos, prior, registro, 1024, 512, 16384, 1024)).toBe(0);
    expect(pesos.brincar[0] - prior.brincar[0]).toBe(Math.round(1024 * 512 * 1024 * 512 / (1024 * 1024 * 2560)));
    expect(pesos.ocioso[0] - prior.ocioso[0]).toBe(-Math.round(1024 * 512 * 1024 * 512 / (1024 * 1024 * 3072)));
    expect(pesos.comer).toEqual(prior.comer);
    /* com teto pequeno, os dois pesos de cada candidato com X != 0 sao cortados */
    expect(atualizarPesos(pesos, prior, registro, 1024 * 64, 512, 100, 1024)).toBe(4);
    expect(pesos.brincar[0] - prior.brincar[0]).toBe(100);
    expect(pesos.ocioso[4] - prior.ocioso[4]).toBe(-100);
    /* um numerador fora dos inteiros exatos do double falha alto */
    expect(() => atualizarPesos(pesos, prior, registro, 2 ** 40, 512, 100, 1024)).toThrow(/inteiros exatos/);
  });

  test("sinalCorpoCanais: a soma dos canais e o sinalCorpo (K-6); um receptor ausente falha alto", () => {
    const drives = ["fome", "higiene", "energia", "tedio", "solidao", "estresse", "dor"];
    const antes = { fome: 700, higiene: 1000, energia: 333, tedio: 90, solidao: 15, estresse: 0, dor: 7, susto: 0, humor: 500, saude: 1024 };
    const depois = { ...antes, fome: 701, energia: 300, tedio: 120, dor: 3 };
    for (const ganho of [1, 3, 4, 7]) {
      const canais = sinalCorpoCanais(antes, depois, drives, ganho, 1024, CLB_V11.pesosDrivesCorpo);
      expect(Object.keys(canais)).toEqual(drives);
      expect(Object.values(canais).reduce((s, f) => s + f, 0)).toBe(sinalCorpo(antes, depois, drives, ganho, 1024, CLB_V11.pesosDrivesCorpo));
    }
    expect(contribuicoesCorpo(antes, depois, ["tedio"], 1024, CLB_V11.pesosDrivesCorpo)).toEqual({ tedio: 2 * (90 * 90 - 120 * 120) });
    expect(() => sinalCorpo(antes, { ...depois, dor: undefined as unknown as number }, drives, 4, 1024, CLB_V11.pesosDrivesCorpo)).toThrow(/dor/);
    expect(() => sinalCorpo(antes, { ...depois, fome: 1025 }, drives, 4, 1024, CLB_V11.pesosDrivesCorpo)).toThrow(/fora/);
  });

  test("falhas altas: elogio e bronca, a fruta, o gancho que falta, a decisao sem gancho, o banheiro", () => {
    const vida = G.v11[0];
    const [agir, observar, conseq] = vida.ganchos.slice(0, 3);
    const decidir = (b: BracoConsequencia) => {
      b.agir(obsDe(agir[1], agir[2], agir[3]), rngDoGabarito(vida.motivos[0].u));
      b.observar({ acao: observar[1] as AcaoPet, observacao: obsDe(observar[2], observar[3], observar[4]),
        observacaoSeguinte: obsDe(observar[5], observar[6], observar[7]) });
    };
    let b = bracoV11();
    expect(() => b.cerebro.receberAcaoDono("elogiar", 0)).toThrow(/elogio/);
    b = bracoV11();
    decidir(b);
    /* a proxima decisao sem o gancho do corpo */
    expect(() => b.agir(obsDe(agir[1], agir[2], agir[3]), rngDoGabarito(vida.motivos[0].u))).toThrow(/gancho/);
    b = bracoV11();
    decidir(b);
    const oc = conseq[2] as OcorridoCorpo;
    expect(() => b.consequenciaCorpo(conseq[1] as AcaoPet, { ...oc, estimulos: [...oc.estimulos, ["fruta", "a"]] },
      obsDe(conseq[3], conseq[4], conseq[5]))).toThrow(/fruta/);
    b = bracoV11();
    decidir(b);
    b.consequenciaCorpo(conseq[1] as AcaoPet, oc, obsDe(conseq[3], conseq[4], conseq[5]));
    expect(() => b.consequenciaCorpo(conseq[1] as AcaoPet, oc, obsDe(conseq[3], conseq[4], conseq[5]))).toThrow(/segunda chamada/);
    expect(() => new CerebroA({ aprendizadoLigado: false, ...CLB,
      corpo: { ligada: true, drives_novos: true, gestos: true, banheiro: true, escala_receptor: 1024 } })).toThrow(/banheiro/);
  });
});
