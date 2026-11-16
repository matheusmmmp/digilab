/* O nivel do Tamer (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, secoes 3.3, 3.4, 4 e 5; decisoes P-1 a P-11 do Matheus, 2026-11-06). So a vista (P-5, opcao V):
   uma funcao pura que le o registro do Tamer e os pets do jogador e devolve os marcos feitos; o nivel e a CONTAGEM dos marcos (3.2), sem XP.
   Nada aqui entra no motor, no save, no registro do Tamer nem nos gabaritos, e "a vista nunca abre antes do motor": cada peca so anuncia o que
   o motor ja libera. Sem DOM e sem armazenamento (o armazenamento e o nivelTela.ts); o teste le este modulo sozinho.
   - os marcos (3.3): 1 chocou o ovo, 2 atendeu 3 chamados, 3 virou Rookie, 4 o primeiro treino, 5 a primeira medalha, 6 virou Champion, 7 tres
     medalhas, 8 seis medalhas, 9 o titulo da Liga; 10 o primeiro Mega
     (MMO-13, docs/PLANO_V3_MMO.md, etapa MMO2): o marco que abre o multijogador, o unico que tambem vai para o registro do Tamer (P-5,
     opcao T; o evento "nivel" de src/tamer.ts). O cartao do 10 espera a prancha (a tela 1 das pranchas do MMO): sem cartao, o marco conta
     em silencio;
   - CADA PECA ABRE PELO PROPRIO MARCO, nao pelo numero (pergunta 11 da prancha): "Tamer Nv N" e so a contagem. Um save com o Champion e sem a
     primeira medalha tem o Nv 5 (chocou, chamados, Rookie, treino, Champion), e o Forcar (marco 6) abre enquanto os Itens (marco 5) nao.
     As Regras de luta (o editor dos gambits, tambem no marco 6) sairam com o combate por turnos (LUTA_POC, LP4): o cartao do Nv 6 passou a ser
     o do Forcar;
   - o estado que a tela guarda (EstadoNivel) tem os marcos ja feitos (a uniao de tudo que ja se viu: o nivel nunca desce, mesmo que um pet
     guardado saia) e os cartoes de destrave ja vistos. Quem tem pet ou Tamer e nao tem o estado entra com o PISO 4 (P-6): os marcos 1 a 4 e os
     cartoes deles vistos em silencio, para nunca trancar o que o jogador ja usava.
   Os numeros e os textos sao PROPOSTO, SEM FONTE (numero de interface, nao de jogo). */
import { TICK_INICIAL, type Motor } from "../motor/index.ts";
import { MARCO_MEGA, evolucaoMega, type Tamer } from "./tamer.ts";
import type { Aba, Destino, Rota } from "./rotas.ts";
import type { Lugar } from "./viagem.ts";

