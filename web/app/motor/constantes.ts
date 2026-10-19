/* Parametros do motor web: espelho de digilab/config.py (e das configs de experimento que o web adota).
   O teste de constantes (test/constantes.test.mjs, tabela test/mapa_constantes.json) confere cada
   numero contra o Python; mudar um valor aqui sem mudar la faz o teste falhar. */
import type {
  AcaoDono, AcaoPet, Carater, Chamado, EixoCarater, EixoTemperamento, Especie, Estagio, EstagioBase, EstagioTreino, Exercicio,
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
   5 = v4 + evolucao canonica: o Ultimate vira Mega, um estagio proprio (docs/DESIGN_EVOLUCAO_CANONICA.md; so no jogo);
   6 = v5 + trava da evolucao pelas medalhas do Tamer (evento "u" no registro; docs/DESIGN_MEDALHAS_ARENAS.md; so no jogo);
   7 = v6 + voz propria: fala espontanea com janela e mentira (evento "fl"; docs/DESIGN_VOZ_PROPRIA.md, secao 9);
   8 = v7 + confianca de combate e desgaste por rival repetido (MVP M1; nenhum evento novo, estado derivado das lutas "l";
   docs/DESIGN_MVP_M1_CONFIANCA.md, espelho de digilab/confianca.py);
   9 = v8 + combate equilibrado: as lutas usam a variante V21E (CV21E; rodada de equilibrio geral, fase 1, docs/EQUILIBRIO_GERAL.md);
   nenhum evento novo;
   10 = v9 + vinculo B, previsibilidade + desejo (CVB; docs/V2_VINCULO_PROPOSTA.md, alternativa B, decisao do Matheus de
   2026-10-01; plano docs/PLANO_ANALISE_V2_VINCULO.md; espelho de ConfigVinculoSituacao ligada): o pedido nao abre e a coerencia
   do feedback agrupa por (acao do pet, situacao do pet); nenhum evento novo;
   11 = o cerebro A e o corpo (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 4): o pet decide e aprende pelos lobos (motor/lobos.ts, a
   consequencia no corpo), sobre o laco do corpo por tick (motor/motor_corpo.ts); o dono tem carinho e tapa, sem elogio nem bronca; o
   desejo e a vontade do cerebro A; o carater pelo metodo do Python, com a escala e o deslocamento do v11. Saem a educacao (as janelas, o
   petisco e o banheiro), a mentira e a obediencia; a lesao fica, e o tratar so cura (decisao do Matheus de 2026-10-18) */
export const VERSAO_PET = 11;
/* medalhas do Tamer que cada evolucao pede nos pets v6 (decisao do Matheus, 2026-09-29: 1, 3 e 5; so no jogo), pela
   chave do estagio de destino: Rookie -> Champion (adolescente), Champion -> Ultimate (adulto), Ultimate -> Mega (mega).
   In-Training -> Rookie nao pede medalha. A tabela das medalhas fica em medalhas.ts */
export const CMD = { adolescente: 1, adulto: 3, mega: 5 };
/* evolucao canonica (pets v5, so no jogo; docs/DESIGN_EVOLUCAO_CANONICA.md, tudo PROPOSTO). O Mega e um estagio proprio
   depois do adulto (Ultimate): a forma (e a passiva) vem do Ultimate, o pet fica mais forte. Ultimate -> Mega pede o tempo do
   Ultimate, a qualificacao da passagem para adulto (CAT.sparring lutas no estagio, CLE.limiarTaxa de vitoria) e
   vinculo >= `vinculo`; a sombria nunca chega ao Mega (regra explicita em Motor.requisitosMega). `vinculo` baixou de 0,7
   para 0,4 (Matheus, 2026-09-29): com 0,7 nenhum dono simulado coerente chegava (artifacts_campanha/mega/limiar_vinculo.json).
   multEstagio: vida e guts (x CAT.estagio.adulto); vida: E na escala da campanha (CESC.vida.adulto = 1500);
   tetoEstagio/tetoVida: treino (CTR.tetoEstagio.adulto = 14, CTR.tetoVida = 36); dur*: tempo no Ultimate (min). */
export const CMG = { multEstagio: 1.15, vida: 3000, tetoEstagio: 16, tetoVida: 40, durRapida: 1440, durClassica: 2880, vinculo: .4 };
/** o estagio das tabelas de sempre: o Mega usa as do adulto (gambits, fala, janelas da educacao) */
export const baseDe = (est: Estagio): EstagioBase => est === "mega" ? "adulto" : est;
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
/* mentira (pets v7; espelho de ConfigMentira, DESIGN_VOZ_PROPRIA secao 9). No jogo a fala vem do evento "fl" (gatilho);
   os slots da pesquisa (intervalo_fala_min, defasagem_fala_min) nao existem aqui.
   h = (fatorSombria se sombria) x (1 - pesoSobrecarga x sobrecarga/100) x especie; p = 0 com h = 1 ou `acertos` broncas
   certas seguidas em mentiras; senao min(tetoChance, coefChance (1-h)(1-disciplina/max) + reforcoImpune x impunes) */
export const CMEN = { fatorSombria: .4, pesoSobrecarga: .5, coefChance: .5, reforcoImpune: .05, tetoChance: .8, acertos: 3,
  impunesPremiada: 2, janela: 30, fracaoTemaEstado: .5, honestidadeEnganador: .7 };
/* heranca (espelho de ConfigHeranca): temperamento = media dos pais + N(0, sigma); especie sorteada entre as dos pais */
export const CHE = { sigma: .1 };
/* confianca de combate e desgaste por rival repetido (MVP M1, espelho de ConfigConfianca; pets v8; tudo PROPOSTO,
   sem fonte). lambda/tauHab: novidade por rival; eta/kSens/tauConf: a confianca; kappaEps: so o epsilon do lutador
   sobe com a inseguranca; limiarFrase/histerese/limiarTedio/nTedio: as frases de estado (motor/confianca.ts) */
export const CCF = { lambda: .7, tauHab: 2880, eta: .25, kSens: .5, tauConf: 1440, kappaEps: .10, limiarFrase: .4, histerese: 120, limiarTedio: .3, nTedio: 3 };
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
/* vinculo B (pets v10; espelho de ConfigVinculoSituacao, tudo PROPOSTO): a situacao do pet = (necessidade baixa: min(fome, higiene)
   < limNec, o limiar do pedido; cansado: energia < limEnergia, a regra de exaustao do instinto; noite: eNoite), lida da observacao
   com que o pet decidiu a acao atual. versaoPet: a partir de qual versao o vinculo e o B (no Python a variante e escolhida pelo
   config, nao por versao de pet) */
export const CVB = { versaoPet: 10, limNec: .5, limEnergia: .25 };
/* o cerebro A (motor/lobos.ts; docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 2): a ConfigLobos do L0. bits: S = 2**bits, a escala dos pesos
   inteiros; escalaTdc: a entrada do tempo sem cuidado, min(1, ticks / escala); maxPesos: o teto de pesos do plano */
export const CLB = { bits: 10, escalaTdc: 480, maxPesos: 1000 };
/** o aprendiz dos pets v11 (motor/lobos.ts, W-PORTE etapa 3): o ponto das vidas do gabarito (test/gabaritos/lobos_python.json,
 *  config_v11), PROPOSTO e nao validado no jogo. O T3 (passo S/2, teto 16 S, piso S/16), o tapa com o valor da bronca, a consequencia
 *  com o ganho 4 nos drives do N3 (fome, higiene e energia, os indices em Estado.vetor), os canais ligados (a montagem `completa`) e o
 *  w_novos 2 nos drives novos (w_d inteiros, pelo nome do receptor) */
export const CLB_V11 = {
  passo: 512, teto: 16384, piso: 64, recompensaTapa: -1,
  ganho: 4, drives: [0, 1, 2], canais: true,
  pesosDrivesCorpo: { fome: 1, higiene: 1, energia: 1, humor: 1, tedio: 2, curiosidade: 2, solidao: 2, estresse: 2, dor: 2, vontade: 1,
    conforto: 1 } as Readonly<Record<string, number>>,
};
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
/** as acoes do dono dos pets v11: as quatro de cuidado, o tapa (os do laco do corpo, ACOES_DONO_V11 de motor_corpo.ts) e o tratar */
export const ACOES_DONO_JOGO_V11: readonly AcaoDono[] = ["alimentar", "limpar", "brincar", "acariciar", "tapa", "tratar_lesao"];
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
  maxRegras: { bebe: 0, crianca: 3, adolescente: 5, adulto: 8 } as Record<EstagioBase, number>, turnos: [5, 10, 20],
};
/* V21D: reequilibrio dos arquetipos, variante a_c_e2v_v (docs/EQUILIBRIO_RODADA2.md, validada em docs/VALIDACAO_V21D.md;
   chaves da ConfigCombateV21D, experiments/configs/v21d/validacao.json). So nas lutas de pets v6 (versaoPet em diante):
   os v1-v5 lutam com a V21C. As outras chaves da V21D (D2, E1, E2 no tita) ficam desligadas e nao existem na web */
