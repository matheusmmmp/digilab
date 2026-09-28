/* Barra de navegacao dos 4 destinos (UI_GUIDELINES 7.12): embaixo no celular, coluna a partir de 900 px.
   Cada destino volta para a ultima aba aberta nele. */
import type { JSX } from "preact";
import { NOME_DESTINO, ORDEM_DESTINOS, type Destino } from "../rotas.ts";
import { NOME_TEMA, PROXIMO_TEMA, trocarTema, useTema, type Tema } from "../tema.ts";

const ICONE: Record<Destino, JSX.Element> = {
  pet: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 17c0-4 3-7 7-7s7 3 7 7c0 2-2 3-7 3s-7-1-7-3z" /><path d="M8 10.5 6.5 5 10 8M16 10.5 17.5 5 14 8" /><path d="M10 15h.01M14 15h.01" /></svg>,
  crescer: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21V11" /><path d="M12 11c0-4 3-6 7-6 0 4-3 6-7 6zM12 14c0-3-2-5-6-5 0 3 2 5 6 5z" /></svg>,
  lutar: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4l10 10M20 4 10 14" /><path d="M12 16l-3 3M12 16l3 3M7 17l-2 2M17 17l2 2" /></svg>,
  diario: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z" /><path d="M5 17a3 3 0 0 1 3-3h11M9 8h6" /></svg>,
};

const ICONE_TEMA: Record<Tema, JSX.Element> = {
  sistema: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" /><path d="M12 4a8 8 0 0 1 0 16z" fill="#FFFFFF" /></svg>,
  claro: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>,
  escuro: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z" /></svg>,
};
/** tema: Auto (o do sistema), Claro, Escuro; cada toque vai para o proximo */
function BotaoTema() {
  const tema = useTema();
  return (
    <button type="button" class="nav-tema" aria-label={`Tema: ${NOME_TEMA[tema]}. Tocar muda para ${NOME_TEMA[PROXIMO_TEMA[tema]]}`} onClick={trocarTema}>
      <span class="circ">{ICONE_TEMA[tema]}</span>{NOME_TEMA[tema]}
    </button>
  );
}

export function Nav({ atual, ir }: { atual: Destino; ir: (d: Destino) => void }) {
  return (
    <nav class="dl-nav" aria-label="Destinos">
      {ORDEM_DESTINOS.map(d => (
        <button type="button" key={d} aria-current={d === atual ? "page" : undefined} onClick={() => ir(d)}>
          <span class="circ">{ICONE[d]}</span>{NOME_DESTINO[d]}
        </button>
      ))}
      <BotaoTema />
    </nav>
  );
}
