/* Os momentos do pet no habitat (docs/PLANO_V3_HABITAT_REACOES.md, etapa HR1; HR-1 a HR-8 aprovadas pelo Matheus em 2026-11-11). SO VISTA: le o
   que o motor ja decidiu (o consumo, o chamado, o sono, o ovo, a morte) e o que o dono acabou de fazer (acoes.ts), e escolhe o clipe que ja existe
   no atlas para mostrar. Nao escreve no motor, no log nem no save, e o replay e a paridade nao o veem. Sem DOM nas contas (testadas em node).
   Duas familias, como no atlas:
     - os clipes de acao (CLIPES_ACOES: Feliz, Sacudir, Chamar; o Die da luta), tocados uma vez (o momento) ou em laco (o estado);
     - os rostos (CLIPES_REACOES: Triste, Cansado, Recusa), que vao para o evento de reacao.ts (so as formas que os tem).
   Os tempos sao da vista: PROPOSTO, SEM FONTE. */
import type { ClipeReacao } from "../../atlas.ts";
import { CAT, type Motor } from "../../../motor/index.ts";
import { REACAO, registrarMomentoRosto } from "./reacao.ts";
import { emitirBipe, emitirSom, emitirVoz } from "../../somEventos.ts";

/** o clipe de acao que um momento toca uma vez */
export type ClipeMomento = "Feliz" | "Sacudir";
/** o clipe em laco que um estado do pet segura enquanto dura */
export type ClipeEstado = "Feliz" | "Chamar" | "Die";

/** os numeros da vista (PROPOSTO, SEM FONTE) */
export const MOMENTOS = {
  /** a espera antes do clipe de um gesto do dono (o flash dele aparece primeiro, como o Idle antes do rosto em reacao.ts) */
  esperaDonoMs: 300,
  /** um momento que nao pode tocar (outro clipe no corpo) espera ate isto e depois e descartado */
  esperaMaxMs: 3000,
  /** a fome que o consumo tem de subir para o pet ficar Feliz depois de comer */
  fomeFeliz: 0.2,
  /** o Feliz do carinho sai quando o pulinho da reacao ao toque acaba (cenaAcao.ts, CENA_ACAO.reacaoMs) */
  carinhoMs: 1600,
  /** os rostos dos momentos: quanto duram */
  acordarMs: 1500, perdidoMs: 2000, podreMs: 2000, vazioMs: 2000,
  /** o pet dormindo vira de lado quando o dono tenta pegar: quanto dura */
  viraMs: 600,
  /** o lance do dono que o pet recusou (BOLA_BRINCAR, BB-9): quanto dura o rosto da recusa */
  recusaBolaMs: 2000,
} as const;

/** o que a vista le do motor a cada quadro */
export interface EntradaMomentos {
  chave: string;
  nascendo: number;
  dormindo: boolean;
  morto: boolean;
  acao: string;
  /** os chamados abertos do bebe e quantos foram atendidos (Motor.chamadosAbertos, Motor.chamados.atendidos); `urgente`: algum esta no ultimo
      terco da janela (o cartao grande de TelaPet.tsx) */
  abertos: readonly string[];
  urgente: boolean;
  atendidos: number;
  /** o tamanho de mundo.consumos e o ultimo consumo (null sem mundo ou sem consumo) */
  consumos: number;
  /** o id do ultimo episodio "nao_havia" da memoria do modular (a ida ao lugar lembrado que estava vazio); null sem modular ou sem episodio */
  vazio: number | null;
  ultimo: { tipo: string; situacao: string; fome_antes: number; fome_depois: number } | null;
}

interface Pendente { clipe: ClipeMomento; em: number; motivo: string }
interface Visto { chave: string; nascendo: number; dormindo: boolean; abertos: readonly string[]; urgente: boolean; atendidos: number; consumos: number; acao: string; vazio: number | null }

let visto: Visto | null = null;
let fila: Pendente[] = [];
let tocando: { clipe: ClipeMomento; desde: number; fim: number; motivo: string } | null = null;
let viraDesde = -1e9;

const agendar = (clipe: ClipeMomento, em: number, motivo: string): void => { fila = [...fila, { clipe, em, motivo }]; };

