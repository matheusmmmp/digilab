/* Revelacao da evolucao (desenho UpEvolucao): so evolucoes novas nesta sessao abrem a revelacao; o save antigo
   nao reabre as dele. O "por que" vem so do que o motor registrou na evolucao. */
import { useEffect, useRef, useState } from "preact/hooks";
import {
  CAT, CSO, NOME_EST, SOMBRIA, chaveSprite, nomeEstagio, nomeForma, type Evolucao, type Forma, type Motor,
} from "../../motor/index.ts";
import { desenharSprite, imagemAtlas, quadroAgora, useAtlas } from "../atlas.ts";
import { Deco } from "./Deco.tsx";
import { abrirModal } from "./modal.ts";
import { useJogo } from "../jogo.ts";
import { BarraCarater, Seg, blocos } from "./Barras.tsx";

const ORDEM_NIVEL = ["bebe", "crianca", "adolescente", "adulto"] as const;
export function Porque({ x }: { x: Evolucao }) {
  if (x.estagio === "crianca") return <>
    <p style={{ margin: 0 }}>decidido pelo <b>cuidado</b> no In-Training: {(x.cuidado! * 100).toFixed(0)}% dos chamados atendidos a tempo (limite {CAT.limiarCuidado * 100}%).</p>
    <Seg n={blocos(x.cuidado!, 10)} m={10} cls="dl-seg--acao" marca={CAT.limiarCuidado * 10} />
    <span class="dl-apoio">traço escuro = limite de {CAT.limiarCuidado * 100}%</span>
  </>;
  if (x.estagio === "adolescente") {
    const eixo = CAT.adolescente[x.linha!].eixo;
    return <>
      <p style={{ margin: 0 }}>decidido pelo caráter <b>{eixo}</b>, o eixo mais alto ao fim do Rookie.</p>
      {Object.entries(x.carater!).map(([k, v]) => <BarraCarater key={k} eixo={k} v={v} />)}
      <span class="dl-apoio">traço escuro = pet comum</span>
    </>;
  }
  const somb = SOMBRIA[x.adulta!], lin = somb ? somb.linha : x.forma.linha!, comp = CAT.adulto[lin].comp;
  return <>
    {somb && <p style={{ margin: 0 }}><span class="dl-tag dl-tag--sombria">sombria</span> sobrecarga {x.sobrecarga!.toFixed(0)} na virada (limite {CSO.sombrio}).</p>}
    <p style={{ margin: 0 }}>decidido pelo eixo complementar <b>{comp}</b> e {x.sparring} lutas de treino.</p>
    <BarraCarater eixo={comp} v={x.carater![comp]} />
    <span class="dl-apoio">traço escuro = pet comum</span>
  </>;
}
/** o pet em escala inteira ate 4x (cabe em 224 px de altura, como o Greymon da prancha), animado no idle */
function Palco({ x }: { x: Evolucao }) {
  const a = useAtlas(), ref = useRef<HTMLCanvasElement>(null), k = chaveSprite(x.forma);
  const sp = a.tipo === "ok" ? a.dados.sprites[k] : null;
  const esc = sp ? Math.max(1, Math.min(4, Math.floor(260 / sp.caixa[0]), Math.floor(224 / sp.caixa[1]))) : 1;
  useEffect(() => {
    const cv = ref.current; if (!cv || a.tipo !== "ok" || !sp) return;
    const g = cv.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
    const desenha = () => { g.clearRect(0, 0, cv.width, cv.height); desenharSprite(g, a, k, esc, esc, esc, quadroAgora(a, k), { sombria: !!SOMBRIA[x.forma.adulta!] }); };
    desenha();
    const t = setInterval(desenha, a.dados.ms_por_quadro);
    return () => clearInterval(t);
  }, [a, k]);
  return sp ? <canvas class="dl-pix revel-spr dl-brilho-pet" ref={ref} width={(sp.caixa[0] + 2) * esc} height={(sp.caixa[1] + 2) * esc} /> : null;
}
/** um passo da linha evolutiva: o Digimon que ele foi (1x, cortado) ou "?" no que ainda nao foi decidido */
function Passo({ f, nivel, atual }: { f: Forma | null; nivel: string; atual: boolean }) {
  const a = useAtlas(), img = f && a.tipo === "ok" ? imagemAtlas(a, chaveSprite(f)) : null;
  return (
    <li class={`revel-passo${atual ? " atual" : ""}`} aria-current={atual ? "step" : undefined}>
      <span class="revel-passo-spr">{img ? <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt={nomeForma(f!)} /> : <b>?</b>}</span>
      <span>{nivel}{f ? "" : " ?"}</span>
    </li>
  );
}
const DECIDIDO: Record<string, string> = { crianca: "decidido pelo cuidado", adolescente: "decidido pelo caráter", adulto: "decidido pelo caráter e treino" };
/** revelacao (pranchas UpEvolucao e EvoCrianca; receita das DIRETRIZES_REPLICAR): tela cheia listrada, circulo de luz,
    anel do Digivice girando (parado com movimento reduzido), o pet ate 4x, a linha evolutiva e o porque */
