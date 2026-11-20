/* As janelas da tela do pet (docs/PLANO_UX_JANELAS.md, etapa JN1; UX-JN-1 a 7 aprovadas pelo Matheus em 2026-11-12): o cadastro das
   janelas e o "exibir" de cada uma. A tela do pet e os Ajustes leem o mesmo cadastro; uma janela nova entra aqui e so aqui.
   Nesta etapa nada se move: so aparece ou some. O arraste por janela e a JN2.
   So apresentacao: o motor, o registro, o chamado e o replay nao mudam. A escolha fica no navegador, fora do save, e nao sobe para a
   nuvem (a CN0: os ajustes de tela ficam no aparelho). */
import { useSyncExternalStore } from "react";
import { CHAVE } from "./save.ts";

/** as janelas, na ordem da lista de Ajustes > Exibir (UX-JN-4) */
export const IDS_JANELA = ["estado", "evolucao", "acoes", "digibrain", "agora", "minimapa"] as const;
export type IdJanela = typeof IDS_JANELA[number];
export type Janelas = Readonly<Record<IdJanela, boolean>>;

/** o nome na tela e o que a janela e (o balao da linha em Ajustes) */
export const JANELAS: Readonly<Record<IdJanela, { nome: string; resumo: string }>> = {
  estado: { nome: "Estado atual", resumo: "comida, energia, higiene, humor e saúde" },
  evolucao: { nome: "Evolução", resumo: "a próxima forma e o tempo do estágio" },
  acoes: { nome: "Últimas ações", resumo: "o que o registro guardou por último" },
  digibrain: { nome: "DigiBrain", resumo: "o porquê das escolhas do pet" },
  agora: { nome: "Agora", resumo: "a linha do alto com o que o pet está fazendo" },
  minimapa: { nome: "Minimapa", resumo: "o mapa da ilha no canto, a partir de 900 px" },
};

/** as quatro janelas que a chave unica de antes ("Exibir detalhes do pet") ligava e desligava juntas */
export const DA_CHAVE_ANTIGA: readonly IdJanela[] = ["estado", "evolucao", "acoes", "digibrain"];

const CHAVE_JANELAS = CHAVE + "-janelas", CHAVE_ANTIGA = CHAVE + "-detalhes-pet";
const TODAS: Janelas = { estado: true, evolucao: true, acoes: true, digibrain: true, agora: true, minimapa: true };

/** o estado das janelas a partir do que esta gravado. `gravado`: o texto da chave nova, ou null; `antigo`: o da chave unica de antes
    ("0" = desligada), ou null. Sem nada gravado, tudo a mostra (o jogo de hoje). Com so a chave antiga desligada, as quatro janelas dela
    comecam escondidas (UX-JN-7). Um texto ilegivel ou de outro formato vale como nada gravado: e preferencia de tela, nao dado do pet */
export function janelasDoGravado(gravado: string | null, antigo: string | null): Janelas {
  if (gravado !== null) {
    try {
      const o: unknown = JSON.parse(gravado);
      if (o && typeof o === "object") {
        const v = (o as { v?: unknown }).v, e = (o as { exibir?: unknown }).exibir;
        if (v === 1 && e && typeof e === "object") {
          const n = { ...TODAS };
          for (const id of IDS_JANELA) { const x = (e as Record<string, unknown>)[id]; if (typeof x === "boolean") n[id] = x; }
          return n;
        }
      }
    } catch { /* cai no padrao, abaixo */ }
  }
  if (antigo === "0") { const n = { ...TODAS }; for (const id of DA_CHAVE_ANTIGA) n[id] = false; return n; }
  return TODAS;
}

function lerDoNavegador(): Janelas {
  try { return janelasDoGravado(localStorage.getItem(CHAVE_JANELAS), localStorage.getItem(CHAVE_ANTIGA)); } catch { return TODAS; }   /* preferência de tela */
}

/* o useSyncExternalStore pede a mesma referencia enquanto nada muda: o estado fica aqui e so troca em exibirJanela */
let atual: Janelas | null = null;
const ouvintes = new Set<() => void>();
const estado = (): Janelas => atual ??= lerDoNavegador();

/** mostra ou esconde uma janela (Ajustes > Exibir) */
export function exibirJanela(id: IdJanela, v: boolean): void {
  atual = { ...estado(), [id]: v };
  try { localStorage.setItem(CHAVE_JANELAS, JSON.stringify({ v: 1, exibir: atual })); } catch { /* preferência de tela */ }
  for (const o of ouvintes) o();
}
/** as janelas a mostra */
export function useJanelas(): Janelas {
  return useSyncExternalStore(o => { ouvintes.add(o); return () => { ouvintes.delete(o); }; }, estado, () => TODAS);
}
/** quantas janelas estao a mostra (o resumo da linha "Exibir" em Ajustes) */
export const quantasAMostra = (j: Janelas): number => IDS_JANELA.filter(id => j[id]).length;
/** so para os testes: esquece o que foi lido, para ler de novo do navegador */
export function esquecerJanelas(): void { atual = null; }
