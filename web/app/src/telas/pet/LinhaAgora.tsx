/* A linha do agora e o chip de causa da tela Pet (docs/PROPOSTAS_V3_UX_TELA_PET.md, "P1"; prancha em docs/pranchas/ux-pet/).
   So le o motor: a acao de agora (Motor.acao, o texto de NOME_PET) e o porque do cerebro A (a leitura da ultima decisao, a mesma do
   painel DigiBrain). Os textos da regra e da acao sao os do painel (REGRA_TXT, ACAO_CURTA); a linha nao inventa frase do pet. A marca
   de "aprendido" so aparece quando o aprendido mudou a escolha (quem_decidiu.mudou); o neutro e silencio. */
import { Angry, ChevronRight, Coffee, Compass, Drumstick, Megaphone, Moon, Music, Tv, type LucideIcon } from "lucide-react";
import { useEffect, useMemo, useRef, type ReactNode } from "react";
import { FATORES_TXT, NOME_PET, leituraDecisao, type AcaoPet, type LeituraDecisao, type MotivoVida, type Motor } from "../../../motor/index.ts";
import { BotaoMovel } from "../../componentes/BotaoMovel.tsx";
import { ACAO_CURTA, REGRA_TXT } from "../../componentes/DigiBrain.tsx";
import { useJogo } from "../../jogo.ts";
import { NOTIFICA_MS, useAviso } from "../../hudPet.ts";
import { CENA } from "./cenaEstado.ts";

export type CasoAgora = "modular" | "sem" | "aprendido" | "instinto" | "uma";
export interface VistaAgora {
  caso: CasoAgora;
  /** a acao de agora ("brincando") */
  acao: string;
  /** o texto da regra do instinto ("Tempo livre"); so nos casos com decisao */
  regra: string | null;
  /** a acao que o instinto sozinho faria ("à toa"); so no caso "aprendido" */
  semEle: string | null;
}

/** a leitura da ultima decisao do cerebro A sem montar o mapa dos pesos (Motor.digibrain() monta o mapa inteiro a cada chamada): as mesmas
    entradas de motor.ts digibrain(), so a decisao. null nos pets sem cerebro A (v1-v10) e antes da primeira decisao. So le */
export function decisaoAgora(m: Motor): LeituraDecisao | null {
  const c = m.cerebro, mo = c === null ? null : c.ultimoMotivo;
  return c === null || mo === null ? null : leituraDecisao(mo, c.prior[mo.regra][mo.acao], c.escala, c.receptoresNovos);
}

/** o nome do que o pet faz agora: o da acao do motor; no pet com a TV no cerebro (a v32), "vendo TV" quando o cerebro escolheu olhar (o motor
    executa o olhar como o ocioso; D-GV-CEREBRO-8: a linha nao diz "a toa" enquanto o DigiBrain diz "olhar") */
export const nomeAcaoAgora = (m: Motor): string => (m.temTv && m.tvNoCerebro()?.olhando ? "vendo TV" : NOME_PET[m.acao]);

/** o caso da linha, pela ordem em que a tela testa: o modular decide; sem decisao; o aprendido mudou a escolha; o instinto bastava; uma opcao so */
export function vistaAgora(m: Motor, decisao?: LeituraDecisao | null): VistaAgora {
  const acao = nomeAcaoAgora(m);
  if (m.lab !== null) return { caso: "modular", acao, regra: null, semEle: null };   /* o modular decide: o A parou, nao se le */
  const d = decisao === undefined ? decisaoAgora(m) : decisao;
  if (d === null) return { caso: "sem", acao, regra: null, semEle: null };
  const regra = REGRA_TXT[d.regra], q = d.quem_decidiu;
  if (q.escolha && q.mudou) return { caso: "aprendido", acao, regra, semEle: ACAO_CURTA[q.acao_instinto] };
  return { caso: q.escolha ? "instinto" : "uma", acao, regra, semEle: null };
}

/** as frases do painel DigiBrain ("Agora"), na forma curta da linha */
const FRASE: Record<"instinto" | "uma", [string, string]> = { instinto: ["o instinto faria o mesmo", "instinto"], uma: ["só havia uma opção", "uma opção"] };

