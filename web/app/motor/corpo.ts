/* O corpo do Creatures 3 por baixo dos drives em TS (docs/TAREFA_V2_CORPO_DRIVES.md, etapa 7 da secao 14): o porte de digilab/corpo.py
   e de digilab/corpo_grafo.py, so o motor e a paridade; nenhuma tela e nenhuma versao de pet nova.

   A quimica guarda a FALTA de cada drive em inteiros de [0, C] (C = 450000, CD-1); o drive de hoje e a leitura (C - q) / C. Por cima:
   o orgao 1, a digestao (o estomago `alimento` e a reacao que o passa para a fome), o orgao 2, a Vida (os receptores de estagio), os
   drives novos (tedio pela variedade, DS-4; curiosidade, so com o mundo fisico; solidao; estresse) e os gestos (o tapa, a dor, o susto
   e o medo da mao no carinho). O grafo do corpo (secao 18) e uma tabela unica, conferida na carga (`checarGrafo`, que falha alto).

   O metabolismo energetico (docs/TAREFA_V2_METABOLISMO.md, secao 3, etapa 4; sub-chave `metabolismo`, que exige a digestao): o
   `combustivel` e a `reserva`, concentracoes sem receptor (ME-2). A digestao poe no combustivel conversao_num/conversao_den do que
   digeriu, com o resto guardado; o gasto basal acordado e dormindo (fase 1); as atividades (o brincar do pet e o do dono, o explorar e o
   andar) tiram do combustivel div_arred(o que somam ao cansaco x gasto_atividades_num, gasto_atividades_den); o armazenamento e a
   mobilizacao (reacoes com limiar, transferencias 1 por 1 entre a fase 1 e a 2); e a falta, que abaixo de falta_limiar sobe o cansaco
   (fase 2, o gatilho `abaixo`), a unica ponte para o pet (ME-1). As contas (CONTAS_METABOLISMO) guardam o que entrou e saiu.

   So inteiros na quimica: a paridade com o Python e exata (test/corpo.test.ts contra tests/gabaritos/corpo_quimica_python.json). A conta
   e a do Python, linha a linha: div_arred (meio longe do zero, sem o -0 do JS; o de motor/mundo.ts), a meia-vida com o minimo de 1, a
   digestao com o descarte, o tick em fases, o tedio pela janela, o carinho vezes o medo da mao. Nenhum sorteio (o corpo nao tem rng: a
   sujeira e o sono vem do estado do pet, como no Python). Os registros usam os nomes em snake_case do Python de proposito. */
import { C, CCO, CCO_V11, DUR_EVO, LIMIAR_PRIVACAO, TPD, type ConfigCorpo, type ConfigMundo } from "./constantes.ts";
import { eNoite } from "./estado.ts";
import { divArred, TIPOS_COMIDA_MUNDO } from "./mundo.ts";
import type { AcaoPet } from "./tipos.ts";

// ================================================================== os nomes
export const QUIMICOS_HOJE = ["fome", "desconforto", "cansaco", "tristeza", "dano"] as const;
/** o drive de hoje lido de cada quimico de hoje (o nome do receptor) */
export const DRIVE_DO_QUIMICO: Readonly<Record<string, string>> = {
  fome: "fome", desconforto: "higiene", cansaco: "energia", tristeza: "humor", dano: "saude",
};
export const QUIMICOS_DA_PRIVACAO = ["fome", "desconforto", "cansaco"] as const;   // Estado.em_privacao: fome, higiene e energia
export const ORGAO_DIGESTAO = ["alimento"] as const;                                 // sem receptor para o cerebro (secao 5)
export const ORGAO_VIDA = ["vida"] as const;                                         // sem receptor para o cerebro (secao 6)
export const ESTAGIOS_CORPO = ["bebe", "crianca", "adolescente", "adulto"] as const; // os de treino_stats.estagio_no_tick, na ordem
export type EstagioCorpo = typeof ESTAGIOS_CORPO[number];
export const NOVOS_CORPO = ["tedio", "curiosidade", "solidao", "estresse"] as const; // etapa 6 (a curiosidade so com o mundo fisico)
export const GESTOS_CORPO = ["dor", "susto"] as const;                               // etapa 6, gestos
export const METABOLISMO_CORPO = ["combustivel", "reserva"] as const;                // o metabolismo; sem receptor (ME-2)
/** as contas do metabolismo, em totais desde o nascimento: o que entrou e saiu do combustivel e da reserva */
export const CONTAS_METABOLISMO = ["convertido", "descartado_teto", "mobilizado", "gasto_basal", "gasto_atividade", "armazenado"] as const;
export type ContaMetabolismo = typeof CONTAS_METABOLISMO[number];
export const DRIVES_DO_ESTRESSE = ["fome", "desconforto", "cansaco", "tedio", "curiosidade", "solidao", "dor"] as const;
export const ATIVIDADES_TEDIO = ["bola", "brincar", "explorar", "dono_brinca"] as const;   // DS-4
export type AtividadeTedio = typeof ATIVIDADES_TEDIO[number];
export const VALOR_TAPA = "tapa";                                                    // AcaoUsuario.TAPA do Python
/** as acoes do dono que o corpo conhece, na ordem do enum do Python (o tapa e o ultimo) */
export const ACOES_DONO_CORPO = ["alimentar", "limpar", "brincar", "acariciar", "elogiar", "repreender", "tapa"] as const;
export type AcaoDonoCorpo = typeof ACOES_DONO_CORPO[number];
type AcaoDonoHoje = Exclude<AcaoDonoCorpo, "tapa">;
/** a ordem das acoes do pet em corpo.taxas_de (a do dicionario do Python, que da a ordem dos emissores "pet:*") */
const ORDEM_PET: readonly AcaoPet[] = ["ocioso", "dormir", "chamar_atencao", "brincar", "explorar", "comer", "emburrar"];
const FRUTAS_MUNDO = ["a", "b", "c"] as const;
export const TOLERANCIA_GRADE = 1e-6;   // quanto um numero de hoje x C pode fugir de um inteiro (so erro de float)

const menos = (x: number): number => 0 - x;   // a negacao sem o -0 do JS

