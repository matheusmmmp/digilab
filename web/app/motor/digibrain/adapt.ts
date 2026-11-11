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
   `obs` do `agir` seguinte, antes da acao seguinte); o mundo de depois e o de hoje. Desligada (todo pet de hoje), nada muda. */
import { leituraReceptor, type PercepcaoCorpoLobos } from "../lobos.ts";
import type { OcorridoMundo, PoliticaCorpoMundo } from "../motor_corpo_mundo.ts";
import type { OcorridoCorpo, ObservacaoLobos, TransicaoLobos } from "../lobos.ts";
import { alvoPonto, type AlvoMundo, type PercepcaoMundo } from "../mundo.ts";
import type { AcaoPet } from "../tipos.ts";
import { chaveJson, raizInteira, type ChaveUnidade } from "./_comum.ts";
import { Afeto } from "./afeto.ts";
import { Arbitragem, type RngPolitica } from "./arb.ts";
import { CONFIG_DIGIBRAIN_LAB, CONFIG_MODULAR_MUNDO, CONTEUDOS_FALA, INATOS_MODULAR, type ConfigDigibrainModular } from "./constantes.ts";
import { EstadoDinamico, type OpcaoFim } from "./estado.ts";
import { Impulso, type UnidadeImpulso } from "./impulso.ts";
import { Memoria, episodioAutobio, episodioLuta } from "./mem.ts";
import { Plasticidade, type OpcaoCredito } from "./plast.ts";
import { COMIDAS_BOAS, Sens, classeDoTipo, type ObservacaoModular, type ResumoLutaSens } from "./sens.ts";

/** o `VERSAO_PET_DIGIBRAIN` do Python (a DM-5); o pet de teste do jogo tem a versao propria (VERSAO_PET_LAB, motor/constantes.ts) */
export const VERSAO_PET_DIGIBRAIN = 13;

type Dict = Record<string, any>;
/** a Observacao do laco com o mundo: o corpo (os receptores) e o mundo (a percepcao) */
export type ObservacaoMundoLobos = ObservacaoLobos & { mundo?: PercepcaoMundo };

/** a escolha do M-ARB vista pelo motor: a acao e, nas acoes com alvo, o tipo do candidato do motor, o id dele e, no lugar lembrado, o ponto */
export interface Intencao { acao: AcaoPet; tipo_alvo: string | null; id_alvo: number | null; ponto: readonly [number, number] | null }

export function intencaoDaUnidade(unidade: UnidadeImpulso): Intencao {
  const [acao, tipo, ident] = unidade.chave;
  if (tipo === "ponto") return { acao: acao as AcaoPet, tipo_alvo: "ponto", id_alvo: null, ponto: ident as readonly [number, number] };
  /* a unidade de fala (DC3, 3.1): o conteudo fica so na chave; o mundo e o do chamar */
  if (acao === "chamar_atencao") return { acao: acao as AcaoPet, tipo_alvo: null, id_alvo: null, ponto: null };
  return { acao: acao as AcaoPet, tipo_alvo: tipo, id_alvo: tipo === "comida" || tipo === "bola" ? (ident as number) : null, ponto: null };
}