/** o piso dos saves de antes (P-6): Pet, Diario, Crescer e Lutar abertos */
export const PISO_NIVEL = 4;
/** o ultimo marco: o 10, o primeiro Mega (MMO-13); do 11 em diante, o nivel sera lido no Respeito (MMO-15, a MMO8) */
export const ULTIMO_MARCO = 10;
/** os chamados atendidos do marco 2 e a vida minima (min do pet) que o vale quando o contador nao serve. PROPOSTO, SEM FONTE */
export const CHAMADOS_MARCO = 3, VIDA_MARCO_MIN = 60;
/** as medalhas dos marcos 5, 7 e 8 (a ultima e MEDALHAS_LIGA, a trava de hoje da Fronteira) */
export const MEDALHAS_MARCO = { primeira: 1, tres: 3, seis: 6 } as const;
/* ---------------------------------------------------------------------------------------------------- os cartoes */
/** o nome do icone (lucide) de cada cartao; quem desenha troca o nome pelo componente */
export type IconeNivel = "heart" | "tent" | "dumbbell" | "swords" | "package" | "shield" | "medal" | "flag" | "trophy";
/** o cartao de destrave de um marco (4.1 tipo A e 4.2): o icone, o titulo (ate 3 palavras), a frase (ate 8) e, se ha lugar para ir, a rota */
export interface Cartao { n: number; icone: IconeNivel; titulo: string; frase: string; rota?: Rota; lugar?: Lugar }
export const CARTOES: readonly Cartao[] = [
  { n: 1, icone: "heart", titulo: "Cuide dele", frase: "Ele chama quando precisa. Atenda logo." },
  { n: 2, icone: "tent", titulo: "Diário", frase: "Veja o que ele fez e por quê.", rota: { destino: "diario", aba: "registro" }, lugar: "barraca" },
  /* o nivel 3 abre Crescer e Conversar (4.2 tem duas linhas); um cartao por nivel (4.1, "uma vez por nivel"), o do saco */
  { n: 3, icone: "dumbbell", titulo: "Crescer", frase: "Treine no saco de pancada.", rota: { destino: "crescer", aba: "treinar" }, lugar: "saco" },
  { n: 4, icone: "swords", titulo: "Lutar", frase: "Vença rivais. Medalhas fazem evoluir.", rota: { destino: "lutar", aba: "arena" }, lugar: "portao" },
  { n: 5, icone: "package", titulo: "Itens", frase: "A medalha trouxe um chip.", rota: { destino: "crescer", aba: "itens" } },
  { n: 6, icone: "shield", titulo: "Forçar o treino", frase: "Treine além do cansaço, com cuidado.", rota: { destino: "crescer", aba: "treinar" } },
  { n: 7, icone: "medal", titulo: "3 medalhas", frase: "O Ultimate está a caminho." },
  { n: 8, icone: "flag", titulo: "Fronteira", frase: "Seis medalhas. A Liga abriu.", rota: { destino: "lutar", aba: "fronteira" } },
  { n: 9, icone: "trophy", titulo: "Campeão", frase: "A Fábrica e o Salão abriram.", rota: { destino: "lutar", aba: "fronteira" } },
];
export const cartaoDe = (n: number): Cartao | undefined => CARTOES.find(c => c.n === n);

/* ---------------------------------------------------------------------------------------------------- as pecas */
/** o que a trava segura: os menus (Diario, Crescer, Lutar, Conversar), as abas Itens e Fronteira e, dentro do treino, o Forcar */
export type Peca = "diario" | "crescer" | "conversar" | "lutar" | "itens" | "forcar" | "fronteira";
export interface DadosPeca { nome: string; marco: number; motivo: string }
/** o marco de cada peca e o motivo dito ao jogador (os textos da prancha, 3.4 "Abre quando ele virar Rookie" e afins) */
export const PECAS: Readonly<Record<Peca, DadosPeca>> = {
  diario: { nome: "Diário", marco: 2, motivo: "Abre com 3 chamados atendidos" },
  crescer: { nome: "Crescer", marco: 3, motivo: "Abre quando ele virar Rookie" },
  conversar: { nome: "Conversar", marco: 3, motivo: "Abre quando ele virar Rookie" },
  lutar: { nome: "Lutar", marco: 4, motivo: "Abre com o primeiro treino" },
  itens: { nome: "Itens", marco: 5, motivo: "Abre com a primeira medalha" },
  forcar: { nome: "Forçar", marco: 6, motivo: "Abre quando ele virar Champion" },
  fronteira: { nome: "Fronteira", marco: 8, motivo: "Abre com 6 medalhas" },
};
/** o numero que o cadeado mostra ("Nv 3"): e o do marco da peca */
export const nivelDaPeca = (p: Peca): number => PECAS[p].marco;
/** a peca que o menu e (Pet e Ajustes nao tem) */
export function pecaDoDestino(d: Destino): Peca | null {
  return d === "diario" ? "diario" : d === "crescer" ? "crescer" : d === "lutar" ? "lutar" : d === "conversar" ? "conversar" : null;
}
/** a peca que a aba e (so Itens e Fronteira tem trava propria) */
export const pecaDaAba = (a: Aba): Peca | null => a === "itens" ? "itens" : a === "fronteira" ? "fronteira" : null;
/** o lugar da ilha de cada menu trancavel (o saco, o portao e a barraca) */
export const LUGAR_DA_PECA: Readonly<Partial<Record<Peca, Lugar>>> = { crescer: "saco", lutar: "portao", diario: "barraca" };
/** o contrario: a peca que cada lugar da ilha guarda */
export const PECA_DO_LUGAR: Readonly<Record<Lugar, Peca>> = { saco: "crescer", portao: "lutar", barraca: "diario" };

