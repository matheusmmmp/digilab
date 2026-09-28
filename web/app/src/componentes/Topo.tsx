/* Topo da casca do desktop (DIRETRIZES_REPLICAR secao 6; pranchas *Desktop): barra de 76 px quadriculada com o titulo
   (Rubik 30), as abas em pilula e, a direita, o mini-card do pet: retrato de 44 px (abre Meus pets), nome, brasao,
   nivel, dia e relogio com "salvo". So aparece a partir de 1100 px; abaixo, cada tela usa o proprio cabecalho. */
import { DO_ESP, NOME_ESP, NOME_EST, nomeEstagio, nomeForma } from "../../motor/index.ts";
import { BRASAO } from "../decoracao.ts";
import { useJogo } from "../jogo.ts";
import { NOME_ABA, type Aba } from "../rotas.ts";
import { Retrato, diaDe, hhmm } from "../telas/pet/TelaPet.tsx";
import { Deco } from "./Deco.tsx";

export function TopoDesktop({ titulo, abas, aba, irAba, abrirMeusPets, voltar }: {
  titulo: string; abas: readonly Aba[]; aba: Aba | null; irAba: (a: Aba) => void; abrirMeusPets: () => void; voltar?: () => void;
}) {
  const { motor: m, nascendo, erroSave } = useJogo(), ovo = nascendo > 0, e = m.e;
  return (
    <header class="topo-desk dl-faixa">
      <Deco nome="TopDeco_Earth2_0" largura={210} altura={210} class="topo-globo" />
      {voltar && <button type="button" class="topo-voltar" aria-label="Voltar ao Pet" onClick={voltar}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M12 4 6 10l6 6" /></svg></button>}
      <h1 class="dl-num topo-tit">{titulo}</h1>
      {abas.length > 1 && (
        <div class="topo-abas" role="tablist" aria-label={`Abas de ${titulo}`}>
          {abas.map(a => <button type="button" role="tab" key={a} class="topo-aba" aria-selected={a === aba} onClick={() => irAba(a)}>{NOME_ABA[a]}</button>)}
        </div>
      )}
      <div class="topo-pet">
        <button type="button" class="topo-retrato" aria-haspopup="dialog" aria-label="Meus pets" onClick={abrirMeusPets}><Retrato m={m} ovo={ovo} /></button>
        <span class="topo-pet-txt">
          <span class="topo-pet-nome"><b>{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</b>
            <Deco nome={BRASAO[m.especie].peca} largura={30} altura={20} alt={NOME_ESP[m.especie]} /></span>
          <span class="topo-pet-sub"><span class="dl-tag dl-tag--estagio">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</span>dia {diaDe(e.tick)}</span>
        </span>
        <span class="topo-relogio">
          <span class="dl-num" aria-label={`${hhmm(e.tick)}, dia ${diaDe(e.tick)}`}>{hhmm(e.tick)}</span>
          <span class={`pet-salvo${erroSave ? " erro" : ""}`}><i aria-hidden="true" />{erroSave ? "não salva" : "salvo"}</span>
        </span>
      </div>
    </header>
  );
}
