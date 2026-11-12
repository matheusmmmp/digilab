/* EQUILIBRIO_CUIDADO, E0: o retrato de hoje (docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md, registrado antes de qualquer vida). Uma vida
   = (versao, dono, semente): o ovo de um pet (VERSAO_PET) ou o grupo do ovo do brasao (VERSAO_GRUPO), montado como o jogo monta
   (src/produto.ts, src/cerebro.ts: as tres chaves do produto, o DigiBrain modular e a ponte da luta), no ritmo "rapida", com um dos tres
   donos roteirizados do EQ-4 (secao 2 do plano), do ovo ate o fim do 3o dia. So le o motor: nenhum numero do jogo muda.

     node scripts/equilibrio_cuidado/e0.ts --versao pet|grupo --dono atento|medio|relapso --semente S [--dias 3] [--saida arquivo.json]

   Sem --saida, grava em scripts/medicoes/equilibrio_cuidado_e0/<versao>_<dono>_<semente>.json. A semente da run sai da faixa de
   calibracao (93101...93505): a bancada falha alto com outra, salvo --teste (as sementes de teste, 101...505). */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import {
  ACAO_CHAMADO, CHAMADO_BEBE, CHAMADO_BEBE_CORPO, CUIDADO_NA_HORA, NOME_ESTAGIO_FALA, TICK_INICIAL, TPD, VERSAO_GRUPO, VERSAO_PET,
  GrupoDoJogo, Motor, type AcaoDono, type Chamado, type Estagio,
} from "../../motor/index.ts";
import { CONFIG_LANCE_DONO_LIGADA } from "../../motor/digibrain/constantes.ts";
import type { MotorCorpoMundo } from "../../motor/motor_corpo_mundo.ts";
import { BITS, feitosDoPet, type TabelaBits } from "../../src/bits.ts";
import { ajusteE1Ligado, type AjusteEquilibrioE1 } from "../../motor/equilibrio_e1.ts";
import { marcosDoPet } from "../../src/nivel.ts";

export const DONOS = ["atento", "medio", "relapso"] as const;
export type NomeDono = typeof DONOS[number];
export const VERSOES = ["pet", "grupo"] as const;
export type NomeVersao = typeof VERSOES[number];
/** as 5 sementes da calibracao usadas no E0 (secao 5 do plano); a validacao (94101...94505) nao e tocada */
export const SEMENTES_E0 = [93101, 93202, 93303, 93404, 93505] as const;
export const FAIXA_CALIBRACAO = [93101, 93505] as const;
/** a faixa da validacao unica (o E2; adendo 1 do plano de analise): so no modo de validacao, que recusa as sementes da calibracao */
export const FAIXA_VALIDACAO = [94101, 94505] as const;
/** a visita do medio e do relapso, em minutos de jogo (EQ-4) */
export const VISITA: Record<NomeDono, number | null> = { atento: null, medio: 120, relapso: 360 };
/** o preco do portao ★★ (docs/PLANO_V3_MOEDA.md, secao 3; PROPOSTO, SEM FONTE) */
export const PRECO_PORTAO_2 = 150;
const CHAMADOS: readonly Chamado[] = ["fome", "higiene", "carinho"];

/** o limiar do estagio (secao 2 do plano): o do chamado do bebe no In-Training, o do cuidado na hora certa do Rookie em diante */
const limiarDe = (est: Estagio): Record<Chamado, number> => est === "bebe" ? CHAMADO_BEBE_CORPO : CUIDADO_NA_HORA;
const valorDe = (m: Motor): Record<Chamado, number> => ({ fome: m.e.fome, higiene: m.e.higiene, carinho: m.e.humor });
/** a acao de cada falta: o carinho e o brincar (o lance) com o pet acordado, o carinho com ele dormindo */
const acaoDe = (c: Chamado, m: Motor): AcaoDono => c === "carinho" ? (m.e.dormindo ? "acariciar" : "brincar") : ACAO_CHAMADO[c][0]!;

/** a celula (estagio, dia) de um tick do pet */
export interface Celula { estagio: string; dia: number }
const chaveCelula = (c: Celula): string => `${c.estagio}|${c.dia}`;

interface Conta {
  minutos: number; fome_025: number; fome_045: number; postas: number; comidas: number; comidas_por_ele: number;
  cochilos: number; energia_ao_acordar: number[]; decisoes: number; explorar: number; brincar: number;
  lances: number; chutes: number; acoes_dono: Record<string, number>;
}
const novaConta = (): Conta => ({ minutos: 0, fome_025: 0, fome_045: 0, postas: 0, comidas: 0, comidas_por_ele: 0, cochilos: 0,
  energia_ao_acordar: [], decisoes: 0, explorar: 0, brincar: 0, lances: 0, chutes: 0, acoes_dono: {} });

