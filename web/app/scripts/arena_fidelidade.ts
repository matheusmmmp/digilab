/* A fidelidade do nucleo novo da luta (docs/TAREFA_V3_LUTA_POC.md, LP1, item 3): o motor/arena/ contra a POC portada no #446/#448 (a pasta
   web/app/arena/ do commit efb2ded, que reproduziu exatamente o harness remaster/fonte/scripts_arena/harness_equilibrio.js).
   No Node do engines (24, que roda TypeScript sem dependencia nova). Le os dados do jogo de D:\Trab\digilab\Assets\arena_up\dados (fora do
   git) e o codigo da POC do historico do git (git show efb2ded:...), copiado para uma pasta temporaria. Tres passos:
     A. a ancora: a POC do efb2ded, com as equipes de 3 e a sequencia unica, reproduz o gabarito do harness
        (scripts/arena_gabarito_prototipo.json do efb2ded) — prova de que a referencia e a POC;
     B. o controle: o nucleo novo com a aritmetica da POC de volta (dist = Math.hypot, seno = Math.sin; uma copia temporaria do
        motor/arena/) contra a POC no 1 contra 1, luta a luta — prova de que o porte so mudou a aritmetica;
     C. a diferenca da aritmetica: o nucleo novo contra a POC, as duas no 1 contra 1, nas mesmas tabelas do harness (arenas, rodizio,
        estagios, niveis), em distribuicao e luta a luta.
   E grava o gabarito do teste do CI (test/gabaritos/arena_poc_1x1.json): a POC 1 contra 1 nas 60 formas da tabela do git, com os stats
   genericos, nos 8 mapas; o teste arena_fidelidade.test.ts roda o nucleo novo nas mesmas lutas.
     node scripts/arena_fidelidade.ts     # grava scripts/medicoes/arena_fidelidade_lp1.json e o gabarito; sai com 1 se A ou B falhar
   O equilibrio por equipes de 3 nao e do jogo (o pet luta sozinho, LP-3 e secao 6); por isso a comparacao com o nucleo novo e no 1 x 1. */
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import { createHash } from "node:crypto";
import os from "node:os";
import { join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const APP = fileURLToPath(new URL("../", import.meta.url));
const URL_MOTOR = pathToFileURL(join(APP, "motor") + "/").href;
const PASTA = new URL("../../../../Assets/arena_up/dados/", import.meta.url);
const COMMIT_POC = "efb2ded";
const t0 = Date.now();

/* ------------------------------------------------------------ as copias temporarias (a POC e o controle) */
const TMP = mkdtempSync(join(os.tmpdir(), "arena_fidelidade_"));
const reimportar = (txt: string) => txt
  .replace(/from "\.\.\/motor\/(rng|mundo)\.ts"/g, (_m, f) => `from "${URL_MOTOR}${f}.ts"`)
  .replace(/from "\.\.\/(rng|mundo)\.ts"/g, (_m, f) => `from "${URL_MOTOR}${f}.ts"`);
const POC_DIR = join(TMP, "poc"), CTRL_DIR = join(TMP, "controle");
mkdirSync(POC_DIR); mkdirSync(CTRL_DIR);
const arquivosPoc = execSync(`git ls-tree --name-only --full-tree ${COMMIT_POC} web/app/arena/`, { cwd: APP }).toString().trim().split("\n");
for (const f of arquivosPoc) writeFileSync(join(POC_DIR, f.split("/").pop()!), reimportar(execSync(`git show ${COMMIT_POC}:${f}`, { cwd: APP, maxBuffer: 1 << 26 }).toString()));
const gabarito = JSON.parse(execSync(`git show ${COMMIT_POC}:web/app/scripts/arena_gabarito_prototipo.json`, { cwd: APP }).toString());
for (const f of readdirSync(join(APP, "motor", "arena"))) writeFileSync(join(CTRL_DIR, f), reimportar(readFileSync(join(APP, "motor", "arena", f), "utf8")));
writeFileSync(join(CTRL_DIR, "aritmetica.ts"), `/* CONTROLE (so a medicao): a aritmetica da POC de volta */
export const dist = (dx: number, dy: number): number => Math.hypot(dx, dy);
export const seno = (x: number): number => Math.sin(x);
export const PI = Math.PI;
export const DOIS_PI = 2 * Math.PI;
`);
const POC = await import(pathToFileURL(join(POC_DIR, "index.ts")).href);
const CTRL = await import(pathToFileURL(join(CTRL_DIR, "index.ts")).href);
const NOVO = await import("../motor/arena/index.ts");
const { criarRng } = await import("../motor/rng.ts");

/* ------------------------------------------------------------ os dados do jogo */
const ler = (n: string) => { const b = readFileSync(new URL(n + ".json", PASTA)); return { j: JSON.parse(b.toString("utf8")), sha: createHash("sha256").update(b).digest("hex") }; };
const arqs = Object.fromEntries(["status", "golpes", "atributos", "atlas"].map(n => [n, ler(n)]));
const dados = { status: arqs.status.j, golpes: arqs.golpes.j, atributos: arqs.atributos.j, atlas: arqs.atlas.j };
POC.conferirDados(dados);

/* ------------------------------------------------------------ A. a ancora: a POC com equipes de 3 reproduz o gabarito */
const modo = "unico";
const estagios = ["InTraining2", "Rookie", "Champion", "Ultimate", "Mega"];
const tabelas3 = {
  arenas_semente_7: POC.medirArenas(dados, POC.IDS_CENA, 10, 7, modo),
  campo_por_semente: Object.fromEntries([42, 99, 123].map(sd => { const r = POC.medirArenas(dados, ["campo"], 10, sd, modo).campo; return [sd, { azul: r.azul, dur: r.dur }]; })),
  rodizio_sementes_7_8: Object.fromEntries(estagios.map(e => [e, POC.rodizio(dados, e, [7, 8], modo)])),
  estagios: Object.fromEntries(POC.PARES_ESTAGIOS.map(([a, b]: [string, string]) => [`${b}>${a}`, POC.cruzar(dados, a, b, modo)])),
  niveis_champion_nv1_contra_rookie: Object.fromEntries([2, 3, 5].map(nv => [nv, POC.cruzar(dados, "Rookie", "Champion", modo, nv, 1)])),
};
const difAncora: string[] = [];
const comparar = (onde: string, esperado: unknown, obtido: unknown, dif: string[]) => {
  if (esperado !== null && typeof esperado === "object") { for (const k of Object.keys(esperado)) comparar(`${onde}.${k}`, (esperado as any)[k], (obtido as any)?.[k], dif); return; }
  if (esperado !== obtido) dif.push(`${onde}: esperado ${JSON.stringify(esperado)}, obtido ${JSON.stringify(obtido)}`);
};
for (const k of Object.keys(gabarito)) if (k !== "fonte") comparar(k, gabarito[k], (tabelas3 as any)[k], difAncora);
console.log(`A. ancora (POC 3x3 contra o gabarito): ${difAncora.length ? difAncora.length + " diferencas" : "tudo igual"}`);

/* ------------------------------------------------------------ o harness no 1 contra 1, com a luta trocavel */
interface Res { vencedor: "a" | "b" | null; fim: boolean; relogio: number; danoAmb: number; danoGolpe: number; ringue: number; bloq: number; pilar: number; runa: number; caiuAmb: number; errou: number; vidaA: number; vidaB: number; pos: string }
type Luta1 = (cena: string, na: string, nb: string, o: { forca?: number; nivelA?: number; nivelB?: number }, semente: number) => Res;

const contar = (res: Res, e: any) => {
  if (e.tipo === "dano") res.danoGolpe += e.perda;
  else if (e.tipo === "ambiente") res.danoAmb += e.perda;
  else if (e.tipo === "queda_ringue") res.ringue++;
  else if (e.tipo === "tiro_bloqueado") res.bloq++;
  else if (e.tipo === "pilar") res.pilar++;
  else if (e.tipo === "runa") res.runa++;
  else if (e.tipo === "queda" && e.motivo !== null) res.caiuAmb++;
  else if (e.tipo === "tiro_errou" || e.tipo === "golpe_ar") res.errou++;
};
const vazio = (): Res => ({ vencedor: null, fim: false, relogio: 0, danoAmb: 0, danoGolpe: 0, ringue: 0, bloq: 0, pilar: 0, runa: 0, caiuAmb: 0, errou: 0, vidaA: 0, vidaB: 0, pos: "" });
/* a sequencia unica do harness (o modo "unico"): o mesmo gerador para todos os usos, semeado pela semente da luta */
const sorteios = (M: any, semente: number) => M.sorteioUnico(criarRng(semente));

/** a POC do efb2ded com equipes de 1 (a luta do pet do #448) */
const lutaPoc: Luta1 = (cena, na, nb, o, semente) => {
  const L = POC.criarLuta(POC.configCpu(cena, [na], [nb], o), dados, sorteios(POC, semente)), res = vazio();
  while (!L.fim && L.relogio < POC.LIMITE_MS) for (const e of POC.passo(L)) contar(res, e);
  return { ...res, vencedor: L.vencedor, fim: L.fim, relogio: L.relogio, vidaA: L.eq.a[0].hp, vidaB: L.eq.b[0].hp, pos: [L.eq.a[0].x, L.eq.a[0].y, L.eq.b[0].x, L.eq.b[0].y].join(",") };
};
/** o Digimon da POC como DadosForma (o golpe, a habilidade, o fr com o Math.pow da POC e a duracao dos clipes pelo tagDe dela) */
const formaDe = (n: string) => {
  const g = dados.golpes[n] || POC.GOLPE_GENERICO, A = dados.atlas.d[n];
  const base = (b: any) => ({ anim: b.anim, t: b.t, proj: b.proj ? { prefab: b.proj.prefab ?? null, vel: b.proj.vel, tipo: b.proj.tipo ?? null } : null, hits: b.hits, fr: POC.fatorRitmo(b) });
  return { digimon: n, nome: n, estagio: dados.status[n]?.estagio ?? "", atributo: dados.atributos[n], generico: !dados.golpes[n],
    golpe: base(g), habilidade: g.skill ? base(g.skill) : null, msGolpe: POC.duracaoTag(A, g.anim), msHabilidade: POC.duracaoTag(A, (g.skill || g).anim) };
};
/** os stats que a POC daria ao Digimon (o statsDoMembro dela, com a fonte "jogo"): o nucleo novo recebe prontos (LP-3) */
const statsDe = (cfgPoc: any, l: "a" | "b", n: string) => { const { origem: _o, ...s } = POC.statsDoMembro(cfgPoc, dados, l, n); return s; };
const lutaNucleo = (M: any): Luta1 => (cena, na, nb, o, semente) => {
  const cp = POC.configCpu(cena, [na], [nb], o);
  const cfg = { cena, dific: cp.dific, forca: cp.forca, pvel: cp.pvel, a: { forma: formaDe(na), stats: statsDe(cp, "a", na) }, b: { forma: formaDe(nb), stats: statsDe(cp, "b", nb) } };
  const L = M.criarLuta(cfg, sorteios(M, semente)), res = vazio();
  for (const e of L.eventos) contar(res, e);
  L.eventos = [];
  const r = M.rodarAteOFim(L, (ev: any[]) => { for (const e of ev) contar(res, e); });
  return { ...res, vencedor: r.vencedor, fim: r.fim, relogio: r.relogio, vidaA: r.vidaA, vidaB: r.vidaB, pos: [L.a.x, L.a.y, L.b.x, L.b.y].join(",") };
};

/* o harness do medicao.ts do efb2ded, com a luta trocavel e equipes de 1 (cada sorteio de equipe tira 1 parceiro, nao 3) */
const parceiro = (n: string) => dados.status[n].tipo === "PartnerDigiMon" && !dados.status[n].estimado && !!dados.golpes[n] && !!dados.atlas.d[n];
function harness(luta: Luta1) {
  const log: string[] = [];
  const L1: Luta1 = (...a) => { const r = luta(...a); log.push(`${r.vencedor}|${r.relogio}|${r.vidaA}|${r.vidaB}|${r.pos}`); return r; };
  const medir = (ids: string[], nConf: number, semente: number) => {
    const ps = Object.keys(dados.status).filter(n => parceiro(n) && ["Rookie", "Champion"].includes(dados.status[n].estagio ?? ""));
    const s = criarRng(semente), confs: [string, string][] = [];
    for (let i = 0; i < nConf; i++) { const p = () => ps[Math.floor(s.random() * ps.length)]; confs.push([p(), p()]); }
    const out: Record<string, any> = {};
    for (const id of ids) {
      const durs: number[] = [], ev = { ringue: 0, bloq: 0, pilar: 0, runa: 0, caiuAmb: 0, errou: 0 };
      let ambT = 0, atkT = 0, winA = 0, tout = 0, k = 0;
      for (const [ea, eb] of confs) for (const lado of [0, 1]) {
        const [A, B] = lado ? [eb, ea] : [ea, eb];
        const r = L1(id, A, B, { forca: 1.5 }, semente + 1000 + k++);
        if (!r.fim) tout++;
        durs.push(r.relogio / 1000); ambT += r.danoAmb; atkT += r.danoGolpe;
        if (r.vencedor === "a") winA++;
        for (const c of Object.keys(ev) as (keyof typeof ev)[]) ev[c] += r[c];
      }
      const n = durs.length; durs.sort((a, b) => a - b);
      out[id] = { lutas: n, dur: +(durs.reduce((a, b) => a + b, 0) / n).toFixed(1), p90: +durs[Math.floor(n * 0.9)].toFixed(1), timeouts: tout,
        ambPct: +(100 * ambT / (ambT + atkT)).toFixed(1), azul: winA / n, ...Object.fromEntries(Object.entries(ev).map(([c, v]) => [c, +(v / n).toFixed(2)])) };
    }
    return out;
  };
  const duelo = (na: string, nb: string, semente: number, nivA = 1, nivB = 1) => L1("campo", na, nb, { forca: 1, nivelA: nivA, nivelB: nivB }, semente);
  const rodizio = (estagio: string, sementes: number[]) => {
    const ns = Object.keys(dados.status).filter(n => parceiro(n) && dados.status[n].estagio === estagio);
    const w: Record<string, number> = Object.fromEntries(ns.map(n => [n, 0])), j: Record<string, number> = Object.fromEntries(ns.map(n => [n, 0]));
    let tempo = 0, nl = 0, tout = 0;
    for (let i = 0; i < ns.length; i++) for (let k = i + 1; k < ns.length; k++) for (const sd of sementes) for (const [a, b] of [[ns[i], ns[k]], [ns[k], ns[i]]]) {
      const r = duelo(a, b, sd * 7919 + i * 131 + k); j[a]++; j[b]++; tempo += r.relogio / 1000; nl++;
      if (r.vencedor === "a") w[a]++; else if (r.vencedor === "b") w[b]++; else { w[a] += 0.5; w[b] += 0.5; tout++; }
    }
    const tab = ns.map(n => ({ n, wr: w[n] / j[n], proj: !!dados.golpes[n].proj }));
    const media = (f: (t: { wr: number; proj: boolean }) => boolean) => { const x = tab.filter(f); return x.length ? +(x.reduce((a, b) => a + b.wr, 0) / x.length).toFixed(3) : null; };
    const wr = tab.map(t => t.wr), dp = Math.sqrt(wr.reduce((a, b) => a + (b - 0.5) * (b - 0.5), 0) / wr.length);
    return { lutas: nl, tempoMedio: +(tempo / nl).toFixed(1), semFim: tout, dist: media(t => t.proj), corpo: media(t => !t.proj), desvio: +dp.toFixed(3),
      min: +Math.min(...wr).toFixed(3), max: +Math.max(...wr).toFixed(3), wr: Object.fromEntries(tab.map(t => [t.n, +t.wr.toFixed(3)])) };
  };
  const cruzar = (e1: string, e2: string, nivel1 = 1, nivel2 = 1) => {
    const por = (e: string) => Object.keys(dados.status).filter(n => parceiro(n) && dados.status[n].estagio === e).slice(0, 8);
    let w = 0, n = 0;
    for (const a of por(e1)) for (const b of por(e2)) for (const lado of [0, 1]) {
      const [x, y, nx, ny] = lado ? [b, a, nivel2, nivel1] : [a, b, nivel1, nivel2];
      const r = duelo(x, y, n * 31 + 5, nx, ny); n++;
      const alto = lado ? r.vencedor === "a" : r.vencedor === "b"; if (alto) w++; else if (!r.vencedor) w += 0.5;
    }
    return +(100 * w / n).toFixed(1);
  };
  const tabelas = {
    arenas_semente_7: medir(POC.IDS_CENA, 10, 7),
    arenas_semente_42: medir(POC.IDS_CENA, 10, 42),
    rodizio_sementes_7_8: Object.fromEntries(estagios.map(e => [e, rodizio(e, [7, 8])])),
    estagios: Object.fromEntries(POC.PARES_ESTAGIOS.map(([a, b]: [string, string]) => [`${b}>${a}`, cruzar(a, b)])),
    niveis_champion_nv1_contra_rookie: Object.fromEntries([2, 3, 5].map(nv => [nv, cruzar("Rookie", "Champion", nv, 1)])),
  };
  return { tabelas, log };
}

const tc = Date.now();
const hPoc = harness(lutaPoc);
const msPoc = Date.now() - tc;
const hCtrl = harness(lutaNucleo(CTRL));
const tn = Date.now();
const hNovo = harness(lutaNucleo(NOVO));
const msNovo = Date.now() - tn;
const iguais = (x: string[], y: string[]) => x.reduce((s, v, i) => s + (v === y[i] ? 1 : 0), 0);
const nLutas = hPoc.log.length;
const ctrlIguais = iguais(hPoc.log, hCtrl.log), novoIguais = iguais(hPoc.log, hNovo.log);
const resultado = (l: string[]) => l.map(x => x.split("|").slice(0, 4).join("|"));
const novoMesmoResultado = iguais(resultado(hPoc.log), resultado(hNovo.log));
console.log(`B. controle (nucleo novo com a aritmetica da POC contra a POC 1x1): ${ctrlIguais}/${nLutas} lutas iguais`);
console.log(`C. aritmetica (nucleo novo contra a POC 1x1): ${novoMesmoResultado}/${nLutas} com o mesmo resultado (vencedor, relogio, vidas); ${novoIguais}/${nLutas} iguais em todos os bits (com as posicoes finais)`);

/* ------------------------------------------------------------ as diferencas das tabelas (C) */
const difTab: Record<string, unknown> = {};
const P = hPoc.tabelas, N = hNovo.tabelas;
for (const k of ["arenas_semente_7", "arenas_semente_42"] as const)
  difTab[k] = Object.fromEntries(Object.keys(P[k]).map(id => [id, { azul: +(N[k][id].azul - P[k][id].azul).toFixed(3), dur: +(N[k][id].dur - P[k][id].dur).toFixed(1),
    p90: +(N[k][id].p90 - P[k][id].p90).toFixed(1), ambPct: +(N[k][id].ambPct - P[k][id].ambPct).toFixed(1), timeouts: N[k][id].timeouts - P[k][id].timeouts }]));
difTab.rodizio = Object.fromEntries(estagios.map(e => {
  const p = P.rodizio_sementes_7_8[e], n = N.rodizio_sementes_7_8[e];
  const dwr = Object.keys(p.wr).map(d => Math.abs(n.wr[d] - p.wr[d]));
  return [e, { tempoMedio: +(n.tempoMedio - p.tempoMedio).toFixed(1), semFim: n.semFim - p.semFim, dist: +(n.dist - p.dist).toFixed(3), corpo: +(n.corpo - p.corpo).toFixed(3),
    desvio: +(n.desvio - p.desvio).toFixed(3), wrMaxAbs: +Math.max(...dwr).toFixed(3), wrMediaAbs: +(dwr.reduce((a, b) => a + b, 0) / dwr.length).toFixed(4) }];
}));
difTab.estagios = Object.fromEntries(Object.keys(P.estagios).map(k => [k, +(N.estagios[k] - P.estagios[k]).toFixed(1)]));
difTab.niveis = Object.fromEntries(Object.keys(P.niveis_champion_nv1_contra_rookie).map(k => [k, +(N.niveis_champion_nv1_contra_rookie[k] - P.niveis_champion_nv1_contra_rookie[k]).toFixed(1)]));

/* "muito" (o criterio do aviso ao coordenador), PROPOSTO, SEM FONTE: vitoria de um lado ou de um estagio mudando mais de 5 pontos
   percentuais agregados, ou a duracao media mais de 5 %. A vitoria de um Digimon so no rodizio tem poucas lutas (2 sementes) e fica so
   registrada. */
const alertas: string[] = [];
for (const k of ["arenas_semente_7", "arenas_semente_42"] as const) for (const [id, d] of Object.entries(difTab[k] as Record<string, any>)) {
  if (Math.abs(d.azul) > 0.05) alertas.push(`${k}.${id}: vitoria do azul ${d.azul > 0 ? "+" : ""}${(100 * d.azul).toFixed(1)} pp`);
  if (Math.abs(d.dur) > 0.05 * P[k][id].dur) alertas.push(`${k}.${id}: duracao ${d.dur} s`);
}
for (const [e, d] of Object.entries(difTab.rodizio as Record<string, any>)) {
  if (Math.abs(d.dist) > 0.05 || Math.abs(d.corpo) > 0.05) alertas.push(`rodizio.${e}: dist ${d.dist}, corpo ${d.corpo}`);
  if (Math.abs(d.tempoMedio) > 0.05 * P.rodizio_sementes_7_8[e].tempoMedio) alertas.push(`rodizio.${e}: tempo ${d.tempoMedio} s`);
}
for (const [k, d] of Object.entries({ ...(difTab.estagios as object), ...(difTab.niveis as object) }) as [string, number][]) if (Math.abs(d) > 5) alertas.push(`${k}: ${d} pp`);
console.log(alertas.length ? `ALERTAS (${alertas.length}):\n  ` + alertas.join("\n  ") : "nenhuma tabela mudou alem do criterio");

/* ------------------------------------------------------------ o gabarito do CI: a POC 1x1 nas 60 formas, stats genericos, 8 mapas */
const FORMAS = NOVO.FORMAS_ARENA as Record<string, { digimon: string }>;
const chaves = Object.keys(FORMAS);
const sorteioGab = criarRng(101), lutasGab: unknown[] = [];
for (const cena of POC.IDS_CENA) for (const ka of chaves) {
  const kb = chaves[Math.floor(sorteioGab.random() * chaves.length)], semente = 101 + lutasGab.length;
  const cfg = { ...POC.configCpu(cena, [FORMAS[ka].digimon], [FORMAS[kb].digimon]), a: { equipe: [FORMAS[ka].digimon], fonte: "generico", nivel: 1, generico: { ...POC.STATS_PADRAO } },
    b: { equipe: [FORMAS[kb].digimon], fonte: "generico", nivel: 1, generico: { ...POC.STATS_PADRAO } } };
  const L = POC.criarLuta(cfg, dados, POC.sorteiosPorFluxo(semente));
  while (!L.fim && L.relogio < POC.LIMITE_MS) POC.passo(L);
  lutasGab.push({ cena, a: ka, b: kb, semente, vencedor: L.vencedor, fim: L.fim, relogio: L.relogio, vidaA: L.eq.a[0].hp, vidaB: L.eq.b[0].hp });
}
const statsGen = { ...POC.STATS_PADRAO, esquiva: 0, atordoa: 0 };
writeFileSync(join(APP, "test", "gabaritos", "arena_poc_1x1.json"), JSON.stringify({
  fonte: `web/app/scripts/arena_fidelidade.ts: a POC do commit ${COMMIT_POC} (web/app/arena/, o porte do arena.html do #446/#448) no 1 contra 1, com os fluxos do jogo, sobre os dados de Assets/arena_up/dados (sha256 abaixo), as 60 formas da tabela motor/arena/formas.ts e os stats genericos da POC (STATS_PADRAO, esquiva e atordoamento 0)`,
  dados: Object.fromEntries(["golpes", "atributos", "atlas"].map(n => [n + ".json", arqs[n].sha])), stats: statsGen, opcoes: { forca: 1.5, pvel: 0.15, dific: "normal" },
  lutas: lutasGab,
}, null, 0).replace(/\},\{/g, "},\n{") + "\n");

/* ------------------------------------------------------------ grava a medicao */
const commit = execSync("git rev-parse --short HEAD", { cwd: APP }).toString().trim();
const saida = {
  gerado_por: "web/app/scripts/arena_fidelidade.ts", commit, data: new Date().toISOString().slice(0, 10), node: process.version, poc: COMMIT_POC,
  dados: Object.fromEntries(Object.entries(arqs).map(([n, a]) => [n + ".json", a.sha])),
  A_ancora: { descricao: "a POC do efb2ded, equipes de 3, sequencia unica, contra o gabarito do harness (arena_gabarito_prototipo.json)", diferencas: difAncora, tabelas: tabelas3 },
  B_controle: { descricao: "o nucleo novo com dist = Math.hypot e seno = Math.sin contra a POC 1x1, luta a luta (vencedor, relogio, vidas e as posicoes finais, todos os bits)", lutas: nLutas, iguais: ctrlIguais },
  C_aritmetica: {
    descricao: "o nucleo novo (sqrt, seno por polinomio, x*x) contra a POC 1x1, nas tabelas do harness com equipes de 1; azul e vitoria do lado a (fracao); dur em s",
    lutas: nLutas, mesmoResultado: novoMesmoResultado, iguaisTodosOsBits: novoIguais, criterio: "vitoria +-5 pp agregada ou duracao +-5 % (PROPOSTO, SEM FONTE)", alertas,
    diferenca: difTab, poc: P, novo: N,
  },
  ms: { harnessPoc: msPoc, harnessNovo: msNovo },
  gabarito_ci: { arquivo: "web/app/test/gabaritos/arena_poc_1x1.json", lutas: lutasGab.length },
  segundos: Math.round((Date.now() - t0) / 1000),
};
mkdirSync(join(APP, "scripts", "medicoes"), { recursive: true });
writeFileSync(join(APP, "scripts", "medicoes", "arena_fidelidade_lp1.json"), JSON.stringify(saida, null, 1) + "\n");
rmSync(TMP, { recursive: true, force: true });
console.log(`arena_fidelidade_lp1.json gravado (${saida.segundos} s)`);
if (difAncora.length || ctrlIguais !== nLutas) process.exit(1);
