/* O laco do motor com o corpo por tick, o dos pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 4): o porte do `_laco`, do `_decidir`,
   do `_aplicar_acao_usuario` e do `_gesto` de digilab/motor_corpo.py, no motor do v11 do Python, com_corpo(MotorComFeedback) no mundo
   `padrao` (experiments/bancada/nucleo.py, fabrica_motor, sem genoma), com a ConfigCorpo do regime `corpo` (drives novos e gestos).

   O que fica de fora, e falha alto se pedido: o mundo fisico, a bola, as frutas, o banheiro, os orgaos, a troca da digestao, a educacao,
   a obediencia e o treino (nenhum deles e do v11; PW-1). O elogio e a bronca nao existem no v11 (decisao de produto de 2026-10-07): aqui
   eles falham alto, embora o MotorCorpo do Python os aceite como estimulo.

   As duas rng sao as do engine.Motor do Python: a do ambiente e random.Random(semente) e a da politica random.Random(semente + 1_000_003),
   com o Mersenne Twister do CPython que o mundo.ts ja porta (RandomPy). A do ambiente so sorteia a sujeira do tick (state.avancar_um_tick,
   com o pet acordado) e a sujeira depois do alimentar; a da politica, o sorteio do cerebro. Nada aqui usa o mulberry32 do jogo.

   O laco de um tick, como no Python: a sincronia conferida (G-BYPASS), a decisao se for a hora, o passo do corpo sobre o estado do
   comeco do tick e o `avancarTick` de hoje (o tick e a sujeira, na mesma rng e na mesma ordem), com os drives float trocados pela leitura
   da quimica. Sem `cfg_evo` (o MotorComFeedback nao tem treino), o estagio pela Vida nao e conferido contra o de hoje, como no Python. */
import { C, TPD } from "./constantes.ts";
import { CCO_CORPO_V11, Corpo, DRIVE_DO_QUIMICO, VALOR_TAPA } from "./corpo.ts";
import { aplicarAcaoDono, avancarTick, efeitoAcaoPet, vetor } from "./estado.ts";
import type { ObservacaoLobos, OcorridoCorpo, RngCerebro, TransicaoLobos } from "./lobos.ts";
import { RandomPy } from "./mundo.ts";
import type { ConfigCorpo } from "./constantes.ts";
import type { AcaoDono, AcaoPet, EstadoVida } from "./tipos.ts";

/** G-BYPASS: com o corpo ligado, um drive do Estado mudou por fora da quimica */
export class ForaDoCorpo extends Error {}

/** a politica que o laco chama, nos ganchos do MotorCorpo do Python (a BracoConsequencia do v11 os tem todos) */
export interface PoliticaCorpo {
  agir(obs: ObservacaoLobos, rng: RngCerebro): AcaoPet;
  observar(t: TransicaoLobos): void;
  consequenciaCorpo(acao: AcaoPet, ocorrido: OcorridoCorpo, obsDepois: ObservacaoLobos): void;
  receberAcaoDono(acao: string, tick: number): void;
  mudancaNoCorpo(antes: ObservacaoLobos, depois: ObservacaoLobos): void;
}

/** um evento do log do Python (events.py): o avanco e a acao do dono */
export interface EventoCorpo { tick: number; tipo: "avanco" | "acao_usuario"; valor: number | string }

/** as acoes do dono que o v11 aceita: as quatro de cuidado e o tapa (o carinho e o tapa sao gestos, CD-6) */
export const ACOES_DONO_V11 = ["alimentar", "limpar", "brincar", "acariciar", VALOR_TAPA] as const;
type AcaoDonoV11 = (typeof ACOES_DONO_V11)[number];

const DRIVES = ["fome", "higiene", "energia", "humor", "saude"] as const;
/** o deslocamento da semente da rng da politica (engine.Motor) */
const DESLOCAMENTO_RNG_POLITICA = 1_000_003;

/** o estado do comeco da vida do Python (state.Estado()): tick 0 e os drives de nascimento */
export function estadoNascimentoPy(tick = 0): EstadoVida {
  return { tick, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1, sujeira: 0, dormindo: false, ultimoCuidado: tick, totalCuidados: 0 };
}

