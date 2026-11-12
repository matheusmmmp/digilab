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
   `consequencia_mundo` dele nao faz nada; nenhum dos dois e chamado aqui. So a chave do laboratorio (`digibrain`, desligada; o DigiBrain
   modular, docs/TAREFA_V3_LAB_MODULAR.md, LM4; antes, a "chave da v13", DM-5) faz o laco dar o mundo ao cerebro (`obs.mundo`), perguntar o
   alvo (`escolherAlvo`, com o `ponto` do lugar lembrado aceito so no explorar: a PE-14 revista; T-PONTO-4) e chamar o `consequenciaMundo`
   depois do `observar`, como o embrulho do MotorMundo do Python. O `fruta_comida` nao (o A do TS nao o tem): o laco o chama so se a
   politica tiver o gancho `frutaComida` (nenhuma do jogo tem) e a chave `frutaComoComida` (AS-11) estiver desligada, como o Python.

   O sacudir a arvore (docs/TAREFA_V3_ARVORE_SACODE.md, S2; as chaves `sacudir` e `frutaComoComida`, desligadas): o dono sacode uma
   arvore do layout (`sacudirArvore`, o evento `sacudir_arvore` do log), e so o mundo muda; nao e contato nem cuidado (AS-1).

   O gosto visual (GOSTO_VISUAL, P1f; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 1, 2, 4 e 8; a opcao `tela`, desligada): o espelho da TV do
   MotorMundo e do orgao da tela do MotorCorpo do Python (P1b a P1d). Ligada (so com um pet, fora do grupo), a TV e um objeto na celula
   `ConfigTV.celula`; antes de cada tick e de cada percepcao do corpo, o laco entrega ao corpo o que ela passa se o pet olha (zeros se nao);
   a novidade pelo corte (GV-23) a cada tick; o assistir (GV-21) e o agrado no corpo (GV-16, pelo gancho `agradoTela`) na decisao em que
   ele olha; as TVs a vista ao cerebro antes de cada decisao (`verTela`); e os eventos `trocar_canal` e `sentido_tela`, que so mudam a TV.
   O pet olha quando esta acordado, no ocioso, com a TV no raio da visao e, com o gancho `olhandoTela` (o DigiBrain), quando o cerebro
   escolheu olhar. Desligada, nada disto roda: a vida, o log e o save de hoje, byte a byte.

   `paridade`: o laco aceita tambem o elogio e a bronca, como o MotorCorpo do Python, so para rejogar o gabarito (os donos sinteticos
   da etapa 0 os usam). O jogo nao liga: o v12, como o v11, nao tem elogio nem bronca. */
import { C } from "./constantes.ts";
import {
  ATIVIDADE_TELA, CANAIS_TELA, ID_TV, RECEPTOR_NOVIDADE_TELA, TIPO_SENTIDO_TELA, TIPO_TROCAR_CANAL, TV, TVSemChave, conferirConfigTV,
  lerSentidoTela, lerTrocarCanal, valorSentidoTela, valorTrocarCanal, type ConfigTela, type ConfigTV,
} from "./tv.ts";
import type { ConfigCorpo, ConfigMundo, ConfigSacudir } from "./constantes.ts";
import { CCO_CORPO_V11 } from "./corpo.ts";
import type { ConfigContrato } from "./contrato.ts";
import { efeitoAcaoPet } from "./estado.ts";
import { ACOES_DONO_V11, MotorCorpo, estadoNascimentoPy, type EventoCorpo, type PoliticaCorpo } from "./motor_corpo.ts";
import type { ObservacaoLobos } from "./lobos.ts";
import type { ConfigEnjooTela } from "./enjoo_tela.ts";
import {
  Mundo, centroDaCelula, distancia, eventoDeixarComida, eventoLevarPet, eventoMudarIlha, eventoSacudirArvore, lerDeixarComida, lerLevarPet, lerMudarIlha, lerSacudirArvore,
  regiaoDe, tamanhoDoMapa, type OpcoesMundo, type PercepcaoMundo,
} from "./mundo.ts";
import type { AcaoPet, EstadoVida } from "./tipos.ts";

