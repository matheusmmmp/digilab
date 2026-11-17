/* A luta ranqueada (MMO4, docs/PLANO_V3_MMO.md seções 3 e 4; MMO-6 e MMO-8): a semente da luta ranqueada vem do servidor, e a semente
   pedida conta como luta feita. Só com a sessão da conta (CN2):
     POST /sementes   {pet: {semente, versao}, indice, hash} -> 201 {numero, semente, indice, hora, dia, semana, restam_hoje}
                      | 403 nivel_insuficiente {marco} | 409 fora_de_ordem, indice_ja_enviado, hash_diferente | 422 versao_pet_desconhecida
                      | 429 limite_do_dia {reabre_em} | 400 malformado | 401 sem sessão | 403 sem CSRF
     GET  /sementes   as sementes entregues à conta, da mais nova à mais velha

   O pedido (seção 3): o cliente manda o tamanho do registro do pet naquela hora (`indice`, a posição em que a luta vai entrar) e o hash do
   registro até ali (`hash`, o SHA-256 do JSON dos `indice` primeiros eventos, D-CONTA-83; o jogo o calcula por hashAte, em
   web/app/src/ranking/pedido.ts). O cliente se compromete antes de saber a semente: o envio (rotas.ts) confere que o registro até o
   `indice` é o do pedido (hash_nao_confere) e só então conta a luta. A luta ranqueada é o evento "l" exatamente no `indice`, com a semente
   entregue (a conta da MMO1, pontos.ts); a semente pedida e não usada ali conta como derrota.

   A semente: HMAC-SHA256(segredo da semana, "<conta>|<número>"), os 4 primeiros bytes (um inteiro sem sinal de 32 bits, como o hashSemente
   do motor). O segredo de cada semana nasce no primeiro pedido dela (32 bytes aleatórios), fica só no banco do servidor, fora do git, e é
   publicado quando a semana fecha (MMO5). O número é o contador de sementes da conta (1, 2, ...).

   As travas do pedido:
     - o nível (MMO-13): a conta tem um envio aceito com o marco do Tamer da config (`marcoRanqueada`: o 10 por padrão, só com o marco
       conferido no registro do pet; no beta, o 7, BT0-1);
     - o limite (MMO-8): no máximo LUTAS_POR_DIA sementes por conta por dia de Brasília, pelo relógio do servidor (pontos.ts);
     - a ordem: o `indice` nunca volta (a conta da MMO1 pede as sementes em ordem), nem fica antes do registro já enviado deste pet; no mesmo
       `indice`, o hash tem de ser o mesmo do pedido anterior. */
import { createHmac, randomBytes } from "node:crypto";
import type { Context, Hono } from "hono";
import { VERSOES_PET } from "../../../web/app/motor/index.ts";
import { diaDe, FUSO_BRASILIA_MS, LUTAS_POR_DIA, semanaDe } from "../../../web/app/src/ranking/pontos.ts";
import { MARCO_MEGA } from "../../../web/app/src/tamer.ts";
import { transacao, type Banco } from "../conta/banco.ts";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta } from "../conta/rotas.ts";
import type { EntregueComHash } from "./conferir.ts";

const DIA_MS = 86_400_000;
/** o tamanho do segredo da semana, em bytes */
export const BYTES_SEGREDO = 32;

/** por que o pedido da semente foi recusado (o código vai na resposta) */
export type MotivoPedido =
  | "versao_pet_desconhecida"  // a versão do pet não é uma das que o servidor confere
  | "nivel_insuficiente"       // a conta não tem um envio aceito com o marco que abre a luta ranqueada
  | "limite_do_dia"            // já foram LUTAS_POR_DIA sementes hoje
  | "fora_de_ordem"            // o indice é menor que o de uma semente já entregue a este pet
  | "indice_ja_enviado"        // o indice é menor que o registro deste pet já enviado: a posição já tem outro evento
  | "hash_diferente";          // o mesmo indice de um pedido anterior, com outro registro até ali

export class PedidoMalformado extends Error {}

export interface Pedido { pet: { semente: number; versao: number }; indice: number; hash: string }

const objeto = (x: unknown): x is Record<string, unknown> => typeof x === "object" && x !== null && !Array.isArray(x);

