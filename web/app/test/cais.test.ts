/* O cliente do cais (src/cais/cais.ts) contra um servidor falso com as rotas do servidor_web/src/envio/semanas.ts: a semana, as tabelas,
   os estados, a troca de semana e o segredo. E as contas puras da tela, o endereco e o cartao do nivel 10. Sem DOM e sem rede. */
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  CA, ESTAGIOS, abrirCais, abrirSegredo, andarSemana, atualizarCais, caisLigado, desligarCais, escolherEstagio, estadoDaSemana, faltaAte, fecharSegredo,
  horaDeBrasilia, ligarCais, linhasDaTela, marcoDoCais, semanasDoCais, temSemana, textoDaSemana, verTodas, type Linha, type Semanas,
} from "../src/cais/cais.ts";
import { CARTAO_DO_CAIS, cartaoDe, cartoesPendentes, ligarCartaoDoCais } from "../src/nivel.ts";
import { ENDERECO_DO_CAIS, caisDoEndereco, configDoEndereco, rotaDoEndereco } from "../src/rotas.ts";

const API = "http://api.teste";
/* quarta, 18/11/2026, 12:00 de Brasilia; a semana abre na segunda 16 e fecha no domingo 22, 23:59 */
const AGORA = Date.parse("2026-11-18T15:00:00Z");
const linha = (posicao: number, apelido: string, pontos: number, voce = false) => ({ posicao, apelido, pontos, rivais_vencidos: posicao, lutas_usadas: 10 + posicao, hora_dos_pontos: null, voce });

function servidor() {
  const s = {
    sessao: true, fora: false, agora: AGORA,
    fechadas: [{ semana: "2026-11-09", publicado_em: "2026-11-16T04:00:00.000Z" }],
    champion: Array.from({ length: 12 }, (_, i) => linha(i + 1, `Tamer#${i + 1}`, 300 - i * 20, i === 10)),
    segredo: "ab".repeat(32) as string | null,
    pedidos: [] as { caminho: string; credentials: unknown }[],
  };
  const json = (status: number, corpo: unknown): Response => new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });
  const buscar = async (url: string, init?: RequestInit): Promise<Response> => {
    if (s.fora) throw new TypeError("fetch failed");
    const caminho = url.slice(API.length);
    s.pedidos.push({ caminho, credentials: init?.credentials });
    if (caminho === "/semanas") return json(200, { atual: "2026-11-16", fecha_em: "2026-11-23T03:00:00.000Z", congela_em: "2026-11-23T04:00:00.000Z", fechadas: s.fechadas });
    const m = /^\/semanas\/(\d{4}-\d{2}-\d{2})\/(tabelas|segredo)$/.exec(caminho);
    if (!m) return json(404, { erro: "rota desconhecida" });
    const [, semana, o] = m, fechada = s.fechadas.some(f => f.semana === semana);
    if (o === "tabelas") {
      if (!s.sessao) return json(401, { erro: "sem sessão" });
      const estagios = { Rookie: [linha(1, "Tamer#7", 30)], Champion: fechada ? s.champion.slice(0, 3) : s.champion, Ultimate: [], Mega: [] };
      return json(200, { semana, estado: fechada ? "fechada" : "aberta", congela_em: "2026-11-23T04:00:00.000Z", estagios,
        total: { Rookie: 1, Champion: estagios.Champion.length, Ultimate: 0, Mega: 0 } });
    }
    if (!fechada) return json(404, { motivo: "semana_aberta", erro: "o segredo sai quando a semana congela" });
    return s.segredo === null ? json(404, { motivo: "sem_segredo", erro: "nenhuma luta" }) : json(200, { semana, segredo: s.segredo, publicado_em: "2026-11-16T04:00:00.000Z", como: "..." });
  };
  ligarCais({ api: API + "/", buscar, agora: () => s.agora });
  return s;
}
afterEach(() => { desligarCais(); ligarCartaoDoCais(false); vi.restoreAllMocks(); });

