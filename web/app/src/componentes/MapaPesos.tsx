/* O mapa dos pesos do painel DigiBrain (pets v11; pranchas DigiBrainDesktop e DigiBrain390): o desenho do connectome do #321
   (docs/futuro/connectome_cerebro_a.md, secao 2) em colunas fixas, geradas da estrutura do cerebro A. Cada traco e um peso
   w[regra][acao][entrada], da entrada a acao passando pela regra (CN-2), com a espessura sqrt(|w| / S) (CN-3) e a cor do aprendido
   (w - w0) / teto. A cada decisao acendem a regra que disparou, os candidatos com a chance, as entradas que mais pesaram e os termos da
   acao escolhida; o lobo que pesou mais fica destacado. Os numeros sao todos do motor (Motor.digibrain: mapaPesos e mapaDecisao, com
   paridade com o Python); a tela so posiciona. Sem animacao nem transicao: entre duas decisoes o mapa fica parado. */
import { ACOES_LOBOS, ENTRADAS_LOBOS, REGRAS_LOBOS, type AcaoPet, type ArestaMapa, type LeituraDecisao, type MapaDecisao, type RegraLobos } from "../../motor/index.ts";

const TXT_ENTRADA: Record<string, string> = {
  vies: "viés", fome: "comida", higiene: "higiene", energia: "energia", humor: "humor", saude: "saúde", sujeira: "sujeira",
  dormindo: "dormindo", hora: "hora", ticks_sem_cuidado: "sem cuidado", tedio: "tédio", curiosidade: "curiosidade", solidao: "solidão",
  estresse: "estresse", dor: "dor", susto: "susto", vontade: "vontade", conforto: "conforto",
};
const TXT_REGRA: Record<RegraLobos, string> = {
  sono_exaustao: "exausto", sono_continuar: "sono", sono_noite: "noite", pedido_necessidade: "precisando", abandono: "sem cuidado",
  fome_moderada: "fome", tempo_livre: "tempo livre",
};
const TXT_ACAO: Record<AcaoPet, string> = {
  ocioso: "à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
};

/** a geometria (unidades do viewBox): as tres colunas, a faixa vertical dos nos e a caixa da memoria e emocao embaixo */
const W = 284, XE = 72, XR = 142, XA = 204, Y0 = 36, SPAN = 192, YB = Y0 + SPAN + 20, YM = YB + 8, H = YM + 22;
const f = (v: number): number => Math.round(v * 10) / 10;

export interface DadosMapa { receptores: readonly string[]; arestas: ArestaMapa[]; acesas: MapaDecisao | null }

