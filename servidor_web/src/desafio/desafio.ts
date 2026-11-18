/* O desafio do dia (MMO6, docs/PLANO_V3_MMO.md seção 6; MMO-10 e MMO-11): a Fábrica do dia. Ninguém luta com o próprio pet: todos recebem
   os mesmos 3 alugados e os mesmos rivais, e cada conta tem uma tentativa por dia de Brasília, pelo relógio do servidor. Só com a sessão da
   conta (CN2):
     GET  /desafio                 o dia aberto, quando fecha e congela, a tentativa da conta (se houver) e os dias fechados
     POST /desafio/tentativa       {v} -> 201 {dia, semente_dia, v, comecou_em, fecha_em, congela_em}
                                   | 409 tentativa_usada | 403 nivel_insuficiente {marco} | 422 versao_fabrica_desconhecida
     POST /desafio/lutas           {dia, k, escolha, trocas} -> 201 {dia, k, semente, hora}
                                   | 404 sem_tentativa | 409 dia_fechado, fora_de_ordem, escolha_diferente, trocas_diferentes, lutas_demais
     POST /desafio/envios          {dia, registro: {v, escolha, lutas, trocas}} -> 200 {resultado: "aceito", ...} | 422 {motivo} | 404 | 409
     GET  /desafio/selos           os selos "Top do dia" da conta
     GET  /desafio/:dia/tabela     a tabela do dia (com a sessão): as 100 primeiras linhas e a de quem pede
     GET  /desafio/:dia/segredo    o segredo de um dia congelado (sem sessão) | 404 {motivo}

   As sementes (MMO-10):
     - a semente do dia = HMAC-SHA256(segredo do dia, "fabrica-do-dia"), os 4 primeiros bytes: a mesma para todos. Dela saem os 3 alugados e
       os rivais (TentativaFabrica.doDia, web/app/motor/fabrica.ts). Pedir a semente do dia já gasta a tentativa do dia (como no desafio
       diário do Spelunky): a segunda leva 409, e o GET devolve a mesma semente a quem perdeu a resposta;
     - a semente da luta k = HMAC-SHA256(segredo do dia, "<conta>|<k>"): de cada conta, e só sai depois da escolha. O pedido leva a escolha
       e as trocas até ali, e o servidor as guarda: o que foi prometido antes de uma semente não muda depois. Com a semente igual para todos,
       quem tem duas contas saberia a sorte antes de escolher; assim, sabe-se a escolha, mas não a sorte.
   O segredo de cada dia nasce na primeira tentativa dele (32 bytes aleatórios), fica só no banco do servidor, fora do git e fora da cascata
   da conta, e é publicado quando o dia congela.

   O envio: o registro da tentativa (web/app/src/ranking/desafio.ts) é refeito pelo motor, no processo (uma tentativa leva milissegundos,
   não o segundo da vida do pet da MMO3). A pontuação nunca vem do cliente. O registro tem de casar com o que o servidor entregou e guardou:
   a versão das regras, a escolha, as sementes (um prefixo das entregues, na ordem) e as trocas prometidas antes de cada semente. Um
   registro mais curto que as sementes entregues só vale se acaba numa derrota (a semente pedida conta como luta). O resultado é o do
   envio aceito com mais lutas; "terminou" é a hora em que o servidor entregou a semente da última luta vencida (o começo da tentativa,
   sem vitória), e não a hora do envio: segurar o envio não muda o desempate.

   O fechamento: o dia vai de 00:00 a 23:59 de Brasília e congela FOLGA_DO_FECHAMENTO_MS depois do fim (a mesma folga da semana; a
   tentativa começada às 23:50 ainda termina). Até lá, as sementes das lutas e os envios ainda entram. No congelamento, numa transação: a
   tabela vai para `tabelas_dia`, com o selo do Top do dia nos primeiros (selosDoDia, MMO-11; só quem venceu ao menos uma luta), e o segredo
   é publicado. A tentativa sem envio aceito não entra na tabela. O fechamento roda sozinho na primeira chamada depois da hora. */
