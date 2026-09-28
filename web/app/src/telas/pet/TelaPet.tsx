/* Tela Pet (desenho UpPet; porte da tela do HTML): cabecalho com retrato, palco, fala com causa, faixa da fala,
   necessidades, chamado do In-Training, desejo, acoes do dono, tempo (teste) e a conversa da fala livre.
   Tudo derivado do motor na hora de desenhar; so mudarMotor() altera o pet. */
import type { ComponentChildren } from "preact";
import { useEffect, useState } from "preact/hooks";
import {
  ACAO_CHAMADO, ALVOS_DESEJO, CAT, DO_ESP, NOME_ESP, EMOCAO_TXT, FATORES_TXT, NOME_CHAMADO, NOME_EST, NOME_PET, OVO, TICK_INICIAL, TPD,
  chaveSprite, nomeEstagio, nomeForma, observacao, type AcaoDono, type Chamado, type MotivoVida, type Motor,
} from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { BRASAO_DECO, Deco } from "../../decoracao.tsx";
import { Seg, blocos } from "../../componentes/Barras.tsx";
import { Grade, Peca } from "../../componentes/Imagens.tsx";
import {
  detalheMotivo, falaDe, falaLLM, motivoParaApi, refsDoMotivo, rotuloLLM, useFalaLLM,
} from "../../fala.ts";
import {
  detalheFalaLivre, gatilhoFalaLivre, iconeVerif, tituloFalaLivre, useFalaLivre,
} from "../../falaLivre.ts";
import { AMPULHETA } from "../../grades.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { ajustarVelocidadeChamado, useTempo } from "../../tempo.ts";
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
  const { motor: m, nascendo, erroSave } = useJogo(), ovo = nascendo > 0, e = m.e;
  return (
    <header class="pet-cab">
      <Deco nome="TopDeco_Earth2_0" w={170} h={170} cls="pet-cab-globo" />
      <button type="button" class="pet-retrato" aria-haspopup="dialog" aria-label="Meus pets: trocar parceiro" onClick={abrirMeusPets}><Retrato m={m} ovo={ovo} /></button>
      <span class="pet-cab-nome">
        <span class="pet-cab-placa"><span class="dl-placa">{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</span>
          <Deco nome={BRASAO_DECO[m.especie]} w={38} h={25} alt={`brasão ${NOME_ESP[m.especie]}`} /></span>
        <span class="pet-cab-sub"><span class="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>{NOME_ESP[m.especie]} · dia {diaDe(e.tick)}</span>
      </span>
      <span class="pet-relogio">
        <span class="dl-num pet-hora" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}`}>{hhmm(e.tick)}</span>
        <span class={`pet-salvo${erroSave ? " erro" : ""}`}><i aria-hidden="true" />{erroSave ? "não salva" : "salvo"}</span>
      </span>
    </header>
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
interface VistaFala { classe: string; balao: ComponentChildren; texto: string; titulo: string; causa: ComponentChildren; detalhe: string }
/** a fala de agora (texto da tabela de expressao, LLM na moldura ou fala livre); a fala livre reage ao pet (gatilho)
    fora do desenho, porque dispara chamadas ao servidor */
function useFala(): VistaFala {
  const { motor: m, revisao } = useJogo(), atlas = useAtlas(), llm = useFalaLLM(), fl = useFalaLivre();
  const [livre, setLivre] = useState(false);
  useEffect(() => { setLivre(gatilhoFalaLivre(m)); }, [revisao, fl.modo]);
  const mot = m.motivo, est = m.estagioAtual;
  const v: VistaFala = { classe: "dl-balao", balao: "…", texto: "", titulo: "Toque para ver o porquê", causa: null, detalhe: "" };
  if (livre && fl.modo === "livre" && fl.ultimo) {
    v.balao = v.texto = "✧ " + fl.ultimo.fala + iconeVerif(fl.ultimo.verificacao);
    v.detalhe = detalheFalaLivre(fl.ultimo); v.titulo = tituloFalaLivre(fl.ultimo);
  } else if (mot) {
    const refs = refsDoMotivo(m, mot), resp = falaLLM(motivoParaApi(mot, refs), est, mot.humor), usarLLM = !!resp && resp.fonte === "llm";
    const fria = m.falaFria || m.sombria, pronta = llm.on && llm.ativo && ["adolescente", "adulto"].includes(est) && !usarLLM;
    v.classe = "dl-balao" + (fria ? " dl-balao--sombria" : "") + (est === "bebe" ? " dl-balao--emote" : "");
    v.balao = <>{usarLLM ? "✦ " + resp!.texto : <TextoFala txt={falaDe(m, mot)} est={est} atlasOk={atlas.tipo === "ok"} />}{pronta && <span class="dl-balao-tag">frase pronta</span>}</>;
    v.texto = usarLLM ? "✦ " + resp!.texto : est === "adolescente" || est === "adulto" ? falaDe(m, mot) : "";
    v.causa = <Causa mot={mot} refs={refs} />;
    v.detalhe = detalheMotivo(mot, est) + (llm.on && llm.ativo && ["adolescente", "adulto"].includes(est)
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
    <span class="balao-palco balao-causa" role="img" aria-label={`causa: ${txt}`} title={txt}>
      {ic.length ? ic.flatMap((x, i) => [i > 0 ? <b key={"m" + i}>+</b> : null, <span key={"p" + i} class="causa-ic">{x === "tempo" ? <Peca nome="icone_tempo" /> : <Peca nome={"emoji_" + x} escala={2} />}</span>])
        : <b class="balao-q">?</b>}
    </span>
  );
}
/** abaixo do palco (PetTela): a fala num balao-botao (toque = o porque) e a faixa da fonte da fala; aberto, o que ele
    faz, a causa registrada e o detalhe */
const MODO_CURTO: Record<string, string> = { template: "frases prontas", moldura: "moldura", livre: "fala livre" };
function LinhaFala({ v, aberto, alternar }: { v: VistaFala; aberto: boolean; alternar: () => void }) {
  const { motor: m } = useJogo(), { freado } = useTempo(), r = rotuloLLM(), fl = useFalaLivre();
  return (
    <div class="pet-fala">
      <div class="pet-fala-topo">
        <button type="button" class={v.classe + " fala-botao"} aria-expanded={aberto} aria-controls="fala-det" title={v.titulo} onClick={alternar}>
          <span class="balao-txt">{v.balao}</span><small>toque para ver o porquê</small></button>
        <span class="fala-status" title={`${r.texto} · ${r.titulo}`}><span class="fala-ponto" data-estado={fl.modo === "template" ? "off" : r.estado} aria-hidden="true" />{MODO_CURTO[fl.modo]}</span>
      </div>
      {aberto && <div class="fala-det" id="fala-det">
        <span class="pet-status dl-lcd">{NOME_PET[m.acao]}{freado ? " · tempo em 1x até atender" : ""}</span>{v.causa}
        <span class="dl-apoio">{v.texto && <>“{v.texto}” · </>}{v.detalhe}</span></div>}
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
  return <span class="palco-emocao">{EMOTE_EMOCAO[ult.nome] && <Peca nome={EMOTE_EMOCAO[ult.nome]} />}{EMOCAO_TXT[ult.nome][0]}</span>;
}

/* ------------------------------------------------ necessidades, chamado e desejo */
const NEC_PET: [("fome" | "energia" | "higiene" | "humor"), string][] = [["fome", "comida"], ["energia", "energia"], ["higiene", "higiene"], ["humor", "humor"]];
const EMOTE_CHAMADO: Record<Chamado, string | null> = { fome: "emoji_carne", carinho: "emoji_coracao", higiene: null };
const EMOTE_DESEJO: Record<string, string> = { comer: "emoji_carne", brincar: "emoji_nota", chamar_atencao: "emoji_exclam", explorar: "emoji_estrela" };

function Necessidades() {
  const { motor: m } = useJogo(), e = m.e, saude = Math.round(e.saude * 100);
  return (
    <div class="necessidades4">
      {NEC_PET.map(([k, rot]) => (
        <div class="nec" key={k}>
          <span class="nec-rot">{rot}</span>
          <Seg n={blocos(e[k], 5)} m={5} cls={e[k] < .5 ? "dl-seg--necessidade" : "dl-seg--acao"} />
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
        <span class="chamado-ic">{c === "fome" ? <Deco nome="Growth_Guide_Icon_06" w={36} h={34} reserva={<Peca nome="emoji_carne" escala={2} />} />
          : EMOTE_CHAMADO[c] ? <Peca nome={EMOTE_CHAMADO[c]!} escala={2} reserva="!" /> : "!"}</span>
        <span class="chamado-txt"><span class="chamado-tit"><b>Chamado: {NOME_CHAMADO[c]}</b><span class="dl-apoio">janela aberta</span></span><Seg n={blocos(resta / CAT.janelaChamado, 10)} m={10} /></span>
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

/* icone de cada acao do dono (PetTela): prato do guia, gota, nota, coracao, joinha e exclamacao */
const GOTA = <svg class="ic-gota" viewBox="0 0 8 8" width="24" height="24" aria-hidden="true"><path fill="#2C73E0" d="M3 0h2v2h1v1h1v3h-1v1h-4v-1h-1v-3h1v-1h1z" /><path fill="#BFE3FF" d="M2 3h1v2h-1z" /></svg>;
function IconeAcao({ a }: { a: AcaoDono }) {
  if (a === "alimentar") return <Deco nome="Growth_Guide_Icon_06" w={24} h={24} cls="ic-acao" reserva={<Peca nome="emoji_carne" escala={2} />} />;
  if (a === "limpar") return GOTA;
  const em = { brincar: "emoji_nota", acariciar: "emoji_coracao", elogiar: "emoji_joinha", repreender: "emoji_exclam" }[a];
  return em ? <Peca nome={em} escala={2} /> : null;
}

/* ------------------------------------------------ a tela */
export function TelaPet({ irRegistro }: { irRegistro: () => void }) {
  const { motor: m, nascendo } = useJogo(), [meusPets, setMeusPets] = useState(false);
  const agir = (a: AcaoDono) => {
    if (nascendo > 0) return;
    mudarMotor(mm => mm.observar(a));
    mostrarFlash(ICONE_DONO[a]);
    ajustarVelocidadeChamado();                  /* atendeu o chamado: volta a velocidade de antes */
  };
  const fala = useFala(), [aberto, setAberto] = useState(false);
  return (
    <section class="pet-tela dl" aria-label="Tela do pet">
      <div class="pet-listra dl-faixa" aria-hidden="true" />
      <CabecalhoPet abrirMeusPets={() => setMeusPets(true)} />
      <div class="pet-corpo">
        <div class="pet-principal">
          <section class="palco-card" aria-label="Palco do pet">
            <div class="palco-cena dl-hexcard">
              <div class="palco-tit">Meu parceiro</div>
              <Emocao />
              <PalcoPet />
              <BalaoCausa />
              <span class="dl-placa palco-nome">{nascendo > 0 ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</span>
            </div>
          </section>
          <LinhaFala v={fala} aberto={aberto} alternar={() => setAberto(!aberto)} />
        </div>
        <aside class="pet-lado">
          <Necessidades />
          <Chamados agir={agir} />
          <div class="dl-par"><Desejo /></div>
          <div class="acoes-pet" role="group" aria-label="Cuidar e ensinar">
            {ACOES.map(([a, rot, tipo]) => <button type="button" key={a} class={`dl-btn dl-btn--${tipo}`} onClick={() => agir(a)}><IconeAcao a={a} />{rot}</button>)}
          </div>
        </aside>
      </div>
      {meusPets && <MeusPets fechar={() => setMeusPets(false)} irRegistro={irRegistro} />}
    </section>
  );
}
