/* Gambits do pet: hibrido (PROVISORIO, so na web).
   O PET propoe e aprende: a linha evolutiva semeia a lista; depois de cada luta contra bot, cada regra que
   disparou tem a nota puxada para o saldo de dano dos turnos em que agiu (+ bonus pelo resultado); a lista
   se reordena pela nota; uma regra ativa com nota ruim e trocada por uma candidata do repertorio (regras de
   todos os estilos, catalogo fechado). O DONO so pode travar (regra fica na posicao) ou vetar (pet nao pode
   usar). Lutas, travas e vetos entram no registro: o replay reconstroi o aprendizado. */
import { CCF, CED, CESC, CLE, CSO, CV, CV21, CV21E_TR, GA, SOMBRIA, TECNICAS, baseDe } from "./constantes.ts";
import {
  ADOL_V21, BOTS_V2, BOTS_V21, BOTS_V21D, BOTS_V21E, CRIANCA_V21, GAMBITS_SOMBRIA, LISTAS_V14, NOME_BOT, NPC, REGRA_BATE_EM_QUEM_RECUA, REGRA_CONTRA_GOLPE_NA_PELE,
  REGRA_DEFENDE_DO_GOLPE, REGRA_RECUA_DO_PREPARO_SOB_PELE, copiarGambits,
  estiloBot, formaRival, gambitNPC, gambitsAdulto,
} from "./bots.ts";
import type { Arena } from "./arenas.ts";
import { epsilonConfianca, type ConfiancaCombate } from "./confianca.ts";
import { ESCALA, caraterCanonico, escalaDaVersao, escalaDe, perfilDe, perfilNPC, perfilNeutro, tecnicaDe } from "./catalogo.ts";
import { CONDICOES_ESTAGIO, DIST, type Cond, type Estilo, type ListaGambits, type Lutador, type Regra, type RegrasLuta, type ResultadoLuta } from "./combate.ts";
import { NOME_V2, nomeFormaLegado } from "./nomes.ts";
import { criarRng, hashSemente } from "./rng.ts";
import { PASSO_TR_MS, T_TR } from "./combate_tr/constantes_tr.ts";
import { condicaoDe, type TreinoPet } from "./treino.ts";
import { ITENS } from "./itens.ts";
import type { Carater, Forma, FormaAdultaNormal, OpGambit, Stats } from "./tipos.ts";

export const chaveRegra = (r: Regra): string => JSON.stringify([r.se.map(c => [c.n, c.p]), r.entao]);
export const REPERTORIO: Map<string, Regra> = (() => {
  const m = new Map<string, Regra>();
  const listas = [...["agressivo", "tartaruga", "atirador", "contragolpe", "adaptativo"].map(n => BOTS_V2[n]),
    ...Object.values(CRIANCA_V21), ...Object.values(ADOL_V21), ...Object.values(BOTS_V21)];
  for (const g of listas) for (const r of g.regras) if (!m.has(chaveRegra(r))) m.set(chaveRegra(r), r);
  return m;
})();
/** regra que a forma pode usar: condicoes do estagio (o vigia tambem ve o pesado vindo) e so a tecnica da propria linha */
export function permitida(r: Regra, f: Forma): boolean {
  const conds = CONDICOES_ESTAGIO[f.est] || [];
  if (!r.se.every(c => conds.includes(c.n) || (c.n === "oponente_vai_preparar" && f.adulta === "vigia"))) return false;
  return !(TECNICAS as readonly string[]).includes(r.entao) || r.entao === tecnicaDe(f);
}
/** semente da forma; R = CV21D (pets v6-v8): a muralha e o vigia adultos semeiam as listas variantes; R = CV21E (pets v9): tambem o
    duelista, o tita, o espelho e a muralha (bots.gambitsAdulto) */
