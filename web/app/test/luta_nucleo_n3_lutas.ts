/* As lutas do gabarito da N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4; D-N-5): o mesmo conjunto para o script que
   grava (scripts/arena_gabarito_n3.ts) e para o teste que confere (test/luta_nucleo_n3_gabarito.test.ts). Os 8 mapas x os 12 pares da
   LP6-1 (test/arena_lp6_lutas.ts) x 2 sementes de teste x as 3 tabelas da luta que as versoes vivas usam: a LUTA_V21 (a v21 e a v22), a
   LUTA_V23 (a v23 a v28, a v30, a v32 e a v35) e a LUTA_V29 (a v29, a v31 e a v36, com o apoio e a elipse da LP6). Cada luta vira o
   sha256 dos eventos e do estado final (o resumoLutaLp6). Com as chaves da N3 desligadas, tem de sair byte a byte igual. */
import { IDS_CENA, type EntradaLuta } from "../motor/arena/index.ts";
import { LUTA_V21, LUTA_V23, LUTA_V29, esquivaDaTabela, statsNpc, statsRivalArena, type TabelaLuta } from "../motor/luta_poc.ts";
import { PARES_LP6, SEMENTES_LP6 } from "./arena_lp6_lutas.ts";

export const TABELAS_N3: readonly TabelaLuta[] = [LUTA_V21, LUTA_V23, LUTA_V29];
const statsDe = (k: string, T: TabelaLuta) => k.startsWith("npc_") ? statsNpc(k, T) : statsRivalArena(k, T);

/** a entrada da luta pela tabela, com tudo o que a tabela liga (o tiro, a esquiva, o apoio e a elipse) */
export function entradaDaTabela(T: TabelaLuta, cena: EntradaLuta["cena"], a: string, b: string, semente: number): EntradaLuta {
  const esq = esquivaDaTabela(T);
  return { cena, semente, a: { forma: a, stats: statsDe(a, T) }, b: { forma: b, stats: statsDe(b, T) },
    ...(T.tiro ? { tiro: T.tiro } : {}), ...(esq ? { esquiva: esq } : {}), ...(T.apoio ? { apoio: T.apoio } : {}), ...(T.arenaPorEstagio ? { arenaPorEstagio: T.arenaPorEstagio } : {}) };
}
/** as lutas do gabarito, cada uma com um id legivel */
export function lutasDoGabaritoN3(): { id: string; entrada: EntradaLuta }[] {
  const out: { id: string; entrada: EntradaLuta }[] = [];
  for (const T of TABELAS_N3) for (const cena of IDS_CENA) for (const [a, b] of PARES_LP6) for (const semente of SEMENTES_LP6)
    out.push({ id: `v${T.versao}|${cena}|${a}|${b}|${semente}`, entrada: entradaDaTabela(T, cena, a, b, semente) });
  return out;
}
