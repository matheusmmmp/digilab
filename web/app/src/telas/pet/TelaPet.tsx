/* Tela Pet sobre o habitat (docs/TAREFA_V2_LAYOUT_HABITAT.md, M3; HUD da docs/TAREFA_V3_LAYOUT_HUD.md): a cena e a camada de fundo da
   casca (Habitat.tsx); aqui ficam so os controles flutuantes: a barra de acoes no rodape, o chamado do pet no alto ao centro, o balao de
   fala e os paineis Estado, Evolucao e Ultimas acoes. A partir de 900 px eles ficam empilhados a direita (recolhiveis, a escolha guardada
   no navegador) e o DigiBrain e uma etiqueta sobre a cena; abaixo (celular, M1 do mobile minimo), o leque do retrato abre um painel por vez. Tudo derivado do
   motor na hora de desenhar; so mudarMotor() altera o pet. */
import type { ReactNode } from "react";
import { useEffect, useId, useRef, useState, useSyncExternalStore } from "react";
import { createPortal } from "react-dom";
import {
  Activity, ArrowRight, Ban, Brain, ChevronDown, ChevronRight, Cross, Droplet, Drumstick, Ellipsis, Hand, Heart, HeartPulse, History, Music, PawPrint, Settings, Smile,
  TrendingUp, Users, X, Zap, type LucideIcon,
} from "lucide-react";
import {
  ACAO_CHAMADO, ALVOS_DESEJO, CAT, DO_ESP, NOME_ESP, EMOCAO_TXT, FATORES_TXT, NOME_CHAMADO, NOME_EST, NOME_PET, OVO, TICK_INICIAL, TPD,
  chaveSprite, eNoite, expressarConfianca, nomeEstagio, nomeForma, nomeRivalConfianca, observacao, type AcaoDono, type Chamado, type MotivoVida, type Motor,
} from "../../../motor/index.ts";
import { imagemAtlas, recorteAtlas, useAtlas } from "../../atlas.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { BRASAO } from "../../decoracao.ts";
import { Seg, blocos } from "../../componentes/Barras.tsx";
import { MedidorHx, PainelHx } from "../../componentes/hx/index.ts";
import { Grade, Peca } from "../../componentes/Imagens.tsx";
import {
  detalheMotivo, falaDe, falaLLM, motivoParaApi, refsDoMotivo, rotuloLLM, useFalaLLM,
} from "../../fala.ts";
import {
  detalheFalaLivre, gatilhoFalaLivre, iconeVerif, tituloFalaLivre, useFalaLivre,
} from "../../falaLivre.ts";
import { AMPULHETA } from "../../grades.ts";
import { ROTULO_DONO, agir } from "../../acoes.ts";
import { useJogo } from "../../jogo.ts";
import { abrirEscolhaBrasao } from "../../jornada.ts";
import { useTempo } from "../../tempo.ts";
import { CHAVE } from "../../save.ts";
import { FOME_FALA, chamadosVisiveis, useArrastavel, useAviso, useDetalhesPet } from "../../hudPet.ts";
import { BotaoMovel, Segura } from "../../componentes/BotaoMovel.tsx";
import { alternarLeque, fecharLeque, mudarLeque, useLeque } from "../../movel.ts";
import { AgoraIcone, ChipCausa, LinhaAgora } from "./LinhaAgora.tsx";
import { BarraBola } from "./PorBola.tsx";
import { AvisoRacao, BarraRacao, FaixaRacao, InfoMundo } from "./PorRacao.tsx";
import "../../estilo/pet_dock.css";
import "../../estilo/pet_hud.css";
import "../../estilo/pet_movel.css";
import { ConteudoDigiBrain, SeloDigiBrain } from "../../componentes/DigiBrain.tsx";
import { ConteudoDigiBrainLab } from "../../componentes/DigiBrainLab.tsx";
import { SeloExperimental } from "../config/Laboratorio.tsx";
import { duracao, previsaoEvo } from "../crescer/TelaEvolucao.tsx";

export const hhmm = (t: number): string => { const m = t % TPD; return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); };
export const diaDe = (t: number): number => Math.floor((t - TICK_INICIAL) / TPD) + 1;

/* ------------------------------------------------ cabecalho e retrato */
export function Retrato({ m, ovo, semArrastar = false }: { m: Motor; ovo: boolean; semArrastar?: boolean }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return null;
  const { url, w, h } = recorteAtlas(a, ovo ? OVO[m.especie] : chaveSprite(m.forma));
  /* `semArrastar` (o retrato do celular, dentro de um botao): o toque longo nao arrasta a imagem; o desktop nao passa, e o DOM dele fica igual */
  return semArrastar ? <img className="dl-pix" src={url} width={w} height={h} alt="" draggable={false} /> : <img className="dl-pix" src={url} width={w} height={h} alt="" />;
}
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
/** o chip de causa do balao e do "Por que ele disse isso" (so com MotivoVida): fator de memoria, malha ciano com o evento; o treino
    com pausa, "vem do corpo"; outro fator, o marcador neutro; sem fator ou exploracao, "? sem motivo registrado" (LinhaAgora.tsx) */
