/* Ajustes na pele XCOM (layout habitat, M5; antes CfgPrincipal, CfgAparencia, CfgDados, CfgFala, CfgSobre), dentro do PainelTela
   (o titulo "Ajustes" e o "x" sao do painel). Uma coluna so, de ate 760 px, no desktop e no celular: o menu (principal) e, ao
   escolher uma parte, ela no lugar do menu, com o botao quadrado de voltar. So junta o que o app ja tinha (tema, registro e
   replay, tempo de teste, fala, som); tudo o que e visual (a pele, o tema, o mapa, a camera e o visual GBA HD/HD-2D) fica na subarea
   Visual (2026-11-01, no lugar da Aparencia; #/config/aparencia leva a ela), e as dicas ficam no menu principal; nada aqui muda o motor, as regras ou o save, a nao ser pelas mesmas acoes de antes
   (tempo e ovo novo, via jogo.ts/tempo.ts). Opcoes das pranchas que o app nao tem ficam de fora. Rotas #/config/<parte> iguais. */
import { useId } from "react";
import { Activity, Camera, ChevronRight, Clock, Eye, FlaskConical, Info, Lightbulb, MessageCircle, RotateCcw, ScrollText, Volume1, Volume2, type LucideIcon } from "lucide-react";
import { Balao, propsBalao } from "../../componentes/Dica.tsx";
import { escolherViagem, useViagemLigada } from "../../viagem.ts";
import { useState } from "react";
import "../../estilo/menus_config.css";
import { Motor } from "../../../motor/index.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { BotaoHx, ChipHx } from "../../componentes/hx/index.ts";
import { ICONE } from "../../decoracao.ts";
import { FALA_LLM, ligarFalaLLM, rotuloLLM, useFalaLLM } from "../../fala.ts";
import { escolherConversaNova, escolherFalaRede, escolherModo, useFalaLivre, type ModoFala } from "../../falaLivre.ts";
import { useJogo } from "../../jogo.ts";
import { abrirEscolhaBrasao } from "../../jornada.ts";
import type { ParteConfig } from "../../rotas.ts";
import { AvisoSom } from "../../componentes/AvisoSom.tsx";
import { SOM, useSom } from "../../som.ts";
import { dicasLigadas, ligarDicas } from "../../dicas.ts";
import { reverOTutorial } from "../../nivelTela.ts";
import { ligarDetalhesPet, useDetalhesPet } from "../../hudPet.ts";
import { textoSave } from "../../save.ts";
import { useHabitat } from "../../habitat.ts";
import { usePele } from "../../pele.ts";
import { escolherTema, useTema, type Tema } from "../../tema.ts";
import { EscolhaHabitat, resumoVisual } from "./EscolhaHabitat.tsx";
import { EscolhaPele } from "./EscolhaPele.tsx";
import { Laboratorio } from "./Laboratorio.tsx";
import { labLigado, useLab } from "../../lab.ts";
import { VELOCIDADES, escolherVelocidade, pularUmaHora, useTempo } from "../../tempo.ts";

const TITULO: Record<ParteConfig, string> = { principal: "Ajustes", visual: "Visual", dados: "Registro e replay", fala: "Fala do pet", laboratorio: "Laboratório", sobre: "Sobre" };
const NOME_MODO: Record<ModoFala, string> = { template: "frases prontas", moldura: "moldura", livre: "livre" };
export const nomeVelocidade = (v: number): string => VELOCIDADES.find(([, x]) => x === v)?.[0] ?? `${v} min/s`;

/** uma linha da lista de Ajustes (L3 de "Lugares da ilha", prancha ajustes_*): so o icone e o nome (a etiqueta, se houver); o resumo de antes vai para o balao e
    para o aria-label. `interruptor`: a linha e um interruptor (a linha inteira e o alvo); senao e um botao que abre a parte. */
