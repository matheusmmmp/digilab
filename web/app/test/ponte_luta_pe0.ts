/* PE0 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.5): o v16 e o v17 lutam? O dono que vive e luta (a mesma vida para o gabarito, o teste
   e o gerador) e o resumo de cada luta: o ResultadoLuta resumido, a assinatura do GambitsPet, a da confianca e o estadoInterno do modular.
   So le o motor; nao muda nada da vida. */
import { createHash } from "node:crypto";
import { TPD } from "../motor/constantes.ts";
import { hashSemente, Motor, PetMorto, petDeTeste, type EventoRegistro } from "../motor/index.ts";

export type Variante = "v16" | "v17_modular" | "v17_a" | "v17_cb";
export const VARIANTES: readonly Variante[] = ["v16", "v17_modular", "v17_a", "v17_cb"];
export const SEMENTES = [101, 202, 303, 404, 505] as const;
export const DIAS = 2;
const RIVAIS = ["aleatorio", "npc_tier1_brutamontes", "npc_tier2_sentinela", "duelista"];

export interface Luta {
  evento: number; tick: number; cerebro: "modular" | "a"; rival: string; serie: number;
  /** por luta da serie: pontos de A, como acabou, a vida de cada lado no comeco e no fim, os passos */
  lutas: { pontosA: number; fim: string; passos: number; hp0: number[]; hp: number[]; acoes: number }[];
  venceu: boolean; lesao: boolean;
  gambits: string; confianca: string; modular: string | null;   // sha256 das tres assinaturas (a do modular e o estadoInterno sem os motivos)
}
export interface Vida { variante: Variante; semente: number; versao: number; estagio: string; log: EventoRegistro[]; lutas: Luta[]; assinatura: string }

/** `ponte` (PE3): grava no ovo a marca "pl" da ponte da luta, como o jogo faz nos ovos novos (src/produto.ts); sem ela, a vida de hoje (o gabarito) */
export function nascer(v: Variante, semente: number, ponte = false): Motor {
  const m = v === "v16" ? petDeTeste(semente) : new Motor(semente);
  if (v !== "v16") m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
  if (v === "v17_modular" || v === "v17_cb") m.trocarCerebro("modular");
  if (v === "v17_a") m.trocarCerebro("a");
  if (ponte) m.ligarPonteLuta();
  return m;
}

const sha = (x: string): string => createHash("sha256").update(x).digest("hex");
function resumir(m: Motor, rival: string, r: ReturnType<Motor["lutar"]>): Luta {
  return {
    evento: m.log.length - 1, tick: m.e.tick, cerebro: m.cerebroAtual,
    rival, serie: r.serie.length,
    lutas: r.serie.map(x => ({ pontosA: x.pontosA, fim: x.fim, passos: x.tr.passos, hp0: x.tr.E0.hp, hp: x.tr.E.L.map((l: { hp: number }) => l.hp), acoes: x.tr.acoes.length })),
    venceu: r.venceu, lesao: !!r.lesao,
    gambits: sha(JSON.stringify(m.gp!.assinatura())), confianca: sha(JSON.stringify(m.conf.assinatura())),
    modular: m.lab ? sha(JSON.stringify({ ...m.lab.estadoInterno(), motivos: undefined })) : null,
  };
}

/** a vida curta com lutas: o dono cuida (racao, limpeza, carinho) e, do Rookie em diante, manda lutar; no `v17_cb` o cerebro troca entre duas lutas */
export function viverComLutas(v: Variante, semente: number, dias = DIAS, ponte = false): Vida {
  const m = nascer(v, semente, ponte), lutas: Luta[] = [];
  let k = 0;
  for (let p = 0; p < Math.round(dias * TPD / 30) && !m.morte; p++) {
    m.avancar(30);
    const mu = m.mundo!, r = hashSemente("pe0", semente, p) % 100;
    try {
      if (m.e.fome < .6 && p % 2 === 0) m.deixarComida("racao", Math.max(0, Math.min(1023, mu.pet[0] + 24)), mu.pet[1]);
      if (m.e.sujeira >= 2) m.observar("limpar");
      if (p % 5 === 0) m.observar("acariciar");
      if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
      if (m.medalhas < 3) m.liberar(3);
      if (m.estagioAtual !== "bebe" && r < 30) m.treinar(["corrida", "alvo", "meditar"][k++ % 3] as never);
      if (m.estagioAtual !== "bebe" && p % 40 === 30) {      // a serie: a Liga dos Lideres (6 lutas), com as 6 medalhas
        m.liberar(6);
        lutas.push(resumir(m, "liga", m.lutar("liga", hashSemente("liga", semente, m.log.length), null)));
      } else if (m.estagioAtual !== "bebe" && r >= 30 && r < 60) {
        const rival = RIVAIS[k++ % RIVAIS.length];
        lutas.push(resumir(m, rival, m.lutar(rival, hashSemente("luta", semente, m.log.length), null)));
        if (v === "v17_cb" && lutas.length <= 2) m.trocarCerebro(lutas.length === 1 ? "a" : "modular");
      }
    } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ }
  }
  return { variante: v, semente, versao: m.versao, estagio: m.estagioAtual, log: JSON.parse(JSON.stringify(m.log)), lutas, assinatura: sha(m.assinatura()) };
}

/** o que o gabarito guarda de uma vida (o registro entra pelo sha256: a vida sai do dono acima, e o registro muda se o motor mudar) */
export interface VidaGravada { variante: Variante; semente: number; versao: number; estagio: string; eventos: number; log_sha: string; assinatura: string; lutas: Luta[] }
export const gravar = (v: Vida): VidaGravada =>
  ({ variante: v.variante, semente: v.semente, versao: v.versao, estagio: v.estagio, eventos: v.log.length, log_sha: sha(JSON.stringify(v.log)), assinatura: v.assinatura, lutas: v.lutas });
export const todasAsVidas = (): Vida[] => VARIANTES.flatMap(v => SEMENTES.map(s => viverComLutas(v, s)));

/** o replay do registro evento a evento: depois de cada "l", as tres assinaturas (a mesma conta do resumir); o motor refeito sai junto */
export function refazer(v: Vida): { m: Motor; lutas: Pick<Luta, "evento" | "gambits" | "confianca" | "modular">[] } {
  const m = v.variante === "v16" ? petDeTeste(v.semente) : new Motor(v.semente), lutas: Pick<Luta, "evento" | "gambits" | "confianca" | "modular">[] = [];
  v.log.forEach((ev, i) => {
    m.aplicarEvento(ev);
    if (ev[1] === "l") lutas.push({ evento: i, gambits: sha(JSON.stringify(m.gp!.assinatura())), confianca: sha(JSON.stringify(m.conf.assinatura())),
      modular: m.lab ? sha(JSON.stringify({ ...m.lab.estadoInterno(), motivos: undefined })) : null });
  });
  return { m, lutas };
}
export const sha256 = sha;
