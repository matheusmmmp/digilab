/* Habitat em tela cheia (docs/TAREFA_V2_LAYOUT_HABITAT.md, M2): a cena da tela Pet (3D, ou a reserva; no v12, a do mundo) e o canvas
   do pet, como camada de fundo da casca. Fica montado em todas as rotas (menos a luta em tela cheia), para o three.js nao subir e
   descer a cada troca de destino. `escurecer`: um painel esta aberto por cima (o veu so escurece; o pet segue visivel). */
import { useEffect } from "react";
import { eNoite, TPD } from "../../motor/index.ts";
import { useJogo } from "../jogo.ts";
import { CenaPet } from "../telas/pet/CenarioPet.tsx";
import { CENA } from "../telas/pet/cenaEstado.ts";
import { PalcoPet } from "../telas/pet/PalcoPet.tsx";
import { Deco } from "./Deco.tsx";

export function Habitat({ escurecer }: { escurecer: boolean }) {
  const { motor: m, nascendo } = useJogo();
  /* a cena sabe que esta coberta pelo veu (a ilha desenha mais devagar por tras dele) */
  useEffect(() => { CENA.coberto = escurecer; return () => { CENA.coberto = false; }; }, [escurecer]);
  return (
    <div className="habitat">
      <section className={"pet-cena habitat-cena" + (m.morte ? " pet-cena--morto" : "")} aria-label="O pet no quarto">
        <CenaPet noite={eNoite(m.e.tick % TPD)} mundo={!!m.mundo} />
        {nascendo > 0 && <Deco nome="Digivice_Circle_01" className="ovo-anel gira" />}
        <PalcoPet />
      </section>
      <div className={"habitat-veu" + (escurecer ? " habitat-veu--ligado" : "")} aria-hidden="true" />
    </div>
  );
}
