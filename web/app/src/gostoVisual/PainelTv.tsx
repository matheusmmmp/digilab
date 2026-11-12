/* O painel da TV (docs/PLANO_UX_GOSTO_VISUAL.md e a prancha docs/pranchas/ux-gosto-visual/, aprovados pelo Matheus em 2026-11-11): o
   controle e a leitura do "pet assistindo TV", no lugar do cartão do canto (UX-GV-1). A tela Pet o abre pelo sistema de painéis dela
   (TelaPet.tsx: a linha "TV" da pilha a partir de 900 px, o leque do retrato abaixo); aqui fica só o miolo.
   - ligar: a TV do jogo é o botão principal; "Mostrar minha tela" é o segundo, com a frase fixa da privacidade (UX-GV-6), e some onde o
     navegador não captura;
   - a leitura em dois níveis (UX-GV-4): a frase "Gosta mais de"; o porquê a um toque, com as três origens separadas (UX-GV-5: de nascença,
     de tanto ver, do carinho, cada uma com a forma dela); o que está passando numa faixa à parte;
   - o carinho é o Carinho do jogo (UX-GV-7): aqui não há botão de carinho, e nenhuma contagem de carinhos (a GV-14: o jogo não pontua);
   - no celular (UX-GV-8) o painel é uma folha baixa: recolhida, a reação e o gosto; "Mais" a estica.
   - no pet com a TV no cérebro (a v32, a v35 e o grupo v36; D-GV-CEREBRO-8): a reação é a do cérebro (o que o motor diz que ele faz, a
     mesma fonte do painel do DigiBrain), o botão "Levar até a TV" aparece quando a TV está fora da vista dele, e o rodapé diz que o que passa
     entra no cérebro. O gosto ("Gosta mais de", o porquê) é o do cérebro (a decisão C, D-GV-TVJOGO-5): o genoma da visão e a exposição do
     DigiBrain; o carinho ainda não entra nele.
   Só existe com `?gosto_visual=1`. Fora do motor, do log e do save, salvo o "st" e o levar o pet da v32 (cerebroTv.ts). */
import { useEffect, useRef, useState, type ReactNode } from "react";
import { ChevronRight, Lock, MonitorUp, PictureInPicture2, Square, Tv } from "lucide-react";
import { COMPONENTES, alvos, gostaMaisDe, tempoJunto, valores, type Componente } from "./gosto.ts";
import { abrirJanelaDaTv, fecharJanelaDaTv, temJanelaPequena, useJanelaDaTv } from "./janelaPequena.ts";
import {
  IMAGEM, SOM, descricaoDaLinha, fraseDaReacao, linhasDoCerebro, linhasDoGosto, linhasMarcadas, nascencaDifere, ondeFica, pontosDasLinhas, type LinhaGosto,
} from "./leituraGosto.ts";
import { ligarTela, ligarTvJogo, pararTv, podeMostrarTela, useSessaoTv, type SessaoTv } from "./sessaoTv.ts";
import { leituraDoCerebro, levarPetATv } from "./cerebroTv.ts";
import { useJogoSeHouver } from "../jogo.ts";

export const FRASE_PRIVACIDADE = "Ele só sente cores, brilho, movimento e som: sete números por segundo. Nenhuma imagem é guardada e nada sai deste computador.";
const pct = (x: number): string => `${Math.round(Math.min(1, Math.max(0, x)) * 1000) / 10}%`;

/** o que está passando, em palavras: "a sua tela" ou "a TV do jogo, <programa>" */
export const passandoEmPalavras = (s: Pick<SessaoTv, "origem" | "programa">): string | null =>
  s.origem === "tela" ? "a sua tela" : s.origem === "jogo" ? (s.programa ? `a TV do jogo, ${s.programa}` : "a TV do jogo") : null;

