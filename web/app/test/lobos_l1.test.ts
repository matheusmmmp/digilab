/* O cerebro A em TS, aprendendo (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 3; o gate G-PAR-L1): motor/lobos.ts reproduz as quatro
   vidas da secao v11 do gabarito do Python (test/gabaritos/lobos_python.json, de experiments/exportar_gabarito_lobos.py), bit a bit no
   Node: o aprendizado pela consequencia no corpo e os gestos do dono (o tapa e o carinho).

   O motor do v11 (o MotorCorpo com o metabolismo) e a etapa 4; aqui o teste rejoga o `traco` da vida, as chamadas que chegaram ao
   cerebro no Python, na ordem e com as observacoes inteiras (o Estado.vetor, o ticks_desde_cuidado e os receptores do corpo):
     agir          a decisao, com a rng que devolve o u gravado no motivo;
     consequencia  a transicao do engine (da observacao da decisao a seguinte) e o f_S que o braco calculou: o TS confere o f_S;
     corpo         o gancho do corpo, com o `ocorrido` e a observacao depois dos estimulos da acao: o sinal pelos receptores;
     dono          o tapa (receber_acao_dono), o unico gesto do dono que passa pelo braco P1-c-tapa;
     carinho       o carinho, so pelo corpo (mudanca_no_corpo), com os receptores antes e depois dele.
   Cada motivo e conferido logo depois do gancho do corpo da decisao (com o sinal_corpo), e no fim o estado interno inteiro: os pesos, os
   pesos do corpo, o aprendizado (as recompensas, as atualizacoes, a ultima decisao), os canais e os contadores da memoria. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCO_DRIVES, Corpo, quimicosDe } from "../motor/corpo.ts";
import {
  CerebroA, atualizarPesos, arred, sinalCorpoCanais, sinalCorpo, tabelaPrior, type ConfigConsequenciaLobos, type ConfigLobosWeb,
  type MotivoLobos, type ObservacaoLobos, type OcorridoCorpo,
} from "../motor/lobos.ts";
import type { AcaoPet } from "../motor/tipos.ts";

type Passo =
  | { t: "agir"; obs: ObservacaoLobos }
  | { t: "consequencia"; acao: AcaoPet; depois: ObservacaoLobos; f_S: number }
  | { t: "corpo"; acao: AcaoPet; ocorrido: OcorridoCorpo; depois: ObservacaoLobos }
  | { t: "dono"; acao: string; tick: number }
  | { t: "carinho"; antes: ObservacaoLobos; depois: ObservacaoLobos };
interface VidaV11 {
  dono: string; semente: number; motivos: MotivoLobos[]; traco: Passo[]; interno: Record<string, unknown>;
  pesos: unknown; pesos_corpo: unknown; aprendizado: { recompensas: Record<string, number> };
}
const G = JSON.parse(readFileSync(new URL("./gabaritos/lobos_python.json", import.meta.url), "utf8")) as {
  braco: string; config: { lobos: Record<string, number | boolean>; consequencia: ConfigConsequenciaLobos }; v11: VidaV11[];
};

/** a ConfigLobos do v11, da config do gabarito */
function configV11(): ConfigLobosWeb {
  const cl = G.config.lobos as Record<string, number>;
  return {
    aprendizadoLigado: G.config.lobos.aprendizado_ligado as boolean, bits: cl.bits_ponto_fixo, escalaTdc: cl.escala_ticks_desde_cuidado,
    maxPesos: cl.maximo_pesos,
    aprendizado: { passo: cl.passo, teto: cl.teto, pisoPeso: cl.piso_peso, janelaLatencia: cl.janela_latencia_ticks,
      recompensaTapa: cl.recompensa_tapa, tracoDecisoes: cl.traco_decisoes },
  };
}

/** a rng que devolve o u gravado, uma vez so; sem u gravado, qualquer chamada falha */
function rngDoGabarito(u: number | null) {
  const r = { chamadas: 0, random() { r.chamadas += 1; if (u === null || r.chamadas > 1) throw new Error("rng chamada sem u gravado"); return u; } };
  return r;
}

/** rejoga o traco de uma vida num cerebro novo; `conferir` recebe cada motivo pronto (depois do gancho do corpo) */
function rejogar(vida: VidaV11, traco: readonly Passo[] = vida.traco, conferir?: (m: MotivoLobos, n: number) => void,
  cfg: ConfigLobosWeb = configV11()): CerebroA {
  const cerebro = new CerebroA(cfg, CCO_DRIVES);
  const cc = G.config.consequencia;
  let k = 0, obs: ObservacaoLobos | null = null, acao: AcaoPet | null = null;
  for (const p of traco) {
    if (p.t === "agir") {
      const m = vida.motivos[k];
      const rng = rngDoGabarito(m.u);
      acao = cerebro.agir(p.obs, rng);
      if (rng.chamadas !== (m.u === null ? 0 : 1)) throw new Error(`decisao ${k}: ${rng.chamadas} chamadas da rng`);
      obs = p.obs;
      k += 1;
    } else if (p.t === "consequencia") {
      if (obs === null || p.acao !== acao) throw new Error(`decisao ${k - 1}: consequencia de ${p.acao}, decisao de ${acao}`);
      cerebro.observarConsequencia({ observacao: obs, acao: p.acao, observacaoSeguinte: p.depois }, p.f_S, cc);
    } else if (p.t === "corpo") {
      cerebro.consequenciaCorpo(p.acao, p.ocorrido, p.depois);
      conferir?.(cerebro.ultimoMotivo!, k - 1);
    } else if (p.t === "dono") cerebro.receberAcaoDono(p.acao, p.tick);
    else if (p.t === "carinho") cerebro.mudancaNoCorpo(p.antes, p.depois);
    else throw new Error(`passo desconhecido no traco: ${JSON.stringify(p)}`);
  }
  return cerebro;
}

