/* Aprendizado (desenhos EnsinarPolitica, DiarioLembrancas; porte do HTML): temperamento, desejo e vinculo;
   tracos de combate relativos ao pet comum; recompensas; instinto x o que aprendeu com voce; memoria (4 recentes
   + 2 duradouras, com os vazios); desejo e obediencia; ultimas decisoes com o porque. Valores exatos recolhidos. */
import {
  ACOES_PET, BASE_CARATER, CAT, CDJ, CME, COMBATE, EIXOS_TEMP, EMOCAO_TXT, FATORES_ESPACOS, NOME_COMB, NOME_PET,
  afinidades, distInstinto, expressarDesejo, expressarEmocao, expressarTemperamento, observacao, termosObediencia,
  type Lembranca, type MemoriaEspacos,
} from "../../../motor/index.ts";
import { BarraCarater, Numeros, Seg, blocos, comSinal, dec } from "../../componentes/Barras.tsx";
import { Peca } from "../../componentes/Imagens.tsx";
import { falaDe, idxDoOrdinal } from "../../fala.ts";
import { useJogo } from "../../jogo.ts";
import { diaDe, hhmm } from "../pet/TelaPet.tsx";

const NOME_MEM: Record<string, string> = { demora: "Você me deixou esperando", bronca: "Broncas", elogio: "Elogios", carinho: "Carinho" };
const EMOTE_MEM: Record<string, string> = { elogio: "emoji_joinha", carinho: "emoji_coracao" };

