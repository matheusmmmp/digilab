/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md): o nucleo da bancada do equilibrio da luta em tempo real. Sem tela: CPU contra CPU,
   com semente, pelo nucleo da POC (lutarNucleoPoc) e os Motor de verdade para os pets.
   - o CANDIDATO (secao 4.3): os numeros que a rodada pode mexer (secao 3.1), so aqui, sem mudar o jogo. O CANDIDATO_V21 e o jogo de hoje, e
     o teste test/equilibrio_poc_bancada.test.ts confere que ele refaz o statsDaLuta, o statsNpc, o statsRivalArena e o statsRivalForma;
   - os PETS (D-LP5-2; desvio D-LP5-0-1): uma forma do jogo do nivel, sorteada pela semente do pet, com o carater canonico; a vida do
     Motor com um dono so da uma forma por estagio (a sonda formas_do_motor.ts mede);
   - o TREINO TIPICO (D-LP5-2): os pontos de um dono que alterna os 6 exercicios pelo TreinoPet.sessao, estagio a estagio, com a aptidao da
     especie e a fadiga (espera ate a fadiga cair abaixo do limiarPausa). Para um total n, a trajetoria e cortada na sessao que passa de n,
     com a ultima sessao interpolada: o total sai exato e a divisao e a do dono;
   - as SEMENTES: por base, o pet i e hashSemente("equilibrio-poc-pet", base, i) e a luta k, hashSemente("equilibrio-poc", base, k) (secao 5).
   Os numeros desta bancada (os tamanhos das amostras) sao PROPOSTOS, SEM FONTE. */
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  CMG, CTR, CIT, FORMAS_ARENA, TIRO_POC_V21, LIMITE_POC_MS, MAPA_STATS, STATS, TreinoPet,
  caraterCanonico, criarRng, rivaisArena, formaDaChave, hashSemente, lutarNucleoPoc, multEstagio, NPC, sorteiosPoc, statsDe,
  type Carater, type Especie, type Estagio, type Exercicio, type Forma, type FormaAdultaNormal, type IdCena, type Stat, type Stats, type StatsPoc, type TiroPoc, type EsquivaPoc,
} from "../../motor/index.ts";
import { APOIO_LP6, APOIO_TABELA, ARENA_POR_ESTAGIO_LP6, type Apoio, type ArenaPorEstagio, type DadosForma, type TabelaFormas } from "../../motor/arena/index.ts";

/* ---------------------------------------------------------------- o candidato */
export type EstagioLuta = "crianca" | "adolescente" | "adulto" | "mega";
export const ESTAGIOS_LUTA: readonly EstagioLuta[] = ["crianca", "adolescente", "adulto", "mega"];
export interface Candidato {
  nome: string;
  /** as bases do mapeamento: o lutador neutro (o MAPA_STATS) */
  mapa: { neutro: number; hp: number; atk: number; def: number; vel: number; cad: number; hcd: number; crit: number; erro: number; hpot: number; esquiva: number; atordoa: number };
  /** o expoente de cada stat na razao ((s / neutro)^gama); 1 e a linha reta de hoje (a D-LP5-4) */
  gama: Record<Stat, number>;
  /** o peso de um ponto de treino (e de chip) na luta: hoje o CTR.pesoPontoCombate */
  pesoPonto: number;
  /** o multiplicador do estagio na vida (hoje o multEstagio do catalogo) e, se preciso, no ataque (hoje 1) */
  multVida: Record<EstagioLuta, number>;
  multAtk: Record<EstagioLuta, number>;
  /** o total de cada NPC (hoje o de bots.ts), dividido igualmente pelos 6 stats */
  npcTotal: Record<string, number>;
  /** a divisao do total de um NPC pelos 6 stats (a D-LP5-9; D-LP5-18): o peso de cada stat, somando 6. Um NPC fora daqui divide igual
      (hoje, todos) */
  npcDivisao: Record<string, Record<Stat, number>>;
  /** os pontos de treino dos rivais de cada lugar (hoje 0), postos pela trajetoria do dono tipico da especie do rival */
  treinoRival: { arena: number; salao: number; liga: number; torre: number; fabrica: number };
  /** o fator nos 6 stats dos rivais de cada torneio (hoje 1; D-LP5-20): o rival da forma com os stats vezes o fator, antes do mapeamento.
      O alugado da Fabrica nao leva o fator */
  fatorRival: { salao: number; liga: number; torre: number; fabrica: number };
  /** a distancia do tiro (o nucleo, D-LP5-12; hoje o TIRO_POC_V21, a luta da POC) */
  tiro: TiroPoc;
  /** a esquiva pela perspicacia e pela velocidade (o nucleo, D-LP5-14): ligada 0 = a luta da POC. A perspicacia e
      (mira / neutro)^gamaMira x (1 + kAtento x o eixo atento do carater); a agilidade, (folego / neutro)^gamaFolego */
  esquiva: EsquivaPoc & { ligada: number; gamaMira: number; kAtento: number; gamaFolego: number };
  /** o golpe de apoio (LP6-1; docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 3): ligado 0 = a luta sem apoio, byte a byte. `ritmo` e o tempo do clipe
      do apoio em vezes o do golpe (a tabela do git tem 0,6; outro valor so na bancada, pela tabelaDoRitmo) */
  apoio: Apoio & { ligado: number; ritmo: number };
  /** a elipse pelo estagio (LP6-1; secao 4a): ligada 0 = a elipse de sempre, byte a byte */
  arena: ArenaPorEstagio & { ligada: number };
}
const NPCS_V6 = ["npc_tier1_brutamontes", "npc_tier2_sentinela", "npc_tier2_carcereiro", "npc_tier2_porteiro", "npc_v6_youkomon",
  "npc_v5_myotismon", "npc_v6_marinbullmon", "npc_v5_puppetmon", "npc_v5_machinedramon", "npc_v5_piedmon"] as const;
