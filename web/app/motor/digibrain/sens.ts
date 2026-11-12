/* M-SENS, a codificacao sensorial: o espelho de digilab/digibrain/sens.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.1 e 4.2; LM1).
   Le so a Observacao (corpo, mundo, o vetor de estado e os ticks desde o cuidado); a aritmetica e inteira; sem rng. O estado e a habituacao
   por classe: a novidade da decisao sai da habituacao de antes dela, e so depois a habituacao anda. */
import { faltaReceptor, leituraReceptor, type PercepcaoCorpoLobos } from "../lobos.ts";
import { CANAIS_TELA, RECEPTORES_TELA } from "../tv.ts";
import { clamp, divArred, ganhoDeTau, integrar, mul } from "./_comum.ts";
import { INATOS_MODULAR, RECEPTORES_DIGIBRAIN, TICKS_POR_DIA, type ConfigOlhar } from "./constantes.ts";
import { genomaNaEscala, type GenomaVisao } from "./genoma_visao.ts";
import { RECEPTOR_ENJOO_TELA, type ConfigEnjooTela } from "../enjoo_tela.ts";

/** a classe da TV (so com a subchave `olhar`; GOSTO_VISUAL, P1f) */
export const CLASSE_TELA = "tela";
/** o pico em inteiros sobre a distancia x ao alvo: S em x = 0, 0 a partir de |x| = largura */
export function pico(x: number, largura: number, S: number): number {
  if (!Number.isInteger(largura) || largura <= 0) throw new Error(`M-SENS: largura do pico ${largura}`);
  return Math.max(0, S - divArred(Math.abs(x) * S, largura));
}
/** uma linha da classe `tela` (a TV a vista, do gancho `verTela`) */
export interface LinhaTela { id: number; tipo: "tela"; classe: "tela"; dx: number; dy: number; d: number; prox: number; nov: number }

export const CLASSES_OBJETO = ["racao", "a", "b", "c", "podre", "bola"] as const;
export const COMIDAS_BOAS = ["racao", "a", "b", "c"] as const;
export type ClasseObjeto = (typeof CLASSES_OBJETO)[number];

/** a PercepcaoCorpo: o receptor ausente e null (o gabarito grava os campos todos) */
export type CorpoModular = Readonly<Record<string, number | null | undefined>>;
/** um item dos `vistos`: [id, tipo, dx, dy, d] */
export type VistoModular = readonly [number, string, number, number, number];
export interface MundoModular { x: number; y: number; regiao: number; direcao_cheiro: number; vistos: readonly VistoModular[] }
/** o que o M-SENS le da Observacao do Python (a `_obs_enxuta` do exportador) */
export interface ObservacaoModular {
  corpo: CorpoModular; mundo: MundoModular; vetor_estado: readonly number[]; ticks_desde_cuidado: number;
}

/** o Config e a ConfigMundo que o M-SENS le (CONFIG_MODULAR_MUNDO) */
export interface ConfigSens { intervalo_decisao_ticks: number; inicio_noite_tick: number; fim_noite_tick: number }
export interface ConfigMundoSens { sub: number; raio_visao_celulas: number; max_vistos: number }
export type InatosSens = Pick<typeof INATOS_MODULAR, "escala" | "tau_hab" | "escala_cuidado">;

export interface ObjetoSens { id: number; tipo: string; classe: ClasseObjeto; dx: number; dy: number; d: number; prox: number; nov: number }
export interface SaidaSens {
  falta: Record<string, number>; leitura: Record<string, number>;
  contexto: { noite: number; dormindo: number; sem_cuidado: number };
  objetos: ObjetoSens[];
  conjuncoes: { comida_vista: number; sem_comida: number; bola_vista: number };
  ha_cheiro: boolean; pos: readonly [number, number]; regiao: number; minuto: number; pc: CorpoModular;
  /** a ponte da luta (PE3): os resumos desde a decisao anterior; so com a `luta_memoria` (desligada, o campo nao existe) */
  lutas?: ResumoLutaSens[];
  /** a tela (P1f; so com a subchave `olhar`): as TVs a vista, os niveis lidos e a novidade do corpo */
  telas?: LinhaTela[];
  tela_niveis?: Record<string, number> | null;
  tela_novidade?: number | null;
  tela_enjoo?: number | null;              // o enjoo (D-GV-ENJOO-CER), so com a ConfigEnjooTela ligada
}
/** o resumo da luta na Observacao: em inteiros (o rival, o resultado -1, 0, +1, a vida perdida em S e o tick) */
export interface ResumoLutaSens { rival: string; resultado: number; vida_perdida_s: number; tick: number }

