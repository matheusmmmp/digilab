# Plano de análise V3: a regularidade do longe separada da geometria (LG)

**Status: PROPOSTO** (2026-11-13, Claude Code, Opus 5.5, na sessão com o Matheus). Nenhuma vida roda antes de quatro coisas:
1. este plano commitado na `main`, com a marca de aprovação do Matheus no cabeçalho;
2. as decisões LG-1 a LG-8 (seção 9) DECIDIDAS;
3. a faixa na `FAIXAS_RESERVADAS` (`experiments/bancada/faixas.py`), num commit próprio;
4. o código da seção 4 na `main`: os dois estilos novos, o gabarito dos estilos byte a byte, o orquestrador e o script de poder da seção 6.

Todo número novo aqui é **PROPOSTO e SEM FONTE**, salvo onde dito.

**De onde vem:**
- a ressalva da geometria do adendo 6 da C1 (`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, A6.2): "o contraste `longe_fixo` × `longe` mistura a regularidade com o lado do mapa e com a âncora";
- os resultados da C1 e da C4 (`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, seções 13 e 16): a memória ganha no `longe_fixo` (M3\* − M2 +0,0489; REL − SEM +0,0646) e não ganha no longe sorteado (M3\* − M2 −0,0106, indeterminado; REL − SEM −0,0223, `< 0`);
- a decomposição D-C1-3 (seções 13.6 e 13.7), que achou o caminho do ganho (as idas e a queda das perdas para o sono), mas não tocou na geometria;
- as auditorias externas de 2026-11-13, no vault: a leitura "a memória paga com mundo regular e falha com mundo aleatório" foi tirada do contraste que a A6.2 já dizia estar misturado.

**O que este plano não afirma:**
- que o longe fica consertado;
- que o modular supera o A;
- que algum cérebro está pronto.

Os contrastes são entre braços do próprio modular e medem um módulo, a memória, em cenários desenhados. **Nenhuma alegação de novidade.**

## 1. A pergunta e as previsões, escritas antes

**A pergunta:** o ganho da memória no `longe_fixo` vem de a ração voltar aos mesmos lugares (a regularidade)? Ou vem de onde e a partir de onde a ração é posta? Hoje o `longe_fixo` põe a ração:
- sempre a leste do comedouro, porque a 20 células dele só cabem 5 das 16 direções no mapa de 64 × 30 (o lado);
- medida a partir do comedouro (a âncora).

Já o longe sorteado usa as 16 direções a partir do pet.

**O que muda neste plano:** um estilo novo, o `longe_ancora`, que põe cada ração num ponto **novo**, sorteado do mesmo jeito que os pontos do `longe_fixo`:
- as mesmas direções viáveis;
- a mesma faixa de 20 a 30 células;
- a mesma âncora, o comedouro.

A distribuição de cada ração é a mesma nos dois estilos (seção 3.2). **A única diferença é se os lugares se repetem.** Então `longe_fixo` × `longe_ancora` mede a regularidade com o lado e a âncora iguais, e `longe_ancora` × `longe` mede a geometria (lado e âncora juntos) sem a regularidade.

**As previsões do sinal** (por episódio de fome, a medida da C1; a direção vem da literatura já usada na A6.1, Giannakakis et al. 2023 e Khan e Cañamero 2018, não o tamanho):

| contraste | a previsão | o papel |
|---|---|---|
| **I-M3:** (M3\* − M2) no `longe_fixo` − (M3\* − M2) no `longe_ancora` | **> 0** | primário, Holm |
| **I-PAD:** (PAD − M2) no `longe_fixo` − (PAD − M2) no `longe_ancora` | **> 0** | primário, Holm |
| **R-UM:** (M3\* − M2) no `longe_um` − (M3\* − M2) no `longe_fixo` | **> 0** (mais regular, mais ganho) | secundária, sem gate |
| **GEO-M0:** a taxa por episódio do M0 no `longe_ancora` − no `longe` | **sem previsão de sinal** | descritivo: a geometria sem aprendizado |
| **M-ANCORA:** (M3\* − M2) no `longe_ancora` | **sem previsão de sinal** | descritivo |

