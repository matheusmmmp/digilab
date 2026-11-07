/* O painel DigiBrain como modal pequeno (D1b da UX_TELA_PET; prancha aprovada em docs/pranchas/ux-digibrain/modal.html, decisoes D1b-1 a
   D1b-7 de docs/PROPOSTAS_V3_UX_TELA_PET.md, sobre a direcao A "scan holografico" da D1). Um <dialog> modal (foco preso, Esc fecha, um clique
   fora fecha, o foco volta a quem abriu) so com o mapa dos pesos: no desktop, a direita, com a ilha e o pet a vista em volta; no celular, uma
   folha baixa. So le o motor por useJogo(): todo numero sai de Motor.digibrain() (mapa, decisao); nenhum mudarMotor aqui. Cada ponto do
   desenho e um no do motor (entrada, regra ou acao) e cada fio e uma aresta de mapa.arestas; a forma de cerebro e as regioes sao so desenho,
   e a dica do "i" diz isso. O movimento e o da D1: so vista e so numa decisao nova (mapa.acesas.n muda), a varredura passa uma vez e o pulso
   percorre as arestas acesas, os dois terminam; o giro lento do plano (so no desktop) e CSS puro. Com "reduzir movimento" nada se move; no
   replay e com o tempo pausado so o destaque troca. O relogio do navegador aqui e so animacao: nada do que e gravado depende dele.
   A ilha continua a pleno ritmo por tras (D1b-3: sem CENA.coberto e sem desfoque de tela cheia). */
import { memo, useEffect, useRef, useState, useSyncExternalStore, type CSSProperties, type MouseEvent, type ReactNode, type SyntheticEvent } from "react";
import { Info, List, X } from "lucide-react";
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
   PROPOSTO, SEM FONTE (D1-11, D1b-2): a frente do cerebro fica a esquerda. Percepcao atras (um arco: as entradas na ordem do motor e os
   receptores do corpo no fim, embaixo), as regras no meio (de cima para baixo, na ordem em que o instinto as testa), as acoes na frente (na ordem
   de ACOES_LOBOS). O viewBox e recortado na silhueta (x 90 a 970, y 16 a 568), para o desenho encher o modal. */
const VB_X = 90, VB_Y = 16, VB_L = 880, VB_A = 552;
const VB = `${VB_X} ${VB_Y} ${VB_L} ${VB_A}`;
const SILHUETA = "M120 330C100 210 220 80 420 62C600 45 820 90 890 220C935 300 900 390 820 420C760 440 700 430 650 445C600 470 540 500 470 488C380 475 330 430 250 430C170 430 130 390 120 330Z";
const CEREBELO = "M650 445C655 505 760 535 825 505C865 485 860 440 820 420C760 440 700 430 650 445Z";
const DIVISAS = ["M380 66C360 180 372 300 345 410", "M612 54C592 170 602 300 592 420"];
/** as regioes (D1b-6): tres rotulos curtos na mesma linha, com os nomes que o dono entende; o id e o do lobo de cada uma (data-lobo). O "pesou
    mais" e a regiao sem pesos da memoria sairam do modal. Os "receptores do corpo" ficam centrados sob o cerebelo */
const REGIOES: [string, string, number][] = [["decisao", "ações", 250], ["impulsos", "regras", 490], ["percepcao", "percepção", 760]];
const Y_REGIOES = 36, SUB_CORPO = { x: 757, y: 556 };
const f = (v: number): number => Math.round(v * 10) / 10;

type Ponto = [number, number];
function posicoes(receptores: readonly string[]) {
  const ent = [...ENTRADAS_LOBOS, ...receptores], n = ent.length;
  const pe = new Map<string, Ponto>(ent.map((e, i) => {
    const a = (-75 + 150 * i / (n - 1)) * Math.PI / 180;
    return [e, [650 + 200 * Math.cos(a), 280 + 190 * Math.sin(a)] as Ponto];
  }));
  const pr = new Map<RegraLobos, Ponto>(REGRAS_LOBOS.map((r, i) => [r, [480 + 26 * Math.sin(Math.PI * i / 6), 128 + 44 * i] as Ponto]));
  const pa = new Map<AcaoPet, Ponto>(ACOES_LOBOS.map((a, i) => [a, [285 - 85 * Math.sin(Math.PI * i / 6), 150 + 42 * i] as Ponto]));
  return { ent, pe, pr, pa };
}

