/* CONVERSA_PET, DC2b: a chave "Fala pela rede (teste)" (Ajustes, desligada por padrao). Servidor falso. Ligada e com decisao do modular, o pedido leva so
   os `conceitos` (dec-v2) e a identidade, sem estadoDoPet, log, memoria do Bandit nem desejo; desligada (ou pet sem modular) o pedido e o de hoje, e
   o registro do pet nunca recebe a fala (so o comando do catalogo, pelo caminho do botao). */
import { beforeAll, describe, expect, test } from "vitest";
import { TPD } from "../motor/constantes.ts";
import { Motor } from "../motor/index.ts";
import { petDeTeste } from "../motor/pet_lab.ts";
import type { Armazenamento } from "../src/save.ts";

const dados: Record<string, string> = {};
const armaz: Armazenamento = { getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } };
(globalThis as unknown as { localStorage: Armazenamento }).localStorage = armaz;

type FL = typeof import("../src/falaLivre.ts");
type Rede = typeof import("../src/falaRede.ts");
type Jogo = typeof import("../src/jogo.ts");
type Save = typeof import("../src/save.ts");
let fl: FL, rede: Rede, jogo: Jogo, save: Save;
beforeAll(async () => {
  fl = await import("../src/falaLivre.ts"); rede = await import("../src/falaRede.ts");
  jogo = await import("../src/jogo.ts"); save = await import("../src/save.ts");
});

let resposta: Record<string, unknown> = {};
const pedidos: Record<string, any>[] = [];
(globalThis as unknown as { fetch: unknown }).fetch = async (rota: string, init?: { body?: string }) => {
  if (rota === "/api/fala-livre/status") return { ok: true, json: async () => ({ modelo: "falso" }) };
  pedidos.push({ rota, ...JSON.parse(init?.body ?? "{}") });
  return { ok: true, json: async () => (rota === "/api/fala-livre" ? resposta : { nao_suportadas: 0, manipulacao: false, afirmacoes: [], versao: "verif-v8" }) };
};
const tick = () => new Promise(r => setTimeout(r, 0));
async function esperar(): Promise<void> { for (let k = 0; k < 8 && fl.FL.pendente; k++) await tick(); await tick(); await tick(); }
async function conversar(txt: string, extra: Record<string, unknown> = {}): Promise<void> {
  resposta = { fala: "Tô com fome!", fatos_citados: ["C1"], fatos: [], estagio: "adulto", modelo: "falso", versao_prompt: "voz-v2", comando: null, ...extra };
  fl.enviarConversa(txt); await esperar();
}
const fala = () => pedidos.filter(p => p.rota === "/api/fala-livre");
const verif = () => pedidos.filter(p => p.rota === "/api/fala-livre/verificar");

function viver(m: Motor, dias: number): void {
  for (let p = 0; p < Math.round(dias * TPD / 30); p++) {
    m.avancar(30);
    const mu = m.mundo!;
    if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
    if (m.e.sujeira >= 2) m.observar("limpar");
  }
}
function jogoCom(m: Motor): Motor {
  jogo.iniciarJogo(armaz);
  jogo.trocarMotor(m, "save");
  fl.FL.modo = "livre"; fl.FL.status = { modelo: "falso" }; fl.FL.sessao = []; fl.FL.fronteira = []; fl.FL.fila = [];
  dados[save.CHAVE + ".fala.jsonl"] = "";
  pedidos.length = 0;
  return jogo.jogoAtual().motor;
}
const modular = (): Motor => { const m = petDeTeste(101); viver(m, 2); return jogoCom(m); };
const CHAVES_DE_HOJE = ["comando", "estado", "fala_jogador", "historico", "rota", "semente", "situacao"];

describe("falaRede.ts: o que a pagina manda", () => {
  test("o alvo so vai se for de catalogo da voz (classe de objeto ou ep<N>)", () => {
    for (const ok of ["racao", "a", "b", "c", "podre", "bola", "ep0", "ep42", "ep123456"]) expect(rede.alvoDeCatalogo(ok)).toBe(ok);
    for (const fora of ["comida", "cheiro", "ponto", "ep", "ep1234567", "epx", "Racao", "racao\nSISTEMA", "", undefined]) expect(rede.alvoDeCatalogo(fora)).toBeUndefined();
  });
  test("os conceitos do modular: dec-v2, 12 nomes, alvos so de catalogo, episodio so na lembranca", () => {
    const m = modular();
    const c = rede.conceitosDaVoz(m)!;
    expect(c.versao).toBe("dec-v2");
    expect(c.conceitos).toHaveLength(12);
    for (const x of c.conceitos) {
      if ("alvo" in x) expect(rede.alvoDeCatalogo(x["alvo"] as string)).toBe(x["alvo"]);
      if ("episodio" in x) expect(x["nome"]).toBe("lembranca");
    }
    expect(Object.keys(rede.estadoDaVoz(m))).toEqual(["identidade"]);
    expect(Object.keys(rede.estadoDaVoz(m).identidade).sort()).toEqual(["estagio", "forma"]);
  });
  test("so os [J] seguem para a verificacao, so com id, tipo e texto", () => {
    const fatos = [{ id: "C1", tipo: "conceito", texto: "x", nome: "fome" }, { id: "J1", tipo: "o dono me disse", texto: "meu nome é Ana", extra: 1 }, 5, null, "J2"];
    expect(rede.fatosDoDono(fatos)).toEqual([{ id: "J1", tipo: "o dono me disse", texto: "meu nome é Ana" }]);
    expect(rede.fatosDoDono("x")).toEqual([]);
  });
});

