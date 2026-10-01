// Medicao dos itens (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13.7).
// NAO RODADA NESTA PARTE: decisao do Matheus (2026-09-30) de nao equilibrar a cada etapa; os itens entraram sem equilibrio, e esta
// medicao fica pronta para a rodada de equilibrio geral do combate (depois das proximas mecanicas).
//
// Gates G-I1 a G-I4, no motor web, com as regras das lutas dos pets v6 (V21D), a escala dos pets v6 e a regra do limite do desafiado, pelos metodos da parte 2
// (test/calibrar_arenas.mjs e test/calibrar_escala_v6.mjs: os mesmos pets de referencia, nomes e sementes de luta, entao a linha
// "sem item" e a da parte 2 e os itens usam numeros aleatorios comuns).
//
// "Melhor combinacao" (secao 13.7): o maximo, POR FORMA, entre todas as combinacoes de ate 3 chips que servem no estagio (um Tamer
// com as 6 medalhas: 3 vagas) com nenhuma carta ou uma das cartas. Os chips de regra entram como no pet recem-equipado
// (itens.listaComChips): cada um vai ao topo, na ordem em que e equipado; a ordem conta, entao as combinacoes sao ordenadas.
//
//   G-I1: o pet SEM treino com a melhor combinacao contra cada um dos 6 lideres: media das formas <= 0,05 (relata a pior forma);
//   G-I2: metas de estagio da escala v6 com o de baixo (treino tipico) com a melhor combinacao (por forma de baixo, a que da mais
//         pontos contra as formas de cima) e o de cima sem treino e sem item: vizinhos <= 0,10 em pontos, dois estagios = 0 vitorias;
//   G-I3: matriz das 8 formas adultas (bots canonicos, V21D, mesma especie dos dois lados, eps 0,05, 100 partidas por par por
//         semente e especie, lados trocados na metade, sem escala), a forma medida com a melhor combinacao e as outras sem item: forca
//         <= 0,60, exceto o furioso. Limite de turnos pela fracao de vida, como a matriz da validacao V21D (docs/VALIDACAO_V21D.md),
//         de onde vem a faixa [0,40; 0,60]; relata tambem com a regra do limite do desafiado (a forma medida desafia, como o pet);
//   G-I4 (relato): cada chip de regra sozinho, o ganho de forca de cada forma adulta e o ganho contra os lideres do nivel (treino
//         tipico), nas formas em que o chip serve.
//
// Com --validar confere a linha "sem item" contra os artefatos de validacao da parte 2 (arenas e escala v6): tem de sair igual.
//
// Pets v9 (rodada de equilibrio geral, fase 3; docs/PLANO_EQUILIBRIO_GERAL.md, metas M-D1 a M-D3 = G-I1 a G-I3): por padrao a medicao e a
// dos pets v9: regras V21E (CV21E), a escala da versao 9 (CESC_V9), os fatores dos lideres dos v9 (FATOR_LIDER_V9) e os itens como valem
// nos pets v9 (itens.ts, pela versao). Metas da rodada: M-D1 = G-I1; M-D2 = G-I2; M-D3 = G-I3 SEM a excecao do furioso (a fase 1 o
// trouxe para a faixa). A linha "sem item" nas sementes de calibracao e conferida contra a fase 2 (arenas_conferencia.json: sem e com o
// treino tipico; escala_conferencia.json: as metas de estagio): tem de sair igual. --v6: a medicao de antes (pets v6, V21D, CESC_V6, os
// fatores de ARENAS, os itens de antes, a excecao do furioso), na pasta de antes; nas sementes de calibracao a linha "sem item" e
// conferida contra a dos v6 da fase 2 (v6_arenas_conferencia.json).
//
// uso (em web/app): node test/medir_itens.mjs [--v6] [--validar] [--gates gi1,gi2,gi3,gi4] [--sem-itens id,id] [--saida nome]
//   sem --validar: sementes de calibracao -> artifacts_equilibrio_geral/fase3/itens_calibracao.json (v9) ou
//     artifacts_campanha/itens/calibracao.json (--v6)
//   --validar: sementes de validacao -> artifacts_equilibrio_geral/fase4/itens_validacao.json (v9; so na fase 4) ou
//     artifacts_campanha/itens/validacao.json (--v6)
//   --sem-itens: tira itens do catalogo (explorar um item fora); --saida: o nome do arquivo (explorar sem sobrescrever)
//   --itens-v6 (so nos v9): os itens de antes (sem trava, chip de regra no topo, chip de stat inteiro, carta em toda luta) nas regras e
//     nos fatores dos v9, para comparar -> itens_calibracao_itens_v6.json
import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";
import { availableParallelism } from "node:os";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";
import { N_ESTAGIO, N_LIDER, N_MATRIZ, TRABALHOS, formasDe } from "./itens_ref.mjs";

