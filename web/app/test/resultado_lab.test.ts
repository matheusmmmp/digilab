/* O resultado da decisao anterior no painel do modular (CADEIA, etapa 3, PR-C da auditoria): `resultadoAnterior` le o `consequencia` que o M-ADAPT
   grava no motivo ao fechar, e `textoResultado` o diz numa linha. No cenario do lugar lembrado (o mesmo de cenario_lugar_lembrado.test.ts), o
   treino tem um resultado "comeu racao; o lugar ficou na memoria", e a fome sem comida tem "chegou e nao havia comida; a visita vazia ficou na
   memoria". So leitura: a assinatura nao muda. */
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/motor.ts";
import { TPD } from "../motor/constantes.ts";
import { resultadoAnterior, type ResultadoLab } from "../motor/index.ts";
import { textoResultado } from "../src/componentes/DigiBrainLab.tsx";

const P: readonly [number, number] = [168, 248];

describe("o resultado da decisao anterior", () => {
  test("no cenario do lugar lembrado: o consumo no treino e a visita vazia depois, cada um com o que ficou na memoria", () => {
    const m = new Motor(101);
    m.trocarCerebro("modular");
    const vistos: ResultadoLab[] = [];
    for (let p = 0; p < Math.round(2 * TPD / 30); p++) {
      m.avancar(30);
      if (m.e.fome < .6 && m.mundo!.comidas.size === 0) m.deixarComida("racao", P[0], P[1]);
      if (m.e.sujeira >= 2) m.observar("limpar");
      const r = resultadoAnterior(m.lab!); if (r) vistos.push(r);
    }
    const assinatura = m.assinatura();
    for (let i = 0; i < 200; i++) { m.avancar(15); const r = resultadoAnterior(m.lab!); if (r) vistos.push(r); }
    const consumo = vistos.find(r => r.memoria === "consumo"), visita = vistos.find(r => r.memoria === "visita");
    expect(consumo, "um resultado de consumo no treino").toBeDefined();
    expect(consumo!.comeu?.tipo).toBe("racao");
    expect(textoResultado(consumo!)).toMatch(/comeu ração; .*o lugar ficou na memória/);
    expect(visita, "um resultado de visita vazia na fome sem comida").toBeDefined();
    expect(visita!.escolha[1]).toBe("ponto");
    expect(visita!.chegou).toBe(true);
    expect(textoResultado(visita!)).toMatch(/chegou e não havia comida; .*a visita vazia ficou na memória/);
    /* so leitura: ler o resultado nao muda a vida */
    const outra = new Motor(101);
    outra.trocarCerebro("modular");
    for (let p = 0; p < Math.round(2 * TPD / 30); p++) {
      outra.avancar(30);
      if (outra.e.fome < .6 && outra.mundo!.comidas.size === 0) outra.deixarComida("racao", P[0], P[1]);
      if (outra.e.sujeira >= 2) outra.observar("limpar");
    }
    expect(outra.assinatura()).toBe(assinatura);
  });
  test("o texto de cada caso", () => {
    const base: ResultadoLab = { k: 3, escolha: ["comer", "comida", 7], comeu: null, chegou: null, efeito: "igual", memoria: null, aprendeu: false };
    expect(textoResultado({ ...base, comeu: { tipo: "a", situacao: "podre" }, efeito: "piorou", aprendeu: true }))
      .toBe("Comer a comida à vista; comeu uma fruta podre; o corpo piorou; o hábito aprendeu.");
    expect(textoResultado({ ...base, escolha: ["explorar", "vagar", null], chegou: false })).toBe("Explorar vagando; não chegou.");
    expect(textoResultado({ ...base, escolha: ["dormir", null, null] })).toBe("Dormir.");
  });
  test("antes de duas decisoes, nada", () => {
    const m = new Motor(101);
    m.trocarCerebro("modular");
    expect(resultadoAnterior(m.lab!)).toBeNull();
  });
});
