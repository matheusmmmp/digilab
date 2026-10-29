/* Os dados do jogo da arena (Assets/arena_up/dados, fora do git; Assets/gerar_arena_up.py) e as regras que leem deles: conferencia que
   falha alto, as tags do atlas, o status no nivel, o triangulo de atributos e a compensacao de ritmo. Porte do arena.html. */
import { EQ } from "./constantes.ts";
import type { AtlasDigimon, Atributo, DadosArena, GolpeBase, StatusJogo } from "./tipos.ts";

const ATRIBUTOS: readonly Atributo[] = ["Vaccine", "Virus", "Data", "Free", "None", "Unknown"];
/** o golpe de quem nao tem script de ataque no jogo (10 dos 280): regra do prototipo, PROPOSTO, PROTOTIPO */
export const GOLPE_GENERICO: GolpeBase & { skill: null } = { anim: "Attack_1", t: 0.4, proj: null, hits: [], skill: null };

/** os recuos explicitos (P4, Matheus, 2026-10-29): a tela avisa uma vez; nada aqui e silencioso */
export interface Recuos {
  /** Digimon cuja animacao do golpe ou da habilidade nao tem a tag no atlas: anima e conta o tempo da tag de recuo */
  tag: { n: string; anim: string; usa: string }[];
  /** Digimon sem script de ataque: golpe generico */
  semGolpe: string[];
  /** Digimon sem registro de status no jogo: status genericos */
  semStatus: string[];
}

const falha = (msg: string): never => { throw new Error(`dados da arena: ${msg}`); };
const num = (x: unknown, onde: string): number => (typeof x === "number" && Number.isFinite(x) ? x : falha(`${onde} nao e numero`));

/** confere a forma dos JSON e devolve os recuos; levanta erro se faltar campo, Digimon ou atributo */
export function conferirDados(d: DadosArena): Recuos {
  if (!d || typeof d !== "object") falha("vazios");
  for (const k of ["status", "golpes", "atributos", "atlas"] as const) if (!d[k] || typeof d[k] !== "object") falha(`falta ${k}`);
  const nomes = Object.keys(d.atlas.d ?? falha("atlas sem d"));
  if (nomes.length === 0) falha("atlas vazio");
  const rec: Recuos = { tag: [], semGolpe: [], semStatus: [] };
  for (const n of nomes) {
    const A = d.atlas.d[n];
    if (!Array.isArray(A.f) || !Array.isArray(A.t) || A.t.length === 0) falha(`${n}: atlas sem quadros ou tags`);
    for (const t of A.t) if (!A.f[t[1]] || !A.f[t[2]]) falha(`${n}: tag ${t[0]} fora dos quadros`);
    for (const f of A.f) num(f[2], `${n}: duracao de quadro`);
    num(A.w, `${n}.w`); num(A.h, `${n}.h`);
    if (!ATRIBUTOS.includes(d.atributos[n])) falha(`${n}: sem atributo (${String(d.atributos[n])})`);
    if (!(n in d.status)) rec.semStatus.push(n);
    const g = d.golpes[n];
    if (!g) { rec.semGolpe.push(n); continue; }
    for (const [base, rot] of [[g, "golpe"], [g.skill, "habilidade"]] as const) {
      if (!base) continue;
      if (typeof base.anim !== "string") falha(`${n}: ${rot} sem animacao`);
      num(base.t, `${n}: instante do ${rot}`);
      if (!Array.isArray(base.hits)) falha(`${n}: ${rot} sem impactos`);
      if (base.proj) num(base.proj.vel, `${n}: velocidade do projetil`);
      const tg = tagDe(A, base.anim);
      if (tg[0] !== base.anim) rec.tag.push({ n, anim: base.anim, usa: tg[0] });
    }
  }
  for (const n of Object.keys(d.golpes)) if (!d.atlas.d[n]) falha(`${n}: golpe sem atlas`);
  for (const [n, s] of Object.entries(d.status)) {
    if (!s.base || !s.nivel) falha(`${n}: status sem base ou nivel`);
    for (const k of ["HP", "Attack", "Defense", "CriticalRate", "EvadeRate", "StunRate"] as const) num(s.base[k], `${n}.base.${k}`);
    for (const k of ["HP", "Attack", "Defense"] as const) num(s.nivel[k], `${n}.nivel.${k}`);
  }
  if (!refRookie(d.status)) falha("nenhum parceiro Rookie com status proprio (a referencia dos estagios)");
  return rec;
}

/** a tag de uma animacao: a de mesmo nome; senao a que comeca com as 4 primeiras letras; senao a primeira do atlas (o recuo do
    prototipo, explicito desde a P4: conferirDados lista quem cai nele) */
export function tagDe(A: AtlasDigimon, nome: string): [string, number, number] {
  return A.t.find(t => t[0] === nome) || A.t.find(t => t[0].toLowerCase().startsWith(nome.toLowerCase().slice(0, 4))) || A.t[0];
}
/** duracao (ms) de uma tag: a soma das duracoes dos quadros */
export function duracaoTag(A: AtlasDigimon, nome: string): number {
  const tg = tagDe(A, nome);
  return A.f.slice(tg[1], tg[2] + 1).reduce((s, f) => s + f[2], 0);
}

/** o perfil Rookie do jogo, referencia da diferenca entre estagios: o primeiro parceiro Rookie com status proprio, na ordem do JSON */
export function refRookie(status: Record<string, StatusJogo>): StatusJogo["base"] | null {
  const rk = Object.values(status).find(v => v.tipo === "PartnerDigiMon" && v.estagio === "Rookie" && !v.estimado);
  return rk ? rk.base : null;
}

/** status de um Digimon no nivel, da tabela do jogo (vida dividida pelo ritmo); a diferenca para o perfil Rookie e o ganho por nivel
    valem EQ.pesoEstagio nos parceiros e nos estimados */
export function statusDoJogo(d: DadosArena, n: string, nivel: number, ritmo: number) {
  const s = d.status[n]; if (!s) return null;
  const k = nivel - 1, l = s.nivel;
  const ref = refRookie(d.status), pe = s.tipo === "PartnerDigiMon" || s.estimado ? EQ.pesoEstagio : 1;
  const b = ref ? { ...s.base, HP: ref.HP + (s.base.HP - ref.HP) * pe, Attack: ref.Attack + (s.base.Attack - ref.Attack) * pe, Defense: ref.Defense + (s.base.Defense - ref.Defense) * pe } : s.base;
  const kk = k * EQ.pesoEstagio;
  return { hp: Math.max(1, Math.round((b.HP + l.HP * kk) / ritmo)), atk: Math.round(b.Attack + l.Attack * kk), def: Math.round(b.Defense + l.Defense * kk),
    crit: b.CriticalRate, esquiva: b.EvadeRate, atordoa: b.StunRate };
}

/** triangulo de atributos (o classico; o jogo nao traz a regra): chave vence valor */
export const VENCE: Partial<Record<Atributo, Atributo>> = { Vaccine: "Virus", Virus: "Data", Data: "Vaccine" };
export function multAtr(a: Atributo, b: Atributo, forca: number): number {
  if (VENCE[a] === b) return forca;
  if (VENCE[b] === a) return 1 / forca;
  return 1;
}
/** golpe mais demorado e projetil mais lento batem mais forte (EQ.kGolpe, EQ.kProj) */
export const fatorRitmo = (d: GolpeBase): number =>
  Math.pow(Math.max(0.2, d.t) / 0.5, EQ.kGolpe) * (d.proj ? Math.pow(30 / (d.proj.vel || 30), EQ.kProj) : 1);
