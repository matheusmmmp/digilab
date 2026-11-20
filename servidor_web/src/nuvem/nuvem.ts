/* O save na nuvem (CN3; docs/PLANO_V3_CONTA.md, seção 5; CN-3, CN-4 e CN-5). Só com a sessão da conta (CN2); o que muda algo pede o
   X-CSRF-Token da sessão, como o envio (MMO3). O protocolo está em web/app/src/nuvem/protocolo.ts.

     GET  /nuvem                       o estado: o pet da nuvem (o resumo), a vez, a divergência pendente e as cópias
     POST /nuvem/levar                 {protocolo, escolha, pacote}: levar o pet para a conta (a tela 3; UX-NV-1 e UX-NV-2)
     POST /nuvem/vez                   {jogar_aqui?}: pede a vez; com jogar_aqui, toma a vez do outro aparelho (5.2)
     POST /nuvem/sync                  PedidoSync -> RespostaSync: os eventos novos, ou o que falta a este aparelho (5.1)
     POST /nuvem/divergencia           {id, fica: "nuvem"|"outra"}: a escolha da história (5.3); a outra vai para Gerações
     GET  /nuvem/pacote                o pacote inteiro da nuvem (para abrir o pet num aparelho que escolheu "os da nuvem")
     GET  /nuvem/historias             as histórias não escolhidas (Gerações, só para ver); /nuvem/historias/:id, o save de uma
     GET  /nuvem/copias                as cópias de 30 dias; POST /nuvem/copias/:id/restaurar (5.6)

   As regras:
     - O PACOTE é um por conta, como no aparelho: o save do pet do jogador e as outras chaves da CN0 (D-CONTA-180). "A vez por pet" é a
       vez deste pacote. Trocar o pet ativo (um ovo novo, um pet guardado) manda o save inteiro, e o de antes vai para as cópias.
     - A VEZ: um aparelho só escreve com a vez, ou com a vez livre (expirada ou de ninguém). Ela se renova a cada pedido de quem a tem e
       expira em VEZ_EXPIRA_MS sem sinal. "Jogar aqui" toma a vez.
     - OS EVENTOS só se juntam quando a base do aparelho é a ponta da nuvem (o mesmo pet, o mesmo número de eventos e o mesmo hash). O
       servidor refaz o registro inteiro depois de juntar (CN-4: o replay na sincronização) e recusa o que não reproduz (422).
     - A DIVERGÊNCIA: o aparelho com eventos novos que não continuam a ponta da nuvem (a vez de outro, ou a base para trás) cria duas
       histórias. Nada se junta e nada se apaga: a dele fica guardada inteira até a escolha, e o pet fica só para ver nos dois aparelhos
       (UX-NV-4). A escolhida vira a da nuvem; a outra vai para Gerações (nuvem_historias) e para as cópias. Um pedido com eventos novos
       durante a escolha pendente vira uma cópia ("durante_divergencia"): nem ele se perde.
     - AS CÓPIAS: a diária (a primeira escrita de cada dia de Brasília) e as do que sai do lugar (o não escolhido, a troca, o de antes de
       restaurar, a história não escolhida), todas por COPIAS_DIAS. A limpeza roda a cada pedido. Restaurar põe a cópia no lugar e o de
       agora vira uma cópia. */
import { randomUUID } from "node:crypto";
import type { Context, Hono } from "hono";
import { bodyLimit } from "hono/body-limit";
import { GrupoDoJogo, Motor, VERSOES_PET, nomeForma, type EventoGrupoJogo, type EventoRegistro } from "../../../web/app/motor/index.ts";
import { FUSO_BRASILIA_MS } from "../../../web/app/src/ranking/pontos.ts";
import {
  COPIAS_DIAS, PROTOCOLO_NUVEM, VEZ_EXPIRA_MS, ehChaveNuvem, ehComeco, pontaFirme, idDoSave, textoExtras, type Base, type DivergenciaVista, type LadoHistoria,
  type Pacote, type PedidoSync, type RespostaSync, type SaveNuvem, type VezVista,
} from "../../../web/app/src/nuvem/protocolo.ts";
import { transacao, type Banco } from "../conta/banco.ts";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta, Sessao } from "../conta/rotas.ts";
import { hashesAte, hashRegistro } from "../envio/conferir.ts";

/** o corpo de um pedido da nuvem, em bytes (PROPOSTO, SEM FONTE): o mesmo do envio; o pior save da CN0 tem ~3 MB cru, mais as outras chaves */
export const LIMITE_NUVEM = 5 * 1024 * 1024;
const DIA_MS = 86_400_000;

