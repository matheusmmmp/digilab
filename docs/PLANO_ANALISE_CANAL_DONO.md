# Plano de análise — o canal do dono que não passa pela forma

Status: **registrado antes de qualquer run** (2026-09-30). Nada foi rodado para escrever este plano. Os números
citados vêm de artefatos em disco, e cada um aponta o arquivo; valores sem fonte estão marcados PROPOSTO.

**Natureza.** Vem depois do painel V21D (`docs/RESULTADO_V21D_PAINEL.md`): comprimir as formas pelo reequilíbrio das
listas não comprimiu o canal nos pets. O Matheus escolheu o caminho da **arquitetura** (2026-09-30): testar se o dono
pode ter efeito mensurável por um caminho que **não passe pela forma final**. A pergunta segue a adotada: que
propriedade do mapa até o desempenho dá efeito ao dono.

## 1. Ponto de partida (conferido nos artefatos)

| achado | número | artefato |
|---|---|---|
| a forma final explica a taxa no painel | r² 0,9585 (640 pets, 14 categorias) | `artifacts_linhagem/dono_ambiente/resultado.json` → `rodadas.especie_fixa.forma_final.todos` |
| dentro da forma sobra pouco, e o dono explica parte desse resto | fração D do resíduo dentro da forma 0,219 | idem → `forma_final.residuo_dentro_da_forma.fracao.D` |
| o mesmo genoma, com o mesmo dono, chega a formas diferentes em cada ambiente | κ de Fleiss: aleatório −0,028, atencioso −0,058, relapso −0,017, permissivo 0,269 | `artifacts_linhagem/natureza_criacao_v21d/especie_fixa/analise_plano.json` → `qd` |
| reequilibrar as listas não comprime o canal de forma nos pets | Δr²_forma +0,0098 [−0,0417; +0,0395] | idem → `gate` |
| frac_D da taxa, 4 donos (E1, V21C) | 0,0504, IC95 [0,0; 0,3236] | `artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json` |

## 2. A arquitetura de hoje: por onde o dono chega à luta

No pet de pesquisa (a vida do E1, `run_natureza_criacao.py` e `run_educacao.py`), o dono chega à taxa no painel por
três vias:

| via | caminho | o que a leva hoje |
|---|---|---|
| **ensino** (o que o pet aprende) | feedback → política (bandit) → **caráter** medido em `T_ADOL` → **linha** → caráter em `T_ADUL` → **forma adulta** → lista canônica | categórica: a forma. O caráter também soma nos stats dentro da forma (`catalogo.stats`), com peso fixo |
| **cuidado e educação** (regras do dono sintético) | saúde (neutralizada no painel B), disciplina → ε, lesão sem tratar → morte | o ε da disciplina e as mortes |
| **treino** | pontos treinados → perfil de stats (normalizado no painel) | contínua, pequena |

Os números da seção 1 dizem que o gargalo categórico (a forma) decide quase tudo, e que é o **ambiente** que decide a
forma. Antes de construir um canal contínuo do dono até a luta, falta saber uma coisa: **o sinal do dono chega ao que
o pet aprendeu?** Se não chega, nenhum mapa depois dele cria o efeito, e o gargalo está no aprendiz, não no combate.

Daí as duas etapas, em ordem:
- **Etapa A.** Só análise: vidas já gravadas, nenhuma mecânica nova.
- **Etapa B.** Só roda se a A passar: um canal contínuo, só no painel, com as vidas fixas.

## 3. Etapa A — onde está o sinal do dono

**Dados.**
- As 640 vidas da rodada `especie_fixa` do E1, arquivadas em
  `D:\Trab\digilab\arquivo\artifacts_linhagem_E1_vidas\natureza_criacao\especie_fixa\vidas`: genomas 81001–81040,
  ambientes 82001–82004, 4 donos.
- **Nenhuma vida nova.** Cada log é reproduzido com `reproduzir_educacao` e as fábricas do genoma (`_fabricas`, como
  no `vida_com_genoma`).

**Portadores do sinal**, medidos no replay:

| grupo | portador | momento | pets |
|---|---|---|---|
| **aprendido** (primário) | caráter nos 4 eixos (`evolucao.carater`, as mesmas sondas `SONDAS`) | `T_ADOL`, o fim da criança: decide a linha | **640** (ninguém morreu ainda) |
| aprendido | caráter nos 4 eixos | `T_ADUL`: decide a forma adulta e entra nos stats | os vivos em `T_ADUL` |
| aprendido | desvio bruto por eixo (antes do corte em [−1, 1]) | `T_ADOL` | 640 |
| imposto pelas regras do dono | disciplina, saúde e vínculo finais; fração do treino em cada stat | fim da vida (ou morte) | 640 |