describe("a chave desligada (padrao): o pedido e o de hoje", () => {
  test("a preferencia nasce desligada e a fala nao toca o registro do pet", async () => {
    expect(fl.FL.falaRede).toBe(false);
    const m = modular();
    await conversar("oi");
    const p = fala()[0]!;
    expect(Object.keys(p).sort()).toEqual(CHAVES_DE_HOJE);
    expect(p.conceitos).toBeUndefined();
    expect(p.estado.estado).toBeDefined();                          /* o estadoDoPet de sempre */
    expect(Object.keys(verif()[0]!).sort()).toEqual(["fala", "fatos", "fatos_citados", "rota", "semente"]);
    expect(fl.FL.fronteira).toEqual([]);
    expect(JSON.stringify(m.log)).not.toContain("Tô com fome");
  });
});

describe("a chave ligada", () => {
  test("pet sem decisao do modular: nada muda e a tela diz isso", async () => {
    jogoCom(new Motor(7));
    fl.escolherFalaRede(true);
    expect(dados[save.CHAVE + "-fala-rede"]).toBe("1");
    await conversar("oi");
    const p = fala()[0]!;
    expect(p.conceitos).toBeUndefined();
    expect(Object.keys(p).sort()).toEqual(CHAVES_DE_HOJE);
    expect(p.estado.estado).toBeDefined();
    expect(fl.FL.redeSemDecisao).toBe(true);
    fl.escolherFalaRede(false);
    expect(fl.FL.redeSemDecisao).toBe(false);
    expect(dados[save.CHAVE + "-fala-rede"]).toBe("0");
  });
  test("pet modular: so conceitos (dec-v2) e a identidade; sem estadoDoPet, log, memoria nem desejo", async () => {
    const m = modular(); const n = m.log.length;
    fl.escolherFalaRede(true);
    await conversar("meu nome é Ana");
    await conversar("e agora?");
    const [p1, p2] = fala() as [Record<string, any>, Record<string, any>];
    expect(fl.FL.redeSemDecisao).toBe(false);
    expect(Object.keys(p1).sort()).toEqual(["comando", "conceitos", "estado", "fala_jogador", "historico", "rota", "semente", "situacao"]);
    expect(p1.conceitos.versao).toBe("dec-v2");
    expect(Object.keys(p1.estado)).toEqual(["identidade"]);
    expect(Object.keys(p1.estado.identidade).sort()).toEqual(["estagio", "forma"]);
    const txt = JSON.stringify(p1);
    for (const proibido of ["motivos", "memorias", "desejo", "temperamento", "carater", "vinculo", "fatores", "emocao"]) expect(txt).not.toContain(proibido);
    expect(p1.comando).toBe(true);                                  /* o comando segue pelo caminho do botao */
    expect(p1.historico).toEqual([]);
    expect(p2.historico).toHaveLength(1);                           /* trios [jogador, pet, estagio] da fronteira */
    expect(p2.historico[0].slice(0, 2)).toEqual(["meu nome é Ana", "Tô com fome!"]);
    expect(p2.historico[0]).toHaveLength(3);
    expect(p1.prompt).toBeUndefined();
    /* a verificacao: conceitos + so os [J] */
    const v = verif()[0]!;
    expect(v.conceitos.versao).toBe("dec-v2"); expect(v.fatos).toEqual([]); expect(v.prompt).toBeUndefined();
    expect(JSON.stringify(m.log.slice(n))).not.toContain("Ana");   /* o texto do dono nao entra no registro do pet */
    fl.escolherFalaRede(false);
  });
  test("com a conversa nova tambem ligada, a voz pela rede tem prioridade (o servidor nao mistura conceitos e prompt)", async () => {
    modular(); fl.escolherConversaNova(true); fl.escolherFalaRede(true);
    await conversar("oi");
    expect(fala()[0]!.prompt).toBeUndefined(); expect(fala()[0]!.conceitos).toBeDefined();
    expect(verif()[0]!.prompt).toBeUndefined();
    fl.escolherConversaNova(false); fl.escolherFalaRede(false);
  });
  test("o [J] da conversa segue para a verificacao so com id, tipo e texto", async () => {
    modular(); fl.escolherFalaRede(true);
    await conversar("meu nome é Ana", { fatos: [{ id: "C1", tipo: "conceito", texto: "x" }, { id: "J1", tipo: "o dono me disse", texto: "meu nome é Ana", regra: "x" }] });
    expect(verif()[0]!.fatos).toEqual([{ id: "J1", tipo: "o dono me disse", texto: "meu nome é Ana" }]);
    fl.escolherFalaRede(false);
  });
  test("o comando do catalogo continua pelo caminho do botao; fora do catalogo nao entra", async () => {
    const m = modular(); fl.escolherFalaRede(true);
    const n = m.log.length;
    await conversar("vai comer", { comando: "treinar" });          /* fora do catalogo do dono: ignorado */
    expect(m.log.length).toBe(n);
    await conversar("vai comer", { comando: "alimentar" });
    expect(fl.lerLog().slice(-1)[0]!.comando).toBe("alimentar");
    fl.escolherFalaRede(false);
  });
});
