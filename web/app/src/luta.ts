/* Luta (Arena e Campanha): um estado so, compartilhado pelas duas abas; o palco aparece na aba visivel e cada
   aba reinicia o palco para o proprio modo quando abre (a mensagem de um modo nao vaza para o outro, revisao
   item 1). A luta entra no registro na hora (motor.lutar); a animacao so mostra os turnos que o motor ja jogou. */
import { useEffect, useState } from "preact/hooks";
import {
  BOTS_V21, BOT_TRACO, CAT, NOME_BOT, NPC, cartaDe, chaveSprite, corDominante, estadoV2, formaRival, hashSemente, jogarV2,
  lutadorBot, lutadorPet, medalhaDoLider, motivoCombate, nomeForma, type Arena, type Estagio, type EstadoLuta, type FormaAdultaNormal, type Lutador,
  Motor, type MotivoCombate, type ResultadoLuta, type TracoCombate, type Turno,
} from "../motor/index.ts";
import { gradeDe } from "./grades.ts";
import { jogoAtual, mudarMotor, mudarTamer, tamerAtual } from "./jogo.ts";
import { conferirRevanche, type ItemGanho, type MedalhaGanha } from "./tamer.ts";

/* bots classicos: Digimon do mapa da Etapa 0 (so rotulo) */
export const DIGIMON_BOT: Record<string, string> = { aleatorio: "Kuramon", agressivo: "Monochromon", tartaruga: "Golemon", atirador: "Tankmon", contragolpe: "Leomon", adaptativo: "Devimon", oraculo: "Jijimon" };
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

