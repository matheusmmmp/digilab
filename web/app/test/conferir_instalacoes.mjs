// Conferencia das instalacoes da Fronteira (docs/DESIGN_FRONTEIRA.md, secao 3; medalhas parte 4b): a Torre de Batalha e o Palacio. SEM
// calibracao (decisao do Matheus: sem rodada de equilibrio nesta parte): so confere que as duas sao jogaveis, ou seja, que um Mega bem
// treinado vence ao menos a primeira luta com frequencia, e que a sequencia acaba longe do teto. Nenhum numero do jogo sai daqui.
//
// Metodo (o da Liga, test/conferir_liga.mjs): motor web, escala dos pets v6 ligada, regras V21D, limite de turnos do desafiado (o rival);
// o pet de referencia = cada uma das 8 formas no Mega, nas 4 especies, com o treino tipico do Mega (40, uniforme), sem chip e sem carta,
// com a lista canonica. Os rivais = os Megas sorteados da instalacao (motor/instalacoes.ts, fator 1), a sequencia como o motor a joga
// (arenas.jogarSequencia, sem cura, ate a primeira luta que nao for vitoria, teto LUTAS_MAX_INSTALACAO). Sementes de validacao da parte 2
// (4101...4505), N tentativas por semente, especie e forma.
// - Torre de Batalha: a tentativa como acima;
// - Palacio: com a lista canonica, sem trava, veto nem chip de regra, a lista que o pet faria sozinho e a mesma: o Palacio do pet de
//   referencia e a Torre (as sementes de tentativa mudam pelo nome da instalacao). A diferenca so aparece num pet com intervencoes do dono;
// - o pet do teste ponta a ponta (e2e/save_liga.json, um Valkyrimon de vida de verdade) nas 50 primeiras tentativas de cada instalacao, pelo
//   motor (Motor.montarLuta com a semente de cada tentativa: o sorteio do jogo).
// uso (em web/app): npx tsx test/conferir_instalacoes.mjs  ->  artifacts_campanha/fronteira/conferencia.json
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";
import { R, formasDe, lutador } from "./itens_ref.mjs";

const { CIT, ESPECIES, INSTALACOES, LUTAS_MAX_INSTALACAO, FATOR_INSTALACAO } = M;
M.ligarEscala(true);
const SEMENTES = [4101, 4202, 4303, 4404, 4505], N = 20, TIPICO = CIT.tipico.mega, N_SAVE = 50;
const r4 = x => +x.toFixed(4);
/** o resumo das sequencias (vitorias seguidas por tentativa) */
function resumo(vs) {
  const o = [...vs].sort((a, b) => a - b), q = p => o[Math.min(o.length - 1, Math.floor(p * o.length))];
  return { tentativas: o.length, vence_a_primeira: r4(o.filter(v => v >= 1).length / o.length), media: r4(o.reduce((a, b) => a + b, 0) / o.length),
    mediana: q(.5), p90: q(.9), maximo: o[o.length - 1], no_teto: o.filter(v => v >= LUTAS_MAX_INSTALACAO).length };
}
const vitorias = serie => serie.filter(x => x.pontosA === 1).length;

/* o pet de referencia: as 8 formas, as 4 especies */
function referencia(inst) {
  const porForma = {};
  for (const fo of formasDe("mega")) {
    const vs = [];
    for (const e of ESPECIES) {
      const A = lutador(fo, e, TIPICO, [], true);
      for (const s of SEMENTES) for (let k = 0; k < N; k++) {
        const st = M.hashSemente("conferir-fronteira", inst, s, A.nome, k);
        vs.push(vitorias(M.jogarSequencia(A, j => M.rivalInstalacao(st, j, R), LUTAS_MAX_INSTALACAO, st, R, 1, null)));
      }
    }
    porForma[fo[0]] = resumo(vs);
  }
  const melhor = Object.entries(porForma).sort((a, b) => b[1].vence_a_primeira - a[1].vence_a_primeira || b[1].media - a[1].media)[0];
  return { por_forma: porForma, melhor_forma: { forma: melhor[0], ...melhor[1] } };
}
/* o pet do teste ponta a ponta: as primeiras tentativas dele, com a semente de cada uma (o sorteio do jogo) */
const SAVE = JSON.parse(readFileSync(new URL("../e2e/save_liga.json", import.meta.url), "utf8"));
function doSave(inst) {
  const m = M.Motor.reproduzir(SAVE.semente, SAVE.log, SAVE.versao);
  m.abrirFronteira();
  const vs = [];
  for (let n = 1; n <= N_SAVE; n++) vs.push(vitorias(m.montarLuta(inst, M.sementeTentativa(m.semente, inst, n)).serie));
  return { pet: M.nomeForma(m.forma), arquetipo: M.NOME_ARQ[m.forma.adulta], treino: m.treino.total, ...resumo(vs) };
}
const porInst = Object.fromEntries(INSTALACOES.map(x => [x.id, { nome: x.nome, referencia: referencia(x.id), pet_do_e2e: doSave(x.id) }]));
const jogavel = Object.values(porInst).every(x => x.referencia.melhor_forma.vence_a_primeira >= .5
  && Object.values(x.referencia.por_forma).every(f => f.no_teto === 0));
const saida = {
  descricao: "Conferencia das instalacoes da Fronteira (sem calibracao): o Mega de referencia com o treino tipico na Torre de Batalha e no Palacio",
  motor: "web/app/motor (escala CESC_V6 ligada, regras V21D, limite do desafiado = o rival)",
  fator: FATOR_INSTALACAO, teto_de_lutas: LUTAS_MAX_INSTALACAO, treino_tipico_mega: TIPICO, sementes: SEMENTES, tentativas_por_semente_especie_forma: N,
  nota_palacio: "com a lista canonica (sem trava, veto nem chip de regra) o Palacio do pet de referencia e a Torre; muda so a semente das tentativas",
  jogavel_melhor_forma_vence_a_primeira_em_metade_e_ninguem_no_teto: jogavel,
  por_instalacao: porInst,
};
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/fronteira/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + "conferencia.json", JSON.stringify(saida, null, 2) + "\n");
for (const [id, x] of Object.entries(porInst)) {
  console.log(`--- ${x.nome} (${id})`);
  for (const [f, r] of Object.entries(x.referencia.por_forma)) console.log(`${f}: vence a 1a ${r.vence_a_primeira}; média ${r.media}; mediana ${r.mediana}; p90 ${r.p90}; máx ${r.maximo}`);
  const p = x.pet_do_e2e;
  console.log(`pet do e2e (${p.pet}, ${p.arquetipo}, treino ${p.treino}): vence a 1a ${p.vence_a_primeira}; média ${p.media}; mediana ${p.mediana}; máx ${p.maximo}`);
}
console.log("jogável:", jogavel);
