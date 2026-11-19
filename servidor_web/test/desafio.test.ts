/* O desafio do dia (MMO6): a semente do dia igual para todos, a tentativa única, as sementes das lutas por conta depois da escolha, o
   envio conferido pelo replay, a virada do dia pelo relógio de mentira, o fechamento com o selo e o segredo publicado, e apagar a conta.
   O jogador de mentira joga a Fábrica do dia pelo motor (TentativaFabrica.doDia), como o jogo vai jogar. */
import { createHmac } from "node:crypto";
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, it } from "vitest";
import { MEDALHAS, Motor, TentativaFabrica, VERSAO_FABRICA_ATUAL } from "../../web/app/motor/index.ts";
import { refazerDesafio, TOP_DO_DIA, type RegistroDesafio } from "../../web/app/src/ranking/desafio.ts";
import { Tamer, VERSAO_TAMER } from "../../web/app/src/tamer.ts";
import { MIGRACOES, VERSAO_BANCO, type Banco } from "../src/conta/banco.ts";
import {
  comSelo, congelaDia, diaValido, fecharDias, fimDoDia, LUTAS_MAX_DO_DIA, ROTULO_SEMENTE_DIA, sementeDaLutaDoDia, sementeDoDia, tabelaDoDia,
} from "../src/desafio/desafio.ts";
import { FOLGA_DO_FECHAMENTO_MS } from "../src/envio/semanas.ts";
import { contar, criarConta, montar, Navegador, type Montado } from "./navegador.ts";

const DIA = "2026-11-16", SEGUINTE = "2026-11-17", SEGREDO_TESTE = "1a".repeat(32);
let M: Montado, nav: Navegador, csrf: string;

const idDaConta = (n: Navegador) => n.pedir("/conta").then(r => r.json()).then((d: any) => d.conta.id as string);
/** abre o nível da conta direto no banco: um envio aceito com o marco 7 (o do beta; a trava é a mesma da luta ranqueada) */
function abrirNivel(banco: Banco, contaId: string): void {
  banco.prepare(`INSERT INTO envios (id, conta_id, recebido_em, pet, versao_pet, eventos, hash_log, versao_tamer, hash_tamer, resultado, motivo, detalhe,
    marco10, pontos, lutas_ranqueadas, ms_conferencia, sementes, marcos_tamer) VALUES (?, ?, 0, 1, 21, 0, 'h', 1, 'h', 'aceito', NULL, NULL, 'sem_marco', 0, 0, 0, 0, '[7]')`)
    .run(`aberto-${contaId}`, contaId);
}
/** uma conta nova no mesmo app, com o nível aberto */
async function jogador(usuario: string): Promise<{ nav: Navegador; csrf: string; id: string }> {
  const n = new Navegador(M.app), c = await criarConta(n, usuario), id = await idDaConta(n);
  abrirNivel(M.banco, id);
  return { nav: n, csrf: c, id };
}
/** o teste sabe o segredo: o alugado que vence a primeira luta desta conta (null: os 3 perdem). Só para escolher o caso, antes de pedir */
function escolhaQueVence(contaId: string): number | null {
  const segredo = Buffer.from(SEGREDO_TESTE, "hex"), dia = sementeDoDia(segredo), s0 = sementeDaLutaDoDia(segredo, contaId, 0);
  for (let e = 0; e < 3; e++) if (TentativaFabrica.doDia(e, dia, [s0]).lutar(s0).venceu) return e;
  return null;
}
/** uma conta nova em que algum alugado vence a primeira luta */
async function jogadorQueVence(): Promise<{ nav: Navegador; csrf: string; id: string; escolha: number }> {
  for (const u of ["j0", "j1", "j2", "j3", "j4", "j5", "j6", "j7", "j8", "j9"]) {
    const j = await jogador(u), e = escolhaQueVence(j.id);
    if (e !== null) return { ...j, escolha: e };
  }
  throw new Error("nenhuma das 10 contas vence a primeira luta: o teste não cobre o caso");
}
const comecar = (n = nav, c = csrf, v = VERSAO_FABRICA_ATUAL) => n.json("POST", "/desafio/tentativa", { v }, c);
const pedirLuta = (k: number, escolha: number, trocas: number[], n = nav, c = csrf, dia = DIA) => n.json("POST", "/desafio/lutas", { dia, k, escolha, trocas }, c);
const enviar = (registro: unknown, n = nav, c = csrf, dia = DIA) => n.json("POST", "/desafio/envios", { dia, registro }, c);

