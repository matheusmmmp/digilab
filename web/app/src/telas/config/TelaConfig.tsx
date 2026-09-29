/* Configuracoes (desenhos CfgPrincipal, CfgAparencia, CfgDados, CfgFala, CfgSobre): tela aberta pela engrenagem do
   Diario. So junta o que o app ja tinha (tema, registro e replay, tempo de teste, fala) num lugar; nada aqui muda
   o motor, as regras ou o save, a nao ser pelas mesmas acoes de antes (tempo e ovo novo, via jogo.ts/tempo.ts).
   Opcoes dos desenhos que o app nao tem (tamanho do texto, reduzir movimento, dicas) ficam de fora; o som aparece
   desligado, como proposta. */
import type { ComponentChildren } from "preact";
import { useState } from "preact/hooks";
import { Motor } from "../../../motor/index.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { Peca } from "../../componentes/Imagens.tsx";
import { ICONE } from "../../decoracao.ts";
import { FALA_LLM, ligarFalaLLM, rotuloLLM, useFalaLLM } from "../../fala.ts";
import { escolherModo, useFalaLivre, type ModoFala } from "../../falaLivre.ts";
import { useJogo } from "../../jogo.ts";
import { abrirEscolhaBrasao } from "../../jornada.ts";
import type { ParteConfig } from "../../rotas.ts";
import { useDesktop } from "../../desktop.ts";
import { dicasLigadas, ligarDicas } from "../../dicas.ts";
import { textoSave } from "../../save.ts";
import { NOME_TEMA, escolherTema, useTema, type Tema } from "../../tema.ts";
import { VELOCIDADES, escolherVelocidade, pularUmaHora, useTempo } from "../../tempo.ts";

const TITULO: Record<ParteConfig, string> = { principal: "Configurações", aparencia: "Aparência", dados: "Registro e replay", fala: "Fala do pet", sobre: "Sobre" };
const NOME_MODO: Record<ModoFala, string> = { template: "frases prontas", moldura: "moldura", livre: "livre" };
export const nomeVelocidade = (v: number): string => VELOCIDADES.find(([, x]) => x === v)?.[0] ?? `${v} min/s`;

