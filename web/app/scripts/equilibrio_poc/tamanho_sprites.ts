/* LUTA_POC: o tamanho dos sprites da luta por estagio, contra a arena (so leitura, sem luta). Le o atlas de clipes (fora do git, Assets) e a
   tabela das formas; mede a largura e a altura do Idle (o maior quadro) de cada forma e compara com a elipse da arena e o corpo do nucleo.
   uso (em web/app): node scripts/equilibrio_poc/tamanho_sprites.ts -> scripts/medicoes/equilibrio_poc/tamanho_sprites.json */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { ACAO_POC, ELIPSE_POC, EQ_POC, FORMAS_ARENA, MUNDO_POC, rivaisArena } from "../../motor/index.ts";
import { ESTAGIOS_LUTA } from "./comum.ts";

const atlas = JSON.parse(readFileSync("D:/Trab/digilab/Assets/digilab_atlas_up_clipes.json", "utf-8"));
const med = (xs: number[]) => { const s = [...xs].sort((a, b) => a - b); return s[Math.floor(s.length / 2)]; };
const out: Record<string, unknown> = {};
for (const e of ESTAGIOS_LUTA) {
  const ws: number[] = [], hs: number[] = [], faltam: string[] = [];
  for (const k of rivaisArena(e)) {
    const sp = atlas.sprites[k];
    const q = sp?.clipes?.Idle?.quadros?.filter((x: number[]) => x[2] > 0) ?? [];
    if (!q.length) { faltam.push(k); continue; }
    ws.push(Math.max(...q.map((x: number[]) => x[2]))); hs.push(Math.max(...q.map((x: number[]) => x[3])));
  }
  const w = med(ws), h = med(hs);
  out[e] = { formas: ws.length, faltam, largura_px: { mediana: w, min: Math.min(...ws), max: Math.max(...ws) }, altura_px: { mediana: h, min: Math.min(...hs), max: Math.max(...hs) },
    sprites_na_largura_da_arena: Math.round(2 * ELIPSE_POC.rx / w * 10) / 10, sprite_contra_corpo_do_nucleo: Math.round(w / (2 * EQ_POC.raio) * 100) / 100,
    distancia_de_entrada_em_sprites: Math.round(2 * ACAO_POC.entradaX / w * 10) / 10 };
  console.log(e, JSON.stringify(out[e]));
}
const saida = { tarefa: "LUTA_POC, o tamanho dos sprites contra a arena", atlas: atlas.atlas ?? "digilab_atlas_up_clipes.json", mundo: MUNDO_POC, elipse: ELIPSE_POC, corpo_px: 2 * EQ_POC.raio, entrada_px: 2 * ACAO_POC.entradaX, alcance_tiro_px: ACAO_POC.alcanceDist, estagios: out };
writeFileSync(fileURLToPath(new URL("../medicoes/equilibrio_poc/tamanho_sprites.json", import.meta.url)), JSON.stringify(saida, null, 1) + "\n");