/** uma linha do porquê: um trilho, o traço de nascença, a seta pontilhada "de tanto ver", a malha tracejada "do carinho" e o losango de hoje */
function Linha({ l, pulso }: { l: LinhaGosto; pulso: number }) {
  const a = l.nascenca, b = Math.min(1, Math.max(0, a + l.deVer)), c = l.hoje;
  return (
    <li className="tvp-linha"><span className="tvp-linha__img" role="img" aria-label={descricaoDaLinha(l)}>
      <b className="tvp-nome">{l.nome}</b>
      <span className="tvp-trilho" aria-hidden="true">
        <i className="tvp-nasc" style={{ left: pct(a) }} />
        {Math.abs(b - a) > 0.004 && <i className={"tvp-ver " + (b > a ? "tvp-ver--dir" : "tvp-ver--esq")} style={{ left: pct(Math.min(a, b)), width: pct(Math.abs(b - a)) }} />}
        {Math.abs(c - b) > 0.004 && <i key={pulso} className="tvp-car" style={{ left: pct(Math.min(b, c)), width: pct(Math.abs(c - b)) }} />}
        <i className="tvp-hoje" style={{ left: pct(c) }} />
      </span>
      <span className="tvp-ext" aria-hidden="true"><span>{l.baixo}</span><span>{l.alto}</span></span>
    </span></li>
  );
}

/** uma linha do que está passando: o mesmo trilho, só com o círculo do agora */
function LinhaAgora({ l, agora }: { l: LinhaGosto; agora: number }) {
  return (
    <li className="tvp-linha">
      <b className="tvp-nome">{l.nome}<span className="sr-only">: {ondeFica(l, agora)}</span></b>
      <span className="tvp-trilho" aria-hidden="true"><i className="tvp-agora" style={{ left: pct(agora) }} /></span>
      <span className="tvp-ext" aria-hidden="true"><span>{l.baixo}</span><span>{l.alto}</span></span>
    </li>
  );
}

const Legenda = () => (
  <p className="tvp-legenda" aria-hidden="true">
    <span><i className="tvp-leg"><i className="tvp-nasc" /></i>de nascença</span>
    <span><i className="tvp-leg"><i className="tvp-ver tvp-ver--dir" /></i>de tanto ver</span>
    <span><i className="tvp-leg"><i className="tvp-car" /></i>do elogio</span>
    <span><i className="tvp-leg"><i className="tvp-hoje" /></i>hoje</span>
  </p>
);

function Abre({ aberto, alternar, children, mais = false }: { aberto: boolean; alternar: () => void; children: ReactNode; mais?: boolean }) {
  return (
    <button type="button" className="tvp-abre" aria-expanded={aberto} data-tv-mais={mais ? "" : undefined} onClick={alternar}>
      <ChevronRight aria-hidden="true" className={aberto ? "tvp-seta tvp-seta--aberta" : "tvp-seta"} />{children}
    </button>
  );
}

const Privacidade = () => <p className="tvp-priv"><Lock aria-hidden="true" /><span>{FRASE_PRIVACIDADE}</span></p>;

