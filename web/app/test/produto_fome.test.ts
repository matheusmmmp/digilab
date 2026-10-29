/* As chaves do produto do pet v12 (docs/TAREFA_V2_PRODUTO_FOME.md): o chamado de fome do bebe pela fome do corpo (a), e a decisao do pet
   logo depois de o dono por a racao no chao (b). Ligadas no jogo (src/produto.ts, o evento "p" no comeco do registro dos ovos novos) e
   desligadas na pesquisa: sem o evento, a vida e a de hoje (os gabaritos v12_jogo_ts, mvp_produto_python e mvp_mundo_python conferem).
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
import { ligarProduto } from "../src/produto.ts";

const LIM = CHAMADO_FOME_CORPO.limiar;
const SO_A = { chamadoPelaFome: true, decisaoNaComida: false }, SO_B = { chamadoPelaFome: false, decisaoNaComida: true };
const AMBAS = { chamadoPelaFome: true, decisaoNaComida: true };

function pet(semente: number, chaves: ChavesProduto | null, classica = false): Motor {
  const m = new Motor(semente, 12);
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
    const m = ligarProduto(new Motor(101, 12));
    expect(m.log).toEqual([[TICK_INICIAL, "p", AMBAS]]);
    expect(m.produto).toEqual(AMBAS);
    brincarCedo(m, 6, 120, (t) => { if (t === 77) racaoPerto(m, 32); });
    const r = Motor.reproduzir(101, m.log, 12);
    expect(r.produto).toEqual(AMBAS);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(JSON.stringify(r.chamados)).toBe(JSON.stringify(m.chamados));
    /* sem o evento (um save de antes), as duas desligadas e outra vida */
    const semP = Motor.reproduzir(101, m.log.slice(1).map(ev => [ev[0], ev[1], ev[2]] as EventoRegistro), 12);
    expect(semP.produto).toEqual({ chamadoPelaFome: false, decisaoNaComida: false });
    expect(semP.assinatura()).not.toBe(m.assinatura());
    /* o ritmo antes das chaves (o brasao), e a origem do filho antes delas */
    const cl = new Motor(202, 12); cl.configurar("classica"); ligarProduto(cl);
    expect(cl.log.map(ev => ev[1])).toEqual(["c", "p"]);
  });

  test("o evento invalido falha alto: fora do comeco, duas vezes, num pet anterior ao v12, malformado", () => {
    const t = TICK_INICIAL;
    expect(() => new Motor(1, 11).ligarProduto(AMBAS)).toThrow(/v12/);
    const duas = new Motor(1, 12); duas.ligarProduto(AMBAS);
    expect(() => duas.ligarProduto(SO_A)).toThrow(/uma vez/);
    const tarde = new Motor(1, 12); tarde.avancar(1);
    expect(() => tarde.ligarProduto(AMBAS)).toThrow(/começo/);
    const dono = new Motor(1, 12); dono.observar("acariciar");
    expect(() => dono.ligarProduto(AMBAS)).toThrow(/começo/);
    for (const ruim of [null, {}, { chamadoPelaFome: true }, { chamadoPelaFome: 1, decisaoNaComida: true },
      { chamadoPelaFome: true, decisaoNaComida: true, outra: true }])
      expect(() => Motor.reproduzir(1, [[t, "p", ruim]] as unknown as EventoRegistro[], 12), JSON.stringify(ruim)).toThrow(/inválidas/);
    expect(() => Motor.reproduzir(1, [[t, "p", AMBAS], [t, "p", AMBAS]], 12)).toThrow(/uma vez/);
    /* o "p" depois de outro evento que nao seja o ritmo ou a origem */
    expect(() => Motor.reproduzir(1, [[t, "t", 1], [t + 1, "p", AMBAS]], 12)).toThrow(/começo/);
    /* a chave no laco so com o mundo do v12 */
    expect(new Motor(1, 11).produto).toEqual({ chamadoPelaFome: false, decisaoNaComida: false });
  });
});