export class PacoteMalformado extends Error {}
export class NaoReproduz extends Error {}
class Recusa extends Error {
  readonly codigo: number; readonly corpo: object;
  constructor(codigo: number, corpo: object) { super(JSON.stringify(corpo)); this.codigo = codigo; this.corpo = corpo; }
}

const objeto = (x: unknown): x is Record<string, unknown> => typeof x === "object" && x !== null && !Array.isArray(x);
const msg = (err: unknown): string => err instanceof Error ? err.message : String(err);
/** o dia de Brasília de uma hora do servidor (a cópia diária) */
export const diaDe = (hora: number): string => new Date(hora + FUSO_BRASILIA_MS).toISOString().slice(0, 10);

/** confere a forma de um save (não o conteúdo: o replay confere) */
export function lerSaveNuvem(d: unknown): SaveNuvem {
  if (!objeto(d)) throw new PacoteMalformado("o save é um objeto {semente, log, versao}");
  if (!Number.isSafeInteger(d.semente)) throw new PacoteMalformado("'semente' é um inteiro");
  if (!Number.isSafeInteger(d.versao)) throw new PacoteMalformado("'versao' é um inteiro");
  if (!Array.isArray(d.log) || !d.log.every(Array.isArray)) throw new PacoteMalformado("'log' é uma lista de eventos");
  if (d.grupo !== undefined && d.grupo !== true) throw new PacoteMalformado("'grupo' é true ou não vem");
  if (d.grupo === true && typeof d.foco !== "string") throw new PacoteMalformado("o save dos dois pets leva o 'foco'");
  const extra = Object.keys(d).filter(k => !["semente", "log", "versao", "grupo", "foco"].includes(k));
  if (extra.length) throw new PacoteMalformado(`campo desconhecido no save: ${extra.join(", ")}`);
  const s: SaveNuvem = { semente: d.semente as number, log: d.log as unknown[][], versao: d.versao as number };
  if (d.grupo === true) { s.grupo = true; s.foco = d.foco as string; }
  return s;
}
/** as outras chaves: só as da CN0, cada uma um texto */
export function lerExtras(d: unknown): Record<string, string> {
  if (!objeto(d)) throw new PacoteMalformado("'extras' é um objeto {chave: texto}");
  for (const [k, v] of Object.entries(d)) {
    if (!ehChaveNuvem(k)) throw new PacoteMalformado(`chave que não sobe para a nuvem: ${k}`);
    if (typeof v !== "string") throw new PacoteMalformado(`o valor de ${k} é um texto`);
  }
  return d as Record<string, string>;
}
export function lerPacote(d: unknown): Pacote {
  if (!objeto(d)) throw new PacoteMalformado("o pacote é um objeto {save, extras}");
  return { save: lerSaveNuvem(d.save), extras: lerExtras(d.extras ?? {}) };
}

/** refaz o save (CN-4) e devolve o resumo: a forma e o tick do pet (o do foco, nos dois pets). O que não reproduz levanta NaoReproduz;
    a versão que o servidor não abre também (o pet de teste do laboratório não sobe) */
export function refazer(s: SaveNuvem): { forma: string; tick: number } {
  if (!VERSOES_PET.includes(s.versao)) throw new NaoReproduz(`versão de pet desconhecida: ${s.versao}`);
  try {
    const m = s.grupo
      ? GrupoDoJogo.reproduzir(s.semente, s.versao, s.log as EventoGrupoJogo[]).motor(s.foco!)
      : Motor.reproduzir(s.semente, s.log as EventoRegistro[], s.versao);
    return { forma: nomeForma(m.forma), tick: m.e.tick };
  } catch (err) { throw new NaoReproduz(msg(err)); }
}

interface LinhaPet {
  conta_id: string; semente: number; versao: number; grupo: number; foco: string | null; log: string; eventos: number; hash: string;
  firme: number; hash_firme: string; extras: string; extras_hash: string; forma: string; tick: number; atualizado_em: number; atualizado_por: string | null;
  vez_aparelho: string | null; vez_desde: number | null; vez_ate: number | null;
}
interface LinhaDiv { id: string; conta_id: string; criada_em: number; aparelho_nome: string; save: string; extras: string; comum: number; lados: string }

const saveDaLinha = (l: LinhaPet): SaveNuvem => {
  const s: SaveNuvem = { semente: l.semente, log: JSON.parse(l.log) as unknown[][], versao: l.versao };
  if (l.grupo) { s.grupo = true; s.foco = l.foco!; }
  return s;
};
/** a posição que a nuvem confirma: a ponta firme do registro (sem o "t" do fim, que ainda cresce) e o hash até ali */
const baseDaLinha = (l: LinhaPet): Base => ({ id: idDoSave({ semente: l.semente, versao: l.versao, grupo: l.grupo ? true : undefined }), eventos: l.firme, hash: l.hash_firme });
const hashExtras = (x: Record<string, string>): string => hashRegistro(JSON.parse(textoExtras(x)));
/** a última ação do registro, para a tela "Duas histórias" ("o último: carinho"): o último evento que não é o tempo */
function ultimaAcao(log: readonly unknown[][]): string | null {
  for (let i = log.length - 1; i >= 0; i--) { const e = log[i]!; if (e[1] !== "t") return typeof e[2] === "string" ? e[2] : String(e[1]); }
  return null;
}

