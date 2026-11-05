/* "O que o pet aprendeu" (so leitura do GambitsPet; src/aprendizadoLuta.ts): a lista com a nota de cada regra, o que o pet trocou ou
   o dono mexeu nas ultimas lutas, e o que esta travado ou vetado. Nao muda nada: quem trava e veta e o EditorRegras. */
import { useJogo } from "../../jogo.ts";
import { visaoAprendizado, type LinhaRegra } from "../../aprendizadoLuta.ts";

const pt = (v: number, d = 2): string => ((v >= 0 ? "+" : "") + v.toFixed(d)).replace(".", ",");
const NOME_ESTADO = { livre: "", travada: "travada por você", chip: "chip" } as const;
const ROTULO_TIPO = { troca: "pet trocou", evolucao: "evolução", dono: "você" } as const;

function Variacao({ l }: { l: LinhaRegra }) {
  if (l.delta === null) return null;
  if (l.delta === 0) return <span className="ap-var" title="na mesma posição da lista de partida">= posição</span>;
  const sobe = l.delta > 0;
  return <span className={`ap-var ${sobe ? "ap-sobe" : "ap-desce"}`} title="posições contra a lista de partida">{sobe ? "▲" : "▼"} {Math.abs(l.delta)}</span>;
}

export function PainelAprendizado() {
  const { motor: m } = useJogo();
  if (!m.gp) return null;
  const v = visaoAprendizado(m.gp), maior = Math.max(.01, ...v.linhas.map(l => Math.abs(l.nota)));
  return (
    <section className="bloco ap-painel" data-testid="painel-aprendizado" aria-labelledby="ap-tit">
      <h2 id="ap-tit">O que o pet aprendeu</h2>
      {v.nLutas === 0
        ? <p className="dl-apoio" data-testid="ap-vazio">Ainda sem lutas: as notas abaixo são as da lista de partida. Depois de cada luta contra um bot, cada regra que disparou ganha uma nota pelo saldo de dano dos turnos em que agiu.</p>
        : <p>Em {v.nLutas} luta{v.nLutas === 1 ? "" : "s"}, a nota de cada regra foi puxada para o <b>saldo de dano</b> dos turnos em que ela agiu (passo {pt(v.passo.alfa, 2).replace("+", "")}, mais {pt(v.passo.bonus, 2).replace("+", "")} pelo resultado). A lista se reordena pela nota.</p>}
      <ol className="g-lista ap-lista" data-testid="ap-lista">
        {v.linhas.map(l => (
          <li key={l.k} className={`ap-linha ap-${l.estado}`} data-testid="ap-regra">
            <span className="g-num">{l.pos + 1}</span>
            <span className="g-corpo">
              <span className="g-se">{l.rotulo}</span>
              <span className="ap-barra" aria-hidden="true"><i className={l.nota < 0 ? "neg" : ""} style={{ width: `${Math.round(Math.abs(l.nota) / maior * 100)}%` }} /></span>
              <span className="g-meta">
                <b data-testid="ap-nota">nota {pt(l.nota)}</b> · usada {l.disparos}× <Variacao l={l} />
                {l.estado !== "livre" && <> · <span className="dl-tag dl-tag--estagio">{NOME_ESTADO[l.estado]}</span></>}
                {l.candidataATroca && <> · <span className="dl-tag dl-tag--espera" data-testid="ap-troca-prox">abaixo de {pt(v.passo.limiar)}: sai na próxima troca</span></>}
              </span>
            </span>
          </li>
        ))}
      </ol>
      <p className="dl-apoio">Ele tenta algo ao acaso em {Math.round(v.passo.eps * 100)}% das decisões (exploração ε). Uma regra livre com nota abaixo de {pt(v.passo.limiar)} é trocada por outra do repertório.</p>
      <h3>O que mudou nas últimas lutas</h3>
      {v.mudancas.length === 0 ? <p className="dl-apoio" data-testid="ap-sem-mudanca">Nenhuma mudança ainda.</p>
        : <ul className="ap-hist" data-testid="ap-hist">{v.mudancas.map((x, i) => (
          <li key={i} className={`ap-${x.tipo}`}><span className="t">luta {x.luta}</span> <span className="dl-tag">{ROTULO_TIPO[x.tipo]}</span> {x.texto.replace(/(\d)\.(\d)/g, "$1,$2")}</li>))}</ul>}
      <h3>Sua mão na lista</h3>
      {v.travadas.length === 0 && v.vetadas.length === 0 && <p data-testid="ap-dono">Você não travou nem vetou nada: o pet decide sozinho.</p>}
      {v.travadas.length > 0 && <><p className="ap-sub">Travadas ({v.travadas.length}): ficam na posição</p><ul className="ap-hist">{v.travadas.map(t => <li key={t}>{t}</li>)}</ul></>}
      {v.vetadas.length > 0 && <><p className="ap-sub">Vetadas ({v.vetadas.length}): o pet não usa</p><ul className="ap-hist">{v.vetadas.map(x => <li key={x.k}>{x.rotulo}</li>)}</ul></>}
      <p className="dl-apoio">O pet ainda não guarda a nota luta a luta: o painel mostra a nota de agora e o texto de cada troca.{v.linhas.some(l => l.delta !== null) ? "" : " ▲▼ (posição contra a lista de partida) só aparece nos pets v14 em diante."}</p>
    </section>
  );
}
