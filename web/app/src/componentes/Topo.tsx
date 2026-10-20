/* Topo da casca do desktop (docs/TAREFA_V2_MOLDURA_DESKTOP.md, prancha TelasLayoutDesktop; antes, TAREFA_V2_UI_DESKTOP), so a partir de
   1100 px: uma linha fixa a direita da barra lateral, com
   - a esquerda, as abas da tela (a ativa sublinhada); a tela sem abas mostra o titulo como a aba ativa; o Voltar, quando a tela tem;
   - os botoes da tela (MpListaDesktop: Novo ovo);
   - a direita, o relogio do jogo (sol de dia, lua de noite, o dia e a hora), o "salvo" e o pet: retrato (abre Meus pets), nome, nivel
     e brasao.
   O logo fica no alto da barra lateral (Nav). Abaixo de 1100 px nada disto aparece; cada tela usa o proprio cabecalho. */
import type { ReactNode } from "react";
import { ChevronLeft, Moon, Sun } from "lucide-react";
import { DO_ESP, NOME_ESP, NOME_EST, TPD, eNoite, nomeEstagio, nomeForma } from "../../motor/index.ts";
import { BRASAO } from "../decoracao.ts";
import { useJogo } from "../jogo.ts";
import { NOME_ABA, type Aba } from "../rotas.ts";
import { Retrato, diaDe, hhmm } from "../telas/pet/TelaPet.tsx";
import { Deco } from "./Deco.tsx";

export function TopoDesktop({ titulo, abas, aba, irAba, abrirMeusPets, voltar, acoes }: {
  titulo: string; abas: readonly Aba[]; aba: Aba | null; irAba: (a: Aba) => void; abrirMeusPets: () => void; voltar?: () => void;
  acoes?: ReactNode;          /* botoes da tela (MpListaDesktop: Novo ovo) */
}) {
  const { motor: m, nascendo, erroSave } = useJogo(), ovo = nascendo > 0, e = m.e, noite = eNoite(e.tick % TPD);
  return (
    <header className="topo-desk">
      <div className="topo-esq">
        {voltar && <button type="button" className="topo-voltar" onClick={voltar}><ChevronLeft size={18} aria-hidden="true" />Voltar ao Pet</button>}
        {abas.length > 1 ? <>
          <h1 className="sr-only">{titulo}</h1>
          <div className="topo-abas" role="tablist" aria-label={`Abas de ${titulo}`}>
            {abas.map(a => <button type="button" role="tab" key={a} className="topo-aba" aria-selected={a === aba} onClick={() => irAba(a)}>{NOME_ABA[a]}</button>)}
          </div>
        </> : <h1 className="topo-tit">{titulo}</h1>}
      </div>
      {acoes && <div className="topo-acoes">{acoes}</div>}
      <span className="topo-relogio" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}`}>
        {noite ? <Moon className="topo-sol" aria-hidden="true" /> : <Sun className="topo-sol" aria-hidden="true" />}
        <span className="topo-hora-txt"><span className="topo-dia">dia {diaDe(e.tick)}</span><span className="topo-hora">{hhmm(e.tick)}</span></span>
        <span className={`pet-salvo${erroSave ? " erro" : ""}`}><i aria-hidden="true" />{erroSave ? "não salva" : "salvo"}</span>
      </span>
      <span className="topo-sep" aria-hidden="true" />
      <div className="topo-pet">
        <button type="button" className="topo-retrato" aria-haspopup="dialog" aria-label="Meus pets" onClick={abrirMeusPets}><Retrato m={m} ovo={ovo} /></button>
        <span className="topo-pet-txt">
          <span className="topo-pet-nome"><b>{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b></span>
          <span className="topo-pet-sub"><span className="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>
            <span aria-hidden="true">·</span><Deco nome={BRASAO[m.especie].peca} largura={20} altura={13} alt="" />{NOME_ESP[m.especie]}</span>
        </span>
      </div>
    </header>
  );
}
