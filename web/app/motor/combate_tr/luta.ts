/* A luta 1 contra 1 em tempo real (docs/ESPEC_COMBATE_TR.md; COMBATE-TR, etapa R1), sem tela. A luta e a do DigiLab (o perfilDe, o Guts,
   as acoes, as tecnicas, as passivas, os numeros de hoje); muda o relogio: o turno vira o tempo de acao T_TR, cada acao ocupa o lutador, os
   dois lados agem sem se esperar e a distancia e a posicao num chao reto (a linha do meio da arena). Os dados do Digimon UP nao entram
   (D-1): o resultado nao depende deles.
   - So o epsilon sorteia, numa RNG de politica por lado (derivarSemente("combate_tr", semente, "politica", lado)); o fluxo "combate" fica
     reservado, sem sorteio (espec item 4).
   - So + - x / e Math.min/max (D-7): o mesmo log da a mesma luta em todo motor de JavaScript (test/combate_tr_sem_dom.test.mjs confere).
   - A versao do pet e a chave (R2): so as lutas dos pets v13 (as regras CV21E_TR) passam por aqui, pelo adaptador.ts (jogarLuta). */
import type { CuraLuta, Desafiado, Lutador, RegrasLuta } from "../combate.ts";
import { custoV2 } from "../combate.ts";
import type { Perfil } from "../catalogo.ts";
import { CSO, CV, CV21 } from "../constantes.ts";
import { derivarSemente } from "../mundo.ts";
import { criarRng, type Rng } from "../rng.ts";
import { CTR_TR, T_TR } from "./constantes_tr.ts";
import { decidirTR, faixaTR, intencaoTR, marcaAtivaTR, peleAtivaTR } from "./controlador.ts";

/** a acao em curso: ocupa os passos [inicio, fim); o golpe cai em inicio + instante */
export interface AcaoTR {
  nome: string; motivo: number | string; inicio: number; fim: number;
  /** o indice no registro das acoes da luta (ResultadoLutaTR.acoes) */
  idx: number;
  /** de onde o lutador saiu (a investida aparada volta para ca) */
  x0: number;
  /** o golpe (ou o tiro) ja saiu */
  feito: boolean;
  /** a sentinela recuou com a passiva pronta nesta acao: o avanco do rival fica travado ate o fim dela */
  sentinela: boolean;
}
export interface LadoTR {
  p: Perfil; hp: number; hpMax: number; guts: number; gutsMax: number; regen: number; x: number;
  acao: AcaoTR | null;
  /** o indice da ultima acao comecada (o dano recebido entre duas acoes conta para ela); -1 antes da primeira */
  ultima: number;
  /** o preparo do pesado terminou: a proxima decisao e o pesado ou a finta */
  prep: boolean;
  /** o preparo em curso comecou com a pele dura ativa (so e lido com a V21D, preparoSobPeleOculto) */
  prepPele: boolean;
  atordoadoAte: number; marcaAte: number; peleAte: number; sentinelaPronta: number; disparou: boolean;
  /** as acoes comecadas, na ordem (oponente_repete, oponente_frequente) */
  hist: string[];
  cura: CuraLuta | null;
}
interface ProjetilTR { de: number; x: number; marcado: boolean; emboscada: boolean; causa: number }
export interface EstadoTR { passo: number; L: LadoTR[]; projeteis: ProjetilTR[] }

/** uma acao do registro da luta: quem, o que, por que e o saldo de dano dela ((causado - recebido) / vida maxima do comeco) */
export interface AcaoRegistro { lado: number; nome: string; motivo: number | string; inicio: number; saldo: number }
export type EventoTR =
  | { t: number; tipo: "acao"; lado: number; nome: string; motivo: number | string }
  | { t: number; tipo: "dano"; lado: number; valor: number; resta: number }
  | { t: number; tipo: "erro"; lado: number; nome: string }
  | { t: number; tipo: "interrompe"; lado: number }
  | { t: number; tipo: "cura"; lado: number; valor: number }
  | { t: number; tipo: "fim"; pontosA: number; fim: "ko" | "limite" };
