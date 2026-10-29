/* O momento da evolucao (docs/TAREFA_V2_EVOLUCAO.md; a quinta tela da referencia, decisao do Matheus de 2026-10-21): tela cheia azul com a
   grade e os estilhacos em CSS, "EVOLUCAO!" e "Rookie -> Champion", o pet grande e nitido na plataforma de luz, o cartao com o nome e o
   estagio, e embaixo o "de -> para", o que decidiu e as medalhas que a evolucao pediu. So evolucoes novas nesta sessao abrem sozinhas (o
   save antigo nao reabre as dele); o historico de Crescer · Evolucao reabre qualquer uma (reverEvolucao). Tudo vem do que o motor
   registrou na evolucao e no registro do pet. */
import { useEffect, useRef, useState } from "react";
import {
  CAT, CLE, CMD, CMG, CSO, MEDALHA_POR_ID, NOME_EST, SOMBRIA, chaveSprite, corDominante, nomeArquetipo, nomeEstagio, nomeForma,
  type Evolucao, type Forma, type Motor, type TracoCombate,
} from "../../motor/index.ts";
import { desenharSprite, quadroAgora, useAtlas } from "../atlas.ts";
import { BRASAO } from "../decoracao.ts";
import { S, gradeDe, imagemGrade, paleta } from "../grades.ts";
import { Deco } from "./Deco.tsx";
import { SeloMedalha } from "./Medalha.tsx";
import { abrirModal, rotaDaTelaCheia } from "./modal.ts";
import { ehLuta } from "../rotas.ts";
import { SOM } from "../som.ts";
import { useLuta } from "../luta.ts";
import { tamerAtual, useJogo } from "../jogo.ts";
import { BarraCarater, Seg, blocos } from "./Barras.tsx";

export function Porque({ x }: { x: Evolucao }) {
  if (x.estagio === "mega") return <>
    <p style={{ margin: 0 }}>a mesma forma, mais forte: decidido pelo <b>vínculo</b> {x.vinculo!.toFixed(2).replace(".", ",")} (mínimo {String(CMG.vinculo).replace(".", ",")})
      e por {x.sparring} lutas no Ultimate com {CLE.limiarTaxa * 100}% ou mais de vitórias.</p>
    <Seg n={blocos(x.vinculo!, 10)} m={10} cls="dl-seg--acao" marca={CMG.vinculo * 10} />
    <span className="dl-apoio">traço escuro = vínculo mínimo para o Mega</span>
  </>;
  if (x.estagio === "crianca") return <>
    <p style={{ margin: 0 }}>decidido pelo <b>cuidado</b> no In-Training: {(x.cuidado! * 100).toFixed(0)}% dos chamados atendidos a tempo (limite {CAT.limiarCuidado * 100}%).</p>
    <Seg n={blocos(x.cuidado!, 10)} m={10} cls="dl-seg--acao" marca={CAT.limiarCuidado * 10} />
    <span className="dl-apoio">traço escuro = limite de {CAT.limiarCuidado * 100}%</span>
  </>;
  if (x.estagio === "adolescente") {
    const eixo = CAT.adolescente[x.linha!].eixo;
    return <>
      <p style={{ margin: 0 }}>decidido pelo caráter <b>{eixo}</b>, o eixo mais alto ao fim do Rookie.</p>
      {Object.entries(x.carater!).map(([k, v]) => <BarraCarater key={k} eixo={k} v={v} />)}
      <span className="dl-apoio">traço escuro = pet comum</span>
    </>;
  }
  const somb = SOMBRIA[x.adulta!], lin = somb ? somb.linha : x.forma.linha!, comp = CAT.adulto[lin].comp;
  return <>
    {somb && <p style={{ margin: 0 }}><span className="dl-tag dl-tag--sombria">sombria</span> sobrecarga {x.sobrecarga!.toFixed(0)} na virada (limite {CSO.sombrio}).</p>}
    <p style={{ margin: 0 }}>decidido pelo eixo complementar <b>{comp}</b> e {x.sparring} lutas de treino.</p>
    <BarraCarater eixo={comp} v={x.carater![comp]} />
    <span className="dl-apoio">traço escuro = pet comum</span>
  </>;
}

/** a forma de antes da evolucao i: a da evolucao anterior, ou o In-Training na primeira (o motor registra so a forma nova) */
export function formaAntes(m: Motor, i: number): Forma {
  return i > 0 ? m.evolucoes[i - 1].forma : { esp: m.especie, est: "bebe" };
}
/** pets v6: as medalhas do Tamer que a evolucao pediu (CMD) e, so quando a derivacao e exata, a que a liberou: a evolucao caiu no tick
    de um evento "u" que levou o pet de uma medalha a menos para o numero pedido (ele esperava pronto), e a medalha e a de numero n do
    Tamer. null nos pets v1-v5 e nas evolucoes que nao pedem medalha */
