// Escala dos pets v6 (CESC_V6; decisao do Matheus, 2026-09-30: "o treino tem que decidir" e "o estagio tem que pesar").
// So no jogo web e so nas lutas de escala dos pets v6 (campanha e arenas); CESC (pets v1-v5, Python da pesquisa) nao muda.
//
// A luta na escala depende so da RAZAO E_A/E_B (o dano vale x E_A/E_B; test/escala.test.mjs), e o perfil do pet nao depende
// de beta (o treino entra no perfil normalizado ao orcamento). Por isso:
//   - as metas de ESTAGIO dependem da razao vida_baixo x (1 + beta x treino tipico) / vida_alto;
//   - as metas dos LIDERES dependem so de beta e do fator (a vida do estagio aparece nos dois lados e cancela).
// O script mede com a escala de cada lado sobreposta (E = vida x (1 + beta x pontos), com a vida e o beta do candidato),
// sem mexer no motor; com --validar mede a CESC_V6 do motor pelo caminho do jogo (perfilDe com a versao 6).
//
// Metas de estagio (Matheus, 2026-09-30, ja com as duas correcoes do dia), pets v6 (regras V21D), bots canonicos de cada
// forma (Rookie: os 2 ramos; Champion: as 4 linhas; Ultimate e Mega: as 8 formas), as 4 especies de cada lado (16 pares de
// especies), lados trocados na metade das partidas:
//   - vizinhos: o pet do estagio de baixo com o treino tipico x o de cima sem treino vence <= 0,10 (pontos: vitoria 1,
//     empate 0,5) — Rookie x Champion, Champion x Ultimate, Ultimate x Mega;
//   - dois estagios de distancia: nenhuma vitoria (0,00) — Rookie x Ultimate, Champion x Mega.
// Treino tipico: Rookie 8, Champion 22, Ultimate 36, Mega 40 (o de test/calibrar_arenas.mjs).
// Metas dos lideres (item 1 do pedido; as de test/calibrar_arenas.mjs): existe fator com sem treino <= 0,05, com o treino
// tipico >= 0,80 e nenhuma forma < 0,5. Aqui so se mede a VIABILIDADE por beta (o fator e escolhido depois, no
// calibrar_arenas.mjs). A Torre de pedra fica fora da escolha de beta: nela o pet sem treino vence por estilo com qualquer
// fator (artifacts_campanha/arenas/calibracao.json), e a alavanca e a lista do Guardromon, nao a escala.
//
// Escolha (sementes de calibracao 3101...3505), com margem nas metas para passarem tambem nas sementes de validacao (cerca de
// 2 erros-padrao de cada taxa: a sem treino de um lider sai de 400 a 1600 partidas, erro-padrao ~0,005-0,011 perto de 0,05;
// a de estagio, de 12.800 a 51.200, ~0,002 perto de 0,10):
//   1. beta: o menor da grade com todos os lideres (menos a Torre) viaveis com folga >= 0,01;
//   2. vidas: Rookie 200 (a de CESC); para cada par de vizinhos, de baixo para cima, a menor razao da grade com pontos <=
//      0,10 - 0,005, e a vida de cima = vida de baixo x razao arredondada para cima em 2 algarismos significativos;
//   3. conferencia nas vidas finais: os tres vizinhos e os dois pares de dois estagios, com o "piso" (vitorias que sobram com a
//      razao 0,01: o de cima nunca acerta o de baixo e o limite de turnos decide pela fracao de vida; a escala nao tira isso).
//
// Limite de turnos: por padrao, a regra do jogo nos pets v6 (decisao do Matheus, 2026-09-30): a luta que chega ao limite sem KO e
// do desafiado (o NPC/lider; nas metas de estagio, o pet do estagio de cima). --limite-fracao: a regra de antes (a fracao de vida
// decide), a que gerou os artefatos de calibracao anteriores a essa decisao.
//
// Pets v9 (rodada de equilibrio geral, fase 2; docs/PLANO_EQUILIBRIO_GERAL.md, meta M-B1): por padrao o script mede os pets v9,
// com as regras das lutas deles (combate V21E, CV21E) e a escala da versao 9 (escalaDaVersao(9): a CESC_V9); os lideres pelas regras
// V21E (as listas V21E nos NPCs de estilo v21). --v6: a medicao de antes, os pets v6 com a V21D e a CESC_V6, nas pastas de antes
// (reproduz os artefatos gravados em artifacts_campanha/escala_v6/). Os pets v9 gravam em artifacts_equilibrio_geral/fase2/.
//
// uso (em web/app): node test/calibrar_escala_v6.mjs [--v6] [--validar | --conferir] [-n 10]
//   sem --validar: sementes de calibracao, grade de beta e de razoes -> escala_calibracao.json (v9) ou
//     artifacts_campanha/escala_v6/calibracao.json (--v6)
//   --conferir: sementes de calibracao, a escala do motor (as metas de estagio, sem escolher nada) -> escala_conferencia.json
//   --validar: sementes de validacao, a escala do motor -> escala_validacao.json (v9; so na fase 4) ou
//     artifacts_campanha/escala_v6/validacao.json (--v6)
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ADOL_V21, ARENAS, CRIANCA_V21, CV, CV21D, CV21E, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, LUGARES_V6, STATS } = M;
const args = process.argv.slice(2), validar = args.includes("--validar"), conferir = args.includes("--conferir"), V6 = args.includes("--v6");
if (validar && conferir) throw new Error("--validar e --conferir juntos");
const n = args.includes("-n") ? Number(args[args.indexOf("-n") + 1]) : 10;
const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
const sementes = validar ? SEM_VALIDACAO : SEM_CALIBRACAO;
/* as regras da luta e a versao do pet (a escala: escalaDe(..., VERSAO)) */
const R = V6 ? CV21D : CV21E, VERSAO = R.versaoPet, ESC = M.escalaDaVersao(VERSAO), FRACAO = args.includes("--limite-fracao"), DESAFIADO = FRACAO ? null : 1;
M.ligarEscala(true);