/** o que a consequencia do mundo devolve (o `ocorrido` do Python, com os nomes dele) */
export interface OcorridoMundo {
  acao: string; u: number; alvo: unknown; de: [number, number]; para: [number, number]; deslocamento: number; energia_gasta: number;
  chegou: boolean; comeu: { tipo: string; situacao: string } & Record<string, unknown> | null; brincou_com_bola: boolean;
  vistos_novos?: [number, string][];
}

/** a politica do laboratorio: o `consequenciaMundo` (o `consequencia_mundo` do Python) depois do `observar`, nas decisoes com alvo */
export interface PoliticaCorpoMundo extends PoliticaCorpo {
  consequenciaMundo?(acao: AcaoPet, ocorrido: OcorridoMundo, obsDepois: ObservacaoLobos): void;
  /** o `fruta_comida` do Python (a E2): o aviso de que o pet comeu a fruta `tipo`; nenhum cerebro do TS o tem. Com a fruta como comida
   *  (AS-11), o laco nao o chama */
  frutaComida?(tipo: string, obsDepois: ObservacaoLobos): void;
}

export interface OpcoesLacoMundo {
  /** a regra da ultima decisao do cerebro (o `ultima_regra` do Python, no registro de cada decisao do mundo); sem ela, null */
  regra?: () => string | null;
  /** aceitar o elogio e a bronca (so a paridade com o gabarito do Python) */
  paridade?: boolean;
  /** o mundo (o `cfg_mundo` do Python); sem ele, o da pesquisa (CMU, o layout padrao) */
  cfgMundo?: ConfigMundo;
  /** a chave do laboratorio (o `ConfigDigibrain.ligada` do Python, DM-5; LM4), desligada: so com ela o laco da a percepcao do mundo ao
   *  cerebro (`obs.mundo`), pergunta o alvo (`politica.escolherAlvo`, o `escolher_alvo` do Python) e chama o `consequenciaMundo`; o Mundo
   *  valida o que vier (os candidatos e, so no explorar, o `ponto` inteiro dentro do mapa; T-PONTO-4). Desligada (o v12 e o A), o alvo e o
   *  padrao do motor e nada disso e chamado, como hoje */
  digibrain?: boolean;
  /** a chave do produto `decisaoNaComida` (o `ConfigDecisaoNaComida.ligada` do Python), desligada: com ela, a comida que o dono deixa no
   *  chao faz o pet decidir ja no proximo passo do laco, em vez de esperar o fim do intervalo. O cerebro e a politica nao mudam: so o
   *  momento da decisao (a seguinte volta a contar o intervalo dali) */
  decidirNaComida?: boolean;
  /** a chave dos pets v15 (a ConfigBolaNoGolpe do Python), desligada: com ela, a bola sai na direcao em que o pet vinha (Mundo, OpcoesMundo) */
  bolaNoGolpe?: boolean;
  /** o contrato da P4 (o `cfg_contrato` do Python), desligado: o layout com agua exige o controlador (docs/TAREFA_V3_ILHA_AGUA.md) */
  contrato?: ConfigContrato;
  /** o sacudir a arvore (a ConfigSacudir do Python, `cfg_sacudir`), desligado: com ele, o mundo tem o galho, as arvores na casa e o
   *  evento `sacudir_arvore` (docs/TAREFA_V3_ARVORE_SACODE.md). Nenhuma versao de pet o liga ainda (D-AS-S2-1) */
  sacudir?: ConfigSacudir;
  /** a fruta do mundo como comida (a ConfigFrutaComoComida do Python, AS-11), desligada: com ela, o laco nao entrega o `frutaComida` */
  frutaComoComida?: boolean;
  /** dois pets (docs/TAREFA_V3_COOPERACAO.md, CO4b): a parte do pet no mundo do grupo, montada pelo Grupo com as opcoes deste laco (o
   *  `mundo=` do MotorMundo do Python). Sem ela, o laco e dono do proprio mundo, com a semente do pet: a vida de hoje */
  parteDoMundo?: (op: OpcoesMundo) => Mundo;
  /** o gosto visual (P1f): o orgao da tela no corpo e a TV no mundo, juntos e ligados (a `cfg_tela` e a `cfg_tv` do Python). Sem ela, nada */
  tela?: { readonly tela: ConfigTela; readonly tv: ConfigTV; readonly enjoo?: ConfigEnjooTela };   // `enjoo`: D-GV-ENJOO-CER
}

