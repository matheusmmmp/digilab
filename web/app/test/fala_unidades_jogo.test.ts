/* DC3d da CONVERSA_PET: a fala com conteudo no jogo.
     - a marca "fu" (so o pet de teste v16, uma vez, no comeco do registro): o modular decide com a `fala_unidades`; o replay le a marca;
     - sem a marca (todo pet de hoje), nada muda (o gabarito das vidas de hoje esta em dc3d_vidas_hoje.test.ts);
     - a preferencia de tela "Fala com conteudo (teste)" (CHAVE-lab-fala) vem desligada e so vale no ovo de teste chocado com ela ligada;
     - com a "Fala pela rede (teste)" ligada, quando a ultima decisao do modular foi uma unidade de fala, o pedido da voz leva o `dec-v3` com
       a intencao do conteudo; nas outras decisoes, o `dec-v2` de hoje. Servidor falso. */
import { beforeAll, describe, expect, test } from "vitest";
import { TPD } from "../motor/constantes.ts";
import { CONTEUDOS_FALA, Motor, VERSAO_PET_LAB, petDeTeste, type EventoRegistro } from "../motor/index.ts";
import type { Armazenamento } from "../src/save.ts";

const dados: Record<string, string> = {};
const armaz: Armazenamento = { getItem: k => (k in dados ? dados[k] : null), setItem(k, v) { dados[k] = v; } };
(globalThis as unknown as { localStorage: Armazenamento & { removeItem(k: string): void } }).localStorage =
  { ...armaz, removeItem(k: string) { delete dados[k]; } };

type FL = typeof import("../src/falaLivre.ts");
type Rede = typeof import("../src/falaRede.ts");
type Jogo = typeof import("../src/jogo.ts");
type Lab = typeof import("../src/lab.ts");
type Save = typeof import("../src/save.ts");
let fl: FL, rede: Rede, jogo: Jogo, lab: Lab, save: Save;
beforeAll(async () => {
  fl = await import("../src/falaLivre.ts"); rede = await import("../src/falaRede.ts");
  jogo = await import("../src/jogo.ts"); lab = await import("../src/lab.ts"); save = await import("../src/save.ts");
});

