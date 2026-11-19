/* O envio dos logs (MMO3, docs/PLANO_V3_MMO.md seções 3 e 11; MMO-4 e MMO-5). Só com a sessão da conta (CN2):
     POST /envios        {pet: {semente, log, versao}, tamer: {versao, log}} -> 201 aceito | 200 o mesmo envio já conferido
                         | 422 recusado {motivo, detalhe} (hash_nao_confere: o registro mudou depois de um pedido de semente, MMO4) | 400 malformado | 401 sem sessão | 403 sem CSRF | 413 grande demais
     GET  /envios        os envios da conta, sem os registros: [{id, recebido_em, pet, versao_pet, eventos, hash_log, resultado, ...}]
   O POST pede o X-CSRF-Token da sessão (o mesmo das rotas da conta) e o corpo JSON até LIMITE_ENVIO.

   O que se guarda (MMO-4, seção 11; D-CONTA-78):
     - de todo envio conferido: o hash do registro do pet e do Tamer, a versão, o número de eventos, o resultado (aceito ou recusado, com o
       motivo), a situação do marco 10, os pontos e o tempo da conferência;
     - os dois registros, só do envio aceito, e só até 30 dias depois do fim da semana de Brasília do envio (LOG_DIAS_DEPOIS_DA_SEMANA,
       PROPOSTO, SEM FONTE): servem à conta da semana (as sementes da MMO4) e a uma contestação. Depois, sai o registro e fica a linha;
     - o envio recusado não guarda o registro (o jogador ainda o tem).
   As sementes ranqueadas (MMO4, sementes.ts): a conferência recebe as sementes entregues a este pet, e a linha guarda quantas foram e os
   marcos do Tamer (a trava do pedido). O mesmo envio de novo só devolve a conferência guardada se nenhuma semente nova foi entregue.
   Apagar a conta leva tudo: as duas tabelas pendem de contas(id) com ON DELETE CASCADE. */
import { randomUUID } from "node:crypto";
import type { Context, Hono } from "hono";
import { bodyLimit } from "hono/body-limit";
import { FUSO_BRASILIA_MS, semanaDe } from "../../../web/app/src/ranking/pontos.ts";
import { transacao, type Banco } from "../conta/banco.ts";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta } from "../conta/rotas.ts";
import { EnvioMalformado, hashRegistro, lerEnvio, type Conferencia } from "./conferir.ts";
import type { Conferidor } from "./conferidor.ts";
import { gravarFronteira } from "../premios/premios.ts";
import { gravarPontuacoes } from "../premios/rankings.ts";
import { fecharSemanas, gravarLutas } from "./semanas.ts";
import { entreguesDoPet } from "./sementes.ts";

/** o corpo do envio, em bytes (PROPOSTO, SEM FONTE): o pior save medido na CN0 tem ~3 MB cru, perto do teto do localStorage; mais o Tamer */
export const LIMITE_ENVIO = 5 * 1024 * 1024;
/** os dias que o registro fica depois do fim da semana do envio (PROPOSTO, SEM FONTE; MMO-4, seção 11 do plano MMO) */
export const LOG_DIAS_DEPOIS_DA_SEMANA = 30;
const DIA_MS = 86_400_000;

/** o fim da semana de Brasília de uma hora do servidor (a segunda seguinte, 00:00 em Brasília, em ms UTC) */
export function fimDaSemana(hora: number): number {
  return Date.parse(semanaDe(hora) + "T00:00:00Z") - FUSO_BRASILIA_MS + 7 * DIA_MS;
}
/** quando sai o registro de um envio aceito nesta hora */
export const apagarRegistroEm = (hora: number): number => fimDaSemana(hora) + LOG_DIAS_DEPOIS_DA_SEMANA * DIA_MS;

/** tira os registros vencidos (a linha do envio fica, com o hash e os pontos); devolve quantos saíram */
export function apagarRegistrosVencidos(banco: Banco, agora: number): number {
  return Number(banco.prepare("DELETE FROM envios_registros WHERE apagar_em <= ?").run(agora).changes);
}

interface LinhaEnvio {
  id: string; recebido_em: number; pet: number; versao_pet: number; eventos: number; hash_log: string; versao_tamer: number;
  hash_tamer: string; resultado: "aceito" | "recusado"; motivo: string | null; detalhe: string | null; marco10: string | null;
  pontos: number; lutas_ranqueadas: number; ms_conferencia: number; sementes: number; marcos_tamer: string;
}
const COLUNAS = "id, recebido_em, pet, versao_pet, eventos, hash_log, versao_tamer, hash_tamer, resultado, motivo, detalhe, marco10, pontos, lutas_ranqueadas, ms_conferencia, sementes, marcos_tamer";

/** a linha de um envio para a resposta e para o "baixar os meus dados" (as horas em ISO; o registro guardado, até quando) */
export function envioParaDict(banco: Banco, l: LinhaEnvio): Record<string, unknown> {
  const reg = banco.prepare("SELECT apagar_em FROM envios_registros WHERE envio_id = ?").get(l.id) as { apagar_em: number } | undefined;
  return { ...l, marcos_tamer: JSON.parse(l.marcos_tamer) as number[], recebido_em: new Date(l.recebido_em).toISOString(), registro_guardado_ate: reg ? new Date(reg.apagar_em).toISOString() : null };
}
/** os envios de uma conta, do mais novo ao mais velho */
export function enviosDaConta(banco: Banco, contaId: string): Record<string, unknown>[] {
  return (banco.prepare(`SELECT ${COLUNAS} FROM envios WHERE conta_id = ? ORDER BY recebido_em DESC, id`).all(contaId) as unknown as LinhaEnvio[])
    .map(l => envioParaDict(banco, l));
}

