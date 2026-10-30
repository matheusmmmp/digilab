/* Treinar (docs/TAREFA_V2_TREINO.md: composicao propria a partir da terceira tela da referencia; antes, pranchas TreinoNormal, TreinoPausa,
   TreinoForcar e TreinoDesktop): a sala clara com o pet grande na plataforma de luz, o estado do treino e o balao "pausa?"; o stat em foco
   (o principal do ultimo exercicio: os pontos dele de 10, os do estagio e os da vida); fadiga com as marcas 40 (pede pausa) e 60 (so
   forcar); sobrecarga roxa com 30 (aviso) e 60 (sombria); os 6 exercicios em grade 3 x 2 (acima de 60 todos viram FORCAR listrado e a
   confirmacao e uma folha com o que ganha e o que custa); o treinado na vida, stat a stat; o ultimo treino. Sem minigame, sem nivel e sem
   XP: o motor nao tem. Tudo o que aparece vem do motor (CTR, CMG, CSO, APTIDAO e o treino do pet). */
import { useEffect, useRef, useState } from "react";
import { Crosshair, Dumbbell, Flower2, Footprints, Shield, Wind, type LucideIcon } from "lucide-react";
import {
  APTIDAO, CMG, CSO, CTR, NOME_ESP, NOME_EXERCICIO, NOME_STAT, STATS, corDominante, type EstagioTreino, type Exercicio, type Stat,
} from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { PetGrande } from "../../componentes/Revelacao.tsx";
import { Seg, blocos, dec } from "../../componentes/Barras.tsx";
import { Grade } from "../../componentes/Imagens.tsx";
import { AMPULHETA } from "../../grades.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { hhmm } from "../pet/TelaPet.tsx";

/* icones de treino do UP (hexagonos pintados, nao pixel art): 54 x 61 no botao, como pede o guia (secao 6) */
const ICONE_TREINO: Record<Exercicio, string> = { levantar_pedra: "treino_pedra", corrida: "treino_corrida", alvo: "treino_soco", esquiva: "treino_arrancada", meditar: "treino_cachoeira", resistencia: "treino_saco" };
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];
const CORES_AMPULHETA = { k: "#173A8A", w: "#FFFFFF", y: "#F0B429" };
const n1 = (x: number): string => dec(x, 1).replace(/,0$/, "");

/* sem o atlas do UP (o CI, as capturas do repositorio): os icones do lucide */
const ICONE_RESERVA: Record<Exercicio, LucideIcon> = { levantar_pedra: Dumbbell, corrida: Footprints, alvo: Crosshair, esquiva: Wind, meditar: Flower2, resistencia: Shield };
function IconeTreino({ ex }: { ex: Exercicio }) {
  const a = useAtlas();
  if (a.tipo !== "ok") { const I = ICONE_RESERVA[ex]; return <span className="treino-ic treino-ic--reserva" aria-hidden="true"><I size={30} strokeWidth={2.2} /></span>; }
  return <img className="treino-ic" src={imagemAtlas(a, ICONE_TREINO[ex]).url} width={54} height={61} alt="" />;
}
/** o ultimo exercicio do registro (o evento "tr"), ou null */
function ultimoExercicio(log: readonly (readonly unknown[])[]): { tick: number; ex: Exercicio } | null {
  for (let i = log.length - 1; i >= 0; i--) if (log[i][1] === "tr") return { tick: log[i][0] as number, ex: log[i][2] as Exercicio };
  return null;
}

/** a sala de treino: parede clara com janela e chao em CSS (o fundo do UP so com o atlas local), o pet grande e nitido na plataforma de
    luz, o estado do treino e o balao "pausa?" quando o motor pede pausa */
