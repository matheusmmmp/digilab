/* M-MEM, a memoria: o espelho de digilab/digibrain/mem.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.6 e 9; docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md; LM3).
   Dois pedacos: o lugar lembrado (os episodios de alimentacao e de visita, `codificar` e `recuperar`, a `casa` do impulso) e a `memoria_autobio`
   no braco REL da C4 (o episodio completo, o tick, a lembranca, o lugar pela soma, a consolidacao e o termo `L`). Aritmetica inteira (`divArred`,
   `mul`), sem rng. O estado e o do Python (`estadoInterno`), campo a campo.
   Ficam fora do laboratorio (LAB-1) e falham alto: as `facetas_mem` (`evidenciaFaceta`, `classesComPositivo`) e os bracos de pesquisa do
   `controle_mem` (sem, rec, emb, rel_sem_neg); os ganchos do M-PERS ficam vazios. */
import { divArred, mul, raizInteira } from "./_comum.ts";
import { INATOS_MODULAR, TICKS_POR_DIA } from "./constantes.ts";
import type { AlvoImpulso, TermoLembranca } from "./impulso.ts";
import type { SaidaSens } from "./sens.ts";

export const COMIDAS_BOAS = ["racao", "a", "b", "c"] as const;
export const CLASSES_EPISODIO = ["racao", "a", "b", "c", "podre", "nao_havia"] as const;
export const ORIGENS = ["consumo", "visita"] as const;
export const CLASSES_AUTOBIO = [...CLASSES_EPISODIO, "bola", "sem_alvo"] as const;
export const ORIGENS_AUTOBIO = ["consumo", "visita", "evento"] as const;
/** a origem a mais da ponte da luta (PE3; so com a `luta_memoria`): `luta` */
export const ORIGEM_LUTA = "luta";
/** os receptores cuja subida conta para o `theta_sig` (3.3) */
export const AFETIVOS = ["dor", "susto", "estresse"] as const;
/** TIPOS_ALVO_DIGIBRAIN (digilab/config.py): a ordem das classes a vista no episodio */
export const TIPOS_ALVO_DIGIBRAIN = ["racao", "a", "b", "c", "podre", "bola", "cheiro", "vagar", "ponto"] as const;

export type InatosMem = typeof INATOS_MODULAR;
/** o que o M-MEM le da ConfigDigibrain */
export interface ConfigDigibrainMem { memoria_autobio: boolean; controle_mem: string; facetas_mem?: boolean; olhar?: boolean }
export interface ConfigMundoMem { sub: number }

type Dict = Record<string, any>;

/** o episodio do lugar lembrado (sem o id): os campos que o `adapt.py` monta */
export interface EntradaEpisodio {
  classe: string; origem: string; decisao: number; ponto: readonly [number, number]; r: number; r_n: number; regiao: number;
  delta: Record<string, number>; fome_antes: number | null; hora: number;
}
export interface Episodio extends EntradaEpisodio { id: number; lugar: [number, number]; ponto: any }
/** o episodio completo (M0) guardado na recente, na duradoura ou na central */
export interface EpisodioAutobio {
  decisao: number; tick: number; ponto: any; regiao: number; vista: string[]; cheiro: boolean; noite: boolean; acao: [string, string | null, any] | [string, string];
  objeto: { id: number; classe: string } | null; dono: string[]; outro: string | null; corpo_antes: Record<string, number>;
  corpo_depois: Record<string, number>; delta: Record<string, number>; V_antes: number; V_depois: number; E_antes: number; E_depois: number;
  r: number; r_n: number; sigma: number; classe: string; origem: string; categoria: [string, string, number]; resultado?: number; vida_perdida_s?: number; fome_antes: number | null;
  hora: number; rep: number; rec: number; memoria: string; id?: number; lugar?: [number, number];
}
export interface Lembrado { recuperado: number | null; sim: number; memoria: string | null; sigma: number }
export interface Recuperacao {
  pista: boolean; recuperado: number | null; lugar: number[] | null; ponto: readonly [number, number] | null; valor: number; M: number; nota?: number;
}

