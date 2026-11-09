/* LUTA_POC, LP2 (docs/TAREFA_V3_LUTA_POC.md, secao 5.1): as vidas de hoje dos pets que abrem no jogo (v13 a v19 e o pet de teste v16), com
   cuidado E lutas pelo Motor (a Arena contra os bots e a Campanha contra o primeiro NPC), gravadas ANTES da luta nova no motor. Com a chave
   LUTA_POC_LIGADA desligada, estas vidas tem de sair byte a byte: o registro, a assinatura do pet e o resultado de cada luta.
   A mesma funcao serve ao gabarito, ao teste e ao gerador (node test/lp2_hoje.ts --gravar). So le o motor. */
import { createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { TPD } from "../motor/constantes.ts";
import { hashSemente, Motor, PetMorto, petDeTeste, type EventoRegistro } from "../motor/index.ts";

export type VarianteHoje = "v13" | "v14" | "v15" | "v16" | "v17_modular" | "v17_a" | "v18" | "v19";
export const VARIANTES_HOJE: readonly VarianteHoje[] = ["v13", "v14", "v15", "v16", "v17_modular", "v17_a", "v18", "v19"];
export const SEMENTES_HOJE = [101, 202, 303, 404, 505] as const;
export const DIAS_HOJE = 5;
/** os rivais da Arena que a vida desafia, em rodizio, e o primeiro desafio da Campanha (o primeiro rival do primeiro lugar) */
export const BOTS_HOJE = ["agressivo", "tartaruga", "atirador"] as const;

const PRODUTO = { chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true };

/** o ovo como o jogo choca hoje (src/produto.ts e src/lab.ts): as chaves do produto, o cerebro dos ovos trocaveis e a ponte da luta */
export function nascerHoje(v: VarianteHoje, semente: number): Motor {
  if (v === "v16") {
    const m = petDeTeste(semente);
    m.ligarProduto(PRODUTO);
    m.ligarPonteLuta(true);
    return m;
  }
  const versao = Number(v.slice(1, 3));
  const m = new Motor(semente, versao);
  m.ligarProduto(PRODUTO);
  if (versao >= 17) {
    m.trocarCerebro(v === "v17_a" ? "a" : "modular");
    m.ligarPonteLuta(true);
  }
  return m;
}

const sha = (x: string): string => createHash("sha256").update(x).digest("hex");

export interface VidaHoje {
  variante: VarianteHoje; semente: number; versao: number; estagio: string; eventos: number; lutas: number; vitorias: number;
  log_sha: string; assinatura: string; resultados: string;
}

/** a vida de cuidado com lutas; devolve o motor, o registro e o resultado de cada luta (vencedor e vida do fim) */
export function viverHoje(v: VarianteHoje, semente: number, dias = DIAS_HOJE): { m: Motor; log: EventoRegistro[]; res: string[] } {
  const m = nascerHoje(v, semente), res: string[] = [];
  for (let p = 0; p < Math.round(dias * TPD / 30) && !m.morte; p++) {
    m.avancar(30);
    const mu = m.mundo!, r = hashSemente("lp2-hoje", semente, p) % 100;
    try {
      if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
      if (m.e.sujeira >= 2 && r < 70) m.observar("limpar");
      if (p % 5 === 0 && r < 80) m.observar("acariciar");
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
      if (p % 12 === 6 && m.estagioAtual !== "bebe") {
        const rival = p % 36 === 30 ? m.lugares[0].rivais[0] : BOTS_HOJE[(p / 12 | 0) % BOTS_HOJE.length];
        const R = m.lutar(rival, hashSemente("lp2-hoje-luta", semente, p));
        res.push(`${rival}:${R.serie.map(x => `${x.pontosA}/${x.fim}/${x.E.L.map(l => l.hp).join(",")}`).join(";")}`);
      }
    } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ }
  }
  return { m, log: JSON.parse(JSON.stringify(m.log)) as EventoRegistro[], res };
}

export function gravarHoje(v: VarianteHoje, semente: number, m: Motor, log: readonly EventoRegistro[], res: readonly string[]): VidaHoje {
  return {
    variante: v, semente, versao: m.versao, estagio: m.estagioAtual, eventos: log.length, lutas: m.lutas.lutas, vitorias: m.lutas.vitorias,
    log_sha: sha(JSON.stringify(log)), assinatura: sha(m.assinatura()), resultados: sha(JSON.stringify(res)),
  };
}

export const todasHoje = (): VidaHoje[] =>
  VARIANTES_HOJE.flatMap(v => SEMENTES_HOJE.map(s => { const { m, log, res } = viverHoje(v, s); return gravarHoje(v, s, m, log, res); }));

if (process.argv.includes("--gravar")) {
  const vidas = todasHoje();
  writeFileSync(new URL("./gabaritos/lp2_vidas_hoje.json", import.meta.url),
    JSON.stringify({ versao: 1, dias: DIAS_HOJE, sementes: SEMENTES_HOJE, variantes: VARIANTES_HOJE, vidas }, null, 1) + "\n");
  console.log(`gravado: ${vidas.length} vidas, ${vidas.reduce((s, x) => s + x.lutas, 0)} lutas`);
}
