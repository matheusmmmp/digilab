/* Ajustes na pele XCOM (layout habitat, M5; antes CfgPrincipal, CfgAparencia, CfgDados, CfgFala, CfgSobre), dentro do PainelTela
   (o titulo "Ajustes" e o "x" sao do painel). Uma coluna so, de ate 760 px, no desktop e no celular: o menu (principal) e, ao
   escolher uma parte, ela no lugar do menu, com o botao quadrado de voltar. So junta o que o app ja tinha (tema, registro e
   replay, tempo de teste, fala, som); nada aqui muda o motor, as regras ou o save, a nao ser pelas mesmas acoes de antes
   (tempo e ovo novo, via jogo.ts/tempo.ts). Opcoes das pranchas que o app nao tem ficam de fora. Rotas #/config/<parte> iguais. */
import type { ReactNode } from "react";
import { useState } from "react";
import "../../estilo/menus_config.css";
import { Motor } from "../../../motor/index.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { BotaoHx, ChipHx, LinhaHx } from "../../componentes/hx/index.ts";
import { Peca } from "../../componentes/Imagens.tsx";
import { ICONE } from "../../decoracao.ts";
import { FALA_LLM, ligarFalaLLM, rotuloLLM, useFalaLLM } from "../../fala.ts";
import { escolherModo, useFalaLivre, type ModoFala } from "../../falaLivre.ts";
import { useJogo } from "../../jogo.ts";
import { abrirEscolhaBrasao } from "../../jornada.ts";
import type { ParteConfig } from "../../rotas.ts";
import { AvisoSom } from "../../componentes/AvisoSom.tsx";
import { SOM, useSom } from "../../som.ts";
import { dicasLigadas, ligarDicas } from "../../dicas.ts";
import { textoSave } from "../../save.ts";
import { usePele } from "../../pele.ts";
import { escolherTema, useTema, type Tema } from "../../tema.ts";
import { EscolhaPele, resumoAparencia } from "./EscolhaPele.tsx";
import { VELOCIDADES, escolherVelocidade, pularUmaHora, useTempo } from "../../tempo.ts";

const TITULO: Record<ParteConfig, string> = { principal: "Ajustes", aparencia: "Aparência", dados: "Registro e replay", fala: "Fala do pet", sobre: "Sobre" };
const NOME_MODO: Record<ModoFala, string> = { template: "frases prontas", moldura: "moldura", livre: "livre" };
export const nomeVelocidade = (v: number): string => VELOCIDADES.find(([, x]) => x === v)?.[0] ?? `${v} min/s`;

