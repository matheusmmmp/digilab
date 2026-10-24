# Plano de análise — V2: o Gate I, o pet integrado aprende na vida pela consequência?

> **Nota (2026-10-24), a direção nova:** o Matheus decidiu, no PROMPT MESTRE, que o produto jogável vem primeiro, que o DigiBrain
> caminha para um cérebro **modular**, e que o cérebro A fica como linha de base, controle e fallback condicionado, e não como o cérebro
> final da web. As decisões "a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15) estão **SUPERADAS** desde 2026-10-24; o
> texto abaixo fica como estava, como registro. Ver `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`.
>
> Com a direção nova, este plano só roda como baseline do protótipo modular, se o Matheus decidir (DM-8).

Status (2026-10-21): **PROPOSTO**, registrado **antes de qualquer run** e antes do código da tarefa (`docs/TAREFA_V2_GATE_I.md`). As GI-1
a GI-5 estão DECIDIDAS (`docs/futuro/gate_integracao_pet.md`, seção 7). As decisões deste plano (as mesmas da tarefa): as GT-1 a GT-8
DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação.

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- O que não está aqui é descritivo pós hoc.
- Nada se ajusta olhando a validação, que roda uma vez só.
- **Nenhuma alegação de novidade.** O controle do sinal embaralhado é PROPOSTO no `docs/futuro/mundo_3d.md` (seção 5.2) e está SEM FONTE
  no projeto. O Creatures é direção, não prova (`gate_integracao_pet.md`).

## 1. A pergunta e as predições

**A pergunta (o I-APRENDE):** na linha de base integrada, a escolha do pet muda ao longo da vida mais do que a do mesmo pet sem
aprendizado, e mais do que a do mesmo pet com a consequência embaralhada?

**Os três braços** (a mesma linha de base, o mesmo mundo, o mesmo corpo e as mesmas sementes):

| braço | o que muda | a predição para Δf |
|---|---|---|
| **I** (o pet integrado) | nada: o A aprende, e os modelos do mundo aprendem | sobe: o pet passa a escolher a x, que faz bem e é a favorita |
| **S** (sem aprendizado) | os pesos do A não mudam; os modelos congelados no nascimento | perto de zero: não há o que mudar a escolha |
| **E** (o sinal embaralhado) | a consequência creditada e a amostra do desfecho trocadas por outras da mesma vida | perto de zero, ou menor que no I: o sinal tem o mesmo tamanho, mas não segue a ação |

**Os outros três critérios do Gate I** (I-CORPO, I-MUNDO, I-REPLAY) são de mecanismo: não têm predição nem IC (seção 7).

## 2. A linha de base, o pet e o dono

| item | valor | fonte |
|---|---|---|
| a configuração | a de `experiments/configs/v2_pet_que_pensa/validacao_adendo8.json`: o corpo com o passo 0, o mundo 2D (`mult_queda` 1,0), a fruta ao lado, o paladar, o dono atencioso no comedouro com 16 interações por dia, o ponto T3, a montagem completa, os canais ligados, o `ganho` 4, o `ganho_gosto` = S/2, o `g_plano` = S | GI-2; o adendo 9 do J5 |
| o pet | o do braço P1-plan | GT-1 |
| a vida | **12 dias, sem o protocolo do J5:** sem `T_m`, sem a fruta na mão, sem a troca do efeito e sem a parada das árvores. A x faz bem a vida inteira | GT-2 |
| a fruta x | a do J5: sorteada por unidade (`pet-que-pensa-x`), a favorita pelo paladar | plano do J5, seção 2, adendo 3 |
| o genoma | sem genoma | como no J5 |
| a morte | desligada | — |

**Nenhum número se calibra.** O cérebro usa os números do adendo 9 do J5.

## 3. Os braços

- **I:** o P1-plan do J5, sem mudança.
- **S:** o mesmo pet sem aprendizado nenhum:
  - os pesos do A não mudam (a L1 desligada, na forma da etapa 1 da tarefa);
  - os modelos do mundo congelados antes da primeira decisão (`congelar("desfecho", "mapa")`). Com eles no prior, o termo do plano
    deve ser zero.
  - O G-SEM-APRENDER confere as duas coisas em toda vida.
