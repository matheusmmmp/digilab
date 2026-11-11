/* SOM-UP (docs/TAREFA_V3_SOM_UP.md): os efeitos pelo nome, o teto de copias do mesmo arquivo, os barramentos da musica e dos efeitos, a
   musica pela prioridade de quem pede, o mapa antigo com aviso, o ciclo da musica da ilha e os sons de um passo da luta. Falsos do
   AudioContext, do fetch e do armazenamento. */
import { expect, test } from "vitest";
import { CHAVE_SOM, CHAVE_SOM_VOL_EFEITOS, CHAVE_SOM_VOL_MUSICA, VOL_MUSICA_PADRAO, VOZES_POR_ARQUIVO, criarSom, type Dependencias, type MapaSom } from "../src/som.ts";
import { EFEITOS_SOM, emitirSom, ouvirSom, type InstanteSom } from "../src/somEventos.ts";
import { CICLO_ILHA, ilhaToca } from "../src/somJogo.ts";
import { somDoPassoPoc } from "../src/somLuta.ts";
import type { EventoPoc, LutaPoc } from "../motor/index.ts";

const MAPA: MapaSom = {
  versao: 2, evolucao: "evo.mp3", sem_som: [], formas: {},
  musicas: {
    "2004": { arq: "ILHA", nome: "camp", ini: 0, loopIni: 10, loopFim: 20 }, "2008": { arq: "TREINO", nome: "t", ini: 0, loopIni: 10, loopFim: 20 },
    "101": { arq: "CAMPO", nome: "s1", ini: 0, loopIni: 10, loopFim: 20 }, "1001": { arq: "CHEFE", nome: "b1", ini: 0, loopIni: 10, loopFim: 20 },
    "4004": { arq: "EVO", nome: "EVO", ini: 0, loopIni: 10, loopFim: 20 },
  },
  efeitos: { comer: { arq: "comer.mp3" }, ui_abrir: { arq: "abrir.mp3" } },
  lugares: { ilha: "2004", treino: "2008", nascimento: "3", luta: { campo: "101" }, chefe: ["1001"] },
};
function falsos(mapa: MapaSom = MAPA, salvo: Record<string, string> = {}) {
  const pedidos: string[] = [], tocados: { buffer: unknown; destino: unknown }[] = [], ganhos: { gain: { value: number } }[] = [];
  const loja = new Map(Object.entries(salvo));
  const dep: Dependencias = {
    criarContexto: () => ({
      state: "running", currentTime: 10, destination: { raiz: true }, resume: async () => undefined,
      createGain: () => { const g = { gain: { value: 1 }, connect: () => undefined }; ganhos.push(g); return g; },
      createBufferSource: () => {
        const s = { buffer: null as unknown, destino: null as unknown, loop: false, loopStart: 0, loopEnd: 0, playbackRate: { value: 1 },
          connect(d: unknown) { s.destino = d; }, stop: () => undefined, start() { tocados.push({ buffer: s.buffer, destino: s.destino }); } };
        return s;
      },
      decodeAudioData: async d => ({ duration: 20, nome: new TextDecoder().decode(d) } as { duration: number }),
    }),
    buscar: async url => {
      pedidos.push(url);
      const nome = url.split("/").pop()!;
      return { ok: true, status: 200, json: async () => mapa, arrayBuffer: async () => new TextEncoder().encode(nome).buffer as ArrayBuffer };
    },
    aleatorio: () => 0.5,
    armazenamento: { getItem: k => loja.get(k) ?? null, setItem: (k, v) => { loja.set(k, v); } },
  };
  return { dep, pedidos, tocados, ganhos, loja };
}
const nomeDe = (t: { buffer: unknown }) => (t.buffer as { nome: string }).nome;

