/* O aviso do descarte 6 (COMBATE-TR, etapa R2; E2 e D-4, decisoes do Matheus de 2026-10-29): a luta virou tempo real nos pets v13, e os
   pets de antes (v1-v12, com o combate por turnos) sairam. O aviso conta quantos pets e quantas tentativas da Fabrica sairam, oferece
   baixar o arquivo dos pets descartados (o mesmo .digilab de Exportar, um por pet, num arquivo so) e leva a escolha do brasao do ovo novo.
   O Tamer (medalhas, itens, titulo, recordes das instalacoes) ficou. */
import { useEffect, useRef } from "react";
import { abrirEscolhaBrasao } from "../jornada.ts";
import { CHAVE_AVISO_TR, CHAVE_DESCARTADOS } from "../tamer.ts";
import { abrirModal } from "./modal.ts";

export interface AvisoTR { pets: number; fabrica: number }
/** o aviso pendente (null: nenhum). Aviso ilegivel conta como um pet (o jogador ve o aviso, e ele sai ao fechar) */
export function avisoTRPendente(): AvisoTR | null {
  try {
    const t = localStorage.getItem(CHAVE_AVISO_TR);
    if (t === null) return null;
    const d = JSON.parse(t) as Partial<AvisoTR>;
    return { pets: Number(d.pets ?? 0), fabrica: Number(d.fabrica ?? 0) };
  } catch { return { pets: 1, fabrica: 0 }; }
}
/** baixa os saves descartados num arquivo so (JSON: a lista de {semente, log, versao}) */
function baixarDescartados(): void {
  const txt = localStorage.getItem(CHAVE_DESCARTADOS);
  if (txt === null) return;
  const url = URL.createObjectURL(new Blob([txt], { type: "application/json" })), a = document.createElement("a");
  a.href = url; a.download = "pets-antigos-combate-por-turnos.json";
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function AvisoCombateTR({ aviso, fechar }: { aviso: AvisoTR; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  const temArquivo = (() => { try { return localStorage.getItem(CHAVE_DESCARTADOS) !== null; } catch { return false; } })();
  const sair = () => {
    try { localStorage.removeItem(CHAVE_AVISO_TR); } catch { /* sem armazenamento: o aviso volta na proxima abertura */ }
    fechar();
    if (aviso.pets) abrirEscolhaBrasao();
  };
  const { pets, fabrica } = aviso;
  return (
    <dialog className="brasao-tela conclusao-tela dl med-aviso aviso-tr" ref={ref} aria-labelledby="atr-tit" onCancel={e => e.preventDefault()} onClose={sair}>
      <div className="bv-texto">
        <h1 className="bv-tit cc-tit" id="atr-tit">A luta agora é em tempo real</h1>
        <p className="bv-slogan">Seu pet luta sozinho, pelas regras que aprendeu. Você ensina as regras entre as lutas.</p>
        {pets > 0 && <p className="cc-texto">
          Os pets de antes lutavam por turnos e não abrem mais nesta versão do jogo: {pets === 1 ? "o pet que você tinha foi descartado" : `os ${pets} pets que você tinha (o ativo e os guardados) foram descartados`}.
          Você começa com um ovo novo. As suas medalhas, os itens, o título e os recordes ficam.
        </p>}
        {fabrica > 0 && <p className="cc-texto">
          {fabrica === 1 ? "A tentativa da Fábrica de antes saiu" : `As ${fabrica} tentativas da Fábrica de antes saíram`}, e o recorde da Fábrica recomeça.
        </p>}
        <div className="bv-pe">
          {temArquivo && <button type="button" className="dl-btn" onClick={baixarDescartados}>Baixar o arquivo dos pets antigos</button>}
          <button type="button" className="dl-btn dl-btn--destaque bv-comecar" onClick={() => ref.current?.close()}>{pets ? "Escolher o brasão do ovo novo" : "Entendi"}</button>
        </div>
      </div>
    </dialog>
  );
}
