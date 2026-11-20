/* A fala do assistir no jogo (src/falaAssistir.ts; docs/futuro/fala_do_assistir.md, FA-5 a FA-7): a frase de template por conceito, o limite
   da FA-5, a chave desligada (nada roda, nada no log), a linha do log de apresentacao (FA-6) e o conceito refeito do registro do pet pelo
   replay. O pet e o da v35 (o olhar com o enjoo), com a TV do P0 por "st", nas sementes dos testes. */
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { CATALOGO_ASSISTIR, CELULA_PERTO_DA_TV_JOGO, Motor, ResumoTela, centroDaCelula, decodificarV4, type EventoRegistro } from "../motor/index.ts";
import { CMU_GRANDE } from "../motor/constantes.ts";
import { CONFIG_FALA_ASSISTIR } from "../motor/digibrain/constantes.ts";
import { ligarProduto } from "../src/produto.ts";
import {
  FA, FRASES_ASSISTIR, VERSAO_LOG_ASSISTIR, VERSAO_TEMPLATE_ASSISTIR, comentarioAtual, comentarioDoAssistir, escolherFalaAssistir, fraseAssistir,
  lerLogAssistir, podeComentar, type RegistroAssistir,
} from "../src/falaAssistir.ts";
import { LOG_FALA, lerLog } from "../src/falaLivre.ts";

type Dict = Record<string, any>;
const mapa = new Map<string, string>();
beforeEach(() => {
  mapa.clear();
  vi.stubGlobal("localStorage", { getItem: (k: string) => mapa.get(k) ?? null, setItem: (k: string, v: string) => { mapa.set(k, v); }, removeItem: (k: string) => { mapa.delete(k); } });
  Object.assign(FA, { ligada: false, ultimo: null, ultK: -1, ultSemente: null, ultimoMs: null, ultimoSustoMs: null });
});
afterEach(() => { vi.unstubAllGlobals(); });

const amostra = (h: number, s: number): number[] => [0, 1, 2, 3, 4, 5, 6].map(k => ((h * 7 + k * 3 + (s % 5)) % 11) / 10);
const perto = (): [number, number] => centroDaCelula(CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE);
/** o pet v35 perto da TV, com a TV do P0 mudando a cada hora; `cada(m)` roda a cada tick (o relogio real do teste e 10 s por tick) */
function viver(s: number, horas: number, cada: (m: Motor) => void): Motor {
  const m = ligarProduto(new Motor(s, 35));
  let r = new ResumoTela("tv");
  for (let h = 0; h < horas; h++) {
    if (!m.e.dormindo) m.levarPet(...perto());
    for (let k = 0; k < 30; k++) { const v = r.amostra(amostra(h, s + k)); if (v !== null) m.sentidoTela(v); }
    if (h % 3 === 2) m.observar("alimentar");
    for (let t = 0; t < 60; t++) { m.avancar(1); cada(m); }
  }
  return m;
}
const relogio = (m: Motor): number => m.e.tick * 10_000;

describe("a frase de template e o limite (FA-5, FA-7)", () => {
  test("uma frase por conceito, e a de duvida abaixo do limiar de confianca", () => {
    for (const c of CATALOGO_ASSISTIR) {
      expect(fraseAssistir(c, CONFIG_FALA_ASSISTIR.limiar_confianca)).toBe(FRASES_ASSISTIR[c].certo);
      expect(fraseAssistir(c, CONFIG_FALA_ASSISTIR.limiar_confianca - 1)).toBe(FRASES_ASSISTIR[c].duvida);
      expect(FRASES_ASSISTIR[c].duvida.toLowerCase()).toMatch(/acho/);
    }
    expect(() => fraseAssistir("de_novo" as never, 900)).toThrow(/desconhecido/);
  });
  test("um comentario a cada 5 min, o susto a cada 1 min furando os 5 min", () => {
    const min = 60_000;
    expect(podeComentar("gostei", 0, null, null)).toBe(true);
    expect(podeComentar("gostei", 5 * min - 1, 0, null)).toBe(false);
    expect(podeComentar("gostei", 5 * min, 0, null)).toBe(true);
    expect(podeComentar("susto", 1 * min, 0, null)).toBe(true);           // fura os 5 min
    expect(podeComentar("susto", 1 * min - 1, 0, 0)).toBe(false);
    expect(podeComentar("chato", 4 * min, 3 * min, 3 * min)).toBe(false);  // o susto tambem conta no relogio dos 5 min
  });
});