test("o efeito pelo nome toca o arquivo do mapa no barramento dos efeitos; desligado nao pede nada", async () => {
  const f = falsos(), som = criarSom(f.dep);
  som.ligar(true);
  await som.efeito("comer");
  expect(f.tocados.map(nomeDe)).toEqual(["comer.mp3"]);
  /* ganhos: o geral, a musica, os efeitos */
  expect(f.tocados[0]!.destino).toBe(f.ganhos[2]);
  const g = falsos(undefined, { [CHAVE_SOM]: "0" }), mudo = criarSom(g.dep);
  await mudo.efeito("comer"); await mudo.pedirMusica("ilha", { lugar: "ilha" });
  expect(g.pedidos).toEqual([]); expect(g.tocados).toEqual([]);
});
test("efeito que o mapa nao tem falha alto; o mapa antigo (sem efeitos nem lugares) avisa uma vez e fica em silencio", async () => {
  const f = falsos(), som = criarSom(f.dep);
  som.ligar(true);
  await expect(som.efeito("medalha")).rejects.toThrow(/medalha/);
  const antigo: MapaSom = { versao: 1, evolucao: "evo.mp3", sem_som: [], formas: {}, musicas: {} };
  const g = falsos(antigo), velho = criarSom(g.dep);
  velho.ligar(true);
  await velho.efeito("comer"); await velho.pedirMusica("ilha", { lugar: "ilha" });
  expect(velho.estado().aviso).toContain("versão antiga");
  expect(g.tocados).toEqual([]);
});
test("no maximo VOZES_POR_ARQUIVO copias do mesmo arquivo tocando juntas", async () => {
  const f = falsos(), som = criarSom(f.dep);
  som.ligar(true);
  for (let i = 0; i < VOZES_POR_ARQUIVO + 3; i++) await som.efeito("comer");
  expect(f.tocados.length).toBe(VOZES_POR_ARQUIVO);
  await som.efeito("ui_abrir");
  expect(nomeDe(f.tocados.at(-1)!)).toBe("abrir.mp3");
});
test("a musica e a do pedido mais forte: evolucao > luta > treino > ilha; largar volta a de baixo, sem recomecar a mesma", async () => {
  const f = falsos(), som = criarSom(f.dep);
  som.ligar(true);
  await som.pedirMusica("ilha", { lugar: "ilha" }); expect(som.musicaAgora()).toBe("2004");
  await som.pedirMusica("ilha", { lugar: "ilha" }); expect(f.tocados.length).toBe(1);
  await som.pedirMusica("treino", { lugar: "treino" }); expect(som.musicaAgora()).toBe("2008");
  await som.pedirMusica("luta", { luta: "campo", chefe: false }); expect(som.musicaAgora()).toBe("101");
  await som.pedirMusica("evolucao", "4004"); expect(som.musicaAgora()).toBe("4004");
  await som.pedirMusica("luta", { luta: "campo", chefe: true }); expect(som.musicaAgora()).toBe("4004");
  await som.pedirMusica("evolucao", null); expect(som.musicaAgora()).toBe("1001");
  await som.pedirMusica("luta", null); await som.pedirMusica("treino", null); expect(som.musicaAgora()).toBe("2004");
  /* a musica vai no barramento da musica */
  expect(f.tocados.at(-1)!.destino).toBe(f.ganhos[1]);
  await som.pedirMusica("ilha", null); expect(som.musicaAgora()).toBeNull();
  await expect(som.pedirMusica("luta", { luta: "lua", chefe: false })).rejects.toThrow(/lua/);
});
test("os volumes da musica e dos efeitos ficam no armazenamento e nos barramentos", () => {
  const f = falsos(), som = criarSom(f.dep);
  expect(som.estado().volMusica).toBe(VOL_MUSICA_PADRAO);
  som.ligar(true); som.volumeMusica(0.2); som.volumeEfeitos(0.7);
  expect(f.loja.get(CHAVE_SOM_VOL_MUSICA)).toBe("0.2"); expect(f.loja.get(CHAVE_SOM_VOL_EFEITOS)).toBe("0.7");
  expect(f.ganhos[1]!.gain.value).toBe(0.2); expect(f.ganhos[2]!.gain.value).toBe(0.7);
  expect(criarSom(f.dep).estado()).toMatchObject({ volMusica: 0.2, volEfeitos: 0.7 });
  expect(() => som.volumeMusica(-1)).toThrow(); expect(() => som.volumeEfeitos(1.5)).toThrow();
});
test("emitirSom: so os efeitos do catalogo; sem ouvinte, nada", () => {
  const ouvidos: InstanteSom[] = [], largar = ouvirSom(i => ouvidos.push(i));
  for (const e of EFEITOS_SOM) emitirSom(e);
  expect(ouvidos.length).toBe(EFEITOS_SOM.length);
  expect(() => emitirSom("buzina" as never)).toThrow(/buzina/);
  largar(); emitirSom("comer"); expect(ouvidos.length).toBe(EFEITOS_SOM.length);
});
test("a musica da ilha: so de dia, com o pet nascido, vivo e acordado, e com o silencio do ciclo", () => {
  const dia = { noite: false, nascendo: 0, morto: false, dormindo: false };
  expect(ilhaToca(dia, 100, 100)).toBe(true);
  expect(ilhaToca(dia, 100 + CICLO_ILHA.tocaS + 1, 100)).toBe(false);
  expect(ilhaToca(dia, 100 + CICLO_ILHA.tocaS + CICLO_ILHA.silencioS + 1, 100)).toBe(true);
  for (const k of ["noite", "morto", "dormindo"] as const) expect(ilhaToca({ ...dia, [k]: true }, 100, 100)).toBe(false);
  expect(ilhaToca({ ...dia, nascendo: 3 }, 100, 100)).toBe(false);
});
test("a luta: o projetil novo toca o golpe de quem atirou (uma vez), a habilidade o golpe dela, o dano o acerto e o fim de quem bateu", () => {
  const ouvidos: InstanteSom[] = [], largar = ouvirSom(i => ouvidos.push(i));
  const pr = { de: { lado: "b" } };
  const L = { projeteis: [pr] } as unknown as LutaPoc;
  const ev = [
    { tipo: "habilidade", u: { lado: "a" } },
    { tipo: "dano", at: { lado: "a" }, hab: true },
    { tipo: "esquiva" },
  ] as unknown as EventoPoc[];
  somDoPassoPoc(L, ev, "sprite_a", "sprite_b");
  somDoPassoPoc(L, [], "sprite_a", "sprite_b");
  largar();
  expect(ouvidos).toEqual([
    { tipo: "golpe", evento: "golpe", sprite: "sprite_b", habilidade: false },
    { tipo: "golpe", evento: "golpe", sprite: "sprite_a", habilidade: true },
    { tipo: "golpe", evento: "acerto", sprite: "sprite_a", habilidade: true },
    { tipo: "golpe", evento: "fim", sprite: "sprite_a", habilidade: true },
  ]);
});
