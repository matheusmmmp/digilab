/* Tela Pet (docs/TAREFA_V2_TELA_PET.md, a Home da referencia de 2026-10-19): o pet no cenario 2.5D com a maior area da tela; embaixo,
   so a necessidade prioritaria e tres acoes (as outras a um toque); o resto (necessidades, desejo, confianca, o porque da fala, as
   atividades recentes e o DigiBrain) num painel sob demanda: folha no celular, coluna recolhivel no desktop.
   Tudo derivado do motor na hora de desenhar; so mudarMotor() altera o pet. */
import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { ArrowRight, Ban, Brain, ChevronRight, Ellipsis, Gamepad2, Hand, House, Layers, MessageSquareText, PawPrint, Sparkles, Syringe } from "lucide-react";
import {
  ACAO_CHAMADO, ALVOS_DESEJO, CAT, CED, CLE, CMEN, DO_ESP, NOME_ESP, EMOCAO_TXT, FATORES_TXT, NOME_CHAMADO, NOME_EST, NOME_PET, OVO, TICK_INICIAL, TPD,
  chaveSprite, eNoite, expressarConfianca, nomeEstagio, nomeForma, nomeRivalConfianca, observacao, type AcaoDono, type Chamado, type MotivoVida, type Motor,
} from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { BRASAO } from "../../decoracao.ts";
import { Seg, blocos } from "../../componentes/Barras.tsx";
import { Grade, Peca } from "../../componentes/Imagens.tsx";
import {
  detalheMotivo, falaDe, falaLLM, motivoParaApi, refsDoMotivo, rotuloLLM, useFalaLLM,
} from "../../fala.ts";
import {
  detalheFalaLivre, falaVozRecente, gatilhoFalaLivre, iconeVerif, tituloFalaLivre, useFalaLivre,
} from "../../falaLivre.ts";
import { AMPULHETA } from "../../grades.ts";
import { ROTULO_DONO, agir } from "../../acoes.ts";
import { useJogo } from "../../jogo.ts";
import { abrirEscolhaBrasao } from "../../jornada.ts";
import { useTempo } from "../../tempo.ts";
import { PalcoPet } from "./PalcoPet.tsx";
import { CenaPet } from "./CenarioPet.tsx";
import { BarraRacao, FaixaRacao, InfoMundo } from "./PorRacao.tsx";
import { useDesktop } from "../../desktop.ts";
import { Folha } from "../../componentes/Folha.tsx";
import { BotaoDigiBrain, ConteudoDigiBrain, SeloDigiBrain } from "../../componentes/DigiBrain.tsx";
import { Modulo, Quadro, type Arranjo } from "../../componentes/Quadro.tsx";
import { duracao, previsaoEvo } from "../crescer/TelaEvolucao.tsx";

export const hhmm = (t: number): string => { const m = t % TPD; return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); };
export const diaDe = (t: number): number => Math.floor((t - TICK_INICIAL) / TPD) + 1;

/* ------------------------------------------------ cabecalho e retrato */
export function Retrato({ m, ovo }: { m: Motor; ovo: boolean }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return null;
  const { url, w, h } = imagemAtlas(a, ovo ? OVO[m.especie] : chaveSprite(m.forma));
  return <img className="dl-pix" src={url} width={w} height={h} alt="" />;
}
/** cabecalho do celular: o nome e o brasao (tocar abre Meus pets), o nivel e o dia, o relogio e, a direita, Conversar e Configuracoes
    (44 px). Sem retrato redondo: o pet aparece no cenario. No desktop o topo da casca faz esse papel e este cabecalho some. */
