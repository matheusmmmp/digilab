/* Treinar (docs/TAREFA_V2_TREINO.md; L2 de "Lugares da ilha", prancha crescer_treinar_*): o estado do treino numa palavra ("Pronto") e o ultimo treino
   ("Corrida 07:31"; o intervalo vai para o balao), os 6 exercicios em grade 3 x 2 com o ganho de cada um e a estrela da aptidao, a fadiga e a
   sobrecarga so em numero (as marcas 40/60 e 30/60 ficam na barra e no aria-label) e o Forcar. O pet treina no saco de pancada da propria ilha
   (a sala e o resumo de stats de antes saíram: a ilha ja mostra o pet, e a prancha nao os desenha). Acima de 60 de fadiga todos viram FORCAR e a
   confirmacao e uma folha com o que ganha e o que custa. Sem minigame, sem nivel e sem XP: o motor nao tem. Tudo o que aparece vem do motor (CTR, CMG,
   CSO, APTIDAO e o treino do pet). */
import { useEffect, useId, useRef, useState } from "react";
import { Crosshair, Dumbbell, Flower2, Footprints, Shield, Star, Wind, type LucideIcon } from "lucide-react";
import {
  APTIDAO, CMG, CSO, CTR, NOME_ESP, NOME_EXERCICIO, NOME_STAT, STATS, type EstagioTreino, type Exercicio, type Stat,
} from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { ComDica, ComoFunciona } from "../../componentes/Dica.tsx";
import { Seg, blocos, dec } from "../../componentes/Barras.tsx";
import { abrirModal } from "../../componentes/modal.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { PecaTrancada } from "../../componentes/PecaTrancada.tsx";
import { useNivel } from "../../nivelTela.ts";
import { pecaAberta } from "../../nivel.ts";
import { hhmm } from "../pet/TelaPet.tsx";
import { CENA } from "../pet/cenaEstado.ts";
import { emitirMusica, emitirSom } from "../../somEventos.ts";

/* icones de treino do UP (hexagonos pintados, nao pixel art): 54 x 61 no botao, como pede o guia (secao 6) */
const ICONE_TREINO: Record<Exercicio, string> = { levantar_pedra: "treino_pedra", corrida: "treino_corrida", alvo: "treino_soco", esquiva: "treino_arrancada", meditar: "treino_cachoeira", resistencia: "treino_saco" };
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];
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