export function medalhasDaEvolucao(m: Motor, x: Evolucao): { pediu: number; liberou: string | null } | null {
  const pediu = m.versao >= 6 ? (CMD as Partial<Record<string, number>>)[x.estagio] ?? 0 : 0;
  if (!pediu) return null;
  let antes = 0, liberou: string | null = null;
  for (const ev of m.log) {
    if (ev[1] !== "u") continue;
    const t = ev[0] as number, n = (ev[2] as { n: number }).n;
    if (t > x.tick) break;
    if (t === x.tick && n === pediu && antes === pediu - 1) {
      const md = tamerAtual().medalhas.find(g => g.n === n);
      liberou = md ? MEDALHA_POR_ID[md.id]?.nome ?? null : null;
    }
    antes = n;
  }
  return { pediu, liberou };
}

/** o pet de uma forma em escala inteira, ate caber em alvo (px de CSS): o idle do atlas do UP animado ou, sem ele (o CI, as capturas do
    repositorio), a grade de pixels de reserva com a cor do pet. Nitido nos dois: so escala inteira, sem suavizar */
export function PetGrande({ f, alvo, cor, sombria = false, maxEscala = 6 }: { f: Forma; alvo: [number, number]; cor: TracoCombate; sombria?: boolean; maxEscala?: number }) {
  const a = useAtlas(), ref = useRef<HTMLCanvasElement>(null), k = chaveSprite(f);
  const sp = a.tipo === "ok" ? a.dados.sprites[k] ?? null : null;
  const esc = sp ? Math.max(1, Math.min(maxEscala, Math.floor(alvo[0] / (sp.caixa[0] + 2)), Math.floor(alvo[1] / (sp.caixa[1] + 2)))) : 1;
  useEffect(() => {
    const cv = ref.current; if (!cv || a.tipo !== "ok" || !sp) return;
    const g = cv.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
    const desenha = () => { g.clearRect(0, 0, cv.width, cv.height); desenharSprite(g, a, k, esc, esc, esc, quadroAgora(a, k), { sombria }); };
    desenha();
    const t = setInterval(desenha, a.dados.ms_por_quadro);
    return () => clearInterval(t);
  }, [a, k, esc, sombria]);
  if (sp) return <canvas className="dl-pix evm-spr" ref={ref} width={(sp.caixa[0] + 2) * esc} height={(sp.caixa[1] + 2) * esc} aria-hidden="true" />;
  const grade = S[gradeDe(f.est)];
  const e = Math.max(1, Math.min(maxEscala * 2, Math.floor(alvo[0] / grade[0].length), Math.floor(alvo[1] / grade.length)));
  const img = imagemGrade(grade, e, paleta(cor));
  return <img className="dl-pix evm-spr evm-spr--reserva" src={img.url} width={img.w} height={img.h} alt="" />;
}
/** o pet pequeno do "de -> para" */
function Mini({ f, cor }: { f: Forma; cor: TracoCombate }) {
  return <span className="evm-mini"><PetGrande f={f} alvo={[56, 56]} cor={cor} maxEscala={2} /></span>;
}

