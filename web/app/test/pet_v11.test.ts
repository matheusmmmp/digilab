/* O pet v11 no Motor (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 4 parte 3b): um ovo novo e v11 e joga alguns dias com um dono de roteiro
   fixo, com cuidado, carinho, tapa, treino, medalha e lutas. Confere:
     - o cerebro A decide e aprende pelo corpo (o laco do corpo por tick), e o estado do pet e o do laco;
     - a vontade do cerebro A chega ao desejo e ao vinculo B;
     - a evolucao usa o carater do v11 (caraterV11, a escala e o deslocamento proprios);
     - as camadas que saem (a educacao, a mentira e a obediencia) nao existem nele, e o elogio, a bronca, o petisco e o banheiro falham
       alto; o tratar so cura;
     - o replay do registro da a mesma vida, e o mesmo pet guardado e reaberto tambem. */
import { describe, expect, test } from "vitest";
import { TPD, VERSAO_PET } from "../motor/constantes.ts";
import { caraterPrevisto, caraterV11, linhaDoCarater } from "../motor/carater.ts";
import { Motor } from "../motor/motor.ts";
import type { AcaoDono } from "../motor/tipos.ts";

/** um dono de roteiro: a cada meia hora cuida do que esta baixo, faz carinho de vez em quando e da um tapa a cada quatro horas; treina e
    luta no Rookie; libera a medalha do Champion */
function viverDias(m: Motor, dias: number): AcaoDono[] {
  const feitas: AcaoDono[] = [];
  const fazer = (a: AcaoDono) => { m.observar(a); feitas.push(a); };
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e;
    if (e.fome < .5) fazer("alimentar");
    if (e.sujeira >= 2) fazer("limpar");
    if (e.humor < .5 && !e.dormindo) fazer("brincar");
    if (p % 5 === 0) fazer("acariciar");
    if (p % 8 === 7) fazer("tapa");
    if (m.lesionadoDesde !== null) fazer("tratar_lesao");
    if (m.estagioAtual === "crianca" && m.medalhas === 0) m.liberar(1);
    if ((m.estagioAtual === "crianca" || m.estagioAtual === "adolescente") && m.treino.podeTocar(m.e.tick) && p % 3 === 0) m.treinar("levantar_pedra");
    if (m.estagioAtual === "adolescente" && p % 6 === 0) m.lutar("aleatorio", 1000 + p);
  }
  return feitas;
}

describe("o pet v11 no Motor", () => {
  test("o pet v11: o cerebro A e o laco do corpo, sem educacao, mentira nem obediencia (os ovos novos sao v13: o v12 com a luta em tempo real)", () => {
    expect(VERSAO_PET).toBe(13);
    const m = new Motor(4242, 11);
    expect(m.versao).toBe(11);
    expect(m.cerebro).not.toBeNull();
    expect(m.e).toBe(m.v11!.laco.estado);
    expect([m.temEducacao, m.temVozPropria, m.disciplina, m.honestidade(), m.chanceMentira()]).toEqual([false, false, 0, 1, 0]);
    for (const a of ["elogiar", "repreender", "petisco", "levar_ao_banheiro"] as AcaoDono[]) expect(() => m.observar(a)).toThrow(/v11/);
    expect(() => m.falar("acordou")).toThrow(/v11/);
    expect(m.log).toEqual([]);
  });

  test("alguns dias: decide pelo cerebro, aprende com o corpo, tem vontade, evolui pelo carater do v11, e o replay da a mesma vida", () => {
    const m = new Motor(4242, 11), feitas = viverDias(m, 4);
    expect(m.e).toBe(m.v11!.laco.estado);
    /* o cerebro decidiu cada decisao do pet e aprendeu: pesos fora do prior, carinhos e tapas creditados */
    const c = m.cerebro!;
    expect(c.motivos.length).toBe(m.nDecisoes);
    expect(m.nDecisoes).toBeGreaterThan(300);
    expect(c.desvioMaximo()).toBeGreaterThan(0);
    expect(feitas.filter(a => a === "tapa").length).toBeGreaterThan(0);
    expect(m.v11!.laco.mudancas).toBe(feitas.filter(a => a === "acariciar").length);
    /* a vontade do cerebro A chega ao desejo e ao vinculo B */
    expect(m.dz.vontades).toBeGreaterThan(0);
    expect(m.vinc.n).toBeGreaterThan(0);
    expect(m.vinc.pedidos).toEqual([]);
    expect(m.vinc.situacao).toMatch(/^[01]{3}$/);
    /* sem educacao, sem obediencia */
    expect([m.janelaAberta(), m.edu.disciplina, m.obed.recusas]).toEqual([null, 0, 0]);
    /* evoluiu ate o Champion, com a linha do carater do v11 */
    const ev = m.evolucoes.find(x => x.estagio === "adolescente")!;
    expect(ev).toBeDefined();
    expect(ev.linha).toBe(linhaDoCarater(ev.carater!));
    expect(Object.values(ev.carater!).every(v => v >= -1 && v <= 1)).toBe(true);
    /* a previsao da aba Evolucao e o carater do cerebro A */
    expect(caraterPrevisto(m, "adulto")).toStrictEqual(caraterV11(c, "adulto"));
    /* o replay do registro da a mesma vida */
    const r = Motor.reproduzir(m.semente, m.log, m.versao);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(r.cerebro!.estadoInterno()).toStrictEqual(c.estadoInterno());
  });

  test("o carater da evolucao e o do cerebro no tick da evolucao", () => {
    const m = new Motor(777, 11);
    let carEsperado = null;
    for (let p = 0; p < 5000 && !m.evolucoes.some(x => x.estagio === "adolescente"); p++) {
      if (m.estagioAtual === "crianca" && m.medalhas === 0) m.liberar(1);
      if (m.e.fome < .5) m.observar("alimentar");
      const falta = m.estagioAtual === "crianca" ? m.requisitosEvolucao()!.falta : Infinity;
      m.avancar(falta > 30 ? 30 : 1);
      /* evoluiu no ultimo tick deste passo de um tick: nada mexeu no cerebro depois da medida */
      if (falta <= 30 && m.evolucoes.some(x => x.estagio === "adolescente")) carEsperado = caraterV11(m.cerebro!, "adolescente");
    }
    const ev = m.evolucoes.find(x => x.estagio === "adolescente")!;
    expect(ev).toBeDefined();
    expect(carEsperado).not.toBeNull();
    expect(ev.carater).toStrictEqual(carEsperado);
  });

  test("o tratar so cura: nao e contato e nao passa pelo corpo", () => {
    const m = new Motor(99, 11);
    m.avancar(30);
    m.lesionadoDesde = m.e.tick;
    const antes = { ...m.e }, corpo = JSON.stringify(m.v11!.laco.corpo.paraDict());
    m.observar("tratar_lesao");
    expect(m.lesionadoDesde).toBeNull();
    expect(m.e).toEqual(antes);
    expect(JSON.stringify(m.v11!.laco.corpo.paraDict())).toBe(corpo);
  });

  test("os pets v10 seguem iguais: com o Bandit, a educacao e o elogio", () => {
    const m = new Motor(4242, 10);
    expect([m.v11, m.cerebro, m.temEducacao, m.temVozPropria]).toEqual([null, null, true, true]);
    m.avancar(60); m.observar("elogiar"); m.observar("petisco");
    expect(() => m.observar("tapa")).toThrow();
  });
});
