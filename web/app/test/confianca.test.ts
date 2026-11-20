/* M1: confianca de combate e desgaste por rival repetido (docs/DESIGN_MVP_M1_CONFIANCA.md).
   Gate G2: motor/confianca.ts reproduz o gabarito do Python (experiments/exportar_gabarito_confianca.py) ate 1e-12,
   inclusive a frase de estado com histerese. E o pet de hoje (a v21, com a confianca desde o v8): a confianca conta por rival e entra na
   experiencia, tambem nas series (Cidadela, Liga, Fronteira). O epsilon do lutador e o passo dos gambits eram do combate por turnos e sairam
   com ele (LUTA_POC, LP4). */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { CCF, DUR_EVO, TICK_INICIAL, VERSAO_PET } from "../motor/constantes.ts";
import { ConfiancaCombate, atualizarConfianca, atualizarEncontros, epsilonConfianca, novidade, tickSaidaFaixa } from "../motor/confianca.ts";
import { CONFIANCA_TXT, expressarConfianca } from "../motor/expressao.ts";
import { LIGA, RIVAL_LIGA } from "../motor/liga.ts";
import { RIVAL_SALAO } from "../motor/salao.ts";
import { Motor, nomeRivalConfianca, rivalDaConfianca } from "../motor/motor.ts";
import { formaRivalInstalacao } from "../motor/instalacoes.ts";
import { nomeForma } from "../motor/nomes.ts";

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
    expect(atualizarConfianca(0, 0, -1, 1, 1)).toBeCloseTo(-CCF.eta * (1 - CCF.kSens), 12);
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

describe("pet v21 com confianca", () => {
  const INI_ADOL = TICK_INICIAL + DUR_EVO.bebe + DUR_EVO.crianca;
  /** vive ate o Champion cuidando o basico, depois luta na Arena contra as formas pedidas (o indice nos rivais do estagio; 30 min entre lutas) */
  function viverELutar(rivais: number[]): Motor {
    const m = new Motor(515);
    while (m.e.tick < INI_ADOL + 30) { m.avancar(15); if (m.e.fome < .5) m.observar("alimentar"); if (m.e.higiene < .5) m.observar("limpar"); }
    const rv = m.rivaisArenaPoc();
    rivais.forEach((r, k) => { m.lutarPoc(rv[r], 7000 + k, "campo"); if (m.lesionadoDesde !== null) m.observar("tratar_lesao"); m.avancar(30); });
    return m;
  }

  test("v21: conf existe, e recalculada no replay e entra na assinatura", () => {
    expect(new Motor(1).conf).not.toBeNull();   /* os ovos novos herdam a confianca */
    const m = viverELutar([0, 0, 1, 0]);
    expect(m.conf!.historico.length).toBe(4);
    const h = m.conf!.historico;
    expect(h[0].novidade).toBe(1); expect(h[2].novidade).toBe(1); expect(h[1].novidade).toBeLessThan(1); expect(h[3].novidade).toBeLessThan(h[1].novidade);
    expect(m.estadoConfianca()).not.toBeNull();
    const r = Motor.reproduzir(m.semente, m.log, VERSAO_PET);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.conf!.historico).toEqual(h);
    /* a experiencia de combate soma a novidade das vitorias (nao 1) */
    expect(m.vitoriasVida).toBeCloseTo(h.filter(x => x.sinal === 1).reduce((s, x) => s + x.novidade, 0), 12);
    /* a assinatura muda se a confianca mudar (ela esta dentro) */
    r.conf!.c += 1e-9;
    expect(r.assinatura()).not.toBe(m.assinatura());
  });

  /** um Rookie que conhece as 6 medalhas (a Liga e, com o titulo, a Fronteira valem do Rookie em diante) */
  function rookie(semente = 8008): Motor {
    const m = new Motor(semente);
    m.liberar(6);
    while (m.estagioAtual === "bebe") m.avancar(30);
    return m;
  }
  test("v21: nas series (Liga, Salao, instalacao) cada luta conta, com o rival dela; o replay da o mesmo pet", () => {
    const m = rookie(), sLiga = 90210;
    const liga = m.lutarPoc(RIVAL_LIGA, sLiga, null).serie.length;
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    const h = m.conf!.historico;
    expect(h).toHaveLength(liga);
    expect(h.map(x => x.rival)).toEqual(LIGA.slice(0, liga).map(x => "liga:" + x.lider));
    expect(h.every(x => x.novidade === 1)).toBe(true);                     /* seis rivais diferentes, todos novos */
    expect(m.confEvento).toEqual(Array(liga).fill(0));
    expect(nomeRivalConfianca(h[0].rival)).toMatch(/ de Gazimon$/);
    m.abrirFronteira();
    m.avancar(30);
    const sSalao = m.sementeSalao(), est = m.estagioAtual;
    m.lutarPoc(RIVAL_SALAO, sSalao, null);
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    expect(m.conf!.historico.at(-1)!.rival).toBe(rivalDaConfianca(RIVAL_SALAO, sSalao, 0, est));
    expect(m.conf!.historico.at(-1)!.rival).toMatch(/^forma:/);
    m.avancar(30);
    const sInst = m.sementeInstalacao("torre_batalha"), n0 = m.conf!.historico.length;
    const nInst = m.lutarPoc("torre_batalha", sInst, null).serie.length;
    const hi = m.conf!.historico.slice(n0);
    expect(hi).toHaveLength(nInst);
    hi.forEach((x, k) => {
      expect(x.rival).toBe(rivalDaConfianca("torre_batalha", sInst, k, est));
      expect(nomeRivalConfianca(x.rival)).toContain(nomeForma(formaRivalInstalacao(sInst, k)));
    });
    expect(m.confEvento.slice(n0)).toEqual(Array(nInst).fill(2));
    const r = Motor.reproduzir(m.semente, m.log, VERSAO_PET);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.confEvento).toEqual(m.confEvento);
    expect(m.vitoriasVida).toBeCloseTo(m.conf!.historico.filter(x => x.sinal === 1).reduce((a, x) => a + x.novidade, 0), 12);
  });
  test("v21: as lutas seguidas da Cidadela sao o mesmo rival repetido (a novidade cai dentro da serie)", () => {
    const c = new ConfiancaCombate();
    const rs = [0, 1, 2].map(k => rivalDaConfianca("npc_v5_myotismon", 5, k, "adulto"));
    expect(new Set(rs)).toEqual(new Set(["npc_v5_myotismon"]));
    const nov = rs.map(r => c.registrar(1000, r, 1, 0).novidade);
    expect(nov[0]).toBe(1); expect(nov[1]).toBeLessThan(1); expect(nov[2]).toBeLessThan(nov[1]);
  });
});
