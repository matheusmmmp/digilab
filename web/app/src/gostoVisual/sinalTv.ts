/* O sinal da TV sobre o pet (docs/PLANO_UX_GOSTO_VISUAL.md, seção 5 e a UX-GV-10; a etapa 2 do código): no 3D sai o balão de texto e entra um
   ícone, no mesmo desenho e no mesmo lugar dos emotes do jogo (grades.ts; o PalcoPet o pinta por último, depois dos emotes do jogo).
   - um sinal por vez (a fila da seção 5.2): o chamado do pet, a fala do jogo e o emote do jogo passam na frente; enquanto um deles está na
     tela, o sinal da TV espera (a pose no cantinho continua);
   - o sinal só muda quando a reação muda, e fica pelo menos `SINAL_MIN_MS` (o P0 trocava a cada segundo sentido).
   Só vista, e só com `?gosto_visual=1`. Sem DOM, para o teste ler no node. Fora do motor, do log e do save. */
import { TV } from "./estadoTv.ts";
import type { Reacao } from "./gosto.ts";

/** o tempo mínimo de um sinal na tela (ms). PROPOSTO, SEM FONTE */
export const SINAL_MIN_MS = 3000;

/** o ícone de cada reação (a chave de grades.ts); null = sem sinal, só a pose (seção 5.1) */
export const SINAL_DA_REACAO: Readonly<Record<Reacao, string | null>> = {
  adorando: "coracao", olhando: null, curioso: "pergunta", enjoou: "reticencias", nao_gosta: "x", distraido: null,
};

/** a reação mostrada: segue a que chega, mas só troca depois de `minMs` da última troca; sem reação (a TV desligou), esquece na hora */
export class FilaSinal {
  private atual: { reacao: Reacao; desde: number } | null = null;
  private readonly minMs: number;
  constructor(minMs: number = SINAL_MIN_MS) {
    if (!(minMs >= 0) || !Number.isFinite(minMs)) throw new Error("FilaSinal: minMs inválido");
    this.minMs = minMs;
  }
  passo(reacao: Reacao | null, agora: number): Reacao | null {
    if (!Number.isFinite(agora)) throw new Error("FilaSinal: agora não finito");
    if (reacao === null) { this.atual = null; return null; }
    if (!this.atual || (reacao !== this.atual.reacao && agora - this.atual.desde >= this.minMs)) this.atual = { reacao, desde: agora };
    return this.atual.reacao;
  }
}

/** o que a cena e a tela Pet dizem ao sinal: o pet está sentado no cantinho (a ilha marca a cada quadro), e quem está na frente na fila */
const CENA_TV = { sentado: false, chamado: false, fala: false };
const fila = new FilaSinal();

/** a ilha marca a cada quadro se o pet está sentado na almofada (ilha/cantinhoTv.ts) */
export const marcarSentadoNaTv = (v: boolean): void => { CENA_TV.sentado = v; };
/** a tela Pet diz se o chamado do pet ou a fala do jogo está na tela agora: com um deles, o sinal da TV espera */
export const ocuparSinalTv = (quem: "chamado" | "fala", v: boolean): void => { CENA_TV[quem] = v; };

/** a reação que o sinal mostra agora (com o mínimo de tempo), ou null: a TV desligada ou o pet fora da almofada */
export function reacaoDoSinal(agora: number): Reacao | null {
  return fila.passo(TV.ligada && CENA_TV.sentado ? TV.reacao : null, agora);
}

/** o ícone do sinal da TV agora (a chave de grades.ts), ou null: sem TV, sem sinal para a reação, ou com o chamado ou a fala na frente */
export function sinalDaTvAgora(agora: number): string | null {
  const r = reacaoDoSinal(agora);
  return r === null || CENA_TV.chamado || CENA_TV.fala ? null : SINAL_DA_REACAO[r];
}

/** só para os testes */
export function esquecerSinalTv(): void { CENA_TV.sentado = CENA_TV.chamado = CENA_TV.fala = false; fila.passo(null, 0); }
