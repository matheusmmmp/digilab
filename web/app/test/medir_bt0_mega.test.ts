// BETA, BT0 (docs/PLANO_V3_BETA.md, secao 3): o script do tempo ate o primeiro Mega (scripts/medir_bt0_mega.ts).
// A vida: os dois ovos do brasao pedido, o estagio de cada pet so anda para a frente, o relogio do palco cresce com as lutas.
// O relogio: o tempo aberto e o tempo de jogo na velocidade mais o que segura o relogio, e os dias saem das sessoes.
import { describe, expect, test } from "vitest";
import { ESPECIES, GrupoDoJogo, TPD, VERSAO_GRUPO } from "../motor/index.ts";
import { HIPOTESES, NIVEIS_CAIS, VARIANTES, diasDeRelogio, medir, segundosAbertos, sementeDoBrasao, viver } from "../scripts/medir_bt0_mega.ts";
import { PERFIS } from "../scripts/medir_cn0_save.ts";

describe("BT0: a vida ate o Mega", () => {
  test("a semente do brasao da o primeiro ovo da especie pedida", () => {
    for (const esp of ESPECIES) {
      const g = new GrupoDoJogo(sementeDoBrasao(esp, 0), VERSAO_GRUPO);
      expect(g.motor(g.ids[0]).especie).toBe(esp);
    }
  });
  test("uma vida curta: o Rookie chega, os estagios vem em ordem e a vida e a mesma de novo (determinismo)", () => {
    const a = viver(PERFIS[0], "brasa", 0, 3), b = viver(PERFIS[0], "brasa", 0, 3);
    expect(JSON.stringify(a)).toBe(JSON.stringify(b));
    expect(a.primeiro.crianca).toBeDefined();
    expect(a.dias).toBe(3);
    expect(a.nivelPorDia.length).toBe(3);
    for (let k = 1; k < a.nivelPorDia.length; k++) expect(a.nivelPorDia[k]).toBeGreaterThanOrEqual(a.nivelPorDia[k - 1]);
    for (const p of a.pets) {
      const ticks = (["crianca", "adolescente", "adulto", "mega"] as const).flatMap(e => p.estagios[e] ? [p.estagios[e]!.tick] : []);
      expect([...ticks].sort((x, y) => x - y)).toEqual(ticks);
    }
    if (a.lutas > 0) expect(a.segundosPalco).toBeGreaterThan(0);
  }, 120_000);
  test("o dono que equipa os chips grava o equipar no registro do pet quando ha medalha", () => {
    const v = viver(PERFIS[0], "cirro", 0, 4, "chips");
    if (v.medalhas > 0) expect(v.chipsEquipados).toBeGreaterThan(0);
    expect(VARIANTES).toContain(v.variante);
  }, 120_000);
});

describe("BT0: o relogio", () => {
  const m = { tick: 480 + TPD, minutosDeJogo: TPD, lutas: 10, segundosPalco: 250, chamadosBebe: 5, dia: 1 };
  test("o tempo aberto e o tempo de jogo na velocidade mais o palco, o Resultado e os chamados", () => {
    const s = segundosAbertos(m, 10, "dedicado");
    expect(s).toBeCloseTo(TPD / 10 + 250 + 10 * HIPOTESES.segundosResultado + 5 * HIPOTESES.segundosAtender.dedicado, 6);
    expect(segundosAbertos(m, 10, "dedicado", true)).toBeCloseTo(s - TPD / 10, 6);
    expect(segundosAbertos(m, 1 / 60, "dedicado")).toBeGreaterThan(TPD * 60);            // a 1x, um dia de jogo e um dia aberto
  });
  test("os dias de relogio dividem o tempo aberto pelos minutos abertos por dia", () => {
    expect(diasDeRelogio(7200, 120)).toBe(1);
    expect(diasDeRelogio(7200, 30)).toBe(4);
  });
  test("a tabela do --rapido tem cada variante, perfil e especie, e os niveis do cais", () => {
    const r = medir({ vidas: 1, especies: ESPECIES.slice(0, 1), dias: 2 });
    expect(r.tabela.length).toBe(VARIANTES.length * PERFIS.length * 2);
    for (const t of r.tabela) {
      expect(Object.keys(t.niveis)).toEqual(NIVEIS_CAIS.map(n => `nivel${n}`));
      expect(t.estagios.Rookie.chegaram).toBe(t.vidas);
    }
  }, 300_000);
});