// ================================================================== a config
/** a ConfigCorpo do Python com `mudancas` por cima, conferida como no __post_init__ (falha alto) */
export function configCorpo(mudancas: Partial<ConfigCorpo> = {}): ConfigCorpo {
  const cc: ConfigCorpo = { ...CCO, ...mudancas };
  const ordem: [string, boolean][] = [["ligada", cc.ligada], ["digestao", cc.digestao], ["vida", cc.vida],
    ["drives_novos", cc.drives_novos], ["gestos", cc.gestos], ["banheiro", cc.banheiro]];
  for (let i = 1; i < ordem.length; i++) {
    if (ordem[i][1] && !ordem[i - 1][1]) throw new Error(`ConfigCorpo.${ordem[i][0]} exige ConfigCorpo.${ordem[i - 1][0]} (E-9: um orgao por vez)`);
  }
  if (cc.taxa_digestao <= 0) throw new Error(`ConfigCorpo.taxa_digestao tem de ser positiva: ${cc.taxa_digestao}`);
  if (cc.vida_decaimento <= 0) throw new Error(`ConfigCorpo.vida_decaimento tem de ser positivo: ${cc.vida_decaimento}`);
  const positivos = ["tedio_sobe", "curiosidade_sobe", "solidao_sobe", "estresse_limiar", "estresse_divisor", "janela_tedio",
    "tedio_bola", "tedio_brincar", "tedio_explorar", "tedio_dono", "curiosidade_novidade", "curiosidade_max_novidades",
    "janela_novidade", "carinho_solidao", "carinho_estresse", "tapa_dor", "tapa_susto", "tapa_estresse"] as const;
  for (const nome of positivos) {
    const v = cc[nome];
    if (!Number.isInteger(v) || v <= 0) throw new Error(`ConfigCorpo.${nome} tem de ser inteiro positivo: ${v}`);
  }
  if (cc.medo_da_mao !== 0 && cc.medo_da_mao !== 1) throw new Error(`ConfigCorpo.medo_da_mao e 0 (sem medo) ou 1: ${cc.medo_da_mao}`);
  // o metabolismo (docs/TAREFA_V2_METABOLISMO.md, secao 3): as conferencias do __post_init__ do Python
  if (typeof cc.metabolismo !== "boolean") throw new Error(`ConfigCorpo.metabolismo e bool: ${cc.metabolismo}`);
  if (cc.metabolismo && !cc.digestao) {
    throw new Error("ConfigCorpo.metabolismo exige ConfigCorpo.digestao (E-9: a comida digerida e o que vira combustivel)");
  }
  const positivosM = ["conversao_num", "conversao_den", "gasto_basal_acordado", "gasto_basal_dormindo", "armazenar_limiar",
    "armazenar_taxa", "mobilizar_limiar", "mobilizar_taxa", "falta_limiar", "falta_cansaco", "gasto_atividades_num",
    "gasto_atividades_den"] as const;
  for (const nome of positivosM) {
    const v = cc[nome];
    if (!Number.isInteger(v) || v <= 0) throw new Error(`ConfigCorpo.${nome} tem de ser inteiro positivo: ${v}`);
  }
  for (const nome of ["combustivel_inicial", "reserva_inicial"] as const) {
    const v = cc[nome];
    if (!Number.isInteger(v) || (cc.metabolismo && !(v >= 0 && v <= cc.escala))) throw new Error(`ConfigCorpo.${nome} tem de ser inteiro em [0, C]: ${v}`);
  }
  if (cc.metabolismo && !(cc.falta_limiar < cc.mobilizar_limiar && cc.mobilizar_limiar < cc.armazenar_limiar && cc.armazenar_limiar < cc.escala)) {
    throw new Error("o metabolismo pede falta_limiar < mobilizar_limiar < armazenar_limiar < C: "
      + `${cc.falta_limiar}, ${cc.mobilizar_limiar}, ${cc.armazenar_limiar}`);
  }
  // o Paladar (docs/futuro/paladar.md) ainda nao tem orgao em TS (a etapa 5 do paladar): ligado, falha alto
  if (cc.paladar) throw new Error("ConfigCorpo.paladar ainda nao existe no TS (paladar, etapa 5)");
  // o banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 3): a vontade, o conforto e as necessidades na zona ainda nao tem quimica em TS (a
  // etapa 4 do banheiro); ligado, o corpo sairia sem eles em silencio (o achado do #333). Sem os gestos, a ordem acima falha antes (E-9)
  if (typeof cc.banheiro !== "boolean") throw new Error(`ConfigCorpo.banheiro e bool: ${cc.banheiro}`);
  if (cc.banheiro) throw new Error("ConfigCorpo.banheiro ainda nao existe no TS (banheiro, etapa 4)");
  return cc;
}
/** CONFIG_CORPO_LIGADA, CONFIG_CORPO_DRIVES e CONFIG_CORPO_METABOLISMO do Python */
export const CCO_LIGADA = configCorpo({ ligada: true });
export const CCO_DRIVES = configCorpo({ ligada: true, digestao: true, vida: true, drives_novos: true, gestos: true });
export const CCO_METABOLISMO = configCorpo({ ...CCO_DRIVES, metabolismo: true });
/** o corpo dos pets v11: o CCO_V11 (o ponto das vidas do v11 do gabarito) completado e conferido */
export const CCO_CORPO_V11 = configCorpo(CCO_V11);

/** os quimicos que o corpo tem com estas chaves: os cinco de hoje, os de cada orgao ligado e os da etapa 6 (a curiosidade so com o
 *  mundo fisico) */
export function quimicosDe(cc: ConfigCorpo, comMundo = false): string[] {
  const novos = cc.drives_novos ? NOVOS_CORPO.filter((n) => n !== "curiosidade" || comMundo) : [];
  return [...QUIMICOS_HOJE, ...(cc.digestao ? ORGAO_DIGESTAO : []), ...(cc.vida ? ORGAO_VIDA : []), ...novos,
    ...(cc.gestos ? GESTOS_CORPO : []), ...(cc.metabolismo ? METABOLISMO_CORPO : [])];
}

// ================================================================== inteiros
/** x * escala como inteiro exato. Um numero de hoje fora da grade falha alto (a CD-1 diz que nenhum fica fora). */
export function naGrade(x: number, escala: number, nome: string): number {
  const v = x * escala;
  const r = Math.round(v);
  if (Math.abs(v - r) > TOLERANCIA_GRADE) throw new Error(`${nome} = ${x} nao cai na grade de ${escala}: ${v}`);
  return r === 0 ? 0 : r;
}

/** a constante da meia-vida h (secao 3): arred(2**bits * (1 - 2**(-1/h))). So para derivar e conferir; o tick nunca a chama */
export function kMeiaVida(h: number, bits = 16): number {
  if (h <= 0) throw new Error(`meia-vida nao positiva: ${h}`);
  return Math.floor(2 ** bits * (1 - 2 ** (-1 / h)) + 0.5);
}

/** um tick de decaimento (secao 3): q - max(1, div_arred(q k, 2**bits)) enquanto q > 0 */
export function passoMeiaVida(q: number, k: number, bits = 16): number {
  if (q <= 0) return 0;
  return Math.max(0, q - Math.max(1, divArred(q * k, 2 ** bits)));
}

// ================================================================== taxas
/** os numeros de hoje na escala C, com o sinal da falta (positivo = o drive piora). `dono` e `pet`: acao -> {quimico: delta} */
export interface TaxasCorpo {
  fome_por_tick: number; desconforto_por_tick: number; desconforto_por_sujeira: number; tristeza_por_tick: number;
  cansaco_acordado: number; cansaco_noite: number; cansaco_dormindo: number; dano_privacao: number; dano_cura: number;
  limiar_privacao: number;
  dono: Record<AcaoDonoHoje, Record<string, number>>;
  pet: Record<AcaoPet, Record<string, number>>;
}

/** corpo.gasto_da_atividade: o que uma atividade tira do combustivel, div_arred(o cansaco dela x gasto_atividades_num,
 *  gasto_atividades_den). Com o fator 1/1, o mesmo numero (ME-3). Um gasto que arredonda a zero falha alto. */
export function gastoDaAtividade(cc: ConfigCorpo, cansaco: number): number {
  if (cansaco <= 0) throw new Error(`atividade sem cansaco: ${cansaco}`);
  const g = divArred(cansaco * cc.gasto_atividades_num, cc.gasto_atividades_den);
  if (g <= 0) throw new Error(`o fator do gasto das atividades zera o gasto de ${cansaco}: ${cc.gasto_atividades_num}/${cc.gasto_atividades_den}`);
  return g;
}

/** corpo.taxas_de: a Config de hoje (C, o espelho de config.Config) na escala da ConfigCorpo */
export function taxasDe(cc: ConfigCorpo): TaxasCorpo {
  const E = cc.escala;
  const g = (x: number, nome: string): number => naGrade(x, E, nome);
  const dono: Record<AcaoDonoHoje, Record<string, number>> = {
    alimentar: { fome: menos(g(C.ganhoAlim, "ganho_alimentar")) },
    limpar: { desconforto: menos(g(C.ganhoLimpar, "ganho_limpar")) },
    brincar: { tristeza: menos(g(C.ganhoBrincHum, "ganho_brincar_humor")), cansaco: g(C.custoBrincEn, "custo_brincar_energia"),
      fome: g(C.custoBrincFome, "custo_brincar_fome") },
    acariciar: { tristeza: menos(g(C.ganhoElogiar * 0.6, "ganho_elogiar * 0.6")) },
    elogiar: { tristeza: menos(g(C.ganhoElogiar, "ganho_elogiar")) },
    repreender: { tristeza: g(C.custoRepr, "custo_repreender") },
  };
  const efeitos: Record<AcaoPet, Record<string, number>> = {
    ocioso: {}, dormir: {}, chamar_atencao: {},
    brincar: { tristeza: menos(g(C.humBrinc * C.intervalo, "humor do brincar")), cansaco: cc.pet_brincar_cansaco },
    explorar: { cansaco: cc.pet_explorar_cansaco, tristeza: cc.pet_explorar_tristeza },
    comer: { fome: cc.pet_comer_fome },
    emburrar: { tristeza: cc.pet_emburrar_tristeza },
  };
  const pet = Object.fromEntries(ORDEM_PET.map((a) => [a, efeitos[a]])) as Record<AcaoPet, Record<string, number>>;
  if (cc.metabolismo) {
    // ME-3: as atividades tiram do combustivel o que somam ao cansaco vezes o fator do gasto; o cansaco de hoje nao muda
    for (const ef of [pet.brincar, pet.explorar, dono.brincar]) ef.combustivel = menos(gastoDaAtividade(cc, ef.cansaco));
  }
  return {
    fome_por_tick: g(C.decFome, "decaimento_fome"),
    desconforto_por_tick: g(C.decHig, "decaimento_higiene"),
    desconforto_por_sujeira: g(C.decHig * C.penHigSuj, "penalidade_higiene_por_sujeira"),
    tristeza_por_tick: g(C.decHum, "decaimento_humor"),
    cansaco_acordado: g(C.decEn, "decaimento_energia"),
    cansaco_noite: g(C.decEn * C.multNoite, "decaimento_energia * multiplicador_noturno"),
    cansaco_dormindo: menos(g(C.enSono, "energia_por_tick_dormindo")),
    dano_privacao: g(C.danoSaude, "dano_saude_por_tick"),
    dano_cura: menos(g(C.curaSaude, "cura_saude_por_tick")),
    limiar_privacao: E - g(LIMIAR_PRIVACAO, "limiar_privacao"),
    dono,
    pet,
  };
}

