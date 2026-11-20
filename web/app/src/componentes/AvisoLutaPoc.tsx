/* O aviso do descarte 7 (LUTA_POC, LP2 e LP-6; decisao do Matheus de 2026-11-08): com a luta da POC ligada, os pets v13 a v19 (que lutavam
   pelo combate de antes) sairam. O aviso conta quantos pets sairam, oferece baixar o arquivo deles (o mesmo dos descartados) e leva a
   escolha do brasao do ovo novo. O Tamer (medalhas, itens, titulo, recordes) ficou. So aparece com a chave ligada (src/lutaPoc.ts). */
import { useEffect, useRef } from "react";
import { abrirEscolhaBrasao } from "../jornada.ts";
import { CHAVE_AVISO_POC, CHAVE_DESCARTADOS } from "../tamer.ts";
import { abrirModal } from "./modal.ts";
import { BotaoContinuar, BotaoHx } from "./hx/index.ts";
import { CabAberta } from "./CabAberta.tsx";
import "../estilo/abertas.css";

export interface AvisoPoc { pets: number; fabrica: number }
/** o aviso pendente (null: nenhum). Aviso ilegivel conta como um pet (o jogador ve o aviso, e ele sai ao fechar) */
export function avisoPocPendente(): AvisoPoc | null {
  try {
    const t = localStorage.getItem(CHAVE_AVISO_POC);
    if (t === null) return null;
    const d = JSON.parse(t) as Partial<AvisoPoc>;
    return { pets: Number(d.pets ?? 0), fabrica: Number(d.fabrica ?? 0) };
  } catch { return { pets: 1, fabrica: 0 }; }
}
function baixarDescartados(): void {
  const txt = localStorage.getItem(CHAVE_DESCARTADOS);
  if (txt === null) return;
  const url = URL.createObjectURL(new Blob([txt], { type: "application/json" })), a = document.createElement("a");
  a.href = url; a.download = "pets-antigos.json";
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function AvisoLutaPoc({ aviso, fechar }: { aviso: AvisoPoc; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  const temArquivo = (() => { try { return localStorage.getItem(CHAVE_DESCARTADOS) !== null; } catch { return false; } })();
  const sair = () => {
    try { localStorage.removeItem(CHAVE_AVISO_POC); } catch { /* sem armazenamento: o aviso volta na proxima abertura */ }
    fechar();
    if (aviso.pets) abrirEscolhaBrasao();
  };
  const { pets, fabrica } = aviso;
  return (
    <dialog className="brasao-tela conclusao-tela ab-hx dl med-aviso aviso-tr aviso-poc" ref={ref} aria-labelledby="apoc-tit" onCancel={e => e.preventDefault()} onClose={sair}>
      <CabAberta titulo="Aviso" />
      <div className="bv-texto">
        <h1 className="bv-tit cc-tit" id="apoc-tit">A luta agora é na arena</h1>
        <p className="bv-slogan">Seu pet luta sozinho, com o golpe e o tempo do Digimon dele, pelos stats que o treino e o cuidado sobem.</p>
        {pets > 0 && <p className="cc-texto">
          Os pets de antes lutavam de outro jeito e não abrem mais nesta versão do jogo: {pets === 1 ? "o pet que você tinha foi descartado" : `os ${pets} pets que você tinha (o ativo e os guardados) foram descartados`}.
          Você começa com um ovo novo. As suas medalhas, os itens, o título e os recordes ficam.
        </p>}
        {fabrica > 0 && <p className="cc-texto">
          {fabrica === 1 ? "A tentativa da Fábrica de antes saiu" : `As ${fabrica} tentativas da Fábrica de antes saíram`}, e o recorde da Fábrica recomeça.
        </p>}
        <div className="bv-pe">
          {temArquivo && <BotaoHx onClick={baixarDescartados}>Baixar o arquivo dos pets antigos</BotaoHx>}
          <BotaoContinuar className="bv-comecar" onClick={() => ref.current?.close()}>{pets ? "Escolher o brasão do ovo novo" : "Entendi"}</BotaoContinuar>
        </div>
      </div>
    </dialog>
  );
}
