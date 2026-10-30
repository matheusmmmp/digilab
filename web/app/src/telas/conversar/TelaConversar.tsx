/* Conversar na pele XCOM (layout habitat, M5), dentro do PainelTela (o titulo e o "x" sao do painel): como o pet fala no nivel
   dele, faixa de status da fala (ponto + texto), o modo da fala, a conversa em baloes (pet a esquerda com o retrato, voce a
   direita em ciano palido; fala sem base riscada com a nota do verificador), atalhos de ensino e a barra de escrever.
   As falas ficam no log de apresentacao (<chave>.fala.jsonl), nunca no registro do pet; o que o jogador escreve nao ensina o pet.
   Comando pelo chat (TAREFA_COMANDO_CHAT): quando o pet entende um pedido claro ("vai comer"), a acao entra na hora pelo mesmo
   caminho do botao (src/acoes.ts) e o historico marca "✓ alimentou". */
import { useEffect, useRef, useState, type FormEvent } from "react";
import "../../estilo/menus_config.css";
import { CDJ, OVO, chaveSprite, nomeEstagio, nomeForma, type AcaoDono } from "../../../motor/index.ts";
import { FEITO_DONO, agir } from "../../acoes.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { Peca } from "../../componentes/Imagens.tsx";
import { BotaoHx } from "../../componentes/hx/index.ts";
import { useDesktop } from "../../desktop.ts";
import { rotuloLLM, useFalaLLM } from "../../fala.ts";
import { enviarConversa, escolherModo, estadoDoPet, lerLog, useFalaLivre, type ModoFala, type RegistroFala } from "../../falaLivre.ts";
import { rotuloRel } from "../../componentes/Barras.tsx";
import { useJogo } from "../../jogo.ts";

/* como a fala aparece em cada nivel (guia, secao 9) */
const COMO_FALA: Record<string, string> = { bebe: "só emotes", crianca: "ícones e sons", adolescente: "frases curtas", adulto: "frases" };
const MODOS: [ModoFala, string][] = [["template", "Frases prontas"], ["moldura", "Moldura"], ["livre", "Livre"]];
const NOME_MODO: Record<ModoFala, string> = { template: "Frases prontas", moldura: "Moldura por LLM", livre: "Fala livre no aparelho" };
/* pets v11: sem elogio nem bronca; o carinho e o tapa sao gestos no corpo */
const ATALHOS_V11: [AcaoDono, string, string | null][] = [["acariciar", "Carinho", "emoji_coracao"], ["tapa", "Tapa", null]];
const MAX_BALOES = 30;

function RetratoPequeno() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas();
  if (a.tipo !== "ok") return <span className="mc-av" aria-hidden="true" />;
  const img = imagemAtlas(a, nascendo > 0 ? OVO[m.especie] : chaveSprite(m.forma));
  return <span className="mc-av" aria-hidden="true"><img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" /></span>;
}
/** fala do pet: sem base (verificador achou afirmacao sem fato) fica riscada, com a nota embaixo */
function BalaoPet({ r }: { r: RegistroFala }) {
  const v = r.verificacao;
  const semBase = !!v && !v.erro && ((v.nao_suportadas ?? 0) > 0 || !!v.manipulacao);
  const trechos = semBase ? (v!.afirmacoes || []).filter(x => !x.sustentada).map(x => x.trecho) : [];
  return (
    <div className="mc-conv__linha">
      <RetratoPequeno />
      <div className="mc-pilha">
        <div className={`mc-balao${semBase ? " mc-balao--sembase" : ""}`}>{r.fala}</div>
        {semBase && <div className="mc-nota"><b>?</b>Sem base{trechos.length ? `: ${trechos.map(t => `«${t}»`).join(", ")}` : ""}{v!.manipulacao ? " · possível manipulação" : ""}.</div>}
        {v?.erro && <div className="mc-nota"><b>?</b>O verificador não respondeu.</div>}
        {r.comando_executado && r.comando && <div className="mc-nota mc-nota--feito"><b>✓</b>{FEITO_DONO[r.comando]}</div>}
      </div>
    </div>
  );
}

/** o que o pet pode citar agora: o mesmo estado que a pagina manda ao servidor da fala livre; os identificadores dos fatos
    sao do servidor e nao aparecem aqui */
