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
   so com os atos de i que k testemunhou (k ve i no momento do ato). Nada aqui sabe de tela: nenhum numero vai para o jogador (D-MM-8). */
import { CCOOP } from "./constantes.ts";
import { distancia, divArred } from "./mundo.ts";

export const ATOS_COOP = ["disputa", "contencao", "encostar"] as const;
export type AtoCoop = typeof ATOS_COOP[number];
export const TIPOS_MADUROS: readonly string[] = ["racao", "a", "b", "c"];
export const BITS_FRACAO_COOP = 16;

/** a ConfigCooperacao do Python (o CCOOP e o espelho conferido); `ligada` fica com quem a usa */
export interface ConfigCooperacao { ligada: boolean; escala: number; pisoFome: number; meiaVida: number; kMeiaVida: number; janelaNovidade: number }
export const CONFIG_COOPERACAO: Readonly<ConfigCooperacao> = Object.freeze({ ligada: false, ...CCOOP });
export const CONFIG_COOPERACAO_LIGADA: Readonly<ConfigCooperacao> = Object.freeze({ ...CONFIG_COOPERACAO, ligada: true });

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
  constructor(cfg: Readonly<ConfigCooperacao>) {
    this.cfg = cfg;
  }

  private brutoEm(tick: number): number {
    return decair(this.bruto, tick - this.tick, this.cfg.kMeiaVida);
  }

  em(tick: number): number {
    return divArred(this.brutoEm(tick), 2 ** BITS_FRACAO_COOP);
  }

  /** [a repeticao, a contribuicao, o valor depois] */
  somar(tick: number, ato: string, alvo: string, valor: number): [number, number, number] {
    this.bruto = this.brutoEm(tick);
    this.tick = tick;
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

  constructor(cfg: Readonly<ConfigCooperacao>) {
    if (!cfg.ligada) throw new Error("a Cooperacao so existe com a ConfigCooperacao ligada");
    for (const n of ["escala", "meiaVida", "kMeiaVida", "janelaNovidade"] as const)
      if (!Number.isInteger(cfg[n]) || cfg[n] <= 0) throw new Error(`ConfigCooperacao.${n} tem de ser inteiro positivo: ${cfg[n]}`);
    if (!(cfg.pisoFome > 0 && cfg.pisoFome < 1)) throw new Error(`ConfigCooperacao.pisoFome em (0, 1): ${cfg.pisoFome}`);
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
    };
  }
}