export function sementeDe(f: Forma, R: RegrasLuta = CV21E_TR): ListaGambits {
  return f.est === "crianca" ? CRIANCA_V21[f.ramo!] : f.est === "adolescente" ? ADOL_V21[f.linha!]
    : (BOTS_V21[f.adulta as FormaAdultaNormal] && gambitsAdulto(f.adulta as FormaAdultaNormal, R)) || GAMBITS_SOMBRIA[f.adulta!] || BOTS_V21[SOMBRIA[f.adulta!]!.base];
}
/* regra pela chave: o repertorio (de onde o pet tira candidatas) ou, fora dele, a semente de uma sombria (a
   do devastador tem "perto e guts >= 60 -> preparar pesado", que nenhum bot usa), do vigia V21D (as duas regras novas
   do reequilibrio, so na semente dos pets v6), das listas V21E (as regras novas do equilibrio geral, so na semente dos pets v9) ou de
   um chip de regra (itens.ts; pets v6). O repertorio nao muda: as candidatas e o replay dos pets v1-v8 ficam iguais. Nos pets v6 o
   vigia recebe as duas regras novas tambem como candidatas de troca (candidatasDoVigia), e nos pets v9 o duelista, o tita e a muralha
   as da V21E (candidatasV21E); as regras dos chips nunca viram candidatas (so entram pelo chip). As das listas candidatas da rodada de
   equilibrio do tempo real (bots.LISTAS_V14, ainda de nenhuma versao) tambem tem chave aqui: nenhum pet de hoje as tem na semente nem nas
   candidatas, entao so a bancada as usa. */
let REGRAS_SEMENTE: Map<string, Regra> | null = null;
export function regraDe(k: string): Regra {
  const r = REPERTORIO.get(k);
  if (r) return r;
  REGRAS_SEMENTE ??= new Map([...Object.values(GAMBITS_SOMBRIA), ...Object.values(BOTS_V21D) as ListaGambits[], ...Object.values(BOTS_V21E) as ListaGambits[], ...Object.values(LISTAS_V14),
    { regras: ITENS.flatMap(x => x.tipo === "chip_regra" ? [x.regra] : []), final: "defender" }]
    .flatMap(g => g.regras.map(x => [chaveRegra(x), x] as [string, Regra])));
  if (!REGRAS_SEMENTE.has(k)) throw new Error("regra fora do repertório: " + k);
  return REGRAS_SEMENTE.get(k)!;
}
export function rotuloCond(c: Cond): string {
  const p = c.p;
  switch (c.n) {
    case "sempre": return "sempre";
    case "distancia_eh": return `distância é ${DIST[p[0] as number]}`;
    case "hp_proprio_abaixo": return `minha vida < ${(p[0] as number) * 100}%`;
    case "guts_proprio_abaixo": return `meu guts < ${p[0]}`;
    case "guts_proprio_acima": return `meu guts ≥ ${p[0]}`;
    case "oponente_preparando": return "oponente preparando pesado";
    case "oponente_hp_abaixo": return `vida do oponente < ${(p[0] as number) * 100}%`;
    case "oponente_guts_abaixo": return `guts do oponente < ${p[0]}`;
    case "oponente_repete": return `oponente repetiu ${NOME_V2[p[0] as string]} ${p[1]}x`;
    case "oponente_frequente": return `oponente insiste em ${NOME_V2[p[0] as string]}`;
    /* o turno t e o relogio t x T_TR (combate_tr/controlador.ts): 2 s por turno */
    case "turno_execucao": return `luta com ${Number(p[0]) * T_TR * PASSO_TR_MS / 1000} s ou mais`;
    case "oponente_vai_preparar": return "vi o pesado vindo";
  }
  return c.n;
}
/** as duas regras novas do vigia V21D (bots.BOTS_V21D.vigia): nos pets v6 (regras V21D) elas voltam como candidatas de
    troca para a forma do vigia (Ultimate ou Mega). Sem isso, a primeira troca que as tirasse da lista as tiraria para sempre,
    porque o repertorio de candidatas nao as tem. So o vigia: nas outras formas as candidatas (e o replay) nao mudam */
