/* A captura do protótipo P0 (docs/futuro/gosto_visual_pet.md, seções 7, 13 e 14): a tela e o som que o dono compartilha pelo
   getDisplayMedia, só depois de um clique. Uma vez por segundo, um quadro reduzido vira o vetor da visão, e as janelas de áudio do
   segundo viram o vetor do som; o quadro e o áudio são descartados na hora. Nada é gravado nem enviado: o áudio não vai para os alto-falantes,
   nem para a rede, nem para o servidor, nem para a LLM. */
import { analisarQuadro, rms, vetorDoSom } from "./sentidos.ts";
import type { Sentido } from "./gosto.ts";

/** o quadro reduzido: 64 x 36 pixels bastam para os quatro números. PROPOSTO, SEM FONTE */
export const LARGURA_QUADRO = 64, ALTURA_QUADRO = 36;
/** um vetor por segundo; o RMS do áudio a cada 100 ms, para a variação. PROPOSTOS, SEM FONTE */
export const PERIODO_MS = 1000, PERIODO_AUDIO_MS = 100;

export interface Captura { parar(): void; temSom: boolean }

/** começa a captura (precisa vir de um clique); `aoSentir` recebe um Sentido por segundo, `aoAcabar` quando o dono para de compartilhar */
export async function capturarTela(aoSentir: (s: Sentido) => void, aoAcabar: (motivo: string) => void): Promise<Captura> {
  if (!navigator.mediaDevices?.getDisplayMedia) throw new Error("este navegador não compartilha a tela (getDisplayMedia indisponível)");
  const fluxo = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
  const video = document.createElement("video");
  video.muted = true; video.playsInline = true; video.srcObject = fluxo;
  await video.play();
  const tela = document.createElement("canvas");
  tela.width = LARGURA_QUADRO; tela.height = ALTURA_QUADRO;
  const g = tela.getContext("2d", { willReadFrequently: true });
  if (!g) throw new Error("canvas 2d indisponível para ler o quadro");

  /* o som: só se o dono marcou "compartilhar áudio"; o analisador não liga na saída (nada toca de novo) */
  const faixasSom = fluxo.getAudioTracks();
  let ctx: AudioContext | null = null, analisador: AnalyserNode | null = null;
  if (faixasSom.length > 0) {
    ctx = new AudioContext();
    analisador = ctx.createAnalyser();
    analisador.fftSize = 1024;
    ctx.createMediaStreamSource(new MediaStream(faixasSom)).connect(analisador);
  }
  const amostras = analisador ? new Float32Array(analisador.fftSize) : null, espectro = analisador ? new Uint8Array(analisador.frequencyBinCount) : null;
  let janelas: number[] = [], anterior: Float32Array | null = null, parado = false;

  const tAudio = analisador ? setInterval(() => { analisador!.getFloatTimeDomainData(amostras!); janelas.push(rms(amostras!)); }, PERIODO_AUDIO_MS) : null;
  const tQuadro = setInterval(() => {
    if (video.readyState < 2) return; /* o primeiro quadro ainda não chegou */
    g.drawImage(video, 0, 0, LARGURA_QUADRO, ALTURA_QUADRO);
    const img = g.getImageData(0, 0, LARGURA_QUADRO, ALTURA_QUADRO);
    const { vetor, lum } = analisarQuadro(img.data, LARGURA_QUADRO, ALTURA_QUADRO, anterior);
    g.clearRect(0, 0, LARGURA_QUADRO, ALTURA_QUADRO); /* o quadro sai daqui; só a luminância reduzida fica, até o próximo segundo */
    anterior = lum;
    let som = null;
    if (analisador && janelas.length > 0) { analisador.getByteFrequencyData(espectro!); som = vetorDoSom(janelas, espectro!); espectro!.fill(0); }
    janelas = [];
    aoSentir({ visao: vetor, som });
  }, PERIODO_MS);

  const parar = (): void => {
    if (parado) return;
    parado = true;
    clearInterval(tQuadro);
    if (tAudio) clearInterval(tAudio);
    for (const f of fluxo.getTracks()) f.stop();
    video.srcObject = null;
    void ctx?.close();
    anterior = null;
  };
  fluxo.getVideoTracks()[0]?.addEventListener("ended", () => { parar(); aoAcabar("o compartilhamento da tela acabou"); });
  return { parar, temSom: analisador !== null };
}
