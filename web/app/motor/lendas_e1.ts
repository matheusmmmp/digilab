/* MITOLOGIA, E1 (docs/TAREFA_V3_MITOLOGIA.md, secao 10): mais sinais e segredos, ainda como funcao pura do pet refeito do log. Nada aqui
   muda o motor, o cerebro ou a luta. Le o que o replay ja deriva (o forcaLutas, o feitosCuidado, o mundo.decisoes, o mundo.regioes, o
   mundo.levadas e o log) e devolve:
     - os sinais dos cinco deuses do aro (D-MM-6): Coragem, Amizade, Conhecimento, Sinceridade e Diversao (a nuvem da E0);
     - o termometro do Myotismon, fora do aro: a repeticao a exaustao num dia escurece a ilha (so vista, D-MM-10);
     - a pedra do macaco na mata (o pet perto dela a noite), as pegadas ate ela (muita exploracao na vida) e o dia 81 de vida;
     - as falas novas do oraculo e o enigma (o texto, por modelo, sem LLM; o criterio F0).
   Quem mostra fica em src/, atras da chave `mitologia`. */
import { CMU_MVP, LAYOUT_MUNDO_GRANDE, TICK_INICIAL, TPD, type ConfigMundo } from "./constantes.ts";
import { NPC } from "./bots.ts";
import { eNoite } from "./estado.ts";
import { centroDaCelula, distancia } from "./mundo.ts";
import { variadaDe, type FontesLenda } from "./lendas.ts";

/** os numeros da E1, DECIDIDOS pelo Matheus em 2026-11-11 ("Aprovo os gatilhos"; D-E1-2 no registro), SEM FONTE */
export const CMIT_E1 = {
  /** Coragem: vencer um lider da Campanha com `total` >= esta razao x a forca do pet na entrada */
  razaoCoragem: 1.0,
  /** Amizade: o dono faz carinho ao menos `amizadeCarinho` e brinca ao menos `amizadeBrincar` vezes por dia, `amizadeDias` dias seguidos
      (a constancia, nao a maratona; o sinal sai no dia que fecha a sequencia, e a contagem recomeca) */
  amizadeCarinho: 3, amizadeBrincar: 2, amizadeDias: 3,
  /** Conhecimento: num dia de jogo, o pet explora ao menos isto (um dia de curiosidade; as 4 regioes num dia nao aconteciam na vida comum,
      D-E1-3) */
  conhecimentoExploracoes: 6,
  /** Sinceridade: num dia de jogo, o dono atende ao menos isto de chamados do pet */
  sinceridadeChamados: 3,
  /** o Myotismon: na janela do ultimo dia, ao menos `myoMinAcoes` acoes do dono com a mais repetida em >= `myoFracao`, ou ao menos
      `myoMesmoRival` lutas contra o mesmo rival */
  myoMinAcoes: 12, myoFracao: 0.75, myoMesmoRival: 6, myoJanela: TPD,
  /** a pedra do macaco: a celula (na mata, em terra nos mapas de 64 x 30) e o raio, em celulas, de onde o pet a "acha" a noite. Na ilha
      grande (128 x 60, v24) a mata vai da coluna 96 a 127, e a pedra fica em `pedraCelulaGrande`, em terra e longe das arvores e dos marcos */
  pedraCelula: [56, 20] as const, pedraCelulaGrande: [104, 28] as const, pedraRaioCelulas: 2,
  /** as pegadas: quantas decisoes de explorar na vida inteira (em qualquer lugar; elas levam do ninho a pedra na mata, D-E1-3) */
  pegadasExploracoes: 60,
  /** o dia de vida do evento raro (as 81 provacoes da estrada) */
  diaRaro: 81,
} as const;