/** a faixa em quartos de S: quantos limites (S/4, S/2, 3S/4) o valor alcanca */
function faixa(v: number, S: number): number {
  return Number(v >= Math.floor(S / 4)) + Number(v >= Math.floor(S / 2)) + Number(v >= Math.floor(3 * S / 4));
}
const sinal = (v: number): number => Number(v > 0) - Number(v < 0);

/** a comparacao de tuplas de inteiros do Python (lexicografica) */
function cmp(a: readonly number[], b: readonly number[]): number {
  for (let i = 0; i < a.length; i++) {
    if (a[i]! !== b[i]!) return a[i]! < b[i]! ? -1 : 1;
  }
  return 0;
}

/** o item do `sens` da decisao (a comida, a bola) que a unidade escolhida tem, ou null */
export interface UnidadeEpisodio { chave: readonly [string, string | null, any]; objeto: { id: number; classe: string } | null | undefined }
export interface Desfecho { comeu: string | null; chegou: boolean; r_ida: number | null }
export interface ConsEpisodio { V: number; E: number; r: number; r_n: number }

/** o episodio completo (M0) do evento, ou null se ele nao vira episodio (M1): a docstring do modulo Python. `gestos` = [[gesto, tick], ...] */
export function episodioAutobio(
  sens: Pick<SaidaSens, "objetos" | "ha_cheiro" | "contexto" | "falta" | "minuto">, pm1: { x: number; y: number; regiao: number },
  recs: readonly string[], l0: readonly number[], l1: readonly number[], afetoAntes: { V: number; E: number }, cons: ConsEpisodio,
  gestos: readonly (readonly [string, ...unknown[]])[], unidade: UnidadeEpisodio, desfecho: Desfecho, k: number, tick: number,
  p: Pick<InatosMem, "theta_sig">,
): EpisodioAutobio | null {
  const [acao, tipo, ident] = unidade.chave;
  const corpoAntes: Record<string, number> = {}, corpoDepois: Record<string, number> = {};
  const n = Math.min(recs.length, l0.length, l1.length);
  for (let i = 0; i < n; i++) { corpoAntes[recs[i]!] = l0[i]!; corpoDepois[recs[i]!] = l1[i]!; }
  let origem: string, classe: string, sigma: number, ponto: [number, number];
  if (desfecho.comeu !== null) {
    origem = "consumo"; classe = desfecho.comeu; sigma = cons.r_n; ponto = [pm1.x, pm1.y];
  } else if (tipo === "ponto" && desfecho.chegou) {
    if (typeof desfecho.r_ida !== "number" || !Number.isInteger(desfecho.r_ida)) throw new Error(`M-MEM: a visita sem o r da ida: ${JSON.stringify(desfecho)}`);
    origem = "visita"; classe = "nao_havia"; sigma = Math.min(0, desfecho.r_ida); ponto = [ident[0], ident[1]];
  } else {
    let subida = 0;                                  // a queda nao conta
    for (const r of AFETIVOS) if (r in corpoDepois) subida = Math.max(subida, corpoDepois[r]! - corpoAntes[r]!);
    if (Math.abs(cons.r_n) < p.theta_sig && subida < p.theta_sig) return null;
    origem = "evento"; classe = "sem_alvo"; sigma = cons.r_n; ponto = [pm1.x, pm1.y];
  }
  const o = unidade.objeto ?? null;                  // o item do `sens` da decisao ou null
  const objeto = o === null ? null : { id: o.id, classe: o.classe };
  if (objeto !== null && origem === "evento") classe = objeto.classe;
  const visita = origem === "visita";
  const vistas = new Set(sens.objetos.map(x => x.classe as string));
  const delta: Record<string, number> = {};
  for (let i = 0; i < n; i++) delta[recs[i]!] = l1[i]! - l0[i]!;
  return {
    decisao: k, tick, ponto, regiao: pm1.regiao, vista: TIPOS_ALVO_DIGIBRAIN.filter(c => vistas.has(c)), cheiro: Boolean(sens.ha_cheiro),
    noite: sens.contexto.noite > 0, acao: [acao, tipo, ident], objeto, dono: gestos.map(g => g[0]), outro: null, corpo_antes: corpoAntes,
    corpo_depois: corpoDepois, delta, V_antes: afetoAntes.V, V_depois: cons.V, E_antes: afetoAntes.E, E_depois: cons.E,
    r: visita ? 0 : cons.r, r_n: visita ? 0 : cons.r_n, sigma, classe, origem, categoria: [acao, classe, sinal(sigma)],
    fome_antes: sens.falta["fome"] ?? null, hora: sens.minuto, rep: 0, rec: 0, memoria: "recente",
  };
}

