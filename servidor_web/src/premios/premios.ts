/* As recompensas e o mural (MMO7, docs/PLANO_V3_MMO.md seções 7 e 8; MMO-12: o ranking paga prestígio, não Bits).
     GET /premios   o que a conta ganhou: o título da semana (no perfil por uma semana), os títulos de antes, os selos "Top do dia", os
                    enfeites da temporada e o Respeito conferido -> 200 | 401
     GET /mural     os recordes de todos os tempos da Torre, da Fábrica e do Salão e os títulos de todas as semanas -> 200 | 401
   As duas pedem a sessão (o beta é de convidados, como as tabelas da semana): o mural mostra os apelidos.

   De onde cada recompensa sai (nada novo é guardado, menos os recordes):
     - o título da semana: o 1º de cada tabela de estágio congelada (`tabelas_semana`, MMO5), com pontos (D-CONTA-153). "Campeão Rookie
       da semana 46" (a semana ISO da segunda-feira que a abre). Fica no perfil por DIAS_DO_TITULO_NO_PERFIL depois do congelamento, e no
       mural para sempre (enquanto a conta existir: apagar a conta tira as linhas dela, como na tabela);
     - o selo "Top do dia": o que o fechamento do dia da MMO6 já marca em `tabelas_dia` (selo = 1);
     - o enfeite da temporada: quem ficou entre os ENFEITE_ATE primeiros (com pontos) de uma tabela de estágio de uma semana da temporada.
       Um por temporada de SEMANAS_POR_TEMPORADA semanas, contadas de EPOCA_TEMPORADAS. Não se vende na loja: o jogo só o põe na ilha
       quando esta rota diz que a conta o tem;
     - o Respeito conferido (seção 8): só o que o servidor viu e deu. Aqui, o título da semana e o selo, pelos valores da tabela do plano.
       As medalhas, o título da Liga e o reset entram na MMO8, com a conta pura dos dois pontos (D-CONTA-156).
   Os recordes (a migração 7): a cada envio aceito, `gravarFronteira` guarda o que a conferência refez (FronteiraVista, conferir.ts): a
   Torre pelo replay do pet, a Fábrica pelo replay do Tamer, e o Salão juntando as lutas que o replay de cada pet viu com as tentativas do
   Tamer. O recorde só sobe. No mural, o desempate é quem chegou primeiro ao valor, pela hora do servidor.

   Todo número daqui é PROPOSTO, SEM FONTE, até o Matheus decidir (os do Respeito são os da tabela do plano). */
import type { Context, Hono } from "hono";
import { semanaDe } from "../../../web/app/src/ranking/pontos.ts";
import type { Banco } from "../conta/banco.ts";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta } from "../conta/rotas.ts";
import type { FronteiraVista } from "../envio/conferir.ts";
import { fecharDias } from "../desafio/desafio.ts";
import { ESTAGIOS, fecharSemanas } from "../envio/semanas.ts";

const DIA_MS = 86_400_000;
/** quantos dias o título da semana fica no perfil depois do congelamento (o plano: "no perfil por uma semana") */
export const DIAS_DO_TITULO_NO_PERFIL = 7;
/** até que posição de uma tabela da semana leva o enfeite da temporada (o plano: os 10 primeiros) */
export const ENFEITE_ATE = 10;
/** as semanas de uma temporada (o plano: 4) e a segunda-feira que abre a temporada 1 (PROPOSTA, SEM FONTE: a semana ISO 45 de 2026, a
    primeira temporada com a MMO5 no ar). A semana de antes da época fica na temporada 1 */
export const SEMANAS_POR_TEMPORADA = 4;
export const EPOCA_TEMPORADAS = "2026-11-02";
/** o Respeito de cada recompensa (a tabela da seção 8 do plano; PROPOSTO, SEM FONTE) */
export const RESPEITO = { titulo_semana: 100, selo_dia: 20 } as const;
/** as linhas de cada recorde que o mural mostra; a de quem olha vem sempre (PROPOSTO, SEM FONTE) */
export const LINHAS_DO_MURAL = 10;
/** as instalações do mural, na ordem da tela */
export const INSTALACOES_MURAL = ["torre", "fabrica", "salao"] as const;
export type InstMural = typeof INSTALACOES_MURAL[number];

