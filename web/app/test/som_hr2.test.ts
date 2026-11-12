/* HABITAT_REACOES, HR2 e HR3 (docs/PLANO_V3_HABITAT_REACOES.md): a voz do pet (o tom pela especie, pelo estagio e pelo humor; a pausa entre duas
   falas), o bipe sintetizado do chamado, o mapa de antes sem os efeitos do cuidado (aviso, sem falha) e os sons que cada momento emite. Falsos do
   AudioContext, do fetch e do armazenamento, como em som_up.test.ts. */
import { beforeEach, expect, test } from "vitest";
import { BIPES, criarSom, type Dependencias, type MapaSom } from "../src/som.ts";
import { ouvirSom, type InstanteSom } from "../src/somEventos.ts";
import { VOZ, esquecerVoz, podeFalar, taxaDaVoz } from "../src/somVoz.ts";
import { esquecerMomentos, momentoAgora, momentoDoDono, tentouPegarDormindo, vigiarMomentos, type EntradaMomentos } from "../src/telas/pet/momentos.ts";
import { esquecerReacaoRosto, registrarAcaoDono } from "../src/telas/pet/reacao.ts";

const MAPA: MapaSom = {
  versao: 2, evolucao: "evo.mp3", sem_som: [], formas: {}, musicas: {},
  efeitos: { voz: { arq: "voz.mp3" }, cuidado_limpar: { arq: "agua.mp3" } },
  lugares: { ilha: "2004", treino: "2008", nascimento: "3", luta: {}, chefe: [] },
};
function falsos(mapa: MapaSom = MAPA, comOscilador = true) {
  const tocados: { nome: string; taxa: number }[] = [], osc: { hz: number; ini: number; fim: number }[] = [];
  const dep: Dependencias = {
    criarContexto: () => ({
      state: "running", currentTime: 10, destination: {}, resume: async () => undefined,
      createGain: () => ({ gain: { value: 1 }, connect: () => undefined }),
      createBufferSource: () => {
        const s = { buffer: null as unknown, loop: false, loopStart: 0, loopEnd: 0, playbackRate: { value: 1 }, connect: () => undefined, stop: () => undefined,
          start() { tocados.push({ nome: (s.buffer as { nome: string }).nome, taxa: s.playbackRate.value }); } };
        return s;
      },
      ...(comOscilador ? {
        createOscillator: () => {
          const o = { type: "", frequency: { value: 0 }, ini: 0, connect: () => undefined, start(t?: number) { o.ini = t ?? 0; }, stop(t?: number) { osc.push({ hz: o.frequency.value, ini: o.ini, fim: t ?? 0 }); } };
          return o;
        },
      } : {}),
      decodeAudioData: async d => ({ duration: 1, nome: new TextDecoder().decode(d) } as { duration: number }),
    }),
    buscar: async url => ({ ok: true, status: 200, json: async () => mapa, arrayBuffer: async () => new TextEncoder().encode(url.split("/").pop()!).buffer as ArrayBuffer }),
    aleatorio: () => 0.5,
    armazenamento: null,
  };
  return { dep, tocados, osc };
}

beforeEach(() => { esquecerVoz(); esquecerMomentos(); esquecerReacaoRosto(); });

test("o tom da voz: humor x especie x estagio, dentro dos limites; especie ou estagio desconhecido falha alto", () => {
  expect(taxaDaVoz("contente", "brasa", "adolescente")).toBeCloseTo(VOZ.humor.contente, 9);
  expect(taxaDaVoz("contente", "brasa", "bebe")).toBeGreaterThan(taxaDaVoz("contente", "brasa", "adulto"));
  expect(taxaDaVoz("susto", "cirro", "bebe")).toBe(VOZ.max);
  expect(taxaDaVoz("bocejo", "ferrugem", "mega")).toBeGreaterThanOrEqual(VOZ.min);
  expect(() => taxaDaVoz("contente", "lobo", "bebe")).toThrow(/especie/);
  expect(() => taxaDaVoz("contente", "brasa", "velho")).toThrow(/estagio/);
});

test("a voz espontanea espera a pausa longa; a resposta ao dono, a curta", () => {
  esquecerVoz();
  expect(VOZ.pausaEspontaneaMs).toBeGreaterThan(VOZ.pausaMs);
  expect(podeFalar(1000, true)).toBe(true);
  expect(podeFalar(1000 + VOZ.pausaMs, true)).toBe(false);          /* o pet mudando de acao sozinho nao fala de novo tao cedo */
  expect(podeFalar(1000 + VOZ.pausaMs)).toBe(true);                 /* mas responde ao gesto do dono */
  expect(podeFalar(1000 + VOZ.pausaMs + VOZ.pausaEspontaneaMs - 1, true)).toBe(false);
  expect(podeFalar(1000 + VOZ.pausaMs + VOZ.pausaEspontaneaMs, true)).toBe(true);
  esquecerVoz();
});

test("a pausa entre duas falas: so uma a cada VOZ.pausaMs", () => {
  expect(podeFalar(1000)).toBe(true);
  expect(podeFalar(1000 + VOZ.pausaMs - 1)).toBe(false);
  expect(podeFalar(1000 + VOZ.pausaMs)).toBe(true);
});

test("a voz toca o arquivo da voz com o tom pedido", async () => {
  const f = falsos(), som = criarSom(f.dep);
  som.ligar(true);
  await som.voz(1.3);
  expect(f.tocados).toEqual([{ nome: "voz.mp3", taxa: 1.3 }]);
  await expect(som.efeito("voz", 0, 0)).rejects.toThrow(/taxa/);
});