/** o dono fez uma acao agora (acoes.ts, `agir`): limpar sacode, tratar a lesao deixa Feliz, o carinho deixa Feliz depois do pulinho */
export function momentoDoDono(acao: string, agora: number): void {
  /* o som do gesto do dono toca na hora (HR2); a voz do pet vem com o clipe, quando ele sente (momentoAgora) */
  if (acao === "limpar") { emitirSom("cuidado_limpar"); agendar("Sacudir", agora + MOMENTOS.esperaDonoMs, "limpar"); }
  else if (acao === "tratar_lesao") { emitirSom("tratar"); agendar("Feliz", agora + MOMENTOS.esperaDonoMs, "tratar"); }
  else if (acao === "acariciar") emitirSom("cuidado_toque");
}
/** a reacao ao toque relaxou o pet (cenaAcao.ts, reacaoDoCorpo): Feliz quando o pulinho acaba */
export function momentoDoCarinho(agora: number): void { agendar("Feliz", agora + MOMENTOS.carinhoMs, "carinho"); }
/** o dono tentou pegar o pet dormindo (PegarPet.tsx): ele vira de lado e segue dormindo */
export function tentouPegarDormindo(agora: number): void { viraDesde = agora; emitirSom("cuidado_recusa"); }
/** o pet dormindo esta virando de lado agora? */
export const virandoAgora = (agora: number): boolean => agora >= viraDesde && agora - viraDesde < MOMENTOS.viraMs;

/** olha o motor e agenda os momentos que nasceram desde a ultima olhada. A primeira olhada e a troca de pet nao contam. Idempotente no mesmo
    estado (as duas vistas podem chamar) */
export function vigiarMomentos(e: EntradaMomentos, agora: number): void {
  for (const k of ["nascendo", "atendidos", "consumos"] as const) if (!Number.isFinite(e[k])) throw new Error(`vigiarMomentos: ${k} nao finito`);
  const v = visto;
  visto = { chave: e.chave, nascendo: e.nascendo, dormindo: e.dormindo, abertos: [...e.abertos], urgente: e.urgente, atendidos: e.atendidos, consumos: e.consumos, acao: e.acao, vazio: e.vazio };
  if (!v || v.chave !== e.chave) { fila = []; tocando = null; viraDesde = -1e9; return; }
  if (e.morto) { fila = []; tocando = null; return; }
  /* a casca quebrou: o pet aparece Feliz, com o som do nascimento */
  if (v.nascendo > 0 && e.nascendo <= 0) { emitirSom("nascer"); agendar("Feliz", agora, "nasceu"); }
  /* dormiu e acordou: o bocejo; acordado, Cansado por um instante. A voz do que o pet faz sozinho e espontanea (a pausa longa de somVoz.ts) */
  if (!v.dormindo && e.dormindo) emitirVoz("bocejo", true);
  if (v.dormindo && !e.dormindo) { registrarMomentoRosto("Cansado", agora, MOMENTOS.acordarMs); emitirVoz("bocejo", true); }
  /* o chamado: abre (o bipe e a voz chamando), aperta (o bipe insistente), e atendido (o contador sobe) ou perdido (um tipo some sem o
     contador subir, com o bipe descendo) */
  if (e.abertos.some(t => !v.abertos.includes(t))) { emitirBipe("abre"); emitirVoz("chamando", true); }
  else if (e.urgente && !v.urgente) { emitirBipe("urgente"); emitirVoz("chamando", true); }
  if (e.atendidos > v.atendidos) { emitirSom("chamado_atendido"); agendar("Feliz", agora, "chamado"); }
  else if (v.abertos.some(t => !e.abertos.includes(t))) { emitirBipe("perdido"); registrarMomentoRosto("Triste", agora, MOMENTOS.perdidoMs); }
  /* a acao do motor que comeca: brincar alegra a voz, emburrar resmunga, chamar atencao chama */
  if (e.acao !== v.acao && !e.dormindo) {
    if (e.acao === "brincar") emitirVoz("contente", true);
    else if (e.acao === "emburrar") emitirVoz("resmungo", true);
    else if (e.acao === "chamar_atencao") emitirVoz("chamando", true);
  }
  /* o lugar lembrado estava vazio (CADEIA, etapa 2, D6): Triste por um instante, com o rosto que o atlas ja tem */
  if (e.vazio !== null && (v.vazio === null || e.vazio > v.vazio)) registrarMomentoRosto("Triste", agora, MOMENTOS.vazioMs);
  /* comeu: a fruta podre e Recusa; a comida madura que encheu bem a barriga, Feliz (depois do clipe Comer, pela fila) */
  if (e.consumos > v.consumos && e.ultimo) {
    const u = e.ultimo;
    if (!Number.isFinite(u.fome_antes) || !Number.isFinite(u.fome_depois)) throw new Error("vigiarMomentos: consumo sem fome finita");
    if (u.situacao !== "madura") { emitirSom("fruta_podre"); emitirVoz("resmungo"); registrarMomentoRosto("Recusa", agora, MOMENTOS.podreMs); }
    else {
      if (u.tipo !== "racao") emitirSom("fruta_boa");
      if (u.tipo !== "racao" || u.fome_depois - u.fome_antes >= MOMENTOS.fomeFeliz) agendar("Feliz", agora, "comeu");
    }
  }
}

