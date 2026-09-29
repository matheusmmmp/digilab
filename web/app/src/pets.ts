/* Varios pets, um ativo (pedido do Matheus, 2026-09-28). O pet ATIVO continua no save de sempre (CHAVE, mesmo
   formato): so ele tem o tempo correndo. Os outros ficam guardados em CHAVE-guardados, cada um so com o registro
   {semente, log, versao}: um pet guardado nao recebe evento, entao o relogio dele fica parado onde estava e, ao ser
   ativado, continua dali (Motor.reproduzir). Trocar = guardar o ativo e reproduzir o escolhido.

   Primeiro acesso a esta versao: os guardados comecam com uma escada de exemplo, do mais fraco ao mais forte
   (In-Training ate Ultimate/Mega treinado), gerada com os donos simulados dos Cenarios e sessoes de treino dentro das
   regras (intervalo, fadiga, tudo no registro de cada pet). */
import { CAT, CD, CTR, Motor, TPD, criarDono, criarRng, hashSemente, type EventoRegistro, type Exercicio, type TipoDono, type VisaoDono } from "../motor/index.ts";
import { jogoAtual, trocarMotor } from "./jogo.ts";
import { LUTA, previa } from "./luta.ts";
import { CHAVE, textoSave } from "./save.ts";

export const CHAVE_GUARDADOS = CHAVE + "-guardados";
export interface Guardado { semente: number; log: EventoRegistro[]; versao: number }

export function lerGuardados(): Guardado[] {
  let bruto: string | null = null;
  try { bruto = localStorage.getItem(CHAVE_GUARDADOS); } catch { return []; }
  if (!bruto) return [];
  const d = JSON.parse(bruto);
  if (!Array.isArray(d)) throw new Error("pets guardados: formato inválido");
  return d as Guardado[];
}
function gravarGuardados(g: Guardado[]): void {
  localStorage.setItem(CHAVE_GUARDADOS, JSON.stringify(g));
}
/** reproduz um pet guardado (so para mostrar; nao muda nada) */
export const abrirGuardado = (g: Guardado): Motor => Motor.reproduzir(g.semente, g.log, g.versao ?? 1);

/** ativa o guardado i: o ativo vai para o lugar dele, o escolhido passa a correr o tempo */
export function ativarGuardado(i: number): void {
  const g = lerGuardados(), escolhido = g[i];
  if (!escolhido) throw new Error("pet guardado não existe: " + i);
  const m = abrirGuardado(escolhido);
  g[i] = JSON.parse(textoSave(jogoAtual().motor)) as Guardado;
  gravarGuardados(g);
  trocarMotor(m, "save");
  LUTA.rivalFixo = null;
  previa("arena");
}

/** apaga o guardado i (a tela confirma antes); o ativo nunca e apagado por aqui */
export function apagarGuardado(i: number): void {
  const g = lerGuardados();
  if (!g[i]) throw new Error("pet guardado não existe: " + i);
  g.splice(i, 1);
  gravarGuardados(g);
}

/** heranca (pets v4): cruza o ativo com o guardado i (os dois adultos e vivos). O filho vira o ativo e choca;
    o pai ativo vai para os guardados (nada se perde). */
export function cruzarComAtivo(i: number): void {
  const g = lerGuardados(), par = g[i];
  if (!par) throw new Error("pet guardado não existe: " + i);
  const ativo = jogoAtual().motor, s = (Date.now() ^ Math.floor(Math.random() * 1e9)) >>> 0;
  const filho = Motor.cruzar(ativo, abrirGuardado(par), s, hashSemente("heranca", s), "dono");
  g.push(JSON.parse(textoSave(ativo)) as Guardado);
  gravarGuardados(g);
  trocarMotor(filho, "novo", 16);
  LUTA.rivalFixo = null;
  previa("arena");
}

/* ------------------------------------------------ escada de exemplo (fraco -> forte) */
interface Receita { dono: TipoDono; dias: number; porDia: number; treinoDia: number; semente: number }
/** do mais fraco ao mais forte: In-Training, Rookie sem e com treino, Champion treinado, adultos sem e com treino */
export const ESCADA: readonly Receita[] = [
  { dono: "atencioso", dias: .1, porDia: 16, treinoDia: 0, semente: 910101 },
  { dono: "relapso", dias: .45, porDia: 8, treinoDia: 0, semente: 910202 },
  { dono: "atencioso", dias: .55, porDia: 16, treinoDia: 10, semente: 910303 },
  { dono: "atencioso", dias: 1.2, porDia: 16, treinoDia: 10, semente: 910404 },
  { dono: "aleatorio", dias: 2.2, porDia: 16, treinoDia: 0, semente: 910505 },
  { dono: "atencioso", dias: 3, porDia: 18, treinoDia: 12, semente: 910606 },
];
const EXERCICIOS: readonly Exercicio[] = ["levantar_pedra", "corrida", "alvo", "esquiva", "meditar", "resistencia"];

/** o pet de uma receita: dono simulado (mesmo laco dos Cenarios) + treino em rodizio quando o motor deixa */
export function petDaReceita(r: Receita): Motor {
  /* v3 de proposito: exemplos estaveis (na v4 o dono simulado nao trata lesao nem responde as janelas) */
  const m = new Motor(r.semente, 3), dono = criarDono(r.dono), rng = criarRng(hashSemente("dono", r.semente, r.dono));
  const passos = Math.round(r.dias * TPD / CD.passo), orc = Math.round(r.porDia * r.dias);
  let gasto = 0, sessoes = 0, ex = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    for (const a of dono.decidir(v, rng)) { m.observar(a); gasto++; }
    if (m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) m.lutar("aleatorio", hashSemente("sparring", r.semente, p));
    /* treino: sem forcar (para abaixo do limite), respeitando o intervalo e a meta do dia */
    const dia = Math.floor(m.e.tick / TPD);
    if (r.treinoDia > 0 && m.estagioAtual !== "bebe" && m.treino.podeTocar(m.e.tick) && m.treino.fadiga + CTR.fadigaSessao < CTR.limiarPausa
        && sessoes < r.treinoDia * (dia + 1)) {
      try { m.treinar(EXERCICIOS[ex++ % EXERCICIOS.length]); sessoes++; } catch { /* o motor recusou (ex.: dormindo): tenta no proximo passo */ }
    }
  }
  return m;
}
/** primeiro acesso a esta versao: cria a escada de exemplo, se ainda nao houver guardados */
export function semearGuardados(): boolean {
  try { if (localStorage.getItem(CHAVE_GUARDADOS) !== null) return false; } catch { return false; }
  gravarGuardados(ESCADA.map(r => JSON.parse(textoSave(petDaReceita(r))) as Guardado));
  return true;
}
