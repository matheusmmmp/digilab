/* Motor com registro de eventos (espelho de engine.py + treino.py + personalidade). Event sourcing: o estado
   nunca e salvo, so o registro (acoes do dono, tempo, lutas, intervencoes, treinos); a vida e reconstruida
   reprocessando o registro. Mesma semente + mesmo registro = mesma assinatura, no mesmo runtime. */
import { CMEN,
  ACAO_CHAMADO, ACOES_DONO, ACOES_DONO_V4, ACOES_PET, CAT, CDJ, CED, CHAMADO_BEBE, CHE, CLE, CMG, EIXOS_TEMP, baseDe, COB, CSO, CT, CTR, C, DUR_CLASSICA, DUR_EVO, ESPECIES,
  TICK_INICIAL, VERSAO_PET,
} from "./constantes.ts";
import { Bandit } from "./bandit.ts";
import { NOME_BOT, NPC, campanhaDe, lugaresDe, type Lugar } from "./bots.ts";
import { MEDALHAS, medalhasPara } from "./medalhas.ts";
import { arenaDaLuta, jogarSequencia, jogarSerie, sementeDaSerie, type Arena } from "./arenas.ts";
import { LIGA, MEDALHAS_LIGA, RIVAL_LIGA, VERSAO_LIGA, lutadoresLiga, nomeMegaLiga } from "./liga.ts";
import {
  INSTALACOES, LUTAS_MAX_INSTALACAO, VERSAO_INSTALACOES, ehInstalacao, formaRivalInstalacao, instalacaoDe, rivalInstalacao, sementeTentativa,
  type IdInstalacao, type Instalacao,
} from "./instalacoes.ts";
import { ESTAGIOS_SALAO, RIVAL_SALAO, VERSAO_SALAO, formaRivalSalao, rivalSalao, sementeSalao } from "./salao.ts";
import { CIT } from "./constantes.ts";
import { cartaDe, chipDe, chipServe, estagioMinimo, pontosComChips, vagasDeChip } from "./itens.ts";
import { caraterDe, caraterPolitica, formaAdultaDe, linhaDoCarater, type QuandoCarater } from "./carater.ts";
import { desafiadoDaVersao, regrasDaVersao, type Lutador, type RegrasLuta, type ResultadoLuta, type Desafiado } from "./combate.ts";
import { ConfiancaCombate } from "./confianca.ts";
import { aplicarAcaoDono, avancarTick, clamp, efeitoAcaoPet, estadoInicial, observacao, temperamentoDe } from "./estado.ts";
import { GambitsPet, chaveRegra, lutadorBot, lutadorPet, regraDe, rotuloRegra } from "./gambits_pet.ts";
import { motivoVida } from "./motivo.ts";
import { NOME_EXERCICIO, nomeArquetipo, nomeForma } from "./nomes.ts";
import { criarRng, hashSemente, type Rng } from "./rng.ts";
import { TreinoPet, type ResultadoSessao } from "./treino.ts";
import { Vinculo, conflitoDono, termosObediencia } from "./vinculo.ts";
import type {
  AcaoDono, AcaoPet, Carater, Chamado, Desejo, Especie, Estagio, EstadoVida, EventoRegistro, Exercicio, Forma, FormaAdulta,
  EstagioTreino, ItemHistorico, Linha, MotivoVida, Observacao, OpGambit, OpItem, Origem, Ramo, Ritmo, Stats, Temperamento, VersaoPet,
} from "./tipos.ts";

/** medalhas do Tamer para uma evolucao (pets v6): tem X, precisa Y */
export interface RequisitoMedalhas { tem: number; precisa: number; ok: boolean }
/** a proxima evolucao do pet e o que falta: so os campos que a evolucao pede (lutas e taxa no Champion e no Mega; vinculo no Mega) */
export interface RequisitosEvolucao {
  alvo: Estagio; falta: number; tempo: boolean; lutas?: boolean; taxa?: boolean; vinculo?: boolean; medalhas: RequisitoMedalhas | null; pronto: boolean;
}
/** registro de uma evolucao (entra na assinatura) */
export interface Evolucao {
  tick: number; estagio: Estagio; ramo?: Ramo; cuidado?: number; linha?: Linha; adulta?: FormaAdulta; carater?: Carater;
  sparring?: number; sobrecarga?: number; forma: Forma;
  /** pets v5: Ultimate -> Mega (a forma adulta nao muda; vinculo na hora da evolucao) */
  vinculo?: number;
}
interface Chamados { abertos: Partial<Record<Chamado, number>>; atendidos: number; total: number }
interface RegistroDesejo { atual: { tick: number; tipo: Desejo["tipo"]; alvo: string } | null; vontades: number; cumpridas: number; abertas: [number, string][]; tVontade: number }

/** a luta como o motor a joga (Motor.montarLuta): os lutadores, a arena (pets v6 contra o lider; null fora dela), as regras
    do pet com que ele lutou (a lista ativa, ou a do Lago) e as lutas: uma, ou as seguidas da Cidadela (ate a primeira que
    nao for vitoria) */
export interface LutaMontada {
  A: Lutador; B: Lutador; arena: Arena | null; usadas: string[] | null; serie: ResultadoLuta[];
  /** pets v6, a Liga dos Lideres (liga.ts): os 6 rivais, na ordem (B e o primeiro); null fora dela */
  lideres: Lutador[] | null;
  /** pets v6: a carta do Tamer que valeu nesta luta (itens.ts; evento "k" logo antes da luta); null sem carta */
  carta: string | null;
  /** pets v6, uma instalacao da Fronteira (instalacoes.ts): qual, e os rivais sorteados das lutas jogadas, na ordem (B e o primeiro);
      null fora dela */
  instalacao: Instalacao | null;
  rivais: Lutador[] | null;
}
/** `res`: a ultima luta da serie (a unica, fora da Cidadela); `venceu`: todas as lutas da serie foram vitorias */
export interface ResultadoLutaPet extends LutaMontada { res: ResultadoLuta; venceu: boolean; lesao?: boolean }

/* ---------------------------------------------------------------- educacao-v1 (pets v4) */
/** janela de travessura aberta: o dono ve tipo e pedido, nunca se e falsa */
export interface Janela {
  tipo: "chamado" | "aviso" | "fala"; pedido: Chamado | "banheiro" | TemaFala; inicio: number; prazo: number; falso: boolean;
  /* so na janela de fala (pets v7): a mentira contradiz as barras? o gatilho, a honestidade e a chance na hora */
  contradiz?: boolean; gatilho?: string; h?: number; p?: number;
}
export type TemaFala = "estado" | "historia";
/** pets v7: estado da mentira (DESIGN_VOZ_PROPRIA, secao 9) */
export interface EstadoMentira { impunes: number; acertos: number }
export interface Educacao {
  disciplina: number; acertos: number; petiscos: number; janela: Janela | null; proximo: Partial<Record<Chamado, number>>;
  contagem: Record<string, number>;
}
/** as tentativas de um pet numa instalacao da Fronteira: quantas, a maior sequencia de vitorias e a da ultima */
export interface ContaInstalacao { tentativas: number; recorde: number; ultima: number }
export interface Lutas { lutas: number; vitorias: number; derrotas: number; empates: number; lesoes: number; tratadas: number }
export class PetMorto extends Error {}
const NIVEL_CHIP: Partial<Record<Estagio, string>> = { crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };
const nomeEstagioChip = (e: Estagio): string => NIVEL_CHIP[e] ?? e;
const NECESSIDADE: Record<Chamado, "fome" | "higiene" | "humor"> = { fome: "fome", higiene: "higiene", carinho: "humor" };
const lutasZeradas = (): Lutas => ({ lutas: 0, vitorias: 0, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 });
/** acao que atende um chamado REAL (carinho = mau humor: elogio tambem resolve; petisco atende a fome) */
function atende(pedido: Chamado, a: AcaoDono): boolean {
  return ACAO_CHAMADO[pedido].includes(a) || (pedido === "fome" && a === "petisco") || (pedido === "carinho" && a === "elogiar");
}

/* ---------------------------------------------------------------- confianca (pets v8, M1): o rival de cada luta
   A novidade conta por rival. Luta comum e de arena: a chave do evento (o bot, o NPC ou o lider; as lutas seguidas da Cidadela repetem o
   mesmo rival). Liga: o Mega de cada lider ("liga:<lider>"). Fronteira e Salao: a forma sorteada do rival da luta ("forma:..."), a
   mesma forma de novo e o mesmo rival */
const chaveFormaRival = (f: Forma): string => "forma:" + [f.esp, f.est, f.ramo ?? "", f.linha ?? "", f.adulta ?? ""].join(".");
/** o rival da luta k da serie do evento "l" (rival, semente), como a confianca o conta */
export function rivalDaConfianca(rival: string, semente: number, k: number, est: Estagio): string {
  if (rival === RIVAL_LIGA) return "liga:" + LIGA[k].lider;
  if (ehInstalacao(rival)) return chaveFormaRival(formaRivalInstalacao(semente, k));
  if (rival === RIVAL_SALAO) return chaveFormaRival(formaRivalSalao(semente, est));
  return rival;
}
/** o nome na tela de um rival da confianca (rivalDaConfianca) */
export function nomeRivalConfianca(chave: string): string {
  if (chave.startsWith("liga:")) {
    const i = LIGA.findIndex(x => x.lider === chave.slice(5));
    return i >= 0 ? `${nomeMegaLiga(i)} de ${NOME_BOT[LIGA[i].lider]}` : chave;
  }
  if (chave.startsWith("forma:")) {
    const [esp, est, ramo, linha, adulta] = chave.slice(6).split(".");
    const f = { esp, est, ...(ramo ? { ramo } : {}), ...(linha ? { linha } : {}), ...(adulta ? { adulta } : {}) } as Forma, arq = nomeArquetipo(f);
    return arq ? `${nomeForma(f)} (${arq})` : nomeForma(f);
  }
  return NOME_BOT[chave] ?? chave;
}

