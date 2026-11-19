/* MMO6: quanto a semente da luta, que é de cada conta (MMO-10), muda o resultado da primeira luta da Fábrica do dia. Para cada segredo de
   dia (os bytes 0x00 a 0x3f repetidos 32 vezes: 64 dias de mentira) e cada alugado (0 a 2), a primeira luta é jogada com a semente de 40
   contas de mentira. Conta, em cada par (dia, alugado), quantas das 40 contas vencem. Um par em que todas vencem ou todas perdem é um par
   em que a semente da conta não mudou nada: quem sabe o dia (os alugados e o primeiro rival, iguais para todos) já sabe o resultado.
   Só a primeira luta (as seguintes dependem da vida que o alugado leva e das trocas). Um processo só.
     cd servidor_web && node scripts/medir_sorte_desafio.ts   ->  medicoes/mmo6_sorte_do_dia.json */
import { mkdirSync, writeFileSync } from "node:fs";
import { TentativaFabrica, chaveSprite } from "../../web/app/motor/index.ts";
import { sementeDaLutaDoDia, sementeDoDia } from "../src/desafio/desafio.ts";

const DIAS = 64, CONTAS = 40, ALUGADOS = 3;
const pares: { dia: string; alugado: number; forma: string; rival: string; vencem: number }[] = [];
for (let b = 0; b < DIAS; b++) {
  const segredo = Buffer.from(b.toString(16).padStart(2, "0").repeat(32), "hex"), dia = sementeDoDia(segredo);
  for (let e = 0; e < ALUGADOS; e++) {
    let vencem = 0;
    const t0 = TentativaFabrica.doDia(e, dia);
    for (let c = 0; c < CONTAS; c++) {
      const s = sementeDaLutaDoDia(segredo, `conta-${c}`, 0);
      if (TentativaFabrica.doDia(e, dia, [s]).lutar(s).venceu) vencem++;
    }
    pares.push({ dia: b.toString(16).padStart(2, "0"), alugado: e, forma: chaveSprite(t0.alugueis[e]!), rival: chaveSprite(t0.proximoRival()!.rival), vencem });
  }
}
const todas = pares.filter(p => p.vencem === CONTAS).length, nenhuma = pares.filter(p => p.vencem === 0).length;
const saida = {
  nota: "MMO6: a primeira luta da Fábrica do dia com a semente de 40 contas; 'vencem' é quantas das 40 vencem. Pares (dia, alugado) com 0 ou 40: a semente da conta não muda o resultado",
  dias: DIAS, contas: CONTAS, alugados: ALUGADOS, pares: pares.length,
  todas_vencem: todas, nenhuma_vence: nenhuma, decididos_pelo_dia: todas + nenhuma, fracao_decidida_pelo_dia: (todas + nenhuma) / pares.length,
  dias_com_um_alugado_que_sempre_vence: new Set(pares.filter(p => p.vencem === CONTAS).map(p => p.dia)).size,
  porPar: pares,
};
mkdirSync(new URL("../medicoes/", import.meta.url), { recursive: true });
writeFileSync(new URL("../medicoes/mmo6_sorte_do_dia.json", import.meta.url), JSON.stringify(saida, null, 1) + "\n");
console.log(`pares ${pares.length}: todas vencem ${todas}, nenhuma vence ${nenhuma}, decididos pelo dia ${(100 * (todas + nenhuma) / pares.length).toFixed(1)} %; dias com um alugado que sempre vence ${saida.dias_com_um_alugado_que_sempre_vence} de ${DIAS}`);