/** joga a tentativa inteira pelo servidor: pede cada semente com a escolha e as trocas, luta pelo motor e troca a cada vitória k com
    k % ritmo === 0 (0: nunca). Para na derrota ou em `max` lutas. Devolve o registro e a tentativa do jogo */
async function jogar(escolha: number, ritmo: number, max = 30, n = nav, c = csrf): Promise<{ registro: RegistroDesafio; t: TentativaFabrica; sementeDia: number }> {
  const r0 = await comecar(n, c);
  expect(r0.status).toBe(201);
  const { semente_dia } = await r0.json() as { semente_dia: number };
  const t = TentativaFabrica.doDia(escolha, semente_dia), trocas: number[] = [], lutas: number[] = [];
  for (let k = 0; k < max && !t.acabou; k++) {
    const r = await pedirLuta(k, escolha, [...trocas], n, c);
    expect(r.status).toBe(201);
    const { semente } = await r.json() as { semente: number };
    t.receberSemente(k, semente); lutas.push(semente);
    const l = t.lutar(semente);
    if (l.venceu && ritmo > 0 && k % ritmo === 0) { t.trocar(); trocas.push(k); }
  }
  return { registro: { v: VERSAO_FABRICA_ATUAL, escolha, lutas, trocas }, t, sementeDia: semente_dia };
}

beforeEach(async () => {
  M = montar(undefined, { DIGILAB_MARCO_RANQUEADA: "7", DIGILAB_CONVIDADOS: ["ana", "caio", "b", "c", "d", "e", ...Array.from({ length: 10 }, (_, i) => "j" + i)].map(u => "falso:" + u).join(" ") });
  nav = new Navegador(M.app);
  csrf = await criarConta(nav);
  abrirNivel(M.banco, await idDaConta(nav));
  /* o segredo do dia é fixo nos testes (no servidor, 32 bytes aleatórios): os resultados das lutas não mudam de uma rodada para outra */
  M.banco.prepare("INSERT INTO segredos_dia (dia, segredo, criado_em) VALUES (?, ?, 0)").run(DIA, SEGREDO_TESTE);
});

describe("o banco e o dia", () => {
  it("a migração 6 é a do desafio, e as tabelas nascem vazias", () => {
    expect(VERSAO_BANCO).toBe(6);
    expect(MIGRACOES[5]).toContain("segredos_dia");
    for (const t of ["desafios", "desafio_lutas", "desafio_envios", "tabelas_dia"]) expect(contar(M.banco, t)).toBe(0);
  });
  it("o dia de Brasília vai das 03:00 UTC às 03:00 UTC, e congela uma hora depois", () => {
    expect(new Date(fimDoDia(DIA)).toISOString()).toBe("2026-11-17T03:00:00.000Z");
    expect(congelaDia(DIA) - fimDoDia(DIA)).toBe(FOLGA_DO_FECHAMENTO_MS);
    expect(diaValido("2026-11-16")).toBe(true);
    expect(diaValido("2026-02-30")).toBe(false);
    expect(diaValido("16/11/2026")).toBe(false);
  });
});

