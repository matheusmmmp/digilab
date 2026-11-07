/* DC3d da CONVERSA_PET (docs/TAREFA_V3_CONVERSA_PET.md, secao DC3d): as vidas de hoje dos pets que abrem no jogo, gravadas ANTES do porte da
   subchave `fala_unidades` (o espelho TS, a marca do ovo de teste e a intencao da voz). Com a marca ausente (todo pet de hoje), estas vidas tem
   de sair byte a byte: o registro, a assinatura do pet, os motivos do modular e os conceitos do `dec-v2` da ultima decisao.
   O dono cuida (racao no comedouro perto do pet, limpeza, carinho) e nao luta (as lutas sao o gabarito da PE0). So le o motor. */
import { createHash } from "node:crypto";
import { TPD } from "../motor/constantes.ts";
import { hashSemente, Motor, PetMorto, petDeTeste, type EventoRegistro } from "../motor/index.ts";

export type VarianteHoje = "v13" | "v14" | "v15" | "v16" | "v17_modular" | "v17_a" | "v18" | "v19";
export const VARIANTES_HOJE: readonly VarianteHoje[] = ["v13", "v14", "v15", "v16", "v17_modular", "v17_a", "v18", "v19"];
export const SEMENTES_HOJE = [101, 202, 303, 404, 505] as const;
export const DIAS_HOJE = 3;

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
  variante: VarianteHoje; semente: number; versao: number; estagio: string; eventos: number;
  log_sha: string; assinatura: string; decisoes_modular: number; motivos: string | null; conceitos_v2: string | null;
}

/** a vida curta de cuidado; devolve o motor e o registro */
export function viverHoje(v: VarianteHoje, semente: number, dias = DIAS_HOJE): { m: Motor; log: EventoRegistro[] } {
  const m = nascerHoje(v, semente);
  for (let p = 0; p < Math.round(dias * TPD / 30) && !m.morte; p++) {
    m.avancar(30);
    const mu = m.mundo!, r = hashSemente("dc3d", semente, p) % 100;
    try {
      if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
      if (m.e.sujeira >= 2 && r < 70) m.observar("limpar");
      if (p % 5 === 0 && r < 80) m.observar("acariciar");
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
    } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ }
  }
  return { m, log: JSON.parse(JSON.stringify(m.log)) as EventoRegistro[] };
}

export function gravarHoje(v: VarianteHoje, semente: number, m: Motor, log: readonly EventoRegistro[]): VidaHoje {
  const lab = m.lab;
  const c = m.conceitosDec("dec-v2");
  return {
    variante: v, semente, versao: m.versao, estagio: m.estagioAtual, eventos: log.length, log_sha: sha(JSON.stringify(log)),
    assinatura: sha(m.assinatura()), decisoes_modular: lab === null ? 0 : lab.motivos.length,
    motivos: lab === null ? null : sha(JSON.stringify(lab.motivos)), conceitos_v2: c === null ? null : sha(JSON.stringify(c)),
  };
}

export const todasHoje = (): VidaHoje[] =>
  VARIANTES_HOJE.flatMap(v => SEMENTES_HOJE.map(s => { const { m, log } = viverHoje(v, s); return gravarHoje(v, s, m, log); }));
