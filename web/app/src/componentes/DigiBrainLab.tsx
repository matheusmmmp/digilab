/* O painel DigiBrain do modular (docs/TAREFA_V3_LAB_MODULAR.md, LM5b; pranchas docs/pranchas/lab/painel_*; LM5-1 a LM5-4 e LM5-6). So le o motor por
   useJogo(): todo numero sai de `Motor.leituraLab()` (motor/digibrain/leitura.ts, o ultimo motivo do M-ADAPT em inteiros) e do historico; a
   tela so escolhe o texto e formata. Nenhum rotulo diz "pensando", "sentindo" ou "querendo": dizem o modulo ou o que o motivo guarda. O painel
   do A v11 (DigiBrain.tsx) segue igual para os pets v11. */
import { NOME_PET, ORDEM_TERMOS, type AcaoPet, type LeituraLab, type TermoLab } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import { hhmm } from "../telas/pet/TelaPet.tsx";
import "../estilo/lab.css";

const NOME_TERMO: Record<TermoLab, string> = {
  memoria: "Lugar lembrado", inato: "Inato", lembranca: "Lembrança", objeto: "Objeto à vista", incentivo: "Incentivo (P1)", persistencia: "Persistência", habito: "Hábito (P2)",
};
const NOME_SONDA: Record<string, string> = {
  sem_memoria: "sem a memória", sem_lembranca: "sem a lembrança", sem_habito: "sem o hábito", sem_incentivo: "sem o incentivo",
  sem_persistencia: "sem a persistência", so_inato: "só o inato",
};
const ACAO_INF: Record<string, string> = {
  ocioso: "ficar à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
};
const maiuscula = (t: string): string => t.charAt(0).toUpperCase() + t.slice(1);

/** o rotulo de uma unidade, da chave [acao, tipo, id]: o que o motivo guarda, sem inventar nome de lugar (LM5-4) */
export function rotuloUnidade(chave: readonly [string, string | null, unknown]): string {
  const [acao, tipo, ident] = chave, verbo = ACAO_INF[acao] ?? acao;
  if (tipo === "ponto" && Array.isArray(ident)) return `${verbo} o lugar lembrado (${ident[0]}, ${ident[1]})`;
  if (tipo === "cheiro") return `${verbo} pelo cheiro`;
  if (tipo === "vagar") return `${verbo} vagando`;
  if (tipo === "comida") return `${verbo} a comida à vista`;
  if (tipo === "bola") return `${verbo} com a bola`;
  return verbo;
}
const dez = (permil: number): number => Math.round(permil / 10);
const pct = (permil: number, sinal: boolean): string => (sinal && permil > 0 ? "+" : "") + String(dez(permil)).replace("-", "−") + "%";

function Barras({ l }: { l: LeituraLab }) {
  const zeradas = ORDEM_TERMOS.filter(t => l.zeradas.includes(t));
  return (
    <section aria-labelledby="dl-pesos">
      <h3 className="db-sec" id="dl-pesos">O peso de cada módulo nesta escolha</h3>
      {l.barras.length ? <ul className="db-barras db-barras--div">
        {l.barras.map(b => <li key={b.termo} data-termo={b.termo}><span>{NOME_TERMO[b.termo]}</span>
          <span className="db-trilho" aria-hidden="true"><b className={b.permil < 0 ? "neg" : ""} style={{ width: Math.min(50, Math.abs(b.permil) / 20) + "%" }} /></span>
          <em>{pct(b.permil, true)}</em></li>)}
      </ul> : <p className="db-vazio">Nenhum módulo contribuiu nesta escolha.</p>}
      {zeradas.length > 0 && l.barras.length > 0 && <p className="db-vazio lab-zeradas">Sem contribuição agora: {zeradas.map(t => NOME_TERMO[t].toLowerCase()).join(", ")}.</p>}
      <p className="db-vazio">Cada barra é a parte do peso da unidade escolhida, em módulo; para a esquerda da linha, o módulo puxou contra.</p>
    </section>
  );
}

