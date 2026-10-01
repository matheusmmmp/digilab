# Plano de análise — o painel do E1 com a V21D (força do canal de forma)

Status: **registrado antes da run** (2026-09-30). Nada foi rodado para escrever este plano; os números citados vêm de
artefatos que já estavam em disco, e cada um aponta o arquivo. Valores sem fonte estão marcados PROPOSTO.

**Natureza.** A pesquisa ficou sem pergunta viva (confirmatória refutada; E1 com o gate FALHOU; análise dono ×
ambiente). A pergunta adotada: **que propriedade do mapa até o desempenho é necessária para que o dono, ou o genoma,
tenha efeito mensurável?** Aqui o tratamento é o mapa, não o dono. Este plano testa um fator desse mapa, a **força do
canal de forma**, em dois níveis que já existem: a V21C (o E1 como rodou) e a V21D (`docs/VALIDACAO_V21D.md`,
APROVADA). Não é confirmatória da hipótese central nem continua a linhagem (E2–E4 arquivados).

## 1. Ponto de partida (conferido nos artefatos)

| número | valor | artefato |
|---|---|---|
| r² da forma final, 640 pets, 14 categorias (morto é uma) | 0,9585 | `artifacts_linhagem/dono_ambiente/resultado.json` → `rodadas.especie_fixa.forma_final.todos` |
| r² da forma final, **só atencioso e permissivo** (320 pets, 0 mortes), 8 categorias presentes | 0,9290 | idem → `forma_final.so_donos_sem_mortes` |
| frações da variância, 4 donos: G / D / DR / e | 0,0492 / 0,0504 / 0,2231 / 0,6574 | `artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json` → `decomposicao.fracao` |
| IC95 pigeonhole de σ²_G (gate do E1: FALHOU) | [−0,000694; +0,003217] | idem → `gate.ic95` |
| IC95 pigeonhole de frac_D, 4 donos | [0,0; 0,3236] | idem → `ic95_pigeonhole_GR.frac_D` |
| frações, só atencioso e permissivo: G / D / DR / e | 0,0450 / 0,0 (σ²_D = −0,0031) / 0,4695 / 0,4049 | `artifacts_linhagem/dono_ambiente/resultado.json` → `decomposicao_taxa_so_donos_sem_mortes` |
| taxa no painel do furioso (pets do E1, 17 pets) | 0,710 | `…/dono_ambiente/resultado.json` → `forma_final.todos` |
| furioso na validação da V21D: força (bot × bot, ε 0,05) / painel B | 0,722 / 0,675 | `artifacts_combate_v21c/validacao_v21d/criterios.json` |
| 7 formas sem o furioso na faixa [0,40; 0,60] (força e painel) | passa | idem |

**Correção ao enunciado da tarefa.** O r² = 0,9290 **não** é "com as 8 formas vivas". É o r² sobre os pets dos dois
donos que nunca perderam pet (atencioso e permissivo). As 8 categorias presentes nesse subconjunto incluem dois
adolescentes (brigão e guardião) e o titã com um único pet. Nos 640 pets, as 14 categorias são:
- as 8 formas adultas normais;
- 2 sombrias (bastião rachado, predador);
- 3 adolescentes (brigão, colosso, guardião);
- morto.

## 2. O que a V21D muda neste painel, e o que não muda

**Muda.** A V21D entra ligando, na config da run, as quatro chaves da variante validada (`a_c_e2v_v`,
`experiments/configs/v21d/validacao.json`). São campos que já existem, desligados por padrão, em
`ConfigCombateV21D` (`digilab/config.py`):

| chave | valor |
|---|---|
| `preparo_sob_pele_oculto` | true |
| `muralha_lista_espelho` | true |
| `vigia_bate_em_quem_recua` | true |
| `vigia_recua_do_preparo_sob_pele` | true |
| `investida_erra_contra_recuo`, `preparo_prende`, `tita_bate_em_quem_recua` | false |

As chaves valem **só para as partidas do painel B**: o pet e os 32 bots do painel lutam sob a V21D, e a muralha e o
vigia usam as listas variantes (`bots.gambits_adulto`).

