/* A mídia local vira o fluxo de sentidos do P0 do gosto visual (2026-11-12, D-GV-VIDEO-1 a 8): um vetor de 7 componentes por segundo,
   como o captura.ts faria se o dono compartilhasse aquela mídia tocando. Engenharia de diagnóstico, não run de pesquisa.
   - os quadros: o ffmpeg decodifica um quadro por segundo (o PERIODO_MS do captura.ts), reduzido a 64 x 36 RGBA (o quadro do captura.ts);
     a conta é a do P0, `analisarQuadro` de src/gostoVisual/sentidos.ts, sem reescrever nada;
   - o som: o ffmpeg dá o PCM mono a 48 kHz (a mistura 0,5 (E + D) do Web Audio); a cada 100 ms o RMS das últimas 1024 amostras (o
     getFloatTimeDomainData do AnalyserNode com o fftSize 1024) e, no fim do segundo, o espectro em bytes do getByteFrequencyData (a janela
     de Blackman, a FFT de 1024, a suavização 0,8 entre chamadas, a faixa de -100 a -30 dB), refeito aqui como a especificação do Web Audio
     manda; a conta do vetor é a do P0, `rms` e `vetorDoSom`;
   - nada é gravado além do fluxo de números: os quadros e o PCM ficam em buffers na memória, descartados ao fim.
   Uso (do web/app):
     node scripts/midia_para_sentidos.ts --saida <fluxo.json> --rotulo <r> --tipo <t> <plano>
   O plano é uma lista de trechos, na ordem: `--video <arq>[@inicio+duracao][#faixa]`, `--audio <arq>@inicio+duracao` (a visão é um quadro
   preto parado) ou `--imagem <arq>+duracao` (sem som), e `--parado <video>@instante+duracao` (um quadro parado de um vídeo, sem som). */
import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream, statSync, writeFileSync } from "node:fs";
import { analisarQuadro, rms, vetorDoSom, type VetorSom, type VetorVisao } from "../src/gostoVisual/sentidos.ts";
import { ALTURA_QUADRO, LARGURA_QUADRO, PERIODO_AUDIO_MS, PERIODO_MS } from "../src/gostoVisual/captura.ts";

/** a versão da ferramenta: muda quando a conta de um número do fluxo muda */
export const VERSAO_FERRAMENTA = 1;
/** o AnalyserNode do captura.ts: o fftSize 1024; a suavização e a faixa em dB são os padrões do Web Audio (o captura.ts não os muda) */
export const FFT = 1024, SUAVIZACAO = 0.8, DB_MIN = -100, DB_MAX = -30;
/** a taxa do AudioContext suposta: 48 kHz, a padrão no Windows com a saída comum (PROPOSTO; o navegador pode usar 44,1 kHz) */
export const TAXA_AUDIO = 48000;
export const COMPONENTES_FLUXO = ["cor", "brilho", "movimento", "complexidade", "volume", "variacao", "timbre"] as const;

// ------------------------------------------------------------------ o AnalyserNode refeito (a especificação do Web Audio, 1.8.4)
/** a FFT radix-2 no lugar (re, im), n potência de 2 */
function fft(re: Float64Array, im: Float64Array): void {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { [re[i], re[j]] = [re[j]!, re[i]!]; [im[i], im[j]] = [im[j]!, im[i]!]; }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = (-2 * Math.PI) / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) {
        const a = i + k, b = a + len / 2;
        const tr = re[b]! * cr - im[b]! * ci, ti = re[b]! * ci + im[b]! * cr;
        re[b] = re[a]! - tr; im[b] = im[a]! - ti; re[a] = re[a]! + tr; im[a] = im[a]! + ti;
        const ncr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = ncr;
      }
    }
  }
}

