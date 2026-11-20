// Save do momento da evolucao (docs/TAREFA_V2_EVOLUCAO.md): um pet v11 (a versao de hoje) no Rookie, cuidado por um dono atencioso, que
// conhece a medalha que a evolucao para o Champion pede (o evento "u" logo no comeco) e para a FALTA minutos do fim do Rookie. O registro
// termina num avanco de tempo. Quando o relogio do app anda (10 min de jogo por segundo, no 10 min/s de sempre), ele vira Champion e a
// revelacao abre: e assim que o e2e e as capturas mostram o momento, sem rota de depuracao. Conferido aqui: refeito do registro, ele ainda
// e Rookie e evolui em ate 10 min de jogo. uso (em web/app): node e2e/gerar_save_evolucao.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import * as M from "../motor/index.ts";

const { ACOES_DONO_JOGO_V11, CD, TPD, VERSAO_PET, Motor, criarDono, criarRng, hashSemente } = M;
const FALTA = 4;

function rookieQuase(semente) {
  const m = new Motor(semente, VERSAO_PET), dono = criarDono("atencioso"), rng = criarRng(hashSemente("dono", semente, "atencioso"));
  m.liberar(1);
  const dias = 2, passos = Math.round(dias * TPD / CD.passo), orc = Math.round(16 * dias);
  let gasto = 0;
  for (let p = 0; p < passos; p++) {
    if (m.estagioAtual === "crianca" && m.tickLimiteEstagio() - m.e.tick <= CD.passo + FALTA) break;
    m.avancar(CD.passo);
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    /* o dono atencioso do Cenarios, so com as acoes que os pets v11 tem (sem elogio, bronca, petisco e banheiro) */
    for (const a of dono.decidir(v, rng)) if (ACOES_DONO_JOGO_V11.includes(a)) { m.observar(a); gasto++; }
  }
  if (m.estagioAtual !== "crianca") return null;
  m.avancar(m.tickLimiteEstagio() - FALTA - m.e.tick);         /* o registro termina num avanco de tempo */
  return m;
}
for (let s = 6300; s < 6400; s++) {
  const m = rookieQuase(s);
  if (!m || m.morte || m.log[m.log.length - 1][1] !== "t") continue;
  const x = Motor.reproduzir(m.semente, m.log, VERSAO_PET), n = x.evolucoes.length;
  if (x.estagioAtual !== "crianca") continue;
  x.avancar(10);
  if (x.evolucoes.length !== n + 1 || x.estagioAtual !== "adolescente") continue;
  const save = { semente: m.semente, log: m.log, versao: m.versao };
  writeFileSync(fileURLToPath(new URL("./save_evolucao.json", import.meta.url)), JSON.stringify(save) + "\n");
  console.log("semente", s, "eventos", m.log.length, M.nomeForma(m.forma), "->", M.nomeForma(x.forma));
  process.exit(0);
}
throw new Error("nenhuma semente deu um Rookie que vira Champion nos proximos 10 min");
