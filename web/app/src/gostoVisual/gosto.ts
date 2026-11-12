/* O gosto do protótipo P0 (docs/futuro/gosto_visual_pet.md, seções 3, 12 e 14): um módulo separado, fora do motor, do log e do save do
   pet, sem par no Python e sem paridade. Não vale para resultado nem decide nenhuma GV.
   - o agrado: um pico por componente, em volta de um alvo; o alvo é o ponto ótimo inato (da semente do pet) mais o que a exposição e o
     carinho deslocaram (seção 3.2);
   - a exposição: o alvo anda devagar na direção do que o pet vê (a mera exposição, seção 3.5);
   - o carinho do dono durante a exibição puxa o alvo para o que está passando (a associação com a consequência, seção 3.5);
   - a habituação presa ao estímulo (seção 3.3; o enjoo, D-GV-ENJOO-1 a 3): uma memória curta de protótipos do vetor, cada um com o seu
     enjoo, que sobe enquanto o pet vê aquilo e decai devagar (horas de TV ligada); o interesse de agora é 1 menos o enjoo do protótipo
     parecido. Só a novidade (a cena longe dos protótipos) ou a constante lenta devolvem o interesse; voltar à mesma imagem não desenjoa;
   - sem o enjoo migrante (D-GV-MIGRANTE-1 a 3): o protótipo fica parado no vetor em que nasceu; o "mesmo" estímulo é medido em cada
     sentido, com um raio pequeno na visão (quadros reais diferentes contam como diferentes) e um raio maior no som suavizado no tempo
     (a mesma voz e o mesmo jogo continuam um estímulo só); o segundo de um corte de cena não entra na memória;
   - a exposição com saturação (o U invertido, D-GV-ENJOO-4): até o enjoo do estímulo chegar a SATURACAO_EXPOSICAO, ela puxa o alvo para
     o que passa; daí em diante para de puxar, e o enjoo acima da saturação vira tédio, que desconta do agrado daquele estímulo;
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
/** a memória do enjoo (D-GV-ENJOO-2): quantos protótipos do vetor ela guarda */
export const PROTOTIPOS = 6;
/** um raio para cada sentido (D-GV-MIGRANTE-2, DECIDIDA na forma; os números PROPOSTOS): um vetor é "o mesmo" estímulo de um protótipo
    quando a visão (a média dos 4 componentes) fica até RAIO_MESMO_VISAO dele, ou quando o som suavizado (a média dos 3) fica até
    RAIO_MESMO_SOM; o enjoo do protótipo ainda pesa até os raios da generalização, caindo em linha de 1 na distância 0 a 0 no raio, e vale
    o maior dos dois sentidos. Eram 0,15 e 0,3 para todos os componentes juntos, e quadros reais diferentes ficam a menos disso uns dos
    outros na visão; o protótipo não anda (D-GV-MIGRANTE-1) */
export const RAIO_MESMO_VISAO = 0.025, RAIO_GENERALIZACAO_VISAO = 0.05;
export const RAIO_MESMO_SOM = 0.1, RAIO_GENERALIZACAO_SOM = 0.2;
/** a suavização do som na memória do enjoo: a fração do caminho até o som deste segundo que a média anda por segundo (a variação natural
    da fala, de um segundo para o outro, não vira um estímulo novo) */
export const SUAVIZA_SOM = 0.1;
/** o corte de cena (D-GV-MIGRANTE-3): o movimento que sobe mais que isto de um segundo para o outro marca um vetor de passagem, que não
    cria nem gasta protótipo */
export const SALTO_CORTE = 0.5;
/** o enjoo que sobe por segundo, olhando e de lado (a fração do que falta até 1) */
export const GASTO_ENJOO_OLHANDO = 0.012, GASTO_ENJOO_DE_LADO = 0.003;
/** a constante lenta do desenjoo, em segundos de TV ligada (2 h): o enjoo de todos os protótipos cai por exp(-dt/TAU) a cada passo */
export const TAU_DESENJOO = 7200;
/** a exposição com saturação (D-GV-ENJOO-4): a exposição puxa o alvo só até este enjoo; acima dele, o enjoo vira tédio */
export const SATURACAO_EXPOSICAO = 0.5;
/** o tédio máximo (no enjoo 1), descontado do agrado do estímulo */
export const PESO_TEDIO = 0.5;
/** o "adorando" pede o agrado e também o interesse acima destes cortes (D-GV-ENJOO-5) */
export const AGRADO_ADORANDO = 0.7, INTERESSE_ADORANDO = 0.6;
/** abaixo deste interesse, o pet que não olha uma coisa de que gosta está enjoado */
export const INTERESSE_ENJOOU = 0.4;
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