function Sala() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), t = m.treino, bebe = m.estagioAtual === "bebe", pode = t.podeTocar(m.e.tick);
  const fundo = a.tipo === "ok" ? imagemAtlas(a, "fundo_treino").url : null;
  const estado = bebe ? "o In-Training ainda não treina" : t.pedePausa ? "pediu pausa" : !pode ? `descansando: próximo em ${CTR.intervalo - (m.e.tick - t.ultimo!)} min`
    : "pronto para treinar";
  return (
    <section className={`trn-sala${fundo ? " trn-sala--up" : ""}`} aria-label="Sala de treino" style={fundo ? { backgroundImage: `url(${fundo})` } : undefined}>
      {!fundo && <span className="trn-janela" aria-hidden="true"><i /><i /></span>}
      <span className="evm-plataforma trn-plataforma" aria-hidden="true"><i /><i /><i /></span>
      {nascendo === 0 && <span className="trn-pet"><PetGrande f={m.forma} alvo={[180, 150]} cor={corDominante(m.tracos)} sombria={m.sombria} maxEscala={4} /></span>}
      <span className={`trn-estado${t.pedePausa ? " trn-estado--pausa" : ""}`}>{estado}</span>
      {t.pedePausa && <span className="dl-balao trn-balao"><Grade grade={AMPULHETA} escala={2} cores={CORES_AMPULHETA} alt="" /> pausa?</span>}
    </section>
  );
}

/** o nome do stat com a inicial maiuscula (NOME_STAT e minusculo, para ir no meio da frase) */
const nomeStat = (k: Stat): string => NOME_STAT[k][0].toUpperCase() + NOME_STAT[k].slice(1);
/** uma barra de 0 a `de` (o teto do stat, do estagio ou da vida) */
const Barra = ({ v, de }: { v: number; de: number }) => <span className="trn-barra" aria-hidden="true"><i style={{ width: `${Math.min(100, v / de * 100)}%` }} /></span>;
/** os tetos do estagio de treino (o Mega com os de CMG); null no In-Training, que nao treina */
function tetos(m: { treino: { estagio: string } }): { est: EstagioTreino | "mega"; estagio: number; vida: number } | null {
  const est = m.treino.estagio;
  if (est === "mega") return { est, estagio: CMG.tetoEstagio, vida: CMG.tetoVida };
  if (!(est in CTR.tetoEstagio)) return null;
  return { est: est as EstagioTreino, estagio: CTR.tetoEstagio[est as EstagioTreino], vida: CTR.tetoVida };
}
/** o stat em foco: o principal do ultimo exercicio (o primeiro, sem treino), com os pontos dele de 10 e os do estagio e da vida. E o que o
    motor tem no lugar do "nivel" da referencia */
function StatFoco() {
  const { motor: m } = useJogo(), t = m.treino, ult = ultimoExercicio(m.log), ex = ult?.ex ?? EXERCICIOS[0], st = CTR.exercicios[ex][0], tt = tetos(m);
  return (
    <section className="trn-card trn-foco" aria-labelledby="trn-foco-tit">
      <span className="trn-foco-ic"><IconeTreino ex={ex} /></span>
      <span className="trn-foco-txt">
        <span className="trn-rot">{ult ? `stat do último treino · ${NOME_EXERCICIO[ex]}` : "stat em foco"}</span>
        <b id="trn-foco-tit">{nomeStat(st)} +{n1(t.pontos[st])} <small>de {CTR.tetoStat}</small></b>
        <Barra v={t.pontos[st]} de={CTR.tetoStat} />
        <span className="trn-foco-sub">{tt ? `no estágio ${n1(t.pontosEst[tt.est] ?? 0)} de ${tt.estagio} · na vida ${n1(t.total)} de ${tt.vida}` : `na vida ${n1(t.total)} de ${CTR.tetoVida}`}</span>
      </span>
    </section>
  );
}
/** o treinado na vida, stat a stat (de 0 a 10), e o total */
function Vida() {
  const { motor: m } = useJogo(), t = m.treino, tt = tetos(m);
  return (
    <section className="trn-card trn-vida" aria-labelledby="trn-vida-tit">
      <h2 className="trn-tit" id="trn-vida-tit"><span>Treinado na vida</span><span className="dl-lcd">+{n1(t.total)} / {tt?.vida ?? CTR.tetoVida}</span></h2>
      <ul className="trn-stats">
        {STATS.map(k => <li key={k}><span>{nomeStat(k)}</span><Barra v={t.pontos[k]} de={CTR.tetoStat} /><b>+{n1(t.pontos[k])}</b></li>)}
      </ul>
    </section>
  );
}

