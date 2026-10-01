/* Comando pelo chat (TAREFA_COMANDO_CHAT): a LLM propoe, o app valida e a acao entra no registro do pet NA HORA pelo mesmo
   caminho do botao Alimentar (execucao direta, decisao do Matheus em 2026-10-01 depois do gate da rodada 3). Registro
   identico ao do clique (mesmo evento, mesma assinatura); log de apresentacao na versao 2 lendo a 1; comando invalido para o
   pet nao entra. */
import { beforeAll, describe, expect, test } from "vitest";
import { Motor, VERSAO_PET } from "../motor/index.ts";
import type { Armazenamento } from "../src/save.ts";

/* localStorage em memoria antes de carregar os modulos (falaLivre.ts le a preferencia de modo ao carregar) */
const dados: Record<string, string> = {};
const armaz: Armazenamento = { getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } };
(globalThis as unknown as { localStorage: Armazenamento }).localStorage = armaz;

type FL = typeof import("../src/falaLivre.ts");
type Acoes = typeof import("../src/acoes.ts");
type Jogo = typeof import("../src/jogo.ts");
type Save = typeof import("../src/save.ts");
let fl: FL, ac: Acoes, jogo: Jogo, save: Save;
beforeAll(async () => {
  fl = await import("../src/falaLivre.ts"); ac = await import("../src/acoes.ts");
  jogo = await import("../src/jogo.ts"); save = await import("../src/save.ts");
});

/** o servidor falso: a proxima resposta de /api/fala-livre */
let resposta: Record<string, unknown> = {};
const pedidos: Record<string, unknown>[] = [];
(globalThis as unknown as { fetch: unknown }).fetch = async (rota: string, init?: { body?: string }) => {
  if (rota === "/api/fala-livre/status") return { ok: true, json: async () => ({ modelo: "falso" }) };
  pedidos.push(JSON.parse(init?.body ?? "{}"));
  return { ok: true, json: async () => resposta };
};
const tick = () => new Promise(r => setTimeout(r, 0));
async function conversar(txt: string, comando: string | null, extra: Record<string, unknown> = {}): Promise<void> {
  resposta = { fala: "Tá bom!", fatos_citados: [], fatos: [], estagio: "adulto", modelo: "falso", versao_prompt: "livre-v8", comando,
    verificacao: null, invencoes: [], ...extra };
  fl.enviarConversa(txt);
  for (let k = 0; k < 5 && fl.FL.pendente; k++) await tick();
}
function jogoNovo(m: Motor = save.petExemplo()): Motor {
  jogo.iniciarJogo(armaz);
  jogo.trocarMotor(m, "save");
  fl.FL.modo = "livre"; fl.FL.status = { modelo: "falso" }; fl.FL.sessao = [];
  dados[save.CHAVE + ".fala.jsonl"] = "";
  return jogo.jogoAtual().motor;
}

describe("validacao do comando no app", () => {
  test("so o catalogo AcaoDono; pet morto ou nascendo nao; acoes v4 so em pets v4+; tratar so com lesao", () => {
    const m = new Motor(7);
    expect(ac.validarComando(m, 0, "alimentar")).toBe("alimentar");
    for (const fora of ["treinar", "lutar", "Alimentar", "evoluir", "", null, undefined, 3, ["alimentar"]]) expect(ac.validarComando(m, 0, fora)).toBeNull();
    expect(ac.validarComando(m, 16, "alimentar")).toBeNull();                       /* nascendo */
    const morto = new Motor(7); morto.morte = { tick: 1, causa: "lesoes" };
    expect(ac.validarComando(morto, 0, "alimentar")).toBeNull();
    const v3 = new Motor(7, 3);
    expect(ac.validarComando(v3, 0, "petisco")).toBeNull();
    expect(ac.validarComando(v3, 0, "brincar")).toBe("brincar");
    expect(ac.validarComando(m, 0, "petisco")).toBe("petisco");
    expect(ac.validarComando(m, 0, "tratar_lesao")).toBeNull();                     /* sem lesao */
    const lesionado = new Motor(7); lesionado.lesionadoDesde = 5;
    expect(ac.validarComando(lesionado, 0, "tratar_lesao")).toBe("tratar_lesao");
  });
});