/** o resumo pronto de uma luta na Observacao (ponte da luta, PE3; espelho de `Sens.resumir_lutas`): em inteiros */
export interface ResumoLuta { rival: string; resultado: number; vida_perdida_s: number; tick: number }

/** o episodio da luta (ponte da luta, PE3; espelho de `mem.episodio_luta`), ou null se ela nao vira episodio: a regra de hoje, sem limiar novo
 *  (|sigma| ou a subida da dor, do susto ou do estresse >= `theta_sig`). `afeto` e o V e o E de agora (a luta nao os mexe), `cons` o r e o r_n */
export function episodioLuta(
  sens: Pick<SaidaSens, "objetos" | "ha_cheiro" | "contexto" | "falta" | "minuto" | "pos" | "regiao">, recs: readonly string[], l0: readonly number[],
  l1: readonly number[], afeto: { V: number; E: number }, cons: { r: number; r_n: number }, resumo: ResumoLuta, k: number, tick: number,
  p: Pick<InatosMem, "theta_sig">,
): EpisodioAutobio | null {
  const corpoAntes: Record<string, number> = {}, corpoDepois: Record<string, number> = {};
  const n = Math.min(recs.length, l0.length, l1.length);
  for (let i = 0; i < n; i++) { corpoAntes[recs[i]!] = l0[i]!; corpoDepois[recs[i]!] = l1[i]!; }
  let subida = 0;
  for (const r of AFETIVOS) if (r in corpoDepois) subida = Math.max(subida, corpoDepois[r]! - corpoAntes[r]!);
  if (Math.abs(cons.r_n) < p.theta_sig && subida < p.theta_sig) return null;
  const rival = resumo.rival, sigma = cons.r_n;
  const vistas = new Set(sens.objetos.map(x => x.classe as string));
  const delta: Record<string, number> = {};
  for (let i = 0; i < n; i++) delta[recs[i]!] = l1[i]! - l0[i]!;
  return {
    decisao: k, tick, ponto: [sens.pos[0], sens.pos[1]], regiao: sens.regiao, vista: TIPOS_ALVO_DIGIBRAIN.filter(c => vistas.has(c)),
    cheiro: Boolean(sens.ha_cheiro), noite: sens.contexto.noite > 0, acao: ["lutar", rival], objeto: null, dono: [], outro: rival,
    corpo_antes: corpoAntes, corpo_depois: corpoDepois, delta, V_antes: afeto.V, V_depois: afeto.V, E_antes: afeto.E, E_depois: afeto.E,
    r: cons.r, r_n: cons.r_n, sigma, classe: rival, origem: ORIGEM_LUTA, categoria: ["lutar", rival, sinal(sigma)],
    resultado: resumo.resultado, vida_perdida_s: resumo.vida_perdida_s,
    fome_antes: sens.falta["fome"] ?? null, hora: sens.minuto, rep: 0, rec: 0, memoria: "recente",
  };
}

export class Memoria {
  p: InatosMem;
  S: number;
  sub: number;
  episodios: Episodio[] = [];
  proximo_id = 0;
  saidas: { id: number; r: number }[] = [];
  recuperacoes = 0;
  autobio: boolean;
  controle = "rel";
  recente: EpisodioAutobio[] = [];
  duradoura: EpisodioAutobio[] = [];
  central: EpisodioAutobio[] = [];
  consolidacoes: Dict[] = [];
  dia_consolidado = 0;
  lembrancas = 0;
  proximo_id_autobio = 0;
  saidas_autobio: { id: number; sigma: number }[] = [];
  dia = 0;
  minuto: number | null = null;
  /** a ponte da luta (PE3): a origem `luta`; desligada, nenhum campo novo */
  luta: boolean;
  /** as classes do episodio completo: as de hoje e, com a subchave `olhar` (P1f, D-GV-P1f-1), a `tela` */
  readonly classesAutobio: readonly string[];

