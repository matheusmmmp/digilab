/* Crescer · Itens (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13): o inventario do Tamer (chips e cartas, do registro
   dele, src/tamer.ts) e os chips equipados no pet ativo (eventos "i" do registro do pet). Equipar e desequipar gravam no registro do
   pet; o motor confere vagas, estagio e lista, e esta tela so oferece o que o Tamer tem. As cartas se escolhem antes da luta (Campanha
   e Arena). Itens sem equilibrio: numeros PROPOSTOS (secao 13). Nos pets v9 (rodada de equilibrio geral, fase 3; itens.ts) os itens pedem
   o treino minimo do nivel, a carta so vale na Campanha, o chip de regra vai para o fim da lista e o de stat vale metade: a tela diz isso. */
import { useState } from "react";
import {
  CARTA_DA_REVANCHE, CIT, CIT_V9, ITENS, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHA_POR_ID, NOME_STAT, NPC, STATS, estagioMinimo, nomeForma, rotuloRegra,
  type Item, type Motor, type Stat,
} from "../../../motor/index.ts";
import { mudarMotor, tamerAtual, useJogo } from "../../jogo.ts";
import { comoGanhar, noLugar, type Tamer } from "../../tamer.ts";

const TIPO: Record<Item["tipo"], string> = { chip_stat: "chip de stat", chip_regra: "chip de regra", carta: "carta" };
const NIVEL: Record<string, string> = { crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };
const dec1 = (x: number): string => x.toFixed(1).replace(".", ",").replace(/,0$/, "");

/** de onde o item vem: a medalha que o da, ou as revanches que dao a carta */
export function deOnde(it: Item): string {
  if (it.tipo === "carta") {
    const ls = Object.entries(CARTA_DA_REVANCHE).filter(([, c]) => c === it.id).map(([md]) => MEDALHA_POR_ID[md]);
    return "revanche vencida contra " + ls.map(md => `o ${NPC[md.lider]!.nome} ${noLugar(LUGARES_V6[md.lugar].nome)}`).join(" ou ");
  }
  const md = MEDALHA_POR_ID[Object.entries(ITEM_DA_MEDALHA).find(([, c]) => c === it.id)![0]];
  return `vem com a ${md.nome}`;
}
/** o que os chips de stat somam agora no pet (pontos de treino na luta, alem do treino dele) */
function somaAgora(m: Motor): Partial<Record<Stat, number>> {
  const p = m.pontosDeLuta(), t = m.treino.pontos;
  return p ? Object.fromEntries(STATS.map(k => [k, p[k] - t[k]]).filter(([, v]) => (v as number) > 1e-9)) : {};
}

function CardChip({ it, m, t, agir }: { it: Item & { tipo: "chip_stat" | "chip_regra" }; m: Motor; t: Tamer; agir: (op: "equipar" | "desequipar", id: string) => void }) {
  const tem = t.temChip(it.id), eq = m.chips.includes(it.id), md = MEDALHA_POR_ID[Object.entries(ITEM_DA_MEDALHA).find(([, c]) => c === it.id)![0]];
  const porque = tem && !eq ? m.porqueNaoEquipa(it.id) : null, soma = eq && it.tipo === "chip_stat" ? somaAgora(m) : null;
  return (
    <li className={`item-card${tem ? "" : " item-falta"}${eq ? " item-eq" : ""}`}>
      <span className="item-cab"><b className="item-nome">{it.nome}</b><span className={`dl-tag item-tag item-tag--${it.tipo}`}>{TIPO[it.tipo]}</span>{eq && <span className="dl-tag dl-tag--ativo">equipado</span>}</span>
      <span className="item-efeito">{it.efeito}</span>
      {it.tipo === "chip_regra" && <span className="item-regra">{rotuloRegra(it.regra).replace(/^se/, "Se")} · pede um {NIVEL[estagioMinimo(it)]}</span>}
      {soma && <span className="item-soma">{Object.keys(soma).length ? "Agora soma " + Object.entries(soma).map(([k, v]) => `+${dec1(v as number)} de ${NOME_STAT[k as Stat].toLowerCase()}`).join(", ") + "."
        : "Agora não soma nada: o treino deste estágio já está no teto (ou o pet ainda não treinou nele)."}</span>}
      {!tem ? <span className="item-onde">Ainda não é seu: {comoGanhar(md)}.</span>
        : eq ? <button type="button" className="dl-btn dl-btn--sec item-bt" onClick={() => agir("desequipar", it.id)}>Desequipar</button>
        : <><button type="button" className="dl-btn item-bt" disabled={!!porque} onClick={() => agir("equipar", it.id)}>Equipar</button>
          {porque && <span className="item-porque">{porque.replace(/^./, c => c.toUpperCase())}.</span>}</>}
    </li>
  );
}