- **Todos os 640 pets estão vivos em `T_ADOL`.** As mortes vêm só de lesão sem tratar (`…/dono_ambiente/resultado.json`
  → `causas_de_morte`), e a lesão só nasce no sparring, que começa depois de `T_ADOL` (`run_educacao.ticks_sparring`).
  O script confere; morte antes de `T_ADOL` falha alto.
- **Conferência do replay.** O estado final, o resumo da educação e a forma de cada pet saem iguais ao
  `…/natureza_criacao/especie_fixa/pets.json`. Qualquer diferença para tudo.

**Análise.** Para cada portador:
- `metrics.componentes_cruzados` (G, D, R, GD, GR, DR, e), a mesma ANOVA do E1;
- bootstrap pigeonhole (`metrics.bootstrap_cruzado`, `reamostrar="GR"`), 10 000 reamostras, semente 20260930 (as do
  E1: `experiments/configs/linhagem/natureza_criacao.json`);
- as médias por dono e o contraste atencioso − aleatório.

**Gate A** (primário: os 4 eixos do caráter em `T_ADOL`, os 4 donos):

| resultado | condição |
|---|---|
| **SINAL PRESENTE** | em pelo menos um eixo, o limite inferior do IC de σ²_D é > 0. O IC é percentil de nível 1 − 0,05/4 = **98,75%** (Bonferroni pelos 4 eixos) |
| **SINAL AUSENTE** | em nenhum eixo |

**Leitura:**
- **SINAL AUSENTE:** o feedback do dono não deixa marca mensurável no que o pet aprende, separada do genoma e do
  ambiente. O negativo é sobre o **aprendiz** (a política e o caráter), antes de qualquer mapa até a luta. A Etapa B
  não roda, porque um canal contínuo levaria só ruído. É o resultado "arquitetura" no sentido forte.
- **SINAL PRESENTE:** existe o que levar à luta, e a Etapa B testa se um canal contínuo o leva.
- **Os portadores impostos** (disciplina, saúde, vínculo, treino) são relatados, mas **não entram no gate nem na
  Etapa B**. O sinal deles vem das regras que escrevemos para os donos sintéticos, e um canal por eles teria o
  resultado decidido antes da run (a mesma razão da V4 em `docs/ANALISE_DONO_AMBIENTE_E1.md`).

**Descritivo, sem gate:**
- σ²_DR e σ²_R de cada eixo: quanto o ambiente move o caráter;
- a relação entre o caráter em `T_ADOL` e a linha (a fração de pets cuja linha segue o eixo dominante);
- o caráter em `T_ADUL`, só nos vivos.

## 4. Etapa B — o canal contínuo (só se a Etapa A der SINAL PRESENTE)

**O canal.** O caráter já entra nos stats dentro da forma, com peso 1: `catalogo.stats` soma
`cat.carater[eixo] × valor` e renormaliza. A Etapa B dá a esse termo um multiplicador **k**:
- é um campo novo `peso_carater_stats` na `ConfigCatalogo`, com padrão **1,0** (o de hoje; ×1,0 é exato em ponto
  flutuante, então nada muda com o padrão);
- vale **só no painel B**: o `lutador_painel` recebe um catálogo com k, e a vida continua com o catálogo padrão. As
  vidas, as formas e as mortes ficam as do E1 byte a byte, e o desenho é pareado, como no V21D;
- nenhuma mudança no `engine.py`, na vida, nos donos, nas listas de gambits ou no jogo web.

É um canal que não passa pela forma: o mesmo pet, na mesma forma, luta diferente conforme o caráter aprendido.

**Níveis.**
- k ∈ {**1** (o E1: não roda de novo), **3**, **9**} (PROPOSTO, sem fonte).
- Os níveis são fixos, e não calibrados pelo resultado.
- O corte dos stats em `stat_min`/`stat_max` pode saturar com k alto. A fração de stats cortados por nível é relatada.

**Painel.** O do E1: V21C, condição neutra, 50 partidas por bot, o rótulo `linhagem-e1` (números aleatórios comuns
entre os níveis).

**Estimandos** (primário: os 4 donos, 640 células, morto = 0, como no E1; os pares são contra k = 1):

| estimando | definição |
|---|---|
| **manipulação** | fração da variância da taxa **dentro da forma**, 1 − r²_forma (13 categorias vivas): Δ(k = 9 − k = 1) |
| **Δfrac_D** | frac_D(k = 9) − frac_D(k = 1) |
| dose-resposta | as mesmas contas em k = 3 |
| transmissão (descritivo) | frac_D da taxa ÷ frac_D do eixo do caráter que passou no gate A |

**Por que os 4 donos, com morto = 0, no primário:**
- o contraste que interessa (coerente × aleatório) precisa do aleatório;
- as mortes são idênticas entre os níveis, e o viés delas vai **contra** a predição. O canal só acrescenta variância
  aos vivos; se ela não estiver carregada de dono, dilui a parte da frac_D que vem das mortes. Um Δfrac_D > 0 exige
  que a variância nova tenha mais dono que a mistura de hoje.