  constructor(cfgMundo: ConfigMundoMem, inatosOuNulo: InatosMem | null, cd: ConfigDigibrainMem, luta = false) {
    this.p = inatosOuNulo ?? INATOS_MODULAR;
    this.S = this.p.escala;
    this.sub = cfgMundo.sub;
    if (cd.facetas_mem) throw new Error("M-MEM: facetas_mem fica fora do laboratorio (LAB-1)");
    if (cd.controle_mem !== "rel") throw new Error(`M-MEM: o controle_mem ${JSON.stringify(cd.controle_mem)} e controle de pesquisa, fora do laboratorio (so "rel")`);
    this.autobio = cd.memoria_autobio;
    this.luta = luta;
    this.classesAutobio = cd.olhar ? [...CLASSES_AUTOBIO, "tela"] : [...CLASSES_AUTOBIO];
    if (luta && !cd.memoria_autobio) throw new Error("M-MEM: a origem luta so com a memoria_autobio");
  }

  lugarDe(x: number, y: number): [number, number] {
    return [Math.floor(x / this.sub), Math.floor(y / this.sub)];
  }

  /** o alcance da memoria de lugar passa a ser `dMax` subunidades (docs/TAREFA_V3_ILHA_AGUA.md, secao 12.16, IG6; a ilha grande; o
   *  Memoria.alcance do Python). So o parametro muda: os episodios guardados ficam como estao. Inteiro positivo; outro valor falha alto */
  alcance(dMax: number): void {
    if (typeof dMax !== "number" || !Number.isInteger(dMax) || dMax <= 0) throw new Error(`M-MEM: o alcance da memoria e um inteiro positivo de subunidades: ${String(dMax)}`);
    this.p = { ...this.p, d_max: dMax } as typeof this.p;
  }

  /** a ida do mundo para a ilha maior (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG4; a IG-7: "deslocados junto com o lar"; o
   *  Memoria.deslocar do Python): cada lugar lembrado anda (dx, dy), como o pet, a comida e a bola. `ajustar(x, y)` devolve o ponto que
   *  vale no mundo novo (dentro do mapa e, se cair em celula fechada, na terra mais perto) e `regiaoDe(x)` o indice da regiao dele; o
   *  lugar e refeito do ponto. Vale para o lugar lembrado e para a memoria autobiografica (as tres camadas). Nada mais do episodio muda.
   *  Devolve quantos episodios andaram */
  deslocar(dx: number, dy: number, ajustar: (x: number, y: number) => [number, number], regiaoDe: (x: number) => number): number {
    const listas: { ponto: any; lugar?: [number, number]; regiao: number }[][] = this.autobio
      ? [this.episodios, this.recente, this.duradoura, this.central] : [this.episodios];
    let n = 0;
    for (const lista of listas) for (const e of lista) {
      const [x, y] = ajustar(e.ponto[0] + dx, e.ponto[1] + dy);
      e.ponto = [x, y]; e.lugar = this.lugarDe(x, y); e.regiao = regiaoDe(x);
      n++;
    }
    return n;
  }

  /** guarda o episodio (sem o id) e devolve o id */
  codificar(ep: EntradaEpisodio): number {
    if (!(CLASSES_EPISODIO as readonly string[]).includes(ep.classe) || !(ORIGENS as readonly string[]).includes(ep.origem)) {
      throw new Error(`M-MEM: episodio ${JSON.stringify(ep)}`);
    }
    if (ep.origem === "visita" && (ep.r !== 0 || ep.classe !== "nao_havia")) throw new Error("M-MEM: a visita sem comida tem r = 0 e a classe nao_havia");
    if (this.episodios.length >= this.p.n_ep) {
      const sai = this.episodios.reduce((a, b) => (cmp([Math.abs(b.r), b.decisao, b.id], [Math.abs(a.r), a.decisao, a.id]) < 0 ? b : a));
      this.episodios.splice(this.episodios.indexOf(sai), 1);
      this.saidas.push({ id: sai.id, r: sai.r });
    }
    const novo: Episodio = { ...ep, id: this.proximo_id, lugar: this.lugarDe(ep.ponto[0], ep.ponto[1]), ponto: [ep.ponto[0], ep.ponto[1]] };
    this.proximo_id += 1;
    this.episodios.push(novo);
    return novo.id;
  }

