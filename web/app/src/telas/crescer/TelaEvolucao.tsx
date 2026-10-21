/* Evolucao (docs/TAREFA_V2_EVOLUCAO.md: composicao propria na linguagem da moldura nova e do momento da evolucao; antes, pranchas EvoArvore e
   EvoPorque): a forma atual em destaque (o pet na plataforma de luz, o nome, o estagio e quanto falta), a proxima evolucao com as medalhas
   que faltam, a arvore, o porque da forma atual e o historico em linha do tempo, com "Ver a revelacao de novo" em cada evolucao.
   A arvore: de cima para baixo (In-Training, 2 Rookie,
   4 Champion e, embaixo de cada um, os 2 arquetipos do Ultimate da linha, o Mega (pets v5) e a sombria), resumo (forma atual, quanto falta, o porque se
   evoluisse agora), com estados percorrido/agora/possivel/provavel/fechado/sombria, detalhe
   do no no toque (nunca so no hover, guia 13), por que da forma atual e historico. A forma futura ainda nao
   decidida pelo motor aparece como silhueta, sem nome (guia, secao 5). */
import { useLayoutEffect, useRef, useState } from "react";
import { GitBranch, History, Info, Sparkles } from "lucide-react";
import {
  CAT, CDJ, CLE, CMD, CMG, CSO, DESC_PASSIVA, DESC_TECNICA, FORMAS_AD, LINHAS, LINHA_DA_FORMA, NOME_ARQ, NOME_V2, SOMBRIA, TICK_INICIAL, TPD,
  caraterPrevisto, chaveSprite, corDominante, formaAdultaDe, linhaDoCarater, nomeArquetipo, nomeEstagio, nomeForma, type Carater, type Forma, type FormaAdultaNormal, type Motor,
} from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, silhuetaAtlas, useAtlas } from "../../atlas.ts";
import { Numeros, rotuloRel } from "../../componentes/Barras.tsx";
import { Deco } from "../../componentes/Deco.tsx";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { PetGrande, Porque, reverEvolucao } from "../../componentes/Revelacao.tsx";
import { useDesktop } from "../../desktop.ts";
import { BRASAO } from "../../decoracao.ts";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { medalhasQueFaltam, textoFalta } from "../../tamer.ts";
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
    return { falta: m.tickLimiteEstagio()! - m.e.tick, prox: { ...f, est: "adolescente", linha }, porque: `caráter ${fmtCar(car)}` };
  }
  if (f.est === "adolescente") {
    const car = caraterPrevisto(m, "adulto"), adulta = formaAdultaDe(f.linha!, car), comp = CAT.adulto[f.linha!].comp;
    return { falta: m.tickLimiteEstagio()! - m.e.tick, prox: { ...f, est: "adulto", adulta },
      porque: `${comp} ${rotuloRel(car[comp])}; lutas de treino ${m.sparring} de ${CAT.sparring}` };
  }
  /* pets v5: Ultimate -> Mega (a sombria nunca) */
  const r = m.requisitosMega();
  if (r && !m.sombria) {
    const L = m.lutas;
    return { falta: r.falta, prox: { ...f, est: "mega" },
      porque: `vínculo ${virgula(m.vinc.valor)} de ${virgula(CMG.vinculo)}; lutas no Ultimate ${L.lutas} de ${CAT.sparring}, `
        + `vitórias ${L.lutas ? Math.round(L.vitorias / L.lutas * 100) : 0}% de ${Math.round(CLE.limiarTaxa * 100)}%` };
  }
  return null;
}
const virgula = (x: number): string => (Math.round(x * 100) / 100).toString().replace(".", ",");
/** id do no da arvore: as duas formas adultas da linha tem o mesmo sprite (o Ultimate), entao o no e pela forma; o Mega
    tem um no por linha */