export interface ResultadoLutaTR {
  /** a vida maxima e o Guts do comeco de cada lado */
  E0: { hpMax: number[]; hp: number[]; guts: number[] };
  acoes: AcaoRegistro[]; pontosA: number; fim: "ko" | "limite"; passos: number; E: EstadoTR;
  /** a carta de Cura de cada lado curou nesta luta */
  curou: boolean[];
  /** so com a opcao eventos (a tela e os testes) */
  eventos: EventoTR[] | null;
}
export interface OpcoesTR {
  R?: RegrasLuta;
  /** o lado A comeca com esta vida e este Guts (as lutas seguidas sem cura); null = os dois inteiros */
  ini?: { hp: number; guts: number } | null;
  desafiado?: Desafiado;
  /** a carta de Cura de cada lado ([A, B]) */
  curas?: readonly (CuraLuta | null)[] | null;
  eventos?: boolean;
}

const CORPO_A_CORPO = ["golpe_rapido", "pesado", "investida", "fintar"];
/** a semente de 32 bits da RNG de politica de um lado */
export const sementePoliticaTR = (semente: number, lado: number): number => Number(derivarSemente("combate_tr", semente, "politica", lado) & 0xffffffffn);
const LIMITE_ESQ = CTR_TR.centro - CTR_TR.meiaLargura, LIMITE_DIR = CTR_TR.centro + CTR_TR.meiaLargura;

export function estadoTR(pa: Perfil, pb: Perfil): EstadoTR {
  const L = (p: Perfil, x: number): LadoTR => ({
    p, hp: p.hpMax, hpMax: p.hpMax, guts: p.guts0, gutsMax: p.gutsMax, regen: p.regen, x, acao: null, ultima: -1, prep: false,
    prepPele: false, atordoadoAte: 0, marcaAte: 0, peleAte: 0, sentinelaPronta: 0, disparou: false, hist: [], cura: null,
  });
  return { passo: 0, L: [L(pa, CTR_TR.centro - CTR_TR.entrada), L(pb, CTR_TR.centro + CTR_TR.entrada)], projeteis: [] };
}
const livre = (S: EstadoTR, l: LadoTR): boolean => l.acao === null && S.passo >= l.atordoadoAte;
/** +1: o rival esta a direita (o lado A); -1: a esquerda (o lado B). Os corpos nao se cruzam */
const rumo = (lado: number): number => (lado === 0 ? 1 : -1);

/** o fim da luta: o fimV2 de hoje, com o limite por tempo */
export function fimTR(S: EstadoTR, desafiado: Desafiado = null): [number, "ko" | "limite"] | null {
  const [a, b] = S.L, koA = a.hp <= 0, koB = b.hp <= 0;
  if (koA || koB) return [koA && koB ? .5 : koA ? 0 : 1, "ko"];
  if (S.passo >= CTR_TR.limite) {
    if (desafiado !== null) return [desafiado === 0 ? 1 : 0, "limite"];
    const fa = a.hp / a.hpMax, fb = b.hp / b.hpMax; return [fa === fb ? .5 : fa > fb ? 1 : 0, "limite"];
  }
  return null;
}

/** um dano do passo: quem recebe, quanto (antes da escala e da morte subita) e a acao que o causou (null: nenhuma) */
interface Dano { para: number; valor: number; causa: number | null; cac: boolean }

/** a luta em andamento: o estado, as duas RNG de politica, o registro das acoes e o dos eventos */
export interface LutaTR {
  S: EstadoTR; A: Lutador; B: Lutador; rng: Rng[]; R: RegrasLuta; acoes: AcaoRegistro[]; eventos: EventoTR[] | null; hpMax0: number[];
  curou: boolean[];
}

