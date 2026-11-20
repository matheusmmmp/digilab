/* O painel DigiBrain como modal pequeno (D1b da UX_TELA_PET; prancha aprovada em docs/pranchas/ux-digibrain/modal.html, decisoes D1b-1 a
   D1b-7 de docs/PROPOSTAS_V3_UX_TELA_PET.md, sobre a direcao A "scan holografico" da D1). Um <dialog> modal (foco preso, Esc fecha, um clique
   fora fecha, o foco volta a quem abriu) so com o mapa dos pesos: no desktop, a direita, com a ilha e o pet a vista em volta; no celular, uma
   folha baixa. So le o motor por useJogo(): todo numero sai de Motor.digibrain() (mapa, decisao); nenhum mudarMotor aqui. Cada ponto do
   desenho e um no do motor (entrada, regra ou acao) e cada fio e uma aresta de mapa.arestas; a forma de cerebro e as regioes sao so desenho,
   e a dica do "i" diz isso. O movimento e o da D1: so vista e so numa decisao nova (mapa.acesas.n muda), a varredura passa uma vez e o pulso
   percorre as arestas acesas, os dois terminam; o giro lento do plano (so no desktop) e CSS puro. Com "reduzir movimento" nada se move; no
   replay e com o tempo pausado so o destaque troca. O relogio do navegador aqui e so animacao: nada do que e gravado depende dele.
   A ilha continua a pleno ritmo por tras (D1b-3: sem CENA.coberto e sem desfoque de tela cheia).
   O campo pequeno (D1c, escolha do Matheus de 2026-11-07, "(a) desk, (b) celular"): no desktop um painel de 420 px sob o relogio, a 390 uma folha
   de 210 px com os botoes numa coluna a esquerda; o titulo e so o icone do cerebro (o nome fica para o leitor de tela); os rotulos so no
   caminho aceso e nas candidatas, e o de qualquer outro ponto aparece ao passar o mouse ou ao tocar nele.
   O visual do scanner (pedido do Matheus em 2026-11-11, com uma imagem de referencia; docs/TAREFA_V3_UX_TELA_PET.md, "D1e"): o quadro escuro
   com cantos em colchete, o nome ao lado do icone no desktop, a rede em anel e, embaixo, uma faixa com a onda da decisao e o "estado atual".
   A coluna de cinco barras da referencia (percepcao, memoria, impulsos, emocao, social) nao entra. No mesmo dia ele pediu o desenho "mais
   ludico": a rede e uma ILUSTRACAO que simula o cerebro em atividade (a "rede viva", abaixo), nao o mapa dos pesos; o que a D1 dizia de
   "cada ponto e um no do motor" deixou de valer para o desenho. Os pesos de verdade ficam no mapa em texto. A onda e o estado atual saem
   do motor: a onda e um pico por entrada com termo nesta decisao (mapa.acesas.arestas), e o estado atual e a regra do instinto que valeu
   (decisao.regra). O motor nao tem um estado chamado "calmo". */
import { memo, useEffect, useMemo, useRef, useState, useSyncExternalStore, type CSSProperties, type MouseEvent, type ReactNode, type SyntheticEvent } from "react";
import { Annoyed, Brain, Frown, Info, List, Meh, Smile, X, type LucideIcon } from "lucide-react";
import { ENTRADAS_LOBOS, type LeituraDecisao, type MapaDecisao, type RegraLobos } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import type { EstadoSelo } from "../seloDigiBrain.ts";
import "../estilo/scan_digibrain.css";
import { ACAO_CURTA, REGRA_TXT, pct, useEstadoSelo } from "./DigiBrain.tsx";
import { abrirModal } from "./modal.ts";
import { TXT_ACAO, TXT_ENTRADA, TXT_REGRA, type DadosMapa } from "./MapaPesos.tsx";

