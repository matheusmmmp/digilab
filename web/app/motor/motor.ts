/* Motor com registro de eventos (espelho de engine.py + treino.py + personalidade). Event sourcing: o estado
   nunca e salvo, so o registro (acoes do dono, tempo, lutas, intervencoes, treinos); a vida e reconstruida
   reprocessando o registro. Mesma semente + mesmo registro = mesma assinatura, no mesmo runtime. */
import { CMEN,
  ACAO_CHAMADO, ACOES_DONO, ACOES_DONO_V4, ACOES_PET, CAT, CDJ, CED, CHAMADO_BEBE, CHE, CLE, EIXOS_TEMP, COB, CSO, CT, CTR, C, DUR_CLASSICA, DUR_EVO, ESPECIES,
  TICK_INICIAL, VERSAO_PET,
} from "./constantes.ts";
import { Bandit } from "./bandit.ts";
import { CAMPANHA, LUGARES, NOME_BOT, NPC } from "./bots.ts";
import { caraterDe, caraterPolitica, formaAdultaDe, linhaDoCarater, type QuandoCarater } from "./carater.ts";
import { jogarV2, type Lutador, type ResultadoLuta } from "./combate.ts";
import { aplicarAcaoDono, avancarTick, clamp, efeitoAcaoPet, estadoInicial, observacao, temperamentoDe } from "./estado.ts";
import { GambitsPet, lutadorBot, lutadorPet, regraDe, rotuloRegra } from "./gambits_pet.ts";
import { motivoVida } from "./motivo.ts";
import { NOME_EXERCICIO } from "./nomes.ts";
import { criarRng, hashSemente, type Rng } from "./rng.ts";
import { TreinoPet, type ResultadoSessao } from "./treino.ts";
import { Vinculo, conflitoDono, termosObediencia } from "./vinculo.ts";
import type {
  AcaoDono, AcaoPet, Carater, Chamado, Desejo, Especie, Estagio, EstadoVida, EventoRegistro, Exercicio, Forma, FormaAdulta,
  EstagioTreino, ItemHistorico, Linha, MotivoVida, Observacao, OpGambit, Origem, Ramo, Ritmo, Temperamento, VersaoPet,
} from "./tipos.ts";

/** registro de uma evolucao (entra na assinatura) */
export interface Evolucao {
  tick: number; estagio: Estagio; ramo?: Ramo; cuidado?: number; linha?: Linha; adulta?: FormaAdulta; carater?: Carater;
  sparring?: number; sobrecarga?: number; forma: Forma;
}
interface Chamados { abertos: Partial<Record<Chamado, number>>; atendidos: number; total: number }
interface RegistroDesejo { atual: { tick: number; tipo: Desejo["tipo"]; alvo: string } | null; vontades: number; cumpridas: number; abertas: [number, string][]; tVontade: number }

export interface ResultadoLutaPet { res: ResultadoLuta; A: Lutador; B: Lutador; lesao?: boolean }

