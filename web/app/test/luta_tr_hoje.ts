/* O gabarito das lutas em tempo real de hoje (docs/TAREFA_V3_LUTA_EMPURRAO.md, etapa 2), gravado ANTES do empurrao novo: as lutas das regras
   v13 (CV21E_TR) e v14 (CV21E_TR14; a v15, a v16 e a v17 lutam com elas) tem de sair byte a byte com a chave do empurrao desligada.
   Por luta: o resultado, a vida do fim e o sha256 do estado passo a passo (o x dos dois lados, a vida, o Guts, a acao e o atordoamento)
   e dos eventos. A mesma funcao serve ao gabarito, ao teste e ao gerador (npx tsx test/luta_tr_hoje.ts --gravar). So le o motor. */
import { createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { CV21E_TR, CV21E_TR14, FORMAS_AD, criarLutaTR, lutadorBot, passoTR, type Lutador, type RegrasLuta } from "../motor/index.ts";

export const SEMENTES = [101, 202, 303, 404, 505] as const;
/** os desafiantes e lideres da campanha que entram, lutando entre si (a escala ligada nos dois lados) */
export const NPCS = ["npc_tier1_brutamontes", "npc_tier2_sentinela", "npc_tier2_porteiro", "npc_v5_puppetmon", "npc_v5_machinedramon"] as const;
export const REGRAS: Readonly<Record<string, RegrasLuta>> = { v13: CV21E_TR, v14: CV21E_TR14 };

export interface LutaGravada { regras: string; a: string; b: string; semente: number; pontosA: number; fim: string; passos: number; hp: number[]; estado: string }

const sha256 = (s: string): string => createHash("sha256").update(s).digest("hex");

/** uma luta, passo a passo, com o registro do estado de cada passo */
export function lutar(regras: string, a: string, b: string, semente: number): LutaGravada {
  const R = REGRAS[regras];
  if (!R) throw new Error(`regras desconhecidas: ${regras}`);
  const A: Lutador = lutadorBot(a, R), B: Lutador = lutadorBot(b, R);
  const Lt = criarLutaTR(A, B, semente, { R, eventos: true }), S = Lt.S, h = createHash("sha256");
  let fim: ReturnType<typeof passoTR> = null;
  while (!(fim = passoTR(Lt))) {
    h.update(S.L.map(l => `${l.x};${l.hp};${l.guts};${l.acao?.nome ?? "-"};${l.atordoadoAte}`).join("|") + "\n");
  }
  h.update(JSON.stringify(Lt.eventos)); h.update(JSON.stringify(Lt.acoes));
  return { regras, a, b, semente, pontosA: fim[0], fim: fim[1], passos: S.passo, hp: S.L.map(l => l.hp), estado: h.digest("hex") };
}

/** todas as lutas do gabarito: as 8 formas adultas contra as 8 e os NPCs entre si, nas duas regras e nas 5 sementes de teste */
export function todas(): LutaGravada[] {
  const out: LutaGravada[] = [];
  for (const r of Object.keys(REGRAS)) for (const s of SEMENTES) {
    for (const a of FORMAS_AD) for (const b of FORMAS_AD) out.push(lutar(r, a, b, s));
    for (const a of NPCS) for (const b of NPCS) if (a !== b) out.push(lutar(r, a, b, s));
  }
  return out;
}

export const assinatura = (ls: LutaGravada[]): string => sha256(JSON.stringify(ls));

if (process.argv.includes("--gravar")) {
  const lutas = todas();
  const saida = new URL("./gabaritos/luta_tr_hoje.json.gz", import.meta.url);
  writeFileSync(saida, gzipSync(Buffer.from(JSON.stringify({ sementes: SEMENTES, npcs: NPCS, lutas, assinatura: assinatura(lutas) }), "utf8"), { level: 9 }));
  console.log(`gravado: ${lutas.length} lutas, assinatura ${assinatura(lutas).slice(0, 16)}`);
}
