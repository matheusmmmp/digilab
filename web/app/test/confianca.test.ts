/* M1: confianca de combate e desgaste por rival repetido (docs/DESIGN_MVP_M1_CONFIANCA.md).
   Gate G2: motor/confianca.ts reproduz o gabarito do Python (experiments/exportar_gabarito_confianca.py) ate 1e-12,
   inclusive a frase de estado com histerese. E os pets v5: a confianca entra no epsilon, na experiencia e no passo
   dos gambits; os v1-v4 nao mudam (gabaritos de paridade e educacao_v4.test.ts seguem iguais). */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCF, CLE, DUR_EVO, GA, TICK_INICIAL } from "../motor/constantes.ts";
import { ConfiancaCombate, atualizarConfianca, atualizarEncontros, epsilonConfianca, novidade, tickSaidaFaixa } from "../motor/confianca.ts";
import { CONFIANCA_TXT, expressarConfianca } from "../motor/expressao.ts";
import { lutadorPet } from "../motor/gambits_pet.ts";
import { Motor } from "../motor/motor.ts";

const G = JSON.parse(readFileSync(new URL("./gabaritos/confianca_python.json", import.meta.url), "utf8"));
const TOL = 1e-12;

describe("confianca (M1)", () => {
  test("constantes = config do gabarito", () => {
    const c = G.config;
    expect([CCF.lambda, CCF.tauHab, CCF.eta, CCF.kSens, CCF.tauConf, CCF.kappaEps, CCF.limiarFrase, CCF.histerese, CCF.limiarTedio, CCF.nTedio])
      .toEqual([c.lambda_novidade, c.tau_habituacao_min, c.eta_confianca, c.k_sensibilidade, c.tau_confianca_min, c.kappa_eps, c.limiar_frase, c.histerese_frase_min, c.limiar_tedio, c.n_tedio]);
  });

  test("G2: 200 lutas do gabarito do Python, c e novidade iguais ate 1e-12, frases de estado iguais", () => {
    const cc = new ConfiancaCombate();
    for (const p of G.passos) {
      const r = cc.registrar(p.tick, p.rival, p.sinal, p.sensibilidade);
      expect(Math.abs(r.novidade - p.novidade), `novidade na luta ${p.k}`).toBeLessThanOrEqual(TOL);
      expect(Math.abs(r.c - p.c), `c na luta ${p.k}`).toBeLessThanOrEqual(TOL);
      expect(Math.abs(cc.valor(p.tick + CCF.histerese) - p.valor_2h), `valor 2 h depois da luta ${p.k}`).toBeLessThanOrEqual(TOL);
      const e0 = cc.estado(p.tick), e1 = cc.estado(p.tick + CCF.histerese);
      expect([e0.estado, e0.desde, e0.lutas], `estado na luta ${p.k}`).toEqual([p.estado, p.desde, p.lutas]);
      expect([e1.estado, e1.desde, e1.lutas], `estado 2 h depois da luta ${p.k}`).toEqual([p.estado_2h, p.desde_2h, p.lutas_2h]);
    }
    expect(Math.abs(cc.c - G.final.c)).toBeLessThanOrEqual(TOL);
    expect(cc.historico.length).toBe(G.final.lutas);
    for (const [r, m] of Object.entries(G.final.encontros as Record<string, number>)) expect(Math.abs(cc.encontros[r] - m)).toBeLessThanOrEqual(TOL);
    expect(G.estados).toEqual(["confiante", "entediado", "inseguro", "neutro"]);   /* o gabarito exercita as 4 faixas */
  });

  test("curvas: novidade 1 -> ~0,25 na 3a -> ~0,06 na 5a; corte em +-1; decaimento", () => {
    let m = 0; const novs: number[] = [];
    for (let i = 0; i < 5; i++) { novs.push(novidade(m, CCF.lambda)); m = atualizarEncontros(m, 0, CCF.tauHab); }
    expect(novs[0]).toBe(1); expect(novs[2]).toBeCloseTo(0.25, 2); expect(novs[4]).toBeCloseTo(0.06, 2);
    let c = 0;
    for (let i = 0; i < 20; i++) c = atualizarConfianca(c, 0, 1, 1, 0);
    expect(c).toBe(1);
    for (let i = 0; i < 40; i++) c = atualizarConfianca(c, 0, -1, 1, 1);
    expect(c).toBe(-1);
    expect(atualizarConfianca(0.8, CCF.tauConf, 0, 1, 0)).toBeCloseTo(0.8 / Math.E, 12);
    expect(atualizarConfianca(0, 0, -1, 1, 1)).toBeCloseTo(-CCF.eta * (1 + CCF.kSens), 12);
    expect(epsilonConfianca(-1, CCF.kappaEps)).toBe(CCF.kappaEps); expect(epsilonConfianca(1, CCF.kappaEps)).toBe(0);
    expect(() => atualizarConfianca(0, 0, 2, 1, 0)).toThrow();
  });

  test("histerese: a frase so troca depois de 2 h na faixa nova", () => {
    const cc = new ConfiancaCombate();
    ["a", "b", "a", "b"].forEach((r, k) => cc.registrar(1000 + 30 * k, r, 1, 0));
    expect(cc.estado(1030 + CCF.histerese - 1).estado).toBe("neutro");
    expect(cc.estado(1030 + CCF.histerese)).toMatchObject({ estado: "confiante", desde: 1030 + CCF.histerese, lutas: [1090, 1060, 1030, 1000] });
    const sai = tickSaidaFaixa(1090, cc.c)!;
    expect(cc.estado(sai + CCF.histerese - 1).estado).toBe("confiante");
    expect(cc.estado(sai + CCF.histerese).estado).toBe("neutro");
  });

  test("frases: marcador unico por estado, bebe so emote, neutro sem frase", () => {
    for (const [k, e] of Object.entries(CONFIANCA_TXT)) {
      for (const est of ["crianca", "adolescente", "adulto"] as const) expect(expressarConfianca(k as never, est)).toContain(e.marcador);
      expect(expressarConfianca(k as never, "bebe")).toBe(e.bebe);
      expect(expressarConfianca(k as never, "mega")).toBe(e.adulto);
    }
    expect(expressarConfianca("confiante", "adulto")).toBe("Tô confiante: ganhei as últimas.");
    expect(expressarConfianca("inseguro", "adulto")).toBe("Ando inseguro depois daquelas derrotas.");
    expect(expressarConfianca("entediado", "adulto")).toBe("De novo esse aí? Já sei tudo dele.");
    expect(expressarConfianca("neutro", "adulto")).toBeNull();
  });
});

