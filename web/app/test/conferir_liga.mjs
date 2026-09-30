// Conferencia da Liga dos Lideres (docs/DESIGN_FRONTEIRA.md, secao 2; medalhas parte 4a) e, desde a rodada de equilibrio geral (fase 3;
// docs/PLANO_EQUILIBRIO_GERAL.md, meta M-C1), a calibracao da Liga dos pets v9.
//
// --v6: a conferencia de antes, SEM calibracao (decisao do Matheus: sem rodada de equilibrio na parte 4a): so confere que o jogo e
// completavel, ou seja, que um Mega bem treinado, com a forma certa para cada confronto, vence cada luta da Liga. Reproduz o artefato
// gravado (artifacts_campanha/liga/conferencia.json) byte a byte.
// Metodo (o dos lideres da parte 2, test/itens_ref.mjs): motor web, escala dos pets v6 ligada, regras V21D, a regra do limite do
// desafiado (o lider); o pet de referencia = cada uma das 8 formas no Mega, nas 4 especies, com o treino tipico do Mega (40, uniforme),
// sem chip e sem carta, como lado A. Os rivais = os Megas da Liga (motor/liga.ts), com o fator do Piedmon da Espiral.
// - por luta: o pet inteiro contra cada lider (a taxa de vitoria por forma, media das especies);
// - a Liga inteira: as 6 lutas seguidas, sem cura (arenas.jogarSerie, como o motor joga), a taxa de titulos por forma.
// Sementes de validacao da parte 2 (4101...4505), N partidas por semente, especie e forma. Dois fatores dos rivais: o do desenho (o do
// Piedmon na arena da Espiral) e o adotado (motor/liga.ts, FATOR_LIGA); mais dois no meio, so como relato.
//
// Pets v9 (padrao): o mesmo metodo com as regras das lutas dos pets v9 (combate V21E, CV21E: as listas V21E nas formas de referencia e
// nos Megas dos lideres), a escala da versao 9 (CESC_V9, a mesma vida do Mega) e a Liga dos v9 do motor (liga.FATOR_LIGA_V9, um fator
// por lider, e liga.CURA_LIGA_V9, a cura parcial entre as lutas; liga.jogarLiga), nas sementes de calibracao (3101...3505). Meta M-C1: com o
// treino tipico do Mega (40), toda forma com chance de titulo >= 0,25 e nenhuma > 0,85 (titulos por forma: media das 4 especies).
// --calibrar: a busca dos fatores e da cura (as alavancas da secao 3 do plano: fatores dos rivais da Liga e a estrutura, a cura parcial
// entre as lutas). Para cada cura da grade CURAS, busca por coordenadas (lider a lider, todos os fatores da grade FATORES com os outros
// fixos, ate nao melhorar) com N_BUSCA partidas por semente, especie e forma, a partir de INICIOS pontos (todos em 1 e INICIOS - 1
// sorteados da grade por uma rng com semente fixa); o fim de cada busca e medido de novo com N e a escolhida e a melhor delas. Ordem (registrada antes de rodar): 1) mais formas dentro da faixa [0,25; 0,85]; 2) a menor soma do
// que falta as formas de fora ate a faixa; 3) a menor cura; 4) os fatores mais perto de 1 (a soma de |fator - 1|).
// uso (em web/app): npx tsx test/conferir_liga.mjs [--v6 | --calibrar]
//   --v6: artifacts_campanha/liga/conferencia.json; padrao: artifacts_equilibrio_geral/fase3/liga_conferencia.json;
//   --calibrar: artifacts_equilibrio_geral/fase3/liga_calibracao.json
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { isMainThread } from "node:worker_threads";
import * as M from "../motor/index.ts";
import { R, R9, formasDe, lutador } from "./itens_ref.mjs";
import { criarPool, servir } from "./pool.mjs";

const { CIT, ESPECIES, LIGA, NPC, FATOR_LIGA, FATOR_LIGA_DESENHO } = M;
M.ligarEscala(true);
const TIPICO = CIT.tipico.mega;

