// Mede os modelos da tabela MODELOS (docs/TAREFA_V3_ITENS_3D.md, secao 4.2): triangulos, materiais, texturas, bytes. Uso, da raiz: node docs/itens3d/medir_kits.mjs web/app > docs/itens3d/kits_cc0_medidas.json
import { readFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
const APP = process.argv[2];
const src = readFileSync(join(APP, "src/telas/pet/ilha/modelos.ts"), "utf8");
const linhas = [...src.matchAll(/^\s+(\w+): \{ arquivos: (.+?), altura: ([\d.]+)/gm)];
const pngDim = f => { const b = readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
const out = [];
for (const [, nome, arqs, altura] of linhas) {
  const lista = [];
  for (const m of arqs.matchAll(/(qua|kay)\(([^)]*)\)/g)) for (const n of m[2].matchAll(/"([^"]+)"/g)) lista.push(`${m[1] === "qua" ? "quaternius" : "kaykit"}/${n[1]}.gltf`);
  for (const a of lista) {
    const f = join(APP, "public/kits3d", a), g = JSON.parse(readFileSync(f, "utf8"));
    let tri = 0, prims = 0, semTex = 0;
    const mats = g.materials ?? [];
    for (const me of g.meshes) for (const p of me.primitives) {
      prims++;
      const n = p.indices !== undefined ? g.accessors[p.indices].count : g.accessors[p.attributes.POSITION].count;
      if ((p.mode ?? 4) === 4) tri += n / 3;
      const mat = mats[p.material];
      if (!mat?.pbrMetallicRoughness?.baseColorTexture) semTex++;
    }
    const imgs = (g.images ?? []).map(i => { const [w, h] = pngDim(join(dirname(f), i.uri)); return `${i.uri} ${w}x${h}`; });
    const bytes = statSync(f).size + g.buffers.reduce((s, b) => s + statSync(join(dirname(f), b.uri)).size, 0);
    const extras = [...new Set(mats.flatMap(m => [m.normalTexture && "normal", m.pbrMetallicRoughness?.metallicRoughnessTexture && "mr", m.emissiveTexture && "emiss"].filter(Boolean)))];
    out.push({ nome, altura: +altura, arquivo: a, tri, prims, materiais: mats.length, prims_sem_textura: semTex, imagens: imgs, outros_mapas: extras, bytes_gltf_bin: bytes });
  }
}
console.log(JSON.stringify(out, null, 1));