const FRUTAS_DO_MUNDO: readonly string[] = ["a", "b", "c"];

/** as acoes do dono no laco com o mundo: as do v11 sem o alimentar (ele vira o deixar_comida) */
export const ACOES_DONO_MUNDO: readonly string[] = ACOES_DONO_V11.filter((a) => a !== "alimentar");
const ACOES_DONO_PARIDADE: readonly string[] = [...ACOES_DONO_MUNDO, "elogiar", "repreender"];

export class MotorCorpoMundo extends MotorCorpo {
  readonly mundo: Mundo;
  /** o registro do que o pet viu e quando (o id do objeto -> o ultimo tick em que o viu; `_vistos_em` do Python), derivado */
  readonly vistosEm = new Map<number, number>();
  private readonly regra: () => string | null;
  private readonly paridade: boolean;
  /** a chave do laboratorio (OpcoesLacoMundo.digibrain); o Motor da v17 a vira quando o cerebro troca (o evento "cb"), sempre entre decisoes */
  digibrain: boolean;
  /** a chave `decisaoNaComida` (OpcoesLacoMundo); o Motor do jogo a liga pelo evento das chaves do produto, no comeco do registro */
  decidirNaComida: boolean;
  /** a fruta do mundo como comida (OpcoesLacoMundo, AS-11) */
  readonly frutaComoComida: boolean;
  /** a TV (P1f): null sem a opcao `tela` (a vida de hoje) */
  readonly tv: TV | null = null;
  /** os ticks em que o `novidade_tela` passou do corte (GV-23), derivados */
  readonly novidadesTela: number[] = [];
  private telaAcima = false;

  constructor(politica: PoliticaCorpo, semente: number, cc: ConfigCorpo = CCO_CORPO_V11, estado: EstadoVida = estadoNascimentoPy(),
              opcoes: OpcoesLacoMundo = {}) {
    if (opcoes.tela !== undefined) {
      const { tela, tv } = opcoes.tela;
      if (!tela.ligada || !tv.ligada) throw new TVSemChave("a TV no mundo e o orgao da tela no corpo vao juntos e ligados (espec do P1, secao 8)");
      if (tv.escala !== tela.teto_intensidade) throw new Error(`a escala da TV (${tv.escala}) tem de ser o teto_intensidade da tela (${tela.teto_intensidade})`);
      if (opcoes.parteDoMundo !== undefined) throw new TVSemChave("a TV (ConfigTV) roda com um pet, fora do grupo");
    }
    super(politica, semente, cc, estado, true, opcoes.tela?.tela, opcoes.tela?.enjoo);
    if (!cc.drives_novos) throw new Error("o laco com o mundo e o do regime `corpo` com os drives novos (a novidade e a atividade)");
    const op: OpcoesMundo = { semente, cfg: opcoes.cfgMundo, bolaNoGolpe: opcoes.bolaNoGolpe ?? false, contrato: opcoes.contrato,
                              ...(opcoes.sacudir !== undefined ? { sacudir: opcoes.sacudir } : {}) };
    this.mundo = opcoes.parteDoMundo ? opcoes.parteDoMundo(op) : new Mundo(op);
    if (opcoes.frutaComoComida !== undefined && typeof opcoes.frutaComoComida !== "boolean")
      throw new Error(`frutaComoComida e bool: ${String(opcoes.frutaComoComida)}`);
    this.frutaComoComida = opcoes.frutaComoComida ?? false;
    this.regra = opcoes.regra ?? (() => null);
    this.paridade = opcoes.paridade ?? false;
    this.digibrain = opcoes.digibrain ?? false;
    this.decidirNaComida = opcoes.decidirNaComida ?? false;
    if (opcoes.tela !== undefined) {
      const ctv = conferirConfigTV(opcoes.tela.tv), cm = this.mundo.cm;
      const [cx, cy] = ctv.celula;
      if (!(cx < cm.celulas_x && cy < cm.celulas_y)) throw new Error(`a celula da TV ${ctv.celula} fora do mapa (${cm.celulas_x} x ${cm.celulas_y})`);
      const [x, y] = centroDaCelula(ctv.celula, cm);
      if (!this.mundo.comum.seca(x, y)) throw new Error(`a celula da TV ${ctv.celula} e agua`);
      this.tv = new TV(ctv, semente, x, y);
    }
  }

