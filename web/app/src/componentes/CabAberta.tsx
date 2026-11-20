/* Cabecalho das telas que abrem sozinhas (TAREFA_V2_LAYOUT_HABITAT, M6): a faixa de titulo da pele XCOM (hachura + caixa alta)
   dentro do dialogo; o titulo da tela segue no h1/h2 do proprio conteudo (os ids dos aria-labelledby nao mudam). */
export function CabAberta({ titulo }: { titulo: string }) {
  return <div className="hx-painel__cab ab-cab" aria-hidden="true"><span className="hx-painel__titulo">{titulo}</span></div>;
}
