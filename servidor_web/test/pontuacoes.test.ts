/* As duas pontuações e o reset (MMO8): a migração 8; a conferência (os pontos do Digimon, os feitos do Tamer vistos no replay do pet, o
   reset no registro final do pet, a versão 11 do Tamer); o que o envio aceito grava; o Respeito conferido, com a trava dos 200 pontos; os
   dois rankings e as rotas; o "baixar os dados" e apagar a conta. A vida é a da MMO3 (test/gabaritos/vida_101.json), que fica no Rookie e
   não ganhou medalha: as medalhas vistas são testadas com a campanha posta à mão no pet. */
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, it } from "vitest";
import { MEDALHAS, Motor } from "../../web/app/motor/index.ts";
import { BONUS_RESET, PONTOS_MINIMOS_RESET, TAMER_LENDARIO } from "../../web/app/src/ranking/pontos.ts";
import { Tamer, VERSAO_TAMER, VERSAO_TAMER_RESET } from "../../web/app/src/tamer.ts";
import { MIGRACOES, VERSAO_BANCO, type Banco } from "../src/conta/banco.ts";
import { conferir, feitosVistos, hashRegistro, VERSOES_TAMER_CONFERIDAS, type Aceito } from "../src/envio/conferir.ts";
import { congelaEm } from "../src/envio/semanas.ts";
import { gravarPontuacoes, LINHAS_DOS_RANKINGS, rankingDigimons, rankingTamers, respeitoDaConta } from "../src/premios/rankings.ts";
import { contar, criarConta, montar, Navegador, type Montado } from "./navegador.ts";

type Evento = [number, string, ...unknown[]];
interface Save { semente: number; log: Evento[]; versao: number }
const VIDA: Save = JSON.parse(readFileSync(new URL("./gabaritos/vida_101.json", import.meta.url), "utf-8"));
const SEMANA = "2026-11-16";
const idDaConta = (n: Navegador) => n.pedir("/conta").then(r => r.json()).then((d: any) => d.conta.id as string);

let M: Montado, nav: Navegador, csrf: string, eu: string;
beforeEach(async () => {
  M = montar();
  nav = new Navegador(M.app);
  csrf = await criarConta(nav);
  eu = await idDaConta(nav);
});

let nContas = 0;
function conta(banco: Banco, apelido = `Gabumon#${3000 + ++nContas}`): string {
  const id = `conta-mmo8-${++nContas}`;
  banco.prepare("INSERT INTO contas (id, apelido, criada_em, idade) VALUES (?, ?, 0, '18_ou_mais')").run(id, apelido);
  return id;
}
/** o que a conferência devolve, só com as partes que gravarPontuacoes lê */
function aceito(x: { pontos?: number; estagio?: string; forma?: string; medalhas?: string[]; liga?: boolean; reset?: Aceito["reset"] }): Aceito {
  return { digimon: { pontos: x.pontos ?? 0, estagio: x.estagio ?? "crianca", forma: x.forma ?? "Agumon", nivelReset: 0 },
    feitos: { medalhas: x.medalhas ?? [], liga: x.liga ?? false },
    reset: x.reset ?? { situacao: "sem_reset", nivel: null, hash: null, por: null } } as unknown as Aceito;
}
const resetConfere = (nivel: 0 | 1 | 2 | 3, por = "reset"): Aceito["reset"] => ({ situacao: "confere", nivel, hash: "a".repeat(64), por });
const pet = (semente: number, versao = VIDA.versao) => ({ semente, versao });
/** o registro do Tamer (versão 11) com o reset do pet da vida, no nível e com o hash e o tamanho dados */
function tamerComReset(nivel: 0 | 1 | 2 | 3, log: readonly unknown[] = VIDA.log): { versao: number; log: unknown[] } {
  const t = new Tamer();
  t.resetar({ pet: VIDA.semente, hash: hashRegistro(log), eventos: log.length, est: "crianca", forma: "Agumon", nivel, tick: 1000, por: "reset" }, Date.UTC(2026, 10, 18));
  return { versao: VERSAO_TAMER_RESET, log: JSON.parse(JSON.stringify(t.log)) };
}
const envioDaVida = (tamer: { versao: number; log: unknown[] }) =>
  ({ pet: { semente: VIDA.semente, log: VIDA.log as never, versao: VIDA.versao }, tamer: tamer as never });

describe("o banco", () => {
  it("a migração 8 traz os Digimon, os resets e os feitos do Tamer, vazios", () => {
    expect(VERSAO_BANCO).toBeGreaterThanOrEqual(8);
    expect(MIGRACOES[7]).toContain("CREATE TABLE digimons");
    for (const t of ["digimons", "resets", "feitos_tamer"]) expect(contar(M.banco, t)).toBe(0);
  });
});

