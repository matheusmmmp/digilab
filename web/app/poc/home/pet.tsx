/* Os pets da página de entrada: o clipe Idle do atlas de clipes do Digimon UP (Assets/digilab_atlas_up_clipes.json, fora do git), o MESMO
   que o jogo usa para as formas (src/atlas.ts, CLIPES_UP = true: juntarClipes troca o sprite do atlas antigo pelo do atlas de clipes). O
   digilab_atlas_up.json antigo não entra aqui. Desenho num canvas em escala inteira, sem suavizar, como o desenharSprite do jogo.
   - O quadro é [x, y, w, h, ox, oy]: o recorte na folha e o deslocamento dentro da caixa do sprite. A caixa dos clipes é larga (cabe as
     outras ações e a base é o pé), então a página recorta a caixa ao mínimo que contém todos os quadros do Idle (RECORTE abaixo).
   - Os recortes são cópias do atlas, para o espaço não depender da arte (guia, princípio 7). Se o atlas mudar e o Digimon ou o recorte
     não baterem, o pet mostra "erro" na tela.
   - O atlas só é servido no modo dev (poc/vite.config.ts). No build e no e2e ele não existe: cada pet vira uma caixa visível
     "sprite ausente", do tamanho do recorte (guia, princípio 8: falhar alto), e o console recebe um aviso, não um erro.
   - Movimento (guia, seção 11): cada quadro dura o `ms` dele no clipe (133 ms nos da linha do Agumon), só enquanto o pet está na tela;
     com prefers-reduced-motion, o quadro 0 e nada se mexe. */
import { useEffect, useRef, useState, useSyncExternalStore } from "react";

type Quadro = [number, number, number, number, number, number];
interface Clipe { quadros: Quadro[]; ms: number[]; loop: boolean }
interface SpriteClipes { digimon?: string; caixa: [number, number]; clipes: Record<string, Clipe | undefined> }
interface DadosClipes { sprites: Record<string, SpriteClipes> }
type EstadoAtlas =
  | { tipo: "carregando" }
  | { tipo: "ok"; dados: DadosClipes; img: HTMLImageElement }
  | { tipo: "ausente"; motivo: string };

/** a forma na tela (o nome do Digimon) → a chave no atlas de clipes e o recorte [x0, y0, w, h] do Idle dentro da caixa, em pixels nativos */
export const FORMAS = {
  Koromon: { chave: "brasa_bebe", recorte: [55, 39, 42, 39] },
  Tanemon: { chave: "limo_bebe", recorte: [56, 15, 41, 44] },
  Agumon: { chave: "brasa_crianca_sereno", recorte: [32, 9, 46, 53] },
  Greymon: { chave: "brasa_adolescente_brigao", recorte: [22, 9, 57, 63] },
  MetalGreymon: { chave: "brasa_adulto_duelista", recorte: [59, 20, 96, 84] },
  WarGreymon: { chave: "brasa_adulto_furioso", recorte: [84, 52, 80, 90] },
} as const satisfies Record<string, { chave: string; recorte: readonly [number, number, number, number] }>;
export type Forma = keyof typeof FORMAS;

const ATLAS_JSON = "/Assets/digilab_atlas_up_clipes.json";
const ATLAS_PNG = "/Assets/digilab_atlas_up_clipes.png";

/** o menor retângulo da caixa que contém todos os quadros não vazios do clipe */
function recorteDoClipe(c: Clipe): [number, number, number, number] {
  const q = c.quadros.filter(x => x[2] > 0 && x[3] > 0);
  if (q.length === 0) throw new Error("clipe sem quadro");
  const x0 = Math.min(...q.map(x => x[4])), y0 = Math.min(...q.map(x => x[5]));
  const x1 = Math.max(...q.map(x => x[4] + x[2])), y1 = Math.max(...q.map(x => x[5] + x[3]));
  return [x0, y0, x1 - x0, y1 - y0];
}

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
    console.warn("[home] build sem o atlas de clipes do Digimon UP (fica fora do git); os pets aparecem como caixas marcadas");
    queueMicrotask(() => mudar({ tipo: "ausente", motivo: "build sem atlas" }));
    return;
  }
  fetch(ATLAS_JSON)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} em ${ATLAS_JSON}`); return r.json() as Promise<DadosClipes>; })
    .then(dados => new Promise<EstadoAtlas>((ok, falha) => {
      const img = new Image();
      img.onload = () => ok({ tipo: "ok", dados, img });
      img.onerror = () => falha(new Error(`imagem do atlas não carregou: ${ATLAS_PNG}`));
      img.src = ATLAS_PNG;
    }))
    .then(mudar)
    .catch((e: unknown) => {
      const motivo = e instanceof Error ? e.message : String(e);
      console.warn("[home] atlas de clipes do Digimon UP ausente; os pets aparecem como caixas marcadas:", motivo);
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
  /** espelhado */
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
  const { chave, recorte } = FORMAS[forma];
  const [rx, ry, rw, rh] = recorte;
  const tela = useRef<HTMLCanvasElement>(null);
  const [visivel, setVisivel] = useState(false);
  const [quadro, setQuadro] = useState(0);

  const sprite = atlas.tipo === "ok" ? atlas.dados.sprites[chave] : undefined;
  const idle = sprite?.clipes.Idle;
  let erro = "";
  if (atlas.tipo === "ok") {
    if (!sprite) erro = `atlas sem ${chave}`;
    else if (sprite.digimon !== forma) erro = `${chave} é ${sprite.digimon ?? "?"}, não ${forma}`;
    else if (!idle || idle.quadros.length === 0 || idle.quadros.length !== idle.ms.length) erro = `${chave} sem Idle válido`;
    else if (recorteDoClipe(idle).join(",") !== recorte.join(",")) erro = `o recorte de ${forma} mudou no atlas`;
  }

  /* só anima o que está na tela */
  useEffect(() => {
    const el = tela.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setVisivel(e.isIntersecting));
    io.observe(el);
    return () => io.disconnect();
  }, [atlas.tipo, erro]);

  /* cada quadro dura o ms dele no clipe */
  useEffect(() => {
    if (reduzido) { setQuadro(0); return; }
    if (!idle || erro || !visivel || !idle.loop) return;
    const id = window.setTimeout(() => setQuadro(q => (q + 1) % idle.quadros.length), idle.ms[quadro % idle.ms.length]);
    return () => window.clearTimeout(id);
  }, [idle, erro, reduzido, visivel, quadro]);

  /* desenha o quadro em pixel inteiro do aparelho, deslocado pelo recorte */
  useEffect(() => {
    const c = tela.current;
    if (atlas.tipo !== "ok" || !idle || erro || !c) return;
    const d = Math.max(1, Math.round(window.devicePixelRatio || 1));
    const p = esc * d;
    c.width = rw * p;
    c.height = rh * p;
    const g = c.getContext("2d");
    if (!g) throw new Error("canvas 2d indisponível");
    g.imageSmoothingEnabled = false;
    g.clearRect(0, 0, c.width, c.height);
    const [sx, sy, w, h, ox, oy] = idle.quadros[quadro % idle.quadros.length];
    if (w > 0 && h > 0) g.drawImage(atlas.img, sx, sy, w, h, (ox - rx) * p, (oy - ry) * p, w * p, h * p);
  }, [atlas, idle, erro, quadro, esc, rx, ry, rw, rh]);

  const tam = { width: rw * esc, height: rh * esc };
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
