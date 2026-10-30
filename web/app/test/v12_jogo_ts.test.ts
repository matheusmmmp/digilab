/* O gabarito das vidas v12 do jogo em TS (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, etapa 1b; o T-PONTO-4, parte 1, da
   docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 15; decisao do Matheus de 2026-10-25): as vidas do pet v12 como o jogo as roda hoje (o Motor, o
   laco com o mundo do produto, CMU_MVP, e o cerebro A do v11), gravadas com o codigo da main ANTES de qualquer mudanca no espelho TS. E o
   G2 do TS para o `ponto` da v13: com a chave desligada, estas vidas tem de sair byte a byte.

   Em cada vida: o log inteiro; num replay incremental do log, a assinatura (sha256) a cada 25 eventos e no fim; e, em cada sub-decisao do
   mundo (explorar, comer, brincar), os candidatos que o motor ofereceu e o alvo escolhido, nos moldes de
   test/gabaritos/mvp_produto_python.json e de tests/gabaritos/digibrain_vidas_de_hoje.json (o sha256 da lista, as contagens por acao e
   por tipo de candidato no explorar). No fim, a impressao do mundo (o resumo inteiro, com o registro de cada decisao e a regra dela) e o
   estado interno do cerebro A.

   Os donos sao os do jogo com o mundo: o botao Alimentar (a racao no comedouro), a racao posta perto do pet, a racao posta nos tres
   lugares nomeados da tela (o comedouro, perto, longe) e um roteiro com o tapa, o treino, a medalha e as lutas.
   Com GRAVAR_V12=1, grava test/gabaritos/v12_jogo_ts.json (so com o codigo de antes); sem, confere. */
import { describe, expect, test } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { CMU_MVP, TPD, VERSAO_PET } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import type { AcaoDono } from "../motor/tipos.ts";

const ARQUIVO = new URL("./gabaritos/v12_jogo_ts.json", import.meta.url);
const PINADOS = ["./gabaritos/mvp_produto_python.json", "./gabaritos/mvp_mundo_python.json", "./gabaritos/mvp_etapa0_ts.json"];
const PASSO_CHECKPOINT = 25;
type Dono = "botao" | "perto" | "lugares" | "roteiro";
/* (semente, dias, o dono) */
const VIDAS: [number, number, Dono][] = [[101, 4, "botao"], [202, 4, "perto"], [303, 4, "lugares"], [404, 4, "roteiro"], [505, 3, "botao"]];

type Evento = Motor["log"][number];
interface Ponto { evento: number; tick: number; sha: string; nDecisoes: number; estagio: string }
interface Escolha { tick: number; acao: string; candidatos: unknown[]; alvo: unknown }
interface VidaGravada {
  semente: number; versao: number; dias: number; dono: Dono; log: Evento[]; pontos: Ponto[]; assinatura: string;
  candidatos: string; n: Record<string, number>; tipos_explorar: Record<string, number>; consumos: number; impressao: string;
  cerebro: string;
}
interface Gabarito { versao_pet: number; arquivos: Record<string, string>; vidas: VidaGravada[] }

const sha = (s: string): string => createHash("sha256").update(s).digest("hex");
const shaArquivo = (rel: string): string => createHash("sha256").update(readFileSync(new URL(rel, import.meta.url))).digest("hex");
const W = CMU_MVP.celulas_x * CMU_MVP.sub, H = CMU_MVP.celulas_y * CMU_MVP.sub;
const preso = (v: number, max: number) => Math.max(0, Math.min(max - 1, v));