export function criarLutaTR(A: Lutador, B: Lutador, semente: number, o: OpcoesTR = {}): LutaTR {
  const ea = A.cond.escala, eb = B.cond.escala;
  if ((ea === undefined) !== (eb === undefined)) throw new Error("escala ligada em um lado só");
  const S = estadoTR(A.cond, B.cond);
  if (o.ini) {
    if (!(o.ini.hp > 0 && o.ini.hp <= S.L[0].hpMax) || !(o.ini.guts >= 0)) throw new Error(`começo da luta inválido: vida ${o.ini.hp}, guts ${o.ini.guts}`);
    S.L[0].hp = o.ini.hp; S.L[0].guts = Math.min(o.ini.guts, S.L[0].gutsMax);
  }
  if (o.curas) { S.L[0].cura = o.curas[0] ?? null; S.L[1].cura = o.curas[1] ?? null; }
  return {
    S, A, B, rng: [criarRng(sementePoliticaTR(semente, 0)), criarRng(sementePoliticaTR(semente, 1))], R: o.R ?? null, acoes: [],
    eventos: o.eventos ? [] : null, hpMax0: [S.L[0].hpMax, S.L[1].hpMax], curou: [false, false],
  };
}

function iniciar(Lt: LutaTR, lado: number, nome: string, motivo: number | string): void {
  const S = Lt.S, eu = S.L[lado], t = S.passo;
  if (nome === "pesado" || nome === "fintar") eu.prep = false;
  eu.guts -= custoV2(nome);
  const idx = Lt.acoes.length;
  Lt.acoes.push({ lado, nome, motivo, inicio: t, saldo: 0 });
  eu.acao = { nome, motivo, inicio: t, fim: t + T_TR, idx, x0: eu.x, feito: false, sentinela: false };
  eu.ultima = idx; eu.hist.push(nome);
  if (nome === "pele_dura") eu.peleAte = t + (eu.p.passiva === "colosso_partido" ? CSO.turnosPeleColosso : CV21.turnosPele) * T_TR;
  if (nome === "preparar_pesado") eu.prepPele = peleAtivaTR(S, eu);
  Lt.eventos?.push({ t, tipo: "acao", lado, nome, motivo });
}

/** o golpe `a` do lado atk acerta agora (a resolucao do resolverV2 de hoje, golpe a golpe, contra a postura em curso do alvo).
    Devolve se a investida foi aparada */
