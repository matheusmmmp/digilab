/* Exportar e importar pets (pranchas MpImportar e MpImportarDesktop). O arquivo .digilab e o proprio save do pet:
   {semente, log, versao}. Importar = replay do registro (tem que abrir); pet novo vai para a espera. Mesma semente com
   outro registro = conflito: o dono escolhe qual fica, e o outro vai para a espera (ninguem e apagado). */
import { useEffect, useState } from "react";
import { Motor, type EventoRegistro } from "../motor/index.ts";
import { jogoAtual, trocarMotor } from "./jogo.ts";
import { CHAVE_GUARDADOS, abrirGuardado, lerGuardados, type Guardado } from "./pets.ts";
import { textoSave } from "./save.ts";
import { diaDe } from "./telas/pet/TelaPet.tsx";
import { nomeForma } from "../motor/index.ts";

/* tela de importar (tela cheia, aberta de Meus pets no celular e no desktop) */
let aberta = false;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
export function abrirImportar(): void { aberta = true; avisar(); }
export function fecharImportar(): void { aberta = false; avisar(); }
export function useImportar(): boolean {
  const [, t] = useState(0);
  useEffect(() => { const f = () => t(x => x + 1); ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return aberta;
}

/** nome do arquivo: o Digimon e o dia (ex.: greymon-D14.digilab) */
export function nomeArquivo(m: Motor): string {
  return `${nomeForma(m.forma).toLowerCase().replace(/[^a-z0-9]+/g, "-")}-D${diaDe(m.e.tick)}.digilab`;
}
/** baixa o registro do pet como arquivo */
export function exportarArquivo(m: Motor): void {
  const blob = new Blob([textoSave(m)], { type: "application/json" });
  const url = URL.createObjectURL(blob), a = document.createElement("a");
  a.href = url; a.download = nomeArquivo(m);
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export interface Lido { g: Guardado; m: Motor; arquivo: string }
/** le e confere o arquivo: JSON {semente, log, versao} que o replay abre; falha alto com o motivo */
export function lerArquivo(texto: string, arquivo: string): Lido {
  let d: unknown;
  try { d = JSON.parse(texto); } catch { throw new Error("o arquivo não é um registro do Digilab (JSON inválido)"); }
  const s = d as { semente?: unknown; log?: unknown; versao?: unknown };
  if (!Number.isInteger(s.semente) || !Array.isArray(s.log)) throw new Error("o arquivo não tem semente e registro");
  const g: Guardado = { semente: s.semente as number, log: s.log as EventoRegistro[], versao: (s.versao ?? 1) as number };
  let m: Motor;
  try { m = Motor.reproduzir(g.semente, g.log, g.versao); } catch (err) { throw new Error("o replay do registro não confere: " + (err instanceof Error ? err.message : String(err))); }
  return { g, m, arquivo };
}

/** onde o pet de mesma semente esta aqui: o ativo, um guardado (indice) ou nenhum */
export type Onde = { tipo: "ativo" } | { tipo: "guardado"; i: number } | { tipo: "nenhum" };
export function localizar(semente: number): Onde {
  if (jogoAtual().motor.semente === semente) return { tipo: "ativo" };
  const i = lerGuardados().findIndex(g => g.semente === semente);
  return i >= 0 ? { tipo: "guardado", i } : { tipo: "nenhum" };
}
/** o pet aqui, com a mesma semente (para comparar) */
export function petAqui(o: Onde): Motor | null {
  return o.tipo === "ativo" ? jogoAtual().motor : o.tipo === "guardado" ? abrirGuardado(lerGuardados()[o.i]) : null;
}
const igual = (a: Guardado, b: Motor): boolean => JSON.stringify(a.log) === JSON.stringify(b.log) && (a.versao ?? 1) === b.versao;

/** sem conflito: vai para a espera. Devolve a mensagem para a tela */
export function importarSemConflito(l: Lido): string {
  const o = localizar(l.g.semente);
  if (o.tipo !== "nenhum") {
    if (igual(l.g, petAqui(o)!)) return `${nomeForma(l.m.forma)} já está aqui, com o mesmo registro.`;
    throw new Error("conflito: o pet já existe com outro registro");
  }
  const g = lerGuardados(); g.push(l.g); localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
  return `${nomeForma(l.m.forma)} importado: está em espera em Meus pets.`;
}
/** conflito resolvido a favor do arquivo: ele toma o lugar do de aqui, e o de aqui vai para a espera */
export function ficarComArquivo(l: Lido): void {
  const o = localizar(l.g.semente), g = lerGuardados();
  if (o.tipo === "ativo") {
    g.push(JSON.parse(textoSave(jogoAtual().motor)) as Guardado);
    localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
    trocarMotor(l.m, "save");
  } else if (o.tipo === "guardado") {
    g.push(g[o.i]); g[o.i] = l.g;
    localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
  } else throw new Error("não há conflito para resolver");
}