/** barra segmentada com os rotulos embaixo, cada um na posicao da sua marca */
function Medidor({ titulo, valor, n, cls, marcas }: { titulo: string; valor: number; n: number; cls: string; marcas: [number, string][] }) {
  return (
    <div className="med">
      <span className="med-cab"><b>{titulo}</b><span className={`dl-lcd ${cls === "dl-seg--sombrio" ? "med-roxo" : ""}`}>{valor.toFixed(0)} / 100</span></span>
      <Seg n={n} m={10} cls={cls} marca={marcas.map(([x]) => x / 10)} />
      <span className="med-marcas">{marcas.map(([x, rot]) => <span key={x} style={{ left: `${x}%` }}>{x} · {rot}</span>)}</span>
    </div>
  );
}

/** folha de confirmacao do forcar (TreinoForcar): o que ganha, o que custa, a sobrecarga e o aviso da sombria */
function ConfirmarForcar({ ex, fechar, forcar }: { ex: Exercicio; fechar: () => void; forcar: () => void }) {
  const { motor: m } = useJogo(), ref = useRef<HTMLDialogElement>(null), t = m.treino;
  useEffect(() => { abrirModal(ref.current); }, []);
  const depois = Math.min(CTR.sobreMax, t.sobrecarga + CTR.sobreForcar);
  return (
    <dialog className="folha dl" ref={ref} aria-labelledby="forcar-tit" onClose={fechar}>
      <span className="folha-alca" aria-hidden="true" />
      <div className="folha-cab"><IconeTreino ex={ex} /><span><b id="forcar-tit">Forçar {NOME_EXERCICIO[ex].toLowerCase()}?</b><span className="dl-apoio">A fadiga passou de {CTR.limiteForcar}.</span></span></div>
      <div className="dl-par">
        <div className="folha-ganha"><b>GANHA</b><span>rende {n1(CTR.multForcar)}×</span></div>
        <div className="folha-custa"><b>CUSTA</b><span>+{CTR.sobreForcar} sobrecarga</span><span>vínculo cai</span></div>
      </div>
      <Medidor titulo="Sobrecarga" valor={t.sobrecarga} n={blocos(t.sobrecarga / 100, 10)} cls="dl-seg--sombrio" marcas={[[CSO.aviso, "aviso"], [CSO.sombrio, "sombria"]]} />
      <p className="folha-aviso">Com isso a sobrecarga vai a {depois.toFixed(0)}.{m.estagioAtual !== "adulto" && m.estagioAtual !== "mega" ? ` Sobrecarga ${CSO.sombrio} ou mais na virada para Ultimate leva à forma sombria.` : ""}</p>
      <div className="folha-bts">
        <button type="button" className="dl-btn" onClick={() => ref.current?.close()}>Descansar</button>
        <button type="button" className="dl-btn dl-btn--forcar" onClick={() => { forcar(); ref.current?.close(); }}>Forçar mesmo assim</button>
      </div>
    </dialog>
  );
}

