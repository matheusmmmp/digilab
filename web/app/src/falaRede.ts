/* CONVERSA_PET, DC2b (decisao DR-1 do Matheus, 2026-11-06: a fala nasce da rede, a LLM so como voz): o que a pagina manda ao servidor com a chave
   "Fala pela rede (teste)" ligada. Sao SO os conceitos do `dec-v2` da ultima decisao do modular (Motor.conceitosDec) e a identidade do pet (estagio
   e forma, para o estilo da especie): nenhum `estadoDoPet`, log, memoria do Bandit nem desejo. Apresentacao pura: nada daqui escreve no pet. */
import { nomeForma, type ConceitosDec, type Motor } from "../motor/index.ts";

/** as classes de objeto que o servidor aceita como `alvo` (digilab_fala_livre/conceitos.py CLASSES_OBJETO) */
const CLASSES_ALVO = ["racao", "a", "b", "c", "podre", "bola"];
const ALVO_EPISODIO = /^ep[0-9]{1,6}$/;

/** o alvo so vai se for de catalogo da voz (uma classe de objeto ou `ep<N>`). A `fome` do DC1 pode trazer o tipo da opcao (`comida`, `cheiro`),
    que nao e do catalogo: o servidor responderia 400; a pagina tira o alvo, que nao muda o que a fome quer dizer (D-CP-DC2b-5). */
export function alvoDeCatalogo(alvo: string | undefined): string | undefined {
  return alvo !== undefined && (CLASSES_ALVO.includes(alvo) || ALVO_EPISODIO.test(alvo)) ? alvo : undefined;
}

/** o campo `conceitos` do pedido, do dec-v2 da ultima decisao do modular; null se o pet nao tem decisao do modular (a chave nao muda nada) */
export function conceitosDaVoz(m: Motor): { versao: string; k: number; intencao: string; conceitos: Record<string, unknown>[] } | null {
  const c: ConceitosDec | null = m.conceitosDec("dec-v2");
  if (c === null) return null;
  return {
    versao: c.versao, k: c.k, intencao: c.intencao,
    conceitos: c.conceitos.map(x => {
      const alvo = alvoDeCatalogo(x.alvo);
      return { nome: x.nome, valor: x.valor, confianca: x.confianca, ...(alvo !== undefined ? { alvo } : {}), ...(x.episodio !== undefined ? { episodio: x.episodio } : {}) };
    }),
  };
}

/** o unico estado do pedido da voz: {identidade: {estagio, forma}} */
export function estadoDaVoz(m: Motor): { identidade: { estagio: string; forma: string } } {
  return { identidade: { estagio: m.forma.est, forma: nomeForma(m.forma).slice(0, 60) } };
}

/** os fatos que a verificacao aceita com `conceitos`: so os [J] "o dono me disse", {id, tipo, texto} */
export function fatosDoDono(fatos: unknown): { id: string; tipo: string; texto: string }[] {
  if (!Array.isArray(fatos)) return [];
  return fatos.filter((f): f is Record<string, string> => typeof f === "object" && f !== null && (f as Record<string, unknown>)["tipo"] === "o dono me disse")
    .map(f => ({ id: f["id"]!, tipo: f["tipo"]!, texto: f["texto"]! }));
}
