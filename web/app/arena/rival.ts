/* O rival do pet na arena em tempo real (correcao do Matheus, 2026-10-29: "e ele que joga, nao sou eu"): um Digimon do mesmo estagio,
   sorteado com a semente da luta (fluxo "rival") e trocavel na tela. PROPOSTO pelo coordenador e pelo worker, SEM FONTE. */
import { criarRng } from "../motor/rng.ts";
import { sementeArena } from "./rng.ts";
import type { DadosArena } from "./tipos.ts";

/** os candidatos a rival de um estagio: parceiros com status proprio, golpe e atlas (o elenco medido no arena_equilibrio.md), sem o
    proprio Digimon do pet */
export function rivaisDoEstagio(d: DadosArena, estagio: string, sem: string): string[] {
  return Object.keys(d.status).filter(n => n !== sem && d.status[n].estagio === estagio && d.status[n].tipo === "PartnerDigiMon"
    && !d.status[n].estimado && !!d.golpes[n] && !!d.atlas.d[n]);
}

/** o rival sorteado de uma luta: o mesmo para a mesma semente */
export function sortearRival(candidatos: readonly string[], semente: number): string {
  if (candidatos.length === 0) throw new Error("arena: nenhum rival do estagio");
  return candidatos[Math.floor(criarRng(sementeArena(semente, "rival")).random() * candidatos.length)];
}