/** confere a forma do corpo do pedido; o que falta, sobra ou tem o tipo errado levanta PedidoMalformado (400) */
export function lerPedido(d: unknown): Pedido {
  if (!objeto(d)) throw new PedidoMalformado("o pedido é um objeto {pet, indice, hash}");
  const extra = Object.keys(d).filter(k => !["pet", "indice", "hash"].includes(k));
  if (extra.length) throw new PedidoMalformado(`campo desconhecido no pedido: ${extra.join(", ")}`);
  const pet = d.pet;
  if (!objeto(pet)) throw new PedidoMalformado("'pet' é {semente, versao}");
  const extraPet = Object.keys(pet).filter(k => k !== "semente" && k !== "versao");
  if (extraPet.length) throw new PedidoMalformado(`campo desconhecido em 'pet': ${extraPet.join(", ")} (o pedido não leva o registro)`);
  if (!Number.isSafeInteger(pet.semente)) throw new PedidoMalformado("'pet.semente' é um inteiro");
  if (!Number.isSafeInteger(pet.versao)) throw new PedidoMalformado("'pet.versao' é um inteiro");
  if (!Number.isSafeInteger(d.indice) || (d.indice as number) < 0) throw new PedidoMalformado("'indice' é um inteiro de 0 em diante");
  if (typeof d.hash !== "string" || !/^[0-9a-f]{64}$/.test(d.hash)) throw new PedidoMalformado("'hash' é o SHA-256 em hexadecimal minúsculo");
  return { pet: { semente: pet.semente as number, versao: pet.versao as number }, indice: d.indice as number, hash: d.hash };
}

/** o segredo da semana (cria no primeiro pedido dela) */
export function segredoDaSemana(banco: Banco, semana: string, agora: number): Buffer {
  const ja = banco.prepare("SELECT segredo FROM segredos_semana WHERE semana = ?").get(semana) as { segredo: string } | undefined;
  if (ja) return Buffer.from(ja.segredo, "hex");
  const novo = randomBytes(BYTES_SEGREDO);
  banco.prepare("INSERT INTO segredos_semana (semana, segredo, criado_em) VALUES (?, ?, ?)").run(semana, novo.toString("hex"), agora);
  return novo;
}

/** a semente da luta ranqueada número `numero` da conta, com o segredo da semana */
export const sementeDe = (segredo: Buffer, contaId: string, numero: number): number =>
  createHmac("sha256", segredo).update(`${contaId}|${numero}`).digest().readUInt32BE(0);

/** o começo do dia seguinte de Brasília, em ms UTC (quando o limite do dia reabre) */
export const proximoDia = (hora: number): number => Date.parse(diaDe(hora) + "T00:00:00Z") - FUSO_BRASILIA_MS + DIA_MS;

interface LinhaSemente { numero: number; pet: number; versao_pet: number; indice: number; hash_ate: string; semente: number; hora: number; dia: string; semana: string }

/** as sementes entregues a um pet da conta, na ordem do pedido (o que a conferência do envio usa) */
export function entreguesDoPet(banco: Banco, contaId: string, pet: number, versao: number): EntregueComHash[] {
  return (banco.prepare("SELECT numero, indice, hash_ate, semente, hora FROM sementes WHERE conta_id = ? AND pet = ? AND versao_pet = ? ORDER BY numero")
    .all(contaId, pet, versao) as unknown as LinhaSemente[])
    .map(l => ({ numero: l.numero, semente: l.semente, indice: l.indice, hora: l.hora, hash: l.hash_ate }));
}

/** as sementes da conta para o GET e o "baixar os meus dados" (as horas em ISO) */
export function sementesDaConta(banco: Banco, contaId: string): Record<string, unknown>[] {
  return (banco.prepare("SELECT numero, pet, versao_pet, indice, hash_ate, semente, hora, dia, semana FROM sementes WHERE conta_id = ? ORDER BY numero DESC")
    .all(contaId) as unknown as LinhaSemente[]).map(l => ({ ...l, hora: new Date(l.hora).toISOString() }));
}

/** a conta já abriu a luta ranqueada: um envio aceito com o marco. O 10 só vale conferido no registro do pet (marco10 = 'confere'); os
    outros (as medalhas e o título) vêm do registro do Tamer do envio aceito */
export function nivelAberto(banco: Banco, contaId: string, marco: number): boolean {
  const sql = marco === MARCO_MEGA
    ? "SELECT 1 FROM envios WHERE conta_id = ? AND resultado = 'aceito' AND marco10 = 'confere' LIMIT 1"
    : "SELECT 1 FROM envios, json_each(envios.marcos_tamer) AS j WHERE envios.conta_id = ? AND envios.resultado = 'aceito' AND j.value = ? LIMIT 1";
  return (marco === MARCO_MEGA ? banco.prepare(sql).get(contaId) : banco.prepare(sql).get(contaId, marco)) !== undefined;
}

