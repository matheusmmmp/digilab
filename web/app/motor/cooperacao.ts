/* A cooperacao entre dois pets do mesmo dono em TS (docs/TAREFA_V3_COOPERACAO.md, etapa CO3): o porte de digilab/cooperacao.py, numero a
   numero (o G-PAR-COOP, test/cooperacao.test.ts). So mede: o Grupo (motor/grupo.ts), com a medida ligada, chama `decisao` logo depois de cada
   pet decidir na vez sorteada e `fimDoTick` depois do toque e da disputa; nada aqui muda o mundo, o corpo ou o cerebro (o G-SEM-DECISAO).

   Os atos (autor i, alvo j):
     disputa    i comeu a comida que j tinha como alvo (o registro `disputas`). Sinal -1 se a fome de j na ultima decisao dele estava abaixo do
                piso; 0 se nao. O efeito e o ganho que i teve.
     contencao  numa decisao de i, j a vista e uma comida madura so a vista, que i nao come; se j a come antes da proxima decisao de i, e o
                ato. Sinal +1; o efeito e o ganho de j.
     encostar   i encostou em j (seguiu j) com j emburrado visto de fora. Sinal +1; o efeito e 0 (o toque ainda nao mexe no corpo).
   A pontuacao em inteiros na escala S, guardada em ponto fixo de 16 bits abaixo de S e lida com divArred: a repeticao n do mesmo ato com o
   mesmo alvo no dia entra com divArred(valor, 2^n), e a conta decai tick a tick pela meia-vida. A reputacao de i vista por k e a mesma conta,
   so com os atos de i que k testemunhou (k ve i no momento do ato). Nada aqui sabe de tela: nenhum numero vai para o jogador (D-MM-8).

   A CO6 (docs/ESPEC_V3_COOPERACAO_CO6.md; so com `co6`): o peso dos deveres `k` de cada pet, o `fim_do_tick_k` do Python (o G-PAR-CO6,
   test/cooperacao_co6.test.ts). No fim de TODO tick, para cada presente i em ordem de id: ha encontro se um outro j esta a ate o raio de i e
   a ate o de j e a reputacao de j vista por i e positiva; com encontro, k ganha kPasso; sem, decai um tick pela meia-vida; e fica no teto do
   estagio da idade (o tick do proprio pet). Em ponto fixo de 16 bits abaixo de S, lido com divArred. Nada aqui muda a decisao. */
import { CCOOP } from "./constantes.ts";
import { distancia, divArred } from "./mundo.ts";

export const ATOS_COOP = ["disputa", "contencao", "encostar"] as const;
export type AtoCoop = typeof ATOS_COOP[number];
export const TIPOS_MADUROS: readonly string[] = ["racao", "a", "b", "c"];
export const BITS_FRACAO_COOP = 16;

/** a ConfigCooperacao do Python (o CCOOP e o espelho conferido); `ligada` fica com quem a usa */
export interface ConfigCooperacao {
  ligada: boolean; escala: number; pisoFome: number; meiaVida: number; kMeiaVida: number; janelaNovidade: number;
  /** a CO6: so com `ligada` */
  co6: boolean; kPasso: number; kTetoBebe: number; kTetoCrianca: number; kTetoAdolescente: number; kTetoAdulto: number;
  diasFimBebe: number; diasFimCrianca: number; diasFimAdolescente: number;
  /** a CO7: so com `co6`; os numeros sao os do motor/digibrain/dever.ts */
  co7: boolean; limiarEscudo: number; rEscudoCelulas: number; pisoPrivacaoS: number; wUniv: number; limiarHumor: number; wCulpa: number;
  wInveja: number; janelaInveja: number;
}
export const CONFIG_COOPERACAO: Readonly<ConfigCooperacao> = Object.freeze({ ligada: false, co6: false, co7: false, ...CCOOP });
export const CONFIG_COOPERACAO_LIGADA: Readonly<ConfigCooperacao> = Object.freeze({ ...CONFIG_COOPERACAO, ligada: true });
export const CONFIG_COOPERACAO_CO6: Readonly<ConfigCooperacao> = Object.freeze({ ...CONFIG_COOPERACAO_LIGADA, co6: true });
export const CONFIG_COOPERACAO_CO7: Readonly<ConfigCooperacao> = Object.freeze({ ...CONFIG_COOPERACAO_CO6, co7: true });

const TICKS_DIA_COOP = 1440;