function Fatos({ aberto }: { aberto: boolean }) {
  const { motor: m } = useJogo();
  const s = estadoDoPet(m) as Record<string, any>, blocos = (x: number) => `${Math.round(Math.max(0, Math.min(1, x)) * 5)} de 5`;
  const extremos = (o: Record<string, number> | undefined, rot: string) => Object.entries(o || {}).filter(([, v]) => Math.abs(v) >= CDJ.limiarTom).map(([k, v]) => `${rot}: ${k} ${rotuloRel(v)}`);
  const sec: [string, string[]][] = [
    ["Identidade", [`${nomeForma(m.forma)}, ${nomeEstagio(m.forma)}${s.identidade.linha ? ", linha " + s.identidade.linha : ""}`]],
    ["Só os extremos", [...extremos(s.temperamento, "temperamento"), ...extremos(s.carater, "caráter")]],
    ["Estado", [`fome ${blocos(s.estado.fome)}`, `energia ${blocos(s.estado.energia)}`, `humor ${blocos(s.estado.humor)}`, ...(s.estado.emocao ? [`emoção: ${s.estado.emocao}`] : []), `fadiga ${s.estado.fadiga}`]],
    ["Memórias", (s.memorias || []).map((x: any) => `${x.evento} · há ${x.ha_min} min`)],
    ["Motivos recentes", (s.motivos || []).map((x: any) => `${x.acao}${x.fatores?.length ? " · " + x.fatores.join(", ") : ""}`)],
    ["Vínculo", s.vinculo != null ? [s.vinculo >= .66 ? "alto (sem número)" : s.vinculo >= .33 ? "médio (sem número)" : "baixo (sem número)"] : []],
  ];
  return (
    <details className="mc-fatos" open={aberto}>
      <summary>O que o pet pode citar agora</summary>
      <div className="mc-fatos__corpo">
        <p className="mc-apoio">A fala livre só pode afirmar causa ou lembrança que esteja nesta lista.</p>
        {sec.filter(([, l]) => l.length).map(([t, l]) => <div key={t}><h3>{t}</h3>{l.map((x, i) => <p key={i}>{x}</p>)}</div>)}
      </div>
    </details>
  );
}

export function TelaConversar(_: { voltar: () => void }) {
  const { motor: m, nascendo } = useJogo(), fl = useFalaLivre(), llm = useFalaLLM(), [msg, setMsg] = useState(""), desk = useDesktop();
  const fim = useRef<HTMLDivElement>(null), r = rotuloLLM();
  const regs = lerLog().slice(-MAX_BALOES);
  useEffect(() => { fim.current?.scrollIntoView({ block: "end" }); }, [regs.length, fl.pendente]);
  const nome = nascendo > 0 ? "o ovo" : nomeForma(m.forma), livre = fl.modo === "livre";
  const pronto = livre ? !!fl.status : fl.modo === "moldura" ? llm.ativo : true;
  const direita = livre ? (fl.status ? `${fl.status.modelo} pronto` : fl.statusErro ? "servidor sem a fala livre" : "conferindo…") : r.texto;
  const enviar = (ev: FormEvent) => { ev.preventDefault(); enviarConversa(msg); setMsg(""); };
  return (
    <section className="mc mc-conv" aria-label="Conversar">
      <p className="mc-apoio">{nascendo > 0 ? "Digi-Egg" : nomeForma(m.forma)} · {nomeEstagio(m.forma)} · {COMO_FALA[m.estagioAtual]}</p>
      <div className="mc-status mc-conv__status">
        <span className="mc-ponto" data-estado={pronto ? "ok" : "off"} aria-hidden="true" />
        <span>{NOME_MODO[fl.modo]}</span>
        <span className="mc-apoio" title={r.titulo} style={{ marginLeft: "auto" }}>{direita}</span>
      </div>
      <div className="mc-linha" role="group" aria-label="Modo da fala">
        {MODOS.map(([k, rot]) => <BotaoHx key={k} aria-pressed={fl.modo === k} onClick={() => escolherModo(k)}>{rot}</BotaoHx>)}
      </div>
      <div className="mc-conv__lista" aria-live="polite">
        {regs.length ? regs.map((x, i) => (
          <div className="mc-troca" key={i}>
            {x.situacao === "conversa" && x.fala_jogador && <div className="mc-balao mc-balao--eu">{x.fala_jogador}</div>}
            <BalaoPet r={x} />
          </div>
        )) : <p className="mc-apoio">{livre ? `Escreva algo para ${nome}.` : "A conversa por texto usa a fala livre (modelo local, experimental). Escolha Livre acima para conversar."}</p>}
        {fl.pendente && <div className="mc-conv__linha"><RetratoPequeno /><div className="mc-balao">…</div></div>}
        <div ref={fim} />
      </div>
      <div className="mc-conv__atalhos" role="group" aria-label="Ensinar agora">
        {ATALHOS_V11.map(([a, rot, em]) => (
          <BotaoHx key={a} disabled={nascendo > 0} onClick={() => agir(a)}>{em && <Peca nome={em} escala={2} />}{rot}</BotaoHx>
        ))}
      </div>
      <form className="mc-conv__escrever" onSubmit={enviar}>
        <label htmlFor="conv-msg" className="sr-only">Mensagem para {nome}</label>
        <input id="conv-msg" type="text" maxLength={300} autoComplete="off" placeholder={livre ? `Escreva para ${nome}` : "Escolha Livre para escrever"} disabled={!livre}
          value={msg} onChange={ev => setMsg((ev.target as HTMLInputElement).value)} />
        <BotaoHx type="submit" aria-label="Enviar" disabled={!livre || !msg.trim()}>
          <svg viewBox="0 0 16 16" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 8h10M8 4l4 4-4 4" /></svg>
        </BotaoHx>
      </form>
      <p className="mc-apoio">O que você escreve não ensina o pet nem entra no registro dele. Um pedido claro ("vai comer") vira a ação na hora, como o botão.</p>
      <Fatos aberto={desk} />
    </section>
  );
}
