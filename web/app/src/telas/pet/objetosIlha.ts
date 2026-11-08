/* Os objetos que falam (direcao A da ilha interativa, prancha docs/pranchas/ux-ilha-a/; decisoes I1-1 e I1-4 a I1-9 do PERGUNTAS.md): as contas, sem DOM
   e sem three, que as etiquetas, o cartao e os selos da ilha (componentes/ObjetosDaIlha.tsx) leem do motor. So leitura: nada aqui muda o motor, a rng,
   o registro ou o save; a marca do diario lido e da tela (localStorage), fora do save e do replay (I1-5).
   - a tigela: as racoes maduras no comedouro (Motor.mundo.comidas e situacao, a mesma celula do comedouro);
   - o alvo atual (I1-4, sem getter novo no motor): a tigela, quando o pet decidiu comer, ha racao madura nela e nenhuma comida madura esta mais perto
     do pet que ela; a bola, quando o pet decidiu brincar. E uma estimativa da vista, como a prancha registra;
   - a linha do que o pet aprendeu (I1-8): o desvio aprendido da acao (Motor.digibrain().aprendido, as 3 maiores), comer para a tigela e brincar para a
     bola; fora das 3 maiores, "nada novo";
   - o saco (I1-7): os treinos de hoje (os eventos "tr" do registro no dia do jogo) e se ja pode treinar (TreinoPet.podeTocar), ou a hora da proxima vez;
   - a barraca (I1-5): ha "diario novo" quando uma linha de regras aprendidas (o historico "gambit") ou uma evolucao veio depois da ultima abertura
     do Diario. */
import { CTR, TPD, type Motor, type Mundo } from "../../../motor/index.ts";
import { CHAVE } from "../../save.ts";

/** as racoes maduras na tigela (a celula do comedouro) */
export function racoesNaTigela(mu: Mundo, tick: number): number {
  const [cx, cy] = mu.comedouro, meia = mu.cm.sub / 2;
  let n = 0;
  for (const c of mu.comidas.values()) if (Math.abs(c.x - cx) <= meia && Math.abs(c.y - cy) <= meia && mu.situacao(c, tick) === "madura") n++;
  return n;
}

/** o objeto que e o alvo atual do pet, pela vista (I1-4): "tigela", "bola" ou null */
export function alvoAtual(m: Motor): "tigela" | "bola" | null {
  const mu = m.mundo;
  if (!mu || m.morte || m.e.dormindo) return null;
  if (m.acao === "brincar") return "bola";
  if (m.acao !== "comer" || racoesNaTigela(mu, m.e.tick) === 0) return null;
  const [px, py] = mu.pet, [cx, cy] = mu.comedouro, dTigela = Math.hypot(cx - px, cy - py), meia = mu.cm.sub / 2;
  for (const c of mu.comidas.values()) {
    if (Math.abs(c.x - cx) <= meia && Math.abs(c.y - cy) <= meia) continue;
    if (mu.situacao(c, m.e.tick) === "madura" && Math.hypot(c.x - px, c.y - py) < dTigela) return null;
  }
  return "tigela";
}

export interface LinhaAprendeu { texto: string; sinal: -1 | 0 | 1 }
/** a linha do que o pet aprendeu sobre o objeto (I1-8): "Come menos", "Brinca mais" ou "Nada novo sobre ..." */
export function linhaAprendeu(aprendido: readonly { acao: string; desvio: number }[] | null, objeto: "tigela" | "bola"): LinhaAprendeu {
  const acao = objeto === "tigela" ? "comer" : "brincar", verbo = objeto === "tigela" ? "Come" : "Brinca";
  const a = aprendido?.find(x => x.acao === acao);
  if (!a || a.desvio === 0) return { texto: `Nada novo sobre ${acao}`, sinal: 0 };
  return a.desvio < 0 ? { texto: `${verbo} menos`, sinal: -1 } : { texto: `${verbo} mais`, sinal: 1 };
}