const linhaDe = (g: Forma): string => g.linha ?? SOMBRIA[g.adulta!]?.linha ?? LINHA_DA_FORMA[g.adulta as FormaAdultaNormal];
export const idNo = (g: Forma): string => g.est === "mega" ? `${g.esp}_mega_${linhaDe(g)}` : g.est === "adulto" ? `${g.esp}_adulto_${g.adulta}` : chaveSprite(g);
/** pets v6: as medalhas do Tamer que a evolucao para a forma pede (texto do no) */
const medReq = (g: Forma, v6: boolean): string => {
  const n = v6 ? (CMD as Record<string, number>)[g.est] ?? 0 : 0;
  return n ? ` · ${n} medalha${n === 1 ? "" : "s"} do Tamer` : "";
};
export function requisito(g: Forma, v6 = false): string {
  if (g.est === "bebe") return "sai do ovo";
  if (g.est === "crianca") return g.ramo === "sereno" ? `cuidado ≥ ${CAT.limiarCuidado * 100}% dos chamados no In-Training` : `cuidado < ${CAT.limiarCuidado * 100}% dos chamados no In-Training`;
  if (g.est === "adolescente") { const a = CAT.adolescente[g.linha!]; return `caráter dominante ${a.eixo} ao fim do Rookie${medReq(g, v6)} · técnica ${NOME_V2[a.tecnica]}: ${DESC_TECNICA[a.tecnica]}`; }
  if (g.est === "mega") return `Mega: o mesmo arquétipo do Ultimate, mais forte · ${duracao(CMG.durRapida)} como Ultimate (o dobro no ritmo clássico), ${CAT.sparring} lutas com ${CLE.limiarTaxa * 100}% ou mais de vitórias e vínculo ${virgula(CMG.vinculo)} ou mais${medReq(g, v6)} (a sombria não chega)`;
  const a = CAT.adulto[g.linha!], s = a.formas[g.adulta as FormaAdultaNormal]!.sinal;
  return `${NOME_ARQ[g.adulta!]}: ${a.comp} ${s > 0 ? "acima" : "abaixo"} do pet comum e ${CAT.sparring} lutas de treino${medReq(g, v6)} · passiva: ${DESC_PASSIVA[g.adulta!]}`;
}

type EstadoNo = "agora" | "percorrido" | "possivel" | "fechado";
type Aresta = [string, string, "percorrido" | "provavel" | "possivel" | "fechado" | "sombria", "elbow" | "reta" | "chave"];
const SUB_RAMO: Record<string, string> = { sereno: `cuidado ≥ ${CAT.limiarCuidado * 100}%`, arisco: `cuidado < ${CAT.limiarCuidado * 100}%` };

/** no da arvore (prancha EvoArvore): o card inteiro e o botao; molduras por estado (percorrido, agora, possivel,
    fechado, sombria); o sprite em 1x, cortado no card quando e maior; forma ainda nao decidida = silhueta sem nome */
function No({ g, estado, provavel, sombriaNo, sombriaAgora, sub, escolher, v6 }: { g: Forma; estado: EstadoNo; provavel: boolean; sombriaNo: boolean; sombriaAgora: boolean; sub: string; escolher: (det: string) => void; v6: boolean }) {
  const a = useAtlas(), spr = chaveSprite(g), id = idNo(g), revelado = estado === "agora" || estado === "percorrido";
  const img = a.tipo === "ok" ? (revelado ? imagemAtlas(a, spr, 1, { sombria: sombriaNo }) : silhuetaAtlas(a, spr)) : null;
  const cls = ["evo-no", `evo-no--${g.est}`, estado, provavel ? "provavel" : "", sombriaNo ? "sombria" : "", estado === "agora" && sombriaAgora ? "sombria-agora" : ""].filter(Boolean).join(" ");
  const det = (revelado ? nomeForma(g) : "Forma ainda não decidida") + ": " + (sombriaNo ? "forma sombria da linha (sobrecarga alta na virada para Ultimate)" : requisito(g, v6));
  return (
    <button type="button" className={cls} data-id={id + (sombriaNo ? "_s" : "")} aria-label={(revelado ? nomeForma(g) : "forma ainda não decidida") + ", " + (sombriaNo ? "sombria, " : "") + estado} onClick={() => escolher(det)}>
      {estado === "percorrido" && <span className="evo-ok" aria-hidden="true"><svg viewBox="0 0 12 12" width="10" height="10"><path d="M2 6.5 5 9l5-6" /></svg></span>}
      {estado === "agora" && <span className="evo-agora">AGORA</span>}
      <span className="evo-img">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" style={revelado ? {} : { opacity: .45 }} />}</span>
      <span className="evo-rot">{revelado ? nomeForma(g) : "?"}</span>
      {sub && <span className="evo-sub">{sub}</span>}
    </button>
  );
}

