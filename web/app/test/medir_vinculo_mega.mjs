// Quantos pets v5 chegam ao Mega com os donos simulados da web (motor/donos.ts) e com que vinculo (a condicao do Mega
// pede vinculo >= CMG.vinculo; docs/DESIGN_EVOLUCAO_CANONICA.md, secao 10). Os donos da web nao conhecem a educacao v4:
// aqui eles tratam a lesao e lutam na arena ate qualificar (10 lutas no Champion, 12 no Ultimate). Descritivo, sem IC.
//
// uso (em web/app): node test/medir_vinculo_mega.mjs -> artifacts_campanha/mega/vinculo_donos.json
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { CAT, CD, CMG, TPD } = M, DIAS = 3, POR_DIA = 16, SEMENTES = [2001, 2002, 2003, 2004, 2005, 2006];
function vida(tipo, semente) {
  const m = new M.Motor(semente, 5), dono = M.criarDono(tipo), r = M.criarRng(M.hashSemente("dono", semente, tipo));
  const passos = Math.round(DIAS * TPD / CD.passo), orc = Math.round(POR_DIA * DIAS);
  let gasto = 0, maxVinculoUltimate = null;
  for (let p = 0; p < passos && !m.morte; p++) {
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, r);
    if (m.lesionadoDesde !== null && acoes.length) acoes[0] = "tratar_lesao";
    for (const a of acoes) { m.observar(a); gasto++; }
    if ((m.estagioAtual === "adolescente" && m.sparring < CAT.sparring) || (m.estagioAtual === "adulto" && m.lutas.lutas < 12))
      m.lutar("aleatorio", M.hashSemente("sparring", semente, p));
    if (m.estagioAtual === "adulto" && !m.forma.mega) maxVinculoUltimate = Math.max(maxVinculoUltimate ?? 0, m.vinc.valor);
  }
  const ev = m.evolucoes.find(x => x.mega);
  return { semente, estagio: m.estagioAtual, mega: !!m.forma.mega, sombria: m.sombria, vinculo_final: +m.vinc.valor.toFixed(3),
    vinculo_max_no_ultimate: maxVinculoUltimate === null ? null : +maxVinculoUltimate.toFixed(3), vinculo_na_evolucao: ev ? +ev.vinculo.toFixed(3) : null };
}
const out = { descricao: "Pets v5 com os donos simulados da web: quantos viram Mega (vinculo >= " + CMG.vinculo + ").", dias: DIAS, interacoes_por_dia: POR_DIA,
  sementes: SEMENTES, donos: {} };
for (const tipo of ["atencioso", "incoerente", "relapso", "aleatorio"]) {
  const vidas = SEMENTES.map(s => { try { return vida(tipo, s); } catch (err) { return { semente: s, erro: String(err.message ?? err) }; } });
  out.donos[tipo] = { megas: vidas.filter(v => v.mega).length, vidas };
  console.log(tipo, `${out.donos[tipo].megas}/${SEMENTES.length} Mega`, vidas.map(v => v.erro ?? v.vinculo_max_no_ultimate).join(" "));
}
const pasta = fileURLToPath(new URL("../../../artifacts_campanha/mega/", import.meta.url));
mkdirSync(pasta, { recursive: true });
writeFileSync(pasta + "vinculo_donos.json", JSON.stringify(out, null, 1) + "\n");