/* ---------------------------------------------------------------------------------------------------- os marcos */
/** a vida do pet em minutos (o tick de agora menos o do ovo) */
export const vidaDoPet = (m: Motor): number => m.e.tick - TICK_INICIAL;
/** os marcos que um pet cumpre (1 so por existir; 2, 3, 4, 6 e 10 pelo registro dele). O contador de chamados zera na evolucao (motor.ts, _evoluir), entao o
    marco 2 tambem vale com 1 h de vida quando o contador nao serve: o pet fora do In-Training, ou sem as chaves de produto dos chamados (3.3, linha 2) */
export function marcosDoPet(m: Motor): number[] {
  const out = [1], vida = vidaDoPet(m), semChaves = !m.produto.chamadoPelaFome && !m.produto.chamadosPeloCorpo;
  if (m.chamados.atendidos >= CHAMADOS_MARCO || (vida >= VIDA_MARCO_MIN && (semChaves || m.estagioAtual !== "bebe"))) out.push(2);
  if (m.evolucoes.some(x => x.estagio === "crianca")) out.push(3);
  if (m.log.some(e => e[1] === "tr")) out.push(4);
  if (m.evolucoes.some(x => x.estagio === "adolescente")) out.push(6);
  if (evolucaoMega(m)) out.push(MARCO_MEGA);
  return out;
}
/** os marcos que o registro do Tamer cumpre: as medalhas (5, 7, 8), o titulo da Liga (9) e o marco 10 gravado (MMO2; o pet que o fez pode
    ter saido) */
export function marcosDoTamer(t: Tamer): number[] {
  const out: number[] = [], n = t.medalhas.length;
  if (n >= MEDALHAS_MARCO.primeira) out.push(5);
  if (n >= MEDALHAS_MARCO.tres) out.push(7);
  if (n >= MEDALHAS_MARCO.seis) out.push(8);
  if (t.titulo) out.push(9);
  if (t.marco(MARCO_MEGA)) out.push(MARCO_MEGA);
  return out;
}
/** a uniao dos marcos do Tamer e dos pets (o ativo e os guardados; sem o pet de exemplo), em ordem */
export function marcosFeitos(pets: readonly Motor[], t: Tamer): number[] {
  const s = new Set<number>(marcosDoTamer(t));
  for (const m of pets) for (const n of marcosDoPet(m)) s.add(n);
  return [...s].sort((a, b) => a - b);
}
/** a assinatura de um pet INTOCADO: a semente, a versao e o registro sem o tempo ("t"). O pet de exemplo das boas-vindas e os da escada semeada (pets.ts) so valem
    como "nao e do jogador" enquanto so o tempo passou neles: um evento a mais (um cuidado, um treino, uma luta) o faz do jogador, ativo ou guardado (um criterio so) */
/*  A passagem para a ilha com agua ("mi"; ILHA_AGUA, IA4) e do jogo, nao do jogador: tambem nao conta */
export const assinaturaIntocada = (m: Motor): string => JSON.stringify([m.semente, m.versao, m.log.filter(e => e[1] !== "t" && e[1] !== "mi" && e[1] !== "ma")]);
/** o pet esta intocado, igual a um dos semeados (`semeados` = as assinaturas do exemplo e da escada) */
export const ehPetIntocado = (m: Motor, semeados: ReadonlySet<string>): boolean => semeados.has(assinaturaIntocada(m));
/** o aviso de leitor de tela do que abriu ("Diario aberto"; "Crescer e Conversar abertos"), pelos marcos novos; "" se nenhum abre uma peca */
export function anuncioDeAbertura(novos: readonly number[]): string {
  const nomes = (Object.values(PECAS) as DadosPeca[]).filter(p => novos.includes(p.marco)).map(p => p.nome);
  if (!nomes.length) return "";
  return `${nomes.length > 1 ? nomes.slice(0, -1).join(", ") + " e " + nomes[nomes.length - 1] : nomes[0]} ${nomes.length > 1 ? "abertos" : "aberto"}`;
}

