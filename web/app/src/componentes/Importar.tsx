/* Importar pet (pranchas MpImportar e MpImportarDesktop): escolhe o arquivo .digilab, confere o replay e, se o pet ja
   existe aqui com outro registro, mostra os dois lado a lado ("Neste aparelho" x "No arquivo") para o dono escolher.
   O que nao fica vai para a espera: nada e apagado. */
import { useEffect, useRef, useState } from "react";
import { NOME_PET, chaveSprite, nomeEstagio, nomeForma, type Motor } from "../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../atlas.ts";
import { ficarComArquivo, importarSemConflito, lerArquivo, localizar, petAqui, type Lido } from "../importar.ts";
import { diaDe, hhmm } from "../telas/pet/TelaPet.tsx";
import { abrirModal } from "./modal.ts";

function Lado({ titulo, m, sel }: { titulo: string; m: Motor; sel?: boolean }) {
  const a = useAtlas(), k = chaveSprite(m.forma);
  const s = a.tipo === "ok" ? imagemAtlas(a, k, Math.max(1, Math.min(3, Math.floor(110 / dimSprite(a.dados, k)[1])))) : null;
  const ult = m.historico.slice(-4).reverse();
  const texto = (h: (typeof ult)[number]) => h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] ?? h.a : h.a;
  return (
    <section className={`imp-lado${sel ? " sel" : ""}`}>
      <h3>{titulo}</h3>
      <div className="imp-palco dl-hexcard">{s && <img className="dl-pix" src={s.url} width={s.w} height={s.h} alt="" />}</div>
      <div className="imp-nome"><b>{nomeForma(m.forma)}</b><span className="dl-tag dl-tag--estagio">{nomeEstagio(m.forma)}</span>
        <span className="dl-lcd">última: D{diaDe(m.e.tick)} {hhmm(m.e.tick)}</span></div>
      <ol className="imp-hist">{ult.map((h, i) => <li key={i}><span className="dl-lcd">D{diaDe(h.t)} {hhmm(h.t)}</span><span>{texto(h)}</span></li>)}</ol>
      <small>{m.log.length} eventos no registro</small>
    </section>
  );
}

/** pagina: no desktop a tela fica dentro da casca (MpImportarDesktop), com o topo da casca; no celular, tela cheia */
export function ImportarPet({ fechar, pagina = false }: { fechar: () => void; pagina?: boolean }) {
  const ref = useRef<HTMLDialogElement>(null), arq = useRef<HTMLInputElement>(null);
  const [lido, setLido] = useState<Lido | null>(null), [conflito, setConflito] = useState<Motor | null>(null), [msg, setMsg] = useState(""), [erro, setErro] = useState("");
  useEffect(() => { if (!pagina) abrirModal(ref.current); }, []);
  const sair = () => { if (pagina) fechar(); else ref.current?.close(); };
  const escolher = async (f: File | undefined) => {
    setMsg(""); setErro(""); setLido(null); setConflito(null);
    if (!f) return;
    try {
      const l = lerArquivo(await f.text(), f.name), o = localizar(l.g.semente), aqui = petAqui(o);
      setLido(l);
      if (aqui && JSON.stringify(aqui.log) !== JSON.stringify(l.g.log)) { setConflito(aqui); return; }
      setMsg(importarSemConflito(l));
    } catch (err) { setErro(err instanceof Error ? err.message : String(err)); }
  };
  const ficar = () => { try { ficarComArquivo(lido!); sair(); } catch (err) { setErro(err instanceof Error ? err.message : String(err)); } };
  const corpo = (
      <div className="imp-corpo">
        <div className="imp-col">
          <section className="imp-arquivo">
            <h3>Arquivo</h3>
            <input ref={arq} type="file" accept=".digilab,.json,application/json" className="imp-input" id="imp-arq" onChange={e => escolher((e.currentTarget as HTMLInputElement).files?.[0])} />
            <label htmlFor="imp-arq" className="dl-btn dl-btn--sec">{lido ? "Escolher outro arquivo" : "Escolher arquivo .digilab"}</label>
            {lido && !erro && <p className="imp-ok"><b>{lido.arquivo}</b><span>✓ replay confere · registro válido</span></p>}
            {erro && <p className="imp-erro" role="alert">{erro}</p>}
            {msg && <p className="imp-ok" aria-live="polite">{msg}</p>}
          </section>
          {conflito && <section className="imp-aviso"><b>Este pet já existe aqui, com outro registro</b>
            <p>Mesma semente, histórias diferentes. Escolha qual fica. A outra não é apagada: vai para a espera.</p></section>}
          <div className="imp-bts">
            {conflito && <button type="button" className="dl-btn dl-btn--largo" onClick={ficar}>Ficar com o arquivo</button>}
            <button type="button" className="dl-btn dl-btn--sec dl-btn--largo" onClick={sair}>{conflito ? "Cancelar" : msg ? "Pronto" : "Voltar"}</button>
          </div>
        </div>
        {conflito && lido && <div className="imp-lados"><Lado titulo="Neste aparelho" m={conflito} /><Lado titulo="No arquivo" m={lido.m} sel /></div>}
      </div>
  );
  if (pagina) return <section className="importar-pagina dl" aria-label="Importar pet">{corpo}</section>;
  return (
    <dialog className="importar-tela dl" ref={ref} aria-labelledby="imp-tit" onClose={fechar}>
      <div className="imp-cab dl-faixa">
        <button type="button" className="conv-voltar" aria-label="Voltar" onClick={sair}>
          <svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M10 3 5 8l5 5" /></svg></button>
        <h2 className="dl-num" id="imp-tit">Importar pet</h2>
      </div>
      {corpo}
    </dialog>
  );
}
