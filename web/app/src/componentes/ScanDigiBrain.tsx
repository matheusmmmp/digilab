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
   O visual do scanner (pedido do Matheus em 2026-11-11, com uma imagem de referencia; docs/TAREFA_V3_UX_TELA_PET.md, "D1e"): a rede em anel no
   lugar da silhueta de cerebro, o quadro escuro com cantos em colchete, o nome ao lado do icone no desktop e, embaixo, uma faixa com a onda da
   decisao e o "estado atual". A coluna de cinco barras da referencia (percepcao, memoria, impulsos, emocao, social) nao entra. A onda e o
   estado saem do motor: a onda e um pico por entrada com termo nesta decisao (mapa.acesas.arestas: o sinal do termo e a forca), e o estado
   atual e a regra do instinto que valeu (decisao.regra). O motor nao tem um estado chamado "calmo": nada disso e inventado na tela. */
import { memo, useEffect, useRef, useState, useSyncExternalStore, type CSSProperties, type MouseEvent, type ReactNode, type SyntheticEvent } from "react";
import { Annoyed, Brain, Frown, Info, List, Meh, Smile, X, type LucideIcon } from "lucide-react";
import { ACOES_LOBOS, ENTRADAS_LOBOS, REGRAS_LOBOS, type AcaoPet, type LeituraDecisao, type MapaDecisao, type RegraLobos } from "../../motor/index.ts";
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

/* ---------------------------------------------------------------- a geometria do desenho (unidades do desenho; so desenho)
   PROPOSTO, SEM FONTE (o anel, pedido do Matheus em 2026-11-11 com uma imagem de referencia; substitui a silhueta de cerebro da D1-11 e da
   D1b-2): a rede e um anel. As acoes ficam num arco a esquerda (de cima para baixo, na ordem de ACOES_LOBOS), o que o pet sente num arco a
   direita (as entradas na ordem do motor e os receptores do corpo no fim, embaixo), e as regras num circulo por dentro (a primeira em cima, no
   sentido do relogio, na ordem em que o instinto as testa). Cada fio sai da entrada, passa pela regra e chega a acao dando a volta pelo anel,
   pelo lado mais curto; a "pista" de cada fio (o quanto ele se afasta do meio da faixa) sai so dos indices dos tres nos, para os fios nao
   ficarem uns em cima dos outros. O viewBox guarda a proporcao 880 x 552 do campo pequeno (D1c). */
const VB_L = 880, VB_A = 552, CX = 440, CY = 276;
const VB_ANEL = `0 0 ${VB_L} ${VB_A}`;
/** o raio dos arcos de fora (acoes e entradas) e o do circulo das regras */
const R_FORA = 212, R_REGRA = 150;
/** a meia abertura, em graus, do arco das acoes (a esquerda) e do das entradas (a direita) */
const ARCO_ACOES = 60, ARCO_ENTRADAS = 78;
/** as pistas dos fios: 7 pistas de 14 unidades, de -42 a +42 em volta do caminho direto */
const N_PISTAS = 7, PISTA = 14;
/** de quantos em quantos graus o fio ganha um ponto */
const PASSO_GRAUS = 10;
/** os rotulos das regioes (D1b-6), com os nomes que o dono entende; o id e o do lobo de cada uma (data-lobo): as acoes no canto de cima a
    esquerda, as regras no meio do anel e a percepcao no canto de cima a direita. Os "receptores do corpo", no canto de baixo a direita */
const REGIOES: [string, string, number, number, "start" | "middle" | "end"][] = [
  ["decisao", "ações", 40, 50, "start"], ["impulsos", "regras", CX, CY + 8, "middle"], ["percepcao", "percepção", VB_L - 40, 50, "end"]];
