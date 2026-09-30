/* Escolha da carta antes da luta (itens, medalhas parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13): so pets v6 e so com carta no
   inventario do Tamer. A carta escolhida fica em LUTA.carta ate a luta que a usa (luta.lutarAnimado grava o evento "k" no registro do
   pet e a carta usada no do Tamer). */
import { CIT, ITENS, cartaDe } from "../../motor/index.ts";
import { tamerAtual, useJogo } from "../jogo.ts";
import { LUTA, avisarLuta, useLuta } from "../luta.ts";

export function EscolhaCarta() {
  const { motor: m } = useJogo(), luta = useLuta(), t = tamerAtual();
  if (m.versao < CIT.versaoPet || luta.rivalFixo) return null;
  const tem = ITENS.filter(x => x.tipo === "carta" && t.cartas(x.id) > 0);
  if (LUTA.carta && t.cartas(LUTA.carta) < 1) LUTA.carta = null;
  if (!tem.length) return null;
  return (
    <label class="carta-escolha">
      <span class="carta-escolha-rot">Carta para esta luta</span>
      <select value={luta.carta ?? ""} disabled={luta.lutando} onChange={e => { LUTA.carta = (e.currentTarget as HTMLSelectElement).value || null; avisarLuta(); }}>
        <option value="">Sem carta</option>
        {tem.map(c => <option key={c.id} value={c.id}>{c.nome} (×{t.cartas(c.id)})</option>)}
      </select>
      {luta.carta && <span class="carta-escolha-ef">{cartaDe(luta.carta).efeito}</span>}
    </label>
  );
}
