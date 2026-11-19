/* Os dois rankings da MMO8 no cais (a prancha docs/pranchas/ux-reset/, tela 6; UX-RS-3 APROVADA em 2026-11-19: as abas Semana, Tamers,
   Digimon e Mural, o que reve a UX-CA-1). O ranking dos Tamers vai pelo Respeito conferido (GET /tamers); o dos Digimon, pelo maximo
   historico de cada pet, o total da vida (GET /digimons). Tudo aqui e tela: as chamadas ficam em src/cais/pontuacoes.ts. Os tamanhos e os
   textos sao PROPOSTOS, SEM FONTE (os da prancha). */
import { useSyncExternalStore } from "react";
import { Info } from "lucide-react";
import { LINHAS_FOLHA, LINHAS_LADO } from "../../cais/cais.ts";
import { abaDigimons, abaTamers, milhares, ouvirPontuacoes, revisaoPontuacoes, type Estado, type LinhaDigimon, type LinhaTamer, type Ranking } from "../../cais/pontuacoes.ts";
import { TAMER_LENDARIO } from "../../ranking/pontos.ts";
import "../../estilo/reset.css";

export type AbaCais = "semana" | "tamers" | "digimon" | "mural";
const ABAS: [AbaCais, string][] = [["semana", "Semana"], ["tamers", "Tamers"], ["digimon", "Digimon"], ["mural", "Mural"]];

/** a aba com que o cais abre na proxima vez ("Ver os rankings no cais", do perfil); volta a "semana" depois de lida */
let abaPedida: AbaCais = "semana";
export function pedirAbaDoCais(a: AbaCais): void { abaPedida = a; }
export function tirarAbaPedida(): AbaCais { const a = abaPedida; abaPedida = "semana"; return a; }

export function AbasCais({ aba, ir }: { aba: AbaCais; ir: (a: AbaCais) => void }) {
  return (
    <div className="rs-abas" role="tablist" aria-label="Rankings do cais">
      {ABAS.map(([a, nome]) => (
        <button type="button" key={a} role="tab" className="ct-filtro" aria-selected={aba === a} onClick={() => ir(a)}
          data-testid={a === "mural" ? "ca-abrir-mural" : `ca-aba-${a}`}>{nome}</button>
      ))}
    </div>
  );
}

/** as linhas da tela: as `n` primeiras e, se a conta ficou fora delas, a linha dela depois do salto */
function daTela<L extends { posicao: number; voce: boolean }>(linhas: readonly L[], n: number): { topo: L[]; voce: L | null } {
  const topo = linhas.slice(0, n), fora = linhas.find(l => l.voce && l.posicao > (topo.at(-1)?.posicao ?? 0)) ?? null;
  return { topo, voce: fora };
}

function Estados<T>({ e, vazio, children }: { e: Estado<T> | null; vazio: string; children: (d: T) => React.ReactNode }) {
  if (e === null || e.passo === "buscando") return <p className="ct-chamada" role="status" data-testid="rs-rk-buscando">Buscando o ranking</p>;
  if (e.passo === "sem_resposta") return (
    <div className="ct-destaque" role="alert" data-testid="rs-rk-sem-resposta"><span className="ct-rot">Sem resposta</span><b>O ranking não veio</b>
      <p>{vazio}</p></div>
  );
  if (e.passo === "sem_conta") return (
    <div className="ct-destaque" role="status" data-testid="rs-rk-sem-conta"><span className="ct-rot">Só com a conta</span><b>Os rankings pedem a conta</b>
      <p>Eles mostram só os apelidos. Sem conta, nada muda no jogo.</p></div>
  );
  return <>{children(e.dados)}</>;
}

