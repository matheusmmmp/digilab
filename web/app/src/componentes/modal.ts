/* Modais (DIRETRIZES_REPLICAR, secao 7): <dialog> com showModal() (o resto da pagina fica inerte, entao o foco fica
   preso no modal), Esc fecha (evento cancel do navegador) e, ao fechar, o foco volta para quem abriu. Um modal por vez:
   se ja houver um aberto, o novo espera o outro fechar. */
const abertos: HTMLDialogElement[] = [];

/** abre o dialogo como modal e devolve o foco ao elemento que estava focado antes, quando ele fechar */
export function abrirModal(d: HTMLDialogElement | null, voltarPara?: () => HTMLElement | null): void {
  if (!d || d.open) return;
  const antes = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  d.showModal();
  /* o botão marcado com data-autofocus recebe o foco ao abrir: o React não escreve o atributo autofocus no HTML (o autoFocus
     dele foca ao montar, com o dialogo ainda fechado), então o showModal sozinho focaria o primeiro botão */
  d.querySelector<HTMLElement>("[data-autofocus]")?.focus();
  abertos.push(d);
  d.addEventListener("close", () => {
    abertos.splice(abertos.indexOf(d), 1);
    const alvo = voltarPara?.() ?? antes;
    if (alvo && alvo.isConnected) alvo.focus();
  }, { once: true });
}
export const haModalAberto = (): boolean => abertos.length > 0;

/** tela cheia com rota propria (secao 7: #/inicio, #/evolucao): enquanto aberta o endereco e o dela; ao fechar volta o
    de antes, se ninguem tiver navegado. Troca por replaceState: nao cria entrada no historico. */
export function rotaDaTelaCheia(endereco: string): () => void {
  const antes = location.hash;
  if (antes !== endereco) history.replaceState(null, "", endereco);
  return () => { if (location.hash === endereco && antes !== endereco) history.replaceState(null, "", antes); };
}
