/* A historia do pet (espelho de digilab/historia.py; DESIGN_VOZ_PROPRIA, secao 2). Funcao pura do registro: o mesmo
   RegistroVida da os mesmos fatos, na mesma ordem. Cada fato sai de um molde fixo por regra. Os textos e a ordem sao
   conferidos contra o Python (test/historia.test.ts, gabarito exportado por experiments/exportar_gabaritos_voz.py).
   H habito meu, O habito do dono, P gosto, L marco. */
import { TPD } from "./constantes.ts";

export interface ConfigHistoria {
  janelaSeq: number; probSeq: number; minSeq: number; lift: number; fatorPeriodo: number; minPeriodo: number;
  fracaoPeriodoDono: number; diasPeriodoDono: number; fracaoCuidado: number; fracaoCedeManha: number; minManhas: number;
  demoraRapida: number; demoraLenta: number; minChamados: number; limiarGosto: number; fracaoTreino: number; minSessoes: number;
  ausencia: number; maxFatos: number; maxPorRegra: number; falasRecentes: number;
}
/* espelho de ConfigHistoria (PROPOSTOS; constantes.test.mjs confere) */
export const CHIS: ConfigHistoria = {
  janelaSeq: 30, probSeq: .6, minSeq: 10, lift: 1.5, fatorPeriodo: 2, minPeriodo: 10, fracaoPeriodoDono: .4, diasPeriodoDono: 3,
  fracaoCuidado: .35, fracaoCedeManha: .6, minManhas: 5, demoraRapida: 5, demoraLenta: 12, minChamados: 5, limiarGosto: .02,
  fracaoTreino: .35, minSessoes: 6, ausencia: 360, maxFatos: 12, maxPorRegra: 2, falasRecentes: 5,
};

export const PERIODOS = [["madrugada", 0, 6], ["manha", 6, 12], ["tarde", 12, 18], ["noite", 18, 24]] as const;
export type Periodo = typeof PERIODOS[number][0];
export const TEXTO_PERIODO: Record<Periodo, string> = { madrugada: "de madrugada", manha: "de manhã", tarde: "à tarde", noite: "à noite" };
export const PET_EU: Record<string, string> = { dormir: "durmo", comer: "como", brincar: "brinco", chamar_atencao: "chamo você",
  explorar: "exploro", emburrar: "emburro" };
export const PET_INF: Record<string, string> = { dormir: "dormir", comer: "comer", brincar: "brincar", chamar_atencao: "chamar você",
  explorar: "explorar", emburrar: "emburrar" };
export const CUIDADO_DONO: Record<string, string> = { alimentar: "me dar comida", limpar: "me limpar", brincar: "brincar comigo",
  acariciar: "me dar carinho", petisco: "me dar petisco" };
export const NIVEL: Record<string, string> = { bebe: "In-Training", crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };   /* mega: so no jogo (pets v5+) */
export type TipoFato = "H" | "O" | "P" | "L";
const ORDEM_TIPOS: TipoFato[] = ["L", "H", "P", "O"];
const MAX_TEXTO = 80;

export interface FatoHistoria { tipo: TipoFato; regra: string; chave: string; texto: string; tick: number; dados: Record<string, unknown> }
export interface JanelaFechada { tipo: string; falso: boolean; desfecho: string; inicio: number; fim: number }
export interface LutaRegistro { tick: number; rival: string; resultado: string; lesao?: boolean }
export interface RegistroVida {
  tickFinal: number;
  acoesDono: [number, string][];
  acoesPet: [number, string][];
  janelas: JanelaFechada[];
  sessoesTreino: [number, string][];
  lutas: LutaRegistro[];
  evolucoes: [number, string][];
  sombriaTick: number | null;
  filhoDeCruzamento: boolean;
  desvioPorAcao: [string, number][];
}

