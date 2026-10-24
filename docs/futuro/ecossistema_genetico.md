# Ecossistema genético — o código genético de cada entidade, e entidades que geram o de outras (desenho)

> **Nota (2026-10-24), a direção nova:** o Matheus decidiu, no PROMPT MESTRE, que o produto jogável vem primeiro, que o DigiBrain
> caminha para um cérebro **modular**, e que o cérebro A fica como linha de base, controle e fallback condicionado, e não como o cérebro
> final da web. As decisões "a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15) estão **SUPERADAS** desde 2026-10-24; o
> texto abaixo fica como estava, como registro. Ver `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`.
>
> **O genoma do cérebro com a direção nova:** a seção `prior` ("desvios do prior do instinto em algumas regras do cérebro A") passa
> a ler-se como os parâmetros inatos de **cada módulo** do cérebro modular (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 9). A
> topologia continua fora (a GI-5), e nada disso está implementado.

Status (2026-10-14): **as decisões EG-1 a EG-8 estão DECIDIDAS pelo Matheus, todas pela recomendação** (seção 8). O resto do desenho
segue PROPOSTO e só papel. É o pedido do Matheus pelo Gerente: um "código genético virtual" de cada entidade, e uma entidade que gere o
código genético de outra, formando um ecossistema. Este documento não autoriza implementação: cada passo da seção 6 entra com tarefa e
plano próprios.

**Regras deste desenho:**
- Os números são PROPOSTOS e SEM FONTE, salvo onde citam o código ou um artefato.
- Só entram referências VERIFICADAS (a skill `literatura-digilab`; as novas foram conferidas no Crossref e no arXiv em 2026-10-14).
- **Nenhuma alegação de novidade.** Herdar o prior do aprendizado sem herdar o aprendido é o efeito Baldwin computacional (Hinton e
  Nowlan 1987; Whitley et al. 1994; Fernando et al. 2018). Separar o instintivo do aprendido num mesmo agente já foi feito (Hallawa et
  al. 2021).

## 1. A pergunta

O Matheus quer duas coisas:
1. **Cada entidade tem um código genético:** um registro do que ela é ao nascer, diferente do que ela aprende na vida.
2. **Uma entidade pode gerar o código genético de outra,** e o conjunto vira um ecossistema: pets que têm filhotes, donos que trocam e
   cruzam pets, e entidades que projetam um genoma de propósito.

## 2. O que já existe (REPOSITÓRIO)

O projeto já tem pedaços de genoma, cada um num lugar e com a sua rng. Nenhum deles junta tudo.

