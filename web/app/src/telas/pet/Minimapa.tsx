/* O minimapa da tela Pet (L1 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md, so a partir de 900 px; quem o monta decide a largura):
   um circulo de 176 px com a ilha vista de cima (VISTA.atual.mapa, publicada pela cena 3D), o cone da vista, o pet e os lugares.
   - A roda aproxima da escala A (a ilha inteira) ate a B (a janela em volta do ponto olhado), e o nivel fica nesta pagina (fora do save).
   - Com `podeSoltar`: um clique leva a camera ao ponto (com transicao), segurar e arrastar leva junto (sem transicao), e com o foco as
     setas andam a camera e o Enter volta ao pet. Com a camera "Fixa" o minimapa so mostra (L1-3).
   - Um laco proprio de requestAnimationFrame redesenha o canvas so quando a vista ou o zoom mudou; as caixinhas dos lugares e o pet sao
     elementos posicionados por estilo direto (sem setState por quadro). So vista: nada do motor, do save nem do replay.
   Nao importa nada de ilha/ nem o three (teste ilha_fronteira). */
import { useEffect, useId, useRef, type ReactNode, type RefObject } from "react";
import { Bed, Dumbbell, Lock, Swords, Tent, Utensils, Volleyball } from "lucide-react";
import { VISTA, andar, irPara, seguirPet, useCameraLivre, type Par, type VistaPublicada } from "./cameraLivre.ts";
import { useNivel } from "../../nivelTela.ts";
import { PECAS, PECA_DO_LUGAR, nivelDaPeca, pecaAberta } from "../../nivel.ts";
import {
  LIMIAR_ARRASTO, MINIMAPA_PX, ZOOM_PASSO, celulaParaPx, corComAlfa, corDoNumero, dentroDoCirculo, janelaDe, limitarZoom, passoDaSeta,
  pontasDoCone, pxParaCelula, type Janela,
} from "./minimapaGeo.ts";

/** o nivel de zoom (0 = escala A, 1 = B), so desta pagina */
let zoomNivel = 0;
export const zoomDoMinimapa = (): number => zoomNivel;

/** a ilha vista de cima de cada ImageData vira um canvas pequeno uma vez (drawImage nao le ImageData) */
const bitmaps = new WeakMap<ImageData, HTMLCanvasElement>();
function bitmapDe(img: ImageData): HTMLCanvasElement {
  let c = bitmaps.get(img);
  if (!c) {
    c = document.createElement("canvas"); c.width = img.width; c.height = img.height;
    const x = c.getContext("2d"); if (!x) throw new Error("minimapa: sem canvas 2d");
    x.putImageData(img, 0, 0); bitmaps.set(img, c);
  }
  return c;
}

/** as cores dos tokens da pele de agora (lidas a cada redesenho: a pele pode mudar) */
function lerTokens() {
  const cs = getComputedStyle(document.documentElement), t = (n: string) => cs.getPropertyValue(n).trim();
  return { fundo: t("--hud-fundo-2"), miolo: t("--hx-miolo"), texto2: t("--hx-texto-2"), foco: t("--hx-foco") };
}

interface Estado { chama: boolean; solta: boolean; podeSoltar: boolean }
type Ref = RefObject<HTMLDivElement | null>;
interface Marcas { ninho: Ref; comedouro: Ref; saco: Ref; portao: Ref; barraca: Ref; bola: Ref; pet: Ref }

