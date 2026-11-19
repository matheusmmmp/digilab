/* As recompensas e o mural (MMO7): a semana ISO e a temporada; os recordes que só sobem, com o Salão juntado de pets diferentes; os
   títulos, os selos, os enfeites e o Respeito saídos das tabelas congeladas; as rotas; o envio aceito gravando o que a conferência refez;
   e apagar a conta. A vida é a da MMO3 (test/gabaritos/vida_101.json). */
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, it } from "vitest";
import { Motor, MEDALHAS } from "../../web/app/motor/index.ts";
import { refazerComLutas } from "../../web/app/src/ranking/pontos.ts";
import { Tamer, VERSAO_TAMER } from "../../web/app/src/tamer.ts";
import { MIGRACOES, VERSAO_BANCO, type Banco } from "../src/conta/banco.ts";
import { conferirAqui, type Conferidor } from "../src/envio/conferidor.ts";
import { conferir, type FronteiraVista } from "../src/envio/conferir.ts";
import { congelaEm } from "../src/envio/semanas.ts";
import {
  DIAS_DO_TITULO_NO_PERFIL, ENFEITE_ATE, EPOCA_TEMPORADAS, gravarFronteira, LINHAS_DO_MURAL, RESPEITO, respeitoConferido, semanaIso,
  semanasDaTemporada, temporadaDe, textoDoTitulo,
} from "../src/premios/premios.ts";
import { contar, criarConta, montar, Navegador, type Montado } from "./navegador.ts";

type Evento = [number, string, ...unknown[]];
interface Save { semente: number; log: Evento[]; versao: number }
const VIDA: Save = JSON.parse(readFileSync(new URL("./gabaritos/vida_101.json", import.meta.url), "utf-8"));
const DIA_MS = 86_400_000;
const SEMANA = "2026-11-16", SEGUINTE = "2026-11-23";
const idDaConta = (n: Navegador) => n.pedir("/conta").then(r => r.json()).then((d: any) => d.conta.id as string);
const vazia = (): FronteiraVista => ({ torre: 0, fabrica: 0, salao: [], tentativasSalao: [] });

let M: Montado, nav: Navegador, csrf: string, eu: string;
beforeEach(async () => {
  M = montar(undefined, { DIGILAB_CONVIDADOS: ["ana", "caio"].map(u => "falso:" + u).join(" ") });
  nav = new Navegador(M.app);
  csrf = await criarConta(nav);
  eu = await idDaConta(nav);
});

/** uma conta direto no banco */
let nContas = 0;
function conta(banco: Banco): string {
  const id = `conta-${++nContas}`;
  banco.prepare("INSERT INTO contas (id, apelido, criada_em, idade) VALUES (?, ?, 0, '18_ou_mais')").run(id, `Gabumon#${2000 + nContas}`);
  return id;
}
/** uma semana congelada direto no banco: as linhas [conta, pontos] de cada estágio, já na ordem */
function congelar(banco: Banco, semana: string, estagios: Record<string, [string, number][]>, publicadoEm = congelaEm(semana)): void {
  banco.prepare("INSERT INTO segredos_semana (semana, segredo, criado_em, publicado_em) VALUES (?, ?, 0, ?)").run(semana, "ab".repeat(32), publicadoEm);
  for (const [estagio, linhas] of Object.entries(estagios)) linhas.forEach(([c, pontos], i) =>
    banco.prepare(`INSERT INTO tabelas_semana (semana, estagio, posicao, conta_id, pontos, rivais_vencidos, lutas_usadas, hora_dos_pontos)
      VALUES (?, ?, ?, ?, ?, 1, 1, NULL)`).run(semana, estagio, i + 1, c, pontos));
}
function selo(banco: Banco, dia: string, c: string, posicao = 1): void {
  banco.prepare("INSERT INTO tabelas_dia (dia, posicao, conta_id, vitorias, vida_ultima, terminou_em, selo) VALUES (?, ?, ?, 3, 10, 0, 1)").run(dia, posicao, c);
}

