/* Registro (desenho DiarioRegistro; porte do HTML): o estado nunca e salvo, so o registro. Verificar replay,
   copiar o registro, filtros por tipo com etiqueta colorida, e o ovo novo numa area de risco separada, com
   confirmacao. A contagem diz o que e evento do registro e o que e linha reconstruida (revisao, item 3). */
import { useState } from "preact/hooks";
import { Motor, NOME_PET, type ItemHistorico } from "../../../motor/index.ts";
import { novoPet, useJogo } from "../../jogo.ts";
import { textoSave } from "../../save.ts";
import { diaDe, hhmm } from "../pet/TelaPet.tsx";

type Filtro = "todos" | "voce" | "pet" | "luta" | "recusa" | "treino";
/* tipo de cada linha do historico: [filtro, etiqueta, cor da etiqueta] (prancha DiarioRegistro) */
const TIPO_REG: Record<string, [Exclude<Filtro, "todos">, string, string]> = {
  dono: ["voce", "você", "voce"], gambit: ["voce", "regras", "regras"], pet: ["pet", "pet", "pet"], recusa: ["recusa", "recusa", "recusa"],
  luta: ["luta", "luta", "luta"], treino: ["treino", "treino", "treino"],
};
const FILTROS: [Filtro, string][] = [["todos", "tudo"], ["voce", "você"], ["pet", "pet"], ["luta", "lutas"], ["recusa", "recusas"], ["treino", "treino"]];
const textoLinha = (h: ItemHistorico): string => h.quem === "gambit" ? `regras de combate: ${h.a}` : h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] : h.a;

export function TelaRegistro({ irPet }: { irPet: () => void }) {
  const { motor: m } = useJogo(), [filtro, setFiltro] = useState<Filtro>("todos"), [msg, setMsg] = useState<{ txt: string; erro?: boolean } | null>(null), [confirmar, setConfirmar] = useState(false);
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
    <div class="tela dl reg-tela">
      <section class="dl-card reg-cab">
        <p>O estado do pet nunca é salvo. Só este registro, e a vida é reconstruída a partir dele.</p>
        <p class="reg-semente"><b>semente</b> <span class="dl-lcd">{m.semente}</span> · <span class="dl-lcd">{m.log.length}</span> <b>eventos</b></p>
        <div class="reg-bts">
          <button type="button" class="dl-btn" onClick={verificar}>Verificar replay</button>
          <button type="button" class="dl-btn dl-btn--sec" onClick={copiar}>Copiar registro</button>
        </div>
        {msg && <p class={`reg-msg${msg.erro ? " erro" : ""}`} aria-live="polite"><i aria-hidden="true">{msg.erro ? "!" : "✓"}</i>{msg.txt}</p>}
      </section>
      <div class="reg-filtros" role="group" aria-label="Filtrar o registro">
        {FILTROS.map(([f, rot]) => <button type="button" key={f} class="chip" aria-pressed={filtro === f} onClick={() => setFiltro(f)}>{rot}</button>)}
      </div>
      <div class="log" aria-live="polite">
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