/** quantos eventos do começo os dois registros têm em comum */
export function comecoComum(a: readonly unknown[], b: readonly unknown[]): number {
  const n = Math.min(a.length, b.length);
  let i = 0;
  while (i < n && JSON.stringify(a[i]) === JSON.stringify(b[i])) i++;
  return i;
}

export function montarRotasNuvem(app: Hono, cfg: ConfigConta, g: GuardasConta): void {
  const { banco, agora } = cfg;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });
  app.use("/nuvem", g.cors);
  app.use("/nuvem/*", g.cors);

  const nomeAparelho = (id: string | null): string | null =>
    id === null ? null : ((banco.prepare("SELECT nome FROM aparelhos WHERE id = ?").get(id) as { nome: string } | undefined)?.nome ?? null);
  const linhaDe = (conta: string) => banco.prepare("SELECT * FROM nuvem_pets WHERE conta_id = ?").get(conta) as LinhaPet | undefined;
  const pendenteDe = (conta: string) =>
    banco.prepare("SELECT * FROM nuvem_divergencias WHERE conta_id = ? AND resolvida_em IS NULL ORDER BY criada_em LIMIT 1").get(conta) as LinhaDiv | undefined;
  const limpar = (t: number) => banco.prepare("DELETE FROM nuvem_copias WHERE apagar_em <= ?").run(t);

  const vezVista = (l: LinhaPet | undefined, s: Sessao, t: number): VezVista => {
    if (!l || l.vez_aparelho === null || (l.vez_ate ?? 0) <= t) return { minha: false, aparelho: null, desde: null, ate: null };
    return { minha: l.vez_aparelho === s.aparelho_id, aparelho: nomeAparelho(l.vez_aparelho), desde: l.vez_desde, ate: l.vez_ate };
  };
  const darVez = (conta: string, s: Sessao, t: number, l?: LinhaPet) => {
    const desde = l && l.vez_aparelho === s.aparelho_id && (l.vez_ate ?? 0) > t ? l.vez_desde : t;
    banco.prepare("UPDATE nuvem_pets SET vez_aparelho = ?, vez_desde = ?, vez_ate = ? WHERE conta_id = ?").run(s.aparelho_id, desde, t + VEZ_EXPIRA_MS, conta);
  };
  const divergenciaVista = (d: LinhaDiv | undefined): DivergenciaVista | null => {
    if (!d) return null;
    const lados = JSON.parse(d.lados) as { nuvem: LadoHistoria; outra: LadoHistoria };
    return { id: d.id, criada_em: d.criada_em, ...lados };
  };
  const copiar = (conta: string, t: number, motivo: string, save: SaveNuvem, extras: Record<string, string>, resumo: { forma: string; tick: number }) => {
    banco.prepare("INSERT INTO nuvem_copias (id, conta_id, feita_em, dia, motivo, save, extras, eventos, forma, tick, apagar_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
      .run(randomUUID(), conta, t, diaDe(t), motivo, JSON.stringify(save), JSON.stringify(extras), save.log.length, resumo.forma, resumo.tick, t + COPIAS_DIAS * DIA_MS);
  };
  const copiarLinha = (l: LinhaPet, t: number, motivo: string) =>
    copiar(l.conta_id, t, motivo, saveDaLinha(l), JSON.parse(l.extras) as Record<string, string>, l);
  /** grava o pacote como o da nuvem (e a cópia diária, se é a primeira escrita do dia) */
  const gravar = (conta: string, s: Sessao, t: number, save: SaveNuvem, extras: Record<string, string>, resumo: { forma: string; tick: number }) => {
    const firme = pontaFirme(save.log);
    const v = [save.semente, save.versao, save.grupo ? 1 : 0, save.foco ?? null, JSON.stringify(save.log), save.log.length, hashRegistro(save.log),
      firme, hashRegistro(save.log.slice(0, firme)), JSON.stringify(extras), hashExtras(extras), resumo.forma, resumo.tick, t, s.aparelho_id];
    if (linhaDe(conta)) banco.prepare(`UPDATE nuvem_pets SET semente = ?, versao = ?, grupo = ?, foco = ?, log = ?, eventos = ?, hash = ?, firme = ?, hash_firme = ?, extras = ?, extras_hash = ?,
      forma = ?, tick = ?, atualizado_em = ?, atualizado_por = ? WHERE conta_id = ?`).run(...v, conta);
    else banco.prepare(`INSERT INTO nuvem_pets (semente, versao, grupo, foco, log, eventos, hash, firme, hash_firme, extras, extras_hash, forma, tick, atualizado_em, atualizado_por, conta_id)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(...v, conta);
    const dia = banco.prepare("SELECT 1 FROM nuvem_copias WHERE conta_id = ? AND motivo = 'diaria' AND dia = ?").get(conta, diaDe(t));
    if (!dia) copiar(conta, t, "diaria", save, extras, resumo);
  };
  const resposta = (situacao: RespostaSync["situacao"], l: LinhaPet | undefined, s: Sessao, t: number, extra: Partial<RespostaSync> = {}): RespostaSync => ({
    situacao, base: l ? baseDaLinha(l) : null, foco: l?.foco ?? null, vez: vezVista(l, s, t), extras_hash: l?.extras_hash ?? null,
    divergencia: l ? divergenciaVista(pendenteDe(l.conta_id)) : null, ...(l ? { forma: l.forma, tick: l.tick, versao: l.versao } : {}), ...extra,
  });

  /* a sessão e o CSRF antes de ler o corpo; o corpo é JSON até LIMITE_NUVEM */
  const mudar = [
    async (c: Context, next: () => Promise<void>) => {
      const s = g.sessaoParaMudar(c);
      if (s instanceof Response) return s;
      c.set("sessaoNuvem" as never, s as never);
      await next();
    },
    bodyLimit({ maxSize: LIMITE_NUVEM, onError: c => json(c, 413, { erro: `pedido grande demais (o limite é ${LIMITE_NUVEM} bytes)` }) }),
  ] as const;
  const corpo = async (c: Context): Promise<Record<string, unknown>> => {
    if (!(c.req.header("content-type") ?? "").startsWith("application/json")) throw new Recusa(415, { erro: "o pedido é JSON" });
    let d: unknown;
    try { d = JSON.parse(await c.req.text()); } catch (err) { throw new Recusa(400, { erro: `o corpo não é JSON: ${msg(err)}` }); }
    if (!objeto(d)) throw new Recusa(400, { erro: "o corpo é um objeto" });
    if (d.protocolo !== undefined && d.protocolo !== PROTOCOLO_NUVEM) throw new Recusa(426, { situacao: "atualize", detalhe: `protocolo ${String(d.protocolo)}; o servidor fala o ${PROTOCOLO_NUVEM}` });
    return d;
  };
  /** roda a rota: as recusas viram a resposta delas; o pacote malformado, 400; o que não reproduz, 422 */
  const rodar = (f: (c: Context, s: Sessao) => Promise<Response>) => async (c: Context) => {
    const s = c.get("sessaoNuvem" as never) as unknown as Sessao;
    try { return await f(c, s); } catch (err) {
      if (err instanceof Recusa) return json(c, err.codigo, err.corpo);
      if (err instanceof PacoteMalformado) return json(c, 400, { erro: `pedido malformado: ${err.message}` });
      if (err instanceof NaoReproduz) return json(c, 422, { erro: "o registro não reproduz", detalhe: err.message });
      throw err;
    }
  };
  /** a versão que o servidor não abre é "atualize o jogo" (5.5), antes do replay */
  const exigirVersao = (s: SaveNuvem) => {
    if (!VERSOES_PET.includes(s.versao)) throw new Recusa(426, { situacao: "atualize", detalhe: `o pet é da versão ${s.versao}, que este servidor não abre` });
  };

  app.get("/nuvem", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const t = agora();
    limpar(t);
    const l = linhaDe(s.conta_id);
    const guardados = l ? contarLista(l.extras) : 0;
    const copias = (banco.prepare("SELECT count(*) AS n FROM nuvem_copias WHERE conta_id = ?").get(s.conta_id) as { n: number }).n;
    return json(c, 200, { ...resposta(l ? "ok" : "sem_pet", l, s, t), guardados, copias, atualizado_em: l?.atualizado_em ?? null, atualizado_por: nomeAparelho(l?.atualizado_por ?? null) });
  });

  app.get("/nuvem/pacote", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const l = linhaDe(s.conta_id);
    if (!l) return json(c, 404, { situacao: "sem_pet" });
    return json(c, 200, { ...resposta("ok", l, s, agora()), pacote: { save: saveDaLinha(l), extras: JSON.parse(l.extras) } });
  });

  /* a tela 3: levar o pet para a conta. A conta sem pet: "levar". A conta com pet: "aparelho" (os deste aparelho ficam; os da nuvem vão
     para as cópias), "nuvem" (os da nuvem ficam; os deste aparelho vão para as cópias) ou "os_dois" (o jogo já juntou os dois no pacote:
     o pet deste aparelho segue ativo e o da nuvem entra nos guardados; o pacote da nuvem de antes vai para as cópias, inteiro, porque o
     Tamer e Gerações dele não se juntam) */
  app.post("/nuvem/levar", ...mudar, rodar(async (c, s) => {
    const d = await corpo(c), t = agora(), escolha = d.escolha;
    if (!["levar", "aparelho", "nuvem", "os_dois"].includes(escolha as string)) throw new Recusa(400, { erro: "escolha: levar, aparelho, nuvem ou os_dois" });
    const p = lerPacote(d.pacote);
    exigirVersao(p.save);
    const resumo = refazer(p.save);
    const r = transacao(banco, () => {
      limpar(t);
      const l = linhaDe(s.conta_id);
      if (pendenteDe(s.conta_id)) throw new Recusa(409, resposta("divergiu", l, s, t));
      if (!l) {
        if (escolha !== "levar") throw new Recusa(409, { ...resposta("sem_pet", l, s, t), erro: "a conta ainda não tem pet: a escolha é levar" });
        gravar(s.conta_id, s, t, p.save, p.extras, resumo);
      } else if (escolha === "levar") {
        throw new Recusa(409, { ...resposta("ok", l, s, t), erro: "a conta já tem pet: escolha aparelho, nuvem ou os_dois", ja_tem: true, guardados: contarLista(l.extras) });
      } else if (escolha === "nuvem") {
        copiar(s.conta_id, t, "nao_escolhido", p.save, p.extras, resumo);
      } else {
        copiarLinha(l, t, "nao_escolhido");
        gravar(s.conta_id, s, t, p.save, p.extras, resumo);
      }
      /* a vez: quem levou o pet a tem; "os da nuvem" só a pega livre (o aparelho que a tem continua jogando) */
      const n = linhaDe(s.conta_id)!, v = vezVista(n, s, t);
      if (escolha !== "nuvem" || v.minha || v.aparelho === null) darVez(s.conta_id, s, t, n);
      return resposta("ok", linhaDe(s.conta_id), s, t);
    });
    return json(c, escolha === "levar" ? 201 : 200, r);
  }));

  app.post("/nuvem/vez", ...mudar, rodar(async (c, s) => {
    const d = await corpo(c), t = agora();
    return json(c, ...transacao(banco, (): [number, RespostaSync] => {
      const l = linhaDe(s.conta_id);
      if (!l) return [404, resposta("sem_pet", l, s, t)];
      if (pendenteDe(s.conta_id)) return [409, resposta("divergiu", l, s, t)];
      const v = vezVista(l, s, t);
      if (v.aparelho !== null && !v.minha && d.jogar_aqui !== true) return [409, resposta("outro", l, s, t)];
      darVez(s.conta_id, s, t, l);
      return [200, resposta("ok", linhaDe(s.conta_id), s, t)];
    }));
  }));

  app.post("/nuvem/sync", ...mudar, rodar(async (c, s) => {
    const d = await corpo(c), t = agora();
    if (d.protocolo !== PROTOCOLO_NUVEM) throw new Recusa(426, { situacao: "atualize", detalhe: "o pedido não diz o protocolo" });
    const p = lerPedido(d);
    if (p.completo) exigirVersao(p.completo);
    return json(c, 200, transacao(banco, () => sincronizar(s, t, p)));
  }));

  /** o coração da sincronização (5.1 a 5.3), numa transação */
  function sincronizar(s: Sessao, t: number, p: PedidoSync): RespostaSync {
    limpar(t);
    const l = linhaDe(s.conta_id);
    if (!l) return resposta("sem_pet", l, s, t);
    const base = baseDaLinha(l), nuvem = saveDaLinha(l), extrasNuvem = JSON.parse(l.extras) as Record<string, string>;
    const extrasMudaram = p.extras !== undefined && hashExtras(p.extras) !== l.extras_hash;
    /* a base deste aparelho é um começo do registro da nuvem: o mesmo pet, e o hash até ali bate (a ponta firme não muda) */
    const comeco = p.base !== null && p.base.id === base.id && p.base.eventos <= l.eventos
      && hashesAte(nuvem.log, [p.base.eventos]).get(p.base.eventos) === p.base.hash;
    /* o registro deste aparelho: o completo, ou a base mais os novos; null se não dá para montar (a base não é um começo da nuvem) */
    const doAparelho = salvoDoAparelho(p, nuvem, comeco);
    const mesmoPet = doAparelho !== null && idDoSave(doAparelho) === base.id;
    const de = comeco ? p.base!.eventos : 0;
    /* atrás: o que este aparelho tem a nuvem já tem; à frente: o registro dele continua o da nuvem (o "t" do fim pode ter crescido) */
    const atras = mesmoPet && ehComeco(doAparelho.log, nuvem.log, de);
    const afrente = mesmoPet && ehComeco(nuvem.log, doAparelho.log, de);
    const logNovo = doAparelho !== null && !atras;
    const focoMudou = mesmoPet && nuvem.grupo === true && doAparelho.foco !== undefined && doAparelho.foco !== l.foco && afrente;
    const temNovo = logNovo || extrasMudaram || focoMudou;
    /* o que falta a este aparelho: os eventos depois da base, ou o save inteiro; e as outras chaves, se o hash dele não bate */
    const emDia = atras && afrente && p.extras_hash === l.extras_hash;
    const oQueFalta = (): Partial<RespostaSync> => ({
      ...(comeco ? { novos: nuvem.log.slice(p.base!.eventos) } : { completo: nuvem }),
      ...(p.extras_hash !== l.extras_hash ? { extras: extrasNuvem } : {}),
    });

    const pendente = pendenteDe(s.conta_id);
    if (pendente) {
      /* a escolha está pendente: nada se junta; o que este aparelho fez nesse meio-tempo vira uma cópia, para não se perder (a não ser
         que seja a mesma história já guardada na divergência) */
      if (logNovo && doAparelho && !jaGuardada(pendente, doAparelho))
        copiar(s.conta_id, t, "durante_divergencia", doAparelho, p.extras ?? extrasNuvem, refazer(doAparelho));
      return resposta("divergiu", l, s, t);
    }
    const v = vezVista(l, s, t), podeEscrever = v.minha || v.aparelho === null;
    if (!temNovo) {
      if (v.minha) darVez(s.conta_id, s, t, l);
      const sit = v.aparelho !== null && !v.minha ? "outro" : emDia ? "ok" : "atras";
      return resposta(sit, linhaDe(s.conta_id), s, t, emDia ? {} : oQueFalta());
    }
    const extras = p.extras ?? extrasNuvem;
    if (podeEscrever && doAparelho) {
      /* o registro deste aparelho continua o da nuvem: entra no lugar, refeito inteiro (CN-4). O pet trocado (o save inteiro de outro pet,
         com a base na ponta firme da nuvem) entra no lugar, e o de antes vai para as cópias */
      const troca = !mesmoPet && comeco && p.base!.eventos === base.eventos;
      if ((mesmoPet && afrente) || troca) {
        const resumo = refazer(doAparelho);
        if (troca) copiarLinha(l, t, "troca");
        gravar(s.conta_id, s, t, doAparelho, extras, resumo);
        darVez(s.conta_id, s, t, linhaDe(s.conta_id));
        return resposta("ok", linhaDe(s.conta_id), s, t);
      }
    }
    if (!logNovo) {
      /* o registro está em dia; mudaram só as outras chaves (ou o foco). Com a vez, sobem; sem ela, não: o aparelho recebe o da nuvem */
      if (!podeEscrever) return resposta("outro", l, s, t, oQueFalta());
      const save = focoMudou ? { ...nuvem, foco: doAparelho!.foco } : nuvem;
      gravar(s.conta_id, s, t, save, extras, l);
      darVez(s.conta_id, s, t, linhaDe(s.conta_id));
      return resposta("ok", linhaDe(s.conta_id), s, t, afrente ? {} : { novos: nuvem.log.slice(de) });
    }
    /* duas histórias: o registro deste aparelho não continua o da nuvem (a vez é de outro, ou a nuvem andou). Sem o registro inteiro, o
       servidor pede (o aparelho manda de novo com o completo) */
    if (!doAparelho) return resposta("atras", l, s, t, { completo: nuvem, detalhe: "mande o save inteiro (completo)" });
    const comum = comecoComum(nuvem.log, doAparelho.log);
    /* o que este aparelho tem a mais é só o tempo andando (nenhuma ação: o aparelho que perdeu a vez anda até saber, no máximo uma
       sincronização). Não é uma história: o aparelho recebe a da nuvem. "O que ele já enviou fica" (a prancha, quadro 4; D-CONTA-183) */
    if (mesmoPet && doAparelho.log.slice(comum).every(e => e[1] === "t"))
      return resposta(v.aparelho !== null && !v.minha ? "outro" : "atras", l, s, t, oQueFalta());
    const resumo = refazer(doAparelho);
    const lado = (sv: SaveNuvem, r: { forma: string; tick: number }, aparelho: string): LadoHistoria =>
      ({ aparelho, tick: r.tick, forma: r.forma, eventos_novos: sv.log.length - comum, ultimo: ultimaAcao(sv.log) });
    const meu = nomeAparelho(s.aparelho_id) ?? "aparelho";
    const lados = { nuvem: lado(nuvem, l, nomeAparelho(l.atualizado_por) ?? "nuvem"), outra: lado(doAparelho, resumo, meu) };
    banco.prepare("INSERT INTO nuvem_divergencias (id, conta_id, criada_em, aparelho_nome, save, extras, comum, lados) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
      .run(randomUUID(), s.conta_id, t, meu, JSON.stringify(doAparelho), JSON.stringify(extras), comum, JSON.stringify(lados));
    return resposta("divergiu", l, s, t);
  }
  /** o save inteiro deste aparelho: o completo, ou a base (um começo da nuvem) mais os novos; null se não dá para montar */
  function salvoDoAparelho(p: PedidoSync, nuvem: SaveNuvem, comeco: boolean): SaveNuvem | null {
    if (p.completo) return p.completo;
    if (!comeco) return null;
    const s: SaveNuvem = { ...nuvem, log: [...nuvem.log.slice(0, p.base!.eventos), ...p.novos] };
    if (p.foco !== undefined && s.grupo) s.foco = p.foco;
    return s;
  }
  /** a história deste aparelho já está guardada na divergência (ele mandou de novo, ou só o tempo andou nela): não vira cópia outra vez */
  function jaGuardada(d: LinhaDiv, sv: SaveNuvem): boolean {
    const outra = JSON.parse(d.save) as SaveNuvem;
    return idDoSave(outra) === idDoSave(sv) && ehComeco(sv.log, outra.log);
  }

  app.post("/nuvem/divergencia", ...mudar, rodar(async (c, s) => {
    const d = await corpo(c), t = agora();
    if (d.fica !== "nuvem" && d.fica !== "outra") throw new Recusa(400, { erro: "fica: nuvem ou outra" });
    return json(c, 200, transacao(banco, () => {
      const pendente = pendenteDe(s.conta_id), l = linhaDe(s.conta_id);
      if (!pendente || !l || pendente.id !== d.id) throw new Recusa(409, { ...resposta("ok", l, s, t), erro: "essa divergência não está pendente" });
      const outra = JSON.parse(pendente.save) as SaveNuvem, extrasOutra = JSON.parse(pendente.extras) as Record<string, string>;
      const lados = JSON.parse(pendente.lados) as { nuvem: LadoHistoria; outra: LadoHistoria };
      /* a que não ficou vai para Gerações (só para ver) e para as cópias */
      const [perde, extrasPerde, resumoPerde, nome] = d.fica === "nuvem"
        ? [outra, extrasOutra, lados.outra, pendente.aparelho_nome]
        : [saveDaLinha(l), JSON.parse(l.extras) as Record<string, string>, l as { forma: string; tick: number }, lados.nuvem.aparelho];
      banco.prepare("INSERT INTO nuvem_historias (id, conta_id, criada_em, aparelho_nome, divergencia_id, save, extras, eventos, forma, tick) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        .run(randomUUID(), s.conta_id, t, nome, pendente.id, JSON.stringify(perde), JSON.stringify(extrasPerde), perde.log.length, resumoPerde.forma, resumoPerde.tick);
      copiar(s.conta_id, t, "historia", perde, extrasPerde, resumoPerde);
      if (d.fica === "outra") gravar(s.conta_id, s, t, outra, extrasOutra, refazer(outra));
      banco.prepare("UPDATE nuvem_divergencias SET resolvida_em = ?, fica = ? WHERE id = ?").run(t, String(d.fica), pendente.id);
      /* a vez fica livre: o primeiro aparelho que abrir o pet a pega */
      banco.prepare("UPDATE nuvem_pets SET vez_aparelho = NULL, vez_desde = NULL, vez_ate = NULL WHERE conta_id = ?").run(s.conta_id);
      return resposta("ok", linhaDe(s.conta_id), s, t);
    }));
  }));

  app.get("/nuvem/historias", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    return json(c, 200, banco.prepare("SELECT id, criada_em, aparelho_nome, eventos, forma, tick FROM nuvem_historias WHERE conta_id = ? ORDER BY criada_em DESC").all(s.conta_id));
  });
  app.get("/nuvem/historias/:id", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const h = banco.prepare("SELECT id, criada_em, aparelho_nome, save FROM nuvem_historias WHERE conta_id = ? AND id = ?").get(s.conta_id, c.req.param("id")) as
      { id: string; criada_em: number; aparelho_nome: string; save: string } | undefined;
    if (!h) return json(c, 404, { erro: "história desconhecida" });
    return json(c, 200, { ...h, save: JSON.parse(h.save) });
  });

  app.get("/nuvem/copias", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    limpar(agora());
    return json(c, 200, banco.prepare("SELECT id, feita_em, motivo, eventos, forma, tick, apagar_em FROM nuvem_copias WHERE conta_id = ? ORDER BY feita_em DESC, id").all(s.conta_id));
  });

  app.post("/nuvem/copias/:id/restaurar", ...mudar, rodar(async (c, s) => {
    const t = agora();
    return json(c, 200, transacao(banco, () => {
      limpar(t);
      const l = linhaDe(s.conta_id);
      if (pendenteDe(s.conta_id)) throw new Recusa(409, resposta("divergiu", l, s, t));
      const cp = banco.prepare("SELECT * FROM nuvem_copias WHERE conta_id = ? AND id = ?").get(s.conta_id, c.req.param("id") ?? "") as
        { save: string; extras: string } | undefined;
      if (!cp) throw new Recusa(404, { erro: "cópia desconhecida (ou já passou dos 30 dias)" });
      const save = JSON.parse(cp.save) as SaveNuvem, extras = JSON.parse(cp.extras) as Record<string, string>;
      /* o de agora vira uma cópia: nada se perde (5.6) */
      if (l) copiarLinha(l, t, "antes_de_restaurar");
      gravar(s.conta_id, s, t, save, extras, refazer(save));
      darVez(s.conta_id, s, t, linhaDe(s.conta_id));
      return resposta("ok", linhaDe(s.conta_id), s, t);
    }));
  }));
}

/** quantos guardados o pacote tem (o resumo da tela 3) */
function contarLista(extras: string): number {
  const x = JSON.parse(extras) as Record<string, string>, k = Object.keys(x).find(c => c.endsWith("-guardados"));
  if (!k) return 0;
  const g = JSON.parse(x[k]!) as unknown;
  return Array.isArray(g) ? g.length : 0;
}

/** confere a forma do pedido de sincronização */
export function lerPedido(d: Record<string, unknown>): PedidoSync {
  const base = d.base;
  let b: Base | null = null;
  if (base !== null) {
    if (!objeto(base) || typeof base.id !== "string" || !Number.isSafeInteger(base.eventos) || (base.eventos as number) < 0 || typeof base.hash !== "string")
      throw new PacoteMalformado("'base' é {id, eventos, hash} ou null");
    b = { id: base.id, eventos: base.eventos as number, hash: base.hash };
  }
  if (typeof d.id !== "string") throw new PacoteMalformado("'id' é o pet do save (semente:versao:grupo)");
  if (!Array.isArray(d.novos) || !d.novos.every(Array.isArray)) throw new PacoteMalformado("'novos' é uma lista de eventos");
  if (d.foco !== undefined && typeof d.foco !== "string") throw new PacoteMalformado("'foco' é um texto");
  if (d.extras_hash !== null && typeof d.extras_hash !== "string") throw new PacoteMalformado("'extras_hash' é um texto ou null");
  const p: PedidoSync = { protocolo: PROTOCOLO_NUVEM, base: b, id: d.id, novos: d.novos as unknown[][], extras_hash: d.extras_hash as string | null };
  if (d.foco !== undefined) p.foco = d.foco as string;
  if (d.completo !== undefined) {
    p.completo = lerSaveNuvem(d.completo);
    if (idDoSave(p.completo) !== p.id) throw new PacoteMalformado("o 'completo' é de outro pet que o 'id'");
  }
  if (d.extras !== undefined) p.extras = lerExtras(d.extras);
  const extra = Object.keys(d).filter(k => !["protocolo", "base", "id", "foco", "novos", "completo", "extras", "extras_hash"].includes(k));
  if (extra.length) throw new PacoteMalformado(`campo desconhecido no pedido: ${extra.join(", ")}`);
  return p;
}

/** o que a nuvem guarda da conta, para o "baixar os meus dados": o pet (sem o registro, que é do próprio jogador), as cópias, as histórias
    e as divergências, só as linhas */
export function nuvemDaConta(banco: Banco, conta: string): Record<string, unknown> {
  const pet = banco.prepare("SELECT semente, versao, grupo, eventos, hash, forma, tick, atualizado_em, vez_desde, vez_ate FROM nuvem_pets WHERE conta_id = ?").get(conta) ?? null;
  return {
    pet,
    copias: banco.prepare("SELECT id, feita_em, motivo, eventos, forma, tick, apagar_em FROM nuvem_copias WHERE conta_id = ? ORDER BY feita_em").all(conta),
    historias: banco.prepare("SELECT id, criada_em, aparelho_nome, eventos, forma, tick FROM nuvem_historias WHERE conta_id = ? ORDER BY criada_em").all(conta),
    divergencias: banco.prepare("SELECT id, criada_em, aparelho_nome, comum, resolvida_em, fica FROM nuvem_divergencias WHERE conta_id = ? ORDER BY criada_em").all(conta),
  };
}
