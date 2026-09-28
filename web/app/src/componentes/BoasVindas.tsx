/* Boas-vindas (prancha PvBoasVindas): so na primeira visita (chave propria -boas-vindas; o save nao muda). Tela cheia
   listrada, o ovo da especie no anel com brilhos, DIGILAB, o slogan e Comecar. */
import { useEffect, useRef } from "preact/hooks";
import { abrirModal, rotaDaTelaCheia } from "./modal.ts";
import { OVO } from "../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../atlas.ts";
import { useJogo } from "../jogo.ts";
import { Peca } from "./Imagens.tsx";

const ITENS: [string, string, string][] = [["emoji_carne", "Cuide", "ele chama; atender logo conta"], ["emoji_joinha", "Ensine", "elogie ou repreenda o que ele acabou de fazer"],
  ["emoji_feliz", "Veja crescer", "o cuidado e o que ele aprende decidem a forma"]];
const BRILHOS: [number, number, number, number][] = [[30, 60, 8, .8], [200, 40, 6, .6], [212, 130, 10, .7], [18, 150, 6, .5]];

export function BoasVindas({ fechar }: { fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null), a = useAtlas(), { motor: m } = useJogo();
  useEffect(() => { abrirModal(ref.current); }, []);
  useEffect(() => rotaDaTelaCheia("#/inicio"), []);
  const ovo = a.tipo === "ok" ? imagemAtlas(a, OVO[m.especie]) : null;
  return (
    <dialog class="boas-vindas-tela dl" ref={ref} aria-labelledby="bv-tit" onClose={fechar}>
      <div class="bv-centro">
        <div class="bv-palco" aria-hidden="true">
          <span class="bv-luz" /><span class="bv-anel" />
          {ovo && <img class="dl-pix bv-ovo" src={ovo.url} width={ovo.w} height={ovo.h} alt="" />}
          {BRILHOS.map(([x, y, t, o], i) => <span key={i} class="bv-brilho" style={{ left: `${x}px`, top: `${y}px`, width: `${t}px`, height: `${t}px`, opacity: o }} />)}
        </div>
      </div>
      <div class="bv-texto">
        <h1 class="bv-tit" id="bv-tit">DIGILAB</h1>
        <p class="bv-slogan">Um pet que aprende com você.</p>
        {/* desktop (PvDesktop): as tres coisas que o jogo pede, ao lado do ovo */}
        <ul class="bv-itens">
          {ITENS.map(([ic, t, d]) => <li key={t}><Peca nome={ic} escala={2} /><span><b>{t}</b><small>{d}</small></span></li>)}
        </ul>
        <div class="bv-pe">
          <button type="button" class="dl-btn dl-btn--destaque bv-comecar" onClick={() => ref.current?.close()}>Começar</button>
          <span>o progresso fica neste navegador</span>
        </div>
      </div>
    </dialog>
  );
}