  // ------------------------------------------------------------ a TV (GOSTO_VISUAL, P1f; o MotorMundo e o MotorCorpo do Python)
  private exigirTv(onde: string): TV {
    if (this.tv === null) throw new TVSemChave(`${onde} sem a TV ligada (a opcao tela do laco)`);
    return this.tv;
  }

  /** o pet olha a TV: ela passa algo, o pet esta acordado e no ocioso, a TV esta no raio da visao e, com o gancho `olhandoTela`, o cerebro
   *  escolheu olhar esta TV */
  private olhandoTv(passa: unknown): boolean {
    if (passa === null || this.estado.dormindo || this.acaoAtual !== "ocioso") return false;
    const olhando = this.politica.olhandoTela;
    if (olhando !== undefined && olhando.call(this.politica) !== ID_TV) return false;
    const tv = this.tv!, p = this.mundo.pet;
    return distancia(tv.x - p[0], tv.y - p[1]) <= this.mundo.raioDaVisao;
  }

  /** se o pet olha a TV agora (so le) */
  olhandoTV(): boolean {
    const tv = this.exigirTv("olhandoTV");
    return this.olhandoTv(tv.em(this.mundo.tm(this.estado.tick)));
  }

  /** as TVs a vista para o cerebro (`verTela`): [id, dx, dy, d] da TV ligada no raio da visao; senao, nenhuma */
  private linhasTela(): [number, number, number, number][] {
    const tv = this.tv!, p = this.mundo.pet;
    const dx = tv.x - p[0], dy = tv.y - p[1], d = distancia(dx, dy);
    if (tv.em(this.mundo.tm(this.estado.tick)) === null || d > this.mundo.raioDaVisao) return [];
    return [[ID_TV, dx, dy, d]];
  }

  protected override sentirAgora(): void {
    if (this.tv === null) return;
    const passa = this.tv.em(this.mundo.tm(this.estado.tick));
    this.corpo.sentirTela(this.olhandoTv(passa) ? { ...passa! } : Object.fromEntries(CANAIS_TELA.map((c) => [c, 0])));
  }

  protected override antesDoPasso(): void {
    if (this.tv === null) return;
    this.sentirAgora();
    const acima = this.corpo.leiturasTela()[RECEPTOR_NOVIDADE_TELA]! > this.corpo.tela.corte_novidade;   // GV-23: uma por subida
    if (acima && !this.telaAcima) {
      this.corpo.estimuloNovidade(1);
      this.novidadesTela.push(this.estado.tick);
    }
    this.telaAcima = acima;
  }

  /** o dono troca o canal da TV do jogo (a fonte "grade"): valida antes do log */
  trocarCanal(programa: number): void {
    const valor = valorTrocarCanal(programa);
    this.canalDoDono(lerTrocarCanal(valor));
    this.log.push({ tick: this.estado.tick, tipo: TIPO_TROCAR_CANAL, valor });
  }

  /** o trocar_canal sem o log do laco: so a TV muda (nao e contato nem cuidado, GV-22) */
  canalDoDono(programa: number): void {
    this.exigirTv("trocar_canal").trocarCanal(programa, this.mundo.tm(this.estado.tick));
  }

  /** o modo livre gravado (a fonte "evento"): o que a TV passa a partir de agora; valida antes do log */
  sentidoTela(fonte: string, niveis: readonly number[]): void {
    const valor = valorSentidoTela(fonte, niveis);
    this.telaDoDono(...lerSentidoTela(valor));
    this.log.push({ tick: this.estado.tick, tipo: TIPO_SENTIDO_TELA, valor });
  }