import { createHash, createHmac, randomBytes, randomUUID } from "node:crypto";
import type { Context, Hono } from "hono";
import { bodyLimit } from "hono/body-limit";
import { VERSAO_FABRICA_ATUAL, VERSOES_FABRICA } from "../../../web/app/motor/index.ts";
import {
  compararDesafio, lerRegistroDesafio, refazerDesafio, RegistroMalformado, selosDoDia, type RegistroDesafio, type ResultadoDesafio,
} from "../../../web/app/src/ranking/desafio.ts";
import { diaDe, FUSO_BRASILIA_MS } from "../../../web/app/src/ranking/pontos.ts";
import { MARCO_MEGA } from "../../../web/app/src/tamer.ts";
import { transacao, type Banco } from "../conta/banco.ts";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta } from "../conta/rotas.ts";
import { FOLGA_DO_FECHAMENTO_MS } from "../envio/semanas.ts";
import { BYTES_SEGREDO, nivelAberto } from "../envio/sementes.ts";

const DIA_MS = 86_400_000;
/** o corpo dos pedidos do desafio, em bytes (PROPOSTO, SEM FONTE): o registro são só as sementes das lutas */
export const LIMITE_DESAFIO = 64 * 1024;
/** as sementes de luta por tentativa (PROPOSTO, SEM FONTE): a Fábrica não tem teto, este é só contra o abuso do banco (33 séries) */
export const LUTAS_MAX_DO_DIA = 100;
/** as linhas da tabela que a resposta leva (PROPOSTO, SEM FONTE); a de quem pede vem sempre */
export const LINHAS_DA_TABELA_DO_DIA = 100;
/** os dias fechados que o GET /desafio lista (PROPOSTO, SEM FONTE) */
export const DIAS_LISTADOS = 14;
/** o texto do HMAC da semente do dia */
export const ROTULO_SEMENTE_DIA = "fabrica-do-dia";

/** por que o pedido ou o envio foi recusado (o código vai na resposta) */
export type MotivoDesafio =
  | "nivel_insuficiente" | "versao_fabrica_desconhecida" | "tentativa_usada" | "sem_tentativa" | "dia_fechado" | "fora_de_ordem"
  | "escolha_diferente" | "trocas_diferentes" | "lutas_demais"
  /* os do envio, em 422 e guardados */
  | "versao_fabrica_diferente" | "escolha_nao_confere" | "semente_nao_confere" | "trocas_nao_conferem" | "lutas_faltando" | "nao_reproduz";

class Malformado extends Error {}

/* ------------------------------------------------ o dia */
/** o começo do dia de Brasília (AAAA-MM-DD), em ms UTC */
export const comecoDoDia = (dia: string): number => Date.parse(dia + "T00:00:00Z") - FUSO_BRASILIA_MS;
/** o fim do dia: o começo do seguinte */
export const fimDoDia = (dia: string): number => comecoDoDia(dia) + DIA_MS;
/** quando o dia congela */
export const congelaDia = (dia: string): number => fimDoDia(dia) + FOLGA_DO_FECHAMENTO_MS;
/** AAAA-MM-DD de um dia que existe */
export function diaValido(s: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
  const t = Date.parse(s + "T00:00:00Z");
  return Number.isFinite(t) && new Date(t).toISOString().slice(0, 10) === s;
}

/* ------------------------------------------------ as sementes */
/** o segredo do dia (cria na primeira tentativa dele) */
export function segredoDoDia(banco: Banco, dia: string, agora: number): Buffer {
  const ja = banco.prepare("SELECT segredo FROM segredos_dia WHERE dia = ?").get(dia) as { segredo: string } | undefined;
  if (ja) return Buffer.from(ja.segredo, "hex");
  const novo = randomBytes(BYTES_SEGREDO);
  banco.prepare("INSERT INTO segredos_dia (dia, segredo, criado_em) VALUES (?, ?, ?)").run(dia, novo.toString("hex"), agora);
  return novo;
}
const u32 = (segredo: Buffer, texto: string): number => createHmac("sha256", segredo).update(texto).digest().readUInt32BE(0);
/** a semente do dia: a mesma para todos (os alugados e os rivais) */
export const sementeDoDia = (segredo: Buffer): number => u32(segredo, ROTULO_SEMENTE_DIA);
/** a semente da luta k da conta no dia */
export const sementeDaLutaDoDia = (segredo: Buffer, contaId: string, k: number): number => u32(segredo, `${contaId}|${k}`);