describe("abrir o cais", () => {
  it("busca a semana de agora e as tabelas, com a sessão, e abre no estágio do pet", async () => {
    const s = servidor();
    expect(caisLigado()).toBe(true);
    await abrirCais("Champion");
    expect(CA.passo).toBe("pronto");
    expect(CA.semana).toBe("2026-11-16");
    expect(CA.estagio).toBe("Champion");
    expect(CA.tabelas!.estado).toBe("aberta");
    expect(CA.tabelas!.total).toEqual({ Rookie: 1, Champion: 12, Ultimate: 0, Mega: 0 });
    expect(CA.tabelas!.estagios.Champion[10]).toEqual({ posicao: 11, apelido: "Tamer#11", pontos: 100, rivaisVencidos: 11, lutasUsadas: 21, voce: true });
    expect(s.pedidos.map(p => p.caminho)).toEqual(["/semanas", "/semanas/2026-11-16/tabelas"]);
    expect(s.pedidos.every(p => p.credentials === "include")).toBe(true);
  });
  it("o pet sem tabela (um In-Training) abre na primeira, a Rookie", async () => {
    servidor();
    await abrirCais("In-Training");
    expect(CA.estagio).toBe(ESTAGIOS[0]);
    await abrirCais(null);
    expect(CA.estagio).toBe("Rookie");
  });
  it("sem sessão (401): sem_conta, com a semana já na tela", async () => {
    const s = servidor(); s.sessao = false;
    await abrirCais("Champion");
    expect(CA.passo).toBe("sem_conta");
    expect(CA.tabelas).toBeNull();
    expect(CA.semana).toBe("2026-11-16");
  });
  it("o servidor não responde: sem_resposta, e Tentar de novo busca outra vez", async () => {
    const s = servidor(); s.fora = true;
    await abrirCais("Champion");
    expect(CA.passo).toBe("sem_resposta");
    s.fora = false;
    await atualizarCais();
    expect(CA.passo).toBe("pronto");
  });
  it("a resposta que o jogo não entende vira sem_resposta, com o erro no console", async () => {
    const s = servidor(), erro = vi.spyOn(console, "error").mockImplementation(() => {});
    s.champion = [{ ...linha(1, "Tamer#1", 10), pontos: "muitos" as unknown as number }];
    await abrirCais("Champion");
    expect(CA.passo).toBe("sem_resposta");
    expect(String(erro.mock.calls[0][0])).toContain("pontos");
  });
  it("desligado, abrir não busca nada: sem_resposta, com o erro no console", async () => {
    const erro = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(caisLigado()).toBe(false);
    await abrirCais("Champion");
    expect(CA.passo).toBe("sem_resposta");   /* a tela nunca monta desligada (TelaCais falha alto antes) */
    expect(String(erro.mock.calls[0][0])).toContain("desligado");
  });
});