describe("G-PAR-L1: o cerebro A aprendendo = o gabarito do Python, vida a vida", () => {
  test("o gabarito e o v11: o braco P1-c-tapa, quatro vidas de 288 decisoes, o aprendizado ligado e o corpo com os gestos", () => {
    expect(G.braco).toBe("P1-c-tapa");
    expect(G.v11.map(v => [v.dono, v.semente, v.motivos.length])).toEqual(
      [["atencioso", 101, 288], ["relapso", 202, 288], ["aleatorio", 303, 288], ["incoerente", 404, 288]]);
    const c = new CerebroA(configV11(), CCO_DRIVES);
    for (const v of G.v11) expect(v.interno.corpo).toStrictEqual({ receptores_novos: c.receptoresNovos, canais_novos: c.canaisNovos });
    /* o v11 passa por tudo o que a etapa porta: o tapa, o carinho com e sem sinal, a consequencia em toda decisao */
    expect(G.v11.every(v => v.aprendizado.recompensas.carinho > 0 && v.aprendizado.recompensas.consequencia === 288)).toBe(true);
    expect(G.v11.some(v => v.aprendizado.recompensas.tapa > 0)).toBe(true);
  });

  test("os receptores do traco sao os de Corpo.receptores() (corpo.ts) com o corpo do v11 sem o metabolismo", () => {
    const corpo = new Corpo(Object.fromEntries(quimicosDe(CCO_DRIVES).map(n => [n, 0])), { cc: CCO_DRIVES });
    const nomes = Object.keys(corpo.receptores()).sort();
    for (const v of G.v11) for (const p of v.traco) {
      for (const o of p.t === "agir" ? [p.obs] : p.t === "carinho" ? [p.antes, p.depois] : p.t === "dono" ? [] : [p.depois]) {
        expect(Object.keys(o.corpo!).sort()).toEqual(nomes);
      }
    }
    /* e o cerebro decide lendo um Corpo do TS direto */
    const cerebro = new CerebroA(configV11(), CCO_DRIVES);
    expect(cerebro.agir({ v: [0.9, 0.9, 0.9, 0.9, 1, 0, 0, 0.5], tdc: 0, corpo: corpo.receptores() }, { random: () => 0.5 })).toBe("explorar");
    expect(cerebro.ultimoMotivo!.percepcao_corpo).toStrictEqual({ tedio: 0, solidao: 0, estresse: 0, dor: 0, susto: 0 });
  });

  for (const vida of G.v11) {
    test(`${vida.dono} ${vida.semente}: cada motivo, os pesos, os pesos do corpo, o aprendizado, os canais e a memoria`, () => {
      const cerebro = rejogar(vida, vida.traco, (m, n) => {
        /* toStrictEqual compara os numeros com Object.is: bit a bit, e o -0 contaria */
        expect(m, `decisao ${n}`).toStrictEqual(vida.motivos[n]);
      });
      const { motivos, ...resto } = cerebro.estadoInterno();
      expect(motivos).toStrictEqual(vida.motivos);
      expect(resto).toStrictEqual(vida.interno);
      expect(resto.pesos).toStrictEqual(vida.pesos);
      expect(resto.pesos_corpo).toStrictEqual(vida.pesos_corpo);
      /* e o cerebro aprendeu: a tabela saiu do prior e as entradas do corpo sairam do zero */
      expect(cerebro.pesos).not.toStrictEqual(tabelaPrior(cerebro.escala));
      expect(Object.values(cerebro.pesosCorpo.tempo_livre!).flat().some(w => w !== 0)).toBe(true);
    });
  }

  test("controles negativos: sem um carinho, sem um tapa ou com o tapa de sinal trocado, os pesos saem outros", () => {
    const vida = G.v11.find(v => v.aprendizado.recompensas.tapa > 0)!;
    const certo = rejogar(vida).estadoInterno();
    /* os gestos que mexem nos pesos, como no Python: so depois de uma decisao com mais de um candidato (com um so, P = S e a regra da
       L1 nao mexe em nada); no carinho, o de maior sinal (um sinal pequeno arredonda a zero em todo peso) */
    const cc = G.config.consequencia, pd = Object.fromEntries(cc.pesos_drives_corpo);
    const drives = ["fome", "higiene", "energia", ...certo.corpo!.canais_novos];
    const decisaoAntes = (i: number) => vida.motivos[vida.traco.slice(0, i).filter(p => p.t === "agir").length - 1];
    const sinal = (p: Passo) => (p.t === "carinho" ? Math.abs(sinalCorpo(p.antes.corpo!, p.depois.corpo!, drives, cc.ganho, 1024, pd)) : 1);
    const mexe = (t: Passo["t"]) => {
      const i = vida.traco.map((p, j) => (p.t === t && decisaoAntes(j).candidatos.length > 1 ? sinal(p) : 0));
      expect(Math.max(...i)).toBeGreaterThan(0);
      return i.indexOf(Math.max(...i));
    };
    /* os pesos logo depois do gesto, com e sem ele (depois, a decisao seguinte ja pode sair outra e o traco nao vale mais) */
    const ate = (i: number) => vida.traco.slice(0, i + 1);
    const pesos = (traco: readonly Passo[], cfg?: ConfigLobosWeb) => rejogar(vida, traco, undefined, cfg).estadoInterno().pesos;
    for (const i of [mexe("carinho"), mexe("dono")]) {
      expect(pesos(ate(i).slice(0, i)), `sem o passo ${i}`).not.toStrictEqual(pesos(ate(i)));
    }
    const cfg = configV11(), tapa = mexe("dono");
    expect(pesos(ate(tapa), { ...cfg, aprendizado: { ...cfg.aprendizado!, recompensaTapa: 1.0 } })).not.toStrictEqual(pesos(ate(tapa)));
  });

  test("controle negativo: um f_S que nao e o da transicao, ou um gancho do corpo que falta, falham alto", () => {
    const vida = G.v11[0];
    const i = vida.traco.findIndex(p => p.t === "consequencia");
    const errado = vida.traco.map((p, j) => (j === i && p.t === "consequencia" ? { ...p, f_S: p.f_S + 1 } : p));
    expect(() => rejogar(vida, errado)).toThrow(/sinal_homeostatico/);
    const semGancho = vida.traco.filter((p, j) => !(p.t === "corpo" && j === i + 1));
    expect(() => rejogar(vida, semGancho)).toThrow(/sem o gancho/);
  });
});

