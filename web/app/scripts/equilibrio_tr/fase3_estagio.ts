/* Rodada de equilibrio do combate em tempo real, fase 3: o estagio, o treino e o aprendizado (docs/PLANO_EQUILIBRIO_COMBATE_TR.md, metas
   P-1 a P-4). So o motor, sem tela, CPU contra CPU, com semente, em cima das fases 1 e 2 (o RELOGIO_V14 e as LISTAS_V14, os candidatos).
   O pet tipico (plano, secao 3): a forma de referencia do estagio (Rookie: os 2 ramos; Champion: as 4 linhas; Ultimate e Mega: as 8
   formas, o Mega com as listas do Ultimate), o carater canonico, o treino uniforme do treino tipico (CIT.tipico) ou nenhum, como na
   campanha (o treino absoluto, na escala dos pets v13: a CESC_V9, ou a candidata de --escala). Mede:
   - P-1 o de baixo com o treino tipico contra o de cima sem treino (as 4 especies de cada lado; o limite fica com o de cima, o
     desafiado): os vizinhos em pontos e os de dois estagios em vitorias (o metodo da M-B1 da rodada geral);
   - P-2 no mesmo estagio, a mesma forma e a mesma especie, o tipico contra o sem treino (no limite, a fracao de vida);
   - P-3 e P-4 com o aprendizado: o pet tipico do Champion e do Ultimate semeia a lista (GambitsPet.semear), luta CAT.sparring lutas contra
     o rival sugerido do estagio (o primeiro rival do primeiro lugar do estagio na campanha dos pets v13, com a regra da arena; a Cidadela
     conta cada luta da serie) e aprende com cada uma (GambitsPet.aprender). P-4: a fracao dos pets com a taxa >= CLE.limiarTaxa nessas
     lutas. P-3: depois delas, a lista aprendida contra a lista de partida, os dois com o mesmo perfil (no limite, a fracao de vida).
   O pet da bancada nao e uma vida: sem dono, sem cuidado, sem a disciplina e a experiencia no epsilon (o epsilon do bot, CV.eps).
   As sementes: a faixa reservada (68101 a 68505 na calibracao), as 5 bases x 20 (hashSemente("equilibrio-tr", base, k)). P-1: 10 sementes
   por confronto de formas e especies, os dois lados; P-2, P-3 e P-4: 100 por forma.
   --escala '{"vida":{"adolescente":700},"beta":.05}': a escala candidata, por cima da CESC_V9; --parte p1|p2|p34: so uma parte.
   uso (em web/app): npx tsx scripts/equilibrio_tr/fase3_estagio.ts --faixa calibracao [--escala JSON] [--parte p1] --saida <arquivo.json> */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { execSync } from "node:child_process";
import {
  ADOL_V21, CAT, CESC_V9, CIT, CLE, CRIANCA_V21, CV, CV21E_TR, ESPECIES, FORMAS_AD, GambitsPet, LINHAS, LINHA_DA_FORMA, LISTAS_V14, LUGARES_V6,
  RELOGIO_V14, STATS, arenaDaLuta, caraterCanonico, copiarGambits, gambitsAdulto, hashSemente, jogarSerie, jogarTR, lutadorBot, perfilDe,
  type Estagio, type Forma, type ListaGambits, type Lutador, type RegrasLuta,
} from "../../motor/index.ts";
import { ligarEscala } from "../../motor/catalogo.ts";

const arg = (k: string): string | null => { const i = process.argv.indexOf("--" + k); return i < 0 ? null : process.argv[i + 1] ?? null; };
const FAIXAS: Record<string, number> = { calibracao: 68101, conferencia: 70101 };
const faixa = arg("faixa"), saida = arg("saida"), parte = arg("parte");
if (!faixa || !(faixa in FAIXAS)) throw new Error("--faixa calibracao | conferencia");
if (!saida) throw new Error("--saida <arquivo.json>");
if (parte !== null && !["p1", "p2", "p34"].includes(parte)) throw new Error("--parte p1 | p2 | p34");
const R: RegrasLuta = { ...CV21E_TR, relogio: RELOGIO_V14 }, VERSAO = R.versaoPet;
ligarEscala(true);
/* a escala: a dos pets v13 (CESC_V9) ou a candidata por cima */
const escArg = JSON.parse(arg("escala") ?? "{}") as { vida?: Partial<Record<Estagio, number>>; beta?: number };
for (const k of Object.keys(escArg)) if (k !== "vida" && k !== "beta") throw new Error("escala: so vida e beta");
const ESC = { vida: { ...CESC_V9.vida, ...escArg.vida }, beta: escArg.beta ?? CESC_V9.beta };
const E = (est: Estagio, pontos: number): number => ESC.vida[est] * (1 + ESC.beta * pontos);
const SEMENTES_POR_BASE = 20;
const bases = [0, 1, 2, 3, 4].map(i => FAIXAS[faixa] + 101 * i);
const sementes = bases.flatMap(b => Array.from({ length: SEMENTES_POR_BASE }, (_, k) => hashSemente("equilibrio-tr", b, k)));
const r4 = (x: number): number => Math.round(x * 10000) / 10000;
const media = (xs: number[]): number => xs.reduce((a, b) => a + b, 0) / xs.length;
const TIPICO = CIT.tipico as Record<string, number>;

