# Gate I: o pet integrado (corpo químico, mundo, aprendizado na vida e replay no mesmo pet)

Status (2026-10-21): **as decisões GI-1 a GI-5 DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação** (seção 7). O Gate I é um
marco do `docs/ROADMAP_V2.md` (seção 8), **ainda não implementado**: a tarefa está em `docs/TAREFA_V2_GATE_I.md`, e o plano, em
`docs/PLANO_ANALISE_V2_GATE_I.md`, ambos PROPOSTOS. O desenho abaixo é a proposta original, só papel. É o pedido do Matheus de 2026-10-21, pelo Gerente: aumentar a chance de o cérebro, o corpo
químico, o aprendizado durante a vida e a genética convergirem para criaturas integradas, na direção da vida artificial que o Creatures
exemplifica. Nada aqui diz que a integração já existe.

**Regras deste documento:**
- Nenhum número novo, nenhuma semente, nenhuma faixa e nenhum gene novo. As medidas exatas do gate saem de um plano de análise próprio,
  antes de qualquer run.
- **O Creatures é direção, não prova.** Só se escreve "o Creatures faz X" quando X está nas frases da seção 1.1 de
  `docs/DEFINICOES_CORPO_V2.md` (Grand, Cliff e Malhotra 1997; Cliff e Grand 1999, pelos resumos). As fontes primárias verificadas tratam
  do Creatures e do ecossistema dos jogadores; **o Creatures 3 não tem fonte primária verificada no repositório**, e o manual dele é
  pista. Que o Creatures tenha integrado essas peças não diz que o Digilab vai integrá-las.
- **Nenhuma alegação de novidade.**

## 1. O que o gate confere

O Gate I confere se **o mesmo pet, numa configuração só e nas mesmas vidas:**
1. **recebe os sinais do corpo químico:** o cérebro lê o corpo só pelos receptores, e o sinal do corpo chega ao aprendizado;
2. **percebe e age num mundo:** escolhe entre os alvos que o mundo oferece pelo que vê, e as consequências do mundo chegam a ele;
3. **aprende durante a vida pelas consequências:** o comportamento muda com a experiência, contra um controle que não aprende dela;
4. **refaz a vida pelo log:** toda vida do gate se refaz bit a bit do log (o event sourcing de hoje), com o corpo, o mundo e o cérebro.

**O gate não confere:** a genética, a reprodução, o mundo 3D, o "pensar" (o R-7 do J5) nem o jogo web.

## 2. O que existe hoje, e onde cada peça já foi conferida

