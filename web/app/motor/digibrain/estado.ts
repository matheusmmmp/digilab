/* M-ESTADO, o estado dinamico: o espelho de digilab/digibrain/estado.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 3 e 4.4; LM2), na forma I
   (integradores com vazamento): a intencao em curso I* = (b, o), o compromisso C, a frustracao F, as decisoes seguidas sem progresso `n_sp`, o
   credito por opcao ao P2 e a DX-4 (a busca pelo cheiro, o "achou" e a opcao composta). Aritmetica inteira, sem rng.
   Ficam fora do laboratorio (LAB-1) e falham alto se ligadas: `intencao_suspensa` (a L-2), `redecidir_evento` (a C3) e `credito_corrida` (a C2). */
import { chaveJson, clamp, ganhoDeTau, mul, type ChaveUnidade } from "./_comum.ts";
import { INATOS_MODULAR } from "./constantes.ts";

export type InatosEstado = typeof INATOS_MODULAR;
/** o que o M-ESTADO le da ConfigDigibrain */
export interface ConfigDigibrainEstado {
  persistencia: boolean; intencao_cheiro: boolean; credito_corrida: boolean; intencao_suspensa: boolean; redecidir_evento: boolean;
}
export interface ConfigEstado { intervalo_decisao_ticks: number }

export const TIPOS_INTENCAO = [["comer", "comida"], ["brincar", "bola"], ["explorar", "ponto"]] as const;
export const BUSCA = ["comer", "cheiro"] as const;   // a intencao da DX-4, so com a subchave `intencao_cheiro`

/** a opcao (a I* ou uma de uma decisao so): a chave, o inicio, a elegibilidade e (os z da decisao que a comecou), o r somado, as decisoes, o g_apr
 *  da ultima e a distancia ao alvo; a I* ainda tem o compromisso C e o `n_sp` */
export interface Opcao {
  chave: ChaveUnidade; inicio: number; e: number[]; r: number; n: number; g_apr: number; d: number | null;
  C?: number; n_sp?: number; composta?: boolean;
}
export type OpcaoFim = Opcao & { motivo: string; meta: boolean | null; credito?: boolean; registro?: boolean };

/** a unidade escolhida como o M-ESTADO a le */
export interface UnidadeEscolhida { chave: ChaveUnidade; d: number | null }
/** o que aconteceu na decisao (`ocorrido` do motor) */
export interface Ocorrido { comeu: { id: number } | null; brincou_com_bola: boolean; chegou: boolean }
/** o que se sabe depois de andar */
export interface DepoisEstado { visto?: boolean; d?: number | null; ha_cheiro: boolean; comida_boa_vista?: boolean }
export interface ContextoEstado { F: number; persistencia: Record<string, number>; I: ChaveUnidade | null; C: number; n_sp: number }

const mesmaChave = (a: ChaveUnidade, b: ChaveUnidade): boolean => JSON.stringify(chaveJson(a)) === JSON.stringify(chaveJson(b));
/** a chave da persistencia (`{texto: h}`), o JSON da chave_json */
const textoChave = (c: ChaveUnidade): string => JSON.stringify(chaveJson(c));

export function eIntencao(chave: ChaveUnidade, intencaoCheiro = false): boolean {
  return TIPOS_INTENCAO.some(([a, t]) => a === chave[0] && t === chave[1]) || (intencaoCheiro && chave[0] === BUSCA[0] && chave[1] === BUSCA[1]);
}

export class EstadoDinamico {
  p: InatosEstado;
  cd: ConfigDigibrainEstado;
  S: number;
  k_c: number;
  k_f_sobe: number;
  k_f_desce: number;
  I: Opcao | null = null;                // a intencao em curso
  opcao: Opcao | null = null;            // a opcao da decisao em curso (a I* ou uma de uma decisao so)
  F = 0;
  fins: Record<string, number> = { meta: 0, trocou: 0, sumiu: 0, desistiu: 0 };
  guardada: OpcaoFim | null = null;      // a busca que acabou em "achou", por uma decisao (DX-4)

