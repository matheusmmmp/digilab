/* Luta (Arena e Campanha): um estado so, compartilhado pelas duas abas; o palco aparece na aba visivel e cada
   aba reinicia o palco para o proprio modo quando abre (a mensagem de um modo nao vaza para o outro, revisao
   item 1). A luta entra no registro na hora (motor.lutar); o palco refaz a luta em tempo real passo a passo, da entrada que o motor
   guardou no resultado (motor/combate_tr: criarLutaTR e passoTR), e confere que o fim e o mesmo (COMBATE-TR, etapa R3). */
import { useEffect, useState } from "react";
import {
  BOTS_V21, BOT_TRACO, CAT, CTR_TR, LIGA, NOME_ARQ, NOME_BOT, NOME_ESP, NOME_EST, NPC, PASSO_TR_MS, RIVAL_LIGA, RIVAL_SALAO, cartaDe, criarLutaTR, formaRivalSalao,
  chaveSprite, corDominante, estadoV2, formaLiga, formaRival, formaRivalInstalacao, hashSemente, instalacaoDe, lutadorBot, lutadorPet, medalhaDoLider, nomeForma,
  passoTR, type Arena, type Estagio, type EstadoTR, type EventoTR, type FormaAdultaNormal, type IdInstalacao, type Instalacao, type Lutador, type LutaTR, Motor,
  type ResultadoLuta, type TracoCombate, duracaoLuta, jogarLuta, tamanhoLuta,
} from "../motor/index.ts";
import { cenaDaLuta, type IdCenaTR } from "./telas/lutar/palcoTR/cenasTR.ts";
import { aplicarEventosTR, visualNovoTR, type VisualTR } from "./telas/lutar/palcoTR/desenhoTR.ts";
import { gradeDe } from "./grades.ts";
import { jogoAtual, mudarMotor, mudarTamer, tamerAtual } from "./jogo.ts";
import { ehLuta } from "./rotas.ts";
import { conferirRevanche, type Campeao, type ItemGanho, type MedalhaGanha, type Recorde } from "./tamer.ts";
import { SOM } from "./som.ts";

/** "limite de turnos" (por turnos) ou "limite de tempo" (pets v13, em tempo real) */
const limiteDe = (_res: ResultadoLuta): string => "limite de tempo";

/* bots classicos: Digimon do mapa da Etapa 0 (so rotulo) */
import { DIGIMON_BOT } from "./nomesRivais.ts";
export { DIGIMON_BOT };
export const RIVAIS_CLASSICOS = ["aleatorio", "agressivo", "tartaruga", "atirador", "contragolpe", "adaptativo", "oraculo"];
export const RIVAIS_ADULTOS: FormaAdultaNormal[] = ["duelista", "furioso", "espelho", "muralha", "sentinela", "emboscador", "vigia", "tita"];

/** o lutador com o que a tela precisa para desenhar (o motor so da estilo e perfil) */
export interface LutadorTela extends Lutador { sprite: string; grade: string; cor: TracoCombate; estagioFala: Estagio; nomeTela: string; estiloTela: string | null }

export function exibirPet(m: Motor, L: Lutador): LutadorTela {
  return { ...L, sprite: chaveSprite(m.forma), grade: gradeDe(m.estagioAtual), cor: corDominante(m.tracos), estagioFala: m.estagioAtual, nomeTela: nomeForma(m.forma), estiloTela: null };
}
/** L: o lutador do bot sob as regras da luta; sem ele, o das regras do pet ativo (V21D nos pets v6; o lider com a regra da
    arena) */
export function exibirBot(nome: string, L: Lutador = lutadorBot(nome, jogoAtual().motor.regras, jogoAtual().motor.arenaDe(nome))): LutadorTela {
  const n = NPC[nome];
  if (n) return { ...L, sprite: n.sprite ?? n.k, grade: n.grade || "adulto", cor: n.cor, estagioFala: n.estagio || "adulto", nomeTela: n.nome, estiloTela: null };
  if (BOTS_V21[nome as FormaAdultaNormal]) {
    const f = formaRival(nome as FormaAdultaNormal);
    return { ...L, sprite: chaveSprite(f), grade: "adulto", cor: "golpe", estagioFala: "adulto", nomeTela: nomeForma(f), estiloTela: NOME_BOT[nome].toLowerCase() };
  }
  return { ...L, sprite: "bot_" + nome, grade: nome === "aleatorio" ? "bebe" : "adulto", cor: BOT_TRACO[nome], estagioFala: "adulto",
    nomeTela: DIGIMON_BOT[nome] || NOME_BOT[nome], estiloTela: DIGIMON_BOT[nome] ? NOME_BOT[nome] : null };
}

/** a aba de onde a luta veio (e para onde ela volta): a Arena, a Campanha ou a Fronteira (a Liga dos Lideres, pets v6) */
export type Modo = "arena" | "campanha" | "fronteira";
/** o Mega do lider i da Liga (motor/liga.ts) como lutador de tela: o sprite do Mega, o nome dele e, no estilo, o arquetipo e o lider */
export function exibirLider(i: number, L: Lutador): LutadorTela {
  const f = formaLiga(i), x = LIGA[i];
  return { ...L, sprite: chaveSprite(f), grade: "adulto", cor: "carga", estagioFala: "mega", nomeTela: nomeForma(f),
    estiloTela: `${NOME_ARQ[x.adulta].toLowerCase()} de ${NPC[x.lider]!.nome}` };
}
/** o rival da luta k (0 = a primeira) de uma tentativa numa instalacao da Fronteira (motor/instalacoes.ts), sorteado da semente dela, como
    lutador de tela: o sprite do Mega, o nome dele e, no estilo, o arquetipo e o brasao */
