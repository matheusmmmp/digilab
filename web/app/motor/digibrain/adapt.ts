/* M-ADAPT, o adaptador cerebro-corpo-motor: o espelho de digilab/digibrain/adapt.py (docs/TAREFA_V3_LAB_MODULAR.md, LM4). O DigiBrain modular sob a
   interface `PoliticaCorpo` do laco, com os ganchos que o laco com o mundo procura no cerebro (`escolherAlvo`, `consequenciaMundo`,
   `consequenciaCorpo`, `receberAcaoDono`). Nenhuma conta propria: encaminha a Observacao aos modulos, a rng de politica so ao M-ARB e a
   consequencia ao M-AFETO, ao M-PLAST, ao M-ESTADO e ao M-MEM.

   A decisao (`agir`): M-SENS -> M-AFETO -> M-ESTADO (o contexto) -> M-MEM (o relogio, a consolidacao, a lembranca, a recuperacao) -> M-IMPULSO
   (as unidades) -> M-ARB (a escolha, o u e as sondas) -> M-ESTADO (a intencao escolhida). A decisao guarda tudo numa pendencia e so a fecha no
   comeco da seguinte. A ordem dos ganchos no laco com o mundo e o corpo: `agir`, `escolherAlvo`, `observar`, `consequenciaMundo` (so nas acoes
   com alvo) e `consequenciaCorpo`.

   Fora do laboratorio (LAB-1; os modulos falham alto se vierem ligados): `facetas_mem` (o M-PERS), `redecidir_evento` (C3), `credito_corrida`
   (C2), `intencao_suspensa` (L-2) e os controles. A rng do EMB nao entra (so o REL e aceito). A rng de politica e a do motor
   (`semente + 1_000_003`), passada ao `agir` e entregue so ao M-ARB. Aritmetica so inteira.

   A subchave `fala_unidades` (DC3d; docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1 e o adendo 1, A1.1): o M-IMPULSO divide o `chamar_atencao` nas
   tres unidades de fala (o conteudo so na chave da escolha, [chamar_atencao, c, null]); a acao entregue ao motor e o chamar de hoje, e a
   opcao de fala credita a linha de H do conteudo. A consequencia da opcao de fala le o corpo de depois na percepcao da decisao seguinte (o
   `obs` do `agir` seguinte, antes da acao seguinte); o mundo de depois e o de hoje. Desligada (todo pet de hoje), nada muda.

   A subchave `olhar` (GOSTO_VISUAL, P1f; o porte da P1d do Python, docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 5 e 6): o genoma da visao do ovo
   (`genomaVisao(semente)`, rng propria `visao-ovo`, ou o dado), a classe `tela` do M-SENS, a unidade de olhar no fim da lista (entregue ao
   motor como o ocioso, sem alvo), o termo `gosto`, o canal `gosto_visual` no r, a exposicao e o P1 da classe `tela`, e os tres ganchos que o
   laco com a TV procura: `verTela`, `olhandoTela` e `agradoTela`. Desligada, nenhum campo, estado nem gancho que funcione (os tres falham
   alto). O gabarito e o test/gabaritos/gosto_visual.json.gz (experiments/exportar_gosto_visual.py).

   O lance do dono (TAREFA_V3_BOLA_BRINCAR, BB2; o porte da BB1 do Python): com a ConfigLanceDono ligada, o laco entrega o convite antes de cada
   decisao pelo gancho `bolaDoDono(bool)` (o tick esta na janela do lance?), e o M-IMPULSO recebe a entrada `bola_do_dono` (S no convite, 0 fora
   dele e 0 com a fome urgente); o motivo ganha `lance`. Com a chave e sem o gancho antes da decisao, falha alto; o gancho sem a chave tambem.
   Desligada, nenhum campo novo. O gabarito e o test/gabaritos/digibrain_modular_lance_dono.json.gz. */
import { leituraReceptor, type PercepcaoCorpoLobos } from "../lobos.ts";
import type { OcorridoMundo, PoliticaCorpoMundo } from "../motor_corpo_mundo.ts";
import type { OcorridoCorpo, ObservacaoLobos, TransicaoLobos } from "../lobos.ts";
import { alvoPonto, type AlvoMundo, type PercepcaoMundo } from "../mundo.ts";
import type { AcaoPet } from "../tipos.ts";
import { chaveJson, ganhoDeTau, integrar, mul, raizInteira, type ChaveUnidade } from "./_comum.ts";
import { conferirConfigEnjooTela, type ConfigEnjooTela } from "../enjoo_tela.ts";
import { genomaVisao, type GenomaVisao } from "./genoma_visao.ts";
import { Afeto } from "./afeto.ts";
import { Arbitragem, type RngPolitica } from "./arb.ts";
import { COMPORTAMENTO_OLHAR, CONFIG_DIGIBRAIN_LAB, CONFIG_EQUILIBRIO_CUIDADO, CONFIG_LANCE_DONO, CONFIG_MODULAR_MUNDO, CONFIG_OLHAR, CONFIG_SONO_SEGURA,
  CONTEUDOS_FALA, INATOS_MODULAR, equilibrioLigado, validarEquilibrioCuidado, validarLanceDono, type ConfigDigibrainModular,
  type ConfigEquilibrioCuidado, type ConfigLanceDono, type ConfigOlhar, type ConfigSonoSegura } from "./constantes.ts";
import { EstadoDinamico, type OpcaoFim } from "./estado.ts";
import { Impulso, type UnidadeImpulso } from "./impulso.ts";
import { Memoria, episodioAutobio, episodioLuta } from "./mem.ts";
import { Plasticidade, type OpcaoCredito } from "./plast.ts";
import { COMIDAS_BOAS, Sens, classeDoTipo, type ObservacaoModular, type ResumoLutaSens, type SocialSens } from "./sens.ts";
import type { ConfigCooperacao } from "../cooperacao.ts";

/** o `VERSAO_PET_DIGIBRAIN` do Python (a DM-5); o pet de teste do jogo tem a versao propria (VERSAO_PET_LAB, motor/constantes.ts) */
export const VERSAO_PET_DIGIBRAIN = 13;

type Dict = Record<string, any>;
/** a Observacao do laco com o mundo: o corpo (os receptores) e o mundo (a percepcao) */
export type ObservacaoMundoLobos = ObservacaoLobos & { mundo?: PercepcaoMundo; social?: SocialSens | null };