  constructor(cfg: ConfigEstado, cfgDigibrain: ConfigDigibrainEstado, inatosOuNulo: InatosEstado | null = null) {
    this.p = inatosOuNulo ?? INATOS_MODULAR;
    this.cd = cfgDigibrain;
    for (const f of ["credito_corrida", "intencao_suspensa", "redecidir_evento"] as const) {
      if (cfgDigibrain[f]) throw new Error(`M-ESTADO: a subchave ${f} fica fora do laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, secao 3)`);
    }
    this.S = this.p.escala;
    const delta = cfg.intervalo_decisao_ticks;
    this.k_c = ganhoDeTau(this.p.tau_c, delta, this.S);
    this.k_f_sobe = ganhoDeTau(this.p.tau_f_sobe, delta, this.S);
    this.k_f_desce = ganhoDeTau(this.p.tau_f_desce, delta, this.S);
    if (cfgDigibrain.intencao_cheiro) this.fins["achou"] = 0;
  }

  contexto(): ContextoEstado {
    this.F = this.F - mul(this.k_f_desce, this.F, this.S);
    const h: Record<string, number> = {};
    if (this.I !== null && this.cd.persistencia) h[textoChave(this.I.chave)] = mul(this.p.w_pers, this.I.C!, this.S);
    return { F: this.F, persistencia: h, I: this.I === null ? null : this.I.chave, C: this.I === null ? 0 : this.I.C!, n_sp: this.I === null ? 0 : this.I.n_sp! };
  }

  private acabar(motivo: string, meta: boolean, frustra = true): OpcaoFim {
    const I = this.I!;
    if (!meta && frustra) this.F = this.F + mul(this.k_f_sobe, this.S - this.F, this.S);
    this.fins[motivo]! += 1;
    this.I = null;
    return { ...I, C: 0, motivo, meta };
  }

  /** a unidade escolhida na decisao k (com a distancia ao alvo, ou null): devolve as opcoes que acabaram por ela (a I* trocada) */
  escolhida(unidade: UnidadeEscolhida, z: readonly number[], gApr: number, k: number, reflexo = false): OpcaoFim[] {
    void reflexo;                                    // so a L-2 (intencao_suspensa) o le; fora do laboratorio
    const chave = unidade.chave;
    const fins: OpcaoFim[] = [];
    if (this.guardada !== null) {
      const busca = this.guardada;
      this.guardada = null;
      if (chave[0] === "comer" && chave[1] === "comida") return this.herdarBusca(busca, unidade, gApr);
      fins.push({ ...busca, registro: false });      // registrada no "achou"; entregue agora, so com a busca
    }
    if (this.I !== null && mesmaChave(this.I.chave, chave)) {
      this.I.C = this.I.C! + mul(this.k_c, this.S - this.I.C!, this.S);
      this.I.n += 1;
      this.I.g_apr = gApr;
      this.I.d = unidade.d;
      this.opcao = this.I;
      return fins;
    }
    if (this.I !== null) fins.push(this.acabar("trocou", false));
    const op: Opcao = { chave, inicio: k, e: [...z], r: 0, n: 1, g_apr: gApr, d: unidade.d };
    if (eIntencao(chave, this.cd.intencao_cheiro)) {
      this.I = { ...op, C: mul(this.k_c, this.S, this.S), n_sp: 0 };
      this.opcao = this.I;
    } else {
      this.opcao = op;
    }
    return fins;
  }

