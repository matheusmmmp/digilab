/* A Fabrica da Fronteira de Batalha (docs/DESIGN_FRONTEIRA.md, secoes 3 e 4; medalhas parte 4c; so no jogo). Depois do titulo da Liga, o
   jogador NAO usa o proprio pet: a cada tentativa, 3 Digimon alugados (Megas, formas e especies sorteadas, lista canonica das regras da luta, sem treino
   e sem itens); ele escolhe 1 e luta series de 3 lutas contra Megas sorteados:
   - sem cura dentro da serie: o alugado leva a vida e o guts de uma luta para a outra; cada rival comeca inteiro; a serie seguinte comeca
     com o alugado inteiro de novo;
   - ao vencer uma luta, o jogador pode trocar o alugado pelo rival derrotado. O novo alugado entra com a mesma fracao da vida e o mesmo
     guts (ate o maximo dele) com que o anterior terminou a luta: a troca nao cura;
   - o limite da luta e do desafiado, o rival (como em toda luta dos pets); perdeu (ou empatou), a tentativa acabou;
   - a serie vencida conta, e a tentativa segue serie apos serie ate perder. Recorde: a maior sequencia de series vencidas.
   A forca: todos sao o Mega na escala dos pets, sem treino, vezes FATOR_FABRICA = 1 (o da Liga e das outras instalacoes). SEM calibracao
   (decisao do Matheus); test/conferir_fabrica_salao.mjs so confere que e jogavel.

   Registro e replay: nenhum pet do jogador luta, entao as lutas vao SO para o registro do Tamer (src/tamer.ts: "fabrica", "fabrica_luta",
   "fabrica_troca"), reproduziveis sozinhas a partir dele. A semente da tentativa sai do registro do Tamer (o numero da tentativa,
   sementeFabrica); os alugueis, os rivais e as sementes das lutas saem dela, e o replay confere cada uma. A escala vale sempre aqui
   (perfilDe com comEscala), independente da chave do app: o replay do Tamer nao pode depender dela. Nada daqui toca pet nenhum.

   As regras da Fabrica (rodada de equilibrio geral, fase 3; docs/EQUILIBRIO_GERAL.md, meta M-C2): combate V21E (as listas V21E nos
   alugados e nos rivais), os rivais com FATOR_RIVAL_FABRICA_V9 (os alugados seguem com 1) e a troca entrando com a vida cheia (o
   rival derrotado entra inteiro: vida e guts do comeco). A cura entre as series nao muda (a serie seguinte ja comeca inteira). Calibrado
   em test/conferir_fabrica_salao.mjs --calibrar (sementes de calibracao), artifacts_equilibrio_geral/fase3/fabrica_calibracao.json.
   As Fabricas de antes (v6, sem o campo `v`; e v9) sairam com o combate por turnos (COMBATE-TR R3): so ha a v13, e o registro do Tamer
   descarta as tentativas antigas (src/tamer.ts, registro versao 7). */
import { copiarGambits, gambitsAdulto, listaDaForma } from "./bots.ts";
import { FATORES_V14 } from "./combate_tr/constantes_tr.ts";
import { caraterCanonico, perfilDe } from "./catalogo.ts";
import { jogarLuta } from "./combate_tr/adaptador.ts";
import { desafiadoDaVersao, regrasDaVersao, type Lutador, type RegrasLuta, type ResultadoLuta } from "./combate.ts";
import { CV, ESPECIES, FORMAS_AD, LINHA_DA_FORMA } from "./constantes.ts";
import { nomeForma } from "./nomes.ts";
import { criarRng, hashSemente } from "./rng.ts";
import type { Forma, FormaAdultaNormal } from "./tipos.ts";

export const FABRICA = {
  id: "fabrica" as const, nome: "Fábrica",
  frase: "Você não usa o seu pet: aluga 1 de 3 Megas sorteados e luta séries de 3 lutas sem cura. Ao vencer, pode trocar o alugado pelo rival derrotado, que entra com a vida cheia.",
};
/** quantos alugados a tentativa oferece e quantas lutas tem uma serie */
export const ALUGUEIS_FABRICA = 3;
export const LUTAS_SERIE_FABRICA = 3;
/** o fator de rival (e dos alugados): 1, o da Liga (sem calibracao) */
export const FATOR_FABRICA = 1;
/** o fator dos rivais da Fabrica (os alugados seguem com FATOR_FABRICA) e a troca com a vida cheia. PROPOSTOS; calibrados nas sementes de
    calibracao (ver o cabecalho) */