/** a forma de referencia: o id (a chave da lista candidata), a forma por especie, o carater e a lista de partida */
interface Ref { id: string; forma: (esp: Forma["esp"]) => Forma; car: Record<string, number> | null; lista: ListaGambits }
const listaDe = (id: string, hoje: ListaGambits): ListaGambits => LISTAS_V14[id] ?? hoje;
function formasDe(est: Estagio): Ref[] {
  if (est === "crianca") return (["sereno", "arisco"] as const).map(r => ({ id: r, forma: esp => ({ esp, est, ramo: r }), car: null, lista: listaDe(r, CRIANCA_V21[r]) }));
  if (est === "adolescente") return LINHAS.map(l => ({ id: l, forma: esp => ({ esp, est, ramo: "sereno", linha: l }),
    car: caraterCanonico(FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l)!), lista: listaDe(l, ADOL_V21[l]) }));
  return FORMAS_AD.map(f => ({ id: f, forma: esp => ({ esp, est, ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f }), car: caraterCanonico(f),
    lista: listaDe(f, gambitsAdulto(f, R)) }));
}
/** o perfil do pet: o treino uniforme de `pontos`, absoluto, na escala (a candidata por cima da do motor) */
function perfil(ref: Ref, esp: Forma["esp"], pontos: number) {
  const tr = pontos ? Object.fromEntries(STATS.map(k => [k, pontos / STATS.length])) : null, f = ref.forma(esp);
  return { ...perfilDe(f, ref.car, 1, tr as never, true, VERSAO), escala: E(f.est, pontos) };
}
const pet = (ref: Ref, esp: Forma["esp"], pontos: number, lista: ListaGambits = ref.lista): Lutador =>
  ({ nome: `${ref.id}+${pontos}@${esp}`, estilo: { nome: ref.id, gambits: copiarGambits(lista), eps: CV.eps }, cond: perfil(ref, esp, pontos) });

const t0 = performance.now();
const out: Record<string, unknown> = {
  gerado_por: "web/app/scripts/equilibrio_tr/fase3_estagio.ts", data: new Date().toISOString().slice(0, 10),
  commit: execSync("git rev-parse --short HEAD").toString().trim(), node: process.version,
  faixa, bases, sementes_por_base: SEMENTES_POR_BASE, relogio: R.relogio, listas: "v14", escala: ESC, parte, metas: {},
};
const metas = out.metas as Record<string, unknown>;

/* P-1: o estagio */
if (!parte || parte === "p1") {
  const sP1 = bases.flatMap(b => [0, 1].map(k => hashSemente("equilibrio-tr", b, k)));   /* 10 sementes por confronto */
  const par = (baixo: Estagio, alto: Estagio) => {
    let pontos = 0, vit = 0, n = 0;
    const por: Record<string, number> = {};
    for (const fb of formasDe(baixo)) for (const fa of formasDe(alto)) for (const eb of ESPECIES) for (const ea of ESPECIES) {
      const A = pet(fb, eb, TIPICO[baixo]), B = pet(fa, ea, 0);
      for (const s of sP1) for (const lado of [0, 1]) {
        /* o limite fica com o de cima (o desafiado) */
        const p = lado === 0 ? jogarTR(A, B, s, { R, desafiado: 1 }).pontosA : 1 - jogarTR(B, A, s, { R, desafiado: 0 }).pontosA;
        pontos += p; n++;
        if (p === 1) { vit++; por[`${fb.id} x ${fa.id}`] = (por[`${fb.id} x ${fa.id}`] ?? 0) + 1; }
      }
    }
    return { pontos: r4(pontos / n), vitorias: r4(vit / n), lutas: n, razao_E: r4(E(baixo, TIPICO[baixo]) / E(alto, 0)), vitorias_por_par: por };
  };
  const viz = { rookie_champion: par("crianca", "adolescente"), champion_ultimate: par("adolescente", "adulto"), ultimate_mega: par("adulto", "mega") };
  const dois = { rookie_ultimate: par("crianca", "adulto"), champion_mega: par("adolescente", "mega") };
  metas["P-1"] = { vizinhos: viz, dois_estagios: dois,
    passa: Object.values(viz).every(x => x.pontos <= .1) && Object.values(dois).every(x => x.vitorias === 0) };
}

