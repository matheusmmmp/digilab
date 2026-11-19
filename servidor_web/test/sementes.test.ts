/* A luta ranqueada (MMO4): o pedido da semente com o hash do registro até ali (POST /sementes), a trava do nível, o limite do dia, a ordem,
   e o envio que confere o hash e conta a luta (a semente pedida conta como luta feita). A vida é o gabarito da MMO3
   (test/gabaritos/vida_101.json): a luta ranqueada é a primeira luta da Arena dela, refeita com a semente do servidor. */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, it } from "vitest";
import { DIGIMON_DA_FORMA, IDS_CENA, MEDALHAS, Motor } from "../../web/app/motor/index.ts";
import { hashAte, pedidoDaSemente } from "../../web/app/src/ranking/pedido.ts";
import { LUTAS_POR_DIA, PONTOS_FAIXA } from "../../web/app/src/ranking/pontos.ts";
import { Tamer, VERSAO_TAMER } from "../../web/app/src/tamer.ts";
import { configDoAmbiente } from "../src/conta/config.ts";
import { abrirBanco } from "../src/conta/banco.ts";
import { conferir, hashesAte, lerEnvio, type EntregueComHash } from "../src/envio/conferir.ts";
import { ConferidorEmWorker } from "../src/envio/conferidor.ts";
import { proximoDia, sementeDe } from "../src/envio/sementes.ts";
import { contar, criarConta, montar, Navegador, API, JOGO, type Montado } from "./navegador.ts";

type Evento = [number, string, ...unknown[]];
interface Save { semente: number; log: Evento[]; versao: number }
const VIDA: Save = JSON.parse(readFileSync(new URL("./gabaritos/vida_101.json", import.meta.url), "utf-8"));
const sha = (x: unknown) => createHash("sha256").update(JSON.stringify(x)).digest("hex");
const DIA_MS = 86_400_000;

/** a posição da primeira luta da Arena da vida (um rival com faixa que vale ponto) */
const K = VIDA.log.findIndex(e => e[1] === "l" && PONTOS_FAIXA[DIGIMON_DA_FORMA[(e[2] as { r: string }).r]?.[1] ?? ""] !== undefined);
const LUTA = VIDA.log[K] as [number, "l", { r: string; s: number; m?: string }];
const prefixo = (n: number): Evento[] => JSON.parse(JSON.stringify(VIDA.log.slice(0, n)));
/** o registro com a luta ranqueada no lugar da luta K: o prefixo e a mesma luta com a semente do servidor */
const comLuta = (semente: number): Evento[] => [...prefixo(K), [LUTA[0], "l", { ...LUTA[2], s: semente }]];

/** um registro do Tamer com n medalhas (o marco 7 são 3), ganhas pelo pet da vida */
function tamerCom(n: number): { versao: number; log: unknown[] } {
  const m = Motor.reproduzir(VIDA.semente, VIDA.log.slice(0, 50) as never, VIDA.versao), t = new Tamer();
  MEDALHAS.slice(0, n).forEach((x, i) => t.ganhar(x.id, m, Date.UTC(2026, 10, 15) + i));
  return { versao: VERSAO_TAMER, log: JSON.parse(JSON.stringify(t.log)) };
}
const pet = (log: Evento[]) => ({ semente: VIDA.semente, log, versao: VIDA.versao });
const pedido = (indice = K, hash = sha(VIDA.log.slice(0, indice))) => ({ pet: { semente: VIDA.semente, versao: VIDA.versao }, indice, hash, rival: LUTA[2].r, mapa: LUTA[2].m ?? null });

let M: Montado, nav: Navegador, csrf: string;
const enviar = (log: Evento[], tamer = tamerCom(3)) => nav.json("POST", "/envios", { pet: pet(log), tamer }, csrf);
const pedir = (corpo: unknown = pedido()) => nav.json("POST", "/sementes", corpo, csrf);
/** a conta com o nível aberto: o marco 7 do beta e um envio aceito do prefixo até a luta, com 3 medalhas */
async function abrir(ambiente: Record<string, string> = { DIGILAB_MARCO_RANQUEADA: "7" }) {
  M = montar(undefined, ambiente);
  nav = new Navegador(M.app);
  csrf = await criarConta(nav);
}
beforeEach(async () => { await abrir(); });

