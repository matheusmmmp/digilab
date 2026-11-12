/* Os dois ovos e o save do grupo (docs/TAREFA_V3_COOPERACAO.md, etapa CO4c; a v26):
   - os dois ovos: o primeiro do brasao escolhido, o segundo surpresa (D-CO4b-6), os dois com o produto ligado, cada um no registro dele;
   - o save do grupo: {semente, log, versao, grupo, foco}; abrir e reprocessar o registro do grupo da a mesma assinatura (o G-REPLAY-2 no save),
     e o save malformado abre como erro visivel, sem gravar por cima;
   - o jogo com os dois pets: o relogio (o avancar do pet em foco) anda os dois, a acao do dono vai ao pet em foco, o foco troca e fica no
     save, e a mudanca grava o grupo;
   - a chave DOIS_OVOS_LIGADO ligou na CO4d; o ovo de um pet so segue v25, e o pet v25 salvo abre igual (o G-HOJE). */
import { describe, expect, test } from "vitest";
import { DOIS_OVOS_LIGADO, ESPECIES, GrupoDoJogo, TPD, VERSAO_PET, VERSAO_V26, sementeDoSegundoJogo } from "../motor/index.ts";
import { CHAVE, lerSave, textoSave, textoSaveGrupo, type Armazenamento } from "../src/save.ts";
import { focar, iniciarJogo, jogoAtual, mudarMotor, trocarGrupo } from "../src/jogo.ts";
import { chocarDoisOvos, especieDaSemente, sementeDoBrasao } from "../src/jornada.ts";

const armaz = (dados: Record<string, string> = {}) => {
  const a: Armazenamento & { dados: Record<string, string> } = { dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } };
  return a;
};
const ESP = ESPECIES[0];
const SEMENTE = (() => { for (let s = 1; ; s++) if (especieDaSemente(s) === ESP) return s; })();

describe("os dois ovos", () => {
  test("o primeiro e do brasao, o segundo e surpresa, e os dois nascem com o produto", () => {
    const g = chocarDoisOvos(ESP, "rapida", SEMENTE);
    expect(g.versao).toBe(VERSAO_V26);
    expect(g.motor("A").especie).toBe(ESP);
    expect(g.motor("B").semente).toBe(sementeDoSegundoJogo(SEMENTE));
    expect(g.motor("B").especie).toBe(especieDaSemente(g.motor("B").semente));
    for (const i of g.ids) expect(g.log.some(e => e[3] === i && e[1] === "p"), `o produto do pet ${i}`).toBe(true);
    expect(() => chocarDoisOvos(ESP, "rapida", SEMENTE + (especieDaSemente(SEMENTE + 1) === ESP ? 2 : 1))).toThrow(/outro brasão/);
    expect(especieDaSemente(sementeDoBrasao(ESP))).toBe(ESP);
  });

  test("a chave ligou na CO4d: o ovo do brasao choca os dois; o ovo de um pet so (a heranca, o exemplo) segue v25", () => {
    expect(DOIS_OVOS_LIGADO).toBe(true);
    expect(VERSAO_PET).toBe(27);
  });
});

describe("o save do grupo", () => {
  const g = chocarDoisOvos(ESP, "rapida", SEMENTE);
  for (let k = 0; k < 24; k++) { g.avancar(15); if (k % 6 === 0) g.agir(k % 12 === 0 ? "A" : "B", m => m.observar("alimentar")); }

  test("o G-REPLAY-2 no save: abrir o save do grupo da a mesma assinatura e o mesmo foco", () => {
    const a = armaz({ [CHAVE]: textoSaveGrupo(g, "B") });
    const l = lerSave(a);
    if (l.tipo !== "ok") throw new Error(JSON.stringify(l));
    expect(l.grupo!.assinatura()).toBe(g.assinatura());
    expect(l.motor).toBe(l.grupo!.motor("B"));
    expect(JSON.parse(a.dados[CHAVE])).toMatchObject({ semente: SEMENTE, versao: VERSAO_V26, grupo: true, foco: "B" });
  });

  test("o save malformado abre como erro visivel", () => {
    const bom = JSON.parse(textoSaveGrupo(g, "A")) as Record<string, unknown>;
    const ruins = [{ ...bom, foco: "C" }, { ...bom, grupo: "sim" }, { ...bom, log: [...(bom.log as unknown[]), [0, "zz", 1, "A"]] },
                   { ...bom, versao: 23 }];
    for (const r of ruins) expect(lerSave(armaz({ [CHAVE]: JSON.stringify(r) })).tipo, JSON.stringify(r).slice(0, 80)).toBe("erro");
    expect(() => textoSave(g.motor("A"))).toThrow(/com o grupo/);
    expect(() => textoSaveGrupo(g, "C")).toThrow(/fora do grupo/);
  });
});

describe("o jogo com os dois pets", () => {
  test("o relogio anda os dois, a acao vai ao pet em foco, o foco troca e o grupo e gravado", () => {
    const a = armaz();
    iniciarJogo(a);
    const g = chocarDoisOvos(ESP, "rapida", SEMENTE);
    trocarGrupo(g, "novo");
    const j = jogoAtual();
    expect(j.grupo).toBe(g);
    expect(j.foco).toBe("A");
    expect(j.motor).toBe(g.motor("A"));
    const t0 = g.tick;
    mudarMotor(m => m.avancar(30), "adiado");
    expect([g.motor("A").e.tick, g.motor("B").e.tick]).toEqual([t0 + 30, t0 + 30]);
    mudarMotor(m => m.observar("acariciar"));
    expect(g.log.at(-1)![3]).toBe("A");
    focar("B");
    expect(jogoAtual().motor).toBe(g.motor("B"));
    mudarMotor(m => m.observar("limpar"));
    expect(g.log.at(-1)![3]).toBe("B");
    mudarMotor(m => m.avancar(TPD / 2), "agora");
    const salvo = JSON.parse(a.dados[CHAVE]) as { grupo: boolean; foco: string };
    expect(salvo).toMatchObject({ grupo: true, foco: "B" });
    /* abrir de novo: o mesmo grupo, o mesmo foco */
    iniciarJogo(armaz({ [CHAVE]: a.dados[CHAVE] }));
    const k = jogoAtual();
    expect(k.grupo!.assinatura()).toBe(g.assinatura());
    expect(k.foco).toBe("B");
    expect(k.motor).toBe(k.grupo!.motor("B"));
  });

  test("o pet de um pet so segue igual (o grupo nao aparece sem os dois ovos)", () => {
    iniciarJogo(armaz());
    mudarMotor(m => m.observar("alimentar"));
    const j = jogoAtual();
    expect(j.grupo).toBeNull();
    expect(j.motor.noGrupo).toBe(false);
    expect(() => focar("B")).toThrow(/so os dois pets/);
    expect(GrupoDoJogo.reproduzir(SEMENTE, VERSAO_V26, []).tick).toBe(chocarDoisOvos(ESP, "rapida", SEMENTE).tick);
  });
});