// ================================================================== o grafo (secao 18; digilab/corpo_grafo.py)
export const GATILHOS_TICK = ["tick", "acordado", "dormindo", "noite_acordado", "dia_acordado", "sujeira", "privacao", "sem_privacao",
  "limiar", "abaixo"] as const;   // abaixo: o metabolismo, um quimico abaixo do limiar (fase 2)
export const LADOS_REACAO = ["acima", "abaixo"] as const;       // o lado do limiar de uma reacao com limiar (a transferencia)
export const GATILHOS = [...GATILHOS_TICK, "estimulo"] as const;
export const LEITURAS_RECEPTOR = ["drive", "falta"] as const;   // drive: S - div_arred(q S, C); falta: div_arred(q S, C)
export const ORDEM_MEIA_VIDA = 10;                              // "na mesma ordem": a maior meia-vida do par < 10 vezes a menor

/** uma checagem estatica do grafo do corpo falhou (secao 18) */
export class GrafoInvalido extends Error {
  constructor(mensagem: string) { super(mensagem); this.name = "GrafoInvalido"; }
}

export interface Quimico {
  nome: string; teto: number; descarte: boolean; receptor: string | null; leitura: string | null; meia_vida: number | null;
  k_meia_vida: number | null;
}
/** uma reacao do tick. Sem limiar (`le` ausente): a digestao, que tira ate `taxa` de cada consumido; o que ela produz sai da fracao
 *  num/den do consumido (`fracoes`), com o resto guardado. Com limiar (o metabolismo): uma transferencia 1 por 1 de um quimico a outro,
 *  que so anda com `le` acima (ou abaixo) de `limiar`, ate min(taxa, a distancia ao limiar, o que ha, o que cabe) */
export interface Reacao {
  nome: string; consome: string[]; produz: string[]; taxa: number;
  fracoes?: [string, number, number][]; le?: string | null; lado?: string | null; limiar?: number;
}
const fracoesDe = (r: Reacao): [string, number, number][] => r.fracoes ?? [];
const leDe = (r: Reacao): string | null => r.le ?? null;
/** uma aresta receptor -> emissor: o emissor le `quimico`, com ganho num/den; sinal +1 (mais do lido, mais efeito) ou -1 */
export interface Leitura { quimico: string; num: number; den: number; sinal: number }
export interface Emissor {
  nome: string; gatilho: string; fase: number; efeitos: [string, number][]; le: Leitura[]; limiar: number; divisor: number;
  variavel: boolean;
}
export interface GrafoCorpo { quimicos: Quimico[]; reacoes: Reacao[]; emissores: Emissor[] }

export const quimico = (nome: string, teto: number, descarte = true, extra: Partial<Quimico> = {}): Quimico =>
  ({ nome, teto, descarte, receptor: null, leitura: null, meia_vida: null, k_meia_vida: null, ...extra });
export const leitura = (q: string, num: number, den: number, sinal = 1): Leitura => ({ quimico: q, num, den, sinal });
export const emissor = (nome: string, gatilho: string, fase: number, efeitos: [string, number][],
  extra: Partial<Pick<Emissor, "le" | "limiar" | "divisor" | "variavel">> = {}): Emissor =>
  ({ nome, gatilho, fase, efeitos, le: [], limiar: 0, divisor: 1, variavel: false, ...extra });

export const nomesDoGrafo = (g: GrafoCorpo): string[] => g.quimicos.map((q) => q.nome);
export function quimicoDoGrafo(g: GrafoCorpo, nome: string): Quimico {
  const q = g.quimicos.find((x) => x.nome === nome);
  if (!q) throw new Error(`quimico fora do grafo: ${nome}`);
  return q;
}
export function emissorDoGrafo(g: GrafoCorpo, nome: string): Emissor {
  const e = g.emissores.find((x) => x.nome === nome);
  if (!e) throw new Error(`emissor fora do grafo: ${nome}`);
  return e;
}
export const temEmissor = (g: GrafoCorpo, nome: string): boolean => g.emissores.some((e) => e.nome === nome);
export const daFase = (g: GrafoCorpo, fase: number): Emissor[] => g.emissores.filter((e) => e.fase === fase && e.gatilho !== "estimulo");
export const receptoresDoGrafo = (g: GrafoCorpo): Quimico[] => g.quimicos.filter((q) => q.receptor !== null);

/** a forma da tabela: nomes unicos, gatilhos e leituras conhecidos, meia-vida e k juntas, deltas inteiros nao nulos */
function forma(g: GrafoCorpo): void {
  const nomes = nomesDoGrafo(g);
  if (new Set(nomes).size !== nomes.length) throw new GrafoInvalido(`quimico repetido: ${nomes}`);
  const receptores = g.quimicos.filter((q) => q.receptor !== null).map((q) => q.receptor);
  if (new Set(receptores).size !== receptores.length) throw new GrafoInvalido(`receptor repetido: ${receptores}`);
  for (const q of g.quimicos) {
    if (!Number.isInteger(q.teto) || q.teto < 0) throw new GrafoInvalido(`${q.nome}: teto ${q.teto}`);
    if ((q.receptor === null) !== (q.leitura === null) || (q.leitura !== null && !(LEITURAS_RECEPTOR as readonly string[]).includes(q.leitura))) {
      throw new GrafoInvalido(`${q.nome}: receptor ${q.receptor} com leitura ${q.leitura}`);
    }
    if ((q.meia_vida === null) !== (q.k_meia_vida === null)) throw new GrafoInvalido(`${q.nome}: meia-vida e k so juntas`);
    if (q.k_meia_vida !== null && (!Number.isInteger(q.k_meia_vida) || q.k_meia_vida <= 0 || (q.meia_vida as number) <= 0)) {
      throw new GrafoInvalido(`${q.nome}: meia-vida ${q.meia_vida}, k ${q.k_meia_vida}`);
    }
  }
  const nomesER = [...g.emissores.map((e) => e.nome), ...g.reacoes.map((r) => r.nome)];
  for (const nome of nomesER) {
    if (nomesER.filter((n) => n === nome).length !== 1) throw new GrafoInvalido(`emissor ou reacao repetido: ${nome}`);
  }
  for (const e of g.emissores) {
    if (!(GATILHOS as readonly string[]).includes(e.gatilho)) throw new GrafoInvalido(`${e.nome}: gatilho ${e.gatilho}`);
    if ((e.gatilho === "estimulo") !== (e.fase === 0) || ![0, 1, 2].includes(e.fase)) {
      throw new GrafoInvalido(`${e.nome}: fase ${e.fase} com o gatilho ${e.gatilho}`);
    }
    if (e.efeitos.length === 0 || e.efeitos.some(([, d]) => !Number.isInteger(d) || d === 0)) {
      throw new GrafoInvalido(`${e.nome}: efeitos ${JSON.stringify(e.efeitos)}`);
    }
    if (e.gatilho === "limiar" && !(e.le.length > 0 && e.divisor > 1)) {
      throw new GrafoInvalido(`${e.nome}: o gatilho limiar precisa de leituras e de divisor > 1`);
    }
    for (const le of e.le) {
      if (!Number.isInteger(le.num) || !Number.isInteger(le.den) || le.num < 0 || le.den <= 0 || (le.sinal !== 1 && le.sinal !== -1)) {
        throw new GrafoInvalido(`${e.nome}: leitura ${JSON.stringify(le)}`);
      }
    }
    if (e.gatilho === "abaixo" && !(e.le.length === 1 && e.le[0].sinal === -1 && e.divisor === 1 && e.fase === 2)) {
      throw new GrafoInvalido(`${e.nome}: o gatilho abaixo le um quimico so, com sinal -1 (menos dele, mais efeito), sem divisor, na fase 2`);
    }
  }
  for (const r of g.reacoes) {
    if (r.consome.length === 0 || !Number.isInteger(r.taxa) || r.taxa <= 0) throw new GrafoInvalido(`${r.nome}: reacao ${JSON.stringify(r)}`);
    const fr = fracoesDe(r);
    for (const [q, num, den] of fr) {
      if (!r.produz.includes(q) || !Number.isInteger(num) || !Number.isInteger(den) || num <= 0 || den <= 0) {
        throw new GrafoInvalido(`${r.nome}: fracao ${JSON.stringify([q, num, den])}`);
      }
    }
    if (new Set(fr.map(([q]) => q)).size !== fr.length) throw new GrafoInvalido(`${r.nome}: fracao repetida ${JSON.stringify(fr)}`);
    const lado = r.lado ?? null, limiar = r.limiar ?? 0;
    if ((leDe(r) === null) !== (lado === null)) throw new GrafoInvalido(`${r.nome}: o limiar de uma reacao pede o quimico lido e o lado juntos`);
    if (leDe(r) !== null) {
      if (!(LADOS_REACAO as readonly string[]).includes(lado as string) || r.consome.length !== 1 || r.produz.length !== 1
        || r.consome[0] === r.produz[0] || fr.length || !Number.isInteger(limiar) || limiar < 0) {
        throw new GrafoInvalido(`${r.nome}: a reacao com limiar e uma transferencia 1 por 1 de um quimico a outro, com o lado `
          + `${LADOS_REACAO} e limiar inteiro: ${JSON.stringify(r)}`);
      }
    } else if (limiar !== 0) {
      throw new GrafoInvalido(`${r.nome}: limiar sem o quimico lido`);
    }
  }
}

