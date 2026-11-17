/* O envio dos logs (MMO3): a rota POST /envios com a sessão e o CSRF da conta (CN2), a conferência pelo replay do motor no Node, o marco
   do nível 10 (marcoConfere, MMO2), os pontos (MMO1), o que fica no banco (MMO-4) e o apagar a conta.
   A vida é a do gabarito test/gabaritos/vida_101.json (scripts/gerar_vida_teste.ts: a vida 101 da MMO0, com o DigiBrain modular). */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, it } from "vitest";
import { Motor, VERSAO_PET_LAB } from "../../web/app/motor/index.ts";
import { VERSAO_TAMER } from "../../web/app/src/tamer.ts";
import { conferir, lerEnvio } from "../src/envio/conferir.ts";
import { apagarRegistroEm, apagarRegistrosVencidos, fimDaSemana, LIMITE_ENVIO, LOG_DIAS_DEPOIS_DA_SEMANA } from "../src/envio/rotas.ts";
import { contar, criarConta, montar, Navegador, ORIGEM_JOGO, type Montado } from "./navegador.ts";

type Evento = [number, string, ...unknown[]];
interface Save { semente: number; log: Evento[]; versao: number }
const VIDA: Save = JSON.parse(readFileSync(new URL("./gabaritos/vida_101.json", import.meta.url), "utf-8"));
const copia = <T,>(x: T): T => JSON.parse(JSON.stringify(x)) as T;
const tamerVazio = () => ({ versao: VERSAO_TAMER, log: [] as unknown[] });
const envioDe = (pet: Save = VIDA, tamer: { versao: number; log: unknown[] } = tamerVazio()) => ({ pet: copia(pet), tamer: copia(tamer) });
const sha = (x: unknown) => createHash("sha256").update(JSON.stringify(x)).digest("hex");

let M: Montado, nav: Navegador, csrf: string;
beforeEach(async () => {
  M = montar();
  nav = new Navegador(M.app);
  csrf = await criarConta(nav);
});
const enviar = (corpo: unknown, token: string | undefined = csrf, extra: Record<string, string> = {}) => nav.json("POST", "/envios", corpo, token, extra);

describe("o gabarito da vida", () => {
  it("é uma vida inteira da MMO0 que o motor do Node refaz", () => {
    expect(VIDA.log.length).toBeGreaterThan(1000);
    expect(VIDA.log.filter(e => e[1] === "l").length).toBeGreaterThan(300);
    const m = Motor.reproduzir(VIDA.semente, VIDA.log as never, VIDA.versao);
    expect(m.morte).toBeTruthy();
  });
});