describe("a conta inteira do aprendizado", () => {
  test("arred: meio longe do zero, sem -0", () => {
    expect([arred(0.5), arred(1.5), arred(-0.5), arred(-1.5), arred(2.4999), arred(-2.4999)]).toEqual([1, 2, -1, -2, 2, -2]);
    expect(Object.is(arred(-0.2), 0)).toBe(true);
  });

  test("atualizarPesos: a escolhida sobe, as outras descem, o teto corta", () => {
    const S = 1024;
    const pesos = { ocioso: [S, 0], brincar: [S, 0] } as Partial<Record<AcaoPet, number[]>>;
    const prior = { ocioso: [S, 0], brincar: [S, 0] } as Partial<Record<AcaoPet, number[]>>;
    const registro = { candidatos: ["ocioso", "brincar"] as AcaoPet[], acao: "ocioso" as AcaoPet, X: [S, 0], P: { ocioso: 512, brincar: 512 },
      W: { ocioso: S, brincar: S } };
    expect(atualizarPesos(pesos, prior, registro, 1024, 512, 16384, S)).toBe(0);
    expect(pesos).toStrictEqual({ ocioso: [S + 256, 0], brincar: [S - 256, 0] });
    expect(atualizarPesos(pesos, prior, registro, 1024 * 64, 512, 1000, S)).toBe(2);
    expect(pesos).toStrictEqual({ ocioso: [S + 1000, 0], brincar: [S - 1000, 0] });
  });

  test("sinalCorpoCanais: a soma dos canais e o sinalCorpo (contrato K-6)", () => {
    const antes = { fome: 700, higiene: 1000, energia: 900, tedio: 300, dor: 0 };
    const depois = { fome: 820, higiene: 990, energia: 880, tedio: 120, dor: 50 };
    const pd = { fome: 1, higiene: 1, energia: 1, tedio: 2, dor: 2 };
    const drives = ["fome", "higiene", "energia", "tedio", "dor"];
    const canais = sinalCorpoCanais(antes, depois, drives, 4, 1024, pd);
    expect(Object.values(canais).reduce((a, b) => a + b, 0)).toBe(sinalCorpo(antes, depois, drives, 4, 1024, pd));
  });

  test("as chaves que o v11 nao tem falham alto", () => {
    const cfg = configV11();
    expect(() => new CerebroA({ ...cfg, aprendizado: undefined })).toThrow(/parametros da L1/);
    expect(() => new CerebroA({ ...cfg, aprendizado: { ...cfg.aprendizado!, tracoDecisoes: 2 } })).toThrow(/traco/);
    expect(() => new CerebroA(cfg, { ...CCO_DRIVES, banheiro: true })).toThrow(/banheiro/);
    const c = new CerebroA(cfg, CCO_DRIVES);
    expect(() => c.receberAcaoDono("elogiar", 10)).toThrow(/elogio/);
  });
});