export function exibirRivalInstalacao(s: number, k: number, L: Lutador): LutadorTela {
  const f = formaRivalInstalacao(s, k);
  return { ...L, sprite: chaveSprite(f), grade: "adulto", cor: "carga", estagioFala: "mega", nomeTela: nomeForma(f),
    estiloTela: `${NOME_ARQ[f.adulta!].toLowerCase()} · ${NOME_ESP[f.esp]}` };
}
/** o rival de uma luta do Salao (pets v6; motor/salao.ts), sorteado da semente e do estagio do pet, como lutador de tela: o sprite, o nome e,
    no estilo, o arquetipo (ou o ramo, ou a linha) e o nivel */
export function exibirRivalSalao(s: number, est: Estagio, L: Lutador): LutadorTela {
  const f = formaRivalSalao(s, est), tipo = f.adulta ?? f.linha ?? f.ramo!;
  return { ...L, sprite: chaveSprite(f), grade: gradeDe(est), cor: "carga", estagioFala: est, nomeTela: nomeForma(f),
    estiloTela: `${NOME_ARQ[tipo].toLowerCase()} · ${NOME_EST[est]}` };
}
/** a vida e o Guts de um lado, para as barras */
export interface HudLado { hp: number; hpMax: number; guts: number; gutsMax: number }
/** a ultima acao que o pet comecou e o motivo dela (o indice da regra, "exploracao" ou "pesado_automatico") */
export interface RegraTR { motivo: number | string; nome: string }
export interface Palco {
  modo: Modo; A: LutadorTela; B: LutadorTela;
  /** o cenario (o mapa do UP do lugar; palcoTR/cenasTR.ts) */
  cena: IdCenaTR;
  hud: HudLado[];
  /** a luta refeita passo a passo (null na previa) e o que so a tela guarda dela (os numeros que sobem, o passo do nocaute de cada lado) */
  sim: LutaTR | null; visual: VisualTR; koEm: (number | null)[];
  /** o relogio da luta (s) e se ja entrou na morte subita; null na previa */
  segundos: number | null; morteSubita: boolean;
  regra: RegraTR | null;
  texto: string; callout: string;
  resultado: ResultadoPalco | null;
  /** replay animado de uma luta do registro chegou ao fim */
  fimReplay?: boolean;
  /** lutas seguidas da arena (Cidadela): a luta que esta no palco (1 = a primeira) e quantas sao; null numa luta so */
  serie?: { k: number; n: number } | null;
  /** a arena da luta (pets v6 contra o lider; motor/arenas.ts); null fora dela */
  arena?: Arena | null;
  /** a Liga dos Lideres (pets v6, modo fronteira): as lutas seguidas sao contra os 6 lideres, sem cura e sem carta */
  liga?: boolean;
  /** uma instalacao da Fronteira (pets v6, modo fronteira): qual, a luta que esta no palco (1 = a primeira: vale a vitoria k) e a vida
      com que o pet comecou esta luta (fracao da maxima); null fora dela */
  sequencia?: { inst: Instalacao; k: number; vida: number } | null;
}
/** rival fixo: o pet B de um cenario (Diario > Cenarios); luta sem ensinar, porque nao e reconstruivel do registro */
/** o que o modal Resultado precisa, tudo do motor: a luta, o estado antes dela e a posicao dela no registro */
export interface ResultadoPalco {
  res: ResultadoLuta; npc: string | null; notasAntes: Record<string, number> | null; cenario: boolean;
  /** regras ativas antes e logo depois da luta (antes de qualquer intervencao do dono na animacao): regra nova = diferenca */
  ativasAntes: string[] | null; ativasDepois: string[] | null;
  /** o lugar ja estava vencido antes (campanha); na arena, true */
  lugarJaVencido: boolean;
  /** lutas de treino (sparring) antes e se esta contou */
  sparringAntes: number; sparringContou: boolean;
  /** indice do evento "l" no registro (replay no Diario); null contra pet de cenario, que nao entra no registro */
  idxLog: number | null;
  /** pets v6: a medalha que o Tamer ganhou com esta luta (primeira vitoria contra o lider); null se nenhuma */
  medalha: MedalhaGanha | null;
  /** as lutas jogadas (a ultima e `res`), quantas a serie tem (1, ou 3 na Cidadela) e a arena (null fora dela) */
  serie: ResultadoLuta[]; nLutas: number; arena: Arena | null;
  /** pets v6 (itens): a carta que valeu nesta luta (null: nenhuma) e os itens que o Tamer ganhou com ela (o da medalha, a carta
      da revanche) */
  carta: string | null; itens: ItemGanho[];
  /** pets v6, a Liga dos Lideres: os 6 lideres na tela (null fora dela) e o titulo que o Tamer ganhou com esta tentativa (null: nenhum) */
  lideres: LutadorTela[] | null; titulo: Campeao | null;
  /** pets v6, uma instalacao da Fronteira: qual, os rivais das lutas jogadas na tela e o recorde do Tamer que esta tentativa bateu (null:
      nenhum); null e [] fora dela */
  instalacao: Instalacao | null; rivais: LutadorTela[] | null; recorde: Recorde | null;
}
export interface RivalFixo { rival: Motor; dias: number; tipo: string }
export const LUTA = { lutando: false, rival: "agressivo", campSel: null as string | null, palco: null as Palco | null, rivalFixo: null as RivalFixo | null,
  /** pets v6: a carta do Tamer escolhida para a proxima luta (Campanha ou Arena); sai quando a luta a usa */
  carta: null as string | null,
  /* tela cheia da luta (#/lutar/luta): pausa e x2 so mudam a animacao; a luta ja esta decidida e no registro */
  pausado: false, rapido: false,
  /** indice no registro da luta que esta sendo revista (replay animado, nada gravado); null numa luta de verdade */
  replay: null as number | null };
