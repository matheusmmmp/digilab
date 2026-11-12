/* LUTA_POC, a investigacao do nucleo, N2 (docs/PLANO_LUTA_NUCLEO.md, secao 2.1; D-N-1, D-N-2): as lutas fixas. O motor de hoje, sem chave
   nova, pelas entradas que o candidato ja traz (o tiro, a esquiva, o apoio e a elipse da LP6). Cada luta anda passo a passo, e a medida
   conta os eventos que o motor ja emite (dano, queda, queda_ringue, ambiente, pilar, tiro_bloqueado, runa, fim). Sem grade: nenhum
   numero do candidato muda. As sementes sao da faixa da investigacao (92101...92505, a D-N-2), com a derivacao da LP5.
   As perguntas (a tabela da secao 2.1 do plano):
   - serie (G1): o Mega tipico contra cada Mega da Liga, com a vida cheia, no mapa do lider: a vida que sobra no vencedor. O mesmo com o
     fator 0,1 nos rivais (o da grade lp5_3/r2), para ver quanto ele tira;
   - ringue (G2, A1): os pares de longe x de perto no Ringue e o Mega tipico contra os Megas da Torre. Cada queda: quem caiu e o que o
     levou a borda nos passos antes (o golpe que empurrou, o pulo da esquiva, ou o andar);
   - castelo (A1): os mesmos pares no Castelo: os tiros gastos nos pilares e a runa, por lado;
   - empates (D2): os pares do estagio nos 8 mapas: a causa de cada empate (o tiro de quem ja caiu, o dano do mapa, os dois no mesmo passo);
   - folego (T2): o pet com 8 pontos no folego contra ele sem treino, nos 8 mapas: o tamanho do pulo, as quedas e o dano do mapa logo depois;
   - espelho (S1): a forma contra ela mesma no Campo e na Praia: o lado A nas lutas com vencedor, quem acerta primeiro e os tiros que batem
     nas rochas, por lado.
   Os tamanhos sao PROPOSTOS, SEM FONTE.
   uso (em web/app): node scripts/equilibrio_poc/lutas_fixas_nucleo.ts --candidato lp5_3 -> scripts/medicoes/luta_nucleo/n2/<candidato>.json */
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  FORMAS_ARENA, IDS_CENA, LIGA, LIMITE_POC_MS, LUGARES_V6, ARENA_POR_ID, caraterCanonico, chaveSprite, configLutaPoc, criarLutaPoc, formaLiga,
  formaRivalInstalacao, mapaDoLugar, passoPoc, rivaisArena, sorteiosPoc,
  type FormaAdultaNormal, type IdCena,
} from "../../motor/index.ts";
import {
  ESTAGIOS_LUTA, TIPICO, argumento, commitAtual, esquivaDe, extrasLp6, lutadorDoPet, petDoEstagio, pontosNumStat, rivalCanonico, rivalDaForma,
  sementeLuta, tiroDaPoc, lutador, type Candidato, type Lado,
} from "./comum.ts";
import { basesDa } from "./faixas.ts";
import { CANDIDATOS } from "./candidatos.ts";
import { catAtr } from "./atributo_nucleo.ts";

