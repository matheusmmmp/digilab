/* O protótipo P0 do gosto visual na tela (docs/futuro/gosto_visual_pet.md, seção 14): um cartão no canto da página, que pode ir para a
   janela pequena flutuante. O dono compartilha a tela (e o som), o pet olha ou desvia, o balão diz o que ele sente, o painel mostra o
   gosto de nascença e o de hoje separados (GV-14), e o tempo assistindo junto. Atrás da chave `?gosto_visual=1`; desligado, não monta.
   Fora do motor, do log e do save do pet: o carinho daqui não é a ação de carinho do jogo, é só a associação do protótipo. */
import "../estilo/gosto_visual.css";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { useJogo } from "../jogo.ts";
import { fonteDoPet } from "../telas/pet/fontePet.ts";
import { gostoVisualLigado } from "./chave.ts";
import { capturarTela, type Captura } from "./captura.ts";
import { abrirJanelaPequena } from "./janelaPequena.ts";
import { ligarTvDoJogo } from "./tvDoJogo.ts";
import {
  COMPONENTES, NOME_COMPONENTE, alvos, chaveGuardada, doTexto, estadoInicial, gostaMaisDe, inatoDaSemente, paraTexto, passo, tempoJunto,
  valores, type Componente, type EstadoGosto, type Inato, type Leitura, type Reacao, type Sentido,
} from "./gosto.ts";

const BALAO: Record<Reacao, string> = {
  adorando: "♥ adorando!", olhando: "olhando…", enjoou: "enjoei disso", nao_gosta: "não curti", curioso: "? o que é isso", distraido: "…",
};
const SOM_COMPONENTES: readonly Componente[] = ["volume", "variacao", "timbre"];

export interface VistaPet {
  sprite: string | null;
  leitura: Leitura | null;
  sentido: Sentido | null;
  inato: Inato;
  estado: EstadoGosto;
  capturando: boolean;
  temSom: boolean;
  /** de onde vem: a tela do dono ou o programa da TV do jogo */
  origem: string | null;
}

/** a vista do pet assistindo, sem estado próprio (o teste a renderiza no node) */
export function PetAssistindo({ v, acoes }: { v: VistaPet; acoes: ReactNode }) {
  const reac = v.leitura?.reacao ?? null, quais = v.temSom || !v.capturando ? COMPONENTES : COMPONENTES.filter(k => !SOM_COMPONENTES.includes(k));
  const hoje = alvos(v.inato, v.estado), agora = v.sentido ? valores(v.sentido) : {};
  return (
    <div className="gv-cartao" data-testid="gosto-visual">
      <div className="gv-palco">
        <div className="gv-tela" aria-hidden="true" style={{ filter: v.sentido ? `brightness(${0.4 + v.sentido.visao.brilho}) saturate(${v.sentido.visao.cor * 2})` : undefined }} />
        <div className={"gv-pet" + (reac ? ` gv-pet--${reac}` : "")}>
          {reac && <div className="gv-balao" role="status">{BALAO[reac]}</div>}
          {v.sprite ? <img className="dl-pix gv-sprite" src={v.sprite} alt="o pet" /> : <div className="gv-sprite gv-sprite--vazio">pet</div>}
        </div>
      </div>
      {v.origem && <p className="gv-linha gv-fraca" data-testid="gv-origem">Assistindo: {v.origem}</p>}
      <p className="gv-linha"><strong>Gosta mais de:</strong> {gostaMaisDe(hoje, quais)}</p>
      <p className="gv-linha gv-fraca">De nascença: {gostaMaisDe(v.inato.otimo, quais)}</p>
      <p className="gv-linha">Assistindo junto: <strong data-testid="gv-tempo">{tempoJunto(v.estado.segundosJuntos)}</strong> · carinhos: {v.estado.carinhos}</p>
      <ul className="gv-barras" aria-label="o gosto por componente: de nascença, de hoje e o que passa agora">
        {quais.map(k => (
          <li key={k}>
            <span className="gv-nome">{NOME_COMPONENTE[k]}</span>
            <span className="gv-trilho">
              <span className="gv-marca gv-marca--inato" style={{ left: `${v.inato.otimo[k] * 100}%` }} title="de nascença" />
              <span className="gv-marca gv-marca--hoje" style={{ left: `${hoje[k] * 100}%` }} title="hoje (nascença + exposição + carinho)" />
              {agora[k] !== undefined && <span className="gv-marca gv-marca--agora" style={{ left: `${agora[k]! * 100}%` }} title="o que passa agora" />}
            </span>
          </li>
        ))}
      </ul>
      <p className="gv-legenda"><span className="gv-ponto gv-marca--inato" /> nascença <span className="gv-ponto gv-marca--hoje" /> hoje <span className="gv-ponto gv-marca--agora" /> agora</p>
      {v.capturando && !v.temSom && <p className="gv-linha gv-fraca">Sem som: marque "compartilhar áudio" para o pet ouvir também.</p>}
      <div className="gv-acoes">{acoes}</div>
    </div>
  );
}

function lerGuardado(semente: number): EstadoGosto {
  const t = localStorage.getItem(chaveGuardada(semente));
  return t === null ? estadoInicial() : doTexto(t);
}

