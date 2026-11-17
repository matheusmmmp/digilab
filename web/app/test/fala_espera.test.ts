/* CONVERSA_PET, F2 (docs/PLANO_ANALISE_V3_CONVERSA_ESPERA.md, D-ES-2): a medida da espera em falaLivre.ts. Desligada por padrao; so liga com
   `?medir_espera=1` (lida uma vez, na carga do modulo). Servidor falso. Desligada: nada em `__medidaEspera`, o log de apresentacao e o pedido
   iguais aos de hoje. Ligada: um registro por chamada, os tempos na ordem certa, a fila no T4 e a espontanea descartada contada. */
import { afterEach, describe, expect, test, vi } from "vitest";
import { TPD } from "../motor/constantes.ts";
import { Motor } from "../motor/index.ts";
import { petDeTeste } from "../motor/pet_lab.ts";
import type { Armazenamento } from "../src/save.ts";

type FL = typeof import("../src/falaLivre.ts");
type Jogo = typeof import("../src/jogo.ts");
type Save = typeof import("../src/save.ts");
const g = globalThis as unknown as Record<string, unknown>;

const dados: Record<string, string> = {};
const armaz: Armazenamento = { getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } };
const pedidos: { rota: string; corpo: Record<string, any> }[] = [];
/* uma chamada da voz fica presa ate `soltar()` quando `segurar` esta ligado (para formar a fila e descartar a espontanea) */
let segurar = false;
const presas: (() => void)[] = [];
const soltar = (): void => { for (const f of presas.splice(0)) f(); };
const tick = () => new Promise(r => setTimeout(r, 0));
const resposta = { fala: "Tô com fome!", fatos_citados: [], fatos: [], estagio: "adulto", modelo: "falso", versao_prompt: "voz-v2", comando: null, latencia_s: 1.5 };

function fetchFalso(): void {
  g.fetch = async (rota: string, init?: { body?: string }) => {
    if (rota === "/api/fala-livre/status") return { ok: true, json: async () => ({ modelo: "falso" }) };
    pedidos.push({ rota, corpo: JSON.parse(init?.body ?? "{}") });
    if (rota === "/api/fala-livre" && segurar) await new Promise<void>(r => presas.push(r));
    return { ok: true, json: async () => (rota === "/api/fala-livre" ? resposta : { nao_suportadas: 0, manipulacao: false, afirmacoes: [], versao: "verif-v8" }) };
  };
}
let fl: FL, jogo: Jogo, save: Save;
async function carregar(url: string): Promise<Motor> {
  vi.resetModules();
  for (const k of Object.keys(dados)) delete dados[k];
  g.localStorage = armaz; g.location = { search: url }; delete g.__medidaEspera;
  fetchFalso(); pedidos.length = 0; segurar = false; presas.length = 0;
  fl = await import("../src/falaLivre.ts"); jogo = await import("../src/jogo.ts"); save = await import("../src/save.ts");
  const m = petDeTeste(101);
  for (let p = 0; p < Math.round(2 * TPD / 30); p++) {
    m.avancar(30);
    const mu = m.mundo!;
    if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
  }
  jogo.iniciarJogo(armaz); jogo.trocarMotor(m, "save");
  fl.FL.modo = "livre"; fl.FL.status = { modelo: "falso" }; fl.FL.sessao = []; fl.FL.fronteira = []; fl.FL.fila = [];
  return jogo.jogoAtual().motor;
}
async function esperar(): Promise<void> { for (let k = 0; k < 12 && (fl.FL.pendente || fl.FL.fila.length); k++) await tick(); await tick(); await tick(); }
afterEach(() => { delete g.__medidaEspera; delete g.location; });

