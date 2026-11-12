/* A captura ligada ao cérebro (GOSTO_VISUAL, 2026-11-12; "Quero ligar a captura ao cerebro", Matheus; docs/registro/2026-11.md,
   D-GV-CEREBRO-1 a 10). Só para o pet que tem a TV no cérebro (a v31, `Motor.temTv`); nos outros pets nada daqui roda e o P0 segue fora do
   motor, do log e do save, como antes.
   - É a ÚNICA porta do P0 para o registro além do Carinho (o teste gosto_visual_p0 confere): o vetor de cada segundo (o da captura da tela ou
     o da TV do jogo do P0, sete números em [0, 1]) vai ao ResumoTela do motor (GV-15: a média de 10 s em 16 níveis, só na mudança), e cada
     valor que ele devolve entra no registro do pet pelo evento "st" (`Motor.sentidoTela`), o modo livre gravado. Nada da imagem nem do som:
     só os sete inteiros. O replay lê o evento.
   - A fonte do evento: "tela" para a captura e "tv" para a TV do jogo do P0 (D-GV-CEREBRO-3).
   - Ao parar a TV, um "st" com os sete níveis em 0 (a tela preta e muda; o formato do GV-15 não tem "desligada": D-GV-CEREBRO-6).
   - A leitura para as telas (o painel da TV e o sinal sobre o pet): o que o cérebro faz agora, do motor (`Motor.tvNoCerebro`), para o painel
     da TV não contradizer o do DigiBrain (D-GV-CEREBRO-8). */
import { CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE, PetMorto, ResumoTela, centroDaCelula, valorSentidoTela, type Motor } from "../../motor/index.ts";
import { jogoSeHouver, mudarMotor } from "../jogo.ts";
import type { Reacao, Sentido } from "./gosto.ts";

/** a escala do cérebro (S) e os cortes do agrado para a reação mostrada sobre o pet (a pose e o ícone). PROPOSTO, SEM FONTE */
const S = 1024;
export const CORTES_AGRADO = { adorando: 0.65, naoGosta: 0.35 } as const;

let resumo: ResumoTela | null = null, alvo: Motor | null = null;

/** o pet de agora, se ele tem a TV no cérebro (o de teste e o grupo não têm) */
function petComTv(): Motor | null {
  const j = jogoSeHouver();
  return j !== null && j.emLab === null && j.grupo === null && j.motor.temTv ? j.motor : null;
}
/** o pet na tela agora (null sem jogo) */
const naTela = (): Motor | null => jogoSeHouver()?.motor ?? null;

/** o vetor do segundo na ordem do evento (cor, brilho, movimento, complexidade, volume, variação, timbre); sem o som, o som é 0 (o silêncio) */
export function vetorDoSentido(s: Sentido): number[] {
  const v = s.visao, o = s.som;
  return [v.cor, v.brilho, v.movimento, v.complexidade, o?.volume ?? 0, o?.variacao ?? 0, o?.timbre ?? 0];
}

/** grava um "st" no pet de agora; o pet morto encerra a ligação (a TV do P0 segue só como vista) */
function gravar(m: Motor, valor: string): void {
  if (naTela() !== m) return;
  try { mudarMotor(x => x.sentidoTela(valor), "adiado"); } catch (x) {
    if (x instanceof PetMorto) { resumo = null; alvo = null; return; }
    throw x;
  }
}

/** a TV ligou: com o pet da v31, o resumo começa, com a fonte da origem */
export function comecarNoCerebro(origem: "tela" | "jogo"): void {
  alvo = petComTv();
  resumo = alvo === null ? null : new ResumoTela(origem === "tela" ? "tela" : "tv");
}

/** um segundo sentido: a amostra vai ao resumo; quando a janela fecha com níveis novos, o "st" entra no registro */
export function sentirNoCerebro(s: Sentido): void {
  if (resumo === null || alvo === null) return;
  if (naTela() !== alvo) { resumo = null; alvo = null; return; }      // o pet mudou: a ligação acaba sem gravar no outro
  const valor = resumo.amostra(vetorDoSentido(s));
  if (valor !== null) gravar(alvo, valor);
}

/** a TV parou: a tela preta e muda entra no registro, se o último "st" não era ela (a janela incompleta é descartada) */
export function pararNoCerebro(): void {
  const r = resumo, m = alvo;
  resumo = null; alvo = null;
  if (r === null || m === null || naTela() !== m) return;
  const u = m.ultimoSentidoTela;
  if (u === null) return;
  const preta = valorSentidoTela(r.fonte, [0, 0, 0, 0, 0, 0, 0]);
  if (u !== preta) gravar(m, preta);
}

/** o que o cérebro faz com a TV agora, em palavras e na reação mostrada sobre o pet; null fora da v31 */
export function leituraDoCerebro(m: Motor): { frase: string; reacao: Reacao; olhando: boolean; noRaio: boolean; agrado: number | null } | null {
  const c = m.tvNoCerebro();
  if (c === null) return null;
  const mo = c.motivo, a = mo === null ? null : (mo["agrado"] as number | null), pct = a === null ? null : Math.round((a * 100) / S);
  if (m.e.dormindo) return { frase: "No cérebro: está dormindo.", reacao: "distraido", olhando: false, noRaio: c.noRaio, agrado: a };
  if (c.olhando) {
    const reacao: Reacao = a === null ? "curioso" : a >= CORTES_AGRADO.adorando * S ? "adorando" : a <= CORTES_AGRADO.naoGosta * S ? "nao_gosta" : "olhando";
    return { frase: `No cérebro: olhando a TV${pct === null ? " (a primeira olhada)" : `, agrado de ${pct}%`}.`, reacao, olhando: true, noRaio: true, agrado: a };
  }
  if (!c.noRaio) return { frase: "No cérebro: a TV está longe, fora da vista dele.", reacao: "distraido", olhando: false, noRaio: false, agrado: a };
  const esc = m.lab?.ultimoMotivo?.["escolha"] as unknown[] | undefined, acao = esc ? String(esc[0]) : m.acao;
  return { frase: `No cérebro: vê a TV, mas escolheu ${NOME_ACAO[acao] ?? acao}.`, reacao: "distraido", olhando: false, noRaio: true, agrado: a };
}
const NOME_ACAO: Record<string, string> = {
  ocioso: "ficar à toa", dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você", explorar: "explorar", emburrar: "emburrar",
  olhar: "olhar",
};

/** a reação do cérebro do pet de agora para o sinal e a pose (a sessão lê a cada segundo); null fora da v31 */
export function reacaoDoCerebroAgora(): { reacao: Reacao; olhando: boolean } | null {
  const m = petComTv(), l = m === null ? null : leituraDoCerebro(m);
  return l === null ? null : { reacao: l.reacao, olhando: l.olhando };
}

/** o dono leva o pet até a frente da TV (o gesto de levar o pet do jogo, o evento "lp"); com o pet dormindo, não (PP-2) */
export function levarPetATv(): void {
  const m = petComTv();
  if (m === null) throw new Error("levar até a TV só no pet com a TV no cérebro");
  const [x, y] = centroDaCelula(CELULA_PERTO_DA_TV_JOGO, CMU_GRANDE);
  mudarMotor(p => p.levarPet(x, y));
}
