/* Os sentidos do protótipo P0 do gosto visual (docs/futuro/gosto_visual_pet.md, seções 2, 13 e 14): o quadro da tela e a janela de áudio
   viram um vetor pequeno, e o resto é descartado na hora. Sem DOM: recebe os pixels e as amostras já lidos, para o teste rodar no node.
   Fora do motor, do log e do save; não tem par no Python. Todos os números daqui são PROPOSTOS, SEM FONTE (protótipo, não mecânica). */

/** a visão: quatro números em [0, 1] (seção 2.1) */
export interface VetorVisao { cor: number; brilho: number; movimento: number; complexidade: number }
/** o som: três números em [0, 1] (seção 13) */
export interface VetorSom { volume: number; variacao: number; timbre: number }

/** o ganho do movimento: a diferença média de luminância entre quadros é pequena, e 0,25 já é um corte de cena. PROPOSTO, SEM FONTE */
export const GANHO_MOVIMENTO = 4;
/** o corte da borda: a soma das diferenças de luminância com o vizinho da direita e o de baixo. PROPOSTO, SEM FONTE */
export const CORTE_BORDA = 0.1;
/** o ganho da complexidade: metade dos pixels com borda já é um quadro "cheio". PROPOSTO, SEM FONTE */
export const GANHO_COMPLEXIDADE = 2;
/** o ganho do volume (o RMS de [-1, 1]): 0,25 de RMS já é alto. PROPOSTO, SEM FONTE */
export const GANHO_VOLUME = 4;
/** o ganho do timbre (o centróide como fração de Nyquist): 0,25 de Nyquist já é agudo. PROPOSTO, SEM FONTE */
export const GANHO_TIMBRE = 4;

const limitar = (x: number): number => (x < 0 ? 0 : x > 1 ? 1 : x);

/** a luminância (0 a 1) de cada pixel RGBA */
export function luminancia(px: Uint8ClampedArray, w: number, h: number): Float32Array {
  if (px.length !== w * h * 4) throw new Error(`quadro com ${px.length} bytes, esperado ${w * h * 4} (${w}x${h} RGBA)`);
  const y = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) y[i] = (0.299 * px[4 * i]! + 0.587 * px[4 * i + 1]! + 0.114 * px[4 * i + 2]!) / 255;
  return y;
}

/** o vetor da visão de um quadro RGBA; `anterior` é a luminância do quadro de antes (null no primeiro: movimento 0). Devolve também a
    luminância deste quadro, para o próximo; os pixels não ficam guardados */
export function analisarQuadro(px: Uint8ClampedArray, w: number, h: number, anterior: Float32Array | null): { vetor: VetorVisao; lum: Float32Array } {
  const lum = luminancia(px, w, h), n = w * h;
  if (anterior && anterior.length !== n) throw new Error(`o quadro anterior tem ${anterior.length} pixels, este tem ${n}`);
  let sat = 0, bri = 0, mov = 0, bordas = 0;
  for (let i = 0; i < n; i++) {
    const r = px[4 * i]!, g = px[4 * i + 1]!, b = px[4 * i + 2]!, mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    sat += mx === 0 ? 0 : (mx - mn) / mx;
    bri += lum[i]!;
    if (anterior) mov += Math.abs(lum[i]! - anterior[i]!);
    const x = i % w, yy = (i - x) / w;
    const dx = x + 1 < w ? Math.abs(lum[i]! - lum[i + 1]!) : 0, dy = yy + 1 < h ? Math.abs(lum[i]! - lum[i + w]!) : 0;
    if (dx + dy > CORTE_BORDA) bordas++;
  }
  return {
    vetor: { cor: limitar(sat / n), brilho: limitar(bri / n), movimento: limitar((mov / n) * GANHO_MOVIMENTO), complexidade: limitar((bordas / n) * GANHO_COMPLEXIDADE) },
    lum,
  };
}

/** o RMS de uma janela de amostras em [-1, 1] */
export function rms(amostras: Float32Array): number {
  if (amostras.length === 0) throw new Error("janela de áudio vazia");
  let s = 0;
  for (const a of amostras) s += a * a;
  return Math.sqrt(s / amostras.length);
}

/** o vetor do som de um segundo: os RMS das janelas curtas dele (a variação) e o espectro em bytes do AnalyserNode (o timbre) */
export function vetorDoSom(rmsJanelas: readonly number[], espectro: Uint8Array): VetorSom {
  if (rmsJanelas.length === 0) throw new Error("nenhuma janela de áudio neste segundo");
  if (espectro.length === 0) throw new Error("espectro vazio");
  const media = rmsJanelas.reduce((s, x) => s + x, 0) / rmsJanelas.length;
  const dp = Math.sqrt(rmsJanelas.reduce((s, x) => s + (x - media) ** 2, 0) / rmsJanelas.length);
  /* o espectro do AnalyserNode vem em bytes de dB (a faixa padrão, de -100 a -30 dB, são 70 dB, ou 3,5 décadas de amplitude); volta à
     magnitude linear para o centróide. O byte 0 é o piso: conta como silêncio */
  let soma = 0, pond = 0;
  for (let i = 0; i < espectro.length; i++) { const m = espectro[i]! === 0 ? 0 : 10 ** ((espectro[i]! / 255) * 3.5); soma += m; pond += m * i; }
  const centroide = soma === 0 ? 0 : pond / soma / espectro.length;
  return { volume: limitar(media * GANHO_VOLUME), variacao: media === 0 ? 0 : limitar(dp / media), timbre: limitar(centroide * GANHO_TIMBRE) };
}
