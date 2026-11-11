/* LUTA_POC, LP5-2 (D-LP5-18, parte 2): a leitura curta da vida para o P5, sem mudar numero nenhum. Por que o pet da vida vence 0,67 do
   sparring no Champion, e o pet tipico da bancada 0,85? Refaz as vidas do grupo vida (a mesma conta do bancada.ts, as mesmas sementes da
   calibracao) e, em cada luta de sparring do Champion, grava o pet como ele estava (a forma, o carater, os pontos, a condicao pela saude) e
   refaz a mesma luta, com a mesma semente, pelo nucleo da bancada, trocando uma coisa por vez:
     real      o pet como estava (confere a luta do Motor);
     cond1     a condicao 1 (o pet bem cuidado);
     sem_car   e sem o carater (o pet tipico da bancada no Champion nao tem carater: o caraterRival so existe da forma adulta em diante);
     tipico    e os pontos do dono tipico da especie no total do Champion (22), em vez dos pontos da vida;
   e, para comparar, a mesma luta com o pet tipico de cada uma das 4 formas da especie (o que a bancada sorteia). Leitura, nao meta.
   uso (em web/app): node scripts/equilibrio_poc/leitura_vida.ts --candidato lp5_2
   -> scripts/medicoes/equilibrio_poc/lp5_2/leitura_vida/leitura.json e leitura.md */
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  ACOES_DONO_JOGO_V11, CAT, CD, CLE, CMD, CTR, TPD, condicaoDe, criarDono, criarRng, formaDaChave, hashSemente, rivaisArena, sementeDaSerie,
  type Exercicio, type VisaoDono,
} from "../../motor/index.ts";
import { TIPICO, argumento, commitAtual, esquivaDe, lutador, lutar, pontosNoTotal, type EstagioLuta, type Lado } from "./comum.ts";
import { candidatoDaLinha } from "./candidatos.ts";
import { motorDoCandidato, TAM } from "./bancada.ts";
import { basesDa } from "./faixas.ts";

const nomeC = argumento("candidato"), c = candidatoDaLinha(nomeC, "", false), ESQ = esquivaDe(c), TIRO = c.tiro;
const EXERCICIOS = Object.keys(CTR.exercicios) as Exercicio[];
const RAMOS_CHAMPION = ["guardiao", "cacador", "colosso", "brigao"];
type Var = "real" | "cond1" | "sem_car" | "tipico";
const VARS: Var[] = ["real", "cond1", "sem_car", "tipico"];
interface Luta { base: number; i: number; especie: string; forma: string; rival: string; condicao: number; atento: number; treino: number; motor: boolean; v: Record<string, number> }
const lutas: Luta[] = [], vidas: unknown[] = [];
let confere = 0, difere = 0;
const ganhou = (r: { vencedor: "a" | "b" | null }) => r.vencedor === "a" ? 1 : 0;

