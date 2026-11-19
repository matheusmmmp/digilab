/* O ranking da semana (MMO5, docs/PLANO_V3_MMO.md seção 5; MMO-9): as tabelas por estágio, o desempate, o fechamento da semana e o
   segredo publicado.
     GET /semanas                    a semana aberta, quando fecha e as fechadas -> 200 {atual, fecha_em, congela_em, fechadas}
     GET /semanas/:semana/tabelas    as tabelas da semana, uma por estágio -> 200 {semana, estado, congela_em, estagios, total} | 400 | 401
     GET /semanas/:semana/segredo    o segredo de uma semana fechada -> 200 {semana, segredo, publicado_em, como} | 404 {motivo} | 400
   As tabelas pedem a sessão da conta (o beta é de convidados); o segredo publicado não pede: não tem dado de ninguém.

   De onde a tabela sai: cada semente entregue guarda o que a conferência do envio achou dela (a situação, o estágio do pet, o rival e a
   faixa; a migração 4). Os pontos não se guardam: a tabela os refaz pela conta da MMO1 (`pontuar`, web/app/src/ranking/pontos.ts), por
   pet, e soma as linhas dos pets da conta em cada estágio. Um jogador aparece em cada tabela em que lutou.

   A primeira conferência vale: a situação de uma semente que já fechou (vitória, derrota, não enviada, fora da Arena, acima do limite) não
   muda num envio seguinte. Só a pendente (o registro ainda não chegou ao indice) e a que nunca foi conferida ainda mudam.

   O fechamento: a semana vai de segunda 00:00 a domingo 23:59 de Brasília. Ela congela FOLGA_DO_FECHAMENTO_MS depois do fim (o envio da
   luta pedida no último minuto ainda entra). No congelamento, numa transação só: a semente pendente e a nunca conferida viram "não
   enviada" (0 pontos, conta como luta usada); as tabelas são gravadas em `tabelas_semana`; o segredo ganha `publicado_em`. Depois disso
   nada da semana muda. O fechamento roda sozinho, na primeira chamada depois da hora (as rotas daqui, o envio e o pedido da semente).

   As divisões de 30 (com 60 jogadores ativos ou mais, MMO-9) não estão aqui: uma tabela por estágio. */
import type { Context, Hono } from "hono";
import {
  compararLinhas, FUSO_BRASILIA_MS, PONTOS_FAIXA, pontuar, semanaDe, type LinhaSemana, type LutaRanqueada, type Situacao,
} from "../../../web/app/src/ranking/pontos.ts";
import { transacao, type Banco } from "../conta/banco.ts";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta } from "../conta/rotas.ts";
import type { EntregueComHash } from "./conferir.ts";

const DIA_MS = 86_400_000;
/** quanto depois do fim da semana ela congela (PROPOSTA, SEM FONTE): o envio da luta pedida no último minuto ainda entra */
export const FOLGA_DO_FECHAMENTO_MS = 60 * 60_000;
/** as linhas de cada tabela que a resposta leva (PROPOSTO, SEM FONTE); a linha de quem pede vem sempre */
export const LINHAS_DA_TABELA = 100;
/** as semanas fechadas que o GET /semanas lista (PROPOSTO, SEM FONTE) */
export const SEMANAS_LISTADAS = 12;
/** os estágios com tabela, na ordem da tela (os nomes do Digimon, as faixas da MMO1) */
export const ESTAGIOS: readonly string[] = Object.keys(PONTOS_FAIXA);
/** as situações que não mudam mais num envio seguinte */
const FINAIS: readonly string[] = ["vitoria", "derrota", "nao_enviada", "fora_da_arena", "acima_do_limite"];