/* ---------------------------------------------------------------- educacao-v1 (pets v4) */
/** janela de travessura aberta: o dono ve tipo e pedido, nunca se e falsa */
export interface Janela {
  tipo: "chamado" | "aviso" | "fala"; pedido: Chamado | "banheiro" | TemaFala; inicio: number; prazo: number; falso: boolean;
  /* so na janela de fala (pets v5): a mentira contradiz as barras? o gatilho, a honestidade e a chance na hora */
  contradiz?: boolean; gatilho?: string; h?: number; p?: number;
}
export type TemaFala = "estado" | "historia";
/** pets v5: estado da mentira (DESIGN_VOZ_PROPRIA, secao 9) */
export interface EstadoMentira { impunes: number; acertos: number }
export interface Educacao {
  disciplina: number; acertos: number; petiscos: number; janela: Janela | null; proximo: Partial<Record<Chamado, number>>;
  contagem: Record<string, number>;
}
export interface Lutas { lutas: number; vitorias: number; derrotas: number; empates: number; lesoes: number; tratadas: number }
export class PetMorto extends Error {}
const NECESSIDADE: Record<Chamado, "fome" | "higiene" | "humor"> = { fome: "fome", higiene: "higiene", carinho: "humor" };
const lutasZeradas = (): Lutas => ({ lutas: 0, vitorias: 0, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 });
/** acao que atende um chamado REAL (carinho = mau humor: elogio tambem resolve; petisco atende a fome) */
function atende(pedido: Chamado, a: AcaoDono): boolean {
  return ACAO_CHAMADO[pedido].includes(a) || (pedido === "fome" && a === "petisco") || (pedido === "carinho" && a === "elogiar");
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
  /* v5: voz propria (fala espontanea com janela e mentira) */
  rMentira!: Rng;
  men!: EstadoMentira;
  honestidadeEspecie = 1;                        /* especie com traco verificado de enganador: CMEN.honestidadeEnganador */
  /* v5: o que o extrator da historia le (motor/historia.ts). Derivado do replay: nao vai para o save nem para a
     assinatura. episodios = inicio de cada trecho de uma mesma acao do pet (fora ocioso) */
  vida5: { episodios: [number, AcaoPet][]; lutas: { tick: number; rival: string; resultado: "vitoria" | "derrota" | "empate"; lesao: boolean }[];
    sessoes: [number, Exercicio][]; anterior: AcaoPet | null } = { episodios: [], lutas: [], sessoes: [], anterior: null };
  lutas!: Lutas;
  lesionadoDesde: number | null = null;
  vitoriasVida = 0;                              /* v4: experiencia de combate (nao zera ao evoluir) */
  morte: { tick: number; causa: "lesoes" | "lesao_sem_tratar" } | null = null;
  janelasFechadas: (Janela & { desfecho: string; fim: number })[] = [];
  origem: Origem | null = null;                   /* v4: filho de um cruzamento (evento "o", o primeiro) */
  /* v4: ritmo dos estagios (evento "c" no comeco do registro); sem ele, o rapido de sempre */
  ritmo: Ritmo = "rapida";
  dur: { bebe: number; crianca: number; adolescente: number } = DUR_EVO;

  constructor(semente: number, versao: number = VERSAO_PET) {
    if (![1, 2, 3, 4, 5].includes(versao)) throw new Error("versão de pet desconhecida: " + versao);
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
    this.campanha = Object.fromEntries(CAMPANHA.map(c => [c.k, 0]));
    if (versao >= 4) {
      /* rng propria das travessuras: sorteada em TODO slot (numeros comuns), nao mexe nas outras */
      this.rTrav = criarRng(hashSemente("travessura", semente));
      this.edu = { disciplina: 0, acertos: 0, petiscos: 0, janela: null, proximo: {}, contagem: {} };
      this.lutas = lutasZeradas();
    }
    if (versao >= 5) {
      /* rng propria da mentira: duas por fala, sempre (numeros comuns), nao mexe nas outras */
      this.rMentira = criarRng(hashSemente("mentira", semente));
      this.men = { impunes: 0, acertos: 0 };
    }
  }
  get disciplina(): number { return this.versao >= 4 ? this.edu.disciplina : 0; }

  /* ---------------------------------------------------------------- heranca (pets v4) */
  /** cruza dois adultos vivos: o filho (v4) herda temperamento (media + ruido) e especie (de um dos pais) */
  static cruzar(pai: Motor, mae: Motor, sementeFilho: number, sementeHeranca: number, quem: string, ger?: [number, number]): Motor {
    const ver = (p: Motor, g?: number) => {
      if (p.estagioAtual !== "adulto") throw new Error("só adultos cruzam (Ultimate ou Mega)");
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
    this.ritmo = dur; this.dur = { bebe: b, crianca: c, adolescente: a };
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
  lugarVencido(L: number): boolean { return LUGARES[L].rivais.some(r => this.campanha[r] > 0); }
  /** desafio da campanha aberto: o primeiro sempre; os outros depois de vencer o anterior */
  desafioAberto(k: string): boolean { const L = NPC[k]!.lug; return L === 0 || this.lugarVencido(L - 1); }
  /** luta contra bot: entra no registro (rival + semente) e ensina os gambits */
  lutar(rival: string, semente: number): ResultadoLutaPet {
    if (!NOME_BOT[rival]) throw new Error("rival desconhecido: " + rival);
    if (this.versao >= 4) { this._conferirMorte(); this._vivo(); }
    if (NPC[rival] && !this.desafioAberto(rival)) throw new Error(`desafio bloqueado: vença alguém em ${LUGARES[NPC[rival]!.lug - 1].nome} antes`);
    this.log.push([this.e.tick, "l", { r: rival, s: semente }]);
    return this._lutar(rival, semente);
  }
  private _lutar(rival: string, semente: number): ResultadoLutaPet {
    /* campanha contra NPC: stats treinados absolutos; arena contra bots: normalizados ao orcamento */
    const A = lutadorPet(this, "Seu pet", !!NPC[rival]), B = lutadorBot(rival), res = jogarV2(A, B, semente);
    if (this.gp) this.gp.aprender(res, semente);
    if (this.estagioAtual === "adolescente") this.sparring++;
    if (NPC[rival] && res.pontosA === 1) this.campanha[rival]++;
    this._hist({ t: this.e.tick, quem: "luta", a: `contra ${NOME_BOT[rival]}: ${res.pontosA === 1 ? "venceu" : res.pontosA === 0 ? "perdeu" : "empatou"}` });
    let lesao = false;
    if (this.versao >= 4) {
      const L = this.lutas;
      L.lutas++;
      if (res.pontosA === 1) { L.vitorias++; this.vitoriasVida++; } else if (res.pontosA === 0) L.derrotas++; else L.empates++;
      /* lesao: so na derrota, numa rng derivada da semente da LUTA */
      lesao = res.pontosA === 0 && criarRng(hashSemente("lesao", semente)).random() < CLE.probLesao;
      if (lesao) {
        L.lesoes++;
        if (this.lesionadoDesde === null) this.lesionadoDesde = this.e.tick;
        if (L.lesoes >= CLE.lesoesMorte) this.morte = { tick: this.e.tick, causa: "lesoes" };
        this._hist({ t: this.e.tick, quem: "lesao", a: "se machucou na luta" });
      }
    }
    if (this.versao >= 5) this.vida5.lutas.push({ tick: this.e.tick, rival, lesao,
      resultado: res.pontosA === 1 ? "vitoria" : res.pontosA === 0 ? "derrota" : "empate" });
    return { res, A, B, lesao };
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
    const iv = est === "bebe" ? null : CED.intervalos[est];
    this.edu.proximo = iv ? Object.fromEntries(Object.entries(iv).map(([k, m]) => [k, t + m])) : {};
  }
  /** slots de chamado na decisao do pet (espelho de MotorEducacao._decisao_observada) */
  private _travessuras(): void {
    const t = this.e.tick, ed = this.edu;
    this._expirar();
    for (const tipo of (Object.keys(ed.proximo) as Chamado[]).sort()) {
      while (t >= ed.proximo[tipo]!) {
        ed.proximo[tipo]! += CED.intervalos[this.estagioAtual as EstagioTreino][tipo];
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
  /* ---------------------------------------------------------------- voz propria: mentira (pets v5) */
  /** h (0 a 1): sombria e sobrecarga tiram; sem sobrecarga e nao sombrio, h = 1 e o pet nunca mente */
  honestidade(): number {
    if (this.versao < 5) return 1;
    const f = this.sombria ? CMEN.fatorSombria : 1;
    return Math.max(0, Math.min(1, f * (1 - CMEN.pesoSobrecarga * this.treino.sobrecarga / 100) * this.honestidadeEspecie));
  }
  chanceMentira(): number {
    if (this.versao < 5) return 0;
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
    if (this.versao < 5) throw new Error("fala espontânea só em pets v5");
    if (!/^[a-z_]+$/.test(gatilho)) throw new Error("gatilho de fala inválido: " + gatilho);
    this._conferirMorte(); this._vivo();
    this.log.push([this.e.tick, "f", gatilho]);
    return this._falar(gatilho);
  }
  private _falar(gatilho: string): Janela | null {
    if (this.versao < 5) throw new Error("evento de fala num pet anterior ao v5");
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
    this._hist({ t, quem: "pet", a: "falou" });
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
        if (this.versao >= 5) {
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
    if (this.versao >= 5 && !s.enrolou) this.vida5.sessoes.push([t, ex]);
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
  private _evoluir(): void {
    const t = this.e.tick - TICK_INICIAL, est = this.estagioAtual, D = this.dur;
    let nova: Omit<Evolucao, "tick" | "forma"> | null = null;
    if (est === "bebe" && t >= D.bebe) {
      const cuidado = this.fracaoCuidado();
      nova = { estagio: "crianca", ramo: cuidado >= CAT.limiarCuidado ? "sereno" : "arisco", cuidado };
    } else if (est === "crianca" && t >= D.bebe + D.crianca) {
      const carater = this.caraterAgora("adolescente");
      /* sobrecarga >= 30: aviso (fala fria); nada muda na forma */
      this.falaFria = this.treino.sobrecarga >= CSO.aviso;
      nova = { estagio: "adolescente", linha: linhaDoCarater(carater), carater, sobrecarga: this.treino.sobrecarga };
    } else if (est === "adolescente" && t >= D.bebe + D.crianca + D.adolescente && this.sparring >= CAT.sparring
               && (this.versao < 4 || this.lutas.vitorias / this.lutas.lutas >= CLE.limiarTaxa)) {
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
    if (this.versao >= 5) this.men = { impunes: 0, acertos: 0 };
    if (!this.gp) this.gp = new GambitsPet();
    this.gp.semear(this.forma);
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
      ...(this.versao >= 5 ? [[this.men, this.honestidadeEspecie]] : [])]);
  }
  /** um evento do registro, sem regravar no registro (replay) */
  aplicarEvento(ev: EventoRegistro): void {
    const t = ev[0];
    if (this.e.tick !== t) throw new Error(`registro fora de ordem no tick ${t}`);
    switch (ev[1]) {
      case "t": this._avancar(ev[2]); break;
      case "d": this._aplicar(ev[2]); break;
      case "l": this._lutar(ev[2].r, ev[2].s); break;
      case "g": this._gambit(ev[2].op, ev[2].k); break;
      case "tr": this._treinar(ev[2]); break;
      case "o": this._origem(ev[2]); break;
      case "c": this._config(ev[2].dur); break;
      case "f": this._falar(ev[2]); break;
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
