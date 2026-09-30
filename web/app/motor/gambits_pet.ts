/* Gambits do pet: hibrido (PROVISORIO, so na web).
   O PET propoe e aprende: a linha evolutiva semeia a lista; depois de cada luta contra bot, cada regra que
   disparou tem a nota puxada para o saldo de dano dos turnos em que agiu (+ bonus pelo resultado); a lista
   se reordena pela nota; uma regra ativa com nota ruim e trocada por uma candidata do repertorio (regras de
   todos os estilos, catalogo fechado). O DONO so pode travar (regra fica na posicao) ou vetar (pet nao pode
   usar). Lutas, travas e vetos entram no registro: o replay reconstroi o aprendizado. */
import { CED, CESC, CESC_V6, CLE, CSO, CV, CV21, GA, SOMBRIA, TECNICAS, baseDe } from "./constantes.ts";
import {
  ADOL_V21, BOTS_V2, BOTS_V21, BOTS_V21D, CRIANCA_V21, GAMBITS_SOMBRIA, NOME_BOT, NPC, REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE, copiarGambits,
  estiloBot, formaRival, gambitNPC, gambitsAdulto,
} from "./bots.ts";
import type { Arena } from "./arenas.ts";
import { ESCALA, caraterCanonico, escalaDe, perfilDe, perfilNPC, perfilNeutro, tecnicaDe } from "./catalogo.ts";
import { CONDICOES_ESTAGIO, DIST, type Cond, type Estilo, type ListaGambits, type Lutador, type Regra, type RegrasLuta, type ResultadoLuta } from "./combate.ts";
import { NOME_V2, nomeFormaLegado } from "./nomes.ts";
import { criarRng, hashSemente } from "./rng.ts";
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
/** semente da forma; R = CV21D (pets v6): a muralha e o vigia adultos semeiam as listas variantes */
export function sementeDe(f: Forma, R: RegrasLuta = null): ListaGambits {
  return f.est === "crianca" ? CRIANCA_V21[f.ramo!] : f.est === "adolescente" ? ADOL_V21[f.linha!]
    : (BOTS_V21[f.adulta as FormaAdultaNormal] && gambitsAdulto(f.adulta as FormaAdultaNormal, R)) || GAMBITS_SOMBRIA[f.adulta!] || BOTS_V21[SOMBRIA[f.adulta!]!.base];
}
/* regra pela chave: o repertorio (de onde o pet tira candidatas) ou, fora dele, a semente de uma sombria (a
   do devastador tem "perto e guts >= 60 -> preparar pesado", que nenhum bot usa), do vigia V21D (as duas regras novas
   do reequilibrio, so na semente dos pets v6) ou de um chip de regra (itens.ts; pets v6). O repertorio nao muda: as candidatas e o
   replay dos pets v1-v5 ficam iguais. Nos pets v6 o vigia recebe as duas regras novas tambem como candidatas de troca
   (candidatasDoVigia); as regras dos chips nunca viram candidatas (so entram pelo chip). */
