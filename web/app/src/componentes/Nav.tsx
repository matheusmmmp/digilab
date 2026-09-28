/* Barra de navegacao dos 4 destinos (UI_GUIDELINES 7.12): embaixo no celular, coluna a partir de 900 px.
   Cada destino volta para a ultima aba aberta nele. */
import type { JSX } from "preact";
import { OVO } from "../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../atlas.ts";
import { Deco } from "../decoracao.tsx";
import { useJogo } from "../jogo.ts";
import { NOME_DESTINO, ORDEM_DESTINOS, type Destino } from "../rotas.ts";

/* icones das pranchas PetTela/PetTelaDesktop: o ovo da especie (Pet), o haltere do guia de crescimento (Crescer), espadas
   (Lutar), o chip (Diario), o rosto (Conversar, pedido do Matheus) e a engrenagem (Configuracoes, quadrada e no fim). Sem
   atlas ou decoracao: os desenhos em traco de reserva. */
const EMOTE: Partial<Record<Destino, string>> = { lutar: "emoji_espadas", conversar: "emoji_feliz" };
const DECO: Partial<Record<Destino, [string, number, number]>> = { crescer: ["Growth_Guide_Icon_07", 26, 25], diario: ["Growth_Guide_Icon_09", 18, 24], config: ["Common_Icon_Setting", 24, 24] };
function IconeDestino({ d }: { d: Destino }) {
  const a = useAtlas(), { motor: m } = useJogo();
  if (DECO[d]) { const [n, w, h] = DECO[d]!; return <Deco nome={n} w={w} h={h} reserva={ICONE[d]} />; }
  if (a.tipo !== "ok") return ICONE[d];
  if (d === "pet") { const o = imagemAtlas(a, OVO[m.especie]); return <img class="nav-ovo" src={o.url} width={19} height={26} alt="" />; }
  const e = imagemAtlas(a, EMOTE[d]!, 2);
  return <img class="dl-pix" src={e.url} width={e.w} height={e.h} alt="" />;
}
const ICONE: Record<Destino, JSX.Element> = {
  pet: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 17c0-4 3-7 7-7s7 3 7 7c0 2-2 3-7 3s-7-1-7-3z" /><path d="M8 10.5 6.5 5 10 8M16 10.5 17.5 5 14 8" /><path d="M10 15h.01M14 15h.01" /></svg>,
  crescer: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21V11" /><path d="M12 11c0-4 3-6 7-6 0 4-3 6-7 6zM12 14c0-3-2-5-6-5 0 3 2 5 6 5z" /></svg>,
  lutar: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4l10 10M20 4 10 14" /><path d="M12 16l-3 3M12 16l3 3M7 17l-2 2M17 17l2 2" /></svg>,
  diario: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z" /><path d="M5 17a3 3 0 0 1 3-3h11M9 8h6" /></svg>,
  conversar: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H10l-4 4v-4H4z" /></svg>,
  config: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3" /><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" /></svg>,
};

export function Nav({ atual, ir }: { atual: Destino; ir: (d: Destino) => void }) {
  return (
    <nav class="dl-nav" aria-label="Destinos">
      {ORDEM_DESTINOS.filter(d => d !== "config").map(d => (
        <button type="button" key={d} aria-current={d === atual ? "page" : undefined} onClick={() => ir(d)}>
          <span class="circ"><IconeDestino d={d} /></span>{NOME_DESTINO[d]}
        </button>
      ))}
      <button type="button" class="nav-config" aria-label="Configurações" aria-current={atual === "config" ? "page" : undefined} onClick={() => ir("config")}>
        <span class="circ"><IconeDestino d="config" /></span>
      </button>
    </nav>
  );
}
