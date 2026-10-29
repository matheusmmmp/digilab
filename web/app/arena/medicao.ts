/* A medicao de equilibrio da arena (docs/TAREFA_V2_UP_ARENA.md, item 4): o harness do arena_equilibrio.md (recuperado na etapa 0,
   remaster/fonte/scripts_arena/harness_equilibrio.js) em Node, com as mesmas sementes por luta. Modo "unico": a sequencia unica do
   prototipo (P1: so teste e medicao); modo "fluxos": o jogo, um fluxo por uso. Sem DOM e sem arquivo: quem grava e scripts/medir_arena.ts. */
import { criarRng } from "../motor/rng.ts";
import { LIMITE_MS, OPCOES_PADRAO, STATS_PADRAO, type Dificuldade } from "./constantes.ts";
import { sementeArena, sorteioUnico, sorteiosPorFluxo } from "./rng.ts";
import { criarLuta, passo } from "./sim.ts";
import type { ConfigLuta, DadosArena, IdCena, Lado, Sorteios } from "./tipos.ts";

export type ModoSorteio = "unico" | "fluxos";
export const sorteiosDaLuta = (modo: ModoSorteio, semente: number): Sorteios =>
  modo === "unico" ? sorteioUnico(criarRng(semente)) : sorteiosPorFluxo(semente);

export interface ResultadoLuta {
  vencedor: Lado | null; fim: boolean; relogio: number;
  danoAmb: number; danoGolpe: number;
  ringue: number; bloq: number; pilar: number; runa: number; caiuAmb: number; errou: number;
}

export function configCpu(cena: IdCena, a: string[], b: string[], o: { forca?: number; nivelA?: number; nivelB?: number; dific?: Dificuldade } = {}): ConfigLuta {
  const lado = (eq: string[], nivel: number) => ({ equipe: eq, fonte: "jogo" as const, nivel, generico: { ...STATS_PADRAO } });
  return { cena, dific: o.dific ?? OPCOES_PADRAO.dific, forca: o.forca ?? OPCOES_PADRAO.forca, ritmo: OPCOES_PADRAO.ritmo, pvel: OPCOES_PADRAO.pvel,
    jogador: false, a: lado(a, o.nivelA ?? 1), b: lado(b, o.nivelB ?? 1) };
}

/** uma luta CPU x CPU ate o fim ou o limite, com as contagens do harness (que ele tirava do texto do log) */
export function lutarAteOFim(cfg: ConfigLuta, dados: DadosArena, r: Sorteios): ResultadoLuta {
  const L = criarLuta(cfg, dados, r);
  const res: ResultadoLuta = { vencedor: null, fim: false, relogio: 0, danoAmb: 0, danoGolpe: 0, ringue: 0, bloq: 0, pilar: 0, runa: 0, caiuAmb: 0, errou: 0 };
  while (!L.fim && L.relogio < LIMITE_MS) {
    for (const e of passo(L)) {
      if (e.tipo === "dano") res.danoGolpe += e.perda;
      else if (e.tipo === "ambiente") res.danoAmb += e.perda;
      else if (e.tipo === "queda_ringue") res.ringue++;
      else if (e.tipo === "tiro_bloqueado") res.bloq++;
      else if (e.tipo === "pilar") res.pilar++;
      else if (e.tipo === "runa") res.runa++;
      else if (e.tipo === "queda" && e.motivo !== null) res.caiuAmb++;
      else if (e.tipo === "tiro_errou" || e.tipo === "golpe_ar") res.errou++;
    }
  }
  res.vencedor = L.vencedor; res.fim = L.fim; res.relogio = L.relogio;
  return res;
}

const parceiro = (d: DadosArena, n: string) => d.status[n].tipo === "PartnerDigiMon" && !d.status[n].estimado && !!d.golpes[n] && !!d.atlas.d[n];

export interface MedidaArena { lutas: number; dur: number; p90: number; timeouts: number; ambPct: number; azul: string; ringue: number; bloq: number; pilar: number; runa: number; caiuAmb: number; errou: number }