export function candidatasDoVigia(f: Forma | null, R: RegrasLuta | null): string[] {
  if (!f || !R || f.adulta !== "vigia" || !R.vigiaBateEmQuemRecua || !R.vigiaRecuaDoPreparoSobPele) return [];
  return [REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE].map(chaveRegra).filter(k => !REPERTORIO.has(k));
}
/** as regras novas da V21E (bots.gambitsAdulto): nos pets v9 elas voltam como candidatas de troca para a forma que as tem na semente
    (o duelista e o tita, "defender do golpe rapido repetido"; a muralha, "contra-golpe em quem usa pele dura"), pelo mesmo motivo
    do vigia (candidatasDoVigia). Nas outras formas e nos pets v1-v8 as candidatas (e o replay) nao mudam */
export function candidatasV21E(f: Forma | null, R: RegrasLuta | null): string[] {
  if (!f || !R) return [];
  const novas = (f.adulta === "duelista" && R.duelistaDefendeDoGolpe) || (f.adulta === "tita" && R.titaDefendeDoGolpe) ? [REGRA_DEFENDE_DO_GOLPE]
    : f.adulta === "muralha" && R.muralhaContraGolpeNaPele ? [REGRA_CONTRA_GOLPE_NA_PELE] : [];
  return novas.map(chaveRegra).filter(k => !REPERTORIO.has(k));
}
export const rotuloRegra = (r: Regra): string => `se ${r.se.map(rotuloCond).join(" e ")} → ${NOME_V2[r.entao]}`;
/** a regra da lista que cobre o chip de regra `chip` (o chip entra no fim da lista de luta): a primeira cujas condicoes sao todas condicoes
    do chip, ou a propria regra do chip ja na lista. Sempre que o chip valeria, ela vale antes, e a primeira regra valida decide: o chip
    nunca decide. null = o chip pode decidir. So o aviso na tela (DE-3, decidida pelo Matheus em 2026-10-30): a lista e as lutas nao mudam */
export function regraQueCobre(lista: readonly Regra[], chip: Regra): Regra | null {
  const k = chaveRegra(chip), conds = new Set(chip.se.map(c => JSON.stringify([c.n, c.p])));
  return lista.find(r => chaveRegra(r) === k || r.se.every(c => conds.has(JSON.stringify([c.n, c.p])))) ?? null;
}

export interface MudancaGambit { luta: number; texto: string; dono?: boolean }

