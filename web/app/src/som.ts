/* Som do jogo (TAREFA_V2_UP_SOM): Web Audio do navegador, sem biblioteca. Sons e musicas do Digimon UP (Bandai; com o credito,
   autorizados pelo Matheus: docs/UI_GUIDELINES.md, secao 5.1) ficam FORA do repositorio, em D:\Trab\digilab\Assets\sons, com o
   mapa.json (chave de sprite -> eventos) gerado por Assets\gerar_sons_up.py. Ligado por padrao (Matheus, 2026-11-10, para a musica da cena da
   evolucao tocar sem passar por Ajustes); desligado pelo jogador, fica lembrado e nada e pedido nem tocado.
   Liga/desliga e volume ficam no localStorage do app (nao no save do pet). So apresentacao: nada daqui entra no motor, no log
   ou no save, e a variacao do som usa o Math.random do app, nunca a RNG do motor. A logica e a do bloco "sons do jogo" da arena do
   prototipo (eventos do script de batalha com atraso e variacao), reescrita. */
import { useSyncExternalStore } from "react";
import { CHAVE } from "./save.ts";
import type { EfeitoSom } from "./somEventos.ts";

export const CHAVE_SOM = CHAVE + "-som";
export const CHAVE_SOM_VOLUME = CHAVE + "-som-volume";
/** os volumes da musica e dos efeitos (SOM-UP, SD-5), por baixo do geral */
export const CHAVE_SOM_VOL_MUSICA = CHAVE + "-som-vol-musica";
export const CHAVE_SOM_VOL_EFEITOS = CHAVE + "-som-vol-efeitos";
/** a mesma convencao do atlas: relativo a pagina em /v1/web/dist/ (no servidor local cai em /Assets/sons/) */
export const SONS_URL = "../../../Assets/sons/";
/** volume padrao ao ligar pela primeira vez (PROPOSTO, SEM FONTE) */
export const VOLUME_PADRAO = 0.6;
/** a musica de fundo nasce mais baixa que os efeitos (SD-6: baixa, para nao cansar). PROPOSTOS, SEM FONTE */
export const VOL_MUSICA_PADRAO = 0.5;
export const VOL_EFEITOS_PADRAO = 1;
/** no maximo tantas copias do mesmo arquivo tocando juntas (o golpe de luta em rajada nao satura). PROPOSTO, SEM FONTE */
export const VOZES_POR_ARQUIVO = 4;
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
/** onde cada musica toca (SOM-UP): chaves da tabela BGM do GameData do Digimon UP */
export interface LugaresSom { ilha: string; treino: string; nascimento: string; luta: Record<string, string>; chefe: string[] }
export interface MapaSom {
  versao: number; evolucao: string; musicas: Record<string, MusicaSom>; formas: Record<string, FormaSom>; sem_som: { forma: string; digimon: string }[];
  /** desde a versao 2 (SOM-UP): os efeitos de interface, cuidado, treino e luta e as musicas por lugar */
  efeitos?: Record<string, { arq: string }>; lugares?: LugaresSom;
}
/** a musica pedida: uma chave de BGM, ou um lugar que o mapa resolve (a luta pelo mapa da arena, ou a de chefe) */
export type AlvoMusica = string | { lugar: "ilha" | "treino" | "nascimento" } | { luta: string; chefe: boolean };
/** quem pede musica, do mais forte ao mais fraco: a evolucao cobre a luta, que cobre o treino e o nascimento, que cobrem a ilha */
/** os efeitos que a HR2 acrescentou ao mapa (Assets/gerar_sons_up.py): com o mapa de antes, o jogo avisa em vez de falhar */
const EFEITOS_HR2: readonly string[] = ["cuidado_toque", "cuidado_limpar", "cuidado_recusa", "fruta_boa", "fruta_podre", "chamado_atendido", "tratar", "nascer", "voz"];
/** o bipe do chamado (HR3): cada toque e [hz, inicio em s, duracao em s]. PROPOSTOS, SEM FONTE (o estilo V-pet da SD-8) */
export type TipoBipe = "abre" | "urgente" | "perdido";
export const BIPES: Readonly<Record<TipoBipe, readonly (readonly [number, number, number])[]>> = {
  abre: [[2000, 0, 0.08], [2000, 0.14, 0.08], [2000, 0.28, 0.08]],
  urgente: [[2400, 0, 0.06], [2400, 0.1, 0.06], [2400, 0.2, 0.06], [2400, 0.3, 0.06], [2400, 0.4, 0.06]],
  perdido: [[1200, 0, 0.12], [800, 0.16, 0.12], [500, 0.32, 0.2]],
};
/** o volume de cada toque do bipe (a onda quadrada e forte). PROPOSTO, SEM FONTE */
export const BIPE_GANHO = 0.08;
export const PRIORIDADE_MUSICA = { evolucao: 3, luta: 2, treino: 1, nascimento: 1, jornada: 1, ilha: 0 } as const;
export type FonteMusica = keyof typeof PRIORIDADE_MUSICA;

