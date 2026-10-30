/* Tela Pet sobre o habitat (docs/TAREFA_V2_LAYOUT_HABITAT.md, M3): a cena e a camada de fundo da casca (Habitat.tsx); aqui ficam so os
   controles flutuantes: o dock de acoes no rodape, o chamado do pet, o balao de fala e, na borda direita, os botoes dos paineis pequenos
   (Estado, Evolucao, Ultimas acoes, DigiBrain; um aberto por vez). Tudo derivado do motor na hora de desenhar; so mudarMotor() altera o pet. */
import type { ReactNode } from "react";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Activity, ArrowRight, Ban, Brain, ChevronRight, Ellipsis, Hand, History, PawPrint, TrendingUp, type LucideIcon } from "lucide-react";
import {
  ACAO_CHAMADO, ALVOS_DESEJO, CAT, DO_ESP, NOME_ESP, EMOCAO_TXT, FATORES_TXT, NOME_CHAMADO, NOME_EST, NOME_PET, OVO, TICK_INICIAL, TPD,
  chaveSprite, eNoite, expressarConfianca, nomeEstagio, nomeForma, nomeRivalConfianca, observacao, type AcaoDono, type Chamado, type MotivoVida, type Motor,
} from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
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
import { AvisoRacao, BarraRacao, FaixaRacao, InfoMundo } from "./PorRacao.tsx";
import "../../estilo/pet_dock.css";
import { ConteudoDigiBrain, SeloDigiBrain } from "../../componentes/DigiBrain.tsx";
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

