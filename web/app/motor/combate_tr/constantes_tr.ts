/* Os numeros da luta em tempo real (docs/ESPEC_COMBATE_TR.md; COMBATE-TR, etapa R1). Os do combate de hoje (o dano, o Guts, as tecnicas,
   as passivas) vem de constantes.ts (CV, CV21, CSO) e nao se repetem aqui; aqui ficam so os do relogio e do espaco. Todo tempo e um
   numero inteiro de passos de 16 ms. Status e fonte de cada um:
   - DECIDIDO (D-5, Matheus, 2026-10-29): o tempo de turno T_TR, o limite e a morte subita;
   - PROPOSTO, com a fonte: "PROTOTIPO" = o prototipo da arena (a pasta web/app/arena/, que saiu na R3 pela D-3; esta no commit efb2ded; sem medicao); "turnos x T_TR" = o numero por turnos de hoje
     convertido pelo T_TR; SEM FONTE onde nao ha. Nenhum foi calibrado: o equilibrio fica para a rodada do fim. */
import { CV } from "../constantes.ts";
import { Cd, Rg, validarLista, type ListaGambits } from "../combate.ts";

/** o passo fixo (ms). PROPOSTO, o da arena (o prototipo, arena/constantes.ts, PASSO_MS) */
export const PASSO_TR_MS = 16;
/** o tempo de turno T_TR em passos: 125 x 16 ms = 2 s. DECIDIDO (D-5); fonte: o ciclo de ataque padrao do prototipo (STATS_PADRAO.cad,
    2 000 ms) igualado a 1 turno */
export const T_TR = 125;

export const CTR_TR = {
  /** o limite da luta: 40 T_TR = 80 s. DECIDIDO (D-5; turnos x T_TR, CV.tMax) */
  limite: CV.tMax * T_TR,
  /** a morte subita: a partir de 25 T_TR = 50 s. DECIDIDO (D-5; turnos x T_TR, CV.turnoMS) */
  morteSubita: CV.turnoMS * T_TR,
  /** o ritmo das decisoes: o lutador livre decide no primeiro passo multiplo disto (16 passos = 256 ms). PROPOSTO; fonte: a reacao da
      CPU "normal" do prototipo (DIFIC.normal.reacao = 260 ms) */
  ritmo: 16,
  /** o instante do golpe dentro da acao (25 passos = 400 ms), igual para todos (D-1). PROPOSTO; fonte: o golpe generico do prototipo
      (o prototipo, arena/dados.ts, GOLPE_GENERICO.t = 0,4 s). A tela estica o clipe do UP para o quadro do golpe cair aqui */
  instante: 25,
  /** o atordoamento de quem tem o preparo interrompido (31 passos ~ 500 ms). PROPOSTO, SEM FONTE */
  atordoaInterrupcao: 31,
  /** px por passo: andar a 70 px/s (STATS_PADRAO.vel, PROTOTIPO); o recuo a 80% do andar (D-8; SEM FONTE); a arrancada da investida a
      420 px/s (ACAO.investidaJogador, PROTOTIPO); o projetil a 300 px/s (SEM FONTE). Todos x 16 / 1000 */
  andar: 70 * PASSO_TR_MS / 1000,
  recuo: .8,
  arrancada: 420 * PASSO_TR_MS / 1000,
  projetil: 300 * PASSO_TR_MS / 1000,
  /** as faixas de distancia (px entre os centros): perto ate 62 (EQ.alcanceCorpo 44 + EQ.raio 18, PROTOTIPO), medio ate 150
      (ACAO.alcanceDist, PROTOTIPO), longe acima. PROPOSTO */
  perto: 62, medio: 150,
  /** o avanco para quando a distancia chega a isto (EQ.alcanceCorpo, PROTOTIPO); os corpos nao chegam mais perto que isto
      ((EQ.raio + EQ.raio) x 0,9, como no passo() da arena, PROTOTIPO). PROPOSTO */
  contato: 44, minimo: 32.4,
  /** o raio do corpo: o projetil acerta ao chegar a isto do centro do alvo (EQ.raio, PROTOTIPO). PROPOSTO */
  raio: 18,
  /** o empurrao de um golpe corpo a corpo que acerta (px; ACAO.empurrao, PROTOTIPO). PROPOSTO, SEM FONTE para manter (espec 1.7) */
  empurrao: 6,
  /** o chao: uma linha no meio da elipse da arena (cx 240, rx 210, cerca a 20 px da borda: nucleo.prender, PROTOTIPO); cada lado entra
      a 65 px do centro (130 px entre os dois: o medio de hoje, estadoV2; SEM FONTE para o valor exato). PROPOSTO */
  centro: 240, meiaLargura: 190, entrada: 65,
} as const;

