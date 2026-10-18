/* Topo da casca do desktop (TAREFA_V2_UI_DESKTOP, 2026-10-18; antes: pranchas *Desktop). Duas partes, so a partir de 1100 px:
   - o cabecalho fixo de 64 px, claro, em toda a largura: a marca, o relogio do jogo com o "salvo" e o mini-card do pet
     (retrato de 40 px, que abre Meus pets; nome, brasao e nivel);
   - a linha da pagina, no comeco do conteudo: Voltar, o titulo, as abas e os botoes da tela. A tela do Pet nao tem essa linha
     (semTitulo): o habitat ja e o assunto.
   Abaixo de 1100 px nada disto aparece; cada tela usa o proprio cabecalho. */
import type { ComponentChildren } from "preact";
import { DO_ESP, NOME_ESP, NOME_EST, nomeEstagio, nomeForma } from "../../motor/index.ts";
import { BRASAO } from "../decoracao.ts";
import { useJogo } from "../jogo.ts";
import { NOME_ABA, type Aba } from "../rotas.ts";
import { Retrato, diaDe, hhmm } from "../telas/pet/TelaPet.tsx";
import { Deco } from "./Deco.tsx";

/* a marca: um frasco de laboratorio em pixel (desenho proprio, 10 x 10) e o nome */
const FRASCO = (
  <svg class="topo-frasco" viewBox="0 0 10 10" width="30" height="30" aria-hidden="true" shape-rendering="crispEdges">
    <path fill="var(--ui-navy)" d="M3 0h4v1H3zM4 1h2v3H4zM3 4h1v1H3zM6 4h1v1H6zM2 5h1v1H2zM7 5h1v1H7zM1 6h1v3H1zM8 6h1v3H8zM2 9h6v1H2z" />
    <path fill="var(--ui-primary)" d="M2 7h6v2H2zM3 6h4v1H3z" />
    <path fill="#FFFFFF" d="M3 7h1v1H3zM6 8h1v1H6z" />
  </svg>
);

export function TopoDesktop({ titulo, abas, aba, irAba, abrirMeusPets, voltar, acoes, semTitulo }: {
  titulo: string; abas: readonly Aba[]; aba: Aba | null; irAba: (a: Aba) => void; abrirMeusPets: () => void; voltar?: () => void;
  acoes?: ComponentChildren;          /* botoes da tela, na linha da pagina (MpListaDesktop: Novo ovo) */
  semTitulo?: boolean;                /* a tela do Pet: so o cabecalho, sem a linha da pagina */
}) {
  const { motor: m, nascendo, erroSave } = useJogo(), ovo = nascendo > 0, e = m.e;
  return <>
    <header class="topo-desk">
      <span class="topo-marca">{FRASCO}<b>Digi<span>Lab</span></b></span>
      <span class="topo-relogio" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}`}>
        <span class="topo-hora">{hhmm(e.tick)}</span><span class="topo-dia">dia {diaDe(e.tick)}</span>
        <span class={`pet-salvo${erroSave ? " erro" : ""}`}><i aria-hidden="true" />{erroSave ? "não salva" : "salvo"}</span>
      </span>
      <div class="topo-pet">
        <button type="button" class="topo-retrato" aria-haspopup="dialog" aria-label="Meus pets" onClick={abrirMeusPets}><Retrato m={m} ovo={ovo} /></button>
        <span class="topo-pet-txt">
          <span class="topo-pet-nome"><b>{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b>
            <Deco nome={BRASAO[m.especie].peca} largura={24} altura={16} alt={NOME_ESP[m.especie]} /></span>
          <span class="topo-pet-sub"><span class="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span></span>
        </span>
      </div>
    </header>
    {!semTitulo && (
      <div class="topo-pagina">
        {voltar && <button type="button" class="topo-voltar" aria-label="Voltar ao Pet" onClick={voltar}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M12 4 6 10l6 6" /></svg></button>}
        <h1 class="topo-tit">{titulo}</h1>
        {abas.length > 1 && (
          <div class="topo-abas" role="tablist" aria-label={`Abas de ${titulo}`}>
            {abas.map(a => <button type="button" role="tab" key={a} class="topo-aba" aria-selected={a === aba} onClick={() => irAba(a)}>{NOME_ABA[a]}</button>)}
          </div>
        )}
        {acoes && <div class="topo-acoes">{acoes}</div>}
      </div>
    )}
  </>;
}