function Revelacao({ x, m, fechar }: { x: Evolucao; m: Motor; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), f = x.forma, i = ORDEM_NIVEL.indexOf(x.estagio);
  /* abre no topo (o foco inicial iria para o Continuar, embaixo, e rolaria a tela) */
  useEffect(() => { const d = ref.current; if (!d) return; abrirModal(d); d.scrollTop = 0; d.querySelector<HTMLElement>(".revel-tit")?.focus(); }, []);
  /* linha ja percorrida: as formas que o pet foi (so o que o motor registrou) */
  const formas: Forma[] = [{ esp: f.esp, est: "bebe" }, ...m.evolucoes.map(v => v.forma)];
  return (
    <dialog class="revelacao revel-tela dl" ref={ref} aria-labelledby="revel-tit" onClose={fechar}>
      <div class="revel-topo">
        <span class="revel-de">{NOME_EST[ORDEM_NIVEL[i - 1]] || ""} → {nomeEstagio(f)}</span>
        <h2 class="dl-num dl-num--grande revel-tit" id="revel-tit" tabIndex={-1}>EVOLUÇÃO!</h2>
      </div>
      <div class="revel-cena">
        <span class="revel-luz" aria-hidden="true" />
        <Deco nome="UI_Fx_Glow_Circle_01" largura={300} altura={300} class="revel-glow" />
        <Deco nome="Digivice_Circle_01" largura={280} altura={280} class="revel-digivice dl-gira" />
        <span class="revel-anel" aria-hidden="true" />
        <Palco x={x} />
        <span class="dl-placa revel-nome">{nomeForma(f)}</span>
      </div>
      <ol class="revel-linha" aria-label="Linha evolutiva">
        {ORDEM_NIVEL.map((n, j) => <Passo key={n} f={j <= i ? formas[j] ?? null : null} nivel={NOME_EST[n]} atual={j === i} />)}
      </ol>
      <section class="revel-porque"><span class="revel-porque-cab"><b>Por que {nomeForma(f)}?</b><span>{DECIDIDO[x.estagio]}</span></span><Porque x={x} /></section>
      <button type="button" class="dl-btn dl-btn--destaque revel-ok" onClick={() => ref.current?.close()}>Continuar</button>
    </dialog>
  );
}
/** acompanha as evolucoes: abre a revelacao quando o motor registra uma nova nesta sessao */
/** revelacao em tela cheia (secao 7); Continuar leva a Crescer · Evolucao */
export function RevelacaoEvolucao({ continuar }: { continuar?: () => void }) {
  const { motor: m } = useJogo(), vistas = useRef<{ motor: Motor; n: number } | null>(null), [aberta, setAberta] = useState<Evolucao | null>(null);
  useEffect(() => {
    const n = m.evolucoes.length;
    /* pet trocado (ovo novo, pet anterior, outra aba): comeca a contar dele */
    if (!vistas.current || vistas.current.motor !== m || n < vistas.current.n) { vistas.current = { motor: m, n }; return; }
    if (n > vistas.current.n) { vistas.current.n = n; setAberta(m.evolucoes[n - 1]); }
  });
  return aberta ? <Revelacao x={aberta} m={m} fechar={() => { setAberta(null); continuar?.(); }} /> : null;
}
