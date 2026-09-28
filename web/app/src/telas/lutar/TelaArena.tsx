/* Arena (desenhos ArenaEscolha, ArenaAoVivo, EnsinarRegras; porte do HTML): escolha do rival em cards com sprite
   e uma linha de estilo, lutas de treino do Champion, Lutar grande e Melhor de 10, o palco e as regras de combate. */
import { useEffect, useState } from "preact/hooks";
import { NOME_ARQ, NOME_BOT, NOME_DONO, NOME_V2, chaveSprite, lutadorBot, lutadorPet, nomeEstagio, nomeForma } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { Seg } from "../../componentes/Barras.tsx";
import { useJogo } from "../../jogo.ts";
import {
  LUTA, RIVAIS_ADULTOS, RIVAIS_CLASSICOS, escolherRival, exibirBot, lutarAnimado, melhorDe10, previa, sparringTexto, useLuta,
} from "../../luta.ts";
import { EditorRegras } from "./EditorRegras.tsx";
import { Cena } from "./PalcoLuta.tsx";
import { ENDERECO_LUTA } from "../../rotas.ts";

function CardRival({ k, adulto = false }: { k: string; adulto?: boolean }) {
  const a = useAtlas(), luta = useLuta(), L = exibirBot(k);
  const img = a.tipo === "ok" ? imagemAtlas(a, L.sprite) : null, h = a.tipo === "ok" ? dimSprite(a.dados, L.sprite)[1] : 0;
  const estilo = L.estiloTela ?? (k === "oraculo" ? "referência" : NOME_BOT[k]);
  return (
    <button type="button" class={`rival-card${adulto ? " rival-card--adulto" : ""}`} role="radio" aria-checked={luta.rival === k && !luta.rivalFixo} disabled={luta.lutando} onClick={() => escolherRival(k)}>
      <span class="rival-spr">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" style={{ marginBottom: `${h > 44 ? -Math.round((h - 44) * .5) : 0}px` }} />}</span>
      <span class="rival-txt"><b>{L.nomeTela}</b><small>{estilo}</small></span>
    </button>
  );
}

/** o seu pet no topo (prancha ArenaEscolha): sprite, nivel, regras de combate, tecnica ou passiva e as lutas de treino */
function CardPet() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), sp = sparringTexto(m), pa = lutadorPet(m, "Seu pet").cond;
  const img = a.tipo === "ok" && nascendo === 0 ? imagemAtlas(a, chaveSprite(m.forma)) : null;
  const nRegras = m.gp ? m.gp.ativas.length : 0;
  const extra = [pa.tecnica && `técnica ${NOME_V2[pa.tecnica]}`, pa.passiva && `passiva ${NOME_ARQ[pa.passiva]}`].filter(Boolean).join(" · ");
  return (
    <div class="dl-card arena-pet">
      <div class="arena-pet-cab">
        <span class="arena-pet-spr">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
        <span class="arena-pet-txt"><b>{nomeForma(m.forma)}</b>
          <span>{nomeEstagio(m.forma)} · {nRegras ? `${nRegras} regras de combate` : "luta ao acaso"}{extra ? " · " + extra : ""}</span></span>
      </div>
      {sp && <div class="arena-pet-treino"><span><span>lutas de treino para virar Ultimate ou Mega</span><span class="dl-lcd">{Math.min(m.sparring, 10)} de 10</span></span>
        <Seg n={Math.min(m.sparring, 10)} m={10} cls="dl-seg--acao" /></div>}
    </div>
  );
}

