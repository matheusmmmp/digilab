/* A cooperacao na tela, sem numero (docs/TAREFA_V3_COOPERACAO.md, etapa CO5; D-MM-8): o que a medida da CO3 (motor/cooperacao.ts) viu os dois
   pets fazerem um com o outro aparece como gesto, nunca como pontuacao.
   - na ilha, um icone rapido sobre o pet que fez o ato ("Icone e linha", Matheus, 2026-11-11; D-CO5-1): o coracao quando ele deixou a comida
     para o irmao ou encostou nele emburrado; a comida riscada quando pegou a comida do irmao com fome. A disputa neutra (o irmao sem fome) fica
     so na linha;
   - em Ultimas acoes, a linha do ato, do ponto de vista do pet em foco ("ele deixou a comida para o irmao", "o irmao encostou nele"), sem o
     nome (os irmaos podem ser da mesma forma);
   - depois da luta do pet em foco, o gesto do irmao que assistiu: consola, comemora ou provoca, pelo resultado e pela reputacao do lutador
     vista pelo irmao ("Resultado e reputacao", Matheus, 2026-11-11; D-CO5-2; motor/grupo_jogo.ts, gestoDepoisDaLuta).
   Nada aqui muda o pet: so le o grupo. */
import { useEffect, useRef, useState } from "react";
import { Frown, Heart, PartyPopper, UtensilsCrossed, type LucideIcon } from "lucide-react";
import type { AtoRegistrado, GestoDoIrmao } from "../../../motor/index.ts";
import { jogoAtual, useJogo } from "../../jogo.ts";
import { CENA } from "./cenaEstado.ts";

/** o icone do ato na ilha, ou null (a disputa neutra so vai a linha) */
export function iconeDoAto(a: Pick<AtoRegistrado, "ato" | "sinal">): "coracao" | "comida_riscada" | null {
  if (a.ato === "contencao" || a.ato === "encostar") return "coracao";
  if (a.ato === "disputa" && a.sinal < 0) return "comida_riscada";
  return null;
}

/** o texto do ato do ponto de vista do pet em foco; null para os atos que nao sao dele nem com ele */
export function textoDoAto(a: Pick<AtoRegistrado, "ato" | "sinal" | "autor" | "alvo">, foco: string): string | null {
  const ele = a.autor === foco, comEle = a.alvo === foco;
  if (!ele && !comEle) return null;
  if (a.ato === "contencao") return ele ? "deixou a comida para o irmão" : "o irmão deixou a comida para ele";
  if (a.ato === "encostar") return ele ? "encostou no irmão, que estava emburrado" : "o irmão encostou nele quando estava emburrado";
  if (a.ato === "disputa") {
    if (a.sinal < 0) return ele ? "pegou a comida do irmão, que estava com fome" : "o irmão pegou a comida dele, quando estava com fome";
    return ele ? "pegou a comida que o irmão queria" : "o irmão pegou a comida que ele queria";
  }
  throw new Error(`ato desconhecido: ${a.ato}`);
}

/** as linhas dos atos do pet em foco para Ultimas acoes: o tick, o texto e se e pro-social (o icone) */
export function linhasDosAtos(n: number): { t: number; texto: string; pro: boolean }[] {
  const j = jogoAtual(), c = j.grupo && !j.emLab ? j.grupo.grupo.coop : null;
  if (c === null) return [];
  const out: { t: number; texto: string; pro: boolean }[] = [];
  for (let i = c.atos.length - 1; i >= 0 && out.length < n; i--) {
    const a = c.atos[i], texto = textoDoAto(a, j.foco);
    if (texto !== null) out.push({ t: a.tick, texto, pro: a.sinal > 0 });
  }
  return out;
}

const ICONE: Record<"coracao" | "comida_riscada", LucideIcon> = { coracao: Heart, comida_riscada: UtensilsCrossed };
/** quanto tempo o icone do ato fica sobre o pet (ms; numero de interface). PROPOSTO, SEM FONTE */
export const ATO_NA_ILHA_MS = 2500;