/** a semana ISO 8601 de uma segunda-feira (AAAA-MM-DD): o número de 1 a 53 */
export function semanaIso(semana: string): number {
  const t = Date.parse(semana + "T00:00:00Z");
  if (!Number.isFinite(t)) throw new Error(`a semana não é uma data AAAA-MM-DD: "${semana}"`);
  const d = new Date(t), dia = (d.getUTCDay() + 6) % 7;   // segunda = 0
  const quinta = new Date(t - dia * DIA_MS + 3 * DIA_MS);  // a quinta da mesma semana decide o ano
  const ano = Date.UTC(quinta.getUTCFullYear(), 0, 1);
  return 1 + Math.floor((quinta.getTime() - ano) / (7 * DIA_MS));
}
/** a temporada de uma semana: 1 a partir da EPOCA_TEMPORADAS, uma a cada SEMANAS_POR_TEMPORADA semanas */
export function temporadaDe(semana: string): number {
  const t = Date.parse(semana + "T00:00:00Z");
  if (!Number.isFinite(t)) throw new Error(`a semana não é uma data AAAA-MM-DD: "${semana}"`);
  return Math.max(1, Math.floor((t - Date.parse(EPOCA_TEMPORADAS + "T00:00:00Z")) / (SEMANAS_POR_TEMPORADA * 7 * DIA_MS)) + 1);
}
/** a primeira e a última segunda-feira de uma temporada */
export function semanasDaTemporada(n: number): { de: string; ate: string } {
  if (!Number.isInteger(n) || n < 1) throw new Error(`temporada inválida: ${n}`);
  const de = Date.parse(EPOCA_TEMPORADAS + "T00:00:00Z") + (n - 1) * SEMANAS_POR_TEMPORADA * 7 * DIA_MS;
  const f = (t: number) => new Date(t).toISOString().slice(0, 10);
  return { de: f(de), ate: f(de + (SEMANAS_POR_TEMPORADA - 1) * 7 * DIA_MS) };
}
/** "Campeão Rookie da semana 46" */
export const textoDoTitulo = (estagio: string, semana: string): string => `Campeão ${estagio} da semana ${semanaIso(semana)}`;

/* ------------------------------------------------------------ os recordes (gravados no envio aceito) */
/** guarda o que a conferência refez da Fronteira (roda na transação do envio aceito); o recorde só sobe. Devolve os que subiram */
export function gravarFronteira(banco: Banco, contaId: string, pet: number, f: FronteiraVista, envioId: string, agora: number): InstMural[] {
  const vista = banco.prepare("INSERT INTO salao_vistas (conta_id, pet, semente, venceu) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING");
  for (const l of f.salao) vista.run(contaId, pet, l.s, l.venceu ? 1 : 0);
  /* o Salão: cada tentativa do Tamer conta, da primeira luta em diante, enquanto a luta foi vista no replay do pet que lutou e venceu */
  const viu = banco.prepare("SELECT venceu FROM salao_vistas WHERE conta_id = ? AND pet = ? AND semente = ?");
  let salao = 0;
  for (const t of f.tentativasSalao) {
    let v = 0;
    for (const l of t.lutas) {
      const x = viu.get(contaId, l.pet, l.s) as { venceu: number } | undefined;
      if (!x || x.venceu !== 1 || !l.venceu) break;
      v++;
    }
    salao = Math.max(salao, v);
  }
  const valores: Record<InstMural, number> = { torre: f.torre, fabrica: f.fabrica, salao };
  const subiu: InstMural[] = [];
  for (const inst of INSTALACOES_MURAL) {
    const v = valores[inst];
    if (!Number.isInteger(v) || v < 1) continue;
    const r = banco.prepare(`INSERT INTO recordes (conta_id, inst, valor, visto_em, envio_id) VALUES (?, ?, ?, ?, ?)
      ON CONFLICT (conta_id, inst) DO UPDATE SET valor = excluded.valor, visto_em = excluded.visto_em, envio_id = excluded.envio_id
      WHERE excluded.valor > recordes.valor`).run(contaId, inst, v, agora, envioId);
    if (r.changes > 0) subiu.push(inst);
  }
  return subiu;
}

