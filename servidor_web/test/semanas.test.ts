/* O ranking da semana (MMO5): o que a conferência acha de cada semente fica guardado; as tabelas por estágio com o desempate; o
   fechamento da semana (a pendente vira não enviada, a tabela congela, o segredo sai); e as rotas. A vida é a da MMO3
   (test/gabaritos/vida_101.json), como nos testes da luta ranqueada. */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, it } from "vitest";
import { DIGIMON_DA_FORMA, MEDALHAS, Motor } from "../../web/app/motor/index.ts";
import { PONTOS_FAIXA, pontuar, type LutaRanqueada } from "../../web/app/src/ranking/pontos.ts";
import { Tamer, VERSAO_TAMER } from "../../web/app/src/tamer.ts";
import { MIGRACOES, VERSAO_BANCO, type Banco } from "../src/conta/banco.ts";
import { congelaEm, ESTAGIOS, fecharSemanas, fimDaSemanaDe, FOLGA_DO_FECHAMENTO_MS, LINHAS_DA_TABELA, semanaValida, tabelasDaSemana } from "../src/envio/semanas.ts";
import { sementeDe } from "../src/envio/sementes.ts";
import { contar, criarConta, montar, Navegador, type Montado } from "./navegador.ts";

type Evento = [number, string, ...unknown[]];
interface Save { semente: number; log: Evento[]; versao: number }
const VIDA: Save = JSON.parse(readFileSync(new URL("./gabaritos/vida_101.json", import.meta.url), "utf-8"));
const sha = (x: unknown) => createHash("sha256").update(JSON.stringify(x)).digest("hex");
const K = VIDA.log.findIndex(e => e[1] === "l" && PONTOS_FAIXA[DIGIMON_DA_FORMA[(e[2] as { r: string }).r]?.[1] ?? ""] !== undefined);
const LUTA = VIDA.log[K] as [number, "l", { r: string; s: number; m?: string }];
const prefixo = (n: number): Evento[] => JSON.parse(JSON.stringify(VIDA.log.slice(0, n)));
const comLuta = (semente: number): Evento[] => [...prefixo(K), [LUTA[0], "l", { ...LUTA[2], s: semente }]];
function tamerCom(n: number): { versao: number; log: unknown[] } {
  const m = Motor.reproduzir(VIDA.semente, VIDA.log.slice(0, 50) as never, VIDA.versao), t = new Tamer();
  MEDALHAS.slice(0, n).forEach((x, i) => t.ganhar(x.id, m, Date.UTC(2026, 10, 15) + i));
  return { versao: VERSAO_TAMER, log: JSON.parse(JSON.stringify(t.log)) };
}
const pet = (log: Evento[]) => ({ semente: VIDA.semente, log, versao: VIDA.versao });
const pedido = () => ({ pet: { semente: VIDA.semente, versao: VIDA.versao }, indice: K, hash: sha(VIDA.log.slice(0, K)), rival: LUTA[2].r, mapa: LUTA[2].m ?? null });

const SEMANA = "2026-11-16", SEGUINTE = "2026-11-23";
let M: Montado, nav: Navegador, csrf: string;
const enviar = (log: Evento[]) => nav.json("POST", "/envios", { pet: pet(log), tamer: tamerCom(3) }, csrf);
const pedir = () => nav.json("POST", "/sementes", pedido(), csrf);
const tabelas = async (semana = SEMANA, n = nav) => (await n.pedir(`/semanas/${semana}/tabelas`)).json() as Promise<any>;
const idDaConta = (apelidoOuNav: Navegador) => apelidoOuNav.pedir("/conta").then(r => r.json()).then((d: any) => d.conta.id as string);

beforeEach(async () => {
  M = montar(undefined, { DIGILAB_MARCO_RANQUEADA: "7" });
  nav = new Navegador(M.app);
  csrf = await criarConta(nav);
});