describe("as contas puras", () => {
  it("a semana ISO da segunda-feira", () => {
    expect(semanaIso("2026-11-09")).toBe(46);
    expect(semanaIso("2026-11-16")).toBe(47);
    expect(semanaIso("2026-12-28")).toBe(53);
    expect(semanaIso("2027-01-04")).toBe(1);
    expect(semanaIso("2025-12-29")).toBe(1);
    expect(textoDoTitulo("Rookie", "2026-11-09")).toBe("Campeão Rookie da semana 46");
  });
  it("a temporada: 4 semanas a partir da época; a semana de antes fica na 1", () => {
    expect(EPOCA_TEMPORADAS).toBe("2026-11-02");
    expect(temporadaDe("2026-11-02")).toBe(1);
    expect(temporadaDe("2026-11-23")).toBe(1);
    expect(temporadaDe("2026-11-30")).toBe(2);
    expect(temporadaDe("2026-10-26")).toBe(1);
    expect(semanasDaTemporada(2)).toEqual({ de: "2026-11-30", ate: "2026-12-21" });
    expect(() => semanasDaTemporada(0)).toThrow();
  });
  it("o Respeito conferido: os valores da tabela do plano", () => {
    expect(RESPEITO).toEqual({ titulo_semana: 100, selo_dia: 20 });
    expect(respeitoConferido(2, 3)).toBe(260);
  });
});

describe("o banco", () => {
  it("a migração 7 traz os recordes e as lutas do Salão vistas, vazias", () => {
    expect(VERSAO_BANCO).toBeGreaterThanOrEqual(7);
    expect(MIGRACOES[6]).toContain("CREATE TABLE recordes");
    expect(contar(M.banco, "recordes")).toBe(0);
    expect(contar(M.banco, "salao_vistas")).toBe(0);
  });
});

describe("os recordes", () => {
  it("só sobem; a hora é a do servidor em que o valor foi visto", () => {
    expect(gravarFronteira(M.banco, eu, 1, { ...vazia(), torre: 3, fabrica: 2 }, "e1", 1000)).toEqual(["torre", "fabrica"]);
    expect(gravarFronteira(M.banco, eu, 1, { ...vazia(), torre: 2, fabrica: 2 }, "e2", 2000)).toEqual([]);
    expect(gravarFronteira(M.banco, eu, 1, { ...vazia(), torre: 5 }, "e3", 3000)).toEqual(["torre"]);
    const r = M.banco.prepare("SELECT inst, valor, visto_em, envio_id FROM recordes WHERE conta_id = ? ORDER BY inst").all(eu);
    expect(r).toEqual([{ inst: "fabrica", valor: 2, visto_em: 1000, envio_id: "e1" }, { inst: "torre", valor: 5, visto_em: 3000, envio_id: "e3" }]);
  });
  it("o Salão conta só até onde cada luta foi vista no replay do pet que lutou", () => {
    /* a tentativa do Tamer: o pet 1 no In-Training, o 2 no Rookie, o 3 no Champion, todos dizem que venceram */
    const tentativa = { n: 1, lutas: [{ pet: 1, s: 11, venceu: true }, { pet: 2, s: 22, venceu: true }, { pet: 3, s: 33, venceu: true }] };
    /* o envio do pet 1 só vê a luta dele: 1 estágio */
    gravarFronteira(M.banco, eu, 1, { ...vazia(), salao: [{ s: 11, tick: 5, venceu: true }], tentativasSalao: [tentativa] }, "e1", 1);
    expect(M.banco.prepare("SELECT valor FROM recordes WHERE conta_id = ? AND inst = 'salao'").get(eu)).toEqual({ valor: 1 });
    /* o pet 3 chega antes do 2: ainda 1 (o 2 não foi visto) */
    gravarFronteira(M.banco, eu, 3, { ...vazia(), salao: [{ s: 33, tick: 9, venceu: true }], tentativasSalao: [tentativa] }, "e2", 2);
    expect(M.banco.prepare("SELECT valor FROM recordes WHERE conta_id = ? AND inst = 'salao'").get(eu)).toEqual({ valor: 1 });
    /* o pet 2 chega, e o replay dele diz que perdeu (o Tamer dizia que venceu): continua 1 */
    gravarFronteira(M.banco, eu, 2, { ...vazia(), salao: [{ s: 22, tick: 7, venceu: false }], tentativasSalao: [tentativa] }, "e3", 3);
    expect(M.banco.prepare("SELECT valor FROM recordes WHERE conta_id = ? AND inst = 'salao'").get(eu)).toEqual({ valor: 1 });
    /* outra tentativa, com o pet 2 vencendo de verdade: 3 */
    const outra = { n: 2, lutas: [{ pet: 1, s: 12, venceu: true }, { pet: 2, s: 23, venceu: true }, { pet: 3, s: 34, venceu: true }] };
    gravarFronteira(M.banco, eu, 1, { ...vazia(), salao: [{ s: 12, tick: 8, venceu: true }], tentativasSalao: [tentativa, outra] }, "e4", 4);
    gravarFronteira(M.banco, eu, 2, { ...vazia(), salao: [{ s: 23, tick: 9, venceu: true }], tentativasSalao: [tentativa, outra] }, "e5", 5);
    gravarFronteira(M.banco, eu, 3, { ...vazia(), salao: [{ s: 34, tick: 10, venceu: true }], tentativasSalao: [tentativa, outra] }, "e6", 6);
    expect(M.banco.prepare("SELECT valor, envio_id FROM recordes WHERE conta_id = ? AND inst = 'salao'").get(eu)).toEqual({ valor: 3, envio_id: "e6" });
  });
});