/** a escolha do M-ARB vista pelo motor: a acao e, nas acoes com alvo, o tipo do candidato do motor, o id dele e, no lugar lembrado, o ponto */
export interface Intencao { acao: AcaoPet; tipo_alvo: string | null; id_alvo: number | null; ponto: readonly [number, number] | null }

export function intencaoDaUnidade(unidade: UnidadeImpulso): Intencao {
  const [acao, tipo, ident] = unidade.chave;
  /* o olhar (P1f): o motor o executa como o ocioso, parado e sem alvo (D-GV-P1d-1) */
  if (acao === COMPORTAMENTO_OLHAR) return { acao: "ocioso", tipo_alvo: null, id_alvo: null, ponto: null };
  if (tipo === "ponto") return { acao: acao as AcaoPet, tipo_alvo: "ponto", id_alvo: null, ponto: ident as readonly [number, number] };
  /* a unidade de fala (DC3, 3.1): o conteudo fica so na chave; o mundo e o do chamar */
  if (acao === "chamar_atencao") return { acao: acao as AcaoPet, tipo_alvo: null, id_alvo: null, ponto: null };
  return { acao: acao as AcaoPet, tipo_alvo: tipo, id_alvo: tipo === "comida" || tipo === "bola" ? (ident as number) : null, ponto: null };
}

export class DigibrainDesligado extends Error {}
/** o olhar no DigiBrain (P1f): o genoma dado (o vazio do controle) ou a semente do ovo, e a ConfigOlhar; so com a subchave `olhar` */
export interface OpcoesOlhar { semente?: number; genoma?: GenomaVisao; cfgOlhar?: ConfigOlhar; cfgEnjooTela?: ConfigEnjooTela;   // D-GV-ENJOO-CER
  irAteTv?: boolean }   // D-GV-TVJOGO-3
/** a ponte da luta sem a chave ligada (o `LutaSemChave` do Python) */
export class LutaSemChave extends Error {}

const ACOES_COM_ALVO: readonly string[] = ["explorar", "comer", "brincar"];

/** a configuracao do laboratorio como o M-ADAPT a recebe (a ConfigDigibrain do braco REL, com a `fala_unidades` ligada ou nao) */
export type ConfigLab = ConfigDigibrainModular;

export interface Pendencia {
  k: number; intencao: Intencao; unidade: UnidadeImpulso; sens: Dict; g_apr: number; pediu: boolean; alvo: AlvoMundo | null;
  corpo: [OcorridoCorpo, ObservacaoLobos] | null; transicao: TransicaoLobos | null; mundo: [OcorridoMundo, ObservacaoLobos] | null;
  tick: number; afeto: { V: number; E: number }; gestos: [string, number][];
}

export class DigiBrain implements PoliticaCorpoMundo {
  readonly nome = "digibrain";
  readonly versao_pet = VERSAO_PET_DIGIBRAIN;
  readonly cd: ConfigLab;
  inatos: typeof INATOS_MODULAR;                              // muda so no alcance da memoria (alcanceDaMemoria)
  readonly S: number;
  readonly sens: Sens;
  readonly afeto: Afeto;
  readonly estado: EstadoDinamico;
  readonly impulso: Impulso;
  readonly mem: Memoria;
  readonly arb: Arbitragem;
  readonly plast: Plasticidade;
  k = 0;
  readonly motivos: Dict[] = [];
  private pendencia: Pendencia | null = null;
  private gestosAgora: [string, number][] = [];
  private readonly gestos: Record<string, number> = {};
  /** a ponte da luta (PE3; a `ConfigLutaMemoria` do Python): desligada, o DigiBrain nao ganha campo, estado nem gancho novo */
  lutaMemoria: boolean;
  private lutas: ResumoLutaSens[] = [];                  // os resumos desde a decisao anterior (so com a luta_memoria)
  private pcAntesLuta: Dict | null = null;               // o corpo da ultima consequencia fechada (so com a luta_memoria)
  /** o olhar (P1f): a ConfigOlhar e o genoma da visao (null sem a subchave), as TVs a vista para a decisao seguinte e a TV que o pet olha */
  readonly co: ConfigOlhar | null = null;
  /** o ir ate a TV (D-GV-TVJOGO-3): a unidade de olhar de uma TV fora do raio vira o "ir_tv" (so com a subchave `olhar`) */
  readonly irAteTv: boolean = false;
  readonly genomaVisao: GenomaVisao | null = null;
  private telas: [number, number, number, number][] | null = null;
  private olhando: number | null = null;
  /** o lance do dono (BB-4): a ConfigLanceDono e o convite entregue pelo laco para a decisao seguinte (null: nao entregue) */
  readonly cl: ConfigLanceDono;
  private convite: boolean | null = null;
  /** as regras do E1 (EQ-7): a ConfigEquilibrioCuidado e o estagio entregue pelo motor do jogo para a decisao seguinte (null: nao entregue) */
  readonly ceq: ConfigEquilibrioCuidado;
  private bebe: boolean | null = null;
  /** o enjoo (D-GV-ENJOO-CER): a ConfigEnjooTela ligada (null desligada), o enjoo lembrado de cada TV e o ganho dele por decisao */
  readonly ce: ConfigEnjooTela | null = null;
  private readonly enjooTv: Record<number, number> = {};
  private kEnjooLembrado = 0;

