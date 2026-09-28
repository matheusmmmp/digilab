// Paridade do motor em TypeScript (web/app/motor) com os gabaritos do motor do HTML (TAREFA_FRONT_TS,
// Etapa 2): mesmo replay incremental, mesmos checkpoints (sha256 da assinatura e contadores fora dela),
// mesma assinatura final. Criterio de aceite: 100% iguais.
//
// Node roda o .ts direto (remocao de tipos); os gabaritos sao do V8 do Node (ver gerar_gabaritos.mjs).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import * as M from "../motor/index.ts";
import { DIR, checkpoints, sha256 } from "./gerar_gabaritos.mjs";

const arquivos = readdirSync(DIR).filter(f => /^vidas_.*\.json$/.test(f)).sort();

test("motor TS: 60 vidas em 15 grupos", () => {
  assert.equal(arquivos.length, 15);
});

for (const f of arquivos) {
  test(`motor TS: ${f}`, () => {
    const g = JSON.parse(readFileSync(DIR + f, "utf8"));
    for (const v of g.vidas) {
      const { m, pts } = checkpoints(M, v.semente, v.versao, v.log);
      const rotulo = `${v.perfil} v${v.versao} @${v.semente}`;
      assert.equal(pts.length, v.checkpoints.length, `${rotulo}: numero de checkpoints`);
      pts.forEach((p, i) => assert.deepEqual(p, v.checkpoints[i], `${rotulo}: checkpoint no evento ${v.checkpoints[i].evento}`));
      assert.equal(sha256(m.assinatura()), sha256(v.assinaturaFinal), `${rotulo}: assinatura final`);
      assert.equal(M.Motor.reproduzir(v.semente, v.log, v.versao).assinatura(), v.assinaturaFinal, `${rotulo}: Motor.reproduzir`);
    }
  });
}

test("motor TS: registro gravado ao vivo = registro do gabarito (mesma vida, mesmas chamadas)", async () => {
  /* joga a mesma vida pelas chamadas publicas (avancar, observar, treinar, lutar, intervirGambit) a partir do
     registro e confere que o registro gravado sai igual (o registro e o save) */
  const g = JSON.parse(readFileSync(DIR + "vidas_v2_exigente.json", "utf8"));
  for (const v of g.vidas) {
    const m = new M.Motor(v.semente, v.versao);
    for (const [, tipo, x] of v.log) {
      if (tipo === "t") m.avancar(x);
      else if (tipo === "d") m.observar(x);
      else if (tipo === "l") m.lutar(x.r, x.s);
      else if (tipo === "g") m.intervirGambit(x.op, x.k);
      else if (tipo === "tr") m.treinar(x);
    }
    assert.deepEqual(m.log, v.log);
    assert.equal(m.assinatura(), v.assinaturaFinal);
  }
});
