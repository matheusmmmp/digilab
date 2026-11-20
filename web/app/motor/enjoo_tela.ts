/* O enjoo da imagem (GOSTO_VISUAL; D-GV-ENJOO-CER no docs/registro/2026-11.md): o espelho da `ConfigEnjooTela` do digilab/config.py.
   Desligada por padrao: a vida de hoje byte a byte. O corpo a recebe pelo laco (`OpcoesCorpoMundo.tela.enjoo`, so com a tela ligada) e o
   cerebro pelo DigiBrain (`OpcoesOlhar.cfgEnjooTela`, so com a subchave `olhar`). Fica num arquivo proprio, e nao no `tv.ts` nem nas
   constantes do modular, para nao mexer no que a captura ligada ao cerebro (#874) tambem muda. Todos os numeros PROPOSTOS, SEM FONTE; o
   porque de cada um esta na docstring da ConfigEnjooTela do Python. O gabarito: test/gabaritos/gosto_visual_enjoo.json.gz. */

/** o receptor do enjoo do estimulo de agora, na escala S (corpo.RECEPTOR_ENJOO_TELA do Python) */
export const RECEPTOR_ENJOO_TELA = "enjoo_tela";

export interface ConfigEnjooTela {
  readonly ligada: boolean;
  readonly meia_vida_desenjoo: number; readonly k_desenjoo: number;
  readonly meia_vida_olhando: number; readonly k_olhando: number;
  readonly meia_vida_enjoo: number; readonly k_enjoo: number;
  readonly prototipos: number; readonly raio_mesmo: number;
  readonly w_enjoo: number; readonly tau_enjoo_lembrado: number; readonly saturacao_exposicao: number; readonly peso_tedio: number;
}
const S = 1024;
export const CONFIG_ENJOO_TELA: ConfigEnjooTela = {
  ligada: false, meia_vida_desenjoo: 720, k_desenjoo: 63, meia_vida_olhando: 10, k_olhando: 4389, meia_vida_enjoo: 15, k_enjoo: 2960,
  prototipos: 6, raio_mesmo: 67500, w_enjoo: S / 2, tau_enjoo_lembrado: 1040, saturacao_exposicao: S / 2, peso_tedio: S / 2,
};
export const CONFIG_ENJOO_TELA_LIGADA: ConfigEnjooTela = { ...CONFIG_ENJOO_TELA, ligada: true };

/** o __post_init__ da ConfigEnjooTela: falha alto */
export function conferirConfigEnjooTela(c: ConfigEnjooTela): ConfigEnjooTela {
  if (typeof c.ligada !== "boolean") throw new Error(`ConfigEnjooTela.ligada e bool: ${String(c.ligada)}`);
  for (const campo of ["meia_vida_desenjoo", "k_desenjoo", "meia_vida_olhando", "k_olhando", "meia_vida_enjoo", "k_enjoo", "prototipos",
    "raio_mesmo", "tau_enjoo_lembrado", "saturacao_exposicao"] as const) {
    if (!Number.isInteger(c[campo]) || c[campo] <= 0) throw new Error(`ConfigEnjooTela.${campo} tem de ser inteiro positivo: ${c[campo]}`);
  }
  for (const campo of ["w_enjoo", "peso_tedio"] as const) {
    if (!Number.isInteger(c[campo]) || c[campo] < 0 || c[campo] > S) throw new Error(`ConfigEnjooTela.${campo} em [0, S]: ${c[campo]}`);
  }
  if (c.saturacao_exposicao >= S) throw new Error(`ConfigEnjooTela.saturacao_exposicao abaixo de S: ${c.saturacao_exposicao}`);
  if (c.tau_enjoo_lembrado < 15) throw new Error(`ConfigEnjooTela.tau_enjoo_lembrado abaixo do passo do cerebro (15 ticks): ${c.tau_enjoo_lembrado}`);
  return c;
}
