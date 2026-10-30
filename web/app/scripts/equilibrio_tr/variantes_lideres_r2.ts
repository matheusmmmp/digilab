/* as variantes das listas dos lideres da fase R2-3 (docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md): fase4_progressao.ts --variante-lider <nome>. Cada
   uma devolve as listas candidatas dos lideres que troca (pela id da arena), por cima das de hoje. So as sementes de calibracao */
import { ARENAS, CV21E_TR, RELOGIO_V14, arenaDaLuta, lutadorBot, Cd, Rg, validarLista, type ListaGambits, type Regra } from "../../motor/index.ts";

const R = { ...CV21E_TR, relogio: RELOGIO_V14 };
const D0 = Cd("distancia_eh", 0), D1 = Cd("distancia_eh", 1), FQ = (a: string) => Cd("oponente_frequente", a), GA = (g: number) => Cd("guts_proprio_acima", g);
const T10 = Cd("turno_execucao", 10);
const chave = (r: Regra): string => JSON.stringify([r.se.map(c => [c.n, c.p]), r.entao]);
/** a lista de hoje do lider da arena (a do motor, com a arena dos pets v13) */
const hoje = (id: string): ListaGambits => { const a = ARENAS.find(x => x.id === id)!; return lutadorBot(a.lider, R, arenaDaLuta(a.lider, 13)!).estilo.gambits!; };
function trocar(g: ListaGambits, de: Regra, para: Regra | null): ListaGambits {
  const i = g.regras.findIndex(r => chave(r) === chave(de));
  if (i < 0) throw new Error("regra nao encontrada: " + chave(de));
  const regras = [...g.regras];
  if (para) regras[i] = para; else regras.splice(i, 1);
  return validarLista({ regras, final: g.final });
}
/** poe a regra na posicao i (a lista cabe em 8) */
const inserir = (g: ListaGambits, i: number, r: Regra): ListaGambits => validarLista({ regras: [...g.regras.slice(0, i), r, ...g.regras.slice(i)], final: g.final });

/* rodada 1: uma mudanca so por variante */
/* quem persegue (a Cidadela e a Espiral, a mesma lista): contra quem recua o tempo todo, carrega o Guts em vez de correr atras */
const carrega = (id: string) => inserir(hoje(id), 2, Rg(FQ("recuar"), "carregar"));
/* sem perseguir do medio */
const semMedio = (id: string) => trocar(hoje(id), Rg(D1, "avancar"), null);
/* o Lago: contra quem dispara, defende em vez de avancar */
const lagoDefende = () => trocar(hoje("lago"), Rg(FQ("disparo"), "avancar"), Rg(FQ("disparo"), "defender"));
const lagoCarrega = () => trocar(hoje("lago"), Rg(GA(20), "avancar"), Rg(FQ("recuar"), "carregar"));
/* a Floresta: de perto fica (sem o recuo); ou, na fase de briga, prepara o pesado (o contra-golpe do guardiao o devolve) */
const florestaFica = () => trocar(hoje("floresta"), Rg(D0, "recuar"), null);
const florestaPesado = () => trocar(hoje("floresta"), Rg([T10, GA(20)], "golpe_rapido"), Rg([T10, GA(20)], "preparar_pesado"));

/* rodada 2: lutas mais longas e com menos sorte (a diferenca do treino pesa mais) */
const EXF = Rg([Cd("executando_pesado"), FQ("esquivar")], "fintar");
/* contra quem dispara, defende (para de correr atras) */
const defende = (id: string) => inserir(hoje(id), 2, Rg(FQ("disparo"), "defender"));
/* sem a finta no pesado */
const semFinta = (id: string) => trocar(hoje(id), EXF, null);
/* o Lago nao persegue quem dispara */
const lagoSemPersegue = () => trocar(hoje("lago"), Rg(FQ("disparo"), "avancar"), null);
/* rodada 3: quem persegue so bate de perto (o golpe rapido de qualquer distancia vira so de perto) */
const soPerto = (id: string) => trocar(hoje(id), Rg(GA(20), "golpe_rapido"), Rg([D0, GA(20)], "golpe_rapido"));
const lagoSoPerto = () => trocar(hoje("lago"), Rg(GA(20), "avancar"), Rg(D1, "avancar"));
export const VARIANTES_LIDER: Record<string, () => Record<string, ListaGambits>> = {
  l1_cid_carrega: () => ({ cidadela: carrega("cidadela") }),
  l1_cid_sem_medio: () => ({ cidadela: semMedio("cidadela") }),
  l1_esp_carrega: () => ({ espiral: carrega("espiral") }),
  l1_esp_sem_medio: () => ({ espiral: semMedio("espiral") }),
  l1_lago_defende: () => ({ lago: lagoDefende() }),
  l1_lago_carrega: () => ({ lago: lagoCarrega() }),
  l1_flo_fica: () => ({ floresta: florestaFica() }),
  l1_flo_pesado: () => ({ floresta: florestaPesado() }),
  l2_cid_defende: () => ({ cidadela: defende("cidadela") }),
  l2_esp_defende: () => ({ espiral: defende("espiral") }),
  l2_cid_sem_finta: () => ({ cidadela: semFinta("cidadela") }),
  l2_esp_sem_finta: () => ({ espiral: semFinta("espiral") }),
  l2_lago_sem_persegue: () => ({ lago: lagoSemPersegue() }),
  l3_cid_so_perto: () => ({ cidadela: soPerto("cidadela") }),
  l3_esp_so_perto: () => ({ espiral: soPerto("espiral") }),
  l3_lago_so_perto: () => ({ lago: lagoSoPerto() }),
};
