/* O laco do motor com o corpo e o mundo fisico, o dos pets v12 (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 1; MV-1): o porte do
   com_corpo(MotorMundo) de digilab/motor_corpo.py e digilab/mundo.py, sobre o laco do v11 (motor_corpo.ts) e o Mundo (mundo.ts). O
   gabarito e o test/gabaritos/mvp_mundo_python.json (experiments/exportar_gabarito_mvp_mundo.py), decisao a decisao, com o mundo da
   pesquisa (o padrao); o pet v12 roda o mundo do produto (CMU_MVP, sem arvores, so a racao do jogador: a opcao 1 do Matheus de
   2026-10-24), com o gabarito test/gabaritos/mvp_produto_python.json (experiments/exportar_gabarito_mvp_produto.py).

   O que muda do laco do v11, na ordem do Python:
     - o corpo nasce com o mundo (a curiosidade, CD-8);
     - a decisao: o embrulho do mundo (_PoliticaComMundo) anda o mundo ate o tick e o pet percebe antes do `agir`; o que o pet ve ao
       decidir entra no registro de novidade; o comer nao da fome por si (MF-2, `acaoPet(acao, true)`); no `observar`, a consequencia do
       mundo vem antes do cerebro (anda, come, brinca), e a transicao leva a observacao de depois dela;
     - a consequencia do mundo vira estimulo no corpo (MotorCorpo._consequencia): o andar, a comida do mapa (`estimuloConsumoMundo`, a
       racao madura com o efeito do alimentar de hoje; MV-9), a bola, a novidade no explorar e a atividade ("bola" ou "brincar",
       "explorar");
     - o dono: o `alimentar` sai (GESTOS_PROIBIDOS do Python) e entra o `deixar_comida(tipo, x, y)`, que conta como contato como o
       alimentar de hoje (o tempo sem cuidado zera, um cuidado a mais, a politica recebe `alimentar`). O carinho e o tapa sao os do v11:
       eventos diretos ao pet, sem posicao do dono (MV-7).

   O cerebro A fica como no v11 (MV-2): sem as chaves do mundo, o alvo e o padrao do motor (o `escolher_alvo` dos lobos devolve null) e o
   `consequencia_mundo` dele nao faz nada; nenhum dos dois e chamado aqui. So a chave da v13 (`digibrain`, desligada; o modular, DM-5)
   faz o laco perguntar o alvo ao cerebro, com o `ponto` do lugar lembrado aceito so no explorar (a PE-14 revista; T-PONTO-4). O `fruta_comida` tambem nao (o A do TS nao o tem).

   `paridade`: o laco aceita tambem o elogio e a bronca, como o MotorCorpo do Python, so para rejogar o gabarito (os donos sinteticos
   da etapa 0 os usam). O jogo nao liga: o v12, como o v11, nao tem elogio nem bronca. */
import { C } from "./constantes.ts";
import type { ConfigCorpo, ConfigMundo } from "./constantes.ts";
import { CCO_CORPO_V11 } from "./corpo.ts";
import { efeitoAcaoPet } from "./estado.ts";
import { ACOES_DONO_V11, MotorCorpo, estadoNascimentoPy, type EventoCorpo, type PoliticaCorpo } from "./motor_corpo.ts";
import { Mundo, eventoDeixarComida, lerDeixarComida, regiaoDe, type PercepcaoMundo } from "./mundo.ts";
import type { AcaoPet, EstadoVida } from "./tipos.ts";

/** o que a consequencia do mundo devolve (o `ocorrido` do Python, com os nomes dele) */
export interface OcorridoMundo {
  acao: string; u: number; alvo: unknown; de: [number, number]; para: [number, number]; deslocamento: number; energia_gasta: number;
  chegou: boolean; comeu: { tipo: string; situacao: string } & Record<string, unknown> | null; brincou_com_bola: boolean;
  vistos_novos?: [number, string][];
}

export interface OpcoesLacoMundo {
  /** a regra da ultima decisao do cerebro (o `ultima_regra` do Python, no registro de cada decisao do mundo); sem ela, null */
  regra?: () => string | null;
  /** aceitar o elogio e a bronca (so a paridade com o gabarito do Python) */
  paridade?: boolean;
  /** o mundo (o `cfg_mundo` do Python); sem ele, o da pesquisa (CMU, o layout padrao) */
  cfgMundo?: ConfigMundo;
  /** a chave da v13 (o `ConfigDigibrain.ligada` do Python, DM-5), desligada: so com ela o laco pergunta o alvo ao cerebro
   *  (`politica.escolherAlvo`, o `escolher_alvo` do Python), e o Mundo valida o que vier (os candidatos e, so no explorar, o `ponto`
   *  inteiro dentro do mapa; T-PONTO-4). Desligada (o v12 e o A), o alvo e o padrao do motor, como hoje */
  digibrain?: boolean;
}