export const CANDIDATO_V21: Candidato = Object.freeze({
  nome: "v21",
  mapa: { ...MAPA_STATS },
  gama: Object.fromEntries(STATS.map(k => [k, 1])) as Record<Stat, number>,
  pesoPonto: CTR.pesoPontoCombate,
  multVida: Object.fromEntries(ESTAGIOS_LUTA.map(e => [e, multEstagio(e)])) as Record<EstagioLuta, number>,
  multAtk: { crianca: 1, adolescente: 1, adulto: 1, mega: 1 },
  npcTotal: Object.fromEntries(NPCS_V6.map(k => { const n = NPC[k]; if (!n) throw new Error(`bancada: o NPC ${k} sumiu`); return [k, n.total]; })),
  npcDivisao: {},
  treinoRival: { arena: 0, salao: 0, liga: 0, torre: 0, fabrica: 0 },
  fatorRival: { salao: 1, liga: 1, torre: 1, fabrica: 1 },
  tiro: { ...TIRO_POC_V21 },
  esquiva: { ligada: 0, kChance: 1, kReacao: 1, kDash: 1, chanceMax: .95, pertoChance: 0, pertoReacao: 200, contraMs: 0, gamaMira: 1, kAtento: .5, gamaFolego: 1 },
  apoio: { ligado: 0, ...APOIO_LP6, ritmo: APOIO_TABELA.ritmo },
  arena: { ligada: 0, ...ARENA_POR_ESTAGIO_LP6 },
});
/** a esquiva do candidato na entrada da luta: so ligada (senao a luta da POC, byte a byte) */
export const esquivaDe = (c: Candidato): EsquivaPoc | undefined => {
  if (c.esquiva.ligada !== 0 && c.esquiva.ligada !== 1) throw new Error(`bancada: esquiva.ligada e 0 ou 1 (${c.esquiva.ligada})`);
  if (!c.esquiva.ligada) return undefined;
  const { kChance, kReacao, kDash, chanceMax, pertoChance, pertoReacao, contraMs } = c.esquiva;
  return { kChance, kReacao, kDash, chanceMax, pertoChance, pertoReacao, contraMs };
};
/** as chaves da LP6 na entrada da luta (LP6-3): o apoio, a elipse pelo estagio e a tabela das formas do ritmo do apoio. Desligadas, nada
    entra, e a luta sai a de sempre, byte a byte */
