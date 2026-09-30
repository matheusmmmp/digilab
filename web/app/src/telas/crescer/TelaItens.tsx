/* Crescer · Itens (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13): o inventario do Tamer (chips e cartas, do registro
   dele, src/tamer.ts) e os chips equipados no pet ativo (eventos "i" do registro do pet). Equipar e desequipar gravam no registro do
   pet; o motor confere vagas, estagio e lista, e esta tela so oferece o que o Tamer tem. As cartas se escolhem antes da luta (Campanha
   e Arena). Itens sem equilibrio: numeros PROPOSTOS (secao 13). */
import { useState } from "preact/hooks";
import {
  CARTA_DA_REVANCHE, CIT, ITENS, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHA_POR_ID, NOME_STAT, NPC, STATS, estagioMinimo, nomeForma, rotuloRegra,
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
  const porque = tem && !eq && m.versao >= CIT.versaoPet ? m.porqueNaoEquipa(it.id) : null, soma = eq && it.tipo === "chip_stat" ? somaAgora(m) : null;
  return (
    <li class={`item-card${tem ? "" : " item-falta"}${eq ? " item-eq" : ""}`}>
      <span class="item-cab"><b class="item-nome">{it.nome}</b><span class={`dl-tag item-tag item-tag--${it.tipo}`}>{TIPO[it.tipo]}</span>{eq && <span class="dl-tag dl-tag--ativo">equipado</span>}</span>
      <span class="item-efeito">{it.efeito}</span>
      {it.tipo === "chip_regra" && <span class="item-regra">{rotuloRegra(it.regra).replace(/^se/, "Se")} · pede um {NIVEL[estagioMinimo(it)]}</span>}
      {soma && <span class="item-soma">{Object.keys(soma).length ? "Agora soma " + Object.entries(soma).map(([k, v]) => `+${dec1(v as number)} de ${NOME_STAT[k as Stat].toLowerCase()}`).join(", ") + "."
        : "Agora não soma nada: o treino deste estágio já está no teto (ou o pet ainda não treinou nele)."}</span>}
      {!tem ? <span class="item-onde">Ainda não é seu: {comoGanhar(md)}.</span>
        : m.versao < CIT.versaoPet ? null
        : eq ? <button type="button" class="dl-btn dl-btn--sec item-bt" onClick={() => agir("desequipar", it.id)}>Desequipar</button>
        : <><button type="button" class="dl-btn item-bt" disabled={!!porque} onClick={() => agir("equipar", it.id)}>Equipar</button>
          {porque && <span class="item-porque">{porque.replace(/^./, c => c.toUpperCase())}.</span>}</>}
    </li>
  );
}

export function TelaItens() {
  const { motor: m, erroTamer } = useJogo(), t = tamerAtual(), [msg, setMsg] = useState("");
  const v6 = m.versao >= CIT.versaoPet, chips = ITENS.filter((x): x is Item & { tipo: "chip_stat" | "chip_regra" } => x.tipo !== "carta"), cartas = ITENS.filter(x => x.tipo === "carta");
  const agir = (op: "equipar" | "desequipar", id: string) => {
    try {
      if (op === "equipar" && !t.temChip(id)) throw new Error("o Tamer não tem este chip");
      mudarMotor(mm => (op === "equipar" ? mm.equipar(id) : mm.desequipar(id)));
      setMsg("");
    } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const nChips = chips.filter(x => t.temChip(x.id)).length, nCartas = cartas.reduce((s, x) => s + t.cartas(x.id), 0);
  return (
    <div class="tela dl desk itens-tela">
      <div class="desk-col itens-lado">
        <section class="dl-card itens-resumo" aria-labelledby="itens-tit">
          <h2 id="itens-tit">Itens do Tamer</h2>
          <p class="itens-conta"><span><span class="dl-num">{nChips}</span> chip{nChips === 1 ? "" : "s"}</span><span><span class="dl-num">{nCartas}</span> carta{nCartas === 1 ? "" : "s"}</span></p>
          <p>Os itens são seus, como as medalhas: o líder de cada arena dá um item na primeira vitória, e a revanche vencida dá uma carta.
            O chip não se gasta; a carta vale uma luta só.</p>
          {!v6 ? <p class="dl-apoio">{nomeForma(m.forma)} é de uma versão antiga: não usa itens.</p>
            : <p class="itens-vagas" role="status"><b>{nomeForma(m.forma)}: {m.chips.length} de {m.vagasChip} vaga{m.vagasChip === 1 ? "" : "s"} de chip</b>
              <span>1 vaga com 1 medalha, 2 com 3 e 3 com 5 (o Tamer tem {t.n}).</span></p>}
          {erroTamer && <p class="med-erro" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
          {msg && <p class="dl-apoio erro" role="alert">{msg}</p>}
          <details class="dl-apoio"><summary>Como funciona</summary>
            <p><b>Chip de stat:</b> +2 pontos de treino, mas só no espaço que ainda falta no teto do estágio e da vida, e todos os chips de stat
              juntos valem no máximo 1/4 do treino típico do estágio: o chip adianta o treino, não passa do teto. <b>Chip de regra:</b> uma regra
              nova entra no topo da lista de combate do pet (sai a de nota mais baixa se a lista estiver cheia); o pet não a troca enquanto o chip
              estiver equipado, e você pode travá-la, não vetá-la. <b>Carta:</b> escolha antes de uma luta na Campanha ou na Arena; uma por luta.
              A carta da revanche vem com um pet do nível da arena, no máximo uma por líder a cada 24 h do relógio do pet. Os números dos itens
              ainda são provisórios.</p></details>
        </section>
      </div>
      <div class="desk-col itens-col">
        <section class="bloco" aria-labelledby="itens-chips-tit">
          <h2 id="itens-chips-tit">Chips</h2>
          <ul class="itens-lista">{chips.map(it => <CardChip key={it.id} it={it} m={m} t={t} agir={agir} />)}</ul>
        </section>
        <section class="bloco" aria-labelledby="itens-cartas-tit">
          <h2 id="itens-cartas-tit">Cartas</h2>
          <ul class="itens-lista">{cartas.map(it => {
            const n = t.cartas(it.id);
            return (
              <li key={it.id} class={`item-card${n ? "" : " item-falta"}`}>
                <span class="item-cab"><b class="item-nome">{it.nome}</b><span class="dl-tag item-tag item-tag--carta">carta</span><span class="item-qtd dl-num">×{n}</span></span>
                <span class="item-efeito">{it.efeito}</span>
                <span class="item-onde">{n ? "Escolha antes de uma luta (Campanha ou Arena)." : "Nenhuma agora."} Vem da {deOnde(it)}.</span>
              </li>
            );
          })}</ul>
        </section>
      </div>
    </div>
  );
}