/* ------------------------------------------------ o banco */
interface LinhaDesafio {
  conta_id: string; dia: string; comecou_em: number; versao: number; escolha: number | null; trocas: string;
  vitorias: number | null; series: number | null; lutas: number | null; acabou: number | null; vida_ultima: number | null;
  terminou_em: number | null; envio_id: string | null;
}
interface LinhaLuta { k: number; semente: number; hora: number; escolha: number; trocas: string }

const desafioDe = (banco: Banco, contaId: string, dia: string): LinhaDesafio | undefined =>
  banco.prepare("SELECT * FROM desafios WHERE conta_id = ? AND dia = ?").get(contaId, dia) as LinhaDesafio | undefined;
const lutasDe = (banco: Banco, contaId: string, dia: string): LinhaLuta[] =>
  banco.prepare("SELECT k, semente, hora, escolha, trocas FROM desafio_lutas WHERE conta_id = ? AND dia = ? ORDER BY k").all(contaId, dia) as unknown as LinhaLuta[];
const iso = (t: number): string => new Date(t).toISOString();

/** a tentativa para o GET e o "baixar os dados" */
function tentativaParaFora(banco: Banco, l: LinhaDesafio): Record<string, unknown> {
  const segredo = segredoDoDia(banco, l.dia, l.comecou_em);
  return {
    dia: l.dia, v: l.versao, semente_dia: sementeDoDia(segredo), comecou_em: iso(l.comecou_em), escolha: l.escolha, trocas: JSON.parse(l.trocas),
    lutas: lutasDe(banco, l.conta_id, l.dia).map(x => ({ k: x.k, semente: x.semente, hora: iso(x.hora) })),
    conferido: l.vitorias === null ? null : { vitorias: l.vitorias, series: l.series, lutas: l.lutas, acabou: l.acabou === 1,
      vida_ultima_vitoria: l.vida_ultima, terminou_em: iso(l.terminou_em!) },
  };
}

/** tudo do desafio da conta, para o "baixar os meus dados": as tentativas, os envios (sem o registro) e as linhas das tabelas */
export function desafiosDaConta(banco: Banco, contaId: string): Record<string, unknown> {
  const tentativas = (banco.prepare("SELECT * FROM desafios WHERE conta_id = ? ORDER BY dia DESC").all(contaId) as unknown as LinhaDesafio[])
    .map(l => tentativaParaFora(banco, l));
  const envios = (banco.prepare("SELECT id, dia, recebido_em, hash_registro, resultado, motivo, detalhe, vitorias, lutas, ms_conferencia FROM desafio_envios WHERE conta_id = ? ORDER BY recebido_em DESC, id")
    .all(contaId) as unknown as { recebido_em: number }[]).map(e => ({ ...e, recebido_em: iso(e.recebido_em) }));
  const tabelas = (banco.prepare("SELECT dia, posicao, vitorias, vida_ultima, terminou_em, selo FROM tabelas_dia WHERE conta_id = ? ORDER BY dia DESC")
    .all(contaId) as unknown as { terminou_em: number; selo: number }[]).map(t => ({ ...t, terminou_em: iso(t.terminou_em), selo: t.selo === 1 }));
  return { tentativas, envios, tabelas };
}

/* ------------------------------------------------ a tabela e o fechamento */
export interface LinhaTabelaDia { contaId: string; apelido: string; vitorias: number; vidaUltimaVitoria: number; terminouEm: number }

