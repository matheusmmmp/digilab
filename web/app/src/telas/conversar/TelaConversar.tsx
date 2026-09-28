/* Conversar (pranchas UpConversar, ConvChat e ConvEstados): tela cheia com cabecalho (voltar, titulo e como o pet fala
   no nivel dele), faixa de status da fala (ponto + texto), o modo da fala, a conversa em baloes (pet a esquerda com o
   retrato, voce a direita em azul; fala sem base riscada com a nota do verificador), atalhos de ensino e a barra de
   escrever. As falas ficam no log de apresentacao (<chave>.fala.jsonl), nunca no registro do pet; o que o jogador
   escreve nao ensina o pet. */
import { useEffect, useRef, useState } from "preact/hooks";
import { OVO, chaveSprite, nomeEstagio, nomeForma, type AcaoDono } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { Peca } from "../../componentes/Imagens.tsx";
import { rotuloLLM, useFalaLLM } from "../../fala.ts";
import { enviarConversa, escolherModo, lerLog, useFalaLivre, type ModoFala, type RegistroFala } from "../../falaLivre.ts";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { ajustarVelocidadeChamado } from "../../tempo.ts";

/* como a fala aparece em cada nivel (guia, secao 9) */
const COMO_FALA: Record<string, string> = { bebe: "só emotes", crianca: "ícones e sons", adolescente: "frases curtas", adulto: "frases" };
const MODOS: [ModoFala, string][] = [["template", "Frases prontas"], ["moldura", "Moldura"], ["livre", "Livre"]];
const NOME_MODO: Record<ModoFala, string> = { template: "Frases prontas", moldura: "Moldura por LLM", livre: "Fala livre no aparelho" };
const ATALHOS: [AcaoDono, string, string | null][] = [["elogiar", "Elogiar", "emoji_joinha"], ["repreender", "Repreender", null], ["acariciar", "Carinho", "emoji_coracao"]];
const MAX_BALOES = 30;

function RetratoPequeno() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas();
  if (a.tipo !== "ok") return <span class="conv-av" aria-hidden="true" />;
  const img = imagemAtlas(a, nascendo > 0 ? OVO[m.especie] : chaveSprite(m.forma));
  return <span class="conv-av" aria-hidden="true"><img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" /></span>;
}
/** fala do pet: sem base (verificador achou afirmacao sem fato) fica riscada, com a nota embaixo */
function BalaoPet({ r }: { r: RegistroFala }) {
  const v = r.verificacao, semBase = !!v && !v.erro && ((v.nao_suportadas ?? 0) > 0 || !!v.manipulacao);
  const trechos = semBase ? (v!.afirmacoes || []).filter(x => !x.sustentada).map(x => x.trecho) : [];
  return (
    <div class="conv-linha">
      <RetratoPequeno />
      <div class="conv-pilha">
        <div class={`conv-balao conv-balao--pet${semBase ? " conv-balao--sembase" : ""}`}>{r.fala}</div>
        {semBase && <div class="conv-nota"><span class="conv-nota-q">?</span>Sem base{trechos.length ? `: ${trechos.map(t => `«${t}»`).join(", ")}` : ""}{v!.manipulacao ? " · possível manipulação" : ""}.</div>}
        {v?.erro && <div class="conv-nota"><span class="conv-nota-q">?</span>O verificador não respondeu.</div>}
      </div>
    </div>
  );
}

export function TelaConversar({ voltar }: { voltar: () => void }) {
  const { motor: m, nascendo } = useJogo(), fl = useFalaLivre(), llm = useFalaLLM(), [msg, setMsg] = useState("");
  const fim = useRef<HTMLDivElement>(null), r = rotuloLLM();
  const regs = lerLog().slice(-MAX_BALOES);
  useEffect(() => { fim.current?.scrollIntoView({ block: "end" }); }, [regs.length, fl.pendente]);
  const nome = nascendo > 0 ? "o ovo" : nomeForma(m.forma), livre = fl.modo === "livre";
  const pronto = livre ? !!fl.status : fl.modo === "moldura" ? llm.ativo : true;
  const direita = livre ? (fl.status ? `${fl.status.modelo} pronto` : fl.statusErro ? "servidor sem a fala livre" : "conferindo…") : r.texto;
  const enviar = (ev: Event) => { ev.preventDefault(); enviarConversa(msg); setMsg(""); };
  const agir = (a: AcaoDono) => { if (nascendo > 0) return; mudarMotor(mm => mm.observar(a)); ajustarVelocidadeChamado(); };
  return (
    <section class="conv-tela dl" aria-labelledby="conv-tit">
      <div class="conv-cab dl-faixa">
        <button type="button" class="conv-voltar" aria-label="Voltar para o Pet" onClick={voltar}>
          <svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M10 3 5 8l5 5" /></svg>
        </button>
        <div class="conv-cab-txt">
          <h1 class="dl-num" id="conv-tit">Conversar</h1>
          <span>{nascendo > 0 ? "Digi-Egg" : nomeForma(m.forma)} · {nomeEstagio(m.forma)} · {COMO_FALA[m.estagioAtual]}</span>
        </div>
      </div>
      <div class="conv-status">
        <span class="fala-ponto" data-estado={pronto ? "ok" : "off"} aria-hidden="true" />
        <span>{NOME_MODO[fl.modo]}</span>
        <span class="conv-status-dir" title={r.titulo}>{direita}</span>
      </div>
      <div class="conv-modos" role="group" aria-label="Modo da fala">
        {MODOS.map(([k, rot]) => <button type="button" key={k} class="dl-chip" aria-pressed={fl.modo === k} onClick={() => escolherModo(k)}>{rot}</button>)}
      </div>
      <div class="conv-lista" aria-live="polite">
        {regs.length ? regs.map((x, i) => (
          <div class="conv-troca" key={i}>
            {x.situacao === "conversa" && x.fala_jogador && <div class="conv-balao conv-balao--eu">{x.fala_jogador}</div>}
            <BalaoPet r={x} />
          </div>
        )) : <p class="dl-apoio conv-vazio">{livre ? `Escreva algo para ${nome}.` : "A conversa por texto usa a fala livre (modelo local, experimental). Escolha Livre acima para conversar."}</p>}
        {fl.pendente && <div class="conv-linha"><RetratoPequeno /><div class="conv-balao conv-balao--pet conv-pensando">…</div></div>}
        <div ref={fim} />
      </div>
      <p class="dl-apoio conv-rodape">O que você escreve não ensina o pet nem entra no registro dele.</p>

      <div class="conv-atalhos" role="group" aria-label="Ensinar agora">
        {ATALHOS.map(([a, rot, em]) => (
          <button type="button" key={a} class={`conv-atalho${a === "elogiar" ? " conv-atalho--destaque" : ""}`} disabled={nascendo > 0} onClick={() => agir(a)}>
            {em && <Peca nome={em} escala={2} />}{rot}
          </button>
        ))}
      </div>
      <form class="conv-escrever" onSubmit={enviar}>
        <label for="conv-msg" class="sr-only">Mensagem para {nome}</label>
        <input id="conv-msg" type="text" maxLength={300} autocomplete="off" placeholder={livre ? `Escreva para ${nome}` : "Escolha Livre para escrever"} disabled={!livre}
          value={msg} onInput={ev => setMsg((ev.target as HTMLInputElement).value)} />
        <button type="submit" aria-label="Enviar" disabled={!livre || !msg.trim()}>
          <svg viewBox="0 0 16 16" width="20" height="20" aria-hidden="true"><path d="M2 8h10M8 4l4 4-4 4" /></svg>
        </button>
      </form>
    </section>
  );
}
