/* M-IMPULSO, os impulsos e os circuitos de comportamento: o espelho de digilab/digibrain/impulso.py (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.1 a
   2.3 e 4.5; LM1). O contexto z (23 caracteristicas) entra em todos os comportamentos; as unidades (b, o) sao as sete acoes, uma por alvo; a
   ativacao soma, termo a termo, o inato, a proximidade, a novidade, o incentivo (P1), o habito (P2), a memoria, a persistencia e a lembranca
   (a `memoria_autobio`). A DX-3 (`cheiro_inato`) soma o `w0_tipo_cheiro` no `comer/cheiro`. Aritmetica inteira; sem estado e sem rng.
   As facetas (`facetas_mem`) ficam fora do laboratorio (LAB-1): ligadas, falha alto.
   **As unidades de fala** (DC3d; docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1; a subchave `fala_unidades`): o `chamar_atencao` vira tres unidades,
   (chamar_atencao, c, null) com c em CONTEUDOS_FALA, sem tipo de alvo. O inato de cada uma e o W0[chamar_atencao].z termo a termo, com o termo
   do receptor do conteudo (TERMO_DO_CONTEUDO) vezes o `ganho_conteudo` (mul) e os dos outros dois conteudos fora; o habito e o da linha de H
   da unidade (linhaDaOpcao). Desligada, a unidade e a de hoje. */
import { chaveUnidade, mul, phi, raizInteira, textoDaChave, type ChaveUnidade } from "./_comum.ts";
import { CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTO_OLHAR, COMPORTAMENTOS_DIGIBRAIN, CONFIG_FALA_UNIDADES, CONFIG_OLHAR, CONTEUDOS_FALA,
  INATOS_MODULAR, RECEPTORES_DIGIBRAIN, TERMO_DO_CONTEUDO, type ConfigOlhar } from "./constantes.ts";
import { linhaDaOpcao } from "./plast.ts";
import type { LeituraAfeto } from "./afeto.ts";
import type { CorpoModular, LinhaTela, ObjetoSens, SaidaSens } from "./sens.ts";

export const TERMOS = ["inato", "prox", "nov", "incentivo", "habito", "memoria", "persistencia"] as const;
/** o comportamento que vira as unidades de fala (so com a subchave `fala_unidades`) */
export const FALA = "chamar_atencao";
/** a ConfigFalaUnidades como o M-IMPULSO a le */
export type ConfigFalaUnidades = { readonly ganho_conteudo: number };

export type InatosImpulso = typeof INATOS_MODULAR;
/** o que o M-IMPULSO le da ConfigDigibrain */
export interface ConfigDigibrainImpulso { cheiro_inato: boolean; memoria_autobio: boolean; facetas_mem: boolean; fala_unidades: boolean; olhar?: boolean }

/** a saida do `mem.recuperar` que o impulso le: o lugar lembrado (ponto) e o termo M */
export interface MemoriaImpulso { recuperado: number | null; ponto: readonly [number, number] | null; M: number }
/** o `estado.contexto` que o impulso le: a frustracao F e a persistencia (`{textoDaChave(chave): h}`) */
export interface ContextoImpulso { F: number; persistencia: Readonly<Record<string, number>> }
/** o termo da lembranca (`mem.termo_lembranca`) e o `casa` do M-MEM */
export interface TermoLembranca { id: number; L: number; acao: string; alvo: string | null; lugar: readonly [number, number]; so_comportamento: boolean }
export type Lembranca = readonly [TermoLembranca, (termo: TermoLembranca, unidade: AlvoImpulso) => boolean];
/** o M-PLAST como o impulso o usa */
export interface PlastImpulso {
  habito(b: string, z: readonly number[]): number;
  incentivo(pc: CorpoModular, classe: string, drives: readonly string[]): number;
}

export interface AlvoImpulso {
  chave: ChaveUnidade; acao: string; tipo: string | null; objeto: ObjetoSens | LinhaTela | null; d: number | null;
}
export interface UnidadeImpulso extends AlvoImpulso { termos: Record<string, number>; soma: number; a: number }

