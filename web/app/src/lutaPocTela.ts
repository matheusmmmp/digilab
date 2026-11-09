/* A luta da POC na tela (LUTA_POC, LP3; docs/TAREFA_V3_LUTA_POC.md, secao 5.1): a luta ja decidida pelo motor (Motor.lutarPoc grava a
   entrada no registro e devolve o resultado) e refeita aqui passo a passo, da mesma entrada (o mapa, as duas formas, os numeros de cada lado e
   a semente), so para desenhar. No fim de cada luta o palco confere que ela acabou como a do motor (o vencedor, o relogio e os passos) e falha
   alto se nao. A tela nao muda o resultado nem o log: nada aqui grava.
   Durante a luta nao ha botao nenhum (o pet luta sozinho); o que vem depois (o resultado e Continuar) so aparece no fim.
   O ritmo e o do palco de antes (src/luta.ts): um quadro a cada 48 ms com 3 passos de 16 ms (o tempo real); com o movimento reduzido, 12 por
   quadro. A pausa do acerto (E1) e a camera lenta do nocaute (E5) so mudam o desenho: os passos e o fim sao os mesmos. */
import { useEffect, useReducer } from "react";
import {
  CENAS, FORMAS_ARENA, LIGA, VERSAO_V21, arenaDaLuta, RIVAL_LIGA, ehInstalacao, LIMITE_POC_MS, NOME_BOT, NPC, configLutaPoc, criarLutaPoc, formaDaChave, naTabela, nomeForma, passoPoc, sementeDaSerie,
  sorteiosPoc, statsNpc, statsRivalArena, type EntradaLutaPoc, type IdCena, type LutaPoc, type ResultadoLutaPoc,
} from "../motor/index.ts";
import { lutaPocLigada } from "./lutaPoc.ts";
import { carregarEfeitos } from "./telas/lutar/palcoPoc/efeitosJogo.ts";
import { arquivosPoc, movimentoReduzido, type LadoDesenhoPoc } from "./telas/lutar/palcoPoc/desenhoPoc.ts";
import {
  aplicarEventosPoc, consumirPausaPoc, passoDe, passosDaEspera, passosDoQuadro, visualNovoPoc, type VisualPoc,
} from "./telas/lutar/palcoPoc/visualPoc.ts";

/** o que a luta da tela tem de dar no fim: o resultado da mesma luta no motor (null: a luta montada da conferencia, sem motor) */
/** ko: alguem caiu (os dois, no nocaute duplo); sem ko, a luta chegou ao limite de tempo */
export interface FimEsperado { vencedor: "a" | "b" | null; relogio: number; passos: number; ko: boolean }
/** uma luta para o palco: a entrada, o fim esperado, os dois lados como a tela os mostra e o rotulo dela na serie */
export interface LutaNaTela { entrada: EntradaLutaPoc; esperado: FimEsperado | null; A: LadoDesenhoPoc; B: LadoDesenhoPoc; rotulo: string }
export interface FimPoc { titulo: string; texto: string; venceu: boolean | null }
export interface PalcoPoc {
  L: LutaPoc; v: VisualPoc; A: LadoDesenhoPoc; B: LadoDesenhoPoc; cena: IdCena;
  /** a luta k (0, 1, ...) de n e o rotulo dela; o contexto (Arena, Campanha, a serie) */
  k: number; n: number; rotulo: string; contexto: string;
  /** no fim de todas: o resultado (o que aparece depois da luta) */
  fim: FimPoc | null;
}
export const LUTA_POC = { palco: null as PalcoPoc | null, lutando: false };

const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };
export function useLutaPoc(): typeof LUTA_POC {
  const [, f] = useReducer((x: number) => x + 1, 0);
  useEffect(() => { ouvintes.add(f); return () => { ouvintes.delete(f); }; }, []);
  return LUTA_POC;
}

/** o nome na tela de uma chave da tabela da arena (uma forma do jogo ou um NPC da Campanha) */
export function nomeDaChave(k: string): string {
  if (NPC[k]) return NOME_BOT[k] ?? NPC[k]!.nome;
  return nomeForma(formaDaChave(k));
}
/** o sprite do atlas de uma chave da tabela: a propria forma, ou o sprite do NPC (alguns NPCs usam o de outro Digimon) */
export const spriteDaChave = (k: string): string => (NPC[k] ? NPC[k]!.sprite ?? k : k);
export const ladoDesenho = (k: string): LadoDesenhoPoc => {
  const f = FORMAS_ARENA[k]; if (!f) throw new Error(`palco: ${k} nao esta na tabela da arena`);
  return { chave: k, sprite: spriteDaChave(k), nomeTela: nomeDaChave(k), forma: f };
};