/** o dono do jogo com o mundo, de roteiro fixo (so le o motor) */
function viverDias(m: Motor, dias: number, dono: Dono): void {
  const passos = Math.round(dias * TPD / 30);
  for (let p = 0; p < passos; p++) {
    m.avancar(30);
    const e = m.e, mu = m.mundo!, [px, py] = mu.pet;
    if (e.fome < .6 && p % 2 === 0) {
      if (dono === "botao" || dono === "roteiro") m.observar("alimentar");
      else if (dono === "perto") m.deixarComida("racao", preso(px + 2 * CMU_MVP.sub, W), py);
      else {
        const k = (p >> 1) % 3;
        if (k === 0) m.observar("alimentar");
        else if (k === 1) m.deixarComida("racao", preso(px + 2 * CMU_MVP.sub, W), preso(py + CMU_MVP.sub, H));
        else m.deixarComida("racao", preso(px < W / 2 ? px + 20 * CMU_MVP.sub : px - 20 * CMU_MVP.sub, W), py);
      }
    }
    if (e.sujeira >= 2) m.observar("limpar");
    if (e.humor < .5 && !e.dormindo) m.observar("brincar");
    if (p % 5 === 0) m.observar("acariciar");
    if (dono !== "roteiro") continue;
    if (p % 8 === 7) m.observar("tapa" as AcaoDono);
    if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    if (m.estagioAtual === "crianca" && m.medalhas === 0) m.liberar(1);
    if ((m.estagioAtual === "crianca" || m.estagioAtual === "adolescente") && m.treino.podeTocar(m.e.tick) && p % 3 === 0) m.treinar("levantar_pedra");
    if (m.estagioAtual === "adolescente" && p % 6 === 0) m.lutar("aleatorio", 1000 + p);
  }
}

/** grava, em cada sub-decisao do mundo, os candidatos e o alvo (so le: embrulha o metodo desta instancia do Mundo, sem mudar a conta) */
function escutarEscolhas(m: Motor): Escolha[] {
  const mu = m.mundo!, original = mu.consequencia.bind(mu), escolhas: Escolha[] = [];
  mu.consequencia = (tick, acao, estado, escolher, regra) => {
    const r = original(tick, acao, estado, escolher, regra);
    if (mu.ultimosCandidatos !== null)
      escolhas.push(JSON.parse(JSON.stringify({ tick, acao, candidatos: mu.ultimosCandidatos, alvo: r.ocorrido!.alvo })) as Escolha);
    return r;
  };
  return escolhas;
}

const ponto = (m: Motor, i: number): Ponto => ({ evento: i, tick: m.e.tick, sha: sha(m.assinatura()), nDecisoes: m.nDecisoes, estagio: m.estagioAtual });

/** o que sai das escolhas: o sha256 da lista, as contagens por acao e por tipo de candidato no explorar */
function resumoEscolhas(es: Escolha[]): Pick<VidaGravada, "candidatos" | "n" | "tipos_explorar"> {
  const n: Record<string, number> = {}, tipos: Record<string, number> = {};
  for (const e of es) {
    n[e.acao] = (n[e.acao] ?? 0) + 1;
    if (e.acao === "explorar") for (const c of e.candidatos as { tipo: string }[]) tipos[c.tipo] = (tipos[c.tipo] ?? 0) + 1;
  }
  const ordenado = (o: Record<string, number>) => Object.fromEntries(Object.keys(o).sort().map(k => [k, o[k]]));
  return { candidatos: sha(JSON.stringify(es)), n: ordenado(n), tipos_explorar: ordenado(tipos) };
}

/** o replay incremental do log, com os pontos fixos e as escolhas (so depende do log) */
function refazer(semente: number, versao: number, log: Evento[]): { m: Motor; pts: Ponto[]; escolhas: Escolha[] } {
  const m = new Motor(semente, versao), escolhas = escutarEscolhas(m), pts = [ponto(m, 0)];
  log.forEach((ev, i) => {
    m.aplicarEvento(ev);
    const n = i + 1;
    if (n % PASSO_CHECKPOINT === 0 || n === log.length) pts.push(ponto(m, n));
  });
  return { m, pts, escolhas };
}

const impressao = (m: Motor): string => sha(JSON.stringify(m.mundo!.resumo()));
const cerebro = (m: Motor): string => sha(JSON.stringify(m.cerebro!.estadoInterno()));

function gerar(): Gabarito {
  const vidas = VIDAS.map(([semente, dias, dono]): VidaGravada => {
    const m = new Motor(semente), escolhas = escutarEscolhas(m);
    viverDias(m, dias, dono);
    const log = JSON.parse(JSON.stringify(m.log)) as Evento[];
    const { pts } = refazer(semente, m.versao, log);
    return { semente, versao: m.versao, dias, dono, log, pontos: pts, assinatura: sha(m.assinatura()), ...resumoEscolhas(escolhas),
             consumos: m.mundo!.consumos.length, impressao: impressao(m), cerebro: cerebro(m) };
  });
  return { versao_pet: VERSAO_PET, arquivos: Object.fromEntries(PINADOS.map(p => [p, shaArquivo(p)])), vidas };
}

