/* Medalhas do Tamer na tela (docs/DESIGN_MEDALHAS_ARENAS.md): o selo (desenho original em SVG, sem asset de
   terceiros), usado na tela Medalhas, na Campanha e no Resultado; e o aviso da primeira abertura com medalhas (os pets
   antigos foram descartados). */
import { useEffect, useRef } from "preact/hooks";
import { abrirEscolhaBrasao } from "../jornada.ts";
import { CHAVE_AVISO_V6 } from "../tamer.ts";
import { abrirModal } from "./modal.ts";

/** selo da medalha n: ganha = cheio (azul de acao, numero branco); nao ganha = apagado e tracejado. O sentido vai
    tambem pela forma (cheio x tracejado) e pelo texto ao lado; o selo em si e decorativo */
export function SeloMedalha({ n, ganha, tam = 36 }: { n: number; ganha: boolean; tam?: number }) {
  return (
    <svg class={`med-selo${ganha ? " ganha" : ""}`} viewBox="0 0 36 44" width={tam} height={tam * 44 / 36} aria-hidden="true">
      <path class="med-fita" d="M9 2h7l-3 16H6zM20 2h7l3 16h-7z" />
      <circle class="med-disco" cx="18" cy="27" r="14" />
      <circle class="med-aro" cx="18" cy="27" r="10.5" />
      <text x="18" y="32" text-anchor="middle">{n}</text>
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
    <dialog class="brasao-tela conclusao-tela dl med-aviso" ref={ref} aria-labelledby="mav-tit" onCancel={e => e.preventDefault()} onClose={sair}>
      <div class="bv-centro">
        <div class="bv-palco med-aviso-palco" aria-hidden="true"><span class="bv-luz" /><span class="bv-anel" />
          <span class="med-aviso-selos">{[1, 2, 3].map(i => <SeloMedalha key={i} n={i} ganha={false} tam={44} />)}</span></div>
      </div>
      <div class="bv-texto">
        <h1 class="bv-tit cc-tit" id="mav-tit">Chegaram as medalhas</h1>
        <p class="bv-slogan">Agora você é o Tamer: as medalhas são suas e liberam as evoluções.</p>
        <p class="cc-texto">
          Para isso começar do zero, {n === 1 ? "o pet que você tinha foi descartado" : `os ${n} pets que você tinha (o ativo e os guardados) foram descartados`}.
          Você começa com um ovo novo e nenhuma medalha. Vença os líderes da campanha para ganhar medalhas:
          com 1 o Rookie vira Champion, com 3 o Champion vira Ultimate e com 5 o Ultimate vira Mega.
        </p>
        <div class="bv-pe">
          <button type="button" class="dl-btn dl-btn--destaque bv-comecar" onClick={() => ref.current?.close()}>Escolher o brasão do ovo novo</button>
        </div>
      </div>
    </dialog>
  );
}
