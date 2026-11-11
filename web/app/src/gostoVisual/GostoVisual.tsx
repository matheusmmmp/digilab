/* O protótipo P0 do gosto visual na tela (docs/futuro/gosto_visual_pet.md, seção 14). Atrás da chave `?gosto_visual=1`; desligado, não
   monta. Fora do motor, do log e do save do pet.
   Desde a etapa 1 do docs/PLANO_UX_GOSTO_VISUAL.md (2026-11-11) o cartão do canto saiu (UX-GV-1): o controle e a leitura estão no painel
   da TV (PainelTv.tsx), e o carinho é o Carinho do jogo (UX-GV-7). Aqui fica o hospedeiro: o selo da captura, os avisos ao leitor de
   tela e a janela pequena, cujo miolo é a JanelaTv.tsx desde a etapa 3 (a vista `PetAssistindo` do P0 saiu). */
import "../estilo/gosto_visual.css";
import { useEffect, useRef, useState } from "react";
import { Square } from "lucide-react";
import { createPortal } from "react-dom";
import { useJogo } from "../jogo.ts";
import { fonteDoPet } from "../telas/pet/fontePet.ts";
import { gostoVisualLigado } from "./chave.ts";
import { fecharJanelaDaTv, useJanelaDaTv } from "./janelaPequena.ts";
import { JanelaDaTv } from "./JanelaTv.tsx";
import { fraseDaReacao } from "./leituraGosto.ts";
import { pararTv, usarPet, useSessaoTv } from "./sessaoTv.ts";
import { agir } from "../acoes.ts";
import { nomeForma } from "../../motor/index.ts";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { FilaSinal, sinalDaTvAgora } from "./sinalTv.ts";
import { ToqueTv } from "./ToqueTv.tsx";

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
  /* o sinal da reação sobre o pet, no lugar dos emotes (sinalTv.ts): o palco o lê pela cena enquanto o protótipo está montado */
  useEffect(() => { CENA.sinalTv = sinalDaTvAgora; return () => { CENA.sinalTv = null; }; }, []);
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
  /* na janela pequena: o balão troca no ritmo do sinal (no mínimo 3 s, sinalTv.ts); ao abrir, o foco vai ao Carinho; o Esc a fecha (o
     "Trazer de volta" do painel) e a TV continua */
  const balao = useRef(new FilaSinal()).current.passo(s.origem !== null ? s.leitura?.reacao ?? null : null, performance.now());
  useEffect(() => {
    if (!janela) return;
    const d = janela.document, tecla = (e: KeyboardEvent) => { if (e.key === "Escape") { e.preventDefault(); fecharJanelaDaTv(); } };
    d.addEventListener("keydown", tecla);
    const t = setTimeout(() => d.querySelector<HTMLElement>("[data-janela-tv-carinho]")?.focus(), 0);
    return () => { d.removeEventListener("keydown", tecla); clearTimeout(t); };
  }, [janela]);
  return (
    <>
      <ToqueTv />
      {s.origem === "tela" && <SeloCaptura parar={pararTv} />}
      <p className="sr-only" role="status" data-testid="tv-anuncio">{tv || fim} {s.origem !== null ? dito : ""}</p>
      {janela && s.inato && s.origem !== null && createPortal(
        <JanelaDaTv v={{ sprite, reacao: balao, inato: s.inato, estado: s.estado, origem: s.origem, programa: s.programa, temSom: s.temSom,
          nome: nomeForma(jogo.motor.forma), dito, erro: erroSprite ?? s.erro }} carinho={() => { agir("acariciar"); }} parar={pararTv} />, janela.document.body)}
    </>
  );
}
