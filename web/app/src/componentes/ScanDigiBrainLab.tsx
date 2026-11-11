/* O DigiBrain do modular no scan (o mesmo modal pequeno do A v11, ScanDigiBrain.tsx, D1b e D1c da UX_TELA_PET), pedido pelo Matheus em 2026-11-11:
   o pet do cerebro modular abria o painel antigo (DigiBrainLab.tsx), e o visual novo tem de valer para ele tambem. A casca e a mesma: o
   <dialog> pequeno sob o relogio (a folha baixa no celular), o titulo, o selo, o "i", o mapa em texto, o fechar e a varredura numa decisao nova.
   O desenho e a rede viva do scan do A (D1e; o Matheus, 2026-11-11, "Sim, leve"): uma ILUSTRACAO do cerebro em atividade, nao o mapa dos
   modulos. O mapa com os 7 modulos, a soma e as opcoes, que este scan desenhava, saiu; o que ele mostrava esta no mapa em texto (as barras
   dos modulos e as opcoes com a chance). Do motor (Motor.leituraLab()) o desenho e a faixa usam:
     - a semente do pet, que da a rede dele;
     - quantos modulos contribuiram na escolha (as barras), que da quantos impulsos correm;
     - a onda: um pico por modulo que contribuiu (na ordem de ORDEM_TERMOS), para cima a favor e para baixo contra, da altura da parte dele
       sobre a maior parte em modulo;
     - a escolha de agora (a acao da unidade escolhida) e a chance dela, no lugar do "estado atual" do A: o modular nao tem as regras do
       instinto, entao nao tem um estado com nome. O tom e sempre o neutro.
   So le o motor por useJogo(); nenhum mudarMotor aqui. O "mapa em texto" e o painel de antes inteiro (ConteudoDigiBrainLab), com a
   intencao, as sondas, os conceitos e as ultimas acoes. */
import { useEffect, useRef, useState, type CSSProperties, type MouseEvent, type ReactNode, type SyntheticEvent } from "react";
import { Brain, Info, List, X } from "lucide-react";
import { ORDEM_TERMOS, type LeituraLab } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import "../estilo/scan_digibrain.css";
import { ConteudoDigiBrainLab, rotuloUnidade, textoResultado } from "./DigiBrainLab.tsx";
import { resultadoAnterior } from "../../motor/index.ts";
import { abrirModal } from "./modal.ts";
import {
  Faixa, GIRO_CICLO_S, GIRO_GRAUS, PULSO_MS, RedeVivaDesenho, SeloForma, VARREDURA_MS, useDecisaoNova, useEscalaDoMapa, useReduzirMovimento, type PicoOnda,
} from "./ScanDigiBrain.tsx";
import { useEstadoSelo } from "./DigiBrain.tsx";

/** os picos da onda do modular: um por modulo que contribuiu, com a parte dele (em permil, com sinal) sobre a maior parte em modulo */
export function picosDoModular(l: LeituraLab): PicoOnda[] {
  const maior = Math.max(1, ...l.barras.map(b => Math.abs(b.permil)));
  return l.barras.map(b => ({ entrada: b.termo, altura: b.permil / maior }));
}
/** a escolha de agora em texto curto: a acao da unidade escolhida e a chance dela ("única" sem sorteio). A unidade inteira vai na dica do rotulo */
export function escolhaDoModular(l: LeituraLab): { curto: string; chance: string; inteiro: string } {
  const esc = l.chances.find(c => c.escolhida);
  if (esc === undefined) throw new Error("a leitura do modular sem a opcao escolhida");
  return { curto: rotuloUnidade([esc.chave[0], null, null]), chance: esc.permil === null ? "única" : Math.round(esc.permil / 10) + "%", inteiro: rotuloUnidade(esc.chave) };
}
/** a faixa do modular: a onda dos modulos e a escolha de agora */
export function FaixaLab({ l }: { l: LeituraLab }) {
  const e = escolhaDoModular(l);
  return (
    <Faixa n={l.k} entradas={ORDEM_TERMOS} picos={picosDoModular(l)} rotulo="escolha" tom="neutro" titulo={e.inteiro}>
      {e.curto}<span className="scan-estado-pct">{e.chance}</span>
    </Faixa>
  );
}

function DicaLab({ aberta }: { aberta: boolean }) {
  return (
    <div className="scan-dica scan-cx" id="db-dica" hidden={!aberta}>
      <p>A rede é só desenho: ela imita um cérebro em atividade, não mostra as ligações de verdade. Cada pet tem a sua.</p>
      <p className="scan-dica-selo">Quanto mais módulos pesaram na escolha de agora, mais impulsos correm.</p>
      <p className="scan-dica-selo">Embaixo: a onda tem um pico por módulo que pesou, para cima a favor e para baixo contra; ao lado, o que ele escolheu e com que chance.</p>
      <p className="scan-dica-selo">O mapa em texto tem o resto: os módulos, as opções, a lembrança, a intenção e os conceitos. Ao lado do título: o ponto é ao vivo, as duas barras são pausado e o triângulo é um replay.</p>
    </div>
  );
}

