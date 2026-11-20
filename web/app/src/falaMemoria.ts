/* A fidelidade da fala com a memoria autobiografica (C4, M6; docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, 7.1, e a MA-8).
   Espelho de digilab_fala_livre/memoria_fala.py, conferido contra test/gabaritos/fala_memoria_python.json. A fala so alega lembranca
   (Q1), causa por memoria (Q2) e mudanca de faceta (Z) que o REGISTRO sustenta; a conferencia e deterministica, sem LLM. So roda
   quando o bloco de fatos tem o fato Q1 (a `memoria_autobio` ligada): o A v11 do jogo nao tem, e a fala dele segue como sempre. */
export interface FatoFala { id: string; tipo: string; texto: string }
export interface Alegacao { tipo: "lembranca" | "causa" | "faceta"; trecho: string; faceta?: string; sentido?: "subiu" | "desceu" }
export interface AlegacaoConferida extends Alegacao { sustentada: boolean; fato: string | null }

export const TIPO_LEMBRANCA = "lembranca autobiografica", TIPO_SEM_LEMBRANCA = "sem lembranca autobiografica";
export const TIPO_DECIDIU = "lembranca que decidiu", TIPO_FACETA = "mudanca de faceta";

const LEMB = /\b(lembr\w*|recordo|recorda\w*)\b/, CAUSA = /\b(porque|por causa|pois|ja que|por isso|gracas a|entao)\b/;
const NEGACAO = /\bnao (me )?(lembr|recordo)/, FACETA = /\b(mais|menos)\s+(cautel\w*|cuidados\w*|apeg\w*|ousad\w*|corajos\w*|aventure\w*)/;
const FACETA_DA_RAIZ: [string, string][] = [["cautel", "cautela_comida"], ["cuidados", "cautela_comida"], ["apeg", "apego_dono"],
  ["ousad", "ousadia_longe"], ["corajos", "ousadia_longe"], ["aventure", "ousadia_longe"]];
const SUFIXOS = ["ando", "endo", "indo", "ar", "er", "ir", "ei", "ou", "eu", "iu", "i", "o", "a", "e"];
const NEUTRAS = ["lembr", "recor", "porq", "caus", "isso", "pois", "entao", "gracas", "episod", "mudou", "agora", "negativ", "positiv"];

export const norm = (t: string): string => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const raiz = (p: string): string => {
  for (const suf of SUFIXOS) if (p.endsWith(suf) && p.length - suf.length >= 3) return p.slice(0, -suf.length);
  return p;
};
const raizes = (t: string): Set<string> => new Set((norm(t).match(/[a-z]+/g) || []).filter(w => w.length >= 4).map(raiz)
  .filter(r => !NEUTRAS.some(n => r.startsWith(n))));

export const alegaLembranca = (trecho: string): boolean => LEMB.test(norm(trecho));
export const memoriaLigada = (fatos: FatoFala[]): boolean => fatos.some(f => f.tipo === TIPO_LEMBRANCA || f.tipo === TIPO_SEM_LEMBRANCA);

export function alegacoes(fala: string): Alegacao[] {
  const out: Alegacao[] = [];
  for (let oracao of norm(fala).split(/[.!?;\n]+/)) {
    if (NEGACAO.test(oracao)) oracao = oracao.split(",").filter(p => !NEGACAO.test(p)).join(",");
    oracao = oracao.trim();
    if (!oracao) continue;
    if (LEMB.test(oracao)) out.push({ tipo: CAUSA.test(oracao) ? "causa" : "lembranca", trecho: oracao });
    const m = FACETA.exec(oracao);
    if (m) out.push({ tipo: "faceta", trecho: oracao, faceta: FACETA_DA_RAIZ.find(([r]) => m[2].startsWith(r))![1], sentido: m[1] === "mais" ? "subiu" : "desceu" });
  }
  return out;
}

/** o que o registro do A v11 tem para sustentar "lembrei de X" (memoria_fala.py, TIPOS_REGISTRO_A) */
const TIPOS_REGISTRO_A = ["memoria", "habito meu", "habito do dono", "gosto", "marco"];

/** cada alegacao com `sustentada` e o `fato` que a sustenta. Com a memoria ligada, as tres; sem ela (A v11, MA-8), o modo simples:
    so lembranca (fato [M] ou de historia) e causa (so o fato Q2, que ali nao existe: a causa por lembranca e recusada), nunca faceta */
export function conferirFalaMemoria(fala: string, fatos: FatoFala[]): AlegacaoConferida[] {
  const simples = !memoriaLigada(fatos);
  return alegacoes(fala).filter(a => !(simples && a.tipo === "faceta")).map(a => {
    let fato: string | null = null;
    if (a.tipo === "faceta") {
      const chave = norm(a.faceta!).replace(/_/g, " ");
      fato = fatos.find(f => f.tipo === TIPO_FACETA && norm(f.texto).includes(chave) && norm(f.texto).includes(a.sentido!))?.id ?? null;
    } else {
      const pal = raizes(a.trecho);
      const tipos = a.tipo === "causa" ? [TIPO_DECIDIU] : simples ? TIPOS_REGISTRO_A : [TIPO_LEMBRANCA];
      fato = fatos.find(f => tipos.includes(f.tipo) && [...raizes(f.texto)].some(r => pal.has(r)))?.id ?? null;
    }
    return { ...a, sustentada: fato !== null, fato };
  });
}