export class Motor {
  semente: number;
  versao: VersaoPet;
  rEnv: Rng;
  rPol: Rng;
  temp: Temperamento;
  e: EstadoVida;
  pol: Bandit;
  /* v2: vinculo, obediencia (rng propria) e registro do desejo (metricas) */
  vinc!: Vinculo;
  rObed!: Rng;
  obed!: { pedidos: number; recusas: number; fazerOutra: number };
  dz!: RegistroDesejo;
  acao: AcaoPet = "ocioso";
  prox = 0;
  log: EventoRegistro[] = [];
  tracos: Record<AcaoPet, number>;
  nDecisoes = 0;
  historico: ItemHistorico[] = [];
  especie: Especie;
  estagioAtual: Estagio = "bebe";
  evolucoes: Evolucao[] = [];
  forma: Forma;
  treino: TreinoPet;
  pausaTreino: { treinou: boolean } | null = null;
  pausas = { atendidas: 0, ignoradas: 0 };
  falaFria = false;
  sombria = false;
  chamados: Chamados = { abertos: {}, atendidos: 0, total: 0 };
  sparring = 0;
  motivos: MotivoVida[] = [];
  motivo: MotivoVida | null = null;
  nDono = 0;
  gp: GambitsPet | null = null;
  campanha: Record<string, number>;
  /* v4: educacao, lutas e lesoes (docs/DESIGN_EDUCACAO_HERANCA_LESOES.md) */
  rTrav!: Rng;
  edu!: Educacao;
  /* v7: voz propria (fala espontanea com janela e mentira) */
  rMentira!: Rng;
  men!: EstadoMentira;
  honestidadeEspecie = 1;                        /* especie com traco verificado de enganador: CMEN.honestidadeEnganador */
  /* v7: o que o extrator da historia le (motor/historia.ts). Derivado do replay: nao vai para o save nem para a
     assinatura. episodios = inicio de cada trecho de uma mesma acao do pet (fora ocioso) */
  vida5: { episodios: [number, AcaoPet][]; lutas: { tick: number; rival: string; resultado: "vitoria" | "derrota" | "empate"; lesao: boolean }[];
    sessoes: [number, Exercicio][]; anterior: AcaoPet | null } = { episodios: [], lutas: [], sessoes: [], anterior: null };
  lutas!: Lutas;
  lesionadoDesde: number | null = null;
  vitoriasVida = 0;                              /* v4: experiencia de combate (nao zera ao evoluir) */
  morte: { tick: number; causa: "lesoes" | "lesao_sem_tratar" } | null = null;
  janelasFechadas: (Janela & { desfecho: string; fim: number })[] = [];
  origem: Origem | null = null;                   /* v4: filho de um cruzamento (evento "o", o primeiro) */
  /* v8 (M1): confianca de combate e novidade por rival, recalculadas das lutas do registro; null nos v1-v7 */
  conf: ConfiancaCombate | null = null;
  /* v8 (M1): para cada luta de conf.historico, a ordem do evento "l" dela entre os "l" do registro (uma serie tem varias lutas num
     evento so); derivado no replay, fora da assinatura. A tela usa para apontar o "porque" da frase para o evento */
  confEvento: number[] = [];
  private nEventosLuta = 0;
  /* v4: ritmo dos estagios (evento "c" no comeco do registro); sem ele, o rapido de sempre */
  ritmo: Ritmo = "rapida";
  dur: { bebe: number; crianca: number; adolescente: number; adulto: number } = { ...DUR_EVO, adulto: CMG.durRapida };
  /** v6: medalhas do Tamer que este pet conhece (evento "u"); a evolucao espera por elas (docs/DESIGN_MEDALHAS_ARENAS.md) */
  medalhas = 0;
  /** v6 (itens, medalhas parte 3; motor/itens.ts): os chips do Tamer equipados neste pet, na ordem em que entraram (evento "i") */
  chips: string[] = [];
  /** v6: a carta que vale na proxima luta (evento "k"); a luta a consome */
  carta: string | null = null;
  /** v6: as cartas que valeram nas lutas deste pet, na ordem */
  cartasUsadas: string[] = [];
  /** v6: o registro tem evento de item; so entao os itens entram na assinatura (a dos pets sem item nao muda) */
  comItens = false;
  /** v6: a Liga dos Lideres (liga.ts): tentativas e titulos (as 6 vencidas) deste pet. Entra na assinatura so depois da primeira
      tentativa (a dos pets que nunca entraram na Liga nao muda) */
  liga = { tentativas: 0, titulos: 0 };
  /** v6: o Tamer venceu a Liga, e as instalacoes da Fronteira abriram para este pet (evento "f"; instalacoes.ts). Entra na assinatura so
      depois do evento */
  fronteira = false;
  /** v6: as tentativas deste pet em cada instalacao da Fronteira, o recorde dele (a maior sequencia de vitorias) e a ultima sequencia.
      Entra na assinatura so depois do evento "f" */
  instalacoes: Record<IdInstalacao, ContaInstalacao> =
    Object.fromEntries(INSTALACOES.map(x => [x.id, { tentativas: 0, recorde: 0, ultima: 0 }])) as Record<IdInstalacao, ContaInstalacao>;
  /** v6: as lutas deste pet no Salao da Fronteira (salao.ts): quantas (uma por tentativa do Tamer em que ele lutou) e quantas venceu. Entra
      na assinatura so depois da primeira (a dos pets que nunca lutaram la nao muda) */
  salao = { tentativas: 0, vitorias: 0 };

  constructor(semente: number, versao: number = VERSAO_PET) {
    if (![1, 2, 3, 4, 5, 6, 7, 8].includes(versao)) throw new Error("versão de pet desconhecida: " + versao);
    this.semente = semente; this.versao = versao as VersaoPet;
    this.rEnv = criarRng(semente); this.rPol = criarRng(semente + 1000003);
    /* temperamento do ovo: rng propria, nao mexe nas outras */
    this.temp = temperamentoDe(semente);
    this.e = estadoInicial(); this.pol = new Bandit(this.temp, versao);
    if (versao >= 2) {
      this.vinc = new Vinculo(); this.rObed = criarRng(hashSemente("obediencia", semente));
      this.obed = { pedidos: 0, recusas: 0, fazerOutra: 0 };
      this.dz = { atual: null, vontades: 0, cumpridas: 0, abertas: [], tVontade: 0 };
    }
    this.tracos = Object.fromEntries(ACOES_PET.map(a => [a, 1 / ACOES_PET.length])) as Record<AcaoPet, number>;
    /* especie: sorteada pela semente (ovo). Evolucao (arvore V2.1): derivada do registro, forma travada em cada transicao */
    this.especie = ESPECIES[hashSemente("especie", semente) % ESPECIES.length];
    this.forma = { esp: this.especie, est: "bebe" };
    /* treino (todas as versoes; so os v2 enrolam por obediencia e mexem no vinculo) */
    this.treino = new TreinoPet(this.especie);
    /* campanha: vitorias por desafio (derivadas das lutas do registro) */
    this.campanha = Object.fromEntries(campanhaDe(versao).map(c => [c.k, 0]));
    if (versao >= 4) {
      /* rng propria das travessuras: sorteada em TODO slot (numeros comuns), nao mexe nas outras */
      this.rTrav = criarRng(hashSemente("travessura", semente));
      this.edu = { disciplina: 0, acertos: 0, petiscos: 0, janela: null, proximo: {}, contagem: {} };
      this.lutas = lutasZeradas();
    }
    if (versao >= 7) {
      /* rng propria da mentira: duas por fala, sempre (numeros comuns), nao mexe nas outras */
      this.rMentira = criarRng(hashSemente("mentira", semente));
      this.men = { impunes: 0, acertos: 0 };
    }
    /* v8 (M1): a confianca de combate e a novidade por rival (estado derivado das lutas "l"; nenhum evento novo) */
    if (versao >= 8) this.conf = new ConfiancaCombate();
  }
  get disciplina(): number { return this.versao >= 4 ? this.edu.disciplina : 0; }

  /* ---------------------------------------------------------------- heranca (pets v4) */
  /** cruza dois adultos vivos (Ultimate ou Mega): o filho (versao atual) herda temperamento (media + ruido) e especie (de um dos pais) */
  static cruzar(pai: Motor, mae: Motor, sementeFilho: number, sementeHeranca: number, quem: string, ger?: [number, number]): Motor {
    const ver = (p: Motor, g?: number) => {
      if (p.estagioAtual !== "adulto" && p.estagioAtual !== "mega") throw new Error("só Ultimate ou Mega cruzam");
      if (p.morte) throw new Error("um dos pais morreu");
      return { h: hashSemente(JSON.stringify(p.log)), esp: p.especie, temp: { ...p.temp }, est: p.estagioAtual, ...(g ? { ger: g } : {}) };
    };
    const filho = new Motor(sementeFilho, VERSAO_PET);
    filho.registrarOrigem({ pais: [ver(pai, ger?.[0]), ver(mae, ger?.[1])], s: sementeHeranca, quem });
    return filho;
  }
  /** ritmo dos estagios: so no comeco do registro, antes de qualquer outro evento */
  configurar(dur: Ritmo): void {
    if (this.log.length) throw new Error("o ritmo se escolhe antes de o ovo chocar");
    this.log.push([this.e.tick, "c", { dur }]);
    this._config(dur);
  }
  private _config(dur: Ritmo): void {
    if (this.versao < 4) throw new Error("ritmo só em pets v4");
    if (this.nDecisoes || this.nDono || this.e.tick !== TICK_INICIAL || this.origem) throw new Error("configuração fora do começo do registro");
    if (dur !== "rapida" && dur !== "classica") throw new Error("ritmo desconhecido: " + dur);
    const [b, c, a] = dur === "classica" ? DUR_CLASSICA : [DUR_EVO.bebe, DUR_EVO.crianca, DUR_EVO.adolescente];
    this.ritmo = dur; this.dur = { bebe: b, crianca: c, adolescente: a, adulto: dur === "classica" ? CMG.durClassica : CMG.durRapida };
  }
  registrarOrigem(o: Origem): void {
    if (this.log.some(ev => ev[1] !== "c")) throw new Error("a origem precisa ser o primeiro evento do registro");
    this.log.push([this.e.tick, "o", o]);
    this._origem(o);
  }
  private _origem(o: Origem): void {
    if (this.versao < 4) throw new Error("origem só em pets v4");
    if (this.origem || this.nDecisoes || this.nDono || this.e.tick !== TICK_INICIAL) throw new Error("evento de origem fora da primeira posição");
    /* rng propria da heranca: especie primeiro, depois os eixos na ordem de EIXOS_TEMP */
    const r = criarRng(hashSemente("heranca", o.s)), [p, q] = o.pais;
    this.especie = [p.esp, q.esp][r.int(2)];
    this.temp = Object.freeze(Object.fromEntries(EIXOS_TEMP.map(e =>
      [e, Math.max(-1, Math.min(1, (p.temp[e] + q.temp[e]) / 2 + CHE.sigma * r.gauss()))]))) as Temperamento;
    this.pol = new Bandit(this.temp, this.versao);
    this.forma = { esp: this.especie, est: "bebe" };
    this.treino = new TreinoPet(this.especie);
    this.origem = o;
  }