for (const base of basesDa("calibracao")) for (let i = 0; i < TAM.vidas; i++) {
  /* a mesma vida do grupo vida (bancada.ts), passo a passo */
  const semente = hashSemente("equilibrio-poc-pet", base, i), m = motorDoCandidato(c, semente), dono = criarDono("atencioso");
  const r = criarRng(hashSemente("dono", semente, "atencioso")), passos = Math.round(TAM.diasVida * TPD / CD.passo), orc = Math.round(CD.porDia * TAM.diasVida);
  let gasto = 0, ex = 0, k = 0, nCh = 0, vCh = 0;
  m.liberar(CMD.mega);
  for (let p = 0; p < passos && m.estagioAtual !== "mega" && !m.morte; p++) {
    m.avancar(CD.passo);
    if (m.morte) break;
    const rest = orc - gasto, min = Math.max(0, rest - (passos - p - 1) * CD.maxPasso), max = Math.min(rest, CD.maxPasso);
    const v: VisaoDono = { e: m.e, acao: m.acao, passo: p, passos, orc, gasto, min, max, atrasado: gasto < orc * (p + 1) / passos, chamados: m.chamadosAbertos() };
    const acoes = dono.decidir(v, r).filter(a => ACOES_DONO_JOGO_V11.includes(a));
    if (m.lesionadoDesde !== null && acoes.length) acoes[0] = "tratar_lesao";
    for (const a of acoes) { m.observar(a); gasto++; }
    if (m.morte) break;
    const est = m.estagioAtual;
    if (est !== "bebe" && m.treino.total < TIPICO[est as EstagioLuta] - 1e-9 && m.treino.podeTocar(m.e.tick) && !m.treino.pedePausa) m.treinar(EXERCICIOS[ex++ % EXERCICIOS.length]);
    if ((est === "adolescente" && m.sparring < CAT.sparring) || (est === "adulto" && m.lutas.lutas < 12)) {
      const rv = m.rivaisArenaPoc(), s = hashSemente("equilibrio-poc", base, "vida", i, k++);
      /* o pet como estava antes da luta (so o Champion entra na leitura) */
      const forma = m.forma, car = m.carater(), pontos = m.pontosDeLuta(), cond = condicaoDe(m.e.saude), treino = m.treino.total;
      const res = m.lutarPoc(rv[s % rv.length], s, "campo"), u = res.serie[0];
      if (est !== "adolescente") continue;
      nCh++; if (res.venceu) vCh++;
      const sl = sementeDaSerie(s, 0), rival: Lado = { forma: u.contra, stats: u.rivalStats };
      const pet = (x: Var): Lado => ({ forma: res.forma, stats: lutador(c, forma, x === "real" || x === "cond1" ? car : null, x === "tipico" ? pontosNoTotal(forma.esp, TIPICO.adolescente) : pontos, x === "real" ? cond : 1) });
      const out: Record<string, number> = {};
      for (const x of VARS) out[x] = ganhou(lutar("campo", sl, pet(x), rival, TIRO, ESQ));
      /* a mesma luta com o pet tipico de cada forma do Champion da especie (o pet da bancada) */
      for (const ramo of RAMOS_CHAMPION) {
        const ch = `${forma.esp}_adolescente_${ramo}`;
        if (!rivaisArena("adolescente").includes(ch)) throw new Error(`leitura: ${ch} nao e uma forma do Champion`);
        const f = formaDaChave(ch);
        out[`forma_${ramo}`] = ganhou(lutar("campo", sl, { forma: ch, stats: lutador(c, f, null, pontosNoTotal(f.esp, TIPICO.adolescente)) }, rival, TIRO, ESQ));
      }
      if (out.real === (res.venceu ? 1 : 0)) confere++; else difere++;
      lutas.push({ base, i, especie: forma.esp, forma: res.forma, rival: u.contra, condicao: cond, atento: car?.atento ?? 0, treino, motor: res.venceu, v: out });
    }
  }
  vidas.push({ base, i, especie: m.especie, forma_champion: lutas.findLast(x => x.base === base && x.i === i)?.forma ?? null, estagio: m.estagioAtual,
    champion: { n: nCh, v: vCh }, taxa_do_motor: m.lutas.lutas ? m.lutas.vitorias / m.lutas.lutas : null });
}
if (difere) throw new Error(`leitura: ${difere} lutas do Motor nao se refazem no nucleo da bancada (${confere} conferem)`);

