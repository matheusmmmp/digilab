/* A bancada do custo do replay da batalha em tempo real (docs/ESPEC_COMBATE_TR.md, item 4; COMBATE-TR, etapa R0). Sem DOM e sem
   node:*: o mesmo modulo roda no Node (scripts/medir_replay_tr.ts) e no Chrome (a pagina que o script serve). Mede a simulacao de hoje
   (web/app/arena/, a do #446) e o combate por turnos de hoje (motor/combate.ts), como estao; nao mexe em nenhum dos dois.
   O que mede:
     - a luta 1 contra 1 no campo, CPU x CPU, um Digimon de cada lado (a duracao natural dela e o custo);
     - a luta 3 contra 3 no campo, a das medicoes da UP-ARENA (~100 s, ~6 000 passos): o caso "luta de ~100 s" da tarefa;
     - o controlador por regras como substituto (proxy): decidirV2 com a lista de uma forma adulta, chamado a cada R passos;
     - o combate por turnos de hoje (jogarV2), a linha de base. */
import { criarLuta, passo, LIMITE_MS, OPCOES_PADRAO, STATS_PADRAO, sorteiosPorFluxo, type ConfigLuta, type DadosArena } from "../arena/index.ts";
import { CV21E } from "../motor/constantes.ts";
import { decidirV2, estadoV2, jogarV2 } from "../motor/combate.ts";
import { lutadorBot } from "../motor/gambits_pet.ts";
import { criarRng } from "../motor/rng.ts";

export interface Opcoes { lutas1x1: number; lutas3x3: number; lutasTurnos: number; chamadasControlador: number; repeticoes: number; semente: number }
export const OPCOES: Opcoes = { lutas1x1: 200, lutas3x3: 40, lutasTurnos: 2000, chamadasControlador: 200_000, repeticoes: 5, semente: 20261029 };

/** os parceiros Rookie e Champion com status proprio, golpe e atlas (os da medicao da UP-ARENA, medicao.parceiro) */
export function parceiros(d: DadosArena): string[] {
  return Object.keys(d.status).filter(n => d.status[n].tipo === "PartnerDigiMon" && !d.status[n].estimado && !!d.golpes[n] && !!d.atlas.d[n]
    && ["Rookie", "Champion"].includes(d.status[n].estagio ?? ""));
}

function config(a: string[], b: string[]): ConfigLuta {
  const lado = (eq: string[]) => ({ equipe: eq as [string, string, string], fonte: "jogo" as const, nivel: 1, generico: { ...STATS_PADRAO } });
  return { cena: "campo", dific: OPCOES_PADRAO.dific, forca: OPCOES_PADRAO.forca, ritmo: OPCOES_PADRAO.ritmo, pvel: OPCOES_PADRAO.pvel,
    jogador: false, a: lado(a), b: lado(b) };
}

/** uma luta CPU x CPU ate o fim ou o limite: os passos, o relogio e uma impressao do resultado (para comparar Node e Chrome) */
function lutar(d: DadosArena, a: string[], b: string[], semente: number): { passos: number; relogio: number; marca: string } {
  const L = criarLuta(config(a, b), d, sorteiosPorFluxo(semente));
  let n = 0;
  while (!L.fim && L.relogio < LIMITE_MS) { passo(L); n++; }
  const hp = [...L.eq.a, ...L.eq.b].map(u => u.hp).join(",");
  return { passos: n, relogio: L.relogio, marca: `${L.vencedor ?? "-"}|${L.relogio}|${hp}` };
}

/** os confrontos sorteados da semente (o fluxo e so da bancada) */
function confrontos(d: DadosArena, n: number, tam: number, semente: number): [string[], string[]][] {
  const ps = parceiros(d), r = criarRng(semente), out: [string[], string[]][] = [];
  const p = () => ps[r.int(ps.length)];
  for (let i = 0; i < n; i++) out.push([Array.from({ length: tam }, p), Array.from({ length: tam }, p)]);
  return out;
}

const mediana = (xs: number[]): number => { const s = [...xs].sort((a, b) => a - b), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const quantil = (xs: number[], q: number): number => { const s = [...xs].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(q * s.length))]; };

export interface MedidaTR {
  lutas: number; passosMedio: number; passosP90: number; segundosJogoMedio: number; segundosJogoP90: number; semFim: number;
  /** a mediana das repeticoes: ms de relogio de parede por luta e microssegundos por passo */
  msPorLuta: number; usPorPasso: number; msPorLutaRepeticoes: number[];
  /** sha simples das marcas de resultado, na ordem (Node e Chrome tem de dar a mesma) */
  impressao: string;
}

function impressao(marcas: string[]): string {
  /* FNV-1a de 32 bits sobre as marcas; so compara Node e Chrome, nao e seguranca */
  let h = 0x811c9dc5;
  for (const s of marcas) for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return h.toString(16).padStart(8, "0");
}