/** o relogio do jogo para (so na interface: o motor, o registro e o replay nao mudam) enquanto uma luta e mostrada no palco e enquanto o
    Resultado dela esta aberto (a tela cheia da luta com o resultado no palco). A luta ja entrou no registro na hora; sem isto, na velocidade
    de teste a lesao da derrota que fecha uma sequencia mataria o pet durante a animacao (6 h de jogo em 36 s). Fechado o Resultado, o
    tempo volta a correr de onde parou, sem compensar o tempo parado (tempo.ts descarta o que passou) */
export const lutaSeguraTempo = (): boolean =>
  LUTA.lutando || (LUTA.replay === null && !!LUTA.palco?.resultado && typeof location !== "undefined" && ehLuta(location.hash));
const ouvintes = new Set<() => void>();
export const avisarLuta = (): void => { for (const o of ouvintes) o(); };
export function useLuta(): typeof LUTA {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return LUTA;
}

/* ------------------------------------------------ campanha: selecao */
/** proximo lugar: o primeiro aberto e sem vitoria (ou o ultimo); o rival sugerido e o primeiro dele */
export function campProximoLugar(m: Motor): number { const Ls = m.lugares, L = Ls.findIndex((_, i) => m.desafioAberto(Ls[i].rivais[0]) && !m.lugarVencido(i)); return L < 0 ? Ls.length - 1 : L; }
export const campProximo = (m: Motor): string => m.lugares[campProximoLugar(m)].rivais[0];
/* o desafio em foco precisa ser da campanha deste pet (pets v5 tem a Montanha Espiral; os antigos, o Piedmon na Cidadela) */
export const campAtual = (m: Motor): string => (LUTA.campSel && LUTA.campSel in m.campanha ? LUTA.campSel : (LUTA.campSel = campProximo(m)));
export const tentativas = (m: Motor, k: string): number => m.log.reduce((n, e) => n + (e[1] === "l" && e[2].r === k ? 1 : 0), 0);

/* ------------------------------------------------ palco em repouso (previa) */
/** o palco sem luta: os dois inteiros, no comeco */
function palcoParado(modo: Modo, A: LutadorTela, B: LutadorTela, cena: IdCenaTR): Palco {
  const E = estadoV2(A.cond, B.cond);
  return { modo, A, B, cena, hud: E.L.map(l => ({ hp: l.hp, hpMax: l.hpMax, guts: l.guts, gutsMax: l.gutsMax })), sim: null, visual: visualNovoTR(), koEm: [null, null],
    segundos: null, morteSubita: false, regra: null, texto: "", callout: "", resultado: null };
}
/** previa do palco (sem luta); manterTexto: so atualiza os lutadores (regras ou forma mudaram) */
export function previa(modo: Modo, manterTexto = false): void {
  if (LUTA.lutando) return;
  const textoAntes = manterTexto && LUTA.palco?.modo === modo ? LUTA.palco.texto : null;
  const m = jogoAtual().motor;
  if (modo === "fronteira") {
    /* a Liga: o pet contra o primeiro lider (so a previa; a luta monta os seis) */
    const L = m.lutadores(RIVAL_LIGA), A = exibirPet(m, L.A), B = exibirLider(0, L.B);
    LUTA.palco = { ...palcoParado(modo, A, B, "coliseu"), arena: null, liga: true, texto: textoAntes ?? "Seis lutas seguidas, sem cura. Aperte Desafiar a Liga." };
    avisarLuta(); return;
  }
  const npc = modo === "campanha" ? campAtual(m) : null, L = npc ? m.lutadores(npc) : null;
  const A = exibirPet(m, L ? L.A : lutadorPet(m, "Seu pet")), B = !npc && LUTA.rivalFixo ? exibirFixo(LUTA.rivalFixo) : exibirBot(npc ?? LUTA.rival, L?.B);
  LUTA.palco = { ...palcoParado(modo, A, B, cenaDaLuta({ npc })), arena: L?.arena ?? null,
    texto: textoAntes ?? (modo === "arena" ? "Escolha um rival e aperte Lutar." : `Seu pet × ${B.nomeTela}: escolha um lugar no mapa e aperte Desafiar.`) };
  avisarLuta();
  /* pets v7: diante do rival que o venceu (e ainda nao foi vencido), ele fala antes da luta */
}
export function escolherRival(k: string): void { if (LUTA.lutando) return; LUTA.rival = k; LUTA.rivalFixo = null; previa("arena"); }
/** o pet B do cenario como lutador de tela */
export function exibirFixo(f: RivalFixo): LutadorTela {
  return { ...exibirPet(f.rival, lutadorPet(f.rival, "Rival do cenário")), nomeTela: nomeForma(f.rival.forma), estiloTela: "pet do cenário" };
}
export function escolherDesafio(k: string): void { if (LUTA.lutando || !(k in jogoAtual().motor.campanha)) return; LUTA.campSel = k; previa("campanha"); }
/** no mapa escolhe o lugar: o rival em foco e o primeiro ainda nao vencido dele */
export function escolherLugar(i: number): void {
  const L = jogoAtual().motor.lugares[i]; if (!L) return;
  escolherDesafio(L.rivais.find(k => !jogoAtual().motor.campanha[k]) || L.rivais[0]);
}