describe("a conferência", () => {
  it("devolve o que a Fronteira do pet e do Tamer mostram (a vida dos testes não foi à Fronteira)", () => {
    const m = Motor.reproduzir(VIDA.semente, VIDA.log.slice(0, 50) as never, VIDA.versao), t = new Tamer();
    MEDALHAS.slice(0, 3).forEach((x, i) => t.ganhar(x.id, m, Date.UTC(2026, 10, 15) + i));
    const r = conferir({ pet: { semente: VIDA.semente, log: VIDA.log as never, versao: VIDA.versao }, tamer: { versao: VERSAO_TAMER, log: t.log } });
    expect(r.resultado).toBe("aceito");
    if (r.resultado !== "aceito") return;
    expect(r.fronteira).toEqual({ torre: 0, fabrica: 0, salao: [], tentativasSalao: [] });
    expect(refazerComLutas(VIDA.semente, VIDA.versao, VIDA.log as never, []).salao).toEqual([]);
  });
  it("o envio aceito grava os recordes que a conferência devolve; o recusado, nada", async () => {
    let fronteira = { ...vazia(), torre: 4, fabrica: 1 };
    const falso: Conferidor = async (e, x) => { const r = await conferirAqui(e, x); return r.resultado === "aceito" ? { ...r, fronteira } : r; };
    M = montar(falso);
    nav = new Navegador(M.app); csrf = await criarConta(nav); eu = await idDaConta(nav);
    const m = Motor.reproduzir(VIDA.semente, VIDA.log.slice(0, 50) as never, VIDA.versao), t = new Tamer();
    MEDALHAS.slice(0, 3).forEach((x, i) => t.ganhar(x.id, m, Date.UTC(2026, 10, 15) + i));
    const envio = (log: unknown[]) => nav.json("POST", "/envios", { pet: { semente: VIDA.semente, log, versao: VIDA.versao }, tamer: { versao: VERSAO_TAMER, log: t.log } }, csrf);
    expect((await envio(VIDA.log.slice(0, 40))).status).toBe(201);
    expect(contar(M.banco, "recordes")).toBe(2);
    fronteira = { ...vazia(), torre: 9 };
    expect((await envio([[0, "nada"]])).status).toBe(422);
    expect(M.banco.prepare("SELECT valor FROM recordes WHERE conta_id = ? AND inst = 'torre'").get(eu)).toEqual({ valor: 4 });
  });
});

