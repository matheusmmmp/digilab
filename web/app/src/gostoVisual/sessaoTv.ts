/* A sessão da TV do gosto visual (docs/PLANO_UX_GOSTO_VISUAL.md; UX-GV-1 e UX-GV-7): o estado que antes morava no cartão do canto e agora
   vive fora dos componentes, porque o painel da TV fecha e a TV continua ligada. O painel (PainelTv.tsx), o selo da captura e a janela
   pequena leem daqui; a ilha continua lendo o estadoTv.ts, que esta sessão escreve.
   O carinho é o Carinho do jogo (UX-GV-7): a sessão só LÊ quando foi o último (telas/pet/reacao.ts, só vista) e, se houve um desde o
   segundo anterior, o gosto do protótipo associa o que está passando a ele. A sessão não escreve nada no motor, no log nem no save, salvo
   no pet com a TV no cérebro (a v32): ali o vetor de cada segundo vai ao cerebroTv.ts, que grava o evento "st" (D-GV-CEREBRO-1), e a reação
   sobre o pet passa a ser a do cérebro (D-GV-CEREBRO-9). */
import { useSyncExternalStore } from "react";
import { ultimoCarinhoEm } from "../telas/pet/reacao.ts";
import { capturarTela } from "./captura.ts";
import { desligarTv, publicarTv } from "./estadoTv.ts";
import { chaveGuardada, doTexto, estadoInicial, inatoDaSemente, paraTexto, passo, type EstadoGosto, type Inato, type Leitura, type Sentido } from "./gosto.ts";
import { ligarTvDoJogo } from "./tvDoJogo.ts";
import { comecarNoCerebro, pararNoCerebro, reacaoDoCerebroAgora, sentirNoCerebro } from "./cerebroTv.ts";

export interface SessaoTv {
  /** o pet de agora (a semente dele); null antes de `usarPet` */
  semente: number | null;
  inato: Inato | null;
  estado: EstadoGosto;
  leitura: Leitura | null;
  sentido: Sentido | null;
  /** de onde vem a imagem: a tela do dono ou a TV do jogo; null desligada */
  origem: "tela" | "jogo" | null;
  /** o programa da TV do jogo de agora; null fora dela */
  programa: string | null;
  temSom: boolean;
  /** sobe a cada carinho que o gosto associou (o painel pulsa a origem "do carinho") */
  carinhosVistos: number;
  erro: string | null;
}

const VAZIA: SessaoTv = { semente: null, inato: null, estado: estadoInicial(), leitura: null, sentido: null, origem: null, programa: null, temSom: false,
  carinhosVistos: 0, erro: null };
let atual: SessaoTv = VAZIA, parador: (() => void) | null = null, carinhoVisto: number | null = null;
const ouvintes = new Set<() => void>();
const mudar = (m: Partial<SessaoTv>): void => { atual = { ...atual, ...m }; for (const f of ouvintes) f(); };

export const sessaoTv = (): SessaoTv => atual;
export function useSessaoTv(): SessaoTv {
  return useSyncExternalStore(f => { ouvintes.add(f); return () => { ouvintes.delete(f); }; }, sessaoTv, sessaoTv);
}

/** o pet mudou: o inato vem da semente; o aprendido, do que este navegador guardou para ele. A TV de outro pet desliga */
export function usarPet(semente: number): void {
  if (atual.semente === semente) return;
  pararTv();
  const inato = inatoDaSemente(semente);
  try {
    const t = localStorage.getItem(chaveGuardada(semente));
    mudar({ ...VAZIA, semente, inato, estado: t === null ? estadoInicial() : doTexto(t) });
  } catch (x) { mudar({ ...VAZIA, semente, inato, erro: `o gosto guardado deste pet não abriu: ${(x as Error).message}` }); }
}

/** um segundo sentido: o gosto anda, a ilha recebe a reação e o aprendido é guardado neste navegador */
function sentir(s: Sentido): void {
  const { inato, semente } = atual;
  if (!inato || semente === null) throw new Error("a TV sentiu sem pet (usarPet não foi chamado)");
  const c = ultimoCarinhoEm(), houve = c !== null && c !== carinhoVisto;
  carinhoVisto = c;
  const { estado, leitura } = passo(inato, atual.estado, s, houve);
  sentirNoCerebro(s);                                     // a v32: o vetor vai ao resumo, e o "st" ao registro
  const cer = reacaoDoCerebroAgora();
  publicarTv({ sentido: s, reacao: cer === null ? leitura.reacao : cer.reacao, petVai: cer === null ? true : cer.olhando });
  let erro = atual.erro;
  try { localStorage.setItem(chaveGuardada(semente), paraTexto(estado)); } catch (x) { erro = `o gosto não foi guardado neste navegador: ${(x as Error).message}`; }
  mudar({ estado, leitura, sentido: s, carinhosVistos: atual.carinhosVistos + (houve ? 1 : 0), erro });
}

const comecar = (): void => { carinhoVisto = ultimoCarinhoEm(); };   /* os carinhos de antes de ligar a TV não contam */

/** liga a TV do jogo (os programas sintéticos; nada do computador é lido) */
export function ligarTvJogo(): void {
  if (atual.semente === null) throw new Error("ligar a TV sem pet");
  pararTv(); comecar();
  comecarNoCerebro("jogo");
  const tv = ligarTvDoJogo(atual.semente, (s, nome) => { if (atual.programa !== nome) { mudar({ programa: nome }); publicarTv({ programa: nome }); } sentir(s); });
  parador = tv.parar;
  mudar({ origem: "jogo", programa: null, temSom: true, erro: null });
  publicarTv({ ligada: true, origem: "jogo", programa: null, video: null });
}

function desligar(erro: string | null): void {
  pararNoCerebro();                                       // a v32: a tela preta e muda entra no registro
  desligarTv();
  mudar({ origem: null, programa: null, temSom: false, leitura: null, sentido: null, erro });
}

/** mostra a tela do dono ao pet (precisa vir de um clique; o seletor é o do navegador). Cancelar no seletor não é erro */
export async function ligarTela(): Promise<void> {
  if (atual.semente === null) throw new Error("mostrar a tela sem pet");
  pararTv(); comecar();
  comecarNoCerebro("tela");
  try {
    const c = await capturarTela(sentir, motivo => { parador = null; desligar(motivo); });
    parador = c.parar;
    mudar({ origem: "tela", programa: null, temSom: c.temSom, erro: null });
    publicarTv({ ligada: true, origem: "tela", programa: null, video: c.video ?? null });
  } catch (x) {
    pararNoCerebro();
    const cancelou = x instanceof DOMException && (x.name === "NotAllowedError" || x.name === "AbortError");
    mudar({ erro: cancelou ? null : `a tela não foi compartilhada: ${(x as Error).message}` });
  }
}

/** desliga a TV (o botão Parar, o pet que mudou, a tela que fechou) */
export function pararTv(): void {
  const p = parador;
  parador = null;
  p?.();
  if (atual.origem !== null) desligar(null);
}

/** o navegador deixa mostrar a tela? (o celular e o navegador sem a captura ficam só com a TV do jogo: nenhum botão que falha) */
export const podeMostrarTela = (): boolean =>
  typeof navigator !== "undefined" && typeof navigator.mediaDevices?.getDisplayMedia === "function"
  && !(typeof matchMedia === "function" && matchMedia("(pointer: coarse)").matches);