**A previsão não se afrouxa até passar.** Se o I sair `≈ 0`, isso é registrado como `≈ 0` (seção 7).

## 2. O que não muda

- **O motor, o corpo, o mundo, o cheiro, o `engine.py`, o A e o cérebro modular.** A `intencao_suspensa` fica desligada em todos os braços, como na C1 e na C4.
- **O cenário da C1** (A6.2), sem mudança:
  - o `CONFIG_MUNDO_MVP` e o corpo do v11;
  - o pet sozinho e os quatro donos sem ensino;
  - **14 dias, orçamento de 16 por dia,** morte desligada.
- **Os valores:** os inatos do #428 e os da C4 para o REL, que seguem PROPOSTOS. **Nenhuma calibração e nenhum piloto:** a variância vem das vidas da C1 e da C4 que já estão no git (seção 6).
- **Os estilos que existem** (`comedouro`, `perto`, `longe`, `longe_fixo`) não mudam, byte a byte. O gabarito dos estilos confere isso.
- **As faixas já reservadas ou gastas** (as de `FAIXAS_RESERVADAS` e `FAIXAS_QUEIMADAS`; entre elas a 71xxx da C1 e a 77xxx da C4) não entram em nada, salvo a leitura dos artefatos que já estão no git.
- **É pesquisa, só no Python:** nada vai ao jogo e nada se porta para a web.

## 3. O desenho

### 3.1 Os lugares (4 estilos)

| estilo | o lugar de cada ração | âncora | lado | regularidade |
|---|---|---|---|---|
| `longe_um` (novo nível; o `longe_fixo` com `n_pontos` = 1) | sempre o mesmo ponto, sorteado uma vez | o comedouro | leste | total |
| `longe_fixo` (a C1, como está) | um de 3 pontos fixos, por sorteio uniforme | o comedouro | leste | 3 lugares |
| **`longe_ancora`** (novo) | um ponto novo a cada ração, sorteado como os pontos do `longe_fixo` | o comedouro | leste | nenhuma |
| `longe` (como está) | direção (16) e distância novas a cada ração | o pet | qualquer | nenhuma |

- **Por que o `longe_um` entra:** ele completa a escada da regularidade (um, três, nenhum) com o lado e a âncora fixos. A C1-E1 tinha a escada, mas o nível "um" era o comedouro, que fica perto, e não longe.
- **O que fica sem separar:** o lado e a âncora entre si. Um estilo ancorado no comedouro com as 16 direções não cabe no mapa de 64 × 30 com o comedouro em (10, 15). Separar os dois pede outro mapa (por exemplo o da ilha grande, 128 × 60) e fica fora deste plano (seção 10).

### 3.2 O estilo `longe_ancora` (o código novo)

- **No `DonoComLugar`** (`digilab/mundo.py`), um estilo novo em `ESTILOS_LUGAR`. A cada `alimentar`, ele sorteia:
  - uma direção, uniforme entre as **mesmas direções viáveis** de `_sortear_pontos_fixos`;
  - uma distância, uniforme em `longe_min_celulas`…`longe_max_celulas`, **com o mesmo teste de que o ponto cabe sem corte** e as mesmas 1 000 tentativas.
- **A rng é própria,** `derivar_semente("dono-lugar-ancora", semente, rotulo_dono)`. Os outros estilos não consomem sorteio novo.
- **A conferência da construção** (teste, antes da run): a distribuição de um ponto do `longe_ancora` é a de um ponto do `longe_fixo`. O primeiro ponto de um sorteio sem reposição é uniforme entre as viáveis, e a distância sai do mesmo jeito. O teste compara as frequências por direção e os quantis da distância em 20 000 sorteios, com sementes de teste, e o descritivo da seção 8 repete a conferência nas vidas.
- **O `longe_um`** é o `longe_fixo` com `n_pontos` = 1 (o parâmetro já existe e aceita 1). Só o rótulo do estilo e a constante entram, com o status PROPOSTO em `config.py`.

