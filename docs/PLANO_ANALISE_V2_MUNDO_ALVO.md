# Plano de análise — V2: o mundo físico com o alvo aprendido (aprender para onde ir ajuda a procurar?)

Status (2026-10-13): **PROPOSTO**, registrado **antes de qualquer run**. **PMA-1 a PMA-9 DECIDIDAS pelo Matheus em 2026-10-13, todas
pela recomendação** (seção 13). Este plano segue o resultado negativo da validação do mundo físico (`docs/RESULTADO_V2_VALIDACAO_MUNDO.md`,
#285) e herda dele o mundo, as medidas e as regras, salvo onde diz o contrário.

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- O que não está aqui é descritivo pós hoc.
- Nada se ajusta olhando a validação, que roda uma vez só.
- Um gate que falha é registrado e não para a V2 (decisão do Matheus de 2026-10-01).
- **Nenhuma alegação de novidade.** Aprender a escolher para onde ir pela consequência é aprendizado por reforço comum. O que se testa é se
  **este** cérebro, com **este** gancho, procura melhor **neste** mundo.

## 1. A pergunta

**Aprender para onde ir ajuda a procurar?** O mesmo P1 da validação do mundo, agora com o alvo aprendido ligado
(`ConfigLobos.alvo_aprendido`, #255), sustenta fome e energia melhor que o P1 com os alvos padrão do motor?

**O ponto de partida** (`artifacts_v2_mundo/validacao/resultado.json`):
- **G-MUNDO passou:** explorar compensa para o instinto (P0z − P0 em `D_FE` +0,0105 [+0,0048; +0,0159]);
- **o P1 perdeu do instinto:** P0 − P1 em `D_FE` −0,0097 [−0,0149; −0,0046], e a perda aparece também com o cuidado fixo (G-MF2r
  −0,0088 [−0,0123; −0,0051]);
- **o P1 fica muito mais em cada mancha** (352 min contra 191 do P0) e visita menos (19,3 contra 26,2 por vida).

**Por que o alvo.** No J1 o P1 aprendeu **quando** explorar, comer e brincar, mas ia sempre ao alvo padrão do motor (seção 3 do plano do
mundo). Os descritivos sugerem que ele aprendeu a ficar onde a comida estava (leitura, não teste). O alvo aprendido dá ao P1 a escolha de
**para onde** ir, entre as classes que o motor oferece:
- **comer:** `comida`, `comida_podre`, `cheiro` e `continuar`;
- **explorar:** `cheiro`, `vagar`, `casa` e `continuar`;
- **brincar:** `bola` e `continuar`.

Ele aprende pela mesma consequência (o crédito do `consequencia_mundo`), com o mesmo sinal da decisão.

**O que este plano não resolve: o crédito entre decisões (R-1 do plano do mundo).** Com a janela imediata, a decisão que só anda registra o
gasto, e o ganho fica com a que come. O alvo aprendido herda isso. Fica registrado como alternativa futura (seção 11).

**As predições** (sentido fixado agora):

| # | predição | contraste | papel |
|---|---|---|---|
| PA-0 | explorar ainda compensa para o instinto | P0z − P0 em `D_FE` > 0 | premissa (G-MUNDO, de novo) |
| PA-U | o P1 com o alvo usa o que aprendeu: o aprendido muda o alvo numa fração das decisões | a fração, no P1-alvo | premissa de mecanismo (G-USO) |
| PA-1 | com o dono reagindo, o P1 com o alvo tem déficit menor que o P1 com os alvos padrão | **P1 − P1-alvo** em `D_FE` > 0 | **primária** (G-ALVO) |
| PA-2 | com o mesmo cuidado, idem | P1^ac − P1-alvo^ac em `D_FE` > 0 | secundária (Holm) |
| PA-3 | o P1 com o alvo deixa de perder do instinto e passa a ganhar | P0 − P1-alvo em `D_FE` > 0 | secundária (Holm) |
| PA-4 | com o alvo, a permanência sobe mais com o custo de viagem que no P1 | inclinação do P1-alvo − a do P1 > 0 | secundária (Holm) |
| PA-5 | com o alvo, a permanência sobe mais com o layout afastado que no P1 | diferença em diferença, P1-alvo contra P1 | secundária (Holm) |

## 2. O mundo, o dono e o cérebro

**O mundo é o da validação do mundo, sem mudança:**
- o `MotorMundo`, o layout padrão e o `m` = 1 (A1.9);
- as frutas "iguais" (PMF-7);
- 14 dias, orçamento de 224, morte desligada;
- os 4 donos da v1 só com o cuidado (PMF-3), com o lugar como fator fixo (comedouro, perto, longe; PMF-4): 12 células;
- o motor com a ordem fixa no desempate do cheiro, como na validação (PMA-8).

**O corpo fica desligado** (PMA-4), como no J1.

**O cérebro é o P1 da validação do mundo:** o A na montagem completa, ponto T3, ganho 4 e canais ligados (`memoria_ganho` 512 não age
no mundo físico, onde a memória não existe). Sem recalibrar (M10).

**O P1-alvo** é esse mesmo P1 com `ConfigLobos.alvo_aprendido` ligada e o `w0_alvo` padrão (S/16, PROPOSTO, SEM FONTE; PMA-3). Não
recalibra nada. Pela contagem do #255, o cérebro no mundo físico sem o corpo, com o alvo, tem 792 pesos: abaixo do padrão de 1000 da
TP-1, sem teto declarado.

## 3. Os braços

Todos em malha fechada, salvo os dois acoplados, que são comparados só entre si (a regra da PMF-2r).

| braço | política | cuidado | papel |
|---|---|---|---|
| **P0** | o instinto do mundo, com os alvos padrão | o dono reage | premissa e secundário (PA-3) |
| **P0z** | o P0 em `sem_explorar` | o dono reage | premissa (G-MUNDO) e **fonte dos acoplados** |
| **P1** | o P1 da validação do mundo, com os alvos padrão | o dono reage | **primário** |
| **P1-alvo** | o mesmo P1, com o alvo aprendido | o dono reage | **primário** |
| **P1^ac** | o P1 | acoplado ao P0z da mesma célula | secundário (PA-2) |
| **P1-alvo^ac** | o P1-alvo | acoplado ao mesmo P0z | secundário (PA-2) |
| **P1 afastado, P1-alvo afastado** | os dois, no `LAYOUT_MUNDO_AFASTADO` | o dono reage | secundário (PA-5); o primeiro bloco a sair se o custo passar do teto (PMA-6) |

**Por que o primário é P1 − P1-alvo, e não P0 − P1-alvo** (PMA-1): os dois braços têm o mesmo cérebro, o mesmo ponto e o mesmo sinal, e
diferem só na chave. O contraste isola "aprender para onde ir". O P0 − P1-alvo responde a outra pergunta ("o aprendiz passa o instinto?"),
que fica como secundária.

**Vidas por unidade:** 6 braços × 12 células = 72 em malha fechada e acoplados, mais 24 do layout afastado: **96**.

## 4. Unidade, pareamento e células

- **Unidade:** a semente de `unidades_derivadas(bases, K, prefixo="mundo")`, o prefixo do plano do mundo (o mundo é o mesmo).
- **Célula:** dono × lugar, 12.
- **Pareamento:** por unidade e célula. As quedas de fruta são as mesmas em todos os braços (G-NUMS do mundo).
- **Estatística por unidade:** a média das 12 células da diferença entre braços.

## 5. As medidas

**A primária: o `D_FE`** dos dias 8 a 14, a mesma definição da seção 5.1 do plano do mundo (`metrics.deficit_fome_energia`).

**As secundárias:** o `D_FE` nos contrastes PA-2 e PA-3; a inclinação da permanência sobre o custo de viagem (G-PERM da A1.8, agora P1-alvo
contra P1); a permanência média no layout afastado contra o padrão (G-DIST da A1.8, idem).

**O uso do alvo aprendido (G-USO).** É a fração das decisões com alvo, nos dias 8 a 14 do P1-alvo, em que o alvo escolhido difere do que
a tabela do prior (todas as classes em `w0_alvo`, mais 1 na classe do padrão) daria **com o mesmo u**. Isola o que foi aprendido do sorteio
que o prior já faz entre as classes.
- **O que falta no código:** o motivo do alvo guarda as classes, a do padrão, a escolhida e os pesos, mas não o `u`. O B põe o `u` no
  motivo; o D faz a sonda. Os dois atrás da chave, com o G2.

**Os descritivos (sem gate):**

| medida | definição |
|---|---|
| as classes escolhidas | a fração de cada classe, por ação e por dia, no P1-alvo |
| os pesos do alvo | a tabela no fim de cada dia, por regra e ação |
| o forrageio | as visitas por vida, a permanência média, o deslocamento por região, os consumos (os do resultado do mundo) |
| a privação | 1 − `fracao_fora_de_privacao`, nos dias 8 a 14 (o G-MF3r do mundo saiu subpotenciado e aqui fica descritivo) |
| a taxa no abandono | a medida 2 da A1.8 |
| G-OPORT | a inclinação sobre a taxa recente, P1-alvo − P1: só descritiva (no mundo não passou e não tem Δ) |
| por dono e por lugar | `D_FE` de P1 − P1-alvo por dono e por lugar |
| o custo | s de CPU por vida, por braço |

## 6. A calibração

**O mundo não se recalibra.** O `m` = 1 e o `Δ_MF` são os da A1.9 do plano do mundo.

**O alvo não se calibra** (PMA-3). O `w0_alvo` fica em S/16, e o passo é o do cérebro. Calibrar o `w0_alvo` pediria uma regra que não lê o
primário, e o único candidato natural (a fração do G-USO numa faixa) puxaria o alvo para "usar mais", o que não é a pergunta.

**O piloto do N.** Na faixa de piloto (seção 12), os braços P0, P0z, P1, P1-alvo, P1^ac e P1-alvo^ac nas 12 células, sem o layout afastado:
72 vidas por unidade, 20 unidades. Serve só para o N, para o G-USO no piloto e para o custo. Os números dele não entram como evidência.

## 7. A margem e o N

**A margem: o `Δ_MF` do plano do mundo, reaproveitado** (PMA-2): `Δ_MF` = 0,007675785900293976, metade do que explorar vale para o
instinto (A1.9).

**Por que cabe reaproveitar:**
- **a mesma escala e o mesmo mundo:** o `D_FE` dos dias 8 a 14, no mesmo motor, no mesmo `m` e com as mesmas células;
- **a mesma pergunta de fundo:** "aprender ajuda a procurar" se mede contra o valor da procura para o instinto. Um ganho do alvo de metade
  desse valor é o mínimo que interessa, pelo mesmo raciocínio que fixou o `Δ_MF`;
- **foi fixado antes de qualquer vida com o alvo:** veio só do P0 e do P0z da calibração do mundo. Não lê nenhum dado do P1-alvo.
- **O que não cabe:** o `Δ_MF` não diz nada da variância de P1 − P1-alvo. Por isso o N sai de um piloto novo.
- **Para leitura, sem mudar a margem:** a perda do P1 na validação (−0,0097) é maior que o `Δ_MF`. Se o alvo recuperar a perda inteira, o
  ganho passa da margem.

**O N:** o menor K, de 4 a 10 por base, com poder simulado ≥ 0,8 para detectar `Δ_MF` no G-ALVO.
- **O método:** o do A1.9. Um bootstrap das diferenças P1 − P1-alvo por unidade do piloto, centradas e deslocadas para `Δ_MF`, com 2.000
  réplicas por K e o teste t unilateral a 0,025, semente 4242.
- **Os secundários:** o poder do PA-2 e do PA-3 no N escolhido sai só como relato; abaixo de 0,5, o gate é lido como subpotenciado. O PA-4 e
  o PA-5 não têm Δ nem poder, como no plano do mundo.
- **Se nem K = 10 chega a 0,8,** a validação roda com 10, e o poder sai declarado.

**O adendo 1:** o K, o poder, o G-USO do piloto e o custo entram num commit antes da validação.

**O custo esperado,** antes do piloto (pela CPU por vida da validação do mundo, `docs/RESULTADO_V2_VALIDACAO_MUNDO.md`, seção 7; o
P1-alvo pelo custo do P1, sem medida própria):
- **o piloto:** 1.440 vidas, ~2,9 h de CPU, ~0,4 h de parede com 8 processos;
- **a validação com K = 8:** 3.840 vidas, ~8,1 h de CPU, ~1,0 h com 8 processos;
- **com K = 10:** 4.800 vidas, ~10,1 h de CPU, ~1,3 h com 8 processos.

## 8. A validação (uma vez)

- **As bases:** a faixa de validação (seção 12), com o K do adendo, nos 8 braços e nas 12 células.
- **O replay:** toda vida é rejogada do disco e comparada bit a bit (G1). Divergência para tudo.
- **O bootstrap:** sobre as unidades, com 10.000 reamostragens e a semente 4242. O IC95 é o primário; o IC90 serve só para a equivalência e
  para o rótulo "abaixo de Δ".

## 9. Gates e regra de decisão

**As premissas:**

| premissa | regra | se falha |
|---|---|---|
| **G-MUNDO** | P0z − P0 em `D_FE`: limite inferior do IC95 > 0 | o G-ALVO é **inconclusivo por premissa**: explorar não compensou nesta run |
| **G-USO** | a fração do G-USO no P1-alvo: limite inferior do IC95 > 0,05 (PROPOSTO; PMA-5) | um G-ALVO equivalente ou inconclusivo é lido como **"o alvo não foi usado"**, e não como "aprender para onde ir não ajuda". Um G-ALVO que ganha ou perde fica com a categoria e com o aviso |

**Os contrastes:**

| gate | contraste (por unidade, média das 12 células) | regra | papel |
|---|---|---|---|
| **G-ALVO** | P1 − P1-alvo em `D_FE` | as categorias abaixo | **primário** |
| G-ALVO-AC | P1^ac − P1-alvo^ac em `D_FE` | limite inferior do IC95 > 0, Holm | secundário |
| G-INSTINTO | P0 − P1-alvo em `D_FE` | limite inferior do IC95 > 0, Holm | secundário |
| G-PERM-A | inclinação da permanência sobre o custo de viagem, P1-alvo − P1 | limite inferior do IC95 > 0, Holm | secundário, sem Δ nem poder |
| G-DIST-A | [P1-alvo(afastado) − P1-alvo(padrão)] − [P1(afastado) − P1(padrão)] na permanência média | limite inferior do IC95 > 0, Holm | secundário, sem Δ nem poder |

**As categorias do G-ALVO** são exclusivas e lidas nesta ordem (a ordem do PR #196 e da seção 8 do plano do mundo):
1. **o alvo ajuda:** o limite inferior do IC95 > 0. Se o limite superior do IC90 < `Δ_MF`, leva o rótulo **"abaixo de Δ"**;
2. **o alvo atrapalha:** o limite superior do IC95 < 0;
3. **equivalente:** o IC90 dentro de ±`Δ_MF`;
4. **inconclusivo:** o resto.

**O Holm** cobre {G-ALVO-AC, G-INSTINTO, G-PERM-A, G-DIST-A}, com α = 0,05. O G-ALVO é único e não entra. Sem o bloco do layout afastado
(PMA-6), o G-DIST-A sai como "não rodado" e o Holm fica com três.

**A leitura**, com o G-MUNDO passando:

| G-ALVO | G-ALVO-AC | leitura |
|---|---|---|
| ajuda | passa | **aprender para onde ir ajuda a procurar, e o ganho é do pet:** aparece também com o cuidado fixo. O G-INSTINTO diz se basta para passar o instinto |
| ajuda | não passa | o ganho pode vir do dono reagindo ao que o P1-alvo faz; fica registrado ao lado, sem trocar a categoria (a segunda linha da A1.5) |
| equivalente ou inconclusivo, com o G-USO passando | qualquer | **o pet usou o alvo e não procurou melhor.** Aponta para o crédito entre decisões (seção 11) e para o pet que planeja (J5) |
| equivalente ou inconclusivo, com o G-USO falhando | qualquer | **o alvo não foi usado:** o aprendiz não tirou o alvo do prior. Não diz nada sobre aprender para onde ir |
| atrapalha | qualquer | registrado. Os descritivos das classes dizem para onde o alvo levou o pet |

- **Com o G-MUNDO falhando,** o P1 e o P1-alvo não são lidos.
- **O J1 não muda.** O resultado da validação do mundo fica como está: este plano é outro experimento, com outras unidades.

## 10. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **O crédito entre decisões** continua: o alvo longe é pago na decisão que anda, e o ganho fica com a que come | registrado; a alternativa está na seção 11. O descritivo das classes mostra se o alvo aprendeu a evitar o longe |
| R-2 | **O alvo não sai do prior** (`w0_alvo` pequeno e o padrão com +1) | o G-USO separa "não usou" de "usou e não ajudou" |
| R-3 | **O desempate do cheiro** (o achado do #232): a classe `cheiro` herda o viés da ordem fixa | igual nos dois braços do primário; o motor fica o da validação (PMA-8) |
| R-4 | **O dono domina** nos donos que cuidam (no J1, a perda veio do atencioso e do incoerente) | o primário é a média das 12 células; por dono e lugar só descritivo |
| R-5 | **O acoplado no espaço:** o cuidado do P0z cai perto de um pet que fica em casa | os dois acoplados recebem o mesmo registro; o contraste é só entre eles |
| R-6 | **A tentação pós hoc** com as classes e os pesos | só os gates da seção 9 decidem |
| R-7 | **O custo** sobe para 96 vidas por unidade | o bloco do afastado é o primeiro a sair (PMA-6); o custo do piloto vai no adendo |

## 11. A alternativa registrada: o crédito entre decisões (R-1 do plano do mundo)

**O problema.** Com a janela imediata, cada decisão recebe só a mudança do próprio passo. Uma ida longa se parte em várias decisões: as
primeiras pagam o andar e a última ganha a comida. O P1 aprende a evitar idas longas mesmo quando compensam, com o alvo padrão ou com o
aprendido.

**As formas que existem no código ou no desenho:**
- **o traço de elegibilidade** dos lobos (`ConfigLobos.traco_decisoes`/`traco_fator`, da revisão do aprendiz). Na revisão, piorou o G_ap
  do P1 nas frutas (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`, o ponto J3: −0,027 [−0,041; −0,014]). Nunca rodou no mundo físico. Hoje os canais recusam o traço
  (CANAIS-REFORCO: `traco_decisoes` > 0 falha alto), então ligar o traço no P1 da montagem completa pede trabalho no cérebro;
- **o crédito por ida:** creditar à decisão que escolheu o alvo o saldo da ida inteira, até chegar ou desistir. É desenho novo, SEM FONTE;
- **o planejador do J5,** que avalia o alvo antes de andar.

**Por que não entra agora:** cada forma muda o sinal do P1, e a pergunta deste plano é só o alvo, com o sinal de sempre. Juntar os dois
tiraria a leitura de cada um. **Entra por plano próprio** se o G-ALVO sair equivalente ou inconclusivo com o G-USO passando (a terceira
linha da leitura).

## 12. Sementes

| uso | faixa | bases |
|---|---|---|
| piloto do N | **47101…47505** | 47101, 47202, 47303, 47404, 47505 (K = 4) |
| validação | **48101…48505** | 48101, 48202, 48303, 48404, 48505 (K do adendo) |

- **O prefixo de unidades:** `"mundo"`, o mesmo do plano do mundo (o mundo é o mesmo; as faixas novas não colidem com as dele).
- **Conferências em 2026-10-13,** no `origin/main` (`067e19b`) e nos branches remotos:
  - as duas faixas estão fora de `FAIXAS_RESERVADAS` (a última é 44101…44505) e da `FAIXAS_QUEIMADAS`;
  - também ficam fora das faixas planejadas e ainda não registradas: 23101…27505 (`docs/LEITURA_PARCIAL_V2_FASE1.md`), 35101…36505
    (transferência e rejeição) e 45101…46505 (o J5, `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`);
  - `git grep -w` das bases em `.py`, `.md` e nas configs não acha uso, na `main` nem nos branches remotos.
- **O D registra** as faixas, com a fonte deste plano.

## 13. Decisões do Matheus

**DECIDIDAS em 2026-10-13: PMA-1 a PMA-9, todas como recomendado** (a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PMA-1 | O contraste primário | **P1 − P1-alvo** em `D_FE`, em malha fechada | P0 − P1-alvo: mistura "aprender para onde" com "aprender quando", que já perdeu do instinto, e um empate não diz qual das duas falhou |
| PMA-2 | A margem | **reaproveitar o `Δ_MF`** (seção 7) | uma margem nova do piloto: sairia de dados do P1-alvo e precisaria de uma regra sem dado de referência |
| PMA-3 | O que se calibra | **nada:** o mundo fica no `m` = 1, e o `w0_alvo` fica em S/16 | calibrar o `w0_alvo` pelo uso: puxa o alvo para "usar mais", e o primário fica ajustado a favor dele |
| PMA-4 | O corpo | **desligado,** como no J1 | ligado: o primário deixa de ser comparável com o J1, e os drives novos mexem no tempo livre dos dois braços |
| PMA-5 | O limiar do G-USO | **0,05** do limite inferior do IC95 | sem premissa de uso: um empate seria lido como "o alvo não ajuda" mesmo se o alvo nunca saiu do prior |
| PMA-6 | O bloco do layout afastado | **fica**, e é o primeiro a sair se o custo do piloto passar do teto de tempo | tirar já: o G-DIST-A, a previsão de forrageio mais direta para quem escolhe para onde ir, não roda |
| PMA-7 | As faixas | **47101…47505** (piloto) e **48101…48505** (validação), prefixo `mundo` | uma colisão tira o "novo" das unidades; reaproveitar a 32101…32505 repetiria as vidas do P0 e do P1 da validação do mundo |
| PMA-8 | O desempate do cheiro | **o motor da validação** (a ordem fixa) | trocar o motor antes: o P1 deste plano deixa de ser o do J1, e o desempate entra sem gate próprio |
| PMA-9 | O crédito entre decisões | **alternativa futura, por plano próprio** (seção 11), depois do G-ALVO | juntar agora: o sinal e o alvo mudam ao mesmo tempo, e nenhum dos dois fica lido |

## 14. Artefatos e reprodução

- **As pastas:** `artifacts_v2_mundo_alvo/piloto/` e `artifacts_v2_mundo_alvo/validacao/`. Cada uma traz `meta.json` (o sha256 de
  `mundo.py`, `config.py`, `lobos.py`, `engine.py`, do plano e da config) e os registros das vidas (fora do git).
- **As configs:** `experiments/configs/v2_mundo_alvo/{piloto,validacao}.json`, com o campo `"plano"`.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe, e o piloto recusa as sementes da validação.

**O que falta no código antes do piloto** (sem tarefa aberta; o coordenador distribui):
- **B:** o `u` do alvo no motivo, para a sonda do G-USO (atrás da chave, com o G2);
- **D:** o braço P1-alvo na bancada de vidas (hoje o alvo aprendido só é ligado na bancada do grupo), a sonda e a medida do G-USO, as
  configs e o orquestrador.

## Desvio D1 (2026-10-13, antes de qualquer run): o canal do humor da comida podre no P1-alvo

**O que apareceu.** Na fumaça do piloto (sementes dos testes), o P1-alvo escolheu a classe `comida_podre` e comeu uma fruta podre (humor
−0,1). Com os canais do J1 ligados e a `presenca_fruta_mundo` desligada, o canal do humor não tinha peso que lesse a fruta naquela decisão,
e o cérebro falhava alto (CANAIS-REFORCO). O P1 do J1 nunca chega a isso, porque o alvo padrão do motor não vai à comida podre.

**A decisão do Matheus (2026-10-13, a saída 1 do PR #292).** O alvo aprendido conta como leitor da comida no `_creditar_canais`: ele já
recebe o sinal inteiro da decisão (todos os canais), e o grupo da fruta fica sem peso a mexer, como em toda decisão do J1. É uma linha no
`lobos.py`, que só tira uma falha alta: nenhum crédito muda, e nenhuma vida que já rodava muda (os gabaritos, na suíte).

**O que não muda:** o P1 e o P1-alvo continuam diferindo só na chave do alvo (PMA-1); as classes da seção 1, a margem, o N, os gates e a
leitura ficam como estão. O desvio é do cérebro e foi registrado antes do piloto; nada foi ajustado olhando resultado.


## Adendo 1 (2026-10-13, antes da validação): o K, o poder, o G-USO do piloto e o custo

Piloto da seção 6, uma vez, nas bases 47101…47505 (K = 4, prefixo `mundo`, 20 unidades), com o código em `5b6e9b2` (árvore limpa) e o
desvio D1. Números de `artifacts_v2_mundo_alvo/piloto/` (`resultado.json`, `medidas.json`, `meta.json`; as vidas ficam fora do
git). **Fica congelado aqui; a validação (48101…48505) roda com este K.**

**O N: K = 4 por base, N = 20.** O poder simulado no G-ALVO (o bootstrap das diferenças P1 − P1-alvo por unidade do piloto, centradas e deslocadas para o `Δ_MF` = 0,007675785900293976, 2.000 réplicas por K, o
teste t unilateral a 0,025, semente 4242):

| K | **4** | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| poder | **0,920** | 0,973 | 0,992 | 0,997 | 0,998 | 1,000 | 1,000 |

**O poder dos secundários no N = 20, só relato** (com o `Δ_MF`; a 0,025 e a 0,0125, o primeiro passo do Holm com quatro):
- **G-ALVO-AC** (P1^ac − P1-alvo^ac): 0,963 a 0,025 e 0,931 a 0,0125;
- **G-INSTINTO** (P0 − P1-alvo): 0,406 a 0,025 e 0,306 a 0,0125: **subpotenciado** (abaixo de 0,5, seção 7);
- **G-PERM-A e G-DIST-A:** sem Δ nem poder (seção 7).

**O G-USO no piloto:** 0,0885 [+0,0806; +0,0970] (limiar 0,05; 94,9 decisões com alvo por vida nos
últimos sete dias, 0 células sem decisão). É do piloto: a premissa da validação é medida de novo lá.

**O custo** (CPU por vida, com a gravação, o replay do disco, a medição e, no P1-alvo, as medidas do alvo; Python 3.13.0, Windows):

| braço | P0 | P0z | P1 | P1-alvo | P1^ac | P1-alvo^ac |
|---|---|---|---|---|---|---|
| s por vida | 6,83 | 3,89 | 8,55 | 9,09 | 8,52 | 8,53 |

- **Este piloto:** 1440 vidas, 3,03 h de CPU, 19 min de parede com 10 processos.
- **A validação com K = 4:** 1920 vidas (96 por unidade, com o bloco afastado pelo custo do P1 e do P1-alvo no padrão), 4,2 h de CPU, ~0,4 h de parede com 10 processos. **O bloco afastado fica** (PMA-6): o custo cabe no teto.

**O piloto não é evidência** (seção 6). Só como relato, por unidade, a média das 12 células em `D_FE`:
- P1 − P1-alvo (G-ALVO): −0,0024 [−0,0068; +0,0023];
- G-MUNDO no piloto (P0z − P0): +0,0137 [+0,0063; +0,0206].