export interface ExtrasLp6 { apoio?: Apoio; arenaPorEstagio?: ArenaPorEstagio; tabela?: TabelaFormas }
const zeroOuUm = (x: number, nome: string) => { if (x !== 0 && x !== 1) throw new Error(`bancada: ${nome} e 0 ou 1 (${x})`); return x === 1; };
export function extrasLp6(c: Candidato): ExtrasLp6 {
  const ap = zeroOuUm(c.apoio.ligado, "apoio.ligado"), ar = zeroOuUm(c.arena.ligada, "arena.ligada");
  if (!ap && c.apoio.ritmo !== APOIO_TABELA.ritmo) throw new Error("bancada: o ritmo do apoio so muda com o apoio ligado");
  const tabela = ap ? tabelaDoRitmo(c.apoio.ritmo) : undefined;
  return {
    ...(ap ? { apoio: { dano: c.apoio.dano, recarga: c.apoio.recarga, longeMs: c.apoio.longeMs } } : {}),
    ...(ar ? { arenaPorEstagio: { Ultimate: c.arena.Ultimate, Mega: c.arena.Mega } } : {}),
    ...(tabela ? { tabela } : {}),
  };
}
const TABELAS_RITMO = new Map<number, TabelaFormas>();
/** a tabela das formas com o clipe do apoio a `ritmo` vezes o do golpe (a regra do tools/gerar_tabela_arena.py: o instante do golpe e o clipe
    vezes o ritmo; o resto igual). No ritmo do git (0,6), undefined: a tabela do git. O teste confere que a regra refaz a tabela do git */
export function tabelaDoRitmo(ritmo: number): TabelaFormas | undefined {
  if (ritmo === APOIO_TABELA.ritmo) return undefined;
  if (!(Number.isFinite(ritmo) && ritmo >= .2 && ritmo <= 1.5)) throw new Error(`bancada: ritmo do apoio fora da faixa (${ritmo})`);
  let t = TABELAS_RITMO.get(ritmo);
  if (!t) { t = Object.freeze(refazerApoio(FORMAS_ARENA, ritmo)); TABELAS_RITMO.set(ritmo, t); }
  return t;
}
export function refazerApoio(base: TabelaFormas, ritmo: number): Record<string, DadosForma> {
  return Object.fromEntries(Object.entries(base).map(([k, f]) => {
    if (!f.apoio || typeof f.msApoio !== "number") throw new Error(`bancada: a forma ${k} nao tem o apoio na tabela`);
    return [k, { ...f, apoio: { ...f.apoio, t: f.golpe.t * ritmo }, msApoio: Math.round(f.msGolpe * ritmo) }];
  }));
}
/** o tiro do candidato e o da POC? (entao a luta nao leva o `tiro` na entrada, e sai a de sempre, byte a byte) */
export const tiroDaPoc = (t: TiroPoc): boolean => (Object.keys(TIRO_POC_V21) as (keyof TiroPoc)[]).every(k => t[k] === TIRO_POC_V21[k]);
const ehEstagioLuta = (e: string): e is EstagioLuta => (ESTAGIOS_LUTA as readonly string[]).includes(e);

/** os numeros da luta de 6 stats pelo candidato (a mesma conta do statsDaLuta, com os expoentes e os multiplicadores do candidato) */
export function statsLuta(c: Candidato, s: Stats, est: Estagio, condicao: number, atento = 0): StatsPoc {
  if (!ehEstagioLuta(est)) throw new Error(`bancada: o estagio ${est} nao luta`);
  for (const k of STATS) if (!(Number.isFinite(s[k]) && s[k] > 0)) throw new Error(`bancada: o stat ${k} precisa ser positivo (${s[k]})`);
  if (!(condicao > 0)) throw new Error(`bancada: condicao invalida (${condicao})`);
  const M = c.mapa, r = (k: Stat) => c.gama[k] === 1 ? s[k] / M.neutro : (s[k] / M.neutro) ** c.gama[k];
  return {
    hp: Math.max(1, Math.round(M.hp * r("vigor") * c.multVida[est] * condicao)),
    atk: M.atk * r("forca") * c.multAtk[est], def: M.def * r("guarda"), vel: M.vel * r("folego"),
    cad: M.cad / r("recuperacao"), hcd: M.hcd / r("recuperacao"),
    crit: M.crit * r("mira"), erro: M.erro / r("mira"),
    hpot: M.hpot, esquiva: M.esquiva, atordoa: M.atordoa,
    /* a perspicacia (a mira e o carater atento) e a agilidade (o folego), so com a esquiva ligada (D-LP5-14) */
    ...(c.esquiva.ligada ? { perc: Math.max(.1, (s.mira / M.neutro) ** c.esquiva.gamaMira * (1 + c.esquiva.kAtento * atento)), agil: (s.folego / M.neutro) ** c.esquiva.gamaFolego } : {}),
  };
}
const somaPontos = (b: Stats, pontos: Stats | null, peso: number): Stats =>
  pontos ? Object.fromEntries(STATS.map(k => [k, b[k] + peso * pontos[k]])) as Stats : b;