const TIPICO = { crianca: 8, adolescente: 22, adulto: 36, mega: 40 };
const META_VIZINHO = 0.10, META_DOIS = 0.0;
const META_SEM = 0.05, META_COM = 0.80, META_FORMA = 0.5;
const VIZINHOS = [["crianca", "adolescente"], ["adolescente", "adulto"], ["adulto", "mega"]];
const DOIS = [["crianca", "adulto"], ["adolescente", "mega"]];
const BETAS = [0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.075, 0.1];
const RAZOES = [2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20];
const FATORES = Array.from({ length: 56 }, (_, i) => Math.round((0.5 + 0.1 * i) * 10) / 10);   /* 0,5..6,0 */
const VIDA_ROOKIE = 200, MARGEM_LIDER = 0.01, MARGEM_ESTAGIO = 0.005;
/** para cima, em 2 algarismos significativos */
const arred = x => { const p = 10 ** (Math.floor(Math.log10(x)) - 1); return Math.ceil(x / p - 1e-9) * p; };

const primeiraForma = l => FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l);
/** as formas de referencia do estagio (as de test/calibrar_arenas.mjs; o Mega com as listas do Ultimate) */
function formasDe(est) {
  if (est === "crianca") return ["sereno", "arisco"].map(r => [r, e => ({ esp: e, est, ramo: r }), null, CRIANCA_V21[r]]);
  if (est === "adolescente") return LINHAS.map(l => [l, e => ({ esp: e, est, ramo: "sereno", linha: l }), M.caraterCanonico(primeiraForma(l)), ADOL_V21[l]]);
  return FORMAS_AD.map(f => [f, e => ({ esp: e, est, ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f }), M.caraterCanonico(f), M.gambitsAdulto(f, R)]);
}
/** pet de referencia; E: a escala sobreposta (calibracao) ou undefined (a do motor, pets v6) */
function pet([nome, forma, car, g], esp, nivel, E) {
  const tr = nivel ? Object.fromEntries(STATS.map(k => [k, nivel / STATS.length])) : null;
  const cond = M.perfilDe(forma(esp), car, 1, tr, true, VERSAO);
  return { nome: `${nome}+${nivel}@${esp}`, estilo: { nome, gambits: M.copiarGambits(g), eps: CV.eps }, cond: E === undefined ? cond : { ...cond, escala: E } };
}

/* ---------------------------------------------------------------- metas de estagio */
/** o de baixo (treino tipico) x o de cima (sem treino); rho = E_baixo / E_alto (calibracao) ou null (a escala do motor) */
function estagio(baixo, alto, rho) {
  let pontos = 0, vit = 0, tot = 0;
  const por = {};
  for (const fb of formasDe(baixo)) for (const fa of formasDe(alto)) {
    let vp = 0;
    for (const eb of ESPECIES) for (const ea of ESPECIES) {
      const A = pet(fb, eb, TIPICO[baixo], rho === null ? undefined : rho), B = pet(fa, ea, 0, rho === null ? undefined : 1);
      for (const s of sementes) for (let k = 0; k < n; k++) {
        const sp = M.hashSemente("escala-v6", s, A.nome, B.nome, k);
        const p = k < n / 2 ? M.jogarV2(A, B, sp, R, null, DESAFIADO).pontosA : 1 - M.jogarV2(B, A, sp, R, null, FRACAO ? null : 0).pontosA;
        pontos += p; tot++;
        if (p === 1) { vit++; vp++; }
      }
    }
    if (vp) por[`${fb[0]} x ${fa[0]}`] = vp;
  }
  return { pontos: +(pontos / tot).toFixed(4), vitorias: +(vit / tot).toFixed(4), partidas: tot, vitorias_por_par: por };
}