- **E:** o mesmo pet com a consequência embaralhada (GT-4):
  - **o A:** em cada decisão, o vetor dos canais que o A creditaria é trocado por um sorteado, pela rng `embaralhar`, entre os vetores
    das decisões já vividas naquela vida, incluída a própria;
  - **o desfecho:** em cada consumo, a amostra (a mudança dos receptores) é trocada por uma sorteada entre as amostras já vividas, de
    qualquer tipo. O mapa aprende como no I, porque não é consequência, é o que o pet vê;
  - **o tamanho:** os sinais têm a mesma distribuição de tamanho que os do próprio pet, mas não seguem a ação.

## 4. As medidas

**Uma oportunidade** é uma decisão de **comer** em que a x madura posta pela regra da fruta ao lado está à vista junto com pelo menos uma
alternativa ao lado (a ração madura ou outra fruta madura da regra). É a oportunidade da A7.2 do J5 (`metrics.oportunidade_ao_lado`), sem
a condição da fruta na mão, porque aqui não há mão. A fome não entra. O pet **escolhe x** quando o alvo do comer é essa x.

**A primária, por unidade e braço** (GT-5):
- `f_cedo` = a fração das oportunidades em que o pet escolhe x, nos dias 0 a 3 (o primeiro terço);
- `f_tarde` = a mesma, nos dias 8 a 11 (o último terço);
- **`Δf` = `f_tarde` − `f_cedo`.** Conta toda oportunidade da janela.
- **A unidade sem oportunidade** numa das duas janelas sai contada como **sem oportunidade** e fica fora dos contrastes daquele braço.

**Os descritivos (sem gate):**

| medida | definição |
|---|---|
| a escolha por dia | a fração de x nas oportunidades, por dia e braço |
| o nível | `f_cedo` e `f_tarde` sozinhos, por braço |
| o acaso | o acaso médio das oportunidades (1/k, o `alvos_ao_lado` do J5), por janela e braço |
| o querer aprendido | os pesos `comida:x` e `comida:racao` por dia, nos braços I e E |
| o corpo no aprendizado | a fração das decisões com a parte do corpo diferente de zero no crédito, por braço |
| quanto o plano decide | a sonda "quem decidiu", por dia, nos braços I e E |
| o desempenho | o `D_FE` e a privação, por braço |
| o custo | o CPU por vida e os bytes de log por dia, por braço |

## 5. A calibração

**Nenhuma.**

## 6. O piloto, a margem e o N

**O piloto:** os três braços, nas 20 unidades do piloto (seção 8). Serve para as premissas, a margem, o N e o custo, e os números dele não
entram como evidência. Ele roda com o sim do Matheus.

**A margem:** `Δ_I` = ½ × (1 − a média de `f_cedo` do braço I no piloto), a metade da subida máxima (a convenção do J5). Se `Δ_I` for ≤
0,05, o I-APRENDE não tem espaço para mostrar mudança: a validação não roda, e o plano volta ao Matheus.

**O N:** o menor K_u de 4 a 15 com poder simulado ≥ 0,8 nos **dois** primários, a α/2 cada (o Holm de 2).
- **O método:** o do J5, um bootstrap das diferenças por unidade do piloto, deslocadas para a margem, com 2.000 réplicas por K_u e
  descontadas as unidades sem oportunidade na taxa do piloto.
- **Se nem K_u = 15 chega a 0,8,** a validação roda com 15, e o poder sai declarado.

**Se uma premissa falhar no piloto,** o piloto para e relata, e o plano volta ao Matheus. Nada se ajusta para ela passar.

**O adendo 1** traz as premissas do piloto, a margem, o K_u, o poder e o custo, num commit antes da validação.

## 7. Gates e regra de decisão

**O bootstrap:** sobre as unidades, agrupado por base, com 10.000 reamostragens, semente 4242 e IC95; o IC90 só na equivalência.

