/* As chaves do produto (docs/TAREFA_V2_PRODUTO_FOME.md), ligadas no jogo web e desligadas na pesquisa: o jogo as grava no comeco do
   registro de cada ovo novo (o evento "p" do motor), e o replay as le de la. Os saves de antes nao tem o evento: seguem com as duas
   desligadas, a vida de sempre. Os gabaritos e as vidas da pesquisa nunca passam por aqui.
     - CHAMADO_PELA_FOME: o chamado de fome do bebe abre pela fome do corpo (CHAMADO_FOME_CORPO), e nao pelo relogio;
     - DECISAO_NA_COMIDA: a racao no chao faz o pet decidir ja no proximo passo, sem esperar o fim do intervalo de 15 min. */
import type { Motor } from "../motor/index.ts";

export const CHAMADO_PELA_FOME = true;
export const DECISAO_NA_COMIDA = true;

/** grava as chaves num ovo novo (pets v12; os de antes nao tem o mundo nem o corpo do v12). Devolve o mesmo motor */
export function ligarProduto(m: Motor): Motor {
  if (m.versao >= 12) m.ligarProduto({ chamadoPelaFome: CHAMADO_PELA_FOME, decisaoNaComida: DECISAO_NA_COMIDA });
  return m;
}
