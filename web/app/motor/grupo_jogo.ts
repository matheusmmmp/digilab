/* Os dois pets do jogo no mesmo mundo (docs/TAREFA_V3_COOPERACAO.md, etapa CO4b): o Motor do jogo dentro do Grupo (motor/grupo.ts).

   Cada pet e um Motor inteiro (o corpo, o cerebro, os chamados, a evolucao, a luta), com a semente dele e a parte dele no mundo do grupo. O
   tempo anda pelo grupo, um tick por vez: em cada tick, os pets que decidem andam na vez sorteada (o fluxo `mundo-ordem`), e depois os que
   nao decidem; no fim do tick com decisao, o toque e a disputa. E o `Grupo._avancar` do Python com o `_um_tick()` de cada motor.

   O registro do grupo do jogo e um so, na ordem em que tudo aconteceu: [tick do mundo, tipo, valor, pet]. O avanco e do grupo (pet null);
   todo outro evento e o registro de hoje de um pet (o "d", o "dc", o "l", o "p"...), com o id dele. O replay (`reproduzir`) rejoga os eventos
   no mesmo relogio e falha alto se o registro refeito diferir do lido. O registro de cada Motor (o log dele) e a projecao desse, e o Grupo
   guarda so a entrada e o avanco (o dono do jogo age pelo Motor).

   As sementes: o primeiro pet usa a do grupo; o segundo, `derivarSemente("segundo-pet", s)` cortada aos 32 bits das sementes do jogo (D-CO4b-2).
   Os dois nascem juntos, no tick de nascimento do jogo (TICK_INICIAL), que e o comeco do relogio do mundo (D-CO4b-3).

   Os pets sao da v26 (a v25 no grupo; CO4c; motor/constantes.ts): o pet v26 so existe no grupo. O `avancar` de qualquer um dos dois anda o grupo inteiro,
   para o relogio do jogo e as telas, que leem o pet em foco, seguirem como hoje (src/jogo.ts). */
import { CMU_GRANDE, CMU_MVP, CMU_MVP_AGUA, TICK_INICIAL, VERSAO_V26, VERSAO_V28, ehDoGrupo, nasceNaAgua, nasceNaGrande, type ConfigMundo } from "./constantes.ts";
import { CONFIG_GRUPO_LIGADA, Grupo, ROTULO_SEGUNDO_PET } from "./grupo.ts";
import { CONFIG_COOPERACAO_LIGADA } from "./cooperacao.ts";
import { Motor } from "./motor.ts";
import type { EventoRegistro } from "./tipos.ts";
import { derivarSemente } from "./mundo.ts";

/** o gesto do irmao que assistiu a luta (D-MM-2; CO5): consola, comemora ou provoca */
export type GestoDoIrmao = "consola" | "comemora" | "provoca";
/** "Resultado e reputacao" (Matheus, 2026-11-11, D-CO5-2): com a reputacao do lutador vista pelo irmao (a medida da CO3) negativa, ele
    provoca; senao, comemora a vitoria e consola a derrota e o empate. Sem sorteio, e nada muda a luta nem o registro: o gesto e derivado */
export function gestoDepoisDaLuta(reputacao: number, venceu: boolean | null): GestoDoIrmao {
  if (reputacao < 0) return "provoca";
  return venceu === true ? "comemora" : "consola";
}

/** [tick do mundo, tipo, valor, pet]: pet null so no avanco do grupo ("t") */
export type EventoGrupoJogo = [number, string, unknown, string | null];

/** a semente do segundo pet do jogo: a do Python, nos 32 bits das sementes do jogo (D-CO4b-2) */
export function sementeDoSegundoJogo(semente: number | bigint): number {
  return Number(derivarSemente(ROTULO_SEGUNDO_PET, semente) & 0xffffffffn);
}

/** o mundo de uma versao de pet (o mesmo do construtor do Motor) */
export function mundoDaVersao(versao: number): ConfigMundo {
  return nasceNaGrande(versao) ? CMU_GRANDE : nasceNaAgua(versao) ? CMU_MVP_AGUA : CMU_MVP;
}

