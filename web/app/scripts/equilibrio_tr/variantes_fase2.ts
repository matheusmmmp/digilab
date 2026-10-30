/* as variantes da grade da fase 2 (fase2_formas.ts --variante <nome>): cada uma devolve as listas que troca, por cima das da rodada.
   So as sementes de calibracao. As listas de partida sao as de hoje (sementeDe, as dos pets v13) */
import { ADOL_V21, BOTS_V21, CRIANCA_V21, CV21E_TR, GAMBITS_SOMBRIA, LISTAS_V14_R1, gambitsAdulto, Cd, Rg, validarLista, type FormaAdultaNormal, type ListaGambits, type Regra } from "../../motor/index.ts";

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

/* segunda rodada (docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md, R2-1): as variantes por cima das candidatas da primeira rodada (LISTAS_V14_R1 ou,
   sem ela, a lista de hoje). A escolhida (r2c_b) entrou nas LISTAS_V14; as grades se refazem com fase2_formas.ts --listas v14r1. Rodada 1: uma mudanca so por variante */
const v14 = (f: string): ListaGambits => LISTAS_V14_R1[f] ?? (f in ADOL_V21 ? ADOL_V21[f as keyof typeof ADOL_V21]
  : f in CRIANCA_V21 ? CRIANCA_V21[f as keyof typeof CRIANCA_V21] : gambitsAdulto(f as FormaAdultaNormal, CV21E_TR));
