/* O grupo em TS (docs/TAREFA_V3_COOPERACAO.md, etapa CO2c): o porte de digilab/grupo.py, so o motor e a paridade; nenhuma tela e nenhuma
   versao de pet nova. N pets (dois nesta etapa) no mesmo MundoPartilhado (motor/mundo.ts, CO2b), no mesmo relogio, cada um com a parte
   dele do mundo, a semente dele e o cerebro dele. O Grupo nao decide nada: chama cada pet na vez sorteada e grava o registro do grupo.

   - A vez no tick (DP-2): em cada tick em que dois ou mais pets decidem, o fluxo `mundo-ordem` sorteia a ordem sobre a lista ordenada pelo
     id, com o Fisher-Yates do random.shuffle do CPython escrito com randrange (o RandomPy); o primeiro age inteiro (decide, anda, come) e o
     segundo percebe o mundo como ficou. Com um pet so decidindo, nao ha sorteio, e o fluxo nem e criado.
   - As sementes: a do mundo e a do grupo, s; o primeiro pet usa s, o segundo `derivarSemente("segundo-pet", s)`.
   - Os sentidos sobre o outro (etapa 3; degrau 1): a visao e o toque, so do que e fisico. O toque e uma conta do grupo no fim de cada tick
     com decisao: ha contato com as celulas a ate `raio_toque_celulas` em Chebyshev, e o tipo (disputa, encostar, esbarrar) sai do que
     aconteceu no tick. A disputa e a comida que um comeu e o outro tinha como alvo (neste tick, ou o pendente que ele trazia).
   - O registro do grupo (DP-3): o cabecalho e os eventos, no relogio do mundo, cada um com o destino (`grupo`, `mundo`, `pet:<id>`), o pet
     e a origem. O replay (`reproduzirGrupo`) rejoga os eventos e falha alto se o registro refeito diferir do lido.
   - O degrau 1b (o cheiro proprio, o rastro e o som; a ConfigSentidos do Python) fica fora: a cooperacao usa so a visao e o toque
     (secao 6 da tarefa). O registro de um grupo com os sentidos ligados falha alto no replay.

   O engine, o corpo e o cerebro de cada pet ficam fora do grupo, atras da interface `PetDoGrupo`: o pet diz se decide no tick, decide
   (percebendo o mundo pela porta que o grupo da) e recebe o que aconteceu. Os registros usam os nomes em snake_case do Python de
   proposito: sao o mesmo dado, conferido campo a campo (o G-PAR-GRUPO, test/grupo.test.ts). */
import { ACOES_DONO, TPD, type ConfigMundo } from "./constantes.ts";
import type { ConfigContrato } from "./contrato.ts";
import {
  DIR16, Mundo, MundoPartilhado, RandomPy, centroDaCelula, derivarSemente, distancia, eventoDeixarBola, eventoDeixarComida, lerDeixarBola,
  lerDeixarComida, type EscolherAlvo, type OpcoesMundo, type EstadoNoMundo, type GanchoGrupo, type PercepcaoMundo, type PercepcaoSocial, type TickSocial,
} from "./mundo.ts";
import { CONFIG_COOPERACAO, Cooperacao, TIPOS_MADUROS, type ConfigCooperacao, type ConsumoCoop, type Posicoes } from "./cooperacao.ts";
import { CONFIG_TVJOGO, TIPO_SENTIDO_TELA, TV, TVSemChave, conferirConfigTV, lerSentidoTela, type ConfigTV, type ConfigTVJogo } from "./tv.ts";

export const ROTULO_ORDEM = "mundo-ordem";              // o fluxo da vez no tick (DP-2)
export const ROTULO_SEGUNDO_PET = "segundo-pet";        // a semente do segundo pet
export const VERSAO_REGISTRO_GRUPO = 1;
export const DESTINO_GRUPO = "grupo";
export const DESTINO_MUNDO = "mundo";
export const ORIGEM_DONO = "dono";                      // um dono para todos (DP-7)

/** A ConfigGrupo do Python (digilab/config.py; DP-1, DP-7, secao 5.2), conferida pelo test/grupo.test.ts contra o config.py */
export interface ConfigGrupo { ligada: boolean; ids: readonly string[]; orcamento_por_dia: number; raio_toque_celulas: number }
export const CONFIG_GRUPO_LIGADA: Readonly<ConfigGrupo> = Object.freeze({ ligada: true, ids: Object.freeze(["A", "B"]), orcamento_por_dia: 16,
                                                                         raio_toque_celulas: 1 });

export class RegistroDivergente extends Error {}

function validarConfigGrupo(cg: ConfigGrupo): void {
  if (!cg.ligada) throw new Error("o grupo so existe com ConfigGrupo.ligada (sem ela, o Mundo de um pet e dono do proprio mundo)");
  const ids = [...cg.ids];
  if (!ids.length || new Set(ids).size !== ids.length || ids.some(i => typeof i !== "string" || !i))
    throw new Error(`ConfigGrupo.ids precisa de nomes distintos e nao vazios: ${JSON.stringify(ids)}`);
  if (ids.length > 2) throw new Error("ConfigGrupo.ids: so dois pets nesta etapa");
  if (ids.join("\u0000") !== [...ids].sort().join("\u0000")) throw new Error(`ConfigGrupo.ids em ordem: ${JSON.stringify(ids)}`);
  if (!Number.isInteger(cg.orcamento_por_dia) || cg.orcamento_por_dia <= 0) throw new Error("ConfigGrupo.orcamento_por_dia inteiro positivo");
  if (!Number.isInteger(cg.raio_toque_celulas) || cg.raio_toque_celulas < 0) throw new Error("ConfigGrupo.raio_toque_celulas inteiro >= 0");
}

