/* As chaves do produto do pet do jogo, o v13 (docs/TAREFA_V2_PRODUTO_FOME.md): o chamado de fome do bebe pela fome do corpo (a), e a decisao do pet
   logo depois de o dono por a racao no chao (b). Ligadas no jogo (src/produto.ts, o evento "p" no comeco do registro dos ovos novos) e
   desligadas na pesquisa: sem o evento, a vida e a de hoje (os gabaritos v13_vidas_ts, v12_jogo_ts, mvp_produto_python e mvp_mundo_python conferem).
     - (a) o caso do Gerente (2026-10-29): a racao vista a 4 celulas, a fome em 0,675 e o chamado "fome" aberto pelo relogio. Com a chave,
       o chamado so abre quando a fome do corpo pede (abaixo de CHAMADO_FOME_CORPO.limiar, o fome_moderada do instinto), e fecha quando
       o dono alimenta, quando o pet come e a fome volta ao limiar, ou quando a janela passa;
     - (b) o pet decidia so no fim do intervalo de 15 min; com a chave, decide ja no proximo passo depois da racao, e o pet com fome vai
       ate ela. O cerebro A e a politica nao mudam: so o momento da decisao.
   O G-PAR da chave (b) contra o Python fica em test/decisao_na_comida.test.ts. */
import { describe, expect, test } from "vitest";
import { CHAMADO_BEBE, CHAMADO_FOME_CORPO, C, TICK_INICIAL } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import type { ChavesProduto, EventoRegistro } from "../motor/tipos.ts";
import { readFileSync } from "node:fs";
import { ligarProduto } from "../src/produto.ts";
import { textoEfeito } from "./medir_chamado_fome.ts";

const LIM = CHAMADO_FOME_CORPO.limiar;
const SO_A = { chamadoPelaFome: true, decisaoNaComida: false }, SO_B = { chamadoPelaFome: false, decisaoNaComida: true };
const AMBAS = { chamadoPelaFome: true, decisaoNaComida: true };
const JOGO = { ...AMBAS, chamadosPeloCorpo: true }, DESLIGADAS = { chamadoPelaFome: false, decisaoNaComida: false, chamadosPeloCorpo: false };

function pet(semente: number, chaves: ChavesProduto | null, classica = false): Motor {
  const m = new Motor(semente);
  if (classica) m.configurar("classica");
  if (chaves) m.ligarProduto(chaves);
  return m;
}
const fomeAberto = (m: Motor) => m.chamadosAbertos().includes("fome");
/** a racao a dx subunidades do pet, para dentro do mapa */
function racaoPerto(m: Motor, dx: number): [number, number] {
  const [x, y] = m.mundo!.pet, rx = x + dx < 1024 ? x + dx : x - dx;
  m.deixarComida("racao", rx, y);
  return [rx, y];
}
/** o dono brinca nos primeiros n x 10 min (o brincar gasta fome: a do bebe cai abaixo do limiar dentro do estagio) */
function brincarCedo(m: Motor, n: number, ate: number, todo: (t: number) => void = () => {}): void {
  for (let t = 1; t <= ate; t++) {
    m.avancar(1);
    if (t <= n * 10 && t % 10 === 0) m.observar("brincar");
    todo(t);
  }
}