const SUB_CORPO = { x: VB_L - 40, y: VB_A - 30 };
/* a silhueta de cerebro de antes (D1-11, D1b-2): o scan do A v11 nao a desenha mais, mas o do cerebro modular (ScanDigiBrainLab.tsx, o pet
   do laboratorio) ainda desenha, com o viewBox recortado nela (x 90 a 970, y 16 a 568). Ficam aqui so para ele */
export const VB = `90 16 ${VB_L} ${VB_A}`;
export const SILHUETA = "M120 330C100 210 220 80 420 62C600 45 820 90 890 220C935 300 900 390 820 420C760 440 700 430 650 445C600 470 540 500 470 488C380 475 330 430 250 430C170 430 130 390 120 330Z";
export const CEREBELO = "M650 445C655 505 760 535 825 505C865 485 860 440 820 420C760 440 700 430 650 445Z";
export const DIVISAS = ["M380 66C360 180 372 300 345 410", "M612 54C592 170 602 300 592 420"];
export const Y_REGIOES = 36;
const f = (v: number): number => Math.round(v * 10) / 10;

type Ponto = [number, number];
/** um no no anel: o angulo em graus (0 a direita, 90 embaixo, como na tela) e o raio */
interface Polar { g: number; r: number }
const xy = (p: Polar): Ponto => { const a = p.g * Math.PI / 180; return [CX + p.r * Math.cos(a), CY + p.r * Math.sin(a)]; };
function posicoes(receptores: readonly string[]) {
  const ent = [...ENTRADAS_LOBOS, ...receptores], n = ent.length;
  const pe = new Map<string, Polar>(ent.map((e, i) => [e, { g: n === 1 ? 0 : -ARCO_ENTRADAS + 2 * ARCO_ENTRADAS * i / (n - 1), r: R_FORA }]));
  const pr = new Map<RegraLobos, Polar>(REGRAS_LOBOS.map((r, i) => [r, { g: -90 + 360 * i / REGRAS_LOBOS.length, r: R_REGRA }]));
  const pa = new Map<AcaoPet, Polar>(ACOES_LOBOS.map((a, i) => [a, { g: 180 + ARCO_ACOES - 2 * ARCO_ACOES * i / (ACOES_LOBOS.length - 1), r: R_FORA }]));
  return { ent, pe, pr, pa };
}
/** os pontos de um trecho do fio, de `a` a `b` pelo lado mais curto do anel; `lombada` afasta o meio do trecho do caminho direto */
function trecho(a: Polar, b: Polar, lombada: number): Ponto[] {
  const dg = ((b.g - a.g) % 360 + 540) % 360 - 180, n = Math.max(2, Math.ceil(Math.abs(dg) / PASSO_GRAUS)), pts: Ponto[] = [];
  for (let k = 0; k <= n; k++) { const t = k / n; pts.push(xy({ g: a.g + dg * t, r: a.r + (b.r - a.r) * t + lombada * Math.sin(Math.PI * t) })); }
  return pts;
}
/** o trecho como curva suave (quadraticas pelos pontos medios), a partir do primeiro ponto, que ja esta no caminho */
function suave(p: Ponto[]): string {
  let d = "";
  for (let i = 1; i < p.length - 1; i++) d += `Q${f(p[i]![0])} ${f(p[i]![1])} ${f((p[i]![0] + p[i + 1]![0]) / 2)} ${f((p[i]![1] + p[i + 1]![1]) / 2)}`;
  const u = p[p.length - 1]!;
  return d + `L${f(u[0])} ${f(u[1])}`;
}
/** afasta os rotulos que ficariam uns em cima dos outros: recebe os y naturais em ordem crescente e devolve os y com pelo menos `folga` entre
    vizinhos, sem passar de `teto` */
function espalhar(ys: number[], folga: number, teto: number): number[] {
  const o = [...ys];
  for (let i = 1; i < o.length; i++) o[i] = Math.max(o[i]!, o[i - 1]! + folga);
  if (o.length && o[o.length - 1]! > teto) { o[o.length - 1] = teto; for (let i = o.length - 2; i >= 0; i--) o[i] = Math.min(o[i]!, o[i + 1]! - folga); }
  return o;
}