/** o primeiro pet usa a semente do grupo; o segundo, `derivarSemente("segundo-pet", s)` */
export function sementesDoGrupo(semente: number | bigint, ids: readonly string[]): Record<string, number | bigint> {
  if (ids.length > 2) throw new Error("so dois pets nesta etapa");
  const out: Record<string, number | bigint> = { [ids[0]]: semente };
  if (ids.length === 2) out[ids[1]] = derivarSemente(ROTULO_SEGUNDO_PET, semente);
  return out;
}

export const destinoDoPet = (ident: string): string => `pet:${ident}`;

// ================================================================== a conta do toque (digilab/mundo.py, secao 5.2)
export function celulaDe(x: number, y: number, cm: ConfigMundo): [number, number] {
  return [Math.floor(x / cm.sub), Math.floor(y / cm.sub)];
}

/** a direcao de uma celula vizinha na tabela do cheiro (1 a 8 = L, NE, N, NO, O, SO, S, SE; y cresce para o sul), 0 na mesma celula */
export function direcaoVizinha(dcx: number, dcy: number): number {
  if (Math.max(Math.abs(dcx), Math.abs(dcy)) > 1) throw new Error(`celula nao vizinha: (${dcx}, ${dcy})`);
  if (dcx === 0 && dcy === 0) return 0;
  for (let k = 0; k < 8; k++) {
    const [cx, cy] = DIR16[2 * k];
    if (Math.sign(cx) === dcx && Math.sign(cy) === dcy) return k + 1;
  }
  throw new Error("tabela das direcoes incompleta");
}

/** as celulas a no maximo `raio` em Chebyshev */
export function emContato(a: readonly [number, number], b: readonly [number, number], cm: ConfigMundo, raio: number): boolean {
  const [ax, ay] = celulaDe(a[0], a[1], cm), [bx, by] = celulaDe(b[0], b[1], cm);
  return Math.max(Math.abs(ax - bx), Math.abs(ay - by)) <= raio;
}

const comparaStr = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);

/** Pura: o que um pet em (x, y) percebe dos outros agora (o perceber_social do Python). `outros` = (id, x, y, acao visivel); `viuComer` e
    `toques`, a memoria do proprio pet; `tick`, o do mundo */
export function perceberSocial(x: number, y: number, tick: number, outros: [string, number, number, string][],
                               viuComer: ReadonlyMap<string, readonly [number, number, number]>,
                               toques: ReadonlyMap<string, readonly [string, number, number]>, raioVisao: number): PercepcaoSocial {
  const vistos: [string, number, number, number, string][] = [];
  for (const [ident, ox, oy, acao] of outros) {
    const dx = ox - x, dy = oy - y, d = distancia(dx, dy);
    if (d <= raioVisao) vistos.push([ident, dx, dy, d, acao]);
  }
  vistos.sort((p, q) => p[3] - q[3] || comparaStr(p[0], q[0]));
  const ordenado = <T>(m: ReadonlyMap<string, T>) => [...m].sort((p, q) => comparaStr(p[0], q[0]));
  return {
    outros: vistos,
    onde_comeu: ordenado(viuComer).map(([i, [cx, cy, t]]) => [i, cx, cy, tick - t]),
    toque: ordenado(toques).map(([i, [tipo, direcao, t]]) => [i, tipo, direcao, tick - t]),
    sentidos: null,
  };
}

/** o tipo do contato para cada um, pelo que aconteceu no tick (nunca por intencao): a disputa vence o encostar, que vence o esbarrar */
export function tiposDoContato(a: string, b: string, disputa: { vencedor: string; perdedor: string } | null,
                               seguiu: Record<string, string | null>): Record<string, string> {
  if (disputa !== null) return { [disputa.vencedor]: "disputa_ganhou", [disputa.perdedor]: "disputa_perdeu" };
  const tipos: Record<string, string> = {};
  for (const [eu, outro] of [[a, b], [b, a]]) {
    if (seguiu[eu] === outro) tipos[eu] = "encostou";
    else if (seguiu[outro] === eu) tipos[eu] = "encostaram";
    else tipos[eu] = "esbarrou";
  }
  return tipos;
}

// ================================================================== o registro do grupo (DP-3)
export interface EventoGrupo {
  tick: number;
  tipo: "entrada" | "avanco" | "acao_usuario" | "deixar_comida" | "deixar_bola" | "sentido_tela";   // o sentido_tela: so com a TV (D-GV-TVJOGO-4)
  valor: string | number;        // o avanco em ticks; a acao; "tipo|x|y"; "x|y"; na entrada, o id do pet
  destino: string;               // grupo | mundo | pet:<id>
  pet: string | null;            // o pet do evento (a entrada; o do orcamento do dono)
  origem: string | null;         // quem causou (o dono); o avanco e a entrada nao tem origem
}
export interface PetNoCabecalho { semente: number | bigint; entrada: number; cerebro: string; dono: string }
export interface CabecalhoGrupo { versao: number; semente: number | bigint; ids: string[]; layout: string; pets: Record<string, PetNoCabecalho> }

/** o json.dumps(sort_keys=True, separators=(",", ":")) do Python, com o bigint como inteiro e o nao-ASCII escapado (ensure_ascii) */
export function jsonPython(v: unknown): string {
  if (v === null) return "null";
  if (typeof v === "bigint") return v.toString();
  if (typeof v === "number") {
    if (!Number.isInteger(v)) throw new Error(`numero nao inteiro no registro do grupo: ${v}`);
    return String(v);
  }
  if (typeof v === "string") return JSON.stringify(v).replace(/[\u007f-￿]/g, c => `\\u${c.charCodeAt(0).toString(16).padStart(4, "0")}`);
  if (typeof v === "boolean") return v ? "true" : "false";
  if (Array.isArray(v)) return `[${v.map(jsonPython).join(",")}]`;
  if (typeof v === "object") {
    const o = v as Record<string, unknown>;
    return `{${Object.keys(o).sort().map(k => `${jsonPython(k)}:${jsonPython(o[k])}`).join(",")}}`;
  }
  throw new Error(`valor fora do registro do grupo: ${String(v)}`);
}