  // ------------------------------------------------------------ a C4, M0 e M1 (so com a `memoria_autobio`)
  /** o tick da decisao pelo relogio do pet: o dia avanca quando a hora do dia volta */
  relogio(minuto: number): number {
    if (!this.autobio) throw new Error("M-MEM: o relogio do episodio so com a memoria_autobio");
    if (!Number.isInteger(minuto) || !(minuto >= 0 && minuto < TICKS_POR_DIA)) throw new Error(`M-MEM: a hora do dia ${minuto}`);
    if (this.minuto !== null && minuto < this.minuto) this.dia += 1;
    this.minuto = minuto;
    return this.dia * TICKS_POR_DIA + minuto;
  }

  /** guarda o episodio completo (de `episodioAutobio`) na recente e devolve o id */
  codificarAutobio(ep: EpisodioAutobio): number {
    if (!this.autobio) throw new Error("M-MEM: o episodio completo so com a memoria_autobio");
    if (ep.origem === ORIGEM_LUTA) {                  // a ponte da luta (PE3): a classe e o rival, e o outro tambem
      if (!this.luta || typeof ep.outro !== "string" || ep.outro === "" || ep.classe !== ep.outro) throw new Error(`M-MEM: episodio de luta ${JSON.stringify(ep)}`);
    } else if (!this.classesAutobio.includes(ep.classe) || !(ORIGENS_AUTOBIO as readonly string[]).includes(ep.origem)) {
      throw new Error(`M-MEM: episodio ${JSON.stringify(ep)}`);
    }
    if (ep.origem === "visita" && (ep.sigma > 0 || ep.classe !== "nao_havia")) throw new Error("M-MEM: a visita sem comida tem sigma <= 0 e a classe nao_havia");
    const lugar = this.lugarDe(ep.ponto[0], ep.ponto[1]);
    const categoria = JSON.stringify(ep.categoria);
    for (const e of this.guardados()) {                // a repeticao: a mesma categoria no mesmo lugar (4.3)
      if (JSON.stringify(e.categoria) === categoria && e.lugar![0] === lugar[0] && e.lugar![1] === lugar[1]) e.rep += 1;
    }
    if (this.recente.length >= this.p.n_rec) {
      const sai = this.recente.reduce((a, b) => (cmp([this.peso(b), b.decisao, b.id!], [this.peso(a), a.decisao, a.id!]) < 0 ? b : a));
      this.recente.splice(this.recente.indexOf(sai), 1);
      this.saidas_autobio.push({ id: sai.id!, sigma: sai.sigma });
    }
    const novo: EpisodioAutobio = { ...ep, id: this.proximo_id_autobio, lugar, ponto: [ep.ponto[0], ep.ponto[1]] };
    this.proximo_id_autobio += 1;
    this.recente.push(novo);
    return novo.id!;
  }

  // ------------------------------------------------------------ a C4, M2 e M3 (so com a `memoria_autobio`)
  /** os episodios das tres memorias, na ordem recente, duradoura, central */
  guardados(): EpisodioAutobio[] {
    return [...this.recente, ...this.duradoura, ...this.central];
  }

  /** o peso afetivo do episodio (4.3): min(S, mul(|sigma|, S + rep x S/2 + rec x S/4)) */
  peso(e: EpisodioAutobio): number {
    const S = this.S;
    return Math.min(S, mul(Math.abs(e.sigma), S + divArred(e.rep * S, 2) + divArred(e.rec * S, 4), S));
  }