  /** `inatos`: os valores de partida (a ConfigDigibrainInatos); so o G-PAR-VIDA dos fins passa outros (digibrain_modular_fins.json.gz) */
  /** `sono`: a ConfigSonoSegura (o 4o argumento, como na main); `olhar`: as opcoes do olhar (P1f), so com a subchave; `lance`: a
   *  ConfigLanceDono (BB-4) */
  constructor(cd: ConfigLab = CONFIG_DIGIBRAIN_LAB, inatos: typeof INATOS_MODULAR = INATOS_MODULAR, lutaMemoria = false,
    sono: ConfigSonoSegura = CONFIG_SONO_SEGURA, olhar?: OpcoesOlhar, lance: ConfigLanceDono = CONFIG_LANCE_DONO,
    cooperacao: Readonly<ConfigCooperacao> | null = null, equilibrio: ConfigEquilibrioCuidado = CONFIG_EQUILIBRIO_CUIDADO) {
    if (!cd.ligada) throw new DigibrainDesligado("o DigiBrain modular so existe com a ConfigDigibrain ligada");
    this.cl = validarLanceDono(lance);
    this.ceq = validarEquilibrioCuidado(equilibrio);
    this.cd = cd;
    this.inatos = inatos;
    const cfg = { intervalo_decisao_ticks: CONFIG_MODULAR_MUNDO.intervalo_decisao_ticks };
    this.S = inatos.escala;
    if (cd.olhar) {                                       // o olhar (P1f): o genoma dado, ou o da semente do ovo (rng propria `visao-ovo`)
      if (cd.fala_unidades) throw new Error("olhar nao se combina com a fala_unidades (GOSTO_VISUAL, P1d: PROPOSTO, sem teste da combinacao)");
      this.co = olhar?.cfgOlhar ?? CONFIG_OLHAR;
      if (olhar?.genoma === undefined && olhar?.semente === undefined) throw new Error("o olhar pede o genoma da visao: a semente do ovo ou o genoma");
      this.genomaVisao = olhar.genoma ?? genomaVisao(olhar.semente!, this.co);
    } else if (olhar !== undefined) {
      throw new Error("a ConfigOlhar e o genoma da visao so com a subchave olhar");
    }
    if (olhar?.cfgEnjooTela !== undefined && conferirConfigEnjooTela(olhar.cfgEnjooTela).ligada) {   // o enjoo (D-GV-ENJOO-CER)
      this.ce = olhar.cfgEnjooTela;
      this.kEnjooLembrado = ganhoDeTau(this.ce.tau_enjoo_lembrado, CONFIG_MODULAR_MUNDO.intervalo_decisao_ticks, this.S);
    }
    this.sens = new Sens(CONFIG_MODULAR_MUNDO, CONFIG_MODULAR_MUNDO, inatos, this.co, this.genomaVisao, this.ce);
    /* o ir ate a TV (a decisao D, D-GV-TVJOGO-3; so com a subchave `olhar`): a unidade de olhar de uma TV fora do raio vai ao motor como o
       "ir_tv"; desligado, uma linha longe falha alto no M-SENS */
    this.irAteTv = olhar?.irAteTv === true;
    if (this.irAteTv) this.sens.ligarIrAteTv();
    this.afeto = new Afeto(cfg, cd, inatos, null);
    this.estado = new EstadoDinamico(cfg, cd, inatos);
    this.impulso = new Impulso(inatos, cd, undefined, this.co, this.cl, this.ceq);
    this.lutaMemoria = lutaMemoria;
    if (lutaMemoria && !cd.memoria_autobio) throw new Error("luta_memoria so com a memoria_autobio (docs/TAREFA_V3_PONTE_LUTA.md, 3.2)");
    this.mem = new Memoria({ sub: CONFIG_MODULAR_MUNDO.sub }, inatos, cd, lutaMemoria);
    this.arb = new Arbitragem(inatos, cd.memoria_autobio, cd.facetas_mem, sono);   // `sono`: o sono que segura (SONO_SEGURA)
    this.plast = new Plasticidade(cd, inatos);
    /* a CO7 (docs/ESPEC_V3_COOPERACAO_CO7.md): os deveres no M-SENS, no M-ARB e no M-AFETO, so com a subchave `co7`; sem ela, nada muda */
    if (cooperacao !== null && cooperacao.co7) {
      this.dever = cooperacao;
      this.sens.ligarDever(cooperacao, CONFIG_MODULAR_MUNDO.sub);
      this.arb.ligarDever(cooperacao);
      this.afeto.ligarDever(cooperacao);
    }
  }
  /** a CO7: a ConfigCooperacao com a `co7`; null desligada */
  dever: Readonly<ConfigCooperacao> | null = null;

  get ultimoMotivo(): Dict | null { return this.motivos.length ? this.motivos[this.motivos.length - 1]! : null; }

