/* O painel DigiBrain como "scan holografico" (D1 da UX_TELA_PET; prancha aprovada em docs/pranchas/ux-digibrain/, direcao A; decisoes D1-1 a
   D1-11 de docs/PROPOSTAS_V3_UX_TELA_PET.md). Um <dialog> modal em tela cheia (foco preso, Esc fecha, o foco volta a quem abriu) com tres
   colunas no desktop e uma folha que rola no celular. So le o motor por useJogo(): todo numero sai de Motor.digibrain() (mapa, decisao,
   aprendido), do historico e da memoria das emocoes; nenhum mudarMotor aqui. Cada ponto do desenho e um no do motor (entrada, regra ou
   acao) e cada fio e uma aresta de mapa.arestas; a forma de cerebro e as regioes sao so desenho, e a tela diz isso.
   O movimento e so vista e so numa decisao nova (mapa.acesas.n muda): a varredura passa uma vez e o pulso percorre as arestas acesas;
   os dois terminam. O giro lento do plano (so no desktop) e CSS puro. Com "reduzir movimento" nada se move; no replay e com o tempo
   pausado so o destaque troca. O relogio do navegador aqui e so animacao: nada do que e gravado depende dele. */
import { memo, useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore, type CSSProperties, type ReactNode } from "react";
import { List, X } from "lucide-react";
import { ACOES_LOBOS, ENTRADAS_LOBOS, NOME_PET, REGRAS_LOBOS, type AcaoPet, type LeituraDecisao, type MapaDecisao, type RegraLobos } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { hhmm } from "../telas/pet/TelaPet.tsx";
import "../estilo/scan_digibrain.css";
import {
  ACAO_CURTA, ACAO_INF, COM_SINAL, ENTRADA_TXT, LOBO_TXT, REGRA_TXT, SeloDigiBrain, SeloEmocao, num, pct, useEstadoSelo,
} from "./DigiBrain.tsx";
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

/* ---------------------------------------------------------------- a geometria do desenho (unidades do viewBox 1000 x 620; so desenho)
   PROPOSTO, SEM FONTE (D1-11): a frente do cerebro fica a esquerda. Percepcao atras (um arco: as entradas na ordem do motor e os receptores do
   corpo no fim, embaixo), impulsos no meio (as regras de cima para baixo, na ordem em que o instinto as testa), decisao na frente (as acoes na
   ordem de ACOES_LOBOS). Memoria e emocao e a regiao de baixo, sem nenhum ponto: o lobo nao tem pesos. */
const VB = "0 0 1000 620";
const SILHUETA = "M120 330C100 210 220 80 420 62C600 45 820 90 890 220C935 300 900 390 820 420C760 440 700 430 650 445C600 470 540 500 470 488C380 475 330 430 250 430C170 430 130 390 120 330Z";
const CEREBELO = "M650 445C655 505 760 535 825 505C865 485 860 440 820 420C760 440 700 430 650 445Z";
const DIVISAS = ["M380 66C360 180 372 300 345 410", "M612 54C592 170 602 300 592 420", "M300 432C360 392 540 388 640 446"];
/** as regioes: o lobo (o mesmo id de lobo_decisivo e do data-lobo), o rotulo e onde ele fica. Os "receptores do corpo" ficam centrados sob o cerebelo */
const REGIOES: [string, string, number, number][] = [
  ["decisao", "decisão", 250, 34], ["impulsos", "impulsos", 490, 30], ["percepcao", "percepção", 760, 40], ["memoria_emocao", "memória e emoção · sem pesos", 460, 526],
];
const SUB_CORPO = { x: 757, y: 566 };
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

/** o rotulo de uma regiao; a que pesou mais ganha "pesou mais" e uma caixa medida depois das fontes (a prancha mede o getBBox do texto) */
function Regiao({ lobo, nome, x, y, dest, movel }: { lobo: string; nome: string; x: number; y: number; dest: boolean; movel: boolean }) {
  const ref = useRef<SVGTextElement>(null);
  const [caixa, setCaixa] = useState<{ x: number; y: number; w: number; h: number } | null>(null);
  useLayoutEffect(() => {
    if (!dest) { setCaixa(null); return; }
    let vivo = true;
    const medir = () => {
      const t = ref.current;
      if (!vivo || !t || typeof t.getBBox !== "function") return;
      const b = t.getBBox(), m = movel ? 10 : 6;
      setCaixa({ x: f(b.x - m), y: f(b.y - m / 2), w: f(b.width + 2 * m), h: f(b.height + m) });
    };
    medir();
    void document.fonts?.ready.then(medir);
    return () => { vivo = false; };
  }, [dest, nome, movel]);
  return (
    <g className={"mp-reg mp-reg--" + lobo + (dest ? " mp-dest" : "")} data-lobo={lobo}>
      {dest && caixa && <rect className="mp-dest-caixa" x={caixa.x} y={caixa.y} width={caixa.w} height={caixa.h} />}
      <text ref={ref} x={x} y={y} textAnchor="middle">{nome}{dest && <tspan className="mp-mais-peso"> · pesou mais</tspan>}</text>
    </g>
  );
}

