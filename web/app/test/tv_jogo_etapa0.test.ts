/* GOSTO_VISUAL, a TV no jogo (as decisoes A a E da captura ligada ao cerebro; docs/registro/2026-11.md, D-GV-TVJOGO): o gabarito do lado
   TS do que a etapa toca, gravado com o codigo da main ANTES de qualquer mudanca. Os saves de hoje tem de abrir iguais depois:
     - a v32 (a TV no cerebro), com o "st" das duas fontes, o pet levado ate a TV e o cerebro A numa das vidas;
     - a v27 (o ovo de um pet so de antes da TV);
     - o grupo v29 (o ovo do brasao), com o cuidado do dono nos dois pets.
   De cada vida, o registro inteiro e, num replay incremental, o sha256 da assinatura a cada 25 eventos e no fim. Com GRAVAR_TV_JOGO=1, grava
   test/gabaritos/tv_jogo_etapa0_ts.json (so com o codigo de antes); sem, confere que o replay de cada registro sai igual e que uma execucao
   nova do roteiro grava o mesmo registro. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { CELULA_PERTO_DA_TV_JOGO, GrupoDoJogo, Motor, ResumoTela, centroDaCelula, type EventoGrupoJogo, type EventoRegistro } from "../motor/index.ts";
import { CMU_GRANDE } from "../motor/constantes.ts";
import { ligarProduto } from "../src/produto.ts";

const ARQUIVO = new URL("./gabaritos/tv_jogo_etapa0_ts.json", import.meta.url);
const PASSO = 25;
const sha = (s: string): string => createHash("sha256").update(s).digest("hex");

interface Ponto { evento: number; sha: string }
interface VidaPet { tipo: "pet"; nome: string; semente: number; versao: number; log: EventoRegistro[]; pontos: Ponto[]; assinatura: string }
interface VidaGrupo { tipo: "grupo"; nome: string; semente: number; versao: number; log: EventoGrupoJogo[]; assinatura: string }
interface Gabarito { vidas: (VidaPet | VidaGrupo)[] }

/** o dono de um pet so (o do gosto_visual_cerebro.test.ts): a racao a cada 3 h, o carinho a cada 5 h e a limpeza a cada 8 h */
function cuidar(m: Motor, horas: number, cada?: (m: Motor, h: number) => void): void {
  for (let h = 1; h <= horas; h++) {
    m.avancar(60);
    if (h % 3 === 0) m.observar("alimentar");
    if (h % 5 === 0 && !m.e.dormindo) m.observar("acariciar");
    if (h % 8 === 0) m.observar("limpar");
    cada?.(m, h);
  }
}
const amostra = (h: number, s: number): number[] => [0, 1, 2, 3, 4, 5, 6].map(k => ((h * 7 + k * 3 + (s % 5)) % 11) / 10);

/** a v32 com a TV: o pet levado ate a TV a cada 2 h, um vetor por "segundo" (20 por hora), a fonte trocando no meio; `a`: o cerebro A */
function vidaV32(s: number, horas: number, a: boolean): Motor {
  const m = ligarProduto(new Motor(s, 32));
  if (a) m.trocarCerebro("a");
  let r = new ResumoTela("tela");
  const [x, y] = centroDaCelula(CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE);
  cuidar(m, horas, (mm, h) => {
    if (h === Math.floor(horas / 2)) r = new ResumoTela("tv");
    if (h % 2 === 0 && !mm.e.dormindo) mm.levarPet(x, y);
    for (let k = 0; k < 20; k++) { const v = r.amostra(amostra(Math.floor(h / 3), s + k)); if (v !== null) mm.sentidoTela(v); }
  });
  return m;
}
function vidaV27(s: number, horas: number): Motor { const m = ligarProduto(new Motor(s, 27)); cuidar(m, horas); return m; }
function vidaGrupo(s: number, horas: number): GrupoDoJogo {
  const g = new GrupoDoJogo(s, 29);
  for (const i of g.ids) g.agir(i, m => ligarProduto(m));
  for (let h = 1; h <= horas; h++) {
    g.avancar(60);
    for (const i of g.ids) g.agir(i, m => {
      if (h % 3 === 0) m.observar("alimentar");
      if (h % 5 === 0 && !m.e.dormindo) m.observar("acariciar");
      if (h % 8 === 0) m.observar("limpar");
    });
  }
  return g;
}

