/* Som do jogo (TAREFA_V2_UP_SOM): Web Audio do navegador, sem biblioteca. Sons e musicas do Digimon UP (Bandai; com o credito,
   autorizados pelo Matheus: docs/UI_GUIDELINES.md, secao 5.1) ficam FORA do repositorio, em D:\Trab\digilab\Assets\sons, com o
   mapa.json (chave de sprite -> eventos) gerado por Assets\gerar_sons_up.py. Desligado por padrao: desligado, nada e pedido nem tocado.
   Liga/desliga e volume ficam no localStorage do app (nao no save do pet). So apresentacao: nada daqui entra no motor, no log
   ou no save, e a variacao do som usa o Math.random do app, nunca a RNG do motor. A logica e a do bloco "sons do jogo" da arena do
   prototipo (eventos do script de batalha com atraso e variacao), reescrita. */
import { useSyncExternalStore } from "react";
import { CHAVE } from "./save.ts";

export const CHAVE_SOM = CHAVE + "-som";
export const CHAVE_SOM_VOLUME = CHAVE + "-som-volume";
/** a mesma convencao do atlas: relativo a pagina em /v1/web/dist/ (no servidor local cai em /Assets/sons/) */
export const SONS_URL = "../../../Assets/sons/";
/** volume padrao ao ligar pela primeira vez (PROPOSTO, SEM FONTE) */
export const VOLUME_PADRAO = 0.6;
/** a variacao do script e aplicada como tom de ate +-variacao/3, como na arena do prototipo (PROPOSTO: o levantamento nao sabe se
    o jogo original varia tom ou volume; SEM FONTE) */
export const DIVISOR_VARIACAO = 3;
/** amostras de silencio que o codificador LAME poe no comeco do MP3 e taxa das posicoes de loop das musicas (evo/index.html) */
export const ATRASO_MP3 = 1105;
export const HZ_MUSICA = 44100;
/** a queda do sfx de evolucao cai na revelacao: o som tem 17,9 s e a luz engole o Digimon aos 15,45 s (evo/index.html) */
export const SFX_QUEDA = 15.45;

export type EventoSom = "golpe" | "acerto" | "fim";
export interface EventoMapa { quando: EventoSom; atraso: number; variacao: number | null; arquivo: string }
export interface FormaSom { digimon: string; ataque: EventoMapa[]; habilidade: EventoMapa[] }
export interface MusicaSom { arq: string; nome: string; ini: number; loopIni: number; loopFim: number }
export interface MapaSom { versao: number; evolucao: string; musicas: Record<string, MusicaSom>; formas: Record<string, FormaSom>; sem_som: { forma: string; digimon: string }[] }

/* o minimo da Web Audio que o modulo usa (o teste injeta um falso) */
export interface NoAudio { connect(destino: unknown): unknown }
export interface FonteAudio extends NoAudio {
  buffer: unknown; loop: boolean; loopStart: number; loopEnd: number; playbackRate: { value: number };
  start(quando?: number, deslocamento?: number): void; stop(): void;
}
export interface GanhoAudio extends NoAudio { gain: { value: number } }
export interface ContextoAudio {
  state: string; currentTime: number; destination: unknown;
  createGain(): GanhoAudio; createBufferSource(): FonteAudio;
  decodeAudioData(dados: ArrayBuffer): Promise<{ duration: number }>; resume(): Promise<void>;
}
export interface Dependencias {
  criarContexto: () => ContextoAudio;
  buscar: (url: string) => Promise<{ ok: boolean; status: number; json(): Promise<unknown>; arrayBuffer(): Promise<ArrayBuffer> }>;
  aleatorio: () => number;
  armazenamento: { getItem(k: string): string | null; setItem(k: string, v: string): void } | null;
}
export interface EstadoSom { ligado: boolean; volume: number; aviso: string | null }

const depsPadrao = (): Dependencias => ({
  criarContexto: () => new (window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)() as unknown as ContextoAudio,
  buscar: url => fetch(url),
  aleatorio: Math.random,
  armazenamento: (() => { try { return localStorage; } catch { return null; } })(),
});