- **Secundário:** o subconjunto atencioso + permissivo, sem mortes, como no V21D.

**Gate B** (com o IC95 pigeonhole pareado):

| passo | resultado | condição |
|---|---|---|
| 1 | **CANAL ABERTO** | limite inferior do IC95 de Δ(1 − r²_forma) > 0 em k = 9. Senão, **CANAL NÃO ABERTO**: o experimento não testa o canal |
| 2 | **O DONO PASSA PELO CANAL** | limite inferior do IC95 de Δfrac_D > 0 em k = 9 |
| 2 | **O DONO NÃO PASSA** | limite superior do IC95 de Δfrac_D < δ = **0,05** (PROPOSTO, o mesmo do V21D) |
| 2 | **INCONCLUSIVO** | nenhum dos dois |

O passo 2 só se lê depois de CANAL ABERTO. Não existe "quase passou".

**Aviso registrado antes.** Com R = 4 ambientes os ICs são largos (frac_D da taxa no E1: [0,0; 0,3236]), e
INCONCLUSIVO é um resultado provável. O "melhor" não é definido: o canal move os stats na direção do caráter, que pode
ajudar ou atrapalhar. Por isso o estimando é a variância atribuída ao dono, não uma vitória.

## 5. Tratamento de `morto`

- **Etapa A:** não há mortos em `T_ADOL` (conferido na run). Nos portadores do fim da vida, o valor do morto é o do
  momento da morte, relatado como descritivo.
- **Etapa B:** morto = 0 em todos os níveis (é idêntico entre eles, porque a vida não muda). O primário usa os 4 donos
  pela razão da seção 4; o subconjunto sem mortes é secundário. O r² da manipulação exclui morto (13 categorias vivas).

## 6. Implementação (antes de cada run)

**Etapa A:**
- **Script.** `experiments/sinal_dono.py`:
  - reproduz os 640 logs arquivados;
  - mede os portadores e confere contra o `pets.json`;
  - aplica a seção 3;
  - usa só funções do `metrics.py`, sem métrica nova.
- **Teste.** Numa vida, o caráter em `T_ADOL` pelo replay é igual ao do `pet._adolescente` da simulação (o mesmo
  caminho do E1).

**Etapa B** (só depois do gate A e de um adendo curto a este plano, registrado antes da run, que diga qual eixo passou
e confirme k):
- **Código.**
  - `ConfigCatalogo.peso_carater_stats` (padrão 1,0) e o uso em `catalogo.stats`;
  - a web não usa o campo; se o teste de constantes (`web/app/test/constantes.test.mjs`) exigir o mapeamento de todo
    campo do Python, ele é registrado como só do Python, com nota;
  - `lutador_painel` com um catálogo opcional.
- **Config.** `experiments/configs/linhagem/natureza_criacao_canal.json`: o E1 com `peso_carater_stats` por nível, só
  no painel.
- **Conferências** (qualquer falha para tudo):
  - com k = 1, o painel do piloto reproduz `…/natureza_criacao/piloto/resultado.json`;
  - as 640 vidas saem byte a byte iguais às do E1;
  - o `pets.json` e o `hash_parametros_educacao` saem iguais;
  - a suíte `pytest` inteira passa com o padrão 1,0.

## 7. Saída

- **Etapa A:** `artifacts_linhagem/sinal_dono/resultado.json` (portadores, componentes, ICs, gate, conferências) e
  `docs/RESULTADO_SINAL_DONO.md`.
- **Etapa B:** `artifacts_linhagem/natureza_criacao_canal/k<k>/`:
  - `pets.json`, `meta.json`, `resultado.json` e `analise_plano.json`;
  - as partidas e as vidas ficam fora do git;
  - o relatório em `docs/RESULTADO_CANAL_DONO.md`.

## 8. O que conta como desvio (para `docs/REGISTRO_DESVIOS.md`)

Qualquer um destes, depois do commit deste plano (ou do adendo da Etapa B), vai para o registro com o motivo,
**antes** de a run seguinte usá-lo:
- as sementes, as vidas usadas, os momentos (`T_ADOL`, `T_ADUL`) ou as sondas do caráter;
- a lista de portadores, a separação aprendido × imposto, ou usar um portador imposto no gate ou na Etapa B;
- as reamostras, a semente, o tipo de bootstrap, o nível do IC ou a correção de Bonferroni;
- os níveis de k, onde o canal atua (fora do painel), o painel, o rótulo das partidas;
- o tratamento de morto, o conjunto primário, as categorias do r², δ ou a ordem dos passos do gate;
- rodar a Etapa B sem SINAL PRESENTE, ou antes do adendo;
- rodar de novo depois de ver um resultado;
- uma conferência que falhou e foi corrigida.