export class Impulso {
  p: InatosImpulso;
  cd: ConfigDigibrainImpulso;
  S: number;
  w0: Record<string, number[]> = {};
  w0_prox: Record<string, number>;
  w0_nov: Record<string, number>;
  w0_tipo: Record<string, Record<string, number>> = {};
  cf: ConfigFalaUnidades;
  /** o indice em z do termo de cada conteudo de fala (3.1), na ordem de CONTEUDOS_FALA */
  jConteudo: Record<string, number>;
  /** o olhar (GOSTO_VISUAL, P1f): a ConfigOlhar com a subchave, null sem ela */
  readonly co: ConfigOlhar | null;

  constructor(inatosOuNulo: InatosImpulso | null, cfgDigibrain: ConfigDigibrainImpulso, cfgFala: ConfigFalaUnidades = CONFIG_FALA_UNIDADES,
              cfgOlhar: ConfigOlhar | null = null) {
    const inatos = inatosOuNulo ?? INATOS_MODULAR;
    this.p = inatos;
    this.cd = cfgDigibrain;
    this.S = inatos.escala;
    if (cfgDigibrain.facetas_mem) throw new Error("M-IMPULSO: a facetas_mem fica fora do laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, secao 3)");
    if (cfgOlhar !== null && !cfgDigibrain.olhar) throw new Error("M-IMPULSO: a ConfigOlhar so com a subchave olhar");
    this.co = cfgDigibrain.olhar ? (cfgOlhar ?? CONFIG_OLHAR) : null;
    const idx = new Map<string, number>(CARACTERISTICAS_DIGIBRAIN.map((c, j) => [c, j]));
    const linhasW0: (readonly [string, readonly (readonly [string, number])[]])[] = [...inatos.w0];
    if (this.co !== null) linhasW0.push([COMPORTAMENTO_OLHAR, this.co.w0_olhar]);
    for (const [b, linha] of linhasW0) {
      const w = new Array<number>(CARACTERISTICAS_DIGIBRAIN.length).fill(0);
      for (const [c, v] of linha) {
        const j = idx.get(c);
        if (j === undefined) throw new Error(`M-IMPULSO: caracteristica desconhecida ${c}`);
        w[j] = v;
      }
      this.w0[b] = w;
    }
    this.w0_prox = Object.fromEntries(inatos.w0_prox);
    this.w0_nov = Object.fromEntries(inatos.w0_nov);
    for (const [b, t] of inatos.w0_tipo) this.w0_tipo[b] = Object.fromEntries(t);
    if ("cheiro" in (this.w0_tipo["comer"] ?? {})) throw new Error("o tipo `cheiro` do comer fica no w0_tipo_cheiro, atras da subchave `cheiro_inato` (DX-3)");
    if (cfgDigibrain.cheiro_inato) this.w0_tipo["comer"] = { ...(this.w0_tipo["comer"] ?? {}), cheiro: inatos.w0_tipo_cheiro };
    this.cf = cfgFala;
    this.jConteudo = Object.fromEntries(TERMO_DO_CONTEUDO.map(([c, termo]) => [c, idx.get(termo)!]));
    if (Object.keys(this.jConteudo).join() !== CONTEUDOS_FALA.join() || Object.values(this.jConteudo).some(j => j === undefined))
      throw new Error("M-IMPULSO: TERMO_DO_CONTEUDO fora de CONTEUDOS_FALA");
  }

  /** o inato de cada unidade de fala (3.1): o W0[chamar_atencao].z termo a termo, com o termo do conteudo da unidade vezes o `ganho_conteudo`
   *  (mul) e os termos dos outros dois conteudos fora */
  inatoFala(z: readonly number[]): Record<string, number> {
    const S = this.S, w = this.w0[FALA]!;
    const termo = w.map((wj, j) => (wj ? mul(wj, z[j]!, S) : 0));
    const js = Object.values(this.jConteudo);
    let comum = 0;
    termo.forEach((t, j) => { if (!js.includes(j)) comum += t; });
    return Object.fromEntries(CONTEUDOS_FALA.map(c => [c, comum + mul(this.cf.ganho_conteudo, termo[this.jConteudo[c]!]!, S)]));
  }

