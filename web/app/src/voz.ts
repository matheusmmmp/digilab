/* Voz propria dos pets v7 (DESIGN_VOZ_PROPRIA, secoes 3, 9 e 10). So APRESENTACAO, fora uma coisa: a fala espontanea
   entra no registro do pet pelo evento "fl" (motor.falar), porque ela abre a janela de fala e pode ser mentira (decidido
   no motor). O texto vem do servidor (voz: prompt livre-v6, verificador que marca invencoes) ou, sem ele, do molde: o
   texto do assunto (verdade) ou a mentira do motor/mentira.ts.

   Gatilhos (secao 3): reencontro (o dono volta depois de >= 3 h sem agir), habito novo (um fato H ou O aparece pela
   primeira vez), aniversario (1 dia de jogo depois de uma evolucao), marco (evolucao, lesao tratada, vitoria sobre um
   desafio da campanha), luta e vontade nova (os de antes). Ritmo: no maximo 1 fala a cada 2 h de jogo, nunca com
   janela aberta nem dormindo; o bebe so faz emote (nao fala). A revanche (antes de lutar contra o rival da revanche)
   ficou para depois: a luta nao passa por aqui. */
import { CMEN, TPD, desvioPorAcao, distorcivel, escolherAssunto, extrair, mentiraDeEstado, mentiraDeHistoria, registroDoMotor,
  selecionar, type FatoHistoria, type Janela, type Motor } from "../motor/index.ts";
import { CHAVE } from "./save.ts";

export const RITMO_MIN = 120;                     /* no maximo 1 fala espontanea a cada 2 h de jogo */
export const REENCONTRO_MIN = 180;
const EXTRAIR_A_CADA_MIN = 30;                    /* o extrator roda no maximo a cada 30 min de jogo */
const INTERNET = CHAVE + "-internet";
export const TEXTO_GATILHO: Record<string, string> = {
  reencontro: "o dono voltou depois de um tempo sumido", habito_novo: "percebi um hábito novo",
  aniversario: "faz um dia que evoluí", marco: "acabou de acontecer uma coisa marcante",
  luta: "acabei de lutar", vontade: "tive uma vontade nova",
};

/** preferencia "o pet comenta coisas da internet" (fora do save; ligada por padrao) */
export function internetLigada(): boolean { try { return localStorage.getItem(INTERNET) !== "0"; } catch { return true; } }
export function ligarInternet(on: boolean): void { try { localStorage.setItem(INTERNET, on ? "1" : "0"); } catch { /* sem armazenamento */ } }

/* ------------------------------------------------ estado dos gatilhos (so memoria da pagina; recomeca ao carregar) */
interface Visto { semente: number; nDono: number; ultDono: number; nEvo: number; nLutas: number; tratadas: number; campanha: number;
  desejo: string; chaves: Set<string> | null; tExtr: number; aniversarios: Set<number> }
let V: Visto | null = null;
const tickUltimaFala = (m: Motor): number => { for (let i = m.log.length - 1; i >= 0; i--) if (m.log[i][1] === "fl") return m.log[i][0] as number; return -Infinity; };
const donos = (m: Motor): number[] => m.log.filter(e => e[1] === "d").map(e => e[0] as number);
const somaCampanha = (m: Motor): number => Object.values(m.campanha).reduce((a, b) => a + b, 0);

function fatosDe(m: Motor, comGostos: boolean): FatoHistoria[] {
  return extrair(registroDoMotor(m, comGostos && m.versao >= 3 ? desvioPorAcao(m) : []));
}
function chavesHabito(fatos: FatoHistoria[]): Set<string> { return new Set(fatos.filter(f => f.tipo === "H" || f.tipo === "O").map(f => f.chave)); }

function olhar(m: Motor): Visto {
  const d = donos(m), dz = m.dz?.atual;
  return { semente: m.semente, nDono: d.length, ultDono: d.length ? d[d.length - 1] : 0, nEvo: m.evolucoes.length,
    nLutas: m.log.filter(e => e[1] === "l").length, tratadas: m.lutas?.tratadas ?? 0, campanha: somaCampanha(m),
    desejo: dz ? dz.tipo + ":" + dz.alvo : "", chaves: null, tExtr: -Infinity, aniversarios: new Set() };
}

