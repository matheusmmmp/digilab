/* MITOLOGIA, E0 (docs/TAREFA_V3_MITOLOGIA.md): as lendas como funcao pura do pet refeito do log. Nada aqui muda o motor, o cerebro
   ou a luta: le so o que o replay ja deriva (o forcaLutas, o mundo.decisoes e o log) e devolve os eventos sutis da mitologia, sempre os
   mesmos para o mesmo log. Quem mostra (o balao do oraculo Jijimon, a nuvem na ilha) fica em src/, atras da chave `mitologia`.

   Os dois eventos da E0 (a Sintese da pesquisa no vault, secao 5; D-MM-16):
     - a hybris: o par (dono e pet, D-MM-18) desafia um lider da Campanha muito acima da forca do pet e perde;
     - a brincadeira variada: num dia de jogo, o pet tem atividades de tedio variadas (as do DS-4: bola, brincar, explorar e o dono
       brincar), e nao a mesma repetida. */
import { TPD } from "./constantes.ts";
import { NPC } from "./bots.ts";

/** os numeros da E0, DECIDIDOS pelo Matheus em 2026-11-11 ("Aprovo os números"; D-E0-4 no registro), SEM FONTE */
export const CMIT = {
  /** a hybris: a forca do lider (o `total` do NPC, a soma dos 6 stats) sobre a do pet na entrada (a soma dos 6 de statsDoPet) */
  razaoHybris: 1.3,
  /** a hybris conta no maximo uma vez por dia de jogo (perder de novo para o mesmo lider no mesmo dia nao e outro pedaco da lenda) */
  hybrisPorDia: 1,
  /** a brincadeira variada: quantas atividades de tedio diferentes num dia de jogo */
  minVariedade: 3,
  /** a nuvem fica na ilha por um dia de jogo depois do evento */
  duracaoDetalhe: TPD,
} as const;

export type AtividadeLenda = "bola" | "brincar" | "explorar" | "dono_brinca";
export type EventoLenda =
  | { tipo: "hybris"; tick: number; rival: string; forcaPet: number; forcaRival: number; parte: number }
  | { tipo: "variada"; tick: number; dia: number; atividades: AtividadeLenda[] };

/** o que lendas() le do pet (o Motor cumpre; os testes passam registros sinteticos) */
export interface FontesLenda {
  forcaLutas: readonly { tick: number; rival: string; forcaPet: number; resultado: string }[];
  log: readonly (readonly unknown[])[];
  mundo: { decisoes: readonly Record<string, unknown>[] } | null;
}

/** os eventos da hybris, na ordem das lutas, no maximo hybrisPorDia por dia de jogo; `parte` conta as hybris anteriores (o pedaco da
    lenda que o oraculo conta) */
export function hybrisDe(lutas: FontesLenda["forcaLutas"]): Extract<EventoLenda, { tipo: "hybris" }>[] {
  const out: Extract<EventoLenda, { tipo: "hybris" }>[] = [];
  const porDia = new Map<number, number>();
  for (const l of lutas) {
    if (l.resultado !== "derrota") continue;
    const npc = NPC[l.rival];
    if (!npc) continue;                                   // so os lideres da Campanha (os torneios e a Arena ficam de fora na E0)
    if (!(l.forcaPet > 0)) throw new Error(`forca do pet nao positiva na luta do tick ${l.tick}: ${l.forcaPet}`);
    const dia = Math.floor(l.tick / TPD), n = porDia.get(dia) ?? 0;
    if (npc.total >= CMIT.razaoHybris * l.forcaPet && n < CMIT.hybrisPorDia) {
      porDia.set(dia, n + 1);
      out.push({ tipo: "hybris", tick: l.tick, rival: l.rival, forcaPet: l.forcaPet, forcaRival: npc.total, parte: out.length });
    }
  }
  return out;
}