function fechado(g: GrafoCorpo): void {
  const conhecidos = new Set(nomesDoGrafo(g));
  const citados: [string, string][] = [];
  for (const r of g.reacoes) {
    for (const q of [...r.consome, ...r.produz, ...(leDe(r) === null ? [] : [leDe(r) as string])]) citados.push([r.nome, q]);
  }
  for (const e of g.emissores) {
    for (const [q] of e.efeitos) citados.push([e.nome, q]);
    for (const le of e.le) citados.push([e.nome, le.quimico]);
  }
  const fora = [...new Set(citados.filter(([, q]) => !conhecidos.has(q)).map(([onde, q]) => `${onde}:${q}`))].sort();
  if (fora.length) throw new GrafoInvalido(`grafo nao fechado: quimicos fora da tabela ${fora.join(", ")}`);
}

/** (sumidouros, fontes) por quimico, com o que os faz */
function caminhos(g: GrafoCorpo): [Record<string, string[]>, Record<string, string[]>] {
  const sumidouros: Record<string, string[]> = {}, fontes: Record<string, string[]> = {};
  for (const q of nomesDoGrafo(g)) { sumidouros[q] = []; fontes[q] = []; }
  for (const r of g.reacoes) {
    for (const q of r.consome) sumidouros[q].push(`reacao:${r.nome}`);
    for (const q of r.produz) fontes[q].push(`reacao:${r.nome}`);
  }
  for (const e of g.emissores) for (const [q, d] of e.efeitos) (d < 0 ? sumidouros : fontes)[q].push(`emissor:${e.nome}`);
  for (const q of g.quimicos) {
    if (q.k_meia_vida !== null) sumidouros[q.nome].push("meia_vida");
    if (q.teto > 0 && q.descarte) sumidouros[q.nome].push("teto");
  }
  return [sumidouros, fontes];
}

/** as arestas de influencia positiva receptor -> emissor -> quimico, com o maior ganho [num, den] entre os emissores (chave "a|b") */
function arestas(g: GrafoCorpo): Map<string, [number, number]> {
  const out = new Map<string, [number, number]>();
  for (const e of g.emissores) {
    for (const le of e.le) {
      for (const [alvo, d] of e.efeitos) {
        if ((d > 0) === (le.sinal > 0)) {                          // mais do lido, mais do alvo
          const chave = `${le.quimico}|${alvo}`;
          const atual = out.get(chave);
          if (atual === undefined || BigInt(le.num) * BigInt(atual[1]) > BigInt(atual[0]) * BigInt(le.den)) out.set(chave, [le.num, le.den]);
        }
      }
    }
  }
  // as transferencias com limiar andam 1 por 1 (ganho local 1). "acima": mais do lido, mais do produzido; "abaixo": mais do lido, menos
  // consumo (mais do consumido). As retroalimentacoes do metabolismo sao negativas e nao viram aresta
  for (const r of g.reacoes) {
    const le = leDe(r);
    if (le === null) continue;
    for (const alvo of (r.lado === "acima" ? r.produz : r.consome)) if (!out.has(`${le}|${alvo}`)) out.set(`${le}|${alvo}`, [1, 1]);
  }
  return out;
}

/** as checagens 2b e 3b (falham alto): o que as transferencias consomem tem fonte, e o que elas tocam chega a um sumidouro de verdade
 *  (nem o teto nem outra transferencia) */
function transferencias(g: GrafoCorpo, sumidouros: Record<string, string[]>, fontes: Record<string, string[]>): void {
  const tr = g.reacoes.filter((r) => leDe(r) !== null);
  if (!tr.length) return;
  const transfere = new Set(tr.map((r) => r.nome));
  const consumidos = [...new Set(tr.flatMap((r) => r.consome))].sort(porTexto);
  const semFonte = consumidos.filter((q) => fontes[q].length === 0);
  if (semFonte.length) throw new GrafoInvalido(`quimicos que uma transferencia consome sem fonte (o teto nao repoe; nao automantido): ${semFonte}`);
  const real = new Set(Object.keys(sumidouros).filter((q) => sumidouros[q].some((x) =>
    x !== "teto" && !(x.startsWith("reacao:") && transfere.has(x.slice("reacao:".length))))));
  const passa = new Map<string, Set<string>>();
  for (const r of tr) {
    if (!passa.has(r.consome[0])) passa.set(r.consome[0], new Set());
    passa.get(r.consome[0])!.add(r.produz[0]);
  }
  const tocados = [...new Set(tr.flatMap((r) => [...r.consome, ...r.produz]))].sort(porTexto);
  const presos: string[] = [];
  for (const q of tocados) {
    const vistos = new Set<string>();
    const pilha = [q];
    while (pilha.length) {
      const x = pilha.pop() as string;
      if (!vistos.has(x)) { vistos.add(x); pilha.push(...(passa.get(x) ?? [])); }
    }
    if (![...vistos].some((x) => real.has(x))) presos.push(q);
  }
  if (presos.length) throw new GrafoInvalido(`estoques que so saem pelo teto (sem sumidouro de verdade pelas transferencias): ${presos}`);
}
const parDe = (chave: string): [string, string] => chave.split("|") as [string, string];
const porTexto = (a: string, b: string): number => (a < b ? -1 : a > b ? 1 : 0);

/** os ciclos simples do grafo dirigido (cada um uma vez, comecando pelo menor no) */
export function ciclosDoGrafo(arest: Map<string, [number, number]>): string[][] {
  const vizinhos = new Map<string, string[]>();
  for (const chave of arest.keys()) {
    const [a, b] = parDe(chave);
    if (!vizinhos.has(a)) vizinhos.set(a, []);
    vizinhos.get(a)!.push(b);
  }
  const achados: string[][] = [];
  const busca = (inicio: string, atual: string, caminho: string[]): void => {
    for (const prox of [...(vizinhos.get(atual) ?? [])].sort(porTexto)) {
      if (prox === inicio) achados.push([...caminho]);
      else if (prox > inicio && !caminho.includes(prox)) busca(inicio, prox, [...caminho, prox]);
    }
  };
  for (const no of [...vizinhos.keys()].sort(porTexto)) busca(no, no, [no]);
  return achados;
}

export interface RelatoGrafo {
  pares_meia_vida_mesma_ordem: string[][]; so_pelo_teto: string[]; lacos: { ciclo: string[]; ganho: [number, number] }[];
  sumidouros: Record<string, string[]>; fontes: Record<string, string[]>;
}

