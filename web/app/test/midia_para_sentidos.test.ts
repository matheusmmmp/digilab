// A ferramenta que transforma uma mídia local no fluxo de sentidos do P0 (scripts/midia_para_sentidos.ts; D-GV-VIDEO-1 a 8). Só mídia
// sintética: o sinal em memória e, com o ffmpeg instalado, um vídeo `testsrc` com `sine` gerado numa pasta temporária, apagada ao fim.
// Nunca as mídias do dono.
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { Analisador, FFT, TAXA_AUDIO, fluxoDoPlano, sonsDoPcm, temFfmpeg } from "../scripts/midia_para_sentidos.ts";
import { GANHO_TIMBRE, GANHO_VOLUME } from "../src/gostoVisual/sentidos.ts";

const seno = (hz: number, amp: number, s: number): Float32Array =>
  Float32Array.from({ length: Math.round(s * TAXA_AUDIO) }, (_, i) => amp * Math.sin((2 * Math.PI * hz * i) / TAXA_AUDIO));

describe("o AnalyserNode refeito e o som do P0", () => {
  test("o pico do espectro de um seno de 1500 Hz cai no bin dele, e o silêncio é o piso", () => {
    const a = new Analisador(), b = a.bytes(seno(1500, 0.5, FFT / TAXA_AUDIO + 0.01).subarray(0, FFT));
    const pico = b.indexOf(Math.max(...b));
    expect(pico).toBe(Math.round((1500 / TAXA_AUDIO) * FFT));
    expect(b.length).toBe(FFT / 2);
    expect(new Analisador().bytes(new Float32Array(FFT)).every(x => x === 0)).toBe(true);
  });

  test("a suavização passa de uma chamada à outra (o nó guarda o bloco anterior)", () => {
    const a = new Analisador(), x = seno(1000, 0.5, 0.1).subarray(0, FFT);
    const b1 = a.bytes(x), b2 = a.bytes(x), k = Math.round((1000 / TAXA_AUDIO) * FFT);
    expect(b2[k]!).toBeGreaterThan(b1[k]!);
  });

  test("um seno de 1 kHz dá o volume e o timbre da conta do P0", () => {
    const sons = sonsDoPcm(seno(1000, 0.125, 4), TAXA_AUDIO, 4);
    expect(sons).toHaveLength(4);
    for (const s of sons.slice(1)) {
      expect(s.volume).toBeCloseTo((0.125 / Math.SQRT2) * GANHO_VOLUME, 2);
      expect(s.variacao).toBeLessThan(0.02);
      expect(s.timbre).toBeCloseTo((1000 / (TAXA_AUDIO / 2)) * GANHO_TIMBRE, 2);
    }
  });

  test("a ferramenta chama as contas do P0 em vez de refazê-las", () => {
    const t = readFileSync(new URL("../scripts/midia_para_sentidos.ts", import.meta.url), "utf8");
    expect(t).toContain('from "../src/gostoVisual/sentidos.ts"');
    expect(t).toMatch(/analisarQuadro\(/);
    expect(t).toMatch(/vetorDoSom\(/);
    expect(t).not.toMatch(/0\.299|0\.587/); /* a luminância é a do sentidos.ts */
    expect(t).not.toMatch(/writeFileSync\([^)]*(png|raw|wav|pcm)/i); /* nenhum quadro nem áudio vai para o disco */
  });
});

describe.skipIf(!temFfmpeg())("com o ffmpeg: um vídeo sintético vira o fluxo", () => {
  test("o testsrc com o sine, uma imagem parada e um áudio sem imagem", async () => {
    const dir = mkdtempSync(join(tmpdir(), "digilab-midia-"));
    try {
      const mp4 = join(dir, "t.mp4"), png = join(dir, "t.png"), wav = join(dir, "t.wav");
      const ff = (...a: string[]): void => { const p = spawnSync("ffmpeg", ["-v", "error", "-y", ...a]); expect(p.status, String(p.stderr)).toBe(0); };
      ff("-f", "lavfi", "-i", "testsrc=size=320x180:rate=30:duration=6", "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=48000:duration=6",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", mp4);
      ff("-f", "lavfi", "-i", "testsrc=size=320x180:rate=1:duration=1", "-frames:v", "1", png);
      ff("-f", "lavfi", "-i", "sine=frequency=500:sample_rate=48000:duration=3", wav);
      const f = await fluxoDoPlano([
        { tipo: "video", arq: mp4, inicio: 0, duracao: 5, faixa: 0 },
        { tipo: "imagem", arq: png, duracao: 4 },
        { tipo: "audio", arq: wav, inicio: 0, duracao: 3 },
      ], "sintetico", "teste", ["video", "imagem", "audio"]);
      expect(f.segundos).toHaveLength(5 + 4 + 3);
      expect(f.trechos.map(t => t.primeiro_segundo)).toEqual([0, 5, 9]);
      expect(f.trechos[0]!.sha256).toBe(createHash("sha256").update(readFileSync(mp4)).digest("hex"));
      const [v, im, au] = [f.segundos.slice(0, 5), f.segundos.slice(5, 9), f.segundos.slice(9)];
      expect(v[0]![2]).toBe(0);                                   // o primeiro quadro não tem anterior
      expect(v.slice(1).every(l => l[2]! > 0)).toBe(true);        // o testsrc mexe
      expect(v.every(l => l[4] !== null && Math.abs(l[6]! - (1000 / 24000) * GANHO_TIMBRE) < 0.01)).toBe(true);
      expect(im.slice(1).every(l => l[2] === 0 && l[4] === null)).toBe(true);   // a imagem parada não mexe e não tem som
      expect(au.every(l => l[0] === 0 && l[1] === 0 && l[4]! > 0)).toBe(true);  // o áudio sem imagem: o quadro preto
      const de_novo = await fluxoDoPlano([{ tipo: "video", arq: mp4, inicio: 0, duracao: 5, faixa: 0 }], "sintetico", "teste");
      expect(de_novo.segundos).toEqual(v);                        // determinístico
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