describe("a vida do teste", () => {
  it("tem uma luta da Arena, e a mesma luta com outra semente reproduz", () => {
    expect(K).toBeGreaterThan(0);
    expect(() => Motor.reproduzir(VIDA.semente, comLuta(12345) as never, VIDA.versao)).not.toThrow();
  });
});

describe("POST /sementes: a trava do nível (MMO-13; no beta, o marco 7)", () => {
  it("sem envio aceito, 403 nivel_insuficiente", async () => {
    const r = await pedir();
    expect(r.status).toBe(403);
    expect(await r.json()).toMatchObject({ motivo: "nivel_insuficiente", marco: 7 });
    expect(contar(M.banco, "sementes")).toBe(0);
  });
  it("um envio aceito com menos de 3 medalhas não abre o marco 7", async () => {
    expect((await enviar(prefixo(K), tamerCom(2))).status).toBe(201);
    expect((await (await pedir()).json() as any).motivo).toBe("nivel_insuficiente");
  });
  it("com 3 medalhas abre; o envio guarda os marcos do Tamer", async () => {
    const e = await enviar(prefixo(K));
    expect(e.status).toBe(201);
    expect((await e.json() as any).marcos_tamer).toEqual([5, 7]);
    expect((await pedir()).status).toBe(201);
  });
  it("no padrão (o marco 10, o primeiro Mega conferido), as medalhas não bastam", async () => {
    await abrir({});
    expect((await enviar(prefixo(K))).status).toBe(201);
    const r = await pedir();
    expect(r.status).toBe(403);
    expect((await r.json() as any).erro).toContain("primeiro Mega");
  });
  it("o marco fora dos do Tamer não sobe", () => {
    expect(() => configDoAmbiente({ porta: 8766, banco: abrirBanco(":memory:"),
      ambiente: { DIGILAB_URL_API: API, DIGILAB_URL_JOGO: JOGO, DIGILAB_MARCO_RANQUEADA: "4" } })).toThrow(/DIGILAB_MARCO_RANQUEADA/);
  });
});

describe("POST /sementes: a semente", () => {
  beforeEach(async () => { expect((await enviar(prefixo(K))).status).toBe(201); });

  it("devolve 201 com a semente, o número, a hora, o dia e a semana do servidor; GET /sementes a lista", async () => {
    const r = await pedir();
    expect(r.status).toBe(201);
    const d = await r.json() as any;
    expect(d).toMatchObject({ numero: 1, indice: K, hora: new Date(M.relogio.t).toISOString(), dia: "2026-11-16", semana: "2026-11-16",
      restam_hoje: LUTAS_POR_DIA - 1 });
    expect(Number.isInteger(d.semente) && d.semente >= 0 && d.semente < 2 ** 32).toBe(true);
    const segredo = M.banco.prepare("SELECT segredo FROM segredos_semana WHERE semana = ?").get("2026-11-16") as { segredo: string };
    const conta = (M.banco.prepare("SELECT conta_id FROM sementes").get() as { conta_id: string }).conta_id;
    expect(d.semente).toBe(sementeDe(Buffer.from(segredo.segredo, "hex"), conta, 1));
    const lista = await (await nav.pedir("/sementes")).json() as any[];
    expect(lista).toHaveLength(1);
    expect(lista[0]).toMatchObject({ numero: 1, semente: d.semente, hash_ate: sha(VIDA.log.slice(0, K)) });
  });
  it("o pedido do jogo (pedidoDaSemente, crypto.subtle) é o mesmo que o servidor confere", async () => {
    const p = await pedidoDaSemente(pet(prefixo(K)) as never, LUTA[2].r, LUTA[2].m ?? null);
    expect(p).toEqual(pedido());
    expect((await pedir(p)).status).toBe(201);
  });
  it("a semente é do segredo da semana, da conta e do número: outra conta, outra semente", () => {
    const s = Buffer.alloc(32, 7);
    expect(sementeDe(s, "a", 1)).toBe(sementeDe(s, "a", 1));
    expect(new Set([sementeDe(s, "a", 1), sementeDe(s, "b", 1), sementeDe(s, "a", 2), sementeDe(Buffer.alloc(32, 8), "a", 1)]).size).toBe(4);
  });
  it("o segredo é um por semana", async () => {
    await pedir();
    M.relogio.t += 7 * DIA_MS;
    await pedir();
    expect(contar(M.banco, "segredos_semana")).toBe(2);
  });
  it("sem sessão leva 401; sem o CSRF, 403; o pedido malformado, 400; a versão desconhecida, 422", async () => {
    const outro = new Navegador(M.app);
    expect((await outro.json("POST", "/sementes", pedido())).status).toBe(401);
    expect((await nav.json("POST", "/sementes", pedido())).status).toBe(403);   // sem o X-CSRF-Token
    expect((await pedir({ ...pedido(), pontos: 80 })).status).toBe(400);
    expect((await pedir({ ...pedido(), pet: { ...pedido().pet, log: [] } })).status).toBe(400);
    expect((await pedir(pedido(K, "abc"))).status).toBe(400);
    expect((await pedir({ ...pedido(), indice: -1 })).status).toBe(400);
    const v = await pedir({ ...pedido(), pet: { semente: VIDA.semente, versao: 999 } });
    expect(v.status).toBe(422);
    expect((await v.json() as any).motivo).toBe("versao_pet_desconhecida");
    expect(contar(M.banco, "sementes")).toBe(0);
  });
});