/** as quatro checagens da secao 18 (falham alto) e o relato: fechado, sumidouro, automantido e laco de ganho >= 1 (em inteiros) */
export function checarGrafo(g: GrafoCorpo): RelatoGrafo {
  forma(g);
  fechado(g);
  const [sumidouros, fontes] = caminhos(g);
  const semSumidouro = Object.keys(sumidouros).filter((q) => sumidouros[q].length === 0);
  if (semSumidouro.length) throw new GrafoInvalido(`quimicos sem sumidouro: ${semSumidouro}`);
  const teto = new Map(g.quimicos.map((q) => [q.nome, q.teto > 0]));
  const semReposicao = Object.keys(sumidouros).filter((q) => sumidouros[q].some((x) => x !== "teto") && fontes[q].length === 0 && !teto.get(q));
  if (semReposicao.length) throw new GrafoInvalido(`quimicos consumidos sem reposicao nem teto (nao automantido): ${semReposicao}`);
  transferencias(g, sumidouros, fontes);
  const arest = arestas(g);
  const lacos: { ciclo: string[]; ganho: [number, number] }[] = [];
  for (const c of ciclosDoGrafo(arest)) {
    let num = 1n, den = 1n;
    for (let i = 0; i < c.length; i++) {
      const [n, d] = arest.get(`${c[i]}|${c[(i + 1) % c.length]}`)!;
      num *= BigInt(n);
      den *= BigInt(d);
    }
    lacos.push({ ciclo: [...c], ganho: [Number(num), Number(den)] });
    if (num >= den) throw new GrafoInvalido(`laco receptor -> emissor com ganho >= 1: ${c} (${num}/${den})`);
  }
  return {
    pares_meia_vida_mesma_ordem: paresMesmaOrdem(g, arest),
    so_pelo_teto: Object.keys(sumidouros).filter((q) => sumidouros[q].length === 1 && sumidouros[q][0] === "teto").sort(porTexto),
    lacos,
    sumidouros: Object.fromEntries(Object.entries(sumidouros).map(([q, s]) => [q, [...s]])),
    fontes: Object.fromEntries(Object.entries(fontes).map(([q, s]) => [q, [...s]])),
  };
}

/** os pares acoplados (uma aresta entre eles, ou o mesmo emissor/reacao mexendo nos dois) com meias-vidas na mesma ordem. So relato */
export function paresMesmaOrdem(g: GrafoCorpo, arest?: Map<string, [number, number]>): string[][] {
  const ar = arest ?? arestas(g);
  const acoplados = new Set<string>();
  const junta = (a: string, b: string): void => { if (a !== b) acoplados.add(a < b ? `${a}|${b}` : `${b}|${a}`); };
  for (const chave of ar.keys()) { const [a, b] = parDe(chave); junta(a, b); }
  for (const e of g.emissores) {
    const alvos = [...e.efeitos.map(([q]) => q), ...e.le.map((le) => le.quimico)];
    for (const a of alvos) for (const b of alvos) junta(a, b);
  }
  for (const r of g.reacoes) {
    const alvos = [...r.consome, ...r.produz];
    for (const a of alvos) for (const b of alvos) junta(a, b);
  }
  const h = new Map(g.quimicos.filter((q) => q.meia_vida !== null).map((q) => [q.nome, q.meia_vida as number]));
  const pares: string[][] = [];
  for (const par of acoplados) {
    const [a, b] = parDe(par);
    const ha = h.get(a), hb = h.get(b);
    if (ha !== undefined && hb !== undefined && Math.max(ha, hb) < ORDEM_MEIA_VIDA * Math.min(ha, hb)) pares.push([a, b]);
  }
  return pares.sort((x, y) => porTexto(x[0], y[0]) || porTexto(x[1], y[1]));
}

const MEIAS_VIDAS: Record<string, ["k_meia_vida_estresse" | "k_meia_vida_dor" | "k_meia_vida_susto", number]> = {
  estresse: ["k_meia_vida_estresse", 1440], dor: ["k_meia_vida_dor", 60], susto: ["k_meia_vida_susto", 30],
};
/** o nome do receptor (o campo da PercepcaoCorpo do Python) */
export const RECEPTOR_DE: Readonly<Record<string, string>> = {
  ...DRIVE_DO_QUIMICO, ...Object.fromEntries([...NOVOS_CORPO, ...GESTOS_CORPO].map((n) => [n, n])),
};

/** corpo.grafo_do_corpo: a tabela unica do corpo com estas chaves. Os estimulos de quantidade variavel guardam so o sinal; com a
 *  digestao, a comida entra no estomago (`alimento`) e a reacao da digestao a tira, junto com a fome */
export function grafoDoCorpo(cc: ConfigCorpo, t: TaxasCorpo, comMundo = false): GrafoCorpo {
  const E = cc.escala;
  const nomes = quimicosDe(cc, comMundo);
  const quimicos = nomes.map((n) => {
    const receptor = RECEPTOR_DE[n] ?? null;
    const lei = receptor === null ? null : ((QUIMICOS_HOJE as readonly string[]).includes(n) ? "drive" : "falta");
    const h = MEIAS_VIDAS[n];
    return quimico(n, E, true, { receptor, leitura: lei, meia_vida: h === undefined ? null : h[1], k_meia_vida: h === undefined ? null : cc[h[0]] });
  });
  // a digestao tira o alimento e a fome; com o metabolismo, poe no combustivel uma fracao do que digeriu
  const fracoes: [string, number, number][] = cc.metabolismo ? [["combustivel", cc.conversao_num, cc.conversao_den]] : [];
  const reacoes: Reacao[] = cc.digestao
    ? [{ nome: "digestao", consome: ["alimento", "fome"], produz: fracoes.map(([q]) => q), taxa: cc.taxa_digestao, fracoes }] : [];
  if (cc.metabolismo) {
    // as transferencias com limiar: o excedente vai a reserva, e a reserva volta quando o combustivel cai
    reacoes.push({ nome: "armazenamento", consome: ["combustivel"], produz: ["reserva"], taxa: cc.armazenar_taxa, le: "combustivel",
      lado: "acima", limiar: cc.armazenar_limiar },
    { nome: "mobilizacao", consome: ["reserva"], produz: ["combustivel"], taxa: cc.mobilizar_taxa, le: "combustivel", lado: "abaixo",
      limiar: cc.mobilizar_limiar });
  }
  const comida = (efeitos: Record<string, number>): [string, number][] => {
    if (cc.digestao && (efeitos.fome ?? 0) < 0) {
      return [...Object.entries(efeitos).filter(([k]) => k !== "fome"), ["alimento", menos(efeitos.fome)]];
    }
    return Object.entries(efeitos);
  };
  const em: Emissor[] = [
    emissor("fome_tick", "tick", 1, [["fome", t.fome_por_tick]]),
    emissor("desconforto_tick", "tick", 1, [["desconforto", t.desconforto_por_tick]]),
    emissor("desconforto_sujeira", "sujeira", 1, [["desconforto", t.desconforto_por_sujeira]]),
    emissor("tristeza_tick", "tick", 1, [["tristeza", t.tristeza_por_tick]]),
    emissor("cansaco_dormindo", "dormindo", 1, [["cansaco", t.cansaco_dormindo]]),
    emissor("cansaco_noite", "noite_acordado", 1, [["cansaco", t.cansaco_noite]]),
    emissor("cansaco_dia", "dia_acordado", 1, [["cansaco", t.cansaco_acordado]]),
  ];
  if (cc.vida) em.push(emissor("vida_tick", "tick", 1, [["vida", menos(cc.vida_decaimento)]]));
  const sobe: Record<string, number> = { tedio: cc.tedio_sobe, curiosidade: cc.curiosidade_sobe, solidao: cc.solidao_sobe };
  for (const n of NOVOS_CORPO) if (n in sobe && nomes.includes(n)) em.push(emissor(`${n}_sobe`, "acordado", 1, [[n, sobe[n]]]));
  if (cc.metabolismo) {
    em.push(emissor("gasto_basal_acordado", "acordado", 1, [["combustivel", menos(cc.gasto_basal_acordado)]]),
      emissor("gasto_basal_dormindo", "dormindo", 1, [["combustivel", menos(cc.gasto_basal_dormindo)]]));
  }
  const degrau = QUIMICOS_DA_PRIVACAO.map((n) => leitura(n, 1, 1));       // um degrau: conta como ganho 1 se entrar num laco
  em.push(emissor("dano_privacao", "privacao", 2, [["dano", t.dano_privacao]], { le: degrau }),
    emissor("dano_cura", "sem_privacao", 2, [["dano", t.dano_cura]]));
  if (nomes.includes("estresse")) {
    const le = DRIVES_DO_ESTRESSE.filter((n) => nomes.includes(n)).map((n) => leitura(n, 1, cc.estresse_divisor));
    em.push(emissor("estresse_drives", "limiar", 2, [["estresse", 1]], { le, limiar: cc.estresse_limiar, divisor: cc.estresse_divisor,
      variavel: true }));
  }
  if (cc.metabolismo) {
    // a falta de combustivel sobe o cansaco (ME-1, a unica ponte); um degrau, como o dano pela privacao
    em.push(emissor("falta_combustivel", "abaixo", 2, [["cansaco", cc.falta_cansaco]], { le: [leitura("combustivel", 1, 1, -1)],
      limiar: cc.falta_limiar }));
  }
  // os estimulos (fase 0): os de hoje pelas taxas, os do mundo e os da etapa 6
  for (const [acao, efeitos] of Object.entries(t.dono)) {
    em.push(emissor(`dono:${acao}`, "estimulo", 0, acao === "alimentar" ? comida(efeitos) : Object.entries(efeitos)));
  }
  for (const [acao, efeitos] of Object.entries(t.pet)) {
    if (Object.keys(efeitos).length) em.push(emissor(`pet:${acao}`, "estimulo", 0, acao === "comer" ? comida(efeitos) : Object.entries(efeitos)));
  }
  em.push(emissor("bola", "estimulo", 0, [["tristeza", -1]], { variavel: true }),
    emissor("fruta", "estimulo", 0, comida({ fome: -1, tristeza: -1 }), { variavel: true }),
    emissor("fruta_ruim", "estimulo", 0, [["tristeza", 1]], { variavel: true }),
    emissor("andar", "estimulo", 0, [["cansaco", 1], ...(cc.metabolismo ? [["combustivel", -1] as [string, number]] : [])],
      { variavel: true }),
    emissor("comida_podre", "estimulo", 0, [["tristeza", 1]], { variavel: true }));
  if (cc.drives_novos) {
    const bases: Record<AtividadeTedio, number> = { bola: cc.tedio_bola, brincar: cc.tedio_brincar, explorar: cc.tedio_explorar,
      dono_brinca: cc.tedio_dono };
    for (const a of ATIVIDADES_TEDIO) em.push(emissor(`atividade:${a}`, "estimulo", 0, [["tedio", menos(bases[a])]]));
    if (nomes.includes("curiosidade")) em.push(emissor("novidade", "estimulo", 0, [["curiosidade", menos(cc.curiosidade_novidade)]]));
    const medo = (d: number): Leitura[] => (cc.gestos ? [leitura("susto", d * cc.medo_da_mao, E, -1)] : []);
    em.push(emissor("carinho_solidao", "estimulo", 0, [["solidao", menos(cc.carinho_solidao)]], { le: medo(cc.carinho_solidao) }));
    em.push(emissor("carinho_estresse", "estimulo", 0, [["estresse", menos(cc.carinho_estresse)]], { le: medo(cc.carinho_estresse) }));
  }
  if (cc.gestos) {
    em.push(emissor("tapa", "estimulo", 0, [["dor", cc.tapa_dor], ["susto", cc.tapa_susto], ["estresse", cc.tapa_estresse]]));
  }
  return { quimicos, reacoes, emissores: em };
}