export type Deus = "coragem" | "amizade" | "conhecimento" | "sinceridade" | "diversao";
export const DEUSES: readonly Deus[] = ["coragem", "amizade", "conhecimento", "sinceridade", "diversao"];
/** o nome na tela e o brasao (os nomes do Digimon: brasa Coragem, cirro Amizade, ferrugem Conhecimento, limo Sinceridade; a Diversao e o
    deus do macaco, encarnado pelo Piedmon, D-MM-4) */
export const NOME_DEUS: Readonly<Record<Deus, string>> = {
  coragem: "Coragem", amizade: "Amizade", conhecimento: "Conhecimento", sinceridade: "Sinceridade", diversao: "Diversão",
};
export const SINAL_DEUS: Readonly<Record<Deus, string>> = {
  coragem: "uma chama que não queima, perto do ninho",
  amizade: "duas flores que se viram uma para a outra",
  conhecimento: "um marco com um risco que ninguém lembra de ter feito",
  sinceridade: "um broto verde que nasce de um dia para o outro",
  diversao: "uma nuvenzinha dourada parada sobre o ninho",
};

export interface SinalDeus { deus: Deus; tick: number; dia: number }

/** o que a E1 le alem do que a E0 le (o Motor cumpre) */
export interface FontesE1 extends FontesLenda {
  feitosCuidado: readonly { tick: number; tipo: string }[];
  mundo: (FontesLenda["mundo"] & {
    regioes?: readonly { tick: number; de: number; para: number }[];
    levadas?: readonly { tick: number; para: readonly [number, number] }[];
    cm?: ConfigMundo;
  }) | null;
}

const diaDe = (tick: number) => Math.floor(tick / TPD);

/** um evento por dia: o tick em que a contagem `chega` no dia, dados os pontos (tick, chave) em ordem */
function porDia<T>(pontos: readonly [number, T][], chega: (contagem: Map<T, number>) => boolean): number[] {
  const out: number[] = [];
  let dia = -1, cont = new Map<T, number>(), feito = false;
  for (const [tick, k] of [...pontos].sort((a, b) => a[0] - b[0])) {
    const d = diaDe(tick);
    if (d !== dia) { dia = d; cont = new Map(); feito = false; }
    if (feito) continue;
    cont.set(k, (cont.get(k) ?? 0) + 1);
    if (chega(cont)) { out.push(tick); feito = true; }
  }
  return out;
}

/** os sinais dos cinco deuses, por tick (no maximo um por deus por dia) */
export function sinaisDe(f: FontesE1): SinalDeus[] {
  const c = CMIT_E1, out: SinalDeus[] = [];
  const add = (deus: Deus, ticks: number[]) => { for (const t of ticks) out.push({ deus, tick: t, dia: diaDe(t) }); };
  /* Coragem: a vitoria contra um lider da Campanha que nao e mais fraco que o pet */
  const coragem: [number, string][] = [];
  for (const l of f.forcaLutas) {
    const npc = NPC[l.rival];
    if (l.resultado === "vitoria" && npc && l.forcaPet > 0 && npc.total >= c.razaoCoragem * l.forcaPet) coragem.push([l.tick, "v"]);
  }
  add("coragem", porDia(coragem, m => (m.get("v") ?? 0) >= 1));
  /* Amizade: os dias de carinho e brincadeira do dono; o sinal no dia que fecha amizadeDias seguidos */
  const dono: [number, string][] = [];
  for (const ev of f.log) if (ev[1] === "d" && (ev[2] === "acariciar" || ev[2] === "brincar")) dono.push([ev[0] as number, ev[2] as string]);
  const diasBons = porDia(dono, m => (m.get("acariciar") ?? 0) >= c.amizadeCarinho && (m.get("brincar") ?? 0) >= c.amizadeBrincar);
  const amizade: number[] = [];
  let seguidos = 0, diaAntes = -2;
  for (const t of diasBons) {
    const d = diaDe(t);
    seguidos = d === diaAntes + 1 ? seguidos + 1 : 1;
    diaAntes = d;
    if (seguidos >= c.amizadeDias) { amizade.push(t); seguidos = 0; diaAntes = -2; }
  }
  add("amizade", amizade);
  /* Conhecimento: um dia de muita exploracao (as decisoes de explorar do mundo) */
  const expl: [number, string][] = [];
  for (const d of f.mundo?.decisoes ?? []) if (d.acao === "explorar" && typeof d.tick === "number") expl.push([d.tick, "e"]);
  add("conhecimento", porDia(expl, m => (m.get("e") ?? 0) >= c.conhecimentoExploracoes));
  /* Sinceridade: os chamados atendidos */
  const cham: [number, string][] = f.feitosCuidado.filter(x => x.tipo === "chamado").map(x => [x.tick, "c"]);
  add("sinceridade", porDia(cham, m => (m.get("c") ?? 0) >= c.sinceridadeChamados));
  /* Diversao: a brincadeira variada da E0 */
  add("diversao", variadaDe(f).map(e => e.tick));
  return out.sort((a, b) => a.tick - b.tick || DEUSES.indexOf(a.deus) - DEUSES.indexOf(b.deus));
}

