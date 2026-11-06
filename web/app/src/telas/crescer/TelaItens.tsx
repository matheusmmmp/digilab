/* Crescer · Itens (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13): o inventario do Tamer (chips e cartas, do registro
   dele, src/tamer.ts) e os chips equipados no pet ativo (eventos "i" do registro do pet). Equipar e desequipar gravam no registro do
   pet; o motor confere vagas, estagio e lista, e esta tela so oferece o que o Tamer tem. As cartas se escolhem antes da luta (Campanha
   e Arena). Itens sem equilibrio: numeros PROPOSTOS (secao 13). Nos pets v9 (rodada de equilibrio geral, fase 3; itens.ts) os itens pedem
   o treino minimo do nivel, a carta so vale na Campanha, o chip de regra vai para o fim da lista e o de stat vale metade: a tela diz isso.
   L2 de "Lugares da ilha" (prancha crescer_itens_*, regra do texto): a vista tem so icone, nome curto, o efeito em 2 a 4 palavras e o estado em
   forma (solido, tracejado, cadeado); a frase inteira de cada item, a regra das vagas e o aviso do treino vao para o balao. */
import { useState } from "react";
import { Check, CreditCard, Cpu, Lock, Puzzle, type LucideIcon } from "lucide-react";
import {
  CARTA_DA_REVANCHE, CIT, CIT_V9, ITENS, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHAS, MEDALHA_POR_ID, NOME_STAT, NPC, STATS, estagioMinimo, nomeForma, regraDe, regraQueCobre, rotuloRegra,
  type Item, type Motor, type Stat,
} from "../../../motor/index.ts";
import { mudarMotor, tamerAtual, useJogo } from "../../jogo.ts";
import { comoGanhar, noLugar, type Tamer } from "../../tamer.ts";
import { Balao, ComDica, ComoFunciona, propsBalao } from "../../componentes/Dica.tsx";

const NIVEL: Record<string, string> = { crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };
const dec1 = (x: number): string => x.toFixed(1).replace(".", ",").replace(/,0$/, "");
const ICONE: Record<Item["tipo"], LucideIcon> = { chip_stat: Cpu, chip_regra: Puzzle, carta: CreditCard };

/** o nome curto do item ("Chip de Força" vira "Força"): o tipo ja vem do icone e da secao */
export const nomeCurto = (it: Item): string => it.nome.replace(/^(Chip|Carta) (de |d[oa] )?/, "");
/** o efeito em 2 a 4 palavras (texto novo de tela, PROPOSTO; o motor nao muda): os chips de stat saem dos pontos deles e os numeros das cartas, das
    constantes; as regras e a carta de foco, do mapa abaixo. Item sem entrada falha alto (o teste confere todos) */
const EFEITO_REGRA: Readonly<Record<string, string>> = {
  chip_recuo: "pesado → recuar", chip_oportunista: "guts < 20 → pesado", chip_perseguidor: "disparo → avançar", chip_aparo: "golpe rápido → defender",
  carta_foco: "não se distrai",
};
export function efeitoCurto(it: Item): string {
  if (it.tipo === "chip_stat") return Object.entries(it.pontos).map(([k, v]) => `+${v} ${NOME_STAT[k as Stat]}`).join(" ");
  if (it.id === "carta_folego") return `+${CIT.gutsFolego} guts`;
  if (it.id === "carta_cura") return `< ${CIT.curaAbaixo * 100}% → +${CIT.curaFracao * 100}%`;
  const e = EFEITO_REGRA[it.id];
  if (!e) throw new Error(`item sem efeito curto na tela: ${it.id}`);
  return e;
}

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