export class RegistroGrupo {
  readonly cabecalho: CabecalhoGrupo;
  readonly eventos: EventoGrupo[];
  constructor(cabecalho: CabecalhoGrupo, eventos: EventoGrupo[] = []) {
    this.cabecalho = cabecalho;
    this.eventos = [...eventos];
  }

  anexar(e: EventoGrupo): void {
    this.eventos.push(e);
  }

  /** JSONL: a primeira linha e o cabecalho, as outras os eventos (o para_jsonl do Python, byte a byte) */
  paraJsonl(): string {
    return [jsonPython({ cabecalho: this.cabecalho }), ...this.eventos.map(jsonPython)].join("\n") + "\n";
  }

  /** o log de hoje do pet `ident`, no relogio dele: os avancos depois da entrada e os eventos do dono dele, sem o destino */
  projecao(ident: string): { tick: number; tipo: string; valor: string | number }[] {
    const pet = this.cabecalho.pets[ident];
    if (pet === undefined) throw new Error(`pet fora do grupo: ${ident}`);
    const out: { tick: number; tipo: string; valor: string | number }[] = [];
    let dentro = false;
    for (const e of this.eventos) {
      if (e.tipo === "entrada") dentro = dentro || e.valor === ident;
      else if (e.tipo === "avanco") { if (dentro) out.push({ tick: e.tick - pet.entrada, tipo: "avanco", valor: e.valor }); }
      else if (e.pet === ident) out.push({ tick: e.tick - pet.entrada, tipo: e.tipo, valor: e.valor });
    }
    return out;
  }
}

// ================================================================== o pet do grupo (o engine, o corpo e o cerebro, de fora)
/** a porta do mundo numa decisao: `antes(fome)` anda o mundo ate o tick, e o pet percebe o mundo e o outro (o _antes_da_decisao) */
export interface PortaDaDecisao { antes(fome: number): { mundo: PercepcaoMundo; social: PercepcaoSocial | null } }
/** a decisao: a acao, o estado depois do efeito de sempre da acao (o engine), a regra do cerebro e o gancho do alvo */
export interface DecisaoNoGrupo { acao: string; estado: EstadoNoMundo; regra: string | null; escolher?: EscolherAlvo | null }
/** o que aconteceu na decisao, para o pet (o engine e o cerebro) seguir */
export interface ResultadoNoGrupo {
  estado: EstadoNoMundo; ocorrido: Record<string, unknown> | null; candidatos: unknown[] | null; tickSocial: TickSocial | null;
  percepcaoDepois: PercepcaoMundo; tickMundo: number;
}
export interface PetDoGrupo {
  /** o pet decide neste tick dele? (o engine: a proxima decisao) */
  decideEm(tickPet: number): boolean;
  /** a decisao; tem de chamar `porta.antes` uma vez, antes de decidir */
  decidir(tickPet: number, porta: PortaDaDecisao): DecisaoNoGrupo;
  depois?(tickPet: number, r: ResultadoNoGrupo): void;
  /** a acao do dono para este pet (o `observar` do motor); o grupo so a registra */
  observar?(acao: string): void;
}
export interface OpcoesPetNoGrupo {
  efeitoFrutas?: Record<string, number>;
  /** o contrato do pet: no grupo, so o controlador sozinho (a ilha com agua, CONFIG_CONTRATO_AGUA; CO4a) */
  contrato?: ConfigContrato;
  estado?: { ganhoAlimentar: number; probSujeiraPosRefeicao: number; sujeiraMaxima: number; intervalo: number };
  bolaNoGolpe?: boolean;
}

/** O pet do jogo inteiro no grupo (CO4b; o MotorMundo do Python): o Motor anda o proprio tick, usando a parte dele do mundo do grupo, e o
    Grupo so sorteia a vez, como o `_um_tick()` do Python. A acao visivel e a do Motor */
export interface MotorNoGrupo {
  decideNoProximoTick(): boolean;
  umTickNoGrupo(): void;
  readonly acao: string;
  /** o modular do pet, se decide com ele (a CO7 le o `dever` do ultimo motivo) */
  readonly lab?: { motivos: readonly Record<string, unknown>[] } | null;
}

/** as opcoes do grupo: o tick do mundo em que ele comeca (o do nascimento dos pets do jogo; 0 na pesquisa) e a semente do segundo pet (o
    jogo a quer nos 32 bits das sementes dele; a pesquisa, o derivarSemente inteiro) */
export interface OpcoesGrupo {
  tickInicial?: number;
  /** a medida da cooperacao (CO3); desligada por padrao */
  cooperacao?: Readonly<ConfigCooperacao>;
  sementeDoSegundo?: (semente: number | bigint) => number | bigint;
  /** a TV do mundo comum (GOSTO_VISUAL, a decisao B; D-GV-TVJOGO-4; o Grupo(cfg_tv=) do Python): so a fonte "evento"; o Grupo a liga, e
      os pets entram com a opcao `tela` do laco com a mesma ConfigTV. Sem ela, o grupo de hoje */
  tv?: ConfigTV;
  /** a TV no jogo no grupo (a ConfigTVJogo; so com a `tv`): a TV desligada */
  tvJogo?: ConfigTVJogo;
}

/** um membro: o pet do traco (o engine e o cerebro de fora, `pet`) ou o pet do jogo inteiro (`motor`) */
interface Membro { pet: PetDoGrupo | null; motor: MotorNoGrupo | null; mundo: Mundo; acaoAtual: string }