function desenhar(ctx: CanvasRenderingContext2D, dpr: number, v: VistaPublicada, j: Janela, e: Estado, marcas: Marcas): void {
  const k = lerTokens(), px = (c: Par): Par => celulaParaPx(c, j);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, MINIMAPA_PX, MINIMAPA_PX);
  ctx.fillStyle = k.fundo; ctx.fillRect(0, 0, MINIMAPA_PX, MINIMAPA_PX);
  ctx.imageSmoothingEnabled = false;
  const img = v.mapa.imagem, [dx, dy] = px([v.mapa.x0, v.mapa.z0]);
  ctx.drawImage(bitmapDe(img), dx, dy, img.width * j.ppc, img.height * j.ppc);

  const ponto = (c: Par, preench: string, traco: string) => {
    const p = px(c); if (!dentroDoCirculo(p, -4)) return;
    ctx.beginPath(); ctx.arc(p[0], p[1], 3.5, 0, Math.PI * 2);
    ctx.fillStyle = preench; ctx.fill(); ctx.strokeStyle = traco; ctx.lineWidth = 1; ctx.stroke();
  };
  for (const a of v.arvores) ponto(a, k.miolo, k.texto2);
  for (const c of v.comidas) ponto([c.x, c.z], corDoNumero(c.cor), k.miolo);

  /* o cone: do ponto olhado, abrindo a meia abertura para cada lado da frente, com o --hx-foco em degrade (0,45 -> 0,12) */
  const f = px(v.foco), [pa, pb] = pontasDoCone(v.foco, v.frente, v.meiaAbertura).map(px), meio: Par = [(pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2];
  const g = ctx.createLinearGradient(f[0], f[1], meio[0], meio[1]);
  g.addColorStop(0, corComAlfa(k.foco, 0.45)); g.addColorStop(1, corComAlfa(k.foco, 0.12));
  ctx.beginPath(); ctx.moveTo(f[0], f[1]); ctx.lineTo(pa[0], pa[1]); ctx.lineTo(pb[0], pb[1]); ctx.closePath();
  ctx.fillStyle = g; ctx.fill();
  /* a camera solta: um losango de 8 px no ponto olhado */
  if (e.solta) {
    ctx.beginPath(); ctx.moveTo(f[0], f[1] - 5.6); ctx.lineTo(f[0] + 5.6, f[1]); ctx.lineTo(f[0], f[1] + 5.6); ctx.lineTo(f[0] - 5.6, f[1]); ctx.closePath();
    ctx.strokeStyle = k.foco; ctx.lineWidth = 2; ctx.stroke();
  }

  /* as caixinhas e o pet: elementos por cima do canvas, posicionados direto (sem React) */
  const poe = (el: HTMLElement | null, c: Par | null) => {
    if (!el) return;
    const p = c ? px(c) : null;
    if (!p || !dentroDoCirculo(p, 9)) { el.style.visibility = "hidden"; return; }
    el.style.visibility = "visible"; el.style.transform = `translate(${p[0].toFixed(1)}px, ${p[1].toFixed(1)}px)`;
  };
  poe(marcas.ninho.current, v.ninho); poe(marcas.comedouro.current, v.comedouro); poe(marcas.saco.current, v.saco); poe(marcas.portao.current, v.portao); poe(marcas.barraca.current, v.barraca); poe(marcas.bola.current, v.bola);
  poe(marcas.pet.current, v.pet);
  marcas.pet.current?.classList.toggle("chama", e.chama);
}