/** o card de um item: o icone, o nome curto e o efeito curto; a frase inteira e o resto no balao */
function CardItem({ it, m, t, proximo, agir }: { it: Item; m: Motor; t: Tamer; proximo: boolean; agir: (op: "equipar" | "desequipar", id: string) => void }) {
  const carta = it.tipo === "carta", n = carta ? t.cartas(it.id) : 0, tem = carta ? n > 0 : t.temChip(it.id);
  const eq = !carta && m.chips.includes(it.id), I = ICONE[it.tipo];
  const porque = !carta && tem && !eq ? m.porqueNaoEquipa(it.id) : null;
  const soma = eq && it.tipo === "chip_stat" ? somaAgora(m) : null;
  /* DE-3: o chip de regra coberto por uma regra ativa do pet (que vem antes dele na lista de luta) so ganha o aviso */
  const cobre = it.tipo === "chip_regra" && m.gp ? regraQueCobre(m.gp.ativas.map(regraDe), it.regra) : null;
  const dica = (
    <>
      <b>{it.nome}</b>{proximo && <> (próximo a ganhar)</>}: {it.efeito}
      {it.tipo === "chip_regra" && <> {rotuloRegra(it.regra).replace(/^se/, "Se")} · pede um {NIVEL[estagioMinimo(it)]}.</>}
      {cobre && <> <span data-testid="chip-coberto">Este chip fica coberto: a regra “{rotuloRegra(cobre)}” do pet vale sempre que ele valeria e vem antes, então o chip quase nunca decide.</span></>}
      {soma && <> {Object.keys(soma).length ? "Agora soma " + Object.entries(soma).map(([k, v]) => `+${dec1(v as number)} de ${NOME_STAT[k as Stat].toLowerCase()}`).join(", ") + "."
        : "Agora não soma nada: o treino deste estágio já está no teto (ou o pet ainda não treinou nele)."}</>}
      {carta ? <> {n ? "Escolha antes de uma luta (Exploração ou Arena)." : "Nenhuma agora."} Vem da {deOnde(it)}.</>
        : !tem ? <> Ainda não é seu: {comoGanhar(MEDALHA_POR_ID[Object.entries(ITEM_DA_MEDALHA).find(([, c]) => c === it.id)![0]])}.</> : null}
      {porque && <> {porque.replace(/^./, c => c.toUpperCase())}.</>}
    </>
  );
  const rotulo = carta ? `${it.nome}, ${n ? `${n} ${n === 1 ? "carta" : "cartas"}` : "nenhuma"}`
    : !tem ? `${it.nome}, ainda não é seu${proximo ? ", próximo a ganhar" : ""}` : eq ? `${it.nome}, equipado: desequipar` : `${it.nome}: equipar`;
  const id = `${it.id}-balao`;
  /* a carta se escolhe na luta; o chip do Tamer se equipa e desequipa aqui */
  const age = !carta && tem && !(porque && !eq);
  return (
    <li className={`it2-card${!tem ? " it2--falta" : ""}${eq ? " it2--eq" : ""}${proximo ? " it2--proximo" : ""}`} data-item={it.id}>
      <button type="button" className="it2 dica-alvo" aria-label={rotulo} aria-describedby={id} aria-pressed={!carta && tem ? eq : undefined} aria-disabled={!age || undefined} {...propsBalao(false)}
        onClick={() => { if (age) agir(eq ? "desequipar" : "equipar", it.id); }}>
        <I aria-hidden="true" />
        <b>{nomeCurto(it)}</b>
        <small>{efeitoCurto(it)}</small>
        <span className="it2-canto">
          {it.tipo === "chip_regra" && <span className="lg-etq">{NIVEL[estagioMinimo(it)]}</span>}
          {carta ? <span className="it2-qtd">×{n}</span> : !tem ? <Lock aria-hidden="true" /> : eq ? <Check aria-hidden="true" /> : null}
        </span>
        <Balao id={id}>{dica}</Balao>
      </button>
    </li>
  );
}

/** as vagas de chip: tres encaixes (ocupado, livre ou fechado com as medalhas que abrem); a regra no balao */
function Vagas({ m, t }: { m: Motor; t: Tamer }) {
  const total = Math.max(...CIT.vagas.map(([, v]) => v));
  const medalhasDaVaga = (k: number): number => Math.min(...CIT.vagas.filter(([, v]) => v >= k).map(([n]) => n));
  const regra = CIT.vagas.slice().reverse().map(([n, v]) => `${v} ${v === 1 ? "vaga" : "vagas"} com ${n} ${n === 1 ? "medalha" : "medalhas"}`).join(", ");
  return (
    <ComDica className="it2-vagas" lado="dir" rotulo={`Vagas de chip do ${nomeForma(m.forma)}: ${m.chips.length} de ${m.vagasChip}`}
      dica={<>{nomeForma(m.forma)}: {m.chips.length} de {m.vagasChip} vaga{m.vagasChip === 1 ? "" : "s"} de chip. {regra} (o Tamer tem {t.n}).</>}>
      {Array.from({ length: total }, (_, i) => {
        const k = i + 1, ocupada = k <= m.chips.length, livre = !ocupada && k <= m.vagasChip, nec = medalhasDaVaga(k);
        return (
          <span key={k} className={`it2-vaga it2-vaga--${ocupada ? "ocupada" : livre ? "livre" : "trancada"}`} aria-hidden="true">
            {ocupada ? <Check /> : livre ? null : <><Lock /><small>{nec}</small></>}
          </span>
        );
      })}
      <small>vagas</small>
    </ComDica>
  );
}

