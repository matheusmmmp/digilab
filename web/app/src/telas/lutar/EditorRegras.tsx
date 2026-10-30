/* Regras de combate do pet (desenhos EnsinarRegras e BatVS; porte do HTML): cards SE/ENTAO numerados, botoes
   de icone com estado (travada, vetada, livre), contador de espacos, a regra final, as vetadas e o que o pet
   mudou. O dono so trava ou veta; tudo entra no registro. */
import { useState } from "react";
import { CV, CV21, NOME_V2, regraDe, rotuloCond, rotuloRegra, type OpGambit, baseDe } from "../../../motor/index.ts";
import { comSinal } from "../../componentes/Barras.tsx";
import { mudarMotor, useJogo } from "../../jogo.ts";

const IcoTrava = () => <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="4" y="9" width="12" height="8" rx="2" /><path d="M7 9V6a3 3 0 0 1 6 0v3" /></svg>;
const IcoVeto = () => <svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7" /><path d="M5 15 15 5" /></svg>;
const IcoLibera = () => <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10l4 4 8-8" /></svg>;

export function EditorRegras() {
  const { motor: m } = useJogo(), [msg, setMsg] = useState(""), gp = m.gp;
  if (!gp) return <p className="dl-apoio">O In-Training ainda não tem estilo de luta: decide ao acaso. Quando evoluir para Rookie, o ramo (sereno ou arisco) semeia as primeiras 3 regras de combate e ele começa a aprender com as lutas.</p>;
  const intervir = (op: OpGambit, k: string) => {
    try { mudarMotor(mm => mm.intervirGambit(op, k)); setMsg(""); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const cartao = (k: string, i: number, estado: "livre" | "travada" | "vetada") => {
    const r = regraDe(k), chip = gp.chipsRegra.includes(k);
    return (
      <li className={`g-card g-${estado}`} key={k}>
        <span className="g-num">{estado === "vetada" ? "×" : i + 1}</span>
        <span className="g-corpo">
          <span className="g-se"><b>SE</b> {r.se.map(rotuloCond).join(" e ")}</span>
          <span className="g-entao"><b>ENTÃO</b> {NOME_V2[r.entao]}</span>
          <span className="g-meta">{estado === "travada" && <><span className="dl-tag dl-tag--estagio">travada</span> </>}{estado === "vetada" && <><span className="dl-tag dl-tag--espera">vetada</span> </>}{chip && <><span className="dl-tag dl-tag--chip">chip</span> </>}
            {estado === "vetada" ? "" : `nota ${comSinal(gp.notas[k], 2).replace(".", ",")} · usada ${gp.disparos[k] || 0}×`}</span>
        </span>
        <span className="g-bts">
          {estado === "vetada"
            ? <button type="button" className="dl-btn dl-btn--icone" aria-label="Liberar esta regra" onClick={() => intervir("liberar", k)}><IcoLibera /></button>
            : <>
              <button type="button" className={`dl-btn dl-btn--icone${estado === "travada" ? " g-on" : ""}`} aria-pressed={estado === "travada"}
                aria-label={estado === "travada" ? "Destravar" : "Travar nesta posição"} onClick={() => intervir(estado === "travada" ? "destravar" : "travar", k)}><IcoTrava /></button>
              {!chip && <button type="button" className="dl-btn dl-btn--icone" aria-label="Vetar: o pet não usa" onClick={() => intervir("vetar", k)}><IcoVeto /></button>}
            </>}
        </span>
      </li>
    );
  };
  const cap = CV21.maxRegras[baseDe(gp.forma!.est)];
  return (
    <div className="bloco">
      <p>Lista aprendida pelo pet em {gp.nLutas} luta{gp.nLutas === 1 ? "" : "s"}. Começou com as regras de <b>{gp.linha}</b>; cabem {cap} regras agora{gp.forma!.est === "adulto" || gp.forma!.est === "mega" ? "" : ", e a lista cresce quando ele evoluir"}. Vale a primeira regra cujas condições batem.</p>
      <details className="dl-apoio"><summary>Como ele escolhe</summary><p>A primeira regra cujas condições valem e cuja ação é possível dispara. Em {Math.round(CV.eps * 100)}% das decisões ele tenta algo ao acaso, para descobrir regras novas.</p></details>
      <p className="g-cont"><b>{gp.ativas.length} de {cap}</b> espaços de regra ocupados</p>
      <ol className="g-lista">
        {gp.ativas.map((k, i) => cartao(k, i, k in gp.travas ? "travada" : "livre"))}
        <li className="g-card g-final"><span className="g-num">∞</span><span className="g-corpo"><span className="g-se"><b>SE</b> nenhuma regra acima valer</span><span className="g-entao"><b>ENTÃO</b> {NOME_V2[gp.final]}</span></span></li>
      </ol>
      {gp.vetos.length > 0 && <><h2>Vetadas por você</h2><ol className="g-lista">{gp.vetos.map((k, i) => cartao(k, i, "vetada"))}</ol></>}
      <p className="dl-apoio">Você só pode <b>travar</b> (a regra fica nessa posição) ou <b>vetar</b> (o pet não pode usá-la). Tudo entra no registro.</p>
      <details><summary>O que o pet mudou</summary><div className="decisoes">
        {gp.mudancas.slice(-15).reverse().map((x, i) => { const tx = x.texto.replace(/(\d)\.(\d)/g, "$1,$2");
          return <div key={i}><span className="t">luta {x.luta}</span> {x.dono ? <b>{tx}</b> : "pet " + tx}</div>; })}
      </div></details>
      {msg && <p className="dl-apoio erro" role="alert">{msg}</p>}
    </div>
  );
}
