/* A medida do sono que segura (docs/TAREFA_V3_SONO_SEGURA.md, a secao do resultado): o pet do jogo com o DigiBrain modular, a v25 (o sono de
   antes) contra a v27 (o sono que segura), sementes 101, 202 e 303, 4 dias de jogo, um tick por vez, com o mesmo roteiro do dono: alimentar
   quando a fome cai abaixo de 0,5 e limpar com a sujeira em 2 ou mais (os numeros do pedido; PROPOSTOS, SEM FONTE). Mede a fracao do tempo
   dormindo, os cochilos depois do primeiro dia e a mediana da energia no comeco e no fim de cada sono. So um teste: nenhum codigo do jogo muda;
   a tabela sai no console. */
import { describe, expect, test } from "vitest";
import { Motor } from "../motor/motor.ts";
import { TPD, VERSAO_V25, VERSAO_V27 } from "../motor/constantes.ts";

const SEMENTES = [101, 202, 303];
const DIAS = 4;

interface Medida { versao: number; semente: number; fracao: number; cochilos: number; cochilosDepoisDia1: number; eInicio: number; eFim: number }
const mediana = (xs: number[]): number => {
  if (!xs.length) return NaN;
  const o = [...xs].sort((a, b) => a - b), n = o.length;
  return n % 2 ? o[(n - 1) / 2]! : (o[n / 2 - 1]! + o[n / 2]!) / 2;
};

function medir(versao: number, semente: number): Medida {
  const m = new Motor(semente, versao);
  m.trocarCerebro("modular");
  let dormindo = 0, cochilos = 0, depoisDia1 = 0;
  const inicio: number[] = [], fim: number[] = [];
  let antes = m.e.dormindo;
  for (let t = 0; t < DIAS * TPD; t++) {
    if (m.morte !== null) throw new Error(`o pet v${versao}/${semente} morreu no tick ${t}`);
    if (m.e.fome < .5) m.observar("alimentar");
    if (m.e.sujeira >= 2) m.observar("limpar");
    const eAntes = m.e.energia;
    m.avancar(1);
    const agora = m.e.dormindo;
    if (agora) dormindo++;
    if (agora && !antes) { cochilos++; if (t >= TPD) depoisDia1++; inicio.push(eAntes); }
    if (!agora && antes) fim.push(eAntes);
    antes = agora;
  }
  return { versao, semente, fracao: dormindo / (DIAS * TPD), cochilos, cochilosDepoisDia1: depoisDia1, eInicio: mediana(inicio), eFim: mediana(fim) };
}

describe("a medida do sono que segura (v25 x v27)", () => {
  test("a tabela: a v27 dorme em menos cochilos e acorda mais descansada", () => {
    const linhas = [VERSAO_V25, VERSAO_V27].flatMap(v => SEMENTES.map(s => medir(v, s)));
    const f = (x: number) => x.toFixed(2);
    console.log(["versao | semente | % dormindo | cochilos | cochilos depois do dia 1 | energia mediana no comeco | no fim",
      ...linhas.map(l => `v${l.versao} | ${l.semente} | ${(100 * l.fracao).toFixed(1)} | ${l.cochilos} | ${l.cochilosDepoisDia1} | ${f(l.eInicio)} | ${f(l.eFim)}`)].join("\n"));
    for (const s of SEMENTES) {
      const a = linhas.find(l => l.versao === VERSAO_V25 && l.semente === s)!, b = linhas.find(l => l.versao === VERSAO_V27 && l.semente === s)!;
      expect(b.cochilosDepoisDia1).toBeLessThan(a.cochilosDepoisDia1);
      expect(b.eFim).toBeGreaterThan(a.eFim);
    }
  });
});
