/* Tela Pet (desenho UpPet; porte da tela do HTML): cabecalho com retrato, palco, fala com causa, faixa da fala,
   necessidades, chamado do In-Training, desejo, acoes do dono, atalho do tempo (teste; os controles ficam em
   Configuracoes) e a conversa da fala livre.
   Tudo derivado do motor na hora de desenhar; so mudarMotor() altera o pet. */
import type { ComponentChildren } from "preact";
import { useEffect, useState } from "preact/hooks";
import {
  ACAO_CHAMADO, ALVOS_DESEJO, CAT, DO_ESP, FATORES_TXT, NOME_CHAMADO, NOME_EST, NOME_PET, OVO, TICK_INICIAL, TPD,
  chaveSprite, nomeEstagio, nomeForma, observacao, type AcaoDono, type Chamado, type MotivoVida, type Motor,
} from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { Seg, blocos } from "../../componentes/Barras.tsx";
import { Grade, Peca } from "../../componentes/Imagens.tsx";
import {
  FALA_LLM, detalheMotivo, falaDe, falaLLM, ligarFalaLLM, motivoParaApi, refsDoMotivo, rotuloLLM, useFalaLLM,
} from "../../fala.ts";
import {
  FL, conversaGravada, detalheFalaLivre, enviarConversa, escolherModo, gatilhoFalaLivre, iconeVerif, tituloFalaLivre, useFalaLivre, type ModoFala,
} from "../../falaLivre.ts";
import { AMPULHETA } from "../../grades.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { BRASAO, ICONE } from "../../decoracao.ts";
import type { ParteConfig } from "../../rotas.ts";
import { ajustarVelocidadeChamado, useTempo } from "../../tempo.ts";
import { nomeVelocidade } from "../config/TelaConfig.tsx";
import { MeusPets } from "./MeusPets.tsx";
import { PalcoPet, mostrarFlash } from "./PalcoPet.tsx";