  /* ---------------------------------------------------------------- campanha e lutas */
  /** lugares da campanha desta versao (pets v5: a Montanha Espiral, com o Piedmon) */
  get lugares(): Lugar[] { return lugaresDe(this.versao); }
  /** regras das lutas deste pet: V21D nos pets v6 (docs/VALIDACAO_V21D.md), V21C nos v1-v5 */
  get regras(): RegrasLuta { return regrasDaVersao(this.versao); }
  /** quem fica com a luta no limite de turnos: nos pets v6 o rival (o pet sempre desafia); nos v1-v5, ninguem (a fracao de vida) */
  get desafiado(): Desafiado { return desafiadoDaVersao(this.versao); }
  lugarVencido(L: number): boolean { return this.lugares[L].rivais.some(r => this.campanha[r] > 0); }
  /** indice do lugar do NPC na campanha deste pet (na v6 o Myotismon e a Montanha Espiral mudam de indice) */
  lugarDe(k: string): number {
    const i = this.lugares.findIndex(L => L.rivais.includes(k));
    if (i < 0) throw new Error(`${NOME_BOT[k] ?? k} não está na campanha deste pet`);
    return i;
  }
  /** desafio da campanha aberto: o primeiro sempre; os outros depois de vencer o anterior */
  desafioAberto(k: string): boolean { const L = this.lugarDe(k); return L === 0 || this.lugarVencido(L - 1); }
  /** a arena cuja regra vale na luta contra o rival (pets v6 contra o lider; docs/DESIGN_MEDALHAS_ARENAS.md, secao 3) */
  arenaDe(rival: string): Arena | null { return NPC[rival] ? arenaDaLuta(rival, this.versao) : null; }
  /** luta contra bot: entra no registro (rival + semente) e ensina os gambits */
  lutar(rival: string, semente: number, carta: string | null = null): ResultadoLutaPet {
    if (rival !== RIVAL_LIGA && rival !== RIVAL_SALAO && !ehInstalacao(rival) && !NOME_BOT[rival]) throw new Error("rival desconhecido: " + rival);
    if (this.versao >= 4) { this._conferirMorte(); this._vivo(); }
    if (rival === RIVAL_LIGA) { const erro = this.porqueNaoLiga(); if (erro) throw new Error(erro); if (carta !== null) throw new Error("as cartas não valem na Liga dos Líderes"); }
    if (ehInstalacao(rival)) {
      /* a Fronteira depois do titulo: a entrada, a carta (nao vale) e a semente da tentativa (sai do registro; ninguem escolhe os rivais) */
      const x = instalacaoDe(rival), erro = this.porqueNaoInstalacao(rival);
      if (erro) throw new Error(erro);
      if (carta !== null) throw new Error(`as cartas não valem na ${x.nome}`);
      if (semente !== this.sementeInstalacao(rival)) throw new Error(`a semente da tentativa na ${x.nome} sai do registro do pet: ${this.sementeInstalacao(rival)}, não ${semente}`);
    }
    if (rival === RIVAL_SALAO) {
      /* o Salao depois do titulo: a entrada, a carta (nao vale) e a semente da luta (sai do registro do pet) */
      const erro = this.porqueNaoSalao(); if (erro) throw new Error(erro);
      if (carta !== null) throw new Error("as cartas não valem no Salão");
      if (semente !== this.sementeSalao()) throw new Error(`a semente da luta no Salão sai do registro do pet: ${this.sementeSalao()}, não ${semente}`);
    }
    if (NPC[rival] && !(rival in this.campanha)) throw new Error(`${NPC[rival]!.nome} não está na campanha deste pet`);
    if (NPC[rival] && !this.desafioAberto(rival)) throw new Error(`desafio bloqueado: vença alguém em ${this.lugares[this.lugarDe(rival) - 1].nome} antes`);
    /* pets v6: a carta do Tamer entra no registro logo antes da luta, e a luta a consome */
    if (carta !== null) { this._validarCarta(carta); this.log.push([this.e.tick, "k", { id: carta }]); this._armarCarta(carta); }
    this.log.push([this.e.tick, "l", { r: rival, s: semente }]);
    return this._lutar(rival, semente);
  }
  /** a luta contra o rival como o motor a joga, sem mexer no pet. Campanha contra NPC: stats treinados absolutos; arena
      contra bots: normalizados ao orcamento. Nas arenas (pets v6 contra o lider, arenas.ts) vale a regra dela: o lider com o
      fator calibrado (e o contra-golpe, na Torre de pedra), o pet com a lista sem o dono (Lago) e as lutas seguidas sem cura
      (Cidadela). O _lutar joga por aqui; a tela refaz as lutas do registro por aqui tambem */
  montarLuta(rival: string, semente: number): LutaMontada {
    const L = this.lutadores(rival, semente), carta = this.carta;
    /* a Liga (liga.ts): os 6 lideres em sequencia, sem cura e sem carta (a carta armada antes dela falha em _lutar) */
    if (L.lideres) return { ...L, carta: null, rivais: null, serie: jogarSerie(L.A, L.lideres, semente, this.regras, this.desafiado, null) };
    /* o Salao (salao.ts): uma luta contra o rival sorteado do estagio do pet, sem carta */
    if (rival === RIVAL_SALAO) return { ...L, carta: null, rivais: null, serie: jogarSerie(L.A, [L.B], semente, this.regras, this.desafiado, null) };
    /* uma instalacao da Fronteira (instalacoes.ts): rivais sorteados da semente, um por luta, ate a primeira que nao for vitoria (ou o
       teto); sem cura e sem carta (a carta armada antes dela falha em _lutar) */
    if (L.instalacao) {
      const rivais: Lutador[] = [];
      const serie = jogarSequencia(L.A, k => { const B = k ? rivalInstalacao(semente, k, this.regras) : L.B; rivais.push(B); return B; },
        LUTAS_MAX_INSTALACAO, semente, this.regras, this.desafiado, null);
      return { ...L, carta: null, rivais, serie };
    }
    return { ...L, carta, rivais: null, serie: jogarSerie(L.A, Array.from({ length: L.arena?.lutas ?? 1 }, () => L.B), semente, this.regras, this.desafiado, carta ? cartaDe(carta).carta : null) };
  }
  /** os dois lados da luta contra o rival, sem jogar (a previa do palco usa isto): o pet (no Lago, com a lista sem o dono),
      o rival (o lider com a regra da arena) e as regras do pet com que ele luta */
  lutadores(rival: string, semente?: number): Omit<LutaMontada, "serie" | "carta" | "rivais"> {
    if (rival === RIVAL_LIGA) {
      /* a Liga: o pet como na campanha (treino absoluto, na escala) com a lista dele (chips valem); os 6 Megas dos lideres */
      const lideres = lutadoresLiga(this.regras);
      return { A: lutadorPet(this, "Seu pet", true), B: lideres[0], lideres, arena: null, usadas: this.gp ? this.gp.ativas.slice() : null, instalacao: null };
    }
    if (ehInstalacao(rival)) {
      /* a Fronteira: o pet como na Liga; no Palacio, com a lista que ele faria sozinho (sem travas, vetos e chips de regra; os chips de
         stat valem). B: o rival da primeira luta da tentativa (sem a semente, a da proxima tentativa deste pet) */
      const instalacao = instalacaoDe(rival), s = semente ?? this.sementeInstalacao(rival);
      let A = lutadorPet(this, "Seu pet", true), usadas = this.gp ? this.gp.ativas.slice() : null;
      if (instalacao.regra === "sozinho" && this.gp) {
        usadas = this.gp.listaPalacio();
        A = { ...A, estilo: { ...A.estilo, gambits: { regras: usadas.map(regraDe), final: this.gp.final } } };
      }
      return { A, B: rivalInstalacao(s, 0, this.regras), lideres: null, arena: null, usadas, instalacao };
    }
    if (rival === RIVAL_SALAO) {
      /* o Salao: o pet como na Liga (chips valem); o rival sorteado do estagio dele (sem a semente, a da proxima luta deste pet la) */
      const s = semente ?? this.sementeSalao();
      return { A: lutadorPet(this, "Seu pet", true), B: rivalSalao(s, this.estagioAtual, this.regras), lideres: null, arena: null,
        usadas: this.gp ? this.gp.ativas.slice() : null, instalacao: null };
    }
    const npc = !!NPC[rival], arena = this.arenaDe(rival);
    let A = lutadorPet(this, "Seu pet", npc), usadas = this.gp ? this.gp.ativas.slice() : null;
    if (arena?.regra === "vinculo" && this.gp) {
      usadas = this.gp.listaSozinho();
      A = { ...A, estilo: { ...A.estilo, gambits: { regras: usadas.map(regraDe), final: this.gp.final } } };
    }
    return { A, B: lutadorBot(rival, this.regras, arena), arena, usadas, lideres: null, instalacao: null };
  }
  /* ---------------------------------------------------------------- a Liga dos Lideres (pets v6; liga.ts) */
  /** por que o pet nao pode desafiar a Liga agora (null: pode). A entrada pede as 6 medalhas, que o pet conhece pelo evento "u" (o
      motor nunca le o Tamer) */
  porqueNaoLiga(): string | null {
    if (this.versao < VERSAO_LIGA) return "a Liga dos Líderes é só de pets v6 em diante";
    if (this.morte) return "o pet morreu";
    if (this.estagioAtual === "bebe") return "o In-Training ainda não luta na Fronteira";
    if (this.medalhas < MEDALHAS_LIGA) return `a Fronteira abre com as ${MEDALHAS_LIGA} medalhas (este pet conhece ${this.medalhas})`;
    return null;
  }
  /* ---------------------------------------------------------------- as instalacoes da Fronteira (pets v6; instalacoes.ts) */
  /** o Tamer venceu a Liga: grava "as instalacoes da Fronteira abrem a partir deste tick" (o app confere o titulo no Tamer; o motor nunca
      le o Tamer) */
  abrirFronteira(): void {
    this._conferirMorte(); this._vivo();
    this._validarFronteira();
    this.log.push([this.e.tick, "f", { campeao: true }]);
    this._abrirFronteira();
  }
  private _validarFronteira(): void {
    if (this.versao < VERSAO_INSTALACOES) throw new Error("a Fronteira é só de pets v6 em diante");
    if (this.fronteira) throw new Error("a Fronteira já está aberta para este pet");
    if (this.medalhas < MEDALHAS_LIGA) throw new Error(`a Fronteira abre com as ${MEDALHAS_LIGA} medalhas (este pet conhece ${this.medalhas})`);
  }
  private _abrirFronteira(): void {
    this._validarFronteira();
    this.fronteira = true;
    this._hist({ t: this.e.tick, quem: "tamer", a: "o Tamer é campeão da Liga: as instalações da Fronteira abriram" });
  }
  /** por que o pet nao pode entrar na instalacao agora (null: pode). A entrada pede o titulo do Tamer, que o pet conhece pelo evento "f" */
  porqueNaoInstalacao(id: string): string | null {
    const x = instalacaoDe(id);
    if (this.versao < VERSAO_INSTALACOES) return `a ${x.nome} é só de pets v6 em diante`;
    if (this.morte) return "o pet morreu";
    if (this.estagioAtual === "bebe") return "o In-Training ainda não luta na Fronteira";
    if (!this.fronteira) return `a ${x.nome} abre depois do título da Liga dos Líderes`;
    return null;
  }
  /** a semente da proxima tentativa deste pet na instalacao (sai do registro: a semente do pet e quantas tentativas ele ja fez ali) */
  sementeInstalacao(id: IdInstalacao): number { return sementeTentativa(this.semente, id, this.instalacoes[id].tentativas + 1); }
  /* ---------------------------------------------------------------- o Salao da Fronteira (pets v6; salao.ts) */
  /** por que o pet nao pode lutar no Salao agora (null: pode): v6, vivo, do Rookie ao Mega, e o titulo do Tamer (evento "f") */
  porqueNaoSalao(): string | null {
    if (this.versao < VERSAO_SALAO) return "o Salão é só de pets v6 em diante";
    if (this.morte) return "o pet morreu";
    if (!ESTAGIOS_SALAO.includes(this.estagioAtual)) return "o In-Training ainda não luta na Fronteira";
    if (!this.fronteira) return "o Salão abre depois do título da Liga dos Líderes";
    return null;
  }
  /** a semente da proxima luta deste pet no Salao (sai do registro: a semente do pet e quantas vezes ele ja lutou la) */
  sementeSalao(): number { return sementeSalao(this.semente, this.salao.tentativas + 1); }
  private _lutar(rival: string, semente: number): ResultadoLutaPet {
    const liga = rival === RIVAL_LIGA, inst = ehInstalacao(rival) ? instalacaoDe(rival) : null, salao = rival === RIVAL_SALAO;
    if (liga) {
      /* no replay tambem: a entrada (as medalhas que o pet conhecia) e a carta, que nao vale na Liga */
      const erro = this.porqueNaoLiga(); if (erro) throw new Error(`luta da Liga no registro sem poder: ${erro}`);
      if (this.carta !== null) throw new Error("as cartas não valem na Liga dos Líderes: carta no registro logo antes da luta da Liga");
    }
    if (inst) {
      /* no replay tambem: a entrada (o titulo que o pet conhecia), a carta e a semente, que sai do registro */
      const erro = this.porqueNaoInstalacao(inst.id); if (erro) throw new Error(`luta da ${inst.nome} no registro sem poder: ${erro}`);
      if (this.carta !== null) throw new Error(`as cartas não valem na ${inst.nome}: carta no registro logo antes da luta`);
      const s = this.sementeInstalacao(inst.id);
      if (semente !== s) throw new Error(`luta da ${inst.nome} no registro com a semente ${semente}; a tentativa ${this.instalacoes[inst.id].tentativas + 1} deste pet tem a ${s}`);
    }
    if (salao) {
      /* no replay tambem: a entrada (o titulo que o pet conhecia), a carta e a semente, que sai do registro */
      const erro = this.porqueNaoSalao(); if (erro) throw new Error(`luta do Salão no registro sem poder: ${erro}`);
      if (this.carta !== null) throw new Error("as cartas não valem no Salão: carta no registro logo antes da luta");
      const s = this.sementeSalao();
      if (semente !== s) throw new Error(`luta do Salão no registro com a semente ${semente}; a luta ${this.salao.tentativas + 1} deste pet lá tem a ${s}`);
    }
    const estSalao = this.estagioAtual;
    const M = this.montarLuta(rival, semente), n = M.lideres ? M.lideres.length : inst ? LUTAS_MAX_INSTALACAO : M.arena?.lutas ?? 1;
    if (this.carta) {
      this._hist({ t: this.e.tick, quem: "carta", a: `usou a ${cartaDe(this.carta).nome} contra ${NOME_BOT[rival]}` });
      this.cartasUsadas.push(this.carta); this.carta = null;
    }
    let lesao = false;
    const ordemL = this.nEventosLuta++;
    M.serie.forEach((res, k) => {
      /* cada luta da serie ensina e conta, com a semente dela (a primeira e a do evento) */
      const s = sementeDaSerie(semente, k);
      /* v8 (M1, espelho de MotorEducacao._lutar): a confianca decai desde a ultima luta e e empurrada pelo resultado, pesado pela
         novidade do rival DESTA luta (a derrota pesa mais pela sensibilidade). O passo dos gambits e a experiencia de combate somam a
         novidade em vez de 1: repetir o mesmo rival ensina e rende menos. Nas series (Cidadela, Liga, Fronteira) cada luta conta */
      const rc = this.conf ? this.conf.registrar(this.e.tick, rivalDaConfianca(rival, semente, k, estSalao),
        res.pontosA === 1 ? 1 : res.pontosA === 0 ? -1 : 0, this.temp.sensibilidade) : null;
      if (rc) this.confEvento.push(ordemL);
      if (this.gp) this.gp.aprender(res, s, M.usadas!, rc ? rc.novidade : 1);
      if (this.estagioAtual === "adolescente") this.sparring++;
      const contra = liga ? `na Liga dos Líderes, contra ${nomeMegaLiga(k)} de ${NOME_BOT[LIGA[k].lider]}`
        : inst ? `${inst.id === "palacio" ? "no" : "na"} ${inst.nome}, contra ${nomeForma(formaRivalInstalacao(semente, k))}`
        : salao ? `no Salão, contra ${nomeForma(formaRivalSalao(semente, estSalao))}` : `contra ${NOME_BOT[rival]}`;
      this._hist({ t: this.e.tick, quem: "luta", a: `${contra}${inst ? ` (luta ${k + 1})` : n > 1 ? ` (luta ${k + 1} de ${n})` : ""}: ${res.pontosA === 1 ? "venceu" : res.pontosA === 0 ? "perdeu" : "empatou"}` });
      if (this.versao >= 4) {
        const L = this.lutas;
        L.lutas++;
        if (res.pontosA === 1) { L.vitorias++; this.vitoriasVida += rc ? rc.novidade : 1; } else if (res.pontosA === 0) L.derrotas++; else L.empates++;
        /* lesao: so na derrota, numa rng derivada da semente da LUTA */
        const l = res.pontosA === 0 && criarRng(hashSemente("lesao", s)).random() < CLE.probLesao;
        if (l) {
          lesao = true;
          L.lesoes++;
          if (this.lesionadoDesde === null) this.lesionadoDesde = this.e.tick;
          if (L.lesoes >= CLE.lesoesMorte) this.morte = { tick: this.e.tick, causa: "lesoes" };
          this._hist({ t: this.e.tick, quem: "lesao", a: "se machucou na luta" });
        }
      }
    });
    const res = M.serie[M.serie.length - 1], venceu = M.serie.length === n && res.pontosA === 1;
    /* campanha: vitorias por desafio; na Cidadela, so a serie inteira conta. A Liga: a tentativa e o titulo (as 6 vencidas) */
    if (NPC[rival] && venceu) this.campanha[rival]++;
    if (liga) { this.liga.tentativas++; if (venceu) this.liga.titulos++; }
    if (salao) { this.salao.tentativas++; if (venceu) this.salao.vitorias++; }
    /* a instalacao: a tentativa, a sequencia de vitorias dela e o recorde do pet ali (o do Tamer sai daqui, src/tamer.ts) */
    if (inst) {
      const x = this.instalacoes[inst.id], v = M.serie.filter(r => r.pontosA === 1).length;
      x.tentativas++; x.ultima = v; x.recorde = Math.max(x.recorde, v);
    }
    if (this.versao >= 7) this.vida5.lutas.push({ tick: this.e.tick, rival, lesao,
      resultado: res.pontosA === 1 ? "vitoria" : res.pontosA === 0 ? "derrota" : "empate" });
    return { ...M, res, venceu, lesao };
  }
  /** intervencao do dono nos gambits: travar, destravar, vetar, liberar */
  intervirGambit(op: OpGambit, k: string): void {
    if (!this.gp) throw new Error("o bebê ainda não tem gambits");
    this.gp.intervir(op, k);                     /* valida antes de gravar */
    this.log.push([this.e.tick, "g", { op, k }]);
    this._hist({ t: this.e.tick, quem: "gambit", a: `${op} ${rotuloRegra(regraDe(k))}` });
  }
  private _gambit(op: OpGambit, k: string): void {
    /* no replay, uma intervencao que nao cabe mais (ex.: pet salvo antes da troca da regra de evolucao)
       e ignorada com aviso em vez de perder o pet inteiro */
    try {
      if (!this.gp) throw new Error("intervenção antes da evolução");
      this.gp.intervir(op, k);
      this._hist({ t: this.e.tick, quem: "gambit", a: `${op} ${rotuloRegra(regraDe(k))}` });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn("intervencao do registro ignorada no replay:", op, msg);
      if (this.gp) this.gp.mudancas.push({ luta: this.gp.nLutas, texto: `intervenção antiga ignorada (${op}): ${msg}`, dono: true });
    }
  }