/** o miolo do painel: `nome` é o nome da forma do pet (o do Digimon); `movel` é a folha do celular */
export function PainelTv({ nome, movel }: { nome: string; movel: boolean }) {
  const s = useSessaoTv(), janela = useJanelaDaTv(), motor = useJogoSeHouver()?.motor ?? null;
  const [porque, setPorque] = useState(false), [todos, setTodos] = useState(false), [passando, setPassando] = useState(false), [mais, setMais] = useState(false);
  /* ligar e parar trocam o botão que tinha o foco por outro: o foco vai para o botão novo, senão cai fora do painel e o Esc não o fecha */
  const ligada = s.origem !== null, raiz = useRef<HTMLDivElement>(null), ligadaAntes = useRef(ligada);
  useEffect(() => {
    if (ligadaAntes.current === ligada) return;
    ligadaAntes.current = ligada;
    const a = document.activeElement;
    if (!a || a === document.body) raiz.current?.querySelector<HTMLElement>(ligada ? "[data-tv-parar]" : "[data-tv-ligar]")?.focus();
  }, [ligada]);
  /* "Mais" e "Menos" da folha do celular trocam a árvore inteira: o foco vai para o botão que ficou no lugar */
  const maisAntes = useRef(mais);
  useEffect(() => {
    if (maisAntes.current === mais) return;
    maisAntes.current = mais;
    raiz.current?.querySelector<HTMLElement>("[data-tv-mais]")?.focus();
  }, [mais]);
  if (!s.inato) return <p className="tvp-fraco">O pet ainda não está aqui.</p>;
  const comTela = podeMostrarTela() && !movel, comJanela = temJanelaPequena() && !movel;
  /* sem som na captura, o grupo do som não entra nas contas (o pet não ouve) */
  const quais: readonly Componente[] = ligada && !s.temSom ? IMAGEM : COMPONENTES;
  /* o pet com a TV no cérebro: o gosto é o do cérebro (a decisão C, D-GV-TVJOGO-5); nos outros pets, o do protótipo */
  const gv = motor === null ? null : motor.gostoVisualDoCerebro();
  const linhas = gv !== null ? linhasDoCerebro(gv.nascenca, gv.deVer, quais) : linhasDoGosto(s.inato, s.estado, quais);
  const curtas = linhasMarcadas(linhas), agora = s.sentido ? valores(s.sentido) : {};
  const img = linhas.filter(l => IMAGEM.includes(l.k)), som = linhas.filter(l => SOM.includes(l.k));
  /* a v32: a reação é a do cérebro (D-GV-CEREBRO-8); nos outros pets, a do protótipo */
  const cer = motor === null ? null : leituraDoCerebro(motor);
  const frase = cer !== null && ligada ? cer.frase : s.leitura ? fraseDaReacao(s.inato, s.estado, s.sentido, s.leitura.reacao) : ligada ? "Ligando…" : null;
  const levar = cer !== null && motor !== null && !cer.noRaio && !motor.e.dormindo && motor.morte === null
    ? <button type="button" className="hx-btn tvp-cheio" data-tv-levar="" onClick={levarPetATv}>Levar até a TV</button> : null;
  const noCerebro = cer !== null && !ligada ? <p className="tvp-fraco" data-testid="tv-cerebro">{cer.frase}</p> : null;
  const gosto = `Gosta mais de: ${gv !== null ? gostaMaisDe(pontosDasLinhas(linhas, "hoje"), quais) : gostaMaisDe(alvos(s.inato, s.estado), quais)}.`;
  const nascDifere = gv !== null ? gostaMaisDe(pontosDasLinhas(linhas, "nascenca"), quais) !== gostaMaisDe(pontosDasLinhas(linhas, "hoje"), quais)
    : nascencaDifere(s.inato, s.estado, quais);
  const nascFrase = gv !== null ? gostaMaisDe(pontosDasLinhas(linhas, "nascenca"), quais) : gostaMaisDe(s.inato.otimo, quais);

  const controle = ligada ? (
    <div className="tvp-sec">
      <p className="tvp-fraco" data-testid="tv-passando">Passando: {passandoEmPalavras(s)}</p>
      <p className="tvp-forte" data-testid="tv-reacao">{frase}</p>
      {s.origem === "tela" && !s.temSom && <p className="tvp-fraco">Ele não está ouvindo. Para ouvir, compartilhe de novo e marque o áudio.</p>}
      {levar}
      <div className="tvp-bts">
        <button type="button" className="hx-btn" data-tv-parar="" onClick={pararTv}><Square aria-hidden="true" />Parar</button>
        {comJanela && (janela
          ? <button type="button" className="hx-btn" onClick={fecharJanelaDaTv}><PictureInPicture2 aria-hidden="true" />Trazer de volta</button>
          : <button type="button" className="hx-btn" onClick={() => void abrirJanelaDaTv()}><PictureInPicture2 aria-hidden="true" />Janela pequena</button>)}
      </div>
      {janela && <p className="tvp-fraco">Ele está na janela pequena.</p>}
    </div>
  ) : (
    <div className="tvp-sec">
      {noCerebro}
      <button type="button" className="hx-continuar tvp-cheio" data-tv-ligar="" onClick={ligarTvJogo}><Tv aria-hidden="true" />Ligar a TV</button>
      {comTela && <button type="button" className="hx-btn tvp-cheio" onClick={() => void ligarTela()}><MonitorUp aria-hidden="true" />Mostrar minha tela</button>}
      {levar}
      {comTela && <Privacidade />}
    </div>
  );

  const leitura = (
    <div className="tvp-sec">
      <h3 className="tvp-tit">Do que o {nome} gosta</h3>
      <p className="tvp-forte" data-testid="tv-gosto" data-gosto-fonte={gv !== null ? "cerebro" : "prototipo"}>{gosto}</p>
      {nascDifere && <p className="tvp-fraco" data-testid="tv-nascenca">De nascença, preferia {nascFrase}.</p>}
      <Abre aberto={porque} alternar={() => setPorque(v => !v)}>Por quê</Abre>
      {porque && (todos ? (
        <>
          <p className="tvp-grupo">Imagem</p>
          <ul className="tvp-linhas">{img.map(l => <Linha key={l.k} l={l} pulso={s.carinhosVistos} />)}</ul>
          <p className="tvp-grupo">Som</p>
          {som.length > 0 ? <ul className="tvp-linhas">{som.map(l => <Linha key={l.k} l={l} pulso={s.carinhosVistos} />)}</ul> : <p className="tvp-fraco">Ele não está ouvindo.</p>}
        </>
      ) : <ul className="tvp-linhas">{curtas.map(l => <Linha key={l.k} l={l} pulso={s.carinhosVistos} />)}</ul>)}
      {porque && <Legenda />}
      {porque && <button type="button" className="hx-btn tvp-p" onClick={() => setTodos(v => !v)}>{todos ? "Ver menos" : "Ver todos"}</button>}
      {ligada && <Abre aberto={passando} alternar={() => setPassando(v => !v)}>O que está passando</Abre>}
      {ligada && passando && (
        <>
          <ul className="tvp-linhas" aria-label="O que a TV mostra agora, por componente">
            {linhas.filter(l => agora[l.k] !== undefined).map(l => <LinhaAgora key={l.k} l={l} agora={agora[l.k]!} />)}
          </ul>
          <p className="tvp-fraco">O círculo é o que a TV mostra agora.</p>
        </>
      )}
    </div>
  );

  const rodape = (
    <div className="tvp-sec">
      <p className="tvp-fraco" data-testid="tv-tempo">Assistiram juntos: {tempoJunto(s.estado.segundosJuntos)}</p>
      {ligada && s.origem === "tela" && <Privacidade />}
      {cer !== null
        ? <p className="tvp-fraco tvp-prot" data-testid="tv-prot">O que a TV passa entra no cérebro dele: sete números a cada 10 segundos, no registro. O gosto acima é o do cérebro: o de nascença e o de tanto ver (o elogio ainda não entra nele).</p>
        : <p className="tvp-fraco tvp-prot" data-testid="tv-prot">Protótipo: o gosto ainda não entra no cérebro do pet.</p>}
    </div>
  );

  const erro = s.erro && <p className="tvp-erro" role="alert" data-testid="tv-erro">{s.erro}</p>;
  /* a folha do celular, recolhida: a reação (ou o botão de ligar) e o gosto; "Mais" abre o resto */
  if (movel && !mais) return (
    <div className="tvp tvp--recolhida" data-testid="painel-tv" ref={raiz}>
      {erro}
      <div className="tvp-sec">
        {ligada ? <p className="tvp-forte" data-testid="tv-reacao">{frase}</p>
          : <button type="button" className="hx-continuar tvp-cheio" data-tv-ligar="" onClick={ligarTvJogo}><Tv aria-hidden="true" />Ligar a TV</button>}
        {noCerebro}
        <p data-testid="tv-gosto">{gosto}</p>
        {levar}
        <div className="tvp-bts">
          {ligada && <button type="button" className="hx-btn" data-tv-parar="" onClick={pararTv}><Square aria-hidden="true" />Parar</button>}
          <Abre aberto={false} alternar={() => setMais(true)} mais>Mais</Abre>
        </div>
      </div>
    </div>
  );
  return (
    <div className="tvp" data-testid="painel-tv" ref={raiz}>
      {erro}
      {controle}
      {leitura}
      {rodape}
      {movel && <div className="tvp-sec"><Abre aberto alternar={() => setMais(false)} mais>Menos</Abre></div>}
    </div>
  );
}