export class DigibrainDesligado extends Error {}
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
  readonly inatos: typeof INATOS_MODULAR;
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

  /** `inatos`: os valores de partida (a ConfigDigibrainInatos); so o G-PAR-VIDA dos fins passa outros (digibrain_modular_fins.json.gz) */
  constructor(cd: ConfigLab = CONFIG_DIGIBRAIN_LAB, inatos: typeof INATOS_MODULAR = INATOS_MODULAR, lutaMemoria = false) {
    if (!cd.ligada) throw new DigibrainDesligado("o DigiBrain modular so existe com a ConfigDigibrain ligada");
    this.cd = cd;
    this.inatos = inatos;
    const cfg = { intervalo_decisao_ticks: CONFIG_MODULAR_MUNDO.intervalo_decisao_ticks };
    this.S = inatos.escala;
    this.sens = new Sens(CONFIG_MODULAR_MUNDO, CONFIG_MODULAR_MUNDO, inatos);
    this.afeto = new Afeto(cfg, cd, inatos, null);
    this.estado = new EstadoDinamico(cfg, cd, inatos);
    this.impulso = new Impulso(inatos, cd);
    this.lutaMemoria = lutaMemoria;
    if (lutaMemoria && !cd.memoria_autobio) throw new Error("luta_memoria so com a memoria_autobio (docs/TAREFA_V3_PONTE_LUTA.md, 3.2)");
    this.mem = new Memoria({ sub: CONFIG_MODULAR_MUNDO.sub }, inatos, cd, lutaMemoria);
    this.arb = new Arbitragem(inatos, cd.memoria_autobio, cd.facetas_mem);
    this.plast = new Plasticidade(cd, inatos);
  }

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
    };
    const lutas = this.lutaMemoria ? this.lutas : null;
    if (this.lutaMemoria) this.lutas = [];
    const sens = lutas === null ? this.sens.codificar(oMod) : this.sens.codificar(oMod, lutas);
    const receptores = this.sens.receptores!;
    this.plast.montar(receptores);
    const afeto = this.afeto.ler(sens);
    const reflexo = this.arb.reflexo(sens);                    // uma conta so, ao M-ESTADO e ao M-ARB
    const ctx = this.estado.contexto();
    const tick = this.mem.relogio(sens.minuto);                // a C4, M2 e M3: o relogio, a consolidacao do dia novo e a lembranca
    const consolidacao = this.mem.consolidar(k);
    const lembranca = this.mem.lembrar(sens);
    const termoLem = this.mem.termoLembranca(lembranca);
    const episodiosLuta = this.lutaMemoria ? this.episodiosLuta(sens, afeto, tick) : null;
    const memoria = cd.m_mem ? this.mem.recuperar(sens, afeto) : null;
    const [unidades, z] = this.impulso.unidades(
      sens, afeto, ctx, this.plast, memoria, this.afeto.drives(receptores), termoLem === null ? null : [termoLem, this.mem.casa], null);
    const esc = this.arb.escolher(unidades, afeto, sens, rng, reflexo, null);   // a rng de politica vai so ao M-ARB
    this.conferirDesligadas(unidades);
    const unidade = esc.unidade;
    const fins = this.estado.escolhida(unidade, z, afeto.g_apr, k, reflexo);
    const creditos = creditar(this.plast, fins);
    const intencao = intencaoDaUnidade(unidade);
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
    this.pendencia = {
      k, intencao, unidade, sens, g_apr: afeto.g_apr, pediu: false, alvo: null, corpo: null, transicao: null, mundo: null,
      tick, afeto: { V: afeto.V, E: afeto.E }, gestos: this.gestosAgora,
    };
    this.gestosAgora = [];
    this.k += 1;
    return intencao.acao;
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
    return {
      nome: this.nome, versao_pet: this.versao_pet, k: this.k, pendente: this.pendencia !== null,
      gestos: Object.fromEntries(Object.entries(this.gestos).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))), modulos, motivos: this.motivos,
    };
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
    const cons = this.afeto.consequencia(pc0, pc1, recs);
    const l0 = recs.map(r => leituraReceptor(pc0 as PercepcaoCorpoLobos, r, S));
    const l1 = recs.map(r => leituraReceptor(pc1, r, S));
    const pos0: readonly [number, number] = p.sens["pos"], pos1: readonly [number, number] = [pm1.x, pm1.y];
    const comeu = ocorrido === null ? null : ocorrido.comeu as Dict | null;
    const classeComida = comeu === null ? null : (comeu["situacao"] === "podre" ? "podre" : comeu["tipo"] as string);
    let p1 = null;
    if (acao === "comer") {
      p1 = this.plast.consequenciaP1("comer", comeu !== null && comeu["como"] === "comer" ? classeComida : null, l0, l1, pos0, pos1, p.g_apr);
    } else if (acao === "brincar") {
      p1 = this.plast.consequenciaP1("brincar", ocorrido!.brincou_com_bola ? "bola" : null, l0, l1, pos0, pos1, p.g_apr);
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