  /* ---------------------------------------------------------------- itens do Tamer (pets v6; motor/itens.ts) */
  /** chips que este pet pode ter equipados, pelas medalhas que ele conhece (0 nos v1-v5) */
  get vagasChip(): number { return this.versao >= CIT.versaoPet ? vagasDeChip(this.medalhas) : 0; }
  /** por que o chip nao pode entrar agora (null: pode). O motor nao sabe se o Tamer tem o chip: o app confere antes */
  porqueNaoEquipa(id: string): string | null {
    if (this.versao < CIT.versaoPet) return "itens só em pets v6";
    const c = chipDe(id);
    if (this.morte) return "o pet morreu";
    if (this.chips.includes(id)) return `${c.nome} já está equipado`;
    if (!chipServe(c, this.estagioAtual)) return `${c.nome} pede um ${nomeEstagioChip(estagioMinimo(c))} ou mais`;
    if (this.chips.length >= this.vagasChip)
      return this.vagasChip ? `as ${this.vagasChip} vaga${this.vagasChip === 1 ? "" : "s"} de chip estão ocupadas: desequipe um antes` : "sem vaga de chip: a primeira vem com a primeira medalha";
    return c.tipo === "chip_regra" ? this.gp!.porqueNaoEquipaRegra(chaveRegra(c.regra)) : null;
  }
  equipar(id: string): void { this._conferirMorte(); this._vivo(); this._validarItem("equipar", id); this.log.push([this.e.tick, "i", { op: "equipar", id }]); this._item("equipar", id); }
  desequipar(id: string): void { this._conferirMorte(); this._vivo(); this._validarItem("desequipar", id); this.log.push([this.e.tick, "i", { op: "desequipar", id }]); this._item("desequipar", id); }
  private _validarItem(op: OpItem, id: string): void {
    if (op === "equipar") { const erro = this.porqueNaoEquipa(id); if (erro) throw new Error(erro); }
    else if (op === "desequipar") { if (this.versao < CIT.versaoPet) throw new Error("itens só em pets v6"); if (!this.chips.includes(id)) throw new Error(`${chipDe(id).nome} não está equipado`); }
    else throw new Error("operação de item desconhecida: " + JSON.stringify(op));
  }
  private _item(op: OpItem, id: string): void {
    this._validarItem(op, id);
    const c = chipDe(id);
    if (op === "equipar") { this.chips.push(id); if (c.tipo === "chip_regra") this.gp!.equiparRegra(chaveRegra(c.regra), c.nome); }
    else { this.chips.splice(this.chips.indexOf(id), 1); if (c.tipo === "chip_regra") this.gp!.desequiparRegra(chaveRegra(c.regra), c.nome); }
    this.comItens = true;
    this._hist({ t: this.e.tick, quem: "item", a: `${op === "equipar" ? "equipou" : "desequipou"} ${c.nome}` });
  }
  private _validarCarta(id: string): void {
    if (this.versao < CIT.versaoPet) throw new Error("cartas só em pets v6");
    cartaDe(id);
    if (this.carta !== null) throw new Error("já tem uma carta para a próxima luta");
  }
  private _armarCarta(id: string): void { this._validarCarta(id); this.carta = id; this.comItens = true; }
  /** o treino com que o pet luta: o dele mais o dos chips de stat, dentro dos tetos (itens.bonusChipsStat); sem chip, o de sempre */
  pontosDeLuta(): Stats | null {
    const treinou = this.treino.total > 0;
    if (!this.chips.length) return treinou ? this.treino.pontos : null;
    const est = this.estagioAtual, pe = est === "bebe" ? 0 : this.treino.pontosEst[est as EstagioTreino | "mega"] ?? 0;
    return pontosComChips(this.chips, est, this.treino.pontos, pe, treinou);
  }