export function montarRotasEnvio(app: Hono, cfg: ConfigConta, g: GuardasConta, conferidor: Conferidor): void {
  const { banco, agora } = cfg;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });

  app.use("/envios", g.cors);
  app.use("/envios/*", g.cors);

  app.get("/envios", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    apagarRegistrosVencidos(banco, agora());
    return json(c, 200, enviosDaConta(banco, s.conta_id));
  });

  app.post("/envios",
    /* a sessão e o CSRF antes de ler o corpo: sem sessão, nem se lê */
    async (c, next) => {
      const s = g.sessaoParaMudar(c);
      if (s instanceof Response) return s;
      c.set("sessaoEnvio" as never, s as never);
      await next();
    },
    bodyLimit({ maxSize: LIMITE_ENVIO, onError: c => json(c, 413, { erro: `envio grande demais (o limite é ${LIMITE_ENVIO} bytes)` }) }),
    async c => {
      const s = c.get("sessaoEnvio" as never) as unknown as { conta_id: string };
      if (!(c.req.header("content-type") ?? "").startsWith("application/json")) return json(c, 415, { erro: "o envio é JSON" });
      let envio;
      try {
        let d: unknown;
        try { d = JSON.parse(await c.req.text()); } catch (err) { throw new EnvioMalformado(`o corpo não é JSON: ${(err as Error).message}`); }
        envio = lerEnvio(d);
      } catch (err) {
        if (err instanceof EnvioMalformado) return json(c, 400, { erro: `envio malformado: ${err.message}` });
        throw err;
      }
      const hashLog = hashRegistro(envio.pet.log), hashTamer = hashRegistro(envio.tamer.log);
      const entregues = entreguesDoPet(banco, s.conta_id, envio.pet.semente, envio.pet.versao);
      /* o mesmo envio de novo (o mesmo pet, os mesmos dois registros, as mesmas sementes): devolve a conferência que já está no banco */
      const ja = banco.prepare(`SELECT ${COLUNAS} FROM envios WHERE conta_id = ? AND pet = ? AND versao_pet = ? AND hash_log = ? AND versao_tamer = ? AND hash_tamer = ? AND sementes = ?`)
        .get(s.conta_id, envio.pet.semente, envio.pet.versao, hashLog, envio.tamer.versao, hashTamer, entregues.length) as LinhaEnvio | undefined;
      if (ja) return json(c, ja.resultado === "aceito" ? 200 : 422, { ...envioParaDict(banco, ja), repetido: true });

      /* no worker, fora do laço de eventos (D-CONTA-86), com as sementes ranqueadas entregues a este pet até agora (MMO4) */
      const r: Conferencia = await conferidor(envio, entregues);
      const t = agora(), id = randomUUID();
      const aceito = r.resultado === "aceito";
      /* a semana que ja passou da hora congela antes: a luta dela que chega agora nao entra mais (MMO5) */
      fecharSemanas(banco, t);
      transacao(banco, () => {
        apagarRegistrosVencidos(banco, t);
        banco.prepare(`INSERT INTO envios (${COLUNAS}, conta_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(
          id, t, envio.pet.semente, envio.pet.versao, envio.pet.log.length, hashLog, envio.tamer.versao, hashTamer, r.resultado,
          aceito ? null : r.motivo, aceito ? null : r.detalhe, aceito ? r.marco10 : null, aceito ? r.pontos : 0,
          aceito ? r.lutas.length : 0, r.ms.total, entregues.length, JSON.stringify(aceito ? r.marcosTamer : []), s.conta_id);
        if (aceito) banco.prepare("INSERT INTO envios_registros (envio_id, registro_pet, registro_tamer, apagar_em) VALUES (?, ?, ?, ?)")
          .run(id, JSON.stringify(envio.pet.log), JSON.stringify(envio.tamer.log), apagarRegistroEm(t));
        /* o que a conferencia achou de cada semente fica na semente, para a tabela da semana (MMO5): a primeira conferencia vale */
        if (aceito) gravarLutas(banco, s.conta_id, entregues, r.lutas, id);
        /* os recordes da Torre, da Fábrica e do Salão que a conferência refez vão para o mural (MMO7) */
        if (aceito) gravarFronteira(banco, s.conta_id, envio.pet.semente, r.fronteira, id, t);
        /* os pontos do Digimon, os feitos do Tamer vistos e o reset conferido vão para os dois rankings (MMO8) */
        if (aceito) gravarPontuacoes(banco, s.conta_id, envio.pet, r, id, t);
      });
      const linha = banco.prepare(`SELECT ${COLUNAS} FROM envios WHERE id = ?`).get(id) as unknown as LinhaEnvio;
      const base = envioParaDict(banco, linha);
      if (!aceito) return json(c, 422, { ...base, erro: r.detalhe });
      return json(c, 201, { ...base, lutas: r.lutas, semanas: r.semanas, ms: r.ms });
    });
}
