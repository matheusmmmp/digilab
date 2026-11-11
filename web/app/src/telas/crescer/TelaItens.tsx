/* Crescer · Itens (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13): o inventario do Tamer (do registro dele, src/tamer.ts) e
   os chips equipados no pet ativo (eventos "i" do registro do pet). Equipar e desequipar gravam no registro do pet; o motor confere vagas e
   estagio, e esta tela so oferece o que o Tamer tem. Desde a LP4 da LUTA_POC so o chip de stat faz efeito (os 6 stats do pet na luta); os
   chips de regra e as cartas que o Tamer ja tinha aparecem numa lista a parte, sem efeito (LP-5). Os itens pedem o treino minimo do nivel e o
   chip de stat vale metade (os pets v9; itens.ts): a tela diz isso. Numeros PROPOSTOS (o equilibrio e o da LP5).
   L2 de "Lugares da ilha" (prancha crescer_itens_*, regra do texto): a vista tem so icone, nome curto, o efeito em 2 a 4 palavras e o estado em
   forma (solido, tracejado, cadeado); a frase inteira de cada item, a regra das vagas e o aviso do treino vao para o balao. */
import { useState } from "react";
import { Archive, Check, Cpu, Lock } from "lucide-react";
import {
  CIT, CIT_V9, ITENS, ITEM_DA_MEDALHA, MEDALHAS, MEDALHA_POR_ID, NOME_STAT, STATS, nomeForma, temEfeito,
  type ChipStat, type Item, type Motor, type Stat,
} from "../../../motor/index.ts";
import { mudarMotor, tamerAtual, useJogo } from "../../jogo.ts";
import { comoGanhar, type Tamer } from "../../tamer.ts";
import { Balao, ComDica, ComoFunciona, propsBalao } from "../../componentes/Dica.tsx";

const dec1 = (x: number): string => x.toFixed(1).replace(".", ",").replace(/,0$/, "");

/** o nome curto do item ("Chip de Força" vira "Força"): o tipo ja vem do icone e da secao */
export const nomeCurto = (it: Item): string => it.nome.replace(/^(Chip|Carta) (de |d[oa] )?/, "");
/** o efeito em 2 a 4 palavras (texto de tela, PROPOSTO; o motor nao muda): os chips de stat saem dos pontos deles; os itens de antes, "sem efeito" */
export function efeitoCurto(it: Item): string {
  if (it.tipo === "chip_stat") return Object.entries(it.pontos).map(([k, v]) => `+${v} ${NOME_STAT[k as Stat]}`).join(" ");
  return "sem efeito";
}

/** de onde o chip de stat vem: a medalha que o da */
export function deOnde(it: ChipStat): string {
  const md = MEDALHA_POR_ID[Object.entries(ITEM_DA_MEDALHA).find(([, c]) => c === it.id)![0]];
  return `vem com a ${md.nome}`;
}
/** o que os chips de stat somam agora no pet (pontos de treino na luta, alem do treino dele) */
function somaAgora(m: Motor): Partial<Record<Stat, number>> {
  const p = m.pontosDeLuta(), t = m.treino.pontos;
  return p ? Object.fromEntries(STATS.map(k => [k, p[k] - t[k]]).filter(([, v]) => (v as number) > 1e-9)) : {};
}