  /* ---------------------------------------------------------------- dono */
  observar(a: AcaoDono): void {
    if (!(this.versao >= 4 ? ACOES_DONO_V4 : ACOES_DONO).includes(a)) throw new Error("acao de dono desconhecida: " + a);
    if (this.versao >= 4) { this._conferirMorte(); this._vivo(); }
    this.log.push([this.e.tick, "d", a]);
    this._aplicar(a);
  }
  private _aplicar(a: AcaoDono): void {
    if (this.versao >= 4) { this._aplicarV4(a); return; }
    this._aplicarBase(a);
  }
  private _aplicarBase(a: AcaoDono): void {
    const t = this.e.tick;
    if (this.versao >= 2 && COB.sujeitas.includes(a) && this._desobedeceu(a, t)) return;
    this.e = aplicarAcaoDono(this.e, a, this.rEnv);
    if (this.estagioAtual === "bebe") this._atender(a);
    this.pol.receberAcaoDono(a, t);
    this.nDono++;
    if (this.versao >= 2) this.vinc.acaoDono(a, t, this.acao, this.nDono);
    this._hist({ t, quem: "dono", a });
  }
  /** v4 (espelho de MotorEducacao._aplicar_acao_usuario): janela, acoes novas e travessuras que se resolvem sozinhas */
  private _aplicarV4(a: AcaoDono): void {
    const t = this.e.tick, ed = this.edu;
    this._conferirMorte(); this._vivo();
    this._expirar();
    const j = ed.janela;
    if (j && j.tipo === "chamado" && j.falso && a === "alimentar") {
      /* chamado falso: recusa a refeicao (efeito descartado, consome a rng do ambiente igual) */
      aplicarAcaoDono(this.e, a, this.rEnv);
      this._conta("refeicoes_recusadas");
      this._contato(a, t, "recusou a refeição (era manha)");
      return;
    }
    const dormia = this.e.dormindo, fomeAntes = this.e.fome, recAntes = this.obed.recusas;
    if (a === "petisco") {
      this.e = { ...this.e, fome: clamp(this.e.fome + C.ganhoAlim * CED.fracaoPetisco) };
      this._contato(a, t);
    } else if (a === "levar_ao_banheiro") this._contato(a, t);
    else if (a === "tratar_lesao") {
      if (this.lesionadoDesde !== null) { this.lesionadoDesde = null; this.lutas.tratadas++; }
      this._contato(a, t);
    } else this._aplicarBase(a);
    /* resolvem sozinhas: acordar o pet dormindo e superalimentacao */
    if (dormia && !this.e.dormindo) { this.e = { ...this.e, humor: clamp(this.e.humor - CED.custoHumorAcordar) }; this._conta("acordado"); }
    const comeu = a === "petisco" || (a === "alimentar" && this.obed.recusas === recAntes);
    if (comeu && fomeAntes >= CED.limiarSuper) { this.e = { ...this.e, saude: clamp(this.e.saude - CED.custoSaudeSuper) }; this._conta("superalimentacao"); }
    if (!j) return;
    if (j.tipo === "fala") { this._julgarFala(j, a); return; }
    if (j.tipo === "aviso") {
      if (a === "levar_ao_banheiro") {
        ed.disciplina = Math.min(CED.disciplinaMax, ed.disciplina + CED.disciplinaBanheiro);
        this._conta("avisos_atendidos"); this._fechar("atendido");
      }
      return;
    }
    if (!j.falso && a === "repreender") { this.vinc.ajustar(CED.vincBroncaSemMotivo, this.nDono); this._conta("broncas_sem_motivo"); }
    if (j.falso) {
      if (a === "repreender") {
        ed.disciplina = Math.min(CED.disciplinaMax, ed.disciplina + CED.passo); ed.acertos++;
        this._conta("falsos_corrigidos"); this._fechar("corrigido");
      } else if (a === "petisco") {
        ed.petiscos++; ed.acertos = 0; this._conta("falsos_cedidos"); this._fechar("cedido");
      }
    } else if (atende(j.pedido as Chamado, a)) { this._conta("reais_atendidos"); this._fechar("atendido"); }
  }
  /** o que toda acao do dono faz alem do efeito: contato, politica, vinculo, historico */
  private _contato(a: AcaoDono, t: number, texto?: string): void {
    this.e = { ...this.e, ultimoCuidado: t, totalCuidados: this.e.totalCuidados + 1 };
    this.pol.receberAcaoDono(a, t);
    this.nDono++;
    this.vinc.acaoDono(a, t, this.acao, this.nDono);
    this._hist({ t, quem: "dono", a: texto ?? a });
  }
  private _conta(k: string): void { this.edu.contagem[k] = (this.edu.contagem[k] ?? 0) + 1; }
  /** chance de um slot sem necessidade real virar chamado falso (0 com disciplina cheia ou depois de aprender) */
  fracaoFalso(): number {
    const ed = this.edu;
    if (ed.disciplina >= CED.disciplinaMax || ed.acertos >= CED.acertos) return 0;
    return Math.min(CED.tetoFalso, CED.fracaoFalsoBase * (1 - ed.disciplina / CED.disciplinaMax) + CED.reforcoPetisco * ed.petiscos);
  }
  private _agendar(est: Estagio, t: number): void {
    const iv = est === "bebe" ? null : CED.intervalos[baseDe(est) as EstagioTreino];
    this.edu.proximo = iv ? Object.fromEntries(Object.entries(iv).map(([k, m]) => [k, t + m])) : {};
  }
  /** slots de chamado na decisao do pet (espelho de MotorEducacao._decisao_observada) */
  private _travessuras(): void {
    const t = this.e.tick, ed = this.edu;
    this._expirar();
    for (const tipo of (Object.keys(ed.proximo) as Chamado[]).sort()) {
      while (t >= ed.proximo[tipo]!) {
        ed.proximo[tipo]! += CED.intervalos[baseDe(this.estagioAtual) as EstagioTreino][tipo];
        this._slot(tipo, t);
      }
    }
  }
  private _slot(tipo: Chamado, t: number): void {
    const u = this.rTrav.random();                 /* sempre: numeros comuns */
    const ed = this.edu;
    if (ed.janela || this.e.dormindo) return;
    if (tipo === "higiene") {                      /* slot de higiene = aviso antes de sujar (coco a cada 120 min) */
      ed.janela = { tipo: "aviso", pedido: "banheiro", inicio: t, prazo: t + CED.janela, falso: false };
      this._conta("avisos"); return;
    }
    const real = this.e[NECESSIDADE[tipo]] < CED.limiarReal;
    if (!real && u >= this.fracaoFalso()) return;
    ed.janela = { tipo: "chamado", pedido: tipo, inicio: t, prazo: t + CED.janela, falso: !real };
    this._conta(real ? "chamados_reais" : "falsos");
  }
  private _fechar(desfecho: string): void {
    this.janelasFechadas.push({ ...this.edu.janela!, desfecho, fim: this.e.tick });
    if (this.janelasFechadas.length > 100) this.janelasFechadas.shift();
    this.edu.janela = null;
  }
  private _expirar(): void {
    const j = this.edu.janela, ed = this.edu;
    if (!j || this.e.tick <= j.prazo) return;
    if (j.tipo === "fala") {
      if (j.falso) { this.men.impunes++; this.men.acertos = 0; this._conta("mentiras_impunes"); this._fechar("impune"); }
      else { this._conta("verdades_ignoradas"); this._fechar("ignorado"); }
      return;
    }
    if (j.tipo === "aviso") { this.e = { ...this.e, sujeira: Math.min(C.sujMax, this.e.sujeira + 1) }; this._conta("avisos_ignorados"); }
    else if (j.falso) { ed.disciplina = Math.max(0, ed.disciplina - CED.passo); ed.acertos = 0; this._conta("falsos_ignorados"); }
    else this._conta("reais_ignorados");
    this._fechar("ignorado");
  }
  private _conferirMorte(): void {
    if (this.versao < 4 || this.morte) return;
    if (this.lesionadoDesde !== null && this.e.tick - this.lesionadoDesde >= CLE.horasMorte * 60)
      this.morte = { tick: this.e.tick, causa: "lesao_sem_tratar" };
  }
  private _vivo(): void {
    if (this.morte) throw new PetMorto(this.morte.causa === "lesoes" ? "ele se machucou demais nas lutas" : "a lesão ficou sem tratamento");
  }
  /* ---------------------------------------------------------------- voz propria: mentira (pets v7) */
  /** h (0 a 1): sombria e sobrecarga tiram; sem sobrecarga e nao sombrio, h = 1 e o pet nunca mente */
  honestidade(): number {
    if (this.versao < 7) return 1;
    const f = this.sombria ? CMEN.fatorSombria : 1;
    return Math.max(0, Math.min(1, f * (1 - CMEN.pesoSobrecarga * this.treino.sobrecarga / 100) * this.honestidadeEspecie));
  }
  chanceMentira(): number {
    if (this.versao < 7) return 0;
    const h = this.honestidade();
    if (h >= 1 || this.men.acertos >= CMEN.acertos) return 0;
    return Math.min(CMEN.tetoChance, CMEN.coefChance * (1 - h) * (1 - this.edu.disciplina / CED.disciplinaMax)
      + CMEN.reforcoImpune * this.men.impunes);
  }
  /** a honestidade que o jogo mostra: cai com a vista grossa, sobe com a disciplina */
  honestidadeMostrada(): number { return 1 - this.chanceMentira() / CMEN.tetoChance; }
  /** fala espontanea (gatilho do app): entra no registro e abre a janela, se couber. Devolve a janela (com a verdade:
      quem chama e a apresentacao) ou null (janela ja aberta, dormindo) */
  falar(gatilho: string): Janela | null {
    if (this.versao < 7) throw new Error("fala espontânea só em pets v7");
    if (!/^[a-z_]+$/.test(gatilho)) throw new Error("gatilho de fala inválido: " + gatilho);
    this._conferirMorte(); this._vivo();
    this.log.push([this.e.tick, "fl", gatilho]);
    return this._falar(gatilho);
  }
  private _falar(gatilho: string): Janela | null {
    if (this.versao < 7) throw new Error("evento de fala num pet anterior ao v7");
    const t = this.e.tick;
    this._conferirMorte();
    this._expirar();
    const u = this.rMentira.random(), uTema = this.rMentira.random();       /* sempre: numeros comuns */
    this._conta("falas");
    if (this.edu.janela || this.e.dormindo || this.morte) { this._conta("falas_sem_janela"); return null; }
    const h = this.honestidade(), p = this.chanceMentira(), falso = u < p;
    const tema: TemaFala = uTema < CMEN.fracaoTemaEstado ? "estado" : "historia";
    this.edu.janela = { tipo: "fala", pedido: tema, inicio: t, prazo: t + CMEN.janela, falso, contradiz: falso && tema === "estado",
      gatilho, h, p };
    if (falso) this._conta("mentiras");
    return { ...this.edu.janela };
  }
  /** o dono julga a fala: bronca, petisco ou elogio fecham a janela; o resto nao (espelho de _julgar_fala) */
  private _julgarFala(j: Janela, a: AcaoDono): void {
    const ed = this.edu;
    if (a === "repreender") {
      if (j.falso) {
        ed.disciplina = Math.min(CED.disciplinaMax, ed.disciplina + CED.passo); this.men.acertos++;
        this._conta("mentiras_corrigidas"); this._fechar("corrigida");
      } else {
        this.vinc.ajustar(CED.vincBroncaSemMotivo, this.nDono); this._conta("broncas_injustas"); this._fechar("bronca_injusta");
      }
    } else if (a === "petisco" || a === "elogiar") {
      if (j.falso) { this.men.impunes += CMEN.impunesPremiada; this.men.acertos = 0; this._conta("mentiras_premiadas"); this._fechar("premiada"); }
      else { this._conta("verdades_aceitas"); this._fechar("aceita"); }
    }
  }
  /** janela aberta agora (so pets v4) */
  janelaAberta(): Janela | null { return this.versao >= 4 ? this.edu.janela : null; }
  /** taxa de vitoria do estagio (v4): a passagem para adulto pede >= limiarTaxa em >= CAT.sparring lutas */
  taxaVitoria(): number | null { return this.versao >= 4 && this.lutas.lutas ? this.lutas.vitorias / this.lutas.lutas : null; }