describe("POST /sementes: o limite do dia (MMO-8) e a ordem", () => {
  beforeEach(async () => { expect((await enviar(prefixo(K))).status).toBe(201); });

  it(`a ${LUTAS_POR_DIA + 1}ª semente do dia leva 429 com a hora em que reabre; no dia seguinte, volta`, async () => {
    for (let i = 0; i < LUTAS_POR_DIA; i++) expect((await pedir()).status).toBe(201);
    const r = await pedir();
    expect(r.status).toBe(429);
    expect(await r.json()).toMatchObject({ motivo: "limite_do_dia", reabre_em: new Date(proximoDia(M.relogio.t)).toISOString() });
    expect(proximoDia(M.relogio.t)).toBe(Date.UTC(2026, 10, 17, 3));   // 00:00 de Brasília
    expect(contar(M.banco, "sementes")).toBe(LUTAS_POR_DIA);
    M.relogio.t = proximoDia(M.relogio.t);
    expect((await pedir()).status).toBe(201);
  });
  it("o limite é da conta, pelo relógio do servidor: a hora de Brasília vira o dia às 03:00 UTC", async () => {
    M.relogio.t = Date.UTC(2026, 10, 17, 2, 59);   // ainda 16/11 em Brasília
    for (let i = 0; i < LUTAS_POR_DIA; i++) expect((await pedir()).status).toBe(201);
    expect((await pedir()).status).toBe(429);
    M.relogio.t = Date.UTC(2026, 10, 17, 3);
    expect((await pedir()).status).toBe(201);
  });
  it("o indice não volta (409 fora_de_ordem); o mesmo indice com outro registro leva 409 hash_diferente", async () => {
    expect((await pedir(pedido(K + 2))).status).toBe(201);
    const a = await pedir(pedido(K + 1));
    expect(a.status).toBe(409);
    expect((await a.json() as any).motivo).toBe("fora_de_ordem");
    const b = await pedir(pedido(K + 2, sha(["outro"])));
    expect(b.status).toBe(409);
    expect((await b.json() as any).motivo).toBe("hash_diferente");
  });
  it("o indice antes do registro já enviado leva 409 indice_ja_enviado", async () => {
    expect((await enviar(prefixo(K + 5))).status).toBe(201);
    const r = await pedir(pedido(K));
    expect(r.status).toBe(409);
    expect((await r.json() as any).motivo).toBe("indice_ja_enviado");
    expect((await pedir(pedido(K + 5))).status).toBe(201);
  });
  it("a hora da semente nunca volta, mesmo que o relógio do servidor recue", async () => {
    await pedir();
    const h = M.relogio.t;
    M.relogio.t -= 60_000;
    expect((await (await pedir()).json() as any).hora).toBe(new Date(h).toISOString());
  });
});