| sistema | o que é inato hoje | onde | sorteio | herdável hoje |
|---|---|---|---|---|
| temperamento (v1) | 4 eixos do motor e os eixos do ovo | `digilab/temperamento.py` | `rng_ovo` da semente | **sim:** média dos pais mais ruído, cortado na faixa (`digilab/heranca.py`) |
| espécie (v1) | o brasão: brasa, cirro, ferrugem, limo | `digilab/evolucao.py`, `heranca.py` | da semente | **sim:** sorteada entre as dos pais |
| frutas (N4) | a neofobia e a preferência inata por fruta | `digilab/frutas.py`, `GenomaFrutas` | `frutas-ovo` | não (F5 prevê, ainda sem herança) |
| paladar (#310) | o peso de cada qualidade do gosto, `h_q` | `digilab/genoma_paladar.py`, `GenomaPaladar` | `paladar-ovo` | não (PL-2 prevê) |
| o prior do cérebro A | os coeficientes do instinto vezes S, o ponto de partida dos lobos | `digilab/policies/lobos.py` (`_tabela_prior`) | nenhum: **igual em todo pet** | — |
| o corpo químico | taxas, meias-vidas, receptores e estímulos | `digilab/corpo.py`, `ConfigCorpo` | nenhum: **igual em todo pet** | — |
| a fisiologia por espécie (#260) | um perfil por espécie sobre o grafo do corpo (camadas 1 a 3) | `docs/futuro/fisiologia_especies.md` | — | desenho; FE-3 aberta |

**O que a v1 mediu** (`docs/historico/claude/v1_pesquisa.md`, a seção da linhagem): no E1, o genoma da v1 explicou **4,9%** da variância
do desempenho, e o gate falhou. Depois disso, a linhagem parou como pesquisa (decisão do Matheus, 2026-09-29) e ficou como mecânica de
jogo, na herança dos pets v4. Um genoma com aptidões por indivíduo foi descartado, porque ajustar o genoma para passar o gate viciaria o
teste.

## 3. O genoma da V2 (proposta)

### 3.1 Um registro único, com uma seção por sistema

O genoma vira **um registro só** (EG-1), dado no log do pet, com uma seção por sistema. Cada seção tem a sua rng derivada da semente
do ovo, como hoje, e a sua chave desligada.

| seção | o que carregaria | o efeito no fenótipo | a ligação |
|---|---|---|---|
| `temperamento` | os eixos de hoje | o de hoje | v1 |
| `especie` | o brasão, e por ele o perfil da espécie | a média das outras seções (FE-1, FE-3) | #260 |
| `corpo` | desvios da camada 2: taxas, meias-vidas, sensibilidade de receptor, raio de um sentido | o grafo do corpo com os números trocados, checado antes da vida | #260, camada 2 |
| `paladar` | os `h_q` de hoje | o canal `gosto` | #310 |
| `frutas` | a neofobia e a preferência inata | o de hoje (N4) | F4, F5 |
| `prior` | **desvios do prior do instinto** em algumas regras do cérebro A | o ponto de partida dos lobos; o aprendido continua por cima | Baldwin (EG-2) |
| `plasticidade` | o passo, o teto e a sensibilidade por canal de reforço | o quanto e de onde o pet aprende | H-R4; H3 do plano da V2 |

**O escopo e o que não está definido** (DECIDIDO pelo Matheus em 2026-10-21, a GI-5; `docs/futuro/gate_integracao_pet.md`, seção 6): as seções acima mudam
**valores** (os traços do corpo, os desvios do prior do A, a plasticidade e as que já existem). **Codificar a topologia** ou outra
estrutura de uma rede neural **não está definido:** o A não tem topologia para codificar, porque a estrutura dele (as regras, os
candidatos e as entradas) é fixa. A codificação indireta da EG-3 gera pesos, não topologia. Evoluir a arquitetura do cérebro só entra
se o Matheus escolher um cérebro com estrutura variável (a GI-1) e uma tarefa própria a especificar. Este desenho não a promete.

### 3.2 As regras

- **O genoma é dado no log.** Ele entra no evento de origem do pet (o `origem` da v1 já leva os traços herdáveis e os sha256 dos logs
  dos pais), e o replay o recalcula e confere. Event sourcing continua: nada de estado salvo.
- **Genoma vazio é a vida de hoje.** Sem o registro, ou com as seções nos valores de hoje, a vida sai byte a byte. O gabarito vai num
  commit antes.
- **O aprendido nunca entra no genoma** (EG-5). Herdar o que o pai aprendeu é herança lamarckiana; herdar só o ponto de partida é o
  efeito Baldwin (Whitley et al. 1994 compara os dois). O projeto já tem a regra (`docs/DEFINICOES_FRUTAS_V2.md`, 2.4; `heranca.py`
  não herda nada aprendido).
- **Do genótipo ao fenótipo, uma função declarada, em inteiros.** Na primeira passada a codificação é **direta** (EG-3): um gene por
  número. Uma codificação indireta, em que um genoma pequeno gera muitos pesos (Stanley 2007; Stanley et al. 2009), fica para depois.
- **Os traços vêm correlacionados** (Sih, Bell e Johnson 2004). Sortear cada seção de forma independente contradiz isso. A espécie é o
  primeiro lugar natural para a correlação.

## 4. As três formas de gerar o genoma de outro

### 4.1 Reprodução: dois pets, mistura e mutação

- **Como:** o filhote recebe, seção a seção, uma mistura dos pais mais uma mutação pequena (EG-4). É o que a v1 já faz para o
  temperamento (média mais ruído) e para a espécie (sorteio entre os pais).
  - Os números contínuos herdam a média mais ruído.
  - Os discretos são sorteados entre os pais.
  - Os desvios do prior herdam por gene.
  - Tudo numa rng própria, `heranca`, derivada da semente da herança.
- **Onde vive:** no `Grupo` (dois pets no mesmo `Mundo`), como um evento do grupo que cria um pet novo com o genoma do evento.
- **A literatura:**
  - evolução de morfologia e controle juntos (Sims 1994, as duas versões);
  - evolução digital com réplica e mutação (Ray 1993; Ofria e Wilke 2004; Lenski et al. 2003);
  - morfologias evoluídas que aprendem mais rápido, o efeito Baldwin morfológico (Gupta et al. 2021).
- **A calibração externa da herdabilidade:**
  - **~52%** da variação de personalidade animal é genética aditiva (Dochtermann, Schwab e Sih 2015);
  - em cães, a raça explica só **9%** da variação de comportamento individual (Morrill et al. 2022).
  - O 4,9% do E1 fica muito abaixo dos dois.

### 4.2 O ecossistema com donos: troca e cruzamento

- **Como:** o dono escolhe quais pets cruzar (**seleção**) e cria cada um (**criação**). O genoma viaja como dado: o `origem` da v1 já
  permite pais de donos diferentes, com os sha256 dos logs deles.
- **O precedente:**
  - o Creatures fez isso em escala: norns com genoma, trocados e cruzados entre jogadores (Grand e Cliff 1998; Cliff e Grand 1999);
  - a evolução interativa usa o humano só como seleção (Takagi 2001; Secretan et al. 2011, o Picbreeder; Dawkins 1995, os biomorphs).
- **A restrição:** a fadiga do avaliador é o gargalo de qualquer linhagem que dependa de escolha explícita (Takagi 2001). No jogo, a
  seleção pode sair do uso: quem o jogador escolhe para lutar, cuidar, cruzar.
- **Confiança:** um genoma vindo de outro jogador é dado de fora. Ele é conferido (faixas, seções, sha256) e falha alto se for inválido.

### 4.3 Uma entidade que projeta o genoma de outra de propósito

É a forma nova do pedido. **Não achei nesta busca um ecossistema de vida artificial em que um agente de dentro do mundo projete o genoma
de outro agente.** Fica SEM FONTE (é uma busca curta: evidência fraca).

**Os precedentes que existem e o que cada um mostra** (verificados por metadados e resumo):

| referência | o que faz | a distância do pedido |
|---|---|---|
| Ha, Dai e Le (2016), HyperNetworks, arXiv:1609.09106 | uma rede gera os pesos de outra; o próprio resumo chama a hiper-rede de genótipo e a rede principal de fenótipo | treinada por gradiente, não é uma entidade do mundo |
| Stanley (2007), CPPN; Stanley et al. (2009), HyperNEAT | um genoma pequeno gera o padrão de conexões de uma rede grande (codificação indireta) | a geração é evoluída, não projetada com um objetivo |
| Wang et al. (2019), POET, arXiv:1901.01753; Dennis et al. (2020), PAIRED/UED, arXiv:2012.02096 | um algoritmo gera os ambientes em que outros agentes aprendem | projeta o ambiente, não o genoma |
| Kriegman et al. (2020), PNAS | métodos de IA projetam organismos in silico para uma função, e o projeto vira um sistema vivo | o projetista é externo ao mundo dos organismos |
| Gibson et al. (2010); Hutchison et al. (2016), Science | humanos projetam e sintetizam o genoma de uma bactéria | a biologia; o projetista é humano |

**Três projetistas possíveis no Digilab:**
1. **o jogador, com uma ferramenta:** um editor de genoma no jogo. É uma mecânica de jogo, sem pergunta de pesquisa nova;
2. **uma entidade projetista com objetivo,** fora dos pets: por exemplo, um "criador" que escolhe o genoma do próximo ovo para
   maximizar o desempenho no ambiente. É um otimizador num nível acima, perto da meta-aprendizagem pelo efeito Baldwin (Fernando et al.
   2018);
3. **um pet que projeta o filho:** um pet com o planejador do J5 usa o próprio modelo do mundo para escolher o genoma do filho.

**O risco central da terceira forma:** se o projeto lê o que o pai aprendeu (o modelo do mundo dele), o aprendido passa ao filho por
outro caminho. É herança lamarckiana por um agente. Isso só entra como **um canal declarado e separado** (o "canal de projeto"), num
braço próprio, nunca escondido dentro do genético (EG-5).

## 5. Criar × selecionar

- **A lacuna:** não localizamos trabalho que separe o efeito da criação pelo usuário do efeito da seleção pelo usuário em agentes
  artificiais. A evolução interativa tem o humano só como seleção; o aprendizado por feedback humano tem o humano só como treinador; o
  Creatures teve os dois, com registro descritivo.
- **A ressalva:** é o resultado negativo de uma busca lexical, e ausência em busca por palavra-chave é evidência fraca. Registrar como
  "não localizamos", nunca como primazia.
- **O desenho** (H3 do `docs/PLANO_V2_PESQUISA.md`, fase 3): um fatorial criação (dono coerente × aleatório) × seleção (a escolha ×
  o acaso).
  - **A forma 4.3 acrescenta um eixo, o projeto,** e o fatorial vira 2 × 2 × 2. Recomendo **não** abrir esse eixo na primeira passada
    (EG-6).
- **O pré-requisito:** um genoma com variância herdável medida, com plano e gate próprios, antes do fatorial (o E1 mostrou 4,9%). Nada
  se ajusta no genoma olhando o gate.
- **A medida:** o desempenho no próprio ambiente da V2 (tempo fora de privação, saúde, acerto), nunca a força na arena, que mede o
  arquétipo.

## 6. Onde entra no roadmap

Na **fase 3** (genoma e gerações), na ordem:

| passo | o quê | depende de |
|---|---|---|
| G0 | o registro do genoma no log e o replay, atrás de chave (genoma vazio = vida de hoje) | só infraestrutura |
| G1 | a variância herdável: a h² de cada seção no mundo da V2, com plano próprio | G0; o corpo e o paladar (já na `main`) |
| G2 | a reprodução no `Grupo`: dois pets, um ovo | os **dois pets aprendendo de verdade** (`docs/futuro/dois_pets.md`) |
| G3 | o fatorial criação × seleção (H3) | G1 e G2 |
| G4 | o ecossistema com donos | a fase 2 (humanos) e o jogo |
| G5 | o projeto deliberado | uma pergunta própria, depois do G3 |

**O J8** (a escada de cognição social: tradição e convenção) depende de gerações, então depende do G2.

**A linha de base integrada** (DECIDIDO pelo Matheus em 2026-10-21, a GI-4; `docs/futuro/gate_integracao_pet.md`; não muda a EG-7): o G1 e o G2 só medem
ou reproduzem sobre um pet que passou no **Gate I** (o corpo químico, o mundo, o aprendizado na vida e o replay no mesmo pet). Sem
isso, a h² mediria um pet que não junta as peças, e uma geração herdaria de um pet que não aprende no mundo. **O G0 pode vir antes**,
porque é só infraestrutura (o genoma no log e o replay, com o genoma vazio = a vida de hoje) e não mede nada. O Gate I é um marco do
`docs/ROADMAP_V2.md` (seção 8), com tarefa e plano em `docs/TAREFA_V2_GATE_I.md` e `docs/PLANO_ANALISE_V2_GATE_I.md`, e ainda não
está implementado.

## 7. Riscos

| # | risco | o que o desenho faz |
|---|---|---|
| RE-1 | **uma espécie domina:** com a espécie herdada, a seleção a fixa em poucas gerações, e se mede a espécie, não o genoma (o conflito 3 do `docs/PLANO_LINHAGEM_ALIFE.md`) | a espécie fica fixa por linhagem nos experimentos (EG-8) |
| RE-2 | **ajustar o genoma para passar o gate** | o G1 tem plano registrado antes, e o genoma não se calibra olhando o gate (a lição do E1) |
| RE-3 | **Lamarck pela porta dos fundos:** o projeto (4.3) ou um gene que copie o aprendido | a EG-5; o canal de projeto separado e declarado |
| RE-4 | **o custo:** gerações de vidas inteiras | as vidas da V2 levam segundos; o G1 dá o custo antes do G3 |
| RE-5 | **a diversidade colapsa** | medir a diversidade de genomas por geração; a busca por diversidade de qualidade (Pugh et al. 2016) é a referência, se for preciso |
| RE-6 | **a fadiga do dono** na seleção explícita | a seleção pelo uso (4.2) |

## 8. Decisões do Matheus

**DECIDIDAS em 2026-10-14: EG-1 a EG-8, todas como recomendado** (a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| EG-1 | Um genoma ou vários | **um registro único com seções**, cada uma com a sua rng e a sua chave | vários: cada sistema herda de um jeito, e a h² e o fatorial não têm um objeto só para medir |
| EG-2 | O prior do cérebro no genoma | **sim, como desvios herdáveis do prior do instinto, começando por poucas regras.** É o efeito Baldwin e não é novidade (Hinton e Nowlan 1987; Fernando et al. 2018) | não: o cérebro fica igual em todo pet, e o genoma só mexe no corpo e no gosto; a pergunta Baldwin (o E4 arquivado) não volta |
| EG-3 | A codificação | **direta na primeira passada,** um gene por número | indireta já: um mapa a mais para depurar antes de saber se há variância herdável |
| EG-4 | A recombinação | **por seção:** média mais ruído nos contínuos e sorteio nos discretos, como a v1 | uma regra só para tudo: a espécie e os pesos herdariam do mesmo jeito, sem sentido biológico nem de jogo |
| EG-5 | O aprendido | **nunca no genoma;** o projeto a partir do aprendido só como canal declarado num braço próprio | misturar: o resultado não separa Baldwin de Lamarck, e a fase 3 não responde nada |
| EG-6 | A terceira forma (projetar) | **pergunta, não mecânica, até o G3:** o editor do jogador é jogo; a entidade projetista é pesquisa depois | abrir já: o fatorial ganha um eixo sem o genoma ter variância medida |
| EG-7 | O lugar no roadmap | **fase 3, depois dos dois pets aprendendo de verdade e antes do J8** | antes: a reprodução no grupo não tem os dois pets; depois do J8: a tradição fica sem gerações |
| EG-8 | A espécie nos experimentos | **fixa por linhagem;** a espécie herdada fica no jogo | herdada na pesquisa: a seleção mede a espécie dominante (RE-1) |

## 9. Referências

As já VERIFICADAS na revisão (`docs/referencias/*.csv`), conferidas por metadados e resumo:

| referência | DOI | o que sustenta aqui |
|---|---|---|
| Ray (1993). Artificial Life 1(1-2) | `10.1162/artl.1993.1.1_2.179` | Tierra: programas autorreplicantes que evoluem por seleção natural |
| Ofria e Wilke (2004). Artificial Life 10(2) | `10.1162/106454604773563612` | Avida: evolução digital controlada, com tratamentos e controles |
| Lenski et al. (2003). Nature 423 | `10.1038/nature01568` | uma função complexa surge por passos simples em evolução digital |
| Sims (1994). SIGGRAPH; Artificial Life 1(4) | `10.1145/192161.192167`; `10.1162/artl.1994.1.4.353` | morfologia e controle evoluídos juntos; a competição como pressão seletiva |
| Grand e Cliff (1998). Auton Agents Multi-Agent Syst | `10.1023/a:1010042522104` | o Creatures: rede e bioquímica especificadas por genoma |
| Cliff e Grand (1999). Artificial Life 5(1) | `10.1162/106454699568683` | o ecossistema dos jogadores: norns trocados e cruzados em escala |
| Hinton e Nowlan (1987). Complex Systems 1 | sem DOI | o efeito Baldwin computacional |
| Whitley, Gordon e Mathias (1994). PPSN III | `10.1007/3-540-58484-6_245` | Lamarck × Baldwin comparados |
| Fernando et al. (2018). GECCO'18 Companion | `10.1145/3205651.3205763` | a evolução produz um prior que acelera o aprendizado, sem herdar o aprendido |
| Hallawa et al. (2021). GECCO'21 Companion | `10.1145/3449726.3459475` | o instintivo e o aprendido separados num mesmo agente |
| Gupta et al. (2021). Nat Commun 12 | `10.1038/s41467-021-25874-z` | morfologias evoluídas aprendem mais rápido |
| Dochtermann, Schwab e Sih (2015). Proc R Soc B | `10.1098/rspb.2014.2201` | ~52% da variação de personalidade animal é genética aditiva |
| Morrill et al. (2022). Science | `10.1126/science.abk0639` | a raça explica 9% do comportamento individual em cães |
| Sih, Bell e Johnson (2004). Trends Ecol Evol | `10.1016/j.tree.2004.04.009` | os traços vêm em síndromes correlacionadas |
| Takagi (2001). Proc IEEE | `10.1109/5.949485` | a evolução interativa: o humano como seleção; a fadiga do avaliador |
| Secretan et al. (2011). Evol Comput | `10.1162/evco_a_00030` | o Picbreeder: linhagens por seleção humana colaborativa |
| Dawkins (1995). The Pattern Book | `10.1142/9789812832061_0004` | os biomorphs: seleção cumulativa interativa |
| Pugh, Soros e Stanley (2016). Front Robot AI | `10.3389/frobt.2016.00040` | a busca por diversidade de qualidade |

As novas, conferidas nesta tarefa (2026-10-14) no Crossref ou no arXiv, por metadados e resumo, sem `update-to`:

| referência | DOI ou id | o que sustenta aqui |
|---|---|---|
| Ha, Dai e Le (2016). HyperNetworks | arXiv:1609.09106 | uma rede que gera os pesos de outra, descrita no resumo como genótipo e fenótipo |
| Stanley (2007). Genet Program Evolvable Mach | `10.1007/s10710-007-9028-8` | a CPPN: uma abstração do desenvolvimento, codificação indireta |
| Stanley, D'Ambrosio e Gauci (2009). Artificial Life 15(2) | `10.1162/artl.2009.15.2.15202` | o HyperNEAT: a CPPN gera a conectividade de redes grandes |
| Wang, Lehman, Clune e Stanley (2019). POET | arXiv:1901.01753 | os problemas (ambientes) gerados pelo próprio algoritmo enquanto os resolve |
| Dennis et al. (2020). PAIRED/UED | arXiv:2012.02096 | o desenho de ambientes sem supervisão |
| Kriegman, Blackiston, Levin e Bongard (2020). PNAS | `10.1073/pnas.1910837117` | IA projeta organismos in silico para uma função, depois construídos |
| Gibson et al. (2010). Science | `10.1126/science.1190719` | uma célula controlada por um genoma sintetizado quimicamente |
| Hutchison et al. (2016). Science | `10.1126/science.aad6253` | o projeto e a síntese de um genoma bacteriano mínimo |

**SEM FONTE:**
- um agente de dentro de um ecossistema de vida artificial que projete o genoma de outro (não achei nesta busca; evidência fraca);
- as seções do genoma, a codificação e as regras de recombinação deste desenho;
- todo número.