/** linha do menu: icone (decoracao), titulo, resumo e seta */
function Linha({ ic, titulo, resumo, tag, abrir }: { ic: ReactNode; titulo: string; resumo: string; tag?: string; abrir: () => void }) {
  return (
    <LinhaHx onClick={abrir} secundario={<span aria-hidden="true">›</span>}>
      <span className="mc-menu__ic" aria-hidden="true">{ic}</span>
      <span className="mc-menu__txt"><b>{titulo}{tag && <ChipHx tom="alerta">{tag}</ChipHx>}</b><small>{resumo}</small></span>
    </LinhaHx>
  );
}
function Principal({ abrir }: { abrir: (p: ParteConfig) => void }) {
  const { motor: m } = useJogo(), tema = useTema(), pele = usePele(), fl = useFalaLivre(), { velocidade } = useTempo();
  useFalaLLM();
  return (
    <>
      <h3 className="mc-sec">Jogo</h3>
      <div className="mc-menu"><Linha ic={<Deco nome={ICONE.pets} />} titulo="Aparência" resumo={resumoAparencia(pele, tema)} abrir={() => abrir("aparencia")} /></div>
      <h3 className="mc-sec">Fala</h3>
      <div className="mc-menu"><Linha ic={<Peca nome="emoji_feliz" escala={2} />} titulo="Fala do pet" resumo={`modo ${NOME_MODO[fl.modo]} · ${rotuloLLM().texto}`} abrir={() => abrir("fala")} /></div>
      <h3 className="mc-sec">Dados</h3>
      <div className="mc-menu">
        <Linha ic={<Deco nome={ICONE.registro} />} titulo="Registro e replay" resumo={`semente ${m.semente} · ${m.log.length} eventos · exportar`} abrir={() => abrir("dados")} />
        <Linha ic={<Deco nome={ICONE.tempo} />} titulo="Tempo" tag="TESTE" resumo={velocidade === 0 ? "pausado" : `velocidade ${nomeVelocidade(velocidade)}`} abrir={() => abrir("dados")} />
      </div>
      <h3 className="mc-sec">Sobre</h3>
      <div className="mc-menu"><Linha ic={<Deco nome="Digivice_Circle_01" />} titulo="Sobre o Digilab" resumo="versão, créditos e procedência" abrir={() => abrir("sobre")} /></div>
      <h3 className="mc-sec">Som</h3>
      <Som />
    </>
  );
}
/** liga/desliga e volume do som (src/som.ts); ficam no localStorage do app, nao no save. Ligar e o gesto que o navegador pede */
function Som() {
  const som = useSom();
  return (
    <section className="mc-bloco" aria-label="Som">
      <label className="mc-interruptor"><span><b>Som do jogo</b><small>golpes e impactos na luta e o efeito da evolução; desligado, nada é baixado</small></span>
        <input type="checkbox" role="switch" checked={som.ligado} onChange={e => SOM.ligar((e.target as HTMLInputElement).checked)} /></label>
      <label className="mc-interruptor"><span><b>Volume</b><small>{Math.round(som.volume * 100)}%</small></span>
        <input type="range" min={0} max={1} step={0.05} value={som.volume} aria-label="Volume do som" disabled={!som.ligado}
          onChange={e => SOM.volume(Number((e.target as HTMLInputElement).value))} /></label>
      <AvisoSom />
    </section>
  );
}
function Aparencia() {
  const tema = useTema(), opcoes: [Tema, string][] = [["claro", "Claro"], ["escuro", "Escuro"], ["sistema", "Sistema"]], [dicas, setDicas] = useState(dicasLigadas);
  return (
    <>
      <EscolhaPele />
      <h3 className="mc-sec" id="cfg-tema">Tema do habitat</h3>
      <div className="mc-opcoes mc-opcoes--3" role="radiogroup" aria-labelledby="cfg-tema">
        {opcoes.map(([t, rot]) => (
          <button type="button" key={t} role="radio" aria-checked={tema === t} className={`mc-opcao mc-opcao--tema mc-opcao--${t}`} onClick={() => escolherTema(t)}>
            <span className="mc-tema-prev" aria-hidden="true"><i /><i /></span><b>{rot}</b>
          </button>
        ))}
      </div>
      <p className="mc-apoio">Sistema segue o claro ou escuro do aparelho. Os menus são sempre escuros; o tema vale para o habitat, o balão, o retrato e o relógio.</p>
      <label className="mc-interruptor"><span><b>Mostrar dicas</b><small>o Professor Agumon explica cada coisa nova, uma vez</small></span>
        <input type="checkbox" role="switch" checked={dicas} onChange={e => { ligarDicas((e.target as HTMLInputElement).checked); setDicas(dicasLigadas()); }} /></label>
    </>
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
    <>
      <section className="mc-bloco" aria-labelledby="cfg-reg">
        <h3 className="mc-bloco__tit" id="cfg-reg"><Deco nome={ICONE.registro} />Registro e replay</h3>
        <p>O estado do pet nunca é salvo: só o registro. A vida é refeita a partir dele.</p>
        <p className="mc-numeros"><span><b>{m.semente}</b> semente</span><span><b>{m.log.length}</b> eventos</span></p>
        <div className="mc-linha">
          <BotaoHx onClick={verificar}>Verificar replay</BotaoHx>
          <BotaoHx onClick={copiar}>Copiar registro</BotaoHx>
          <BotaoHx onClick={exportar}>Exportar pet</BotaoHx>
        </div>
        {msg && <p className={msg.erro ? "mc-erro" : "mc-ok"} aria-live="polite">{msg.txt}</p>}
      </section>
      <section className="mc-bloco" aria-labelledby="cfg-tempo">
        <h3 className="mc-bloco__tit" id="cfg-tempo"><Deco nome={ICONE.tempo} />Tempo <ChipHx tom="alerta">TESTE</ChipHx></h3>
        <p>Acelera o relógio do pet. Tudo entra no registro. Durante a luta e o Resultado dela o relógio para.</p>
        <div className="mc-linha tempo-pet" role="group" aria-label="Velocidade do tempo">
          {VELOCIDADES.map(([rot, v, dica]) => (
            <BotaoHx key={rot} aria-pressed={velocidade === v} title={dica} onClick={() => escolherVelocidade(v)}>{rot}</BotaoHx>
          ))}
          <BotaoHx onClick={pularUmaHora}>+1 h</BotaoHx>
        </div>
      </section>
      <section className="mc-risco" aria-label="Área de risco">
        <div className="mc-linha">
          <BotaoHx onClick={() => setConfirmar(true)}>Novo ovo (apaga este pet)</BotaoHx>
          {confirmar && <BotaoHx tom="perigo" onClick={() => { setConfirmar(false); abrirEscolhaBrasao(); irPet(); }}>Confirmar: apagar este pet</BotaoHx>}
        </div>
      </section>
    </>
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
    <>
      <section className="mc-bloco">
        <p className="mc-status"><span className="mc-ponto" data-estado={r.estado} aria-hidden="true" /><b title={r.titulo}>{r.texto}</b></p>
        <p className="mc-apoio">{fl.status ? `fala livre: ${fl.status.modelo}, local` : fl.statusErro ? "servidor sem a fala livre" : ""}</p>
        <label className="mc-interruptor"><span><b>Usar o modelo de linguagem</b><small>Só no Champion em diante. Desligado, o pet fala por frases prontas.</small></span>
          <input type="checkbox" role="switch" checked={FALA_LLM.on} disabled={!llm.ativo} onChange={ev => ligarFalaLLM((ev.target as HTMLInputElement).checked)} /></label>
      </section>
      <h3 className="mc-sec" id="cfg-modo">Como ele monta a fala</h3>
      <div className="mc-opcoes" role="radiogroup" aria-labelledby="cfg-modo">
        {modos.map(([k, rot, desc, tag]) => (
          <button type="button" key={k} role="radio" aria-checked={fl.modo === k} className="mc-opcao" onClick={() => escolherModo(k)}>
            <b>{rot}{tag && <ChipHx tom="alerta">{tag}</ChipHx>}</b><small>{desc}</small>
          </button>
        ))}
      </div>
      <p className="mc-apoio">Em todos os modos, a fala não decide nada e o que você escreve na conversa não ensina o pet.</p>
    </>
  );
}
function Sobre() {
  return (
    <>
      <div className="mc-sobre-topo">
        <Deco nome="Digivice_Circle_01" />
        <span className="mc-sobre-nome">DIGILAB</span>
        <span className="mc-lcd">motor v1 · combate V2.1</span>
      </div>
      <section className="mc-bloco"><h3 className="mc-bloco__tit">Sobre</h3>
        <p>Um pet virtual que aprende com o dono. O estado nunca é salvo, só o registro do que aconteceu; a vida é refeita a partir dele, sempre igual.</p></section>
      {/* a procedencia dos assets (docs/UI_GUIDELINES.md, secao 5.1; a MV-6, decisao definitiva do Matheus de 2026-10-24) */}
      <section className="mc-bloco"><h3 className="mc-bloco__tit">Créditos e procedência</h3>
        <p>Os sprites, os ícones e os fundos são do Digimon UP (Bandai), com o crédito, e o uso neste projeto foi autorizado pelo Matheus. O atlas
          fica fora do repositório; sem ele, o jogo usa os sprites de reserva, de arte própria.</p></section>
    </>
  );
}
export function TelaConfig({ parte, abrir, irPet }: { parte: ParteConfig; abrir: (p: ParteConfig) => void; fechar: () => void; irPet: () => void }) {
  return (
    <section className="mc mc-cfg" aria-label={TITULO[parte]}>
      {parte !== "principal" && (
        <div className="mc-linha">
          <BotaoHx className="mc-voltar" aria-label="Voltar aos Ajustes" onClick={() => abrir("principal")}><span aria-hidden="true">‹</span> Ajustes</BotaoHx>
          <h3 className="mc-bloco__tit" id="tela-titulo">{TITULO[parte]}</h3>
        </div>
      )}
      {parte === "principal" ? <Principal abrir={abrir} /> : parte === "aparencia" ? <Aparencia /> : parte === "dados" ? <Dados irPet={irPet} />
        : parte === "fala" ? <Fala /> : <Sobre />}
    </section>
  );
}
