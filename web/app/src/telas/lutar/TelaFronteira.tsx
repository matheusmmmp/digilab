/* Lutar · Fronteira (docs/DESIGN_FRONTEIRA.md, secoes 2 e 5; medalhas parte 4a; so pets v6): a Liga dos Lideres. Os 6 lideres com os
   Megas deles, na ordem das lutas; as regras da Liga; a ultima tentativa (ate que luta chegou e a vida que sobrou em cada uma, refeitas
   do registro); o titulo do Tamer; e o botao de desafiar (a luta em tela cheia, #/lutar/luta). Tudo do motor (motor/liga.ts,
   Motor.liga, o evento de luta da Liga) e do registro do Tamer (o evento "campeao"). */
import { useEffect, useMemo } from "preact/hooks";
import { LIGA, MEDALHAS_LIGA, NOME_ARQ, NOME_ESP, NOME_V2, NPC, RIVAL_LIGA, LUGARES_V6, MEDALHA_POR_ID, chaveSprite, formaLiga, nomeMegaLiga, type Motor } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { LUTA, lutarLiga, previa, reconstruirLuta, useLuta } from "../../luta.ts";
import { ENDERECO_LUTA } from "../../rotas.ts";
import { textoFalta } from "../../tamer.ts";
import { diaDe } from "../pet/TelaPet.tsx";

/** a ultima tentativa da Liga no registro do pet (null: nenhuma): as lutas jogadas (o pet no fim de cada uma) e o indice do evento */
function ultimaTentativa(m: Motor): { idx: number; lutas: { venceu: boolean; vida: number; turnos: number }[] } | null {
  let idx = -1;
  for (let i = m.log.length - 1; i >= 0; i--) { const ev = m.log[i]; if (ev[1] === "l" && ev[2].r === RIVAL_LIGA) { idx = i; break; } }
  if (idx < 0) return null;
  const L = reconstruirLuta(m, idx);
  return { idx, lutas: L.serie.map(r => ({ venceu: r.pontosA === 1, vida: Math.max(0, r.E.L[0].hp) / r.E.L[0].hpMax, turnos: r.turnos.length })) };
}
const pct = (x: number): string => `${Math.round(x * 100)}%`;