### 3.3 Os braços

| braço | o que é | o papel |
|---|---|---|
| **PAD** | o braço REL da C4: o `CONFIG_DIGIBRAIN_LAB` (o M3\* com a `memoria_autobio`, `controle_mem` = "rel", sem facetas), a base do cérebro do jogo | o braço do produto |
| **M3\*** | completo, com as duas subchaves do cheiro, sem a autobiográfica | o braço da C1 (a réplica) |
| **M2** | sem M-MEM, com as duas subchaves do cheiro | o controle dos primários |
| **M0** | sem P1, sem P2 e sem M-MEM, com o cheiro | o inato: a geometria sem aprendizado |

- O PAD é configurado pela mesma função que montou o REL na C4, conferida contra o `meta.json` da C4 antes da run.
- **O sono que segura** (`ConfigSonoSegura`, que o jogo liga da v27 em diante) **fica desligado em todos os braços,** como na C1 e na C4. Ligá-lo mudaria o cenário e quebraria a comparação com as duas runs (LG-2).

- **As células:** os 4 donos × 4 estilos = 16 células. Com 4 braços, são **64 vidas por unidade.**
- **O pareamento:** por unidade e célula. Os braços vivem a mesma semente, o mesmo genoma, o mesmo dono e os mesmos lugares; só o cérebro muda. As rngs do dono e dos lugares não dependem do braço.

### 3.4 As sementes e a faixa

- **A faixa proposta: 93101…93505.** Conferida em 2026-11-13: não aparece em `faixas.py` nem em `docs/` em nenhum branch remoto. **A confirmar com o coordenador** antes de entrar na tabela.
- **As bases:** 93101, 93202, 93303, 93404 e 93505.
- **O K proposto: 30 por base, 150 unidades,** o da C1 (seção 6). São **9 600 vidas.**
- **A derivação:** a da C1 (A6.3), `bancada_v2.unidades_derivadas(bases, 30, prefixo="digibrain_prototipo")`.
- **A run roda uma vez,** com todas as bases. As sementes 101…505 servem só à fumaça do orquestrador.

## 4. O código, antes da run

1. **O estilo `longe_ancora` e o rótulo `longe_um`** em `digilab/mundo.py` e `digilab/config.py`, com teste:
   - a conferência da construção (3.2);
   - os estilos que existem iguais byte a byte (o gabarito dos estilos ganha os dois novos).
2. **O orquestrador** `experiments/run_v3_longe_geometria.py`, reusando o da C1 e o da C4:
   - os 4 braços nos 4 estilos;
   - o G1 (toda vida rejogada do disco bit a bit);
   - o `meta.json` com o commit, a árvore limpa e os sha256;
   - no máximo 4 processos.
3. **O script de poder** `experiments/poder_longe_geometria.py` (seção 6). Ele só lê o `medidas.json` da C1 e o da C4, sem vida nova, e grava o `artifacts_v3_longe_geometria/poder.json`.
4. **As medidas** são as da C1, em `digilab/metrics.py`, sem medida nova. A taxa por episódio é a do G-MVP-EP (A3.3, com a W(d₀)).

## 5. Os contrastes primários

- **A medida:** a taxa de fechamento por episódio de fome, como na C1 (A6.4).
- **A unidade:** a (base, semente). Em cada unidade e estilo, a diferença entre braços célula a célula (no mesmo dono), com a média das 4 células.
- **O I-M3:** a diferença de M3\* − M2 do `longe_fixo` menos a do `longe_ancora`. Cada unidade dá um valor.
- **O I-PAD:** o mesmo, com o PAD no lugar do M3\*.
- **O teste:** o IC95 pelo t sobre as 150 unidades (`metrics.ic_t`). **O Holm na família dos dois** (α = 0,025 unilateral, como na C4). **Passa** com o limite inferior acima de 0 e o p ajustado dentro do Holm.
- **As premissas** (A6.4, por estilo, no M3\* e no PAD):
  - **G-PESA da memória:** a fração das decisões com `memoria_decidiu`, com o limite inferior do IC95 acima de 0,01, no `longe_fixo` e no `longe_ancora`;
  - **G-ELEGIVEL-EP:** ao menos 80 % das vidas com 3 episódios ou mais, nos mesmos dois estilos.

  Se uma premissa falha, o primário daquele braço é **inconclusivo por premissa.**
