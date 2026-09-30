/* Regras de combate do pet (desenhos EnsinarRegras e BatVS; porte do HTML): cards SE/ENTAO numerados, botoes
   de icone com estado (travada, vetada, livre), contador de espacos, a regra final, as vetadas e o que o pet
   mudou. O dono so trava ou veta; tudo entra no registro. */
import { useState } from "preact/hooks";
import { CV, CV21, NOME_V2, regraDe, rotuloCond, rotuloRegra, type OpGambit, baseDe } from "../../../motor/index.ts";
import { comSinal } from "../../componentes/Barras.tsx";
import { mudarMotor, useJogo } from "../../jogo.ts";

const IcoTrava = () => <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="4" y="9" width="12" height="8" rx="2" /><path d="M7 9V6a3 3 0 0 1 6 0v3" /></svg>;
const IcoVeto = () => <svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7" /><path d="M5 15 15 5" /></svg>;
const IcoLibera = () => <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10l4 4 8-8" /></svg>;

export function EditorRegras() {
  const { motor: m } = useJogo(), [msg, setMsg] = useState(""), gp = m.gp;
  if (!gp) return <p class="dl-apoio">O In-Training ainda não tem estilo de luta: decide ao acaso. Quando evoluir para Rookie, o ramo (sereno ou arisco) semeia as primeiras 3 regras de combate e ele começa a aprender com as lutas.</p>;
  const intervir = (op: OpGambit, k: string) => {
    try { mudarMotor(mm => mm.intervirGambit(op, k)); setMsg(""); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const cartao = (k: string, i: number, estado: "livre" | "travada" | "vetada") => {
    const r = regraDe(k), chip = gp.chipsRegra.includes(k);
    return (
      <li class={`g-card g-${estado}`} key={k}>
        <span class="g-num">{estado === "vetada" ? "×" : i + 1}</span>
        <span class="g-corpo">
          <span class="g-se"><b>SE</b> {r.se.map(rotuloCond).join(" e ")}</span>
          <span class="g-entao"><b>ENTÃO</b> {NOME_V2[r.entao]}</span>
          <span class="g-meta">{estado === "travada" && <><span class="dl-tag dl-tag--estagio">travada</span> </>}{estado === "vetada" && <><span class="dl-tag dl-tag--espera">vetada</span> </>}{chip && <><span class="dl-tag dl-tag--chip">chip</span> </>}
            {estado === "vetada" ? "" : `nota ${comSinal(gp.notas[k], 2).replace(".", ",")} · usada ${gp.disparos[k] || 0}×`}</span>
        </span>
        <span class="g-bts">
          {estado === "vetada"
            ? <button type="button" class="dl-btn dl-btn--icone" aria-label="Liberar esta regra" onClick={() => intervir("liberar", k)}><IcoLibera /></button>
            : <>
              <button type="button" class={`dl-btn dl-btn--icone${estado === "travada" ? " g-on" : ""}`} aria-pressed={estado === "travada"}
                aria-label={estado === "travada" ? "Destravar" : "Travar nesta posição"} onClick={() => intervir(estado === "travada" ? "destravar" : "travar", k)}><IcoTrava /></button>
              {!chip && <button type="button" class="dl-btn dl-btn--icone" aria-label="Vetar: o pet não usa" onClick={() => intervir("vetar", k)}><IcoVeto /></button>}
            </>}
        </span>
      </li>
    );
  };
  const cap = CV21.maxRegras[baseDe(gp.forma!.est)];
  return (
    <div class="bloco">
      <p>Lista aprendida pelo pet em {gp.nLutas} luta{gp.nLutas === 1 ? "" : "s"}. Começou com as regras de <b>{gp.linha}</b>; cabem {cap} regras agora{gp.forma!.est === "adulto" || gp.forma!.est === "mega" ? "" : ", e a lista cresce quando ele evoluir"}. Vale a primeira regra cujas condições batem.</p>
      <details class="dl-apoio"><summary>Como ele escolhe</summary><p>A primeira regra cujas condições valem e cuja ação é possível dispara. Em {Math.round(CV.eps * 100)}% das decisões ele tenta algo ao acaso, para descobrir regras novas.</p></details>
      <p class="g-cont"><b>{gp.ativas.length} de {cap}</b> espaços de regra ocupados</p>
      <ol class="g-lista">
        {gp.ativas.map((k, i) => cartao(k, i, k in gp.travas ? "travada" : "livre"))}
        <li class="g-card g-final"><span class="g-num">∞</span><span class="g-corpo"><span class="g-se"><b>SE</b> nenhuma regra acima valer</span><span class="g-entao"><b>ENTÃO</b> {NOME_V2[gp.final]}</span></span></li>
      </ol>
      {gp.vetos.length > 0 && <><h2>Vetadas por você</h2><ol class="g-lista">{gp.vetos.map((k, i) => cartao(k, i, "vetada"))}</ol></>}
      <p class="dl-apoio">Você só pode <b>travar</b> (a regra fica nessa posição) ou <b>vetar</b> (o pet não pode usá-la). Tudo entra no registro.</p>
      <details><summary>O que o pet mudou</summary><div class="decisoes">
        {gp.mudancas.slice(-15).reverse().map((x, i) => { const tx = x.texto.replace(/(\d)\.(\d)/g, "$1,$2");
          return <div key={i}><span class="t">luta {x.luta}</span> {x.dono ? <b>{tx}</b> : "pet " + tx}</div>; })}
      </div></details>
      {msg && <p class="dl-apoio erro" role="alert">{msg}</p>}
    </div>
  );
}

/** desktop (ArenaDesktop): as regras em cards compactos, numerados, travada ou aprendida; o card escolhido mostra
    Travar/Vetar (ou Liberar, se vetada). Mesmas intervencoes do editor, mesmo registro. */
export function RegrasCompactas() {
  const { motor: m } = useJogo(), gp = m.gp, [sel, setSel] = useState<string | null>(null), [msg, setMsg] = useState("");
  if (!gp) return <p class="dl-apoio">O In-Training ainda luta ao acaso; as regras de combate começam no Rookie.</p>;
  const cap = CV21.maxRegras[baseDe(gp.forma!.est)];
  const intervir = (op: OpGambit, k: string) => {
    try { mudarMotor(mm => mm.intervirGambit(op, k)); setMsg(""); setSel(null); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  return (
    <div class="rc">
      <h2 class="rc-tit"><span>Regras de combate</span><small>{gp.ativas.length} de {cap}</small></h2>
      <ol class="rc-lista">
        {gp.ativas.map((k, i) => {
          const trav = k in gp.travas, aberto = sel === k, chip = gp.chipsRegra.includes(k);
          return (
            <li key={k} class={`rc-card dl-malha${aberto ? " rc-card--sel" : ""}`}>
              <button type="button" class="rc-toque" aria-expanded={aberto} onClick={() => setSel(aberto ? null : k)}>
                <span class="rc-topo"><span class="rc-num">{i + 1}{trav ? " · TRAVADA" : ""}</span><span class="rc-sub">{trav ? "travada por você" : chip ? "de um chip" : "aprendida"}</span></span>
                <span class="rc-txt">{rotuloRegra(regraDe(k)).replace(/^se/, "Se")}</span>
              </button>
              {aberto && <span class="luta-regra-bts">
                <button type="button" class="regra-travar" onClick={() => intervir(trav ? "destravar" : "travar", k)}><IcoTrava />{trav ? "Destravar" : "Travar"}</button>
                {!chip && <button type="button" class="regra-vetar" onClick={() => intervir("vetar", k)}>Vetar</button>}</span>}
            </li>
          );
        })}
        {gp.vetos.map(k => (
          <li key={k} class="rc-vetada">
            <button type="button" class="rc-toque" aria-expanded={sel === k} onClick={() => setSel(sel === k ? null : k)}>
              <s>{rotuloRegra(regraDe(k)).replace(/^se /, "")}</s> · vetada</button>
            {sel === k && <button type="button" class="dl-btn dl-btn--sec rc-liberar" onClick={() => intervir("liberar", k)}>Liberar</button>}
          </li>
        ))}
      </ol>
      <p class="dl-apoio rc-pe">Ele aprende lutando. Você só trava ou veta.</p>
      {msg && <p class="dl-apoio erro" role="alert">{msg}</p>}
    </div>
  );
}
