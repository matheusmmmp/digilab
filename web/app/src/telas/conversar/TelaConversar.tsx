/* Conversar (pranchas UpConversar, ConvChat e ConvEstados): tela cheia com cabecalho (voltar, titulo e como o pet fala
   no nivel dele), faixa de status da fala (ponto + texto), o modo da fala, a conversa em baloes (pet a esquerda com o
   retrato, voce a direita em azul; fala sem base riscada com a nota do verificador; na voz propria, o que ele inventou
   marcado com o lapis), atalhos de ensino e a barra de
   escrever. As falas ficam no log de apresentacao (<chave>.fala.jsonl), nunca no registro do pet; o que o jogador
   escreve nao ensina o pet. Comando pelo chat (TAREFA_COMANDO_CHAT): quando o pet entende um pedido claro ("vai comer"),
   a acao entra na hora pelo mesmo caminho do botao (src/acoes.ts; execucao direta desde 2026-10-01) e o historico marca
   "✓ alimentou". */
import { useEffect, useRef, useState, type FormEvent } from "react";
import { CDJ, OVO, chaveSprite, nomeEstagio, nomeForma, type AcaoDono } from "../../../motor/index.ts";
import { FEITO_DONO, agir } from "../../acoes.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { Peca } from "../../componentes/Imagens.tsx";
import { rotuloLLM, useFalaLLM } from "../../fala.ts";
import { enviarConversa, escolherModo, estadoDoPet, lerLog, useFalaLivre, type ModoFala, type RegistroFala } from "../../falaLivre.ts";
import { rotuloRel } from "../../componentes/Barras.tsx";
import { useJogo } from "../../jogo.ts";

/* como a fala aparece em cada nivel (guia, secao 9) */
const COMO_FALA: Record<string, string> = { bebe: "só emotes", crianca: "ícones e sons", adolescente: "frases curtas", adulto: "frases" };
const MODOS: [ModoFala, string][] = [["template", "Frases prontas"], ["moldura", "Moldura"], ["livre", "Livre"]];
const NOME_MODO: Record<ModoFala, string> = { template: "Frases prontas", moldura: "Moldura por LLM", livre: "Fala livre no aparelho" };
const ATALHOS: [AcaoDono, string, string | null][] = [["elogiar", "Elogiar", "emoji_joinha"], ["repreender", "Repreender", null], ["acariciar", "Carinho", "emoji_coracao"]];
/* pets v11: sem elogio nem bronca; o carinho e o tapa sao gestos no corpo */
const ATALHOS_V11: [AcaoDono, string, string | null][] = [["acariciar", "Carinho", "emoji_coracao"], ["tapa", "Tapa", null]];
const MAX_BALOES = 30;

function RetratoPequeno() {
  const { motor: m, nascendo } = useJogo(), a = useAtlas();
  if (a.tipo !== "ok") return <span className="conv-av" aria-hidden="true" />;
  const img = imagemAtlas(a, nascendo > 0 ? OVO[m.especie] : chaveSprite(m.forma));
  return <span className="conv-av" aria-hidden="true"><img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" /></span>;
}
/** fala do pet: sem base (verificador achou afirmacao sem fato) fica riscada, com a nota embaixo. Pets v7 (voz propria):
    inventar pode, desde que se saiba; a fala fica inteira e a nota marca com o lapis o que ele inventou */
function BalaoPet({ r }: { r: RegistroFala }) {
  const v = r.verificacao, voz = !!r.voz;
  const semBase = !voz && !!v && !v.erro && ((v.nao_suportadas ?? 0) > 0 || !!v.manipulacao);
  const trechos = semBase ? (v!.afirmacoes || []).filter(x => !x.sustentada).map(x => x.trecho) : [];
  const inventou = voz ? r.voz!.invencoes : [];
  return (
    <div className="conv-linha">
      <RetratoPequeno />
      <div className="conv-pilha">
        <div className={`conv-balao conv-balao--pet${semBase ? " conv-balao--sembase" : ""}`}>{r.fala}</div>
        {semBase && <div className="conv-nota"><span className="conv-nota-q">?</span>Sem base{trechos.length ? `: ${trechos.map(t => `«${t}»`).join(", ")}` : ""}{v!.manipulacao ? " · possível manipulação" : ""}.</div>}
        {inventou.length > 0 && <div className="conv-nota"><span className="conv-nota-q">✎</span>Inventou: {inventou.map(t => `«${t}»`).join(", ")}.</div>}
        {!voz && v?.erro && <div className="conv-nota"><span className="conv-nota-q">?</span>O verificador não respondeu.</div>}
        {r.comando_executado && r.comando && <div className="conv-nota conv-nota--feito"><span className="conv-nota-q">✓</span>{FEITO_DONO[r.comando]}</div>}
      </div>
    </div>
  );
}

