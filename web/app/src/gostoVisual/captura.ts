/* A captura do protótipo P0 (docs/futuro/gosto_visual_pet.md, seções 7, 13 e 14): as fontes que viram canais da TV (canais.ts).
   - A tela e o som que o dono compartilha pelo getDisplayMedia, só depois de um clique (`abrirTela`);
   - um vídeo deste computador, escolhido num <input type=file> e tocado num <video> local (`abrirVideo`; D-GV-CANAL-7): o mesmo caminho
     da captura, e o arquivo não sai da máquina.
   Uma vez por segundo, um quadro reduzido vira o vetor da visão, e as janelas de áudio do segundo viram o vetor do som; o quadro e o áudio
   são descartados na hora. Nada é gravado nem enviado: o áudio lido não vai para os alto-falantes (o do vídeo local toca pelo próprio
   elemento, como num tocador), nem para a rede, nem para o servidor, nem para a LLM. */
import { analisarQuadro, rms, vetorDoSom } from "./sentidos.ts";
import type { Fonte } from "./canais.ts";
/** um vetor por segundo: o relógio é o dos canais (canais.ts), reexportado para quem lê a captura (scripts/midia_para_sentidos.ts) */
export { PERIODO_MS } from "./canais.ts";

/** o quadro reduzido: 64 x 36 pixels bastam para os quatro números. PROPOSTO, SEM FONTE */
export const LARGURA_QUADRO = 64, ALTURA_QUADRO = 36;
/** o RMS do áudio a cada 100 ms, para a variação. PROPOSTO, SEM FONTE */
export const PERIODO_AUDIO_MS = 100;

/** `aoAcabar` recebe o motivo quando a fonte acaba por fora (o dono parou de compartilhar) */
type AoAcabar = (motivo: string) => void;

/** a fonte sobre um <video> que já toca: lê o quadro e, se houver faixas de som, o áudio, só enquanto o canal é o atual */
function fonteDoVideo(tipo: Fonte["tipo"], video: HTMLVideoElement, faixasSom: MediaStreamTrack[], soltar: () => void): Fonte {
  const tela = document.createElement("canvas");
  tela.width = LARGURA_QUADRO; tela.height = ALTURA_QUADRO;
  const g = tela.getContext("2d", { willReadFrequently: true });
  if (!g) throw new Error("canvas 2d indisponível para ler o quadro");
  /* o som: o analisador não liga na saída (nada toca de novo) */
  let ctx: AudioContext | null = null, analisador: AnalyserNode | null = null;
  if (faixasSom.length > 0) {
    ctx = new AudioContext();
    analisador = ctx.createAnalyser();
    analisador.fftSize = 1024;
    ctx.createMediaStreamSource(new MediaStream(faixasSom)).connect(analisador);
    void ctx.resume();                                     /* criado depois do await do seletor: sem isto, pode nascer suspenso */
  }
  const amostras = analisador ? new Float32Array(analisador.fftSize) : null, espectro = analisador ? new Uint8Array(analisador.frequencyBinCount) : null;
  let janelas: number[] = [], tAudio: ReturnType<typeof setInterval> | null = null, parado = false;
  const ouvir = (sim: boolean): void => {
    if (tAudio) clearInterval(tAudio);
    tAudio = null; janelas = [];
    if (sim && analisador) tAudio = setInterval(() => { analisador!.getFloatTimeDomainData(amostras!); janelas.push(rms(amostras!)); }, PERIODO_AUDIO_MS);
  };
  return {
    tipo, temSom: analisador !== null, video,
    sentir(anterior) {
      if (parado || video.readyState < 2) return null;    /* o primeiro quadro ainda não chegou */
      g.drawImage(video, 0, 0, LARGURA_QUADRO, ALTURA_QUADRO);
      const img = g.getImageData(0, 0, LARGURA_QUADRO, ALTURA_QUADRO);
      const { vetor, lum } = analisarQuadro(img.data, LARGURA_QUADRO, ALTURA_QUADRO, anterior);
      g.clearRect(0, 0, LARGURA_QUADRO, ALTURA_QUADRO);   /* o quadro sai daqui; só a luminância reduzida fica, até o próximo segundo */
      let som = null;
      if (analisador && janelas.length > 0) { analisador.getByteFrequencyData(espectro!); som = vetorDoSom(janelas, espectro!); espectro!.fill(0); }
      janelas = [];
      return { sentido: { visao: vetor, som }, lum };
    },
    ativar(sim) {
      if (parado) return;
      ouvir(sim);
      if (tipo === "video") { if (sim) void video.play().catch(() => undefined); else video.pause(); }
    },
    parar() {
      if (parado) return;
      parado = true;
      ouvir(false);
      void ctx?.close();
      soltar();
    },
  };
}

/** abre o seletor do navegador (precisa vir de um clique) e devolve a tela escolhida como fonte; o NotAllowedError do cancelar sobe */
export async function abrirTela(aoAcabar: AoAcabar): Promise<Fonte> {
  if (!navigator.mediaDevices?.getDisplayMedia) throw new Error("este navegador não compartilha a tela (getDisplayMedia indisponível)");
  const fluxo = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
  const video = document.createElement("video");
  video.muted = true; video.playsInline = true; video.srcObject = fluxo;
  try { await video.play(); } catch (x) { for (const f of fluxo.getTracks()) f.stop(); throw x; }
  const fonte = fonteDoVideo("tela", video, fluxo.getAudioTracks(), () => { for (const f of fluxo.getTracks()) f.stop(); video.srcObject = null; });
  fluxo.getVideoTracks()[0]?.addEventListener("ended", () => aoAcabar("o compartilhamento da tela acabou"));
  return fonte;
}

/** um vídeo deste computador como fonte: tocado num <video> local, em laço, com o som dele; o som que o pet ouve vem do captureStream do
    elemento (sem ele, o pet só vê). O arquivo não sai da máquina */
export async function abrirVideo(arquivo: File, aoAcabar: AoAcabar): Promise<Fonte> {
  if (!arquivo.type.startsWith("video/")) throw new Error(`o arquivo não é um vídeo (${arquivo.type || "tipo desconhecido"})`);
  const url = URL.createObjectURL(arquivo), video = document.createElement("video");
  video.src = url; video.loop = true; video.playsInline = true;
  let solto = false;
  const soltar = (): void => { solto = true; video.pause(); video.removeAttribute("src"); video.load(); URL.revokeObjectURL(url); };
  try {
    try { await video.play(); } catch (x) {
      if (!(x instanceof DOMException && x.name === "NotAllowedError")) throw x;
      video.muted = true; await video.play();             /* o navegador não deixou tocar com som: toca mudo, e o pet não ouve */
    }
  } catch (x) { soltar(); throw new Error(`o vídeo não abriu: ${(x as Error).message}`); }
  const cap = (video as HTMLVideoElement & { captureStream?: () => MediaStream }).captureStream?.();
  const fonte = fonteDoVideo("video", video, video.muted || !cap ? [] : cap.getAudioTracks(), soltar);
  video.addEventListener("error", () => { if (!solto) aoAcabar("o vídeo parou de tocar"); });
  return fonte;
}
