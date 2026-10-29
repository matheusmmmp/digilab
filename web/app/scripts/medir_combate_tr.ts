/* A duracao e o custo por luta da luta em tempo real (docs/ESPEC_COMBATE_TR.md; COMBATE-TR, etapa R1), no Node do engines (24, que roda
   TypeScript sem dependencia nova). As lutas: as 8 formas adultas da V21E umas contra as outras e os 6 bots classicos com lista (o oraculo
   nao luta em tempo real, D-6) contra elas, cada par com as sementes abaixo. Grava scripts/medicoes/combate_tr.json.
     node scripts/medir_combate_tr.ts
   Nao calibra nada: so mede (o equilibrio fica para a rodada do fim). A comparacao com o combate por turnos usa o jogarV2 de hoje nos
   mesmos pares e sementes. */
import { writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import os from "node:os";
import {
  CTR_TR, CV21E, FORMAS_AD, PASSO_TR_MS, jogarTR, jogarV2, lutadorBot, type Lutador,
} from "../motor/index.ts";

const SEMENTES = [101, 202, 303, 404, 505];
const CLASSICOS = ["aleatorio", "agressivo", "tartaruga", "atirador", "contragolpe", "adaptativo"];
const pares: [string, Lutador, Lutador][] = [];
for (const a of FORMAS_AD) for (const b of FORMAS_AD) pares.push([`${a}x${b}`, lutadorBot(a, CV21E), lutadorBot(b, CV21E)]);
for (const a of CLASSICOS) for (const b of FORMAS_AD) pares.push([`${a}x${b}`, lutadorBot(a, CV21E), lutadorBot(b, CV21E)]);

const quantil = (xs: number[], q: number) => { const s = [...xs].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(q * s.length))]; };
const media = (xs: number[]) => xs.reduce((s, x) => s + x, 0) / xs.length;
const mediana = (xs: number[]) => quantil(xs, .5);

function rodada() {
  const passos: number[] = [], acoes: number[] = [];
  let ko = 0, limite = 0, vA = 0, emp = 0;
  for (const [, A, B] of pares) for (const s of SEMENTES) {
    const r = jogarTR(A, B, s, { R: CV21E });
    passos.push(r.passos); acoes.push(r.acoes.length);
    if (r.fim === "ko") ko++; else limite++;
    if (r.pontosA === 1) vA++; else if (r.pontosA === .5) emp++;
  }
  return { passos, acoes, ko, limite, vA, emp };
}
/* aquecimento, depois 5 repeticoes medidas */
rodada();
const tempos: number[] = []; let res = rodada();
for (let k = 0; k < 5; k++) { const t0 = performance.now(); res = rodada(); tempos.push(performance.now() - t0); }
const n = res.passos.length, msLuta = mediana(tempos) / n;

/* a linha de base: o combate por turnos de hoje nos mesmos pares e sementes */
const turnos = () => { let tt = 0; for (const [, A, B] of pares) for (const s of SEMENTES) tt += jogarV2(A, B, s, CV21E).turnos.length; return tt; };
turnos();
const tv: number[] = []; let nt = 0;
for (let k = 0; k < 5; k++) { const t0 = performance.now(); nt = turnos(); tv.push(performance.now() - t0); }

const seg = (p: number) => +(p * PASSO_TR_MS / 1000).toFixed(1);
const saida = {
  gerado_por: "web/app/scripts/medir_combate_tr.ts", data: new Date().toISOString().slice(0, 10), node: process.version,
  maquina: { cpu: os.cpus()[0]?.model ?? "?", nucleos: os.cpus().length, plataforma: `${os.platform()} ${os.release()}` },
  lutas: n, pares: pares.length, sementes: SEMENTES, limite_s: seg(CTR_TR.limite), morte_subita_s: seg(CTR_TR.morteSubita),
  duracao_s: { media: seg(media(res.passos)), mediana: seg(mediana(res.passos)), p90: seg(quantil(res.passos, .9)), max: seg(Math.max(...res.passos)) },
  acoes_por_luta: +media(res.acoes).toFixed(1),
  fim: { ko: res.ko, limite: res.limite }, resultado: { vitorias_a: res.vA, empates: res.emp, derrotas_a: n - res.vA - res.emp },
  custo: {
    ms_por_luta: +msLuta.toFixed(3), us_por_passo: +(1000 * mediana(tempos) / res.passos.reduce((s, x) => s + x, 0)).toFixed(3),
    ms_por_luta_repeticoes: tempos.map(x => +(x / n).toFixed(3)),
    refazer_lutas_s: Object.fromEntries([100, 500, 1000].map(k => [k, +(k * msLuta / 1000).toFixed(2)])),
    luta_no_limite_ms: +(CTR_TR.limite * mediana(tempos) / res.passos.reduce((s, x) => s + x, 0)).toFixed(3),
  },
  turnos_hoje: { turnos_por_luta: +(nt / n).toFixed(1), ms_por_luta: +(mediana(tv) / n).toFixed(4) },
};
const DESTINO = fileURLToPath(new URL("./medicoes/", import.meta.url));
mkdirSync(DESTINO, { recursive: true });
writeFileSync(DESTINO + "combate_tr.json", JSON.stringify(saida, null, 1) + "\n");
console.log(JSON.stringify(saida, null, 1));