/* ------------------------------------------------------------ o que sai das tabelas congeladas */
export interface Titulo { semana: string; numero: number; estagio: string; texto: string; congelou_em: number }
/** os títulos da semana (o 1º com pontos de cada tabela congelada); de uma conta, ou de todas */
export function titulos(banco: Banco, contaId?: string): (Titulo & { conta_id: string; apelido: string })[] {
  const linhas = banco.prepare(`SELECT t.semana, t.estagio, t.conta_id, c.apelido, g.publicado_em FROM tabelas_semana t
      JOIN contas c ON c.id = t.conta_id JOIN segredos_semana g ON g.semana = t.semana
    WHERE t.posicao = 1 AND t.pontos > 0 ${contaId ? "AND t.conta_id = ?" : ""} ORDER BY t.semana DESC`)
    .all(...(contaId ? [contaId] : [])) as { semana: string; estagio: string; conta_id: string; apelido: string; publicado_em: number }[];
  const ordem = (e: string) => ESTAGIOS.indexOf(e);
  return linhas.sort((a, b) => (a.semana < b.semana ? 1 : a.semana > b.semana ? -1 : ordem(a.estagio) - ordem(b.estagio)))
    .map(l => ({ semana: l.semana, numero: semanaIso(l.semana), estagio: l.estagio, texto: textoDoTitulo(l.estagio, l.semana),
      congelou_em: l.publicado_em, conta_id: l.conta_id, apelido: l.apelido }));
}

export interface Enfeite { temporada: number; de: string; ate: string; melhor: { semana: string; estagio: string; posicao: number } }
/** os enfeites da temporada de uma conta: um por temporada em que ela ficou entre os ENFEITE_ATE primeiros (com pontos) de uma tabela
    da semana; a melhor colocação da temporada vai junto */
export function enfeitesDaConta(banco: Banco, contaId: string): Enfeite[] {
  const linhas = banco.prepare(`SELECT semana, estagio, posicao FROM tabelas_semana WHERE conta_id = ? AND posicao <= ? AND pontos > 0
    ORDER BY semana, posicao`).all(contaId, ENFEITE_ATE) as { semana: string; estagio: string; posicao: number }[];
  const por = new Map<number, Enfeite>();
  for (const l of linhas) {
    const n = temporadaDe(l.semana), ja = por.get(n);
    if (!ja || l.posicao < ja.melhor.posicao) por.set(n, { temporada: n, ...semanasDaTemporada(n), melhor: { ...l } });
  }
  return [...por.values()].sort((a, b) => b.temporada - a.temporada);
}

/** os selos "Top do dia" de uma conta (o fechamento do dia da MMO6 os marca) */
export function selosDaConta(banco: Banco, contaId: string): { dia: string; posicao: number; vitorias: number }[] {
  return banco.prepare("SELECT dia, posicao, vitorias FROM tabelas_dia WHERE conta_id = ? AND selo = 1 ORDER BY dia DESC").all(contaId) as never;
}

/** o Respeito que o servidor deu a uma conta (só os títulos da semana e os selos; MMO8 soma o resto) */
export function respeitoConferido(nTitulos: number, nSelos: number): number {
  return nTitulos * RESPEITO.titulo_semana + nSelos * RESPEITO.selo_dia;
}

