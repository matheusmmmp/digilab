# TAREFA V2 — O PET QUE PENSA (J5): o modelo do desfecho, o mapa da comida e o planejador de um alvo (2026-10-13)

**Equipe:** coordenador: Gerente. Workers:
- **B:** os modelos, o planejador e o cérebro;
- **A:** o mundo (a troca de tipo, a fruta na mão, os candidatos de árvore);
- **D:** a bancada e as medidas;
- **C:** o plano.

Worktree e branch de cada etapa: `v2-pet-que-pensa-<etapa>`.

**Status: ABERTA.** O desenho é `docs/futuro/pet_que_pensa.md`, com **PQ-1 a PQ-7 DECIDIDAS** pelo Matheus (2026-10-13). O plano é
`docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, commitado antes de qualquer run. As decisões que sobram (PP-1 a PP-9) estão no plano.

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
