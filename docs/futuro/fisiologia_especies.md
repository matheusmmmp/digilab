# Fisiologia por espécie: um corpo-base comum e um perfil herdável por linhagem

Status: **IDEIA** (Matheus, 2026-10-08), registrada para a fase em que o genoma passar a gerar o corpo. **Não autoriza implementação**,
não muda nenhum experimento e não marca nenhum módulo como existente. O desenho é PROPOSTO; as decisões FE-1, FE-2, FE-4, FE-5 e FE-6
foram tomadas pelo Matheus em 2026-10-08, seguindo as recomendações (seção 10). FE-3 segue aberta.

## 1. A ideia

Diferenciar os Digimon sem dar a cada um um corpo inteiro próprio. Todos partem de um **corpo-base comum**, e cada linhagem traz um
**perfil fisiológico herdável** com quatro camadas:

| camada | o que é | herdável? | exemplo |
|---|---|---|---|
| **1. órgãos presentes** | um módulo de corpo que só algumas linhagens têm | sim | um sistema respiratório adaptado à água; um órgão sensorial a mais |
| **2. configuração dos órgãos comuns** | o mesmo órgão, operando de outro jeito | sim | capacidade energética, sensibilidade dos sentidos, tolerância térmica, ritmo de recuperação |
| **3. predisposições inatas** | as tendências de comportamento do começo da vida | sim | o que o pet faz antes de aprender qualquer coisa |
| **4. estado aprendido** | memórias, pesos aprendidos, o que a rede de si aprendeu daquele corpo | **não**: é do indivíduo | o que aquela criatura viveu |

**A regra de escolha:**
- **Órgão diferente** quando a linhagem tem de fato uma capacidade corporal que as outras não têm.
- **Configuração diferente** quando o órgão é o mesmo, mas funciona de outro jeito.
- **Predisposição** quando a diferença é só de comportamento.

**Rótulo só com efeito no mundo.** "Aquático", "blindado" ou "aéreo" só vira diferença fisiológica se essa diferença mudar alguma coisa
no mundo do jogo. Sem lugar onde a água importa, não há módulo aquático.

## 2. Como o Creatures 3 faz

Pelo *Creatures 3 Genetics Kit Manual* (CORPUS, documentação de produto, lido em 2026-10-07; o ponto abaixo foi trazido pelo Matheus em
2026-10-08, e a página ainda precisa ser anotada):
- os genomas de **Ettins e Grendels compartilham muitas estruturas com os das Norns**;
- a diferença destacada entre as espécies está sobretudo nos **genes de instinto** e nos **genes de estímulo**;
- o genoma também pode variar **a química que cada órgão contém e regula**.

**A leitura para o Digilab (INTERPRETAÇÃO):** o Creatures 3 já usa a separação proposta acima. O corpo e o cérebro são quase os mesmos
entre as espécies; o que muda é a predisposição (o instinto, camada 3), a forma como cada estímulo mexe na química (camada 2) e a química
de cada órgão (camadas 1 e 2). Não é preciso um corpo inteiro por espécie.

## 3. O que existe hoje (REPOSITÓRIO)

- **Espécies:** o catálogo tem seis espécies e quatro ativas no jogo (brasa, cirro, ferrugem, limo; na tela, os brasões Coragem, Amizade,
  Conhecimento e Sinceridade). Elas diferem **só no combate**: stats por espécie (`config._catalogo_especies`) e aptidão de treino por
  espécie (`config._aptidao_especie`). No corpo, todas são iguais.
- **Genoma:** espécie, os quatro eixos de temperamento (`digilab/temperamento.py`) e, nas frutas, a neofobia e a preferência inata
  (`digilab/frutas.py`). O genoma **não gera nenhum componente do corpo**.
- **Corpo:** o corpo químico existe (`digilab/corpo.py`, `digilab/motor_corpo.py`), com digestão, Vida, drives novos, gestos e banheiro
  atrás de chaves (`ConfigCorpo`). O grafo do corpo é **uma tabela única, validada na carga** (`digilab/corpo_grafo.py`): químicos,
  reações e emissores, com as checagens de fechado, sumidouro, automantido e laço de ganho. As taxas são as mesmas para todo pet.
