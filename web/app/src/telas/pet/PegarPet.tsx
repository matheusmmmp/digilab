/* Pegar o pet com o mouse ou o dedo e solta-lo onde quiser (docs/TAREFA_V3_PEGAR_PET.md, P2), no modelo do ArrastoBola (PorBola.tsx):
   Pointer Events na cena do habitat, setPointerCapture, o mesmo caminho para o mouse e o toque.
   - o gesto (PP-5): um pointerdown no sprite do pet (o retangulo CENA.ret, com a folga do dedo do ToquePet) e um arrasto de mais de
     LIMIAR_ARRASTO px. O toque rapido continua sendo o carinho (ToquePet.tsx: ele larga o toque quando o pet esta na mao);
   - quem pode ser pego: so os pets v19 em diante com o mundo, vivos, fora do ovo e acordados (PP-2), sem painel por cima (CENA.coberto)
     nem lugar aberto (viagem.ts, lugarAberto: com o lugar aberto, clicar na ilha nao grava, como a bola e o toque) e sem a bola na mao (CENA.bolaNaMao; a bola tem a vez quando os dois estao sob o dedo);
   - na mao: CENA.petNaMao e CENA.maoPet (o ponto do cliente em que fica o pe do pet) contam a vista (ilha/vista.ts), que segura a camera,
     desenha o pet suspenso, balancando e com a careta, e a sombra onde ele vai cair;
   - ao soltar: o evento "levar pet" (Motor.levarPet, o "lp" do registro) por mudarMotor(), no ponto do chao sob o pe (CENA.mundo.pousoEm);
     fora do mapa, o motor o poe na borda mais proxima (PP-4). Fora do chao (o ceu), vale o ultimo ponto do chao por onde ele passou; sem
     nenhum, nada se grava e o pet volta para onde estava. O pointercancel tambem nao grava.
   So a posicao muda (PP-1): nada aqui mexe no humor, na quimica, no aprendizado, no contato ou no cuidado. A reserva do mundo (sem WebGL)
   nao tem o pousoEm: la o pet nao e pego. */
import { useEffect, type RefObject } from "react";
import { VERSAO_V19, type Motor } from "../../../motor/index.ts";
import { jogoAtual, mudarMotor } from "../../jogo.ts";
import { lugarAberto } from "../../viagem.ts";
import { CENA } from "./cenaEstado.ts";
import { LIMIAR_ARRASTO, avisarNoDock } from "./PorRacao.tsx";
import { noSprite } from "./ToquePet.tsx";

/** o pet pode ser pego agora? (o motor e a cena; o ponteiro sobre o sprite e conferido a parte) */
export function podePegar(m: Motor, nascendo: number, cena: { coberto: boolean; bolaNaMao: boolean; pousoEm: boolean }): boolean {
  return m.versao >= VERSAO_V19 && !!m.mundo && !m.morte && nascendo <= 0 && !m.e.dormindo && !cena.coberto && !cena.bolaNaMao && cena.pousoEm;
}
/** o arrasto (px de CSS) ja pega o pet? (PP-5: mais de LIMIAR_ARRASTO px a partir do pointerdown) */
export const arrastoPega = (dx: number, dy: number): boolean => Math.hypot(dx, dy) > LIMIAR_ARRASTO;

/** o que a cena precisa ter para o gesto (o elemento da cena do habitat; nos testes, um EventTarget com o retangulo) */
export type AlvoPonteiro = EventTarget & { getBoundingClientRect(): { left: number; top: number }; setPointerCapture?(id: number): void };
type Ponteiro = Event & { pointerId: number; clientX: number; clientY: number; button: number; pointerType: string };

/** solta o pet no ponto do chao `p` (subunidades): o "levar pet" do motor; devolve se gravou */
function soltarEm(p: [number, number] | null): boolean {
  if (!p) { avisarNoDock("Solte o pet no chão da cena: ele voltou para onde estava."); return false; }
  try {
    mudarMotor(m => m.levarPet(Math.round(p[0]), Math.round(p[1])));
    return true;
  } catch (err) { avisarNoDock(err instanceof Error ? err.message : String(err)); return false; }
}

