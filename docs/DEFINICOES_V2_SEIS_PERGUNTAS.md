# DEFINIÇÕES DA V2: o que a segunda revisão de literatura sustenta para as seis perguntas

Status: **PROPOSTO**, escrito pelo coordenador em 2026-10-07 a pedido do Matheus. **Só texto:** não muda código, config nem decisão
tomada, e não autoriza run. As decisões ficam na seção 9.

**Fonte única:** `docs/referencias/F_REVISAO_V2_SEIS_PERGUNTAS.md` (a revisão do Claude Science, prompt #208), lida inteira, com
`docs/referencias/REGRAS_CITACAO_DIGILAB.md`. Os números do projeto apontam o artefato. Não há número novo.

**Regras de citação deste documento:**
- **Só se cita pelo conteúdo o que a revisão leu.**
  - Akam et al. 2015: o resumo (1 de 25 páginas).
  - Kimmel e Terrant 1968: a página 1 de 4. Os resultados empíricos deles não se citam.
- **Só título e metadados, nunca pelo conteúdo:** Daw, Niv e Dayan 2005, Daw et al. 2011, Miller et al. 2017, Church 1964, Charnov 1976,
  Ghirlanda e Enquist 2003 e Dymond et al. 2015. Aparecem só como pista ou como nome de uma objeção.
- **Pistas não verificadas** (seção 6 da revisão) **não se citam.**
- **Referências reaproveitadas** de rodadas anteriores valem pelo que a coluna `o_que_sustenta` de
  `docs/referencias/v2_referencias_verificadas.csv` diz delas.

**Rótulos:**
- APOIADA: a fonte lida sustenta a definição;
- APOIADA COM RESSALVA: sustenta com limite declarado;
- SEM APOIO DIRETO: nenhuma fonte lida sustenta, e a definição é leitura nossa;
- CONTESTADA: uma fonte lida vai contra o desenho de hoje.

**Estado** (vocabulário do projeto):
- EXECUTADO: rodou e tem artefato;
- ESPECIFICADO: está numa tarefa ou plano commitado;
- IDEIA: só aqui.

---

## 1. Planejamento com modelo × hábito (a pergunta do "pet que pensa")

**Definição.** O pet "planeja" quando muda a escolha depois de uma mudança no mundo **sem ter reexperimentado a consequência**. A medida é
um **par de testes**, e não um só.

1. **Revalorização da recompensa sem reexperiência.**
   - **O teste:** troca-se o efeito de uma fruta (o que ela faz no corpo) e mede-se a escolha na primeira oportunidade, antes de o pet
     comê-la de novo.
   - **O que se espera:** o hábito não muda. A representação de sucessor (SR) e o modelo do mundo mudam.
2. **Mudança de transição sem reexperiência.**
   - **O teste:** troca-se **onde** a fruta cai (a árvore, a região), com os efeitos iguais, e mede-se a primeira busca.
   - **O que se espera:** a SR não acompanha, e o modelo acompanha.

**O critério que separa SR de planejamento com modelo:**
- só o teste 1 passa: SR (ou um modelo só de recompensa);
- os dois passam: planejamento com modelo de transição;
- nenhum passa: hábito.

**A tarefa de dois passos sozinha não serve.** Akam, Costa e Dayan 2015, `10.1371/journal.pcbi.1004648` (resumo): estratégias sem modelo
podem produzir a assinatura atribuída ao controle com modelo nessa tarefa.

**A arquitetura mínima candidata:**
- o prior herdado;
- o aprendiz sem modelo de hoje;
- uma camada de SR sobre os estados do mapa, aprendida por TD (Dayan 1993, `10.1162/neco.1993.5.4.613`, resumo).

O caráter intermediário da SR (flexível à recompensa, insensível à transição) é de Momennejad et al. 2017, `10.1038/s41562-017-0180-8`
(resumo). Que ela caiba em inteiros e rode no navegador é leitura nossa, sem fonte.

**Evidência animal de simular antes de agir:** Pfeiffer e Foster 2013, `10.1038/nature12112` (resumo). As sequências hipocampais antes do
movimento traçam caminhos até a meta lembrada.

- **Rótulo:** a medida em par é **APOIADA COM RESSALVA**. Akam e Momennejad sustentam as duas metades, no nível do resumo. O par como
  desenho é leitura da revisão. A arbitragem por incerteza (Daw, Niv e Dayan 2005) fica só como pista.
- **Estado:**
  - **IDEIA:** o par de testes, a camada de SR e a medida;
  - **ESPECIFICADO:** o mundo onde o teste 2 pode rodar (árvores e regiões, `docs/TAREFA_V2_MUNDO_FISICO.md`);
  - **EXECUTADO** (parte do material do teste 1): a troca de efeito no meio da vida (o mutável) existe e rodou na validação única
    (`artifacts_v2_validacao_unica/`). Ela mede a recuperação **com** reexperiência, então não é o teste 1.

## 2. O controle acoplado e a alternativa

**Definição.** O controle "só cuidado" passa a ser um **acoplado recíproco dentro do mesmo pet e da mesma vida**, no lugar do acoplado em
malha aberta entre pets.

- **Dois canais por pet:** duas frutas ou duas regiões.
- Num canal, o dono responde ao que **este** pet faz. No outro, o pet recebe o que o dono fez em resposta ao **parceiro**.
- **O contraste ensino × cuidado é dentro do pet:** a diferença de qualidade de cuidado entre pets, que deixou a separação ilegível na
  validação única, sai por construção.

**A fonte.** O desenho recíproco é de Kimmel e Terrant 1968, `10.3758/BF03209860` (página 1). Na mesma página eles descrevem como o
acoplado comum gera uma diferença espúria quando os sujeitos do par diferem.

**A objeção ao acoplado é contestada.** A objeção clássica tem o nome de Church 1964, `10.1037/h0042733`, mas desse artigo só os
metadados foram conferidos. Kimmel e Terrant, que propõem a alternativa, criticam as premissas dele. O defensável é "o acoplado é
enviesável", e não "o acoplado é inválido".

- **Rótulo:** **APOIADA COM RESSALVA.** A fonte da alternativa foi lida só na página 1, e a magnitude da objeção é contestada na própria
  fonte. A tradução para dois canais no Digilab é leitura nossa.
- **Estado:**
  - **EXECUTADO:** o acoplado em malha aberta (validação única: em todo braço com dono, o só cuidado cuidou pior que o original,
    `docs/RESULTADO_V2_VALIDACAO_UNICA.md`);
  - **ESPECIFICADO:** a mitigação sem reciprocidade, com os dois lados acoplados à mesma fonte e o primário em malha fechada
    (`docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, 3.5; o adendo da PMF-2 do mundo, pedido ao chat C);
  - **IDEIA:** o acoplado recíproco.

## 3. Aprender o que faz mal sem alternativa (o achado 1)

**O achado.** No cérebro A, o pet aprende a evitar a fruta ruim **quando escolhe entre frutas** (2% a 11% de escolha da ruim, contra 29% a
65% do herdado). **Com uma fruta só**, come o que houver (`docs/DESCRITIVO_V2_PLATO.md`, `artifacts_v2_descritivo_plato/`).

**Os três mecanismos candidatos e o que cada um prevê:**
1. **Aversão gustativa condicionada.**
   - Garcia e Koelling 1966, `10.3758/BF03342209` (PDF obtido): a associabilidade depende do par pista e consequência. O gosto se associa
     ao mal-estar visceral, e isso permite aprender com pouca experiência e com atraso.
   - **Prevê:** a rejeição é aprendida sem alternativa, porque muda o valor do item.
2. **Aprendiz de escolha relativa** (leitura nossa, **SEM FONTE**). A atualização só ocorre sobre o contraste entre as opções presentes, e
   uma opção sozinha não gera gradiente.
   - **Prevê:** o achado 1 exatamente.
3. **O valor do item separado do valor do ato de comer** (leitura nossa, **SEM FONTE**). O pet aprende sobre a fruta, mas a decisão de
   comer é dominada pela fome.
   - **Prevê:** o achado 1 e o termo de presença na decisão de comer aprendendo pouco, que é o que o descritivo mostrou.

**O teste que distingue os três: a transferência da rejeição da escolha múltipla para o item único.**
- **Como:** depois de treino só com escolha (duas frutas ou mais), oferece-se a fruta ruim sozinha e mede-se p(comer).
- **Se a rejeição transfere:** o mecanismo é o 1.
- **Se não transfere:** é o 2 ou o 3.
- **Para separar o 2 do 3:** com a fome baixa, o 3 rejeita a ruim sozinha e o 2 não.

- **Rótulo:** **SEM APOIO DIRETO.** Garcia sustenta que o mecanismo 1 existe em animais. A revisão não localizou trabalho que compare
  rejeição absoluta e escolha relativa.
- **Estado:**
  - **EXECUTADO:** o achado (descritivo pós hoc);
  - **IDEIA:** o teste de transferência.
  - Não "consertar" o aprendiz antes de rodar o teste.

## 4. Tédio, curiosidade e drives saciáveis

**Definição do tédio.** A variável do tédio é a **diversidade recente** dos estados visitados e das interações, e não o tempo parado.
Repetir a mesma coisa reduz menos o tédio que variar: brincar com a bola duas vezes seguidas reduz menos que brincar e depois explorar.

- **A fonte:** Burn 2017, `10.1016/j.anbehav.2017.06.006` (resumo e destaques). O tédio é excitação subótima somada a **aversão à
  monotonia**, as duas mensuráveis. Meagher e Mason 2012, `10.1371/journal.pone.0049180`, e Meagher, Campbell e Mason 2017,
  `10.1016/j.applanim.2017.08.001` (PDFs obtidos), dão os estados tipo-tédio em martas e a replicação.
- **Leitura nossa:** a tradução para "diversidade recente".

**Definição da curiosidade.** A redução da curiosidade acompanha o **progresso de aprendizado**, e não a surpresa bruta.
- Oudeyer e Kaplan 2007, `10.3389/neuro.12.006.2007` (verificada no projeto), separam novidade, progresso de aprendizado e competência
  como tipos de motivação intrínseca.
- Que o progresso proteja contra o agente preso numa fonte de ruído é a defesa citada pela revisão, **SEM FONTE** verificada aqui.

**Sem vício.** Os drives são saciáveis: a recompensa é a redução do desvio do ponto de ajuste, e um drive satisfeito deixa de pagar
(Keramati e Gutkin 2014, `10.7554/eLife.04811`, verificada no projeto).

**A arbitragem entre vários drives sem um dominar:** **SEM FONTE.** A revisão não a localizou além de Keramati e Gutkin.

- **Rótulo:** o tédio por diversidade é **APOIADA COM RESSALVA** (Burn no nível do resumo; a variável é tradução nossa). **O tédio de hoje
  é CONTESTADA:** em `docs/TAREFA_V2_CORPO_DRIVES.md` (seção 7, CD decididas) ele sobe +450 por tick acordado e cai ao brincar. É a
  formalização por tempo, que a revisão aponta como a errada (seção 3 dela, força média-alta). A curiosidade da tarefa cai por novidade
  achada (com janela de 1440 ticks), mais perto de novidade que de progresso.
- **Estado:**
  - **ESPECIFICADO:** o tédio por tempo e a curiosidade por novidade (a tarefa do corpo);
  - **IDEIA:** o tédio por diversidade e a curiosidade por progresso.
  - Mudar o tédio da tarefa é decisão (seção 9).

## 5. Forrageio no mapa: "explorar compensou"

**Definição.** Três medidas, em ordem de robustez:
1. **O tempo de permanência por região contra o custo de viagem até a próxima.** Hayden, Pearson e Platt 2011, `10.1038/nn.2856` (resumo):
   com viagens mais longas, o limiar de abandono da mancha sobe.
2. **A taxa de ganho realizada no abandono contra a taxa média do ambiente.**
3. **O custo de oportunidade estimado pelo agente contra o real.** Constantino e Daw 2015, `10.3758/s13415-015-0350-y` (PDF obtido): o
   custo de oportunidade do tempo é aprendido.

**A previsão para o nosso mundo.** Com as árvores mais distantes e nada mais mudado, o pet fica mais em cada árvore antes de sair. Se não
muda, ele segue o cheiro e não forrageia.

**Charnov 1976**, `10.1016/0040-5809(76)90040-x`, **não é citado pelo conteúdo do teorema** (só metadados). Ligar o padrão de Hayden ao
teorema do valor marginal é leitura nossa. A medida 2 é a forma do teorema e fica **SEM FONTE** lida.

- **Rótulo:** a medida 1 é **APOIADA COM RESSALVA** (Hayden, resumo; em macacos, numa tarefa de manchas). A 3 é **APOIADA COM RESSALVA**
  (Constantino e Daw). A 2 é **SEM APOIO DIRETO**.
- **Estado:**
  - **ESPECIFICADO:** a medida primária do plano do mundo (a energia líquida, PMF-1, `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`);
  - **IDEIA:** as três medidas acima e a previsão da distância entre as árvores.

## 6. Punição e generalização: as quatro medidas do tapa

**Definição.** Quatro medidas, sempre separadas:

| medida | o que é | onde se mede |
|---|---|---|
| **medo** | a resposta ao estímulo em si | o medo da mão: a redução por carinho nas 6 h depois de um tapa, e a fração de `chamar_atencao` (tarefa do corpo, seção 8) |
| **estresse** | o estado de base fora do episódio | o estresse médio no fim do dia e a fração do tempo acima de 0,75 (idem) |
| **vínculo** | o comportamento dirigido ao dono em contexto neutro | o vínculo da base nova (S-4); "não disponível" até ela |
| **generalização** | a **inclinação** do gradiente da aversão sobre as frutas **não punidas** | a queda de p(comer) e do peso da escolha nas frutas não punidas, contra a punida, depois de punir uma fruta só; a inclinação, e não o valor numa fruta |

A quarta é a que diagnostica o achado 3 (no cérebro C, a punição numa fruta valeu para todas, `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`).
Hoje ela não está especificada.

**As fontes.**
- **O custo de bem-estar da punição por um parceiro social:** Casey et al. 2021, `10.1038/s41598-021-97743-0`, e Vieira de Castro et al.
  2020, `10.1371/journal.pone.0225023` (verificadas no projeto). China, Mills e Cooper 2020, `10.3389/fvets.2020.00508`, dá o desenho de
  comparação de métodos.
- **A literatura de generalização:** Ghirlanda e Enquist 2003 e Dymond et al. 2015, conferidos só nos títulos. Ficam como pista, sem
  sustentar o conteúdo.
- **Que um estímulo no corpo, com dimensões, permite um gradiente não plano** é leitura da revisão, **SEM FONTE**.

- **Rótulo:**
  - medo, estresse e vínculo como custo esperado: **APOIADA COM RESSALVA** (cães, desfecho por questionário ou teste de viés; o pet não é
    um cão);
  - a medida de generalização: **SEM APOIO DIRETO**.
- **Estado:**
  - **ESPECIFICADO:** o medo, o estresse e o vínculo pendente (`docs/TAREFA_V2_CORPO_DRIVES.md`, seção 8; `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`);
  - **IDEIA:** a inclinação da generalização.

## 7. Resumo

| # | definição | rótulo | sustentação | estado |
|---|---|---|---|---|
| 1 | o par revalorização + transição sem reexperiência; SR × modelo pelo segundo teste | APOIADA COM RESSALVA | `10.1371/journal.pcbi.1004648`, `10.1038/s41562-017-0180-8` | IDEIA |
| 1 | a tarefa de dois passos como medida única | CONTESTADA | `10.1371/journal.pcbi.1004648` | não usar |
| 2 | o acoplado recíproco em dois canais do mesmo pet | APOIADA COM RESSALVA | `10.3758/BF03209860` (objeção de `10.1037/h0042733` contestada) | IDEIA |
| 2 | o acoplado em malha aberta contra malha fechada | CONTESTADA pelo próprio resultado do projeto | `docs/RESULTADO_V2_VALIDACAO_UNICA.md` | EXECUTADO; adendo pedido |
| 3 | a transferência da rejeição para o item único | SEM APOIO DIRETO | `10.3758/BF03342209` só para o mecanismo 1 | IDEIA |
| 4 | o tédio por diversidade recente | APOIADA COM RESSALVA | `10.1016/j.anbehav.2017.06.006` | IDEIA |
| 4 | o tédio por tempo acordado (o da tarefa do corpo) | CONTESTADA | `10.1016/j.anbehav.2017.06.006` | ESPECIFICADO |
| 4 | a curiosidade por progresso; drives saciáveis | APOIADA COM RESSALVA | `10.3389/neuro.12.006.2007`, `10.7554/eLife.04811` | IDEIA (a curiosidade); ESPECIFICADO (a saciedade) |
| 5 | permanência × custo de viagem; custo de oportunidade aprendido | APOIADA COM RESSALVA | `10.1038/nn.2856`, `10.3758/s13415-015-0350-y` | IDEIA |
| 5 | a taxa no abandono igual à média (teorema) | SEM APOIO DIRETO | Charnov só nos metadados | IDEIA |
| 6 | medo, estresse e vínculo separados | APOIADA COM RESSALVA | `10.1038/s41598-021-97743-0`, `10.1371/journal.pone.0225023` | ESPECIFICADO (o vínculo pendente) |
| 6 | a inclinação da generalização sobre as frutas não punidas | SEM APOIO DIRETO | — | IDEIA |

## 8. O que este documento não faz

- Não muda as CD do corpo, as PCD, as MF nem as PMF; as divergências viram decisões na seção 9.
- Não decide a arquitetura do "pet que pensa" (caminho E): só diz como medir se ele planeja.
- Não faz alegação de novidade. Onde a revisão não achou nada, é "não localizado nas buscas da revisão F" (busca sem varredura por
  código, cobertura estreita, declarada na revisão).

## 9. Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| DS-1 | Adotar o par revalorização + transição sem reexperiência como a medida de "o pet planeja" | **sim**, com o critério da seção 1; a tarefa de dois passos fica fora como medida única | só a de dois passos: um hábito sofisticado passa por planejamento. Só a revalorização: a SR passa por modelo |
| DS-2 | O acoplado recíproco entra como desenho a estudar para o próximo plano com dono | **sim, como IDEIA registrada**. A mitigação já especificada (primário em malha fechada, acoplados à mesma fonte) fica valendo até lá | adotá-lo já: dois canais por pet mudam o mundo e os planos em curso. Ignorá-lo: o só cuidado continua enviesável |
| DS-3 | Rodar o teste de transferência (seção 3) antes de qualquer mudança no aprendiz para o achado 1 | **sim**, como descritivo nas vidas que já existem ou num plano curto próprio | mudar o aprendiz antes: conserta o mecanismo errado |
| DS-4 | Trocar o tédio da tarefa do corpo (por tempo) pelo tédio por diversidade recente | **sim, por revisão da tarefa antes da etapa 6** (drives novos), que é quando o tédio entra no código; a química base e os órgãos não mudam | manter: o pet pode se contentar em repetir a mesma brincadeira e o drive mede outra coisa. Trocar já: refaz a CD-2/CD-8 do plano e os números PROPOSTOS da seção 7 |
| DS-5 | Pôr as medidas de forrageio da seção 5 no plano do mundo como secundárias | **sim, por adendo antes da calibração** (as medidas 1 e 3; a 2 só descritiva) | sem elas: "explorar compensou" fica só na energia, sem separar forragear de seguir o cheiro |
| DS-6 | Pôr a inclinação da generalização no plano do corpo como medida do tapa | **sim, por adendo**, só descritiva | sem ela: o achado 3 do C fica sem medida, e o tapa pode generalizar sem ninguém ver |
