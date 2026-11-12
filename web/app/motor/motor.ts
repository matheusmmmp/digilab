/* Motor com registro de eventos (espelho de engine.py + treino.py + personalidade). Event sourcing: o estado
   nunca e salvo, so o registro (acoes do dono, tempo, lutas, intervencoes, treinos); a vida e reconstruida
   reprocessando o registro. Mesma semente + mesmo registro = mesma assinatura, no mesmo runtime.
   So os pets da versao de hoje abrem: a v21 (o cerebro trocavel, o mundo, o levar pet e a luta da POC, motor/arena/) e o pet de teste do
   laboratorio (v16). Os ramos das versoes v1-v12 sairam com o descarte 6 (COMBATE-TR, R2b) e os das v13 a v19, com o combate por turnos, no
   descarte 7 (LUTA_POC, LP4; LP-6 e D-9). Alguns campos dessas versoes ficam com o valor fixo porque entram na assinatura (a educacao, a
   mentira e a obediencia, sempre zeradas; a memoria por espacos do Bandit; os gambits e as cartas, sempre vazios): a assinatura das vidas
   v21 nao muda (test/luta_poc_pet.test.ts). */
import type { ConfigCooperacao } from "./cooperacao.ts";
import {
  ACAO_CHAMADO, ACOES_DONO_JOGO_V11, CUIDADO_NA_HORA, ACOES_PET, CAT, CDJ, CHAMADO_BEBE, CHAMADO_BEBE_CORPO, CHAMADO_FOME_CORPO, CHE, CLE, CMG, EIXOS_TEMP, CSO, CT, CTR, C, DUR_CLASSICA, DUR_EVO, ESPECIES,
  TICK_INICIAL, VERSAO_PET, VERSAO_PET_LAB, VERSAO_V21, VERSAO_V17, VERSAO_V19, VERSOES_PET, CEREBROS, ehCerebroTrocavel, ehDoGrupo, ehLutaPoc, nasceNaAgua,
  nasceNaGrande, nasceComMemoriaLonga, nasceComSonoSegura, nasceComLance, nasceComTv, nasceComTvJogo, CMU_GRANDE, CMU_MVP_AGUA, ILHA_DOS_V21, ILHA_DOS_VIVOS, VERSOES_COM_SACUDIR,
} from "./constantes.ts";
import { Bandit } from "./bandit.ts";
import { LUGARES_V6, NOME_BOT, NPC, campanhaDe, lugaresDe, type Lugar } from "./bots.ts";
import { MEDALHAS, medalhasPara } from "./medalhas.ts";
import { ARENA_POR_ID, arenaDaLuta, sementeDaSerie, type Arena } from "./arenas.ts";
import { LIGA, MEDALHAS_LIGA, RIVAL_LIGA, formaLiga, nomeMegaLiga } from "./liga.ts";
import {
  INSTALACOES, LUTAS_MAX_INSTALACAO, ehInstalacao, formaRivalInstalacao, instalacaoDe, sementeTentativa,
  type IdInstalacao, type Instalacao,
} from "./instalacoes.ts";
import { ESTAGIOS_SALAO, RIVAL_SALAO, caraterDoRivalSalao, formaRivalSalao, sementeSalao } from "./salao.ts";
import { CMU_MVP, STATS } from "./constantes.ts";
import { chipDe, chipServe, itensValem, porqueItensNaoValem, pontosComChips, vagasDeChip } from "./itens.ts";
import { caraterV11, formaAdultaDe, linhaDoCarater, type QuandoCarater } from "./carater.ts";
import { CCO_CORPO_V11, CONFIG_LUTA_CORPO_LIGADA } from "./corpo.ts";
import { desejoLobos, type BracoConsequencia, type CerebroA, type ObservacaoLobos } from "./lobos.ts";
import { MotorCorpo, estadoNascimentoPy, type PoliticaCorpo } from "./motor_corpo.ts";
import { MotorCorpoMundo, type PoliticaCorpoMundo } from "./motor_corpo_mundo.ts";
import {
  MAPA_PADRAO, eventoDeixarBola, eventoDeixarComida, eventoLevarPet, eventoMudarIlha, eventoSacudirArvore, lerDeixarBola, lerDeixarComida, lerLevarPet,
  lerMudarIlha, lerSacudirArvore, noMapa, regiaoDe, tamanhoDoMapa, type Mundo, type OpcoesMundo,
} from "./mundo.ts";
import { CONFIG_CONTRATO_AGUA } from "./contrato.ts";
import { bracoV11 } from "./pet_v11.ts";
import { leituraLab, type LeituraLab } from "./digibrain/leitura.ts";
import { decodificar, decodificarV2, decodificarV4, type ConceitosDec, type ConceitosDecV4 } from "./digibrain/decodificador.ts";
import { DigiBrain } from "./digibrain/adapt.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_DIGIBRAIN_LAB_FALA, CONFIG_DIGIBRAIN_LAB_OLHAR, CONFIG_LANCE_DONO, CONFIG_LANCE_DONO_LIGADA, CONFIG_OLHAR_JOGO, CONFIG_SONO_SEGURA,
  CONFIG_SONO_SEGURA_LIGADA, CONTEUDOS_FALA, D_MAX_ILHA_GRANDE, INATOS_MODULAR,
  type ConteudoFala } from "./digibrain/constantes.ts";
