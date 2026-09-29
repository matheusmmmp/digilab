/* Parametros do motor web: espelho de digilab/config.py (e das configs de experimento que o web adota).
   O teste de constantes (test/constantes.test.mjs, tabela test/mapa_constantes.json) confere cada
   numero contra o Python; mudar um valor aqui sem mudar la faz o teste falhar. */
import type {
  AcaoDono, AcaoPet, Carater, Chamado, EixoCarater, EixoTemperamento, Especie, Estagio, EstagioTreino, Exercicio,
  FormaAdultaNormal, FormaSombria, Linha, Ramo, Stat, Stats, Temperamento, TracoCombate,
} from "./tipos.ts";

export type Tecnica = "investida" | "contra_golpe" | "marcar" | "pele_dura";

export const TPD = 1440;
export const C = {
  decFome: 1 / 1200, decHig: 1 / 1500, decEn: 1 / 900, decHum: 1 / 1200,
  enSono: 1 / 240, humBrinc: 1 / 120,
  ganhoAlim: .45, ganhoLimpar: .60, ganhoBrincHum: .25, custoBrincEn: .08, custoBrincFome: .05,
  ganhoElogiar: .10, custoRepr: .12,
  probSuj: 1 / 400, probSujRef: .35, sujMax: 5, penHigSuj: .12,
  danoSaude: 1 / 2000, curaSaude: 1 / 3000,
  iniNoite: 22 * 60, fimNoite: 7 * 60, multNoite: 1.8,
  intervalo: 15, janelaAtencao: 240,
};
export const CB = { lambda: 1, var: .25, piso: .05, elogio: 1, repr: -1, janela: 120, ignorado: -.5, escalaTdc: 480 };
/* temperamento inato (espelho de ConfigTemperamento): 0 e neutro e da os mesmos numeros de CB.
   Web: rancor so escala o decaimento das broncas (a demora aqui nao decai); sorteio pela semente
   com o rng da web (nao e o mesmo numero do Python) */
export const CTP = { amplitude: 1, kCuriosidade: Math.LN2, kTeimosia: .5, kSensibilidade: .5, kRancor: Math.LN2 };
export const EIXOS_TEMP: readonly EixoTemperamento[] = ["curiosidade", "teimosia", "sensibilidade", "rancor"];
/* desejo (espelho de ConfigDesejo) e limiar do tom do temperamento (ConfigExpressao) */
export const CDJ = { limiarNecessidade: .3, limiarVontade: .1, limiarTom: .2, kCumprimento: 60 };
/* versao do pet salvo: 1 = memoria curta antiga, sem vinculo nem obediencia; 2 = memoria por espacos +
   vinculo + obediencia + condicao no combate; 3 = v2 + carater pelo desvio da politica; 4 = v3 + educacao,
   lesoes e qualificacao por vitorias (docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, espelho de digilab/educacao.py);
   5 = v4 + evolucao canonica: o Ultimate vira Mega (docs/DESIGN_EVOLUCAO_CANONICA.md; so no jogo, sem par no Python) */
export const VERSAO_PET = 5;
/* evolucao canonica (pets v5, so no jogo; docs/DESIGN_EVOLUCAO_CANONICA.md, tudo PROPOSTO). O Mega e o estagio
   adulto com forma.mega: a forma (e a passiva) nao muda, o pet fica mais forte. Ultimate -> Mega pede o tempo do
   Ultimate, a qualificacao da passagem para adulto (CAT.sparring lutas no estagio, CLE.limiarTaxa de vitoria) e
   vinculo >= `vinculo`; a sombria tem vinculo com teto CSO.tetoVinc (0,6), entao nunca chega ao Mega.
   multEstagio: vida e guts (x CAT.estagio.adulto); vida: E na escala da campanha (CESC.vida.adulto = 1500);
   tetoEstagio/tetoVida: treino (CTR.tetoEstagio.adulto = 14, CTR.tetoVida = 36); dur*: tempo no Ultimate (min). */
