/* Registro (desenho DiarioRegistro; porte do HTML): o estado nunca e salvo, so o registro. Verificar replay,
   copiar o registro, filtros por tipo com etiqueta colorida, e o ovo novo numa area de risco separada, com
   confirmacao. A contagem diz o que e evento do registro e o que e linha reconstruida (revisao, item 3). */
import { useEffect, useRef, useState } from "preact/hooks";
import { Motor, NOME_PET, type ItemHistorico } from "../../../motor/index.ts";
import { novoPet, useJogo } from "../../jogo.ts";
import { textoSave } from "../../save.ts";
import { diaDe, hhmm } from "../pet/TelaPet.tsx";
import { REPLAY, reconstruirLuta } from "../../luta.ts";
import { fraseTurno } from "../lutar/ModalResultado.tsx";

type Filtro = "todos" | "voce" | "pet" | "luta" | "recusa" | "treino";
/* tipo de cada linha do historico: [filtro, etiqueta, cor da etiqueta] (prancha DiarioRegistro) */
const TIPO_REG: Record<string, [Exclude<Filtro, "todos">, string, string]> = {
  dono: ["voce", "você", "voce"], gambit: ["voce", "regras", "regras"], pet: ["pet", "pet", "pet"], recusa: ["recusa", "recusa", "recusa"],
  luta: ["luta", "luta", "luta"], treino: ["treino", "treino", "treino"],
};
const FILTROS: [Filtro, string][] = [["todos", "tudo"], ["voce", "você"], ["pet", "pet"], ["luta", "lutas"], ["recusa", "recusas"], ["treino", "treino"]];
const textoLinha = (h: ItemHistorico): string => h.quem === "gambit" ? `regras de combate: ${h.a}` : h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] : h.a;

/** Ver replay (modal Resultado): a luta do evento idx refeita do registro, turno a turno. So leitura. */
function ReplayLuta({ idx, fechar }: { idx: number; fechar: () => void }) {
  const { motor: m } = useJogo(), tit = useRef<HTMLHeadingElement>(null);
  const [luta] = useState(() => { try { return reconstruirLuta(m, idx); } catch (err) { return err instanceof Error ? err.message : String(err); } });
  useEffect(() => { tit.current?.focus(); }, []);
  if (typeof luta === "string") return (
    <section class="dl-card reg-replay" aria-labelledby="rep-tit"><h2 id="rep-tit" ref={tit} tabIndex={-1}>Replay da luta</h2>
      <p class="reg-msg erro"><i aria-hidden="true">!</i>Não foi possível refazer a luta: {luta}</p>
      <button type="button" class="dl-btn dl-btn--sec" onClick={fechar}>Fechar replay</button></section>
  );
  const { res, A, B } = luta, ev = m.log[idx];
  const txt = res.pontosA === 1 ? `${A.nomeTela} venceu` : res.pontosA === 0 ? `${B.nomeTela} venceu` : "Empate";
  return (
    <section class="dl-card reg-replay" aria-labelledby="rep-tit">
      <h2 id="rep-tit" ref={tit} tabIndex={-1}>Replay da luta</h2>
      <p><b>{A.nomeTela} × {B.nomeTela}</b> · <span class="dl-lcd">D{diaDe(ev[0])} {hhmm(ev[0])}</span> · {txt} em {res.turnos.length} turnos ({res.fim === "ko" ? "nocaute" : "limite de turnos"}).</p>
      <p class="dl-apoio">Refeita do registro (evento {idx + 1} de {m.log.length}): o pet reconstruído até a luta, o mesmo rival e a mesma semente.</p>
      <ol class="reg-replay-turnos">
        {res.turnos.map(tr => <li key={tr.t}><span class="dl-lcd">T{tr.t}</span><span>{fraseTurno(tr, A, B, null)}</span></li>)}
      </ol>
      <button type="button" class="dl-btn dl-btn--sec" onClick={fechar}>Fechar replay</button>
    </section>
  );
}