/** o carater do rival de perfil canonico: o canonico da forma adulta; nenhum antes */
export const caraterRival = (f: Forma): Partial<Carater> | null => f.adulta ? caraterCanonico(f.adulta as FormaAdultaNormal) : null;
/** um lutador de uma forma, com carater, pontos e condicao */
export function lutador(c: Candidato, f: Forma, car: Partial<Carater> | null, pontos: Stats | null, condicao = 1): StatsPoc {
  return statsLuta(c, somaPontos(statsDe(f, car), pontos, c.pesoPonto), f.est, condicao, car?.atento ?? 0);
}
/** o rival canonico (a Arena, os torneios): a forma pela chave da tabela, sem treino ou com o treino do lugar */
export function rivalCanonico(c: Candidato, chave: string, treino = 0): StatsPoc {
  const f = formaDaChave(chave);
  return lutador(c, f, caraterRival(f), treino ? pontosNoTotal(f.esp, treino) : null);
}
export function rivalDaForma(c: Candidato, f: Forma, car: Partial<Carater> | null, treino = 0, fator = 1): StatsPoc {
  if (fator === 1) return lutador(c, f, car, treino ? pontosNoTotal(f.esp, treino) : null);
  if (!(Number.isFinite(fator) && fator > 0)) throw new Error(`bancada: o fator do rival precisa ser positivo (${fator})`);
  const s = somaPontos(statsDe(f, car), treino ? pontosNoTotal(f.esp, treino) : null, c.pesoPonto);
  return statsLuta(c, Object.fromEntries(STATS.map(k => [k, s[k] * fator])) as Stats, f.est, 1, car?.atento ?? 0);
}
/** o NPC pelo candidato: o total dividido pelos 6 stats (igual, ou pelos pesos do npcDivisao), no estagio do lugar dele */
export function npc(c: Candidato, k: string): StatsPoc {
  const n = NPC[k], total = c.npcTotal[k];
  if (!n || total === undefined) throw new Error(`bancada: ${k} nao e um NPC da campanha v6`);
  const v = total / STATS.length, w = c.npcDivisao[k];
  return statsLuta(c, Object.fromEntries(STATS.map(s => [s, v * (w ? w[s] : 1)])) as Stats, n.est, 1);
}
/** confere uma divisao de NPC: os 6 stats, cada peso positivo, a soma 6 (o total nao muda) */
export function conferirDivisao(k: string, w: Record<string, unknown>): void {
  const ks = Object.keys(w);
  if (ks.length !== STATS.length || !STATS.every(s => s in w)) throw new Error(`bancada: a divisao de ${k} precisa dos 6 stats (${ks.join(", ")})`);
  for (const s of STATS) { const x = w[s]; if (typeof x !== "number" || !Number.isFinite(x) || !(x > 0)) throw new Error(`bancada: a divisao de ${k}.${s} invalida (${String(x)})`); }
  const soma = STATS.reduce((a, s) => a + (w[s] as number), 0);
  if (Math.abs(soma - STATS.length) > 1e-9) throw new Error(`bancada: a divisao de ${k} soma ${soma}, nao ${STATS.length}`);
}