/** as acoes do dono no laco com o mundo: as do v11 sem o alimentar (ele vira o deixar_comida) */
export const ACOES_DONO_MUNDO: readonly string[] = ACOES_DONO_V11.filter((a) => a !== "alimentar");
const ACOES_DONO_PARIDADE: readonly string[] = [...ACOES_DONO_MUNDO, "elogiar", "repreender"];

export class MotorCorpoMundo extends MotorCorpo {
  readonly mundo: Mundo;
  /** o registro do que o pet viu e quando (o id do objeto -> o ultimo tick em que o viu; `_vistos_em` do Python), derivado */
  readonly vistosEm = new Map<number, number>();
  private readonly regra: () => string | null;
  private readonly paridade: boolean;
  private readonly digibrain: boolean;

  constructor(politica: PoliticaCorpo, semente: number, cc: ConfigCorpo = CCO_CORPO_V11, estado: EstadoVida = estadoNascimentoPy(),
              opcoes: OpcoesLacoMundo = {}) {
    super(politica, semente, cc, estado, true);
    if (!cc.drives_novos) throw new Error("o laco com o mundo e o do regime `corpo` com os drives novos (a novidade e a atividade)");
    this.mundo = new Mundo({ semente, cfg: opcoes.cfgMundo });
    this.regra = opcoes.regra ?? (() => null);
    this.paridade = opcoes.paridade ?? false;
    this.digibrain = opcoes.digibrain ?? false;
  }

  // ------------------------------------------------------------ o dono
  protected override acoesAceitas(): readonly string[] { return this.paridade ? ACOES_DONO_PARIDADE : ACOES_DONO_MUNDO; }

  protected override aplicarAcaoUsuario(acao: string): void {
    if (acao === "alimentar") throw new Error("alimentar numa vida com o mundo: o dono deixa a racao num lugar (deixar_comida)");
    super.aplicarAcaoUsuario(acao);
  }

  /** o dono deixa a comida em (x, y): o evento valida o tipo e a posicao antes do log (MotorMundo.deixar_comida) */
  deixarComida(tipo: string, x: number, y: number): void {
    const ev = eventoDeixarComida(this.estado.tick, tipo, x, y);
    this.log.push({ tick: ev.tick, tipo: "deixar_comida", valor: ev.valor });
    this.comidaDoDono(...lerDeixarComida(ev));
  }

  /** o deixar_comida sem o log do laco (o Motor do jogo grava o registro dele): a comida no mundo e o contato do alimentar de hoje
   *  (MotorMundo._aplicar_deixar_comida e MotorEducacao._contato) */
  comidaDoDono(tipo: string, x: number, y: number): void {
    const tick = this.estado.tick;
    lerDeixarComida(eventoDeixarComida(tick, tipo, x, y));
    this.conferirSincronia("antes de deixar_comida");
    this.mundo.deixarComida(tick, tipo, x, y);
    this.estado = { ...this.estado, ultimoCuidado: tick, totalCuidados: this.estado.totalCuidados + 1 };
    this.politica.receberAcaoDono("alimentar", tick);
  }

  override aplicarEvento(e: EventoCorpo): void {
    if (e.tipo !== "deixar_comida") { super.aplicarEvento(e); return; }
    if (e.tick !== this.estado.tick) throw new Error(`evento no tick ${e.tick}, o motor esta no ${this.estado.tick}`);
    if (typeof e.valor !== "string") throw new Error(`deixar_comida malformado: ${JSON.stringify(e)}`);
    const [tipo, x, y] = lerDeixarComida({ tick: e.tick, tipo: "deixar_comida", valor: e.valor });
    this.deixarComida(tipo, x, y);
  }

  // ------------------------------------------------------------ a decisao (MotorCorpo._decidir com o embrulho do mundo)
  protected override decidir(produzidas: [number, AcaoPet][]): void {
    const intervalo = C.intervalo;
    const obs = this.observacao();
    this.antesDaDecisao();
    const acao = this.politica.agir(obs, this.rngPolitica);
    this.acaoAtual = acao;
    const e = efeitoAcaoPet(this.estado, acao);
    this.corpo.acaoPet(acao, true);                       // MF-2: com o mundo, o comer so da fome com comida do mapa
    this.estado = this.corpo.noEstado(e);
    this.estimulos = [["pet", acao]];
    this.acoesPet.push([this.estado.tick, acao]);
    produzidas.push([this.estado.tick, acao]);
    this.proximaDecisao = this.estado.tick + intervalo;
    // o observar do embrulho: a consequencia do mundo antes do cerebro, e a transicao com a observacao de depois dela
    this.consequencia(acao);
    this.politica.observar({ observacao: obs, acao, observacaoSeguinte: this.observacao() });
    this.conferirEstimulo("decisao", new Set());
    this.sincronizar();
    this.politica.consequenciaCorpo(acao, { acao, estimulos: this.estimulos.map((s) => [...s]) }, this.observacao());
    this.consequencias += 1;
  }

