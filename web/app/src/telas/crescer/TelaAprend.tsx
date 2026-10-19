/* Aprendizado (pranchas EnsinarAgora, EnsinarPolitica, EnsinarDecisoes e DiarioLembrancas): secoes num grupo de
   botoes. Agora: o que ele acabou de fazer, elogiar ou repreender e o que isso muda. Instinto x aprendido:
   recompensas e as duas barras por acao, rotulo so onde divergem. Decisoes: as ultimas com o chip da causa ou
   "? instinto e acaso", mais desejo e obediencia em blocos. Lembrancas: 4 recentes + 2 duradouras. Jeito:
   temperamento, desejo, vinculo e tracos de combate. Valores exatos recolhidos; tudo vem do motor. */
import { useState } from "react";
import { useDesktop } from "../../desktop.ts";
import {
  ACOES_PET, BASE_CARATER, CAT, CDJ, CME, COMBATE, EIXOS_TEMP, EMOCAO_TXT, FATORES_ESPACOS, FATORES_TXT, NOME_COMB, NOME_PET,
  afinidades, chaveSprite, distInstinto, expressarDesejo, expressarEmocao, expressarTemperamento, nomeForma, observacao, termosObediencia,
  type AcaoDono, type AcaoPet, type Lembranca, type MemoriaEspacos, type Motor, type MotivoVida,
} from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { BarraCarater, Numeros, comSinal, dec } from "../../componentes/Barras.tsx";
import { Grade, Peca } from "../../componentes/Imagens.tsx";
import { falaDe, idxDoOrdinal } from "../../fala.ts";
import { AMPULHETA } from "../../grades.ts";
import { jogoAtual, mudarMotor, useJogo } from "../../jogo.ts";
import { ajustarVelocidadeChamado } from "../../tempo.ts";
import { diaDe, hhmm, lutasDaCausa } from "../pet/TelaPet.tsx";

const NOME_MEM: Record<string, string> = { demora: "Você me deixou esperando", bronca: "Broncas", elogio: "Elogios", carinho: "Carinho" };
const EMOTE_MEM: Record<string, string> = { elogio: "emoji_joinha", carinho: "emoji_coracao", bronca: "emoji_exclam" };
const EMOTE_FATOR: Record<string, string> = { fome: "emoji_carne", necessidade_fome: "emoji_carne", elogio: "emoji_joinha", elogios: "emoji_joinha",
  carinho: "emoji_coracao", bronca: "emoji_exclam", repreensoes: "emoji_exclam" };
const EMOTE_EMOCAO: Record<string, string> = { alegria: "emoji_feliz", euforia: "emoji_feliz", orgulho: "emoji_feliz", ternura: "emoji_coracao" };
const FATOR_DEMORA = new Set(["demora", "latencia_fome", "latencia_higiene", "tempo_sem_cuidado"]);
const CORES_AMPULHETA = { k: "#173A8A", w: "#FFFFFF", y: "#F0B429" };
const SECOES = ["Agora", "Instinto × aprendido", "Decisões", "Lembranças", "Jeito"] as const;
type Secao = typeof SECOES[number];
const pct = (x: number): string => `${(x * 100).toFixed(0)}%`;
const nomeAcao = (mot: MotivoVida): string => NOME_PET[mot.acao as AcaoPet] || (mot.recusa ? `desobedeceu (${mot.recusa.acaoDono})` : mot.acao);

function IconeFator({ f, esc = 1 }: { f: string; esc?: number }) {
  if (EMOTE_FATOR[f]) return <Peca nome={EMOTE_FATOR[f]} escala={esc} />;
  if (FATOR_DEMORA.has(f)) return <Grade grade={AMPULHETA} escala={esc + 1} cores={CORES_AMPULHETA} alt="" />;
  return null;
}

