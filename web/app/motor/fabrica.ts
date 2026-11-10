/* A Fabrica da Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4c; so no jogo). Depois do titulo da Liga, o
   jogador NAO usa o proprio pet: a cada tentativa, 3 Digimon alugados (Megas, formas e especies sorteadas, sem treino e sem itens); ele
   escolhe 1 e luta series de 3 lutas contra Megas sorteados:
   - sem cura dentro da serie: o alugado leva a vida de uma luta para a outra; cada rival comeca inteiro; a serie seguinte comeca com o
     alugado inteiro de novo;
   - ao vencer uma luta, o jogador pode trocar o alugado pelo rival derrotado, que entra inteiro;
   - perdeu (ou empatou), a tentativa acabou;
   - a serie vencida conta, e a tentativa segue serie apos serie ate perder. Recorde: a maior sequencia de series vencidas.
   Na luta da POC (LUTA_POC, LP2b; LP-5 revista; LP4) os alugados e os rivais lutam no nucleo de motor/arena/, com os numeros do perfil
   canonico do Mega pelo mapeamento da LP2-2 (sem fator: o mapeamento nao tem escala), no mapa MAPA_FABRICA (PROPOSTO).

   Registro e replay: nenhum pet do jogador luta, entao as lutas vao SO para o registro do Tamer (src/tamer.ts: "fabrica", "fabrica_luta",
   "fabrica_troca"), reproduziveis sozinhas a partir dele. A semente da tentativa sai do registro do Tamer (o numero da tentativa,
   sementeFabrica); os alugueis, os rivais e as sementes das lutas saem dela, e o replay confere cada uma. Nada daqui toca pet nenhum.

   As Fabricas do combate por turnos (v6, v9, v13 e v14) sairam com ele: o registro do Tamer descarta as tentativas delas (src/tamer.ts, o
   descarte 7 da LP4). So ha a v21. */
import { caraterCanonico } from "./catalogo.ts";
import { ESPECIES, FORMAS_AD, LINHA_DA_FORMA } from "./constantes.ts";
import { chaveSprite } from "./nomes.ts";
import { lutar as lutarArena, sorteiosPorFluxo, type ResultadoLuta as ResultadoArena, type Stats as StatsArena } from "./arena/index.ts";
import { MAPA_FABRICA, statsRivalForma } from "./luta_poc.ts";
import { criarRng, hashSemente } from "./rng.ts";
import type { Forma, FormaAdultaNormal } from "./tipos.ts";

export const FABRICA = {
  id: "fabrica" as const, nome: "Fábrica",
  frase: "Você não usa o seu pet: aluga 1 de 3 Megas sorteados e luta séries de 3 lutas sem cura. Ao vencer, pode trocar o alugado pelo rival derrotado, que entra com a vida cheia.",
};
/** quantos alugados a tentativa oferece e quantas lutas tem uma serie */
export const ALUGUEIS_FABRICA = 3;
export const LUTAS_SERIE_FABRICA = 3;
/** a Fabrica da luta da POC (LUTA_POC, LP2b; LP-5 revista): os alugados e os rivais lutam no nucleo de motor/arena/, com os numeros do perfil
    canonico do Mega pelo mapeamento da LP2-2 (sem o fator dos rivais: o mapeamento nao tem escala), no mapa MAPA_FABRICA (PROPOSTO). As series
    de 3, sem cura dentro da serie, e a troca pelo derrotado, que entra inteiro, ficam. Desde a LP4, a unica */
export const VERSAO_FABRICA_POC = 21;
/** as versoes das regras da Fabrica que o registro conhece: so a da luta da POC (LP4) */
export const VERSOES_FABRICA: readonly number[] = [VERSAO_FABRICA_POC];
export const VERSAO_FABRICA_ATUAL = VERSAO_FABRICA_POC;
/** as regras da Fabrica (so a versao, desde a LP4: a luta e a da POC, sem fator, e a troca entra inteira) */
export interface RegraFabrica { versao: number }
export function regraFabrica(versao: number): RegraFabrica {
  if (versao === VERSAO_FABRICA_POC) return { versao };
  throw new Error(`versão das regras da Fábrica desconhecida: ${JSON.stringify(versao)} (só a ${VERSAO_FABRICA_POC}, da luta em tempo real; as do combate por turnos saíram)`);
}

