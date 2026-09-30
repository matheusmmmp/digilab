/* Registro do Tamer (src/tamer.ts; docs/DESIGN_MEDALHAS_ARENAS.md, secao 5): event sourcing proprio na chave
   CHAVE-tamer; medalha na primeira vitoria contra o lider (so pets v6); o pet ativo recebe o "u"; o descarte unico
   tira os pets v1-v5 (medalhas) e os v6 de antes do combate V21D. E o ciclo no estado do app (src/jogo.ts): vencer o lider grava a medalha e libera a evolucao. */
import { describe, expect, test } from "vitest";
import { DUR_EVO, MEDALHAS, Motor, hashSemente } from "../motor/index.ts";
import { CHAVE, textoSave, type Armazenamento } from "../src/save.ts";
import { iniciarJogo, jogoAtual, mudarMotor, tamerAtual, trocarMotor } from "../src/jogo.ts";
import {
  CHAVE_AVISO_V6, CHAVE_DESCARTE, CHAVE_TAMER, Tamer, conferirMedalhas, descartarPetsAntigos, gravarTamer, lerTamer, sincronizarPet, textoFalta,
  type EventoTamer,
} from "../src/tamer.ts";

const GUARDADOS = CHAVE + "-guardados";
const armaz = (dados: Record<string, string> = {}) => {
  const a: Armazenamento & { dados: Record<string, string>; removeItem(k: string): void } = {
    dados, getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; }, removeItem(k) { delete dados[k]; },
  };
  return a;
};
const GAZIMON = "npc_tier1_brutamontes";
const FIM_ROOKIE = DUR_EVO.bebe + DUR_EVO.crianca;
/** luta contra o lider ate a primeira vitoria (as lutas entram no registro); devolve quantas foram */
function vencer(m: Motor, k: string): number {
  for (let i = 1; i <= 60; i++) if (m.lutar(k, hashSemente("teste", m.semente, m.log.length)).res.pontosA === 1) return i;
  throw new Error("nao venceu em 60 lutas");
}

describe("registro do Tamer", () => {
  test("ganhar, gravar e reproduzir: o mesmo estado", () => {
    const t = new Tamer(), m = new Motor(5, 6), a = armaz();
    t.ganhar("campina", m, 1000); t.ganhar("floresta", m, 2000);
    gravarTamer(a, t);
    const r = lerTamer(a);
    expect(r.n).toBe(2);
    expect(r.medalhas).toEqual(t.medalhas);
    expect(r.ganha("floresta")).toMatchObject({ n: 2, quando: 2000, pet: 5 });
    expect(JSON.parse(a.dados[CHAVE_TAMER])).toEqual({ versao: 1, log: t.log });
    expect(lerTamer(armaz()).n).toBe(0);                          /* sem a chave: Tamer novo */
  });
  test("evento desconhecido, medalha repetida, contador fora de ordem e JSON quebrado falham alto", () => {
    const ok: EventoTamer = ["medalha", { id: "campina", n: 1, quando: 1, pet: 1, forma: "Agumon", tick: 480 }];
    expect(() => Tamer.reproduzir([["troféu", {}] as unknown as EventoTamer])).toThrow(/desconhecido/);
    expect(() => Tamer.reproduzir([ok, ["medalha", { ...ok[1], n: 2 }]])).toThrow(/repetida/);
    expect(() => Tamer.reproduzir([["medalha", { ...ok[1], n: 2 }]])).toThrow(/fora de ordem/);
    expect(() => Tamer.reproduzir([["medalha", { ...ok[1], id: "lua" }]])).toThrow(/desconhecida/);
    expect(() => lerTamer(armaz({ [CHAVE_TAMER]: "{" }))).toThrow(/JSON/);
    expect(() => lerTamer(armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 9, log: [] }) }))).toThrow(/versão/);
  });
  test("medalha so na primeira vitoria contra o lider, uma vez por Tamer, e so com pet v6", () => {
    const t = new Tamer(), m = new Motor(11, 6);
    m.avancar(DUR_EVO.bebe + 30);
    vencer(m, GAZIMON);
    const novas = conferirMedalhas(t, m, 5);
    expect(novas.map(x => x.id)).toEqual(["campina"]);
    expect(novas[0]).toMatchObject({ n: 1, pet: 11, tick: m.e.tick, quando: 5 });
    vencer(m, GAZIMON);
    expect(conferirMedalhas(t, m)).toEqual([]);                  /* revanche: nada novo */
    const v5 = new Motor(12, 5); v5.avancar(DUR_EVO.bebe + 30); vencer(v5, GAZIMON);
    expect(conferirMedalhas(new Tamer(), v5)).toEqual([]);
    expect(textoFalta(t, 3)).toBe("Faltam 2 medalhas: Medalha da Torre de pedra (vença o Guardromon na Torre de pedra) e Medalha da Floresta (vença o Youkomon na Floresta).");
    expect(textoFalta(new Tamer(), 1)).toBe("Falta a Medalha da Campina: vença o Gazimon na Campina.");
  });
  test("sincronizar: o pet v6 recebe o u; v5 e pet em dia nao mudam", () => {
    const t = new Tamer(), m = new Motor(13, 6);
    t.ganhar("campina", m); t.ganhar("torre", m);
    expect(sincronizarPet(t, m)).toBe(true);
    expect(m.log).toEqual([[m.e.tick, "u", { n: 2 }]]);
    expect(sincronizarPet(t, m)).toBe(false);
    const v5 = new Motor(14, 5);
    expect(sincronizarPet(t, v5)).toBe(false);
    expect(v5.log).toEqual([]);
  });
});