describe("a tabela", () => {
  it("escolher o estágio fecha o Ver todas; um estágio sem tabela falha alto", async () => {
    servidor();
    await abrirCais("Champion");
    verTodas();
    expect(CA.todas).toBe(true);
    escolherEstagio("Rookie");
    expect(CA.estagio).toBe("Rookie");
    expect(CA.todas).toBe(false);
    expect(() => escolherEstagio("Fresh")).toThrow(/sem tabela/);
  });
  it("as linhas da tela: as de cima e a de quem olha depois do salto; dentro das de cima, sem salto", () => {
    const linhas: Linha[] = Array.from({ length: 12 }, (_, i) => ({ posicao: i + 1, apelido: `T${i + 1}`, pontos: 100 - i, rivaisVencidos: 1, lutasUsadas: 1, voce: i === 10 }));
    const a = linhasDaTela(linhas, 8, false);
    expect(a.topo.map(l => l.posicao)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
    expect(a.voce?.posicao).toBe(11);
    expect(linhasDaTela(linhas, 11, false).voce).toBeNull();
    expect(linhasDaTela(linhas.map(l => ({ ...l, voce: false })), 8, false).voce).toBeNull();
    const todas = linhasDaTela(linhas, 8, true);
    expect(todas.topo).toHaveLength(12);
    expect(todas.voce).toBeNull();
  });
});

describe("as semanas", () => {
  it("a seta de antes leva à semana fechada, e a de depois volta; fora da lista, nada", async () => {
    const s = servidor();
    await abrirCais("Champion");
    expect(temSemana(-1)).toBe(true);
    expect(temSemana(1)).toBe(false);
    await andarSemana(1);
    expect(CA.semana).toBe("2026-11-16");
    await andarSemana(-1);
    expect(CA.semana).toBe("2026-11-09");
    expect(CA.tabelas!.estado).toBe("fechada");
    expect(estadoDaSemana(CA.semanas!, CA.semana!, s.agora)).toBe("fechada");
    expect(temSemana(-1)).toBe(false);
    await andarSemana(1);
    expect(CA.semana).toBe("2026-11-16");
  });
  it("a semana de antes entra na lista enquanto não congelou (a folga), como 'fechando'", () => {
    const s: Semanas = { atual: "2026-11-16", fechaEm: Date.parse("2026-11-23T03:00:00Z"), congelaEm: Date.parse("2026-11-23T04:00:00Z"), fechadas: [] };
    const naFolga = Date.parse("2026-11-16T03:30:00Z"), depois = Date.parse("2026-11-16T04:00:00Z");
    expect(semanasDoCais(s, naFolga)).toEqual(["2026-11-09", "2026-11-16"]);
    expect(estadoDaSemana(s, "2026-11-09", naFolga)).toBe("fechando");
    expect(semanasDoCais(s, depois)).toEqual(["2026-11-16"]);
    expect(estadoDaSemana(s, "2026-11-16", depois)).toBe("aberta");
    expect(semanasDoCais({ ...s, fechadas: [{ semana: "2026-11-09", publicadoEm: 0 }, { semana: "2026-11-02", publicadoEm: 0 }] }, depois)).toEqual(["2026-11-02", "2026-11-09", "2026-11-16"]);
  });
  it("uma busca mais nova ganha da mais antiga", async () => {
    servidor();
    await abrirCais("Champion");
    const a = andarSemana(-1), b = atualizarCais();   /* a segunda busca e da semana de agora (a escolhida ainda nao trocou) */
    await Promise.all([a, b]);
    expect(CA.semana).toBe("2026-11-16");
    expect(CA.passo).toBe("pronto");
  });
});

describe("conferir a semana", () => {
  it("busca o segredo publicado da semana fechada, e voltar fecha", async () => {
    const s = servidor();
    await abrirCais("Champion");
    await andarSemana(-1);
    await abrirSegredo();
    expect(CA.segredo).toEqual({ tipo: "pronto", segredo: "ab".repeat(32), publicadoEm: Date.parse("2026-11-16T04:00:00Z") });
    expect(s.pedidos.at(-1)!.caminho).toBe("/semanas/2026-11-09/segredo");
    fecharSegredo();
    expect(CA.segredo).toBeNull();
  });
  it("a semana sem luta ranqueada não tem segredo; a rede caída diz sem_resposta", async () => {
    const s = servidor(); s.segredo = null;
    await abrirCais("Champion");
    await andarSemana(-1);
    await abrirSegredo();
    expect(CA.segredo).toEqual({ tipo: "sem_segredo" });
    s.fora = true;
    await abrirSegredo();
    expect(CA.segredo).toEqual({ tipo: "sem_resposta" });
  });
  it("trocar de semana enquanto o segredo vem descarta a resposta", async () => {
    servidor();
    await abrirCais("Champion");
    await andarSemana(-1);
    const a = abrirSegredo(), b = andarSemana(1);
    await Promise.all([a, b]);
    expect(CA.segredo).toBeNull();
    expect(CA.semana).toBe("2026-11-16");
  });
});

describe("as contas da tela", () => {
  it("o texto da semana, no mesmo mês e virando o mês e o ano", () => {
    expect(textoDaSemana("2026-11-16")).toBe("16 a 22 de novembro");
    expect(textoDaSemana("2026-11-30")).toBe("30 de novembro a 6 de dezembro");
    expect(textoDaSemana("2026-12-28")).toBe("28 de dezembro a 3 de janeiro");
    expect(() => textoDaSemana("semana")).toThrow(/AAAA-MM-DD/);
  });
  it("quanto falta, em duas unidades", () => {
    const t = Date.parse("2026-11-23T03:00:00Z");
    expect(faltaAte(t, t - (2 * 24 + 4) * 3600_000)).toBe("2 d 4 h");
    expect(faltaAte(t, t - (3 * 60 + 12) * 60_000)).toBe("3 h 12 min");
    expect(faltaAte(t, t - 8 * 60_000 + 1)).toBe("8 min");
    expect(faltaAte(t, t)).toBe("");
  });
  it("a hora de Brasília", () => {
    expect(horaDeBrasilia(Date.parse("2026-11-16T04:00:00Z"))).toBe("16/11, à 1h");
    expect(horaDeBrasilia(Date.parse("2026-11-16T16:05:00Z"))).toBe("16/11, às 13h05");
  });
  it("o marco do build: vazio dá o 10; fora de 1 a 10 falha alto", () => {
    expect(marcoDoCais("")).toBe(10);
    expect(marcoDoCais("7")).toBe(7);
    for (const ruim of ["0", "11", "7.5", "sete"]) expect(() => marcoDoCais(ruim)).toThrow(/VITE_DIGILAB_MARCO_RANQUEADA/);
  });
});

describe("o endereço e o cartão do nível 10", () => {
  it("#/cais é do cais, e não de um destino nem dos Ajustes", () => {
    expect(ENDERECO_DO_CAIS).toBe("#/cais");
    for (const h of ["#/cais", "#cais", "#/cais/"]) expect(caisDoEndereco(h)).toBe(true);
    for (const h of ["#/cais/semana", "#/lutar/arena", "#/config", ""]) expect(caisDoEndereco(h)).toBe(false);
    expect(rotaDoEndereco("#/cais")).toBeNull();
    expect(configDoEndereco("#/cais")).toBeNull();
  });
  it("desligado, o marco 10 não tem cartão; ligado, é o do cais", () => {
    const estado = { marcos: [1, 2, 3, 4, 10], cartoes: [1, 2, 3, 4] };
    expect(cartaoDe(10)).toBeUndefined();
    expect(cartoesPendentes(estado)).toEqual([]);
    ligarCartaoDoCais(true);
    expect(cartaoDe(10)).toBe(CARTAO_DO_CAIS);
    expect(CARTAO_DO_CAIS).toMatchObject({ n: 10, titulo: "Cais", frase: "Veja o ranking da semana.", cais: true });
    expect(CARTAO_DO_CAIS.frase.split(" ").length).toBeLessThanOrEqual(8);
    expect(cartoesPendentes(estado)).toEqual([10]);
  });
});

describe("o cais na vista 3D (trancas.ts)", () => {
  it("desligado de partida; a versão só sobe quando algo muda", async () => {
    const { CAIS, definirCais } = await import("../src/trancas.ts");
    expect(CAIS).toMatchObject({ ligado: false, trancado: true });
    const v0 = CAIS.versao;
    expect(definirCais(false, true)).toBe(false);
    expect(CAIS.versao).toBe(v0);
    expect(definirCais(true, true)).toBe(true);
    expect(definirCais(true, false)).toBe(true);
    expect(definirCais(true, false)).toBe(false);
    expect(CAIS).toMatchObject({ ligado: true, trancado: false, versao: v0 + 2 });
    definirCais(false, true);
  });
});
