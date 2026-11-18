/* CONVERSA_PET, F2, D-ES-4 (a saida (0), Matheus, 2026-11-18): a chave `-fala-verif-depois` (desligada por padrao), lida na carga do modulo.
   Ligada e pela rede, o pedido da voz leva `verificar_na_chamada: false`, e a verificacao de depois do balao continua. Desligada, ou fora da
   rede, o pedido e o de hoje. Servidor falso. */
import { describe, expect, test, vi } from "vitest";
import { TPD } from "../motor/constantes.ts";
import { petDeTeste } from "../motor/pet_lab.ts";
import type { Armazenamento } from "../src/save.ts";

const g = globalThis as unknown as Record<string, unknown>;
const dados: Record<string, string> = {};
const armaz: Armazenamento = { getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } };
const pedidos: Record<string, any>[] = [];
const tick = () => new Promise(r => setTimeout(r, 0));

async function conversar(verifDepois: string | null, rede: boolean): Promise<Record<string, any>[]> {
  vi.resetModules();
  for (const k of Object.keys(dados)) delete dados[k];
  g.localStorage = armaz;
  const CHAVE = (await import("../src/save.ts")).CHAVE;
  if (verifDepois !== null) dados[CHAVE + "-fala-verif-depois"] = verifDepois;
  if (rede) dados[CHAVE + "-fala-rede"] = "1";
  pedidos.length = 0;
  g.fetch = async (rota: string, init?: { body?: string }) => {
    if (rota === "/api/fala-livre/status") return { ok: true, json: async () => ({ modelo: "falso" }) };
    pedidos.push({ rota, ...JSON.parse(init?.body ?? "{}") });
    return { ok: true, json: async () => (rota === "/api/fala-livre"
      ? { fala: "Tô com fome!", fatos_citados: ["C1"], fatos: [], estagio: "adulto", modelo: "falso", versao_prompt: "voz-v2", comando: null }
      : { nao_suportadas: 0, manipulacao: false, afirmacoes: [], versao: "verif-v8" }) };
  };
  const fl = await import("../src/falaLivre.ts"); const jogo = await import("../src/jogo.ts");
  const m = petDeTeste(101);
  for (let p = 0; p < Math.round(2 * TPD / 30); p++) {
    m.avancar(30);
    const mu = m.mundo!;
    if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
  }
  jogo.iniciarJogo(armaz); jogo.trocarMotor(m, "save");
  fl.FL.modo = "livre"; fl.FL.status = { modelo: "falso" }; fl.FL.sessao = []; fl.FL.fronteira = []; fl.FL.fila = [];
  fl.enviarConversa("oi");
  for (let k = 0; k < 12 && fl.FL.pendente; k++) await tick();
  await tick(); await tick();
  return pedidos;
}

describe("a chave da verificacao depois do balao (falaLivre.ts)", () => {
  test("ligada e pela rede: o pedido leva `verificar_na_chamada: false`, e a verificacao de depois do balao continua", async () => {
    const p = await conversar("1", true);
    const voz = p.filter(x => x.rota === "/api/fala-livre");
    expect(voz).toHaveLength(1);
    expect(voz[0].conceitos).toBeDefined();
    expect(voz[0].verificar_na_chamada).toBe(false);
    expect(p.filter(x => x.rota === "/api/fala-livre/verificar")).toHaveLength(1);
  });

  test.each([[null, true], ["0", true], ["1", false]])("chave %s, rede %s: o pedido e o de hoje, sem o campo", async (chave, rede) => {
    const p = await conversar(chave, rede);
    const voz = p.filter(x => x.rota === "/api/fala-livre");
    expect(voz).toHaveLength(1);
    expect("verificar_na_chamada" in voz[0]).toBe(false);
    expect(voz[0].conceitos !== undefined).toBe(rede);
  });
});