/** o conteudo do painel do modular, o mesmo no desktop (coluna) e no celular (folha) */
export function ConteudoDigiBrainLab() {
  const { motor: m } = useJogo(), l = m.leituraLab();
  const ultimas = m.historico.filter(h => h.quem === "pet").slice(-5).reverse();
  if (l === null) return <div className="db-conteudo"><p className="db-vazio">Ainda não decidiu nada.</p></div>;
  const peso = l.barras.find(b => b.termo === "lembranca");
  const doMem = l.alvo?.do_mem === true;
  return (
    <div className="db-conteudo db-conteudo--lab">
      <section aria-labelledby="dl-agora">
        <h3 className="db-sec" id="dl-agora">Agora</h3>
        <div className="db-agora"><b>{maiuscula(rotuloUnidade(l.escolha))}</b>
          {l.sem_lugar && <small>Sem o lugar lembrado, teria escolhido: {rotuloUnidade(l.sem_lugar).toLowerCase()}.</small>}
          {l.reflexo && <small>Reflexo do sono: sem sorteio.</small>}
          {l.nada_a_fazer && <small>Nenhuma opção com peso: nada a fazer.</small>}</div>
      </section>
      <section aria-labelledby="dl-lemb">
        <h3 className="db-sec" id="dl-lemb">Lembrança da vez</h3>
        {doMem || l.lembranca ? <div className="db-agora lab-lembranca">
          <b>{doMem && l.alvo ? `Lembrou do lugar (${l.alvo.x}, ${l.alvo.y})` : "Lembrou de um episódio"}</b>
          <small>{l.lembranca ? `da memória ${l.lembranca.memoria} · semelhança ${dez(l.lembranca.sim_permil)}%${peso ? ` · peso na escolha ${pct(peso.permil, true)}` : " · sem peso na escolha"}`
            : "o lugar veio do M-MEM, sem episódio lembrado nesta decisão"}</small></div>
          : <p className="db-vazio">Nada lembrado nesta decisão.</p>}
      </section>
      <Barras l={l} />
      <section aria-labelledby="dl-int">
        <h3 className="db-sec" id="dl-int">Intenção em curso</h3>
        {l.intencao ? <>
          <dl className="lab-int">
            <div><dt>{maiuscula(rotuloUnidade(l.intencao.chave))}</dt><dd>{l.intencao.inicio !== null ? `desde a decisão ${l.intencao.inicio}` : ""}</dd></div>
            <div><dt>Compromisso</dt><dd>{dez(l.intencao.C_permil)}%</dd></div>
            <div><dt>Frustração</dt><dd>{dez(l.intencao.F_permil)}%</dd></div>
            <div><dt>Passos sem avançar</dt><dd>{l.intencao.n_sp}</dd></div>
          </dl>
          <p className="db-vazio">Compromisso: o quanto ele segue a intenção; frustração: o quanto ela tem falhado; passos sem avançar: quantos seguidos sem chegar mais perto.</p>
        </> : <p className="db-vazio">Nenhuma intenção em curso.</p>}
      </section>
      <section aria-labelledby="dl-opc">
        <h3 className="db-sec" id="dl-opc">As opções e a chance de cada uma</h3>
        <ul className="db-opcoes">{l.chances.map(c => <li key={JSON.stringify(c.chave)} className={c.escolhida ? "esc" : ""}>
          <span>{maiuscula(rotuloUnidade(c.chave))}{c.escolhida && <small> · escolhida</small>}</span>
          <span className="db-trilho" aria-hidden="true"><b style={{ width: (c.permil ?? 1000) / 10 + "%" }} /></span>
          <em>{c.permil === null ? "única" : dez(c.permil) + "%"}</em></li>)}</ul>
        {l.chances.length === 1 && <p className="db-vazio">{l.reflexo ? "No reflexo do sono não há sorteio." : "Uma opção só: não houve sorteio."}</p>}
      </section>
      <section aria-labelledby="dl-son">
        <h3 className="db-sec" id="dl-son">O que mudaria a escolha</h3>
        {l.reflexo ? <p className="db-vazio">No reflexo do sono, nenhuma sonda decide.</p>
          : <ul className="db-chips">{l.sondas.filter(s => s.nome in NOME_SONDA).map(s => <li key={s.nome} data-sonda={s.nome} data-muda={s.mudaria}>{NOME_SONDA[s.nome]}: {s.mudaria ? "muda" : "não muda"}</li>)}</ul>}
      </section>
      <section aria-labelledby="dl-ult">
        <h3 className="db-sec" id="dl-ult">Últimas ações</h3>
        <ol className="db-ultimas">{ultimas.map((h, i) => <li key={i}><span className="dl-lcd">{hhmm(h.t)}</span>{NOME_PET[h.a as AcaoPet] ?? h.a}</li>)}</ol>
      </section>
    </div>
  );
}