export class MotorCorpo {
  readonly politica: PoliticaCorpo;
  readonly semente: number;
  readonly cc: ConfigCorpo;
  readonly corpo: Corpo;
  readonly log: EventoCorpo[] = [];
  /** as acoes do pet com o tick (o _acoes_pet do Python) */
  readonly acoesPet: [number, AcaoPet][] = [];
  estado: EstadoVida;
  acaoAtual: AcaoPet = "ocioso";
  proximaDecisao = 0;
  /** quantas vezes o gancho `consequenciaCorpo` e o `mudancaNoCorpo` (o carinho) foram chamados */
  consequencias = 0;
  mudancas = 0;
  private readonly rngAmbiente: RandomPy;
  private readonly rngPolitica: RandomPy;
  private estimulos: (string | number)[][] = [];

  constructor(politica: PoliticaCorpo, semente: number, cc: ConfigCorpo = CCO_CORPO_V11, estado: EstadoVida = estadoNascimentoPy()) {
    if (!Number.isSafeInteger(semente)) throw new Error(`semente do motor tem de ser inteira: ${semente}`);
    if (!cc.ligada || !cc.drives_novos || !cc.gestos) {
      throw new Error("o laco do v11 e o do regime `corpo`: ConfigCorpo ligada, com os drives novos e os gestos");
    }
    this.politica = politica;
    this.semente = semente;
    this.cc = cc;
    this.rngAmbiente = new RandomPy(semente);
    this.rngPolitica = new RandomPy(semente + DESLOCAMENTO_RNG_POLITICA);
    this.corpo = Corpo.deEstado(estado, { cc });
    this.estado = this.corpo.noEstado(estado);
  }

  // ------------------------------------------------------------ a API do engine.Motor
  observar(acao: string): void {
    this.log.push({ tick: this.estado.tick, tipo: "acao_usuario", valor: acao });
    this.aplicarAcaoUsuario(acao);
  }

  avancar(ticks: number): [number, AcaoPet][] {
    if (!Number.isInteger(ticks) || ticks < 0) throw new Error(`avanco precisa de ticks inteiros >= 0: ${ticks}`);
    this.log.push({ tick: this.estado.tick, tipo: "avanco", valor: ticks });
    return this.laco(ticks);
  }

  /** o laco de um tick e a acao do dono sem o log do MotorCorpo: os pets v11 do jogo (motor.ts) gravam o registro do Motor, e o
   *  MotorCorpo so roda a vida por baixo. A mesma conta do avancar e do observar */
  passo(): [number, AcaoPet][] { return this.laco(1); }
  acaoDono(acao: string): void { this.aplicarAcaoUsuario(acao); }

  /** o passo do replay: o evento tem de cair no tick de agora (o log e a vida andam juntos) */
  aplicarEvento(e: EventoCorpo): void {
    if (e.tick !== this.estado.tick) throw new Error(`evento no tick ${e.tick}, o motor esta no ${this.estado.tick}`);
    if (e.tipo === "avanco") this.avancar(e.valor as number);
    else if (e.tipo === "acao_usuario") this.observar(e.valor as string);
    else throw new Error(`evento desconhecido no log: ${JSON.stringify(e)}`);
  }

  /** o motor.estado() do Python: o Estado (com os nomes do Python), a acao atual, a hora do dia e o corpo */
  estadoDict(): Record<string, unknown> {
    const e = this.estado;
    return {
      tick: e.tick, fome: e.fome, higiene: e.higiene, energia: e.energia, humor: e.humor, saude: e.saude, sujeira: e.sujeira,
      dormindo: e.dormindo, tick_ultimo_cuidado: e.ultimoCuidado, total_cuidados: e.totalCuidados, acao_atual: this.acaoAtual,
      tick_do_dia: e.tick % TPD, corpo: this.corpo.paraDict(),
    };
  }

  // ------------------------------------------------------------ leituras
  observacao(): ObservacaoLobos {
    return { v: vetor(this.estado), tdc: this.estado.tick - this.estado.ultimoCuidado, corpo: this.corpo.receptores() };
  }

  private conferirSincronia(onde: string): void {
    const leitura = this.corpo.drives();
    const fora = DRIVES.filter((d) => this.estado[d] !== leitura[d]);
    if (fora.length) throw new ForaDoCorpo(`${onde}, tick ${this.estado.tick}: drive mudado por fora do corpo ${fora}`);
  }

  private conferirEstimulo(onde: string, permitidos: ReadonlySet<string>): void {
    const leitura = this.corpo.drives();
    const fora = DRIVES.filter((d) => !permitidos.has(d) && this.estado[d] !== leitura[d]);
    if (fora.length) throw new ForaDoCorpo(`${onde}, tick ${this.estado.tick}: drive mudado por fora do estimulo ${fora}`);
  }

  private sincronizar(): void {
    this.estado = this.corpo.noEstado(this.estado);
  }