  /** a consequencia da decisao em curso. `depois` = {visto: o alvo nos `vistos` depois de andar, d: a distancia a ele (null sem ele), ha_cheiro,
   *  comida_boa_vista}. Devolve as opcoes que acabaram nela. */
  consequencia(rN: number, ocorrido: Ocorrido | null, depois: DepoisEstado): OpcaoFim[] {
    const op = this.opcao;
    if (op === null) throw new Error("M-ESTADO: consequencia sem a opcao da decisao");
    this.opcao = null;
    op.r = clamp(op.r + rN, -this.S, this.S);
    if (op !== this.I) return [{ ...op, motivo: "unica", meta: null }];
    const [acao, tipo, ident] = op.chave;
    if (acao === BUSCA[0] && tipo === BUSCA[1]) return this.consequenciaBusca(op, ocorrido, depois);
    if (ocorrido !== null && ((acao === "comer" && ocorrido.comeu !== null && ocorrido.comeu.id === ident)
      || (acao === "brincar" && ocorrido.brincou_com_bola) || (acao === "explorar" && ocorrido.chegou))) {
      return [this.acabar("meta", true)];
    }
    if (!depois.visto && !depois.ha_cheiro) return [this.acabar("sumiu", false)];
    if (depois.d !== null && depois.d !== undefined && op.d !== null && depois.d < op.d) op.n_sp = 0;
    else op.n_sp! += 1;
    if (op.n_sp! >= this.p.n_desiste) return [this.acabar("desistiu", false)];
    return [];
  }

  // ------------------------------------------------------------ a DX-4: a busca pelo cheiro e a opcao composta
  /** o fim da busca, so pelo que o cerebro ja le: o consumo, as comidas boas nos `vistos` e se ha cheiro */
  private consequenciaBusca(op: Opcao, ocorrido: Ocorrido | null, depois: DepoisEstado): OpcaoFim[] {
    if (ocorrido !== null && ocorrido.comeu !== null) return [this.acabar("meta", true)];
    if (depois.comida_boa_vista) {
      const fim = this.acabar("achou", false, false);   // o "achou" nao sobe o F (decisao de 2026-10-26)
      this.guardada = fim;
      return [{ ...fim, credito: false }];               // guardada: o credito segue pela opcao composta
    }
    if (!depois.ha_cheiro) return [this.acabar("sumiu", false)];
    op.n_sp! += 1;
    if (op.n >= this.p.n_desiste_cheiro) return [this.acabar("desistiu", false)];
    return [];
  }

  /** a opcao composta: a intencao `comer/comida` com a elegibilidade, o inicio e o r da busca guardada */
  private herdarBusca(busca: OpcaoFim, unidade: UnidadeEscolhida, gApr: number): OpcaoFim[] {
    const op: Opcao = { chave: unidade.chave, inicio: busca.inicio, e: [...busca.e], r: busca.r, n: busca.n + 1, g_apr: gApr, d: unidade.d, composta: true };
    this.I = { ...op, C: mul(this.k_c, this.S, this.S), n_sp: 0 };
    this.opcao = this.I;
    return [];
  }

  // ------------------------------------------------------------ fora do laboratorio
  cuidarSuspensa(): never { throw new Error("M-ESTADO: cuidar_suspensa sem a subchave intencao_suspensa (fora do laboratorio)"); }
  eventos(): never { throw new Error("M-ESTADO: eventos sem a subchave redecidir_evento (fora do laboratorio)"); }
  registrarRedecisao(): never { throw new Error("M-ESTADO: registrar_redecisao sem a subchave redecidir_evento (fora do laboratorio)"); }
  /** a suspensa no registro da decisao: sem a L-2, nunca ha */
  suspensaResumo(): null { return null; }

  estadoInterno(): Record<string, unknown> {
    const I = this.I;
    const out: Record<string, any> = {
      I: I === null ? null : { chave: chaveJson(I.chave), C: I.C, n_sp: I.n_sp, inicio: I.inicio, n: I.n, r: I.r, d: I.d },
      F: this.F, fins: { ...this.fins },
    };
    if (this.cd.intencao_cheiro) {                  // so com a DX-4 (desligada, o estado e o de hoje, byte a byte)
      const g = this.guardada;
      out["guardada"] = g === null ? null : { chave: chaveJson(g.chave), inicio: g.inicio, n: g.n, r: g.r };
      if (I !== null && I.composta) out["I"].composta = true;
    }
    return out;
  }
}
