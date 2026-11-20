/* O laboratorio do modular no jogo (docs/TAREFA_V3_LAB_MODULAR.md, LM5b; LAB-2, LM5-5, LM5-7 a LM5-9). O pet de teste (v16, motor/pet_lab.ts) tem
   um espaco proprio do save, CHAVE-lab, no mesmo formato {semente, log, versao}: nunca se mistura com o save do pet de hoje (CHAVE) nem com os
   pets guardados (CHAVE-guardados). So um por vez. A chave do laboratorio (CHAVE-lab-ligado) e uma preferencia de tela e vem desligada.
   Abrir mostra o pet de teste na tela Pet sem trocar o pet ativo (jogo.ts: abrirLab). Descartar apaga so CHAVE-lab. Nao ha opcao de baixar o log.
   DC3d da CONVERSA_PET: a "Fala com conteudo (teste)" (CHAVE-lab-fala) tambem e uma preferencia de tela, desligada por padrao. Ela so vale no ovo
   de teste chocado com ela ligada: o ovo ganha a marca "fu" no comeco do registro (o modular com a `fala_unidades`), e o replay le a marca, nao a
   preferencia. Um pet de teste ja chocado segue como esta no registro. */
import { useEffect, useState } from "react";
import { Motor, VERSAO_PET_LAB, petDeTeste, type EventoRegistro } from "../motor/index.ts";
import { ligarProduto } from "./produto.ts";
import { CHAVE, textoSave } from "./save.ts";

export const CHAVE_LAB = CHAVE + "-lab";
export const CHAVE_LAB_LIGADO = CHAVE + "-lab-ligado";
export const CHAVE_LAB_FALA = CHAVE + "-lab-fala";

const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
/** hook: a tela redesenha quando o laboratorio muda (a chave, o ovo, o descarte) */
export function useLab(): number {
  const [n, t] = useState(0);
  useEffect(() => { const f = () => t(x => x + 1); ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return n;
}

/** a chave do laboratorio: desligada ate o jogador ligar (preferencia de tela, fora do save) */
export function labLigado(): boolean {
  try { return localStorage.getItem(CHAVE_LAB_LIGADO) === "1"; } catch { return false; }
}
export function ligarLab(on: boolean): void {
  try { localStorage.setItem(CHAVE_LAB_LIGADO, on ? "1" : "0"); } catch { /* preferencia de tela: sem armazenamento, so nao lembra */ }
  avisar();
}

/** DC3d: a fala com conteudo nos ovos de teste novos: desligada ate o jogador ligar (preferencia de tela, fora do save) */
export function falaComConteudo(): boolean {
  try { return localStorage.getItem(CHAVE_LAB_FALA) === "1"; } catch { return false; }
}
export function ligarFalaComConteudo(on: boolean): void {
  try { localStorage.setItem(CHAVE_LAB_FALA, on ? "1" : "0"); } catch { /* preferencia de tela: sem armazenamento, so nao lembra */ }
  avisar();
}

export type LeituraLab = { tipo: "vazio" } | { tipo: "ok"; motor: Motor } | { tipo: "erro"; erro: string };
/** le e reproduz o pet de teste; save que existe e nao abre e erro visivel (nada e apagado nem regravado) */
export function lerPetLab(): LeituraLab {
  let bruto: string | null;
  try { bruto = localStorage.getItem(CHAVE_LAB); } catch (err) { return { tipo: "erro", erro: "armazenamento do navegador indisponível: " + String(err) }; }
  if (bruto === null) return { tipo: "vazio" };
  try {
    const s = JSON.parse(bruto) as { semente?: unknown; log?: unknown; versao?: unknown };
    if (!Number.isInteger(s.semente) || !Array.isArray(s.log)) return { tipo: "erro", erro: "o save do pet de teste não tem semente e registro" };
    if (s.versao !== VERSAO_PET_LAB) return { tipo: "erro", erro: `o save do pet de teste é da versão ${String(s.versao)}, e o laboratório abre só a ${VERSAO_PET_LAB}` };
    return { tipo: "ok", motor: Motor.reproduzir(s.semente as number, s.log as EventoRegistro[], VERSAO_PET_LAB) };
  } catch (err) { return { tipo: "erro", erro: "o save do pet de teste não abre: " + (err instanceof Error ? err.message : String(err)) }; }
}
/** grava o registro do pet de teste no espaco dele */
export function gravarPetLab(m: Motor): void {
  if (m.versao !== VERSAO_PET_LAB) throw new Error("só o pet de teste (v" + VERSAO_PET_LAB + ") vai para o espaço do laboratório");
  localStorage.setItem(CHAVE_LAB, textoSave(m));
}
/** choca o ovo de teste: um pet v16 novo no espaco proprio. So um por vez: com um vivo (ou um save que nao abre), falha */
export function chocarOvoLab(): Motor {
  if (lerPetLab().tipo !== "vazio") throw new Error("já existe um pet de teste; descarte-o antes de chocar outro ovo de teste");
  /* as chaves do produto, como em todo ovo novo do jogo (src/produto.ts): sem elas o bebe chamava pelo relogio (fome a cada 30 min,
     carinho a cada 45), sem olhar o corpo (o Matheus, 2026-11-04). Os pets de teste ja chocados seguem como estao no registro */
  const m = ligarProduto(petDeTeste((Date.now() ^ Math.floor(Math.random() * 1e9)) >>> 0));
  if (falaComConteudo()) m.ligarFalaUnidades();       // DC3d: a marca "fu", depois das chaves do produto e da ponte da luta
  gravarPetLab(m);
  avisar();
  return m;
}
/** descarta o pet de teste: apaga so o espaco dele (a tela confirma antes; os pets de hoje nao sao tocados) */
export function descartarPetLab(): void {
  localStorage.removeItem(CHAVE_LAB);
  avisar();
}
/** o save do pet de teste (um importado v16 entra aqui, nunca no pet ativo nem nos guardados) */
export function guardarImportadoLab(m: Motor): void {
  if (lerPetLab().tipo !== "vazio") throw new Error("já existe um pet de teste; descarte-o antes de importar outro");
  gravarPetLab(m);
  avisar();
}
