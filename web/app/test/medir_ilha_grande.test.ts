/* A medida da IG5 (docs/TAREFA_V3_ILHA_AGUA.md, secao 12.13, o plano escrito antes de rodar): como o pet do jogo se sai na ilha grande
   (a v24, 128 x 60) contra a ilha com agua de 64 x 30 (a v23), com o DigiBrain modular e com o cerebro A. E o Motor do jogo, com as
   chaves do produto; so as sementes dos testes. Descritiva: sem hipotese e sem gate.

   Nao e teste: so roda com MEDIR_IG5=1, e grava docs/pranchas/ilha-grande/medida_ig5.json.
       MEDIR_IG5=1 npx vitest run test/medir_ilha_grande.test.ts
   Sem a variavel, um teste so confere que o artefato gravado tem a forma que a tarefa cita. */
import { describe, expect, test } from "vitest";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { TPD } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import { celulasSecas } from "../motor/mundo.ts";
import { ligarProduto } from "../src/produto.ts";
import { lugaresNomeados } from "../src/telas/pet/vistaMundo.ts";

const ARQUIVO = new URL("../../../docs/pranchas/ilha-grande/medida_ig5.json", import.meta.url);
const SEMENTES = [101, 202, 303, 404, 505], DIAS = 5, PASSO = 30, PRAZO = 240, FOME_BAIXA = 0.2, FOME_DO_DONO = 0.6;
const MUNDOS = [["hoje_64x30", 23], ["grande_128x60", 24]] as const;
const CEREBROS = ["modular", "a"] as const;
const CENARIOS = ["comedouro", "perto", "longe"] as const;
const RETORNOS: Record<string, number[]> = { hoje_64x30: [20, 40], grande_128x60: [20, 40, 70] };
const PERTO_DO_COMEDOURO = 3;         // celulas

/* o adendo da 12.15 (exploratorio): a racao a 6 celulas a leste do ninho, so na ilha grande, onde o comedouro fica a 8 */
type Cenario = (typeof CENARIOS)[number] | "comedouro6";
const media = (v: number[]): number | null => v.length ? Math.round((v.reduce((a, b) => a + b, 0) / v.length) * 1000) / 1000 : null;
const mediana = (v: number[]): number | null => { const o = [...v].sort((a, b) => a - b); return o.length ? o[Math.floor(o.length / 2)] : null; };

function pet(semente: number, versao: number, cerebro: "modular" | "a"): Motor {
  const m = ligarProduto(new Motor(semente, versao));
  if (m.cerebroAtual !== cerebro) m.trocarCerebro(cerebro);
  return m;
}
/** um passo do dono: a racao no lugar do cenario quando o pet tem fome e nao ha comida no chao; a limpeza e o carinho */
function cuidar(m: Motor, p: number, cenario: Cenario | null): boolean {
  const e = m.e, mu = m.mundo!;
  let pos = false;
  if (cenario !== null && !e.dormindo && e.fome < FOME_DO_DONO && mu.comidas.size === 0) {
    const [x, y] = cenario === "comedouro6" ? [(mu.cm.layout.ninho[0] + 6) * mu.cm.sub + mu.cm.sub / 2, mu.cm.layout.ninho[1] * mu.cm.sub + mu.cm.sub / 2]
      : lugaresNomeados(mu)[cenario];
    m.deixarComida("racao", x, y);
    pos = true;
  }
  if (e.sujeira >= 2) m.observar("limpar");
  if (p % 5 === 0) m.observar("acariciar");
  return pos;
}

function vida(semente: number, versao: number, cerebro: "modular" | "a", cenario: Cenario): Record<string, number | null> {
  const m = pet(semente, versao, cerebro), passos = Math.round(DIAS * TPD / PASSO);
  let postas = 0, fomeBaixa = 0, somaFome = 0;
  const t0 = performance.now();
  for (let p = 0; p < passos; p++) {
    m.avancar(PASSO);
    if (cuidar(m, p, cenario)) postas++;
    somaFome += m.e.fome;
    if (m.e.fome < FOME_BAIXA) fomeBaixa++;
  }
  const ms = performance.now() - t0, mu = m.mundo!, sub = mu.cm.sub;
  const doDono = mu.consumos.filter(c => c.origem === "dono"), tempos = doDono.map(c => (c.tick as number) - (c.tick_posta as number));
  let andou = 0;
  const celulas = new Set<number>();
  for (const d of mu.contratoDecisoes) {
    const tr = d.trajetoria ?? [];
    for (let k = 0; k < tr.length; k++) {
      celulas.add(Math.floor(tr[k][1] / sub) * mu.cm.celulas_x + Math.floor(tr[k][0] / sub));
      if (k > 0) andou += Math.hypot(tr[k][0] - tr[k - 1][0], tr[k][1] - tr[k - 1][1]);
    }
  }
  const livres = celulasSecas(mu.cm)!.filter(Boolean).length;
  return {
    postas, comidas: doDono.length, fracao_no_prazo: postas ? Math.round((tempos.filter(t => t <= PRAZO).length / postas) * 1000) / 1000 : null,
    mediana_ticks: mediana(tempos), fracao_fome_baixa: Math.round((fomeBaixa / passos) * 1000) / 1000, fome_media: Math.round((somaFome / passos) * 1000) / 1000,
    celulas_andadas_por_dia: Math.round(andou / sub / DIAS), cobertura: Math.round((celulas.size / livres) * 1000) / 1000,
    ms_por_dia: Math.round(ms / DIAS),
  };
}

/** o retorno: dois dias comendo no comedouro; depois o dono solta o pet com fome a `d` celulas a leste do comedouro, sem comida no
    chao, e o tempo anda um dia. Devolve a menor distancia ao comedouro (celulas) e se chegou perto */