/** o texto de uma tabela, ou erro: falhar alto em vez de mostrar uma chave crua */
function txt<T extends string>(tabela: Record<string, string>, k: T, onde: string): string {
  const v = tabela[k];
  if (v === undefined) throw new Error(`${onde}: "${k}" sem texto`);
  return v;
}

/** o mapa dos pesos em SVG (D1-1), em anel. As classes que o e2e le: svg.mp com data-n, .mp-pesos path, .mp-acesas path, .mp-lit, .mp-cand,
    .mp-esc, .mp-pct, .mp-reg[data-lobo]. `movendo`: o pulso (um ponto que percorre cada aresta acesa) esta no DOM; o pai o tira quando termina */
function MapaScanBruto({ mapa, decisao, movel, movendo }: { mapa: DadosMapa; decisao: LeituraDecisao | null; movel: boolean; movendo: boolean }) {
  /* o ponto tocado (D1c): o rotulo dele aparece; tocar de novo, ou em outro, troca. So vista */
  const [tocado, setTocado] = useState<string | null>(null);
  const tocar = (id: string) => () => setTocado(t => t === id ? null : id);
  const cls = (id: string, base: string): string => base + (tocado === id ? " mp-toque" : "");
  const { ent, pe, pr, pa } = posicoes(mapa.receptores);
  for (const a of mapa.arestas) {
    if (!pe.has(a.entrada)) throw new Error(`entrada fora do mapa: ${a.entrada}`);
    if (!pr.has(a.regra)) throw new Error(`regra fora do mapa: ${a.regra}`);
    if (!pa.has(a.acao)) throw new Error(`ação fora do mapa: ${a.acao}`);
  }
  const ac: MapaDecisao | null = mapa.acesas;
  if (ac !== null && decisao !== null && (ac.n !== decisao.n || ac.acao !== decisao.acao)) throw new Error("o mapa e a leitura de decisoes diferentes");
  if ((ac === null) !== (decisao === null)) throw new Error("a decisao e as arestas acesas fora de par");
  const curva = (e: string, r: RegraLobos, a: AcaoPet): string => {
    const ie = ent.indexOf(e), ir = REGRAS_LOBOS.indexOf(r), ia = ACOES_LOBOS.indexOf(a);
    if (ie < 0) throw new Error(`entrada fora do mapa: ${e}`);
    const p1 = pe.get(e)!, p2 = pr.get(r)!, p3 = pa.get(a)!, meio = (N_PISTAS - 1) / 2;
    const ida = trecho(p1, p2, PISTA * ((ie * 5 + ia * 3 + ir) % N_PISTAS - meio)), volta = trecho(p2, p3, PISTA * ((ie * 3 + ia * 5 + ir * 2) % N_PISTAS - meio));
    return `M${f(ida[0]![0])} ${f(ida[0]![1])}` + suave(ida) + suave(volta);
  };
  const top = new Set(decisao ? decisao.percepcao.map(p => p.entrada) : []);
  /* as entradas das arestas acesas: o rotulo delas fica sempre a vista (D1c), mesmo fora das que mais pesaram */
  const caminho = new Set(ac ? ac.arestas.map(x => x.entrada) : []);
  const chance = new Map(decisao ? decisao.chances.map(c => [c.acao, c.chance]) : []);
  /* a espessura de hoje vezes a escala do desenho; os raios idem (a 390 o desenho fica menor, entao os tracos crescem) */
  const K = movel ? 2.6 : 1.5, R = movel ? 1.8 : 1;
  const tracejado = (neg: boolean): CSSProperties | undefined => neg ? { strokeDasharray: `${f(6 * K)} ${f(4 * K)}` } : undefined;
  /* os rotulos das entradas que ficam sempre a vista (as que mais pesaram e as do caminho aceso) se afastam para nao se cobrirem; os outros,
     que so aparecem ao passar o mouse ou ao tocar, ficam ao lado do ponto. A folga e a altura do texto na tela (11 px) em unidades do desenho */
  const yNatural = (e: string): number => xy(pe.get(e)!)[1] + 5 * R;
  const fixos = ent.filter(e => top.has(e) || caminho.has(e));
  const yFixos = new Map(espalhar(fixos.map(yNatural), movel ? 46 : 28, VB_A - 8).map((y, i) => [fixos[i]!, y]));
  const rotulo = ac && decisao
    ? `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Nesta decisão: regra ${TXT_REGRA[ac.regra]}, escolheu ${TXT_ACAO[ac.acao]} com ${Math.round(chance.get(ac.acao)! * 100)}% de chance.`
    : `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Ainda sem decisão.`;

  return (
    <svg className="mp" viewBox={VB_ANEL} preserveAspectRatio="xMidYMid meet" role="img" aria-label={rotulo} data-n={ac ? ac.n : ""}>
      <g aria-hidden="true">
        {REGIOES.map(([lobo, nome, x, y, ancora]) => <text key={lobo} className="mp-reg" data-lobo={lobo} x={x} y={y} textAnchor={ancora}>{nome}</text>)}
        {mapa.receptores.length > 0 && <text className="mp-sub" x={SUB_CORPO.x} y={SUB_CORPO.y} textAnchor="end">receptores do corpo</text>}
      </g>
      <g className={"mp-pesos" + (ac ? " mp-pesos--fundo" : "")}>
        {mapa.arestas.map(a => {
          const cls = a.aprendido > 0 ? "mp-mais" : a.aprendido < 0 ? "mp-menos" : "mp-prior";
          return <path key={a.regra + a.acao + a.entrada} className={cls} d={curva(a.entrada, a.regra, a.acao)} strokeWidth={f(K * (0.4 + a.espessura * 1.4))}
            strokeOpacity={a.aprendido === 0 ? undefined : f(0.35 + 0.65 * Math.sqrt(Math.abs(a.aprendido)))} style={tracejado(a.w < 0)} />;
        })}
      </g>
      {ac && <g className="mp-acesas">
        {ac.arestas.map(x => <path key={x.entrada} className={x.termo < 0 ? "mp-neg" : undefined} d={curva(x.entrada, ac.regra, ac.acao)}
          strokeWidth={f(K * (0.6 + 3 * x.forca))} strokeOpacity={f(0.35 + 0.65 * x.forca)} style={tracejado(x.termo < 0)} />)}
      </g>}
      {/* o pulso: um ponto em cada aresta acesa (entrada, regra, acao), que anda uma vez e some; o pai tira o grupo quando termina */}
      {ac && movendo && <g className="mp-pulso" aria-hidden="true">
        {ac.arestas.map(x => <path key={x.entrada} pathLength={1} d={curva(x.entrada, ac.regra, ac.acao)} strokeWidth={f(7 * R)} />)}
      </g>}
      <g className="mp-nos">
        {ent.map((e, i) => {
          const [x, y] = xy(pe.get(e)!), lit = top.has(e);
          return <g key={e} className={cls("e" + e, "mp-no" + (i >= ENTRADAS_LOBOS.length ? " mp-corpo" : "") + (lit ? " mp-lit" : "") + (caminho.has(e) ? " mp-caminho" : ""))}
            data-entrada={e} onClick={tocar("e" + e)}>
            <circle className="mp-alvo" cx={f(x)} cy={f(y)} r={f(R * (movel ? 16 : 12))} />
            <circle cx={f(x)} cy={f(y)} r={f(R * (lit ? 6 : 4))} /><text x={f(x + 13 * R)} y={f(yFixos.get(e) ?? yNatural(e))}>{txt(TXT_ENTRADA, e, "entrada")}</text></g>;
        })}
        {REGRAS_LOBOS.map(r => {
          const p = pr.get(r)!, [x, y] = xy(p), lit = ac !== null && r === ac.regra;
          /* o rotulo da regra aponta para o meio do anel, onde nao ha fio */
          const c = Math.cos(p.g * Math.PI / 180), s = Math.sin(p.g * Math.PI / 180);
          const [tx, ty] = xy({ g: p.g, r: p.r - 26 * R });
          return <g key={r} className={cls("r" + r, "mp-no" + (lit ? " mp-lit" : ""))} data-regra={r} onClick={tocar("r" + r)}>
            <circle className="mp-alvo" cx={f(x)} cy={f(y)} r={f(R * 14)} />
            <circle cx={f(x)} cy={f(y)} r={f(R * (lit ? 7.5 : 5))} />
            <text x={f(tx)} y={f(ty + (s < -0.35 ? 14 : s > 0.35 ? -2 : 6) * R)} textAnchor={c > 0.35 ? "end" : c < -0.35 ? "start" : "middle"}>{TXT_REGRA[r]}</text></g>;
        })}
        {ACOES_LOBOS.map(a => {
          const [x, y] = xy(pa.get(a)!), c = chance.get(a), esc = ac !== null && a === ac.acao;
          const pc = c === undefined ? null : Math.round(c * 100) + "%";
          return <g key={a} className={cls("a" + a, "mp-no" + (c !== undefined ? " mp-cand" : "") + (esc ? " mp-esc" : ""))} data-acao={a} onClick={tocar("a" + a)}>
            <circle className="mp-alvo" cx={f(x)} cy={f(y)} r={f(R * 14)} />
            <circle cx={f(x)} cy={f(y)} r={f(R * (esc ? 8.5 : c !== undefined ? 6.5 : 5))} />
            <text x={f(x - 14 * R)} y={f(y + 5 * R)} textAnchor="end">{TXT_ACAO[a]}{pc !== null && <tspan className="mp-pct"> {pc}</tspan>}</text></g>;
        })}
      </g>
    </svg>
  );
}