  /** obediencia (espelho de MotorPersonalidade): p = logistica(b0 + b_v vinculo - b_t teimosia - b_c conflito).
      Na desobediencia o efeito do dono roda num estado descartado (consome a rng do ambiente igual), a
      tentativa conta como contato e a politica recebe a acao normalmente (recusa nao corta aprendizado) */
  private _desobedeceu(a: AcaoDono, t: number): boolean {
    this.obed.pedidos++;
    const [conf, nec] = conflitoDono(observacao(this.e).v, a);
    const [p, contrib] = termosObediencia(this.vinc.valor, this.temp.teimosia, conf, nec);
    if (this.rObed.random() < p) return false;
    const tipo = this.rObed.random() < COB.probFazerOutra ? "fazer_outra" : "recusar";
    aplicarAcaoDono(this.e, a, this.rEnv);                        /* efeito descartado */
    this.e = { ...this.e, ultimoCuidado: t, totalCuidados: this.e.totalCuidados + 1 };
    if (tipo === "fazer_outra") { this.e = efeitoAcaoPet(this.e, this.acao); this.obed.fazerOutra++; }
    this.obed.recusas++;
    this.pol.receberAcaoDono(a, t);
    this.nDono++;
    this.vinc.acaoDono(a, t, this.acao, this.nDono);
    /* motivo honesto: so o termo de maior contribuicao negativa, se passar do limiar */
    const neg = Object.entries(contrib).filter(([, c]) => c <= -COB.limiarMotivo).sort((x, y) => x[1] - y[1] || (x[0] < y[0] ? -1 : 1));
    const fatores = neg.length ? [neg[0][0]] : [];
    const refs = fatores[0] === "vinculo_baixo" && this.vinc.ultRefBaixa != null ? [this.vinc.ultRefBaixa] : [];
    this.motivo = {
      origem: "vida", tick: t, acao: tipo, fatores, refsOrd: refs, intensidade: Math.min(1, Math.max(0, 1 - p)),
      exploracao: false, humor: this.e.humor, valorDecidiu: true, recusa: { acaoDono: a, p },
    };
    this.motivos.push(this.motivo); if (this.motivos.length > 200) this.motivos.shift();
    this._hist({ t, quem: "recusa", a: `${tipo === "recusar" ? "recusou" : "fez outra coisa em vez de"} ${a}` });
    return true;
  }
  /** desejo depois de cada decisao: registra so quando muda; alimenta o vinculo e as metricas (cumprimento:
      vontade com alvo X cumprida se o pet escolhe X em ate kCumprimento ticks) */
  private _desejo(obs: Observacao, a: AcaoPet, t: number): void {
    const d = this.desejoAtual(obs, t), u = this.dz.atual, ch = (x: { tipo: string; alvo: string } | null) => x ? x.tipo + ":" + x.alvo : "";
    const mudou = ch(d) !== ch(u);
    if (mudou) {
      if (u && u.tipo === "vontade") this.dz.tVontade += t - u.tick;
      if (d && d.tipo === "vontade") { this.dz.vontades++; this.dz.abertas.push([t, d.alvo]); }
      this.dz.atual = d ? { tick: t, tipo: d.tipo, alvo: d.alvo } : null;
    }
    this.dz.abertas = this.dz.abertas.filter(([t0, alvo]) => {
      if (t - t0 > CDJ.kCumprimento) return false;
      if (alvo === a) { this.dz.cumpridas++; return false; }
      return true;
    });
    this.vinc.decisao(obs, a, t, mudou ? d : null);
  }
  /** fracao da vida com vontade ativa (ate agora) */
  fracaoVontade(): number {
    const vida = this.e.tick - TICK_INICIAL, u = this.dz.atual;
    return vida > 0 ? (this.dz.tVontade + (u && u.tipo === "vontade" ? this.e.tick - u.tick : 0)) / vida : 0;
  }

