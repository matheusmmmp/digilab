# A individualidade do pet: uma medida para o temperamento, o dono, a memória e o hábito

Status (2026-11-07): **as IN-1 a IN-8 DECIDIDAS pelo Matheus, todas pela recomendação** ("Agora siga com as recomendações", nesta
sessão, depois do merge do #676). A frente é a `docs/TAREFA_V3_INDIVIDUALIDADE.md`, e cada etapa tem o seu PR. A conferência do I0 trocou
uma sonda da bateria (3.1, "a conferência do I0"). Nenhum código, nenhuma faixa, nenhuma vida, nenhum plano de análise.

**O pedido (Matheus, 2026-11-07):** a conversa partiu do connectome. A pergunta era se escalar o modular até o tamanho de um conectoma
real (o da mosca) faria o pet aprender mais e criar personalidade, trejeitos e aprendizado com o dono. A leitura foi que não: o que falta
hoje não é tamanho (seção 1). O pedido é direcionar a pesquisa para o que produz essas coisas:
- o temperamento herdado forte e estável;
- mais sinal do dono;
- a memória de episódios;
- hábitos que pegam com a repetição.

**Regras deste documento:**
- referências só as verificadas (a skill `literatura-digilab`, `docs/referencias/referencias_verificadas.csv`), lidas pelo resumo; o
  resto é SEM FONTE;
- todo número novo é PROPOSTO;
- **nenhuma alegação de novidade.** "Personalidade formada no uso" já é a afirmação do postmortem de Black & White (regra 3 da skill), e
  rede, bioquímica e genoma juntos numa criatura de jogo já existiram no Creatures (Grand e Cliff 1998, `10.1023/a:1010042522104`). O
  que pode ser defensável é só a medida falsificável, com controles;
- nada aqui muda `engine.py`, o modular, a web ou uma decisão já tomada (seção 2).

## 0. Em uma página

- **A proposta é uma medida, não um mecanismo.** Hoje cada frente do cérebro se mede por um índice próprio (o episódio no `longe_fixo`, o
  índice do P2, o contraste REL − SEM). Nenhum deles pergunta: **este pet ficou diferente dos outros, de um jeito estável, e por quê?**
- **A medida:** uma bateria fixa de sondas (comida nova, bola, o dono sumindo, um susto, o longe, o tédio), aplicada a cópias do estado do pet em
  vários momentos da vida, sem tocar na vida real (seção 3). Dela sai a **repetibilidade** de cada traço: quanto das diferenças entre pets
  se repete de uma sonda para outra e de um dia para outro.
- **O desenho:** pets cruzados por genoma e por dono (clones com donos diferentes, genomas diferentes com o mesmo dono), para dividir a
  individualidade numa parte do genoma, numa parte do dono e na interação (seção 4).
- **As quatro frentes passam a ser julgadas por essa medida:**
  - o temperamento pela parte do genoma;
  - o dono pela parte da criação;
  - a memória pelas facetas que explicam essa parte;
  - o hábito pela repetição própria de cada pet.
- **A ordem** (seção 5): a bateria como ferramenta, uma linha de base descritiva no modular de hoje, e só então os mecanismos.

## 1. Por que não é escala

| | a mosca (FlyWire) | o cérebro A, vida de exemplo do J5 |
|---|---|---|
| tamanho | cerca de 139 mil neurônios e 54,5 milhões de sinapses (Dorkenwald et al. 2024, `10.1038/s41586-024-07558-y`, CORPUS) | 54 nós e 831 posições de peso; 203 não nulas no fim |
| quem decide | — | o lobo impulsos (o prior do instinto) em 913 das 960 decisões |

Os números do A saem de `docs/futuro/connectome_cerebro_a.md`, seções 3 e 5. O modular ainda não tem uma contagem equivalente gravada;
a ordem de grandeza conversada (dezenas de nós, centenas de posições) é SEM FONTE até um artefato contar.

A leitura: o pet **não usa a capacidade que já tem**. A experiência de uma vida (centenas a poucos milhares de decisões com consequência)
é pequena perto dos pesos. Multiplicar os pesos por cinco ordens de grandeza com a mesma experiência deixaria quase todos sem sinal. A
diferença entre pets sorteados assim seria ruído, não personalidade.

Personalidade, na literatura de comportamento animal, é **diferença individual consistente** entre situações e no tempo. Os traços vêm
correlacionados, em síndromes, e não independentes (Sih, Bell e Johnson 2004, `10.1016/j.tree.2004.04.009`). O formalismo para separar o
nível do indivíduo da resposta dele ao ambiente é a norma de reação: o intercepto é o nível, a inclinação é a plasticidade (Dingemanse et
al. 2010, `10.1016/j.tree.2009.07.013`). Esta proposta usa as duas ideias como desenho de medida, não como alegação sobre o pet.

O caminho de uma rede maior **num módulo só** (percepção ou movimento no mundo 3D, na escala de centenas a poucos milhares de unidades)
fica fora daqui (seção 6).

## 2. O que já existe (conferido na `main`, `3d79072`)

| peça | o estado | onde |
|---|---|---|
| o modular como cérebro padrão | os ovos novos nascem v17 com o modular; o A fica selecionável | #562; `docs/PAINEL_V3.md` |
| os pesos inatos | o `W⁰[b, j]` do M-IMPULSO é o ponto de ligação com o genoma; o aprendido nunca entra no genoma | `docs/ESPEC_DIGIBRAIN_MODULAR.md`, seções 2.2 e 4.9 |
| o genoma no log | o evento `genoma` no tick 0, atrás da `ConfigGenoma` desligada, só no Python; a seção `prior` lida como os parâmetros inatos de cada módulo | G0, #556 a #570; `docs/TAREFA_V3_GENOMA_G0.md` |
| a h² de cada seção (G1) | não começou; pela GI-4, só mede sobre um pet que passou no Gate I | `docs/futuro/ecossistema_genetico.md`, seção 6 |
| o Gate I | ADIADO pela DM-8; os critérios servem ao pet modular | `docs/FECHAMENTO_V2.md`; `docs/TAREFA_V2_GATE_I.md` |
| a memória autobiográfica | a run única passou (#541: REL − SEM +0,0646 [+0,0515; +0,0778]) | C4; `docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md` |
| as facetas adquiridas | três, `cautela_comida`, `apego_dono` e `ousadia_longe` (MA-5), cada mudança com os ids dos episódios; o temperamento inato intocado (DM-6) | M5, #535 |
| o hábito (P2) | a C2 fechou negativa (#517: M2c − M2 +0,0028 [−0,0003; +0,0060]); sem mecanismo novo no P2 (D-C2-4-1 a 4) | `docs/TAREFA_V3_HABITO_INTENCAO.md` |
| a pergunta do dono | ENCERRADA na v1: o dono pesa pelo cuidado, não pelo ensino; só reabre com pergunta nova sobre o aprendiz | `docs/LEITURA_CONSOLIDADA_DONO.md` |
| o treino pelo toque | nunca por clicar carinho e tapa (a vida do pet, v1) | `docs/TAREFA_V3_VIDA_PET_REF.md` |

O que falta não é peça. Falta uma medida comum e um desenho que cruze genoma e dono no modular.

## 3. A medida: a individualidade

### 3.1 As sondas

Uma **sonda** é uma situação padronizada aplicada a uma **cópia** do pet num tick t. O log é rejogado até t, a situação é posta na cópia,
e as decisões dela por uma janela curta são lidas. A vida real segue sem a sonda (event sourcing; nada é salvo). A sonda tem a sua rng,
derivada por `derivar_semente`, e não toca a rng do ambiente nem a da política da vida real.

A bateria PROPOSTA, cada sonda ligada a um traço:

| sonda | a situação | o traço lido | a faceta perto |
|---|---|---|---|
| **comida nova** | uma classe de comida sem episódio, à vista, com fome média | latência e chance de comer | `cautela_comida` |
| **o longe** | comida conhecida só num lugar longe, com fome média | ir ou não; a distância até desistir | `ousadia_longe` |
| **o dono some** (era "o dono chama", trocada no I0) | uma janela sem nenhum gesto do dono, sem necessidade urgente | chamar a atenção e a latência | `apego_dono` |
| **a bola** | a bola à vista, necessidades satisfeitas | brincar e por quanto tempo | — |
| **o susto** | um evento de susto perto (com o receptor, se ligado) | afastar-se e o tempo até voltar | — |
| **o tédio** | nada à vista, necessidades satisfeitas | explorar, ficar parado ou chamar | — |

**A conferência do I0 (2026-11-07, na `main` `da9a3a5`):** cada sonda tem de sair de um gesto ou de um estado que o motor já tem. Uma
situação que o motor não tem seria mecânica nova.

| sonda | como o motor produz | o que muda |
|---|---|---|
| comida nova | `MotorMundo.deixar_fruta(tipo, x, y)` (`digilab/mundo.py`): o mundo do produto (o layout padrão sem árvores, só a ração do dono, `run_v2_digibrain_prototipo.py`) nunca tem fruta, então as frutas a, b e c são classes novas para o pet; a novidade já está no M-SENS (`nov = S − hab[classe]`) | nada |
| o longe | o gesto `alimentar` vira `deixar_comida` no ponto do dono (`DonoComLugar`); a sonda põe a ração longe da posição do pet | nada |
| ~~o dono chama~~ → **o dono some** | **não existe ação de chamar do dono** (`AcaoUsuario`, `digilab/events.py`). A troca: uma janela sem nenhum gesto do dono, com as necessidades satisfeitas, lendo o `chamar_atencao`. É a ação em que o termo da faceta `apego_dono` entra (`digilab/digibrain/pers.py`) | **a sonda trocada** (o desvio D-IND-I0-1) |
| a bola | o gesto `por_bola` vira `deixar_bola(x, y)` | nada |
| o susto | o `tapa` com o corpo dos gestos (o corpo do braço P1-c-tapa, o mesmo das vidas da C1 e da C4) sobe susto, dor e estresse (`digilab/corpo.py`; o mem lê a subida). **Só na cópia:** a vida real nunca recebe o tapa (a regra "nunca treino pelo toque") | nada |
| o tédio | nenhum gesto e nada à vista; o tédio é um drive do corpo dos drives novos (`corpo.py`, `drives_novos`), e o `g_exp` do M-AFETO lê a falta dele | o I1 confere se o corpo das vidas da C4 liga os drives novos; se não, a sonda lê só a exploração, sem o drive |

**A cópia:** a vida das runs do modular é um laço simples sobre os passos do dono (`simular_vida_fisico` em
`experiments/bancada/regras_mundo.py`), e a bancada já rejoga logs (`Bancada.rejogar` em `experiments/bancada/nucleo.py`). As duas
formas de copiar o pet no fim de um dia (uma cópia profunda do motor com o cérebro, ou o replay do prefixo do log) ficam para o I1
escolher, pela que passar no G2 (a vida com e sem as sondas sai byte a byte) e custar menos.

**O dono das vidas:** as vidas da C1 e da C4 usam o `CanalSemEnsino` (PMF-3). O dono cuida só pelos gestos do mundo, e o elogio e a bronca
ficam fora. Isso já cumpre a IN-6 (só sinais naturais, nunca o toque como treino). As personas são os quatro donos de
`run_v2_digibrain_prototipo.DONOS`: atencioso, relapso, aleatório e incoerente. O incoerente faz o papel do dono inconsistente.

Os momentos PROPOSTOS: o fim de cada dia da vida. Cada sonda roda em réplicas de semente da própria sonda, para separar o pet do acaso
da sonda.

### 3.2 As medidas

- **A repetibilidade R de cada traço:** a variância entre pets sobre a variância total, com as réplicas e os dias como medidas repetidas.
  R perto de 0 quer dizer que a diferença é ruído. R alto quer dizer que é do pet.
- **A divisão da variância entre pets** (seção 4): σ²_genoma, σ²_dono, σ²_genoma×dono e o resto.
- **A norma de reação no tempo** (Dingemanse et al. 2010): por pet, o intercepto (o nível no começo) e a inclinação (quanto o traço muda
  ao longo da vida). A leitura PROPOSTA é que o temperamento aparece no intercepto e a criação na inclinação.
- **A síndrome:** a correlação entre os traços, entre pets. Traços independentes contradizem o que a literatura descreve (Sih et al.
  2004). Uma correlação que surja sem ter sido posta à mão é um achado; uma posta pelo genoma é desenho.
- **A rastreabilidade:** em cada pet, a parte da inclinação que as facetas explicam, pelos ids dos episódios (`evidencia_faceta`) e pela
  sonda `sem_faceta`.

**Números externos, só para ler o resultado, nunca como meta:**
- em animais, cerca de 52 % da variação de personalidade é atribuída a variação genética aditiva (Dochtermann, Schwab e Sih 2015,
  `10.1098/rspb.2014.2201`, meta-análise);
- em cães, a raça explica só 9 % da variação individual de comportamento, com h² > 25 % na maioria dos traços (Morrill et al. 2022,
  `10.1126/science.abk0639`).

O genoma não se calibra olhando esses números nem o gate (a lição do E1; RE-2 do `ecossistema_genetico.md`).

## 4. O desenho: genoma × dono

Um fatorial cruzado:
- **G genomas** (com o genoma vazio como um dos níveis, a vida de hoje);
- **D donos**, como personas sintéticas que só usam sinais naturais: o horário de cuidado, a fruta dada, a chamada, a brincadeira, a
  bronca. **Nunca o toque como treino.** Entre as personas, uma **inconsistente**, porque o dono real não é nem coerente nem aleatório
  (Thomaz e Breazeal 2008, `10.1016/j.artint.2007.09.009`);
- **K sementes** de ambiente por célula.

Clones (mesmo genoma) com donos diferentes dão a parte do dono. Genomas diferentes com o mesmo dono dão a parte do genoma.

**A relação com o que já existe:**
- é o G1 do `ecossistema_genetico.md` (a h² de cada seção) medido sobre traços de comportamento, e não sobre as seções do genoma;
- a parte do dono é **uma pergunta nova sobre o aprendiz**, o modular com memória e facetas. Ela não reabre a leitura da v1, que foi
  sobre o bandit. Se o dono pesar de novo só pelo cuidado, esse é o resultado, e ele fica registrado;
- a v1 já mediu natureza × criação (`docs/RESULTADO_SINAL_DONO.md`: o ambiente pesou tanto quanto o dono ou mais). Por isso o ambiente
  entra como fator ou como sementes, e não fica escondido no resto.

**O custo, ordem de grandeza:** a C2 rodou 5 400 vidas de 14 dias em 58 min com 4 processos (`docs/TAREFA_V3_HABITO_INTENCAO.md`,
etapa 4). As sondas multiplicam o custo pelo replay até cada tick e pelas janelas. G, D e K vêm do plano de análise, pelo poder, e são
PROPOSTOS lá.

## 5. Os passos

| passo | o quê | depende de | mede? |
|---|---|---|---|
| **I0** | a tarefa: a bateria, os traços, as medidas e o desenho, no papel | as IN-1 a IN-8 | não |
| **I1** | a bateria como ferramenta: as sondas por cópia do replay, só leitura, com o gabarito e o G2 (a vida com e sem sonda sai byte a byte) | I0 | não |
| **I2** | **a linha de base descritiva:** o modular v17 de hoje, genoma vazio, com D donos e K sementes. Quanto de individualidade a história sozinha já produz, e quanto disso as facetas explicam | I1; plano descritivo registrado antes | descritivo |
| **I3** | **o temperamento:** a seção `prior` do genoma escreve os parâmetros inatos dos módulos (o `W⁰`, os ganhos do M-AFETO, as taxas do M-PLAST); a pergunta é se a parte do genoma sobe e fica estável no intercepto | I2; o Gate I no modular (GI-4, IN-4) | gate, com plano |
| **I4** | **o dono:** o fatorial completo genoma × dono; a pergunta é se clones com donos diferentes divergem de forma estável na inclinação, e se as facetas explicam a divergência | I3 | gate, com plano |
| **I5** | **o hábito como trejeito:** só medida, sem mecanismo novo no P2 (D-C2-4-2). Pergunta: cada pet repete sequências, lugares ou horários próprios, acima do que o genoma e o dono explicam? | I2 (pode ir junto) | descritivo |
| **I6** | **o produto:** uma ficha de personalidade na tela, lida das mesmas medidas, com Python e web em paridade | um resultado que valha mostrar | não |

O I2 e o I5 não dependem do Gate I, porque não medem o genoma. O I3 e o I4 dependem, pela GI-4.

## 6. O que fica fora

- **Escalar a rede.** Uma rede do tamanho de um conectoma não entra (seção 1). Um módulo maior num ponto só (percepção ou movimento no
  mundo 3D) é outra ideia, para um documento próprio, se o Matheus quiser.
- **Mecanismo novo de hábito.** A C2 fechou sem mecanismo novo no P2. O I5 só mede; um mecanismo depende de uma decisão nova.
- **A calibração.** Nenhum número de mecânica se ajusta aqui (`v2-calibracao-no-fim`); o genoma não se ajusta ao gate (RE-2).
- **A web** até o I6.
- **Os dois pets.** O outro pet como fonte de individualidade (a imitação, a hierarquia) é um passo depois.

## 7. Riscos

- **Ler ruído como personalidade.** Mitigação: a repetibilidade com réplicas de sonda e de semente, e o genoma vazio como controle.
- **A sonda mexer na vida.** Mitigação: só cópia, rng própria, e o G2 byte a byte no I1.
- **As sondas medirem a mecânica, não o pet.** Uma sonda em que todo pet faz a mesma coisa não separa ninguém. Mitigação: o I2 mostra
  quais sondas têm variância, e as sem variância saem antes do I3, por regra escrita no plano.
- **Circularidade das facetas.** As três facetas foram desenhadas perto de três sondas. Mitigação: sondas sem faceta (bola, susto, tédio)
  e a sonda `sem_faceta` como controle.
- **O dono voltar a não pesar.** É um resultado possível e aceitável. A tarefa registra o negativo como está (CLAUDE.md, "Gate que falha
  não para a V3").
- **O custo do replay até cada tick.** Mitigação: sondas só no fim do dia; o I1 mede o custo antes do plano.

## 8. Decisões para o Matheus

**DECIDIDAS em 2026-11-07: IN-1 a IN-8, todas como recomendado** (Matheus, "Agora siga com as recomendações"). A coluna da recomendação
é o que vale.

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **IN-1** | Abrir a frente da individualidade como a medida comum do cérebro. | **Sim**, como tarefa V3 própria, com o I0 só papel. | Sem a medida, cada mecanismo segue com índice próprio, e "personalidade" fica sem teste. |
| **IN-2** | A bateria: as seis sondas da 3.1 ou menos. | **As seis**, com a regra de tirar as sem variância depois do I2. | Poucas sondas não testam a consistência entre situações, que é a definição de personalidade. |
| **IN-3** | A linha de base (I2) antes de qualquer mecanismo. | **Sim.** | Sem ela, um ganho no I3 ou no I4 não se separa do que a memória e as facetas já fazem. |
| **IN-4** | O Gate I antes do I3 (GI-4), com os critérios no modular. | **Sim**, rodar o Gate I no modular entre o I2 e o I3. | Pular a GI-4 mede h² num pet que não se sabe integrado; a GI-4 foi decidida por isso. |
| **IN-5** | O dono como pergunta nova sobre o aprendiz modular. | **Sim**, com o texto da seção 4 no topo da tarefa, deixando claro que a leitura da v1 não se reabre. | Sem o enquadramento, parece reabrir a pergunta encerrada; com ele, um negativo fica limpo. |
| **IN-6** | As personas de dono: só sinais naturais, com uma inconsistente. | **Sim**; nunca o toque como treino. | O toque como treino contradiz a decisão da vida do pet; sem a inconsistente, o contraste fica artificial. |
| **IN-7** | O hábito no I5 só como medida. | **Sim**, respeitando a D-C2-4-2. | Um mecanismo novo agora reabre a C2 sem pergunta nova. |
| **IN-8** | Onde fica: tarefa nova (`TAREFA_V3_INDIVIDUALIDADE.md`) e plano novo (`PLANO_ANALISE_V3_INDIVIDUALIDADE.md`). | **Sim**, uma tarefa e um plano V3 próprios, e não adendos ao protótipo. | Como adendo, a medida fica presa ao cenário do protótipo (`longe_fixo`, comedouro). |