/** o estagio pela idade em ticks do pet (o estagio_por_idade do Python, o provisorio da ConfigExpressao) */
export function estagioDaIdade(idade: number, cfg: Readonly<ConfigCooperacao>): "bebe" | "crianca" | "adolescente" | "adulto" {
  if (!Number.isInteger(idade) || idade < 0) throw new Error(`idade em ticks, inteira e nao negativa: ${idade}`);
  const dias = idade / TICKS_DIA_COOP;
  return dias < cfg.diasFimBebe ? "bebe" : dias < cfg.diasFimCrianca ? "crianca" : dias < cfg.diasFimAdolescente ? "adolescente" : "adulto";
}

export interface ConsumoCoop { id: number; fome_antes: number; fome_depois: number; humor_antes: number; humor_depois: number }

/** o bem-estar que a refeicao deu a quem comeu, na escala S (nunca negativo) */
export function ganhoDaRefeicao(c: ConsumoCoop, escala: number): number {
  const delta = (c.fome_depois - c.fome_antes) + (c.humor_depois - c.humor_antes);
  return Math.max(0, Math.floor(escala * delta + 0.5));
}

/** o passo_meia_vida do corpo: q - max(1, divArred(q k, 2^16)) enquanto q > 0 */
function passoMeiaVida(q: number, k: number): number {
  if (q <= 0) return 0;
  return Math.max(0, q - Math.max(1, divArred(q * k, 65536)));
}

/** `ticks` passos da meia-vida sobre v, com o sinal de fora */
export function decair(v: number, ticks: number, k: number): number {
  if (ticks < 0) throw new Error(`a pontuacao nao volta no tempo: ${ticks}`);
  const sinal = v >= 0 ? 1 : -1;
  let q = Math.abs(v);
  for (let t = 0; t < ticks && q !== 0; t++) q = passoMeiaVida(q, k);
  return q === 0 ? 0 : sinal * q;
}

/** uma pontuacao: o valor (x 2^16) no ultimo tick e as repeticoes de cada (janela, ato, alvo) */
export class ContaCoop {
  private bruto = 0;
  private tick = 0;
  private readonly repeticoes = new Map<string, number>();
  private readonly cfg: Readonly<ConfigCooperacao>;
  private lido: [number, number] | null = null;      // [tick, bruto decaido ate ele]: o decaimento e passo a passo, e partir dele e exato
  constructor(cfg: Readonly<ConfigCooperacao>) {
    this.cfg = cfg;
  }

  private brutoEm(tick: number): number {
    let baseTick = this.tick, base = this.bruto;
    if (this.lido !== null && baseTick <= this.lido[0] && this.lido[0] <= tick) [baseTick, base] = this.lido;
    const v = decair(base, tick - baseTick, this.cfg.kMeiaVida);
    this.lido = [tick, v];
    return v;
  }

  em(tick: number): number {
    return divArred(this.brutoEm(tick), 2 ** BITS_FRACAO_COOP);
  }

  /** [a repeticao, a contribuicao, o valor depois] */
  somar(tick: number, ato: string, alvo: string, valor: number): [number, number, number] {
    this.bruto = this.brutoEm(tick);
    this.tick = tick;
    this.lido = null;
    const chave = `${Math.floor(tick / this.cfg.janelaNovidade)}|${ato}|${alvo}`;
    const n = this.repeticoes.get(chave) ?? 0;
    this.repeticoes.set(chave, n + 1);
    const contribuicao = divArred(valor, 2 ** n);
    this.bruto += contribuicao * 2 ** BITS_FRACAO_COOP;
    return [n, contribuicao, this.em(tick)];
  }
}

export interface AtoRegistrado {
  tick: number; ato: AtoCoop; autor: string; alvo: string; comida: number | null; sinal: number; efeito: number; valor: number;
  repeticao: number; contribuicao: number; pontuacao_depois: number; testemunhas: string[];
  reputacao: Record<string, { repeticao: number; contribuicao: number; depois: number }>;
}
export type Posicoes = Record<string, readonly [number, number]>;

const comparaStr = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);

/** A medida da cooperacao de um grupo (a ConfigCooperacao ligada). So le o que o Grupo passa; nao muda nada. */
export class Cooperacao {
  readonly cfg: Readonly<ConfigCooperacao>;
  readonly atos: AtoRegistrado[] = [];
  private readonly pontuacoes = new Map<string, ContaCoop>();
  private readonly reputacoes = new Map<string, ContaCoop>();
  private readonly fome = new Map<string, number>();                         // o fome_antes da ultima decisao de cada pet
  private readonly oportunidades = new Map<string, [number, string, number][]>();   // autor -> [(tick, alvo, comida)]
  private ganhos = new Map<string, number>();                                 // "tick|quem|comida" -> o ganho, so no tick
  private readonly kDe = new Map<string, number>();                           // a CO6: o k de cada pet x 2^16, no fim do ultimo tick