if (process.env.GRAVAR_V12 === "1") writeFileSync(ARQUIVO, JSON.stringify(gerar(), null, 1) + "\n", "utf8");

const G = JSON.parse(readFileSync(ARQUIVO, "utf8")) as Gabarito;

describe("o gabarito das vidas v12 do jogo em TS (T-PONTO-4, parte 1)", () => {
  test("o gabarito e o do v12 de hoje: cinco vidas, os donos, os eventos, as tres sub-decisoes e os arquivos pinados", () => {
    expect(G.versao_pet).toBe(12);
    expect(G.vidas.map(v => [v.semente, v.versao, v.dias, v.dono])).toEqual(VIDAS.map(([s, d, o]) => [s, 12, d, o]));
    const tipos = (v: VidaGravada) => [...new Set(v.log.map(e => e[1]))].sort();
    for (const v of G.vidas) {
      expect(tipos(v), `${v.semente}`).toEqual(expect.arrayContaining(["d", "dc", "t"]));
      expect(v.log.length >= 90 && v.pontos.length >= 4, `${v.semente}`).toBe(true);
      expect(Object.keys(v.n).sort(), `${v.semente}`).toEqual(["brincar", "comer", "explorar"]);
    }
    /* o roteiro tem o treino, as lutas e a medalha */
    expect(tipos(G.vidas[3])).toEqual(expect.arrayContaining(["l", "tr", "u"]));
    /* o explorar de hoje: so os candidatos do motor (sem `ponto`, sem `lembranca`) */
    for (const v of G.vidas) for (const t of Object.keys(v.tipos_explorar)) expect(["casa", "cheiro", "continuar", "vagar"]).toContain(t);
    expect(Object.keys(G.arquivos)).toEqual(PINADOS);
  });

  test("os gabaritos do MVP que o G-PAR e o G2 do v11 leem continuam os de hoje", () => {
    for (const p of PINADOS) expect(shaArquivo(p), p).toBe(G.arquivos[p]);
  });

  /* os pets v12 nao abrem mais (o descarte 6, COMBATE-TR, etapa R2b): as vidas do gabarito se refazem no v13, que e o v12 com a luta em
     tempo real, e saem iguais, bit a bit. A vida do roteiro, que luta, muda com a luta nova e sai daqui (o gabarito das vidas v13,
     test/vidas_v13.test.ts, confere as vidas com luta) */
  for (const v of G.vidas.filter(x => !x.log.some(e => e[1] === "l"))) {
    test(`v12 @${v.semente} (${v.dono}, ${v.dias} dias), refeita no v13: o replay do log, ponto a ponto, os candidatos, o mundo e o cerebro no fim`, () => {
      const { m, pts, escolhas } = refazer(v.semente, VERSAO_PET, v.log);
      expect(pts.length).toBe(v.pontos.length);
      pts.forEach((p, i) => expect(p, `ponto no evento ${v.pontos[i].evento}`).toEqual(v.pontos[i]));
      expect(resumoEscolhas(escolhas)).toEqual({ candidatos: v.candidatos, n: v.n, tipos_explorar: v.tipos_explorar });
      expect(m.mundo!.consumos.length).toBe(v.consumos);
      expect(impressao(m)).toBe(v.impressao);
      expect(sha(m.assinatura())).toBe(v.assinatura);
      expect(cerebro(m)).toBe(v.cerebro);
      /* e pelo caminho publico */
      expect(sha(Motor.reproduzir(v.semente, v.log, VERSAO_PET).assinatura())).toBe(v.assinatura);
    });
  }

  test("o mesmo dono, jogado de novo hoje, da o mesmo log (o dono e o motor deterministas)", () => {
    for (const k of [0, 2]) {
      const [semente, dias, dono] = VIDAS[k];
      const m = new Motor(semente);
      viverDias(m, dias, dono);
      expect(JSON.parse(JSON.stringify(m.log))).toEqual(G.vidas[k].log);
    }
  });
});