/* o minimo da Web Audio que o modulo usa (o teste injeta um falso) */
export interface NoAudio { connect(destino: unknown): unknown }
export interface FonteAudio extends NoAudio {
  buffer: unknown; loop: boolean; loopStart: number; loopEnd: number; playbackRate: { value: number };
  start(quando?: number, deslocamento?: number): void; stop(): void;
}
export interface GanhoAudio extends NoAudio { gain: { value: number } }
/** o oscilador do bipe do chamado (HR3); opcional no contexto: sem ele (o teste antigo), o bipe nao toca */
export interface OsciladorAudio extends NoAudio { type: string; frequency: { value: number }; start(quando?: number): void; stop(quando?: number): void }
export interface ContextoAudio {
  state: string; currentTime: number; destination: unknown;
  createGain(): GanhoAudio; createBufferSource(): FonteAudio; createOscillator?(): OsciladorAudio;
  decodeAudioData(dados: ArrayBuffer): Promise<{ duration: number }>; resume(): Promise<void>;
}
export interface Dependencias {
  criarContexto: () => ContextoAudio;
  buscar: (url: string) => Promise<{ ok: boolean; status: number; json(): Promise<unknown>; arrayBuffer(): Promise<ArrayBuffer> }>;
  aleatorio: () => number;
  armazenamento: { getItem(k: string): string | null; setItem(k: string, v: string): void } | null;
  /** chama f uma vez no proximo gesto do jogador (o navegador so libera o audio depois de um); opcional: o teste nao precisa */
  aoGesto?: (f: () => void) => void;
}
export interface EstadoSom { ligado: boolean; volume: number; volMusica: number; volEfeitos: number; aviso: string | null }

const depsPadrao = (): Dependencias => ({
  criarContexto: () => new (window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)() as unknown as ContextoAudio,
  buscar: url => fetch(url),
  aleatorio: Math.random,
  armazenamento: (() => { try { return localStorage; } catch { return null; } })(),
  aoGesto: f => { const g = (): void => { removeEventListener("pointerdown", g); removeEventListener("keydown", g); f(); }; addEventListener("pointerdown", g); addEventListener("keydown", g); },
});