describe("a tentativa e a semente do dia", () => {
  it("sem sessão leva 401, sem CSRF 403, e o nível fechado 403 com o marco", async () => {
    const outro = new Navegador(M.app);
    expect((await outro.json("POST", "/desafio/tentativa", { v: VERSAO_FABRICA_ATUAL })).status).toBe(401);
    expect((await outro.pedir("/desafio")).status).toBe(401);
    expect((await nav.json("POST", "/desafio/tentativa", { v: VERSAO_FABRICA_ATUAL })).status).toBe(403);
    const fechado = new Navegador(M.app), c = await criarConta(fechado, "caio");
    const r = await comecar(fechado, c);
    expect(r.status).toBe(403);
    expect(await r.json()).toMatchObject({ motivo: "nivel_insuficiente", marco: 7 });
    expect(contar(M.banco, "desafios")).toBe(0);
  });
  it("o pedido malformado leva 400 e a versão de outra Fábrica 422", async () => {
    expect((await nav.json("POST", "/desafio/tentativa", { v: VERSAO_FABRICA_ATUAL, pontos: 9 }, csrf)).status).toBe(400);
    expect((await nav.json("POST", "/desafio/tentativa", "{", csrf)).status).toBe(400);
    const r = await comecar(nav, csrf, 13);
    expect(r.status).toBe(422);
    expect((await r.json() as any).motivo).toBe("versao_fabrica_desconhecida");
    expect(contar(M.banco, "desafios")).toBe(0);
  });
  it("todos recebem a mesma semente do dia, que é o HMAC do segredo do dia", async () => {
    const r1 = await comecar(), b = await jogador("caio"), r2 = await comecar(b.nav, b.csrf);
    expect(r1.status).toBe(201); expect(r2.status).toBe(201);
    const d1 = await r1.json() as any, d2 = await r2.json() as any;
    expect(d1.dia).toBe(DIA); expect(d2.dia).toBe(DIA);
    expect(d1.semente_dia).toBe(d2.semente_dia);
    const segredo = (M.banco.prepare("SELECT segredo FROM segredos_dia WHERE dia = ?").get(DIA) as { segredo: string }).segredo;
    expect(d1.semente_dia).toBe(createHmac("sha256", Buffer.from(segredo, "hex")).update(ROTULO_SEMENTE_DIA).digest().readUInt32BE(0));
    expect(contar(M.banco, "segredos_dia")).toBe(1);
    /* os mesmos 3 alugados e os mesmos rivais para os dois */
    const a = TentativaFabrica.doDia(0, d1.semente_dia), c = TentativaFabrica.doDia(2, d2.semente_dia);
    expect(a.alugueis).toEqual(c.alugueis);
    expect(a.proximoRival()).toEqual(c.proximoRival());
  });
  it("a segunda tentativa no mesmo dia é recusada (pedir a semente já conta), e o GET devolve a mesma semente", async () => {
    const d = await (await comecar()).json() as any;
    M.relogio.t += 5 * 3600_000;
    const r = await comecar();
    expect(r.status).toBe(409);
    expect(await r.json()).toMatchObject({ motivo: "tentativa_usada", reabre_em: "2026-11-17T03:00:00.000Z" });
    expect(contar(M.banco, "desafios")).toBe(1);
    const g = await (await nav.pedir("/desafio")).json() as any;
    expect(g.dia).toBe(DIA);
    expect(g.tentativa).toMatchObject({ dia: DIA, semente_dia: d.semente_dia, escolha: null, lutas: [], conferido: null });
  });
  it("a virada do dia pelo relógio do servidor: às 02:59 UTC ainda é o dia; às 03:00, um dia novo, outra tentativa e outro segredo", async () => {
    const d1 = await (await comecar()).json() as any;
    M.relogio.t = Date.UTC(2026, 10, 17, 2, 59, 59);
    expect((await comecar()).status).toBe(409);
    M.relogio.t = Date.UTC(2026, 10, 17, 3, 0, 0);
    const r = await comecar();
    expect(r.status).toBe(201);
    const d2 = await r.json() as any;
    expect(d2.dia).toBe(SEGUINTE);
    expect(d2.semente_dia).not.toBe(d1.semente_dia);
    expect(contar(M.banco, "segredos_dia")).toBe(2);
    expect(contar(M.banco, "desafios")).toBe(2);
  });
});

