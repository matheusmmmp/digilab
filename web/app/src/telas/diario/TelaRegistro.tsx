/* Registro (desenho DiarioRegistro; porte do HTML): o estado nunca e salvo, so o registro. Verificar replay,
   copiar o registro, filtros por tipo com etiqueta colorida, e o ovo novo numa area de risco separada, com
   confirmacao. A contagem diz o que e evento do registro e o que e linha reconstruida (revisao, item 3). */
import { useState } from "preact/hooks";
import { Motor, NOME_PET, type ItemHistorico } from "../../../motor/index.ts";
import { novoPet, useJogo } from "../../jogo.ts";
import { textoSave } from "../../save.ts";
import { diaDe, hhmm } from "../pet/TelaPet.tsx";

type Filtro = "todos" | "voce" | "pet" | "luta" | "treino";
/* tipo de cada linha do historico: [filtro, etiqueta] */
const TIPO_REG: Record<string, [Exclude<Filtro, "todos">, string]> = {
  dono: ["voce", "você"], gambit: ["voce", "você"], pet: ["pet", "pet"], recusa: ["pet", "recusou"], luta: ["luta", "luta"], treino: ["treino", "treino"],
};
const FILTROS: [Filtro, string][] = [["todos", "Tudo"], ["voce", "Você"], ["pet", "Pet"], ["luta", "Lutas"], ["treino", "Treino"]];
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
    <div class="tela dl">
      <p>O estado do pet nunca é salvo. Só o registro de ações e passagem de tempo, e a vida é reconstruída do zero a partir dele.</p>
      <div class="dl-linha">
        <button type="button" class="dl-btn" onClick={verificar}>Verificar replay</button>
        <button type="button" class="dl-btn dl-btn--sec" onClick={copiar}>Copiar registro</button>
      </div>
      {msg && <p class={msg.erro ? "erro" : "dl-apoio"} aria-live="polite" style={{ fontWeight: 900 }}>{msg.txt}</p>}
      <div class="reg-filtros" role="group" aria-label="Filtrar o registro">
        {FILTROS.map(([f, rot]) => <button type="button" key={f} class="chip" aria-pressed={filtro === f} onClick={() => setFiltro(f)}>{rot}</button>)}
      </div>
      <p class="dl-apoio">Semente {m.semente} · {m.log.length} eventos no registro (suas ações, lutas e passagens de tempo). Abaixo, o que aconteceu, reconstruído a partir dele: {nh > 80 ? `as últimas 80 de ${nh} linhas` : `${nh} linha${nh === 1 ? "" : "s"}`}.</p>
      <div class="log" aria-live="polite">
        {vis.length ? vis.map((h, i) => {
          const [tp, rot] = TIPO_REG[h.quem];
          return <div class="reg-linha" key={i}><span class="t">D{diaDe(h.t)} {hhmm(h.t)}</span> <span class={`reg-tag reg-${tp}`}>{rot}</span> {h.quem === "recusa" ? <b>{textoLinha(h)}</b> : textoLinha(h)}</div>;
        }) : <div class="dl-apoio">nada deste tipo nas últimas 80 linhas</div>}
      </div>
      <section class="zona-risco" aria-label="Área de risco">
        <h2>Área de risco</h2>
        <p class="dl-apoio">Um ovo novo apaga este pet e o registro dele. Não dá para desfazer.</p>
        <div class="dl-linha">
          <button type="button" class="dl-btn dl-btn--sec" onClick={() => setConfirmar(true)}>Novo ovo</button>
          {confirmar && <button type="button" class="dl-btn dl-btn--perigo" onClick={() => { setConfirmar(false); novoPet(); irPet(); }}>Confirmar: apagar este pet</button>}
        </div>
      </section>
    </div>
  );
}
