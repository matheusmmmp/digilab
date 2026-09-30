/* Acoes do dono a partir da interface: UM caminho so, usado pelos botoes da tela do Pet, pelos atalhos do Conversar e
   pelo comando do chat (TAREFA_COMANDO_CHAT). O motor grava o evento "d" de sempre (Motor.observar); aqui ficam so o
   flash do palco e a velocidade do chamado. Nada aqui le a LLM: o comando chega como texto e e validado contra o
   catalogo fechado (AcaoDono) e contra o estado do pet antes de virar o mesmo clique do botao. */
import { ACOES_DONO_V4, ACOES_EDUCACAO, type AcaoDono, type Motor } from "../motor/index.ts";
import { mostrarFlash } from "./flash.ts";
import { jogoAtual, mudarMotor } from "./jogo.ts";
import { ajustarVelocidadeChamado } from "./tempo.ts";

/** rotulo dos botoes (tela do Pet) e do chip do comando ("Alimentar?") */
export const ROTULO_DONO: Record<AcaoDono, string> = {
  alimentar: "Alimentar", limpar: "Limpar", brincar: "Brincar", acariciar: "Carinho", elogiar: "Elogiar", repreender: "Repreender",
  petisco: "Petisco", levar_ao_banheiro: "Banheiro", tratar_lesao: "Tratar",
};
/** o que o dono fez, no historico da conversa ("✓ alimentou") */
export const FEITO_DONO: Record<AcaoDono, string> = {
  alimentar: "alimentou", limpar: "limpou", brincar: "brincou", acariciar: "fez carinho", elogiar: "elogiou", repreender: "repreendeu",
  petisco: "deu petisco", levar_ao_banheiro: "levou ao banheiro", tratar_lesao: "tratou a lesão",
};
export const ICONE_DONO: Record<AcaoDono, string> = {
  alimentar: "carne", limpar: "brilho", brincar: "nota", acariciar: "coracao", elogiar: "coracao", repreender: "gota",
  petisco: "carne", levar_ao_banheiro: "brilho", tratar_lesao: "coracao",
};

/** o dono so age no pet nascido e vivo */
export const podeAgir = (m: Motor, nascendo: number): boolean => nascendo === 0 && !m.morte;

/** a acao do dono pela interface (o botao da tela do Pet, o atalho do Conversar, o toque no chip do comando): grava o
    evento "d" pelo motor, mostra o flash e ajusta a velocidade do chamado. Devolve false se o pet nao pode receber acao. */
export function agir(a: AcaoDono): boolean {
  const j = jogoAtual();
  if (!podeAgir(j.motor, j.nascendo)) return false;
  mudarMotor(mm => mm.observar(a));
  mostrarFlash(ICONE_DONO[a]);
  ajustarVelocidadeChamado();                  /* atendeu o chamado: volta a velocidade de antes */
  return true;
}

/** validacao do comando proposto pela LLM (a segunda, depois da do servidor): so o catalogo AcaoDono; pet nascido e vivo;
    as acoes v4 (petisco, banheiro, tratar lesao) so em pets versao >= 4; tratar_lesao so com lesao. Fora disso, null. */
/** so o catalogo fechado (as 9 acoes de AcaoDono): qualquer outra coisa vira null */
export const noCatalogo = (c: unknown): AcaoDono | null =>
  typeof c === "string" && (ACOES_DONO_V4 as readonly string[]).includes(c) ? c as AcaoDono : null;

export function validarComando(m: Motor, nascendo: number, c: unknown): AcaoDono | null {
  const a = noCatalogo(c);
  if (!a) return null;
  if (!podeAgir(m, nascendo)) return null;
  if (ACOES_EDUCACAO.includes(a) && m.versao < 4) return null;
  if (a === "tratar_lesao" && m.lesionadoDesde === null) return null;
  return a;
}