const ROTEIRO: { nome: string; fazer: () => Motor | GrupoDoJogo; semente: number; versao: number }[] = [
  { nome: "v32|101", semente: 101, versao: 32, fazer: () => vidaV32(101, 36, false) },
  { nome: "v32|202", semente: 202, versao: 32, fazer: () => vidaV32(202, 36, false) },
  { nome: "v32|A|303", semente: 303, versao: 32, fazer: () => vidaV32(303, 24, true) },
  { nome: "v27|404", semente: 404, versao: 27, fazer: () => vidaV27(404, 36) },
  { nome: "grupo29|101", semente: 101, versao: 29, fazer: () => vidaGrupo(101, 24) },
];

function pontos(semente: number, versao: number, log: readonly EventoRegistro[]): Ponto[] {
  const m = new Motor(semente, versao), pts: Ponto[] = [];
  log.forEach((ev, i) => { m.aplicarEvento(JSON.parse(JSON.stringify(ev)) as EventoRegistro); if ((i + 1) % PASSO === 0) pts.push({ evento: i + 1, sha: sha(m.assinatura()) }); });
  return pts;
}

function gravar(): Gabarito {
  return {
    vidas: ROTEIRO.map(({ nome, semente, versao, fazer }) => {
      const x = fazer();
      if (x instanceof GrupoDoJogo) return { tipo: "grupo", nome, semente, versao, log: JSON.parse(JSON.stringify(x.log)), assinatura: sha(x.assinatura()) };
      const log = JSON.parse(JSON.stringify(x.log)) as EventoRegistro[];
      return { tipo: "pet", nome, semente, versao, log, pontos: pontos(semente, versao, log), assinatura: sha(x.assinatura()) };
    }),
  };
}

if (process.env.GRAVAR_TV_JOGO === "1") writeFileSync(ARQUIVO, JSON.stringify(gravar()) + "\n", "utf8");
const G = JSON.parse(readFileSync(ARQUIVO, "utf8")) as Gabarito;

describe("a TV no jogo, etapa 0: os saves de hoje (v32, v27 e o grupo v29) abrem iguais", () => {
  test("o gabarito tem as cinco vidas, e a v32 tem o \"st\" e o levar o pet", () => {
    expect(G.vidas.map(v => v.nome)).toEqual(ROTEIRO.map(r => r.nome));
    for (const v of G.vidas.filter(v => v.versao === 32)) {
      expect((v.log as EventoRegistro[]).some(e => e[1] === "st")).toBe(true);
      expect((v.log as EventoRegistro[]).some(e => e[1] === "lp")).toBe(true);
    }
  });
  for (const v of G.vidas) {
    test(`${v.nome}: o replay do registro gravado da a mesma assinatura (e os pontos do caminho)`, () => {
      if (v.tipo === "grupo") {
        expect(sha(GrupoDoJogo.reproduzir(v.semente, v.versao, v.log).assinatura())).toBe(v.assinatura);
      } else {
        expect(pontos(v.semente, v.versao, v.log)).toEqual(v.pontos);
        expect(sha(Motor.reproduzir(v.semente, JSON.parse(JSON.stringify(v.log)) as EventoRegistro[], v.versao).assinatura())).toBe(v.assinatura);
      }
    });
    test(`${v.nome}: uma execucao nova do roteiro grava o mesmo registro`, () => {
      const x = ROTEIRO.find(r => r.nome === v.nome)!.fazer();
      expect(JSON.parse(JSON.stringify(x.log))).toEqual(v.log);
      expect(sha(x.assinatura())).toBe(v.assinatura);
    });
  }
});
