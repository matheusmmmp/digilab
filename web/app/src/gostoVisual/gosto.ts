/* O gosto do protótipo P0 (docs/futuro/gosto_visual_pet.md, seções 3, 12 e 14): um módulo separado, fora do motor, do log e do save do
   pet, sem par no Python e sem paridade. Não vale para resultado nem decide nenhuma GV.
   - o agrado: um pico por componente, em volta de um alvo; o alvo é o ponto ótimo inato (da semente do pet) mais o que a exposição e o
     carinho deslocaram (seção 3.2);
   - a exposição: o alvo anda devagar na direção do que o pet vê (a mera exposição, seção 3.5);
   - o carinho do dono durante a exibição puxa o alvo para o que está passando (a associação com a consequência, seção 3.5);
   - o interesse se gasta enquanto o pet olha e volta quando ele não olha ou quando o quadro muda (a habituação, seção 3.3);
   - o pet olha quando o agrado vezes o interesse passa de um corte, e desvia quando caem (com folga entre os dois cortes).
   Determinístico: o mesmo pet e a mesma sequência de vetores dão o mesmo estado. Todos os números são PROPOSTOS, SEM FONTE. */
import { criarRng, hashSemente } from "../../motor/rng.ts";
import type { VetorSom, VetorVisao } from "./sentidos.ts";

export const COMPONENTES = ["cor", "brilho", "movimento", "complexidade", "volume", "variacao", "timbre"] as const;
export type Componente = (typeof COMPONENTES)[number];
export type PorComponente = Record<Componente, number>;
/** o que o pet sente num segundo: a visão sempre; o som só se a captura trouxe áudio */
export interface Sentido { visao: VetorVisao; som: VetorSom | null }

/* --- os números do protótipo (PROPOSTOS, SEM FONTE) --- */
/** a faixa do ponto ótimo inato e da largura do pico */
export const OTIMO_MIN = 0.15, OTIMO_MAX = 0.85, LARGURA_MIN = 0.18, LARGURA_MAX = 0.38;
/** quanto o alvo anda por segundo na direção do que o pet vê (a exposição), olhando e não olhando */
export const TAXA_EXPOSICAO_OLHANDO = 0.004, TAXA_EXPOSICAO_DE_LADO = 0.001;
/** quanto um carinho puxa o alvo para o que está passando */
export const TAXA_CARINHO = 0.12;
/** o máximo que a exposição e o carinho deslocam o alvo, cada um */
export const LIMITE_EXPOSICAO = 0.25, LIMITE_CARINHO = 0.3;
/** o traço do que o pet espera ver (a novidade é a distância a ele), por segundo */
export const TAXA_ESPERADO = 0.25;
/** o gasto do interesse por segundo olhando e a volta por segundo sem olhar */
export const GASTO_INTERESSE = 0.012, VOLTA_INTERESSE = 0.02;
/** quanto a novidade devolve de interesse (a deshabituação) */
export const GANHO_NOVIDADE = 1.5;
/** os cortes da vontade de olhar: começa acima de COMECA, para abaixo de PARA */
export const COMECA_OLHAR = 0.42, PARA_OLHAR = 0.24;

const limitar = (x: number, a = 0, b = 1): number => (x < a ? a : x > b ? b : x);
const zeros = (): PorComponente => ({ cor: 0, brilho: 0, movimento: 0, complexidade: 0, volume: 0, variacao: 0, timbre: 0 });

/** o gosto de nascença: o ponto ótimo e a largura de cada componente */
export interface Inato { otimo: PorComponente; largura: PorComponente }

/** o inato do pet, da semente dele, por uma rng própria (a "gosto-visual-ovo"); não consome nada da rng do motor */
export function inatoDaSemente(semente: number): Inato {
  if (!Number.isFinite(semente)) throw new Error(`semente inválida para o gosto: ${semente}`);
  const rng = criarRng(hashSemente("gosto-visual-ovo", semente)), otimo = zeros(), largura = zeros();
  for (const k of COMPONENTES) {
    otimo[k] = OTIMO_MIN + (OTIMO_MAX - OTIMO_MIN) * rng.random();
    largura[k] = LARGURA_MIN + (LARGURA_MAX - LARGURA_MIN) * rng.random();
  }
  return { otimo, largura };
}

