/* O cliente da luta ranqueada (MMO4, src/ranking/ranqueada.ts): o pedido da semente e os estados dele, a previa, o envio e o reenvio, com
   um servidor falso (as respostas do servidor_web/src/envio: sementes.ts e rotas.ts). */
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { DIGIMON_DA_FORMA } from "../motor/index.ts";
import { PONTOS_FAIXA, diaDe, semanaDe } from "../src/ranking/pontos.ts";
import {
  CHAVE_RANQUEADA, RQ, desligarRanqueada, divergiu, enviarRegistro, fecharEstado, lerGuardado, ligarRanqueada, lutaPerdida, pedirSemente, placarDoPet,
  registrarPrevia, temPendente, valorDoRival,
} from "../src/ranking/ranqueada.ts";

const AGORA = Date.parse("2026-11-18T15:00:00Z");   // uma quarta
const PET = { semente: 101, versao: 21, log: [] as never[] };
const TAMER = { versao: 10, log: [] };
const RIVAL = Object.keys(DIGIMON_DA_FORMA).find(k => DIGIMON_DA_FORMA[k]?.[1] === "Champion")!;
const VALE = PONTOS_FAIXA.Champion;

type Resposta = { status: number; corpo: unknown } | "cai";
function ambiente(rotas: Record<string, (corpo: unknown) => Resposta>) {
  const guardado = new Map<string, string>(), pedidos: { rota: string; corpo: unknown; csrf: string | null; credentials: unknown }[] = [];
  ligarRanqueada({
    api: "http://127.0.0.1:8766/", agora: () => AGORA,
    armaz: { getItem: k => guardado.get(k) ?? null, setItem: (k, v) => { guardado.set(k, v); } },
    buscar: async (url, init) => {
      const rota = `${init?.method ?? "GET"} ${url.replace("http://127.0.0.1:8766", "")}`, corpo = init?.body ? JSON.parse(String(init.body)) : null;
      pedidos.push({ rota, corpo, csrf: (init?.headers as Record<string, string> | undefined)?.["X-CSRF-Token"] ?? null, credentials: init?.credentials });
      const f = rotas[rota];
      if (!f) throw new Error(`rota sem resposta no teste: ${rota}`);
      const r = f(corpo);
      if (r === "cai") throw new TypeError("fetch failed");
      return new Response(JSON.stringify(r.corpo), { status: r.status, headers: { "Content-Type": "application/json" } });
    },
  });
  return { guardado, pedidos };
}
const conta = () => ({ status: 200, corpo: { conta: { id: "c1" }, csrf: "tok" } });
const entregue = (numero: number, restam: number, indice = 0) => ({ status: 201, corpo: { numero, semente: 1000 + numero, indice, hora: new Date(AGORA).toISOString(),
  dia: diaDe(AGORA), semana: semanaDe(AGORA), restam_hoje: restam } });

beforeEach(() => desligarRanqueada());
afterEach(() => desligarRanqueada());