  constructor(cfg: Readonly<ConfigCooperacao>) {
    if (!cfg.ligada) throw new Error("a Cooperacao so existe com a ConfigCooperacao ligada");
    for (const n of ["escala", "meiaVida", "kMeiaVida", "janelaNovidade"] as const)
      if (!Number.isInteger(cfg[n]) || cfg[n] <= 0) throw new Error(`ConfigCooperacao.${n} tem de ser inteiro positivo: ${cfg[n]}`);
    if (!(cfg.pisoFome > 0 && cfg.pisoFome < 1)) throw new Error(`ConfigCooperacao.pisoFome em (0, 1): ${cfg.pisoFome}`);
    if (cfg.co6 && !cfg.ligada) throw new Error("ConfigCooperacao.co6 so liga com a cooperacao ligada");
    if (cfg.co7 && !cfg.co6) throw new Error("ConfigCooperacao.co7 so liga com a co6 ligada");
    if (!Number.isInteger(cfg.kPasso) || cfg.kPasso <= 0 || cfg.kPasso > cfg.escala) throw new Error(`ConfigCooperacao.kPasso em (0, escala]: ${cfg.kPasso}`);
    const tetos = [cfg.kTetoBebe, cfg.kTetoCrianca, cfg.kTetoAdolescente, cfg.kTetoAdulto];
    if (tetos.some((t, i) => !Number.isInteger(t) || t < 0 || t > cfg.escala || (i > 0 && t < tetos[i - 1]!)))
      throw new Error(`ConfigCooperacao.kTeto*: inteiros em [0, escala], sem descer com o estagio: ${tetos}`);
    this.cfg = cfg;
  }

  // ------------------------------------------------------------ o que o Grupo chama
  /** o pet `ident` acabou de decidir no tick: as comidas maduras que ele via, os outros a vista, a fome com que decidiu e o que comeu */
  decisao(tick: number, ident: string, maduras: readonly number[], outrosVistos: readonly string[], fomeAntes: number,
          consumo: ConsumoCoop | null, posicoes: Posicoes, raios: Record<string, number>): void {
    this.fome.set(ident, fomeAntes);
    if (consumo !== null) {
      const ganho = ganhoDaRefeicao(consumo, this.cfg.escala);
      this.ganhos.set(`${tick}|${ident}|${consumo.id}`, ganho);
      for (const autor of [...this.oportunidades.keys()].sort(comparaStr)) {
        if (autor === ident) continue;
        const lista = this.oportunidades.get(autor)!;
        for (const op of [...lista]) {
          if (op[1] === ident && op[2] === consumo.id) {
            lista.splice(lista.indexOf(op), 1);
            this.ato(tick, "contencao", autor, ident, consumo.id, 1, ganho, posicoes, raios);
          }
        }
      }
    }
    const comeu = consumo === null ? null : consumo.id;
    const novas: [number, string, number][] = maduras.length === 1 && maduras[0] !== comeu
      ? [...outrosVistos].sort(comparaStr).map((j): [number, string, number] => [tick, j, maduras[0]])
      : [];
    this.oportunidades.set(ident, novas);
  }

  /** o fim de um tick com decisao: as disputas e os contatos deste tick, a acao visivel e a posicao de cada presente */
  fimDoTick(tick: number, disputas: readonly { vencedor: string; perdedor: string; comida: number }[],
            contatos: readonly { pets: unknown; tipos: Record<string, string> }[], acoes: Record<string, string>, posicoes: Posicoes,
            raios: Record<string, number>): void {
    for (const d of disputas) {
      const g = this.ganhos.get(`${tick}|${d.vencedor}|${d.comida}`);
      if (g === undefined) throw new Error(`disputa sem a refeicao do vencedor no tick: ${JSON.stringify(d)}`);
      const f = this.fome.get(d.perdedor);
      if (f === undefined) throw new Error(`disputa com um perdedor que nunca decidiu: ${JSON.stringify(d)}`);
      this.ato(tick, "disputa", d.vencedor, d.perdedor, d.comida, f < this.cfg.pisoFome ? -1 : 0, g, posicoes, raios);
    }
    for (const c of contatos) {
      const [a, b] = c.pets as [string, string];
      for (const [eu, outro] of [[a, b], [b, a]])
        if (c.tipos[eu] === "encostou" && acoes[outro] === "emburrar") this.ato(tick, "encostar", eu, outro, null, 1, 0, posicoes, raios);
    }
    this.ganhos = new Map([...this.ganhos].filter(([k]) => !k.startsWith(`${tick}|`)));
  }