/** Config.e_noite */
export function eNoite(cfg: ConfigSens, tickDoDia: number): boolean {
  if (cfg.inicio_noite_tick > cfg.fim_noite_tick) return tickDoDia >= cfg.inicio_noite_tick || tickDoDia < cfg.fim_noite_tick;
  return cfg.inicio_noite_tick <= tickDoDia && tickDoDia < cfg.fim_noite_tick;
}

/** o `round` do Python (meio para o par) */
function arredondarPar(x: number): number {
  const f = Math.floor(x), d = x - f;
  if (d < 0.5) return f;
  if (d > 0.5) return f + 1;
  return f % 2 === 0 ? f : f + 1;
}

/** a classe do item dos `vistos`: o tipo maduro, `podre` (qualquer `_podre`) ou `bola` */
export function classeDoTipo(tipo: string): ClasseObjeto {
  if (tipo.endsWith("_podre")) return "podre";
  if (!(CLASSES_OBJETO as readonly string[]).includes(tipo)) throw new Error(`M-SENS: tipo de objeto desconhecido '${tipo}'`);
  return tipo as ClasseObjeto;
}

/** o M-SENS */
export class Sens {
  p: InatosSens;
  S: number;
  cfg: ConfigSens;
  raio: number;
  maxVistos: number;
  kHab: number;
  hab: Record<ClasseObjeto, number>;
  /** os receptores presentes, fixados na primeira decisao */
  receptores: string[] | null = null;
  /** a tela (P1f): so com a subchave `olhar` (null desligada) */
  readonly olhar: ConfigOlhar | null = null;
  otimo: Record<string, number> = {};
  largura: Record<string, number> = {};
  desloc: Record<string, number> = {};
  kExpo = 0;
  exposicoes = 0;
  telaPresente: boolean | null = null;
  /** o enjoo (D-GV-ENJOO-CER): so com o olhar e a ConfigEnjooTela ligada (null desligado) */
  readonly enjoo: ConfigEnjooTela | null = null;

  constructor(cfg: ConfigSens, cfgMundo: ConfigMundoSens, inatos: InatosSens = INATOS_MODULAR, olhar: ConfigOlhar | null = null,
              genoma: GenomaVisao | null = null, enjoo: ConfigEnjooTela | null = null) {
    this.p = inatos;
    this.S = inatos.escala;
    this.cfg = cfg;
    this.raio = cfgMundo.raio_visao_celulas * cfgMundo.sub;
    this.maxVistos = cfgMundo.max_vistos;
    this.kHab = ganhoDeTau(inatos.tau_hab, cfg.intervalo_decisao_ticks, this.S);
    this.hab = { racao: 0, a: 0, b: 0, c: 0, podre: 0, bola: 0 };
    if ((olhar === null) !== (genoma === null)) throw new Error("M-SENS: a ConfigOlhar e o GenomaVisao vem juntos (so com a subchave `olhar`)");
    if (olhar !== null) {
      this.olhar = olhar;
      (this.hab as Record<string, number>)[CLASSE_TELA] = 0;
      [this.otimo, this.largura] = genomaNaEscala(genoma!, this.S, olhar.escala);
      this.desloc = Object.fromEntries(CANAIS_TELA.map(c => [c, 0]));
      this.kExpo = ganhoDeTau(olhar.tau_exposicao, cfg.intervalo_decisao_ticks, this.S);
    }
    if (enjoo !== null && enjoo.ligada) {
      if (olhar === null) throw new Error("M-SENS: o enjoo (ConfigEnjooTela ligada) so com a subchave olhar");
      this.enjoo = enjoo;
    }
  }

  /** a TV no jogo (D-GV-TVJOGO-3): as linhas da TV fora do raio, so com `ligarIrAteTv` */
  irAteTv = false;
  /** a decisao D (so com a subchave `olhar`): o motor manda a linha da TV tambem fora do raio da visao. A linha longe tem a proximidade 0 e
   *  nao conta como vista na habituacao da classe `tela` */
  ligarIrAteTv(): void { this.exigirOlhar("ligar_ir_ate_tv"); this.irAteTv = true; }
  /** a linha da TV esta fora do raio da visao (so com o ir ate a TV) */
  longe(linha: { d: number }): boolean { return linha.d > this.raio; }