function TabTamers({ r, curto }: { r: Ranking<LinhaTamer>; curto: boolean }) {
  if (r.total === 0) return <div className="ca-vazia" role="status" data-testid="rs-tamers-vazio"><b>Ninguém tem Respeito conferido ainda</b>
    <span>A tabela nasce com o primeiro feito que o servidor vir.</span></div>;
  const { topo, voce } = daTela(r.linhas, curto ? LINHAS_FOLHA : LINHAS_LADO);
  const linha = (l: LinhaTamer) => (
    <tr key={l.posicao + l.apelido} className={l.voce ? "ca-eu" : undefined} aria-current={l.voce ? "true" : undefined} data-testid={l.voce ? "rs-tamers-voce" : undefined}>
      <td className="ca-pos">{l.posicao}º</td>
      <th scope="row"><span>{l.apelido}</span>{l.voce && <span className="ct-etq ok">você</span>}{l.titulo && <span className="ct-etq">Lendário</span>}</th>
      <td className="ca-pts">{milhares(l.respeito)}</td><td>{l.nivel === null ? "—" : `Nv ${l.nivel}`}</td>
    </tr>
  );
  return (
    <table className="ca-tab" data-testid="rs-tamers">
      <caption className="sr-only">Ranking dos Tamers pelo Respeito conferido: {r.total} {r.total === 1 ? "Tamer" : "Tamers"}</caption>
      <thead><tr><th scope="col">#</th><th scope="col">Tamer</th><th scope="col">Respeito</th><th scope="col">Nível</th></tr></thead>
      <tbody>{topo.map(linha)}
        {voce && <><tr className="ca-salto" aria-hidden="true"><td colSpan={4}>· · ·</td></tr>{linha(voce)}</>}</tbody>
    </table>
  );
}

function TabDigimons({ r, curto }: { r: Ranking<LinhaDigimon>; curto: boolean }) {
  if (r.total === 0) return <div className="ca-vazia" role="status" data-testid="rs-digimons-vazio"><b>Nenhum Digimon pontuou ainda</b>
    <span>A tabela nasce com a primeira vitória ranqueada conferida.</span></div>;
  const { topo, voce } = daTela(r.linhas, curto ? LINHAS_FOLHA : LINHAS_LADO);
  const linha = (l: LinhaDigimon) => (
    <tr key={l.posicao + l.apelido + l.forma} className={l.voce ? "ca-eu" : undefined} data-testid={l.voce ? "rs-digimons-seu" : undefined}>
      <td className="ca-pos">{l.posicao}º</td>
      <th scope="row"><span>{l.forma}</span>{l.voce && <span className="ct-etq ok">seu</span>}{l.aposentado && <span className="ct-etq">aposentado</span>}</th>
      {!curto && <td className="rs-tamer">{l.apelido}</td>}
      <td className="ca-pts">{milhares(l.pontos)}</td>
    </tr>
  );
  return (
    <table className="ca-tab" data-testid="rs-digimons">
      <caption className="sr-only">Ranking dos Digimon: o total da vida de cada pet, {r.total} {r.total === 1 ? "pet" : "pets"}</caption>
      <thead><tr><th scope="col">#</th><th scope="col">Digimon</th>{!curto && <th scope="col">Tamer</th>}<th scope="col">Pontos</th></tr></thead>
      <tbody>{topo.map(linha)}
        {voce && <><tr className="ca-salto" aria-hidden="true"><td colSpan={curto ? 3 : 4}>· · ·</td></tr>{linha(voce)}</>}</tbody>
    </table>
  );
}

/** a aba Tamers ou Digimon do cais */
export function RankingDoCais({ aba, curto }: { aba: "tamers" | "digimon"; curto: boolean }) {
  useSyncExternalStore(ouvirPontuacoes, revisaoPontuacoes);
  if (aba === "tamers") return (
    <>
      <Estados e={abaTamers.atual()} vazio="O seu Respeito continua guardado no servidor.">{r => <TabTamers r={r} curto={curto} />}</Estados>
      <p className="ca-parcial"><Info aria-hidden="true" /><span>O Respeito só sobe. "Lendário" a partir de {milhares(TAMER_LENDARIO)}; a conta não para.</span></p>
      {!curto && <details className="ca-como"><summary><Info aria-hidden="true" />Como a tabela conta</summary>
        <p>O Respeito vem dos feitos do Tamer e dos resets, só os que o servidor conferiu. No empate, fica na frente quem chegou antes.</p></details>}
    </>
  );
  return (
    <>
      <Estados e={abaDigimons.atual()} vazio="Os pontos dos seus pets continuam guardados no servidor.">{r => <TabDigimons r={r} curto={curto} />}</Estados>
      <p className="ca-parcial"><Info aria-hidden="true" /><span>Uma linha por pet, pelo total da vida. O aposentado fica com o que tinha.</span></p>
    </>
  );
}