function medirTR(d: DadosArena, confs: [string[], string[]][], o: Opcoes, agora: () => number): MedidaTR {
  /* aquecimento: o JIT compila antes da primeira repeticao medida */
  for (const [a, b] of confs.slice(0, Math.min(10, confs.length))) lutar(d, a, b, o.semente);
  const tempos: number[] = [];
  let res: ReturnType<typeof lutar>[] = [];
  for (let rep = 0; rep < o.repeticoes; rep++) {
    const t0 = agora();
    res = confs.map(([a, b], i) => lutar(d, a, b, o.semente + 1 + i));
    tempos.push(agora() - t0);
  }
  const passos = res.map(r => r.passos), seg = res.map(r => r.relogio / 1000), tot = passos.reduce((s, x) => s + x, 0), t = mediana(tempos);
  return {
    lutas: confs.length, passosMedio: Math.round(tot / confs.length), passosP90: quantil(passos, .9),
    segundosJogoMedio: +(seg.reduce((s, x) => s + x, 0) / seg.length).toFixed(1), segundosJogoP90: +quantil(seg, .9).toFixed(1),
    semFim: res.filter(r => r.relogio >= LIMITE_MS).length,
    msPorLuta: +(t / confs.length).toFixed(3), usPorPasso: +(1000 * t / tot).toFixed(3), msPorLutaRepeticoes: tempos.map(x => +(x / confs.length).toFixed(3)),
    impressao: impressao(res.map(r => r.marca)),
  };
}

/** o controlador por regras (proxy): uma decisao da lista do Duelista (8 regras, V21E) num estado de luta por turnos. A R1 troca as
    condicoes por versoes de tempo real; o custo por chamada deve ficar na mesma ordem (a mesma lista, as mesmas comparacoes) */
function medirControlador(o: Opcoes, agora: () => number): { chamadas: number; usPorChamada: number } {
  const A = lutadorBot("duelista", CV21E), B = lutadorBot("muralha", CV21E), E = estadoV2(A.cond, B.cond), rng = criarRng(o.semente);
  let soma = 0;
  for (let i = 0; i < 10_000; i++) soma += decidirV2(A.estilo, E, 0, rng, null, CV21E)[0].length;
  const tempos: number[] = [];
  for (let rep = 0; rep < o.repeticoes; rep++) {
    const t0 = agora();
    for (let i = 0; i < o.chamadasControlador; i++) soma += decidirV2(A.estilo, E, 0, rng, null, CV21E)[0].length;
    tempos.push(agora() - t0);
  }
  if (soma <= 0) throw new Error("controlador: nenhuma decisao");
  return { chamadas: o.chamadasControlador, usPorChamada: +(1000 * mediana(tempos) / o.chamadasControlador).toFixed(4) };
}

/** o combate por turnos de hoje, a linha de base: as 8 formas adultas da V21E umas contra as outras */
function medirTurnos(o: Opcoes, agora: () => number): { lutas: number; turnosMedio: number; msPorLuta: number } {
  const formas = ["duelista", "furioso", "espelho", "muralha", "sentinela", "emboscador", "vigia", "tita"];
  const L = formas.map(f => lutadorBot(f, CV21E));
  const jogar = () => { let turnos = 0; for (let i = 0; i < o.lutasTurnos; i++) turnos += jogarV2(L[i % 8], L[(i >> 3) % 8], o.semente + i, CV21E).turnos.length; return turnos; };
  jogar();
  const tempos: number[] = []; let turnos = 0;
  for (let rep = 0; rep < o.repeticoes; rep++) { const t0 = agora(); turnos = jogar(); tempos.push(agora() - t0); }
  return { lutas: o.lutasTurnos, turnosMedio: +(turnos / o.lutasTurnos).toFixed(1), msPorLuta: +(mediana(tempos) / o.lutasTurnos).toFixed(4) };
}

export interface ResultadoBancada {
  opcoes: Opcoes; parceiros: number;
  luta1x1: MedidaTR; luta3x3: MedidaTR;
  controlador: { chamadas: number; usPorChamada: number };
  turnos: { lutas: number; turnosMedio: number; msPorLuta: number };
}

export function bancada(d: DadosArena, agora: () => number, o: Opcoes = OPCOES): ResultadoBancada {
  return {
    opcoes: o, parceiros: parceiros(d).length,
    luta1x1: medirTR(d, confrontos(d, o.lutas1x1, 1, o.semente), o, agora),
    luta3x3: medirTR(d, confrontos(d, o.lutas3x3, 3, o.semente + 7), o, agora),
    controlador: medirControlador(o, agora),
    turnos: medirTurnos(o, agora),
  };
}