**Não muda: a vida.** O sparring da vida (a qualificação para adulto) roda com `campanha.REGRAS_CAMPANHA`, uma
constante V21C (`digilab/educacao.py`, `lutar`). A forma adulta vem do caráter e da linha (`forma_adulta`), não do
combate. Com as mesmas sementes, então, as 640 vidas, as mortes, as qualificações e as formas finais são
**byte a byte as do E1**. Ligar a V21D na vida exigiria mudar a `REGRAS_CAMPANHA`, o que muda a campanha do jogo e a
reprodução da V3 e do E1: fica fora deste plano (seção 11, decisão 4).

**Consequência para o desenho.** O experimento é **pareado**: os mesmos 640 pets, com a mesma forma, no mesmo painel,
com as mesmas sementes de partida, sob as duas regras. O tratamento isola o **último elo do mapa, forma → desempenho**,
com o genótipo → forma fixo. Toda diferença entre as condições vem das regras da luta.

## 3. Hipótese e predição (falsificável)

- **H.** A falta de efeito do dono no painel vem de o canal de forma ser forte demais: a forma final carrega quase toda
  a variância e o dono só aparece através de qual forma o pet virou. Se o canal for comprimido, o que o dono faz
  dentro da forma passa a pesar mais.
- **Predição direcional** (as duas precisam valer no subconjunto primário, seção 4):
  - **P1 (manipulação):** comprimir o canal **reduz** o r² da forma final: Δr²_forma = r²(V21D) − r²(V21C) < 0.
  - **P2 (efeito):** comprimir o canal **aumenta** a fração do dono: Δfrac_D = frac_D(V21D) − frac_D(V21C) > 0.
- **O que falsifica:** o canal comprimido (P1 verificada) e frac_D sem subir (seção 7). Aí o resultado negativo deixa
  de ser sobre calibração dos arquétipos e passa a ser sobre a **arquitetura**: o dono, como está modelado, não tem
  efeito no desempenho que não passe pela forma.
- **Mecanismo esperado, para ler o resultado** (não entra no gate): dentro da forma o dono explicava 22% do resíduo
  (`…/dono_ambiente/resultado.json` → `forma_final.residuo_dentro_da_forma.fracao.D` = 0,219), pelo ε da disciplina.
  Se esse termo ficar estável e a variância entre formas encolher, frac_D sobe.

## 4. Desenho

| item | valor | status / fonte |
|---|---|---|
| rodada | a `especie_fixa` do E1 (brasa) | `experiments/configs/linhagem/natureza_criacao.json` |
| genomas (G = 40) | sementes **81001–81040** | idem e `…/especie_fixa/meta.json` |
| ambientes (R = 4) | sementes **82001–82004** | idem |
| donos (D = 4) | atencioso, aleatório, permissivo, relapso | idem |
| vida | a do E1 (V3 com o genoma injetado), 14 dias, sem mudança | idem |
| painel B | 8 formas × 4 espécies, 50 partidas por bot, condição neutra | idem |
| sementes das partidas | `derivar_semente("linhagem-e1\|B\|<g>:<r>", bot, k)`: **o mesmo rótulo** `linhagem-e1`, para números aleatórios comuns entre as condições | idem |
| condição V21C | **não roda de novo**: `taxa_por_celula` e `pets.json` do E1 | `…/natureza_criacao/especie_fixa/resultado.json`, `pets.json` |
| condição V21D | o painel acima com as quatro chaves da seção 2 | PROPOSTO: este plano |

**Subconjunto primário: atencioso e permissivo** (40 × 2 × 4 = 320 células). É o maior subconjunto cruzado e
balanceado **sem nenhuma morte** (`…/dono_ambiente/resultado.json` → `morte_dado_lesao`: 0 mortos nos dois). A razão
da escolha é a seção 6. Ela foi feita conhecendo o E1, mas antes da run V21D, e pelo mecanismo (quem trata a lesão é
regra do dono sintético), não pelo valor de frac_D.

**Análise completa (secundária):** os 4 donos, 640 células, com morto = 0 como no E1.

## 5. Estimandos e análise

**Resposta.** Y(g, d, r) = a taxa média do pet contra o painel (a do E1).

**Decomposição.** A mesma do E1: `metrics.componentes_cruzados`, ANOVA de 3 fatores cruzados, método dos momentos,
modelo aleatório sem restrição. A `fracao` trunca cada componente em 0 antes de dividir, como no E1; os componentes
sem truncar também são relatados. Com 2 donos, σ²_D mede o contraste atencioso − permissivo.

