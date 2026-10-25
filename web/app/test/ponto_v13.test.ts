/* O `ponto` no espelho TS, atras da chave da v13 (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, etapa 1b; o T-PONTO-4, parte 2, da
   docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.1, 11 e 15; a PE-14 revista). O Mundo do TS ja validava o `ponto` como o Python
   (mundo.ts, `validarAlvo`; digilab/mundo.py:1415-1422), mas o laco do jogo nunca perguntava o alvo ao cerebro. Agora:
     - com a chave desligada (o v12 e o A), o laco nao pergunta: um `escolherAlvo` na politica nunca e chamado, e a vida sai igual a de
       hoje (o gabarito das vidas v12, test/v12_jogo_ts.test.ts, gravado antes desta mudanca, confere o jogo);
     - com a chave ligada, o laco pergunta, e o Mundo aceita o `ponto` so no explorar, com coordenadas inteiras dentro do mapa; fora do
       mapa ou nao inteiro, `raise`; no comer e no brincar, e para qualquer alvo fora dos candidatos, `raise` (a validacao dos demais
       alvos nao relaxa);
     - o explorar do motor nao ganha candidato novo. */
import { describe, expect, test } from "vitest";
import { CMU_MVP, TICK_INICIAL } from "../motor/constantes.ts";
import { CCO_CORPO_V11 } from "../motor/corpo.ts";
import { MotorCorpoMundo } from "../motor/motor_corpo_mundo.ts";
import { estadoNascimentoPy, type PoliticaCorpo } from "../motor/motor_corpo.ts";
import { alvo, alvoPonto, type EscolherAlvo } from "../motor/mundo.ts";
import { bracoV11 } from "../motor/pet_v11.ts";

const W = CMU_MVP.celulas_x * CMU_MVP.sub, H = CMU_MVP.celulas_y * CMU_MVP.sub;
const PASSOS = 40;                                         // 40 x 30 ticks: dezenas de sub-decisoes nas tres acoes

/** o laco do pet v12 (o do Motor do jogo), com o A do v11 e, se vier, um `escolherAlvo` na politica */
function laco(escolher: EscolherAlvo | undefined, digibrain: boolean | undefined): MotorCorpoMundo {
  const braco = bracoV11();
  const politica: PoliticaCorpo = {
    agir: (o, rng) => braco.agir(o, rng), observar: (t) => braco.observar(t),
    consequenciaCorpo: (a, oc, d) => braco.consequenciaCorpo(a, oc, d), receberAcaoDono: (a, t) => braco.receberAcaoDono(a, t),
    mudancaNoCorpo: (a, d) => braco.mudancaNoCorpo(a, d), ...(escolher ? { escolherAlvo: escolher } : {}),
  };
  return new MotorCorpoMundo(politica, 101, CCO_CORPO_V11, estadoNascimentoPy(TICK_INICIAL),
                             { regra: () => braco.cerebro.ultimaRegra, cfgMundo: CMU_MVP, ...(digibrain === undefined ? {} : { digibrain }) });
}

/** a vida curta do teste: o dono deixa a racao no comedouro de tempos em tempos */
function viver(m: MotorCorpoMundo): MotorCorpoMundo {
  for (let p = 0; p < PASSOS; p++) {
    m.avancar(30);
    if (p % 4 === 0) m.deixarComida("racao", ...m.mundo.comedouro);
  }
  return m;
}
const impressao = (m: MotorCorpoMundo) => JSON.stringify({ log: m.log, mundo: m.mundo.resumo(), estado: m.estado });