**Os gates de mecanismo** (o I-CORPO, o I-MUNDO e o I-REPLAY; GT-7), conferidos em toda vida da validação; um que falha para a run
(falhar alto) e entra no veredito como "não passou":

| gate | critério | conferido |
|---|---|---|
| **I-CORPO** | a G-RECEPTOR (`tests/test_corpo.py`) e o G-SEM-DIRECAO (`tests/test_cheiro_orgao.py`) passam no commit da run; em toda vida do braço I, ao menos uma atualização de peso tem a parte do corpo diferente de zero | antes da run (os testes) e por vida |
| **I-MUNDO** | em toda vida, toda decisão com alvo escolhe um dos candidatos que o motor ofereceu naquela decisão, e a consequência do mundo chega ao cérebro; no braço I, os pesos das classes de alvo mudam ao menos uma vez | por vida |
| **I-REPLAY** | **G1:** toda vida se refaz do log bit a bit (o log e o sha do estado interno); **G2:** com as chaves novas desligadas, os gabaritos da etapa 0 saem iguais | por vida e no commit |
| G-SEM-APRENDER | no braço S, nenhum peso do A muda e o termo do plano é zero em toda decisão | por vida |
| G-EMB | no braço E, o sinal creditado em cada decisão é um dos já vividos naquela vida, e a rng `embaralhar` não toca o mundo | por vida |

**As premissas:**

| premissa | regra | se falha |
|---|---|---|
| **G-OPORTUNIDADE** | no máximo 25% das unidades sem oportunidade numa das janelas, por braço | o I-APRENDE é **inconclusivo por premissa** |
| **G-ESPACO** | a margem `Δ_I` > 0,05 no piloto | a validação não roda (seção 6) |

**Os contrastes:**

| gate | contraste (por unidade) | regra | papel |
|---|---|---|---|
| **G-I-SEM** | `Δf`(I) − `Δf`(S) | as categorias abaixo, com o Holm de 2 | **primário** |
| **G-I-EMB** | `Δf`(I) − `Δf`(E) | as categorias abaixo, com o Holm de 2 | **primário** |

**As categorias de cada primário** são exclusivas e lidas nesta ordem (as do J5), com a margem `Δ_I`:
1. **passa:** o limite inferior do IC95, ajustado pelo Holm, > 0. Se o limite superior do IC90 < a margem, leva o rótulo **"abaixo de Δ"**;
2. **oposto:** o limite superior do IC95 < 0;
3. **equivalente:** o IC90 dentro de ± a margem;
4. **inconclusivo:** o resto.

**O I-APRENDE passa** só com os dois primários em **passa** (GT-3).

**O veredito do Gate I:**
- **passa:** o I-CORPO, o I-MUNDO e o I-REPLAY em toda vida, e o I-APRENDE. O `ROADMAP_V2.md` muda o estado do marco, e o G1 e o G2
  genéticos podem pedir os planos deles;
- **"medido, não passou":** qualquer outro caso, com o que falhou.

**A leitura:**
- **Os dois primários passam:** o pet integrado aprende pela consequência, e não só por receber um sinal.
- **Passa contra o S e não contra o E:** o pet muda com a experiência, mas a mudança não se separa de receber um sinal do mesmo tamanho. O
  aprendizado pela consequência não está mostrado.
- **Passa contra o E e não contra o S:** a consequência importa, mas a mudança total não passa da do pet sem aprendizado. Os descritivos
  dizem se o S muda por outra coisa (o corpo, o mundo).
- **Equivalente nos dois:** o pet integrado não aprende nesta linha de base. É registrado como está, e a genética continua esperando
  (GI-4).
- **Oposto:** registrado; os pesos e a sonda dizem por quê.

## 8. Sementes

| uso | faixa | bases |
|---|---|---|
| o piloto | **63101…63505** (nova; DECIDIDA, GT-6) | 63101, 63202, 63303, 63404, 63505 (K_u = 4) |
| a validação | **64101…64505** (nova; DECIDIDA, GT-6) | 64101, 64202, 64303, 64404, 64505 (K_u do adendo 1) |

