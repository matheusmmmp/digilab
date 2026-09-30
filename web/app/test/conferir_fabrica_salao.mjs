// Conferencia da Fabrica e do Salao da Fronteira (docs/DESIGN_FRONTEIRA.md, secao 3; medalhas parte 4c). SEM calibracao (decisao do
// Matheus: sem rodada de equilibrio nesta parte): so confere que as duas sao jogaveis e relata. Nenhum numero do jogo sai daqui.
//
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
// uso (em web/app): npx tsx test/conferir_fabrica_salao.mjs  ->  artifacts_campanha/fronteira/conferencia_4c.json
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";
import { R, formasDe, lutador } from "./itens_ref.mjs";

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