/** os treinos do dia do jogo de agora: os eventos "tr" do registro com o mesmo dia (tick / TPD) */
export function treinosHoje(log: readonly (readonly unknown[])[], tick: number): number {
  /* o registro esta em ordem de tick: conta de tras para a frente e para no primeiro evento de um dia anterior */
  const dia = Math.floor(tick / TPD);
  let n = 0;
  for (let i = log.length - 1; i >= 0; i--) {
    const d = Math.floor((log[i][0] as number) / TPD);
    if (d < dia) break;
    if (d === dia && log[i][1] === "tr") n++;
  }
  return n;
}
/** o saco: os treinos de hoje e, se ainda nao pode treinar, o tick da proxima vez (TreinoPet.podeTocar e CTR.intervalo) */
export function seloDoSaco(m: Motor): { hoje: number; proxima: number | null } {
  const t = m.treino, tick = m.e.tick;
  return { hoje: treinosHoje(m.log, tick), proxima: t.podeTocar(tick) || t.ultimo === null ? null : t.ultimo + CTR.intervalo };
}

/* ------------------------------------------------ o diario lido (I1-5): so a tela, num localStorage, por pet (a semente) */
export const CHAVE_DIARIO_VISTO = CHAVE + "-diario-visto";
/** o tick da ultima novidade do diario: a ultima linha de regras aprendidas (gambit) ou a ultima evolucao; null sem nenhuma */
export function ultimaNovidade(m: Motor): number | null {
  let t: number | null = null;
  for (const h of m.historico) if (h.quem === "gambit" && (t === null || h.t > t)) t = h.t;
  for (const e of m.evolucoes) if (t === null || e.tick > t) t = e.tick;
  return t;
}
/* a marca lida fica guardada aqui (a tela le a cada tick; o armazenamento so na primeira vez e depois de cada marca) */
let cacheVisto: { semente: number; tick: number | null } | null = null;
/** le a marca do pet `semente`: o tick em que o dono abriu o Diario pela ultima vez; null sem marca (ou sem armazenamento) */
export function lerDiarioVisto(semente: number): number | null {
  if (cacheVisto && cacheVisto.semente === semente) return cacheVisto.tick;
  const t = lerDiarioVistoArmazenado(semente);
  cacheVisto = { semente, tick: t };
  return t;
}
/** as marcas guardadas, por pet: { "<semente>": tick }. Conteudo que nao e esse mapa falha alto */
function lerMarcas(): Record<string, number> {
  let texto: string | null = null;
  try { texto = localStorage.getItem(CHAVE_DIARIO_VISTO); } catch { return {}; }   /* sem armazenamento (aba privada): sem marca, sem erro */
  if (texto === null) return {};
  const v = JSON.parse(texto) as unknown;
  if (typeof v !== "object" || v === null || Array.isArray(v) || Object.values(v).some(t => typeof t !== "number"))
    throw new Error(`marca do diário inválida em ${CHAVE_DIARIO_VISTO}: ${texto}`);
  return v as Record<string, number>;
}
function lerDiarioVistoArmazenado(semente: number): number | null {
  return lerMarcas()[String(semente)] ?? null;
}
/** grava a marca: o dono abriu o Diario no tick `tick` do pet `semente` (so a tela; fora do save). Uma marca por pet, na mesma chave */
export function marcarDiarioVisto(semente: number, tick: number): void {
  cacheVisto = { semente, tick };
  try { localStorage.setItem(CHAVE_DIARIO_VISTO, JSON.stringify({ ...lerMarcas(), [String(semente)]: tick })); } catch { /* preferencia de tela */ }
}
/** esquece a marca guardada (os testes, que trocam o armazenamento) */
export const esquecerDiarioVisto = (): void => { cacheVisto = null; };
export const diarioNovo = (novidade: number | null, visto: number | null): boolean => novidade !== null && (visto === null || novidade > visto);
