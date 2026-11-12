/* A leitura do gosto em linguagem de jogo (docs/PLANO_UX_GOSTO_VISUAL.md, seção 4; UX-GV-4 e UX-GV-5, aprovadas em 2026-11-11): as contas
   sem tela que o painel da TV mostra. Uma linha por componente, com as três origens separadas (de nascença, de tanto ver, do carinho), os
   componentes que valem aparecer primeiro, a frase para o leitor de tela e o motivo da reação em palavras (a PR-3 da prancha).
   Fora do motor, do log e do save, como o resto do protótipo. Sem DOM. Os números e os textos são PROPOSTOS, SEM FONTE. */
import {
  COMPONENTES, NOME_COMPONENTE, PALAVRAS, alvo, alvos, gostaMaisDe, valores, type Componente, type EstadoGosto, type Inato, type Reacao, type Sentido,
} from "./gosto.ts";

export const IMAGEM: readonly Componente[] = ["cor", "brilho", "movimento", "complexidade"];
export const SOM: readonly Componente[] = ["volume", "variacao", "timbre"];
/** a partir de quanto o aprendido conta como "mudou" (para a linha entrar na lista curta) */
export const MUDOU = 0.05;
/** quantas linhas a lista curta mostra no máximo */
export const LINHAS_CURTAS = 3;

export interface LinhaGosto {
  k: Componente; nome: string; baixo: string; alto: string;
  /** de 0 a 1: o ponto de nascença, o deslocamento de tanto ver, o do carinho e o ponto de hoje (limitado a [0, 1]) */
  nascenca: number; deVer: number; doCarinho: number; hoje: number;
}

/** uma linha por componente, na ordem de sempre */
export function linhasDoGosto(ina: Inato, e: EstadoGosto, quais: readonly Componente[] = COMPONENTES): LinhaGosto[] {
  return quais.map(k => ({ k, nome: NOME_COMPONENTE[k], baixo: PALAVRAS[k][0], alto: PALAVRAS[k][1],
    nascenca: ina.otimo[k], deVer: e.exposicao[k], doCarinho: e.carinho[k], hoje: alvo(ina, e, k) }));
}

/** as linhas do gosto do cerebro (a decisao C, D-GV-TVJOGO-5; os pets com a TV no cerebro): o de nascenca e o de tanto ver vem do DigiBrain
    (`Motor.gostoVisualDoCerebro`, em [0, 1]); o carinho ainda nao entra no gosto do cerebro (0). Os componentes sao os canais da tela */
export function linhasDoCerebro(nascenca: Readonly<Record<string, number>>, deVer: Readonly<Record<string, number>>,
                                quais: readonly Componente[] = COMPONENTES): LinhaGosto[] {
  return quais.map(k => {
    const a = nascenca[k], v = deVer[k];
    if (a === undefined || v === undefined) throw new Error(`o gosto do cerebro sem o canal ${k}`);
    return { k, nome: NOME_COMPONENTE[k], baixo: PALAVRAS[k][0], alto: PALAVRAS[k][1], nascenca: a, deVer: v, doCarinho: 0, hoje: Math.min(1, Math.max(0, a + v)) };
  });
}
/** os pontos de hoje e os de nascenca de um conjunto de linhas (para o "Gosta mais de") */
export function pontosDasLinhas(linhas: readonly LinhaGosto[], de: "hoje" | "nascenca"): Record<Componente, number> {
  const r = Object.fromEntries(COMPONENTES.map(k => [k, 0.5])) as Record<Componente, number>;
  for (const l of linhas) r[l.k] = l[de];
  return r;
}

/** a lista curta: os dois componentes da frase "Gosta mais de" (os mais longe do meio) e depois os que mais mudaram, até LINHAS_CURTAS */
export function linhasMarcadas(linhas: readonly LinhaGosto[]): LinhaGosto[] {
  const ordem = (l: LinhaGosto): number => COMPONENTES.indexOf(l.k);
  const frase = [...linhas].sort((a, b) => Math.abs(b.hoje - 0.5) - Math.abs(a.hoje - 0.5) || ordem(a) - ordem(b)).slice(0, 2);
  const mudou = linhas.filter(l => !frase.includes(l) && Math.abs(l.deVer) + Math.abs(l.doCarinho) >= MUDOU)
    .sort((a, b) => Math.abs(b.deVer) + Math.abs(b.doCarinho) - Math.abs(a.deVer) - Math.abs(a.doCarinho) || ordem(a) - ordem(b));
  return [...frase, ...mudou].slice(0, LINHAS_CURTAS).sort((a, b) => ordem(a) - ordem(b));
}

