// Conferencia da Fabrica e do Salao da Fronteira (docs/DESIGN_FRONTEIRA.md, secao 3; medalhas parte 4c) e, desde a rodada de equilibrio geral
// (fase 3; docs/PLANO_EQUILIBRIO_GERAL.md, metas M-C2 e M-C3), a calibracao das duas nos pets v9.
//
// --v6: a conferencia de antes, SEM calibracao (decisao do Matheus: sem rodada de equilibrio na parte 4c): so confere que as duas sao jogaveis
// e relata. Reproduz o artefato gravado (artifacts_campanha/fronteira/conferencia_4c.json) byte a byte.
// Metodo (o das partes 4a e 4b): motor web, escala dos pets v6 ligada, regras V21D, limite de turnos do desafiado (o rival).
// - Fabrica: as tentativas 1..N_FABRICA do jogo (a semente de cada uma sai do numero dela, sementeFabrica), jogadas pelo motor
//   (TentativaFabrica) com tres politicas simples do jogador: o primeiro alugado sem troca; o de melhor arquetipo (a ordem da conferencia da
//   parte 4b, vence a 1a luta da Torre: furioso, duelista, espelho, emboscador, vigia, sentinela, tita, muralha) sem troca; e o mesmo,
//   trocando quando o rival derrotado e de arquetipo melhor. Relato a parte (NAO adotado): a troca entrando inteira (trocando por
//   arquetipo melhor, e trocando sempre, para curar);
// - Salao: o pet de referencia de cada estagio (as formas de referencia, test/itens_ref.mjs: Rookie os 2 ramos, Champion as 4 linhas,
//   Ultimate e Mega as 8 formas, nas 4 especies), com o treino tipico do estagio (CIT.tipico) e sem treino, contra os rivais sorteados do
//   Salao (rivalSalao, fator 1), sementes de validacao 4101...4505 x N_SALAO por especie e forma. As lutas do Salao sao independentes (um
//   pet por nivel, sem cura a levar), entao a chance de vencer os 4 com um time fixo e o produto das chances de cada nivel;
// - os pets dos testes ponta a ponta (e2e/save_salao.json e o Mega de e2e/save_liga.json) nas 50 primeiras lutas de cada um no Salao, pelo
//   motor (Motor.lutar com a semente do registro: o sorteio do jogo).
//
// Pets v9 (padrao), nas sementes de calibracao (3101...3505):
// - Fabrica (M-C2): as tentativas nas regras dos v9 (TentativaFabrica com a versao 9: V21E, o fator dos rivais FATOR_RIVAL_FABRICA_V9, a troca
//   com a vida cheia), POR_SEMENTE tentativas por semente de calibracao (a semente da tentativa: hashSemente("conferir-fabrica", semente, i);
//   as do jogo saem do numero da tentativa e nao sao sementes de calibracao). Meta: escolhendo o melhor alugado (a politica "o de melhor
//   arquetipo, trocando pelo rival derrotado de arquetipo melhor"; a ordem dos arquetipos e a de antes, que e tambem a da conferencia da Torre
//   de Batalha dos v9), vencer ao menos uma serie em >= 0,25 das tentativas. As outras duas politicas ficam como relato. Teto de LUTAS_MAX
//   lutas por tentativa (so a conferencia; relata quantas chegam nele);
// - Salao (M-C3): o metodo de antes com as regras dos v9 (V21E, CESC_V9) e o fator do rival de cada nivel dos v9 (salao.fatorSalao, FATOR_SALAO_V9).
//   Meta: cada nivel, com o treino tipico, entre 0,70 e 0,95 (a media das formas e especies);
// - --calibrar: Fabrica: a grade FATORES_FABRICA do fator dos rivais; escolhido (regra registrada antes de rodar) o MAIOR fator (a Fabrica mais
//   dificil, o mais perto do 1 de antes) que passa a meta com folga >= FOLGA_FABRICA. Salao: a grade FATORES_SALAO por nivel; so os fatores
//   >= 1 (o rival nao fica mais fraco que o de antes: sem treino o pet nao vence mais que hoje; a maior folga pura levava o Champion a 0,5,
//   com o pet sem treino vencendo 0,75), e entre eles o de maior folga robusta: a menor folga min(taxa - 0,70, 0,95 - taxa) entre o fator e
//   os dois vizinhos da grade (o Rookie tem um degrau entre 1,2 e 1,3).
// --validar (fase 4, a validacao unica): a conferencia dos v9 (a Fabrica e o Salao do motor, nada muda) nas sementes de validacao (4101...4505).
// uso (em web/app): npx tsx test/conferir_fabrica_salao.mjs [--v6 | --calibrar | --validar]
//   --v6: artifacts_campanha/fronteira/conferencia_4c.json; padrao: artifacts_equilibrio_geral/fase3/fabrica_salao_conferencia.json;
//   --calibrar: artifacts_equilibrio_geral/fase3/fabrica_calibracao.json e salao_calibracao.json;
//   --validar: artifacts_equilibrio_geral/fase4/fabrica_salao_validacao.json
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { isMainThread } from "node:worker_threads";
import * as M from "../motor/index.ts";
import { R, R9, formasDe, lutador } from "./itens_ref.mjs";
import { criarPool, servir } from "./pool.mjs";