function Necessidades() {
  const { motor: m } = useJogo(), e = m.e, saude = Math.round(e.saude * 100);
  return (
    <div className="necessidades4">
      {NEC_PET.map(([k, rot]) => <MedidorHx key={k} rotulo={rot} valor={blocos(e[k], 5)} max={5} tom={e[k] < .5 ? "alerta" : "neutro"} />)}
      <MedidorHx rotulo="saúde" valor={saude} max={100} tom={e.saude < .3 ? "perigo" : "ok"} />
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
  const { motor: m } = useJogo(), ab = m.chamadosAbertos(), tick = m.e.tick;
  if (!ab.length && m.acao === "chamar_atencao") return (
    <div className="dl-card chamado">
      <span className="chamado-ic"><Peca nome="emoji_exclam" escala={2} reserva="!" /></span>
      <span className="chamado-txt"><b>Chamando você</b><span className="dl-apoio">um carinho atende o pedido</span></span>
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
/** ha um pedido aberto que pede resposta agora (o chamado do In-Training, ou ele chamando)? */
function temPedido(m: Motor): boolean {
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


/* ------------------------------------------------ o dock de acoes (o clique passa por src/acoes.ts, como o comando do chat) */
/* pets v11 em diante: sem elogio, bronca, petisco e banheiro (ACOES_DONO_JOGO_V11); o carinho e o tapa sao gestos no corpo. O dock mostra
   as seis na ordem abaixo; no celular, as quatro primeiras e as outras em "Mais", com o Por racao (so pets v12, com mundo). */
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

/** a partir de 900 px (a mesma largura em que a casca vira trilho) o dock mostra as seis acoes; abaixo, quatro e o Mais */
const CONSULTA_LARGO = "(min-width: 900px)";
const eLargo = (): boolean => typeof matchMedia === "function" && matchMedia(CONSULTA_LARGO).matches;
function useLargo(): boolean {
  return useSyncExternalStore(o => {
    if (typeof matchMedia !== "function") return () => {};
    const mq = matchMedia(CONSULTA_LARGO); mq.addEventListener("change", o);
    return () => mq.removeEventListener("change", o);
  }, eLargo, () => true);
}

function DockPet() {
  const { motor: m, nascendo } = useJogo(), largo = useLargo(), [mais, setMais] = useState(false);
  const botaoMais = useRef<HTMLButtonElement>(null), menu = useRef<HTMLDivElement>(null);
  const sugerida = resumoAgora(m, nascendo).acao;
  const fixas = largo ? ORDEM_DOCK : ORDEM_DOCK.slice(0, 4), extras = ORDEM_DOCK.filter(a => !fixas.includes(a));
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
    <IconeAcao a={a} /><span>{ROTULO_DONO[a]}</span>{reserva(a) && <small className="acao-reserva">reserva</small>}</button>;
  return (
    <div className="acoes-pet dock" role="group" aria-label="Cuidar e ensinar">
      {fixas.map(a => botao(a, "acao-destaque" + (sugerida === a ? " acao-destaque--sugerida" : "")))}
      {temMais && <button type="button" ref={botaoMais} className="hx-btn dock-bt acao-mais" aria-expanded={mais} aria-controls="acoes-mais" aria-haspopup="true"
        onClick={() => setMais(!mais)}><Ellipsis size={24} aria-hidden="true" /><span>Mais</span></button>}
      {mais && <div className="acoes-mais dock-mais" id="acoes-mais" ref={menu} role="group" aria-label="Mais ações">
        {extras.map(a => botao(a, "acao-extra"))}
        {comRacao && <BarraRacao aoUsar={() => fechar(false)} />}
      </div>}
    </div>
  );
}

/* ------------------------------------------------ os paineis recolhiveis sobre o habitat (um aberto por vez) */
type Painel = "estado" | "evolucao" | "acoes" | "digibrain" | "fala";

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
function UltimasAcoes({ irRegistro }: { irRegistro: () => void }) {
  const { motor: m } = useJogo();
  const itens = m.historico.filter(h => h.quem === "dono" || h.quem === "pet" || h.quem === "recusa").slice(-8).reverse();
  const texto = (h: (typeof itens)[number]) => h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] ?? h.a : h.a;
  return (
    <>
      {itens.length ? <ol className="mod-registro">{itens.map((h, i) => {
        const I = ICONE_QUEM[h.quem as keyof typeof ICONE_QUEM];
        return <li key={i} data-quem={h.quem}><time>{hhmm(h.t)}</time><span className="mod-registro-ic"><I size={18} aria-hidden="true" /></span>
          <span>{h.quem === "dono" ? "você: " : h.quem === "recusa" ? "recusou: " : ""}{texto(h)}</span></li>;
      })}</ol> : <p className="mod-vazio">nada no registro ainda</p>}
      <button type="button" className="hx-btn mod-link" onClick={irRegistro}>Ver tudo no Diário</button>
    </>
  );
}

const TITULO_PAINEL: Record<Painel, string> = { estado: "Estado atual", evolucao: "Evolução", acoes: "Últimas ações", digibrain: "DigiBrain", fala: "Por que ele disse isso" };
const BOTOES_LADO: [Exclude<Painel, "fala">, LucideIcon][] = [["estado", Activity], ["evolucao", TrendingUp], ["acoes", History], ["digibrain", Brain]];

function ConteudoPainel({ id, v, irRegistro, irEvolucao }: { id: Painel; v: VistaFala; irRegistro: () => void; irEvolucao: () => void }) {
  switch (id) {
    case "estado": return <div className="det-estado"><Emocao /><InfoMundo /><Necessidades /><Desejo /><EstadoConfianca /></div>;
    case "evolucao": return <ProximaEvolucao irEvolucao={irEvolucao} />;
    case "acoes": return <UltimasAcoes irRegistro={irRegistro} />;
    /* o DigiBrain e o porque da fala mantem o visual claro de hoje (.dl) dentro do painel escuro; a pele deles fica para o polimento */
    case "digibrain": return <div className="pet-painel__folha dl digibrain"><div className="db-folha-selo"><SeloDigiBrain replay={false} /></div><ConteudoDigiBrain /></div>;
    case "fala": return <div className="pet-painel__folha dl"><DetalheFala v={v} semTitulo /></div>;
  }
}

/* ------------------------------------------------ a tela */
/** o dock ocupa o pe da tela: o habitat (camada de fundo) deixa esse espaco livre para o pet nao ficar coberto */
function useReservaDoHabitat(ref: { current: HTMLElement | null }): void {
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const raiz = document.documentElement.style;
    const medir = () => raiz.setProperty("--hab-baixo", `calc(${Math.ceil(el.getBoundingClientRect().height) + 24}px + var(--casca-barra))`);
    medir();
    const ro = new ResizeObserver(medir); ro.observe(el);
    return () => { ro.disconnect(); raiz.removeProperty("--hab-baixo"); };
  }, [ref]);
}
export function TelaPet({ irRegistro, irEvolucao }: { irRegistro: () => void; irEvolucao: () => void }) {
  const { motor: m, nascendo } = useJogo(), fala = useFala(), [aberto, setAberto] = useState<Painel | null>(null);
  const painel = useRef<HTMLDivElement>(null), gatilho = useRef<HTMLElement | null>(null), dock = useRef<HTMLDivElement>(null);
  useReservaDoHabitat(dock);
  const vivo = nascendo === 0 && !m.morte, temEvo = vivo && !!previsaoEvo(m);
  /* o painel que deixou de fazer sentido (o ovo chocando, o pet que morreu) fecha sozinho */
  const valido = (p: Painel | null): p is Painel => p !== null && (p === "estado" || (nascendo === 0 && (p !== "evolucao" || temEvo)));
  const atual = valido(aberto) ? aberto : null;
  const abrir = (p: Painel) => { gatilho.current = document.activeElement as HTMLElement | null; setAberto(aberto === p ? null : p); };
  const fechar = () => { setAberto(null); const g = gatilho.current; gatilho.current = null; setTimeout(() => { if (g?.isConnected) g.focus(); }, 0); };
  useEffect(() => { if (atual) painel.current?.focus(); }, [atual]);
  const botoesLado = BOTOES_LADO.filter(([id]) => id === "estado" || (id === "digibrain" ? nascendo === 0 : id === "evolucao" ? temEvo : vivo));
  return (
    <section className="pet-tela pet-home dl" aria-label="Tela do pet">
      <div className="pet-balcao">
        {vivo && <BalaoFala v={fala} abrir={() => abrir("fala")} />}
        {m.mundo && vivo && <FaixaRacao />}
      </div>
      <nav className="pet-lado" aria-label="Painéis do pet">
        {botoesLado.map(([id, I]) => (
          <button type="button" key={id} className="hx-btn pet-lado__bt" aria-pressed={atual === id} aria-controls="pet-painel" aria-label={TITULO_PAINEL[id]} title={TITULO_PAINEL[id]}
            onClick={() => abrir(id)}><I size={22} aria-hidden="true" /></button>
        ))}
      </nav>
      {atual && (
        <div className="pet-painel" id="pet-painel" ref={painel} tabIndex={-1} onKeyDown={e => { if (e.key === "Escape") { e.stopPropagation(); fechar(); } }}>
          <PainelHx titulo={TITULO_PAINEL[atual]} onFechar={fechar} rotuloFechar={`Fechar ${TITULO_PAINEL[atual]}`} className="pet-painel__hx">
            <ConteudoPainel id={atual} v={fala} irRegistro={irRegistro} irEvolucao={irEvolucao} />
          </PainelHx>
        </div>
      )}
      <div className="pet-dock" ref={dock}>
        {m.mundo && <AvisoRacao />}
        <Prioridade abrirDetalhes={() => abrir("estado")} />
        {!m.morte && <DockPet />}
      </div>
    </section>
  );
}
