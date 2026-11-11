/* O DigiBrain do modular no scan (o mesmo modal pequeno do A v11, ScanDigiBrain.tsx, D1b e D1c da UX_TELA_PET), pedido pelo Matheus em 2026-11-11:
   o pet do laboratorio (v16) abria o painel antigo (DigiBrainLab.tsx), e o visual novo tem de valer para ele tambem. A casca e a mesma: o
   <dialog> pequeno sob o relogio (a folha baixa no celular), o titulo so com o icone, o selo, o "i", o mapa em texto, o fechar, a varredura e o
   pulso so numa decisao nova. O desenho troca de conteudo, porque o modular nao tem as regras e as entradas do A:
     - atras (a percepcao): os 7 modulos do motivo (ORDEM_TERMOS), na ordem do motor;
     - no meio: a soma dos modulos na unidade escolhida (um ponto so);
     - na frente: as opcoes com chance (Motor.leituraLab().chances), com a chance de cada uma.
   Os fios sao as barras de hoje (a parte de cada modulo no peso da unidade escolhida, em permil): a espessura e o modulo, o tracejado e o que
   puxou contra. So os modulos que contribuiram tem fio; as outras opcoes nao tem, porque a leitura so traz as barras da escolhida.
   So le o motor por useJogo(): todo numero sai de Motor.leituraLab(); nenhum mudarMotor aqui. O "mapa em texto" e o painel de antes inteiro
   (ConteudoDigiBrainLab), com a intencao, as sondas, os conceitos e as ultimas acoes. */
import { memo, useEffect, useRef, useState, type CSSProperties, type MouseEvent, type ReactNode, type SyntheticEvent } from "react";
import { Brain, Info, List, X } from "lucide-react";
import { ORDEM_TERMOS, type LeituraLab, type TermoLab } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import "../estilo/scan_digibrain.css";
import { ConteudoDigiBrainLab, NOME_TERMO, rotuloUnidade, textoResultado } from "./DigiBrainLab.tsx";
import { resultadoAnterior } from "../../motor/index.ts";
import { abrirModal } from "./modal.ts";
import {
  CEREBELO, DIVISAS, GIRO_CICLO_S, GIRO_GRAUS, PULSO_MS, SILHUETA, SeloForma, VARREDURA_MS, VB, Y_REGIOES, useDecisaoNova, useEscalaDoMapa,
  useReduzirMovimento,
} from "./ScanDigiBrain.tsx";
import { useEstadoSelo } from "./DigiBrain.tsx";

/** quantas opcoes o desenho mostra (as de maior chance; a escolhida sempre entra); as outras ficam no mapa em texto. PROPOSTO, SEM FONTE */
export const OPCOES_NO_DESENHO = 7;
/** o centro do meio (a soma dos modulos) e as regioes, nas unidades do viewBox do scan. So desenho */
const MEIO: [number, number] = [480, 300];
const REGIOES_LAB: [string, string, number][] = [["decisao", "opções", 250], ["impulsos", "soma", 490], ["percepcao", "módulos", 760]];
const f = (v: number): number => Math.round(v * 10) / 10;
type Ponto = [number, number];

/** as opcoes desenhadas: a escolhida e as de maior chance, ate OPCOES_NO_DESENHO, na ordem da leitura */
export function opcoesDoDesenho(l: LeituraLab): LeituraLab["chances"] {
  if (l.chances.length <= OPCOES_NO_DESENHO) return l.chances;
  const ord = [...l.chances].sort((a, b) => (b.escolhida ? 1 : 0) - (a.escolhida ? 1 : 0) || (b.permil ?? 1000) - (a.permil ?? 1000)).slice(0, OPCOES_NO_DESENHO);
  return l.chances.filter(c => ord.includes(c));
}

