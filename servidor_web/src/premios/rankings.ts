/* As duas pontuações e o reset (MMO8, docs/PLANO_V3_MMO.md seções 8 e 9; MMO-15 a MMO-19 APROVADAS em 2026-11-11).
     GET /digimons  o máximo histórico dos Digimon: uma linha por pet, pelo total da vida que o servidor conferiu; o aposentado fica com o
                    que tinha. As LINHAS_DOS_RANKINGS primeiras e as linhas de quem pede -> 200 | 401
     GET /tamers    o ranking dos Tamers: uma linha por conta, pelo Respeito conferido; "Tamer Lendário" a partir de TAMER_LENDARIO, sem
                    parar a conta -> 200 | 401
   As duas pedem a sessão, como o mural (mostram os apelidos). Nenhuma das duas tem semana: não zeram.

   O Respeito conta só o que o servidor viu (seção 8), com a conta pura da MMO1 (web/app/src/ranking/pontos.ts, respeito):
     - a 1ª medalha de cada líder e o título da Liga: os feitos do registro do Tamer que o replay do pet que os fez mostra (feitosVistos,
       conferir.ts), guardados em `feitos_tamer` (a migração 8) no primeiro envio aceito que os mostra;
     - o reset: o do registro do Tamer cujo registro final do pet o servidor conferiu (`resets`), pelo nível, só com o mínimo de pontos do
       Digimon conferidos daquele pet (PONTOS_MINIMOS_RESET, MMO-18; a conta é refeita a cada leitura, então um pet que chega ao mínimo
       depois passa a contar);
     - os títulos da semana e os selos Top do dia: os da MMO7 (premios.ts).
   O desempate dos Tamers é quem chegou antes ao Respeito de hoje: a hora do servidor do último feito que conta (`chegou_em`).

   Todo número daqui é PROPOSTO, SEM FONTE (os do Respeito são os da tabela do plano). */
import type { Context, Hono } from "hono";
import { NIVEL_DO_ESTAGIO, type Estagio } from "../../../web/app/motor/index.ts";
import {
  BONUS_RESET, NIVEL_DO_PRIMEIRO_MEGA, RESPEITO_FEITO, nivelPeloRespeito, respeito, respeitoDoReset, tituloDoRespeito, type NivelReset, type Respeito,
} from "../../../web/app/src/ranking/pontos.ts";
import type { Banco } from "../conta/banco.ts";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta } from "../conta/rotas.ts";
import type { Aceito } from "../envio/conferir.ts";
import { fecharDias } from "../desafio/desafio.ts";
import { fecharSemanas } from "../envio/semanas.ts";
import { titulos } from "./premios.ts";

/** as linhas de cada ranking na resposta; as de quem pede vêm sempre (PROPOSTO, SEM FONTE) */
export const LINHAS_DOS_RANKINGS = 100;

/* ------------------------------------------------------------ o que o envio aceito grava (na transação dele) */
/** guarda o que a conferência refez das duas pontuações: o total da vida do pet (só sobe), os feitos do Tamer vistos e o reset conferido */
export function gravarPontuacoes(banco: Banco, contaId: string, pet: { semente: number; versao: number }, r: Aceito, envioId: string, agora: number): void {
  const d = r.digimon;
  banco.prepare(`INSERT INTO digimons (conta_id, pet, versao_pet, pontos, estagio, forma, pontos_em, aposentado_em, envio_id) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?)
    ON CONFLICT (conta_id, pet, versao_pet) DO UPDATE SET
      pontos_em = CASE WHEN excluded.pontos > digimons.pontos THEN excluded.pontos_em ELSE digimons.pontos_em END,
      pontos = MAX(digimons.pontos, excluded.pontos), estagio = excluded.estagio, forma = excluded.forma, envio_id = excluded.envio_id`)
    .run(contaId, pet.semente, pet.versao, d.pontos, d.estagio, d.forma, agora, envioId);
  const feito = banco.prepare("INSERT INTO feitos_tamer (conta_id, feito, pet, visto_em, envio_id) VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING");
  for (const id of r.feitos.medalhas) feito.run(contaId, "medalha:" + id, pet.semente, agora, envioId);
  if (r.feitos.liga) feito.run(contaId, "liga", pet.semente, agora, envioId);
  if (r.reset.situacao === "confere") {
    banco.prepare("INSERT INTO resets (conta_id, pet, nivel, hash, por, visto_em, envio_id) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING")
      .run(contaId, pet.semente, r.reset.nivel, r.reset.hash, r.reset.por, agora, envioId);
    banco.prepare("UPDATE digimons SET aposentado_em = ? WHERE conta_id = ? AND pet = ? AND aposentado_em IS NULL").run(agora, contaId, pet.semente);
  }
}