/** o nome acessivel junta tudo; com o botao, o nome nao diz "abrir" (o estado vai em aria-expanded); sem ele (P1-5), e o texto lido da linha */
export function rotuloAgora(v: VistaAgora, comBotao: boolean): string {
  const base = `Agora: ${v.acao}. `;
  const porque = v.caso === "modular" ? "Cérebro modular."
    : v.caso === "sem" ? "Sem motivo registrado."
      : v.caso === "aprendido" ? `Aprendido: sem ele, ${v.semEle}.`
        : `${v.regra}: ${FRASE[v.caso][0]}.`;
  return base + porque + (comBotao ? " Porquê no DigiBrain." : "");
}

function Meio({ v }: { v: VistaAgora }) {
  switch (v.caso) {
    case "modular": return <span className="agora-neutro">cérebro modular</span>;
    case "sem": return <span className="chip-causa chip-causa--sem"><b className="chip-causa__q">?</b>sem motivo registrado</span>;
    case "aprendido": return <span className="chip-causa chip-causa--aprendido dl-malha"><b>aprendido</b><span className="agora-longo"> · sem ele: {v.semEle}</span></span>;
    default: return <span className="agora-neutro"><span className="agora-longo">{v.regra} · {FRASE[v.caso][0]}</span><span className="agora-curto">{FRASE[v.caso][1]}</span></span>;
  }
}

/** a linha ja decidida (para o teste e para a tela). Com `aoAbrir` e um botao que abre o DigiBrain; sem ele (os detalhes do pet desligados), texto */
export function LinhaAgoraVista({ v, aoAbrir, aberto = false, sobPainel = false }: { v: VistaAgora; aoAbrir?: () => void; aberto?: boolean; sobPainel?: boolean }) {
  const corpo: ReactNode = (
    <>
      <span className="agora-rot" aria-hidden="true">agora</span><span className="agora-acao" aria-hidden="true">{v.acao}</span>
      <span className="agora-ponto" aria-hidden="true">·</span><span className="agora-meio" aria-hidden="true"><Meio v={v} /></span>
    </>
  );
  /* sem botao: o visual curto fica escondido e um sr-only diz a linha inteira, para o leitor de tela ler em modo de navegacao */
  if (!aoAbrir) return <div className="hud-caixa pet-agora pet-agora--texto" data-caso={v.caso} data-sob-painel={sobPainel}>{corpo}<span className="sr-only">{rotuloAgora(v, false)}</span></div>;
  return (
    <button type="button" className="hud-caixa pet-agora" aria-label={rotuloAgora(v, true)} aria-expanded={aberto} aria-controls="pet-painel" data-caso={v.caso} data-sob-painel={sobPainel} onClick={aoAbrir}>
      {corpo}<ChevronRight className="agora-seta" size={18} aria-hidden="true" />
    </button>
  );
}

/** a linha do agora da tela Pet: desde 2026-11-08 aparece por NOTIFICA_MS quando a acao muda e depois sai; com o DigiBrain aberto, fica
    (o Matheus: "eles estão ocupando muito, muito espaço"). Some com o ovo chocando e com o pet morto. A leitura e refeita so quando o motor muda (a revisao) */
/** `sobPainel`: um painel da tela Pet esta aberto (a 390 px ele cobre a linha, e o painel vence: a linha se esconde por CSS, sem sair da arvore,
    para o foco voltar a ela ao fechar) */
export function LinhaAgora({ aoAbrir, aberto, sobPainel = false }: { aoAbrir?: () => void; aberto: boolean; sobPainel?: boolean }) {
  const { motor: m, revisao, nascendo } = useJogo();
  const v = useMemo(() => vistaAgora(m), [m, revisao]);
  /* fechar o DigiBrain mostra a linha de novo por NOTIFICA_MS: o foco volta a ela (quem abriu) */
  const vis = useAviso(v.acao + (aberto ? "|aberto" : ""), aberto, NOTIFICA_MS);
  if (nascendo > 0 || m.morte || !vis) return null;
  return <LinhaAgoraVista v={v} aoAbrir={aoAbrir} aberto={aberto} sobPainel={sobPainel} />;
}

/* ------------------------------------------------ o icone do agora (celular, M1 do mobile minimo) */
/** o icone de cada acao do pet (M1-5; PROPOSTO, desenho do ux-designer): a nota e a carne repetem os emotes da cena (cenaAcao.ts). O Record deixa
    o tsc acusar uma acao nova do motor sem icone */