describe("POST /envios: o envio válido", () => {
  it("refaz o log, guarda o hash, o resultado e os pontos, e devolve 201", async () => {
    const r = await enviar(envioDe());
    expect(r.status).toBe(201);
    const d = await r.json() as any;
    expect(d).toMatchObject({ resultado: "aceito", motivo: null, marco10: "sem_marco", pontos: 0, lutas_ranqueadas: 0, pet: 101,
      versao_pet: VIDA.versao, eventos: VIDA.log.length, hash_log: sha(VIDA.log), versao_tamer: VERSAO_TAMER, hash_tamer: sha([]) });
    expect(d.lutas).toEqual([]);   // nenhuma semente ranqueada entregue ainda (a MMO4)
    expect(d.ms.total).toBeGreaterThan(0);
    expect(d.registro_guardado_ate).toBe(new Date(apagarRegistroEm(M.relogio.t)).toISOString());
    expect(contar(M.banco, "envios")).toBe(1);
    expect(contar(M.banco, "envios_registros")).toBe(1);
    const reg = M.banco.prepare("SELECT registro_pet, registro_tamer FROM envios_registros").get() as { registro_pet: string; registro_tamer: string };
    expect(JSON.parse(reg.registro_pet)).toEqual(VIDA.log);
    expect(JSON.parse(reg.registro_tamer)).toEqual([]);
    console.log(`  a conferência de uma vida (${VIDA.log.length} eventos, rota inteira): ${JSON.stringify(d.ms)} ms`);
  });
  it("o mesmo envio de novo devolve a conferência guardada (200, repetido), sem linha nova", async () => {
    expect((await enviar(envioDe())).status).toBe(201);
    const r = await enviar(envioDe());
    expect(r.status).toBe(200);
    expect(await r.json()).toMatchObject({ resultado: "aceito", repetido: true });
    expect(contar(M.banco, "envios")).toBe(1);
  });
  it("GET /envios lista os envios da conta, sem os registros", async () => {
    await enviar(envioDe());
    const r = await nav.pedir("/envios");
    expect(r.status).toBe(200);
    const lista = await r.json() as any[];
    expect(lista).toHaveLength(1);
    expect(lista[0]).toMatchObject({ resultado: "aceito", hash_log: sha(VIDA.log) });
    expect(JSON.stringify(lista)).not.toContain("registro_pet");
  });
  it("a origem do jogo passa (CORS com credenciais); a de fora leva 403", async () => {
    const ok = await enviar(envioDe(), csrf, { Origin: ORIGEM_JOGO });
    expect(ok.status).toBe(201);
    expect(ok.headers.get("access-control-allow-origin")).toBe(ORIGEM_JOGO);
    expect((await enviar(envioDe(), csrf, { Origin: "https://outro.exemplo" })).status).toBe(403);
  });
});

describe("POST /envios: o que se recusa, com o motivo", () => {
  it("um log adulterado (um evento fora de ordem) não reproduz: 422 com o erro do motor, e o registro não fica", async () => {
    const pet = copia(VIDA);
    pet.log[500]![0] = (pet.log[499]![0] as number) - 100;
    const r = await enviar(envioDe(pet));
    expect(r.status).toBe(422);
    const d = await r.json() as any;
    expect(d).toMatchObject({ resultado: "recusado", motivo: "pet_nao_reproduz", pontos: 0, hash_log: sha(pet.log) });
    expect(d.erro).toMatch(/^o registro do pet não reproduz: /);
    expect(contar(M.banco, "envios")).toBe(1);
    expect(contar(M.banco, "envios_registros")).toBe(0);
  });
  it("um evento inventado também não reproduz", async () => {
    const pet = copia(VIDA);
    pet.log.splice(300, 0, [pet.log[300]![0], "vitoria_gratis", {}]);
    const r = await enviar(envioDe(pet));
    expect(r.status).toBe(422);
    expect(await r.json()).toMatchObject({ motivo: "pet_nao_reproduz" });
  });
  it("uma versão de pet desconhecida: 422 versao_pet_desconhecida, sem refazer", async () => {
    const r = await enviar(envioDe({ ...VIDA, versao: 999 }));
    expect(r.status).toBe(422);
    const d = await r.json() as any;
    expect(d).toMatchObject({ resultado: "recusado", motivo: "versao_pet_desconhecida", versao_pet: 999 });
    expect(d.erro).toMatch(/999/);
  });
  it("o pet de teste do laboratório não se envia", async () => {
    const r = await enviar(envioDe({ ...VIDA, versao: VERSAO_PET_LAB }));
    expect(r.status).toBe(422);
    expect(await r.json()).toMatchObject({ motivo: "versao_pet_desconhecida" });
  });
  it("um registro do Tamer de outra versão: 422 versao_tamer_desconhecida (atualize o jogo)", async () => {
    const r = await enviar(envioDe(VIDA, { versao: VERSAO_TAMER - 1, log: [] }));
    expect(r.status).toBe(422);
    const d = await r.json() as any;
    expect(d.motivo).toBe("versao_tamer_desconhecida");
    expect(d.erro).toMatch(/atualize o jogo/);
  });
  it("um registro do Tamer que não reproduz: 422 tamer_nao_reproduz", async () => {
    const r = await enviar(envioDe(VIDA, { versao: VERSAO_TAMER, log: [["medalha_inventada", {}]] }));
    expect(r.status).toBe(422);
    expect(await r.json()).toMatchObject({ motivo: "tamer_nao_reproduz" });
  });
  it("o marco 10 deste pet sem a evolução a Mega no registro dele: 422 marco_nao_confere", async () => {
    const nivel = ["nivel", { n: 10, quando: 1, pet: VIDA.semente, forma: "WarGreymon", tick: 9000 }];
    const r = await enviar(envioDe(VIDA, { versao: VERSAO_TAMER, log: [nivel] }));
    expect(r.status).toBe(422);
    const d = await r.json() as any;
    expect(d.motivo).toBe("marco_nao_confere");
    expect(contar(M.banco, "envios_registros")).toBe(0);
  });
  it("o marco 10 de outro pet não se confere por este envio (aceito, de_outro_pet)", async () => {
    const nivel = ["nivel", { n: 10, quando: 1, pet: 7, forma: "WarGreymon", tick: 9000 }];
    const r = await enviar(envioDe(VIDA, { versao: VERSAO_TAMER, log: [nivel] }));
    expect(r.status).toBe(201);
    expect(await r.json()).toMatchObject({ resultado: "aceito", marco10: "de_outro_pet" });
  });
  it("a pontuação vinda do cliente, o save do grupo e a forma errada levam 400, e nada se guarda", async () => {
    for (const corpo of [{ ...envioDe(), pontos: 9999 }, { pet: { ...VIDA, grupo: true }, tamer: tamerVazio() }, { pet: VIDA },
      { pet: { ...VIDA, semente: "101" }, tamer: tamerVazio() }, { pet: { ...VIDA, log: [1, 2] }, tamer: tamerVazio() }, [1], "não é json"]) {
      const r = await enviar(corpo);
      expect(r.status, JSON.stringify(corpo).slice(0, 60)).toBe(400);
      expect((await r.json() as any).erro).toMatch(/^envio malformado: /);
    }
    expect(contar(M.banco, "envios")).toBe(0);
  });
});