const nomeC = argumento("candidato"), C: Candidato | undefined = CANDIDATOS[nomeC];
if (!C) throw new Error(`lutas fixas: candidato desconhecido ${nomeC} (${Object.keys(CANDIDATOS).join(", ")})`);
const BASES = basesDa("investigacao");
/** os tamanhos (PROPOSTOS, SEM FONTE) */
const TAM = { pets: 8, lutasSerie: 2, lutasPar: 4, lutasEmpate: 2, petsFolego: 8, lutasFolego: 2, lutasEspelho: 8, tentativasTorre: 2 };
const TIRO = tiroDaPoc(C.tiro) ? undefined : C.tiro, ESQ = esquivaDe(C), LP6 = extrasLp6(C);
const r3 = (x: number) => Math.round(x * 1000) / 1000;
let LUTAS = 0;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type L = any;
/** a luta montada como na bancada (comum.ts lutar), mas devolvida para andar passo a passo */
function montar(cena: IdCena, s: number, a: Lado, b: Lado): L {
  LUTAS++;
  return criarLutaPoc(configLutaPoc({ cena, semente: s, a, b, ...(TIRO ? { tiro: TIRO } : {}), ...(ESQ ? { esquiva: ESQ } : {}),
    ...(LP6.apoio ? { apoio: LP6.apoio } : {}), ...(LP6.arenaPorEstagio ? { arenaPorEstagio: LP6.arenaPorEstagio } : {}) }, LP6.tabela), sorteiosPoc(s));
}
/** anda ate o fim, chamando f(eventos, luta) a cada passo */
function andar(Lt: L, f: (ev: L[], Lt: L) => void): void {
  while (!Lt.fim && Lt.relogio < LIMITE_POC_MS) f(passoPoc(Lt), Lt);
}
const inc = (m: Record<string, number>, k: string, d = 1) => { m[k] = (m[k] ?? 0) + d; };
const atira = (k: string) => !!FORMAS_ARENA[k].golpe.proj;
const sem = (base: number, off: number, k: number) => sementeLuta(base, off + k);

/* ---------------------------------------------------------------- serie (G1) */
function serie() {
  const megasLiga = LIGA.map((x, k) => {
    const f = formaLiga(k), mapa = mapaDoLugar(LUGARES_V6[ARENA_POR_ID[x.arena].lugar]);
    return { chave: chaveSprite(f), mapa, um: rivalDaForma(C!, f, caraterCanonico(x.adulta), 0, 1), dez: rivalDaForma(C!, f, caraterCanonico(x.adulta), 0, .1) };
  });
  const out: Record<string, unknown> = {};
  for (const fator of ["um", "dez"] as const) {
    const porRival: Record<string, { lutas: number; vitorias: number; soma_vida_que_sobra: number; por_atributo: Record<string, { lutas: number; vitorias: number; soma: number }> }> = {};
    let somaPerdas = 0, nPets = 0;
    for (const base of BASES) for (let i = 0; i < TAM.pets; i++) {
      const p = petDoEstagio(base, i, "mega"), pet: Lado = { forma: p.chave, stats: lutadorDoPet(C!, p, TIPICO.mega) };
      let perdaPet = 0;
      megasLiga.forEach((rv, j) => {
        for (let q = 0; q < TAM.lutasSerie; q++) {
          const Lt = montar(rv.mapa, sem(base, 100_000 + (i * 6 + j) * TAM.lutasSerie, q), pet, { forma: rv.chave, stats: rv[fator] }); andar(Lt, () => {});
          const k = `${j + 1}_${rv.chave}_${rv.mapa}`, a = catAtr(p.chave, rv.chave), r = porRival[k] ??= { lutas: 0, vitorias: 0, soma_vida_que_sobra: 0, por_atributo: {} };
          const pa = r.por_atributo[a] ??= { lutas: 0, vitorias: 0, soma: 0 };
          const sobra = Lt.vencedor === "a" ? Lt.a.hp / Lt.a.st.hp : 0;
          r.lutas++; pa.lutas++; if (Lt.vencedor === "a") { r.vitorias++; pa.vitorias++; r.soma_vida_que_sobra += sobra; pa.soma += sobra; }
          perdaPet += 1 - sobra;
        }
      });
      somaPerdas += perdaPet / TAM.lutasSerie; nPets++;
    }
    out[fator === "um" ? "fator_1" : "fator_0_1"] = {
      /* a vida que sobra no pet, so nas vitorias; a soma das perdas ao longo dos 6 (a perda de uma derrota conta 1) */
      por_rival: Object.fromEntries(Object.entries(porRival).map(([k, r]) => [k, { lutas: r.lutas, taxa: r3(r.vitorias / r.lutas), vida_que_sobra_na_vitoria: r.vitorias ? r3(r.soma_vida_que_sobra / r.vitorias) : null,
        por_atributo: Object.fromEntries(Object.entries(r.por_atributo).map(([q, z]) => [q, { lutas: z.lutas, taxa: r3(z.vitorias / z.lutas), vida_que_sobra_na_vitoria: z.vitorias ? r3(z.soma / z.vitorias) : null }])) }])),
      soma_media_das_perdas_nos_6: r3(somaPerdas / nPets), pets: nPets,
    };
  }
  /* quanto o fator 0,1 tira dos numeros de cada rival (a conta pelo candidato) */
  out.rivais = megasLiga.map(rv => ({ chave: rv.chave, mapa: rv.mapa, vida: [rv.um.hp, rv.dez.hp], ataque: [r3(rv.um.atk), r3(rv.dez.atk)] }));
  return out;
}