describe("POST /envios com a semente: a luta ranqueada conta", () => {
  let semente: number;
  beforeEach(async () => {
    expect((await enviar(prefixo(K))).status).toBe(201);
    semente = (await (await pedir()).json() as any).semente;
  });

  it("a luta com a semente do servidor no indice do pedido conta: vitória pela faixa, derrota 0", async () => {
    const r = await enviar(comLuta(semente));
    expect(r.status).toBe(201);
    const d = await r.json() as any;
    expect(d.sementes).toBe(1);
    expect(d.lutas).toHaveLength(1);
    const l = d.lutas[0];
    expect(l).toMatchObject({ semente, indice: K, rival: LUTA[2].r, dia: "2026-11-16", semana: "2026-11-16" });
    expect(["vitoria", "derrota"]).toContain(l.situacao);
    const faixa = DIGIMON_DA_FORMA[LUTA[2].r]![1];
    expect(d.pontos).toBe(l.situacao === "vitoria" ? PONTOS_FAIXA[faixa] : 0);
    expect(d.semanas).toEqual([expect.objectContaining({ semana: "2026-11-16", lutasUsadas: 1, pontos: d.pontos })]);
    console.log(`  a luta ranqueada do teste: ${l.situacao} contra ${l.rival} (${faixa}), ${d.pontos} pontos`);
  });
  it("antes da luta, a semente fica pendente (0, mas usada)", async () => {
    const r = await enviar(prefixo(K));   // o mesmo registro de antes, agora com uma semente: não é o repetido
    expect(r.status).toBe(201);
    const d = await r.json() as any;
    expect(d.repetido).toBeUndefined();
    expect(d.lutas[0].situacao).toBe("pendente");
    expect(d.semanas[0]).toMatchObject({ lutasUsadas: 1, pontos: 0 });
  });
  it("a semente pedida e não usada no indice conta como derrota (nao_enviada)", async () => {
    const r = await enviar(prefixo(K + 1));   // no indice está a luta de antes, com a semente da própria vida
    expect(r.status).toBe(201);
    const d = await r.json() as any;
    expect(d.lutas[0].situacao).toBe("nao_enviada");
    expect(d.pontos).toBe(0);
    expect(d.semanas[0].lutasUsadas).toBe(1);
  });
  it("o registro mudado antes do indice depois do pedido leva 422 hash_nao_confere, e não fica registro", async () => {
    const log = comLuta(semente);
    log.splice(K - 1, 1);   // tira um evento antes da luta: a posição e o registro até ali mudam
    log.push([LUTA[0], "l", { ...LUTA[2], s: semente }]);
    const r = await enviar(log);
    expect(r.status).toBe(422);
    expect(await r.json()).toMatchObject({ resultado: "recusado", motivo: "hash_nao_confere" });
    expect((M.banco.prepare("SELECT count(*) AS n FROM envios_registros r JOIN envios e ON e.id = r.envio_id WHERE e.resultado = 'recusado'").get() as { n: number }).n).toBe(0);
  });
  it("o worker recebe as sementes e dá a mesma conferência", async () => {
    const conta = (M.banco.prepare("SELECT conta_id FROM sementes").get() as { conta_id: string }).conta_id;
    const entregues: EntregueComHash[] = [{ numero: 1, semente, indice: K, hora: M.relogio.t, hash: sha(VIDA.log.slice(0, K)) }];
    const e = lerEnvio({ pet: pet(comLuta(semente)), tamer: tamerCom(3) });
    const w = new ConferidorEmWorker();
    try {
      const la = await w.conferir(e, entregues), aqui = conferir(e, entregues);
      expect(la.resultado).toBe("aceito");
      expect({ ...la, ms: null }).toEqual({ ...aqui, ms: null });
    } finally { await w.fechar(); }
    expect(conta).toBeTruthy();
  });
  it("apagar a conta leva as sementes; o segredo da semana fica (é do servidor)", async () => {
    expect(contar(M.banco, "sementes")).toBe(1);
    const r = await nav.json("DELETE", "/conta", { confirmar: "apagar" }, csrf);
    expect(r.status).toBe(200);
    expect(contar(M.banco, "sementes")).toBe(0);
    expect(contar(M.banco, "segredos_semana")).toBe(1);
  });
  it("o \"baixar os meus dados\" lista as sementes, sem o segredo", async () => {
    const d = await (await nav.pedir("/conta/dados")).json() as any;
    expect(d.sementes).toHaveLength(1);
    expect(d.sementes[0]).toMatchObject({ numero: 1, semente, indice: K });
    const segredo = (M.banco.prepare("SELECT segredo FROM segredos_semana").get() as { segredo: string }).segredo;
    expect(JSON.stringify(d)).not.toContain(segredo);
  });
});