/** as atividades de tedio de cada decisao do mundo (a mesma regra do atividadeMundo de motor_corpo_mundo.ts) e o dono brincar do log */
function atividadesNoTempo(f: FontesLenda): [number, AtividadeLenda][] {
  const out: [number, AtividadeLenda][] = [];
  for (const d of f.mundo?.decisoes ?? []) {
    const tick = d.tick, acao = d.acao;
    if (typeof tick !== "number") throw new Error(`decisao do mundo sem tick: ${JSON.stringify(d)}`);
    if (acao === "brincar") out.push([tick, d.brincou_com_bola === true ? "bola" : "brincar"]);
    else if (acao === "explorar") out.push([tick, "explorar"]);
  }
  for (const ev of f.log) if (ev[1] === "d" && ev[2] === "brincar") out.push([ev[0] as number, "dono_brinca"]);
  return out.sort((a, b) => a[0] - b[0]);
}

/** os eventos da brincadeira variada: no maximo um por dia de jogo, no tick em que a atividade diferente de numero minVariedade aparece */
export function variadaDe(f: FontesLenda): Extract<EventoLenda, { tipo: "variada" }>[] {
  const out: Extract<EventoLenda, { tipo: "variada" }>[] = [];
  let dia = -1, vistas: AtividadeLenda[] = [], feito = false;
  for (const [tick, a] of atividadesNoTempo(f)) {
    const d = Math.floor(tick / TPD);
    if (d !== dia) { dia = d; vistas = []; feito = false; }
    if (feito || vistas.includes(a)) continue;
    vistas.push(a);
    if (vistas.length >= CMIT.minVariedade) { out.push({ tipo: "variada", tick, dia, atividades: [...vistas] }); feito = true; }
  }
  return out;
}

/** todos os eventos da mitologia do pet, por tick (no empate, a hybris antes) */
export function lendas(f: FontesLenda): EventoLenda[] {
  return [...hybrisDe(f.forcaLutas), ...variadaDe(f)].sort((a, b) => a.tick - b.tick || (a.tipo === "hybris" ? -1 : 1) - (b.tipo === "hybris" ? -1 : 1));
}

/** a nuvem do dia: o ultimo evento da brincadeira variada que ainda vale no tick (por duracaoDetalhe ticks), ou null */
export function detalheNoTick(eventos: readonly EventoLenda[], tick: number): Extract<EventoLenda, { tipo: "variada" }> | null {
  for (let i = eventos.length - 1; i >= 0; i--) {
    const e = eventos[i];
    if (e.tipo === "variada" && e.tick <= tick && tick < e.tick + CMIT.duracaoDetalhe) return e;
  }
  return null;
}

/* ------------------------------------------------------------------ a voz do oraculo (por modelo, sem LLM; D-MM-11 (a))
   A lenda e um mito proprio no molde do macaco que desafiou o Ceu (resposta 3 do Matheus, 2026-11-11): reescrita por nos do enredo de
   dominio publico, sem nomear a obra na fala e sem texto de traducao (o criterio F0); o credito vai na tela de creditos. Um pedaco por
   hybris, na ordem; contada inteira, o oraculo fecha. O par ouve junto (D-MM-18): a fala fala com os dois. */
export const NOME_ORACULO = "Jijimon";
export const LENDA_DO_MACACO: readonly string[] = [
  "Conheço essa pressa. Houve um macaco, nascido de uma pedra, que achava que nada era alto demais para ele.",
  "O macaco aprendeu a saltar de nuvem em nuvem e começou a chamar o céu de casa. Ninguém o tinha convidado.",
  "Ele desafiou os guardiões um a um. Cada vitória o deixava maior por dentro do que por fora.",
  "Um dia apostou que sairia da mão de quem o desafiava. Saltou até o fim do mundo… e ainda era a palma da mão.",
  "A mão virou montanha, e o macaco ficou embaixo, só com a cabeça de fora, vendo as estações passarem.",
  "Ninguém o soltou pela força. Soltou-o quem precisava de companhia na estrada, e ele aprendeu a andar ao lado.",
  "Perder para quem é maior não é vergonha. Vergonha é não perguntar quanto se é. Vocês dois sabem quanto são?",
];
export const LENDA_CONTADA = "A lenda já foi contada inteira. O resto da estrada é de vocês dois.";

/** o que o oraculo diz numa hybris */
export function falaDoOraculo(e: Extract<EventoLenda, { tipo: "hybris" }>): string {
  return e.parte < LENDA_DO_MACACO.length ? LENDA_DO_MACACO[e.parte] : LENDA_CONTADA;
}
