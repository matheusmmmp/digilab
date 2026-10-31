/* T2 do tema dos menus (docs/TAREFA_V2_TEMA_MENUS.md §5): a escolha da pele em Ajustes > Aparencia, dois cartoes de previa no molde
   do tema do habitat (.mc-opcao--tema). Padrao radiogroup do WAI-ARIA: setas, Home e End movem e escolhem; so o cartao escolhido entra
   na ordem de Tab. A troca vale na hora (escolherPele muda o data-pele do <html>) e fica gravada; fora do save, do registro e do replay.
   Na tela so os nomes de NOME_PELE (TM2). A previa e desenhada em CSS (.mc-pele-prev, menus_config.css), com as cores fixas de cada pele. */
import { useRef, type KeyboardEvent } from "react";
import { indiceAbaPorTecla } from "../../componentes/hx/index.ts";
import { NOME_PELE, escolherPele, usePele, type Pele } from "../../pele.ts";
import { NOME_TEMA, type Tema } from "../../tema.ts";

export const PELES: readonly Pele[] = ["vidro", "xcom"];

/** resumo da linha "Aparencia" no menu de Ajustes: a pele e o tema */
export const resumoAparencia = (p: Pele, t: Tema): string => `pele ${NOME_PELE[p]} · tema ${t === "sistema" ? "do sistema" : NOME_TEMA[t].toLowerCase()}`;

export function EscolhaPele() {
  const pele = usePele(), refs = useRef<(HTMLButtonElement | null)[]>([]);
  function aoTecla(e: KeyboardEvent<HTMLButtonElement>, i: number) {
    const alvo = indiceAbaPorTecla(e.key, i, PELES.length);
    if (alvo === null) return;
    e.preventDefault();
    escolherPele(PELES[alvo]);
    refs.current[alvo]?.focus();
  }
  return (
    <>
      <h3 className="mc-sec" id="cfg-pele">Pele dos menus</h3>
      <div className="mc-opcoes mc-opcoes--2" role="radiogroup" aria-labelledby="cfg-pele">
        {PELES.map((p, i) => (
          <button type="button" key={p} ref={el => { refs.current[i] = el; }} role="radio" aria-checked={pele === p} tabIndex={pele === p ? 0 : -1}
            className={`mc-opcao mc-opcao--tema mc-opcao--pele-${p}`} onClick={() => escolherPele(p)} onKeyDown={e => aoTecla(e, i)}>
            <span className="mc-pele-prev" aria-hidden="true"><i /><i /><i /></span><b>{NOME_PELE[p]}</b>
          </button>
        ))}
      </div>
      <p className="mc-apoio">A pele vale nos menus e na tela do pet: painéis, barra, dock e janelas. O tema, logo abaixo, vale no habitat.</p>
    </>
  );
}