/** o espectro em bytes do AnalyserNode, com o estado da suavização entre as chamadas (como o nó guarda o bloco anterior) */
export class Analisador {
  private anterior = new Float64Array(FFT / 2);
  private readonly janela = new Float64Array(FFT);
  constructor() {
    const a = 0.16, a0 = (1 - a) / 2, a1 = 0.5, a2 = a / 2;
    for (let n = 0; n < FFT; n++) this.janela[n] = a0 - a1 * Math.cos((2 * Math.PI * n) / FFT) + a2 * Math.cos((4 * Math.PI * n) / FFT);
  }
  /** o getByteFrequencyData sobre as últimas FFT amostras: Blackman, |X[k]| / N, a suavização, 20 log10 e os bytes */
  bytes(ultimas: Float32Array): Uint8Array {
    if (ultimas.length !== FFT) throw new Error(`o analisador precisa de ${FFT} amostras, veio ${ultimas.length}`);
    const re = new Float64Array(FFT), im = new Float64Array(FFT);
    for (let n = 0; n < FFT; n++) re[n] = ultimas[n]! * this.janela[n]!;
    fft(re, im);
    const out = new Uint8Array(FFT / 2);
    for (let k = 0; k < FFT / 2; k++) {
      const mag = Math.hypot(re[k]!, im[k]!) / FFT;
      const x = SUAVIZACAO * this.anterior[k]! + (1 - SUAVIZACAO) * mag;
      this.anterior[k] = x;
      const db = x === 0 ? -Infinity : 20 * Math.log10(x);
      const b = Math.floor((255 / (DB_MAX - DB_MIN)) * (db - DB_MIN));
      out[k] = b < 0 ? 0 : b > 255 ? 255 : b;
    }
    return out;
  }
}

/** as FFT amostras que terminam (exclusive) em `fim`; antes do começo, zeros (o nó ainda sem som) */
function ultimasAmostras(pcm: Float32Array, fim: number): Float32Array {
  const r = new Float32Array(FFT), ini = fim - FFT;
  for (let i = 0; i < FFT; i++) { const j = ini + i; r[i] = j >= 0 && j < pcm.length ? pcm[j]! : 0; }
  return r;
}

/** o som de cada segundo de um PCM mono: as janelas a cada PERIODO_AUDIO_MS (as 10 do segundo) e o espectro no fim do segundo; o
    analisador é um só para o trecho (a suavização passa de um segundo ao outro, como no captura.ts) */
export function sonsDoPcm(pcm: Float32Array, taxa: number, segundos: number, analisador = new Analisador()): VetorSom[] {
  const porSeg = PERIODO_MS / PERIODO_AUDIO_MS, r: VetorSom[] = [];
  if (!Number.isInteger(porSeg)) throw new Error("o período do áudio não divide o do quadro");
  for (let s = 0; s < segundos; s++) {
    const janelas: number[] = [];
    for (let j = 1; j <= porSeg; j++) janelas.push(rms(ultimasAmostras(pcm, Math.round((s + j / porSeg) * taxa))));
    r.push(vetorDoSom(janelas, analisador.bytes(ultimasAmostras(pcm, Math.round((s + 1) * taxa)))));
  }
  return r;
}

/** a visão de cada quadro, na ordem, com o quadro anterior do mesmo fluxo (o `anterior` do captura.ts); `anterior` entra de fora para o
    movimento atravessar a troca de trecho */
export function visoesDosQuadros(quadros: Uint8ClampedArray[], anterior: Float32Array | null): { visoes: VetorVisao[]; ultimo: Float32Array | null } {
  const visoes: VetorVisao[] = [];
  let ant = anterior;
  for (const q of quadros) { const { vetor, lum } = analisarQuadro(q, LARGURA_QUADRO, ALTURA_QUADRO, ant); visoes.push(vetor); ant = lum; }
  return { visoes, ultimo: ant };
}

// ------------------------------------------------------------------ o ffmpeg (os buffers ficam na memória)
export function temFfmpeg(): boolean {
  try { return spawnSync("ffmpeg", ["-version"], { stdio: "ignore" }).status === 0; } catch { return false; }
}

function ffmpeg(args: string[]): Promise<Buffer> {
  return new Promise((ok, falha) => {
    const p = spawn("ffmpeg", ["-v", "error", "-nostdin", ...args, "pipe:1"], { stdio: ["ignore", "pipe", "pipe"] });
    const partes: Buffer[] = [], erro: Buffer[] = [];
    p.stdout.on("data", (d: Buffer) => partes.push(d));
    p.stderr.on("data", (d: Buffer) => erro.push(d));
    p.on("error", falha);
    p.on("close", c => (c === 0 ? ok(Buffer.concat(partes)) : falha(new Error(`ffmpeg saiu com ${c}: ${Buffer.concat(erro).toString().slice(0, 400)}`))));
  });
}