// ================================================================== orgao 2: os limiares da Vida
/** as duracoes de bebe, crianca e adolescente em minutos (ConfigEvolucaoPesquisa; o padrao e o de hoje, DUR_EVO) */
export type DuracoesEstagio = readonly [number, number, number];
export const DURACOES_PESQUISA: DuracoesEstagio = [DUR_EVO.bebe, DUR_EVO.crianca, DUR_EVO.adolescente];

/** os ticks em que o estagio de hoje muda (treino_stats.estagio_no_tick): fim do bebe, da crianca e do adolescente */
export function ticksDeEstagio(d: DuracoesEstagio): [number, number, number] {
  const t1 = d[0], t2 = t1 + d[1];
  return [t1, t2, t2 + d[2]];
}

/** os limiares dos receptores de estagio: C - v T para cada tick de estagio T; um limiar que nao fica acima de 0 falha alto */
export function limiaresEstagio(cc: ConfigCorpo, d: DuracoesEstagio = DURACOES_PESQUISA): number[] {
  const lim = ticksDeEstagio(d).map((t) => cc.escala - cc.vida_decaimento * t);
  if (lim.some((x) => x <= 0)) throw new Error(`a Vida acaba antes de um estagio: limiares ${lim} (v = ${cc.vida_decaimento})`);
  return lim;
}

// ================================================================== o corpo
/** o estado do pet no comeco do tick, o que o corpo le dele: a hora (tick absoluto), o sono e a sujeira */
export interface EstadoNoTick { tick: number; dormindo: boolean; sujeira: number }
/** os drives de hoje e o tick (o Estado do Python), para nascer um corpo deles */
export interface EstadoDrives { tick: number; fome: number; higiene: number; energia: number; humor: number; saude: number }
export interface OpcoesCorpo {
  cc?: ConfigCorpo;
  duracoes?: DuracoesEstagio;    // a cfg_evo do Python (so com a Vida)
  comMundo?: boolean;            // o mundo fisico: a curiosidade existe (CD-8)
}
type DrivesHoje = { fome: number; higiene: number; energia: number; humor: number; saude: number };

/** A quimica dos drives de hoje e os orgaos ligados. `q` guarda cada quimico em [0, C] (a falta, nos de hoje). Nao sorteia. */
export class Corpo {
  readonly cc: ConfigCorpo;
  readonly C: number;
  readonly S: number;
  readonly t: TaxasCorpo;
  readonly comMundo: boolean;
  /** a tabela unica, conferida na carga (falha alto); trocavel como no Python (o tick a le a cada passo) */
  grafo: GrafoCorpo;
  readonly relato_grafo: RelatoGrafo;
  readonly quimicos: string[];
  q: Record<string, number>;
  janela_tedio: string[] = [];                 // DS-4: as ultimas atividades (so com drives_novos)
  // orgao 1: o que passou do estomago para a fome (no tick corrente, no ultimo tick fechado e no total) e o que se descartou
  digerido_tick = 0;
  digerido_no_tick = 0;
  digerido_total = 0;
  descartado_total = 0;
  // metabolismo: o resto da conversao (em [0, conversao_den)), as transferencias com limiar e a contabilidade do combustivel e da reserva,
  // em totais (CONTAS_METABOLISMO); sem o metabolismo, as contas sao null
  resto_combustivel = 0;
  private readonly fracoes: [string, number, number][];
  private readonly transferencias: Reacao[];
  readonly contas_metabolismo: Record<ContaMetabolismo, number> | null;
  readonly limiares_estagio: number[];

  constructor(q: Record<string, number>, opcoes: OpcoesCorpo = {}) {
    this.cc = opcoes.cc ?? CCO_LIGADA;
    if (!this.cc.ligada) throw new Error("Corpo com ConfigCorpo desligada: com a chave desligada o corpo nao existe");
    this.comMundo = opcoes.comMundo ?? false;
    this.C = this.cc.escala;
    this.S = this.cc.escala_receptor;
    this.t = taxasDe(this.cc);
    this.grafo = grafoDoCorpo(this.cc, this.t, this.comMundo);
    this.relato_grafo = checarGrafo(this.grafo);
    this.quimicos = nomesDoGrafo(this.grafo);
    const esperados = quimicosDe(this.cc, this.comMundo);
    if (this.quimicos.join() !== esperados.join()) throw new Error("o grafo e a lista de quimicos divergem");
    const chaves = Object.keys(q);
    if (chaves.length !== this.quimicos.length || !this.quimicos.every((n) => n in q)) {
      throw new Error(`quimicos do corpo: esperava ${this.quimicos}, veio ${[...chaves].sort()}`);
    }
    for (const [nome, v] of Object.entries(q)) {
      const teto = quimicoDoGrafo(this.grafo, nome).teto;
      if (!Number.isInteger(v) || v < 0 || v > teto) throw new Error(`concentracao de ${nome} fora de [0, ${teto}] ou nao inteira: ${v}`);
    }
    this.q = Object.fromEntries(this.quimicos.map((n) => [n, q[n] + 0]));
    this.fracoes = fracoesDe(this.grafo.reacoes.find((r) => r.nome === "digestao") ?? { nome: "", consome: [], produz: [], taxa: 0 });
    for (const [nome] of this.fracoes) {
      if (nome !== "combustivel") throw new Error(`a digestao produz ${nome}, que o corpo em TS nao tem (so o combustivel do metabolismo)`);
    }
    this.transferencias = this.grafo.reacoes.filter((r) => leDe(r) !== null);
    this.contas_metabolismo = this.cc.metabolismo
      ? Object.fromEntries(CONTAS_METABOLISMO.map((k) => [k, 0])) as Record<ContaMetabolismo, number> : null;
    this.limiares_estagio = this.cc.vida ? limiaresEstagio(this.cc, opcoes.duracoes ?? DURACOES_PESQUISA) : [];
  }