/** a tabela de um dia pelas tentativas conferidas, na ordem do desempate (seção 6); quem empata nos três fica na ordem do apelido */
export function tabelaDoDia(banco: Banco, dia: string): LinhaTabelaDia[] {
  const linhas = (banco.prepare(`SELECT d.conta_id, c.apelido, d.vitorias, d.vida_ultima, d.terminou_em FROM desafios d JOIN contas c ON c.id = d.conta_id
    WHERE d.dia = ? AND d.vitorias IS NOT NULL`).all(dia) as unknown as { conta_id: string; apelido: string; vitorias: number; vida_ultima: number; terminou_em: number }[])
    .map(l => ({ contaId: l.conta_id, apelido: l.apelido, vitorias: l.vitorias, vidaUltimaVitoria: l.vida_ultima, terminouEm: l.terminou_em }));
  return linhas.sort((a, b) => compararDesafio(a, b) || (a.apelido < b.apelido ? -1 : a.apelido > b.apelido ? 1 : 0));
}
/** quem da tabela leva o selo: as primeiras selosDoDia(jogadores) posições, só com ao menos uma vitória */
export const comSelo = (tabela: readonly LinhaTabelaDia[]): boolean[] => {
  const n = selosDoDia(tabela.length);
  return tabela.map((l, i) => i < n && l.vitorias > 0);
};

/** fecha todo dia que já passou da hora de congelar; devolve os que fechou agora. Cada um na sua transação */
export function fecharDias(banco: Banco, agora: number): string[] {
  const abertos = (banco.prepare("SELECT dia FROM segredos_dia WHERE publicado_em IS NULL ORDER BY dia").all() as { dia: string }[])
    .map(l => l.dia).filter(d => congelaDia(d) <= agora);
  for (const dia of abertos) {
    transacao(banco, () => {
      const tabela = tabelaDoDia(banco, dia), selo = comSelo(tabela);
      const por = banco.prepare("INSERT INTO tabelas_dia (dia, posicao, conta_id, vitorias, vida_ultima, terminou_em, selo) VALUES (?, ?, ?, ?, ?, ?, ?)");
      tabela.forEach((l, i) => por.run(dia, i + 1, l.contaId, l.vitorias, l.vidaUltimaVitoria, l.terminouEm, selo[i] ? 1 : 0));
      banco.prepare("UPDATE segredos_dia SET publicado_em = ? WHERE dia = ?").run(agora, dia);
    });
  }
  return abertos;
}
const publicadoEm = (banco: Banco, dia: string): number | null | undefined =>
  (banco.prepare("SELECT publicado_em FROM segredos_dia WHERE dia = ?").get(dia) as { publicado_em: number | null } | undefined)?.publicado_em;

/* ------------------------------------------------ a conferência do envio */
export interface Conferencia { motivo: MotivoDesafio | null; detalhe: string | null; resultado: ResultadoDesafio | null; terminouEm: number | null }

/** confere o registro contra o que o servidor entregou e guardou, e o refaz pelo motor */
export function conferirDesafio(banco: Banco, d: LinhaDesafio, r: RegistroDesafio): Conferencia {
  const recusa = (motivo: MotivoDesafio, detalhe: string): Conferencia => ({ motivo, detalhe, resultado: null, terminouEm: null });
  if (r.v !== d.versao) return recusa("versao_fabrica_diferente", `a tentativa começou com as regras da versão ${d.versao}, não ${r.v}`);
  const entregues = lutasDe(banco, d.conta_id, d.dia);
  if (r.lutas.length > entregues.length) return recusa("semente_nao_confere", `o registro tem ${r.lutas.length} lutas, e o servidor entregou ${entregues.length} sementes`);
  const k = r.lutas.findIndex((s, i) => s !== entregues[i]!.semente);
  if (k >= 0) return recusa("semente_nao_confere", `a luta ${k} não usa a semente que o servidor entregou`);
  if (r.lutas.length > 0 && r.escolha !== d.escolha) return recusa("escolha_nao_confere", `o alugado escolhido antes da primeira semente foi o ${d.escolha}, não o ${r.escolha}`);
  /* as trocas prometidas antes de cada semente: as do registro antes da luta k são as do pedido da semente k */
  for (const e of entregues.slice(0, r.lutas.length)) {
    const prometidas = JSON.stringify(JSON.parse(e.trocas)), doRegistro = JSON.stringify(r.trocas.filter(x => x < e.k));
    if (prometidas !== doRegistro) return recusa("trocas_nao_conferem", `antes da semente da luta ${e.k}, as trocas prometidas foram ${prometidas}, não ${doRegistro}`);
  }
  let refeito: ReturnType<typeof refazerDesafio>;
  try {
    refeito = refazerDesafio(sementeDoDia(segredoDoDia(banco, d.dia, d.comecou_em)), r);
  } catch (err) {
    return recusa("nao_reproduz", (err as Error).message);
  }
  if (r.lutas.length < entregues.length && !refeito.resultado.acabou)
    return recusa("lutas_faltando", `o servidor entregou ${entregues.length} sementes, e o registro para na luta ${r.lutas.length - 1} sem derrota (a semente pedida conta como luta)`);
  const vencidas = refeito.tentativa.lutas.filter(l => l.venceu), u = vencidas[vencidas.length - 1];
  return { motivo: null, detalhe: null, resultado: refeito.resultado, terminouEm: u ? entregues[u.k]!.hora : d.comecou_em };
}

