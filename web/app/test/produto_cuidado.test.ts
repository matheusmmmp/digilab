/* A chave chamadosPeloCorpo (docs/TAREFA_V2_PRODUTO_CUIDADO.md; a opcao (C) do Matheus de 2026-10-30): os tres chamados do bebe abrem
   pelo corpo, com os limiares do bebe (CHAMADO_BEBE_CORPO: a fome abaixo de 0,7, a higiene abaixo de 0,9 e o humor abaixo de 0,8, no de
   carinho), e nao pelo relogio. O alimentar ou a racao posta atendem o de fome: a comida conta no cuidado do bebe. Os intervalos de
   30/60/45 min e a janela de 15 ficam como hoje. A chave vem no evento "p" dos ovos novos; o evento de 2026-10-29, sem ela, e os saves sem
   o evento seguem como estavam (os testes do test/produto_fome.test.ts e o gabarito v13_vidas_ts conferem). O corpo, o cerebro e o Python
   nao mudam. */
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { ACAO_CHAMADO, CAT, CHAMADO_BEBE, CHAMADO_BEBE_CORPO, TICK_INICIAL } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import type { Chamado, ChavesProduto, EventoRegistro } from "../motor/tipos.ts";
import { textoEfeitoBebe } from "./medir_chamados_bebe.ts";

const FOME = { chamadoPelaFome: true, decisaoNaComida: true };
const CORPO = { ...FOME, chamadosPeloCorpo: true };
const TIPOS = Object.keys(CHAMADO_BEBE) as Chamado[];

function pet(semente: number, chaves: ChavesProduto | null, classica = false): Motor {
  const m = new Motor(semente);
  if (classica) m.configurar("classica");
  if (chaves) m.ligarProduto(chaves);
  return m;
}
const valorDo = (m: Motor, tipo: Chamado): number => (tipo === "fome" ? m.e.fome : tipo === "higiene" ? m.e.higiene : m.e.humor);

describe("os chamados do bebe pelo corpo", () => {
  test("cada chamado so abre com o corpo abaixo do limiar do bebe, na primeira vez que ele cai, e no maximo um por intervalo", () => {
    for (const classica of [false, true]) for (const s of [101, 202, 303]) {
      const m = pet(s, CORPO, classica), visto: Partial<Record<Chamado, number>> = {}, aberturas: Record<string, number[]> = {};
      const primeiraAbaixo: Partial<Record<Chamado, number>> = {};
      while (m.estagioAtual === "bebe") {
        m.avancar(1);
        if (m.estagioAtual !== "bebe") break;
        for (const tipo of TIPOS) {
          if (primeiraAbaixo[tipo] === undefined && valorDo(m, tipo) < CHAMADO_BEBE_CORPO[tipo]) primeiraAbaixo[tipo] = m.e.tick;
          const ab = m.chamados.abertos[tipo];
          if (ab !== undefined && visto[tipo] !== ab) {
            visto[tipo] = ab; (aberturas[tipo] ??= []).push(ab);
            expect(ab).toBe(m.e.tick);
            expect(valorDo(m, tipo), `${tipo} ${s}`).toBeLessThan(CHAMADO_BEBE_CORPO[tipo]);
          }
        }
      }
      for (const tipo of TIPOS) {
        const a = aberturas[tipo] ?? [];
        /* o bebe sem cuidado chama de tudo: a fome e a higiene caem abaixo do limiar no estagio, e o humor comeca abaixo */
        expect(a.length, `${tipo} ${s} ${classica}`).toBeGreaterThan(0);
        expect(a[0]).toBe(primeiraAbaixo[tipo]);
        for (let i = 1; i < a.length; i++) expect(a[i] - a[i - 1]).toBeGreaterThanOrEqual(CHAMADO_BEBE[tipo]);
      }
    }
  });

  test("a acao do dono atende; a racao posta atende o de fome; a janela que passa conta como perdido", () => {
    for (const tipo of TIPOS) {
      const m = pet(202, CORPO);
      while (!(tipo in m.chamados.abertos)) m.avancar(1);
      const { atendidos, total } = m.chamados;
      m.observar(ACAO_CHAMADO[tipo][0]);
      expect(tipo in m.chamados.abertos).toBe(false);
      expect(m.chamados.atendidos).toBe(atendidos + 1);
      expect(m.chamados.total).toBe(total + 1);
    }
    /* a racao posta no chao, longe do comedouro, atende o de fome */
    const r = pet(101, CORPO);
    while (!("fome" in r.chamados.abertos)) r.avancar(1);
    const [x, y] = r.mundo!.pet, a0 = r.chamados.atendidos;
    r.deixarComida("racao", x < 512 ? x + 32 : x - 32, y);
    expect("fome" in r.chamados.abertos).toBe(false);
    expect(r.chamados.atendidos).toBe(a0 + 1);
    /* sem o dono, o chamado aberto vira perdido quando a janela passa (o humor que sobe sozinho nao o fecha) */
    const p = pet(303, CORPO);
    while (!("carinho" in p.chamados.abertos)) p.avancar(1);
    const abriu = p.chamados.abertos.carinho!, { atendidos, total } = p.chamados;
    while (p.e.tick - abriu <= CAT.janelaChamado) p.avancar(1);
    expect("carinho" in p.chamados.abertos).toBe(false);
    expect(p.chamados.atendidos).toBe(atendidos);
    expect(p.chamados.total).toBeGreaterThan(total);
  });

  test("a chave so mexe nos chamados: o estado, o mundo e o cerebro saem iguais aos de sem ela", () => {
    for (const s of [101, 202]) {
      const corpo = pet(s, CORPO), fome = pet(s, FOME);
      for (let t = 1; t < corpo.dur.bebe; t++) {
        corpo.avancar(1); fome.avancar(1);
        if (t % 50 === 0) { corpo.observar("limpar"); fome.observar("limpar"); }
      }
      expect(corpo.e).toEqual(fome.e);
      expect(JSON.stringify(corpo.mundo!.resumo())).toBe(JSON.stringify(fome.mundo!.resumo()));
      expect(JSON.stringify(corpo.cerebro!.estadoInterno())).toBe(JSON.stringify(fome.cerebro!.estadoInterno()));
      expect(JSON.stringify(corpo.chamados)).not.toBe(JSON.stringify(fome.chamados));
    }
  });

  test("o evento: as tres chaves no replay; o evento de 2026-10-29, sem a terceira, a deixa desligada", () => {
    const m = pet(101, CORPO);
    expect(m.log).toEqual([[TICK_INICIAL, "p", CORPO]]);
    for (let t = 1; t <= 90; t++) { m.avancar(1); if (t % 20 === 0) m.observar("acariciar"); }
    const r = Motor.reproduzir(101, m.log);
    expect(r.produto).toEqual(CORPO);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(JSON.stringify(r.chamados)).toBe(JSON.stringify(m.chamados));
    const velho = Motor.reproduzir(101, [[TICK_INICIAL, "p", FOME], ...m.log.slice(1)] as EventoRegistro[]);
    expect(velho.produto).toEqual({ ...FOME, chamadosPeloCorpo: false });
    expect(JSON.stringify(velho.chamados)).not.toBe(JSON.stringify(m.chamados));
    expect(() => Motor.reproduzir(1, [[TICK_INICIAL, "p", { ...CORPO, chamadosPeloCorpo: 1 }]] as unknown as EventoRegistro[]))
      .toThrow(/inválidas/);
    expect(() => Motor.reproduzir(1, [[TICK_INICIAL, "p", { chamadosPeloCorpo: true, decisaoNaComida: true }]] as unknown as EventoRegistro[]))
      .toThrow(/inválidas/);
  });
});

