/* A camera solta da ilha (L1 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md, secao "Lugares da ilha (L1)"): so a partir de 900 px
   e com o controle "Livre" (habitat.ts), a camera deixa de seguir o pet e anda pela ilha.
   - WASD e as setas andam no chao, na direcao em que a camera olha (W e a frente); arrastar com o botao direito ou o do meio leva o chao
     junto; o minimapa (Minimapa.tsx) leva a camera a um ponto (com uma transicao curta) ou junto do arrasto;
   - F, um toque no retrato (Topo.tsx), o botao "seguir o pet" e o aviso de borda voltam a camera ao pet (seguirPet);
   - Q e E giram e + e - aproximam, como Shift + roda e a roda (orbita.ts, L1-5).
   O giro, a inclinacao e o zoom (a ORBITA) continuam valendo em volta do ponto olhado, que e o pet enquanto a camera segue.
   So vista: fora do save, do registro e do replay, como a ORBITA; o estado fica so nesta pagina. A vista da ilha (ilha/vista.ts) pede o
   ponto olhado a cada quadro (focoDoQuadro) e publica o que a HUD e o minimapa leem (publicarVista). Os numeros sao PROPOSTO, SEM FONTE
   (L1-7, aprovados como proposta pelo Matheus em 2026-11-06). */
import { useSyncExternalStore } from "react";
import { CENA } from "./cenaEstado.ts";
import { aproximar, girar } from "./orbita.ts";

/** celulas por segundo no WASD; a distancia (celulas) a partir da qual o "seguir o pet" aparece; a transicao (ms) ao voltar ao pet ou ir a
    um ponto do minimapa; o giro (rad) e o fator de zoom por toque de Q/E e de +/- */
export const VEL_CELULAS_S = 12, SEGUIR_DIST = 6, TRANSICAO_MS = 400, GIRO_TECLA = 0.12, ZOOM_TECLA = 1.12;
/** a largura em que a camera pode soltar: a mesma da pilha e do trilho (TelaPet.tsx, CONSULTA_LARGO) */
export const CONSULTA_SOLTA = "(min-width: 900px)";

export type Par = [number, number];
/** o retangulo em que o ponto olhado pode andar (celulas; a grade da ilha inteira, grade.ts) */
export interface Limites { x0: number; z0: number; x1: number; z1: number }
type Lado = "esquerda" | "direita" | "cima" | "baixo";

/** o estado da camera, so desta pagina */
export const LIVRE: {
  solta: boolean; foco: Par;
  trans: { de: Par; para: Par | "pet"; desde: number } | null;
} = { solta: false, foco: [0, 0], trans: null };
/** as teclas de andar seguradas agora */
const teclas = new Set<string>();

/** o que a vista publica a cada quadro: o minimapa le aqui (sem React), e a HUD le o resumo (useCameraLivre) */
export interface MapaDaIlha {
  /** a ilha vista de cima, uma celula por pixel (ilha/minimapa.ts) */
  imagem: ImageData;
  /** a primeira celula da imagem e o tamanho (celulas), e a area andavel do motor */
  x0: number; z0: number; larg: number; prof: number; area: { w: number; h: number };
}
export interface VistaPublicada {
  /** o ponto olhado, o pet e a bola desenhados (celulas) */
  foco: Par; pet: Par; bola: Par | null;
  /** a frente da camera no chao (unitario) e meia abertura da vista (rad) */
  frente: Par; meiaAbertura: number;
  /** a comida no chao (celulas e cor 0xRRGGBB, a da cena) */
  comidas: { x: number; z: number; cor: number }[];
  /** os lugares fixos: o ninho, o comedouro e o saco de pancada (celulas) */
  ninho: Par; comedouro: Par; saco: Par;
  /** as arvores de fruta do layout (celulas) */
  arvores: Par[];
  /** o pet esta fora da tela, e de que lado */
  petFora: boolean; lado: Lado;
  /** px de CSS por celula na distancia do ponto olhado (o arrasto direito) e o seno da elevacao da camera */
  pxPorCelula: number; senoElevacao: number;
  mapa: MapaDaIlha;
  limites: Limites;
}
export const VISTA: { atual: VistaPublicada | null; versao: number } = { atual: null, versao: 0 };