function Causa({ mot, refs }: { mot: MotivoVida; refs: number[] }) {
  const mem = mot.exploracao ? [] : mot.fatores.filter(f => CAUSA_MEMORIA[f]).slice(0, 2);
  if (!mem.length) return <ChipCausa mot={mot} />;
  return <>{mot.fatores.includes("fadiga_treino") && <ChipCausa mot={{ ...mot, fatores: ["fadiga_treino"] }} />}{mem.map(f => {
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
  const ult = fl.modo === "livre" ? fl.ultimo : null;
  if (livre && ult) {
    v.balao = v.texto = "✧ " + ult.fala + iconeVerif(ult.verificacao);
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
/** a causa da ultima decisao em icones, no "Por que ele disse isso" (fora da cena: sobre ela so o chamado, o balao e o DigiBrain); sem causa, "?" */
const ICONE_CAUSA: Record<string, "carne" | "tempo" | "joinha" | "coracao" | "exclam"> = {
  fome: "carne", necessidade_fome: "carne", latencia_fome: "tempo", latencia_higiene: "tempo", tempo_sem_cuidado: "tempo", demora: "tempo",
  elogio: "joinha", elogios: "joinha", carinho: "coracao", bronca: "exclam", repreensoes: "exclam",
};
function CausaIcones() {
  const { motor: m } = useJogo(), mot = m.motivo;
  if (!mot || mot.origem !== "vida") return null;
  const ic = mot.exploracao ? [] : [...new Set(mot.fatores.map(f => ICONE_CAUSA[f]).filter(Boolean))].slice(0, 3);
  const txt = mot.exploracao || !mot.fatores.length ? "sem causa registrada" : mot.fatores.map(f => FATORES_TXT[f]?.marcador ?? f).join(" + ");
  return (
    <span className="causa-icones" role="img" aria-label={`causa: ${txt}`} title={txt}>
      {ic.length ? ic.flatMap((x, i) => [i > 0 ? <b key={"m" + i}>+</b> : null, <span key={"p" + i} className="causa-ic">{x === "tempo" ? <Peca nome="icone_tempo" /> : <Peca nome={"emoji_" + x} escala={2} />}</span>])
        : <b className="balao-q">?</b>}
    </span>
  );
}
/** a fala de agora num balao sobre o cenario; tocar abre o porque no painel de detalhes */
const MODO_CURTO: Record<string, string> = { template: "frases prontas", moldura: "moldura", livre: "fala livre" };
/** some AVISO_MS depois da ultima reacao (hudPet.ts); sem fala registrada, nada; arrasta pela tela */
function BalaoFala({ v, abrir }: { v: VistaFala; abrir: () => void }) {
  const { motor: m } = useJogo(), mot = m.motivo;
  const chave = mot && mot.origem === "vida" ? `${mot.acao}|${mot.fatores.join(",")}|${mot.recusa?.acaoDono ?? ""}|${v.texto}` : v.texto;
  const vis = useAviso(chave), arr = useArrastavel<HTMLButtonElement>("fala");
  if (!vis || (!v.texto && !v.detalhe)) return null;
  return (
    <button type="button" className={v.classe + " cena-fala"} title={v.titulo} aria-haspopup="dialog" onClick={abrir} {...arr}>
      <span className="balao-txt">{v.balao}</span>{v.causa}<small>toque para ver o porquê</small></button>
  );
}
/** no painel: o que ele faz, a causa registrada, o detalhe e a fonte da fala */
function DetalheFala({ v, semTitulo = false }: { v: VistaFala; semTitulo?: boolean }) {
  const { motor: m } = useJogo(), { freado } = useTempo(), r = rotuloLLM(), fl = useFalaLivre();
  return (
    <section className="det-sec det-fala" aria-labelledby="det-fala-tit">
      {!semTitulo && <h3 id="det-fala-tit">Por que ele disse isso</h3>}
      <div className="fala-det">
        <span className="pet-status dl-lcd">{NOME_PET[m.acao]}{freado ? " · tempo em 1x até atender" : ""}</span><CausaIcones />{v.causa}
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
  if (nascendo > 0 || m.morte) return null;
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

/* emocao (prancha UpPet): a ultima emocao registrada na memoria do pet (so pets v2+; v1 nao tem emocao), no painel Estado */
const EMOTE_EMOCAO: Record<string, string> = { alegria: "emoji_feliz", euforia: "emoji_feliz", orgulho: "emoji_feliz", ternura: "emoji_coracao" };
function Emocao() {
  const { motor: m } = useJogo();
  const em = (m.pol.mem as unknown as { emocoes: { nome: string }[] }).emocoes;
  const ult = em[em.length - 1];
  if (!ult) return null;
  return <p className="est-linha est-emocao"><span className="est-rot">emoção</span>{EMOTE_EMOCAO[ult.nome] && <Peca nome={EMOTE_EMOCAO[ult.nome]} />}{EMOCAO_TXT[ult.nome][0]}</p>;
}

/* ------------------------------------------------ necessidades, chamado e desejo */
const NEC_PET: [("fome" | "energia" | "higiene" | "humor"), string][] = [["fome", "comida"], ["energia", "energia"], ["higiene", "higiene"], ["humor", "humor"]];
const EMOTE_CHAMADO: Record<Chamado, string | null> = { fome: "emoji_carne", carinho: "emoji_coracao", higiene: null };
const EMOTE_DESEJO: Record<string, string> = { comer: "emoji_carne", brincar: "emoji_nota", chamar_atencao: "emoji_exclam", explorar: "emoji_estrela" };

const ICONE_NEC: Record<Necessidade, LucideIcon> = { fome: Drumstick, energia: Zap, higiene: Droplet, humor: Smile };
/** as cinco do motor em % (o valor de 0 a 1 do motor, arredondado); abaixo de metade a barra fica na cor de alerta */
function Necessidades() {
  const { motor: m } = useJogo(), e = m.e;
  const linha = (k: string, I: LucideIcon, medidor: ReactNode) => <div className={"nec-linha nec-linha--" + k} key={k}><I className="nec-ic" aria-hidden="true" />{medidor}</div>;
  return (
    <div className="necessidades4">
      {NEC_PET.map(([k, rot]) => linha(k, ICONE_NEC[k], <MedidorHx rotulo={rot} valor={Math.round(e[k] * 100)} max={100} porcento tom={e[k] < LIMIAR_NEC ? "alerta" : "neutro"} />))}
      {linha("saude", HeartPulse, <MedidorHx rotulo="saúde" valor={Math.round(e.saude * 100)} max={100} porcento tom={e.saude < .3 ? "perigo" : "ok"} />)}
      {e.saude < .3 && <span className="nec-critica">saúde crítica</span>}
    </div>
  );
}
/** pets v4: morreu (lesão demais ou sem tratar). O registro fica; so um ovo novo continua o jogo */
function Morte() {
  const { motor: m } = useJogo();
  if (!m.morte) return null;
  return (
    <div className="dl-card chamado chamado--morte" role="alert">
      <span className="chamado-txt"><b>{nomeForma(m.forma)} se foi</b>
        <span className="dl-apoio">{m.morte.causa === "lesoes" ? "se machucou demais nas lutas" : "a lesão ficou sem tratamento por tempo demais"}. O Diário guarda a vida inteira.</span></span>
      <button type="button" className="hx-continuar" onClick={abrirEscolhaBrasao}>Chocar um ovo novo</button>
    </div>
  );
}
function Chamados({ agir }: { agir: (a: AcaoDono) => void }) {
  const { motor: m } = useJogo(), ab = chamadosVisiveis(m), tick = m.e.tick;
  if (!ab.length && m.acao === "chamar_atencao") return (
    <div className="dl-card chamado">
      <span className="chamado-ic"><Peca nome="emoji_exclam" escala={2} reserva="!" /></span>
      <span className="chamado-txt"><b>Chamando você</b><span className="dl-apoio">um carinho atende</span></span>
      <button type="button" className="hx-continuar" onClick={() => agir("acariciar")}>Atender</button>
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
        <button type="button" className="hx-continuar" onClick={() => agir(ACAO_CHAMADO[c][0])}>Atender</button>
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
const ROTULO_BAIXO: Record<Necessidade, string> = { fome: "está com fome", energia: "energia baixa", higiene: "higiene baixa", humor: "humor baixo" };
const EMOTE_NEC: Record<Necessidade, string | null> = { fome: "emoji_carne", energia: null, higiene: null, humor: "emoji_nota" };
const ACAO_NEC: Record<Necessidade, AcaoDono | null> = { fome: "alimentar", energia: null, higiene: "limpar", humor: "brincar" };
const ACAO_DESEJO: Record<string, AcaoDono> = { comer: "alimentar", brincar: "brincar", limpar: "limpar", chamar_atencao: "acariciar" };
/** abaixo de metade a barra fica na cor de necessidade (Necessidades); a mais baixa delas e a prioritaria */
const LIMIAR_NEC = .5;

/** a mais baixa das necessidades que passaram do limiar (a fome em FOME_FALA, as outras em LIMIAR_NEC); a regra do resumo e a do aviso do celular */
function necessidadeBaixa(m: Motor): Necessidade | undefined {
  return NEC_PET.map(([k]) => k).filter(k => m.e[k] < (k === "fome" ? FOME_FALA : LIMIAR_NEC)).sort((a, b) => m.e[a] - m.e[b])[0];
}

interface Resumo { texto: string; emote: string | null; acao: AcaoDono | null }
/** o resumo de agora, so do motor: o ovo; a necessidade mais baixa (se alguma esta abaixo da metade); o desejo; ou o que ele faz */
const TEXTO_CHAMADO: Record<Chamado, string> = { fome: "está com fome", higiene: "quer um banho", carinho: "quer carinho" };
function resumoAgora(m: Motor, nascendo: number): Resumo {
  if (nascendo > 0) return { texto: "o ovo está chocando", emote: null, acao: null };
  /* chamado aberto que ainda nao aperta: so o resumo (e a acao certa destacada no dock); o cartao com o Atender e o temPedido */
  const c = chamadosVisiveis(m)[0];
  if (c) return { texto: TEXTO_CHAMADO[c], emote: EMOTE_CHAMADO[c], acao: ACAO_CHAMADO[c][0] };
  /* a fome so vira texto abaixo de FOME_FALA; entre ela e a metade, so o emoji sobre a cabeca do pet (PalcoPet) */
  const baixa = necessidadeBaixa(m);
  if (baixa) return { texto: ROTULO_BAIXO[baixa], emote: EMOTE_NEC[baixa], acao: ACAO_NEC[baixa] };
  const d = m.desejoAtual(m.observacaoAgora(), m.e.tick);
  if (d) return { texto: (d.tipo === "necessidade" ? "precisa " : "quer ") + ALVOS_DESEJO[d.alvo][1], emote: EMOTE_DESEJO[d.alvo] ?? null, acao: ACAO_DESEJO[d.alvo] ?? null };
  return { texto: "agora: " + NOME_PET[m.acao], emote: null, acao: null };
}
/** o que o celular mostra de uma necessidade (docs/PROPOSTAS_V3_UX_TELA_PET.md, "Mobile minimo", M1-6 a M1-8, M1-13): o aviso (icone e %), o ponto
    rosa no retrato e a acao rosa e maior saem da MESMA regra do resumo (resumoAgora: o chamado aberto, a necessidade mais baixa, o desejo que e
    necessidade), sem o texto e sem numero novo. `acao` e a que resolve (a energia nao tem); `pct` so na necessidade do corpo; `aviso` e false so
    na energia baixa com o pet dormindo (dormir ja e ele resolvendo): o ponto fica */
const ICONE_CHAMADO: Record<Chamado, LucideIcon> = { fome: Drumstick, higiene: Droplet, carinho: Heart };
export interface NecMovel { icone: LucideIcon; pct: number | null; texto: string; acao: AcaoDono | null; aviso: boolean }
export function necessidadeMovel(m: Motor, nascendo: number): NecMovel | null {
  if (nascendo > 0 || m.morte) return null;
  const c = chamadosVisiveis(m)[0];
  if (c) return { icone: ICONE_CHAMADO[c], pct: null, texto: TEXTO_CHAMADO[c], acao: ACAO_CHAMADO[c][0], aviso: true };
  const baixa = necessidadeBaixa(m);
  if (baixa) return { icone: ICONE_NEC[baixa], pct: Math.round(m.e[baixa] * 100), texto: ROTULO_BAIXO[baixa], acao: ACAO_NEC[baixa], aviso: !(baixa === "energia" && m.acao === "dormir") };
  const d = m.desejoAtual(m.observacaoAgora(), m.e.tick);
  /* o desejo que e necessidade pinta so o ponto e a acao (nao ha numero para o aviso); a vontade aprendida nao e necessidade (M1-13) */
  if (d && d.tipo === "necessidade") return { icone: ICONE_CHAMADO.carinho, pct: null, texto: "precisa " + ALVOS_DESEJO[d.alvo][1], acao: ACAO_DESEJO[d.alvo] ?? null, aviso: false };
  return null;
}
/** o cartao grande so quando aperta: um chamado do In-Training no ultimo terco da janela, ou ele mesmo chamando voce. Antes disso o
    chamado fica no resumo, sem cobrir a cena (o Matheus, 2026-11-01: o pedido na cara so quando for emergencia). PROPOSTO, SEM FONTE */
const URGENTE_RESTA = CAT.janelaChamado / 3;
function temPedido(m: Motor): boolean {
  const tick = m.e.tick;
  return chamadosVisiveis(m).some(c => CAT.janelaChamado - (tick - m.chamados.abertos[c]!) <= URGENTE_RESTA) || m.acao === "chamar_atencao";
}
/** a necessidade prioritaria, no cartao do alto ao centro: a morte, um pedido aberto (com o Atender) ou o resumo, que abre o Estado.
    Sem o nome do pet (ele esta na plaquinha do topo) */
function Prioridade({ abrirDetalhes, movel = false }: { abrirDetalhes?: () => void; movel?: boolean }) {
  const { motor: m, nascendo } = useJogo(), r = resumoAgora(m, nascendo), pedido = !m.morte && nascendo === 0 && temPedido(m), nec = movel ? necessidadeMovel(m, nascendo) : null;
  /* o resumo so aparece por AVISO_MS quando muda (hudPet.ts); a fome critica, o pedido e a morte ficam. No celular o aviso da necessidade segue o mesmo tempo */
  const vis = useAviso(movel ? nec?.texto ?? "" : r.texto, nascendo === 0 && m.e.fome < FOME_FALA), arr = useArrastavel<HTMLDivElement>("alerta");
  /* o celular anuncia a necessidade uma vez a cada mudanca do texto (nao a cada tick que muda o %): a regiao fica sempre montada e o % entra no texto
     no momento da mudanca */
  const falado = movel && nec?.aviso ? nec.texto : "", [anuncio, setAnuncio] = useState("");
  useEffect(() => { setAnuncio(falado ? falado + (nec?.pct != null ? `, ${nec.pct} %` : "") : ""); }, [falado]);
  if (movel) {
    /* o celular (M1): o pedido urgente e a morte ficam como hoje, com texto; o resto do resumo vira o aviso (icone e %) */
    const cartao = m.morte ? <Morte /> : pedido ? <div className="pet-pedido"><Chamados agir={agir} /></div> : null;
    return (
      <>
        <span className="sr-only" role="status" aria-live="polite">{anuncio}</span>
        {cartao ? <div className="pet-alerta" {...arr}>{cartao}</div> : vis && nec?.aviso ? <AvisoNec nec={nec} abrirDetalhes={abrirDetalhes} /> : null}
      </>
    );
  }
  const corpo = m.morte ? <Morte /> : pedido ? <div className="pet-pedido"><Chamados agir={agir} /></div> : vis ? <Resumo r={r} nascendo={nascendo} abrirDetalhes={abrirDetalhes!} /> : null;
  if (!corpo) return null;
  return <div className="pet-alerta" {...arr}>{corpo}</div>;
}
/** o aviso da necessidade no celular: o icone e o %, em rosa cheio (a forma, a caixa, nao so a cor); o nome e o texto do resumo de hoje e "Estado"
    (sr-only), o % e so desenho. Com os detalhes do pet desligados nao ha Estado para abrir: um status, nao um botao */
function AvisoNec({ nec, abrirDetalhes }: { nec: NecMovel; abrirDetalhes?: () => void }) {
  const I = nec.icone;
  const corpo = <><I aria-hidden="true" />{nec.pct !== null && <span aria-hidden="true">{nec.pct} %</span>}<span className="sr-only">{nec.texto}</span>{abrirDetalhes && <span className="sr-only">Estado</span>}</>;
  const cls = "mm-aviso hx-chip--necessidade";
  return abrirDetalhes ? <button type="button" className={cls + " mm-bt"} onClick={abrirDetalhes}>{corpo}</button> : <span className={cls}>{corpo}</span>;
}
function Resumo({ r, nascendo, abrirDetalhes }: { r: Resumo; nascendo: number; abrirDetalhes: () => void }) {
  return (
    <button type="button" className="pet-prioridade" onClick={abrirDetalhes}>
      <span className="pet-prioridade-ic" aria-hidden="true">{r.emote ? <Peca nome={r.emote} escala={2} reserva="•" /> : nascendo > 0 ? "•" : <Peca nome="emoji_feliz" escala={2} reserva="•" />}</span>
      <span className="pet-prioridade-txt"><b>{r.texto}</b></span>
      <span className="pet-prioridade-ver">Estado<ChevronRight size={16} aria-hidden="true" /></span>
    </button>
  );
}


/* ------------------------------------------------ o dock de acoes (o clique passa por src/acoes.ts, como o comando do chat) */
/* pets v11 em diante: sem elogio, bronca, petisco e banheiro (ACOES_DONO_JOGO_V11); o carinho e o tapa sao gestos no corpo. O dock mostra
   as seis na ordem abaixo; no celular (DockMovel), as tres primeiras e as outras em "Mais", com o Por racao (so pets v12, com mundo). */
const ORDEM_DOCK: AcaoDono[] = ["alimentar", "brincar", "limpar", "acariciar", "tapa", "tratar_lesao"];
const ICONE_QUEM = { dono: Hand, pet: PawPrint, recusa: Ban } as const;

/* icone de cada acao do dono: prato do guia, gota, nota, coracao, joinha e exclamacao */
const GOTA = <svg className="ic-gota" viewBox="0 0 8 8" width="24" height="24" aria-hidden="true"><path fill="#2C73E0" d="M3 0h2v2h1v1h1v3h-1v1h-4v-1h-1v-3h1v-1h1z" /><path fill="#BFE3FF" d="M2 3h1v2h-1z" /></svg>;
const CRUZ = <svg className="ic-cruz" viewBox="0 0 8 8" width="24" height="24" aria-hidden="true"><path fill="#E0443A" d="M3 1h2v2h2v2h-2v2h-2v-2h-2v-2h2z" /></svg>;
function IconeAcao({ a }: { a: AcaoDono }) {
  if (a === "alimentar") return <Deco nome="Growth_Guide_Icon_06" largura={24} altura={24} className="ic-acao" reserva={<Peca nome="emoji_carne" escala={2} />} />;
  if (a === "limpar") return GOTA;
  if (a === "levar_ao_banheiro") return GOTA;
  if (a === "tratar_lesao") return CRUZ;
  const em = ({ brincar: "emoji_nota", acariciar: "emoji_coracao", elogiar: "emoji_joinha", repreender: "emoji_exclam", petisco: "emoji_estrela", tapa: "emoji_exclam" } as Partial<Record<AcaoDono, string>>)[a];
  return em ? <Peca nome={em} escala={2} /> : null;
}

/** a partir de 900 px (a mesma largura em que a casca vira trilho) o dock mostra as seis acoes; abaixo, tres e o Mais (DockMovel) */
const CONSULTA_LARGO = "(min-width: 900px)";
const eLargo = (): boolean => typeof matchMedia === "function" && matchMedia(CONSULTA_LARGO).matches;
function useLargo(): boolean {
  return useSyncExternalStore(o => {
    if (typeof matchMedia !== "function") return () => {};
    const mq = matchMedia(CONSULTA_LARGO); mq.addEventListener("change", o);
    return () => mq.removeEventListener("change", o);
  }, eLargo, () => true);
}

function DockLargo() {
  const { motor: m, nascendo } = useJogo(), [mais, setMais] = useState(false);
  const botaoMais = useRef<HTMLButtonElement>(null), menu = useRef<HTMLDivElement>(null);
  const sugerida = resumoAgora(m, nascendo).acao;
  const fixas = ORDEM_DOCK, extras = ORDEM_DOCK.filter(a => !fixas.includes(a));
  const comRacao = !!m.mundo && nascendo === 0, temMais = extras.length > 0 || comRacao;
  const fechar = (voltarFoco: boolean) => { setMais(false); if (voltarFoco) botaoMais.current?.focus(); };
  useEffect(() => {
    if (!mais) return;
    menu.current?.querySelector<HTMLElement>("button")?.focus();
    const tecla = (e: KeyboardEvent) => { if (e.key === "Escape") { e.stopPropagation(); fechar(true); } };
    const fora = (e: PointerEvent) => { const n = e.target as Node; if (!menu.current?.contains(n) && !botaoMais.current?.contains(n)) setMais(false); };
    document.addEventListener("keydown", tecla); document.addEventListener("pointerdown", fora);
    return () => { document.removeEventListener("keydown", tecla); document.removeEventListener("pointerdown", fora); };
  }, [mais]);
  useEffect(() => { if (!temMais) setMais(false); }, [temMais]);
  /* v12: o Alimentar e a reserva temporaria do MVP (poe a racao no comedouro); a interacao planejada e por a racao no lugar (BarraRacao) */
  const reserva = (a: AcaoDono) => !!m.mundo && a === "alimentar";
  const botao = (a: AcaoDono, cls: string) => <button type="button" key={a} className={`hx-btn dock-bt ${cls}`} onClick={() => { agir(a); setMais(false); }}
    aria-label={reserva(a) ? `${ROTULO_DONO[a]} (reserva: põe a ração no comedouro)` : undefined} title={reserva(a) ? "Reserva temporária: põe a ração no comedouro" : undefined}>
    <IconeAcao a={a} /><span>{ROTULO_DONO[a]}</span>{reserva(a) && <small className="acao-reserva" aria-hidden="true">reserva</small>}</button>;
  return (
    <div className="acoes-pet dock" role="group" aria-label="Cuidar e ensinar">
      {fixas.map(a => botao(a, "acao-destaque" + (sugerida === a ? " acao-destaque--sugerida" : "")))}
      {temMais && <button type="button" ref={botaoMais} className="hx-btn dock-bt acao-mais" aria-expanded={mais} aria-controls="acoes-mais" aria-haspopup="true"
        onClick={() => setMais(!mais)}><Ellipsis size={24} aria-hidden="true" /><span>Mais</span></button>}
      {mais && <div className="acoes-mais dock-mais" id="acoes-mais" ref={menu} role="group" aria-label="Mais ações">
        {extras.map(a => botao(a, "acao-extra"))}
        {comRacao && <BarraRacao aoUsar={() => fechar(false)} />}
        {comRacao && <BarraBola aoUsar={() => fechar(false)} />}
      </div>}
    </div>
  );
}

/* o celular (M1 do mobile minimo; docs/PROPOSTAS_V3_UX_TELA_PET.md): quatro circulos so com icone, as tres que resolvem uma necessidade e o Mais, que
   abre uma fileira com o Carinho, o Tapa, o Tratar e, nos pets com mundo, o Por racao e o Por a bola. A acao que resolve a necessidade cresce e fica rosa
   (a mesma regra do aviso, necessidadeMovel); a vontade aprendida ganha so o contorno ciano tracejado; se a sugerida mora no Mais, o Mais leva a marca
   (M1-13). O Mais e um leque do estado movel (movel.ts): abrir o retrato fecha o Mais e o contrario */
const ICONE_DONO: Partial<Record<AcaoDono, LucideIcon>> = { alimentar: Drumstick, brincar: Music, limpar: Droplet, acariciar: Heart, tapa: Hand, tratar_lesao: Cross };
function DockMovel() {
  const { motor: m, nascendo } = useJogo(), mais = useLeque() === "mais";
  const botaoMais = useRef<HTMLButtonElement>(null), menu = useRef<HTMLDivElement>(null);
  const nec = necessidadeMovel(m, nascendo), rosa = nec?.acao ?? null, aprendida = nec ? null : resumoAgora(m, nascendo).acao;
  const fixas = ORDEM_DOCK.slice(0, 3), extras = ORDEM_DOCK.slice(3), comRacao = !!m.mundo && nascendo === 0;
  const sugerida = rosa ?? aprendida, marcaMais = sugerida && extras.includes(sugerida) ? (rosa ? "necessidade" : "aprendida") : undefined;
  const fechar = (voltarFoco: boolean) => { fecharLeque("mais"); if (voltarFoco) botaoMais.current?.focus(); };
  useEffect(() => {
    if (!mais) return;
    menu.current?.querySelector<HTMLElement>("button")?.focus();
    const tecla = (e: KeyboardEvent) => { if (e.key === "Escape") { e.stopPropagation(); fechar(true); } };
    const fora = (e: PointerEvent) => { const n = e.target as Node; if (!menu.current?.contains(n) && !botaoMais.current?.contains(n)) fecharLeque("mais"); };
    document.addEventListener("keydown", tecla); document.addEventListener("pointerdown", fora);
    return () => { document.removeEventListener("keydown", tecla); document.removeEventListener("pointerdown", fora); };
  }, [mais]);
  /* v12: o Alimentar e a reserva temporaria do MVP; o nome acessivel e o de hoje */
  const reserva = (a: AcaoDono) => !!m.mundo && a === "alimentar";
  const botao = (a: AcaoDono, cls: string) => {
    const I = ICONE_DONO[a];
    if (!I) throw new Error("acao do dono sem icone no celular: " + a);
    return <BotaoMovel key={a} className={"mm-bt " + cls} rotulo={ROTULO_DONO[a]} lado="cima" onClick={() => { agir(a); fecharLeque("mais"); }}
      aria-label={reserva(a) ? `${ROTULO_DONO[a]} (reserva: põe a ração no comedouro)` : undefined} title={reserva(a) ? "Reserva temporária: põe a ração no comedouro" : undefined}>
      <I aria-hidden="true" /></BotaoMovel>;
  };
  const marca = (a: AcaoDono) => (a === rosa ? " mm-sug" : a === aprendida ? " mm-sug mm-sug--aprendida" : "");
  return (
    <div className="acoes-pet mm-acoes" role="group" aria-label="Cuidar e ensinar">
      {fixas.map(a => botao(a, "mm-acao acao-destaque" + (rosa === a ? " acao-destaque--sugerida" : aprendida === a ? " acao-destaque--aprendida" : "")))}
      <BotaoMovel ref={botaoMais} className="mm-bt mm-acao acao-mais" rotulo="Mais" lado="cima" aria-expanded={mais} aria-controls="acoes-mais" aria-haspopup="true" data-marca={marcaMais}
        onClick={() => alternarLeque("mais")}>{mais ? <X aria-hidden="true" /> : <Ellipsis aria-hidden="true" />}</BotaoMovel>
      {mais && <div className="acoes-mais mm-mais" id="acoes-mais" ref={menu} role="group" aria-label="Mais ações">
        {extras.map(a => botao(a, "mm-extra acao-extra" + marca(a)))}
        {comRacao && <Segura className="mm-segura" rotulo="Pôr ração"><BarraRacao aoUsar={() => fechar(false)} /></Segura>}
        {comRacao && <Segura className="mm-segura" rotulo="Pôr a bola"><BarraBola aoUsar={() => fechar(false)} /></Segura>}
      </div>}
    </div>
  );
}
/** o dock: as seis acoes e o Mais (>= 900 px) ou o dock do celular (abaixo) */
function DockPet() { return useLargo() ? <DockLargo /> : <DockMovel />; }

/* ------------------------------------------------ os paineis: empilhados a direita (>= 900 px) ou um por vez pela borda (celular) */
type Painel = "estado" | "evolucao" | "acoes" | "digibrain" | "fala";
type PainelHud = "estado" | "evolucao" | "acoes";

/** a proxima evolucao, so com o que o motor tem (previsaoEvo, o mesmo da tela Evolucao): a forma atual, o nivel que vem e, se o motor ja
    decidiu (o Mega), a forma seguinte; sem proxima evolucao, nada */
function ProximaEvolucao({ irEvolucao }: { irEvolucao: () => void }) {
  const { motor: m } = useJogo(), a = useAtlas(), p = previsaoEvo(m);
  if (!p) return <p className="mod-vazio">sem próxima evolução</p>;
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
      <button type="button" className="hx-btn mod-link" onClick={irEvolucao}>Ver a árvore de evolução</button>
    </div>
  );
}
/** as ultimas linhas do registro (o que voce fez, o que ele fez e as recusas) */
type LinhaHist = Motor["historico"][number];
const ultimasDoRegistro = (m: Motor, n: number): LinhaHist[] => m.historico.filter(h => h.quem === "dono" || h.quem === "pet" || h.quem === "recusa").slice(-n).reverse();
const textoHist = (h: LinhaHist): string => h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] ?? h.a : h.a;
function UltimasAcoes({ irRegistro, n = 8 }: { irRegistro: () => void; n?: number }) {
  const { motor: m } = useJogo(), itens = ultimasDoRegistro(m, n);
  return (
    <>
      {itens.length ? <ol className="mod-registro">{itens.map((h, i) => {
        const I = ICONE_QUEM[h.quem as keyof typeof ICONE_QUEM];
        return <li key={i} data-quem={h.quem}><time>{hhmm(h.t)}</time><span className="mod-registro-ic"><I size={18} aria-hidden="true" /></span>
          <span>{h.quem === "dono" ? "você: " : h.quem === "recusa" ? "recusou: " : ""}{textoHist(h)}</span></li>;
      })}</ol> : <p className="mod-vazio">nada no registro ainda</p>}
      <button type="button" className="hx-btn mod-link" onClick={irRegistro}>Ver tudo no Diário</button>
    </>
  );
}
/** o Estado: as cinco necessidades e, em "Detalhes", a emocao, o mundo (v12), o desejo e a confianca de combate */
function EstadoPet({ detalhes, alternarDetalhes }: { detalhes: boolean; alternarDetalhes: () => void }) {
  const id = useId();
  return (
    <div className="det-estado">
      <Necessidades />
      <button type="button" className="hud-detalhes" aria-expanded={detalhes} aria-controls={id} onClick={alternarDetalhes}>
        Detalhes<ChevronRight size={16} aria-hidden="true" /></button>
      {detalhes && <div className="det-estado-mais" id={id}><Emocao /><InfoMundo /><Desejo /><EstadoConfianca /></div>}
    </div>
  );
}

const TITULO_PAINEL: Record<Painel, string> = { estado: "Estado atual", evolucao: "Evolução", acoes: "Últimas ações", digibrain: "DigiBrain", fala: "Por que ele disse isso" };
const ICONE_PAINEL: Record<Exclude<Painel, "fala">, LucideIcon> = { estado: Activity, evolucao: TrendingUp, acoes: History, digibrain: Brain };

/* o que fica aberto nos paineis empilhados: uma preferencia de tela, numa chave propria (fora do save, do registro e do replay) */
interface AbertosHud { estado: boolean; evolucao: boolean; acoes: boolean; detalhes: boolean }
const CHAVE_HUD = CHAVE + "-hud";
const HUD_PADRAO: AbertosHud = { estado: true, evolucao: false, acoes: false, detalhes: false };
function lerHud(): AbertosHud {
  let salvo: string | null = null;
  try { salvo = localStorage.getItem(CHAVE_HUD); } catch { /* sem armazenamento: o padrao */ }
  if (!salvo) return HUD_PADRAO;
  try {
    const o = JSON.parse(salvo) as Partial<AbertosHud>;
    return { estado: o.estado ?? true, evolucao: !!o.evolucao, acoes: !!o.acoes, detalhes: !!o.detalhes };
  } catch { return HUD_PADRAO; }    /* preferencia de tela ilegivel: o padrao (nao e dado do pet) */
}
function useAbertosHud(): [AbertosHud, (k: keyof AbertosHud, v?: boolean) => void] {
  const [ab, setAb] = useState(lerHud);
  const mudar = (k: keyof AbertosHud, v?: boolean) => setAb(a => {
    const n = { ...a, [k]: v ?? !a[k] };
    try { localStorage.setItem(CHAVE_HUD, JSON.stringify(n)); } catch { /* preferencia de tela */ }
    return n;
  });
  return [ab, mudar];
}

/** um painel empilhado: o cabecalho e o botao que recolhe; fechado, mostra uma linha de resumo */
function PainelHud({ id, aberto, alternar, resumo, children }: { id: PainelHud; aberto: boolean; alternar: () => void; resumo?: string; children: ReactNode }) {
  const corpo = useId(), desc = useId(), I = ICONE_PAINEL[id];
  return (
    <section className="hud-painel" data-painel-pet={id} data-aberto={aberto}>
      <h2 className="hud-painel__cab">
        <button type="button" className="hud-painel__bt" aria-expanded={aberto} aria-controls={corpo} aria-label={TITULO_PAINEL[id]}
          aria-describedby={!aberto && resumo ? desc : undefined} onClick={alternar}>
          <I className="hud-painel__ic" aria-hidden="true" />
          <span className="hud-painel__txt"><span className="hud-painel__tit">{TITULO_PAINEL[id]}</span>
            {!aberto && resumo && <span className="hud-painel__resumo" id={desc}>{resumo}</span>}</span>
          <span className="hud-risca" aria-hidden="true" />
          <ChevronDown className="hud-painel__seta" aria-hidden="true" />
        </button>
      </h2>
      {aberto && <div className="hud-painel__corpo" id={corpo}>{children}</div>}
    </section>
  );
}

/** o painel DigiBrain: o do modular no pet de teste (v16), o do A v11 nos outros */
function PainelDigiBrain() {
  const { motor: m } = useJogo();
  return m.lab ? <div className="pet-painel__folha dl digibrain"><div className="db-folha-selo"><SeloExperimental /><span className="db-selo">cérebro modular</span></div><ConteudoDigiBrainLab /></div>
    : <div className="pet-painel__folha dl digibrain"><div className="db-folha-selo"><SeloDigiBrain replay={false} /></div><ConteudoDigiBrain /></div>;
}
function ConteudoPainel({ id, v, irRegistro, irEvolucao, detalhes, alternarDetalhes }: {
  id: Painel; v: VistaFala; irRegistro: () => void; irEvolucao: () => void; detalhes: boolean; alternarDetalhes: () => void;
}) {
  switch (id) {
    case "estado": return <EstadoPet detalhes={detalhes} alternarDetalhes={alternarDetalhes} />;
    case "evolucao": return <ProximaEvolucao irEvolucao={irEvolucao} />;
    case "acoes": return <UltimasAcoes irRegistro={irRegistro} />;
    /* o DigiBrain e o porque da fala, com a pele escura (D8) */
    case "digibrain": return <PainelDigiBrain />;
    case "fala": return <div className="pet-painel__folha dl"><DetalheFala v={v} semTitulo /></div>;
  }
}

/* ------------------------------------------------ o leque do retrato (celular) */
/** o toque no retrato (Topo.tsx, so abaixo de 900 px) abre os cinco vitais em icones (um botao so, o "Estado atual", com os valores em aria-describedby;
    abaixo do limiar o numero vai numa caixa rosa cheia: a forma e a cor, M1-14) e os paineis (Evolucao, Ultimas acoes, DigiBrain) com o Configuracoes e o
    Meus pets (M1-1). Esc, o toque fora e um segundo toque no retrato fecham, e o foco volta ao retrato. Com os detalhes do pet desligados so ha o
    Configuracoes e o Meus pets (M1-11) */
function LequePet({ tem, abrirDe, abrirConfig, abrirMeusPets }: {
  tem: (id: Painel) => boolean; abrirDe: (q: Painel) => void; abrirConfig: () => void; abrirMeusPets: () => void;
}) {
  const { motor: m } = useJogo(), aberto = useLeque() === "paineis", raiz = useRef<HTMLDivElement>(null), desc = useId();
  const retrato = () => document.querySelector<HTMLElement>(".mm-retrato");
  const fechar = (voltarFoco: boolean) => { fecharLeque("paineis"); if (voltarFoco) retrato()?.focus(); };
  useEffect(() => {
    if (!aberto) return;
    raiz.current?.querySelector<HTMLElement>("button")?.focus();
    const tecla = (e: KeyboardEvent) => { if (e.key === "Escape") { e.stopPropagation(); fechar(true); } };
    const fora = (e: PointerEvent) => { const n = e.target as Node; if (!raiz.current?.contains(n) && !(n instanceof Element && n.closest(".mm-retrato"))) fecharLeque("paineis"); };
    document.addEventListener("keydown", tecla); document.addEventListener("pointerdown", fora);
    return () => { document.removeEventListener("keydown", tecla); document.removeEventListener("pointerdown", fora); };
  }, [aberto]);
  if (!aberto) return null;
  const e = m.e;
  const vitais = [...NEC_PET.map(([k, rot]) => ({ k, rot, I: ICONE_NEC[k], v: Math.round(e[k] * 100), baixa: e[k] < LIMIAR_NEC, critica: false })),
    { k: "saude", rot: "saúde", I: HeartPulse, v: Math.round(e.saude * 100), baixa: false, critica: e.saude < .3 }];
  const falado = vitais.map(x => `${x.rot} ${x.v} %${x.baixa ? ", baixa" : x.critica ? ", crítica" : ""}`).join("; ");
  /* os modais (Ajustes, Meus pets) devolvem o foco a quem estava focado ao abrir: o retrato, e nao o item do leque, que ja saiu da arvore */
  const abrirModalDe = (abrir: () => void) => () => { retrato()?.focus(); fecharLeque("paineis"); abrir(); };
  return (
    <div className="mm-leque" id="leque-pet" ref={raiz} role="group" aria-label="Painéis do pet">
      {tem("estado") && (
        <button type="button" className="mm-caixa mm-pilula mm-bt mm-vitais" aria-label={TITULO_PAINEL.estado} aria-describedby={desc} onClick={() => abrirDe("estado")}>
          {vitais.map(x => (
            <span key={x.k} className={"mm-vit" + (x.baixa ? " mm-vit--baixa" : x.critica ? " mm-vit--critica" : "")} aria-hidden="true">
              <x.I /><b className={x.baixa ? "hx-chip--necessidade" : undefined}>{x.v}</b></span>
          ))}
          <span className="sr-only" id={desc}>{falado}</span>
        </button>
      )}
      <div className="mm-leque-paineis">
        {(["evolucao", "acoes", "digibrain"] as const).filter(tem).map(id => {
          const I = ICONE_PAINEL[id];
          return <BotaoMovel key={id} className="mm-caixa mm-forma mm-bt mm-bt48" rotulo={TITULO_PAINEL[id]} lado="dir" aria-label={TITULO_PAINEL[id]}
            onClick={() => abrirDe(id)}><I aria-hidden="true" /></BotaoMovel>;
        })}
        <BotaoMovel className="mm-caixa mm-forma mm-bt mm-bt48" rotulo="Configurações" lado="dir" aria-label="Configurações" onClick={abrirModalDe(abrirConfig)}><Settings aria-hidden="true" /></BotaoMovel>
        <BotaoMovel className="mm-caixa mm-forma mm-bt mm-bt48" rotulo="Meus pets" lado="dir" aria-label="Meus pets" aria-haspopup="dialog" onClick={abrirModalDe(abrirMeusPets)}><Users aria-hidden="true" /></BotaoMovel>
      </div>
    </div>
  );
}

/* ------------------------------------------------ a tela */
/** a barra de acoes ocupa o pe da tela: o habitat (camada de fundo) deixa esse espaco livre para o pet nao ficar coberto */
function useReservaDoHabitat(ref: { current: HTMLElement | null }, ativo: boolean): void {
  useEffect(() => {
    /* so a partir de 900 px: no celular a cena ocupa a tela inteira por tras das acoes (pet_movel.css) e nao reserva o pe */
    const el = ref.current; if (!el || !ativo) return;
    const raiz = document.documentElement.style;
    const medir = () => raiz.setProperty("--hab-baixo", `calc(${Math.ceil(el.getBoundingClientRect().height) + 24}px + var(--casca-barra))`);
    medir();
    const ro = new ResizeObserver(medir); ro.observe(el);
    return () => { ro.disconnect(); raiz.removeProperty("--hab-baixo"); };
  }, [ref, ativo]);
}
/** o encaixe do topo da casca (Topo.tsx, .topo-agora): a linha do agora entra nele, logo depois da plaquinha (a prancha da P1); no servidor e no
    primeiro desenho ainda nao ha topo, e a linha espera */
function useTopo(): HTMLElement | null {
  const [topo, setTopo] = useState<HTMLElement | null>(null);
  useEffect(() => { setTopo(document.querySelector<HTMLElement>(".topo-agora")); }, []);
  return topo;
}
export function TelaPet({ irRegistro, irEvolucao, abrirConfig, abrirMeusPets }: { irRegistro: () => void; irEvolucao: () => void; abrirConfig: () => void; abrirMeusPets: () => void }) {
  const { motor: m, nascendo } = useJogo(), fala = useFala(), largo = useLargo(), [aberto, setAberto] = useState<Painel | null>(null);
  const [hud, mudarHud] = useAbertosHud(), detalhesPet = useDetalhesPet();
  const painel = useRef<HTMLDivElement>(null), gatilho = useRef<HTMLElement | null>(null), dock = useRef<HTMLDivElement>(null), pilha = useRef<HTMLElement>(null);
  useReservaDoHabitat(dock, largo);
  const vivo = nascendo === 0 && !m.morte, p = vivo ? previsaoEvo(m) : null, temEvo = !!p;
  /* "Exibir detalhes do pet" desligado (Ajustes): sem Estado, Evolucao, Ultimas acoes e DigiBrain; o porque da fala fica */
  const tem = (id: Painel): boolean => id === "fala" ? nascendo === 0 : !detalhesPet ? false : id === "estado" || (nascendo === 0 && (id === "evolucao" ? temEvo : id === "digibrain" ? true : vivo));
  /* o painel que deixou de fazer sentido (o ovo chocando, o pet que morreu) fecha sozinho; no desktop Estado, Evolucao e Ultimas acoes
     ficam na pilha, e o painel flutuante e so o do DigiBrain e o do porque */
  const valido = (q: Painel | null): q is Painel => q !== null && tem(q) && (!largo || q === "digibrain" || q === "fala");
  const atual = valido(aberto) ? aberto : null;
  const abrir = (q: Painel) => { gatilho.current = document.activeElement as HTMLElement | null; setAberto(aberto === q ? null : q); };
  /* do leque do retrato (celular): o item que abriu sai da arvore, entao o foco volta ao retrato */
  const abrirDoLeque = (q: Painel) => { fecharLeque("paineis"); gatilho.current = document.querySelector<HTMLElement>(".mm-retrato"); setAberto(aberto === q ? null : q); };
  /* o leque e o Mais so existem abaixo de 900 px: ao largar o celular fecham, e ao sair da tela Pet nao ficam abertos */
  useEffect(() => { if (largo) mudarLeque(null); }, [largo]);
  useEffect(() => () => mudarLeque(null), []);
  const fechar = () => { setAberto(null); const g = gatilho.current; gatilho.current = null; setTimeout(() => { if (g?.isConnected) g.focus(); }, 0); };
  useEffect(() => { if (atual) painel.current?.focus(); }, [atual]);
  /* o resumo do chamado abre o Estado: na pilha (desktop) ou o painel da borda (celular) */
  const abrirEstado = () => {
    if (!largo) { abrir("estado"); return; }
    setAberto(null); mudarHud("estado", true);
    setTimeout(() => pilha.current?.querySelector<HTMLElement>("[data-painel-pet='estado'] .hud-painel__bt")?.focus(), 0);
  };
  const ult = ultimasDoRegistro(m, 1)[0], topo = useTopo();
  const resumoEvo = p ? (p.falta > 0 ? `próxima forma em ${duracao(p.falta)}` : "tempo do estágio cumprido") : undefined;
  const conteudo = (id: Painel) => <ConteudoPainel id={id} v={fala} irRegistro={irRegistro} irEvolucao={irEvolucao} detalhes={hud.detalhes} alternarDetalhes={() => mudarHud("detalhes")} />;
  return (
    <section className="pet-tela pet-home dl" aria-label="Tela do pet">
      <div className="pet-balcao">
        {vivo && <BalaoFala v={fala} abrir={() => abrir("fala")} />}
        {m.mundo && vivo && <FaixaRacao />}
      </div>
      {topo && largo && createPortal(<LinhaAgora aberto={atual === "digibrain"} sobPainel={atual !== null} aoAbrir={detalhesPet ? () => abrir("digibrain") : undefined} />, topo, "agora")}
      {!largo && <AgoraIcone aberto={atual === "digibrain"} sobPainel={atual !== null} aoAbrir={detalhesPet ? () => abrir("digibrain") : undefined} />}
      <Prioridade abrirDetalhes={largo || detalhesPet ? abrirEstado : undefined} movel={!largo} />
      {largo ? (!atual && detalhesPet && (
        <aside className="pet-hud" ref={pilha} aria-label="Painéis do pet">
          <PainelHud id="estado" aberto={hud.estado} alternar={() => mudarHud("estado")}>{conteudo("estado")}</PainelHud>
          {temEvo && <PainelHud id="evolucao" aberto={hud.evolucao} alternar={() => mudarHud("evolucao")} resumo={resumoEvo}>{conteudo("evolucao")}</PainelHud>}
          {vivo && <PainelHud id="acoes" aberto={hud.acoes} alternar={() => mudarHud("acoes")} resumo={ult ? `${hhmm(ult.t)} · ${textoHist(ult)}` : "nada no registro ainda"}>
            <UltimasAcoes irRegistro={irRegistro} n={5} /></PainelHud>}
        </aside>
      )) : (
        <LequePet tem={tem} abrirDe={abrirDoLeque} abrirConfig={abrirConfig} abrirMeusPets={abrirMeusPets} />
      )}
      {largo && nascendo === 0 && detalhesPet && (
        <button type="button" className="pet-etiqueta-db" aria-pressed={atual === "digibrain"} aria-controls="pet-painel" aria-label="DigiBrain" onClick={() => abrir("digibrain")}>
          <Brain size={18} aria-hidden="true" /><span>DigiBrain</span></button>
      )}
      {atual && (
        <div className="pet-painel" id="pet-painel" data-painel-pet={atual} ref={painel} tabIndex={-1} onKeyDown={e => { if (e.key === "Escape") { e.stopPropagation(); fechar(); } }}>
          <PainelHx titulo={TITULO_PAINEL[atual]} onFechar={fechar} rotuloFechar={`Fechar ${TITULO_PAINEL[atual]}`} className="pet-painel__hx">
            {conteudo(atual)}
          </PainelHx>
        </div>
      )}
      <div className="pet-dock" ref={dock}>
        {m.mundo && <AvisoRacao />}
        {!m.morte && <DockPet />}
      </div>
    </section>
  );
}