export const CV21D = {
  versaoPet: 6,
  preparoSobPeleOculto: true, muralhaListaEspelho: true, vigiaBateEmQuemRecua: true, vigiaRecuaDoPreparoSobPele: true,
} as const;
/* V21E: rodada de equilibrio geral, fase 1 (docs/EQUILIBRIO_GERAL.md; chaves da ConfigCombateV21E,
   experiments/configs/v21e/calibracao.json). So nas lutas de pets v9 (versaoPet em diante): as quatro chaves da V21D e as cinco
   da V21E, todas listas das formas (bots.gambitsAdulto); a base (custo do golpe rapido, parry, C3) nao muda. Os v6-v8 seguem na
   V21D e os v1-v5 na V21C */
export const CV21E = {
  versaoPet: 9,
  preparoSobPeleOculto: true, muralhaListaEspelho: true, vigiaBateEmQuemRecua: true, vigiaRecuaDoPreparoSobPele: true,
  duelistaDefendeDoGolpe: true, titaDefendeDoGolpe: true, espelhoSemCarregar: true, muralhaSemCarregar: true, muralhaContraGolpeNaPele: true,
} as const;

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
  estagio: { bebe: .4, crianca: .6, adolescente: .8, adulto: 1 } as Record<EstagioBase, number>,
};
/* escala de stats (ConfigEscala, TAREFA_PLANILHA_PROGRESSAO Parte C): E = vida do estagio x (1 + beta x pontos);
   no combate da CAMPANHA o dano que A causa em B vale x E_A/E_B e a vida perde o multiplicador de estagio. NPC:
   perfil neutro, E = vida do estagio sugerido x fator, epsilon proprio. A arena contra bots nao usa a escala. */