let REGRAS_SEMENTE: Map<string, Regra> | null = null;
export function regraDe(k: string): Regra {
  const r = REPERTORIO.get(k);
  if (r) return r;
  REGRAS_SEMENTE ??= new Map([...Object.values(GAMBITS_SOMBRIA), ...Object.values(BOTS_V21D) as ListaGambits[],
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
    case "turno_execucao": return `luta no turno ${p[0]} ou mais`;
    case "oponente_vai_preparar": return "vi o pesado vindo";
  }
  return c.n;
}
/** as duas regras novas do vigia V21D (bots.BOTS_V21D.vigia): nos pets v6 (regras V21D) elas voltam como candidatas de
    troca para a forma do vigia (Ultimate ou Mega). Sem isso, a primeira troca que as tirasse da lista as tiraria para sempre,
    porque o repertorio de candidatas nao as tem. So o vigia: nas outras formas as candidatas (e o replay) nao mudam */
export function candidatasDoVigia(f: Forma | null, R: RegrasLuta): string[] {
  if (!f || f.adulta !== "vigia" || !R?.vigiaBateEmQuemRecua || !R.vigiaRecuaDoPreparoSobPele) return [];
  return [REGRA_BATE_EM_QUEM_RECUA, REGRA_RECUA_DO_PREPARO_SOB_PELE].map(chaveRegra).filter(k => !REPERTORIO.has(k));
}
export const rotuloRegra = (r: Regra): string => `se ${r.se.map(rotuloCond).join(" e ")} → ${NOME_V2[r.entao]}`;

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
  /** regras das lutas do pet (a da ultima semeadura): CV21D nos pets v6, null nos v1-v5. Nao entra na assinatura: sai da versao */
  regras: RegrasLuta = null;
  /** evolucao: a semente da forma nova entra com nota-base pela posicao; o que ja foi aprendido fica; a
      lista cabe na capacidade do estagio */
  semear(forma: Forma, nome: string = nomeFormaLegado(forma), R: RegrasLuta = null): void {
    const base = sementeDe(forma, R), cap = CV21.maxRegras[baseDe(forma.est)];
    this.forma = { ...forma }; this.linha = nome; this.final = base.final; this.regras = R;
    const novas: string[] = [];
    base.regras.forEach((r, i) => {
      const k = chaveRegra(r), nb = GA.base * (1 - i / cap);
      this.notas[k] = k in this.notas ? Math.max(this.notas[k], nb) : nb;
      if (!this.vetos.includes(k)) novas.push(k);
    });
    for (const k of Object.keys(this.travas)) if (!novas.includes(k) && REPERTORIO.has(k) && permitida(REPERTORIO.get(k)!, forma)) novas.push(k);
    /* pets v6: as regras dos chips equipados continuam na lista da forma nova (na frente, para o corte da capacidade nao tira-las) */
    for (const k of [...this.chipsRegra].reverse()) if (permitida(regraDe(k), forma)) { const i = novas.indexOf(k); if (i >= 0) novas.splice(i, 1); novas.unshift(k); }
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
    return [...REPERTORIO.keys(), ...candidatasDoVigia(this.forma, this.regras)]
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
  /** por que a regra do chip nao pode entrar agora (null: pode). A regra entra no topo; com a lista cheia sai a regra livre (nao
      travada e nao de chip) de nota mais baixa */
  porqueNaoEquipaRegra(k: string): string | null {
    if (!this.forma) return "o pet ainda não tem regras de combate";
    if (this.chipsRegra.includes(k)) return "esta regra já está no pet por um chip";
    if (this.vetos.includes(k)) return "você vetou esta regra: libere o veto antes";
    if (!permitida(regraDe(k), this.forma)) return "a regra usa condições que esta forma ainda não tem";
    const cap = CV21.maxRegras[baseDe(this.forma.est)];
    if (!this.ativas.includes(k) && this.ativas.length >= cap && !this.ativas.some(x => !(x in this.travas) && !this.chipsRegra.includes(x)))
      return "a lista está cheia de regras travadas e de chips: destrave uma antes";
    return null;
  }
  equiparRegra(k: string, nome: string): void {
    const erro = this.porqueNaoEquipaRegra(k);
    if (erro) throw new Error(erro);
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
  aprender(res: ResultadoLuta, semente: number, usadas: string[] = this.ativas.slice()): void {
    this.nLutas++;
    const soma: Record<string, number> = {}, cont: Record<string, number> = {};
    for (const tr of res.turnos) {
      if (typeof tr.ma !== "number" || tr.ma >= usadas.length) continue;
      const k = usadas[tr.ma], saldo = (tr.dano[1] - tr.dano[0]) / res.E0.L[0].hpMax;
      soma[k] = (soma[k] || 0) + saldo; cont[k] = (cont[k] || 0) + 1;
    }
    const bonus = GA.bonusResultado * (res.pontosA - .5);
    for (const k of Object.keys(cont)) {
      this.notas[k] += GA.alfa * (soma[k] / cont[k] + bonus - this.notas[k]);
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
  gp: GambitsPet | null; forma: Forma; versao: number; e: { saude: number }; treino: TreinoPet; carater(): Carater | null;
  disciplina?: number; vitoriasVida?: number;
  /** o treino com que ele luta (pets v6: com os chips de stat, itens.ts); sem isto, o treino dele */
  pontosDeLuta?(): Stats | null;
}
export function estiloDoPet(m: PetLutador): Estilo {
  const e: Estilo = m.gp ? { ...m.gp.estilo(), base: m.gp.linha! } : { ...estiloBot("aleatorio"), base: "aleatorio" };
  if (SOMBRIA[m.forma.adulta!]) e.eps = Math.max(e.eps, CSO.epsMin);   /* sombria: instavel */
  /* v4: sem educacao ele ignora os proprios gambits mais vezes (PLANO_ANALISE_V3, secao 2.2) */
  /* e a experiencia de combate (estilo "lutar"): cada vitoria tira um pouco, ate expMax; nunca abaixo de 0 */
  if (m.versao >= 4) e.eps = Math.max(0, e.eps + (1 - (m.disciplina ?? 0) / CED.disciplinaMax) * CED.deltaEps
    - Math.min(CLE.expMax, (m.vitoriasVida ?? 0) * CLE.expPorVitoria));
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
    luta (CV21D contra um pet v6: a muralha e o vigia com as listas variantes); arena = o NPC e o lider e a luta e de arena
    (pets v6, arenas.arenaDaLuta): o fator calibrado do lider e, na Torre de pedra, o contra-golpe */
export function lutadorBot(nome: string, R: RegrasLuta = null, arena: Arena | null = null): Lutador {
  const n = NPC[nome];
  if (n) {
    if (arena && arena.lider !== nome) throw new Error(`${n.nome} não é o líder da arena ${arena.id}`);
    const tec = arena?.tecnica ?? null, base = estiloBot(nome, R);
    const estilo = arena?.lista ? { ...base, gambits: copiarGambits(gambitNPC("arena:" + arena.lista)) }
      : tec ? { ...base, gambits: copiarGambits(gambitNPC(n.estilo, R, tec)) } : base;
    /* campanha na escala: E = vida do estagio sugerido (ou do Mega, na Montanha Espiral) x fator; epsilon da escala. Nas lutas
       dos pets v6 (as regras da luta dizem a versao) a escala e a CESC_V6 e o desafiante tem o fator dela */
    if (ESCALA.ligada) {
      const versao = R?.versaoPet ?? 0, fator = arena?.fator ?? (versao >= CESC_V6.versaoPet ? CESC_V6.fatorNpc[nome] : undefined) ?? n.fator ?? CESC.fatorNpc[nome];
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