function golpe(Lt: LutaTR, atk: number, a: string, danos: Dano[], causa: number, marcado = false, emboscada = false): boolean {
  const S = Lt.S, alvo = 1 - atk, eu = S.L[atk], pa = eu.p, al = S.L[alvo], pal = al.p, r = al.acao?.nome ?? null;
  let bruto = 0;
  if (a === "golpe_rapido" || a === "fintar") bruto = CV.dano.golpe_rapido * pa.mPerto;
  else if (a === "investida") bruto = CV21.danoInvestida * pa.mPerto;
  else if (a === "pesado") { bruto = CV.dano.pesado * pa.mPerto; if (pa.passiva === "tita") bruto *= CV21.multTita; }
  else if (a === "disparo") {
    bruto = CV.dano.disparo * pa.mDisparo;
    if (marcado) bruto *= CV21.multMarca;
    if (emboscada) bruto *= CV21.multEmb;
    if (pa.passiva === "predador") bruto *= CSO.multPred;
  }
  const cac = CORPO_A_CORPO.includes(a);
  if (cac && pa.passiva === "furioso" && eu.hp / eu.hpMax < CV21.limFurioso) bruto *= CV21.multFurioso;
  if (cac && pa.passiva === "devastador") bruto *= CSO.multDev;
  if (!bruto) return false;
  let rec = bruto, dev = 0, parry = false;
  const peleAlvo = peleAtivaTR(S, al), causaAlvo = al.acao?.idx ?? null;
  if (r === "esquivar") {
    if (a === "pesado" || a === "disparo") {
      rec = 0;
      if (a === "pesado" && pa.passiva === "duelista") { rec = CV21.duelista; eu.guts = Math.min(eu.gutsMax, eu.guts + CV.custo.preparar_pesado); }
    }
  } else if (r === "defender" || r === "contra_golpe") {
    /* o disparo marcado ignora a reducao da postura; o contra-golpe ainda devolve */
    if (marcado) { /* sem reducao */ }
    else if (a === "investida") { rec = bruto * CV21.parry; if (r === "defender") parry = true; }
    else if (a === "pesado") rec = bruto * CV.multDefPesado * pal.mGuarda;
    else rec = bruto * CV.multDef * pal.mGuarda;
    if (r === "contra_golpe") {
      if (cac) dev = (pal.passiva === "bastiao_rachado" ? CSO.fracBastiao : CV21.fracCG) * bruto;
      else if (a === "disparo" && pal.passiva === "espelho") dev = CV21.espelho * bruto;
    }
  } else if (r === "carregar") rec = bruto * CV.multCarregar;
  if (peleAlvo) rec *= CV21.multPele;
  if (rec > 0) danos.push({ para: alvo, valor: rec, causa, cac });
  /* o parry da defesa contra o golpe rapido (ou a finta) devolve dano ao atacante */
  if ((a === "golpe_rapido" || a === "fintar") && r === "defender") danos.push({ para: atk, valor: CV.parry, causa: causaAlvo, cac: true });
  if (dev) danos.push({ para: atk, valor: dev * (peleAtivaTR(S, eu) ? CV21.multPele : 1), causa: causaAlvo, cac: true });
  /* o golpe rapido, a investida e a finta interrompem o preparo do pesado (menos sob pele dura) */
  if ((a === "golpe_rapido" || a === "investida" || a === "fintar") && r === "preparar_pesado" && !peleAlvo) {
    al.acao = null; al.prep = false; al.atordoadoAte = S.passo + CTR_TR.atordoaInterrupcao;
    Lt.eventos?.push({ t: S.passo, tipo: "interrompe", lado: alvo });
  }
  return parry;
}

/** um passo de 16 ms: o Guts, as decisoes, o movimento, os golpes, os projeteis, o dano, a cura e o fim das acoes. Devolve o fim da luta
    (ou null) */