/** os deuses com sinal na ilha no tick (cada sinal vale um dia de jogo a partir do evento) */
export function sinaisNoTick(sinais: readonly SinalDeus[], tick: number): Deus[] {
  const out = new Set<Deus>();
  for (const s of sinais) if (s.tick <= tick && tick < s.tick + TPD) out.add(s.deus);
  return DEUSES.filter(d => out.has(d));
}

/** o termometro do Myotismon no tick: a repeticao a exaustao na janela do ultimo dia (as acoes do dono, ou as lutas contra o mesmo rival) */
export function myotismonNoTick(f: FontesE1, tick: number): boolean {
  const c = CMIT_E1, desde = tick - c.myoJanela;
  const acoes = new Map<string, number>();
  let n = 0;
  for (const ev of f.log) {
    const t = ev[0] as number;
    if (ev[1] !== "d" || t <= desde || t > tick) continue;
    n++; acoes.set(ev[2] as string, (acoes.get(ev[2] as string) ?? 0) + 1);
  }
  if (n >= c.myoMinAcoes && Math.max(...acoes.values()) >= c.myoFracao * n) return true;
  const rivais = new Map<string, number>();
  for (const l of f.forcaLutas) if (l.tick > desde && l.tick <= tick) rivais.set(l.rival, (rivais.get(l.rival) ?? 0) + 1);
  return [...rivais.values()].some(k => k >= c.myoMesmoRival);
}

/** o Myotismon ja apareceu alguma vez ate o tick? (a mesma regra do myotismonNoTick, em janela deslizante sobre o log e as lutas) */
export function myotismonJaApareceu(f: FontesE1, ate: number): boolean {
  const c = CMIT_E1;
  const acoes = f.log.filter(ev => ev[1] === "d" && (ev[0] as number) <= ate).map(ev => [ev[0] as number, ev[2] as string] as const);
  const cont = new Map<string, number>();
  let i = 0;
  for (let j = 0; j < acoes.length; j++) {
    cont.set(acoes[j][1], (cont.get(acoes[j][1]) ?? 0) + 1);
    while (acoes[i][0] <= acoes[j][0] - c.myoJanela) { cont.set(acoes[i][1], cont.get(acoes[i][1])! - 1); i++; }
    const n = j - i + 1;
    if (n >= c.myoMinAcoes && Math.max(...cont.values()) >= c.myoFracao * n) return true;
  }
  const lutas = f.forcaLutas.filter(l => l.tick <= ate), porRival = new Map<string, number[]>();
  for (const l of lutas) {
    const ts = porRival.get(l.rival) ?? [];
    ts.push(l.tick);
    porRival.set(l.rival, ts);
    const dentro = ts.filter(t => t > l.tick - c.myoJanela).length;
    if (dentro >= c.myoMesmoRival) return true;
  }
  return false;
}