describe("descarte unico dos pets antigos (medalhas, combate V21D, arenas, escala v6 e limite)", () => {
  const v = (versao?: number) => JSON.stringify({ semente: 1, log: [], ...(versao ? { versao } : {}) });
  test("primeira abertura: os pets v1-v6 saem (ativo e guardados), o aviso fica pendente e o Tamer comeca vazio; roda uma vez", () => {
    const a = armaz({ [CHAVE]: v(5), [GUARDADOS]: JSON.stringify([{ semente: 2, log: [], versao: 3 }, { semente: 3, log: [] }, { semente: 4, log: [], versao: 6 }]) });
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(4);
    expect(a.dados[CHAVE]).toBeUndefined();
    expect(a.dados[GUARDADOS]).toBe("[]");
    expect(a.dados[CHAVE_AVISO_V6]).toBe("4");
    expect(a.dados[CHAVE_DESCARTE]).toBe("5");
    expect(lerTamer(a).n).toBe(0);
    a.dados[CHAVE] = v(6);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBeNull();          /* ja rodou: nada sai (o v6 de agora fica) */
    expect(a.dados[CHAVE]).toBe(v(6));
  });
  test("depois do descarte das medalhas (Tamer sem marcador): os v6 de antes do V21D saem, o Tamer recomeca, mesmo aviso", () => {
    const t = new Tamer(); t.ganhar("campina", new Motor(9, 6), 1);
    const a = armaz({ [CHAVE]: v(6), [GUARDADOS]: JSON.stringify([{ semente: 5, log: [], versao: 6 }]) });
    gravarTamer(a, t);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(2);
    expect(a.dados[CHAVE]).toBeUndefined();
    expect(a.dados[GUARDADOS]).toBe("[]");
    expect(a.dados[CHAVE_AVISO_V6]).toBe("2");
    expect(lerTamer(a).n).toBe(0);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBeNull();
  });
  test("depois do descarte do V21D (marcador 2): os v6 de antes das arenas saem de novo, mesmo aviso", () => {
    const a = armaz({ [CHAVE]: v(6), [CHAVE_DESCARTE]: "2" });
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(1);
    expect(a.dados[CHAVE]).toBeUndefined();
    expect(a.dados[CHAVE_DESCARTE]).toBe("5");
    expect(a.dados[CHAVE_AVISO_V6]).toBe("1");
    a.dados[CHAVE] = v(6);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBeNull();
    expect(a.dados[CHAVE]).toBe(v(6));
  });
  test("depois do descarte da escala v6 (marcador 4): os v6 de antes da regra do limite saem de novo, mesmo aviso", () => {
    const a = armaz({ [CHAVE]: v(6), [CHAVE_DESCARTE]: "4" });
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(1);
    expect(a.dados[CHAVE]).toBeUndefined();
    expect(a.dados[CHAVE_DESCARTE]).toBe("5");
    expect(a.dados[CHAVE_AVISO_V6]).toBe("1");
  });
  test("depois do descarte das arenas (marcador 3): os v6 de antes da escala v6 saem de novo, mesmo aviso", () => {
    const a = armaz({ [CHAVE]: v(6), [GUARDADOS]: JSON.stringify([{ semente: 7, log: [], versao: 6 }]), [CHAVE_DESCARTE]: "3" });
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(2);
    expect(a.dados[CHAVE]).toBeUndefined();
    expect(a.dados[GUARDADOS]).toBe("[]");
    expect(a.dados[CHAVE_DESCARTE]).toBe("5");
    expect(a.dados[CHAVE_AVISO_V6]).toBe("2");
    a.dados[CHAVE] = v(6);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBeNull();
    expect(a.dados[CHAVE]).toBe(v(6));
  });
  test("Tamer sem pet para descartar: fica como esta, sem aviso; marcador invalido falha alto", () => {
    const t = new Tamer(); t.ganhar("campina", new Motor(9, 6), 1);
    const a = armaz(); gravarTamer(a, t);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(0);
    expect(lerTamer(a).n).toBe(1);
    expect(a.dados[CHAVE_AVISO_V6]).toBeUndefined();
    expect(a.dados[CHAVE_DESCARTE]).toBe("5");
    expect(() => descartarPetsAntigos(armaz({ [CHAVE_DESCARTE]: "x" }), GUARDADOS)).toThrow();
  });
  test("primeiro acesso (sem nada): nada sai, sem aviso; save que nao e JSON fica para o erro de sempre", () => {
    const a = armaz();
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(0);
    expect(a.dados[CHAVE_AVISO_V6]).toBeUndefined();
    expect(a.dados[GUARDADOS]).toBeUndefined();
    expect(a.dados[CHAVE_TAMER]).toBeDefined();
    const c = armaz({ [CHAVE]: "{" });
    expect(descartarPetsAntigos(c, GUARDADOS)).toBe(0); expect(c.dados[CHAVE]).toBe("{");
  });
});

