/* LUTA_POC, LP5-0 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.1; desvio D-LP5-0-1): a sonda das formas que a vida do Motor da. Cada pet vive
   com um dos 4 donos simulados ate o Mega, com as travas da evolucao abertas a mao (o sparring, a taxa, o vinculo e as medalhas, como o
   ultimate() de test/evolucao_canonica.test.ts); a sonda conta as formas de cada estagio. Sem luta: nao e medicao (as sementes sao as
   da calibracao, bases e pets, so para a forma).
   uso (em web/app): node scripts/equilibrio_poc/formas_do_motor.ts -> scripts/medicoes/equilibrio_poc/lp5_0/formas_do_motor.json */
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  ACOES_DONO_JOGO_V11, CAT, CD, CMD, CMG, Motor, TPD, chaveSprite, criarDono, criarRng, hashSemente,
  type Carater, type Especie, type Forma, type TipoDono, type VisaoDono,
} from "../../motor/index.ts";
import { ESTAGIOS_LUTA, commitAtual, type EstagioLuta } from "./comum.ts";
import { basesDa } from "./faixas.ts";

const ehEstagioLuta = (e: string): e is EstagioLuta => (ESTAGIOS_LUTA as readonly string[]).includes(e);
interface PetDaVida { base: number; i: number; semente: number; especie: Especie; forma: Record<EstagioLuta, Forma>; carater: Record<EstagioLuta, Partial<Carater> | null> }
const LUTAS_CHEIAS = () => ({ lutas: 10, vitorias: 10, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 });
/** o pet i da base: uma vida com o dono atencioso, ate o Mega, com a forma e o carater de cada estagio (os da entrada no estagio) */
function petDaVida(base: number, i: number, tipo: TipoDono = "atencioso"): PetDaVida {
  const semente = hashSemente("equilibrio-poc-pet", base, i), m = new Motor(semente), dono = criarDono(tipo);
  const r = criarRng(hashSemente("dono", semente, tipo)), dias = 4, passos = Math.round(dias * TPD / CD.passo), orc = Math.round(CD.porDia * dias);
  const forma: Partial<Record<EstagioLuta, Forma>> = {}, carater: Partial<Record<EstagioLuta, Partial<Carater> | null>> = {};
  let gasto = 0;
  m.liberar(CMD.mega);
  for (let p = 0; p < passos && m.estagioAtual !== "mega"; p++) {
    /* as travas da evolucao abertas a mao: a forma nao depende da luta (a luta e o que se mede) */
    if (m.estagioAtual === "adolescente") { m.sparring = CAT.sparring; m.lutas = LUTAS_CHEIAS(); }
    if (m.estagioAtual === "adulto") { m.lutas = LUTAS_CHEIAS(); if (m.vinc.valor < CMG.vinculo) m.vinc.valor = CMG.vinculo; }
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    for (const a of dono.decidir(v, r).filter(a => ACOES_DONO_JOGO_V11.includes(a))) { if (m.morte || m.estagioAtual === "mega") break; m.observar(a); gasto++; }
    if (m.morte) throw new Error(`bancada: o pet ${semente} (base ${base}, ${i}) morreu: ${m.morte.causa}`);
    const e = m.estagioAtual;
    if (ehEstagioLuta(e) && !forma[e]) { forma[e] = { ...m.forma }; carater[e] = m.carater(); }
  }
  for (const e of ESTAGIOS_LUTA) if (!forma[e]) throw new Error(`bancada: o pet ${semente} (base ${base}, ${i}) nao chegou ao ${e} (ficou ${m.estagioAtual})`);
  return { base, i, semente, especie: m.especie, forma: forma as Record<EstagioLuta, Forma>, carater: carater as Record<EstagioLuta, Partial<Carater> | null> };
}


const TIPOS: readonly TipoDono[] = ["atencioso", "relapso", "aleatorio", "incoerente"], PETS_POR_BASE = 20;
const saida: Record<string, unknown> = { tarefa: "LUTA_POC, LP5-0, a sonda das formas da vida do Motor", commit: commitAtual(), faixa: "calibracao", pets_por_base: PETS_POR_BASE, donos: {} };
for (const tipo of TIPOS) {
  const formas: Record<string, Record<string, number>> = {};
  for (const base of basesDa("calibracao")) for (let i = 0; i < PETS_POR_BASE; i++) {
    const p = petDaVida(base, i, tipo);
    for (const e of ESTAGIOS_LUTA) { const k = chaveSprite(p.forma[e]); (formas[e] ??= {})[k] = (formas[e][k] ?? 0) + 1; }
  }
  (saida.donos as Record<string, unknown>)[tipo] = { formas_distintas: Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, Object.keys(formas[e]).length])), formas };
  console.log(tipo, JSON.stringify(Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, Object.keys(formas[e]).length]))));
}
const dir = fileURLToPath(new URL("../medicoes/equilibrio_poc/lp5_0/", import.meta.url));
mkdirSync(dir, { recursive: true });
writeFileSync(dir + "formas_do_motor.json", JSON.stringify(saida, null, 1) + "\n");