/** os tetos do estagio de treino (o Mega com os de CMG); null no In-Training, que nao treina */
function tetos(m: { treino: { estagio: string } }): { est: EstagioTreino | "mega"; estagio: number; vida: number } | null {
  const est = m.treino.estagio;
  if (est === "mega") return { est, estagio: CMG.tetoEstagio, vida: CMG.tetoVida };
  if (!(est in CTR.tetoEstagio)) return null;
  return { est: est as EstagioTreino, estagio: CTR.tetoEstagio[est as EstagioTreino], vida: CTR.tetoVida };
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

/** um medidor so em numero (L2): a barra com as marcas (o rotulo delas vai no aria-label) e o valor; a sobrecarga usa --hx-sombrio */
function Medida({ rot, valor, marcas, sombrio }: { rot: string; valor: number; marcas: [number, string][]; sombrio?: boolean }) {
  return (
    <div className="trn2-med">
      <span className="lg-rot">{rot}</span>
      <span className={`trn2-barra${sombrio ? " trn2-barra--sombrio" : ""}`} role="img" aria-label={`${rot} ${valor.toFixed(0)} de 100; marcas ${marcas.map(([x, r]) => `${x}: ${r}`).join("; ")}`}>
        <i style={{ width: `${Math.min(100, valor)}%` }} />{marcas.map(([x]) => <span key={x} className="lim" style={{ left: `${x}%` }} />)}
      </span>
      <em>{valor.toFixed(0)}</em>
    </div>
  );
}

export function TelaTreinar({ lutando = false }: { lutando?: boolean }) {
  const { motor: m, nascendo } = useJogo(), [msg, setMsg] = useState(""), [confirmar, setConfirmar] = useState<Exercicio | null>(null), [escolher, setEscolher] = useState(false);
  const t = m.treino, bebe = m.estagioAtual === "bebe", pode = t.podeTocar(m.e.tick), mult = t.forcaria ? CTR.multForcar : 1, tt = tetos(m), ult = ultimoExercicio(m.log);
  /* SOM-UP: a musica do treino do Digimon UP enquanto a tela esta aberta */
  useEffect(() => { emitirMusica("treino", { lugar: "treino" }); return () => emitirMusica("treino", null); }, []);
  const treinar = (ex: Exercicio) => {
    try {
      let texto = "";
      mudarMotor(mm => {
        const s = mm.treinar(ex);
        emitirSom(`treino_${ex}`);                /* SOM-UP: o aparelho do treino (so som) */
        CENA.treino = performance.now();         /* a ilha mostra o pet no saco de pancada (so vista) */
        const g = Object.entries(s.ganho).map(([k, v]) => `+${dec(v as number, 2)} ${NOME_STAT[k as Stat] || k}`).join(", ");
        texto = s.enrolou ? "Ele enrolou: a sessão não rendeu." + (s.forcada ? " A sobrecarga entrou mesmo assim." : "")
          : `${s.forcada ? "Forçado: " : ""}${g || "sem ganho (teto atingido)"}.${mm.pausaTreino ? " Ele pediu pausa." : ""}`;
      });
      setMsg(texto);
    } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const apt = APTIDAO[m.especie], fortes = STATS.filter(k => apt[k] > 1).sort((x, y) => apt[y] - apt[x]);
  /* o estado numa palavra (L2, regra do texto); o intervalo e a frase do treino vao para o balao */
  const estado = bebe ? "Não treina" : t.pedePausa ? "Pausa" : !pode ? "Descansa" : "Pronto";
  const falta = !bebe && !pode && !t.pedePausa && t.ultimo !== null ? CTR.intervalo - (m.e.tick - t.ultimo) : null;
  const idForcar = useId(), nivel = useNivel(), desabilitaForcar = !t.forcaria || bebe || !pode || lutando || nascendo > 0;
  return (
    <div className="tela dl trn2-tela lg">
      <div className="lg-destaque lg-linha" role="status">
        <b className="trn2-status trn2-estado">{estado}</b>{falta !== null && <span className="lg-num lg-num--p">{falta}<small> min</small></span>}
        {ult && (
          <ComDica className="lg-sec lg-linha trn2-ultimo" rotulo={`Último treino: ${NOME_EXERCICIO[ult.ex]} às ${hhmm(ult.tick)}`} dica={<>Um treino por vez, com {CTR.intervalo} min de intervalo.</>}>
            <span style={{ marginLeft: "auto" }}>{NOME_EXERCICIO[ult.ex]} {hhmm(ult.tick)}</span>
          </ComDica>
        )}
      </div>
      <div className="trn2-grade treino-grade" role="group" aria-label="Exercícios">
        {EXERCICIOS.map(ex => {
          const [pri, sec] = CTR.exercicios[ex], des = bebe || !pode || lutando || nascendo > 0, forte = apt[pri] > 1;
          return (
            <button type="button" key={ex} className={`treino-ex${t.forcaria ? " forcar" : ""}`} disabled={des}
              aria-label={`${t.forcaria ? "Forçar" : "Treinar"} ${NOME_EXERCICIO[ex]}${forte ? ": aptidão" : ""}${t.forcaria ? ": gera sobrecarga" : ""}, +${n1(CTR.ganhoPri * mult)} ${NOME_STAT[pri]} +${n1(CTR.ganhoSec * mult)} ${NOME_STAT[sec]}`}
              onClick={() => (t.forcaria ? setConfirmar(ex) : treinar(ex))}>
              {forte && <span className="lg-etq lg-etq--alerta"><Star aria-hidden="true" /></span>}
              <IconeTreino ex={ex} />
              <b>{NOME_EXERCICIO[ex]}</b>
              <small>+{n1(CTR.ganhoPri * mult)} {NOME_STAT[pri]} +{n1(CTR.ganhoSec * mult)} {NOME_STAT[sec]}</small>
              {t.forcaria && <span className="treino-perigo"><span>FORÇAR</span></span>}
            </button>
          );
        })}
      </div>
      <p className="trn2-msg lg-sec" aria-live="polite" style={{ margin: 0 }}>{msg}</p>
      <section className="trn2-cansaco" aria-label="Cansaço" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Medida rot="Fadiga" valor={t.fadiga} marcas={[[CTR.limiarPausa, "pede pausa"], [CTR.limiteForcar, "só forçar"]]} />
        <Medida rot="Sobrecarga" valor={t.sobrecarga} marcas={[[CSO.aviso, "aviso"], [CSO.sombrio, "sombria"]]} sombrio />
      </section>
      <div className="lg-linha">
        {/* o Forcar abre no Champion (Nv 6, P-4): antes, o botao trancado com o marco; o motor nao muda */}
        {pecaAberta(nivel, "forcar")
          ? <ComDica foco={false} idBalao={idForcar} dica={t.forcaria ? "Rende mais e gera sobrecarga." : <>Abre com fadiga {CTR.limiteForcar}.</>}>
            <button type="button" className="dl-btn dl-btn--sec treino-forcar" disabled={desabilitaForcar} aria-describedby={idForcar} onClick={() => setEscolher(true)}>
              <span className="treino-forcar-faixa" aria-hidden="true" />Forçar</button>
          </ComDica>
          : <PecaTrancada peca="forcar" />}
        {tt && <span className="lg-sec" style={{ marginLeft: "auto" }}>estágio <b className="lg-num lg-num--p">{n1(t.pontosEst[tt.est] ?? 0)}/{tt.estagio}</b></span>}
      </div>
      <ComoFunciona>
        Um toque por sessão, com pelo menos {CTR.intervalo} min entre elas. Cada exercício sobe um stat principal e um secundário (com a aptidão do brasão e retorno decrescente; tetos de +{CTR.tetoStat} por stat e +{tt?.vida ?? CTR.tetoVida} na vida).
        {fortes.length ? ` A estrela é a aptidão do brasão: ${NOME_ESP[m.especie]} rende ${fortes.map(k => `${n1(apt[k])}× em ${NOME_STAT[k]}`).join(" e ")}.` : ""} A fadiga reduz o ganho e passa com o tempo
        acordado e com o sono; com fadiga {CTR.limiarPausa} ele pede pausa. Com fadiga {CTR.limiteForcar} o botão vira <b>Forçar</b>: rende mais, mas gera <b>sobrecarga</b>, que não some na evolução. Sobrecarga alta na virada
        para Ultimate leva à <b>forma sombria</b>. Cada ponto treinado vale 3 pontos de stat no combate. Na arena o treino muda o perfil (stats normalizados); na campanha vale o ganho inteiro.
      </ComoFunciona>
      {escolher && <EscolherForcar escolher={ex => { setEscolher(false); setConfirmar(ex); }} fechar={() => setEscolher(false)} />}
      {confirmar && <ConfirmarForcar ex={confirmar} fechar={() => setConfirmar(null)} forcar={() => treinar(confirmar)} />}
    </div>
  );
}