  /** o sentido_tela sem o log do laco: so a TV muda (o replay le o evento) */
  telaDoDono(fonte: string, niveis: readonly number[]): void {
    this.exigirTv("sentido_tela").sentir(fonte, niveis, this.mundo.tm(this.estado.tick));
  }

  // ------------------------------------------------------------ o dono
  protected override acoesAceitas(): readonly string[] { return this.paridade ? ACOES_DONO_PARIDADE : ACOES_DONO_MUNDO; }

  protected override aplicarAcaoUsuario(acao: string): void {
    if (acao === "alimentar") throw new Error("alimentar numa vida com o mundo: o dono deixa a racao num lugar (deixar_comida)");
    super.aplicarAcaoUsuario(acao);
  }

  /** o dono deixa a comida em (x, y): o evento valida o tipo e a posicao antes do log (MotorMundo.deixar_comida) */
  deixarComida(tipo: string, x: number, y: number): void {
    const mapa = tamanhoDoMapa(this.mundo.cm), ev = eventoDeixarComida(this.estado.tick, tipo, x, y, mapa);
    this.log.push({ tick: ev.tick, tipo: "deixar_comida", valor: ev.valor });
    this.comidaDoDono(...lerDeixarComida(ev, mapa));
  }

  /** o deixar_comida sem o log do laco (o Motor do jogo grava o registro dele): a comida no mundo e o contato do alimentar de hoje
   *  (MotorMundo._aplicar_deixar_comida e MotorEducacao._contato) */
  comidaDoDono(tipo: string, x: number, y: number): void {
    const tick = this.estado.tick;
    const mapa = tamanhoDoMapa(this.mundo.cm);
    lerDeixarComida(eventoDeixarComida(tick, tipo, x, y, mapa), mapa);
    this.conferirSincronia("antes de deixar_comida");
    this.mundo.deixarComida(tick, tipo, x, y);
    this.estado = { ...this.estado, ultimoCuidado: tick, totalCuidados: this.estado.totalCuidados + 1 };
    this.politica.receberAcaoDono("alimentar", tick);
    if (this.decidirNaComida) this.proximaDecisao = Math.min(this.proximaDecisao, tick);
  }

  /** o deixar_bola sem o log do laco (o Motor do jogo grava o registro dele): a bola parada em (x, y). Como no Python
   *  (MotorMundo._aplicar_deixar_bola), nao e contato nem cuidado: nao passa pelo estado nem pelo cerebro */
  bolaDoDono(x: number, y: number): void {
    this.conferirSincronia("antes de deixar_bola");
    this.mundo.deixarBola(this.estado.tick, x, y);
  }

  /** v19 (MotorMundo.levar_pet do Python): o dono solta o pet em (x, y); o evento valida a posicao e o laco o estado (dormindo falha alto)
   *  antes do log */
  levarPet(x: number, y: number): void {
    const ev = eventoLevarPet(this.estado.tick, x, y);
    this.petDoDono(...lerLevarPet(ev));
    this.log.push({ tick: ev.tick, tipo: "levar_pet", valor: ev.valor });
  }

  /** o levar_pet sem o log do laco (o Motor do jogo grava o registro dele): so a posicao do pet muda, limitada ao mapa (PP-1, PP-4). Como o
   *  deixar_bola, nao e contato nem cuidado: nao passa pelo estado, pelo corpo nem pelo cerebro. O pet dormindo nao e pego (PP-2) */
  petDoDono(x: number, y: number): void {
    lerLevarPet(eventoLevarPet(this.estado.tick, x, y));
    if (this.estado.dormindo) throw new Error(`levar_pet com o pet dormindo (tick ${this.estado.tick}): o dono pega o pet acordado`);
    this.conferirSincronia("antes de levar_pet");
    this.mundo.levarPet(this.estado.tick, x, y);
  }

