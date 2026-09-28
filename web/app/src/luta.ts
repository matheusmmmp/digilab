/* Luta (Arena e Campanha): um estado so, compartilhado pelas duas abas; o palco aparece na aba visivel e cada
   aba reinicia o palco para o proprio modo quando abre (a mensagem de um modo nao vaza para o outro, revisao
   item 1). A luta entra no registro na hora (motor.lutar); a animacao so mostra os turnos que o motor ja jogou. */
import { useEffect, useState } from "preact/hooks";
import {
  BOTS_V21, BOT_TRACO, CAT, LUGARES, NOME_BOT, NPC, chaveSprite, corDominante, estadoV2, formaRival, hashSemente, jogarV2,
  lutadorBot, lutadorPet, motivoCombate, nomeForma, type Estagio, type EstadoLuta, type FormaAdultaNormal, type Lutador,
  type MotivoCombate, type Motor, type ResultadoLuta, type TracoCombate, type Turno,
} from "../motor/index.ts";
import { gradeDe } from "./grades.ts";
import { jogoAtual, mudarMotor } from "./jogo.ts";

/* bots classicos: Digimon do mapa da Etapa 0 (so rotulo) */
export const DIGIMON_BOT: Record<string, string> = { aleatorio: "Kuramon", agressivo: "Monochromon", tartaruga: "Golemon", atirador: "Tankmon", contragolpe: "Leomon", adaptativo: "Devimon", oraculo: "Jijimon" };
export const RIVAIS_CLASSICOS = ["aleatorio", "agressivo", "tartaruga", "atirador", "contragolpe", "adaptativo", "oraculo"];
export const RIVAIS_ADULTOS: FormaAdultaNormal[] = ["duelista", "furioso", "espelho", "muralha", "sentinela", "emboscador", "vigia", "tita"];

/** o lutador com o que a tela precisa para desenhar (o motor so da estilo e perfil) */
export interface LutadorTela extends Lutador { sprite: string; grade: string; cor: TracoCombate; estagioFala: Estagio; nomeTela: string; estiloTela: string | null }

export function exibirPet(m: Motor, L: Lutador): LutadorTela {
  return { ...L, sprite: chaveSprite(m.forma), grade: gradeDe(m.estagioAtual), cor: corDominante(m.tracos), estagioFala: m.estagioAtual, nomeTela: nomeForma(m.forma), estiloTela: null };
}
export function exibirBot(nome: string, L: Lutador = lutadorBot(nome)): LutadorTela {
  const n = NPC[nome];
  if (n) return { ...L, sprite: n.k, grade: n.grade || "adulto", cor: n.cor, estagioFala: n.estagio || "adulto", nomeTela: n.nome, estiloTela: null };
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
  resultado: { res: ResultadoLuta; npc: string | null; notasAntes: Record<string, number> | null; cenario: boolean } | null; log: LinhaLog[];
}
/** rival fixo: o pet B de um cenario (Diario > Cenarios); luta sem ensinar, porque nao e reconstruivel do registro */
export interface RivalFixo { rival: Motor; dias: number; tipo: string }
export const LUTA = { lutando: false, rival: "agressivo", campSel: null as string | null, palco: null as Palco | null, rivalFixo: null as RivalFixo | null };
const ouvintes = new Set<() => void>();
export const avisarLuta = (): void => { for (const o of ouvintes) o(); };
export function useLuta(): typeof LUTA {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return LUTA;
}

/* ------------------------------------------------ campanha: selecao */
/** proximo lugar: o primeiro aberto e sem vitoria (ou o ultimo); o rival sugerido e o primeiro dele */
export function campProximoLugar(m: Motor): number { const L = LUGARES.findIndex((_, i) => m.desafioAberto(LUGARES[i].rivais[0]) && !m.lugarVencido(i)); return L < 0 ? LUGARES.length - 1 : L; }
export const campProximo = (m: Motor): string => LUGARES[campProximoLugar(m)].rivais[0];
export const campAtual = (m: Motor): string => (LUTA.campSel && NPC[LUTA.campSel] ? LUTA.campSel : (LUTA.campSel = campProximo(m)));
export const tentativas = (m: Motor, k: string): number => m.log.reduce((n, e) => n + (e[1] === "l" && e[2].r === k ? 1 : 0), 0);

