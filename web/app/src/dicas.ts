/* Tutorial contextual (docs/JORNADA_JOGADOR.md, aprovado): o Bit, zelador do laboratorio (personagem original), diz
   UMA frase no momento em que a mecanica aparece; some ao tocar em Entendi e nao volta. Do adulto em diante ele se
   despede e o proprio pet explica (a revelacao ja traz o porque). Preferencia e dicas vistas em chaves proprias: o
   save do pet nao muda. */
import { useEffect, useState } from "react";
import { CHAVE } from "./save.ts";

/** nome na tela do mentor do tutorial (nomes em Digimon; antes "Bit", decisao do Matheus em 2026-09-29) */
export const NOME_MENTOR = "Professor Agumon";
export const CHAVE_DICAS = CHAVE + "-dicas";          // ids das dicas ja vistas
export const CHAVE_DICAS_LIGADAS = CHAVE + "-dicas-ligadas";

/** o texto de cada momento da jornada (uma mecanica por vez) */
export const DICAS = {
  ovo: "É seu. Ele só vive com o jogo aberto: fechar o jogo pausa o tempo dele.",
  chamado: "Ele está chamando! Toque no botão certo em até 15 min. Enquanto chama, o tempo anda em 1x.",
  rookie: "Virou Rookie. A sala de treino fica em Crescer · Treinar, e o primeiro rival da Campina pede treino.",
  ensinar: "Elogie ou repreenda o que ele ACABOU de fazer: vale por 2 min e muda a vontade dele numa situação parecida.",
  /* pets v11: sem elogio nem bronca; ele aprende pelo corpo, e o carinho e o tapa sao gestos */
  ensinar_v11: "Ele aprende sozinho com o que as próprias ações fazem no corpo dele. O carinho acalma; o tapa diz que você não gostou do que ele ACABOU de fazer.",
  derrota_campanha: "Faltou força: treine e volte. Cada ponto treinado aumenta o tamanho dele na campanha.",
  champion: "Virou Champion. Com fadiga 40 ele pede pausa; com 60 o treino vira Forçar: rende mais e gera sobrecarga.",
  regra_nova: "Ele tirou uma regra da luta. Travar a mantém na posição; Vetar proíbe. O resto ele aprende sozinho.",
  lutas_treino: "Para virar Ultimate ele precisa de 10 lutas de treino na Arena, além do tempo.",
  /* pets v5 (evolucao canonica): o Ultimate ainda vira Mega */
  ultimate: "Virou Ultimate! Para o Mega: mais tempo, 10 lutas com 80% de vitórias e vínculo com você. Forçado à exaustão (forma sombria), ele não chega lá.",
  adulto: "Daqui em diante ele mesmo explica o que sente e por quê. Até mais! — Professor Agumon",
  /* pets v4 (educacao-v1) */
  manha: "Ele chamou: confira a barra. Se a necessidade está em dia, é manha — bronca educa; petisco ensina a pedir mais.",
  banheiro: "Ele avisou que vai sujar: leve ao banheiro em até 15 min e a sujeira não acontece.",
  fala: "Ele falou por conta própria. Às vezes o que ele diz não é verdade: bronca numa mentira educa; petisco ou elogio numa mentira ensina a mentir mais.",
  lesao: "Machucou na luta! Trate em até 6 h ou ele morre. Muitas lesões no mesmo estágio também matam.",
  vitorias: "Além das 10 lutas, ele precisa vencer 80% das lutas deste estágio para evoluir.",
  /* saude critica (qualquer versao): a saude so sobe sem privacao (motor/estado.ts, avancarTick) e devagar (C.curaSaude) */
  saude: "Saúde crítica. Ela só sobe com comida, higiene e energia acima de 15%, e devagar (uns 2% por hora de jogo). Deixe-o dormir e não o canse brincando; Tratar só cuida de lesão.",
} as const;
export type IdDica = keyof typeof DICAS;

const ler = (k: string): string | null => { try { return localStorage.getItem(k); } catch { return null; } };
const vistas = (): Set<string> => { try { return new Set(JSON.parse(ler(CHAVE_DICAS) || "[]") as string[]); } catch { return new Set(); } };
export const dicasLigadas = (): boolean => ler(CHAVE_DICAS_LIGADAS) !== "0";
export function ligarDicas(v: boolean): void {
  try { localStorage.setItem(CHAVE_DICAS_LIGADAS, v ? "1" : "0"); } catch { /* preferencia de tela */ }
  avisar();
}

/* fila: uma dica por vez */
let fila: IdDica[] = [];
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
/** pede uma dica: entra na fila se ainda nao foi vista (e se as dicas estao ligadas) */
export function pedirDica(id: IdDica): void {
  if (!dicasLigadas() || vistas().has(id) || fila.includes(id)) return;
  fila = [...fila, id];
  avisar();
}
/* dicas de evento (a derrota, a regra nova) ficam na fila; as de estagio so valem para o estagio do pet ativo */
const DE_EVENTO: readonly IdDica[] = ["derrota_campanha", "regra_nova", "lesao"];
/** as dicas do momento do pet ativo: tira da fila as de outro estagio (trocar de pet ou evoluir) e pede as novas */
export function dicasDoMomento(ids: readonly IdDica[]): void {
  const antes = fila.join();
  fila = fila.filter(x => DE_EVENTO.includes(x) || ids.includes(x));
  if (fila.join() !== antes) avisar();
  for (const id of ids) pedirDica(id);
}
export function dispensarDica(id: IdDica): void {
  const v = vistas(); v.add(id);
  try { localStorage.setItem(CHAVE_DICAS, JSON.stringify([...v])); } catch { /* sem armazenamento: some so nesta sessao */ }
  fila = fila.filter(x => x !== id);
  avisar();
}
export function useDicaAtual(): IdDica | null {
  const [, t] = useState(0);
  useEffect(() => { const f = () => t(x => x + 1); ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return dicasLigadas() ? fila[0] ?? null : null;
}