describe("as sementes das lutas", () => {
  it("são da conta: a mesma luta tem outra semente em outra conta, e só sai depois da escolha", async () => {
    await comecar();
    const b = await jogador("caio");
    await comecar(b.nav, b.csrf);
    const s1 = (await (await pedirLuta(0, 1, [])).json() as any).semente, s2 = (await (await pedirLuta(0, 1, [], b.nav, b.csrf)).json() as any).semente;
    expect(s1).not.toBe(s2);
    const segredo = Buffer.from((M.banco.prepare("SELECT segredo FROM segredos_dia WHERE dia = ?").get(DIA) as { segredo: string }).segredo, "hex");
    expect(s1).toBe(sementeDaLutaDoDia(segredo, await idDaConta(nav), 0));
    expect((M.banco.prepare("SELECT escolha FROM desafios WHERE conta_id = ?").get(await idDaConta(nav)) as { escolha: number }).escolha).toBe(1);
  });
  it("sem tentativa leva 404; fora de ordem, outra escolha ou outras trocas levam 409", async () => {
    expect((await (await pedirLuta(0, 0, [])).json() as any).motivo).toBe("sem_tentativa");
    await comecar();
    expect((await (await pedirLuta(1, 0, [])).json() as any).motivo).toBe("fora_de_ordem");
    expect((await pedirLuta(0, 0, [])).status).toBe(201);
    expect((await (await pedirLuta(1, 2, [])).json() as any).motivo).toBe("escolha_diferente");
    expect((await pedirLuta(1, 0, [0])).status).toBe(201);
    /* a troca depois da luta 0 já foi prometida: não sai, e a de antes não entra depois */
    const r = await pedirLuta(2, 0, []);
    expect(r.status).toBe(409);
    expect((await r.json() as any).motivo).toBe("trocas_diferentes");
    expect((await pedirLuta(2, 0, [0, 1])).status).toBe(201);
    /* a troca depois de uma luta que ainda não houve é malformada */
    expect((await pedirLuta(3, 0, [0, 1, 3])).status).toBe(400);
    expect((await pedirLuta(3, 0, [1, 0])).status).toBe(400);
  });
  it("o teto de lutas por tentativa", async () => {
    await comecar();
    const id = await idDaConta(nav), ins = M.banco.prepare("INSERT INTO desafio_lutas (conta_id, dia, k, semente, hora, escolha, trocas) VALUES (?, ?, ?, 1, 0, 0, '[]')");
    for (let k = 0; k < LUTAS_MAX_DO_DIA; k++) ins.run(id, DIA, k);
    M.banco.prepare("UPDATE desafios SET escolha = 0").run();
    expect((await (await pedirLuta(LUTAS_MAX_DO_DIA, 0, [])).json() as any).motivo).toBe("lutas_demais");
  });
});

