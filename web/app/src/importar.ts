/* Exportar e importar pets (pranchas MpImportar e MpImportarDesktop). O arquivo .digilab e o proprio save do pet:
   {semente, log, versao}. Importar = replay do registro (tem que abrir); pet novo vai para a espera. Mesma semente com
   outro registro = conflito: o dono escolhe qual fica, e o outro vai para a espera (ninguem e apagado). */
import { useEffect, useState } from "react";
import { Motor, VERSAO_PET_LAB, VERSOES_PET, type EventoRegistro } from "../motor/index.ts";
import { motorReal, sairDoLab, textoDoSaveAtual, trocarMotor } from "./jogo.ts";
import { guardarImportadoLab, lerPetLab } from "./lab.ts";
import { CHAVE_GUARDADOS, abrirGuardado, lerGuardados, type Guardado } from "./pets.ts";
import { textoSave } from "./save.ts";
import { diaDe } from "./telas/pet/TelaPet.tsx";
import { nomeForma } from "../motor/index.ts";
import { versoesQueAbrem } from "./lutaPoc.ts";

/* tela de importar (tela cheia, aberta de Meus pets no celular e no desktop) */
let aberta = false;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
export function abrirImportar(): void { sairDoLab(); aberta = true; avisar(); }
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

/** `lab`: o arquivo e do pet de teste (v16): ele vai para o espaco do laboratorio, nunca para os pets de hoje */
export interface Lido { g: Guardado; m: Motor; arquivo: string; lab: boolean }
/** le e confere o arquivo: JSON {semente, log, versao} que o replay abre, da versao de hoje (a dos ovos novos); falha alto com o motivo */
export function lerArquivo(texto: string, arquivo: string): Lido {
  let d: unknown;
  try { d = JSON.parse(texto); } catch { throw new Error("o arquivo não é um registro do Digilab (JSON inválido)"); }
  const s = d as { semente?: unknown; log?: unknown; versao?: unknown; grupo?: unknown };
  if (!Number.isInteger(s.semente) || !Array.isArray(s.log)) throw new Error("o arquivo não tem semente e registro");
  if (s.grupo !== undefined) throw new Error("o arquivo é dos dois pets: ele ainda não se importa (só se abre como o save de hoje)");
  const g: Guardado = { semente: s.semente as number, log: s.log as EventoRegistro[], versao: (s.versao ?? 1) as number };
  /* o descarte 6 (COMBATE-TR, E2): os pets de antes da luta em tempo real nao abrem mais, nem pelo arquivo */
  const lab = g.versao === VERSAO_PET_LAB;
  /* com a luta da POC ligada (LP2, LP-6), so a v21 abre */
  const abrem = versoesQueAbrem();
  if (!lab && !abrem.includes(g.versao)) throw new Error(`este pet é da versão ${g.versao} do jogo${g.versao < Math.min(...VERSOES_PET) ? ", com o combate por turnos," : abrem !== VERSOES_PET ? ", com a luta de antes," : ""} e não abre nesta versão (só a ${abrem.join(" e a ")}, com a luta em tempo real, e a ${VERSAO_PET_LAB} do laboratório)`);
  let m: Motor;
  try { m = Motor.reproduzir(g.semente, g.log, g.versao); } catch (err) { throw new Error("o replay do registro não confere: " + (err instanceof Error ? err.message : String(err))); }
  return { g, m, arquivo, lab };
}

/** onde o pet de mesma semente esta aqui: o ativo, um guardado (indice) ou nenhum */
export type Onde = { tipo: "ativo" } | { tipo: "guardado"; i: number } | { tipo: "nenhum" };
export function localizar(semente: number): Onde {
  if (motorReal().semente === semente) return { tipo: "ativo" };
  const i = lerGuardados().findIndex(g => g.semente === semente);
  return i >= 0 ? { tipo: "guardado", i } : { tipo: "nenhum" };
}
/** o pet aqui, com a mesma semente (para comparar) */
export function petAqui(o: Onde): Motor | null {
  return o.tipo === "ativo" ? motorReal() : o.tipo === "guardado" ? abrirGuardado(lerGuardados()[o.i]) : null;
}
/* o mesmo pet: o mesmo registro, sem contar a passagem de ilha (o "mi" e do jogo, nao do jogador: o arquivo exportado antes da ilha
   grande e o pet daqui, que ja passou, sao o mesmo pet) */
const semIlha = (log: readonly EventoRegistro[]): string => JSON.stringify(log.filter(e => e[1] !== "mi"));
const igual = (a: Guardado, b: Motor): boolean => semIlha(a.log) === semIlha(b.log) && (a.versao ?? 1) === b.versao;

/** sem conflito: vai para a espera. Devolve a mensagem para a tela */
export function importarSemConflito(l: Lido): string {
  if (l.lab) {
    /* o pet de teste (v16): no espaco do laboratorio, um por vez; o mesmo registro ja la e so um aviso */
    const aqui = lerPetLab();
    if (aqui.tipo === "ok" && aqui.motor.semente === l.g.semente && igual(l.g, aqui.motor)) return `${nomeForma(l.m.forma)} de teste já está no Laboratório, com o mesmo registro.`;
    guardarImportadoLab(l.m);
    return `${nomeForma(l.m.forma)} de teste importado: está em Ajustes › Laboratório, fora dos seus pets.`;
  }
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
  if (l.lab) throw new Error("o pet de teste não toma o lugar de um pet: ele só entra no Laboratório");
  sairDoLab();
  const o = localizar(l.g.semente), g = lerGuardados();
  if (o.tipo === "ativo") {
    g.push(JSON.parse(textoDoSaveAtual()) as Guardado);     // o par dos dois pets vai inteiro para a espera (CO4d)
    localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
    trocarMotor(l.m, "save");
  } else if (o.tipo === "guardado") {
    g.push(g[o.i]); g[o.i] = l.g;
    localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
  } else throw new Error("não há conflito para resolver");
}