export function MapaPesos({ mapa, decisao }: { mapa: DadosMapa; decisao: LeituraDecisao | null }) {
  const entradas = [...ENTRADAS_LOBOS, ...mapa.receptores];
  const ye = new Map(entradas.map((e, i) => [e, Y0 + i * SPAN / (entradas.length - 1)]));
  const yr = new Map(REGRAS_LOBOS.map((r, i) => [r, Y0 + i * SPAN / (REGRAS_LOBOS.length - 1)]));
  const ya = new Map(ACOES_LOBOS.map((a, i) => [a, Y0 + i * SPAN / (ACOES_LOBOS.length - 1)]));
  const curva = (e: string, r: RegraLobos, a: AcaoPet): string => {
    const y1 = ye.get(e), y2 = yr.get(r)!, y3 = ya.get(a)!;
    if (y1 === undefined) throw new Error(`entrada fora do mapa: ${e}`);
    return `M${XE} ${f(y1)}C${XE + 34} ${f(y1)} ${XR - 30} ${f(y2)} ${XR} ${f(y2)}C${XR + 26} ${f(y2)} ${XA - 26} ${f(y3)} ${XA} ${f(y3)}`;
  };
  const ac = mapa.acesas;
  if (ac !== null && decisao !== null && (ac.n !== decisao.n || ac.acao !== decisao.acao)) throw new Error("o mapa e a leitura de decisoes diferentes");
  const top = new Set(decisao ? decisao.percepcao.map(p => p.entrada) : []);
  const chance = new Map(decisao ? decisao.chances.map(c => [c.acao, c.chance]) : []);
  const dest = ac ? ac.lobo_decisivo : null;
  const rotulo = ac && decisao
    ? `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Nesta decisão: regra ${TXT_REGRA[ac.regra]}, escolheu ${TXT_ACAO[ac.acao]} com ${Math.round(chance.get(ac.acao)! * 100)}% de chance.`
    : `Mapa dos pesos do pet, ${mapa.arestas.length} pesos. Ainda sem decisão.`;

  const regiao = (lobo: string, x: number, y: number, w: number, h: number, txt: string) =>
    <g className={"mp-reg mp-reg--" + lobo + (dest === lobo ? " mp-dest" : "")} data-lobo={lobo}>
      <rect x={x} y={y} width={w} height={h} rx={8} /><text x={x + 6} y={y + 11}>{txt}</text>
      {dest === lobo && <text className="mp-mais-peso" x={x + w - 6} y={y + h - 5} textAnchor="end">pesou mais</text>}
    </g>;

  return (
    <svg className="mp" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={rotulo} data-n={ac ? ac.n : ""}>
      {regiao("percepcao", 0, 4, 94, YB, "percepção")}
      {regiao("impulsos", 102, 4, 82, YB, "impulsos")}
      {regiao("decisao", 192, 4, 92, YB, "decisão")}
      {regiao("memoria_emocao", 0, YM, W, 18, "memória e emoção: sem pesos")}
      <g className={"mp-pesos" + (ac ? " mp-pesos--fundo" : "")}>
        {mapa.arestas.map(a => {
          const cls = a.aprendido > 0 ? "mp-mais" : a.aprendido < 0 ? "mp-menos" : "mp-prior";
          return <path key={a.regra + a.acao + a.entrada} className={cls} d={curva(a.entrada, a.regra, a.acao)} strokeWidth={f(0.4 + a.espessura * 1.4)}
            strokeOpacity={a.aprendido === 0 ? undefined : f(0.35 + 0.65 * Math.sqrt(Math.abs(a.aprendido)))} strokeDasharray={a.w < 0 ? "3 2" : undefined} />;
        })}
      </g>
      {ac && <g className="mp-acesas">
        {ac.arestas.map(x => <path key={x.entrada} className={x.termo < 0 ? "mp-neg" : undefined} d={curva(x.entrada, ac.regra, ac.acao)}
          strokeWidth={f(0.6 + 3 * x.forca)} strokeOpacity={f(0.35 + 0.65 * x.forca)} />)}
      </g>}
      <g className="mp-nos">
        {entradas.map((e, i) => {
          const y = ye.get(e)!, lit = top.has(e);
          return <g key={e} className={"mp-no" + (i >= ENTRADAS_LOBOS.length ? " mp-corpo" : "") + (lit ? " mp-lit" : "")} data-entrada={e}>
            <circle cx={XE} cy={f(y)} r={lit ? 4 : 3} /><text x={XE - 7} y={f(y + 3)} textAnchor="end">{TXT_ENTRADA[e] ?? e}</text></g>;
        })}
        {REGRAS_LOBOS.map(r => {
          const y = yr.get(r)!, lit = ac !== null && r === ac.regra;
          return <g key={r} className={"mp-no" + (lit ? " mp-lit" : "")} data-regra={r}>
            <circle cx={XR} cy={f(y)} r={lit ? 5.5 : 4} /><text x={XR} y={f(y - 8)} textAnchor="middle">{TXT_REGRA[r]}</text></g>;
        })}
        {ACOES_LOBOS.map(a => {
          const y = ya.get(a)!, c = chance.get(a), esc = ac !== null && a === ac.acao;
          return <g key={a} className={"mp-no" + (c !== undefined ? " mp-cand" : "") + (esc ? " mp-esc" : "")} data-acao={a}>
            <circle cx={XA} cy={f(y)} r={esc ? 6 : c !== undefined ? 5 : 4} />
            <text x={XA + 9} y={f(y + 3)}>{TXT_ACAO[a]}</text>
            {c !== undefined && <text className="mp-pct" x={XA + 9} y={f(y + 13)}>{Math.round(c * 100)}%</text>}</g>;
        })}
      </g>
    </svg>
  );
}

/** a legenda e a nota do mapa: o que a cor e a espessura querem dizer */
export function LegendaMapa() {
  return <>
    <ul className="mp-leg">
      <li><i style={{ "--c": "var(--dl-muted)" }} />instinto</li><li><i style={{ "--c": "var(--mp-mais)" }} />aprendeu a mais</li>
      <li><i style={{ "--c": "var(--mp-menos)" }} />aprendeu a menos</li><li><i style={{ "--c": "var(--mp-aceso)" }} />esta decisão</li>
    </ul>
    <p className="mp-nota">Cada traço é um peso do pet, da entrada à ação, passando pela regra; a espessura é o tamanho do peso.</p>
  </>;
}
