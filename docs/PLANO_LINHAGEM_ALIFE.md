# Plano — linhagem por procriação (lente de Vida Artificial)

Status: **encerrado como pesquisa** (decisão do Matheus, 2026-09-29).

- O E1 (natureza × criação) rodou e **o gate falhou**: `docs/PLANO_ANALISE_LINHAGEM.md` e `artifacts_linhagem/natureza_criacao/`.
- Com a espécie fixa, o genoma explica 4,9% da variância, e o IC inclui 0. Com as 4 espécies, a espécie responde por 32% da diferença entre genomas.
- **E2, E3 e E4 ficam arquivados.** A linhagem continua só como mecânica de jogo (herança dos pets v4); aposentadoria, retrato e árvore podem virar desenho de jogo quando o Matheus pedir.
- **Genoma novo com aptidões por indivíduo: descartado.** Na arena da pesquisa o treino é normalizado ao orçamento, e montar um genoma só para o gate passar viciaria o teste.
- **O que o E1 abriu:** a interação dono × ambiente (22% da variância) é a pergunta mais promissora.

O texto abaixo é o planejamento original, mantido como registro.

## 1. Estado real (passo 0)

**Feito, com artefato e testes:**

| tarefa ou espec | evidência |
|---|---|
| arena v1 canônica | `artifacts/`, `test_canonico_intacto.py` |
| ablação treino × cuidado (instinto × bandit) | `artifacts_ablacao/` (2026-09-24). **Não é bloqueio.** Efeito do treino 0,14 [0,00; 0,28]; declarada superada em 2026-09-29. |
| ESPEC_COMBATE_V2 e V21, TAREFA_CORRECAO_COMBATE | `artifacts_combate_v2*`, `artifacts_combate_v21*`; V2C e V21C aprovadas com ressalvas (E2, E4, G6b, G8) |
| ESPEC_EVOLUCAO_COMBATE, pesquisa V2.1 | `artifacts_v21_pesquisa/`, `digilab/evolucao.py` |
| TAREFA_MEMORIA_EXPRESSAO, adendo DF | `artifacts_expressao/`, `artifacts_v1_memoria*`, `artifacts_v1_habituacao/` |
| TAREFA_PERSONALIDADE_OBEDIENCIA | `artifacts_v1_personalidade/` |
| TAREFA_TREINO_SOMBRIO | `artifacts_treino/`, `artifacts_campanha/` |
| TAREFA_PLANILHA_PROGRESSAO | `artifacts_progressao/`, `ConfigEscala` |
| TAREFA_ANALISE_PODER | `artifacts_poder/`, `PLANO_ANALISE.md` |
| confirmatória | `artifacts_confirmatoria/`: hipótese central **REFUTADA** |
| DESIGN_EDUCACAO_HERANCA_LESOES | `artifacts_educacao*` (V3, V3b, V3c), `test_educacao.py` |
| TAREFA_FALA_LIVRE, TAREFA_FRONT_TS, TAREFA_INTERFACE_UP | `artifacts_fala_livre/`, `web/app/` |

**Só especificação (sem código nem artefato):**
- `TAREFA_AFINACAO_BANDIT`: ela pedia para rodar antes do piloto de poder, e o piloto já rodou sem ela.
- `TAREFA_QD_MAP_ELITES`: não existe `digilab_qd/`.
- `TAREFA_CAMPEAO_SECRETO`: depende da QD.
- Em desenho, sem aprovação: `DESIGN_VOZ_PROPRIA` e `DESIGN_EVOLUCAO_CANONICA` (branches locais).

**O que a linhagem já tem pronto** (`digilab/heranca.py`, `ConfigHeranca`, pets web v4):
- cruzamento de **2 genitores adultos**;
- temperamento herdado: a média dos pais + N(0; 0,1), cortado na faixa;
- espécie sorteada entre as dos pais;
- `rng_heranca` própria;
- evento `origem` no log do filho, com o sha256 dos logs dos pais, e `conferir_pais`;
- nada aprendido é herdado;
- na web: Cruzar em Meus pets e a tela Gerações.

