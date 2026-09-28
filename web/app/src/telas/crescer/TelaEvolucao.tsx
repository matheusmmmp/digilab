/* Evolucao (desenhos EvoArvore e EvoPorque; porte do HTML): resumo (forma atual, quanto falta, o porque se
   evoluisse agora), arvore em 4 colunas com estados percorrido/agora/possivel/provavel/fechado/sombria, detalhe
   do no no toque (nunca so no hover, guia 13), por que da forma atual e historico. A forma futura ainda nao
   decidida pelo motor aparece como silhueta, sem nome (guia, secao 5). */
import { useLayoutEffect, useRef, useState } from "preact/hooks";
import {
  CAT, CDJ, DESC_PASSIVA, DESC_TECNICA, DUR_EVO, FORMAS_AD, LINHAS, LINHA_DA_FORMA, NOME_ARQ, NOME_V2, TICK_INICIAL, TPD,
  caraterPrevisto, chaveSprite, formaAdultaDe, linhaDoCarater, nomeEstagio, nomeForma, type Carater, type Forma, type FormaAdultaNormal, type Motor,
} from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, silhuetaAtlas, useAtlas } from "../../atlas.ts";
import { Numeros, rotuloRel } from "../../componentes/Barras.tsx";
import { Porque } from "../../componentes/Revelacao.tsx";
import { useJogo } from "../../jogo.ts";
import { diaDe, hhmm } from "../pet/TelaPet.tsx";

export function duracao(min: number): string {
  const d = Math.floor(min / TPD), h = Math.floor((min % TPD) / 60), m = min % 60;
  return [d ? `${d}d` : "", h ? `${h}h` : "", !d && m ? `${m}min` : ""].filter(Boolean).join(" ") || "agora";
}
/** caráter em palavras: so os eixos fora da faixa comum */
export const fmtCar = (car: Partial<Carater>): string => {
  const f = Object.entries(car).filter(([, v]) => Math.abs(v as number) >= CDJ.limiarTom).map(([k, v]) => `${k} ${rotuloRel(v as number)}`);
  return f.length ? f.join(", ") : "todos os eixos na faixa comum";
};
/** para onde o pet iria se a transicao acontecesse agora, e por que */
export function previsaoEvo(m: Motor): { falta: number; prox: Forma; porque: string } | null {
  const t = m.e.tick - TICK_INICIAL, D = DUR_EVO, f = m.forma;
  if (f.est === "bebe") {
    const c = m.fracaoCuidado();
    return { falta: D.bebe - t, prox: { ...f, est: "crianca", ramo: c >= CAT.limiarCuidado ? "sereno" : "arisco" },
      porque: `cuidado ${(c * 100).toFixed(0)}% (${m.chamados.atendidos} de ${m.chamados.total} chamados atendidos em até ${CAT.janelaChamado} min)` };
  }
  if (f.est === "crianca") {
    const car = caraterPrevisto(m, "adolescente"), linha = linhaDoCarater(car);
    return { falta: D.bebe + D.crianca - t, prox: { ...f, est: "adolescente", linha }, porque: `caráter ${fmtCar(car)}` };
  }
  if (f.est === "adolescente") {
    const car = caraterPrevisto(m, "adulto"), adulta = formaAdultaDe(f.linha!, car), comp = CAT.adulto[f.linha!].comp;
    return { falta: D.bebe + D.crianca + D.adolescente - t, prox: { ...f, est: "adulto", adulta },
      porque: `${comp} ${rotuloRel(car[comp])}; lutas de treino ${m.sparring} de ${CAT.sparring}` };
  }
  return null;
}
export function requisito(g: Forma): string {
  if (g.est === "bebe") return "sai do ovo";
  if (g.est === "crianca") return g.ramo === "sereno" ? `cuidado ≥ ${CAT.limiarCuidado * 100}% dos chamados no In-Training` : `cuidado < ${CAT.limiarCuidado * 100}% dos chamados no In-Training`;
  if (g.est === "adolescente") { const a = CAT.adolescente[g.linha!]; return `caráter dominante ${a.eixo} ao fim do Rookie · técnica ${NOME_V2[a.tecnica]}: ${DESC_TECNICA[a.tecnica]}`; }
  const a = CAT.adulto[g.linha!], s = a.formas[g.adulta as FormaAdultaNormal]!.sinal;
  return `${a.comp} ${s > 0 ? "acima" : "abaixo"} do pet comum e ${CAT.sparring} lutas de treino · passiva: ${DESC_PASSIVA[g.adulta!]}`;
}

type EstadoNo = "agora" | "percorrido" | "possivel" | "fechado";
type Aresta = [string, string, "percorrido" | "provavel" | "possivel" | "fechado"];

