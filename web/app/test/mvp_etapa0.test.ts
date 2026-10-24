/* MVP, etapa 0 (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, secao 4): o gabarito do lado TS do que o MVP vai tocar, gravado com o codigo da main
   ANTES de qualquer mudanca. O G2 do MVP no TS:
     - as vidas do jogo: tres pets v11 de hoje, com um dono de roteiro fixo (o do pet_v11.test.ts: cuidado, carinho, tapa, treino,
       medalha e lutas), gravados com o log inteiro e, num replay incremental do log, a assinatura (sha256) a cada 25 eventos e no fim,
       com o estado interno do cerebro A no fim. Com a versao nova do MVP, um v11 rejogado destes logs tem de sair igual;
     - as vidas do lobos_v11.test.ts e as do laco: os gabaritos do Python que o G-PAR do v11, do mundo, do contrato e do MVP leem ficam
       com o sha256 de hoje (com eles fixos e esses testes passando, o lobos.ts, o corpo do v11 e o mundo.ts saem iguais).
   Com GRAVAR_MVP=1, grava test/gabaritos/mvp_etapa0_ts.json (so com o codigo de antes); sem, confere. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { TPD, VERSAO_PET } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import type { AcaoDono } from "../motor/tipos.ts";

const ARQUIVO = new URL("./gabaritos/mvp_etapa0_ts.json", import.meta.url);
const PINADOS = ["./gabaritos/lobos_python.json", "./gabaritos/lobos_laco_python.json", "./gabaritos/carater_v11_python.json",
  "./gabaritos/painel_digibrain_python.json", "./gabaritos/mapa_digibrain_python.json", "./gabaritos/mundo_python.json",
  "./gabaritos/contrato_python.json", "./gabaritos/mvp_mundo_python.json"];
const PASSO_CHECKPOINT = 25;
/* (semente, dias, o dono): o roteiro do pet_v11.test.ts e um mais calmo (sem tapa, sem luta) */
const VIDAS: [number, number, "roteiro" | "calmo"][] = [[101, 4, "roteiro"], [202, 3, "calmo"], [303, 4, "roteiro"]];

type Evento = Motor["log"][number];
interface Ponto { evento: number; tick: number; sha: string; nDecisoes: number; estagio: string }
interface VidaGravada {
  semente: number; versao: number; dias: number; dono: string; log: Evento[]; pontos: Ponto[]; assinatura: string; cerebro: string;
}
interface Gabarito { versao_pet: number; arquivos: Record<string, string>; vidas: VidaGravada[] }

const sha = (s: string): string => createHash("sha256").update(s).digest("hex");
const shaArquivo = (rel: string): string => createHash("sha256").update(readFileSync(new URL(rel, import.meta.url))).digest("hex");

/** o dono de roteiro do pet_v11.test.ts (o "calmo" so cuida e faz carinho) */
function viverDias(m: Motor, dias: number, dono: "roteiro" | "calmo"): void {
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e;
    if (e.fome < .5) m.observar("alimentar");
    if (e.sujeira >= 2) m.observar("limpar");
    if (e.humor < .5 && !e.dormindo) m.observar("brincar");
    if (p % 5 === 0) m.observar("acariciar");
    if (dono === "calmo") continue;
    if (p % 8 === 7) m.observar("tapa" as AcaoDono);
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    if (m.estagioAtual === "crianca" && m.medalhas === 0) m.liberar(1);
    if ((m.estagioAtual === "crianca" || m.estagioAtual === "adolescente") && m.treino.podeTocar(m.e.tick) && p % 3 === 0) m.treinar("levantar_pedra");
    if (m.estagioAtual === "adolescente" && p % 6 === 0) m.lutar("aleatorio", 1000 + p);
  }
}

const ponto = (m: Motor, i: number): Ponto => ({ evento: i, tick: m.e.tick, sha: sha(m.assinatura()), nDecisoes: m.nDecisoes, estagio: m.estagioAtual });