  contextoZ(sens: Pick<SaidaSens, "contexto" | "conjuncoes">, afeto: Pick<LeituraAfeto, "urgencias" | "V" | "E">, contexto: Pick<ContextoImpulso, "F">): number[] {
    const S = this.S, u = afeto.urgencias, cs = sens.contexto, cj = sens.conjuncoes;
    const z = [S, ...RECEPTORES_DIGIBRAIN.map(r => u[r] ?? 0)];
    z.push(cs.noite, cs.dormindo, cs.sem_cuidado, cj.comida_vista, cj.sem_comida, cj.bola_vista,
      mul(u["fome"] ?? 0, cj.sem_comida, S), mul(cs.sem_cuidado, u["humor"] ?? 0, S), contexto.F, afeto.V, afeto.E);
    if (z.length !== CARACTERISTICAS_DIGIBRAIN.length) throw new Error("M-IMPULSO: z fora de CARACTERISTICAS_DIGIBRAIN");
    return z;
  }

  /** as unidades possiveis da decisao, na ordem fixa: {chave, acao, tipo (o tipo do alvo para o W0_tipo), objeto, d} */
  static alvos(sens: Pick<SaidaSens, "objetos" | "ha_cheiro" | "pos">, memoria: MemoriaImpulso | null, fala = false): AlvoImpulso[] {
    const out: AlvoImpulso[] = [];
    const [x, y] = sens.pos;
    for (const b of COMPORTAMENTOS_DIGIBRAIN) {
      if (b === "comer") {
        for (const o of sens.objetos) {
          if (o.classe !== "bola") out.push({ chave: chaveUnidade(b, "comida", o.id), acao: b, tipo: o.classe, objeto: o, d: o.d });
        }
        if (sens.ha_cheiro) out.push({ chave: chaveUnidade(b, "cheiro"), acao: b, tipo: "cheiro", objeto: null, d: null });
      } else if (b === "brincar") {
        const bolas = sens.objetos.filter(o => o.classe === "bola");
        for (const o of bolas) out.push({ chave: chaveUnidade(b, "bola", o.id), acao: b, tipo: "bola", objeto: o, d: o.d });
        if (!bolas.length) out.push({ chave: chaveUnidade(b), acao: b, tipo: null, objeto: null, d: null });
      } else if (b === "explorar") {
        out.push({ chave: chaveUnidade(b, "vagar"), acao: b, tipo: "vagar", objeto: null, d: null });
        if (sens.ha_cheiro) out.push({ chave: chaveUnidade(b, "cheiro"), acao: b, tipo: "cheiro", objeto: null, d: null });
        if (memoria !== null && memoria.recuperado !== null) {
          const [px, py] = memoria.ponto!;
          const d = raizInteira((px - x) * (px - x) + (py - y) * (py - y));
          out.push({ chave: chaveUnidade(b, "ponto", [px, py]), acao: b, tipo: "ponto", objeto: null, d });
        }
      } else if (b === FALA && fala) {                   // a `fala_unidades`: as tres unidades de fala, na ordem de CONTEUDOS_FALA, sem tipo de alvo
        for (const c of CONTEUDOS_FALA) out.push({ chave: chaveUnidade(b, c), acao: b, tipo: null, objeto: null, d: null });
      } else {
        out.push({ chave: chaveUnidade(b), acao: b, tipo: null, objeto: null, d: null });
      }
    }
    return out;
  }