**r² da forma.** A fração da soma de quadrados da taxa entre categorias de forma final: a mesma conta de
`experiments/analisar_dono_ambiente.py` (`r2_forma`). Pela regra "métricas existem uma vez só", ela passa para
`digilab/metrics.py`. A conferência: o script antigo, importando de lá, tem de reproduzir 0,9585 e 0,9290.

**Estimandos primários** (subconjunto atencioso + permissivo):

| estimando | definição |
|---|---|
| **Δfrac_D** | frac_D(V21D) − frac_D(V21C) |
| **Δr²_forma** | r²_forma(V21D) − r²_forma(V21C), categorias de forma dos pets do subconjunto (sem morto, porque não há) |

**Estimandos secundários** (as duas condições e a diferença, com IC, sem gate):
- frac_G, frac_DR e frac_e; também frac_R, frac_GD, frac_GR e os componentes sem truncar;
- σ²_G sob a V21D, com o critério do E1 (limite inferior do IC95 > 0), só descritivo;
- o contraste atencioso − permissivo;
- a análise completa (4 donos):
  - as mesmas frações e Δ;
  - r²_forma sobre os **600 vivos** (13 categorias);
  - r²_forma sobre os **640 com morto** (14 categorias, a conta do E1);
  - atencioso − aleatório e atencioso − permissivo;
- r²_forma só com os pets nas 8 formas adultas normais;
- a taxa média por forma nas duas condições e a amplitude entre formas;
- as formas da V21D ao lado da força e do painel da validação (`criterios.json`), para ver se a compressão chega aos
  pets reais (com caráter, treino e disciplina).

**Incerteza.**
- **Bootstrap pigeonhole do E1** (`metrics.bootstrap_cruzado`, `reamostrar="GR"`):
  - reamostra genomas e ambientes com reposição, de forma independente; os donos ficam fixos;
  - **10 000 reamostras, semente 20260930**, conferidas no script e nos artefatos, não assumidas:
    `experiments/configs/linhagem/natureza_criacao.json` (`bootstrap`), `…/especie_fixa/meta.json` e
    `run_natureza_criacao.analisar`, que passa `cfg_boot["reamostragens"]` e `cfg_boot["semente"]`;
  - IC95 percentil (`metrics.ic_percentil`).
- **Pareamento.** Cada célula leva o par (Y_V21C, Y_V21D) e a forma do pet. Assim as duas condições usam a **mesma
  reamostra**, e o IC de cada Δ inclui a correlação entre elas. A função não muda; só o valor da célula passa a ser
  uma tupla.
- **Secundário:** reamostrar só os genomas (`reamostrar="G"`), como no E1.

## 6. Tratamento de `morto`

**Decisão:** morto **sai da análise principal**. Nas análises secundárias, entra como **estado absorvente**, relatado à
parte.

**Por quê.** Morto não luta e conta 0. As mortes vêm só da vida, que é idêntica nas duas condições. Comprimir as
formas vivas em direção ao meio aumenta, por construção, a distância entre morto (0) e vivo. Assim a fração do dono
subiria só porque o aleatório (32 mortos) e o relapso (8) perdem pets, por uma regra de dono sintético que nós
escrevemos (`docs/ANALISE_DONO_AMBIENTE_E1.md`). Isso passaria por P2 sem dizer nada sobre a forma. Como categoria de
forma, morto também infla o r² (a 14ª categoria, com taxa 0 e n = 40).

**Como.**
- Na análise principal, o subconjunto sem mortes (seção 4) tira morto sem desbalancear o cruzamento.
- **Falha alto:** se aparecer uma morte no subconjunto, a run para. Não pode aparecer, porque a vida é a do E1.
- Nas análises secundárias, morto entra com Y = 0 nas duas condições, como no E1. Os r² são relatados sem morto
  (600 vivos) e com morto (640).
- As mortes por dono e por ambiente vão numa tabela à parte, iguais nas duas condições. É uma conferência: se
  diferirem, a vida mudou, e a run é inválida.

## 7. Gate e regra de decisão (escritos antes)

Os três passos se aplicam em ordem, no subconjunto primário, com o IC95 pigeonhole pareado. Não existe "quase passou":
um resultado perto da fronteira é relatado como está.

**Passo 1 — a compressão chegou aos pets (P1):**