export interface Disputa {
  tick: number; comida: number; tipo: string; situacao: string | null; vencedor: string; perdedor: string;
  vencedor_primeiro: boolean | null; d_vencedor: number; d_perdedor: number; perdedor_decidiu: boolean; contato?: boolean;
}

// ================================================================== o grupo
export class Grupo implements GanchoGrupo {
  readonly cg: Readonly<ConfigGrupo>;
  readonly comum: MundoPartilhado;
  readonly sementes: Record<string, number | bigint>;
  tick = 0;                                                     // o relogio do mundo
  private readonly membros = new Map<string, Membro>();
  private rngOrdem: RandomPy | null = null;                     // so com dois pets decidindo no mesmo tick
  readonly ordens: { tick: number; decidem: string[]; ordem: string[] }[] = [];
  readonly contatos: Record<string, unknown>[] = [];
  readonly disputas: Disputa[] = [];
  /** a CO7 (so com a `co7`): o que os deveres fizeram em cada decisao de um pet do jogo com o modular (o `dever` do motivo), para o gesto na tela;
      derivado, fora do resumo e da assinatura */
  readonly deveres: { tick: number; pet: string; escolha: unknown; dever: Record<string, unknown> }[] = [];
  private readonly motivosVistos = new Map<string, number>();
  readonly registro: RegistroGrupo;
  /** a cooperacao (CO3): so mede; null com a ConfigCooperacao desligada (o grupo de hoje) */
  readonly coop: Cooperacao | null;
  readonly cm: ConfigMundo;
  readonly semente: number | bigint;
  readonly tickInicial: number;

  constructor(cm: ConfigMundo, semente: number | bigint, cg: Readonly<ConfigGrupo> = CONFIG_GRUPO_LIGADA, op: OpcoesGrupo = {}) {
    validarConfigGrupo(cg);
    const cco = op.cooperacao ?? CONFIG_COOPERACAO;
    if (cco.co6 && !cco.ligada) throw new Error("ConfigCooperacao.co6 so liga com a cooperacao ligada (ESPEC_V3_COOPERACAO_CO6, secao 4)");
    if (cco.co7 && !cco.co6) throw new Error("ConfigCooperacao.co7 so liga com a co6 ligada (ESPEC_V3_COOPERACAO_CO7, secao 6)");
    this.coop = cco.ligada ? new Cooperacao(cco) : null;
    this.cm = cm;
    this.semente = semente;
    this.cg = cg;
    const t0 = op.tickInicial ?? 0;
    if (!Number.isInteger(t0) || t0 < 0) throw new Error(`tickInicial inteiro >= 0: ${t0}`);
    this.tickInicial = t0;
    this.tick = t0;
    this.comum = new MundoPartilhado(cm, semente);
    this.sementes = sementesDoGrupo(semente, cg.ids);
    if (op.sementeDoSegundo && cg.ids.length === 2) this.sementes[cg.ids[1]] = op.sementeDoSegundo(semente);
    this.registro = new RegistroGrupo({ versao: VERSAO_REGISTRO_GRUPO, semente, ids: [...cg.ids], layout: cm.layout.nome, pets: {} });
    this.tvJogo = op.tvJogo ?? CONFIG_TVJOGO;
    if (op.tv !== undefined && op.tv.ligada) {           // a TV do mundo comum (D-GV-TVJOGO-4), na celula da ConfigTV (terra; falha alto)
      const ctv = conferirConfigTV(op.tv);
      if (ctv.fonte !== "evento") throw new TVSemChave("a TV no grupo e a do modo livre gravado (a fonte \"evento\")");
      const [cx, cy] = ctv.celula;
      if (!(cx < cm.celulas_x && cy < cm.celulas_y)) throw new Error(`a celula da TV ${ctv.celula} fora do mapa`);
      const [x, y] = centroDaCelula(ctv.celula, cm);
      if (!this.comum.seca(x, y)) throw new Error(`a celula da TV ${ctv.celula} e agua`);
      this.comum.tv = new TV(ctv, semente, x, y);
      (this.registro.cabecalho as unknown as Record<string, unknown>)["tv"] = { ...ctv, celula: [...ctv.celula] };
      if (this.tvJogo.desligar || this.tvJogo.ir_ate_tv) (this.registro.cabecalho as unknown as Record<string, unknown>)["tv_jogo"] = { ...this.tvJogo };
    } else if (op.tvJogo !== undefined && (op.tvJogo.desligar || op.tvJogo.ir_ate_tv)) {
      throw new TVSemChave("a ConfigTVJogo no grupo exige a TV ligada");
    }
  }
  /** a TV no jogo no grupo (a ConfigTVJogo) */
  readonly tvJogo: ConfigTVJogo;

  /** o que a TV do mundo comum passa a partir de agora (o modo livre gravado; o valor do `sentido_tela`, `fonte|n1|...|n7` ou, com a
      ConfigTVJogo.desligar, `fonte|desligada`): um evento do grupo, do mundo, sem pet. Valida antes do registro */
  sentidoTela(valor: string): void {
    const tv = this.comum.tv;
    if (tv === null) throw new TVSemChave("o sentido_tela no grupo exige a TV do mundo comum (a opcao `tv`)");
    const [fonte, niveis] = lerSentidoTela(valor);
    if (niveis === null && !this.tvJogo.desligar) throw new TVSemChave("a TV desligada exige a ConfigTVJogo.desligar");
    this.registro.anexar({ tick: this.tick, tipo: TIPO_SENTIDO_TELA, valor, destino: DESTINO_MUNDO, pet: null, origem: ORIGEM_DONO });
    tv.sentir(fonte, niveis, this.tick);
  }

