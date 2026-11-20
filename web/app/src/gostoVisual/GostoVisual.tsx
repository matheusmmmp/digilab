/* O protótipo P0 do gosto visual na tela (docs/futuro/gosto_visual_pet.md, seção 14). Atrás da chave `?gosto_visual=1`; desligado, não
   monta. Fora do motor, do log e do save do pet, exceto o Carinho da janela pequena, que é o do jogo (a ação "acariciar", a porta de
   sempre) e só vale onde o jogo aceita o toque no pet.
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
import { passandoEmPalavras } from "./PainelTv.tsx";
import { pararTv, usarPet, useSessaoTv } from "./sessaoTv.ts";
import { agir } from "../acoes.ts";
import { nomeForma } from "../../motor/index.ts";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { painelTvAberto } from "./painelTvEstado.ts";
import { FilaSinal, sinalDaTvAgora } from "./sinalTv.ts";
import { ToqueTv } from "./ToqueTv.tsx";
import { toqueIgnorado } from "../telas/pet/ToquePet.tsx";
import { lutaSeguraTempo } from "../lutaPocTela.ts";

/** o que o leitor de tela ouve da reação: a frase só é dita quando a reação (`chave`) muda, não quando só o motivo muda, e no máximo
    uma vez a cada ANUNCIO_MS; a frase dita é a do instante em que ela sai */
export const ANUNCIO_MS = 5000;
function useAnuncio(chave: string, texto: string): string {
  const [dito, setDito] = useState(""), ultimo = useRef(-Infinity), agora = useRef(texto);
  agora.current = texto;
  useEffect(() => {
    const espera = Math.max(0, ultimo.current + ANUNCIO_MS - performance.now());
    const t = setTimeout(() => { ultimo.current = performance.now(); setDito(agora.current); }, chave === "" ? 0 : espera);
    return () => clearTimeout(t);
  }, [chave]);
  return dito;
}

/** o selo da captura (UX-GV-6): fixo no topo enquanto a tela do dono é lida, com o Parar */
export function SeloCaptura({ parar, video = false }: { parar: () => void; video?: boolean }) {
  return (
    <div className="tv-selo" role="group" aria-label={video ? "O pet está vendo um vídeo seu" : "O pet está vendo a sua tela"} data-testid="tv-selo">
      <i aria-hidden="true" /><span>{video ? "Vendo um vídeo seu" : "Vendo a sua tela"}</span>
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
  /* o canal entra na frase dita (D-GV-CANAL-6): a troca de canal é anunciada ao leitor de tela, sem o nome da janela */
  const tv = s.origem === "tela" ? `O pet está vendo ${passandoEmPalavras(s)}.` : s.origem === "jogo" ? "A TV do jogo está ligada." : "";
  const dito = useAnuncio(s.origem !== null ? s.leitura?.reacao ?? "" : "", reacao), ligou = useRef(false);
  /* a TV ligando e desligando é dita uma vez, numa região só dela (a reação tem a sua): "A TV foi desligada." fica ANUNCIO_MS e sai */
  const [ditoTv, setDitoTv] = useState("");
  useEffect(() => {
    if (tv) { ligou.current = true; setDitoTv(tv); return; }
    if (!ligou.current) return;
    ligou.current = false; setDitoTv("A TV foi desligada.");
    const t = setTimeout(() => setDitoTv(""), ANUNCIO_MS);
    return () => clearTimeout(t);
  }, [tv]);
  /* o Parar do selo some junto com o selo: com o painel fechado, o foco vai à linha "TV" da pilha (ou ao retrato, no celular) */
  const pararPeloSelo = () => {
    pararTv();
    if (!painelTvAberto()) setTimeout(() => (document.querySelector<HTMLElement>(".pet-hud [data-painel-pet='tv'] .hud-painel__bt") ?? document.querySelector<HTMLElement>(".mm-retrato"))?.focus(), 0);
  };
  /* o Carinho da janela é o do jogo, e a janela fica à mão em qualquer rota: ele só vale onde o toque no pet vale (ToquePet.tsx: sem menu
     nem lugar aberto por cima da cena, sem a bola ou o pet na mão) e sem luta na tela. A sessão redesenha a cada segundo sentido */
  const carinhoVale = (): boolean => !toqueIgnorado() && !lutaSeguraTempo(), podeCarinho = carinhoVale();
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
      {s.origem === "tela" && <SeloCaptura parar={pararPeloSelo} video={s.canal?.tipo === "video"} />}
      <p className="sr-only" role="status" data-testid="tv-anuncio">{ditoTv}</p>
      <p className="sr-only" role="status" data-testid="tv-anuncio-reacao">{s.origem !== null ? dito : ""}</p>
      {janela && s.inato && s.origem !== null && createPortal(
        <JanelaDaTv v={{ sprite, reacao: balao, inato: s.inato, estado: s.estado, origem: s.origem, programa: s.programa, temSom: s.temSom,
          nome: nomeForma(jogo.motor.forma), dito, erro: erroSprite ?? s.erro, podeCarinho }} carinho={() => { if (carinhoVale()) agir("acariciar"); }} parar={pararTv} />, janela.document.body)}
    </>
  );
}