/** o fim de uma semana pela segunda-feira que a abre (AAAA-MM-DD): a segunda seguinte, 00:00 de Brasília, em ms UTC */
export const fimDaSemanaDe = (semana: string): number => Date.parse(semana + "T00:00:00Z") - FUSO_BRASILIA_MS + 7 * DIA_MS;
/** quando a semana congela */
export const congelaEm = (semana: string): number => fimDaSemanaDe(semana) + FOLGA_DO_FECHAMENTO_MS;
/** AAAA-MM-DD de uma segunda-feira que existe */
export function semanaValida(s: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
  const t = Date.parse(s + "T00:00:00Z");
  return Number.isFinite(t) && new Date(t).toISOString().slice(0, 10) === s && new Date(t).getUTCDay() === 1;
}

/** uma linha da tabela de um estágio, com a conta */
export interface LinhaTabela extends LinhaSemana { contaId: string; apelido: string }

/** guarda o que a conferência de um envio aceito achou de cada semente do pet. Roda na transação do envio. A semente de uma semana já
    fechada e a que já tem uma situação final ficam como estão; devolve quantas mudaram */
export function gravarLutas(banco: Banco, contaId: string, entregues: readonly EntregueComHash[], lutas: readonly LutaRanqueada[], envioId: string): number {
  const numero = new Map(entregues.map(x => [x.semente, x.numero]));
  let mudaram = 0;
  for (const l of lutas) {
    const n = numero.get(l.semente);
    if (n === undefined) throw new Error(`a conferência devolveu uma luta de uma semente que não foi entregue: ${l.semente}`);
    const ja = banco.prepare(`SELECT s.situacao, g.publicado_em FROM sementes s LEFT JOIN segredos_semana g ON g.semana = s.semana
      WHERE s.conta_id = ? AND s.numero = ?`).get(contaId, n) as { situacao: string | null; publicado_em: number | null } | undefined;
    if (!ja) throw new Error(`a semente ${n} da conta sumiu durante a conferência`);
    if (ja.publicado_em !== null || (ja.situacao !== null && FINAIS.includes(ja.situacao))) continue;
    banco.prepare("UPDATE sementes SET situacao = ?, estagio = ?, rival = ?, faixa = ?, envio_id = ? WHERE conta_id = ? AND numero = ?")
      .run(l.situacao, l.estagio, l.rival, l.faixa, envioId, contaId, n);
    mudaram++;
  }
  return mudaram;
}

interface LinhaSemente {
  conta_id: string; apelido: string; numero: number; pet: number; versao_pet: number; indice: number; semente: number; hora: number;
  dia: string; semana: string; situacao: string; estagio: string | null; rival: string | null; faixa: string | null;
}

/** as tabelas de uma semana pelas sementes conferidas: uma por estágio, na ordem do desempate (seção 5). Quem empata nos quatro
    critérios fica na ordem do apelido */