  // ------------------------------------------------------------ a tela (P1f, so com a subchave `olhar`)
  private exigirOlhar(onde: string): ConfigOlhar {
    if (this.olhar === null) throw new Error(`M-SENS: ${onde} sem a subchave olhar`);
    return this.olhar;
  }

  /** os niveis da tela na percepcao do corpo (canal -> [0, S]), ou null sem os receptores da tela */
  niveisTela(pc: CorpoModular): Record<string, number> | null {
    this.exigirOlhar("niveis_tela");
    if (pc["tela_cor"] === null || pc["tela_cor"] === undefined) return null;
    const niveis = Object.fromEntries(CANAIS_TELA.map(c => [c, pc[`tela_${c}`] as number]));
    if (Object.values(niveis).some(v => !Number.isInteger(v) || v < 0 || v > this.S)) throw new Error(`M-SENS: niveis da tela fora de [0, S]: ${JSON.stringify(niveis)}`);
    return niveis;
  }

  private agradoCom(niveis: Readonly<Record<string, number>>, desloc: Readonly<Record<string, number>>): number {
    if (Object.keys(niveis).join() !== CANAIS_TELA.join()) throw new Error(`M-SENS: os niveis da tela por canal, na ordem ${CANAIS_TELA}`);
    let soma = 0;
    for (const c of CANAIS_TELA) soma += pico(niveis[c]! - (this.otimo[c]! + desloc[c]!), this.largura[c]!, this.S);
    return divArred(soma, CANAIS_TELA.length);
  }

  /** o agrado do nivel visto contra o alvo (o otimo do genoma mais o deslocamento da exposicao), em [0, S] */
  agrado(niveis: Readonly<Record<string, number>>): number { this.exigirOlhar("agrado"); return this.agradoCom(niveis, this.desloc); }

  /** o agrado do nivel visto contra o otimo do genoma so */
  agradoInato(niveis: Readonly<Record<string, number>>): number {
    this.exigirOlhar("agrado_inato");
    return this.agradoCom(niveis, Object.fromEntries(CANAIS_TELA.map(c => [c, 0])));
  }

  /** a exposicao: o alvo de cada canal anda para o nivel visto, com o teto do deslocamento (so quando o pet olhou) */
  expor(niveis: Readonly<Record<string, number>>, enjoo: number | null = null): void {
    const co = this.exigirOlhar("expor"), S = this.S;
    let fator: number | null = null;
    if (this.enjoo !== null) {                         // o enjoo (D-GV-ENJOO-CER): o passo cai a zero na saturacao
      this.conferirEnjoo(enjoo);
      fator = Math.max(0, S - divArred(enjoo! * S, this.enjoo.saturacao_exposicao));
    } else if (enjoo !== null) throw new Error("M-SENS: o enjoo na exposicao sem a ConfigEnjooTela ligada");
    for (const c of CANAIS_TELA) {
      const alvo = this.otimo[c]! + this.desloc[c]!;
      let passo = mul(this.kExpo, niveis[c]! - alvo, S);
      if (fator !== null) passo = mul(fator, passo, S);
      this.desloc[c] = clamp(this.desloc[c]! + passo, -co.teto_exposicao, co.teto_exposicao);
    }
    this.exposicoes += 1;
  }

  private conferirEnjoo(enjoo: unknown): void {
    if (!Number.isInteger(enjoo) || (enjoo as number) < 0 || (enjoo as number) > this.S) throw new Error(`M-SENS: o enjoo da tela e inteiro em [0, S]: ${String(enjoo)}`);
  }

  /** o tedio do enjoo (D-GV-ENJOO-CER), em [0, peso_tedio]: 0 ate a saturacao, mul(peso_tedio, (e - sat)/(S - sat)) acima */
  tedio(enjoo: number): number {
    if (this.enjoo === null) throw new Error("M-SENS: o tedio sem a ConfigEnjooTela ligada");
    this.conferirEnjoo(enjoo);
    const S = this.S, sat = this.enjoo.saturacao_exposicao;
    return mul(this.enjoo.peso_tedio, divArred(Math.max(0, enjoo - sat) * S, S - sat), S);
  }

  /** o agrado do nivel visto menos o tedio do enjoo (D-GV-ENJOO-CER), em [0, S] */
  agradoEfetivo(niveis: Readonly<Record<string, number>>, enjoo: number): number {
    this.exigirOlhar("agrado_efetivo");
    return Math.max(0, this.agrado(niveis) - this.tedio(enjoo));
  }

