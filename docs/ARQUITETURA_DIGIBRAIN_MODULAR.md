# Arquitetura do DigiBrain modular (2026-10-24)

**Status:**
- **A direção está DECIDIDA pelo Matheus em 2026-10-24** (o PROMPT MESTRE, repassado pelo Gerente; o texto integral fica fora do
  repositório, em `_ref/TAREFA_PROMPT_MESTRE_MODULAR.md`):
  - o produto jogável vem primeiro;
  - o DigiBrain caminha para um cérebro **modular;**
  - o cérebro A fica como linha de base, controle e fallback condicionado.
- **Todo o resto deste documento é PROPOSTO:** as interfaces, os nomes dos módulos, a forma do estado, a ordem e os critérios. Nada aqui
  está implementado. As decisões técnicas DM-1 a DM-9 estão DECIDIDAS (seção 13, 2026-10-24 e 2026-10-25); a especificação é a próxima entrega.
- O estado real de cada peça está em `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`. As tarefas estão na seção 12.

**Regras deste documento:**
- Não fixar uma topologia final antes da pesquisa que a justifique.
- Cada peça leva uma marca:
  - **[EXISTE]:** está no código da `main`;
  - **[MECANISMO]:** mecanismo transferível de uma fonte verificada;
  - **[INSPIRAÇÃO]:** fonte de jogo ou de desenho, que não prova arquitetura;
  - **[HIPÓTESE]:** aposta nossa, a testar.
- Só referências VERIFICADAS (a skill `literatura-digilab`); onde não há, SEM FONTE. Nenhuma alegação de novidade.
- Os números novos são PROPOSTOS e SEM FONTE.

## 1. O que o cérebro precisa fazer

Pelo pedido do Matheus, o DigiBrain modular deve ter:
1. **estado interno dinâmico** que persiste entre decisões;
2. **memória** (associativa e episódica, com consolidação);
3. **aprendizagem durante a vida;**
4. **sinais do corpo e da bioquímica** que mudam a atividade e a aprendizagem;
5. **uma decisão rastreável**, com o motivo registrado.

Ele deve ser mais do que um gerenciador de estados, uma coleção de regras narrativas ou uma LLM que escolhe ações.

**Para o produto,** a primeira capacidade a servir é a do MVP (`docs/PRODUTO_VISAO.md`): o pet percebe uma comida posta no cenário,
decide ir, navega, come, e a consequência muda o corpo e o comportamento depois.