describe("o hash do registro até o indice", () => {
  it("hashesAte (um passe, no servidor) e hashAte (o jogo, crypto.subtle) dão o SHA-256 do JSON do prefixo", async () => {
    const indices = [0, 1, 2, K, VIDA.log.length - 1, VIDA.log.length];
    const h = hashesAte(VIDA.log, [...indices, VIDA.log.length + 3]);
    expect([...h.keys()].sort((a, b) => a - b)).toEqual(indices);   // o indice além do registro fica de fora (pendente)
    for (const i of indices) {
      expect(h.get(i)).toBe(sha(VIDA.log.slice(0, i)));
      expect(await hashAte(VIDA.log as never, i)).toBe(sha(VIDA.log.slice(0, i)));
    }
    expect(h.get(0)).toBe(sha([]));
    await expect(hashAte(VIDA.log as never, VIDA.log.length + 1)).rejects.toThrow(/fora do registro/);
  });
});

describe("o rival e o mapa vão no pedido (D-CONTA-116)", () => {
  const OUTRO_RIVAL = Motor.reproduzir(VIDA.semente, prefixo(K) as never, VIDA.versao).rivaisArenaPoc().find(r => r !== LUTA[2].r)!;
  const MAPA = LUTA[2].m ?? null, OUTRO_MAPA = IDS_CENA.find(m => m !== MAPA)!;
  const lutaCom = (semente: number, troca: { r?: string; m?: string }): Evento[] => [...prefixo(K), [LUTA[0], "l", { ...LUTA[2], s: semente, ...troca }]];
  beforeEach(async () => { expect((await enviar(prefixo(K))).status).toBe(201); });

  it("a vida tem outro rival na Arena e outro mapa para trocar", () => {
    expect(OUTRO_RIVAL).toBeTruthy();
    expect(OUTRO_MAPA).toBeTruthy();
  });
  it("sem o rival, com o rival fora da forma ou com o mapa desconhecido, 400, e nenhuma semente sai", async () => {
    const { rival: _r, ...semRival } = pedido();
    const { mapa: _m, ...semMapa } = pedido();
    for (const corpo of [semRival, semMapa, { ...pedido(), rival: "" }, { ...pedido(), rival: "Agumon; DROP" }, { ...pedido(), mapa: "lua" }, { ...pedido(), mapa: 3 }])
      expect((await pedir(corpo)).status).toBe(400);
    expect(contar(M.banco, "sementes")).toBe(0);
  });
  it("201 devolve e guarda o rival e o mapa prometidos; o mapa pode ser null", async () => {
    const d = await (await pedir()).json() as any;
    expect(d).toMatchObject({ rival: LUTA[2].r, mapa: MAPA });
    expect(M.banco.prepare("SELECT rival_pedido, mapa_pedido FROM sementes").get()).toEqual({ rival_pedido: LUTA[2].r, mapa_pedido: MAPA });
    expect((await (await nav.pedir("/sementes")).json() as any)[0]).toMatchObject({ rival_pedido: LUTA[2].r, mapa_pedido: MAPA });
  });
  it("a luta contra o rival prometido, no mapa prometido, conta", async () => {
    const s = await (await pedir()).json() as any;
    const d = await (await enviar(comLuta(s.semente))).json() as any;
    expect(["vitoria", "derrota"]).toContain(d.lutas[0].situacao);
    expect(d.lutas[0].rival).toBe(LUTA[2].r);
  });
  it("a mesma semente contra outro rival não conta: fica não enviada, com 0", async () => {
    const s = await (await pedir()).json() as any;
    const e = await enviar(lutaCom(s.semente, { r: OUTRO_RIVAL }));
    expect(e.status).toBe(201);
    const d = await e.json() as any;
    expect(d.lutas[0]).toMatchObject({ situacao: "nao_enviada", pontos: 0, rival: null });
    expect(d.pontos).toBe(0);
  });
  it("a mesma semente em outro mapa não conta", async () => {
    const s = await (await pedir()).json() as any;
    const d = await (await enviar(lutaCom(s.semente, { m: OUTRO_MAPA }))).json() as any;
    expect(d.lutas[0]).toMatchObject({ situacao: "nao_enviada", pontos: 0 });
  });
  it("a semente de antes da regra (sem rival guardado) conta com qualquer rival", async () => {
    const s = await (await pedir()).json() as any;
    M.banco.prepare("UPDATE sementes SET rival_pedido = NULL, mapa_pedido = NULL").run();
    const d = await (await enviar(lutaCom(s.semente, { r: OUTRO_RIVAL }))).json() as any;
    expect(["vitoria", "derrota"]).toContain(d.lutas[0].situacao);
    expect(d.lutas[0].rival).toBe(OUTRO_RIVAL);
  });
});