  private linhasTela(telas: readonly (readonly number[])[]): LinhaTela[] {
    const S = this.S, nov = S - (this.hab as Record<string, number>)[CLASSE_TELA]!;
    const out = telas.map(l => {
      if (l.length !== 4 || l.some(v => !Number.isInteger(v)) || l[3]! < 0) throw new Error(`M-SENS: linha da tela malformada: ${JSON.stringify(l)}`);
      const [id, dx, dy, d] = l as [number, number, number, number];
      if (d > this.raio && !this.irAteTv) throw new Error(`M-SENS: linha da tela fora do raio da visao (${d} > ${this.raio}) sem o ir ate a TV`);
      return { id, tipo: CLASSE_TELA, classe: CLASSE_TELA, dx, dy, d, prox: this.proximidade(d), nov } as LinhaTela;
    });
    if (new Set(out.map(o => o.id)).size !== out.length) throw new Error("M-SENS: duas linhas da tela com o mesmo id");
    return out;
  }

  private _receptores(pc: CorpoModular): string[] {
    // os onze do prototipo vem na ordem da PercepcaoCorpo, que e a de RECEPTORES_DIGIBRAIN; qualquer outro receptor presente e de fora
    let presentesTodos = Object.keys(pc).filter(k => pc[k] !== null && pc[k] !== undefined);
    if (this.olhar !== null) {                         // a tela (P1f): os receptores dela ficam a parte, fora dos `receptores`
      const tela = RECEPTORES_TELA.filter(r => presentesTodos.includes(r));
      if (tela.length && tela.length !== RECEPTORES_TELA.length) throw new Error(`M-SENS: os receptores da tela vem todos juntos: ${tela}`);
      if (this.telaPresente === null) this.telaPresente = tela.length > 0;
      else if ((tela.length > 0) !== this.telaPresente) throw new Error("M-SENS: os receptores da tela mudaram desde a primeira decisao");
      const enjoo = presentesTodos.includes(RECEPTOR_ENJOO_TELA);
      if (this.enjoo !== null && this.telaPresente && !enjoo) throw new Error("M-SENS: o enjoo ligado (ConfigEnjooTela) sem o receptor enjoo_tela do corpo");
      if (enjoo && !tela.length) throw new Error("M-SENS: o receptor enjoo_tela sem os receptores da tela");
      presentesTodos = presentesTodos.filter(r => !(RECEPTORES_TELA as readonly string[]).includes(r) && r !== RECEPTOR_ENJOO_TELA);
    }
    const fora = presentesTodos.filter(r => !(RECEPTORES_DIGIBRAIN as readonly string[]).includes(r));
    if (fora.length) throw new Error(`M-SENS: receptores fora do prototipo (os orgaos, o paladar, o banheiro; espec, secao 6): ${fora}`);
    const presentes = RECEPTORES_DIGIBRAIN.filter(r => presentesTodos.includes(r)) as string[];
    if (this.receptores === null) this.receptores = [...presentes];
    else if (presentes.join() !== this.receptores.join()) throw new Error(`M-SENS: receptores ${presentes}, na primeira decisao ${this.receptores}`);
    return presentes;
  }

  proximidade(d: number): number {
    return clamp(this.S - divArred(d * this.S, this.raio), 0, this.S);
  }

  /** o resumo da luta na Observacao (ponte da luta, PE3; espelho de `Sens.resumir_lutas`): na ordem; falha alto num resumo malformado */
  resumirLutas(lutas: readonly ResumoLutaSens[]): ResumoLutaSens[] {
    return lutas.map(r => {
      if (typeof r.rival !== "string" || r.rival === "" || ![-1, 0, 1].includes(r.resultado) || !Number.isInteger(r.resultado)
          || !Number.isInteger(r.vida_perdida_s) || r.vida_perdida_s < 0 || !Number.isInteger(r.tick)) {
        throw new Error(`M-SENS: resumo da luta malformado ${JSON.stringify(r)}`);
      }
      return { rival: r.rival, resultado: r.resultado, vida_perdida_s: r.vida_perdida_s, tick: r.tick };
    });
  }