/** o mural: os recordes de cada instalação (as LINHAS_DO_MURAL primeiras e a de quem olha) e os títulos de todas as semanas */
export function mural(banco: Banco, contaId: string): Record<string, unknown> {
  const recordes: Record<string, unknown> = {}, total: Record<string, number> = {};
  for (const inst of INSTALACOES_MURAL) {
    const linhas = (banco.prepare(`SELECT r.conta_id, c.apelido, r.valor, r.visto_em FROM recordes r JOIN contas c ON c.id = r.conta_id
      WHERE r.inst = ? ORDER BY r.valor DESC, r.visto_em, c.apelido`).all(inst) as { conta_id: string; apelido: string; valor: number; visto_em: number }[]);
    total[inst] = linhas.length;
    recordes[inst] = linhas.map((l, i) => ({ posicao: i + 1, apelido: l.apelido, valor: l.valor, visto_em: new Date(l.visto_em).toISOString(), voce: l.conta_id === contaId }))
      .filter((l, i) => i < LINHAS_DO_MURAL || l.voce);
  }
  const ts = titulos(banco).map(t => ({ semana: t.semana, numero: t.numero, estagio: t.estagio, texto: t.texto, apelido: t.apelido, voce: t.conta_id === contaId }));
  return { recordes, total, titulos: ts };
}

/* ------------------------------------------------------------ as rotas */
export function montarRotasPremios(app: Hono, cfg: ConfigConta, g: GuardasConta): void {
  const { banco, agora } = cfg;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });
  const iso = (t: number): string => new Date(t).toISOString();
  for (const r of ["/premios", "/mural"]) app.use(r, g.cors);

  app.get("/premios", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const t = agora();
    fecharSemanas(banco, t); fecharDias(banco, t);
    const ts = titulos(banco, s.conta_id), selos = selosDaConta(banco, s.conta_id);
    const noPerfil = ts.filter(x => t < x.congelou_em + DIAS_DO_TITULO_NO_PERFIL * DIA_MS);
    const dict = (x: Titulo) => ({ semana: x.semana, numero: x.numero, estagio: x.estagio, texto: x.texto, congelou_em: iso(x.congelou_em),
      no_perfil_ate: iso(x.congelou_em + DIAS_DO_TITULO_NO_PERFIL * DIA_MS) });
    const recordes = Object.fromEntries(INSTALACOES_MURAL.map(inst => {
      const r = banco.prepare("SELECT valor, visto_em FROM recordes WHERE conta_id = ? AND inst = ?").get(s.conta_id, inst) as { valor: number; visto_em: number } | undefined;
      return [inst, r ? { valor: r.valor, visto_em: iso(r.visto_em) } : null];
    }));
    return json(c, 200, {
      titulo_atual: noPerfil.map(dict),
      titulos: ts.map(dict),
      selos: { total: selos.length, lista: selos },
      enfeites: enfeitesDaConta(banco, s.conta_id),
      recordes,
      respeito: { conferido: respeitoConferido(ts.length, selos.length), titulos: ts.length * RESPEITO.titulo_semana, selos: selos.length * RESPEITO.selo_dia,
        como: `só o que o servidor deu: ${RESPEITO.titulo_semana} por título da semana e ${RESPEITO.selo_dia} por selo Top do dia (as medalhas, a Liga e o reset entram depois)` },
      temporada_atual: temporadaDe(semanaDe(t)),
    });
  });

  app.get("/mural", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    fecharSemanas(banco, agora());
    return json(c, 200, mural(banco, s.conta_id));
  });
}

/** o que a conta tem de prêmios e recordes, para o "baixar os meus dados" */
export function premiosDaConta(banco: Banco, contaId: string): Record<string, unknown> {
  const iso = (t: number): string => new Date(t).toISOString();
  return {
    recordes: (banco.prepare("SELECT inst, valor, visto_em, envio_id FROM recordes WHERE conta_id = ? ORDER BY inst").all(contaId) as { visto_em: number }[])
      .map(r => ({ ...r, visto_em: iso(r.visto_em) })),
    salao_vistas: banco.prepare("SELECT pet, semente, venceu FROM salao_vistas WHERE conta_id = ? ORDER BY pet, semente").all(contaId),
  };
}