/** os numeros do relogio e do espaco que a rodada de equilibrio pode mudar (docs/PLANO_EQUILIBRIO_COMBATE_TR.md, secao 4). Eles viajam nas
    regras da luta (RegrasV21.relogio) e no estado dela (EstadoTR.C): cada versao de pet tem os seus, e a v13 tem os de CTR_TR. O limite, a
    morte subita (D-5), o instante do golpe (D-1) e a geometria do chao nao entram: ficam em CTR_TR. `disparo`: o multiplicador do dano
    do disparo so no tempo real (a base, CV.dano.disparo e o perfil, nao muda; decisao do Matheus de 2026-10-30, DECIDIDA pela
    recomendacao do coordenador: um numero proprio do tempo real, calibrado na rodada) */
export interface RelogioTR {
  readonly ritmo: number; readonly atordoaInterrupcao: number; readonly andar: number; readonly recuo: number; readonly arrancada: number;
  readonly projetil: number; readonly perto: number; readonly medio: number; readonly contato: number; readonly empurrao: number;
  readonly disparo: number;
}
/** o relogio dos pets v13 (os numeros de CTR_TR, sem calibracao; o disparo sem multiplicador, 1) */
export const RELOGIO_V13: RelogioTR = {
  ritmo: CTR_TR.ritmo, atordoaInterrupcao: CTR_TR.atordoaInterrupcao, andar: CTR_TR.andar, recuo: CTR_TR.recuo, arrancada: CTR_TR.arrancada,
  projetil: CTR_TR.projetil, perto: CTR_TR.perto, medio: CTR_TR.medio, contato: CTR_TR.contato, empurrao: CTR_TR.empurrao, disparo: 1,
};
/** o relogio candidato dos pets v14, da fase 1 da rodada de equilibrio (docs/PLANO_EQUILIBRIO_COMBATE_TR.md; docs/EQUILIBRIO_COMBATE_TR.md,
    fase 1). PROPOSTOS, calibrados so nas sementes de calibracao (68101 a 68505): web/app/scripts/medicoes/equilibrio_tr/fase1/grade3/
    r06arr8.json. O resto e o da v13. Ainda nao e de nenhuma versao de pet: a v14 so liga no fim da rodada, com os numeros de todas as fases
    (DE-1), e ate la so a bancada (scripts/equilibrio_tr/) o usa
    - empurrao 6 -> 0: o empurrao do golpe corpo a corpo afastava o atacante para fora do contato, e as listas defensivas nao voltavam;
    - medio 150 -> 120: a faixa media mais curta faz as listas sairem do longe mais cedo e reagirem ao preparo do rival (T-5);
    - recuo .8 -> .6 e arrancada 420 -> 500 px/s: quem recua o tempo todo (a sentinela) e alcancado;
    - disparo 1 -> 6: o melhor das formas na grade de 1,5 a 8 (depois da fase 3, DE-8; scripts/medicoes/equilibrio_tr/disparo/; a
      conferencia em disparo/conferencia_d6/). Todo valor acima de 1 reprova o T-1 da fase 1 (a luta media cai para perto de 35 s), e o
      Matheus decidiu ligar o 6 mesmo assim (DE-9, 2026-10-30): o T-1 fica reprovado e registrado como esta */
export const RELOGIO_V14: RelogioTR = { ...RELOGIO_V13, empurrao: 0, medio: 120, recuo: .6, arrancada: 500 * PASSO_TR_MS / 1000, disparo: 6 };