describe("pets v5 com confianca", () => {
  const INI_ADOL = TICK_INICIAL + DUR_EVO.bebe + DUR_EVO.crianca;
  /** vive ate o Champion cuidando o basico, depois luta contra os rivais pedidos (30 min entre lutas) */
  function viverELutar(versao: number, rivais: string[]): Motor {
    const m = new Motor(515, versao);
    while (m.e.tick < INI_ADOL + 30) { m.avancar(15); if (m.e.fome < .5) m.observar("alimentar"); if (m.e.higiene < .5) m.observar("limpar"); }
    rivais.forEach((r, k) => { m.lutar(r, 7000 + k); m.avancar(30); });
    return m;
  }

  test("v5: conf existe, e recalculada no replay e entra na assinatura; v4 nao tem", () => {
    expect(new Motor(1, 4).conf).toBeNull();
    const m = viverELutar(5, ["aleatorio", "aleatorio", "agressivo", "aleatorio"]);
    expect(m.conf!.historico.length).toBe(4);
    const h = m.conf!.historico;
    expect(h[0].novidade).toBe(1); expect(h[2].novidade).toBe(1); expect(h[1].novidade).toBeLessThan(1); expect(h[3].novidade).toBeLessThan(h[1].novidade);
    expect(m.estadoConfianca()).not.toBeNull();
    const r = Motor.reproduzir(m.semente, m.log, 5);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.conf!.historico).toEqual(h);
    /* a experiencia de combate soma a novidade das vitorias (nao 1) */
    expect(m.vitoriasVida).toBeCloseTo(h.filter(x => x.sinal === 1).reduce((s, x) => s + x.novidade, 0), 12);
    /* a assinatura muda se a confianca mudar (ela esta dentro) */
    r.conf!.c += 1e-9;
    expect(r.assinatura()).not.toBe(m.assinatura());
  });

  test("v5: a inseguranca sobe o epsilon do lutador; a confianca positiva nao baixa", () => {
    const m = viverELutar(5, []);
    const base = lutadorPet(m, "x").estilo.eps;
    m.conf!.c = -1; m.conf!.tickC = m.e.tick;
    expect(lutadorPet(m, "x").estilo.eps).toBeCloseTo(base + CCF.kappaEps, 12);
    m.conf!.c = 1;
    expect(lutadorPet(m, "x").estilo.eps).toBeCloseTo(base, 12);
    /* v4: nada muda mesmo com a experiencia igual */
    const m4 = viverELutar(4, []);
    const b4 = lutadorPet(m4, "x").estilo.eps;
    expect(b4).toBeCloseTo(base, 12);
  });

  test("v5: repetir o rival ensina menos aos gambits (passo GA.alfa x novidade)", () => {
    const m = viverELutar(5, []);
    const g1 = Motor.reproduzir(m.semente, m.log, 5), g2 = Motor.reproduzir(m.semente, m.log, 5);
    /* mesma luta, mesmo estado: no g2 o rival ja foi visto muitas vezes (novidade baixa) */
    for (let k = 0; k < 6; k++) g2.conf!.registrar(g2.e.tick, "aleatorio", 0, 0);
    const n1 = { ...g1.gp!.notas }, n2 = { ...g2.gp!.notas };
    g1.lutar("aleatorio", 4321); g2.lutar("aleatorio", 4321);
    const d1 = Object.keys(n1).map(k => Math.abs(g1.gp!.notas[k] - n1[k])), d2 = Object.keys(n2).map(k => Math.abs(g2.gp!.notas[k] - n2[k]));
    const s1 = d1.reduce((a, b) => a + b, 0), s2 = d2.reduce((a, b) => a + b, 0);
    expect(s1).toBeGreaterThan(0);
    expect(s2).toBeLessThan(s1 * 0.2);
    expect(g2.conf!.historico.at(-1)!.novidade).toBeLessThan(0.1);
    expect(GA.alfa).toBe(0.2); expect(CLE.expPorVitoria).toBe(0.002);
  });
});