/** o clipe de momento no corpo agora, ou null. `livre` diz se o corpo pode toca-lo (sem golpe, sem o Comer, sem a mao, acordado); `ciclo` e a
    soma dos ms do clipe em cada forma (null: a forma nao tem o clipe, e o momento sai sem tocar) */
export function momentoAgora(agora: number, livre: boolean, ciclo: (c: ClipeMomento) => number | null): { clipe: ClipeMomento; desde: number } | null {
  if (tocando && agora < tocando.fim) return { clipe: tocando.clipe, desde: tocando.desde };
  tocando = null;
  fila = fila.filter(p => agora - p.em <= MOMENTOS.esperaMaxMs);
  if (!livre) return null;
  const i = fila.findIndex(p => agora >= p.em);
  if (i < 0) return null;
  const p = fila[i];
  fila = fila.filter((_, j) => j !== i);
  const c = ciclo(p.clipe);
  if (c === null) return null;
  if (!(c > 0) || !Number.isFinite(c)) throw new Error(`ciclo do ${p.clipe} invalido: ${c}`);
  tocando = { clipe: p.clipe, desde: agora, fim: agora + c, motivo: p.motivo };
  /* o som de quando o clipe comeca (HR2): o fim do comer depois do clipe Comer, e a voz contente do pet que sentiu */
  if (p.motivo === "comeu") emitirSom("comer_fim");
  emitirVoz("contente");
  return { clipe: p.clipe, desde: agora };
}

/** algum chamado do bebe aberto esta no ultimo terco da janela? (a regra do cartao grande de TelaPet.tsx, sem a acao chamar_atencao, que tem a
    voz dela) */
export function chamadoUrgente(m: Pick<Motor, "chamadosAbertos" | "chamados" | "e">): boolean {
  return m.chamadosAbertos().some(c => CAT.janelaChamado - (m.e.tick - m.chamados.abertos[c]!) <= CAT.janelaChamado / 3);
}
/** o id do ultimo episodio "nao_havia" da memoria do modular, ou null (o A, ou nenhum ainda) */
export function ultimoVazio(m: { lab: { mem: { episodios: readonly { id: number; classe: string }[] } } | null }): number | null {
  let r: number | null = null;
  for (const ep of m.lab?.mem.episodios ?? []) if (ep.classe === "nao_havia" && (r === null || ep.id > r)) r = ep.id;
  return r;
}
/** o clipe em laco do estado do pet: Die morto; Chamar com um chamado aberto ou chamando atencao; Feliz brincando. Null nos outros */
export function estadoAgora(e: Pick<EntradaMomentos, "morto" | "dormindo" | "abertos" | "acao" | "nascendo">): ClipeEstado | null {
  if (e.nascendo > 0) return null;
  if (e.morto) return "Die";
  if (e.dormindo) return null;
  if (e.abertos.length > 0 || e.acao === "chamar_atencao") return "Chamar";
  if (e.acao === "brincar") return "Feliz";
  return null;
}

/** o clipe de momento ou de estado no corpo agora (a ilha marca a cada quadro; o e2e le por window.__digilab.clipeMomento) */
let noCorpo: string | null = null;
export const marcarClipeMomento = (c: string | null): void => { noCorpo = c; };
export const clipeMomentoAgora = (): string | null => noCorpo;
/** o motivo do momento que toca agora (o e2e le por window.__digilab.momento) */
export const motivoAgora = (): string | null => tocando?.motivo ?? null;
/** os rostos que um momento usa (para o teste conferir que existem em CLIPES_REACOES) */
export const ROSTOS_DOS_MOMENTOS: readonly ClipeReacao[] = ["Cansado", "Triste", "Recusa"];

/* ------------------------------------------------------------------ a bola do dono (docs/TAREFA_V3_BOLA_BRINCAR.md, BB-9; a etapa BB3)
   O motor ja decidiu tudo: o Brincar do dono jogou a bola (o `lances` do Mundo, BB-1), e o pet chutou (uma rolagem nova) ou nao, dentro da janela
   do convite (`janela_convite_ticks`, BB-4). A vista so mostra: o som do lance, o som do chute com a voz contente, e, se a janela passou sem chute,
   o rosto da recusa (Cansado com a energia baixa, senao Recusa; o momento de hoje do emburrar e do cansado). So vista, como o resto do arquivo. */