  /** a lembranca da decisao (M2, 4.1); soma 1 em `rec` do lembrado */
  lembrar(sens: Pick<SaidaSens, "pos" | "objetos" | "ha_cheiro" | "contexto" | "leitura">): Lembrado {
    if (!this.autobio) throw new Error("M-MEM: a lembranca so com a memoria_autobio");
    const S = this.S, p = this.p;
    const [x, y] = sens.pos;
    const vista = new Set<string>(sens.objetos.map(o => o.classe));
    if (sens.ha_cheiro) vista.add("cheiro");
    if (sens.contexto.noite > 0) vista.add("noite");
    const faixas = Object.entries(sens.leitura).map(([r, v]) => [r, faixa(v, S)] as const);
    const pesoTotal = p.w_lugar + p.w_vista + p.w_corpo;
    let melhor: EpisodioAutobio | null = null;
    let chaveMelhor: number[] | null = null;
    for (const e of this.guardados()) {
      const [px, py] = e.ponto as [number, number];
      const dist = raizInteira((px - x) * (px - x) + (py - y) * (py - y));
      const sLugar = S - Math.min(S, divArred(dist * S, p.d_max));
      const b = new Set<string>(e.vista);
      if (e.cheiro) b.add("cheiro");
      if (e.noite) b.add("noite");
      let inter = 0;
      for (const c of vista) if (b.has(c)) inter++;
      const uniao = vista.size + b.size - inter;
      const sVista = vista.size === 0 && b.size === 0 ? S : divArred(inter * S, uniao);
      let iguais = 0;
      for (const [r, f] of faixas) if (r in e.corpo_antes && faixa(e.corpo_antes[r]!, S) === f) iguais++;
      const sCorpo = faixas.length ? divArred(iguais * S, faixas.length) : S;
      const sim = divArred(p.w_lugar * sLugar + p.w_vista * sVista + p.w_corpo * sCorpo, pesoTotal);
      const chave = [sim, Math.abs(e.sigma), e.decisao, e.id!];
      if (chaveMelhor === null || cmp(chave, chaveMelhor) > 0) { melhor = e; chaveMelhor = chave; }
    }
    if (melhor === null) return { recuperado: null, sim: 0, memoria: null, sigma: 0 };
    const sim = chaveMelhor![0]!;
    if (sim < p.sim_min) return { recuperado: null, sim, memoria: null, sigma: 0 };
    melhor.rec += 1;
    this.lembrancas += 1;
    return { recuperado: melhor.id!, sim, memoria: melhor.memoria, sigma: melhor.sigma };
  }

  /** o termo da lembranca (M4, 6.1): L = mul(w_lem, sigma) do episodio lembrado e a quem ele se aplica, ou null sem lembranca. Nao muda o estado */
  termoLembranca(lembranca: Pick<Lembrado, "recuperado">): TermoLembranca | null {
    if (!this.autobio) throw new Error("M-MEM: o termo da lembranca so com a memoria_autobio");
    if (lembranca.recuperado === null) return null;
    const e = this.guardados().find(x => x.id === lembranca.recuperado);
    if (e === undefined) throw new Error(`M-MEM: o episodio ${lembranca.recuperado} lembrado nao esta guardado`);
    const acao = e.acao[0], tipo = e.acao[1];       // a luta tem (lutar, rival); nenhuma unidade casa com ela
    const alvo = e.objeto !== null ? e.objeto.classe : tipo;       // a classe de alvo do episodio
    return { id: e.id!, L: mul(this.p.w_lem, e.sigma, this.S), acao, alvo, lugar: [e.lugar![0], e.lugar![1]], so_comportamento: e.classe === "sem_alvo" };
  }

  /** se a unidade da lista de agora tem a mesma acao do episodio lembrado (6.1): o mesmo comportamento e a mesma classe de alvo (para `ponto`,
   *  o mesmo lugar; para `sem_alvo`, o comportamento). Funcao de seta: vai ao impulso solta, sem o `this` */
  casa = (termo: TermoLembranca, unidade: AlvoImpulso): boolean => {
    if (unidade.acao !== termo.acao) return false;
    if (termo.so_comportamento) return true;
    if (unidade.tipo !== termo.alvo) return false;
    if (unidade.tipo !== "ponto") return true;
    const [x, y] = unidade.chave[2] as readonly [number, number];
    const l = this.lugarDe(x, y);
    return l[0] === termo.lugar[0] && l[1] === termo.lugar[1];
  };