/* ------------------------------------------------ luta animada */
/** npc != null: desafio da campanha; senao o rival escolhido na arena */
export function lutarAnimado(npc: string | null): void {
  if (LUTA.lutando) return;
  const modo: Modo = npc ? "campanha" : "arena", jogo = jogoAtual();
  let m = jogo.motor;
  const Li = npc ? m.lugarDe(npc) : -1, lugarJaVencido = npc ? m.lugarVencido(Li) : true, notasAntes = m.gp ? { ...m.gp.notas } : null;
  const ativasAntes = m.gp ? [...m.gp.ativas] : null, sparringAntes = m.sparring, adolescente = m.estagioAtual === "adolescente";
  let idxLog: number | null = null, ativasDepois: string[] | null = null;
  let r: { res: ResultadoLuta; A: Lutador; B: Lutador; serie: ResultadoLuta[]; arena: Arena | null; venceu?: boolean };
  const cenario = !npc && !!LUTA.rivalFixo, t0 = tamerAtual(), medalhasAntes = t0.n, itensAntes = t0.itens.length, rival = npc || LUTA.rival;
  /* pets v6: a carta escolhida (a luta contra pet de cenario nao entra no registro: sem carta) e se a medalha do lider ja era do
     Tamer (a vitoria entao e revanche, e pode dar a carta dele) */
  const carta = !cenario ? LUTA.carta : null, mdLider = medalhaDoLider(rival), medalhaAntes = !!mdLider && t0.tem(mdLider.id);
  try {
    if (carta && t0.cartas(carta) < 1) throw new Error(`o Tamer não tem mais a ${cartaDe(carta).nome}`);
    if (cenario) {   /* pet de cenario nao e reconstruivel do registro: luta sem ensinar */
      const A0 = lutadorPet(m, "Seu pet"), B0 = lutadorPet(LUTA.rivalFixo!.rival, "Rival do cenário");
      const res0 = jogarLuta(A0, B0, hashSemente("cenario", m.semente, m.log.length), m.regras);
      r = { res: res0, A: A0, B: B0, serie: [res0], arena: null };
    } else {
      mudarMotor(mm => { r = mm.lutar(rival, hashSemente("luta", mm.semente, mm.log.length), carta); idxLog = mm.log.length - 1; ativasDepois = mm.gp ? [...mm.gp.ativas] : null; });
    }
    m = jogoAtual().motor;
  } catch (err) {
    previa(modo);
    if (LUTA.palco) LUTA.palco.texto = err instanceof Error ? err.message : String(err);
    avisarLuta(); return;
  }
  /* a carta saiu do inventario; a revanche vencida pode dar a carta do lider */
  if (!cenario) {
    try {
      mudarTamer(t => {
        if (carta) t.usarCarta(carta, m);
        if (npc) conferirRevanche(t, m, npc, r!.venceu === true, medalhaAntes);
      });
    } catch (err) { console.error("o Tamer não gravou a carta da luta:", err); }
    if (carta) LUTA.carta = null;
  }
  const t = tamerAtual(), medalha = t.n > medalhasAntes ? t.medalhas[t.n - 1] : null, itens = t.itens.slice(itensAntes);
  const { res, serie, arena } = r!, nLutas = arena?.lutas ?? 1, A = exibirPet(m, r!.A), B = cenario ? exibirFixo(LUTA.rivalFixo!) : exibirBot(npc || LUTA.rival, r!.B);
  LUTA.replay = null;
  animar(serie, nLutas, A, B, modo, cenaDaLuta({ npc }), arena, p => {
      const primeiraDoLugar = !lugarJaVencido && res.pontosA === 1;
      const txt = res.pontosA === 1 ? "Seu pet venceu" : res.pontosA === 0 ? "O rival venceu" : "Empate";
      p.texto = (nLutas > 1 ? (res.pontosA === 1 ? `Seu pet venceu as ${nLutas} lutas seguidas. ` : `A série parou na luta ${serie.length} de ${nLutas}. `) : "")
        + `${txt} em ${duracaoLuta(res)} (${res.fim === "ko" ? "nocaute" : !cenario && m.desafiado === 1 ? `${limiteDe(res)}: a luta fica com quem foi desafiado` : `${limiteDe(res)}: vence quem tem mais vida`}).`
        + (primeiraDoLugar && Li < m.lugares.length - 1 ? ` ${m.lugares[Li + 1].nome} liberada!` : "")
        + (primeiraDoLugar && Li === m.lugares.length - 1 ? " Campanha concluída!" : "")
        + (cenario ? " (Contra pet de cenário o seu não aprende.)" : "");
      if (primeiraDoLugar) LUTA.campSel = null;   /* venceu o lugar pela 1a vez: o mapa vai ao proximo */
      p.resultado = { res, npc, notasAntes, cenario, ativasAntes, ativasDepois, lugarJaVencido, sparringAntes, sparringContou: adolescente && !cenario, idxLog, medalha,
        serie, nLutas, arena, carta, itens, lideres: null, titulo: null, instalacao: null, rivais: null, recorde: null };
  });
}
/** a Liga dos Lideres (pets v6; motor/liga.ts): a tentativa inteira entra no registro como uma luta (Motor.lutar com o rival da Liga,
    sem carta) e as 6 lutas sao animadas uma depois da outra, cada uma contra o Mega do lider dela. O titulo (as 6 vencidas) vira o
    evento "campeao" do Tamer (jogo.mudarMotor confere) */