  /* ---------------------------------------------------------------- tempo */
  avancar(n: number): void {
    if (!(n > 0)) throw new Error("avanco precisa ser positivo");
    const u = this.log[this.log.length - 1];
    if (u && u[1] === "t" && u[0] + u[2] === this.e.tick) u[2] += n; else this.log.push([this.e.tick, "t", n]);
    this._avancar(n);
  }
  private _avancar(n: number): void {
    for (let i = 0; i < n; i++) {
      if (this.e.tick >= this.prox) {
        const obs = observacao(this.e);
        const a = this.pol.agir(obs, this.rPol);
        const t = this.e.tick;
        this.motivo = motivoVida(this, obs, a, t);
        this.motivos.push(this.motivo); if (this.motivos.length > 200) this.motivos.shift();
        this.acao = a;
        if (this.versao >= 7) {
          const v = this.vida5;
          if (a !== v.anterior && a !== "ocioso") v.episodios.push([t, a]);
          v.anterior = a;
        }
        this.e = efeitoAcaoPet(this.e, a);
        this.prox = this.e.tick + C.intervalo;
        this.pol.observar(obs, a, t);
        if (this.versao >= 2) this._desejo(obs, a, t);
        if (this.versao >= 4) { this._conferirMorte(); this._travessuras(); }
        for (const k of ACOES_PET) this.tracos[k] = (1 - CT.alfa) * this.tracos[k] + (k === a ? CT.alfa : 0);
        this.nDecisoes++;
        const ult = this.historico[this.historico.length - 1];
        if (!ult || ult.quem !== "pet" || ult.a !== a) this._hist({ t, quem: "pet", a });
      }
      this.e = avancarTick(this.e, this.rEnv);
      if (this.estagioAtual === "bebe") this._chamados();
      this._evoluir();
      const e = this.e;
      this.treino.avancar(e.tick, e.dormindo, Math.min(e.fome, e.higiene, e.energia) >= CTR.bemCuidado, this.estagioAtual);
      this._pausaTreino();
    }
    if (this.versao >= 4) this._conferirMorte();      /* o prazo da lesao cai no passo do dono */
  }
  /** pedido de pausa: fadiga >= 40. Acabar sem treino = pausa atendida (vinculo sobe); treinar por cima derruba */
  private _pausaTreino(): void {
    if (this.treino.pedePausa && !this.pausaTreino) this.pausaTreino = { treinou: false };
    else if (!this.treino.pedePausa && this.pausaTreino) {
      if (!this.pausaTreino.treinou) { this.pausas.atendidas++; if (this.versao >= 2) this.vinc._amostra(1, CTR.pesoPausa, null); }
      this.pausaTreino = null;
    }
  }

  /* ---------------------------------------------------------------- treino */
  treinar(ex: Exercicio): ResultadoSessao {
    if (!CTR.exercicios[ex]) throw new Error("exercício desconhecido: " + ex);
    if (this.versao >= 4) { this._conferirMorte(); this._vivo(); }
    if (this.estagioAtual === "bebe") throw new Error("o bebê ainda não treina");
    if (!this.treino.podeTocar(this.e.tick)) throw new Error(`descansa um pouco: próximo treino em ${CTR.intervalo - (this.e.tick - this.treino.ultimo!)} min`);
    this.log.push([this.e.tick, "tr", ex]);
    return this._treinar(ex);
  }
  private _treinar(ex: Exercicio): ResultadoSessao {
    const t = this.e.tick;
    let obedece = true, p = 1, contrib: Record<string, number> = {};
    if (this.versao >= 2) {
      const [conf, nec] = conflitoDono(observacao(this.e).v, "treino");
      [p, contrib] = termosObediencia(this.vinc.valor, this.temp.teimosia, conf, nec);
      obedece = this.rObed.random() < p;
    }
    const s = this.treino.sessao(t, ex, obedece);
    if (this.versao >= 7 && !s.enrolou) this.vida5.sessoes.push([t, ex]);
    const base = { origem: "vida" as const, tick: t, refsOrd: [], exploracao: false, humor: this.e.humor, valorDecidiu: true };
    let mot: MotivoVida | null = null;
    if (s.forcada) {
      if (this.versao >= 2) this.vinc.ajustar(CTR.vincForcar, null);
      mot = { ...base, acao: "forcar_treino", fatores: ["fadiga_treino"], intensidade: Math.min(1, s.fadigaAntes / 100) };
    }
    if (this.pausaTreino) {
      if (!this.pausaTreino.treinou) this.pausas.ignoradas++;
      this.pausaTreino.treinou = true;
      if (this.versao >= 2) this.vinc._amostra(0, CTR.pesoPausa, null);
      mot = mot || { ...base, acao: "treinar_cansado", fatores: ["fadiga_treino"], intensidade: Math.min(1, s.fadigaAntes / 100) };
    }
    if (s.enrolou) {
      const neg = Object.entries(contrib).filter(([, c]) => c <= -COB.limiarMotivo).sort((x, y) => x[1] - y[1] || (x[0] < y[0] ? -1 : 1));
      mot = { ...base, acao: "enrolar", fatores: neg.length ? [neg[0][0]] : [], intensidade: Math.min(1, Math.max(0, 1 - p)), recusa: { acaoDono: "treinar", p } };
    }
    if (mot) { this.motivo = mot; this.motivos.push(mot); if (this.motivos.length > 200) this.motivos.shift(); }
    this._hist({ t, quem: "treino", a: `${s.enrolou ? "enrolou no treino de" : s.forcada ? "forçou" : "treinou"} ${NOME_EXERCICIO[ex].toLowerCase()}` });
    return s;
  }
  /** desejo com o pedido de pausa do treino na frente (espelho de MotorTreino._desejo_atual) */
  desejoAtual(obs: Observacao, t: number): Desejo | null {
    if (this.treino.pedePausa) return { tick: t, tipo: "necessidade", alvo: "descansar", causa: "fadiga_treino", intensidade: Math.min(1, this.treino.fadiga / 100) };
    return this.pol.desejo(obs, t);
  }

  /* ---------------------------------------------------------------- chamados do bebe e evolucao */
  /** janelas de chamado do bebe (cronograma_interacoes.json): o bebe chama em horario fixo (fome a cada 30
      min, higiene a cada 60, carinho a cada 45); conta como atendido se o dono fizer a acao certa dentro da
      janela de 15 min. Chamado novo do mesmo tipo com um aberto: o aberto conta como perdido. */
  private _chamados(): void {
    const tk = this.e.tick, t = tk - TICK_INICIAL, ab = this.chamados.abertos;
    for (const tipo of Object.keys(ab) as Chamado[]) if (tk - ab[tipo]! > CAT.janelaChamado) { this.chamados.total++; delete ab[tipo]; }
    for (const [tipo, iv] of Object.entries(CHAMADO_BEBE) as [Chamado, number][]) if (t > 0 && t < this.dur.bebe && t % iv === 0) {
      if (tipo in ab) this.chamados.total++;
      ab[tipo] = tk;
    }
  }
  private _atender(a: AcaoDono): void {
    const ab = this.chamados.abertos;
    for (const tipo of Object.keys(ab) as Chamado[]) if (ACAO_CHAMADO[tipo].includes(a)) { this.chamados.atendidos++; this.chamados.total++; delete ab[tipo]; return; }
  }
  chamadosAbertos(): Chamado[] { return this.estagioAtual === "bebe" ? Object.keys(this.chamados.abertos) as Chamado[] : []; }
  fracaoCuidado(): number { return this.chamados.total ? this.chamados.atendidos / this.chamados.total : 1; }
  /** tick em que a condicao de tempo do estagio atual se cumpre (In-Training, Rookie e Champion; null nos outros).
      v1-v5: desde o nascimento (bebe, bebe + crianca, bebe + crianca + adolescente). v6: desde a evolucao anterior, para
      um pet que esperou a medalha nao ganhar um estagio seguinte curto (DESIGN_MEDALHAS_ARENAS, parte 1). */
  tickLimiteEstagio(): number | null {
    const est = this.estagioAtual, D = this.dur;
    if (est === "bebe") return TICK_INICIAL + D.bebe;
    if (est !== "crianca" && est !== "adolescente") return null;
    if (this.versao < 6) return TICK_INICIAL + D.bebe + D.crianca + (est === "adolescente" ? D.adolescente : 0);
    const ev = [...this.evolucoes].reverse().find(x => x.estagio === est);
    if (!ev) throw new Error(`pet v6 no estagio ${est} sem a evolucao que o trouxe ate ele`);
    return ev.tick + (est === "crianca" ? D.crianca : D.adolescente);
  }
  private _evoluir(): void {
    const t = this.e.tick - TICK_INICIAL, est = this.estagioAtual, D = this.dur, lim = this.tickLimiteEstagio();
    let nova: Omit<Evolucao, "tick" | "forma"> | null = null;
    if (est === "bebe" && t >= D.bebe) {
      const cuidado = this.fracaoCuidado();
      nova = { estagio: "crianca", ramo: cuidado >= CAT.limiarCuidado ? "sereno" : "arisco", cuidado };
    } else if (est === "crianca" && this.e.tick >= lim!) {
      /* v6: pronto para evoluir, mas o Tamer ainda nao tem as medalhas: espera (nada muda ate o evento "u") */
      if (!this.medalhasBastam("adolescente")) return;
      const carater = this.caraterAgora("adolescente");
      /* sobrecarga >= 30: aviso (fala fria); nada muda na forma */
      this.falaFria = this.treino.sobrecarga >= CSO.aviso;
      nova = { estagio: "adolescente", linha: linhaDoCarater(carater), carater, sobrecarga: this.treino.sobrecarga };
    } else if (est === "adulto" && this.versao >= 5) {
      if (this.podeMega()) this._virarMega();
      return;
    } else if (est === "adolescente" && this.e.tick >= lim! && this.sparring >= CAT.sparring
               && (this.versao < 4 || this.lutas.vitorias / this.lutas.lutas >= CLE.limiarTaxa) && this.medalhasBastam("adulto")) {
      const carater = this.caraterAgora("adulto");
      /* sobrecarga >= 60: a forma adulta vira a sombria da linha (permanente: vinculo com teto, instavel na luta) */
      this.sombria = this.treino.sobrecarga >= CSO.sombrio;
      const adulta = this.sombria ? CSO.formas[this.forma.linha!].nome : formaAdultaDe(this.forma.linha!, carater);
      if (this.sombria && this.versao >= 2) this.vinc.limitar(CSO.tetoVinc);
      nova = { estagio: "adulto", adulta, carater, sparring: this.sparring, sobrecarga: this.treino.sobrecarga };
    }
    if (!nova) return;
    const { estagio: e2, ramo, linha, adulta } = nova;
    this.forma = { ...this.forma, est: e2, ...(ramo ? { ramo } : {}), ...(linha ? { linha } : {}), ...(adulta ? { adulta } : {}) };
    this.estagioAtual = e2;
    this.evolucoes.push({ tick: this.e.tick, ...nova, forma: { ...this.forma } });
    this.chamados = { abertos: {}, atendidos: 0, total: 0 }; this.sparring = 0;   /* contadores zeram */
    if (this.versao >= 4) {
      this.lutas = lutasZeradas();
      this.edu.disciplina = Math.floor(this.edu.disciplina * CED.fatorEvoluir); this.edu.acertos = 0;
      this._agendar(e2, this.e.tick);
    }
    if (this.versao >= 7) this.men = { impunes: 0, acertos: 0 };
    if (!this.gp) this.gp = new GambitsPet();
    if (this.versao >= 5) this.gp.semear(this.forma, nomeForma(this.forma), this.regras); else this.gp.semear(this.forma);
  }
  /* ---------------------------------------------------------------- Mega (pets v5; docs/DESIGN_EVOLUCAO_CANONICA.md) */
  /** tick em que virou Ultimate (null antes) */
  tickUltimate(): number | null { const ev = this.evolucoes.find(x => x.estagio === "adulto"); return ev ? ev.tick : null; }
  /** o que falta para o Mega, pelas condicoes do desenho (secao 3): tempo no Ultimate, lutas, vitoria e vinculo; pets v6:
      e as medalhas do Tamer (tem X, precisa Y; null nos v5) */
  requisitosMega(): { tempo: boolean; lutas: boolean; taxa: boolean; vinculo: boolean; falta: number; medalhas: RequisitoMedalhas | null } | null {
    const t0 = this.tickUltimate();
    /* a sombria nunca vira Mega (o vinculo dela tem teto 0,6, acima do limiar de hoje: a regra fica explicita) */
    if (this.versao < 5 || t0 === null || this.estagioAtual !== "adulto" || this.sombria) return null;
    const falta = Math.max(0, t0 + this.dur.adulto - this.e.tick), L = this.lutas;
    return { tempo: falta === 0, lutas: L.lutas >= CAT.sparring, taxa: L.lutas > 0 && L.vitorias / L.lutas >= CLE.limiarTaxa,
      vinculo: this.vinc.valor >= CMG.vinculo, falta, medalhas: this.requisitoMedalhas("mega") };
  }
  podeMega(): boolean { const r = this.requisitosMega(); return !!r && r.tempo && r.lutas && r.taxa && r.vinculo && (!r.medalhas || r.medalhas.ok); }

