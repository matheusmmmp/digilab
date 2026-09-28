/* Revelacao da evolucao (desenho UpEvolucao): so evolucoes novas nesta sessao abrem a revelacao; o save antigo
   nao reabre as dele. O "por que" vem so do que o motor registrou na evolucao. */
import { useEffect, useRef, useState } from "preact/hooks";
import {
  CAT, CSO, NOME_EST, SOMBRIA, chaveSprite, nomeEstagio, nomeForma, type Evolucao, type Motor,
} from "../../motor/index.ts";
import { desenharSprite, quadroAgora, useAtlas } from "../atlas.ts";
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
function Palco({ x }: { x: Evolucao }) {
  const a = useAtlas(), ref = useRef<HTMLCanvasElement>(null), k = chaveSprite(x.forma);
  const sp = a.tipo === "ok" ? a.dados.sprites[k] : null;
  const esc = sp ? Math.max(1, Math.min(4, Math.floor((Math.min(innerWidth, 480) - 56) / sp.caixa[0]), Math.floor(260 / sp.caixa[1]))) : 1;
  useEffect(() => {
    const cv = ref.current; if (!cv || a.tipo !== "ok" || !sp) return;
    const g = cv.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
    const desenha = () => { g.clearRect(0, 0, cv.width, cv.height); desenharSprite(g, a, k, esc, esc, esc, quadroAgora(a, k), { sombria: !!SOMBRIA[x.forma.adulta!] }); };
    desenha();
    const t = setInterval(desenha, a.dados.ms_por_quadro);
    return () => clearInterval(t);
  }, [a, k]);
  return <div class="revel-palco">{sp && <canvas class="dl-pix" ref={ref} width={(sp.caixa[0] + 2) * esc} height={(sp.caixa[1] + 2) * esc} />}</div>;
}
function Revelacao({ x, m, fechar }: { x: Evolucao; m: Motor; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), f = x.forma, i = ORDEM_NIVEL.indexOf(x.estagio);
  useEffect(() => { ref.current?.showModal(); }, []);
  /* linha ja percorrida: os Digimon que o pet foi (so o que o motor registrou) */
  const passados = [nomeForma({ esp: f.esp, est: "bebe" }), ...m.evolucoes.map(v => nomeForma(v.forma))];
  return (
    <dialog class="revelacao dl" ref={ref} aria-labelledby="revel-tit" onClose={fechar}>
      <div class="revel-fundo">
        <p class="revel-de dl-lcd">{NOME_EST[ORDEM_NIVEL[i - 1]] || ""} → {nomeEstagio(f)}</p>
        <h2 class="dl-num revel-tit" id="revel-tit">EVOLUÇÃO!</h2>
        <Palco x={x} />
        <span class="dl-placa">{nomeForma(f)}</span>
        <ol class="revel-linha">{ORDEM_NIVEL.map((n, j) => <li key={n} aria-current={j === i ? "step" : undefined}>{j <= i ? passados[j] : "?"}</li>)}</ol>
        <section class="dl-card revel-porque"><h3 class="dl-titulo-card">Por que {nomeForma(f)}?</h3><Porque x={x} /></section>
        <button type="button" class="dl-btn dl-btn--destaque revel-ok" onClick={() => ref.current?.close()}>Continuar</button>
      </div>
    </dialog>
  );
}
/** acompanha as evolucoes: abre a revelacao quando o motor registra uma nova nesta sessao */
export function RevelacaoEvolucao() {
  const { motor: m } = useJogo(), vistas = useRef<{ motor: Motor; n: number } | null>(null), [aberta, setAberta] = useState<Evolucao | null>(null);
  useEffect(() => {
    const n = m.evolucoes.length;
    /* pet trocado (ovo novo, pet anterior, outra aba): comeca a contar dele */
    if (!vistas.current || vistas.current.motor !== m || n < vistas.current.n) { vistas.current = { motor: m, n }; return; }
    if (n > vistas.current.n) { vistas.current.n = n; setAberta(m.evolucoes[n - 1]); }
  });
  return aberta ? <Revelacao x={aberta} m={m} fechar={() => setAberta(null)} /> : null;
}
