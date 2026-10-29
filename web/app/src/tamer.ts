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
   luta. No registro do pet entram "i" (equipar, desequipar) e "k" (a carta da proxima luta): o motor do pet continua sem ler o Tamer.

   O titulo (a Liga dos Lideres na Fronteira, medalhas parte 4a; docs/DESIGN_FRONTEIRA.md, secao 2): registro versao 3 (le a 1 e a 2).
   Evento "campeao": o pet venceu as 6 lutas da Liga (o motor do pet conta os titulos dele, Motor.liga, a partir do evento de luta "l"
   da Liga). Um por pet (o primeiro titulo dele), so depois das 6 medalhas; o primeiro do registro e o titulo do Tamer (a medalha de
   ouro).

   Os recordes (as instalacoes da Fronteira, medalhas parte 4b; docs/DESIGN_FRONTEIRA.md, secao 3): registro versao 4 (le a 1, a 2 e a 3).
   Evento "recorde": a maior sequencia de vitorias numa instalacao (Torre de Batalha, Palacio), com o pet que fez. So entra quando passa o
   recorde que o Tamer ja tem, e so depois do titulo. O motor do pet conta as sequencias dele (Motor.instalacoes, a partir do evento de luta
   "l" da instalacao); o pet conhece o titulo do Tamer pelo evento "f" do registro dele (Motor.abrirFronteira), gravado aqui, como o "u".

   A Fabrica e o Salao (medalhas parte 4c; docs/DESIGN_FRONTEIRA.md, secoes 3 e 4): registro versao 5 (le 1 a 4).
   - Fabrica (motor/fabrica.ts): nenhum pet do jogador luta, entao a tentativa inteira fica SO aqui e se refaz sozinha a partir daqui:
     "fabrica" (o comeco da tentativa n, com a semente dela, que sai do numero da tentativa, e o alugado escolhido entre os 3), "fabrica_luta"
     (a luta k, com a semente dela; o replay joga a luta de novo) e "fabrica_troca" (depois da vitoria k, o alugado vira o rival derrotado).
     O recorde (a maior sequencia de series vencidas) sai das tentativas, sem evento proprio.
   - Salao (motor/salao.ts): cada pet luta no registro DELE (evento "l" {r: "salao", s}); aqui fica a tentativa, "salao": os pets (um por
     estagio, na ordem), a tentativa de cada um no Salao, a semente (que sai do registro dele; o replay confere a conta) e quem venceu. O
     recorde (quantos estagios venceu seguidos, ate 4) sai das tentativas.

   A Fabrica dos v9 (rodada de equilibrio geral, fase 3; motor/fabrica.ts): registro versao 6 (le 1 a 5). O evento "fabrica" ganha o campo
   `v`, a versao das regras da tentativa (VERSOES_FABRICA): sem ele, a Fabrica de antes (V21D, fator 1, a troca nao cura), e as tentativas
   ja gravadas se refazem iguais; as tentativas novas gravam `v: 9` (VERSAO_FABRICA_ATUAL: V21E, o fator dos rivais dos v9, a troca com a
   vida cheia). Versao desconhecida falha alto.

   A Fabrica em tempo real (COMBATE-TR, etapa R2; D-4, decisao do Matheus de 2026-10-29): registro versao 7. As tentativas novas gravam
   `v: 13` (VERSAO_FABRICA_TR: a luta em tempo real dos pets v13), e o registro 7 so aceita essas. As tentativas antigas (v ausente ou 9)
   saem do registro no descarte unico 6 (descartarPetsAntigos), com aviso na tela; o recorde da Fabrica recomeca. O resto do Tamer (as
   medalhas, os itens, o titulo, os recordes das instalacoes, o Salao) fica. Os registros 1 a 6 ainda se leem (com a Fabrica de antes). */