/** põe uma semente já conferida direto no banco (para as contas da tabela, sem refazer uma vida por linha) */
let proximo = 100;
function semear(banco: Banco, contaId: string, x: { pet?: number; semana?: string; situacao: string | null; estagio?: string | null; rival?: string | null; hora?: number }): void {
  const numero = proximo++, semana = x.semana ?? SEMANA, hora = x.hora ?? Date.parse(semana + "T15:00:00Z") + numero;
  if ((banco.prepare("SELECT 1 FROM segredos_semana WHERE semana = ?").get(semana)) === undefined)
    banco.prepare("INSERT INTO segredos_semana (semana, segredo, criado_em) VALUES (?, ?, ?)").run(semana, "ab".repeat(32), hora);
  const estagio = x.estagio === undefined ? "Rookie" : x.estagio, rival = x.rival === undefined ? null : x.rival;
  banco.prepare(`INSERT INTO sementes (conta_id, numero, pet, versao_pet, indice, hash_ate, semente, hora, dia, semana, situacao, estagio, rival, faixa)
    VALUES (?, ?, ?, 21, ?, 'h', ?, ?, ?, ?, ?, ?, ?, ?)`).run(contaId, numero, x.pet ?? 1, numero, numero * 7, hora, semana, semana, x.situacao, estagio, rival,
    rival ? DIGIMON_DA_FORMA[rival]![1] : null);
}
const ROOKIE_A = "brasa_crianca_sereno", ROOKIE_B = "cirro_crianca_arisco", CHAMPION = "brasa_adolescente_brigao";

describe("o banco", () => {
  it("a migração 4 é a última, e as colunas novas nascem vazias", () => {
    expect(VERSAO_BANCO).toBe(5);
    expect(MIGRACOES[3]).toContain("tabelas_semana");
    expect(contar(M.banco, "tabelas_semana")).toBe(0);
  });
});

describe("a semana", () => {
  it("fecha na segunda seguinte, 00:00 de Brasília, e congela uma hora depois", () => {
    expect(new Date(fimDaSemanaDe(SEMANA)).toISOString()).toBe("2026-11-23T03:00:00.000Z");
    expect(congelaEm(SEMANA) - fimDaSemanaDe(SEMANA)).toBe(FOLGA_DO_FECHAMENTO_MS);
    expect(FOLGA_DO_FECHAMENTO_MS).toBe(3_600_000);
  });
  it("só a segunda-feira que existe é uma semana", () => {
    expect(semanaValida("2026-11-16")).toBe(true);
    expect(semanaValida("2026-11-17")).toBe(false);
    expect(semanaValida("2026-02-30")).toBe(false);
    expect(semanaValida("16/11/2026")).toBe(false);
  });
  it("os estágios com tabela são as faixas que valem ponto", () => {
    expect(ESTAGIOS).toEqual(["Rookie", "Champion", "Ultimate", "Mega"]);
  });
});

describe("pontuar (a regra da metade, a mesma da conferência)", () => {
  const luta = (situacao: LutaRanqueada["situacao"], rival: string | null, semana = SEMANA): LutaRanqueada =>
    ({ semente: 1, indice: 1, hora: 1, dia: semana, semana, situacao, rival, faixa: rival ? DIGIMON_DA_FORMA[rival]![1] : null, estagio: "Rookie", pontos: 99, vidaFinal: null });
  it("a vitória pela faixa, a metade para o mesmo rival na semana, 0 para o resto", () => {
    const l = [luta("vitoria", ROOKIE_A), luta("derrota", ROOKIE_A), luta("vitoria", ROOKIE_A), luta("vitoria", CHAMPION), luta("vitoria", ROOKIE_A, SEGUINTE), luta("pendente", null)];
    pontuar(l);
    expect(l.map(x => x.pontos)).toEqual([10, 0, 5, 20, 10, 0]);
  });
  it("a vitória sem faixa que vale ponto falha alto", () => {
    expect(() => pontuar([{ ...luta("vitoria", ROOKIE_A), faixa: null }])).toThrow("sem faixa");
  });
});

