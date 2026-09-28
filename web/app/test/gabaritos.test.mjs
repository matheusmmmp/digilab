// Confere os gabaritos de paridade (gerar_gabaritos.mjs) contra o motor extraido do HTML atual:
// replay incremental de cada registro, e cada checkpoint gravado tem que bater (sha256 da
// assinatura e os contadores fora dela). Na Etapa 2 o mesmo teste roda contra o motor em TS.
//
// Rodar em Node (os gabaritos sao do V8 do Node; ver gerar_gabaritos.mjs).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { carregarMotor } from "./motor_html.mjs";
import { DIR, SIMBOLOS, checkpoints, sha256 } from "./gerar_gabaritos.mjs";

const M = carregarMotor(SIMBOLOS);
const arquivos = readdirSync(DIR).filter(f => /^vidas_.*\.json$/.test(f)).sort();

test("ha gabaritos (60 vidas, 15 grupos)", () => {
  assert.equal(arquivos.length, 15);
  const n = arquivos.reduce((s, f) => s + JSON.parse(readFileSync(DIR + f, "utf8")).vidas.length, 0);
  assert.equal(n, 60);
});

for (const f of arquivos) {
  test(f, () => {
    const g = JSON.parse(readFileSync(DIR + f, "utf8"));
    for (const v of g.vidas) {
      const { m, pts } = checkpoints(M, v.semente, v.versao, v.log);
      const rotulo = `${v.perfil} v${v.versao} @${v.semente}`;
      assert.equal(pts.length, v.checkpoints.length, `${rotulo}: numero de checkpoints`);
      pts.forEach((p, i) => assert.deepEqual(p, v.checkpoints[i], `${rotulo}: checkpoint no evento ${v.checkpoints[i].evento}`));
      assert.equal(sha256(m.assinatura()), sha256(v.assinaturaFinal), `${rotulo}: assinatura final`);
      /* e pelo caminho publico */
      assert.equal(M.Motor.reproduzir(v.semente, v.log, v.versao).assinatura(), v.assinaturaFinal, `${rotulo}: Motor.reproduzir`);
    }
  });
}