test("o bipe do chamado: os toques do roteiro, no tempo do contexto; sem oscilador ou desligado, nada", () => {
  const f = falsos(), som = criarSom(f.dep);
  som.ligar(true);
  som.bipe("abre");
  expect(f.osc.map(o => o.hz)).toEqual(BIPES.abre.map(b => b[0]));
  expect(f.osc[1]!.ini).toBeCloseTo(10 + BIPES.abre[1]![1], 9);
  som.bipe("perdido");
  expect(f.osc.slice(3).map(o => o.hz)).toEqual([1200, 800, 500]);
  const g = falsos(MAPA, false), semOsc = criarSom(g.dep);
  semOsc.ligar(true); semOsc.bipe("urgente");
  expect(g.osc).toEqual([]);
  som.ligar(false); som.bipe("abre");
  expect(f.osc.length).toBe(6);
});

test("o mapa de antes da HR2 (sem os efeitos do cuidado): avisa uma vez e fica em silencio, sem falhar", async () => {
  const f = falsos({ ...MAPA, efeitos: { comer: { arq: "comer.mp3" } } }), som = criarSom(f.dep);
  som.ligar(true);
  await som.efeito("cuidado_toque");
  await som.voz(1);
  expect(f.tocados).toEqual([]);
  expect(som.estado().aviso).toMatch(/versão antiga/);
});

/* ------------------------------------------------------------------ o que cada momento emite */
const BASE: EntradaMomentos = { chave: "p", nascendo: 0, dormindo: false, morto: false, acao: "ocioso", abertos: [], urgente: false, atendidos: 0, consumos: 0, ultimo: null, vazio: null };
const em = (o: Partial<EntradaMomentos> = {}): EntradaMomentos => ({ ...BASE, ...o });
function ouvindo(): { ouvidos: string[]; parar: () => void } {
  const ouvidos: string[] = [];
  const parar = ouvirSom((i: InstanteSom) => { ouvidos.push(i.tipo === "efeito" ? i.efeito : i.tipo === "voz" ? "voz:" + i.humor : i.tipo === "bipe" ? "bipe:" + i.bipe : i.tipo); });
  return { ouvidos, parar };
}

test("o chamado: abre (bipe e voz chamando), aperta (bipe urgente), perdido (bipe descendo) e atendido (o som do atendido)", () => {
  const o = ouvindo();
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ abertos: ["fome"] }), 10);
  vigiarMomentos(em({ abertos: ["fome"], urgente: true }), 20);
  vigiarMomentos(em({ abertos: [] }), 30);
  vigiarMomentos(em({ abertos: ["higiene"] }), 40);
  vigiarMomentos(em({ abertos: [], atendidos: 1 }), 50);
  o.parar();
  expect(o.ouvidos).toEqual(["bipe:abre", "voz:chamando", "bipe:urgente", "voz:chamando", "bipe:perdido", "bipe:abre", "voz:chamando", "chamado_atendido"]);
});

test("a casca, o sono, a fruta e a acao do motor emitem o som e a voz do plano", () => {
  const o = ouvindo();
  vigiarMomentos(em({ nascendo: 2 }), 0);
  vigiarMomentos(em(), 10);                                                          // nasceu
  vigiarMomentos(em({ dormindo: true }), 20);                                        // dormiu
  vigiarMomentos(em(), 30);                                                          // acordou
  vigiarMomentos(em({ consumos: 1, ultimo: { tipo: "maca", situacao: "podre", fome_antes: .5, fome_depois: .5 } }), 40);
  vigiarMomentos(em({ consumos: 2, ultimo: { tipo: "maca", situacao: "madura", fome_antes: .5, fome_depois: .7 } }), 50);
  vigiarMomentos(em({ consumos: 2, acao: "emburrar" }), 60);
  o.parar();
  expect(o.ouvidos).toEqual(["nascer", "voz:bocejo", "voz:bocejo", "fruta_podre", "voz:resmungo", "fruta_boa", "voz:resmungo"]);
});

test("o momento que comeca da a voz contente; o do comer, tambem o fim do comer", () => {
  const o = ouvindo();
  vigiarMomentos(em(), 0);
  vigiarMomentos(em({ consumos: 1, ultimo: { tipo: "racao", situacao: "madura", fome_antes: .1, fome_depois: .6 } }), 0);
  momentoAgora(0, true, () => 500);
  o.parar();
  expect(o.ouvidos).toEqual(["comer_fim", "voz:contente"]);
});

test("os gestos do dono: o som na hora (limpar, tratar, carinho, recusa); o tapa e a recusa da comida dao a voz", () => {
  const o = ouvindo();
  vigiarMomentos(em(), 0);
  momentoDoDono("limpar", 0); momentoDoDono("tratar_lesao", 0); momentoDoDono("acariciar", 0); momentoDoDono("alimentar", 0);
  tentouPegarDormindo(0);
  registrarAcaoDono("tapa", 0, .5);
  registrarAcaoDono("alimentar", 0, .9);
  registrarAcaoDono("alimentar", 0, .2);
  o.parar();
  expect(o.ouvidos).toEqual(["cuidado_limpar", "tratar", "cuidado_toque", "cuidado_recusa", "voz:choro", "cuidado_recusa", "voz:resmungo"]);
});