function retorno(semente: number, versao: number, cerebro: "modular" | "a", d: number): { solto: boolean; menor: number | null; voltou: boolean; ticks: number | null } {
  const m = pet(semente, versao, cerebro), treino = Math.round(2 * TPD / PASSO);
  for (let p = 0; p < treino; p++) { m.avancar(PASSO); cuidar(m, p, "comedouro"); }
  let p = treino;
  for (; p < treino + Math.round(TPD / PASSO); p++) {          // espera o pet acordado, com fome e sem comida no chao (ate um dia)
    if (!m.e.dormindo && m.e.fome < FOME_DO_DONO && m.mundo!.comidas.size === 0) break;
    m.avancar(PASSO); cuidar(m, p, null);
  }
  const mu = m.mundo!, sub = mu.cm.sub, [cx, cy] = mu.comedouro;
  if (m.e.dormindo || mu.comidas.size !== 0) return { solto: false, menor: null, voltou: false, ticks: null };
  m.levarPet(cx + d * sub, cy);
  const partida = Math.hypot(mu.pet[0] - cx, mu.pet[1] - cy) / sub;
  let menor = partida, ticks: number | null = null;
  for (let k = 0; k < Math.round(TPD / 15); k++) {
    m.avancar(15);
    const dist = Math.hypot(mu.pet[0] - cx, mu.pet[1] - cy) / sub;
    if (dist < menor) menor = dist;
    if (ticks === null && dist <= PERTO_DO_COMEDOURO) ticks = (k + 1) * 15;
    if (m.e.sujeira >= 2) m.observar("limpar");
  }
  return { solto: true, menor: Math.round(menor * 10) / 10, voltou: ticks !== null, ticks };
}

function medir(): Record<string, unknown> {
  const cenarios: Record<string, unknown> = {}, retornos: Record<string, unknown> = {};
  for (const [mundo, versao] of MUNDOS) for (const cerebro of CEREBROS) {
    for (const cenario of CENARIOS) {
      const vidas = SEMENTES.map(s => vida(s, versao, cerebro, cenario)), chaves = Object.keys(vidas[0]);
      cenarios[`${mundo}|${cerebro}|${cenario}`] = {
        media: Object.fromEntries(chaves.map(k => [k, media(vidas.map(v => v[k]).filter((x): x is number => x !== null))])), vidas,
      };
    }
    for (const d of RETORNOS[mundo]) {
      const r = SEMENTES.map(s => retorno(s, versao, cerebro, d)), soltos = r.filter(x => x.solto);
      retornos[`${mundo}|${cerebro}|${d}`] = {
        soltos: soltos.length, voltaram: soltos.filter(x => x.voltou).length, menor_media: media(soltos.map(x => x.menor!)),
        mediana_ticks: mediana(soltos.filter(x => x.voltou).map(x => x.ticks!)), vidas: r,
      };
    }
  }
  return { sementes: SEMENTES, dias: DIAS, passo: PASSO, prazo: PRAZO, fome_baixa: FOME_BAIXA, fome_do_dono: FOME_DO_DONO,
           perto_do_comedouro: PERTO_DO_COMEDOURO, mundos: Object.fromEntries(MUNDOS), cenarios, retornos };
}

/** o adendo: so o cenario `comedouro6`, na ilha grande, com os dois cerebros; entra no mesmo artefato, na chave `adendo_comedouro6` */
function medirAdendo(): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const cerebro of CEREBROS) {
    const vidas = SEMENTES.map(s => vida(s, 24, cerebro, "comedouro6")), chaves = Object.keys(vidas[0]);
    out[`grande_128x60|${cerebro}|comedouro6`] = { media: Object.fromEntries(chaves.map(k => [k, media(vidas.map(v => v[k]).filter((x): x is number => x !== null))])), vidas };
  }
  return out;
}

describe("a medida da IG5", () => {
  test.skipIf(process.env.MEDIR_IG5_ADENDO !== "1")("roda o adendo do comedouro a 6 celulas e o acrescenta ao artefato", () => {
    const g = JSON.parse(readFileSync(ARQUIVO, "utf8")) as Record<string, unknown>;
    g.adendo_comedouro6 = medirAdendo();
    writeFileSync(ARQUIVO, JSON.stringify(g, null, 1) + "
", "utf8");
  }, 3_600_000);

  test.skipIf(process.env.MEDIR_IG5 !== "1")("roda a medida e grava o artefato", () => {
    const g = medir();
    writeFileSync(ARQUIVO, JSON.stringify(g, null, 1) + "\n", "utf8");
  }, 3_600_000);

  test.skipIf(!existsSync(ARQUIVO))("o artefato gravado tem os dois mundos, os dois cerebros, os tres cenarios e os retornos", () => {
    const g = JSON.parse(readFileSync(ARQUIVO, "utf8")) as { sementes: number[]; cenarios: Record<string, { media: Record<string, number | null>; vidas: unknown[] }>; retornos: Record<string, { soltos: number }> };
    expect(g.sementes).toEqual(SEMENTES);
    expect(Object.keys(g.cenarios).sort()).toEqual(MUNDOS.flatMap(([m]) => CEREBROS.flatMap(c => CENARIOS.map(k => `${m}|${c}|${k}`))).sort());
    for (const c of Object.values(g.cenarios)) { expect(c.vidas.length).toBe(SEMENTES.length); expect(c.media.postas).not.toBeNull(); }
    expect(Object.keys(g.retornos).sort()).toEqual(MUNDOS.flatMap(([m]) => CEREBROS.flatMap(c => RETORNOS[m].map(d => `${m}|${c}|${d}`))).sort());
  });
});