/* ---------------------------------------------------------------- os numeros do movimento (D1-2): so vista, nenhum numero de jogo */
/** a varredura passa uma vez, em ms. PROPOSTO, SEM FONTE (D1-2) */
export const VARREDURA_MS = 1200;
/** o pulso percorre as arestas acesas logo depois da varredura, em ms. PROPOSTO, SEM FONTE (D1-2) */
export const PULSO_MS = 800;
/** o giro lento do plano: a amplitude em graus de cada lado. PROPOSTO, SEM FONTE (D1-2) */
export const GIRO_GRAUS = 8;
/** o giro lento do plano: o ciclo inteiro (ida e volta), em s. PROPOSTO, SEM FONTE (D1-2) */
export const GIRO_CICLO_S = 40;
/** a folga depois do fim da animacao antes de tirar a varredura e o pulso do DOM, em ms (so para o timer; nao e o tempo da animacao) */
const FOLGA_MS = 150;

/* ---------------------------------------------------------------- a rede viva (unidades do desenho; so desenho)
   O Matheus, em 2026-11-11, depois de ver o anel com os pesos de verdade: "quero que faca outro desenho, algo mais ludico e menos realmente
   como o cerebro efetivamente esta funcionando"; "simule como o cerebro funcione mas nao exatamente como as conexoes estao acontecendo, algo
   que visualmente seja interessante". O desenho e uma ILUSTRACAO: uma rede de pontos e fios em anel, com impulsos correndo por ela. Os
   pontos e os fios NAO sao os nos nem os pesos do motor (esses ficam no mapa em texto). Do motor o desenho usa so tres coisas:
   - a semente do pet, para cada pet ter a sua rede (a forma do anel, os pontos e os fios saem de um gerador proprio da vista, semeado nela);
   - quantas entradas pesaram na decisao de agora (mapa.acesas.arestas.length), que da quantos impulsos correm;
   - a regra da decisao, que da a cor dos impulsos (o tom do estado atual).
   A mesma rede serve ao scan do cerebro modular (ScanDigiBrainLab.tsx), com os modulos que contribuiram no lugar das entradas.
   O gerador e so da vista: nao e nenhuma rng do motor, nada dele e gravado e o replay nao o le. Todo numero aqui e de desenho,
   PROPOSTO, SEM FONTE. O viewBox guarda a proporcao 880 x 552 do campo pequeno (D1c). */
const VB_L = 880, VB_A = 552, CX = 440, CY = 276;
const VB_ANEL = `0 0 ${VB_L} ${VB_A}`;
/** quantos pontos a rede tem, o raio medio do anel, a ondulacao dele e a meia largura da faixa em que os pontos se espalham */
const N_PONTOS = 150, R_ANEL = 178, ONDULACAO = 9, MEIA_FAIXA = 64;
/** os impulsos: quantos a rede tem prontos, o minimo que corre e quantos entram por entrada que pesou na decisao */
export const N_IMPULSOS = 14, IMPULSOS_MIN = 4, IMPULSOS_POR_ENTRADA = 2;
/** a volta de um impulso, em s: a mais curta e o passo entre uma e outra (cinco duracoes, para os impulsos nao andarem juntos) */
const IMPULSO_S = 2.6, IMPULSO_PASSO_S = 0.7;
const f = (v: number): number => Math.round(v * 10) / 10;