export const CESC = {
  vida: { bebe: 50, crianca: 200, adolescente: 600, adulto: 1500 } as Record<EstagioBase, number>,
  beta: .03,
  fatorNpc: { npc_tier1_brutamontes: 1.1, npc_tier2_sentinela: 1.6, npc_tier2_carcereiro: 1.5, npc_tier2_porteiro: 1.1,
    npc_tier3_soberano: 1.2 } as Record<string, number>,
  epsNpc: .2,
  vidaNeutra: 100,       /* hpBase + 10 x hpVigor: vida exibida = E x vida propria / vida neutra */
};
/* escala dos pets v6 (so no jogo; decisao do Matheus, 2026-09-30: "o treino tem que decidir" e "o estagio tem que pesar").
   Mesma formula da CESC (E = vida do estagio x (1 + beta x pontos); o dano da campanha vale x E_A/E_B), com a vida de cada
   estagio (o Mega inclusive) e o peso do ponto de treino proprios. Vale so nas lutas de escala dos pets v6 (campanha e arenas:
   o pet, pela versao dele, e o NPC, pelas regras da luta); CESC, os pets v1-v5 e o Python da pesquisa nao mudam. fatorNpc:
   os desafiantes da campanha v6 (os NPCs que nao sao lideres) recalibrados na escala nova; os lideres tem o fator em
   arenas.ts. Numeros PROPOSTOS, calibrados em test/calibrar_escala_v6.mjs e test/calibrar_arenas.mjs
   (artifacts_campanha/escala_v6/, artifacts_campanha/arenas/). */