  // ------------------------------------------------------------ a entrada
  /** o pet `ident` entra agora (um inicio de dia do mundo), com a semente dele; `cerebro` e `dono` sao os rotulos do cabecalho */
  entrar(ident: string, pet: PetDoGrupo, cerebro: string, dono: string, op: OpcoesPetNoGrupo = {}): Mundo {
    if (!this.cg.ids.includes(ident)) throw new Error(`pet fora do grupo: ${ident} (ids ${this.cg.ids})`);
    if (this.membros.has(ident)) throw new Error(`o pet ${ident} ja entrou`);
    this.conferirEntrada(ident);
    const mundo = new Mundo({ semente: this.sementes[ident], cfg: this.cm, partilhado: this.comum, entrada: this.tick - this.tickInicial, ...op });
    this.registrarEntrada(ident, { pet, motor: null, mundo, acaoAtual: "ocioso" }, cerebro, dono);
    return mundo;
  }

  /** O pet do jogo inteiro entra agora (CO4b): `criar` monta o Motor e lhe da a funcao `parte`, que o laco dele chama uma vez para montar a
      parte dele no mundo do grupo, com a semente dele. `tickDoPet` e o relogio do pet na entrada (o do nascimento): o do mundo menos ele e a
      entrada (um multiplo do dia; com os dois nascendo juntos, 0) */
  entrarMotor(ident: string, tickDoPet: number, criar: (parte: (op: OpcoesMundo) => Mundo) => MotorNoGrupo, cerebro: string,
              dono: string): MotorNoGrupo {
    this.conferirEntrada(ident);
    let mundo: Mundo | null = null;
    const parte = (op: OpcoesMundo): Mundo => {
      if (mundo !== null) throw new Error(`a parte do pet ${ident} no mundo do grupo ja foi montada`);
      if (op.semente !== this.sementes[ident]) throw new Error(`o pet ${ident} tem de nascer com a semente do grupo: ${op.semente} x ${this.sementes[ident]}`);
      if (op.cfg !== undefined && JSON.stringify(op.cfg) !== JSON.stringify(this.cm)) throw new Error(`o pet ${ident} quer outro mundo que o do grupo`);
      mundo = new Mundo({ ...op, cfg: this.cm, partilhado: this.comum, entrada: this.tick - tickDoPet });
      return mundo;
    };
    const motor = criar(parte);
    const feito = mundo as Mundo | null;
    if (feito === null) throw new Error(`o pet ${ident} nasceu sem a parte dele no mundo do grupo`);
    this.registrarEntrada(ident, { pet: null, motor, mundo: feito, acaoAtual: motor.acao }, cerebro, dono);
    return motor;
  }

  private conferirEntrada(ident: string): void {
    if (!this.cg.ids.includes(ident)) throw new Error(`pet fora do grupo: ${ident} (ids ${this.cg.ids})`);
    if (this.membros.has(ident)) throw new Error(`o pet ${ident} ja entrou`);
    if ((this.tick - this.tickInicial) % TPD) throw new Error(`o pet entra num inicio de dia do mundo: tick ${this.tick}`);
  }

  private registrarEntrada(ident: string, mb: Membro, cerebro: string, dono: string): void {
    for (const outro of this.membros.values())                  // o efeito de cada fruta e do mundo: o mesmo para todos
      if (JSON.stringify(outro.mundo.efeitoFrutas) !== JSON.stringify(mb.mundo.efeitoFrutas))
        throw new Error(`efeitoFrutas diferente entre os pets: ${JSON.stringify(outro.mundo.efeitoFrutas)} x ${JSON.stringify(mb.mundo.efeitoFrutas)}`);
    mb.mundo.ligarGrupo(this, ident);
    this.membros.set(ident, mb);
    this.registro.cabecalho.pets[ident] = { semente: this.sementes[ident], entrada: mb.mundo.entrada, cerebro, dono };
    this.registro.anexar({ tick: this.tick, tipo: "entrada", valor: ident, destino: DESTINO_GRUPO, pet: ident, origem: null });
  }

  idsPresentes(): string[] {
    return this.cg.ids.filter(i => this.membros.has(i));
  }

  mundoDe(ident: string): Mundo {
    const m = this.membros.get(ident);
    if (m === undefined) throw new Error(`o pet ${ident} nao entrou`);
    return m.mundo;
  }

  private membro(ident: string): Membro {
    const m = this.membros.get(ident);
    if (m === undefined) throw new Error(`o pet ${ident} nao entrou`);
    return m;
  }

  // ------------------------------------------------------------ o tempo
  /** um avanco do grupo (um evento so): os ticks andam intercalados, e em cada um os pets que decidem agem na vez sorteada */
  avancar(ticks: number): void {
    if (!Number.isInteger(ticks) || ticks <= 0) throw new Error(`avanco precisa de ticks inteiros positivos: ${ticks}`);
    this.registro.anexar({ tick: this.tick, tipo: "avanco", valor: ticks, destino: DESTINO_GRUPO, pet: null, origem: null });
    const presentes = this.idsPresentes();
    for (let k = 0; k < ticks; k++) {
      const decidem = presentes.filter(i => {
        const mb = this.membro(i);
        return mb.motor !== null ? mb.motor.decideNoProximoTick() : mb.pet!.decideEm(this.tick - mb.mundo.entrada);
      });
      const ordem = decidem.length >= 2 ? this.sortear(decidem) : decidem;
      const nContatos = this.contatos.length, nDisputas = this.disputas.length;
      /* a vez sorteada primeiro, depois os que nao decidem (o `ordem + os outros` do Python); o pet do traco que nao decide nao tem tick. A
         medida (CO3) le cada um logo depois da decisao dele, o pet do traco ou o pet do jogo (CO5) */
      for (const i of ordem) {
        const mb = this.membro(i);
        if (mb.motor !== null) mb.motor.umTickNoGrupo(); else this.decidirUm(i);
        if (this.coop !== null && this.coop.cfg.co7 && mb.motor !== null) this.lerDever(i, mb.motor.lab ?? null);
        if (this.coop !== null) this.coopDecisao(i, presentes);
      }
      for (const i of presentes) {
        const mb = this.membro(i);
        if (mb.motor !== null && !decidem.includes(i)) mb.motor.umTickNoGrupo();
      }
      if (decidem.length && presentes.length >= 2) this.toqueEDisputa(presentes, ordem);
      if (this.coop !== null && decidem.length) {
        const [pos, raios] = this.posicoesERaios(presentes);
        this.coop.fimDoTick(this.tick, this.disputas.slice(nDisputas), this.contatos.slice(nContatos) as { pets: unknown; tipos: Record<string, string> }[],
                            Object.fromEntries(presentes.map(i => [i, this.acaoVisivel(i)])), pos, raios);
      }
      if (this.coop !== null && this.coop.cfg.co6) {     // a CO6: o peso dos deveres no fim de todo tick; a idade e o tick do pet depois deste
        const [pos, raios] = this.posicoesERaios(presentes);
        this.coop.fimDoTickK(this.tick, pos, raios, Object.fromEntries(presentes.map(i => [i, this.tick + 1 - this.membro(i).mundo.entrada])));
      }
      this.tick++;
    }
  }