/* ------------------------------------------------------------------------------------------------ pets v6 (a conferencia de antes) */
function conferirV6() {
const SEMENTES = [4101, 4202, 4303, 4404, 4505], N = 20;
const formas = formasDe("mega");
const r4 = x => +x.toFixed(4);
const FATORES = [...new Set([FATOR_LIGA_DESENHO, 1.4, 1.2, FATOR_LIGA])];
function conferir(fator) {
const lideres = M.lutadoresLiga(R, fator);

/* por luta: o pet inteiro contra cada lider */
const porLuta = LIGA.map((x, i) => {
  const porForma = {};
  for (const fo of formas) {
    let v = 0, tot = 0;
    for (const e of ESPECIES) {
      const A = lutador(fo, e, TIPICO, [], true);
      for (const s of SEMENTES) for (let k = 0; k < N; k++) {
        v += M.jogarV2(A, lideres[i], M.hashSemente("conferir-liga", s, A.nome, i, k), R, null, 1).pontosA === 1 ? 1 : 0; tot++;
      }
    }
    porForma[fo[0]] = r4(v / tot);
  }
  const melhor = Object.entries(porForma).sort((a, b) => b[1] - a[1])[0];
  return { luta: i + 1, lider: NPC[x.lider].nome, mega: M.nomeMegaLiga(i), arquetipo: M.NOME_ARQ[x.adulta], especie: M.NOME_ESP[x.esp],
    melhor_forma: melhor[0], melhor_taxa: melhor[1], por_forma: porForma };
});
/* a Liga inteira: as 6 lutas seguidas, sem cura */
const liga = {};
for (const fo of formas) {
  let titulos = 0, tot = 0;
  const chegou = Array(LIGA.length).fill(0);
  for (const e of ESPECIES) {
    const A = lutador(fo, e, TIPICO, [], true);
    for (const s of SEMENTES) for (let k = 0; k < N; k++) {
      const serie = M.jogarSerie(A, lideres, M.hashSemente("conferir-liga-serie", s, A.nome, k), R, 1, null);
      serie.forEach((_, j) => chegou[j]++);
      if (serie.length === LIGA.length && serie[serie.length - 1].pontosA === 1) titulos++;
      tot++;
    }
  }
  liga[fo[0]] = { titulos: r4(titulos / tot), chegou_na_luta: chegou.map(c => r4(c / tot)) };
}
const melhor = Object.entries(liga).sort((a, b) => b[1].titulos - a[1].titulos)[0];
return { fator, por_luta: porLuta, liga_inteira: liga, vencivel_cada_luta: porLuta.every(x => x.melhor_taxa > 0),
  liga_completavel: melhor[1].titulos > 0, melhor_forma_na_liga: { forma: melhor[0], titulos: melhor[1].titulos } };
}
const porFator = FATORES.map(conferir);
const saida = {
  descricao: "Conferencia da Liga dos Lideres (sem calibracao): o Mega de referencia com o treino tipico contra cada lider e a Liga inteira",
  motor: "web/app/motor (escala CESC_V6 ligada, regras V21D, limite do desafiado = o lider)",
  fator_desenho: FATOR_LIGA_DESENHO, fator_adotado: FATOR_LIGA, treino_tipico_mega: TIPICO, sementes: SEMENTES, partidas_por_semente_especie_forma: N,
  por_fator: porFator,
};
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/liga/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + "conferencia.json", JSON.stringify(saida, null, 2) + "\n");
for (const c of porFator) {
  console.log(`--- fator ${c.fator}: cada luta vencivel ${c.vencivel_cada_luta}; Liga completavel ${c.liga_completavel} (melhor ${c.melhor_forma_na_liga.forma} ${c.melhor_forma_na_liga.titulos})`);
  for (const x of c.por_luta) console.log(`${x.luta}. ${x.lider} (${x.mega} · ${x.arquetipo}): melhor ${x.melhor_forma} ${x.melhor_taxa}`, JSON.stringify(x.por_forma));
  for (const [f, x] of Object.entries(c.liga_inteira)) console.log(`Liga inteira, ${f}: títulos ${x.titulos}; chegou`, x.chegou_na_luta.join(" "));
}
}

