/* Tamer: o jogador (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 4 e 5; so no jogo). As medalhas sao dele, nao do pet, e
   sobrevivem ao pet. Registro proprio, com event sourcing como o do pet: a chave CHAVE-tamer guarda so os eventos
   {versao, log}; o estado (quais medalhas, com que pet) e reconstruido reprocessando o registro. Evento desconhecido
   falha alto. O formato do save do pet nao muda.

   O motor do pet NUNCA le o Tamer por fora (o replay do pet tem de dar o mesmo resultado sozinho): quando o Tamer tem
   mais medalhas do que o pet ativo conhece, o app grava no registro do pet o evento "u" (Motor.liberar), e o motor
   re-verifica a evolucao nessa hora. Um pet guardado recebe o "u" quando volta a ser o ativo. */
import { LUGARES_V5, MEDALHAS, MEDALHA_POR_ID, Motor, NPC, PetMorto, nomeForma, type Medalha } from "../motor/index.ts";
import { CHAVE, type Armazenamento } from "./save.ts";

export const CHAVE_TAMER = CHAVE + "-tamer";
/** aviso pendente de que os pets antigos foram descartados (sai quando o jogador le) */
export const CHAVE_AVISO_V6 = CHAVE + "-aviso-v6";
export const VERSAO_TAMER = 1;

/** uma medalha ganha: qual, o contador (1 = a primeira), a hora de parede, o pet que venceu (semente, forma e tick dele) */
export interface MedalhaGanha { id: string; n: number; quando: number; pet: number; forma: string; tick: number }
export type EventoTamer = ["medalha", MedalhaGanha];

export class Tamer {
  log: EventoTamer[] = [];
  /** estado reconstruido: as medalhas na ordem em que foram ganhas */
  medalhas: MedalhaGanha[] = [];
  get n(): number { return this.medalhas.length; }
  tem(id: string): boolean { return this.medalhas.some(x => x.id === id); }
  ganha(id: string): MedalhaGanha | null { return this.medalhas.find(x => x.id === id) ?? null; }

  /** um evento do registro (replay): confere tudo antes de aplicar */
  aplicar(ev: EventoTamer): void {
    if (!Array.isArray(ev) || ev[0] !== "medalha") throw new Error("tipo de evento desconhecido no registro do Tamer: " + JSON.stringify(Array.isArray(ev) ? ev[0] : ev));
    const x = ev[1];
    if (!x || !MEDALHA_POR_ID[x.id]) throw new Error("medalha desconhecida no registro do Tamer: " + JSON.stringify(x?.id));
    if (this.tem(x.id)) throw new Error(`medalha repetida no registro do Tamer: ${x.id}`);
    if (x.n !== this.n + 1) throw new Error(`contador fora de ordem no registro do Tamer: ${x.n} (esperado ${this.n + 1})`);
    for (const k of ["quando", "pet", "tick"] as const) if (!Number.isFinite(x[k])) throw new Error(`medalha ${x.id} sem ${k} no registro do Tamer`);
    if (typeof x.forma !== "string") throw new Error(`medalha ${x.id} sem a forma do pet no registro do Tamer`);
    this.medalhas.push({ ...x });
  }
  /** ganha a medalha agora, com o pet m (grava o evento e aplica) */
  ganhar(id: string, m: Motor, quando: number = Date.now()): MedalhaGanha {
    const ev: EventoTamer = ["medalha", { id, n: this.n + 1, quando, pet: m.semente, forma: nomeForma(m.forma), tick: m.e.tick }];
    this.aplicar(ev);
    this.log.push(ev);
    return this.medalhas[this.n - 1];
  }
  static reproduzir(log: readonly EventoTamer[]): Tamer {
    const t = new Tamer();
    for (const ev of log) t.aplicar(ev);
    t.log = log.map(ev => [ev[0], { ...ev[1] }] as EventoTamer);
    return t;
  }
}

/** le o registro do Tamer (sem a chave: um Tamer novo, sem medalhas). Registro que nao reproduz falha alto */
export function lerTamer(armaz: Armazenamento): Tamer {
  const bruto = armaz.getItem(CHAVE_TAMER);
  if (bruto === null) return new Tamer();
  let d: unknown;
  try { d = JSON.parse(bruto); } catch (err) { throw new Error("o registro do Tamer não é JSON: " + (err instanceof Error ? err.message : String(err))); }
  const s = d as { versao?: unknown; log?: unknown };
  if (s.versao !== VERSAO_TAMER || !Array.isArray(s.log)) throw new Error("o registro do Tamer não tem versão " + VERSAO_TAMER + " e eventos");
  return Tamer.reproduzir(s.log as EventoTamer[]);
}
export const textoTamer = (t: Tamer): string => JSON.stringify({ versao: VERSAO_TAMER, log: t.log });
export function gravarTamer(armaz: Armazenamento, t: Tamer): void { armaz.setItem(CHAVE_TAMER, textoTamer(t)); }

