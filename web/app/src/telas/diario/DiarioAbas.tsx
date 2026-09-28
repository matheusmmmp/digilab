/* Abas do Diario no desenho AssetsDiario: dois tiles grandes do UP (Catalogo e Laboratorio = Cenarios) e a linha do
   Registro. Sao as proprias abas (tablist), nao um menu a mais; sem a decoracao, ficam os blocos com o texto. */
import { ESPECIES } from "../../../motor/index.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { ICONE } from "../../decoracao.ts";
import { useJogo } from "../../jogo.ts";
import type { Aba } from "../../rotas.ts";
import { formasVistas } from "./TelaCatalogo.tsx";

const TOTAL_FORMAS = ESPECIES.length * 15;
export function DiarioAbas({ aba, ir }: { aba: Aba; ir: (a: Aba) => void }) {
  const { motor: m } = useJogo(), vistas = formasVistas(m).size;
  const tab = (a: Aba) => ({ role: "tab" as const, "aria-selected": a === aba, onClick: () => ir(a) });
  return (
    <div class="diario-abas" role="tablist" aria-label="Abas do Diário">
      <button type="button" class="hub-tile" {...tab("catalogo")}>
        <Deco nome="Explore_Icon_Encyclopedia" />
        <span class="hub-tile-txt"><b>Catálogo</b><small>{vistas} de {TOTAL_FORMAS} vistas</small></span>
      </button>
      <button type="button" class="hub-tile" {...tab("cenarios")}>
        <Deco nome="Explore_Icon_DGame" />
        <span class="hub-tile-txt"><b>Laboratório</b><small>cenários de pesquisa</small></span>
      </button>
      <button type="button" class="hub-linha" {...tab("registro")}>
        <Deco nome={ICONE.registro} class="hub-linha-ic" />
        <span><b>Registro</b><small>tudo o que aconteceu, dia a dia</small></span>
      </button>
    </div>
  );
}