- **O prefixo das unidades:** `"pet_que_pensa"` (GT-8, DECIDIDA). A x e a fruta ao lado saem pelas derivações do J5, e as unidades são outras
  porque as bases são outras.
- **Conferências em 2026-10-21,** no `origin/main` (`0647d3e`):
  - as duas faixas estão fora de `FAIXAS_RESERVADAS` e de `FAIXAS_QUEIMADAS`, e fora das propostas da P4 (61101 e 62101) e da V3-3
    (58101 e 59101, num branch);
  - o `git grep -w` das bases em `.py`, `.md` e `.json`, fora dos artefatos, acha só um número dentro de uma série de
    `tests/gabaritos/corpo_quimica_python.json`, que não é semente;
  - nos 76 branches remotos com commit desde 2026-10-14, o `git grep` em `docs/*.md`, na `faixas.py` e nas configs não acha uso. Os
    branches mais velhos não foram varridos.
- **O registro na `FAIXAS_RESERVADAS`** vai na etapa 1 da tarefa, antes de qualquer run. Este PR é só de documento.

## 9. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **O pet já nasce escolhendo a x:** a atração inata e a geometria dão um `f_cedo` alto, e sobra pouco para subir | a margem vem do próprio `f_cedo` do piloto; com ≤ 0,05, o plano volta (G-ESPACO) |
| R-2 | **O primeiro terço já tem aprendizado:** o pet aprende rápido, e o `Δf` subestima o aprendizado | o contraste é entre braços com as mesmas janelas; a escolha por dia mostra a curva |
| R-3 | **O E ainda aprende:** o vetor sorteado, sendo do próprio pet, carrega a média da consequência, e o pet aprende o que é bom em média | é o que o controle mede: o I tem de passar do E. Se o E aprender tanto quanto o I, a leitura da seção 7 diz isso |
| R-4 | **O S não é o instinto puro:** com os modelos congelados no prior, o termo do plano deveria ser zero, mas o código decide | o G-SEM-APRENDER confere em toda vida |
| R-5 | **A oportunidade sem a mão** muda o que conta, em relação ao J5 | é a A7.2 sem a condição da mão; a escolha por dia e o acaso médio saem nos descritivos |
| R-6 | **A linha de base não é a do jogo:** o jogo web não tem o mundo físico nem o planejador | é a decisão GI-2: o Gate I é da pesquisa; o porte fica fora |
| R-7 | **O veredito vira alegação:** "o pet integrado" lido como "o pet do Creatures" | o relato diz o que o gate mede, e o Creatures continua só direção |

## 10. O lugar dos adendos

- **Adendo 1:** as premissas do piloto, a margem, o N e o custo. É obrigatório antes da validação.
- **Nenhum adendo muda os primários deste plano.**

## 11. Artefatos e reprodução

- **As pastas:** `artifacts_v2_gate_i/piloto/` e `artifacts_v2_gate_i/validacao/`. Cada uma traz:
  - o `meta.json`, com o sha256 do pacote (`sha256_do_pacote`) e de `mundo.py`, `corpo.py`, `modelo_mundo.py`, `lobos.py`, `config.py`
    e `engine.py`;
  - as medidas por braço e os gates de mecanismo por vida. As vidas ficam fora do git.
- **As configs:** `experiments/configs/v2_gate_i/{piloto,validacao}.json`, com o campo `"plano"`.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe, e o piloto recusa as sementes da validação.

## 12. Decisões do Matheus

As de `docs/TAREFA_V2_GATE_I.md` (seção 8). **As GT-1 a GT-8 DECIDIDAS em 2026-10-21, pela recomendação.** As que
tocam este plano:
- **GT-3:** os dois controles, com o I-APRENDE passando só contra os dois;
- **GT-4:** como embaralhar;
- **GT-5:** a medida;
- **GT-6:** as faixas;
- **GT-7:** os gates de mecanismo;
- **GT-8:** o prefixo, `"pet_que_pensa"` (DECIDIDA).

## 13. Referências

Nenhuma referência nova. As do Creatures estão em `docs/futuro/gate_integracao_pet.md` (seção 8) e são direção, não base do teste.