/** as lutas de um resultado do motor (uma, ou a serie: a Cidadela, a Liga, a Torre), com a mesma entrada que o motor usou (Motor._lutarPoc) */
export function lutasDoResultado(r: ResultadoLutaPoc): LutaNaTela[] {
  /* a serie da Cidadela: as lutas que ela tem (as jogadas param na primeira que nao for vitoria) */
  const nSerie = NPC[r.rival] ? arenaDaLuta(r.rival, VERSAO_V21)?.lutas ?? 1 : 1;
  return r.serie.map((s, k) => ({
    entrada: { cena: s.mapa, semente: sementeDaSerie(r.semente, k), a: { forma: r.forma, stats: r.pet, ...(k ? { vida0: s.vida0 } : {}) }, b: { forma: s.contra, stats: s.rivalStats } },
    esperado: { vencedor: s.vencedor, relogio: s.relogio, passos: s.passos, ko: s.vidaA <= 0 || s.vidaB <= 0 },
    A: ladoDesenho(r.forma), B: ladoDesenho(s.contra),
    /* a Liga tem 6 lutas, a Cidadela 3; a Torre vai ate a primeira que nao for vitoria (o numero de lutas nao aparece) */
    rotulo: r.rival === RIVAL_LIGA ? `Luta ${k + 1} de ${LIGA.length}` : ehInstalacao(r.rival) ? `vitória ${k + 1}` : nSerie > 1 ? `Luta ${k + 1} de ${nSerie}` : "",
  }));
}

/* ---------------------------------------------------------------- o ritmo */
/** quadros da tela e a espera do fim. PROPOSTOS, SEM FONTE (os do palco de antes: src/luta.ts) */
export const RITMO_POC = { quadroMs: 48, passos: 3, passosReduzido: 12, pausaFim: 900, pausaFimKo: 1800, pausaSerie: 1500 } as const;

let timer: ReturnType<typeof setTimeout> | undefined;
/** para o palco (sai da tela: Continuar, ou outra luta comecou) */
export function fecharPalcoPoc(): void { clearTimeout(timer); LUTA_POC.palco = null; LUTA_POC.lutando = false; avisar(); }

function criar(l: LutaNaTela): LutaPoc {
  const L = criarLutaPoc(configLutaPoc(l.entrada), sorteiosPoc(l.entrada.semente));
  L.eventos = [];
  return L;
}

/** assiste as lutas (ja decididas) no palco, uma depois da outra; no fim, `fim(ultima)` da o resultado que aparece depois da luta */
export function assistirPoc(lutas: readonly LutaNaTela[], contexto: string, fim: (L: LutaPoc) => FimPoc): void {
  if (!lutas.length) throw new Error("palco: nenhuma luta para assistir");
  clearTimeout(timer);
  for (const l of lutas) arquivosPoc(l.entrada.cena);
  void carregarEfeitos();
  const reduz = movimentoReduzido();
  let j = 0;
  const abrir = () => {
    const l = lutas[j];
    LUTA_POC.palco = { L: criar(l), v: visualNovoPoc(), A: l.A, B: l.B, cena: l.entrada.cena, k: j, n: lutas.length, rotulo: l.rotulo, contexto, fim: null };
  };
  const conferir = (p: PalcoPoc) => {
    const e = lutas[j].esperado; if (!e) return;
    const L = p.L, passos = passoDe(L);
    if (L.vencedor !== e.vencedor || L.relogio !== e.relogio || passos !== e.passos) {
      LUTA_POC.lutando = false; avisar();
      throw new Error(`a luta refeita no palco não bate com a do motor: vencedor ${L.vencedor} × ${e.vencedor}, relógio ${L.relogio} × ${e.relogio}, passos ${passos} × ${e.passos}`);
    }
  };
  /** um quadro: os passos da luta deste quadro (a camera lenta no fim de uma luta que acaba em nocaute) */
  const quadro = () => {
    const p = LUTA_POC.palco; if (!p) return;
    const L = p.L, e = lutas[j].esperado, base = reduz ? RITMO_POC.passosReduzido : RITMO_POC.passos;
    const n = e ? passosDoQuadro(passoDe(L), base, { passos: e.passos, fim: e.ko ? "ko" : "limite" }, reduz) : base;
    for (let q = 0; q < n && !L.fim && L.relogio < LIMITE_POC_MS; q++) aplicarEventosPoc(p.v, L, passoPoc(L), [p.A.forma, p.B.forma]);
    avisar();
    if (L.fim || L.relogio >= LIMITE_POC_MS) { conferir(p); esperar(); return; }
    timer = setTimeout(quadro, RITMO_POC.quadroMs + consumirPausaPoc(p.v, reduz));
  };
  /** a espera depois do fim (o nocaute fica na tela): os efeitos do ultimo golpe acabam de sumir (visual.extra) */
  const esperar = () => {
    const p = LUTA_POC.palco!, ko = p.L.a.morto || p.L.b.morto, ultima = j === lutas.length - 1;
    let falta = Math.ceil((ultima ? (ko ? RITMO_POC.pausaFimKo : RITMO_POC.pausaFim) : RITMO_POC.pausaSerie) / RITMO_POC.quadroMs), k = 0;
    const tic = () => {
      p.v.extra += passosDaEspera(k++, RITMO_POC.passos, ko, reduz); avisar();
      if (--falta > 0) { timer = setTimeout(tic, RITMO_POC.quadroMs); return; }
      if (!ultima) { j++; abrir(); avisar(); timer = setTimeout(quadro, RITMO_POC.quadroMs); return; }
      p.fim = fim(p.L); LUTA_POC.lutando = false; avisar();
    };
    timer = setTimeout(tic, RITMO_POC.quadroMs);
  };
  LUTA_POC.lutando = true;
  abrir(); avisar();
  timer = setTimeout(quadro, RITMO_POC.quadroMs);
}

