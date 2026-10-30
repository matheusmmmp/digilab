/* Topo flutuante da casca (docs/TAREFA_V2_LAYOUT_HABITAT.md, M2), por cima do habitat em toda rota menos a luta em tela cheia: o retrato
   do pet (abre Meus pets), o logo, o relogio do jogo com o aviso de salvo e, so abaixo de 900 px, Conversar e Ajustes. O retrato, o
   relogio e o visual deles seguem nos tokens --dl-* (tema claro); a pele hx-* e so dos menus. */
import { MessageCircle, Moon, Settings, Sun } from "lucide-react";
import { DO_ESP, NOME_ESP, NOME_EST, TPD, eNoite, nomeEstagio, nomeForma } from "../../motor/index.ts";
import { BRASAO } from "../decoracao.ts";
import { useJogo } from "../jogo.ts";
import { Retrato, diaDe, hhmm } from "../telas/pet/TelaPet.tsx";
import { Deco } from "./Deco.tsx";

export function TopoHabitat({ abrirMeusPets, irConversar, abrirConfig }: { abrirMeusPets: () => void; irConversar: () => void; abrirConfig: () => void }) {
  const { motor: m, nascendo, erroSave } = useJogo(), ovo = nascendo > 0, e = m.e, noite = eNoite(e.tick % TPD);
  return (
    <header className="topo-hab">
      <div className="topo-pet">
        <button type="button" className="topo-retrato" aria-haspopup="dialog" aria-label="Meus pets" onClick={abrirMeusPets}><Retrato m={m} ovo={ovo} /></button>
        <span className="topo-pet-txt">
          <span className="topo-pet-nome"><b>{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b></span>
          <span className="topo-pet-sub"><span className="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>
            <span aria-hidden="true">·</span><Deco nome={BRASAO[m.especie].peca} largura={20} altura={13} alt="" />{NOME_ESP[m.especie]}</span>
        </span>
      </div>
      <b className="topo-logo dl-num" aria-hidden="true">DIGILAB</b>
      <span className="topo-relogio" role="group" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}`}>
        {noite ? <Moon className="topo-sol" aria-hidden="true" /> : <Sun className="topo-sol" aria-hidden="true" />}
        <span className="topo-hora-txt"><span className="topo-dia">dia {diaDe(e.tick)}</span><span className="topo-hora">{hhmm(e.tick)}</span></span>
        <span className={`pet-salvo${erroSave ? " erro" : ""}`}><i aria-hidden="true" />{erroSave ? "não salva" : "salvo"}</span>
      </span>
      <span className="topo-bts">
        <button type="button" className="topo-bt" aria-label="Conversar" onClick={irConversar}><MessageCircle aria-hidden="true" /></button>
        <button type="button" className="topo-bt" aria-label="Configurações" onClick={abrirConfig}><Settings aria-hidden="true" /></button>
      </span>
    </header>
  );
}
