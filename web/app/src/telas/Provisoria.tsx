/* Tela provisoria do esqueleto (Etapa 3): mostra o que o motor tem para cada aba, derivado na hora, para
   conferir que o save abriu inteiro. A Etapa 4 troca cada uma pela tela desenhada. */
import type { JSX } from "preact";
import { useState } from "preact/hooks";
import { CAMPANHA, NOME_ESP, NOME_PET, Motor, nomeForma } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import type { Aba } from "../rotas.ts";

const pct = (x: number): string => Math.round(x * 100) + "%";
const n1 = (x: number): string => x.toFixed(1).replace(".", ",");

function dados(m: Motor, aba: Aba): [string, string | number][] {
  const e = m.e;
  switch (aba) {
    case "estado": return [["fazendo", NOME_PET[m.acao]], ["fome", pct(e.fome)], ["higiene", pct(e.higiene)], ["energia", pct(e.energia)],
      ["humor", pct(e.humor)], ["saúde", pct(e.saude)], ["sujeira", e.sujeira], ["dormindo", e.dormindo ? "sim" : "não"]];
    case "treinar": return [["pontos treinados", n1(m.treino.total)], ["fadiga", n1(m.treino.fadiga)], ["sobrecarga", n1(m.treino.sobrecarga)],
      ["sessões", m.treino.sessoes], ["forçadas", m.treino.forcadas], ["enroladas", m.treino.enroladas]];
    case "aprend": return [["decisões do pet", m.nDecisoes], ["ações do dono", m.nDono], ["motivos guardados", m.motivos.length],
      ...(m.versao >= 2 ? [["vínculo", pct(m.vinc.valor)] as [string, string]] : [])];
    case "evolucao": return [["brasão", NOME_ESP[m.especie]], ["forma", nomeForma(m.forma)], ["evoluções", m.evolucoes.length],
      ["versão do pet", m.versao], ["sombria", m.sombria ? "sim" : "não"]];
    case "arena": return [["regras ativas", m.gp ? m.gp.ativas.length : 0], ["lutas que ensinaram", m.gp ? m.gp.nLutas : 0], ["sparring", m.sparring]];
    case "campanha": return CAMPANHA.map(c => [c.nome, m.campanha[c.k] + " vitória(s)"]);
    case "registro": return [["eventos no registro", m.log.length], ["semente", m.semente], ["versão", m.versao]];
    case "catalogo": return [["brasão", NOME_ESP[m.especie]]];
    case "cenarios": return [];
  }
}

function ConferirReplay({ m }: { m: Motor }) {
  const [res, setRes] = useState<JSX.Element | null>(null);
  const conferir = () => {
    const t0 = performance.now(), igual = Motor.reproduzir(m.semente, m.log, m.versao).assinatura() === m.assinatura();
    setRes(igual ? <span class="ok">o replay do registro dá o mesmo pet ({Math.round(performance.now() - t0)} ms)</span>
      : <span class="erro">o replay do registro NÃO dá o mesmo pet</span>);
  };
  return <p style="margin:0"><button type="button" class="dl-btn dl-btn--sec" onClick={conferir}>Conferir replay</button> {res}</p>;
}

export function TelaProvisoria({ aba }: { aba: Aba }) {
  const { motor } = useJogo(), kv = dados(motor, aba);
  return (
    <div class="tela">
      <p class="dl-apoio" style="margin:0">Tela provisória do esqueleto: a tela desenhada entra na Etapa 4.</p>
      {kv.length > 0 && (
        <dl class="kv">{kv.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
      )}
      {aba === "registro" && <ConferirReplay m={motor} />}
    </div>
  );
}
