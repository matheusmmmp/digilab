/* O cadeado do cais na ilha (MMO5; a prancha docs/pranchas/ux-cais/, trancado e destravado): o mesmo desenho dos outros lugares
   (CadeadosDaIlha.tsx, nivel.css). Trancado, o cadeado com o "Nv N" aparece translucido com o mouse sobre ele ou no foco, e tocar nele
   abre o cartao do motivo; quando o nivel abre o cais, o cadeado aberto e o brilho aparecem UMA vez. So existe com o cais ligado (o
   servidor no build): desligado, nao monta nada.
   A posicao vem da vista (CENA.aoCais, no fim de cada quadro, so com cadeado ou brilho na tela); aqui so se escreve o estilo. O tempo do
   brilho (ABRE_MS) so comeca quando o cais entra no quadro, como nos outros lugares. So vista. */
import { useEffect, useRef, useState } from "react";
import { Lock, LockOpen } from "lucide-react";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { caisAcabouDeAbrir, consumirBrilhoDoCais, motivoDoCais, useCais, useVersaoBrilhos } from "../nivelTela.ts";
import { ABRE_MS, VISTO_MS } from "./CadeadosDaIlha.tsx";
import "../estilo/nivel.css";

/** onde o cadeado fica na altura do cais (fracao da altura, a partir do pe). PROPOSTO, SEM FONTE (numero de interface) */
const ALTURA_CADEADO = 0.6;

export function CadeadoDoCais({ abrir }: { abrir: () => void }) {
  const cais = useCais(), versao = useVersaoBrilhos(), [abrindo, setAbrindo] = useState(false);
  const caixa = useRef<HTMLElement | null>(null), brilho = useRef<HTMLElement | null>(null), timer = useRef<number | null>(null);
  const abrindoRef = useRef(false), visto = useRef(false), desde = useRef<number | null>(null);
  abrindoRef.current = abrindo;
  useEffect(() => {
    if (!caisAcabouDeAbrir()) return;
    consumirBrilhoDoCais(); visto.current = false; desde.current = null;
    setAbrindo(true);
  }, [cais?.trancado, versao]);
  useEffect(() => () => { if (timer.current !== null) clearTimeout(timer.current); }, []);
  const algo = cais !== null && (cais.trancado || abrindo);
  useEffect(() => {
    if (!algo) return;
    const ultimo = new WeakMap<HTMLElement, string>();
    CENA.aoCais = ([x, y, h]) => {
      const cy = y - h * ALTURA_CADEADO, dentro = x > 0 && x < innerWidth && cy > 0 && cy < innerHeight;
      if (abrindoRef.current && !visto.current) {
        const agora = performance.now();
        if (!dentro) desde.current = null;
        else if (desde.current === null) desde.current = agora;
        else if (agora - desde.current >= VISTO_MS) {
          visto.current = true; desde.current = null;
          timer.current = window.setTimeout(() => setAbrindo(false), ABRE_MS);
        }
      }
      for (const el of [caixa.current, brilho.current]) {
        if (!el) continue;
        const t = dentro ? `translate(${Math.round(x)}px, ${Math.round(cy)}px) translate(-50%, -50%)` : "hidden";
        if (ultimo.get(el) === t) continue;
        ultimo.set(el, t);
        el.style.visibility = dentro ? "visible" : "hidden";
        if (dentro) el.style.transform = t;
      }
    };
    return () => { CENA.aoCais = null; };
  }, [algo]);
  if (!cais) return null;
  return (
    <div className="cadeados-ilha">
      {cais.trancado ? (
        <button type="button" className="cadeado-ilha" ref={el => { caixa.current = el; }} style={{ visibility: "hidden" }} data-lugar="cais"
          aria-label={`Cais, trancado, Nv ${cais.marco}: ${motivoDoCais(cais.marco)}`} onClick={abrir}>
          <Lock aria-hidden="true" /><b aria-hidden="true">Nv {cais.marco}</b>
        </button>
      ) : abrindo ? (
        <span>
          <span className="brilho-ilha" ref={el => { brilho.current = el; }} style={{ visibility: "hidden" }} data-lugar="cais" aria-hidden="true" />
          <span className="cadeado-ilha aberto" ref={el => { caixa.current = el; }} style={{ visibility: "hidden" }} data-lugar="cais" role="img" aria-label="Cais: aberto">
            <LockOpen aria-hidden="true" />
          </span>
        </span>
      ) : null}
    </div>
  );
}