function fato(tipo: TipoFato, regra: string, chave: string, texto: string, tick: number, dados: Record<string, unknown> = {}): FatoHistoria {
  if (!texto || texto.length > MAX_TEXTO || /[[\]{}\n\r]/.test(texto)) throw new Error("texto fora do molde: " + texto);
  return { tipo, regra, chave, texto, tick, dados };
}
export function periodoDoTick(tick: number): Periodo {
  const hora = Math.floor((tick % TPD) / 60);
  for (const [nome, a, b] of PERIODOS) if (a <= hora && hora < b) return nome;
  throw new Error("hora fora do dia: " + hora);
}
export const diaDoTick = (tick: number): number => Math.floor(tick / TPD) + 1;
const cmp = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);
/** maximo com empate para o primeiro na ordem dada (como max() do Python sobre uma lista ordenada) */
function maxPor<T>(xs: T[], f: (x: T) => number): T { let m = xs[0]; for (const x of xs) if (f(x) > f(m)) m = x; return m; }
function minPor<T>(xs: T[], f: (x: T) => number): T { let m = xs[0]; for (const x of xs) if (f(x) < f(m)) m = x; return m; }
function mediana(xs: number[]): number {
  const s = [...xs].sort((a, b) => a - b), n = s.length;
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
}

export function episodios(acoesPet: [number, string][]): [number, string][] {
  const out: [number, string][] = []; let anterior: string | null = null;
  for (const [t, a] of acoesPet) { if (a !== anterior && a !== "ocioso") out.push([t, a]); anterior = a; }
  return out;
}

/* ------------------------------------------------------------ H */
function sequencias(ep: [number, string][], c: ConfigHistoria, fim: number): FatoHistoria[] {
  if (!ep.length) return [];
  const seguintes: Set<string>[] = [];
  let j = 0;
  ep.forEach(([t], i) => {
    j = Math.max(j, i + 1);
    while (j < ep.length && ep[j][0] <= t) j++;
    const s = new Set<string>();
    for (let k = j; k < ep.length && ep[k][0] <= t + c.janelaSeq; k++) s.add(ep[k][1]);
    seguintes.push(s);
  });
  const n = ep.length, acoes = [...new Set(ep.map(x => x[1]))].sort(cmp);
  const base = Object.fromEntries(acoes.map(b => [b, seguintes.filter(s => s.has(b)).length / n]));
  const out: FatoHistoria[] = [];
  for (const a of acoes) {
    const idx = ep.map((x, i) => (x[1] === a ? i : -1)).filter(i => i >= 0);
    if (idx.length < c.minSeq) continue;
    for (const b of acoes) {
      if (b === a || base[b] === 0) continue;
      const p = idx.filter(i => seguintes[i].has(b)).length / idx.length, lift = p / base[b];
      if (p >= c.probSeq && lift >= c.lift)
        out.push(fato("H", "sequencia", `H:seq:${a}:${b}`, `quase sempre ${PET_EU[b]} depois de ${PET_INF[a]}`, fim,
          { a, b, prob: p, lift, ocorrencias: idx.length }));
    }
  }
  return out;
}
function periodosPet(ep: [number, string][], c: ConfigHistoria, fim: number): FatoHistoria[] {
  const out: FatoHistoria[] = [];
  for (const a of [...new Set(ep.map(x => x[1]))].sort(cmp)) {
    const ts = ep.filter(x => x[1] === a).map(x => x[0]), media = ts.length / PERIODOS.length;
    for (const [nome] of PERIODOS) {
      const k = ts.filter(t => periodoDoTick(t) === nome).length;
      if (k >= c.minPeriodo && k >= c.fatorPeriodo * media)
        out.push(fato("H", "periodo", `H:per:${a}:${nome}`, `${TEXTO_PERIODO[nome]} eu ${PET_EU[a]} mais`, fim,
          { acao: a, periodo: nome, ocorrencias: k, media }));
    }
  }
  return out;
}