/** o cartão do protótipo; null com a chave desligada */
export function GostoVisual() {
  if (!gostoVisualLigado()) return null;
  return <GostoVisualLigado />;
}

function GostoVisualLigado() {
  const jogo = useJogo(), semente = jogo.motor.semente;
  const [inato, setInato] = useState(() => inatoDaSemente(semente));
  const [estado, setEstado] = useState<EstadoGosto>(estadoInicial);
  const [leitura, setLeitura] = useState<Leitura | null>(null);
  const [sentido, setSentido] = useState<Sentido | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [captura, setCaptura] = useState<Captura | null>(null);
  const [origem, setOrigem] = useState<string | null>(null);
  const [janela, setJanela] = useState<Window | null>(null);
  const [sprite, setSprite] = useState<string | null>(null);
  const [aberto, setAberto] = useState(true);
  const carinho = useRef(false), estadoRef = useRef(estado), inatoRef = useRef(inato);

  /* o pet de agora: o inato vem da semente; o aprendido, do que este navegador guardou para ele */
  useEffect(() => {
    try { const e = lerGuardado(semente); const i = inatoDaSemente(semente); setInato(i); inatoRef.current = i; setEstado(e); estadoRef.current = e; setErro(null); }
    catch (x) { setErro(`o gosto guardado deste pet não abriu: ${(x as Error).message}`); }
  }, [semente]);
  /* o sprite do pet, a cada meio segundo, do mesmo jeito que a cena 3D o pega */
  useEffect(() => {
    let q = 0;
    const t = setInterval(() => { try { setSprite(fonteDoPet(q++).canvas.toDataURL()); } catch (x) { setErro(`o sprite do pet não desenhou: ${(x as Error).message}`); } }, 500);
    return () => clearInterval(t);
  }, []);
  useEffect(() => () => captura?.parar(), [captura]);
  useEffect(() => { if (!janela) return; const f = () => setJanela(null); janela.addEventListener("pagehide", f); return () => janela.removeEventListener("pagehide", f); }, [janela]);

  const sentir = (s: Sentido): void => {
    const { estado: e, leitura: l } = passo(inatoRef.current, estadoRef.current, s, carinho.current);
    carinho.current = false;
    estadoRef.current = e;
    setEstado(e); setLeitura(l); setSentido(s);
    try { localStorage.setItem(chaveGuardada(semente), paraTexto(e)); } catch (x) { setErro(`o gosto não foi guardado neste navegador: ${(x as Error).message}`); }
  };
  const ligar = async (): Promise<void> => {
    setErro(null);
    try { setCaptura(await capturarTela(sentir, m => { setCaptura(null); setOrigem(null); setLeitura(null); setSentido(null); setErro(m); })); setOrigem("a sua tela"); }
    catch (x) { setErro(`a tela não foi compartilhada: ${(x as Error).message}`); }
  };
  const ligarTv = (): void => {
    setErro(null);
    const tv = ligarTvDoJogo(semente, (s, nome) => { setOrigem(`a TV do jogo, ${nome}`); sentir(s); });
    setCaptura({ parar: tv.parar, temSom: true }); setOrigem("a TV do jogo");
  };
  const desligar = (): void => { captura?.parar(); setCaptura(null); setOrigem(null); setLeitura(null); setSentido(null); };
  const flutuar = async (): Promise<void> => {
    setErro(null);
    try { setJanela(await abrirJanelaPequena()); } catch (x) { setErro(`a janela pequena não abriu: ${(x as Error).message}`); }
  };

  const acoes = (
    <>
      {captura ? <button type="button" className="gv-botao" onClick={desligar}>Parar de mostrar</button>
        : <><button type="button" className="gv-botao gv-botao--forte" onClick={() => void ligar()}>Mostrar minha tela</button>
          <button type="button" className="gv-botao" onClick={ligarTv}>Ligar a TV do jogo</button></>}
      <button type="button" className="gv-botao" disabled={!captura} onClick={() => { carinho.current = true; }}>Fazer carinho</button>
      {janela ? <button type="button" className="gv-botao" onClick={() => janela.close()}>Voltar para a página</button>
        : <button type="button" className="gv-botao" onClick={() => void flutuar()}>Janela pequena</button>}
    </>
  );
  const vista = <PetAssistindo v={{ sprite, leitura, sentido, inato, estado, capturando: !!captura, temSom: !!captura?.temSom, origem }} acoes={acoes} />;
  const aviso = erro && <div className="aviso gv-aviso" role="alert" data-testid="gv-erro">{erro}</div>;
  return (
    <aside className="gv-canto" aria-label="O pet assistindo a sua tela (protótipo)">
      <div className="gv-cabeca">
        <strong>TV do pet</strong> <span className="gv-selo">protótipo</span>
        <button type="button" className="gv-botao gv-mini" onClick={() => setAberto(a => !a)} aria-expanded={aberto}>{aberto ? "–" : "+"}</button>
      </div>
      {aviso}
      {aberto && (janela ? <p className="gv-linha">O pet está na janela pequena.</p> : vista)}
      {aberto && <p className="gv-legenda">Só sete números por segundo saem da tela e do som; o quadro e o áudio são descartados e nada é enviado.</p>}
      {janela && createPortal(<div className="gv-na-janela">{aviso}{vista}</div>, janela.document.body)}
    </aside>
  );
}
