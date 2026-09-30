/* Treinar (pranchas TreinoNormal, TreinoPausa e TreinoForcar): sala de treino com o fundo do UP e o pet em 3x,
   estado do treino e o balao "pausa?" quando o motor pede pausa; fadiga com as marcas 40 (pede pausa) e 60
   (so forcar); sobrecarga roxa com 30 (aviso) e 60 (sombria); intervalo entre treinos num card; os 6 exercicios
   em grade 3 x 2, o card inteiro e o botao; acima de 60 todos viram FORCAR listrado e a confirmacao e uma folha
   com o que ganha e o que custa. Tudo o que aparece vem do motor (CTR, CSO, APTIDAO e o treino do pet). */
import { useEffect, useRef, useState } from "preact/hooks";
import {
  APTIDAO, CSO, CTR, NOME_ESP, NOME_EXERCICIO, NOME_STAT, STATS, chaveSprite, nomeForma, type Exercicio, type Stat,
} from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { Seg, blocos, dec } from "../../componentes/Barras.tsx";
import { Grade, Peca } from "../../componentes/Imagens.tsx";
import { AMPULHETA } from "../../grades.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { hhmm } from "../pet/TelaPet.tsx";

/* icones de treino do UP (hexagonos pintados, nao pixel art): 54 x 61 no botao, como pede o guia (secao 6) */
const ICONE_TREINO: Record<Exercicio, string> = { levantar_pedra: "treino_pedra", corrida: "treino_corrida", alvo: "treino_soco", esquiva: "treino_arrancada", meditar: "treino_cachoeira", resistencia: "treino_saco" };
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];
const CORES_AMPULHETA = { k: "#173A8A", w: "#FFFFFF", y: "#F0B429" };
const n1 = (x: number): string => dec(x, 1).replace(/,0$/, "");

function IconeTreino({ ex }: { ex: Exercicio }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return null;
  return <img class="treino-ic" src={imagemAtlas(a, ICONE_TREINO[ex]).url} width={54} height={61} alt="" />;
}

/** sala de treino (prancha TreinoNormal): 190 px de ponta a ponta, fundo do UP, sombra 140 x 16 e o pet em escala
    inteira (ate 3x, sem esticar) com os pes em 170 */
function Sala() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), t = m.treino, bebe = m.estagioAtual === "bebe", pode = t.podeTocar(m.e.tick);
  const fundo = a.tipo === "ok" ? imagemAtlas(a, "fundo_treino").url : null;
  let pet = null;
  if (a.tipo === "ok" && nascendo === 0) {
    const nome = chaveSprite(m.forma), [, h] = dimSprite(a.dados, nome), esc = Math.max(1, Math.min(3, Math.floor(168 / h)));
    const img = imagemAtlas(a, nome, esc);
    pet = <img class="dl-pix sala-pet" src={img.url} width={img.w} height={img.h} alt={nomeForma(m.forma)} />;
  }
  const estado = bebe ? "In-Training ainda não treina" : t.pedePausa ? "pediu pausa" : !pode ? "descansando" : "pronto para treinar";
  return (
    <section class="sala-treino" aria-label="Sala de treino" style={fundo ? { backgroundImage: `url(${fundo})` } : {}}>
      <span class="sala-sombra" aria-hidden="true" />
      {pet}
      <span class="sala-estado">{estado}</span>
      {t.pedePausa && <span class="dl-balao sala-balao"><Grade grade={AMPULHETA} escala={2} cores={CORES_AMPULHETA} alt="" /> pausa?</span>}
    </section>
  );
}

/** barra segmentada com os rotulos embaixo, cada um na posicao da sua marca */
function Medidor({ titulo, valor, n, cls, marcas }: { titulo: string; valor: number; n: number; cls: string; marcas: [number, string][] }) {
  return (
    <div class="med">
      <span class="med-cab"><b>{titulo}</b><span class={`dl-lcd ${cls === "dl-seg--sombrio" ? "med-roxo" : ""}`}>{valor.toFixed(0)} / 100</span></span>
      <Seg n={n} m={10} cls={cls} marca={marcas.map(([x]) => x / 10)} />
      <span class="med-marcas">{marcas.map(([x, rot]) => <span key={x} style={{ left: `${x}%` }}>{x} · {rot}</span>)}</span>
    </div>
  );
}