export function lutarLiga(): void {
  if (LUTA.lutando) return;
  const modo: Modo = "fronteira", jogo = jogoAtual(), m0 = jogo.motor, t0 = tamerAtual(), titulosAntes = t0.campeoes.length;
  const notasAntes = m0.gp ? { ...m0.gp.notas } : null, ativasAntes = m0.gp ? [...m0.gp.ativas] : null, sparringAntes = m0.sparring;
  let idxLog: number | null = null, ativasDepois: string[] | null = null;
  let r: ReturnType<Motor["lutar"]>;
  try {
    mudarMotor(mm => { r = mm.lutar(RIVAL_LIGA, hashSemente("luta", mm.semente, mm.log.length)); idxLog = mm.log.length - 1; ativasDepois = mm.gp ? [...mm.gp.ativas] : null; });
  } catch (err) {
    previa(modo);
    if (LUTA.palco) LUTA.palco.texto = err instanceof Error ? err.message : String(err);
    avisarLuta(); return;
  }
  const m = jogoAtual().motor, t = tamerAtual(), titulo = t.campeoes.length > titulosAntes ? t.campeoes[t.campeoes.length - 1] : null;
  const { res, serie } = r!, lideres = r!.lideres!.map((L, i) => exibirLider(i, L)), A = exibirPet(m, r!.A), n = lideres.length;
  LUTA.replay = null;
  animar(serie, n, A, lideres, modo, cenaDaLuta({ npc: null, liga: true }), null, p => {
    const txt = res.pontosA === 1 ? "Seu pet venceu" : res.pontosA === 0 ? `${lideres[serie.length - 1].nomeTela} venceu` : "Empate";
    p.texto = (r!.venceu ? `Seu pet venceu os ${n} líderes seguidos: campeão da Liga. ` : `A Liga parou na luta ${serie.length} de ${n}. `)
      + `${txt} em ${duracaoLuta(res)} (${res.fim === "ko" ? "nocaute" : `${limiteDe(res)}: a luta fica com quem foi desafiado, o líder`}).`;
    p.resultado = { res, npc: null, notasAntes, cenario: false, ativasAntes, ativasDepois, lugarJaVencido: true, sparringAntes, sparringContou: false, idxLog, medalha: null,
      serie, nLutas: n, arena: null, carta: null, itens: [], lideres, titulo, instalacao: null, rivais: null, recorde: null };
  });
}
/** uma tentativa numa instalacao da Fronteira (pets v6; motor/instalacoes.ts): entra no registro como uma luta (Motor.lutar com o id da
    instalacao e a semente da proxima tentativa do pet, que sai do registro; sem carta), e as lutas sao animadas uma depois da outra, cada
    uma contra o Mega sorteado dela, ate a primeira que nao for vitoria. O recorde (a sequencia que passa a do Tamer) vira o evento
    "recorde" do Tamer (jogo.mudarMotor confere) */
export function lutarInstalacao(id: IdInstalacao): void {
  if (LUTA.lutando) return;
  const modo: Modo = "fronteira", inst = instalacaoDe(id), m0 = jogoAtual().motor, recordesAntes = tamerAtual().recordes.length;
  const notasAntes = m0.gp ? { ...m0.gp.notas } : null, ativasAntes = m0.gp ? [...m0.gp.ativas] : null, sparringAntes = m0.sparring;
  let idxLog: number | null = null, ativasDepois: string[] | null = null, s = 0;
  let r: ReturnType<Motor["lutar"]>;
  try {
    mudarMotor(mm => { s = mm.sementeInstalacao(id); r = mm.lutar(id, s); idxLog = mm.log.length - 1; ativasDepois = mm.gp ? [...mm.gp.ativas] : null; });
  } catch (err) {
    previa(modo);
    if (LUTA.palco) LUTA.palco.texto = err instanceof Error ? err.message : String(err);
    avisarLuta(); return;
  }
  const m = jogoAtual().motor, t = tamerAtual(), recorde = t.recordes.slice(recordesAntes).find(x => x.inst === id) ?? null;
  const { res, serie } = r!, rivais = r!.rivais!.map((L, k) => exibirRivalInstalacao(s, k, L)), A = exibirPet(m, r!.A);
  const v = serie.filter(x => x.pontosA === 1).length;
  LUTA.replay = null;
  animar(serie, serie.length, A, rivais, modo, cenaDaLuta({ npc: null, instalacao: inst }), null, p => {
    const txt = res.pontosA === 1 ? "Seu pet venceu" : res.pontosA === 0 ? `${rivais[serie.length - 1].nomeTela} venceu` : "Empate";
    p.texto = `${inst.nome}: ${v} vitória${v === 1 ? "" : "s"} seguida${v === 1 ? "" : "s"}. `
      + `${txt} em ${duracaoLuta(res)} (${res.fim === "ko" ? "nocaute" : `${limiteDe(res)}: a luta fica com quem foi desafiado, o rival`}).`
      + (recorde ? ` Recorde novo do Tamer: ${recorde.valor}.` : "");
    p.resultado = { res, npc: null, notasAntes, cenario: false, ativasAntes, ativasDepois, lugarJaVencido: true, sparringAntes, sparringContou: false, idxLog, medalha: null,
      serie, nLutas: serie.length, arena: null, carta: null, itens: [], lideres: null, titulo: null, instalacao: inst, rivais, recorde };
  }, inst);
}
/** so apresentacao (src/som.ts, desligado por padrao): quem comeca um golpe toca o golpe da forma dele; quem acerta, o acerto; o fim da luta,
    o som de fim de quem venceu. O pesado, o disparo e a investida usam o som de habilidade. Nada disto toca o motor, o registro ou a RNG */
