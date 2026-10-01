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
//
// Pets v9 (padrao; rodada de equilibrio geral, fase 3, meta M-E1): o mesmo metodo com as regras das lutas dos pets v9 (combate V21E: as listas
// V21E nas formas de referencia e nos rivais), a escala da versao 9 (CESC_V9, a mesma vida do Mega) e o fator dos rivais das instalacoes
// (FATOR_INSTALACAO = 1, o mesmo: a meta passou sem mudar), nas sementes de calibracao (3101...3505). Meta M-E1: na Torre de Batalha e no
// Palacio, a melhor forma vence a 1a luta >= 0,70 e a pior >= 0,40. O pet do teste ponta a ponta (um v6) fica so no --v6.
// --validar (fase 4, a validacao unica): a conferencia dos v9 (nada muda) nas sementes de validacao (4101...4505).
// uso (em web/app): npx tsx test/conferir_instalacoes.mjs [--v6 | --validar]
//   --v6: artifacts_campanha/fronteira/conferencia.json (a de antes, byte a byte); padrao: artifacts_equilibrio_geral/fase3/instalacoes_conferencia.json;
//   --validar: artifacts_equilibrio_geral/fase4/instalacoes_validacao.json
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";
import { R, R9, formasDe, lutador } from "./itens_ref.mjs";

/* ------------------------------------------------------------------------------------------------ pets v6 (a conferencia de antes) */
function conferirV6() {
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
}

/* ------------------------------------------------------------------------------------------------ pets v9 (meta M-E1) */
function conferirV9(validar) {
  const { ESPECIES, INSTALACOES, LUTAS_MAX_INSTALACAO, FATOR_INSTALACAO, CIT } = M;
  M.ligarEscala(true);
  const SEM_CALIBRACAO = [3101, 3202, 3303, 3404, 3505], SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505];
  const SEMENTES = validar ? SEM_VALIDACAO : SEM_CALIBRACAO, N = 20, TIPICO = CIT.tipico.mega, META_MELHOR = 0.70, META_PIOR = 0.40;
  const r4 = x => +x.toFixed(4);
  function resumo(vs) {
    const o = [...vs].sort((a, b) => a - b), q = p => o[Math.min(o.length - 1, Math.floor(p * o.length))];
    return { tentativas: o.length, vence_a_primeira: r4(o.filter(v => v >= 1).length / o.length), media: r4(o.reduce((a, b) => a + b, 0) / o.length),
      mediana: q(.5), p90: q(.9), maximo: o[o.length - 1], no_teto: o.filter(v => v >= LUTAS_MAX_INSTALACAO).length };
  }
  const porInst = {};
  for (const x of INSTALACOES) {
    const porForma = {};
    for (const fo of formasDe("mega", R9)) {
      const vs = [];
      for (const e of ESPECIES) {
        const A = lutador(fo, e, TIPICO, [], true, M.VERSAO_ESCALA_V9);
        for (const s of SEMENTES) for (let k = 0; k < N; k++) {
          const st = M.hashSemente("conferir-fronteira", x.id, s, A.nome, k);
          vs.push(M.jogarSequencia(A, j => M.rivalInstalacao(st, j, R9), LUTAS_MAX_INSTALACAO, st, R9, 1, null).filter(r => r.pontosA === 1).length);
        }
      }
      porForma[fo[0]] = resumo(vs);
    }
    const ord = Object.entries(porForma).sort((a, b) => b[1].vence_a_primeira - a[1].vence_a_primeira);
    const melhor = { forma: ord[0][0], vence_a_primeira: ord[0][1].vence_a_primeira }, pior = { forma: ord[ord.length - 1][0], vence_a_primeira: ord[ord.length - 1][1].vence_a_primeira };
    porInst[x.id] = { nome: x.nome, melhor, pior, meta_e1: { passa: melhor.vence_a_primeira >= META_MELHOR && pior.vence_a_primeira >= META_PIOR,
      folga: r4(Math.min(melhor.vence_a_primeira - META_MELHOR, pior.vence_a_primeira - META_PIOR)) }, por_forma: porForma };
  }
  const saida = {
    descricao: validar ? "Validacao das instalacoes da Fronteira dos pets v9 (fase 4, meta M-E1): tudo congelado, nas sementes de validacao"
      : "Conferencia das instalacoes da Fronteira dos pets v9 (fase 3, meta M-E1): o Mega de referencia com o treino tipico na Torre de Batalha e no Palacio",
    motor: "web/app/motor (escala CESC_V9 ligada, regras V21E, limite do desafiado = o rival)", conjunto: validar ? "validacao" : "calibracao",
    fator: FATOR_INSTALACAO, teto_de_lutas: LUTAS_MAX_INSTALACAO, treino_tipico_mega: TIPICO, sementes: SEMENTES, tentativas_por_semente_especie_forma: N,
    metas: { melhor_forma_vence_a_primeira_min: META_MELHOR, pior_forma_vence_a_primeira_min: META_PIOR },
    nota_palacio: "com a lista canonica (sem trava, veto nem chip de regra) o Palacio do pet de referencia e a Torre; muda so a semente das tentativas",
    meta_e1: { passa: Object.values(porInst).every(x => x.meta_e1.passa), menor_folga: Math.min(...Object.values(porInst).map(x => x.meta_e1.folga)) },
    por_instalacao: porInst,
  };
  const pasta = fileURLToPath(new URL(validar ? "../../../artifacts_equilibrio_geral/fase4/" : "../../../artifacts_equilibrio_geral/fase3/", import.meta.url));
  mkdirSync(pasta, { recursive: true });
  writeFileSync(pasta + (validar ? "instalacoes_validacao.json" : "instalacoes_conferencia.json"), JSON.stringify(saida, null, 1) + "\n");
  for (const [id, x] of Object.entries(porInst)) {
    console.log(`--- ${x.nome} (${id}): melhor ${x.melhor.forma} ${x.melhor.vence_a_primeira}; pior ${x.pior.forma} ${x.pior.vence_a_primeira}; M-E1 ${x.meta_e1.passa}`);
    for (const [f, r] of Object.entries(x.por_forma)) console.log(`${f}: vence a 1a ${r.vence_a_primeira}; média ${r.media}; máx ${r.maximo}`);
  }
}

const args = process.argv.slice(2);
if (args.includes("--v6")) conferirV6();
else conferirV9(args.includes("--validar"));
