/* O Salao da Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4c; so no jogo e so nos pets v6). Depois do
   titulo da Liga, o jogador escolhe um pet de CADA estagio (Rookie, Champion, Ultimate, Mega), entre o pet ativo e os guardados, e cada um
   luta contra um rival sorteado do mesmo estagio, na ordem dos estagios; perdeu, acabou. Recorde: quantos estagios venceu seguidos (ate 4).
   - o rival: o bot canonico do estagio (Rookie: o ramo, sereno ou arisco, com a semente de 3 regras da web; Champion: a linha, com a lista
     do adolescente; Ultimate e Mega: a forma adulta, com a lista canonica V21D e a tecnica e a passiva), numa das 4 especies, com o carater
     canonico (os mesmos bots de referencia das metas de estagio, test/calibrar_escala_v6.mjs); E = vida do estagio na escala dos pets v6,
     sem treino, vezes FATOR_SALAO = 1. SEM calibracao (decisao do Matheus);
   - o pet: como na Liga e nas outras instalacoes (treino absoluto na escala, a lista dele; os chips valem, as cartas nao); o limite de turnos
     e do desafiado, o rival.

   Registro e replay: a luta de cada pet e um evento de luta "l" do registro DELE, {r: "salao", s}, como qualquer luta, com a semente que
   sai do registro dele (sementeSalao: a semente do pet e o numero da tentativa dele no Salao); o motor confere. O rival sai da semente e do
   estagio do pet na hora (formaRivalSalao). A tentativa inteira (os pets, as sementes, quem venceu) e o recorde vao para o registro do Tamer
   (src/tamer.ts, evento "salao"). A entrada pede o titulo, que o pet conhece pelo evento "f" (Motor.abrirFronteira), como na Torre de
   Batalha e no Palacio. */
import { ADOL_V21, CRIANCA_V21, copiarGambits, gambitsAdulto } from "./bots.ts";
import { ESCALA, caraterCanonico, perfilDe } from "./catalogo.ts";
import type { Lutador, RegrasLuta } from "./combate.ts";
import { CV, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA } from "./constantes.ts";
import { VERSAO_LIGA } from "./liga.ts";
import { nomeForma } from "./nomes.ts";
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
/** o fator dos rivais do Salao: 1, o da Liga (sem calibracao) */
export const FATOR_SALAO = 1;
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
/** o lutador do rival: o bot canonico do estagio (ver o cabecalho); com a escala ligada (o app), E = vida do estagio na escala dos pets v6 x
    fator, sem treino */
export function rivalSalao(s: number, est: Estagio, R: RegrasLuta, fator: number = FATOR_SALAO): Lutador {
  const f = formaRivalSalao(s, est);
  const car = f.est === "crianca" ? null : caraterCanonico(f.adulta ? f.adulta as FormaAdultaNormal : primeiraForma(f.linha!));
  const g = f.est === "crianca" ? CRIANCA_V21[f.ramo!] : f.est === "adolescente" ? ADOL_V21[f.linha!] : gambitsAdulto(f.adulta as FormaAdultaNormal, R);
  const p = perfilDe(f, car, 1, null, true, VERSAO_SALAO);
  const cond = ESCALA.ligada ? { ...p, escala: p.escala! * fator } : p;
  return { nome: "Rival " + nomeForma(f), estilo: { nome: `salao:${est}`, gambits: copiarGambits(g), eps: CV.eps }, cond };
}
