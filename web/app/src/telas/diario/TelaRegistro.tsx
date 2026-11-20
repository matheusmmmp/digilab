/* Registro (desenho DiarioRegistro; L3 de "Lugares da ilha", prancha diario_registro_*): o estado nunca e salvo, so o registro. A vista tem a semente, os
   eventos, Verificar e Copiar, os filtros e as linhas (hora, tipo em icone, texto); a frase do "como funciona" e o aviso do Novo ovo ficam fechados. O tipo
   de cada linha e um icone (o nome vai no aria-label); "regras" e o aprendido (tracejado ciano). Verificar replay, copiar o registro, e o ovo novo em
   area de risco separada, com confirmacao. */
import { useState } from "react";
import { Ban, Brain, ChevronRight, Copy, Dumbbell, Hand, HeartCrack, Layers, Medal, Package, PawPrint, RotateCcw, Swords, X, type LucideIcon } from "lucide-react";
import { Motor, NOME_PET, type ItemHistorico } from "../../../motor/index.ts";
import { replayDaTelaConfere, textoDaTela, useJogo } from "../../jogo.ts";
import { abrirEscolhaBrasao } from "../../jornada.ts";
import { textoSave } from "../../save.ts";
import { diaDe, hhmm } from "../pet/TelaPet.tsx";
import { Folha } from "../../componentes/Folha.tsx";
import { ComoFunciona } from "../../componentes/Dica.tsx";
import { Codice } from "../../componentes/Codice.tsx";

type Filtro = "todos" | "voce" | "pet" | "luta" | "recusa" | "treino";
/* tipo de cada linha do historico: [filtro, etiqueta, cor da etiqueta] (prancha DiarioRegistro) */
const TIPO_REG: Record<string, [Exclude<Filtro, "todos">, string, string]> = {
  dono: ["voce", "você", "voce"], gambit: ["voce", "regras", "regras"], pet: ["pet", "pet", "pet"], recusa: ["recusa", "recusa", "recusa"],
  luta: ["luta", "luta", "luta"], treino: ["treino", "treino", "treino"],
  /* pets v6: o pet passou a saber das medalhas do Tamer (evento "u") */
  tamer: ["luta", "medalha", "luta"],
  /* a lesao da luta, a carta usada nela e o chip equipado: sem tipo aqui, o filtro de lutas quebrava a tela inteira */
  lesao: ["luta", "lesão", "luta"], carta: ["luta", "carta", "luta"], item: ["voce", "item", "regras"],
};
const FILTROS: [Filtro, string][] = [["todos", "tudo"], ["voce", "você"], ["pet", "pet"], ["luta", "lutas"], ["recusa", "recusas"], ["treino", "treino"]];
const textoLinha = (h: ItemHistorico): string => h.quem === "gambit" ? `regras de combate: ${h.a}` : h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] : h.a;
/** o icone de cada tipo de linha (o nome vai no aria-label) */
const ICONE_TIPO: Record<string, LucideIcon> = {
  dono: Hand, gambit: Brain, pet: PawPrint, recusa: Ban, luta: Swords, treino: Dumbbell, tamer: Medal, lesao: HeartCrack, carta: Layers, item: Package,
};

