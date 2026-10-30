/* Aprendizado (pranchas DiarioLembrancas e o jeito): o cerebro deste pet, as lembrancas (4 recentes + 2 duradouras) e o jeito
   (temperamento, desejo, vinculo, confianca e tracos de combate). Valores exatos recolhidos; tudo vem do motor. As secoes do Bandit dos
   pets v1-v10 (Agora, Instinto x aprendido, Decisoes, desejo e obediencia) sairam com o descarte 6 (COMBATE-TR, etapa R2b; D-9). */
import {
  BASE_CARATER, CAT, CDJ, CME, COMBATE, EIXOS_TEMP, EMOCAO_TXT, FATORES_ESPACOS, NOME_COMB,
  afinidades, expressarDesejo, expressarEmocao, expressarTemperamento, type Lembranca, type MemoriaEspacos, type Motor,
} from "../../../motor/index.ts";
import { BarraCarater, comSinal, dec } from "../../componentes/Barras.tsx";
import { Grade, Peca } from "../../componentes/Imagens.tsx";
import { idxDoOrdinal } from "../../fala.ts";
import { AMPULHETA } from "../../grades.ts";
import { useJogo } from "../../jogo.ts";
import { diaDe, hhmm, lutasDaCausa } from "../pet/TelaPet.tsx";

const NOME_MEM: Record<string, string> = { demora: "Você me deixou esperando", bronca: "Broncas", elogio: "Elogios", carinho: "Carinho" };
const EMOTE_MEM: Record<string, string> = { elogio: "emoji_joinha", carinho: "emoji_coracao", bronca: "emoji_exclam" };
const EMOTE_EMOCAO: Record<string, string> = { alegria: "emoji_feliz", euforia: "emoji_feliz", orgulho: "emoji_feliz", ternura: "emoji_coracao" };
const CORES_AMPULHETA = { k: "#173A8A", w: "#FFFFFF", y: "#F0B429" };
const pct = (x: number): string => `${(x * 100).toFixed(0)}%`;

/* ------------------------------------------------ Lembrancas (DiarioLembrancas) */
function Lembrancas() {
  const { motor: m } = useJogo(), tick = m.e.tick, f = m.pol.mem.feat(tick);
  const mem = m.pol.mem as MemoriaEspacos;
  const barra = (rot: string, v: number, cls: string) => (
    <span className="lem-barra"><span><span>{rot}</span><span>{pct(v)}</span></span><span className="lem-trilho"><i className={cls} style={{ width: pct(Math.min(1, v)) }} /></span></span>
  );
  const slot = (x: Lembranca | undefined, i: number, dur: boolean) => x ? (
    <div className={`lem${dur ? " lem--dur" : ""}`} key={i}>
      <span className="lem-cab">{EMOTE_MEM[x.cat] ? <Peca nome={EMOTE_MEM[x.cat]} escala={2} /> : x.cat === "demora" ? <Grade grade={AMPULHETA} escala={3} cores={CORES_AMPULHETA} alt="" /> : null}<b>{NOME_MEM[x.cat]}</b></span>
      {x.emocao && <span className="dl-apoio">sentiu {EMOCAO_TXT[x.emocao][0]}</span>}
      {barra("força", x.int, "forca")}
      {barra("ativa agora", mem.ativacao(x, tick), "ativa")}
      <span className="dl-lcd lem-desde">desde D{diaDe(x.criada)} {hhmm(x.criada)}</span>
    </div>
  ) : <div className="lem lem--vazio" key={i}>espaço livre</div>;
  const ult = mem.emocoes.length ? mem.emocoes[mem.emocoes.length - 1] : null;
  return (
    <>
      <span className="ensinar-cab"><h2>Recentes</h2><span className="dl-apoio">{CME.nCurto} espaços · a mais forte de cada tipo fica</span></span>
      <div className="lem-grade">{Array.from({ length: CME.nCurto }, (_, i) => slot(mem.curto[i], i, false))}</div>
      <span className="ensinar-cab"><h2>Duradouras</h2><span className="dl-apoio">{CME.nLongo} espaços · depois de 12 h, uma recente tenta entrar</span></span>
      <div className="lem-grade">{Array.from({ length: CME.nLongo }, (_, i) => slot(mem.longo[i], i, true))}</div>
      {ult && (
        <div className="dl-card lem-ult">
          {EMOTE_EMOCAO[ult.nome] && <Peca nome={EMOTE_EMOCAO[ult.nome]} escala={2} />}
          <span><b>Último sentimento: {EMOCAO_TXT[ult.nome][0]}</b>
            <span>{expressarEmocao(ult, ult.cat, m.estagioAtual, ult.ref == null ? null : idxDoOrdinal(m, ult.ref))}</span>
            <span className="dl-apoio">{ult.eixo ? "pelo temperamento: " + ult.eixo : "reação padrão (nenhum traço de temperamento pesou)"}</span></span>
        </div>
      )}
      <details className="dl-apoio"><summary>Como funciona e valores exatos</summary>
        <p>Uma lembrança por tipo; a mais forte fica. Depois de 12 h uma lembrança pode virar duradoura; a cada 4 h acordado ele relembra tudo. O que ele lembra entra no que ele aprende.</p>
        <p>{FATORES_ESPACOS.map((c, i) => `${NOME_MEM[c].toLowerCase()} ${pct(f[i])}`).join(", ")}</p>
      </details>
    </>
  );
}