function CabecalhoPet({ abrirMeusPets, irConversar, abrirConfig }: { abrirMeusPets: () => void; irConversar: () => void; abrirConfig: () => void }) {
  const { motor: m, nascendo, erroSave } = useJogo(), ovo = nascendo > 0, e = m.e;
  return (
    <header className="pet-cab">
      <button type="button" className="pet-cab-nome" aria-haspopup="dialog" aria-label="Meus pets: trocar parceiro" onClick={abrirMeusPets}>
        <span className="pet-cab-placa"><span className="dl-placa">{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</span>
          <Deco nome={BRASAO[m.especie].peca} largura={30} altura={20} alt={`brasão ${NOME_ESP[m.especie]}`} className="pet-cab-brasao" /></span>
        <span className="pet-cab-sub"><span className="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>dia {diaDe(e.tick)}</span>
      </button>
      <span className="pet-relogio">
        <span className="dl-num pet-hora" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}`}>{hhmm(e.tick)}</span>
        <span className={`pet-salvo${erroSave ? " erro" : ""}`}><i aria-hidden="true" />{erroSave ? "não salva" : "salvo"}</span>
      </span>
      <span className="pet-cab-bts">
        <button type="button" className="pet-cab-bt pet-cab-bt--conversar" aria-label="Conversar" onClick={irConversar}>{ICONE_CONVERSAR}</button>
        <button type="button" className="pet-cab-bt pet-cab-bt--config" aria-label="Configurações" onClick={abrirConfig}>
          <Deco nome="Common_Icon_Setting" largura={24} altura={24} reserva={<span aria-hidden="true">⚙</span>} /></button>
      </span>
    </header>
  );
}

/** balao de conversa das pranchas (PetTela, PetTelaDesktop) */
export const ICONE_CONVERSAR = <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M4 5h16v10H10l-4 4v-4H4z" fill="#FFFFFF" stroke="#FFFFFF" strokeWidth="1.5" strokeLinejoin="round" /><path d="M8 9h8M8 12h5" stroke="#173A8A" strokeWidth="2" strokeLinecap="round" /></svg>;

/* ------------------------------------------------ fala: balao por estagio (guia, secao 9), causa e detalhe */
const EMOTE_KAOMOJI: Record<string, string> = { "(^_^)": "emoji_feliz", "(*^_^*)": "emoji_coracao", "(o.o)?": "emoji_surpreso" };
const EMOTE_FATOR: Record<string, string> = { fome: "emoji_carne", necessidade_fome: "emoji_carne", elogio: "emoji_joinha", elogios: "emoji_joinha", carinho: "emoji_coracao" };
const FATOR_DEMORA = new Set(["demora", "latencia_fome", "latencia_higiene", "tempo_sem_cuidado"]);
const CAUSA_MEMORIA: Record<string, string> = { demora: "demora", latencia_fome: "demora", latencia_higiene: "demora", bronca: "bronca", repreensoes: "bronca", elogio: "elogio", elogios: "elogio", carinho: "carinho" };
const EMOTE_CAUSA: Record<string, string> = { elogio: "emoji_joinha", carinho: "emoji_coracao" };
const CORES_AMPULHETA = { k: "#173A8A", w: "#FFFFFF", y: "#F0B429" };

/** o texto vem da tabela de expressao do motor; a tela so troca marcas por emotes (In-Training: emote; Rookie:
    icones da causa; Champion em diante: frase) */
function TextoFala({ txt, est, atlasOk }: { txt: string; est: string; atlasOk: boolean }) {
  if (est === "bebe" && atlasOk && EMOTE_KAOMOJI[txt]) return <Peca nome={EMOTE_KAOMOJI[txt]} escala={2} alt={txt} />;
  if (est !== "crianca" || !atlasOk) return <>{txt}</>;
  const partes: ReactNode[] = [];
  let ult = 0, i = 0;
  for (const m of txt.matchAll(/\[:(.+?):\]/g)) {
    partes.push(txt.slice(ult, m.index));
    const marc = m[1], f = Object.keys(FATORES_TXT).find(k => FATORES_TXT[k].marcador === marc);
    partes.push(f && EMOTE_FATOR[f] ? <Peca key={i++} nome={EMOTE_FATOR[f]} escala={2} alt={marc} />
      : f && FATOR_DEMORA.has(f) ? <Grade key={i++} grade={AMPULHETA} escala={3} cores={CORES_AMPULHETA} alt={marc} />
      : <span key={i++} className="fala-marca">{marc}</span>);
    ult = (m.index ?? 0) + m[0].length;
  }
  partes.push(txt.slice(ult));
  return <>{partes}</>;
}
function Causa({ mot, refs }: { mot: MotivoVida; refs: number[] }) {
  if (mot.exploracao || !mot.fatores.length) return <span className="dl-causa dl-causa--sem">? sem motivo registrado</span>;
  const mem = mot.fatores.filter(f => CAUSA_MEMORIA[f]).slice(0, 2);
  return <>{mem.map(f => {
    const c = CAUSA_MEMORIA[f];
    return <span key={f} className="dl-causa dl-causa--registro dl-malha">{EMOTE_CAUSA[c] && <Peca nome={EMOTE_CAUSA[c]} />}{c}{refs.length ? " · evento #" + refs.join(", #") : ""}</span>;
  })}</>;
}
interface VistaFala { classe: string; balao: ReactNode; texto: string; titulo: string; causa: ReactNode; detalhe: string }
/** a fala de agora (texto da tabela de expressao, LLM na moldura ou fala livre); a fala livre reage ao pet (gatilho)
    fora do desenho, porque dispara chamadas ao servidor */
function useFala(): VistaFala {
  const { motor: m, revisao } = useJogo(), atlas = useAtlas(), llm = useFalaLLM(), fl = useFalaLivre();
  const [livre, setLivre] = useState(false);
  useEffect(() => { setLivre(gatilhoFalaLivre(m)); }, [revisao, fl.modo]);
  const mot = m.motivo, est = m.estagioAtual;
  const v: VistaFala = { classe: "dl-balao", balao: "…", texto: "", titulo: "Toque para ver o porquê", causa: null, detalhe: "" };
  const ult = m.temVozPropria ? falaVozRecente(m) : fl.modo === "livre" ? fl.ultimo : null;
  if (livre && ult) {
    v.balao = v.texto = "✧ " + ult.fala + iconeVerif(ult.verificacao, ult);
    v.detalhe = detalheFalaLivre(ult); v.titulo = tituloFalaLivre(ult);
  } else if (mot) {
    const refs = refsDoMotivo(m, mot), resp = falaLLM(motivoParaApi(mot, refs), est, mot.humor), usarLLM = !!resp && resp.fonte === "llm";
    const fria = m.falaFria || m.sombria, pronta = llm.on && llm.ativo && ["adolescente", "adulto", "mega"].includes(est) && !usarLLM;
    v.classe = "dl-balao" + (fria ? " dl-balao--sombria" : "") + (est === "bebe" ? " dl-balao--emote" : "");
    v.balao = <>{usarLLM ? "✦ " + resp!.texto : <TextoFala txt={falaDe(m, mot)} est={est} atlasOk={atlas.tipo === "ok"} />}{pronta && <span className="dl-balao-tag">frase pronta</span>}</>;
    v.texto = usarLLM ? "✦ " + resp!.texto : est === "adolescente" || est === "adulto" || est === "mega" ? falaDe(m, mot) : "";
    v.causa = <Causa mot={mot} refs={refs} />;
    v.detalhe = detalheMotivo(mot, est) + (llm.on && llm.ativo && ["adolescente", "adulto", "mega"].includes(est)
      ? ` · fonte: ${usarLLM ? "LLM (" + resp!.detalhe + ")" : resp ? "template (" + resp.detalhe + ")" : "template (aguardando LLM)"}` : " · fonte: template");
  }
  return v;
}
/** balao sobre o pet (PetTela, em (223, 54) com o rabinho): a causa da ultima decisao em icones; sem causa, "?" */
const ICONE_CAUSA: Record<string, "carne" | "tempo" | "joinha" | "coracao" | "exclam"> = {
  fome: "carne", necessidade_fome: "carne", latencia_fome: "tempo", latencia_higiene: "tempo", tempo_sem_cuidado: "tempo", demora: "tempo",
  elogio: "joinha", elogios: "joinha", carinho: "coracao", bronca: "exclam", repreensoes: "exclam",
};
function BalaoCausa() {
  const { motor: m } = useJogo(), mot = m.motivo;
  if (!mot || mot.origem !== "vida") return null;
  const ic = mot.exploracao ? [] : [...new Set(mot.fatores.map(f => ICONE_CAUSA[f]).filter(Boolean))].slice(0, 3);
  const txt = mot.exploracao || !mot.fatores.length ? "sem causa registrada" : mot.fatores.map(f => FATORES_TXT[f]?.marcador ?? f).join(" + ");
  return (
    <span className="balao-palco balao-causa" role="img" aria-label={`causa: ${txt}`} title={txt}>
      {ic.length ? ic.flatMap((x, i) => [i > 0 ? <b key={"m" + i}>+</b> : null, <span key={"p" + i} className="causa-ic">{x === "tempo" ? <Peca nome="icone_tempo" /> : <Peca nome={"emoji_" + x} escala={2} />}</span>])
        : <b className="balao-q">?</b>}
    </span>
  );
}
/** a fala de agora num balao sobre o cenario; tocar abre o porque no painel de detalhes */
const MODO_CURTO: Record<string, string> = { template: "frases prontas", moldura: "moldura", livre: "fala livre" };
function BalaoFala({ v, abrir }: { v: VistaFala; abrir: () => void }) {
  return (
    <button type="button" className={v.classe + " cena-fala"} title={v.titulo} aria-haspopup="dialog" onClick={abrir}>
      <span className="balao-txt">{v.balao}</span><small>toque para ver o porquê</small></button>
  );
}
/** no painel: o que ele faz, a causa registrada, o detalhe e a fonte da fala */
function DetalheFala({ v, semTitulo = false }: { v: VistaFala; semTitulo?: boolean }) {
  const { motor: m } = useJogo(), { freado } = useTempo(), r = rotuloLLM(), fl = useFalaLivre();
  return (
    <section className="det-sec det-fala" aria-labelledby="det-fala-tit">
      {!semTitulo && <h3 id="det-fala-tit">Por que ele disse isso</h3>}
      <div className="fala-det">
        <span className="pet-status dl-lcd">{NOME_PET[m.acao]}{freado ? " · tempo em 1x até atender" : ""}</span>{v.causa}
        <span className="dl-apoio">{v.texto && <>“{v.texto}” · </>}{v.detalhe}</span></div>
      <span className="fala-status" title={`${r.texto} · ${r.titulo}`}><span className="fala-ponto" data-estado={fl.modo === "template" ? "off" : r.estado} aria-hidden="true" />{MODO_CURTO[fl.modo]}</span>
    </section>
  );
}

/* confianca de combate (M1, so pets v8): a frase de estado (confiante, inseguro, entediado do rival) quando existe, com
   o "porque" apontando para as lutas do registro que a causaram (ConfiancaCombate.estado). Neutro: nada. */
const RESULTADO_LUTA: Record<number, string> = { 1: "venceu", 0: "empatou", [-1]: "perdeu" };
export function lutasDaCausa(m: Motor, lutas: readonly number[], estado: string): { idx: number; k: number; tick: number; rival: string; sinal: number }[] {
  if (!m.conf) return [];
  /* a i-esima luta da confianca e de um evento "l" do registro (event sourcing): Motor.confEvento da a ordem dele entre os "l"
     (uma serie, como a Liga ou a Cidadela, tem varias lutas num evento so) */
  const idxL: number[] = [];
  m.log.forEach((ev, i) => { if (ev[1] === "l") idxL.push(i); });
  const sinal = estado === "confiante" ? 1 : estado === "inseguro" ? -1 : null;
  return m.conf.historico.map((h, i) => ({ idx: idxL[m.confEvento[i]], k: i, tick: h.tick, rival: h.rival, sinal: h.sinal }))
    .filter(x => lutas.includes(x.tick) && (sinal === null || x.sinal === sinal)).reverse();
}
function EstadoConfianca() {
  const { motor: m, nascendo } = useJogo(), [aberto, setAberto] = useState(false);
  if (m.versao < 8 || nascendo > 0 || m.morte) return null;
  const e = m.estadoConfianca();
  if (!e || e.estado === "neutro") return null;
  const txt = expressarConfianca(e.estado, m.estagioAtual)!, causa = lutasDaCausa(m, e.lutas, e.estado);
  const desde = e.desde !== null ? `desde D${diaDe(e.desde)} ${hhmm(e.desde)}` : "";
  return (
    <div className="pet-conf">
      <button type="button" className="pet-conf-frase" aria-expanded={aberto} aria-controls="conf-det" title="Toque para ver as lutas que causaram" onClick={() => setAberto(!aberto)}>
        <span className="dl-tag pet-conf-tag">{e.estado === "entediado" ? "entediado do rival" : e.estado}</span>
        <b><TextoFala txt={txt} est={m.estagioAtual} atlasOk={false} /></b><small>{desde}</small></button>
      {aberto && <ul className="pet-conf-det dl-apoio" id="conf-det">
        {causa.map(x => <li key={x.k}><span className="dl-lcd">D{diaDe(x.tick)} {hhmm(x.tick)}</span> {RESULTADO_LUTA[x.sinal]} de {nomeRivalConfianca(x.rival)} · evento #{x.idx} do registro</li>)}
        {!causa.length && <li>sem luta registrada</li>}
      </ul>}
    </div>
  );
}

/* emocao (prancha UpPet): a ultima emocao registrada na memoria do pet (so pets v2+; v1 nao tem emocao) */
const EMOTE_EMOCAO: Record<string, string> = { alegria: "emoji_feliz", euforia: "emoji_feliz", orgulho: "emoji_feliz", ternura: "emoji_coracao" };
function Emocao() {
  const { motor: m } = useJogo();
  if (m.versao < 2) return null;
  const em = (m.pol.mem as unknown as { emocoes: { nome: string }[] }).emocoes;
  const ult = em[em.length - 1];
  if (!ult) return null;
  return <span className="palco-emocao">{EMOTE_EMOCAO[ult.nome] && <Peca nome={EMOTE_EMOCAO[ult.nome]} />}{EMOCAO_TXT[ult.nome][0]}</span>;
}

/* ------------------------------------------------ necessidades, chamado e desejo */
const NEC_PET: [("fome" | "energia" | "higiene" | "humor"), string][] = [["fome", "comida"], ["energia", "energia"], ["higiene", "higiene"], ["humor", "humor"]];
const EMOTE_CHAMADO: Record<Chamado, string | null> = { fome: "emoji_carne", carinho: "emoji_coracao", higiene: null };
const EMOTE_DESEJO: Record<string, string> = { comer: "emoji_carne", brincar: "emoji_nota", chamar_atencao: "emoji_exclam", explorar: "emoji_estrela" };

function Necessidades() {
  const { motor: m } = useJogo(), e = m.e, saude = Math.round(e.saude * 100);
  return (
    <div className="necessidades4">
      <h2 className="desk-so nec-tit">Estado atual</h2>
      {NEC_PET.map(([k, rot]) => (
        <div className="nec" key={k}>
          <span className="nec-rot">{rot}</span>
          <Seg n={blocos(e[k], 5)} m={5} cls={e[k] < .5 ? "dl-seg--necessidade" : "dl-seg--acao"} />
        </div>
      ))}
      <div className="dl-vida nec-saude">
        <div className="dl-vida-topo"><span>Saúde</span><span className="dl-lcd">{saude}%{e.saude < .3 ? " · crítica" : ""}</span></div>
        <div className="dl-vida-trilho" role="img" aria-label={`saúde ${saude} de 100`}>
          <i style={{ width: `${e.saude * 100}%`, ...(e.saude < .3 ? { background: "var(--dl-need)" } : {}) }} />
        </div>
      </div>
      {m.temEducacao && <div className="nec nec-disciplina">
        <span className="nec-rot">Disciplina</span>
        <Seg n={blocos(m.disciplina / CED.disciplinaMax, 4)} m={4} cls="dl-seg--acao" />
      </div>}
    </div>
  );
}
/** pets v4: a janela aberta (chamado ou aviso) e a lesao. O dono ve o pedido, nunca se e manha: confere a
    necessidade e decide (atender ou dar bronca). */
function JanelaV4({ agir }: { agir: (a: AcaoDono) => void }) {
  const { motor: m } = useJogo(), j = m.janelaAberta(), tick = m.e.tick;
  const lesao = m.lesionadoDesde !== null ? CLE.horasMorte * 60 - (tick - m.lesionadoDesde) : null;
  return <>
    {lesao !== null && (
      <div className="dl-card chamado chamado--lesao">
        <span className="chamado-ic"><Peca nome="emoji_exclam" escala={2} reserva="!" /></span>
        <span className="chamado-txt"><span className="chamado-tit"><b>Machucado na luta</b><span className="dl-apoio">trate em até {Math.floor(lesao / 60)} h {lesao % 60} min</span></span>
          <Seg n={blocos(lesao / (CLE.horasMorte * 60), 10)} m={10} /></span>
        <button type="button" className="dl-btn" onClick={() => agir("tratar_lesao")}>Tratar</button>
      </div>
    )}
    {j && (() => {
      const resta = Math.max(0, j.prazo - tick);
      const barra = <Seg n={blocos(resta / CED.janela, 10)} m={10} />;
      if (j.tipo === "fala") {
        /* pets v7: ele falou (voz propria). O dono nunca sabe se foi mentira: acredita, premia ou desconfia */
        const f = falaVozRecente(m), barraFala = <Seg n={blocos(resta / CMEN.janela, 10)} m={10} />;
        return (
          <div className="dl-card chamado chamado--fala">
            <span className="chamado-ic"><Peca nome="emoji_exclam" escala={2} reserva="!" /></span>
            <span className="chamado-txt"><span className="chamado-tit"><b>{f ? `“${f.fala}”` : "Ele disse uma coisa"}</b>
              <span className="dl-apoio">{m.sombria ? "é sombrio: não confie em tudo que ele diz" : "acredita? confira o que você sabe dele"}</span></span>{barraFala}</span>
            <span className="chamado-botoes">
              <button type="button" className="dl-btn" onClick={() => agir("elogiar")}>Acreditar</button>
              <button type="button" className="dl-btn" onClick={() => agir("petisco")}>Petisco</button>
              <button type="button" className="dl-btn" onClick={() => agir("repreender")}>É mentira!</button>
            </span>
          </div>
        );
      }
      if (j.tipo === "aviso") return (
        <div className="dl-card chamado">
          <span className="chamado-ic"><Peca nome="emoji_surpreso" escala={2} reserva="!" /></span>
          <span className="chamado-txt"><span className="chamado-tit"><b>Vai fazer sujeira!</b><span className="dl-apoio">leve ao banheiro</span></span>{barra}</span>
          <button type="button" className="dl-btn" onClick={() => agir("levar_ao_banheiro")}>Banheiro</button>
        </div>
      );
      const c = j.pedido as Chamado;
      return (
        <div className="dl-card chamado">
          <span className="chamado-ic">{EMOTE_CHAMADO[c] ? <Peca nome={EMOTE_CHAMADO[c]!} escala={2} reserva="!" /> : "!"}</span>
          <span className="chamado-txt"><span className="chamado-tit"><b>Chamando: {NOME_CHAMADO[c]}</b><span className="dl-apoio">precisa mesmo? confira a barra</span></span>{barra}</span>
          <span className="chamado-botoes">
            <button type="button" className="dl-btn" onClick={() => agir(ACAO_CHAMADO[c][0])}>Atender</button>
            <button type="button" className="dl-btn" onClick={() => agir("repreender")}>É manha</button>
          </span>
        </div>
      );
    })()}
  </>;
}
/** pets v4: morreu (lesão demais ou sem tratar). O registro fica; so um ovo novo continua o jogo */
function Morte() {
  const { motor: m } = useJogo();
  if (!m.morte) return null;
  return (
    <div className="dl-card chamado chamado--morte" role="alert">
      <span className="chamado-txt"><b>{nomeForma(m.forma)} se foi</b>
        <span className="dl-apoio">{m.morte.causa === "lesoes" ? "se machucou demais nas lutas" : "a lesão ficou sem tratamento por tempo demais"}. O Diário guarda a vida inteira.</span></span>
      <button type="button" className="dl-btn dl-btn--destaque" onClick={abrirEscolhaBrasao}>Chocar um ovo novo</button>
    </div>
  );
}
function Chamados({ agir }: { agir: (a: AcaoDono) => void }) {
  const { motor: m } = useJogo(), ab = m.chamadosAbertos(), tick = m.e.tick;
  if (m.temEducacao && m.estagioAtual !== "bebe") return <JanelaV4 agir={agir} />;
  if (!ab.length && m.acao === "chamar_atencao") return (
    <div className="dl-card chamado">
      <span className="chamado-ic"><Peca nome="emoji_exclam" escala={2} reserva="!" /></span>
      <span className="chamado-txt"><b>Chamando você</b><span className="dl-apoio">um carinho atende o pedido</span></span>
      <button type="button" className="dl-btn" onClick={() => agir("acariciar")}>Atender</button>
    </div>
  );
  /* chamado aberto (so o In-Training chama): barra da janela, nunca cronometro */
  return <>{ab.map(c => {
    const resta = Math.max(0, CAT.janelaChamado - (tick - m.chamados.abertos[c]!));
    return (
      <div className="dl-card chamado" key={c}>
        <span className="chamado-ic">{c === "fome" ? <Deco nome="Growth_Guide_Icon_06" largura={36} altura={34} reserva={<Peca nome="emoji_carne" escala={2} />} />
          : EMOTE_CHAMADO[c] ? <Peca nome={EMOTE_CHAMADO[c]!} escala={2} reserva="!" /> : "!"}</span>
        <span className="chamado-txt"><span className="chamado-tit"><b>Chamado: {NOME_CHAMADO[c]}</b><span className="dl-apoio">janela aberta</span></span><Seg n={blocos(resta / CAT.janelaChamado, 10)} m={10} /></span>
        <button type="button" className="dl-btn" onClick={() => agir(ACAO_CHAMADO[c][0])}>Atender</button>
      </div>
    );
  })}</>;
}
/** desejo: necessidade (rosa, vem do corpo) ou vontade aprendida (malha); so o que o motor calculou */
function Desejo() {
  const { motor: m } = useJogo(), d = m.desejoAtual(m.observacaoAgora(), m.e.tick);
  if (!d) return null;
  const em = EMOTE_DESEJO[d.alvo];
  if (d.tipo === "necessidade") return (
    <div className="dl-desejo dl-desejo--necessidade"><span className="dl-desejo-cab">NECESSIDADE</span>
      <span className="dl-desejo-corpo">{em && <Peca nome={em} escala={2} />}<span><strong>{ALVOS_DESEJO[d.alvo][1]}</strong><span>vem do corpo</span></span></span></div>
  );
  return (
    <div className="dl-desejo dl-desejo--aprendida dl-malha"><span className="dl-desejo-cab">VONTADE APRENDIDA</span>
      <span className="dl-desejo-corpo"><span className="dl-desejo-icone">{em ? <Peca nome={em} escala={2} reserva="★" /> : "★"}</span>
        <span><strong>{ALVOS_DESEJO[d.alvo][1]}</strong><span>aprendida com você</span></span></span></div>
  );
}

/* ------------------------------------------------ a necessidade prioritaria */
type Necessidade = "fome" | "energia" | "higiene" | "humor";
const ROTULO_BAIXO: Record<Necessidade, string> = { fome: "comida baixa", energia: "energia baixa", higiene: "higiene baixa", humor: "humor baixo" };
const EMOTE_NEC: Record<Necessidade, string | null> = { fome: "emoji_carne", energia: null, higiene: null, humor: "emoji_nota" };
const ACAO_NEC: Record<Necessidade, AcaoDono | null> = { fome: "alimentar", energia: null, higiene: "limpar", humor: "brincar" };
const ACAO_DESEJO: Record<string, AcaoDono> = { comer: "alimentar", brincar: "brincar", limpar: "limpar", chamar_atencao: "acariciar" };
/** abaixo de metade a barra fica na cor de necessidade (Necessidades); a mais baixa delas e a prioritaria */
const LIMIAR_NEC = .5;

interface Resumo { texto: string; emote: string | null; acao: AcaoDono | null }
/** o resumo de agora, so do motor: o ovo; a necessidade mais baixa (se alguma esta abaixo da metade); o desejo; ou o que ele faz */
function resumoAgora(m: Motor, nascendo: number): Resumo {
  if (nascendo > 0) return { texto: "o ovo está chocando", emote: null, acao: null };
  const baixa = NEC_PET.map(([k]) => k).filter(k => m.e[k] < LIMIAR_NEC).sort((a, b) => m.e[a] - m.e[b])[0];
  if (baixa) return { texto: ROTULO_BAIXO[baixa], emote: EMOTE_NEC[baixa], acao: ACAO_NEC[baixa] };
  const d = m.desejoAtual(m.observacaoAgora(), m.e.tick);
  if (d) return { texto: (d.tipo === "necessidade" ? "precisa " : "quer ") + ALVOS_DESEJO[d.alvo][1], emote: EMOTE_DESEJO[d.alvo] ?? null, acao: ACAO_DESEJO[d.alvo] ?? null };
  return { texto: "agora: " + NOME_PET[m.acao], emote: null, acao: null };
}
/** ha um pedido aberto que pede resposta agora (chamado, janela da educacao ou lesao)? */
function temPedido(m: Motor): boolean {
  if (m.temEducacao && m.estagioAtual !== "bebe") return m.lesionadoDesde !== null || !!m.janelaAberta();
  return m.chamadosAbertos().length > 0 || m.acao === "chamar_atencao";
}
/** a necessidade prioritaria: a morte, um pedido aberto (o card de sempre, com o Atender) ou o resumo, que abre os detalhes */
function Prioridade({ abrirDetalhes }: { abrirDetalhes: () => void }) {
  const { motor: m, nascendo } = useJogo();
  if (m.morte) return <Morte />;
  if (nascendo === 0 && temPedido(m)) return <div className="pet-pedido"><Chamados agir={agir} /></div>;
  const r = resumoAgora(m, nascendo);
  return (
    <button type="button" className="pet-prioridade" aria-haspopup="dialog" onClick={abrirDetalhes}>
      <span className="pet-prioridade-ic" aria-hidden="true">{r.emote ? <Peca nome={r.emote} escala={2} reserva="•" /> : nascendo > 0 ? "•" : <Peca nome="emoji_feliz" escala={2} reserva="•" />}</span>
      <span className="pet-prioridade-txt"><b>{nascendo > 0 ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b><span>{r.texto}</span></span>
      <span className="pet-prioridade-ver">Detalhes<ChevronRight size={18} aria-hidden="true" /></span>
    </button>
  );
}

/* ------------------------------------------------ acoes do dono (o clique passa por src/acoes.ts, como o comando do chat) */
const ACOES: [AcaoDono, string][] = [["alimentar", "sec"], ["limpar", "sec"], ["brincar", "sec"], ["acariciar", "sec"], ["elogiar", "destaque"], ["repreender", "sec"]];
/* pets v4 (educacao-v1): petisco, banheiro e tratar lesao */
const ACOES_V4: [AcaoDono, string][] = [["petisco", "sec"], ["levar_ao_banheiro", "sec"], ["tratar_lesao", "sec"]];
/* pets v11: sem elogio, bronca, petisco e banheiro; o carinho e o tapa sao gestos no corpo (ACOES_DONO_JOGO_V11) */
const ACOES_V11: [AcaoDono, string][] = [["alimentar", "sec"], ["limpar", "sec"], ["brincar", "sec"], ["acariciar", "destaque"], ["tapa", "sec"],
  ["tratar_lesao", "sec"]];
/** as tres em destaque: a que atende a necessidade prioritaria (se houver) e, depois, alimentar, brincar e carinho */
const DESTAQUE_PADRAO: AcaoDono[] = ["alimentar", "brincar", "acariciar"];

/* icone de cada acao do dono: prato do guia, gota, nota, coracao, joinha e exclamacao */
const GOTA = <svg className="ic-gota" viewBox="0 0 8 8" width="24" height="24" aria-hidden="true"><path fill="#2C73E0" d="M3 0h2v2h1v1h1v3h-1v1h-4v-1h-1v-3h1v-1h1z" /><path fill="#BFE3FF" d="M2 3h1v2h-1z" /></svg>;
const CRUZ = <svg className="ic-cruz" viewBox="0 0 8 8" width="24" height="24" aria-hidden="true"><path fill="#E0443A" d="M3 1h2v2h2v2h-2v2h-2v-2h-2v-2h2z" /></svg>;
function IconeAcao({ a }: { a: AcaoDono }) {
  if (a === "alimentar") return <Deco nome="Growth_Guide_Icon_06" largura={24} altura={24} className="ic-acao" reserva={<Peca nome="emoji_carne" escala={2} />} />;
  if (a === "limpar") return GOTA;
  if (a === "levar_ao_banheiro") return GOTA;
  if (a === "tratar_lesao") return CRUZ;
  const em = ({ brincar: "emoji_nota", acariciar: "emoji_coracao", elogiar: "emoji_joinha", repreender: "emoji_exclam", petisco: "emoji_estrela" } as Partial<Record<AcaoDono, string>>)[a];
  return em ? <Peca nome={em} escala={2} /> : null;
}
function AcoesPet() {
  const { motor: m, nascendo } = useJogo(), [mais, setMais] = useState(false);
  /* ao abrir, as acoes extras entram na tela (no celular ficam abaixo da dobra) */
  useEffect(() => { if (mais) document.getElementById("acoes-mais")?.scrollIntoView({ block: "nearest" }); }, [mais]);
  const todas = (m.versao >= 11 ? ACOES_V11 : m.versao >= 4 ? [...ACOES, ...ACOES_V4] : ACOES).map(([a]) => a);
  const sugerida = resumoAgora(m, nascendo).acao;
  const destaque = [...new Set([...(sugerida ? [sugerida] : []), ...DESTAQUE_PADRAO])].filter(a => todas.includes(a)).slice(0, 3);
  const resto = todas.filter(a => !destaque.includes(a));
  /* v12: o Alimentar e a reserva temporaria do MVP (poe a racao no comedouro); a interacao planejada e por a racao no lugar (BarraRacao) */
  const reserva = (a: AcaoDono) => !!m.mundo && a === "alimentar";
  const botao = (a: AcaoDono, cls: string) => <button type="button" key={a} className={`dl-btn ${cls}`} onClick={() => agir(a)}
    aria-label={reserva(a) ? `${ROTULO_DONO[a]} (reserva: põe a ração no comedouro)` : undefined} title={reserva(a) ? "Reserva temporária: põe a ração no comedouro" : undefined}>
    <IconeAcao a={a} /><span>{ROTULO_DONO[a]}</span>{reserva(a) && <small className="acao-reserva">reserva</small>}</button>;
  return (
    <div className="acoes-pet" role="group" aria-label="Cuidar e ensinar">
      {destaque.map((a, i) => botao(a, i === 0 && sugerida === a ? "acao-destaque acao-destaque--sugerida" : "dl-btn--sec acao-destaque"))}
      <button type="button" className="dl-btn dl-btn--sec acao-mais" aria-expanded={mais} aria-controls="acoes-mais" onClick={() => setMais(!mais)}><Ellipsis size={24} aria-hidden="true" /><span>Mais</span></button>
      {mais && <div className="acoes-mais" id="acoes-mais">{resto.map(a => botao(a, "dl-btn--sec acao-extra"))}</div>}
    </div>
  );
}

/* ------------------------------------------------ o painel de detalhes do celular (sob demanda, numa folha) */
type Secao = "estado" | "fala" | "digibrain";
function PainelDetalhes({ v, foco }: { v: VistaFala; foco: Secao }) {
  const secoes: [Secao, ReactNode][] = [
    ["fala", <DetalheFala key="fala" v={v} />],
    ["estado", <div key="estado" className="det-estado"><Necessidades /><div className="dl-par"><Desejo /></div><EstadoConfianca /></div>],
  ];
  secoes.sort(([a], [b]) => (b === foco ? 1 : 0) - (a === foco ? 1 : 0));
  return <div className="pet-detalhes-conteudo">{secoes.map(([, n]) => n)}</div>;
}

/* ------------------------------------------------ o desktop: o quadro modular (docs/TAREFA_V2_PET_QUADRO.md) */
/* a coluna principal com o habitat e as acoes; a lateral com os modulos que o motor sustenta. O arranjo e preferencia de quem joga
   (localStorage), fora do save */
const CHAVE_QUADRO = "digilab-web-v21-sprites-quadro-pet";
const PADRAO_QUADRO: Arranjo = {
  principal: ["cenario", "acoes"], lado: ["estado", "desejo", "evolucao", "registro", "digibrain", "fala"], recolhidos: ["fala"], ladoRecolhido: false,
};
const CRESCE = ["cenario", "registro"] as const;
const ICONE_QUEM = { dono: Hand, pet: PawPrint, recusa: Ban } as const;

/** a proxima evolucao, so com o que o motor tem (previsaoEvo, o mesmo da tela Evolucao): a forma atual, o nivel que vem e, se o motor ja
    decidiu (o Mega), a forma seguinte; sem proxima evolucao, nada */
function ProximaEvolucao({ irEvolucao }: { irEvolucao: () => void }) {
  const { motor: m } = useJogo(), a = useAtlas(), p = previsaoEvo(m);
  if (!p) return null;
  const img = (nome: string) => { if (a.tipo !== "ok") return null; const i = imagemAtlas(a, nome); return <img className="dl-pix evo-mod-spr" src={i.url} width={i.w * 2} height={i.h * 2} alt="" />; };
  const decidida = p.prox.est === "mega";
  return (
    <div className="evo-mod">
      <div className="evo-mod-formas">
        <span className="evo-mod-forma">{img(chaveSprite(m.forma))}<small>{nomeForma(m.forma)}</small></span>
        <ArrowRight className="evo-mod-seta" size={28} aria-hidden="true" />
        <span className="evo-mod-forma">{decidida ? img(chaveSprite(p.prox)) : <b className="evo-mod-q" aria-hidden="true">?</b>}<small>{decidida ? nomeForma(p.prox) : nomeEstagio(p.prox)}</small></span>
      </div>
      <p className="evo-mod-txt">{p.falta > 0 ? <>até virar {nomeEstagio(p.prox)}: <b>{duracao(p.falta)}</b></> : <>o tempo do estágio já passou; o que falta está na árvore</>}</p>
      <button type="button" className="mod-link" onClick={irEvolucao}>Ver a árvore de evolução</button>
    </div>
  );
}
/** as ultimas linhas do registro (o que voce fez, o que ele fez e as recusas) */
function UltimasAcoes() {
  const { motor: m } = useJogo();
  const itens = m.historico.filter(h => h.quem === "dono" || h.quem === "pet" || h.quem === "recusa").slice(-8).reverse();
  const texto = (h: (typeof itens)[number]) => h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] ?? h.a : h.a;
  if (!itens.length) return <p className="mod-vazio">nada no registro ainda</p>;
  return (
    <ol className="mod-registro">{itens.map((h, i) => {
      const I = ICONE_QUEM[h.quem as keyof typeof ICONE_QUEM];
      return <li key={i} data-quem={h.quem}><time>{hhmm(h.t)}</time><span className="mod-registro-ic"><I size={18} aria-hidden="true" /></span>
        <span>{h.quem === "dono" ? "você: " : h.quem === "recusa" ? "recusou: " : ""}{texto(h)}</span></li>;
    })}</ol>
  );
}
function TelaPetDesktop({ irRegistro, irEvolucao }: { irRegistro: () => void; irEvolucao: () => void }) {
  const { motor: m, nascendo } = useJogo(), fala = useFala(), abrir = useRef<((id: string) => void) | null>(null);
  const d = m.desejoAtual(m.observacaoAgora(), m.e.tick);
  const render = (id: string): ReactNode | null => {
    switch (id) {
      case "cenario": return (
        <Modulo icone={House} titulo="Habitat">
          <section className={"pet-cena" + (m.morte ? " pet-cena--morto" : "")} aria-label="O pet no quarto">
            <CenaPet noite={eNoite(m.e.tick % TPD)} mundo={!!m.mundo} />
            {nascendo > 0 && <Deco nome="Digivice_Circle_01" className="ovo-anel gira" />}
            <PalcoPet />
            {nascendo === 0 && !m.morte && <BalaoFala v={fala} abrir={() => abrir.current?.("fala")} />}
            <BalaoCausa />
            {m.mundo && <InfoMundo />}
            {m.mundo && nascendo === 0 && !m.morte && <FaixaRacao />}
          </section>
        </Modulo>);
      case "acoes": return (
        <Modulo icone={Gamepad2} titulo="Ações">
          <div className="pet-doca"><Prioridade abrirDetalhes={() => abrir.current?.("estado")} />{m.mundo && nascendo === 0 && !m.morte && <BarraRacao />}{!m.morte && <AcoesPet />}</div>
        </Modulo>);
      case "estado": return (
        <Modulo icone={Syringe} titulo="Estado atual" aside={<Emocao />}>
          <div className="det-estado"><Necessidades /><EstadoConfianca /></div>
        </Modulo>);
      case "desejo": return (
        <Modulo icone={Sparkles} titulo="Desejo">
          {d && !m.morte ? <div className="dl-par"><Desejo /></div> : <p className="mod-vazio">nenhum desejo agora</p>}
        </Modulo>);
      case "evolucao": return previsaoEvo(m) && !m.morte && nascendo === 0 ? (
        <Modulo icone={Layers} titulo="Próxima evolução"><ProximaEvolucao irEvolucao={irEvolucao} /></Modulo>) : null;
      case "registro": return (
        <Modulo icone={Layers} titulo="Últimas ações" aside={<button type="button" className="mod-link" onClick={irRegistro}>Ver tudo</button>}>
          <UltimasAcoes />
        </Modulo>);
      case "digibrain": return m.versao >= 11 && nascendo === 0 ? (
        <Modulo icone={Brain} titulo="DigiBrain" aside={<SeloDigiBrain replay={false} />}>
          <div className="digibrain digibrain--modulo"><ConteudoDigiBrain /></div>
        </Modulo>) : null;
      case "fala": return nascendo === 0 && !m.morte ? (
        <Modulo icone={MessageSquareText} titulo="Por que ele disse isso"><DetalheFala v={fala} semTitulo /></Modulo>) : null;
      default: throw new Error("módulo desconhecido no quadro do Pet: " + id);
    }
  };
  return (
    <section className="pet-tela pet-home pet-home--quadro dl" aria-label="Tela do pet">
      <Quadro chave={CHAVE_QUADRO} padrao={PADRAO_QUADRO} render={render} cresce={CRESCE} abrirRef={abrir} />
    </section>
  );
}

/* ------------------------------------------------ a tela */
export function TelaPet({ abrirMeusPets, irConversar, abrirConfig, irRegistro, irEvolucao }: { abrirMeusPets: () => void; irConversar: () => void; abrirConfig: () => void; irRegistro: () => void; irEvolucao: () => void }) {
  const { motor: m, nascendo } = useJogo(), desk = useDesktop();
  const fala = useFala(), [detalhes, setDetalhes] = useState<Secao | null>(null);
  if (desk) return <TelaPetDesktop irRegistro={irRegistro} irEvolucao={irEvolucao} />;
  return (
    <section className="pet-tela pet-home dl" aria-label="Tela do pet">
      <CabecalhoPet abrirMeusPets={abrirMeusPets} irConversar={irConversar} abrirConfig={abrirConfig} />
      <div className="pet-home-corpo">
        <div className="pet-home-principal">
          <section className={"pet-cena" + (m.morte ? " pet-cena--morto" : "")} aria-label="O pet no quarto">
            <CenaPet noite={eNoite(m.e.tick % TPD)} mundo={!!m.mundo} />
            {nascendo > 0 && <Deco nome="Digivice_Circle_01" className="ovo-anel gira" />}
            <PalcoPet />
            <div className="cena-topo">
              <Emocao />
              <span className="cena-topo-dir">{nascendo === 0 && m.versao >= 11 && <BotaoDigiBrain />}</span>
            </div>
            {nascendo === 0 && !m.morte && <BalaoFala v={fala} abrir={() => setDetalhes("fala")} />}
            <BalaoCausa />
            {m.mundo && <InfoMundo />}
            {m.mundo && nascendo === 0 && !m.morte && <FaixaRacao />}
          </section>
          <div className="pet-doca">
            <Prioridade abrirDetalhes={() => setDetalhes("estado")} />
            {m.mundo && nascendo === 0 && !m.morte && <BarraRacao />}
            {!m.morte && <AcoesPet />}
          </div>
        </div>
        {detalhes && <Folha titulo="Como ele está" fechar={() => setDetalhes(null)}><PainelDetalhes v={fala} foco={detalhes} /></Folha>}
      </div>
    </section>
  );
}