/** o gosto de hoje em palavras é outro que o de nascença? (a segunda linha só aparece quando difere) */
export function nascencaDifere(ina: Inato, e: EstadoGosto, quais: readonly Componente[] = COMPONENTES): boolean {
  return gostaMaisDe(ina.otimo, quais) !== gostaMaisDe(alvos(ina, e), quais);
}

/** onde um ponto fica entre os dois extremos, em palavras: "mais para cores vivas", "no meio, entre cores suaves e cores vivas" */
export function ondeFica(l: LinhaGosto, x: number): string {
  return x < 0.4 ? `mais para ${l.baixo}` : x > 0.6 ? `mais para ${l.alto}` : `no meio, entre ${l.baixo} e ${l.alto}`;
}

/** a linha como uma frase, para o leitor de tela (nada só por cor nem só por posição) */
export function descricaoDaLinha(l: LinhaGosto): string {
  const ver = Math.abs(l.deVer) >= MUDOU, car = Math.abs(l.doCarinho) >= MUDOU;
  const hoje = ver || car ? `hoje, ${ondeFica(l, l.hoje)}; mudou ${[ver ? "de tanto ver" : "", car ? "com o carinho" : ""].filter(Boolean).join(" e ")}` : "hoje, quase igual";
  return `${l.nome}: de nascença, ${ondeFica(l, l.nascenca)}. ${hoje}.`;
}

/** o que cada reação é, em palavras (o plano, 5.1) */
export const PALAVRA_REACAO: Record<Reacao, string> = {
  adorando: "Está adorando", olhando: "Está assistindo", curioso: "Ficou curioso", enjoou: "Enjoou disso", nao_gosta: "Não curtiu",
  distraido: "Não está prestando atenção",
};
const GOSTA: Record<Componente, string> = {
  cor: "tem as cores de que ele gosta", brilho: "tem o brilho de que ele gosta", movimento: "tem o movimento de que ele gosta",
  complexidade: "tem o tanto de detalhe de que ele gosta", volume: "o som está no volume de que ele gosta",
  variacao: "o som tem o ritmo de que ele gosta", timbre: "o som tem o tom de que ele gosta",
};
const DEMAIS: Record<Componente, [pouco: string, muito: string]> = {
  cor: ["as cores são suaves demais para ele", "as cores são vivas demais para ele"],
  brilho: ["a imagem é escura demais para ele", "a imagem é clara demais para ele"],
  movimento: ["a cena é parada demais para ele", "tem movimento demais para ele"],
  complexidade: ["a cena é simples demais para ele", "tem detalhe demais para ele"],
  volume: ["o som está baixo demais para ele", "o som está alto demais para ele"],
  variacao: ["o som é constante demais para ele", "o som é agitado demais para ele"],
  timbre: ["o som é grave demais para ele", "o som é agudo demais para ele"],
};

/** o pico de cada componente presente neste segundo (a parcela dele no agrado, de 0 a 1) */
export function picos(ina: Inato, e: EstadoGosto, s: Sentido): { k: Componente; pico: number; valor: number; alvo: number }[] {
  const v = valores(s);
  return (Object.keys(v) as Componente[]).map(k => {
    const a = alvo(ina, e, k);
    return { k, pico: Math.exp(-(((v[k]! - a) / ina.largura[k]) ** 2)), valor: v[k]!, alvo: a };
  });
}

/** o motivo da reação em palavras de jogo (PR-3): o componente que mais pesou no agrado (adorando), o que mais atrapalhou (não curtiu),
    o interesse gasto (enjoou) ou a novidade (curioso); "olhando" e "distraído" não têm motivo */
export function motivoDaReacao(ina: Inato, e: EstadoGosto, s: Sentido, r: Reacao): string | null {
  if (r === "enjoou") return "já viu muito disso";
  if (r === "curioso") return "é novo para ele";
  if (r !== "adorando" && r !== "nao_gosta") return null;
  const ps = picos(ina, e, s), ordem = (k: Componente): number => COMPONENTES.indexOf(k);
  if (ps.length === 0) throw new Error("motivoDaReacao: o sentido não tem componente");
  if (r === "adorando") return GOSTA[[...ps].sort((a, b) => b.pico - a.pico || ordem(a.k) - ordem(b.k))[0]!.k];
  const pior = [...ps].sort((a, b) => a.pico - b.pico || ordem(a.k) - ordem(b.k))[0]!;
  return DEMAIS[pior.k][pior.valor >= pior.alvo ? 1 : 0];
}

/** a frase inteira da reação: "Está adorando: tem as cores de que ele gosta." */
export function fraseDaReacao(ina: Inato, e: EstadoGosto, s: Sentido | null, r: Reacao): string {
  const m = s ? motivoDaReacao(ina, e, s, r) : null;
  return m ? `${PALAVRA_REACAO[r]}: ${m}.` : `${PALAVRA_REACAO[r]}.`;
}