describe("o envio", () => {
  it("o registro jogado é aceito, e o resultado é o do motor", async () => {
    const { registro, t, sementeDia } = await jogar(2, 1);
    const r = await enviar(registro);
    expect(r.status).toBe(200);
    const d = await r.json() as any;
    expect(d.resultado).toBe("aceito");
    const conta = refazerDesafio(sementeDia, registro).resultado;
    expect(conta.vitorias).toBe(t.vitorias);
    expect(d.tentativa.conferido).toMatchObject({ vitorias: t.vitorias, series: t.series, lutas: t.lutas.length, acabou: t.acabou, vida_ultima_vitoria: conta.vidaUltimaVitoria });
    /* o mesmo registro de novo devolve a conferência guardada */
    const de_novo = await enviar(registro);
    expect((await de_novo.json() as any).id).toBe(d.id);
    expect(contar(M.banco, "desafio_envios")).toBe(1);
  });
  it("o envio adulterado é recusado com o motivo, e guardado", async () => {
    const { registro } = await jogar(1, 0);
    const casos: [unknown, string][] = [
      [{ ...registro, escolha: (registro.escolha + 1) % 3 }, "escolha_nao_confere"],
      [{ ...registro, lutas: [(registro.lutas[0]! ^ 1) >>> 0, ...registro.lutas.slice(1)] }, "semente_nao_confere"],
      [{ ...registro, lutas: [...registro.lutas, 7] }, "semente_nao_confere"],
      [{ ...registro, trocas: [0] }, registro.lutas.length > 1 ? "trocas_nao_conferem" : "nao_reproduz"],
      [{ ...registro, v: 13 }, "versao_fabrica_diferente"],
    ];
    for (const [reg, motivo] of casos) {
      const r = await enviar(reg);
      expect(r.status, motivo).toBe(422);
      expect((await r.json() as any).motivo).toBe(motivo);
    }
    expect((M.banco.prepare("SELECT count(*) AS n FROM desafio_envios WHERE resultado = 'recusado'").get() as { n: number }).n).toBe(casos.length);
    expect((M.banco.prepare("SELECT vitorias FROM desafios").get() as { vitorias: number | null }).vitorias).toBeNull();
    /* a pontuação do cliente e o campo a mais são malformados */
    expect((await enviar({ ...registro, vitorias: 99 })).status).toBe(400);
    expect((await nav.json("POST", "/desafio/envios", { dia: DIA, registro, pontos: 1 }, csrf)).status).toBe(400);
  });
  it("a luta depois da derrota não reproduz, e o registro que para antes da última semente sem derrota é recusado", async () => {
    const { registro, t } = await jogar(0, 0);
    expect(t.acabou).toBe(true);
    /* pede mais uma semente depois da derrota e a põe no registro: o motor recusa */
    const s = (await (await pedirLuta(registro.lutas.length, 0, [])).json() as any).semente;
    expect((await (await enviar({ ...registro, lutas: [...registro.lutas, s] })).json() as any).motivo).toBe("nao_reproduz");
    /* o registro até a derrota ainda vale: a semente a mais fica sem uso */
    expect((await enviar(registro)).status).toBe(200);
    /* numa outra conta: vence a primeira, pede a segunda e envia só a primeira */
    const b = await jogadorQueVence(), { semente_dia } = await (await comecar(b.nav, b.csrf)).json() as any;
    const tt = TentativaFabrica.doDia(b.escolha, semente_dia), s0 = (await (await pedirLuta(0, b.escolha, [], b.nav, b.csrf)).json() as any).semente;
    tt.receberSemente(0, s0);
    expect(tt.lutar(s0).venceu).toBe(true);
    await pedirLuta(1, b.escolha, [], b.nav, b.csrf);
    const r = await enviar({ v: VERSAO_FABRICA_ATUAL, escolha: b.escolha, lutas: [s0], trocas: [] }, b.nav, b.csrf);
    expect((await r.json() as any).motivo).toBe("lutas_faltando");
  });
  it("o envio parcial vale, e o seguinte com mais lutas o substitui", async () => {
    const b = await jogadorQueVence(), e = b.escolha;
    const { semente_dia } = await (await comecar(b.nav, b.csrf)).json() as any;
    const t = TentativaFabrica.doDia(e, semente_dia), lutas: number[] = [];
    const s0 = (await (await pedirLuta(0, e, [], b.nav, b.csrf)).json() as any).semente;
    t.receberSemente(0, s0); lutas.push(s0);
    expect(t.lutar(s0).venceu).toBe(true);
    const r1 = await (await enviar({ v: VERSAO_FABRICA_ATUAL, escolha: e, lutas: [...lutas], trocas: [] }, b.nav, b.csrf)).json() as any;
    expect(r1.resultado).toBe("aceito");
    expect(r1.tentativa.conferido).toMatchObject({ lutas: 1, vitorias: 1, acabou: false });
    const s1 = (await (await pedirLuta(1, e, [0], b.nav, b.csrf)).json() as any).semente;
    t.trocar(); t.receberSemente(1, s1); lutas.push(s1); t.lutar(s1);
    const r2 = await (await enviar({ v: VERSAO_FABRICA_ATUAL, escolha: e, lutas: [...lutas], trocas: [0] }, b.nav, b.csrf)).json() as any;
    expect(r2.tentativa.conferido).toMatchObject({ lutas: 2, vitorias: t.vitorias });
    /* a troca prometida antes da segunda semente não sai do registro */
    expect((await (await enviar({ v: VERSAO_FABRICA_ATUAL, escolha: e, lutas: [...lutas], trocas: [] }, b.nav, b.csrf)).json() as any).motivo).toBe("trocas_nao_conferem");
    /* o mais curto de novo não volta o resultado */
    expect((await enviar({ v: VERSAO_FABRICA_ATUAL, escolha: e, lutas: [s0], trocas: [] }, b.nav, b.csrf)).status).toBe(200);
    expect((M.banco.prepare("SELECT lutas FROM desafios WHERE conta_id = ?").get(b.id) as { lutas: number }).lutas).toBe(2);
  });
});