export class GrupoDoJogo {
  readonly grupo: Grupo;
  readonly versao: number;
  readonly semente: number;
  readonly motores: Readonly<Record<string, Motor>>;
  readonly log: EventoGrupoJogo[] = [];

  /** `medir`: a medida da cooperacao (CO3), ligada no jogo; desligada so no teste do G-SEM-DECISAO (ela nao muda nada) */
  constructor(semente: number, versao: number, medir = true) {
    if (!Number.isInteger(semente) || semente < 0 || semente > 0xffffffff) throw new Error(`semente do grupo fora dos 32 bits: ${semente}`);
    if (!ehDoGrupo(versao)) throw new Error(`o grupo do jogo e de pets v${VERSAO_V26} ou v${VERSAO_V28}, nao v${versao}`);
    this.semente = semente;
    this.versao = versao;
    this.grupo = new Grupo(mundoDaVersao(versao), semente, CONFIG_GRUPO_LIGADA,
                           { tickInicial: TICK_INICIAL, sementeDoSegundo: sementeDoSegundoJogo, ...(medir ? { cooperacao: CONFIG_COOPERACAO_LIGADA } : {}) });   // a medida (CO3), ligada no jogo (CO5): so mede
    const motores: Record<string, Motor> = {};
    for (const ident of CONFIG_GRUPO_LIGADA.ids) {
      const s = Number(this.grupo.sementes[ident]);
      motores[ident] = this.grupo.entrarMotor(ident, TICK_INICIAL, parte => new Motor(s, versao, { parteDoMundo: parte }), "jogo", "jogador") as Motor;
    }
    this.motores = Object.freeze(motores);
    /* CO4c: o avancar de qualquer um dos dois anda o grupo (o relogio do jogo chama o do pet em foco) */
    for (const m of Object.values(motores)) m.ligarAvancoDoGrupo(n => this.avancar(n));
  }

  get ids(): readonly string[] { return CONFIG_GRUPO_LIGADA.ids; }
  get tick(): number { return this.grupo.tick; }

  motor(ident: string): Motor {
    const m = this.motores[ident];
    if (m === undefined) throw new Error(`pet fora do grupo: ${ident}`);
    return m;
  }

  // ------------------------------------------------------------ o tempo
  /** um avanco do grupo: o "t" no registro do grupo e no de cada pet, os ticks intercalados no Grupo e, no fim, a conferencia da morte */
  avancar(n: number): void {
    if (!Number.isInteger(n) || n <= 0) throw new Error(`avanco precisa de ticks inteiros positivos: ${n}`);
    this.descarregar();                          // dentro de uma acao do dono: o que o pet gravou antes do tempo vem antes dele
    const u = this.log[this.log.length - 1];
    if (u && u[1] === "t" && u[3] === null && u[0] + (u[2] as number) === this.tick) u[2] = (u[2] as number) + n;
    else this.log.push([this.tick, "t", n, null]);
    this._avancar(n);
    if (this.acao !== null) this.acao.cursor = this.motor(this.acao.ident).log.length;   // o "t" do pet ja esta no registro do grupo
  }

  private _avancar(n: number): void {
    for (const m of Object.values(this.motores)) m.abrirAvancoNoGrupo(n);
    this.grupo.avancar(n);
    for (const [i, m] of Object.entries(this.motores)) {
      m.fecharAvancoNoGrupo();
      if (m.e.tick !== this.tick) throw new Error(`o relogio do pet ${i} (${m.e.tick}) saiu do relogio do mundo (${this.tick})`);
    }
  }

