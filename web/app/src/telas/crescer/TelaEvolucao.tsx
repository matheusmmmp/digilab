/* Evolucao (pranchas EvoArvore e EvoPorque; porte do HTML): arvore de cima para baixo (In-Training, 2 Rookie,
   4 Champion e, embaixo de cada um, os 2 Ultimate/Mega da linha e a sombria), resumo (forma atual, quanto falta, o porque se
   evoluisse agora), com estados percorrido/agora/possivel/provavel/fechado/sombria, detalhe
   do no no toque (nunca so no hover, guia 13), por que da forma atual e historico. A forma futura ainda nao
   decidida pelo motor aparece como silhueta, sem nome (guia, secao 5). */
import { useLayoutEffect, useRef, useState } from "preact/hooks";
import {
  CAT, CDJ, CLE, CSO, DESC_PASSIVA, DESC_TECNICA, FORMAS_AD, LINHAS, LINHA_DA_FORMA, NOME_ARQ, NOME_V2, TICK_INICIAL, TPD,
  caraterPrevisto, chaveSprite, formaAdultaDe, linhaDoCarater, nomeEstagio, nomeForma, type Carater, type Forma, type FormaAdultaNormal, type Motor,
} from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, silhuetaAtlas, useAtlas } from "../../atlas.ts";
import { Numeros, rotuloRel } from "../../componentes/Barras.tsx";
import { Deco } from "../../componentes/Deco.tsx";
import { Porque } from "../../componentes/Revelacao.tsx";
import { BRASAO } from "../../decoracao.ts";
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
  const t = m.e.tick - TICK_INICIAL, D = m.dur, f = m.forma;
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
type Aresta = [string, string, "percorrido" | "provavel" | "possivel" | "fechado" | "sombria", "elbow" | "reta" | "chave"];
const SUB_RAMO: Record<string, string> = { sereno: `cuidado ≥ ${CAT.limiarCuidado * 100}%`, arisco: `cuidado < ${CAT.limiarCuidado * 100}%` };

/** no da arvore (prancha EvoArvore): o card inteiro e o botao; molduras por estado (percorrido, agora, possivel,
    fechado, sombria); o sprite em 1x, cortado no card quando e maior; forma ainda nao decidida = silhueta sem nome */
function No({ g, estado, provavel, sombriaNo, sombriaAgora, sub, escolher }: { g: Forma; estado: EstadoNo; provavel: boolean; sombriaNo: boolean; sombriaAgora: boolean; sub: string; escolher: (det: string) => void }) {
  const a = useAtlas(), id = chaveSprite(g), revelado = estado === "agora" || estado === "percorrido";
  const img = a.tipo === "ok" ? (revelado ? imagemAtlas(a, id, 1, { sombria: sombriaNo }) : silhuetaAtlas(a, id)) : null;
  const cls = ["evo-no", `evo-no--${g.est}`, estado, provavel ? "provavel" : "", sombriaNo ? "sombria" : "", estado === "agora" && sombriaAgora ? "sombria-agora" : ""].filter(Boolean).join(" ");
  const det = (revelado ? nomeForma(g) : "Forma ainda não decidida") + ": " + (sombriaNo ? "forma sombria da linha (sobrecarga alta na virada para Ultimate)" : requisito(g));
  return (
    <button type="button" class={cls} data-id={id + (sombriaNo ? "_s" : "")} aria-label={(revelado ? nomeForma(g) : "forma ainda não decidida") + ", " + (sombriaNo ? "sombria, " : "") + estado} onClick={() => escolher(det)}>
      {estado === "percorrido" && <span class="evo-ok" aria-hidden="true"><svg viewBox="0 0 12 12" width="10" height="10"><path d="M2 6.5 5 9l5-6" /></svg></span>}
      {estado === "agora" && <span class="evo-agora">AGORA</span>}
      <span class="evo-img">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" style={revelado ? {} : { opacity: .45 }} />}</span>
      <span class="evo-rot">{revelado ? nomeForma(g) : "?"}</span>
      {sub && <span class="evo-sub">{sub}</span>}
    </button>
  );
}