export const CESC_V6 = {
  versaoPet: 6,
  vida: { bebe: 50, crianca: 200, adolescente: 700, adulto: 2500, mega: 23000 } as Record<Estagio, number>,
  beta: .045,
  /* Tortomon: nenhum fator fecha as metas (o de maior folga; a excecao da Sentinela de sempre, agora na escala v6). Com a regra
     do limite do desafiado (2026-09-30) o Tortomon e o Machinedramon sairam das metas na validacao e foram recalibrados (1,6 -> 1,5
     e 2,7 -> 2,2); Devidramon e Puppetmon seguiram nas metas e ficaram */
  fatorNpc: { npc_tier2_sentinela: 1.5, npc_tier2_porteiro: 1.1, npc_v5_puppetmon: 2.5, npc_v5_machinedramon: 2.2 } as Record<string, number>,
};
/* escala dos pets v9 (rodada de equilibrio geral, fase 2; docs/EQUILIBRIO_GERAL.md, metas M-B1 e M-B3): a mesma formula e o mesmo
   uso da CESC_V6, so nas lutas de escala dos pets v9 (o pet pela versao, o NPC pelas regras V21E da luta). A CESC_V6 (pets v6-v8) nao
   muda. vida e beta: os da CESC_V6 (com as regras V21E as metas de estagio passam sem mudar a escala: test/calibrar_escala_v6.mjs
   --conferir, artifacts_equilibrio_geral/fase2/escala_conferencia.json); os rivais da Fronteira (Liga, instalacoes, Salao) seguem na
   vida da CESC_V6, a mesma. fatorNpc: os desafiantes da campanha recalibrados nas regras V21E, pelo metodo de sempre (o fator de
   maior folga; test/calibrar_desafiantes_v6.mjs, desafiantes_calibracao.json): Devidramon 1,1 (igual), Puppetmon 2,5 -> 1,8,
   Machinedramon 2,2 -> 2,3; o Tortomon, que nao fechava com a grade de 0,1, fecha com 1,53 (grade de 0,01 entre 1,4 e 1,7,
   desafiantes_calibracao_npc_tier2_sentinela_grade.json; passa de 1,51 a 1,54). Os lideres tem o fator dos pets v9 em arenas.ts
   (FATOR_LIDER_V9). So sementes de calibracao; PROPOSTOS */
export const CESC_V9 = {
  versaoPet: 9,
  vida: { bebe: 50, crianca: 200, adolescente: 700, adulto: 2500, mega: 23000 } as Record<Estagio, number>,
  beta: .045,
  fatorNpc: { npc_tier2_sentinela: 1.53, npc_tier2_porteiro: 1.1, npc_v5_puppetmon: 1.8, npc_v5_machinedramon: 2.3 } as Record<string, number>,
};
/* itens do Tamer (medalhas, parte 3; so no jogo e so nos pets v6; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13). Numeros PROPOSTOS e SEM
   EQUILIBRIO (decisao do Matheus, 2026-09-30: o equilibrio dos itens entra na rodada de equilibrio geral do combate, depois das
   proximas mecanicas). vagas: chips equipados por pet pelas medalhas que ele conhece ([minimo de medalhas, chips], do maior para o
   menor; sem medalha, nenhum). tetoChipStat: a soma dos chips de stat vale no maximo esta fracao do treino tipico do estagio (tipico:
   o das metas da parte 2, test/calibrar_arenas.mjs). espera: minutos do relogio do pet entre duas cartas de revanche do mesmo lider.
   gutsFolego, curaAbaixo e curaFracao: as cartas de Folego e de Cura */
export const CIT = {
  versaoPet: 6,
  vagas: [[5, 3], [3, 2], [1, 1]] as readonly (readonly [number, number])[],
  tetoChipStat: .25,
  tipico: { crianca: 8, adolescente: 22, adulto: 36, mega: 40 } as Readonly<Partial<Record<Estagio, number>>>,
  espera: 1440,
  gutsFolego: 20, curaAbaixo: .3, curaFracao: .2,
};
/* itens nos pets v9 (rodada de equilibrio geral, fase 3; docs/EQUILIBRIO_GERAL.md, metas M-D1 a M-D3; itens.ts): restricoes de uso e valores
   so para os pets v9. treinoMinimo: os itens (chips e carta) so fazem efeito com o treino do pet >= esta fracao do treino tipico do nivel
   (CIT.tipico); cartaSoContraNpc: a carta so vale contra os NPCs da campanha (nao na arena contra bots); fatorChipStat: o valor do ponto
   do chip de stat. O chip de regra entra no fim da lista (itens.listaComChips, GambitsPet.listaDeLuta). Calibrados em test/medir_itens.mjs
   (sementes de calibracao). PROPOSTOS */