export class GambitsPet {
  notas: Record<string, number> = {};
  disparos: Record<string, number> = {};
  ativas: string[] = [];
  final = "defender";
  linha: string | null = null;
  forma: Forma | null = null;
  travas: Record<string, number> = {};
  vetos: string[] = [];
  mudancas: MudancaGambit[] = [];
  nLutas = 0;
  versao = 0;
  /** pets v6: as regras dos chips de regra equipados (itens.ts; evento "i" do pet). O pet nao as troca enquanto o chip estiver
      equipado; o dono pode travar, nao vetar */
  chipsRegra: string[] = [];
  /** as regras de chip que ja estavam na lista quando o chip entrou: ao desequipar, ficam (so perdem a protecao) */
  chipsJaAtivos: string[] = [];
  /** algum chip de regra ja entrou: so entao os chips entram na assinatura (a dos pets sem item nao muda) */
  usouChip = false;
  /** pets v9 (itens.ts, rodada de equilibrio geral fase 3): o chip de regra nao entra na lista (ativas); a regra dele vai para o fim da lista
      com que o pet luta (comChips), sem tirar nenhuma, e o pet nao a reordena nem a troca. O motor liga ao criar (sai da versao; nao entra
      na assinatura) */
  chipsNoFim = false;
  /** regras das lutas do pet (a da ultima semeadura): CV21E_TR nos pets v13; null antes da primeira semeadura. Nao entra na assinatura: sai
      da versao */
  regras: RegrasLuta | null = null;
  /** evolucao: a semente da forma nova entra com nota-base pela posicao; o que ja foi aprendido fica; a
      lista cabe na capacidade do estagio. `base`: a lista de partida (a semente da forma; a bancada da rodada de equilibrio passa as
      candidatas, bots.LISTAS_V14) */
  semear(forma: Forma, nome: string = nomeFormaLegado(forma), R: RegrasLuta = CV21E_TR, base: ListaGambits = sementeDe(forma, R)): void {
    const cap = CV21.maxRegras[baseDe(forma.est)];
    this.forma = { ...forma }; this.linha = nome; this.final = base.final; this.regras = R;
    const novas: string[] = [];
    base.regras.forEach((r, i) => {
      const k = chaveRegra(r), nb = GA.base * (1 - i / cap);
      this.notas[k] = k in this.notas ? Math.max(this.notas[k], nb) : nb;
      if (!this.vetos.includes(k)) novas.push(k);
    });
    for (const k of Object.keys(this.travas)) if (!novas.includes(k) && REPERTORIO.has(k) && permitida(REPERTORIO.get(k)!, forma)) novas.push(k);
    /* pets v6: as regras dos chips equipados continuam na lista da forma nova (na frente, para o corte da capacidade nao tira-las); nos v9
       elas ficam fora da lista (comChips) */
    if (!this.chipsNoFim) for (const k of [...this.chipsRegra].reverse()) if (permitida(regraDe(k), forma)) { const i = novas.indexOf(k); if (i >= 0) novas.splice(i, 1); novas.unshift(k); }
    this.ativas = novas.slice(0, cap);
    for (const k of Object.keys(this.travas)) if (!this.ativas.includes(k)) delete this.travas[k];
    this.mudancas.push({ luta: this.nLutas, texto: `evoluiu para ${this.linha}: a forma semeou a lista (até ${cap} regras)` });
    this.ordenar(); this.versao++;
  }
  /** pets v5: o Ultimate virou Mega. A forma e a mesma, entao a lista aprendida fica como esta (nao semeia de novo) */
  promover(forma: Forma, nome: string): void {
    this.forma = { ...forma }; this.linha = nome;
    this.mudancas.push({ luta: this.nLutas, texto: `evoluiu para ${nome}: a lista aprendida continua` });
    this.versao++;
  }
  ordenar(): void {
    const n = this.ativas.length, fixas: Record<number, string> = {}, livres: string[] = [];
    for (const k of this.ativas) if (!(k in this.travas)) livres.push(k);
    for (const [k, i] of Object.entries(this.travas).sort((a, b) => a[1] - b[1])) {
      if (!this.ativas.includes(k)) continue;
      let j = Math.min(i, n - 1);
      while (j in fixas) j = (j + 1) % n;          /* duas travas na mesma posicao: a segunda vai para a proxima livre */
      fixas[j] = k;
    }
    livres.sort((a, b) => (this.notas[b] - this.notas[a]) || (this.ativas.indexOf(a) - this.ativas.indexOf(b)));
    const saida: (string | undefined)[] = [];
    for (let i = 0; i < n; i++) saida.push(i in fixas ? fixas[i] : livres.shift());
    this.ativas = saida.filter(Boolean) as string[];
  }
  /** candidatas de troca: regras que o pet ainda nao usa, nao vetadas e permitidas na forma. O repertorio, na ordem dele; nos
      pets v6 com a forma do vigia, mais as duas regras novas do vigia V21D (no fim, para a ordem das outras nao mudar) */
  candidatas(): string[] {
    return [...REPERTORIO.keys(), ...candidatasDoVigia(this.forma, this.regras), ...candidatasV21E(this.forma, this.regras)]
      .filter(k => !this.ativas.includes(k) && !this.vetos.includes(k) && permitida(regraDe(k), this.forma!));
  }
  estilo(): Estilo { return { nome: "aprendido", gambits: { regras: this.ativas.map(regraDe), final: this.final }, eps: CV.eps }; }
  /** Lago (regra de vinculo, arenas.ts): a lista que o pet usaria sem o dono. Sem as travas (so a nota dele ordena) e com as
      regras vetadas de volta (as que ele conhece, com nota, e a forma permite), cortada na capacidade do estagio. Sem trava e
      sem veto, e a lista de sempre (a ativa ja esta na ordem da nota) */
  listaSozinho(): string[] {
    const cap = CV21.maxRegras[baseDe(this.forma!.est)];
    const ks = [...this.ativas, ...this.vetos.filter(k => k in this.notas && !this.ativas.includes(k) && permitida(regraDe(k), this.forma!))];
    return ks.map((k, i) => ({ k, i })).sort((a, b) => (this.notas[b.k] - this.notas[a.k]) || (a.i - b.i)).slice(0, cap).map(x => x.k);
  }
  /** Palacio da Fronteira (instalacoes.ts): a lista que o pet faria sozinho, sem o dono e sem os chips. A do Lago (listaSozinho: sem
      as travas, com as vetadas de volta) menos as regras que so estao no pet por um chip de regra. A regra de chip que ja estava na lista
      quando o chip entrou (chipsJaAtivos) e do pet: fica, como fica ao desequipar. Sem chip de regra, e a do Lago */
  listaPalacio(): string[] {
    const soDoChip = this.chipsRegra.filter(k => !this.chipsJaAtivos.includes(k));
    if (!soDoChip.length) return this.listaSozinho();
    const cap = CV21.maxRegras[baseDe(this.forma!.est)];
    const ks = [...this.ativas, ...this.vetos.filter(k => k in this.notas && !this.ativas.includes(k) && permitida(regraDe(k), this.forma!))]
      .filter(k => !soDoChip.includes(k));
    return ks.map((k, i) => ({ k, i })).sort((a, b) => (this.notas[b.k] - this.notas[a.k]) || (a.i - b.i)).slice(0, cap).map(x => x.k);
  }
  /* ---------------------------------------------------------------- chips de regra (pets v6; itens.ts) */
  /** pets v9: a lista `base` com as regras dos chips equipados no fim (as que ja estao nela ficam onde estao; so as que a forma permite).
      Nos v6-v8 (chipsNoFim falso) os chips ja estao na lista: `base` como esta */
  comChips(base: readonly string[]): string[] {
    if (!this.chipsNoFim || !this.forma) return base.slice();
    return [...base, ...this.chipsRegra.filter(k => !base.includes(k) && permitida(regraDe(k), this.forma!))];
  }
  /** por que a regra do chip nao pode entrar agora (null: pode). A regra entra no topo; com a lista cheia sai a regra livre (nao
      travada e nao de chip) de nota mais baixa */
  porqueNaoEquipaRegra(k: string): string | null {
    if (!this.forma) return "o pet ainda não tem regras de combate";
    if (this.chipsRegra.includes(k)) return "esta regra já está no pet por um chip";
    if (this.vetos.includes(k)) return "você vetou esta regra: libere o veto antes";
    if (!permitida(regraDe(k), this.forma)) return "a regra usa condições que esta forma ainda não tem";
    const cap = CV21.maxRegras[baseDe(this.forma.est)];
    if (!this.chipsNoFim && !this.ativas.includes(k) && this.ativas.length >= cap && !this.ativas.some(x => !(x in this.travas) && !this.chipsRegra.includes(x)))
      return "a lista está cheia de regras travadas e de chips: destrave uma antes";
    return null;
  }
  equiparRegra(k: string, nome: string): void {
    const erro = this.porqueNaoEquipaRegra(k);
    if (erro) throw new Error(erro);
    if (this.chipsNoFim) {
      /* pets v9: fica fora da lista, no fim da lista de luta (comChips); a nota comeca em 0 (o aprendizado mexe nela como nas outras) */
      if (!(k in this.notas)) this.notas[k] = 0;
      this.chipsRegra.push(k); this.usouChip = true;
      this.mudancas.push({ luta: this.nLutas, texto: `${nome}: “${rotuloRegra(regraDe(k))}” entrou no fim da lista`, dono: true });
      this.versao++;
      return;
    }
    const cap = CV21.maxRegras[baseDe(this.forma!.est)], ja = this.ativas.includes(k);
    if (ja) this.ativas.splice(this.ativas.indexOf(k), 1);
    else if (this.ativas.length >= cap) {
      /* sai a livre de nota mais baixa (empate: a mais abaixo na lista) */
      const livres = this.ativas.filter(x => !(x in this.travas) && !this.chipsRegra.includes(x));
      const nota = (x: string) => this.notas[x] ?? 0;
      const pior = livres.reduce((a, b) => nota(b) < nota(a) || (nota(b) === nota(a) && this.ativas.indexOf(b) > this.ativas.indexOf(a)) ? b : a);
      this.ativas.splice(this.ativas.indexOf(pior), 1);
    }
    /* no topo: a nota da melhor da lista (no empate vale a ordem da lista, e ela fica na frente) */
    this.notas[k] = Math.max(GA.base, ...this.ativas.map(x => this.notas[x] ?? 0));
    this.ativas.unshift(k);
    this.chipsRegra.push(k); if (ja) this.chipsJaAtivos.push(k);
    this.usouChip = true;
    this.mudancas.push({ luta: this.nLutas, texto: `${nome}: “${rotuloRegra(regraDe(k))}” entrou na lista`, dono: true });
    this.ordenar(); this.versao++;
  }
  desequiparRegra(k: string, nome: string): void {
    const i = this.chipsRegra.indexOf(k);
    if (i < 0) throw new Error("esta regra não está no pet por um chip");
    this.chipsRegra.splice(i, 1);
    if (this.chipsNoFim) {
      this.mudancas.push({ luta: this.nLutas, texto: `${nome} saiu: “${rotuloRegra(regraDe(k))}” saiu do fim da lista`, dono: true });
      this.versao++;
      return;
    }
    const ja = this.chipsJaAtivos.indexOf(k);
    if (ja >= 0) this.chipsJaAtivos.splice(ja, 1);
    else {
      delete this.travas[k];
      const j = this.ativas.indexOf(k);
      if (j >= 0) {
        /* a vaga volta para a melhor candidata (como no veto) */
        const cands = this.candidatas().filter(x => x !== k).sort((a, b) => (this.notas[b] ?? 0) - (this.notas[a] ?? 0));
        if (cands.length) { this.ativas[j] = cands[0]; if (!(cands[0] in this.notas)) this.notas[cands[0]] = 0; }
        else this.ativas.splice(j, 1);
      }
    }
    this.mudancas.push({ luta: this.nLutas, texto: `${nome} saiu: “${rotuloRegra(regraDe(k))}”${ja >= 0 ? " fica, sem a proteção do chip" : " saiu da lista"}`, dono: true });
    this.ordenar(); this.versao++;
  }
  /** `usadas`: as regras da lista com que o pet lutou, na ordem (o indice do motivo de cada turno aponta para ela); por padrao
      as ativas. Na arena do Lago e a listaSozinho; nas lutas seguidas da Cidadela, a lista do comeco da serie */
  /** `novidade` (pets v8, M1): o passo de aprendizado e GA.alfa * novidade; 1 = o passo de sempre (v1-v7) */
  aprender(res: ResultadoLuta, semente: number, usadas: string[] = this.ativas.slice(), novidade: number = 1): void {
    if (!(novidade > 0 && novidade <= 1)) throw new Error("novidade fora de (0, 1]: " + novidade);
    this.nLutas++;
    const soma: Record<string, number> = {}, cont: Record<string, number> = {};
    /* a luta em tempo real (pets v13): cada acao do pet conta, com o saldo dela ja sobre a vida do comeco (combate_tr) */
    for (const a of res.tr.acoes) {
      if (a.lado !== 0 || typeof a.motivo !== "number" || a.motivo >= usadas.length) continue;
      const k = usadas[a.motivo];
      soma[k] = (soma[k] || 0) + a.saldo; cont[k] = (cont[k] || 0) + 1;
    }
    const bonus = GA.bonusResultado * (res.pontosA - .5), alfa = GA.alfa * novidade;
    for (const k of Object.keys(cont)) {
      this.notas[k] += alfa * (soma[k] / cont[k] + bonus - this.notas[k]);
      this.disparos[k] = (this.disparos[k] || 0) + cont[k];
    }
    /* o pet propoe: a pior regra livre abaixo do limiar da lugar a uma candidata */
    const livres = this.ativas.filter(k => !(k in this.travas) && !this.chipsRegra.includes(k));
    const pior = livres.sort((a, b) => this.notas[a] - this.notas[b])[0];
    const candidatas = this.candidatas();
    if (pior && this.notas[pior] < GA.limiarTroca && candidatas.length) {
      const nova = candidatas[criarRng(hashSemente("propor", semente)).int(candidatas.length)];
      this.ativas[this.ativas.indexOf(pior)] = nova;
      if (!(nova in this.notas)) this.notas[nova] = 0;
      this.mudancas.push({ luta: this.nLutas, texto: `trocou “${rotuloRegra(regraDe(pior))}” (nota ${this.notas[pior].toFixed(3)}) por “${rotuloRegra(regraDe(nova))}”` });
    }
    this.ordenar(); this.versao++;
  }
  intervir(op: OpGambit, k: string): void {
    regraDe(k);                                  /* falha alto se a regra nao existe */
    if (op === "travar") { const i = this.ativas.indexOf(k); if (i < 0) throw new Error("só dá para travar regra ativa"); this.travas[k] = i; }
    else if (op === "destravar") delete this.travas[k];
    else if (op === "vetar") {
      if (this.chipsRegra.includes(k)) throw new Error("esta regra vem de um chip: para tirá-la, desequipe o chip");
      if (!this.vetos.includes(k)) this.vetos.push(k);
      delete this.travas[k];
      const i = this.ativas.indexOf(k);
      if (i >= 0) {
        const cands = this.candidatas().sort((a, b) => (this.notas[b] ?? 0) - (this.notas[a] ?? 0));
        if (cands.length) { this.ativas[i] = cands[0]; if (!(cands[0] in this.notas)) this.notas[cands[0]] = 0; }
        else this.ativas.splice(i, 1);
      }
    }
    else if (op === "liberar") this.vetos = this.vetos.filter(v => v !== k);
    else throw new Error("intervenção desconhecida: " + op);
    this.mudancas.push({ luta: this.nLutas, texto: `você: ${op} “${rotuloRegra(regraDe(k))}”`, dono: true });
    this.ordenar(); this.versao++;
  }
  assinatura(): unknown[] {
    return [this.notas, this.disparos, this.ativas, this.final, this.linha, this.forma, this.travas, this.vetos, this.nLutas,
      ...(this.usouChip ? [[this.chipsRegra, this.chipsJaAtivos]] : [])];
  }
}