function Arvore({ m, p }: { m: Motor; p: ReturnType<typeof previsaoEvo> }) {
  const [det, setDet] = useState<string | null>(null), arv = useRef<HTMLDivElement>(null), [linhas, setLinhas] = useState<{ w: number; h: number; d: [string, string][] }>({ w: 0, h: 0, d: [] });
  const f = m.forma, esp = m.especie, idDe = (g: Forma) => chaveSprite(g), evs = m.evolucoes;
  const bebe: Forma = { esp, est: "bebe" };
  const cri: Forma[] = (["sereno", "arisco"] as const).map(r => ({ esp, est: "crianca", ramo: r }));
  const ado: Forma[] = LINHAS.map(l => ({ esp, est: "adolescente", ramo: "sereno", linha: l }));
  const aduDe = (l: string): Forma[] => FORMAS_AD.filter(ad => LINHA_DA_FORMA[ad] === l).map(ad => ({ esp, est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[ad], adulta: ad }));
  const somDe = (l: string): Forma => { const x = CSO.formas[l as keyof typeof CSO.formas]; return { esp, est: "adulto", ramo: "sereno", linha: l as Forma["linha"], adulta: x.nome as Forma["adulta"] }; };
  const caminho = new Set([idDe(bebe), ...evs.map(x => chaveSprite(x.forma))]);
  const atualId = idDe(f), provId = p ? idDe(p.prox) : null;
  const adu = LINHAS.flatMap(aduDe);
  /* o que ainda da para alcancar a partir da forma atual */
  const alcance = new Set(f.est === "bebe" ? [...cri, ...ado, ...adu].map(idDe) : f.est === "crianca" ? [...ado, ...adu].map(idDe)
    : f.est === "adolescente" ? adu.filter(x => x.linha === f.linha).map(idDe) : []);
  const estado = (id: string): EstadoNo => id === atualId ? "agora" : caminho.has(id) ? "percorrido" : alcance.has(id) ? "possivel" : "fechado";
  const tipo = (a: string, b: string): Aresta[2] => caminho.has(a) && (caminho.has(b) || b === atualId) ? "percorrido" : a === atualId && b === provId ? "provavel"
    : estado(b) === "fechado" || estado(a) === "fechado" ? "fechado" : "possivel";
  /* arestas: bebe -> criancas; a crianca atual (ou as duas, no bebe) -> adolescentes; adolescente -> adultos da linha e a sombria */
  const criDe = f.est === "bebe" ? cri : cri.filter(c => caminho.has(idDe(c)) || idDe(c) === atualId);
  const arestas: Aresta[] = [
    ...cri.map(c => [idDe(bebe), idDe(c), tipo(idDe(bebe), idDe(c)), "elbow"] as Aresta),
    ...criDe.flatMap(c => ado.map(x => [idDe(c), idDe(x), tipo(idDe(c), idDe(x)), "elbow"] as Aresta)),
    ...ado.flatMap(x => aduDe(x.linha!).map((y, k) => [idDe(x) + "#" + k, idDe(y), tipo(idDe(x), idDe(y)), "reta"] as Aresta)),
    ...ado.map(x => [idDe(x), idDe(somDe(x.linha!)) + "_s", "sombria", "chave"] as Aresta),
  ];
  const chave = arestas.map(x => x.join(">")).join("|");
  /* linhas da arvore a partir das posicoes dos nos (a arvore e HTML; so as linhas sao SVG): cotovelo entre niveis,
     retas do Champion aos dois adultos (a segunda passa atras do primeiro) e o colchete tracejado ate a sombria */
  useLayoutEffect(() => {
    const medir = () => {
      const el = arv.current; if (!el || !el.offsetParent) return;
      /* com o zoom do desktop (escala.ts) as medidas da tela vem multiplicadas; o SVG desenha em px de CSS: divide pela
         escala real da propria arvore */
      const r0 = el.getBoundingClientRect(), z = el.offsetWidth > 0 ? r0.width / el.offsetWidth : 1, pos: Record<string, DOMRect> = {};
      el.querySelectorAll<HTMLElement>(".evo-no").forEach(n => { pos[n.dataset.id!] = n.getBoundingClientRect(); });
      const ordem = { fechado: 0, sombria: 0, possivel: 1, provavel: 2, percorrido: 3 };
      const d = [...arestas].sort((x, y) => ordem[x[2]] - ordem[y[2]]).flatMap(([a0, b, c, forma]) => {
        const [a, k] = a0.split("#"), A = pos[a], Bn = pos[b]; if (!A || !Bn) return [];
        const L = (x: number) => (x - r0.left) / z, T = (y: number) => (y - r0.top) / z;
        if (forma === "elbow") {
          const x1 = L(A.left + A.width / 2), y1 = T(A.bottom), x2 = L(Bn.left + Bn.width / 2), y2 = T(Bn.top), ym = (y1 + y2) / 2;
          return [[`M${x1} ${y1} V${ym} H${x2} V${y2}`, c] as [string, string]];
        }
        if (forma === "reta") { const x = L(A.left + A.width / 2) + (k === "0" ? -8 : 8); return [[`M${x} ${T(A.bottom)} V${T(Bn.top)}`, c] as [string, string]]; }
        const x = L(A.left) - 2, y1 = T(A.top + A.height / 2), y2 = T(Bn.top + Bn.height / 2);
        return [[`M${x + 2} ${y1} H${x - 4} V${y2} H${x + 4}`, c] as [string, string]];
      });
      setLinhas({ w: el.offsetWidth, h: el.offsetHeight, d });
    };
    medir();
    /* remede quando a arvore muda de tamanho (layout do desktop, fontes, sprites que chegam depois), nao so no resize */
    const ro = typeof ResizeObserver === "function" ? new ResizeObserver(medir) : null;
    if (arv.current) ro?.observe(arv.current);
    addEventListener("resize", medir);
    return () => { ro?.disconnect(); removeEventListener("resize", medir); };
  }, [chave]);
  const no = (g: Forma, sub: string, sombriaNo = false) => (
    <No key={idDe(g) + (sombriaNo ? "_s" : "")} g={g} estado={sombriaNo ? (m.sombria && idDe(g) === atualId ? "agora" : "fechado") : estado(idDe(g))}
      provavel={!sombriaNo && idDe(g) === provId} sombriaNo={sombriaNo} sombriaAgora={m.sombria} sub={sub} escolher={setDet} />
  );
  return <>
    <div class="evo-arv" ref={arv} role="group" aria-label="Árvore de evolução">
      <svg class="evo-linhas" aria-hidden="true" width={linhas.w} height={linhas.h} viewBox={`0 0 ${linhas.w} ${linhas.h}`}>
        {linhas.d.map(([d, c], i) => <path key={i} class={`evo-aresta ${c}`} d={d} />)}
      </svg>
      <div class="evo-nivel evo-nivel--bebe">{no(bebe, "")}</div>
      <div class="evo-nivel evo-nivel--crianca">{cri.map(c => no(c, SUB_RAMO[c.ramo!]))}</div>
      <div class="evo-nivel evo-nivel--linhas">
        {ado.map(x => (
          <div class="evo-coluna" key={x.linha}>
            {no(x, CAT.adolescente[x.linha!].eixo)}
            {aduDe(x.linha!).map(y => no(y, ""))}
            {no(somDe(x.linha!), "sombria", true)}
          </div>
        ))}
      </div>
    </div>
    <ul class="evo-legenda" aria-label="Legenda da árvore">
      <li><span class="evo-mini percorrido" />percorrido</li><li><span class="evo-mini agora" />agora</li>
      <li><span class="evo-mini possivel" />possível</li><li><span class="evo-mini provavel" />se evoluísse agora</li>
      <li><span class="evo-mini fechado" />fechado</li><li><span class="evo-mini sombria" />sombria</li>
    </ul>
    {det ? <p class="dl-card evo-no-det" aria-live="polite">{det}</p> : <p class="dl-apoio" style={{ margin: 0 }}>Toque num nó para ver o que leva até ele.</p>}
  </>;
}

