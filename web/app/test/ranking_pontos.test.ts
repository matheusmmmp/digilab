/* MMO1 (docs/PLANO_V3_MMO.md, secoes 4 e 5): a conta dos pontos, src/ranking/pontos.ts. Um pet que nasce como no jogo, cresce ate o
   Rookie e luta na Arena com sementes "entregues"; a conta refaz o registro e tem de dar os pontos que as regras dizem, pela vitoria que o
   motor deu na hora. */
import { describe, expect, it } from "vitest";
import { Motor, PetMorto, VERSAO_PET, hashSemente, IDS_CENA, type EventoRegistro } from "../motor/index.ts";
import { ligarProduto } from "../src/produto.ts";
import {
  LUTAS_POR_DIA, PONTOS_FAIXA, compararLinhas, diaDe, linhasDaSemana, lutasRanqueadas, ordenarTabela, semanaDe,
  type LinhaSemana, type SementeEntregue,
} from "../src/ranking/pontos.ts";

const H = 3600_000;
/** segunda-feira, 16/11/2026, 12:00 em Brasilia (15:00 UTC) */
const SEG = Date.UTC(2026, 10, 16, 15);

/** um pet de semente 101 ate o Rookie, cuidado como no scripts/mmo0/vida.ts */
function petRookie(): Motor {
  const m = ligarProduto(new Motor(101, VERSAO_PET));
  for (let p = 0; p < 3000 && m.estagioAtual === "bebe"; p++) {
    m.avancar(10);
    try {
      if (m.e.fome < .6) m.deixarComida("racao", Math.max(0, Math.min(1023, m.mundo!.pet[0] + 24)), m.mundo!.pet[1]);
      if (m.e.sujeira >= 2) m.observar("limpar");
    } catch (e) { if (e instanceof PetMorto) throw e; /* o motor recusou (dormindo): segue */ }
  }
  if (m.estagioAtual !== "crianca") throw new Error("o pet de teste nao chegou ao Rookie");
  return m;
}
/** n lutas ranqueadas contra os rivais dados (um por luta), com a hora de cada uma; devolve o registro, as entregues e se venceu */
function lutar(m: Motor, rivais: string[], horas: number[]): { entregues: SementeEntregue[]; venceu: boolean[] } {
  const entregues: SementeEntregue[] = [], venceu: boolean[] = [];
  rivais.forEach((r, k) => {
    m.avancar(10);
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    const s = hashSemente("teste-mmo1", m.log.length, k), indice = m.log.length;
    entregues.push({ semente: s, indice, hora: horas[k] });
    venceu.push(m.lutarPoc(r, s, IDS_CENA[0]).venceu);
  });
  return { entregues, venceu };
}
const copia = (log: readonly EventoRegistro[]) => JSON.parse(JSON.stringify(log)) as EventoRegistro[];

describe("MMO1: a semana e o dia de Brasilia", () => {
  it("o dia vira a 00:00 de Brasilia (03:00 UTC), e a semana na segunda", () => {
    expect(diaDe(Date.UTC(2026, 10, 16, 2, 59))).toBe("2026-11-15");
    expect(diaDe(Date.UTC(2026, 10, 16, 3, 0))).toBe("2026-11-16");
    expect(semanaDe(Date.UTC(2026, 10, 16, 2, 59))).toBe("2026-11-09");   // domingo 23:59 em Brasilia: a semana de antes
    expect(semanaDe(Date.UTC(2026, 10, 16, 3, 0))).toBe("2026-11-16");
    expect(semanaDe(Date.UTC(2026, 10, 23, 2, 59))).toBe("2026-11-16");
  });
});