export const CMG = { multEstagio: 1.15, vida: 3000, tetoEstagio: 16, tetoVida: 40, durRapida: 1440, durClassica: 2880, vinculo: .7 };
/* educacao (espelho de ConfigEducacao): travessuras com janela da crianca em diante, disciplina 0-100 */
export const CED = {
  janela: 15, intervalos: { crianca: { fome: 90, higiene: 120, carinho: 90 }, adolescente: { fome: 150, higiene: 120, carinho: 120 },
    adulto: { fome: 180, higiene: 120, carinho: 180 } } as Record<EstagioTreino, Record<Chamado, number>>,
  limiarReal: .35, fracaoFalsoBase: .25, reforcoPetisco: .05, tetoFalso: .5, disciplinaMax: 100, passo: 25, acertos: 3,
  fatorEvoluir: .5, fracaoPetisco: .5, disciplinaBanheiro: 0, vincBroncaSemMotivo: -.05, custoHumorAcordar: .12,
  limiarSuper: .9, custoSaudeSuper: .05, deltaEps: .10,
};
/* lesoes e qualificacao por vitorias (espelho de ConfigLesoes): so lutas fora da arena de pesquisa */
/* expPorVitoria/expMax: estilo "lutar" (experiencia de combate, decisao do Matheus em 2026-09-29) */
export const CLE = { probLesao: .2, lesoesMorte: 20, horasMorte: 6, limiarTaxa: .8, expPorVitoria: .002, expMax: .05 };
/* heranca (espelho de ConfigHeranca): temperamento = media dos pais + N(0, sigma); especie sorteada entre as dos pais */
export const CHE = { sigma: .1 };
/* memoria por espacos (espelho de ConfigMemoriaEspacos) */
export type CategoriaMemoria = "demora" | "bronca" | "elogio" | "carinho";
export const CME = {
  nCurto: 4, nLongo: 2, dCurto: 12 * 60, relembrar: 4 * 60, tau: 360, limiarPedido: .5, janela: 240,
  intensidade: { demora: null, bronca: 1, elogio: 1, carinho: .5 } as Record<CategoriaMemoria, number | null>,
};
export const FATORES_ESPACOS: readonly CategoriaMemoria[] = ["demora", "bronca", "elogio", "carinho"];
/* emocao filtrada pelo temperamento (adendo DF 2.1, espelho de emocao.py) */
export const CEM = { limiarEixo: .2 };
/* vinculo e obediencia (espelho de ConfigVinculo e ConfigObediencia) */
export const CVI = { inicial: .5, alfa: .1, pesoAtend: 1, pesoCoer: 1, pesoDesejo: .5, janelaLat: 240, janelaCoer: 1440, janelaDesejo: 60 };
export const COB = {
  b0: 1, bVinculo: 2, bTeimosia: 1, bConflito: 2, limiarConflito: .3, probFazerOutra: .5,
  sujeitas: ["alimentar", "limpar", "brincar", "acariciar"] as readonly AcaoDono[], limiarMotivo: .05,
};
/* treino (espelho de ConfigTreino, docs/pve_treino.json; sobrecarga por forcada calibrada 15 -> 25) e
   formas sombrias (espelho de ConfigSombrio). Sem rng: so a obediencia (pets v2) sorteia se o pet enrola. */
export const CTR = {
  pesoPontoCombate: 3,   /* cada ponto treinado vale 3 em stat de combate (ConfigTreino.peso_ponto_combate) */
  exercicios: {
    levantar_pedra: ["forca", "vigor"], corrida: ["folego", "recuperacao"], alvo: ["mira", "folego"],
    esquiva: ["guarda", "vigor"], meditar: ["recuperacao", "guarda"], resistencia: ["vigor", "forca"],
  } as Record<Exercicio, readonly [Stat, Stat]>,
  ganhoPri: 2, ganhoSec: 1, tetoStat: 10, tetoEstagio: { crianca: 10, adolescente: 12, adulto: 14 } as Record<EstagioTreino, number>, tetoVida: 36,
  fadigaSessao: 20, recuperaHora: 10, limiarPausa: 40, limiteForcar: 60, intervalo: 10,
  multForcar: 1.5, sobreForcar: 25, estresseForcar: 10, vincForcar: -.05, sobreMax: 100,
  decaiHora: 2, decaiSono: 10, sonoCompleto: 360, bemCuidado: .3, pesoPausa: 1,
};
export const APTIDAO: Record<Especie, Stats> = {
  brasa: { forca: 1.2, guarda: 1.1, folego: 1.0, vigor: .9, mira: .9, recuperacao: .9 },
  cirro: { mira: 1.2, recuperacao: 1.1, folego: 1.0, guarda: .9, forca: .9, vigor: .9 },
  ferrugem: { guarda: 1.2, vigor: 1.1, forca: 1.0, folego: .9, recuperacao: .9, mira: .9 },
  limo: { recuperacao: 1.2, folego: 1.1, vigor: 1.0, guarda: .9, mira: .9, forca: .9 },
};
export interface FormaSombriaDef { nome: FormaSombria; base: FormaAdultaNormal; stats: Partial<Stats> }
export const CSO = {
  aviso: 30, sombrio: 60, epsMin: .2, tetoVinc: .6, multDev: 1.3, fracBastiao: 1, multPred: 1.4, turnosPeleColosso: 3, multRegenColosso: .85,
  formas: {
    brigao: { nome: "devastador", base: "furioso", stats: { forca: 4, folego: 1, recuperacao: -3, guarda: -2 } },
    guardiao: { nome: "bastiao_rachado", base: "espelho", stats: { guarda: 4, vigor: 1, recuperacao: -3, mira: -2 } },
    cacador: { nome: "predador", base: "emboscador", stats: { mira: 4, forca: 1, vigor: -3, guarda: -2 } },
    colosso: { nome: "colosso_partido", base: "tita", stats: { vigor: 4, guarda: 1, folego: -3, recuperacao: -2 } },
  } as Record<Linha, FormaSombriaDef>,
};
export const SOMBRIA = Object.fromEntries(Object.entries(CSO.formas).map(([l, x]) => [x.nome, { ...x, linha: l as Linha }])) as
  Partial<Record<string, FormaSombriaDef & { linha: Linha }>>;