/** desktop (TreinoDesktop): o ultimo treino do registro e quando sai o proximo */
function UltimoTreino() {
  const { motor: m } = useJogo(), t = m.treino, pode = t.podeTocar(m.e.tick), ult = ultimoExercicio(m.log);
  if (!ult) return <div className="dl-card treino-ult"><span className="dl-apoio">Nenhum treino ainda.</span></div>;
  const ex = ult.ex, [pri, sec] = CTR.exercicios[ex];
  return (
    <div className="dl-card treino-ult">
      <IconeTreino ex={ex} />
      <span className="treino-ult-txt"><small>último treino · {hhmm(ult.tick)}</small><b>{NOME_EXERCICIO[ex]} · {NOME_STAT[pri]} e {NOME_STAT[sec]}</b></span>
      {!pode && t.ultimo !== null && <span className="dl-lcd treino-ult-prox">próximo em {CTR.intervalo - (m.e.tick - t.ultimo)} min</span>}
    </div>
  );
}

/** desktop (TreinoDesktop): Forcar treino escolhe o exercicio e cai na mesma confirmacao de sempre; so abre com a fadiga
    no limite do motor (CTR.limiteForcar), como os proprios cards */
function EscolherForcar({ escolher, fechar }: { escolher: (ex: Exercicio) => void; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), ex = useRef<Exercicio | null>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog className="modal-conf dl" ref={ref} aria-labelledby="forcar-esc-tit" onClose={() => (ex.current ? escolher(ex.current) : fechar())}>
      <h2 id="forcar-esc-tit">Forçar qual treino?</h2>
      <p>Rende mais, mas gera sobrecarga.</p>
      <div className="forcar-lista">{EXERCICIOS.map(e => <button type="button" key={e} className="dl-btn dl-btn--sec" onClick={() => { ex.current = e; ref.current?.close(); }}><IconeTreino ex={e} />{NOME_EXERCICIO[e]}</button>)}</div>
      <button type="button" className="dl-btn dl-btn--sec" onClick={() => ref.current?.close()}>Cancelar</button>
    </dialog>
  );
}