  /* ---------------------------------------------------------------- medalhas do Tamer (pets v6; docs/DESIGN_MEDALHAS_ARENAS.md) */
  /** medalhas que a evolucao para `alvo` pede e quantas o Tamer tem (null: pet sem trava, v1-v5) */
  requisitoMedalhas(alvo: Estagio): RequisitoMedalhas | null {
    if (this.versao < 6) return null;
    const precisa = medalhasPara(alvo);
    return { tem: this.medalhas, precisa, ok: this.medalhas >= precisa };
  }
  private medalhasBastam(alvo: Estagio): boolean { const r = this.requisitoMedalhas(alvo); return !r || r.ok; }
  /** a proxima evolucao e o que falta para ela (o equivalente do requisitosMega para as outras): tempo, lutas e vitoria do
      estagio (Champion), vinculo (Mega) e as medalhas do Tamer (v6). null: nao ha proxima (In-Training, Mega, sombria) */
  requisitosEvolucao(): RequisitosEvolucao | null {
    const est = this.estagioAtual, lim = this.tickLimiteEstagio();
    if (est === "crianca") {
      const falta = Math.max(0, lim! - this.e.tick), medalhas = this.requisitoMedalhas("adolescente");
      return { alvo: "adolescente", falta, tempo: falta === 0, medalhas, pronto: falta === 0 && (!medalhas || medalhas.ok) };
    }
    if (est === "adolescente") {
      const falta = Math.max(0, lim! - this.e.tick), medalhas = this.requisitoMedalhas("adulto");
      const lutas = this.sparring >= CAT.sparring, taxa = this.versao < 4 || (this.lutas.lutas > 0 && this.lutas.vitorias / this.lutas.lutas >= CLE.limiarTaxa);
      return { alvo: "adulto", falta, tempo: falta === 0, lutas, taxa, medalhas, pronto: falta === 0 && lutas && taxa && (!medalhas || medalhas.ok) };
    }
    const r = this.requisitosMega();
    if (!r) return null;
    return { alvo: "mega", falta: r.falta, tempo: r.tempo, lutas: r.lutas, taxa: r.taxa, vinculo: r.vinculo, medalhas: r.medalhas,
      pronto: r.tempo && r.lutas && r.taxa && r.vinculo && (!r.medalhas || r.medalhas.ok) };
  }
  /** pronto para evoluir, so esperando medalha do Tamer: quantas tem e quantas precisa (null: nao esta esperando medalha) */
  esperandoMedalha(): RequisitoMedalhas | null {
    const r = this.requisitosEvolucao();
    if (!r || !r.medalhas || r.medalhas.ok) return null;
    return r.tempo && (r.lutas ?? true) && (r.taxa ?? true) && (r.vinculo ?? true) ? r.medalhas : null;
  }
  /** o Tamer ganhou medalha: grava "o Tamer tem n medalhas a partir deste tick" e re-verifica a evolucao na hora */
  liberar(n: number): void {
    this._conferirMorte(); this._vivo();
    this._validarLiberacao(n);
    this.log.push([this.e.tick, "u", { n }]);
    this._liberar(n);
  }
  private _validarLiberacao(n: number): void {
    if (this.versao < 6) throw new Error("medalhas do Tamer só em pets v6");
    if (!Number.isInteger(n) || n <= this.medalhas || n > MEDALHAS.length)
      throw new Error(`liberação inválida: ${n} medalhas (o pet já conhece ${this.medalhas}; o máximo é ${MEDALHAS.length})`);
  }
  private _liberar(n: number): void {
    this._validarLiberacao(n);
    this.medalhas = n;
    this._hist({ t: this.e.tick, quem: "tamer", a: `o Tamer tem ${n} medalha${n === 1 ? "" : "s"}` });
    this._evoluir();
  }
  /** estagio novo; a forma adulta, a passiva e o carater vem do Ultimate. A sombria nunca chega aqui (requisitosMega) */
  private _virarMega(): void {
    this.forma = { ...this.forma, est: "mega" };
    this.estagioAtual = "mega";
    this.evolucoes.push({ tick: this.e.tick, estagio: "mega", sparring: this.lutas.lutas, vinculo: this.vinc.valor,
      sobrecarga: this.treino.sobrecarga, forma: { ...this.forma } });
    this.chamados = { abertos: {}, atendidos: 0, total: 0 }; this.sparring = 0;
    this.lutas = lutasZeradas();
    this.edu.disciplina = Math.floor(this.edu.disciplina * CED.fatorEvoluir); this.edu.acertos = 0;
    this._agendar("mega", this.e.tick);
    this.gp!.promover(this.forma, nomeForma(this.forma));
  }
  /** carater medido agora: pets v3 pelo desvio da politica aprendida; v1/v2 pelos tracos (PROVISORIO) */
  caraterAgora(quando: QuandoCarater): Carater { return this.versao >= 3 ? caraterPolitica(this, quando) : caraterDe(this.tracos, quando); }
  /** caráter travado na ultima evolucao que o mediu (adolescente/adulto); antes disso, neutro */
  carater(): Carater | null { const ev = [...this.evolucoes].reverse().find(x => x.carater); return ev ? ev.carater! : null; }
  private _hist(x: ItemHistorico): void { this.historico.push(x); if (this.historico.length > 300) this.historico.shift(); }

  /* ---------------------------------------------------------------- assinatura e replay */
  assinatura(): string {
    return JSON.stringify([this.e, this.acao, this.tracos, this.pol.assinatura(), this.evolucoes, this.forma, this.chamados, this.sparring, this.gp ? this.gp.assinatura() : null, this.campanha,
      this.versao >= 2 ? [this.vinc.assinatura(), this.obed, this.dz] : null, this.treino.assinatura(), this.pausas, this.falaFria, this.sombria,
      ...(this.versao >= 4 ? [[this.edu, this.lutas, this.lesionadoDesde, this.morte, this.origem, this.especie, this.temp, this.vitoriasVida, this.ritmo]] : []),
      ...(this.versao >= 6 ? [this.medalhas] : []), ...(this.comItens ? [[this.chips, this.carta, this.cartasUsadas]] : []),
      ...(this.liga.tentativas ? [["liga", this.liga]] : []),
      ...(this.fronteira ? [["fronteira", this.instalacoes]] : []), ...(this.salao.tentativas ? [["salao", this.salao]] : []),
      ...(this.versao >= 7 ? [[this.men, this.honestidadeEspecie]] : []),
      ...(this.versao >= 8 ? [this.conf!.assinatura()] : [])]);
  }
  /** v8 (M1): a frase de estado da confianca agora (null nos v1-v7) */
  estadoConfianca(): ReturnType<ConfiancaCombate["estado"]> | null { return this.conf ? this.conf.estado(this.e.tick) : null; }
  /** um evento do registro, sem regravar no registro (replay) */
  aplicarEvento(ev: EventoRegistro): void {
    const t = ev[0];
    if (this.e.tick !== t) throw new Error(`registro fora de ordem no tick ${t}`);
    if (this.carta !== null && ev[1] !== "l") throw new Error(`carta para a próxima luta, mas o evento seguinte do registro não é luta (tick ${t})`);
    switch (ev[1]) {
      case "t": this._avancar(ev[2]); break;
      case "d": this._aplicar(ev[2]); break;
      case "l": this._lutar(ev[2].r, ev[2].s); break;
      case "g": this._gambit(ev[2].op, ev[2].k); break;
      case "tr": this._treinar(ev[2]); break;
      case "o": this._origem(ev[2]); break;
      case "c": this._config(ev[2].dur); break;
      case "fl": this._falar(ev[2]); break;
      case "u": this._liberar(ev[2].n); break;
      case "i": this._item(ev[2].op, ev[2].id); break;
      case "k": this._armarCarta(ev[2].id); break;
      case "f":
        if (!ev[2] || typeof ev[2] !== "object" || Object.keys(ev[2]).length !== 1 || ev[2].campeao !== true)
          throw new Error(`evento da Fronteira inválido no registro (tick ${t}): ${JSON.stringify(ev[2])}`);
        this._abrirFronteira(); break;
      default: throw new Error("tipo de evento desconhecido no registro: " + (ev as unknown[])[1]);
    }
  }
  static reproduzir(semente: number, log: readonly EventoRegistro[], versao: number = VERSAO_PET): Motor {
    const m = new Motor(semente, versao);
    for (const ev of log) m.aplicarEvento(ev);
    m.log = log.map(x => [...x] as EventoRegistro);
    return m;
  }
}
