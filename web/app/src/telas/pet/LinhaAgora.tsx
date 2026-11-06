/* A linha do agora e o chip de causa da tela Pet (docs/PROPOSTAS_V3_UX_TELA_PET.md, "P1"; prancha em docs/pranchas/ux-pet/).
   So le o motor: a acao de agora (Motor.acao, o texto de NOME_PET) e o porque do cerebro A (a leitura da ultima decisao, a mesma do
   painel DigiBrain). Os textos da regra e da acao sao os do painel (REGRA_TXT, ACAO_CURTA); a linha nao inventa frase do pet. A marca
   de "aprendido" so aparece quando o aprendido mudou a escolha (quem_decidiu.mudou); o neutro e silencio. */
import { ChevronRight } from "lucide-react";
import { useMemo, type ReactNode } from "react";
import { FATORES_TXT, NOME_PET, leituraDecisao, type LeituraDecisao, type MotivoVida, type Motor } from "../../../motor/index.ts";
import { ACAO_CURTA, REGRA_TXT } from "../../componentes/DigiBrain.tsx";
import { useJogo } from "../../jogo.ts";

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

/** o caso da linha, pela ordem em que a tela testa: o modular decide; sem decisao; o aprendido mudou a escolha; o instinto bastava; uma opcao so */
export function vistaAgora(m: Motor, d: LeituraDecisao | null = decisaoAgora(m)): VistaAgora {
  const acao = NOME_PET[m.acao];
  if (m.lab !== null) return { caso: "modular", acao, regra: null, semEle: null };
  if (d === null) return { caso: "sem", acao, regra: null, semEle: null };
  const regra = REGRA_TXT[d.regra], q = d.quem_decidiu;
  if (q.escolha && q.mudou) return { caso: "aprendido", acao, regra, semEle: ACAO_CURTA[q.acao_instinto] };
  return { caso: q.escolha ? "instinto" : "uma", acao, regra, semEle: null };
}

/** as frases do painel DigiBrain ("Agora"), na forma curta da linha */
const FRASE: Record<"instinto" | "uma", [string, string]> = { instinto: ["o instinto faria o mesmo", "instinto"], uma: ["só havia uma opção", "uma opção"] };

/** o nome acessivel junta tudo; sem o botao (P1-5) nao ha o convite a abrir */
export function rotuloAgora(v: VistaAgora, comBotao: boolean): string {
  const base = `Agora: ${v.acao}. `;
  const porque = v.caso === "modular" ? "Cérebro modular."
    : v.caso === "sem" ? "Sem motivo registrado."
      : v.caso === "aprendido" ? `Aprendido: sem ele, ${v.semEle}.`
        : `${v.regra}: ${FRASE[v.caso][0]}.`;
  return base + porque + (comBotao ? " Abrir o porquê no DigiBrain." : "");
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
export function LinhaAgoraVista({ v, aoAbrir, aberto = false }: { v: VistaAgora; aoAbrir?: () => void; aberto?: boolean }) {
  const corpo: ReactNode = (
    <>
      <span className="agora-rot" aria-hidden="true">agora</span><span className="agora-acao" aria-hidden="true">{v.acao}</span>
      <span className="agora-ponto" aria-hidden="true">·</span><span className="agora-meio" aria-hidden="true"><Meio v={v} /></span>
    </>
  );
  if (!aoAbrir) return <div className="hud-caixa pet-agora pet-agora--texto" role="group" aria-label={rotuloAgora(v, false)} data-caso={v.caso}>{corpo}</div>;
  return (
    <button type="button" className="hud-caixa pet-agora" aria-label={rotuloAgora(v, true)} aria-pressed={aberto} aria-controls="pet-painel" data-caso={v.caso} onClick={aoAbrir}>
      {corpo}<ChevronRight className="agora-seta" size={18} aria-hidden="true" />
    </button>
  );
}

/** a linha sempre visivel da tela Pet: some com o ovo chocando e com o pet morto. A leitura e refeita so quando o motor muda (a revisao) */
export function LinhaAgora({ aoAbrir, aberto }: { aoAbrir?: () => void; aberto: boolean }) {
  const { motor: m, revisao, nascendo } = useJogo();
  const v = useMemo(() => vistaAgora(m), [m, revisao]);
  if (nascendo > 0 || m.morte) return null;
  return <LinhaAgoraVista v={v} aoAbrir={aoAbrir} aberto={aberto} />;
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
