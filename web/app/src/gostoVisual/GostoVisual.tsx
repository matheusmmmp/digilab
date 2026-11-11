/* O protótipo P0 do gosto visual na tela (docs/futuro/gosto_visual_pet.md, seção 14). Atrás da chave `?gosto_visual=1`; desligado, não
   monta. Fora do motor, do log e do save do pet.
   Desde a etapa 1 do docs/PLANO_UX_GOSTO_VISUAL.md (2026-11-11) o cartão do canto saiu (UX-GV-1): o controle e a leitura estão no painel
   da TV (PainelTv.tsx), e o carinho é o Carinho do jogo (UX-GV-7). Aqui ficam o hospedeiro (o selo da captura, os avisos ao leitor de
   tela, a janela pequena) e a vista `PetAssistindo`, que hoje só a janela pequena usa (ela é redesenhada na etapa 3). */
import "../estilo/gosto_visual.css";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Square } from "lucide-react";
import { createPortal } from "react-dom";
import { useJogo } from "../jogo.ts";
import { fonteDoPet } from "../telas/pet/fontePet.ts";
import { gostoVisualLigado } from "./chave.ts";
import { fecharJanelaDaTv, useJanelaDaTv } from "./janelaPequena.ts";
import { fraseDaReacao } from "./leituraGosto.ts";
import { passandoEmPalavras } from "./PainelTv.tsx";
import { pararTv, usarPet, useSessaoTv } from "./sessaoTv.ts";
import { agir } from "../acoes.ts";
import { BALAO } from "./estadoTv.ts";
import {
  COMPONENTES, NOME_COMPONENTE, alvos, gostaMaisDe, tempoJunto, valores, type Componente, type EstadoGosto, type Inato, type Leitura, type Sentido,
} from "./gosto.ts";

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
      <p className="gv-linha">Assistindo junto: <strong data-testid="gv-tempo">{tempoJunto(v.estado.segundosJuntos)}</strong></p>
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

/** o que o leitor de tela ouve: a reação quando ela muda (no máximo uma a cada ANUNCIO_MS) e a TV ligando e desligando */
export const ANUNCIO_MS = 5000;
function useAnuncio(texto: string): string {
  const [dito, setDito] = useState(""), ultimo = useRef(-Infinity);
  useEffect(() => {
    const espera = Math.max(0, ultimo.current + ANUNCIO_MS - performance.now());
    const t = setTimeout(() => { ultimo.current = performance.now(); setDito(texto); }, texto === "" ? 0 : espera);
    return () => clearTimeout(t);
  }, [texto]);
  return dito;
}

/** o selo da captura (UX-GV-6): fixo no topo enquanto a tela do dono é lida, com o Parar */
export function SeloCaptura({ parar }: { parar: () => void }) {
  return (
    <div className="tv-selo" role="group" aria-label="O pet está vendo a sua tela" data-testid="tv-selo">
      <i aria-hidden="true" /><span>Vendo a sua tela</span>
      <button type="button" className="hx-btn tv-selo__bt" onClick={parar}><Square aria-hidden="true" />Parar</button>
    </div>
  );
}

/** o hospedeiro do protótipo; null com a chave desligada */
export function GostoVisual() {
  if (!gostoVisualLigado()) return null;
  return <GostoVisualLigado />;
}

/* Desde a etapa 1 do PLANO_UX_GOSTO_VISUAL (UX-GV-1) o cartão do canto saiu: o controle e a leitura moram no painel da TV (PainelTv.tsx,
   aberto pela tela Pet), e o estado mora na sessão (sessaoTv.ts). Aqui fica o que precisa existir com o painel fechado: o pet de agora
   entregue à sessão, o selo da captura, os avisos ao leitor de tela e a janela pequena. */
function GostoVisualLigado() {
  const jogo = useJogo(), semente = jogo.motor.semente, s = useSessaoTv(), janela = useJanelaDaTv();
  const [sprite, setSprite] = useState<string | null>(null), [erroSprite, setErroSprite] = useState<string | null>(null);
  useEffect(() => { usarPet(semente); }, [semente]);
  /* a TV e a janela não sobrevivem ao protótipo desmontado */
  useEffect(() => () => { pararTv(); fecharJanelaDaTv(); }, []);
  /* parar a TV fecha a janela pequena (o plano, 3.3); fechar a janela não para a TV */
  useEffect(() => { if (s.origem === null) fecharJanelaDaTv(); }, [s.origem]);
  /* o sprite do pet para a janela pequena, a cada meio segundo, do mesmo jeito que a cena 3D o pega; só com a janela aberta */
  useEffect(() => {
    if (!janela) return;
    let q = 0;
    const t = setInterval(() => { try { setSprite(fonteDoPet(q++).canvas.toDataURL()); } catch (x) { setErroSprite(`o sprite do pet não desenhou: ${(x as Error).message}`); } }, 500);
    return () => clearInterval(t);
  }, [janela]);
  const reacao = s.inato && s.leitura ? fraseDaReacao(s.inato, s.estado, s.sentido, s.leitura.reacao) : "";
  const tv = s.origem === "tela" ? "O pet está vendo a sua tela." : s.origem === "jogo" ? "A TV do jogo está ligada." : "";
  const dito = useAnuncio(reacao), ligou = useRef(false);
  const fim = !tv && ligou.current ? "A TV foi desligada." : "";
  useEffect(() => { ligou.current = s.origem !== null; }, [s.origem]);
  const aviso = (erroSprite ?? s.erro) && <div className="aviso gv-aviso" role="alert" data-testid="gv-erro">{erroSprite ?? s.erro}</div>;
  const acoes = (
    <>
      <button type="button" className="gv-botao gv-botao--forte" onClick={() => { agir("acariciar"); }}>Carinho</button>
      <button type="button" className="gv-botao" onClick={pararTv}>Parar</button>
    </>
  );
  return (
    <>
      {s.origem === "tela" && <SeloCaptura parar={pararTv} />}
      <p className="sr-only" role="status" data-testid="tv-anuncio">{tv || fim} {s.origem !== null ? dito : ""}</p>
      {janela && s.inato && createPortal(
        <div className="gv-na-janela">{aviso}
          <PetAssistindo v={{ sprite, leitura: s.leitura, sentido: s.sentido, inato: s.inato, estado: s.estado, capturando: s.origem !== null, temSom: s.temSom,
            origem: passandoEmPalavras(s) }} acoes={acoes} />
        </div>, janela.document.body)}
    </>
  );
}