describe("as tabelas (a conta e o desempate)", () => {
  let ana: string, caio: string;
  beforeEach(async () => {
    ana = await idDaConta(nav);
    const outro = new Navegador(M.app);
    await criarConta(outro, "caio");
    caio = await idDaConta(outro);
  });
  const rookie = () => tabelasDaSemana(M.banco, SEMANA).get("Rookie")!;

  it("uma tabela por estágio; um jogador aparece em cada uma em que lutou", () => {
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
    semear(M.banco, ana, { situacao: "vitoria", rival: CHAMPION, estagio: "Champion" });
    const t = tabelasDaSemana(M.banco, SEMANA);
    expect([...t.keys()]).toEqual(["Rookie", "Champion", "Ultimate", "Mega"]);
    expect(t.get("Rookie")).toMatchObject([{ contaId: ana, pontos: 10, rivaisVencidos: 1, lutasUsadas: 1 }]);
    expect(t.get("Champion")).toMatchObject([{ contaId: ana, pontos: 20 }]);
    expect(t.get("Mega")).toEqual([]);
  });
  it("1) mais pontos", () => {
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
    semear(M.banco, caio, { situacao: "vitoria", rival: CHAMPION });
    expect(rookie().map(l => l.contaId)).toEqual([caio, ana]);
  });
  it("2) com os mesmos pontos, mais rivais diferentes vencidos", () => {
    /* ana: 10 + 5 do mesmo rival, e 5 mais abaixo? não: 15 de um rival só contra 15 de dois */
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A }); semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A }); semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });   // 10 + 5 + 2,5 + 1,25 + 0,625 = 19,375
    semear(M.banco, caio, { situacao: "vitoria", rival: ROOKIE_A }); semear(M.banco, caio, { situacao: "vitoria", rival: ROOKIE_B });   // 20
    expect(rookie().map(l => [l.contaId, l.pontos, l.rivaisVencidos])).toEqual([[caio, 20, 2], [ana, 19.375, 1]]);
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });   // + 0,3125
    semear(M.banco, ana, { pet: 2, situacao: "vitoria", rival: ROOKIE_A }); // outro pet: 10 cheios -> 29,6875
    expect(rookie()[0]).toMatchObject({ contaId: ana, rivaisVencidos: 1 });
  });
  it("2) e 3) no empate de pontos: os rivais, depois menos lutas usadas", () => {
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A }); semear(M.banco, ana, { situacao: "derrota", rival: ROOKIE_B });
    semear(M.banco, caio, { situacao: "vitoria", rival: ROOKIE_B });
    expect(rookie().map(l => [l.contaId, l.pontos, l.lutasUsadas])).toEqual([[caio, 10, 1], [ana, 10, 2]]);
  });
  it("4) no empate dos três, quem chegou antes aos pontos", () => {
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A, hora: Date.parse("2026-11-18T12:00:00Z") });
    semear(M.banco, caio, { situacao: "vitoria", rival: ROOKIE_B, hora: Date.parse("2026-11-17T12:00:00Z") });
    expect(rookie().map(l => l.contaId)).toEqual([caio, ana]);
  });
  it("a derrota, a não enviada e a pendente contam como luta usada, com 0; a acima do limite e a sem estágio não entram", () => {
    for (const situacao of ["derrota", "nao_enviada", "pendente", "fora_da_arena"]) semear(M.banco, ana, { situacao });
    semear(M.banco, ana, { situacao: "acima_do_limite", estagio: null });
    semear(M.banco, ana, { situacao: "pendente", estagio: null });
    semear(M.banco, ana, { situacao: null, estagio: null });   // ainda não conferida
    expect(rookie()).toMatchObject([{ contaId: ana, pontos: 0, rivaisVencidos: 0, lutasUsadas: 4, horaDosPontos: null }]);
  });
  it("a semana seguinte começa do zero, e o In-Training não tem tabela", () => {
    semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
    semear(M.banco, ana, { situacao: "derrota", estagio: "In-Training" });
    expect([...tabelasDaSemana(M.banco, SEGUINTE).values()].flat()).toEqual([]);
    expect([...tabelasDaSemana(M.banco, SEMANA).values()].flat()).toHaveLength(1);
  });

  describe("o fechamento", () => {
    it("antes da hora de congelar não fecha; depois, a pendente e a nunca conferida viram não enviada, a tabela congela e o segredo sai", () => {
      semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
      semear(M.banco, ana, { situacao: "pendente" });
      semear(M.banco, caio, { situacao: null, estagio: null });
      expect(fecharSemanas(M.banco, congelaEm(SEMANA) - 1)).toEqual([]);
      expect(contar(M.banco, "tabelas_semana")).toBe(0);
      expect(fecharSemanas(M.banco, congelaEm(SEMANA))).toEqual([SEMANA]);
      expect(M.banco.prepare("SELECT situacao FROM sementes ORDER BY numero").all().map((l: any) => l.situacao)).toEqual(["vitoria", "nao_enviada", "nao_enviada"]);
      expect(M.banco.prepare("SELECT estagio, posicao, conta_id, pontos, lutas_usadas FROM tabelas_semana").all())
        .toEqual([{ estagio: "Rookie", posicao: 1, conta_id: ana, pontos: 10, lutas_usadas: 2 }]);
      expect((M.banco.prepare("SELECT publicado_em FROM segredos_semana WHERE semana = ?").get(SEMANA) as any).publicado_em).toBe(congelaEm(SEMANA));
      /* de novo não fecha duas vezes */
      expect(fecharSemanas(M.banco, congelaEm(SEMANA) + 5)).toEqual([]);
      expect(contar(M.banco, "tabelas_semana")).toBe(1);
    });
    it("fecha as semanas atrasadas de uma vez, cada uma com a sua tabela", () => {
      semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
      semear(M.banco, caio, { semana: SEGUINTE, situacao: "vitoria", rival: ROOKIE_B });
      expect(fecharSemanas(M.banco, congelaEm(SEGUINTE))).toEqual([SEMANA, SEGUINTE]);
      expect(M.banco.prepare("SELECT semana, conta_id FROM tabelas_semana ORDER BY semana").all()).toEqual([{ semana: SEMANA, conta_id: ana }, { semana: SEGUINTE, conta_id: caio }]);
    });
    it("apagar a conta tira a linha dela da tabela congelada; a posição do outro fica", () => {
      semear(M.banco, ana, { situacao: "vitoria", rival: CHAMPION });
      semear(M.banco, caio, { situacao: "vitoria", rival: ROOKIE_A });
      fecharSemanas(M.banco, congelaEm(SEMANA));
      M.banco.prepare("DELETE FROM contas WHERE id = ?").run(ana);
      expect(M.banco.prepare("SELECT posicao, conta_id FROM tabelas_semana").all()).toEqual([{ posicao: 2, conta_id: caio }]);
    });
  });

  describe("GET /semanas/:semana/tabelas", () => {
    it("sem sessão, 401; a semana que não é segunda, 400", async () => {
      expect((await new Navegador(M.app).pedir(`/semanas/${SEMANA}/tabelas`)).status).toBe(401);
      expect((await nav.pedir("/semanas/2026-11-17/tabelas")).status).toBe(400);
    });
    it("a semana aberta: as linhas com a posição, o apelido e a marca de quem pede; nada do id da conta", async () => {
      semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
      semear(M.banco, caio, { situacao: "vitoria", rival: CHAMPION });
      const d = await tabelas();
      expect(d).toMatchObject({ semana: SEMANA, estado: "aberta", congela_em: "2026-11-23T04:00:00.000Z", total: { Rookie: 2, Champion: 0, Ultimate: 0, Mega: 0 } });
      expect(d.estagios.Rookie).toMatchObject([{ posicao: 1, pontos: 20, voce: false }, { posicao: 2, pontos: 10, rivais_vencidos: 1, lutas_usadas: 1, voce: true }]);
      expect(d.estagios.Rookie[1].apelido).toMatch(/^[A-Za-z]+#\d{4}$/);
      expect(JSON.stringify(d)).not.toContain(ana);
      expect(JSON.stringify(d)).not.toContain(caio);
    });
    it("a semana sem lutas devolve as quatro tabelas vazias", async () => {
      expect((await tabelas(SEGUINTE)).estagios).toEqual({ Rookie: [], Champion: [], Ultimate: [], Mega: [] });
    });
    it("depois da hora, a rota fecha a semana e devolve a tabela congelada", async () => {
      semear(M.banco, ana, { situacao: "vitoria", rival: ROOKIE_A });
      semear(M.banco, caio, { situacao: "pendente" });
      M.relogio.t = congelaEm(SEMANA) + 1;
      const d = await tabelas();
      expect(d.estado).toBe("fechada");
      expect(d.estagios.Rookie).toMatchObject([{ posicao: 1, pontos: 10, voce: true }, { posicao: 2, pontos: 0, lutas_usadas: 1, voce: false }]);
      /* uma semente conferida depois não muda a tabela congelada */
      semear(M.banco, caio, { situacao: "vitoria", rival: CHAMPION });
      expect((await tabelas()).estagios.Rookie[0]).toMatchObject({ posicao: 1, pontos: 10, voce: true });
    });
    it("a tabela longa leva as primeiras linhas e a de quem pede", async () => {
      semear(M.banco, ana, { situacao: "derrota" });
      for (let i = 0; i < LINHAS_DA_TABELA + 2; i++) {
        const id = `conta-${i}`;
        M.banco.prepare("INSERT INTO contas (id, apelido, criada_em, idade) VALUES (?, ?, 0, '18_ou_mais')").run(id, `Agumon#${1000 + i}`);
        semear(M.banco, id, { situacao: "vitoria", rival: ROOKIE_A });
      }
      const d = await tabelas();
      expect(d.total.Rookie).toBe(LINHAS_DA_TABELA + 3);
      expect(d.estagios.Rookie).toHaveLength(LINHAS_DA_TABELA + 1);
      expect(d.estagios.Rookie.at(-1)).toMatchObject({ posicao: LINHAS_DA_TABELA + 3, voce: true });
    });
  });
});

