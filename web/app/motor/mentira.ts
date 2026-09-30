/* Moldes da mentira (espelho de digilab_fala_livre/mentira.py; DESIGN_VOZ_PROPRIA, secao 9). A mentira e decidida pelo
   motor (janela de fala com falso); aqui so o texto falso de um fato verdadeiro, por molde fixo. Sem o servidor, a
   fala do pet e este molde (ou o texto do assunto, quando e verdade). Conferido contra o Python (test/voz.test.ts). */
import { CUIDADO_DONO, PET_EU, PET_INF, TEXTO_PERIODO, rivalPadrao, type FatoHistoria, type Periodo } from "./historia.ts";

export const LIMIAR_REAL = .35;                    /* = CED.limiarReal (necessidade abaixo disto e real) */
const NEGA: Record<string, string> = { fome: "estou cheio, nem quero comer", higiene: "estou limpinho", energia: "estou cheio de energia",
  humor: "estou muito feliz", saude: "estou ótimo, nada dói" };
const FINGE: Record<string, string> = { fome: "estou morrendo de fome", humor: "estou muito triste", higiene: "estou todo sujo",
  energia: "estou morto de cansaço", saude: "estou doente" };
const ORDEM = ["fome", "humor", "higiene", "energia", "saude"];
const nivel = (v: number) => (v < .34 ? "baixo" : v < .67 ? "medio" : "alto");

/** mentira sobre o estado: nega a necessidade mais baixa (abaixo do limiar) ou, com tudo em dia, finge uma */
export function mentiraDeEstado(est: Record<string, number>): { verdade: string; falsa: string; molde: string } {
  const tem = ORDEM.filter(n => n in est);
  if (!tem.length) return { verdade: "estado não informado", falsa: FINGE.fome, molde: "estado:finge:fome" };
  let k = ORDEM[0], melhor = Infinity;
  for (const n of ORDEM) { const v = n in est ? est[n] : 2; if (v < melhor) { melhor = v; k = n; } }
  if (est[k] < LIMIAR_REAL) return { verdade: `${k} ${nivel(est[k])}`, falsa: NEGA[k], molde: `estado:nega:${k}` };
  const f = tem[0];
  return { verdade: `${f} ${nivel(est[f])}`, falsa: FINGE[f], molde: `estado:finge:${f}` };
}

/** molde por regra da historia (null: a regra nao admite distorcao) */
export function mentiraDeHistoria(regra: string, d: Record<string, unknown>): string | null {
  const s = (k: string) => (typeof d[k] === "string" ? (d[k] as string) : "");
  if (regra === "demora") return d.rapido ? "você nunca me atende" : "você sempre me atende na hora";
  if (regra === "periodo_dono" && s("periodo") in TEXTO_PERIODO) return `você nunca aparece ${TEXTO_PERIODO[s("periodo") as Periodo]}`;
  if (regra === "cuidado_dono" && s("acao") in CUIDADO_DONO) return `você nunca quer ${CUIDADO_DONO[s("acao")]}`;
  if (regra === "cede_manha") return "você nunca cede quando faço manha";
  if (regra === "gosto" && s("acao") in PET_INF) return `odeio ${PET_INF[s("acao")]}`;
  if (regra === "desgosto" && s("acao") in PET_INF) return `adoro ${PET_INF[s("acao")]}`;
  if (regra === "treino_favorito" && s("exercicio")) return `odeio treinar ${s("exercicio").replace(/_/g, " ")}`;
  if ((regra === "revanche" || regra === "venceu_depois" || regra === "primeira_derrota") && s("rival")) return `eu venci ${s("nome") || rivalPadrao(s("rival"))} fácil`;   /* nome: o do jogo, quando vem */
  if (regra === "primeira_vitoria") return "nunca venci uma luta";
  if (regra === "lesao") return d.tratada ? "me machuquei e ninguém me tratou" : "nunca me machuquei";
  if (regra === "ausencia") return "você nunca some";
  if (regra === "sombria") return "nunca virei sombrio";
  if (regra === "sequencia" && s("a") in PET_INF && s("b") in PET_EU) return `nunca ${PET_EU[s("b")]} depois de ${PET_INF[s("a")]}`;
  if (regra === "periodo" && s("acao") in PET_EU && s("periodo") in TEXTO_PERIODO)
    return `${TEXTO_PERIODO[s("periodo") as Periodo]} eu quase não ${PET_EU[s("acao")]}`;
  return null;
}

/** o primeiro fato distorcivel da lista (na ordem dada) */
export function distorcivel(fatos: FatoHistoria[]): FatoHistoria | null {
  return fatos.find(f => mentiraDeHistoria(f.regra, f.dados) !== null) ?? null;
}