export function passoTR(Lt: LutaTR, desafiado: Desafiado = null): [number, "ko" | "limite"] | null {
  const S = Lt.S, t = S.passo, R = Lt.R, est = [Lt.A.estilo, Lt.B.estilo];
  /* o Guts volta a cada passo: regen por T_TR */
  for (const l of S.L) l.guts = Math.min(l.gutsMax, l.guts + l.regen * (l.p.passiva === "colosso_partido" ? CSO.multRegenColosso : 1) / T_TR);
  /* as decisoes: o lado livre decide no passo multiplo do ritmo; o vigia ve a intencao do rival antes de qualquer um decidir */
  if (t % CTR_TR.ritmo === 0) {
    const decide = [0, 1].map(l => livre(S, S.L[l]));
    const ctx = [0, 1].map(l => decide[l] && S.L[l].p.passiva === "vigia" ? { intencao: intencaoTR(est[1 - l], S, 1 - l, R) } : null);
    const dec = [0, 1].map(l => decide[l] ? decidirTR(est[l], S, l, Lt.rng[l], ctx[l], R) : null);
    for (const l of [0, 1]) if (dec[l]) iniciar(Lt, l, dec[l]![0], dec[l]![1]);
  }
  /* a sentinela pronta que recua de quem avanca trava o avanco dele ate o fim do recuo */
  for (const l of [0, 1]) {
    const eu = S.L[l], op = S.L[1 - l];
    if (eu.p.passiva === "sentinela" && eu.acao?.nome === "recuar" && !eu.acao.sentinela && t >= eu.sentinelaPronta
        && (op.acao?.nome === "avancar" || (op.acao?.nome === "investida" && !op.acao.feito))) {
      eu.acao.sentinela = true; eu.sentinelaPronta = t + CV21.recargaSent * T_TR;
    }
  }
  /* o movimento: os dois ao mesmo tempo, depois a cerca e os corpos */
  const travado = [0, 1].map(l => !!S.L[1 - l].acao?.sentinela);
  const dx = [0, 0];
  for (const l of [0, 1]) {
    const eu = S.L[l], a = eu.acao;
    if (!a) continue;
    if (a.nome === "avancar" && !travado[l]) dx[l] = rumo(l) * CTR_TR.andar;
    else if (a.nome === "investida" && !a.feito && !travado[l]) dx[l] = rumo(l) * CTR_TR.arrancada;
    else if (a.nome === "recuar") dx[l] = -rumo(l) * CTR_TR.andar * (a.sentinela ? 1 : CTR_TR.recuo);
  }
  for (const l of [0, 1]) S.L[l].x += dx[l];
  acomodar(S);
  const d = S.L[1].x - S.L[0].x;
  /* o avanco termina ao chegar ao contato */
  for (const l of [0, 1]) { const a = S.L[l].acao; if (a?.nome === "avancar" && d <= CTR_TR.contato) a.fim = t + 1; }
  /* os golpes do passo: os dois lados contra o estado do comeco do passo, o dano junto no fim (como no turno de hoje) */
  const danos: Dano[] = [];
  for (const l of [0, 1]) {
    const eu = S.L[l], a = eu.acao;
    if (!a || a.feito) continue;
    if (a.nome === "investida" && d <= CTR_TR.contato) {
      a.feito = true;
      if (golpe(Lt, l, "investida", danos, a.idx)) eu.x = a.x0;   /* aparada: volta de onde saiu */
    } else if (t === a.inicio + CTR_TR.instante && ["golpe_rapido", "fintar", "pesado", "disparo"].includes(a.nome)) {
      a.feito = true;
      if (a.nome === "disparo") {
        S.projeteis.push({ de: l, x: eu.x, marcado: marcaAtivaTR(S, eu), emboscada: eu.p.passiva === "emboscador" && !eu.disparou, causa: a.idx });
        eu.marcaAte = 0; eu.disparou = true;
      } else if (faixaTR(S) === 0) golpe(Lt, l, a.nome, danos, a.idx);
      else Lt.eventos?.push({ t, tipo: "erro", lado: l, nome: a.nome });
    }
  }
  /* os projeteis em linha reta: acertam ao chegar ao corpo do alvo */
  for (const pr of S.projeteis) {
    const alvo = S.L[1 - pr.de];
    pr.x += rumo(pr.de) * CTR_TR.projetil;
    if (rumo(pr.de) * (alvo.x - pr.x) <= CTR_TR.raio) { golpe(Lt, pr.de, "disparo", danos, pr.causa, pr.marcado, pr.emboscada); pr.de = -1; }
  }
  S.projeteis = S.projeteis.filter(pr => pr.de >= 0);
  aplicarDanos(Lt, danos);
  /* a carta de Cura: na primeira vez abaixo do limiar, uma vez */
  for (const l of [0, 1]) {
    const s = S.L[l], c = s.cura;
    if (!c || s.hp <= 0 || s.hp >= c.abaixo * s.hpMax) continue;
    const ganho = Math.min(s.hpMax - s.hp, c.fracao * s.hpMax);
    s.hp += ganho; s.cura = null; Lt.curou[l] = true;
    Lt.eventos?.push({ t, tipo: "cura", lado: l, valor: ganho });
  }
  /* o fim das acoes: o Guts da defesa e do carregar, a marca, o preparo pronto */
  for (const l of [0, 1]) {
    const eu = S.L[l], a = eu.acao, p = eu.p;
    if (!a || t + 1 < a.fim) continue;
    if (a.nome === "defender" && p.passiva !== "bastiao_rachado") eu.guts = Math.min(eu.gutsMax, eu.guts + CV.gutsDef + (p.passiva === "muralha" ? CV21.muralha : 0));
    if (a.nome === "carregar") eu.guts = Math.min(eu.gutsMax, eu.guts + CV.gutsCarregar);
    if (a.nome === "marcar") eu.marcaAte = t + 1 + CV21.turnosMarca * T_TR;
    if (a.nome === "preparar_pesado") eu.prep = true;
    eu.acao = null;
  }
  /* a marca se perde em perto */
  if (faixaTR(S) === 0) for (const l of S.L) l.marcaAte = 0;
  S.passo = t + 1;
  const fim = fimTR(S, desafiado);
  if (fim) Lt.eventos?.push({ t: S.passo, tipo: "fim", pontosA: fim[0], fim: fim[1] });
  return fim;
}