describe("GET /semanas e o segredo publicado", () => {
  it("diz a semana aberta, quando fecha e quando congela; sem sessão", async () => {
    const d = await (await new Navegador(M.app).pedir("/semanas")).json() as any;
    expect(d).toEqual({ atual: SEMANA, fecha_em: "2026-11-23T03:00:00.000Z", congela_em: "2026-11-23T04:00:00.000Z", fechadas: [] });
  });
  it("o segredo: 404 sem lutas na semana, 404 com a semana aberta, 200 depois de congelar, e refaz a semente entregue", async () => {
    const anonimo = new Navegador(M.app);
    expect(await (await anonimo.pedir(`/semanas/${SEMANA}/segredo`)).json()).toMatchObject({ motivo: "sem_segredo" });
    expect((await enviar(prefixo(K))).status).toBe(201);
    const s = await (await pedir()).json() as any;
    const aberta = await anonimo.pedir(`/semanas/${SEMANA}/segredo`);
    expect(aberta.status).toBe(404);
    expect(await aberta.json()).toMatchObject({ motivo: "semana_aberta", congela_em: "2026-11-23T04:00:00.000Z" });
    M.relogio.t = congelaEm(SEMANA);
    const r = await anonimo.pedir(`/semanas/${SEMANA}/segredo`);
    expect(r.status).toBe(200);
    const d = await r.json() as any;
    expect(d).toMatchObject({ semana: SEMANA, publicado_em: "2026-11-23T04:00:00.000Z" });
    expect(d.segredo).toMatch(/^[0-9a-f]{64}$/);
    expect(sementeDe(Buffer.from(d.segredo, "hex"), await idDaConta(nav), s.numero)).toBe(s.semente);
    expect((await (await anonimo.pedir("/semanas")).json() as any).fechadas).toEqual([{ semana: SEMANA, publicado_em: "2026-11-23T04:00:00.000Z" }]);
    expect((await anonimo.pedir("/semanas/2026-11-17/segredo")).status).toBe(400);
  });
});