/* ------------------------------------------------ Agora (EnsinarAgora) */
/** situacao de agora em palavras, pelas mesmas grandezas da observacao do motor */
function situacao(v: number[]): string {
  const nivel = (x: number) => (x < .34 ? "baixa" : x < .67 ? "média" : "alta");
  const partes = [`comida ${nivel(v[0])}`, `energia ${nivel(v[2])}`, v[6] >= .5 ? "dormindo" : v[7] >= .25 && v[7] < .75 ? "de dia" : "de noite"];
  return partes.join(", ");
}
function Agora() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas();
  const ult = m.pol.ultima, acao = ult ? ult[1] : null;
  /* desde quando: a primeira das decisoes seguidas com a mesma acao */
  const mot = m.motivos.filter((x): x is MotivoVida => x.origem === "vida");
  let desde: number | null = null;
  for (let i = mot.length - 1; i >= 0 && mot[i].acao === acao; i--) if (i > 0 && mot[i - 1].acao !== acao) desde = mot[i].tick;
  const fala = m.motivo && m.motivo.origem === "vida" ? falaDe(m, m.motivo) : "";
  let pet = null;
  if (a.tipo === "ok" && nascendo === 0) {
    const nome = chaveSprite(m.forma), esc = Math.max(1, Math.min(3, Math.floor(168 / dimSprite(a.dados, nome)[1])));
    pet = imagemAtlas(a, nome, esc);
  }
  const agir = (x: AcaoDono) => { if (nascendo > 0 || jogoAtual().motor.morte) return; mudarMotor(mm => mm.observar(x)); ajustarVelocidadeChamado(); };
  const des = nascendo > 0 || !acao;
  return (
    <>
      <section className="ensinar-palco dl-hexcard" aria-label="O que ele acabou de fazer">
        <span className="ensinar-anel" aria-hidden="true" />
        {pet && <img className="dl-pix ensinar-pet" src={pet.url} width={pet.w} height={pet.h} alt={nomeForma(m.forma)} />}
        <div className="ensinar-acabou"><span>ACABOU DE</span><b>{acao ? NOME_PET[acao] : "…"}</b>{desde !== null && <span className="dl-lcd">há {m.e.tick - desde} min</span>}</div>
        {fala && <span className="dl-balao ensinar-balao">{fala}</span>}
      </section>
      <div className="ensinar-bts">
        <button type="button" className="dl-btn dl-btn--destaque" disabled={des} onClick={() => agir("elogiar")}><Peca nome="emoji_joinha" escala={2} />Elogiar</button>
        <button type="button" className="dl-btn dl-btn--sec" disabled={des} onClick={() => agir("repreender")}><Peca nome="emoji_exclam" escala={2} />Repreender</button>
      </div>
      {acao && (
        <div className="ensinar-muda dl-malha">
          <b>O QUE MUDA</b>
          <span>Ajusta a vontade de {NOME_PET[acao].toLowerCase()} numa situação como esta: {situacao(observacao(m.e).v)}.</span>
        </div>
      )}
      <p className="dl-apoio">Atender rápido um pedido de atenção também conta como recompensa.</p>
    </>
  );
}

/* ------------------------------------------------ Instinto x aprendido (EnsinarPolitica) */
function Politica() {
  const { motor: m } = useJogo(), obs = observacao(m.e), p0 = distInstinto(obs), pm = m.pol.media(obs), r = m.pol.rec;
  return (
    <>
      <div className="ensinar-cont">
        <div className="dl-card"><Peca nome="emoji_joinha" escala={2} /><span className="dl-num">{r.elogio}</span><span className="dl-apoio">elogios</span></div>
        <div className="dl-card"><Peca nome="emoji_exclam" escala={2} /><span className="dl-num">{r.repreensao}</span><span className="dl-apoio">broncas</span></div>
        <div className="dl-card"><Peca nome="emoji_coracao" escala={2} /><span className="dl-num">{r.atendido}</span><span className="dl-apoio">atendeu rápido</span></div>
      </div>
      <section className="dl-card bloco">
        <span className="ensinar-cab"><h2>No estado de agora</h2><span className="dl-apoio">{situacao(obs.v)}</span></span>
        <div className="legenda"><span className="leg-instinto">instinto</span><span className="leg-aprendido">o que aprendeu com você</span></div>
        <div className="linhas">
          {ACOES_PET.map(a => {
            const d = pm[a] - p0[a];
            return (
              <div className="pol-linha" key={a}>
                <span className="pol-cab"><b>{NOME_PET[a]}</b>{Math.abs(d) >= .05 && <span className={d > 0 ? "pol-mais" : "pol-menos"}>{d > 0 ? "mais" : "menos"} que o instinto</span>}</span>
                <div className="bar prior" role="img" aria-label={`instinto ${Math.round(p0[a] * 100)}%`}><i style={{ width: `${(p0[a] * 100).toFixed(1)}%` }} /></div>
                <div className="bar agora" role="img" aria-label={`aprendido ${Math.round(pm[a] * 100)}%`}><i className="dl-malha" style={{ width: `${(pm[a] * 100).toFixed(1)}%` }} /></div>
              </div>
            );
          })}
        </div>
        <p className="dl-apoio">Chance de cada ação agora. O rótulo só aparece onde o que ele aprendeu se afastou 5 pontos ou mais do instinto.</p>
        <details className="dl-apoio"><summary>Valores exatos</summary>
          <p>{ACOES_PET.map(a => `${NOME_PET[a].toLowerCase()} ${pct(p0[a])} → ${pct(pm[a])}`).join(", ")}. Pedidos de atenção ignorados: {r.ignorado} (contam como castigo para chamar atenção).</p>
        </details>
      </section>
    </>
  );
}

