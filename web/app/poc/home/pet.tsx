/* Os pets da página de entrada: o ciclo parado (Idle) do atlas do jogo (Assets/digilab_atlas_up.json, fora do git), desenhado num
   canvas em escala inteira, sem suavizar, como o desenharSprite do jogo (src/atlas.ts). O quadro é [x, y, w, h, ox, oy]: o recorte na
   folha e o deslocamento dentro da caixa comum do ciclo.
   - O atlas só é servido no modo dev (poc/vite.config.ts). No build e no e2e ele não existe: cada pet vira uma caixa visível
     "sprite ausente", do tamanho da caixa dele (guia, princípio 8: falhar alto), e o console recebe um aviso, não um erro.
   - As caixas abaixo são cópias do atlas, para o espaço não depender da arte (guia, princípio 7). Se o atlas mudar e a caixa ou o
     Digimon não baterem, o pet mostra o erro na tela.
   - Movimento (guia, seção 11): um quadro a cada ms_por_quadro do atlas (120 ms), só enquanto o pet está na tela; com
     prefers-reduced-motion, o quadro 0 e nada se mexe. */
import { useEffect, useRef, useState, useSyncExternalStore } from "react";

type Quadro = [number, number, number, number, number, number];
interface SpriteAtlas { digimon?: string; caixa: [number, number]; quadros: Quadro[] }
interface DadosAtlas { ms_por_quadro: number; sprites: Record<string, SpriteAtlas> }
type EstadoAtlas =
  | { tipo: "carregando" }
  | { tipo: "ok"; dados: DadosAtlas; img: HTMLImageElement }
  | { tipo: "ausente"; motivo: string };

/** a forma na tela (o nome do Digimon) → a chave no atlas e a caixa do ciclo, em pixels nativos */
export const FORMAS = {
  Koromon: { chave: "brasa_bebe", caixa: [42, 36] },
  Tanemon: { chave: "limo_bebe", caixa: [36, 40] },
  Agumon: { chave: "brasa_crianca_sereno", caixa: [46, 49] },
  Greymon: { chave: "brasa_adolescente_brigao", caixa: [57, 58] },
  MetalGreymon: { chave: "brasa_adulto_duelista", caixa: [91, 79] },
  WarGreymon: { chave: "brasa_adulto_furioso", caixa: [80, 82] },
} as const satisfies Record<string, { chave: string; caixa: readonly [number, number] }>;
export type Forma = keyof typeof FORMAS;

const ATLAS_JSON = "/Assets/digilab_atlas_up.json";
const ATLAS_PNG = "/Assets/digilab_atlas_up.png";

