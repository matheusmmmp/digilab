/* Treino, fadiga e sobrecarga (espelho de treino_stats.py; integrado tick a tick). Estado proprio: nada
   disso entra nas necessidades. Evolucao zera fadiga e estresse; pontos e sobrecarga ficam. */
import { APTIDAO, CCOND, CTR, STATS, TICK_INICIAL } from "./constantes.ts";
import type { Especie, Estagio, EstagioTreino, Exercicio, Stat, Stats } from "./tipos.ts";

export interface ResultadoSessao { forcada: boolean; enrolou: boolean; ganho: Partial<Stats>; fadigaAntes: number }

export class TreinoPet {
  esp: Especie;
  pontos: Stats;
  pontosEst: Record<EstagioTreino, number> = { crianca: 0, adolescente: 0, adulto: 0 };
  fadiga = 0;
  sobrecarga = 0;
  estresse = 0;
  tick = TICK_INICIAL;
  estagio: Estagio = "bebe";
  dormindo = false;
  inicioSono: number | null = null;
  bem = true;
  ultimo: number | null = null;
  sessoes = 0;
  forcadas = 0;
  enroladas = 0;
  constructor(esp: Especie) {
    if (!APTIDAO[esp]) throw new Error("espécie sem aptidão de treino: " + esp);
    this.esp = esp; this.pontos = Object.fromEntries(STATS.map(k => [k, 0])) as Stats;
  }
  avancar(tick: number, dormindo: boolean, bem: boolean, estagio: Estagio): void {
    if (tick < this.tick) throw new Error("treino: tempo voltou");
    const dt = tick - this.tick;
    if (dt && !this.dormindo) {
      this.fadiga = Math.max(0, this.fadiga - CTR.recuperaHora * dt / 60);
      if (this.bem) this.sobrecarga = Math.max(0, this.sobrecarga - CTR.decaiHora * dt / 60);
    }
    this.tick = tick;
    if (estagio !== this.estagio) { this.estagio = estagio; this.fadiga = 0; this.estresse = 0; }
    if (dormindo && !this.dormindo) { this.fadiga = 0; this.inicioSono = tick; }
    else if (!dormindo && this.dormindo) {
      if (this.inicioSono !== null && tick - this.inicioSono >= CTR.sonoCompleto) this.sobrecarga = Math.max(0, this.sobrecarga - CTR.decaiSono);
      this.inicioSono = null;
    }
    this.dormindo = dormindo; this.bem = bem;
  }
  podeTocar(t: number): boolean { return this.ultimo === null || t - this.ultimo >= CTR.intervalo; }
  get forcaria(): boolean { return this.fadiga >= CTR.limiteForcar; }
  get pedePausa(): boolean { return this.fadiga >= CTR.limiarPausa; }
  get total(): number { return STATS.reduce((a, k) => a + this.pontos[k], 0); }
  sessao(t: number, ex: Exercicio, obedece: boolean): ResultadoSessao {
    if (!CTR.exercicios[ex]) throw new Error("exercício desconhecido: " + ex);
    if (!(this.estagio in CTR.tetoEstagio)) throw new Error(`${this.estagio} não treina`);
    if (!this.podeTocar(t)) throw new Error("dentro do intervalo mínimo entre treinos");
    const forcada = this.forcaria, fadigaAntes = this.fadiga;
    this.ultimo = t; this.sessoes++;
    if (forcada) { this.sobrecarga = Math.min(CTR.sobreMax, this.sobrecarga + CTR.sobreForcar); this.estresse += CTR.estresseForcar; this.forcadas++; }
    if (!obedece) { this.enroladas++; return { forcada, enrolou: true, ganho: {}, fadigaAntes }; }
    const est = this.estagio as EstagioTreino;
    const mult = forcada ? CTR.multForcar : 1 - this.fadiga / 100, apt = APTIDAO[this.esp], ganho: Partial<Stats> = {};
    const [pri, sec] = CTR.exercicios[ex];
    for (const [st, base] of [[pri, CTR.ganhoPri], [sec, CTR.ganhoSec]] as [Stat, number][]) {
      let g = base * apt[st] * (1 - this.pontos[st] / CTR.tetoStat) * mult;
      g = Math.max(0, Math.min(g, CTR.tetoStat - this.pontos[st], CTR.tetoEstagio[est] - this.pontosEst[est], CTR.tetoVida - this.total));
      this.pontos[st] += g; this.pontosEst[est] += g; ganho[st] = g;
    }
    this.fadiga = Math.min(100, this.fadiga + CTR.fadigaSessao);
    return { forcada, enrolou: false, ganho, fadigaAntes };
  }
  assinatura(): unknown[] {
    return [this.pontos, this.pontosEst, this.fadiga, this.sobrecarga, this.estresse, this.tick, this.estagio, this.dormindo,
      this.inicioSono, this.bem, this.ultimo, this.sessoes, this.forcadas, this.enroladas];
  }
}
/** condicao do cuidado no combate: saude 0 -> 0,95; 1 -> 1,05 */
export const condicaoDe = (saude: number): number => CCOND.min + (CCOND.max - CCOND.min) * Math.max(0, Math.min(1, saude));
