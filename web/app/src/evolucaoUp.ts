/* A cena oficial de digievolucao do Digimon UP na Revelacao (docs/TAREFA_V2_UP_EVOLUCAO.md). As cenas (Bandai; com o credito, autorizadas
   pelo Matheus: docs/UI_GUIDELINES.md, secao 5.1) ficam FORA do repositorio, em D:\Trab\digilab\Assets\evolucao_up: quadros WebP
   650x500 a 30 por segundo, em camadas (o fundo e a frente separada por trecho da ordem de desenho), convertidos do Spine por
   evolucao_up\ferramentas\converter.html, e o mapa.json gerado por Assets\gerar_evolucao_up.py. O pet e o sprite do app, entre o
   fundo e a frente, no osso AAA_Digimon da cena. So apresentacao: nada daqui entra no motor, no log ou no save. */
import type { AtlasOk, Clipe, Quadro } from "./atlas.ts";
import { quadroDoClipe } from "./atlas.ts";

/** Chave da cena oficial (TAREFA_V2_UP_EVOLUCAO), DESLIGADA: desligada, a Revelacao de hoje, igual. E do app, nao do motor. */
export const CENA_EVOLUCAO_UP = false;
/** a mesma convencao do atlas: relativo a pagina em /v1/web/dist/ (no servidor local cai em /Assets/evolucao_up/) */
export const EVOLUCAO_URL = "../../../Assets/evolucao_up/";

export type NomeCena = "adventure" | "zero2" | "tamers" | "tamers_mega" | "jogress" | "dramon";
/** o Digimon num quadro: o de antes, o novo, nenhum; "herda" (so na revelacao) = o que a Summon deixou, continuando */
export type QuemNaCena = "antes" | "depois" | "herda" | null;
/** um quadro como o conversor grava: as camadas que existem (bk sempre; tNNa somada, tNNn por cima), o osso [x, y, escala x, escala y]
    na camera da cena (y para cima) e o clipe do Digimon com o tempo dele em ms */
export interface QuadroCena { camadas: string[]; osso: [number, number, number, number]; digimon: QuemNaCena; clipe: "Idle" | "Evol" | null; clipe_ms: number | null }
export interface MapaEvolucao {
  versao: number; w: number; h: number; fps: number; camera: [number, number]; escala_digimon: number;
  cenas: Record<NomeCena, { quadros: QuadroCena[]; revela_s: number }>;
  revelacao: { quadros: QuadroCena[] };
  formas: Record<string, { digimon: string; cena: NomeCena; bgm: string }>;
  sem_cena: { forma: string; digimon: string; evol: boolean }[];
}
/** o que a Revelacao toca: a cena oficial, o clipe Evol do atlas (a reserva) ou a Revelacao de hoje */
export type Escolha = { tipo: "cena"; cena: NomeCena; bgm: string } | { tipo: "evol" } | { tipo: "hoje" };

/** a escolha pela linha oficial do Digimon da forma nova (D4: as linhas so escolhem a cena e a musica) */
export function escolherCena(mapa: MapaEvolucao, chave: string, temEvol: boolean): Escolha {
  const f = mapa.formas[chave];
  if (f) {
    if (!mapa.cenas[f.cena]) throw new Error(`mapa da evolucao: a forma ${chave} pede a cena ${f.cena}, que nao existe`);
    return { tipo: "cena", cena: f.cena, bgm: f.bgm };
  }
  return temEvol ? { tipo: "evol" } : { tipo: "hoje" };
}

/** um quadro pronto para tocar: o prefixo dos arquivos e o Digimon resolvido (sem "herda") */
export interface PassoCena { arquivo: string; camadas: string[]; osso: [number, number, number, number]; digimon: "antes" | "depois" | null; clipe: "Idle" | "Evol" | null; clipe_ms: number | null }
/** a Summon da cena e depois a revelacao compartilhada; o "herda" continua o Digimon e o clipe do ultimo quadro da Summon */
export function sequencia(mapa: MapaEvolucao, cena: NomeCena): PassoCena[] {
  const c = mapa.cenas[cena];
  if (!c || !c.quadros.length) throw new Error("mapa da evolucao: cena sem quadros: " + cena);
  const ms = 1000 / mapa.fps, fora: PassoCena[] = [];
  c.quadros.forEach((q, i) => {
    const d = q.digimon;
    if (d === "herda") throw new Error(`mapa da evolucao: "herda" na Summon de ${cena}`);
    fora.push({ arquivo: `${cena}_${String(i).padStart(4, "0")}`, camadas: q.camadas, osso: q.osso, digimon: d, clipe: q.clipe, clipe_ms: q.clipe_ms });
  });
  const ult = fora[fora.length - 1];
  mapa.revelacao.quadros.forEach((q, i) => {
    const d = q.digimon, base = { arquivo: `revelacao_${String(i).padStart(4, "0")}`, camadas: q.camadas, osso: q.osso };
    if (d === "herda") fora.push({ ...base, digimon: ult.digimon, clipe: ult.clipe, clipe_ms: ult.clipe_ms === null ? null : ult.clipe_ms + Math.round((i + 1) * ms) });
    else fora.push({ ...base, digimon: d, clipe: q.clipe, clipe_ms: q.clipe_ms });
  });
  return fora;
}