/* ------------------------------------------------------------------------------------------------ pets v9 */
const r4 = x => +x.toFixed(4);
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505];
const META_MIN = 0.25, META_MAX = 0.85;
const N = 20, N_BUSCA = 5;
const FATORES = Array.from({ length: 30 }, (_, i) => Math.round((0.1 + 0.1 * i) * 10) / 10);   /* 0,1..3,0 */
const CURAS = [0, 0.1, 0.2, 0.3, 0.4, 0.5];
const INICIOS = 8;
const formas9 = formasDe("mega", R9);

/** a tarefa: a Liga inteira de uma forma (as 4 especies), com os fatores e a cura dados (null: os do motor) */
function tarefaLiga(t) {
  M.ligarEscala(true);
  const fo = formas9[t.forma], lideres = t.fatores ? M.lutadoresLiga(R9, t.fatores) : M.lutadoresLiga(R9), cura = t.cura ?? M.curaLiga(R9);
  let titulos = 0, tot = 0;
  const chegou = Array(LIGA.length).fill(0), venceu = Array(LIGA.length).fill(0);
  for (const e of ESPECIES) {
    const A = lutador(fo, e, TIPICO, [], true, M.VERSAO_ESCALA_V9);
    for (const s of t.sementes) for (let k = 0; k < t.n; k++) {
      const serie = M.jogarLiga(A, M.hashSemente("conferir-liga-serie", s, A.nome, k), R9, 1, lideres, cura);
      serie.forEach((r, j) => { chegou[j]++; if (r.pontosA === 1) venceu[j]++; });
      if (serie.length === LIGA.length && serie[serie.length - 1].pontosA === 1) titulos++;
      tot++;
    }
  }
  return { titulos: titulos / tot, chegou: chegou.map(c => c / tot), venceu_dado_que_chegou: venceu.map((v, j) => chegou[j] ? v / chegou[j] : null) };
}
/** a tarefa: o pet inteiro contra um lider (a taxa por forma, as 4 especies), com o fator do motor */
function tarefaLuta(t) {
  M.ligarEscala(true);
  const fo = formas9[t.forma], B = M.lutadorLiga(t.lider, R9);
  let v = 0, tot = 0;
  for (const e of ESPECIES) {
    const A = lutador(fo, e, TIPICO, [], true, M.VERSAO_ESCALA_V9);
    for (const s of t.sementes) for (let k = 0; k < t.n; k++) {
      v += M.jogarV2(A, B, M.hashSemente("conferir-liga", s, A.nome, t.lider, k), R9, null, 1).pontosA === 1 ? 1 : 0; tot++;
    }
  }
  return v / tot;
}
const TRABALHOS = { liga: tarefaLiga, luta: tarefaLuta };

/** a meta M-C1 sobre os titulos por forma */
function metaC1(titulos) {
  const xs = Object.values(titulos), mn = Math.min(...xs), mx = Math.max(...xs);
  const falta = xs.reduce((a, t) => a + Math.max(0, META_MIN - t) + Math.max(0, t - META_MAX), 0);
  return { min: r4(mn), forma_min: Object.keys(titulos).find(k => titulos[k] === mn), max: r4(mx), forma_max: Object.keys(titulos).find(k => titulos[k] === mx),
    na_faixa: xs.filter(t => t >= META_MIN && t <= META_MAX).length, falta_ate_a_faixa: r4(falta),
    folga: r4(Math.min(mn - META_MIN, META_MAX - mx)), passa: mn >= META_MIN && mx <= META_MAX };
}
/** a ordem da calibracao: 1) mais formas na faixa; 2) menos falta; 3) menos cura; 4) fatores mais perto de 1 */
const distancia1 = fs => fs.reduce((a, f) => a + Math.abs(f - 1), 0);
function melhor(a, b) {
  if (a.meta.na_faixa !== b.meta.na_faixa) return a.meta.na_faixa > b.meta.na_faixa ? a : b;
  if (Math.abs(a.meta.falta_ate_a_faixa - b.meta.falta_ate_a_faixa) > 1e-9) return a.meta.falta_ate_a_faixa < b.meta.falta_ate_a_faixa ? a : b;
  if (a.cura !== b.cura) return a.cura < b.cura ? a : b;
  return distancia1(b.fatores) < distancia1(a.fatores) - 1e-9 ? b : a;
}