/** um sistema de som; o jogo usa a instancia SOM, o teste cria a dele com dependencias falsas */
export function criarSom(dep: Dependencias, base = SONS_URL) {
  const ouvintes = new Set<() => void>();
  /* ganho: o geral; gMusica e gEfeitos ficam por baixo dele (os barramentos da musica e dos efeitos) */
  let ctx: ContextoAudio | null = null, ganho: GanhoAudio | null = null, gMusica: GanhoAudio | null = null, gEfeitos: GanhoAudio | null = null;
  let mapa: Promise<MapaSom | null> | null = null;
  const buffers = new Map<string, Promise<{ duration: number } | null>>();
  let musica: FonteAudio | null = null, sfx: FonteAudio | null = null, ordemMus = 0, ordemSfx = 0, esperandoGesto = false;
  /** a musica tocando agora (a chave de BGM) e os pedidos de cada fonte; o fim previsto de cada copia tocando, por arquivo */
  let musicaId: string | null = null;
  const pedidos = new Map<FonteMusica, AlvoMusica>(), tocando = new Map<string, number[]>();

  const ler = (k: string): string | null => { try { return dep.armazenamento?.getItem(k) ?? null; } catch { return null; } };
  const gravar = (k: string, v: string): void => { try { dep.armazenamento?.setItem(k, v); } catch { /* preferencia de tela */ } };
  /* o que estava lembrado: desligado so com "0" (sem nada gravado, ligado); volume so se for numero entre 0 e 1 */
  const lerVol = (k: string, padrao: number): number => { const t = ler(k), v = Number(t); return t !== null && Number.isFinite(v) && v >= 0 && v <= 1 ? v : padrao; };
  let estado: EstadoSom = {
    ligado: ler(CHAVE_SOM) !== "0", volume: lerVol(CHAVE_SOM_VOLUME, VOLUME_PADRAO),
    volMusica: lerVol(CHAVE_SOM_VOL_MUSICA, VOL_MUSICA_PADRAO), volEfeitos: lerVol(CHAVE_SOM_VOL_EFEITOS, VOL_EFEITOS_PADRAO), aviso: null,
  };
  const mudar = (p: Partial<EstadoSom>): void => { estado = { ...estado, ...p }; for (const o of ouvintes) o(); };

  /** falha uma vez so: o aviso fica visivel e a tela segue (nada de falha calada) */
  const avisar = (msg: string): void => { if (estado.aviso === null) { console.error(msg); mudar({ aviso: msg }); } };

  const contexto = (): ContextoAudio => {
    if (!ctx) {
      ctx = dep.criarContexto(); ganho = ctx.createGain(); ganho.gain.value = estado.volume; ganho.connect(ctx.destination);
      gMusica = ctx.createGain(); gMusica.gain.value = estado.volMusica; gMusica.connect(ganho);
      gEfeitos = ctx.createGain(); gEfeitos.gain.value = estado.volEfeitos; gEfeitos.connect(ganho);
    }
    /* com o som ligado por padrao, a cena da evolucao pode abrir antes de qualquer clique (o pet evolui ao abrir o jogo): o contexto
       nasce suspenso e o que ja comecou toca quando o jogador fizer o primeiro gesto */
    if (ctx.state === "suspended") {
      const c = ctx;
      void c.resume();
      if (!esperandoGesto && dep.aoGesto) { esperandoGesto = true; dep.aoGesto(() => { esperandoGesto = false; void c.resume(); }); }
    }
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

  /** toca um arquivo no barramento dos efeitos, com atraso (s) e variacao de tom opcional; com VOZES_POR_ARQUIVO copias dele ainda
      tocando, esta nao toca (a rajada da luta nao satura) */
  const tocarArquivo = async (arq: string, atraso: number, variacao: number | null, taxaFixa = 1): Promise<void> => {
    const b = await buffer(arq);
    if (!b || !estado.ligado || !ctx || !gEfeitos) return;
    const agora = ctx.currentTime, ini = agora + Math.max(0, atraso), vivas = (tocando.get(arq) ?? []).filter(t => t > agora);
    if (vivas.length >= VOZES_POR_ARQUIVO) { tocando.set(arq, vivas); return; }
    const s = ctx.createBufferSource();
    s.buffer = b;
    const taxa = taxaFixa * (variacao ? 1 + (dep.aleatorio() * 2 - 1) * variacao / DIVISOR_VARIACAO : 1);
    if (taxa !== 1) s.playbackRate.value = taxa;
    s.connect(gEfeitos); s.start(ini);
    vivas.push(ini + b.duration / taxa); tocando.set(arq, vivas);
  };
  const avisoMapaAntigo = (): void => avisar("O mapa de sons é de uma versão antiga, sem os efeitos e as músicas por lugar. Rode python gerar_sons_up.py em D:\\Trab\\digilab\\Assets.");
  /** a chave de BGM de um pedido (o lugar pelo mapa); sem os lugares no mapa (o mapa antigo), null */
  const resolver = (m: MapaSom, a: AlvoMusica): string | null => {
    if (typeof a === "string") return a;
    const l = m.lugares; if (!l) { avisoMapaAntigo(); return null; }
    if ("lugar" in a) return l[a.lugar];
    if (a.chefe) return l.chefe.length ? l.chefe[0]! : null;
    const k = l.luta[a.luta]; if (k === undefined) throw new Error(`mapa de sons: a luta no mapa ${a.luta} nao tem musica`);
    return k;
  };
  /** a musica que deve tocar agora: o pedido de maior prioridade; ja tocando, segue sem recomecar */
  const reger = async (): Promise<void> => {
    let melhor: AlvoMusica | null = null, pr = -1;
    for (const [f, a] of pedidos) if (PRIORIDADE_MUSICA[f] > pr) { pr = PRIORIDADE_MUSICA[f]; melhor = a; }
    if (melhor === null) { if (musicaId !== null) api.pararMusica(); return; }
    if (!estado.ligado) return;
    const m = await carregarMapa(); if (!m) return;
    const id = resolver(m, melhor);
    if (id === null) { api.pararMusica(); return; }
    if (id !== musicaId) await api.tocarMusica(id);
  };

  const api = {
    estado: (): EstadoSom => estado,
    ouvir(o: () => void): () => void { ouvintes.add(o); return () => { ouvintes.delete(o); }; },
    /** ligar e o gesto que o navegador exige: cria o contexto aqui */
    ligar(on: boolean): void {
      gravar(CHAVE_SOM, on ? "1" : "0");
      if (on) { contexto(); mudar({ ligado: true }); void carregarMapa(); void reger(); } else { api.parar(); mudar({ ligado: false }); }
    },
    volume(v: number): void {
      if (!Number.isFinite(v) || v < 0 || v > 1) throw new Error("volume fora de 0 a 1: " + v);
      gravar(CHAVE_SOM_VOLUME, String(v));
      if (ganho) ganho.gain.value = v;
      mudar({ volume: v });
    },
    /** os volumes da musica e dos efeitos (por baixo do geral) */
    volumeMusica(v: number): void {
      if (!Number.isFinite(v) || v < 0 || v > 1) throw new Error("volume da música fora de 0 a 1: " + v);
      gravar(CHAVE_SOM_VOL_MUSICA, String(v)); if (gMusica) gMusica.gain.value = v; mudar({ volMusica: v });
    },
    volumeEfeitos(v: number): void {
      if (!Number.isFinite(v) || v < 0 || v > 1) throw new Error("volume dos efeitos fora de 0 a 1: " + v);
      gravar(CHAVE_SOM_VOL_EFEITOS, String(v)); if (gEfeitos) gEfeitos.gain.value = v; mudar({ volEfeitos: v });
    },
    /** um efeito do jogo (src/somEventos.ts) pelo nome; desligado nao faz nada (nem pede arquivo). O mapa antigo (sem "efeitos") avisa
        uma vez; efeito que o mapa nao tem falha alto */
    async efeito(e: EfeitoSom, atraso = 0, taxa = 1): Promise<void> {
      if (!estado.ligado) return;
      if (!(taxa > 0) || !Number.isFinite(taxa)) throw new Error("taxa do efeito invalida: " + taxa);
      const m = await carregarMapa(); if (!m) return;
      if (!m.efeitos) { avisoMapaAntigo(); return; }
      const x = m.efeitos[e];
      if (!x) {
        /* o mapa da versao 2 de antes da HR2 nao tem os efeitos do cuidado: avisa uma vez, como o mapa antigo (Assets fica fora do git) */
        if (EFEITOS_HR2.includes(e)) { avisoMapaAntigo(); return; }
        throw new Error(`mapa de sons: o efeito ${e} nao esta no mapa`);
      }
      await tocarArquivo(x.arq, atraso, null, taxa);
    },
    /** a voz do pet (HR2): o arquivo da voz do UP com o tom da especie, do estagio e do humor (src/somVoz.ts, taxaDaVoz) */
    voz(taxa: number): Promise<void> { return this.efeito("voz", 0, taxa); },
    /** o bipe do chamado do bebe (HR3, SD-8): sintetizado, sem arquivo. "abre": tres toques; "urgente": cinco, mais agudos e mais rapidos;
        "perdido": tres toques descendo. Desligado, ou sem oscilador no contexto, nada */
    bipe(tipo: TipoBipe): void {
      if (!estado.ligado) return;
      const c = contexto(); if (!c.createOscillator || !gEfeitos) return;
      const roteiro = BIPES[tipo]; if (!roteiro) throw new Error("bipe desconhecido: " + tipo);
      const t0 = c.currentTime;
      roteiro.forEach(([hz, ini, dur]) => {
        const o = c.createOscillator!(), g = c.createGain();
        o.type = "square"; o.frequency.value = hz; g.gain.value = BIPE_GANHO;
        o.connect(g); g.connect(gEfeitos!); o.start(t0 + ini); o.stop(t0 + ini + dur);
      });
    },
    /** a fonte pede (ou, com null, larga) a musica; toca a do pedido mais forte (PRIORIDADE_MUSICA) */
    pedirMusica(fonte: FonteMusica, alvo: AlvoMusica | null): Promise<void> {
      if (alvo === null) pedidos.delete(fonte); else pedidos.set(fonte, alvo);
      return reger();
    },
    /** a musica tocando agora (a chave de BGM), para o teste e o e2e */
    musicaAgora: (): string | null => musicaId,
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
      const s = ctx.createBufferSource(); s.buffer = b; s.connect(gEfeitos ?? ganho); s.start(0, inicio); sfx = s;
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
      s.connect(gMusica ?? ganho); s.start(0, (mu.ini + d) / HZ_MUSICA); musica = s; musicaId = id;
    },
    pararMusica(): void { ordemMus++; musicaId = null; if (musica) { try { musica.stop(); } catch { /* ja parou */ } musica = null; } },
    parar(): void { api.pararMusica(); api.pararEvolucao(); },
  };
  return api;
}

export const SOM = criarSom(depsPadrao());

export function useSom(): EstadoSom {
  return useSyncExternalStore(o => SOM.ouvir(o), SOM.estado);
}
