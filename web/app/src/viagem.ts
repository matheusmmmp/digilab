/* A viagem da camera ate o lugar (L2 de "Lugares da ilha", docs/PROPOSTAS_V3_UX_TELA_PET.md, secao "Lugares da ilha: menus (L2/L3)"):
   abrir Crescer leva a camera da ilha ate o saco de pancada e o pet anda ate la; ao sair, os dois voltam. So vista: o pet do motor nao
   se move, e nada disto entra no registro, no save nem no replay (o estado fica so nesta pagina, como a ORBITA e a camera solta).
   - o progresso vai de 0 (a ilha de sempre) a 1 (no lugar) a razao de 1/VIAGEM_MS por milissegundo; a vista (ilha/vista.ts) le o progresso
     a cada quadro (progressoViagem) e mistura a camera e o pet por ele;
   - sem animacao (corte seco): com "reduzir movimento" do sistema, com a opcao "Viagem da camera" desligada em Ajustes ou com ?viagem=0 no
     endereco (conferencia e testes, nao grava); clicar ou Esc durante a viagem pula para o fim (pularViagem).
   Os numeros sao PROPOSTO, SEM FONTE (numero de interface, nao de jogo), aprovados como proposta pelo Matheus em 2026-11-06. */
import { useSyncExternalStore } from "react";
import { CHAVE } from "./save.ts";

/** a viagem da camera (ms). PROPOSTO, SEM FONTE (numero de interface, nao de jogo) */
export const VIAGEM_MS = 700;
/** o painel do lugar entrando (ms): o "card entrando" do guia, secao 11. PROPOSTO, SEM FONTE (numero de interface) */
export const PAINEL_MS = 180;
/** onde o saco aparece na tela com o painel aberto. PROPOSTO, SEM FONTE (numero de interface, nao de jogo).
    `largo` (de 900 px em diante): a fracao da largura em que ele fica, a esquerda do painel; `movel` (abaixo): a fracao da altura, no alto,
    acima da folha que sobe da base */
export const SACO_NA_TELA = { largo: 0.41, movel: 0.26 } as const;

/** abaixo de 900 px a camera se aproxima do saco no lugar: a distancia dela vira esta fracao da de antes (1 = sem zoom). So a vista, volta ao sair.
    PROPOSTO, SEM FONTE (numero de interface, nao de jogo) */
export const ZOOM_LUGAR_MOVEL = 0.55;

export type Lugar = "saco";
/** a chave propria da preferencia (ao lado da do save; nunca no save) */
export const CHAVE_VIAGEM = CHAVE + "-viagem";

/** o estado da viagem: para onde vai (0 a ilha, 1 o lugar), de onde saiu e quando */
export const VIAGEM: { alvo: 0 | 1; de: number; desde: number } = { alvo: 0, de: 0, desde: 0 };

/* ---------- a preferencia "Viagem da camera" (Ajustes) */
const ouvintes = new Set<() => void>();
let ligada: boolean | null = null;
function lerLigada(): boolean {
  try {
    const q = new URLSearchParams(location.search).get("viagem");
    if (q === "0") return false;
    if (q === "1") return true;
  } catch { /* sem endereco */ }
  if (ligada !== null) return ligada;
  try { ligada = localStorage.getItem(CHAVE_VIAGEM) !== "0"; } catch { ligada = true; }
  return ligada;
}
/** a viagem esta ligada (o padrao): a camera anda; desligada, corte seco */
export const viagemLigada = (): boolean => lerLigada();
export function escolherViagem(v: boolean): void {
  ligada = v;
  try { localStorage.setItem(CHAVE_VIAGEM, v ? "1" : "0"); } catch { /* preferencia de tela */ }
  for (const o of ouvintes) o();
}
export function useViagemLigada(): boolean {
  return useSyncExternalStore(o => { ouvintes.add(o); return () => { ouvintes.delete(o); }; }, viagemLigada, () => true);
}

/** corte seco agora: "reduzir movimento" do sistema ou a viagem desligada */
export const semAnimacao = (): boolean =>
  (typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches) || !lerLigada();

/* ---------- o progresso */
/** o progresso de 0 a 1 em `agora` (performance.now()); linear no tempo, a vista aplica a suavizacao */
export function progressoViagem(agora: number = performance.now()): number {
  const falta = VIAGEM.alvo - VIAGEM.de;
  if (falta === 0) return VIAGEM.alvo;
  const passo = Math.max(0, agora - VIAGEM.desde) / VIAGEM_MS;
  return falta > 0 ? Math.min(VIAGEM.alvo, VIAGEM.de + passo) : Math.max(VIAGEM.alvo, VIAGEM.de - passo);
}
/** a viagem esta andando (nao chegou ao alvo) */
export const viajando = (agora: number = performance.now()): boolean => progressoViagem(agora) !== VIAGEM.alvo;
/** o lugar esta aberto (ou indo para la): o painel e a camera estao no saco */
export const lugarAberto = (): boolean => VIAGEM.alvo === 1;

function irPara(alvo: 0 | 1, agora: number): void {
  if (VIAGEM.alvo === alvo) return;
  const de = progressoViagem(agora);
  VIAGEM.alvo = alvo; VIAGEM.de = semAnimacao() ? alvo : de; VIAGEM.desde = agora;
}
/** abrir o lugar: a camera vai ao saco e o pet anda ate la */
export const entrarLugar = (agora: number = performance.now()): void => irPara(1, agora);
/** sair do lugar: a camera e o pet voltam */
export const sairLugar = (agora: number = performance.now()): void => irPara(0, agora);
/** clicar ou Esc durante a viagem: pula para o fim */
export function pularViagem(agora: number = performance.now()): void {
  VIAGEM.de = VIAGEM.alvo; VIAGEM.desde = agora;
}
/** de volta ao comeco (testes) */
export function zerarViagem(): void { VIAGEM.alvo = 0; VIAGEM.de = 0; VIAGEM.desde = 0; }