**O que falta:**
- 1 genitor (clone com mutação);
- a condição para procriar;
- a aposentadoria;
- aptidões por indivíduo (hoje são fixas por espécie, em `ConfigTreino.aptidao_especie`);
- o desvio de prior (Baldwin);
- o estágio 5 por profundidade de linhagem;
- o replay da cadeia inteira de gerações.

**Nenhuma pré-condição bloqueia o plano.** O ponto crítico é o E1 da seção 5: se o genoma não explica o desempenho, a seleção não tem sobre o que agir.

## 2. Conflitos

1. **"Não aumentar escopo"** (CLAUDE.md, regras). A linhagem é uma mecânica nova e precisa de autorização explícita, como as exceções já registradas.
2. **O vínculo como condição para procriar.** Na personalidade, o vínculo do aleatório (0,607) fica **acima** do atencioso (0,539). O CLAUDE.md pede: "revisar o desenho do vínculo antes de usar como medida de coerência". Com o piso de vínculo, o dono incoerente procriaria mais; isso confunde o 2×2.
   - Além disso, a sombria tem teto de vínculo 0,6 (`CSO.tetoVinc`), então o piso decide sozinho se uma sombria procria.
3. **Espécie dominante (E2, aceita).** A ferrugem vence as outras espécies. Com a espécie herdada, a seleção por desempenho fixa a ferrugem em poucas gerações: mede-se a espécie, não o genoma.
4. **A semente do ovo e a do ambiente são a mesma.** `engine.Motor(semente)` usa a semente para o ambiente, e `temperamento.sortear(semente_ovo)` e `evolucao.ovo` derivam dela. O "efeito do ovo" medido até hoje mistura genoma com a sorte do ambiente: ICC de 0,74 no desenho A do poder, e 8,5–13% da variância na personalidade.
   - Dá para separar sem mexer no `engine.py`: o temperamento já é injetado (`PoliticaBanditPersonalidade(temperamento=...)`), e a espécie vem do `origem`.
5. **Estágio 5 duplicado.** `DESIGN_EVOLUCAO_CANONICA` já propõe um 5º estágio (Mega) por tempo + qualificação + vínculo, só no jogo. Um estágio 5 "por profundidade de linhagem" disputa o mesmo lugar.
   - Além disso, o Python tem 4 estágios (`heranca.ORDEM_ESTAGIOS`, catálogo V2.1). Um estágio novo na pesquisa mexe no catálogo de combate: hash novo e bateria nova.
6. **O Baldwin e o braço instinto.** O prior do bandit é **exatamente** a distribuição da `PoliticaInstinto` (`policies/bandit.py`). Um desvio herdável do prior quebra essa igualdade: o controle instinto deixa de ser o prior do bandit, e a ablação instinto × bandit perde a leitura.
7. **O diálogo como evento (backlog).**
   - Contraria "o que o jogador escreve não ensina o pet" (fala livre) e a decisão de deixar para depois o pet pegar expressões do dono (`DESIGN_VOZ_PROPRIA`, seção 5).
   - Se o evento mudar o pet, ele precisa passar pelo `CanalDeInteracao` e contar no orçamento.
8. **O brasão como alvo (backlog).** Hoje o brasão **é** o rótulo da espécie na tela (brasa = Coragem...). Usá-lo como alvo de caráter exige separar brasão de espécie.
9. **O nome "protocolo v2".** Já existem "combate V2" e "arena V2" (gambits adiados). Sugestão: `linhagem-v1`.

## 3. Arquivos que seriam criados ou tocados (sem código agora)

**Criados:**
- `digilab/genoma.py`:
  - o genoma (temperamento 4 eixos, aptidões 6 com média 1, desvio de prior opcional);
  - os operadores (mutação gaussiana com corte, mistura, renormalização);
  - a `rng_genetica`.