/* ---------- o resumo para a HUD: so muda quando um dos campos muda (nao a cada quadro) */
export interface ResumoCamera { ativa: boolean; podeSoltar: boolean; solta: boolean; longe: boolean; petFora: boolean; lado: Lado }
const RESUMO_ZERO: ResumoCamera = { ativa: false, podeSoltar: false, solta: false, longe: false, petFora: false, lado: "direita" };
let resumo = RESUMO_ZERO;
const ouvintes = new Set<() => void>();
function publicarResumo(n: ResumoCamera): void {
  if (n.ativa === resumo.ativa && n.podeSoltar === resumo.podeSoltar && n.solta === resumo.solta && n.longe === resumo.longe
    && n.petFora === resumo.petFora && n.lado === resumo.lado) return;
  resumo = n;
  for (const o of ouvintes) o();
}
export function useCameraLivre(): ResumoCamera {
  return useSyncExternalStore(o => { ouvintes.add(o); return () => { ouvintes.delete(o); }; }, () => resumo, () => RESUMO_ZERO);
}
export const resumoCamera = (): ResumoCamera => resumo;

const dentro = (p: Par, l: Limites): Par => [Math.min(l.x1, Math.max(l.x0, p[0])), Math.min(l.z1, Math.max(l.z0, p[1]))];
const suave = (f: number) => f * f * (3 - 2 * f);
const movimentoReduzido = (): boolean => typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/** solta a camera a partir do ponto olhado de agora (o pet, se ela seguia) */
function soltar(): void {
  const v = VISTA.atual;
  if (!LIVRE.solta) LIVRE.foco = v ? [...v.foco] : LIVRE.foco;
  LIVRE.solta = true; LIVRE.trans = null;
}
/** anda o ponto olhado no plano da vista: `frente` e `lado` em celulas (frente: para onde a camera olha; lado: para a direita) */
export function andar(frente: number, lado: number, f: Par, l: Limites): void {
  soltar();
  /* a direita no chao e a frente girada 90 graus: com a frente para o norte (0, -1), a direita e o leste (1, 0) */
  LIVRE.foco = dentro([LIVRE.foco[0] + f[0] * frente - f[1] * lado, LIVRE.foco[1] + f[1] * frente + f[0] * lado], l);
}
/** leva a camera a um ponto (celulas); `transicao` falso: na hora (o arrasto no minimapa) */
export function irPara(x: number, z: number, agora: number, transicao = true): void {
  const v = VISTA.atual, alvo: Par = v ? dentro([x, z], v.limites) : [x, z];
  const de: Par = v ? [...v.foco] : alvo;
  LIVRE.solta = true;
  if (!transicao || movimentoReduzido()) { LIVRE.foco = alvo; LIVRE.trans = null; return; }
  LIVRE.foco = de; LIVRE.trans = { de, para: alvo, desde: agora };
}
/** volta a camera ao pet e passa a segui-lo (com a transicao, sem ela com "reduzir movimento") */
export function seguirPet(agora = performance.now()): void {
  if (!LIVRE.solta) return;
  if (movimentoReduzido() || !VISTA.atual) { LIVRE.solta = false; LIVRE.trans = null; return; }
  LIVRE.trans = { de: [...VISTA.atual.foco], para: "pet", desde: agora };
}
/** de volta ao comeco (a camera segue o pet), sem transicao: o controle "Fixa", a largura do celular, a cena que desliga */
export function zerarCamera(): void { LIVRE.solta = false; LIVRE.trans = null; teclas.clear(); }

/** o ponto olhado deste quadro; `pet` e o desenhado (celulas), `dtMs` o tempo desde o anterior, `f` a frente da camera no chao.
    `pode`: a camera pode soltar agora (o controle "Livre" e a largura); senao ela segue o pet */