| resultado | condição | leitura |
|---|---|---|
| **COMPRESSÃO VERIFICADA** | limite superior do IC95 de Δr²_forma < 0 | segue para o passo 2 |
| **COMPRESSÃO NÃO VERIFICADA** | o IC95 inclui 0, ou fica todo > 0 | a V21D não comprimiu o canal nos pets deste painel; **o experimento não testa H**, e nada se conclui sobre o dono. Relatado como tal |

**Passo 2 — o dono ganhou peso (P2).** δ = **0,05** em frac_D (PROPOSTO, sem fonte; é o tamanho da frac_D dos 4 donos
no E1, e o valor fica para o Matheus referendar, seção 11):

| resultado | condição | leitura |
|---|---|---|
| **PREDIÇÃO CONFIRMADA** | limite inferior do IC95 de Δfrac_D > 0 | comprimir o canal de forma dá peso mensurável ao dono: o negativo anterior era, ao menos em parte, de calibração dos arquétipos |
| **PREDIÇÃO REFUTADA (arquitetura)** | limite superior do IC95 de Δfrac_D < δ | com o canal comprimido, o dono segue sem ganhar peso relevante: o negativo passa a ser sobre a arquitetura do dono e da vida, não sobre a calibração |
| **INCONCLUSIVO** | nenhum dos dois | o IC é largo demais para decidir |

**Aviso registrado antes.** Com R = 4 ambientes o IC pigeonhole é largo: no E1, com os 4 donos, o de frac_D foi
[0,0; 0,3236] (`…/especie_fixa/resultado.json`). O pareamento deve estreitar o IC do Δ, mas **INCONCLUSIVO é um
resultado provável**. Não foi feito cálculo de poder. Aumentar R mudaria as sementes do E1, o que este plano proíbe;
fica como decisão (seção 11).

**Depois da run não se mexe em número nenhum por causa do resultado:** chaves, sementes, subconjunto, δ e categorias
ficam como estão. Se o resultado não servir, a decisão do que fazer é do Matheus.

## 8. Desfecho por distribuição de formas (quality diversity)

**Espaço de descritores.** As **8 formas adultas normais** (os nichos). Adolescentes, sombrias e morto ficam fora dos
nichos e são relatados em contagem.

Por dono (160 pets, os 4 donos):

| métrica | definição | muda com a V21D? |
|---|---|---|
| **cobertura** | nichos alcançados por pelo menos um pet do dono ÷ 8 | **não**: as formas são as do E1 |
| **QD-score** | soma, nos nichos alcançados, da taxa média dos pets do dono naquele nicho | **sim**: é a única que mede qualidade × diversidade entre as condições |
| **concordância entre ambientes** | para cada (g, d), a forma final nos 4 ambientes: κ de Fleiss (40 genomas × 4 ambientes; categorias = as 14 da forma final) e a fração de pares de ambientes com a mesma forma | **não** |

- Usamos κ de Fleiss no lugar da ICC proposta, porque a forma é categórica e a ICC pede resposta contínua. A ICC da
  **taxa** entre ambientes, por dono, sai como secundário.
- κ e o QD-score entram no `digilab/metrics.py`.
- ICs pelo mesmo bootstrap pigeonhole, sem gate: é descritivo.

**Consequência do desenho (seção 2):** a cobertura e a concordância são **idênticas nas duas condições por
construção**. Elas descrevem uma vez quanto o dono controla o fenótipo, que é a alternativa "medir o dono pela
distribuição de formas". Se diferirem, é erro e a run para. Só o QD-score responde à V21D. Uma distribuição de formas
que responda às regras exigiria a V21D na vida (seção 11, decisão 4).

## 9. Implementação e conferências (antes da run)

**Mudanças de código** (nenhuma no `digilab/engine.py`; nenhum default do `config.py` muda):
1. `experiments/run_poder.regras_de`: monta `ConfigCombateV21D` quando a config traz uma chave da V21D; sem nenhuma,
   devolve a `ConfigCombateV21C` de hoje, igual.
2. `experiments/run_educacao.lutador_painel`: o pet adulto pega a lista em `bots.gambits_adulto(forma, cfg_v21)` no
   lugar de `ADULTOS[forma]`. Com as chaves desligadas é a mesma lista. Com elas ligadas, o **pet** muralha ou vigia
   usa a lista variante, como os bots do painel e como na validação. Sem essa mudança, só os bots mudariam.