describe("a medida da espera (falaLivre.ts)", () => {
  test("desligada: sem a chave na URL nao ha lista, nem `window.__medidaEspera`, e o log e o pedido sao os de sempre", async () => {
    await carregar("");
    expect(fl.MEDIDA_ESPERA).toBeNull();
    expect(g.__medidaEspera).toBeUndefined();
    fl.enviarConversa("oi"); await esperar();
    expect(fl.FL.ultimo?.fala).toBe("Tô com fome!");
    expect(pedidos.map(p => p.rota)).toEqual(["/api/fala-livre", "/api/fala-livre/verificar"]);
    expect(g.__medidaEspera).toBeUndefined();
    expect(fl.lerLog()).toHaveLength(1);
  });

  test("a chave com outro valor nao liga; sem `location` (try/catch) tambem nao", async () => {
    await carregar("?medir_espera=0");
    expect(fl.MEDIDA_ESPERA).toBeNull();
    vi.resetModules(); delete g.location;
    const f = await import("../src/falaLivre.ts");
    expect(f.MEDIDA_ESPERA).toBeNull();
  });

  test("ligada: um registro por conversa, com os campos na ordem t_envio <= t_chamada <= t_balao <= t_verif", async () => {
    await carregar("?medir_espera=1");
    expect(g.__medidaEspera).toBe(fl.MEDIDA_ESPERA);
    expect(fl.MEDIDA_ESPERA).toEqual([]);
    fl.enviarConversa("oi"); await esperar();
    const l = fl.MEDIDA_ESPERA!;
    expect(l).toHaveLength(1);
    const r = l[0];
    expect(Object.keys(r)).toEqual(["situacao", "t_envio", "t_chamada", "t_primeira", "t_balao", "t_verif", "descartada", "modelo", "erro", "latencia_s"]);
    expect(r.situacao).toBe("conversa");
    expect(r.descartada).toBe(false);
    expect(r.modelo).toBe("falso");
    expect(r.erro).toBeNull();
    expect(r.latencia_s).toBe(1.5);
    expect(r.t_chamada).not.toBeNull(); expect(r.t_balao).not.toBeNull(); expect(r.t_verif).not.toBeNull();
    expect(r.t_envio).toBeLessThanOrEqual(r.t_chamada!);
    expect(r.t_chamada!).toBeLessThanOrEqual(r.t_balao!);
    expect(r.t_balao!).toBeLessThanOrEqual(r.t_verif!);
    expect(r.t_primeira).toBe(r.t_balao);                       /* T2 = T1 hoje (sem streaming) */
    /* o jogo sai igual: o mesmo log de apresentacao (sem campos da medida) e a mesma versao */
    expect(fl.VERSAO_LOG).toBe(2);
    const linha = JSON.parse(dados[save.CHAVE + ".fala.jsonl"].trim());
    expect(Object.keys(linha)).not.toContain("t_envio");
    expect(JSON.stringify(pedidos)).not.toContain("t_envio");
  });

  test("a segunda conversa espera a primeira: o T4 (t_chamada - t_envio) aparece na fila", async () => {
    await carregar("?medir_espera=1");
    segurar = true;
    fl.enviarConversa("primeira"); await tick();
    fl.enviarConversa("segunda"); await tick();
    expect(fl.FL.fila).toHaveLength(1);
    await new Promise(r => setTimeout(r, 30));
    soltar(); await tick(); await tick(); await tick();
    soltar(); await esperar();
    const [a, b] = fl.MEDIDA_ESPERA!;
    expect(fl.MEDIDA_ESPERA).toHaveLength(2);
    expect(a.t_chamada! - a.t_envio).toBeLessThan(b.t_chamada! - b.t_envio);
    expect(b.t_chamada!).toBeGreaterThanOrEqual(a.t_balao!);    /* a fila: a segunda so sai depois do balao da primeira */
    expect(b.t_chamada! - b.t_envio).toBeGreaterThanOrEqual(25);
    expect(b.t_balao).not.toBeNull();
  });

  test("a espontanea que chega com uma chamada em curso e descartada e contada", async () => {
    const m = await carregar("?medir_espera=1");
    segurar = true;
    fl.enviarConversa("oi"); await tick();
    expect(fl.FL.pendente).toBe(true);
    fl.FL.ultMotivo = null; fl.FL.tEspontanea = 0;
    if (!m.motivo) m.motivo = { acao: "ocioso", fatores: [] } as unknown as typeof m.motivo;   /* o gatilho "acabei de decidir" so precisa de um motivo novo */
    fl.gatilhoFalaLivre(m);
    const esp = fl.MEDIDA_ESPERA!.filter(x => x.situacao === "espontanea");
    expect(esp).toHaveLength(1);
    expect(esp[0].descartada).toBe(true);
    expect(esp[0].t_chamada).toBeNull(); expect(esp[0].t_balao).toBeNull();
    soltar(); await esperar();
    expect(pedidos.filter(p => p.rota === "/api/fala-livre")).toHaveLength(1);   /* so a conversa chamou a voz */
    const conv = fl.MEDIDA_ESPERA!.filter(x => x.situacao === "conversa");
    expect(conv).toHaveLength(1); expect(conv[0].descartada).toBe(false);
    /* sem chamada em curso, a espontanea sai: registro com os tempos e sem descarte */
    segurar = false;
    fl.FL.ultMotivo = null; fl.FL.tEspontanea = 0;
    fl.gatilhoFalaLivre(m); await esperar();
    const esp2 = fl.MEDIDA_ESPERA!.filter(x => x.situacao === "espontanea");
    expect(esp2).toHaveLength(2);
    expect(esp2[1].descartada).toBe(false); expect(esp2[1].t_balao).not.toBeNull();
  });
});