function Jeito() {
  const { motor: m } = useJogo(), e = m.e, est = m.estagioAtual, des = m.desejoAtual(observacao(e), e.tick);
  const vinculo = m.versao >= 2
    ? `${(m.vinc.valor * 100).toFixed(0)}% · sem conflito, aceita um cuidado com ${(termosObediencia(m.vinc.valor, m.temp.teimosia, 0, null)[0] * 100).toFixed(0)}% de chance`
    : "pet de versão antiga: sem vínculo nem recusa (um pet novo já nasce com eles)";
  return (
    <section class="bloco">
      <h2>Temperamento e desejo</h2>
      <div class="jeito"><span class="dl-apoio">Temperamento</span> <b>{expressarTemperamento(m.temp, est)}</b></div>
      <div class="jeito"><span class="dl-apoio">Desejo</span> <b>{des ? expressarDesejo(des, est) : "…"}</b></div>
      <div class="jeito"><span class="dl-apoio">Vínculo</span> <b>{vinculo}</b></div>
      <div>{EIXOS_TEMP.map(k => <BarraCarater key={k} eixo={k} v={m.temp[k]} />)}</div>
      <details class="dl-apoio"><summary>Como funciona e valores exatos</summary>
        <p>O <b>temperamento</b> vem de nascença (sorteado pela semente, igual a vida inteira): muda <i>como</i> o pet aprende, não <i>o que</i>. O <b>desejo</b> é calculado agora: uma necessidade abaixo do limite ou, se não houver, a ação que ele aprendeu a preferir. A partir do Rookie ele sabe dizer qual dos dois é.</p>
        <p>{"temperamento: " + EIXOS_TEMP.map(k => `${k} ${comSinal(m.temp[k], 2)}`).join(", ")
          + ` (a fala só comenta eixos a partir de ${dec(CDJ.limiarTom, 1)} para mais ou para menos)` + " · desejo: "
          + (des ? `${des.tipo} ${des.alvo}${des.causa ? " (" + des.causa + ")" : ""}, intensidade ${dec(des.intensidade, 2)}` : "nenhum agora")}</p>
      </details>
    </section>
  );
}
function Tracos() {
  const { motor: m } = useJogo();
  /* relativo a um pet comum (mesma base que o carater usa), na escala que vira carater na evolucao */
  const bruto = afinidades(m.tracos), base = BASE_CARATER[m.estagioAtual === "adulto" ? "adulto" : "adolescente"];
  const af = Object.fromEntries(COMBATE.map(c => [c, bruto[c] - base[c]])) as Record<string, number>;
  const r = m.pol.rec;
  return (
    <section class="bloco">
      <h2>Traços de combate</h2>
      <p class="dl-apoio">Comparados com um pet comum. Na evolução viram <b>caráter</b>.</p>
      <div>{COMBATE.map(c => <BarraCarater key={c} eixo={NOME_COMB[c]} v={af[c] / CAT.escalaCarater} />)}</div>
      <details class="dl-apoio"><summary>Como funciona e valores exatos</summary>
        <p>Média lenta do que o pet faz no dia a dia. Todo pet dorme e fica à toa muito, e isso conta como bloqueio; por isso a comparação com um pet comum.</p>
        <p>{"diferença para o pet comum: " + COMBATE.map(c => `${NOME_COMB[c].toLowerCase()} ${comSinal(af[c], 3)}`).join(", ")}</p>
      </details>
      <p>Elogio e repreensão ajustam a ação que ele acabou de fazer. Atender rápido um pedido de atenção também conta.</p>
      <Numeros itens={[["Elogios", r.elogio], ["Repreensões", r.repreensao], ["Pedidos atendidos", r.atendido], ["Pedidos ignorados", r.ignorado]]} />
    </section>
  );
}
function Politica() {
  const { motor: m } = useJogo(), obs = observacao(m.e), p0 = distInstinto(obs), pm = m.pol.media(obs);
  return (
    <section class="bloco">
      <h2>No estado de agora</h2>
      <div class="legenda"><span class="leg-instinto">instinto</span><span class="leg-aprendido">o que aprendeu com você</span></div>
      <div class="linhas">
        {ACOES_PET.map(a => {
          const d = pm[a] - p0[a];
          return (
            <div class="dupla" key={a}>
              <span>{NOME_PET[a]}</span>
              <div class="bars">
                <div class="bar prior" role="img" aria-label={`instinto ${Math.round(p0[a] * 100)}%`}><i style={{ width: `${(p0[a] * 100).toFixed(1)}%` }} /></div>
                <div class="bar agora" role="img" aria-label={`aprendido ${Math.round(pm[a] * 100)}%`}><i class="dl-malha" style={{ width: `${(pm[a] * 100).toFixed(1)}%` }} /></div>
              </div>
              <span class="v">{Math.abs(d) >= .05 ? `${d > 0 ? "mais" : "menos"} ${Math.abs(Math.round(d * 100))} pts` : ""}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
function Memoria() {
  const { motor: m } = useJogo(), tick = m.e.tick, f = m.pol.mem.feat(tick), v2 = m.versao >= 2;
  const rot = v2 ? FATORES_ESPACOS.map(c => NOME_MEM[c]) : ["Demora com a comida", "Demora para limpar", "Broncas recentes", "Elogios recentes"];
  const mem = m.pol.mem as MemoriaEspacos;
  const slot = (x: Lembranca | undefined, i: number) => x ? (
    <div class="mem-slot" key={i}>
      <span class="mem-cab">{EMOTE_MEM[x.cat] && <Peca nome={EMOTE_MEM[x.cat]} />}<b>{NOME_MEM[x.cat]}</b></span>
      <span class="dl-apoio">{x.emocao ? EMOCAO_TXT[x.emocao][0] + " · " : ""}força {(x.int * 100).toFixed(0)}% · desde D{diaDe(x.criada)} {hhmm(x.criada)}</span>
      <Seg n={blocos(mem.ativacao(x, tick), 5)} m={5} cls="dl-seg--acao" />
    </div>
  ) : <div class="mem-slot mem-vazio" key={i}>vazio</div>;
  const cheio = (lst: Lembranca[], n: number) => Array.from({ length: n }, (_, i) => slot(lst[i], i));
  const ult = v2 && mem.emocoes.length ? mem.emocoes[mem.emocoes.length - 1] : null;
  return (
    <section class="bloco">
      <h2>O que ele lembra de você</h2>
      <p class="dl-apoio">{v2
        ? "4 lembranças recentes e 2 duradouras, uma por tipo; a mais forte fica. Depois de 12 h uma lembrança pode virar duradoura; a cada 4 h acordado ele relembra tudo. O que ele lembra entra no que ele aprende."
        : "Memória curta (pet de versão antiga): quanto você demorou para atender o último pedido de comida ou de limpeza, e as broncas e elogios recentes (somem com o tempo). Entra no aprendizado como contexto."}</p>
      <Numeros itens={rot.map((k, i) => [k, `${(f[i] * 100).toFixed(0)}%`])} />
      {v2 && <>
        <h3 class="mem-tit">Recentes <span class="dl-apoio">{mem.curto.length} de {CME.nCurto}</span></h3><div class="mem-grade">{cheio(mem.curto, CME.nCurto)}</div>
        <h3 class="mem-tit">Duradouras <span class="dl-apoio">{mem.longo.length} de {CME.nLongo}</span></h3><div class="mem-grade">{cheio(mem.longo, CME.nLongo)}</div>
      </>}
      {ult && <div><span class="t">sentiu</span> {expressarEmocao(ult, ult.cat, m.estagioAtual, ult.ref == null ? null : idxDoOrdinal(m, ult.ref))} <span class="dl-apoio">({ult.eixo ? "pelo temperamento: " + ult.eixo : "reação padrão"})</span></div>}
    </section>
  );
}
function Obediencia() {
  const { motor: m } = useJogo();
  if (m.versao < 2) return null;
  const dz = m.dz, ob = m.obed;
  return (
    <section class="bloco">
      <h2>Desejo e obediência</h2>
      <p class="dl-apoio">Cumprimento: das vontades que ele anunciou, quantas ele fez de fato em até 1 h. Se for baixo, a fala promete o que o pet não faz. Obediência: quantos cuidados seus ele aceitou.</p>
      <Numeros itens={[["Vontades anunciadas", dz.vontades], ["Cumprimento", dz.vontades ? `${(dz.cumpridas / dz.vontades * 100).toFixed(0)}%` : "—"],
        ["Tempo com vontade", `${(m.fracaoVontade() * 100).toFixed(0)}%`], ["Cuidados aceitos", ob.pedidos ? `${((ob.pedidos - ob.recusas) / ob.pedidos * 100).toFixed(0)}% de ${ob.pedidos}` : "—"],
        ["Recusas", ob.recusas - ob.fazerOutra], ["Fez outra coisa", ob.fazerOutra]]} />
    </section>
  );
}
function Decisoes() {
  const { motor: m } = useJogo();
  return (
    <section class="bloco">
      <h2>Últimas decisões e o porquê</h2>
      <p class="dl-apoio">A fala nunca inventa causa: só cita um fator quando o que ele aprendeu mudou a escolha. No resto, quem decidiu foi o instinto e o acaso, e ele não sabe dizer por quê.</p>
      <div class="decisoes">
        {m.motivos.slice(-12).reverse().map((mot, i) => (
          <div key={i}><span class="t">D{diaDe(mot.tick)} {hhmm(mot.tick)}</span> <b>{NOME_PET[mot.acao as keyof typeof NOME_PET] || (mot.recusa ? `desobedeceu (${mot.recusa.acaoDono})` : mot.acao)}</b>{" "}
            <span class="dl-apoio">[{mot.fatores.join(", ") || "sem fator"}]</span> {falaDe(m, mot)}</div>
        ))}
      </div>
    </section>
  );
}
export function TelaAprend() {
  return <div class="tela dl"><Jeito /><Tracos /><Politica /><Memoria /><Obediencia /><Decisoes /></div>;
}