/* ---------------------------------------------------------------- viabilidade dos lideres por beta */
function taxaArena(a, b, arena) {
  let soma = 0, tot = 0;
  for (const s of sementes) for (let k = 0; k < n; k++) {
    const serie = M.jogarArena(a, b, M.hashSemente("calib-arena", s, a.nome, b.nome, k), R, arena.lutas ?? 1, DESAFIADO);
    soma += serie.length === (arena.lutas ?? 1) ? serie[serie.length - 1].pontosA : 0; tot++;
  }
  return soma / tot;
}
const cacheSem = new Map();
/** sem treino (nao depende de beta) e com o treino tipico (pet com E = 1 + beta x pontos, lider com E = fator) */
function lider(arena, fator, beta) {
  const est = LUGARES_V6[arena.lugar].est, formas = formasDe(est), nv = TIPICO[est], ar = { ...arena, fator };
  const B0 = M.lutadorBot(arena.lider, R, ar), B = { ...B0, cond: { ...B0.cond, escala: fator } };
  const media = nivel => {
    const por = formas.map(fo => ESPECIES.reduce((s, e) => s + taxaArena(pet(fo, e, nivel, 1 + beta * nivel), B, ar), 0) / ESPECIES.length);
    return { media: por.reduce((s, x) => s + x, 0) / por.length, pior: Math.min(...por), pior_forma: formas[por.indexOf(Math.min(...por))][0] };
  };
  const ch = `${arena.id}@${fator}`;
  if (!cacheSem.has(ch)) cacheSem.set(ch, media(0).media);
  const sem = cacheSem.get(ch);
  if (sem > META_SEM) return { fator, sem: +sem.toFixed(4), passa: false };
  const c = media(nv);
  return { fator, sem: +sem.toFixed(4), com: +c.media.toFixed(4), pior: +c.pior.toFixed(4), pior_forma: c.pior_forma,
    passa: c.media >= META_COM && c.pior >= META_FORMA, folga: +Math.min(META_SEM - sem, c.media - META_COM, c.pior - META_FORMA).toFixed(4) };
}
function viabilidade(beta) {
  const out = {};
  for (const a of ARENAS) {
    const med = FATORES.map(f => lider(a, f, beta)), ok = med.filter(m => m.passa);
    const melhor = (ok.length ? ok : med.filter(m => m.com !== undefined)).reduce((x, y) => (y.folga ?? -9) > (x?.folga ?? -9) ? y : x, null);
    out[a.id] = { viavel: ok.length > 0, com_margem: !!melhor && melhor.passa && melhor.folga >= MARGEM_LIDER, fatores_que_passam: ok.map(m => m.fator), melhor };
  }
  return out;
}

const pasta = fileURLToPath(new URL(V6 ? "../../../artifacts_campanha/escala_v6/" : "../../../artifacts_equilibrio_geral/fase2/", import.meta.url));
const arquivo = nome => pasta + (V6 ? nome : "escala_" + nome);
mkdirSync(pasta, { recursive: true });
const cab = { limite: FRACAO ? "fracao" : "desafiado", sementes, n_por_semente: n, regras: V6 ? "v21d" : "v21e", ...(V6 ? {} : { versao_pet: VERSAO }), treino_tipico: TIPICO,
  metas: { vizinho_pontos_max: META_VIZINHO, dois_estagios_vitorias_max: META_DOIS, lider_sem_max: META_SEM, lider_com_min: META_COM, lider_pior_forma_min: META_FORMA } };