/* ------------------------------------------------------------ o Respeito conferido */
export interface RespeitoConta extends Respeito { chegou_em: number | null; contagem: { lideres: number; liga: boolean; resets: number; titulos: number; selos: number } }
/** o Respeito que o servidor deu a uma conta, por feito, e a hora em que chegou ao total de hoje */
export function respeitoDaConta(banco: Banco, contaId: string): RespeitoConta {
  const feitos = banco.prepare("SELECT feito, visto_em FROM feitos_tamer WHERE conta_id = ?").all(contaId) as { feito: string; visto_em: number }[];
  const lideres = feitos.filter(f => f.feito.startsWith("medalha:")), liga = feitos.find(f => f.feito === "liga");
  const resets = banco.prepare(`SELECT r.nivel, r.visto_em, (SELECT MAX(d.pontos) FROM digimons d WHERE d.conta_id = r.conta_id AND d.pet = r.pet) AS pontos,
      (SELECT MAX(d.pontos_em) FROM digimons d WHERE d.conta_id = r.conta_id AND d.pet = r.pet) AS pontos_em
    FROM resets r WHERE r.conta_id = ?`).all(contaId) as { nivel: NivelReset; visto_em: number; pontos: number | null; pontos_em: number | null }[];
  const ts = titulos(banco, contaId);
  const selos = banco.prepare(`SELECT t.dia, g.publicado_em FROM tabelas_dia t LEFT JOIN segredos_dia g ON g.dia = t.dia WHERE t.conta_id = ? AND t.selo = 1`)
    .all(contaId) as { dia: string; publicado_em: number | null }[];
  const r = respeito({ lideres: lideres.length, liga: !!liga, resets: resets.map(x => ({ nivel: x.nivel, pontos: x.pontos ?? 0 })), titulosSemana: ts.length, selos: selos.length });
  /* a hora do último feito que conta */
  const horas: number[] = [...lideres.map(f => f.visto_em), ...(liga ? [liga.visto_em] : []), ...ts.map(t => t.congelou_em),
    ...selos.map(s => s.publicado_em ?? 0),
    ...resets.filter(x => respeitoDoReset(x.nivel, x.pontos ?? 0) > 0).map(x => Math.max(x.visto_em, x.pontos_em ?? 0))];
  return { ...r, chegou_em: horas.length ? Math.max(...horas) : null,
    contagem: { lideres: lideres.length, liga: !!liga, resets: resets.length, titulos: ts.length, selos: selos.length } };
}
/** o nível do Tamer no servidor: com o marco 10 conferido (MMO4, marcos_tamer de um envio aceito), 10 e mais um a cada 1 000 de
    Respeito (MMO-15); sem ele, null (o servidor não vê os marcos 1 a 9) */
export function nivelDaConta(banco: Banco, contaId: string, resp: number): number | null {
  const tem10 = (banco.prepare("SELECT marcos_tamer FROM envios WHERE conta_id = ? AND resultado = 'aceito'").all(contaId) as { marcos_tamer: string }[])
    .some(l => (JSON.parse(l.marcos_tamer) as number[]).includes(NIVEL_DO_PRIMEIRO_MEGA));
  return tem10 ? nivelPeloRespeito(NIVEL_DO_PRIMEIRO_MEGA, resp) : null;
}

/* ------------------------------------------------------------ os dois rankings */
const iso = (t: number | null): string | null => (t === null ? null : new Date(t).toISOString());
const nomeDoEstagio = (e: string): string => NIVEL_DO_ESTAGIO[e as Estagio] ?? e;

/** o ranking dos Tamers: as contas com Respeito, pelo Respeito e por quem chegou antes */
export function rankingTamers(banco: Banco, contaId: string): Record<string, unknown> {
  const contas = banco.prepare(`SELECT id, apelido FROM contas WHERE id IN (SELECT conta_id FROM feitos_tamer UNION SELECT conta_id FROM resets
      UNION SELECT conta_id FROM tabelas_dia WHERE selo = 1 UNION SELECT conta_id FROM tabelas_semana WHERE posicao = 1 AND pontos > 0)`)
    .all() as { id: string; apelido: string }[];
  const linhas = contas.map(c => ({ c, r: respeitoDaConta(banco, c.id) })).filter(x => x.r.total > 0)
    .sort((a, b) => (b.r.total - a.r.total) || ((a.r.chegou_em ?? 0) - (b.r.chegou_em ?? 0)) || (a.c.apelido < b.c.apelido ? -1 : a.c.apelido > b.c.apelido ? 1 : 0))
    .map((x, i) => ({ posicao: i + 1, apelido: x.c.apelido, respeito: x.r.total, nivel: nivelDaConta(banco, x.c.id, x.r.total),
      titulo: tituloDoRespeito(x.r.total), chegou_em: iso(x.r.chegou_em), voce: x.c.id === contaId }));
  return { linhas: linhas.filter((l, i) => i < LINHAS_DOS_RANKINGS || l.voce), total: linhas.length };
}