export function montarRotasSemente(app: Hono, cfg: ConfigConta, g: GuardasConta): void {
  const { banco, agora, marcoRanqueada } = cfg;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });
  const recusar = (c: Context, codigo: number, motivo: MotivoPedido, erro: string, extra: Record<string, unknown> = {}) =>
    json(c, codigo, { motivo, erro, ...extra });

  app.use("/sementes", g.cors);

  app.get("/sementes", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    return json(c, 200, sementesDaConta(banco, s.conta_id));
  });

  app.post("/sementes", async c => {
    const s = g.sessaoParaMudar(c);
    if (s instanceof Response) return s;
    if (!(c.req.header("content-type") ?? "").startsWith("application/json")) return json(c, 415, { erro: "o pedido é JSON" });
    let p: Pedido;
    try {
      let d: unknown;
      try { d = JSON.parse(await c.req.text()); } catch (err) { throw new PedidoMalformado(`o corpo não é JSON: ${(err as Error).message}`); }
      p = lerPedido(d);
    } catch (err) {
      if (err instanceof PedidoMalformado) return json(c, 400, { erro: `pedido malformado: ${err.message}` });
      throw err;
    }
    if (!VERSOES_PET.includes(p.pet.versao))
      return recusar(c, 422, "versao_pet_desconhecida", `versão de pet desconhecida: ${p.pet.versao} (o servidor confere a ${VERSOES_PET.join(", ")})`);

    /* tudo numa transação, sem await no meio: dois pedidos ao mesmo tempo não passam juntos do limite */
    return transacao(banco, () => {
      /* a hora nunca volta dentro da conta (a conta da MMO1 pede as sementes em ordem de hora): um relógio que recua fica na última */
      const ultimaHora = (banco.prepare("SELECT max(hora) AS h FROM sementes WHERE conta_id = ?").get(s.conta_id) as { h: number | null }).h;
      const t = Math.max(agora(), ultimaHora ?? -Infinity), dia = diaDe(t), semana = semanaDe(t);
      if (!nivelAberto(banco, s.conta_id, marcoRanqueada))
        return recusar(c, 403, "nivel_insuficiente", `a luta ranqueada abre no marco ${marcoRanqueada} do Tamer, num envio aceito desta conta`
          + (marcoRanqueada === MARCO_MEGA ? " (o primeiro Mega, conferido no registro do pet)" : ""), { marco: marcoRanqueada });
      const hoje = (banco.prepare("SELECT count(*) AS n FROM sementes WHERE conta_id = ? AND dia = ?").get(s.conta_id, dia) as { n: number }).n;
      if (hoje >= LUTAS_POR_DIA)
        return recusar(c, 429, "limite_do_dia", `já foram ${LUTAS_POR_DIA} lutas ranqueadas hoje (o dia de Brasília, pelo relógio do servidor)`,
          { reabre_em: new Date(proximoDia(t)).toISOString() });
      const ultima = banco.prepare("SELECT indice, hash_ate FROM sementes WHERE conta_id = ? AND pet = ? AND versao_pet = ? ORDER BY numero DESC LIMIT 1")
        .get(s.conta_id, p.pet.semente, p.pet.versao) as { indice: number; hash_ate: string } | undefined;
      if (ultima && p.indice < ultima.indice)
        return recusar(c, 409, "fora_de_ordem", `o indice ${p.indice} é menor que o da última semente deste pet (${ultima.indice})`);
      if (ultima && p.indice === ultima.indice && p.hash !== ultima.hash_ate)
        return recusar(c, 409, "hash_diferente", `o registro até o indice ${p.indice} não é o do pedido anterior no mesmo indice`);
      const enviado = (banco.prepare("SELECT max(eventos) AS n FROM envios WHERE conta_id = ? AND pet = ? AND versao_pet = ? AND resultado = 'aceito'")
        .get(s.conta_id, p.pet.semente, p.pet.versao) as { n: number | null }).n;
      if (enviado !== null && p.indice < enviado)
        return recusar(c, 409, "indice_ja_enviado", `o registro deste pet já foi enviado com ${enviado} eventos: a luta entra no fim do registro`);

      /* o número da luta: o próximo da conta. Uma semente que já foi deste pet (2^-32 por par) pula para o número seguinte: a conta da MMO1
         não aceita a mesma semente duas vezes */
      const segredo = segredoDaSemana(banco, semana, t);
      const doPet = new Set(entreguesDoPet(banco, s.conta_id, p.pet.semente, p.pet.versao).map(x => x.semente));
      let numero = Number((banco.prepare("SELECT coalesce(max(numero), 0) AS n FROM sementes WHERE conta_id = ?").get(s.conta_id) as { n: number }).n) + 1;
      let semente = sementeDe(segredo, s.conta_id, numero);
      while (doPet.has(semente)) semente = sementeDe(segredo, s.conta_id, ++numero);
      banco.prepare("INSERT INTO sementes (conta_id, numero, pet, versao_pet, indice, hash_ate, semente, hora, dia, semana) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        .run(s.conta_id, numero, p.pet.semente, p.pet.versao, p.indice, p.hash, semente, t, dia, semana);
      return json(c, 201, { numero, semente, indice: p.indice, hora: new Date(t).toISOString(), dia, semana, restam_hoje: LUTAS_POR_DIA - hoje - 1 });
    });
  });
}