function No({ g, estado, provavel, sombria, escolher }: { g: Forma; estado: EstadoNo; provavel: boolean; sombria: boolean; escolher: (det: string) => void }) {
  const a = useAtlas(), id = chaveSprite(g), revelado = estado === "agora" || estado === "percorrido";
  const img = a.tipo === "ok" ? (revelado ? imagemAtlas(a, id) : silhuetaAtlas(a, id)) : null;
  const h = a.tipo === "ok" ? dimSprite(a.dados, id)[1] : 32, top = h > 44 ? -Math.round(h * .08) : Math.round((44 - h) / 2);
  const cls = ["evo-no", estado, provavel ? "provavel" : "", estado === "agora" && sombria ? "sombria" : ""].filter(Boolean).join(" ");
  const det = (revelado ? nomeForma(g) : "Forma ainda não decidida") + ": " + requisito(g);
  return (
    <button type="button" class={cls} data-id={id} aria-label={(revelado ? nomeForma(g) : "forma ainda não decidida") + ", " + estado} onClick={() => escolher(det)}>
      <span class="evo-cx">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" style={{ marginTop: `${top}px`, ...(revelado ? {} : { opacity: .45 }) }} />}{!revelado && <b class="evo-q">?</b>}</span>
      <span class="evo-rot">{revelado ? nomeForma(g) : "?"}</span>
    </button>
  );
}

function Arvore({ m, p }: { m: Motor; p: ReturnType<typeof previsaoEvo> }) {
  const [det, setDet] = useState<string | null>(null), arv = useRef<HTMLDivElement>(null), [linhas, setLinhas] = useState<{ w: number; h: number; d: [string, string][] }>({ w: 0, h: 0, d: [] });
  const f = m.forma, esp = m.especie, idDe = (g: Forma) => chaveSprite(g), evs = m.evolucoes;
  const bebe: Forma = { esp, est: "bebe" };
  const cri: Forma[] = (["sereno", "arisco"] as const).map(r => ({ esp, est: "crianca", ramo: r }));
  const ado: Forma[] = LINHAS.map(l => ({ esp, est: "adolescente", ramo: "sereno", linha: l }));
  const adu: Forma[] = FORMAS_AD.map(ad => ({ esp, est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[ad], adulta: ad }));
  const caminho = new Set([idDe(bebe), ...evs.map(x => chaveSprite(x.forma))]);
  const atualId = idDe(f), provId = p ? idDe(p.prox) : null;
  /* o que ainda da para alcancar a partir da forma atual */
  const alcance = new Set(f.est === "bebe" ? [...cri, ...ado, ...adu].map(idDe) : f.est === "crianca" ? [...ado, ...adu].map(idDe)
    : f.est === "adolescente" ? adu.filter(x => x.linha === f.linha).map(idDe) : []);
  const estado = (id: string): EstadoNo => id === atualId ? "agora" : caminho.has(id) ? "percorrido" : alcance.has(id) ? "possivel" : "fechado";
  /* arestas: bebe -> criancas -> (qualquer) adolescente -> adultos da linha */
  const arestas: Aresta[] = [...cri.map(c => [idDe(bebe), idDe(c)]), ...cri.flatMap(c => ado.map(x => [idDe(c), idDe(x)])),
    ...adu.map(x => [idDe(ado[LINHAS.indexOf(x.linha!)]), idDe(x)])].map(([a, b]) =>
    [a, b, caminho.has(a) && (caminho.has(b) || b === atualId) ? "percorrido" : a === atualId && b === provId ? "provavel" : estado(b) === "fechado" || estado(a) === "fechado" ? "fechado" : "possivel"] as Aresta);
  const chave = arestas.map(x => x.join(">")).join("|");
  /* linhas da arvore a partir das posicoes dos nos na tela (a arvore e HTML; so as linhas sao SVG) */
  useLayoutEffect(() => {
    const medir = () => {
      const el = arv.current; if (!el || !el.offsetParent) return;
      const r0 = el.getBoundingClientRect(), pos: Record<string, [number, number, number]> = {};
      el.querySelectorAll<HTMLElement>(".evo-no").forEach(n => { const r = n.querySelector(".evo-cx")!.getBoundingClientRect(); pos[n.dataset.id!] = [r.left - r0.left, r.right - r0.left, r.top - r0.top + r.height / 2]; });
      const ordem = { fechado: 0, possivel: 1, provavel: 2, percorrido: 3 };
      const d = [...arestas].sort((x, y) => ordem[x[2]] - ordem[y[2]]).flatMap(([a, b, c]) => {
        const A = pos[a], B = pos[b]; if (!A || !B) return [];
        const x1 = A[1], y1 = A[2], x2 = B[0], y2 = B[2], xm = (x1 + x2) / 2;
        return [[`M${x1} ${y1} C ${xm} ${y1}, ${xm} ${y2}, ${x2} ${y2}`, c] as [string, string]];
      });
      setLinhas({ w: r0.width, h: r0.height, d });
    };
    medir();
    addEventListener("resize", medir);
    return () => removeEventListener("resize", medir);
  }, [chave]);
  const col = (tit: string, gs: Forma[]) => (
    <div class="evo-col"><span class="evo-col-tit">{tit}</span>
      <div class="evo-col-nos">{gs.map(g => <No key={idDe(g)} g={g} estado={estado(idDe(g))} provavel={idDe(g) === provId} sombria={m.sombria} escolher={setDet} />)}</div></div>
  );
  return <>
    <div class="evo-arv" ref={arv} role="group" aria-label="Árvore de evolução">
      <svg class="evo-linhas" aria-hidden="true" width={linhas.w} height={linhas.h} viewBox={`0 0 ${linhas.w} ${linhas.h}`}>
        {linhas.d.map(([d, c], i) => <path key={i} class={`evo-aresta ${c}`} d={d} />)}
      </svg>
      {col("In-Training", [bebe])}{col("Rookie", cri)}{col("Champion", ado)}{col("Ultimate/Mega", adu)}
    </div>
    {det && <p class="dl-card evo-no-det" aria-live="polite">{det}</p>}
  </>;
}

