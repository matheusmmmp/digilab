# Plano de análise — V2/V3: a competição entre as regras urgentes (V3-3/V3-4)

Data: 2026-10-21. Status: **DECIDIDO** (as decisões PC-1 a PC-6, seção 12, DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação). Tarefa: `docs/TAREFA_V2_V3_COMPETICAO.md`
(as CR-1 a CR-7 DECIDIDAS em 2026-10-21; a etapa 0, #383; o código, etapas 1 e 2). Commitado antes de qualquer vida nas faixas 58101…58505
e 59101…59505.

**Os números de contexto** (só para desenhar; nenhum entra como evidência): `artifacts_v2_v3/competicao_etapa0.json`, as 20 vidas do E0 nas
sementes dos testes.

## 1. A pergunta e as predições

**A pergunta (CR-5):** abrir a disputa entre as regras urgentes que valem faz o pet sem mundo cuidar melhor do próprio corpo? A comparação
é contra o A (R0), e a mesma abertura sem aprender (R1-congelado) é o controle de mecanismo.

**As predições** (registradas agora):
- **V3-P1 (corrigida, descritiva):** a fração de decisões forçadas cai de cerca de 55% no R0 para cerca de 38% no R1. A etapa 0 deu 37,9%
  sobre a vida do R0; a do R1 sai do piloto. O 2,2% do E0 não vale para a forma decidida.
- **V3-P2 (o primário):** o `D_FE` do R1 é menor que o do R0.
- **V3-P4 (o mecanismo):** o R1 tem o `D_FE` menor que o R1-congelado, ou seja, o aprendido usa a abertura.
- **A segurança:** o R1 não piora a saúde nem a privação contra o R0, além das margens de não inferioridade.

**O que a etapa 0 já diz sobre o tamanho** (só contexto):
- a disputa abre quase só no relapso (37% das decisões) e no aleatório (32%); no atencioso e no incoerente, menos de 0,5%;
- no κ = 16, a abertura muda a ação em cerca de 9% das abertas e ensina 15,6% a mais do que o A ensina hoje.
- **Um efeito pequeno é o esperado.** Um empate não diz que a abertura é inútil: diz que, com o instinto forte, ela não move a homeostase
  em 14 dias.

## 2. O mundo, o dono e o cérebro

- **O mundo do v11** (CR-4): a `bancada_v11` (`experiments/exportar_gabarito_lobos.py`), o corpo químico com os drives novos e os gestos
  (o regime `corpo`, o ponto (2, 1) do adendo 4), o mundo `padrao`, 14 dias, 16 interações do dono por dia.
- **Os donos:** os quatro da v1 (atencioso, relapso, aleatório e incoerente). Cada um é uma célula.
- **O cérebro:** o A v11 (o ponto T3), com `ConfigCompeticao` ligada ou desligada pela `Bancada.cfg_competicao`, e o κ = 16 (CR-2).
- **Nada se calibra** (seção 6).

## 3. Os braços

| braço | o que é na bancada | papel |
|---|---|---|
| **R0** | `P1-c-tapa`, a chave desligada (o A v11) | o primário (contra o R1) |
| **R1** | `P1-c-tapa`, a chave ligada | o primário |
| **R1-cong** | `P0-c-tapa` (o mesmo corpo e o mesmo dono, o aprendizado desligado), a chave ligada | o secundário de mecanismo |
| **P0** | `P0-c-tapa`, a chave desligada (o instinto) | a margem (seção 7) e o descritivo |

- **Todos em malha fechada:** o dono reage ao que o pet faz.
- **Vidas por unidade:** 4 braços × 4 donos = **16**.

## 4. Unidade, pareamento e células

- **Unidade:** a semente de `unidades_derivadas(bases, K, prefixo="competicao")`. O prefixo é novo, e as unidades não colidem com as do E0
  nem com as do corpo.
- **Célula:** o dono (4).
- **Pareamento:** por unidade e dono. O dono e o mundo têm rng própria, e trocar o cérebro não muda o mundo (CLAUDE.md).
- **A estatística por unidade (PC-1):** a média das 4 células da diferença entre braços.
  - **Uma propriedade conta a favor:** numa vida em que nenhuma decisão abre, a vida do R1 é a do R0 bit a bit (o G-R1-UMA-REGRA), e a
    diferença é zero exato. Ela dilui a média, mas não acrescenta variância. Numa vida com poucas aberturas, as duas vidas só divergem a
    partir da primeira.

## 5. As medidas

**O primário: o `D_FE`** dos dias 8 a 14 (`digilab/metrics.py`, `deficit_fome_energia`, `JANELA_8_14`).

**A segurança, por não inferioridade (CR-5):**
- **a privação:** 1 − a fração das decisões fora de privação nos dias 8 a 14, pela `Estado.em_privacao` (a fome, a higiene ou a energia
  abaixo de 0,15). É a medida do plano do corpo (seção 5.2). A energia cobre o sono;
- **a saúde média** nos dias 8 a 14, a mesma do plano do corpo.

**Os descritivos (sem gate), todos por braço, por dono e por dia:**

| medida | definição |
|---|---|
| as forçadas | a fração das decisões com um candidato só (a V3-P1) |
| as abertas | a fração das decisões com `competicao` no motivo |
| quem decidiu | nas abertas, a fração com `abertura_decidiu` e com `aprendido_decidiu` |
| as ações nas abertas | a fração de cada ação, contra a do instinto |
| a exaustão | a fração das decisões com a energia abaixo de 0,25 (a condição do `sono_exaustao`) |
| os pesos | as tabelas das regras urgentes no fim de cada dia |
| o E0 | a sonda contrafactual "o aprendido mudou", por regra e por dia |
| o custo | s de CPU por vida |

- **As medidas que faltam no código** entram em `digilab/metrics.py`, com teste, antes do piloto: as abertas, quem decidiu e a exaustão.
  A privação e a saúde já existem na bancada do corpo.

## 6. A calibração

**Nada se calibra.**
- O κ = 16 vem da regra da CR-2 (a etapa 0), sem desfecho.
- O resto é o v11.

**O piloto do N** roda na faixa 58101…58505, com K = 4 por base (20 unidades), nos 4 braços e nos 4 donos: 320 vidas. Serve para:
- a margem (seção 7);
- o N (seção 7);
- a fração de abertas no R1 (a premissa G-ABRE);
- o custo.

Os números dele não entram como evidência.

## 7. As margens e o N

**A margem do primário (PC-2): `Δ_R1` = ½ × [`D_FE`(P0) − `D_FE`(R0)] no piloto,** a metade do que o aprendiz de hoje ganha sobre o
instinto em `D_FE`.
- **Não lê nenhum dado do R1 nem do R1-cong.**
- **Se o R0 não ganha do P0 no piloto** (a diferença ≤ 0,001), não há escala para a margem, e o plano volta ao Matheus antes da validação.

**As margens da segurança (PC-3), pela convenção do plano do corpo** (adendo 4):
- `Δ_priv` = ¼ da privação média do P0 no piloto;
- `Δ_saude` = ¼ de (1 − a saúde média do P0) no piloto.

**O N:** o menor K, de 4 a 10 por base, com poder simulado ≥ 0,8 para o primário no `Δ_R1`.
- **O método:** o da A1.9. Um bootstrap das diferenças R0 − R1 por unidade do piloto, centradas e deslocadas para `Δ_R1`, com 2.000
  réplicas por K, o teste unilateral a 0,025 e a semente 4242.
- **Os secundários:** o poder deles sai só como relato.
- **Se nem K = 10 chega a 0,8,** a validação roda com 10, e o poder sai declarado.

**O adendo 1** guarda as margens, o K, o poder, a G-ABRE do piloto e o custo, num commit antes da validação.

**O custo esperado:** uma vida do v11 de 14 dias leva cerca de 2 s com o replay (o gabarito da etapa 0). O piloto, 320 vidas, fica em minutos; a
validação com K = 10, 800 vidas, também.

## 8. A validação (uma vez)

- **As bases:** a faixa 59101…59505, com o K do adendo, nos 4 braços e nos 4 donos.
- **O replay:** toda vida é rejogada do disco e comparada bit a bit (G1). Uma divergência para tudo.
- **Os gates de mecanismo** falham alto em toda vida:
  - com a chave desligada, nenhuma decisão tem `competicao`;
  - com a chave ligada, o `sono_exaustao` é sempre forçado;
  - o R1-cong fica com os pesos no prior.
- **O bootstrap:** sobre as unidades, agrupado por base, com 10.000 reamostragens e a semente 4242. O IC95 é o primário; o IC90 serve só
  para a equivalência e para o rótulo "abaixo de Δ".

## 9. Gates e regra de decisão

**A premissa:**

| premissa | regra | se falha |
|---|---|---|
| **G-ABRE** | a fração das decisões abertas no R1, média por unidade: limite inferior do IC95 > 0,05 (PROPOSTO, PC-4) | o G-R1 é **inconclusivo por premissa**: a disputa quase não aconteceu |

**Os contrastes:**

| gate | contraste (por unidade, média das 4 células) | regra | papel |
|---|---|---|---|
| **G-R1** | `D_FE`(R0) − `D_FE`(R1) | as categorias abaixo | **primário** |
| G-R1-CONG | `D_FE`(R1-cong) − `D_FE`(R1) | limite inferior do IC95 > 0, Holm | secundário: o aprendido usa a abertura (V3-P4) |
| G-NI-PRIV | privação(R1) − privação(R0) | limite superior do IC95 < `Δ_priv`, Holm | segurança, não inferioridade |
| G-NI-SAUDE | saúde(R0) − saúde(R1) | limite superior do IC95 < `Δ_saude`, Holm | segurança, não inferioridade |

**As categorias do G-R1,** exclusivas e lidas nesta ordem (a do PR #196):
1. **a disputa ajuda:** o limite inferior do IC95 > 0. Se o limite superior do IC90 < `Δ_R1`, leva o rótulo **"abaixo de Δ"**;
2. **a disputa atrapalha:** o limite superior do IC95 < 0;
3. **equivalente:** o IC90 dentro de ±`Δ_R1`;
4. **inconclusivo:** o resto.

**O Holm** cobre {G-R1-CONG, G-NI-PRIV, G-NI-SAUDE}, com α = 0,05. O G-R1 é único e não entra.

**A leitura:**

| G-R1 | G-R1-CONG | segurança | leitura |
|---|---|---|---|
| ajuda | passa | passa | **a disputa ajuda, e o aprendido usa a abertura** |
| ajuda | não passa | passa | o ganho vem de abrir, não de aprender; o instinto aberto já basta |
| ajuda | qualquer | falha | **o pet melhora num lado e piora no outro:** registrado como está, sem a palavra "ajuda" sozinha |
| equivalente | qualquer | qualquer | com o instinto forte, a abertura não move a homeostase em 14 dias |
| atrapalha | qualquer | qualquer | registrado; os descritivos dizem onde (as ações nas abertas, a exaustão) |
| inconclusivo | — | — | registrado com o poder |

- **Por dono, só descritivo.** O relapso e o aleatório, onde a disputa abre, ficam ao lado, sem gate. Um efeito só neles é leitura, não
  resultado.

## 10. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **O efeito pequeno** (a abertura muda ~9% das abertas, e as abertas são ~17% das decisões) | o poder do piloto e o rótulo "abaixo de Δ"; o empate lido como "não move em 14 dias" |
| R-2 | **A margem sem escala:** o R0 pode não ganhar do P0 em `D_FE` neste mundo | a regra da seção 7: o plano volta ao Matheus |
| R-3 | **O pet dorme menos** e parece melhor por outro lado | a privação e a saúde por não inferioridade, mais a exaustão descritiva |
| R-4 | **A diluição pelos donos que cuidam** | o pareamento faz a diferença ser zero exato nas vidas em que nada abre (seção 4) |
| R-5 | **A tentação pós hoc por dono** | por dono, só descritivo |

## 11. Sementes

| uso | faixa | bases |
|---|---|---|
| piloto do N | **58101…58505** | 58101, 58202, 58303, 58404, 58505 (K = 4) |
| validação | **59101…59505** | 59101, 59202, 59303, 59404, 59505 (K do adendo) |

- As duas faixas já estão em `experiments/bancada/faixas.py` (CR-6, #383).
- O prefixo é `"competicao"`.

## 12. Decisões do Matheus

**DECIDIDAS em 2026-10-21: PC-1 a PC-6, todas como recomendado** (a coluna "recomendação" é o que vale). Os números delas
(o 0,05 da G-ABRE, o ½ e o ¼ das margens) continuam SEM FONTE.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **PC-1** (DECIDIDA) | a estatística do primário | **a média das 4 células (donos)**, com a margem na mesma escala. Numa vida em que nada abre, a diferença é zero exato e não acrescenta variância | só no relapso e no aleatório: escolher os donos depois de ver onde a disputa abre (na etapa 0, nas sementes dos testes) é escolher o recorte pelo dado; fica descritivo |
| **PC-2** (DECIDIDA) | a margem do primário | **½ × [`D_FE`(P0) − `D_FE`(R0)] no piloto**, sem ler o R1 | uma margem fixa sem escala neste mundo: sem referência, ela vira arbítrio; ler o R1 no piloto para a margem é calibrar pelo resultado |
| **PC-3** (DECIDIDA) | as margens da segurança | **¼ da privação do P0 e ¼ de (1 − saúde do P0) no piloto**, a convenção do plano do corpo | mais frouxas: aceitar um pet bem pior de cuidar como "não inferior"; mais apertadas: a segurança vira o gate mais difícil e esconde o primário |
| **PC-4** (DECIDIDA) | o limiar da G-ABRE | **0,05** do limite inferior do IC95 da fração de abertas no R1 | sem premissa: um empate seria lido como "a disputa não ajuda" mesmo se ela quase não acontecesse |
| **PC-5** (DECIDIDA) | o R1-congelado | **`P0-c-tapa` com a chave** (o mesmo corpo e o mesmo dono, sem aprender) | o `P0` comum: outro corpo, e o contraste mediria o corpo, não o aprendizado |
| **PC-6** (DECIDIDA) | o horizonte | **14 dias, os do E0 e do v11** | mais longo: mais tempo para as tabelas das regras forçadas aprenderem, mas outro mundo, sem o E0 de referência e com o metabolismo em aberto |

## 13. Artefatos e reprodução

- `artifacts_v2_v3_competicao/piloto/` e `.../validacao/`: as medidas por vida, o `meta.json` (o sha do pacote, a config, as sementes) e o
  resumo. As vidas ficam fora do git, e os artefatos ficam num commit próprio.
- **O orquestrador** `experiments/run_v2_competicao.py` e a config em `experiments/configs/v2_competicao/` são o código da etapa 4, num PR
  antes do piloto, com a fumaça nas sementes dos testes.