- **Cérebro:** o prior do cérebro (o instinto) é o mesmo para todo pet; não vem do genoma (`docs/research/digibrain/mechanisms/
  genome_plasticity.md`).
- **Pesquisa:** a hipótese H-GEN-02 ("o genoma define a fisiologia e o prior") está registrada como IDEIA, para a fase 3.

## 4. Desenho proposto

### 4.1 O perfil como dado sobre o grafo do corpo

O grafo do corpo já é uma tabela única validada. O perfil de uma linhagem seria **uma alteração declarada dessa tabela**:
- **camada 1:** acrescentar químicos, reações, emissores e receptores de um módulo (o órgão a mais);
- **camada 2:** trocar números da tabela comum (taxas, meias-vidas, ganhos de emissores, quantidades dos estímulos, raios dos sentidos).

O corpo de cada linhagem passaria pelas mesmas checagens (fechado, sumidouro, automantido, sem laço de ganho) **antes da run**, um grafo
por perfil. Um perfil que quebre o grafo falha alto, como hoje.

Tudo em inteiros, como o corpo de hoje, para o replay bit a bit e a paridade Python/web.

### 4.2 As predisposições no cérebro

A camada 3 é o prior do cérebro por linhagem: os pesos iniciais do instinto mudam por espécie, como os genes de instinto do Creatures 3.
O que o pet aprende continua por cima, igual para todas as linhagens. Assim a pergunta maior se mantém: o P0 (só o herdado) passa a ter
um herdado por espécie.

### 4.3 O estado aprendido fica fora do genoma

Memórias, pesos aprendidos e o que a rede de si aprendeu nunca vão para o genoma nem para o filho (sem herança do adquirido). O filho
herda o perfil, não a experiência.

### 4.4 Estágio e variação individual

- **Estágio:** um módulo pode ligar num estágio, como os genes que ligam por estágio no Creatures 3 (`docs/futuro/ego_existencia.md`,
  seção 2.2). A evolução para Champion pode trazer o órgão novo, e a rede de si teria de reaprender o próprio corpo, um dos testes do ego.
- **Variação dentro da linhagem:** cada indivíduo pode variar em torno do perfil da espécie, em faixas pequenas. Fica para a fase 3, com
  plano próprio (seção 7).

## 5. Exemplos PROPOSTOS e o efeito no mundo que cada um exige

| perfil | camadas | o que muda no corpo | o que o mundo precisa ter para o rótulo valer |
|---|---|---|---|
| **aquático** | 1 e 2 | módulo respiratório adaptado à água; gasto diferente dentro e fora dela | uma região de água no mapa (um lago), onde os outros não entram ou gastam muito mais, com comida que só se alcança por ali |
| **blindado** | 2 | proteção corporal maior (menos dano por estímulo de dano) e recuperação diferente | fontes de dano no mundo: a praga que pica, a fruta podre, quedas; o tapa, se o jogador usar |
| **aéreo** | 1 e 2 | propriocepção e equilíbrio mais desenvolvidos; andar custa menos | obstáculos ou desníveis no mapa, ou distâncias que pesam no forrageio |
| **sensorial** | 2 | olfato mais sensível (cheiro de mais longe) | já existe: o cheiro do mundo físico pesa no forrageio |

O perfil sensorial é o único que o mundo de hoje já sustenta. Os outros pedem uma peça nova no mapa, que entra junto com o módulo e nunca
antes dele.

Qual perfil vai para cada brasão é decisão do Matheus (FE-3). A tradição dos Digimon pode inspirar, mas não é evidência de nada (regra da
skill `literatura-digilab`).

## 6. Ligações com o que já está registrado

- **Corpo e ego** (`docs/futuro/ego_existencia.md`): o perfil é o "genoma de fisiologia" da seção 2.2. Um corpo diferente por espécie dá
  à rede de si um corpo diferente para aprender.
- **Mundo físico** (`docs/futuro/mundo_fisico.md`): as regiões novas (água, desníveis) entram por causa dos perfis.
- **Doença de órgão** (`docs/futuro/doenca_remedio.md`): a mesma doença pode pesar diferente por espécie. Uma linhagem pode depender mais
  do olfato e sofrer mais com a perda dele.