function Arvore({ m, p }: { m: Motor; p: ReturnType<typeof previsaoEvo> }) {
  const [det, setDet] = useState<string | null>(null), arv = useRef<HTMLDivElement>(null), [linhas, setLinhas] = useState<{ w: number; h: number; d: [string, string][] }>({ w: 0, h: 0, d: [] });
  const f = m.forma, esp = m.especie, idDe = idNo, evs = m.evolucoes, v5 = m.versao >= 5;
  const bebe: Forma = { esp, est: "bebe" };
  const cri: Forma[] = (["sereno", "arisco"] as const).map(r => ({ esp, est: "crianca", ramo: r }));
  const ado: Forma[] = LINHAS.map(l => ({ esp, est: "adolescente", ramo: "sereno", linha: l }));
  const aduDe = (l: string): Forma[] => FORMAS_AD.filter(ad => LINHA_DA_FORMA[ad] === l).map(ad => ({ esp, est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[ad], adulta: ad }));
  const somDe = (l: string): Forma => { const x = CSO.formas[l as keyof typeof CSO.formas]; return { esp, est: "adulto", ramo: "sereno", linha: l as Forma["linha"], adulta: x.nome as Forma["adulta"] }; };
  const megaDe = (l: string): Forma => ({ ...aduDe(l)[0], est: "mega" });
  const caminho = new Set([idDe(bebe), ...evs.map(x => idDe(x.forma))]);
  const atualId = idDe(f), provId = p ? idDe(p.prox) : null;
  const adu = LINHAS.flatMap(aduDe), meg = v5 ? LINHAS.map(megaDe) : [];
  /* o que ainda da para alcancar a partir da forma atual (o Mega: so pets v5, e nunca a sombria) */
  const alcance = new Set(f.est === "bebe" ? [...cri, ...ado, ...adu, ...meg].map(idDe) : f.est === "crianca" ? [...ado, ...adu, ...meg].map(idDe)
    : f.est === "adolescente" ? [...adu, ...meg].filter(x => x.linha === f.linha).map(idDe)
    : f.est === "adulto" && v5 && !m.sombria ? [idDe(megaDe(f.linha!))] : []);
  const estado = (id: string): EstadoNo => id === atualId ? "agora" : caminho.has(id) ? "percorrido" : alcance.has(id) ? "possivel" : "fechado";
  const tipo = (a: string, b: string): Aresta[2] => caminho.has(a) && (caminho.has(b) || b === atualId) ? "percorrido" : a === atualId && b === provId ? "provavel"
    : estado(b) === "fechado" || estado(a) === "fechado" ? "fechado" : "possivel";
  /* arestas: bebe -> criancas; a crianca atual (ou as duas, no bebe) -> adolescentes; adolescente -> adultos da linha e a sombria */
  const criDe = f.est === "bebe" ? cri : cri.filter(c => caminho.has(idDe(c)) || idDe(c) === atualId);
  const arestas: Aresta[] = [
    ...cri.map(c => [idDe(bebe), idDe(c), tipo(idDe(bebe), idDe(c)), "elbow"] as Aresta),
    ...criDe.flatMap(c => ado.map(x => [idDe(c), idDe(x), tipo(idDe(c), idDe(x)), "elbow"] as Aresta)),
    ...ado.flatMap(x => aduDe(x.linha!).map((y, k) => [idDe(x) + "#" + k, idDe(y), tipo(idDe(x), idDe(y)), "reta"] as Aresta)),
    ...(v5 ? ado.flatMap(x => aduDe(x.linha!).map((y, k) => [idDe(y) + "#" + k, idDe(megaDe(x.linha!)), tipo(idDe(y), idDe(megaDe(x.linha!))), "reta"] as Aresta)) : []),
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
      provavel={!sombriaNo && idDe(g) === provId} sombriaNo={sombriaNo} sombriaAgora={m.sombria} sub={sub} escolher={setDet} v6={m.versao >= 6} />
  );
  return <>
    <div className="evo-arv" ref={arv} role="group" aria-label="Árvore de evolução">
      <svg className="evo-linhas" aria-hidden="true" width={linhas.w} height={linhas.h} viewBox={`0 0 ${linhas.w} ${linhas.h}`}>
        {linhas.d.map(([d, c], i) => <path key={i} className={`evo-aresta ${c}`} d={d} />)}
      </svg>
      <div className="evo-nivel evo-nivel--bebe">{no(bebe, "")}</div>
      <div className="evo-nivel evo-nivel--crianca">{cri.map(c => no(c, SUB_RAMO[c.ramo!]))}</div>
      <div className="evo-nivel evo-nivel--linhas">
        {ado.map(x => (
          <div className="evo-coluna" key={x.linha}>
            {no(x, CAT.adolescente[x.linha!].eixo)}
            {aduDe(x.linha!).map(y => no(y, NOME_ARQ[y.adulta!]))}
            {v5 && no(megaDe(x.linha!), "Mega")}
            {no(somDe(x.linha!), "sombria", true)}
          </div>
        ))}
      </div>
    </div>
    <ul className="evo-legenda" aria-label="Legenda da árvore">
      <li><span className="evo-mini percorrido" />percorrido</li><li><span className="evo-mini agora" />agora</li>
      <li><span className="evo-mini possivel" />possível</li><li><span className="evo-mini provavel" />se evoluísse agora</li>
      <li><span className="evo-mini fechado" />fechado</li><li><span className="evo-mini sombria" />sombria</li>
    </ul>
    {det ? <p className="dl-card evo-no-det" aria-live="polite">{det}</p> : <p className="dl-apoio" style={{ margin: 0 }}>Toque num nó para ver o que leva até ele.</p>}
  </>;
}