/** os icones dos atos na ilha, ao lado da cabeca do pet que fez cada um, no retangulo que a cena publica a cada quadro (CENA.ret e CENA.irmaos) */
export function AtosNaIlha() {
  const { revisao, grupo, foco, emLab } = useJogo();
  const [vivos, setVivos] = useState<{ id: number; autor: string; icone: "coracao" | "comida_riscada"; ate: number }[]>([]);
  const vistos = useRef<number | null>(null), proximo = useRef(0), refs = useRef(new Map<number, HTMLSpanElement>());
  const coop = grupo && !emLab ? grupo.grupo.coop : null;
  /* os atos novos desde a ultima olhada (os de antes de abrir a tela nao aparecem) */
  useEffect(() => {
    if (coop === null) { vistos.current = null; return; }
    const n = coop.atos.length;
    if (vistos.current === null || vistos.current > n) { vistos.current = n; return; }
    const novos = coop.atos.slice(vistos.current).map(a => ({ a, icone: iconeDoAto(a) })).filter(x => x.icone !== null);
    vistos.current = n;
    if (!novos.length) return;
    const agora = performance.now();
    setVivos(v => [...v.filter(x => x.ate > agora), ...novos.map(x => ({ id: proximo.current++, autor: x.a.autor, icone: x.icone!, ate: agora + ATO_NA_ILHA_MS }))]);
  }, [revisao, coop]);
  /* presos ao pet que fez o ato, como o icone do agora (LinhaAgora.tsx); somem no fim do tempo */
  useEffect(() => {
    if (!vivos.length) return;
    let id = 0;
    const laco = () => {
      const agora = performance.now();
      for (const v of vivos) {
        const el = refs.current.get(v.id), r = v.autor === foco ? CENA.ret : CENA.irmaos[v.autor];
        /* ao lado da cabeca, a direita: acima dela fica o icone do agora (LinhaAgora.tsx), e sobre o pet o toque e o carinho */
        if (el && r) { el.style.left = Math.round(r.x + r.w * 0.9) + "px"; el.style.top = Math.round(Math.max(r.y + r.h * 0.2, 76)) + "px"; el.style.visibility = "visible"; }
        else if (el) el.style.visibility = "hidden";
      }
      if (vivos.some(v => v.ate <= agora)) { setVivos(x => x.filter(v => v.ate > agora)); return; }
      id = requestAnimationFrame(laco);
    };
    id = requestAnimationFrame(laco);
    return () => cancelAnimationFrame(id);
  }, [vivos, foco]);
  if (!vivos.length) return null;
  return <>{vivos.map(v => {
    const I = ICONE[v.icone];
    return <span key={v.id} className="ato-ilha" data-ato={v.icone} role="img" aria-label={v.icone === "coracao" ? "um gesto com o irmão" : "pegou a comida do irmão"}
      ref={el => { if (el) refs.current.set(v.id, el); else refs.current.delete(v.id); }} style={{ visibility: "hidden" }}><I aria-hidden="true" /></span>;
  })}</>;
}

const GESTO: Record<GestoDoIrmao, { icone: LucideIcon; texto: (venceu: boolean | null) => string }> = {
  consola: { icone: Heart, texto: v => v === null ? "O irmão, que assistia, consolou ele pelo empate." : "O irmão, que assistia, consolou ele." },
  comemora: { icone: PartyPopper, texto: () => "O irmão, que assistia, comemorou com ele." },
  provoca: { icone: Frown, texto: v => v === true ? "O irmão, que assistia, provocou ele mesmo assim." : "O irmão, que assistia, provocou ele." },
};
/** o gesto do irmao no fim da luta do pet em foco (so com os dois pets e fora do replay) */
export function GestoDoIrmaoNaLuta({ venceu }: { venceu: boolean | null }) {
  const { grupo, foco, emLab } = useJogo();
  if (!grupo || emLab || grupo.grupo.coop === null) return null;
  const { gesto } = grupo.gestoDoIrmao(foco, venceu), g = GESTO[gesto], I = g.icone;
  return <p className="gesto-irmao" data-gesto={gesto}><I aria-hidden="true" />{g.texto(venceu)}</p>;
}
