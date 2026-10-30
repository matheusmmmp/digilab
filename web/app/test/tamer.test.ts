/* Registro do Tamer (src/tamer.ts; docs/DESIGN_MEDALHAS_ARENAS.md, secao 5): event sourcing proprio na chave
   CHAVE-tamer; medalha na primeira vitoria contra o lider; o pet ativo recebe o "u"; o descarte unico
   (o 6, da luta em tempo real) tira os pets v1-v12 e a Fabrica de antes. E o ciclo no estado do app (src/jogo.ts): vencer o lider grava a medalha e libera a evolucao. */
import { describe, expect, test } from "vitest";
import { DUR_EVO, MEDALHAS, Motor, hashSemente } from "../motor/index.ts";
import { CHAVE, textoSave, type Armazenamento } from "../src/save.ts";
import { iniciarJogo, jogoAtual, mudarMotor, tamerAtual, trocarMotor } from "../src/jogo.ts";
import {
  CHAVE_AVISO_TR, CHAVE_AVISO_V6, CHAVE_DESCARTADOS, CHAVE_DESCARTE, CHAVE_TAMER, Tamer, VERSAO_DESCARTE, conferirMedalhas, descartarPetsAntigos,
  gravarTamer, lerTamer, semFabricaAntiga, sincronizarPet, textoFalta, type EventoTamer,
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
    const t = new Tamer(), m = new Motor(5), a = armaz();
    t.ganhar("campina", m, 1000); t.ganhar("floresta", m, 2000);
    gravarTamer(a, t);
    const r = lerTamer(a);
    expect(r.n).toBe(2);
    expect(r.medalhas).toEqual(t.medalhas);
    expect(r.ganha("floresta")).toMatchObject({ n: 2, quando: 2000, pet: 5 });
    expect(JSON.parse(a.dados[CHAVE_TAMER])).toEqual({ versao: 7, log: t.log });
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
  test("medalha so na primeira vitoria contra o lider, uma vez por Tamer", () => {
    const t = new Tamer(), m = new Motor(11);
    m.avancar(DUR_EVO.bebe + 30);
    vencer(m, GAZIMON);
    const novas = conferirMedalhas(t, m, 5);
    expect(novas.map(x => x.id)).toEqual(["campina"]);
    expect(novas[0]).toMatchObject({ n: 1, pet: 11, tick: m.e.tick, quando: 5 });
    vencer(m, GAZIMON);
    expect(conferirMedalhas(t, m)).toEqual([]);                  /* revanche: nada novo */
    expect(textoFalta(t, 3)).toBe("Faltam 2 medalhas: Medalha da Torre de pedra (vença o Guardromon na Torre de pedra) e Medalha da Floresta (vença o Youkomon na Floresta).");
    expect(textoFalta(new Tamer(), 1)).toBe("Falta a Medalha da Campina: vença o Gazimon na Campina.");
  });
  test("sincronizar: o pet atras do Tamer recebe o u; pet em dia nao muda", () => {
    const t = new Tamer(), m = new Motor(13);
    t.ganhar("campina", m); t.ganhar("torre", m);
    expect(sincronizarPet(t, m)).toBe(true);
    expect(m.log).toEqual([[m.e.tick, "u", { n: 2 }]]);
    expect(sincronizarPet(t, m)).toBe(false);
  });
});