/** folha de confirmacao do forcar (TreinoForcar): o que ganha, o que custa, a sobrecarga e o aviso da sombria */
function ConfirmarForcar({ ex, fechar, forcar }: { ex: Exercicio; fechar: () => void; forcar: () => void }) {
  const { motor: m } = useJogo(), ref = useRef<HTMLDialogElement>(null), t = m.treino;
  useEffect(() => { abrirModal(ref.current); }, []);
  const depois = Math.min(CTR.sobreMax, t.sobrecarga + CTR.sobreForcar);
  return (
    <dialog class="folha dl" ref={ref} aria-labelledby="forcar-tit" onClose={fechar}>
      <span class="folha-alca" aria-hidden="true" />
      <div class="folha-cab"><IconeTreino ex={ex} /><span><b id="forcar-tit">Forçar {NOME_EXERCICIO[ex].toLowerCase()}?</b><span class="dl-apoio">A fadiga passou de {CTR.limiteForcar}.</span></span></div>
      <div class="dl-par">
        <div class="folha-ganha"><b>GANHA</b><span>rende {n1(CTR.multForcar)}×</span></div>
        <div class="folha-custa"><b>CUSTA</b><span>+{CTR.sobreForcar} sobrecarga</span>{m.versao >= 2 && <span>vínculo cai</span>}</div>
      </div>
      <Medidor titulo="Sobrecarga" valor={t.sobrecarga} n={blocos(t.sobrecarga / 100, 10)} cls="dl-seg--sombrio" marcas={[[CSO.aviso, "aviso"], [CSO.sombrio, "sombria"]]} />
      <p class="folha-aviso">Com isso a sobrecarga vai a {depois.toFixed(0)}.{m.estagioAtual !== "adulto" && m.estagioAtual !== "mega" ? ` Sobrecarga ${CSO.sombrio} ou mais na virada para Ultimate leva à forma sombria.` : ""}</p>
      <div class="folha-bts">
        <button type="button" class="dl-btn" onClick={() => ref.current?.close()}>Descansar</button>
        <button type="button" class="dl-btn dl-btn--forcar" onClick={() => { forcar(); ref.current?.close(); }}>Forçar mesmo assim</button>
      </div>
    </dialog>
  );
}

/** desktop (TreinoDesktop): o ultimo treino do registro e quando sai o proximo */
function UltimoTreino() {
  const { motor: m } = useJogo(), t = m.treino, pode = t.podeTocar(m.e.tick);
  let ev: (typeof m.log)[number] | null = null;
  for (let i = m.log.length - 1; i >= 0; i--) if (m.log[i][1] === "tr") { ev = m.log[i]; break; }
  if (!ev) return <div class="dl-card treino-ult"><span class="dl-apoio">Nenhum treino ainda.</span></div>;
  const ex = ev[2] as Exercicio, [pri, sec] = CTR.exercicios[ex];
  return (
    <div class="dl-card treino-ult">
      <IconeTreino ex={ex} />
      <span class="treino-ult-txt"><small>último treino · {hhmm(ev[0])}</small><b>{NOME_EXERCICIO[ex]} · {NOME_STAT[pri]} e {NOME_STAT[sec]}</b></span>
      {!pode && t.ultimo !== null && <span class="dl-lcd treino-ult-prox">próximo em {CTR.intervalo - (m.e.tick - t.ultimo)} min</span>}
    </div>
  );
}

/** desktop (TreinoDesktop): Forcar treino escolhe o exercicio e cai na mesma confirmacao de sempre; so abre com a fadiga
    no limite do motor (CTR.limiteForcar), como os proprios cards */