/* ---------------------------------------------------------------- o rastro de cada lutador nos passos antes de um evento */
interface Marca { dash: boolean; golpe: boolean; hab: boolean; recua: boolean; estado: string; norm: number }
const JANELA = 16;
function rastreador() {
  const buf: Record<string, Marca[]> = { a: [], b: [] };
  return {
    passo(ev: L[], Lt: L) {
      for (const lado of ["a", "b"] as const) {
        const u = Lt[lado], o = Lt[lado === "a" ? "b" : "a"];
        const golpe = ev.find((e: L) => e.tipo === "dano" && e.alvo.lado === lado);
        const dx = u.x - o.x, dy = u.y - o.y, norm = Math.hypot((u.x - Lt.el.cx) / Lt.el.rx, (u.y - Lt.el.cy) / Lt.el.ry);
        const ant = buf[lado][buf[lado].length - 1];
        const recua = !!ant && u.estado === "run" && u.dash <= 0 && Math.hypot(dx, dy) > 0 && norm > ant.norm;
        buf[lado].push({ dash: u.dash > 0, golpe: !!golpe, hab: !!golpe?.hab, recua, estado: u.estado, norm });
        if (buf[lado].length > JANELA) buf[lado].shift();
      }
    },
    /** a causa da queda do lado: o golpe nos ultimos 4 passos (o empurrao), senao o pulo nos ultimos 16, senao o andar (o recuo ou a IA) */
    causa(lado: "a" | "b"): string {
      const b = buf[lado], n = b.length;
      for (let k = n - 1; k >= Math.max(0, n - 4); k--) if (b[k].golpe) return b[k].hab ? "golpe_habilidade" : "golpe";
      if (b.some(m => m.dash)) return "pulo_esquiva";
      if (b.slice(-6).some(m => m.recua)) return "andar_para_fora";
      return "outro";
    },
  };
}

