/* Voz propria no app (src/voz.ts): gatilhos, ritmo, assunto da fala e a queda sem o servidor (o molde). A fala entra no
   registro do pet pelo evento "fl" e rejoga igual. */
import { describe, expect, test } from "vitest";
import { Motor, TPD, mentiraDeHistoria } from "../motor/index.ts";
import { REENCONTRO_REAL_MS, RITMO_MIN, assuntoDaFala, gatilhoDe, podeFalar } from "../src/voz.ts";

/** pet v7 criado e levado ate a crianca, com o dono agindo a cada 15 min */
function crianca(semente = 11): Motor {
  const m = new Motor(semente, 7);
  while (m.estagioAtual === "bebe") { m.avancar(15); m.observar(m.e.fome > .5 ? "alimentar" : "acariciar"); }
  return m;
}

describe("gatilhos e ritmo", () => {
  test("ao carregar so observa; evolucao dispara marco; reencontro depois de 3 h", () => {
    const m = new Motor(21, 7);
    expect(gatilhoDe(m)).toBeNull();                           /* primeira vez: so olha */
    const vistos: (string | null)[] = [];
    let t = 1e12;                                                /* relogio (ms) */
    while (m.estagioAtual === "bebe") { m.avancar(15); m.observar("acariciar"); vistos.push(gatilhoDe(m, t += 1000)); }
    expect(vistos[vistos.length - 1]).toBe("marco");            /* o passo em que evoluiu */
    m.avancar(200); expect(gatilhoDe(m, t += 1000)).not.toBe("reencontro");
    m.observar("acariciar"); expect(gatilhoDe(m, t += REENCONTRO_REAL_MS)).toBe("reencontro");
  });
  test("reencontro pede o jogador sumido de verdade: 3 h de jogo em segundos de relogio nao contam", () => {
    const m = new Motor(21, 7);
    let t = 1e12;
    gatilhoDe(m, t);
    while (m.estagioAtual === "bebe") { m.avancar(15); m.observar("acariciar"); gatilhoDe(m, t += 1000); }
    m.avancar(200); gatilhoDe(m, t += 1000);
    m.observar("acariciar"); expect(gatilhoDe(m, t += 18_000)).toBeNull();   /* tempo de teste: 3 h de jogo em 18 s */
  });
  test("ritmo: no maximo uma fala a cada 2 h; nunca com janela aberta; bebe nao fala", () => {
    expect(podeFalar(new Motor(5, 7))).toBe(false);          /* bebe */
    expect(podeFalar(new Motor(5, 6))).toBe(false);          /* pet v6 */
    const m = crianca();
    while (!podeFalar(m)) { m.avancar(15); if (m.janelaAberta()) m.observar("repreender"); }
    m.falar("marco");
    expect(podeFalar(m)).toBe(false);
    m.avancar(RITMO_MIN); if (m.janelaAberta()) m.observar("elogiar");
    while (m.e.dormindo || m.janelaAberta()) { m.avancar(15); if (m.janelaAberta()) m.observar("elogiar"); }
    expect(podeFalar(m)).toBe(true);
  });
});

describe("assunto e molde", () => {
  test("verdade: o assunto vem da historia; mentira: o molde e a verdade guardada", () => {
    const m = crianca(31);
    m.avancar(TPD);
    const t = m.e.tick;
    const verdade = assuntoDaFala(m, { tipo: "fala", pedido: "historia", inicio: t, prazo: t + 30, falso: false }, []);
    expect(verdade.mentira).toBeNull();
    expect(verdade.historia.length).toBe(1);
    expect(verdade.molde).toMatch(/[.!?]$/);
    const hist = assuntoDaFala(m, { tipo: "fala", pedido: "historia", inicio: t, prazo: t + 30, falso: true }, []);
    expect(hist.mentira).toEqual({ tema: "historia" });
    if (hist.historia.length) {
      const f = hist.historia[0] as { regra: string; dados: Record<string, unknown>; texto: string };
      expect(hist.verdade).toBe(f.texto);
      expect(hist.molde.toLowerCase()).toContain(mentiraDeHistoria(f.regra, f.dados)!.slice(1));
    }
    const est = assuntoDaFala(m, { tipo: "fala", pedido: "estado", inicio: t, prazo: t + 30, falso: true }, []);
    expect(est.mentira).toEqual({ tema: "estado" }); expect(est.verdade).toBeTruthy();
  });
  test("a fala espontanea rejoga igual pelo registro", () => {
    const m = crianca(41);
    for (let k = 0; k < 6; k++) { m.avancar(RITMO_MIN); if (podeFalar(m)) m.falar("reencontro"); if (m.janelaAberta()) m.observar("elogiar"); }
    expect(m.log.some(e => e[1] === "fl")).toBe(true);
    expect(Motor.reproduzir(41, m.log, 7).assinatura()).toBe(m.assinatura());
  });
});