export function TelaEvolucao() {
  const { motor: m } = useJogo(), f = m.forma, evs = m.evolucoes, p = previsaoEvo(m), t = tamerAtual();
  /* pets v6: as medalhas do Tamer que a proxima evolucao pede (null nos v1-v5 e sem proxima evolucao) */
  const rMed = m.requisitosEvolucao()?.medalhas ?? null, faltaMed = !!rMed && !rMed.ok, prontoMed = !!m.esperandoMedalha();
  const espera = !!p && p.falta <= 0 && (f.est === "adolescente" || f.est === "adulto" || (f.est === "crianca" && faltaMed)), ult = evs[evs.length - 1];
  const rMega = f.est === "adulto" ? m.requisitosMega() : null;
  /* pets v4: alem das 10 lutas, a taxa de vitoria do adolescente precisa chegar a 80% */
  const taxa = m.taxaVitoria(), faltaTaxa = m.versao >= 4 && m.sparring >= CAT.sparring && (taxa ?? 0) < CLE.limiarTaxa;
  const det = (x: typeof evs[number]) => x.estagio === "mega" ? `vínculo ${virgula(x.vinculo!)}; ${x.sparring} lutas no Ultimate`
    : x.estagio === "crianca" ? `cuidado ${(x.cuidado! * 100).toFixed(0)}%`
    : x.estagio === "adolescente" ? `caráter: ${fmtCar(x.carater!)}` : `${NOME_ARQ[x.adulta!]}; caráter: ${fmtCar(x.carater!)}; ${x.sparring} lutas de treino`;
  /* o que falta, na espera (o tempo ja passou): as lutas e as vitorias do estagio, no Mega o vinculo e, nos pets v6, por
     ultimo as medalhas do Tamer */
  const med = (): string => { const fm = medalhasQueFaltam(t, rMed!.precisa); return fm.length === 1 ? `a ${fm[0].nome}` : `${rMed!.precisa - rMed!.tem} medalhas do Tamer`; };
  const falta = (): string => {
    if (rMega) return !rMega.lutas ? `${CAT.sparring - m.lutas.lutas} lutas` : !rMega.taxa ? `vitórias ${Math.round((taxa ?? 0) * 100)}% de ${Math.round(CLE.limiarTaxa * 100)}%`
      : !rMega.vinculo ? `vínculo ${virgula(m.vinc.valor)} de ${virgula(CMG.vinculo)}` : faltaMed ? med() : "";
    if (f.est === "crianca") return faltaMed ? med() : "";
    return m.sparring < CAT.sparring ? `${CAT.sparring - m.sparring} lutas` : faltaTaxa ? `vitórias ${Math.round((taxa ?? 0) * 100)}% de ${Math.round(CLE.limiarTaxa * 100)}%`
      : faltaMed ? med() : "";
  };
  const alvo = p ? nomeEstagio(p.prox) : "", cor = corDominante(m.tracos), arq = nomeArquetipo(f), br = BRASAO[m.especie], desk = useDesktop();
  return (
    <div className="tela dl desk evo-tela evt">
      <div className="evo-principal">
        {/* a forma atual em destaque: o pet na plataforma de luz, como no momento da evolucao */}
        <section className="evt-heroi" aria-label="Forma atual">
          <span className="evm-estilhacos" aria-hidden="true"><i /><i /><i /><i /></span>
          <div className="evt-heroi-palco">
            <span className="evm-plataforma evt-plataforma" aria-hidden="true"><i /><i /><i /></span>
            <span className="evt-heroi-pet"><PetGrande f={f} alvo={desk ? [210, 170] : [150, 130]} cor={cor} sombria={m.sombria} /></span>
          </div>
          <div className="evt-heroi-txt">
            <span className="evt-rot">forma atual</span>
            <b className="evt-nome">{nomeForma(f)}</b>
            <span className="evt-estagio">{nomeEstagio(f)}{arq ? ` · ${arq}` : ""}</span>
            <span className="evt-brasao"><Deco nome={br.peca} largura={30} altura={20} className="evm-brasao-img" />brasão {br.nome}</span>
            <span className="evt-prazo"><b>{p ? (espera ? falta() || "pronto" : duracao(Math.max(0, p.falta))) : "forma final"}</b>
              <small>{p ? (espera ? `falta para virar ${alvo}` : `até virar ${alvo}`) : "não há próxima evolução"}</small></span>
          </div>
        </section>
        <section className="evt-painel evt-arvore" aria-labelledby="evt-arv-tit">
          <h2 className="evt-tit" id="evt-arv-tit"><GitBranch size={18} aria-hidden="true" />Árvore de {br.nome}</h2>
          <Arvore m={m} p={p} />
        </section>
      </div>
      <div className="evo-lado">
        <section className="evt-painel evt-prox" aria-labelledby="evt-prox-tit">
          <h2 className="evt-tit" id="evt-prox-tit"><Sparkles size={18} aria-hidden="true" />{p ? `Próxima evolução: ${alvo}` : "Forma final"}</h2>
          {rMed && (
            <div className="evt-selos" aria-label={`medalhas do Tamer: ${rMed.tem} de ${rMed.precisa}`}>
              {Array.from({ length: rMed.precisa }, (_, k) => <SeloMedalha key={k} n={k + 1} ganha={k < rMed.tem} tam={26} />)}
              <span>{rMed.tem} de {rMed.precisa} medalhas do Tamer</span>
            </div>
          )}
          {faltaMed && <p className={`evo-medalha${prontoMed ? " pronto" : ""}`} role="status">{prontoMed ? <b>Pronto para evoluir. </b> : null}{textoFalta(t, rMed!.precisa)}</p>}
          <Numeros itens={[
            ...(m.versao >= 4 ? [["experiência de combate: cada vitória o deixa mais preciso na luta",
              `${m.vitoriasVida} ${m.vitoriasVida === 1 ? "vitória" : "vitórias"}${m.vitoriasVida * CLE.expPorVitoria >= CLE.expMax ? " (máximo)" : ""}`] as [string, string]] : []),
            ...(m.versao >= 4 && (f.est === "adolescente" || rMega) ? [["vitórias nas lutas deste estágio (precisa de 80% para evoluir)",
              m.lutas.lutas ? `${m.lutas.vitorias} de ${m.lutas.lutas}` : "nenhuma luta"] as [string, string]] : []),
            /* a forma futura ainda nao foi decidida pelo motor: mostra so o porque, sem o nome */
            [p ? `se evoluísse agora: ${p.porque}` : `passiva: ${DESC_PASSIVA[f.adulta!]}`, p ? (p.prox.est === "mega" ? nomeForma(p.prox) : "?") : NOME_ARQ[f.adulta!]],
          ]} />
        </section>
        {ult && <section className="evt-painel revel-porque evt-porque"><h2 className="evt-tit"><Info size={18} aria-hidden="true" />Por que {nomeForma(f)}?</h2><Porque x={ult} /></section>}
        <section className="evt-painel evt-hist" aria-labelledby="evt-hist-tit">
          <h2 className="evt-tit" id="evt-hist-tit"><History size={18} aria-hidden="true" />Histórico</h2>
          <ol className="evo-hist evt-linha">
            <li><span className="evt-ponto" aria-hidden="true" /><span className="t">D1 {hhmm(TICK_INICIAL)}</span><span>nasceu: <b>{nomeForma({ esp: m.especie, est: "bebe" })}</b></span></li>
            {evs.map((x, i) => (
              <li key={i}><span className="evt-ponto evt-ponto--evo" aria-hidden="true" /><span className="t">D{diaDe(x.tick)} {hhmm(x.tick)}</span>
                <span>virou <b>{nomeForma(x.forma)}</b> ({det(x)})</span>
                <button type="button" className="evt-rever" aria-label={`Ver a revelação de novo: ${nomeForma(x.forma)}`} onClick={() => reverEvolucao(i)}>Ver a revelação de novo</button></li>
            ))}
          </ol>
        </section>
        <section className="evt-painel evt-como">
          <p className="evo-selo"><Deco nome={br.peca} className="evo-selo-img" /><span>brasão <b>{br.nome}</b>: as formas da árvore são as deste brasão.</span></p>
          <p style={{ margin: 0 }}>Cada evolução é decidida pelo que o pet viveu: cuidado, caráter e lutas de treino.</p>
          <details className="dl-apoio"><summary>Como funciona</summary>
            <p>Uma moeda por transição (os contadores zeram a cada evolução). <b>In-Training → Rookie</b> ({m.dur.bebe / 60} h): o <b>cuidado</b> decide o ramo; o In-Training chama em horário fixo (fome a cada 30 min, higiene a cada 60, carinho a cada 45) e atender pelo menos 80% dos chamados em até 15 min dá Sereno, menos dá Arisco. <b>Rookie → Champion</b> ({m.dur.crianca / 60} h): o <b>caráter dominante</b> decide a linha e a técnica. <b>Champion → Ultimate</b> ({m.dur.adolescente / 60} h e 10 lutas de treino na arena): o <b>eixo complementar</b> da linha decide o arquétipo e a passiva (as duas formas da linha são o mesmo Ultimate).{m.versao >= 5 ? <> <b>Ultimate → Mega</b> ({m.dur.adulto / 60} h, {CAT.sparring} lutas com {CLE.limiarTaxa * 100}% ou mais de vitórias e vínculo {virgula(CMG.vinculo)} ou mais): o mesmo arquétipo, mais forte. A forma sombria não chega ao Mega.</> : " Pets de versões antigas param no Ultimate."}{m.versao >= 6 ? <> Além disso, cada evolução depois do Rookie pede <b>medalhas do Tamer</b>: {CMD.adolescente} para virar Champion, {CMD.adulto} para Ultimate e {CMD.mega} para Mega. Se o pet cumpre o resto e falta medalha, ele espera pronto e evolui assim que você ganhar a medalha.</> : ""} Caráter: quanto os traços do pet estão acima de um pet comum em cada eixo.</p>
          </details>
        </section>
      </div>
    </div>
  );
}
