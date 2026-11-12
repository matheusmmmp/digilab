/* A captura ligada ao cérebro (GOSTO_VISUAL, 2026-11-12; "Quero ligar a captura ao cerebro", Matheus; docs/registro/2026-11.md,
   D-GV-CEREBRO-1 a 10, e a TV no jogo, D-GV-TVJOGO). Só para o pet que tem a TV no cérebro (a v32 e a v33, `Motor.temTv`) e para o grupo com
   a TV do mundo comum (a v34, `GrupoDoJogo.temTv`); nos outros pets nada daqui roda e o P0 segue fora do motor, do log e do save, como antes.
   - É a ÚNICA porta do P0 para o registro além do Carinho (o teste gosto_visual_p0 confere): o vetor de cada segundo (o da captura da tela ou
     o da TV do jogo do P0, sete números em [0, 1]) vai ao ResumoTela do motor (GV-15: a média de 10 s em 16 níveis, só na mudança), e cada
     valor que ele devolve entra no registro pelo evento "st" (`Motor.sentidoTela`; no grupo, `GrupoDoJogo.sentidoTela`, um evento do grupo:
     os dois pets veem a mesma TV), o modo livre gravado. Nada da imagem nem do som: só os sete inteiros. O replay lê o evento.
   - A fonte do evento: "tela" para a captura e "tv" para a TV do jogo do P0 (D-GV-CEREBRO-3).
   - Ao parar a TV: na v33 e na v34, a TV desligada (`fonte|desligada`, a decisão A, D-GV-TVJOGO-1: a TV sai da vista do pet e ele não a
     olha); na v32, um "st" com os sete níveis em 0 (a tela preta e muda; D-GV-CEREBRO-6).
   - A leitura para as telas (o painel da TV e o sinal sobre o pet): o que o cérebro faz agora, do motor (`Motor.tvNoCerebro`), para o painel
     da TV não contradizer o do DigiBrain (D-GV-CEREBRO-8); na v33 e na v34, também o "indo até a TV" e o enjoo (D-GV-TVJOGO). */
import {
  CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE, PetMorto, ResumoTela, centroDaCelula, nasceComTvJogo, valorSentidoTela, valorSentidoTelaDesligada,
  type GrupoDoJogo, type Motor,
} from "../../motor/index.ts";
import { jogoSeHouver, mudarGrupo, mudarMotor } from "../jogo.ts";
import type { Reacao, Sentido } from "./gosto.ts";

/** a escala do cérebro (S) e os cortes do agrado para a reação mostrada sobre o pet (a pose e o ícone). PROPOSTO, SEM FONTE */
const S = 1024;
export const CORTES_AGRADO = { adorando: 0.65, naoGosta: 0.35 } as const;
/** a partir de quanto enjoo lido (na escala S) a reação do cérebro é "enjoou" (a v33 e a v34, com o enjoo do #875; D-GV-TVJOGO-6). PROPOSTO,
    SEM FONTE: a metade, o ponto em que a exposição para de andar e o tédio começa a sair do agrado (D-GV-ENJOO-CER-8) */
export const CORTE_ENJOO = 0.5;

/** quem recebe o "st": o pet de um só, ou o grupo inteiro (a TV do mundo comum) */
type Alvo = { tipo: "pet"; m: Motor } | { tipo: "grupo"; g: GrupoDoJogo };
let resumo: ResumoTela | null = null, alvo: Alvo | null = null;

/** quem tem a TV no cérebro agora: o pet de um só da v32 ou da v33, ou o grupo da v34 (o de teste não tem) */
function alvoComTv(): Alvo | null {
  const j = jogoSeHouver();
  if (j === null || j.emLab !== null) return null;
  if (j.grupo !== null) return j.grupo.temTv ? { tipo: "grupo", g: j.grupo } : null;
  return j.motor.temTv ? { tipo: "pet", m: j.motor } : null;
}
/** o alvo segue na tela (o pet de um só, ou o grupo, com qualquer um dos dois em foco) */
function naTela(a: Alvo): boolean {
  const j = jogoSeHouver();
  if (j === null || j.emLab !== null) return false;
  return a.tipo === "grupo" ? j.grupo === a.g : j.grupo === null && j.motor === a.m;
}
const versaoDo = (a: Alvo): number => a.tipo === "grupo" ? a.g.versao : a.m.versao;
const ultimoDo = (a: Alvo): string | null => a.tipo === "grupo" ? a.g.ultimoSentidoTela : a.m.ultimoSentidoTela;

/** o vetor do segundo na ordem do evento (cor, brilho, movimento, complexidade, volume, variação, timbre); sem o som, o som é 0 (o silêncio) */
export function vetorDoSentido(s: Sentido): number[] {
  const v = s.visao, o = s.som;
  return [v.cor, v.brilho, v.movimento, v.complexidade, o?.volume ?? 0, o?.variacao ?? 0, o?.timbre ?? 0];
}

/** grava um "st"; o pet morto encerra a ligação (a TV do P0 segue só como vista) */
function gravar(a: Alvo, valor: string): void {
  if (!naTela(a)) return;
  try {
    if (a.tipo === "grupo") mudarGrupo(g => g.sentidoTela(valor), "adiado");
    else mudarMotor(x => x.sentidoTela(valor), "adiado");
  } catch (x) {
    if (x instanceof PetMorto) { resumo = null; alvo = null; return; }
    throw x;
  }
}