import {
  ARENA_POR_ID, CARTA_DA_REVANCHE, CIT, ESTAGIOS_SALAO, INSTALACOES, LUTAS_SERIE_FABRICA, TentativaFabrica, VERSAO_FABRICA, VERSAO_FABRICA_ATUAL, VERSAO_FABRICA_TR, VERSOES_FABRICA, sementeFabrica, sementeSalao, ITEM_DA_MEDALHA, LUGARES_V6, MEDALHAS, MEDALHAS_LIGA, MEDALHA_POR_ID, Motor, NPC, PetMorto, VERSAO_INSTALACOES,
  VERSAO_LIGA, cartaDe, ehInstalacao, itemDe, medalhaDoLider, nomeForma, type Estagio, type IdInstalacao, type Medalha,
} from "../motor/index.ts";
import { CHAVE, type Armazenamento } from "./save.ts";

export const CHAVE_TAMER = CHAVE + "-tamer";
/** aviso pendente de que os pets antigos foram descartados (sai quando o jogador le) */
export const CHAVE_AVISO_V6 = CHAVE + "-aviso-v6";
/** aviso pendente do descarte 6 (a luta em tempo real, pets v13): JSON {pets, fabrica}, quantos pets e quantas tentativas da Fabrica sairam
    (sai quando o jogador le) */
export const CHAVE_AVISO_TR = CHAVE + "-aviso-tr";
/** os saves dos pets que o descarte 6 tirou, como estavam ({semente, log, versao}[]): o aviso oferece baixar o arquivo deles. Fica ate o
    jogador baixar ou dispensar */
export const CHAVE_DESCARTADOS = CHAVE + "-descartados";
/** versao do registro do Tamer: 1 = medalhas (parte 1); 2 = medalhas e itens (parte 3); 3 = e o titulo da Liga (parte 4a); 4 = e os
    recordes das instalacoes da Fronteira (parte 4b); 5 = e a Fabrica e o Salao (parte 4c); 6 = e a versao das regras de cada tentativa da
    Fabrica (campo `v`, equilibrio geral fase 3); 7 = so a Fabrica em tempo real (v: 13; COMBATE-TR, D-4). Grava a 7; le as sete */
export const VERSAO_TAMER = 7;
const VERSOES_TAMER = [1, 2, 3, 4, 5, 6, 7];
/** os eventos da Fabrica no registro do Tamer */
const EVENTOS_FABRICA = ["fabrica", "fabrica_luta", "fabrica_troca"];

/** uma medalha ganha: qual, o contador (1 = a primeira), a hora de parede, o pet que venceu (semente, forma e tick dele) */
export interface MedalhaGanha { id: string; n: number; quando: number; pet: number; forma: string; tick: number }
/** um item ganho: qual, o contador dos itens (1 = o primeiro), a hora de parede, de onde veio (o item da medalha do lider, ou a carta
    da revanche contra ele) e o pet (semente, forma, estagio e tick dele; a espera da revanche conta no relogio do pet) */
export interface ItemGanho { id: string; n: number; quando: number; origem: "medalha" | "revanche"; lider: string; pet: number; forma: string; est: Estagio; tick: number }
/** uma carta que valeu numa luta (sai do inventario) */
export interface CartaUsada { id: string; quando: number; pet: number; tick: number }
/** um titulo da Liga dos Lideres: o contador (1 = o primeiro, o titulo do Tamer), a hora de parede e o pet que venceu as 6 (semente,
    forma e tick dele) */
export interface Campeao { n: number; quando: number; pet: number; forma: string; tick: number }
/** um recorde numa instalacao da Fronteira: qual, o valor (a sequencia de vitorias), a hora de parede e o pet que fez (semente, forma e
    tick dele) */
export interface Recorde { inst: IdInstalacao; valor: number; quando: number; pet: number; forma: string; tick: number }
/** Fabrica: o comeco da tentativa n (1 = a primeira), a semente dela (sementeFabrica(n)), o alugado escolhido (0 a 2) e a versao das regras
    (registro versao 6; sem ela, a Fabrica de antes, VERSAO_FABRICA) */