/** o que o pet pode citar agora (ConvDesktop): o mesmo estado que a pagina manda ao servidor da fala livre; os
    identificadores dos fatos sao do servidor e nao aparecem aqui. So no desktop. */
function Fatos() {
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
    <aside className="conv-fatos" aria-label="O que o pet pode citar agora">
      <div className="conv-fatos-cab dl-malha"><b>O QUE O PET PODE CITAR AGORA</b><span>A fala livre só pode afirmar causa ou lembrança que esteja nesta lista.</span></div>
      <div className="conv-fatos-lista">
        {sec.filter(([, l]) => l.length).map(([t, l]) => <div key={t}><h3>{t}</h3>{l.map((x, i) => <p key={i}>{x}</p>)}</div>)}
      </div>
    </aside>
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
  const enviar = (ev: FormEvent) => { ev.preventDefault(); enviarConversa(msg); setMsg(""); };
  return (
    <section className="conv-tela dl" aria-labelledby="conv-tit">
      <div className="conv-cab dl-faixa">
        <button type="button" className="conv-voltar" aria-label="Voltar para o Pet" onClick={voltar}>
          <svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M10 3 5 8l5 5" /></svg>
        </button>
        <div className="conv-cab-txt">
          <h1 className="dl-num" id="conv-tit">Conversar</h1>
          <span>{nascendo > 0 ? "Digi-Egg" : nomeForma(m.forma)} · {nomeEstagio(m.forma)} · {COMO_FALA[m.estagioAtual]}</span>
        </div>
      </div>
      <div className="conv-status">
        <span className="fala-ponto" data-estado={pronto ? "ok" : "off"} aria-hidden="true" />
        <span>{NOME_MODO[fl.modo]}</span>
        <span className="conv-status-dir" title={r.titulo}>{direita}</span>
      </div>
      <div className="conv-modos" role="group" aria-label="Modo da fala">
        {MODOS.map(([k, rot]) => <button type="button" key={k} className="dl-chip" aria-pressed={fl.modo === k} onClick={() => escolherModo(k)}>{rot}</button>)}
      </div>
      <div className="conv-lista" aria-live="polite">
        {regs.length ? regs.map((x, i) => (
          <div className="conv-troca" key={i}>
            {x.situacao === "conversa" && x.fala_jogador && <div className="conv-balao conv-balao--eu">{x.fala_jogador}</div>}
            <BalaoPet r={x} />
          </div>
        )) : <p className="dl-apoio conv-vazio">{livre ? `Escreva algo para ${nome}.` : "A conversa por texto usa a fala livre (modelo local, experimental). Escolha Livre acima para conversar."}</p>}
        {fl.pendente && <div className="conv-linha"><RetratoPequeno /><div className="conv-balao conv-balao--pet conv-pensando">…</div></div>}
        <div ref={fim} />
      </div>
      <Fatos />
      <p className="dl-apoio conv-rodape">O que você escreve não ensina o pet nem entra no registro dele. Um pedido claro ("vai comer") vira a ação na hora, como o botão.</p>

      <div className="conv-atalhos" role="group" aria-label="Ensinar agora">
        {(m.versao >= 11 ? ATALHOS_V11 : ATALHOS).map(([a, rot, em]) => (
          <button type="button" key={a} className={`conv-atalho${a === "elogiar" ? " conv-atalho--destaque" : ""}`} disabled={nascendo > 0} onClick={() => agir(a)}>
            {em && <Peca nome={em} escala={2} />}{rot}
          </button>
        ))}
      </div>
      <form className="conv-escrever" onSubmit={enviar}>
        <label htmlFor="conv-msg" className="sr-only">Mensagem para {nome}</label>
        <input id="conv-msg" type="text" maxLength={300} autoComplete="off" placeholder={livre ? `Escreva para ${nome}` : "Escolha Livre para escrever"} disabled={!livre}
          value={msg} onChange={ev => setMsg((ev.target as HTMLInputElement).value)} />
        <button type="submit" aria-label="Enviar" disabled={!livre || !msg.trim()}>
          <svg viewBox="0 0 16 16" width="20" height="20" aria-hidden="true"><path d="M2 8h10M8 4l4 4-4 4" /></svg>
        </button>
      </form>
    </section>
  );
}