/** um sistema de som; o jogo usa a instancia SOM, o teste cria a dele com dependencias falsas */
export function criarSom(dep: Dependencias, base = SONS_URL) {
  const ouvintes = new Set<() => void>();
  let ctx: ContextoAudio | null = null, ganho: GanhoAudio | null = null, mapa: Promise<MapaSom | null> | null = null;
  const buffers = new Map<string, Promise<{ duration: number } | null>>();
  let musica: FonteAudio | null = null, sfx: FonteAudio | null = null, ordemMus = 0, ordemSfx = 0;

  const ler = (k: string): string | null => { try { return dep.armazenamento?.getItem(k) ?? null; } catch { return null; } };
  const gravar = (k: string, v: string): void => { try { dep.armazenamento?.setItem(k, v); } catch { /* preferencia de tela */ } };
  /* o que estava lembrado: ligado so com "1"; volume so se for numero entre 0 e 1 */
  const salvoVol = ler(CHAVE_SOM_VOLUME), v0 = Number(salvoVol);
  let estado: EstadoSom = {
    ligado: ler(CHAVE_SOM) === "1", volume: salvoVol !== null && Number.isFinite(v0) && v0 >= 0 && v0 <= 1 ? v0 : VOLUME_PADRAO, aviso: null,
  };
  const mudar = (p: Partial<EstadoSom>): void => { estado = { ...estado, ...p }; for (const o of ouvintes) o(); };

  /** falha uma vez so: o aviso fica visivel e a tela segue (nada de falha calada) */
  const avisar = (msg: string): void => { if (estado.aviso === null) { console.error(msg); mudar({ aviso: msg }); } };

  const contexto = (): ContextoAudio => {
    if (!ctx) {
      ctx = dep.criarContexto(); ganho = ctx.createGain(); ganho.gain.value = estado.volume; ganho.connect(ctx.destination);
    }
    if (ctx.state === "suspended") void ctx.resume();
    return ctx;
  };
  const carregarMapa = (): Promise<MapaSom | null> => {
    if (!mapa) {
      mapa = dep.buscar(base + "mapa.json").then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() as Promise<MapaSom>; })
        .catch((e: unknown) => { avisar(`O mapa de sons não carregou (${base}mapa.json): ${e instanceof Error ? e.message : String(e)}. Rode python gerar_sons_up.py em D:\\Trab\\digilab\\Assets.`); return null; });
    }
    return mapa;
  };
  const buffer = (arq: string): Promise<{ duration: number } | null> => {
    let b = buffers.get(arq);
    if (!b) {
      const c = contexto();
      b = dep.buscar(base + arq).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.arrayBuffer(); }).then(d => c.decodeAudioData(d))
        .catch((e: unknown) => { avisar(`O som ${arq} não carregou: ${e instanceof Error ? e.message : String(e)}.`); return null; });
      buffers.set(arq, b);
    }
    return b;
  };

  /** toca um arquivo, com atraso (s) e variacao de tom opcional */
  const tocarArquivo = async (arq: string, atraso: number, variacao: number | null): Promise<void> => {
    const b = await buffer(arq);
    if (!b || !estado.ligado || !ctx || !ganho) return;
    const s = ctx.createBufferSource();
    s.buffer = b;
    if (variacao) s.playbackRate.value = 1 + (dep.aleatorio() * 2 - 1) * variacao / DIVISOR_VARIACAO;
    s.connect(ganho); s.start(ctx.currentTime + Math.max(0, atraso));
  };

  const api = {
    estado: (): EstadoSom => estado,
    ouvir(o: () => void): () => void { ouvintes.add(o); return () => { ouvintes.delete(o); }; },
    /** ligar e o gesto que o navegador exige: cria o contexto aqui */
    ligar(on: boolean): void {
      gravar(CHAVE_SOM, on ? "1" : "0");
      if (on) { contexto(); mudar({ ligado: true }); void carregarMapa(); } else { api.parar(); mudar({ ligado: false }); }
    },
    volume(v: number): void {
      if (!Number.isFinite(v) || v < 0 || v > 1) throw new Error("volume fora de 0 a 1: " + v);
      gravar(CHAVE_SOM_VOLUME, String(v));
      if (ganho) ganho.gain.value = v;
      mudar({ volume: v });
    },
    /** o que o mapa sabe dessa chave de sprite e desse evento (vazio: sem som, silencio esperado) */
    async eventos(evento: EventoSom, forma: string, habilidade = false): Promise<EventoMapa[]> {
      const m = await carregarMapa(), f = m?.formas[forma];
      if (!f) return [];
      return (habilidade && f.habilidade.length ? f.habilidade : f.ataque).filter(e => e.quando === evento);
    },
    /** toca o evento da forma; desligado nao faz nada (nem pede arquivo); forma ou evento sem som e silencio */
    async tocar(evento: EventoSom, forma: string, habilidade = false): Promise<void> {
      if (!estado.ligado) return;
      const evs = await api.eventos(evento, forma, habilidade);
      await Promise.all(evs.map(e => tocarArquivo(e.arquivo, e.atraso, e.variacao)));
    },
    /** o efeito da evolucao, alinhado a queda na revelacao (revelacao: em quantos segundos a cena revela) */
    async tocarEvolucao(revelacao = SFX_QUEDA): Promise<void> {
      if (!estado.ligado) return;
      const m = await carregarMapa(); if (!m) return;
      const meu = ++ordemSfx, b = await buffer(m.evolucao);
      if (!b || meu !== ordemSfx || !estado.ligado || !ctx || !ganho) return;
      const inicio = Math.max(0, SFX_QUEDA - revelacao);
      if (inicio >= b.duration) return;
      api.pararEvolucao();
      const s = ctx.createBufferSource(); s.buffer = b; s.connect(ganho); s.start(0, inicio); sfx = s;
    },
    pararEvolucao(): void { ordemSfx++; if (sfx) { try { sfx.stop(); } catch { /* ja parou */ } sfx = null; } },
    /** musica em loop com inicio e laco em amostras a 44,1 kHz (a UP-EVOLUCAO escolhe a faixa por tipo) */
    async tocarMusica(id: string): Promise<void> {
      if (!estado.ligado) return;
      const m = await carregarMapa(), mu = m?.musicas[id]; if (!mu) return;
      const meu = ++ordemMus, b = await buffer(mu.arq + ".mp3");
      if (!b || meu !== ordemMus || !estado.ligado || !ctx || !ganho) return;
      api.pararMusica();
      const s = ctx.createBufferSource(), d = ATRASO_MP3;
      s.buffer = b; s.loop = true; s.loopStart = (mu.loopIni + d) / HZ_MUSICA; s.loopEnd = Math.min(b.duration, (mu.loopFim + d) / HZ_MUSICA);
      s.connect(ganho); s.start(0, (mu.ini + d) / HZ_MUSICA); musica = s;
    },
    pararMusica(): void { ordemMus++; if (musica) { try { musica.stop(); } catch { /* ja parou */ } musica = null; } },
    parar(): void { api.pararMusica(); api.pararEvolucao(); },
  };
  return api;
}

export const SOM = criarSom(depsPadrao());

export function useSom(): EstadoSom {
  return useSyncExternalStore(o => SOM.ouvir(o), SOM.estado);
}