/** os fatores candidatos dos pets v14, da fase 4 da rodada de equilibrio (docs/EQUILIBRIO_COMBATE_TR.md, fase 4). PROPOSTOS, calibrados so
    nas sementes de calibracao (68101 a 68505): web/app/scripts/medicoes/equilibrio_tr/fase4/. As tabelas inteiras, com as mesmas chaves
    das de hoje (FATOR_LIDER_V9, CESC_V9.fatorNpc, FATOR_LIGA_V9, FATOR_INSTALACAO, FATOR_RIVAL_FABRICA_V9, FATOR_SALAO_V9; o teste
    listas_v14 confere); o que nao esta abaixo e o de hoje. Ainda nao e de nenhuma versao de pet (DE-1): so a bancada os usa
    - lider da Torre 1,5 -> 1,8: o pet sem treino vencia 0,08 (G-1 pede <= 0,05);
    - Tortomon (npc_tier2_sentinela) 1,53 -> 1,4: o desafiante do Champion e o rival sugerido do P-4 (DE-4); com 1,4 fecham G-2 e P-4;
    - Liga, Campina 0,4 -> 0,2 e Torre 0,3 -> 0,8: as formas de longe caiam no furioso da Campina e o duelista passava de 0,85 (G-3);
    - Salao, Rookie 1,15 -> 1,2 e Champion 1 -> 1,6: o pet tipico vencia mais de 0,95 (G-6);
    - rodada 2 (R2-3): o lider da Floresta 1,5 -> 1,4, com a lista candidata dele (LISTAS_LIDER_V14) */
export const FATORES_V14 = {
  lider: { campina: 1.3, torre: 1.8, floresta: 1.4, cidadela: .9, lago: 1.5, espiral: 1.4 } as Readonly<Record<string, number>>,
  npc: { npc_tier2_sentinela: 1.4, npc_tier2_porteiro: 1.1, npc_v5_puppetmon: 1.8, npc_v5_machinedramon: 2.3 } as Readonly<Record<string, number>>,
  liga: { campina: .2, torre: .8, floresta: .1, cidadela: 1, lago: 1.7, espiral: .9 } as Readonly<Record<string, number>>,
  instalacao: 1,
  fabrica: .6,
  salao: { crianca: 1.2, adolescente: 1.6, adulto: 1.05, mega: 1.05 } as Readonly<Record<string, number>>,
} as const;

/** o aprendizado proprio do tempo real do candidato v14 (DR2-5; docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md, R2-2): GambitsPet.aprendizadoTR.
    null = o GA de sempre (a ordem so pela nota). Ainda nao e de nenhuma versao de pet: so a bancada o usa. PROPOSTOS, calibrados so nas
    sementes de calibracao da rodada 2 (72101 a 72505; web/app/scripts/medicoes/equilibrio_tr/r2_2/, a grade 3):
    - limiar da troca -0,02 -> 0,05: o pet troca a pior regra mais cedo (com o limiar de hoje quase nao troca, e a lista so se reordena);
    - prior 0,1: a posicao na lista de partida pesa na ordem (a reserva e as especificas nao afundam so pela nota);
    - alfa 0,2 e bonus 0,1, os do GA */
export const APRENDIZADO_V14: { readonly alfa: number; readonly prior: number; readonly bonus?: number; readonly limiar?: number } | null =
  { alfa: .2, prior: .1, bonus: .1, limiar: .05 };

/** as listas candidatas dos lideres das arenas do candidato v14 (DR2-3; docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md, R2-3), pela id da arena, por
    cima das de hoje (as do motor). Ainda nao e de nenhuma versao de pet: so a bancada as usa. PROPOSTAS, so nas sementes de calibracao
    da rodada 2 (72101 a 72505; web/app/scripts/medicoes/equilibrio_tr/r2_3/, a variante l1_flo_fica com o fator 1,4):
    - a Floresta fica de perto (sem o recuo): o guardiao, que devolve o golpe, deixa de perder a luta inteira (o fator vai a 1,4,
      FATORES_V14). A Cidadela, o Lago e a Espiral ficam com as de hoje: nenhuma variante fechou o G-1 (ver o relatorio) */
const T10 = Cd("turno_execucao", 10), D0_ = Cd("distancia_eh", 0), D1_ = Cd("distancia_eh", 1), D2_ = Cd("distancia_eh", 2), GA20 = Cd("guts_proprio_acima", 20);
export const LISTAS_LIDER_V14: Readonly<Record<string, ListaGambits>> = {
  floresta: validarLista({ regras: [Rg([T10, D2_], "avancar"), Rg([T10, D1_], "avancar"), Rg([T10, GA20], "golpe_rapido"),
    Rg([Cd("oponente_preparando"), D0_], "esquivar"), Rg(GA20, "disparo")], final: "carregar" }),
};

/** as cartas candidatas do candidato v14 (DR2-4; docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md, R2-4): o efeito por cima do de hoje (itens.ts), pela
    id da carta. Vazio = as de hoje. Ainda nao e de nenhuma versao de pet: so a bancada as usa */
export const CARTAS_V14: Readonly<Record<string, import("../combate.ts").EfeitoCarta>> = {};
