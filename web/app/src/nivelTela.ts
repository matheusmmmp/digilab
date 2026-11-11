/* O nivel do Tamer na tela (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md; a conta pura e o nivel.ts). Aqui ficam o que toca o navegador:
   - a chave propria CHAVE-nivel (preferencia de tela, como -hud e -dicas; NUNCA no save, nem no registro do Tamer): os marcos ja feitos e os
     cartoes ja vistos, em JSON. Nao existe na primeira visita; quem ja tem pet ou Tamer e nao a tem entra com o piso 4 (P-6);
   - o jogo e os pets que alimentam a conta: o pet ativo (motorReal), os guardados e o registro do Tamer. Um criterio so diz quem NAO e do jogador (o mesmo para o
     ativo e os guardados): o pet de exemplo das boas-vindas e os da escada que o pets.ts semeia no primeiro acesso, enquanto estiverem intocados (so o tempo
     passou: nivel.ts, `assinaturaIntocada`). Se o jogador cuidou do exemplo ou jogou com um da escada, ele conta;
   - as travas: o estado dos tres lugares da ilha (trancas.ts, que a vista 3D le), os brilhos de "acabou de abrir", o aviso de leitor de tela e o cartao do
     motivo que a tecla, a rota ou o toque num lugar trancado abrem (3.4);
   - o cartao de destrave: pede a fila das dicas (dicas.ts) e sai dela quando visto.
   NADA acontece durante o render: `calcularNivel` so le (a chave, o jogo) e guarda o resultado; gravar a chave, as travas, os brilhos e o aviso saem no efeito
   (`confirmarNivel`, chamado pelo useNivelRaiz). So vista: nada aqui muda o motor, o save, o registro do Tamer nem o replay; "a vista nunca abre antes do motor". */
import { VERSOES_PET } from "../motor/index.ts";
import { useEffect, useSyncExternalStore } from "react";
import { type Motor } from "../motor/index.ts";
import { motorReal, pagarNivel, tamerAtual, useJogo } from "./jogo.ts";
import { CHAVE_GUARDADOS, abrirGuardado, lerGuardados } from "./pets.ts";
import { CHAVE, SEMENTE_EXEMPLO, petExemplo } from "./save.ts";
import { dicasLigadas, pedirCartao, retirarCartao, esquecerDicasVistas } from "./dicas.ts";
import { definirTrancas } from "./trancas.ts";
import {
  LUGAR_DA_PECA, PECAS, PECA_DO_LUGAR, VIDA_MARCO_MIN, anuncioDeAbertura, assinaturaIntocada, cartoesPendentes, ehPetIntocado, jaConheco, lerEstado, marcarCartao, marcosFeitos,
  nivelDe, pecaAberta, reverTutorial, sincronizar, textoEstado, vidaDoPet, type EstadoNivel, type Peca,
} from "./nivel.ts";
import type { Lugar } from "./viagem.ts";
import { emitirSom } from "./somEventos.ts";

export const CHAVE_NIVEL = CHAVE + "-nivel";

/** os guardados sao lidos (e reproduzidos) no maximo a cada tanto: eles nao andam, so mudam quando o jogador mexe. PROPOSTO, SEM FONTE (interface) */
const GUARDADOS_MS = 1500;

/* ---------------------------------------------------------------------------------------------------- quem nao e do jogador */
/* desde a LP2 da LUTA_POC (e para todos desde a LP4) a escada de exemplo nao e semeada: so o pet de exemplo. A assinatura dele sai da
   simulacao da vida de exemplo, feita so quando o pet tem a semente do exemplo e uma vez por versao: o pet de exemplo de quem abriu o jogo
   antes da v22 (ILHA_AGUA, IA4) e v21 e continua valendo como "nao e do jogador" */
const assinaturasDoExemplo = new Map<number, ReadonlySet<string>>();
function assinaturaDoExemplo(versao: number): ReadonlySet<string> {
  let s = assinaturasDoExemplo.get(versao);
  if (!s) {
    s = new Set(VERSOES_PET.includes(versao) ? [assinaturaIntocada(petExemplo(versao))] : []);
    assinaturasDoExemplo.set(versao, s);
  }
  return s;
}
/** o pet e do jogador: nao e o de exemplo ainda intocado (o criterio do ativo e dos guardados) */
export function ehPetDoJogador(m: Motor): boolean {
  if (m.semente !== SEMENTE_EXEMPLO) return true;
  return !ehPetIntocado(m, assinaturaDoExemplo(m.versao));
}