export function TelaItens() {
  const { motor: m, erroTamer } = useJogo(), t = tamerAtual(), [msg, setMsg] = useState("");
  const semEfeito = m.porqueItensNaoValem(), chips = ITENS.filter((x): x is Item & { tipo: "chip_stat" | "chip_regra" } => x.tipo !== "carta"), cartas = ITENS.filter(x => x.tipo === "carta");
  const agir = (op: "equipar" | "desequipar", id: string) => {
    try {
      if (op === "equipar" && !t.temChip(id)) throw new Error("o Tamer não tem este chip");
      mudarMotor(mm => (op === "equipar" ? mm.equipar(id) : mm.desequipar(id)));
      setMsg("");
    } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const nChips = chips.filter(x => t.temChip(x.id)).length, nCartas = cartas.reduce((s, x) => s + t.cartas(x.id), 0);
  return (
    <div className="tela dl desk itens-tela">
      <div className="desk-col itens-lado">
        <section className="dl-card itens-resumo" aria-labelledby="itens-tit">
          <h2 id="itens-tit">Itens do Tamer</h2>
          <p className="itens-conta"><span><span className="dl-num">{nChips}</span> chip{nChips === 1 ? "" : "s"}</span><span><span className="dl-num">{nCartas}</span> carta{nCartas === 1 ? "" : "s"}</span></p>
          <p>Os itens são seus, como as medalhas: o líder de cada arena dá um item na primeira vitória, e a revanche vencida dá uma carta.
            O chip não se gasta; a carta vale uma luta só.</p>
          {<p className="itens-vagas" role="status"><b>{nomeForma(m.forma)}: {m.chips.length} de {m.vagasChip} vaga{m.vagasChip === 1 ? "" : "s"} de chip</b>
              <span>1 vaga com 1 medalha, 2 com 3 e 3 com 5 (o Tamer tem {t.n}).</span></p>}
          {semEfeito && <p className="dl-apoio itens-sem-efeito" role="status">Agora os itens não fazem efeito: {semEfeito}.</p>}
          {erroTamer && <p className="med-erro" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
          {msg && <p className="dl-apoio erro" role="alert">{msg}</p>}
          <details className="dl-apoio"><summary>Como funciona</summary>
            <p><b>Os itens pedem treino:</b> com menos da metade do treino típico do nível, os chips não fazem efeito e a carta não pode ser usada.
              <b>Chip de stat:</b> +1 ponto de treino, só no espaço que ainda falta no teto do estágio e da vida (1/4 do treino típico no máximo).
              <b>Chip de regra:</b> a regra entra no fim da lista de combate, depois das regras do pet e sem tirar nenhuma: completa a forma, não
              passa na frente dela. <b>Carta:</b> só na Exploração (desafiantes e líderes), escolhida antes da luta; uma por luta. A carta da revanche
              vem com um pet do nível da arena, no máximo uma por líder a cada 24 h do relógio do pet.</p></details>

        </section>
      </div>
      <div className="desk-col itens-col">
        <section className="bloco" aria-labelledby="itens-chips-tit">
          <h2 id="itens-chips-tit">Chips</h2>
          <ul className="itens-lista">{chips.map(it => <CardChip key={it.id} it={it} m={m} t={t} agir={agir} />)}</ul>
        </section>
        <section className="bloco" aria-labelledby="itens-cartas-tit">
          <h2 id="itens-cartas-tit">Cartas</h2>
          <ul className="itens-lista">{cartas.map(it => {
            const n = t.cartas(it.id);
            return (
              <li key={it.id} className={`item-card${n ? "" : " item-falta"}`}>
                <span className="item-cab"><b className="item-nome">{it.nome}</b><span className="dl-tag item-tag item-tag--carta">carta</span><span className="item-qtd dl-num">×{n}</span></span>
                <span className="item-efeito">{it.efeito}</span>
                <span className="item-onde">{n ? "Escolha antes de uma luta (Exploração ou Arena)." : "Nenhuma agora."} Vem da {deOnde(it)}.</span>
              </li>
            );
          })}</ul>
        </section>
      </div>
    </div>
  );
}
