/* A lista de convidados (CN-10: só convidados adultos até a revisão da LGPD). Só cria conta quem está nela; quem já tem conta continua
   entrando mesmo se sair da lista (tirar alguém é apagar a conta dele).

   A lista vem de duas fontes, somadas: a variável DIGILAB_CONVIDADOS (separada por vírgula ou espaço) e a tabela `convidados`.
   Cada entrada é uma chave:
     github:<login>          o login público do GitHub (sem diferença de maiúsculas)
     <provedor>:id:<id>      o id do provedor (o `sub` do Google, o id numérico do GitHub)
     email:<e-mail>          o e-mail verificado (o Google); vira email:<sha256> ao ler, e a tabela só guarda o hash
     falso:<login>           o usuário do provedor falso (só local)
   O e-mail do provedor só se compara na memória e não se guarda (seção 9 do plano). */
import { createHash } from "node:crypto";
import type { Banco } from "./banco.ts";
import type { NomeProvedor, Perfil } from "./provedores.ts";

const hashEmail = (email: string): string => createHash("sha256").update(email.trim().toLowerCase()).digest("hex");

/** a chave normalizada de uma entrada da lista (levanta se a entrada não tem formato conhecido) */
export function normalizarChave(entrada: string): string {
  const e = entrada.trim();
  const m = /^(google|github|falso|email):(.+)$/i.exec(e);
  if (!m) throw new Error(`convidado sem formato conhecido: ${JSON.stringify(e)} (github:<login>, <provedor>:id:<id>, email:<e-mail>)`);
  const tipo = m[1]!.toLowerCase(), resto = m[2]!.trim();
  if (tipo === "email") {
    if (/^[0-9a-f]{64}$/.test(resto)) return `email:${resto}`;
    if (!resto.includes("@")) throw new Error(`convidado com e-mail inválido: ${JSON.stringify(e)}`);
    return `email:${hashEmail(resto)}`;
  }
  if (tipo === "google" && !resto.startsWith("id:")) throw new Error(`o Google entra na lista por id:<sub> ou por email:<e-mail>: ${JSON.stringify(e)}`);
  return resto.startsWith("id:") ? `${tipo}:id:${resto.slice(3).trim()}` : `${tipo}:${resto.toLowerCase()}`;
}

/** as chaves pelas quais este perfil pode estar na lista */
export function chavesDoPerfil(provedor: NomeProvedor, p: Perfil): string[] {
  const chaves = [`${provedor}:id:${p.id}`];
  if (p.login) chaves.push(`${provedor}:${p.login.toLowerCase()}`);
  if (p.emailVerificado) chaves.push(`email:${hashEmail(p.emailVerificado)}`);
  return chaves;
}

export function lerListaAmbiente(valor: string | undefined): Set<string> {
  return new Set((valor ?? "").split(/[\s,]+/).filter(Boolean).map(normalizarChave));
}

export class Convidados {
  private readonly banco: Banco;
  private readonly doAmbiente: ReadonlySet<string>;
  constructor(banco: Banco, doAmbiente: ReadonlySet<string>) { this.banco = banco; this.doAmbiente = doAmbiente; }
  contem(provedor: NomeProvedor, p: Perfil): boolean {
    const consulta = this.banco.prepare("SELECT 1 FROM convidados WHERE chave = ?");
    return chavesDoPerfil(provedor, p).some(k => this.doAmbiente.has(k) || consulta.get(k) !== undefined);
  }
  /** põe uma entrada na tabela (o formato de normalizarChave) */
  adicionar(entrada: string, agora = Date.now()): string {
    const k = normalizarChave(entrada);
    this.banco.prepare("INSERT OR IGNORE INTO convidados (chave, adicionado_em) VALUES (?, ?)").run(k, agora);
    return k;
  }
}