describe("as rotas", () => {
  it("pedem a sessão", async () => {
    const sem = new Navegador(M.app);
    expect((await sem.pedir("/premios")).status).toBe(401);
    expect((await sem.pedir("/mural")).status).toBe(401);
  });

  it("sem nada ganho, tudo vazio e o Respeito 0", async () => {
    const d = await (await nav.pedir("/premios")).json() as any;
    expect(d).toMatchObject({ titulo_atual: [], titulos: [], selos: { total: 0, lista: [] }, enfeites: [], respeito: { conferido: 0 },
      recordes: { torre: null, fabrica: null, salao: null }, temporada_atual: 1 });
    const mu = await (await nav.pedir("/mural")).json() as any;
    expect(mu).toEqual({ recordes: { torre: [], fabrica: [], salao: [] }, total: { torre: 0, fabrica: 0, salao: 0 }, titulos: [] });
  });

  it("o título da semana: o 1º com pontos de cada tabela; no perfil por uma semana, no mural para sempre", async () => {
    const outro = conta(M.banco);
    congelar(M.banco, SEMANA, { Rookie: [[eu, 30], [outro, 10]], Champion: [[outro, 20], [eu, 20]], Ultimate: [[eu, 0]] });
    M.relogio.t = congelaEm(SEMANA) + DIA_MS;
    const d = await (await nav.pedir("/premios")).json() as any;
    /* o Ultimate com 0 pontos não é título */
    expect(d.titulos.map((t: any) => t.texto)).toEqual(["Campeão Rookie da semana 47"]);
    expect(d.titulo_atual).toHaveLength(1);
    expect(d.titulo_atual[0].no_perfil_ate).toBe(new Date(congelaEm(SEMANA) + DIAS_DO_TITULO_NO_PERFIL * DIA_MS).toISOString());
    expect(d.respeito).toMatchObject({ conferido: 100, titulos: 100, selos: 0 });
    M.relogio.t = congelaEm(SEMANA) + DIAS_DO_TITULO_NO_PERFIL * DIA_MS;
    const depois = await (await nav.pedir("/premios")).json() as any;
    expect(depois.titulo_atual).toEqual([]);
    expect(depois.titulos).toHaveLength(1);
    const mu = await (await nav.pedir("/mural")).json() as any;
    expect(mu.titulos.map((t: any) => [t.estagio, t.voce])).toEqual([["Rookie", true], ["Champion", false]]);
  });

  it("o selo Top do dia vem das tabelas do dia e soma 20 de Respeito cada", async () => {
    selo(M.banco, "2026-11-16", eu, 2); selo(M.banco, "2026-11-17", eu);
    const d = await (await nav.pedir("/premios")).json() as any;
    expect(d.selos.total).toBe(2);
    expect(d.selos.lista.map((x: any) => x.dia)).toEqual(["2026-11-17", "2026-11-16"]);
    expect(d.respeito.conferido).toBe(2 * RESPEITO.selo_dia);
  });

  it("o enfeite da temporada: um por temporada, para os 10 primeiros com pontos", async () => {
    const outros = Array.from({ length: ENFEITE_ATE + 1 }, () => conta(M.banco));
    /* semana 1 da temporada 1: eu em 3º do Rookie; a seguinte: em 1º do Champion. Temporada 2: eu em 11º, sem enfeite */
    congelar(M.banco, SEMANA, { Rookie: [[outros[0]!, 30], [outros[1]!, 20], [eu, 10]] });
    congelar(M.banco, SEGUINTE, { Champion: [[eu, 40]] });
    congelar(M.banco, "2026-11-30", { Mega: [...outros.slice(0, ENFEITE_ATE).map(c => [c, 50] as [string, number]), [eu, 5]] });
    M.relogio.t = congelaEm("2026-11-30") + 1;
    const d = await (await nav.pedir("/premios")).json() as any;
    expect(d.enfeites).toEqual([{ temporada: 1, de: "2026-11-02", ate: "2026-11-23", melhor: { semana: SEGUINTE, estagio: "Champion", posicao: 1 } }]);
    expect(d.temporada_atual).toBe(2);
  });

  it("o mural: os recordes por valor, o primeiro a chegar desempata, a linha de quem olha vem sempre", async () => {
    const cs = Array.from({ length: LINHAS_DO_MURAL + 2 }, () => conta(M.banco));
    cs.forEach((c, i) => gravarFronteira(M.banco, c, 1, { ...vazia(), torre: 20 - i }, "e", 100 + i));
    gravarFronteira(M.banco, eu, 1, { ...vazia(), torre: 1, fabrica: 3 }, "e", 1);
    /* empate na Fábrica: quem viu antes fica na frente */
    gravarFronteira(M.banco, cs[0]!, 1, { ...vazia(), fabrica: 3 }, "e", 50);
    const mu = await (await nav.pedir("/mural")).json() as any;
    expect(mu.total.torre).toBe(LINHAS_DO_MURAL + 3);
    expect(mu.recordes.torre).toHaveLength(LINHAS_DO_MURAL + 1);
    expect(mu.recordes.torre[0]).toMatchObject({ posicao: 1, valor: 20, voce: false });
    expect(mu.recordes.torre.at(-1)).toMatchObject({ posicao: LINHAS_DO_MURAL + 3, valor: 1, voce: true });
    expect(mu.recordes.fabrica.map((l: any) => l.voce)).toEqual([true, false]);
    const d = await (await nav.pedir("/premios")).json() as any;
    expect(d.recordes).toMatchObject({ torre: { valor: 1 }, fabrica: { valor: 3 }, salao: null });
  });

  it("apagar a conta leva os recordes e as lutas do Salão vistas; o baixar os dados os traz", async () => {
    gravarFronteira(M.banco, eu, 1, { ...vazia(), torre: 2, salao: [{ s: 9, tick: 1, venceu: true }] }, "e", 1);
    const dados = await (await nav.pedir("/conta/dados")).json() as any;
    expect(dados.premios.recordes).toHaveLength(1);
    expect(dados.premios.salao_vistas).toEqual([{ pet: 1, semente: 9, venceu: 1 }]);
    expect((await nav.json("DELETE", "/conta", { confirmar: "apagar" }, csrf)).status).toBe(200);
    expect(contar(M.banco, "recordes")).toBe(0);
    expect(contar(M.banco, "salao_vistas")).toBe(0);
  });
});