/** o estado aprendido: o deslocamento da exposição e o do carinho, o que o pet espera ver, o interesse e o tempo junto */
export interface EstadoGosto {
  exposicao: PorComponente;
  carinho: PorComponente;
  esperado: PorComponente | null;
  interesse: number;
  olhando: boolean;
  segundosJuntos: number;
  carinhos: number;
}
export const estadoInicial = (): EstadoGosto =>
  ({ exposicao: zeros(), carinho: zeros(), esperado: null, interesse: 1, olhando: false, segundosJuntos: 0, carinhos: 0 });

export type Reacao = "adorando" | "olhando" | "enjoou" | "nao_gosta" | "curioso" | "distraido";
export interface Leitura { agrado: number; interesse: number; novidade: number; vontade: number; olhando: boolean; reacao: Reacao }

/** os componentes presentes neste segundo e o valor de cada um */
export function valores(s: Sentido): Partial<PorComponente> {
  const v: Partial<PorComponente> = { ...s.visao };
  if (s.som) Object.assign(v, s.som);
  for (const [k, x] of Object.entries(v)) if (!(x >= 0 && x <= 1)) throw new Error(`componente ${k} fora de [0, 1]: ${x}`);
  return v;
}

/** o alvo de hoje de um componente: o inato mais o que a exposição e o carinho deslocaram */
export const alvo = (ina: Inato, e: EstadoGosto, k: Componente): number => limitar(ina.otimo[k] + e.exposicao[k] + e.carinho[k]);

/** o agrado de um sentido: a média do pico de cada componente presente */
export function agrado(ina: Inato, e: EstadoGosto, s: Sentido): number {
  const v = valores(s), ks = Object.keys(v) as Componente[];
  return ks.reduce((t, k) => t + Math.exp(-(((v[k]! - alvo(ina, e, k)) / ina.largura[k]) ** 2)), 0) / ks.length;
}

/** um segundo assistindo junto: devolve o estado novo (o antigo não muda) e a leitura do segundo */
export function passo(ina: Inato, e0: EstadoGosto, s: Sentido, carinho: boolean, dt = 1): { estado: EstadoGosto; leitura: Leitura } {
  if (!(dt > 0)) throw new Error(`passo do gosto com dt ${dt}`);
  const v = valores(s), ks = Object.keys(v) as Componente[];
  const e: EstadoGosto = { ...e0, exposicao: { ...e0.exposicao }, carinho: { ...e0.carinho }, esperado: e0.esperado ? { ...e0.esperado } : null };
  /* a novidade: a distância média ao que o pet espera; no primeiro segundo, tudo é novo */
  const novidade = e.esperado ? ks.reduce((t, k) => t + Math.abs(v[k]! - e.esperado![k]), 0) / ks.length : 1;
  const esp = e.esperado ?? { ...zeros(), ...v };
  for (const k of ks) esp[k] += limitar(TAXA_ESPERADO * dt) * (v[k]! - esp[k]);
  e.esperado = esp;
  const a = agrado(ina, e0, s);
  /* a exposição e o carinho deslocam o alvo na direção do que está passando */
  const taxa = (e.olhando ? TAXA_EXPOSICAO_OLHANDO : TAXA_EXPOSICAO_DE_LADO) * dt;
  for (const k of ks) {
    e.exposicao[k] = limitar(e.exposicao[k] + taxa * (v[k]! - alvo(ina, e0, k)), -LIMITE_EXPOSICAO, LIMITE_EXPOSICAO);
    if (carinho) e.carinho[k] = limitar(e.carinho[k] + TAXA_CARINHO * (v[k]! - alvo(ina, e0, k)), -LIMITE_CARINHO, LIMITE_CARINHO);
  }
  if (carinho) e.carinhos += 1;
  /* o interesse se gasta olhando, volta sem olhar, e a novidade devolve uma parte */
  const gasto = e.olhando ? -GASTO_INTERESSE * dt : VOLTA_INTERESSE * dt * (1 - e.interesse);
  e.interesse = limitar(e.interesse + gasto + GANHO_NOVIDADE * novidade * novidade);
  const vontade = a * e.interesse, estava = e.olhando;
  e.olhando = estava ? vontade >= PARA_OLHAR : vontade > COMECA_OLHAR;
  e.segundosJuntos += dt;
  const reacao: Reacao = e.olhando
    ? a > 0.7 ? "adorando" : "olhando"
    : estava ? (e.interesse < 0.4 ? "enjoou" : "nao_gosta")
    : novidade > 0.15 ? "curioso" : a < 0.3 ? "nao_gosta" : "distraido";
  return { estado: e, leitura: { agrado: a, interesse: e.interesse, novidade, vontade, olhando: e.olhando, reacao } };
}