/** o "medir" do harness: nConf confrontos de equipes de 3 parceiros Rookie e Champion sorteados, cada um com os lados trocados */
export function medirArenas(d: DadosArena, ids: IdCena[], nConf: number, semente: number, modo: ModoSorteio, forca = OPCOES_PADRAO.forca): Record<string, MedidaArena> {
  const parceiros = Object.keys(d.status).filter(n => parceiro(d, n) && ["Rookie", "Champion"].includes(d.status[n].estagio ?? ""));
  const sorteio = criarRng(modo === "unico" ? semente : sementeArena(semente, "sorteio")), confs: [string[], string[]][] = [];
  for (let i = 0; i < nConf; i++) { const p = () => parceiros[Math.floor(sorteio.random() * parceiros.length)]; confs.push([[p(), p(), p()], [p(), p(), p()]]); }
  const out: Record<string, MedidaArena> = {};
  for (const id of ids) {
    const durs: number[] = [], ev = { ringue: 0, bloq: 0, pilar: 0, runa: 0, caiuAmb: 0, errou: 0 };
    let ambT = 0, atkT = 0, winA = 0, tout = 0, k = 0;
    for (const [ea, eb] of confs) for (const lado of [0, 1]) {
      const [A, B] = lado ? [eb, ea] : [ea, eb];
      const r = lutarAteOFim(configCpu(id, A, B, { forca }), d, sorteiosDaLuta(modo, semente + 1000 + k++));
      if (!r.fim) tout++;
      durs.push(r.relogio / 1000); ambT += r.danoAmb; atkT += r.danoGolpe;
      if (r.vencedor === "a") winA++;
      for (const c of Object.keys(ev) as (keyof typeof ev)[]) ev[c] += r[c];
    }
    const n = durs.length; durs.sort((a, b) => a - b);
    out[id] = { lutas: n, dur: +(durs.reduce((a, b) => a + b, 0) / n).toFixed(0), p90: +durs[Math.floor(n * 0.9)].toFixed(0), timeouts: tout,
      ambPct: +(100 * ambT / (ambT + atkT)).toFixed(1), azul: `${winA}/${n}`,
      ...Object.fromEntries(Object.entries(ev).map(([c, v]) => [c, +(v / n).toFixed(1)])) as typeof ev };
  }
  return out;
}

/** o "duelo": campo de treino, equipes de 3 copias do mesmo Digimon, atributo desligado */
export function duelo(d: DadosArena, na: string, nb: string, semente: number, modo: ModoSorteio, nivA = 1, nivB = 1): ResultadoLuta {
  return lutarAteOFim(configCpu("campo", [na, na, na], [nb, nb, nb], { forca: 1, nivelA: nivA, nivelB: nivB }), d, sorteiosDaLuta(modo, semente));
}

export interface LinhaRodizio { n: string; wr: number; proj: boolean }
export interface MedidaRodizio { lutas: number; tempoMedio: number; semFim: number; dist: string; corpo: string; desvio: string; faixa: string; tabela: LinhaRodizio[] }
/** o "rodizio"/"teste": todos contra todos dentro de um estagio, lados trocados, uma luta por semente */
export function rodizio(d: DadosArena, estagio: string, sementes: number[], modo: ModoSorteio): MedidaRodizio {
  const ns = Object.keys(d.status).filter(n => parceiro(d, n) && d.status[n].estagio === estagio);
  const w: Record<string, number> = Object.fromEntries(ns.map(n => [n, 0])), j: Record<string, number> = Object.fromEntries(ns.map(n => [n, 0]));
  let tempo = 0, nl = 0, tout = 0;
  for (let i = 0; i < ns.length; i++) for (let k = i + 1; k < ns.length; k++) for (const sd of sementes) for (const [a, b] of [[ns[i], ns[k]], [ns[k], ns[i]]]) {
    const r = duelo(d, a, b, sd * 7919 + i * 131 + k, modo); j[a]++; j[b]++; tempo += r.relogio / 1000; nl++;
    if (r.vencedor === "a") w[a]++; else if (r.vencedor === "b") w[b]++; else { w[a] += 0.5; w[b] += 0.5; tout++; }
  }
  const tabela = ns.map(n => ({ n, wr: +(w[n] / j[n]).toFixed(2), proj: !!d.golpes[n].proj })).sort((p, q) => q.wr - p.wr);
  const g = (f: (t: LinhaRodizio) => boolean) => { const x = tabela.filter(f); return x.length ? (x.reduce((a, b) => a + b.wr, 0) / x.length).toFixed(2) : "-"; };
  const wr = tabela.map(t => t.wr), dp = Math.sqrt(wr.reduce((a, b) => a + (b - 0.5) ** 2, 0) / wr.length);
  return { lutas: nl, tempoMedio: +(tempo / nl).toFixed(0), semFim: tout, dist: g(t => t.proj), corpo: g(t => !t.proj), desvio: dp.toFixed(3),
    faixa: Math.min(...wr).toFixed(2) + "–" + Math.max(...wr).toFixed(2), tabela };
}

/** o "cruzar": os 8 primeiros parceiros de um estagio contra os 8 de outro, lados trocados; devolve a vitoria (%) do segundo */
export function cruzar(d: DadosArena, e1: string, e2: string, modo: ModoSorteio, nivel1 = 1, nivel2 = 1): number {
  const por = (e: string) => Object.keys(d.status).filter(n => parceiro(d, n) && d.status[n].estagio === e).slice(0, 8);
  let w = 0, n = 0;
  for (const a of por(e1)) for (const b of por(e2)) for (const lado of [0, 1]) {
    const [x, y, nx, ny] = lado ? [b, a, nivel2, nivel1] : [a, b, nivel1, nivel2];
    const r = duelo(d, x, y, n * 31 + 5, modo, nx, ny); n++;
    const alto = lado ? r.vencedor === "a" : r.vencedor === "b"; if (alto) w++; else if (!r.vencedor) w += 0.5;
  }
  return +(100 * w / n).toFixed(0);
}
export const PARES_ESTAGIOS = [["Rookie", "Champion"], ["Champion", "Ultimate"], ["Ultimate", "Mega"], ["Rookie", "Ultimate"], ["Rookie", "Mega"]] as const;