describe("a conferência", () => {
  it("o envio aceito diz o Digimon (os pontos da vida, o maior estágio, a forma, o nível do reset), os feitos e o reset", () => {
    const r = conferir(envioDaVida({ versao: VERSAO_TAMER, log: [] }));
    expect(r.resultado).toBe("aceito");
    if (r.resultado !== "aceito") return;
    expect(r.digimon).toMatchObject({ pontos: 0, estagio: "crianca", nivelReset: 0 });
    expect(typeof r.digimon.forma).toBe("string");
    expect(r.feitos).toEqual({ medalhas: [], liga: false });
    expect(r.reset).toEqual({ situacao: "sem_reset", nivel: null, hash: null, por: null });
  });
  it("as versões do Tamer: a 10 e a 11; a 12 e a 9, não", () => {
    expect(VERSOES_TAMER_CONFERIDAS).toEqual([10, 11]);
    expect(conferir(envioDaVida({ versao: 11, log: [] })).resultado).toBe("aceito");
    for (const v of [9, 12]) {
      const r = conferir(envioDaVida({ versao: v, log: [] }));
      expect(r.resultado === "recusado" && r.motivo).toBe("versao_tamer_desconhecida");
    }
  });
  it("as medalhas contam só se o replay do pet que as ganhou mostra a vitória contra o líder; a Liga, se o pet tem o título", () => {
    const m = new Motor(101), t = new Tamer();
    MEDALHAS.slice(0, 6).forEach((md, i) => t.ganhar(md.id, m, 1000 + i));
    m.campanha[MEDALHAS[0].lider] = 1;
    m.campanha[MEDALHAS[2].lider] = 2;
    t.ganharTitulo(m, 2000);
    expect(feitosVistos(t, m)).toEqual({ medalhas: [MEDALHAS[0].id, MEDALHAS[2].id], liga: false });
    m.liga.titulos = 1;
    expect(feitosVistos(t, m).liga).toBe(true);
    expect(feitosVistos(t, new Motor(202))).toEqual({ medalhas: [], liga: false });   // outro pet: nada dele
  });
  it("o reset no registro final do pet confere pelo nível refeito; o nível errado é recusado; outro registro do pet não confere", () => {
    const ok = conferir(envioDaVida(tamerComReset(0)));
    expect(ok.resultado === "aceito" && ok.reset).toEqual({ situacao: "confere", nivel: 0, hash: hashRegistro(VIDA.log), por: "reset" });
    const errado = conferir(envioDaVida(tamerComReset(1)));
    expect(errado.resultado === "recusado" && errado.motivo).toBe("reset_nao_confere");
    expect(errado.resultado === "recusado" && errado.detalhe).toMatch(/nível 1 .* nível 0/);
    const antes = conferir(envioDaVida(tamerComReset(1, VIDA.log.slice(0, 500))));
    expect(antes.resultado === "aceito" && antes.reset.situacao).toBe("outro_registro");
  });
});

describe("o que o envio aceito grava", () => {
  it("o total da vida só sobe, e a hora é a de quando chegou ao valor; o estágio e a forma são os do último envio", () => {
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ pontos: 30, estagio: "crianca", forma: "Agumon" }), "e1", 1000);
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ pontos: 20, estagio: "adolescente", forma: "Greymon" }), "e2", 2000);
    expect(M.banco.prepare("SELECT pontos, estagio, forma, pontos_em, aposentado_em FROM digimons WHERE conta_id = ?").get(eu))
      .toEqual({ pontos: 30, estagio: "adolescente", forma: "Greymon", pontos_em: 1000, aposentado_em: null });
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ pontos: 45 }), "e3", 3000);
    expect(M.banco.prepare("SELECT pontos, pontos_em FROM digimons WHERE conta_id = ?").get(eu)).toEqual({ pontos: 45, pontos_em: 3000 });
  });
  it("os feitos entram uma vez, no primeiro envio que os mostra; o reset conferido aposenta o Digimon", () => {
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ medalhas: ["campina"], liga: true }), "e1", 1000);
    gravarPontuacoes(M.banco, eu, pet(8), aceito({ medalhas: ["campina", "torre"] }), "e2", 2000);
    expect(M.banco.prepare("SELECT feito, pet, visto_em FROM feitos_tamer WHERE conta_id = ? ORDER BY feito").all(eu)).toEqual([
      { feito: "liga", pet: 7, visto_em: 1000 }, { feito: "medalha:campina", pet: 7, visto_em: 1000 }, { feito: "medalha:torre", pet: 8, visto_em: 2000 }]);
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ reset: { situacao: "outro_registro", nivel: 1, hash: "b".repeat(64), por: "reset" } }), "e3", 3000);
    expect(contar(M.banco, "resets")).toBe(0);
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ reset: resetConfere(1) }), "e4", 4000);
    expect(M.banco.prepare("SELECT pet, nivel, por, visto_em FROM resets WHERE conta_id = ?").all(eu)).toEqual([{ pet: 7, nivel: 1, por: "reset", visto_em: 4000 }]);
    expect(M.banco.prepare("SELECT aposentado_em FROM digimons WHERE conta_id = ? AND pet = 7").get(eu)).toEqual({ aposentado_em: 4000 });
  });
  it("pela rota: o envio aceito grava o Digimon e o reset conferido; o recusado, nada", async () => {
    const env = (tamer: { versao: number; log: unknown[] }) => nav.json("POST", "/envios", envioDaVida(tamer), csrf);
    expect((await env(tamerComReset(1))).status).toBe(422);
    expect(contar(M.banco, "digimons")).toBe(0);
    expect((await env(tamerComReset(0))).status).toBe(201);
    expect(M.banco.prepare("SELECT pet, pontos, estagio FROM digimons WHERE conta_id = ?").get(eu)).toEqual({ pet: VIDA.semente, pontos: 0, estagio: "crianca" });
    expect(M.banco.prepare("SELECT nivel FROM resets WHERE conta_id = ?").get(eu)).toEqual({ nivel: 0 });
  });
});

