/* COOPERACAO, CO1 (docs/TAREFA_V3_COOPERACAO.md, secoes 3 e 4): o gabarito do lado TS do que a frente vai tocar, gravado com o codigo da
   main ANTES de qualquer mudanca. O G-HOJE do TS:
     - os gabaritos do Python que o mundo e o grupo leem ficam com o sha256 de hoje (o grupo_python.json.gz e o da CO1, que a CO2
       reproduz; o mundo_python.json e o mvp_mundo_python.json sao os do mundo de um pet, que a CO2 vai tornar partilhado);
     - tres vidas do pet da versao de hoje (VERSAO_PET), como o jogo as roda, com um dono de roteiro fixo: o log inteiro, a assinatura a
       cada 25 eventos de um replay incremental e no fim, e a impressao do mundo. Com a ConfigCooperacao desligada (CO3) e o save de
       hoje (CO4), estas vidas tem de sair byte a byte.
   Com GRAVAR_COOP=1, grava test/gabaritos/coop_etapa0_ts.json (so com o codigo de antes); sem, confere. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { CMU_MVP, TPD } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";

const ARQUIVO = new URL("./gabaritos/coop_etapa0_ts.json", import.meta.url);
const PINADOS = ["./gabaritos/grupo_python.json.gz", "./gabaritos/mundo_python.json", "./gabaritos/mvp_mundo_python.json"];
const PASSO_CHECKPOINT = 25;
/* (semente, dias) */
const VIDAS: [number, number][] = [[101, 3], [202, 3], [303, 2]];

type Evento = Motor["log"][number];
interface Ponto { evento: number; tick: number; sha: string; estagio: string }
interface VidaGravada { semente: number; versao: number; dias: number; log: Evento[]; pontos: Ponto[]; assinatura: string; impressao: string }
interface Gabarito { versao_pet: number; arquivos: Record<string, string>; vidas: VidaGravada[] }

const sha = (s: string): string => createHash("sha256").update(s).digest("hex");
const shaArquivo = (rel: string): string => createHash("sha256").update(readFileSync(new URL(rel, import.meta.url))).digest("hex");
const W = CMU_MVP.celulas_x * CMU_MVP.sub;
const preso = (v: number, max: number) => Math.max(0, Math.min(max - 1, v));

/** o dono do jogo de roteiro fixo (so le o motor): o botao Alimentar e a racao perto, alternados, o limpar, o brincar e o carinho */
function viverDias(m: Motor, dias: number): void {
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e, [px, py] = m.mundo!.pet;
    if (e.fome < .6 && p % 2 === 0) {
      if ((p >> 1) % 2 === 0) m.observar("alimentar");
      else m.deixarComida("racao", preso(px + 2 * CMU_MVP.sub, W), py);
    }
    if (e.sujeira >= 2) m.observar("limpar");
    if (e.humor < .5 && !e.dormindo) m.observar("brincar");
    if (p % 5 === 0) m.observar("acariciar");
  }
}

const ponto = (m: Motor, i: number): Ponto => ({ evento: i, tick: m.e.tick, sha: sha(m.assinatura()), estagio: m.estagioAtual });

/** o replay incremental do log, com os pontos fixos (so depende do log) */
function refazer(semente: number, versao: number, log: Evento[]): { m: Motor; pts: Ponto[] } {
  const m = new Motor(semente, versao), pts = [ponto(m, 0)];
  log.forEach((ev, i) => {
    m.aplicarEvento(ev);
    const n = i + 1;
    if (n % PASSO_CHECKPOINT === 0 || n === log.length) pts.push(ponto(m, n));
  });
  return { m, pts };
}

const impressao = (m: Motor): string => sha(JSON.stringify(m.mundo!.resumo()));

function gerar(): Gabarito {
  const vidas = VIDAS.map(([semente, dias]): VidaGravada => {
    /* as vidas gravadas sao v21, a versao do dia da CO1; desde a v22 (ILHA_AGUA, IA4) a versao e pedida de forma explicita */
    const m = new Motor(semente, 21);
    viverDias(m, dias);
    const log = JSON.parse(JSON.stringify(m.log)) as Evento[];
    const { pts } = refazer(semente, m.versao, log);
    return { semente, versao: m.versao, dias, log, pontos: pts, assinatura: sha(m.assinatura()), impressao: impressao(m) };
  });
  return { versao_pet: 21, arquivos: Object.fromEntries(PINADOS.map(p => [p, shaArquivo(p)])), vidas };
}

if (process.env.GRAVAR_COOP === "1") writeFileSync(ARQUIVO, JSON.stringify(gerar(), null, 1) + "\n", "utf8");

const G = JSON.parse(readFileSync(ARQUIVO, "utf8")) as Gabarito;

describe("COOPERACAO, CO1: o G-HOJE do lado TS", () => {
  test("o gabarito e o de hoje: a versao do pet, as vidas e os arquivos pinados", () => {
    expect(G.versao_pet).toBe(21);
    expect(G.vidas.map(v => [v.semente, v.versao, v.dias])).toEqual(VIDAS.map(([s, d]) => [s, 21, d]));
    expect(Object.keys(G.arquivos)).toEqual(PINADOS);
    for (const v of G.vidas) expect(v.log.length >= 50 && v.pontos.length >= 3, `${v.semente}`).toBe(true);
  });
  test("os gabaritos do Python do mundo e do grupo continuam os de hoje", () => {
    for (const p of PINADOS) expect(shaArquivo(p), p).toBe(G.arquivos[p]);
  });
  for (const v of G.vidas) {
    test(`a vida ${v.semente} (${v.dias} dias): o replay do log da os mesmos pontos, a mesma assinatura e o mesmo mundo`, () => {
      const { m, pts } = refazer(v.semente, v.versao, v.log);
      expect(pts).toEqual(v.pontos);
      expect(sha(m.assinatura())).toBe(v.assinatura);
      expect(impressao(m)).toBe(v.impressao);
    });
    test(`a vida ${v.semente}: o mesmo dono de roteiro refaz o mesmo log`, () => {
      const m = new Motor(v.semente, v.versao);
      viverDias(m, v.dias);
      expect(JSON.parse(JSON.stringify(m.log))).toEqual(v.log);
    });
  }
});