export const CIT_V9 = {
  versaoPet: 9,
  treinoMinimo: .5,
  cartaSoContraNpc: true,
  fatorChipStat: .5,
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
/* o carater dos pets v11 (PW-4, opcao (b), decisao do Matheus de 2026-10-18; docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 15): a escala
   propria (CCP.escala x a razao das medianas de |bruto| v11 / v10) e o deslocamento remedido para o cerebro A, nas 32 sondas com os
   receptores do corpo (carater.ts, caraterV11). PROPOSTOS: a calibracao (experiments/calibrar_carater_v11.py ->
   artifacts_v2_w_porte/carater_v11_calibracao.json, 20 pets das sementes dos testes) fecha as linhas e as formas, mas nao a escala
   (13,75% dos eixos cortados em +-1, acima do limite de 10,6%) */
export const CCP_V11 = { escala: .015 };
export const DESLOC_CARATER_V11: Record<"adolescente" | "adulto", Carater> = {
  adolescente: { atento: -0.0117, impetuoso: 0.0142, paciente: -0.0167, resistente: 0.0142 },
  adulto: { atento: -0.7917, impetuoso: 0.2604, paciente: 0.25, resistente: 0 },
};

/* V2, o mundo fisico minimo (docs/TAREFA_V2_MUNDO_FISICO.md, etapa 5): espelho de ConfigMundo e dos layouts de digilab/config.py.
   O motor do mundo e motor/mundo.ts; a paridade (test/mundo.test.ts) confere estes numeros contra o gabarito do Python. Posicoes do
   layout em celulas; regioes por faixa de x (inclusivas). Todos PROPOSTOS, sem fonte, como no Python. */
export interface LayoutMundo {
  nome: string;
  regioes: readonly (readonly [string, number, number])[];
  ninho: readonly [number, number];
  comedouro: readonly [number, number];
  bola_inicio: readonly [number, number];
  arvores: readonly (readonly [string, number, number, string])[];
}
export const LAYOUT_MUNDO_PADRAO: LayoutMundo = {
  nome: "padrao",
  regioes: [["casa", 0, 15], ["jardim", 16, 33], ["campo", 34, 47], ["mata", 48, 63]],
  ninho: [4, 15], comedouro: [10, 15], bola_inicio: [40, 15],
  arvores: [["J1", 22, 6, "a"], ["J2", 29, 20, "b"], ["J3", 19, 14, "c"],
            ["M1", 53, 4, "a"], ["M2", 60, 15, "b"], ["M3", 50, 23, "c"],
            ["M4", 62, 26, "a"], ["M5", 56, 10, "b"], ["M6", 55, 19, "c"]],
};
/** o layout do G-DIST (config.layout_afastado): cada tronco a duas vezes a distancia do centro da regiao, cortado para dentro dela */
export function layoutAfastado(base: LayoutMundo, altura = 30): LayoutMundo {
  const arvores = base.arvores.map(([id, x, y, fruta]) => {
    const r = base.regioes.find(([, x0, x1]) => x0 <= x && x <= x1);
    if (!r) throw new Error(`arvore ${id} fora de toda regiao`);
    const [, x0, x1] = r;
    const cx = Math.floor((x0 + x1 + 1) / 2), cy = Math.floor(altura / 2);
    return [id, Math.min(x1, Math.max(x0, cx + 2 * (x - cx))), Math.min(altura - 1, Math.max(0, cy + 2 * (y - cy))), fruta] as const;
  });
  return { ...base, nome: "afastado", arvores };
}
export const LAYOUT_MUNDO_AFASTADO: LayoutMundo = layoutAfastado(LAYOUT_MUNDO_PADRAO);
export interface ConfigMundo {
  ligada: boolean; layout: LayoutMundo; celulas_x: number; celulas_y: number; sub: number;
  velocidade: number; custo_energia_por_subunidade: number; raio_pegar_celulas: number;
  raio_visao_celulas: number; max_vistos: number; cheiro_racao: number; cheiro_fruta: number; raio_cheiro_celulas: number;
  limiar_cheiro_explorar: number; passo_cheiro_celulas: number; vagar_min_celulas: number; vagar_max_celulas: number;
  fome_max_comer_achado: number; nutricao_fruta: number; efeito_podre: number; ganho_humor_bola: number;
  passo_mundo_ticks: number; p_queda_jardim: number; p_queda_mata: number; mult_queda: number;
  frutas_por_queda_min: number; frutas_por_queda_max: number; raio_queda_celulas: number; max_frutas_por_arvore: number; recarga_min: number;
  maduro_fruta_min: number; maduro_racao_min: number; prazo_podre_min: number;
  bola_min_celulas: number; bola_max_celulas: number; mult_bola_campo: number; atrito: number;
  perto_max_celulas: number; longe_min_celulas: number; longe_max_celulas: number; raio_mancha_celulas: number;
}
/* os nomes em snake_case de proposito: o espelho campo a campo da ConfigMundo do Python, conferido pelo nome */
export const CMU: ConfigMundo = {
  ligada: true, layout: LAYOUT_MUNDO_PADRAO, celulas_x: 64, celulas_y: 30, sub: 16,
  velocidade: 4, custo_energia_por_subunidade: 1 / 6000, raio_pegar_celulas: 1,
  raio_visao_celulas: 6, max_vistos: 8, cheiro_racao: 64, cheiro_fruta: 32, raio_cheiro_celulas: 24,
  limiar_cheiro_explorar: 16, passo_cheiro_celulas: 8, vagar_min_celulas: 4, vagar_max_celulas: 12,
  fome_max_comer_achado: .85, nutricao_fruta: .15, efeito_podre: -.10, ganho_humor_bola: .15,
  passo_mundo_ticks: 15, p_queda_jardim: 1 / 96, p_queda_mata: 2 / 96, mult_queda: 1,
  frutas_por_queda_min: 1, frutas_por_queda_max: 3, raio_queda_celulas: 2, max_frutas_por_arvore: 4, recarga_min: 720,
  maduro_fruta_min: 720, maduro_racao_min: 1440, prazo_podre_min: 720,
  bola_min_celulas: 3, bola_max_celulas: 10, mult_bola_campo: 2, atrito: 8,
  perto_max_celulas: 2, longe_min_celulas: 20, longe_max_celulas: 30, raio_mancha_celulas: 3,
};

/* V2, o corpo do Creatures 3 por baixo dos drives (docs/TAREFA_V2_CORPO_DRIVES.md, etapa 7): espelho da ConfigCorpo de
   digilab/config.py, campo a campo (snake_case de proposito, conferido pelo nome contra o gabarito do Python). O motor do corpo e
   motor/corpo.ts. Aqui e o padrao: desligado (o corpo so existe com `ligada`); corpo.configCorpo troca campos e confere as
   sub-chaves. Os numeros das secoes 7, 8 e 17 sao PROPOSTOS, sem fonte, como no Python. */
export interface ConfigCorpo {
  ligada: boolean; digestao: boolean; vida: boolean; drives_novos: boolean; gestos: boolean; banheiro: boolean;
  escala: number; escala_receptor: number; bits_meia_vida: number;
  pet_brincar_cansaco: number; pet_explorar_cansaco: number; pet_explorar_tristeza: number; pet_comer_fome: number;
  pet_emburrar_tristeza: number;
  k_meia_vida_susto: number; k_meia_vida_dor: number; k_meia_vida_estresse: number;
  taxa_digestao: number; vida_decaimento: number;
  tedio_sobe: number; curiosidade_sobe: number; solidao_sobe: number; estresse_limiar: number; estresse_divisor: number;
  janela_tedio: number; tedio_bola: number; tedio_brincar: number; tedio_explorar: number; tedio_dono: number;
  curiosidade_novidade: number; curiosidade_max_novidades: number; janela_novidade: number;
  carinho_solidao: number; carinho_estresse: number; tapa_dor: number; tapa_susto: number; tapa_estresse: number; medo_da_mao: number;
  /* o banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 3 e BN-6): so o espelho dos numeros; a quimica em TS e a etapa 4 do banheiro */
  vontade_sobe: number; vontade_digestao_num: number; vontade_digestao_den: number; vontade_limiar: number; vontade_desconforto: number;
  necessidade_desconforto: number; necessidade_regiao: number; necessidade_max_regiao: number; conforto_carinho: number;
  k_meia_vida_conforto: number;
  /* o metabolismo (docs/TAREFA_V2_METABOLISMO.md, secao 3): so o espelho dos numeros; a quimica em TS e a etapa 4 do metabolismo */
  metabolismo: boolean; combustivel_inicial: number; reserva_inicial: number; conversao_num: number; conversao_den: number;
  gasto_basal_acordado: number; gasto_basal_dormindo: number; armazenar_limiar: number; armazenar_taxa: number;
  mobilizar_limiar: number; mobilizar_taxa: number; falta_limiar: number; falta_cansaco: number;
  gasto_atividades_num: number; gasto_atividades_den: number;
  /* o Paladar (docs/futuro/paladar.md, secao 3.2): so o espelho dos numeros; o orgao em TS e a etapa 5 do paladar (o A) */
  paladar: boolean; meia_vida_sabor: number; k_meia_vida_sabor: number; meia_vida_saciedade: number; k_meia_vida_saciedade: number;
  saciedade_num: number; saciedade_den: number; paladar_h_min: number; paladar_h_max: number; paladar_h_salgado: number;
}
export const CCO: ConfigCorpo = {
  ligada: false, digestao: false, vida: false, drives_novos: false, gestos: false, banheiro: false,
  escala: 450000, escala_receptor: 1024, bits_meia_vida: 16,
  pet_brincar_cansaco: 9000, pet_explorar_cansaco: 6750, pet_explorar_tristeza: -4500, pet_comer_fome: -22500,
  pet_emburrar_tristeza: 4500,
  k_meia_vida_susto: 1497, k_meia_vida_dor: 753, k_meia_vida_estresse: 32,
  taxa_digestao: 450000, vida_decaimento: 11,
  tedio_sobe: 450, curiosidade_sobe: 300, solidao_sobe: 225, estresse_limiar: 337500, estresse_divisor: 256,
  janela_tedio: 8, tedio_bola: 135000, tedio_brincar: 45000, tedio_explorar: 90000, tedio_dono: 90000,
  curiosidade_novidade: 90000, curiosidade_max_novidades: 2, janela_novidade: 1440,
  carinho_solidao: 180000, carinho_estresse: 90000, tapa_dor: 90000, tapa_susto: 180000, tapa_estresse: 45000, medo_da_mao: 1,
  vontade_sobe: 150, vontade_digestao_num: 1, vontade_digestao_den: 3, vontade_limiar: 337500, vontade_desconforto: 150,
  necessidade_desconforto: 22500, necessidade_regiao: 100, necessidade_max_regiao: 3, conforto_carinho: 45000,
  k_meia_vida_conforto: 753,
  metabolismo: false, combustivel_inicial: 225000, reserva_inicial: 112500, conversao_num: 1, conversao_den: 1,
  gasto_basal_acordado: 375, gasto_basal_dormindo: 187, armazenar_limiar: 337500, armazenar_taxa: 375,
  mobilizar_limiar: 225000, mobilizar_taxa: 375, falta_limiar: 112500, falta_cansaco: 500,
  gasto_atividades_num: 1, gasto_atividades_den: 1,
  paladar: false, meia_vida_sabor: 4, k_meia_vida_sabor: 10427, meia_vida_saciedade: 720, k_meia_vida_saciedade: 63,
  saciedade_num: 1, saciedade_den: 2, paladar_h_min: -512, paladar_h_max: 1024, paladar_h_salgado: 256,
};
/* pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md; a etapa 4 de docs/TAREFA_V2_METABOLISMO.md): o corpo do ponto do v11, o que muda
   sobre o CCO (corpo.configCorpo o completa e confere). E a ConfigCorpo que as vidas do v11 do gabarito usaram (config_v11.corpo de
   test/gabaritos/lobos_python.json): a etapa 6 inteira com o metabolismo, sem o mundo fisico, o banheiro e o paladar; o ponto (2, 1) do
   adendo 4 (as subidas x 2: o tedio e a solidao, o divisor do estresse / 2; as reducoes x 1) e o gasto 4/5 do adendo 5 (o basal
   300/150 e as atividades x 4/5, o unico numero do corpo que fechou). PROPOSTOS, nenhum validado no jogo. */
export const CCO_V11: Partial<ConfigCorpo> = {
  ligada: true, digestao: true, vida: true, drives_novos: true, gestos: true, metabolismo: true,
  tedio_sobe: 900, solidao_sobe: 450, estresse_divisor: 128,
  gasto_basal_acordado: 300, gasto_basal_dormindo: 150, gasto_atividades_num: 4, gasto_atividades_den: 5,
};
/* Config.limiar_privacao do Python (Estado.em_privacao: algum de fome, higiene e energia abaixo disto); estado.ts usa o mesmo literal.
   Fica fora de C de proposito: C e conferido folha a folha contra o HTML antigo (test/constantes.test.mjs), que nao o tem */
export const LIMIAR_PRIVACAO = .15;