export function TelaRegistro({ irPet }: { irPet: () => void }) {
  const { motor: m } = useJogo(), [filtro, setFiltro] = useState<Filtro>("todos"), [msg, setMsg] = useState<{ txt: string; erro?: boolean } | null>(null), [confirmar, setConfirmar] = useState(false), [evSel, setEvSel] = useState<number | null>(null);
  const nh = m.historico.length;
  const vis = m.historico.slice(-80).reverse().filter(h => filtro === "todos" || TIPO_REG[h.quem][0] === filtro);
  /* detalhe: o evento tocado */
  const ev = evSel !== null ? vis[evSel] : undefined;
  const detalhe = ev && <>
    <span className="dl-lcd">D{diaDe(ev.t)} {hhmm(ev.t)}</span>
    <b>{textoLinha(ev)}</b>
    <span className={`reg-tag reg-${TIPO_REG[ev.quem][2]}`}>{TIPO_REG[ev.quem][1]}</span>
    <span className="dl-apoio">evento do registro</span>
  </>;
  const verificar = () => {
    const t0 = performance.now();
    try {
      const { ok, eventos } = replayDaTelaConfere();       // os dois pets (CO4d): o registro do grupo inteiro
      setMsg(ok ? { txt: `Replay idêntico: ${eventos} eventos reconstruíram o mesmo pet, até o último decimal, em ${(performance.now() - t0).toFixed(0)} ms.` }
        : { txt: "O replay divergiu do pet atual. Isso é um bug do porte; copie o registro e mande para análise.", erro: true });
    } catch (err) { setMsg({ txt: "Replay falhou: " + (err instanceof Error ? err.message : String(err)), erro: true }); }
  };
  const copiar = async () => {
    /* o mesmo conteudo do save: semente, registro e versao do pet */
    const txt = textoDaTela();
    try { await navigator.clipboard.writeText(txt); setMsg({ txt: "Registro copiado." }); }
    catch { console.log(txt); setMsg({ txt: "Não foi possível copiar automaticamente. O registro está no console do navegador." }); }
  };
  return (
    <div className="tela dl rg2-tela lg">
      <section className="lg-destaque lg-linha rg2-topo" aria-label="Registro do pet">
        <span className="rg2-par"><small>semente</small><b className="lg-num lg-num--p">{m.semente}</b></span>
        <span className="rg2-par"><small>eventos</small><b className="lg-num lg-num--p">{m.log.length}</b></span>
        <span className="lg-linha rg2-bts">
          <button type="button" className="rg2-bt rg2-bt--acao" aria-label="Verificar replay" onClick={verificar}><RotateCcw aria-hidden="true" />Verificar</button>
          <button type="button" className="rg2-bt" aria-label="Copiar registro" onClick={copiar}><Copy aria-hidden="true" />Copiar</button>
        </span>
      </section>
      {/* MITOLOGIA, E1: o Codice das lendas (so com a chave `mitologia`) */}
      <Codice />
      {/* a regiao viva fica sempre no DOM (so assim o leitor anuncia a primeira mensagem) */}
      <p className={msg ? `reg-msg${msg.erro ? " erro" : ""}` : "sr-so"} aria-live="polite">{msg && <><i aria-hidden="true">{msg.erro ? "!" : "✓"}</i>{msg.txt}</>}</p>
      <div className="rg2-filtros" role="group" aria-label="Filtrar o registro">
        {FILTROS.map(([f, rot]) => <button type="button" key={f} className="rg2-filtro" aria-pressed={filtro === f} onClick={() => { setFiltro(f); setEvSel(null); }}>{rot}</button>)}
      </div>
      <div className="rg2-log" role="region" aria-label="O registro, do mais novo ao mais velho">
        {vis.length ? vis.map((h, i) => {
          const [, rot] = TIPO_REG[h.quem], I = ICONE_TIPO[h.quem] ?? Hand;
          return (
            <button type="button" className={`rg2-linha${h.quem === "recusa" ? " rg2-linha--recusa" : ""}`} key={i} onClick={() => setEvSel(i)}>
              <span className="rg2-t">D{diaDe(h.t)} {hhmm(h.t)}</span>
              <span className={"rg2-tipo" + (h.quem === "gambit" ? " rg2-tipo--apr" : "")} role="img" aria-label={rot}><I aria-hidden="true" /></span>
              <span className="rg2-txt">{textoLinha(h)}</span>
              <ChevronRight className="rg2-seta" aria-hidden="true" />
            </button>
          );
        }) : <p className="lg-sec">nada deste tipo</p>}
      </div>
      {evSel !== null && ev && <Folha titulo="Evento do registro" fechar={() => setEvSel(null)}><div className="reg-det reg-det--folha">{detalhe}</div></Folha>}
      <ComoFunciona>
        O estado do pet nunca é salvo. Só este registro, e a vida é reconstruída a partir dele. Verificar refaz o pet a partir dos eventos e confere se sai o mesmo, até o último decimal. Linhas reconstruídas do registro: {nh > 80 ? `as últimas 80 de ${nh}` : `${nh}`}.
      </ComoFunciona>
      <details className="lg-como zona-risco">
        <summary><X aria-hidden="true" />Novo ovo<ChevronRight className="lg-seta" aria-hidden="true" /></summary>
        <p className="lg-sec">Um ovo novo apaga este pet e o registro dele. Não dá para desfazer.</p>
        <div className="lg-linha">
          <button type="button" className="rg2-bt" onClick={() => setConfirmar(true)}>Novo ovo</button>
          {confirmar && <button type="button" className="rg2-bt rg2-bt--perigo" onClick={() => { setConfirmar(false); abrirEscolhaBrasao(); irPet(); }}>Confirmar: apagar este pet</button>}
        </div>
      </details>
    </div>
  );
}