export const ICONE_AGORA: Record<AcaoPet, LucideIcon> = {
  ocioso: Coffee, dormir: Moon, comer: Drumstick, brincar: Music, chamar_atencao: Megaphone, explorar: Compass, emburrar: Angry, ir_tv: Tv,
};
/** a linha do agora abaixo de 900 px: so o icone, sem texto (o nome acessivel e o mesmo da linha). Com `aoAbrir` e um botao que abre o DigiBrain;
    sem ele (os detalhes do pet desligados, M1-11), so desenho. O caso "aprendido" e ciano tracejado; "sem motivo", um "?" no canto */
export function AgoraIconeVista({ v, icone: I, aoAbrir, aberto = false, sobPainel = false }: { v: VistaAgora; icone: LucideIcon; aoAbrir?: () => void; aberto?: boolean; sobPainel?: boolean }) {
  const corpo = <><I aria-hidden="true" />{v.caso === "sem" && <span className="mm-agora-q" aria-hidden="true">?</span>}</>;
  const cls = "mm-caixa mm-forma mm-agora";
  if (!aoAbrir) return <div className={cls + " mm-agora--desenho"} role="img" aria-label={rotuloAgora(v, false)} data-caso={v.caso} data-sob-painel={sobPainel}>{corpo}</div>;
  return (
    <BotaoMovel className={"mm-bt " + cls} rotulo={`Agora: ${v.acao}`} lado="cima" aria-label={rotuloAgora(v, true)} aria-expanded={aberto} aria-controls="pet-painel"
      data-caso={v.caso} data-sob-painel={sobPainel} onClick={aoAbrir}>{corpo}</BotaoMovel>
  );
}
/** o icone sempre visivel da tela Pet no celular: some com o ovo chocando e com o pet morto, como a linha */
export function AgoraIcone({ aoAbrir, aberto, sobPainel = false }: { aoAbrir?: () => void; aberto: boolean; sobPainel?: boolean }) {
  const { motor: m, revisao, nascendo } = useJogo();
  const v = useMemo(() => vistaAgora(m), [m, revisao]), ancora = useRef<HTMLSpanElement>(null);
  /* preso ao pet: o icone fica logo acima da cabeca, no retangulo que a cena publica a cada quadro (CENA.ret, o mesmo do balao e do toque no pet; px de
     CSS desde o canto da caixa do habitat, que no celular e a tela). Nunca sobre o pet: o toque nele e o carinho. Sem retangulo (a cena ainda nao subiu), fica
     no lugar de reserva do CSS */
  useEffect(() => {
    let id = 0, ultimo = "";
    const laco = () => {
      const r = CENA.ret, el = ancora.current;
      if (el && r) {
        const x = Math.round(Math.min(Math.max(r.x + r.w / 2, 32), innerWidth - 32)), y = Math.round(Math.max(r.y, 76)), chave = x + "," + y;
        if (chave !== ultimo) { ultimo = chave; el.style.left = x + "px"; el.style.top = y + "px"; }
      }
      id = requestAnimationFrame(laco);
    };
    id = requestAnimationFrame(laco);
    return () => cancelAnimationFrame(id);
  }, []);
  if (nascendo > 0 || m.morte) return null;
  return <span className="mm-agora-ancora" ref={ancora}><AgoraIconeVista v={v} icone={ICONE_AGORA[m.acao]} aoAbrir={aoAbrir} aberto={aberto} sobPainel={sobPainel} /></span>;
}

/* ------------------------------------------------ o chip de causa do balao */
/** o chip do balao, so com um MotivoVida: o fator `fadiga_treino` e o pedido do corpo (caixa solida de necessidade); outro fator, o marcador
    neutro; sem fator ou exploracao, o vazio honesto ("? sem motivo registrado"). Os fatores de memoria (elogio, carinho, demora, bronca),
    que os pets v13+ nao produzem, ficam no desenho de hoje (Causa, em TelaPet.tsx) */
export function ChipCausa({ mot }: { mot: MotivoVida }) {
  if (mot.exploracao || !mot.fatores.length) return <span className="chip-causa chip-causa--sem"><b className="chip-causa__q" aria-hidden="true">?</b>sem motivo registrado</span>;
  if (mot.fatores.includes("fadiga_treino")) return <span className="chip-causa chip-causa--corpo"><b>vem do corpo</b> · {FATORES_TXT.fadiga_treino.marcador}</span>;
  return <span className="chip-causa chip-causa--neutro">{mot.fatores.map(f => FATORES_TXT[f]?.marcador ?? f).join(" + ")}</span>;
}