  // ------------------------------------------------------------ a decisao
  agir(obs: ObservacaoMundoLobos, rng: RngPolitica): AcaoPet {
    if (obs.corpo === undefined || obs.mundo === undefined) {
      throw new Error("o DigiBrain modular decide com o corpo e o mundo na Observacao (obs.corpo e obs.mundo)");
    }
    if (this.pendencia !== null) {
      this.fechar(this.pendencia, obs);
      this.pendencia = null;
    }
    const cd = this.cd, k = this.k;
    const m = obs.mundo;
    const oMod: ObservacaoModular = {
      corpo: obs.corpo, vetor_estado: obs.v, ticks_desde_cuidado: obs.tdc,
      mundo: { x: m.x, y: m.y, regiao: m.regiao, direcao_cheiro: m.direcao_cheiro, vistos: m.vistos },
      ...(obs.social !== undefined ? { social: obs.social } : {}),      // a CO6: so o M-SENS a le
    };
    const lutas = this.lutaMemoria ? this.lutas : null;
    if (this.lutaMemoria) this.lutas = [];
    let sens;
    if (cd.olhar) {                                       // o olhar (P1f): as TVs a vista, do gancho `verTela` (sem ele, nenhuma)
      const telas = this.telas ?? [];
      this.telas = null;
      sens = this.sens.codificar(oMod, lutas, telas);
    } else {
      sens = lutas === null ? this.sens.codificar(oMod) : this.sens.codificar(oMod, lutas);
    }
    const receptores = this.sens.receptores!;
    this.plast.montar(receptores);
    const afeto = this.afeto.ler(sens);
    const reflexo = this.arb.reflexo(sens, afeto.urgencias);   // uma conta so, ao M-ESTADO e ao M-ARB (o sono que segura le a fome)
    const ctx = this.estado.contexto();
    const tick = this.mem.relogio(sens.minuto);                // a C4, M2 e M3: o relogio, a consolidacao do dia novo e a lembranca
    const consolidacao = this.mem.consolidar(k);
    const lembranca = this.mem.lembrar(sens);
    const termoLem = this.mem.termoLembranca(lembranca);
    const episodiosLuta = this.lutaMemoria ? this.episodiosLuta(sens, afeto, tick) : null;
    const memoria = cd.m_mem ? this.mem.recuperar(sens, afeto) : null;
    const [gosto, resumoOlhar] = cd.olhar ? this.gostoDaDecisao(sens) : [null, null];
    const lance = this.cl.ligada ? this.entradaBolaDoDono(afeto.urgencias) : null;   // o lance do dono (BB-4): o convite, salvo a fome urgente
    let bebe: number | null = null;                     // o bebe que come com a fome dele (EQ-7): a entrada `bebe` do gancho do motor
    if (this.ceq.comer_bebe) {
      if (this.bebe === null) throw new Error("o DigiBrain com a ConfigEquilibrioCuidado.comer_bebe decide sem o gancho estagio_bebe do motor");
      bebe = this.bebe ? this.S : 0;
      this.bebe = null;
    }
    let guarda: boolean | null = null;                  // a guarda da fome urgente no brincar (EQ-7): a fome urgente do sono e do convite
    if (this.ceq.guarda_fome_brincar) {
      if (!("fome" in afeto.urgencias)) throw new Error("a guarda do brincar le a urgencia da fome, e ela nao veio do M-AFETO");
      guarda = afeto.urgencias["fome"]! > this.inatos.urgencia_lambda;
    }
    const [unidades, z] = this.impulso.unidades(
      sens, afeto, ctx, this.plast, memoria, this.afeto.drives(receptores), termoLem === null ? null : [termoLem, this.mem.casa], null, gosto,
      lance === null ? null : lance.bola_do_dono, this.ce === null ? null : this.termoEnjoo(resumoOlhar!), bebe);
    const esc = this.arb.escolher(unidades, afeto, sens, rng, reflexo, null, guarda === true);   // a rng de politica vai so ao M-ARB
    this.conferirDesligadas(unidades);
    const unidade = esc.unidade;
    const fins = this.estado.escolhida(unidade, z, afeto.g_apr, k, reflexo);
    const creditos = creditar(this.plast, fins);
    let intencao = intencaoDaUnidade(unidade);
    if (this.irAteTv && unidade.chave[0] === COMPORTAMENTO_OLHAR && this.sens.longe(unidade.objeto as { d: number }))
      intencao = { acao: "ir_tv", tipo_alvo: null, id_alvo: null, ponto: null };   // a TV fora do raio (D-GV-TVJOGO-3): o pet anda ate ela
    const urg = afeto.urgencias;
    let drive: string | null = null;
    for (const r of Object.keys(urg).sort()) if (drive === null || urg[r]! > urg[drive]!) drive = r;
    const motivo: Dict = {
      k, acao: intencao.acao, escolha: chaveJson(unidade.chave), tipo_escolha: unidade.tipo, reflexo: esc.reflexo, nada_a_fazer: esc.nada_a_fazer, u: esc.u,
      unidades: unidades.map((x, i) => ({ chave: chaveJson(x.chave), termos: x.termos, a: x.a, w: esc.pesos[i] })),
      afeto: { urgencias: urg, V: afeto.V, E: afeto.E, e_usada: afeto.e_usada, g_apr: afeto.g_apr, g_exp: afeto.g_exp },
      estado: { I: chaveJson(ctx.I), C: ctx.C, n_sp: ctx.n_sp, F: ctx.F },
      memoria: memoria === null ? null : { pista: memoria.pista, recuperado: memoria.recuperado, lugar: memoria.lugar, valor: memoria.valor },
      sondas: esc.sondas,
      falta_fome: sens.falta["fome"] ?? null,
      contexto: { drive: Object.keys(urg).length ? drive : null, comida_vista: sens.conjuncoes.comida_vista > 0, noite: sens.contexto.noite > 0 },
      fins: registrados(fins), creditos, gestos: this.gestosAgora, consequencia: null,
    };
    this.motivos.push(motivo);
    const entregue = fins.filter(f => f.registro === false).map(fim);
    if (entregue.length) motivo["busca_entregue"] = entregue;   // a busca guardada (DX-4), entregue sem a opcao composta
    motivo["lembranca"] = {
      ...lembranca, L: termoLem === null ? null : termoLem.L,
      unidades: termoLem === null ? [] : unidades.filter(x => this.mem.casa(termoLem, x)).map(x => chaveJson(x.chave)),
    };
    motivo["consolidacao"] = consolidacao;
    if (this.lutaMemoria) motivo["lutas"] = episodiosLuta;      // a ponte da luta (PE3): desligada, nenhum campo novo
    if (lance !== null) motivo["lance"] = lance;               // o lance do dono (BB-4): desligada, nenhum campo novo
    if (equilibrioLigado(this.ceq)) motivo["equilibrio"] = { bebe, fome_urgente_sem_brincar: guarda };   // as regras do E1: desligadas, nada
    if (this.dever !== null)                              // a CO7: desligada, nenhum campo novo
      motivo["dever"] = esc.dever === null || esc.dever === undefined ? null : { ...esc.dever, culpa: afeto.culpa, inveja: afeto.inveja };
    if (cd.olhar) {                                       // o olhar (P1f): desligada, nenhum campo novo
      this.olhando = unidade.chave[0] === COMPORTAMENTO_OLHAR && intencao.acao === "ocioso" ? unidade.chave[2] as number : null;
      motivo["olhar"] = { ...resumoOlhar, olha: this.olhando };
    }
    this.pendencia = {
      k, intencao, unidade, sens, g_apr: afeto.g_apr, pediu: false, alvo: null, corpo: null, transicao: null, mundo: null,
      tick, afeto: { V: afeto.V, E: afeto.E }, gestos: this.gestosAgora,
    };
    this.gestosAgora = [];
    this.k += 1;
    return intencao.acao;
  }

  // ------------------------------------------------------------ o lance do dono (BB-4, so com a ConfigLanceDono ligada)
  /** o laco com o lance do dono, antes de cada decisao: o tick esta na janela do convite (`janela_convite_ticks` depois do lance)? Sem a chave,
   *  ou duas vezes sem decisao, falha alto (o motor e o cerebro divergem na chave) */
  bolaDoDono(convite: boolean): void {
    if (!this.cl.ligada) throw new Error("bola_do_dono: o lance do dono com o DigiBrain modular exige a ConfigLanceDono ligada no cerebro (BB-4)");
    if (typeof convite !== "boolean") throw new Error(`bola_do_dono recebe um bool: ${String(convite)}`);
    if (this.convite !== null) throw new Error("bola_do_dono duas vezes antes da mesma decisao");
    this.convite = convite;
  }