describe("POST /envios: a sessão, o CSRF e o tamanho", () => {
  it("sem sessão: 401, e nada se guarda", async () => {
    const anonimo = new Navegador(M.app);
    const r = await anonimo.json("POST", "/envios", envioDe(), csrf);
    expect(r.status).toBe(401);
    expect((await anonimo.pedir("/envios")).status).toBe(401);
    expect(contar(M.banco, "envios")).toBe(0);
  });
  it("sem o CSRF ou com o errado: 403, e nada se guarda", async () => {
    expect((await nav.json("POST", "/envios", envioDe())).status).toBe(403);
    expect((await enviar(envioDe(), "x".repeat(csrf.length))).status).toBe(403);
    expect(contar(M.banco, "envios")).toBe(0);
  });
  it("grande demais: 413 (pelo Content-Length e pelo corpo lido), e nada se guarda", async () => {
    const pet = { ...VIDA, log: [...VIDA.log, [0, "x", "a".repeat(LIMITE_ENVIO)]] };
    const r = await enviar(envioDe(pet as Save));
    expect(r.status).toBe(413);
    expect((await r.json() as any).erro).toMatch(/grande demais/);
    /* sem o Content-Length: um corpo em fluxo */
    const corpo = JSON.stringify(envioDe(pet as Save));
    const fluxo = new ReadableStream({ start(c) { c.enqueue(new TextEncoder().encode(corpo)); c.close(); } });
    const r2 = await nav.pedir("/envios", { method: "POST", body: fluxo, duplex: "half",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf } } as never);
    expect(r2.status).toBe(413);
    expect(contar(M.banco, "envios")).toBe(0);
  });
  it("o corpo que não é JSON pelo Content-Type: 415", async () => {
    const r = await nav.pedir("/envios", { method: "POST", body: JSON.stringify(envioDe()), headers: { "Content-Type": "text/plain", "X-CSRF-Token": csrf } });
    expect(r.status).toBe(415);
  });
});