3. `experiments/configs/linhagem/natureza_criacao_v21d.json`:
   - é a config do E1 com as quatro chaves em `combate.regras_v21`;
   - o rótulo de partidas continua `linhagem-e1`;
   - só a rodada `especie_fixa` roda.
4. As métricas novas no `digilab/metrics.py`: `r2_forma` (movida), κ de Fleiss e QD-score.
5. `experiments/analisar_v21d.py`: lê as duas condições e aplica este plano.

**Conferências** (qualquer falha para tudo; não é desvio a contornar):
- **Testes.** Com as chaves desligadas:
  - `lutador_painel` dá as listas de `ADULTOS` nas 8 formas;
  - `regras_de` na config do E1 dá a mesma config de antes.
- **Piloto.** O painel V21C do piloto, refeito com o código novo, reproduz `…/natureza_criacao/piloto/resultado.json`
  (`taxa_por_celula`).
- **Vidas.** Na run:
  - as 640 vidas saem byte a byte iguais às do E1, arquivadas em
    `D:\Trab\digilab\arquivo\artifacts_linhagem_E1_vidas\natureza_criacao\especie_fixa\vidas` (640 arquivos, fora do
    repo);
  - o `pets.json` sai igual ao do E1;
  - o `hash_parametros_educacao` sai igual ao do `…/especie_fixa/meta.json` (`6a9037ad…`).
- **r² de referência.** `r2_forma`, no `metrics.py`, reproduz 0,9585 e 0,9290 a partir do E1.

**Custo esperado** (tempos do E1, `…/especie_fixa/meta.json`): vidas 888 s, painel 77 s, análise 6 s.

## 10. Saída

- **Onde:** `artifacts_linhagem/natureza_criacao_v21d/especie_fixa/`:
  - `analise_plano.json`: este plano (gate, estimandos, ICs, QD e conferências), de `experiments/analisar_v21d.py`;
  - `resultado.json`, `pets.json` e `meta.json` do `run_natureza_criacao.py`, como no E1. O `resultado.json` traz a
    análise do E1 refeita sob a V21D, incluindo o "gate" de σ²_G do E1, que aqui é só descritivo;
  - as partidas e as vidas ficam fora do git, como no E1.
- **Relatório:** `docs/RESULTADO_V21D_PAINEL.md`, depois da run e num commit separado.

## 11. O que conta como desvio (para `docs/REGISTRO_DESVIOS.md`)

Qualquer um destes, depois do commit deste plano, é desvio e vai para o registro com o motivo, **antes** de a run
seguinte usá-lo:
- sementes de genoma, ambiente ou partida, rótulo das partidas, número de partidas por bot, condição do painel;
- chaves da V21D diferentes das quatro da seção 2, ou V21D fora do painel (na vida);
- reamostras, semente do bootstrap, tipo de bootstrap ou nível do IC;
- subconjunto primário, tratamento de morto, conjunto de categorias do r² ou espaço de nichos do QD;
- δ, a ordem dos passos do gate ou qualquer critério da seção 7;
- mudança de código além das cinco da seção 9;
- rodar de novo depois de ver um resultado, ou trocar a análise por uma que "funcione";
- conferência da seção 9 que falhou e foi corrigida (o que falhou, a correção e por que a run ainda vale).

Não é desvio: mudança de texto sem efeito em número. Não precisa de registro.

## 12. Decisões do Matheus (antes de rodar)

**Decididas em 2026-09-30:** o Matheus aceitou as cinco recomendações abaixo. O plano vale como está escrito.

1. **Métrica de QD:** cobertura + QD-score + κ de Fleiss sobre as 8 formas adultas (recomendação), ou a proposta
   original (cobertura + ICC).
2. **8 ou 14 formas no r² principal:** as categorias presentes no subconjunto sem mortes (recomendação), ou as 14 com
   morto.
3. **δ do gate:** 0,05 (recomendação), ou outro valor.
4. **V21D só no painel** (recomendação), ou também na vida (exige mudar a `REGRAS_CAMPANHA`: fora das restrições
   desta tarefa).
5. **R = 4 ambientes** (recomendação, pela restrição das mesmas sementes), aceitando INCONCLUSIVO como resultado
   provável.
