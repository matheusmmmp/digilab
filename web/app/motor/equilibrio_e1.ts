/* EQUILIBRIO_CUIDADO, E1: o ajuste da calibracao (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md; docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E1.md). Um objeto
   so com tudo o que o E1 muda no pet, cada item atras da sua chave e desligado por padrao:
   - `cerebro`: as duas regras novas da EQ-7 (a ConfigEquilibrioCuidado do Python e do modular: a guarda da fome urgente no brincar e o bebe que
     come com a fome dele);
   - os numeros do modular que ja existem e so trocam de valor (null: o de hoje): o `lambda_acordar` do sono que segura, o `urgencia_lambda`
     dos inatos (a fome urgente, que tambem acorda), o vies do brincar no W0 e o `w_bola_do_dono` do lance (so o do cerebro).
   O `Motor.ligarEquilibrioE1` o aplica ao modular do pet, ANTES da primeira troca para o modular. Nao entra no registro: e so da bancada do E1
   (scripts/equilibrio_cuidado/); o jogo nao o chama, e os pets de hoje (todas as versoes) seguem byte a byte. A versao nova, com os valores
   escolhidos, e o E3 (EQ-6). Os Bits (so do jogo) ficam fora daqui: a tabela BITS_V2 de src/bits.ts. */
import { CONFIG_EQUILIBRIO_CUIDADO, INATOS_MODULAR, validarEquilibrioCuidado, type ConfigEquilibrioCuidado, type ConfigLanceDono,
  type ConfigSonoSegura } from "./digibrain/constantes.ts";

export interface AjusteEquilibrioE1 {
  readonly cerebro: ConfigEquilibrioCuidado;
  readonly lambda_acordar: number | null;
  readonly urgencia_lambda: number | null;
  readonly vies_brincar: number | null;
  readonly w_bola_do_dono: number | null;
}
export const AJUSTE_E1_DESLIGADO: AjusteEquilibrioE1 = {
  cerebro: CONFIG_EQUILIBRIO_CUIDADO, lambda_acordar: null, urgencia_lambda: null, vies_brincar: null, w_bola_do_dono: null,
};

/** confere o ajuste (falha alto): os campos, a config do cerebro e os numeros inteiros */
export function validarAjusteE1(a: AjusteEquilibrioE1): AjusteEquilibrioE1 {
  const nomes = ["cerebro", "lambda_acordar", "urgencia_lambda", "vies_brincar", "w_bola_do_dono"];
  if (a === null || typeof a !== "object" || Object.keys(a).sort().join() !== nomes.join())
    throw new Error(`AjusteEquilibrioE1 com os campos ${nomes.join(", ")}: ${JSON.stringify(a)}`);
  validarEquilibrioCuidado(a.cerebro);
  for (const k of ["lambda_acordar", "urgencia_lambda", "vies_brincar", "w_bola_do_dono"] as const) {
    const v = a[k];
    if (v !== null && !Number.isSafeInteger(v)) throw new Error(`AjusteEquilibrioE1.${k} e inteiro ou null: ${String(v)}`);
  }
  const S = INATOS_MODULAR.escala;
  if (a.lambda_acordar !== null && !(INATOS_MODULAR.lambda_sono < a.lambda_acordar && a.lambda_acordar <= S))
    throw new Error(`AjusteEquilibrioE1.lambda_acordar em (lambda_sono, S]: ${a.lambda_acordar}`);
  if (a.urgencia_lambda !== null && !(0 <= a.urgencia_lambda && a.urgencia_lambda <= S))
    throw new Error(`AjusteEquilibrioE1.urgencia_lambda em [0, S]: ${a.urgencia_lambda}`);
  if (a.w_bola_do_dono !== null && a.w_bola_do_dono <= 0) throw new Error(`AjusteEquilibrioE1.w_bola_do_dono positivo: ${a.w_bola_do_dono}`);
  return a;
}
/** algum item do ajuste ligado */
export const ajusteE1Ligado = (a: AjusteEquilibrioE1): boolean =>
  a.cerebro.guarda_fome_brincar || a.cerebro.comer_bebe || a.lambda_acordar !== null || a.urgencia_lambda !== null ||
  a.vies_brincar !== null || a.w_bola_do_dono !== null;

/** os inatos com o ajuste (o `urgencia_lambda` e o vies do brincar no W0); sem ajuste, os mesmos objetos */
export function inatosComAjuste<T extends typeof INATOS_MODULAR>(inatos: T, a: AjusteEquilibrioE1): T {
  let out: T = inatos;
  if (a.urgencia_lambda !== null) out = { ...out, urgencia_lambda: a.urgencia_lambda };
  if (a.vies_brincar !== null) {
    const v = a.vies_brincar;
    let achou = false;
    const w0 = out.w0.map(([b, linha]) => {
      if (b !== "brincar") return [b, linha] as const;
      achou = true;
      return [b, linha.map(([c, x]) => (c === "vies" ? [c, v] as const : [c, x] as const))] as const;
    });
    if (!achou) throw new Error("AjusteEquilibrioE1: o W0 sem a linha do brincar");
    out = { ...out, w0 } as T;
  }
  return out;
}
/** o sono que segura com o ajuste (so o `lambda_acordar`, e so se a versao ja o liga) */
export const sonoComAjuste = (s: ConfigSonoSegura, a: AjusteEquilibrioE1): ConfigSonoSegura =>
  a.lambda_acordar === null || !s.ligada ? s : { ...s, lambda_acordar: a.lambda_acordar };
/** o lance do cerebro com o ajuste (so o `w_bola_do_dono`, e so se a versao ja o liga); o do laco nao muda */
export const lanceComAjuste = (l: ConfigLanceDono, a: AjusteEquilibrioE1): ConfigLanceDono =>
  a.w_bola_do_dono === null || !l.ligada ? l : { ...l, w_bola_do_dono: a.w_bola_do_dono };

/** o ajuste que o E1 propoe (a rodada F2 da grade; docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E1.md): as duas regras ligadas, o peso do bebe de
    hoje da config (S/2), a fome urgente em 640 e o vies do brincar em 0; o `lambda_acordar` e o `w_bola_do_dono` ficam os de hoje (a grade nao
    achou ganho neles). PROPOSTO, SEM FONTE; o Python tem os mesmos numeros (config.INATOS_E1_PROPOSTOS), conferidos pelo gabarito do
    test/equilibrio_cuidado_paridade.test.ts */
export const AJUSTE_E1_PROPOSTO: AjusteEquilibrioE1 = {
  cerebro: { ...CONFIG_EQUILIBRIO_CUIDADO, guarda_fome_brincar: true, comer_bebe: true }, lambda_acordar: null, urgencia_lambda: 640,
  vies_brincar: 0, w_bola_do_dono: null,
};