const BYTES_QUADRO = LARGURA_QUADRO * ALTURA_QUADRO * 4;
/** o redimensionamento: a média por área (o drawImage do Chrome reduz com filtro próprio; ver o relato, D-GV-VIDEO-2) */
const ESCALA = `scale=${LARGURA_QUADRO}:${ALTURA_QUADRO}:flags=area`;

function quadrosDoBuffer(b: Buffer): Uint8ClampedArray[] {
  if (b.length % BYTES_QUADRO !== 0) throw new Error(`o ffmpeg deu ${b.length} bytes, que não é múltiplo de um quadro (${BYTES_QUADRO})`);
  const r: Uint8ClampedArray[] = [];
  for (let i = 0; i < b.length; i += BYTES_QUADRO) r.push(new Uint8ClampedArray(b.subarray(i, i + BYTES_QUADRO)));
  return r;
}

/** os quadros de um vídeo a um por segundo, nos instantes inicio + 0, + 1, ...; o captura.ts lê o quadro no fim de cada segundo, então
    quem usa descarta o do instante 0 */
async function quadrosDoVideo(arq: string, inicio: number, duracao: number): Promise<Uint8ClampedArray[]> {
  return quadrosDoBuffer(await ffmpeg(["-ss", String(inicio), "-t", String(duracao + 1), "-i", arq, "-map", "0:v:0",
    "-vf", `fps=1,${ESCALA}`, "-pix_fmt", "rgba", "-f", "rawvideo"]));
}
/** um quadro só (uma imagem, ou um vídeo parado no instante) */
async function quadroUnico(arq: string, instante: number | null): Promise<Uint8ClampedArray> {
  const q = quadrosDoBuffer(await ffmpeg([...(instante === null ? [] : ["-ss", String(instante)]), "-i", arq, "-map", "0:v:0", "-frames:v", "1",
    "-vf", ESCALA, "-pix_fmt", "rgba", "-f", "rawvideo"]));
  if (q.length !== 1) throw new Error(`esperado um quadro de ${arq}, veio ${q.length}`);
  return q[0]!;
}
/** os canais da faixa de som (0 sem a faixa) */
function canaisDe(arq: string, faixa: number): number {
  const p = spawnSync("ffprobe", ["-v", "error", "-select_streams", `a:${faixa}`, "-show_entries", "stream=channels", "-of", "csv=p=0", arq], { encoding: "utf8" });
  if (p.status !== 0) throw new Error(`o ffprobe falhou em ${arq}`);
  const t = p.stdout.trim();
  return t === "" ? 0 : Number(t);
}
/** o PCM mono a TAXA_AUDIO: o estéreo vira 0,5 (E + D), a mistura "speakers" do Web Audio; o mono fica como está; mais de 2 canais
    falha alto (a mistura do Web Audio para 5.1 não está refeita aqui) */
async function pcmMono(arq: string, inicio: number, duracao: number, faixa: number): Promise<Float32Array> {
  const canais = canaisDe(arq, faixa);
  if (canais === 0) throw new Error(`Stream map 0:a:${faixa} matches no streams em ${arq}`);
  if (canais > 2) throw new Error(`${arq} tem ${canais} canais de som; só mono e estéreo têm a mistura do Web Audio refeita`);
  const b = await ffmpeg(["-ss", String(inicio), "-t", String(duracao), "-i", arq, "-map", `0:a:${faixa}`,
    ...(canais === 2 ? ["-af", "pan=mono|c0=0.5*c0+0.5*c1"] : []), "-ar", String(TAXA_AUDIO), "-f", "f32le"]);
  const c = new Uint8Array(b.length);
  c.set(b);
  return new Float32Array(c.buffer, 0, Math.floor(b.length / 4));
}

export function sha256DoArquivo(arq: string): Promise<string> {
  return new Promise((ok, falha) => {
    const h = createHash("sha256");
    createReadStream(arq).on("data", d => h.update(d)).on("end", () => ok(h.digest("hex"))).on("error", falha);
  });
}