export interface InicioFabrica { n: number; s: number; alugado: number; quando: number; v?: number }
/** Fabrica: a luta k (0 = a primeira) da tentativa n, com a semente dela (sementeLutaFabrica) */
export interface EventoLutaFabrica { n: number; k: number; s: number; quando: number }
/** Fabrica: depois da vitoria k da tentativa n, o alugado vira o rival derrotado */
export interface TrocaFabrica { n: number; k: number; quando: number }
/** Salao: a luta de um pet (o estagio, a semente e a forma dele, a tentativa dele no Salao, a semente da luta, o tick dele e se venceu) */
export interface LutaSalao { est: Estagio; pet: number; forma: string; k: number; s: number; tick: number; venceu: boolean }
/** Salao: uma tentativa (n = 1 a primeira), as lutas na ordem dos estagios, ate a primeira que nao foi vitoria */
export interface TentativaSalao { n: number; quando: number; lutas: LutaSalao[] }
export type EventoTamer = ["medalha", MedalhaGanha] | ["item", ItemGanho] | ["carta_usada", CartaUsada] | ["campeao", Campeao] | ["recorde", Recorde]
  | ["fabrica", InicioFabrica] | ["fabrica_luta", EventoLutaFabrica] | ["fabrica_troca", TrocaFabrica] | ["salao", TentativaSalao];
/** um recorde da Fabrica ou do Salao, tirado das tentativas: o valor, a tentativa que o fez (a primeira que chegou nele) e a hora de parede */
export interface RecordeTentativa { valor: number; n: number; quando: number }
const ESTAGIOS: readonly string[] = ["bebe", "crianca", "adolescente", "adulto", "mega"];

