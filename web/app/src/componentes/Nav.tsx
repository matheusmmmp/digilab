/* Navegacao da casca (docs/TAREFA_V2_LAYOUT_HABITAT.md, M2; pele hx-*): a partir de 900 px, um trilho estreito de icones a esquerda
   (Pet, Crescer, Lutar, Diario e, no pe, Conversar e Ajustes); abaixo de 900 px, a barra embaixo com os 4 destinos (Conversar e
   Ajustes ficam no cabecalho, Topo.tsx). Cada destino volta para a ultima aba aberta nele. O rotulo fica sempre visivel (nada so no
   hover) e o `aria-current` marca o destino aberto. */
import { BookOpen, Lock, MessageCircle, PawPrint, Settings, Sprout, Swords, type LucideIcon } from "lucide-react";
import { NOME_DESTINO, ORDEM_DESTINOS, type Destino } from "../rotas.ts";
import { dAbreDiario } from "../atalhosLugar.ts";
import { useHabitat } from "../habitat.ts";
import { useNivel } from "../nivelTela.ts";
import { PECAS, nivelDaPeca, pecaAberta, pecaDoDestino } from "../nivel.ts";
import "../estilo/nivel.css";

const DESTINOS_BARRA = ORDEM_DESTINOS.filter(d => d !== "conversar");
const ICONE: Record<Destino, LucideIcon> = { pet: PawPrint, crescer: Sprout, lutar: Swords, diario: BookOpen, conversar: MessageCircle };

export function Nav({ atual, ir, configAberta, abrirConfig }: { atual: Destino | null; ir: (d: Destino) => void; configAberta: boolean; abrirConfig: () => void }) {
  useHabitat();         // o D so e atalho do Diario com a camera que nao solta (atalhosLugar.ts): a escolha do controle muda a declaracao
  const nivel = useNivel();
  /* um menu trancado (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.4): o icone igual, apagado, com o cadeado; o nome acessivel diz o nivel e o marco, e o toque
     abre o cartao do motivo (App.tsx, `ir`), nao o painel */
  const trava = (d: Destino) => {
    const p = pecaDoDestino(d);
    return p && !pecaAberta(nivel, p) ? { classe: " hx-nav__bt--trancado", props: { "aria-disabled": true as const, "aria-label": `${NOME_DESTINO[d]}, trancado, Nv ${nivelDaPeca(p)}: ${PECAS[p].motivo}`, title: PECAS[p].motivo }, cadeado: <Lock className="nav-cad" aria-hidden="true" /> } : null;
  };
  return (
    <nav className="dl-nav hx-nav" aria-label="Destinos">
      {DESTINOS_BARRA.map(d => {
        const I = ICONE[d], t = trava(d);
        return (
          <button type="button" key={d} className={"hx-nav__bt" + (t?.classe ?? "")} {...t?.props} aria-current={d === atual ? "page" : undefined} aria-keyshortcuts={d === "crescer" ? "C" : d === "lutar" ? "L" : d === "diario" && (dAbreDiario() || atual !== null && atual !== "pet") ? "D" : undefined} onClick={() => ir(d)}>
            <I className="hx-nav__ic" aria-hidden="true" /><span className="hx-nav__rot">{NOME_DESTINO[d]}</span>{t?.cadeado}
          </button>
        );
      })}
      <span className="nav-pe">
        <button type="button" className={"nav-quad hx-nav__bt" + (trava("conversar")?.classe ?? "")} {...trava("conversar")?.props} aria-current={atual === "conversar" ? "page" : undefined} onClick={() => ir("conversar")}>
          <MessageCircle className="hx-nav__ic" aria-hidden="true" /><span className="hx-nav__rot">Conversar</span>{trava("conversar")?.cadeado}
        </button>
        <button type="button" className="nav-quad hx-nav__bt" aria-current={configAberta ? "page" : undefined} onClick={abrirConfig}>
          <Settings className="hx-nav__ic" aria-hidden="true" /><span className="hx-nav__rot">Ajustes</span>
        </button>
      </span>
    </nav>
  );
}