const GOLPES = ["golpe_rapido", "fintar", "disparo", "pesado", "investida"];
const ultimoGolpe = ["golpe_rapido", "golpe_rapido"];
function somDosEventos(ev: readonly EventoTR[], L: LutadorTela[]): void {
  if (!SOM.estado().ligado) return;
  for (const e of ev) {
    if (e.tipo === "acao" && GOLPES.includes(e.nome)) { ultimoGolpe[e.lado] = e.nome; void SOM.tocar("golpe", L[e.lado].sprite, e.nome !== "golpe_rapido"); }
    else if (e.tipo === "dano") { const de = 1 - e.lado; void SOM.tocar("acerto", L[de].sprite, ultimoGolpe[de] !== "golpe_rapido"); }
    else if (e.tipo === "fim" && e.pontosA !== .5) { const v = e.pontosA === 1 ? 0 : 1; void SOM.tocar("fim", L[v].sprite, ultimoGolpe[v] !== "golpe_rapido"); }
  }
}
const hudDe = (S: EstadoTR): HudLado[] => S.L.map(l => ({ hp: l.hp, hpMax: l.hpMax, guts: l.guts, gutsMax: l.gutsMax }));
/** passos da luta por quadro da tela (um quadro a cada QUADRO_MS): o tempo real (3 x 16 ms = 48 ms); x2 o dobro; com o movimento reduzido,
    4x (menos tempo de movimento na tela). PROPOSTO, SEM FONTE */
const QUADRO_MS = 48, PASSOS_QUADRO = 3, PASSOS_RAPIDO = 6, PASSOS_REDUZ = 12;
/** a pausa no fim de cada luta (o nocaute fica na tela) e entre as lutas de uma serie (ms). PROPOSTO, SEM FONTE */
const PAUSA_FIM = 900, PAUSA_SERIE = 1500;
/** a animacao de uma luta ja decidida (ou das lutas seguidas, uma depois da outra, com "luta k de n" no palco): o palco refaz cada luta
    da entrada guardada no resultado (res.tr.entrada), passo a passo, e confere que ela acaba como a do motor (falha alto se nao). Pausa
    e x2 so mudam a velocidade de mostrar; no fim chama fim(palco) e para. nLutas: quantas lutas a serie tem (as jogadas podem ser
    menos: ela para na primeira que nao for vitoria) */
