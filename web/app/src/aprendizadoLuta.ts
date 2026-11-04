/* O que o pet aprendeu sozinho nas lutas, em linhas legiveis para a tela (painel "O que o pet aprendeu", ao lado do EditorRegras).
   So leitura do GambitsPet (motor/gambits_pet.ts): nada aqui muda o motor, o registro ou o replay.
   O motor guarda a nota ATUAL de cada regra, quantas vezes ela disparou, a lista de partida (so nos pets v14: posSemente) e o texto das
   mudancas. Ele nao guarda a nota luta a luta; por isso "subiu/desceu" so existe contra a lista de partida e so nos v14 (senao, null). */
import { CV, GA, baseDe, CV21, regraDe, rotuloRegra, type GambitsPet, type MudancaGambit } from "../motor/index.ts";

export type EstadoRegra = "livre" | "travada" | "chip";
export interface LinhaRegra {
  k: string; pos: number; rotulo: string; nota: number; disparos: number; estado: EstadoRegra;
  /** posicoes ganhas (+) ou perdidas (-) contra a lista de partida; null quando o motor nao guarda a partida (pets v13) */
  delta: number | null;
  /** a pior regra livre abaixo do limiar: a proxima a ser trocada na proxima luta */
  candidataATroca: boolean;
}
export interface PassoAprendizado { alfa: number; limiar: number; bonus: number; eps: number }
export interface Mudanca { luta: number; tipo: "troca" | "evolucao" | "dono"; texto: string }
export interface VisaoAprendizado {
  nLutas: number; passo: PassoAprendizado; capacidade: number; linhas: LinhaRegra[]; mudancas: Mudanca[];
  travadas: string[]; vetadas: { k: string; rotulo: string }[];
}

export function passoDe(gp: GambitsPet): PassoAprendizado {
  const a = gp.aprendizadoTR;
  return { alfa: a?.alfa ?? GA.alfa, limiar: a?.limiar ?? GA.limiarTroca, bonus: a?.bonus ?? GA.bonusResultado, eps: CV.eps };
}
export function tipoMudanca(x: MudancaGambit): Mudanca["tipo"] {
  return x.dono ? "dono" : x.texto.startsWith("trocou") ? "troca" : "evolucao";
}
export function visaoAprendizado(gp: GambitsPet, quantas = 12): VisaoAprendizado {
  if (!gp.forma) throw new Error("o pet ainda não tem regras de combate");
  const passo = passoDe(gp);
  const livres = gp.ativas.filter(k => !(k in gp.travas) && !gp.chipsRegra.includes(k));
  const pior = livres.slice().sort((a, b) => gp.notas[a] - gp.notas[b])[0];
  const linhas = gp.ativas.map((k, pos): LinhaRegra => ({
    k, pos, rotulo: rotuloRegra(regraDe(k)), nota: gp.notas[k], disparos: gp.disparos[k] || 0,
    estado: k in gp.travas ? "travada" : gp.chipsRegra.includes(k) ? "chip" : "livre",
    delta: k in gp.posSemente ? gp.posSemente[k] - pos : null,
    candidataATroca: k === pior && gp.notas[k] < passo.limiar,
  }));
  return {
    nLutas: gp.nLutas, passo, capacidade: CV21.maxRegras[baseDe(gp.forma.est)], linhas,
    mudancas: gp.mudancas.slice(-quantas).reverse().map(x => ({ luta: x.luta, tipo: tipoMudanca(x), texto: x.texto })),
    travadas: Object.keys(gp.travas).filter(k => gp.ativas.includes(k)).map(k => rotuloRegra(regraDe(k))),
    vetadas: gp.vetos.map(k => ({ k, rotulo: rotuloRegra(regraDe(k)) })),
  };
}