/* ------------------------------------------------ as rotas */
const objeto = (x: unknown): x is Record<string, unknown> => typeof x === "object" && x !== null && !Array.isArray(x);
function campos(d: unknown, nomes: readonly string[], o: string): Record<string, unknown> {
  if (!objeto(d)) throw new Malformado(`${o} é um objeto {${nomes.join(", ")}}`);
  const extra = Object.keys(d).filter(k => !nomes.includes(k));
  if (extra.length) throw new Malformado(`campo desconhecido em ${o}: ${extra.join(", ")}`);
  return d;
}
const lerDia = (x: unknown): string => {
  if (typeof x !== "string" || !diaValido(x)) throw new Malformado("'dia' é AAAA-MM-DD");
  return x;
};

export function montarRotasDesafio(app: Hono, cfg: ConfigConta, g: GuardasConta): void {
  const { banco, agora, marcoRanqueada } = cfg;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });
  const recusar = (c: Context, codigo: number, motivo: MotivoDesafio, erro: string, extra: Record<string, unknown> = {}) => json(c, codigo, { motivo, erro, ...extra });
  const limite = bodyLimit({ maxSize: LIMITE_DESAFIO, onError: c => json(c, 413, { erro: `pedido grande demais (o limite é ${LIMITE_DESAFIO} bytes)` }) });
  /** o corpo JSON (ou a resposta do erro) */
  async function corpo(c: Context): Promise<unknown | Response> {
    if (!(c.req.header("content-type") ?? "").startsWith("application/json")) return json(c, 415, { erro: "o pedido é JSON" });
    try { return JSON.parse(await c.req.text()); } catch (err) { return json(c, 400, { erro: `pedido malformado: o corpo não é JSON: ${(err as Error).message}` }); }
  }
  /** a tentativa do dia que ainda aceita sementes e envios (ou a resposta da recusa) */
  function aberta(c: Context, contaId: string, dia: string, t: number): LinhaDesafio | Response {
    const d = desafioDe(banco, contaId, dia);
    if (!d) return recusar(c, 404, "sem_tentativa", `a conta não começou a tentativa do dia ${dia}`);
    if (congelaDia(dia) <= t) return recusar(c, 409, "dia_fechado", `o dia ${dia} congelou às ${iso(congelaDia(dia))}`);
    return d;
  }

  app.use("/desafio", g.cors);
  app.use("/desafio/*", g.cors);

  app.get("/desafio", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const t = agora();
    fecharDias(banco, t);
    const dia = diaDe(t), d = desafioDe(banco, s.conta_id, dia);
    const fechados = (banco.prepare("SELECT dia, publicado_em FROM segredos_dia WHERE publicado_em IS NOT NULL ORDER BY dia DESC LIMIT ?")
      .all(DIAS_LISTADOS) as { dia: string; publicado_em: number }[]).map(l => ({ dia: l.dia, publicado_em: iso(l.publicado_em) }));
    return json(c, 200, { dia, v: VERSAO_FABRICA_ATUAL, fecha_em: iso(fimDoDia(dia)), congela_em: iso(congelaDia(dia)),
      tentativa: d ? tentativaParaFora(banco, d) : null, fechados });
  });

  app.post("/desafio/tentativa", limite, async c => {
    const s = g.sessaoParaMudar(c);
    if (s instanceof Response) return s;
    const d = await corpo(c);
    if (d instanceof Response) return d;
    let v: number;
    try {
      const x = campos(d, ["v"], "o pedido");
      if (!Number.isSafeInteger(x.v)) throw new Malformado("'v' é a versão das regras da Fábrica do jogo");
      v = x.v as number;
    } catch (err) {
      if (err instanceof Malformado) return json(c, 400, { erro: `pedido malformado: ${err.message}` });
      throw err;
    }
    if (!VERSOES_FABRICA.includes(v) || v !== VERSAO_FABRICA_ATUAL)
      return recusar(c, 422, "versao_fabrica_desconhecida", `o servidor confere a Fábrica da versão ${VERSAO_FABRICA_ATUAL}, não ${v}: atualize o jogo`);
    const t = agora();
    fecharDias(banco, t);
    return transacao(banco, () => {
      if (!nivelAberto(banco, s.conta_id, marcoRanqueada))
        return recusar(c, 403, "nivel_insuficiente", `o desafio do dia abre no marco ${marcoRanqueada} do Tamer, num envio aceito desta conta`
          + (marcoRanqueada === MARCO_MEGA ? " (o primeiro Mega, conferido no registro do pet)" : ""), { marco: marcoRanqueada });
      const dia = diaDe(t);
      if (desafioDe(banco, s.conta_id, dia))
        return recusar(c, 409, "tentativa_usada", `a tentativa do dia ${dia} já começou (uma por dia de Brasília); a próxima abre às ${iso(fimDoDia(dia))}`,
          { reabre_em: iso(fimDoDia(dia)) });
      const segredo = segredoDoDia(banco, dia, t);
      banco.prepare("INSERT INTO desafios (conta_id, dia, comecou_em, versao) VALUES (?, ?, ?, ?)").run(s.conta_id, dia, t, v);
      return json(c, 201, { dia, semente_dia: sementeDoDia(segredo), v, comecou_em: iso(t), fecha_em: iso(fimDoDia(dia)), congela_em: iso(congelaDia(dia)) });
    });
  });

  app.post("/desafio/lutas", limite, async c => {
    const s = g.sessaoParaMudar(c);
    if (s instanceof Response) return s;
    const d = await corpo(c);
    if (d instanceof Response) return d;
    let dia: string, k: number, escolha: number, trocas: number[];
    try {
      const x = campos(d, ["dia", "k", "escolha", "trocas"], "o pedido");
      dia = lerDia(x.dia);
      if (!Number.isInteger(x.k) || (x.k as number) < 0) throw new Malformado("'k' é o índice da luta, de 0 em diante");
      k = x.k as number;
      /* a forma da escolha e das trocas é a do registro (as trocas antes da luta k: todas menores que k) */
      const r = lerRegistroDesafio({ v: VERSAO_FABRICA_ATUAL, escolha: x.escolha, lutas: [], trocas: x.trocas });
      escolha = r.escolha; trocas = r.trocas;
      if (trocas.some(j => j >= k)) throw new Malformado(`as trocas antes da luta ${k} são depois de vitórias de índice menor que ${k}`);
    } catch (err) {
      if (err instanceof Malformado || err instanceof RegistroMalformado) return json(c, 400, { erro: `pedido malformado: ${err.message}` });
      throw err;
    }
    const t = agora();
    fecharDias(banco, t);
    return transacao(banco, () => {
      const des = aberta(c, s.conta_id, dia, t);
      if (des instanceof Response) return des;
      const n = lutasDe(banco, s.conta_id, dia).length;
      if (k !== n) return recusar(c, 409, "fora_de_ordem", `a próxima semente desta tentativa é a da luta ${n}, não ${k} (o GET /desafio devolve as já entregues)`);
      if (n >= LUTAS_MAX_DO_DIA) return recusar(c, 409, "lutas_demais", `uma tentativa tem no máximo ${LUTAS_MAX_DO_DIA} lutas`);
      if (des.escolha !== null && escolha !== des.escolha) return recusar(c, 409, "escolha_diferente", `o alugado escolhido foi o ${des.escolha}`);
      /* as trocas prometidas não mudam: as de antes ficam, e só a troca depois da última luta (k - 1) pode entrar */
      const antes: number[] = JSON.parse(des.trocas);
      const mesmas = antes.every(j => trocas.includes(j)) && trocas.every(j => antes.includes(j) || j === k - 1);
      if (!mesmas) return recusar(c, 409, "trocas_diferentes", `as trocas já prometidas foram ${JSON.stringify(antes)}; só a troca depois da luta ${k - 1} pode entrar`);
      const semente = sementeDaLutaDoDia(segredoDoDia(banco, dia, t), s.conta_id, k);
      banco.prepare("INSERT INTO desafio_lutas (conta_id, dia, k, semente, hora, escolha, trocas) VALUES (?, ?, ?, ?, ?, ?, ?)")
        .run(s.conta_id, dia, k, semente, t, escolha, JSON.stringify(trocas));
      banco.prepare("UPDATE desafios SET escolha = ?, trocas = ? WHERE conta_id = ? AND dia = ?").run(escolha, JSON.stringify(trocas), s.conta_id, dia);
      return json(c, 201, { dia, k, semente, hora: iso(t) });
    });
  });

  app.post("/desafio/envios", limite, async c => {
    const s = g.sessaoParaMudar(c);
    if (s instanceof Response) return s;
    const d = await corpo(c);
    if (d instanceof Response) return d;
    let dia: string, r: RegistroDesafio;
    try {
      const x = campos(d, ["dia", "registro"], "o envio");
      dia = lerDia(x.dia);
      r = lerRegistroDesafio(x.registro);
    } catch (err) {
      if (err instanceof Malformado || err instanceof RegistroMalformado) return json(c, 400, { erro: `envio malformado: ${err.message}` });
      throw err;
    }
    const t = agora();
    fecharDias(banco, t);
    return transacao(banco, () => {
      const des = aberta(c, s.conta_id, dia, t);
      if (des instanceof Response) return des;
      const hash = createHash("sha256").update(JSON.stringify(r)).digest("hex");
      /* o mesmo registro de novo devolve a conferência guardada */
      const ja = banco.prepare("SELECT id, resultado, motivo, detalhe FROM desafio_envios WHERE conta_id = ? AND dia = ? AND hash_registro = ? ORDER BY recebido_em LIMIT 1")
        .get(s.conta_id, dia, hash) as { id: string; resultado: string; motivo: string | null; detalhe: string | null } | undefined;
      const resposta = (id: string, conf: { motivo: string | null; detalhe: string | null }) => {
        const atual = desafioDe(banco, s.conta_id, dia)!;
        if (conf.motivo !== null) return json(c, 422, { id, resultado: "recusado", motivo: conf.motivo, erro: conf.detalhe });
        return json(c, 200, { id, resultado: "aceito", tentativa: tentativaParaFora(banco, atual) });
      };
      if (ja) return resposta(ja.id, ja);
      const t0 = performance.now(), conf = conferirDesafio(banco, des, r), ms = performance.now() - t0, id = randomUUID();
      banco.prepare(`INSERT INTO desafio_envios (id, conta_id, dia, recebido_em, hash_registro, resultado, motivo, detalhe, vitorias, lutas, ms_conferencia)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(id, s.conta_id, dia, t, hash, conf.motivo === null ? "aceito" : "recusado", conf.motivo, conf.detalhe,
        conf.resultado?.vitorias ?? null, r.lutas.length, ms);
      /* o resultado é o do envio aceito com mais lutas (os registros aceitos são prefixos uns dos outros: mais lutas nunca dá menos vitórias) */
      if (conf.resultado && (des.lutas === null || conf.resultado.lutas > des.lutas)) {
        const x = conf.resultado;
        banco.prepare("UPDATE desafios SET vitorias = ?, series = ?, lutas = ?, acabou = ?, vida_ultima = ?, terminou_em = ?, envio_id = ? WHERE conta_id = ? AND dia = ?")
          .run(x.vitorias, x.series, x.lutas, x.acabou ? 1 : 0, x.vidaUltimaVitoria, conf.terminouEm, id, s.conta_id, dia);
      }
      return resposta(id, conf);
    });
  });

  app.get("/desafio/selos", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    fecharDias(banco, agora());
    const selos = banco.prepare("SELECT dia, posicao, vitorias FROM tabelas_dia WHERE conta_id = ? AND selo = 1 ORDER BY dia DESC").all(s.conta_id);
    return json(c, 200, { total: selos.length, selos });
  });

  app.get("/desafio/:dia/tabela", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const dia = c.req.param("dia");
    if (!diaValido(dia)) return json(c, 400, { erro: "o dia é AAAA-MM-DD" });
    fecharDias(banco, agora());
    const fechado = typeof publicadoEm(banco, dia) === "number";
    type Linha = LinhaTabelaDia & { posicao: number; selo: boolean };
    let linhas: Linha[];
    if (fechado) {
      linhas = (banco.prepare(`SELECT t.posicao, t.conta_id, c.apelido, t.vitorias, t.vida_ultima, t.terminou_em, t.selo FROM tabelas_dia t JOIN contas c ON c.id = t.conta_id
        WHERE t.dia = ? ORDER BY t.posicao`).all(dia) as unknown as { posicao: number; conta_id: string; apelido: string; vitorias: number; vida_ultima: number; terminou_em: number; selo: number }[])
        .map(l => ({ posicao: l.posicao, contaId: l.conta_id, apelido: l.apelido, vitorias: l.vitorias, vidaUltimaVitoria: l.vida_ultima, terminouEm: l.terminou_em, selo: l.selo === 1 }));
    } else {
      const tabela = tabelaDoDia(banco, dia), selo = comSelo(tabela);
      linhas = tabela.map((l, i) => ({ ...l, posicao: i + 1, selo: selo[i]! }));
    }
    return json(c, 200, { dia, estado: fechado ? "fechado" : "aberto", congela_em: iso(congelaDia(dia)), total: linhas.length,
      linhas: linhas.map(l => ({ posicao: l.posicao, apelido: l.apelido, vitorias: l.vitorias, vida_ultima_vitoria: l.vidaUltimaVitoria,
        terminou_em: iso(l.terminouEm), selo: l.selo, voce: l.contaId === s.conta_id })).filter((l, i) => i < LINHAS_DA_TABELA_DO_DIA || l.voce) });
  });

  app.get("/desafio/:dia/segredo", c => {
    const dia = c.req.param("dia");
    if (!diaValido(dia)) return json(c, 400, { erro: "o dia é AAAA-MM-DD" });
    fecharDias(banco, agora());
    const l = banco.prepare("SELECT segredo, publicado_em FROM segredos_dia WHERE dia = ?").get(dia) as { segredo: string; publicado_em: number | null } | undefined;
    if (!l) return json(c, 404, { motivo: "sem_segredo", erro: "ninguém começou o desafio neste dia" });
    if (l.publicado_em === null) return json(c, 404, { motivo: "dia_aberto", erro: "o segredo sai quando o dia congela", congela_em: iso(congelaDia(dia)) });
    return json(c, 200, { dia, segredo: l.segredo, publicado_em: iso(l.publicado_em),
      como: `a semente do dia = os 4 primeiros bytes (inteiro sem sinal, big-endian) de HMAC-SHA256(segredo em bytes, "${ROTULO_SEMENTE_DIA}"); a da luta k = os de HMAC-SHA256(segredo, "<id da conta>|<k>")` });
  });
}