/** a semente da tentativa n (1 = a primeira) do Tamer na Fabrica: sai do registro do Tamer (quantas tentativas ele ja fez), e o replay confere */
export const sementeFabrica = (n: number): number => {
  if (!Number.isInteger(n) || n < 1) throw new Error("número de tentativa da Fábrica inválido: " + n);
  return hashSemente("fronteira", "fabrica", n);
};
/** a semente da luta k (0 = a primeira) da tentativa de semente s */
export const sementeLutaFabrica = (s: number, k: number): number => {
  if (!Number.isInteger(k) || k < 0) throw new Error("luta da Fábrica inválida: " + k);
  return hashSemente("fabrica-luta", s, k);
};
const mega = (adulta: FormaAdultaNormal, esp: Forma["esp"]): Forma => ({ esp, est: "mega", ramo: "sereno", linha: LINHA_DA_FORMA[adulta], adulta });
/** os 3 alugados da tentativa de semente s: 3 formas adultas diferentes (arquetipos distintos) no Mega, cada uma numa especie sorteada */
export function alugueisFabrica(s: number): Forma[] {
  const r = criarRng(hashSemente("fabrica-aluguel", s)), resto = [...FORMAS_AD], out: Forma[] = [];
  for (let i = 0; i < ALUGUEIS_FABRICA; i++) {
    const adulta = resto.splice(r.int(resto.length), 1)[0];
    out.push(mega(adulta, ESPECIES[r.int(ESPECIES.length)]));
  }
  return out;
}
/** o Mega do rival da luta k da tentativa de semente s: uma das 8 formas adultas numa das 4 especies (rng propria da luta) */
export function formaRivalFabrica(s: number, k: number): Forma {
  if (!Number.isInteger(k) || k < 0) throw new Error("luta da Fábrica inválida: " + k);
  const r = criarRng(hashSemente("fabrica-rival", s, k)), adulta = FORMAS_AD[r.int(FORMAS_AD.length)];
  return mega(adulta, ESPECIES[r.int(ESPECIES.length)]);
}
/** uma luta jogada da tentativa: o indice (0 = a primeira), a semente, o alugado e o rival, o resultado e a vida do alugado no fim (fracao) */
export interface LutaFabrica {
  /** `poc`: a luta (o nucleo da luta da POC) */
  k: number; s: number; alugado: Forma; rival: Forma; poc: ResultadoArena; venceu: boolean; vidaFim: number;
  /** depois desta vitoria o jogador trocou o alugado por este rival */
  trocou: boolean;
}
/** a proxima luta da tentativa: o indice, a semente, a serie (1 = a primeira), a luta dentro dela (1 a 3) e o rival */
export interface ProximaLutaFabrica { k: number; s: number; serie: number; naSerie: number; rival: Forma }

/** uma tentativa da Fabrica, refeita das decisoes do jogador (a escolha, as lutas e as trocas) e das sementes. Deterministica: o registro do
    Tamer guarda so as decisoes e as sementes (e a versao das regras), e o replay joga as lutas de novo por aqui.
    `versao`: as regras da tentativa (regraFabrica; sem ela, as de hoje). `semente`: so as conferencias (test/) usam outra (a do jogo sai de n) */
