// uso (da raiz), com a lib numa pasta fora do repo: npm install --prefix <pasta> gltf-validator@2.0.0-dev.3.10; NODE_PATH=<pasta>/node_modules node docs/itens3d/validar.cjs <item.gltf> <relatorio.json>
// Valida um .gltf pelo Khronos glTF-Validator (lib npm gltf-validator), com os recursos externos lidos da pasta do arquivo.
const v = require("gltf-validator"), fs = require("fs"), path = require("path");
const f = process.argv[2], dir = path.dirname(f);
v.validateBytes(new Uint8Array(fs.readFileSync(f)), { uri: path.basename(f), externalResourceFunction: u => Promise.resolve(new Uint8Array(fs.readFileSync(path.join(dir, decodeURIComponent(u))))) })
  .then(r => { fs.writeFileSync(process.argv[3], JSON.stringify(r, null, 1) + "\n"); console.log("VALIDADOR", r.validatorVersion, "erros", r.issues.numErrors, "avisos", r.issues.numWarnings, "infos", r.issues.numInfos, "dicas", r.issues.numHints); for (const m of r.issues.messages.slice(0, 8)) console.log(m.severity, m.code, m.pointer, m.message); });
