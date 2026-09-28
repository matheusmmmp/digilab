/* Donos sinteticos para treinar rivais e para a aba Cenarios (espelho de donos.py). Os chamados abertos do
   bebe viram a primeira acao de quem cuida (so na web: a evolucao nao existe no Python). */
import { ACAO_CHAMADO, ACOES_DONO, CAT, CD, TPD } from "./constantes.ts";
import { eNoite } from "./estado.ts";
import { Motor } from "./motor.ts";
import { criarRng, hashSemente, type Rng } from "./rng.ts";
import type { AcaoDono, AcaoPet, Chamado, EstadoVida } from "./tipos.ts";

export type TipoDono = "atencioso" | "relapso" | "aleatorio" | "incoerente";
/** o que o dono ve em cada passo */
export interface VisaoDono {
  e: EstadoVida; acao: AcaoPet; passo: number; passos: number; orc: number; gasto: number; min: number; max: number; atrasado: boolean; chamados: Chamado[];
}
export interface Dono { decidir(v: VisaoDono, r: Rng): AcaoDono[] }

export function cuidadosNecessarios(e: EstadoVida): AcaoDono[] {
  const a: AcaoDono[] = [];
  if (e.fome < CD.limAlim) a.push("alimentar");
  if (e.higiene < CD.limLimpar || e.sujeira >= CD.sujLimpar) a.push("limpar");
  if (e.humor < CD.limHumBrinc) a.push("brincar");
  return a;
}
export function julgar(e: EstadoVida, acao: AcaoPet): number {
  const cansado = e.energia < CD.limSono, noite = eNoite(e.tick % TPD);
  const precisa = Math.min(e.fome, e.higiene) < CD.limPedido;
  switch (acao) {
    case "dormir": return (cansado || noite) ? 1 : -1;
    case "chamar_atencao": return precisa ? 1 : -1;
    case "emburrar": return -1;
    case "brincar": case "explorar": return (cansado || precisa) ? -1 : 1;
    case "comer": return e.fome < CD.limAlim ? 1 : 0;
    default: return 0;
  }
}
const fb = (s: number): AcaoDono => s > 0 ? "elogiar" : "repreender";
const atenderChamados = (v: VisaoDono): AcaoDono[] => (v.chamados || []).map(c => ACAO_CHAMADO[c][0]);

export function criarDono(tipo: TipoDono): Dono {
  const base = (desejo: (v: VisaoDono, r: Rng) => AcaoDono[], preencher: (v: VisaoDono, r: Rng) => AcaoDono): Dono => ({
    decidir(v, r) { const a = desejo(v, r).slice(0, v.max); while (a.length < v.min) a.push(preencher(v, r)); return a; },
  });
  if (tipo === "atencioso") return base(
    (v) => { const a = [...atenderChamados(v), ...cuidadosNecessarios(v.e)]; if (v.atrasado) { const s = julgar(v.e, v.acao); if (s) a.push(fb(s)); } return a; },
    (v) => { const s = julgar(v.e, v.acao); return s ? fb(s) : "acariciar"; });
  if (tipo === "incoerente") return base(
    (v, r) => { const a = [...atenderChamados(v), ...cuidadosNecessarios(v.e)]; if (v.atrasado) a.push(r.random() < CD.probElogioInc ? "elogiar" : "repreender"); return a; },
    (_v, r) => r.random() < CD.probElogioInc ? "elogiar" : "repreender");
  if (tipo === "aleatorio") {
    let plano: number[] | null = null;
    return base((v, r) => {
      if (!plano) { plano = new Array<number>(v.passos).fill(0); let c = 0; while (c < v.orc) { const p = r.int(v.passos); if (plano[p] < CD.maxPasso) { plano[p]++; c++; } } }
      return Array.from({ length: plano[v.passo] }, () => ACOES_DONO[r.int(ACOES_DONO.length)]);
    }, (_v, r) => ACOES_DONO[r.int(ACOES_DONO.length)]);
  }
  if (tipo === "relapso") {
    const ppd = TPD / CD.passo; let visitas = new Set<number>(), dia = -1;
    return base((v, r) => {
      const d = Math.floor(v.passo / ppd);
      if (d !== dia) {
        const ini = d * ppd, fim = Math.min(ini + ppd, v.passos); const pool: number[] = []; for (let p = ini; p < fim; p++) pool.push(p);
        visitas = new Set(); while (visitas.size < Math.min(CD.visitasRelapso, pool.length)) visitas.add(pool[r.int(pool.length)]); dia = d;
      }
      if (!visitas.has(v.passo)) return [];
      const diasTot = Math.ceil(v.passos / ppd), futuros = diasTot - 1 - d;
      const rest = [...visitas].filter(p => p >= v.passo).length + CD.visitasRelapso * futuros;
      const cota = Math.ceil((v.orc - v.gasto) / rest);
      const raj: AcaoDono[] = [...atenderChamados(v), "alimentar", "limpar", "brincar"]; const s = julgar(v.e, v.acao); if (s) raj.push(fb(s));
      while (raj.length < cota) raj.push("acariciar");
      return raj.slice(0, cota);
    }, () => "acariciar");
  }
  throw new Error("dono desconhecido: " + tipo);
}
export function treinarRival(tipo: TipoDono, dias: number, semente: number): Motor { return treinarPet(tipo, dias, CD.porDia, semente); }
export function treinarPet(tipo: TipoDono, dias: number, porDia: number, semente: number): Motor {
  const m = new Motor(semente), dono = criarDono(tipo), r = criarRng(hashSemente("dono", semente, tipo));
  const passos = Math.round(dias * TPD / CD.passo), orc = Math.round(porDia * dias);
  if (passos < 1) throw new Error("dias de vida precisa ser positivo");
  if (orc < 1) throw new Error("o orçamento precisa ter pelo menos 1 interação");
  if (orc > passos * CD.maxPasso) throw new Error(`orçamento de ${orc} interações não cabe em ${passos} passos (máximo ${CD.maxPasso} por passo)`);
  let gasto = 0;
  for (let p = 0; p < passos; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, r);
    if (acoes.length > max || acoes.length < min) throw new Error(`dono ${tipo} violou o orçamento no passo ${p}`);
    for (const a of acoes) { m.observar(a); gasto++; }
    /* sparring do adolescente (cronograma): uma luta por passo contra o bot aleatorio, ate o minimo */
    if (m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) m.lutar("aleatorio", hashSemente("sparring", semente, p));
  }
  if (gasto !== orc) throw new Error(`rival terminou com ${gasto}/${orc} interações`);
  return m;
}