  /** o corpo de um estado de hoje (o do nascimento, por exemplo): cada drive tem de cair na grade de C; a Vida e a do tick; os
   *  quimicos da etapa 6 comecam em 0 */
  static deEstado(estado: EstadoDrives, opcoes: OpcoesCorpo = {}): Corpo {
    const cc = opcoes.cc ?? CCO_LIGADA;
    const E = cc.escala;
    const q: Record<string, number> = {};
    for (const [nome, drive] of Object.entries(DRIVE_DO_QUIMICO)) {
      q[nome] = naGrade(1 - estado[drive as keyof DrivesHoje], E, `Estado.${drive}`);
    }
    if (cc.digestao) q.alimento = 0;                // o estado de hoje nao tem estomago: comeca vazio
    if (cc.vida) q.vida = Math.max(0, E - cc.vida_decaimento * estado.tick);
    if (cc.metabolismo) {
      q.combustivel = cc.combustivel_inicial;
      q.reserva = cc.reserva_inicial;
    }
    for (const nome of quimicosDe(cc, opcoes.comMundo ?? false)) if (!(nome in q)) q[nome] = 0;
    return new Corpo(q, { ...opcoes, cc });
  }

  // ---------------------------------------------------------- estimulos
  /** soma os deltas, cortados em [0, C]. Com o metabolismo, o que sai do combustivel por aqui e gasto (`rubrica`: o basal no tick, as
   *  atividades nos estimulos) e entra nas contas pelo que de fato saiu; combustivel subindo por aqui falha alto (a conversao e a
   *  mobilizacao tem caminho proprio) */
  private somar(deltas: Record<string, number>, rubrica: "gasto_basal" | "gasto_atividade" = "gasto_atividade"): void {
    const temComb = Object.hasOwn(deltas, "combustivel");
    if (temComb && !this.contas_metabolismo) throw new Error("quimico fora do corpo: combustivel");
    const antes = temComb ? this.q.combustivel : 0;
    for (const [nome, d] of Object.entries(deltas)) {
      if (!(nome in this.q)) throw new Error(`quimico fora do corpo: ${nome}`);
      this.q[nome] = Math.min(this.C, Math.max(0, this.q[nome] + d));
    }
    if (temComb) {
      if (deltas.combustivel > 0) throw new Error(`combustivel subindo fora da conversao e da mobilizacao: ${deltas.combustivel}`);
      (this.contas_metabolismo as Record<ContaMetabolismo, number>)[rubrica] += antes - this.q.combustivel;
    }
  }

  /** os deltas de uma acao; com a digestao, o que a comida tira da fome vai para o estomago */
  private efeito(deltas: Record<string, number>, comida: boolean): void {
    if (comida && this.cc.digestao) {
      if (deltas.fome === undefined) throw new Error("comida sem fome nos deltas");
      this.somar(Object.fromEntries(Object.entries(deltas).filter(([k]) => k !== "fome")));
      this.ingerir(menos(deltas.fome));
    } else {
      this.somar(deltas);
    }
  }

  /** o efeito de state.aplicar_acao_usuario nos drives (as seis de hoje e o tapa, com `gestos`). Com `drives_novos`, o dono brincar e
   *  a atividade "dono_brinca" e o acariciar e o carinho (solidao e estresse, vezes o medo da mao com `gestos`). A sujeira e o sono
   *  continuam com o motor. Acao fora destas falha alto. */
  acaoDono(acao: string): void {
    if (acao === VALOR_TAPA) {
      if (!this.cc.gestos) throw new Error("tapa sem a sub-chave gestos (secao 8): so o MotorCorpo com gestos aceita");
      this.estimulo("tapa");
      return;
    }
    if (!Object.hasOwn(this.t.dono, acao)) throw new Error(`acao do dono sem estimulo no corpo nesta etapa: ${acao}`);
    this.efeito(this.t.dono[acao as AcaoDonoHoje], acao === "alimentar");
    if (this.cc.drives_novos) {
      if (acao === "brincar") this.atividade("dono_brinca");
      else if (acao === "acariciar") this.carinho();
    }
  }

  /** um estimulo de quantidade fixa da tabela (o tapa) */
  private estimulo(nome: string): void {
    this.somar(Object.fromEntries(emissorDoGrafo(this.grafo, nome).efeitos));
  }

  /** secao 8: o carinho na solidao e no estresse, vezes (C - medo_da_mao q_susto) / C com `gestos`; sem `gestos`, inteiro */
  private carinho(): void {
    const fator = this.cc.gestos ? this.C - this.cc.medo_da_mao * this.q.susto : this.C;
    for (const nome of ["carinho_solidao", "carinho_estresse"]) {
      this.somar(Object.fromEntries(emissorDoGrafo(this.grafo, nome).efeitos.map(([q, d]) => [q, divArred(d * fator, this.C)])));
    }
  }

  /** DS-4: a reducao do tedio pela atividade e div_arred(base (J - r), J), r as vezes que ela aparece na janela das ultimas J antes
   *  desta; depois ela entra na janela e a mais antiga sai. So com `drives_novos`. */
  atividade(nome: string): void {
    if (!this.cc.drives_novos) throw new Error("atividade do tedio sem a sub-chave drives_novos");
    if (!(ATIVIDADES_TEDIO as readonly string[]).includes(nome)) throw new Error(`atividade desconhecida: ${nome} (so ${ATIVIDADES_TEDIO})`);
    const base = menos(Object.fromEntries(emissorDoGrafo(this.grafo, `atividade:${nome}`).efeitos).tedio);
    const J = this.cc.janela_tedio;
    const r = this.janela_tedio.filter((a) => a === nome).length;
    this.somar({ tedio: menos(divArred(base * (J - r), J)) });
    this.janela_tedio.push(nome);
    if (this.janela_tedio.length > J) this.janela_tedio.splice(0, this.janela_tedio.length - J);
  }

  /** secao 7: explorar e achar `n` objetos novos tira a curiosidade por novidade, ate o maximo. Sem a curiosidade, falha alto */
  estimuloNovidade(n: number): void {
    if (!("curiosidade" in this.q)) throw new Error("novidade sem a curiosidade: ela exige drives_novos e o mundo fisico (CD-8)");
    if (!Number.isInteger(n) || n < 0) throw new Error(`numero de novidades precisa ser inteiro >= 0: ${n}`);
    const k = Math.min(n, this.cc.curiosidade_max_novidades);
    if (k) this.somar(Object.fromEntries(emissorDoGrafo(this.grafo, "novidade").efeitos.map(([q, d]) => [q, d * k])));
  }

  /** o efeito de policy.efeito_da_acao_do_pet nos drives, na decisao, antes do tick. O comer e comida. No mundo fisico (MF-2), comer
   *  nao da fome por si: a comida vem do mapa */
  acaoPet(acao: AcaoPet, comMundo = false): void {
    if (comMundo && acao === "comer") return;
    if (!Object.hasOwn(this.t.pet, acao)) throw new Error(`acao do pet desconhecida: ${acao}`);
    this.efeito(this.t.pet[acao], acao === "comer");
  }

  /** brincar com a bola no cenario: humor + ganho_humor_bola */
  estimuloBola(ganhoHumor: number): void {
    this.somar({ tristeza: menos(naGrade(ganhoHumor, this.C, "ganho_humor_bola")) });
  }

  /** comer uma fruta: fome + nutricao e humor + o efeito da fruta. Sem a digestao, direto na fome */
  estimuloFruta(nutricao: number, efeitoHumor: number): void {
    this.efeito({ fome: menos(naGrade(nutricao, this.C, "nutricao")), tristeza: menos(naGrade(efeitoHumor, this.C, "efeito_humor")) }, true);
  }

  // ---------------------------------------------------------- o mundo fisico
  /** o andar: energia - custo x deslocamento (subunidades, inteiro >= 0); um custo fora da grade falha alto. Com o metabolismo, a
   *  tabela tira do combustivel o gasto da atividade sobre o andar inteiro desta decisao (o arredondamento e um so) */
  estimuloAndar(deslocamento: number, custoPorSubunidade: number): void {
    if (!Number.isInteger(deslocamento) || deslocamento < 0) throw new Error(`deslocamento precisa ser inteiro >= 0: ${deslocamento}`);
    const k = naGrade(custoPorSubunidade, this.C, "custo_energia_por_subunidade");
    if (deslocamento) {
      const cansaco = k * deslocamento;
      this.somar(Object.fromEntries(emissorDoGrafo(this.grafo, "andar").efeitos.map(([q, d]) =>
        [q, d * (q === "cansaco" ? cansaco : gastoDaAtividade(this.cc, cansaco))])));
    }
  }