/** o estagio do pet num tick do pet (pela lista das evolucoes) */
function estagioNoTick(m: Motor, tick: number): Estagio {
  let est: Estagio = "bebe";
  for (const ev of m.evolucoes) if (ev.tick <= tick) est = ev.estagio;
  return est;
}
const celulaDe = (m: Motor, tick: number): Celula =>
  ({ estagio: NOME_ESTAGIO_FALA[estagioNoTick(m, tick)], dia: Math.floor((tick - TICK_INICIAL) / TPD) + 1 });

/** o estado do dono de um pet: o ultimo tick de cada tipo de acao (o espacamento do atento do Rookie em diante) e os Brincar dados */
interface EstadoDono { ultimo: Partial<Record<Chamado, number>>; brincos: number[]; acoes: [number, AcaoDono][] }

/** o dono age no pet antes do avanco do tick t (t = minutos desde o ovo); `agir` faz a acao pelo caminho certo (o Motor ou o g.agir) */
function vezDoDono(dono: NomeDono, m: Motor, t: number, st: EstadoDono, agir: (a: AcaoDono) => void): void {
  const fazer = (a: AcaoDono): void => { agir(a); st.acoes.push([m.e.tick, a]); if (a === "brincar") st.brincos.push(m.e.tick); };
  const est = m.estagioAtual;
  if (dono === "atento") {
    if (est === "bebe") {
      for (const c of m.chamadosAbertos()) fazer(acaoDe(c, m));   // o tick em que o chamado aparece: depois de atendido, ele fecha
      return;
    }
    const lim = limiarDe(est), v = valorDe(m);
    for (const c of CHAMADOS) {
      const u = st.ultimo[c];
      if (v[c] < lim[c] && (u === undefined || m.e.tick - u >= CHAMADO_BEBE[c])) { st.ultimo[c] = m.e.tick; fazer(acaoDe(c, m)); }
    }
    return;
  }
  const visita = VISITA[dono]!;
  if (t === 0 || t % visita !== 0) return;
  const lim = limiarDe(est), v = valorDe(m);
  for (const c of CHAMADOS) if (v[c] < lim[c]) fazer(acaoDe(c, m));
}

const mediana = (xs: number[]): number | null => {
  if (!xs.length) return null;
  const o = [...xs].sort((a, b) => a - b), n = o.length;
  return n % 2 ? o[(n - 1) / 2]! : (o[n / 2 - 1]! + o[n / 2]!) / 2;
};
const r4 = (x: number | null): number | null => x === null ? null : Math.round(x * 1e4) / 1e4;

/** as chaves do E1 (EQUILIBRIO_CUIDADO; scripts/equilibrio_cuidado/e1.ts): o ajuste do modular e a tabela dos Bits. Sem elas, a vida do E0,
    byte a byte. `validacao`: o modo da validacao unica (o E2), o unico que aceita as sementes 94101...94505 */
export interface OpcoesVida { ajuste?: AjusteEquilibrioE1; bits?: TabelaBits; validacao?: boolean }