export function TelaRegistro({ irPet }: { irPet: () => void }) {
  const { motor: m } = useJogo(), [replay, setReplay] = useState(() => { const x = REPLAY.pedido; REPLAY.pedido = null; return x; }),
    [filtro, setFiltro] = useState<Filtro>(replay !== null ? "luta" : "todos"), [msg, setMsg] = useState<{ txt: string; erro?: boolean } | null>(null), [confirmar, setConfirmar] = useState(false);
  const nh = m.historico.length;
  const vis = m.historico.slice(-80).reverse().filter(h => filtro === "todos" || TIPO_REG[h.quem][0] === filtro);
  const verificar = () => {
    const t0 = performance.now();
    try {
      const ok = Motor.reproduzir(m.semente, m.log, m.versao).assinatura() === m.assinatura();
      setMsg(ok ? { txt: `Replay idêntico: ${m.log.length} eventos reconstruíram o mesmo pet, até o último decimal, em ${(performance.now() - t0).toFixed(0)} ms.` }
        : { txt: "O replay divergiu do pet atual. Isso é um bug do porte; copie o registro e mande para análise.", erro: true });
    } catch (err) { setMsg({ txt: "Replay falhou: " + (err instanceof Error ? err.message : String(err)), erro: true }); }
  };
  const copiar = async () => {
    /* o mesmo conteudo do save: semente, registro e versao do pet */
    const txt = textoSave(m);
    try { await navigator.clipboard.writeText(txt); setMsg({ txt: "Registro copiado." }); }
    catch { console.log(txt); setMsg({ txt: "Não foi possível copiar automaticamente. O registro está no console do navegador." }); }
  };
  return (
    <div class={`tela dl desk reg-tela${replay !== null ? " reg-tela--replay" : ""}`}>
      {replay !== null && <ReplayLuta idx={replay} fechar={() => setReplay(null)} />}
      <section class="dl-card reg-cab">
        <h2 class="desk-so reg-h">Replay</h2>
        <p>O estado do pet nunca é salvo. Só este registro, e a vida é reconstruída a partir dele.</p>
        <p class="reg-semente"><b>semente</b> <span class="dl-lcd">{m.semente}</span> · <span class="dl-lcd">{m.log.length}</span> <b>eventos</b></p>
        <div class="reg-bts">
          <button type="button" class="dl-btn" onClick={verificar}>Verificar replay</button>
          <button type="button" class="dl-btn dl-btn--sec" onClick={copiar}>Copiar registro</button>
        </div>
        {msg && <p class={`reg-msg${msg.erro ? " erro" : ""}`} aria-live="polite"><i aria-hidden="true">{msg.erro ? "!" : "✓"}</i>{msg.txt}</p>}
      </section>
      <div class="reg-filtros" role="group" aria-label="Filtrar o registro">
        <h2 class="desk-so reg-h">Mostrar</h2>
        {FILTROS.map(([f, rot]) => <button type="button" key={f} class="chip" aria-pressed={filtro === f} onClick={() => setFiltro(f)}>{rot}</button>)}
      </div>
      <div class="log" aria-live="polite">
        <h2 class="desk-so reg-h reg-log-tit"><span>Registro</span><small>dia {diaDe(m.e.tick)} · o mais novo em cima</small></h2>
        {vis.length ? vis.map((h, i) => {
          const [, rot, cor] = TIPO_REG[h.quem];
          return <div class={`reg-linha${h.quem === "recusa" ? " reg-linha--recusa" : ""}`} key={i}><span class="dl-lcd">D{diaDe(h.t)} {hhmm(h.t)}</span><span class={`reg-tag reg-${cor}`}>{rot}</span><span>{textoLinha(h)}</span></div>;
        }) : <div class="dl-apoio">nada deste tipo nas últimas 80 linhas</div>}
      </div>
      {vis[0] && <section class="dl-card reg-det" aria-label="Último evento">
        <span class="dl-lcd">D{diaDe(vis[0].t)} {hhmm(vis[0].t)}</span>
        <b>{textoLinha(vis[0])}</b>
        <span class={`reg-tag reg-${TIPO_REG[vis[0].quem][2]}`}>{TIPO_REG[vis[0].quem][1]}</span>
        <span class="dl-apoio">último evento{filtro === "todos" ? "" : " deste filtro"}</span>
      </section>}
      <p class="dl-apoio">Linhas reconstruídas do registro: {nh > 80 ? `as últimas 80 de ${nh}` : `${nh}`}.</p>
      <details class="zona-risco">
        <summary>Novo ovo (apaga este pet)</summary>
        <p class="dl-apoio">Um ovo novo apaga este pet e o registro dele. Não dá para desfazer.</p>
        <div class="dl-linha">
          <button type="button" class="dl-btn dl-btn--sec" onClick={() => setConfirmar(true)}>Novo ovo</button>
          {confirmar && <button type="button" class="dl-btn dl-btn--perigo" onClick={() => { setConfirmar(false); novoPet(); irPet(); }}>Confirmar: apagar este pet</button>}
        </div>
      </details>
    </div>
  );
}