/** o que o motor precisa do pet para montar o lutador */
export interface PetLutador {
  gp: GambitsPet | null; forma: Forma; versao: number; e: { saude: number; tick: number }; treino: TreinoPet; carater(): Carater | null;
  disciplina?: number; vitoriasVida?: number;
  /** o treino com que ele luta (pets v6: com os chips de stat, itens.ts); sem isto, o treino dele */
  pontosDeLuta?(): Stats | null;
  /** v8 (M1): a confianca de combate; a inseguranca sobe o epsilon */
  conf?: ConfiancaCombate | null;
  /** pets v9 (itens.ts): os chips de regra fazem efeito agora (o treino minimo)? Sem isto, nao ha chip no fim da lista */
  chipsValem?(): boolean;
}
export function estiloDoPet(m: PetLutador): Estilo {
  const e: Estilo = m.gp ? { ...m.gp.estilo(), base: m.gp.linha! } : { ...estiloBot("aleatorio"), base: "aleatorio" };
  /* pets v9: as regras dos chips no fim da lista, se os itens valem (o treino minimo) */
  if (m.gp?.chipsNoFim && m.gp.chipsRegra.length && m.chipsValem?.()) e.gambits = { regras: m.gp.comChips(m.gp.ativas).map(regraDe), final: m.gp.final };
  if (SOMBRIA[m.forma.adulta!]) e.eps = Math.max(e.eps, CSO.epsMin);   /* sombria: instavel */
  /* v4: sem educacao ele ignora os proprios gambits mais vezes (PLANO_ANALISE_V3, secao 2.2) */
  /* e a experiencia de combate (estilo "lutar"): cada vitoria tira um pouco, ate expMax; nunca abaixo de 0 */
  if (m.versao >= 4) e.eps = Math.max(0, e.eps + (1 - (m.disciplina ?? 0) / CED.disciplinaMax) * CED.deltaEps
    - Math.min(CLE.expMax, (m.vitoriasVida ?? 0) * CLE.expPorVitoria));
  /* v8 (M1, espelho de educacao.epsilon_pet): inseguro hesita e erra mais; a confianca positiva nao reduz */
  if (m.versao >= 8 && m.conf) e.eps += epsilonConfianca(m.conf.valor(m.e.tick), CCF.kappaEps);
  return e;
}
/** lutador do pet (so o que a luta usa; sprite, cor e grade sao da interface) */
export function lutadorPet(m: PetLutador, rotulo: string, absoluto = false): Lutador {
  return {
    nome: rotulo, estilo: estiloDoPet(m), sombra: !!SOMBRIA[m.forma.adulta!],
    cond: perfilDe(m.forma, m.carater(), m.versao >= 2 ? condicaoDe(m.e.saude) : 1,
      m.pontosDeLuta ? m.pontosDeLuta() : m.treino.total > 0 ? m.treino.pontos : null, absoluto, m.versao),
  };
}
/** lutador de um bot: NPC da campanha, forma adulta canonica da V2.1 ou bot classico (stats neutros); R = regras da
    luta (a muralha e o vigia com as listas variantes); arena = o NPC e o lider e a luta e de arena
    (pets v6, arenas.arenaDaLuta): o fator calibrado do lider e, na Torre de pedra, o contra-golpe */