describe("o ponto no laco do TS, atras da chave da v13 (T-PONTO-4)", () => {
  test("a chave nasce desligada: sem ela, o escolherAlvo da politica nunca e chamado e a vida e a de hoje", () => {
    const hoje = impressao(viver(laco(undefined, undefined)));
    let chamadas = 0;
    const contar: EscolherAlvo = () => { chamadas++; return alvoPonto(0, 0); };
    expect(impressao(viver(laco(contar, undefined)))).toBe(hoje);
    expect(impressao(viver(laco(contar, false)))).toBe(hoje);
    expect(chamadas).toBe(0);
    /* ligada, o cerebro que devolve null fica com o padrao do motor: a mesma vida */
    const nulo: EscolherAlvo = () => { chamadas++; return null; };
    expect(impressao(viver(laco(nulo, true)))).toBe(hoje);
    expect(chamadas).toBeGreaterThan(0);
  });

  test("ligada: o ponto inteiro dentro do mapa entra so no explorar, o pet anda ate ele e o registro diz `ponto`", () => {
    const vistos: string[] = [];
    const escolher: EscolherAlvo = (acao, cands) => {
      vistos.push(...cands.map(c => c.tipo));
      return acao === "explorar" ? alvoPonto(W - 1, H - 1) : null;
    };
    const m = viver(laco(escolher, true));
    const exploradas = m.mundo.decisoes.filter(d => d.acao === "explorar");
    expect(exploradas.length).toBeGreaterThan(0);
    expect(exploradas.every(d => d.alvo === "ponto")).toBe(true);
    expect(m.mundo.decisoes.filter(d => d.acao !== "explorar").some(d => d.alvo === "ponto")).toBe(false);
    /* cada explorar anda para o canto (W - 1, H - 1), e algum chega a sair do lugar */
    const passos = exploradas.map(d => { const [x0, y0] = d.antes as number[]; return [(d.x as number) - x0, (d.y as number) - y0]; });
    expect(passos.every(([dx, dy]) => dx >= 0 && dy >= 0)).toBe(true);
    expect(passos.some(([dx, dy]) => dx + dy > 0)).toBe(true);
    /* o explorar do motor nao ganhou candidato novo */
    for (const t of new Set(vistos)) expect(["bola", "casa", "cheiro", "comida", "continuar", "vagar"]).toContain(t);
    /* e a vida se refaz pelo log, com a mesma chave e o mesmo cerebro */
    const r = laco(escolher, true);
    for (const e of m.log) r.aplicarEvento(e);
    expect(impressao(r)).toBe(impressao(m));
  });

  test("ligada: o ponto fora do mapa ou nao inteiro levanta erro no motor", () => {
    for (const [x, y] of [[W, 0], [0, H], [-1, 5], [1.5, 0], [0, 2.5]]) {
      const m = laco((acao) => (acao === "explorar" ? alvoPonto(x, y) : null), true);
      expect(() => viver(m), `(${x}, ${y})`).toThrow(/ponto fora do mapa ou nao inteiro/);
    }
  });

  test("ligada: a validacao dos outros alvos nao relaxa (o ponto no comer e no brincar, e o alvo fora dos candidatos)", () => {
    for (const a of ["comer", "brincar"]) {
      const m = laco((acao) => (acao === a ? alvoPonto(10, 10) : null), true);
      expect(() => viver(m), a).toThrow(new RegExp(`alvo fora dos candidatos de ${a}`));
    }
    /* o ponto com id ou com `de` nao e o ponto do lugar lembrado */
    for (const p of [alvo("ponto", 10, 10, 3), alvo("ponto", 10, 10, null, "vagar")]) {
      const m = laco((acao) => (acao === "explorar" ? p : null), true);
      expect(() => viver(m)).toThrow(/alvo fora dos candidatos de explorar/);
    }
    /* um candidato com a posicao mudada */
    const torto = laco((acao, cands) => {
      if (acao !== "explorar") return null;
      const c = cands.find(k => k.tipo === "vagar")!;
      return { ...c, x: c.x === 0 ? 1 : c.x - 1 };
    }, true);
    expect(() => viver(torto)).toThrow(/alvo fora dos candidatos de explorar/);
    /* e o candidato do motor passa */
    const certo = laco((acao, cands) => (acao === "explorar" ? cands.find(k => k.tipo === "vagar")! : null), true);
    expect(() => viver(certo)).not.toThrow();
  });
});
