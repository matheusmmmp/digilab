/* Arena (desenhos ArenaEscolha, ArenaAoVivo, EnsinarRegras; L3 de "Lugares da ilha", prancha lutar_arena_*): o seu pet em uma linha, as lutas de treino do
   Champion, a escolha do rival (nome e estilo), Lutar grande e Melhor de 10, as Regras de combate (e o que o pet aprendeu) num bloco fechado e a medalha
   da vez. O corte de texto da prancha: as frases vao para os baloes e para o "Como funciona" fechado. */
import { useEffect, useMemo, useRef, useState } from "react";
import { Brain, ChevronRight, Info, Medal, Swords } from "lucide-react";
import { LUGARES_V6, MEDALHAS, NOME_ARQ, NOME_BOT, NOME_DONO, NOME_V2, chaveSprite, lutadorBot, lutadorPet, nomeEstagio, nomeForma, vidaExibida, duracaoLuta } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { ComDica, ComoFunciona } from "../../componentes/Dica.tsx";
import { tamerAtual, useJogo } from "../../jogo.ts";
import {
  LUTA, RIVAIS_ADULTOS, RIVAIS_CLASSICOS, escolherRival, exibirBot, lutarAnimado, melhorDe10, previa, reconstruirLuta, sparringTexto, useLuta,
} from "../../luta.ts";
import { EditorRegras } from "./EditorRegras.tsx";
import { PainelAprendizado } from "./PainelAprendizado.tsx";
import { ENDERECO_LUTA } from "../../rotas.ts";
import { EscolhaCarta } from "../../componentes/EscolhaCarta.tsx";
import { comoGanhar } from "../../tamer.ts";

/** um rival (L3): o nome e o estilo, em radio */
function Rival({ k, adulto = false }: { k: string; adulto?: boolean }) {
  const luta = useLuta(), L = exibirBot(k), estilo = L.estiloTela ?? (k === "oraculo" ? "referência" : NOME_BOT[k]);
  return (
    <button type="button" className="ar2-rival" data-adulto={adulto ? "1" : undefined} role="radio" aria-checked={luta.rival === k && !luta.rivalFixo} disabled={luta.lutando} onClick={() => escolherRival(k)}>
      <span className="ar2-radio" aria-hidden="true" /><span><b>{L.nomeTela}</b><small>{estilo}</small></span>
    </button>
  );
}

/** a ultima luta do registro, com o resultado e o replay no Diario; sem luta nenhuma, a linha some (prancha) */
function UltimaLuta({ verReplay }: { verReplay: (idx: number) => void }) {
  const { motor: m } = useJogo();
  let idx = -1;
  for (let i = m.log.length - 1; i >= 0; i--) if (m.log[i][1] === "l") { idx = i; break; }
  const luta = useMemo(() => (idx < 0 ? null : reconstruirLuta(m, idx)), [idx, m.semente]);
  if (!luta) return null;
  const r = luta.res.pontosA, tag = r === 1 ? "vitória" : r === 0 ? "derrota" : "empate";
  return (
    <div className="lg-linha arena-ult">
      <span className={`arena-ult-tag arena-ult-tag--${r === 1 ? "vit" : r === 0 ? "der" : "emp"}`}>{tag}</span>
      <b>{luta.B.nomeTela} · {duracaoLuta(luta.res)}</b>
      <button type="button" className="arena-ult-ver" aria-label="Ver a última luta no Diário" onClick={() => verReplay(idx)}>Diário</button>
    </div>
  );
}