/** a TV ligou: com o pet (ou o grupo) com a TV no cérebro, o resumo começa, com a fonte da origem */
export function comecarNoCerebro(origem: "tela" | "jogo"): void {
  alvo = alvoComTv();
  resumo = alvo === null ? null : new ResumoTela(origem === "tela" ? "tela" : "tv");
}

/** um segundo sentido: a amostra vai ao resumo; quando a janela fecha com níveis novos, o "st" entra no registro */
export function sentirNoCerebro(s: Sentido): void {
  if (resumo === null || alvo === null) return;
  if (!naTela(alvo)) { resumo = null; alvo = null; return; }      // o pet mudou: a ligação acaba sem gravar no outro
  const valor = resumo.amostra(vetorDoSentido(s));
  if (valor !== null) gravar(alvo, valor);
}

/** a TV parou (a janela incompleta é descartada): na v33 e na v34, a TV desligada; na v32, a tela preta e muda. Só se o último "st" não era
    esse, e só se a TV já recebeu algo */
export function pararNoCerebro(): void {
  const r = resumo, a = alvo;
  resumo = null; alvo = null;
  if (r === null || a === null || !naTela(a)) return;
  const u = ultimoDo(a);
  if (u === null) return;
  const fim = nasceComTvJogo(versaoDo(a)) ? valorSentidoTelaDesligada(r.fonte) : valorSentidoTela(r.fonte, [0, 0, 0, 0, 0, 0, 0]);
  if (u !== fim) gravar(a, fim);
}

/** o que o cérebro faz com a TV agora, em palavras e na reação mostrada sobre o pet; null fora dos pets com a TV no cérebro */
export function leituraDoCerebro(m: Motor): { frase: string; reacao: Reacao; olhando: boolean; noRaio: boolean; agrado: number | null; indo: boolean; enjoo: number | null } | null {
  const c = m.tvNoCerebro();
  if (c === null) return null;
  const mo = c.motivo, a = mo === null ? null : (mo["agrado"] as number | null), pct = a === null ? null : Math.round((a * 100) / S);
  const e = mo === null ? null : (mo["enjoo"] as number | null | undefined) ?? null;
  const base = { noRaio: c.noRaio, agrado: a, indo: false, enjoo: e };
  if (m.e.dormindo) return { ...base, frase: "No cérebro: está dormindo.", reacao: "distraido", olhando: false };
  if (c.olhando) {
    if (e !== null && e >= CORTE_ENJOO * S)
      return { ...base, frase: `No cérebro: olhando a TV, mas enjoado dela (enjoo de ${Math.round((e * 100) / S)}%).`, reacao: "enjoou", olhando: true, noRaio: true };
    const reacao: Reacao = a === null ? "curioso" : a >= CORTES_AGRADO.adorando * S ? "adorando" : a <= CORTES_AGRADO.naoGosta * S ? "nao_gosta" : "olhando";
    return { ...base, frase: `No cérebro: olhando a TV${pct === null ? " (a primeira olhada)" : `, agrado de ${pct}%`}.`, reacao, olhando: true, noRaio: true };
  }
  /* a v33 e a v34 (D-GV-TVJOGO-3): o cérebro escolheu a TV de longe, e o pet anda até ela */
  if (m.lab?.ultimoMotivo?.["acao"] === "ir_tv") return { ...base, frase: "No cérebro: indo até a TV.", reacao: "curioso", olhando: false, indo: true };
  if (!c.noRaio) return { ...base, frase: "No cérebro: a TV está longe, fora da vista dele.", reacao: "distraido", olhando: false };
  const esc = m.lab?.ultimoMotivo?.["escolha"] as unknown[] | undefined, acao = esc ? String(esc[0]) : m.acao;
  return { ...base, frase: `No cérebro: vê a TV, mas escolheu ${NOME_ACAO[acao] ?? acao}.`, reacao: "distraido", olhando: false };
}
const NOME_ACAO: Record<string, string> = {
  ocioso: "ficar à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
  olhar: "olhar", ir_tv: "ir até a TV",
};

/** a reação do cérebro do pet de agora para o sinal e a pose (a sessão lê a cada segundo); null fora dos pets com a TV no cérebro */
export function reacaoDoCerebroAgora(): { reacao: Reacao; olhando: boolean } | null {
  const a = alvoComTv(), j = jogoSeHouver();
  if (a === null || j === null) return null;
  const l = leituraDoCerebro(j.motor);
  return l === null ? null : { reacao: l.reacao, olhando: l.olhando };
}

/** o dono leva o pet até a frente da TV (o gesto de levar o pet do jogo, o evento "lp"); com o pet dormindo, não (PP-2) */
export function levarPetATv(): void {
  const j = jogoSeHouver();
  if (alvoComTv() === null || j === null) throw new Error("levar até a TV só no pet com a TV no cérebro");
  const [x, y] = centroDaCelula(CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE);
  mudarMotor(p => p.levarPet(x, y));
}