describe("descarte unico dos pets antigos (o 6: a luta em tempo real, pets v13; E2 e D-4)", () => {
  const v = (versao?: number, semente = 1) => JSON.stringify({ semente, log: [], ...(versao ? { versao } : {}) });
  const avisoTR = (a: ReturnType<typeof armaz>) => JSON.parse(a.dados[CHAVE_AVISO_TR]);
  test("primeira abertura: os pets v1-v12 saem (ativo e guardados), ficam guardados para o arquivo e o aviso fica pendente; roda uma vez", () => {
    const guardados = [{ semente: 2, log: [], versao: 3 }, { semente: 3, log: [] }, { semente: 4, log: [], versao: 12 }, { semente: 5, log: [], versao: 13 }];
    const a = armaz({ [CHAVE]: v(5), [GUARDADOS]: JSON.stringify(guardados) });
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(4);
    expect(a.dados[CHAVE]).toBeUndefined();
    expect(JSON.parse(a.dados[GUARDADOS])).toEqual([guardados[3]]);           /* o v13 fica */
    expect(avisoTR(a)).toEqual({ pets: 4, fabrica: 0 });
    expect(a.dados[CHAVE_AVISO_V6]).toBeUndefined();
    expect(a.dados[CHAVE_DESCARTE]).toBe(String(VERSAO_DESCARTE));
    expect(VERSAO_DESCARTE).toBe(6);
    expect(JSON.parse(a.dados[CHAVE_DESCARTADOS])).toEqual([JSON.parse(v(5)), ...guardados.slice(0, 3)]);
    expect(lerTamer(a).n).toBe(0);
    a.dados[CHAVE] = v(12);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBeNull();          /* ja rodou: nada sai */
    expect(a.dados[CHAVE]).toBe(v(12));
  });
  test("depois do descarte 5 (o limite): os v6-v12 saem; o v13 fica; o Tamer fica com as medalhas", () => {
    const t = new Tamer(); t.ganhar("campina", new Motor(9), 1);
    const a = armaz({ [CHAVE]: v(13), [GUARDADOS]: JSON.stringify([{ semente: 7, log: [], versao: 6 }, { semente: 8, log: [], versao: 11 }]), [CHAVE_DESCARTE]: "5" });
    gravarTamer(a, t);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(2);
    expect(a.dados[CHAVE]).toBe(v(13));
    expect(a.dados[GUARDADOS]).toBe("[]");
    expect(avisoTR(a)).toEqual({ pets: 2, fabrica: 0 });
    expect(lerTamer(a).n).toBe(1);
    expect(JSON.parse(a.dados[CHAVE_TAMER]).versao).toBe(7);
  });
  test("a Fabrica de antes sai do Tamer (D-4): o aviso conta as tentativas; o resto do Tamer fica", () => {
    /* o registro de um Tamer com o titulo e uma tentativa da Fabrica dos v9 (as lutas dela nao precisam estar no registro) */
    const seis = MEDALHAS.slice(0, 6).map((md, i) => ["medalha", { id: md.id, n: i + 1, quando: i + 1, pet: 1, forma: "Agumon", tick: 900 }]);
    const t = Tamer.reproduzir([...seis, ["campeao", { n: 1, quando: 10, pet: 1, forma: "WarGreymon", tick: 950 }]] as EventoTamer[]);
    t.alugarFabrica(0, 20);
    const log = t.log.map(ev => ev[0] === "fabrica" ? ["fabrica", { ...(ev[1] as object), v: 9 }] : ev) as EventoTamer[];
    const a = armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 6, log }) });
    expect(() => Tamer.reproduzir(log)).toThrow(/versão 9/);                 /* a Fabrica de antes nao se refaz mais */
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(0);
    expect(avisoTR(a)).toEqual({ pets: 0, fabrica: 1 });
    const r = lerTamer(a);
    expect(r.fabrica).toEqual([]); expect(r.titulo).not.toBeNull();
    expect(JSON.parse(a.dados[CHAVE_TAMER]).versao).toBe(7);
    /* o registro 7 nao aceita a Fabrica de antes */
    const b = armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 7, log }) });
    expect(() => lerTamer(b)).toThrow(/regras de antes/);
    expect(semFabricaAntiga(log).tentativas).toBe(1);
  });
  test("Tamer sem pet para descartar: fica como esta, sem aviso; marcador invalido falha alto", () => {
    const t = new Tamer(); t.ganhar("campina", new Motor(9), 1);
    const a = armaz(); gravarTamer(a, t);
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(0);
    expect(lerTamer(a).n).toBe(1);
    expect(a.dados[CHAVE_AVISO_TR]).toBeUndefined();
    expect(a.dados[CHAVE_DESCARTE]).toBe("6");
    expect(() => descartarPetsAntigos(armaz({ [CHAVE_DESCARTE]: "x" }), GUARDADOS)).toThrow();
  });
  test("primeiro acesso (sem nada): nada sai, sem aviso; save que nao e JSON fica para o erro de sempre", () => {
    const a = armaz();
    expect(descartarPetsAntigos(a, GUARDADOS)).toBe(0);
    expect(a.dados[CHAVE_AVISO_TR]).toBeUndefined();
    expect(a.dados[GUARDADOS]).toBeUndefined();
    expect(a.dados[CHAVE_TAMER]).toBeDefined();
    const c = armaz({ [CHAVE]: "{" });
    expect(descartarPetsAntigos(c, GUARDADOS)).toBe(0); expect(c.dados[CHAVE]).toBe("{");
  });
});

describe("o ciclo no app", () => {
  test("vencer o lider grava a medalha, o u entra no registro do pet e o Rookie pronto evolui", () => {
    const m = new Motor(21);
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
    const pronto = new Motor(22);
    pronto.avancar(FIM_ROOKIE + 60);
    const t = new Tamer(); t.ganhar(MEDALHAS[0].id, new Motor(1));
    const a = armaz({ [CHAVE_TAMER]: JSON.stringify({ versao: 1, log: t.log }) });
    iniciarJogo(a);
    trocarMotor(Motor.reproduzir(22, pronto.log, 13), "save");
    expect(jogoAtual().motor.estagioAtual).toBe("adolescente");
    expect(jogoAtual().evolucoesAoTrocar).toBe(1);
    /* abertura: o save de um pet atras do Tamer recebe o u e e regravado */
    const b = armaz({ [CHAVE]: textoSave(pronto), [CHAVE_TAMER]: JSON.stringify({ versao: 1, log: t.log }) });
    iniciarJogo(b);
    expect(jogoAtual().motor.estagioAtual).toBe("adolescente");
    expect(JSON.parse(b.dados[CHAVE]).log.at(-1)[1]).toBe("u");
  });
  test("registro do Tamer que nao abre: erro visivel, sem medalha e sem gravar por cima", () => {
    const m = new Motor(23); m.avancar(DUR_EVO.bebe + 30);
    const a = armaz({ [CHAVE]: textoSave(m), [CHAVE_TAMER]: "{" });
    iniciarJogo(a);
    expect(jogoAtual().erroTamer).toMatch(/JSON/);
    mudarMotor(mm => { vencer(mm, GAZIMON); });
    expect(a.dados[CHAVE_TAMER]).toBe("{");
    expect(jogoAtual().motor.log.some(e => e[1] === "u")).toBe(false);
  });
});