function posicoesLab(n: number) {
  const pm = new Map<TermoLab, Ponto>(ORDEM_TERMOS.map((t, i) => {
    const a = (-70 + 140 * i / (ORDEM_TERMOS.length - 1)) * Math.PI / 180;
    return [t, [650 + 200 * Math.cos(a), 290 + 190 * Math.sin(a)] as Ponto];
  }));
  const po: Ponto[] = Array.from({ length: n }, (_, i) => {
    const s = n === 1 ? 0.5 : i / (n - 1);
    return [285 - 85 * Math.sin(Math.PI * s), 130 + 330 * s] as Ponto;
  });
  return { pm, po };
}

/** o mapa do modular em SVG: as classes sao as do scan (svg.mp com data-n, .mp-acesas path, .mp-esc, .mp-cand, .mp-pct, .mp-lit, .mp-reg) */
function MapaLabBruto({ l, movel, movendo }: { l: LeituraLab; movel: boolean; movendo: boolean }) {
  const [tocado, setTocado] = useState<string | null>(null);
  const tocar = (id: string) => () => setTocado(t => t === id ? null : id);
  const cls = (id: string, base: string): string => base + (tocado === id ? " mp-toque" : "");
  const ops = opcoesDoDesenho(l), { pm, po } = posicoesLab(ops.length);
  const iEsc = ops.findIndex(c => c.escolhida);
  if (iEsc < 0) throw new Error("a leitura do modular sem a opcao escolhida");
  const esc = po[iEsc]!;
  const curva = (t: TermoLab): string => {
    const [x1, y1] = pm.get(t) ?? (() => { throw new Error(`modulo fora do mapa: ${t}`); })(), [x2, y2] = MEIO, [x3, y3] = esc;
    return `M${f(x1)} ${f(y1)}C${f(x1 - 110)} ${f(y1)} ${f(x2 + 90)} ${f(y2)} ${f(x2)} ${f(y2)}C${f(x2 - 90)} ${f(y2)} ${f(x3 + 90)} ${f(y3)} ${f(x3)} ${f(y3)}`;
  };
  const maior = Math.max(1, ...l.barras.map(b => Math.abs(b.permil)));
  const K = movel ? 2.2 : 1.1, R = movel ? 1.8 : 1;
  const tracejado = (neg: boolean): CSSProperties | undefined => neg ? { strokeDasharray: `${f(6 * K)} ${f(4 * K)}` } : undefined;
  const escolhida = ops[iEsc]!;
  const rotulo = `Mapa do cérebro modular. Nesta decisão escolheu ${rotuloUnidade(escolhida.chave)}${escolhida.permil === null ? ", opção única" : ` com ${Math.round(escolhida.permil / 10)}% de chance`}; ${l.barras.length} módulos contribuíram.`;
  return (
    <svg className="mp mp--lab" viewBox={VB} preserveAspectRatio="xMidYMid meet" role="img" aria-label={rotulo} data-n={l.k}>
      <g className="mp-desenho" aria-hidden="true">
        <path className="mp-silhueta" d={SILHUETA} /><path className="mp-silhueta" d={CEREBELO} />
        <g className="mp-divisas">{DIVISAS.map(p => <path key={p} d={p} />)}</g>
      </g>
      <g aria-hidden="true">
        {REGIOES_LAB.map(([lobo, nome, x]) => <text key={lobo} className="mp-reg" data-lobo={lobo} x={x} y={Y_REGIOES} textAnchor="middle">{nome}</text>)}
      </g>
      <g className="mp-acesas">
        {l.barras.map(b => <path key={b.termo} data-termo={b.termo} className={b.permil < 0 ? "mp-neg" : undefined} d={curva(b.termo)}
          strokeWidth={f(K * (0.6 + 3 * Math.abs(b.permil) / maior))} strokeOpacity={f(0.35 + 0.65 * Math.abs(b.permil) / maior)} style={tracejado(b.permil < 0)} />)}
      </g>
      {movendo && <g className="mp-pulso" aria-hidden="true">
        {l.barras.map(b => <path key={b.termo} pathLength={1} d={curva(b.termo)} strokeWidth={f(7 * R)} />)}
      </g>}
      <g className="mp-nos">
        {ORDEM_TERMOS.map(t => {
          const [x, y] = pm.get(t)!, b = l.barras.find(z => z.termo === t), lit = b !== undefined;
          return <g key={t} className={cls("t" + t, "mp-no" + (lit ? " mp-lit mp-caminho" : ""))} data-termo={t} onClick={tocar("t" + t)}>
            <circle className="mp-alvo" cx={f(x)} cy={f(y)} r={f(R * (movel ? 16 : 12))} />
            <circle cx={f(x)} cy={f(y)} r={f(R * (lit ? 7 : 5))} />
            <text x={f(x + 12 * R)} y={f(y + 5 * R)}>{NOME_TERMO[t]}{b && <tspan className="mp-pct"> {(b.permil > 0 ? "+" : "") + String(Math.round(b.permil / 10)).replace("-", "−")}%</tspan>}</text></g>;
        })}
        <g className={cls("meio", "mp-no mp-lit")} data-meio="soma" onClick={tocar("meio")}>
          <circle className="mp-alvo" cx={MEIO[0]} cy={MEIO[1]} r={f(R * 14)} />
          <circle cx={MEIO[0]} cy={MEIO[1]} r={f(R * 9)} />
          <text x={MEIO[0]} y={f(MEIO[1] - 14 * R)} textAnchor="middle">{l.reflexo ? "reflexo do sono" : "a soma"}</text></g>
        {ops.map((c, i) => {
          const [x, y] = po[i]!, e = c.escolhida, pc = c.permil === null ? "única" : Math.round(c.permil / 10) + "%";
          const id = "o" + i;
          return <g key={JSON.stringify(c.chave)} className={cls(id, "mp-no mp-cand" + (e ? " mp-esc" : ""))} data-opcao={i} onClick={tocar(id)}>
            <circle className="mp-alvo" cx={f(x)} cy={f(y)} r={f(R * 14)} />
            <circle cx={f(x)} cy={f(y)} r={f(R * (e ? 10 : 8))} />
            <text x={f(movel ? x + 14 * R : x - 14)} y={f(y + 5 * R)} textAnchor={movel ? "start" : "end"}>{rotuloUnidade(c.chave)}{movel && <tspan className="mp-pct"> {pc}</tspan>}</text>
            {!movel && <text className="mp-pct" x={f(x - 14)} y={f(y + 30)} textAnchor="end">{pc}</text>}</g>;
        })}
      </g>
    </svg>
  );
}
const assinaturaLab = (l: LeituraLab): string => l.k + "|" + l.barras.map(b => b.termo + b.permil).join() + "|" + l.chances.map(c => c.permil).join();
export const MapaLab = memo(MapaLabBruto, (a, b) => a.movel === b.movel && a.movendo === b.movendo && assinaturaLab(a.l) === assinaturaLab(b.l));