export class Tamer {
  log: EventoTamer[] = [];
  /** estado reconstruido: as medalhas na ordem em que foram ganhas */
  medalhas: MedalhaGanha[] = [];
  /** os itens ganhos, na ordem, e as cartas usadas */
  itens: ItemGanho[] = [];
  usadas: CartaUsada[] = [];
  /** os titulos da Liga, na ordem (um por pet) */
  campeoes: Campeao[] = [];
  /** os recordes das instalacoes, na ordem em que foram batidos (o ultimo de cada instalacao e o recorde dela) */
  recordes: Recorde[] = [];
  /** as tentativas da Fabrica, refeitas do registro (a ultima pode estar em andamento), e a hora de parede de cada luta delas */
  fabrica: TentativaFabrica[] = [];
  private quandoFabrica: number[][] = [];
  /** as tentativas do Salao */
  salao: TentativaSalao[] = [];
  /** a tentativa da Fabrica em andamento (null: nenhuma; a ultima acabou) */
  get fabricaAtual(): TentativaFabrica | null { const t = this.fabrica[this.fabrica.length - 1]; return t && !t.acabou ? t : null; }
  /** o recorde da Fabrica: a maior sequencia de series vencidas numa tentativa (null: nenhuma serie vencida ainda) */
  get recordeFabrica(): RecordeTentativa | null {
    let r: RecordeTentativa | null = null;
    this.fabrica.forEach((t, i) => {
      if (t.series < 1 || (r && t.series <= r.valor)) return;
      /* a hora da vitoria que fechou a ultima serie contada */
      r = { valor: t.series, n: t.n, quando: this.quandoFabrica[i][t.series * LUTAS_SERIE_FABRICA - 1] };
    });
    return r;
  }
  /** o recorde do Salao: quantos estagios seguidos uma tentativa venceu (null: nenhum ainda) */
  get recordeSalao(): RecordeTentativa | null {
    let r: RecordeTentativa | null = null;
    for (const t of this.salao) {
      const v = t.lutas.filter(x => x.venceu).length;
      if (v >= 1 && (!r || v > r.valor)) r = { valor: v, n: t.n, quando: t.quando };
    }
    return r;
  }
  get n(): number { return this.medalhas.length; }
  /** o titulo do Tamer: o primeiro campeao (null: ainda nao venceu a Liga) */
  get titulo(): Campeao | null { return this.campeoes[0] ?? null; }
  /** o titulo que o pet (semente) deu ao Tamer (null: nenhum) */
  tituloDe(pet: number): Campeao | null { return this.campeoes.find(x => x.pet === pet) ?? null; }
  /** o recorde do Tamer na instalacao (null: nenhuma vitoria la ainda) */
  recorde(inst: IdInstalacao): Recorde | null { return [...this.recordes].reverse().find(x => x.inst === inst) ?? null; }
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
    if (!Array.isArray(ev) || !["medalha", "item", "carta_usada", "campeao", "recorde", "fabrica", "fabrica_luta", "fabrica_troca", "salao"].includes(ev[0]))
      throw new Error("tipo de evento desconhecido no registro do Tamer: " + JSON.stringify(Array.isArray(ev) ? ev[0] : ev));
    if (ev[0] === "item") { this._item(ev[1]); return; }
    if (ev[0] === "fabrica") { this._fabrica(ev[1]); return; }
    if (ev[0] === "fabrica_luta") { this._fabricaLuta(ev[1]); return; }
    if (ev[0] === "fabrica_troca") { this._fabricaTroca(ev[1]); return; }
    if (ev[0] === "salao") { this._salao(ev[1]); return; }
    if (ev[0] === "campeao") { this._campeao(ev[1]); return; }
    if (ev[0] === "recorde") { this._recorde(ev[1]); return; }
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
  private _campeao(x: Campeao): void {
    if (!x || typeof x !== "object") throw new Error("título sem dados no registro do Tamer");
    if (this.n < MEDALHAS_LIGA) throw new Error(`título da Liga antes das ${MEDALHAS_LIGA} medalhas no registro do Tamer (tem ${this.n})`);
    if (x.n !== this.campeoes.length + 1) throw new Error(`contador de títulos fora de ordem no registro do Tamer: ${x.n} (esperado ${this.campeoes.length + 1})`);
    for (const k of ["quando", "pet", "tick"] as const) if (!Number.isFinite(x[k])) throw new Error(`título sem ${k} no registro do Tamer`);
    if (typeof x.forma !== "string") throw new Error("título sem a forma do pet no registro do Tamer");
    if (this.tituloDe(x.pet)) throw new Error(`título repetido para o mesmo pet no registro do Tamer (${x.pet})`);
    this.campeoes.push({ ...x });
  }
  private _recorde(x: Recorde): void {
    if (!x || typeof x !== "object") throw new Error("recorde sem dados no registro do Tamer");
    if (typeof x.inst !== "string" || !ehInstalacao(x.inst)) throw new Error("recorde de instalação desconhecida no registro do Tamer: " + JSON.stringify(x.inst));
    if (!this.titulo) throw new Error("recorde da Fronteira antes do título da Liga no registro do Tamer");
    if (!Number.isInteger(x.valor) || x.valor < 1) throw new Error(`recorde inválido no registro do Tamer: ${JSON.stringify(x.valor)}`);
    const antes = this.recorde(x.inst);
    if (antes && x.valor <= antes.valor) throw new Error(`recorde que não passa o anterior no registro do Tamer (${x.inst}: ${x.valor}, o recorde era ${antes.valor})`);
    for (const k of ["quando", "pet", "tick"] as const) if (!Number.isFinite(x[k])) throw new Error(`recorde sem ${k} no registro do Tamer`);
    if (typeof x.forma !== "string") throw new Error("recorde sem a forma do pet no registro do Tamer");
    this.recordes.push({ ...x });
  }
  /* ------------------------------------------------ a Fabrica (motor/fabrica.ts) */
  private _campos(x: object | null | undefined, o: string, campos: readonly string[]): void {
    if (!x || typeof x !== "object") throw new Error(`${o} sem dados no registro do Tamer`);
    for (const k of campos) if (!Number.isFinite((x as Record<string, unknown>)[k])) throw new Error(`${o} sem ${k} no registro do Tamer`);
  }
  private _fabrica(x: InicioFabrica): void {
    this._campos(x, "tentativa da Fábrica", ["n", "s", "alugado", "quando"]);
    if (!this.titulo) throw new Error("tentativa da Fábrica antes do título da Liga no registro do Tamer");
    if (x.n !== this.fabrica.length + 1) throw new Error(`tentativa da Fábrica fora de ordem no registro do Tamer: ${x.n} (esperada ${this.fabrica.length + 1})`);
    const atual = this.fabricaAtual;
    if (atual) throw new Error(`tentativa ${x.n} da Fábrica com a ${atual.n} ainda em andamento no registro do Tamer`);
    if (x.s !== sementeFabrica(x.n)) throw new Error(`a tentativa ${x.n} da Fábrica tem a semente ${sementeFabrica(x.n)}, não ${x.s}, no registro do Tamer`);
    if (x.v !== undefined && !VERSOES_FABRICA.includes(x.v)) throw new Error(`a tentativa ${x.n} da Fábrica com as regras da versão ${JSON.stringify(x.v)}, desconhecida, no registro do Tamer`);
    this.fabrica.push(new TentativaFabrica(x.n, x.alugado, x.v ?? VERSAO_FABRICA));
    this.quandoFabrica.push([]);
  }
  private _fabricaEmAndamento(n: number, o: string): TentativaFabrica {
    const t = this.fabricaAtual;
    if (!t || t.n !== n) throw new Error(`${o} da tentativa ${n} da Fábrica, que não está em andamento no registro do Tamer`);
    return t;
  }
  private _fabricaLuta(x: EventoLutaFabrica): void {
    this._campos(x, "luta da Fábrica", ["n", "k", "s", "quando"]);
    const t = this._fabricaEmAndamento(x.n, "luta");
    if (x.k !== t.lutas.length) throw new Error(`luta ${x.k} da tentativa ${x.n} da Fábrica fora de ordem no registro do Tamer (esperada ${t.lutas.length})`);
    t.lutar(x.s);
    this.quandoFabrica[this.fabrica.length - 1].push(x.quando);
  }
  private _fabricaTroca(x: TrocaFabrica): void {
    this._campos(x, "troca da Fábrica", ["n", "k", "quando"]);
    const t = this._fabricaEmAndamento(x.n, "troca");
    if (x.k !== t.lutas.length - 1) throw new Error(`troca da Fábrica depois da luta ${x.k}, mas a última luta da tentativa ${x.n} é a ${t.lutas.length - 1}`);
    t.trocar();
  }
  /** a tentativa nova da Fabrica, com o alugado escolhido (0 a 2) entre os 3 dela, nas regras de hoje (VERSAO_FABRICA_ATUAL) */
  alugarFabrica(escolha: number, quando: number = Date.now()): TentativaFabrica {
    const n = this.fabrica.length + 1;
    this._gravar(["fabrica", { n, s: sementeFabrica(n), alugado: escolha, quando, v: VERSAO_FABRICA_ATUAL }]);
    return this.fabrica[this.fabrica.length - 1];
  }
  /** a proxima luta da tentativa em andamento (grava e joga) */
  lutarFabrica(quando: number = Date.now()): TentativaFabrica["lutas"][number] {
    const t = this.fabricaAtual, p = t?.proxima();
    if (!t || !p) throw new Error("nenhuma tentativa da Fábrica em andamento");
    this._gravar(["fabrica_luta", { n: t.n, k: p.k, s: p.s, quando }]);
    return t.lutas[t.lutas.length - 1];
  }
  /** troca o alugado pelo rival que ele acabou de derrotar */
  trocarFabrica(quando: number = Date.now()): void {
    const t = this.fabricaAtual;
    if (!t) throw new Error("nenhuma tentativa da Fábrica em andamento");
    this._gravar(["fabrica_troca", { n: t.n, k: t.lutas.length - 1, quando }]);
  }
  /* ------------------------------------------------ o Salao (motor/salao.ts) */
  private _salao(x: TentativaSalao): void {
    this._campos(x, "tentativa do Salão", ["n", "quando"]);
    if (!this.titulo) throw new Error("tentativa do Salão antes do título da Liga no registro do Tamer");
    if (x.n !== this.salao.length + 1) throw new Error(`tentativa do Salão fora de ordem no registro do Tamer: ${x.n} (esperada ${this.salao.length + 1})`);
    const L = x.lutas;
    if (!Array.isArray(L) || L.length < 1 || L.length > ESTAGIOS_SALAO.length) throw new Error(`tentativa ${x.n} do Salão sem as lutas no registro do Tamer`);
    L.forEach((l, i) => {
      this._campos(l, `luta ${i + 1} da tentativa ${x.n} do Salão`, ["pet", "k", "s", "tick"]);
      if (l.est !== ESTAGIOS_SALAO[i]) throw new Error(`a luta ${i + 1} do Salão é do estágio ${ESTAGIOS_SALAO[i]}, não ${JSON.stringify(l.est)}, no registro do Tamer`);
      if (typeof l.forma !== "string" || typeof l.venceu !== "boolean") throw new Error(`luta ${i + 1} do Salão sem a forma ou o resultado no registro do Tamer`);
      if (l.s !== sementeSalao(l.pet, l.k)) throw new Error(`a luta ${l.k} do pet ${l.pet} no Salão tem a semente ${sementeSalao(l.pet, l.k)}, não ${l.s}, no registro do Tamer`);
      if (!l.venceu && i < L.length - 1) throw new Error(`a tentativa ${x.n} do Salão segue depois de uma derrota no registro do Tamer`);
    });
    if (L.length < ESTAGIOS_SALAO.length && L[L.length - 1].venceu) throw new Error(`a tentativa ${x.n} do Salão parou numa vitória no registro do Tamer`);
    if (new Set(L.map(l => l.pet)).size !== L.length) throw new Error(`o mesmo pet em dois estágios na tentativa ${x.n} do Salão no registro do Tamer`);
    this.salao.push({ n: x.n, quando: x.quando, lutas: L.map(l => ({ ...l })) });
  }
  /** a tentativa do Salao que acabou de acontecer (as lutas ja estao nos registros dos pets): grava */
  registrarSalao(lutas: LutaSalao[], quando: number = Date.now()): TentativaSalao {
    this._gravar(["salao", { n: this.salao.length + 1, quando, lutas: lutas.map(l => ({ ...l })) }]);
    return this.salao[this.salao.length - 1];
  }
  /** o pet m fez uma sequencia de `valor` vitorias na instalacao, maior que o recorde do Tamer: grava o recorde novo */
  baterRecorde(inst: IdInstalacao, valor: number, m: Motor, quando: number = Date.now()): Recorde {
    this._gravar(["recorde", { inst, valor, quando, pet: m.semente, forma: nomeForma(m.forma), tick: m.e.tick }]);
    return this.recordes[this.recordes.length - 1];
  }
  private _gravar(ev: EventoTamer): void { this.aplicar(ev); this.log.push(ev); }
  /** o pet m venceu a Liga: grava o titulo (o primeiro dele) */
  ganharTitulo(m: Motor, quando: number = Date.now()): Campeao {
    this._gravar(["campeao", { n: this.campeoes.length + 1, quando, pet: m.semente, forma: nomeForma(m.forma), tick: m.e.tick }]);
    return this.campeoes[this.campeoes.length - 1];
  }
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
    t.log = log.map(ev => JSON.parse(JSON.stringify(ev)) as EventoTamer);
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
  /* o registro 7 so tem a Fabrica em tempo real: uma tentativa antiga nele e registro corrompido */
  if (s.versao === 7) for (const ev of s.log as EventoTamer[])
    if (Array.isArray(ev) && ev[0] === "fabrica" && (ev[1] as InicioFabrica).v !== VERSAO_FABRICA_TR)
      throw new Error(`o registro 7 do Tamer tem a tentativa ${(ev[1] as InicioFabrica).n} da Fábrica com as regras de antes (v ${JSON.stringify((ev[1] as InicioFabrica).v)})`);
  return Tamer.reproduzir(s.log as EventoTamer[]);
}
/** o registro do Tamer sem a Fabrica de antes (descarte 6): tira as tentativas que nao sao da luta em tempo real. Devolve o registro novo e
    quantas tentativas sairam */