export function TelaEvolucao() {
  const { motor: m } = useJogo(), f = m.forma, evs = m.evolucoes, p = previsaoEvo(m);
  const espera = !!p && p.falta <= 0 && f.est === "adolescente", ult = evs[evs.length - 1];
  const det = (x: typeof evs[number]) => x.estagio === "crianca" ? `cuidado ${(x.cuidado! * 100).toFixed(0)}%`
    : x.estagio === "adolescente" ? `caráter: ${fmtCar(x.carater!)}` : `caráter: ${fmtCar(x.carater!)}; ${x.sparring} lutas de treino`;
  return (
    <div class="tela dl">
      <p style={{ margin: 0 }}>Cada evolução é decidida pelo que o pet viveu: cuidado, caráter e lutas de treino.</p>
      <details class="dl-apoio"><summary>Como funciona</summary>
        <p>Uma moeda por transição (os contadores zeram a cada evolução). <b>In-Training → Rookie</b> (3 h): o <b>cuidado</b> decide o ramo; o In-Training chama em horário fixo (fome a cada 30 min, higiene a cada 60, carinho a cada 45) e atender pelo menos 80% dos chamados em até 15 min dá Sereno, menos dá Arisco. <b>Rookie → Champion</b> (12 h): o <b>caráter dominante</b> decide a linha e a técnica. <b>Champion → Ultimate ou Mega</b> (18 h e 10 lutas de treino na arena): o <b>eixo complementar</b> da linha decide a forma e a passiva. Caráter: quanto os traços do pet estão acima de um pet comum em cada eixo.</p>
      </details>
      <Numeros itens={[
        ["forma atual", nomeForma(f)],
        [p ? (espera ? "de treino (arena) para virar Ultimate ou Mega" : `até virar ${p.prox.est === "adulto" ? "Ultimate ou Mega" : nomeEstagio(p.prox)}`) : "forma final",
          p ? (espera ? `${CAT.sparring - m.sparring} lutas` : duracao(Math.max(0, p.falta))) : "—"],
        /* a forma futura ainda nao foi decidida pelo motor: mostra so o porque, sem o nome */
        [p ? `se evoluísse agora: ${p.porque}` : `passiva: ${DESC_PASSIVA[f.adulta!]}`, p ? "?" : NOME_ARQ[f.adulta!]],
      ]} />
      <Arvore m={m} p={p} />
      <ul class="evo-legenda" aria-label="Legenda da árvore">
        <li><span class="evo-mini percorrido" />percorrido</li><li><span class="evo-mini agora" />agora</li>
        <li><span class="evo-mini possivel" />possível</li><li><span class="evo-mini provavel" />se evoluísse agora</li>
        <li><span class="evo-mini fechado" />fechado</li><li><span class="evo-mini sombria" />sombria</li>
      </ul>
      <p class="dl-apoio" style={{ margin: 0 }}>Toque num nó para ver o que leva até ele.</p>
      {ult && <section class="dl-card revel-porque"><h3 class="dl-titulo-card">Por que {nomeForma(f)}?</h3><Porque x={ult} /></section>}
      <section class="bloco">
        <h2>Histórico</h2>
        <div class="evo-hist">
          <div><span class="t">D1 {hhmm(TICK_INICIAL)}</span><span>nasceu: <b>{nomeForma({ esp: m.especie, est: "bebe" })}</b></span></div>
          {evs.map((x, i) => <div key={i}><span class="t">D{diaDe(x.tick)} {hhmm(x.tick)}</span><span>virou <b>{nomeForma(x.forma)}</b> ({det(x)})</span></div>)}
        </div>
      </section>
    </div>
  );
}