export function TelaItens() {
  const { motor: m, erroTamer } = useJogo(), t = tamerAtual(), [msg, setMsg] = useState("");
  const semEfeito = m.porqueItensNaoValem(), chips = ITENS.filter(x => x.tipo !== "carta"), cartas = ITENS.filter(x => x.tipo === "carta");
  const agir = (op: "equipar" | "desequipar", id: string) => {
    try {
      if (op === "equipar" && !t.temChip(id)) throw new Error("o Tamer não tem este chip");
      mudarMotor(mm => (op === "equipar" ? mm.equipar(id) : mm.desequipar(id)));
      setMsg("");
    } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const nChips = chips.filter(x => t.temChip(x.id)).length, nCartas = cartas.reduce((s, x) => s + t.cartas(x.id), 0);
  /* o destaque: o primeiro item que o Tamer pode ganhar, pela ordem das medalhas */
  const proxMed = MEDALHAS.find(x => !t.tem(x.id)), proximo = proxMed ? ITEM_DA_MEDALHA[proxMed.id] : null;
  /* "treino 10/11": os pontos do pet e o minimo do nivel (a frase inteira vai para o balao) */
  const tip = CIT.tipico[m.estagioAtual], minimo = tip === undefined ? null : Math.ceil(CIT_V9.treinoMinimo * tip);
  return (
    <div className="tela dl itens-tela lg">
      <div className="it2-topo">
        <span className="it2-conta" role="img" aria-label={`${nChips} chip${nChips === 1 ? "" : "s"}`}><Cpu aria-hidden="true" /><b className="lg-num">{nChips}</b><small>chips</small></span>
        <span className="it2-conta" role="img" aria-label={`${nCartas} carta${nCartas === 1 ? "" : "s"}`}><CreditCard aria-hidden="true" /><b className="lg-num">{nCartas}</b><small>cartas</small></span>
        {semEfeito && (
          <ComDica className="it2-aviso itens-sem-efeito" rotulo={`Os itens ainda não fazem efeito: ${semEfeito}`} dica={<>Agora os itens não fazem efeito: {semEfeito}.</>}>
            treino{minimo !== null && <b>{Math.floor(m.treino.total)}/{minimo}</b>}
          </ComDica>
        )}
        <Vagas m={m} t={t} />
      </div>
      {erroTamer && <p className="it2-msg" role="alert">O registro do Tamer não abriu, e o app não vai gravar por cima dele: {erroTamer}</p>}
      {msg && <p className="it2-msg" role="alert">{msg}</p>}
      <span className="lg-rot">Chips</span>
      <ul className="it2-grade" aria-label="Chips">{chips.map(it => <CardItem key={it.id} it={it} m={m} t={t} proximo={it.id === proximo} agir={agir} />)}</ul>
      <span className="lg-rot">Cartas</span>
      <ul className="it2-grade it2-grade--cartas" aria-label="Cartas">{cartas.map(it => <CardItem key={it.id} it={it} m={m} t={t} proximo={false} agir={agir} />)}</ul>
      <ComoFunciona>
        Os itens são seus, como as medalhas: o líder de cada arena dá um item na primeira vitória, e a revanche vencida dá uma carta. O chip não se gasta; a carta vale uma luta só.
        <b> Os itens pedem treino:</b> com menos da metade do treino típico do nível, os chips não fazem efeito e a carta não pode ser usada.
        <b> Chip de stat:</b> +1 ponto de treino, só no espaço que ainda falta no teto do estágio e da vida (1/4 do treino típico no máximo).
        <b> Chip de regra:</b> a regra entra no fim da lista de combate, depois das regras do pet e sem tirar nenhuma: completa a forma, não passa na frente dela.
        <b> Carta:</b> só na Exploração (desafiantes e líderes), escolhida antes da luta; uma por luta. A carta da revanche vem com um pet do nível da arena, no máximo uma por líder a cada 24 h do relógio do pet.
      </ComoFunciona>
    </div>
  );
}