describe("o pedido da semente", () => {
  it("201: guarda a luta, manda o csrf e a sessão, e conta a luta de hoje", async () => {
    const a = ambiente({ "GET /conta": conta, "POST /sementes": () => entregue(8, 2) });
    const l = await pedirSemente(PET);
    expect(l).toMatchObject({ numero: 8, semente: 1008, indice: 0, doDia: 8, pet: 101, envio: "pendente", previa: null });
    expect(RQ.pedido.tipo).toBe("parado");
    expect(RQ.hoje).toBe(8);
    const p = a.pedidos.find(x => x.rota === "POST /sementes")!;
    expect(p.csrf).toBe("tok");
    expect(p.credentials).toBe("include");
    expect(p.corpo).toMatchObject({ pet: { semente: 101, versao: 21 }, indice: 0 });
    expect((p.corpo as { hash: string }).hash).toMatch(/^[0-9a-f]{64}$/);
    expect(lerGuardado(a.guardado.get(CHAVE_RANQUEADA)!)).toHaveLength(1);
  });
  it("sem sessão (401 no /conta): sem_conta, e nada é pedido", async () => {
    const a = ambiente({ "GET /conta": () => ({ status: 401, corpo: { erro: "sem sessão" } }) });
    expect(await pedirSemente(PET)).toBeNull();
    expect(RQ.pedido.tipo).toBe("sem_conta");
    expect(a.pedidos.some(x => x.rota === "POST /sementes")).toBe(false);
  });
  it("o servidor não responde: sem_resposta, e nada fica guardado", async () => {
    ambiente({ "GET /conta": conta, "POST /sementes": () => "cai" });
    expect(await pedirSemente(PET)).toBeNull();
    expect(RQ.pedido.tipo).toBe("sem_resposta");
    expect(RQ.lutas).toHaveLength(0);
    fecharEstado();
    expect(RQ.pedido.tipo).toBe("parado");
  });
  it("429: limite, com a hora em que volta", async () => {
    ambiente({ "GET /conta": conta, "POST /sementes": () => ({ status: 429, corpo: { motivo: "limite_do_dia", erro: "x", reabre_em: "2026-11-19T03:00:00.000Z" } }) });
    expect(await pedirSemente(PET)).toBeNull();
    expect(RQ.pedido).toEqual({ tipo: "limite", reabreEm: Date.parse("2026-11-19T03:00:00Z") });
    expect(RQ.hoje).toBe(10);
  });
  it("403 nivel_insuficiente: trancada, com o marco; 422: versão; 409: recusado sem gastar", async () => {
    ambiente({ "GET /conta": conta, "POST /sementes": () => ({ status: 403, corpo: { motivo: "nivel_insuficiente", erro: "x", marco: 7 } }) });
    expect(await pedirSemente(PET)).toBeNull();
    expect(RQ.pedido).toEqual({ tipo: "trancada", marco: 7 });
    expect(RQ.trancada).toBe(7);
    ambiente({ "GET /conta": conta, "POST /sementes": () => ({ status: 422, corpo: { motivo: "versao_pet_desconhecida", erro: "x" } }) });
    expect(await pedirSemente(PET)).toBeNull();
    expect(RQ.pedido.tipo).toBe("versao");
    ambiente({ "GET /conta": conta, "POST /sementes": () => ({ status: 409, corpo: { motivo: "fora_de_ordem", erro: "x" } }) });
    expect(await pedirSemente(PET)).toBeNull();
    expect(RQ.pedido).toEqual({ tipo: "recusado", motivo: "fora_de_ordem", gasta: false });
  });
  it("resposta que o jogo não entende levanta (falha alto), e o pedido volta a parado", async () => {
    ambiente({ "GET /conta": conta, "POST /sementes": () => ({ status: 201, corpo: { numero: 1 } }) });
    await expect(pedirSemente(PET)).rejects.toThrow(/não entende/);
    expect(RQ.pedido.tipo).toBe("parado");
    ambiente({ "GET /conta": conta, "POST /sementes": () => ({ status: 500, corpo: { erro: "quebrou" } }) });
    await expect(pedirSemente(PET)).rejects.toThrow(/quebrou/);
  });
  it("a luta pedida que não entrou no registro fica gasta", async () => {
    ambiente({ "GET /conta": conta, "POST /sementes": () => entregue(1, 9) });
    const l = (await pedirSemente(PET))!;
    lutaPerdida(l.numero, "o registro do pet mudou durante o pedido");
    expect(RQ.pedido).toEqual({ tipo: "recusado", motivo: "o registro do pet mudou durante o pedido", gasta: true });
  });
});

describe("a prévia e o valor do rival", () => {
  it("a vitória vale a faixa; a seguinte contra o mesmo rival na semana, a metade", async () => {
    let n = 0;
    ambiente({ "GET /conta": conta, "POST /sementes": () => { n++; return entregue(n, 10 - n, n - 1); } });
    expect(valorDoRival(RIVAL, 101, AGORA)).toEqual({ pontos: VALE, vencido: 0 });
    const a = (await pedirSemente(PET))!;
    registrarPrevia(a.numero, RIVAL, "campo", true, AGORA);
    expect(RQ.lutas[0].previa).toEqual({ venceu: true, pontos: VALE });
    expect(RQ.resultado).toBe(a.numero);
    expect(valorDoRival(RIVAL, 101, AGORA)).toEqual({ pontos: VALE / 2, vencido: 1 });
    /* a derrota vale 0 e não mexe na metade; outro pet não herda a metade */
    const b = (await pedirSemente({ ...PET, log: [[0, "x", {}]] as never[] }))!;
    registrarPrevia(b.numero, RIVAL, "campo", false, AGORA);
    expect(RQ.lutas[1].previa).toEqual({ venceu: false, pontos: 0 });
    expect(valorDoRival(RIVAL, 101, AGORA).vencido).toBe(1);
    expect(valorDoRival(RIVAL, 202, AGORA).pontos).toBe(VALE);
    /* a prévia nunca soma no placar da semana (UX-LR-3) */
    expect(placarDoPet(101, AGORA)).toEqual({ hoje: 2, pontos: 0, rivais: 0 });
  });
});