/* condicao do cuidado no combate (ConfigCatalogo.condicao_mult_*): saude 0 -> 0,95; 1 -> 1,05 */
export const CCOND = { min: .95, max: 1.05 };
export const CD = { passo: 15, maxPasso: 6, limAlim: .5, limLimpar: .5, sujLimpar: 2, limHumBrinc: .4, limSono: .4, limPedido: .35, visitasRelapso: 3, probElogioInc: .5, porDia: 16 };
export const CT = { alfa: 1 / 288 };
export const CA = {
  hp: 100, dano: 10, ganhoAf: .5, maxTurnos: 40, fome: .7, hig: .7, saude: 1, hora: .5,
  mapa: { ocioso: "bloqueio", dormir: "bloqueio", comer: "agarrao", brincar: "golpe", chamar_atencao: "carga", explorar: "finta", emburrar: "agarrao" } as Record<AcaoPet, TracoCombate>,
};
export const TICK_INICIAL = 8 * 60;
export const TEMP_NEUTRO: Temperamento = Object.freeze({ curiosidade: 0, teimosia: 0, sensibilidade: 0, rancor: 0 });

export const ACOES_PET: readonly AcaoPet[] = ["ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar"];
export const ACOES_DONO: readonly AcaoDono[] = ["alimentar", "limpar", "brincar", "acariciar", "elogiar", "repreender"];
export const ACOES_EDUCACAO: readonly AcaoDono[] = ["petisco", "levar_ao_banheiro", "tratar_lesao"];
export const ACOES_DONO_V4: readonly AcaoDono[] = [...ACOES_DONO, ...ACOES_EDUCACAO];
export const COMBATE: readonly TracoCombate[] = ["golpe", "bloqueio", "agarrao", "finta", "carga"];

/* memoria curta dos pets v1 (espelho de digilab/memoria.py, ConfigMemoria) */
export const CM = { limiarPedido: .5, janela: 240, tau: 360, escala: 3 };
export const FATORES_MEMORIA = ["latencia_fome", "latencia_higiene", "repreensoes", "elogios"] as const;
/* motivo (espelho de ConfigExpressao.limiar_motivo) */
export const CE = { limiar: .05 };
export const NF = 11 + 4;   /* 11 do bandit v1 + 4 de memoria */

/* combate V2.1 (ConfigCombateV2C, ConfigCombateV21C) */
export const CV = {
  tMax: 40,
  custo: { golpe_rapido: 10, preparar_pesado: 15, disparo: 20, esquivar: 20 } as Record<string, number>,
  dano: { golpe_rapido: 8, disparo: 6, pesado: 25 },
  multDef: .3, multDefPesado: .6, multCarregar: 1.5, gutsDef: 5, gutsCarregar: 25,
  eps: .05, maxRegras: 8, maxCond: 2, fracoes: [.25, .5, .75], guts: [20, 40, 60], ks: [2, 3], janelaFreq: 5, limiarFreq: .4,
  pesoGutsOr: .002, pesoPendOr: .5,
  /* base corrigida (V2C, TAREFA_CORRECAO_COMBATE): parry contra golpe rapido e morte subita */
  parry: 5, turnoMS: 25, multMS: 1.5,
};
/* V21C: vida por vigor 3 -> 2,5 (base 70 -> 75; vida neutra continua 100) contra a dominancia da Ferrugem */
export const CV21 = {
  hpBase: 75, hpVigor: 2.5, g0Base: 30, g0Folego: 2, gMaxBase: 80, gMaxFolego: 2, regenBase: 4, regenRec: .4,
  multBase: .7, multPonto: .03, guardaBase: 1.3, guardaPonto: .03,
  custo: { investida: 20, contra_golpe: 15, marcar: 10, pele_dura: 20 } as Record<string, number>,
  danoInvestida: 8, parry: 0, fracCG: .5, turnosMarca: 3, multMarca: 2, turnosPele: 2, multPele: .5,
  duelista: 4, limFurioso: .5, multFurioso: 1.25, espelho: 1, muralha: 3, recargaSent: 4, multEmb: 2, multTita: 1.3,
  maxRegras: { bebe: 0, crianca: 3, adolescente: 5, adulto: 8 } as Record<Estagio, number>, turnos: [5, 10, 20],
};

