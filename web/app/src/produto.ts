/* As chaves do produto (docs/TAREFA_V2_PRODUTO_FOME.md), ligadas no jogo web e desligadas na pesquisa: o jogo as grava no comeco do
   registro de cada ovo novo (o evento "p" do motor), e o replay as le de la. Os saves de antes nao tem o evento: seguem com as duas
   desligadas, a vida de sempre. Os gabaritos e as vidas da pesquisa nunca passam por aqui.
     - CHAMADO_PELA_FOME: o chamado de fome do bebe abre pela fome do corpo (CHAMADO_FOME_CORPO), e nao pelo relogio;
     - DECISAO_NA_COMIDA: a racao no chao faz o pet decidir ja no proximo passo, sem esperar o fim do intervalo de 15 min;
     - CHAMADOS_PELO_CORPO (docs/TAREFA_V2_PRODUTO_CUIDADO.md): os tres chamados do bebe abrem pelo corpo, com os limiares do bebe
       (CHAMADO_BEBE_CORPO; no bebe, o da fome no lugar do CHAMADO_FOME_CORPO). */
import type { Motor } from "../motor/index.ts";

export const CHAMADO_PELA_FOME = true;
export const DECISAO_NA_COMIDA = true;
export const CHAMADOS_PELO_CORPO = true;

/** grava as chaves num ovo novo (os pets v13, os unicos que abrem desde o descarte 6). Devolve o mesmo motor */
export function ligarProduto(m: Motor): Motor {
  m.ligarProduto({ chamadoPelaFome: CHAMADO_PELA_FOME, decisaoNaComida: DECISAO_NA_COMIDA, chamadosPeloCorpo: CHAMADOS_PELO_CORPO });
  return m;
}
