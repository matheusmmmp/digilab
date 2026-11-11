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

   Nenhuma versao de pet nova aqui: o save e os dois ovos sao a CO4c. */
import { CMU_GRANDE, CMU_MVP, CMU_MVP_AGUA, TICK_INICIAL, nasceNaAgua, nasceNaGrande, type ConfigMundo } from "./constantes.ts";
import { CONFIG_GRUPO_LIGADA, Grupo, ROTULO_SEGUNDO_PET } from "./grupo.ts";
import { Motor } from "./motor.ts";
import type { EventoRegistro } from "./tipos.ts";
import { derivarSemente } from "./mundo.ts";

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

  constructor(semente: number, versao: number) {
    if (!Number.isInteger(semente) || semente < 0 || semente > 0xffffffff) throw new Error(`semente do grupo fora dos 32 bits: ${semente}`);
    this.semente = semente;
    this.versao = versao;
    this.grupo = new Grupo(mundoDaVersao(versao), semente, CONFIG_GRUPO_LIGADA,
                           { tickInicial: TICK_INICIAL, sementeDoSegundo: sementeDoSegundoJogo });
    const motores: Record<string, Motor> = {};
    for (const ident of CONFIG_GRUPO_LIGADA.ids) {
      const s = Number(this.grupo.sementes[ident]);
      motores[ident] = this.grupo.entrarMotor(ident, TICK_INICIAL, parte => new Motor(s, versao, { parteDoMundo: parte }), "jogo", "jogador") as Motor;
    }
    this.motores = Object.freeze(motores);
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
    const u = this.log[this.log.length - 1];
    if (u && u[1] === "t" && u[3] === null && u[0] + (u[2] as number) === this.tick) u[2] = (u[2] as number) + n;
    else this.log.push([this.tick, "t", n, null]);
    this._avancar(n);
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
    const m = this.motor(ident), antes = m.log.length, ultimo = antes > 0 ? JSON.stringify(m.log[antes - 1]) : null;
    const r = f(m);
    if (m.log.length < antes || (antes > 0 && JSON.stringify(m.log[antes - 1]) !== ultimo))
      throw new Error(`a acao do dono reescreveu o registro do pet ${ident}`);
    for (const ev of m.log.slice(antes)) {
      if (ev[1] === "t") throw new Error(`a acao do dono andou o tempo do pet ${ident}: o tempo e do grupo`);
      this.log.push([ev[0], ev[1], ev[2], ident]);
    }
    return r;
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

  // ------------------------------------------------------------ leitura
  /** a assinatura do grupo: a de cada pet, o mundo partilhado e as vezes, os contatos e as disputas (o que o replay tem de refazer) */
  assinatura(): string {
    const g = this.grupo;
    return JSON.stringify([this.versao, this.semente, this.tick, Object.fromEntries(Object.entries(this.motores).map(([i, m]) => [i, m.assinatura()])),
                           g.comum.resumo(), g.ordens, g.contatos, g.disputas]);
  }
}
