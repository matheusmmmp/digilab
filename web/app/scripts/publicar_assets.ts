/* Manda ao R2 os assets que ficam fora do repositório (CN5, docs/infra/DEPLOY_CN5.md, seção 6). Roda na máquina do Matheus, onde a pasta
   Assets está: o CI não tem os assets, só o código. O bucket é PRIVADO (D-CONTA-199 revista em 2026-11-21): o jogo só lê pelo Worker dos
   assets (servidor_web/deploy/worker_assets), com a URL assinada da CN4; a chave de cada objeto é o caminho que o jogo assina, sem a "/".
     node scripts/publicar_assets.ts                  # só lista o que iria (o padrão): nada sai da máquina
     node scripts/publicar_assets.ts --enviar         # manda o que mudou (compara o MD5 com o ETag do R2)
   A lista é a de scripts/assets_publicos.ts (a mesma do dev): os kits que não se redistribuem não sobem. As chaves vêm do ambiente, nunca do
   repositório: DIGILAB_R2_CONTA, DIGILAB_R2_BUCKET_ASSETS, DIGILAB_R2_CHAVE_ID, DIGILAB_R2_CHAVE_SEGREDO (um token do R2 com "Object Read &
   Write" só no bucket dos assets). --assets troca a pasta (o padrão é D:/Trab/digilab/Assets, ao lado do repositório). */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";
import { faltandoNaLista, listarAssetsPublicos } from "./assets_publicos.ts";
import { pedirR2 } from "./r2.ts";


const { values: a } = parseArgs({ options: {
  enviar: { type: "boolean", default: false },
  assets: { type: "string", default: fileURLToPath(new URL("../../../../Assets/", import.meta.url)) },
}, strict: true });

const achados = listarAssetsPublicos(a.assets);
const faltam = faltandoNaLista(a.assets, achados);
if (faltam.length) throw new Error(`faltam ${faltam.length} arquivos da lista fixa em ${a.assets}: ${faltam.slice(0, 5).join(", ")}`);
const total = achados.reduce((s, x) => s + x.bytes, 0);
console.log(`${achados.length} arquivos publicáveis, ${(total / 2 ** 20).toFixed(1)} MiB, de ${a.assets}`);

if (!a.enviar) {
  for (const x of achados) console.log(`  ${x.chave}  (${x.tipo}, ${x.bytes} B)`);
  console.log("só a lista: nada foi enviado (use --enviar)");
  process.exit(0);
}

const env = (n: string): string => {
  const v = process.env[n]?.trim();
  if (!v) throw new Error(`falta ${n} no ambiente`);
  return v;
};
const conta = env("DIGILAB_R2_CONTA"), bucket = env("DIGILAB_R2_BUCKET_ASSETS");
const cred = { id: env("DIGILAB_R2_CHAVE_ID"), segredo: env("DIGILAB_R2_CHAVE_SEGREDO") };

let enviados = 0, iguais = 0;
for (const x of achados) {
  const corpo = new Uint8Array(readFileSync(x.arquivo));
  const md5 = createHash("md5").update(corpo).digest("hex");
  const cab = await pedirR2(conta, cred, "HEAD", x.chave, bucket);
  if (cab.ok && cab.headers.get("etag")?.replaceAll('"', "") === md5) { iguais++; continue; }
  if (!cab.ok && cab.status !== 404) throw new Error(`HEAD ${x.chave}: ${cab.status}`);
  const r = await pedirR2(conta, cred, "PUT", x.chave, bucket, corpo, { "content-type": x.tipo });
  if (!r.ok) throw new Error(`PUT ${x.chave}: ${r.status} ${await r.text()}`);
  enviados++;
  console.log(`  enviado ${x.chave}`);
}
console.log(`pronto: ${enviados} enviados, ${iguais} já iguais no R2 (bucket ${bucket})`);