describe("o achado: o bebe nao come a racao do dono", () => {
  test("o dono que atende todo chamado deixa racao a cada chamado de fome, e ela fica no mundo: a fome do bebe nao sobe", () => {
    for (const [classica, n] of [[false, 2], [true, 8]] as const) for (const s of [101, 202]) {
      const m = pet(s, CORPO, classica), visto: Partial<Record<Chamado, number>> = {};
      let fomeAntes = m.e.fome, subiu = 0;
      while (m.estagioAtual === "bebe") {
        m.avancar(1);
        if (m.estagioAtual !== "bebe") break;
        if (m.e.fome > fomeAntes) subiu++;
        fomeAntes = m.e.fome;
        for (const tipo of TIPOS) {
          const ab = m.chamados.abertos[tipo];
          if (ab !== undefined && visto[tipo] !== ab) { visto[tipo] = ab; m.observar(ACAO_CHAMADO[tipo][0]); }
        }
      }
      /* o pet so come abaixo do 0,45 do instinto (lobos.ts, agirInstinto), e a fome do bebe fica acima dele no estagio */
      expect(subiu).toBe(0);
      expect(m.mundo!.comidas.size, `semente ${s}`).toBe(n);
      expect(m.evolucoes[0]).toMatchObject({ ramo: "sereno", cuidado: 1 });
    }
  });
});

describe("o efeito no bebe (test/medir_chamados_bebe.ts)", () => {
  test("o arquivo gravado esta em dia", () => {
    expect(readFileSync(new URL("./efeito_chamados_bebe.json", import.meta.url), "utf8")).toBe(textoEfeitoBebe());
  });

  test("com as tres chaves: quem nao faz nada sai arisco, quem atende tudo sai sereno, e a comida conta no cuidado", () => {
    const { vidas } = JSON.parse(readFileSync(new URL("./efeito_chamados_bebe.json", import.meta.url), "utf8")) as {
      vidas: { ritmo: string; dono: string; chaves: string; semente: number; cuidado: number; ramo: string }[] };
    const de = (dono: string, chaves: string) => vidas.filter(v => v.dono === dono && v.chaves === chaves);
    expect(vidas.length).toBe(2 * 6 * 3 * 3);
    for (const v of de("nada", "corpo")) { expect(v.cuidado).toBe(0); expect(v.ramo).toBe("arisco"); }
    for (const dono of ["atende", "atende_10min", "brinca_atende"]) for (const v of de(dono, "corpo")) {
      expect(v.cuidado).toBe(1); expect(v.ramo).toBe("sereno");
    }
    /* quem nunca alimenta ja nao sai sereno (com as duas chaves de 2026-10-29, saia); quem so alimenta ja nao cai a 0 */
    for (const v of de("nao_alimenta", "fome")) expect(v.ramo).toBe("sereno");
    for (const v of de("nao_alimenta", "corpo")) { expect(v.ramo).toBe("arisco"); expect(v.cuidado).toBeLessThan(CAT.limiarCuidado); }
    for (const v of de("so_alimenta", "corpo")) { expect(v.ramo).toBe("arisco"); expect(v.cuidado).toBeGreaterThan(0); }
  });
});