  // ------------------------------------------------------------ o bebe que come com a fome dele (EQ-7, so com a chave `comer_bebe`)
  /** o motor do jogo, antes de cada decisao: o pet e um bebe (o In-Training da tela)? Sem a chave, ou duas vezes sem decisao, falha alto */
  estagioBebe(bebe: boolean): void {
    if (!this.ceq.comer_bebe) throw new Error("estagio_bebe: o gancho do bebe exige a ConfigEquilibrioCuidado.comer_bebe ligada no cerebro (EQ-7)");
    if (typeof bebe !== "boolean") throw new Error(`estagio_bebe recebe um bool: ${String(bebe)}`);
    if (this.bebe !== null) throw new Error("estagio_bebe duas vezes antes da mesma decisao");
    this.bebe = bebe;
  }

  /** a entrada `bola_do_dono` da decisao: S na janela do convite, 0 fora dela e 0 com a fome urgente (a urgencia da fome acima do
   *  `urgencia_lambda`). Sem o gancho do laco antes da decisao, falha alto */
  private entradaBolaDoDono(urgencias: Readonly<Record<string, number>>): { convite: boolean; fome_urgente: boolean; bola_do_dono: number } {
    if (this.convite === null) throw new Error("o DigiBrain com a ConfigLanceDono ligada decide sem o gancho bola_do_dono do motor (o motor sem o lance?)");
    if (!("fome" in urgencias)) throw new Error("o convite le a urgencia da fome, e ela nao veio do M-AFETO");
    const convite = this.convite;
    this.convite = null;
    const urgente = urgencias["fome"]! > this.inatos.urgencia_lambda;
    return { convite, fome_urgente: urgente, bola_do_dono: convite && !urgente ? this.S : 0 };
  }

  // ------------------------------------------------------------ o olhar (P1f, so com a subchave `olhar`)
  /** o termo `gosto` da unidade da TV que o pet olhava (se ela ainda esta a vista e o corpo le a tela): mul(w_gosto, agrado - S/2); e o resumo */
  private gostoDaDecisao(sens: Dict): [Record<number, number>, Dict] {
    const S = this.S, niveis = sens["tela_niveis"] as Record<string, number> | null, telas = sens["telas"] as { id: number }[];
    let a: number | null = null, aInato: number | null = null;
    const gosto: Record<number, number> = {};
    const visivel = telas.some(o => o.id === this.olhando && !this.sens.longe(o as unknown as { d: number }));
    const leu = this.olhando !== null && visivel && niveis !== null;
    let eAgora: number | null = null;
    if (this.ce !== null) {                               // o enjoo (D-GV-ENJOO-CER): o lembrado cai; o da TV olhada vira o lido agora
      for (const id of Object.keys(this.enjooTv).map(Number).sort((x, y) => x - y)) this.enjooTv[id] = integrar(this.enjooTv[id]!, 0, this.kEnjooLembrado, S);
      eAgora = sens["tela_enjoo"] as number | null;
      if (leu) {
        if (eAgora === null) throw new Error("o enjoo ligado e a percepcao sem o receptor enjoo_tela");
        this.enjooTv[this.olhando!] = eAgora;
      }
    }
    let aGosto: number | null = null;
    if (leu) {
      a = this.sens.agrado(niveis!);
      aInato = this.sens.agradoInato(niveis!);
      aGosto = this.ce === null ? a : this.sens.agradoEfetivo(niveis!, eAgora!);
      gosto[this.olhando!] = mul(this.co!.w_gosto, aGosto - Math.floor(S / 2), S);
    }
    const resumo: Dict = { telas: telas.map(o => o.id), olhava: this.olhando, agrado: a, agrado_inato: aInato,
                           gosto: this.olhando !== null && this.olhando in gosto ? gosto[this.olhando]! : null };
    if (this.ce !== null) {                               // desligado, nenhum campo novo
      const termo: Record<number, number> = {};
      for (const o of telas) if (o.id in this.enjooTv) termo[o.id] = 0 - mul(this.ce.w_enjoo, this.enjooTv[o.id]!, S);   // 0 - x: sem o -0 do TS
      Object.assign(resumo, { enjoo: leu ? eAgora : null, agrado_efetivo: leu ? aGosto : null, enjoo_tv: { ...this.enjooTv }, termo_enjoo: { ...termo } });
    }
    return [gosto, resumo];
  }

  /** o termo `enjoo` de cada TV a vista (D-GV-ENJOO-CER), do resumo da decisao */
  private termoEnjoo(resumo: Dict): Record<number, number> {
    return { ...(resumo["termo_enjoo"] as Record<number, number>) };
  }

  private exigirOlhar(gancho: string): ConfigOlhar {
    if (!this.cd.olhar) throw new Error(`${gancho}: a TV com o DigiBrain modular exige a subchave olhar (GOSTO_VISUAL, P1d)`);
    return this.co!;
  }

  /** o laco, antes da decisao: as TVs a vista, [id, dx, dy, d] inteiros (validadas no M-SENS). Duas vezes sem decisao falha alto */
  verTela(linhas: [number, number, number, number][]): void {
    this.exigirOlhar("ver_tela");
    if (this.telas !== null) throw new Error("ver_tela duas vezes antes da mesma decisao");
    if (!Array.isArray(linhas)) throw new Error("ver_tela recebe a lista das TVs a vista");
    this.telas = linhas.map(l => [...l] as [number, number, number, number]);
  }

  /** o id da TV que o pet olha (a unidade de olhar da ultima decisao), ou null */
  olhandoTela(): number | null {
    this.exigirOlhar("olhando_tela");
    return this.olhando;
  }

  /** GV-16, com a `agrado_no_corpo`: o agrado do nivel lido agora, quando o pet olha; sem ela, ou sem olhar, null */
  agradoTela(leituras: Readonly<Record<string, number>>): number | null {
    const co = this.exigirOlhar("agrado_tela");
    if (!co.agrado_no_corpo || this.olhando === null) return null;
    const niveis = Object.fromEntries(Object.keys(this.sens.otimo).map(c => [c, leituras[`tela_${c}`]!]));
    if (this.ce !== null) return this.sens.agradoEfetivo(niveis, leituras["enjoo_tela"]!);   // o enjoo (D-GV-ENJOO-CER)
    return this.sens.agrado(niveis);
  }