  /** a CO7: o `dever` da decisao que o pet do jogo acabou de tomar com o modular (nada sem ele) */
  private lerDever(ident: string, lab: { motivos: readonly Record<string, unknown>[] } | null): void {
    if (lab === null) return;
    const n = lab.motivos.length, visto = this.motivosVistos.get(ident) ?? 0;
    this.motivosVistos.set(ident, n);
    if (n === visto) return;
    const m = lab.motivos[n - 1]!, d = m["dever"] as Record<string, unknown> | null | undefined;
    if (d !== null && d !== undefined) this.deveres.push({ tick: this.tick, pet: ident, escolha: m["escolha"], dever: d });
  }

  /** a acao que se ve de fora: a do Motor (o pet do jogo) ou a ultima decidida (o pet do traco) */
  private acaoVisivel(ident: string): string {
    const o = this.membro(ident);
    return o.motor !== null ? o.motor.acao : o.acaoAtual;
  }

  // ------------------------------------------------------------ a cooperacao (CO3): o que a medida le, sem mudar nada
  private posicoesERaios(presentes: readonly string[]): [Posicoes, Record<string, number>] {
    const pos: Posicoes = {}, raios: Record<string, number> = {};
    for (const i of presentes) { const m = this.membro(i).mundo; pos[i] = [m.pet[0], m.pet[1]]; raios[i] = m.raioDaVisao; }
    return [pos, raios];
  }

  /** o pet `ident` acabou de decidir: o que ele via (as comidas maduras e os outros), a fome com que decidiu e o que comeu */
  private coopDecisao(ident: string, presentes: readonly string[]): void {
    const m = this.membro(ident).mundo, ts = this.noTick(m), p = m.percepcaoDaDecisao;
    if (ts === null || p === null) throw new Error(`o pet ${ident} decidiu no tick ${this.tick} sem o registro social da decisao`);
    const maduras = p.vistos.filter(v => TIPOS_MADUROS.includes(v[1])).map(v => v[0]);
    const outros = m.social === null ? [] : m.social.outros.map(o => o[0]);
    let consumo: ConsumoCoop | null = null;
    if (ts.comeu !== null) {
      consumo = m.consumos.at(-1) as unknown as ConsumoCoop;
      if (consumo.id !== ts.comeu.id) throw new Error(`o consumo do pet ${ident} nao e o da decisao`);
    }
    this.coop!.decisao(this.tick, ident, maduras, outros, m.fomeDaDecisao, consumo, ...this.posicoesERaios(presentes));
  }

  /** DP-2: um sorteio por tick com dois ou mais pets decidindo, no fluxo `mundo-ordem`, sobre a lista ordenada pelo id */
  private sortear(decidem: string[]): string[] {
    if (this.rngOrdem === null) this.rngOrdem = new RandomPy(derivarSemente(ROTULO_ORDEM, this.semente));
    const ordem = [...decidem];
    for (let k = ordem.length - 1; k > 0; k--) {
      const j = this.rngOrdem.randrange(k + 1);
      [ordem[k], ordem[j]] = [ordem[j], ordem[k]];
    }
    this.ordens.push({ tick: this.tick, decidem: [...decidem], ordem: [...ordem] });
    return ordem;
  }

  private decidirUm(ident: string): void {
    const mb = this.membro(ident), m = mb.mundo, t = this.tick - m.entrada;
    let percebeu = false;
    const porta: PortaDaDecisao = {
      antes: (fome: number) => {
        if (percebeu) throw new Error(`o pet ${ident} percebeu duas vezes na mesma decisao`);
        percebeu = true;
        const mundo = m.antesDaDecisao(t, fome);
        return { mundo, social: m.social };
      },
    };
    const d = mb.pet!.decidir(t, porta);
    if (!percebeu) throw new Error(`o pet ${ident} decidiu sem perceber (porta.antes)`);
    mb.acaoAtual = d.acao;                                       // a acao que se ve de fora
    const r = m.consequencia(t, d.acao, d.estado, d.escolher ?? null, d.regra);
    mb.pet!.depois?.(t, { ...r, candidatos: m.ultimosCandidatos, tickSocial: m.tickSocial, percepcaoDepois: m.perceber(t), tickMundo: this.tick });
  }

