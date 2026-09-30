// Conferencia da Liga dos Lideres (docs/DESIGN_FRONTEIRA.md, secao 2; medalhas parte 4a). SEM calibracao (decisao do Matheus: sem
// rodada de equilibrio nesta parte): so confere que o jogo e completavel, ou seja, que um Mega bem treinado, com a forma certa para cada
// confronto, vence cada luta da Liga. Nenhum numero do jogo sai daqui.
//
// Metodo (o dos lideres da parte 2, test/itens_ref.mjs): motor web, escala dos pets v6 ligada, regras V21D, a regra do limite do
// desafiado (o lider); o pet de referencia = cada uma das 8 formas no Mega, nas 4 especies, com o treino tipico do Mega (40, uniforme),
// sem chip e sem carta, como lado A. Os rivais = os Megas da Liga (motor/liga.ts), com o fator do Piedmon da Espiral.
// - por luta: o pet inteiro contra cada lider (a taxa de vitoria por forma, media das especies);
// - a Liga inteira: as 6 lutas seguidas, sem cura (arenas.jogarSerie, como o motor joga), a taxa de titulos por forma.
// Sementes de validacao da parte 2 (4101...4505), N partidas por semente, especie e forma. Dois fatores dos rivais: o do desenho (o do
// Piedmon na arena da Espiral) e o adotado (motor/liga.ts, FATOR_LIGA); mais dois no meio, so como relato.
// uso (em web/app): npx tsx test/conferir_liga.mjs  ->  artifacts_campanha/liga/conferencia.json
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";
import { R, formasDe, lutador } from "./itens_ref.mjs";

const { CIT, ESPECIES, LIGA, NPC, FATOR_LIGA, FATOR_LIGA_DESENHO } = M;
M.ligarEscala(true);
const SEMENTES = [4101, 4202, 4303, 4404, 4505], N = 20, TIPICO = CIT.tipico.mega;
const formas = formasDe("mega");
const r4 = x => +x.toFixed(4);
const FATORES = [...new Set([FATOR_LIGA_DESENHO, 1.4, 1.2, FATOR_LIGA])];
function conferir(fator) {
const lideres = M.lutadoresLiga(R, fator);

/* por luta: o pet inteiro contra cada lider */
const porLuta = LIGA.map((x, i) => {
  const porForma = {};
  for (const fo of formas) {
    let v = 0, tot = 0;
    for (const e of ESPECIES) {
      const A = lutador(fo, e, TIPICO, [], true);
      for (const s of SEMENTES) for (let k = 0; k < N; k++) {
        v += M.jogarV2(A, lideres[i], M.hashSemente("conferir-liga", s, A.nome, i, k), R, null, 1).pontosA === 1 ? 1 : 0; tot++;
      }
    }
    porForma[fo[0]] = r4(v / tot);
  }
  const melhor = Object.entries(porForma).sort((a, b) => b[1] - a[1])[0];
  return { luta: i + 1, lider: NPC[x.lider].nome, mega: M.nomeMegaLiga(i), arquetipo: M.NOME_ARQ[x.adulta], especie: M.NOME_ESP[x.esp],
    melhor_forma: melhor[0], melhor_taxa: melhor[1], por_forma: porForma };
});
/* a Liga inteira: as 6 lutas seguidas, sem cura */
const liga = {};
for (const fo of formas) {
  let titulos = 0, tot = 0;
  const chegou = Array(LIGA.length).fill(0);
  for (const e of ESPECIES) {
    const A = lutador(fo, e, TIPICO, [], true);
    for (const s of SEMENTES) for (let k = 0; k < N; k++) {
      const serie = M.jogarSerie(A, lideres, M.hashSemente("conferir-liga-serie", s, A.nome, k), R, 1, null);
      serie.forEach((_, j) => chegou[j]++);
      if (serie.length === LIGA.length && serie[serie.length - 1].pontosA === 1) titulos++;
      tot++;
    }
  }
  liga[fo[0]] = { titulos: r4(titulos / tot), chegou_na_luta: chegou.map(c => r4(c / tot)) };
}
const melhor = Object.entries(liga).sort((a, b) => b[1].titulos - a[1].titulos)[0];
return { fator, por_luta: porLuta, liga_inteira: liga, vencivel_cada_luta: porLuta.every(x => x.melhor_taxa > 0),
  liga_completavel: melhor[1].titulos > 0, melhor_forma_na_liga: { forma: melhor[0], titulos: melhor[1].titulos } };
}
const porFator = FATORES.map(conferir);
const saida = {
  descricao: "Conferencia da Liga dos Lideres (sem calibracao): o Mega de referencia com o treino tipico contra cada lider e a Liga inteira",
  motor: "web/app/motor (escala CESC_V6 ligada, regras V21D, limite do desafiado = o lider)",
  fator_desenho: FATOR_LIGA_DESENHO, fator_adotado: FATOR_LIGA, treino_tipico_mega: TIPICO, sementes: SEMENTES, partidas_por_semente_especie_forma: N,
  por_fator: porFator,
};
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/liga/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + "conferencia.json", JSON.stringify(saida, null, 2) + "\n");
for (const c of porFator) {
  console.log(`--- fator ${c.fator}: cada luta vencivel ${c.vencivel_cada_luta}; Liga completavel ${c.liga_completavel} (melhor ${c.melhor_forma_na_liga.forma} ${c.melhor_forma_na_liga.titulos})`);
  for (const x of c.por_luta) console.log(`${x.luta}. ${x.lider} (${x.mega} · ${x.arquetipo}): melhor ${x.melhor_forma} ${x.melhor_taxa}`, JSON.stringify(x.por_forma));
  for (const [f, x] of Object.entries(c.liga_inteira)) console.log(`Liga inteira, ${f}: títulos ${x.titulos}; chegou`, x.chegou_na_luta.join(" "));
}
