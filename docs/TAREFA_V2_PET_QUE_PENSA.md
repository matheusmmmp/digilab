# TAREFA V2 — O PET QUE PENSA (J5): o modelo do desfecho, o mapa da comida e o planejador de um alvo (2026-10-13)

**Equipe:** coordenador: Gerente. Workers:
- **B:** os modelos, o planejador e o cérebro;
- **A:** o mundo (a troca de tipo, a fruta na mão, os candidatos de árvore);
- **D:** a bancada e as medidas;
- **C:** o plano.

Worktree e branch de cada etapa: `v2-pet-que-pensa-<etapa>`.

**Status: ABERTA.** O desenho é `docs/futuro/pet_que_pensa.md`, com **PQ-1 a PQ-7 DECIDIDAS** pelo Matheus (2026-10-13). O plano é
`docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, commitado antes de qualquer run. As **PP-1 a PP-9** do plano também estão **DECIDIDAS** (2026-10-13), pela recomendação.

**O que já está decidido:**
- **DS-1 (2026-10-07), a medida:** o pet planeja quando muda a escolha depois de uma mudança no mundo, sem ter reexperimentado a
  consequência. É o par revalorização + mudança de transição.
- **PQ-1, a arquitetura:** o modelo do desfecho, o mapa da comida e o planejador de um alvo, somados ao cérebro A.
- **PQ-2, o horizonte:** um alvo.
- **PQ-3, onde entra:** um lobo novo no A, `planejamento`, somado pelo `g_plano`. Com 0, o cérebro de hoje.
- **PQ-4, o teste 1:** a fruta revalorizada é dada na mão, fora do mapa.
- **PQ-5, o Digicorpo:** fica separado.
- **PQ-6, o tamanho:** os modelos ficam num módulo próprio, com teto próprio, e o A ganha 0 pesos pelo planejador.
- **PQ-7, a web:** o v11 segue pausado.
- **TP-1 e TP-2, o teto de pesos:** o teto é por plano. O padrão é 1000 e o limite é 2000. As classes de alvo por árvore da etapa 2b
  pedem o teto deste plano.

## 1. Pergunta

**O cérebro A com o planejador muda a escolha depois de uma mudança no mundo que ele não reexperimentou, e o A de hoje não?**

O par da DS-1 separa o que cada peça faz:
- **teste 1, a revalorização:** passa com o modelo do desfecho;
- **teste 2, a mudança de transição:** só passa com o mapa.

## 2. O desenho (PROPOSTO; detalhe em `docs/futuro/pet_que_pensa.md`, seções 2 e 3)

### 2.1 Os modelos

Ficam no módulo novo `digilab/modelo_mundo.py`, com a `ConfigModeloMundo` no fim de `config.py`. Só inteiros, sem rng. O módulo só importa
`config` e `events`.

**O modelo do desfecho**, por tipo de comida (a ração, `a`, `b`, `c` e a podre) e por receptor:
- **o que guarda:** a mudança esperada da leitura ao comer, Δ̂;
- **como atualiza:** `Δ̂ ← Δ̂ + div_arred((Δ_obs − Δ̂) · passo_desfecho, S)` em cada consumo que o pet percebe. Conta o consumo no mapa e
  o da mão;
- **Δ_obs:** os receptores logo depois de comer menos os da decisão;
- **o prior:** 0, o pet não sabe nada.

**O mapa da comida**, por árvore do layout e pelo comedouro, por tipo:
- **o que guarda:** a frequência do que o pet **viu** lá, em S;
- **como atualiza:** cada vez que uma comida madura aparece nos `vistos` a até `raio_ancora` de um tronco, ela conta para aquela árvore,
  com o esquecimento `m ← m + div_arred((1[tipo] · S − m) · passo_mapa, S)`;
- **o prior:** 0. O pet não sabe o que cai onde;
- **a posição das árvores:** é a dos troncos que o pet já viu (os `vistos`).

**O que os modelos não leem:** o químico, o `Estado`, o registro do mundo, o `efeito_frutas` do motor e o tipo de uma árvore que o pet
ainda não viu dar fruta.

### 2.2 O planejador e o lobo `planejamento`

Para cada candidato de alvo k:

`V(k) = Σ_tipo p̂(tipo | k) · valor(Δ̂_tipo, receptores de agora) − custo(distância até k)`

- **`valor`:** a conta do `lobos.sinal_corpo` com a leitura prevista. Ela é a leitura de agora mais Δ̂, cortada em [0, S], e o ganho é o
  da consequência.
- **`custo`:** a distância vezes o gasto de andar previsto, que é o Δ̂ do cansaço por subunidade, aprendido no `estimulo_andar` como o
  desfecho.
- **O termo no peso efetivo:** `div_arred(g_plano · V(k), S)`, cortado em [−teto_plano, +teto_plano]. Vai ao alvo, em cima do alvo
  aprendido, e à decisão de comer ou explorar, com o maior V dos alvos dela. Com `g_plano` 0, nada.

**A sonda "quem decidiu":** o mesmo u sem o termo, no motivo.

**O fator do motivo:**
- só quando a sonda muda a escolha;
- o texto nomeia o tipo e a árvore do modelo, por exemplo "fui ao J2 porque lá cai a b, e a b me faz bem";
- a expressão ganha os textos com marcador único.

### 2.3 O mundo (A)

**A troca de tipo por árvore:**
- num tick gravado no registro, os tipos de duas classes de árvore se trocam: as do tipo x passam a dar y, e as do y passam a dar x;
- funciona como a troca do mutável e é refeita pelo replay;
- desligada, nada muda.

**A fruta na mão:** um evento do dono, `dar_fruta_<f>`, fora do orçamento e pelo canal do mundo.
- **Onde:** o pet come a fruta na hora, onde estiver, com o efeito vigente, sem decisão e sem andar.
- **Na percepção:** entra como consumo, com o tipo, para o modelo do desfecho.
- **G-SEM-CREDITO:** nenhum sinal de reforço vai a peso de decisão nem de alvo do A. O `mudanca_no_corpo` não credita esse evento.
  Sem isso o hábito também mudaria, e o teste 1 não mediria nada.

**Os candidatos de árvore lembrada:** no explorar, o motor oferece `arvore:<id>` para cada tronco que o pet já viu, com o alvo no pé da
árvore. Vêm depois dos de hoje. O padrão do motor e o instinto nunca os escolhem. É a PP-1 do plano.

### 2.4 As classes de alvo por árvore no alvo aprendido (B, a PP-2)

O hábito tem de poder aprender "ir ao J2", senão o teste 1 compara o planejador com um hábito que não sabe ir a lugar nenhum.
- **As classes novas:** uma por árvore (`arvore:J1` … `arvore:M6`), nas regras em que o explorar é candidato.
- **O tamanho:** 3 regras × 9 árvores = 27 pesos a mais.
- **O teto:** o teto do plano (TP-1) declara o número.

## 3. Depende de

- **Na `main`:** o mundo físico, o corpo (o regime "química"), o alvo aprendido (#255) e o sinal pelo corpo.
- **Antes da calibração:** o J1 validado, com os números do mundo, e o desempate do cheiro no motor (o achado do #278).

## 4. Etapas e donos

| etapa | dono | arquivos | entrega | gates |
|---|---|---|---|---|
| **0. gabaritos** | B | `tests/gabaritos/pet_que_pensa_vidas_de_hoje.json` | as vidas do mundo físico com o corpo químico (P0, P1, P3; os dois layouts; o alvo aprendido), gravadas **antes** | — |
| **1. os modelos** | B | `digilab/modelo_mundo.py`, a `ConfigModeloMundo` no fim de `config.py` | o modelo do desfecho e o mapa, só observando | **G-INT** (AST); **G-TETO-MODELO**; **G-RECEPTOR-MM** (só a percepção; mudar um químico sem receptor e o registro do mundo não muda os modelos); conta exata de um passo de cada; **G-OBS-MM** (os modelos observando, com `g_plano` 0: a vida byte a byte, gabaritos da etapa 0); **G1** (o replay refaz os modelos) |
| **2. o planejador** | B | `digilab/policies/lobos.py` (o lobo `planejamento`, atrás de `ConfigLobos.g_plano`), `digilab/motivo.py`, `digilab/expressao.py` | o termo no alvo e na decisão, a sonda, o fator e os textos | **G2** (`g_plano` 0 = a vida de hoje); **G-PESOS-A** (o `n_pesos` do A igual com e sem o planejador); conta exata de V(k) e do termo; a sonda reproduz a escolha sem o termo; **G1** |
| **2b. as classes por árvore** | B | `digilab/policies/lobos.py` (`CLASSES_ALVO`, atrás de uma chave) | `arvore:<id>` no alvo aprendido | **G2** com a chave desligada; no prior, o P0 com lobos é o instinto do mundo byte a byte com os candidatos de árvore oferecidos; conta exata; **G1** |
| **3. o mundo** | A | `digilab/mundo.py`, `digilab/events.py` (o fim do enum) | a troca de tipo por árvore, a fruta na mão e os candidatos de árvore lembrada | **G2** (desligados = a vida de hoje); **G-SEM-CREDITO** (espião: a fruta na mão não chega ao `receber_acao_dono` nem ao crédito do A, e chega ao modelo do desfecho); a troca no tick e o replay; os candidatos só de troncos vistos, depois dos de hoje; **G1** |
| **4. a bancada** | D | `experiments/bancada_v2.py`, `digilab/metrics.py`, `experiments/configs/v2_pet_que_pensa/` | os braços do plano (P1, P1-plan, P1-plan-desfecho, P1-plan-cong); os protocolos T1 e T2; as oportunidades e as medidas; as faixas e o prefixo `pet_que_pensa` | o G1 de toda vida; as medidas em dados com a resposta conhecida; o congelamento conferido (depois do tick da mudança, o mapa do P1-plan-desfecho e os dois modelos do P1-plan-cong não mudam; PP-8) |
| **5. o plano** | C | `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md` | — | commitado antes de qualquer run (vai neste PR) |
| **6. a web** | A | depois da validação, com o porte do A (PQ-7) | — | **G-PAR** |

**A ordem:** 0 → 1 → 2 → 2b, e a 3 em paralelo com a 1 e a 2. Depois vem a 4.

Um PR por etapa, com o relato no corpo. **O merge é do Matheus.**

## 5. Experimento e gate

- **O plano:** `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`.
- **As sementes propostas:** 45101…45505 (calibração e piloto) e 46101…46505 (validação), com o prefixo `pet_que_pensa`. O D as registra.
- **GPU:** não.

## 6. Fronteiras (o que não muda)

- **`engine.py` e o `AcaoPet`:** não mudam. O evento da mão entra no fim do `AcaoUsuario`.
- **O instinto:** não lê os modelos, e o P0 continua o instinto do mundo.
- **O Digicorpo:** não muda (PQ-5).
- **Os modelos não decidem nada:** só o planejador, pelo `g_plano`.
- **Os pets v1 a v10 e a web de hoje:** iguais.

## 7. Fora desta tarefa

- **O horizonte além de um alvo, a busca em árvore e a SR** (PQ-1, PQ-2).
- **A arbitragem por incerteza** (a pista de Daw, Niv e Dayan).
- **O mapa aprendendo do que o outro pet comeu** (os dois pets).
- **O Digicorpo na decisão** (a etapa 3 do ego).
- **A web.**

## Paladar, etapa 1, o mundo (A, 2026-10-14; `docs/futuro/paladar.md`, seções 3.1, 4 e 6) — GATES PASSAM

PL-1 a PL-9 e PJ-1 a PJ-5 decididas pelo Matheus, pela recomendação. Infraestrutura, sem run; só as sementes dos testes. Mudaram a
`ConfigPaladar` no fim de `config.py`, `digilab/mundo.py` e uma conferência em `digilab/grupo.py`. `engine.py`, o corpo, o
`motor_corpo.py` (é do B, na etapa 2), os cérebros, a bancada e a web não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O gabarito antes do código** (commit próprio): `tests/gabarito_paladar_mundo.py` → `tests/gabaritos/paladar_mundo_vidas_de_hoje.json`,
  84 vidas. Reusa os casos do gabarito do mundo do J5 (os dois layouts, sem o corpo e com o corpo químico, o instinto, o P0 e o P1 com o
  alvo aprendido) e os do planejador (o mundo do J5 com a fruta na mão e a troca de tipo no dia 2, o corpo químico com e sem o
  metabolismo), mais o corpo inteiro.
- **`ConfigPaladar`** (desligada; `CONFIG_PALADAR_LIGADA`; registro `mundo.PARAMETROS_PALADAR_MUNDO`, PROPOSTOS, SEM FONTE):
  - `perfis`: por tipo (`racao`, `a`, `b`, `c`), um inteiro em [0, C] por qualidade (`QUALIDADES_PALADAR`: doce, azedo, amargo e
    salgado);
  - as frutas são a mesma forma girada (3C/4 e C/4 nas três primeiras qualidades), e a ração tem C/4 de salgado e nada mais;
  - só com o mundo físico. A config confere os tipos, as qualidades e a faixa.
- **No motor** (`MotorMundo(..., cfg_paladar=)`, guardada em `self.cpal`):
  - o registro de cada consumo (`consumos_mundo`) ganha `perfil`: uma cópia do perfil do tipo na comida madura, None na podre;
  - o `ocorrido["comeu"]` do `comer` e do "achou e comeu" é esse mesmo registro;
  - a fruta na mão (sempre madura) também entra com o perfil;
  - `perfil_de(tipo)` dá a cópia e falha alto sem a chave;
  - o mundo não usa o perfil para mais nada: a nutrição, o humor, o cheiro, a percepção, os candidatos e as rngs não mudam.
- **No grupo:** os pets têm de ter o mesmo Paladar (os perfis são das comidas do mundo); senão, falha alto.
- **O contrato com o B** (etapa 2, combinado por mensagem): o `MotorCorpo` passa `perfil=comeu["perfil"]` ao `estimulo_consumo_mundo`
  com a sub-chave `paladar` do corpo, e na mão lê `self.cpal.perfis[f]`. O `motor_corpo.py` fica só com ele.
- **Gates** (`tests/test_paladar_mundo.py`, 11):
  - **G2:** as 84 vidas byte a byte, sem a chave e com a chave explícita desligada;
  - **ligado, a vida é a mesma:** em todas as 84 vidas, o log, o estado, as ações, as rngs e o registro do mundo físico saem iguais; só os
    consumos ganham o `perfil`. O perfil é o do tipo na madura e None na podre, nos três caminhos (o comer, o achou e comeu e a mão). O
    `ocorrido["comeu"]` é o próprio registro;
  - outros perfis mudam só o registro; o perfil é uma cópia;
  - a config: os perfis do desenho, a forma girada, o registro de status e as falhas altas;
  - **G1:** o replay refaz os registros com o perfil (instinto e P1, sem e com o corpo);
  - o grupo: o mesmo Paladar nos dois pets.

## A fruta ao lado da ração, o lado do mundo e do dono (A, 2026-10-14; o RP-2 de `docs/futuro/paladar.md`) — GATES PASSAM

Decisão do Matheus depois do #316 (o pet come ~20% de fruta, mas o querer vai à ração, porque as duas nunca ficam lado a lado). Os números
foram combinados com o C, que escreve o adendo 5 do plano. Infraestrutura, sem run; só as sementes dos testes. Mudaram a
`ConfigFrutaAoLado` no fim de `config.py`, o evento `deixar_fruta` em `digilab/events.py` e `digilab/mundo.py`. `engine.py`, o corpo, os
cérebros, a bancada e a web não mudaram. Interpretações em `docs/registro/2026-10.md`.
- **O gabarito antes do código** (commit próprio): `tests/gabarito_fruta_ao_lado.py` → `tests/gabaritos/fruta_ao_lado_vidas_de_hoje.json`,
  92 vidas. São os 84 casos do mundo com o paladar e 8 vidas da bancada do J5 com o paladar (P1 e P1-plan, T1 e T2, duas sementes).
- **`ConfigFrutaAoLado`** (desligada; PROPOSTOS, SEM FONTE):
  - `tipos` (a, b, c), `coluna` (+1) e `linhas` (−1, 0, +1), relativas ao comedouro;
  - `teto_por_tipo` (1 madura de cada tipo ao lado no chão).
- **No motor:**
  - o evento `deixar_fruta(tipo, x, y)` só vale logo depois de uma ração deixada pelo dono no mesmo tick, e grava o id dela;
  - a fruta nasce madura, com a origem `dono_ao_lado`;
  - os registros `frutas_ao_lado` (tick, id, tipo, x, y, ração) e o consumo com o tipo e a origem;
  - o `estado()` ganha `fruta_ao_lado` (as maduras ao lado no chão, por tipo);
  - **fora do orçamento e sem contato;** só com um pet. O replay refaz tudo.
- **O dono** (`DonoFrutaAoLado`, pelo `simular_vida_mundo(..., ao_lado=)`):
  - depois de cada ração do `DonoComLugar` no comedouro, põe os tipos abaixo do teto;
  - as células seguem a permutação de (a, b, c) sorteada uma vez por vida pela rng `fruta-ao-lado`;
  - com o estilo `perto` ou `longe`, falha alto.
- **Gates** (`tests/test_fruta_ao_lado.py`, 13):
  - **G2:** as 92 vidas byte a byte, sem a chave e com a chave explícita desligada; sem a chave, nada novo no `estado()` nem no resumo;
  - **a mecânica**, numa vida com o atencioso e com o relapso, três sementes cada:
    - toda fruta vai logo depois de uma ração, no mesmo tick, na célula do tipo;
    - em cada passo com ração, o dono põe exatamente os tipos abaixo do teto, e nunca passa dele;
    - o orçamento fecha igual, e as frutas não contam como gesto do dono;
    - os consumos ao lado levam o tipo e a origem;
  - **sem contato:** o relógio do cuidado e o cérebro não veem a fruta;
  - **a permutação:** a do `shuffle` da rng própria, uniforme entre as 6 em 600 sementes, com o `random` global intocado;
  - **com o corpo e o paladar:** a fruta ao lado é comida com o perfil do tipo;
  - **G1:** o replay refaz as frutas ao lado e a vida, sem e com o corpo;
  - **as recusas:** o estilo, a chave, a fruta sem ração e o grupo.
- **Fumaça descritiva** (só o encanamento, instinto, atencioso, 5 dias, sementes 101 a 303): o pet comeu de 2 a 16 frutas ao lado por vida.
- **Para o D:** a bancada liga a regra nos braços do J5 (o `simular_vida_fisico` com o `ao_lado` e a `cfg_fruta_ao_lado` no motor).