/* ------------------------------------------------ Jeito: temperamento, desejo, vinculo e tracos */
/** confianca de combate (M1, pets v8) so em palavras: o estado mostrado (com histerese) e as lutas da causa */
function confiancaEmPalavras(m: Motor): string {
  const e = m.estadoConfianca()!, n = lutasDaCausa(m, e.lutas, e.estado).length;
  const desde = e.desde !== null ? ` desde D${diaDe(e.desde)} ${hhmm(e.desde)}` : "";
  if (e.estado === "confiante") return `confiante${desde}: ganhou as últimas (${n} ${n === 1 ? "vitória" : "vitórias"} no registro); nada muda na luta`;
  if (e.estado === "inseguro") return `inseguro${desde}: perdeu as últimas (${n} ${n === 1 ? "derrota" : "derrotas"} no registro); hesita e erra mais na luta`;
  if (e.estado === "entediado") return `entediado do rival${desde}: as últimas ${n} lutas foram contra rival repetido; elas ensinam e rendem menos`;
  return m.conf.historico.length ? "sem estado marcante: nem confiante nem inseguro" : "ainda não lutou: nem confiante nem inseguro";
}
function Jeito() {
  const { motor: m } = useJogo(), e = m.e, est = m.estagioAtual, des = m.desejoAtual(m.observacaoAgora(), e.tick);
  const vinculo = `${(m.vinc.valor * 100).toFixed(0)}% · sobe quando você atende uma vontade dele`;
  const bruto = afinidades(m.tracos), base = BASE_CARATER[est === "adulto" || est === "mega" ? "adulto" : "adolescente"];
  const af = Object.fromEntries(COMBATE.map(c => [c, bruto[c] - base[c]])) as Record<string, number>;
  return (
    <>
      <section className="dl-card bloco">
        <h2>Temperamento e desejo</h2>
        <div className="jeito"><span className="dl-apoio">Temperamento</span> <b>{expressarTemperamento(m.temp, est)}</b></div>
        <div className="jeito"><span className="dl-apoio">Desejo</span> <b>{des ? expressarDesejo(des, est) : "…"}</b></div>
        <div className="jeito"><span className="dl-apoio">Vínculo</span> <b>{vinculo}</b></div>
        <div className="jeito"><span className="dl-apoio">Confiança</span> <b>{confiancaEmPalavras(m)}</b></div>
        <div>{EIXOS_TEMP.map(k => <BarraCarater key={k} eixo={k} v={m.temp[k]} />)}</div>
        <details className="dl-apoio"><summary>Como funciona e valores exatos</summary>
          <p>O <b>temperamento</b> vem de nascença (sorteado pela semente, igual a vida inteira): muda <i>como</i> o pet aprende, não <i>o que</i>. O <b>desejo</b> é calculado agora: uma necessidade abaixo do limite ou, se não houver, a ação que ele aprendeu a preferir. A partir do Rookie ele sabe dizer qual dos dois é.</p>
          <p>{"temperamento: " + EIXOS_TEMP.map(k => `${k} ${comSinal(m.temp[k], 2)}`).join(", ")
            + ` (a fala só comenta eixos a partir de ${dec(CDJ.limiarTom, 1)} para mais ou para menos)` + " · desejo: "
            + (des ? `${des.tipo} ${des.alvo}${des.causa ? " (" + des.causa + ")" : ""}, intensidade ${dec(des.intensidade, 2)}` : "nenhum agora")}</p>
        </details>
      </section>
      <section className="dl-card bloco">
        <h2>Traços de combate</h2>
        <p className="dl-apoio">Comparados com um pet comum. Na evolução viram <b>caráter</b>.</p>
        <div>{COMBATE.map(c => <BarraCarater key={c} eixo={NOME_COMB[c]} v={af[c] / CAT.escalaCarater} />)}</div>
        <details className="dl-apoio"><summary>Como funciona e valores exatos</summary>
          <p>Média lenta do que o pet faz no dia a dia. Todo pet dorme e fica à toa muito, e isso conta como bloqueio; por isso a comparação com um pet comum.</p>
          <p>{"diferença para o pet comum: " + COMBATE.map(c => `${NOME_COMB[c].toLowerCase()} ${comSinal(af[c], 3)}`).join(", ")}</p>
        </details>
      </section>
    </>
  );
}

/** o cerebro e o A (os lobos), nao o Bandit: as secoes do Bandit (Agora, Instinto x aprendido e Decisoes) eram dos pets v1-v10, que sairam
    com o descarte 6 (COMBATE-TR, etapa R2b). Ficam as lembrancas (a memoria por espacos) e o jeito */
export function TelaAprend() {
  return (
    <div className="tela dl">
      <div>
        <section className="dl-card bloco">
          <h2>O cérebro deste pet</h2>
          <p className="dl-apoio">Ele decide pelo instinto e aprende sozinho com o que as próprias ações fazem no corpo dele: comer quando tem
            fome, brincar quando está entediado, o seu carinho e o seu tapa. Não há elogio nem bronca. O painel com as decisões do cérebro
            vem numa próxima versão do jogo.</p>
        </section>
        <Lembrancas />
      </div>
      <div><Jeito /></div>
    </div>
  );
}