export function TelaArena({ voltarPet }: { voltarPet: () => void }) {
  const { motor: m } = useJogo(), luta = useLuta(), [todos, setTodos] = useState(false);
  /* a aba abre com o palco do proprio modo (a mensagem da campanha nao aparece aqui) */
  useEffect(() => { if (!LUTA.palco || LUTA.palco.modo !== "arena") previa("arena"); }, []);
  useEffect(() => { if (!LUTA.lutando && LUTA.palco?.modo === "arena" && !LUTA.palco.resultado) previa("arena", true); }, [m.gp?.versao, m.estagioAtual]);
  const A = lutadorPet(m, "Seu pet"), B = lutadorBot(luta.rival), pa = A.cond;
  const extra = [pa.tecnica && `técnica ${NOME_V2[pa.tecnica]}`, pa.passiva && `passiva ${NOME_ARQ[pa.passiva]}`].filter(Boolean).join(", ");
  /* formas adultas: duas a mostra (e a escolhida), o resto num toque, como na prancha */
  const adultos = todos ? RIVAIS_ADULTOS : RIVAIS_ADULTOS.filter((k, i) => i < 2 || k === luta.rival);
  const escondidos = RIVAIS_ADULTOS.length - adultos.length;
  return (
    <div class="tela dl">
      <CardPet />
      <div class="rivais" role="radiogroup" aria-label="Rival">
        <h2 class="rivais-tit">Bots de treino</h2><div class="rivais-grade">{RIVAIS_CLASSICOS.map(k => <CardRival key={k} k={k} />)}</div>
        <h2 class="rivais-tit">Formas adultas</h2><div class="rivais-grade">{adultos.map(k => <CardRival key={k} k={k} adulto />)}</div>
        {escondidos > 0 && <button type="button" class="rivais-mais" onClick={() => setTodos(true)}>+ {escondidos} formas adultas</button>}
      </div>
      {luta.rivalFixo && <p class="dl-apoio">Rival do cenário: pet de dono {NOME_DONO[luta.rivalFixo.tipo]}, {luta.rivalFixo.dias} dia(s), lutando com o estilo da linha dele. Troque o rival nos cards para voltar aos bots.</p>}
      <div class="arena-acoes">
        <button type="button" class="dl-btn dl-btn--sec" disabled={luta.lutando} onClick={melhorDe10}>Melhor de 10</button>
        <button type="button" class="dl-btn lutar-grande" disabled={luta.lutando} onClick={() => { lutarAnimado(null, NOME_V2); if (LUTA.lutando) location.hash = ENDERECO_LUTA; }}>Lutar</button>
      </div>
      <p class="dl-apoio">{`Seu pet: ${nomeForma(m.forma)}, vida ${pa.hpMax.toFixed(0)}, guts ${pa.guts0.toFixed(0)}/${pa.gutsMax.toFixed(0)}${extra ? ", " + extra : ""}; regras de combate semeadas por ${NOME_BOT[A.estilo.base!] || A.estilo.base} · rival: ${luta.rivalFixo ? nomeForma(luta.rivalFixo.rival.forma) + " (cenário)" : B.estilo.oraculo ? "oráculo (referência fora das regras de combate)" : exibirBot(luta.rival).nomeTela}.`}</p>
      {/* desktop: previa parada da arena com o rival escolhido (a luta abre em tela cheia) */}
      {luta.palco && !luta.lutando && <div class="arena-previa"><Cena p={luta.palco} /></div>}
      {luta.palco?.texto && !luta.lutando && <p class="dl-card arena-ultima">{luta.palco.texto}</p>}
      <section class="bloco"><h2>Regras de combate do seu pet</h2><EditorRegras /></section>
      <details class="dl-apoio"><summary>Como funciona</summary>
        <p>Lute contra um rival. Seu pet decide por <b>regras de combate</b> que ele mesmo aprende lutando; você pode travar ou vetar regras. Distância, guts e golpe pesado anunciado um turno antes, com os <b>stats da forma</b>, a <b>técnica da linha</b> (Champion) e a <b>passiva</b> (Ultimate e Mega). A lista de regras (condição → ação) cresce a cada nível: Rookie 3, Champion 5, Ultimate e Mega 8. A campanha contra os NPCs fica na aba <b>Campanha</b>.</p></details>
      <details class="dl-apoio"><summary>Regras da luta</summary>
        <p>Os dois revelam a ação ao mesmo tempo. Golpe rápido (perto, 10 guts, 8 de dano) interrompe quem prepara o pesado; defender contra golpe rápido devolve 5 (parry). O pesado (perto, 15 guts) sai no turno seguinte com 25 de dano e não é interrompido; foge-se dele recuando no turno da preparação ou esquivando (20 guts) no da execução. No turno de execução dá para <b>fintar</b> em vez de soltar o pesado: um golpe de 8 que acerta quem esquivou e não quebra a guarda. Disparo (médio/longe, 20 guts, 6 de dano). Defender reduz o dano a 30% (pesado: 60%) e rende +5 guts; carregar rende +25 guts mas o dano recebido sobe 50%. <b>Recuar não afasta se o oponente avança no mesmo turno</b> (avançar é ilegal de perto e recuar é ilegal de longe). A marca do caçador se perde se ele levar dano corpo a corpo ou terminar o turno de perto. A partir do turno 25 todo dano sobe 50% (morte súbita). Os danos, a vida, o guts e a defesa mudam com os stats da forma (aba Catálogo); as técnicas e passivas também estão lá. Após 40 turnos vence quem tem mais vida (proporcional). Os bots clássicos lutam com stats neutros.</p></details>
    </div>
  );
}
