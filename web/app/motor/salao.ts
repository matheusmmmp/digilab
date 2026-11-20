/* O Salao da Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4c; so no jogo e so nos pets v6). Depois do
   titulo da Liga, o jogador escolhe um pet de CADA estagio (Rookie, Champion, Ultimate, Mega), entre o pet ativo e os guardados, e cada um
   luta contra um rival sorteado do mesmo estagio, na ordem dos estagios; perdeu, acabou. Recorde: quantos estagios venceu seguidos (ate 4).
   Na luta da POC (LUTA_POC, LP2b; LP4) o rival e uma forma sorteada do estagio, com o perfil canonico pelo mapeamento da LP2-2, no Coliseu
   (MAPA_SALAO, PROPOSTO); os fatores e as listas do combate por turnos sairam.

   Registro e replay: a luta de cada pet e um evento de luta "l" do registro DELE, {r: "salao", s}, como qualquer luta, com a semente que
   sai do registro dele (sementeSalao: a semente do pet e o numero da tentativa dele no Salao); o motor confere. O rival sai da semente e do
   estagio do pet na hora (formaRivalSalao). A tentativa inteira (os pets, as sementes, quem venceu) e o recorde vao para o registro do Tamer
   (src/tamer.ts, evento "salao"). A entrada pede o titulo, que o pet conhece pelo evento "f" (Motor.abrirFronteira), como na Torre de
   Batalha. */
import { caraterCanonico } from "./catalogo.ts";
import { ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA } from "./constantes.ts";
import { VERSAO_LIGA } from "./liga.ts";
import { criarRng, hashSemente } from "./rng.ts";
import type { Estagio, Forma, FormaAdultaNormal, Linha, Ramo } from "./tipos.ts";

/** versao de pet em que o Salao existe (a da Liga) */
export const VERSAO_SALAO = VERSAO_LIGA;
/** a chave do rival no evento de luta "l" do Salao */
export const RIVAL_SALAO = "salao";
export const SALAO = {
  id: "salao" as const, nome: "Salão",
  frase: "Um pet seu de cada nível, do Rookie ao Mega, cada um contra um rival sorteado do mesmo nível, um depois do outro. Perdeu, acabou.",
};
/** os estagios do Salao, na ordem das lutas */
export const ESTAGIOS_SALAO: readonly Estagio[] = ["crianca", "adolescente", "adulto", "mega"];
const RAMOS: readonly Ramo[] = ["sereno", "arisco"];
const primeiraForma = (l: Linha): FormaAdultaNormal => FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l)!;

/** a semente da luta do pet na tentativa n dele no Salao (1 = a primeira): sai do registro do pet, e o motor confere */
export const sementeSalao = (pet: number, n: number): number => {
  if (!Number.isInteger(n) || n < 1) throw new Error("número de tentativa do Salão inválido: " + n);
  return hashSemente("fronteira", "salao", pet, n);
};
/** a forma do rival do estagio `est` na luta de semente s (rng propria: a especie e, pelo estagio, o ramo, a linha ou a forma adulta) */
export function formaRivalSalao(s: number, est: Estagio): Forma {
  if (!ESTAGIOS_SALAO.includes(est)) throw new Error("estágio fora do Salão: " + est);
  const r = criarRng(hashSemente("salao-rival", s, est)), esp = ESPECIES[r.int(ESPECIES.length)];
  if (est === "crianca") return { esp, est, ramo: RAMOS[r.int(RAMOS.length)] };
  if (est === "adolescente") return { esp, est, ramo: "sereno", linha: LINHAS[r.int(LINHAS.length)] };
  const adulta = FORMAS_AD[r.int(FORMAS_AD.length)];
  return { esp, est, ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta };
}
/** o carater do rival do Salao: nenhum no Rookie; o canonico da forma adulta (ou da primeira forma da linha, no Champion) */
export const caraterDoRivalSalao = (f: Forma): ReturnType<typeof caraterCanonico> | null =>
  f.est === "crianca" ? null : caraterCanonico(f.adulta ? f.adulta as FormaAdultaNormal : primeiraForma(f.linha!));