**O que o A já mostra** (a auditoria, seção 2):
- uma política aprendida sobre as regras do instinto aprende pouco no mundo (o J1 e o alvo aprendido falham);
- o planejador revaloriza pela mão (o G-T1 do J5 passa);
- a competição entre regras ajuda a homeostase (#396);
- a memória de episódios muda a escolha da fruta, com efeito pequeno (N6).

Essas são **as peças candidatas** a módulos, não o cérebro final.

## 2. Os módulos

Os nomes da lista do Matheus, conferidos com os documentos:
- percepção;
- memória e estado afetivo;
- impulsos/motivações;
- decisão/arbitragem;
- aprendizagem/plasticidade;
- personalidade;
- fisiologia/necessidades;
- genoma/hereditariedade.

O `docs/PLANO_V2_PESQUISA.md` (seção 3) e o `docs/research/digibrain/` usam os mesmos blocos com outras palavras ("estado interno",
"contexto e memória", "sistemas de comportamento", "arbitragem", "reforço → aprendizado local"). Abaixo, um módulo por responsabilidade.
**O que é "módulo":** um contrato (entradas, estado, saídas, regra de atualização, rng), não um arquivo nem uma rede.

| módulo (PROPOSTO) | da lista do Matheus | responsabilidade | entradas | estado que guarda | saídas | o que já existe |
|---|---|---|---|---|---|---|
| **M-SENS, codificação sensorial** | percepção | transformar a Observação do contrato em traços e eventos sensoriais | a Observação (os `vistos` pelo cone, os obstáculos, o contato, o resultado percebido, os cheiros, os sons) e os receptores do corpo | a habituação e a novidade por estímulo | traços sensoriais, eventos ("comida nova à vista") | [EXISTE] o lobo `percepcao` (`lobos.py:405-410`), a `PercepcaoContrato` da P4 (`mundo.py:311`), os receptores (`motor_corpo.py:92-133`) |
| **M-ESTADO, estado dinâmico** | memória e estado afetivo | manter um estado interno que persiste e decai entre decisões | os traços sensoriais, os afetos, a intenção anterior | um vetor de estados com dinâmica no tempo (forma na DM-1) | o contexto para impulsos, memória e arbitragem | **não existe no A.** O B tem uma célula recorrente (CfC) e não aprendeu |
| **M-AFETO, afetos e moduladores** | memória e estado afetivo; fisiologia | ler o corpo químico e devolver o estado afetivo e os ganhos que modulam o resto | os receptores (fome, higiene, energia, humor, saúde, drives novos, dor, susto) | o afeto corrente | os ganhos de aprendizagem, de exploração e de urgência | [EXISTE] o corpo químico e o `sinal_corpo` por canal. **Não existe** a modulação da aprendizagem pela química (o R3 do `digibrain_v3_e0.md`; os hormônios H1 a H3, propostos) |
| **M-IMPULSO, impulsos e circuitos de comportamento** | impulsos/motivações | propor intenções candidatas com urgência, por sistema (comer, descansar, brincar, explorar, social, banheiro) | drives, traços sensoriais, estado | — | propostas (intenção, alvo, urgência) | [EXISTE] o lobo `impulsos` (as regras do instinto) e a disputa das regras urgentes (V3-3/4) |
| **M-MEM, memória** | memória e estado afetivo | guardar e recuperar associações e episódios; consolidar | eventos, consequências, afeto, contexto | as associações; os episódios recentes, duradouros e centrais | lembranças recuperadas pelo contexto, valores associados | [EXISTE] em parte: o N6 (só a fruta), a memória por espaços (só no bandit da v1), a história (só a fala). Detalhe na seção 5 |
| **M-ARB, arbitragem** | decisão/arbitragem | escolher uma intenção entre as propostas, com as lembranças, os valores aprendidos e a personalidade | propostas, lembranças, valores, estado | — | a Intenção escolhida, com o motivo | [EXISTE] o lobo `decisao` (pesos L1 e sorteio), a disputa (V3-3/4), o termo do planejador |
| **M-PLAST, plasticidade** | aprendizagem/plasticidade | mudar associações, valores e parâmetros com a consequência, com o ganho que o M-AFETO dá | consequência (corpo e mundo), traço de elegibilidade, ganhos | — (muda o estado dos outros módulos) | atualizações registradas | [EXISTE] a regra L1, o traço, o `ModeloMundo` (desfecho, mapa) |
| **M-PERS, personalidade** | personalidade | os traços inatos (do genoma) e as facetas adquiridas (da memória consolidada), que pesam a arbitragem e a aprendizagem | o genoma; a consolidação | as facetas adquiridas | os pesos de personalidade | [EXISTE] o temperamento (só modula o bandit da v1). As facetas adquiridas **não existem** |
| **M-ADAPT, adaptador cérebro-corpo-motor** | fisiologia/necessidades (a ponte) | a fronteira: a Observação entra, a Intenção sai; o motor executa e devolve a consequência | o motor | — | a Observação; a Intenção ao controlador | [EXISTE] o contrato da P4 no Python (as chaves `contrato`, etapas 1 a 3) e no POC TS; o `Protocol` `Politica` |
| **M-GEN, genoma (futuro)** | genoma/hereditariedade | a origem dos parâmetros inatos de **todo** módulo (não só do prior do A) | — | — | os parâmetros iniciais | [EXISTE] só o paladar e o temperamento; o G0 não existe |
| **M-EXPR, expressão** | (fora do cérebro) | transformar estados e evidências em texto ao jogador, fiel ao que está registrado | o motivo, as lembranças recuperadas, o estado | — | a fala | [EXISTE] a história, o motivo, a fala por LLM (com três lacunas de fidelidade, auditoria seção 4) |

**O que fica no motor, fora do cérebro:**
- o corpo químico (fisiologia/necessidades);
- a física e o controlador;
- o mundo.

O cérebro só os vê pelos receptores e pela Observação. A G-RECEPTOR e o G-SEM-DIRECAO continuam valendo.

## 3. As distinções que o desenho mantém

| coisa | o que é | onde mora | muda como |
|---|---|---|---|
| **neurônios / estados dinâmicos** | o estado do M-ESTADO e do M-AFETO, com dinâmica e decaimento | o cérebro, por pet | a cada tick ou decisão, pela regra do módulo |
| **memórias episódicas** | registros de experiências: contexto, participantes, corpo e afeto, ação e consequência | o M-MEM | codificadas no evento; consolidadas ou esquecidas |
| **associações aprendidas** | ligações estímulo-ação-consequência e valores | o M-MEM e o M-PLAST | pela plasticidade, com a consequência |
| **personalidade inata** | traços que vêm do genoma (hoje, o temperamento e o paladar) | o M-GEN e o M-PERS | **não muda na vida** |
| **facetas adquiridas** | inclinações que a experiência consolidada forma | o M-PERS | devagar e de forma rastreável: cada mudança aponta os episódios que a causaram |
| **expressão textual** | o que o pet diz ao jogador | o M-EXPR, fora da decisão | gerada a partir do registro; **nunca diz que uma lembrança causou uma escolha sem o registro e a demonstração disso** |

## 4. O ciclo de uma decisão (PROPOSTO)

1. O M-ADAPT entrega a Observação. O M-SENS a codifica.
2. O M-AFETO lê os receptores e atualiza o afeto e os ganhos.
3. O M-ESTADO se atualiza.
4. O M-IMPULSO propõe intenções.
5. O M-MEM recupera pelo contexto.
6. O M-ARB escolhe a Intenção. O motivo registra quem pesou quanto (as contribuições por módulo, como o motivo de hoje faz por lobo).
7. O M-ADAPT entrega a Intenção ao controlador do motor.
8. A consequência volta:
   - o M-PLAST atualiza;
   - o M-MEM codifica o episódio;
   - a consolidação roda no seu próprio ritmo.

**Cada passo entra no registro da decisão:** é o que permite a sonda "quem decidiu", a fidelidade da fala e o replay.

## 5. A memória autobiográfica na arquitetura

**A direção do Matheus:** o *Dwarf Fortress* é referência de **desenho** para memória, personalidade, estado interno e consequências
narrativas. A memória pretendida distingue quatro coisas:
1. **a associativa** (estímulo, ação, consequência);
2. **a episódica/autobiográfica** (contexto, participantes, corpo e afeto, consequência);
3. **a consolidação** (recente → duradoura → central);
4. **a influência causal** (lembranças recuperadas mudam decisões e, devagar e de forma rastreável, as facetas e os valores).

**O que existe** está na auditoria, seção 4:
- nenhuma memória muda a personalidade;
- não há memória central;
- a recuperação contextual só existe no N6 (a fruta);
- a história não decide.

**O confronto com o adendo DF:** o `docs/ADENDO_MEMORIA_EMOCAO_DF.md` (linhas 149-153, texto de 2026-09-25) põe fora de escopo
"Memórias mudando o temperamento ao longo da vida (reabre o confundidor cuidado × treino; exige desenho próprio)".
- **O que muda:** a direção nova planeja a consolidação autobiográfica e a influência gradual como parte futura do cérebro modular.
- **A proposta:**
  - a influência vai nas **facetas adquiridas** (M-PERS), nunca no **temperamento inato**, que continua só do genoma. Assim se preserva a
    separação entre o inato e o adquirido, e o confundidor do adendo fica isolado;
  - a pergunta do efeito do dono está encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`), e esta frente não a reabre: ela pergunta sobre a
    memória do pet, não sobre o dono.
  - É a DM-6.
- **Recuperação determinística:** o DigiLab escolheu o replay determinístico. Se a recuperação for contextual e determinística (a pista
  é o contexto, e o empate se desfaz por uma ordem fixa ou por uma rng própria derivada da semente), **isso é escolha de desenho nossa**.
  As mecânicas do *Dwarf Fortress* estão NÃO VERIFICADAS EM FONTE PRIMÁRIA no repositório (`docs/referencias/v2_referencias_verificadas.csv`,
  a linha da Bay 12), e o DigiLab não precisa copiar os sorteios do jogo.
- **A tarefa:** `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`.

## 6. O que as regras de hoje travam, e a rota versionada

Nenhuma regra de determinismo, replay, hash ou método sai. As que travam o modular ganham uma **rota segura**, PROPOSTA, para o Matheus
decidir (DM-4):

| regra | onde | o que protege | trava o modular? | rota proposta |
|---|---|---|---|---|
| `engine.py` congelado (`ENGINE_SHA256_V0`) | `CLAUDE.md`, `protocol.py:57`, hooks H1 e H1b | a v1 e o hash da arena | **não:** os cérebros entram pelo `Protocol` `Politica`, e o motor cresce por subclasses atrás de chave | fica como está. Se o modular precisar de outro laço de motor, ele entra como camada nova (o precedente do `MotorCorpo` e do `MotorMundo`) ou como nova versão do protocolo, nunca editando o `engine.py` |
| só biblioteca padrão no `digilab/` | `CLAUDE.md`, o preflight pela AST, `tests/test_lobos.py:89-98` (proíbe também `math` no `lobos.py`) | determinismo e porte | **trava** módulos com numpy ou torch no pacote | os módulos do produto em aritmética inteira ou de ponto fixo, sem dependência (o precedente do A e do `ModeloMundo`). Ferramentas de estudo com outra biblioteca ficam fora do pacote (o precedente do `tools/connectome_cerebro_a.py`) e não entram no replay |
| paridade Python/web bit a bit | `CLAUDE.md`; `web/app/CLAUDE.md:15` (o `exp` e o `log` do Chrome diferem no último bit) | o replay no jogo | **trava** módulos em ponto flutuante na web | o mesmo: ponto fixo nos módulos que vão ao jogo (DM-2). O B, em float, só reproduz no mesmo runtime |
| "a web recebe **um** DigiBrain, o escolhido"; o M6 ("o cérebro da web é o A") | `PLANO_V2_PESQUISA.md` (seção 3 e seção 5), `ROADMAP_V2.md`, `CLAUDE.md` | concentrar o custo de paridade | **sim** | **SUPERADAS em 2026-10-24.** A web recebe o DigiBrain modular, por módulos, cada um com paridade e gabarito. O A fica no jogo como o cérebro dos v11 até o modular entrar |
| `AcaoPet` não pode ganhar membros | `PLANO_V2_PESQUISA.md:77`, `ROADMAP_V2.md:37`, `V2_INVENTARIO_JOGO.md:179-182` | a v1 e o bandit | **não mais:** o `ALIVIAR` entrou no fim do enum, com `ACOES_PET_HOJE` (`digilab/events.py:211-222`; `bandit.py:42`) | ações novas no fim do enum, com a lista do bandit fixa; as intenções da tabela 4.3 do `mundo_3d.md` ficam como sub-decisão |
| uma versão de pet por mecânica | `web/app/CLAUDE.md:11` | os saves | não, mas custa | o cérebro modular entra no jogo como **uma versão de pet nova** (v12), e cada mudança de módulo que mude a vida vira uma versão (DM-5) |
| "não aumentar escopo" | `CLAUDE.md` | a deriva | não | continua. O escopo do modular é o das tarefas da seção 12 |
| uma alavanca por vez | `V2_TRABALHO_PARALELO.md:42-43`; `ROADMAP_V2.md:21` | atribuir o efeito à peça certa | em parte | continua na **pesquisa** (a ablação por módulo). O **produto** pode ligar vários módulos juntos, com a ablação medida no protótipo |
| só um chat mexe em `lobos.py` | `ROADMAP_V2.md:99` | conflitos de merge | trava frentes paralelas | um dono por módulo, cada módulo no seu arquivo |

## 7. Onde o cérebro roda

- **Hoje:** a pesquisa fica no Python; o jogo roda o A v11 em TS com paridade bit a bit por componente.
- **A proposta (DM-2):** cada módulo que vai ao produto tem:
  - uma implementação de referência;
  - o espelho na outra linguagem;
  - gabaritos e um G-PAR, como o A v11.
- **A alternativa:** o TS como referência, com a pesquisa rodando no Node. Ela muda o método (a bancada, as sementes e as métricas
  estão no Python), e a recomendação é não ir por ela agora.

## 8. O lugar do cérebro A

- **[EXISTE]** O A continua no jogo como o cérebro dos v11, e como a referência da pesquisa.
- **Baseline e controle:** onde responder a uma pergunta útil, por exemplo "o módulo de memória do protótipo muda a escolha mais que o
  N6 do A?".
- **Fallback condicionado:** só pelos critérios de `docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, decididos antes, que distinguem falha de
  implementação de limitação da arquitetura. **Nunca por impressão nem pela primeira implementação.**
- **Peças do A como módulos candidatos** [HIPÓTESE]:
  - as regras do instinto como M-IMPULSO inicial;
  - a L1 como uma das regras do M-PLAST;
  - o planejador como módulo de previsão;
  - a disputa como M-ARB.
  
  Isso não está decidido (DM-7). Reaproveitar não quer dizer manter o A como cérebro final.
- **Sem rodadas só para validar o A como destino.** A seção 9 da auditoria diz o que pausa e o que muda.

## 9. O genoma futuro

- O `docs/futuro/ecossistema_genetico.md` (EG-1 a EG-8, a GI-5) propõe genes do corpo, **do prior** e da plasticidade.
- Com o modular, "o prior" passa a ser **os parâmetros inatos de cada módulo:** os ganhos do M-AFETO, as constantes de tempo do
  M-ESTADO, as taxas do M-PLAST, os traços do M-PERS e o prior do M-IMPULSO.
- A seção do genoma deixa de ser presa ao A.
- **A topologia continua fora** até um cérebro com estrutura variável ser especificado. Este documento não promete evolução de
  arquitetura neural.
- Nada disso está implementado. O G0 continua sendo só infraestrutura.

## 10. Literatura: o que cada referência sustenta aqui

Conferida pela skill `literatura-digilab` e pelas tabelas de `docs/referencias/`. "Lido" é sempre metadados e resumo, nunca o texto
completo.

| referência | status | o que sustenta, e só isso | uso aqui |
|---|---|---|---|
| Grand, Cliff e Malhotra (1997), `10.1145/267658.267663` | VERIFICADA | o norn tem uma rede para a coordenação sensório-motora e uma bioquímica artificial (metabolismo, hormônios); arquitetura e bioquímica especificadas por um genoma de tamanho variável | [INSPIRAÇÃO] da direção (rede, bioquímica e genética juntas) |
| Cliff e Grand (1999), `10.1162/106454699568683` | VERIFICADA | rede recorrente modular com aprendizado hebbiano e modulação hormonal difusa, especificadas geneticamente | [MECANISMO]: a modulação química da rede e da aprendizagem (M-AFETO → M-PLAST) |
| Grand e Cliff (1998), `10.1023/a:1010042522104` | VERIFICADA, **só metadados** | não sustenta conteúdo | só a existência |
| o manual do Creatures 3; a Creatures Wiki; o openc2e | CORPUS / NÃO VERIFICADA EM FONTE PRIMÁRIA | pista | [INSPIRAÇÃO], nunca "o Creatures faz X" |
| Adams (2019), `10.1201/9780429488337-15` | VERIFICADA (resumo) | só a narrativa emergente | [INSPIRAÇÃO] para a identidade narrativa |
| Adams (2021), `10.1515/9783839453452-007` | VERIFICADA, só título | o *Dwarf Fortress* é objeto de análise acadêmica; **não** valida seus mecanismos | — |
| mecânicas do *Dwarf Fortress* (Bay 12, wiki) | NÃO VERIFICADA EM FONTE PRIMÁRIA | pista de desenho | [INSPIRAÇÃO] da memória (seção 5) |
| Conway e Pleydell-Pearce (2000), `10.1037/0033-295x.107.2.261` | VERIFICADA | a memória autobiográfica no sistema *self-memory* | [MECANISMO] para a memória central e a identidade |
| Nader, Schafe e LeDoux (2000), `10.1038/35021052` | VERIFICADA | relembrar altera a memória | [MECANISMO] para a reconsolidação |
| McGaugh (2005), `10.1101/lm.93405` | VERIFICADA, só título | a excitação emocional modula a consolidação | [HIPÓTESE] (só o título) |
| Raaijmakers e Jakab (2011), `10.3758/s13421-011-0131-y` | VERIFICADA | limita a "disputa por força" entre lembranças | restrição ao desenho da capacidade por slots |
| Castro e Gudwin (2013), `10.4018/jse.2013010102` | VERIFICADA | um módulo de memória episódica por cenas acoplado a uma arquitetura cognitiva | [MECANISMO], **sem** afirmar que a cena recuperada informa a escolha (o CSV não sustenta isso) |
| Jacobs et al. (1991), `10.1162/neco.1991.3.1.79` | VERIFICADA | aprendizado localizado por módulo sob um gate | [MECANISMO] para a arbitragem e o aprendizado por módulo |
| Brooks (1986, 1991); Bryson (2003); Sutton, Precup e Singh (1999) | VERIFICADAS (`docs/referencias/v2_referencias_verificadas.csv`) | arquiteturas por comportamentos e opções | [MECANISMO] para o M-IMPULSO e o M-ARB |
| Lewis e Cañamero (2016), `10.1177/1059712316666331` | VERIFICADA (resumo) | o prazer, ligado ou não a uma necessidade, melhora a viabilidade e a flexibilidade | [MECANISMO] para o M-AFETO |
| Lones, Lewis e Cañamero (2018), `10.1109/TCDS.2017.2775620` | VERIFICADA; o conteúdo não foi lido | não sustenta conteúdo (`DEFINICOES_CORPO_V2.md`) | — |
| Yaeger (1994), PolyWorld | VERIFICADA (sem DOI), pp. 1-10 | as entradas (visão, energia, aleatório) e a visão desenhada | [INSPIRAÇÃO] para o M-SENS |
| Framsticks (Komosiński) | VERIFICADA | a existência do simulador; o cheiro como energia | comparação de modelo de sinal |
| Unreal AI Perception (Epic) | VERIFICADA (sem DOI), cinza | a audição por evento com alcance; os campos do estímulo | [INSPIRAÇÃO] para o M-SENS |
| Molyneux (2001), o postmortem de *Black & White* | VERIFICADA, cinza | uma criatura que aprende e age sozinha; a personalidade se forma no uso, sem elementos aleatórios | bloqueia a alegação de novidade de "ensinado, não roteirizado" |
| Evans (2002), *Varieties of Learning* | VERIFICADA (sem DOI), conteúdo não conferido | só a existência | lacuna aberta |
| CfC (Hasani et al. 2022), `10.1038/s42256-022-00556-7`; NCP (Lechner et al. 2020), `10.1038/s42256-020-00237-3` | CORPUS (pista) | modelo recorrente de tempo contínuo em forma fechada; conectividade esparsa | [HIPÓTESE] para a forma do M-ESTADO (DM-1). **Licenças conferidas em 2026-10-25** (PR #408): o código do CfC e o `ncps` em Apache-2.0; patentes não buscadas; nenhum código copiado (PE-15 feita quanto à licença) |
| NORNBRAIN | software não revisado, "nunca evidência" | estudo de caso; **código em PolyForm Noncommercial 1.0.0, documentação em CC BY-NC 4.0** (`docs/research/digibrain/sources/nornbrain.md:39-40`); declara que ainda não funciona | **o código não pode entrar no produto;** as ideias podem ser estudadas |
| *The Sims*, Tamagotchi | ausentes da literatura do repositório | — | só inspiração de produto, SEM FONTE |
| Hebb; traços de elegibilidade; sistemas complementares de aprendizagem | **revisão feita em 2026-10-25** (`docs/referencias/DM_REVISAO_SUBSTRATO_NEURAL.md`, PR #408; aplicada na espec pelo PR #409) | Hebb (2005 [1949], a descrição da editora); os três fatores e a elegibilidade: Frémaux e Gerstner (2016), Gerstner et al. (2018), Kuśmierz et al. (2017); a memória episódica informando a escolha: Clayton e Dickinson (1998), Gershman e Daw (2017), Lengyel e Dayan (2007) | **continuam SEM FONTE, como escolha nossa:** o integrador em ponto fixo como substrato de criatura; o alívio homeostático como terceiro fator; a regra "o mais recente do lugar manda"; a comparação direta crédito por opção × por janela; a curva das urgências. Os sistemas complementares de aprendizagem não foram buscados |

**Correções que esta revisão achou no próprio repositório** (registradas em `docs/registro/2026-10.md`, sem mudar as fontes):
- o aprendizado hebbiano é do resumo de Cliff e Grand (1999), não do de 1997 (`docs/research/digibrain/mechanisms/associative_memory.md:7`
  e `references/source_index.md:11` atribuem a 1997);
- Grand e Cliff (1998) só tem metadados, e não sustenta conteúdo;
- Adams (2021) é usado como "legíveis como indivíduos com história" (`sources/dwarf_fortress.md`, `mechanisms/personality.md`,
  `mechanisms/episodic_memory.md`), e a tabela não sustenta isso;
- Castro e Gudwin (2013) é usado como "a cena recuperada informa a escolha", e a tabela não sustenta isso;
- o postmortem de *Black & White* é usado em `docs/futuro/mundo_fisico.md:175` para "a criatura copia o jogador", e a tabela não sustenta
  isso;
- as revisões G e H ficam fora das `REGRAS_CITACAO_DIGILAB.md`, que cobrem só as 79 linhas da primeira tabela.

**Sem fonte:** que a modularidade melhore a legibilidade com capacidade igual. Ao contrário: na L1, a camada única foi mais legível que
os lobos (`docs/RESULTADO_V2_L1.md`). Esta arquitetura não promete legibilidade por ser modular. Ela a mede.

## 11. A pergunta científica que continua útil

**A pergunta maior da V2** (`PLANO_V2_PESQUISA.md`, seção 2): "Em que condições a plasticidade durante a vida produz vantagem adaptativa
sobre as predisposições herdadas?"

**No modular** ela vira uma pergunta sobre **os módulos de aprendizagem e memória**, e não uma justificativa para validar o A:
- quanto do comportamento do pet vem do M-MEM e do M-PLAST (desligados, congelados ou com o sinal embaralhado);
- quanto vem do inato (o M-IMPULSO e o M-PERS inato).

A medida é a ablação dentro do mesmo cérebro modular, nos cenários do MVP. O A entra só como baseline, quando a comparação responder a
algo.

## 12. As tarefas

| # | tarefa | arquivo |
|---|---|---|
| 1 | a especificação técnica do DigiBrain modular | `docs/TAREFA_V2_DIGIBRAIN_MODULAR_ESPEC.md` |
| 2 | o MVP do mundo físico integrado ao produto | `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md` |
| 3 | o protótipo e a avaliação dos mecanismos do modular | `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` |
| 4 | a memória autobiográfica com influência causal | `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md` |
| 5 | a integração progressiva do modular no produto | `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md` |
| 6 | os critérios do A como baseline ou fallback | `docs/TAREFA_V2_CEREBRO_A_BASELINE.md` |
| 7 | as fases posteriores (multiplayer, social, genética ampla, comunicação avançada) | `docs/TAREFA_V2_FASES_POSTERIORES.md` |

**A ordem de dependência:**
- **o MVP (2) não espera o cérebro modular:** ele liga o mundo ao jogo com o A v11 como o cérebro do momento, e o cérebro troca depois;
- **a espec (1)** vem antes do protótipo (3) e da memória (4);
- **o protótipo (3)** vem antes da integração (5);
- **os critérios do A (6)** são escritos antes do protótipo ser avaliado.

## 13. Decisões do Matheus

**Todas DECIDIDAS** (a DM-8 em 2026-10-24; as outras em 2026-10-25, no chat da sessão do Gerente, pelas recomendações, com as
condições dele anotadas em cada linha). A DM-5 mudou de v12 para **v13**, porque a v12 ficou com o MVP e o A (MV-1). O que ele pediu ao
fim: **a especificação vem para revisão antes de aprovar implementação ou experimento, comparada com a visão do produto e da pesquisa;
o protótipo não começa até essa revisão.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **DM-1** (DECIDIDA 2026-10-25) | a forma do estado dinâmico (M-ESTADO, M-AFETO) | **começar por integradores com vazamento em ponto fixo** (um estado por variável, com uma constante de tempo), e comparar no protótipo com uma forma recorrente (do tipo CfC) só se a primeira não bastar. **A condição do Matheus:** a especificação descreve separadamente **o substrato neural** do cérebro modular (os neurônios ou unidades, as conexões, a ativação, a plasticidade e como o aprendizado altera o comportamento ao longo da vida); integradores, impulsos e regras de arbitragem, por si só, não bastam para caracterizar o protótipo como cérebro neural. Onde a literatura e a especificação ainda não sustentarem uma escolha, fica explícito como **decisão a pesquisar antes de implementar** | começar pela recorrente: a última (o B) não aprendeu, e o float quebra a paridade. Ficar só no integrador: pode faltar expressividade, e a avaliação do protótipo existe para ver isso |
| **DM-2** (DECIDIDA 2026-10-25) | onde fica a referência de cada módulo | **implementação de referência em Python e espelho TS com G-PAR, em ponto fixo,** como o A v11. **A condição do Matheus:** a paridade não é tratada como evidência de aprendizagem nem de qualidade comportamental | só TS: muda o método da pesquisa. Float: o replay no jogo se perde |
| **DM-3** (DECIDIDA 2026-10-25) | a granularidade do primeiro protótipo | **os módulos que o laço do MVP pede** (M-SENS, M-AFETO, M-ESTADO, M-IMPULSO, M-ARB, M-PLAST, M-ADAPT) e um M-MEM mínimo (a memória episódica de alimentação); o M-PERS e o M-GEN em fases posteriores. **A condição do Matheus:** a memória autobiográfica consolidada fica registrada como **etapa própria** (`docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`), com influência causal futura nas decisões e nas facetas adquiridas | todos de uma vez: nada se atribui a nada, e o protótipo demora |
| **DM-4** (DECIDIDA 2026-10-25) | as rotas versionadas da seção 6 | **aceitar as rotas como estão** (o `engine.py` intacto, o ponto fixo, as ações no fim do enum, a versão de pet nova) | sem rota: cada frente reabre a regra; regras afrouxadas: o replay e a paridade se perdem |
| **DM-5** (DECIDIDA 2026-10-25) | a versão de pet do modular | **v13** para o primeiro pet com o cérebro modular no jogo. **A v12 permanece como o MVP com o A** (MV-1); cada mudança posterior que altere a vida usa uma versão nova | sem versão: os saves quebram. Reusar a v12: o save do MVP muda de cérebro |
| **DM-6** (DECIDIDA 2026-10-25) | a memória que muda a personalidade | **as mudanças aprendidas afetam as facetas adquiridas, nunca o temperamento inato** (seção 5) | no temperamento: o inato e o adquirido se misturam, e a genética mede o que a vida fez |
| **DM-7** (DECIDIDA 2026-10-25) | as peças do A reaproveitadas | **decidir na especificação, módulo a módulo,** justificando cada escolha com a evidência de cada peça. **A condição do Matheus:** o modular não deve ser apenas o A reorganizado | reaproveitar tudo: o modular vira o A com outro nome; nada: perde-se o que funcionou (o planejador, a disputa) |
| **DM-8** (DECIDIDA 2026-10-24) | o que pausa das rodadas do A | **a seção 9 da auditoria:** pausar o piloto e a validação da P4 e a run do Gate I com o A; manter o contrato e os critérios | continuar: a pesquisa segue validando o A e adia o produto; parar tudo: perde-se o contrato do motor, que o MVP usa |
| **DM-9** (DECIDIDA 2026-10-25) | o NORNBRAIN, o CfC e o NCP | **só estudo;** nenhum código do NORNBRAIN (licença não comercial); conferir a licença do CfC e do NCP antes de qualquer reúso | reusar sem conferir: risco de licença no produto |