if (validar || conferir) {
  const E = (est, pontos) => M.escalaDe(est, pontos, VERSAO);
  const out = { descricao: V6 ? "Validacao da escala dos pets v6 (CESC_V6 do motor): metas de estagio."
    : `${validar ? "Validacao" : "Conferencia"} da escala dos pets v9 (a do motor, versao 9; regras V21E): metas de estagio.`,
    conjunto: validar ? "validacao" : "calibracao", ...cab, escala: { vida: ESC.vida, beta: ESC.beta }, vizinhos: {}, dois_estagios: {} };
  for (const [b, a] of [...VIZINHOS, ...DOIS]) {
    const viz = VIZINHOS.some(([x, y]) => x === b && y === a), r = estagio(b, a, null), rho = E(b, TIPICO[b]) / E(a, 0);
    const passa = viz ? r.pontos <= META_VIZINHO : r.vitorias <= META_DOIS;
    (viz ? out.vizinhos : out.dois_estagios)[`${b} x ${a}`] = { razao_E: +rho.toFixed(4), ...r, passa };
    console.log(`${b} (+${TIPICO[b]}) x ${a}: razao ${rho.toFixed(3)} pontos ${r.pontos} vitorias ${r.vitorias} ${passa ? "OK" : "NAO PASSA"}`);
  }
  writeFileSync(arquivo(validar ? "validacao.json" : "conferencia.json"), JSON.stringify(out, null, 1) + "\n");
} else {
  const out = { descricao: `Calibracao da escala dos pets ${V6 ? "v6" : "v9 (regras V21E)"}: viabilidade dos lideres por beta, metas de estagio por razao de vida.`,
    conjunto: "calibracao", ...cab, margem_lider: MARGEM_LIDER, margem_estagio: MARGEM_ESTAGIO, betas: BETAS, razoes: RAZOES, fatores: [FATORES[0], FATORES[FATORES.length - 1]], lideres_por_beta: {} };
  /* 1. beta: o menor com todos os lideres viaveis (a Torre fora: a alavanca dela e a lista) */
  let beta = null;
  for (const b of BETAS) {
    const v = viabilidade(b);
    out.lideres_por_beta[b] = v;
    const faltam = Object.entries(v).filter(([id, x]) => id !== "torre" && !x.com_margem).map(([id]) => id);
    console.log(`beta ${b}: ${Object.entries(v).map(([id, x]) => `${id} ${x.com_margem ? "ok" : x.viavel ? "sem margem" : "nao"} (folga ${x.melhor?.folga ?? "-"})`).join(", ")}`);
    if (!faltam.length && beta === null) beta = b;
  }
  if (beta === null) throw new Error("nenhum beta da grade deixa os lideres viaveis");
  out.beta = beta;
  /* 2. vidas: de baixo para cima, a menor razao com pontos <= 0,10 - margem; a vida de cima arredondada para cima */
  out.vizinhos = {};
  const vida = { bebe: 50, crianca: VIDA_ROOKIE };
  for (const [b, a] of VIZINHOS) {
    const med = [];
    for (const q of RAZOES) {
      const rho = (1 + beta * TIPICO[b]) / q, r = estagio(b, a, rho);
      med.push({ razao_vida: q, razao_E: +rho.toFixed(4), pontos: r.pontos, vitorias: r.vitorias });
      console.log(`  ${b} (+${TIPICO[b]}) x ${a}: vida x${q} (E ${rho.toFixed(3)}) pontos ${r.pontos} vitorias ${r.vitorias}`);
      if (r.pontos <= META_VIZINHO - MARGEM_ESTAGIO) { vida[a] = arred(vida[b] * q); break; }
    }
    if (vida[a] === undefined) throw new Error(`nenhuma razao da grade passa em ${b} x ${a}`);
    out.vizinhos[`${b} x ${a}`] = { escolha: med[med.length - 1].razao_vida, medidas: med };
  }
  out.vida = vida;
  console.log("vida", JSON.stringify(vida), "beta", beta);
  /* 3. conferencia nas vidas finais (sementes de calibracao) */
  out.conferencia = {};
  for (const [b, a] of [...VIZINHOS, ...DOIS]) {
    const viz = VIZINHOS.some(([x, y]) => x === b && y === a), rho = vida[b] * (1 + beta * TIPICO[b]) / vida[a], r = estagio(b, a, rho);
    const piso = viz ? null : estagio(b, a, 0.01);
    out.conferencia[`${b} x ${a}`] = { razao_vida: +(vida[a] / vida[b]).toFixed(4), razao_E: +rho.toFixed(4), ...r,
      passa: viz ? r.pontos <= META_VIZINHO : r.vitorias <= META_DOIS,
      ...(piso ? { piso: { razao_E: 0.01, pontos: piso.pontos, vitorias: piso.vitorias, vitorias_por_par: piso.vitorias_por_par } } : {}) };
    console.log(`  ${b} (+${TIPICO[b]}) x ${a}: E ${rho.toFixed(4)} pontos ${r.pontos} vitorias ${r.vitorias}${piso ? `; piso (E 0,01) vitorias ${piso.vitorias}` : ""}`);
  }
  writeFileSync(arquivo("calibracao.json"), JSON.stringify(out, null, 1) + "\n");
}