- **A ressalva do g1** (A4.4.6), como está.

## 6. A margem e o K, pelo poder

**A conta de bolso** (a refazer no script, que é o que vale):
- o primário da C1 tem IC95 [+0,0355; +0,0624] com 150 unidades, então o dp das diferenças por unidade é cerca de **0,083**;
- o I é a diferença de duas diferenças, em células diferentes da mesma unidade. Sem correlação, o dp fica perto de 0,083 × √2 ≈ **0,12**; com correlação positiva, fica menor;
- com o poder de 0,8 e α = 0,025 unilateral, a margem δ(K) ≈ 2,8 × σ / √K:

| K (unidades) | por base | vidas | δ(K) com σ = 0,12 |
|---|---|---|---|
| 100 | 20 | 6 400 | 0,034 |
| **150** | **30** | **9 600** | **0,027** |
| 200 | 40 | 12 800 | 0,024 |
| 300 | 60 | 19 200 | 0,019 |

- **A escala do que se procura:** se o `longe_ancora` se comportar como o longe sorteado da C1, o I fica perto de +0,049 − (−0,011) ≈ **+0,06**, mais de duas vezes a margem com K = 150. Se a geometria explicar tudo, o I fica perto de 0. Uma margem perto de 0,027 separa os dois.
- **O script** faz a conta como a A6.5: a dispersão das diferenças por unidade na C1 e na C4, o σ de planejamento com a folga de 20 %, a aproximação normal do t não central e a conferência por simulação (2 000 réplicas, semente 4242). O K e a δ ficam DECIDIDOS pelo Matheus depois do script, antes da run (LG-5).

## 7. A classificação e a regra de leitura

**O "≈ 0" e as classes:** a regra da A6.6, com a δ da seção 6:
- **≈ 0:** o IC95 inteiro dentro de (−δ, +δ);
- **> 0:** o limite inferior acima de 0 e o IC fora de (−δ, +δ);
- **< 0:** o limite superior abaixo de 0 e o IC fora de (−δ, +δ);
- **indeterminado:** qualquer outro caso.

**A regra de leitura, escrita antes** (I-M3 e I-PAD lidos cada um; a M-ANCORA ao lado):

| o I | a M-ANCORA (M3\* − M2 no `longe_ancora`) | a leitura |
|---|---|---|
| **> 0** | ≈ 0 ou < 0 | **a regularidade explica o ganho:** a memória paga quando os lugares se repetem, com o lado e a âncora iguais. A leitura da C1 e da C4 fica de pé, agora sem a mistura |
| **> 0** | > 0 | a memória paga com a geometria do `longe_fixo` mesmo sem repetição, e paga mais com ela |
| **≈ 0** | > 0 | **a geometria explica o ganho, não a regularidade:** a memória ganha porque a ração cai sempre do mesmo lado do comedouro (a patrulha e a posição, as H1 e H1′ da D-C1-3), repetindo ou não. A frase "a memória paga com mundo regular" não se sustenta |
| **≈ 0** | ≈ 0 ou < 0 | a memória não ganha em nenhum dos dois: contra a C1. Diagnosticar antes de ler (por exemplo, uma diferença de cenário com a run da C1) |
| < 0 | qualquer | a regularidade atrapalha a memória: contra a previsão |
| indeterminado, ou inconclusivo por premissa | — | registrado como está; nada se decide com ele |

- **Se o I-M3 e o I-PAD discordarem,** as duas leituras ficam registradas, e a do PAD é a que vale para o jogo.
- **O GEO-M0** é lido à parte, como descritivo: quanto da queda do `longe_fixo` para o `longe` já existe sem aprendizado nenhum, só pela geometria.
- **Gate que falha não para a V3.** O resultado negativo é registrado como está. **A run não se repete,** e uma faixa nova só vem com um adendo novo.

