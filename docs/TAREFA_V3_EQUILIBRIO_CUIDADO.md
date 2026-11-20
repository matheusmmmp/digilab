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

## Resultado do E2 e do E3 (2026-11-12)

**O E2, a validação única,** rodou uma vez, depois do adendo 1 do plano de análise (seção 9, commitado antes da primeira vida) e do modo de
validação da bancada: a F2 do E1 com as chaves ligadas, nas 30 vidas da faixa de validação (94101, 94202, 94303, 94404 e 94505), com o ovo
de um pet v35 e o grupo v37 (o `VERSAO_GRUPO` depois do merge da `main`; a calibração foi na v36, D-EQ2-1). O resultado está em
`docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E2.md`:
- **das 52 linhas de meta, falham 16 no E0, 6 no E1 e 10 no E2.** As 6 do E1 falham também na validação; caem mais 4 (o sono e os chutes do
  relapso do ovo de um pet, a ração do 3º dia e o brincar do 2º dia do atento do grupo, os dois na borda);
- passam a fome, a saúde, o explorar, o ★★ antes do Champion, os Bits por dia do atento e nenhuma morte, nas duas versões; das 16 do E0, 7
  consertadas se mantêm;
- os gates que falham ficam como estão e não pararam a rodada.

**O E3, a versão nova (EQ-6):** a **v38** (a v35 com a F2, o ovo de um pet) e a **v39** (a v37 com a F2, o grupo). O `VERSAO_PET` é 38 e o
`VERSAO_GRUPO` é 39. O ajuste vem da versão (o replay pelo log refaz a vida), a `BITS_V2` vale para as duas, e os pets das versões de antes
saem byte a byte. Os números da F2 ficam DECIDIDOS no `config.py`.

**Os testes:** o `npm run tipos`; o vitest inteiro com `--maxWorkers=4` (191 arquivos, 1 896 testes, 3 pulados); os pytest tocados (266 de 266); o e2e inteiro (143 de 143). O teste novo `test/equilibrio_cuidado_e3.test.ts` confere que a v38 e a v39 nascem com as chaves ligadas e a v35 e a v37 não, o replay das duas pelo log e que, na bancada, a v38 refaz a vida da v35 com a F2 ligada (e a v39 a da v37).

**Para o Matheus:** as propostas do E1 seguem abertas com os números da validação ao lado (D-EQ1-6, a régua da M-A1; D-EQ1-7, a da M-C1;
D-EQ1-8, uma fonte de Bits que pague o cuidado bom); e se a diferença do grupo entre a v36 e a v37 (a CO7) pede uma medida própria
(D-EQ2-1). Os desvios são os D-EQ2-1 a D-EQ2-10 (`docs/registro/2026-11.md`).