describe("(a) o chamado de fome do bebe pela fome do corpo", () => {
  test("o caso: a racao vista, o pet saciado e o chamado de fome aberto pelo relogio; com a chave, nenhum chamado de fome", () => {
    const hoje = pet(101, null), chave = pet(101, SO_A);
    hoje.avancar(30); chave.avancar(30);
    /* o relogio abre o chamado de fome aos 30 min, com a fome bem acima do limiar */
    expect(fomeAberto(hoje)).toBe(true);
    expect(hoje.e.fome).toBeGreaterThan(.7);
    expect(fomeAberto(chave)).toBe(false);
    /* a racao a 4 celulas: o mundo a ve (o raio de visao), nos dois */
    for (const m of [hoje, chave]) {
      racaoPerto(m, 64);
      expect(m.mundo!.perceber(m.e.tick).vistos.map(v => v[1])).toContain("racao");
    }
    /* o bebe inteiro sem brincadeira: a fome nunca chega ao limiar, e a chave nunca abre o de fome (o de hoje abre pelo relogio) */
    let abriuHoje = 0, abriuChave = 0;
    for (let t = 31; t < hoje.dur.bebe; t++) {
      hoje.avancar(1); chave.avancar(1);
      if (fomeAberto(hoje)) abriuHoje++;
      if (fomeAberto(chave)) abriuChave++;
      expect(chave.e.fome).toBeGreaterThanOrEqual(LIM);
    }
    expect(abriuHoje).toBeGreaterThan(0);
    expect(abriuChave).toBe(0);
    /* a fome do bebe sem cuidado: nasce em 0,80 e chega a ~0,65 no fim dos 180 min (por isso o chamado quase nao abre no bebe) */
    expect(chave.e.fome).toBeGreaterThan(.6);
    expect(chave.e.fome).toBeLessThan(.7);
    /* a chave so mexe no chamado: a vida do pet (o estado, o mundo e o cerebro) e a mesma */
    expect(chave.e).toEqual(hoje.e);
    expect(JSON.stringify(chave.mundo!.resumo())).toBe(JSON.stringify(hoje.mundo!.resumo()));
    expect(JSON.stringify(chave.cerebro!.estadoInterno())).toBe(JSON.stringify(hoje.cerebro!.estadoInterno()));
  });

  test("com a chave, o chamado so fica aberto com a fome abaixo do limiar, abre na primeira vez que ela cai e no maximo um a cada 30 min", () => {
    for (const s of [101, 202, 303]) {
      const m = pet(s, SO_A), aberturas: number[] = [];
      let antes = false, primeiraAbaixo: number | null = null;
      brincarCedo(m, 6, m.dur.bebe - 1, (t) => {
        const ab = fomeAberto(m);
        if (ab) expect(m.e.fome, `semente ${s}, t ${t}`).toBeLessThan(LIM);
        if (primeiraAbaixo === null && m.e.fome < LIM) primeiraAbaixo = t;
        if (ab && !antes) aberturas.push(t);
        antes = ab;
      });
      expect(aberturas.length, `semente ${s}`).toBeGreaterThanOrEqual(2);
      expect(aberturas[0]).toBe(primeiraAbaixo);
      for (let i = 1; i < aberturas.length; i++) expect(aberturas[i] - aberturas[i - 1]).toBeGreaterThanOrEqual(CHAMADO_BEBE.fome);
    }
  });

  test("fecha como atendido quando o dono deixa a racao, e quando o pet come a racao do chao e a fome volta ao limiar", () => {
    /* o dono atende: a racao com o chamado aberto */
    const m = pet(101, SO_A);
    brincarCedo(m, 6, 100);
    while (!fomeAberto(m)) m.avancar(1);
    const at = m.chamados.atendidos;
    racaoPerto(m, 16);
    expect(fomeAberto(m)).toBe(false);
    expect(m.chamados.atendidos).toBe(at + 1);
    /* o pet come a racao que ja estava no chao, com o chamado aberto (o ritmo classico, o bebe de 6 h; achado por varredura) */
    const r = pet(101, SO_A, true);
    let fechou: { t: number; fome: number } | null = null, antes = false, atendidos = 0;
    brincarCedo(r, 3, r.dur.bebe - 1, (t) => {
      if (t === 109) { expect(fomeAberto(r)).toBe(false); racaoPerto(r, 16); }
      const ab = fomeAberto(r);
      /* fechou sem acao do dono neste tick (o brincar e so ate os 30 min), contando como atendido */
      if (fechou === null && antes && !ab && t > 109 && r.chamados.atendidos === atendidos + 1) fechou = { t, fome: r.e.fome };
      antes = ab; atendidos = r.chamados.atendidos;
    });
    expect(fechou).not.toBeNull();
    expect(fechou!.fome).toBeGreaterThanOrEqual(LIM);
    expect(r.mundo!.consumos.length).toBeGreaterThan(0);
  });
});