const { ARENAS, CIT, ITENS, LUGARES_V6, NPC } = M;
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
const META_SEM = 0.05, META_VIZINHO = 0.10, META_DOIS = 0.0, META_FORCA = 0.60;
const VIZINHOS = [["crianca", "adolescente"], ["adolescente", "adulto"], ["adulto", "mega"]];
const DOIS = [["crianca", "adulto"], ["adolescente", "mega"]];
const TIPICO = CIT.tipico;


if (!isMainThread) {
  for (const id of workerData.semItens) if (!M.ITEM_POR_ID[id]) throw new Error("item desconhecido: " + id);
  parentPort.on("message", ({ i, t }) => parentPort.postMessage({ i, r: TRABALHOS[t.tipo](t) }));
} else await principal();

/* ------------------------------------------------ o processo principal */
async function principal() {
  const args = process.argv.slice(2), validar = args.includes("--validar"), V6 = args.includes("--v6"), v6 = V6, itensV6 = !V6 && args.includes("--itens-v6");
  const arg = (k, pad) => args.includes(k) ? args[args.indexOf(k) + 1] : pad;
  const gates = new Set(arg("--gates", V6 ? "gi1,gi2,gi3,gi4" : "gi1,gi1l,gi2,gi3,gi4").split(","));
  const semItens = arg("--sem-itens", "").split(",").filter(Boolean);
  const sementes = validar ? SEM_VALIDACAO : SEM_CALIBRACAO;
  const catalogo = ITENS.filter(x => !semItens.includes(x.id));
  const versao = V6 || itensV6 ? M.VERSAO_ESCALA_V6 : M.VERSAO_ESCALA_V9;
  const chipsDe = est => catalogo.filter(M.ehChip).filter(c => M.chipServe(c, est, versao));
  const cartas = [null, ...catalogo.filter(x => x.tipo === "carta").map(x => x.id)];
  /** as combinacoes de ate 3 chips que servem no estagio (chips de stat sem ordem, de regra com ordem), vezes as cartas */
  function combos(est, semCartas = false) {
    const cs = chipsDe(est), st = cs.filter(c => c.tipo === "chip_stat").map(c => c.id), rg = cs.filter(c => c.tipo === "chip_regra").map(c => c.id);
    const subconj = xs => xs.reduce((acc, x) => [...acc, ...acc.map(s => [...s, x])], [[]]);
    const seqs = (xs, n) => n === 0 ? [[]] : [[], ...xs.flatMap(x => seqs(xs.filter(y => y !== x), n - 1).map(s => [x, ...s]))];
    const unicas = new Map();
    for (const S of subconj(st)) if (S.length <= 3) for (const Q of seqs(rg, 3 - S.length)) unicas.set(JSON.stringify([...S, ...Q]), [...S, ...Q]);
    return [...unicas.values()].flatMap(ch => (semCartas ? [null] : cartas).map(carta => ({ chips: ch, carta })));
  }
  const rotulo = c => [...c.chips, c.carta ?? "sem carta"].join(" + ") || "nenhum";

  /* pool de workers, um so para a medicao inteira; no maximo 8 por padrao (com 18 o Node caiu com falha de segmentacao no Windows;
     DIGILAB_WORKERS muda) */
  const W = Number(process.env.DIGILAB_WORKERS ?? Math.min(8, Math.max(1, availableParallelism() - 2))), pool = [];
  let ocupado = null;
  const executar = tarefas => new Promise((ok, falha) => {
    const out = new Array(tarefas.length);
    if (!tarefas.length) { ok(out); return; }
    while (pool.length < Math.min(W, tarefas.length)) {
      const w = new Worker(new URL(import.meta.url), { workerData: { semItens } });
      w.on("message", m => ocupado.aoReceber(w, m));
      w.on("error", err => ocupado.aoFalhar(err));
      pool.push(w);
    }
    let feitas = 0, envio = 0;
    const mandar = w => { if (envio < tarefas.length) { const i = envio++; w.postMessage({ i, t: tarefas[i] }); } };
    ocupado = {
      aoReceber: (w, { i, r }) => { out[i] = r; if (++feitas === tarefas.length) ok(out); else mandar(w); },
      aoFalhar: err => falha(err),
    };
    for (const w of pool) mandar(w);
  });
  const t0 = performance.now(), relogio = () => `${((performance.now() - t0) / 1000).toFixed(0)} s`;
  const out = {
    descricao: V6 ? "Medicao dos itens (medalhas, parte 3; DESIGN_MEDALHAS_ARENAS secao 13.7): motor web, regras V21D, escala dos pets v6, limite do desafiado."
      : "Medicao dos itens nos pets v9 (rodada de equilibrio geral, fase 3; metas M-D1 a M-D3 = G-I1 a G-I3): motor web, regras V21E, escala CESC_V9, fatores dos lideres dos v9, itens dos v9, limite do desafiado.",
    conjunto: validar ? "validacao" : "calibracao", ...(V6 ? {} : { regras: "v21e", versao_pet: M.VERSAO_ESCALA_V9, itens: itensV6 ? "os de antes (v6)" : "os dos v9" }), sementes, catalogo: catalogo.map(x => x.id), fora_do_catalogo: semItens,
    vagas: 3, n: { lider: N_LIDER, estagio: N_ESTAGIO, matriz: N_MATRIZ },
    metas: { gi1_sem_treino_max: META_SEM, gi2_vizinho_pontos_max: META_VIZINHO, gi2_dois_estagios_vitorias_max: META_DOIS, gi3_forca_max: META_FORCA },
  };
  const conferencia = [];
  /* a linha "sem item" contra os artefatos gravados das mesmas sementes: v6 com --validar, a validacao da parte 2; v6 nas de calibracao, a
     medida dos v6 da fase 2; v9 nas de calibracao, a conferencia da fase 2 (arenas e escala). v9 com --validar (fase 4): sem referencia */
  const REF_ARENAS = V6 ? (validar ? "../../../artifacts_campanha/arenas/validacao.json" : "../../../artifacts_equilibrio_geral/fase2/v6_arenas_conferencia.json")
    : (validar ? null : "../../../artifacts_equilibrio_geral/fase2/arenas_conferencia.json");
  const REF_ESCALA = V6 ? (validar ? "../../../artifacts_campanha/escala_v6/validacao.json" : null)
    : (validar ? null : "../../../artifacts_equilibrio_geral/fase2/escala_conferencia.json");
  const ler = p => JSON.parse(readFileSync(fileURLToPath(new URL(p, import.meta.url)), "utf8"));

  /* ---------------- G-I1 */
  if (gates.has("gi1")) {
    const tarefas = [], idx = [];
    for (const a of ARENAS) {
      const est = LUGARES_V6[a.lugar].est, cs = combos(est);
      formasDe(est).forEach((fo, f) => cs.forEach((c, j) => { tarefas.push({ tipo: "lider", v6, itensV6, arena: a.id, forma: f, nivel: 0, chips: c.chips, carta: c.carta, sementes }); idx.push(`${a.id}|${f}|${j}`); }));
    }
    const r = await executar(tarefas), pos = new Map(idx.map((k, i) => [k, i]));
    out.gi1 = {};
    for (const a of ARENAS) {
      const est = LUGARES_V6[a.lugar].est, cs = combos(est), fs = formasDe(est), por = {};
      fs.forEach((fo, f) => {
        const v = cs.map((c, j) => r[pos.get(`${a.id}|${f}|${j}`)]);
        const jm = v.indexOf(Math.max(...v));
        por[fo[0]] = { sem_item: +v[0].toFixed(4), melhor: +v[jm].toFixed(4), combinacao: rotulo(cs[jm]),
          top3: v.map((x, j) => [x, j]).sort((p, q) => q[0] - p[0]).slice(0, 3).map(([x, j]) => `${rotulo(cs[j])} ${x.toFixed(4)}`) };
      });
      const ks = Object.keys(por), media = k => ks.reduce((s, f) => s + por[f][k], 0) / ks.length;
      const pior = ks.reduce((x, y) => por[y].melhor > por[x].melhor ? y : x);
      /* cada item sozinho (media das formas): de onde vem a vitoria */
      const sozinhos = {};
      cs.forEach((c, j) => { if (c.chips.length + (c.carta ? 1 : 0) === 1) sozinhos[rotulo(c).replace(" + sem carta", "")] = +(fs.reduce((s, _, f) => s + r[pos.get(`${a.id}|${f}|${j}`)], 0) / fs.length).toFixed(4); });
      out.gi1[a.id] = { lider: NPC[a.lider].nome, estagio: est, combinacoes: cs.length, sem_item: +media("sem_item").toFixed(4), com_itens: +media("melhor").toFixed(4),
        pior_forma: pior, pior_forma_taxa: por[pior].melhor, passa: media("melhor") <= META_SEM, item_sozinho: sozinhos, por_forma: por };
      console.log(`G-I1 ${a.id}: sem item ${out.gi1[a.id].sem_item} com os melhores itens ${out.gi1[a.id].com_itens} (pior forma ${pior} ${por[pior].melhor}: ${por[pior].combinacao}) ${out.gi1[a.id].passa ? "OK" : "NAO PASSA"} [${relogio()}]
   sozinhos: ${JSON.stringify(sozinhos)}`);
    }
    if (REF_ARENAS) {
      const v = ler(REF_ARENAS);
      for (const a of ARENAS) conferencia.push({ o_que: `G-I1 ${a.id} sem item = ${REF_ARENAS.split("/").slice(-2).join("/")} sem`, esperado: v.arenas[a.id].sem, obtido: out.gi1[a.id].sem_item });
    }
  }

  /* ---------------- G-I1 no limiar (relato, pets v9): o pet com o treino minimo dos itens (CIT_V9.treinoMinimo do tipico) e a melhor
     combinacao contra cada lider, ao lado do mesmo pet sem item e do pet com o treino tipico sem item (gi4 sem_chip) */
  if (!V6 && gates.has("gi1l")) {
    const tarefas = [], idx = [];
    for (const a of ARENAS) {
      const est = LUGARES_V6[a.lugar].est, cs = combos(est), nivel = M.CIT_V9.treinoMinimo * TIPICO[est];
      formasDe(est).forEach((fo, f) => cs.forEach((c, j) => { tarefas.push({ tipo: "lider", v6, itensV6, arena: a.id, forma: f, nivel, chips: c.chips, carta: c.carta, sementes }); idx.push(`${a.id}|${f}|${j}`); }));
    }
    const r = await executar(tarefas), pos = new Map(idx.map((k, i) => [k, i]));
    out.gi1_limiar = {};
    for (const a of ARENAS) {
      const est = LUGARES_V6[a.lugar].est, cs = combos(est), fs = formasDe(est), por = {};
      fs.forEach((fo, f) => {
        const v = cs.map((c, j) => r[pos.get(`${a.id}|${f}|${j}`)]), jm = v.indexOf(Math.max(...v));
        por[fo[0]] = { sem_item: +v[0].toFixed(4), melhor: +v[jm].toFixed(4), combinacao: rotulo(cs[jm]) };
      });
      const ks = Object.keys(por), media = k => ks.reduce((s, f) => s + por[f][k], 0) / ks.length;
      out.gi1_limiar[a.id] = { lider: NPC[a.lider].nome, estagio: est, treino: M.CIT_V9.treinoMinimo * TIPICO[est], sem_item: +media("sem_item").toFixed(4),
        com_itens: +media("melhor").toFixed(4), por_forma: por };
      console.log(`G-I1 no limiar ${a.id} (treino ${M.CIT_V9.treinoMinimo * TIPICO[est]}): sem item ${out.gi1_limiar[a.id].sem_item} com os melhores itens ${out.gi1_limiar[a.id].com_itens} [${relogio()}]`);
    }
  }

  /* ---------------- G-I2 */
  if (gates.has("gi2")) {
    const pares = [...VIZINHOS, ...DOIS], tarefas = [], idx = [];
    for (const [b, a] of pares) {
      const cs = combos(b);
      formasDe(b).forEach((fo, f) => cs.forEach((c, j) => { tarefas.push({ tipo: "estagio", v6, itensV6, baixo: b, alto: a, forma: f, chips: c.chips, carta: c.carta, sementes }); idx.push(`${b}|${a}|${f}|${j}`); }));
    }
    const r = await executar(tarefas), pos = new Map(idx.map((k, i) => [k, i]));
    out.gi2 = {};
    for (const [b, a] of pares) {
      const viz = VIZINHOS.some(([x, y]) => x === b && y === a), cs = combos(b), fs = formasDe(b), por = {};
      let pontos = 0, vit = 0, tot = 0, p0 = 0, v0 = 0;
      fs.forEach((fo, f) => {
        const v = cs.map((_, j) => r[pos.get(`${b}|${a}|${f}|${j}`)]);
        /* a melhor por forma de baixo: a que da mais pontos (empate: mais vitorias) */
        const jm = v.reduce((m, x, j) => (x.pontos > v[m].pontos || (x.pontos === v[m].pontos && x.vitorias > v[m].vitorias)) ? j : m, 0);
        por[fo[0]] = { sem_item: { pontos: +v[0].pontos.toFixed(4), vitorias: +v[0].vitorias.toFixed(4) }, melhor: { pontos: +v[jm].pontos.toFixed(4), vitorias: +v[jm].vitorias.toFixed(4) }, combinacao: rotulo(cs[jm]) };
        pontos += v[jm].pontos * v[jm].partidas; vit += v[jm].vitorias * v[jm].partidas; tot += v[jm].partidas;
        p0 += v[0].pontos * v[0].partidas; v0 += v[0].vitorias * v[0].partidas;
      });
      const pt = pontos / tot, vt = vit / tot, passa = viz ? pt <= META_VIZINHO : vt <= META_DOIS;
      out.gi2[`${b} x ${a}`] = { tipo: viz ? "vizinhos" : "dois estagios", sem_item: { pontos: +(p0 / tot).toFixed(4), vitorias: +(v0 / tot).toFixed(4) },
        com_itens: { pontos: +pt.toFixed(4), vitorias: +vt.toFixed(4) }, partidas: tot, passa, por_forma_de_baixo: por };
      console.log(`G-I2 ${b} (+${TIPICO[b]}) x ${a}: sem item ${(p0 / tot).toFixed(4)}/${(v0 / tot).toFixed(4)}; com os melhores itens pontos ${pt.toFixed(4)} vitorias ${vt.toFixed(4)} ${passa ? "OK" : "NAO PASSA"} [${relogio()}]`);
    }
    if (REF_ESCALA) {
      const v = ler(REF_ESCALA);
      for (const [b, a] of pares) {
        const k = `${b} x ${a}`, ref = v.vizinhos[k] ?? v.dois_estagios[k];
        conferencia.push({ o_que: `G-I2 ${k} sem item = ${REF_ESCALA.split("/").slice(-2).join("/")}`, esperado: [ref.pontos, ref.vitorias], obtido: [out.gi2[k].sem_item.pontos, out.gi2[k].sem_item.vitorias] });
      }
    }
  }

  /* ---------------- G-I3 e G-I4 (matriz) */
  let matriz = null;
  /* M-D3 nos pets v9: a carta nao vale na arena contra bots (CIT_V9.cartaSoContraNpc), entao a matriz mede so os chips; e sem a trava do
     treino minimo (itens_ref: a matriz e sem treino; o efeito do chip em si) */
  const cs3 = combos("adulto", !V6 && !itensV6 && M.CIT_V9.cartaSoContraNpc), fs3 = formasDe("adulto");
  if (gates.has("gi3") || gates.has("gi4")) {
    const tarefas = [];
    fs3.forEach((_, f) => cs3.forEach(c => tarefas.push({ tipo: "matriz", v6, itensV6, forma: f, chips: c.chips, carta: c.carta, desafiado: false, sementes })));
    const r = await executar(tarefas);
    matriz = fs3.map((_, f) => cs3.map((_, j) => r[f * cs3.length + j]));
    console.log(`matriz: ${tarefas.length} combinacoes x forma [${relogio()}]`);
  }
  if (gates.has("gi3")) {
    /* a regra do limite do desafiado (a forma medida desafia): so a linha sem item e a melhor combinacao, como relato */
    const melhores = fs3.map((_, f) => { const v = matriz[f].map(x => x.forca); return v.indexOf(Math.max(...v)); });
    const tarefasD = fs3.flatMap((_, f) => [0, melhores[f]].map(j => ({ tipo: "matriz", v6, itensV6, forma: f, chips: cs3[j].chips, carta: cs3[j].carta, desafiado: true, sementes })));
    const rd = await executar(tarefasD);
    out.gi3 = { limite: "fracao de vida (a matriz da validacao V21D); relato: o limite do desafiado, a forma medida desafia", combinacoes: cs3.length, formas: {} };
    fs3.forEach((fo, f) => {
      const jm = melhores[f], base = matriz[f][0], m = matriz[f][jm], exc = V6 && fo[0] === "furioso";
      out.gi3.formas[fo[0]] = { sem_item: +base.forca.toFixed(4), com_itens: +m.forca.toFixed(4), combinacao: rotulo(cs3[jm]),
        passa: exc ? null : m.forca <= META_FORCA, excecao: exc || undefined, por_rival_sem_item: base.por_rival, por_rival_com_itens: m.por_rival,
        top3: matriz[f].map((x, j) => [x.forca, j]).sort((p, q) => q[0] - p[0]).slice(0, 3).map(([x, j]) => `${rotulo(cs3[j])} ${x.toFixed(4)}`),
        desafiado: { sem_item: +rd[2 * f].forca.toFixed(4), com_itens: +rd[2 * f + 1].forca.toFixed(4) } };
      console.log(`G-I3 ${fo[0]}: sem item ${base.forca.toFixed(4)} com os melhores ${m.forca.toFixed(4)} (${rotulo(cs3[jm])})${exc ? " excecao" : m.forca <= META_FORCA ? " OK" : " NAO PASSA"}; desafiado ${rd[2 * f].forca.toFixed(4)} -> ${rd[2 * f + 1].forca.toFixed(4)}`);
    });
    out.gi3.passa = Object.values(out.gi3.formas).every(x => x.passa !== false);
  }

  /* ---------------- G-I4 (relato): cada chip de regra sozinho */
  if (gates.has("gi4")) {
    const regras = catalogo.filter(x => x.tipo === "chip_regra");
    out.gi4 = { matriz: {}, lideres: {} };
    for (const c of regras) {
      const j = cs3.findIndex(x => x.chips.length === 1 && x.chips[0] === c.id && !x.carta);
      out.gi4.matriz[c.id] = Object.fromEntries(fs3.map((fo, f) => [fo[0], { sem: +matriz[f][0].forca.toFixed(4), com: +matriz[f][j].forca.toFixed(4), ganho: +(matriz[f][j].forca - matriz[f][0].forca).toFixed(4) }]));
    }
    /* contra os lideres do nivel, com o treino tipico: sem chip e com cada chip de regra que serve no estagio da arena */
    const tarefas = [], idx = [];
    for (const a of ARENAS) {
      const est = LUGARES_V6[a.lugar].est;
      formasDe(est).forEach((fo, f) => [null, ...regras.filter(c => M.chipServe(c, est)).map(c => c.id)].forEach(id => {
        tarefas.push({ tipo: "lider", v6, itensV6, arena: a.id, forma: f, nivel: TIPICO[est], chips: id ? [id] : [], carta: null, sementes }); idx.push(`${a.id}|${f}|${id}`);
      }));
    }
    const r = await executar(tarefas), pos = new Map(idx.map((k, i) => [k, i]));
    for (const a of ARENAS) {
      const est = LUGARES_V6[a.lugar].est, fs = formasDe(est), linha = {};
      for (const id of [null, ...regras.filter(c => M.chipServe(c, est)).map(c => c.id)]) {
        const por = Object.fromEntries(fs.map((fo, f) => [fo[0], +r[pos.get(`${a.id}|${f}|${id}`)].toFixed(4)]));
        const media = Object.values(por).reduce((s, x) => s + x, 0) / fs.length;
        linha[id ?? "sem_chip"] = { media: +media.toFixed(4), pior: Math.min(...Object.values(por)), por_forma: por };
      }
      out.gi4.lideres[a.id] = { lider: NPC[a.lider].nome, estagio: est, treino: TIPICO[est], ...linha };
      if (REF_ARENAS) {
        const v = ler(REF_ARENAS);
        conferencia.push({ o_que: `G-I4 ${a.id} sem chip com o treino tipico = ${REF_ARENAS.split("/").slice(-2).join("/")} com`, esperado: v.arenas[a.id].com, obtido: linha.sem_chip.media });
      }
      console.log(`G-I4 ${a.id}: ${Object.entries(linha).map(([k, x]) => `${k} ${x.media} (pior ${x.pior})`).join("; ")}`);
    }
    for (const c of regras) console.log(`G-I4 matriz ${c.id}: ${Object.entries(out.gi4.matriz[c.id]).map(([f, x]) => `${f} ${x.ganho >= 0 ? "+" : ""}${x.ganho}`).join(", ")}`);
  }

  if (conferencia.length) {
    for (const c of conferencia) c.igual = JSON.stringify(c.esperado) === JSON.stringify(c.obtido);
    out.conferencia = conferencia;
    const falhas = conferencia.filter(c => !c.igual);
    console.log(falhas.length ? `CONFERENCIA FALHOU: ${falhas.map(c => c.o_que).join("; ")}` : `conferencia com os artefatos gravados: ${conferencia.length} iguais`);
  }
  out.segundos = Math.round((performance.now() - t0) / 1000);
  /* os pets v9: a calibracao na fase 3; a validacao (--validar) na fase 4 */
  const pasta = fileURLToPath(new URL(V6 ? "../../../artifacts_campanha/itens/" : validar ? "../../../artifacts_equilibrio_geral/fase4/" : "../../../artifacts_equilibrio_geral/fase3/", import.meta.url));
  mkdirSync(pasta, { recursive: true });
  const nome = (V6 ? "" : "itens_") + arg("--saida", (validar ? "validacao" : "calibracao") + (itensV6 ? "_itens_v6" : ""));
  writeFileSync(pasta + nome + ".json", JSON.stringify(out, null, 1) + "\n");
  console.log(`gravado ${nome}.json [${relogio()}]`);
  await Promise.all(pool.map(w => w.terminate()));
}