function DicaLab({ aberta }: { aberta: boolean }) {
  return (
    <div className="scan-dica scan-cx" id="db-dica" hidden={!aberta}>
      <p>A forma de cérebro é só desenho. Atrás ficam os módulos do cérebro modular, no meio a soma deles e na frente as opções, com a chance de cada uma.</p>
      <p className="scan-dica-selo">Cada fio é a parte de um módulo no peso da escolha; tracejado, o módulo puxou contra. Ao lado do título: o ponto é ao vivo, as duas barras são pausado e o triângulo é um replay.</p>
      <p className="scan-dica-selo">O mapa em texto tem o resto: a lembrança, a intenção, o que mudaria a escolha e os conceitos.</p>
      <ul className="mp-leg">
        <li><span className="scan-leg scan-leg--aceso" />esta decisão</li><li><span className="scan-leg scan-leg--neg" />puxou contra</li>
      </ul>
    </div>
  );
}

export function ScanDigiBrainLab({ fechar, movel, replay = false, chamado }: { fechar: () => void; movel: boolean; replay?: boolean; chamado?: ReactNode }) {
  const { motor: m } = useJogo();
  if (!m.lab) throw new Error("o scan do modular so abre no pet do laboratorio (v16)");
  const l = m.leituraLab(), res = resultadoAnterior(m.lab);
  const ref = useRef<HTMLDialogElement>(null), saindo = useRef(false);
  const giro = useRef<HTMLDivElement>(null), [verTexto, setVerTexto] = useState(false), [verDica, setVerDica] = useState(false);
  useEscalaDoMapa(giro, l !== null && !verTexto);
  const selo = useEstadoSelo(replay), reduzir = useReduzirMovimento();
  const mov = useDecisaoNova(l ? l.k : null, selo === "vivo" && !reduzir);
  useEffect(() => {
    const dlg = ref.current; if (!dlg) return;
    saindo.current = false;
    abrirModal(dlg);
    return () => { saindo.current = true; if (dlg.open) dlg.close(); };
  }, []);
  const cancelar = (e: SyntheticEvent<HTMLDialogElement>) => { if (verDica) { e.preventDefault(); setVerDica(false); } };
  const cliqueFora = (e: MouseEvent<HTMLDialogElement>) => { if (e.target === e.currentTarget) ref.current?.close(); };
  return (
    <dialog className={"scan scan--lab" + (movel ? " scan--folha" : "")} id="pet-painel" data-painel-pet="digibrain" aria-labelledby="db-titulo" ref={ref}
      style={{ "--scan-giro-graus": GIRO_GRAUS + "deg", "--scan-giro-ciclo": GIRO_CICLO_S + "s", "--scan-t-varre": VARREDURA_MS + "ms", "--scan-t-pulso": PULSO_MS + "ms" } as CSSProperties}
      onCancel={cancelar} onClick={cliqueFora} onClose={() => { if (!saindo.current) fechar(); }}>
      <div className="scan-in scan-cx digibrain">
        {movel && <span className="scan-alca" aria-hidden="true" />}
        <header className="scan-topo">
          <h2 className="scan-tit" id="db-titulo"><Brain aria-hidden="true" /><span className="sr-only">DigiBrain, cérebro modular</span></h2>
          <SeloForma replay={replay} />
          <button type="button" className="scan-ic scan-info" aria-label="O que é este desenho" aria-expanded={verDica} aria-controls="db-dica"
            onClick={() => setVerDica(v => !v)}><Info aria-hidden="true" /></button>
          <button type="button" className="scan-ic scan-texto-bt" aria-label="O mapa em texto" aria-pressed={verTexto}
            onClick={() => setVerTexto(v => !v)}><List aria-hidden="true" /></button>
          <button type="button" className="scan-ic scan-fechar" aria-label="Fechar DigiBrain" title="Fechar (Esc)" data-autofocus onClick={() => ref.current?.close()}>
            <X aria-hidden="true" /></button>
        </header>
        <DicaLab aberta={verDica} />
        <div className="scan-moldura">
          {verTexto || l === null
            ? <section className="scan-texto db-texto dl digibrain pet-painel__folha" id="db-texto" aria-label="O mapa em texto" tabIndex={0}><ConteudoDigiBrainLab /></section>
            : <>
              {mov !== null && <div className="scan-varre-trilho" key={"varre" + mov} aria-hidden="true"><div className="scan-varredura" /></div>}
              <div className="scan-giro" ref={giro}><MapaLab l={l} movel={movel} movendo={mov !== null} /></div>
            </>}
        </div>
        {/* o resultado da decisao anterior numa linha (CADEIA, etapa 3): o que ele fez e o que mudou nele */}
        {res && !verTexto && <p className="scan-resultado" data-testid="resultado-anterior" data-k={res.k}>{textoResultado(res)}</p>}
      </div>
      {chamado}
    </dialog>
  );
}