## 9. Decisões do Matheus (antes de rodar)

**Decididas em 2026-09-30:** o Matheus aceitou as cinco recomendações abaixo, inclusive a exceção de escopo da Etapa B
(condicionada ao gate A). O plano vale como está escrito.

1. **Escopo da Etapa B.** O `peso_carater_stats` é um parâmetro novo de mecânica, só no Python e só no painel de
   pesquisa: pede exceção de escopo. **Recomendação:** autorizar agora, condicionado ao gate A. Custo de errar: sem a
   exceção, um SINAL PRESENTE fica sem teste; com ela sem o gate, rodaria um canal sem sinal.
2. **Doses k = 3 e 9.** **Recomendação:** manter. Custo de errar: k baixo demais não abre o canal (passo 1 falha);
   alto demais satura no corte dos stats e o canal vira ruído.
3. **Bonferroni (98,75%) no gate A.** **Recomendação:** manter. Custo de errar: sem correção, 4 eixos dão mais chance
   de um falso SINAL PRESENTE; com uma correção mais dura, um sinal fraco passa como ausente.
4. **Portadores impostos fora do gate e da Etapa B.** **Recomendação:** manter. Custo de errar: incluí-los testaria
   regras que escrevemos, e o resultado estaria decidido antes.
5. **δ = 0,05 na Etapa B.** **Recomendação:** manter, igual ao V21D. Custo de errar: o mesmo do V21D.

## Adendo B (2026-09-30, registrado antes da run da Etapa B)

**Gate A:** SINAL PRESENTE, só pelo eixo **resistente** (σ²_D +0,0034, IC 98,75% [+0,0009; +0,0121]; frac D 0,208),
de `artifacts_linhagem/sinal_dono/resultado.json`. O relatório é o `docs/RESULTADO_SINAL_DONO.md`. O sinal que passou
separa o permissivo do relapso, não o atencioso do aleatório.

**Decisão do Matheus** (aceitou a recomendação):
- O canal fica como a seção 4 escreve: **k multiplica o termo do caráter inteiro** em `catalogo.stats`, nos 4 eixos.
  Não age só no resistente, para o eixo não ser escolhido pelo resultado.
- **k = 3 e k = 9**, como estava. k = 1 é o E1 e não roda de novo.
- O resistente entra só na medida de transmissão: frac_D da taxa ÷ 0,208.
- Nada mais muda:
  - painel V21C, condição neutra, rótulo `linhagem-e1`;
  - morto = 0 no primário (4 donos), e o subconjunto atencioso + permissivo como secundário;
  - o gate B em dois passos;
  - δ = 0,05;
  - bootstrap pigeonhole com 10 000 reamostras e semente 20260930.

**A manipulação, escrita sem ambiguidade:** 1 − r²_forma sobre os pets vivos, com as 13 categorias de forma, nos 4
donos. CANAL ABERTO quando o IC95 de Δr²_vivos (k = 9 − k = 1) fica todo abaixo de 0, que é o mesmo que o IC95 de
Δ(1 − r²) ficar todo acima de 0.

**Implementação:**
- `ConfigCatalogo.peso_carater_stats` (padrão 1,0);
- `catalogo.stats` soma o termo do caráter com peso v × k;
- `lutador_painel(..., cat)`: só o pet usa o catálogo com k; os bots do painel e a vida usam o padrão;
- configs `experiments/configs/linhagem/natureza_criacao_canal_k3.json` e `_k9.json`, com o campo
  `catalogo_painel.peso_carater_stats`;
- a análise em `experiments/analisar_canal.py`, com as mesmas conferências do V21D: vidas iguais às do E1 byte a byte,
  `pets.json` e hash iguais.

### Desvio do adendo B (2026-09-30, antes da run de k alto): k = 9 → k = 8

- **Problema:** com k = 9, a renormalização dos stats (`catalogo.renormalizar`) fica sem stats livres em **3 dos 600
  pets vivos** e levanta `CatalogoInvalido`. A run de k = 9 falharia no painel, e foi parada antes de chegar lá.
  Com k = 7 ou 8 nenhum pet quebra (os de k = 1 a 6 também foram conferidos).
- **Regra da troca, que não olha a taxa nem os donos:** a dose alta passa a ser o **maior k inteiro ≤ 9 em que todos
  os 600 pets vivos têm stats válidos**, que é **k = 8**.
- O resto não muda:
  - o gate passa a usar Δ(k = 8 − k = 1) onde dizia k = 9;
  - k = 3 segue igual;
  - a config passa a ser `natureza_criacao_canal_k8.json`.
- Registrado também em `docs/REGISTRO_DESVIOS.md`.