/* ------------------------------------------------------------------------------------------------ pets v6 (a conferencia de antes) */
function conferirV6() {
const { CIT, ESPECIES, ESTAGIOS_SALAO, LUTAS_SERIE_FABRICA, FATOR_FABRICA, FATOR_SALAO } = M;
M.ligarEscala(true);
const N_FABRICA = 2000, SEMENTES = [4101, 4202, 4303, 4404, 4505], N_SALAO = 20, N_SAVE = 50;
const r4 = x => +x.toFixed(4);
const ORDEM = ["furioso", "duelista", "espelho", "emboscador", "vigia", "sentinela", "tita", "muralha"];
const rank = f => ORDEM.indexOf(f.adulta);
const melhor = a => a.reduce((b, f, i) => (rank(f) < rank(a[b]) ? i : b), 0);

/* ---------------------------------------------------------------- Fabrica */
function resumoFabrica(tentativas) {
  const n = tentativas.length, lutas = tentativas.flatMap(t => t.lutas);
  const porLuta = [0, 1, 2].map(j => { const x = lutas.filter(l => l.k % LUTAS_SERIE_FABRICA === j); return { lutas: x.length, vence: r4(x.filter(l => l.venceu).length / x.length) }; });
  const series = tentativas.map(t => t.series);
  return { tentativas: n, vence_a_primeira: r4(tentativas.filter(t => t.lutas[0].venceu).length / n), vitorias_media: r4(tentativas.reduce((a, t) => a + t.vitorias, 0) / n),
    series_media: r4(series.reduce((a, b) => a + b, 0) / n), pelo_menos_uma_serie: r4(series.filter(s => s >= 1).length / n), maximo_de_series: Math.max(...series),
    vence_por_luta_da_serie: porLuta, lutas_no_limite: r4(lutas.filter(l => l.res.fim === "limite").length / lutas.length) };
}
function politica(escolher, trocar) {
  const ts = [];
  for (let n = 1; n <= N_FABRICA; n++) {
    const a = M.alugueisFabrica(M.sementeFabrica(n)), t = new M.TentativaFabrica(n, escolher(a));
    while (!t.acabou) {
      const l = t.lutar(t.proxima().s);
      if (!t.acabou && trocar(t, l)) t.trocar();
    }
    ts.push(t);
  }
  return resumoFabrica(ts);
}
/* variante NAO adotada (so relato, para a rodada de equilibrio): a troca entra inteira (a vida cheia do Mega novo) */
function trocaInteira(escolher, trocar) {
  const ts = [];
  for (let n = 1; n <= N_FABRICA; n++) {
    const s = M.sementeFabrica(n), al = M.alugueisFabrica(s), lutas = [];
    let a = al[escolher(al)], ini = null, k = 0;
    for (;;) {
      const riv = M.formaRivalFabrica(s, k), A = M.megaFabrica(a, "A"), res = M.jogarV2(A, M.megaFabrica(riv, "B"), M.sementeLutaFabrica(s, k), R, k % 3 ? ini : null, 1);
      lutas.push({ k, venceu: res.pontosA === 1, res });
      if (res.pontosA !== 1) break;
      ini = { hp: res.E.L[0].hp, guts: res.E.L[0].guts };
      if (trocar(a, riv)) { a = riv; ini = null; }
      k++;
    }
    const vitorias = lutas.filter(l => l.venceu).length;
    ts.push({ lutas, vitorias, series: Math.floor(vitorias / 3) });
  }
  return resumoFabrica(ts);
}
const fabrica = {
  primeiro_sem_troca: politica(() => 0, () => false),
  melhor_arquetipo_sem_troca: politica(melhor, () => false),
  melhor_arquetipo_troca_por_melhor: politica(melhor, (t, l) => rank(l.rival) < rank(t.alugado)),
  variante_nao_adotada_troca_inteira_por_melhor: trocaInteira(melhor, (a, riv) => rank(riv) < rank(a)),
  variante_nao_adotada_troca_inteira_sempre: trocaInteira(melhor, () => true),
};

/* ---------------------------------------------------------------- Salao */
function salaoEstagio(est, nivel) {
  const porForma = {};
  for (const fo of formasDe(est)) {
    let v = 0, tot = 0;
    for (const e of ESPECIES) {
      const A = lutador(fo, e, nivel, [], true);
      for (const s of SEMENTES) for (let k = 0; k < N_SALAO; k++) {
        const st = M.hashSemente("conferir-salao", est, s, A.nome, k);
        if (M.jogarV2(A, M.rivalSalao(st, est, R), st, R, null, 1).pontosA === 1) v++;
        tot++;
      }
    }
    porForma[fo[0]] = r4(v / tot);
  }
  const xs = Object.values(porForma), media = xs.reduce((a, b) => a + b, 0) / xs.length;
  const pior = Object.entries(porForma).sort((a, b) => a[1] - b[1])[0], melhorF = Object.entries(porForma).sort((a, b) => b[1] - a[1])[0];
  return { treino: nivel, media: r4(media), melhor: { forma: melhorF[0], vence: melhorF[1] }, pior: { forma: pior[0], vence: pior[1] }, por_forma: porForma };
}
const comTreino = Object.fromEntries(ESTAGIOS_SALAO.map(est => [est, salaoEstagio(est, CIT.tipico[est])]));
const semTreino = Object.fromEntries(ESTAGIOS_SALAO.map(est => [est, salaoEstagio(est, 0)]));
const produto = (f) => r4(ESTAGIOS_SALAO.reduce((p, est) => p * f(est), 1));
const sequencia = (tab, f) => ESTAGIOS_SALAO.map((_, j) => r4(ESTAGIOS_SALAO.slice(0, j + 1).reduce((p, est) => p * f(tab[est]), 1)));

/* os pets dos testes ponta a ponta: as primeiras lutas de cada um no Salao (a semente do registro) */
const SAVE_SALAO = JSON.parse(readFileSync(new URL("../e2e/save_salao.json", import.meta.url), "utf8")).guardados;
const SAVE_LIGA = JSON.parse(readFileSync(new URL("../e2e/save_liga.json", import.meta.url), "utf8"));
const doE2e = [...SAVE_SALAO, SAVE_LIGA].map(x => {
  const m = M.Motor.reproduzir(x.semente, x.log, x.versao);
  m.abrirFronteira();
  let v = 0;
  for (let n = 1; n <= N_SAVE; n++) if (m.montarLuta(M.RIVAL_SALAO, M.sementeSalao(m.semente, n)).serie[0].pontosA === 1) v++;
  return { pet: M.nomeForma(m.forma), nivel: M.NOME_EST[m.estagioAtual], treino: r4(m.treino.total), vence: r4(v / N_SAVE) };
});

const salao = {
  com_o_treino_tipico: comTreino,
  sem_treino: semTreino,
  vence_os_4_time_medio: produto(est => comTreino[est].media),
  vence_os_4_melhores_formas: produto(est => comTreino[est].melhor.vence),
  vence_os_4_piores_formas: produto(est => comTreino[est].pior.vence),
  chega_ao_nivel_time_medio: sequencia(comTreino, x => x.media),
  vence_os_4_sem_treino_time_medio: produto(est => semTreino[est].media),
  pets_do_e2e: doE2e,
};
const f = fabrica.melhor_arquetipo_troca_por_melhor;
const jogavel = { fabrica: f.vence_a_primeira >= .3 && f.pelo_menos_uma_serie > 0, salao: salao.vence_os_4_time_medio > 0 && Object.values(comTreino).every(x => x.media >= .5) };
const saida = {
  descricao: "Conferencia da Fabrica e do Salao da Fronteira (sem calibracao): jogaveis? Politicas simples na Fabrica; pets de referencia no Salao",
  motor: "web/app/motor (escala CESC_V6 ligada, regras V21D, limite do desafiado = o rival)",
  fator_fabrica: FATOR_FABRICA, fator_salao: FATOR_SALAO, tentativas_fabrica: N_FABRICA, sementes_salao: SEMENTES, lutas_por_semente_especie_forma_salao: N_SALAO,
  ordem_dos_arquetipos_da_politica: ORDEM,
  criterio_de_jogavel: "Fabrica: a politica do melhor arquetipo vence a 1a luta em >= 0,3 das tentativas e vence ao menos uma serie as vezes; Salao: todo nivel com media >= 0,5 com o treino tipico e o time medio vence os 4 as vezes",
  jogavel,
  fabrica, salao,
};
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/fronteira/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + "conferencia_4c.json", JSON.stringify(saida, null, 2) + "\n");
console.log("--- Fábrica");
for (const [k, x] of Object.entries(fabrica)) console.log(`${k}: vence a 1a ${x.vence_a_primeira}; séries média ${x.series_media}; >= 1 série ${x.pelo_menos_uma_serie}; máx ${x.maximo_de_series}; por luta ${x.vence_por_luta_da_serie.map(y => y.vence).join("/")}; limite ${x.lutas_no_limite}`);
console.log("--- Salão (treino típico / sem treino)");
for (const est of ESTAGIOS_SALAO) console.log(`${M.NOME_EST[est]}: média ${comTreino[est].media} (melhor ${comTreino[est].melhor.forma} ${comTreino[est].melhor.vence}, pior ${comTreino[est].pior.forma} ${comTreino[est].pior.vence}) / sem treino ${semTreino[est].media}`);
console.log(`vence os 4: time médio ${salao.vence_os_4_time_medio}; melhores ${salao.vence_os_4_melhores_formas}; piores ${salao.vence_os_4_piores_formas}; sem treino ${salao.vence_os_4_sem_treino_time_medio}`);
for (const x of doE2e) console.log(`e2e: ${x.pet} (${x.nivel}, treino ${x.treino}) vence ${x.vence}`);
console.log("jogável:", jogavel);
}