  codificar(obs: ObservacaoModular, lutas?: readonly ResumoLutaSens[] | null, telas?: readonly (readonly number[])[]): SaidaSens {
    const S = this.S, pc = obs.corpo, pm = obs.mundo;
    if (telas !== undefined && this.olhar === null) throw new Error("M-SENS: as linhas da tela sem a subchave olhar");
    const recs = this._receptores(pc);
    const pcl = pc as PercepcaoCorpoLobos;
    const falta: Record<string, number> = {}, leitura: Record<string, number> = {};
    for (const r of recs) falta[r] = faltaReceptor(pcl, r, S);
    for (const r of recs) leitura[r] = leituraReceptor(pcl, r, S);
    const hora = obs.vetor_estado[7]!, dormindo = obs.vetor_estado[6]!;
    const minuto = ((arredondarPar(hora * TICKS_POR_DIA) % TICKS_POR_DIA) + TICKS_POR_DIA) % TICKS_POR_DIA;
    const ticks = obs.ticks_desde_cuidado;
    if (!Number.isInteger(ticks) || ticks < 0) throw new Error(`M-SENS: ticks_desde_cuidado ${ticks}`);
    const contexto = {
      noite: eNoite(this.cfg, minuto) ? S : 0, dormindo: dormindo !== 0 ? S : 0,
      sem_cuidado: Math.min(S, divArred(ticks * S, this.p.escala_cuidado)),
    };
    if (pm.vistos.length > this.maxVistos) throw new Error(`M-SENS: ${pm.vistos.length} vistos, o maximo e ${this.maxVistos}`);
    const objetos: ObjetoSens[] = [];
    const vistas = new Set<ClasseObjeto>();
    for (const [id, tipo, dx, dy, d] of pm.vistos) {
      const c = classeDoTipo(tipo);
      vistas.add(c);
      objetos.push({ id, tipo, classe: c, dx, dy, d, prox: this.proximidade(d), nov: S - this.hab[c] });
    }
    const linhasTela = this.olhar !== null ? this.linhasTela(telas ?? []) : null;
    for (const c of CLASSES_OBJETO) this.hab[c] = integrar(this.hab[c], vistas.has(c) ? S : 0, this.kHab, S);   // a habituacao anda depois da novidade
    if (linhasTela !== null) {                         // a classe `tela` (P1f), no fim, com a mesma regra
      const h = this.hab as Record<string, number>;
      /* o ir ate a TV (D-GV-TVJOGO-3): a linha longe nao conta como vista (sem ele, toda linha esta no raio: a conta de hoje) */
      h[CLASSE_TELA] = integrar(h[CLASSE_TELA]!, linhasTela.some(o => !this.longe(o)) ? S : 0, this.kHab, S);
    }
    let comida = 0, bola = 0;
    for (const o of objetos) {
      if ((COMIDAS_BOAS as readonly string[]).includes(o.classe)) comida = Math.max(comida, o.prox);
      else if (o.classe === "bola") bola = Math.max(bola, o.prox);
    }
    const out: SaidaSens = { falta, leitura, contexto, objetos, conjuncoes: { comida_vista: comida, sem_comida: S - comida, bola_vista: bola },
      ha_cheiro: pm.direcao_cheiro !== 0, pos: [pm.x, pm.y], regiao: pm.regiao, minuto, pc };
    if (lutas !== undefined && lutas !== null) out.lutas = this.resumirLutas(lutas);      // a ponte da luta (PE3): desligada, nenhum campo novo
    if (linhasTela !== null) {                         // a tela (P1f): desligada, nenhum campo novo
      out.telas = linhasTela;
      out.tela_niveis = this.niveisTela(pc);
      out.tela_novidade = (pc["novidade_tela"] ?? null) as number | null;
      if (this.enjoo !== null) {                       // o enjoo (D-GV-ENJOO-CER): desligado, nenhum campo novo
        const e = (pc[RECEPTOR_ENJOO_TELA] ?? null) as number | null;
        if (e !== null) this.conferirEnjoo(e);
        out.tela_enjoo = e;
      }
    }
    return out;
  }

  estadoInterno(): Record<string, unknown> {
    const out: Record<string, unknown> = { hab: { ...this.hab }, receptores: this.receptores === null ? null : [...this.receptores] };
    if (this.olhar !== null) {                         // a tela (P1f): desligada, o estado de hoje, byte a byte
      out["tela"] = { otimo: { ...this.otimo }, largura: { ...this.largura }, desloc: { ...this.desloc }, exposicoes: this.exposicoes };
    }
    return out;
  }
}