/* ------------------------------------------------------------ O */
function dono(r: RegistroVida, c: ConfigHistoria): FatoHistoria[] {
  const out: FatoHistoria[] = [], fim = r.tickFinal, acoes = r.acoesDono;
  if (acoes.length) {
    const n = acoes.length;
    for (const [nome] of PERIODOS) {
      const ts = acoes.filter(([t]) => periodoDoTick(t) === nome).map(([t]) => t);
      const dias = new Set(ts.map(diaDoTick)).size;
      if (ts.length / n >= c.fracaoPeriodoDono && dias >= c.diasPeriodoDono)
        out.push(fato("O", "periodo_dono", `O:per:${nome}`, `você costuma aparecer ${TEXTO_PERIODO[nome]}`, fim,
          { periodo: nome, fracao: ts.length / n, dias }));
    }
    const chaves = Object.keys(CUIDADO_DONO).sort(cmp);
    const cont = Object.fromEntries(chaves.map(a => [a, acoes.filter(x => x[1] === a).length]));
    const melhor = maxPor(chaves, a => cont[a]);
    if (cont[melhor] / n >= c.fracaoCuidado)
      out.push(fato("O", "cuidado_dono", `O:cui:${melhor}`, `o que você mais faz é ${CUIDADO_DONO[melhor]}`, fim,
        { acao: melhor, fracao: cont[melhor] / n }));
  }
  const manhas = r.janelas.filter(j => j.tipo === "chamado" && j.falso && (j.desfecho === "cedido" || j.desfecho === "corrigido"));
  if (manhas.length >= c.minManhas) {
    const cede = manhas.filter(j => j.desfecho === "cedido").length / manhas.length;
    if (cede >= c.fracaoCedeManha)
      out.push(fato("O", "cede_manha", "O:manha", "quando faço manha, você cede com petisco", fim, { fracao: cede, manhas: manhas.length }));
  }
  const chamados = r.janelas.filter(j => j.tipo === "aviso" || (j.tipo === "chamado" && !j.falso));
  if (chamados.length >= c.minChamados) {
    const med = mediana(chamados.map(j => j.fim - j.inicio));
    if (med <= c.demoraRapida)
      out.push(fato("O", "demora", "O:demora", "você atende meus chamados rápido", fim, { mediana_min: med, chamados: chamados.length, rapido: true }));
    else if (med >= c.demoraLenta)
      out.push(fato("O", "demora", "O:demora", "você demora para atender meus chamados", fim, { mediana_min: med, chamados: chamados.length, rapido: false }));
  }
  return out;
}

/* ------------------------------------------------------------ P */
export function rivalPadrao(nome: string): string {
  const resto = nome.includes(":") ? nome.slice(nome.indexOf(":") + 1) : "";
  const partes = resto.split("@")[0].split("_");
  return `o ${partes[partes.length - 1]}`;
}
function gostos(r: RegistroVida, c: ConfigHistoria, nomeRival: (n: string) => string): FatoHistoria[] {
  const out: FatoHistoria[] = [], fim = r.tickFinal;
  const desvio = Object.fromEntries(r.desvioPorAcao.filter(([a]) => a !== "ocioso"));
  const ordem = Object.keys(desvio).sort(cmp);
  if (ordem.length) {
    const alto = maxPor(ordem, a => desvio[a]), baixo = minPor(ordem, a => desvio[a]);
    if (desvio[alto] >= c.limiarGosto) out.push(fato("P", "gosto", `P:gosto:${alto}`, `gosto de ${PET_INF[alto]}`, fim, { acao: alto, desvio: desvio[alto] }));
    if (desvio[baixo] <= -c.limiarGosto) out.push(fato("P", "desgosto", `P:desgosto:${baixo}`, `não curto ${PET_INF[baixo]}`, fim, { acao: baixo, desvio: desvio[baixo] }));
  }
  if (r.sessoesTreino.length >= c.minSessoes) {
    const cont: Record<string, number> = {};
    for (const [, e] of r.sessoesTreino) cont[e] = (cont[e] ?? 0) + 1;
    const fav = maxPor(Object.keys(cont).sort(cmp), e => cont[e]);
    if (cont[fav] / r.sessoesTreino.length >= c.fracaoTreino)
      out.push(fato("P", "treino_favorito", `P:treino:${fav}`, `meu treino favorito é ${fav.replace(/_/g, " ")}`, fim,
        { exercicio: fav, fracao: cont[fav] / r.sessoesTreino.length }));
  }
  let ultimo: LutaRegistro | null = null;
  for (const x of r.lutas) {
    if (x.resultado === "derrota") ultimo = x;
    else if (x.resultado === "vitoria" && ultimo && x.rival === ultimo.rival) ultimo = null;
  }
  if (ultimo) out.push(fato("P", "revanche", `P:revanche:${ultimo.rival}`, `quero revanche contra ${nomeRival(ultimo.rival)}`, ultimo.tick, { rival: ultimo.rival }));
  return out;
}