/** o gatilho de agora, ou null. Atualiza o que ja foi visto (chamar a cada mudanca do pet) */
export function gatilhoDe(m: Motor): string | null {
  if (m.versao < 7) return null;
  if (!V || V.semente !== m.semente) { V = olhar(m); return null; }            /* ao carregar: so observa */
  const a = olhar(m), t = m.e.tick;
  let g: string | null = null;
  if (a.nDono > V.nDono && V.nDono > 0 && donos(m)[V.nDono] - V.ultDono >= REENCONTRO_MIN) g = "reencontro";
  if (a.nEvo > V.nEvo || a.tratadas > V.tratadas || a.campanha > V.campanha) g = g ?? "marco";
  if (a.nLutas > V.nLutas) g = g ?? "luta";
  for (const ev of m.evolucoes) if (t >= ev.tick + TPD && !V.aniversarios.has(ev.tick)) { V.aniversarios.add(ev.tick); if (t < ev.tick + TPD + 60) g = g ?? "aniversario"; }
  if (a.desejo && a.desejo !== V.desejo) g = g ?? "vontade";
  if (t - V.tExtr >= EXTRAIR_A_CADA_MIN) {
    const ch = chavesHabito(fatosDe(m, false));
    if (V.chaves && [...ch].some(k => !V!.chaves!.has(k))) g = g ?? "habito_novo";
    V.chaves = ch; V.tExtr = t;
  }
  Object.assign(V, { nDono: a.nDono, ultDono: a.ultDono, nEvo: a.nEvo, nLutas: a.nLutas, tratadas: a.tratadas, campanha: a.campanha, desejo: a.desejo });
  return g;
}

/** pode falar agora? (ritmo, janela, sono, estagio) */
export function podeFalar(m: Motor): boolean {
  return m.versao >= 7 && !m.morte && m.estagioAtual !== "bebe" && !m.janelaAberta() && !m.e.dormindo
    && m.e.tick - tickUltimaFala(m) >= RITMO_MIN;
}

/* ------------------------------------------------ o que o pet diz */
export interface AssuntoFala { historia: Record<string, unknown>[]; mentira: { tema: string } | null; chaves: string[];
  verdade: string | null; molde: string }
const paraFato = (f: FatoHistoria) => ({ tipo: f.tipo, regra: f.regra, chave: f.chave, texto: f.texto, dados: f.dados });
const frase = (t: string) => t[0].toUpperCase() + t.slice(1) + (/[.!?]$/.test(t) ? "" : ".");

/** o assunto da fala espontanea (o codigo escolhe; a LLM so escreve) e o texto de queda (sem servidor) */
export function assuntoDaFala(m: Motor, j: Janela, dadosRecentes: string[][]): AssuntoFala {
  const fatos = fatosDe(m, true);
  const e = { fome: 1 - m.e.fome, higiene: m.e.higiene, energia: m.e.energia, humor: m.e.humor, saude: m.e.saude };
  if (j.falso && j.pedido === "historia") {
    const alvo = distorcivel(selecionar(fatos, dadosRecentes));
    if (alvo) return { historia: [paraFato(alvo)], mentira: { tema: "historia" }, chaves: [alvo.chave], verdade: alvo.texto,
      molde: frase(mentiraDeHistoria(alvo.regra, alvo.dados)!) };
  }
  if (j.falso) {                                   /* estado (ou historia sem fato distorcivel: cai no estado, como o Python) */
    const me = mentiraDeEstado(e);
    return { historia: [], mentira: { tema: j.pedido === "historia" ? "historia" : "estado" }, chaves: [], verdade: me.verdade, molde: frase(me.falsa) };
  }
  const a = escolherAssunto(fatos, dadosRecentes);
  return a ? { historia: [paraFato(a)], mentira: null, chaves: [a.chave], verdade: null, molde: frase(a.texto) }
    : { historia: [], mentira: null, chaves: [], verdade: null, molde: "…" };
}

/** fatos da historia para a CONVERSA (a selecao inteira, sem mentira) */
export function historiaDaConversa(m: Motor, citados: string[][]): Record<string, unknown>[] {
  return m.versao >= 7 ? selecionar(fatosDe(m, true), citados).map(paraFato) : [];
}
export const JANELA_FALA_MIN = CMEN.janela;
