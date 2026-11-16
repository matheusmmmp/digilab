/* EQUILIBRIO_CUIDADO, E3 (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, EQ-6): a versao nova do pet com a F2 do E1. A v38 (a v35 com o equilibrio do
   cuidado, o ovo de um pet) e a v39 (a v37 com ele, o grupo):
   - nascem com as chaves ligadas (o AJUSTE_E1_PROPOSTO no modular e a BITS_V2), e as versoes de antes nao;
   - o ajuste vem da versao: o replay pelo log refaz a vida (a assinatura e os motivos do modular);
   - a v38 refaz, na bancada, a vida da v35 com a F2 ligada pela bancada (o E1), e a v39 a da v37 (o mesmo pet, a mesma conta);
   - a bancada nao liga o ajuste duas vezes. */
import { describe, expect, test } from "vitest";
import {
  GrupoDoJogo, Motor, TPD, VERSAO_GRUPO, VERSAO_PET, VERSAO_V35, VERSAO_V37, VERSAO_V38, VERSAO_V39, VERSOES_PET, nasceComEquilibrioCuidado,
  type EventoRegistro,
} from "../motor/index.ts";
import { AJUSTE_E1_DESLIGADO, AJUSTE_E1_PROPOSTO, ajusteE1Ligado } from "../motor/equilibrio_e1.ts";
import { BITS, BITS_V2, feitosDoPet, tabelaBitsDe } from "../src/bits.ts";
import { vida } from "../scripts/equilibrio_cuidado/e0.ts";

/** o ovo como o jogo monta (src/produto.ts e src/cerebro.ts): as tres chaves do produto, o modular e a ponte da luta */
const montar = (m: Motor): void => {
  m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
  m.trocarCerebro("modular");
  m.ligarPonteLuta(true);
};
/** um dia e meio com um dono simples (alimentar, limpar e brincar de tempos em tempos) */
function cuidar(m: Motor, k: number): void {
  if (k % 9 === 0) m.observar("alimentar");
  if (k % 13 === 0) m.observar("limpar");
  if (k % 7 === 0 && !m.e.dormindo) m.observar("brincar");
}

describe("o E3: a v38 e a v39", () => {
  test("os ovos novos sao a v38 e a v39, e so elas nascem com o equilibrio do cuidado", () => {
    expect([VERSAO_PET, VERSAO_GRUPO]).toEqual([VERSAO_V38, VERSAO_V39]);
    expect([VERSAO_V38, VERSAO_V39]).toEqual([38, 39]);
    expect(VERSOES_PET.filter(nasceComEquilibrioCuidado)).toEqual([38, 39]);
    expect(new Motor(101, VERSAO_V38).equilibrioE1).toBe(AJUSTE_E1_PROPOSTO);
    expect(ajusteE1Ligado(new Motor(101, VERSAO_V35).equilibrioE1)).toBe(false);
    for (const m of Object.values(new GrupoDoJogo(101, VERSAO_V39).motores)) expect(m.equilibrioE1).toBe(AJUSTE_E1_PROPOSTO);
    for (const m of Object.values(new GrupoDoJogo(101, VERSAO_V37).motores)) expect(m.equilibrioE1).toBe(AJUSTE_E1_DESLIGADO);
  });

  test("a tabela dos Bits pela versao: a BITS_V2 na v38 e na v39, a BITS nas de antes", () => {
    expect(tabelaBitsDe(VERSAO_V38)).toBe(BITS_V2);
    expect(tabelaBitsDe(VERSAO_V39)).toBe(BITS_V2);
    for (const v of VERSOES_PET.filter(x => x < 38)) expect(tabelaBitsDe(v)).toBe(BITS);
  });

  test("a bancada nao liga o ajuste na v38 (ele ja vem da versao); nas de antes, sim", () => {
    expect(() => new Motor(101, VERSAO_V38).ligarEquilibrioE1(AJUSTE_E1_PROPOSTO)).toThrow(/ja nasce com o ajuste/);
    expect(() => new Motor(101, VERSAO_V35).ligarEquilibrioE1(AJUSTE_E1_PROPOSTO)).not.toThrow();
  });

  test("o modular da v38 decide com as regras ligadas, e o da v35 sem elas", () => {
    const viver = (v: number): Motor => {
      const m = new Motor(202, v);
      montar(m);
      for (let k = 0; k < 96; k++) { cuidar(m, k); m.avancar(15); }
      return m;
    };
    const novo = viver(VERSAO_V38), antigo = viver(VERSAO_V35);
    expect(novo.lab!.ceq).toEqual(AJUSTE_E1_PROPOSTO.cerebro);
    expect(novo.lab!.motivos.every(x => "equilibrio" in x)).toBe(true);
    const bebe = novo.lab!.motivos.map(x => (x["equilibrio"] as { bebe: number | null }).bebe);   // o estagio entregue: S no bebe, 0 depois
    expect(bebe.some(b => b !== null && b > 0)).toBe(true);
    expect(bebe.some(b => b === 0)).toBe(true);
    expect(antigo.lab!.motivos.some(x => "equilibrio" in x)).toBe(false);
    expect(novo.assinatura()).not.toBe(antigo.assinatura());
    /* a regra dos Bits do ovo novo e a BITS_V2: a evolucao para o Rookie paga 60 */
    expect(feitosDoPet(novo).find(f => f.id === "evolucao:crianca")?.valor).toBe(60);
    expect(feitosDoPet(antigo).find(f => f.id === "evolucao:crianca")?.valor).toBe(50);
  });

  test("o replay da v38 pelo log refaz a vida (a assinatura e os motivos do modular)", () => {
    const m = new Motor(303, VERSAO_V38);
    montar(m);
    for (let k = 0; k < (1.5 * TPD) / 15; k++) { cuidar(m, k); m.avancar(15); }
    const r = Motor.reproduzir(303, JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], VERSAO_V38);
    expect(r.assinatura()).toBe(m.assinatura());
    expect(JSON.stringify(r.lab!.motivos)).toBe(JSON.stringify(m.lab!.motivos));
    expect(r.equilibrioE1).toBe(AJUSTE_E1_PROPOSTO);
  });

  test("o replay da v39 pelo log refaz o grupo", () => {
    const g = new GrupoDoJogo(404, VERSAO_V39);
    for (const i of g.ids) g.agir(i, montar);
    for (let k = 0; k < TPD / 15; k++) {
      g.avancar(15);
      g.agir(k % 2 === 0 ? "A" : "B", m => cuidar(m, k));
    }
    const r = GrupoDoJogo.reproduzir(404, VERSAO_V39, JSON.parse(JSON.stringify(g.log)));
    expect(r.assinatura()).toBe(g.assinatura());
    for (const i of g.ids) expect(JSON.stringify(r.motor(i).lab!.motivos)).toBe(JSON.stringify(g.motor(i).lab!.motivos));
  });

  test("na bancada, a v38 refaz a vida da v35 com a F2 ligada (o E1), e a v39 a da v37", () => {
    const semNumero = (x: { numero_versao: number }) => JSON.stringify({ ...x, numero_versao: null });
    for (const [versao, novo] of [["pet", VERSAO_V38], ["grupo", VERSAO_V39]] as const) {
      const e1 = vida(versao, "atento", 101, 1, true, { ajuste: AJUSTE_E1_PROPOSTO, bits: BITS_V2 });
      const e3 = vida(versao, "atento", 101, 1, true, { numero: novo });
      expect(e3.numero_versao).toBe(novo);
      expect(semNumero(e3)).toBe(semNumero(e1));
    }
  });
});
