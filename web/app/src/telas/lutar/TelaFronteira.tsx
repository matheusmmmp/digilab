/* Lutar · Fronteira (docs/DESIGN_FRONTEIRA.md, secoes 2 e 5; medalhas parte 4a; so pets v6): a Liga dos Lideres. Os 6 lideres com os
   Megas deles, na ordem das lutas; as regras da Liga; a ultima tentativa (ate que luta chegou e a vida que sobrou em cada uma, refeitas
   do registro); o titulo do Tamer; e o botao de desafiar (a luta em tela cheia, #/lutar/luta). Tudo do motor (motor/liga.ts,
   Motor.liga, o evento de luta da Liga) e do registro do Tamer (o evento "campeao").
   Depois do titulo (medalhas parte 4b, motor/instalacoes.ts), as instalacoes: a Torre de Batalha e o Palacio, cada uma com a regra em uma
   frase, o recorde do Tamer (o evento "recorde"), as tentativas deste pet (Motor.instalacoes) e "Tentar" (a luta em tela cheia).
   E (medalhas parte 4c) a Fabrica e o Salao, com a escolha dos alugados e dos pets de cada nivel no proprio card (FabricaSalao.tsx). */
import { useEffect, useMemo } from "react";
import {
  INSTALACOES, LIGA, MEDALHAS_LIGA, NOME_ARQ, NOME_ESP, NOME_V2, NPC, RIVAL_LIGA, LUGARES_V6, MEDALHA_POR_ID, chaveSprite, formaLiga, nomeMegaLiga,
  type Instalacao, type Motor, duracaoLuta } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { LUTA, lutarInstalacao, lutarLiga, previa, reconstruirLuta, useLuta } from "../../luta.ts";
import { ENDERECO_LUTA } from "../../rotas.ts";
import { textoFalta, type Tamer } from "../../tamer.ts";
import { diaDe } from "../pet/TelaPet.tsx";
import { CartaoFabrica, CartaoSalao } from "./FabricaSalao.tsx";

/** a ultima tentativa da Liga no registro do pet (null: nenhuma): as lutas jogadas (o pet no fim de cada uma) e o indice do evento */
function ultimaTentativa(m: Motor): { idx: number; lutas: { venceu: boolean; vida: number; dur: string }[] } | null {
  let idx = -1;
  for (let i = m.log.length - 1; i >= 0; i--) { const ev = m.log[i]; if (ev[1] === "l" && ev[2].r === RIVAL_LIGA) { idx = i; break; } }
  if (idx < 0) return null;
  const L = reconstruirLuta(m, idx);
  return { idx, lutas: L.serie.map(r => ({ venceu: r.pontosA === 1, vida: Math.max(0, r.E.L[0].hp) / r.E.L[0].hpMax, dur: duracaoLuta(r) })) };
}
const pct = (x: number): string => `${Math.round(x * 100)}%`;
const vitorias = (n: number): string => `${n} vitória${n === 1 ? "" : "s"}`;

/** uma instalacao da Fronteira: a regra em uma frase, o recorde do Tamer, o que este pet fez nela e "Tentar". Antes do titulo, trancada */
function CartaoInstalacao({ x, m, t, lutando }: { x: Instalacao; m: Motor; t: Tamer; lutando: boolean }) {
  const erro = m.porqueNaoInstalacao(x.id), rec = t.recorde(x.id), c = m.instalacoes[x.id];
  const tentar = () => { lutarInstalacao(x.id); if (LUTA.lutando) location.hash = ENDERECO_LUTA; };
  return (
    <li className={`dl-card fr-inst-card${t.titulo ? "" : " fr-inst-card--fechada"}`} aria-labelledby={`fr-inst-${x.id}`}>
      <span className="fr-inst-cab">
        <b className="fr-inst-nome" id={`fr-inst-${x.id}`}>{x.nome}</b>
        <span className="fr-inst-rec" aria-label={`recorde do Tamer: ${vitorias(rec?.valor ?? 0)}`}><span className="dl-num">{rec?.valor ?? 0}</span><small>recorde</small></span>
      </span>
      <span className="fr-inst-frase">{x.frase}</span>
      <span className="fr-inst-quem">{rec ? `Recorde do Tamer: ${vitorias(rec.valor)} seguidas, com ${rec.forma}, no dia ${diaDe(rec.tick)}.` : t.titulo ? "Sem recorde ainda: a primeira vitória já é um." : "Abre depois do título da Liga dos Líderes."}</span>
      {c && c.tentativas > 0 && <span className="fr-inst-pet">Este pet: {c.tentativas} tentativa{c.tentativas === 1 ? "" : "s"}, melhor {c.recorde}, última {c.ultima} (vitórias seguidas).</span>}
      {t.titulo && erro && <span className="dl-apoio">Agora não dá para entrar: {erro}.</span>}
      <button type="button" className="dl-btn fr-inst-tentar" disabled={!!erro || lutando} onClick={tentar}>{c && c.tentativas ? "Tentar de novo" : "Tentar"}</button>
    </li>
  );
}

