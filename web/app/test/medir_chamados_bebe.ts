/* O efeito dos chamados do bebe pelo corpo (a chave chamadosPeloCorpo; docs/TAREFA_V2_PRODUTO_CUIDADO.md, a opcao (C) do Matheus de
   2026-10-30): quantos chamados abrem no bebe, de cada tipo, e a fracao de cuidado com que ele evolui (o ramo da crianca: sereno com 0,8
   ou mais, arisco abaixo; CAT.limiarCuidado), nos ritmos rapido e classico. Tres estados das chaves, nos mesmos seis donos de roteiro do
   test/medir_chamado_fome.ts (SEM FONTE) e nas sementes 101, 202 e 303:
     hoje        sem o evento "p" (os chamados pelo relogio);
     fome        as duas chaves de 2026-10-29 (o chamado de fome pelo corpo, com o 0,45; o PR #450);
     corpo       as tres, as dos ovos novos desde 2026-10-30 (os tres chamados pelo corpo, com os limiares do bebe).
   So le o motor; nao muda nada do jogo.

     node --experimental-strip-types test/medir_chamados_bebe.ts     # grava test/efeito_chamados_bebe.json */
import { writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { CHAMADO_BEBE_CORPO } from "../motor/constantes.ts";
import type { ChavesProduto } from "../motor/tipos.ts";
import { DONOS, SEMENTES, vida } from "./medir_chamado_fome.ts";

const SAIDA = new URL("./efeito_chamados_bebe.json", import.meta.url);
const CHAVES: Record<string, ChavesProduto | null> = {
  hoje: null,
  fome: { chamadoPelaFome: true, decisaoNaComida: true },
  corpo: { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true },
};

/** a medicao inteira (o test/produto_cuidado.test.ts confere que o arquivo gravado esta em dia) */
export function medirEfeitoBebe() {
  const vidas = [];
  for (const ritmo of ["rapida", "classica"] as const) for (const dono of DONOS) for (const [chaves, ch] of Object.entries(CHAVES))
    for (const s of SEMENTES) vidas.push({ ritmo, dono, chaves, semente: s, ...vida(s, ritmo, ch, dono) });
  return {
    descricao: "o efeito dos chamados do bebe pelo corpo no pet do jogo (v13): os chamados abertos no bebe e a fracao de cuidado da "
      + "evolucao para a crianca, sem o evento \"p\" (hoje), com as duas chaves de 2026-10-29 (fome) e com as tres (corpo), nos ritmos "
      + "rapido (180 min) e classico (360 min)",
    limiares: CHAMADO_BEBE_CORPO, sementes: SEMENTES, donos: DONOS, vidas,
  };
}
export const textoEfeitoBebe = (): string => JSON.stringify(medirEfeitoBebe(), null, 1) + "\n";

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  writeFileSync(SAIDA, textoEfeitoBebe());
  for (const l of medirEfeitoBebe().vidas) console.log(l.ritmo.padEnd(8), l.dono.padEnd(13), l.chaves.padEnd(5), l.semente,
    JSON.stringify(l.chamados_abertos), "cuidado", l.cuidado?.toFixed(3), l.ramo);
}