  // ------------------------------------------------------------ o dono
  /** o dono faz algo com o pet `ident` pelo Motor dele (observar, deixarBola, lutarPoc...): o que o Motor grava no registro dele vai ao
      registro do grupo, com o id. Um avanco dentro da acao falha alto (o tempo e do grupo) */
  agir<T>(ident: string, f: (m: Motor) => T): T {
    if (this.acao !== null) throw new Error(`acao do dono dentro de outra (do pet ${this.acao.ident})`);
    const m = this.motor(ident);
    this.acao = { ident, cursor: m.log.length };
    try {
      const r = f(m);
      this.descarregar();
      return r;
    } finally {
      this.acao = null;
    }
  }
  /** a acao do dono em andamento: o pet e ate onde o registro dele ja foi para o do grupo. Um avanco dentro dela (o relogio do jogo pelo
      `mudarMotor`, CO4c) entra no registro do grupo na ordem certa: o que veio antes, o "t", e o que veio depois */
  private acao: { ident: string; cursor: number } | null = null;
  private descarregar(): void {
    if (this.acao === null) return;
    const m = this.motor(this.acao.ident);
    if (m.log.length < this.acao.cursor) throw new Error(`a acao do dono reescreveu o registro do pet ${this.acao.ident}`);
    for (const ev of m.log.slice(this.acao.cursor)) {
      if (ev[1] === "t") throw new Error(`o pet ${this.acao.ident} andou o tempo por fora do grupo`);
      this.log.push([ev[0], ev[1], ev[2], this.acao.ident]);
    }
    this.acao.cursor = m.log.length;
  }

  // ------------------------------------------------------------ o replay
  /** Refaz o grupo e rejoga o registro no mesmo relogio. Evento fora do tick, de pet de fora, desconhecido ou o registro refeito diferente
      do lido falham alto */
  static reproduzir(semente: number, versao: number, log: readonly EventoGrupoJogo[]): GrupoDoJogo {
    const g = new GrupoDoJogo(semente, versao);
    for (const ev of log) {
      if (!Array.isArray(ev) || ev.length !== 4) throw new Error(`evento do grupo malformado: ${JSON.stringify(ev)}`);
      const [t, tipo, valor, pet] = ev;
      if (t !== g.tick) throw new Error(`evento no tick ${t} com o grupo no tick ${g.tick}: ${JSON.stringify(ev)}`);
      if (pet === null) {
        if (tipo !== "t") throw new Error(`evento sem pet que nao e o avanco: ${JSON.stringify(ev)}`);
        g.avancar(valor as number);
      } else {
        if (tipo === "t") throw new Error(`avanco com pet no registro do grupo: ${JSON.stringify(ev)}`);
        const m = g.motor(pet);
        const evento = [t, tipo, valor] as unknown as EventoRegistro;
        const antes = m.log.length;
        m.aplicarEvento(evento);
        if (m.log.length === antes) m.log.push(JSON.parse(JSON.stringify(evento)) as EventoRegistro);   // o aplicarEvento nao grava
        g.log.push([t, tipo, JSON.parse(JSON.stringify(valor ?? null)), pet]);
      }
    }
    if (JSON.stringify(g.log) !== JSON.stringify(log)) throw new Error("o replay refez um registro do grupo diferente do lido");
    return g;
  }

  /** o gesto do irmao do `lutador` depois da luta dele, pela reputacao do lutador vista pelo irmao agora (CO5) */
  gestoDoIrmao(lutador: string, venceu: boolean | null): { irmao: string; gesto: GestoDoIrmao } {
    const irmao = this.ids.find(i => i !== lutador);
    if (irmao === undefined || !this.ids.includes(lutador)) throw new Error(`lutador fora do grupo: ${lutador}`);
    const c = this.grupo.coop;
    if (c === null) throw new Error("o gesto do irmao le a medida da cooperacao, desligada");
    return { irmao, gesto: gestoDepoisDaLuta(c.reputacao(lutador, irmao, this.tick), venceu) };
  }

  // ------------------------------------------------------------ leitura
  /** a assinatura do grupo: a de cada pet, o mundo partilhado e as vezes, os contatos e as disputas (o que o replay tem de refazer) */
  assinatura(): string {
    const g = this.grupo;
    return JSON.stringify([this.versao, this.semente, this.tick, Object.fromEntries(Object.entries(this.motores).map(([i, m]) => [i, m.assinatura()])),
                           g.comum.resumo(), g.ordens, g.contatos, g.disputas]);
  }
}