- `digilab/linhagem.py`:
  - a condição de procriar;
  - os eventos `procriacao` e `aposentadoria`;
  - o retrato congelado para sparring;
  - o replay da cadeia desde o primeiro ovo, reusando `conferir_pais`.
- `digilab/policies/bandit_baldwin.py`: uma subclasse com o prior deslocado. O Protocol `Politica` não muda.
- `experiments/run_natureza_criacao.py`, `run_heranca_pais_filhos.py`, `run_linhagem.py` e as configs em `experiments/configs/linhagem/`.
- `artifacts_linhagem/` e `docs/PLANO_ANALISE_LINHAGEM.md` (congelado antes da confirmatória).
- `tests/test_genoma.py` e `tests/test_linhagem.py`: determinismo, replay da cadeia, as rngs separadas, e a v1 e a V3 intactas.

**Tocados:**
- `digilab/heranca.py`: modo de 1 genitor e aptidões. Os 2 genitores de hoje precisam reproduzir igual.
- `digilab/treino_stats.py`: aptidão **por indivíduo**, passada ao `MotorTreino`, em vez de `cfg.aptidao_especie[especie]`.
- `digilab/config.py` (seção 4) e `digilab/protocol.py` (`PROTOCOLO_LINHAGEM_V1`, `PARAMETROS_LINHAGEM_V1`).
- `digilab/metrics.py`:
  - herdabilidade (regressão do filho sobre a média dos pais);
  - resposta à seleção;
  - decomposição cruzada genoma × dono × ambiente, que estende `decomposicao_ovo_braco`.
- `digilab/donos_educacao.py`: a política de escolha do genitor (coerente ou aleatória).
- Na web (depois, só se a pesquisa sustentar):
  - `web/app/motor/` (herança com aptidão, eventos, aposentadoria);
  - Gerações e Meus pets;
  - `mapa_constantes.json`.
- `CLAUDE.md` e `docs/REGISTRO_DESVIOS.md`.

**Não mudam:** `engine.py`, o Protocol `Politica`, o limite do `CanalDeInteracao`, o combate V2/V21C e a v1 canônica.

## 4. Campos novos (todos PROPOSTOS, sem fonte)

`ConfigLinhagem`:

| campo | valor inicial | nota |
|---|---|---|
| `ligada` | False | desligada, as runs antigas não mudam |
| `genitores` | 1 ou 2 | decisão 6.1 |
| `sparring_minimo` | = `ConfigEvolucaoPesquisa.sparring_minimo_adulto` (10) | já especificado |
| `vinculo_piso` | 0,5 | conflito 2.2: talvez trocar por outro critério |
| `falha` | "fim" ou "ovo_neutro" | decisão 6.2 |
| `aposentar_ao_chocar` | True | um pet ativo por vez |
| `fator_lamarck_carater` | 0,0 | caráter aprendido não herda |

`ConfigGenoma`:

| campo | valor inicial |
|---|---|
| `sigma_temperamento` | 0,1 (já existe em `ConfigHeranca`) |
| `sigma_aptidao` | 0,05 |
| `corte_aptidao` | [0,8; 1,2], renormalizado para média 1 |
| `baldwin_ligado` | False |
| `sigma_baldwin` | 0,02 |
| `teto_baldwin` | 0,1 (em log-prior, por ação) |

`ConfigEstagio5`:

| campo | valor inicial |
|---|---|
| `geracoes_necessarias` | N (decisão 6.3) |
| `teto_ganho` | +5% no multiplicador de estágio |
| `formas_por_linha` | 1 |

`PROTOCOLO_LINHAGEM_V1`:

| campo | valor inicial |
|---|---|
| `geracoes` | G = 5 |
| `candidatos_por_geracao` | K = 4 |
| `criterio_selecao` | "arena_mesma_geracao" |
| `orcamento_por_vida` e `duracao` | iguais aos da V3 |
| arena | normalizada (`condicao_neutra`) |
| sementes | ovos de piloto e de confirmatória separados |
| braços | 2×2 |

## 5. Experimentos, em ordem, com gates

Todos usam `metrics.py` (taxa de vitória, Bradley-Terry, JSD, bootstrap sobre ovos) e gravam em `artifacts_linhagem/<exp>/`.

**E1 — natureza × criação (primeiro; viável já no motor atual, sem mecânica nova).**
- **Hipótese:** o genoma (temperamento + espécie) explica parte da taxa de vitória, além do dono e do ambiente.
- **Braços:** um cruzamento completo:
  - G genomas × D donos (atencioso, aleatório, permissivo, relapso) × R sementes de ambiente;
  - **genoma e ambiente separados** (conflito 2.4);
  - uma espécie fixa numa rodada e as 4 balanceadas noutra (conflito 2.3).
- **Métrica:** a decomposição da variância (genoma, dono, genoma × dono, ambiente, resíduo), com IC por bootstrap.
- **Gate (bloqueante para o resto):** a variância do genoma com a espécie fixa, com o IC fora de 0. Se não passar, a linhagem não tem o que selecionar e o plano para aqui.
- **Artefato:** `artifacts_linhagem/natureza_criacao/`.

**E2 — herdabilidade pai-filho (usa o `cruzar` que já existe).**
- **Hipótese:** h² > 0 no desempenho e nos eixos de caráter.
- **Braços:** pares de pais adultos da V3 → filhos criados por um dono fixo (e pelo aleatório como controle).
- **Métrica:** a inclinação filho ~ média dos pais, com bootstrap.
- **Gate:** o IC de h² fora de 0.

**E3 — linhagem 2×2 (depois do E1 e do E2).**
- **Hipótese:** a seleção coerente de genitor soma com a criação coerente ao longo das gerações.
- **Braços:**
  - criação: dono coerente ou aleatório;
  - seleção: melhor dos K na arena da mesma geração, ou um dos K ao acaso;
  - o mesmo orçamento por vida e o mesmo K em todos os braços.
- **Métrica:**
  - a taxa de vitória por geração, comparando **só pets da mesma geração**;
  - o pareamento vale só na geração 1 (mesmos ovos); depois as linhagens divergem e a comparação é entre braços por geração;
  - a resposta à seleção;
  - a deriva do genoma.
- **Gate:** o efeito da seleção coerente na geração G com IC fora de 0; o plano de análise é congelado antes.

**E4 — efeito Baldwin (opcional).**
- **Hipótese:** com o desvio de prior herdável, o comportamento aprendido vira inato ao longo das gerações.
- **Métrica:** a JSD entre o prior e a política adulta cai com a geração no braço Baldwin, e não no controle.
- **Gate:** a diferença de inclinação com IC fora de 0. Registrar o conflito 2.6 antes.

**E5 — estágio 5 (só jogo, depois de resolver o conflito 2.5).**
- **Gate de game design:** o ganho ≤ `teto_ganho`, e uma forma desperta não vence todas as normais (como o S1 das sombrias).

## 6. Decisões em aberto (para o Matheus)

1. **1 ou 2 genitores.**

   | opção | a favor | contra |
   |---|---|---|
   | 1 genitor (clone + mutação) | simples, um pet ativo por vez, leitura limpa da seleção | a diversidade cai rápido |
   | 2 genitores (inclui o retrato de outro jogador) | já existe, e mantém a diversidade | precisa de parceiro, e a espécie do filhote é problema: sortear (hoje), a da mãe (previsível), ou só a mesma espécie (isola a E2) |

2. **Falha na condição de procriar.**
   - **Fim permanente:** a seleção é real, mas pesa no apego e reduz as linhagens.
   - **Ovo sem herança** (temperamento neutro): o jogador continua, mas a pressão seletiva fica fraca.