/* ---------------------------------------------------------------- ringue (G2, A1) e castelo (A1): os pares de longe x de perto */
function pares(cena: IdCena) {
  const out: Record<string, unknown> = {};
  for (const est of ESTAGIOS_LUTA) {
    const rv = rivaisArena(est), longe = rv.filter(atira), perto = rv.filter(k => !atira(k)), lados = Object.fromEntries(rv.map(k => [k, { forma: k, stats: rivalCanonico(C!, k) }]));
    const quedas: Record<string, Record<string, number>> = { longe: {}, perto: {} }, cont = { lutas: 0, vitoria_longe: 0, empates: 0, lutas_neutras: 0, vitoria_longe_neutras: 0 };
    const pilar: Record<string, number> = {}, runa: Record<string, number> = {}, comRuna: Record<string, { lutas: number; vence: number }> = {};
    let x0 = 0;
    for (const x of longe) for (const y of perto) for (const base of BASES) for (let q = 0; q < TAM.lutasPar; q++) for (const ladoLonge of ["a", "b"] as const) {
      const s = sem(base, 200_000 + (cena === "ringue" ? 0 : 50_000), x0++);
      const A = ladoLonge === "a" ? lados[x] : lados[y], B = ladoLonge === "a" ? lados[y] : lados[x], Lt = montar(cena, s, A, B), tr = rastreador();
      const tipo = (lado: string) => lado === ladoLonge ? "longe" : "perto", pegou: Record<string, boolean> = {};
      andar(Lt, (ev, Lt2) => {
        for (const e of ev) {
          if (e.tipo === "queda_ringue") inc(quedas[tipo(e.u.lado)], tr.causa(e.u.lado));
          if (e.tipo === "pilar") inc(pilar, tipo(e.u.lado));
          if (e.tipo === "tiro_bloqueado") inc(pilar, `${tipo(e.u.lado)}_bloqueado_${e.obst}`);
          if (e.tipo === "runa") { inc(runa, tipo(e.u.lado)); pegou[tipo(e.u.lado)] = true; }
        }
        tr.passo(ev, Lt2);
      });
      const venceLonge = Lt.vencedor === ladoLonge, neutro = catAtr(x, y) === "0";
      cont.lutas++; if (venceLonge) cont.vitoria_longe++; if (Lt.vencedor === null) cont.empates++;
      if (neutro) { cont.lutas_neutras++; if (venceLonge) cont.vitoria_longe_neutras++; }
      if (cena === "castelo") { const k = pegou.longe && pegou.perto ? "os_dois" : pegou.longe ? "so_longe" : pegou.perto ? "so_perto" : "nenhum"; const z = comRuna[k] ??= { lutas: 0, vence: 0 }; z.lutas++; if (venceLonge) z.vence++; }
    }
    out[est] = {
      longe: longe.length, perto: perto.length, ...cont, taxa_longe: cont.lutas ? r3(cont.vitoria_longe / cont.lutas) : null,
      taxa_longe_neutras: cont.lutas_neutras ? r3(cont.vitoria_longe_neutras / cont.lutas_neutras) : null,
      ...(cena === "ringue" ? { quedas_por_lutador_e_causa: quedas, quedas_por_luta: { longe: r3(Object.values(quedas.longe).reduce((a, b) => a + b, 0) / Math.max(1, cont.lutas)), perto: r3(Object.values(quedas.perto).reduce((a, b) => a + b, 0) / Math.max(1, cont.lutas)) } } : {}),
      ...(cena === "castelo" ? { pilar_e_bloqueio_por_luta: Object.fromEntries(Object.entries(pilar).map(([k, v]) => [k, r3(v / Math.max(1, cont.lutas))])), runa_por_luta: Object.fromEntries(Object.entries(runa).map(([k, v]) => [k, r3(v / Math.max(1, cont.lutas))])),
        taxa_longe_por_runa: Object.fromEntries(Object.entries(comRuna).map(([k, z]) => [k, { lutas: z.lutas, taxa_longe: r3(z.vence / z.lutas) }])) } : {}),
    };
  }
  return out;
}
/** a Torre: o Mega tipico contra os Megas sorteados, no Ringue, com a vida cheia: a derrota e as quedas de cada lado */
function torre() {
  const quedas: Record<string, Record<string, number>> = { pet: {}, rival: {} };
  let lutas = 0, vence = 0, perdeComQueda = 0, perdas = 0, somaSobra = 0;
  for (const base of BASES) for (let i = 0; i < TAM.pets; i++) {
    const p = petDoEstagio(base, i, "mega"), pet: Lado = { forma: p.chave, stats: lutadorDoPet(C!, p, TIPICO.mega) };
    for (let t = 0; t < TAM.tentativasTorre; t++) {
      const s = sem(base, 300_000 + i * TAM.tentativasTorre, t), f = formaRivalInstalacao(s, 0);
      const Lt = montar("ringue", s, pet, { forma: chaveSprite(f), stats: rivalDaForma(C!, f, caraterCanonico(f.adulta as FormaAdultaNormal), 0, 1) }), tr = rastreador();
      let caiu = false;
      andar(Lt, (ev, Lt2) => { for (const e of ev) if (e.tipo === "queda_ringue") { inc(quedas[e.u.lado === "a" ? "pet" : "rival"], tr.causa(e.u.lado)); if (e.u.lado === "a") caiu = true; } tr.passo(ev, Lt2); });
      lutas++; if (Lt.vencedor === "a") { vence++; somaSobra += Lt.a.hp / Lt.a.st.hp; } else { perdas++; if (caiu) perdeComQueda++; }
    }
  }
  return { lutas, taxa: r3(vence / lutas), vida_que_sobra_na_vitoria: vence ? r3(somaSobra / vence) : null, derrotas_com_queda_do_pet: perdas ? r3(perdeComQueda / perdas) : null, quedas_por_lado_e_causa: quedas };
}