/* ---------------------------------------------------------------- o treino tipico (D-LP5-2) */
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];
const ESTAGIOS_TREINO: readonly EstagioLuta[] = ESTAGIOS_LUTA;
/** a trajetoria do dono tipico de uma especie: os pontos depois de cada sessao, do Rookie ao Mega, ate nao ganhar mais nada */
function trajetoria(esp: Especie): Stats[] {
  const t = new TreinoPet(esp), out: Stats[] = [{ ...t.pontos }];
  let tick = t.tick, ex = 0;
  for (const est of ESTAGIOS_TREINO) {
    tick += 1; t.avancar(tick, false, true, est);
    for (let parado = 0; parado < EXERCICIOS.length; ) {
      while (t.pedePausa || !t.podeTocar(tick)) { tick += CTR.intervalo; t.avancar(tick, false, true, est); }
      const antes = t.total;
      t.sessao(tick, EXERCICIOS[ex % EXERCICIOS.length], true); ex++;
      if (t.total > antes + 1e-12) { out.push({ ...t.pontos }); parado = 0; } else parado++;
    }
  }
  return out;
}
const TRAJ = new Map<Especie, Stats[]>();
const trajDe = (esp: Especie): Stats[] => { let x = TRAJ.get(esp); if (!x) { x = trajetoria(esp); TRAJ.set(esp, x); } return x; };
const totalDe = (p: Stats): number => STATS.reduce((a, k) => a + p[k], 0);
/** os pontos do dono tipico da especie com o total n (exato; a ultima sessao interpolada). Falha alto acima do que o treino da */
export function pontosNoTotal(esp: Especie, n: number): Stats {
  const tr = trajDe(esp);
  if (n < 0 || n > totalDe(tr[tr.length - 1]) + 1e-9) throw new Error(`bancada: o treino da ${esp} nao chega a ${n} pontos (teto ${totalDe(tr[tr.length - 1])})`);
  if (n === 0) return Object.fromEntries(STATS.map(k => [k, 0])) as Stats;
  let i = tr.findIndex(p => totalDe(p) >= n - 1e-12);
  const a = tr[i - 1], b = tr[i], ta = totalDe(a), tb = totalDe(b), w = tb === ta ? 1 : (n - ta) / (tb - ta);
  return Object.fromEntries(STATS.map(k => [k, a[k] + w * (b[k] - a[k])])) as Stats;
}
/** o treino tipico de cada estagio (o CIT.tipico) e o teto acumulado do treino ate o estagio (CTR e CMG) */
export const TIPICO: Readonly<Record<EstagioLuta, number>> = { crianca: CIT.tipico.crianca!, adolescente: CIT.tipico.adolescente!, adulto: CIT.tipico.adulto!, mega: CIT.tipico.mega! };
export const TETO: Readonly<Record<EstagioLuta, number>> = (() => {
  const a = CTR.tetoEstagio.crianca, b = a + CTR.tetoEstagio.adolescente, c = Math.min(CTR.tetoVida, b + CTR.tetoEstagio.adulto);
  return { crianca: a, adolescente: b, adulto: c, mega: Math.min(CMG.tetoVida, c + CMG.tetoEstagio) };
})();
/** um so stat com n pontos (o T2) */
export const pontosNumStat = (st: Stat, n: number): Stats => Object.fromEntries(STATS.map(k => [k, k === st ? n : 0])) as Stats;

/* ---------------------------------------------------------------- os pets (D-LP5-2; desvio D-LP5-0-1) */
/** o pet i da base no estagio: uma forma do jogo daquele nivel (as da Arena), sorteada pela semente do pet, com o carater canonico dela.
    A vida do Motor com um dono simulado so da uma forma por estagio (a sonda formas_do_motor.ts): o sorteio cobre todas as formas e as 4
    especies, que o V1, o V2 e o P1 pedem */
export interface PetBancada { base: number; i: number; semente: number; est: EstagioLuta; chave: string; forma: Forma; especie: Especie; carater: Partial<Carater> | null }
export function petDoEstagio(base: number, i: number, est: EstagioLuta): PetBancada {
  const semente = hashSemente("equilibrio-poc-pet", base, i), rv = rivaisArena(est);
  if (!rv.length) throw new Error(`bancada: o ${est} nao tem formas`);
  const chave = rv[criarRng(hashSemente(semente, "forma", est)).int(rv.length)], forma = formaDaChave(chave);
  return { base, i, semente, est, chave, forma, especie: forma.esp, carater: caraterRival(forma) };
}
/** o lutador do pet com n pontos do dono tipico da especie (condicao 1: o pet bem cuidado) */
export const lutadorDoPet = (c: Candidato, p: PetBancada, n: number): StatsPoc => lutador(c, p.forma, p.carater, n ? pontosNoTotal(p.especie, n) : null);