function animar(serie: ResultadoLuta[], nLutas: number, A: LutadorTela, Bs: LutadorTela | LutadorTela[], modo: Modo, cena: IdCenaTR, arena: Arena | null,
  fim: (p: Palco) => void, inst: Instalacao | null = null): void {
  if (!serie.length) throw new Error("série de lutas vazia para animar");
  for (const r of serie) if (!r.tr) throw new Error("luta sem o tempo real: o palco só desenha as lutas dos pets v13");
  LUTA.lutando = true;
  let j = 0, lidos = 0, acabou = false, sim: LutaTR;
  /* a Liga e as instalacoes da Fronteira (varios rivais): cada luta da serie contra o dela. Nas instalacoes o numero de lutas nao aparece
     (a sequencia vai ate a primeira derrota): o palco mostra a vitoria que esta em jogo e a vida com que o pet comecou */
  const liga = Array.isArray(Bs) && !inst, rivalDe = (k: number): LutadorTela => Array.isArray(Bs) ? Bs[k] : Bs;
  const abrir = () => {
    const k = j + 1, en = serie[j].tr!.entrada, B = rivalDe(j);
    sim = criarLutaTR(en.A, en.B, en.semente, { ...en.o, eventos: true }); lidos = 0; acabou = false;
    const base = { modo, A, B, cena, hud: hudDe(sim.S), sim, visual: visualNovoTR(), koEm: [null, null], segundos: 0, morteSubita: false, regra: null, resultado: null, arena };
    if (inst) {
      const L0 = sim.S.L[0], vida = Math.max(0, L0.hp) / L0.hpMax;
      LUTA.palco = { ...base, callout: `LUTA ${k}`, serie: null, liga: false, sequencia: { inst, k, vida },
        texto: `${inst.nome} · vitória ${k}: ${B.nomeTela}` + (j ? `, sem cura: seu pet começa com ${Math.round(vida * 100)}% da vida.` : ".") };
      return;
    }
    LUTA.palco = { ...base, callout: nLutas > 1 ? `LUTA ${k} DE ${nLutas}` : "", serie: nLutas > 1 ? { k, n: nLutas } : null, liga,
      texto: nLutas > 1 ? `Luta ${k} de ${nLutas}` + (j ? ": sem cura, seu pet começa com a vida e o guts que sobraram." : liga ? `: ${B.nomeTela}, o Mega de ${NPC[LIGA[0].lider]!.nome}.` : ": vença as três seguidas.") : "" };
  };
  /** avanca n passos da luta refeita (ou ate o fim dela); devolve se acabou. O fim tem de ser o do motor */
  const avancar = (n: number, comSom: boolean): boolean => {
    const p = LUTA.palco!, res = serie[j].tr!, desafiado = res.entrada.o.desafiado ?? null;
    for (let q = 0; q < n && !acabou; q++) {
      const f = passoTR(sim, desafiado), ev = sim.eventos!.slice(lidos);
      lidos = sim.eventos!.length;
      aplicarEventosTR(p.visual, sim, ev);
      for (const e of ev) {
        if (e.tipo === "acao" && e.lado === 0) p.regra = { motivo: e.motivo, nome: e.nome };
        if (e.tipo === "dano" && e.resta <= 0 && p.koEm[e.lado] === null) p.koEm[e.lado] = sim.S.passo;
      }
      if (comSom) somDosEventos(ev, [A, p.B]);
      if (f) {
        acabou = true;
        if (sim.S.passo !== res.passos || f[0] !== res.pontosA || f[1] !== res.fim) {
          const msg = `a luta refeita no palco não bate com a do motor: passo ${sim.S.passo} × ${res.passos}, pontos ${f[0]} × ${res.pontosA}`;
          p.texto = "Erro: " + msg; LUTA.lutando = false; avisarLuta();
          throw new Error(msg);
        }
        p.callout = f[1] === "ko" ? "NOCAUTE!" : "TEMPO!";
      }
    }
    p.hud = hudDe(sim.S); p.segundos = Math.floor(sim.S.passo * PASSO_TR_MS / 1000); p.morteSubita = sim.S.passo >= CTR_TR.morteSubita;
    return acabou;
  };
  const terminar = (pausa: boolean) => {
    /* a proxima luta da serie: o palco recomeca com a vida que sobrou (uma pausa maior entre elas) */
    if (j < serie.length - 1) {
      const seguir = () => { j++; abrir(); avisarLuta(); agendar(); };
      if (pausa) timer = setTimeout(seguir, PAUSA_SERIE); else seguir();
      return;
    }
    const fechar = () => { fim(LUTA.palco!); LUTA.lutando = false; avisarLuta(); };
    if (pausa) timer = setTimeout(fechar, PAUSA_FIM); else fechar();
  };
  const reduz = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const quadro = () => {
    if (LUTA.pausado) { agendar(); return; }
    const feito = avancar(reduz ? PASSOS_REDUZ : LUTA.rapido ? PASSOS_RAPIDO : PASSOS_QUADRO, true);
    avisarLuta();
    if (feito) terminar(true); else agendar();
  };
  const agendar = () => { timer = setTimeout(quadro, QUADRO_MS); };
  let timer: ReturnType<typeof setTimeout> | undefined;
  /* pular: refaz o resto sem desenhar e vai para o fim da ultima luta jogada */
  pularParaOFim = () => {
    clearTimeout(timer); LUTA.pausado = false;
    if (j < serie.length - 1) { j = serie.length - 1; abrir(); }
    while (!avancar(CTR_TR.limite, false));
    avisarLuta();
    terminar(false);
  };
  LUTA.pausado = false;
  abrir();
  avisarLuta();
  agendar();
}
/** Desistir / Ver o fim: a luta ja foi decidida e gravada quando comecou; isto so pula a animacao ate o resultado */
let pularParaOFim: () => void = () => {};
export function pularAnimacao(): void { if (LUTA.lutando) pularParaOFim(); }
export function alternarPausa(): void { LUTA.pausado = !LUTA.pausado; avisarLuta(); }
export function alternarRapido(): void { LUTA.rapido = !LUTA.rapido; avisarLuta(); }
/** 10 lutas seguidas contra o rival da arena (sem animacao); todas entram no registro */
export function melhorDe10(): string {
  if (LUTA.lutando) return "";
  let v = 0, d = 0, e = 0, lim = 0, trocas = 0;
  if (LUTA.rivalFixo) {
    const m = jogoAtual().motor, B = lutadorPet(LUTA.rivalFixo.rival, "Rival do cenário");
    for (let k = 0; k < 10; k++) {
      const r = jogarLuta(lutadorPet(m, "Seu pet"), B, hashSemente("cenario-m10", m.semente, m.log.length, k), m.regras);
      if (r.pontosA === 1) v++; else if (r.pontosA === 0) d++; else e++;
      lim += r.fim === "limite" ? 1 : 0;
    }
    previa("arena");
    const txt = `10 lutas: ${v} vitórias, ${d} derrotas, ${e} empates (${((v + e / 2) * 10).toFixed(0)}% dos pontos). ${lim} acabaram no limite${m.regras?.tempoReal ? " de tempo" : " de turnos"}. Contra pet de cenário o seu não aprende.`;
    if (LUTA.palco) LUTA.palco.texto = txt;
    avisarLuta();
    return txt;
  }
  mudarMotor(m => {
    const antes = m.gp ? m.gp.mudancas.length : 0;
    for (let k = 0; k < 10; k++) {
      const r = m.lutar(LUTA.rival, hashSemente("luta", m.semente, m.log.length)).res;
      if (r.pontosA === 1) v++; else if (r.pontosA === 0) d++; else e++;
      lim += r.fim === "limite" ? 1 : 0;
    }
    trocas = m.gp ? m.gp.mudancas.length - antes : 0;
  });
  previa("arena");
  const txt = `10 lutas: ${v} vitórias, ${d} derrotas, ${e} empates (${((v + e / 2) * 10).toFixed(0)}% dos pontos). ${lim} acabaram no limite${jogoAtual().motor.regras?.tempoReal ? " de tempo" : " de turnos"}. O pet fez ${trocas} troca${trocas === 1 ? "" : "s"} de regra.`;
  if (LUTA.palco) LUTA.palco.texto = txt;
  avisarLuta();
  return txt;
}
export const sparringTexto = (m: Motor): string | null => m.estagioAtual === "adolescente" ? `${Math.min(m.sparring, CAT.sparring)} de ${CAT.sparring}` : null;