  // ------------------------------------------------------------ os sentidos sobre o outro (GanchoGrupo)
  /** a visao e o toque do pet `ident` agora, so do que e fisico; null com o pet sozinho no grupo */
  perceberSocial(ident: string): PercepcaoSocial | null {
    const outros = this.idsPresentes().filter(i => i !== ident);
    if (!outros.length) return null;
    const m = this.membro(ident).mundo;
    const fisico = outros.map((i): [string, number, number, string] => {
      const o = this.membro(i);
      return [i, o.mundo.pet[0], o.mundo.pet[1], this.acaoVisivel(i)];
    });
    const p = perceberSocial(m.pet[0], m.pet[1], this.tick, fisico, m.viuComerDe, m.toques, m.raioDaVisao);
    if (this.coop !== null && this.coop.cfg.co6) {        // a CO6: a reputacao de cada outro presente e o proprio k (sem ela, nenhum campo)
      p.reputacao = [...outros].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0)).map((i): [string, number] => [i, this.coop!.reputacao(i, ident, this.tick)]);
      p.peso_dever = this.coop.pesoDever(ident);
    }
    return p;
  }

  /** o pet `quem` comeu a comida de (x, y) agora: cada outro que o tem a vista guarda o ponto */
  viuComer(quem: string, x: number, y: number): void {
    const mq = this.membro(quem).mundo;
    for (const i of this.idsPresentes()) {
      if (i === quem) continue;
      const m = this.membro(i).mundo;
      const d = distancia(mq.pet[0] - m.pet[0], mq.pet[1] - m.pet[1]);
      if (d <= m.raioDaVisao) {
        m.viuComerDe.set(quem, [x, y, this.tick]);
        m.vistosComer.push({ tick: this.tick, outro: quem, x, y, d });
      }
    }
  }

  private noTick(m: Mundo): TickSocial | null {
    const ts = m.tickSocial;
    return ts !== null && ts.tick === this.tick ? ts : null;
  }

  /** o fim de um tick com decisao: por par, a disputa (registrada com ou sem contato) e o contato com o tipo de cada um */
  private toqueEDisputa(presentes: string[], ordem: string[]): void {
    const cm = this.cm;
    for (let k = 0; k < presentes.length; k++) {
      for (const b of presentes.slice(k + 1)) {
        const a = presentes[k];
        const ma = this.membro(a).mundo, mb = this.membro(b).mundo;
        const disputa = this.disputa(a, b) ?? this.disputa(b, a);
        const contato = emContato(ma.pet, mb.pet, cm, this.cg.raio_toque_celulas);
        if (disputa !== null) {
          disputa.contato = contato;
          this.disputas.push(disputa);
        }
        if (!contato) continue;
        const seguiu = { [a]: this.seguiu(ma), [b]: this.seguiu(mb) };
        const tipos = tiposDoContato(a, b, disputa, seguiu);
        const [ax, ay] = celulaDe(ma.pet[0], ma.pet[1], cm), [bx, by] = celulaDe(mb.pet[0], mb.pet[1], cm);
        const direcoes = { [a]: direcaoVizinha(Math.sign(bx - ax), Math.sign(by - ay)), [b]: direcaoVizinha(Math.sign(ax - bx), Math.sign(ay - by)) };
        for (const [eu, outro] of [[a, b], [b, a]]) this.membro(eu).mundo.toques.set(outro, [tipos[eu], direcoes[eu], this.tick]);
        this.contatos.push({ tick: this.tick, pets: [a, b], tipos, direcoes, celulas: { [a]: [ax, ay], [b]: [bx, by] }, decidem: [...ordem] });
      }
    }
  }

  /** o id do pet que `m` seguiu neste tick (o candidato `seguir`, ou o continuar dele), ou null */
  private seguiu(m: Mundo): string | null {
    const ts = this.noTick(m);
    if (ts === null || ts.alvo === null) return null;
    const classe = ts.alvo.tipo === "continuar" ? ts.alvo.de : ts.alvo.tipo;
    return classe === "seguir" ? ts.social : null;
  }

  /** o `vencedor` comeu neste tick a comida que o `perdedor` tinha como alvo neste tick, ou trazia como alvo pendente */
  private disputa(vencedor: string, perdedor: string): Disputa | null {
    const mv = this.membro(vencedor).mundo, mp = this.membro(perdedor).mundo;
    const tv = this.noTick(mv);
    if (tv === null || tv.comeu === null) return null;
    const c = tv.comeu;
    const tp = this.noTick(mp);
    const alvos = [];
    if (tp !== null) {
      alvos.push(tp.alvo);
      if (tp.pendente_antes !== null) alvos.push(tp.pendente_antes.alvo);
    } else if (mp.pendenteAtual !== null) {
      alvos.push(mp.pendenteAtual.alvo);
    }
    const daComida = (a: { tipo: string; de: string | null; id: number | null } | null) =>
      a !== null && (a.tipo === "continuar" ? a.de : a.tipo) === "comida" && a.id === c.id;
    if (!alvos.some(daComida)) return null;
    const deV = tv.de, deP = tp !== null ? tp.de : mp.pet;
    const ultima = this.ordens.at(-1);
    const vez = ultima !== undefined && ultima.tick === this.tick ? ultima.ordem : null;
    return {
      tick: this.tick, comida: c.id, tipo: c.tipo, situacao: c.situacao, vencedor, perdedor,
      vencedor_primeiro: vez === null ? null : vez.indexOf(vencedor) < vez.indexOf(perdedor),
      d_vencedor: distancia(c.x - deV[0], c.y - deV[1]), d_perdedor: distancia(c.x - deP[0], c.y - deP[1]), perdedor_decidiu: tp !== null,
    };
  }

  /** o dono do pet do jogo age pelo Motor dele (o GrupoDoJogo grava o registro); o registro do Grupo so tem a entrada e o avanco */
  private semMotor(mb: Membro, ident: string): void {
    if (mb.motor !== null) throw new Error(`o dono do pet ${ident} do jogo age pelo Motor dele (o GrupoDoJogo), nao pelo Grupo`);
  }

  // ------------------------------------------------------------ o dono (DP-7: o orcamento e o contato sao de um pet)
  acaoDono(ident: string, acao: string): void {
    const mb = this.membro(ident);
    this.semMotor(mb, ident);
    if (!(ACOES_DONO as readonly string[]).includes(acao)) throw new Error(`acao do dono desconhecida no grupo: ${acao}`);
    this.registro.anexar({ tick: this.tick, tipo: "acao_usuario", valor: acao, destino: destinoDoPet(ident), pet: ident, origem: ORIGEM_DONO });
    mb.pet!.observar?.(acao);
  }

  deixarComida(ident: string, tipo: string, x: number, y: number): void {
    this.semMotor(this.membro(ident), ident);
    const m = this.membro(ident).mundo;
    const ev = eventoDeixarComida(this.tick, tipo, x, y);       // valida antes do registro
    this.registro.anexar({ tick: this.tick, tipo: "deixar_comida", valor: ev.valor, destino: DESTINO_MUNDO, pet: ident, origem: ORIGEM_DONO });
    m.deixarComida(this.tick - m.entrada, tipo, x, y);
  }

  deixarBola(ident: string, x: number, y: number): void {
    this.semMotor(this.membro(ident), ident);
    const m = this.membro(ident).mundo;
    const ev = eventoDeixarBola(this.tick, x, y);
    this.registro.anexar({ tick: this.tick, tipo: "deixar_bola", valor: ev.valor, destino: DESTINO_MUNDO, pet: ident, origem: ORIGEM_DONO });
    m.deixarBola(this.tick - m.entrada, x, y);
  }

  // ------------------------------------------------------------ leitura
  /** o resumo do Grupo do Python, sem as rngs e sem o que e do engine e do cerebro (o estado, o log, a politica) */
  resumo(): Record<string, unknown> {
    return {
      tick: this.tick, mundo: this.comum.resumo(), ordens: this.ordens, contatos: this.contatos, disputas: this.disputas,
      pets: Object.fromEntries([...this.membros].map(([i, mb]) => [i, { fisico: mb.mundo.resumo(), social: mb.mundo.resumoSocial(), entrada: mb.mundo.entrada }])),
      ...(this.coop !== null ? { cooperacao: this.coop.resumo(this.idsPresentes(), this.tick) } : {}),
    };
  }
}