/* ---------------------------------------------------------------- as lutas e as contas */
export const sementeLuta = (base: number, k: number): number => hashSemente("equilibrio-poc", base, k);
export interface Lado { forma: string; stats: StatsPoc; vida0?: number }
export interface Luta1 { vencedor: "a" | "b" | null; fim: boolean; relogio: number; vidaA: number }
export function lutar(cena: IdCena, semente: number, a: Lado, b: Lado, tiro?: TiroPoc, esquiva?: EsquivaPoc, lp6: ExtrasLp6 = {}): Luta1 {
  const r = lutarNucleoPoc({ cena, semente, a, b, ...(tiro && !tiroDaPoc(tiro) ? { tiro } : {}), ...(esquiva ? { esquiva } : {}),
    ...(lp6.apoio ? { apoio: lp6.apoio } : {}), ...(lp6.arenaPorEstagio ? { arenaPorEstagio: lp6.arenaPorEstagio } : {}) }, sorteiosPoc(semente), lp6.tabela);
  return { vencedor: r.vencedor, fim: r.fim, relogio: r.relogio, vidaA: r.vidaA };
}
/** um contador de vitorias, empates, lutas sem fim e o relogio (histograma em 100 ms) */
export interface Conta { n: number; v: number; e: number; sem_fim: number; relogio: Record<string, number> }
export const novaConta = (): Conta => ({ n: 0, v: 0, e: 0, sem_fim: 0, relogio: {} });
export function contar(c: Conta, r: Luta1): void {
  c.n++; if (r.vencedor === "a") c.v++; else if (r.vencedor === null) c.e++;
  if (!r.fim && r.relogio >= LIMITE_POC_MS) c.sem_fim++;
  const b = String(Math.floor(r.relogio / 100)); c.relogio[b] = (c.relogio[b] ?? 0) + 1;
}
export function juntar(a: Conta, b: Conta): Conta {
  const out: Conta = { n: a.n + b.n, v: a.v + b.v, e: a.e + b.e, sem_fim: a.sem_fim + b.sem_fim, relogio: { ...a.relogio } };
  for (const [k, x] of Object.entries(b.relogio)) out.relogio[k] = (out.relogio[k] ?? 0) + x;
  return out;
}
/** o quantil q do relogio (s), pelo histograma (o meio do bin) */
export function quantil(h: Record<string, number>, q: number): number {
  const ks = Object.keys(h).map(Number).sort((x, y) => x - y), n = ks.reduce((a, k) => a + h[k], 0);
  if (!n) throw new Error("bancada: quantil de histograma vazio");
  let acc = 0;
  for (const k of ks) { acc += h[k]; if (acc >= q * n) return (k + 0.5) / 10; }
  return (ks[ks.length - 1] + 0.5) / 10;
}
/** o intervalo de Wilson a 95 % (so para leitura; os criterios sao sobre a estimativa pontual, secao 2) */
export function wilson(v: number, n: number): [number, number] {
  if (!n) return [0, 1];
  const z = 1.959963984540054, p = v / n, d = 1 + z * z / n, c = p + z * z / (2 * n), m = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
  return [(c - m) / d, (c + m) / d];
}
export const taxa = (c: Conta): number => { if (!c.n) throw new Error("bancada: taxa sem lutas"); return c.v / c.n; };
/** as formas da tabela que atiram (com projetil no golpe) e as de perto, de um nivel */
export const atira = (chave: string): boolean => { const d = FORMAS_ARENA[chave]; if (!d) throw new Error(`bancada: ${chave} nao esta na tabela`); return !!d.golpe.proj; };

/* ---------------------------------------------------------------- o artefato */
export function commitAtual(): string {
  const aqui = fileURLToPath(new URL(".", import.meta.url));
  const sha = execSync("git rev-parse HEAD", { encoding: "utf-8", cwd: aqui }).trim();
  const sujo = execSync("git status --porcelain -- . ../../motor", { encoding: "utf-8", cwd: aqui }).trim();
  return sujo ? `${sha}+sujo` : sha;
}
export function argumento(nome: string, padrao?: string): string {
  const i = process.argv.indexOf(`--${nome}`), x = i >= 0 ? process.argv[i + 1] : process.argv.find(a => a.startsWith(`--${nome}=`))?.split("=")[1];
  if (x === undefined) { if (padrao === undefined) throw new Error(`bancada: falta --${nome}`); return padrao; }
  return x;
}
export { ESTAGIOS_TREINO };
