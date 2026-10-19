/* O painel DigiBrain dos pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 4 e etapa 5; pranchas DigiBrainDesktop e DigiBrain390).
   So le o motor por useJogo(): todo numero sai de Motor.digibrain() (motor/digibrain.ts, com paridade com o Python), do historico e da
   memoria do pet. A tela so escolhe o texto e formata. Nos pets v1 a v10 nao aparece (PW-7). Nada aqui anima para fingir atividade, e
   nenhum rotulo diz "pensando" ou "sentindo". */
import { useState } from "preact/hooks";
import { EMOCAO_TXT, NOME_PET, type AcaoPet, type LoboBarra, type RegraLobos } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import { lutaSeguraTempo } from "../luta.ts";
import { estadoSelo } from "../seloDigiBrain.ts";
import { useTempo } from "../tempo.ts";
import { hhmm } from "../telas/pet/TelaPet.tsx";
import { Folha } from "./Folha.tsx";

/** a regra do instinto que disparou, em texto do jogo */
const REGRA_TXT: Record<RegraLobos, string> = {
  sono_exaustao: "Exausto", sono_continuar: "Ainda com sono", sono_noite: "De noite", pedido_necessidade: "Precisando de você",
  abandono: "Sem cuidado há muito tempo", fome_moderada: "Com fome", tempo_livre: "Tempo livre",
};
/** a acao no infinitivo ("decidiu brincar") */
const ACAO_INF: Record<AcaoPet, string> = {
  ocioso: "ficar à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
};
/** a acao como opcao (curta) */
const ACAO_CURTA: Record<AcaoPet, string> = {
  ocioso: "à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
};
/** as entradas da percepcao, com os nomes da tela do Pet (a fome e a barra "comida") */
const ENTRADA_TXT: Record<string, string> = {
  fome: "comida", higiene: "higiene", energia: "energia", humor: "humor", saude: "saúde", sujeira: "sujeira", dormindo: "dormindo",
  hora: "hora do dia", ticks_sem_cuidado: "tempo sem cuidado", tedio: "tédio", solidao: "solidão", estresse: "estresse", dor: "dor", susto: "susto",
};
/** os lobos das barras, com os nomes do codigo em portugues de tela; o piso so aparece quando entra na conta */
const LOBO_TXT: [LoboBarra, string][] = [["impulsos", "Impulsos"], ["decisao", "Aprendido"], ["corpo", "Corpo"], ["memoria_emocao", "Memória e emoção"], ["piso", "Piso"]];
const COM_SINAL: ReadonlySet<LoboBarra> = new Set(["decisao", "corpo"]);

const pct = (v: number, casas: number, sinal: boolean): string =>
  (sinal && v > 0 ? "+" : "") + (v * 100).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }).replace("-", "−") + "%";
const num = (v: number): string => (v > 0 ? "+" : "") + v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).replace("-", "−");

/** o cerebro A, ICONE ESTATICO: uma cor por lobo (impulsos, aprendido, corpo, memoria e emocao). O connectome (#321) fica na pesquisa ate
    o J5 (CN-1); nada aqui acende nem anima */
export function IconeCerebro({ largura = 32 }: { largura?: number }) {
  return (
    <svg class="db-icone" width={largura} height={Math.round(largura * 56 / 64)} viewBox="0 0 64 56" aria-hidden="true">
      <path d="M32 4C20 4 8 11 8 26c0 13 10 24 24 24s24-11 24-24C56 11 44 4 32 4z" fill="#F4F8FE" stroke="#173A8A" stroke-width="2" />
      <path d="M32 6v42" stroke="#173A8A" stroke-width="1.5" />
      <path d="M12 18c6 0 10 4 10 10" fill="none" stroke="#FFD23F" stroke-width="5" stroke-linecap="round" />
      <path d="M52 18c-6 0-10 4-10 10" fill="none" stroke="#6FE3FF" stroke-width="5" stroke-linecap="round" />
      <path d="M14 38c5-2 10-1 13 3" fill="none" stroke="#E5489F" stroke-width="5" stroke-linecap="round" />
      <path d="M50 38c-5-2-10-1-13 3" fill="none" stroke="#7B3FB8" stroke-width="5" stroke-linecap="round" />
    </svg>
  );
}

/** o selo (seloDigiBrain.ts): "replay" num replay, "ao vivo" so com o tempo do jogo andando, senao "pausado" */
export function SeloDigiBrain({ replay }: { replay: boolean }) {
  const { motor: m, nascendo, erroSave } = useJogo(), { velocidade } = useTempo();
  const estado = estadoSelo({ replay, velocidade, nascendo, erroSave: erroSave !== null, lutaSegura: lutaSeguraTempo(), morto: m.morte !== null });
  return <span class={"db-selo db-selo--" + estado}><i aria-hidden="true" />{estado === "vivo" ? "ao vivo" : estado}</span>;
}

/** a emocao de hoje do pet, como selo a parte com a fonte (PW-6): a ultima emocao da memoria por espacos, a mesma do palco */
function SeloEmocao() {
  const { motor: m } = useJogo();
  const em = (m.pol.mem as unknown as { emocoes: { nome: string }[] }).emocoes, ult = em[em.length - 1];
  return <span class="db-emo">{ult ? <>emoção de hoje: {EMOCAO_TXT[ult.nome][0]} · da memória do pet</> : "nenhuma emoção na memória do pet ainda"}</span>;
}