// ------------------------------------------------------------------ o plano e o fluxo
export type Trecho =
  | { tipo: "video"; arq: string; inicio: number; duracao: number | null; faixa: number }
  | { tipo: "audio"; arq: string; inicio: number; duracao: number }
  | { tipo: "imagem"; arq: string; duracao: number }
  | { tipo: "parado"; arq: string; instante: number; duracao: number };

/** a duração de uma mídia em segundos (o ffprobe) */
function duracaoDe(arq: string): number {
  const p = spawnSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq], { encoding: "utf8" });
  const d = Number(p.stdout.trim());
  if (p.status !== 0 || !(d > 0)) throw new Error(`o ffprobe não deu a duração de ${arq}`);
  return d;
}

/** um segundo do fluxo: as 4 da visão e as 3 do som (null sem som) */
export type Linha = [number, number, number, number, number | null, number | null, number | null];
export interface Fluxo {
  ferramenta: "midia_para_sentidos"; versao: number; rotulo: string; tipo: string;
  quadro: [number, number]; periodo_ms: number; periodo_audio_ms: number; fft: number; taxa_audio: number;
  componentes: readonly string[];
  trechos: { papel: string; sha256: string; bytes: number; inicio_s: number; duracao_s: number; primeiro_segundo: number; marca: string }[];
  segundos: Linha[];
}

const linha = (v: VetorVisao, s: VetorSom | null): Linha =>
  [v.cor, v.brilho, v.movimento, v.complexidade, s ? s.volume : null, s ? s.variacao : null, s ? s.timbre : null];

/** o fluxo de um plano: os trechos em sequência, com o movimento atravessando a troca (como a tela que muda de uma coisa para outra) */
export async function fluxoDoPlano(trechos: Trecho[], rotulo: string, tipo: string, marcas: string[] = []): Promise<Fluxo> {
  const fluxo: Fluxo = {
    ferramenta: "midia_para_sentidos", versao: VERSAO_FERRAMENTA, rotulo, tipo, quadro: [LARGURA_QUADRO, ALTURA_QUADRO],
    periodo_ms: PERIODO_MS, periodo_audio_ms: PERIODO_AUDIO_MS, fft: FFT, taxa_audio: TAXA_AUDIO, componentes: COMPONENTES_FLUXO, trechos: [], segundos: [],
  };
  const hashes = new Map<string, string>();
  const hash = async (a: string): Promise<string> => { if (!hashes.has(a)) hashes.set(a, await sha256DoArquivo(a)); return hashes.get(a)!; };
  let anterior: Float32Array | null = null;
  for (const [i, t] of trechos.entries()) {
    const primeiro = fluxo.segundos.length;
    let visoes: VetorVisao[], sons: (VetorSom | null)[], inicio = 0, duracao: number;
    if (t.tipo === "video") {
      inicio = t.inicio;
      duracao = Math.floor(t.duracao ?? duracaoDe(t.arq) - t.inicio);
      const qs = (await quadrosDoVideo(t.arq, t.inicio, duracao)).slice(1);
      let pcm: Float32Array | null = null;
      try { pcm = await pcmMono(t.arq, t.inicio, duracao, t.faixa); } catch (e) {
        if (!/matches no streams|Stream map/i.test(String(e))) throw e; /* o vídeo sem faixa de som: o som fica null (falha alto no resto) */
      }
      const n = Math.min(qs.length, duracao, pcm ? Math.floor(pcm.length / TAXA_AUDIO) : Infinity);
      if (n < 1) throw new Error(`o trecho ${i} (${t.arq}) não deu nenhum segundo`);
      ({ visoes, ultimo: anterior } = visoesDosQuadros(qs.slice(0, n), anterior));
      sons = pcm ? sonsDoPcm(pcm, TAXA_AUDIO, n) : Array.from({ length: n }, () => null);
      duracao = n;
    } else if (t.tipo === "audio") {
      inicio = t.inicio;
      const pcm = await pcmMono(t.arq, t.inicio, t.duracao, 0);
      const n = Math.min(t.duracao, Math.floor(pcm.length / TAXA_AUDIO));
      const preto = new Uint8ClampedArray(BYTES_QUADRO);
      for (let k = 3; k < BYTES_QUADRO; k += 4) preto[k] = 255;
      ({ visoes, ultimo: anterior } = visoesDosQuadros(Array.from({ length: n }, () => preto), anterior));
      sons = sonsDoPcm(pcm, TAXA_AUDIO, n);
      duracao = n;
    } else {
      const q = await quadroUnico(t.arq, t.tipo === "parado" ? t.instante : null);
      if (t.tipo === "parado") inicio = t.instante;
      duracao = t.duracao;
      ({ visoes, ultimo: anterior } = visoesDosQuadros(Array.from({ length: t.duracao }, () => q), anterior));
      sons = Array.from({ length: t.duracao }, () => null);
    }
    for (let k = 0; k < visoes.length; k++) fluxo.segundos.push(linha(visoes[k]!, sons[k]!));
    fluxo.trechos.push({ papel: t.tipo, sha256: await hash(t.arq), bytes: statSync(t.arq).size, inicio_s: inicio, duracao_s: duracao,
      primeiro_segundo: primeiro, marca: marcas[i] ?? `trecho${i}` });
  }
  for (const [s, l] of fluxo.segundos.entries())
    for (const [k, x] of l.entries()) if (x !== null && !(x >= 0 && x <= 1)) throw new Error(`o segundo ${s} tem ${COMPONENTES_FLUXO[k]} = ${x}`);
  return fluxo;
}