describe("a política do log (MMO-4) e o apagar a conta", () => {
  it("o registro sai 30 dias depois do fim da semana de Brasília; a linha fica, com o hash e os pontos", async () => {
    await enviar(envioDe());
    const fim = fimDaSemana(M.relogio.t);
    /* 2026-11-16 12:00 UTC é segunda, 09:00 em Brasília: a semana fecha na segunda 23, 00:00 em Brasília (03:00 UTC) */
    expect(new Date(fim).toISOString()).toBe("2026-11-23T03:00:00.000Z");
    /* a sessão (30 dias) vence antes: a limpeza roda pela função, como roda em cada envio e em cada GET /envios */
    const limite = fim + LOG_DIAS_DEPOIS_DA_SEMANA * 86_400_000;
    expect(apagarRegistroEm(Date.UTC(2026, 10, 16, 12))).toBe(limite);
    expect(apagarRegistrosVencidos(M.banco, limite - 1)).toBe(0);
    expect(contar(M.banco, "envios_registros")).toBe(1);
    expect(apagarRegistrosVencidos(M.banco, limite)).toBe(1);
    expect(contar(M.banco, "envios_registros")).toBe(0);
    const linha = M.banco.prepare("SELECT resultado, hash_log, pontos FROM envios").get() as Record<string, unknown>;
    expect(linha).toEqual({ resultado: "aceito", hash_log: sha(VIDA.log), pontos: 0 });
  });
  it("a limpeza também roda no GET /envios da conta", async () => {
    await enviar(envioDe());
    /* dentro da sessão de 30 dias, com o prazo do registro trazido para agora */
    M.relogio.t += 29 * 86_400_000;
    M.banco.prepare("UPDATE envios_registros SET apagar_em = ?").run(M.relogio.t);
    const lista = await (await nav.pedir("/envios")).json() as any[];
    expect(lista[0]).toMatchObject({ resultado: "aceito", hash_log: sha(VIDA.log), pontos: 0, registro_guardado_ate: null });
    expect(contar(M.banco, "envios_registros")).toBe(0);
  });
  it("baixar os meus dados traz os envios, sem os registros", async () => {
    await enviar(envioDe());
    const d = await (await nav.pedir("/conta/dados")).json() as any;
    expect(d.envios).toHaveLength(1);
    expect(d.envios[0]).toMatchObject({ hash_log: sha(VIDA.log), resultado: "aceito" });
  });
  it("apagar a conta apaga os envios e os registros, e a outra conta fica", async () => {
    await enviar(envioDe());
    const pet = copia(VIDA);
    pet.log[500]![0] = 0;
    await enviar(envioDe(pet));   // um recusado também
    const outro = new Navegador(M.app);
    const csrf2 = await criarConta(outro, "caio");
    expect((await outro.json("POST", "/envios", envioDe(), csrf2)).status).toBe(201);
    expect(contar(M.banco, "envios")).toBe(3);
    const r = await nav.json("DELETE", "/conta", { confirmar: "apagar" }, csrf);
    expect(r.status).toBe(200);
    expect(contar(M.banco, "envios")).toBe(1);
    expect(contar(M.banco, "envios_registros")).toBe(1);
    expect((await outro.pedir("/envios")).status).toBe(200);
  });
});

describe("a conferência sem a rota", () => {
  it("é a mesma conta do jogo: o pet refeito pelo Motor.reproduzir e os pontos pela MMO1", () => {
    const r = conferir(lerEnvio(envioDe()));
    expect(r.resultado).toBe("aceito");
    if (r.resultado !== "aceito") return;
    expect(r.marco10).toBe("sem_marco");
    expect(r.ms.replay).toBeGreaterThan(0);
    expect(r.ms.pontos).toBeGreaterThan(0);
  });
});