export function TelaArena({ voltarPet, verReplay }: { voltarPet: () => void; verReplay: (idx: number) => void }) {
  void voltarPet;
  const { motor: m, nascendo } = useJogo(), luta = useLuta(), [todos, setTodos] = useState(false), a = useAtlas(), t = tamerAtual();
  /* "+N adultos" some ao ser tocado: o foco vai para o primeiro rival adulto que acabou de aparecer */
  const grupo = useRef<HTMLDivElement>(null);
  useEffect(() => { if (todos) grupo.current?.querySelector<HTMLElement>('[data-adulto]:not([aria-checked="true"])')?.focus(); }, [todos]);
  /* a aba abre com o palco do proprio modo (a mensagem da campanha nao aparece aqui) */
  useEffect(() => { if (!LUTA.palco || LUTA.palco.modo !== "arena") previa("arena"); }, []);
  useEffect(() => { if (!LUTA.lutando && LUTA.palco?.modo === "arena" && !LUTA.palco.resultado) previa("arena", true); }, [m.gp?.versao, m.estagioAtual]);
  const A = lutadorPet(m, "Seu pet"), B = lutadorBot(luta.rival, m.regras), pa = A.cond, sp = sparringTexto(m);
  const extra = [pa.tecnica && `técnica ${NOME_V2[pa.tecnica]}`, pa.passiva && `passiva ${NOME_ARQ[pa.passiva]}`].filter(Boolean).join(", ");
  const nRegras = m.gp ? m.gp.ativas.length : 0, img = a.tipo === "ok" && nascendo === 0 ? imagemAtlas(a, chaveSprite(m.forma)) : null;
  /* os bots a vista; as formas adultas atras do "+N adultos" (a escolhida fica a vista) */
  const adultos = todos ? RIVAIS_ADULTOS : RIVAIS_ADULTOS.filter(k => k === luta.rival);
  const escondidos = RIVAIS_ADULTOS.length - adultos.length, proxima = MEDALHAS.find(md => !t.ganha(md.id));
  const resumo = `Seu pet: ${nomeForma(m.forma)}, vida ${Math.round(vidaExibida(pa, m.forma.est, m.treino.total, m.versao)).toLocaleString("pt-BR")}, guts ${pa.guts0.toFixed(0)}/${pa.gutsMax.toFixed(0)}${extra ? ", " + extra : ""}; `
    + `regras de combate semeadas por ${NOME_BOT[A.estilo.base!] || A.estilo.base}. Rival: ${luta.rivalFixo ? nomeForma(luta.rivalFixo.rival.forma) + " (cenário)" : B.estilo.oraculo ? "oráculo (referência fora das regras de combate)" : exibirBot(luta.rival).nomeTela}.`;
  return (
    <div className="tela dl ar2-tela lg">
      <div className="lg-linha ar2-pet">
        <ComDica className="lg-linha" rotulo={`${nomeForma(m.forma)}, ${nomeEstagio(m.forma)}`} dica={resumo}>
          <span className="ar2-palco" aria-hidden="true">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
          <b className="ar2-nome">{nomeForma(m.forma)}</b><span className="lg-etq">{nomeEstagio(m.forma)}</span>
        </ComDica>
        <ComDica className="lg-etq lg-etq--apr ar2-apr" papel="img" lado="dir" rotulo={nRegras ? `${nRegras} regras de combate` : "luta ao acaso"}
          dica={nRegras ? "O pet aprende estas regras de combate lutando; você pode travar ou vetar." : "Ainda sem estilo de luta: decide ao acaso."}>
          <Brain aria-hidden="true" />{nRegras ? `${nRegras} regras` : "acaso"}
        </ComDica>
      </div>
      {sp && (
        <ComDica className="lg-destaque lg-linha ar2-treino" rotulo={`Lutas de treino: ${Math.min(m.sparring, 10)} de 10`}
          dica="As lutas de treino da Arena contam para virar Ultimate: 10, com 80% ou mais de vitórias.">
          <Swords aria-hidden="true" /><b className="lg-num">{Math.min(m.sparring, 10)}/10</b><span>lutas de treino</span><span className="lg-etq">Ultimate</span>
        </ComDica>
      )}
      {luta.rivalFixo && (
        <ComDica className="lg-etq" papel="img" rotulo="Rival do cenário"
          dica={`Pet de dono ${NOME_DONO[luta.rivalFixo.tipo]}, ${luta.rivalFixo.dias} dia(s), lutando com o estilo da linha dele. Troque o rival para voltar aos bots.`}>
          Rival do cenário
        </ComDica>
      )}
      <div className="ar2-rivais" role="radiogroup" aria-label="Rival" ref={grupo}>
        {RIVAIS_CLASSICOS.map(k => <Rival key={k} k={k} />)}
        {adultos.map(k => <Rival key={k} k={k} adulto />)}
        {escondidos > 0 && (
          <button type="button" className="ar2-rival ar2-rival--mais" aria-label={`Mostrar as ${RIVAIS_ADULTOS.length} formas adultas`} onClick={() => setTodos(true)}>
            <span className="ar2-radio ar2-radio--tracejado" aria-hidden="true" /><span><b>+{escondidos}</b><small>adultos</small></span>
          </button>
        )}
      </div>
      <EscolhaCarta rival={luta.rival} />
      <div className="ar2-acoes lg-linha">
        <button type="button" className="lutar-grande ar2-lutar" disabled={luta.lutando} onClick={() => { lutarAnimado(null); if (LUTA.lutando) location.hash = ENDERECO_LUTA; }}><Swords aria-hidden="true" />Lutar</button>
        <button type="button" className="ar2-melhor" disabled={luta.lutando} onClick={melhorDe10}>Melhor de 10</button>
      </div>
      {luta.palco?.resultado && luta.palco?.texto && !luta.lutando && <p className="ar2-ultima">{luta.palco.texto}</p>}
      <UltimaLuta verReplay={verReplay} />
      <div className="lg-linha ar2-bts">
        <details className="lg-como ar2-regras">
          <summary><Brain aria-hidden="true" />Regras<ChevronRight className="lg-seta" aria-hidden="true" /></summary>
          <section className="bloco"><h2>Regras de combate do seu pet</h2><EditorRegras /></section>
          <PainelAprendizado />
        </details>
        {proxima && (
          <ComDica className="lg-etq ar2-medalha" papel="img" rotulo={`${proxima.nome}: ${comoGanhar(proxima)}, na Exploração`}
            dica={<><b>{proxima.nome}</b>: {comoGanhar(proxima).replace(/^v/, "V")}, na Exploração.</>}>
            <Medal aria-hidden="true" />{LUGARES_V6[proxima.lugar].nome}
          </ComDica>
        )}
      </div>
      <ComoFunciona>
        Lute contra um rival. Seu pet decide por <b>regras de combate</b> que ele mesmo aprende lutando; você pode travar ou vetar regras. Distância, guts e golpe pesado anunciado um turno antes, com os <b>stats da forma</b>, a <b>técnica da linha</b> (Champion) e a <b>passiva</b> (Ultimate e Mega). A lista de regras (condição → ação) cresce a cada nível: Rookie 3, Champion 5, Ultimate e Mega 8. A campanha contra os NPCs fica na aba <b>Exploração</b>.
      </ComoFunciona>
      <details className="lg-como">
        <summary><Info aria-hidden="true" />Regras da luta<ChevronRight className="lg-seta" aria-hidden="true" /></summary>
        <p>Os dois revelam a ação ao mesmo tempo. Golpe rápido (perto, 10 guts, 8 de dano) interrompe quem prepara o pesado; defender contra golpe rápido devolve 5 (parry). O pesado (perto, 15 guts) sai no turno seguinte com 25 de dano e não é interrompido; foge-se dele recuando no turno da preparação ou esquivando (20 guts) no da execução. No turno de execução dá para <b>fintar</b> em vez de soltar o pesado: um golpe de 8 que acerta quem esquivou e não quebra a guarda. Disparo (médio/longe, 20 guts, 6 de dano). Defender reduz o dano a 30% (pesado: 60%) e rende +5 guts; carregar rende +25 guts mas o dano recebido sobe 50%. <b>Recuar não afasta se o oponente avança no mesmo turno</b> (avançar é ilegal de perto e recuar é ilegal de longe). A marca do caçador se perde se ele levar dano corpo a corpo ou terminar o turno de perto. A partir do turno 25 todo dano sobe 50% (morte súbita). Os danos, a vida, o guts e a defesa mudam com os stats da forma (aba Catálogo); as técnicas e passivas também estão lá. Após 40 turnos vence quem tem mais vida (proporcional); nos pets novos (v6) a luta que chega aos 40 turnos sem nocaute fica com quem foi desafiado, o rival. Os bots clássicos lutam com stats neutros.</p>
      </details>
    </div>
  );
}