/** "no Coliseu", "na Floresta Green Shade": o artigo de cada mapa */
const NA: Record<IdCena, string> = { campo: "no", coliseu: "no", floresta: "na", praia: "na", deserto: "no", castelo: "no", caverna: "na", ringue: "no" };
export const naCena = (id: IdCena): string => `${NA[id]} ${CENAS[id].nome}`;
/** o texto do fim de uma luta do pet (o lado a) */
export function fimDoPet(L: LutaPoc, A: LadoDesenhoPoc, B: LadoDesenhoPoc, extra = ""): FimPoc {
  const s = (L.relogio / 1000).toFixed(1).replace(".", ",");
  const venceu = L.vencedor === "a" ? true : L.vencedor === "b" ? false : null;
  const duplo = L.a.morto && L.b.morto, titulo = venceu ? `${A.nomeTela} venceu` : venceu === false ? `${B.nomeTela} venceu` : "Empate";
  const como = duplo ? "os dois caíram (nocaute duplo)" : L.vencedor !== null ? "por nocaute" : "no limite de tempo";
  return { titulo, venceu, texto: `${titulo} em ${s} s, ${como}, ${naCena(L.cena.id)}.${extra ? " " + extra : ""}` };
}

/* ---------------------------------------------------------------- a luta montada (a conferencia e as capturas) */
/** ?luta_poc=1&palco_poc=<mapa>,<forma do lado azul>,<forma do lado vermelho>,<semente>: uma luta montada direto no nucleo, com o perfil
    canonico de cada forma (statsRivalArena) ou o do NPC (statsNpc), sem pet e sem registro. So com a chave ligada; nada grava */
export function lutaMontadaDoEndereco(busca: string = typeof location !== "undefined" ? location.search : ""): LutaNaTela | null {
  if (!lutaPocLigada()) return null;
  const q = new URLSearchParams(busca).get("palco_poc"); if (!q) return null;
  const [cena, fa, fb, s] = q.split(",");
  if (!(cena in CENAS)) throw new Error(`palco_poc: mapa desconhecido ${cena}`);
  for (const f of [fa, fb]) if (!f || !naTabela(f)) throw new Error(`palco_poc: forma fora da tabela ${f}`);
  const semente = Number(s); if (!Number.isInteger(semente)) throw new Error(`palco_poc: semente inválida ${s}`);
  const st = (k: string) => (NPC[k] ? statsNpc(k) : statsRivalArena(k));
  return { entrada: { cena: cena as IdCena, semente, a: { forma: fa, stats: st(fa) }, b: { forma: fb, stats: st(fb) } }, esperado: null, A: ladoDesenho(fa), B: ladoDesenho(fb), rotulo: "" };
}