/* ------------------------------------------------ replay de uma luta do registro (Diario) */
/** rever no palco a luta do evento idx: refeita do registro e animada; nada entra no registro nem ensina o pet */
export function reverLuta(idx: number): void {
  if (LUTA.lutando) return;
  const L = reconstruirLuta(jogoAtual().motor, idx);
  LUTA.replay = idx;
  const cena = cenaDaLuta({ npc: L.npc ? L.rival : null, liga: !!L.lideres, instalacao: L.instalacao, salao: L.rival === RIVAL_SALAO });
  animar(L.serie, L.nLutas, L.A, L.lideres ?? L.rivais ?? L.B, L.lideres || L.instalacao || L.rival === RIVAL_SALAO ? "fronteira" : L.npc ? "campanha" : "arena", cena, L.arena, p => {
    const txt = L.res.pontosA === 1 ? `${L.A.nomeTela} venceu` : L.res.pontosA === 0 ? `${L.B.nomeTela} venceu` : "Empate";
    const v = L.serie.filter(x => x.pontosA === 1).length;
    p.texto = `Fim do replay: ${L.instalacao ? `${L.instalacao.nome}, ${v} vitória${v === 1 ? "" : "s"} seguida${v === 1 ? "" : "s"}; ` : L.nLutas > 1 ? `luta ${L.serie.length} de ${L.nLutas}, ` : ""}${txt} em ${duracaoLuta(L.res)}.`;
    p.fimReplay = true;
  }, L.instalacao);
}
/** luta pedida pelo "Ver replay" do Resultado: indice do evento no registro */
export const REPLAY = { pedido: null as number | null };
export interface LutaReconstruida {
  res: ResultadoLuta; A: LutadorTela; B: LutadorTela; rival: string; npc: boolean;
  /** as lutas do evento (mais de uma nas seguidas da Cidadela e na Liga), quantas a serie tem e a arena */
  serie: ResultadoLuta[]; nLutas: number; arena: Arena | null;
  /** a Liga dos Lideres: os 6 lideres na tela (B e o da ultima luta jogada); null fora dela */
  lideres: LutadorTela[] | null;
  /** uma instalacao da Fronteira: qual e os rivais sorteados das lutas jogadas (B e o da ultima); null fora dela */
  instalacao: Instalacao | null; rivais: LutadorTela[] | null;
}
/** refaz a luta do evento idx do registro: o pet reconstruido ate ali (event sourcing), o mesmo rival e a mesma
    semente. So leitura: nada e gravado nem ensinado ao pet vivo. */
export function reconstruirLuta(m: Motor, idx: number): LutaReconstruida {
  const ev = m.log[idx];
  if (!ev || ev[1] !== "l") throw new Error(`o evento ${idx} do registro não é uma luta`);
  const { r, s } = ev[2] as { r: string; s: number };
  const m0 = Motor.reproduzir(m.semente, m.log.slice(0, idx), m.versao), npc = !!NPC[r];
  /* a mesma luta que o motor jogou (Motor.montarLuta: a regra da arena, se houver; a Liga, com os 6 lideres) */
  const L = m0.montarLuta(r, s), res = L.serie[L.serie.length - 1];
  if (L.lideres) {
    const lideres = L.lideres.map((x, i) => exibirLider(i, x));
    return { res, A: exibirPet(m0, L.A), B: lideres[L.serie.length - 1], rival: r, npc, serie: L.serie, nLutas: lideres.length, arena: null, lideres, instalacao: null, rivais: null };
  }
  if (L.instalacao) {
    const rivais = L.rivais!.map((x, k) => exibirRivalInstalacao(s, k, x));
    return { res, A: exibirPet(m0, L.A), B: rivais[rivais.length - 1], rival: r, npc, serie: L.serie, nLutas: L.serie.length, arena: null, lideres: null, instalacao: L.instalacao, rivais };
  }
  /* o Salao: o rival sorteado do estagio do pet na hora da luta */
  if (r === RIVAL_SALAO) return { res, A: exibirPet(m0, L.A), B: exibirRivalSalao(s, m0.estagioAtual, L.B), rival: r, npc, serie: L.serie, nLutas: 1, arena: null, lideres: null, instalacao: null, rivais: null };
  return { res, A: exibirPet(m0, L.A), B: exibirBot(r, L.B), rival: r, npc, serie: L.serie, nLutas: L.arena?.lutas ?? 1, arena: L.arena, lideres: null, instalacao: null, rivais: null };
}

/** uma luta do registro, refeita: rival, turnos, resultado e quantas regras novas o pet tirou dela */
export interface LutaDoRegistro { idx: number; rival: string; turnos: number; pontosA: number; regrasNovas: number }
let cacheLutas: { semente: number; n: number; lutas: LutaDoRegistro[] } | null = null;
/** todas as lutas do registro, refeitas numa passada so (event sourcing, so leitura). O resultado fica guardado ate
    entrar luta nova: o tempo grava eventos a cada poucos segundos e nao muda nenhuma luta. */
export function lutasDoRegistro(m: Motor): LutaDoRegistro[] {
  let n = 0;
  for (const ev of m.log) if (ev[1] === "l") n++;
  if (cacheLutas && cacheLutas.semente === m.semente && cacheLutas.n === n) return cacheLutas.lutas;
  const m0 = new Motor(m.semente, m.versao), lutas: LutaDoRegistro[] = [];
  m.log.forEach((ev, idx) => {
    if (ev[1] !== "l") { m0.aplicarEvento(ev); return; }
    const { r, s } = ev[2] as { r: string; s: number };
    /* a luta como o motor a jogou (nas seguidas da Cidadela, a serie: turnos somados, o resultado da ultima) */
    const serie = m0.montarLuta(r, s).serie, res = serie[serie.length - 1], antes = m0.gp ? [...m0.gp.ativas] : [];
    m0.aplicarEvento(ev);
    lutas.push({ idx, rival: r, turnos: serie.reduce((n, x) => n + tamanhoLuta(x), 0), pontosA: res.pontosA,
      regrasNovas: m0.gp ? m0.gp.ativas.filter(k => !antes.includes(k)).length : 0 });
  });
  cacheLutas = { semente: m.semente, n, lutas };
  return lutas;
}