/** a cerca e os corpos: ninguem sai do chao nem entra no corpo do outro */
function acomodar(S: EstadoTR): void {
  const [a, b] = S.L;
  const falta = CTR_TR.minimo - (b.x - a.x);
  if (falta > 0) { a.x -= falta / 2; b.x += falta / 2; }
  if (a.x < LIMITE_ESQ) { a.x = LIMITE_ESQ; b.x = Math.max(b.x, LIMITE_ESQ + CTR_TR.minimo); }
  if (b.x > LIMITE_DIR) { b.x = LIMITE_DIR; a.x = Math.min(a.x, LIMITE_DIR - CTR_TR.minimo); }
}

/** aplica os danos do passo: a escala da campanha, a morte subita, o saldo das acoes, o empurrao e a marca perdida no corpo a corpo */
function aplicarDanos(Lt: LutaTR, danos: Dano[]): void {
  if (!danos.length) return;
  const S = Lt.S, ea = S.L[0].p.escala, eb = S.L[1].p.escala;
  const ms = S.passo >= CTR_TR.morteSubita ? CV.multMS : 1;
  const total = [0, 0], cac = [false, false];
  for (const x of danos) {
    /* a escala: o dano recebido por i veio do oponente e passa para as unidades de i por E_oponente / E_i */
    const esc = ea !== undefined && eb !== undefined ? (x.para === 0 ? eb / ea : ea / eb) : 1;
    const v = x.valor * esc * ms;
    total[x.para] += v;
    if (x.cac) cac[x.para] = true;
    if (x.causa !== null) Lt.acoes[x.causa].saldo += v / Lt.hpMax0[Lt.acoes[x.causa].lado];
    const atual = S.L[x.para].acao?.idx ?? S.L[x.para].ultima;
    if (atual >= 0) Lt.acoes[atual].saldo -= v / Lt.hpMax0[x.para];
  }
  for (const l of [0, 1]) {
    if (!total[l]) continue;
    const s = S.L[l];
    s.hp -= total[l];
    Lt.eventos?.push({ t: S.passo, tipo: "dano", lado: l, valor: total[l], resta: s.hp });
    if (cac[l]) { s.marcaAte = 0; s.x -= rumo(l) * CTR_TR.empurrao; }
  }
  acomodar(S);
}

/** a luta inteira, do comeco ao fim (o jogarV2 do tempo real) */
export function jogarTR(A: Lutador, B: Lutador, semente: number, o: OpcoesTR = {}): ResultadoLutaTR {
  const Lt = criarLutaTR(A, B, semente, o), S = Lt.S;
  const E0 = { hpMax: [S.L[0].hpMax, S.L[1].hpMax], hp: [S.L[0].hp, S.L[1].hp], guts: [S.L[0].guts, S.L[1].guts] };
  let fim: ReturnType<typeof passoTR> = null;
  while (!(fim = passoTR(Lt, o.desafiado ?? null)));
  return { E0, acoes: Lt.acoes, pontosA: fim[0], fim: fim[1], passos: S.passo, E: S, curou: Lt.curou, eventos: Lt.eventos };
}
