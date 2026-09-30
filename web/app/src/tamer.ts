/* Tamer: o jogador (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 4 e 5; so no jogo). As medalhas sao dele, nao do pet, e
   sobrevivem ao pet. Registro proprio, com event sourcing como o do pet: a chave CHAVE-tamer guarda so os eventos
   {versao, log}; o estado (quais medalhas, com que pet) e reconstruido reprocessando o registro. Evento desconhecido
   falha alto. O formato do save do pet nao muda.

   O motor do pet NUNCA le o Tamer por fora (o replay do pet tem de dar o mesmo resultado sozinho): quando o Tamer tem
   mais medalhas do que o pet ativo conhece, o app grava no registro do pet o evento "u" (Motor.liberar), e o motor
   re-verifica a evolucao nessa hora. Um pet guardado recebe o "u" quando volta a ser o ativo. */
import { ARENA_POR_ID, LUGARES_V6, MEDALHAS, MEDALHA_POR_ID, Motor, NPC, PetMorto, nomeForma, type Medalha } from "../motor/index.ts";
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

/* ------------------------------------------------ descarte unico dos pets antigos */
/** marcador do descarte unico: a versao do descarte que ja rodou neste navegador. 1 = medalhas do Tamer (2026-09-29: os
    pets v1-v5 saem); 2 = combate V21D nos pets v6 (2026-09-30, docs/VALIDACAO_V21D.md: os v6 de antes mudariam de
    comportamento no replay e saem tambem); 3 = arenas com lideres (2026-09-30, DESIGN_MEDALHAS_ARENAS parte 2: as lutas
    de arena mudam no replay dos v6 de antes, e saem de novo). Sem a chave: 1 se o registro do Tamer existe (o descarte das medalhas rodou
    antes do marcador existir), senao 0 */
export const CHAVE_DESCARTE = CHAVE + "-descarte";
export const VERSAO_DESCARTE = 3;
/** cada descarte apaga os pets ate esta versao (inclusive) */
const DESCARTA_ATE: Record<number, number> = { 1: 5, 2: 6, 3: 6 };

/** decisoes do Matheus: os pets de antes da trava das medalhas (v1-v5, 2026-09-29) e os v6 de antes do combate V21D
    (2026-09-30) sao descartados, o ativo e os guardados, e o jogo comeca num ovo novo v6 com o Tamer sem medalhas. Roda uma
    vez por versao do descarte (CHAVE_DESCARTE). Save que nao e JSON fica como esta (o app mostra o erro e nao grava por
    cima, como sempre). Devolve quantos pets sairam, ou null se ja tinha rodado. As geracoes aposentadas (Diario ·
    Geracoes, so para ver) ficam. Sem pet nenhum para descartar, o Tamer que ja existe fica como esta (sem aviso). */
export function descartarPetsAntigos(armaz: Armazenamento & { removeItem(k: string): void }, chaveGuardados: string): number | null {
  const marca = armaz.getItem(CHAVE_DESCARTE), tinhaTamer = armaz.getItem(CHAVE_TAMER) !== null;
  const feito = marca !== null ? Number(marca) : tinhaTamer ? 1 : 0;
  if (!Number.isInteger(feito) || feito < 0 || feito > VERSAO_DESCARTE) throw new Error(`marcador do descarte inválido: ${JSON.stringify(marca)}`);
  if (feito >= VERSAO_DESCARTE) return null;
  const ate = DESCARTA_ATE[VERSAO_DESCARTE];
  const antigo = (txt: string | null): boolean => {
    if (txt === null) return false;
    try { const d = JSON.parse(txt) as { versao?: number } | null; return !!d && (d.versao ?? 1) <= ate; } catch { return false; }
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
  /* o aviso de sempre diz "um ovo novo e nenhuma medalha": com pet descartado o Tamer recomeca vazio */
  if (descartados || !tinhaTamer) gravarTamer(armaz, new Tamer());
  armaz.setItem(CHAVE_DESCARTE, String(VERSAO_DESCARTE));
  if (descartados) armaz.setItem(CHAVE_AVISO_V6, String(descartados));
  return descartados;
}

/* ------------------------------------------------ textos da tela (Evolucao, Campanha, Medalhas) */
/** as medalhas que ainda faltam ao Tamer para chegar a `precisa`, na ordem da tabela */
export function medalhasQueFaltam(t: Tamer, precisa: number): Medalha[] {
  return MEDALHAS.filter(x => !t.tem(x.id)).slice(0, Math.max(0, precisa - t.n));
}
/** "na Campina", "no Lago": o lugar da campanha v6 com a preposicao (so o Lago e masculino) */
export const noLugar = (nome: string): string => `${nome === "Lago" ? "no" : "na"} ${nome}`;
/** onde a medalha se ganha: o lider da arena dela (na Cidadela, tres vezes seguidas) */
export const comoGanhar = (md: Medalha): string => {
  const n = ARENA_POR_ID[md.id]?.lutas ?? 1;
  return `vença o ${NPC[md.lider]!.nome}${n > 1 ? ` ${n === 3 ? "três" : n} vezes seguidas` : ""} ${noLugar(LUGARES_V6[md.lugar].nome)}`;
};
/** "Falta a Medalha da Campina: vença o Gazimon na Campina." (ou a lista, quando falta mais de uma) */
export function textoFalta(t: Tamer, precisa: number): string {
  const f = medalhasQueFaltam(t, precisa);
  if (!f.length) return "";
  if (f.length === 1) return `Falta a ${f[0].nome}: ${comoGanhar(f[0])}.`;
  return `Faltam ${f.length} medalhas: ` + f.map(x => `${x.nome} (${comoGanhar(x)})`).join(", ").replace(/, ([^,]*)$/, " e $1") + ".";
}