/** um lance do motor, como a vista o le (o `Lance` do Mundo): o tick (relogio do mundo) e onde a bola caiu (subunidades) */
export interface LanceLido { tick: number; para: readonly [number, number] }
/** o que a vista le do mundo para a bola a cada quadro */
export interface EntradaBola {
  chave: string;
  /** os lances do mundo (null sem o lance ligado: o pet de antes da v30) */
  lances: readonly LanceLido[] | null;
  /** os ticks (relogio do mundo) das rolagens da bola, em ordem */
  rolagens: readonly number[];
  /** o tick de agora no relogio do mundo */
  tickMundo: number;
  /** a janela do convite (ticks) */
  janela: number;
  /** a energia do pet (0..1), para o rosto da recusa */
  energia: number;
  dormindo: boolean;
  /** o cerebro recebe o convite (o modular)? Com o A (BB-6) o pet nao foi convidado, e nao ha recusa a mostrar */
  convidado: boolean;
}
/** o que aconteceu desde a ultima olhada: o lance novo (para o arco), se houve chute, e o rosto da recusa */
export interface SaidaBola { lance: LanceLido | null; chutou: boolean; recusa: ClipeReacao | null }

let vistoBola: { chave: string; lances: number; rolagens: number } | null = null;
/** quantos lances, chutes e recusas a vista mostrou desde a ultima troca de pet (o e2e le por window.__digilab.bolaVista) */
let contaBola = { lances: 0, chutes: 0, recusas: 0 };
export const bolaVista = (): { lances: number; chutes: number; recusas: number } => ({ ...contaBola });
/** o lance que ainda espera o chute (o tick dele no relogio do mundo) */
let esperaChute: number | null = null;

/** a rolagem do tick `r` responde ao lance do tick `l`, na janela do convite? */
export const chuteNaJanela = (l: number, r: number, janela: number): boolean => r >= l && r < l + janela;

/** olha o mundo e diz o que a bola fez desde a ultima olhada; emite o som do lance, o do chute e a voz, e registra o rosto da recusa. A primeira
    olhada e a troca de pet nao contam. Idempotente no mesmo estado */
export function vigiarBola(e: EntradaBola, agora: number): SaidaBola {
  for (const k of ["tickMundo", "janela", "energia"] as const) if (!Number.isFinite(e[k])) throw new Error(`vigiarBola: ${k} nao finito`);
  if (!(e.janela > 0)) throw new Error(`vigiarBola: janela invalida ${e.janela}`);
  const nl = e.lances?.length ?? 0, nr = e.rolagens.length, v = vistoBola;
  vistoBola = { chave: e.chave, lances: nl, rolagens: nr };
  const saida: SaidaBola = { lance: null, chutou: false, recusa: null };
  if (!v || v.chave !== e.chave) { esperaChute = null; contaBola = { lances: 0, chutes: 0, recusas: 0 }; return saida; }
  if (nl > v.lances) {
    const l = e.lances![nl - 1]!;
    saida.lance = l;
    esperaChute = l.tick;
    contaBola.lances++;
    emitirSom("cuidado_toque");                       /* o gesto do dono que joga a bola */
  }
  if (nr > v.rolagens) {
    saida.chutou = true;
    contaBola.chutes++;
    emitirSom("treino_alvo"); emitirVoz("contente");  /* a batida na bola e o pet contente */
    if (esperaChute !== null && e.rolagens.slice(v.rolagens).some(r => chuteNaJanela(esperaChute!, r, e.janela))) esperaChute = null;
  }
  if (esperaChute !== null && e.tickMundo >= esperaChute + e.janela) {
    esperaChute = null;
    if (e.convidado && !e.dormindo) {
      const r: ClipeReacao = e.energia < REACAO.energiaBaixa ? "Cansado" : "Recusa";
      registrarMomentoRosto(r, agora, MOMENTOS.recusaBolaMs);
      emitirVoz(r === "Cansado" ? "bocejo" : "resmungo");
      saida.recusa = r;
      contaBola.recusas++;
    }
  }
  return saida;
}

/** so para os testes */
export function esquecerMomentos(): void { visto = null; fila = []; tocando = null; viraDesde = -1e9; noCorpo = null; vistoBola = null; esperaChute = null; contaBola = { lances: 0, chutes: 0, recusas: 0 }; }