describe("o Respeito conferido", () => {
  it("100 por líder, 500 a Liga; o reset pelo nível, só com 200 pontos do Digimon conferidos (refeito a cada leitura)", () => {
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ pontos: 80, medalhas: ["campina", "torre"], liga: true }), "e1", 1000);
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ pontos: 80, reset: resetConfere(1) }), "e2", 2000);
    expect(respeitoDaConta(M.banco, eu)).toMatchObject({ total: 700, lideres: 200, liga: 500, resets: 0, chegou_em: 1000 });
    /* o mesmo pet (outra versão do save) chega ao mínimo: o reset passa a contar */
    gravarPontuacoes(M.banco, eu, pet(7, VIDA.versao - 1), aceito({ pontos: PONTOS_MINIMOS_RESET }), "e3", 3000);
    expect(respeitoDaConta(M.banco, eu)).toMatchObject({ total: 700 + BONUS_RESET[1].respeito, resets: 300, chegou_em: 3000 });
  });
  it("soma os títulos da semana e os selos da MMO7", () => {
    M.banco.prepare("INSERT INTO segredos_semana (semana, segredo, criado_em, publicado_em) VALUES (?, ?, 0, ?)").run(SEMANA, "ab".repeat(32), congelaEm(SEMANA));
    M.banco.prepare(`INSERT INTO tabelas_semana (semana, estagio, posicao, conta_id, pontos, rivais_vencidos, lutas_usadas, hora_dos_pontos)
      VALUES (?, 'Rookie', 1, ?, 30, 1, 1, NULL)`).run(SEMANA, eu);
    M.banco.prepare("INSERT INTO tabelas_dia (dia, posicao, conta_id, vitorias, vida_ultima, terminou_em, selo) VALUES ('2026-11-17', 1, ?, 3, 10, 0, 1)").run(eu);
    gravarPontuacoes(M.banco, eu, pet(7), aceito({ medalhas: ["campina"] }), "e1", 1000);
    expect(respeitoDaConta(M.banco, eu)).toMatchObject({ total: 100 + 100 + 20, titulos: 100, selos: 20, chegou_em: congelaEm(SEMANA) });
  });
});