async function v9(calibrar) {
  const pool = criarPool(new URL(import.meta.url));
  const t0 = performance.now(), relogio = () => `${((performance.now() - t0) / 1000).toFixed(0)} s`;
  /** mede as configuracoes (fatores, cura) com n partidas: os titulos por forma e a meta */
  async function medir(configs, n) {
    const tarefas = configs.flatMap(c => formas9.map((_, f) => ({ tipo: "liga", forma: f, fatores: c.fatores, cura: c.cura, sementes: SEM_CALIBRACAO, n })));
    const r = await pool.executar(tarefas);
    return configs.map((c, i) => {
      const por = Object.fromEntries(formas9.map((fo, f) => [fo[0], r[i * formas9.length + f]]));
      const titulos = Object.fromEntries(Object.entries(por).map(([k, x]) => [k, r4(x.titulos)]));
      return { ...c, titulos, meta: metaC1(titulos), por_forma: por };
    });
  }
  let out;
  if (calibrar) {
    const buscas = [];
    for (const cura of CURAS) for (let ini = 0; ini < INICIOS; ini++) {
      const rng = M.criarRng(M.hashSemente("liga-calibracao", cura, ini));
      const inicio = ini === 0 ? LIGA.map(() => 1) : LIGA.map(() => FATORES[rng.int(FATORES.length)]);
      let atual = (await medir([{ fatores: inicio, cura }], N_BUSCA))[0];
      const passos = [];
      for (let volta = 0, mudou = true; mudou && volta < 8; volta++) {
        mudou = false;
        for (let l = 0; l < LIGA.length; l++) {
          const cands = FATORES.map(f => ({ fatores: atual.fatores.map((x, j) => j === l ? f : x), cura }));
          const med = await medir(cands, N_BUSCA);
          const esc = med.reduce((a, b) => melhor(a, b), atual);
          if (esc !== atual) { mudou = true; atual = esc; passos.push({ volta, lider: LIGA[l].arena, fatores: atual.fatores, meta: atual.meta }); }
        }
        console.log(`cura ${cura} inicio ${ini} volta ${volta}: fatores ${atual.fatores.join(" ")} na faixa ${atual.meta.na_faixa} falta ${atual.meta.falta_ate_a_faixa} [${relogio()}]`);
      }
      const final = (await medir([{ fatores: atual.fatores, cura }], N))[0];
      buscas.push({ cura, inicio, busca: { n: N_BUSCA, fatores: atual.fatores, titulos: atual.titulos, meta: atual.meta }, passos,
        com_n: { n: N, fatores: final.fatores, titulos: final.titulos, meta: final.meta } });
      console.log(`  cura ${cura} inicio ${ini} com n=${N}: ${JSON.stringify(final.titulos)} ${JSON.stringify(final.meta)}`);
    }
    const esc = buscas.map(b => ({ fatores: b.com_n.fatores, cura: b.cura, meta: b.com_n.meta })).reduce((a, b) => melhor(a, b));
    out = {
      descricao: "Calibracao da Liga dos Lideres dos pets v9 (rodada de equilibrio geral, fase 3, meta M-C1): fatores por lider e cura parcial entre as lutas",
      motor: "web/app/motor (escala CESC_V9 ligada, regras V21E, limite do desafiado = o lider; liga.jogarLiga)",
      conjunto: "calibracao", sementes: SEM_CALIBRACAO, treino_tipico_mega: TIPICO, n_busca: N_BUSCA, n: N,
      metas: { titulo_min: META_MIN, titulo_max: META_MAX }, grade_fatores: FATORES, grade_curas: CURAS, inicios: INICIOS,
      ordem: "1) mais formas na faixa; 2) menor soma do que falta ate a faixa; 3) menor cura; 4) fatores mais perto de 1",
      lideres: LIGA.map(x => x.arena), escolha: { fatores: Object.fromEntries(LIGA.map((x, i) => [x.arena, esc.fatores[i]])), cura: esc.cura, meta: esc.meta },
      buscas,
    };
    console.log("escolha:", JSON.stringify(out.escolha));
  } else {
    /* a Liga dos v9 como o motor a joga (fatores e cura do motor) */
    const [liga, antes] = await medir([{ fatores: null, cura: null }, { fatores: LIGA.map(() => FATOR_LIGA), cura: 0 }], N);
    const tarefas = LIGA.flatMap((_, i) => formas9.map((_, f) => ({ tipo: "luta", forma: f, lider: i, sementes: SEM_CALIBRACAO, n: N })));
    const r = await pool.executar(tarefas);
    const porLuta = LIGA.map((x, i) => {
      const por = Object.fromEntries(formas9.map((fo, f) => [fo[0], r4(r[i * formas9.length + f])]));
      const ord = Object.entries(por).sort((a, b) => b[1] - a[1]);
      return { luta: i + 1, lider: NPC[x.lider].nome, mega: M.nomeMegaLiga(i), arquetipo: M.NOME_ARQ[x.adulta], fator: M.fatorLiga(i, R9),
        melhor_forma: ord[0][0], melhor_taxa: ord[0][1], pior_forma: ord[ord.length - 1][0], pior_taxa: ord[ord.length - 1][1], por_forma: por };
    });
    out = {
      descricao: "Conferencia da Liga dos Lideres dos pets v9 (rodada de equilibrio geral, fase 3, meta M-C1): a Liga do motor, o Mega de referencia com o treino tipico",
      motor: "web/app/motor (escala CESC_V9 ligada, regras V21E, limite do desafiado = o lider; liga.jogarLiga com FATOR_LIGA_V9 e CURA_LIGA_V9)",
      conjunto: "calibracao", sementes: SEM_CALIBRACAO, treino_tipico_mega: TIPICO, partidas_por_semente_especie_forma: N,
      metas: { titulo_min: META_MIN, titulo_max: META_MAX },
      fatores: Object.fromEntries(LIGA.map((x, i) => [x.arena, M.fatorLiga(i, R9)])), cura_entre_lutas: M.curaLiga(R9),
      meta_c1: liga.meta, titulos: liga.titulos,
      relato_fator_de_antes: { descricao: "a mesma Liga dos v9 (regras V21E) com o fator de antes (FATOR_LIGA nos 6, sem cura)", titulos: antes.titulos, meta_c1: antes.meta },
      liga_inteira: Object.fromEntries(Object.entries(liga.por_forma).map(([k, x]) => [k, { titulos: r4(x.titulos), chegou_na_luta: x.chegou.map(r4),
        venceu_dado_que_chegou: x.venceu_dado_que_chegou.map(v => v === null ? null : r4(v)) }])),
      por_luta: porLuta,
    };
    for (const x of porLuta) console.log(`${x.luta}. ${x.lider} (${x.mega} · ${x.arquetipo}, fator ${x.fator}): melhor ${x.melhor_forma} ${x.melhor_taxa}; pior ${x.pior_forma} ${x.pior_taxa}`);
    for (const [f, x] of Object.entries(out.liga_inteira)) console.log(`Liga inteira, ${f}: títulos ${x.titulos}; chegou`, x.chegou_na_luta.join(" "));
    console.log("M-C1:", JSON.stringify(out.meta_c1));
  }
  const pasta = fileURLToPath(new URL("../../../artifacts_equilibrio_geral/fase3/", import.meta.url));
  mkdirSync(pasta, { recursive: true });
  writeFileSync(pasta + (calibrar ? "liga_calibracao.json" : "liga_conferencia.json"), JSON.stringify(out, null, 1) + "\n");
  console.log(`[${relogio()}]`);
  await pool.fechar();
}

const args = process.argv.slice(2);
if (!isMainThread) servir(TRABALHOS);
else if (args.includes("--v6")) conferirV6();
else await v9(args.includes("--calibrar"));
