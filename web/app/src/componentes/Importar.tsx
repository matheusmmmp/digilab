/* Importar pet na pele XCOM (layout habitat, M5): escolhe o arquivo .digilab, confere o replay e, se o pet ja existe aqui com
   outro registro, mostra os dois lado a lado ("Neste aparelho" x "No arquivo") para o dono escolher. O que nao fica vai para a
   espera: nada e apagado. No desktop e uma pagina dentro do PainelTela; no celular, uma caixa centralizada. */
import { useEffect, useRef, useState } from "react";
import "../estilo/menus_config.css";
import { NOME_PET, chaveSprite, nomeEstagio, nomeForma, type Motor } from "../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../atlas.ts";
import { ficarComArquivo, importarSemConflito, lerArquivo, localizar, petAqui, type Lido } from "../importar.ts";
import { diaDe, hhmm } from "../telas/pet/TelaPet.tsx";
import { BotaoContinuar, BotaoHx, ChipHx, PainelHx } from "./hx/index.ts";
import { abrirModal } from "./modal.ts";

function Lado({ titulo, m, sel }: { titulo: string; m: Motor; sel?: boolean }) {
  const a = useAtlas(), k = chaveSprite(m.forma);
  const s = a.tipo === "ok" ? imagemAtlas(a, k, Math.max(1, Math.min(3, Math.floor(110 / dimSprite(a.dados, k)[1])))) : null;
  const ult = m.historico.slice(-4).reverse();
  const texto = (h: (typeof ult)[number]) => h.quem === "pet" ? NOME_PET[h.a as keyof typeof NOME_PET] ?? h.a : h.a;
  return (
    <section className={`mc-lado${sel ? " mc-lado--sel" : ""}`}>
      <h3>{titulo}</h3>
      <div className="mc-palco">{s && <img className="dl-pix" src={s.url} width={s.w} height={s.h} alt="" />}</div>
      <div className="mc-tags"><b>{nomeForma(m.forma)}</b><ChipHx tom="rotulo">{nomeEstagio(m.forma)}</ChipHx>
        <span className="mc-apoio mc-num">última: D{diaDe(m.e.tick)} {hhmm(m.e.tick)}</span></div>
      <ol className="mc-hist">{ult.map((h, i) => <li key={i}><span className="mc-apoio mc-num">D{diaDe(h.t)} {hhmm(h.t)}</span><span>{texto(h)}</span></li>)}</ol>
      <small className="mc-apoio">{m.log.length} eventos no registro</small>
    </section>
  );
}

/** pagina: no desktop a tela fica dentro do painel; no celular, uma caixa centralizada */
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
    <div className={`mc-imp${pagina ? "" : " mc"}`}>
      <section className="mc-bloco">
        <h3 className="mc-bloco__tit">Arquivo</h3>
        <input ref={arq} type="file" accept=".digilab,.json,application/json" className="mc-input-arq" id="imp-arq" onChange={e => escolher((e.currentTarget as HTMLInputElement).files?.[0])} />
        <label htmlFor="imp-arq" className="hx-btn mc-largo">{lido ? "Escolher outro arquivo" : "Escolher arquivo .digilab"}</label>
        {lido && !erro && <p className="mc-ok"><b>{lido.arquivo}</b> · ✓ replay confere · registro válido</p>}
        {erro && <p className="mc-erro" role="alert">{erro}</p>}
        {msg && <p className="mc-ok" aria-live="polite">{msg}</p>}
      </section>
      {conflito && <section className="mc-bloco"><h3 className="mc-bloco__tit">Este pet já existe aqui, com outro registro</h3>
        <p>Mesma semente, histórias diferentes. Escolha qual fica. A outra não é apagada: vai para a espera.</p></section>}
      {conflito && lido && <div className="mc-imp__lados"><Lado titulo="Neste aparelho" m={conflito} /><Lado titulo="No arquivo" m={lido.m} sel /></div>}
      <div className="mc-linha">
        {conflito && <BotaoContinuar onClick={ficar}>Ficar com o arquivo</BotaoContinuar>}
        <BotaoHx onClick={sair}>{conflito ? "Cancelar" : msg ? "Pronto" : "Voltar"}</BotaoHx>
      </div>
    </div>
  );
  if (pagina) return <section aria-label="Importar pet" className="mc mc-imp-pagina">{corpo}</section>;
  return (
    <dialog className="importar-tela mc-dialogo" ref={ref} aria-label="Importar pet" onClose={fechar}>
      <PainelHx titulo="Importar pet" onFechar={sair} rotuloFechar="Fechar Importar pet">{corpo}</PainelHx>
    </dialog>
  );
}