describe("o efeito no bebe (test/efeito_chamado_fome.json, de test/medir_chamado_fome.ts)", () => {
  test("o arquivo esta em dia, e o efeito e o relatado: os chamados de fome que abrem e a fracao de cuidado conforme o dono", () => {
    const texto = textoEfeito();
    expect(readFileSync(new URL("./efeito_chamado_fome.json", import.meta.url), "utf8")).toBe(texto);
    type Linha = { ritmo: string; dono: string; chave: boolean; chamados_abertos: Record<string, number>; cuidado: number; ramo: string;
      fome_ao_abrir: number[] };
    const vidas = (JSON.parse(texto) as { vidas: Linha[] }).vidas;
    const de = (ritmo: string, dono: string, chave: boolean) => vidas.filter(v => v.ritmo === ritmo && v.dono === dono && v.chave === chave);
    for (const ritmo of ["rapida", "classica"]) {
      /* hoje, o relogio abre 5 (rapido) ou 11 (classico) de fome, todos com a fome acima do limiar */
      for (const v of de(ritmo, "nada", false)) {
        expect(v.chamados_abertos.fome).toBe(ritmo === "rapida" ? 5 : 11);
        expect(Math.min(...v.fome_ao_abrir)).toBeGreaterThan(LIM);
      }
      /* com a chave, so abre com a fome abaixo do limiar: nenhum sem o brincar do dono */
      for (const d of ["nada", "atende", "atende_10min", "so_alimenta", "nao_alimenta"])
        for (const v of de(ritmo, d, true)) expect(v.chamados_abertos.fome).toBe(0);
      /* quem so alimenta perde o cuidado; quem nunca alimenta (e atende o resto) vira sereno */
      for (const v of de(ritmo, "so_alimenta", true)) expect([v.cuidado, v.ramo]).toEqual([0, "arisco"]);
      for (const v of de(ritmo, "nao_alimenta", true)) expect([v.cuidado, v.ramo]).toEqual([1, "sereno"]);
      for (const v of de(ritmo, "nao_alimenta", false)) expect(v.ramo).toBe("arisco");
    }
    for (const v of vidas.filter(v => v.chave)) expect(v.fome_ao_abrir.every(f => f < LIM)).toBe(true);
    /* so o classico com brincadeira chega a abrir o de fome com a chave */
    for (const v of de("classica", "brinca_atende", true)) expect(v.chamados_abertos.fome).toBeGreaterThan(0);
    for (const v of de("rapida", "brinca_atende", true)) expect(v.chamados_abertos.fome).toBe(0);
  });
});

describe("o mesmo descompasso na higiene e no carinho (so relatado; a tarefa nao os muda)", () => {
  test("pelo relogio, o chamado de higiene abre com o pet limpo e o de carinho com o humor alto", () => {
    const vistos: Record<string, number[]> = { higiene: [], carinho: [] };
    for (const s of [101, 202, 303]) for (const ch of [null, AMBAS]) {
      const m = pet(s, ch);
      let antes: string[] = [];
      for (let t = 1; t < m.dur.bebe; t++) {
        m.avancar(1);
        const ab = m.chamadosAbertos();
        for (const c of ab) if (!antes.includes(c) && c !== "fome") {
          vistos[c].push(c === "higiene" ? m.e.higiene : m.e.humor);
          if (c === "higiene") expect(m.e.sujeira).toBe(0);
        }
        antes = ab;
      }
    }
    /* as mesmas aberturas com e sem as chaves do produto (elas nao mexem na higiene nem no carinho) */
    expect(vistos.higiene.length).toBe(12);
    expect(vistos.carinho.length).toBe(18);
    expect(Math.min(...vistos.higiene)).toBeGreaterThan(.9);
    expect(Math.min(...vistos.carinho)).toBeGreaterThan(.6);
  });
});