describe("o envio", () => {
  const luta = (semente: number, situacao: string, pontos: number) => ({ semente, indice: 0, hora: AGORA, dia: diaDe(AGORA), semana: semanaDe(AGORA), situacao, rival: RIVAL, faixa: "Champion",
    estagio: "Champion", pontos, vidaFinal: 1 });
  async function comPrevia(envio: (corpo: unknown) => Resposta) {
    const a = ambiente({ "GET /conta": conta, "POST /sementes": () => entregue(3, 7), "POST /envios": envio });
    const l = (await pedirSemente(PET))!;
    registrarPrevia(l.numero, RIVAL, "campo", true, AGORA);
    return { a, l };
  }
  it("201: a luta vira conferida e os pontos entram no placar", async () => {
    const { a } = await comPrevia(() => ({ status: 201, corpo: { resultado: "aceito", lutas: [luta(1003, "vitoria", VALE)] } }));
    expect(temPendente(101)).toBe(true);
    expect(await enviarRegistro(PET, TAMER)).toBe(true);
    expect(RQ.lutas[0]).toMatchObject({ envio: "conferido", servidor: { situacao: "vitoria", pontos: VALE } });
    expect(divergiu(RQ.lutas[0])).toBe(false);
    expect(temPendente(101)).toBe(false);
    expect(placarDoPet(101, AGORA)).toEqual({ hoje: 3, pontos: VALE, rivais: 1 });
    const p = a.pedidos.find(x => x.rota === "POST /envios")!;
    expect(p.corpo).toEqual({ pet: { semente: 101, log: [], versao: 21 }, tamer: TAMER });
    expect(p.csrf).toBe("tok");
  });
  it("o servidor viu outra luta: vale a dele", async () => {
    await comPrevia(() => ({ status: 201, corpo: { resultado: "aceito", lutas: [luta(1003, "derrota", 0)] } }));
    await enviarRegistro(PET, TAMER);
    expect(divergiu(RQ.lutas[0])).toBe(true);
    expect(placarDoPet(101, AGORA).pontos).toBe(0);
  });
  it("sem resposta: a luta continua pendente, e o reenvio a confere", async () => {
    let cai = true;
    await comPrevia(() => (cai ? "cai" : { status: 201, corpo: { resultado: "aceito", lutas: [luta(1003, "vitoria", VALE)] } }));
    expect(await enviarRegistro(PET, TAMER)).toBe(false);
    expect(RQ.lutas[0].envio).toBe("pendente");
    expect(RQ.enviando).toBe(false);
    cai = false;
    expect(await enviarRegistro(PET, TAMER)).toBe(true);
    expect(RQ.lutas[0].envio).toBe("conferido");
  });
  it("200 repetido (sem as lutas): a prévia fica como conferida", async () => {
    await comPrevia(() => ({ status: 200, corpo: { resultado: "aceito", repetido: true, pontos: VALE } }));
    await enviarRegistro(PET, TAMER);
    expect(RQ.lutas[0]).toMatchObject({ envio: "conferido", servidor: { situacao: "vitoria", pontos: VALE } });
  });
  it("422: o envio recusado marca a luta, e a versão antiga pede para atualizar", async () => {
    await comPrevia(() => ({ status: 422, corpo: { resultado: "recusado", motivo: "versao_tamer_desconhecida", erro: "x" } }));
    expect(await enviarRegistro(PET, TAMER)).toBe(true);
    expect(RQ.lutas[0]).toMatchObject({ envio: "recusado", motivo: "versao_tamer_desconhecida" });
    expect(RQ.pedido.tipo).toBe("versao");
  });
  it("a luta do pet pedida em outro aparelho entra pelo que o servidor contou", async () => {
    ambiente({ "GET /conta": conta, "POST /envios": () => ({ status: 201, corpo: { resultado: "aceito", lutas: [luta(777, "vitoria", VALE)] } }) });
    await enviarRegistro(PET, TAMER);
    expect(RQ.lutas).toHaveLength(1);
    expect(placarDoPet(101, AGORA).pontos).toBe(VALE);
    expect(valorDoRival(RIVAL, 101, AGORA).pontos).toBe(VALE / 2);
  });
});

describe("o que fica guardado", () => {
  it("volta ao ligar de novo; formato desconhecido levanta", async () => {
    const a = ambiente({ "GET /conta": conta, "POST /sementes": () => entregue(1, 9) });
    await pedirSemente(PET);
    const texto = a.guardado.get(CHAVE_RANQUEADA)!;
    desligarRanqueada();
    expect(RQ.lutas).toHaveLength(0);
    ligarRanqueada({ api: "http://x", agora: () => AGORA, armaz: { getItem: () => texto, setItem: () => {} }, buscar: async () => { throw new Error("não"); } });
    expect(RQ.lutas).toHaveLength(1);
    expect(() => lerGuardado('{"versao":2,"lutas":[]}')).toThrow(/formato desconhecido/);
    expect(() => lerGuardado('{"versao":1,"lutas":[{"numero":"a"}]}')).toThrow(/inválida/);
    expect(lerGuardado(null)).toEqual([]);
  });
});