  /** as unidades da decisao com os termos e a ativacao, e o z. `lembranca` = [o termo da M4, o `casa` do M-MEM] ou null; so com a
   *  `memoria_autobio` as unidades ganham o termo `lembranca` (L nas que casam com o episodio lembrado, 0 nas outras) */
  unidades(sens: SaidaSens, afeto: LeituraAfeto, contexto: ContextoImpulso, plast: PlastImpulso, memoria: MemoriaImpulso | null,
    drives: readonly string[], lembranca: Lembranca | null = null, facetas: unknown = null,
    gosto: Readonly<Record<number, number>> | null = null): [UnidadeImpulso[], number[]] {
    if (facetas !== null) throw new Error("M-IMPULSO: as facetas ficam fora do laboratorio");
    if ((gosto !== null) !== (this.co !== null)) throw new Error("M-IMPULSO: o termo gosto vem so com a subchave olhar, e com ela sempre");
    const S = this.S, aMax = this.p.a_max;
    const z = this.contextoZ(sens, afeto, contexto);
    const inatoB: Record<string, number> = {}, habitoB: Record<string, number> = {};
    for (const b of COMPORTAMENTOS_DIGIBRAIN) {
      let soma = 0;
      this.w0[b]!.forEach((w, j) => { if (w) soma += mul(w, z[j]!, S); });
      inatoB[b] = soma;
    }
    const fala = this.cd.fala_unidades;
    for (const b of COMPORTAMENTOS_DIGIBRAIN) if (!(fala && b === FALA)) habitoB[b] = plast.habito(b, z);
    const inatoF = fala ? this.inatoFala(z) : null;
    if (fala) for (const c of CONTEUDOS_FALA) habitoB[`${FALA}/${c}`] = plast.habito(`${FALA}/${c}`, z);
    const incentivos: Record<string, number> = {};
    const olhar = this.co !== null;
    const nomesTermos = [...TERMOS, ...(this.cd.memoria_autobio ? ["lembranca"] : []), ...(olhar ? ["gosto"] : [])];
    const lista = Impulso.alvos(sens, memoria, fala);
    if (olhar) {                                        // o olhar (P1f): o inato e o habito da linha nova; uma unidade por TV a vista, no fim
      let soma = 0;
      this.w0[COMPORTAMENTO_OLHAR]!.forEach((w, j) => { if (w) soma += mul(w, z[j]!, S); });
      inatoB[COMPORTAMENTO_OLHAR] = soma;
      habitoB[COMPORTAMENTO_OLHAR] = plast.habito(COMPORTAMENTO_OLHAR, z);
      const telas = sens.telas ?? [];
      for (const o of telas) lista.push({ chave: chaveUnidade(COMPORTAMENTO_OLHAR, o.classe, o.id), acao: COMPORTAMENTO_OLHAR, tipo: o.classe, objeto: o, d: o.d });
      if (Object.keys(gosto!).some(id => !telas.some(o => String(o.id) === id))) throw new Error(`M-IMPULSO: o gosto de uma TV fora da vista: ${JSON.stringify(gosto)}`);
    }
    const out: UnidadeImpulso[] = [];
    for (const u of lista) {
      const b = u.acao, o = u.objeto;
      const termos: Record<string, number> = Object.fromEntries(nomesTermos.map(t => [t, 0]));
      const inato = inatoF !== null && b === FALA ? inatoF[u.chave[1] as string]! : inatoB[b]!;
      termos["inato"] = inato + (u.tipo !== null ? (this.w0_tipo[b]?.[u.tipo] ?? 0) : 0);
      if (b === COMPORTAMENTO_OLHAR) {                  // o olhar (P1f): a linha da TV, o incentivo da classe `tela` e o gosto
        const co = this.co!, ot = o as LinhaTela;
        termos["prox"] = mul(co.w0_prox, ot.prox, S);
        termos["nov"] = mul(co.w0_nov, ot.nov, S);
        if (!(ot.classe in incentivos)) incentivos[ot.classe] = plast.incentivo(sens.pc, ot.classe, drives);
        termos["incentivo"] = mul(incentivos[ot.classe]!, ot.prox, S);
        termos["gosto"] = gosto![ot.id] ?? 0;
      } else if (o !== null) {
        termos["prox"] = mul(this.w0_prox[b] ?? 0, o.prox, S);
        termos["nov"] = mul(this.w0_nov[b] ?? 0, o.nov, S);
        if (b === "comer" || b === "brincar") {
          const c = o.classe;
          if (!(c in incentivos)) incentivos[c] = plast.incentivo(sens.pc, c, drives);
          termos["incentivo"] = mul(incentivos[c]!, o.prox, S);
        }
      }
      termos["habito"] = habitoB[linhaDaOpcao(u.chave, fala)]!;
      if (u.tipo === "ponto") termos["memoria"] = memoria!.M;
      termos["persistencia"] = contexto.persistencia[textoDaChave(u.chave)] ?? 0;
      if (lembranca !== null && lembranca[1](lembranca[0], u)) termos["lembranca"] = lembranca[0].L;
      let soma = 0;
      for (const v of Object.values(termos)) soma += v;
      out.push({ ...u, termos, soma, a: phi(soma, aMax) });
    }
    return [out, z];
  }
}
