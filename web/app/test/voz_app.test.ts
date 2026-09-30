/* Voz propria no app (src/voz.ts): gatilhos, ritmo, assunto da fala e a queda sem o servidor (o molde). A fala entra no
   registro do pet pelo evento "f" e rejoga igual. */
import { describe, expect, test } from "vitest";
import { Motor, TPD, mentiraDeHistoria } from "../motor/index.ts";
import { RITMO_MIN, assuntoDaFala, gatilhoDe, podeFalar } from "../src/voz.ts";

/** pet v5 criado e levado ate a crianca, com o dono agindo a cada 15 min */
function crianca(semente = 11): Motor {
  const m = new Motor(semente, 5);
  while (m.estagioAtual === "bebe") { m.avancar(15); m.observar(m.e.fome > .5 ? "alimentar" : "acariciar"); }
  return m;
}

describe("gatilhos e ritmo", () => {
  test("ao carregar so observa; evolucao dispara marco; reencontro depois de 3 h", () => {
    const m = new Motor(21, 5);
    expect(gatilhoDe(m)).toBeNull();                           /* primeira vez: so olha */
    const vistos: (string | null)[] = [];
    while (m.estagioAtual === "bebe") { m.avancar(15); m.observar("acariciar"); vistos.push(gatilhoDe(m)); }
    expect(vistos[vistos.length - 1]).toBe("marco");            /* o passo em que evoluiu */
    m.avancar(200); expect(gatilhoDe(m)).not.toBe("reencontro");
    m.observar("acariciar"); expect(gatilhoDe(m)).toBe("reencontro");
  });
  test("ritmo: no maximo uma fala a cada 2 h; nunca com janela aberta; bebe nao fala", () => {
    expect(podeFalar(new Motor(5, 5))).toBe(false);          /* bebe */
    expect(podeFalar(new Motor(5, 4))).toBe(false);          /* pet v4 */
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
    expect(m.log.some(e => e[1] === "f")).toBe(true);
    expect(Motor.reproduzir(41, m.log, 5).assinatura()).toBe(m.assinatura());
  });
});
