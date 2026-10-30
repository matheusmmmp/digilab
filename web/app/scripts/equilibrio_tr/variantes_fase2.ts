/* as variantes da grade da fase 2 (fase2_formas.ts --variante <nome>): cada uma devolve as listas que troca, por cima das da rodada.
   So as sementes de calibracao. As listas de partida sao as de hoje (sementeDe, as dos pets v13) */
import { ADOL_V21, BOTS_V21, CRIANCA_V21, CV21E_TR, GAMBITS_SOMBRIA, gambitsAdulto, Cd, Rg, validarLista, type ListaGambits, type Regra } from "../../motor/index.ts";

const PREP = Cd("oponente_preparando"), D0 = Cd("distancia_eh", 0), D1 = Cd("distancia_eh", 1), D2 = Cd("distancia_eh", 2);
const GA = (g: number) => Cd("guts_proprio_acima", g), GB = (g: number) => Cd("guts_proprio_abaixo", g);
const chave = (r: Regra): string => JSON.stringify([r.se.map(c => [c.n, c.p]), r.entao]);
/** troca a regra `de` da lista por `para` (null tira); falha alto se a regra nao estiver la */
function trocar(g: ListaGambits, de: Regra, para: Regra | null): ListaGambits {
  const i = g.regras.findIndex(r => chave(r) === chave(de));
  if (i < 0) throw new Error("regra nao encontrada: " + chave(de));
  const regras = [...g.regras];
  if (para) regras[i] = para; else regras.splice(i, 1);
  return validarLista({ regras, final: g.final });
}
const LONGE = { sentinela: BOTS_V21.sentinela, emboscador: BOTS_V21.emboscador, cacador: ADOL_V21.cacador };
const cada = (f: (g: ListaGambits) => ListaGambits): Record<string, ListaGambits> =>
  Object.fromEntries(Object.entries(LONGE).map(([k, g]) => [k, f(g)]));
/* de perto, sem ter para onde recuar, a lista de longe bate (golpe rapido) no lugar de recuar */
const perto = (g: ListaGambits) => trocar(g, Rg(D0, "recuar"), Rg(D0, "golpe_rapido"));
/* contra o preparo de perto, o golpe rapido interrompe (no lugar da esquiva, que no tempo real cai antes do pesado) */
const interrompe = (g: ListaGambits) => trocar(g, Rg([PREP, D0], "esquivar"), Rg([PREP, D0], "golpe_rapido"));
/* o emboscador marca e dispara desde o comeco (sem esperar os 10 s) */
const emboscadorJa = (g: ListaGambits) => trocar(trocar(g, Rg(Cd("turno_execucao", 5), "marcar"), Rg(GA(40), "marcar")),
  Rg(Cd("turno_execucao", 5), "disparo"), Rg(GA(20), "disparo"));
/* o sereno do Rookie avanca de qualquer distancia (a regra "sempre -> avancar" nao vale de perto) */
const sereno = trocar(CRIANCA_V21.sereno, Rg(D2, "avancar"), Rg(Cd("sempre"), "avancar"));

/* rodada 2 */
const FQ = (a: string) => Cd("oponente_frequente", a);
/* o sereno bate primeiro e so carrega por ultimo (a paciencia fica na regra final, defender) */
const sereno2 = validarLista({ regras: [Rg([D0, GA(20)], "golpe_rapido"), Rg(Cd("sempre"), "avancar"), Rg(GB(40), "carregar")], final: "defender" });
const sereno3 = validarLista({ regras: [Rg([D0, GA(40)], "golpe_rapido"), Rg(Cd("sempre"), "avancar"), Rg(GB(40), "carregar")], final: "defender" });
/* o predador (a mira da sombria, sem recuar) dispara de onde estiver e so avanca de longe sem Guts */
const predador = validarLista({ regras: [Rg([D1, GA(20)], "disparo"), Rg([D2, GA(20)], "disparo"), Rg(D2, "avancar"), Rg(D0, "golpe_rapido")], final: "carregar" });
/* o bastiao rachado devolve o golpe de perto (o contra-golpe inteiro da passiva) */
const bastiao = validarLista({ regras: [Rg([D0, GA(20)], "contra_golpe"), Rg(GB(40), "carregar"), Rg(Cd("sempre"), "avancar")], final: "defender" });
/* a muralha nao devolve sozinha todo golpe rapido frequente */
const muralhaA = () => trocar(gambitsAdulto("muralha", CV21E_TR), Rg(FQ("golpe_rapido"), "contra_golpe"), null);
const r2a = (): Record<string, ListaGambits> => ({ cacador: perto(ADOL_V21.cacador), sentinela: interrompe(BOTS_V21.sentinela),
  emboscador: interrompe(emboscadorJa(BOTS_V21.emboscador)), sereno: sereno2, predador, bastiao_rachado: bastiao });
void GAMBITS_SOMBRIA;
/* rodada 3 */
/* a muralha so devolve o golpe rapido frequente com Guts para isso */
const muralhaB = () => trocar(gambitsAdulto("muralha", CV21E_TR), Rg(FQ("golpe_rapido"), "contra_golpe"), Rg([FQ("golpe_rapido"), GA(40)], "contra_golpe"));
const bastiao40 = validarLista({ regras: [Rg([D0, GA(40)], "contra_golpe"), Rg(GB(40), "carregar"), Rg(Cd("sempre"), "avancar")], final: "defender" });
/* o predador marca de longe antes de disparar */
const predador2 = validarLista({ regras: [Rg([D2, GA(40)], "marcar"), Rg([D1, GA(20)], "disparo"), Rg([D2, GA(20)], "disparo"), Rg(D2, "avancar"),
  Rg(D0, "golpe_rapido")], final: "carregar" });
/* o sereno como o arisco, mas com a regra final de defender (o parry contra o golpe rapido) */
const sereno4 = validarLista({ regras: [Rg(D2, "avancar"), Rg(D1, "avancar"), Rg([D0, GA(20)], "golpe_rapido")], final: "defender" });
/* o tita sem a pele dura contra o preparo (fica a esquiva) */
const titaA = () => trocar(gambitsAdulto("tita", CV21E_TR), Rg(PREP, "pele_dura"), null);
const r3base = (): Record<string, ListaGambits> => ({ ...r2a(), bastiao_rachado: bastiao40, predador: predador2, sereno: sereno4 });

export const VARIANTES: Record<string, () => Record<string, ListaGambits>> = {
  perto: () => cada(perto),
  interrompe: () => cada(interrompe),
  perto_interrompe: () => cada(g => interrompe(perto(g))),
  embosc: () => ({ emboscador: emboscadorJa(BOTS_V21.emboscador) }),
  perto_embosc: () => ({ ...cada(perto), emboscador: emboscadorJa(perto(BOTS_V21.emboscador)) }),
  sereno: () => ({ sereno }),
  r2a,
  r2b: () => ({ ...r2a(), muralha: muralhaA() }),
  r2c: () => ({ ...r2a(), sereno: sereno3 }),
  r3a: () => ({ ...r3base(), muralha: muralhaB() }),
  r3b: () => ({ ...r3base(), muralha: muralhaB(), tita: titaA() }),
  r3c: () => ({ ...r3base(), muralha: muralhaA() }),
  r3d: () => ({ ...r3base(), muralha: muralhaA(), tita: titaA() }),
  r2d: () => ({ ...r2a(), muralha: muralhaA(), emboscador: interrompe(perto(emboscadorJa(BOTS_V21.emboscador))) }),
};