  /** o `escolher_alvo` do Python: o candidato do motor do tipo (e do id) da unidade escolhida; o `u` do motor e ignorado. A excecao unica
   *  (a PE-14 revista): em EXPLORAR, o lugar lembrado e entregue como o ponto (que o mundo valida). Brincar sem bola a vista nao tem alvo */
  escolherAlvo = (acao: "explorar" | "comer" | "brincar", candidatos: AlvoMundo[], _percepcao: PercepcaoMundo, _u: number): AlvoMundo | null => {
    const p = this.pendente(acao, "escolher_alvo");
    if (p.pediu) throw new Error(`escolher_alvo duas vezes na mesma decisao (${acao})`);
    p.pediu = true;
    const it = p.intencao, motivo = this.motivos[this.motivos.length - 1]!;
    if (it.tipo_alvo === null) {
      if (acao === "brincar" && !candidatos.some(c => c.tipo === "bola")) return null;   // brincar sem bola a vista: sem alvo
      throw new Error(`a intencao de ${acao} chegou sem objeto, e o motor pede um alvo`);
    }
    if (it.tipo_alvo === "ponto") {
      if (acao !== "explorar") throw new Error(`o lugar lembrado (ponto) so em EXPLORAR, nao em ${acao}`);
      const alvo = alvoPonto(it.ponto![0], it.ponto![1]);
      motivo["alvo"] = { tipo: alvo.tipo, x: alvo.x, y: alvo.y, id: alvo.id, de: alvo.de, do_mem: true };
      p.alvo = alvo;
      return alvo;
    }
    const alvo = candidatos.find(c => c.tipo === it.tipo_alvo && (it.id_alvo === null || c.id === it.id_alvo));
    if (alvo === undefined) {
      throw new Error(`o alvo da intencao (${it.tipo_alvo}, ${it.id_alvo}) nao esta entre os candidatos do motor: ${JSON.stringify(candidatos.map(c => [c.tipo, c.id]))}`);
    }
    motivo["alvo"] = { tipo: alvo.tipo, x: alvo.x, y: alvo.y, id: alvo.id, de: alvo.de, do_mem: false };
    p.alvo = alvo;
    return alvo;
  };

  // ------------------------------------------------------------ a consequencia (guardada; vai aos modulos na decisao seguinte)
  consequenciaCorpo(acao: AcaoPet, ocorrido: OcorridoCorpo, obsDepois: ObservacaoLobos): void {
    const p = this.pendente(acao, "consequencia_corpo");
    if (p.corpo !== null) throw new Error("consequencia_corpo duas vezes na mesma decisao");
    p.corpo = [ocorrido, obsDepois];
  }

  observar(transicao: TransicaoLobos): void {
    const p = this.pendente(transicao.acao, "observar");
    if (p.transicao !== null) throw new Error("observar duas vezes na mesma decisao");
    p.transicao = transicao;
  }

  consequenciaMundo(acao: AcaoPet, ocorrido: OcorridoMundo, obsDepois: ObservacaoLobos): void {
    const p = this.pendente(acao, "consequencia_mundo");
    if (p.mundo !== null) throw new Error("consequencia_mundo duas vezes na mesma decisao");
    p.mundo = [ocorrido, obsDepois];
  }

  /** o alcance da memoria de lugar do M-MEM passa a ser `dMax` (a ilha grande, IG6; o DigiBrain.alcance_da_memoria do Python); os
   *  `inatos` do cerebro acompanham */
  alcanceDaMemoria(dMax: number): void {
    this.mem.alcance(dMax);
    this.inatos = { ...this.inatos, d_max: dMax } as typeof INATOS_MODULAR;
  }

  /** liga a `luta_memoria` num DigiBrain que ainda nao decidiu (a marca `pl` do registro chega depois de o pet nascer): idempotente */
  ligarLutaMemoria(): void {
    if (this.lutaMemoria) return;
    if (this.k !== 0 || this.pendencia !== null) throw new Error("a luta_memoria liga antes da primeira decisao");
    if (!this.cd.memoria_autobio) throw new Error("luta_memoria so com a memoria_autobio (docs/TAREFA_V3_PONTE_LUTA.md, 3.2)");
    this.lutaMemoria = true;
    this.mem.luta = true;
  }

  /** o resumo pronto da luta (ponte da luta, PE3; espelho de `DigiBrain.receber_luta`), so guardado ate a decisao seguinte. Sem a chave, falha alto */
  receberLuta(rival: string, resultado: number, vidaPerdidaS: number, tick: number): void {
    if (!this.lutaMemoria) throw new LutaSemChave("receberLuta exige a luta_memoria ligada (ponte da luta, PE3)");
    this.sens.resumirLutas([{ rival, resultado, vida_perdida_s: vidaPerdidaS, tick }]);     // a validacao do resumo
    this.lutas.push({ rival, resultado, vida_perdida_s: vidaPerdidaS, tick });
  }

  /** a ponte da luta (PE3): cada resumo da Observacao vira, se a regra de hoje o aceita, um episodio de origem `luta`. O corpo de antes e o da
   *  ultima consequencia fechada (sem ela, antes = depois); o V e o E nao andam */
  private episodiosLuta(sens: Dict, afeto: Dict, tick: number): Dict[] {
    const out: Dict[] = [];
    for (const resumo of sens["lutas"] as ResumoLutaSens[]) {
      const recs = this.sens.receptores!;
      const antes = this.pcAntesLuta !== null ? this.pcAntesLuta : sens["pc"];
      const cons = this.afeto.sigmaLuta(antes, sens["pc"], recs);
      const l0 = recs.map(r => leituraReceptor(antes as PercepcaoCorpoLobos, r, this.S));
      const l1 = recs.map(r => sens["leitura"][r] as number);
      const ep = episodioLuta(sens as any, recs, l0, l1, { V: afeto["V"], E: afeto["E"] }, cons, resumo, this.k, tick, this.inatos);
      out.push({ ...resumo, episodio: ep === null ? null : this.mem.codificarAutobio(ep) });
    }
    return out;
  }

  /** o gesto do dono, so registrado: nenhum modulo o recebe como sinal (o corpo o sente pelos receptores) */
  receberAcaoDono(acao: string, tick: number): void {
    this.gestosAgora.push([acao, tick]);
    this.gestos[acao] = (this.gestos[acao] ?? 0) + 1;
  }

