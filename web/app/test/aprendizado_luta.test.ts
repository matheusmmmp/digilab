// O painel "O que o pet aprendeu" (src/aprendizadoLuta.ts): so leitura do GambitsPet. Aqui: as linhas (nota, usos, estado), o que subiu
// ou desceu contra a lista de partida (so v14), a troca da pior regra, as travas e os vetos, e que ler nao muda o pet (assinatura igual).
import { describe, expect, test } from "vitest";
import { passoDe, tipoMudanca, visaoAprendizado } from "../src/aprendizadoLuta.ts";
import { APRENDIZADO_V14 } from "../motor/combate_tr/constantes_tr.ts";
import { CRIANCA_V21, GA, GambitsPet, CV21E_TR, sementeDe, type Forma } from "../motor/index.ts";

const forma = (): Forma => ({ esp: "brasa", est: "crianca", ramo: Object.keys(CRIANCA_V21)[0] as Forma["ramo"] });
function pet(v14: boolean): GambitsPet {
  const gp = new GambitsPet(), f = forma();
  if (v14) gp.aprendizadoTR = APRENDIZADO_V14;
  gp.semear(f, "teste", CV21E_TR, sementeDe(f, CV21E_TR));
  return gp;
}

describe("visaoAprendizado", () => {
  test("pet novo: uma linha por regra ativa, sem lutas, com a mudanca de semeadura", () => {
    const gp = pet(false), v = visaoAprendizado(gp);
    expect(v.nLutas).toBe(0);
    expect(v.linhas.map(l => l.k)).toEqual(gp.ativas);
    expect(v.linhas.every(l => l.disparos === 0 && l.estado === "livre" && l.delta === null)).toBe(true);
    expect(v.mudancas).toHaveLength(1);
    expect(v.mudancas[0].tipo).toBe("evolucao");
    expect(v.passo).toEqual({ alfa: GA.alfa, limiar: GA.limiarTroca, bonus: GA.bonusResultado, eps: expect.any(Number) });
  });
  test("pets v14: o passo vem do aprendizado do tempo real e o delta e contra a lista de partida", () => {
    const gp = pet(true), v = visaoAprendizado(gp);
    expect(passoDe(gp).limiar).toBe(APRENDIZADO_V14!.limiar);
    expect(v.linhas.every(l => typeof l.delta === "number")).toBe(true);
    const k = gp.ativas[gp.ativas.length - 1];
    gp.notas[k] = 5; gp.ordenar();
    const l = visaoAprendizado(gp).linhas.find(x => x.k === k)!;
    expect(l.delta).toBeGreaterThan(0);                 // subiu
    expect(l.pos).toBeLessThan(gp.ativas.length - 1);
  });
  test("nota abaixo do limiar marca a pior regra livre como proxima a sair", () => {
    const gp = pet(true), k = gp.ativas[1];
    gp.notas[k] = -1;
    const v = visaoAprendizado(gp);
    expect(v.linhas.filter(l => l.candidataATroca).map(l => l.k)).toEqual([k]);
    gp.travas[k] = 1;
    for (const o of gp.ativas) if (o !== k) gp.notas[o] = 1;
    expect(visaoAprendizado(gp).linhas.some(l => l.candidataATroca)).toBe(false);   // travada nao sai
  });
  test("travas e vetos do dono aparecem, e a historia traz quem mexeu", () => {
    const gp = pet(false), [a, b] = gp.ativas;
    gp.intervir("travar", a); gp.intervir("vetar", b);
    const v = visaoAprendizado(gp);
    expect(v.travadas).toHaveLength(1);
    expect(v.vetadas.map(x => x.k)).toEqual([b]);
    expect(v.linhas.find(l => l.k === a)!.estado).toBe("travada");
    expect(v.mudancas.filter(x => x.tipo === "dono")).toHaveLength(2);
  });
  test("so le: a assinatura do pet nao muda; sem forma, falha alto", () => {
    const gp = pet(true), antes = JSON.stringify(gp.assinatura());
    visaoAprendizado(gp);
    expect(JSON.stringify(gp.assinatura())).toBe(antes);
    expect(() => visaoAprendizado(new GambitsPet())).toThrow(/ainda não tem regras/);
  });
  test("tipoMudanca separa troca do pet, evolucao e dono", () => {
    expect(tipoMudanca({ luta: 1, texto: "trocou “x” por “y”" })).toBe("troca");
    expect(tipoMudanca({ luta: 1, texto: "evoluiu para A" })).toBe("evolucao");
    expect(tipoMudanca({ luta: 1, texto: "você: travar", dono: true })).toBe("dono");
  });
});