  /** o MotorMundo antes de cada decisao: o mundo anda ate o tick e o pet percebe; o que ele ve ao decidir entra no registro de novidade */
  protected antesDaDecisao(): PercepcaoMundo {
    const t = this.estado.tick;
    const p = this.mundo.antesDaDecisao(t, this.estado.fome);
    for (const v of p.vistos) this.vistosEm.set(v[0], t);
    return p;
  }

  /** a consequencia do mundo como estimulo no corpo (MotorCorpo._consequencia): o mundo escreve energia, fome, humor e sujeira no
   *  Estado; os drives viram os estimulos do corpo, e o Estado volta a ser a leitura */
  protected consequencia(acao: AcaoPet): OcorridoMundo | null {
    this.conferirSincronia("antes da consequencia do mundo");
    const ocorrido = this.consequenciaDoMundo(acao);
    if (ocorrido === null) {
      this.conferirEstimulo("mundo, acao sem alvo", new Set());
      return null;
    }
    const comeu = ocorrido.comeu, bola = ocorrido.brincou_com_bola;
    const permitidos = new Set(["energia", ...(comeu !== null ? ["fome", "humor"] : []), ...(bola ? ["humor"] : [])]);
    this.conferirEstimulo("mundo", permitidos);
    const cm = this.mundo.cm;
    this.corpo.estimuloAndar(ocorrido.deslocamento, cm.custo_energia_por_subunidade);
    this.estimulos.push(["andar", ocorrido.deslocamento]);
    if (comeu !== null) {
      this.corpo.estimuloConsumoMundo(comeu.tipo, comeu.situacao, cm, this.mundo.efeitoFrutas[comeu.tipo] ?? 0);
      this.estimulos.push(["comida", comeu.tipo, comeu.situacao]);
    }
    if (bola) {
      this.corpo.estimuloBola(cm.ganho_humor_bola);
      this.estimulos.push(["bola"]);
    }
    this.novidade(acao, ocorrido);
    this.atividadeMundo(acao, bola);
    this.sincronizar();
    return ocorrido;
  }

  /** a consequencia do MotorMundo (andar, comer, brincar, o MF-2 e o registro), com o Estado em float, antes do corpo */
  protected consequenciaDoMundo(acao: AcaoPet): OcorridoMundo | null {
    const e = this.estado;
    const escolher = this.digibrain ? this.politica.escolherAlvo ?? null : null;
    const r = this.mundo.consequencia(e.tick, acao, { fome: e.fome, energia: e.energia, humor: e.humor, sujeira: e.sujeira }, escolher,
                                      this.regra());
    this.estado = { ...this.estado, ...r.estado };
    return r.ocorrido as OcorridoMundo | null;
  }

  /** secao 7 do corpo: uma novidade e um objeto dos `vistos` que o pet nao viu nas ultimas `janela_novidade` ticks, achado numa decisao
   *  de explorar (na percepcao depois de andar); o que ele ja via ao decidir nao conta. Os `vistos_novos` vao ao `ocorrido` de toda
   *  decisao com alvo (vazio fora do explorar) */
  private novidade(acao: AcaoPet, ocorrido: OcorridoMundo): void {
    const tick = this.estado.tick;
    const vistos = this.mundo.perceber(tick).vistos;
    let novos: [number, string][] = [];
    if (acao === "explorar") {
      const J = this.cc.janela_novidade;
      novos = vistos.filter((v) => !this.vistosEm.has(v[0]) || tick - this.vistosEm.get(v[0])! >= J).map((v) => [v[0], v[1]]);
      this.corpo.estimuloNovidade(novos.length);
      this.estimulos.push(["novidade", novos.length]);
    }
    ocorrido.vistos_novos = novos;
    for (const v of vistos) this.vistosEm.set(v[0], tick);
  }

  /** o tedio pela variedade (DS-4) com o mundo: brincar com a bola e "bola", sem ela "brincar"; explorar e "explorar" */
  private atividadeMundo(acao: AcaoPet, bola: boolean): void {
    const nome = acao === "brincar" ? (bola ? "bola" : "brincar") : acao === "explorar" ? "explorar" : null;
    if (nome === null) return;
    this.corpo.atividade(nome);
    this.estimulos.push(["atividade", nome]);
  }

  // ------------------------------------------------------------ leitura
  /** o motor.estado() do Python com a chave `mundo` (a posicao, a regiao, a bola e as comidas no chao) */
  override estadoDict(): Record<string, unknown> {
    const m = this.mundo, t = this.estado.tick;
    return {
      ...super.estadoDict(),
      mundo: { pet: [m.pet[0], m.pet[1]], regiao: m.cm.layout.regioes[regiaoDe(m.pet[0], m.cm)][0], bola: m.bolaEm(t),
               comidas: [...m.comidas.values()].filter((c) => m.situacao(c, t) !== null).length },
    };
  }
}