function EscolherForcar({ escolher, fechar }: { escolher: (ex: Exercicio) => void; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), ex = useRef<Exercicio | null>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog class="modal-conf dl" ref={ref} aria-labelledby="forcar-esc-tit" onClose={() => (ex.current ? escolher(ex.current) : fechar())}>
      <h2 id="forcar-esc-tit">Forçar qual treino?</h2>
      <p>Rende mais, mas gera sobrecarga.</p>
      <div class="forcar-lista">{EXERCICIOS.map(e => <button type="button" key={e} class="dl-btn dl-btn--sec" onClick={() => { ex.current = e; ref.current?.close(); }}><IconeTreino ex={e} />{NOME_EXERCICIO[e]}</button>)}</div>
      <button type="button" class="dl-btn dl-btn--sec" onClick={() => ref.current?.close()}>Cancelar</button>
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
    <div class="tela dl desk treino-tela">
      <div class="desk-col treino-col-esq">
      <Sala />
      <div class="dl-card treino-medidores">
        <h2 class="desk-so treino-med-tit">Cansaço</h2>
        <Medidor titulo="Fadiga" valor={t.fadiga} n={blocos(t.fadiga / 100, 10)} cls={t.pedePausa ? "dl-seg--necessidade" : ""} marcas={[[CTR.limiarPausa, "pede pausa"], [CTR.limiteForcar, "só forçar"]]} />
        <Medidor titulo="Sobrecarga" valor={t.sobrecarga} n={blocos(t.sobrecarga / 100, 10)} cls="dl-seg--sombrio" marcas={[[CSO.aviso, "aviso"], [CSO.sombrio, "sombria"]]} />
        <div class="med">
          <span class="med-cab"><b>Treinado na vida</b><span class="dl-lcd">+{n1(t.total)} / {CTR.tetoVida}</span></span>
          <span class="dl-apoio">{STATS.filter(k => t.pontos[k] > 0).map(k => `${NOME_STAT[k]} +${dec(t.pontos[k], 1)}`).join(", ") || "nada ainda"}</span>
        </div>
      </div>
      </div>
      <div class="desk-col treino-col-dir">
      <h2 class="desk-so treino-ex-tit"><span>Exercícios</span><small>um treino por vez · {CTR.intervalo} min de intervalo</small></h2>
      {!bebe && !pode && (
        <div class="dl-card treino-intervalo desk-nao"><Peca nome="icone_tempo" reserva="⏳" />
          <span><b>Próximo treino em {CTR.intervalo - (m.e.tick - t.ultimo!)} min de jogo</b><span class="dl-apoio">a fadiga baixa {CTR.recuperaHora} por hora acordado e zera quando ele dorme</span></span></div>
      )}
      {bebe && <p class="dl-apoio" style={{ margin: 0 }}>O In-Training ainda não treina.</p>}
      <div class="treino-grade" role="group" aria-label="Exercícios">
        {EXERCICIOS.map(ex => {
          const [pri, sec] = CTR.exercicios[ex], des = bebe || !pode || lutando || nascendo > 0;
          return (
            <button type="button" key={ex} class={`treino-ex${t.forcaria ? " forcar" : ""}`} disabled={des}
              aria-label={`${t.forcaria ? "Forçar" : "Treinar"} ${NOME_EXERCICIO[ex]}${t.forcaria ? ": gera sobrecarga" : ""}`}
              onClick={() => (t.forcaria ? setConfirmar(ex) : treinar(ex))}>
              {apt[pri] > 1 && <span class="treino-selo">aptidão</span>}
              <IconeTreino ex={ex} />
              <b>{NOME_EXERCICIO[ex]}</b>
              <span class="treino-ganho">+{n1(CTR.ganhoPri * mult)} {NOME_STAT[pri]} · +{n1(CTR.ganhoSec * mult)} {NOME_STAT[sec]}</span>
              {t.forcaria && <span class="treino-perigo"><span>FORÇAR<small>+ sobrecarga</small></span></span>}
            </button>
          );
        })}
      </div>
      <p class="treino-legenda desk-nao"><span class="treino-selo">aptidão</span>{fortes.length ? `${NOME_ESP[m.especie]} rende ${fortes.map(k => `${n1(apt[k])}× em ${NOME_STAT[k]}`).join(" e ")}.` : ""} Um treino por vez, com {CTR.intervalo} min de intervalo.</p>
      <p class="dl-apoio" aria-live="polite" style={{ margin: 0 }}>{msg}</p>
      <details class="dl-apoio"><summary>Como o treino funciona</summary>
        <p>Um toque por sessão, com pelo menos 10 min entre elas. Cada exercício sobe um stat principal e um secundário (com a aptidão do brasão e retorno decrescente; tetos de +10 por stat e +36 na vida). A fadiga reduz o ganho e passa com o tempo acordado e com o sono; com fadiga 40 ele pede pausa. Com fadiga 60 o botão vira <b>Forçar</b>: rende mais, mas gera <b>sobrecarga</b>, que não some na evolução. Sobrecarga alta na virada para Ultimate leva à <b>forma sombria</b>. Cada ponto treinado vale 3 pontos de stat no combate. Na arena o treino muda o perfil (stats normalizados); na campanha vale o ganho inteiro.</p>
      </details>
      <span class="desk-so treino-ult-caixa"><UltimoTreino />
        <span class="treino-ult-bts">
          <button type="button" class="dl-btn dl-btn--sec treino-forcar" disabled={!t.forcaria || bebe || !pode || lutando || nascendo > 0}
            title={t.forcaria ? "rende mais e gera sobrecarga" : `abre com fadiga ${CTR.limiteForcar}`} onClick={() => setEscolher(true)}>
            <span class="treino-forcar-faixa" aria-hidden="true" />Forçar treino</button>
          {!t.forcaria && <small class="dl-apoio">abre com fadiga {CTR.limiteForcar}</small>}
        </span></span>
      {escolher && <EscolherForcar escolher={ex => { setEscolher(false); setConfirmar(ex); }} fechar={() => setEscolher(false)} />}
      </div>
      {confirmar && <ConfirmarForcar ex={confirmar} fechar={() => setConfirmar(null)} forcar={() => treinar(confirmar)} />}
    </div>
  );
}