const DECIDIDO: Record<string, string> = { crianca: "o cuidado", adolescente: "o caráter", adulto: "o caráter e o treino", mega: "o vínculo e as vitórias" };
/** a revelacao da evolucao i do pet (tela cheia, por cima de tudo, tambem no desktop) */
function Revelacao({ i, m, fechar }: { i: number; m: Motor; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), x = m.evolucoes[i], f = x.forma, antes = formaAntes(m, i), cor = corDominante(m.tracos);
  const med = medalhasDaEvolucao(m, x), arq = nomeArquetipo(f), br = BRASAO[m.especie], largo = matchMedia("(min-width: 900px)").matches;
  /* abre no topo (o foco inicial iria para o Continuar, embaixo, e rolaria a tela) */
  useEffect(() => { const d = ref.current; if (!d) return; abrirModal(d); d.scrollTop = 0; d.querySelector<HTMLElement>(".revel-tit")?.focus(); }, []);
  useEffect(() => rotaDaTelaCheia("#/evolucao"), []);
  /* so apresentacao: o efeito da evolucao (src/som.ts; desligado por padrao); a revelacao daqui e imediata, entao a queda cai no começo */
  useEffect(() => { void SOM.tocarEvolucao(0); return () => SOM.pararEvolucao(); }, []);
  return (
    <dialog className="revelacao evm dl" ref={ref} aria-labelledby="revel-tit" onClose={fechar}>
      <span className="evm-estilhacos" aria-hidden="true"><i /><i /><i /><i /></span>
      <div className="evm-corpo">
        <div className="evm-palco">
          <div className="evm-topo">
            <span className="revel-de">{NOME_EST[antes.est]} → {nomeEstagio(f)}</span>
            <h2 className="dl-num revel-tit evm-tit" id="revel-tit" tabIndex={-1}>EVOLUÇÃO!</h2>
          </div>
          <div className="evm-cena">
            <span className="evm-raio" aria-hidden="true" />
            <Deco nome="UI_Fx_Glow_Circle_01" largura={320} altura={320} className="evm-glow" />
            <Deco nome="Digivice_Circle_01" largura={300} altura={300} className="evm-digivice dl-gira" />
            <span className="evm-plataforma" aria-hidden="true"><i /><i /><i /></span>
            <span className="evm-pet"><PetGrande f={f} alvo={largo ? [340, 300] : [250, 220]} cor={cor} sombria={!!SOMBRIA[f.adulta!]} /></span>
          </div>
          <div className="evm-cartao">
            <b className="evm-nome">{nomeForma(f)}</b>
            <span className="evm-estagio">{nomeEstagio(f)}{arq ? ` · ${arq}` : ""}</span>
            <span className="evm-brasao"><Deco nome={br.peca} largura={30} altura={20} className="evm-brasao-img" />brasão {br.nome}</span>
          </div>
        </div>
        <div className="evm-detalhes">
          <section className="evm-bloco evm-depara" aria-label={`De ${nomeForma(antes)} para ${nomeForma(f)}`}>
            <span className="evm-forma"><Mini f={antes} cor={cor} /><span><b>{nomeForma(antes)}</b><small>{nomeEstagio(antes)}</small></span></span>
            <span className="evm-seta" aria-hidden="true">→</span>
            <span className="evm-forma"><Mini f={f} cor={cor} /><span><b>{nomeForma(f)}</b><small>{nomeEstagio(f)}</small></span></span>
          </section>
          <section className="evm-bloco revel-porque">
            <span className="revel-porque-cab"><b>O que decidiu</b><span>{DECIDIDO[x.estagio]}</span></span>
            <Porque x={x} />
          </section>
          {med && (
            <section className="evm-bloco evm-medalhas">
              <span className="evm-selos" aria-hidden="true">{Array.from({ length: med.pediu }, (_, k) => <SeloMedalha key={k} n={k + 1} ganha tam={22} />)}</span>
              <p>Esta evolução pediu {med.pediu === 1 ? "1 medalha" : `${med.pediu} medalhas`} do Tamer.{med.liberou ? <> Foi liberada pela <b>{med.liberou}</b>.</> : null}</p>
            </section>
          )}
          <button type="button" className="dl-btn evm-continuar revel-ok" onClick={() => ref.current?.close()}>Continuar</button>
        </div>
      </div>
    </dialog>
  );
}

/* contagem das evolucoes ja vistas e a revelacao pendente ficam fora do componente: a luta em tela cheia desmonta o app
   (e esta revelacao) e, quando a luta faz o pet evoluir, a revelacao espera o fim da luta e o Resultado */
const VISTAS: { motor: Motor | null; n: number; pendente: number | null } = { motor: null, n: 0, pendente: null };
const ouvintes = new Set<() => void>();
/** reabre a revelacao da evolucao i do pet de agora (o historico de Crescer · Evolucao) */
export function reverEvolucao(i: number): void {
  VISTAS.pendente = i;
  for (const o of ouvintes) o();
}
/** acompanha as evolucoes: abre a revelacao quando o motor registra uma nova nesta sessao; Continuar leva a Crescer · Evolucao */
export function RevelacaoEvolucao({ continuar }: { continuar?: () => void }) {
  const jogo = useJogo(), { motor: m } = jogo, luta = useLuta(), [, redesenhar] = useState(0);
  useEffect(() => { const o = () => redesenhar(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  useEffect(() => {
    const n = m.evolucoes.length;
    /* pet trocado (ovo novo, pet anterior, outra aba): comeca a contar dele; se ele evoluiu ao receber as medalhas do Tamer
       na troca (pet guardado que estava pronto), a revelacao mostra essa evolucao */
    if (VISTAS.motor !== m || n < VISTAS.n) {
      VISTAS.motor = m; VISTAS.pendente = null; VISTAS.n = jogo.evolucoesAoTrocar ?? n; jogo.evolucoesAoTrocar = null;
      if (VISTAS.n >= n) return;
    }
    if (n > VISTAS.n) { VISTAS.n = n; VISTAS.pendente = n - 1; redesenhar(x => x + 1); }
  });
  const i = VISTAS.pendente;
  if (i === null || !m.evolucoes[i] || luta.lutando || ehLuta(location.hash)) return null;
  return <Revelacao key={i} i={i} m={m} fechar={() => { VISTAS.pendente = null; redesenhar(x => x + 1); continuar?.(); }} />;
}