describe("(b) a decisao do pet logo depois da racao no chao", () => {
  test("no meio do intervalo: com a chave, a decisao vem no proximo passo; sem ela, so no fim do intervalo; o intervalo recomeca dali", () => {
    for (const s of [101, 202, 303]) {
      const hoje = pet(s, null), chave = pet(s, SO_B);
      hoje.avancar(37); chave.avancar(37);                  // 37 min: 7 depois de uma decisao (a cada 15)
      for (const m of [hoje, chave]) racaoPerto(m, 64);
      const n0 = hoje.nDecisoes;
      expect(chave.nDecisoes).toBe(n0);
      hoje.avancar(1); chave.avancar(1);
      expect(chave.nDecisoes).toBe(n0 + 1);
      expect(hoje.nDecisoes).toBe(n0);
      /* depois dela, o intervalo de 15 conta dali */
      let k = 0;
      while (chave.nDecisoes === n0 + 1) { chave.avancar(1); k++; }
      expect(k).toBe(C.intervalo);
    }
  });

  test("o pet com fome e acordado vai ate a racao ja no proximo passo (sem a chave, espera o fim do intervalo)", () => {
    for (const s of [101, 202, 303, 505]) {
      const chave = pet(s, SO_B), hoje = pet(s, null);
      /* o dono so faz carinho, ate a fome passar do limiar com o pet acordado, no meio de um intervalo */
      let t = 0;
      for (;;) {
        chave.avancar(1); hoje.avancar(1); t++;
        if (t % 45 === 0) { chave.observar("acariciar"); hoje.observar("acariciar"); }
        const e = chave.e;
        if (e.fome < LIM - .01 && !e.dormindo && e.energia > .5 && e.tick % C.intervalo === 7) break;
        if (t > 2000) throw new Error("nao achou o pet com fome acordado");
      }
      expect(chave.e).toEqual(hoje.e);
      const [rx, ry] = racaoPerto(chave, 64); racaoPerto(hoje, 64);
      const d0 = Math.abs(chave.mundo!.pet[0] - rx) + Math.abs(chave.mundo!.pet[1] - ry), n0 = chave.nDecisoes;
      chave.avancar(1); hoje.avancar(1);
      expect(chave.nDecisoes).toBe(n0 + 1);
      expect(hoje.nDecisoes).toBe(n0);
      /* comeu ja nesta decisao ou na seguinte (o A as vezes chama atencao antes): o pet andou ate a racao */
      for (let k = 0; k < C.intervalo && chave.mundo!.consumos.length === 0; k++) chave.avancar(1);
      expect(chave.mundo!.consumos.length, `semente ${s}`).toBeGreaterThan(0);
      const [px, py] = chave.mundo!.pet;
      expect(Math.abs(px - rx) + Math.abs(py - ry)).toBeLessThan(d0);
      expect(chave.e.fome).toBeGreaterThan(LIM);
    }
  });
});

describe("as chaves no registro: o evento \"p\"", () => {
  test("o jogo grava as chaves no comeco do registro dos ovos novos, e o replay as le de la", () => {
    const m = ligarProduto(new Motor(101));
    expect(m.log).toEqual([[TICK_INICIAL, "p", JOGO]]);
    expect(m.produto).toEqual(JOGO);
    brincarCedo(m, 6, 120, (t) => { if (t === 77) racaoPerto(m, 32); });
    const r = Motor.reproduzir(101, m.log);
    expect(r.produto).toEqual(JOGO);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(JSON.stringify(r.chamados)).toBe(JSON.stringify(m.chamados));
    /* sem o evento (um save de antes), as duas desligadas e outra vida */
    const semP = Motor.reproduzir(101, m.log.slice(1).map(ev => [ev[0], ev[1], ev[2]] as EventoRegistro));
    expect(semP.produto).toEqual(DESLIGADAS);
    expect(semP.assinatura()).not.toBe(m.assinatura());
    /* o ritmo antes das chaves (o brasao), e a origem do filho antes delas */
    const cl = new Motor(202); cl.configurar("classica"); ligarProduto(cl);
    expect(cl.log.map(ev => ev[1])).toEqual(["c", "p"]);
  });

  test("o evento invalido falha alto: fora do comeco, duas vezes, malformado", () => {
    const t = TICK_INICIAL;
    const duas = new Motor(1); duas.ligarProduto(AMBAS);
    expect(() => duas.ligarProduto(SO_A)).toThrow(/uma vez/);
    const tarde = new Motor(1); tarde.avancar(1);
    expect(() => tarde.ligarProduto(AMBAS)).toThrow(/começo/);
    const dono = new Motor(1); dono.observar("acariciar");
    expect(() => dono.ligarProduto(AMBAS)).toThrow(/começo/);
    for (const ruim of [null, {}, { chamadoPelaFome: true }, { chamadoPelaFome: 1, decisaoNaComida: true },
      { chamadoPelaFome: true, decisaoNaComida: true, outra: true }])
      expect(() => Motor.reproduzir(1, [[t, "p", ruim]] as unknown as EventoRegistro[]), JSON.stringify(ruim)).toThrow(/inválidas/);
    expect(() => Motor.reproduzir(1, [[t, "p", AMBAS], [t, "p", AMBAS]])).toThrow(/uma vez/);
    /* o "p" depois de outro evento que nao seja o ritmo ou a origem */
    expect(() => Motor.reproduzir(1, [[t, "t", 1], [t + 1, "p", AMBAS]])).toThrow(/começo/);
    /* sem o evento, as duas desligadas */
    expect(new Motor(1).produto).toEqual(DESLIGADAS);
  });
});