  /** lugar -> (a soma dos sigma, cortada em [-S, S], o episodio mais recente que a compoe): so consumo de comida boa e visita (MA-2) */
  valoresSoma(): Map<string, { lugar: [number, number]; valor: number; e: EpisodioAutobio }> {
    const soma = new Map<string, { lugar: [number, number]; total: number; rep: EpisodioAutobio }>();
    for (const e of this.guardados()) {
      if (e.origem === "visita" || (e.origem === "consumo" && (COMIDAS_BOAS as readonly string[]).includes(e.classe))) {
        const chave = `${e.lugar![0]},${e.lugar![1]}`;
        const at = soma.get(chave);
        if (at === undefined) soma.set(chave, { lugar: [e.lugar![0], e.lugar![1]], total: e.sigma, rep: e });
        else {
          at.total += e.sigma;
          if (cmp([e.decisao, e.id!], [at.rep.decisao, at.rep.id!]) > 0) at.rep = e;
        }
      }
    }
    const out = new Map<string, { lugar: [number, number]; valor: number; e: EpisodioAutobio }>();
    for (const [c, t] of soma) out.set(c, { lugar: t.lugar, valor: Math.max(-this.S, Math.min(this.S, t.total)), e: t.rep });
    return out;
  }

  /** lugar -> o episodio mais recente nele (a decisao, depois o id) */
  valores(): Map<string, { lugar: [number, number]; e: Episodio }> {
    const out = new Map<string, { lugar: [number, number]; e: Episodio }>();
    for (const e of this.episodios) {
      const c = `${e.lugar[0]},${e.lugar[1]}`;
      const atual = out.get(c);
      if (atual === undefined || cmp([e.decisao, e.id], [atual.e.decisao, atual.e.id]) > 0) out.set(c, { lugar: e.lugar, e });
    }
    return out;
  }

  /** a recuperacao da decisao: {pista, recuperado (o id ou null), lugar, ponto, valor, M} */
  recuperar(
    sens: Pick<SaidaSens, "pos" | "conjuncoes">, afeto: { urgencias: Readonly<Record<string, number>> },
  ): Recuperacao {
    const S = this.S, p = this.p;
    const pista = (afeto.urgencias["fome"] ?? 0) > p.lambda_busca && sens.conjuncoes.comida_vista === 0;
    const nada: Recuperacao = { pista, recuperado: null, lugar: null, ponto: null, valor: 0, M: 0 };
    if (!pista) return nada;
    const [x, y] = sens.pos;
    type Ep = { id?: number; decisao: number; ponto: any };
    let melhor: { lugar: number[]; e: Ep; nota: number; valor: number } | null = null;
    let chaveMelhor: number[] | null = null;
    const valores: { lugar: [number, number]; valor: number; e: Ep }[] = this.autobio
      ? [...this.valoresSoma().values()]
      : [...this.valores().values()].map(v => ({ lugar: v.lugar, valor: v.e.r_n, e: v.e }));
    valores.sort((a, b) => cmp(a.lugar, b.lugar));
    for (const { lugar, valor, e } of valores) {
      if (valor <= 0) continue;
      const [px, py] = e.ponto as [number, number];
      const dist = raizInteira((px - x) * (px - x) + (py - y) * (py - y));
      const nota = mul(valor, S - Math.min(S, divArred(dist * S, p.d_max)), S);
      if (nota <= 0) continue;
      const chave = [nota, e.decisao, e.id!];
      if (chaveMelhor === null || cmp(chave, chaveMelhor) > 0) { melhor = { lugar, e, nota, valor }; chaveMelhor = chave; }
    }
    if (melhor === null) return nada;
    this.recuperacoes += 1;
    return {
      pista: true, recuperado: melhor.e.id!, lugar: [...melhor.lugar], ponto: [melhor.e.ponto[0], melhor.e.ponto[1]], valor: melhor.valor,
      nota: melhor.nota, M: mul(p.w_mem, melhor.valor, S),
    };
  }