/* ------------------------------------------------------------------------------------------------ pets v9 */
const r4 = x => +x.toFixed(4);
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
const POR_SEMENTE = 400, LUTAS_MAX = 120, N_SALAO = 20;
const META_FABRICA = 0.25, FOLGA_FABRICA = 0.05, META_SALAO_MIN = 0.70, META_SALAO_MAX = 0.95;
const FATORES_FABRICA = Array.from({ length: 15 }, (_, i) => Math.round((0.3 + 0.05 * i) * 100) / 100);   /* 0,30..1,00 */
const FATORES_SALAO = Array.from({ length: 35 }, (_, i) => Math.round((0.3 + 0.05 * i) * 100) / 100);     /* 0,30..2,00 */
const ORDEM = ["furioso", "duelista", "espelho", "emboscador", "vigia", "sentinela", "tita", "muralha"];
const rank = f => ORDEM.indexOf(f.adulta);
const melhorAluguel = a => a.reduce((b, f, i) => (rank(f) < rank(a[b]) ? i : b), 0);
const POLITICAS = {
  melhor_arquetipo_troca_por_melhor: [melhorAluguel, (t, l) => rank(l.rival) < rank(t.alugado)],
  melhor_arquetipo_sem_troca: [melhorAluguel, () => false],
  primeiro_sem_troca: [() => 0, () => false],
};
const POLITICA_META = "melhor_arquetipo_troca_por_melhor";