export function TelaFronteira() {
  const { motor: m, erroTamer } = useJogo(), luta = useLuta(), a = useAtlas(), t = tamerAtual();
  useEffect(() => { if (!LUTA.lutando && (!LUTA.palco || LUTA.palco.modo !== "fronteira")) previa("fronteira"); }, []);
  const erro = m.porqueNaoLiga();
  const nLiga = m.liga.tentativas;
  /* a ultima tentativa, refeita do registro (so muda com luta nova da Liga) */
  const ult = useMemo(() => (nLiga ? ultimaTentativa(m) : null), [nLiga, m.semente]);
  const img = (k: string, cls: string) => { if (a.tipo !== "ok") return null; const i = imagemAtlas(a, k); return <img className={`dl-pix ${cls}`} src={i.url} width={i.w} height={i.h} alt="" />; };
  const titulo = t.titulo, meu = t.tituloDe(m.semente), parou = ult ? ult.lutas.length : 0, venceuUlt = !!ult && ult.lutas.length === LIGA.length && ult.lutas[LIGA.length - 1].venceu;
  const desafiar = () => { lutarLiga(); if (LUTA.lutando) location.hash = ENDERECO_LUTA; };
  return (
    <div className="tela dl fr-tela">
      <div className="fr-lado">
        <section className="dl-card fr-cab" aria-labelledby="fr-tit">
          <h2 id="fr-tit">Liga dos Líderes</h2>
          <p>Os {LIGA.length} líderes das arenas, um depois do outro, cada um com um Mega de outro arquétipo. Vencer os {LIGA.length} faz de você o <b>Campeão</b>.</p>
          <ul className="fr-regras" aria-label="Regras da Liga">
            <li><b>Sem cura</b> entre as lutas: a vida e o guts passam de uma para a outra.</li>
            <li>Os <b>chips</b> equipados valem; as <b>cartas</b> não valem.</li>
            <li>No limite de tempo, a luta fica com o <b>líder</b>.</li>
            <li>Perder uma luta encerra a tentativa. Tentar de novo não custa nada.</li>
          </ul>
          {erroTamer && <p className="med-erro" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
          {titulo
            ? <div className={`fr-titulo${meu ? " meu" : ""}`} role="status"><SeloMedalha n={0} ouro ganha tam={40} />
                <span><b>Campeão da Liga</b><span>{meu ? `${meu.forma} venceu os ${LIGA.length} no dia ${diaDe(meu.tick)}.` : `O título é seu desde ${titulo.forma}, no dia ${diaDe(titulo.tick)}.`}</span></span></div>
            : null}
          {m.medalhas < MEDALHAS_LIGA
            ? <p className="med-espera" role="status"><b>A Fronteira abre com as {MEDALHAS_LIGA} medalhas.</b> {textoFalta(t, MEDALHAS_LIGA)}</p>
            : erro ? <p className="dl-apoio">Agora não dá para desafiar a Liga: {erro}.</p> : null}
          {nLiga > 0 && <p className="fr-conta"><span><b className="dl-num">{nLiga}</b> tentativa{nLiga === 1 ? "" : "s"}</span><span><b className="dl-num">{m.liga.titulos}</b> título{m.liga.titulos === 1 ? "" : "s"}</span></p>}
          {ult && <p className="fr-ultima" role="status">{venceuUlt
            ? `Última tentativa: venceu os ${LIGA.length}, e terminou com ${pct(ult.lutas[LIGA.length - 1].vida)} da vida.`
            : `Última tentativa: parou na luta ${parou} de ${LIGA.length}, contra ${nomeMegaLiga(parou - 1)} de ${NPC[LIGA[parou - 1].lider]!.nome}.`}</p>}
        </section>
        <button type="button" className="dl-btn fr-lutar" disabled={!!erro || luta.lutando} onClick={desafiar}>
          {nLiga ? "Tentar a Liga de novo" : "Desafiar a Liga"} ({LIGA.length} lutas seguidas)</button>
        <section className="fr-inst" aria-labelledby="fr-inst-tit">
          <h2 id="fr-inst-tit">Instalações</h2>
          <p className="dl-apoio">{t.titulo ? "Para rejogar por recorde: nada daqui deixa o pet mais forte fora da Fronteira." : "Abrem depois do título da Liga dos Líderes, para rejogar por recorde."}</p>
          <ul className="fr-inst-lista">
            {INSTALACOES.map(x => <CartaoInstalacao key={x.id} x={x} m={m} t={t} lutando={luta.lutando} />)}
            <CartaoFabrica t={t} lutando={luta.lutando} />
            <CartaoSalao t={t} lutando={luta.lutando} />
          </ul>
        </section>
      </div>
      <ol className="fr-lista" aria-label="Os líderes da Liga, na ordem das lutas">
        {LIGA.map((x, i) => {
          const f = formaLiga(i), lider = NPC[x.lider]!, md = MEDALHA_POR_ID[x.arena], r = ult?.lutas[i];
          const st = !ult ? null : r ? (r.venceu ? "vit" : "der") : "nao";
          return (
            <li key={x.arena} className={`fr-card${st ? " fr-card--" + st : ""}`}>
              <span className="fr-num dl-num" aria-hidden="true">{i + 1}</span>
              <span className="fr-sprs">{img(lider.sprite ?? lider.k, "fr-lider")}{img(chaveSprite(f), "fr-mega")}</span>
              <span className="fr-txt">
                <b className="fr-nome">Luta {i + 1}: {lider.nome} <span>· {LUGARES_V6[md.lugar].nome}</span></b>
                <span className="fr-mega-txt">luta com <b>{nomeMegaLiga(i)}</b> (Mega)</span>
                <span className="fr-tags"><span className="dl-tag fr-tag-arq">{NOME_ARQ[x.adulta]}</span><span className="dl-tag fr-tag-esp">{NOME_ESP[x.esp]}</span></span>
                {st && <span className={`fr-st fr-st--${st}`}>{r ? `${r.venceu ? "venceu" : "perdeu"} em ${r.dur} · ${pct(r.vida)} da vida no fim` : "não chegou a lutar"}</span>}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