export function lutadorBot(nome: string, R: RegrasLuta = CV21E_TR, arena: Arena | null = null): Lutador {
  const n = NPC[nome];
  if (n) {
    if (arena && arena.lider !== nome) throw new Error(`${n.nome} não é o líder da arena ${arena.id}`);
    const tec = arena?.tecnica ?? null, base = estiloBot(nome, R);
    const estilo = arena?.lista ? { ...base, gambits: copiarGambits(gambitNPC("arena:" + arena.lista)) }
      : tec ? { ...base, gambits: copiarGambits(gambitNPC(n.estilo, R, tec)) } : base;
    /* campanha na escala: E = vida do estagio sugerido (ou do Mega, na Montanha Espiral) x fator; epsilon da escala. Nas lutas
       do pet (as regras da luta dizem a versao) a escala e a CESC_V9 e o desafiante tem o fator dela */
    if (ESCALA.ligada) {
      const versao = R.versaoPet, fator = arena?.fator ?? escalaDaVersao(versao).fatorNpc[nome] ?? n.fator ?? CESC.fatorNpc[nome];
      if (fator === undefined) throw new Error(`${n.nome} sem fator de escala`);
      return { nome: "Rival " + n.nome, estilo: { ...estilo, eps: CESC.epsNpc }, cond: perfilNPC(n.total, n.estagio || "adulto", escalaDe(n.est, 0, versao) * fator, tec) };
    }
    return { nome: "Rival " + n.nome, estilo, cond: perfilNPC(n.total, n.estagio || "adulto", undefined, tec) };
  }
  if (BOTS_V21[nome as FormaAdultaNormal]) {
    const f = formaRival(nome as FormaAdultaNormal);
    return { nome: "Rival " + nomeFormaLegado(f), estilo: estiloBot(nome, R), cond: perfilDe(f, caraterCanonico(nome as FormaAdultaNormal)) };
  }
  return { nome: "Rival " + NOME_BOT[nome], estilo: estiloBot(nome), cond: perfilNeutro() };
}