export function ScanDigiBrainLab({ fechar, movel, replay = false, chamado }: { fechar: () => void; movel: boolean; replay?: boolean; chamado?: ReactNode }) {
  const { motor: m } = useJogo();
  if (!m.lab) throw new Error("o scan do modular so abre no pet do cerebro modular");
  const l = m.leituraLab(), res = resultadoAnterior(m.lab);
  const ref = useRef<HTMLDialogElement>(null), saindo = useRef(false);
  const giro = useRef<HTMLDivElement>(null), [verTexto, setVerTexto] = useState(false), [verDica, setVerDica] = useState(false);
  useEscalaDoMapa(giro, l !== null && !verTexto);
  const selo = useEstadoSelo(replay), reduzir = useReduzirMovimento();
  const mov = useDecisaoNova(l ? l.k : null, selo === "vivo" && !reduzir);
  useEffect(() => {
    const dlg = ref.current; if (!dlg) return;
    saindo.current = false;
    abrirModal(dlg);
    return () => { saindo.current = true; if (dlg.open) dlg.close(); };
  }, []);
  const cancelar = (e: SyntheticEvent<HTMLDialogElement>) => { if (verDica) { e.preventDefault(); setVerDica(false); } };
  const cliqueFora = (e: MouseEvent<HTMLDialogElement>) => { if (e.target === e.currentTarget) ref.current?.close(); };
  return (
    <dialog className={"scan scan--lab" + (movel ? " scan--folha" : "")} id="pet-painel" data-painel-pet="digibrain" aria-labelledby="db-titulo" ref={ref}
      style={{ "--scan-giro-graus": GIRO_GRAUS + "deg", "--scan-giro-ciclo": GIRO_CICLO_S + "s", "--scan-t-varre": VARREDURA_MS + "ms", "--scan-t-pulso": PULSO_MS + "ms" } as CSSProperties}
      onCancel={cancelar} onClick={cliqueFora} onClose={() => { if (!saindo.current) fechar(); }}>
      <div className="scan-in scan-cx digibrain">
        {movel && <span className="scan-alca" aria-hidden="true" />}
        <header className="scan-topo">
          <h2 className="scan-tit" id="db-titulo"><Brain aria-hidden="true" /><span className="scan-tit-nome">DigiBrain</span><span className="sr-only">, cérebro modular</span></h2>
          <SeloForma replay={replay} />
          <button type="button" className="scan-ic scan-info" aria-label="O que é este desenho" aria-expanded={verDica} aria-controls="db-dica"
            onClick={() => setVerDica(v => !v)}><Info aria-hidden="true" /></button>
          <button type="button" className="scan-ic scan-texto-bt" aria-label="O mapa em texto" aria-pressed={verTexto}
            onClick={() => setVerTexto(v => !v)}><List aria-hidden="true" /></button>
          <button type="button" className="scan-ic scan-fechar" aria-label="Fechar DigiBrain" title="Fechar (Esc)" data-autofocus onClick={() => ref.current?.close()}>
            <X aria-hidden="true" /></button>
        </header>
        <DicaLab aberta={verDica} />
        <div className="scan-corpo">
          <div className="scan-moldura">
            {/* os cantos em colchete do scanner: so desenho; saem no mapa em texto, para nao ficarem por cima das letras */}
            {!verTexto && l !== null && <><i className="scan-canto scan-canto--ce" aria-hidden="true" /><i className="scan-canto scan-canto--cd" aria-hidden="true" /><i className="scan-canto scan-canto--be" aria-hidden="true" /><i className="scan-canto scan-canto--bd" aria-hidden="true" /></>}
            {verTexto || l === null
              ? <section className="scan-texto db-texto dl digibrain pet-painel__folha" id="db-texto" aria-label="O mapa em texto" tabIndex={0}><ConteudoDigiBrainLab /></section>
              : <>
                {mov !== null && <div className="scan-varre-trilho" key={"varre" + mov} aria-hidden="true"><div className="scan-varredura" /></div>}
                <div className="scan-giro" ref={giro}><RedeVivaDesenho semente={m.semente} n={l.k} pesaram={l.barras.length} tom="neutro" movel={movel} correndo={selo === "vivo"} surto={mov !== null} /></div>
              </>}
          </div>
          {l !== null && <FaixaLab l={l} />}
          {/* o resultado da decisao anterior numa linha (CADEIA, etapa 3): o que ele fez e o que mudou nele */}
          {res && !verTexto && <p className="scan-resultado" data-testid="resultado-anterior" data-k={res.k}>{textoResultado(res)}</p>}
        </div>
      </div>
      {chamado}
    </dialog>
  );
}