/** o mapa dos pesos em SVG (D1-1). As classes que o e2e le: svg.mp com data-n, .mp-pesos path, .mp-acesas path, .mp-lit, .mp-cand, .mp-esc, .mp-pct,
    .mp-dest[data-lobo]. `movendo`: o pulso (um ponto que percorre cada aresta acesa) esta no DOM; o pai o tira quando termina */
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
  const dest = ac ? ac.lobo_decisivo : null;
  /* a espessura de hoje (MapaPesos.tsx) vezes a escala do desenho; os raios idem */
  const K = movel ? 2.6 : 1.1, R = movel ? 2 : 1;
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
      {REGIOES.map(([lobo, nome, x, y]) => <Regiao key={lobo} lobo={lobo} nome={nome} x={x} y={y} dest={dest === lobo} movel={movel} />)}
      {mapa.receptores.length > 0 && <text className="mp-sub" x={SUB_CORPO.x} y={SUB_CORPO.y} textAnchor="middle">receptores do corpo</text>}
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
            <circle cx={f(x)} cy={f(y)} r={f(R * (lit ? 9 : 6.5))} /><text x={f(x)} y={f(y - 14 * R)} textAnchor="middle">{TXT_REGRA[r]}</text></g>;
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

/** o scan cobre a ilha: a cena 3D desenha mais devagar enquanto ele esta aberto (CENA.coberto, o mesmo sinal do veu dos outros paineis).
    Devolve a limpeza, que volta o valor a false */
export function cobrirCena(): () => void {
  CENA.coberto = true;
  return () => { CENA.coberto = false; };
}
/** a escala do desenho (a largura renderizada sobre a do viewBox, a menor das duas por causa do "meet") numa variavel CSS: o CSS pede o texto
    do mapa com pelo menos 11 px na tela, max(base, 11px / escala), em unidades do viewBox. So vista */
const VB_L = 1000, VB_A = 620, TEXTO_MIN_PX = 11;
function useEscalaDoMapa(ref: { current: HTMLElement | null }, ativo: boolean): void {
  useEffect(() => {
    const el = ref.current; if (!el || !ativo || typeof ResizeObserver !== "function") return;
    const medir = () => { const w = el.clientWidth, h = el.clientHeight; if (w > 0 && h > 0) el.style.setProperty("--scan-esc", String(Math.min(w / VB_L, h / VB_A))); el.style.setProperty("--scan-txt-min", TEXTO_MIN_PX + "px"); };
    medir();
    const ro = new ResizeObserver(medir); ro.observe(el);
    return () => ro.disconnect();
  }, [ref, ativo]);
}