/** um protótipo da memória do enjoo: o vetor (só os componentes que ele viu) e o enjoo dele, em [0, 1] */
export interface Prototipo { vetor: Partial<PorComponente>; enjoo: number }

/** o estado aprendido: o deslocamento da exposição e o do carinho, a memória do enjoo, o interesse de agora e o tempo junto */
export interface EstadoGosto {
  exposicao: PorComponente;
  carinho: PorComponente;
  /** no máximo PROTOTIPOS, na ordem da criação; a troca é determinística (`passo`) */
  memoria: Prototipo[];
  interesse: number;
  olhando: boolean;
  segundosJuntos: number;
  carinhos: number;
  /** o movimento do segundo anterior, para achar o corte de cena (null antes do primeiro segundo; não vai ao estado guardado) */
  movimentoAntes: number | null;
  /** o som suavizado no tempo, que a memória do enjoo usa (null sem som; não vai ao estado guardado) */
  somSuave: VetorSom | null;
}
export const estadoInicial = (): EstadoGosto =>
  ({ exposicao: zeros(), carinho: zeros(), memoria: [], interesse: 1, olhando: false, segundosJuntos: 0, carinhos: 0, movimentoAntes: null, somSuave: null });

export type Reacao = "adorando" | "olhando" | "enjoou" | "nao_gosta" | "curioso" | "distraido";
/** o agrado já com o tédio descontado, e o tédio à parte; a novidade é a distância ao protótipo mais perto (1 com a memória vazia) */
export interface Leitura { agrado: number; tedio: number; interesse: number; novidade: number; vontade: number; olhando: boolean; reacao: Reacao }

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

/** a distância de um vetor a um protótipo: a média por componente presente agora; um componente que o protótipo não viu conta 1 */
export function distancia(v: Partial<PorComponente>, p: Prototipo): number {
  const ks = Object.keys(v) as Componente[];
  if (ks.length === 0) throw new Error("distância de um sentido sem componente");
  return ks.reduce((t, k) => t + (p.vetor[k] === undefined ? 1 : Math.abs(v[k]! - p.vetor[k]!)), 0) / ks.length;
}

const VISAO = ["cor", "brilho", "movimento", "complexidade"] as const, SOM = ["volume", "variacao", "timbre"] as const;
/** a distância num sentido: a média dos componentes dele presentes no vetor (o que o protótipo não viu conta 1); null se o vetor não tem
    esse sentido */
function distanciaSentido(v: Partial<PorComponente>, p: Prototipo, ks: readonly Componente[]): number | null {
  const presentes = ks.filter(k => v[k] !== undefined);
  if (presentes.length === 0) return null;
  return presentes.reduce((t, k) => t + (p.vetor[k] === undefined ? 1 : Math.abs(v[k]! - p.vetor[k]!)), 0) / presentes.length;
}
/** quão perto o vetor está do protótipo, na escala do "mesmo" (até 1 é o mesmo estímulo): o menor dos dois sentidos, cada um no seu raio */
export function proximidade(v: Partial<PorComponente>, p: Prototipo): number {
  const dv = distanciaSentido(v, p, VISAO), ds = distanciaSentido(v, p, SOM);
  if (dv === null && ds === null) throw new Error("distância de um sentido sem componente");
  return Math.min(dv === null ? Infinity : dv / RAIO_MESMO_VISAO, ds === null ? Infinity : ds / RAIO_MESMO_SOM);
}
/** o peso da generalização de um protótipo para um vetor: o maior dos dois sentidos, cada um caindo em linha até o raio dele */
function generalizacao(v: Partial<PorComponente>, p: Prototipo): number {
  const dv = distanciaSentido(v, p, VISAO), ds = distanciaSentido(v, p, SOM);
  return Math.max(dv === null ? 0 : 1 - dv / RAIO_GENERALIZACAO_VISAO, ds === null ? 0 : 1 - ds / RAIO_GENERALIZACAO_SOM, 0);
}
/** o enjoo de um vetor (a visão e o som suavizado): o maior enjoo da memória, pesado pela generalização */
export const enjooDe = (v: Partial<PorComponente>, memoria: readonly Prototipo[]): number =>
  memoria.reduce((m, p) => Math.max(m, p.enjoo * generalizacao(v, p)), 0);

/** o tédio de um enjoo: zero até a saturação da exposição; acima dela, cresce em linha até PESO_TEDIO no enjoo 1 */
export const tedioDe = (enjoo: number): number => PESO_TEDIO * Math.max(0, enjoo - SATURACAO_EXPOSICAO) / (1 - SATURACAO_EXPOSICAO);