/** o texto de uma tabela, ou erro: falhar alto em vez de mostrar uma chave crua */
function txt<T extends string>(tabela: Record<string, string>, k: T, onde: string): string {
  const v = tabela[k];
  if (v === undefined) throw new Error(`${onde}: "${k}" sem texto`);
  return v;
}

/** o mapa dos pesos em SVG (D1-1). As classes que o e2e le: svg.mp com data-n, .mp-pesos path, .mp-acesas path, .mp-lit, .mp-cand, .mp-esc, .mp-pct,
    .mp-reg[data-lobo]. `movendo`: o pulso (um ponto que percorre cada aresta acesa) esta no DOM; o pai o tira quando termina */
function MapaScanBruto({ mapa, decisao, movel, movendo }: { mapa: DadosMapa; decisao: LeituraDecisao | null; movel: boolean; movendo: boolean }) {
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
    const [x1, y1] = pe.get(e) ?? (() => { throw new Error(`entrada fora do mapa: ${e}`); })(), [x2, y2] = pr.get(r)!, [x3, y3] = pa.get(a)!;
    return `M${f(x1)} ${f(y1)}C${f(x1 - 110)} ${f(y1)} ${f(x2 + 90)} ${f(y2)} ${f(x2)} ${f(y2)}C${f(x2 - 90)} ${f(y2)} ${f(x3 + 90)} ${f(y3)} ${f(x3)} ${f(y3)}`;
  };
  const top = new Set(decisao ? decisao.percepcao.map(p => p.entrada) : []);
  const chance = new Map(decisao ? decisao.chances.map(c => [c.acao, c.chance]) : []);
  /* a espessura de hoje (MapaPesos.tsx) vezes a escala do desenho; os raios idem (a 390 o desenho fica menor, entao os tracos crescem) */
  const K = movel ? 2.2 : 1.1, R = movel ? 1.8 : 1;
  const tracejado = (neg: boolean): CSSProperties | undefined => neg ? { strokeDasharray: `${f(6 * K)} ${f(4 * K)}` } : undefined;
  const rotulo = ac && decisao
    ? `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Nesta decisão: regra ${TXT_REGRA[ac.regra]}, escolheu ${TXT_ACAO[ac.acao]} com ${Math.round(chance.get(ac.acao)! * 100)}% de chance.`
    : `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Ainda sem decisão.`;

  return (
    <svg className="mp" viewBox={VB} preserveAspectRatio="xMidYMid meet" role="img" aria-label={rotulo} data-n={ac ? ac.n : ""}>
      <defs><pattern id="db-malha" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><path className="mp-malha" d="M0 0H16M0 0V16" /></pattern></defs>
      <g className="mp-desenho" aria-hidden="true">
        <path className="mp-silhueta" d={SILHUETA} /><path className="mp-silhueta" d={CEREBELO} />
        <g className="mp-divisas">{DIVISAS.map(p => <path key={p} d={p} />)}</g>
      </g>
      <g aria-hidden="true">
        {REGIOES.map(([lobo, nome, x]) => <text key={lobo} className="mp-reg" data-lobo={lobo} x={x} y={Y_REGIOES} textAnchor="middle">{nome}</text>)}
        {mapa.receptores.length > 0 && <text className="mp-sub" x={SUB_CORPO.x} y={SUB_CORPO.y} textAnchor="middle">receptores do corpo</text>}
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
          const [x, y] = pe.get(e)!, lit = top.has(e);
          return <g key={e} className={"mp-no" + (i >= ENTRADAS_LOBOS.length ? " mp-corpo" : "") + (lit ? " mp-lit" : "")} data-entrada={e}>
            <circle cx={f(x)} cy={f(y)} r={f(R * (lit ? 7 : 5))} /><text x={f(x + 12 * R)} y={f(y + 5 * R)}>{txt(TXT_ENTRADA, e, "entrada")}</text></g>;
        })}
        {REGRAS_LOBOS.map(r => {
          const [x, y] = pr.get(r)!, lit = ac !== null && r === ac.regra;
          return <g key={r} className={"mp-no" + (lit ? " mp-lit" : "")} data-regra={r}>
            <circle cx={f(x)} cy={f(y)} r={f(R * (lit ? 9 : 6.5))} />
            {/* a 390 o rotulo da regra vai para a direita do ponto: em cima bate no da acao ao lado, embaixo no ponto da regra seguinte */}
            {movel ? <text x={f(x + 14 * R)} y={f(y + 5 * R)} textAnchor="start">{TXT_REGRA[r]}</text>
              : <text x={f(x)} y={f(y - 14 * R)} textAnchor="middle">{TXT_REGRA[r]}</text>}</g>;
        })}
        {ACOES_LOBOS.map(a => {
          const [x, y] = pa.get(a)!, c = chance.get(a), esc = ac !== null && a === ac.acao;
          const pc = c === undefined ? null : Math.round(c * 100) + "%";
          /* a 390 o rotulo vai para dentro (a direita do ponto), senao sai da moldura; no desktop a chance fica numa linha embaixo */
          return <g key={a} className={"mp-no" + (c !== undefined ? " mp-cand" : "") + (esc ? " mp-esc" : "")} data-acao={a}>
            <circle cx={f(x)} cy={f(y)} r={f(R * (esc ? 10 : c !== undefined ? 8 : 6.5))} />
            <text x={f(movel ? x + 14 * R : x - 14)} y={f(y + 5 * R)} textAnchor={movel ? "start" : "end"}>{TXT_ACAO[a]}{pc !== null && movel && <tspan className="mp-pct"> {pc}</tspan>}</text>
            {pc !== null && !movel && <text className="mp-pct" x={f(x - 14)} y={f(y + 22)} textAnchor="end">{pc}</text>}</g>;
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
function useEscalaDoMapa(ref: { current: HTMLElement | null }, ativo: boolean): void {
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
function SeloForma({ replay }: { replay: boolean }) {
  const estado = useEstadoSelo(replay);
  return <span className={"db-selo db-selo--" + estado} role="img" aria-label={SELO_TXT[estado]} title={SELO_TXT[estado]}><i aria-hidden="true" /></span>;
}

/** a dica do "i" (D1b-7): a forma e so desenho, e a legenda curta que saiu do rodape */
function Dica({ receptores, aberta }: { receptores: boolean; aberta: boolean }) {
  return (
    <div className="scan-dica scan-cx" id="db-dica" hidden={!aberta}>
      <p>A forma de cérebro é só desenho. Cada ponto é o que o pet sente, uma regra ou uma ação; cada fio é um peso.</p>
      <p className="scan-dica-selo">Ao lado do título: o ponto é ao vivo, as duas barras são pausado e o triângulo é um replay.</p>
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
          <h2 className="scan-tit" id="db-titulo">DigiBrain</h2>
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
          <div className="scan-moldura">
            {verTexto
              ? <section className="scan-texto db-texto" id="db-texto" aria-label="O mapa em texto" tabIndex={0}><MapaEmTexto mapa={mapa} d={d} /></section>
              : <>
                {mov !== null && <div className="scan-varre-trilho" key={"varre" + mov} aria-hidden="true"><div className="scan-varredura" /></div>}
                <div className="scan-giro" ref={giro}><MapaScan mapa={mapa} decisao={d} movel={movel} movendo={mov !== null} /></div>
              </>}
          </div>
        )}
      </div>
      {/* o cartao do chamado do pet (D1-10) fica fora da caixa, no alto ao centro da tela, como na tela Pet; depois da caixa no DOM, para o foco
          nao cair num botao do chamado ao abrir (rev-a11y da D1b) */}
      {chamado}
    </dialog>
  );
}