export function focoDoQuadro(pet: Par, agora: number, dtMs: number, f: Par, l: Limites, pode: boolean): Par {
  if (!pode) { if (LIVRE.solta || LIVRE.trans || teclas.size) zerarCamera(); return pet; }
  /* as teclas seguradas: frente e lado, normalizados (a diagonal nao anda mais rapido) */
  let fr = 0, la = 0;
  for (const k of teclas) { const d = DIR_TECLA[k]; if (d) { fr += d[0]; la += d[1]; } }
  if (fr || la) {
    const n = Math.hypot(fr, la), passo = (VEL_CELULAS_S * Math.min(100, dtMs)) / 1000;
    andar((fr / n) * passo, (la / n) * passo, f, l);
  }
  const t = LIVRE.trans;
  if (t) {
    const para = t.para === "pet" ? pet : t.para, k = Math.min(1, (agora - t.desde) / TRANSICAO_MS), s = suave(k);
    LIVRE.foco = [t.de[0] + (para[0] - t.de[0]) * s, t.de[1] + (para[1] - t.de[1]) * s];
    if (k >= 1) { LIVRE.trans = null; if (t.para === "pet") LIVRE.solta = false; }
  }
  return LIVRE.solta ? LIVRE.foco : pet;
}

/** a vista publica o quadro: o minimapa le VISTA.atual, e a HUD recebe o resumo se ele mudou */
export function publicarVista(v: VistaPublicada, ativa: boolean, pode: boolean): void {
  /* a versao so sobe quando algo que o minimapa desenha mudou: parado, o minimapa nao redesenha */
  if (!VISTA.atual || mudouVista(VISTA.atual, v)) VISTA.versao++;
  VISTA.atual = v;
  const longe = LIVRE.solta && Math.hypot(v.foco[0] - v.pet[0], v.foco[1] - v.pet[1]) > SEGUIR_DIST;
  publicarResumo({ ativa, podeSoltar: pode, solta: LIVRE.solta, longe: longe || (LIVRE.solta && v.petFora), petFora: LIVRE.solta && v.petFora, lado: v.lado });
}
const perto = (a: number, b: number) => Math.abs(a - b) < 1e-3;
const mesmoPar = (a: Par | null, b: Par | null) => a === b || (!!a && !!b && perto(a[0], b[0]) && perto(a[1], b[1]));
/** algo que o minimapa desenha mudou entre duas publicacoes (o ponto olhado, o pet, a bola, a vista, a comida, os lugares) */
export function mudouVista(a: VistaPublicada, b: VistaPublicada): boolean {
  if (!mesmoPar(a.foco, b.foco) || !mesmoPar(a.pet, b.pet) || !mesmoPar(a.bola, b.bola) || !mesmoPar(a.frente, b.frente)
    || !perto(a.meiaAbertura, b.meiaAbertura) || a.mapa !== b.mapa || !mesmoPar(a.saco, b.saco) || a.arvores.length !== b.arvores.length
    || a.comidas.length !== b.comidas.length) return true;
  return a.comidas.some((c, i) => { const d = b.comidas[i]; return !perto(c.x, d.x) || !perto(c.z, d.z) || c.cor !== d.cor; });
}
/** a cena desligou: nada publicado */
export function despublicarVista(): void { VISTA.atual = null; VISTA.versao++; zerarCamera(); publicarResumo(RESUMO_ZERO); }

/* ---------- o teclado e o arrasto direito/do meio */
/** a tecla (KeyboardEvent.code) e o passo dela: [frente, lado] */
const DIR_TECLA: Readonly<Record<string, Par>> = {
  KeyW: [1, 0], ArrowUp: [1, 0], KeyS: [-1, 0], ArrowDown: [-1, 0], KeyA: [0, -1], ArrowLeft: [0, -1], KeyD: [0, 1], ArrowRight: [0, 1],
};
const SETAS = new Set(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]);
/** um campo de texto (ou um componente que usa as teclas) com o foco: as teclas ficam com ele */
function teclaDoCampo(alvo: EventTarget | null): boolean {
  if (!(alvo instanceof Element)) return false;
  return !!alvo.closest("input, textarea, select, [contenteditable=''], [contenteditable='true'], [role='slider'], [role='tablist'], [role='tab'], "
    + "[role='listbox'], [role='menu'], [role='menubar'], [role='radiogroup'], [role='combobox'], [role='spinbutton'], [role='searchbox'], "
    + "[role='textbox'], [role='grid'], [role='tree'], dialog, .minimapa");
}
/** as setas so andam com o foco solto (no corpo da pagina ou na cena): num botao ou numa lista elas sao do componente */
function focoSolto(): boolean {
  const a = document.activeElement;
  return !a || a === document.body || !!a.closest(".habitat");
}