  /** comer uma comida do mapa: a racao madura (a do alimentar), a fruta madura (a nutricao do mundo e o efeito da fruta) e a podre
   *  (so o humor). Tipo ou situacao fora disso falha alto */
  estimuloConsumoMundo(tipo: string, situacao: string, cfgMundo: Pick<ConfigMundo, "nutricao_fruta" | "efeito_podre">, efeitoFruta = 0): void {
    if (!(TIPOS_COMIDA_MUNDO as readonly string[]).includes(tipo)) throw new Error(`comida do mundo desconhecida: ${tipo}`);
    if (situacao === "podre") this.somar({ tristeza: menos(naGrade(cfgMundo.efeito_podre, this.C, "efeito_podre")) });
    else if (situacao !== "madura") throw new Error(`situacao da comida desconhecida: ${situacao}`);
    else if (tipo === "racao") this.efeito(this.t.dono.alimentar, true);
    else if ((FRUTAS_MUNDO as readonly string[]).includes(tipo)) this.estimuloFruta(cfgMundo.nutricao_fruta, efeitoFruta);
    else throw new Error(`comida sem estimulo: ${tipo}`);
  }

  // ---------------------------------------------------------- orgao 1: a digestao
  /** a comida vai ao estomago (cortado em C) e a digestao anda na hora, com o que resta da taxa do tick */
  private ingerir(quantidade: number): void {
    if (quantidade < 0) throw new Error(`comida negativa: ${quantidade}`);
    this.q.alimento = Math.min(this.C, this.q.alimento + quantidade);
    this.digerir();
  }

  /** a reacao da secao 5: t = min(alimento, fome, o que resta da taxa no tick); com a fome em 0, o resto do estomago e descartado */
  private digerir(): void {
    const t = Math.min(this.q.alimento, this.q.fome, this.cc.taxa_digestao - this.digerido_tick);
    if (t > 0) {
      this.q.alimento -= t;
      this.q.fome -= t;
      this.digerido_tick += t;
      this.digerido_total += t;
      // o que a digestao produz, pela tabela: com o metabolismo, o combustivel sobe num/den do que se digeriu, com o resto guardado
      for (const [nome, num, den] of this.fracoes) {
        const resto = this.resto_combustivel + t * num;
        const v = Math.floor(resto / den);
        this.resto_combustivel = resto - v * den;
        const novo = this.q[nome] + v;
        this.q[nome] = Math.min(this.C, novo);
        const k = this.contas_metabolismo as Record<ContaMetabolismo, number>;
        k.convertido += v;
        k.descartado_teto += novo - this.q[nome];
      }
    }
    if (this.q.fome === 0 && this.q.alimento > 0) {
      this.descartado_total += this.q.alimento;
      this.q.alimento = 0;
    }
  }

  // ---------------------------------------------------------- o tick
  /** o receptor de privacao: algum de fome, desconforto e cansaco acima do limiar (Estado.em_privacao de hoje) */
  emPrivacao(): boolean {
    return QUIMICOS_DA_PRIVACAO.some((n) => this.q[n] > this.t.limiar_privacao);
  }

  private dispara(e: Emissor, antes: EstadoNoTick, noite: boolean): boolean {
    switch (e.gatilho) {
      case "tick": case "sujeira": return true;
      case "acordado": return !antes.dormindo;
      case "dormindo": return antes.dormindo;
      case "noite_acordado": return !antes.dormindo && noite;
      case "dia_acordado": return !antes.dormindo && !noite;
      default: throw new Error(`gatilho ${e.gatilho} fora da fase 1`);
    }
  }

  /** um tick, na ordem de state.avancar_um_tick, pelos emissores da tabela: 0) a digestao; 1) a fase 1, somada por quimico e cortada
   *  uma vez; 2) a fase 2 sobre os valores depois da fase 1 (o dano pelo receptor de privacao, o estresse pelos drives acima do
   *  limiar); 3) as meias-vidas. `antes` e o estado no comeco do tick */
  passo(antes: EstadoNoTick): void {
    if (this.cc.digestao) this.digerir();
    const noite = eNoite(antes.tick % TPD);
    let deltas: Record<string, number> = {};
    for (const e of daFase(this.grafo, 1)) {
      if (this.dispara(e, antes, noite)) {
        const n = e.gatilho === "sujeira" ? antes.sujeira : 1;
        for (const [q, d] of e.efeitos) deltas[q] = (deltas[q] ?? 0) + d * n;
      }
    }
    this.somar(deltas, "gasto_basal");
    // metabolismo: as transferencias com limiar, sobre os valores depois da fase 1 (antes da fase 2: a falta ve o que a reserva devolveu)
    for (const r of this.transferencias) this.transferir(r);
    const privacao = this.emPrivacao();
    deltas = {};
    for (const e of daFase(this.grafo, 2)) {
      let v: number;
      if (e.gatilho === "limiar") {
        let soma = 0;
        for (const le of e.le) soma += Math.max(0, this.q[le.quimico] - e.limiar);
        v = divArred(soma, e.divisor);
      } else if (e.gatilho === "privacao" || e.gatilho === "sem_privacao") {
        v = privacao === (e.gatilho === "privacao") ? 1 : 0;
      } else if (e.gatilho === "abaixo") {
        v = this.q[e.le[0].quimico] < e.limiar ? 1 : 0;
      } else {
        throw new Error(`gatilho ${e.gatilho} fora da fase 2`);
      }
      if (v) for (const [q, d] of e.efeitos) deltas[q] = (deltas[q] ?? 0) + d * v;
    }
    this.somar(deltas);
    const bits = this.cc.bits_meia_vida;
    for (const qm of this.grafo.quimicos) {
      if (qm.k_meia_vida !== null) this.q[qm.nome] = passoMeiaVida(this.q[qm.nome], qm.k_meia_vida, bits);
    }
    if (this.cc.digestao) {
      this.digerido_no_tick = this.digerido_tick;     // o tick fechou: a taxa volta inteira no proximo
      this.digerido_tick = 0;
    }
  }

  /** uma transferencia com limiar (o metabolismo): com o quimico lido do lado certo do limiar, passa 1 por 1 do consumido ao produzido
   *  ate min(taxa, a distancia ao limiar, o que ha, o que cabe): nada se perde e nada passa do teto */
  private transferir(r: Reacao): void {
    const de = r.consome[0], para = r.produz[0], le = leDe(r) as string, limiar = r.limiar ?? 0;
    const distancia = r.lado === "acima" ? this.q[le] - limiar : limiar - this.q[le];
    const t = Math.min(r.taxa, distancia, this.q[de], quimicoDoGrafo(this.grafo, para).teto - this.q[para]);
    if (t > 0) {
      this.q[de] -= t;
      this.q[para] += t;
      (this.contas_metabolismo as Record<ContaMetabolismo, number>)[para === "reserva" ? "armazenado" : "mobilizado"] += t;
    }
  }

  // ---------------------------------------------------------- leituras
  /** os drives de hoje lidos da quimica: (C - q) / C (a divisao IEEE e exata, igual no Python) */
  drives(): DrivesHoje {
    const d = (n: string): number => (this.C - this.q[n]) / this.C;
    return { fome: d("fome"), higiene: d("desconforto"), energia: d("cansaco"), humor: d("tristeza"), saude: d("dano") };
  }

  /** o estado com os cinco drives trocados pela leitura da quimica */
  noEstado<T extends DrivesHoje>(estado: T): T {
    return { ...estado, ...this.drives() };
  }

  /** a falta de um quimico na escala S do cerebro: div_arred(q S, C) */
  falta(nome: string): number {
    return divArred(this.q[nome] * this.S, this.C);
  }

  /** o que o pet sente, na escala S, pelos receptores da tabela: os drives de hoje leem S - falta; os novos leem a falta */
  receptores(): Record<string, number> {
    return Object.fromEntries(receptoresDoGrafo(this.grafo).map((qm) =>
      [qm.receptor as string, qm.leitura === "drive" ? this.S - this.falta(qm.nome) : this.falta(qm.nome)]));
  }

  /** os receptores de estagio sobre a Vida (so com o orgao 2): o numero de limiares que a Vida ja cruzou */
  estagio(): EstagioCorpo {
    if (!this.cc.vida) throw new Error("estagio pela Vida sem o orgao 2 (ConfigCorpo.vida desligada)");
    return ESTAGIOS_CORPO[this.limiares_estagio.filter((l) => this.q.vida <= l).length];
  }

  paraDict(): Record<string, unknown> {
    const d: Record<string, unknown> = { q: { ...this.q } };
    if (this.cc.digestao) {
      d.digestao = { digerido_no_tick: this.digerido_no_tick, digerido_total: this.digerido_total, descartado_total: this.descartado_total };
    }
    if (this.cc.vida) d.estagio = this.estagio();
    if (this.cc.drives_novos) d.janela_tedio = [...this.janela_tedio];
    if (this.contas_metabolismo) d.metabolismo = { resto_combustivel: this.resto_combustivel, contas: { ...this.contas_metabolismo } };
    return d;
  }
}