export function TelaTreinar({ lutando = false }: { lutando?: boolean }) {
  const { motor: m, nascendo } = useJogo(), [msg, setMsg] = useState(""), [confirmar, setConfirmar] = useState<Exercicio | null>(null), [escolher, setEscolher] = useState(false);
  const t = m.treino, bebe = m.estagioAtual === "bebe", pode = t.podeTocar(m.e.tick), mult = t.forcaria ? CTR.multForcar : 1;
  const treinar = (ex: Exercicio) => {
    try {
      let texto = "";
      mudarMotor(mm => {
        const s = mm.treinar(ex);
        const g = Object.entries(s.ganho).map(([k, v]) => `+${dec(v as number, 2)} ${NOME_STAT[k as Stat] || k}`).join(", ");
        texto = s.enrolou ? "Ele enrolou: a sessão não rendeu." + (s.forcada ? " A sobrecarga entrou mesmo assim." : "")
          : `${s.forcada ? "Forçado: " : ""}${g || "sem ganho (teto atingido)"}.${mm.pausaTreino ? " Ele pediu pausa." : ""}`;
      });
      setMsg(texto);
    } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const apt = APTIDAO[m.especie], fortes = STATS.filter(k => apt[k] > 1).sort((x, y) => apt[y] - apt[x]);
  return (
    <div className="tela dl treino-tela trn">
      <div className="treino-col-esq">
        <Sala />
        <StatFoco />
        <Vida />
      </div>
      <div className="treino-col-dir">
        <section className="dl-card treino-medidores trn-medidores" aria-labelledby="trn-med-tit">
          <h2 className="trn-tit" id="trn-med-tit">Cansaço</h2>
          <Medidor titulo="Fadiga" valor={t.fadiga} n={blocos(t.fadiga / 100, 10)} cls={t.pedePausa ? "dl-seg--necessidade" : ""} marcas={[[CTR.limiarPausa, "pede pausa"], [CTR.limiteForcar, "só forçar"]]} />
          <Medidor titulo="Sobrecarga" valor={t.sobrecarga} n={blocos(t.sobrecarga / 100, 10)} cls="dl-seg--sombrio" marcas={[[CSO.aviso, "aviso"], [CSO.sombrio, "sombria"]]} />
        </section>
        <section className="trn-exercicios" aria-labelledby="trn-ex-tit">
          <h2 className="trn-tit treino-ex-tit" id="trn-ex-tit"><span>Exercícios</span><small>um treino por vez · {CTR.intervalo} min de intervalo</small></h2>
          {bebe && <p className="dl-apoio" style={{ margin: 0 }}>O In-Training ainda não treina.</p>}
          <div className="treino-grade" role="group" aria-label="Exercícios">
            {EXERCICIOS.map(ex => {
              const [pri, sec] = CTR.exercicios[ex], des = bebe || !pode || lutando || nascendo > 0;
              return (
                <button type="button" key={ex} className={`treino-ex${t.forcaria ? " forcar" : ""}`} disabled={des}
                  aria-label={`${t.forcaria ? "Forçar" : "Treinar"} ${NOME_EXERCICIO[ex]}${t.forcaria ? ": gera sobrecarga" : ""}`}
                  onClick={() => (t.forcaria ? setConfirmar(ex) : treinar(ex))}>
                  {apt[pri] > 1 && <span className="treino-selo">aptidão</span>}
                  <IconeTreino ex={ex} />
                  <b>{NOME_EXERCICIO[ex]}</b>
                  <span className="treino-ganho">+{n1(CTR.ganhoPri * mult)} {NOME_STAT[pri]} · +{n1(CTR.ganhoSec * mult)} {NOME_STAT[sec]}</span>
                  {t.forcaria && <span className="treino-perigo"><span>FORÇAR<small>+ sobrecarga</small></span></span>}
                </button>
              );
            })}
          </div>
          <p className="treino-legenda"><span className="treino-selo">aptidão</span>{fortes.length ? `${NOME_ESP[m.especie]} rende ${fortes.map(k => `${n1(apt[k])}× em ${NOME_STAT[k]}`).join(" e ")}.` : ""} Um treino por vez, com {CTR.intervalo} min de intervalo.</p>
          <p className="dl-apoio trn-msg" aria-live="polite" style={{ margin: 0 }}>{msg}</p>
        </section>
        <section className="trn-ultimo">
          <UltimoTreino />
          <span className="treino-ult-bts">
            <button type="button" className="dl-btn dl-btn--sec treino-forcar" disabled={!t.forcaria || bebe || !pode || lutando || nascendo > 0}
              title={t.forcaria ? "rende mais e gera sobrecarga" : `abre com fadiga ${CTR.limiteForcar}`} onClick={() => setEscolher(true)}>
              <span className="treino-forcar-faixa" aria-hidden="true" />Forçar treino</button>
            {!t.forcaria && <small className="dl-apoio">abre com fadiga {CTR.limiteForcar}</small>}
          </span>
        </section>
        <details className="dl-apoio trn-como"><summary>Como o treino funciona</summary>
          <p>Um toque por sessão, com pelo menos 10 min entre elas. Cada exercício sobe um stat principal e um secundário (com a aptidão do brasão e retorno decrescente; tetos de +10 por stat e +36 na vida). A fadiga reduz o ganho e passa com o tempo acordado e com o sono; com fadiga 40 ele pede pausa. Com fadiga 60 o botão vira <b>Forçar</b>: rende mais, mas gera <b>sobrecarga</b>, que não some na evolução. Sobrecarga alta na virada para Ultimate leva à <b>forma sombria</b>. Cada ponto treinado vale 3 pontos de stat no combate. Na arena o treino muda o perfil (stats normalizados); na campanha vale o ganho inteiro.</p>
        </details>
        {escolher && <EscolherForcar escolher={ex => { setEscolher(false); setConfirmar(ex); }} fechar={() => setEscolher(false)} />}
      </div>
      {confirmar && <ConfirmarForcar ex={confirmar} fechar={() => setConfirmar(null)} forcar={() => treinar(confirmar)} />}
    </div>
  );
}