export const hhmm = (t: number): string => { const m = t % TPD; return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"); };
export const diaDe = (t: number): number => Math.floor((t - TICK_INICIAL) / TPD) + 1;

/* ------------------------------------------------ cabecalho e retrato */
function Retrato({ m, ovo }: { m: Motor; ovo: boolean }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return null;
  const { url, w, h } = imagemAtlas(a, ovo ? OVO[m.especie] : chaveSprite(m.forma));
  return <img class="dl-pix" src={url} width={w} height={h} alt="" />;
}
function CabecalhoPet({ abrirMeusPets }: { abrirMeusPets: () => void }) {
  const { motor: m, nascendo } = useJogo(), ovo = nascendo > 0, e = m.e;
  return (
    <div class="pet-cab dl-faixa">
      <Deco nome="TopDeco_Earth2_0" class="cab-globo" />
      <button type="button" class="pet-retrato" aria-haspopup="dialog" aria-label="Meus pets" onClick={abrirMeusPets}><Retrato m={m} ovo={ovo} /></button>
      <span class="pet-cab-nome">
        <Deco nome={BRASAO[m.especie].peca} class="pet-brasao" alt={`brasão ${DO_ESP[m.especie]}`} />
        <span class="dl-placa">{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</span>
        <span class="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>
      </span>
      <span class="dl-lcd pet-relogio">DIA {diaDe(e.tick)} · {hhmm(e.tick)}</span>
    </div>
  );
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
  const partes: ComponentChildren[] = [];
  let ult = 0, i = 0;
  for (const m of txt.matchAll(/\[:(.+?):\]/g)) {
    partes.push(txt.slice(ult, m.index));
    const marc = m[1], f = Object.keys(FATORES_TXT).find(k => FATORES_TXT[k].marcador === marc);
    partes.push(f && EMOTE_FATOR[f] ? <Peca key={i++} nome={EMOTE_FATOR[f]} escala={2} alt={marc} />
      : f && FATOR_DEMORA.has(f) ? <Grade key={i++} grade={AMPULHETA} escala={3} cores={CORES_AMPULHETA} alt={marc} />
      : <span key={i++} class="fala-marca">{marc}</span>);
    ult = (m.index ?? 0) + m[0].length;
  }
  partes.push(txt.slice(ult));
  return <>{partes}</>;
}
function Causa({ mot, refs }: { mot: MotivoVida; refs: number[] }) {
  if (mot.exploracao || !mot.fatores.length) return <span class="dl-causa dl-causa--sem">? sem motivo registrado</span>;
  const mem = mot.fatores.filter(f => CAUSA_MEMORIA[f]).slice(0, 2);
  return <>{mem.map(f => {
    const c = CAUSA_MEMORIA[f];
    return <span key={f} class="dl-causa dl-causa--registro dl-malha">{EMOTE_CAUSA[c] && <Peca nome={EMOTE_CAUSA[c]} />}{c}{refs.length ? " · evento #" + refs.join(", #") : ""}</span>;
  })}</>;
}
function Fala() {
  const { motor: m, revisao } = useJogo(), atlas = useAtlas(), llm = useFalaLLM(), fl = useFalaLivre();
  const [aberto, setAberto] = useState(false);
  const [livre, setLivre] = useState(false);
  /* a fala livre reage ao pet (gatilho) fora do desenho: dispara chamadas ao servidor */
  useEffect(() => { setLivre(gatilhoFalaLivre(m)); }, [revisao, fl.modo]);
  const mot = m.motivo, est = m.estagioAtual;
  let balao: ComponentChildren = "…", classe = "dl-balao", detalhe = "", titulo = "Toque para ver o porquê", causa: ComponentChildren = null;
  if (livre && fl.modo === "livre" && fl.ultimo) {
    balao = "✧ " + fl.ultimo.fala + iconeVerif(fl.ultimo.verificacao);
    detalhe = detalheFalaLivre(fl.ultimo); titulo = tituloFalaLivre(fl.ultimo);
  } else if (mot) {
    const refs = refsDoMotivo(m, mot), resp = falaLLM(motivoParaApi(mot, refs), est, mot.humor), usarLLM = !!resp && resp.fonte === "llm";
    const fria = m.falaFria || m.sombria, pronta = llm.on && llm.ativo && ["adolescente", "adulto"].includes(est) && !usarLLM;
    classe = "dl-balao" + (fria ? " dl-balao--sombria" : "") + (est === "bebe" ? " dl-balao--emote" : "");
    balao = <>{usarLLM ? "✦ " + resp!.texto : <TextoFala txt={falaDe(m, mot)} est={est} atlasOk={atlas.tipo === "ok"} />}{pronta && <span class="dl-balao-tag">frase pronta</span>}</>;
    causa = <Causa mot={mot} refs={refs} />;
    detalhe = detalheMotivo(mot, est) + (llm.on && llm.ativo && ["adolescente", "adulto"].includes(est)
      ? ` · fonte: ${usarLLM ? "LLM (" + resp!.detalhe + ")" : resp ? "template (" + resp.detalhe + ")" : "template (aguardando LLM)"}` : " · fonte: template");
  }
  const r = rotuloLLM();
  return (
    <>
      <div class="fala-area">
        <button type="button" class={classe} aria-expanded={aberto} title={titulo} onClick={() => setAberto(!aberto)}>{balao}</button>
        {causa && <div class="causa-area">{causa}</div>}
        {aberto && <div class="fala-det dl-apoio">{detalhe}</div>}
      </div>
      <div class="fala-status dl-apoio">
        <span class="fala-ponto" data-estado={r.estado} aria-hidden="true" /><span title={r.titulo}>{r.texto}</span>
        <label class="fala-troca"><input type="checkbox" role="switch" checked={FALA_LLM.on} disabled={!llm.ativo}
          onChange={ev => ligarFalaLLM((ev.target as HTMLInputElement).checked)} /> fala por LLM</label>
      </div>
    </>
  );
}

/* ------------------------------------------------ necessidades, chamado e desejo */
const NEC_PET: [("fome" | "energia" | "higiene" | "humor"), string, string | null][] = [["fome", "Comida", "emoji_carne"], ["energia", "Energia", null], ["higiene", "Higiene", null], ["humor", "Humor", "emoji_feliz"]];
const EMOTE_CHAMADO: Record<Chamado, string | null> = { fome: "emoji_carne", carinho: "emoji_coracao", higiene: null };
const EMOTE_DESEJO: Record<string, string> = { comer: "emoji_carne", brincar: "emoji_nota", chamar_atencao: "emoji_exclam", explorar: "emoji_estrela" };

function Necessidades() {
  const { motor: m } = useJogo(), e = m.e, saude = Math.round(e.saude * 100);
  return (
    <div class="necessidades4">
      {NEC_PET.map(([k, rot, em]) => (
        <div class="nec" key={k}>
          <span class="nec-rot">{em && <Peca nome={em} />}{rot}</span>
          <Seg n={blocos(e[k], 5)} m={5} cls={e[k] < .5 ? "dl-seg--necessidade" : ""} />
        </div>
      ))}
      <div class="dl-vida nec-saude">
        <div class="dl-vida-topo"><span>Saúde</span><span class="dl-lcd">{saude}%{e.saude < .3 ? " · crítica" : ""}</span></div>
        <div class="dl-vida-trilho" role="img" aria-label={`saúde ${saude} de 100`}>
          <i style={{ width: `${e.saude * 100}%`, ...(e.saude < .3 ? { background: "var(--dl-need)" } : {}) }} />
        </div>
      </div>
    </div>
  );
}
function Chamados({ agir }: { agir: (a: AcaoDono) => void }) {
  const { motor: m } = useJogo(), ab = m.chamadosAbertos(), tick = m.e.tick;
  if (!ab.length && m.acao === "chamar_atencao") return (
    <div class="dl-card chamado">
      <span class="chamado-ic"><Peca nome="emoji_exclam" escala={2} reserva="!" /></span>
      <span class="chamado-txt"><b>Chamando você</b><span class="dl-apoio">um carinho atende o pedido</span></span>
      <button type="button" class="dl-btn" onClick={() => agir("acariciar")}>Atender</button>
    </div>
  );
  /* chamado aberto (so o In-Training chama): barra da janela, nunca cronometro */
  return <>{ab.map(c => {
    const resta = Math.max(0, CAT.janelaChamado - (tick - m.chamados.abertos[c]!));
    return (
      <div class="dl-card chamado" key={c}>
        <span class="chamado-ic">{EMOTE_CHAMADO[c] ? <Peca nome={EMOTE_CHAMADO[c]!} escala={2} reserva="!" /> : "!"}</span>
        <span class="chamado-txt"><b>Chamado: {NOME_CHAMADO[c]}</b><Seg n={blocos(resta / CAT.janelaChamado, 5)} m={5} cls="dl-seg--acao" /><span class="dl-apoio">janela aberta</span></span>
        <button type="button" class="dl-btn" onClick={() => agir(ACAO_CHAMADO[c][0])}>Atender</button>
      </div>
    );
  })}</>;
}
/** desejo: necessidade (rosa, vem do corpo) ou vontade aprendida (malha); so o que o motor calculou */
function Desejo() {
  const { motor: m } = useJogo(), d = m.desejoAtual(observacao(m.e), m.e.tick);
  if (!d) return null;
  const em = EMOTE_DESEJO[d.alvo];
  if (d.tipo === "necessidade") return (
    <div class="dl-desejo dl-desejo--necessidade"><span class="dl-desejo-cab">NECESSIDADE</span>
      <span class="dl-desejo-corpo">{em && <Peca nome={em} escala={2} />}<span><strong>{ALVOS_DESEJO[d.alvo][1]}</strong><span>vem do corpo</span></span></span></div>
  );
  return (
    <div class="dl-desejo dl-desejo--aprendida dl-malha"><span class="dl-desejo-cab">VONTADE APRENDIDA</span>
      <span class="dl-desejo-corpo"><span class="dl-desejo-icone">{em ? <Peca nome={em} escala={2} reserva="★" /> : "★"}</span>
        <span><strong>{ALVOS_DESEJO[d.alvo][1]}</strong><span>aprendida com você</span></span></span></div>
  );
}

/* ------------------------------------------------ acoes do dono e tempo */
const ACOES: [AcaoDono, string, string][] = [["alimentar", "Alimentar", "sec"], ["limpar", "Limpar", "sec"], ["brincar", "Brincar", "sec"],
  ["acariciar", "Carinho", "sec"], ["elogiar", "Elogiar", "destaque"], ["repreender", "Repreender", "sec"]];
const ICONE_DONO: Record<AcaoDono, string> = { alimentar: "carne", limpar: "brilho", brincar: "nota", acariciar: "coracao", elogiar: "coracao", repreender: "gota" };

/** o tempo de teste mora em Configuracoes > Registro e replay; aqui so a velocidade atual e o atalho */
function Tempo({ abrirConfig }: { abrirConfig: (p: ParteConfig) => void }) {
  const { velocidade } = useTempo();
  return (
    <button type="button" class="tempo-atalho" onClick={() => abrirConfig("dados")}>
      <Deco nome={ICONE.tempo} class="tempo-atalho-ic" />
      <span><span><b>Tempo (teste)</b> · {velocidade === 0 ? "pausado" : nomeVelocidade(velocidade)}</span><small>mudar em Configurações › Registro e replay</small></span>
    </button>
  );
}

/* ------------------------------------------------ conversa da fala livre (experimental) */
function Conversa() {
  const fl = useFalaLivre(), [msg, setMsg] = useState("");
  const regs = conversaGravada();
  const enviar = () => { enviarConversa(msg); setMsg(""); };
  return (
    <section class="dl-card fl-bloco" aria-labelledby="fl-titulo">
      <h2 class="dl-titulo-card" id="fl-titulo">Conversa <span class="fl-exp">experimental</span></h2>
      <div class="dl-linha">
        <label for="fl-modo">Modo da fala</label>
        <select id="fl-modo" value={fl.modo} onChange={ev => escolherModo((ev.target as HTMLSelectElement).value as ModoFala)}>
          <option value="template">template</option><option value="moldura">moldura (LLM só abre e fecha a frase)</option>
          <option value="livre">livre (LLM local, experimento)</option>
        </select>
        <span class="dl-apoio">{fl.status ? `(${fl.status.modelo}, local)` : fl.statusErro ? "(servidor sem a fala livre)" : ""}</span>
      </div>
      <div class="fl-conv" aria-live="polite">
        {regs.length ? regs.map((r, i) => <div key={i}><div class="fl-j">você: {r.fala_jogador}</div><div class="fl-p">pet: {r.fala}{iconeVerif(r.verificacao)}</div></div>)
          : <div class="dl-apoio">Escreva algo para o seu pet.</div>}
      </div>
      <div class="dl-linha">
        <input type="text" class="fl-msg" maxLength={300} placeholder="Fale com o pet (modo livre)" aria-label="Mensagem para o pet" value={msg}
          disabled={fl.modo !== "livre"} onInput={ev => setMsg((ev.target as HTMLInputElement).value)} onKeyDown={ev => { if (ev.key === "Enter") enviar(); }} />
        <button type="button" class="dl-btn" disabled={fl.modo !== "livre"} onClick={enviar}>Falar</button>
        {fl.pendente && <span class="dl-apoio">pensando…</span>}
      </div>
      <p class="dl-apoio" style={{ margin: 0 }}>O que você escreve aqui não ensina o pet nem entra no registro dele. ⚠ = o verificador achou uma afirmação sem fato por trás.</p>
    </section>
  );
}

/* ------------------------------------------------ a tela */
export function TelaPet({ irRegistro, irTreinar, abrirConfig }: { irRegistro: () => void; irTreinar: () => void; abrirConfig: (p: ParteConfig) => void }) {
  const { motor: m, nascendo } = useJogo(), { freado } = useTempo(), [meusPets, setMeusPets] = useState(false);
  const agir = (a: AcaoDono) => {
    if (nascendo > 0) return;
    mudarMotor(mm => mm.observar(a));
    mostrarFlash(ICONE_DONO[a]);
    ajustarVelocidadeChamado();                  /* atendeu o chamado: volta a velocidade de antes */
  };
  return (
    <section class="pet-tela dl" aria-label="Tela do pet">
      <CabecalhoPet abrirMeusPets={() => setMeusPets(true)} />
      <div class="dl-card dl-card--palco dl-hexcard palco-pet">
        <PalcoPet />
        <div class="pet-status dl-lcd">{NOME_PET[m.acao]}{freado ? " · tempo em 1x até atender" : ""}</div>
        <Fala />
      </div>
      <Necessidades />
      <Chamados agir={agir} />
      <div class="dl-par"><Desejo /></div>
      <div class="acoes-pet" role="group" aria-label="Ações do dono">
        {ACOES.map(([a, rot, tipo]) => <button type="button" key={a} class={`dl-btn dl-btn--${tipo}`} onClick={() => agir(a)}>{a === "alimentar" && <Deco nome={ICONE.alimentar} class="acao-ic" />}{rot}</button>)}
      </div>
      <button type="button" class="treinar-atalho" onClick={irTreinar}>
        <Deco nome="Explore_Icon_Training" class="treinar-atalho-tile" />
        <span><span class="treinar-atalho-tit"><Deco nome={ICONE.treinar} class="acao-ic" />Treinar</span><small>sessões de treino em Crescer</small></span>
      </button>
      <Tempo abrirConfig={abrirConfig} />
      <Conversa />
      {meusPets && <MeusPets fechar={() => setMeusPets(false)} irRegistro={irRegistro} />}
    </section>
  );
}
