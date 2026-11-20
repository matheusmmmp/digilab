/* O gabarito do save de hoje, antes da CN3 (docs/PLANO_V3_CONTA.md, seção 5; a regra "mecânica nova entra atrás de chave desligada"):
   um roteiro do jogo pelo src/jogo.ts num armazenamento de mentira, com tudo o que o jogo grava no navegador (a chave, o tamanho e o
   SHA-256 de cada setItem, na ordem). Com a nuvem desligada (o build de sempre), o roteiro tem de gravar os mesmos bytes, na mesma ordem.
   O gabarito (test/gabaritos/cn3_save_desligado.json) foi gravado num commit próprio, antes do código da CN3:
     DIGILAB_GRAVAR_GABARITO=1 npx vitest run test/nuvem_desligada.test.ts */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { Motor } from "../motor/index.ts";
import { ligarProduto } from "../src/produto.ts";
import { CHAVE, type Armazenamento } from "../src/save.ts";
import { gravarPendente, iniciarJogo, jogoAtual, mudarMotor, trocarMotor } from "../src/jogo.ts";

const GABARITO = new URL("./gabaritos/cn3_save_desligado.json", import.meta.url);
type Gravacao = [chave: string, bytes: number, sha256: string];

function armaz(dados: Record<string, string> = {}): Armazenamento & { gravacoes: Gravacao[] } {
  const gravacoes: Gravacao[] = [];
  return {
    gravacoes,
    getItem: k => (k in dados ? dados[k]! : null),
    setItem(k, v) { dados[k] = v; gravacoes.push([k, v.length, createHash("sha256").update(v).digest("hex")]); },
  };
}

/** o roteiro: o pet de exemplo cuidado e o tempo passando; um ovo novo de semente fixa; o mesmo save aberto de novo */
function roteiro(): Record<string, Gravacao[]> {
  const a = armaz();
  iniciarJogo(a);
  for (const acao of ["alimentar", "brincar", "limpar", "acariciar"] as const) { mudarMotor(m => m.avancar(30)); mudarMotor(m => m.observar(acao)); }
  gravarPendente();
  trocarMotor(ligarProduto(new Motor(101, jogoAtual().motor.versao)), "novo");
  for (let i = 0; i < 6; i++) mudarMotor(m => m.avancar(20));
  mudarMotor(m => m.observar("alimentar"));
  const texto = a.getItem(CHAVE)!;
  const b = armaz({ [CHAVE]: texto });
  iniciarJogo(b);
  mudarMotor(m => m.avancar(15));
  mudarMotor(m => m.observar("brincar"));
  return { primeiro: a.gravacoes, reaberto: b.gravacoes };
}

describe("a nuvem desligada (CN3): o save de hoje sai byte a byte", () => {
  /* o registro do Tamer leva a hora do relogio: parada, o roteiro grava sempre os mesmos bytes */
  beforeEach(() => { vi.useFakeTimers({ toFake: ["Date"] }); vi.setSystemTime(Date.UTC(2026, 10, 20, 12)); });
  afterEach(() => { vi.useRealTimers(); });
  test("o roteiro grava as mesmas chaves, os mesmos bytes e na mesma ordem do gabarito", () => {
    const r = roteiro();
    if (process.env.DIGILAB_GRAVAR_GABARITO === "1" || !existsSync(GABARITO)) {
      if (process.env.DIGILAB_GRAVAR_GABARITO !== "1") throw new Error("falta o gabarito: grave com DIGILAB_GRAVAR_GABARITO=1");
      writeFileSync(GABARITO, JSON.stringify(r, null, 1) + "\n");
    }
    const g = JSON.parse(readFileSync(GABARITO, "utf-8")) as Record<string, Gravacao[]>;
    expect(r.primeiro.length).toBeGreaterThan(3);
    expect(r).toEqual(g);
  });
});