/* ---------------------------------------------------------------------------------------------------- o estado do modulo */
/** o estado confirmado (gravado): undefined = a chave ainda nao foi lida; null = nao ha chave */
let confirmado: EstadoNivel | null | undefined;
let versaoConfirmado = 0;
const ouvintes = new Set<() => void>();
const avisar = (): void => { for (const o of ouvintes) o(); };

function lerChave(): EstadoNivel | null {
  let texto: string | null = null;
  try { texto = localStorage.getItem(CHAVE_NIVEL); } catch { return null; }
  try { return lerEstado(texto); } catch (err) {
    /* a chave nao abre: o piso 4 refaz o nivel de quem ja joga (nada se perde do jogo), e o erro fica a vista no console */
    console.error("o nivel gravado nao abriu; recomecando pelo piso:", err);
    return null;
  }
}
function gravarChave(e: EstadoNivel): void {
  try { localStorage.setItem(CHAVE_NIVEL, textoEstado(e)); } catch { /* preferencia de tela: sem armazenamento, vale so nesta sessao */ }
}

/* ---------------------------------------------------------------------------------------------------- os guardados */
let guardados: { quando: number; raw: string | null; motores: Motor[]; id: number } | null = null, idGuardados = 0;
function guardadosDoJogador(agora: number): { motores: Motor[]; id: number } {
  if (guardados && agora - guardados.quando < GUARDADOS_MS) return guardados;
  let raw: string | null = null;
  try { raw = localStorage.getItem(CHAVE_GUARDADOS); } catch { raw = null; }
  if (guardados && guardados.raw === raw) { guardados.quando = agora; return guardados; }
  const motores: Motor[] = [];
  try {
    for (const g of lerGuardados()) {
      try { const m = abrirGuardado(g); if (ehPetDoJogador(m)) motores.push(m); } catch (err) { console.error("nivel: um pet guardado nao abriu:", err); }
    }
  } catch (err) { console.error("nivel: os pets guardados nao abriram:", err); }
  guardados = { quando: agora, raw, motores, id: ++idGuardados };
  return guardados;
}

/* ---------------------------------------------------------------------------------------------------- a avaliacao (sem efeito colateral) */
interface Resultado { estado: EstadoNivel; novos: number[] }
let memo: { chave: string; r: Resultado } | null = null;
let brilhos = new Set<Lugar>();
/** os lugares que acabaram de abrir e ainda nao brilharam (o brilho consome na hora de desenhar) */
export const brilhosPendentes = (): readonly Lugar[] => [...brilhos];
export function consumirBrilho(l: Lugar): void { brilhos.delete(l); }
/** muda quando ha brilho novo (quem desenha a ilha o le para recolher os pendentes, mesmo que o efeito da casca rode depois do dele) */
let versaoBrilhos = 0;
const ouvBrilhos = new Set<() => void>();
export function useVersaoBrilhos(): number {
  return useSyncExternalStore(o => { ouvBrilhos.add(o); return () => { ouvBrilhos.delete(o); }; }, () => versaoBrilhos, () => 0);
}

/** o nivel de agora, so lendo: junta os marcos do Tamer e dos pets contra o estado confirmado. O mesmo resultado (o mesmo objeto) enquanto nada que conta mudar */
function calcularNivel(): Resultado {
  if (confirmado === undefined) confirmado = lerChave();
  const ativo = motorReal(), t = tamerAtual(), g = guardadosDoJogador(performance.now());
  const doJogador = ehPetDoJogador(ativo);
  const chave = [ativo.semente, ativo.log.length, ativo.evolucoes.length, ativo.chamados.atendidos, ativo.estagioAtual, vidaDoPet(ativo) >= VIDA_MARCO_MIN ? 1 : 0, doJogador ? 1 : 0,
    t.log.length, g.id, versaoConfirmado].join("|");
  if (memo && memo.chave === chave) return memo.r;
  const pets: Motor[] = [...(doJogador ? [ativo] : []), ...g.motores];
  const r = sincronizar(confirmado, marcosFeitos(pets, t), pets.length > 0 || t.log.length > 0);
  memo = { chave, r };
  return r;
}
const lerAgora = (): EstadoNivel => calcularNivel().estado;

