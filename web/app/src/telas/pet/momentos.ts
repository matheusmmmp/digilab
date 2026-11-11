/* Os momentos do pet no habitat (docs/PLANO_V3_HABITAT_REACOES.md, etapa HR1; HR-1 a HR-8 aprovadas pelo Matheus em 2026-11-11). SO VISTA: le o
   que o motor ja decidiu (o consumo, o chamado, o sono, o ovo, a morte) e o que o dono acabou de fazer (acoes.ts), e escolhe o clipe que ja existe
   no atlas para mostrar. Nao escreve no motor, no log nem no save, e o replay e a paridade nao o veem. Sem DOM nas contas (testadas em node).
   Duas familias, como no atlas:
     - os clipes de acao (CLIPES_ACOES: Feliz, Sacudir, Chamar; o Die da luta), tocados uma vez (o momento) ou em laco (o estado);
     - os rostos (CLIPES_REACOES: Triste, Cansado, Recusa), que vao para o evento de reacao.ts (so as formas que os tem).
   Os tempos sao da vista: PROPOSTO, SEM FONTE. */
import type { ClipeReacao } from "../../atlas.ts";
import { registrarMomentoRosto } from "./reacao.ts";

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
  acordarMs: 1500, perdidoMs: 2000, podreMs: 2000,
  /** o pet dormindo vira de lado quando o dono tenta pegar: quanto dura */
  viraMs: 600,
} as const;

/** o que a vista le do motor a cada quadro */
export interface EntradaMomentos {
  chave: string;
  nascendo: number;
  dormindo: boolean;
  morto: boolean;
  acao: string;
  /** os chamados abertos do bebe e quantos foram atendidos (Motor.chamadosAbertos, Motor.chamados.atendidos) */
  abertos: readonly string[];
  atendidos: number;
  /** o tamanho de mundo.consumos e o ultimo consumo (null sem mundo ou sem consumo) */
  consumos: number;
  ultimo: { tipo: string; situacao: string; fome_antes: number; fome_depois: number } | null;
}

interface Pendente { clipe: ClipeMomento; em: number; motivo: string }
interface Visto { chave: string; nascendo: number; dormindo: boolean; abertos: readonly string[]; atendidos: number; consumos: number }

let visto: Visto | null = null;
let fila: Pendente[] = [];
let tocando: { clipe: ClipeMomento; desde: number; fim: number; motivo: string } | null = null;
let viraDesde = -1e9;

const agendar = (clipe: ClipeMomento, em: number, motivo: string): void => { fila = [...fila, { clipe, em, motivo }]; };

/** o dono fez uma acao agora (acoes.ts, `agir`): limpar sacode, tratar a lesao deixa Feliz, o carinho deixa Feliz depois do pulinho */
export function momentoDoDono(acao: string, agora: number): void {
  if (acao === "limpar") agendar("Sacudir", agora + MOMENTOS.esperaDonoMs, "limpar");
  else if (acao === "tratar_lesao") agendar("Feliz", agora + MOMENTOS.esperaDonoMs, "tratar");
}
/** a reacao ao toque relaxou o pet (cenaAcao.ts, reacaoDoCorpo): Feliz quando o pulinho acaba */
export function momentoDoCarinho(agora: number): void { agendar("Feliz", agora + MOMENTOS.carinhoMs, "carinho"); }
/** o dono tentou pegar o pet dormindo (PegarPet.tsx): ele vira de lado e segue dormindo */
export function tentouPegarDormindo(agora: number): void { viraDesde = agora; }
/** o pet dormindo esta virando de lado agora? */
export const virandoAgora = (agora: number): boolean => agora >= viraDesde && agora - viraDesde < MOMENTOS.viraMs;

/** olha o motor e agenda os momentos que nasceram desde a ultima olhada. A primeira olhada e a troca de pet nao contam. Idempotente no mesmo
    estado (as duas vistas podem chamar) */
export function vigiarMomentos(e: EntradaMomentos, agora: number): void {
  for (const k of ["nascendo", "atendidos", "consumos"] as const) if (!Number.isFinite(e[k])) throw new Error(`vigiarMomentos: ${k} nao finito`);
  const v = visto;
  visto = { chave: e.chave, nascendo: e.nascendo, dormindo: e.dormindo, abertos: [...e.abertos], atendidos: e.atendidos, consumos: e.consumos };
  if (!v || v.chave !== e.chave) { fila = []; tocando = null; viraDesde = -1e9; return; }
  if (e.morto) { fila = []; tocando = null; return; }
  /* a casca quebrou: o pet aparece Feliz */
  if (v.nascendo > 0 && e.nascendo <= 0) agendar("Feliz", agora, "nasceu");
  /* acordou: Cansado por um instante */
  if (v.dormindo && !e.dormindo) registrarMomentoRosto("Cansado", agora, MOMENTOS.acordarMs);
  /* o chamado: atendido (o contador sobe) ou perdido (um tipo some sem o contador subir) */
  if (e.atendidos > v.atendidos) agendar("Feliz", agora, "chamado");
  else if (v.abertos.some(t => !e.abertos.includes(t))) registrarMomentoRosto("Triste", agora, MOMENTOS.perdidoMs);
  /* comeu: a fruta podre e Recusa; a comida madura que encheu bem a barriga, Feliz (depois do clipe Comer, pela fila) */
  if (e.consumos > v.consumos && e.ultimo) {
    const u = e.ultimo;
    if (!Number.isFinite(u.fome_antes) || !Number.isFinite(u.fome_depois)) throw new Error("vigiarMomentos: consumo sem fome finita");
    if (u.situacao !== "madura") registrarMomentoRosto("Recusa", agora, MOMENTOS.podreMs);
    else if (u.tipo !== "racao" || u.fome_depois - u.fome_antes >= MOMENTOS.fomeFeliz) agendar("Feliz", agora, "comeu");
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
  return { clipe: p.clipe, desde: agora };
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

/** so para os testes */
export function esquecerMomentos(): void { visto = null; fila = []; tocando = null; viraDesde = -1e9; noCorpo = null; }