type Ponto = [number, number];
/** o gerador da vista (mulberry32): deterministico pela semente, so para o desenho */
function geradorDaVista(semente: number): () => number {
  let a = semente >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
/** uma curva suave pelos pontos (quadraticas pelos pontos medios) */
function suave(p: Ponto[]): string {
  let d = `M${f(p[0]![0])} ${f(p[0]![1])}`;
  for (let i = 1; i < p.length - 1; i++) d += `Q${f(p[i]![0])} ${f(p[i]![1])} ${f((p[i]![0] + p[i + 1]![0]) / 2)} ${f((p[i]![1] + p[i + 1]![1]) / 2)}`;
  const u = p[p.length - 1]!;
  return d + `L${f(u[0])} ${f(u[1])}`;
}
export interface RedeViva { pontos: { x: number; y: number; r: number; pisca: boolean }[]; fios: string[]; impulsos: string[] }
/** a rede de um pet: os pontos em volta do anel (na ordem do angulo), os fios entre vizinhos proximos e alguns mais longos, e os caminhos dos
    impulsos (cada um passa por uma fila de pontos). A mesma semente da sempre a mesma rede */
export function redeViva(semente: number): RedeViva {
  const r = geradorDaVista(semente), fase = r() * Math.PI * 2, pts: Ponto[] = [], pontos: RedeViva["pontos"] = [];
  for (let i = 0; i < N_PONTOS; i++) {
    const g = (i + r() * 0.9) / N_PONTOS * Math.PI * 2, raio = R_ANEL + ONDULACAO * (Math.sin(3 * g + fase) + Math.sin(5 * g - fase)) + (r() + r() - 1) * MEIA_FAIXA;
    const p: Ponto = [CX + raio * Math.cos(g), CY + raio * Math.sin(g)];
    pts.push(p); pontos.push({ x: f(p[0]), y: f(p[1]), r: f(1.8 + r() * r() * 5), pisca: r() < 0.3 });
  }
  const no = (i: number): Ponto => pts[((i % N_PONTOS) + N_PONTOS) % N_PONTOS]!;
  /* um fio entre dois pontos: uma curva com a barriga para dentro ou para fora do anel */
  const fio = (a: Ponto, b: Ponto): string => {
    const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, d = Math.hypot(mx - CX, my - CY) || 1, e = (r() - 0.5) * 0.9 * Math.hypot(b[0] - a[0], b[1] - a[1]);
    return `M${f(a[0])} ${f(a[1])}Q${f(mx + (mx - CX) / d * e)} ${f(my + (my - CY) / d * e)} ${f(b[0])} ${f(b[1])}`;
  };
  const fios: string[] = [];
  for (let i = 0; i < N_PONTOS; i++) {
    fios.push(fio(no(i), no(i + 1)), fio(no(i), no(i + 2)));
    fios.push(fio(no(i), no(i + 3 + Math.floor(r() * 6))));
    if (r() < 0.6) fios.push(fio(no(i), no(i + 9 + Math.floor(r() * 16))));
  }
  const impulsos: string[] = [];
  for (let k = 0; k < N_IMPULSOS; k++) {
    let i = Math.floor(r() * N_PONTOS);
    const sentido = r() < 0.5 ? 1 : -1, n = 9 + Math.floor(r() * 8), caminho: Ponto[] = [no(i)];
    for (let j = 0; j < n; j++) { i += sentido * (2 + Math.floor(r() * 4)); caminho.push(no(i)); }
    impulsos.push(suave(caminho));
  }
  return { pontos, fios, impulsos };
}
/** quantos impulsos correm: o minimo, mais dois por coisa que pesou na decisao de agora (as entradas com termo, no A; os modulos que
    contribuiram, no modular), ate o teto da rede */
export function impulsosDaDecisao(pesaram: number): number {
  if (!Number.isInteger(pesaram) || pesaram < 0) throw new Error(`quantas coisas pesaram: ${pesaram}`);
  return Math.min(N_IMPULSOS, IMPULSOS_MIN + IMPULSOS_POR_ENTRADA * pesaram);
}

/** o texto de uma tabela, ou erro: falhar alto em vez de mostrar uma chave crua */
function txt<T extends string>(tabela: Record<string, string>, k: T, onde: string): string {
  const v = tabela[k];
  if (v === undefined) throw new Error(`${onde}: "${k}" sem texto`);
  return v;
}

/** a rede viva em SVG, a mesma nos dois scans (o do A e o do modular). `n`: o numero da decisao de agora (null sem decisao); `pesaram`: quantas
    coisas pesaram nela. `correndo`: o tempo do jogo anda (parado, os impulsos congelam onde estao); `surto`: uma decisao nova acabou de chegar
    (a rede acende uma vez; o pai tira a marca quando termina). Com "reduzir movimento" o CSS nao anima nada e os impulsos nao aparecem.
    As classes que o e2e le: svg.mp.rv com data-n e data-impulsos, .rv-fios path, .rv-impulsos path, .rv-pontos circle */
function RedeVivaBruta({ semente, n: decisao, pesaram, tom, movel, correndo, surto }: { semente: number; n: number | null; pesaram: number; tom: TomEstado | null; movel: boolean; correndo: boolean; surto: boolean }) {
  const rede = useMemo(() => redeViva(semente), [semente]), n = impulsosDaDecisao(pesaram);
  /* a 390 o desenho fica menor na tela, entao os tracos e os pontos crescem */
  const K = movel ? 1.9 : 1;
  return (
    <svg className={"mp rv" + (correndo ? "" : " rv--parada") + (surto ? " rv--surto" : "")} viewBox={VB_ANEL} preserveAspectRatio="xMidYMid meet" role="img"
      aria-label="Ilustração do cérebro do pet em atividade. É só um desenho: os pesos de verdade estão no mapa em texto."
      data-n={decisao ?? ""} data-impulsos={n} data-tom={tom ?? "sem"}>
      <g className="rv-fios" strokeWidth={f(1.3 * K)}>{rede.fios.map((d, i) => <path key={i} d={d} />)}</g>
      <g className="rv-impulsos" strokeWidth={f(5 * K)}>
        {rede.impulsos.slice(0, n).map((d, i) => <path key={i} pathLength={1} d={d}
          style={{ animationDuration: f(IMPULSO_S + (i % 5) * IMPULSO_PASSO_S) + "s", animationDelay: f(-i * 0.83) + "s" }} />)}
      </g>
      <g className="rv-pontos">
        {rede.pontos.map((p, i) => <circle key={i} className={p.pisca ? "rv-pisca" : undefined} cx={p.x} cy={p.y} r={f(p.r * K)}
          style={p.pisca ? { animationDelay: f(-(i % 9) * 0.37) + "s" } : undefined} />)}
      </g>
    </svg>
  );
}
export const RedeVivaDesenho = memo(RedeVivaBruta);

/* ---------------------------------------------------------------- a faixa de baixo: a onda da decisao e o estado atual
   Os dois saem do motor e mudam so com a decisao; nada anima. PROPOSTO, SEM FONTE (o desenho da faixa e o tom de cada regra; nenhum numero de jogo) */
/** o tom do "estado atual" por regra do instinto: so a cor e o rosto ao lado do nome da regra. PROPOSTO, SEM FONTE: o tempo livre e o estado
    bom; dormir de noite e continuar dormindo sao neutros; a fome e a exaustao pedem atencao; o pedido de necessidade e o abandono sao os ruins */
export type TomEstado = "ok" | "neutro" | "alerta" | "perigo";
export const TOM_REGRA: Record<RegraLobos, TomEstado> = {
  tempo_livre: "ok", sono_noite: "neutro", sono_continuar: "neutro", fome_moderada: "alerta", sono_exaustao: "alerta", pedido_necessidade: "perigo", abandono: "perigo",
};
const ROSTO: Record<TomEstado, LucideIcon> = { ok: Smile, neutro: Meh, alerta: Annoyed, perigo: Frown };
/** a largura de cada entrada na onda, a meia largura do pico e a altura da onda, em unidades do desenho da onda (so desenho) */
const ONDA_PASSO = 12, ONDA_MEIO = 4, ONDA_A = 40;
/** um pico da onda: de quem e (a entrada, no A; o modulo, no modular) e a altura com sinal, de -1 (contra) a 1 (a favor) */
export interface PicoOnda { entrada: string; altura: number }
/** os picos do A: um por entrada com termo nesta decisao, com o sinal do termo e a forca que o motor da (mapa.acesas.arestas) */
export const picosDaDecisao = (acesas: MapaDecisao | null): PicoOnda[] =>
  acesas ? acesas.arestas.map(x => ({ entrada: x.entrada, altura: Math.sign(x.termo) * x.forca })) : [];
/** os pontos da onda: uma linha de base e, em cada entrada com pico, um pico para cima (a favor) ou para baixo (contra). As entradas vem na
    ordem do motor */
export function pontosDaOnda(entradas: readonly string[], picos: readonly PicoOnda[]): string {
  const pico = new Map(picos.map(x => [x.entrada, x.altura] as const)), base = ONDA_A / 2, pts: string[] = [`0,${base}`];
  for (const [e, a] of pico) {
    if (!entradas.includes(e)) throw new Error(`entrada fora do mapa: ${e}`);
    if (!(Math.abs(a) <= 1)) throw new Error(`pico de ${e} fora de -1 a 1: ${a}`);
  }
  entradas.forEach((e, i) => {
    const a = pico.get(e), x = ONDA_PASSO * i + ONDA_PASSO / 2;
    if (a === undefined) return;
    pts.push(`${x - ONDA_MEIO},${base}`, `${x},${f(base - a * (base - 3))}`, `${x + ONDA_MEIO},${base}`);
  });
  pts.push(`${ONDA_PASSO * entradas.length},${base}`);
  return pts.join(" ");
}
/** a faixa, a mesma nos dois scans: a onda a esquerda e, a direita, um rotulo com o que os filhos disserem */
export function Faixa({ n, entradas, picos, rotulo, tom, regra = "", titulo, children }: {
  n: number | null; entradas: readonly string[]; picos: readonly PicoOnda[]; rotulo: string; tom: TomEstado | null; regra?: string; titulo?: string; children: ReactNode }) {
  return (
    <div className="scan-faixa">
      <svg className="scan-onda" viewBox={`0 0 ${ONDA_PASSO * entradas.length} ${ONDA_A}`} preserveAspectRatio="none" role="img" data-n={n ?? ""}
        aria-label={n !== null ? `A onda desta decisão: ${picos.length} picos, um por coisa que pesou.` : "A onda: ainda sem decisão."}>
        <line className="scan-onda-base" x1="0" y1={ONDA_A / 2} x2={ONDA_PASSO * entradas.length} y2={ONDA_A / 2} />
        <polyline points={pontosDaOnda(entradas, picos)} />
      </svg>
      <p className="scan-estado" data-tom={tom ?? "sem"} data-regra={regra} title={titulo}>
        <span className="scan-estado-rot">{rotulo}</span>
        <b>{children}</b>
      </p>
    </div>
  );
}
export function FaixaEstado({ mapa, decisao }: { mapa: DadosMapa; decisao: LeituraDecisao | null }) {
  const ac = mapa.acesas, tom: TomEstado | null = decisao ? TOM_REGRA[decisao.regra] : null, Rosto = tom ? ROSTO[tom] : null;
  return (
    <Faixa n={ac ? ac.n : null} entradas={[...ENTRADAS_LOBOS, ...mapa.receptores]} picos={picosDaDecisao(ac)} rotulo="estado atual" tom={tom} regra={decisao ? decisao.regra : ""}>
      {Rosto && <Rosto aria-hidden="true" />}{decisao ? TXT_REGRA[decisao.regra] : "sem decisão"}
    </Faixa>
  );
}

/* ---------------------------------------------------------------- o mapa em texto: o mesmo mapa, em lista e tabela (D1-7) */
function MapaEmTexto({ mapa, d }: { mapa: DadosMapa; d: LeituraDecisao | null }) {
  const ac = mapa.acesas;
  return <>
    {d && ac ? <>
      <p>Nesta decisão: a regra <b>{REGRA_TXT[d.regra]}</b> e a ação <b>{ACAO_CURTA[d.acao]}</b>. Os pesos acesos, do mais forte para o mais fraco:</p>
      <ol className="db-texto-acesas">{[...ac.arestas].sort((p, r) => r.forca - p.forca).map(x =>
        <li key={x.entrada}>{txt(TXT_ENTRADA, x.entrada, "entrada")} · {x.termo < 0 ? "contra" : "a favor"} · força <em>{pct(x.forca, 0, false)}</em></li>)}</ol>
    </> : <p>Ainda sem decisão: nada aceso.</p>}
    <table>
      <caption>Os {mapa.arestas.length} pesos, por regra (inteiros do motor)</caption>
      <thead><tr><th scope="col">regra</th><th scope="col">ação</th><th scope="col">entrada</th><th scope="col">peso</th><th scope="col">no instinto</th><th scope="col">marca</th></tr></thead>
      <tbody>{mapa.arestas.map(a => <tr key={a.regra + a.acao + a.entrada}>
        <td>{TXT_REGRA[a.regra]}</td><td>{TXT_ACAO[a.acao]}</td><td>{txt(TXT_ENTRADA, a.entrada, "entrada")}</td><td>{a.w}</td><td>{a.w0}</td>
        <td>{(a.aprendido > 0 ? "aprendeu a mais" : a.aprendido < 0 ? "aprendeu a menos" : "instinto") + (a.w < 0 ? " · negativo" : "")}</td></tr>)}</tbody>
    </table>
  </>;
}

/* ---------------------------------------------------------------- o movimento numa decisao nova */
const CONSULTA_REDUZIR = "(prefers-reduced-motion: reduce)";
/** "reduzir movimento" do sistema; sem matchMedia (testes em node) conta como reduzido, que e o lado seguro */
export function useReduzirMovimento(): boolean {
  return useSyncExternalStore(o => {
    if (typeof matchMedia !== "function") return () => {};
    const mq = matchMedia(CONSULTA_REDUZIR); mq.addEventListener("change", o);
    return () => mq.removeEventListener("change", o);
  }, () => typeof matchMedia !== "function" || matchMedia(CONSULTA_REDUZIR).matches, () => true);
}
/** o numero da decisao cuja varredura e pulso estao passando, ou null. So uma decisao NOVA dispara: o numero diferente do que ja estava na tela
    (o primeiro quadro, ao abrir, nao pulsa), com `pode` (tempo vivo e sem "reduzir movimento") e depois que a decisao anterior ficou na tela pelo
    menos o tempo da animacao (VARREDURA_MS + PULSO_MS, mais a folga do timer). Em avanco rapido (10 min por segundo do pet, uma decisao a cada 15 min dele) as
    decisoes chegam mais depressa que a animacao e so o destaque troca: nada vira pisca-pisca (guia 11). O timer tira a varredura e o pulso
    do DOM, entao nada fica em loop. O relogio do navegador aqui e so vista */
export function useDecisaoNova(n: number | null, pode: boolean): number | null {
  const visto = useRef(n), desde = useRef(performance.now()), [mov, setMov] = useState<number | null>(null);
  useEffect(() => {
    if (visto.current === n) return;
    visto.current = n;
    const agora = performance.now(), folgado = agora - desde.current >= VARREDURA_MS + PULSO_MS + FOLGA_MS;
    desde.current = agora;
    if (n === null || !pode) setMov(null);
    else if (folgado) setMov(n);   // chegou antes do fim da anterior (avanco rapido): nao interrompe nem recomeca
  }, [n, pode]);
  /* o fim: o timer e so do `mov`, para uma mudanca de `pode` no meio da animacao nao deixar a varredura presa no DOM */
  useEffect(() => {
    if (mov === null) return;
    const t = setTimeout(() => setMov(null), VARREDURA_MS + PULSO_MS + FOLGA_MS);
    return () => clearTimeout(t);
  }, [mov]);
  return mov;
}

/** a escala do desenho (a largura renderizada sobre a do viewBox, a menor das duas por causa do "meet") numa variavel CSS: o CSS pede o texto
    do mapa com pelo menos 11 px na tela, max(base, 11px / escala), em unidades do viewBox. So vista */
const TEXTO_MIN_PX = 11;
export function useEscalaDoMapa(ref: { current: HTMLElement | null }, ativo: boolean): void {
  useEffect(() => {
    const el = ref.current; if (!el || !ativo || typeof ResizeObserver !== "function") return;
    const medir = () => { const w = el.clientWidth, h = el.clientHeight; if (w > 0 && h > 0) el.style.setProperty("--scan-esc", String(Math.min(w / VB_L, h / VB_A))); el.style.setProperty("--scan-txt-min", TEXTO_MIN_PX + "px"); };
    medir();
    const ro = new ResizeObserver(medir); ro.observe(el);
    return () => ro.disconnect();
  }, [ref, ativo]);
}

/* ---------------------------------------------------------------- o modal */
/** o selo so como forma (D1b-5): o ponto (ao vivo), as duas barras (pausado) ou o triangulo (replay), com o nome acessivel e a dica */
const SELO_TXT: Record<EstadoSelo, string> = { vivo: "ao vivo", pausado: "pausado", replay: "replay: uma decisão do passado" };
export function SeloForma({ replay }: { replay: boolean }) {
  const estado = useEstadoSelo(replay);
  return <span className={"db-selo db-selo--" + estado} role="img" aria-label={SELO_TXT[estado]} title={SELO_TXT[estado]}><i aria-hidden="true" /></span>;
}

/** a dica do "i" (D1b-7): a forma e so desenho, e a legenda curta que saiu do rodape */
function Dica({ aberta }: { aberta: boolean }) {
  return (
    <div className="scan-dica scan-cx" id="db-dica" hidden={!aberta}>
      <p>A rede é só desenho: ela imita um cérebro em atividade, não mostra as ligações de verdade. Cada pet tem a sua.</p>
      <p className="scan-dica-selo">Quanto mais coisas pesaram na decisão de agora, mais impulsos correm; a cor deles é a do estado atual.</p>
      <p className="scan-dica-selo">Embaixo: a onda tem um pico por coisa que pesou nesta decisão, para cima a favor e para baixo contra; o estado atual é a regra do instinto que valeu.</p>
      <p className="scan-dica-selo">Os pesos de verdade estão no mapa em texto. Ao lado do título: o ponto é ao vivo, as duas barras são pausado e o triângulo é um replay.</p>
    </div>
  );
}

export function ScanDigiBrain({ fechar, movel, replay = false, chamado }: { fechar: () => void; movel: boolean; replay?: boolean; chamado?: ReactNode }) {
  const { motor: m } = useJogo(), db = m.digibrain();
  const ref = useRef<HTMLDialogElement>(null), saindo = useRef(false);
  const giro = useRef<HTMLDivElement>(null), [verTexto, setVerTexto] = useState(false), [verDica, setVerDica] = useState(false);
  useEscalaDoMapa(giro, db !== null && !verTexto);
  const selo = useEstadoSelo(replay), reduzir = useReduzirMovimento();
  const mov = useDecisaoNova(db?.mapa.acesas ? db.mapa.acesas.n : null, selo === "vivo" && !reduzir);
  /* o modal: showModal prende o foco e deixa o resto inerte; o Esc dispara o close nativo; ao fechar, o foco volta a quem abriu (modal.ts) */
  useEffect(() => {
    const dlg = ref.current; if (!dlg) return;
    saindo.current = false;
    abrirModal(dlg);
    return () => { saindo.current = true; if (dlg.open) dlg.close(); };
  }, []);
  /* o Esc com a dica aberta fecha so a dica */
  const cancelar = (e: SyntheticEvent<HTMLDialogElement>) => { if (verDica) { e.preventDefault(); setVerDica(false); } };
  /* um clique fora fecha (D1b-3): o clique no ::backdrop chega ao proprio <dialog>, que nao tem area propria (a caixa o preenche inteiro) */
  const cliqueFora = (e: MouseEvent<HTMLDialogElement>) => { if (e.target === e.currentTarget) ref.current?.close(); };

  const d = db?.decisao ?? null, mapa = db?.mapa ?? null;
  if (mapa && (d === null) !== (mapa.acesas === null)) throw new Error("a decisao e as arestas acesas fora de par");
  return (
    <dialog className={"scan" + (movel ? " scan--folha" : "")} id="pet-painel" data-painel-pet="digibrain" aria-labelledby="db-titulo" ref={ref}
      style={{ "--scan-giro-graus": GIRO_GRAUS + "deg", "--scan-giro-ciclo": GIRO_CICLO_S + "s", "--scan-t-varre": VARREDURA_MS + "ms", "--scan-t-pulso": PULSO_MS + "ms" } as CSSProperties}
      onCancel={cancelar} onClick={cliqueFora} onClose={() => { if (!saindo.current) fechar(); }}>
      <div className="scan-in scan-cx digibrain">
        {movel && <span className="scan-alca" aria-hidden="true" />}
        <header className="scan-topo">
          <h2 className="scan-tit" id="db-titulo"><Brain aria-hidden="true" /><span className="scan-tit-nome">DigiBrain</span></h2>
          <SeloForma replay={replay} />
          {mapa && <>
            <button type="button" className="scan-ic scan-info" aria-label="O que é este desenho" aria-expanded={verDica} aria-controls="db-dica"
              onClick={() => setVerDica(v => !v)}><Info aria-hidden="true" /></button>
            <button type="button" className="scan-ic scan-texto-bt" aria-label="O mapa em texto" aria-pressed={verTexto}
              onClick={() => setVerTexto(v => !v)}><List aria-hidden="true" /></button>
          </>}
          <button type="button" className="scan-ic scan-fechar" aria-label="Fechar DigiBrain" title="Fechar (Esc)" data-autofocus onClick={() => ref.current?.close()}>
            <X aria-hidden="true" /></button>
        </header>
        {mapa && <Dica aberta={verDica} />}
        {mapa === null ? <p className="scan-vazio">Este pet não tem mapa dos pesos.</p> : (
          <div className="scan-corpo">
            <div className="scan-moldura">
              {/* os cantos em colchete do scanner: so desenho; saem no mapa em texto, para nao ficarem por cima das letras */}
              {!verTexto && <><i className="scan-canto scan-canto--ce" aria-hidden="true" /><i className="scan-canto scan-canto--cd" aria-hidden="true" /><i className="scan-canto scan-canto--be" aria-hidden="true" /><i className="scan-canto scan-canto--bd" aria-hidden="true" /></>}
              {verTexto
                ? <section className="scan-texto db-texto" id="db-texto" aria-label="O mapa em texto" tabIndex={0}><MapaEmTexto mapa={mapa} d={d} /></section>
                : <>
                  {mov !== null && <div className="scan-varre-trilho" key={"varre" + mov} aria-hidden="true"><div className="scan-varredura" /></div>}
                  <div className="scan-giro" ref={giro}><RedeVivaDesenho semente={m.semente} n={mapa.acesas ? mapa.acesas.n : null} pesaram={mapa.acesas ? mapa.acesas.arestas.length : 0} tom={d ? TOM_REGRA[d.regra] : null} movel={movel} correndo={selo === "vivo"} surto={mov !== null} /></div>
                </>}
            </div>
            <FaixaEstado mapa={mapa} decisao={d} />
          </div>
        )}
      </div>
      {/* o cartao do chamado do pet (D1-10) fica fora da caixa, no alto ao centro da tela, como na tela Pet; depois da caixa no DOM, para o foco
          nao cair num botao do chamado ao abrir (rev-a11y da D1b) */}
      {chamado}
    </dialog>
  );
}