export function TelaEvolucao() {
  const { motor: m } = useJogo(), f = m.forma, evs = m.evolucoes, p = previsaoEvo(m);
  const espera = !!p && p.falta <= 0 && f.est === "adolescente", ult = evs[evs.length - 1];
  /* pets v4: alem das 10 lutas, a taxa de vitoria do adolescente precisa chegar a 80% */
  const taxa = m.taxaVitoria(), faltaTaxa = m.versao >= 4 && m.sparring >= CAT.sparring && (taxa ?? 0) < CLE.limiarTaxa;
  const det = (x: typeof evs[number]) => x.estagio === "crianca" ? `cuidado ${(x.cuidado! * 100).toFixed(0)}%`
    : x.estagio === "adolescente" ? `caráter: ${fmtCar(x.carater!)}` : `caráter: ${fmtCar(x.carater!)}; ${x.sparring} lutas de treino`;
  return (
    <div class="tela dl desk evo-tela">
      <div class="evo-principal"><h2 class="desk-so evo-arv-tit">Árvore de {BRASAO[m.especie].nome}</h2><Arvore m={m} p={p} /></div>
      <div class="evo-lado">
      <div class="desk-col evo-resumo">
      <p class="evo-selo"><Deco nome={BRASAO[m.especie].peca} class="evo-selo-img" /><span>brasão <b>{BRASAO[m.especie].nome}</b>: as formas da árvore são as deste brasão.</span></p>
      <p style={{ margin: 0 }}>Cada evolução é decidida pelo que o pet viveu: cuidado, caráter e lutas de treino.</p>
      <details class="dl-apoio"><summary>Como funciona</summary>
        <p>Uma moeda por transição (os contadores zeram a cada evolução). <b>In-Training → Rookie</b> ({m.dur.bebe / 60} h): o <b>cuidado</b> decide o ramo; o In-Training chama em horário fixo (fome a cada 30 min, higiene a cada 60, carinho a cada 45) e atender pelo menos 80% dos chamados em até 15 min dá Sereno, menos dá Arisco. <b>Rookie → Champion</b> ({m.dur.crianca / 60} h): o <b>caráter dominante</b> decide a linha e a técnica. <b>Champion → Ultimate ou Mega</b> ({m.dur.adolescente / 60} h e 10 lutas de treino na arena): o <b>eixo complementar</b> da linha decide a forma e a passiva. Caráter: quanto os traços do pet estão acima de um pet comum em cada eixo.</p>
      </details>
      <Numeros itens={[
        ["forma atual", nomeForma(f)],
        [p ? (espera ? "de treino (arena) para virar Ultimate ou Mega" : `até virar ${p.prox.est === "adulto" ? "Ultimate ou Mega" : nomeEstagio(p.prox)}`) : "forma final",
          p ? (espera ? (faltaTaxa ? `vitórias ${Math.round((taxa ?? 0) * 100)}% de ${Math.round(CLE.limiarTaxa * 100)}%` : `${CAT.sparring - m.sparring} lutas`)
            : duracao(Math.max(0, p.falta))) : "—"],
        ...(m.versao >= 4 ? [["experiência de combate: cada vitória o deixa mais preciso na luta",
          `${m.vitoriasVida} ${m.vitoriasVida === 1 ? "vitória" : "vitórias"}${m.vitoriasVida * CLE.expPorVitoria >= CLE.expMax ? " (máximo)" : ""}`] as [string, string]] : []),
        ...(m.versao >= 4 && f.est === "adolescente" ? [["vitórias nas lutas deste estágio (precisa de 80% para evoluir)",
          m.lutas.lutas ? `${m.lutas.vitorias} de ${m.lutas.lutas}` : "nenhuma luta"] as [string, string]] : []),
        /* a forma futura ainda nao foi decidida pelo motor: mostra so o porque, sem o nome */
        [p ? `se evoluísse agora: ${p.porque}` : `passiva: ${DESC_PASSIVA[f.adulta!]}`, p ? "?" : NOME_ARQ[f.adulta!]],
      ]} />
      </div>
      {ult && <section class="dl-card revel-porque"><h3 class="dl-titulo-card">Por que {nomeForma(f)}?</h3><Porque x={ult} /></section>}
      <section class="bloco">
        <h2>Histórico</h2>
        <div class="evo-hist">
          <div><span class="t">D1 {hhmm(TICK_INICIAL)}</span><span>nasceu: <b>{nomeForma({ esp: m.especie, est: "bebe" })}</b></span></div>
          {evs.map((x, i) => <div key={i}><span class="t">D{diaDe(x.tick)} {hhmm(x.tick)}</span><span>virou <b>{nomeForma(x.forma)}</b> ({det(x)})</span></div>)}
        </div>
      </section>
      </div>
    </div>
  );
}