import { leituraAprendido, leituraDecisao, mapaDecisao, mapaPesos, type ArestaMapa, type LeituraDecisao, type MapaDecisao } from "./digibrain.ts";
import { ConfiancaCombate } from "./confianca.ts";
import { CONFIG_ENJOO_TELA_LIGADA } from "./enjoo_tela.ts";
import { genomaVisao } from "./digibrain/genoma_visao.ts";
import { CONFIG_TELA_LIGADA, CONFIG_TV_JOGO, CONFIG_TVJOGO_LIGADA, ID_TV, lerSentidoTela, valorSentidoTela, valorSentidoTelaDesligada } from "./tv.ts";
import { lutar as lutarArena, sorteiosPorFluxo, type IdCena, type ResultadoLuta as ResultadoArena, type Stats as StatsArena, type Tiro as TiroLutaPoc, type Esquiva as EsquivaLutaPoc, type Apoio as ApoioLutaPoc, type ArenaPorEstagio as ArenaLutaPoc, type TabelaFormas as TabelaFormasPoc, type EntradaLuta as EntradaLutaArena } from "./arena/index.ts";
import { MAPA_SALAO, MAPA_TORRE, statsRivalForma, ehMapa, esquivaDaTabela, formaDaChave as formaDaChaveMotor, mapaDoLugar, naTabela, rivaisArena, statsDaLuta, statsDoPet, statsNpc, statsRivalArena, tabelaLuta } from "./luta_poc.ts";
import { condicaoDe } from "./treino.ts";
import { caraterCanonico } from "./catalogo.ts";
import { estadoInicial, observacao, temperamentoDe } from "./estado.ts";
import { NOME_EXERCICIO, chaveSprite, nomeArquetipo, nomeForma } from "./nomes.ts";
import { criarRng, hashSemente } from "./rng.ts";
import { TreinoPet, type ResultadoSessao } from "./treino.ts";
import { Vinculo } from "./vinculo.ts";
import type {
  AcaoDono, AcaoPet, Carater, Chamado, ChavesProduto, Desejo, Especie, Estagio, EstadoVida, EventoRegistro, Exercicio, Forma, FormaAdulta, FormaAdultaNormal,
  EstagioTreino, ItemHistorico, Linha, MotivoVida, Observacao, OpItem, Origem, Ramo, Ritmo, Stats, Temperamento, VersaoPet,
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
/** a luta de um pet v21 (a luta da POC, LP2): o rival, o mapa, os numeros dos dois lados, cada luta da serie (1, ou 3 na Cidadela) e se a serie
    inteira foi vitoria */
export interface ResultadoLutaPoc {
  /** o mapa da Arena e da Campanha; null nos torneios (cada luta tem o dela, em serie[k].mapa) */
  rival: string; mapa: IdCena | null; semente: number; arena: boolean; torneio: boolean;
  /** os numeros do pet; os do primeiro rival (cada luta tem os do rival dela) */
  pet: StatsArena; rivalStats: StatsArena; forma: string;
  /** cada luta jogada: com a vida com que o pet entrou, o rival (a forma na tabela), o mapa e os numeros dele */
  serie: (ResultadoArena & { vida0: number; pontosA: number; contra: string; mapa: IdCena; rivalStats: StatsArena })[];
  venceu: boolean; lesao: boolean;
  /** o tiro e a esquiva que a luta usou (a v23 em diante, ou a bancada); ausentes na luta da POC de sempre (v21 e v22). O palco refaz a luta
      com eles (src/lutaPocTela.ts, lutasDoResultado) */
  tiro?: TiroLutaPoc; esquiva?: EsquivaLutaPoc;
  /** o golpe de apoio e a arena por estagio que a luta usou (a v29, ou a bancada; LP6-4); ausentes sem eles. O palco os repassa tambem */
  apoio?: ApoioLutaPoc; arenaPorEstagio?: ArenaLutaPoc;
}
/** pets v21 (LP2b; LP-5 revista): o Palacio juntou-se a Torre de Batalha, porque na luta nova todo pet decide sozinho */
export const PALACIO_NA_TORRE = "o Palácio juntou-se à Torre de Batalha na luta nova: lute na Torre";
const lutasZeradas = (): Lutas => ({ lutas: 0, vitorias: 0, derrotas: 0, empates: 0, lesoes: 0, tratadas: 0 });

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
  temp: Temperamento;
  e: EstadoVida;
  pol: Bandit;
  /* o vinculo (o B: coerencia por situacao), a obediencia dos v2-v10 (zerada: so na assinatura) e o registro do desejo (metricas) */
  vinc: Vinculo;
  obed: { pedidos: number; recusas: number; fazerOutra: number };
  dz: RegistroDesejo;
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
  /** os feitos de cuidado que dao Bits ao Tamer (docs/PLANO_V3_MOEDA.md, secao 2; so no jogo, o app le em src/bits.ts): o chamado do bebe
      atendido, a pausa do treino atendida e o cuidado na hora certa do Rookie em diante (CUIDADO_NA_HORA). Derivado do replay: fora do
      save, do registro e da assinatura (a vida nao muda) */
  feitosCuidado: { tick: number; tipo: "chamado" | "pausa" | "cuidado" }[] = [];
  /** as chaves do produto (EventoProduto, no comeco do registro dos ovos novos); sem o evento, as duas desligadas */
  produto: Required<ChavesProduto> = { chamadoPelaFome: false, decisaoNaComida: false, chamadosPeloCorpo: false };
  /** com o chamadoPelaFome ou o chamadosPeloCorpo: o tick em que o ultimo chamado de cada tipo abriu (derivado do registro; fora da
      assinatura) */
  private ultimoChamado: Partial<Record<Chamado, number>> = {};
  private produtoLido = false;
  /** a ponte da luta (PE3): o registro tem a marca "pl" (ovo novo v16/v17); sem ela, a luta passa ao lado do corpo e do cerebro, como hoje */
  ponteLuta = false;
  /** a distancia do tiro (LUTA_POC, D-LP5-12): so a bancada do equilibrio a poe (o candidato); o jogo nao a usa ate a versao do pet da LP5-5.
      Sem ela (o padrao), a luta e a de sempre. Nao vai ao registro nem ao save */
  tiroLutaPoc: TiroLutaPoc | null = null;
  /** a esquiva pela perspicacia e pela velocidade (D-LP5-14): como o tiroLutaPoc, so a bancada a poe; null = a luta de sempre */
  esquivaLutaPoc: EsquivaLutaPoc | null = null;
  /** as chaves da LP6-1 (o golpe de apoio, a elipse pelo estagio e a tabela das formas com outro ritmo do apoio): como o tiroLutaPoc, so a
      bancada as poe (LP6-3); null = a da tabela da versao (a v29 tem o apoio e a arena, LUTA_V29; LP6-4) */
  apoioLutaPoc: ApoioLutaPoc | null = null;
  arenaLutaPoc: ArenaLutaPoc | null = null;
  formasLutaPoc: TabelaFormasPoc | null = null;
  /** as chaves da N3 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 4): como o tiroLutaPoc, so a bancada as poe (a N4); null =
      nenhuma, a luta de sempre. Nenhuma versao de pet as liga (D-N-7). Nao vai ao registro nem ao save */
  nucleoLutaPoc: Pick<EntradaLutaArena, "forcaAtr" | "tiroDoMorto" | "puloMax" | "bordaRingue"> | null = null;
  /** DC3d da CONVERSA_PET: o registro tem a marca "fu" (so o pet de teste v16): o modular decide com a subchave `fala_unidades` (o
      `chamar_atencao` em tres unidades de fala com conteudo, docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1 e A1.1); sem ela, o modular de hoje */
  falaUnidades = false;
  /** PE4: a marca "pl" tem eps (o epsilon da luta do combate por turnos lia o g_exp do modular; a luta da POC nao tem epsilon: a marca so
      fica no registro e na assinatura) */
  epsLuta = false;
  sparring = 0;
  motivos: MotivoVida[] = [];
  motivo: MotivoVida | null = null;
  nDono = 0;
  campanha: Record<string, number>;
  /* a educacao dos v4-v10 e a mentira dos v7-v10 nao existem mais; o estado delas fica zerado, so na assinatura */
  edu: Educacao;
  men: EstadoMentira;
  honestidadeEspecie = 1;                        /* especie com traco verificado de enganador: CMEN.honestidadeEnganador */
  /* v7: o que o extrator da historia le (motor/historia.ts). Derivado do replay: nao vai para o save nem para a
     assinatura. episodios = inicio de cada trecho de uma mesma acao do pet (fora ocioso) */
  vida5: { episodios: [number, AcaoPet][]; lutas: { tick: number; rival: string; resultado: "vitoria" | "derrota" | "empate"; lesao: boolean }[];
    sessoes: [number, Exercicio][]; anterior: AcaoPet | null } = { episodios: [], lutas: [], sessoes: [], anterior: null };
  /** MITOLOGIA, E0 (docs/TAREFA_V3_MITOLOGIA.md): a forca do pet na entrada de cada luta da POC (a soma dos 6 stats de statsDoPet, sem a
      condicao) e o resultado, para o evento da hybris (motor/lendas.ts). Derivado do replay, como o vida5: fora do save e da assinatura */
  forcaLutas: { tick: number; rival: string; forcaPet: number; resultado: "vitoria" | "derrota" | "empate" }[] = [];
  lutas: Lutas;
  lesionadoDesde: number | null = null;
  vitoriasVida = 0;                              /* v4: experiencia de combate (nao zera ao evoluir) */
  morte: { tick: number; causa: "lesoes" | "lesao_sem_tratar" } | null = null;
  janelasFechadas: (Janela & { desfecho: string; fim: number })[] = [];
  origem: Origem | null = null;                   /* v4: filho de um cruzamento (evento "o", o primeiro) */
  /* v8 (M1): confianca de combate e novidade por rival, recalculadas das lutas do registro */
  conf: ConfiancaCombate;
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
  /** v11: o cerebro A atras do braco da consequencia e o laco do corpo por tick, que roda a vida por baixo (o estado do pet e o do laco;
      `e` e a copia dele depois de cada passo). null nos v1-v10. Nos v12, o laco e o com o mundo fisico (MotorCorpoMundo) */
  v11: { braco: BracoConsequencia; laco: MotorCorpo } | null = null;
  /** o laboratorio (LM4; v16, VERSAO_PET_LAB): o DigiBrain modular decide no lugar do cerebro A (o `braco` fica so para o desejo e o carater,
      sem aprender); null nos outros pets. Na v17, o modular so enquanto ele e o cerebro que decide (o evento "cb") */
  get lab(): DigiBrain | null { return this.modularAtivo ? this.modular : null; }
  /** o DigiBrain modular do pet: o da v16 desde o ovo; o da v17 desde o primeiro "cb" do modular (e fica, parado, quando o A volta) */
  private modular: DigiBrain | null = null;
  /** o modular decide agora (a v16 sempre; a v17 depois de um "cb" do modular) */
  private modularAtivo = false;

  /** dois pets (docs/TAREFA_V3_COOPERACAO.md, CO4b): o pet vive no mundo de um grupo, e o tempo dele anda pelo GrupoDoJogo (motor/grupo_jogo.ts)
      um tick por vez, na vez sorteada; o `avancar` dele falha alto. Fora do grupo, false: a vida de hoje */
  readonly noGrupo: boolean;

  constructor(semente: number, versao: number = VERSAO_PET, opcoes: { parteDoMundo?: (op: OpcoesMundo) => Mundo } = {}) {
    /* so a v21 e o pet de teste (v16): os pets de antes (v1-v19, com o combate por turnos) foram descartados (os descartes 6 e 7, src/tamer.ts) */
    if (!VERSOES_PET.includes(versao) && versao !== VERSAO_PET_LAB) throw new Error(`versão de pet desconhecida: ${versao} (só a ${VERSOES_PET.join(" e a ")} e o pet de teste v${VERSAO_PET_LAB} abrem; os pets de antes, com o combate por turnos, foram descartados)`);
    this.semente = semente; this.versao = versao as VersaoPet;
    this.noGrupo = opcoes.parteDoMundo !== undefined;
    /* a v26 so existe no grupo, e o grupo so tem a v26 (CO4c) */
    if (this.noGrupo !== ehDoGrupo(versao))
      throw new Error(this.noGrupo ? `o pet do grupo e da v26, da v28, da v29 ou da v31, nao da v${versao}` : `o pet v${versao} so nasce no grupo, com o irmao`);
    /* temperamento do ovo: rng propria, nao mexe nas outras */
    this.temp = temperamentoDe(semente);
    /* o Bandit nao decide nem aprende para o pet; fica so a memoria por espacos dele, como o lobo de memoria e emocao (D-W7 do #201): a
       emocao, a fala e as lembrancas */
    this.e = estadoInicial(); this.pol = new Bandit(this.temp, versao);
    const braco = bracoV11(), m = this;
    /* o laco chama o cerebro por aqui: o desejo antes de decidir (como o gabarito da vontade) e, depois da decisao, o que o Motor
       registra dela (nada que mexa no estado do pet: o efeito da acao e do laco) */
    /* a v25 nasce com a memoria de lugar de 128 celulas (IG6): o modular dela e criado com esse alcance (no "cb") */
    if (nasceComMemoriaLonga(versao)) this.alcanceMemoria = D_MAX_ILHA_GRANDE;
    const lab = versao === VERSAO_PET_LAB ? new DigiBrain() : null;
    this.modular = lab; this.modularAtivo = lab !== null;
    const politicaA: PoliticaCorpoMundo = {
      agir(o, rng) {
        const t = m.v11!.laco.estado.tick, d = m.desejoAtual(o, t), a = braco.agir(o, rng);
        m._decisaoV11(o, a, t, d);
        return a;
      },
      observar: tr => braco.observar(tr),
      consequenciaCorpo: (a, oc, depois) => braco.consequenciaCorpo(a, oc, depois),
      receberAcaoDono: (a, tick) => braco.receberAcaoDono(a, tick),
      mudancaNoCorpo: (antes, depois) => braco.mudancaNoCorpo(antes, depois),
    };
    /* o pet de teste (v16): o mesmo embrulho, com o DigiBrain modular no lugar do A; o laco com a chave do laboratorio da o mundo ao cerebro,
       pergunta o alvo e chama o consequenciaMundo */
    /* a v17 (o cerebro trocavel): cada gancho vai ao cerebro que decide agora. A troca e um evento entre decisoes, e o laco chama o agir,
       o alvo e as consequencias de uma decisao no mesmo passo: a decisao inteira fica com um cerebro so */
    const qual = (): DigiBrain | null => m.modularAtivo ? m.modular : null;
    const politicaTrocavel: PoliticaCorpoMundo = {
      agir(o, rng) {
        const b = qual(), t = m.v11!.laco.estado.tick, d = m.desejoAtual(o, t), a = b ? b.agir(o, rng) : braco.agir(o, rng);
        m._decisaoV11(o, a, t, d);
        return a;
      },
      observar: tr => { const b = qual(); if (b) b.observar(tr); else braco.observar(tr); },
      consequenciaCorpo: (a, oc, depois) => { const b = qual(); if (b) b.consequenciaCorpo(a, oc, depois); else braco.consequenciaCorpo(a, oc, depois); },
      receberAcaoDono: (a, tick) => { const b = qual(); if (b) b.receberAcaoDono(a, tick); else braco.receberAcaoDono(a, tick); },
      mudancaNoCorpo: (antes, depois) => { const b = qual(); if (b) b.mudancaNoCorpo(); else braco.mudancaNoCorpo(antes, depois); },
      /* a TV no cerebro (a v32; D-GV-CEREBRO-5): as TVs a vista e o agrado vao ao modular que decide; com o A, o olhar e a regra provisoria da
         P1c (o pet olha quando esta parado, acordado e com a TV no raio: o olhandoTela devolve a TV, como sem o gancho no Python) e nao ha agrado.
         Os tres ganchos so existem na v32: o laco so os le com a TV ligada */
      ...(nasceComTv(versao) ? {
        verTela: (linhas: [number, number, number, number][]) => { const b = qual(); if (b) b.verTela(linhas); },
        olhandoTela: () => { const b = qual(); return b ? b.olhandoTela() : ID_TV; },
        agradoTela: (leituras: Readonly<Record<string, number>>) => { const b = qual(); return b ? b.agradoTela(leituras) : null; },
      } : {}),
      escolherAlvo: (acao, candidatos, percepcao, u) => {
        const b = qual();
        if (!b) throw new Error("o laco pediu o alvo ao cerebro A (so o modular escolhe o alvo)");
        return b.escolherAlvo(acao, candidatos, percepcao, u);
      },
      consequenciaMundo: (a, oc, depois) => {
        const b = qual();
        if (!b) throw new Error("o laco deu a consequencia do mundo ao cerebro A (so o modular a recebe)");
        b.consequenciaMundo(a, oc, depois);
      },
      /* o lance do dono (BOLA_BRINCAR, BB-4 e BB-6): o gancho do convite existe so com o modular decidindo; com o A, o laco nao o acha (so a
         bola se mexe, no relogio de sempre) */
      get bolaDoDono() {
        const b = qual();
        return b === null ? undefined : (convite: boolean) => b.bolaDoDono(convite);
      },
    };
    /* o modular do pet de teste e lido a cada gancho: a marca "fu" (DC3d) o troca, antes da primeira decisao, pelo da `fala_unidades` */
    const doLab = (): DigiBrain => m.modular!;
    const politica: PoliticaCorpoMundo = ehCerebroTrocavel(versao) ? politicaTrocavel : lab === null ? politicaA : {
      agir(o, rng) {
        const t = m.v11!.laco.estado.tick, d = m.desejoAtual(o, t), a = doLab().agir(o, rng);
        m._decisaoV11(o, a, t, d);
        return a;
      },
      observar: tr => doLab().observar(tr),
      consequenciaCorpo: (a, oc, depois) => doLab().consequenciaCorpo(a, oc, depois),
      receberAcaoDono: (a, tick) => doLab().receberAcaoDono(a, tick),
      mudancaNoCorpo: () => doLab().mudancaNoCorpo(),
      escolherAlvo: (acao, candidatos, percepcao, u) => doLab().escolherAlvo(acao, candidatos, percepcao, u),
      consequenciaMundo: (a, oc, depois) => doLab().consequenciaMundo(a, oc, depois),
    };
    /* o laco com o mundo fisico (MV-1), o do produto (CMU_MVP: sem arvores, so a racao do jogador; a opcao 1 do Matheus de 2026-10-24);
       a regra de cada decisao vai ao registro do mundo, como o ultima_regra do Python */
    const laco = new MotorCorpoMundo(politica, semente, CCO_CORPO_V11, estadoNascimentoPy(TICK_INICIAL),
                                     { regra: () => braco.cerebro.ultimaRegra, digibrain: lab !== null,
                                       /* a v24 nasce na ilha grande (IG4); a v22 e a v23, na ilha com agua de 64 x 30 (IA4); as tres com o
                                          controlador do contrato. As outras, no mundo sem agua */
                                       cfgMundo: nasceNaGrande(versao) ? CMU_GRANDE : nasceNaAgua(versao) ? CMU_MVP_AGUA : CMU_MVP,
                                       ...(nasceNaGrande(versao) || nasceNaAgua(versao) ? { contrato: CONFIG_CONTRATO_AGUA } : {}),
                                       bolaNoGolpe: ehCerebroTrocavel(versao),
                                       /* a v30 e a v31 nascem com o lance do dono (BOLA_BRINCAR, BB-7): o Brincar joga a bola */
                                       ...(nasceComLance(versao) ? { lance: CONFIG_LANCE_DONO_LIGADA } : {}),
                                       /* a v32: o orgao da tela no corpo e a TV do jogo no mundo, pela fonte "evento" (o evento "st") */
                                       /* a v35 e a v36: a TV no jogo (a TV desligada e o ir ate a TV; D-GV-TVJOGO) e o enjoo da imagem no corpo
                                          (a ConfigEnjooTela do #875; a decisao E) */
                                       ...(nasceComTv(versao) ? { tela: { tela: CONFIG_TELA_LIGADA, tv: CONFIG_TV_JOGO,
                                                                          ...(nasceComTvJogo(versao) ? { tvJogo: CONFIG_TVJOGO_LIGADA, enjoo: CONFIG_ENJOO_TELA_LIGADA } : {}) } } : {}),
                                       ...(opcoes.parteDoMundo ? { parteDoMundo: opcoes.parteDoMundo } : {}) });     // o pet de teste (v16): a bola de antes; a v21, a bola no golpe
    this.v11 = { braco, laco };
    this.e = laco.estado;
    /* o vinculo B (coerencia por situacao, sem pedido), sem obediencia */
    this.vinc = new Vinculo(true);
    this.obed = { pedidos: 0, recusas: 0, fazerOutra: 0 };
    this.dz = { atual: null, vontades: 0, cumpridas: 0, abertas: [], tVontade: 0 };
    this.tracos = Object.fromEntries(ACOES_PET.map(a => [a, 1 / ACOES_PET.length])) as Record<AcaoPet, number>;
    /* especie: sorteada pela semente (ovo). Evolucao (arvore V2.1): derivada do registro, forma travada em cada transicao */
    this.especie = ESPECIES[hashSemente("especie", semente) % ESPECIES.length];
    this.forma = { esp: this.especie, est: "bebe" };
    this.treino = new TreinoPet(this.especie);
    /* campanha: vitorias por desafio (derivadas das lutas do registro) */
    this.campanha = Object.fromEntries(campanhaDe(versao).map(c => [c.k, 0]));
    this.edu = { disciplina: 0, acertos: 0, petiscos: 0, janela: null, proximo: {}, contagem: {} };
    this.lutas = lutasZeradas();
    this.men = { impunes: 0, acertos: 0 };
    /* v8 (M1): a confianca de combate e a novidade por rival (estado derivado das lutas "l"; nenhum evento novo) */
    this.conf = new ConfiancaCombate();
  }
  /** o cerebro A do pet */
  get cerebro(): CerebroA | null { return this.v11 ? this.v11.braco.cerebro : null; }
  /** v11: a leitura do painel DigiBrain (digibrain.ts): a da ultima decisao do cerebro (null antes da primeira), o "o que aprendeu"
      na observacao de agora (o desvio aprendido, a base da vontade) e o mapa dos pesos. null nos v1-v10 (PW-7). So le: nao muda o
      cerebro nem a rng */
  digibrain(): {
    decisao: LeituraDecisao | null; aprendido: ReturnType<typeof leituraAprendido>;
    mapa: { receptores: readonly string[]; arestas: ArestaMapa[]; acesas: MapaDecisao | null };
  } | null {
    const c = this.cerebro;
    if (c === null) return null;
    const m = c.ultimoMotivo, ap = c.cfg.aprendiz;
    if (ap === undefined) throw new Error("o mapa dos pesos precisa do teto do aprendiz");
    return {
      decisao: m === null ? null : leituraDecisao(m, c.prior[m.regra][m.acao], c.escala, c.receptoresNovos),
      aprendido: leituraAprendido(c.desvioAprendido(this.observacaoAgora())),
      /* o mapa dos pesos: as arestas com os pesos de agora e as acesas na ultima decisao (o termo da hora da decisao) */
      mapa: {
        receptores: c.receptoresNovos,
        arestas: mapaPesos(c.prior, c.pesos, c.priorCorpo, c.pesosCorpo, c.escala, ap.teto, c.receptoresNovos),
        acesas: m === null ? null : mapaDecisao(m, c.prior[m.regra][m.acao], c.escala, c.receptoresNovos),
      },
    };
  }
  /** o laboratorio (v16): a leitura do ultimo motivo do DigiBrain modular para o painel (digibrain/leitura.ts); null nos outros pets e antes da
      primeira decisao. So le */
  leituraLab(): LeituraLab | null { return this.lab === null ? null : leituraLab(this.lab); }
  /** os conceitos do `dec-v1` sobre o ultimo motivo do modular (DC1); so le, nao muda a vida; null sem modular ou antes da primeira decisao */
  conceitosDec(versao: "dec-v1" | "dec-v2" = "dec-v1"): ConceitosDec | null {
    const l = this.lab, mo = l === null ? null : l.ultimoMotivo;
    if (l === null || mo === null) return null;
    if (versao === "dec-v1") return decodificar(mo, l.S);
    /* dec-v2 (DC2b): o episodio recuperado nesta decisao, lido da memoria agora; se ja saiu dela (consolidacao ou capacidade), o conceito vai sem `episodio` */
    const rec = (mo["lembranca"] as Record<string, any> | undefined)?.["recuperado"] ?? null;
    const ep = rec === null ? undefined : l.mem.guardados().find(e => e.id === rec);
    return decodificarV2(mo, l.S, ep === undefined ? null : (ep as unknown as Record<string, any>));
  }
  /** a fala do assistir (docs/futuro/fala_do_assistir.md, FA-2): o `dec-v4` sobre o ultimo motivo do modular, com o motivo anterior; null
      nos pets sem o olhar com o enjoo (antes da v35), sem modular ou antes da primeira decisao. So le, nao muda a vida */
  conceitosAssistir(): ConceitosDecV4 | null {
    const l = this.lab;
    if (l === null || !nasceComTvJogo(this.versao) || l.motivos.length === 0) return null;
    const n = l.motivos.length;
    return decodificarV4(l.motivos[n - 1]!, n > 1 ? l.motivos[n - 2]! : null, l.S);
  }
  /** DC3d da CONVERSA_PET: o conteudo da unidade de fala que o modular escolheu na ultima decisao (fome, higiene ou solidao), so com a
      marca "fu"; null sem ela, sem decisao ainda ou quando a ultima decisao nao foi uma fala. So le */
  conteudoDaFala(): ConteudoFala | null {
    const l = this.lab, mo = l === null ? null : l.ultimoMotivo;
    if (!this.falaUnidades || l === null || mo === null || mo["acao"] !== "chamar_atencao") return null;
    const c = (mo["escolha"] as unknown[])[1];
    if (!(CONTEUDOS_FALA as readonly unknown[]).includes(c)) throw new Error(`a fala da decisao ${String(mo["k"])} sem conteudo com a marca "fu"`);
    return c as ConteudoFala;
  }
  /** v12: o mundo fisico do pet (null nos v1-v11). A tela so le */
  get mundo(): Mundo | null { return this.v11 && this.v11.laco instanceof MotorCorpoMundo ? this.v11.laco.mundo : null; }
  /** a observacao de agora, a que o pet le: nos v11, com os receptores do corpo */
  /** so le: com a TV (a v32), sem entregar a tela ao corpo de novo (MotorCorpo.leituraObservacao; D-GV-CEREBRO-7) */
  observacaoAgora(): ObservacaoLobos { return this.v11 ? this.v11.laco.leituraObservacao() : observacao(this.e); }

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
    if (this.nDecisoes || this.nDono || this.e.tick !== TICK_INICIAL || this.origem) throw new Error("configuração fora do começo do registro");
    if (dur !== "rapida" && dur !== "classica") throw new Error("ritmo desconhecido: " + dur);
    const [b, c, a] = dur === "classica" ? DUR_CLASSICA : [DUR_EVO.bebe, DUR_EVO.crianca, DUR_EVO.adolescente];
    this.ritmo = dur; this.dur = { bebe: b, crianca: c, adolescente: a, adulto: dur === "classica" ? CMG.durClassica : CMG.durRapida };
  }
  /** as chaves do produto, uma vez, no comeco do registro (antes de qualquer decisao, acao do dono ou avanco; depois do ritmo e
      da origem, se houver). O jogo liga nos ovos novos (src/produto.ts); a pesquisa e os gabaritos nunca chamam */
  ligarProduto(ch: ChavesProduto): void {
    const v: ChavesProduto = { chamadoPelaFome: ch.chamadoPelaFome, decisaoNaComida: ch.decisaoNaComida,
      ...(ch.chamadosPeloCorpo === undefined ? {} : { chamadosPeloCorpo: ch.chamadosPeloCorpo }) };
    this._produto(v);
    this.log.push([this.e.tick, "p", v]);
  }
  private _produto(ch: unknown): void {
    /* as duas chaves de 2026-10-29, ou as tres desde 2026-10-30 */
    const nomes = ch && typeof ch === "object" ? Object.keys(ch).sort().join() : "";
    if ((nomes !== "chamadoPelaFome,decisaoNaComida" && nomes !== "chamadoPelaFome,chamadosPeloCorpo,decisaoNaComida")
        || !Object.values(ch as object).every(x => typeof x === "boolean"))
      throw new Error(`chaves do produto inválidas: ${JSON.stringify(ch)}`);
    if (this.produtoLido || this.nDecisoes || this.nDono || this.e.tick !== TICK_INICIAL)
      throw new Error("as chaves do produto vão uma vez, no começo do registro");
    this.produto = { chamadosPeloCorpo: false, ...(ch as ChavesProduto) }; this.produtoLido = true;
    (this.v11!.laco as MotorCorpoMundo).decidirNaComida = this.produto.decisaoNaComida;
  }
  /** a ponte da luta (PE3), uma vez, no comeco do registro de um ovo v16 ou v17 (depois das chaves do produto e do "cb" do ovo): a luta passa a
      entregar o resumo ao corpo e, com o modular ativo, ao DigiBrain. O jogo grava nos ovos novos (src/produto.ts); a pesquisa e os gabaritos
      nunca chamam */
  ligarPonteLuta(eps = false): void {
    /* PE4: com `eps`, a marca e { luta: true, eps: true } e o epsilon da luta passa a ler o g_exp do modular; sem ela ({ luta: true }, os
       saves da PE3) o epsilon e o de hoje, byte a byte */
    const v = eps ? { luta: true as const, eps: true as const } : { luta: true as const };
    this._ponteLuta(v);
    this.log.push([this.e.tick, "pl", v]);
  }
  private _ponteLuta(v: unknown): void {
    const chaves = v && typeof v === "object" ? Object.keys(v).join() : "";
    if (!v || typeof v !== "object" || (chaves !== "luta" && chaves !== "luta,eps") || (v as { luta: unknown }).luta !== true
      || (chaves === "luta,eps" && (v as { eps: unknown }).eps !== true))
      throw new Error(`marca da ponte da luta inválida: ${JSON.stringify(v)}`);
    if (!ehCerebroTrocavel(this.versao) && this.versao !== VERSAO_PET_LAB) throw new Error(`só os pets v${VERSAO_PET_LAB} e v${VERSAO_V17} (e a v18, a v17 com o empurrão) têm a ponte da luta (este é v${this.versao})`);
    if (this.ponteLuta || this.nDecisoes || this.nDono || this.e.tick !== TICK_INICIAL)
      throw new Error("a marca da ponte da luta vai uma vez, no começo do registro");
    this.ponteLuta = true; this.epsLuta = chaves === "luta,eps";
    (this.v11!.laco as MotorCorpoMundo).corpo.luta = CONFIG_LUTA_CORPO_LIGADA;
    this.modular?.ligarLutaMemoria();                    // o modular da v16 e o da v17 com o "cb" do ovo (o "cb" de depois liga em _trocarCerebro)
  }
  /** DC3d da CONVERSA_PET: a fala com conteudo, uma vez, no comeco do registro de um pet de teste v16 (depois das chaves do produto e da ponte
      da luta). O jogo grava no ovo de teste novo so com a preferencia de tela ligada (src/lab.ts); a pesquisa e os gabaritos nunca chamam */
  ligarFalaUnidades(): void {
    const v = { fala: true as const };
    this._falaUnidades(v);
    this.log.push([this.e.tick, "fu", v]);
  }
  private _falaUnidades(v: unknown): void {
    if (!v || typeof v !== "object" || Object.keys(v).join() !== "fala" || (v as { fala: unknown }).fala !== true)
      throw new Error(`marca da fala com conteúdo inválida: ${JSON.stringify(v)}`);
    if (this.versao !== VERSAO_PET_LAB) throw new Error(`só o pet de teste (v${VERSAO_PET_LAB}) tem a fala com conteúdo (este é v${this.versao})`);
    if (this.falaUnidades || this.nDecisoes || this.nDono || this.e.tick !== TICK_INICIAL || this.modular === null || this.modular.k !== 0)
      throw new Error("a marca da fala com conteúdo vai uma vez, no começo do registro");
    this.falaUnidades = true;
    /* o modular de hoje sai sem ter decidido; o novo fica com o alcance da memoria do pet (IG6; no pet de teste, o de sempre) */
    this.modular = new DigiBrain(CONFIG_DIGIBRAIN_LAB_FALA, { ...INATOS_MODULAR, d_max: this.alcanceMemoria } as typeof INATOS_MODULAR, this.ponteLuta);
  }
  registrarOrigem(o: Origem): void {
    if (this.log.some(ev => ev[1] !== "c" && ev[1] !== "p" && ev[1] !== "pl" && ev[1] !== "fu")) throw new Error("a origem precisa ser o primeiro evento do registro");
    this.log.push([this.e.tick, "o", o]);
    this._origem(o);
  }
  private _origem(o: Origem): void {
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
  /* ---------------------------------------------------------------- a Liga dos Lideres (pets v6; liga.ts) */
  /** por que o pet nao pode desafiar a Liga agora (null: pode). A entrada pede as 6 medalhas, que o pet conhece pelo evento "u" (o
      motor nunca le o Tamer) */
  porqueNaoLiga(): string | null {
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
    if (this.morte) return "o pet morreu";
    if (x.id === "palacio") return PALACIO_NA_TORRE;
    if (this.estagioAtual === "bebe") return "o In-Training ainda não luta na Fronteira";
    if (!this.fronteira) return `a ${x.nome} abre depois do título da Liga dos Líderes`;
    return null;
  }
  /** a semente da proxima tentativa deste pet na instalacao (sai do registro: a semente do pet e quantas tentativas ele ja fez ali) */
  sementeInstalacao(id: IdInstalacao): number { return sementeTentativa(this.semente, id, this.instalacoes[id].tentativas + 1); }
  /* ---------------------------------------------------------------- o Salao da Fronteira (pets v6; salao.ts) */
  /** por que o pet nao pode lutar no Salao agora (null: pode): v6, vivo, do Rookie ao Mega, e o titulo do Tamer (evento "f") */
  porqueNaoSalao(): string | null {
    if (this.morte) return "o pet morreu";
    if (!ESTAGIOS_SALAO.includes(this.estagioAtual)) return "o In-Training ainda não luta na Fronteira";
    if (!this.fronteira) return "o Salão abre depois do título da Liga dos Líderes";
    return null;
  }
  /** a semente da proxima luta deste pet no Salao (sai do registro: a semente do pet e quantas vezes ele ja lutou la) */
  sementeSalao(): number { return sementeSalao(this.semente, this.salao.tentativas + 1); }
  /** a ponte da luta (PE3; docs/TAREFA_V3_PONTE_LUTA.md, 3.2 e 3.7): o dano da luta (da vida do comeco ate a do fim) e a vida maxima viram a
      vida perdida em S; o corpo recebe o resumo (a dor, com qualquer cerebro), e o modular ativo tambem; com o A ativo o modular esta parado
      e nao recebe nada (a regra do #562). O formato do resumo (rival, resultado, vida perdida em S) nao muda (PONTE_LUTA). Sem rng */
  private _aplicarResumo(rival: string, resultado: number, dano: number, hpMax: number): void {
    if (!(hpMax > 0)) throw new Error(`vida maxima da luta invalida: ${hpMax}`);
    const s = (this.v11!.laco as MotorCorpoMundo).corpo.S;
    const vidaPerdidaS = Math.min(s, Math.max(0, Math.round(dano * s / hpMax)));
    const laco = this.v11!.laco as MotorCorpoMundo;
    laco.aplicarResumoLuta(rival, resultado, vidaPerdidaS);
    if (this.lab !== null) this.lab.receberLuta(rival, resultado, vidaPerdidaS, laco.estado.tick);
  }
  /* ---------------------------------------------------------------- a luta da POC (pets v21; docs/TAREFA_V3_LUTA_POC.md, LP2) */
  /** a forma do pet na tabela da luta (a chave do sprite) */
  get formaLutaPoc(): string { return chaveSprite(this.forma); }
  /** os numeros do pet na luta da POC agora: os 6 stats (especie, carater, forma, treino e chips de stat) e a condicao do cuidado */
  statsLutaPoc(): StatsArena {
    /* a tabela da luta da versao do pet (a v23 tem a dela; LP5-5); o eixo atento do carater so entra na esquiva */
    const T = tabelaLuta(this.versao), car = this.carater();
    return statsDaLuta(statsDoPet(this.forma, car, this.pontosDeLuta(), T), this.forma.est, condicaoDe(this.e.saude), T, car?.atento ?? 0);
  }
  /** os rivais da Arena para este pet: as formas do estagio dele */
  rivaisArenaPoc(): string[] { return rivaisArena(this.estagioAtual); }
  /** por que o pet nao pode lutar com este rival neste mapa (null: pode). Arena: uma forma do estagio do pet, num dos 8 mapas. Campanha: um
      NPC da campanha deste pet, com o desafio aberto, no mapa do lugar dele (LP-4). Os torneios (LP2b): a Liga, a Torre de Batalha e o
      Salao, sem mapa no evento (cada luta tem o dela), com as entradas e as sementes de sempre; o Palacio juntou-se a Torre (LP-5) */
  porqueNaoLutaPoc(rival: string, mapa: unknown, semente?: number): string | null {
    if (!ehLutaPoc(this.versao)) return this.versao === VERSAO_PET_LAB ? `o pet de teste (v${VERSAO_PET_LAB}) não luta: a luta em tempo real é dos pets v${VERSAO_V21}` : `só os pets v${VERSAO_V21} lutam (este é v${this.versao})`;
    if (this.morte) return "o pet morreu";
    if (rival === RIVAL_LIGA || ehInstalacao(rival) || rival === RIVAL_SALAO) {
      if (mapa !== undefined && mapa !== null) return `os torneios não escolhem mapa: cada luta tem o dela (${JSON.stringify(mapa)})`;
      if (rival === RIVAL_LIGA) return this.porqueNaoLiga();
      if (rival === RIVAL_SALAO) {
        const e = this.porqueNaoSalao(); if (e) return e;
        if (semente !== undefined && semente !== this.sementeSalao()) return `a semente da luta no Salão sai do registro do pet: ${this.sementeSalao()}, não ${semente}`;
        return null;
      }
      if (rival === "palacio") return PALACIO_NA_TORRE;
      const e = this.porqueNaoInstalacao(rival); if (e) return e;
      if (semente !== undefined && semente !== this.sementeInstalacao(rival)) return `a semente da tentativa na ${instalacaoDe(rival).nome} sai do registro do pet: ${this.sementeInstalacao(rival)}, não ${semente}`;
      return null;
    }
    if (!ehMapa(mapa)) return `mapa desconhecido: ${JSON.stringify(mapa)}`;
    if (NPC[rival]) {
      if (!(rival in this.campanha)) return `${NPC[rival]!.nome} não está na campanha deste pet`;
      if (!this.desafioAberto(rival)) return `desafio bloqueado: vença alguém em ${this.lugares[this.lugarDe(rival) - 1].nome} antes`;
      const m = mapaDoLugar(this.lugares[this.lugarDe(rival)]);
      if (mapa !== m) return `a luta contra ${NPC[rival]!.nome} é no mapa do lugar (${m}), não em ${mapa}`;
      return null;
    }
    if (!naTabela(rival)) return `rival desconhecido: ${rival}`;
    if (!this.rivaisArenaPoc().includes(rival)) return `${rival} não é do estágio do pet (${this.estagioAtual})`;
    return null;
  }
  /** a luta da POC: entra no registro (rival, semente e, fora dos torneios, o mapa) e conta como as lutas de sempre (a confianca, a lesao, o
      sparring, a campanha, os torneios e a ponte da luta). Sem carta e sem regras de combate (LP2, decisao 6). Nos torneios, `mapa` e null */
  lutarPoc(rival: string, semente: number, mapa: IdCena | null): ResultadoLutaPoc {
    this._conferirMorte(); this._vivo();
    if (!Number.isInteger(semente)) throw new Error(`semente da luta inválida: ${semente}`);
    const erro = this.porqueNaoLutaPoc(rival, mapa, semente);
    if (erro) throw new Error(erro);
    this.log.push([this.e.tick, "l", mapa === null ? { r: rival, s: semente } : { r: rival, s: semente, m: mapa }]);
    return this._lutarPoc(rival, semente, mapa ?? undefined);
  }
  /** o rival da luta k da serie (null: a serie acabou): a forma na tabela, os numeros, o mapa e o texto do historico */
  private _rivalPoc(rival: string, semente: number, k: number, mapa: IdCena | undefined, est: Estagio): { forma: string; stats: StatsArena; mapa: IdCena; nome: string } | null {
    if (rival === RIVAL_LIGA) {
      if (k >= LIGA.length) return null;
      const f = formaLiga(k), x = LIGA[k];
      return { forma: chaveSprite(f), stats: statsRivalForma(f, caraterCanonico(x.adulta), tabelaLuta(this.versao), tabelaLuta(this.versao).fatorRival.liga), mapa: mapaDoLugar(LUGARES_V6[ARENA_POR_ID[x.arena].lugar]),
        nome: `na Liga dos Líderes, contra ${nomeMegaLiga(k)} de ${NOME_BOT[x.lider]}` };
    }
    if (ehInstalacao(rival)) {
      if (k >= LUTAS_MAX_INSTALACAO) return null;
      const f = formaRivalInstalacao(semente, k);
      return { forma: chaveSprite(f), stats: statsRivalForma(f, caraterCanonico(f.adulta as FormaAdultaNormal), tabelaLuta(this.versao), tabelaLuta(this.versao).fatorRival.torre), mapa: MAPA_TORRE,
        nome: `na ${instalacaoDe(rival).nome}, contra ${nomeForma(f)}` };
    }
    if (rival === RIVAL_SALAO) {
      if (k >= 1) return null;
      const f = formaRivalSalao(semente, est);
      return { forma: chaveSprite(f), stats: statsRivalForma(f, caraterDoRivalSalao(f), tabelaLuta(this.versao), tabelaLuta(this.versao).fatorRival.salao), mapa: MAPA_SALAO, nome: `no Salão, contra ${nomeForma(f)}` };
    }
    /* das regras das arenas dos lideres fica so a serie da Cidadela (LP2, decisao 5): 3 lutas sem cura para o pet; o lider volta inteiro */
    const npc = !!NPC[rival], n = npc ? arenaDaLuta(rival, this.versao)?.lutas ?? 1 : 1;
    if (k >= n) return null;
    return { forma: rival, stats: npc ? statsNpc(rival, tabelaLuta(this.versao)) : statsRivalArena(rival, tabelaLuta(this.versao)), mapa: mapa!,
      nome: `contra ${npc ? NOME_BOT[rival] : nomeForma(formaDaChaveMotor(rival))}${n > 1 ? ` (luta ${k + 1} de ${n})` : ""}` };
  }
  private _lutarPoc(rival: string, semente: number, mapa: unknown): ResultadoLutaPoc {
    /* no replay tambem: a entrada, o rival, o mapa e a semente */
    if (!Number.isInteger(semente)) throw new Error(`luta no registro com a semente inválida: ${semente}`);
    const erro = this.porqueNaoLutaPoc(rival, mapa, semente);
    if (erro) throw new Error(`luta no registro sem poder: ${erro}`);
    const liga = rival === RIVAL_LIGA, inst = ehInstalacao(rival) ? instalacaoDe(rival) : null, salao = rival === RIVAL_SALAO;
    const npc = !!NPC[rival], torneio = liga || !!inst || salao, forma = this.formaLutaPoc, est = this.estagioAtual;
    const pet = this.statsLutaPoc();
    /* o tiro e a esquiva: os da bancada, se ela os pos; senao, os da tabela da versao (a v21 e a v22, nenhum: a luta da POC) */
    const T = tabelaLuta(this.versao), tiro = this.tiroLutaPoc ?? T.tiro, esquiva = this.esquivaLutaPoc ?? esquivaDaTabela(T);
    /* o golpe de apoio e a arena por estagio: os da bancada, se ela os pos; senao, os da tabela da versao (so a v29; LP6-4) */
    const apoio = this.apoioLutaPoc ?? T.apoio ?? null, arenaPorEstagio = this.arenaLutaPoc ?? T.arenaPorEstagio ?? null;
    /* a forca do pet para o oraculo (MITOLOGIA E0): a soma dos 6 stats pelo peso de sempre, a mesma em todas as versoes */
    const base = statsDoPet(this.forma, this.carater(), this.pontosDeLuta()), forcaBase = STATS.reduce((t, k) => t + base[k], 0);
    const serie: ResultadoLutaPoc["serie"] = [];
    let vida0 = pet.hp, lesao = false, n = 0;
    const ordemL = this.nEventosLuta++;
    /* sem cura entre as lutas de uma serie (a Cidadela, a Liga e a Torre): o pet leva a vida de uma luta para a outra; cada rival entra inteiro */
    for (let k = 0; ; k++) {
      const rv = this._rivalPoc(rival, semente, k, mapa as IdCena | undefined, est);
      if (!rv) break;
      n = k + 1;
      const s = sementeDaSerie(semente, k);
      const r = lutarArena({ cena: rv.mapa, semente: s, a: { forma, stats: pet, ...(k ? { vida0 } : {}) }, b: { forma: rv.forma, stats: rv.stats }, ...(tiro ? { tiro } : {}), ...(esquiva ? { esquiva } : {}),
        ...(apoio ? { apoio } : {}), ...(arenaPorEstagio ? { arenaPorEstagio } : {}), ...(this.nucleoLutaPoc ?? {}) }, sorteiosPorFluxo(s), this.formasLutaPoc ?? undefined);
      const pontosA = r.vencedor === "a" ? 1 : r.vencedor === "b" ? 0 : 0.5, res = pontosA === 1 ? 1 : pontosA === 0 ? -1 : 0;
      serie.push({ ...r, vida0, pontosA, contra: rv.forma, mapa: rv.mapa, rivalStats: rv.stats });
      const chave = rivalDaConfianca(rival, semente, k, est);
      const rc = this.conf ? this.conf.registrar(this.e.tick, chave, res, this.temp.sensibilidade) : null;
      if (rc) this.confEvento.push(ordemL);
      if (this.ponteLuta) this._aplicarResumo(chave, res, Math.max(0, vida0 - r.vidaA), pet.hp);
      if (this.estagioAtual === "adolescente") this.sparring++;
      this._hist({ t: this.e.tick, quem: "luta", a: `${rv.nome}${inst || liga ? ` (luta ${k + 1})` : ""}: ${pontosA === 1 ? "venceu" : pontosA === 0 ? "perdeu" : "empatou"}` });
      const L = this.lutas;
      L.lutas++;
      if (pontosA === 1) { L.vitorias++; this.vitoriasVida += rc ? rc.novidade : 1; } else if (pontosA === 0) L.derrotas++; else L.empates++;
      /* lesao: so na derrota, numa rng derivada da semente da LUTA (como sempre) */
      if (pontosA === 0 && criarRng(hashSemente("lesao", s)).random() < CLE.probLesao) {
        lesao = true;
        L.lesoes++;
        if (this.lesionadoDesde === null) this.lesionadoDesde = this.e.tick;
        if (L.lesoes >= CLE.lesoesMorte) this.morte = { tick: this.e.tick, causa: "lesoes" };
        this._hist({ t: this.e.tick, quem: "lesao", a: "se machucou na luta" });
      }
      vida0 = r.vidaA;
      if (pontosA !== 1) break;
    }
    const ult = serie[serie.length - 1];
    /* a serie inteira vencida: o desafio da Campanha (na Cidadela, as 3), o titulo da Liga (as 6), a vitoria no Salao; na Torre, so chegando
       ao teto (ela vai ate a primeira que nao for vitoria) */
    const venceu = ult.pontosA === 1 && serie.length === n && (!inst || n === LUTAS_MAX_INSTALACAO);
    if (npc && venceu) this.campanha[rival]++;
    if (liga) { this.liga.tentativas++; if (venceu) this.liga.titulos++; }
    if (salao) { this.salao.tentativas++; if (venceu) this.salao.vitorias++; }
    if (inst) {
      const x = this.instalacoes[inst.id], v = serie.filter(r => r.pontosA === 1).length;
      x.tentativas++; x.ultima = v; x.recorde = Math.max(x.recorde, v);
    }
    this.vida5.lutas.push({ tick: this.e.tick, rival, lesao, resultado: ult.pontosA === 1 ? "vitoria" : ult.pontosA === 0 ? "derrota" : "empate" });
    this.forcaLutas.push({ tick: this.e.tick, rival, forcaPet: forcaBase, resultado: this.vida5.lutas[this.vida5.lutas.length - 1].resultado });
    return { rival, mapa: torneio ? null : mapa as IdCena, semente, arena: !npc && !torneio, torneio, pet, rivalStats: serie[0].rivalStats, forma, serie, venceu, lesao,
      ...(tiro ? { tiro } : {}), ...(esquiva ? { esquiva } : {}), ...(apoio ? { apoio } : {}), ...(arenaPorEstagio ? { arenaPorEstagio } : {}) };
  }
  /* ---------------------------------------------------------------- itens do Tamer (pets v6; motor/itens.ts) */
  /** chips que este pet pode ter equipados, pelas medalhas que ele conhece (0 nos v1-v5) */
  get vagasChip(): number { return vagasDeChip(this.medalhas); }
  /** por que o chip nao pode entrar agora (null: pode). O motor nao sabe se o Tamer tem o chip: o app confere antes */
  porqueNaoEquipa(id: string): string | null {
    const c = chipDe(id);
    if (this.morte) return "o pet morreu";
    if (c.tipo === "chip_regra") return `${c.nome} é um chip de regra da luta de antes: a luta em tempo real não tem regras de combate`;
    if (this.chips.includes(id)) return `${c.nome} já está equipado`;
    if (!chipServe(c, this.estagioAtual)) return `${c.nome} pede um Rookie ou mais`;
    if (this.chips.length >= this.vagasChip)
      return this.vagasChip ? `as ${this.vagasChip} vaga${this.vagasChip === 1 ? "" : "s"} de chip estão ocupadas: desequipe um antes` : "sem vaga de chip: a primeira vem com a primeira medalha";
    return null;
  }
  equipar(id: string): void { this._conferirMorte(); this._vivo(); this._validarItem("equipar", id); this.log.push([this.e.tick, "i", { op: "equipar", id }]); this._item("equipar", id); }
  desequipar(id: string): void { this._conferirMorte(); this._vivo(); this._validarItem("desequipar", id); this.log.push([this.e.tick, "i", { op: "desequipar", id }]); this._item("desequipar", id); }
  private _validarItem(op: OpItem, id: string): void {
    if (op === "equipar") { const erro = this.porqueNaoEquipa(id); if (erro) throw new Error(erro); }
    else if (op === "desequipar") { if (!this.chips.includes(id)) throw new Error(`${chipDe(id).nome} não está equipado`); }
    else throw new Error("operação de item desconhecida: " + JSON.stringify(op));
  }
  private _item(op: OpItem, id: string): void {
    this._validarItem(op, id);
    const c = chipDe(id);
    if (op === "equipar") this.chips.push(id);
    else this.chips.splice(this.chips.indexOf(id), 1);
    this.comItens = true;
    this._hist({ t: this.e.tick, quem: "item", a: `${op === "equipar" ? "equipou" : "desequipou"} ${c.nome}` });
  }
  /** o treino com que o pet luta: o dele mais o dos chips de stat, dentro dos tetos (itens.bonusChipsStat); sem chip, o de sempre. Nos
      pets v9 os chips so somam com o treino minimo (itens.itensValem) e cada ponto vale CIT_V9.fatorChipStat */
  pontosDeLuta(): Stats | null {
    const treinou = this.treino.total > 0;
    if (!this.chips.length || !this.itensValem) return treinou ? this.treino.pontos : null;
    const est = this.estagioAtual, pe = est === "bebe" ? 0 : this.treino.pontosEst[est as EstagioTreino | "mega"] ?? 0;
    return pontosComChips(this.chips, est, this.treino.pontos, pe, treinou, this.versao);
  }
  /** os itens fazem efeito agora? Nos pets v9 pedem o treino minimo do nivel (itens.itensValem); nos v6-v8 sempre */
  get itensValem(): boolean { return itensValem(this.versao, this.estagioAtual, this.treino.total); }
  /** por que os itens nao fazem efeito agora (null: fazem); a frase da tela */
  porqueItensNaoValem(): string | null { return porqueItensNaoValem(this.versao, this.estagioAtual, this.treino.total); }
  /* ---------------------------------------------------------------- dono */
  observar(a: AcaoDono): void {
    if (!ACOES_DONO_JOGO_V11.includes(a)) throw new Error(`acao de dono fora dos pets v11: ${a} (sem elogio, bronca, petisco e banheiro)`);
    this._conferirMorte(); this._vivo();
    /* v12: o botao Alimentar e a reserva temporaria do MVP; poe a racao no comedouro (o lugar padrao do DonoComLugar) */
    if (a === "alimentar") { const [x, y] = this.mundo!.comedouro; this.deixarComida("racao", x, y); return; }
    this.log.push([this.e.tick, "d", a]);
    this._aplicar(a);
  }
  /** v12: o dono deixa a racao em (x, y) do mapa do mundo (subunidades inteiras). Tipo que nao e racao (MV-3), posicao fora do mapa ou
      nao inteira falham alto antes do registro. O mundo de hoje nao tem obstaculo (o contrato da P4 fica desligado no jogo) */
  deixarComida(tipo: string, x: number, y: number): void {
    this._validarComida(tipo, x, y);
    this._conferirMorte(); this._vivo();
    this.log.push([this.e.tick, "dc", { tipo: "racao", x, y }]);
    this._deixarComida(tipo, x, y);
  }
  /** o dono poe a bola parada em (x, y) do mapa do mundo (subunidades inteiras), em qualquer pet com o mundo: um evento novo, que os logs
      de antes nao tem. Posicao fora do mapa ou nao inteira falha alto antes do registro. Nao e cuidado nem contato (o deixar_bola do
      Python): so a bola muda de lugar */
  deixarBola(x: number, y: number): void {
    lerDeixarBola(eventoDeixarBola(this.e.tick, x, y, this._mapa()), this._mapa());
    this._conferirMorte(); this._vivo();
    this.log.push([this.e.tick, "db", { x, y }]);
    this._deixarBola(x, y);
  }
  private _deixarBola(x: number, y: number): void {
    lerDeixarBola(eventoDeixarBola(this.e.tick, x, y, this._mapa()), this._mapa());
    this._conferirMorte(); this._vivo();
    (this.v11!.laco as MotorCorpoMundo).bolaDoDono(x, y);
  }
  /** v19 (docs/TAREFA_V3_PEGAR_PET.md): o dono pega o pet e o solta em (x, y) do mapa do mundo (subunidades inteiras, com sinal; fora do
      mapa ele cai na borda mais proxima, PP-4). So a posicao muda (PP-1): nao e contato nem cuidado, e nada vai ao cerebro, ao corpo, ao
      vinculo ou ao historico. O pet dormindo nao e pego (PP-2), e o morto tambem nao. Antes da v19 o evento nao existe: falha alto */
  levarPet(x: number, y: number): void {
    lerLevarPet(eventoLevarPet(this.e.tick, x, y));
    this._conferirLevarPet();
    this._conferirMorte(); this._vivo();
    if (this.e.dormindo) throw new Error(`o pet está dormindo (tick ${this.e.tick}): não dá para pegá-lo (PP-2)`);
    const t = this.e.tick;
    this._levarPet(x, y);
    this.log.push([t, "lp", { x, y }]);
  }
  private _conferirLevarPet(): void {
    if (this.versao < VERSAO_V19 || this.mundo === null) throw new Error(`só os pets v${VERSAO_V19} em diante são levados pelo dono (este é v${this.versao})`);
  }
  private _levarPet(x: number, y: number): void {
    lerLevarPet(eventoLevarPet(this.e.tick, x, y));
    this._conferirLevarPet();
    this._conferirMorte(); this._vivo();
    (this.v11!.laco as MotorCorpoMundo).petDoDono(x, y);
  }
  /** o sacudir a arvore (docs/TAREFA_V3_ARVORE_SACODE.md, S2): o dono sacode a arvore `arvore` do layout; cai uma fruta se houver no
      galho e lugar no chao. So o mundo muda (AS-1): nao e contato nem cuidado, nao passa pelo cerebro, pelo corpo, pelo vinculo nem pelo
      historico, e nao atende o chamado do bebe. Vale com o pet acordado ou dormindo; o pet morto, uma versao sem o sacudir (hoje, todas:
      VERSOES_COM_SACUDIR vazia, D-AS-S2-1) e o id que nao e de arvore do layout falham alto antes do registro */
  sacudirArvore(arvore: string): void {
    lerSacudirArvore(eventoSacudirArvore(this.e.tick, arvore));
    this._conferirSacudir();
    this._conferirMorte(); this._vivo();
    const t = this.e.tick;
    this._sacudirArvore(arvore);
    this.log.push([t, "sa", { arvore }]);
  }
  private _conferirSacudir(): void {
    if (!VERSOES_COM_SACUDIR.includes(this.versao) || this.mundo === null || this.mundo.sacudidas === null)
      throw new Error(`nenhum pet sacode árvore ainda: o sacudir não está em nenhuma versão de pet (este é v${this.versao})`);
  }
  private _sacudirArvore(arvore: string): void {
    lerSacudirArvore(eventoSacudirArvore(this.e.tick, arvore));
    this._conferirSacudir();
    this._conferirMorte(); this._vivo();
    (this.v11!.laco as MotorCorpoMundo).sacudirDoDono(arvore);
  }
  /** o pet pode passar para a ilha grande agora (IG4): e v21, v22 ou v23, esta vivo e o mundo dele ainda e o de 64 x 30 (sem agua, ou
      com ela: o v21 que ja tinha passado para a agua, o v22 e o v23) */
  get podeMudarIlha(): boolean {
    return (this.versao === VERSAO_V21 || nasceNaAgua(this.versao)) && this.mundo !== null && this.mundo.cm.layout.nome !== ILHA_DOS_VIVOS && this.morte === null;
  }
  /** o alcance da memoria de lugar do DigiBrain modular deste pet, em subunidades (IG6): o de sempre (1 024), ou o da ilha grande
      (2 048) na v25 desde o ovo e nos v21 a v24 depois do evento "ma". Vale para o modular que existe e para o que for criado depois */
  alcanceMemoria: number = INATOS_MODULAR.d_max;
  /** o pet pode ganhar a memoria de 128 celulas agora: e v21 a v24, esta vivo, esta na ilha grande e ainda tem o alcance de sempre */
  get podeAlongarMemoria(): boolean {
    return (this.versao === VERSAO_V21 || nasceNaAgua(this.versao) || (nasceNaGrande(this.versao) && !nasceComMemoriaLonga(this.versao)))
      && this.naIlhaGrande && this.alcanceMemoria !== D_MAX_ILHA_GRANDE && this.morte === null;
  }
  /** IG6 (docs/TAREFA_V3_ILHA_AGUA.md, secao 12.16; "Todos, por evento", Matheus, 2026-11-11): a memoria de lugar do pet passa a alcancar
      128 celulas. So o alcance muda: o que ele lembra, o corpo, o mundo e o vinculo ficam como estao. Nao e contato nem cuidado. Vale com
      o cerebro A decidindo (o alcance fica para o modular), com o pet acordado ou dormindo, uma vez; fora da ilha grande, na v25, no pet
      de teste ou no morto, falha alto */
  alongarMemoria(): void {
    if (!this.podeAlongarMemoria) throw new Error(`só o pet v21 a v24 vivo, na ilha grande e com a memória de sempre ganha a memória longa (este é v${this.versao})`);
    const t = this.e.tick;
    this._alongarMemoria(D_MAX_ILHA_GRANDE);
    this.log.push([t, "ma", { alcance: D_MAX_ILHA_GRANDE }]);
  }
  private _alongarMemoria(alcance: unknown): void {
    if (alcance !== D_MAX_ILHA_GRANDE) throw new Error(`o alcance da memória do registro é ${D_MAX_ILHA_GRANDE}, não ${String(alcance)}`);
    if (!this.podeAlongarMemoria) throw new Error(`só o pet v21 a v24 vivo, na ilha grande e com a memória de sempre ganha a memória longa (este é v${this.versao})`);
    this._conferirMorte(); this._vivo();
    this.alcanceMemoria = D_MAX_ILHA_GRANDE;
    this.modular?.alcanceDaMemoria(D_MAX_ILHA_GRANDE);
  }
  /* ---------------------------------------------------------------- a TV no cerebro (a v32; GOSTO_VISUAL, D-GV-CEREBRO) */
  /** o pet tem a TV no cerebro (a v32): o que a TV passa entra pelo evento "st" */
  get temTv(): boolean { return nasceComTv(this.versao); }
  /** o modo livre gravado (D-GV-CEREBRO-1): o que a TV do jogo passa a partir de agora, o valor do evento `sentido_tela` (`fonte|n1|...|n7`, o
      que o ResumoTela devolve). So a TV muda: nao e contato nem cuidado, nao passa pelo vinculo nem pelo historico; vale com o pet acordado ou
      dormindo. Fora da v32, com o pet morto ou com o valor mal formado, falha alto antes do registro */
  sentidoTela(valor: string): void {
    this._validarSentidoTela(valor);
    this._conferirMorte(); this._vivo();
    const t = this.e.tick;
    this._sentidoTela(valor);
    this.log.push([t, "st", valor]);
  }
  private _validarSentidoTela(valor: unknown): [string, number[] | null] {
    if (!nasceComTv(this.versao)) throw new Error(`só o pet v32 tem a TV no cérebro (este é v${this.versao})`);
    const [fonte, niveis] = lerSentidoTela(valor);
    /* a TV desligada (a decisao A, D-GV-TVJOGO-1): so nos pets da TV no jogo (a v35 e a v36); a v32 a recusa */
    if (niveis === null && !nasceComTvJogo(this.versao)) throw new Error(`a TV desligada só no pet v35 (este é v${this.versao})`);
    if ((niveis === null ? valorSentidoTelaDesligada(fonte) : valorSentidoTela(fonte, niveis)) !== valor)
      throw new Error(`sentido_tela fora da forma canônica: ${JSON.stringify(valor)}`);
    return [fonte, niveis];
  }
  private _sentidoTela(valor: unknown): void {
    const [fonte, niveis] = this._validarSentidoTela(valor);
    this._conferirMorte(); this._vivo();
    (this.v11!.laco as MotorCorpoMundo).telaDoDono(fonte, niveis);
  }
  /** o ultimo `sentido_tela` do registro (o valor), ou null: a TV do cerebro ainda nao recebeu nada. So le */
  get ultimoSentidoTela(): string | null {
    const tv = this.v11 && this.v11.laco instanceof MotorCorpoMundo ? this.v11.laco.tv : null;
    const u = tv === null ? undefined : tv.sentidos[tv.sentidos.length - 1];
    return u === undefined ? null : u.niveis === null ? valorSentidoTelaDesligada(u.fonte) : valorSentidoTela(u.fonte, u.niveis);
  }
  /** a TV no cerebro agora, para as telas (so le): se o pet olha a TV (o OCIOSO do olhar, acordado e com ela no raio), se ela esta no raio da
      visao, e o `olhar` do ultimo motivo do modular (o agrado, o termo gosto e a TV escolhida); null fora da v32 */
  /** o gosto visual do cerebro, para o "Gosta mais de" do painel da TV (a decisao C, D-GV-TVJOGO-5; so le): por canal, o otimo de nascenca
      e o deslocamento de tanto ver, em [0, 1] (o genoma da visao do DigiBrain e a exposicao dele, na escala S). Com o A decidindo e o modular
      ainda nao criado, o genoma da semente do ovo (o mesmo que o modular tera) e nenhum deslocamento. null fora dos pets com a TV no cerebro */
  gostoVisualDoCerebro(): { nascenca: Record<string, number>; deVer: Record<string, number> } | null {
    if (!nasceComTv(this.versao)) return null;
    const b = this.modular;
    if (b !== null && b.co !== null) {
      const S = b.S;
      return { nascenca: Object.fromEntries(Object.entries(b.sens.otimo).map(([c, v]) => [c, v / S])),
               deVer: Object.fromEntries(Object.entries(b.sens.desloc).map(([c, v]) => [c, v / S])) };
    }
    const g = genomaVisao(this.semente, CONFIG_OLHAR_JOGO);
    return { nascenca: Object.fromEntries(Object.entries(g.otimo).map(([c, v]) => [c, v / CONFIG_OLHAR_JOGO.escala])),
             deVer: Object.fromEntries(Object.keys(g.otimo).map(c => [c, 0])) };
  }
  tvNoCerebro(): { olhando: boolean; noRaio: boolean; ligada: boolean; motivo: Record<string, unknown> | null } | null {
    if (!nasceComTv(this.versao)) return null;
    const laco = this.v11!.laco as MotorCorpoMundo, tv = laco.tv!, p = laco.mundo.pet, mo = this.lab?.ultimoMotivo ?? null;
    /* `ligada`: a TV passa algo (null antes do primeiro "st" e, na v35 e na v36, depois da TV desligada; D-GV-TVJOGO-1) */
    return { olhando: laco.olhandoTV(), noRaio: Math.hypot(tv.x - p[0], tv.y - p[1]) <= laco.mundo.raioDaVisao, ligada: tv.em(laco.mundo.tm(this.e.tick)) !== null,
             motivo: mo === null ? null : (mo["olhar"] as Record<string, unknown> | undefined) ?? null };
  }
  /** o pet vive na ilha grande (a v24 desde o ovo; a v21, a v22 e a v23 depois do "mi" para ela) */
  get naIlhaGrande(): boolean { return this.mundo !== null && this.mundo.cm.layout.nome === ILHA_DOS_VIVOS; }
  /** o mapa do mundo do pet, em subunidades: o limite das posicoes da racao e da bola (o de 64 x 30 sem o mundo) */
  private _mapa(): readonly [number, number] { return this.mundo === null ? MAPA_PADRAO : tamanhoDoMapa(this.mundo.cm); }
  /** a ilha do pet tem agua (a v22 desde o ovo; a v21 depois do "mi") */
  get naIlhaComAgua(): boolean { return this.mundo !== null && this.mundo.secas !== null; }
  /** IG4 (docs/TAREFA_V3_ILHA_AGUA.md, secao 12; "Migram por evento", Matheus, 2026-11-10, e a IG-7, 2026-11-11): o pet v21 ou v22
      passa para a ilha grande. So o mundo muda: o lar de la vira o lar de ca, e a comida, a bola e o pet vao deslocados junto com ele; o
      que cai em agua, arvore ou marco vai para a terra mais perto. Nao e contato nem cuidado, e nada vai ao cerebro, ao corpo, ao
      vinculo ou ao historico. Vale com o pet acordado ou dormindo, uma vez; com o pet morto, de teste ou ja na ilha grande, falha alto */
  mudarIlha(): void {
    if (!this.podeMudarIlha) throw new Error(`só o pet v${VERSAO_V21}, v22 ou v23 vivo, fora da ilha grande, passa para ela (este é v${this.versao})`);
    const t = this.e.tick;
    this._mudarIlha(ILHA_DOS_VIVOS);
    this.log.push([t, "mi", { ilha: ILHA_DOS_VIVOS }]);
  }
  /* o "mi" do registro: para a ilha grande (os v21, os v22 e os v23, desde a IG4) ou para a ilha com agua de 64 x 30 (so os v21, nos
     registros gravados entre a IA4 e a IG4) */
  private _mudarIlha(ilha: string): void {
    lerMudarIlha(eventoMudarIlha(this.e.tick, ilha));
    if (this.mundo === null || !(this.versao === VERSAO_V21 || (nasceNaAgua(this.versao) && ilha === ILHA_DOS_VIVOS)))
      throw new Error(`só os pets v${VERSAO_V21}, v22 e v23 passam de ilha pelo registro (este é v${this.versao}, para ${ilha})`);
    if (ilha !== ILHA_DOS_V21 && ilha !== ILHA_DOS_VIVOS) throw new Error(`os pets passam para a ilha ${ILHA_DOS_V21} ou ${ILHA_DOS_VIVOS}, não para ${ilha}`);
    this._conferirMorte(); this._vivo();
    (this.v11!.laco as MotorCorpoMundo).ilhaDoDono(ilha);
    /* na ida para a ilha grande, os lugares que o DigiBrain modular lembra andam com o mundo (IG-7; o gancho mundo_deslocado do Python).
       Vale mesmo com o cerebro A decidindo agora: a memoria do modular fica coerente se o dono trocar de cerebro depois */
    const mu = this.mundo, ida = mu.trocaMaior;
    if (ilha === ILHA_DOS_VIVOS && ida !== null && this.modular !== null) {
      const [dx, dy] = ida.deslocamento;
      ida.lugares_lembrados = this.modular.mem.deslocar(dx, dy, (x, y) => mu.emTerra(...noMapa(x, y, mu.cm)), x => regiaoDe(x, mu.cm));
    }
  }
  private _validarComida(tipo: unknown, x: unknown, y: unknown): void {
    if (tipo !== "racao") throw new Error(`só a ração vai ao chão nos pets v12 (MV-3): ${String(tipo)}`);
    lerDeixarComida(eventoDeixarComida(this.e.tick, tipo, x, y, this._mapa()), this._mapa());
  }
  /** v12: a racao no mundo e o contato do alimentar de hoje (MotorMundo._aplicar_deixar_comida): no laco, o mundo e o cerebro; aqui, o
      chamado do bebe, a memoria por espacos, o vinculo e o historico, como o alimentar dos v11 */
  private _deixarComida(tipo: string, x: number, y: number): void {
    this._validarComida(tipo, x, y);
    this._conferirMorte(); this._vivo();
    const t = this.e.tick, laco = this.v11!.laco as MotorCorpoMundo;
    this._cuidadoNaHora("alimentar");
    laco.comidaDoDono(tipo, x, y);
    this.e = laco.estado;
    if (this.estagioAtual === "bebe") this._atender("alimentar");
    this.pol.receberAcaoDono("alimentar", t);
    this.nDono++;
    this.vinc.acaoDono("alimentar", t, this.acao, this.nDono);
    this._hist({ t, quem: "dono", a: "alimentar" });
  }
  /** v11: a acao do dono pelo laco do corpo (o cuidado pelo estado de sempre e pelo corpo, o carinho e o tapa so pelo corpo; o cerebro
      recebe o que o laco manda), sem obediencia e sem janela. A memoria por espacos e o vinculo recebem a acao como nos v10. O tratar
      so cura a lesao: nao e contato e nao passa pelo corpo (decisao do Matheus de 2026-10-18) */
  private _aplicar(a: AcaoDono): void {
    if (!(ACOES_DONO_JOGO_V11 as readonly string[]).includes(a)) throw new Error(`acao de dono fora dos pets v11: ${a}`);
    const t = this.e.tick;
    this._conferirMorte(); this._vivo();
    if (a === "tratar_lesao") {
      if (this.lesionadoDesde !== null) { this.lesionadoDesde = null; this.lutas.tratadas++; }
      this.nDono++;
      this._hist({ t, quem: "dono", a });
      return;
    }
    this._cuidadoNaHora(a);
    this.v11!.laco.acaoDono(a);
    this.e = this.v11!.laco.estado;
    if (this.estagioAtual === "bebe") this._atender(a);
    this.pol.receberAcaoDono(a, t);
    this.nDono++;
    this.vinc.acaoDono(a, t, this.acao, this.nDono);
    this._hist({ t, quem: "dono", a });
  }
  private _conferirMorte(): void {
    if (this.morte) return;
    if (this.lesionadoDesde !== null && this.e.tick - this.lesionadoDesde >= CLE.horasMorte * 60)
      this.morte = { tick: this.e.tick, causa: "lesao_sem_tratar" };
  }
  private _vivo(): void {
    if (this.morte) throw new PetMorto(this.morte.causa === "lesoes" ? "ele se machucou demais nas lutas" : "a lesão ficou sem tratamento");
  }
  /** taxa de vitoria do estagio (v4): a passagem para adulto pede >= limiarTaxa em >= CAT.sparring lutas */
  taxaVitoria(): number | null { return this.lutas.lutas ? this.lutas.vitorias / this.lutas.lutas : null; }

  /** desejo depois de cada decisao: registra so quando muda; alimenta o vinculo e as metricas (cumprimento:
      vontade com alvo X cumprida se o pet escolhe X em ate kCumprimento ticks) */
  private _desejo(obs: Observacao, a: AcaoPet, t: number, desejo?: Desejo | null): void {
    const d = desejo !== undefined ? desejo : this.desejoAtual(obs, t), u = this.dz.atual, ch = (x: { tipo: string; alvo: string } | null) => x ? x.tipo + ":" + x.alvo : "";
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
    if (this.noGrupo) {
      /* CO4c: o tempo do pet do grupo e o do grupo; o relogio do jogo (src/tempo.ts) anda os dois pets por aqui */
      if (this.avancarDoGrupo === null) throw new Error("o pet do grupo anda pelo GrupoDoJogo, um tick por vez na vez sorteada (CO4b)");
      this.avancarDoGrupo(n);
      return;
    }
    this._registrarAvanco(n);
    this._avancar(n);
  }
  /** o avanco do grupo do pet (o GrupoDoJogo o liga na montagem; CO4c) */
  private avancarDoGrupo: ((n: number) => void) | null = null;
  /** a CO7 (docs/ESPEC_V3_COOPERACAO_CO7.md): a ConfigCooperacao com a `co7` que o modular deste pet do grupo recebe ao nascer (o GrupoDoJogo a
      liga na montagem, antes do cerebro do ovo); null desligada, como no jogo de hoje */
  private deveres: Readonly<ConfigCooperacao> | null = null;
  ligarDeveres(cfg: Readonly<ConfigCooperacao>): void {
    if (!this.noGrupo || this.deveres !== null || this.modular !== null || !cfg.co7) throw new Error("ligarDeveres so uma vez, no pet do grupo, antes do cerebro e com a co7");
    this.deveres = cfg;
  }
  ligarAvancoDoGrupo(f: (n: number) => void): void {
    if (!this.noGrupo || this.avancarDoGrupo !== null) throw new Error("ligarAvancoDoGrupo so uma vez, no pet do grupo");
    this.avancarDoGrupo = f;
  }
  private _registrarAvanco(n: number): void {
    if (!(n > 0)) throw new Error("avanco precisa ser positivo");
    const u = this.log[this.log.length - 1];
    if (u && u[1] === "t" && u[0] + u[2] === this.e.tick) u[2] += n; else this.log.push([this.e.tick, "t", n]);
  }
  /* ---- dois pets (CO4b): o avanco em tres partes, como o _abrir_avanco, o _um_tick e o _fechar_avanco do Python. O GrupoDoJogo as chama */
  /** o avanco do grupo chega ao registro do pet (o mesmo "t" de hoje) */
  abrirAvancoNoGrupo(n: number): void {
    if (!this.noGrupo) throw new Error("abrirAvancoNoGrupo so no pet do grupo");
    this._registrarAvanco(n);
  }
  /** o pet decide no proximo tick (o Grupo sorteia a vez entre os que decidem) */
  decideNoProximoTick(): boolean { return this.v11!.laco.decideNoProximoPasso(); }
  /** um tick do pet: o do laco e o que vem depois (os chamados, a evolucao, o treino e a pausa), o mesmo do _avancar */
  umTickNoGrupo(): void {
    if (!this.noGrupo) throw new Error("umTickNoGrupo so no pet do grupo");
    this._umTick();
  }
  /** o fim do avanco do grupo (a conferencia da morte, como no fim do _avancar) */
  fecharAvancoNoGrupo(): void {
    if (!this.noGrupo) throw new Error("fecharAvancoNoGrupo so no pet do grupo");
    this._conferirMorte();
  }
  /** v11: o laco do corpo anda um tick por vez (a decisao, se for a hora, chama o cerebro e o _decisaoV11); o que vem depois do tick e o
      dos v10 (os chamados do bebe, a evolucao, o treino e a pausa), sem mexer no estado do pet */
  private _avancar(n: number): void {
    if (this.noGrupo) throw new Error("o pet do grupo anda pelo GrupoDoJogo, um tick por vez na vez sorteada (CO4b)");
    for (let i = 0; i < n; i++) this._umTick();
    this._conferirMorte();
  }
  private _umTick(): void {
    const laco = this.v11!.laco;
    laco.passo();
    this.e = laco.estado;
    if (this.estagioAtual === "bebe") this._chamados();
    this._evoluir();
    const e = this.e;
    this.treino.avancar(e.tick, e.dormindo, Math.min(e.fome, e.higiene, e.energia) >= CTR.bemCuidado, this.estagioAtual);
    this._pausaTreino();
  }
  /** v11: o que o Motor registra de uma decisao do cerebro (chamado pelo laco, logo depois do agir). Como nos v10, sem o motivo do
      Bandit (o motivo do cerebro A fica no cerebro: o painel DigiBrain e a etapa 5), sem o efeito (o do laco) e sem travessuras */
  private _decisaoV11(obs: ObservacaoLobos, a: AcaoPet, t: number, d: Desejo | null): void {
    this.acao = a;
    const v = this.vida5;
    if (a !== v.anterior && a !== "ocioso") v.episodios.push([t, a]);
    v.anterior = a;
    this.prox = t + C.intervalo;
    this.pol.observar(obs, a, t);
    this._desejo(obs, a, t, d);
    this._conferirMorte();
    /* o ir ate a TV (v35 e v36; D-GV-TVJOGO-3) conta como o explorar nos tracos (e andar); as outras, como sao */
    const at = a === "ir_tv" ? "explorar" : a;
    for (const k of ACOES_PET) this.tracos[k] = (1 - CT.alfa) * this.tracos[k] + (k === at ? CT.alfa : 0);
    this.nDecisoes++;
    const ult = this.historico[this.historico.length - 1];
    if (!ult || ult.quem !== "pet" || ult.a !== a) this._hist({ t, quem: "pet", a });
  }
  /** pedido de pausa: fadiga >= 40. Acabar sem treino = pausa atendida (vinculo sobe); treinar por cima derruba */
  private _pausaTreino(): void {
    if (this.treino.pedePausa && !this.pausaTreino) this.pausaTreino = { treinou: false };
    else if (!this.treino.pedePausa && this.pausaTreino) {
      if (!this.pausaTreino.treinou) { this.pausas.atendidas++; this.vinc._amostra(1, CTR.pesoPausa, null); this.feitosCuidado.push({ tick: this.e.tick, tipo: "pausa" }); }
      this.pausaTreino = null;
    }
  }

  /* ---------------------------------------------------------------- treino */
  treinar(ex: Exercicio): ResultadoSessao {
    if (!CTR.exercicios[ex]) throw new Error("exercício desconhecido: " + ex);
    this._conferirMorte(); this._vivo();
    if (this.estagioAtual === "bebe") throw new Error("o bebê ainda não treina");
    if (!this.treino.podeTocar(this.e.tick)) throw new Error(`descansa um pouco: próximo treino em ${CTR.intervalo - (this.e.tick - this.treino.ultimo!)} min`);
    this.log.push([this.e.tick, "tr", ex]);
    return this._treinar(ex);
  }
  private _treinar(ex: Exercicio): ResultadoSessao {
    const t = this.e.tick;
    /* sem a obediencia dos v2-v10: o pet nunca enrola */
    const s = this.treino.sessao(t, ex, true);
    this.vida5.sessoes.push([t, ex]);
    const base = { origem: "vida" as const, tick: t, refsOrd: [], exploracao: false, humor: this.e.humor, valorDecidiu: true };
    let mot: MotivoVida | null = null;
    if (s.forcada) {
      this.vinc.ajustar(CTR.vincForcar, null);
      mot = { ...base, acao: "forcar_treino", fatores: ["fadiga_treino"], intensidade: Math.min(1, s.fadigaAntes / 100) };
    }
    if (this.pausaTreino) {
      if (!this.pausaTreino.treinou) this.pausas.ignoradas++;
      this.pausaTreino.treinou = true;
      this.vinc._amostra(0, CTR.pesoPausa, null);
      mot = mot || { ...base, acao: "treinar_cansado", fatores: ["fadiga_treino"], intensidade: Math.min(1, s.fadigaAntes / 100) };
    }
    if (mot) { this.motivo = mot; this.motivos.push(mot); if (this.motivos.length > 200) this.motivos.shift(); }
    this._hist({ t, quem: "treino", a: `${s.forcada ? "forçou" : "treinou"} ${NOME_EXERCICIO[ex].toLowerCase()}` });
    return s;
  }
  /** desejo com o pedido de pausa do treino na frente (espelho de MotorTreino._desejo_atual) */
  desejoAtual(obs: Observacao, t: number): Desejo | null {
    if (this.treino.pedePausa) return { tick: t, tipo: "necessidade", alvo: "descansar", causa: "fadiga_treino", intensidade: Math.min(1, this.treino.fadiga / 100) };
    /* a vontade do cerebro A (PW-3), na observacao com o corpo (observacaoAgora) */
    return desejoLobos(obs, this.v11!.braco.cerebro, t);
  }

  /* ---------------------------------------------------------------- chamados do bebe e evolucao */
  /** janelas de chamado do bebe (cronograma_interacoes.json): o bebe chama em horario fixo (fome a cada 30
      min, higiene a cada 60, carinho a cada 45); conta como atendido se o dono fizer a acao certa dentro da
      janela de 15 min. Chamado novo do mesmo tipo com um aberto: o aberto conta como perdido. */
  private _chamados(): void {
    const tk = this.e.tick, t = tk - TICK_INICIAL, ab = this.chamados.abertos;
    const corpo = this.produto.chamadosPeloCorpo, pelaFome = this.produto.chamadoPelaFome && !corpo;
    for (const tipo of Object.keys(ab) as Chamado[]) if (tk - ab[tipo]! > CAT.janelaChamado) { this.chamados.total++; delete ab[tipo]; }
    if (corpo) {
      /* a chave chamadosPeloCorpo: os tres pelo corpo, com os limiares do bebe (o da fome no lugar do CHAMADO_FOME_CORPO) */
      const e = this.e, valor: Record<Chamado, number> = { fome: e.fome, higiene: e.higiene, carinho: e.humor };
      for (const tipo of Object.keys(CHAMADO_BEBE) as Chamado[]) this._chamadoCorpo(tipo, valor[tipo], CHAMADO_BEBE_CORPO[tipo], tk, t);
      return;
    }
    for (const [tipo, iv] of Object.entries(CHAMADO_BEBE) as [Chamado, number][]) if (t > 0 && t < this.dur.bebe && t % iv === 0) {
      if (pelaFome && tipo === "fome") continue;
      if (tipo in ab) this.chamados.total++;
      ab[tipo] = tk;
    }
    if (pelaFome) this._chamadoCorpo("fome", this.e.fome, CHAMADO_FOME_CORPO.limiar, tk, t);
  }
  /** um chamado pelo corpo (as chaves chamadoPelaFome e chamadosPeloCorpo): abre quando o valor do corpo fica abaixo do limiar, no maximo
      um a cada CHAMADO_BEBE[tipo] ticks. Fecha como atendido com a acao do dono (o _atender, como hoje); o de fome, tambem quando a fome
      volta ao limiar (no pet com o mundo, ela so sobe comendo a racao que o dono deixou). Fecha como perdido quando a janela passa (como
      hoje). A higiene nao sobe sozinha; o humor sobe, e o chamado de carinho fica aberto ate o dono atender ou a janela passar */
  private _chamadoCorpo(tipo: Chamado, valor: number, lim: number, tk: number, t: number): void {
    const ab = this.chamados.abertos, ultimo = this.ultimoChamado[tipo];
    if (tipo in ab) {
      if (tipo === "fome" && valor >= lim) { this.chamados.atendidos++; this.chamados.total++; delete ab[tipo]; this.feitosCuidado.push({ tick: tk, tipo: "chamado" }); }
      return;
    }
    if (t > 0 && t < this.dur.bebe && valor < lim && (ultimo === undefined || tk - ultimo >= CHAMADO_BEBE[tipo])) {
      ab[tipo] = tk;
      this.ultimoChamado[tipo] = tk;
    }
  }
  private _atender(a: AcaoDono): void {
    const ab = this.chamados.abertos;
    for (const tipo of Object.keys(ab) as Chamado[]) if (ACAO_CHAMADO[tipo].includes(a)) {
      this.chamados.atendidos++; this.chamados.total++; delete ab[tipo]; this.feitosCuidado.push({ tick: this.e.tick, tipo: "chamado" }); return;
    }
  }
  /** o cuidado na hora certa (Bits, docs/PLANO_V3_MOEDA.md, secao 2): do Rookie em diante nao ha chamado, entao conta a acao do dono que
      atende o corpo que precisava, lido ANTES da acao (comida com a fome abaixo do limiar, banho com a higiene, carinho ou brincar com o
      humor). So o feito: nada muda no pet */
  private _cuidadoNaHora(a: AcaoDono): void {
    if (this.estagioAtual === "bebe") return;
    const tipo = (Object.keys(ACAO_CHAMADO) as Chamado[]).find(c => ACAO_CHAMADO[c].includes(a));
    if (!tipo) return;
    const e = this.e, valor: Record<Chamado, number> = { fome: e.fome, higiene: e.higiene, carinho: e.humor };
    if (valor[tipo] < CUIDADO_NA_HORA[tipo]) this.feitosCuidado.push({ tick: e.tick, tipo: "cuidado" });
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
    } else if (est === "adulto") {
      if (this.podeMega()) this._virarMega();
      return;
    } else if (est === "adolescente" && this.e.tick >= lim! && this.sparring >= CAT.sparring
               && this.lutas.vitorias / this.lutas.lutas >= CLE.limiarTaxa && this.medalhasBastam("adulto")) {
      const carater = this.caraterAgora("adulto");
      /* sobrecarga >= 60: a forma adulta vira a sombria da linha (permanente: vinculo com teto, instavel na luta) */
      this.sombria = this.treino.sobrecarga >= CSO.sombrio;
      const adulta = this.sombria ? CSO.formas[this.forma.linha!].nome : formaAdultaDe(this.forma.linha!, carater);
      if (this.sombria) this.vinc.limitar(CSO.tetoVinc);
      nova = { estagio: "adulto", adulta, carater, sparring: this.sparring, sobrecarga: this.treino.sobrecarga };
    }
    if (!nova) return;
    const { estagio: e2, ramo, linha, adulta } = nova;
    this.forma = { ...this.forma, est: e2, ...(ramo ? { ramo } : {}), ...(linha ? { linha } : {}), ...(adulta ? { adulta } : {}) };
    this.estagioAtual = e2;
    this.evolucoes.push({ tick: this.e.tick, ...nova, forma: { ...this.forma } });
    this.chamados = { abertos: {}, atendidos: 0, total: 0 }; this.sparring = 0;   /* contadores zeram */
    this.lutas = lutasZeradas();
    /* sem regras de combate (LP2, decisao 6; LP4): a luta da POC decide pelos dois lados */
  }
  /* ---------------------------------------------------------------- Mega (pets v5; docs/DESIGN_EVOLUCAO_CANONICA.md) */
  /** tick em que virou Ultimate (null antes) */
  tickUltimate(): number | null { const ev = this.evolucoes.find(x => x.estagio === "adulto"); return ev ? ev.tick : null; }
  /** o que falta para o Mega, pelas condicoes do desenho (secao 3): tempo no Ultimate, lutas, vitoria e vinculo; pets v6:
      e as medalhas do Tamer (tem X, precisa Y; null nos v5) */
  requisitosMega(): { tempo: boolean; lutas: boolean; taxa: boolean; vinculo: boolean; falta: number; medalhas: RequisitoMedalhas | null } | null {
    const t0 = this.tickUltimate();
    /* a sombria nunca vira Mega (o vinculo dela tem teto 0,6, acima do limiar de hoje: a regra fica explicita) */
    if (t0 === null || this.estagioAtual !== "adulto" || this.sombria) return null;
    const falta = Math.max(0, t0 + this.dur.adulto - this.e.tick), L = this.lutas;
    return { tempo: falta === 0, lutas: L.lutas >= CAT.sparring, taxa: L.lutas > 0 && L.vitorias / L.lutas >= CLE.limiarTaxa,
      vinculo: this.vinc.valor >= CMG.vinculo, falta, medalhas: this.requisitoMedalhas("mega") };
  }
  podeMega(): boolean { const r = this.requisitosMega(); return !!r && r.tempo && r.lutas && r.taxa && r.vinculo && (!r.medalhas || r.medalhas.ok); }

  /* ---------------------------------------------------------------- medalhas do Tamer (pets v6; docs/DESIGN_MEDALHAS_ARENAS.md) */
  /** medalhas que a evolucao para `alvo` pede e quantas o Tamer tem (null: pet sem trava, v1-v5) */
  requisitoMedalhas(alvo: Estagio): RequisitoMedalhas | null {
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
      const lutas = this.sparring >= CAT.sparring, taxa = this.lutas.lutas > 0 && this.lutas.vitorias / this.lutas.lutas >= CLE.limiarTaxa;
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
  /* ---------------------------------------------------------------- o cerebro trocavel (v17) */
  /** v17: algum "cb" ja entrou no registro */
  private cerebroEscolhido = false;
  /** o cerebro que decide agora: "modular" ou "a" (os pets de antes da v17 tem um so: o A, ou o modular no pet de teste) */
  get cerebroAtual(): "modular" | "a" { return this.modularAtivo ? "modular" : "a"; }
  /** v17: o dono troca o cerebro do pet (os Ajustes): o escolhido decide dali em diante, o outro fica parado com o que aprendeu. Entre
      decisoes, com o pet vivo; o mesmo cerebro de agora e erro (o registro so guarda trocas de verdade, menos o do ovo, no comeco) */
  trocarCerebro(cerebro: "modular" | "a"): void {
    this._conferirMorte(); this._vivo();
    const v = { cerebro };
    this._validarCerebro(v);
    this.log.push([this.e.tick, "cb", v]);
    this._trocarCerebro(v);
  }
  private _validarCerebro(v: unknown): asserts v is { cerebro: "modular" | "a" } {
    if (!ehCerebroTrocavel(this.versao)) throw new Error(`só os pets v${VERSAO_V17} (e a v18, a v17 com o empurrão) trocam de cérebro (este é v${this.versao})`);
    if (!v || typeof v !== "object" || Object.keys(v).join() !== "cerebro" || !(CEREBROS as readonly unknown[]).includes((v as { cerebro: unknown }).cerebro))
      throw new Error(`troca de cérebro inválida: ${JSON.stringify(v)}`);
    const c = (v as { cerebro: string }).cerebro, noOvo = !this.cerebroEscolhido && !this.nDecisoes && this.e.tick === TICK_INICIAL;
    if (!noOvo && c === this.cerebroAtual) throw new Error(`o pet já decide com o cérebro ${c}`);
  }
  private _trocarCerebro(v: unknown): void {
    this._validarCerebro(v);
    this._conferirMorte(); this._vivo();
    /* o modular nasce com o alcance da memoria deste pet (o de sempre, ou o da ilha grande: a v25 e o evento "ma"; IG6) e, na v27, com o sono
       que segura (SONO_SEGURA) */
    if (v.cerebro === "modular") {
      /* a v32: o modular com a subchave `olhar`, o genoma da visao da semente do ovo (rng propria `visao-ovo`) e o agrado no corpo */
      const tv = nasceComTv(this.versao);
      this.modular ??= new DigiBrain(tv ? CONFIG_DIGIBRAIN_LAB_OLHAR : CONFIG_DIGIBRAIN_LAB, { ...INATOS_MODULAR, d_max: this.alcanceMemoria } as typeof INATOS_MODULAR, false,
        nasceComSonoSegura(this.versao) ? CONFIG_SONO_SEGURA_LIGADA : CONFIG_SONO_SEGURA,
        tv ? { semente: this.semente, cfgOlhar: CONFIG_OLHAR_JOGO,
               ...(nasceComTvJogo(this.versao) ? { irAteTv: true, cfgEnjooTela: CONFIG_ENJOO_TELA_LIGADA } : {}) } : undefined,   // a v35 e a v36: o ir ate a TV e o enjoo (D-GV-TVJOGO)
        nasceComLance(this.versao) ? CONFIG_LANCE_DONO_LIGADA : CONFIG_LANCE_DONO,    // e, na v30, na v31, na v35 e na v36, com o lance do dono (BB-4)
        this.deveres);                                    // e, so com a CO7 ligada no grupo (`ligarDeveres`; desligada no jogo, D-CO6c-1), com os deveres
      if (this.ponteLuta) this.modular.ligarLutaMemoria();
    }
    this.modularAtivo = v.cerebro === "modular";
    this.cerebroEscolhido = true;
    (this.v11!.laco as MotorCorpoMundo).digibrain = this.modularAtivo;   // o modular ve o mundo, escolhe o alvo e recebe a consequencia dele
  }
  /** o Tamer ganhou medalha: grava "o Tamer tem n medalhas a partir deste tick" e re-verifica a evolucao na hora */
  liberar(n: number): void {
    this._conferirMorte(); this._vivo();
    this._validarLiberacao(n);
    this.log.push([this.e.tick, "u", { n }]);
    this._liberar(n);
  }
  private _validarLiberacao(n: number): void {
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
  }
  /** carater medido agora: pelo cerebro A (carater.caraterV11) */
  caraterAgora(quando: QuandoCarater): Carater { return caraterV11(this.v11!.braco.cerebro, quando); }
  /** caráter travado na ultima evolucao que o mediu (adolescente/adulto); antes disso, neutro */
  carater(): Carater | null { const ev = [...this.evolucoes].reverse().find(x => x.carater); return ev ? ev.carater! : null; }
  private _hist(x: ItemHistorico): void { this.historico.push(x); if (this.historico.length > 300) this.historico.shift(); }

  /* ---------------------------------------------------------------- assinatura e replay */
  assinatura(): string {
    return JSON.stringify([this.e, this.acao, this.tracos, this.pol.assinatura(), this.evolucoes, this.forma, this.chamados, this.sparring, null, this.campanha,
      [this.vinc.assinatura(), this.obed, this.dz], this.treino.assinatura(), this.pausas, this.falaFria, this.sombria,
      [this.edu, this.lutas, this.lesionadoDesde, this.morte, this.origem, this.especie, this.temp, this.vitoriasVida, this.ritmo],
      /* os gambits (o null acima) e as cartas (o null e o [] abaixo) sairam com o combate por turnos (LP4): o lugar deles fica, e a assinatura
         dos v21 nao muda */
      this.medalhas, ...(this.comItens ? [[this.chips, null, []]] : []),
      ...(this.liga.tentativas ? [["liga", this.liga]] : []),
      ...(this.fronteira ? [["fronteira", this.instalacoes]] : []), ...(this.salao.tentativas ? [["salao", this.salao]] : []),
      [this.men, this.honestidadeEspecie], this.conf.assinatura(),
      ...(this.versao === VERSAO_PET_LAB ? [["lab", { ...this.modular!.estadoInterno(), motivos: undefined }]] : []),
      /* a v17 depois do primeiro "cb": o cerebro que decide e o modular (a v17 sem "cb" assina como a v15) */
      ...(this.cerebroEscolhido ? [["cb", this.modularAtivo ? "modular" : "a", this.modular ? { ...this.modular.estadoInterno(), motivos: undefined } : null]] : []),
      /* a memoria longa pelo evento "ma" (IG6): so com o evento (a assinatura dos pets sem ele nao muda; a v25 ja nasce com ela) */
      ...(this.alcanceMemoria !== INATOS_MODULAR.d_max && !nasceComMemoriaLonga(this.versao) ? [["ma", this.alcanceMemoria]] : []),
      ...(this.ponteLuta ? [this.epsLuta ? ["pl", "eps"] : ["pl", true]] : []),   /* a ponte da luta: so com a marca (a assinatura dos pets sem ela nao muda) */
      ...(this.falaUnidades ? [["fu", true]] : []),   /* DC3d: a fala com conteudo, so com a marca (a assinatura dos pets sem ela nao muda) */
      ["v11", this.v11!.braco.cerebro.estadoInterno(), this.v11!.laco.estadoDict(), this.v11!.laco.proximaDecisao],
      ["mundo", this.mundo!.resumo(), [...(this.v11!.laco as MotorCorpoMundo).vistosEm]]]);
  }
  /** v8 (M1): a frase de estado da confianca agora */
  estadoConfianca(): ReturnType<ConfiancaCombate["estado"]> | null { return this.conf.estado(this.e.tick); }
  /** um evento do registro, sem regravar no registro (replay) */
  aplicarEvento(ev: EventoRegistro): void {
    const t = ev[0];
    if (this.e.tick !== t) throw new Error(`registro fora de ordem no tick ${t}`);
    switch (ev[1]) {
      case "t": this._avancar(ev[2]); break;
      case "d": this._aplicar(ev[2]); break;
      case "l": this._lutarPoc(ev[2].r, ev[2].s, ev[2].m); break;
      case "g": throw new Error(`evento "g" (regras de combate) no registro (tick ${t}): o combate por turnos saiu (LUTA_POC, LP4)`);
      case "tr": this._treinar(ev[2]); break;
      case "o": this._origem(ev[2]); break;
      case "c": this._config(ev[2].dur); break;
      case "p": this._produto(ev[2]); break;
      case "cb": this._trocarCerebro(ev[2]); break;
      case "pl": this._ponteLuta(ev[2]); break;
      case "fu": this._falaUnidades(ev[2]); break;
      case "u": this._liberar(ev[2].n); break;
      case "i": this._item(ev[2].op, ev[2].id); break;
      case "k": throw new Error(`evento "k" (carta) no registro (tick ${t}): as cartas sairam com o combate por turnos (LUTA_POC, LP4)`);
      case "dc": {
        const c = ev[2] as unknown;
        if (!c || typeof c !== "object" || Object.keys(c).sort().join() !== "tipo,x,y")
          throw new Error(`evento de comida inválido no registro (tick ${t}): ${JSON.stringify(c)}`);
        const { tipo, x, y } = c as Record<string, unknown>;
        this._validarComida(tipo, x, y);
        this._deixarComida(tipo as string, x as number, y as number); break;
      }
      case "db": {
        const b = ev[2] as unknown;
        if (!b || typeof b !== "object" || Object.keys(b).sort().join() !== "x,y")
          throw new Error(`evento de bola inválido no registro (tick ${t}): ${JSON.stringify(b)}`);
        const { x, y } = b as Record<string, unknown>;
        lerDeixarBola(eventoDeixarBola(t, x, y, this._mapa()), this._mapa());
        this._deixarBola(x as number, y as number); break;
      }
      case "lp": {
        const l = ev[2] as unknown;
        if (!l || typeof l !== "object" || Object.keys(l).sort().join() !== "x,y")
          throw new Error(`evento de levar o pet inválido no registro (tick ${t}): ${JSON.stringify(l)}`);
        const { x, y } = l as Record<string, unknown>;
        lerLevarPet(eventoLevarPet(t, x, y));
        this._levarPet(x as number, y as number); break;
      }
      case "sa": {
        const a = ev[2] as unknown;
        if (!a || typeof a !== "object" || Object.keys(a).join() !== "arvore")
          throw new Error(`evento de sacudir a árvore inválido no registro (tick ${t}): ${JSON.stringify(a)}`);
        const arvore = lerSacudirArvore({ tipo: "sacudir_arvore", valor: (a as Record<string, unknown>).arvore });
        this._sacudirArvore(arvore); break;
      }
      case "st": this._sentidoTela(ev[2]); break;
      case "ma": {
        const a = ev[2] as unknown;
        if (!a || typeof a !== "object" || Object.keys(a).join() !== "alcance")
          throw new Error(`evento do alcance da memória inválido no registro (tick ${t}): ${JSON.stringify(a)}`);
        this._alongarMemoria((a as Record<string, unknown>).alcance); break;
      }
      case "mi": {
        const i = ev[2] as unknown;
        if (!i || typeof i !== "object" || Object.keys(i).join() !== "ilha")
          throw new Error(`evento de troca de ilha inválido no registro (tick ${t}): ${JSON.stringify(i)}`);
        this._mudarIlha(lerMudarIlha({ tipo: "mudar_ilha", valor: (i as Record<string, unknown>).ilha })); break;
      }
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
