/* Escolha da carta antes da luta (itens, medalhas parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13): so pets v6 e so com carta no
   inventario do Tamer. A carta escolhida fica em LUTA.carta ate a luta que a usa (luta.lutarAnimado grava o evento "k" no registro do
   pet e a carta usada no do Tamer). Nos pets v9 (rodada de equilibrio geral, fase 3) a carta so vale contra os NPCs da campanha e com o
   treino minimo (Motor.porqueSemCartaV9): fora disso a escolha some e fica a frase do porque. */
import { CIT, ITENS, cartaDe } from "../../motor/index.ts";
import { tamerAtual, useJogo } from "../jogo.ts";
import { LUTA, avisarLuta, useLuta } from "../luta.ts";

export function EscolhaCarta({ rival }: { rival: string | null }) {
  const { motor: m } = useJogo(), luta = useLuta(), t = tamerAtual();
  if (luta.rivalFixo) return null;
  const tem = ITENS.filter(x => x.tipo === "carta" && t.cartas(x.id) > 0);
  if (LUTA.carta && t.cartas(LUTA.carta) < 1) LUTA.carta = null;
  if (!tem.length) return null;
  const semCarta = rival ? m.porqueSemCartaV9(rival) : null;
  if (semCarta) { if (LUTA.carta) LUTA.carta = null; return <p className="dl-apoio carta-escolha-sem">Sem carta nesta luta: {semCarta}.</p>; }
  return (
    <label className="carta-escolha">
      <span className="carta-escolha-rot">Carta para esta luta</span>
      <select value={luta.carta ?? ""} disabled={luta.lutando} onChange={e => { LUTA.carta = (e.currentTarget as HTMLSelectElement).value || null; avisarLuta(); }}>
        <option value="">Sem carta</option>
        {tem.map(c => <option key={c.id} value={c.id}>{c.nome} (×{t.cartas(c.id)})</option>)}
      </select>
      {luta.carta && <span className="carta-escolha-ef">{cartaDe(luta.carta).efeito}</span>}
    </label>
  );
}