/* catalogo (docs/catalogo_pets.json, docs/arvore_evolucao.json): 4 especies ativas */
export const STATS: readonly Stat[] = ["vigor", "folego", "recuperacao", "forca", "mira", "guarda"];
export const ESPECIES: readonly Especie[] = ["brasa", "cirro", "ferrugem", "limo"];
export const LINHAS: readonly Linha[] = ["brigao", "guardiao", "cacador", "colosso"];
export interface AdultoDaLinha { comp: EixoCarater; formas: Partial<Record<FormaAdultaNormal, { sinal: number; stats: Partial<Stats> }>> }
export const CAT = {
  min: 3, max: 20, limiarCuidado: .8, sparring: 10, janelaChamado: 15, escalaCarater: .1,
  especies: {
    brasa: { vigor: 9, folego: 10, recuperacao: 7, forca: 14, mira: 8, guarda: 12 },
    cirro: { vigor: 7, folego: 11, recuperacao: 11, forca: 7, mira: 15, guarda: 9 },
    ferrugem: { vigor: 13, folego: 8, recuperacao: 8, forca: 9, mira: 7, guarda: 15 },
    limo: { vigor: 11, folego: 12, recuperacao: 15, forca: 6, mira: 7, guarda: 9 },
  } as Record<Especie, Stats>,
  conceito: {
    brasa: "lagarto de brasas; pressão de perto", cirro: "ave de nuvem; luta de longe",
    ferrugem: "tatu de placas metálicas; aguenta pancada", limo: "lesma de musgo; guerra de desgaste",
  } as Record<Especie, string>,
  carater: {
    impetuoso: { forca: 3, folego: 1, guarda: -3, recuperacao: -1 }, paciente: { guarda: 3, recuperacao: 1, forca: -3, folego: -1 },
    atento: { mira: 3, recuperacao: 1, vigor: -3, forca: -1 }, resistente: { vigor: 3, guarda: 1, mira: -3, folego: -1 },
  } as Record<EixoCarater, Partial<Stats>>,
  crianca: { sereno: { recuperacao: 2, guarda: 1, forca: -2, mira: -1 }, arisco: { forca: 2, mira: 1, recuperacao: -2, guarda: -1 } } as Record<Ramo, Partial<Stats>>,
  adolescente: {
    brigao: { eixo: "impetuoso", tecnica: "investida", stats: { forca: 3, folego: 1, guarda: -2, mira: -2 } },
    guardiao: { eixo: "paciente", tecnica: "contra_golpe", stats: { guarda: 3, recuperacao: 1, forca: -2, folego: -2 } },
    cacador: { eixo: "atento", tecnica: "marcar", stats: { mira: 3, folego: 1, vigor: -2, guarda: -2 } },
    colosso: { eixo: "resistente", tecnica: "pele_dura", stats: { vigor: 3, guarda: 1, mira: -2, recuperacao: -2 } },
  } as Record<Linha, { eixo: EixoCarater; tecnica: Tecnica; stats: Partial<Stats> }>,
  adulto: {
    brigao: { comp: "paciente", formas: { duelista: { sinal: 1, stats: { mira: 1, guarda: 1, vigor: -1, folego: -1 } }, furioso: { sinal: -1, stats: { forca: 2, guarda: -2 } } } },
    guardiao: { comp: "impetuoso", formas: { espelho: { sinal: 1, stats: { forca: 1, mira: 1, vigor: -1, recuperacao: -1 } }, muralha: { sinal: -1, stats: { vigor: 2, forca: -2 } } } },
    cacador: { comp: "resistente", formas: { sentinela: { sinal: 1, stats: { vigor: 1, guarda: 1, mira: -1, forca: -1 } }, emboscador: { sinal: -1, stats: { mira: 2, vigor: -2 } } } },
    colosso: { comp: "atento", formas: { vigia: { sinal: 1, stats: { mira: 1, recuperacao: 1, forca: -1, folego: -1 } }, tita: { sinal: -1, stats: { forca: 2, recuperacao: -2 } } } },
  } as Record<Linha, AdultoDaLinha>,
  estagio: { bebe: .4, crianca: .6, adolescente: .8, adulto: 1 } as Record<Estagio, number>,
};
/* escala de stats (ConfigEscala, TAREFA_PLANILHA_PROGRESSAO Parte C): E = vida do estagio x (1 + beta x pontos);
   no combate da CAMPANHA o dano que A causa em B vale x E_A/E_B e a vida perde o multiplicador de estagio. NPC:
   perfil neutro, E = vida do estagio sugerido x fator, epsilon proprio. A arena contra bots nao usa a escala. */