/** a tarefa: as tentativas da Fabrica dos v9 de uma semente de calibracao, com uma politica e um fator dos rivais (null: o do motor) */
function tarefaFabrica(t) {
  M.ligarEscala(false);   /* a Fabrica vale sempre na escala (comEscala), sem depender da chave */
  const [escolher, trocar] = POLITICAS[t.politica], out = [];
  for (let i = 0; i < t.por; i++) {
    const s = M.hashSemente("conferir-fabrica", t.semente, i), x = new M.TentativaFabrica(i + 1, escolher(M.alugueisFabrica(s)), M.VERSAO_FABRICA_V9, s, t.fator ?? undefined);
    while (!x.acabou && x.lutas.length < LUTAS_MAX) {
      const l = x.lutar(x.proxima().s);
      if (!x.acabou && trocar(x, l)) x.trocar();
    }
    const porLuta = [0, 1, 2].map(j => { const ls = x.lutas.filter(l => l.k % M.LUTAS_SERIE_FABRICA === j); return [ls.length, ls.filter(l => l.venceu).length]; });
    out.push({ primeira: x.lutas[0].venceu, vitorias: x.vitorias, series: x.series, teto: !x.acabou, porLuta, limite: x.lutas.filter(l => l.res.fim === "limite").length, lutas: x.lutas.length });
  }
  return out;
}
/** a tarefa: a taxa de vitoria de uma forma de referencia no Salao dos v9, num nivel, com um treino e um fator (null: o do motor), nas
    sementes da tarefa (as de calibracao, ou as de validacao na fase 4) */