**As peças existem, e quase todas já rodaram juntas, mas nenhum gate exige as quatro no mesmo pet.** O mais perto disso são as vidas
da validação do J5 com o adendo 8 (#370):

| requisito | o que existe | onde foi conferido | o que falta para o gate |
|---|---|---|---|
| 1, o corpo | o corpo químico (o J2, `digilab/corpo.py`), o regime "química" nas vidas do J5 (PP-3 do plano do J5) | a G-RECEPTOR (`tests/test_corpo.py`), o G-SEM-DIRECAO (`tests/test_cheiro_orgao.py`) | nada de mecanismo. O plano diz como se mostra que o sinal do corpo chega ao aprendizado nas vidas do gate |
| 2, o mundo | o mundo físico 2D (o J1, `digilab/mundo.py`), com a visão em disco, os alvos e a consequência do mundo | o G-MUNDO do J1 (#285), os testes do mundo | é o mundo de hoje, com a posição absoluta (W-3, acesso privilegiado) e sem colisão |
| 3, o aprendizado | o cérebro A com o aprendizado (a L1, a E2) e, no J5, o planejador | **em parte:** o Gate C APROVADO EM PARTE (2026-10-21): o G-T1 passa (o planejador contra o hábito), e o G-T1-CONG não. No mundo, o aprendiz perde do instinto (o J1, #285) e o alvo aprendido atrapalha (#296) | um resultado validado de aprendizado pela consequência, com controle, **na configuração do gate** (GI-3) |
| 4, o replay | o log e o replay de hoje | o G1 em toda vida da validação do J5 (#370) e o G2 de cada chave | nada de mecanismo; o gate exige o G1 em toda vida dele |

**O que fica separado hoje:**
- **o jogo web:** o `lobos.ts` roda o cérebro A sem as chaves do mundo, das frutas e do plano, e o jogo não tem o mundo físico
  (`docs/TAREFA_V2_P4_CEREBRO_MUNDO.md`, seção 0);
- **a genética:** o genoma da V2 ainda é desenho (`docs/futuro/ecossistema_genetico.md`); nenhum pet das vidas da V2 nasce de um genoma
  que varie o corpo, o prior ou a plasticidade;
- **o contrato sensório-motor:** só no POC, em TS, com o cérebro de teste (o Gate B). A P4 o leva ao mundo do motor.

## 3. O gate (PROPOSTO)

**O nome:** Gate I, o pet integrado. A letra entra ao lado dos gates A a E do `docs/futuro/mundo_3d.md`, seção 7.

**A entrada:**
- **uma configuração única do pet,** nomeada e com o gabarito (a "linha de base integrada"): o corpo químico, o mundo físico, o cérebro com
  o aprendizado ligado e o dono. A escolha dela é a GI-2;
- **a decisão do cérebro** (GI-1);
- **um plano de análise** commitado antes da primeira vida, com o critério do aprendizado (GI-3), o controle, as premissas e as faixas.

**A saída** (todas nas mesmas vidas da mesma configuração):
- **I-CORPO:** a G-RECEPTOR e o G-SEM-DIRECAO passam; e o sinal do corpo aparece no aprendizado, pela medida do plano;
- **I-MUNDO:** as decisões com alvo escolhem entre os candidatos que o mundo oferece pela percepção, e as consequências do mundo chegam ao
  cérebro, pela medida do plano;
- **I-APRENDE:** o critério da GI-3 passa na validação, rodada uma vez;
- **I-REPLAY:** o G1 em toda vida do gate e o G2 de todas as chaves ligadas.

**A condição de falha:** se um dos quatro não passa, o gate fica **"medido, não passou"**, com o que falhou. Pela regra da V2, um gate
que falha não para a V2. Ele condiciona só o que depende dele (seção 4).

**A dependência:** o J2 (o corpo) e o J1 (o mundo) na `main`, já cumpridos; o Gate C, aprovado em parte; a GI-1 e a GI-2 decididas.

## 4. Onde entra, e por que no mundo 2D

- **Antes da genética que mede ou reproduz:** o G1 (a h²) e o G2 (a reprodução) do `ecossistema_genetico.md` pedem uma linha de base
  integrada. Sem ela, a h² mediria um pet que não junta as peças, e uma geração herdaria de um pet que não aprende no mundo.
- **O G0 pode vir antes,** porque é só infraestrutura (o genoma no log, o replay, o genoma vazio = a vida de hoje) e não mede nada.
- **Em paralelo à P4, sem depender dela:** os quatro requisitos se testam no mundo físico 2D de hoje.
  - **A P4 é integração sensório-motora:** ela troca a percepção e o andar pelo contrato, com o mesmo cérebro, corpo e protocolo do
    J5. Se a replicação do T1 passar, ela vale como uma evidência do I-APRENDE no mundo com o contrato, mas não fecha o Gate I sozinha:
    o critério dele é o da GI-3, na configuração da GI-2.
  - **O 3D não é pedido,** porque a vista não muda a ciência no arranjo V (W-1): a física e a percepção são as do motor.
- **Os limites de fazer no 2D:**
  - o pet sabe a própria posição (W-3);
  - a visão é um disco sem oclusão;
  - nada é sólido.
  
  "Percebe e age num mundo" vale para este mundo, e não para um corpo que só conhece o mundo pelos sensores. A P4 é o passo que tira o
  disco e o passo reto; a posição absoluta continua (W-3).

**Como o Gate I se relaciona com os gates que já existem:**

| gate | o que confere | a relação com o Gate I |
|---|---|---|
| A (o POC) | a viabilidade técnica da vista e da física | nenhuma: é técnica |
| B (o organismo corporificado) | o laço do contrato no POC, em TS, com o cérebro de teste | não conta: o cérebro não é o real, e não há aprendizado |
| C (o aprendizado demonstrável) | uma mudança de comportamento pela experiência, com plano e validação única | o I-APRENDE é um Gate C **na configuração do Gate I**. O Gate C de hoje (em parte) foi no mundo do J5, que é a candidata da GI-2 |
| a P4 (a replicação do T1 com o contrato) | o G-T1 no mundo com o contrato | uma evidência do I-APRENDE com outra percepção; não fecha o Gate I |
| G1 e G2 (o replay e a chave desligada) | o determinismo de cada vida | são o I-REPLAY |
| D (a variabilidade biológica, o G1 genético) | a h² do genoma | **depende do Gate I** (seção 4) |
| E (a reprodução, o G2 e o G3 genéticos) | herança e desenvolvimento | **depende do Gate I** e dos dois pets aprendendo (o J7) |

## 5. O cérebro: o A não é uma rede recorrente

- **O que o cérebro A é** (`digilab/policies/lobos.py`):
  - uma política aprendida, com pesos inteiros que pontuam os candidatos que o instinto propõe;
  - o peso efetivo é linear nas entradas, e a ação sai por um sorteio proporcional;
  - no J5, um termo do planejador soma ao peso de cada alvo.
- **O que ele não é:** a decisão é uma soma linear das entradas da decisão atual. O que passa de uma decisão a outra são os pesos
  aprendidos, as memórias nomeadas e, no J5, os modelos do mundo, e não um estado de rede que se realimenta. Não é uma rede neural
  recorrente modular, nem equivale à arquitetura que Cliff e Grand (1999) descrevem para o norn (uma rede recorrente
  e modular com aprendizado hebbiano, modulada pela bioquímica, pelo resumo). O "inspirado no Creatures" do `PLANO_V2_PESQUISA.md` (seção
  3) é inspiração de nome e de desenho, não equivalência.
- **O que o projeto já tentou:**
  - **o cérebro B** (`digilab/policies/cerebro_b.py`): uma célula recorrente de tempo contínuo (CfC) com ator e crítico. Saiu da
    comparação por "não aprende": a parte aprendida mudou menos de 1% das escolhas (`docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`);
  - **o cérebro C** (`digilab/policies/cerebro_c.py`): na comparação A × C (#197), empate nos dois critérios; pela regra do M6 o
    escolhido seria o C, por pouco, e o A ficou como o cérebro da web (rodada 15; `docs/PAINEL_V2.md`).
- **A decisão** é a GI-1 (seção 7), DECIDIDA em 2026-10-21: integrar tudo ao redor do A agora; uma rede recorrente ou outro modelo
  só como pergunta própria, com o modelo definido, depois do Gate I.

## 6. A genética: o escopo proposto e o que não está definido

- **O escopo já proposto** (`ecossistema_genetico.md`, seção 3.1, com a EG-2 e a EG-3 decididas), em codificação direta, um gene por
  número:
  - **os traços do corpo:** desvios da camada 2 (taxas, meias-vidas, sensibilidade de receptor);
  - **os desvios do prior** do cérebro A em algumas regras;
  - **a plasticidade:** o passo, o teto e a sensibilidade por canal de reforço;
  - mais as seções que já existem: o temperamento, a espécie, o paladar e as frutas.
- **O que não está definido: codificar a topologia** ou outra estrutura de uma rede neural (quantos neurônios, quais ligações, quais
  módulos).
  - **O A não tem topologia para codificar.** A estrutura dele é fixa: as regras, os candidatos e as entradas. Os genes do escopo mudam
    valores, não a estrutura.
  - A codificação indireta (a CPPN e o HyperNEAT, citados na EG-3) gera **pesos** de uma rede a partir de um genoma pequeno. Ela não é a
    mesma coisa que evoluir a topologia, e também ficou para depois.
  - **Evoluir a arquitetura do cérebro só entra se a GI-1 escolher um cérebro com estrutura variável e se uma tarefa própria a
    especificar.** Até lá, o desenho não promete evolução de arquitetura neural.

## 7. Decisões do Matheus

**DECIDIDAS em 2026-10-21: GI-1 a GI-5, todas pela recomendação** (pelo Gerente; a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **GI-1** (DECIDIDA) | o cérebro do pet integrado: (1) integrar o corpo, o mundo, o aprendizado e a genética **ao redor do cérebro A**; ou (2) adotar **também** uma rede recorrente, ou outro modelo de cérebro explicitamente definido | **(1) agora:** o Gate I e a genética ao redor do A, que é o único com aprendizado validado em parte no mundo (o G-T1) e com porte na web. **(2) só como pergunta própria**, com o modelo definido numa tarefa e comparado com o A na mesma linha de base integrada, depois do Gate I. As alternativas de (2): voltar ao B (já saiu por "não aprende"); uma rede recorrente modular com aprendizado hebbiano e modulação química, mais perto do que Cliff e Grand (1999) descrevem, que ainda não está definida no repositório; ou o C | **(1), se o destino pedir uma rede recorrente:** o genoma do prior, o Gate I e o porte web ficam feitos para as tabelas do A, os genes de topologia não têm o que codificar, e a troca depois refaz o caminho. **(2) agora:** os resultados do J5 e da P4 não passam para o cérebro novo, que pede calibração e um gate de aprendizado próprio; o Gate I espera um cérebro sem resultado, e a última rede recorrente do projeto (o B) não aprendeu |
| **GI-2** (DECIDIDA) | a linha de base integrada | **a configuração da validação do J5 com o adendo 8** (o corpo químico, o mundo 2D com a fruta ao lado, o cérebro A com o planejador), no mundo 2D de hoje | a do J1 (sem o planejador): o aprendiz perde do instinto ali (#285), e o I-APRENDE tende a falhar por construção. Esperar o mundo da P4: o gate passa a depender do contrato, sem que a pergunta peça |
| **GI-3** (DECIDIDA) | o critério do I-APRENDE | **uma validação nova na linha de base, com o controle do sinal embaralhado** (`mundo_3d.md`, seção 5.2) ou o braço sem aprendizado, com plano próprio | contar o G-T1 do J5 (#370): ele compara o planejador com o hábito, os dois aprendendo, e o G-T1-CONG não passou; o gate passaria com um resultado que não isola o aprendizado pela consequência. A validação nova custa um plano e uma run curta |
| **GI-4** (DECIDIDA) | o lugar do gate | **antes do G1 e do G2 genéticos, depois do Gate C em parte, em paralelo à P4, no mundo 2D;** o G0 pode vir antes | depois da P4: a genética espera o contrato sem razão. Sem o gate: a h² e a reprodução medem um pet que não junta as peças |
| **GI-5** (DECIDIDA) | o escopo genético | **o de hoje** (o corpo, os desvios do prior e a plasticidade, em codificação direta); a topologia fora até a GI-1 escolher um cérebro com estrutura variável e uma tarefa a especificar | prometer a topologia agora: um gene sem o que codificar no A, e uma expectativa que o desenho não sustenta |

## 8. Referências

Só as já VERIFICADAS (`docs/referencias/referencias_verificadas.csv`), pelos resumos:

| referência | DOI | o que sustenta aqui |
|---|---|---|
| Grand, Cliff e Malhotra (1997). Proc. 1st Int. Conf. on Autonomous Agents | `10.1145/267658.267663` | o norn com uma rede para a coordenação sensório-motora e uma bioquímica artificial (o metabolismo e os hormônios) |
| Grand e Cliff (1998). Auton Agents Multi-Agent Syst | `10.1023/a:1010042522104` | a mesma arquitetura, em revista, com mais detalhe sobre o aprendizado |
| Cliff e Grand (1999). Artificial Life 5(1) | `10.1162/106454699568683` | a rede recorrente e modular com aprendizado hebbiano, a modulação hormonal e a especificação genética da rede e da bioquímica |

**SEM FONTE:** o Gate I, os critérios dele, as decisões GI-1 a GI-5 e tudo sobre o Creatures 3 especificamente.
