/* As lutas do gabarito da LP6-1 (docs/PLANO_LP6_SEGUNDO_GOLPE.md): o mesmo conjunto para o script que grava (scripts/arena_gabarito_lp6.ts)
   e para o teste que confere (test/arena_lp6_gabarito.test.ts). Os 8 mapas x 12 pares de formas x 2 sementes de teste x 2 tabelas da luta
   (a v21, sem o tiro e a esquiva; a v23, com os do lp5_3). Os pares cobrem os 5 estagios, quem atira e quem bate de perto, os 7 com
   habilidade propria e os 2 de golpe generico. */
import { createHash } from "node:crypto";
import { IDS_CENA, configLuta, criarLuta, rodarAteOFim, sorteiosPorFluxo, type EntradaLuta, type Evento, type Luta } from "../motor/arena/index.ts";
import { LUTA_V21, LUTA_V23, esquivaDaTabela, statsNpc, statsRivalArena, type TabelaLuta } from "../motor/luta_poc.ts";

export const PARES_LP6: readonly (readonly [string, string])[] = [
  ["brasa_bebe", "ferrugem_bebe"],                             // Koromon (longe) x DemiVeemon (perto), In-Training
  ["cirro_crianca_arisco", "ferrugem_crianca_arisco"],         // Gabumon (longe) x Veemon (perto)
  ["brasa_crianca_sereno", "limo_crianca_arisco"],             // Agumon x Gomamon, os dois de longe
  ["limo_adolescente_guardiao", "limo_adolescente_brigao"],    // Togemon (habilidade propria) x Stingmon (perto)
  ["brasa_adolescente_brigao", "limo_crianca_sereno"],         // Greymon (Champion) x Palmon (Rookie, perto)
  ["limo_adulto_espelho", "cirro_adulto_duelista"],            // Lillymon (habilidade propria) x WereGarurumon (perto)
  ["ferrugem_adulto_duelista", "cirro_adolescente_colosso"],   // Paildramon (Ultimate) x Gatomon (Champion), os dois de perto
  ["limo_adulto_emboscador", "brasa_adulto_furioso"],          // MetalSeadramon (Mega, habilidade propria de perto) x WarGreymon
  ["limo_adulto_furioso", "ferrugem_adulto_vigia"],            // Imperialdramon FM (Mega, perto) x MegaKabuterimon (Ultimate)
  ["npc_v5_puppetmon", "npc_v5_piedmon"],                      // os dois NPCs Mega com habilidade propria
  ["npc_v5_myotismon", "npc_v5_machinedramon"],                // Ultimate x Mega, habilidade propria
  ["ferrugem_adolescente_guardiao", "npc_v6_marinbullmon"],    // os dois de golpe generico
];
export const SEMENTES_LP6 = [101, 202] as const;
const TABELAS: readonly TabelaLuta[] = [LUTA_V21, LUTA_V23];

const statsDe = (k: string, T: TabelaLuta) => k.startsWith("npc_") ? statsNpc(k, T) : statsRivalArena(k, T);

/** as lutas do gabarito, cada uma com um id legivel */
export function lutasDoGabaritoLp6(): { id: string; entrada: EntradaLuta }[] {
  const out: { id: string; entrada: EntradaLuta }[] = [];
  for (const T of TABELAS) for (const cena of IDS_CENA) for (const [a, b] of PARES_LP6) for (const semente of SEMENTES_LP6) {
    const esq = esquivaDaTabela(T);
    out.push({ id: `v${T.versao}|${cena}|${a}|${b}|${semente}`, entrada: {
      cena, semente, a: { forma: a, stats: statsDe(a, T) }, b: { forma: b, stats: statsDe(b, T) },
      ...(T.tiro ? { tiro: T.tiro } : {}), ...(esq ? { esquiva: esq } : {}) } });
  }
  return out;
}

/** a luta inteira e o resumo dela: o sha256 do JSON de todos os eventos e do estado final dos dois lutadores, e o resultado */
export function resumoLutaLp6(e: EntradaLuta): { sha: string; vencedor: string | null; relogio: number; vidaA: number; vidaB: number; eventos: number } {
  const L: Luta = criarLuta(configLuta(e), sorteiosPorFluxo(e.semente)), ev: Evento[] = [];
  const res = rodarAteOFim(L, x => { ev.push(...x); });
  const fim = [L.a, L.b].map(u => [u.hp, u.x, u.y, u.estado, u.recarga, u.recSk, u.dano, u.golpes, u.dash, u.reacao, u.esperaTiro]);
  const sha = createHash("sha256").update(JSON.stringify({ ev, fim })).digest("hex");
  return { sha, vencedor: res.vencedor, relogio: res.relogio, vidaA: res.vidaA, vidaB: res.vidaB, eventos: ev.length };
}