/** `soMostra`: so desenha (dentro do lugar, L2: a camera esta no lugar): sem foco, sem rotulo, sem teclado, roda nem ponteiro */
export function Minimapa({ chama = false, soMostra = false }: { chama?: boolean; soMostra?: boolean }) {
  const { ativa, podeSoltar, solta } = useCameraLivre();
  const cv = useRef<HTMLCanvasElement>(null);
  const marcas: Marcas = { ninho: useRef(null), comedouro: useRef(null), saco: useRef(null), portao: useRef(null), barraca: useRef(null), bola: useRef(null), pet: useRef(null) };
  const estado = useRef<Estado>({ chama, solta, podeSoltar });
  estado.current = { chama, solta, podeSoltar };
  const idDesc = useId(), nivel = useNivel();
  /* o lugar trancado (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.4): a marca apagada e tracejada, com o cadeado e o "Nv N" */
  const trancados = (["saco", "portao", "barraca"] as const).filter(l => !pecaAberta(nivel, PECA_DO_LUGAR[l]));
  const marca = (l: "saco" | "portao" | "barraca", icone: ReactNode) => (
    <div ref={marcas[l]} className={"minimapa-marca minimapa-ic" + (trancados.includes(l) ? " minimapa-marca--trancado" : "")} aria-hidden="true">
      {icone}{trancados.includes(l) && <span className="nivel-nv"><Lock />Nv {nivelDaPeca(PECA_DO_LUGAR[l])}</span>}
    </div>
  );

  useEffect(() => {
    const canvas = cv.current;
    if (!ativa || !canvas) return;
    const ctx = canvas.getContext("2d"); if (!ctx) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = canvas.height = Math.round(MINIMAPA_PX * dpr);
    let pedido = 0, versaoVista = -1, zoomVisto = -1, chaveEstado = "";
    /* durante o arrasto a janela fica parada: senao ela seguiria a camera e o cursor fugiria do ponto */
    let congelada: Janela | null = null;
    const janelaAgora = (v: VistaPublicada): Janela => congelada ?? janelaDe(v.mapa.area, v.foco, zoomNivel);
    const forcar = () => { versaoVista = -1; };

    const quadro = () => {
      pedido = requestAnimationFrame(quadro);
      const v = VISTA.atual; if (!v) return;
      const e = estado.current, chave = `${e.chama}|${e.solta}|${e.podeSoltar}`;
      if (VISTA.versao === versaoVista && zoomNivel === zoomVisto && chave === chaveEstado) return;
      versaoVista = VISTA.versao; zoomVisto = zoomNivel; chaveEstado = chave;
      desenhar(ctx, dpr, v, janelaAgora(v), e, marcas);
    };
    pedido = requestAnimationFrame(quadro);

    const celulaDo = (ev: { clientX: number; clientY: number }, v: VistaPublicada): Par => {
      const r = canvas.getBoundingClientRect(), k = MINIMAPA_PX / (r.width || MINIMAPA_PX);
      return pxParaCelula([(ev.clientX - r.left) * k, (ev.clientY - r.top) * k], janelaAgora(v));
    };
    let toque: { id: number; x: number; y: number; arrasto: boolean } | null = null;
    const baixo = (ev: PointerEvent) => {
      const v = VISTA.atual;
      if (ev.button !== 0 || !v || !estado.current.podeSoltar) return;
      canvas.setPointerCapture(ev.pointerId);
      congelada = janelaDe(v.mapa.area, v.foco, zoomNivel);
      toque = { id: ev.pointerId, x: ev.clientX, y: ev.clientY, arrasto: false };
    };
    const mover = (ev: PointerEvent) => {
      const v = VISTA.atual;
      if (!toque || ev.pointerId !== toque.id || !v) return;
      if (!toque.arrasto && Math.hypot(ev.clientX - toque.x, ev.clientY - toque.y) > LIMIAR_ARRASTO) toque.arrasto = true;
      if (toque.arrasto) { const [x, z] = celulaDo(ev, v); irPara(x, z, performance.now(), false); }
    };
    const cima = (ev: PointerEvent) => {
      const v = VISTA.atual;
      if (!toque || ev.pointerId !== toque.id) return;
      if (!toque.arrasto && v) { const [x, z] = celulaDo(ev, v); irPara(x, z, performance.now()); }
      toque = null; congelada = null; forcar();
    };
    const cancelar = (ev: PointerEvent) => { if (toque && ev.pointerId === toque.id) { toque = null; congelada = null; forcar(); } };
    const roda = (ev: WheelEvent) => {
      ev.preventDefault();
      if (toque) return;
      zoomNivel = limitarZoom(zoomNivel + (ev.deltaY < 0 ? ZOOM_PASSO : -ZOOM_PASSO));
    };
    const tecla = (ev: KeyboardEvent) => {
      const v = VISTA.atual;
      if (!v || !estado.current.podeSoltar || ev.ctrlKey || ev.metaKey || ev.altKey) return;
      const passo = passoDaSeta(ev.code);
      if (passo) { ev.preventDefault(); andar(passo[0], passo[1], v.frente, v.limites); return; }
      if (ev.code === "Enter") { ev.preventDefault(); seguirPet(); }
    };
    if (soMostra) return () => cancelAnimationFrame(pedido);
    canvas.addEventListener("pointerdown", baixo);
    canvas.addEventListener("pointermove", mover);
    canvas.addEventListener("pointerup", cima);
    canvas.addEventListener("pointercancel", cancelar);
    canvas.addEventListener("wheel", roda, { passive: false });   /* passivo nao deixa o preventDefault: a pagina rolaria */
    canvas.addEventListener("keydown", tecla);
    return () => {
      cancelAnimationFrame(pedido);
      canvas.removeEventListener("pointerdown", baixo);
      canvas.removeEventListener("pointermove", mover);
      canvas.removeEventListener("pointerup", cima);
      canvas.removeEventListener("pointercancel", cancelar);
      canvas.removeEventListener("wheel", roda);
      canvas.removeEventListener("keydown", tecla);
    };
    // as marcas sao refs estaveis; o laco le o estado pelo ref
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ativa, soMostra]);

  if (!ativa) return null;
  return (
    <div className={"minimapa-caixa" + (podeSoltar ? "" : " fixa")}>
      {/* role="application": o minimapa trata as setas, o Enter e a roda por conta propria, e o leitor de tela precisa deixar essas teclas
          passarem (um "button" prometeria so Enter e Espaco). O nome e a descricao dos atalhos vao em aria-label e aria-describedby */}
      {soMostra
        ? <canvas ref={cv} className="minimapa" role="presentation" tabIndex={-1} style={{ width: MINIMAPA_PX, height: MINIMAPA_PX, cursor: "default" }} />
        : <canvas ref={cv} className="minimapa" role="application" aria-label="Minimapa da ilha" aria-describedby={idDesc}
          aria-keyshortcuts={podeSoltar ? "ArrowUp ArrowDown ArrowLeft ArrowRight Enter" : undefined}
          tabIndex={podeSoltar ? 0 : -1} style={{ width: MINIMAPA_PX, height: MINIMAPA_PX }} />}
      {!soMostra && <span id={idDesc} className="minimapa-desc">Clique ou arraste para levar a câmera. Setas movem a câmera, Enter volta ao pet, a roda aproxima.
        {trancados.map(l => ` ${PECAS[PECA_DO_LUGAR[l]].nome} trancado, Nv ${nivelDaPeca(PECA_DO_LUGAR[l])}: ${PECAS[PECA_DO_LUGAR[l]].motivo}.`).join("")}</span>}
      <span className="minimapa-n" aria-hidden="true">N</span>
      <div ref={marcas.ninho} className="minimapa-marca minimapa-ic" aria-hidden="true"><Bed /></div>
      <div ref={marcas.comedouro} className="minimapa-marca minimapa-ic" aria-hidden="true"><Utensils /></div>
      {marca("saco", <Dumbbell />)}
      {marca("portao", <Swords />)}
      {marca("barraca", <Tent />)}
      <div ref={marcas.bola} className="minimapa-marca minimapa-ic" aria-hidden="true"><Volleyball /></div>
      <div ref={marcas.pet} className="minimapa-marca minimapa-pet" aria-hidden="true" />
    </div>
  );
}
