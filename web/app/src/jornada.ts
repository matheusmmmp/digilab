/* Jornada do jogador (pedido do Matheus, 2026-09-28): escolher o brasao -> chocar o ovo -> crescer ate o Ultimate (e o
   Mega, pets v5) -> vencer o Piedmon (Cidadela nos pets v1-v4, Montanha Espiral nos v5) -> mensagem de conclusao. Nos pets v6 (medalhas
   parte 4a, docs/DESIGN_FRONTEIRA.md) a jornada termina na Liga dos Lideres da Fronteira, nao mais no Piedmon. Nada disso muda o motor nem o save: a especie do
   ovo sai da semente (motor), entao escolher o brasao e sortear sementes ate cair na especie escolhida. A conclusao
   vista fica numa chave propria (sementes dos pets que ja viram a mensagem; a da Liga, noutra, para o pet v6 que viu a do Piedmon
   antes desta parte ver a nova). */
import { useEffect, useState } from "preact/hooks";
import { ESPECIES, Motor, VERSAO_LIGA, campanhaDe, hashSemente, type Especie, type Ritmo } from "../motor/index.ts";
import { jogoAtual, trocarMotor } from "./jogo.ts";
import { CHAVE, textoSave } from "./save.ts";
import { CHAVE_GUARDADOS, lerGuardados } from "./pets.ts";

export const CHAVE_CONCLUSAO = CHAVE + "-conclusao";
/** pets v6: a conclusao vista vem da Liga dos Lideres (chave propria) */
export const CHAVE_CONCLUSAO_LIGA = CHAVE + "-conclusao-liga";
/** o chefe da campanha do pet: o ultimo desafio da ultima ilha (o Piedmon; a chave muda com a versao) */
export const chefeDe = (m: Motor): string => { const c = campanhaDe(m.versao); return c[c.length - 1].k; };

/* ------------------------------------------------ escolha do brasao (tela cheia) */
let escolhendo = false;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
export function abrirEscolhaBrasao(): void { escolhendo = true; avisar(); }
export function fecharEscolhaBrasao(): void { escolhendo = false; avisar(); }
export function useEscolhaBrasao(): boolean {
  const [, t] = useState(0);
  useEffect(() => { const f = () => t(x => x + 1); ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return escolhendo;
}

/** especie que a semente da ao ovo (a mesma conta do construtor do Motor) */
export const especieDaSemente = (s: number): Especie => ESPECIES[hashSemente("especie", s) % ESPECIES.length];
/** semente nova (relogio + acaso, como o ovo novo do HTML) cujo ovo e da especie pedida */
export function sementeDoBrasao(esp: Especie): number {
  for (let i = 0; i < 10000; i++) {
    const s = (Date.now() ^ Math.floor(Math.random() * 1e9) ^ (i * 2654435761)) >>> 0;
    if (especieDaSemente(s) === esp) return s;
  }
  throw new Error("não achei um ovo desse brasão");
}
/** choca um ovo do brasao escolhido. guardarAtivo: o pet ativo vai para os guardados (nao se perde) */
export function chocarDoBrasao(esp: Especie, guardarAtivo = false, ritmo: Ritmo = "rapida"): void {
  if (guardarAtivo) {
    const g = lerGuardados();
    g.push(JSON.parse(textoSave(jogoAtual().motor)));
    localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
  }
  const m = new Motor(sementeDoBrasao(esp));
  if (m.especie !== esp) throw new Error("ovo de outro brasão");
  if (ritmo !== "rapida") m.configurar(ritmo);
  trocarMotor(m, "novo", 16);
  guardarNoProximoOvo = false;
  fecharEscolhaBrasao();
}
/** a conclusao pede para guardar o campeao quando o dono escolher um ovo novo por ela */
let guardarNoProximoOvo = false;
export const guardarAtivoNoProximoOvo = (): boolean => guardarNoProximoOvo;
export function novoOvoGuardandoAtivo(): void { guardarNoProximoOvo = true; abrirEscolhaBrasao(); }

/* ------------------------------------------------ conclusao */
/** a jornada termina na Liga dos Lideres (pets v6) ou no chefe da campanha (v1-v5) */
export const terminaNaLiga = (m: Motor): boolean => m.versao >= VERSAO_LIGA;
const chaveConclusao = (m: Motor): string => terminaNaLiga(m) ? CHAVE_CONCLUSAO_LIGA : CHAVE_CONCLUSAO;
const vistas = (chave: string): number[] => { try { return JSON.parse(localStorage.getItem(chave) || "[]") as number[]; } catch { return []; } };
export const conclusaoVista = (m: Motor): boolean => vistas(chaveConclusao(m)).includes(m.semente);
export function marcarConclusao(m: Motor): void {
  const k = chaveConclusao(m);
  try { localStorage.setItem(k, JSON.stringify([...new Set([...vistas(k), m.semente])])); } catch { /* preferencia de tela */ }
}
/** venceu o chefe da campanha (o Piedmon) */
export const venceuOChefe = (m: Motor): boolean => (m.campanha[chefeDe(m)] ?? 0) > 0;
/** a jornada acabou: nos pets v6, venceu a Liga dos Lideres (o titulo); nos v1-v5, o chefe da campanha */
export const concluiuJornada = (m: Motor): boolean => terminaNaLiga(m) ? m.liga.titulos > 0 : venceuOChefe(m);

/** os marcos da jornada, na ordem, com o que o motor diz de cada um */
export function marcos(m: Motor): { rotulo: string; feito: boolean }[] {
  const ev = (est: string) => m.evolucoes.some(x => x.estagio === est);
  return [
    { rotulo: "Chocou o ovo", feito: true },
    { rotulo: "Virou Rookie", feito: ev("crianca") },
    { rotulo: "Virou Champion", feito: ev("adolescente") },
    { rotulo: "Virou Ultimate", feito: ev("adulto") },
    ...(m.versao >= 5 ? [{ rotulo: "Virou Mega", feito: ev("mega") }] : []),
    ...m.lugares.map((L, i) => ({ rotulo: `Venceu ${L.nome}`, feito: m.lugarVencido(i) })),
    ...(terminaNaLiga(m) ? [{ rotulo: "Venceu a Liga dos Líderes", feito: m.liga.titulos > 0 }] : []),
  ];
}