  /** a troca de ilha (docs/TAREFA_V3_ILHA_AGUA.md, IA4; MotorMundo.mudar_ilha do Python): o mundo do pet passa para a ilha com agua
   *  `nome`; o evento valida o nome e o Mundo a troca, antes do log */
  mudarIlha(nome: string): void {
    const ev = eventoMudarIlha(this.estado.tick, nome);
    this.ilhaDoDono(lerMudarIlha(ev));
    this.log.push({ tick: ev.tick, tipo: "mudar_ilha", valor: ev.valor });
  }

  /** o mudar_ilha sem o log do laco (o Motor do jogo grava o registro dele). Como o levar_pet, nao e contato nem cuidado: nao passa pelo
   *  estado, pelo corpo nem pelo cerebro. Vale com o pet acordado ou dormindo */
  ilhaDoDono(nome: string): void {
    lerMudarIlha(eventoMudarIlha(this.estado.tick, nome));
    if (this.tv !== null) throw new TVSemChave("mudar_ilha com a TV ligada: a TV ficaria onde a agua pode chegar (P1c)");
    this.conferirSincronia("antes de mudar_ilha");
    this.mundo.mudarIlha(this.estado.tick, nome);
  }

  /** o sacudir a arvore (TAREFA_V3_ARVORE_SACODE; MotorMundo.sacudir_arvore do Python): o evento valida o id e o mundo a arvore e a
   *  chave, antes do log */
  sacudirArvore(arvore: string): void {
    const ev = eventoSacudirArvore(this.estado.tick, arvore);
    this.sacudirDoDono(lerSacudirArvore(ev));
    this.log.push({ tick: ev.tick, tipo: "sacudir_arvore", valor: ev.valor });
  }

  /** o sacudir_arvore sem o log do laco (o Motor do jogo grava o registro dele). So o mundo muda (AS-1): o galho e a fruta que cai. Nao e
   *  contato nem cuidado: nao passa pelo estado, pelo corpo nem pelo cerebro, como o deixar_bola. Vale com o pet acordado ou dormindo */
  sacudirDoDono(arvore: string): void {
    arvore = lerSacudirArvore(eventoSacudirArvore(this.estado.tick, arvore));
    this.conferirSincronia("antes de sacudir_arvore");
    this.mundo.sacudirArvore(this.estado.tick, arvore);
  }

  override aplicarEvento(e: EventoCorpo): void {
    if (e.tipo === TIPO_TROCAR_CANAL || e.tipo === TIPO_SENTIDO_TELA) {
      if (e.tick !== this.estado.tick) throw new Error(`evento no tick ${e.tick}, o motor esta no ${this.estado.tick}`);
      if (e.tipo === TIPO_TROCAR_CANAL) this.trocarCanal(lerTrocarCanal(e.valor));
      else this.sentidoTela(...lerSentidoTela(e.valor));
      return;
    }
    if (e.tipo === "sacudir_arvore") {
      if (e.tick !== this.estado.tick) throw new Error(`evento no tick ${e.tick}, o motor esta no ${this.estado.tick}`);
      this.sacudirArvore(lerSacudirArvore(e));
      return;
    }
    if (e.tipo === "mudar_ilha") {
      if (e.tick !== this.estado.tick) throw new Error(`evento no tick ${e.tick}, o motor esta no ${this.estado.tick}`);
      this.mudarIlha(lerMudarIlha(e));
      return;
    }
    if (e.tipo === "levar_pet") {
      if (e.tick !== this.estado.tick) throw new Error(`evento no tick ${e.tick}, o motor esta no ${this.estado.tick}`);
      if (typeof e.valor !== "string") throw new Error(`levar_pet malformado: ${JSON.stringify(e)}`);
      this.levarPet(...lerLevarPet({ tick: e.tick, tipo: "levar_pet", valor: e.valor }));
      return;
    }
    if (e.tipo !== "deixar_comida") { super.aplicarEvento(e); return; }
    if (e.tick !== this.estado.tick) throw new Error(`evento no tick ${e.tick}, o motor esta no ${this.estado.tick}`);
    if (typeof e.valor !== "string") throw new Error(`deixar_comida malformado: ${JSON.stringify(e)}`);
    const [tipo, x, y] = lerDeixarComida({ tick: e.tick, tipo: "deixar_comida", valor: e.valor }, tamanhoDoMapa(this.mundo.cm));
    this.deixarComida(tipo, x, y);
  }

