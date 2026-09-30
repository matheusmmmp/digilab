// Exploracao da lista do Guardromon na luta de arena da Torre de pedra (escala dos pets v6), SO nas sementes de calibracao (as
// de validacao ficam para test/calibrar_arenas.mjs --validar). Com a lista de antes (a do espelho com o contra-golpe) nenhum
// fator de 0,5 a 4,0 deixa o Champion sem treino abaixo de 0,05: o cacador vence sem treino (0,985 com o fator 1,8 e ainda
// 0,415 com 4,0), porque o lider responde ao disparo frequente com o contra-golpe, que nao devolve disparo (so a passiva do
// espelho devolveria, e o NPC nao tem passiva): ele fica parado defendendo e o cacador atira de longe.
// A ideia da arena fica (paciencia: o contra-golpe contra quem prepara o pesado, insiste no golpe rapido ou na investida); as
// variantes mudam so a resposta a quem atira de longe (no maximo 8 regras, o teto da linguagem). Mesmo metodo de calibrar_arenas.mjs (o pet e o lado A; as 4 linhas do
// Champion com a lista do adolescente e o carater canonico, 4 especies, sem treino e com 22; metas sem treino <= 0,05, com o
// treino tipico >= 0,80, nenhuma forma < 0,5; fatores 0,5..4,0). Escolha: a variante com a maior folga; empate: a mais perto
// da lista de antes (a ordem abaixo). Saida: artifacts_campanha/arenas/torre_variantes.json.
// uso (em web/app): node test/explorar_torre.mjs
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ADOL_V21, ARENAS, CV, CV21D, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, STATS, Cd, Rg } = M;
const R = CV21D; M.ligarEscala(true);
const SEM = [3101, 3202, 3303, 3404, 3505], n = 10;
const META_SEM = 0.05, META_COM = 0.80, META_FORMA = 0.5, TIPICO = 22;
const FATORES = Array.from({ length: 36 }, (_, i) => Math.round((0.5 + 0.1 * i) * 10) / 10);
const PREP = Cd("oponente_preparando"), D0 = Cd("distancia_eh", 0), D1 = Cd("distancia_eh", 1), D2 = Cd("distancia_eh", 2);
const GA = g => Cd("guts_proprio_acima", g), GB = g => Cd("guts_proprio_abaixo", g), FQ = a => Cd("oponente_frequente", a);
const CG = "contra_golpe";
/* o nucleo da paciencia (as regras de contra-golpe corpo a corpo e o resto da lista do espelho) */
const CORPO = [Rg(FQ("golpe_rapido"), CG), Rg(FQ("investida"), CG)];
const RESTO = [Rg([D0, Cd("oponente_repete", "defender", 2)], "preparar_pesado"), Rg([D0, GA(60)], "golpe_rapido"), Rg(GB(40), "carregar"), Rg(D2, "avancar")];
const VARIANTES = {
  /* a de antes: o espelho com o contra-golpe (gambitNPC("v21:espelho", R, "contra_golpe")) */
  t0_antes: [Rg(PREP, CG), Rg(FQ("disparo"), CG), ...CORPO, ...RESTO],
  /* quem atira com frequencia: ele vai buscar (a resposta da muralha canonica) */
  t1_avanca_no_disparo: [Rg(PREP, CG), Rg(FQ("disparo"), "avancar"), ...CORPO, ...RESTO],
  /* t1 com a busca depois das regras do contra-golpe */
  t2_avanca_depois: [Rg(PREP, CG), ...CORPO, Rg(FQ("disparo"), "avancar"), ...RESTO],
  /* sem a regra do disparo: ele sempre encurta (D2 e D1 -> avancar) */
  t3_sempre_encurta: [Rg(PREP, CG), ...CORPO, ...RESTO, Rg(D1, "avancar")],
};
const arena = ARENAS.find(a => a.id === "torre");
const primeiraForma = l => FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l);
const pet = (l, e, nivel) => ({ nome: `${l}+${nivel}@${e}`, estilo: { nome: l, gambits: M.copiarGambits(ADOL_V21[l]), eps: CV.eps },
  cond: M.perfilDe({ esp: e, est: "adolescente", ramo: "sereno", linha: l }, M.caraterCanonico(primeiraForma(l)), 1,
    nivel ? Object.fromEntries(STATS.map(k => [k, nivel / STATS.length])) : null, true, M.VERSAO_ESCALA_V6) });
function medir(regras, fator) {
  const B0 = M.lutadorBot(arena.lider, R, { ...arena, fator }), B = { ...B0, estilo: { ...B0.estilo, gambits: { regras, final: "defender" } } };
  const por = {};
  for (const l of LINHAS) por[l] = [0, TIPICO].map(nv => {
    let s = 0, t = 0;
    for (const e of ESPECIES) { const A = pet(l, e, nv); for (const se of SEM) for (let k = 0; k < n; k++) { s += M.jogarV2(A, B, M.hashSemente("calib-arena", se, A.nome, B.nome, k), R).pontosA; t++; } }
    return s / t;
  });
  const sem = LINHAS.reduce((a, l) => a + por[l][0], 0) / LINHAS.length, com = LINHAS.reduce((a, l) => a + por[l][1], 0) / LINHAS.length;
  const pior = Math.min(...LINHAS.map(l => por[l][1]));
  return { fator, sem: +sem.toFixed(4), com: +com.toFixed(4), pior: +pior.toFixed(4), pior_forma: LINHAS.find(l => por[l][1] === pior),
    passa: sem <= META_SEM && com >= META_COM && pior >= META_FORMA, folga: +Math.min(META_SEM - sem, com - META_COM, pior - META_FORMA).toFixed(4),
    por_forma: Object.fromEntries(LINHAS.map(l => [l, { sem: +por[l][0].toFixed(4), com: +por[l][1].toFixed(4) }])) };
}
const saida = {};
for (const [nome, regras] of Object.entries(VARIANTES)) {
  M.validarLista({ regras, final: "defender" });
  const med = FATORES.map(f => medir(regras, f)), pool = med.some(m => m.passa) ? med.filter(m => m.passa) : med;
  const melhor = pool.reduce((x, y) => y.folga > x.folga ? y : x);
  saida[nome] = { regras: regras.map(r => JSON.stringify(r)), melhor, passa: melhor.passa };
  console.log(nome, JSON.stringify({ fator: melhor.fator, sem: melhor.sem, com: melhor.com, pior: melhor.pior, pior_forma: melhor.pior_forma, passa: melhor.passa, folga: melhor.folga }));
}
const escolhida = Object.entries(saida).filter(([, v]) => v.passa).reduce((x, y) => !x || y[1].melhor.folga > x[1].melhor.folga ? y : x, null);
console.log("escolhida:", escolhida ? escolhida[0] : "nenhuma passa");
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/arenas/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + "torre_variantes.json", JSON.stringify({ descricao: "variantes da lista do Guardromon na arena da Torre (escala dos pets v6), sementes de calibracao",
  sementes: SEM, n_por_semente: n, metas: { sem_treino_max: META_SEM, com_treino_min: META_COM, pior_forma_min: META_FORMA }, treino_tipico: TIPICO,
  final: "defender", variantes: saida, escolhida: escolhida ? escolhida[0] : null }, null, 1) + "\n");