export class TentativaFabrica {
  readonly n: number;
  readonly s: number;
  readonly alugueis: readonly Forma[];
  readonly escolha: number;
  readonly regra: RegraFabrica;
  /** o alugado de agora (muda na troca) */
  alugado: Forma;
  lutas: LutaFabrica[] = [];
  /** perdeu (ou empatou) uma luta: a tentativa acabou */
  acabou = false;
  /** na luta da POC: a vida (inteira) com que o alugado comeca a proxima luta, dentro da serie; null = inteiro */
  private iniPoc: number | null = null;
  constructor(n: number, escolha: number, versao: number = VERSAO_FABRICA_ATUAL, semente: number = sementeFabrica(n)) {
    this.regra = regraFabrica(versao);
    this.n = n; this.s = semente; this.alugueis = alugueisFabrica(this.s);
    if (!Number.isInteger(escolha) || escolha < 0 || escolha >= ALUGUEIS_FABRICA) throw new Error("escolha de alugado inválida na Fábrica: " + JSON.stringify(escolha));
    this.escolha = escolha; this.alugado = this.alugueis[escolha];
  }
  get vitorias(): number { return this.lutas.filter(x => x.venceu).length; }
  /** as series vencidas (3 vitorias seguidas cada; a tentativa para na primeira derrota) */
  get series(): number { return Math.floor(this.vitorias / LUTAS_SERIE_FABRICA); }
  /** a fracao da vida com que o alugado entra na proxima luta (1 no comeco de serie) */
  get vidaAgora(): number {
    return this.iniPoc === null ? 1 : this.iniPoc / this.statsPoc(this.alugado).hp;
  }
  proxima(): ProximaLutaFabrica | null {
    if (this.acabou) return null;
    const k = this.lutas.length;
    return { k, s: sementeLutaFabrica(this.s, k), serie: Math.floor(k / LUTAS_SERIE_FABRICA) + 1, naSerie: k % LUTAS_SERIE_FABRICA + 1, rival: formaRivalFabrica(this.s, k) };
  }
  /** os numeros de um Mega na luta da POC: o perfil canonico pelo mapeamento da LP2-2 (alugado e rival iguais, sem fator) */
  statsPoc(f: Forma): StatsArena {
    const adulta = f.adulta as FormaAdultaNormal;
    if (f.est !== "mega" || !FORMAS_AD.includes(adulta)) throw new Error("a Fábrica só tem Megas das 8 formas adultas: " + JSON.stringify(f));
    return statsRivalForma(f, caraterCanonico(adulta));
  }
  /** joga a proxima luta com a semente dada (tem de ser a da tentativa: ninguem escolhe os rivais) */
  lutar(s: number): LutaFabrica {
    const p = this.proxima();
    if (!p) throw new Error(`a tentativa ${this.n} da Fábrica já acabou`);
    if (s !== p.s) throw new Error(`a luta ${p.k + 1} da tentativa ${this.n} da Fábrica tem a semente ${p.s}, não ${s}`);
    /* o alugado leva a vida dentro da serie (iniPoc), e cada rival entra inteiro */
    const A = this.statsPoc(this.alugado), B = this.statsPoc(p.rival), v0 = p.naSerie === 1 ? null : this.iniPoc;
    const r = lutarArena({ cena: MAPA_FABRICA, semente: s, a: { forma: chaveSprite(this.alugado), stats: A, ...(v0 !== null ? { vida0: v0 } : {}) },
      b: { forma: chaveSprite(p.rival), stats: B } }, sorteiosPorFluxo(s));
    const venceu = r.vencedor === "a";
    const luta: LutaFabrica = { k: p.k, s, alugado: this.alugado, rival: p.rival, poc: r, venceu, vidaFim: Math.max(0, r.vidaA) / A.hp, trocou: false };
    this.lutas.push(luta);
    if (venceu) this.iniPoc = r.vidaA; else { this.acabou = true; this.iniPoc = null; }
    return luta;
  }
  /** por que nao da para trocar agora (null: da): so logo depois de uma vitoria, uma vez */
  porqueNaoTroca(): string | null {
    const u = this.lutas[this.lutas.length - 1];
    if (this.acabou) return "a tentativa acabou";
    if (!u) return "a troca vem depois de uma vitória";
    if (u.trocou) return "já trocou depois desta vitória";
    return null;
  }
  /** troca o alugado pelo rival derrotado na ultima luta: ele entra inteiro (a vida e o guts do comeco) */
  trocar(): void {
    const erro = this.porqueNaoTroca();
    if (erro) throw new Error(`troca na Fábrica recusada: ${erro}`);
    const u = this.lutas[this.lutas.length - 1];
    this.iniPoc = null;
    this.alugado = u.rival; u.trocou = true;
  }
}