describe("do pedido à tabela, pelo servidor inteiro", () => {
  beforeEach(async () => { expect((await enviar(prefixo(K))).status).toBe(201); });
  const daSemente = () => M.banco.prepare("SELECT situacao, estagio, rival, faixa, envio_id FROM sementes").all() as any[];

  it("a semente pedida e ainda não conferida não entra na tabela; o envio da luta a põe lá", async () => {
    const s = await (await pedir()).json() as any;
    expect(daSemente()).toEqual([{ situacao: null, estagio: null, rival: null, faixa: null, envio_id: null }]);
    expect((await tabelas()).total).toEqual({ Rookie: 0, Champion: 0, Ultimate: 0, Mega: 0 });
    const e = await enviar(comLuta(s.semente));
    expect(e.status).toBe(201);
    const d = await e.json() as any, luta = d.lutas[0];
    expect(["vitoria", "derrota"]).toContain(luta.situacao);
    expect(daSemente()).toEqual([{ situacao: luta.situacao, estagio: luta.estagio, rival: luta.rival, faixa: luta.faixa, envio_id: d.id }]);
    const t = await tabelas();
    expect(t.estagios[luta.estagio]).toMatchObject([{ posicao: 1, pontos: luta.pontos, lutas_usadas: 1, rivais_vencidos: luta.situacao === "vitoria" ? 1 : 0, voce: true }]);
    expect((await (await nav.pedir("/sementes")).json() as any)[0]).toMatchObject({ situacao: luta.situacao, estagio: luta.estagio });
  });
  it("a pendente (o envio sem a luta) entra como luta usada e ainda muda; fechada a semana, vira não enviada", async () => {
    await pedir();
    /* o mesmo registro de antes, agora com uma semente nova: confere de novo, e a semente fica pendente */
    expect((await enviar(prefixo(K))).status).toBe(201);
    expect(daSemente()[0]).toMatchObject({ situacao: "pendente" });
    const estagio = daSemente()[0].estagio as string;
    expect((await tabelas()).estagios[estagio]).toMatchObject([{ pontos: 0, lutas_usadas: 1 }]);
    M.relogio.t = congelaEm(SEMANA);
    expect((await tabelas()).estado).toBe("fechada");
    expect(daSemente()[0]).toMatchObject({ situacao: "nao_enviada" });
  });
  it("a primeira conferência vale: o envio seguinte com outra luta no mesmo lugar não muda a semente", async () => {
    const s = await (await pedir()).json() as any;
    const primeiro = await (await enviar(comLuta(s.semente))).json() as any;
    const antes = daSemente()[0];
    /* o registro reescrito: outro evento no lugar da luta (a luta de treino da vida, com a semente dela) */
    const reescrito = await enviar(prefixo(K + 1));
    expect(reescrito.status).toBe(201);
    expect((await reescrito.json() as any).lutas[0].situacao).toBe("nao_enviada");
    expect(daSemente()[0]).toEqual(antes);
    expect(antes.envio_id).toBe(primeiro.id);
  });
  it("a luta que chega depois de a semana congelar não entra: fica não enviada", async () => {
    const s = await (await pedir()).json() as any;
    M.relogio.t = congelaEm(SEMANA) + 60_000;
    const e = await enviar(comLuta(s.semente));
    expect(e.status).toBe(201);
    expect(daSemente()[0]).toMatchObject({ situacao: "nao_enviada", envio_id: null });
    const t = await tabelas();
    expect(t.estado).toBe("fechada");
    expect(Object.values(t.total)).toEqual([0, 0, 0, 0]);
  });
  it("a luta pedida no último minuto e enviada dentro da folga ainda entra", async () => {
    M.relogio.t = fimDaSemanaDe(SEMANA) - 60_000;
    const s = await (await pedir()).json() as any;
    expect(s.semana).toBe(SEMANA);
    M.relogio.t = fimDaSemanaDe(SEMANA) + 30 * 60_000;
    const d = await (await enviar(comLuta(s.semente))).json() as any;
    expect(daSemente()[0]).toMatchObject({ situacao: d.lutas[0].situacao, envio_id: d.id });
  });
  it("o baixar os meus dados leva o que o servidor achou de cada semente", async () => {
    const s = await (await pedir()).json() as any;
    const d = await (await enviar(comLuta(s.semente))).json() as any;
    const dados = await (await nav.pedir("/conta/dados")).json() as any;
    expect(dados.sementes[0]).toMatchObject({ numero: s.numero, situacao: d.lutas[0].situacao, estagio: d.lutas[0].estagio, rival: d.lutas[0].rival });
  });
});