/** o card de um chip de stat: o icone, o nome curto e o efeito curto; a frase inteira e o resto no balao */
function CardItem({ it, m, t, proximo, agir }: { it: ChipStat; m: Motor; t: Tamer; proximo: boolean; agir: (op: "equipar" | "desequipar", id: string) => void }) {
  const tem = t.temChip(it.id), eq = m.chips.includes(it.id), I = Cpu;
  const porque = tem && !eq ? m.porqueNaoEquipa(it.id) : null;
  const soma = eq ? somaAgora(m) : null;
  const dica = (
    <>
      <b>{it.nome}</b>{proximo && <> (próximo a ganhar)</>}: {it.efeito}
      {soma && <> {Object.keys(soma).length ? "Agora soma " + Object.entries(soma).map(([k, v]) => `+${dec1(v as number)} de ${NOME_STAT[k as Stat].toLowerCase()}`).join(", ") + "."
        : "Agora não soma nada: o treino deste estágio já está no teto (ou o pet ainda não treinou nele)."}</>}
      {!tem ? <> Ainda não é seu: {comoGanhar(MEDALHA_POR_ID[Object.entries(ITEM_DA_MEDALHA).find(([, c]) => c === it.id)![0]])}.</> : null}
      {porque && <> {porque.replace(/^./, c => c.toUpperCase())}.</>}
    </>
  );
  const rotulo = !tem ? `${it.nome}, ainda não é seu${proximo ? ", próximo a ganhar" : ""}` : eq ? `${it.nome}, equipado: desequipar` : `${it.nome}: equipar`;
  const id = `${it.id}-balao`;
  /* o chip do Tamer se equipa e desequipa aqui */
  const age = tem && !(porque && !eq);
  return (
    <li className={`it2-card${!tem ? " it2--falta" : ""}${eq ? " it2--eq" : ""}${proximo ? " it2--proximo" : ""}`} data-item={it.id}>
      <button type="button" className="it2 dica-alvo" aria-label={rotulo} aria-describedby={id} aria-pressed={tem ? eq : undefined} aria-disabled={!age || undefined} {...propsBalao(false)}
        onClick={() => { if (age) agir(eq ? "desequipar" : "equipar", it.id); }}>
        <I aria-hidden="true" />
        <b>{nomeCurto(it)}</b>
        <small>{efeitoCurto(it)}</small>
        <span className="it2-canto">
          {!tem ? <Lock aria-hidden="true" /> : eq ? <Check aria-hidden="true" /> : null}
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
  const semEfeito = m.porqueItensNaoValem(), chips = ITENS.filter(temEfeito);
  /* os itens de antes que o Tamer tem (chips de regra e cartas): so na lista, sem efeito (LP4) */
  const antigos = ITENS.filter(x => !temEfeito(x) && (x.tipo === "carta" ? t.cartas(x.id) > 0 : t.temChip(x.id)));
  const agir = (op: "equipar" | "desequipar", id: string) => {
    try {
      if (op === "equipar" && !t.temChip(id)) throw new Error("o Tamer não tem este chip");
      mudarMotor(mm => (op === "equipar" ? mm.equipar(id) : mm.desequipar(id)));
      setMsg("");
    } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  const nChips = chips.filter(x => t.temChip(x.id)).length;
  /* o destaque: o primeiro chip de stat que o Tamer pode ganhar, pela ordem das medalhas */
  const proxMed = MEDALHAS.find(x => !t.tem(x.id) && chips.some(c => c.id === ITEM_DA_MEDALHA[x.id])), proximo = proxMed ? ITEM_DA_MEDALHA[proxMed.id] : null;
  /* "treino 10/11": os pontos do pet e o minimo do nivel (a frase inteira vai para o balao) */
  const tip = CIT.tipico[m.estagioAtual], minimo = tip === undefined ? null : Math.ceil(CIT_V9.treinoMinimo * tip);
  return (
    <div className="tela dl itens-tela lg">
      <div className="it2-topo">
        <span className="it2-conta" role="img" aria-label={`${nChips} chip${nChips === 1 ? "" : "s"}`}><Cpu aria-hidden="true" /><b className="lg-num">{nChips}</b><small>chips</small></span>
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
      {antigos.length > 0 && <>
        <span className="lg-rot">Da luta de antes</span>
        <ul className="it2-antigos" aria-label="Itens da luta de antes, sem efeito" data-testid="itens-antigos">
          {antigos.map(it => <li key={it.id}><Archive aria-hidden="true" /><b>{it.nome}</b>{it.tipo === "carta" && <small>×{t.cartas(it.id)}</small>}<small>{it.efeito}</small></li>)}
        </ul>
      </>}
      <ComoFunciona>
        Os chips são seus, como as medalhas: o líder da Campina e o da Cidadela dão um chip na primeira vitória. O chip não se gasta.
        <b> Os chips pedem treino:</b> com menos da metade do treino típico do nível, eles não fazem efeito.
        <b> Chip de stat:</b> +1 ponto de treino, só no espaço que ainda falta no teto do estágio e da vida (1/4 do treino típico no máximo); ele entra nos stats com que o pet luta.
        <b> Da luta de antes:</b> os chips de regra e as cartas mudavam as regras do combate por turnos, que saiu. Eles ficam com você, sem efeito na luta em tempo real.
      </ComoFunciona>
    </div>
  );
}