const PRODUTO = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true };
/** o ovo de teste como o laboratorio choca: as chaves do produto, a ponte da luta e, com `fala`, a marca "fu" */
function ovo(semente: number, fala: boolean): Motor {
  const m = petDeTeste(semente);
  m.ligarProduto(PRODUTO);
  m.ligarPonteLuta(true);
  if (fala) m.ligarFalaUnidades();
  return m;
}
/** o dono de cuidado (racao perto, limpeza, carinho), de 15 em 15 min; `cada` e chamado depois de cada passo */
function viver(m: Motor, dias: number, cada: (m: Motor) => void = () => {}): void {
  for (let p = 0; p < Math.round(dias * TPD / 15); p++) {
    m.avancar(15);
    const mu = m.mundo!;
    if (m.e.fome < .6 && p % 4 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
    if (m.e.sujeira >= 2 && p % 3 === 0) m.observar("limpar");
    if (p % 10 === 0) m.observar("acariciar");
    cada(m);
  }
}

describe("a marca \"fu\": o modular do pet de teste com a fala_unidades", () => {
  test("so no v16, uma vez, no comeco do registro; o replay le a marca e refaz o pet", () => {
    for (const v of [13, 15, 17, 19]) expect(() => new Motor(101, v).ligarFalaUnidades(), `v${v}`).toThrow(/só o pet de teste/);
    const m = ovo(101, true);
    expect(m.falaUnidades).toBe(true);
    expect(m.log.filter(e => e[1] === "fu")).toEqual([[m.log[0]![0], "fu", { fala: true }]]);
    expect(() => m.ligarFalaUnidades()).toThrow(/uma vez/);
    const tarde = ovo(202, false); tarde.avancar(15);
    expect(() => tarde.ligarFalaUnidades()).toThrow(/uma vez/);
    viver(m, 1);
    const r = Motor.reproduzir(101, m.log, VERSAO_PET_LAB);
    expect(r.falaUnidades).toBe(true);
    expect(r.assinatura()).toBe(m.assinatura());
    for (const ruim of [{ fala: false }, { fala: true, x: 1 }, {}, null, "fala"]) {
      const log = m.log.map(e => (e[1] === "fu" ? [e[0], "fu", ruim] : e)) as EventoRegistro[];
      expect(() => Motor.reproduzir(101, log, VERSAO_PET_LAB), JSON.stringify(ruim)).toThrow(/fala com conteúdo inválida/);
    }
  });

  test("com a marca, o chamar vira tres unidades de fala e as linhas de H sao as do conteudo; sem ela, o de hoje", () => {
    const com = ovo(303, true), sem = ovo(303, false);
    viver(com, 2); viver(sem, 2);
    expect(com.lab!.cd.fala_unidades).toBe(true);
    expect(sem.lab!.cd.fala_unidades).toBe(false);
    expect(Object.keys(com.lab!.plast.H).filter(b => b.startsWith("chamar"))).toEqual(CONTEUDOS_FALA.map(c => `chamar_atencao/${c}`));
    expect(Object.keys(sem.lab!.plast.H).filter(b => b.startsWith("chamar"))).toEqual(["chamar_atencao"]);
    const falas = com.lab!.motivos.filter(m => m["acao"] === "chamar_atencao");
    expect(falas.length).toBeGreaterThan(0);
    expect(falas.every(m => (CONTEUDOS_FALA as readonly unknown[]).includes((m["escolha"] as unknown[])[1]))).toBe(true);
    expect(sem.conteudoDaFala()).toBeNull();
    expect(com.assinatura()).not.toBe(sem.assinatura());
  });

  test("conteudoDaFala: o conteudo so quando a ultima decisao do modular foi uma fala", () => {
    const m = ovo(404, true), vistos = new Set<string>();
    let fora = 0;
    viver(m, 3, x => {
      const c = x.conteudoDaFala(), mo = x.lab!.ultimoMotivo;
      if (mo === null) return expect(c).toBeNull();
      if (mo["acao"] === "chamar_atencao") { expect(c).toBe((mo["escolha"] as unknown[])[1]); vistos.add(c!); } else { expect(c).toBeNull(); fora++; }
    });
    expect(vistos.size).toBeGreaterThan(0);
    expect(fora).toBeGreaterThan(0);
  });
});

describe("a preferencia de tela \"Fala com conteudo (teste)\" no laboratorio", () => {
  test("desligada por padrao; o ovo de teste so ganha a marca com ela ligada; o pet ja chocado nao muda", () => {
    expect(lab.falaComConteudo()).toBe(false);
    lab.descartarPetLab();
    const sem = lab.chocarOvoLab();
    expect(sem.log.some(e => e[1] === "fu")).toBe(false);
    lab.ligarFalaComConteudo(true);
    expect(lab.falaComConteudo()).toBe(true);
    const lido = lab.lerPetLab();                       // o pet ja chocado segue como esta no registro
    expect(lido.tipo === "ok" && lido.motor.falaUnidades).toBe(false);
    lab.descartarPetLab();
    const com = lab.chocarOvoLab();
    expect(com.log.filter(e => e[1] === "fu").length).toBe(1);
    expect(com.log.map(e => e[1]).slice(0, 3)).toEqual(["p", "pl", "fu"]);
    const relido = lab.lerPetLab();
    expect(relido.tipo === "ok" && relido.motor.falaUnidades).toBe(true);
    expect(dados[save.CHAVE + "-lab-fala"]).toBe("1");
    expect(dados[save.CHAVE] ?? null, "o pet ativo nao e tocado").toBeNull();
    lab.ligarFalaComConteudo(false); lab.descartarPetLab();
  });
});

describe("o pedido da voz com a fala com conteudo", () => {
  let resposta: Record<string, unknown> = {};
  const pedidos: Record<string, any>[] = [];
  beforeAll(() => {
    (globalThis as unknown as { fetch: unknown }).fetch = async (rota: string, init?: { body?: string }) => {
      if (rota === "/api/fala-livre/status") return { ok: true, json: async () => ({ modelo: "falso" }) };
      pedidos.push({ rota, ...JSON.parse(init?.body ?? "{}") });
      return { ok: true, json: async () => (rota === "/api/fala-livre" ? resposta : { nao_suportadas: 0, manipulacao: false, afirmacoes: [], versao: "verif-v9" }) };
    };
  });
  const tick = () => new Promise(r => setTimeout(r, 0));
  async function conversar(txt: string): Promise<void> {
    resposta = { fala: "Me dá um banho?", fatos_citados: ["P"], fatos: [], estagio: "crianca", modelo: "falso", versao_prompt: "voz-v3", comando: null };
    fl.enviarConversa(txt);
    for (let k = 0; k < 8 && fl.FL.pendente; k++) await tick();
    await tick(); await tick();
  }
  function jogoCom(m: Motor): void {
    jogo.iniciarJogo(armaz);
    jogo.trocarMotor(m, "save");
    fl.FL.modo = "livre"; fl.FL.status = { modelo: "falso" }; fl.FL.sessao = []; fl.FL.fronteira = []; fl.FL.fila = [];
    dados[save.CHAVE + ".fala.jsonl"] = "";
    pedidos.length = 0;
  }
  /** o pet de teste com a marca, vivido ate a ultima decisao ser uma fala (ou outra coisa, com `fala` false) */
  function ateUma(semente: number, fala: boolean): Motor {
    const m = ovo(semente, true);
    for (let p = 0; p < 4 * TPD / 15; p++) {
      viver(m, 15 / TPD);
      if (m.lab!.ultimoMotivo !== null && (m.conteudoDaFala() !== null) === fala) return m;
    }
    throw new Error("o pet nao chegou ao momento pedido");
  }

  test("conceitosDaVoz: a ultima decisao e uma fala -> dec-v3 com a intencao do conteudo; senao, o dec-v2 de hoje", () => {
    const f = ateUma(505, true), c = rede.conceitosDaVoz(f)!, d = f.conceitosDec("dec-v2")!;
    expect(c.versao).toBe("dec-v3");
    expect(c.intencao).toBe(f.conteudoDaFala());
    expect(c.k).toBe(d.k);
    expect(c.conceitos.map(x => x["nome"])).toEqual(d.conceitos.map(x => x.nome));
    const o = ateUma(505, false), c2 = rede.conceitosDaVoz(o)!;
    expect(c2.versao).toBe("dec-v2");
    expect(c2.intencao).toBe(o.conceitosDec("dec-v2")!.intencao);
    const hoje = ovo(505, false); viver(hoje, 1);
    expect(rede.conceitosDaVoz(hoje)!.versao).toBe("dec-v2");
  });

  test("com a 'Fala pela rede' ligada, a conversa manda o dec-v3 e a verificacao os mesmos conceitos; o registro do pet nao muda", async () => {
    const m = ateUma(101, true), log = JSON.stringify(m.log);
    jogoCom(m);
    fl.escolherFalaRede(true);
    await conversar("oi!");
    const [p] = pedidos.filter(x => x.rota === "/api/fala-livre");
    expect(p!["conceitos"]["versao"]).toBe("dec-v3");
    expect((CONTEUDOS_FALA as readonly string[]).includes(p!["conceitos"]["intencao"])).toBe(true);
    expect(p!["estado"]).toEqual(rede.estadoDaVoz(jogo.jogoAtual().motor));
    const [v] = pedidos.filter(x => x.rota === "/api/fala-livre/verificar");
    expect(v!["conceitos"]).toEqual(p!["conceitos"]);
    expect(JSON.stringify(jogo.jogoAtual().motor.log)).toBe(log);
    fl.escolherFalaRede(false);
  });
});