export function tabelasDaSemana(banco: Banco, semana: string): Map<string, LinhaTabela[]> {
  const linhas = banco.prepare(`SELECT s.conta_id, c.apelido, s.numero, s.pet, s.versao_pet, s.indice, s.semente, s.hora, s.dia, s.semana,
      s.situacao, s.estagio, s.rival, s.faixa
    FROM sementes s JOIN contas c ON c.id = s.conta_id
    WHERE s.semana = ? AND s.situacao IS NOT NULL ORDER BY c.apelido, s.conta_id, s.pet, s.versao_pet, s.numero`).all(semana) as unknown as LinhaSemente[];
  /* os pontos por pet (a metade para o mesmo rival na semana é do registro de cada pet, como na conferência) */
  const porPet = new Map<string, { contaId: string; apelido: string; lutas: LutaRanqueada[] }>();
  for (const l of linhas) {
    const chave = `${l.conta_id}|${l.pet}|${l.versao_pet}`;
    const g = porPet.get(chave) ?? { contaId: l.conta_id, apelido: l.apelido, lutas: [] };
    g.lutas.push({ semente: l.semente, indice: l.indice, hora: l.hora, dia: l.dia, semana: l.semana, situacao: l.situacao as Situacao,
      rival: l.rival, faixa: l.faixa, estagio: l.estagio, pontos: 0, vidaFinal: null });
    porPet.set(chave, g);
  }
  /* as linhas da conta em cada estágio: os pets somam */
  const porConta = new Map<string, LinhaTabela & { rivais: Set<string> }>();
  for (const g of porPet.values()) {
    pontuar(g.lutas);
    for (const l of g.lutas) {
      if (l.situacao === "acima_do_limite" || l.estagio === null) continue;
      if (!ESTAGIOS.includes(l.estagio)) continue;   // o In-Training não tem tabela
      const chave = `${l.estagio}|${g.contaId}`;
      const x = porConta.get(chave) ?? { semana, estagio: l.estagio, pontos: 0, rivaisVencidos: 0, lutasUsadas: 0, horaDosPontos: null,
        contaId: g.contaId, apelido: g.apelido, rivais: new Set<string>() };
      x.lutasUsadas++;
      if (l.situacao === "vitoria") {
        x.rivais.add(l.rival!); x.pontos += l.pontos;
        x.horaDosPontos = x.horaDosPontos === null ? l.hora : Math.max(x.horaDosPontos, l.hora);
      }
      x.rivaisVencidos = x.rivais.size;
      porConta.set(chave, x);
    }
  }
  const tabelas = new Map<string, LinhaTabela[]>(ESTAGIOS.map(e => [e, []]));
  for (const { rivais: _r, ...x } of porConta.values()) tabelas.get(x.estagio)!.push(x);
  for (const t of tabelas.values()) t.sort((a, b) => compararLinhas(a, b) || (a.apelido < b.apelido ? -1 : a.apelido > b.apelido ? 1 : 0));
  return tabelas;
}