export const CESC = {
  vida: { bebe: 50, crianca: 200, adolescente: 600, adulto: 1500 } as Record<Estagio, number>,
  beta: .03,
  fatorNpc: { npc_tier1_brutamontes: 1.1, npc_tier2_sentinela: 1.6, npc_tier2_carcereiro: 1.5, npc_tier2_porteiro: 1.1,
    npc_tier3_soberano: 1.2 } as Record<string, number>,
  epsNpc: .2,
  vidaNeutra: 100,       /* hpBase + 10 x hpVigor: vida exibida = E x vida propria / vida neutra */
};
/* duracao de cada estagio em minutos e chamados do bebe (docs/cronograma_interacoes.json);
   acoes do dono que atendem cada chamado */
export const DUR_EVO = { bebe: 180, crianca: 720, adolescente: 1080 };
/* ritmo classico (ConfigDuracoes.canonica, v-pets: 6 h, 24 h, 36 h): bebe, crianca, adolescente em minutos */
export const DUR_CLASSICA = [360, 1440, 2160];
export const CHAMADO_BEBE: Record<Chamado, number> = { fome: 30, higiene: 60, carinho: 45 };
export const ACAO_CHAMADO: Record<Chamado, readonly AcaoDono[]> = { fome: ["alimentar"], higiene: ["limpar"], carinho: ["acariciar", "brincar"] };
export const FORMAS_AD: readonly FormaAdultaNormal[] = ["duelista", "furioso", "espelho", "muralha", "sentinela", "emboscador", "vigia", "tita"];
export const LINHA_DA_FORMA = Object.fromEntries(LINHAS.flatMap(l => Object.keys(CAT.adulto[l].formas).map(f => [f, l]))) as Record<FormaAdultaNormal, Linha>;
/* caráter PROVISORIO (so na web): cada eixo junta os tracos de combate que se parecem com ele */
export const EIXO_TRACO: Record<EixoCarater, readonly TracoCombate[]> = { impetuoso: ["golpe", "carga"], paciente: ["bloqueio"], atento: ["finta"], resistente: ["agarrao"] };
export const TECNICAS: readonly Tecnica[] = ["investida", "contra_golpe", "marcar", "pele_dura"];

/* gambits hibridos (so na web) */
export const GA = { base: .05, alfa: .2, bonusResultado: .1, limiarTroca: -.02 };

/* Linha de base do caráter pelos tracos (PROVISORIO, so na web, pets v1/v2): afinidades medias de um pet
   comum no momento de cada transicao (ver o comentario completo no HTML de origem) */
export const BASE_CARATER: Record<"adolescente" | "adulto", Record<TracoCombate, number>> = {
  adolescente: { golpe: -0.0551, bloqueio: 0.1059, agarrao: 0.0364, finta: -0.0552, carga: -0.0314 },
  adulto: { golpe: -0.0466, bloqueio: 0.1246, agarrao: -0.0067, finta: -0.0680, carga: -0.0311 },
};
/* carater pelo desvio da politica (pets v3; espelho de evolucao.carater, ConfigEvolucaoPesquisa).
   web: 32 sondas x 100 amostras (o Python usa 64 x 200): ~4x mais rapido, mais ruido */
export const CCP = { nEstados: 32, amostras: 100, semente: 9001, escala: .05 };
/* deslocamento por eixo (so na web, jogabilidade): linhas ~25% cada no adolescente e ~50/50 entre as duas
   formas adultas, com os donos simulados (195 pets v3, 2026-09-25) */
export const DESLOC_CARATER: Record<"adolescente" | "adulto", Carater> = {
  adolescente: { atento: -0.0264, impetuoso: -0.0088, paciente: 0.0990, resistente: 0.0536 },
  adulto: { atento: -0.0500, impetuoso: 0.0625, paciente: 0.1875, resistente: -0.0875 },
};
