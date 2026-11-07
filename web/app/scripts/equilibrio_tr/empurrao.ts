/* A opcao --empurrao das bancadas da rodada de equilibrio (docs/TAREFA_V3_LUTA_EMPURRAO.md, etapa 4): `--empurrao v18` poe o empurrao de quem
   leva o golpe dos pets v18 (EMPURRAO_V18) por cima do relogio da bancada; sem a opcao, o relogio fica como estava. Outro valor falha alto. */
import { EMPURRAO_V18, type RelogioTR } from "../../motor/index.ts";

export function comEmpurrao(rel: RelogioTR, argv: readonly string[] = process.argv): RelogioTR {
  const i = argv.indexOf("--empurrao");
  if (i < 0) return rel;
  if (argv[i + 1] !== "v18") throw new Error(`--empurrao ${argv[i + 1] ?? ""}: so v18`);
  return { ...rel, empurraoAlvo: EMPURRAO_V18 };
}