3. **Números:** o σ da mutação (0,05 / 0,1 / 0,2), N gerações para o estágio 5 (3 / 5 / 7) e o teto de ganho (+3% / +5% / +10%).
4. **O critério de procriar** no lugar do vínculo (conflito 2.2): a obediência, a taxa de cuidado, ou só o sparring.
5. **O estágio 5** (conflito 2.5):
   - o Mega canônico e a forma desperta em trilhas separadas;
   - a forma desperta como variante cosmética do Mega;
   - ou largar o estágio 5 por linhagem.

## 7. Riscos

- **Crescimento de poder sem fim:** os eixos têm corte, as aptidões são renormalizadas para média 1 e o estágio 5 tem teto. Mesmo assim, a seleção empurra para os extremos do corte. Medir a variância do genoma por geração.
- **Apego:** a aposentadoria e o fim da linhagem pesam mais que a morte da v4. Mostrar o retrato do ancestral, a árvore em Gerações e a lembrança do pet (voz própria, marco L).
- **Confundidores:**
  - a espécie dominante (2.3);
  - a semente do ovo junto com a do ambiente (2.4);
  - o vínculo invertido (2.2);
  - o viés de sobrevivência: só quem cumpre a condição procria, então a análise por geração vê pets selecionados;
  - a geração confundida com o tempo de jogo do dono humano (na web).
- **Legibilidade:** o genoma é invisível. Sem mostrar o que foi herdado (Gerações), o jogador não entende por que o filho é diferente.
- **Pouco sinal:** o efeito do dono já é pequeno (confirmatória refutada; V3c: só o limiar de cuidado). A linhagem não o aumenta se o E1 disser que o genoma pesa pouco.

## 8. Backlog de Vida Artificial (avaliação curta)

Para ideias mais amplas (progressão do Tamer, medalhas, economia, Battle Frontier, personalidade contínua, fairness e herança comportamental), ver `docs/IDEIAS_PROGRESSAO_PERSONALIDADE.md`, um prompt de pesquisa aprofundada ainda não rodado.

| item | avaliação |
|---|---|
| ambiente como contexto do bandit e ritmo das necessidades | Viável sem mexer no `engine.py`: ritmos por `Config`, contexto numa política nova. Experimento: 1 × 3 ambientes, JSD entre braços × dentro do braço. Custo médio. Risco: mais features diluem o aprendizado, que já é fraco (JSD ~0,02). |
| brasão como alvo nos eixos de caráter; afinidade com o brasão | Métrica barata de controlabilidade: o alinhamento entre o alvo e o caráter final. Exige separar brasão de espécie (conflito 2.8). Bom candidato depois do E1. |
| diálogo → evento estruturado (lista fechada) | Encaixa no modo livre gravado (o log grava o evento; a LLM só interpreta). Precisa contar no `CanalDeInteracao` e rever a regra da fala livre (conflito 2.7). Se mexer no limite do canal: **bloqueio**. |
| fadiga por sessão caindo com o estágio | Barato: `fadiga_sessao` por estágio em `ConfigTreino`, espelhado no `CTR` da web. Muda a calibração do treino e da sobrecarga; refazer o S1 e o S2. |
| explicitamente fora | nível da jaula ou dos equipamentos, níveis de treino Lv1–3, genoma bioquímico, NEAT no pet, ecossistema aberto |

## 9. Bloqueios

Nenhum item exige alterar o `engine.py`, o Protocol `Politica` ou o limite do `CanalDeInteracao`, desde que:
- os eventos novos entrem por subclasse (precedente: `luta`, `origem` e `decisao_externa` no `MotorEducacao`);
- o temperamento e a aptidão sejam injetados;
- o diálogo, se entrar, conte no orçamento.

Qualquer variante que mude um desses três é **bloqueio** e volta para decisão.