/** a assinatura do que o desenho mostra: Motor.digibrain() devolve objetos novos a cada render, entao o memo compara pelo conteudo que muda
    (os pesos w de cada aresta, os receptores, a decisao n e as acesas n), nao pela identidade */
const assinatura = (p: { mapa: DadosMapa; decisao: LeituraDecisao | null }): string =>
  p.mapa.receptores.join() + "|" + p.mapa.arestas.map(a => a.w).join() + "|" + (p.mapa.acesas ? p.mapa.acesas.n : "") + "|" + (p.decisao ? p.decisao.n : "");
export const MapaScan = memo(MapaScanBruto, (a, b) => a.movel === b.movel && a.movendo === b.movendo && assinatura(a) === assinatura(b));

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
/** os pontos da onda: uma linha de base e, em cada entrada com termo nesta decisao, um pico para cima (a favor) ou para baixo (contra), da
    altura da forca que o motor da (mapa.acesas.arestas). As entradas vem na ordem do mapa (as do motor e os receptores do corpo) */
export function pontosDaOnda(entradas: readonly string[], acesas: MapaDecisao | null): string {
  const termo = new Map(acesas ? acesas.arestas.map(x => [x.entrada, x] as const) : []), base = ONDA_A / 2, pts: string[] = [`0,${base}`];
  for (const e of termo.keys()) if (!entradas.includes(e)) throw new Error(`entrada fora do mapa: ${e}`);
  entradas.forEach((e, i) => {
    const t = termo.get(e), x = ONDA_PASSO * i + ONDA_PASSO / 2;
    if (t === undefined) return;
    pts.push(`${x - ONDA_MEIO},${base}`, `${x},${f(base - Math.sign(t.termo) * t.forca * (base - 3))}`, `${x + ONDA_MEIO},${base}`);
  });
  pts.push(`${ONDA_PASSO * entradas.length},${base}`);
  return pts.join(" ");
}
export function FaixaEstado({ mapa, decisao }: { mapa: DadosMapa; decisao: LeituraDecisao | null }) {
  const ent = [...ENTRADAS_LOBOS, ...mapa.receptores], ac = mapa.acesas;
  const tom: TomEstado | null = decisao ? TOM_REGRA[decisao.regra] : null, Rosto = tom ? ROSTO[tom] : null;
  return (
    <div className="scan-faixa">
      <svg className="scan-onda" viewBox={`0 0 ${ONDA_PASSO * ent.length} ${ONDA_A}`} preserveAspectRatio="none" role="img" data-n={ac ? ac.n : ""}
        aria-label={ac ? `A onda desta decisão: ${ac.arestas.length} picos, um por coisa que pesou.` : "A onda: ainda sem decisão."}>
        <line className="scan-onda-base" x1="0" y1={ONDA_A / 2} x2={ONDA_PASSO * ent.length} y2={ONDA_A / 2} />
        <polyline points={pontosDaOnda(ent, ac)} />
      </svg>
      <p className="scan-estado" data-tom={tom ?? "sem"} data-regra={decisao ? decisao.regra : ""}>
        <span className="scan-estado-rot">estado atual</span>
        <b>{Rosto && <Rosto aria-hidden="true" />}{decisao ? TXT_REGRA[decisao.regra] : "sem decisão"}</b>
      </p>
    </div>
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
function Dica({ receptores, aberta }: { receptores: boolean; aberta: boolean }) {
  return (
    <div className="scan-dica scan-cx" id="db-dica" hidden={!aberta}>
      <p>A forma de anel é só desenho. Cada ponto é o que o pet sente (à direita), uma regra (por dentro) ou uma ação (à esquerda); cada fio é um peso.</p>
      <p className="scan-dica-selo">Embaixo: a onda tem um pico por coisa que pesou nesta decisão, para cima a favor e para baixo contra; o estado atual é a regra do instinto que valeu.</p>
      <p className="scan-dica-selo">Ao lado do título: o ponto é ao vivo, as duas barras são pausado e o triângulo é um replay.</p>
      <p className="scan-dica-selo">Só o caminho desta decisão tem nome; passe o mouse ou toque num ponto para ver o dele, ou abra o mapa em texto.</p>
      <ul className="mp-leg">
        <li><span className="scan-leg scan-leg--aceso" />esta decisão</li><li><span className="scan-leg scan-leg--mais" />aprendeu a mais</li>
        <li><span className="scan-leg scan-leg--menos" />aprendeu a menos</li><li><span className="scan-leg scan-leg--neg" />peso negativo</li>
        {receptores && <li><span className="scan-leg scan-leg--corpo" />receptor do corpo</li>}
      </ul>
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
        {mapa && <Dica receptores={mapa.receptores.length > 0} aberta={verDica} />}
        {mapa === null ? <p className="scan-vazio">Este pet não tem mapa dos pesos.</p> : (
          <div className="scan-corpo">
            <div className="scan-moldura">
              {/* os cantos em colchete do scanner: so desenho */}
              <i className="scan-canto scan-canto--ce" aria-hidden="true" /><i className="scan-canto scan-canto--cd" aria-hidden="true" />
              <i className="scan-canto scan-canto--be" aria-hidden="true" /><i className="scan-canto scan-canto--bd" aria-hidden="true" />
              {verTexto
                ? <section className="scan-texto db-texto" id="db-texto" aria-label="O mapa em texto" tabIndex={0}><MapaEmTexto mapa={mapa} d={d} /></section>
                : <>
                  {mov !== null && <div className="scan-varre-trilho" key={"varre" + mov} aria-hidden="true"><div className="scan-varredura" /></div>}
                  <div className="scan-giro" ref={giro}><MapaScan mapa={mapa} decisao={d} movel={movel} movendo={mov !== null} /></div>
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