/** liga o teclado e o arrasto direito/do meio; `pode` diz se a camera pode soltar agora (o controle "Livre" e a largura).
    Devolve a funcao que desliga */
export function ligarCameraLivre(pode: () => boolean, elevacao0: () => number): () => void {
  const livreAgora = () => pode() && !CENA.coberto;
  const baixo = (e: KeyboardEvent) => {
    /* uma tecla que um componente ja tratou (defaultPrevented) fica com ele */
    if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || !livreAgora() || teclaDoCampo(e.target)) return;
    if (DIR_TECLA[e.code]) {
      if (SETAS.has(e.code) && !focoSolto()) return;
      e.preventDefault(); teclas.add(e.code); return;
    }
    switch (e.code) {
      case "KeyF": if (!e.repeat) { e.preventDefault(); seguirPet(); } return;
      case "KeyQ": e.preventDefault(); girar(-GIRO_TECLA, 0, elevacao0()); return;
      case "KeyE": e.preventDefault(); girar(GIRO_TECLA, 0, elevacao0()); return;
      case "Equal": case "NumpadAdd": e.preventDefault(); aproximar(1 / ZOOM_TECLA); return;
      case "Minus": case "NumpadSubtract": e.preventDefault(); aproximar(ZOOM_TECLA); return;
    }
  };
  const cima = (e: KeyboardEvent) => { teclas.delete(e.code); };
  const largar = () => teclas.clear();
  /* o arrasto: o chao acompanha o cursor (a distancia na tela vira celulas na distancia do ponto olhado) */
  let arrasto: { id: number; x: number; y: number } | null = null;
  const naCena = (e: Event) => e.target instanceof Element && !!e.target.closest(".habitat");
  const pBaixo = (e: PointerEvent) => {
    if (e.pointerType !== "mouse" || (e.button !== 1 && e.button !== 2) || !livreAgora() || !naCena(e)) return;
    e.preventDefault();   /* o botao do meio: sem a rolagem automatica do navegador */
    arrasto = { id: e.pointerId, x: e.clientX, y: e.clientY };
  };
  const pMove = (e: PointerEvent) => {
    const v = VISTA.atual;
    if (!arrasto || e.pointerId !== arrasto.id || !v) return;
    const dx = e.clientX - arrasto.x, dy = e.clientY - arrasto.y;
    arrasto.x = e.clientX; arrasto.y = e.clientY;
    if (!dx && !dy) return;
    const k = Math.max(1e-6, v.pxPorCelula);
    /* arrastar para a direita leva o chao para a direita: a camera vai para a esquerda; para baixo, a camera vai para a frente (o chao
       visto de cima encurta pelo seno da elevacao) */
    andar(dy / k / Math.max(0.2, v.senoElevacao), -dx / k, v.frente, v.limites);
  };
  const pCima = (e: PointerEvent) => { if (arrasto && e.pointerId === arrasto.id) arrasto = null; };
  /* o menu do botao direito sobre a cena atrapalharia o arrasto */
  const menu = (e: MouseEvent) => { if (livreAgora() && naCena(e)) e.preventDefault(); };
  addEventListener("keydown", baixo);
  addEventListener("keyup", cima);
  addEventListener("blur", largar);
  addEventListener("pointerdown", pBaixo);
  addEventListener("pointermove", pMove);
  addEventListener("pointerup", pCima);
  addEventListener("pointercancel", pCima);
  addEventListener("contextmenu", menu);
  return () => {
    removeEventListener("keydown", baixo);
    removeEventListener("keyup", cima);
    removeEventListener("blur", largar);
    removeEventListener("pointerdown", pBaixo);
    removeEventListener("pointermove", pMove);
    removeEventListener("pointerup", pCima);
    removeEventListener("pointercancel", pCima);
    removeEventListener("contextmenu", menu);
    zerarCamera();
  };
}