/* ------------------------------------------------ Decisoes (EnsinarDecisoes) */
function Decisoes({ max = 8 }: { max?: number }) {
  const { motor: m } = useJogo();
  /* uma linha por mudanca: decisoes seguidas iguais (mesma acao e mesmos fatores) viram uma, com a hora da primeira */
  const lin: MotivoVida[] = [];
  for (const x of m.motivos) {
    if (x.origem !== "vida") continue;
    const p = lin[lin.length - 1];
    if (!p || p.acao !== x.acao || p.fatores.join() !== x.fatores.join() || !!p.recusa !== !!x.recusa) lin.push(x);
  }
  const dz = m.dz, ob = m.obed;
  return (
    <>
      <section className="dl-card bloco">
        <h2>Últimas decisões e o porquê</h2>
        <div className="decisoes">
          {lin.slice(-max).reverse().map((mot, i) => {
            const f = mot.fatores[0];
            return (
              <div className="dec" key={i}>
                <span className="dl-lcd">{hhmm(mot.tick)}</span>
                <span className="dec-corpo"><b>{nomeAcao(mot)}</b>
                  {f ? <span className="dec-causa" title={falaDe(m, mot)}><IconeFator f={f} />{FATORES_TXT[f]?.marcador ?? f}{mot.fatores.length > 1 ? ` +${mot.fatores.length - 1}` : ""}</span>
                    : <span className="dec-acaso">? instinto e acaso · ele não sabe dizer</span>}
                </span>
              </div>
            );
          })}
        </div>
      </section>
      <p className="dl-apoio">A causa só aparece quando o que ele aprendeu mudou a escolha. No resto, decidiram o instinto e o acaso.</p>
      {m.versao >= 2 && (
        <section className="dl-card bloco">
          <h2>Desejo e obediência</h2>
          <div className="ensinar-num">
            {([[dz.vontades, "vontades anunciadas"], [dz.vontades ? pct(dz.cumpridas / dz.vontades) : "—", "cumpridas em 1 h"],
              [ob.pedidos ? pct((ob.pedidos - ob.recusas) / ob.pedidos) : "—", "cuidados aceitos"], [ob.recusas - ob.fazerOutra, "recusas"],
              [ob.fazerOutra, "fez outra coisa"], [pct(m.fracaoVontade()), "tempo com vontade"]] as [string | number, string][]).map(([v, k]) => (
              <span key={k}><span className="dl-num">{v}</span><span className="dl-apoio">{k}</span></span>
            ))}
          </div>
          <details className="dl-apoio"><summary>Como funciona</summary>
            <p>Cumprimento: das vontades que ele anunciou, quantas ele fez de fato em até 1 h. Se for baixo, a fala promete o que o pet não faz. Obediência: quantos cuidados seus ele aceitou ({ob.pedidos} pedidos).</p>
          </details>
        </section>
      )}
    </>
  );
}