/* ---------------------------------------------------------------- a tela */
export function ScanDigiBrain({ fechar, movel, replay = false, chamado }: { fechar: () => void; movel: boolean; replay?: boolean; chamado?: ReactNode }) {
  const { motor: m } = useJogo(), db = m.digibrain();
  const ref = useRef<HTMLDialogElement>(null), saindo = useRef(false), texto = useRef<HTMLElement>(null);
  const giro = useRef<HTMLDivElement>(null), [verTexto, setVerTexto] = useState(false);
  useEffect(cobrirCena, []);
  useEscalaDoMapa(giro, db !== null);
  const selo = useEstadoSelo(replay), reduzir = useReduzirMovimento();
  const mov = useDecisaoNova(db?.mapa.acesas ? db.mapa.acesas.n : null, selo === "vivo" && !reduzir);
  /* o modal: showModal prende o foco e deixa o resto inerte; o Esc dispara o close nativo; ao fechar, o foco volta a quem abriu (modal.ts) */
  useEffect(() => {
    const dlg = ref.current; if (!dlg) return;
    saindo.current = false;
    abrirModal(dlg);
    return () => { saindo.current = true; if (dlg.open) dlg.close(); };
  }, []);
  useEffect(() => { if (verTexto && movel) texto.current?.scrollIntoView({ block: "nearest" }); }, [verTexto, movel]);

  const raiz = (corpo: ReactNode) => (
    <dialog className="scan" id="pet-painel" data-painel-pet="digibrain" aria-labelledby="db-titulo" ref={ref}
      style={{ "--scan-giro-graus": GIRO_GRAUS + "deg", "--scan-giro-ciclo": GIRO_CICLO_S + "s" } as CSSProperties}
      onClose={() => { if (!saindo.current) fechar(); }}>
      <div className="scan-in digibrain">
      <header className="scan-topo">
        <h2 className="scan-tit" id="db-titulo">DigiBrain <small>mapa dos pesos</small></h2>
        <SeloDigiBrain replay={replay} />
        <button type="button" className="hx-btn scan-fechar" aria-label="Fechar DigiBrain" onClick={() => ref.current?.close()}>
          <X aria-hidden="true" /><kbd aria-hidden="true">Esc</kbd></button>
      </header>
      {chamado}
      {corpo}
      </div>
    </dialog>
  );
  if (db === null) return raiz(<div className="scan-corpo scan-corpo--vazio"><p className="scan-vazio">Este pet não tem mapa dos pesos.</p></div>);

  const d = db.decisao, mapa = db.mapa, ac = mapa.acesas;
  if ((d === null) !== (ac === null)) throw new Error("a decisao e as arestas acesas fora de par");
  const aprendido = d !== null && d.quem_decidiu.mudou;
  const nPontos = ENTRADAS_LOBOS.length + mapa.receptores.length + REGRAS_LOBOS.length + ACOES_LOBOS.length;
  const ultimas = m.historico.filter(h => h.quem === "pet").slice(-5).reverse();

  const agora = (
    <section className={"scan-cx scan-lad scan-agora sec-agora" + (aprendido ? " scan-agora--aprendido" : "")} aria-labelledby="db-agora">
      <h3 className="scan-sec" id="db-agora">Agora</h3>
      {aprendido && <span className="scan-tag-aprendido">aprendido</span>}
      {d ? <>
        <b>{txt(REGRA_TXT, d.regra, "regra")}: decidiu {txt(ACAO_INF, d.acao, "ação")}</b>
        <small>{!d.quem_decidiu.escolha ? "Nesta situação só havia uma opção."
          : d.quem_decidiu.mudou ? `Sem o aprendido, teria decidido ${txt(ACAO_INF, d.quem_decidiu.acao_instinto, "ação")}.`
            : "O instinto sozinho faria o mesmo."}</small></> : <small>Ainda não decidiu nada.</small>}
    </section>
  );
  const lobos = d && (
    <section className="scan-cx scan-lad sec-lobos" aria-labelledby="db-lobos">
      <h3 className="scan-sec" id="db-lobos">O peso de cada lobo nesta escolha</h3>
      <ul className="db-barras">
        {LOBO_TXT.filter(([l]) => l !== "piso" || d.barras.piso !== 0).map(([l, nome]) => {
          const v = d.barras[l];
          if (typeof v !== "number") throw new Error(`barras.${l} ausente`);
          /* o eixo no zero (D1-5): o positivo a direita, o negativo a esquerda, o cheio de um lado e 100% */
          return <li key={l} data-lobo={l}><span>{nome}</span>
            <span className="scan-trilho scan-trilho--sinal"><b className={v < 0 ? "neg" : ""} style={{ width: Math.min(50, Math.abs(v) * 50) + "%" }} /></span>
            <em>{pct(v, l === "impulsos" ? 0 : 1, COM_SINAL.has(l))}</em></li>;
        })}
      </ul>
      <SeloEmocao />
    </section>
  );
  const perc = d && (
    <section className="scan-cx scan-lad sec-perc" aria-labelledby="db-perc">
      <h3 className="scan-sec" id="db-perc">O que mais pesou</h3>
      {d.percepcao.length ? <ul className="scan-chips">{d.percepcao.map(p => <li key={p.entrada}>
        {ENTRADA_TXT[p.entrada] ?? p.entrada} {p.entrada === "dormindo" ? (p.x ? "sim" : "não") : pct(p.x, 0, false)}{" "}
        <span className={p.termo > 0 ? "scan-favor" : "scan-contra"}>{p.termo > 0 ? "a favor" : "contra"}</span></li>)}</ul>
        : <p className="scan-vazio">Nada do que ele lê pesou nesta regra.</p>}
    </section>
  );
  const opc = d && (
    <section className="scan-cx scan-lad sec-opc" aria-labelledby="db-opc">
      <h3 className="scan-sec" id="db-opc">As opções e a chance de cada uma</h3>
      <ul className="db-opcoes">{d.chances.map(c => <li key={c.acao} className={c.acao === d.acao ? "esc" : ""}>
        <span>{txt(ACAO_CURTA, c.acao, "ação")}{c.acao === d.acao && <small> · escolhida</small>}</span>
        <span className="scan-trilho"><b style={{ width: c.chance * 100 + "%" }} /></span><em>{pct(c.chance, 0, false)}</em></li>)}</ul>
    </section>
  );
  const apr = (
    <section className="scan-cx scan-lad sec-apr" aria-labelledby="db-apr">
      <h3 className="scan-sec" id="db-apr">O que aprendeu desde que nasceu</h3>
      {db.aprendido.length ? <ul className="scan-aprendeu">{db.aprendido.map(a => <li key={a.acao}>
        <span>{a.desvio > 0 ? "mais" : "menos"} {txt(ACAO_CURTA, a.acao, "ação")} do que o instinto</span><em>{num(a.desvio)}</em></li>)}</ul>
        : <p className="scan-vazio">Ainda igual ao instinto.</p>}
    </section>
  );
  const ult = (
    <section className="scan-cx scan-lad sec-ult" aria-labelledby="db-ult">
      <h3 className="scan-sec" id="db-ult">Últimas ações</h3>
      {ultimas.length ? <ol className="db-ultimas">{ultimas.map((h, i) => <li key={i}><span className="scan-hora">{hhmm(h.t)}</span>{NOME_PET[h.a as AcaoPet] ?? h.a}</li>)}</ol>
        : <p className="scan-vazio">Nenhuma ação ainda.</p>}
    </section>
  );
  const legenda = (
    <ul className="mp-leg">
      <li><span className="scan-leg scan-leg--prior" />instinto</li><li><span className="scan-leg scan-leg--mais" />aprendeu a mais</li>
      <li><span className="scan-leg scan-leg--menos" />aprendeu a menos</li><li><span className="scan-leg scan-leg--aceso" />esta decisão</li>
      <li><span className="scan-leg scan-leg--neg" />peso negativo</li>{mapa.receptores.length > 0 && <li><span className="scan-leg scan-leg--corpo" />receptor do corpo</li>}
    </ul>
  );
  const centro = (
    <section className="scan-centro" aria-labelledby="db-mapa">
      <div className="scan-moldura" style={{ "--scan-t-varre": VARREDURA_MS + "ms", "--scan-t-pulso": PULSO_MS + "ms" } as CSSProperties}>
        <h3 className="scan-moldura-tit" id="db-mapa">Mapa dos pesos <small>{nPontos} pontos · {mapa.arestas.length} pesos</small></h3>
        {mov !== null && <div className="scan-varre-trilho" key={"varre" + mov} aria-hidden="true"><div className="scan-varredura" /></div>}
        <div className="scan-mapa-caixa"><div className="scan-giro" ref={giro}><MapaScan mapa={mapa} decisao={d} movel={movel} movendo={mov !== null} /></div></div>
      </div>
      <div className="scan-rodape-mapa">
        {legenda}
        <p className="mp-nota">Cada ponto é uma entrada, uma regra ou uma ação do pet; cada fio é um peso, da entrada à ação, passando pela regra. A espessura é o tamanho do peso. A forma de cérebro e as regiões são só o desenho.</p>
        <button type="button" className="hx-btn scan-texto-bt" aria-expanded={verTexto} aria-controls="db-texto" onClick={() => setVerTexto(v => !v)}>
          <List aria-hidden="true" />O mapa em texto</button>
      </div>
      <section className="scan-cx scan-texto db-texto" id="db-texto" aria-labelledby="db-texto-tit" hidden={!verTexto} ref={texto}>
        <h3 className="scan-sec" id="db-texto-tit">O mapa em texto</h3><MapaEmTexto mapa={mapa} d={d} />
      </section>
    </section>
  );
  return raiz(
    <div className="scan-corpo">{/* a ordem do DOM e a do celular; o desktop se arruma por grid-area (scan_digibrain.css) */}
      {agora}{centro}{lobos}{perc}{opc}{apr}{ult}
    </div>,
  );
}
