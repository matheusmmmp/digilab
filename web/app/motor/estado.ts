/* Camada 1 — estado e necessidades (espelho de state.py). Deterministico; o ambiente, nao o agente. */
import { C, CTP, EIXOS_TEMP, TICK_INICIAL, TPD } from "./constantes.ts";
import { criarRng, hashSemente, type Rng } from "./rng.ts";
import type { AcaoDono, AcaoPet, EstadoVida, Observacao, Temperamento } from "./tipos.ts";

export const clamp = (x: number): number => Math.max(0, Math.min(1, x));
export const eNoite = (t: number): boolean => C.iniNoite > C.fimNoite ? (t >= C.iniNoite || t < C.fimNoite) : (t >= C.iniNoite && t < C.fimNoite);

/** uniforme em [-amplitude, amplitude] por eixo, pela semente do ovo (stream propria) */
export function temperamentoDe(semente: number): Temperamento {
  const r = criarRng(hashSemente("temperamento", semente));
  return Object.freeze(Object.fromEntries(EIXOS_TEMP.map(e => [e, CTP.amplitude * (2 * r.random() - 1)]))) as Temperamento;
}

export function estadoInicial(): EstadoVida {
  return { tick: TICK_INICIAL, fome: .8, higiene: 1, energia: .9, humor: .7, saude: 1, sujeira: 0, dormindo: false, ultimoCuidado: TICK_INICIAL, totalCuidados: 0 };
}
export function vetor(e: EstadoVida): number[] { return [e.fome, e.higiene, e.energia, e.humor, e.saude, e.sujeira / 5, e.dormindo ? 1 : 0, (e.tick % TPD) / TPD]; }
export function observacao(e: EstadoVida): Observacao { return { v: vetor(e), tdc: e.tick - e.ultimoCuidado }; }

export function avancarTick(e: EstadoVida, rng: Pick<Rng, "random">): EstadoVida {
  const mult = eNoite(e.tick % TPD) ? C.multNoite : 1;
  const n = { ...e };
  n.fome = clamp(e.fome - C.decFome);
  n.higiene = clamp(e.higiene - C.decHig * (1 + C.penHigSuj * e.sujeira));
  n.humor = clamp(e.humor - C.decHum);
  n.energia = clamp(e.dormindo ? e.energia + C.enSono : e.energia - C.decEn * mult);
  if (!e.dormindo && rng.random() < C.probSuj) n.sujeira = Math.min(C.sujMax, e.sujeira + 1);
  const priv = Math.min(n.fome, n.higiene, n.energia) < .15;
  n.saude = clamp(e.saude + (priv ? -C.danoSaude : C.curaSaude));
  n.tick = e.tick + 1;
  return n;
}
export function aplicarAcaoDono(e: EstadoVida, a: AcaoDono, rng: Pick<Rng, "random">): EstadoVida {
  const n = { ...e };
  if (a === "alimentar") { n.fome = clamp(n.fome + C.ganhoAlim); if (rng.random() < C.probSujRef) n.sujeira = Math.min(C.sujMax, n.sujeira + 1); }
  else if (a === "limpar") { n.higiene = clamp(n.higiene + C.ganhoLimpar); n.sujeira = Math.max(0, n.sujeira - 1); }
  else if (a === "brincar") { n.humor = clamp(n.humor + C.ganhoBrincHum); n.energia = clamp(n.energia - C.custoBrincEn); n.fome = clamp(n.fome - C.custoBrincFome); n.dormindo = false; }
  else if (a === "acariciar") { n.humor = clamp(n.humor + C.ganhoElogiar * .6); }
  else if (a === "elogiar") { n.humor = clamp(n.humor + C.ganhoElogiar); }
  else if (a === "repreender") { n.humor = clamp(n.humor - C.custoRepr); }
  else throw new Error("acao de dono desconhecida: " + a);
  n.ultimoCuidado = n.tick; n.totalCuidados = n.totalCuidados + 1;
  return n;
}
export function efeitoAcaoPet(e: EstadoVida, a: AcaoPet): EstadoVida {
  if (a === "dormir") return { ...e, dormindo: true };
  const n = { ...e, dormindo: false };
  if (a === "brincar") { n.humor = clamp(n.humor + C.humBrinc * C.intervalo); n.energia = clamp(n.energia - .02); }
  else if (a === "explorar") { n.energia = clamp(n.energia - .015); n.humor = clamp(n.humor + .01); }
  else if (a === "comer") { n.fome = clamp(n.fome + .05); }
  else if (a === "emburrar") { n.humor = clamp(n.humor - .01); }
  return n;
}
