/* PE0 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.5), na luta da POC (LUTA_POC, LP4): os pets v21 lutam com o modular, com o A e com um
   "cb" entre duas lutas? O dono que vive e luta (a mesma vida para o teste) e o resumo de cada luta: o resultado da luta da POC resumido, a
   assinatura da confianca e o estadoInterno do modular. So le o motor; nao muda nada da vida.
   Antes da LP4 as variantes eram o pet de teste v16 e a v17, no combate por turnos, com o gabarito das lutas delas
   (test/gabaritos/ponte_luta_pe0.json.gz); o pet de teste nao luta mais, e o gabarito saiu com as versoes antigas (LP-6). */
import { createHash } from "node:crypto";
import { TPD } from "../motor/constantes.ts";
import { hashSemente, Motor, PetMorto, type EventoRegistro } from "../motor/index.ts";

export type Variante = "v21_modular" | "v21_a" | "v21_cb";
export const VARIANTES: readonly Variante[] = ["v21_modular", "v21_a", "v21_cb"];
export const SEMENTES = [101, 202, 303, 404, 505] as const;
export const DIAS = 2;

export interface Luta {
  evento: number; tick: number; cerebro: "modular" | "a"; rival: string; serie: number;
  /** por luta da serie: pontos de A, se acabou em nocaute, a vida de cada lado no comeco e no fim, os passos */
  lutas: { pontosA: number; ko: boolean; passos: number; hp0: number[]; hp: number[] }[];
  venceu: boolean; lesao: boolean;
  confianca: string; modular: string | null;   // sha256 das duas assinaturas (a do modular e o estadoInterno sem os motivos)
}
export interface Vida { variante: Variante; semente: number; versao: number; estagio: string; log: EventoRegistro[]; lutas: Luta[]; assinatura: string }

/** `ponte` (PE3): grava no ovo a marca "pl" da ponte da luta, como o jogo faz nos ovos novos (src/produto.ts); "eps" (PE4) grava { luta, eps } */
export function nascer(v: Variante, semente: number, ponte: boolean | "eps" = false): Motor {
  const m = new Motor(semente, 21);
  m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true });
  m.trocarCerebro(v === "v21_a" ? "a" : "modular");
  if (ponte) m.ligarPonteLuta(ponte === "eps");
  return m;
}

const sha = (x: string): string => createHash("sha256").update(x).digest("hex");
function resumir(m: Motor, rival: string, r: ReturnType<Motor["lutarPoc"]>): Luta {
  return {
    evento: m.log.length - 1, tick: m.e.tick, cerebro: m.cerebroAtual,
    rival, serie: r.serie.length,
    lutas: r.serie.map(x => ({ pontosA: x.pontosA, ko: x.fim, passos: x.passos, hp0: [x.vida0, x.rivalStats.hp], hp: [x.vidaA, x.vidaB] })),
    venceu: r.venceu, lesao: r.lesao,
    confianca: sha(JSON.stringify(m.conf.assinatura())),
    modular: m.lab ? sha(JSON.stringify({ ...m.lab.estadoInterno(), motivos: undefined })) : null,
  };
}

/** a vida curta com lutas: o dono cuida (racao, limpeza, carinho) e, do Rookie em diante, manda lutar na Arena (uma forma do estagio, no
    Campo de treino) e, de tempos em tempos, na Liga (a serie de 6, com as 6 medalhas); no `v21_cb` o cerebro troca entre duas lutas */
export function viverComLutas(v: Variante, semente: number, dias = DIAS, ponte: boolean | "eps" = false): Vida {
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
        lutas.push(resumir(m, "liga", m.lutarPoc("liga", hashSemente("liga", semente, m.log.length), null)));
      } else if (m.estagioAtual !== "bebe" && r >= 30 && r < 60) {
        const rivais = m.rivaisArenaPoc(), rival = rivais[k++ % rivais.length];
        lutas.push(resumir(m, rival, m.lutarPoc(rival, hashSemente("luta", semente, m.log.length), "campo")));
        if (v === "v21_cb" && lutas.length <= 2) m.trocarCerebro(lutas.length === 1 ? "a" : "modular");
      }
    } catch (err) { if (err instanceof PetMorto) throw err; /* o motor recusou: segue */ }
  }
  return { variante: v, semente, versao: m.versao, estagio: m.estagioAtual, log: JSON.parse(JSON.stringify(m.log)), lutas, assinatura: sha(m.assinatura()) };
}

/** o replay do registro evento a evento: depois de cada "l", as duas assinaturas (a mesma conta do resumir); o motor refeito sai junto */
export function refazer(v: Vida): { m: Motor; lutas: Pick<Luta, "evento" | "confianca" | "modular">[] } {
  const m = new Motor(v.semente, 21), lutas: Pick<Luta, "evento" | "confianca" | "modular">[] = [];
  v.log.forEach((ev, i) => {
    m.aplicarEvento(ev);
    if (ev[1] === "l") lutas.push({ evento: i, confianca: sha(JSON.stringify(m.conf.assinatura())),
      modular: m.lab ? sha(JSON.stringify({ ...m.lab.estadoInterno(), motivos: undefined })) : null });
  });
  return { m, lutas };
}
export const sha256 = sha;
