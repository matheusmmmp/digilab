/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.3): os candidatos da rodada, so na bancada. Um candidato e o CANDIDATO_V21 com
   alguns numeros trocados (candidatoDe); um nome desconhecido, uma chave que o candidato nao tem ou um numero que nao e positivo falham alto.
   Os candidatos com nome ficam no CANDIDATOS; os da grade (grade.ts) vem de um JSON e so rodam com --grade. Os numeros novos sao
   PROPOSTOS, SEM FONTE, ate o Matheus decidir. */
import { readFileSync } from "node:fs";
import { CANDIDATO_V21, type Candidato } from "./comum.ts";

/** as trocas de um candidato: cada chave do Candidato, com as sub-chaves que mudam */
export type Troca = { nome: string } & { [K in Exclude<keyof Candidato, "nome">]?: Partial<Candidato[K]> | number };
export function candidatoDe(t: Troca): Candidato {
  if (!/^[a-z0-9_]+$/.test(t.nome) || t.nome === CANDIDATO_V21.nome) throw new Error(`candidato: nome invalido ${JSON.stringify(t.nome)}`);
  const base = JSON.parse(JSON.stringify(CANDIDATO_V21)) as Candidato, out = base as unknown as Record<string, unknown>;
  for (const [k, v] of Object.entries(t)) {
    if (k === "nome") continue;
    if (!(k in base)) throw new Error(`candidato ${t.nome}: a chave ${k} nao existe`);
    const atual = out[k];
    if (typeof atual === "number") {
      if (typeof v !== "number" || !(v > 0)) throw new Error(`candidato ${t.nome}: ${k} precisa ser um numero positivo`);
      out[k] = v;
      continue;
    }
    if (typeof v !== "object" || v === null) throw new Error(`candidato ${t.nome}: ${k} precisa ser um objeto`);
    const alvo = atual as Record<string, number>;
    for (const [s, x] of Object.entries(v)) {
      if (!(s in alvo)) throw new Error(`candidato ${t.nome}: ${k}.${s} nao existe`);
      /* o treino dos rivais pode ser 0; o resto e positivo */
      if (typeof x !== "number" || !Number.isFinite(x) || x < 0 || (x === 0 && k !== "treinoRival")) throw new Error(`candidato ${t.nome}: ${k}.${s} invalido (${x})`);
      alvo[s] = x;
    }
  }
  out.nome = t.nome;
  return Object.freeze(base);
}

/** os candidatos com nome (os que entram nas medidas inteiras e no relato) */
export const CANDIDATOS: Readonly<Record<string, Candidato>> = { v21: CANDIDATO_V21 };
/** o candidato da linha de comando: --candidato <nome>, ou --candidato-json <arquivo> (so a grade) */
export function candidatoDaLinha(nome: string, json: string, grade: boolean): Candidato {
  if (json) {
    if (!grade) throw new Error("candidato: o --candidato-json so roda na grade (--grade)");
    return candidatoDe(JSON.parse(readFileSync(json, "utf-8")) as Troca);
  }
  const c = CANDIDATOS[nome];
  if (!c) throw new Error(`candidato desconhecido ${nome} (${Object.keys(CANDIDATOS).join(", ")})`);
  return c;
}