  // ------------------------------------------------------------ a consolidacao (M3, 4.3)
  /** a consolidacao diaria: so com a `memoria_autobio`, uma vez por dia do pet, na primeira decisao depois da virada do dia (o dia vem do
   *  `relogio`); devolve o registro (tambem guardado em `consolidacoes`) ou null. A ordem esta na docstring do Python. */
  consolidar(decisao: number): Dict | null {
    if (!this.autobio || this.dia <= this.dia_consolidado) return null;
    const p = this.p;
    this.dia_consolidado = this.dia;
    const reg = { dia: this.dia, decisao, subiram: { duradoura: [] as number[], central: [] as number[] }, esquecidos: [] as number[], voltaram: [] as number[],
      por_capacidade: { duradoura: [] as number[] } };
    for (const e of [...this.recente].sort((a, b) => cmp([a.decisao, a.id!], [b.decisao, b.id!]))) {
      if (decisao - e.decisao <= p.janela_rec) continue;
      this.recente.splice(this.recente.indexOf(e), 1);
      if (e.rep >= 1 || Math.abs(e.sigma) >= p.theta_dur || e.rec >= 1) {
        e.memoria = "duradoura";
        this.duradoura.push(e);
        reg.subiram.duradoura.push(e.id!);
      } else {
        reg.esquecidos.push(e.id!);
      }
    }
    const melhores = new Map<string, { chave: number[]; e: EpisodioAutobio }>();   // categoria -> o de maior peso entre a central e os candidatos
    for (const e of [...this.central, ...this.duradoura.filter(x => x.rep >= p.n_rep_central)]) {
      const c = JSON.stringify(e.categoria);
      const chave = [this.peso(e), -e.decisao, -e.id!];
      const at = melhores.get(c);
      if (at === undefined || cmp(chave, at.chave) > 0) melhores.set(c, { chave, e });
    }
    const nova = [...melhores.values()].sort((a, b) => cmp(b.chave, a.chave)).slice(0, p.n_cen).map(t => t.e);
    const idsNova = new Set(nova.map(e => e.id!));
    for (const e of [...this.central]) {
      if (!idsNova.has(e.id!)) {
        this.central.splice(this.central.indexOf(e), 1);
        e.memoria = "duradoura";
        this.duradoura.push(e);
        reg.voltaram.push(e.id!);
      }
    }
    for (const e of nova) {
      if (e.memoria !== "central") {
        this.duradoura.splice(this.duradoura.indexOf(e), 1);
        e.memoria = "central";
        this.central.push(e);
        reg.subiram.central.push(e.id!);
      }
    }
    while (this.duradoura.length > p.n_dur) {
      const sai = this.duradoura.reduce((a, b) => (cmp([this.peso(b), b.decisao, b.id!], [this.peso(a), a.decisao, a.id!]) < 0 ? b : a));
      this.duradoura.splice(this.duradoura.indexOf(sai), 1);
      reg.por_capacidade.duradoura.push(sai.id!);
    }
    this.consolidacoes.push(reg);
    return reg;
  }

  // ------------------------------------------------------------ a interface da memoria consolidada (secao 9)
  /** o termo M de cada unidade: no prototipo, so o do lugar recuperado, indexado pelo texto da chave */
  termosDecisao(recuperacao: Recuperacao | null): Record<string, number> {
    if (recuperacao === null || recuperacao.recuperado === null) return {};
    return { [JSON.stringify(["explorar", "ponto", [recuperacao.ponto![0], recuperacao.ponto![1]]])]: recuperacao.M };
  }

  /** as facetas (M5) ficam fora do laboratorio (LAB-1) */
  evidenciaFaceta(_nome: string): never {
    throw new Error("M-MEM.evidenciaFaceta: facetas_mem fica fora do laboratorio (LAB-1)");
  }

  classesComPositivo(): never {
    throw new Error("M-MEM.classesComPositivo: so serve as facetas_mem, que ficam fora do laboratorio (LAB-1)");
  }

  estadoInterno(): Dict {
    const out: Dict = {
      episodios: this.episodios.map(e => ({ ...e })), proximo_id: this.proximo_id, saidas: this.saidas.map(s => ({ ...s })), recuperacoes: this.recuperacoes,
    };
    if (this.autobio) {                              // desligada, o estado e o de hoje, byte a byte
      out["autobio"] = {
        recente: this.recente.map(e => ({ ...e })), proximo_id: this.proximo_id_autobio, saidas: this.saidas_autobio.map(s => ({ ...s })),
        relogio: { dia: this.dia, minuto: this.minuto }, duradoura: this.duradoura.map(e => ({ ...e })), central: this.central.map(e => ({ ...e })),
        consolidacoes: this.consolidacoes.map(c => ({ ...c })), lembrancas: this.lembrancas, dia_consolidado: this.dia_consolidado,
      };
    }
    return out;
  }
}