/* ------------------------------------------------------------ L */
function marcos(r: RegistroVida, c: ConfigHistoria, nomeRival: (n: string) => string): FatoHistoria[] {
  const out: FatoHistoria[] = [];
  for (const [t, est] of r.evolucoes) out.push(fato("L", "evolucao", `L:evo:${est}`, `virei ${NIVEL[est]} no dia ${diaDoTick(t)}`, t, { estagio: est }));
  const primeira: Record<string, boolean> = {}, derrotas: Record<string, number> = {};
  for (const x of r.lutas) {
    const { resultado: res, rival: rv, tick: t } = x;
    if ((res === "vitoria" || res === "derrota") && !primeira[res]) {
      primeira[res] = true;
      const txt = res === "vitoria" ? "venci minha primeira luta" : "perdi minha primeira luta";
      out.push(fato("L", `primeira_${res}`, `L:primeira:${res}`, `${txt} no dia ${diaDoTick(t)}`, t, { rival: rv }));
    }
    if (res === "derrota") derrotas[rv] = (derrotas[rv] ?? 0) + 1;
    else if (res === "vitoria" && rv in derrotas) {
      const n = derrotas[rv]; delete derrotas[rv];
      if (n >= 2) out.push(fato("L", "venceu_depois", `L:depois:${rv}:${t}`, `perdi para ${nomeRival(rv)} ${n} vezes antes de vencer`, t, { rival: rv, derrotas: n }));
    }
    if (x.lesao) {
      const tratou = r.acoesDono.some(([td, a]) => a === "tratar_lesao" && t <= td);
      out.push(fato("L", "lesao", `L:lesao:${t}`, `me machuquei no dia ${diaDoTick(t)} ${tratou ? "e você me tratou" : "e ninguém me tratou"}`, t, { tratada: tratou }));
    }
  }
  const ticks = r.acoesDono.map(([t]) => t), ini = [0, ...ticks], fimT = [...ticks, r.tickFinal];
  ini.forEach((a, i) => {
    const b = fimT[i];
    if (b - a >= c.ausencia) {
      const h = Math.floor((b - a) / 60);
      out.push(fato("L", "ausencia", `L:ausencia:${a}`, `você sumiu por ${h} h no dia ${diaDoTick(a)}`, b, { inicio: a, fim: b, horas: h }));
    }
  });
  if (r.sombriaTick !== null) out.push(fato("L", "sombria", "L:sombria", "virei uma forma sombria", r.sombriaTick));
  if (r.filhoDeCruzamento) out.push(fato("L", "cruzamento", "L:cruzamento", "nasci de um cruzamento de dois pets", 0));
  return out;
}

/** todos os fatos do registro, em ordem fixa: L (por tick), H, P, O */
export function extrair(r: RegistroVida, c: ConfigHistoria = CHIS, nomeRival: (n: string) => string = rivalPadrao): FatoHistoria[] {
  const ep = episodios(r.acoesPet), fim = r.tickFinal;
  const ls = marcos(r, c, nomeRival).sort((a, b) => a.tick - b.tick || cmp(a.chave, b.chave));
  return [...ls, ...sequencias(ep, c, fim), ...periodosPet(ep, c, fim), ...gostos(r, c, nomeRival), ...dono(r, c)];
}