export function semFabricaAntiga(log: readonly EventoTamer[]): { log: EventoTamer[]; tentativas: number } {
  const antigas = new Set<number>();
  for (const ev of log) if (ev[0] === "fabrica" && (ev[1] as InicioFabrica).v !== VERSAO_FABRICA_TR) antigas.add((ev[1] as InicioFabrica).n);
  if (antigas.size && log.some(ev => ev[0] === "fabrica" && (ev[1] as InicioFabrica).v === VERSAO_FABRICA_TR))
    throw new Error("o registro do Tamer mistura a Fábrica de antes com a em tempo real");
  return { log: log.filter(ev => !(EVENTOS_FABRICA.includes(ev[0]) && antigas.has((ev[1] as { n: number }).n))), tentativas: antigas.size };
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
/** o titulo que o pet acabou de dar ao Tamer: a primeira vez que ele venceu a Liga dos Lideres (o motor conta os titulos do pet pelo
    evento de luta da Liga). So pets v6 e com as 6 medalhas no Tamer. Devolve o titulo novo (ja aplicado) ou null */
export function conferirCampeao(t: Tamer, m: Motor, quando: number = Date.now()): Campeao | null {
  if (m.versao < VERSAO_LIGA || m.liga.titulos < 1 || t.n < MEDALHAS_LIGA || t.tituloDe(m.semente)) return null;
  return t.ganharTitulo(m, quando);
}
/** os recordes que o pet acabou de dar ao Tamer: a maior sequencia dele numa instalacao da Fronteira, quando passa a do Tamer (o motor
    conta as sequencias do pet pelo evento de luta da instalacao). So pets v6 e depois do titulo. Devolve os recordes novos (ja aplicados) */
export function conferirRecordes(t: Tamer, m: Motor, quando: number = Date.now()): Recorde[] {
  if (m.versao < VERSAO_INSTALACOES || !t.titulo) return [];
  const novos: Recorde[] = [];
  for (const x of INSTALACOES) {
    const v = m.instalacoes[x.id].recorde;
    if (v > (t.recorde(x.id)?.valor ?? 0)) novos.push(t.baterRecorde(x.id, v, m, quando));
  }
  return novos;
}
/** o pet passa a conhecer as medalhas do Tamer (evento "u" no registro dele) e, com as 6 e o titulo do Tamer, a Fronteira aberta (evento
    "f": as instalacoes). Pet v1-v5 ou morto: nada. Devolve true se o registro do pet mudou */
export function sincronizarPet(t: Tamer, m: Motor): boolean {
  if (m.versao < 6 || m.morte) return false;
  let mudou = false;
  try {
    if (m.medalhas < t.n) { m.liberar(t.n); mudou = true; }
    if (t.titulo && !m.fronteira && m.medalhas >= MEDALHAS_LIGA && !m.morte) { m.abrirFronteira(); mudou = true; }
  } catch (err) { if (err instanceof PetMorto) return mudou; throw err; }
  return mudou;
}

/* ------------------------------------------------ descarte unico dos pets antigos */
/** marcador do descarte unico: a versao do descarte que ja rodou neste navegador. 1 = medalhas do Tamer (2026-09-29: os
    pets v1-v5 saem); 2 = combate V21D nos pets v6 (2026-09-30, docs/VALIDACAO_V21D.md: os v6 de antes mudariam de
    comportamento no replay e saem tambem); 3 = arenas com lideres (2026-09-30, DESIGN_MEDALHAS_ARENAS parte 2: as lutas
    de arena mudam no replay dos v6 de antes, e saem de novo); 4 = escala dos pets v6 (2026-09-30, CESC_V6: as lutas da
    campanha e das arenas mudam no replay dos v6 de antes, e eles saem de novo); 5 = limite de turnos do desafiado (2026-09-30: as
    lutas dos v6 que chegam ao limite mudam de resultado no replay, e eles saem de novo); 6 = a luta em tempo real (2026-10-29, COMBATE-TR,
    E2 e D-4: os pets v1-v12 lutavam por turnos e saem; o Tamer fica, sem a Fabrica de antes, e os saves descartados ficam guardados para
    o aviso oferecer o arquivo). Sem a chave: 1 se o registro do Tamer existe (o descarte das medalhas rodou antes do marcador existir),
    senao 0 */
export const CHAVE_DESCARTE = CHAVE + "-descarte";
export const VERSAO_DESCARTE = 6;
/** cada descarte apaga os pets ate esta versao (inclusive) */
const DESCARTA_ATE: Record<number, number> = { 1: 5, 2: 6, 3: 6, 4: 6, 5: 6, 6: 12 };

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
  const saves: unknown[] = [];
  const ativo = armaz.getItem(CHAVE);
  if (antigo(ativo)) { saves.push(JSON.parse(ativo!)); armaz.removeItem(CHAVE); descartados++; }
  const bg = armaz.getItem(chaveGuardados);
  if (bg !== null) {
    let g: unknown = null;
    try { g = JSON.parse(bg); } catch { /* guardados ilegiveis: ficam para o erro de sempre */ }
    if (Array.isArray(g)) {
      const ficam = g.filter(x => !antigo(JSON.stringify(x)));
      saves.push(...g.filter(x => antigo(JSON.stringify(x))));
      descartados += g.length - ficam.length;
      if (ficam.length !== g.length) armaz.setItem(chaveGuardados, JSON.stringify(ficam));
    }
  }
  /* sem a chave dos guardados, a escada de exemplo (pets v3) seria semeada logo depois: fica vazia de proposito */
  if (descartados && armaz.getItem(chaveGuardados) === null) armaz.setItem(chaveGuardados, "[]");
  /* o descarte 6 (D-4): o Tamer fica, sem a Fabrica de antes; os saves descartados ficam para o arquivo; o aviso conta os dois */
  let fabrica = 0;
  if (tinhaTamer) {
    const r = semFabricaAntiga(lerTamer(armaz).log);
    fabrica = r.tentativas;
    gravarTamer(armaz, Tamer.reproduzir(r.log));
  } else gravarTamer(armaz, new Tamer());
  if (saves.length) {
    let ja: unknown[] = [];
    try { const x = JSON.parse(armaz.getItem(CHAVE_DESCARTADOS) ?? "[]"); if (Array.isArray(x)) ja = x; } catch { /* ilegivel: recomeca */ }
    armaz.setItem(CHAVE_DESCARTADOS, JSON.stringify([...ja, ...saves]));
  }
  armaz.setItem(CHAVE_DESCARTE, String(VERSAO_DESCARTE));
  if (descartados || fabrica) armaz.setItem(CHAVE_AVISO_TR, JSON.stringify({ pets: descartados, fabrica }));
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