export function TelaFronteira() {
  const { motor: m, erroTamer } = useJogo(), luta = useLuta(), a = useAtlas(), t = tamerAtual();
  useEffect(() => { if (!LUTA.lutando && m.versao >= 6 && (!LUTA.palco || LUTA.palco.modo !== "fronteira")) previa("fronteira"); }, []);
  const v6 = m.versao >= 6, erro = v6 ? m.porqueNaoLiga() : "a Fronteira é só dos pets v6";
  const nLiga = v6 ? m.liga.tentativas : 0;
  /* a ultima tentativa, refeita do registro (so muda com luta nova da Liga) */
  const ult = useMemo(() => (nLiga ? ultimaTentativa(m) : null), [nLiga, m.semente]);
  const img = (k: string, cls: string) => { if (a.tipo !== "ok") return null; const i = imagemAtlas(a, k); return <img class={`dl-pix ${cls}`} src={i.url} width={i.w} height={i.h} alt="" />; };
  const titulo = t.titulo, meu = t.tituloDe(m.semente), parou = ult ? ult.lutas.length : 0, venceuUlt = !!ult && ult.lutas.length === LIGA.length && ult.lutas[LIGA.length - 1].venceu;
  const desafiar = () => { lutarLiga(NOME_V2); if (LUTA.lutando) location.hash = ENDERECO_LUTA; };
  return (
    <div class="tela dl desk fr-tela">
      <div class="desk-col fr-lado">
        <section class="dl-card fr-cab" aria-labelledby="fr-tit">
          <h2 id="fr-tit">Liga dos Líderes</h2>
          <p>Os {LIGA.length} líderes das arenas, um depois do outro, cada um com um Mega de outro arquétipo. Vencer os {LIGA.length} faz de você o <b>Campeão</b>.</p>
          <ul class="fr-regras" aria-label="Regras da Liga">
            <li><b>Sem cura</b> entre as lutas: a vida e o guts passam de uma para a outra.</li>
            <li>Os <b>chips</b> equipados valem; as <b>cartas</b> não valem.</li>
            <li>No limite de turnos, a luta fica com o <b>líder</b>.</li>
            <li>Perder uma luta encerra a tentativa. Tentar de novo não custa nada.</li>
          </ul>
          {erroTamer && <p class="med-erro" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
          {titulo
            ? <div class={`fr-titulo${meu ? " meu" : ""}`} role="status"><SeloMedalha n={0} ouro ganha tam={40} />
                <span><b>Campeão da Liga</b><span>{meu ? `${meu.forma} venceu os ${LIGA.length} no dia ${diaDe(meu.tick)}.` : `O título é seu desde ${titulo.forma}, no dia ${diaDe(titulo.tick)}.`}</span></span></div>
            : null}
          {v6 && m.medalhas < MEDALHAS_LIGA
            ? <p class="med-espera" role="status"><b>A Fronteira abre com as {MEDALHAS_LIGA} medalhas.</b> {textoFalta(t, MEDALHAS_LIGA)}</p>
            : erro ? <p class="dl-apoio">Agora não dá para desafiar a Liga: {erro}.</p> : null}
          {nLiga > 0 && <p class="fr-conta"><span><b class="dl-num">{nLiga}</b> tentativa{nLiga === 1 ? "" : "s"}</span><span><b class="dl-num">{m.liga.titulos}</b> título{m.liga.titulos === 1 ? "" : "s"}</span></p>}
          {ult && <p class="fr-ultima" role="status">{venceuUlt
            ? `Última tentativa: venceu os ${LIGA.length}, e terminou com ${pct(ult.lutas[LIGA.length - 1].vida)} da vida.`
            : `Última tentativa: parou na luta ${parou} de ${LIGA.length}, contra ${nomeMegaLiga(parou - 1)} de ${NPC[LIGA[parou - 1].lider]!.nome}.`}</p>}
        </section>
        <button type="button" class="dl-btn fr-lutar" disabled={!!erro || luta.lutando} onClick={desafiar}>
          {nLiga ? "Tentar a Liga de novo" : "Desafiar a Liga"} ({LIGA.length} lutas seguidas)</button>
      </div>
      <ol class="fr-lista" aria-label="Os líderes da Liga, na ordem das lutas">
        {LIGA.map((x, i) => {
          const f = formaLiga(i), lider = NPC[x.lider]!, md = MEDALHA_POR_ID[x.arena], r = ult?.lutas[i];
          const st = !ult ? null : r ? (r.venceu ? "vit" : "der") : "nao";
          return (
            <li key={x.arena} class={`fr-card${st ? " fr-card--" + st : ""}`}>
              <span class="fr-num dl-num" aria-hidden="true">{i + 1}</span>
              <span class="fr-sprs">{img(lider.sprite ?? lider.k, "fr-lider")}{img(chaveSprite(f), "fr-mega")}</span>
              <span class="fr-txt">
                <b class="fr-nome">Luta {i + 1}: {lider.nome} <span>· {LUGARES_V6[md.lugar].nome}</span></b>
                <span class="fr-mega-txt">luta com <b>{nomeMegaLiga(i)}</b> (Mega)</span>
                <span class="fr-tags"><span class="dl-tag fr-tag-arq">{NOME_ARQ[x.adulta]}</span><span class="dl-tag fr-tag-esp">{NOME_ESP[x.esp]}</span></span>
                {st && <span class={`fr-st fr-st--${st}`}>{r ? `${r.venceu ? "venceu" : "perdeu"} em ${r.turnos} turnos · ${pct(r.vida)} da vida no fim` : "não chegou a lutar"}</span>}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
