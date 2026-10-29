/* Som do jogo (UP-SOM): o evento certo da forma, a variacao dentro da faixa, nada toca nem e pedido desligado, o aviso de arquivo
   ausente, o lembrete no armazenamento. AudioContext, fetch e armazenamento falsos. */
import { expect, test } from "vitest";
import { ATRASO_MP3, CHAVE_SOM, CHAVE_SOM_VOLUME, DIVISOR_VARIACAO, criarSom, type Dependencias, type MapaSom } from "../src/som.ts";

const MAPA: MapaSom = {
  versao: 1, evolucao: "evo.mp3", sem_som: [],
  musicas: { "4004": { arq: "EVO", nome: "EVO", ini: 0, loopIni: 1000, loopFim: 2000 } },
  formas: {
    forma_a: { digimon: "A", ataque: [
      { quando: "golpe", atraso: 0.1, variacao: 0.3, arquivo: "a_golpe.mp3" }, { quando: "acerto", atraso: 0, variacao: null, arquivo: "a_hit.mp3" }], habilidade: [
      { quando: "golpe", atraso: 0, variacao: null, arquivo: "a_hab.mp3" }] },
  },
};
function falsos(opc: { ausentes?: string[]; salvo?: Record<string, string>; aleatorio?: number } = {}) {
  const pedidos: string[] = [], tocados: { buffer: unknown; taxa: number; quando: number | undefined }[] = [];
  const loja = new Map(Object.entries(opc.salvo ?? {}));
  const dep: Dependencias = {
    criarContexto: () => ({
      state: "running", currentTime: 10, destination: {}, resume: async () => undefined,
      createGain: () => ({ gain: { value: 1 }, connect: () => undefined }),
      createBufferSource: () => {
        const s = { buffer: null as unknown, loop: false, loopStart: 0, loopEnd: 0, playbackRate: { value: 1 }, connect: () => undefined, stop: () => undefined,
          start(q?: number) { tocados.push({ buffer: s.buffer, taxa: s.playbackRate.value, quando: q }); } };
        return s;
      },
      decodeAudioData: async d => ({ duration: 20, nome: new TextDecoder().decode(d) } as { duration: number }),
    }),
    buscar: async url => {
      pedidos.push(url);
      const nome = url.split("/").pop()!;
      if (opc.ausentes?.includes(nome)) return { ok: false, status: 404, json: async () => ({}), arrayBuffer: async () => new ArrayBuffer(0) };
      return { ok: true, status: 200, json: async () => MAPA, arrayBuffer: async () => new TextEncoder().encode(nome).buffer as ArrayBuffer };
    },
    aleatorio: () => opc.aleatorio ?? 0.5,
    armazenamento: { getItem: k => loja.get(k) ?? null, setItem: (k, v) => { loja.set(k, v); } },
  };
  return { dep, pedidos, tocados, loja };
}
const nomeDe = (t: { buffer: unknown }) => (t.buffer as { nome: string }).nome;

test("desligado (padrao): nao toca nem pede arquivo", async () => {
  const { dep, pedidos, tocados } = falsos(), som = criarSom(dep);
  expect(som.estado().ligado).toBe(false);
  await som.tocar("golpe", "forma_a"); await som.tocarEvolucao(); await som.tocarMusica("4004");
  expect(pedidos).toEqual([]); expect(tocados).toEqual([]);
});
test("ligado: o golpe da forma toca o arquivo do mapa, com o atraso do script", async () => {
  const { dep, tocados } = falsos(), som = criarSom(dep);
  som.ligar(true);
  await som.tocar("golpe", "forma_a");
  expect(tocados.map(nomeDe)).toEqual(["a_golpe.mp3"]);
  expect(tocados[0].quando).toBeCloseTo(10.1, 9);
  await som.tocar("acerto", "forma_a");
  expect(nomeDe(tocados[1])).toBe("a_hit.mp3");
});
test("habilidade usa o conjunto de habilidade", async () => {
  const { dep, tocados } = falsos(), som = criarSom(dep);
  som.ligar(true);
  await som.tocar("golpe", "forma_a", true);
  expect(tocados.map(nomeDe)).toEqual(["a_hab.mp3"]);
});
test("variacao como tom, dentro de +-variacao/3", async () => {
  for (const [r, esperado] of [[0, 1 - 0.3 / DIVISOR_VARIACAO], [1, 1 + 0.3 / DIVISOR_VARIACAO], [0.5, 1]] as const) {
    const { dep, tocados } = falsos({ aleatorio: r }), som = criarSom(dep);
    som.ligar(true); await som.tocar("golpe", "forma_a");
    expect(tocados[0].taxa).toBeCloseTo(esperado, 12);
  }
});
test("forma ou evento sem som e silencio, sem erro", async () => {
  const { dep, tocados } = falsos(), som = criarSom(dep);
  som.ligar(true);
  await som.tocar("golpe", "forma_que_nao_existe"); await som.tocar("fim", "forma_a");
  expect(tocados).toEqual([]); expect(som.estado().aviso).toBeNull();
});
test("arquivo ausente com o som ligado: um aviso, uma vez, e o resto segue", async () => {
  const { dep, tocados } = falsos({ ausentes: ["a_golpe.mp3", "a_hit.mp3"] }), som = criarSom(dep);
  let avisos = 0; som.ouvir(() => { if (som.estado().aviso) avisos++; });
  som.ligar(true);
  await som.tocar("golpe", "forma_a"); await som.tocar("acerto", "forma_a");
  expect(som.estado().aviso).toContain("a_golpe.mp3");
  expect(avisos).toBe(1);
  expect(tocados).toEqual([]);
  await som.tocar("golpe", "forma_a", true);
  expect(tocados.map(nomeDe)).toEqual(["a_hab.mp3"]);
});
test("mapa ausente com o som ligado: aviso visivel", async () => {
  const { dep } = falsos({ ausentes: ["mapa.json"] }), som = criarSom(dep);
  som.ligar(true); await som.tocar("golpe", "forma_a");
  expect(som.estado().aviso).toContain("mapa");
});
test("liga/desliga e volume ficam no armazenamento e voltam", () => {
  const { dep, loja } = falsos(), som = criarSom(dep);
  som.ligar(true); som.volume(0.25);
  expect(loja.get(CHAVE_SOM)).toBe("1"); expect(loja.get(CHAVE_SOM_VOLUME)).toBe("0.25");
  const outro = criarSom(dep);
  expect(outro.estado()).toMatchObject({ ligado: true, volume: 0.25 });
  expect(() => som.volume(2)).toThrow();
  som.ligar(false);
  expect(criarSom(dep).estado().ligado).toBe(false);
});
test("a evolucao toca o sfx e a musica usa inicio e laco em amostras", async () => {
  const { dep, tocados } = falsos(), som = criarSom(dep);
  som.ligar(true);
  await som.tocarEvolucao(0); expect(nomeDe(tocados[0])).toBe("evo.mp3");
  await som.tocarMusica("4004"); expect(nomeDe(tocados[1])).toBe("EVO.mp3");
  expect(ATRASO_MP3).toBe(1105);
});