/** um segundo assistindo junto: devolve o estado novo (o antigo não muda) e a leitura do segundo */
export function passo(ina: Inato, e0: EstadoGosto, s: Sentido, carinho: boolean, dt = 1): { estado: EstadoGosto; leitura: Leitura } {
  if (!(dt > 0)) throw new Error(`passo do gosto com dt ${dt}`);
  const v = valores(s), ks = Object.keys(v) as Componente[];
  const e: EstadoGosto = { ...e0, exposicao: { ...e0.exposicao }, carinho: { ...e0.carinho },
    memoria: e0.memoria.map(p => ({ vetor: { ...p.vetor }, enjoo: p.enjoo })) };
  /* a constante lenta: todo enjoo cai devagar, olhando ou não */
  const desenjoo = Math.exp(-dt / TAU_DESENJOO);
  for (const p of e.memoria) p.enjoo *= desenjoo;
  /* o vetor da memória: a visão deste segundo e o som suavizado no tempo (sem som, a média recomeça) */
  const a0 = limitar(1 - (1 - SUAVIZA_SOM) ** dt), ss = e0.somSuave;
  e.somSuave = s.som === null ? null : ss === null ? { ...s.som }
    : { volume: ss.volume + a0 * (s.som.volume - ss.volume), variacao: ss.variacao + a0 * (s.som.variacao - ss.variacao), timbre: ss.timbre + a0 * (s.som.timbre - ss.timbre) };
  const vm: Partial<PorComponente> = e.somSuave === null ? { ...s.visao } : { ...s.visao, ...e.somSuave };
  /* a novidade: a distância (a média por componente) ao protótipo mais perto; o que reconhece o estímulo é o mais perto na escala do
     "mesmo" de cada sentido (no empate, o primeiro na ordem da memória); com a memória vazia, tudo é novo */
  let perto = -1, prox = Infinity, novidade = 1;
  e.memoria.forEach((p, j) => {
    novidade = Math.min(novidade, distancia(vm, p));
    const x = proximidade(vm, p);
    if (x < prox) { prox = x; perto = j; }
  });
  /* o estímulo de agora: o protótipo que o reconhece (parado no vetor em que nasceu), ou um novo, sem enjoo; com a memória cheia, o novo
     toma o lugar do de menor enjoo (no empate, o mais antigo). No segundo de um corte de cena, o estímulo é uma cópia solta: a memória
     não muda, e o enjoo dele não fica guardado */
  const corte = e0.movimentoAntes !== null && s.visao.movimento - e0.movimentoAntes > SALTO_CORTE;
  e.movimentoAntes = s.visao.movimento;
  let p: Prototipo;
  if (perto >= 0 && prox <= 1) {
    p = corte ? { vetor: { ...e.memoria[perto]!.vetor }, enjoo: e.memoria[perto]!.enjoo } : e.memoria[perto]!;
  } else if (corte) {
    p = { vetor: { ...vm }, enjoo: 0 };
  } else {
    p = { vetor: { ...vm }, enjoo: 0 };
    if (e.memoria.length >= PROTOTIPOS) {
      let troca = 0;
      e.memoria.forEach((q, j) => { if (q.enjoo < e.memoria[troca]!.enjoo) troca = j; });
      e.memoria.splice(troca, 1);
    }
    e.memoria.push(p);
  }
  const enjooAntes = p.enjoo, base = agrado(ina, e0, s);
  /* o agrado do gosto (o alvo de antes deste segundo) menos o tédio deste estímulo */
  const tedio = tedioDe(enjooAntes), a = Math.max(0, base - tedio);
  /* a exposição (com saturação) e o carinho deslocam o alvo na direção do que está passando */
  const satura = Math.max(0, 1 - enjooAntes / SATURACAO_EXPOSICAO);
  const taxa = (e.olhando ? TAXA_EXPOSICAO_OLHANDO : TAXA_EXPOSICAO_DE_LADO) * dt * satura;
  for (const k of ks) {
    e.exposicao[k] = limitar(e.exposicao[k] + taxa * (v[k]! - alvo(ina, e0, k)), -LIMITE_EXPOSICAO, LIMITE_EXPOSICAO);
    if (carinho) e.carinho[k] = limitar(e.carinho[k] + TAXA_CARINHO * (v[k]! - alvo(ina, e0, k)), -LIMITE_CARINHO, LIMITE_CARINHO);
  }
  if (carinho) e.carinhos += 1;
  /* o enjoo do estímulo sobe (olhando mais que de lado), e o interesse é o que sobra do enjoo do vetor de agora */
  p.enjoo = limitar(p.enjoo + limitar((e.olhando ? GASTO_ENJOO_OLHANDO : GASTO_ENJOO_DE_LADO) * dt) * (1 - p.enjoo));
  e.interesse = 1 - enjooDe(vm, e.memoria);
  const vontade = a * e.interesse, estava = e.olhando;
  e.olhando = estava ? vontade >= PARA_OLHAR : vontade > COMECA_OLHAR;
  e.segundosJuntos += dt;
  /* sem olhar: o que não agrada nem de cara é "não curtiu"; o que agrada, com o interesse gasto, é "enjoou" (D-GV-ENJOO-5) */
  const reacao: Reacao = e.olhando
    ? a > AGRADO_ADORANDO && e.interesse > INTERESSE_ADORANDO ? "adorando" : "olhando"
    : estava ? (e.interesse < INTERESSE_ENJOOU ? "enjoou" : "nao_gosta")
    : novidade > 0.15 ? "curioso" : base < 0.3 ? "nao_gosta" : e.interesse < INTERESSE_ENJOOU ? "enjoou" : "distraido";
  return { estado: e, leitura: { agrado: a, tedio, interesse: e.interesse, novidade, vontade, olhando: e.olhando, reacao } };
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

/** a versão do texto guardado: a 2 traz a memória do enjoo (D-GV-ENJOO-3); a 1, de antes, não tinha */
export const VERSAO_GUARDADA = 2;

/** o estado guardado em texto: os deslocamentos aprendidos, a memória do enjoo, o tempo junto e os carinhos */
export const paraTexto = (e: EstadoGosto): string =>
  JSON.stringify({ v: VERSAO_GUARDADA, exposicao: e.exposicao, carinho: e.carinho, memoria: e.memoria, segundosJuntos: e.segundosJuntos, carinhos: e.carinhos });

/** a memória do enjoo de volta do texto: no máximo PROTOTIPOS, cada vetor com componentes conhecidos em [0, 1] e o enjoo em [0, 1] */
function lerMemoria(x: unknown): Prototipo[] {
  if (!Array.isArray(x) || x.length > PROTOTIPOS) throw new Error("gosto guardado com a memória do enjoo estragada");
  return x.map((q, j) => {
    const p = q as { vetor?: unknown; enjoo?: unknown } | null, vetor: Partial<PorComponente> = {};
    if (typeof p?.vetor !== "object" || p.vetor === null) throw new Error(`gosto guardado sem o vetor do protótipo ${j}`);
    for (const [k, n] of Object.entries(p.vetor)) {
      if (!(COMPONENTES as readonly string[]).includes(k) || typeof n !== "number" || !(n >= 0 && n <= 1)) throw new Error(`gosto guardado com memoria[${j}].${k} inválido`);
      vetor[k as Componente] = n;
    }
    if (Object.keys(vetor).length === 0) throw new Error(`gosto guardado com o protótipo ${j} vazio`);
    if (typeof p.enjoo !== "number" || !(p.enjoo >= 0 && p.enjoo <= 1)) throw new Error(`gosto guardado com memoria[${j}].enjoo inválido`);
    return { vetor, enjoo: p.enjoo };
  });
}

/** o estado de volta do texto; um texto que não é o do P0 levanta erro (não volta ao zero em silêncio). A versão 1 (de antes do enjoo)
    migra de propósito com a memória vazia: ela nunca guardou a habituação, e o interesse dela já voltava ao abrir (D-GV-ENJOO-3) */
export function doTexto(t: string): EstadoGosto {
  const o = JSON.parse(t) as Record<string, unknown>;
  if (o.v !== 1 && o.v !== VERSAO_GUARDADA) throw new Error(`gosto guardado numa versão desconhecida: ${String(o.v)}`);
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
  const memoria = o.v === 1 ? [] : lerMemoria(o.memoria);
  return { ...estadoInicial(), exposicao: ler(o.exposicao, "exposicao"), carinho: ler(o.carinho, "carinho"), memoria, segundosJuntos: o.segundosJuntos, carinhos: o.carinhos };
}

/** "1 h 05 min", "12 min 30 s", "40 s" */
export function tempoJunto(seg: number): string {
  const s = Math.floor(seg), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
  return h > 0 ? `${h} h ${String(m).padStart(2, "0")} min` : m > 0 ? `${m} min ${String(r).padStart(2, "0")} s` : `${r} s`;
}
