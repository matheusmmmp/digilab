/* As marcas da fala do Rookie e o rotulo do porque (src/falaMarcas.ts, defeitos vistos no promo de 2026-11-06): depois de treinar
   com o pedido de pausa, o balao mostrava "[sem pausa] [:treino puxado:]" e o painel "a toa ?". O save e o do e2e (um Palmon v11 no
   Rookie que pediu pausa); o motor treina de verdade e o motivo e o que o jogo grava. */
import { describe, expect, test } from "vitest";
import { readFileSync } from "node:fs";
import { FATORES_TXT, Motor, type EventoRegistro } from "../motor/index.ts";
import { falaDe } from "../src/fala.ts";
import { ACAO_MOTIVO, ICONE_FATOR, partesFala, rotuloAcaoFala } from "../src/falaMarcas.ts";

const SAVE = JSON.parse(readFileSync(new URL("../e2e/save_treino_pausa.json", import.meta.url), "utf8")) as { semente: number; log: EventoRegistro[]; versao: number };
function treinadoCansado(): Motor {
  const m = Motor.reproduzir(SAVE.semente, SAVE.log, SAVE.versao);
  expect(m.estagioAtual).toBe("crianca");
  /* o intervalo de 10 min entre treinos, um minuto por vez, com o pedido de pausa de pe */
  for (let i = 0; i < 30 && !(m.treino.podeTocar(m.e.tick) && m.treino.pedePausa); i++) m.avancar(1);
  expect(m.treino.pedePausa).toBe(true);
  m.treinar("esquiva");
  expect(m.motivo?.acao).toBe("treinar_cansado");
  return m;
}

describe("a fala do Rookie sem marcas cruas", () => {
  test("a acao e a causa saem separadas, sem colchetes nem dois-pontos", () => {
    expect(partesFala("[sem pausa] [:treino puxado:]")).toEqual([
      { tipo: "acao", txt: "sem pausa" }, { tipo: "texto", txt: " " }, { tipo: "causa", txt: "treino puxado", fator: "fadiga_treino" },
    ]);
    expect(partesFala("... [comer] [:barriga vazia:]")).toEqual([
      { tipo: "texto", txt: "... " }, { tipo: "acao", txt: "comer" }, { tipo: "texto", txt: " " }, { tipo: "causa", txt: "barriga vazia", fator: "necessidade_fome" },
    ]);
    /* marcador fora dos fatores (a confianca de combate): etiqueta sem fator */
    expect(partesFala("[:confiante:] Ganhei!")).toEqual([{ tipo: "causa", txt: "confiante", fator: null }, { tipo: "texto", txt: " Ganhei!" }]);
  });
  test("a fala do treino com pausa pedida: nenhuma marca crua sobra e a causa tem icone", () => {
    const m = treinadoCansado(), txt = falaDe(m, m.motivo!);
    expect(txt).toContain("[:treino puxado:]");
    const partes = partesFala(txt);
    for (const p of partes) expect(p.txt, `parte ${p.tipo}`).not.toMatch(/[[\]]|^:|:$/);
    const causa = partes.find(p => p.tipo === "causa");
    expect(causa).toMatchObject({ fator: "fadiga_treino" });
    expect(ICONE_FATOR.fadiga_treino).toBeTruthy();
  });
  test("todo fator com icone existe nas tabelas de fala", () => {
    for (const f of Object.keys(ICONE_FATOR)) expect(FATORES_TXT[f], f).toBeTruthy();
  });
});

describe("o porque diz o que o pet fez", () => {
  test("o motivo do treino com pausa pedida: o rotulo do treino, nao a acao de agora", () => {
    const m = treinadoCansado();
    expect(rotuloAcaoFala(m)).toBe(ACAO_MOTIVO.treinar_cansado);
    expect(rotuloAcaoFala(m)).not.toBe("à toa");
  });
  test("acao de motivo sem rotulo falha alto", () => {
    const m = treinadoCansado();
    m.motivo = { ...m.motivo!, acao: "acao_nova" };
    expect(() => rotuloAcaoFala(m)).toThrow(/acao_nova/);
  });
});