function tarefaSalao(t) {
  M.ligarEscala(true);
  const fo = formasDe(t.est, R9)[t.forma];
  let v = 0, tot = 0;
  for (const e of M.ESPECIES) {
    const A = lutador(fo, e, t.nivel, [], true, M.VERSAO_ESCALA_V9);
    for (const s of t.sementes) for (let k = 0; k < N_SALAO; k++) {
      const st = M.hashSemente("conferir-salao", t.est, s, A.nome, k);
      if (M.jogarV2(A, M.rivalSalao(st, t.est, R9, t.fator ?? undefined), st, R9, null, 1).pontosA === 1) v++;
      tot++;
    }
  }
  return v / tot;
}
const TRABALHOS = { fabrica: tarefaFabrica, salao: tarefaSalao };

function resumoFabrica(ts) {
  const n = ts.length, series = ts.map(t => t.series), lutas = ts.reduce((a, t) => a + t.lutas, 0);
  const porLuta = [0, 1, 2].map(j => { const [l, v] = ts.reduce((a, t) => [a[0] + t.porLuta[j][0], a[1] + t.porLuta[j][1]], [0, 0]); return { lutas: l, vence: l ? r4(v / l) : null }; });
  const serie1 = series.filter(s => s >= 1).length / n;
  return { tentativas: n, vence_a_primeira: r4(ts.filter(t => t.primeira).length / n), vitorias_media: r4(ts.reduce((a, t) => a + t.vitorias, 0) / n),
    series_media: r4(series.reduce((a, b) => a + b, 0) / n), pelo_menos_uma_serie: r4(serie1), maximo_de_series: Math.max(...series),
    no_teto: ts.filter(t => t.teto).length, vence_por_luta_da_serie: porLuta, lutas_no_limite: r4(ts.reduce((a, t) => a + t.limite, 0) / lutas) };
}