describe("a tabela, o fechamento, o selo e o segredo", () => {
  /** põe uma tentativa já conferida direto no banco (para a tabela, sem jogar uma por linha) */
  function semear(contaId: string, vitorias: number, vida: number, terminou: number, dia = DIA): void {
    M.banco.prepare(`INSERT INTO desafios (conta_id, dia, comecou_em, versao, escolha, vitorias, series, lutas, acabou, vida_ultima, terminou_em, envio_id)
      VALUES (?, ?, 0, ?, 0, ?, 0, ?, 1, ?, ?, 'e')`).run(contaId, dia, VERSAO_FABRICA_ATUAL, vitorias, vitorias + 1, vida, terminou);
  }
  it("o desempate: mais vitórias, mais vida no fim da última vitória, quem terminou antes", async () => {
    const ids = [];
    for (const u of ["b", "c", "d", "e"]) ids.push((await jogador(u)).id);
    semear(ids[0]!, 3, 10, 5); semear(ids[1]!, 3, 20, 9); semear(ids[2]!, 3, 20, 7); semear(ids[3]!, 5, 1, 99);
    expect(tabelaDoDia(M.banco, DIA).map(l => l.contaId)).toEqual([ids[3], ids[2], ids[1], ids[0]]);
  });
  it("o selo vai aos 10 primeiros com ao menos uma vitória", () => {
    const linha = (v: number) => ({ contaId: "", apelido: "", vitorias: v, vidaUltimaVitoria: 0, terminouEm: 0 });
    expect(TOP_DO_DIA).toBe(10);
    expect(comSelo(Array.from({ length: 12 }, () => linha(1))).filter(Boolean)).toHaveLength(10);
    expect(comSelo([linha(2), linha(1), linha(0)])).toEqual([true, true, false]);
  });
  it("o dia congela uma hora depois do fim: a tabela fica, o selo sai, o segredo é publicado, e depois nada entra", async () => {
    const { registro } = await jogar(2, 1);
    expect((await enviar(registro)).status).toBe(200);
    const b = await jogador("caio");
    const outro = await jogar(1, 0, 30, b.nav, b.csrf);
    expect((await enviar(outro.registro, b.nav, b.csrf)).status).toBe(200);
    expect((await nav.pedir(`/desafio/${DIA}/segredo`)).status).toBe(404);
    const aberta = await (await nav.pedir(`/desafio/${DIA}/tabela`)).json() as any;
    expect(aberta).toMatchObject({ estado: "aberto", total: 2 });

    /* depois do fim, antes do congelamento: o envio ainda entra */
    M.relogio.t = fimDoDia(DIA) + 10 * 60_000;
    expect((await enviar(registro)).status).toBe(200);
    expect(fecharDias(M.banco, M.relogio.t)).toEqual([]);
    M.relogio.t = congelaDia(DIA);
    const g = await (await nav.pedir("/desafio")).json() as any;
    expect(g.dia).toBe(SEGUINTE);
    expect(g.fechados.map((x: any) => x.dia)).toEqual([DIA]);
    const fechada = await (await nav.pedir(`/desafio/${DIA}/tabela`)).json() as any;
    expect(fechada.estado).toBe("fechado");
    expect(fechada.linhas.map((l: any) => [l.posicao, l.voce])).toEqual(aberta.linhas.map((l: any) => [l.posicao, l.voce]));
    expect(fechada.linhas.map((l: any) => l.selo)).toEqual(fechada.linhas.map((l: any) => l.vitorias > 0));
    expect(contar(M.banco, "tabelas_dia")).toBe(2);
    const sel = await (await nav.pedir("/desafio/selos")).json() as any;
    expect(sel.total).toBe(fechada.linhas.find((l: any) => l.voce).selo ? 1 : 0);
    /* o segredo publicado refaz a semente do dia de todos */
    const seg = await (await new Navegador(M.app).pedir(`/desafio/${DIA}/segredo`)).json() as any;
    expect(sementeDoDia(Buffer.from(seg.segredo, "hex"))).toBe(outro.sementeDia);
    /* congelado: nem semente, nem envio */
    expect((await (await enviar(registro)).json() as any).motivo).toBe("dia_fechado");
    expect((await (await pedirLuta(registro.lutas.length, 0, registro.trocas)).json() as any).motivo).toBe("dia_fechado");
  });
  it("o segredo publicado é o que deu a semente do dia e as das lutas", async () => {
    const d = await (await comecar()).json() as any;
    const s0 = (await (await pedirLuta(0, 0, [])).json() as any).semente;
    M.relogio.t = congelaDia(DIA);
    const seg = await (await new Navegador(M.app).pedir(`/desafio/${DIA}/segredo`)).json() as any;
    const segredo = Buffer.from(seg.segredo, "hex");
    expect(sementeDoDia(segredo)).toBe(d.semente_dia);
    expect(sementeDaLutaDoDia(segredo, await idDaConta(nav), 0)).toBe(s0);
    expect((await nav.pedir(`/desafio/${SEGUINTE}/segredo`)).status).toBe(404);
    expect((await nav.pedir("/desafio/ontem/segredo")).status).toBe(400);
  });
  it("a tabela pede a sessão, e traz a linha de quem pede", async () => {
    expect((await new Navegador(M.app).pedir(`/desafio/${DIA}/tabela`)).status).toBe(401);
    expect((await nav.pedir("/desafio/2026-13-01/tabela")).status).toBe(400);
  });
});