/* ---- o atlas: carregado uma vez, para todos os pets */
let estado: EstadoAtlas = { tipo: "carregando" };
const ouvintes = new Set<() => void>();
let pedido = false;
function mudar(novo: EstadoAtlas): void { estado = novo; ouvintes.forEach(f => f()); }
function carregar(): void {
  if (pedido) return;
  pedido = true;
  /* no build da POC o atlas não é servido: nem pede (um 404 viraria erro no console do e2e) */
  if (!import.meta.env.DEV) {
    console.warn("[home] build sem o atlas do Digimon UP (fica fora do git); os pets aparecem como caixas marcadas");
    queueMicrotask(() => mudar({ tipo: "ausente", motivo: "build sem atlas" }));
    return;
  }
  fetch(ATLAS_JSON)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} em ${ATLAS_JSON}`); return r.json() as Promise<DadosAtlas>; })
    .then(dados => new Promise<EstadoAtlas>((ok, falha) => {
      const img = new Image();
      img.onload = () => ok({ tipo: "ok", dados, img });
      img.onerror = () => falha(new Error(`imagem do atlas não carregou: ${ATLAS_PNG}`));
      img.src = ATLAS_PNG;
    }))
    .then(mudar)
    .catch((e: unknown) => {
      const motivo = e instanceof Error ? e.message : String(e);
      /* aviso, não erro: no build da POC o atlas não existe de propósito (fica fora do git) */
      console.warn("[home] atlas do Digimon UP ausente; os pets aparecem como caixas marcadas:", motivo);
      mudar({ tipo: "ausente", motivo });
    });
}
function useAtlas(): EstadoAtlas {
  useEffect(carregar, []);
  return useSyncExternalStore(f => { ouvintes.add(f); return () => { ouvintes.delete(f); }; }, () => estado);
}

/* ---- movimento reduzido e largura (a escala inteira muda a 600 px) */
function useMedia(q: string): boolean {
  return useSyncExternalStore(f => {
    const m = matchMedia(q);
    m.addEventListener("change", f);
    return () => m.removeEventListener("change", f);
  }, () => matchMedia(q).matches);
}
export const useReduzido = (): boolean => useMedia("(prefers-reduced-motion: reduce)");
const useLargo = (): boolean => useMedia("(min-width: 600px)");

interface PropsPet {
  forma: Forma;
  /** escala inteira abaixo de 600 px */
  k: number;
  /** escala inteira de 600 px em diante (padrão: a mesma) */
  kLargo?: number;
  /** espelhado (olhando para a direita) */
  vira?: boolean;
  /** decorativo: o nome já está escrito ao lado */
  decorativo?: boolean;
}

export function Pet({ forma, k, kLargo, vira = false, decorativo = false }: PropsPet) {
  const atlas = useAtlas();
  const reduzido = useReduzido();
  const largo = useLargo();
  const esc = largo ? (kLargo ?? k) : k;
  if (!Number.isInteger(esc) || esc < 1) throw new Error(`escala de sprite só inteira: ${forma} ${esc}`);
  const { chave, caixa } = FORMAS[forma];
  const [cw, ch] = caixa;
  const tela = useRef<HTMLCanvasElement>(null);
  const [visivel, setVisivel] = useState(false);
  const [quadro, setQuadro] = useState(0);

  const sprite = atlas.tipo === "ok" ? atlas.dados.sprites[chave] : undefined;
  let erro = "";
  if (atlas.tipo === "ok") {
    if (!sprite) erro = `atlas sem ${chave}`;
    else if (sprite.digimon !== forma) erro = `${chave} é ${sprite.digimon ?? "?"}, não ${forma}`;
    else if (sprite.caixa[0] !== cw || sprite.caixa[1] !== ch) erro = `caixa de ${forma} mudou no atlas`;
  }

  /* só anima o que está na tela */
  useEffect(() => {
    const el = tela.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setVisivel(e.isIntersecting));
    io.observe(el);
    return () => io.disconnect();
  }, [atlas.tipo, erro]);

  useEffect(() => {
    if (atlas.tipo !== "ok" || !sprite || erro || reduzido || !visivel) { if (reduzido) setQuadro(0); return; }
    const n = sprite.quadros.length;
    const id = window.setInterval(() => setQuadro(q => (q + 1) % n), atlas.dados.ms_por_quadro);
    return () => window.clearInterval(id);
  }, [atlas, sprite, erro, reduzido, visivel]);

  /* desenha o quadro em pixel inteiro do aparelho */
  useEffect(() => {
    const c = tela.current;
    if (atlas.tipo !== "ok" || !sprite || erro || !c) return;
    const d = Math.max(1, Math.round(window.devicePixelRatio || 1));
    const p = esc * d;
    c.width = cw * p;
    c.height = ch * p;
    const g = c.getContext("2d");
    if (!g) throw new Error("canvas 2d indisponível");
    g.imageSmoothingEnabled = false;
    g.clearRect(0, 0, c.width, c.height);
    const [sx, sy, w, h, ox, oy] = sprite.quadros[quadro % sprite.quadros.length];
    g.drawImage(atlas.img, sx, sy, w, h, ox * p, oy * p, w * p, h * p);
  }, [atlas, sprite, erro, quadro, esc, cw, ch]);

  const tam = { width: cw * esc, height: ch * esc };
  const rotulo = decorativo ? {} : { role: "img", "aria-label": forma };
  const ocultar = decorativo ? { "aria-hidden": true } : {};
  if (atlas.tipo === "ausente" || erro) {
    return (
      <span className="pet pet-ausente" style={tam} title={erro || atlas.tipo} {...rotulo} {...ocultar}>
        <span aria-hidden="true">{erro ? "erro" : "sprite"}<br />{forma}</span>
      </span>
    );
  }
  return <canvas ref={tela} className={vira ? "pet vira" : "pet"} style={tam} {...rotulo} {...ocultar} />;
}