function Cabecalho({ parte, voltar }: { parte: ParteConfig; voltar: () => void }) {
  return (
    <div class="tela-cab dl-faixa cfg-cab">
      <Deco nome="TopDeco_Earth2_0" class="cab-globo" />
      <button type="button" class="cfg-voltar" aria-label={parte === "principal" ? "Voltar ao Diário" : "Voltar a Configurações"} onClick={voltar}>
        <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M12 4 6 10l6 6" /></svg></button>
      {parte === "principal" && <Deco nome="Common_Icon_Setting" class="cfg-cab-ic" />}
      <h1 class="dl-num" id="tela-titulo">{TITULO[parte]}</h1>
    </div>
  );
}
/** linha da lista: icone (decoracao, com o texto ao lado), titulo, resumo e seta */
function Linha({ ic, titulo, resumo, tag, abrir, atual = false }: { ic: ComponentChildren; titulo: string; resumo: string; tag?: string; abrir: () => void; atual?: boolean }) {
  return (
    <button type="button" class="cfg-linha" aria-current={atual ? "page" : undefined} onClick={abrir}>
      <span class="cfg-ic" aria-hidden="true">{ic}</span>
      <span class="cfg-txt"><b>{titulo}{tag && <span class="dl-tag cfg-tag">{tag}</span>}</b><small>{resumo}</small></span>
      <svg class="cfg-seta" viewBox="0 0 20 20" aria-hidden="true"><path d="M8 4l6 6-6 6" /></svg>
    </button>
  );
}
function Principal({ abrir, atual = null }: { abrir: (p: ParteConfig) => void; atual?: ParteConfig | null }) {
  const { motor: m } = useJogo(), tema = useTema(), fl = useFalaLivre(), { velocidade } = useTempo();
  useFalaLLM();
  return (
    <div class="tela dl cfg">
      <h2 class="cfg-secao">JOGO</h2>
      <Linha ic={<Deco nome={ICONE.pets} />} titulo="Aparência" resumo={`tema ${tema === "sistema" ? "do sistema" : NOME_TEMA[tema].toLowerCase()}`} abrir={() => abrir("aparencia")} atual={atual === "aparencia"} />
      <h2 class="cfg-secao">FALA</h2>
      <Linha ic={<Peca nome="emoji_feliz" escala={2} />} titulo="Fala do pet" resumo={`modo ${NOME_MODO[fl.modo]} · ${rotuloLLM().texto}`} abrir={() => abrir("fala")} atual={atual === "fala"} />
      <h2 class="cfg-secao">DADOS</h2>
      <Linha ic={<Deco nome={ICONE.registro} />} titulo="Registro e replay" resumo={`semente ${m.semente} · ${m.log.length} eventos · exportar`} abrir={() => abrir("dados")} atual={atual === "dados"} />
      <Linha ic={<Deco nome={ICONE.tempo} />} titulo="Tempo" tag="TESTE" resumo={velocidade === 0 ? "pausado" : `velocidade ${nomeVelocidade(velocidade)}`} abrir={() => abrir("dados")} />
      <h2 class="cfg-secao">SOBRE</h2>
      <Linha ic={<Deco nome="Digivice_Circle_01" />} titulo="Sobre o Digilab" resumo="versão, créditos e uso pessoal" abrir={() => abrir("sobre")} atual={atual === "sobre"} />
      <div class="cfg-linha cfg-linha--off" aria-disabled="true">
        <span class="cfg-ic" aria-hidden="true">♪</span>
        <span class="cfg-txt"><b>Som</b><small>o jogo ainda não tem som (proposta; desligado)</small></span>
      </div>
    </div>
  );
}
function Aparencia() {
  const tema = useTema(), opcoes: [Tema, string][] = [["claro", "Claro"], ["escuro", "Escuro"], ["sistema", "Sistema"]], [dicas, setDicas] = useState(dicasLigadas);
  return (
    <div class="tela dl cfg">
      <h2 class="cfg-secao" id="cfg-tema">TEMA</h2>
      <div class="cfg-temas" role="radiogroup" aria-labelledby="cfg-tema">
        {opcoes.map(([t, rot]) => (
          <button type="button" key={t} role="radio" aria-checked={tema === t} class={`cfg-tema cfg-tema--${t}`} onClick={() => escolherTema(t)}>
            <span class="cfg-tema-prev" aria-hidden="true"><i /><i /></span>{rot}
          </button>
        ))}
      </div>
      <p class="dl-apoio">Sistema segue o claro ou escuro do aparelho.</p>
      <label class="cfg-interruptor"><span><b>Mostrar dicas</b><small>o Professor Agumon explica cada coisa nova, uma vez</small></span>
        <input type="checkbox" role="switch" checked={dicas} onChange={e => { ligarDicas((e.target as HTMLInputElement).checked); setDicas(dicasLigadas()); }} /></label>
    </div>
  );
}
function Dados({ irPet }: { irPet: () => void }) {
  const { motor: m } = useJogo(), { velocidade } = useTempo(), [msg, setMsg] = useState<{ txt: string; erro?: boolean } | null>(null), [confirmar, setConfirmar] = useState(false);
  const verificar = () => {
    const t0 = performance.now();
    try {
      const ok = Motor.reproduzir(m.semente, m.log, m.versao).assinatura() === m.assinatura();
      setMsg(ok ? { txt: `Replay idêntico: ${m.log.length} eventos reconstruíram o mesmo pet em ${(performance.now() - t0).toFixed(0)} ms.` }
        : { txt: "O replay divergiu do pet atual. Isso é um bug do porte; copie o registro e mande para análise.", erro: true });
    } catch (err) { setMsg({ txt: "Replay falhou: " + (err instanceof Error ? err.message : String(err)), erro: true }); }
  };
  const copiar = async () => {
    const txt = textoSave(m);
    try { await navigator.clipboard.writeText(txt); setMsg({ txt: "Registro copiado." }); }
    catch { console.log(txt); setMsg({ txt: "Não foi possível copiar automaticamente. O registro está no console do navegador." }); }
  };
  const exportar = () => {
    /* o mesmo conteudo do save num arquivo .json baixado pelo navegador */
    const url = URL.createObjectURL(new Blob([textoSave(m)], { type: "application/json" })), a = document.createElement("a");
    a.href = url; a.download = `digilab-pet-${m.semente}.json`; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setMsg({ txt: "Arquivo do pet exportado." });
  };
  return (
    <div class="tela dl cfg">
      <section class="dl-card cfg-bloco" aria-labelledby="cfg-reg">
        <h2 class="cfg-bloco-tit" id="cfg-reg"><Deco nome={ICONE.registro} class="cfg-bloco-ic" />Registro e replay</h2>
        <p>O estado do pet nunca é salvo: só o registro. A vida é refeita a partir dele.</p>
        <p class="cfg-numeros"><span><b class="dl-lcd">{m.semente}</b> semente</span><span><b class="dl-lcd">{m.log.length}</b> eventos</span></p>
        <div class="dl-linha">
          <button type="button" class="dl-btn" onClick={verificar}>Verificar replay</button>
          <button type="button" class="dl-btn dl-btn--sec" onClick={copiar}>Copiar registro</button>
          <button type="button" class="dl-btn dl-btn--sec" onClick={exportar}>Exportar pet</button>
        </div>
        {msg && <p class={msg.erro ? "erro" : "dl-apoio"} aria-live="polite" style={{ fontWeight: 900, margin: 0 }}>{msg.txt}</p>}
      </section>
      <section class="dl-card cfg-bloco" aria-labelledby="cfg-tempo">
        <h2 class="cfg-bloco-tit" id="cfg-tempo"><Deco nome={ICONE.tempo} class="cfg-bloco-ic" />Tempo <span class="dl-tag cfg-tag">TESTE</span></h2>
        <p>Acelera o relógio do pet. Tudo entra no registro.</p>
        <div class="tempo-pet" role="group" aria-label="Velocidade do tempo">
          {VELOCIDADES.map(([rot, v, dica]) => (
            <button type="button" key={rot} class="dl-btn dl-btn--sec" aria-pressed={velocidade === v} title={dica} onClick={() => escolherVelocidade(v)}>{rot}</button>
          ))}
          <button type="button" class="dl-btn dl-btn--sec" onClick={pularUmaHora}>+1 h</button>
        </div>
      </section>
      <section class="zona-risco" aria-label="Área de risco">
        <div class="dl-linha">
          <button type="button" class="dl-btn dl-btn--sec" onClick={() => setConfirmar(true)}>Novo ovo (apaga este pet)</button>
          {confirmar && <button type="button" class="dl-btn dl-btn--perigo" onClick={() => { setConfirmar(false); abrirEscolhaBrasao(); irPet(); }}>Confirmar: apagar este pet</button>}
        </div>
      </section>
    </div>
  );
}
function Fala() {
  const llm = useFalaLLM(), fl = useFalaLivre(), r = rotuloLLM();
  const modos: [ModoFala, string, string, string?][] = [
    ["template", "Frases prontas", "Sempre as mesmas frases do jogo. Nunca erra, mas repete."],
    ["moldura", "Moldura", "O modelo completa uma moldura com os fatos do pet."],
    ["livre", "Livre", "Sem moldura. O verificador marca o que não tiver base, sem trocar a fala.", "EXPERIMENTO"],
  ];
  return (
    <div class="tela dl cfg">
      <section class="dl-card cfg-bloco">
        <p class="cfg-status"><span class="fala-ponto" data-estado={r.estado} aria-hidden="true" /><b title={r.titulo}>{r.texto}</b></p>
        <p class="dl-apoio" style={{ margin: 0 }}>{fl.status ? `fala livre: ${fl.status.modelo}, local` : fl.statusErro ? "servidor sem a fala livre" : ""}</p>
        <label class="cfg-switch"><span><b>Usar o modelo de linguagem</b><small>Só no Champion em diante. Desligado, o pet fala por frases prontas.</small></span>
          <input type="checkbox" role="switch" checked={FALA_LLM.on} disabled={!llm.ativo} onChange={ev => ligarFalaLLM((ev.target as HTMLInputElement).checked)} /></label>
      </section>
      <h2 class="cfg-secao" id="cfg-modo">COMO ELE MONTA A FALA</h2>
      <div class="cfg-modos" role="radiogroup" aria-labelledby="cfg-modo">
        {modos.map(([k, rot, desc, tag]) => (
          <button type="button" key={k} role="radio" aria-checked={fl.modo === k} class="cfg-modo" onClick={() => escolherModo(k)}>
            <b>{rot}{tag && <span class="dl-tag cfg-tag">{tag}</span>}</b><small>{desc}</small>
          </button>
        ))}
      </div>
      <p class="dl-apoio">Em todos os modos, a fala não decide nada e o que você escreve na conversa não ensina o pet.</p>
    </div>
  );
}
function Sobre() {
  return (
    <div class="tela dl cfg">
      <div class="cfg-sobre-topo">
        <Deco nome="Digivice_Circle_01" class="cfg-sobre-anel gira" />
        <span class="dl-num cfg-sobre-nome">DIGILAB</span>
        <span class="dl-lcd">motor v1 · combate V2.1</span>
      </div>
      <section class="dl-card cfg-bloco"><h2 class="cfg-bloco-tit">Sobre</h2>
        <p>Um pet virtual que aprende com o dono. O estado nunca é salvo, só o registro do que aconteceu; a vida é refeita a partir dele, sempre igual.</p></section>
      <section class="dl-card cfg-bloco"><h2 class="cfg-bloco-tit">Só para uso pessoal</h2>
        <p>Sprites, ícones e fundos do Digimon UP (Bandai), usados só neste computador como protótipo. Não publicar nem distribuir.</p></section>
    </div>
  );
}
export function TelaConfig({ parte, abrir, fechar, irPet }: { parte: ParteConfig; abrir: (p: ParteConfig) => void; fechar: () => void; irPet: () => void }) {
  const desk = useDesktop();
  /* desktop (CfgDesktop): a lista a esquerda e a parte escolhida a direita (na principal, a Aparencia) */
  if (desk) {
    const p = parte === "principal" ? "aparencia" : parte;
    return (
      <section class="painel" aria-label={TITULO[parte]}>
        <div class="tela dl desk cfg-desk">
          <div class="desk-col cfg-desk-lista"><Principal abrir={abrir} atual={p} /></div>
          <div class="desk-col cfg-desk-parte">
            <h2 class="cfg-desk-tit">{TITULO[p]}</h2>
            {p === "aparencia" ? <Aparencia /> : p === "dados" ? <Dados irPet={irPet} /> : p === "fala" ? <Fala /> : <Sobre />}
          </div>
        </div>
      </section>
    );
  }
  return (
    <section class="painel" aria-labelledby="tela-titulo">
      <Cabecalho parte={parte} voltar={parte === "principal" ? fechar : () => abrir("principal")} />
      {parte === "principal" ? <Principal abrir={abrir} /> : parte === "aparencia" ? <Aparencia /> : parte === "dados" ? <Dados irPet={irPet} />
        : parte === "fala" ? <Fala /> : <Sobre />}
    </section>
  );
}