/** o quadro do sprite naquele clipe e instante: o Evol nao repete e segue no Idle, como no prototipo; sem o atlas de clipes
    (chave CLIPES_UP desligada) so ha o Idle do atlas atual, a ms_por_quadro */
export function quadroDigimon(a: AtlasOk, chave: string, clipe: "Idle" | "Evol", ms: number): { quadro: Quadro; img: HTMLImageElement } {
  const s = a.dados.sprites[chave];
  if (!s) throw new Error("sprite desconhecido na cena da evolucao: " + chave);
  if (!s.clipes) return { quadro: s.quadros[Math.floor(ms / a.dados.ms_por_quadro) % s.quadros.length], img: a.img };
  if (!a.imgClipes) throw new Error("atlas de clipes sem imagem: " + chave);
  let nome: Clipe = clipe, t = ms;
  const evol = s.clipes.Evol;
  if (clipe === "Evol") {
    if (!evol) nome = "Idle";
    else { const total = evol.ms.reduce((x, y) => x + y, 0); if (ms >= total) { nome = "Idle"; t = ms - total; } }
  }
  const c = s.clipes[nome];
  if (!c) throw new Error(`clipe ${nome} indisponível para ${chave}`);
  return { quadro: c.quadros[quadroDoClipe(c.ms, c.loop, t)], img: a.imgClipes };
}
/** o centro do corpo parado (o primeiro quadro do Idle) dentro da caixa do sprite: o ponto que vai no osso, como no prototipo */
export function centroDoCorpo(a: AtlasOk, chave: string): [number, number] {
  const s = a.dados.sprites[chave];
  if (!s) throw new Error("sprite desconhecido na cena da evolucao: " + chave);
  const q = (s.clipes?.Idle?.quadros ?? s.quadros).find(x => x[2] > 0);
  if (!q) throw new Error("sprite sem quadro desenhavel: " + chave);
  return [q[4] + q[2] / 2, q[5] + q[3] / 2];
}
/** onde desenhar o sprite, em pixels dos quadros da cena: a origem da caixa e a escala (decisao 3 do Matheus: segue o osso, fora da
    escala inteira, so durante a cena; quem desenha usa vizinho mais proximo) */
export function lugarDigimon(mapa: MapaEvolucao, osso: [number, number, number, number], centro: [number, number]): { x: number; y: number; escala: number } {
  const k = mapa.w / mapa.camera[0], px = (osso[0] + mapa.camera[0] / 2) * k, py = (mapa.camera[1] / 2 - osso[1]) * k;
  const escala = mapa.escala_digimon * osso[2] * k;
  return { x: px - centro[0] * escala, y: py - centro[1] * escala, escala };
}

let mapaPromessa: Promise<MapaEvolucao> | null = null;
/** o mapa, uma vez por sessao; falha alto (quem chama mostra o aviso e cai na Revelacao de hoje) */
export function carregarMapaEvolucao(base = EVOLUCAO_URL): Promise<MapaEvolucao> {
  mapaPromessa ??= fetch(base + "mapa.json").then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status} em ${base}mapa.json`);
    return r.json() as Promise<MapaEvolucao>;
  }).then(m => { if (m.versao !== 1) throw new Error("mapa da evolucao com versao desconhecida: " + m.versao); return m; });
  mapaPromessa.catch(() => { mapaPromessa = null; });
  return mapaPromessa;
}
/** baixa todos os quadros da sequencia antes de tocar (so os bytes; a decodificacao e numa janela, para nao guardar a cena inteira
    decodificada); avisa o progresso de 0 a 1 */
export async function baixarQuadros(seq: PassoCena[], progresso: (p: number) => void, base = EVOLUCAO_URL, paralelo = 8): Promise<Map<string, Blob>> {
  const nomes = seq.flatMap(p => p.camadas.map(c => `${p.arquivo}_${c}.webp`)), fora = new Map<string, Blob>();
  let i = 0, feitos = 0;
  const um = async (): Promise<void> => {
    while (i < nomes.length) {
      const n = nomes[i++], r = await fetch(base + "quadros/" + n);
      if (!r.ok) throw new Error(`HTTP ${r.status} em ${base}quadros/${n}`);
      fora.set(n, await r.blob()); progresso(++feitos / nomes.length);
    }
  };
  await Promise.all(Array.from({ length: paralelo }, um));
  return fora;
}
