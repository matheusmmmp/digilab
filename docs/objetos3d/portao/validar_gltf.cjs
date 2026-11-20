// O Khronos glTF-Validator num glTF separado (o pacote npm gltf-validator 2.0.0-dev.3.10, instalado fora do repositorio, sem dependencia nova
// no package.json). Grava o relatorio JSON, o mesmo formato do docs/lugares3d/<lugar>/validacao.json.
// uso: node validar_gltf.cjs <pasta onde o gltf-validator esta instalado> <arquivo.gltf> <saida.json>
const { createRequire } = require("node:module");
const fs = require("node:fs"), path = require("node:path");
const [mod, arq, sai] = process.argv.slice(2);
const validator = createRequire(path.join(path.resolve(mod), "package.json"))("gltf-validator");
const dir = path.dirname(arq);
validator.validateBytes(new Uint8Array(fs.readFileSync(arq)), {
  uri: path.basename(arq),
  externalResourceFunction: uri => new Promise((ok, falha) => {
    fs.readFile(path.join(dir, decodeURIComponent(uri)), (e, d) => (e ? falha(e.toString()) : ok(new Uint8Array(d))));
  }),
}).then(r => {
  fs.writeFileSync(sai, JSON.stringify(r, null, 1) + "\n");
  console.log("VALIDADOR erros", r.issues.numErrors, "avisos", r.issues.numWarnings, "infos", r.issues.numInfos);
}, e => { console.error(e); process.exit(1); });