/* as contas: a taxa de cada troca, no todo, por forma do pet e por especie */
const taxaDe = (xs: Luta[], k: string) => Math.round(xs.reduce((a, x) => a + x.v[k], 0) / xs.length * 1000) / 1000;
const chaves = [...VARS, ...RAMOS_CHAMPION.map(r => `forma_${r}`)];
const grupo = (f: (x: Luta) => string) => {
  const g: Record<string, Luta[]> = {};
  for (const x of lutas) (g[f(x)] ??= []).push(x);
  return Object.fromEntries(Object.entries(g).map(([k, xs]) => [k, { n: xs.length, motor: Math.round(xs.filter(x => x.motor).length / xs.length * 1000) / 1000, ...Object.fromEntries(chaves.map(c2 => [c2, taxaDe(xs, c2)])) }]));
};
const cond = lutas.map(x => x.condicao).sort((a, b) => a - b), med = (xs: number[]) => xs[Math.floor(xs.length / 2)];
/* a chance de passar no Champion com uma taxa p por luta: >= 0,8 (CLE.limiarTaxa) nas 10 lutas (CAT.sparring) do dono simulado */
const binom = (n: number, kmin: number, p: number) => { let s = 0; for (let x = kmin; x <= n; x++) { let comb = 1; for (let j = 0; j < x; j++) comb = comb * (n - j) / (j + 1); s += comb * p ** x * (1 - p) ** (n - x); } return Math.round(s * 1000) / 1000; };
const kmin = Math.ceil(CLE.limiarTaxa * CAT.sparring - 1e-9);
const todas = grupo(() => "todas").todas;
const saida = {
  tarefa: "LUTA_POC, LP5-2, a leitura da vida (D-LP5-18)", candidato: c.nome, commit: commitAtual(), faixa: "calibracao", bases: basesDa("calibracao"),
  vidas_por_base: TAM.vidas, dias: TAM.diasVida, lutas_champion: lutas.length, conferem_com_o_motor: confere,
  taxa: todas, por_forma: grupo(x => x.forma), por_ramo: grupo(x => x.forma.split("_").pop()!), por_especie: grupo(x => x.especie),
  condicao: { min: cond[0], mediana: med(cond), max: cond[cond.length - 1], abaixo_de_1: Math.round(cond.filter(x => x < 1).length / cond.length * 1000) / 1000 },
  atento: { mediana: med(lutas.map(x => x.atento).sort((a, b) => a - b)) },
  treino: { mediana: med(lutas.map(x => x.treino).sort((a, b) => a - b)) },
  passar_no_champion: { regra: `>= ${kmin} de ${CAT.sparring}`, ...Object.fromEntries(chaves.map(k2 => [k2, binom(CAT.sparring, kmin, (todas as Record<string, number>)[k2])])), com_p_0_85: binom(CAT.sparring, kmin, .85) },
  vidas,
};
const dir = fileURLToPath(new URL(`../medicoes/equilibrio_poc/${nomeC}/leitura_vida/`, import.meta.url));
mkdirSync(dir, { recursive: true });
writeFileSync(dir + "leitura.json", JSON.stringify(saida, null, 1) + "\n");
const linhas = (o: Record<string, Record<string, number>>) => Object.entries(o).map(([k, x]) => `| ${k} | ${x.n} | ${x.motor} | ${chaves.map(c2 => x[c2]).join(" | ")} |`);
const cab = `| | lutas | o Motor | ${chaves.join(" | ")} |\n|---|---|---|${chaves.map(() => "---").join("|")}|`;
writeFileSync(dir + "leitura.md", [`# A leitura da vida, ${c.nome} (D-LP5-18)`, "", `commit \`${saida.commit}\`, ${lutas.length} lutas de sparring do Champion em ${vidas.length} vidas; ${confere} refeitas iguais pelo nucleo da bancada.`, "",
  "## A taxa no Champion, trocando uma coisa por vez", "", cab, ...linhas({ todas }), "", "## Por forma do pet", "", cab, ...linhas(saida.por_forma), "", "## Por especie", "", cab, ...linhas(saida.por_especie), "",
  `A condicao pela saude: ${JSON.stringify(saida.condicao)}. O eixo atento: ${JSON.stringify(saida.atento)}. O treino: ${JSON.stringify(saida.treino)}.`, "",
  `A chance de passar no Champion (${saida.passar_no_champion.regra}, se cada luta valesse a taxa): ${JSON.stringify(saida.passar_no_champion)}.`, ""].join("\n"));
console.log(`leitura: ${lutas.length} lutas, ${confere} conferem -> ${dir}`);