describe("a chave desligada: o jogo de hoje", () => {
  test("nada roda e nada vai ao log de apresentacao", () => {
    let chamou = 0;
    const m = viver(101, 4, mm => { if (comentarioDoAssistir(mm, relogio(mm)) !== null) chamou++; expect(comentarioAtual(mm)).toBeNull(); });
    expect(chamou).toBe(0);
    expect(mapa.has(LOG_FALA)).toBe(false);
    expect(FA.ultK).toBe(-1);
    expect(m.lab!.motivos.length).toBeGreaterThan(10);
  });
  test("a chave nao muda o pet: o registro e a vida sao os mesmos ligada e desligada", () => {
    const a = viver(202, 6, () => {});
    escolherFalaAssistir(true);
    const b = viver(202, 6, mm => { comentarioDoAssistir(mm, relogio(mm)); });
    expect(b.log).toEqual(a.log);
    expect(b.assinatura()).toBe(a.assinatura());
  });
});

describe("ligada: a linha do log de apresentacao (FA-6) e o replay", () => {
  test("os comentarios respeitam o limite, so saem olhando, e o conceito se refaz do registro do pet pelo replay", () => {
    escolherFalaAssistir(true);
    const ditos: RegistroAssistir[] = [], s = 303;
    const m = viver(s, 30, mm => {
      const r = comentarioDoAssistir(mm, relogio(mm));
      if (r !== null) { ditos.push(r); expect(comentarioAtual(mm)).toBe(r); }
    });
    expect(ditos.length).toBeGreaterThan(0);
    const log = lerLogAssistir();
    expect(log).toEqual(ditos);
    expect(lerLog()).toEqual([]);                                    // a fala livre nao le as linhas do assistir
    for (let i = 0; i < log.length; i++) {
      const r = log[i]!;
      expect([r.versao, r.situacao, r.versao_dec, r.versao_voz, r.modelo, r.semente]).toEqual([VERSAO_LOG_ASSISTIR, "assistir", "dec-v4", VERSAO_TEMPLATE_ASSISTIR, "template", null]);
      expect(r.fala).toBe(fraseAssistir(r.conceito, r.confianca));
      if (i > 0) {
        const dt = (r.t - log[i - 1]!.t) * 10_000;
        if (r.conceito !== "susto") expect(dt).toBeGreaterThanOrEqual(CONFIG_FALA_ASSISTIR.intervalo_comentario_s * 1000);
      }
    }
    /* o replay do registro do pet (sem o log de apresentacao) refaz cada conceito, na mesma decisao */
    const rep = Motor.reproduzir(s, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], 35);
    expect(rep.assinatura()).toBe(m.assinatura());
    const ms = rep.lab!.motivos as Dict[];
    for (const r of log) {
      const d = decodificarV4(ms[r.k]!, r.k ? ms[r.k - 1]! : null, rep.lab!.S);
      expect(d.assistir).not.toBeNull();
      expect(d.assistir!.olhava).toBe(r.olhava);
      expect(d.assistir!.intencao).toBe(r.conceito);
      const c = d.assistir!.conceitos.find(x => x.nome === r.conceito)!;
      expect([c.valor, c.confianca]).toEqual([r.valor, r.confianca]);
    }
    expect(JSON.stringify(m.log)).not.toMatch(/assistir|Gostei|chato/);   // o texto nunca entra no registro do pet
  });
  test("uma linha mal formada do assistir falha alto", () => {
    mapa.set(LOG_FALA, JSON.stringify({ versao: 1, situacao: "assistir", t: 1, k: 1, conceito: "de_novo", fala: "x" }) + "\n");
    expect(() => lerLogAssistir()).toThrow(/invalida/);
  });
});
