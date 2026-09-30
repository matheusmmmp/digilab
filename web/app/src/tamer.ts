/* Tamer: o jogador (docs/DESIGN_MEDALHAS_ARENAS.md, secoes 4 e 5; so no jogo). As medalhas sao dele, nao do pet, e
   sobrevivem ao pet. Registro proprio, com event sourcing como o do pet: a chave CHAVE-tamer guarda so os eventos
   {versao, log}; o estado (quais medalhas, com que pet) e reconstruido reprocessando o registro. Evento desconhecido
   falha alto. O formato do save do pet nao muda.

   O motor do pet NUNCA le o Tamer por fora (o replay do pet tem de dar o mesmo resultado sozinho): quando o Tamer tem
   mais medalhas do que o pet ativo conhece, o app grava no registro do pet o evento "u" (Motor.liberar), e o motor
   re-verifica a evolucao nessa hora. Um pet guardado recebe o "u" quando volta a ser o ativo.

   Itens (medalhas, parte 3; docs/DESIGN_MEDALHAS_ARENAS.md, secao 13): o inventario tambem e do Tamer. Registro versao 2 (a versao 1,
   so com medalhas, continua abrindo): eventos "item" (o item da medalha, na primeira vitoria contra o lider, e a carta da revanche) e
   "carta_usada". O chip nao se gasta (qualquer pet do Tamer pode ter uma copia equipada); a carta sai do inventario quando vale numa
   luta. No registro do pet entram "i" (equipar, desequipar) e "k" (a carta da proxima luta): o motor do pet continua sem ler o Tamer. */
import {
  ARENA_POR_ID, CARTA_DA_REVANCHE, CIT, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHAS, MEDALHA_POR_ID, Motor, NPC, PetMorto, cartaDe, itemDe, medalhaDoLider,
  nomeForma, type Estagio, type Medalha,
} from "../motor/index.ts";
import { CHAVE, type Armazenamento } from "./save.ts";

export const CHAVE_TAMER = CHAVE + "-tamer";
/** aviso pendente de que os pets antigos foram descartados (sai quando o jogador le) */
export const CHAVE_AVISO_V6 = CHAVE + "-aviso-v6";
/** versao do registro do Tamer: 1 = medalhas (parte 1); 2 = medalhas e itens (parte 3). Grava a 2; le as duas */
export const VERSAO_TAMER = 2;
const VERSOES_TAMER = [1, 2];

/** uma medalha ganha: qual, o contador (1 = a primeira), a hora de parede, o pet que venceu (semente, forma e tick dele) */
export interface MedalhaGanha { id: string; n: number; quando: number; pet: number; forma: string; tick: number }
/** um item ganho: qual, o contador dos itens (1 = o primeiro), a hora de parede, de onde veio (o item da medalha do lider, ou a carta
    da revanche contra ele) e o pet (semente, forma, estagio e tick dele; a espera da revanche conta no relogio do pet) */
export interface ItemGanho { id: string; n: number; quando: number; origem: "medalha" | "revanche"; lider: string; pet: number; forma: string; est: Estagio; tick: number }
/** uma carta que valeu numa luta (sai do inventario) */
export interface CartaUsada { id: string; quando: number; pet: number; tick: number }
export type EventoTamer = ["medalha", MedalhaGanha] | ["item", ItemGanho] | ["carta_usada", CartaUsada];
const ESTAGIOS: readonly string[] = ["bebe", "crianca", "adolescente", "adulto", "mega"];

export class Tamer {
  log: EventoTamer[] = [];
  /** estado reconstruido: as medalhas na ordem em que foram ganhas */
  medalhas: MedalhaGanha[] = [];
  /** os itens ganhos, na ordem, e as cartas usadas */
  itens: ItemGanho[] = [];
  usadas: CartaUsada[] = [];
  get n(): number { return this.medalhas.length; }
  tem(id: string): boolean { return this.medalhas.some(x => x.id === id); }
  ganha(id: string): MedalhaGanha | null { return this.medalhas.find(x => x.id === id) ?? null; }
  /** o Tamer tem o chip (chip nao se gasta) */
  temChip(id: string): boolean { return this.itens.some(x => x.id === id) && itemDe(id).tipo !== "carta"; }
  /** quantas cartas desse tipo o Tamer tem agora (ganhas menos usadas) */
  cartas(id: string): number { return this.itens.filter(x => x.id === id).length - this.usadas.filter(x => x.id === id).length; }
  /** o item que a medalha do lider ja deu (null: ainda nao) */
  itemDaMedalha(lider: string): ItemGanho | null { return this.itens.find(x => x.origem === "medalha" && x.lider === lider) ?? null; }
  /** a ultima carta de revanche que o pet ganhou do lider (a espera conta dela) */
  ultimaRevanche(lider: string, pet: number): ItemGanho | null {
    return [...this.itens].reverse().find(x => x.origem === "revanche" && x.lider === lider && x.pet === pet) ?? null;
  }

