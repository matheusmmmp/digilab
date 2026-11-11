/* Lutar · Fronteira (docs/DESIGN_FRONTEIRA.md, secoes 2 e 5; medalhas parte 4a): a Liga dos Lideres. Os 6 lideres com os Megas deles, na
   ordem das lutas; as regras da Liga; as contas das tentativas; o titulo do Tamer; e o botao de desafiar (a luta no palco da luta da POC, LP3).
   Tudo do motor (motor/liga.ts, Motor.liga, o evento de luta da Liga) e do registro do Tamer (o evento "campeao").
   Depois do titulo (medalhas parte 4b, motor/instalacoes.ts), as instalacoes: a Torre de Batalha (o Palacio juntou-se a ela, LP-5), com a
   regra em uma frase, o recorde do Tamer (o evento "recorde"), as tentativas deste pet (Motor.instalacoes) e "Tentar" (no palco novo).
   E (medalhas parte 4c) a Fabrica e o Salao, com a escolha dos alugados e dos pets de cada nivel no proprio card (FabricaSalao.tsx). */
import { useState } from "react";
import {
  INSTALACOES, LIGA, MEDALHAS_LIGA, NOME_ARQ, NOME_ESP, NPC, RIVAL_LIGA, LUGARES_V6, MEDALHA_POR_ID, chaveSprite, formaLiga, nomeMegaLiga,
  type Instalacao, type Motor } from "../../../motor/index.ts";
import { lutarNoPalco } from "./palcoPoc/TelaLugaresPoc.tsx";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { useLutaPoc } from "../../lutaPocTela.ts";
import { textoFalta, type Tamer } from "../../tamer.ts";
import { diaDe } from "../pet/TelaPet.tsx";
import { CartaoFabrica, CartaoSalao } from "./FabricaSalao.tsx";

const vitorias = (n: number): string => `${n} vitória${n === 1 ? "" : "s"}`;

/** uma instalacao da Fronteira: a regra em uma frase, o recorde do Tamer, o que este pet fez nela e "Tentar". Antes do titulo, trancada */
function CartaoInstalacao({ x, m, t, lutando }: { x: Instalacao; m: Motor; t: Tamer; lutando: boolean }) {
  const [erroPoc, setErroPoc] = useState<string | null>(null);
  const erro = m.porqueNaoInstalacao(x.id), rec = t.recorde(x.id), c = m.instalacoes[x.id];
  /* a tentativa no palco da luta da POC (LP3), com a semente da proxima tentativa do pet */
  const tentar = () => { lutarNoPalco(x.id, null, `Fronteira · ${x.nome}`, setErroPoc, mm => mm.sementeInstalacao(x.id)); };
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
      {erroPoc && <span className="aviso" role="alert">A luta não começou: {erroPoc}</span>}
      <button type="button" className="dl-btn fr-inst-tentar" disabled={!!erro || lutando} onClick={tentar}>{c && c.tentativas ? "Tentar de novo" : "Tentar"}</button>
    </li>
  );
}

export function TelaFronteira() {
  const { motor: m, erroTamer } = useJogo(), luta = useLutaPoc(), a = useAtlas(), t = tamerAtual();
  const erro = m.porqueNaoLiga(), [erroPoc, setErroPoc] = useState<string | null>(null);
  const nLiga = m.liga.tentativas;
  const img = (k: string, cls: string) => { if (a.tipo !== "ok") return null; const i = imagemAtlas(a, k); return <img className={`dl-pix ${cls}`} src={i.url} width={i.w} height={i.h} alt="" />; };
  const titulo = t.titulo, meu = t.tituloDe(m.semente);
  /* a ultima tentativa so tem as contas (LP3): a luta da POC nao e refeita aqui */
  const desafiar = () => { lutarNoPalco(RIVAL_LIGA, null, "Fronteira · Liga dos Líderes", setErroPoc); };
  return (
    <div className="tela dl fr-tela">
      <div className="fr-lado">
        <section className="dl-card fr-cab" aria-labelledby="fr-tit">
          <h2 id="fr-tit">Liga dos Líderes</h2>
          <p>Os {LIGA.length} líderes das arenas, um depois do outro, cada um com um Mega de outro arquétipo. Vencer os {LIGA.length} faz de você o <b>Campeão</b>.</p>
          <ul className="fr-regras" aria-label="Regras da Liga">
            <li><b>Sem cura</b> entre as lutas: a vida passa de uma para a outra.</li>
            <li>Cada líder luta no <b>mapa</b> da arena dele, com a regra do mapa.</li>
            <li>Os <b>chips de stat</b> equipados valem.</li>
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
        </section>
        <button type="button" className="dl-btn fr-lutar" disabled={!!erro || luta.lutando} onClick={desafiar}>
          {nLiga ? "Tentar a Liga de novo" : "Desafiar a Liga"} ({LIGA.length} lutas seguidas)</button>
        {erroPoc && <p className="aviso" role="alert">A luta não começou: {erroPoc}</p>}
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
          const f = formaLiga(i), lider = NPC[x.lider]!, md = MEDALHA_POR_ID[x.arena];
          return (
            <li key={x.arena} className="fr-card">
              <span className="fr-num dl-num" aria-hidden="true">{i + 1}</span>
              <span className="fr-sprs">{img(lider.sprite ?? lider.k, "fr-lider")}{img(chaveSprite(f), "fr-mega")}</span>
              <span className="fr-txt">
                <b className="fr-nome">Luta {i + 1}: {lider.nome} <span>· {LUGARES_V6[md.lugar].nome}</span></b>
                <span className="fr-mega-txt">luta com <b>{nomeMegaLiga(i)}</b> (Mega)</span>
                <span className="fr-tags"><span className="dl-tag fr-tag-arq">{NOME_ARQ[x.adulta]}</span><span className="dl-tag fr-tag-esp">{NOME_ESP[x.esp]}</span></span>
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
