/* GOSTO_VISUAL, a TV no jogo combinada com o lance do dono (a decisao E; docs/registro/2026-11.md, D-GV-TVJOGO-10 em diante): o gabarito das
   vidas da v30 (a v27 com o lance, o ovo de um pet) e da v31 (a v29 com ele, o grupo do brasao) da main, gravado com o codigo da main (o #872
   entrou antes da TV no jogo) ANTES da combinacao. Os saves v30 e v31 tem de abrir iguais depois, e a v35 e a v36 (as versoes combinadas), sem
   nenhum "st", tem de ser a v30 e a v31.
   De cada vida, o registro inteiro e, num replay incremental, o sha256 da assinatura a cada 25 eventos e no fim. Com GRAVAR_TV_JOGO_LANCE=1,
   grava test/gabaritos/tv_jogo_lance_etapa0_ts.json (so com o codigo da main); sem, confere que o replay de cada registro sai igual e que uma
   execucao nova do roteiro grava o mesmo registro. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { GrupoDoJogo, Motor, type EventoGrupoJogo, type EventoRegistro } from "../motor/index.ts";
import { ligarProduto } from "../src/produto.ts";

const ARQUIVO = new URL("./gabaritos/tv_jogo_lance_etapa0_ts.json", import.meta.url);
const PASSO = 25;
const sha = (s: string): string => createHash("sha256").update(s).digest("hex");

interface Ponto { evento: number; sha: string }
interface VidaPet { tipo: "pet"; nome: string; semente: number; versao: number; log: EventoRegistro[]; pontos: Ponto[]; assinatura: string }
interface VidaGrupo { tipo: "grupo"; nome: string; semente: number; versao: number; log: EventoGrupoJogo[]; assinatura: string }
interface Gabarito { vidas: (VidaPet | VidaGrupo)[] }

/** o dono: a racao a cada 3 h, o carinho a cada 5 h, a limpeza a cada 8 h e o Brincar (o lance, na v30 e na v31) a cada 2 h, acordado */
function cuidar(m: Motor, h: number): void {
  if (h % 3 === 0) m.observar("alimentar");
  if (h % 5 === 0 && !m.e.dormindo) m.observar("acariciar");
  if (h % 8 === 0) m.observar("limpar");
  if (h % 2 === 0 && !m.e.dormindo) m.observar("brincar");
}
function vidaPet(s: number, versao: number, horas: number): Motor {
  const m = ligarProduto(new Motor(s, versao));
  for (let h = 1; h <= horas; h++) { m.avancar(60); cuidar(m, h); }
  return m;
}
function vidaGrupo(s: number, versao: number, horas: number): GrupoDoJogo {
  const g = new GrupoDoJogo(s, versao);
  for (const i of g.ids) g.agir(i, m => ligarProduto(m));
  for (let h = 1; h <= horas; h++) { g.avancar(60); for (const i of g.ids) g.agir(i, m => cuidar(m, h)); }
  return g;
}

const ROTEIRO: { nome: string; fazer: () => Motor | GrupoDoJogo; semente: number; versao: number }[] = [
  { nome: "v30|101", semente: 101, versao: 30, fazer: () => vidaPet(101, 30, 36) },
  { nome: "v30|202", semente: 202, versao: 30, fazer: () => vidaPet(202, 30, 36) },
  { nome: "grupo31|101", semente: 101, versao: 31, fazer: () => vidaGrupo(101, 31, 24) },
  { nome: "grupo31|202", semente: 202, versao: 31, fazer: () => vidaGrupo(202, 31, 24) },
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

if (process.env.GRAVAR_TV_JOGO_LANCE === "1") writeFileSync(ARQUIVO, JSON.stringify(gravar()) + "\n", "utf8");
const G = JSON.parse(readFileSync(ARQUIVO, "utf8")) as Gabarito;

describe("a TV no jogo com o lance, etapa 0: os saves v30 e v31 de hoje abrem iguais", () => {
  test("o gabarito tem as quatro vidas, com o Brincar do dono", () => {
    expect(G.vidas.map(v => v.nome)).toEqual(ROTEIRO.map(r => r.nome));
    for (const v of G.vidas) expect(JSON.stringify(v.log)).toContain("brincar");
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