// ------------------------------------------------------------------ a linha de comando
function lerTrecho(tipo: string, v: string): Trecho {
  const m = /^(.*?)(?:@([\d.]+))?(?:\+([\d.]+))?(?:#(\d+))?$/.exec(v);
  if (!m) throw new Error(`trecho ilegível: ${v}`);
  const arq = m[1]!, a = m[2] === undefined ? null : Number(m[2]), d = m[3] === undefined ? null : Number(m[3]);
  if (tipo === "video") return { tipo, arq, inicio: a ?? 0, duracao: d, faixa: m[4] === undefined ? 0 : Number(m[4]) };
  if (d === null) throw new Error(`o trecho ${tipo} precisa da duração (+segundos): ${v}`);
  if (tipo === "audio") return { tipo, arq, inicio: a ?? 0, duracao: d };
  if (tipo === "imagem") return { tipo, arq, duracao: d };
  if (tipo === "parado") { if (a === null) throw new Error(`o parado precisa do instante (@s): ${v}`); return { tipo, arq, instante: a, duracao: d }; }
  throw new Error(`tipo de trecho desconhecido: ${tipo}`);
}

async function principal(argv: string[]): Promise<void> {
  let saida: string | null = null, rotulo: string | null = null, tipo: string | null = null;
  const trechos: Trecho[] = [], marcas: string[] = [];
  for (let i = 0; i < argv.length; i += 2) {
    const k = argv[i]!, v = argv[i + 1];
    if (v === undefined) throw new Error(`${k} sem valor`);
    if (k === "--saida") saida = v; else if (k === "--rotulo") rotulo = v; else if (k === "--tipo") tipo = v;
    else if (k === "--marca") marcas[trechos.length - 1] = v;
    else if (/^--(video|audio|imagem|parado)$/.test(k)) trechos.push(lerTrecho(k.slice(2), v));
    else throw new Error(`opção desconhecida: ${k}`);
  }
  if (!saida || !rotulo || !tipo || trechos.length === 0) throw new Error("uso: --saida <json> --rotulo <r> --tipo <t> e ao menos um trecho");
  const f = await fluxoDoPlano(trechos, rotulo, tipo, marcas);
  writeFileSync(saida, JSON.stringify(f));
  console.log(`${rotulo}: ${f.segundos.length} s, ${f.trechos.length} trecho(s) -> ${saida}`);
}

if (process.argv[1] && /midia_para_sentidos\.ts$/.test(process.argv[1])) {
  principal(process.argv.slice(2)).catch(e => { console.error(e instanceof Error ? e.message : e); process.exit(1); });
}