/** liga o gesto de pegar o pet num alvo; devolve a funcao que desliga. Ligar DEPOIS do ToquePet no mesmo alvo: no pointermove e no
    pointerup ele confere CENA.petNaMao antes deste laco o mudar */
export function ligarPegarPet(el: AlvoPonteiro): () => void {
  let mao: { id: number; x: number; y: number; dx: number; dy: number } | null = null, pegou = false, pouso: [number, number] | null = null;
  const largar = () => { mao = null; pegou = false; pouso = null; CENA.petNaMao = false; CENA.maoPet = null; };
  const baixo = (ev: Event) => {
    const e = ev as Ponteiro, { motor: m, nascendo } = jogoAtual(), v = CENA.mundo;
    if ((e.pointerType === "mouse" && e.button !== 0) || mao || !v) return;
    if (!podePegar(m, nascendo, { coberto: CENA.coberto || lugarAberto(), bolaNaMao: CENA.bolaNaMao, pousoEm: !!v.pousoEm })) return;
    if (!noSprite(e.clientX, e.clientY, el.getBoundingClientRect(), CENA.ret)) return;
    /* a distancia do pe do pet (onde a vista o desenha) ao ponteiro: na mao, o pe fica a essa distancia do dedo */
    const [fx, fy] = v.paraTela(...v.pet);
    mao = { id: e.pointerId, x: e.clientX, y: e.clientY, dx: fx - e.clientX, dy: fy - e.clientY };
  };
  const move = (ev: Event) => {
    const e = ev as Ponteiro;
    if (!mao || mao.id !== e.pointerId) return;
    if (!pegou) {
      /* a bola tem a vez (o ArrastoBola ja a pegou neste arrasto), e as condicoes podem ter mudado desde o pointerdown */
      const { motor: m, nascendo } = jogoAtual();
      if (CENA.bolaNaMao || !podePegar(m, nascendo, { coberto: CENA.coberto || lugarAberto(), bolaNaMao: false, pousoEm: !!CENA.mundo?.pousoEm })) { largar(); return; }
      if (!arrastoPega(e.clientX - mao.x, e.clientY - mao.y)) return;
      pegou = true;
      el.setPointerCapture?.(e.pointerId);
      CENA.petNaMao = true;
    }
    ev.preventDefault();
    CENA.maoPet = { x: e.clientX + mao.dx, y: e.clientY + mao.dy };
    pouso = CENA.mundo?.pousoEm?.(CENA.maoPet.x, CENA.maoPet.y) ?? pouso;
  };
  const cima = (ev: Event) => {
    const e = ev as Ponteiro;
    if (!mao || mao.id !== e.pointerId) return;
    const segurava = pegou, m0 = mao;
    let p = pouso;
    if (segurava) p = CENA.mundo?.pousoEm?.(e.clientX + m0.dx, e.clientY + m0.dy) ?? p;
    /* grava antes de largar a marca: a vista ve o pet ja no lugar novo no quadro em que ele sai da mao */
    if (segurava) soltarEm(p);
    largar();
  };
  el.addEventListener("pointerdown", baixo); el.addEventListener("pointermove", move);
  el.addEventListener("pointerup", cima); el.addEventListener("pointercancel", largar);
  return () => {
    el.removeEventListener("pointerdown", baixo); el.removeEventListener("pointermove", move);
    el.removeEventListener("pointerup", cima); el.removeEventListener("pointercancel", largar);
    largar();
  };
}

/** pegar o pet na cena do habitat (`alvo`); montar depois do ToquePet */
export function PegarPet({ alvo }: { alvo: RefObject<HTMLElement | null> }) {
  useEffect(() => {
    const el = alvo.current;
    return el ? ligarPegarPet(el) : undefined;
  }, [alvo]);
  return null;
}