/* --- o "gosta mais de…" em palavras (GV-14: a parte de nascença e a de hoje, separadas) --- */
export const PALAVRAS: Record<Componente, [baixo: string, alto: string]> = {
  cor: ["cores suaves", "cores vivas"],
  brilho: ["imagens escuras", "imagens claras"],
  movimento: ["cenas calmas", "muito movimento"],
  complexidade: ["cenas simples", "cenas cheias de detalhe"],
  volume: ["som baixinho", "som alto"],
  variacao: ["som constante", "ritmo agitado"],
  timbre: ["sons graves", "sons agudos"],
};
export const NOME_COMPONENTE: Record<Componente, string> = {
  cor: "cor", brilho: "brilho", movimento: "movimento", complexidade: "detalhe", volume: "volume", variacao: "ritmo", timbre: "timbre",
};

/** as duas preferências mais marcadas (as mais longe do meio), em palavras: "cores vivas e muito movimento" */
export function gostaMaisDe(pontos: PorComponente, quais: readonly Componente[] = COMPONENTES): string {
  const ord = [...quais].sort((a, b) => Math.abs(pontos[b] - 0.5) - Math.abs(pontos[a] - 0.5) || COMPONENTES.indexOf(a) - COMPONENTES.indexOf(b));
  return ord.slice(0, 2).map(k => PALAVRAS[k][pontos[k] >= 0.5 ? 1 : 0]).join(" e ");
}
/** os alvos de hoje de todos os componentes */
export function alvos(ina: Inato, e: EstadoGosto): PorComponente {
  const r = zeros();
  for (const k of COMPONENTES) r[k] = alvo(ina, e, k);
  return r;
}

/* --- o estado guardado (só o aprendido e o tempo junto; nenhum quadro, nenhum áudio) --- */
export const chaveGuardada = (semente: number): string => `digilab-gosto-visual-p0:${semente}`;

/** o estado guardado em texto: só os deslocamentos aprendidos, o tempo junto e os carinhos */
export const paraTexto = (e: EstadoGosto): string =>
  JSON.stringify({ v: 1, exposicao: e.exposicao, carinho: e.carinho, segundosJuntos: e.segundosJuntos, carinhos: e.carinhos });

/** o estado de volta do texto; um texto que não é o do P0 levanta erro (não volta ao zero em silêncio) */
export function doTexto(t: string): EstadoGosto {
  const o = JSON.parse(t) as Record<string, unknown>;
  if (o.v !== 1) throw new Error(`gosto guardado numa versão desconhecida: ${String(o.v)}`);
  const ler = (x: unknown, nome: string): PorComponente => {
    const r = zeros();
    for (const k of COMPONENTES) {
      const n = (x as Record<string, unknown> | null)?.[k];
      if (typeof n !== "number" || !Number.isFinite(n)) throw new Error(`gosto guardado sem ${nome}.${k}`);
      r[k] = n;
    }
    return r;
  };
  if (typeof o.segundosJuntos !== "number" || typeof o.carinhos !== "number") throw new Error("gosto guardado sem o tempo junto");
  return { ...estadoInicial(), exposicao: ler(o.exposicao, "exposicao"), carinho: ler(o.carinho, "carinho"), segundosJuntos: o.segundosJuntos, carinhos: o.carinhos };
}

/** "1 h 05 min", "12 min 30 s", "40 s" */
export function tempoJunto(seg: number): string {
  const s = Math.floor(seg), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
  return h > 0 ? `${h} h ${String(m).padStart(2, "0")} min` : m > 0 ? `${m} min ${String(r).padStart(2, "0")} s` : `${r} s`;
}