/* ---------------------------------------------------------------------------------------------------- o estado */
/** o que a tela guarda (CHAVE-nivel): os marcos ja feitos e os cartoes ja vistos. Nunca no save */
export interface EstadoNivel { marcos: number[]; cartoes: number[] }
const unico = (a: readonly number[]): number[] => [...new Set(a)].sort((x, y) => x - y);
const valido = (x: unknown): x is number[] => Array.isArray(x) && x.every(n => Number.isInteger(n) && n >= 1 && n <= ULTIMO_MARCO);

/** le o texto da chave; null se nao ha. Texto que nao e o estado falha alto (quem chama decide o que fazer) */
export function lerEstado(texto: string | null): EstadoNivel | null {
  if (texto === null) return null;
  const d = JSON.parse(texto) as { marcos?: unknown; cartoes?: unknown };
  if (!d || !valido(d.marcos) || !valido(d.cartoes)) throw new Error("o nivel gravado nao tem marcos e cartoes validos");
  return { marcos: unico(d.marcos), cartoes: unico(d.cartoes) };
}
export const textoEstado = (e: EstadoNivel): string => JSON.stringify({ marcos: e.marcos, cartoes: e.cartoes });

/** a conta de cada abertura: o estado novo e os marcos que acabaram de ser feitos (os que pedem cartao e brilho).
    - sem o estado e sem jogo (primeira visita): vazio, Nv 0;
    - sem o estado e com pet ou Tamer: o piso 4 (P-6), os cartoes dos marcos de agora vistos em silencio, nenhum "novo";
    - com o estado: a uniao; os marcos fora do estado de antes sao os novos (o nivel nunca desce) */
export function sincronizar(antes: EstadoNivel | null, feitos: readonly number[], haJogo: boolean): { estado: EstadoNivel; novos: number[] } {
  if (antes === null) {
    if (!haJogo) return { estado: { marcos: [], cartoes: [] }, novos: [] };
    const marcos = unico([...feitos, ...Array.from({ length: PISO_NIVEL }, (_, i) => i + 1)]);
    return { estado: { marcos, cartoes: marcos }, novos: [] };
  }
  const marcos = unico([...antes.marcos, ...feitos]);
  return { estado: marcos.length === antes.marcos.length ? antes : { marcos, cartoes: antes.cartoes }, novos: marcos.filter(n => !antes.marcos.includes(n)) };
}
/** o nivel do Tamer: a quantidade de marcos (3.2) */
export const nivelDe = (e: EstadoNivel): number => e.marcos.length;
/** a peca esta aberta: o marco dela esta feito */
export const pecaAberta = (e: EstadoNivel, p: Peca): boolean => e.marcos.includes(PECAS[p].marco);
/** os marcos feitos cujo cartao ainda nao foi visto, em ordem */
export const cartoesPendentes = (e: EstadoNivel): number[] => e.marcos.filter(n => !e.cartoes.includes(n) && !!cartaoDe(n));
/** o cartao do marco `n` foi visto (Ir, Depois ou Esc) */
export const marcarCartao = (e: EstadoNivel, n: number): EstadoNivel => e.cartoes.includes(n) ? e : { marcos: e.marcos, cartoes: unico([...e.cartoes, n]) };
/** "Ja conheco o jogo" (P-7): abre os niveis 1 a 4 e pula os cartoes deles. O resto (Itens, Fronteira) segue os marcos */
export function jaConheco(e: EstadoNivel): EstadoNivel {
  const piso = Array.from({ length: PISO_NIVEL }, (_, i) => i + 1);
  return { marcos: unico([...e.marcos, ...piso]), cartoes: unico([...e.cartoes, ...piso]) };
}
/** "Rever o tutorial" (4.3): os cartoes voltam a valer (as dicas vistas sao do dicas.ts). Os marcos ficam: nada tranca de novo */
export const reverTutorial = (e: EstadoNivel): EstadoNivel => ({ marcos: e.marcos, cartoes: [] });
