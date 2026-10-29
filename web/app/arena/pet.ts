/* A luta do pet na arena em tempo real, sem tela (correcao do Matheus, 2026-10-29: "e o pet lutando sozinho"; e a decisao de 2026-10-29
   de que a batalha em tempo real substitui o combate do jogo inteiro, com plano da coordenacao). Entrada: o Digimon do pet, o do rival,
   a arena e a semente; saida: o resultado. Os dois lados sao a IA da arena; nao ha entrada do jogador. A tela usa a mesma configuracao
   (configLutaPet) e so assiste passo a passo. */
import { LIMITE_MS, OPCOES_PADRAO, STATS_PADRAO } from "./constantes.ts";
import { sorteiosPorFluxo } from "./rng.ts";
import { criarLuta, passo, vivos } from "./sim.ts";
import type { ConfigLuta, DadosArena, IdCena } from "./tipos.ts";

/** o nivel do jogo dos dois lados: 1 (PROPOSTO, SEM FONTE). O estagio do pet ja entra pelo status do Digimon dele (status.json, com
    EQ.pesoEstagio) e o rival e do mesmo estagio; somar um nivel pelo estagio contaria o estagio duas vezes */
export const NIVEL_ARENA = 1;

export interface EntradaLutaPet { pet: string; rival: string; cena: IdCena; semente: number }
export interface ResultadoLutaPet {
  vencedor: "pet" | "rival" | null;   // null: empate, ou chegou ao limite sem fim
  fim: boolean; relogio: number;
  vidaPet: number; vidaRival: number;  // vida que sobrou no fim
}

/** a configuracao da luta do pet: 1 contra 1, os dois pela IA (dificuldade, atributo, ritmo e projeteis do padrao) */
export function configLutaPet(e: EntradaLutaPet): ConfigLuta {
  const lado = (n: string) => ({ equipe: [n], fonte: "jogo" as const, nivel: NIVEL_ARENA, generico: { ...STATS_PADRAO } });
  return { cena: e.cena, dific: OPCOES_PADRAO.dific, forca: OPCOES_PADRAO.forca, ritmo: OPCOES_PADRAO.ritmo, pvel: OPCOES_PADRAO.pvel,
    jogador: false, a: lado(e.pet), b: lado(e.rival) };
}

/** a luta inteira, sem tela: a mesma entrada da sempre o mesmo resultado */
export function lutarPet(dados: DadosArena, e: EntradaLutaPet): ResultadoLutaPet {
  const L = criarLuta(configLutaPet(e), dados, sorteiosPorFluxo(e.semente));
  while (!L.fim && L.relogio < LIMITE_MS) passo(L);
  return {
    vencedor: L.vencedor === "a" ? "pet" : L.vencedor === "b" ? "rival" : null, fim: L.fim, relogio: L.relogio,
    vidaPet: vivos(L, "a").reduce((s, u) => s + u.hp, 0), vidaRival: vivos(L, "b").reduce((s, u) => s + u.hp, 0),
  };
}