/** a vida inteira: o resultado por pet e o do Tamer */
export function vida(versao: NomeVersao, dono: NomeDono, semente: number, dias = 3, teste = false, opcoes: OpcoesVida = {}) {
  const tabela = opcoes.bits ?? BITS, ajuste = opcoes.ajuste;
  if (!DONOS.includes(dono)) throw new Error(`dono desconhecido: ${JSON.stringify(dono)}`);
  if (!VERSOES.includes(versao)) throw new Error(`versao desconhecida: ${JSON.stringify(versao)}`);
  if (!Number.isInteger(dias) || dias < 1) throw new Error(`dias precisa ser inteiro >= 1: ${dias}`);
  if (opcoes.validacao !== undefined && typeof opcoes.validacao !== "boolean") throw new Error(`validacao e bool: ${String(opcoes.validacao)}`);
  if (opcoes.validacao === true) {
    if (teste) throw new Error("o modo de validacao nao roda com as sementes de teste");
    if (!(semente >= FAIXA_VALIDACAO[0] && semente <= FAIXA_VALIDACAO[1])) throw new Error(`semente ${semente} fora da faixa de validacao (94101...94505)`);
  } else if (teste ? !(semente >= 101 && semente <= 505) : !(semente >= FAIXA_CALIBRACAO[0] && semente <= FAIXA_CALIBRACAO[1]))
    throw new Error(`semente ${semente} fora da faixa ${teste ? "de teste (101...505)" : "de calibracao (93101...93505)"}`);
  /* a montagem do jogo (src/produto.ts e src/cerebro.ts): as tres chaves, o modular e a ponte da luta, na ordem do ligarProduto */
  const montar = (m: Motor): void => {
    if (ajuste !== undefined && ajusteE1Ligado(ajuste)) m.ligarEquilibrioE1(ajuste);   // o E1: antes da troca para o modular
    m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
    m.trocarCerebro("modular");
    m.ligarPonteLuta(true);
  };
  let pets: [string, Motor][], avancar: () => void, agirEm: (id: string, a: AcaoDono) => void, numero: number;
  if (versao === "pet") {
    const m = new Motor(semente, VERSAO_PET);
    montar(m);
    pets = [["pet", m]]; numero = VERSAO_PET;
    avancar = () => m.avancar(1);
    agirEm = (_id, a) => m.observar(a);
  } else {
    const g = new GrupoDoJogo(semente, VERSAO_GRUPO);
    for (const i of g.ids) g.agir(i, montar);
    pets = g.ids.map(i => [i, g.motor(i)] as [string, Motor]); numero = VERSAO_GRUPO;
    avancar = () => g.avancar(1);
    agirEm = (id, a) => g.agir(id, x => x.observar(a));
  }
  for (const [, m] of pets) if (m.cerebroAtual !== "modular") throw new Error("o pet nao decide com o modular");

  const contas = Object.fromEntries(pets.map(([i]) => [i, new Map<string, Conta>()]));
  const conta = (i: string, c: Celula): Conta => { const mp = contas[i]!, k = chaveCelula(c); if (!mp.has(k)) mp.set(k, novaConta()); return mp.get(k)!; };
  const donos = Object.fromEntries(pets.map(([i]) => [i, { ultimo: {}, brincos: [], acoes: [] } as EstadoDono]));
  const saude = Object.fromEntries(pets.map(([i]) => [i, [] as { dia: number; saude: number }[]]));
  const marcos = new Map<number, number>();   // o marco do Tamer -> o tick do pet em que apareceu pela primeira vez
  const antes = Object.fromEntries(pets.map(([i, m]) => [i, { dormindo: m.e.dormindo, energia: m.e.energia }]));
  const prontoChampion: Record<string, number | null> = Object.fromEntries(pets.map(([i]) => [i, null]));
  for (const [, m] of pets) for (const n of marcosDoPet(m)) if (!marcos.has(n)) marcos.set(n, m.e.tick);   // o marco 1: chocou
  const T = dias * TPD;
  for (let t = 0; t < T; t++) {
    for (const [i, m] of pets) {
      if (m.morte !== null) throw new Error(`o pet ${i} morreu no tick ${m.morte.tick} (${m.morte.causa}): sem luta, nao devia`);
      vezDoDono(dono, m, t, donos[i]!, a => agirEm(i, a));
      const c = conta(i, celulaDe(m, m.e.tick));
      c.minutos++;
      if (m.e.fome < .25) c.fome_025++;
      if (m.e.fome < .45) c.fome_045++;
      antes[i] = { dormindo: m.e.dormindo, energia: m.e.energia };
    }
    avancar();
    for (const [i, m] of pets) {
      const a = antes[i]!, agora = m.e.dormindo, c = conta(i, celulaDe(m, m.e.tick - 1));
      if (agora && !a.dormindo) c.cochilos++;
      if (!agora && a.dormindo) c.energia_ao_acordar.push(a.energia);
      if ((t + 1) % TPD === 0) saude[i]!.push({ dia: (t + 1) / TPD, saude: r4(m.e.saude)! });
      if (prontoChampion[i] === null && m.estagioAtual === "crianca" && m.requisitosEvolucao()!.tempo) prontoChampion[i] = m.e.tick;
      for (const n of marcosDoPet(m)) if (!marcos.has(n)) marcos.set(n, m.e.tick);
    }
  }
  /* as decisoes, as racoes e os lances, lidos dos registros do laco e do mundo no fim da vida */
  const consumidas = new Map<number, string>();
  for (const [i, m] of pets) for (const r of m.mundo!.consumos) consumidas.set(r["id"] as number, i);
  const janela = CONFIG_LANCE_DONO_LIGADA.janela_convite_ticks;
  const porPet = pets.map(([i, m]) => {
    const laco = m.v11!.laco as MotorCorpoMundo, mundo = m.mundo!;
    for (const [tk, ac] of laco.acoesPet) {
      if (tk - TICK_INICIAL >= T) continue;
      const c = conta(i, celulaDe(m, tk));
      c.decisoes++;
      if (ac === "explorar") c.explorar++;
      if (ac === "brincar") c.brincar++;
    }
    for (const d of mundo.deixadas) {
      if (d["tipo"] !== "racao") continue;
      const tk = (d["tick"] as number) - mundo.entrada, c = conta(i, celulaDe(m, tk));
      c.postas++;
      const quem = consumidas.get(d["id"] as number);
      if (quem !== undefined) { c.comidas++; if (quem === i) c.comidas_por_ele++; }
    }
    const rol = mundo.rolagens.map(r => r["tick"] as number);
    for (const tk of donos[i]!.brincos) {
      const c = conta(i, celulaDe(m, tk)), tm = tk + mundo.entrada;
      c.lances++;
      c.chutes += rol.filter(r => tm <= r && r < tm + janela).length;
    }
    for (const [tk, a] of donos[i]!.acoes) { const c = conta(i, celulaDe(m, tk)); c.acoes_dono[a] = (c.acoes_dono[a] ?? 0) + 1; }
    const nLances = mundo.lances === null ? null : mundo.lances.length;
    const feitos = feitosDoPet(m, tabela).filter(f => f.tick - TICK_INICIAL < T);
    const celulas = [...contas[i]!.entries()].map(([k, c]) => {
      const [estagio, dia] = k.split("|");
      const { energia_ao_acordar, ...resto } = c;
      return { estagio, dia: Number(dia), ...resto, energia_mediana_ao_acordar: r4(mediana(energia_ao_acordar)), acordou: energia_ao_acordar.length };
    }).sort((a, b) => a.dia - b.dia || (a.estagio === "In-Training" ? -1 : 1));
    return {
      ident: i, semente_pet: m.semente, especie: m.especie, estagio_final: NOME_ESTAGIO_FALA[m.estagioAtual],
      evolucoes: m.evolucoes.map(e => ({ tick: e.tick, estagio: NOME_ESTAGIO_FALA[e.estagio] })),
      pronto_champion_pelo_tempo: prontoChampion[i], morte: m.morte, saude_fim_do_dia: saude[i], celulas,
      lances_no_mundo: nLances, feitos_bits: feitos,
    };
  });
  /* os Bits do Tamer: os feitos dos pets e os niveis (30 por marco, uma vez por Tamer) */
  const bits: { tick: number; valor: number; origem: string }[] = [];
  for (const p of porPet) for (const f of p.feitos_bits) bits.push({ tick: f.tick, valor: f.valor, origem: f.origem });
  for (const [n, tk] of marcos) if (tk - TICK_INICIAL < T) bits.push({ tick: tk, valor: tabela.nivel, origem: `nivel:${n}` });
  bits.sort((a, b) => a.tick - b.tick);
  let soma = 0, tick150: number | null = null;
  const porDia: Record<string, number> = {}, porOrigem: Record<string, number> = {};
  for (const b of bits) {
    soma += b.valor;
    if (tick150 === null && soma >= PRECO_PORTAO_2) tick150 = b.tick;
    const d = String(Math.floor((b.tick - TICK_INICIAL) / TPD) + 1);
    porDia[d] = (porDia[d] ?? 0) + b.valor;
    const o = b.origem.startsWith("nivel") ? "nivel" : b.origem;
    porOrigem[o] = (porOrigem[o] ?? 0) + b.valor;
  }
  const pronto = porPet.map(p => p.pronto_champion_pelo_tempo).filter((x): x is number => x !== null);
  return {
    versao, numero_versao: numero, dono, semente, dias, ritmo: "rapida",
    pets: porPet,
    tamer: {
      bits_total: soma, bits_por_dia: porDia, bits_por_origem: porOrigem, marcos: Object.fromEntries(marcos),
      tick_150: tick150, dia_150: tick150 === null ? null : Math.floor((tick150 - TICK_INICIAL) / TPD) + 1,
      tick_pronto_champion: pronto.length ? Math.min(...pronto) : null,
      ha_150_antes_do_champion: tick150 !== null && pronto.length > 0 ? tick150 <= Math.min(...pronto) : null,
    },
  };
}

export const PASTA_E0 = fileURLToPath(new URL("../medicoes/equilibrio_cuidado_e0/", import.meta.url));

function argumento(nome: string, padrao?: string): string {
  const i = process.argv.indexOf(`--${nome}`);
  if (i < 0) { if (padrao === undefined) throw new Error(`falta --${nome}`); return padrao; }
  const v = process.argv[i + 1];
  if (v === undefined || v.startsWith("--")) throw new Error(`--${nome} sem valor`);
  return v;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const versao = argumento("versao") as NomeVersao, dono = argumento("dono") as NomeDono, semente = Number(argumento("semente"));
  const dias = Number(argumento("dias", "3")), teste = process.argv.includes("--teste");
  const saida = argumento("saida", `${PASTA_E0}${versao}_${dono}_${semente}.json`);
  const t0 = Date.now(), r = vida(versao, dono, semente, dias, teste);
  mkdirSync(dirname(saida), { recursive: true });
  writeFileSync(saida, JSON.stringify(r, null, 1) + "\n");
  console.log(`${versao} ${dono} ${semente}: ${((Date.now() - t0) / 1000).toFixed(1)} s -> ${saida}`);
}