describe("os dois rankings", () => {
  it("os Digimon: só os pets com pontos, pelo total e por quem chegou antes; o aposentado fica; as linhas de quem pede vêm marcadas", () => {
    const a = conta(M.banco, "Palmon#1001"), b = conta(M.banco, "Tentomon#1002");
    gravarPontuacoes(M.banco, a, pet(1), aceito({ pontos: 120, forma: "Togemon", estagio: "adolescente" }), "a1", 1000);
    gravarPontuacoes(M.banco, b, pet(2), aceito({ pontos: 120, forma: "Kabuterimon", estagio: "adolescente" }), "b1", 900);
    gravarPontuacoes(M.banco, eu, pet(3), aceito({ pontos: 300, forma: "WarGrowlmon", estagio: "adulto", reset: resetConfere(1) }), "e1", 2000);
    gravarPontuacoes(M.banco, eu, pet(4), aceito({ pontos: 0 }), "e2", 2000);
    const d = rankingDigimons(M.banco, eu) as { linhas: any[]; total: number };
    expect(d.total).toBe(3);
    expect(d.linhas.map(l => [l.posicao, l.forma, l.pontos, l.estagio, l.aposentado, l.voce])).toEqual([
      [1, "WarGrowlmon", 300, "Ultimate", true, true], [2, "Kabuterimon", 120, "Champion", false, false], [3, "Togemon", 120, "Champion", false, false]]);
    expect(d.linhas[0].pet).toBe(3);
    expect(d.linhas[1].pet).toBeUndefined();   // a semente de outra conta não sai
  });
  it("os Tamers: pelo Respeito, por quem chegou antes; o nível só com o marco 10 conferido; Lendário a partir de 10 000", () => {
    const a = conta(M.banco, "Palmon#1001"), b = conta(M.banco, "Tentomon#1002");
    gravarPontuacoes(M.banco, a, pet(1), aceito({ medalhas: ["campina"] }), "a1", 2000);
    gravarPontuacoes(M.banco, b, pet(2), aceito({ medalhas: ["torre"] }), "b1", 1000);
    /* eu: 6 líderes, a Liga e 9 resets no nível 3, cada um com 200 pontos: 600 + 500 + 9 000 */
    MEDALHAS.slice(0, 6).forEach(md => gravarPontuacoes(M.banco, eu, pet(10), aceito({ medalhas: [md.id], liga: true }), "e0", 500));
    for (let i = 0; i < 9; i++) gravarPontuacoes(M.banco, eu, pet(20 + i), aceito({ pontos: 200, reset: resetConfere(3) }), "e" + i, 600 + i);
    M.banco.prepare(`INSERT INTO envios (id, conta_id, recebido_em, pet, versao_pet, eventos, hash_log, versao_tamer, hash_tamer, resultado, marco10, pontos,
      lutas_ranqueadas, ms_conferencia, marcos_tamer) VALUES ('x', ?, 0, 10, 38, 1, 'h', 10, 'h', 'aceito', 'confere', 0, 0, 1, '[5,7,8,9,10]')`).run(eu);
    const d = rankingTamers(M.banco, eu) as { linhas: any[]; total: number };
    expect(d.total).toBe(3);
    expect(d.linhas.map(l => [l.posicao, l.apelido, l.respeito, l.titulo, l.nivel, l.voce])).toEqual([
      [1, expect.any(String), 10100, "Tamer Lendário", 20, true], [2, "Tentomon#1002", 100, null, null, false], [3, "Palmon#1001", 100, null, null, false]]);
    expect(10100).toBeGreaterThanOrEqual(TAMER_LENDARIO);
    expect(LINHAS_DOS_RANKINGS).toBe(100);
  });
});

describe("as rotas", () => {
  it("pedem a sessão", async () => {
    const sem = new Navegador(M.app);
    expect((await sem.pedir("/digimons")).status).toBe(401);
    expect((await sem.pedir("/tamers")).status).toBe(401);
  });
  it("devolvem os rankings, e o /premios traz o Respeito inteiro", async () => {
    gravarPontuacoes(M.banco, eu, pet(3), aceito({ pontos: 60, forma: "Greymon", medalhas: ["campina"] }), "e1", 1000);
    const dg = await (await nav.pedir("/digimons")).json() as any;
    expect(dg).toMatchObject({ total: 1, linhas: [{ posicao: 1, forma: "Greymon", pontos: 60, voce: true, pet: 3 }] });
    const tm = await (await nav.pedir("/tamers")).json() as any;
    expect(tm).toMatchObject({ total: 1, linhas: [{ posicao: 1, respeito: 100, voce: true, titulo: null }] });
    const pr = await (await nav.pedir("/premios")).json() as any;
    expect(pr.respeito).toMatchObject({ conferido: 100, lideres: 100, liga: 0, resets: 0, titulos: 0, selos: 0, contagem: { lideres: 1 } });
    expect(pr.respeito.como).toMatch(/reset/);
  });
  it("o baixar os dados traz as pontuações; apagar a conta leva tudo", async () => {
    gravarPontuacoes(M.banco, eu, pet(3), aceito({ pontos: 60, medalhas: ["campina"], reset: resetConfere(0) }), "e1", 1000);
    const d = await (await nav.pedir("/conta/dados")).json() as any;
    expect(d.pontuacoes.digimons).toHaveLength(1);
    expect(d.pontuacoes.resets).toHaveLength(1);
    expect(d.pontuacoes.feitos).toEqual([{ feito: "medalha:campina", pet: 3, visto_em: new Date(1000).toISOString(), envio_id: "e1" }]);
    expect((await nav.json("DELETE", "/conta", { confirmar: "apagar" }, csrf)).status).toBe(200);
    for (const t of ["digimons", "resets", "feitos_tamer"]) expect(contar(M.banco, t)).toBe(0);
  });
});
