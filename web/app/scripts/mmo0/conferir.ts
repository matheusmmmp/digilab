/* MMO0: a conferencia no Node de uma vida gravada no Chrome (scripts/mmo0/vida.ts). Quatro perguntas, as da secao 12 do
   docs/PLANO_V3_MMO.md:
     1. o Node aceita o registro do Chrome? (Motor.reproduzir, o caminho do replay; um evento que nao reproduz falha alto)
     2. a mesma assinatura no fim? (e, se nao, o primeiro marco de 50 passos em que ela diverge)
     3. o mesmo resultado de cada luta? (venceu, lesao, a vida que sobrou e os passos de cada luta da serie)
     4. o mesmo registro? (o Node vive a mesma vida do roteiro e compara o registro com o do Chrome)
   E, para ver o tamanho da divergencia, os numeros que diferem no fim, no estado do pet (m.e) e na assinatura inteira, e a maior
   diferenca relativa. */
import { Motor, type EventoRegistro } from "../../motor/index.ts";
import { fnv, viver, type LutaVista, type Vida } from "./vida.ts";

export interface Conferencia {
  semente: number; cerebro: string; eventos: number; lutas: number; passos: number; morreu: boolean;
  aceito: boolean; erro: string | null;
  mesmaAssinatura: boolean; primeiroMarcoDivergente: number | null;
  lutasIguais: number; lutasDiferentes: number; primeiraLutaDiferente: number | null;
  mesmoRegistro: boolean; primeiroEventoDiferente: number | null;
  numerosDiferentes: number; maiorDiferencaRelativa: number;
  /** a assinatura inteira: os numeros que diferem, a maior diferenca relativa, os valores nao numericos que diferem e os caminhos (a posicao
      no array da assinatura, Motor.assinatura) */
  assinaturaNumerosDiferentes: number; assinaturaMaiorDiferencaRelativa: number; assinaturaNaoNumericos: number; assinaturaCaminhos: string[];
}

/** dois JSON: os numeros que diferem (quantos, a maior diferenca relativa |a-b| / max(|a|,|b|) e os caminhos) e os outros valores que
    diferem (texto, booleano, chave a mais), que nao seriam o ultimo bit */
/** um texto que e JSON, ou uma lista de numeros separados por virgula, lido como valor (null: nao e) */
function numerosNoTexto(t: string): unknown {
  for (const x of [t, "[" + t + "]"]) { try { return JSON.parse(x); } catch { /* nao e esse formato: tenta o outro */ } }
  return null;
}
interface Dif { n: number; max: number; caminhos: string[]; naoNumericos: number }
function diferencas(a: unknown, b: unknown, caminho = "", acc: Dif = { n: 0, max: 0, caminhos: [], naoNumericos: 0 }): Dif {
  if (typeof a === "number" && typeof b === "number") {
    if (a !== b) {
      acc.n++; const d = Math.abs(a - b) / Math.max(Math.abs(a), Math.abs(b)); if (d > acc.max) acc.max = d;
      if (acc.caminhos.length < 10) acc.caminhos.push(caminho);
    }
  } else if (a && b && typeof a === "object" && typeof b === "object") {
    for (const k of new Set([...Object.keys(a as object), ...Object.keys(b as object)]))
      diferencas((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k], caminho + "/" + k, acc);
  } else if (typeof a === "string" && typeof b === "string" && a !== b && numerosNoTexto(a) && numerosNoTexto(b)) {
    diferencas(numerosNoTexto(a), numerosNoTexto(b), caminho + " (texto)", acc);   // a assinatura do cerebro e um texto de numeros
  } else if (JSON.stringify(a) !== JSON.stringify(b)) { acc.naoNumericos++; if (acc.caminhos.length < 10) acc.caminhos.push(caminho + " (nao numerico)"); }
  return acc;
}
const igualLuta = (x: LutaVista, y: LutaVista | undefined): boolean => !!y && JSON.stringify(x) === JSON.stringify(y);

export function conferir(v: Vida): Conferencia {
  const base = { semente: v.semente, cerebro: v.cerebro, eventos: v.log.length, lutas: v.lutas.length, passos: v.passos, morreu: v.morreu };
  /* 1 e 2: o replay oficial */
  let replay: Motor | null = null, erro: string | null = null;
  try { replay = Motor.reproduzir(v.semente, v.log, v.versao); } catch (e) { erro = e instanceof Error ? e.message : String(e); }
  /* 2 (os marcos) e 3 (as lutas): o mesmo registro, evento a evento, com a luta pelo lutarPoc (o caminho do roteiro no Chrome) */
  const lutasNode: LutaVista[] = [];
  let primeiroMarco: number | null = null;
  if (replay) {
    const m = new Motor(v.semente, v.versao), marcos = new Map(v.marcos.map(x => [x.indice, x.hash]));
    v.log.forEach((ev: EventoRegistro, i: number) => {
      if (ev[1] === "l") {
        const r = m.lutarPoc(ev[2].r, ev[2].s, ev[2].m ?? null);
        lutasNode.push({ indice: i, rival: r.rival, semente: r.semente, venceu: r.venceu, lesao: r.lesao, vidas: r.serie.flatMap(x => [x.vidaA, x.vidaB, x.passos]) });
      } else m.aplicarEvento(ev);
      const h = marcos.get(i + 1);
      if (h !== undefined && primeiroMarco === null && fnv(m.assinatura()) !== h) primeiroMarco = i + 1;
    });
  }
  let lutasIguais = 0, primeiraLuta: number | null = null;
  v.lutas.forEach((l, k) => { if (igualLuta(l, lutasNode[k])) lutasIguais++; else if (primeiraLuta === null) primeiraLuta = k; });
  /* 4: o Node vive a mesma vida */
  const node = viver(v.semente, v.cerebro);
  const a = v.log.map(x => JSON.stringify(x)), b = node.log.map(x => JSON.stringify(x));
  let primeiroEvento: number | null = null;
  for (let i = 0; i < Math.max(a.length, b.length); i++) if (a[i] !== b[i]) { primeiroEvento = i; break; }
  const vazio: Dif = { n: -1, max: -1, caminhos: [], naoNumericos: -1 };
  const dif = replay ? diferencas(JSON.parse(v.estado), JSON.parse(JSON.stringify(replay.e))) : vazio;
  const difA = replay ? diferencas(JSON.parse(v.assinatura), JSON.parse(replay.assinatura())) : vazio;
  return { ...base, aceito: !!replay, erro,
    mesmaAssinatura: !!replay && replay.assinatura() === v.assinatura, primeiroMarcoDivergente: primeiroMarco,
    lutasIguais, lutasDiferentes: v.lutas.length - lutasIguais, primeiraLutaDiferente: primeiraLuta,
    mesmoRegistro: primeiroEvento === null, primeiroEventoDiferente: primeiroEvento,
    numerosDiferentes: dif.n, maiorDiferencaRelativa: dif.max,
    assinaturaNumerosDiferentes: difA.n, assinaturaMaiorDiferencaRelativa: difA.max, assinaturaNaoNumericos: difA.naoNumericos,
    assinaturaCaminhos: difA.caminhos };
}
