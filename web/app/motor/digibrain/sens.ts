/* M-SENS, a codificacao sensorial: o espelho de digilab/digibrain/sens.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.1 e 4.2; LM1).
   Le so a Observacao (corpo, mundo, o vetor de estado e os ticks desde o cuidado); a aritmetica e inteira; sem rng. O estado e a habituacao
   por classe: a novidade da decisao sai da habituacao de antes dela, e so depois a habituacao anda. */
import { faltaReceptor, leituraReceptor, type PercepcaoCorpoLobos } from "../lobos.ts";
import { clamp, divArred, ganhoDeTau, integrar } from "./_comum.ts";
import { INATOS_MODULAR, RECEPTORES_DIGIBRAIN, TICKS_POR_DIA } from "./constantes.ts";

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

  constructor(cfg: ConfigSens, cfgMundo: ConfigMundoSens, inatos: InatosSens = INATOS_MODULAR) {
    this.p = inatos;
    this.S = inatos.escala;
    this.cfg = cfg;
    this.raio = cfgMundo.raio_visao_celulas * cfgMundo.sub;
    this.maxVistos = cfgMundo.max_vistos;
    this.kHab = ganhoDeTau(inatos.tau_hab, cfg.intervalo_decisao_ticks, this.S);
    this.hab = { racao: 0, a: 0, b: 0, c: 0, podre: 0, bola: 0 };
  }

  private _receptores(pc: CorpoModular): string[] {
    // os onze do prototipo vem na ordem da PercepcaoCorpo, que e a de RECEPTORES_DIGIBRAIN; qualquer outro receptor presente e de fora
    const presentesTodos = Object.keys(pc).filter(k => pc[k] !== null && pc[k] !== undefined);
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

  codificar(obs: ObservacaoModular, lutas?: readonly ResumoLutaSens[]): SaidaSens {
    const S = this.S, pc = obs.corpo, pm = obs.mundo;
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
    for (const c of CLASSES_OBJETO) this.hab[c] = integrar(this.hab[c], vistas.has(c) ? S : 0, this.kHab, S);   // a habituacao anda depois da novidade
    let comida = 0, bola = 0;
    for (const o of objetos) {
      if ((COMIDAS_BOAS as readonly string[]).includes(o.classe)) comida = Math.max(comida, o.prox);
      else if (o.classe === "bola") bola = Math.max(bola, o.prox);
    }
    const out: SaidaSens = { falta, leitura, contexto, objetos, conjuncoes: { comida_vista: comida, sem_comida: S - comida, bola_vista: bola },
      ha_cheiro: pm.direcao_cheiro !== 0, pos: [pm.x, pm.y], regiao: pm.regiao, minuto, pc };
    if (lutas !== undefined) out.lutas = this.resumirLutas(lutas);      // a ponte da luta (PE3): desligada, nenhum campo novo
    return out;
  }

  estadoInterno(): { hab: Record<string, number>; receptores: string[] | null } {
    return { hab: { ...this.hab }, receptores: this.receptores === null ? null : [...this.receptores] };
  }
}