  /** o carinho e o tapa, pelo corpo: o modular nao os le como sinal (o Python nao tem este gancho) */
  mudancaNoCorpo(): void { /* nada */ }

  estadoInterno(): Dict {
    const modulos: Dict = {};
    for (const [nome, mod] of [["sens", this.sens], ["afeto", this.afeto], ["estado", this.estado], ["mem", this.mem], ["arb", this.arb],
                               ["plast", this.plast]] as const) modulos[nome] = mod.estadoInterno();
    const out: Dict = {
      nome: this.nome, versao_pet: this.versao_pet, k: this.k, pendente: this.pendencia !== null,
      gestos: Object.fromEntries(Object.entries(this.gestos).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))), modulos, motivos: this.motivos,
    };
    if (this.sens.social !== null) out["social"] = { reputacao: { ...this.sens.social.reputacao }, peso_dever: this.sens.social.peso_dever };   // a CO6
    if (this.cd.olhar) out["olhar"] = { olhando: this.olhando, genoma_visao: { otimo: { ...this.genomaVisao!.otimo }, largura: { ...this.genomaVisao!.largura } } };
    if (this.ce !== null) (out["olhar"] as Dict)["enjoo_tv"] = { ...this.enjooTv };   // o enjoo (D-GV-ENJOO-CER): desligado, nenhum campo novo
    return out;
  }

  // ------------------------------------------------------------ a pendencia
  private pendente(acao: string, gancho: string): Pendencia {
    const p = this.pendencia;
    if (p === null) throw new Error(`${gancho} sem decisao pendente`);
    if (p.intencao.acao !== acao) throw new Error(`${gancho} de ${acao} na decisao de ${p.intencao.acao}`);
    return p;
  }

  /** com uma subchave desligada, o termo do modulo e 0 em toda unidade e o estado dele fica em 0 (falha alto) */
  private conferirDesligadas(unidades: readonly UnidadeImpulso[]): void {
    const cd = this.cd;
    for (const [termo, ligada] of [["incentivo", cd.p1], ["habito", cd.p2], ["memoria", cd.m_mem], ["persistencia", cd.persistencia]] as const) {
      if (!ligada && unidades.some(x => x.termos[termo] !== 0)) throw new Error(`a subchave do termo '${termo}' esta desligada e o termo nao e 0`);
    }
    if (!cd.p1 && !this.plast.desfechoZero()) throw new Error("sem o P1, o desfecho e o andar ficam em 0");
    if (!cd.p2 && !this.plast.habitoZero()) throw new Error("sem o P2, o habito fica em 0");
    if (!cd.m_mem && this.mem.episodios.length) throw new Error("sem o M-MEM, a memoria fica vazia");
    if (!cd.olhar && unidades.some(x => x.acao === COMPORTAMENTO_OLHAR || "gosto" in x.termos)) throw new Error("sem a subchave olhar, nenhuma unidade de olhar nem termo gosto");
    const fala = unidades.filter(x => x.acao === "chamar_atencao").map(x => x.chave[1]);
    if (JSON.stringify(fala) !== JSON.stringify(cd.fala_unidades ? [...CONTEUDOS_FALA] : [null]))
      throw new Error(`as unidades do chamar ${JSON.stringify(fala)} nao sao as da fala_unidades ${cd.fala_unidades ? "ligada" : "desligada"}`);
  }

  /** a consequencia da decisao anterior aos modulos. Com a `fala_unidades` (A1.1), a opcao de fala le o corpo de depois na percepcao da
   *  decisao seguinte (`obsSeguinte`, antes da acao seguinte); as outras opcoes, e o chamar desligada a subchave, leem o corpo do tick da acao */
  private fechar(p: Pendencia, obsSeguinte: ObservacaoMundoLobos): void {
    const it = p.intencao, S = this.S, acao = it.acao;
    if (p.corpo === null || p.transicao === null) throw new Error(`a decisao de ${acao} ficou sem o gancho de consequencia (o corpo e o observar)`);
    const comAlvo = ACOES_COM_ALVO.includes(acao);
    if (comAlvo && !p.pediu) throw new Error(`a decisao de ${acao} tinha alvo, e o motor nao pediu o alvo`);
    if (comAlvo && p.mundo === null) throw new Error(`a decisao de ${acao} ficou sem o consequencia_mundo`);
    const pc0 = p.sens["pc"];
    let pc1 = p.corpo[1].corpo;
    if (this.cd.fala_unidades && acao === "chamar_atencao") {           // A1.1: a fala ate a decisao seguinte
      if (!(CONTEUDOS_FALA as readonly unknown[]).includes(p.unidade.chave[1])) throw new Error(`a fala da decisao ${p.k} sem conteudo com a fala_unidades ligada`);
      pc1 = obsSeguinte.corpo;
    }
    const pm1 = (p.transicao.observacaoSeguinte as ObservacaoMundoLobos).mundo;
    if (pc1 === undefined || pm1 === undefined) throw new Error("a consequencia sem o corpo ou sem o mundo de depois");
    const ocorrido: OcorridoMundo | null = p.mundo === null ? null : p.mundo[0];
    const recs = this.sens.receptores!;
    /* o ir ate a TV (D-GV-TVJOGO-3): a opcao de olhar executada como o "ir_tv" nao olhou (sem agrado, sem exposicao e sem o P1 da tela) */
    const olhou = this.cd.olhar === true && p.unidade.chave[0] === COMPORTAMENTO_OLHAR && acao === "ocioso";
    let gv: number | null = null, olhar: Dict | null = null, niveis: Record<string, number> | null = null;
    if (olhou) {                                          // o olhar (P1f): o agrado do nivel de depois, contra o alvo de antes da exposicao
      niveis = this.sens.niveisTela(pc1 as Dict);
      if (niveis !== null) {
        const a = this.sens.agrado(niveis);
        if (this.ce !== null) {                           // o enjoo (D-GV-ENJOO-CER): o agrado efetivo, com o enjoo de depois
          const e1 = (pc1 as Dict)["enjoo_tela"] as number | null | undefined;
          if (e1 === null || e1 === undefined) throw new Error("o enjoo ligado e o corpo de depois sem o receptor enjoo_tela");
          const aEf = this.sens.agradoEfetivo(niveis, e1);
          gv = mul(this.co!.ganho_gosto_visual, aEf - Math.floor(S / 2), S);
          olhar = { agrado: a, gosto_visual: gv, enjoo: e1, agrado_efetivo: aEf };
        } else {
          gv = mul(this.co!.ganho_gosto_visual, a - Math.floor(S / 2), S);
          olhar = { agrado: a, gosto_visual: gv };
        }
      }
    }
    const cons = this.afeto.consequencia(pc0, pc1, recs, gv);
    const l0 = recs.map(r => leituraReceptor(pc0 as PercepcaoCorpoLobos, r, S));
    const l1 = recs.map(r => leituraReceptor(pc1, r, S));
    if (olhar !== null) {
      this.sens.expor(niveis!, this.ce === null ? null : olhar["enjoo"] as number);   // a exposicao (saturada com o enjoo, D-GV-ENJOO-CER)
      olhar["desloc"] = { ...this.sens.desloc };
    }
    const pos0: readonly [number, number] = p.sens["pos"], pos1: readonly [number, number] = [pm1.x, pm1.y];
    const comeu = ocorrido === null ? null : ocorrido.comeu as Dict | null;
    const classeComida = comeu === null ? null : (comeu["situacao"] === "podre" ? "podre" : comeu["tipo"] as string);
    let p1 = null;
    if (acao === "comer") {
      p1 = this.plast.consequenciaP1("comer", comeu !== null && comeu["como"] === "comer" ? classeComida : null, l0, l1, pos0, pos1, p.g_apr);
    } else if (acao === "brincar") {
      p1 = this.plast.consequenciaP1("brincar", ocorrido!.brincou_com_bola ? "bola" : null, l0, l1, pos0, pos1, p.g_apr);
    } else if (olhou) {                                   // o olhar (P1f): o desfecho da classe `tela`
      p1 = this.plast.consequenciaOlhar(l0, l1, p.g_apr);
    }
    const chave = p.unidade.chave;
    let visto = true, d: number | null = null;
    if (chave[1] === "comida" || chave[1] === "bola") {
      const alvo = pm1.vistos.find(v => v[0] === chave[2]);
      visto = alvo !== undefined;
      d = alvo === undefined ? null : alvo[4];
    } else if (chave[1] === "ponto") {
      const [px, py] = chave[2] as readonly [number, number];
      d = raizInteira((px - pos1[0]) * (px - pos1[0]) + (py - pos1[1]) * (py - pos1[1]));
    }
    const fins = this.estado.consequencia(cons.r_n, ocorrido === null ? null : { comeu: comeu as { id: number } | null, brincou_com_bola: ocorrido.brincou_com_bola, chegou: ocorrido.chegou }, {
      visto, d, ha_cheiro: pm1.direcao_cheiro !== 0,
      comida_boa_vista: pm1.vistos.some(v => (COMIDAS_BOAS as readonly string[]).includes(classeDoTipo(v[1]))),
    });
    const creditos = creditar(this.plast, fins);
    let episodio: number | null = null;
    if (this.cd.m_mem) {
      const delta = Object.fromEntries(recs.map((r, i) => [r, l1[i]! - l0[i]!]));
      const base = { decisao: p.k, regiao: pm1.regiao, delta, r: cons.r, r_n: cons.r_n, hora: p.sens["minuto"] as number, fome_antes: (p.sens["falta"]["fome"] ?? null) as number | null };
      if (comeu !== null) {
        episodio = this.mem.codificar({ ...base, ponto: pos1, classe: classeComida!, origem: "consumo" });
      } else if (chave[1] === "ponto" && ocorrido!.chegou) {
        episodio = this.mem.codificar({ ...base, ponto: chave[2] as readonly [number, number], classe: "nao_havia", origem: "visita", r: 0, r_n: 0 });
      }
    }
    if (this.lutaMemoria) this.pcAntesLuta = pc1;       // o corpo de antes da proxima luta (nenhum efeito nos modulos)
    // a C4, M0 e M1: o episodio completo, que a lembranca le
    const ida = chave[1] === "ponto" ? (fins.find(f => JSON.stringify(chaveJson(f.chave)) === JSON.stringify(chaveJson(chave)))?.r ?? null) : null;
    const desfecho = { comeu: classeComida, chegou: ocorrido !== null && ocorrido.chegou, r_ida: ida };
    const ep = episodioAutobio(p.sens as any, pm1, recs, l0, l1, p.afeto, cons, p.gestos, p.unidade as any, desfecho, p.k, p.tick, this.inatos);
    const autobio = ep === null ? null : this.mem.codificarAutobio(ep);
    const motivo = this.motivos[p.k]!;
    motivo["consequencia"] = {
      r: cons.r, r_n: cons.r_n, canais: cons.canais,
      comeu: comeu === null ? null : { id: comeu["id"], tipo: comeu["tipo"], situacao: comeu["situacao"], como: comeu["como"] },
      chegou: ocorrido === null ? null : ocorrido.chegou, p1, creditos, episodio, autobio,
    };
    if (this.cd.olhar) motivo["consequencia"]["olhar"] = olhar;   // o olhar (P1f): desligada, nenhum campo novo
    motivo["fins"] = [...motivo["fins"], ...registrados(fins)];
  }
}

/** as opcoes que acabaram ao P2, salvo a busca guardada no "achou" (DX-4: o credito dela segue pela opcao composta) */
function creditar(plast: Plasticidade, fins: readonly OpcaoFim[]): Dict[] {
  return fins.filter(f => f.credito ?? true).map(f => plast.creditar(f as OpcaoCredito)).filter((c): c is NonNullable<typeof c> => c !== null);
}

/** os fins para o registro: sem as opcoes de uma decisao e sem a busca entregue depois do "achou" (ja registrada nele) */
function registrados(fins: readonly OpcaoFim[]): Dict[] {
  return fins.filter(f => f.motivo !== "unica" && (f.registro ?? true)).map(fim);
}

/** o resumo de uma opcao que acabou, para o registro (a opcao composta da DX-4 marcada) */
function fim(f: OpcaoFim): Dict {
  const out: Dict = { chave: chaveJson(f.chave as ChaveUnidade), inicio: f.inicio, n: f.n, motivo: f.motivo, meta: f.meta, r: f.r };
  if (f.composta) out["composta"] = true;
  return out;
}