/** medalhas que o pet acabou de ganhar para o Tamer: a primeira vitoria dele contra um lider cuja medalha o Tamer
    ainda nao tem. So pets v6 (os v1-v5 nao tem Tamer). Devolve as medalhas novas (ja aplicadas ao Tamer) */
export function conferirMedalhas(t: Tamer, m: Motor, quando: number = Date.now()): MedalhaGanha[] {
  if (m.versao < 6) return [];
  const novas: MedalhaGanha[] = [];
  for (const md of MEDALHAS) if (!t.tem(md.id) && (m.campanha[md.lider] ?? 0) > 0) novas.push(t.ganhar(md.id, m, quando));
  return novas;
}
/** o pet passa a conhecer as medalhas do Tamer (evento "u" no registro dele). Pet v1-v5 ou morto: nada.
    Devolve true se o registro do pet mudou */
export function sincronizarPet(t: Tamer, m: Motor): boolean {
  if (m.versao < 6 || m.morte || m.medalhas >= t.n) return false;
  try { m.liberar(t.n); } catch (err) { if (err instanceof PetMorto) return false; throw err; }
  return true;
}

/* ------------------------------------------------ primeira abertura com medalhas: os pets antigos saem */
/** decisao do Matheus (2026-09-29): os pets de antes da trava (v1-v5) sao descartados, o ativo e os guardados, e o jogo
    comeca num ovo novo v6 com o Tamer sem medalhas. Roda uma vez: a chave do Tamer marca que ja rodou. Save que nao e
    JSON fica como esta (o app mostra o erro e nao grava por cima, como sempre). Devolve quantos pets saíram, ou null se
    ja tinha rodado. As geracoes aposentadas (Diario · Geracoes, so para ver) ficam. */
export function migrarParaMedalhas(armaz: Armazenamento & { removeItem(k: string): void }, chaveGuardados: string): number | null {
  if (armaz.getItem(CHAVE_TAMER) !== null) return null;
  const antigo = (txt: string | null): boolean => {
    if (txt === null) return false;
    try { const d = JSON.parse(txt) as { versao?: number } | null; return !!d && (d.versao ?? 1) < 6; } catch { return false; }
  };
  let descartados = 0;
  const ativo = armaz.getItem(CHAVE);
  if (antigo(ativo)) { armaz.removeItem(CHAVE); descartados++; }
  const bg = armaz.getItem(chaveGuardados);
  if (bg !== null) {
    let g: unknown = null;
    try { g = JSON.parse(bg); } catch { /* guardados ilegiveis: ficam para o erro de sempre */ }
    if (Array.isArray(g)) {
      const ficam = g.filter(x => !antigo(JSON.stringify(x)));
      descartados += g.length - ficam.length;
      if (ficam.length !== g.length) armaz.setItem(chaveGuardados, JSON.stringify(ficam));
    }
  }
  /* sem a chave dos guardados, a escada de exemplo (pets v3) seria semeada logo depois: fica vazia de proposito */
  if (descartados && armaz.getItem(chaveGuardados) === null) armaz.setItem(chaveGuardados, "[]");
  gravarTamer(armaz, new Tamer());
  if (descartados) armaz.setItem(CHAVE_AVISO_V6, String(descartados));
  return descartados;
}

/* ------------------------------------------------ textos da tela (Evolucao, Campanha, Medalhas) */
/** as medalhas que ainda faltam ao Tamer para chegar a `precisa`, na ordem da tabela */
export function medalhasQueFaltam(t: Tamer, precisa: number): Medalha[] {
  return MEDALHAS.filter(x => !t.tem(x.id)).slice(0, Math.max(0, precisa - t.n));
}
/** onde a medalha se ganha hoje (todos os lugares da campanha sao femininos: "na Campina") */
export const comoGanhar = (md: Medalha): string => `vença o ${NPC[md.lider]!.nome} na ${LUGARES_V5[md.lugar].nome}`;
/** "Falta a Medalha da Campina: vença o Gazimon na Campina." (ou a lista, quando falta mais de uma) */
export function textoFalta(t: Tamer, precisa: number): string {
  const f = medalhasQueFaltam(t, precisa);
  if (!f.length) return "";
  if (f.length === 1) return `Falta a ${f[0].nome}: ${comoGanhar(f[0])}.`;
  return `Faltam ${f.length} medalhas: ` + f.map(x => `${x.nome} (${comoGanhar(x)})`).join(", ").replace(/, ([^,]*)$/, " e $1") + ".";
}
