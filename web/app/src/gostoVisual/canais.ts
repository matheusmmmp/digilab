/* Os canais da TV do dono (GOSTO_VISUAL, 2026-11-12; "adiciona um botão para a gente alterar qual tela que eu estou streamando. No caso seria
   como mudar de canal", Matheus; docs/registro/2026-11.md, D-GV-CANAL-1 a 8). O navegador não lista as telas sozinho: cada canal novo passa
   uma vez pelo seletor dele ("+ Canal", captura.ts) ou pelo arquivo escolhido ("+ Vídeo"), e o "Canal ▸" alterna entre os já escolhidos sem
   abrir o seletor de novo.
   - Uma leitura por segundo, sempre da fonte do canal atual: as outras não são lidas (D-GV-CANAL-3). A troca não para a sessão: o mesmo
     relógio continua, o cérebro (cerebroTv.ts) segue com o mesmo resumo, e o "st" só leva os números do canal atual, no formato de sempre,
     sem dizer qual janela é (GV-10).
   - A luminância do último quadro atravessa a troca (D-GV-CANAL-4): o primeiro segundo do canal novo mede o movimento contra o último quadro
     do anterior, como um corte de cena no mesmo fluxo; o gosto do P0 aplica a regra dele do corte (D-GV-MIGRANTE-3) sem nada novo.
   - Uma fonte encerrada (o dono parou de compartilhar) sai da lista; sem nenhuma, a TV desliga (D-GV-CANAL-5).
   Sem DOM em tempo de execução (as fontes de verdade moram em captura.ts), para o teste ler no node. Fora do motor, do log e do save. */
import type { Sentido } from "./gosto.ts";

/** quantos canais o dono pode ter de uma vez. PROPOSTO, SEM FONTE */
export const MAX_CANAIS = 3;
/** um vetor por segundo (o mesmo período da captura de antes). PROPOSTO, SEM FONTE */
export const PERIODO_MS = 1000;

/** uma fonte de imagem (e talvez de som): a captura de uma tela ou um vídeo deste computador */
export interface Fonte {
  /** "tela" pelo seletor do navegador, "video" por um arquivo local; nenhum dos dois vai ao registro */
  tipo: "tela" | "video";
  temSom: boolean;
  /** o elemento que toca a fonte, para o cantinho da TV na ilha (só tipo aqui; nada dele é gravado) */
  video: HTMLVideoElement | null;
  /** um segundo desta fonte: o Sentido e a luminância do quadro; `anterior` é a luminância do quadro de antes (de qualquer canal).
      null enquanto o primeiro quadro não chegou */
  sentir(anterior: Float32Array | null): { sentido: Sentido; lum: Float32Array } | null;
  /** o canal virou o atual (true) ou deixou de ser (false): o vídeo local pausa fora do canal, e o som recomeça a janela */
  ativar(sim: boolean): void;
  /** solta a fonte (para a captura, fecha o arquivo); pode ser chamada mais de uma vez */
  parar(): void;
}

/** o canal de agora, para as palavras do painel: o número (1 a `de`), quantos há e de que tipo é */
export interface CanalAgora { n: number; de: number; tipo: Fonte["tipo"] }

export class Canais {
  private readonly fontes: Fonte[] = [];
  private i = -1;
  private anterior: Float32Array | null = null;
  private relogio: ReturnType<typeof setInterval> | null;

  /** `aoSentir`: um Sentido por segundo do canal atual; `aoMudar`: o canal atual mudou; `aoAcabar`: a última fonte acabou */
  constructor(private readonly aoSentir: (s: Sentido) => void, private readonly aoMudar: () => void,
    private readonly aoAcabar: (motivo: string) => void, periodoMs: number = PERIODO_MS) {
    if (!(periodoMs > 0) || !Number.isFinite(periodoMs)) throw new Error(`Canais: período inválido ${periodoMs}`);
    this.relogio = setInterval(() => this.segundo(), periodoMs);
  }

  private segundo(): void {
    const f = this.fontes[this.i];
    if (!f) return;
    const r = f.sentir(this.anterior);
    if (r === null) return;                               /* o primeiro quadro ainda não chegou */
    this.anterior = r.lum;
    this.aoSentir(r.sentido);
  }

  get quantos(): number { return this.fontes.length; }
  get atual(): Fonte | null { return this.fontes[this.i] ?? null; }
  get agora(): CanalAgora | null { const f = this.atual; return f === null ? null : { n: this.i + 1, de: this.fontes.length, tipo: f.tipo }; }
  tem(f: Fonte): boolean { return this.fontes.includes(f); }

  private irPara(j: number): void {
    const antes = this.atual;
    this.i = j;
    if (antes !== null && antes !== this.atual && this.tem(antes)) antes.ativar(false);
    this.atual?.ativar(true);
    this.aoMudar();
  }

  /** um canal novo vira o atual; com a lista cheia, ele toma o lugar do canal atual, que é solto (D-GV-CANAL-2) */
  adicionar(f: Fonte): void {
    if (this.relogio === null) throw new Error("Canais: adicionar depois de parar");
    if (this.tem(f)) throw new Error("Canais: a fonte já é um canal");
    if (this.fontes.length >= MAX_CANAIS) {
      const saiu = this.fontes[this.i]!;
      this.fontes[this.i] = f;
      saiu.parar();
      f.ativar(true);
      this.aoMudar();
      return;
    }
    this.fontes.push(f);
    this.irPara(this.fontes.length - 1);
  }

  /** o "Canal ▸": o próximo da lista, dando a volta; com um canal só, nada muda */
  proximo(): void {
    if (this.relogio === null) throw new Error("Canais: trocar depois de parar");
    if (this.fontes.length === 0) throw new Error("Canais: trocar sem canal");
    if (this.fontes.length === 1) return;
    this.irPara((this.i + 1) % this.fontes.length);
  }

  /** a fonte acabou por fora (o dono parou de compartilhar): sai da lista. Se era a atual, vai para a que ficou no lugar dela (ou a
      primeira); sem nenhuma, a TV acaba */
  encerrada(f: Fonte, motivo: string): void {
    const j = this.fontes.indexOf(f);
    if (j < 0) throw new Error("Canais: encerrada uma fonte que não é canal");
    this.fontes.splice(j, 1);
    f.parar();
    if (this.fontes.length === 0) { this.i = -1; this.parar(); this.aoAcabar(motivo); return; }
    if (j < this.i) { this.i--; this.aoMudar(); return; }
    if (j > this.i) { this.aoMudar(); return; }
    this.i = -1;
    this.irPara(j % this.fontes.length);
  }

  /** desliga tudo: o relógio e todas as fontes */
  parar(): void {
    if (this.relogio !== null) clearInterval(this.relogio);
    this.relogio = null;
    for (const f of this.fontes.splice(0)) f.parar();
    this.i = -1;
    this.anterior = null;
  }
}