/* ---------------------------------------------------------------- empates (D2) */
function empates() {
  const out: Record<string, unknown> = {};
  for (const est of ESTAGIOS_LUTA) {
    const rv = rivaisArena(est), lados = Object.fromEntries(rv.map(k => [k, { forma: k, stats: rivalCanonico(C!, k) }]));
    const causa: Record<string, number> = {}, porMapa: Record<string, number> = {}; let lutas = 0, emp = 0, x0 = 0;
    for (const m of IDS_CENA) for (const x of rv) for (const y of rv) for (const base of BASES) for (let q = 0; q < TAM.lutasEmpate; q++) {
      const Lt = montar(m, sem(base, 400_000, x0++), lados[x], lados[y]);
      let primeira: string | null = null, tiroMorto = false, mapaMata = false, mesmoPasso = false;
      andar(Lt, ev => {
        const quedas = ev.filter((e: L) => e.tipo === "queda");
        for (const e of ev) {
          if (e.tipo === "dano" && Lt[e.at.lado].morto && primeira === e.at.lado && e.resta <= 0) tiroMorto = true;
          if (e.tipo === "queda" && e.motivo) mapaMata = true;
        }
        if (quedas.length === 2 && primeira === null) mesmoPasso = true;
        if (quedas.length && primeira === null) primeira = quedas[0].u.lado;
      });
      lutas++;
      if (Lt.vencedor === null) {
        emp++; inc(porMapa, m);
        inc(causa, !Lt.fim ? "sem_fim" : tiroMorto ? "tiro_de_quem_caiu" : mesmoPasso ? "os_dois_no_mesmo_passo" : mapaMata ? "dano_do_mapa" : "outro");
      }
    }
    out[est] = { lutas, empates: emp, taxa_empate: r3(emp / lutas), por_causa: causa, por_mapa: porMapa };
  }
  return out;
}

/* ---------------------------------------------------------------- folego (T2) */
function folego() {
  const out: Record<string, unknown> = {};
  for (const est of ["crianca", "adulto"] as const) {
    let lutas = 0, vence = 0, pulos = 0, somaPulo = 0, maiorPulo = 0, quedaPosPulo = 0, mapaPosPulo = 0, cercaPosPulo = 0;
    const porMapa: Record<string, { lutas: number; vence: number }> = {};
    for (const base of BASES) for (let i = 0; i < TAM.petsFolego; i++) {
      const p = petDoEstagio(base, i, est), A: Lado = { forma: p.chave, stats: lutador(C!, p.forma, p.carater, pontosNumStat("folego", 8)) }, B: Lado = { forma: p.chave, stats: lutadorDoPet(C!, p, 0) };
      for (const m of IDS_CENA) for (let q = 0; q < TAM.lutasFolego; q++) {
        const Lt = montar(m, sem(base, 500_000 + (i * IDS_CENA.length + IDS_CENA.indexOf(m)) * TAM.lutasFolego, q), A, B);
        let emPulo = false, x0 = 0, y0 = 0, desde = -1, passo = 0;
        andar(Lt, (ev, Lt2) => {
          passo++;
          const u = Lt2.a;
          if (u.dash > 0 && !emPulo) { emPulo = true; x0 = u.x; y0 = u.y; }
          if (u.dash <= 0 && emPulo) {
            emPulo = false; const d = Math.hypot(u.x - x0, u.y - y0); pulos++; somaPulo += d; maiorPulo = Math.max(maiorPulo, d); desde = passo;
            const E = Lt2.el, n = Math.hypot((u.x - E.cx) / (E.rx - 20), (u.y - E.cy) / (E.ry - 10)); if (n > .995) cercaPosPulo++;
          }
          if (desde >= 0 && passo - desde <= 30) for (const e of ev) {
            if (e.tipo === "queda_ringue" && e.u.lado === "a") quedaPosPulo++;
            if (e.tipo === "ambiente" && e.u.lado === "a") mapaPosPulo++;
          }
        });
        lutas++; const z = porMapa[m] ??= { lutas: 0, vence: 0 }; z.lutas++; if (Lt.vencedor === "a") { vence++; z.vence++; }
      }
    }
    out[est] = { lutas, taxa: r3(vence / lutas), por_mapa: Object.fromEntries(Object.entries(porMapa).map(([m, z]) => [m, r3(z.vence / z.lutas)])),
      pulos_por_luta: r3(pulos / lutas), pulo_medio_px: pulos ? r3(somaPulo / pulos) : null, maior_pulo_px: r3(maiorPulo),
      pulos_que_acabam_na_cerca: pulos ? r3(cercaPosPulo / pulos) : null, quedas_do_ringue_ate_30_passos_depois: quedaPosPulo, eventos_de_dano_do_mapa_ate_30_passos_depois: mapaPosPulo };
  }
  return out;
}