/* o vigia e o tita: a pele dura de perto so com mais Guts (o espelho do vigia nao trava no limite; o tita deixa de segurar tudo) */
const vigiaPele60 = () => trocar(v14("vigia"), Rg([D0, GA(40)], "pele_dura"), Rg([D0, GA(60)], "pele_dura"));
const vigiaSemPele = () => trocar(v14("vigia"), Rg([D0, GA(40)], "pele_dura"), null);
const titaPele60 = () => trocar(v14("tita"), Rg([D0, GA(40)], "pele_dura"), Rg([D0, GA(60)], "pele_dura"));
const titaSemPelePrep = () => trocar(v14("tita"), Rg(PREP, "pele_dura"), null);
/* as de longe: atiram em quem avanca em vez de recuar (a sentinela sem os dois recuos pela leitura; o emboscador sem o recuo do medio) */
const sentAtira = () => trocar(trocar(v14("sentinela"), Rg(Cd("oponente_repete", "avancar", 2), "recuar"), null), Rg(FQ("investida"), "recuar"), null);
const embAtira = () => trocar(v14("emboscador"), Rg([D1, FQ("avancar")], "recuar"), null);
/* o espelho anda do medio (so andava do longe) */
const espelhoAnda = () => validarLista({ regras: [...v14("espelho").regras, Rg(D1, "avancar")], final: v14("espelho").final });
/* a muralha sem o contra-golpe na investida frequente */
const muralhaSemInv = () => trocar(v14("muralha"), Rg(FQ("investida"), "contra_golpe"), null);
/* o cacador do Champion recua menos (sem o recuo do medio) */
const cacadorFica = () => trocar(v14("cacador"), Rg(D1, "recuar"), null);
/* o sereno do Rookie so bate com mais Guts */
const sereno40 = () => trocar(v14("sereno"), Rg([D0, GA(20)], "golpe_rapido"), Rg([D0, GA(40)], "golpe_rapido"));
/* o bastiao devolve so com mais Guts; o predador nao avanca de longe sem Guts (dispara do medio) */
const bastiao60 = () => trocar(v14("bastiao_rachado"), Rg([D0, GA(40)], "contra_golpe"), Rg([D0, GA(60)], "contra_golpe"));
const predadorFica = () => trocar(v14("predador"), Rg(D2, "avancar"), null);
/* o duelista: a investida do medio so com Guts (sem ele, defende) */
const duelistaInv = () => trocar(v14("duelista"), Rg(D1, "investida"), Rg([D1, GA(40)], "investida"));
/* rodada 2 da R2-1: as mudancas compostas (cada uma recebe as listas da variante e devolve as que troca) */
type Mod = (L: Record<string, ListaGambits>) => Record<string, ListaGambits>;
const de = (L: Record<string, ListaGambits>, f: string): ListaGambits => L[f] ?? v14(f);
const compor = (...ms: Mod[]) => (): Record<string, ListaGambits> => ms.reduce((L, m) => ({ ...L, ...m(L) }), {} as Record<string, ListaGambits>);
/** troca de lugar duas regras da lista (a primeira passa para onde estava a segunda) */
function trocarOrdem(g: ListaGambits, a: Regra, b: Regra): ListaGambits {
  const ia = g.regras.findIndex(r => chave(r) === chave(a)), ib = g.regras.findIndex(r => chave(r) === chave(b));
  if (ia < 0 || ib < 0) throw new Error("regra nao encontrada para trocar a ordem");
  const regras = [...g.regras]; [regras[ia], regras[ib]] = [regras[ib], regras[ia]];
  return validarLista({ regras, final: g.final });
}
const mVigia: Mod = () => ({ vigia: vigiaPele60() });
const mSereno: Mod = () => ({ sereno: sereno40() });
const mDuelista: Mod = () => ({ duelista: duelistaInv() });
const mBastiao: Mod = () => ({ bastiao_rachado: bastiao60() });
const mCacador: Mod = () => ({ cacador: cacadorFica() });
const mMuralha: Mod = () => ({ muralha: muralhaSemInv() });
/* as de longe disparam antes de marcar */
const mLongeDispara: Mod = L => Object.fromEntries((["sentinela", "emboscador"] as const).map(f => [f, trocarOrdem(de(L, f), Rg(GA(40), "marcar"), Rg(GA(20), "disparo"))]));
/* o espelho bate de perto com menos Guts */
const mEspelho: Mod = L => ({ espelho: trocar(de(L, "espelho"), Rg([D0, GA(60)], "golpe_rapido"), Rg([D0, GA(40)], "golpe_rapido")) });
/* o tita so prepara o pesado com mais Guts */
const mTita: Mod = L => ({ tita: trocar(de(L, "tita"), Rg([D0, GA(20)], "preparar_pesado"), Rg([D0, GA(40)], "preparar_pesado")) });
/* o cacador do Champion dispara sem marcar */
const mCacadorDispara: Mod = L => ({ cacador: trocar(de(L, "cacador"), Rg(GA(40), "marcar"), null) });
/* o predador dispara do longe antes de marcar */
const mPredador: Mod = L => ({ predador: trocarOrdem(de(L, "predador"), Rg([D2, GA(40)], "marcar"), Rg([D2, GA(20)], "disparo")) });
const B2 = [mVigia, mSereno, mDuelista, mBastiao, mCacador, mMuralha];
export const VARIANTES_R2_2: Record<string, () => Record<string, ListaGambits>> = {
  r2b_a: compor(mVigia, mLongeDispara),
  r2b_b: compor(...B2),
  r2b_c: compor(...B2, mLongeDispara),
  r2b_d: compor(...B2, mLongeDispara, mEspelho),
  r2b_e: compor(...B2, mLongeDispara, mTita),
  r2b_f: compor(...B2, mLongeDispara, mCacadorDispara),
  r2b_g: compor(...B2, mLongeDispara, mPredador),
  r2b_h: compor(...B2, mLongeDispara, mEspelho, mTita, mCacadorDispara, mPredador),
};
export const VARIANTES_R2: Record<string, () => Record<string, ListaGambits>> = {
  r2_vigia_pele60: () => ({ vigia: vigiaPele60() }),
  r2_vigia_sem_pele: () => ({ vigia: vigiaSemPele() }),
  r2_tita_pele60: () => ({ tita: titaPele60() }),
  r2_tita_sem_pele_prep: () => ({ tita: titaSemPelePrep() }),
  r2_sent_atira: () => ({ sentinela: sentAtira() }),
  r2_emb_atira: () => ({ emboscador: embAtira() }),
  r2_espelho_anda: () => ({ espelho: espelhoAnda() }),
  r2_muralha_sem_inv: () => ({ muralha: muralhaSemInv() }),
  r2_cacador_fica: () => ({ cacador: cacadorFica() }),
  r2_sereno40: () => ({ sereno: sereno40() }),
  r2_bastiao60: () => ({ bastiao_rachado: bastiao60() }),
  r2_predador_fica: () => ({ predador: predadorFica() }),
  r2_duelista_inv: () => ({ duelista: duelistaInv() }),
};

/* rodada 3 da R2-1: em cima da r2b_b */
/* as de longe so recuam de perto sem Guts (com ele, marcam e disparam de perto) */
const mLongeD0: Mod = L => Object.fromEntries((["sentinela", "emboscador"] as const).map(f => [f, trocar(de(L, f), Rg(D0, "recuar"), Rg([D0, GB(40)], "recuar"))]));
/* o cacador do Champion so bate de perto com Guts */
const mCacadorD0: Mod = L => ({ cacador: trocar(de(L, "cacador"), Rg(D0, "golpe_rapido"), Rg([D0, GA(40)], "golpe_rapido")) });
export const VARIANTES_R2_3: Record<string, () => Record<string, ListaGambits>> = {
  r2c_a: compor(...B2, mPredador),
  r2c_b: compor(...B2, mPredador, mEspelho),
  r2c_c: compor(...B2, mPredador, mLongeD0),
  r2c_d: compor(...B2, mPredador, mCacadorD0),
  r2c_e: compor(...B2, mPredador, mEspelho, mLongeD0, mCacadorD0),
  r2c_f: compor(...B2, mPredador, mEspelho, mCacadorD0),
};
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
  ...VARIANTES_R2,
  ...VARIANTES_R2_2,
  ...VARIANTES_R2_3,
};