export const FATOR_RIVAL_FABRICA_V9 = 0.6;
/** a Fabrica da luta em tempo real (COMBATE-TR, etapa R2; D-4): as regras dos pets v13 (CV21E_TR), com o fator e a troca dos v9 (sem
    recalibrar: o equilibrio fica para a rodada do fim). As tentativas antigas (v ausente ou 9) saem do registro do Tamer com aviso
    (src/tamer.ts, registro versao 7) */
export const VERSAO_FABRICA_TR = 13;
/** a Fabrica do candidato v14 (B2; DE-1): as regras CV21E_TR14, o fator dos rivais e as listas candidatas. As tentativas v13 do registro do
    Tamer seguem refazendo-se iguais (CV14-1); as novas gravam esta */
export const VERSAO_FABRICA_V14 = 14;
/** as versoes das regras da Fabrica que o registro conhece (a v13 e a v14) */
export const VERSOES_FABRICA: readonly number[] = [VERSAO_FABRICA_TR, VERSAO_FABRICA_V14];
export const VERSAO_FABRICA_ATUAL = VERSAO_FABRICA_V14;
/** as regras da Fabrica: as regras da luta, o fator dos rivais e se a troca entra inteira */
export interface RegraFabrica { versao: number; R: RegrasLuta; fatorRival: number; trocaInteira: boolean }
export function regraFabrica(versao: number, fatorRival?: number): RegraFabrica {
  if (versao === VERSAO_FABRICA_TR) return { versao, R: regrasDaVersao(VERSAO_FABRICA_TR), fatorRival: fatorRival ?? FATOR_RIVAL_FABRICA_V9, trocaInteira: true };
  if (versao === VERSAO_FABRICA_V14) return { versao, R: regrasDaVersao(VERSAO_FABRICA_V14), fatorRival: fatorRival ?? FATORES_V14.fabrica, trocaInteira: true };
  throw new Error("versão das regras da Fábrica desconhecida: " + JSON.stringify(versao));
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
/** o lutador de um Mega da Fabrica (alugado ou rival): tecnica da linha, passiva da forma, carater canonico, lista canonica das regras da luta, epsilon dos
    bots canonicos; E = vida do Mega na escala x fator, sem treino e sem item (a escala da versao das regras R: CESC_V9). A escala vale sempre (comEscala) */
export function megaFabrica(f: Forma, nome: string, fator: number = FATOR_FABRICA, R: RegrasLuta = regrasDaVersao(VERSAO_FABRICA_TR)): Lutador {
  const adulta = f.adulta as FormaAdultaNormal;
  if (f.est !== "mega" || !FORMAS_AD.includes(adulta)) throw new Error("a Fábrica só tem Megas das 8 formas adultas: " + JSON.stringify(f));
  const p = perfilDe(f, caraterCanonico(adulta), 1, null, true, R.versaoPet, true);
  return { nome, estilo: { nome: `fabrica:${adulta}`, gambits: copiarGambits(listaDaForma(adulta, R, gambitsAdulto(adulta, R))), eps: CV.eps }, cond: { ...p, escala: p.escala! * fator } };
}

/** uma luta jogada da tentativa: o indice (0 = a primeira), a semente, o alugado e o rival, o resultado e a vida do alugado no fim (fracao) */
export interface LutaFabrica {
  k: number; s: number; alugado: Forma; rival: Forma; res: ResultadoLuta; venceu: boolean; vidaFim: number;
  /** depois desta vitoria o jogador trocou o alugado por este rival */
  trocou: boolean;
}
/** a proxima luta da tentativa: o indice, a semente, a serie (1 = a primeira), a luta dentro dela (1 a 3) e o rival */
export interface ProximaLutaFabrica { k: number; s: number; serie: number; naSerie: number; rival: Forma }

/** uma tentativa da Fabrica, refeita das decisoes do jogador (a escolha, as lutas e as trocas) e das sementes. Deterministica: o registro do
    Tamer guarda so as decisoes e as sementes (e a versao das regras), e o replay joga as lutas de novo por aqui.
    `versao`: as regras da tentativa (regraFabrica; sem ela, as de hoje). `semente` e `fatorRival`: so as conferencias (test/) usam outros
    (a semente do jogo sai de n; o fator, da versao) */
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
  /** a vida e o guts com que o alugado comeca a proxima luta, dentro da serie; null = inteiro (comeco de serie) */
  private ini: { hp: number; guts: number } | null = null;
  constructor(n: number, escolha: number, versao: number = VERSAO_FABRICA_ATUAL, semente: number = sementeFabrica(n), fatorRival?: number) {
    this.regra = regraFabrica(versao, fatorRival);
    this.n = n; this.s = semente; this.alugueis = alugueisFabrica(this.s);
    if (!Number.isInteger(escolha) || escolha < 0 || escolha >= ALUGUEIS_FABRICA) throw new Error("escolha de alugado inválida na Fábrica: " + JSON.stringify(escolha));
    this.escolha = escolha; this.alugado = this.alugueis[escolha];
  }
  get vitorias(): number { return this.lutas.filter(x => x.venceu).length; }
  /** as series vencidas (3 vitorias seguidas cada; a tentativa para na primeira derrota) */
  get series(): number { return Math.floor(this.vitorias / LUTAS_SERIE_FABRICA); }
  /** a fracao da vida com que o alugado entra na proxima luta (1 no comeco de serie) */
  get vidaAgora(): number {
    if (!this.ini) return 1;
    return this.ini.hp / this.mega(this.alugado, "Alugado").cond.hpMax;
  }
  /** o lutador de um Mega desta tentativa: alugado (fator 1) ou rival (o fator dos rivais das regras dela) */
  private mega(f: Forma, nome: string, rival = false): Lutador {
    return megaFabrica(f, nome, rival ? this.regra.fatorRival : FATOR_FABRICA, this.regra.R);
  }
  proxima(): ProximaLutaFabrica | null {
    if (this.acabou) return null;
    const k = this.lutas.length;
    return { k, s: sementeLutaFabrica(this.s, k), serie: Math.floor(k / LUTAS_SERIE_FABRICA) + 1, naSerie: k % LUTAS_SERIE_FABRICA + 1, rival: formaRivalFabrica(this.s, k) };
  }
  /** os lutadores da proxima luta (o alugado no lado A), sem jogar */
  lutadores(): { A: Lutador; B: Lutador; ini: { hp: number; guts: number } | null } {
    const p = this.proxima();
    if (!p) throw new Error(`a tentativa ${this.n} da Fábrica já acabou`);
    return { A: this.mega(this.alugado, "Alugado " + nomeForma(this.alugado)), B: this.mega(p.rival, "Rival " + nomeForma(p.rival), true), ini: p.naSerie === 1 ? null : this.ini };
  }
  /** joga a proxima luta com a semente dada (tem de ser a da tentativa: ninguem escolhe os rivais) */
  lutar(s: number): LutaFabrica {
    const p = this.proxima();
    if (!p) throw new Error(`a tentativa ${this.n} da Fábrica já acabou`);
    if (s !== p.s) throw new Error(`a luta ${p.k + 1} da tentativa ${this.n} da Fábrica tem a semente ${p.s}, não ${s}`);
    const { A, B, ini } = this.lutadores(), res = jogarLuta(A, B, s, this.regra.R, ini, desafiadoDaVersao(this.regra.versao));
    const fim = res.E.L[0], venceu = res.pontosA === 1;
    const luta: LutaFabrica = { k: p.k, s, alugado: this.alugado, rival: p.rival, res, venceu, vidaFim: Math.max(0, fim.hp) / fim.hpMax, trocou: false };
    this.lutas.push(luta);
    if (venceu) this.ini = { hp: fim.hp, guts: fim.guts }; else { this.acabou = true; this.ini = null; }
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
    this.ini = null;
    this.alugado = u.rival; u.trocou = true;
  }
}
