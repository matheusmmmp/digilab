/* Os cadeados na ilha (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.4, P-11; prancha docs/pranchas/ux-lugares-menus/lugar_trancado_*): o saco (Nv 3), o portao (Nv 4) e a
   barraca (Nv 2) aparecem na ilha desde o Nv 1, apagados pela vista 3D (ilha/vista.ts, `estadoDoLugar`), e este desenho poe sobre cada um o cadeado com o
   "Nv N". Tocar nele abre o cartao do motivo (como a tecla e a rota). O cadeado provisorio e DOM simples, com os tokens, sem modelo 3D (o modelo vem depois do
   ITENS_3D, `cadeado` em lugares.ts). Desde 2026-11-08 o cadeado fechado so aparece, translucido, com o mouse sobre o lugar ou sobre ele (nivel.css; o toque
   no lugar trancado continua abrindo o motivo, ToqueLugar.tsx).
   - o "acabou de abrir": o lugar que o nivel acabou de destrancar mostra o cadeado aberto e brilha UMA vez (--hx-alerta); com "reduzir movimento" o brilho
     some (nivel.css) e fica so o cadeado aberto. Os ABRE_MS contam a partir da primeira vez que o lugar entra no quadro, nao da montagem: na planta A a
     barraca comeca fora da tela, e o brilho corria sem ninguem ver (Matheus, 2026-11-10, "Sim, esperar"; D-E2E-2);
   - a posicao de cada lugar na tela vem da vista (CENA.aoLugares: ela chama o retorno no fim do quadro, so com cadeado ou brilho na tela), e o estilo e
     escrito direto (sem setState, sem rAF proprio, sem ler o layout); sem a cena 3D (a sala) nao ha o que mostrar. So vista. */
import { useEffect, useRef, useState } from "react";
import { Lock, LockOpen } from "lucide-react";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { brilhosPendentes, consumirBrilho, useNivel, useVersaoBrilhos } from "../nivelTela.ts";
import { PECAS, PECA_DO_LUGAR, nivelDaPeca, pecaAberta } from "../nivel.ts";
import type { Lugar } from "../viagem.ts";
import { useObjetoSobre } from "./ObjetosDaIlha.tsx";
import "../estilo/nivel.css";

const LUGARES: readonly Lugar[] = ["saco", "portao", "barraca"];
/** quanto tempo o cadeado aberto e o brilho ficam na ilha (ms). PROPOSTO, SEM FONTE (numero de interface, nao de jogo) */
export const ABRE_MS = 2400;
/** quanto tempo o lugar fica no quadro, sem sair, para contar como visto e o tempo do brilho comecar (ms): o primeiro quadro, antes de a camera
    assentar, passa por cima dos lugares. PROPOSTO, SEM FONTE (numero de interface) */
export const VISTO_MS = 500;
/** onde o cadeado fica na altura do lugar (fracao da altura, a partir do pe). PROPOSTO, SEM FONTE (numero de interface) */
const ALTURA_CADEADO = 0.6;

export function CadeadosDaIlha({ abrir }: { abrir: (l: Lugar) => void }) {
  const sobre = useObjetoSobre(), nivel = useNivel(), versaoBrilhos = useVersaoBrilhos(), [abrindo, setAbrindo] = useState<readonly Lugar[]>([]);
  const caixas = useRef<Partial<Record<Lugar, HTMLElement | null>>>({}), brilhos = useRef<Partial<Record<Lugar, HTMLElement | null>>>({}), timers = useRef<number[]>([]);
  /* os que estao abrindo (lido pelo retorno da vista, que nao refaz a cada render) e os que ja entraram no quadro, com o tempo correndo */
  const abrindoRef = useRef<readonly Lugar[]>([]), vistos = useRef(new Set<Lugar>()), desde = useRef(new Map<Lugar, number>());
  abrindoRef.current = abrindo;
  /* os lugares que o nivel acabou de abrir: cadeado aberto e brilho; o tempo (ABRE_MS) so comeca quando o lugar entra no quadro (o retorno da vista, abaixo) */
  useEffect(() => {
    const novos = brilhosPendentes().slice();
    if (!novos.length) return;
    for (const l of novos) consumirBrilho(l);
    for (const l of novos) vistos.current.delete(l);
    setAbrindo(a => [...new Set([...a, ...novos])]);
  }, [nivel, versaoBrilhos]);
  useEffect(() => () => { for (const t of timers.current) clearTimeout(t); }, []);
  /* a posicao de cada um: a vista chama este retorno no fim de cada quadro, so enquanto ha cadeado ou brilho (senao nem calcula); aqui so se ESCREVE o estilo, sem ler
     o layout (o centro vem do CSS, translate(-50%, -50%)) */
  const algo = LUGARES.some(l => !pecaAberta(nivel, PECA_DO_LUGAR[l])) || abrindo.length > 0;
  useEffect(() => {
    if (!algo) return;
    const ultimo = new WeakMap<HTMLElement, string>();
    CENA.aoLugares = p => {
      for (const l of LUGARES) {
        const [x, y, h] = p[l], cy = y - h * ALTURA_CADEADO, dentro = x > 0 && x < innerWidth && cy > 0 && cy < innerHeight;
        if (abrindoRef.current.includes(l) && !vistos.current.has(l)) {
          const agora = performance.now(), t0 = desde.current.get(l);
          if (!dentro) desde.current.delete(l);
          else if (t0 === undefined) desde.current.set(l, agora);
          else if (agora - t0 >= VISTO_MS) {
            vistos.current.add(l); desde.current.delete(l);
            timers.current.push(window.setTimeout(() => setAbrindo(a => a.filter(x => x !== l)), ABRE_MS));
          }
        }
        for (const el of [caixas.current[l], brilhos.current[l]]) {
          if (!el) continue;
          const t = dentro ? `translate(${Math.round(x)}px, ${Math.round(cy)}px) translate(-50%, -50%)` : "hidden";
          if (ultimo.get(el) === t) continue;
          ultimo.set(el, t);
          el.style.visibility = dentro ? "visible" : "hidden";
          if (dentro) el.style.transform = t;
        }
      }
    };
    return () => { CENA.aoLugares = null; };
  }, [algo]);
  return (
    <div className="cadeados-ilha">
      {LUGARES.map(l => {
        const peca = PECA_DO_LUGAR[l], d = PECAS[peca], n = nivelDaPeca(peca), aberta = pecaAberta(nivel, peca);
        if (!aberta) {
          return (
            <button type="button" key={l} className="cadeado-ilha" ref={el => { caixas.current[l] = el; }} style={{ visibility: "hidden" }} data-lugar={l}
              data-sobre={sobre === l ? "" : undefined} aria-label={`${d.nome}, trancado, Nv ${n}: ${d.motivo}`} onClick={() => abrir(l)}>
              <Lock aria-hidden="true" /><b aria-hidden="true">Nv {n}</b>
            </button>
          );
        }
        return abrindo.includes(l) ? (
          <span key={l}>
            <span className="brilho-ilha" ref={el => { brilhos.current[l] = el; }} style={{ visibility: "hidden" }} data-lugar={l} aria-hidden="true" />
            <span className="cadeado-ilha aberto" ref={el => { caixas.current[l] = el; }} style={{ visibility: "hidden" }} data-lugar={l} role="img" aria-label={`${d.nome}: aberto`}>
              <LockOpen aria-hidden="true" />
            </span>
          </span>
        ) : null;
      })}
    </div>
  );
}
