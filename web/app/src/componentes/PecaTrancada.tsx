/* Uma peca trancada dentro de um lugar aberto (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.3 e P-4; prancha docs/pranchas/ux-lugares-menus/crescer_treinar_*, lutar_arena_*):
   o Forcar do treino (Nv 6) e as Regras de combate (Nv 6) ficam escondidos ate o Champion, sem tocar no motor: o mesmo botao, tracejado e apagado, com o cadeado e o
   "Nv N", e o marco que falta no balao (foco e hover) e no aria-label. O toque (e o clique) abre o cartao do motivo, como nos menus trancados; a frase tambem esta no balao (hover) e no nome acessivel. So vista. */
import { useId } from "react";
import { Lock } from "lucide-react";
import { ComDica } from "./Dica.tsx";
import { ICONE_PECA } from "./iconesNivel.ts";
import { PECAS, nivelDaPeca, type Peca } from "../nivel.ts";
import { abrirMotivo } from "../nivelTela.ts";
import "../estilo/nivel.css";

export function PecaTrancada({ peca, className }: { peca: Peca; className?: string }) {
  const d = PECAS[peca], I = ICONE_PECA[peca], id = useId(), n = nivelDaPeca(peca);
  return (
    <ComDica foco={false} idBalao={id} dica={d.motivo + "."} className={className}>
      <button type="button" className="fechado-trancado" aria-disabled="true" aria-label={`${d.nome}, trancado, Nv ${n}: ${d.motivo}`} onClick={() => abrirMotivo(peca)}>
        <I aria-hidden="true" /><span>{d.nome}</span><span className="nivel-nv" aria-hidden="true"><Lock />Nv {n}</span>
      </button>
    </ComDica>
  );
}