describe("o ciclo no app", () => {
  test("vencer o lider grava a medalha, o u entra no registro do pet e o Rookie pronto evolui", () => {
    const m = new Motor(21, 6);
    m.avancar(FIM_ROOKIE + 60);
    expect(m.estagioAtual).toBe("crianca");
    const a = armaz({ [CHAVE]: textoSave(m), [CHAVE_TAMER]: JSON.stringify({ versao: 1, log: [] }) });
    iniciarJogo(a);
    mudarMotor(mm => { vencer(mm, GAZIMON); });
    const j = jogoAtual();
    expect(tamerAtual().n).toBe(1);
    expect(lerTamer(a).ganha("campina")).toMatchObject({ pet: 21 });
    expect(j.motor.estagioAtual).toBe("adolescente");
    expect(j.motor.log[j.motor.log.length - 1][1]).toBe("u");
    /* o save gravado reproduz o mesmo pet */
    const s = JSON.parse(a.dados[CHAVE]);
    expect(Motor.reproduzir(s.semente, s.log, s.versao).assinatura()).toBe(j.motor.assinatura());
  });
  test("pet guardado pronto evolui quando volta a ser o ativo; na abertura o ativo tambem recebe o u", () => {
    const pronto = new Motor(22, 6);
    pronto.avancar(FIM_ROOKIE + 60);
    const t = new Tamer(); t.ganhar(MEDALHAS[0].id, new Motor(1, 6));
    const a = armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 1, log: t.log }) });
    iniciarJogo(a);
    trocarMotor(Motor.reproduzir(22, pronto.log, 6), "save");
    expect(jogoAtual().motor.estagioAtual).toBe("adolescente");
    expect(jogoAtual().evolucoesAoTrocar).toBe(1);
    /* abertura: o save de um pet atras do Tamer recebe o u e e regravado */
    const b = armaz({ [CHAVE]: textoSave(pronto), [CHAVE_TAMER]: JSON.stringify({ versao: 1, log: t.log }) });
    iniciarJogo(b);
    expect(jogoAtual().motor.estagioAtual).toBe("adolescente");
    expect(JSON.parse(b.dados[CHAVE]).log.at(-1)[1]).toBe("u");
  });
  test("registro do Tamer que nao abre: erro visivel, sem medalha e sem gravar por cima", () => {
    const m = new Motor(23, 6); m.avancar(DUR_EVO.bebe + 30);
    const a = armaz({ [CHAVE]: textoSave(m), [CHAVE_TAMER]: "{" });
    iniciarJogo(a);
    expect(jogoAtual().erroTamer).toMatch(/JSON/);
    mudarMotor(mm => { vencer(mm, GAZIMON); });
    expect(a.dados[CHAVE_TAMER]).toBe("{");
    expect(jogoAtual().motor.log.some(e => e[1] === "u")).toBe(false);
  });
});
