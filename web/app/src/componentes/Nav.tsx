/* Navegacao da casca (docs/TAREFA_V2_LAYOUT_HABITAT.md, M2; pele hx-*): a partir de 900 px, um trilho estreito de icones a esquerda
   (Pet, Crescer, Lutar, Diario e, no pe, Conversar e Ajustes); abaixo de 900 px, a barra embaixo com os 4 destinos (Conversar e
   Ajustes ficam no cabecalho, Topo.tsx). Cada destino volta para a ultima aba aberta nele. O rotulo fica sempre visivel (nada so no
   hover) e o `aria-current` marca o destino aberto. */
import { BookOpen, MessageCircle, PawPrint, Settings, Sprout, Swords, type LucideIcon } from "lucide-react";
import { NOME_DESTINO, ORDEM_DESTINOS, type Destino } from "../rotas.ts";

const DESTINOS_BARRA = ORDEM_DESTINOS.filter(d => d !== "conversar");
const ICONE: Record<Destino, LucideIcon> = { pet: PawPrint, crescer: Sprout, lutar: Swords, diario: BookOpen, conversar: MessageCircle };

export function Nav({ atual, ir, configAberta, abrirConfig }: { atual: Destino | null; ir: (d: Destino) => void; configAberta: boolean; abrirConfig: () => void }) {
  return (
    <nav className="dl-nav hx-nav" aria-label="Destinos">
      {DESTINOS_BARRA.map(d => {
        const I = ICONE[d];
        return (
          <button type="button" key={d} className="hx-nav__bt" aria-current={d === atual ? "page" : undefined} onClick={() => ir(d)}>
            <I className="hx-nav__ic" aria-hidden="true" /><span className="hx-nav__rot">{NOME_DESTINO[d]}</span>
          </button>
        );
      })}
      <span className="nav-pe">
        <button type="button" className="nav-quad hx-nav__bt" aria-current={atual === "conversar" ? "page" : undefined} onClick={() => ir("conversar")}>
          <MessageCircle className="hx-nav__ic" aria-hidden="true" /><span className="hx-nav__rot">Conversar</span>
        </button>
        <button type="button" className="nav-quad hx-nav__bt" aria-current={configAberta ? "page" : undefined} onClick={abrirConfig}>
          <Settings className="hx-nav__ic" aria-hidden="true" /><span className="hx-nav__rot">Ajustes</span>
        </button>
      </span>
    </nav>
  );
}