function Aj({ ic: I, nome, rotulo, resumo, tag, novo, interruptor, abrir }: {
  ic: LucideIcon; nome: string; rotulo?: string; resumo: string; tag?: string; novo?: boolean;
  interruptor?: { ligado: boolean; mudar: (v: boolean) => void; desligado?: boolean }; abrir?: () => void;
}) {
  const id = useId(), cls = "aj" + (novo ? " aj--novo" : ""), nomeAcessivel = `${rotulo ?? nome}${tag ? `, ${tag}` : ""}`;
  const miolo = <><I className="aj-ic" aria-hidden="true" /><span className="aj-nome"><b>{nome}</b>{tag && <span className="lg-etq lg-etq--alerta">{tag}</span>}</span></>;
  return (
    <span className="dica-alvo dica-alvo--sem-foco aj-alvo" {...propsBalao(false)}>
      {interruptor
        ? <label className={cls}>{miolo}<input type="checkbox" role="switch" aria-label={nomeAcessivel} aria-describedby={id} checked={interruptor.ligado} disabled={interruptor.desligado}
            onChange={e => interruptor.mudar((e.target as HTMLInputElement).checked)} /></label>
        : <button type="button" className={cls} aria-label={nomeAcessivel} aria-describedby={id} onClick={abrir}>{miolo}<ChevronRight className="aj-seta" aria-hidden="true" /></button>}
      <Balao id={id} lado="cima">{resumo}</Balao>
    </span>
  );
}
function Principal({ abrir }: { abrir: (p: ParteConfig) => void }) {
  const { motor: m } = useJogo(), tema = useTema(), pele = usePele(), habitat = useHabitat(), fl = useFalaLivre(), { velocidade } = useTempo(), viagem = useViagemLigada(), som = useSom();
  const [dicas, setDicas] = useState(dicasLigadas), detalhesPet = useDetalhesPet(), [revisto, setRevisto] = useState(false);
  useFalaLLM(); useLab();
  return (
    <div className="aj-lista lg">
      <Aj ic={Eye} nome="Visual" resumo={resumoVisual(pele, tema, habitat, !!m.mundo)} abrir={() => abrir("visual")} />
      <Aj ic={Lightbulb} nome="Dicas" resumo="o Professor Agumon explica cada coisa nova, uma vez" interruptor={{ ligado: dicas, mudar: v => { ligarDicas(v); setDicas(dicasLigadas()); } }} />
      <Aj ic={RotateCcw} nome="Rever o tutorial" tag={revisto ? "feito" : undefined} resumo="os cartões dos níveis e as dicas do Professor Agumon voltam, cada um no seu momento (com as dicas ligadas)"
        abrir={() => { reverOTutorial(); setRevisto(true); }} />
      <span className="sr-only" role="status" aria-live="polite">{revisto ? "Tutorial reiniciado" : ""}</span>
      <Aj ic={Activity} nome="Detalhes do pet" rotulo="Exibir detalhes do pet" resumo="os painéis Estado atual, Evolução, Últimas ações e DigiBrain na tela do pet"
        interruptor={{ ligado: detalhesPet, mudar: ligarDetalhesPet }} />
      <Aj ic={Camera} nome="Viagem da câmera" novo resumo="desligada, os lugares abrem num corte seco" interruptor={{ ligado: viagem, mudar: escolherViagem }} />
      <Aj ic={MessageCircle} nome="Fala" rotulo="Fala do pet" resumo={`modo ${NOME_MODO[fl.modo]} · ${rotuloLLM().texto}`} abrir={() => abrir("fala")} />
      <Aj ic={Volume2} nome="Som" rotulo="Som do jogo" resumo="golpes e impactos na luta e o efeito da evolução; desligado, nada é baixado" interruptor={{ ligado: som.ligado, mudar: v => SOM.ligar(v) }} />
      {som.ligado && (
        <label className="aj aj--volume"><Volume1 className="aj-ic" aria-hidden="true" /><span className="aj-nome"><b>{Math.round(som.volume * 100)}%</b></span>
          <input type="range" min={0} max={1} step={0.05} value={som.volume} aria-label="Volume do som" aria-valuetext={`${Math.round(som.volume * 100)}%`} onChange={e => SOM.volume(Number((e.target as HTMLInputElement).value))} /></label>
      )}
      <AvisoSom />
      <Aj ic={ScrollText} nome="Registro" rotulo="Registro e replay" resumo={`semente ${m.semente} · ${m.log.length} eventos · exportar`} abrir={() => abrir("dados")} />
      <Aj ic={Clock} nome="Tempo" tag="teste" resumo={velocidade === 0 ? "pausado" : `velocidade ${nomeVelocidade(velocidade)}`} abrir={() => abrir("dados")} />
      <Aj ic={FlaskConical} nome="Laboratório" tag="experimental" resumo={labLigado() ? "modo ligado · o pet de teste com o DigiBrain modular" : "desligado · o jogo é o de hoje"} abrir={() => abrir("laboratorio")} />
      <Aj ic={Info} nome="Sobre" resumo="versão, créditos e procedência" abrir={() => abrir("sobre")} />
    </div>
  );
}
/** a subarea Visual: os menus (a pele) e o habitat (o tema, o mapa, a camera e o visual) */
function Visual() {
  const { motor: m } = useJogo(), tema = useTema(), opcoes: [Tema, string][] = [["claro", "Claro"], ["escuro", "Escuro"], ["sistema", "Sistema"]];
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
      <EscolhaHabitat temMundo={!!m.mundo} />
    </>
  );
}
function Dados({ irPet }: { irPet: () => void }) {
  const { motor: m, emLab } = useJogo(), { velocidade } = useTempo(), [msg, setMsg] = useState<{ txt: string; erro?: boolean } | null>(null), [confirmar, setConfirmar] = useState(false);
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
      {emLab ? <section className="mc-risco" aria-label="Área de risco"><p className="mc-apoio">Este é o pet de teste. Para chocar um ovo novo, volte ao seu pet; o pet de teste se descarta em Ajustes › Laboratório.</p></section>
      : <section className="mc-risco" aria-label="Área de risco">
        <div className="mc-linha">
          <BotaoHx onClick={() => setConfirmar(true)}>Novo ovo (apaga este pet)</BotaoHx>
          {confirmar && <BotaoHx tom="perigo" onClick={() => { setConfirmar(false); abrirEscolhaBrasao(); irPet(); }}>Confirmar: apagar este pet</BotaoHx>}
        </div>
      </section>}
    </>
  );
}
function Fala() {
  const llm = useFalaLLM(), fl = useFalaLivre(), r = rotuloLLM(), { motor: pet } = useJogo();
  const redeSemEfeito = fl.falaRede && pet.conceitosDec() === null;      /* DC2b: pet sem decisao do modular, a chave nao muda nada */
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
      <section className="mc-bloco">
        <label className="mc-interruptor"><span><b>Conversa nova (teste)</b><small>Só no modo Livre: prompt novo da conversa, com a memória só desta sessão e do estágio de agora.</small></span>
          <input type="checkbox" role="switch" checked={fl.conversaNova} disabled={fl.modo !== "livre"} onChange={ev => escolherConversaNova((ev.target as HTMLInputElement).checked)} /></label>
      </section>
      <section className="mc-bloco">
        <label className="mc-interruptor"><span><b>Fala pela rede (teste)</b><small>Só no modo Livre: a fala nasce do que o cérebro modular decidiu por último; o modelo só põe em palavras e não vê o resto do pet.</small></span>
          <input type="checkbox" role="switch" checked={fl.falaRede} disabled={fl.modo !== "livre"} onChange={ev => escolherFalaRede((ev.target as HTMLInputElement).checked)} /></label>
        {redeSemEfeito && <p className="mc-apoio" role="status">Este pet não tem uma decisão do cérebro modular: a chave não muda nada e a fala segue como antes.</p>}
      </section>
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
          fica fora do repositório; sem ele, o jogo usa os sprites de reserva, de arte própria.</p>
        {/* os kits 3D da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H1 e H-1): CC0, com as licencas em public/kits3d/ */}
        <p className="mc-credito-kits">As árvores, as plantas e as pedras da ilha são dos kits 3D de Quaternius (Stylized Nature MegaKit) e de Kay
          Lousberg (KayKit Forest Nature Pack), em domínio público (CC0). O saco de pancada, o kit médico, o cocô, os postes de luz, o carro, a geladeira e o trilho foram gerados com a Meshy (meshy.ai) e consertados no Blender; o céu do mapa Digital também é da Meshy. A bola foi feita no Blender pelo próprio projeto, sem IA.</p></section>
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
      {parte === "principal" ? <Principal abrir={abrir} /> : parte === "visual" ? <Visual /> : parte === "dados" ? <Dados irPet={irPet} />
        : parte === "fala" ? <Fala /> : parte === "laboratorio" ? <Laboratorio irPet={irPet} /> : <Sobre />}
    </section>
  );
}
