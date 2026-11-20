/* A sessão da TV do gosto visual (docs/PLANO_UX_GOSTO_VISUAL.md; UX-GV-1 e UX-GV-7): o estado que antes morava no cartão do canto e agora
   vive fora dos componentes, porque o painel da TV fecha e a TV continua ligada. O painel (PainelTv.tsx), o selo da captura e a janela
   pequena leem daqui; a ilha continua lendo o estadoTv.ts, que esta sessão escreve.
   O carinho é o Carinho do jogo (UX-GV-7): a sessão só LÊ quando foi o último (telas/pet/reacao.ts, só vista) e, se houve um desde o
   segundo anterior, o gosto do protótipo associa o que está passando a ele. A sessão não escreve nada no motor, no log nem no save, salvo
   no pet com a TV no cérebro (a v32): ali o vetor de cada segundo vai ao cerebroTv.ts, que grava o evento "st" (D-GV-CEREBRO-1), e a reação
   sobre o pet passa a ser a do cérebro (D-GV-CEREBRO-9). */
import { useSyncExternalStore } from "react";
import { ultimoCarinhoEm } from "../telas/pet/reacao.ts";
import { abrirTela, abrirVideo } from "./captura.ts";
import { Canais, type CanalAgora, type Fonte } from "./canais.ts";
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
  /** o canal da tela do dono (canais.ts): o número, quantos há e o tipo; null fora da captura */
  canal: CanalAgora | null;
  /** sobe a cada carinho que o gosto associou (o painel pulsa a origem "do carinho") */
  carinhosVistos: number;
  erro: string | null;
}

const VAZIA: SessaoTv = { semente: null, inato: null, estado: estadoInicial(), leitura: null, sentido: null, origem: null, programa: null, temSom: false,
  canal: null, carinhosVistos: 0, erro: null };
let atual: SessaoTv = VAZIA, parador: (() => void) | null = null, carinhoVisto: number | null = null, canais: Canais | null = null;
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
  mudar({ origem: null, programa: null, temSom: false, canal: null, leitura: null, sentido: null, erro });
}

/** abre uma fonte (o seletor do navegador ou o arquivo escolhido); `aoAcabar` recebe o motivo quando ela acaba por fora */
export type AbrirFonte = (aoAcabar: (motivo: string) => void) => Promise<Fonte>;

/** o canal atual mudou (a troca, o canal novo, a fonte encerrada): o painel e a ilha seguem a fonte de agora; a sessão não para */
function canalMudou(): void {
  const c = canais, f = c?.atual ?? null;
  if (c === null || f === null) return;
  mudar({ temSom: f.temSom, canal: c.agora });
  publicarTv({ video: f.video });
}

/** um canal novo da tela do dono (D-GV-CANAL-1): com a TV desligada ou na TV do jogo, liga a captura com ele; com a captura ligada, ele
    entra na lista e vira o atual, sem parar a sessão nem o cérebro. Cancelar no seletor não é erro */
export async function ligarCanal(abrir: AbrirFonte): Promise<void> {
  if (atual.semente === null) throw new Error("mostrar a tela sem pet");
  const jaLigada = atual.origem === "tela" && canais !== null;
  if (!jaLigada) { pararTv(); comecar(); comecarNoCerebro("tela"); }
  let f: Fonte | null = null;
  try {
    f = await abrir(motivo => { const c = canais; if (f !== null && c !== null && c.tem(f)) c.encerrada(f, motivo); });
  } catch (x) {
    if (!jaLigada) pararNoCerebro();
    const cancelou = x instanceof DOMException && (x.name === "NotAllowedError" || x.name === "AbortError");
    mudar({ erro: cancelou ? null : `a tela não foi compartilhada: ${(x as Error).message}` });
    return;
  }
  if (jaLigada) {
    if (canais === null) { f.parar(); return; }          /* a captura acabou enquanto o seletor estava aberto: o canal novo não entra */
    canais.adicionar(f);
    mudar({ erro: null });
    return;
  }
  const c = new Canais(sentir, canalMudou, motivo => { if (canais === c) { canais = null; parador = null; desligar(motivo); } });
  canais = c;
  parador = () => { if (canais === c) canais = null; c.parar(); };
  mudar({ origem: "tela", programa: null, temSom: f.temSom, erro: null });
  publicarTv({ ligada: true, origem: "tela", programa: null, video: f.video });
  c.adicionar(f);
}

/** mostra a tela do dono ao pet (precisa vir de um clique; o seletor é o do navegador): o primeiro canal, ou um canal a mais */
export const ligarTela = (): Promise<void> => ligarCanal(abrirTela);
/** um vídeo deste computador vira um canal (D-GV-CANAL-7); o arquivo não sai da máquina */
export const ligarVideo = (arquivo: File): Promise<void> => ligarCanal(aoAcabar => abrirVideo(arquivo, aoAcabar));

/** o "Canal ▸": o próximo canal já escolhido, sem abrir o seletor; a sessão continua */
export function proximoCanal(): void {
  if (canais === null) throw new Error("mudar de canal sem a tela do dono ligada");
  canais.proximo();
}

/** desliga a TV (o botão Parar, o pet que mudou, a tela que fechou) */
export function pararTv(): void {
  const p = parador;
  parador = null;
  p?.();
  if (atual.origem !== null) desligar(null);
}

/** o navegador abre um vídeo deste computador? (o arquivo e o <video> local; no celular o painel não oferece, D-GV-CANAL-6) */
export const podeAbrirVideo = (): boolean => typeof document !== "undefined" && typeof URL?.createObjectURL === "function";

/** o navegador deixa mostrar a tela? (o celular e o navegador sem a captura ficam só com a TV do jogo: nenhum botão que falha) */
export const podeMostrarTela = (): boolean =>
  typeof navigator !== "undefined" && typeof navigator.mediaDevices?.getDisplayMedia === "function"
  && !(typeof matchMedia === "function" && matchMedia("(pointer: coarse)").matches);