/* P-2: um nivel de treino no mesmo estagio */
if (!parte || parte === "p2") {
  const porEst: Record<string, { media: number; pior: string; pior_taxa: number; formas: Record<string, number> }> = {};
  for (const est of ["crianca", "adolescente", "adulto", "mega"] as Estagio[]) {
    const formas: Record<string, number> = {};
    for (const ref of formasDe(est)) {
      let p = 0, n = 0;
      sementes.forEach((s, k) => {
        const esp = ESPECIES[k % ESPECIES.length], A = pet(ref, esp, TIPICO[est]), B = pet(ref, esp, 0);
        p += jogarTR(A, B, s, { R }).pontosA + 1 - jogarTR(B, A, s, { R }).pontosA; n += 2;
      });
      formas[ref.id] = r4(p / n);
    }
    const pior = Object.entries(formas).sort((a, b) => a[1] - b[1])[0];
    porEst[est] = { media: r4(media(Object.values(formas))), pior: pior[0], pior_taxa: pior[1], formas };
  }
  metas["P-2"] = { por_estagio: porEst, passa: Object.values(porEst).every(x => x.pior_taxa >= .8) };
}

/* P-3 e P-4: o aprendizado nas lutas contra o rival sugerido do estagio */
if (!parte || parte === "p34") {
  const rivalDe = (est: Estagio): string => LUGARES_V6.find(L => L.est === est)!.rivais[0];
  const p3: Record<string, unknown> = {}, p4: Record<string, unknown> = {};
  for (const est of ["adolescente", "adulto"] as Estagio[]) {
    const rival = rivalDe(est), arena = arenaDaLuta(rival, VERSAO), B0 = lutadorBot(rival, R, arena), lutasSerie = arena?.lutas ?? 1;
    /* o rival na escala candidata: a vida do estagio dele troca na mesma proporcao (o fator fica) */
    const B: Lutador = { ...B0, cond: { ...B0.cond, escala: B0.cond.escala! * ESC.vida[B0.cond.est] / CESC_V9.vida[B0.cond.est] } };
    const formasP3: Record<string, number> = {}, formasP4: Record<string, number> = {}, taxas: number[] = [], trocas: Record<string, number> = {};
    for (const ref of formasDe(est)) {
      let p = 0, n = 0, qual = 0;
      sementes.forEach((s, k) => {
        const esp = ESPECIES[k % ESPECIES.length], gp = new GambitsPet();
        gp.chipsNoFim = true; gp.semear(ref.forma(esp), ref.id, R, ref.lista);
        const cond = perfil(ref, esp, TIPICO[est]);
        let lutas = 0, vit = 0, ev = 0;
        while (lutas < CAT.sparring) {
          const se = hashSemente("equilibrio-tr-sparring", s, ev++), usadas = gp.ativas.slice();
          const A: Lutador = { nome: "pet", estilo: gp.estilo(), cond };
          const serie = jogarSerie(A, Array.from({ length: lutasSerie }, () => B), se, R, 1, null);
          for (let j = 0; j < serie.length && lutas < CAT.sparring; j++) {
            gp.aprender(serie[j], hashSemente("equilibrio-tr-aprender", se, j), usadas);
            lutas++; if (serie[j].pontosA === 1) vit++;
          }
        }
        taxas.push(vit / lutas);
        /* diagnostico: as trocas de regra (a regra de partida que saiu da lista) */
        trocas[ref.id] = (trocas[ref.id] ?? 0) + gp.mudancas.filter(x => x.texto.startsWith("trocou")).length / sementes.length;
        if (vit / lutas >= CLE.limiarTaxa) qual++;
        /* P-3: a lista aprendida contra a de partida, o mesmo perfil, numa semente nova */
        const Ap: Lutador = { nome: "aprendida", estilo: gp.estilo(), cond }, As: Lutador = { nome: "semente", estilo: { nome: "semente", gambits: copiarGambits(ref.lista), eps: CV.eps }, cond };
        const sl = hashSemente("equilibrio-tr-p3", s);
        p += jogarTR(Ap, As, sl, { R }).pontosA + 1 - jogarTR(As, Ap, sl, { R }).pontosA; n += 2;
      });
      formasP3[ref.id] = r4(p / n); formasP4[ref.id] = r4(qual / sementes.length);
    }
    const nome = est === "adolescente" ? "champion" : "ultimate";
    p3[nome] = { media: r4(media(Object.values(formasP3))), formas: formasP3,
      trocas_por_pet: Object.fromEntries(Object.entries(trocas).map(([k, v]) => [k, r4(v)])) };
    p4[nome] = { rival, lutas_por_serie: lutasSerie, qualificados: r4(media(Object.values(formasP4))), taxa_media: r4(media(taxas)), formas: formasP4 };
  }
  metas["P-3"] = { ...p3, passa: Object.values(p3).every(x => (x as { media: number }).media >= .55 && (x as { media: number }).media <= .7) };
  metas["P-4"] = { ...p4, passa: Object.values(p4).every(x => (x as { qualificados: number }).qualificados >= .8) };
}
out.custo_s = r4((performance.now() - t0) / 1000);
mkdirSync(dirname(saida), { recursive: true });
writeFileSync(saida, JSON.stringify(out, null, 1) + "\n");
console.log(JSON.stringify(metas, (k, v) => k === "vitorias_por_par" ? undefined : v, 1));
