/* Nova geracao (pranchas HerEscolher, HerPrevia, HerConfirmar, HerOvo, HerDesktop, HerGeracoes). Pai 1 = o pet ativo
   (adulto e vivo); pai 2 = um log: um pet em espera ou um arquivo importado de outro dono (fica na espera). Ao cruzar,
   o pai ativo se APOSENTA: sai do jogo e vai para Diario · Geracoes (so para ver); o filho (pet v4, evento de origem
   no comeco do registro) vira o ativo e choca. O outro pai continua onde estava. Nao da para desfazer. */
import { useEffect, useState } from "preact/hooks";
import { CHE, EIXOS_TEMP, Motor, hashSemente, type EixoTemperamento, type Especie, type EventoRegistro } from "../motor/index.ts";
import { jogoAtual, trocarMotor } from "./jogo.ts";
import { CHAVE_GUARDADOS, abrirGuardado, lerGuardados } from "./pets.ts";
import { CHAVE, textoSave } from "./save.ts";

export const CHAVE_GERACOES = CHAVE + "-geracoes";

/* ------------------------------------------------ tela (aberta de Meus pets; pai 2 pre-escolhido opcional) */
let aberta: { pai2: number | null } | null = null;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
export function abrirHeranca(pai2: number | null = null): void { aberta = { pai2 }; avisar(); }
export function fecharHeranca(): void { aberta = null; avisar(); }
export function useHeranca(): { pai2: number | null } | null {
  const [, t] = useState(0);
  useEffect(() => { const f = () => t(x => x + 1); ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return aberta;
}

/** geracao de um pet: 1 sem origem; filho = 1 + a maior geracao dos pais */
export const geracao = (m: Motor): number => m.origem ? 1 + Math.max(...m.origem.pais.map(p => p.ger ?? 1)) : 1;
export const podeSerPai = (m: Motor): boolean => m.estagioAtual === "adulto" && !m.morte;

/** os pets em espera, com o motivo quando nao podem ser pai */
export function candidatos(): { i: number; m: Motor; ok: boolean }[] {
  return lerGuardados().map((g, i) => { const m = abrirGuardado(g); return { i, m, ok: podeSerPai(m) }; });
}

/** o que o filho pode herdar: especies (1 em 2, ou certa) e, por eixo, os pais, a media e a faixa (media +- 2 sigma) */
export interface Previa { especies: Especie[]; eixos: { e: EixoTemperamento; p: number; q: number; media: number; faixa: [number, number] }[] }
export function previa(p: Motor, q: Motor): Previa {
  const cl = (x: number) => Math.max(-1, Math.min(1, x));
  return {
    especies: p.especie === q.especie ? [p.especie] : [p.especie, q.especie],
    eixos: EIXOS_TEMP.map(e => {
      const media = (p.temp[e] + q.temp[e]) / 2;
      return { e, p: p.temp[e], q: q.temp[e], media, faixa: [cl(media - 2 * CHE.sigma), cl(media + 2 * CHE.sigma)] as [number, number] };
    }),
  };
}

/** um pai aposentado (Diario · Geracoes): o registro dele, a geracao e o filho */
export interface Aposentado { semente: number; log: EventoRegistro[]; versao: number; ger: number; filho: number; quando: number }
export function lerAposentados(): Aposentado[] {
  try { return JSON.parse(localStorage.getItem(CHAVE_GERACOES) || "[]") as Aposentado[]; } catch { return []; }
}

/** cruza o ativo com o guardado i: o ativo se aposenta, o filho vira o ativo (choca). Devolve o filho */
export function cruzar(i: number): Motor {
  const ativo = jogoAtual().motor, g = lerGuardados(), par = g[i];
  if (!par) throw new Error("pet em espera não existe: " + i);
  const outro = abrirGuardado(par);
  if (!podeSerPai(ativo) || !podeSerPai(outro)) throw new Error("os dois pais precisam ser adultos e vivos");
  const s = (Date.now() ^ Math.floor(Math.random() * 1e9)) >>> 0;
  const filho = Motor.cruzar(ativo, outro, s, hashSemente("heranca", s), "dono", [geracao(ativo), geracao(outro)]);
  const ap = lerAposentados();
  ap.push({ ...JSON.parse(textoSave(ativo)), ger: geracao(ativo), filho: s, quando: Date.now() });
  localStorage.setItem(CHAVE_GERACOES, JSON.stringify(ap));
  localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
  trocarMotor(filho, "novo", 16);
  return filho;
}
