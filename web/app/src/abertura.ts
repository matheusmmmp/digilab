/* A camera do primeiro dia (a regra 6 de "guiar o olhar sem texto"; prancha em docs/pranchas/ux-ilha-abertura/, AB-1 a AB-5 APROVADAS pelo
   Matheus em 2026-11-10: "siga a recomendação."): quando o ovo choca, a ilha se mostra uma vez, com a proposta B.
   - AB-2: uma vez por pet. O registro fica numa chave da pagina (CHAVE-abertura), fora do save, do log e do replay, como o nivel do Tamer:
     o ovo que choca pede a abertura ({semente, tocada: false}); a vista toca e marca tocada quando acaba, quando e interrompida, quando sai da
     tela no meio ou quando o "reduzir movimento" esta ligado (AB-5: nao toca).
   - Recarregar a pagina antes de a abertura tocar nao a perde: o pedido fica gravado ate ela tocar.
   Sem localStorage (aba privada, armazenamento cheio), a abertura nao toca: e uma preferencia de tela, como as dicas. */
import { CHAVE } from "./save.ts";

export const CHAVE_ABERTURA = CHAVE + "-abertura";
/** AB-1: a proposta escolhida, o afastar (uma das de aberturaConta.ts; sem importar a ilha, que so o cena3d.ts carrega: ilha_fronteira.test) */
export const PROPOSTA_ESCOLHIDA = "b" as const;

interface Registro { semente: number; tocada: boolean }
function ler(): Registro | null {
  try {
    const t = localStorage.getItem(CHAVE_ABERTURA);
    if (t === null) return null;
    const r = JSON.parse(t) as Partial<Registro>;
    return typeof r.semente === "number" && typeof r.tocada === "boolean" ? { semente: r.semente, tocada: r.tocada } : null;
  } catch { return null; }
}
function gravar(r: Registro): void {
  try { localStorage.setItem(CHAVE_ABERTURA, JSON.stringify(r)); } catch { /* preferencia de tela */ }
}

/** o ovo do pet `semente` chocou: a abertura fica pedida para a proxima vez que a ilha estiver a vista */
export function pedirAbertura(semente: number): void { gravar({ semente, tocada: false }); }
/** a abertura do pet `semente` esta pedida e ainda nao tocou */
export function aberturaPendente(semente: number): boolean {
  const r = ler();
  return r !== null && r.semente === semente && !r.tocada;
}
/** a abertura do pet `semente` ja tocou (acabou, foi interrompida ou foi pulada) */
export function marcarAberturaTocada(semente: number): void { gravar({ semente, tocada: true }); }