- **Convivência** (`docs/futuro/convivencia_mundo_fisico.md`): pets de espécies diferentes no mesmo mapa ocupam lugares diferentes. Copiar
  um pet de outra espécie pode levar a um lugar onde o corpo do copiador não funciona: o aprendizado social com corpos diferentes é uma
  pergunta própria.
- **Combate:** as espécies hoje só diferem no combate, e o E2 da V2.1 mostrou que a soma de stats não dá identidade nem ciclo entre
  espécies. A fisiologia poderia dar identidade às espécies, mas o combate tem equilíbrio validado (V21E, pets v9). **Nada aqui mexe no
  combate** sem tarefa própria, na rodada de equilíbrio (FE-5).

## 7. Para a pesquisa

- **Corpo casado e descasado com o mundo.** Um pet cujo corpo combina com o lugar onde vive é a versão corporal da condição casado; um
  aquático num mapa seco é o descasado. A pergunta maior ganha um eixo: quanto vale aprender quando o corpo herdado não serve ao mundo.
  É a norma de reação de sempre, perfil × ambiente (Dingemanse et al. 2010).
- **O herdado separado do vivido.** Com o aprendizado desligado, duas espécies no mesmo mundo diferem só pelo corpo e pelo instinto. Com
  ele ligado, a diferença que sobra mede o quanto cada corpo muda o que se aprende.
- **Genomas fixados por desenho antes de evoluir.** Os perfis entram primeiro como fixos por espécie (como na H-GEN-01), sem seleção. A
  lição do E1 vale: um genoma ajustado para passar um gate vicia o teste; genoma novo só com plano próprio.
- **Literatura:** o Creatures codifica no genoma o substrato neural e de desenvolvimento (Grand, Cliff e Malhotra 1997, VERIFICADA) e
  modula a rede pela bioquímica (Grand e Cliff 1998, VERIFICADA). Corpo diferente com o mesmo corpo-base não é novidade do Digilab.

## 8. Riscos

- **Escopo.** Um módulo por vez, cada um com o efeito no mundo e o gate dele; nunca os quatro perfis de uma vez.
- **Rótulo sem efeito.** Um "aquático" sem água no mapa é só nome; a regra da seção 1 barra isso.
- **Equilíbrio do jogo.** Uma espécie pode passar a dominar o forrageio ou a sobrevivência, como a Ferrugem dominou o combate (E2).
  Precisa de medida de equilíbrio entre espécies, por mundo.
- **Paridade e replay.** Um grafo por perfil multiplica os gabaritos; cada perfil precisa da paridade Python × TypeScript.
- **Pets antigos.** Pets v1 a v10 não mudam; o perfil entra numa versão de pet nova.

## 9. Ordem possível

1. **Camada 2 sobre o corpo de hoje:** números por espécie na tabela do grafo, sem órgão novo. Começa pelo olfato, que o mundo já usa.
2. **Camada 3:** o prior do cérebro por espécie.
3. **Camada 1:** o primeiro módulo, junto com a peça do mundo que lhe dá efeito.
4. **Variação individual e herança dos perfis,** na fase 3, com plano próprio.

## 10. Decisões do Matheus

| # | decisão | estado |
|---|---|---|
| FE-1 | O perfil é da espécie (brasão) ou da linha evolutiva (cada Digimon) | **DECIDIDO** (2026-10-08): configurações e predisposições pela espécie; módulos que ligam por estágio na linha, na evolução |
| FE-2 | O primeiro passo | **DECIDIDO** (2026-10-08): a camada 2 no corpo de hoje, começando pelo olfato, sem órgão novo |
| FE-3 | Que perfil vai para cada um dos quatro brasões | **aberta**: decisão do Matheus; o sensorial é o único que o mundo de hoje já sustenta |
| FE-4 | Variação individual dentro da espécie agora ou só na fase 3 | **DECIDIDO** (2026-10-08): na fase 3, com plano próprio |
| FE-5 | O perfil mexe nos stats de combate | **DECIDIDO** (2026-10-08): não agora; o combate tem equilíbrio validado e só muda numa rodada de equilíbrio própria |
| FE-6 | Regiões novas no mapa (água, desníveis) | **DECIDIDO** (2026-10-08): só junto com o módulo que precisa delas |