/* ------------------------------------------------ Lembrancas (DiarioLembrancas) */
function Lembrancas() {
  const { motor: m } = useJogo(), tick = m.e.tick, f = m.pol.mem.feat(tick);
  if (m.versao < 2) {
    return (
      <section className="dl-card bloco">
        <h2>O que ele lembra de você</h2>
        <p className="dl-apoio">Memória curta (pet de versão antiga, sem espaços): quanto você demorou para atender o último pedido de comida ou de limpeza, e as broncas e elogios recentes (somem com o tempo).</p>
        <Numeros itens={(["Demora com a comida", "Demora para limpar", "Broncas recentes", "Elogios recentes"]).map((k, i) => [k, pct(f[i])])} />
      </section>
    );
  }
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
  if (m.versao < 8) return "pet de versão antiga: sem confiança de combate (um pet novo já nasce com ela)";
  const e = m.estadoConfianca()!, n = lutasDaCausa(m, e.lutas, e.estado).length;
  const desde = e.desde !== null ? ` desde D${diaDe(e.desde)} ${hhmm(e.desde)}` : "";
  if (e.estado === "confiante") return `confiante${desde}: ganhou as últimas (${n} ${n === 1 ? "vitória" : "vitórias"} no registro); nada muda na luta`;
  if (e.estado === "inseguro") return `inseguro${desde}: perdeu as últimas (${n} ${n === 1 ? "derrota" : "derrotas"} no registro); hesita e erra mais na luta`;
  if (e.estado === "entediado") return `entediado do rival${desde}: as últimas ${n} lutas foram contra rival repetido; elas ensinam e rendem menos`;
  return m.conf!.historico.length ? "sem estado marcante: nem confiante nem inseguro" : "ainda não lutou: nem confiante nem inseguro";
}
function Jeito() {
  const { motor: m } = useJogo(), e = m.e, est = m.estagioAtual, des = m.desejoAtual(m.observacaoAgora(), e.tick);
  const vinculo = m.versao >= 11 ? `${(m.vinc.valor * 100).toFixed(0)}% · sobe quando você atende uma vontade dele`
    : m.versao >= 2
    ? `${(m.vinc.valor * 100).toFixed(0)}% · sem conflito, aceita um cuidado com ${(termosObediencia(m.vinc.valor, m.temp.teimosia, 0, null)[0] * 100).toFixed(0)}% de chance`
    : "pet de versão antiga: sem vínculo nem recusa (um pet novo já nasce com eles)";
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

/** pets v11: o cerebro e o A (os lobos), nao o Bandit. As secoes do Bandit (Agora, Instinto x aprendido e Decisoes) nao valem para
    ele; o painel DigiBrain, que mostra o cerebro A, e a etapa 5. Ficam as lembrancas (a memoria por espacos) e o jeito */
function TelaAprendV11() {
  const desk = useDesktop();
  return (
    <div className={desk ? "tela dl desk aprend-desk" : "tela dl"}>
      <div className={desk ? "desk-col aprend-col" : ""}>
        <section className="dl-card bloco">
          <h2>O cérebro deste pet</h2>
          <p className="dl-apoio">Ele decide pelo instinto e aprende sozinho com o que as próprias ações fazem no corpo dele: comer quando tem
            fome, brincar quando está entediado, o seu carinho e o seu tapa. Não há elogio nem bronca. O painel com as decisões do cérebro
            vem numa próxima versão do jogo.</p>
        </section>
        <Lembrancas />
      </div>
      <div className={desk ? "desk-col aprend-col" : ""}><Jeito /></div>
    </div>
  );
}

export function TelaAprend() {
  const [secao, setSecao] = useState<Secao>("Agora"), desk = useDesktop(), { motor: m } = useJogo();
  if (m.versao >= 11) return <TelaAprendV11 />;
  /* desktop (AprendizadoDesktop): as secoes lado a lado, sem as abas internas */
  if (desk) return (
    <div className="tela dl desk aprend-desk">
      <div className="desk-col aprend-col"><section className="aprend-agora-card"><Agora /></section></div>
      <div className="desk-col aprend-col"><Politica />
        <details className="aprend-jeito"><summary>Jeito: temperamento e desejo</summary><Jeito /></details></div>
      <div className="desk-col aprend-col"><Decisoes max={4} /><Lembrancas /></div>
    </div>
  );
  return (
    <div className="tela dl">
      <div className="aprend-secoes" role="group" aria-label="Seções">
        {SECOES.map(s => <button type="button" key={s} aria-pressed={secao === s} onClick={() => setSecao(s)}>{s}</button>)}
      </div>
      {secao === "Agora" ? <Agora /> : secao === "Instinto × aprendido" ? <Politica /> : secao === "Decisões" ? <Decisoes /> : secao === "Lembranças" ? <Lembrancas /> : <Jeito />}
    </div>
  );
}