  /** a CO6: o fim de TODO tick, depois da medida do tick; `idades`, o tick do proprio pet */
  fimDoTickK(tick: number, posicoes: Posicoes, raios: Record<string, number>, idades: Record<string, number>): void {
    if (!this.cfg.co6) throw new Error("o peso dos deveres (fimDoTickK) exige a subchave co6 da ConfigCooperacao");
    const ids = Object.keys(posicoes).sort(comparaStr);
    const mesmo = (o: Record<string, unknown>) => Object.keys(o).sort(comparaStr).join("|") === ids.join("|");
    if (!mesmo(raios) || !mesmo(idades)) throw new Error(`posicoes, raios e idades de presentes diferentes: ${ids}`);
    const um = 2 ** BITS_FRACAO_COOP;
    for (const i of ids) {
      const [xi, yi] = posicoes[i]!;
      let encontro = false;
      for (const j of ids) {
        if (j === i) continue;
        const d = distancia(posicoes[j]![0] - xi, posicoes[j]![1] - yi);
        if (d <= raios[i]! && d <= raios[j]! && this.reputacao(j, i, tick) > 0) { encontro = true; break; }
      }
      const k = this.kDe.get(i) ?? 0;
      const novo = encontro ? k + this.cfg.kPasso * um : decair(k, 1, this.cfg.kMeiaVida);
      this.kDe.set(i, Math.min(novo, this.tetoK(idades[i]!) * um));
    }
  }

  /** o teto do k no estagio da idade em ticks do proprio pet (CO6-4) */
  tetoK(idade: number): number {
    const e = estagioDaIdade(idade, this.cfg);
    return e === "bebe" ? this.cfg.kTetoBebe : e === "crianca" ? this.cfg.kTetoCrianca : e === "adolescente" ? this.cfg.kTetoAdolescente : this.cfg.kTetoAdulto;
  }

  /** o k do pet no fim do ultimo tick, na escala S */
  pesoDever(ident: string): number {
    if (!this.cfg.co6) throw new Error("o peso dos deveres exige a subchave co6 da ConfigCooperacao");
    return divArred(this.kDe.get(ident) ?? 0, 2 ** BITS_FRACAO_COOP);
  }

  // ------------------------------------------------------------ a conta
  private conta(tabela: Map<string, ContaCoop>, chave: string): ContaCoop {
    let c = tabela.get(chave);
    if (c === undefined) { c = new ContaCoop(this.cfg); tabela.set(chave, c); }
    return c;
  }

  private ato(tick: number, ato: AtoCoop, autor: string, alvo: string, comida: number | null, sinal: number, efeito: number,
              posicoes: Posicoes, raios: Record<string, number>): void {
    if (!Number.isInteger(efeito) || efeito < 0 || ![-1, 0, 1].includes(sinal)) throw new Error(`ato invalido: ${ato} ${sinal} ${efeito}`);
    const valor = sinal * efeito + 0;                                          // sem o -0 do JS
    const [ax, ay] = posicoes[autor];
    const testemunhas = Object.keys(posicoes).filter(k => k !== autor && distancia(posicoes[k][0] - ax, posicoes[k][1] - ay) <= raios[k])
      .sort(comparaStr);
    const [n, contribuicao, p] = this.conta(this.pontuacoes, autor).somar(tick, ato, alvo, valor);
    const reputacao: AtoRegistrado["reputacao"] = {};
    for (const k of testemunhas) {
      const [nk, ck, rk] = this.conta(this.reputacoes, `${autor}|${k}`).somar(tick, ato, alvo, valor);
      reputacao[k] = { repeticao: nk, contribuicao: ck, depois: rk };
    }
    this.atos.push({ tick, ato, autor, alvo, comida, sinal, efeito, valor, repeticao: n, contribuicao, pontuacao_depois: p, testemunhas,
                     reputacao });
  }

  // ------------------------------------------------------------ leitura
  pontuacao(ident: string, tick: number): number {
    return this.pontuacoes.get(ident)?.em(tick) ?? 0;
  }

  reputacao(ident: string, vistaPor: string, tick: number): number {
    return this.reputacoes.get(`${ident}|${vistaPor}`)?.em(tick) ?? 0;
  }

  /** os atos, a pontuacao de cada pet e a reputacao de cada um vista por cada outro, no tick */
  resumo(ids: readonly string[], tick: number): Record<string, unknown> {
    return {
      atos: this.atos,
      pontuacao: Object.fromEntries(ids.map(i => [i, this.pontuacao(i, tick)])),
      reputacao: Object.fromEntries(ids.map(i => [i, Object.fromEntries(ids.filter(k => k !== i).map(k => [k, this.reputacao(i, k, tick)]))])),
      ...(this.cfg.co6 ? { peso_dever: Object.fromEntries(ids.map(i => [i, this.pesoDever(i)])) } : {}),
    };
  }
}