/** o máximo histórico dos Digimon: os pets com pontos, pelo total da vida e por quem chegou antes ao total */
export function rankingDigimons(banco: Banco, contaId: string): Record<string, unknown> {
  const linhas = (banco.prepare(`SELECT d.conta_id, c.apelido, d.pet, d.forma, d.estagio, d.pontos, d.pontos_em, d.aposentado_em FROM digimons d
      JOIN contas c ON c.id = d.conta_id WHERE d.pontos > 0 ORDER BY d.pontos DESC, d.pontos_em, c.apelido, d.pet`).all() as
      { conta_id: string; apelido: string; pet: number; forma: string; estagio: string; pontos: number; pontos_em: number; aposentado_em: number | null }[])
    .map((l, i) => ({ posicao: i + 1, apelido: l.apelido, forma: l.forma, estagio: nomeDoEstagio(l.estagio), pontos: l.pontos,
      aposentado: l.aposentado_em !== null, voce: l.conta_id === contaId, ...(l.conta_id === contaId ? { pet: l.pet } : {}) }));
  return { linhas: linhas.filter((l, i) => i < LINHAS_DOS_RANKINGS || l.voce), total: linhas.length };
}

/** o que a conta tem das duas pontuações, para o "baixar os meus dados" */
export function pontuacoesDaConta(banco: Banco, contaId: string): Record<string, unknown> {
  return {
    digimons: (banco.prepare("SELECT pet, versao_pet, pontos, estagio, forma, pontos_em, aposentado_em, envio_id FROM digimons WHERE conta_id = ? ORDER BY pet").all(contaId) as
      { pontos_em: number; aposentado_em: number | null }[]).map(l => ({ ...l, pontos_em: iso(l.pontos_em), aposentado_em: iso(l.aposentado_em) })),
    resets: (banco.prepare("SELECT pet, nivel, hash, por, visto_em, envio_id FROM resets WHERE conta_id = ? ORDER BY visto_em").all(contaId) as { visto_em: number }[])
      .map(l => ({ ...l, visto_em: iso(l.visto_em) })),
    feitos: (banco.prepare("SELECT feito, pet, visto_em, envio_id FROM feitos_tamer WHERE conta_id = ? ORDER BY visto_em, feito").all(contaId) as { visto_em: number }[])
      .map(l => ({ ...l, visto_em: iso(l.visto_em) })),
  };
}

/** o Respeito da conta como a rota /premios o mostra (o detalhe de cada feito e como a conta é feita) */
export function respeitoParaDict(banco: Banco, contaId: string): Record<string, unknown> {
  const r = respeitoDaConta(banco, contaId);
  return {
    conferido: r.total, lideres: r.lideres, liga: r.liga, resets: r.resets, titulos: r.titulos, selos: r.selos, contagem: r.contagem,
    nivel: nivelDaConta(banco, contaId, r.total), titulo: tituloDoRespeito(r.total), chegou_em: iso(r.chegou_em),
    como: `só o que o servidor viu: ${RESPEITO_FEITO.lider} pela 1ª medalha de cada líder e ${RESPEITO_FEITO.liga} pelo título da Liga, vistos no registro do pet `
      + `que os fez; o reset pelo nível (${BONUS_RESET[1].respeito}, ${BONUS_RESET[2].respeito} ou ${BONUS_RESET[3].respeito}), conferido no registro final do pet e com `
      + `o mínimo de pontos dele; ${RESPEITO_FEITO.titulo_semana} por título da semana e ${RESPEITO_FEITO.selo_dia} por selo Top do dia`,
  };
}

/* ------------------------------------------------------------ as rotas */
export function montarRotasRankings(app: Hono, cfg: ConfigConta, g: GuardasConta): void {
  const { banco, agora } = cfg;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });
  for (const r of ["/digimons", "/tamers"]) app.use(r, g.cors);

  app.get("/digimons", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    return json(c, 200, rankingDigimons(banco, s.conta_id));
  });

  app.get("/tamers", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const t = agora();
    fecharSemanas(banco, t); fecharDias(banco, t);
    return json(c, 200, rankingTamers(banco, s.conta_id));
  });
}