/** o replay incremental do log, com os pontos fixos (so depende do log) */
function pontos(semente: number, versao: number, log: Evento[]): { m: Motor; pts: Ponto[] } {
  const m = new Motor(semente, versao), pts = [ponto(m, 0)];
  log.forEach((ev, i) => {
    m.aplicarEvento(ev);
    const n = i + 1;
    if (n % PASSO_CHECKPOINT === 0 || n === log.length) pts.push(ponto(m, n));
  });
  return { m, pts };
}

function gerar(): Gabarito {
  const vidas = VIDAS.map(([semente, dias, dono]) => {
    const m = new Motor(semente);
    viverDias(m, dias, dono);
    const log = JSON.parse(JSON.stringify(m.log)) as Evento[];
    const { pts } = pontos(semente, m.versao, log);
    return { semente, versao: m.versao, dias, dono, log, pontos: pts, assinatura: sha(m.assinatura()),
             cerebro: sha(JSON.stringify(m.cerebro!.estadoInterno())) };
  });
  return { versao_pet: VERSAO_PET, arquivos: Object.fromEntries(PINADOS.map(p => [p, shaArquivo(p)])), vidas };
}

if (process.env.GRAVAR_MVP === "1") writeFileSync(ARQUIVO, JSON.stringify(gerar(), null, 1) + "\n", "utf8");

const G = JSON.parse(readFileSync(ARQUIVO, "utf8")) as Gabarito;

describe("G2 do MVP (etapa 0): o lado TS de hoje", () => {
  test("o gabarito e o do v11 de hoje: tres vidas, as versoes, os eventos e os arquivos pinados", () => {
    expect(G.versao_pet).toBe(11);
    expect(G.vidas.map(v => [v.semente, v.versao, v.dias, v.dono])).toEqual(VIDAS.map(([s, d, o]) => [s, 11, d, o]));
    /* o log junta os avancos seguidos: o roteiro tem o cuidado, o treino, as lutas e a medalha; o calmo, so o cuidado e o carinho */
    const tipos = (v: VidaGravada) => [...new Set(v.log.map(e => e[1]))].sort();
    expect(G.vidas.map(tipos)).toEqual([["d", "l", "t", "tr", "u"], ["d", "t"], ["d", "l", "t", "tr", "u"]]);
    expect(G.vidas.every(v => v.log.length >= 90 && v.pontos.length >= 4)).toBe(true);
    expect(Object.keys(G.arquivos)).toEqual(PINADOS);
  });

  test("os gabaritos do Python que o G-PAR do v11, do mundo, do contrato e do MVP leem continuam os de hoje", () => {
    for (const p of PINADOS) expect(shaArquivo(p), p).toBe(G.arquivos[p]);
  });

  for (const v of G.vidas) {
    test(`v11 @${v.semente} (${v.dono}, ${v.dias} dias): o replay do log, ponto a ponto, a assinatura e o cerebro no fim`, () => {
      const { m, pts } = pontos(v.semente, v.versao, v.log);
      expect(pts.length).toBe(v.pontos.length);
      pts.forEach((p, i) => expect(p, `ponto no evento ${v.pontos[i].evento}`).toEqual(v.pontos[i]));
      expect(sha(m.assinatura())).toBe(v.assinatura);
      expect(sha(JSON.stringify(m.cerebro!.estadoInterno()))).toBe(v.cerebro);
      /* e pelo caminho publico */
      expect(sha(Motor.reproduzir(v.semente, v.log, v.versao).assinatura())).toBe(v.assinatura);
    });
  }

  test("o mesmo roteiro, jogado de novo hoje, da o mesmo log (o dono e o motor deterministas)", () => {
    const [semente, dias, dono] = VIDAS[0];
    const m = new Motor(semente);
    viverDias(m, dias, dono);
    expect(JSON.parse(JSON.stringify(m.log))).toEqual(G.vidas[0].log);
  });
});