  /** um evento do registro (replay): confere tudo antes de aplicar */
  aplicar(ev: EventoTamer): void {
    if (!Array.isArray(ev) || !["medalha", "item", "carta_usada"].includes(ev[0]))
      throw new Error("tipo de evento desconhecido no registro do Tamer: " + JSON.stringify(Array.isArray(ev) ? ev[0] : ev));
    if (ev[0] === "item") { this._item(ev[1]); return; }
    if (ev[0] === "carta_usada") { this._usada(ev[1]); return; }
    const x = ev[1];
    if (!x || !MEDALHA_POR_ID[x.id]) throw new Error("medalha desconhecida no registro do Tamer: " + JSON.stringify(x?.id));
    if (this.tem(x.id)) throw new Error(`medalha repetida no registro do Tamer: ${x.id}`);
    if (x.n !== this.n + 1) throw new Error(`contador fora de ordem no registro do Tamer: ${x.n} (esperado ${this.n + 1})`);
    for (const k of ["quando", "pet", "tick"] as const) if (!Number.isFinite(x[k])) throw new Error(`medalha ${x.id} sem ${k} no registro do Tamer`);
    if (typeof x.forma !== "string") throw new Error(`medalha ${x.id} sem a forma do pet no registro do Tamer`);
    this.medalhas.push({ ...x });
  }
  private _item(x: ItemGanho): void {
    if (!x || typeof x.id !== "string") throw new Error("item sem id no registro do Tamer");
    const it = itemDe(x.id), md = medalhaDoLider(x.lider);
    if (x.n !== this.itens.length + 1) throw new Error(`contador de itens fora de ordem no registro do Tamer: ${x.n} (esperado ${this.itens.length + 1})`);
    for (const k of ["quando", "pet", "tick"] as const) if (!Number.isFinite(x[k])) throw new Error(`item ${x.id} sem ${k} no registro do Tamer`);
    if (typeof x.forma !== "string" || !ESTAGIOS.includes(x.est)) throw new Error(`item ${x.id} sem a forma e o estágio do pet no registro do Tamer`);
    if (!md) throw new Error(`item ${x.id} de quem não é líder: ${JSON.stringify(x.lider)}`);
    if (!this.tem(md.id)) throw new Error(`item ${x.id} antes da ${md.nome} no registro do Tamer`);
    if (x.origem === "medalha") {
      if (ITEM_DA_MEDALHA[md.id] !== x.id) throw new Error(`a ${md.nome} dá ${itemDe(ITEM_DA_MEDALHA[md.id]).nome}, não ${it.nome}`);
      if (this.itemDaMedalha(x.lider)) throw new Error(`item da ${md.nome} repetido no registro do Tamer`);
    } else if (x.origem === "revanche") {
      if (CARTA_DA_REVANCHE[md.id] !== x.id) throw new Error(`a revanche contra o ${NPC[x.lider]!.nome} dá ${itemDe(CARTA_DA_REVANCHE[md.id]).nome}, não ${it.nome}`);
      const est = LUGARES_V6[md.lugar].est;
      if (x.est !== est) throw new Error(`carta de revanche com um pet fora do nível da arena (${x.est}, a arena pede ${est})`);
      const ult = this.ultimaRevanche(x.lider, x.pet);
      if (ult && x.tick - ult.tick < CIT.espera) throw new Error(`carta de revanche antes da espera: ${x.tick - ult.tick} min de ${CIT.espera}`);
    } else throw new Error(`origem de item desconhecida no registro do Tamer: ${JSON.stringify(x.origem)}`);
    this.itens.push({ ...x });
  }
  private _usada(x: CartaUsada): void {
    if (!x || typeof x.id !== "string") throw new Error("carta usada sem id no registro do Tamer");
    const c = cartaDe(x.id);
    for (const k of ["quando", "pet", "tick"] as const) if (!Number.isFinite(x[k])) throw new Error(`carta usada ${x.id} sem ${k} no registro do Tamer`);
    if (this.cartas(x.id) < 1) throw new Error(`${c.nome} usada sem estar no inventário do Tamer`);
    this.usadas.push({ ...x });
  }
  private _gravar(ev: EventoTamer): void { this.aplicar(ev); this.log.push(ev); }
  /** o item da medalha do lider, agora, com o pet m */
  ganharItem(id: string, origem: ItemGanho["origem"], lider: string, m: Motor, quando: number = Date.now()): ItemGanho {
    this._gravar(["item", { id, n: this.itens.length + 1, quando, origem, lider, pet: m.semente, forma: nomeForma(m.forma), est: m.estagioAtual, tick: m.e.tick }]);
    return this.itens[this.itens.length - 1];
  }
  /** a carta valeu numa luta do pet m (o app grava logo depois da luta que a usou) */
  usarCarta(id: string, m: Motor, quando: number = Date.now()): void {
    this._gravar(["carta_usada", { id, quando, pet: m.semente, tick: m.e.tick }]);
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
  if (!VERSOES_TAMER.includes(s.versao as number) || !Array.isArray(s.log)) throw new Error("o registro do Tamer não tem versão " + VERSOES_TAMER.join(" ou ") + " e eventos");
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
/** itens das medalhas: o Tamer que tem a medalha e ainda nao tem o item dela ganha agora (na mesma hora da medalha; um Tamer de antes
    desta parte recebe na abertura). So com pet v6. Devolve os itens novos (ja aplicados) */
export function conferirItensDasMedalhas(t: Tamer, m: Motor, quando: number = Date.now()): ItemGanho[] {
  if (m.versao < 6) return [];
  const novos: ItemGanho[] = [];
  for (const g of t.medalhas) {
    const md = MEDALHA_POR_ID[g.id];
    if (!t.itemDaMedalha(md.lider)) novos.push(t.ganharItem(ITEM_DA_MEDALHA[md.id], "medalha", md.lider, m, quando));
  }
  return novos;
}
/** por que a vitoria contra o lider nao da carta de revanche (null: da). `medalhaAntes`: o Tamer ja tinha a medalha dele antes
    desta luta (a primeira vitoria da a medalha e o item, nao carta) */
export function porqueSemCarta(t: Tamer, m: Motor, lider: string, medalhaAntes: boolean): string | null {
  const md = medalhaDoLider(lider);
  if (m.versao < 6 || !md) return "só o líder de uma arena dá carta, e só a pets v6";
  if (!medalhaAntes) return "a primeira vitória dá a medalha e o item, não carta";
  const est = LUGARES_V6[md.lugar].est;
  if (m.estagioAtual !== est) return `a carta da revanche vem com um pet do nível da arena (${NIVEL_TAMER[est] ?? est})`;
  const ult = t.ultimaRevanche(lider, m.semente);
  if (ult && m.e.tick - ult.tick < CIT.espera) {
    const falta = CIT.espera - (m.e.tick - ult.tick);
    return `este pet já ganhou a carta deste líder há pouco: a próxima em ${Math.floor(falta / 60)} h ${falta % 60} min de jogo`;
  }
  return null;
}
const NIVEL_TAMER: Partial<Record<Estagio, string>> = { crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };
/** a revanche vencida da a carta do lider (se pode): grava e devolve o item, ou null */
export function conferirRevanche(t: Tamer, m: Motor, lider: string, venceu: boolean, medalhaAntes: boolean, quando: number = Date.now()): ItemGanho | null {
  if (!venceu || porqueSemCarta(t, m, lider, medalhaAntes)) return null;
  const md = medalhaDoLider(lider)!;
  return t.ganharItem(CARTA_DA_REVANCHE[md.id], "revanche", lider, m, quando);
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
    de arena mudam no replay dos v6 de antes, e saem de novo); 4 = escala dos pets v6 (2026-09-30, CESC_V6: as lutas da
    campanha e das arenas mudam no replay dos v6 de antes, e eles saem de novo); 5 = limite de turnos do desafiado (2026-09-30: as
    lutas dos v6 que chegam ao limite mudam de resultado no replay, e eles saem de novo). Sem a chave: 1 se o registro do Tamer existe (o
    descarte das medalhas rodou antes do marcador existir), senao 0 */
export const CHAVE_DESCARTE = CHAVE + "-descarte";
export const VERSAO_DESCARTE = 5;
/** cada descarte apaga os pets ate esta versao (inclusive) */
const DESCARTA_ATE: Record<number, number> = { 1: 5, 2: 6, 3: 6, 4: 6, 5: 6 };

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
