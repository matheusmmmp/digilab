# TAREFA_V3_EQUILIBRIO_CUIDADO: a rodada de equilíbrio do dia a dia do pet

Fase: V3. Coordenador: o Gerente da V3. Data: 2026-11-12. Estado: plano aprovado (EQ-1 a EQ-8 DECIDIDAS, 2026-11-12).

- **O pedido:** o Matheus, em 2026-11-12: "pode fazer uma rodada de equilíbrio".
- **O plano:** `docs/PLANO_V3_EQUILIBRIO_CUIDADO.md`, com os itens, o método (E0 a E3) e as decisões EQ-1 a EQ-8, DECIDIDAS pelo Matheus em 2026-11-12 ("Sim, os dois").
- **O resultado de cada etapa** entra numa seção no fim deste documento.

## Resultado do E0 (2026-11-12)

O retrato de hoje rodou na faixa de calibração (93101…93505, 5 sementes), com o ovo de um pet v35 e o grupo do brasão v36, os três donos do
EQ-4 e 3 dias no ritmo "rapida". Nenhum número do jogo mudou. O plano de análise (`docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md`) e as
faixas entraram antes das vidas. O retrato está em `docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E0.md`:
- o atento passa a fome, a saúde, o sono e o explorar, mas não os Bits por dia (de 6 a 15 nos dias 2 e 3) nem o brincar do Rookie;
- no ovo de um pet, o médio não junta o ★★ antes do tempo do Champion (143 Bits no dia 1);
- o médio e o relapso não alimentam o In-Training; o relapso quebra o sono (energia ao acordar de 0,44 a 0,57) e os chutes por lance;
- ninguém morre e ninguém adoece de verdade em 3 dias.

As metas são PROPOSTAS e esperam o Matheus (EQ-3). Os desvios são os D-EQ0-1 a D-EQ0-8 (`docs/registro/2026-11.md`).

## Resultado do E1 (2026-11-12)

A calibração rodou só na faixa de calibração (93101…93505), nas mesmas 30 vidas do E0, com as metas APROVADAS. Tudo está atrás de chave
desligada: os pets de hoje saem byte a byte, e nenhuma versão de pet liga as chaves (a versão é o E3). O resultado, com a grade inteira, está
em `docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E1.md`:
- **as duas regras da EQ-7**, no Python e no TS, com a paridade: a guarda da fome urgente no brincar (o M-ARB zera o brincar) e o bebê que come
  com a fome dele (o gancho `estagio_bebe` e a entrada `bebe` no inato do comer), na `ConfigEquilibrioCuidado`;
- **os números propostos** (a rodada F2 de 30 rodadas): o bebê com o peso 512, a fome urgente em 640 (hoje 512), o vies do brincar em 0
  (hoje −256), e a `BITS_V2` com o cuidado 5, o teto 40 e a evolução do Rookie 60;
- **as metas:** 6 linhas falham, contra 16 no E0, e nenhuma que passava cai. Passam o sono do médio do ovo de um pet (e os cochilos do médio do grupo), o brincar do atento, o ★★ do médio e os
  Bits por dia do atento. Não fecham a ração do Rookie do atento no ovo de um pet (a medida e o dono, não o bebê), o sono do relapso e os
  chutes do relapso do grupo (a guarda os baixa, como o G-BB-2 pede);
- **para o Matheus:** os valores, a medida da M-A1 e da M-C1, e uma fonte de Bits que pague o cuidado bom (regra nova, fora da EQ-7).

Os desvios são os D-EQ1-1 a D-EQ1-11 (`docs/registro/2026-11.md`).