  // ------------------------------------------------------------ o laco do tick (MotorCorpo._laco)
  private laco(ticks: number): [number, AcaoPet][] {
    const produzidas: [number, AcaoPet][] = [];
    for (let i = 0; i < ticks; i++) {
      this.conferirSincronia("tick");
      if (this.estado.tick >= this.proximaDecisao) this.decidir(produzidas);
      const antes = this.estado;
      this.corpo.passo(antes);
      // o tick e a sujeira de hoje (a mesma rng, na mesma ordem); os drives float dele sao trocados pela leitura
      this.estado = this.corpo.noEstado(avancarTick(antes, this.rngAmbiente));
    }
    return produzidas;
  }

  /** MotorCorpo._decidir, sem a bola e sem o mundo: a decisao, o efeito do pet (o float so deixa o dormindo), a transicao, a atividade
   *  do tedio e o gancho do corpo */
  private decidir(produzidas: [number, AcaoPet][]): void {
    const intervalo = C.intervalo;
    const obs = this.observacao();
    const acao = this.politica.agir(obs, this.rngPolitica);
    this.acaoAtual = acao;
    const e = efeitoAcaoPet(this.estado, acao);
    this.corpo.acaoPet(acao);
    this.estado = this.corpo.noEstado(e);
    this.estimulos = [["pet", acao]];
    this.acoesPet.push([this.estado.tick, acao]);
    produzidas.push([this.estado.tick, acao]);
    this.proximaDecisao = this.estado.tick + intervalo;
    this.politica.observar({ observacao: obs, acao, observacaoSeguinte: this.observacao() });
    this.conferirEstimulo("decisao", new Set());
    this.sincronizar();
    this.atividade(acao);
    this.politica.consequenciaCorpo(acao, { acao, estimulos: this.estimulos.map((s) => [...s]) }, this.observacao());
    this.consequencias += 1;
  }

  /** o tedio pela variedade (DS-4): a atividade da propria acao, depois dos estimulos dela (sem a bola: brincar e "brincar") */
  private atividade(acao: AcaoPet): void {
    const nome = acao === "brincar" ? "brincar" : acao === "explorar" ? "explorar" : null;
    if (nome === null) return;
    this.corpo.atividade(nome);
    this.estimulos.push(["atividade", nome]);
  }

  // ------------------------------------------------------------ o dono (MotorCorpo._aplicar_acao_usuario e MotorComFeedback)
  private aplicarAcaoUsuario(acao: string): void {
    if (!(ACOES_DONO_V11 as readonly string[]).includes(acao)) {
      throw new Error(`acao do dono fora do v11: ${acao} (so ${ACOES_DONO_V11}; o v11 nao tem elogio nem bronca)`);
    }
    const a = acao as AcaoDonoV11;
    if (a === VALOR_TAPA || a === "acariciar") {
      this.gesto(a);
      return;
    }
    const tick = this.estado.tick;
    this.conferirSincronia(`antes de ${a}`);
    this.estado = aplicarAcaoDono(this.estado, a as AcaoDono, this.rngAmbiente);
    this.politica.receberAcaoDono(a, tick);              // o MotorComFeedback, logo depois de aplicar
    const deltas = this.corpo.t.dono[a];
    // os drives que a acao de hoje muda (o combustivel do metabolismo nao e drive: so o corpo o tem)
    this.conferirEstimulo(a, new Set(Object.keys(deltas).filter((q) => q in DRIVE_DO_QUIMICO).map((q) => DRIVE_DO_QUIMICO[q])));
    if (Object.keys(deltas).length) this.corpo.acaoDono(a);
    this.sincronizar();
  }

  /** o tapa e o carinho (secao 8): contato que conta como cuidado, efeito so no corpo. O tapa vai ao cerebro pelo receberAcaoDono; o
   *  carinho, so pelo mudancaNoCorpo(antes, depois) */
  private gesto(acao: "acariciar" | typeof VALOR_TAPA): void {
    const tick = this.estado.tick;
    this.conferirSincronia(`antes de ${acao}`);
    const antes = acao === "acariciar" ? this.observacao() : null;
    this.estado = { ...this.estado, ultimoCuidado: tick, totalCuidados: this.estado.totalCuidados + 1 };
    this.corpo.acaoDono(acao);
    this.sincronizar();
    if (acao === VALOR_TAPA) this.politica.receberAcaoDono(acao, tick);
    if (antes !== null) {
      this.politica.mudancaNoCorpo(antes, this.observacao());
      this.mudancas += 1;
    }
  }
}