/** a celula da pedra no mundo do pet (a ilha grande tem a sua, na mata dela) */
export function pedraCelulaDe(cm: ConfigMundo = CMU_MVP): readonly [number, number] {
  return cm.layout.nome === LAYOUT_MUNDO_GRANDE.nome ? CMIT_E1.pedraCelulaGrande : CMIT_E1.pedraCelula;
}
/** onde fica a pedra do macaco (subunidades do mundo) */
export function pedraEm(cm: ConfigMundo = CMU_MVP): [number, number] {
  return centroDaCelula(pedraCelulaDe(cm), cm);
}

/** o tick em que o pet achou a pedra: o fim de uma decisao, ou o ponto onde o dono o soltou, perto dela e de noite (null: ainda nao) */
export function pedraAchadaDe(f: FontesE1): number | null {
  const cm = f.mundo?.cm ?? CMU_MVP, [px, py] = pedraEm(cm), raio = CMIT_E1.pedraRaioCelulas * cm.sub;
  const perto = (x: unknown, y: unknown, t: unknown): t is number =>
    typeof x === "number" && typeof y === "number" && typeof t === "number" && distancia(x - px, y - py) <= raio && eNoite(t % TPD);
  let melhor: number | null = null;
  for (const d of f.mundo?.decisoes ?? []) if (perto(d.x, d.y, d.tick) && (melhor === null || (d.tick as number) < melhor)) melhor = d.tick as number;
  for (const l of f.mundo?.levadas ?? []) if (perto(l.para[0], l.para[1], l.tick) && (melhor === null || l.tick < melhor)) melhor = l.tick;
  return melhor;
}

/** o tick em que as pegadas aparecem: a decisao de explorar numero `pegadasExploracoes` da vida (null: ainda nao) */
export function pegadasDe(f: FontesE1): number | null {
  let n = 0;
  for (const d of f.mundo?.decisoes ?? []) {
    if (d.acao !== "explorar" || typeof d.tick !== "number") continue;
    if (++n >= CMIT_E1.pegadasExploracoes) return d.tick;
  }
  return null;
}

/** o dia de vida no tick (o pet nasce no TICK_INICIAL: o primeiro dia e o 1) */
export const diaDeVida = (tick: number): number => Math.floor((tick - TICK_INICIAL) / TPD) + 1;
/** o primeiro tick do dia raro */
export const tickDoDiaRaro = (): number => TICK_INICIAL + (CMIT_E1.diaRaro - 1) * TPD;

/* ------------------------------------------------------------------ as falas novas do oraculo e o enigma (por nos; nenhuma nomeia a obra) */
export const FALA_PEDRA = "Você achou a pedra. Dizem que o macaco nasceu de uma assim: o céu e a terra a aqueceram por tanto tempo que ela " +
  "rachou, e de dentro saiu alguém com pressa de ver tudo.";
export const FALA_PEGADAS = "Pegadas pequenas, de quem anda em quatro e pensa em duas. Siga-as numa noite clara.";
export const FALA_DIA_RARO = "Oitenta e um dias. Foram oitenta e uma as provações da estrada, e nenhuma foi vencida sozinho. " +
  "Hoje os cinco olham para vocês ao mesmo tempo.";
export const ENIGMA = {
  pergunta: "Tenho cem caminhos e nenhum pé. Levo o macaco aonde ele quiser e sumo quando o sol esquenta. O que sou?",
  opcoes: ["O vento", "A nuvem", "A estrada"] as const,
  certa: 1,
  acerto: "Isso. A nuvem dele ainda passa por aqui às vezes. Deixei uma coisa perto do ninho, para quem pensa antes de responder.",
  erro: "Quase. Pense no que voa sem asas e não deixa rastro.",
} as const;
export const FALA_PESSEGO = "um pêssego dourado perto do ninho, presente de quem decifra";