/** fecha toda semana que já passou da hora de congelar; devolve as que fechou agora. Cada uma na sua transação */
export function fecharSemanas(banco: Banco, agora: number): string[] {
  const abertas = (banco.prepare("SELECT semana FROM segredos_semana WHERE publicado_em IS NULL ORDER BY semana").all() as { semana: string }[])
    .map(l => l.semana).filter(s => congelaEm(s) <= agora);
  for (const semana of abertas) {
    transacao(banco, () => {
      banco.prepare("UPDATE sementes SET situacao = 'nao_enviada' WHERE semana = ? AND (situacao IS NULL OR situacao = 'pendente')").run(semana);
      const por = banco.prepare(`INSERT INTO tabelas_semana (semana, estagio, posicao, conta_id, pontos, rivais_vencidos, lutas_usadas, hora_dos_pontos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
      for (const [estagio, linhas] of tabelasDaSemana(banco, semana))
        linhas.forEach((l, i) => por.run(semana, estagio, i + 1, l.contaId, l.pontos, l.rivaisVencidos, l.lutasUsadas, l.horaDosPontos));
      banco.prepare("UPDATE segredos_semana SET publicado_em = ? WHERE semana = ?").run(agora, semana);
    });
  }
  return abertas;
}

/** o segredo de uma semana, se já foi publicado */
export function segredoPublicado(banco: Banco, semana: string): { segredo: string; publicadoEm: number } | "aberta" | null {
  const l = banco.prepare("SELECT segredo, publicado_em FROM segredos_semana WHERE semana = ?").get(semana) as { segredo: string; publicado_em: number | null } | undefined;
  if (!l) return null;
  return l.publicado_em === null ? "aberta" : { segredo: l.segredo, publicadoEm: l.publicado_em };
}

/** as tabelas gravadas de uma semana fechada (a conta apagada sai da tabela; as posições dos outros ficam) */
function tabelasGravadas(banco: Banco, semana: string): Map<string, (LinhaTabela & { posicao: number })[]> {
  const linhas = banco.prepare(`SELECT t.estagio, t.posicao, t.conta_id, c.apelido, t.pontos, t.rivais_vencidos, t.lutas_usadas, t.hora_dos_pontos
    FROM tabelas_semana t JOIN contas c ON c.id = t.conta_id WHERE t.semana = ? ORDER BY t.estagio, t.posicao`).all(semana) as unknown as
    { estagio: string; posicao: number; conta_id: string; apelido: string; pontos: number; rivais_vencidos: number; lutas_usadas: number; hora_dos_pontos: number | null }[];
  const tabelas = new Map<string, (LinhaTabela & { posicao: number })[]>(ESTAGIOS.map(e => [e, []]));
  for (const l of linhas) tabelas.get(l.estagio)?.push({ semana, estagio: l.estagio, posicao: l.posicao, contaId: l.conta_id, apelido: l.apelido,
    pontos: l.pontos, rivaisVencidos: l.rivais_vencidos, lutasUsadas: l.lutas_usadas, horaDosPontos: l.hora_dos_pontos });
  return tabelas;
}

export function montarRotasSemana(app: Hono, cfg: ConfigConta, g: GuardasConta): void {
  const { banco, agora } = cfg;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store" });
  const iso = (t: number): string => new Date(t).toISOString();

  app.use("/semanas", g.cors);
  app.use("/semanas/*", g.cors);

  app.get("/semanas", c => {
    const t = agora();
    fecharSemanas(banco, t);
    const atual = semanaDe(t);
    const fechadas = (banco.prepare("SELECT semana, publicado_em FROM segredos_semana WHERE publicado_em IS NOT NULL ORDER BY semana DESC LIMIT ?")
      .all(SEMANAS_LISTADAS) as { semana: string; publicado_em: number }[]).map(l => ({ semana: l.semana, publicado_em: iso(l.publicado_em) }));
    return json(c, 200, { atual, fecha_em: iso(fimDaSemanaDe(atual)), congela_em: iso(congelaEm(atual)), fechadas });
  });

  app.get("/semanas/:semana/tabelas", c => {
    const s = g.sessaoDe(c);
    if (!s) return json(c, 401, { erro: "sem sessão" });
    const semana = c.req.param("semana");
    if (!semanaValida(semana)) return json(c, 400, { erro: "a semana é a segunda-feira que a abre, AAAA-MM-DD" });
    fecharSemanas(banco, agora());
    const fechada = typeof segredoPublicado(banco, semana) === "object" && segredoPublicado(banco, semana) !== null;
    const tabelas: Map<string, (LinhaTabela & { posicao?: number })[]> = fechada ? tabelasGravadas(banco, semana) : tabelasDaSemana(banco, semana);
    const estagios: Record<string, unknown[]> = {}, total: Record<string, number> = {};
    for (const estagio of ESTAGIOS) {
      const linhas = tabelas.get(estagio)!;
      total[estagio] = linhas.length;
      estagios[estagio] = linhas.map((l, i) => ({ posicao: l.posicao ?? i + 1, apelido: l.apelido, pontos: l.pontos, rivais_vencidos: l.rivaisVencidos,
        lutas_usadas: l.lutasUsadas, hora_dos_pontos: l.horaDosPontos === null ? null : iso(l.horaDosPontos), voce: l.contaId === s.conta_id }))
        .filter((l, i) => i < LINHAS_DA_TABELA || l.voce);
    }
    return json(c, 200, { semana, estado: fechada ? "fechada" : "aberta", congela_em: iso(congelaEm(semana)), estagios, total });
  });

  app.get("/semanas/:semana/segredo", c => {
    const semana = c.req.param("semana");
    if (!semanaValida(semana)) return json(c, 400, { erro: "a semana é a segunda-feira que a abre, AAAA-MM-DD" });
    fecharSemanas(banco, agora());
    const r = segredoPublicado(banco, semana);
    if (r === null) return json(c, 404, { motivo: "sem_segredo", erro: "nenhuma luta ranqueada foi pedida nesta semana" });
    if (r === "aberta") return json(c, 404, { motivo: "semana_aberta", erro: "o segredo sai quando a semana congela", congela_em: iso(congelaEm(semana)) });
    return json(c, 200, { semana, segredo: r.segredo, publicado_em: iso(r.publicadoEm),
      como: 'a semente da luta = os 4 primeiros bytes (inteiro sem sinal, big-endian) de HMAC-SHA256(segredo em bytes, "<id da conta>|<número da luta>")' });
  });
}