  // ------------------------------------------------------------ a decisao (MotorCorpo._decidir com o embrulho do mundo)
  protected override decidir(produzidas: [number, AcaoPet][]): void {
    const intervalo = C.intervalo;
    const base = this.observacao();
    const percepcao = this.antesDaDecisao();
    const obs = this.digibrain ? { ...base, mundo: percepcao } : base;       // a chave do laboratorio: o cerebro ve o mundo (obs.mundo)
    const acao = this.politica.agir(obs, this.rngPolitica);
    this.acaoAtual = acao;
    const e = efeitoAcaoPet(this.estado, acao);
    this.corpo.acaoPet(acao, true);                       // MF-2: com o mundo, o comer so da fome com comida do mapa
    this.estado = this.corpo.noEstado(e);
    this.estimulos = [["pet", acao]];
    this.acoesPet.push([this.estado.tick, acao]);
    produzidas.push([this.estado.tick, acao]);
    this.proximaDecisao = this.estado.tick + intervalo;
    this.sentirAgora();                                   // a TV (P1f): a observacao seguinte do MotorCorpo do Python, antes do mundo
    // o observar do embrulho: a consequencia do mundo antes do cerebro, e a transicao com a observacao de depois dela
    const ocorrido = this.consequencia(acao);
    const seguinte = this.digibrain ? { ...this.observacao(), mundo: this.mundo.perceber(this.estado.tick) } : this.observacao();
    this.politica.observar({ observacao: obs, acao, observacaoSeguinte: seguinte });
    const comeu = ocorrido !== null ? ocorrido.comeu : null;
    if (comeu !== null && FRUTAS_DO_MUNDO.includes(comeu.tipo) && !this.frutaComoComida)
      (this.politica as PoliticaCorpoMundo).frutaComida?.(comeu.tipo, seguinte);   // a E2, so com o gancho (nenhum cerebro do TS o tem)
    if (this.digibrain && ocorrido !== null) (this.politica as PoliticaCorpoMundo).consequenciaMundo?.(acao, ocorrido, seguinte);
    this.conferirEstimulo("decisao", new Set());
    this.sincronizar();
    if (this.tv !== null && this.olhandoTV()) {           // a TV (P1f, GV-21): o assistir, depois dos estimulos da acao
      this.corpo.atividade(ATIVIDADE_TELA);
      this.estimulos.push(["atividade", ATIVIDADE_TELA]);
      const a = this.politica.agradoTela === undefined ? null : this.politica.agradoTela(this.corpo.leiturasTela());   // GV-16
      if (a !== null) {
        this.corpo.estimuloAgradoTela(a);
        this.estimulos.push(["agrado_tela", a]);
        this.sincronizar();
      }
    }
    this.politica.consequenciaCorpo(acao, { acao, estimulos: this.estimulos.map((s) => [...s]) }, this.observacao());
    this.consequencias += 1;
  }

  /** o MotorMundo antes de cada decisao: o mundo anda ate o tick e o pet percebe; o que ele ve ao decidir entra no registro de novidade */
  protected antesDaDecisao(): PercepcaoMundo {
    const t = this.estado.tick;
    const p = this.mundo.antesDaDecisao(t, this.estado.fome);
    if (this.tv !== null && this.politica.verTela !== undefined) this.politica.verTela(this.linhasTela());   // a TV (P1f): as TVs a vista
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
      ...(m.sacudidas !== null ? { sacudir: { no_galho: m.noGalho(t), sacudidas: m.sacudidas.length } } : {}),
      ...(this.tv !== null ? { tv: { programa: this.tv.programaEm(m.tm(t)), ligada: this.tv.em(m.tm(t)) !== null, olhando: this.olhandoTV() },
                               novidades_tela: [...this.novidadesTela] } : {}),
    };
  }
}
