/* Medalhas do Tamer na tela (docs/DESIGN_MEDALHAS_ARENAS.md): o selo (desenho original em SVG, sem asset de
   terceiros), usado na tela Medalhas, na Campanha e no Resultado; e o aviso da primeira abertura com medalhas (os pets
   antigos foram descartados). */
import { useEffect, useRef } from "react";
import { abrirEscolhaBrasao } from "../jornada.ts";
import { CHAVE_AVISO_V6 } from "../tamer.ts";
import { abrirModal } from "./modal.ts";
import { BotaoContinuar } from "./hx/index.ts";
import { CabAberta } from "./CabAberta.tsx";
import "../estilo/abertas.css";

/** selo da medalha n: ganha = cheio (azul de acao, numero branco); nao ganha = apagado e tracejado. O sentido vai
    tambem pela forma (cheio x tracejado) e pelo texto ao lado; o selo em si e decorativo */
export function SeloMedalha({ n, ganha, tam = 36, ouro = false }: { n: number; ganha: boolean; tam?: number; ouro?: boolean }) {
  /* ouro: a medalha do titulo da Liga dos Lideres (Fronteira, medalhas parte 4a), com uma estrela no lugar do numero */
  return (
    <svg className={`med-selo${ganha ? " ganha" : ""}${ouro ? " ouro" : ""}`} viewBox="0 0 36 44" width={tam} height={tam * 44 / 36} aria-hidden="true">
      <path className="med-fita" d="M9 2h7l-3 16H6zM20 2h7l3 16h-7z" />
      <circle className="med-disco" cx="18" cy="27" r="14" />
      <circle className="med-aro" cx="18" cy="27" r="10.5" />
      {ouro ? <path className="med-estrela" d="M18 19.5l2.3 4.7 5.2.8-3.8 3.6.9 5.1-4.6-2.4-4.6 2.4.9-5.1-3.8-3.6 5.2-.8z" />
        : <text x="18" y="32" textAnchor="middle">{n}</text>}
    </svg>
  );
}

/** primeira abertura depois das medalhas: os pets de antes (v1-v5) foram descartados (decisao do Matheus); o jogo
    comeca num ovo novo, com o Tamer sem medalhas. So sai escolhendo o brasao do ovo novo */
export function AvisoPetsDescartados({ n, fechar }: { n: number; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  const sair = () => {
    try { localStorage.removeItem(CHAVE_AVISO_V6); } catch { /* sem armazenamento: o aviso volta na proxima abertura */ }
    fechar(); abrirEscolhaBrasao();
  };
  return (
    <dialog className="brasao-tela conclusao-tela ab-hx dl med-aviso" ref={ref} aria-labelledby="mav-tit" onCancel={e => e.preventDefault()} onClose={sair}>
      <CabAberta titulo="Medalhas" />
      <div className="bv-centro">
        <div className="bv-palco med-aviso-palco" aria-hidden="true"><span className="bv-luz" /><span className="bv-anel" />
          <span className="med-aviso-selos">{[1, 2, 3].map(i => <SeloMedalha key={i} n={i} ganha={false} tam={44} />)}</span></div>
      </div>
      <div className="bv-texto">
        <h1 className="bv-tit cc-tit" id="mav-tit">Chegaram as medalhas</h1>
        <p className="bv-slogan">Agora você é o Tamer: as medalhas são suas e liberam as evoluções.</p>
        <p className="cc-texto">
          Para isso começar do zero, {n === 1 ? "o pet que você tinha foi descartado" : `os ${n} pets que você tinha (o ativo e os guardados) foram descartados`}.
          Você começa com um ovo novo e nenhuma medalha. Vença os líderes da campanha para ganhar medalhas:
          com 1 o Rookie vira Champion, com 3 o Champion vira Ultimate e com 5 o Ultimate vira Mega.
        </p>
        <div className="bv-pe">
          <BotaoContinuar className="bv-comecar" onClick={() => ref.current?.close()}>Escolher o brasão do ovo novo</BotaoContinuar>
        </div>
      </div>
    </dialog>
  );
}
