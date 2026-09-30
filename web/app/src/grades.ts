/* Arte original em pixel (placeholders do HTML): o pet sem atlas, o ovo, a sujeira e os icones do palco que o
   Digimon UP nao tem (sono, raiva, pergunta, brilho, gota). Cor do corpo pelo traco de combate dominante. */
import type { TracoCombate } from "../motor/index.ts";

export const S: Record<string, string[]> = {
  bebe: [".....kkkk.....", "...kkbbbbkk...", "..kbbbbbbbbk..", ".kbbllbbbbbbk.", ".kbllbbbbbbbk.", "kbbbkwbbkwbbbk", "kbbbkkbbkkbbbk",
    "kbpbbbbbbbbpbk", "kbbbbbkkbbbbbk", ".kbbbbbbbbbbk.", "..kkbbbbbbkk..", "....kkkkkk...."],
  crianca: ["..kk........kk..", ".kbbk......kbbk.", ".kbbbkkkkkkbbbk.", "..kbbbbbbbbbbk..", ".kbbllbbbbbbbbk.", ".kbllbbbbbbbbbk.",
    "kbbbkwbbbbkwbbbk", "kbbbkkbbbbkkbbbk", "kbpbbbbbbbbbbpbk", "kbbbbbbkkbbbbbbk", ".kbbbbbbbbbbbbk.", ".kbbddddddddbbk.",
    "..kbddddddddbk..", "..kbbkkkkkkbbk..", "..kkk......kkk.."],
  adulto: [".......hh........", "......hhhk.......", "..kk..khhk...kk..", ".kbbk.kbbk..kbbk.", ".kbbbkkbbkkkbbbk.", "..kbbbbbbbbbbbk..",
    ".kbbllbbbbbbbbbk.", ".kbllbbbbbbbbbbk.", "kbbbkwbbbbbkwbbbk", "kbbbkkbbbbbkkbbbk", "kbpbbbbbbbbbbbpbk", "kbbbbbbkkkbbbbbbk",
    "kbbbbbbbbbbbbbbbk.kk", ".kbbddddddddbbbkkbbk", "..kbddddddddbbbbbbk.", "..kbbkkkkkkkbbkkkk..", "..kkk.......kkk....."],
  ovo: ["....kkkk....", "...kwwwwk...", "..kwwssswk..", ".kwwssssswk.", ".kwwwsswwwk.", "kwwwwwwwwwwk", "kwsswwwwsswk", "kwssswwssswk",
    "kwwsswwwsswk", "kwwwwwwwwwwk", ".kwwwwwwwwk.", ".kwwwwwwwwk.", "..kkwwwwkk..", "....kkkk...."],
  coco: ["...k...", "..kdk..", ".kdddk.", ".kdddk.", "kdddddk", "kkkkkkk"],
  coracao: [".kk.kk.", "krrkrrk", "krrrrrk", "krrrrrk", ".krrrk.", "..krk..", "...k..."],
  zz: ["kkkk...", "...k...", "..k....", ".k..kkk", "kkkk.k.", "....k..", "....kkk"],
  exclam: ["..kkk..", "..kyk..", "..kyk..", "..kyk..", "..kkk..", "..kyk..", "..kkk.."],
  pergunta: [".kkkk..", "kk..kk.", "....kk.", "...kk..", "..kk...", ".......", "..kk..."],
  raiva: ["k.k.k..", ".krk...", "kr.rk..", ".krk...", "k.k.k.."],
  nota: ["...kkk.", "...k.k.", "...k...", "...k...", ".kkk...", "kkkk...", ".kk...."],
  carne: ["....kk.", "...kwwk", ".kkkkk.", "kddddk.", "kddddk.", ".kkkk.."],
  brilho: ["...k...", "...y...", ".k.y.k.", "kyyyyyk", ".k.y.k.", "...y...", "...k..."],
  gota: ["...k...", "..kck..", ".kccck.", ".kccck.", "..kkk.."],
};
/* ampulheta original (a crianca fala com icones; o UP nao tem emote de demora) */
export const AMPULHETA = ["kkkkkkk", "kwwwwwk", ".kyyyk.", "..kyk..", "..kwk..", ".kwywk.", "kwyyywk", "kkkkkkk"];

const CORES: Record<TracoCombate, [string, string, string]> = {
  golpe: ["#F07A5A", "#FFB59E", "#C9533A"], bloqueio: ["#6C86C9", "#AFC0EC", "#4B63A3"], agarrao: ["#8FA84A", "#C6D98A", "#6B8030"],
  finta: ["#3FB5A6", "#90E0D3", "#2A8C7F"], carga: ["#F0B43A", "#FFE08A", "#C68A16"],
};
export type Paleta = Record<string, string>;
export function paleta(cor: TracoCombate): Paleta {
  const [b, l, d] = CORES[cor];
  return { k: "#1D2233", b, l, d, w: "#FFFFFF", p: "#FF8FA3", h: "#F5C542", s: "#7FB8E8", r: "#E8445A", y: "#F5C542", c: "#7FC8F0" };
}
/** desenha uma grade (1 unidade por pixel da grade); cor que falta aparece em magenta, como no HTML */
export function desenharGrade(ctx: CanvasRenderingContext2D, grade: string[], x0: number, y0: number, pal: Paleta,
  opts: { olhosFechados?: boolean; espelho?: boolean } = {}): void {
  const larg = Math.max(...grade.map(l => l.length));
  for (let y = 0; y < grade.length; y++) for (let x = 0; x < grade[y].length; x++) {
    let ch = grade[y][x]; if (ch === ".") continue;
    if (opts.olhosFechados && ch === "w") ch = "b";
    const px = opts.espelho ? x0 + (larg - 1 - x) : x0 + x;
    ctx.fillStyle = pal[ch] || "#FF00FF"; ctx.fillRect(px, y0 + y, 1, 1);
  }
}
/** grade como imagem (data URL) em escala inteira; cor fora da tabela falha alto */
const cacheGrade = new Map<string, { url: string; w: number; h: number }>();
export function imagemGrade(grade: string[], escala: number, cores: Paleta): { url: string; w: number; h: number } {
  const ch = JSON.stringify([grade, escala, cores]), pronta = cacheGrade.get(ch);
  if (pronta) return pronta;
  const r = desenharImagemGrade(grade, escala, cores);
  cacheGrade.set(ch, r);
  return r;
}
function desenharImagemGrade(grade: string[], escala: number, cores: Paleta): { url: string; w: number; h: number } {
  const c = document.createElement("canvas"); c.width = grade[0].length * escala; c.height = grade.length * escala;
  const g = c.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
  grade.forEach((l, y) => [...l].forEach((ch, x) => {
    if (ch === ".") return; if (!cores[ch]) throw new Error("cor da grade: " + ch);
    g.fillStyle = cores[ch]; g.fillRect(x * escala, y * escala, escala, escala);
  }));
  return { url: c.toDataURL(), w: c.width, h: c.height };
}
export const gradeDe = (est: string): string => est === "adolescente" ? "crianca" : est === "mega" ? "adulto" : est;