/** o conteudo do painel, o mesmo no desktop (coluna) e no celular (folha) */
export function ConteudoDigiBrain() {
  const { motor: m } = useJogo(), db = m.digibrain();
  if (db === null) return null;
  const d = db.decisao;
  const ultimas = m.historico.filter(h => h.quem === "pet").slice(-5).reverse();
  return (
    <div class="db-conteudo">
      <section aria-labelledby="db-agora">
        <h3 class="db-sec" id="db-agora">Agora</h3>
        {d ? <div class="db-agora"><b>{REGRA_TXT[d.regra]}: decidiu {ACAO_INF[d.acao]}</b>
          <small>{!d.quem_decidiu.escolha ? "Nesta situação só havia uma opção."
            : d.quem_decidiu.mudou ? `Sem o aprendido, teria decidido ${ACAO_INF[d.quem_decidiu.acao_instinto]}.`
              : "O instinto sozinho faria o mesmo."}</small></div>
          : <div class="db-agora"><small>Ainda não decidiu nada.</small></div>}
      </section>
      {d && <>
        <section aria-labelledby="db-lobos">
          <h3 class="db-sec" id="db-lobos">O peso de cada lobo nesta escolha</h3>
          <ul class="db-barras">
            {LOBO_TXT.filter(([l]) => l !== "piso" || d.barras.piso !== 0).map(([l, txt]) => {
              const v = d.barras[l];
              return <li key={l} data-lobo={l}><span>{txt}</span>
                <span class="db-trilho"><b class={v < 0 ? "neg" : ""} style={{ width: Math.min(100, Math.abs(v) * 100) + "%" }} /></span>
                <em>{pct(v, l === "impulsos" ? 0 : 1, COM_SINAL.has(l))}</em></li>;
            })}
          </ul>
          <SeloEmocao />
        </section>
        <section aria-labelledby="db-perc">
          <h3 class="db-sec" id="db-perc">O que mais pesou</h3>
          {d.percepcao.length ? <ul class="db-chips">{d.percepcao.map(p => <li key={p.entrada}>
            {ENTRADA_TXT[p.entrada] ?? p.entrada} {p.entrada === "dormindo" ? (p.x ? "sim" : "não") : pct(p.x, 0, false)}{" "}
            <span class={p.termo > 0 ? "db-favor" : "db-contra"}>{p.termo > 0 ? "a favor" : "contra"}</span></li>)}</ul>
            : <p class="db-vazio">Nada do que ele lê pesou nesta regra.</p>}
        </section>
        <section aria-labelledby="db-opc">
          <h3 class="db-sec" id="db-opc">As opções e a chance de cada uma</h3>
          <ul class="db-opcoes">{d.chances.map(c => <li key={c.acao} class={c.acao === d.acao ? "esc" : ""}>
            <span>{ACAO_CURTA[c.acao]}{c.acao === d.acao && <small> · escolhida</small>}</span>
            <span class="db-trilho"><b style={{ width: c.chance * 100 + "%" }} /></span><em>{pct(c.chance, 0, false)}</em></li>)}</ul>
        </section>
      </>}
      <section aria-labelledby="db-apr">
        <h3 class="db-sec" id="db-apr">O que aprendeu desde que nasceu</h3>
        {db.aprendido.length ? <ul class="db-aprendeu">{db.aprendido.map(a => <li key={a.acao}>
          <span>{a.desvio > 0 ? "mais" : "menos"} {ACAO_CURTA[a.acao]} do que o instinto</span><em>{num(a.desvio)}</em></li>)}</ul>
          : <p class="db-vazio">Ainda igual ao instinto.</p>}
      </section>
      <section aria-labelledby="db-ult">
        <h3 class="db-sec" id="db-ult">Últimas ações</h3>
        <ol class="db-ultimas">{ultimas.map((h, i) => <li key={i}><span class="dl-lcd">{hhmm(h.t)}</span>{NOME_PET[h.a as AcaoPet] ?? h.a}</li>)}</ol>
      </section>
    </div>
  );
}

/** desktop: o card do painel, na coluna entre o habitat e a coluna de sempre (prancha DigiBrainDesktop) */
export function CardDigiBrain({ replay = false }: { replay?: boolean }) {
  const { motor: m } = useJogo();
  if (m.versao < 11) return null;
  return (
    <section class="dl-card digibrain" aria-labelledby="db-tit">
      <div class="db-cab"><IconeCerebro /><h2 id="db-tit">DigiBrain</h2><SeloDigiBrain replay={replay} /></div>
      <div class="db-rola"><ConteudoDigiBrain /></div>
    </section>
  );
}

/** celular: o botao no canto do palco abre o painel numa folha (prancha DigiBrain390) */
export function BotaoDigiBrain({ replay = false }: { replay?: boolean }) {
  const { motor: m } = useJogo(), [aberto, setAberto] = useState(false);
  if (m.versao < 11) return null;
  return <>
    <button type="button" class="db-botao" aria-haspopup="dialog" onClick={() => setAberto(true)}><IconeCerebro largura={18} />DigiBrain</button>
    {aberto && <Folha titulo="DigiBrain" fechar={() => setAberto(false)}>
      <div class="db-folha-selo"><IconeCerebro /><SeloDigiBrain replay={replay} /></div>
      <ConteudoDigiBrain />
    </Folha>}
  </>;
}
