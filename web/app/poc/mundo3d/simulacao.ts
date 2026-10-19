/* O simulador do WORLD-POC-01a: junta o mundo, os sensores, o cérebro e o controlador no laço do contrato
   (Mundo -> Observação -> cérebro -> Intenção -> controlador -> Mundo -> consequências), com as duas rng separadas (a do ambiente e a da
   política, derivadas da semente) e o log de eventos (event sourcing, como o jogo). O replay é refazer o log: `reproduzir`. Sem DOM. */
import { INTERVALO_DECISAO } from "./config.ts";
import { Controlador } from "./controlador.ts";
import { cerebroDeTeste } from "./cerebro.ts";
import { Rng, derivarSemente, distancia, fnv1a } from "./inteiros.ts";
import { Mundo } from "./mundo.ts";
import type { RegistroDecisao } from "./registro.ts";
import { ler } from "./sensores.ts";
import type { Cerebro, Observacao, ResultadoPercebido } from "./tipos.ts";

export type Evento = { tipo: "avancar"; ticks: number } | { tipo: "deixar_comida"; x: number; y: number };

interface EmCurso {
  registro: Omit<RegistroDecisao, "executada" | "fisico" | "corpo_depois" | "percebido">;
  controlador: Controlador;
  distancia: number;
  petDe: [number, number]; bolaDe: [number, number];
  comeu0: number; empurroes0: number;
  bolaVista0: number | null;
}

export class Simulacao {
  readonly mundo: Mundo;
  readonly log: Evento[] = [];
  readonly registros: RegistroDecisao[] = [];
  private readonly rngPolitica: Rng;
  private emCurso: EmCurso | null = null;
  private percebido: ResultadoPercebido | null = null;
  readonly semente: number;
  private readonly cerebro: Cerebro;

  constructor(semente: number, cerebro: Cerebro = cerebroDeTeste) {
    this.semente = semente;
    this.cerebro = cerebro;
    this.mundo = new Mundo(new Rng(derivarSemente(semente, "ambiente")));
    this.rngPolitica = new Rng(derivarSemente(semente, "politica"));
  }

  /** o passo do replay: aplica um evento do log (um evento desconhecido falha alto) */
  aplicarEvento(e: Evento): void {
    if (e.tipo === "avancar") {
      if (!Number.isInteger(e.ticks) || e.ticks < 0) throw new Error(`avancar com ticks invalidos: ${e.ticks}`);
      for (let i = 0; i < e.ticks; i++) this.tick();
    } else if (e.tipo === "deixar_comida") this.mundo.deixarComida(e.x, e.y);
    else throw new Error(`evento desconhecido: ${JSON.stringify(e)}`);
    this.log.push(e);
  }

  avancar(ticks: number): void { this.aplicarEvento({ tipo: "avancar", ticks }); }

  private tick(): void {
    const m = this.mundo;
    if (m.tick % INTERVALO_DECISAO === 0) this.decidir();
    const ec = this.emCurso!;
    const antes: [number, number] = [m.pet.x, m.pet.y];
    const cmd = ec.controlador.passo(m);
    m.passo(cmd.vx, cmd.vy, cmd.podeComer);
    ec.distancia += distancia(m.pet.x - antes[0], m.pet.y - antes[1]);
  }

  /** fecha a decisão em curso e abre a próxima: os sensores leem, o cérebro decide, o controlador recebe a Intenção */
  private decidir(): void {
    this.fechar();
    const m = this.mundo;
    const { obs, refs } = ler(m, this.percebido);
    const intencao = this.cerebro.decidir(JSON.parse(JSON.stringify(obs)) as Observacao, this.rngPolitica);
    const controlador = new Controlador(intencao, refs, m);
    this.emCurso = {
      registro: { n: this.registros.length, tick: m.tick, observacao: obs, intencao, corpo_antes: { fome: m.pet.fome, tedio: m.pet.tedio } },
      controlador, distancia: 0, petDe: [m.pet.x, m.pet.y], bolaDe: [m.bola.x, m.bola.y], comeu0: m.comeu, empurroes0: m.empurroes,
      bolaVista0: distanciaDaBola(obs),
    };
  }

  /** fecha a decisão em curso no registro; o resultado percebido vai para a próxima Observação */
  private fechar(): void {
    const ec = this.emCurso;
    if (ec === null) return;
    const m = this.mundo, c = ec.controlador, r = ec.registro;
    const parou_por = c.status ?? "hora";
    const comeu = m.comeu - ec.comeu0, empurroes = m.empurroes - ec.empurroes0;
    const { obs } = ler(m, null, false);
    const bolaVista1 = distanciaDaBola(obs);
    const percebido: ResultadoPercebido = {
      parou_por, comeu: comeu > 0, empurrou: empurroes > 0,
      bola_afastou: ec.bolaVista0 !== null && bolaVista1 !== null ? bolaVista1 - ec.bolaVista0 : null,
    };
    this.registros.push({
      n: r.n, tick: r.tick, observacao: r.observacao, intencao: r.intencao,
      executada: { ticks: c.ticks, distancia: ec.distancia, parou_por },
      fisico: { pet_de: ec.petDe, pet_para: [m.pet.x, m.pet.y], bola_de: ec.bolaDe, bola_para: [m.bola.x, m.bola.y], comeu, empurroes,
        contatos: m.contatos.map(k => ({ ...k })) },
      corpo_antes: r.corpo_antes, corpo_depois: { fome: m.pet.fome, tedio: m.pet.tedio },
      percebido,
    });
    this.percebido = percebido;
    this.emCurso = null;
  }

  /** o estado inteiro (a verdade, em JSON puro) e o hash dele */
  estado() {
    return { semente: this.semente, mundo: this.mundo.estado(), rng_politica: this.rngPolitica.estado, n_registros: this.registros.length };
  }
  hash(): string { return fnv1a(JSON.stringify(this.estado())); }
}

/** a distância percebida até a bola, ou null se ela não está à vista */
const distanciaDaBola = (obs: Observacao): number | null => obs.vistos.find(v => v.categoria === "bola")?.distancia ?? null;

/** refaz uma vida pelo log */
export function reproduzir(semente: number, log: readonly Evento[], cerebro?: Cerebro): Simulacao {
  const s = new Simulacao(semente, cerebro);
  for (const e of log) s.aplicarEvento(e);
  return s;
}