/* ---------------------------------------------------------------- espelho (S1) */
function espelho() {
  const out: Record<string, unknown> = {};
  for (const est of ESTAGIOS_LUTA) {
    const rv = rivaisArena(est), porMapa: Record<string, unknown> = {};
    for (const m of ["campo", "praia", "ringue"] as IdCena[]) {
      let a = 0, b = 0, e = 0, primeiroA = 0, primeiroB = 0, x0 = 0, ganhaQuemAcertaPrimeiro = 0;
      const bloq: Record<string, number> = {};
      for (const k of rv) for (const base of BASES) for (let q = 0; q < TAM.lutasEspelho; q++) {
        const lado: Lado = { forma: k, stats: rivalCanonico(C!, k) }, Lt = montar(m, sem(base, 600_000, x0++), lado, lado);
        let primeiro: string | null = null;
        andar(Lt, ev => { for (const z of ev) { if (z.tipo === "dano" && primeiro === null) primeiro = z.at.lado; if (z.tipo === "tiro_bloqueado") inc(bloq, `${z.u.lado}_${z.obst}`); } });
        if (Lt.vencedor === "a") a++; else if (Lt.vencedor === "b") b++; else e++;
        if (primeiro === "a") primeiroA++; else if (primeiro === "b") primeiroB++;
        if (primeiro && Lt.vencedor === primeiro) ganhaQuemAcertaPrimeiro++;
      }
      porMapa[m] = { lado_a_com_vencedor: r3(a / Math.max(1, a + b)), empates: e, lutas: a + b + e, primeiro_golpe_do_a: r3(primeiroA / Math.max(1, primeiroA + primeiroB)),
        vence_quem_acerta_primeiro: r3(ganhaQuemAcertaPrimeiro / Math.max(1, a + b)), tiros_bloqueados_por_lado: bloq };
    }
    out[est] = porMapa;
  }
  return out;
}

/* ---------------------------------------------------------------- a saida */
const t0 = Date.now();
const dados = { serie: serie(), ringue: pares("ringue"), torre: torre(), castelo: pares("castelo"), empates: empates(), folego: folego(), espelho: espelho() };
const SAIDA = fileURLToPath(new URL("../medicoes/luta_nucleo/n2/", import.meta.url));
mkdirSync(SAIDA, { recursive: true });
const res = { tarefa: "LUTA_POC, investigacao do nucleo, N2", commit: commitAtual(), candidato: C, faixa: "investigacao", bases: BASES, tamanhos: TAM, lutas: LUTAS, segundos: (Date.now() - t0) / 1000, dados };
writeFileSync(`${SAIDA}${nomeC}.json`, JSON.stringify(res, null, 1) + "\n");
console.log(`lutas fixas ${nomeC}: ${LUTAS} lutas em ${res.segundos} s -> ${SAIDA}${nomeC}.json`);