## 8. O descritivo (sem gate; nenhum muda a seção 7)

1. **A conferência da construção nas vidas:** a distribuição da distância ração–comedouro e da direção por estilo. O `longe_um`, o `longe_fixo` e o `longe_ancora` devem ter a mesma marginal; o `longe` não.
2. **As taxas por faixa de d₀,** por estilo e braço, lidas primeiro no M0, com a ressalva da LP-2 (a faixa de d₀ depende do cérebro e não serve de contraste entre braços).
3. **A decomposição da D-C1-3** (A10.4: F-a a F-d, P-a a P-e) no `longe_fixo` e no `longe_ancora`, no M3\* − M2 e no PAD − M2, para ver se o caminho do ganho (as idas e a queda do sono) muda com a repetição.
4. **As visitas ao lugar lembrado que acham a ração,** por estilo (só nos braços com M-MEM).
5. **O R-UM** (seção 1) e a escada um → três → nenhum, com a classe de cada degrau.
6. **As medidas da C5** (a viabilidade do corpo), como na C1.
7. **Por dono, só descritivo.**

## 9. As decisões para o Matheus (todas PROPOSTAS)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| LG-1 | os 4 estilos, com o `longe_ancora` e o `longe_um` | sim | sem o `longe_ancora` a pergunta não se responde; sem o `longe_um`, perde-se só a escada (secundária) |
| LG-2 | os 4 braços (PAD, M3\*, M2, M0), com o sono que segura desligado | sim | sem o PAD, a leitura não vale para o cérebro do jogo; sem o M0, perde-se a geometria sem aprendizado; com o sono que segura ligado, a run deixa de ser comparável à C1 e à C4 |
| LG-3 | os dois primários com Holm (I-M3 e I-PAD) | sim | um primário só deixaria o outro cérebro como leitura solta |
| LG-4 | a regra de leitura da seção 7, escrita antes | sim | regra escrita depois abre espaço para escolher a leitura |
| LG-5 | K = 150 e δ pelo script, decididos antes da run | K = 150, se o script der δ ≤ 0,03 | K menor pode não separar o +0,06 do 0; maior custa mais horas de máquina |
| LG-6 | a faixa 93101…93505, a confirmar | sim | nenhum, se a conferência no coordenador passar |
| LG-7 | nenhuma calibração e nenhum piloto | sim | a variância vem de vidas de outra faixa; se o σ real for maior, a margem efetiva sai no relato e o critério não muda |
| LG-8 | a separação do lado e da âncora fica fora (seção 10) | sim | a pergunta da regularidade fica respondida; a do lado contra a âncora fica para outro plano |

## 10. O que fica fora

- **Separar o lado da âncora,** que pede um mapa onde caibam as 16 direções a 20–30 células do comedouro (por exemplo, a ilha grande, 128 × 60). Fica como candidato, se a seção 7 apontar a geometria.
- **O teste causal das idas** (a D-C1-3, seção 13.6: um braço que proíbe a ida perto da queda).
- **Qualquer mudança no jogo** e a comparação com o A.

## 11. O tamanho da run e a máquina

- **150 unidades × 64 vidas = 9 600 vidas,** 14 dias cada.
- **O tempo estimado:** a L-2 levou 0,88 s de parede por vida com 4 processos (seção 12 do RESULTADO), então são cerca de **2 h 20 min a 3 h 30 min,** com o G1. O orquestrador grava a medida real no `meta.json`.
- **No máximo 4 processos e uma run de pesquisa por vez** (a V3-D8).
- **Os artefatos:** `artifacts_v3_longe_geometria/` (o `poder.json`, e o `run/` com o `meta.json`, o `resultado.json`, as medidas e as vidas compactadas, como na C1). O resultado vai no `docs/RESULTADO_V3_LONGE_GEOMETRIA.md`, e os desvios em `docs/registro/2026-11.md`.