/** o efeito da casca: confirma o resultado (grava a chave, poe as travas, guarda os brilhos e o aviso dos lugares que abriram) */
function confirmarNivel(): void {
  const r = calcularNivel(), antes = confirmado;
  /* os Bits de cada nivel do Tamer (docs/PLANO_V3_MOEDA.md, MO1): pagos uma vez, a partir do nivel confirmado (com o piso dos saves antigos) */
  pagarNivel(nivelDe(r.estado));
  definirTrancas({ saco: !pecaAberta(r.estado, "crescer"), portao: !pecaAberta(r.estado, "lutar"), barraca: !pecaAberta(r.estado, "diario") });
  if (antes !== null && r.estado === antes) return;
  confirmado = r.estado; versaoConfirmado++;
  gravarChave(r.estado);
  /* o lugar que acabou de abrir brilha uma vez (quando a ilha aparecer) e o leitor de tela ouve o que abriu */
  for (const n of r.novos) for (const p of Object.keys(LUGAR_DA_PECA) as Peca[]) if (PECAS[p].marco === n) brilhos.add(LUGAR_DA_PECA[p]!);
  if (brilhos.size) { versaoBrilhos++; for (const o of ouvBrilhos) o(); }
  if (antes !== null && r.novos.length) emitirSom("nivel");   /* SOM-UP: o nivel novo (nao na primeira leitura) */
  const fala = anuncioDeAbertura(r.novos);
  if (fala) falar(fala);
  avisar();
}

/** a casca (App): a cada mudanca do jogo calcula, confirma no efeito e pede os cartoes pendentes */
export function useNivelRaiz(): EstadoNivel {
  useJogo();
  const e = lerAgora(), pend = cartoesPendentes(e).join(","), ligadas = dicasLigadas();
  useEffect(() => { confirmarNivel(); });
  useEffect(() => { for (const n of cartoesPendentes(e)) pedirCartao(n); }, [pend, e, ligadas]);
  return useSyncExternalStore(assinar, lerAgora, lerAgora);
}
/** quem so le (o trilho, a coluna, o minimapa, as abas): muda quando o estado muda */
export function useNivel(): EstadoNivel { return useSyncExternalStore(assinar, lerAgora, lerAgora); }
function assinar(o: () => void): () => void { ouvintes.add(o); return () => { ouvintes.delete(o); }; }

/* ---------------------------------------------------------------------------------------------------- consultas */
export const nivelAgora = (): number => nivelDe(lerAgora());
export const pecaLiberada = (p: Peca): boolean => pecaAberta(lerAgora(), p);

/* ---------------------------------------------------------------------------------------------------- as acoes */
function mudar(novo: EstadoNivel): void {
  if (novo === confirmado) return;
  confirmado = novo; versaoConfirmado++; gravarChave(novo); avisar();
}
/** o cartao do marco `n` foi visto (Ir, Depois ou Esc): sai da fila e nao volta */
export function cartaoVisto(n: number): void {
  retirarCartao(n);
  mudar(marcarCartao(lerAgora(), n));
}
/** "Ja conheco o jogo" (boas-vindas, P-7): abre os niveis 1 a 4 e pula os cartoes deles */
export function jaConhecoOJogo(): void {
  mudar(jaConheco(lerAgora()));
  for (const n of [1, 2, 3, 4]) retirarCartao(n);
}
/** "Rever o tutorial" (Ajustes, 4.3): limpa os cartoes e as dicas vistas; cada um volta no proximo momento dele */
export function reverOTutorial(): void {
  mudar(reverTutorial(lerAgora()));
  esquecerDicasVistas();
}

/* ---------------------------------------------------------------------------------------------------- o aviso de leitor de tela */
let aviso = "";
const ouvAviso = new Set<() => void>();
function falar(t: string): void { aviso = t; for (const o of ouvAviso) o(); }
/** o texto do "Diario aberto" e afins (a regiao aria-live da casca: AnuncioNivel); vale mesmo sem o cartao */
export function useAnuncioNivel(): string {
  return useSyncExternalStore(o => { ouvAviso.add(o); return () => { ouvAviso.delete(o); }; }, () => aviso, () => "");
}

/* ---------------------------------------------------------------------------------------------------- o cartao do motivo (3.4) */
/** a peca trancada cujo motivo o cartao mostra (a tecla, a rota ou o toque num lugar trancado), ou null */
let motivo: Peca | null = null;
const ouvMotivo = new Set<() => void>();
export function abrirMotivo(p: Peca): void { motivo = p; for (const o of ouvMotivo) o(); }
export function fecharMotivo(): void { if (motivo === null) return; motivo = null; for (const o of ouvMotivo) o(); }
export function useMotivo(): Peca | null {
  return useSyncExternalStore(o => { ouvMotivo.add(o); return () => { ouvMotivo.delete(o); }; }, () => motivo, () => null);
}

/** o lugar da ilha esta trancado agora (ao tocar nele) */
export const lugarTrancado = (l: Lugar): boolean => !pecaLiberada(PECA_DO_LUGAR[l]);