describe("apagar a conta", () => {
  it("leva a tentativa, as sementes das lutas, os envios e a linha da tabela; o segredo do dia fica (é do servidor)", async () => {
    const { registro } = await jogar(2, 1);
    await enviar(registro);
    await enviar({ ...registro, escolha: (registro.escolha + 1) % 3 });
    const b = await jogador("caio");
    const outro = await jogar(2, 0, 30, b.nav, b.csrf);
    await enviar(outro.registro, b.nav, b.csrf);
    M.relogio.t = congelaDia(DIA);
    fecharDias(M.banco, M.relogio.t);
    const dados = await (await nav.pedir("/conta/dados")).json() as any;
    expect(dados.desafio.tentativas).toHaveLength(1);
    expect(dados.desafio.envios).toHaveLength(2);
    expect(dados.desafio.tabelas).toHaveLength(1);
    const id = await idDaConta(nav);
    const r = await nav.json("DELETE", "/conta", { confirmar: "apagar" }, csrf);
    expect(r.status).toBe(200);
    for (const t of ["desafios", "desafio_lutas", "desafio_envios", "tabelas_dia"])
      expect((M.banco.prepare(`SELECT count(*) AS n FROM ${t} WHERE conta_id = ?`).get(id) as { n: number }).n, t).toBe(0);
    /* a outra conta fica, com a posição gravada */
    expect(contar(M.banco, "desafios")).toBe(1);
    expect(contar(M.banco, "tabelas_dia")).toBe(1);
    expect(contar(M.banco, "segredos_dia")).toBe(1);
  });
});

describe("o nível aberto pelo envio de verdade (a trava da luta ranqueada)", () => {
  it("com um envio aceito do marco 7, a tentativa começa", async () => {
    type Evento = [number, string, ...unknown[]];
    const VIDA: { semente: number; log: Evento[]; versao: number } = JSON.parse(readFileSync(new URL("./gabaritos/vida_101.json", import.meta.url), "utf-8"));
    const n = new Navegador(M.app), c = await criarConta(n, "caio");
    expect((await comecar(n, c)).status).toBe(403);
    const m = Motor.reproduzir(VIDA.semente, VIDA.log.slice(0, 50) as never, VIDA.versao), t = new Tamer();
    MEDALHAS.slice(0, 3).forEach((x, i) => t.ganhar(x.id, m, Date.UTC(2026, 10, 15) + i));
    const e = await n.json("POST", "/envios", { pet: { semente: VIDA.semente, log: VIDA.log.slice(0, 50), versao: VIDA.versao },
      tamer: { versao: VERSAO_TAMER, log: JSON.parse(JSON.stringify(t.log)) } }, c);
    expect(e.status).toBe(201);
    expect((await comecar(n, c)).status).toBe(201);
  });
});
