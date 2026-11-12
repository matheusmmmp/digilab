/* A CO7 no grupo do jogo (docs/ESPEC_V3_COOPERACAO_CO7.md, secoes 2 a 4 e CO7-7): o modular de cada pet nasce com os deveres quando o grupo
   liga a `co7`; o gesto aparece sem numero (D-MM-8).
   - desligada no jogo (D-CO6c-1): o GrupoDoJogo de hoje nao a liga, e nenhum motivo ganha o `dever`;
   - ligada (so nos testes): cada decisao do modular registra o `dever`, o grupo guarda o que os deveres fizeram, e nenhuma decisao com o
     escudo valendo escolhe comer a comida proibida (o G-ESCUDO no motor do jogo);
   - o texto do gesto: hesitar e deixar a comida, consolar; nenhum algarismo. */
import { describe, expect, test } from "vitest";
import { GrupoDoJogo, TPD, VERSAO_GRUPO } from "../motor/index.ts";
import { gestoDoDever } from "../src/telas/pet/AtosDoIrmao.tsx";

function viver(co7: boolean, semente = 303): GrupoDoJogo {
  const g = new GrupoDoJogo(semente, VERSAO_GRUPO, true, co7, co7);
  for (const i of g.ids) g.agir(i, m => m.trocarCerebro("modular"));
  for (let k = 0; k < (4 * TPD) / 15; k++) {
    g.avancar(15);
    if (k % 8 === 0) g.agir(k % 16 === 0 ? "A" : "B", m => m.observar("alimentar"));
  }
  return g;
}
const LIGADA = viver(true), DESLIGADA = viver(false);

describe("a CO7 no grupo do jogo", () => {
  test("desligada no jogo: nenhum motivo tem o dever, e o grupo nao guarda nada", () => {
    expect(new GrupoDoJogo(101, VERSAO_GRUPO).grupo.coop!.cfg.co7).toBe(false);
    for (const m of Object.values(DESLIGADA.motores)) expect(m.lab!.motivos.some(x => "dever" in x)).toBe(false);
    expect(DESLIGADA.grupo.deveres).toEqual([]);
    expect(() => new GrupoDoJogo(101, VERSAO_GRUPO, true, false, true)).toThrow(/CO6/);
  });

  test("ligada: o dever em cada decisao do modular, e o grupo guarda os que tinham o irmao a vista ou lembrado", () => {
    for (const m of Object.values(LIGADA.motores)) {
      expect(m.lab!.dever).not.toBeNull();
      expect(m.lab!.motivos.every(x => "dever" in x)).toBe(true);
    }
    const comDever = Object.values(LIGADA.motores).flatMap(m => m.lab!.motivos.filter(x => x["dever"] !== null)).length;
    expect(LIGADA.grupo.deveres.length).toBe(comDever);
    expect(comDever).toBeGreaterThan(0);
  });

  test("o G-ESCUDO no jogo: com o escudo valendo, nenhuma escolha come a comida proibida", () => {
    for (const x of LIGADA.grupo.deveres) {
      const d = x.dever as { escudo: boolean; proibidas: unknown[] }, e = x.escolha as unknown[];
      if (d.escudo && d.proibidas.length) expect(e[0] === "comer" && e[1] === "comida" && d.proibidas.includes(e[2])).toBe(false);
    }
  });
});

describe("o gesto, em palavras", () => {
  const base = { removidas: [] as unknown[], aprovadas: 0, proibidas: [7] as unknown[], culpa: 0 };
  test("hesitar e deixar a comida, consolar, ou nada; sem numero", () => {
    expect(gestoDoDever(["explorar", "vagar", null], { ...base, removidas: [["comer", "comida", 7]] })).toBe("hesitou e deixou a comida para o irmão, que estava aflito");
    expect(gestoDoDever(["ocioso", null, null], { ...base, aprovadas: 2 })).toBe("hesitou e deixou a comida para o irmão, que estava aflito");
    expect(gestoDoDever(["comer", "comida", 7], { ...base, aprovadas: 2 })).toBeNull();               // pegou mesmo assim (sem o escudo)
    expect(gestoDoDever(["explorar", "vagar", null], { ...base, culpa: 128 })).toBe("quis consolar o irmão, que estava aflito");
    expect(gestoDoDever(["explorar", "vagar", null], base)).toBeNull();
    for (const t of ["hesitou e deixou a comida para o irmão, que estava aflito", "quis consolar o irmão, que estava aflito"]) expect(/\d/.test(t)).toBe(false);
  });
});