export type Modo = "arena" | "campanha";
/** uma linha do registro da luta: o motivo de cada lado; o texto sai da tabela de expressao na hora de desenhar */
export interface LinhaLog { t: number; pet: string; rival: string; ma: MotivoCombate; mb: MotivoCombate; estPet: Estagio; estRival: Estagio; humor: number }
export interface Palco {
  modo: Modo; A: LutadorTela; B: LutadorTela; E: EstadoLuta; tr: Turno | null; turno: number | null;
  texto: string; callout: string; intencao: string | null; regra: { ma: MotivoCombate; A: LutadorTela } | null;
  resultado: ResultadoPalco | null; log: LinhaLog[];
  /** replay animado de uma luta do registro chegou ao fim */
  fimReplay?: boolean;
  /** lutas seguidas da arena (Cidadela): a luta que esta no palco (1 = a primeira) e quantas sao; null numa luta so */
  serie?: { k: number; n: number } | null;
  /** a arena da luta (pets v6 contra o lider; motor/arenas.ts); null fora dela */
  arena?: Arena | null;
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
}
export interface RivalFixo { rival: Motor; dias: number; tipo: string }
export const LUTA = { lutando: false, rival: "agressivo", campSel: null as string | null, palco: null as Palco | null, rivalFixo: null as RivalFixo | null,
  /** pets v6: a carta do Tamer escolhida para a proxima luta (Campanha ou Arena); sai quando a luta a usa */
  carta: null as string | null,
  /* tela cheia da luta (#/lutar/luta): pausa e x2 so mudam a animacao; a luta ja esta decidida e no registro */
  pausado: false, rapido: false,
  /** indice no registro da luta que esta sendo revista (replay animado, nada gravado); null numa luta de verdade */
  replay: null as number | null };
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
/** previa do palco (sem luta); manterTexto: so atualiza os lutadores (regras ou forma mudaram) */
export function previa(modo: Modo, manterTexto = false): void {
  if (LUTA.lutando) return;
  const textoAntes = manterTexto && LUTA.palco?.modo === modo ? LUTA.palco.texto : null;
  const m = jogoAtual().motor, npc = modo === "campanha" ? campAtual(m) : null, L = npc ? m.lutadores(npc) : null;
  const A = exibirPet(m, L ? L.A : lutadorPet(m, "Seu pet")), B = !npc && LUTA.rivalFixo ? exibirFixo(LUTA.rivalFixo) : exibirBot(npc ?? LUTA.rival, L?.B), E = estadoV2(A.cond, B.cond);
  LUTA.palco = { modo, A, B, E, tr: null, turno: null, callout: "", intencao: null, regra: null, resultado: null, log: [], arena: L?.arena ?? null,
    texto: textoAntes ?? (modo === "arena" ? "Escolha um rival e aperte Lutar." : `Seu pet × ${B.nomeTela}: escolha um lugar no mapa e aperte Desafiar.`) };
  avisarLuta();
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
const DIST_TXT = (tr: Turno): string => (tr.a === "fintar" || tr.b === "fintar") ? "FINTA!" : (tr.interr[0] || tr.interr[1]) ? "INTERROMPEU!" : (tr.errou[0] || tr.errou[1]) ? "ERROU!" : "";
const dec1 = (v: number): string => v.toFixed(1).replace(".", ",");

/** npc != null: desafio da campanha; senao o rival escolhido na arena */
export function lutarAnimado(npc: string | null, nomeAcaoV2: Record<string, string>): void {
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
  const carta = !cenario && m.versao >= 6 ? LUTA.carta : null, mdLider = medalhaDoLider(rival), medalhaAntes = !!mdLider && t0.tem(mdLider.id);
  try {
    if (carta && t0.cartas(carta) < 1) throw new Error(`o Tamer não tem mais a ${cartaDe(carta).nome}`);
    if (cenario) {   /* pet de cenario nao e reconstruivel do registro: luta sem ensinar */
      const A0 = lutadorPet(m, "Seu pet"), B0 = lutadorPet(LUTA.rivalFixo!.rival, "Rival do cenário");
      const res0 = jogarV2(A0, B0, hashSemente("cenario", m.semente, m.log.length), m.regras);
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
  if (!cenario && m.versao >= 6) {
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
  animar(serie, nLutas, A, B, modo, nomeAcaoV2, arena, p => {
      const primeiraDoLugar = !lugarJaVencido && res.pontosA === 1;
      const txt = res.pontosA === 1 ? "Seu pet venceu" : res.pontosA === 0 ? "O rival venceu" : "Empate";
      p.texto = (nLutas > 1 ? (res.pontosA === 1 ? `Seu pet venceu as ${nLutas} lutas seguidas. ` : `A série parou na luta ${serie.length} de ${nLutas}. `) : "")
        + `${txt} em ${res.turnos.length} turnos (${res.fim === "ko" ? "nocaute" : !cenario && m.desafiado === 1 ? "limite de turnos: a luta fica com quem foi desafiado" : "limite de turnos: vence quem tem mais vida"}).`
        + (primeiraDoLugar && Li < m.lugares.length - 1 ? ` ${m.lugares[Li + 1].nome} liberada!` : "")
        + (primeiraDoLugar && Li === m.lugares.length - 1 ? " Campanha concluída!" : "")
        + (cenario ? " (Contra pet de cenário o seu não aprende.)" : "");
      if (primeiraDoLugar) LUTA.campSel = null;   /* venceu o lugar pela 1a vez: o mapa vai ao proximo */
      p.resultado = { res, npc, notasAntes, cenario, ativasAntes, ativasDepois, lugarJaVencido, sparringAntes, sparringContou: adolescente && !cenario, idxLog, medalha,
        serie, nLutas, arena, carta, itens };
  });
}
/** a animacao de uma luta ja decidida (ou das lutas seguidas da Cidadela, uma depois da outra, com "luta k de n" no palco):
    um turno por vez (pausa e x2); no fim chama fim(palco) e para. nLutas: quantas lutas a serie tem (as jogadas podem ser
    menos: ela para na primeira que nao for vitoria) */
function animar(serie: ResultadoLuta[], nLutas: number, A: LutadorTela, B: LutadorTela, modo: Modo, nomeAcaoV2: Record<string, string>, arena: Arena | null,
  fim: (p: Palco) => void): void {
  if (!serie.length) throw new Error("luta sem turnos para animar");
  LUTA.lutando = true;
  let j = 0, i = 0;
  const abrir = () => {
    const k = j + 1, log = j && LUTA.palco ? LUTA.palco.log : [];
    LUTA.palco = { modo, A, B, E: serie[j].E0, tr: null, turno: null, callout: nLutas > 1 ? `LUTA ${k} DE ${nLutas}` : "", intencao: null, regra: null, resultado: null, log,
      texto: nLutas > 1 ? `Luta ${k} de ${nLutas}` + (j ? ": sem cura, seu pet começa com a vida e o guts que sobraram." : ": vença as três seguidas.") : "",
      serie: nLutas > 1 ? { k, n: nLutas } : null, arena };
  };
  abrir();
  avisarLuta();
  const reduz = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const passo = () => {
    const p = LUTA.palco!, res = serie[j];
    if (i >= res.turnos.length) {
      /* a proxima luta da serie: o palco recomeca com a vida que sobrou (uma pausa maior entre elas) */
      if (j < serie.length - 1) { j++; i = 0; abrir(); avisarLuta(); agendar(3); return; }
      fim(p); LUTA.lutando = false; avisarLuta(); return;
    }
    const tr = res.turnos[i++];
    const ma = motivoCombate(tr, 0, A.estilo), mb = motivoCombate(tr, 1, B.estilo);
    const dano = tr.dano[1] ? `seu pet causa ${dec1(tr.dano[1])}` : "", dano2 = tr.dano[0] ? `o rival causa ${dec1(tr.dano[0])}` : "";
    const extra = [tr.interr[0] && "seu pesado foi interrompido", tr.interr[1] && "o pesado do rival foi interrompido",
      tr.errou[0] && "seu pesado errou", tr.errou[1] && "o pesado do rival errou", tr.cura?.[0] && "a Carta de Cura curou seu pet"].filter(Boolean) as string[];
    const partes = [dano, dano2, ...extra].filter(Boolean);
    Object.assign(p, {
      E: tr.depois, tr, turno: tr.t, callout: DIST_TXT(tr),
      /* intencao telegrafada: so o que o motor mostra (o rival preparando o pesado) */
      intencao: tr.depois.L[1].prep ? `${B.nomeTela} prepara um golpe pesado. Chega no próximo turno.` : null,
      regra: { ma, A },
      texto: `Turno ${tr.t}: ${nomeAcaoV2[tr.a]} × ${nomeAcaoV2[tr.b]}` + (partes.length ? " · " + partes.join(", ") : " · ninguém se machuca"),
      log: [{ t: tr.t, pet: A.nomeTela, rival: B.nomeTela, ma, mb, estPet: A.estagioFala, estRival: B.estagioFala, humor: jogoAtual().motor.e.humor }, ...p.log].slice(0, 8),
    });
    avisarLuta();
    agendar();
  };
  /* proximo turno: parado enquanto pausado; x2 corta a espera pela metade */
  const agendar = (vezes = 1) => { timer = setTimeout(() => { if (LUTA.pausado) agendar(); else passo(); }, LUTA.pausado ? 150 : (reduz ? 80 : LUTA.rapido ? 325 : 650) * vezes); };
  let timer: ReturnType<typeof setTimeout> | undefined;
  /* pular: vai para o fim da ultima luta jogada, com o palco no estado final dela */
  pularParaOFim = () => {
    clearTimeout(timer); LUTA.pausado = false;
    if (j < serie.length - 1) { j = serie.length - 1; abrir(); }
    const res = serie[j], ult = res.turnos[res.turnos.length - 1];
    i = res.turnos.length;
    if (LUTA.palco && ult) Object.assign(LUTA.palco, { E: res.E, tr: ult, turno: ult.t });
    passo();
  };
  LUTA.pausado = false;
  passo();
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
      const r = jogarV2(lutadorPet(m, "Seu pet"), B, hashSemente("cenario-m10", m.semente, m.log.length, k), m.regras);
      if (r.pontosA === 1) v++; else if (r.pontosA === 0) d++; else e++;
      lim += r.fim === "limite" ? 1 : 0;
    }
    previa("arena");
    const txt = `10 lutas: ${v} vitórias, ${d} derrotas, ${e} empates (${((v + e / 2) * 10).toFixed(0)}% dos pontos). ${lim} acabaram no limite de turnos. Contra pet de cenário o seu não aprende.`;
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
  const txt = `10 lutas: ${v} vitórias, ${d} derrotas, ${e} empates (${((v + e / 2) * 10).toFixed(0)}% dos pontos). ${lim} acabaram no limite de turnos. O pet fez ${trocas} troca${trocas === 1 ? "" : "s"} de regra.`;
  if (LUTA.palco) LUTA.palco.texto = txt;
  avisarLuta();
  return txt;
}
export const sparringTexto = (m: Motor): string | null => m.estagioAtual === "adolescente" ? `${Math.min(m.sparring, CAT.sparring)} de ${CAT.sparring}` : null;

/* ------------------------------------------------ replay de uma luta do registro (Diario) */
/** rever no palco a luta do evento idx: refeita do registro e animada; nada entra no registro nem ensina o pet */
export function reverLuta(idx: number, nomeAcaoV2: Record<string, string>): void {
  if (LUTA.lutando) return;
  const L = reconstruirLuta(jogoAtual().motor, idx);
  LUTA.replay = idx;
  animar(L.serie, L.nLutas, L.A, L.B, L.npc ? "campanha" : "arena", nomeAcaoV2, L.arena, p => {
    const txt = L.res.pontosA === 1 ? `${L.A.nomeTela} venceu` : L.res.pontosA === 0 ? `${L.B.nomeTela} venceu` : "Empate";
    p.texto = `Fim do replay: ${L.nLutas > 1 ? `luta ${L.serie.length} de ${L.nLutas}, ` : ""}${txt} em ${L.res.turnos.length} turnos.`;
    p.fimReplay = true;
  });
}
/** luta pedida pelo "Ver replay" do Resultado: indice do evento no registro */
export const REPLAY = { pedido: null as number | null };
export interface LutaReconstruida {
  res: ResultadoLuta; A: LutadorTela; B: LutadorTela; rival: string; npc: boolean;
  /** as lutas do evento (mais de uma so nas seguidas da Cidadela), quantas a serie tem e a arena */
  serie: ResultadoLuta[]; nLutas: number; arena: Arena | null;
}
/** refaz a luta do evento idx do registro: o pet reconstruido ate ali (event sourcing), o mesmo rival e a mesma
    semente. So leitura: nada e gravado nem ensinado ao pet vivo. */
export function reconstruirLuta(m: Motor, idx: number): LutaReconstruida {
  const ev = m.log[idx];
  if (!ev || ev[1] !== "l") throw new Error(`o evento ${idx} do registro não é uma luta`);
  const { r, s } = ev[2] as { r: string; s: number };
  const m0 = Motor.reproduzir(m.semente, m.log.slice(0, idx), m.versao), npc = !!NPC[r];
  /* a mesma luta que o motor jogou (Motor.montarLuta: a regra da arena, se houver) */
  const L = m0.montarLuta(r, s), res = L.serie[L.serie.length - 1];
  return { res, A: exibirPet(m0, L.A), B: exibirBot(r, L.B), rival: r, npc, serie: L.serie, nLutas: L.arena?.lutas ?? 1, arena: L.arena };
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
    lutas.push({ idx, rival: r, turnos: serie.reduce((n, x) => n + x.turnos.length, 0), pontosA: res.pontosA,
      regrasNovas: m0.gp ? m0.gp.ativas.filter(k => !antes.includes(k)).length : 0 });
  });
  cacheLutas = { semente: m.semente, n, lutas };
  return lutas;
}