describe("MMO1: os pontos das lutas ranqueadas", () => {
  const m = petRookie(), rivais = m.rivaisArenaPoc();
  const [a, b] = rivais;
  /* tres lutas contra a na mesma semana, uma contra b, e uma contra a na semana seguinte */
  const horas = [SEG, SEG + H, SEG + 2 * H, SEG + 3 * H, SEG + 7 * 24 * H];
  const { entregues, venceu } = lutar(m, [a, a, a, b, a], horas);
  const log = copia(m.log);
  const lutas = lutasRanqueadas(101, VERSAO_PET, log, entregues);

  it("a vitoria vale a faixa do rival, a repetida na semana vale a metade da anterior, e a semana nova zera a metade", () => {
    const base = PONTOS_FAIXA.Rookie;
    let k = 0;
    const esperado = lutas.map((l, i) => {
      if (!venceu[i]) return 0;
      if (i === 3 || i === 4) return base;   // outro rival; outra semana
      return base / 2 ** k++;
    });
    expect(lutas.map(l => l.pontos)).toEqual(esperado);
    expect(lutas.map(l => l.situacao)).toEqual(venceu.map(v => v ? "vitoria" : "derrota"));
    expect(lutas.every(l => l.faixa === "Rookie" && l.estagio === "Rookie")).toBe(true);
  });
  it("a linha da semana soma os pontos, conta os rivais vencidos e as lutas usadas", () => {
    const linhas = linhasDaSemana(lutas);
    expect(linhas.map(l => l.semana)).toEqual(["2026-11-16", "2026-11-23"]);
    const s1 = linhas[0];
    expect(s1.lutasUsadas).toBe(4);
    expect(s1.pontos).toBe(lutas.slice(0, 4).reduce((x, l) => x + l.pontos, 0));
    expect(s1.rivaisVencidos).toBe(new Set(lutas.slice(0, 4).filter(l => l.situacao === "vitoria").map(l => l.rival)).size);
  });
  it("a semente entregue que nao virou a luta naquele indice conta como luta, com 0", () => {
    const extra: SementeEntregue = { semente: 7, indice: entregues[1].indice, hora: entregues[1].hora };
    const r = lutasRanqueadas(101, VERSAO_PET, log, [entregues[0], extra, ...entregues.slice(1)]);
    expect(r[1].situacao).toBe("nao_enviada");
    expect(r[1].pontos).toBe(0);
    expect(linhasDaSemana(r)[0].lutasUsadas).toBe(5);
  });
  it("a semente pedida depois do fim do registro fica pendente, com 0, e conta como luta usada", () => {
    const r = lutasRanqueadas(101, VERSAO_PET, log, [...entregues.slice(0, 4), { semente: 9, indice: log.length, hora: SEG + 4 * H }]);
    expect(r[4].situacao).toBe("pendente");
    expect(r[4].pontos).toBe(0);
    expect(linhasDaSemana(r)[0].lutasUsadas).toBe(5);
  });
  it("a semente alem do limite do dia nao conta", () => {
    const muitas: SementeEntregue[] = Array.from({ length: LUTAS_POR_DIA + 1 }, (_, k) => ({ semente: 1000 + k, indice: log.length, hora: SEG + k }));
    const r = lutasRanqueadas(101, VERSAO_PET, log, muitas);
    expect(r.filter(l => l.situacao === "acima_do_limite").length).toBe(1);
    expect(r[LUTAS_POR_DIA].situacao).toBe("acima_do_limite");
    expect(linhasDaSemana(r)[0].lutasUsadas).toBe(LUTAS_POR_DIA);
  });
  it("falha alto: semente repetida, fora de ordem e registro que nao reproduz", () => {
    expect(() => lutasRanqueadas(101, VERSAO_PET, log, [entregues[0], entregues[0]])).toThrow(/duas vezes/);
    expect(() => lutasRanqueadas(101, VERSAO_PET, log, [entregues[1], entregues[0]])).toThrow(/fora de ordem/);
    const ruim = copia(log); ruim[ruim.length - 1][0] += 1;
    expect(() => lutasRanqueadas(101, VERSAO_PET, ruim, entregues)).toThrow();
  });
  it("a mesma conta duas vezes da o mesmo resultado (funcao pura)", () => {
    expect(lutasRanqueadas(101, VERSAO_PET, log, entregues)).toEqual(lutas);
  });
});

describe("MMO1: o desempate da tabela da semana", () => {
  const l = (pontos: number, rivaisVencidos: number, lutasUsadas: number, horaDosPontos: number | null): LinhaSemana =>
    ({ semana: "2026-11-16", estagio: "Rookie", pontos, rivaisVencidos, lutasUsadas, horaDosPontos });
  it("pontos, depois rivais, depois menos lutas, depois quem chegou antes", () => {
    const t = ordenarTabela([l(10, 1, 3, 5), l(20, 1, 9, 9), l(10, 2, 9, 9), l(10, 1, 2, 9), l(10, 1, 3, 4), l(0, 0, 1, null)]);
    expect(t.map(x => [x.pontos, x.rivaisVencidos, x.lutasUsadas, x.horaDosPontos])).toEqual([
      [20, 1, 9, 9], [10, 2, 9, 9], [10, 1, 2, 9], [10, 1, 3, 4], [10, 1, 3, 5], [0, 0, 1, null]]);
  });
  it("sem pontos vem depois de quem tem a mesma contagem com pontos", () => {
    expect(compararLinhas(l(0, 0, 1, null), l(0, 0, 1, 3))).toBeGreaterThan(0);
  });
  it("nao mistura semanas nem estagios", () => {
    expect(() => ordenarTabela([l(1, 1, 1, 1), { ...l(1, 1, 1, 1), estagio: "Champion" }])).toThrow(/misturados/);
  });
});