async function v9(calibrar, validar) {
  if (calibrar && validar) throw new Error("--calibrar e --validar juntos");
  const sementes = validar ? SEM_VALIDACAO : SEM_CALIBRACAO, conjunto = validar ? "validacao" : "calibracao";
  const pool = criarPool(new URL(import.meta.url));
  const t0 = performance.now(), relogio = () => `${((performance.now() - t0) / 1000).toFixed(0)} s`;
  async function fabrica(politica, fatores) {
    const tar = fatores.flatMap(fator => sementes.map(semente => ({ tipo: "fabrica", politica, fator, semente, por: POR_SEMENTE })));
    const r = await pool.executar(tar);
    return fatores.map((_, i) => resumoFabrica(r.slice(i * sementes.length, (i + 1) * sementes.length).flat()));
  }
  async function salao(fatorDe, niveis) {
    const tar = [], idx = [];
    for (const est of M.ESTAGIOS_SALAO) for (const nivel of niveis(est)) for (const fator of fatorDe(est)) formasDe(est, R9).forEach((fo, f) => {
      tar.push({ tipo: "salao", est, forma: f, nivel, fator, sementes }); idx.push([est, nivel, fator, fo[0]]);
    });
    const r = await pool.executar(tar), out = {};
    idx.forEach(([est, nivel, fator, fo], i) => { ((out[est] ??= {})[nivel] ??= {})[fator ?? "motor"] ??= {}; out[est][nivel][fator ?? "motor"][fo] = r4(r[i]); });
    return out;
  }
  const resumoSalao = por => {
    const xs = Object.entries(por), media = xs.reduce((a, [, v]) => a + v, 0) / xs.length, ord = [...xs].sort((a, b) => a[1] - b[1]);
    return { media: r4(media), pior: { forma: ord[0][0], vence: ord[0][1] }, melhor: { forma: ord[ord.length - 1][0], vence: ord[ord.length - 1][1] },
      folga: r4(Math.min(media - META_SALAO_MIN, META_SALAO_MAX - media)), passa: media >= META_SALAO_MIN && media <= META_SALAO_MAX, por_forma: por };
  };
  const pasta = fileURLToPath(new URL(validar ? "../../../artifacts_equilibrio_geral/fase4/" : "../../../artifacts_equilibrio_geral/fase3/", import.meta.url));
  mkdirSync(pasta, { recursive: true });
  const gravar = (nome, o) => writeFileSync(pasta + nome, JSON.stringify(o, null, 1) + "\n");
  const cab = { conjunto, sementes };
  if (calibrar) {
    /* a Fabrica: a grade do fator dos rivais, na politica da meta */
    const med = (await fabrica(POLITICA_META, FATORES_FABRICA)).map((x, i) => ({ fator: FATORES_FABRICA[i], ...x, folga: r4(x.pelo_menos_uma_serie - META_FABRICA) }));
    for (const x of med) console.log(`Fábrica fator ${x.fator}: 1a ${x.vence_a_primeira}; >= 1 série ${x.pelo_menos_uma_serie}; séries ${x.series_media}; teto ${x.no_teto} [${relogio()}]`);
    const ok = med.filter(x => x.folga >= FOLGA_FABRICA), esc = ok.length ? ok.reduce((a, b) => b.fator > a.fator ? b : a) : med.reduce((a, b) => b.folga > a.folga ? b : a);
    gravar("fabrica_calibracao.json", { descricao: "Calibracao da Fabrica dos pets v9 (fase 3, meta M-C2): o fator dos rivais, com a troca entrando inteira e as regras V21E",
      ...cab, tentativas_por_semente: POR_SEMENTE, teto_de_lutas: LUTAS_MAX, meta: { pelo_menos_uma_serie_min: META_FABRICA }, folga_minima: FOLGA_FABRICA,
      politica: POLITICA_META, ordem_dos_arquetipos: ORDEM, regra: "o maior fator com folga >= folga_minima (o mais perto de 1)", grade: FATORES_FABRICA,
      escolha: { fator: esc.fator, pelo_menos_uma_serie: esc.pelo_menos_uma_serie, folga: esc.folga, passa: esc.folga >= 0 }, medidas: med });
    console.log("Fábrica, escolha:", esc.fator, esc.pelo_menos_uma_serie);
    /* o Salao: a grade do fator de cada nivel, com o treino tipico */
    const s = await salao(() => FATORES_SALAO, est => [M.CIT.tipico[est]]);
    const niveis = {};
    for (const est of M.ESTAGIOS_SALAO) {
      const medS = FATORES_SALAO.map(f => ({ fator: f, ...resumoSalao(s[est][M.CIT.tipico[est]][f]) }));
      medS.forEach((x, i) => { x.folga_robusta = r4(Math.min(x.folga, medS[i - 1]?.folga ?? x.folga, medS[i + 1]?.folga ?? x.folga)); });
      const cands = medS.filter(x => x.fator >= 1), escS = cands.reduce((a, b) => b.folga_robusta > a.folga_robusta ? b : a);
      const puro = medS.reduce((a, b) => b.folga > a.folga ? b : a);
      niveis[est] = { treino: M.CIT.tipico[est], escolha: { fator: escS.fator, media: escS.media, folga: escS.folga, folga_robusta: escS.folga_robusta,
        passa: escS.passa, pior: escS.pior }, maior_folga_sem_restricao: { fator: puro.fator, media: puro.media, folga: puro.folga },
        medidas: medS.map(({ por_forma, ...x }) => x) };
      console.log(`Salão ${est}: fator ${escS.fator} média ${escS.media} folga ${escS.folga} [${relogio()}]`);
    }
    gravar("salao_calibracao.json", { descricao: "Calibracao do Salao dos pets v9 (fase 3, meta M-C3): o fator do rival de cada nivel, regras V21E, escala CESC_V9",
      ...cab, lutas_por_semente_especie_forma: N_SALAO, meta: { min: META_SALAO_MIN, max: META_SALAO_MAX }, regra: "fator >= 1; entre eles, a maior folga robusta (a menor folga entre o fator e os dois vizinhos da grade)",
      grade: FATORES_SALAO, niveis });
  } else {
    /* a Fabrica e o Salao dos v9 como o motor os joga */
    const fab = {};
    for (const p of Object.keys(POLITICAS)) fab[p] = (await fabrica(p, [null]))[0];
    const meta2 = fab[POLITICA_META].pelo_menos_uma_serie;
    const s = await salao(() => [null], est => [M.CIT.tipico[est], 0]);
    const com = Object.fromEntries(M.ESTAGIOS_SALAO.map(est => [est, { fator: M.fatorSalao(est, R9), treino: M.CIT.tipico[est], ...resumoSalao(s[est][M.CIT.tipico[est]].motor) }]));
    const sem = Object.fromEntries(M.ESTAGIOS_SALAO.map(est => [est, resumoSalao(s[est][0].motor).media]));
    const produto = f => r4(M.ESTAGIOS_SALAO.reduce((p, est) => p * f(est), 1));
    const saida = {
      descricao: validar ? "Validacao da Fabrica e do Salao dos pets v9 (fase 4, metas M-C2 e M-C3): as regras do motor, tudo congelado, nas sementes de validacao"
        : "Conferencia da Fabrica e do Salao dos pets v9 (fase 3, metas M-C2 e M-C3): as regras do motor",
      motor: "web/app/motor (regras V21E; Fabrica: TentativaFabrica versao 9, a troca com a vida cheia; Salao: escala CESC_V9, fatorSalao; limite do desafiado = o rival)",
      ...cab,
      fabrica: { fator_rivais: M.FATOR_RIVAL_FABRICA_V9, fator_alugados: M.FATOR_FABRICA, troca_inteira: M.regraFabrica(M.VERSAO_FABRICA_V9).trocaInteira,
        tentativas_por_semente: POR_SEMENTE, teto_de_lutas: LUTAS_MAX, ordem_dos_arquetipos: ORDEM, politica_da_meta: POLITICA_META,
        meta_c2: { pelo_menos_uma_serie: meta2, min: META_FABRICA, folga: r4(meta2 - META_FABRICA), passa: meta2 >= META_FABRICA }, politicas: fab },
      salao: { lutas_por_semente_especie_forma: N_SALAO, meta_c3: { min: META_SALAO_MIN, max: META_SALAO_MAX, passa: Object.values(com).every(x => x.passa),
        menor_folga: r4(Math.min(...Object.values(com).map(x => x.folga))) }, com_o_treino_tipico: com, sem_treino: sem,
        vence_os_4_time_medio: produto(est => com[est].media), vence_os_4_sem_treino_time_medio: produto(est => sem[est]) },
    };
    gravar(validar ? "fabrica_salao_validacao.json" : "fabrica_salao_conferencia.json", saida);
    for (const [k, x] of Object.entries(fab)) console.log(`Fábrica ${k}: 1a ${x.vence_a_primeira}; >= 1 série ${x.pelo_menos_uma_serie}; séries ${x.series_media}; máx ${x.maximo_de_series}; teto ${x.no_teto}`);
    for (const est of M.ESTAGIOS_SALAO) console.log(`Salão ${est} (fator ${com[est].fator}): média ${com[est].media} (pior ${com[est].pior.forma} ${com[est].pior.vence}) folga ${com[est].folga}; sem treino ${sem[est]}`);
    console.log("M-C2:", JSON.stringify(saida.fabrica.meta_c2), "M-C3:", JSON.stringify(saida.salao.meta_c3));
  }
  console.log(`[${relogio()}]`);
  await pool.fechar();
}

const args = process.argv.slice(2);
if (!isMainThread) servir(TRABALHOS);
else if (args.includes("--v6")) conferirV6();
else await v9(args.includes("--calibrar"), args.includes("--validar"));