/* ------------------------------------------------ palco em repouso (previa) */
/** previa do palco (sem luta); manterTexto: so atualiza os lutadores (regras ou forma mudaram) */
export function previa(modo: Modo, manterTexto = false): void {
  if (LUTA.lutando) return;
  const textoAntes = manterTexto && LUTA.palco?.modo === modo ? LUTA.palco.texto : null;
  const m = jogoAtual().motor, npc = modo === "campanha" ? campAtual(m) : null;
  const A = exibirPet(m, lutadorPet(m, "Seu pet", modo === "campanha")), B = !npc && LUTA.rivalFixo ? exibirFixo(LUTA.rivalFixo) : exibirBot(npc ?? LUTA.rival), E = estadoV2(A.cond, B.cond);
  LUTA.palco = { modo, A, B, E, tr: null, turno: null, callout: "", intencao: null, regra: null, resultado: null, log: [],
    texto: textoAntes ?? (modo === "arena" ? "Escolha um rival e aperte Lutar." : `Seu pet × ${B.nomeTela}: escolha um lugar no mapa e aperte Desafiar.`) };
  avisarLuta();
}
export function escolherRival(k: string): void { if (LUTA.lutando) return; LUTA.rival = k; LUTA.rivalFixo = null; previa("arena"); }
/** o pet B do cenario como lutador de tela */
export function exibirFixo(f: RivalFixo): LutadorTela {
  return { ...exibirPet(f.rival, lutadorPet(f.rival, "Rival do cenário")), nomeTela: nomeForma(f.rival.forma), estiloTela: "pet do cenário" };
}
export function escolherDesafio(k: string): void { if (LUTA.lutando || !NPC[k]) return; LUTA.campSel = k; previa("campanha"); }
/** no mapa escolhe o lugar: o rival em foco e o primeiro ainda nao vencido dele */
export function escolherLugar(i: number): void {
  const L = LUGARES[i]; if (!L) return;
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
  const lugarJaVencido = npc ? m.lugarVencido(NPC[npc]!.lug) : true, notasAntes = m.gp ? { ...m.gp.notas } : null;
  let r: { res: ResultadoLuta; A: Lutador; B: Lutador };
  const cenario = !npc && !!LUTA.rivalFixo;
  try {
    if (cenario) {   /* pet de cenario nao e reconstruivel do registro: luta sem ensinar */
      const A0 = lutadorPet(m, "Seu pet"), B0 = lutadorPet(LUTA.rivalFixo!.rival, "Rival do cenário");
      r = { res: jogarV2(A0, B0, hashSemente("cenario", m.semente, m.log.length)), A: A0, B: B0 };
    } else {
      const rival = npc || LUTA.rival;
      mudarMotor(mm => { r = mm.lutar(rival, hashSemente("luta", mm.semente, mm.log.length)); });
    }
    m = jogoAtual().motor;
  } catch (err) {
    previa(modo);
    if (LUTA.palco) LUTA.palco.texto = err instanceof Error ? err.message : String(err);
    avisarLuta(); return;
  }
  const { res } = r!, A = exibirPet(m, r!.A), B = cenario ? exibirFixo(LUTA.rivalFixo!) : exibirBot(npc || LUTA.rival, r!.B);
  LUTA.lutando = true;
  LUTA.palco = { modo, A, B, E: res.E0, tr: null, turno: null, texto: "", callout: "", intencao: null, regra: null, resultado: null, log: [] };
  avisarLuta();
  const reduz = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let i = 0;
  const passo = () => {
    const p = LUTA.palco!;
    if (i >= res.turnos.length) {
      const primeiraDoLugar = !lugarJaVencido && res.pontosA === 1;
      const txt = res.pontosA === 1 ? "Seu pet venceu" : res.pontosA === 0 ? "O rival venceu" : "Empate";
      p.texto = `${txt} em ${res.turnos.length} turnos (${res.fim === "ko" ? "nocaute" : "limite de turnos: vence quem tem mais vida"}).`
        + (primeiraDoLugar && NPC[npc!]!.lug < LUGARES.length - 1 ? ` ${LUGARES[NPC[npc!]!.lug + 1].nome} liberada!` : "")
        + (primeiraDoLugar && NPC[npc!]!.lug === LUGARES.length - 1 ? " Campanha concluída!" : "")
        + (cenario ? " (Contra pet de cenário o seu não aprende.)" : "");
      if (primeiraDoLugar) LUTA.campSel = null;   /* venceu o lugar pela 1a vez: o mapa vai ao proximo */
      p.resultado = { res, npc, notasAntes, cenario };
      LUTA.lutando = false; avisarLuta(); return;
    }
    const tr = res.turnos[i++];
    const ma = motivoCombate(tr, 0, A.estilo), mb = motivoCombate(tr, 1, B.estilo);
    const dano = tr.dano[1] ? `seu pet causa ${dec1(tr.dano[1])}` : "", dano2 = tr.dano[0] ? `o rival causa ${dec1(tr.dano[0])}` : "";
    const extra = [tr.interr[0] && "seu pesado foi interrompido", tr.interr[1] && "o pesado do rival foi interrompido",
      tr.errou[0] && "seu pesado errou", tr.errou[1] && "o pesado do rival errou"].filter(Boolean) as string[];
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
    setTimeout(passo, reduz ? 80 : 650);
  };
  passo();
}
/** 10 lutas seguidas contra o rival da arena (sem animacao); todas entram no registro */
export function melhorDe10(): string {
  if (LUTA.lutando) return "";
  let v = 0, d = 0, e = 0, lim = 0, trocas = 0;
  if (LUTA.rivalFixo) {
    const m = jogoAtual().motor, B = lutadorPet(LUTA.rivalFixo.rival, "Rival do cenário");
    for (let k = 0; k < 10; k++) {
      const r = jogarV2(lutadorPet(m, "Seu pet"), B, hashSemente("cenario-m10", m.semente, m.log.length, k));
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