/** ate maxFatos para uma fala: marcos recentes, habitos, gostos, habitos do dono; citado nas ultimas falas vai para o fim;
    no maximo maxPorRegra de cada regra */
export function selecionar(fatos: FatoHistoria[], citadosRecentes: string[][] = [], c: ConfigHistoria = CHIS): FatoHistoria[] {
  const recentes = new Set(citadosRecentes.slice(-c.falasRecentes).flat());
  const ordem = (f: FatoHistoria) => ORDEM_TIPOS.indexOf(f.tipo);
  const chave = (x: FatoHistoria, y: FatoHistoria) =>
    (+recentes.has(x.chave) - +recentes.has(y.chave)) || (ordem(x) - ordem(y))
    || ((x.tipo === "L" ? -x.tick : 0) - (y.tipo === "L" ? -y.tick : 0)) || cmp(x.chave, y.chave);
  const out: FatoHistoria[] = [], porRegra: Record<string, number> = {};
  for (const f of [...fatos].sort(chave)) {
    if ((porRegra[f.regra] ?? 0) < c.maxPorRegra) { porRegra[f.regra] = (porRegra[f.regra] ?? 0) + 1; out.push(f); }
  }
  return out.slice(0, c.maxFatos);
}

/** o assunto de UMA fala: gira entre os tipos (o dado ha mais tempo primeiro) e, dentro do tipo, a ordem de selecionar */
export function escolherAssunto(fatos: FatoHistoria[], dadosRecentes: string[][] = [], c: ConfigHistoria = CHIS): FatoHistoria | null {
  const n = fatos.length || 1;
  const cands = selecionar(fatos, dadosRecentes, { ...c, maxFatos: n, maxPorRegra: n });
  if (!cands.length) return null;
  const ultimo: Record<string, number> = {};
  [...dadosRecentes].reverse().forEach((fala, idade) => { for (const k of fala) if (!(k[0] in ultimo)) ultimo[k[0]] = idade; });
  const tipos = [...new Set(cands.map(f => f.tipo))].sort((a, b) =>
    (-(ultimo[a] ?? 1e6)) - (-(ultimo[b] ?? 1e6)) || "LHPO".indexOf(a) - "LHPO".indexOf(b));
  return cands.find(f => f.tipo === tipos[0])!;
}

/** o registro de um pet v5 do jogo (o que o extrator le). desvio: da sonda do carater (motor/carater.ts) */
export function registroDoMotor(m: {
  e: { tick: number }; log: readonly unknown[][]; janelasFechadas: readonly { tipo: string; falso: boolean; desfecho: string; inicio: number; fim: number }[];
  vida5: { episodios: [number, string][]; lutas: LutaRegistro[]; sessoes: [number, string][] };
  evolucoes: readonly { tick: number; estagio: string }[]; sombria: boolean; origem: unknown;
}, desvio: [string, number][] = []): RegistroVida {
  const adulto = m.evolucoes.find(e => e.estagio === "adulto");
  return {
    tickFinal: m.e.tick,
    /* pets v12: a racao deixada pelo dono (o "dc") e o alimentar dele */
    acoesDono: m.log.filter(ev => ev[1] === "d" || ev[1] === "dc").map(ev => [ev[0] as number, ev[1] === "dc" ? "alimentar" : ev[2] as string]),
    acoesPet: m.vida5.episodios.map(([t, a]) => [t, a] as [number, string]),
    janelas: m.janelasFechadas.map(j => ({ tipo: j.tipo, falso: j.falso, desfecho: j.desfecho, inicio: j.inicio, fim: j.fim })),
    sessoesTreino: m.vida5.sessoes.map(([t, e]) => [t, e] as [number, string]),
    lutas: m.vida5.lutas.map(x => ({ ...x })),
    evolucoes: m.evolucoes.map(e => [e.tick, e.estagio] as [number, string]),
    sombriaTick: m.sombria && adulto ? adulto.tick : null,
    filhoDeCruzamento: m.origem !== null,
    desvioPorAcao: desvio,
  };
}