// ================================================================== o replay
/** Refaz o grupo do cabecalho e rejoga os eventos no mesmo relogio. `pets[id]` monta o pet (o engine e o cerebro) e as opcoes da parte dele
    do mundo. O registro refeito tem de ser o lido (falha alto); evento desconhecido, fora do tick ou de pet que nao entrou tambem. */
export function reproduzirGrupo(registro: RegistroGrupo, pets: Record<string, () => { pet: PetDoGrupo; opcoes?: OpcoesPetNoGrupo }>,
                                cm: ConfigMundo, cg: Readonly<ConfigGrupo> = CONFIG_GRUPO_LIGADA,
                                cco: Readonly<ConfigCooperacao> = CONFIG_COOPERACAO, tv: { tv?: ConfigTV; tvJogo?: ConfigTVJogo } = {}): Grupo {
  const cab = registro.cabecalho as CabecalhoGrupo & { sentidos?: unknown };
  if (cab.versao !== VERSAO_REGISTRO_GRUPO) throw new Error(`versao do registro do grupo desconhecida: ${String(cab.versao)}`);
  if (cab.ids.join("\u0000") !== cg.ids.join("\u0000") || cab.layout !== cm.layout.nome)
    throw new Error("o cabecalho do registro nao e o desta ConfigGrupo/ConfigMundo");
  if (cab.sentidos !== undefined && cab.sentidos !== null) throw new Error("o registro tem os sentidos do degrau 1b, fora do grupo em TS");
  if (Object.keys(pets).sort().join() !== Object.keys(cab.pets).sort().join())
    throw new Error(`pets ${Object.keys(pets).sort()} para o cabecalho ${Object.keys(cab.pets).sort()}`);
  const g = new Grupo(cm, cab.semente, cg, { cooperacao: cco, ...tv });
  for (const e of registro.eventos) {
    if (e.tick !== g.tick) throw new Error(`evento no tick ${e.tick} com o grupo no tick ${g.tick}: ${jsonPython(e)}`);
    if (e.tipo === "entrada") {
      const p = cab.pets[e.valor as string];
      if (p === undefined) throw new Error(`entrada de pet fora do cabecalho: ${String(e.valor)}`);
      const { pet, opcoes } = pets[e.valor as string]();
      g.entrar(e.valor as string, pet, p.cerebro, p.dono, opcoes);
    } else if (e.tipo === "avanco") {
      g.avancar(e.valor as number);
    } else if (e.tipo === "acao_usuario") {
      g.acaoDono(e.pet!, e.valor as string);
    } else if (e.tipo === "deixar_comida") {
      const [tipo, x, y] = lerDeixarComida({ tick: e.tick, tipo: "deixar_comida", valor: String(e.valor) });
      g.deixarComida(e.pet!, tipo, x, y);
    } else if (e.tipo === "deixar_bola") {
      const [x, y] = lerDeixarBola({ tick: e.tick, tipo: "deixar_bola", valor: String(e.valor) });
      g.deixarBola(e.pet!, x, y);
    } else if (e.tipo === TIPO_SENTIDO_TELA && e.destino === DESTINO_MUNDO && e.pet === null) {
      g.sentidoTela(String(e.valor));                     // a TV do mundo comum (D-GV-TVJOGO-4)
    } else {
      throw new Error(`tipo de evento desconhecido no registro do grupo: ${String((e as { tipo: unknown }).tipo)}`);
    }
  }
  if (g.registro.paraJsonl() !== registro.paraJsonl()) throw new RegistroDivergente("o replay refez um registro do grupo diferente do lido");
  return g;
}
