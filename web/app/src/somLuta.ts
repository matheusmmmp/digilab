/* O som da luta da POC (SOM-UP, docs/TAREFA_V3_SOM_UP.md): os golpes e os acertos do mapa de sons por Digimon (o mesmo da UP-SOM, que a
   LP4 deixou sem chamador quando o combate por turnos saiu). Sai dos eventos de cada passo, como os efeitos do palco (visualPoc.ts): a mesma
   luta toca os mesmos sons, e o pular (Desistir, Sair do replay) nao passa por aqui. So apresentacao.
   - o projetil que nasce: o golpe de quem atirou (o conjunto de ataque);
   - a habilidade: o golpe de quem usou (o conjunto de habilidade);
   - o dano: o acerto e o fim de quem bateu (habilidade ou ataque, pelo dano). */
import type { EventoPoc, LutaPoc } from "../motor/index.ts";
import { emitirGolpe } from "./somEventos.ts";

const vistos = new WeakMap<LutaPoc, WeakSet<object>>();

/** os sons de um passo da luta (ja aplicado: os projeteis sao os do fim do passo); spriteA e spriteB, as chaves do mapa de sons */
export function somDoPassoPoc(L: LutaPoc, ev: readonly EventoPoc[], spriteA: string, spriteB: string): void {
  const sprite = (l: "a" | "b"): string => (l === "a" ? spriteA : spriteB);
  let v = vistos.get(L); if (!v) { v = new WeakSet(); vistos.set(L, v); }
  for (const pr of L.projeteis) if (!v.has(pr)) { v.add(pr); emitirGolpe("golpe", sprite(pr.de.lado), false); }
  for (const e of ev) {
    if (e.tipo === "habilidade") emitirGolpe("golpe", sprite(e.u.lado), true);
    else if (e.tipo === "dano") { emitirGolpe("acerto", sprite(e.at.lado), e.hab); emitirGolpe("fim", sprite(e.at.lado), e.hab); }
  }
}