describe("log de apresentacao", () => {
  test("versao 2 le a 1 (comando null, nao executado) e recusa outra versao", () => {
    const v1 = { versao: 1, t: 500, situacao: "conversa", fala_jogador: "oi", fala: "Oi.", fatos_citados: [], fatos: [], estagio: "adulto",
      modelo: "x", versao_prompt: "livre-v2", semente: 1, verificacao: null };
    dados[save.CHAVE + ".fala.jsonl"] = JSON.stringify(v1) + "\n" + JSON.stringify({ ...v1, versao: 2, comando: "alimentar", comando_executado: true }) + "\n";
    const regs = fl.lerLog();
    expect(regs.length).toBe(2);
    expect(regs[0].comando).toBeNull(); expect(regs[0].comando_executado).toBe(false);
    expect(regs[1].comando).toBe("alimentar"); expect(regs[1].comando_executado).toBe(true);
    expect(fl.VERSAO_LOG).toBe(2);
    dados[save.CHAVE + ".fala.jsonl"] = JSON.stringify({ ...v1, versao: 3 }) + "\n";
    expect(() => fl.lerLog()).toThrow(/invalido/);
  });
});

describe("execucao direta e o registro do pet", () => {
  test('"vai comer" grava na hora exatamente o evento "d" do botao Alimentar (mesma assinatura)', async () => {
    const m = jogoNovo();
    expect(m.versao).toBe(VERSAO_PET);
    const antes = m.log.map(e => [...e]), n = antes.length;
    await conversar("vai comer", "alimentar");
    expect(pedidos[pedidos.length - 1].voz).toBe(true);
    /* o gemeo: o mesmo registro ate antes, mais o clique no botao Alimentar (Motor.observar, como acoes.agir) */
    const gemeo = Motor.reproduzir(m.semente, antes as never, m.versao);
    gemeo.observar("alimentar");
    expect(m.log.length).toBe(n + 1);
    expect(m.log[n]).toEqual([m.e.tick, "d", "alimentar"]);
    expect(m.log[n]).toEqual(gemeo.log[n]);
    expect(m.assinatura()).toBe(gemeo.assinatura());
    /* o log de apresentacao marca a execucao; o save saiu igual ao motor */
    const reg = fl.lerLog()[0];
    expect(reg.comando).toBe("alimentar"); expect(reg.comando_executado).toBe(true);
    expect(dados[save.CHAVE]).toBe(save.textoSave(m));
  });
  test("comando invalido para este pet: registro guarda a proposta, nada entra", async () => {
    const m = jogoNovo();
    const n = m.log.length;
    await conversar("cuida do machucado", "tratar_lesao");                          /* no catalogo, mas sem lesao */
    const reg = fl.lerLog()[0];
    expect(reg.comando).toBe("tratar_lesao"); expect(reg.comando_executado).toBe(false);
    await conversar("vai treinar", "treinar");                                        /* fora do catalogo (nunca vem do servidor) */
    expect(fl.lerLog()[1].comando).toBeNull(); expect(fl.lerLog()[1].comando_executado).toBe(false);
    await conversar("oi", null);
    expect(fl.lerLog()[2].comando_executado).toBe(false);
    expect(m.log.length).toBe(n);
  });
  test("pet morto quando a resposta chega: nada entra no registro", async () => {
    const m = jogoNovo();
    m.morte = { tick: m.e.tick, causa: "lesoes" };
    const n = m.log.length;
    await conversar("vai comer", "alimentar");
    expect(fl.lerLog()[0].comando).toBe("alimentar"); expect(fl.lerLog()[0].comando_executado).toBe(false);
    expect(m.log.length).toBe(n);
  });
  test("duas mensagens seguidas: duas acoes, na ordem", async () => {
    const m = jogoNovo();
    const n = m.log.length;
    await conversar("toma banho", "limpar");
    await conversar("vamos brincar", "brincar");
    expect(m.log.slice(n).map(e => e[2])).toEqual(["limpar", "brincar"]);
    expect(fl.lerLog().map(r => r.comando_executado)).toEqual([true, true]);
  });
});
