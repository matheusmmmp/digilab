# Espec da sonda do E(P): quantos corpos o pet alcança de um lugar (F5)

Status (2026-11-17): **APROVADO pelo Matheus** (2026-11-17, no chat da sessão da F5): à pergunta "Você revisa e aprova a espec e as
D-F5-2 a D-F5-8 no PR #965?", a resposta literal foi **"Aprovo as recomendações"**. Os números novos continuam PROPOSTOS, SEM FONTE.
As três correções do SE1 (seções 2.1, 2.2 e 2.4) foram aceitas pelo Matheus em 2026-11-17: à pergunta "Aceita as três correções da
espec feitas no SE1?", a resposta literal foi **"Aceito as correções"**.
Esta é a espec da sonda descritiva da frente F5, pedida pela decisão **D-F5-1** do Matheus (2026-11-17,
no chat da sessão da F5): à pergunta "A F5 fica como pesquisa ou vira frente agora?", a resposta literal foi **"Pesquisa, com sonda"**.
Depois, a esta pergunta: "Escrevo agora a espec da sonda do E(P) em docs/, numa worktree com PR?", ele respondeu **"Sim, escreva a
espec"**.

O código vem só depois desta aprovação, e só em `experiments/` e `tests/`. As decisões D-F5-2 a D-F5-8 (seção 8) foram aceitas como
recomendadas. A tarefa é a `docs/TAREFA_V3_SONDA_EMPOWERMENT.md`. O levantamento está no vault, em
`DigiLab — Revisão de escopo/LEVANTAMENTO_EMPOWERMENT_F5_2026-11-17.md`. O código foi lido na `origin/main` `586b1107` (2026-11-17).

**Regras desta espec:**
- **só leitura**: nenhuma vida nova, nenhuma semente nova, nenhuma faixa. O motor, o `engine.py`, o corpo, o DigiBrain e a web não
  mudam;
- a conta é pura, em inteiros, sobre cópias das entradas da decisão. **Nenhuma rng é chamada**, e a vida sai igual com e sem a sonda
  (G-S0, seção 6);
- todo número novo é **PROPOSTO, SEM FONTE**, e nenhum vai para o `digilab/config.py`: a sonda não é mecânica de jogo. Por isso também
  não há espelho na web nem G-PAR;
- **nenhuma alegação de novidade.** A conta é a forma determinística do empowerment, que já está publicada (seção 1);
- **vocabulário:** o `E(P)` é uma medida tirada do registro, não algo que o pet "pensa" ou "sabe". O Dreyfus (2002),
  `10.1023/A:1021351606209`, sustenta que o especialista age sem representar o objetivo, e isso tensiona uma estimativa explícita. A
  sonda não diz que o pet faz essa conta;
- **o papel é descritivo, não gate**: a leitura da seção 5.4 só diz se a H-EMP-1 vale um plano depois da F3.

## 0. Em uma página

| peça | o que é |
|---|---|
| **a pergunta** | o número de corpos distintos que o pet alcança comendo, a partir de um lugar, varia entre lugares? E ele se separa da simples contagem das classes lembradas por perto? |
| **a conta** | `E(P)`: de P, todas as sequências de até n = 2 consumos das classes ao alcance. Para cada uma, o corpo previsto pelo `d̂` e pelo `andar` do M-PLAST, em faixas de quartos de S. O `E(P)` é o número de tuplas distintas de faixas (seção 2) |
| **o controle** | `CONT(P)`: o número de classes distintas ao alcance de P (seção 2.5) |
| **onde roda** | um script novo, `experiments/sonda_empowerment_f5.py`, que embrulha o `Impulso.unidades` na instância do cérebro, como a auditoria da PET_VIVO (`experiments/auditoria_pet_vivo.py`) |
| **as vidas** | as que já existem (D-F5-2): os gabaritos das sementes dos testes e, se a D-F5-2 quiser, as vidas de uma run já feita |
| **o que mede** | M-S1, se o `E` varia; M-S2, se a ordem do `E` difere da do `CONT`; M-S3, exploratória, se o `explorar` já vai aos lugares de `E` maior (seção 5) |
| **o que decide** | nada no jogo. Se o `E` é plano ou igual ao `CONT`, a F5 acaba ali. Se não é, a H-EMP-1 vira um plano **depois da F3** |

## 1. De onde vem a conta

ACHADO DA LITERATURA (as referências estão em `docs/referencias/v3_f5_empowerment_referencias_verificadas.csv`, conferidas no Crossref em
2026-11-17):
- O empowerment é a capacidade de canal, no sentido de Shannon, do canal que vai dos atuadores do agente aos seus sensores (Klyubin,
  Polani e Nehaniv 2005, `10.1109/CEC.2005.1554676`, texto).
- Num mundo discreto e determinístico, ele se reduz a `log |S_A|`, o log do número de estados alcançáveis com as ações disponíveis (Salge,
  Glackin e Polani 2014, `10.1007/978-3-642-53734-9_4`, seção 4.4.6, eq. 4.15, pela versão arXiv 1310.1863). A mesma fonte diz que o número
  de sequências cresce exponencialmente com o horizonte (4.5.5) e que a resolução dos sensores é um problema.
- Brändle et al. (2023), `10.1038/s41562-023-01661-2`, medem o "empowerment" de um elemento de jogo pela contagem de elementos distintos a
  que ele leva (texto do preprint).
- Klyubin, Polani e Nehaniv (2008), `10.1371/journal.pone.0004018`, texto: o estado de maior empowerment é um bom palpite a priori para
  alcançar um objetivo que surja de repente. É de onde vem a H-EMP-1.

**Leitura do DigiLab** (HIPÓTESE): o modelo do desfecho do pet é um número por classe e receptor, não uma distribuição. Então, dentro do
modelo do pet, vale o caso determinístico. O empowerment vira uma contagem, e o log não muda a ordem. **É estreito:** o `d̂` só prevê o
consumo, então o `E(P)` conta os corpos alcançados comendo, e não o que dormir, brincar ou chamar o dono abririam.

## 2. A conta

### 2.1 O que a conta lê (na decisão k, sem mudar nada)

FATO VERIFICADO (`origin/main` `586b1107`):
- `Plasticidade.desfecho`: classe → os `d̂` na ordem de `Plasticidade.receptores` (`digilab/digibrain/plast.py:55`). As classes são
  `CLASSES_DESFECHO` (`plast.py:34`), mais a `tela` com a subchave `olhar`;
- `Plasticidade.andar`, o custo aprendido de andar (`plast.py:56`). A correção da energia pelo andar previsto é
  `div_arred(andar × d, S)` (docstring, `plast.py:8-9`);
- os episódios guardados do M-MEM, com `ponto`, `lugar`, `classe` e `origem`: a memória de lugar, `Memoria.episodios` (o `n_ep`), e, com
  a memória autobiográfica, as três camadas dela, `Memoria._guardados()` (`digilab/digibrain/mem.py:267`). O lugar de um ponto é
  `lugar_de(x, y)` (`mem.py:186`). **Correção do SE1:** a espec aprovada citava só o `_guardados()`. Nas vidas dos gabaritos, a
  autobiográfica guarda só os consumos que passam do limiar, e a de lugar guarda todos; a sonda lê as duas;
- o alcance da memória de lugar, `d_max` (`digilab/config.py:2982`, 1024 subunidades, PROPOSTO, SEM FONTE);
- a faixa em quartos de S, `_faixa(v, S)` (`mem.py:79`): quantos dos limites S/4, S/2 e 3S/4 o valor alcança, de 0 a 3;
- a percepção da decisão, `sens`: `pos`, `objetos` (com `classe`, `dx` e `dy`, relativos ao pet: o ponto do objeto é `pos + (dx, dy)`;
  **correção do SE1**, a espec aprovada dizia `x` e `y`) e `leitura` (receptor → valor na escala S), como o `lembrar` a
  usa (`mem.py:276-290`).

### 2.2 Os lugares P

PROPOSTO: em cada decisão k, P percorre:
- o lugar do pet, `lugar_de(sens["pos"])`;
- os lugares de todo episódio guardado, sem repetir;
- os lugares dos alvos `explorar/ponto` das unidades da decisão, sem repetir (para a M-S3 ler o `E` do alvo; **acréscimo do SE1**, que a
  espec aprovada deixava implícito no "mais um" do custo).

Cada lugar é representado pelo seu centro, `(lx·sub + sub/2, ly·sub + sub/2)` em subunidades, com a divisão inteira (D-F5-5).

### 2.3 As classes ao alcance de P

Um **ponto de classe c** é:
- o `ponto` de um episódio guardado com `origem = "consumo"` e `classe = c`, para c em `CLASSES_DESFECHO`; ou
- a posição de um objeto que a decisão vê, com classe c em `CLASSES_DESFECHO`.

A classe c está **ao alcance** de P quando algum ponto dela está a `dist ≤ d_max` de P, com `dist = raiz_inteira(dx² + dy²)`. A
distância da classe, `d(P, c)`, é a do ponto mais perto (no empate, o primeiro na ordem dos episódios, depois a dos objetos). O conjunto é
`A(P)`, na ordem de `CLASSES_DESFECHO`.

### 2.4 As sequências e o corpo previsto

PROPOSTO (D-F5-3, D-F5-4):
- Contam as sequências de 0, 1 ou 2 classes de `A(P)`, **sem repetir classe**. A sequência vazia (não comer) conta. Com |A| ≤ 6, são no
  máximo 1 + 6 + 30 = 37 sequências.
- O caminho de uma sequência é `d(P, c₁)` e, para a segunda, mais a distância entre os pontos escolhidos de c₁ e de c₂.
- O corpo previsto de cada receptor r:
  `v_r = clamp( leitura_r + Σ_i d̂[c_i, r] + [r = energia] · div_arred(andar × caminho, S), 0, S )`
  **Correção do SE1 (o sinal):** a espec aprovada tinha `−`. O `andar` é a mudança da energia por subunidade andada, × S, e fica negativo
  quando andar cansa (`plast.py:107`: `amostra = div_arred((energia depois − energia antes) × S, d)`). Ele entra somado, como no
  `valor_previsto` do lobos (`digilab/policies/lobos.py:2168`). A intenção aprovada (o custo de andar até a comida) não muda.
- A tupla de faixas da sequência: `( _faixa(v_r, S) for r in receptores )`.

### 2.5 E(P) e CONT(P)

- `E(P)` = o número de tuplas de faixas distintas entre as sequências, de 1 a 37.
- `CONT(P)` = |A(P)|, de 0 a 6.
- **O `E(P)` não depende do log:** a ordem é a mesma. Nenhuma fração nem float entra na conta.

**Custo:** por decisão, no máximo L × 37 sequências × R receptores, com L lugares (o do pet mais os lugares distintos dos episódios
guardados, mais os alvos `explorar/ponto` das unidades da decisão) e R ≤ 11 (NÃO CONFIRMADO: o tempo real; a seção 6 mede).

## 3. Onde fica no código

PROPOSTO (D-F5-6):
- **Novo:** `experiments/sonda_empowerment_f5.py`.
  - As funções puras `alcance(P, eps, objetos, d_max)`, `e_de(P, ...)` e `cont_de(P, ...)` recebem cópias e devolvem inteiros.
  - O coletor embrulha, na instância do cérebro, o `Impulso.unidades` (o mesmo jeito da auditoria da PET_VIVO,
    `experiments/auditoria_pet_vivo.py`, docstring). Ele lê o estado do M-PLAST e do M-MEM **antes** da decisão e grava, por decisão:
    - k, o tick, o lugar do pet;
    - para cada P: `(P, E, CONT)`;
    - o comportamento escolhido e, se for `explorar` com alvo, o lugar do alvo.
- **Novo:** `tests/test_sonda_empowerment_f5.py` (seção 7).
- **Não mudam:** `digilab/` inteiro, `web/`, `engine.py` e o `config.py`. A sonda não toca a lista de comportamentos, o M-ARB nem as
  sondas "quem decidiu".
- **Saída:** `artifacts_v3_f5_sonda/sonda.json` (as medidas da seção 5) e `sonda_decisoes.json.gz` (o registro por decisão).

## 4. As vidas

PROPOSTO (D-F5-2), duas fontes possíveis:
- **(a) os gabaritos das sementes dos testes**, refeitos com o código de hoje e conferidos contra o gabarito decisão a decisão (o jeito da
  AN0 na auditoria da PET_VIVO). É barato e usa o código exato da `main`.
- **(b) as vidas de uma run já feita** (por exemplo, a da LONGE_GEOMETRIA, `artifacts_v3_longe_geometria/`), rejogadas com o código da
  run numa worktree destacada. NÃO CONFIRMADO: se os logs dessa run guardam o necessário para o replay e com qual commit. A D-F5-2 pede
  essa conferência antes.

**Recomendação: (a) primeiro.** A (b) só se a (a) não for plana (seção 5.4), para ver o mesmo em mais vidas.

## 5. As medidas (descritivas)

Todas em inteiros ou frações `num/den`, sem teste de hipótese.

- **M-S1, a variação.**
  - A distribuição do `E` do lugar do pet por decisão: o mínimo, os quartis e o máximo.
  - A fração das decisões com `E > 1`.
  - Por decisão, a amplitude `max_P E − min_P E` entre os lugares, com a mediana e a fração das decisões com amplitude ≥ 2.
- **M-S2, a separação do `CONT`.** Em cada decisão, para os pares de lugares (P, Q), a fração de pares **discordantes**: `E(P) > E(Q)`
  e `CONT(P) < CONT(Q)`, ou o contrário. Os empates de um lado só contam à parte. É a contagem de Kendall, sem estatística.
- **M-S3, exploratória.** Nas decisões de `explorar` com alvo de lugar: a fração em que o lugar do alvo tem o maior `E` entre os
  candidatos, comparada com 1/(número de candidatos). Só descreve. A sonda não muda o alvo.

### 5.4 A leitura (registrada antes, PROPOSTA, SEM FONTE; D-F5-7)

- **"plano"**: a fração das decisões com amplitude ≥ 2 fica abaixo de 1/10;
- **"igual ao CONT"**: a fração de pares discordantes fica abaixo de 1/20;
- se der "plano" ou "igual ao CONT", **a F5 acaba ali**, sem plano;
- se não der nenhum dos dois, a H-EMP-1 do levantamento (com os braços SEM, EMP e CONT) vira um plano de análise **depois da F3**, com
  as decisões dele.

## 6. As conferências que falham alto

- **G-S0, a vida igual:** cada vida sai igual com e sem a sonda: o mesmo log byte a byte e o mesmo sha256 do gabarito. Se não sair, a
  sonda para.
- **G-S1, nenhuma rng:** o estado de toda rng do pet é o mesmo antes e depois de cada chamada da sonda.
- **O tempo:** antes da medida, o tempo por decisão numa semente dos testes (`--medir-tempo`, como na auditoria da PET_VIVO). No máximo 4
  processos, por causa da máquina.

## 7. Os testes (antes do código da medida)

| teste | o que confere |
|---|---|
| **T-E1** | um mundo de brinquedo com o `d̂` e os pontos dados à mão: o `E` e o `CONT` iguais à conta feita no papel (incluindo dois corpos que caem na mesma faixa e contam um só) |
| **T-E2** | sem episódio e sem objeto: `E = 1` (só a sequência vazia) e `CONT = 0` |
| **T-E3** | com o `d̂` todo 0 (o pet não aprendeu nada): `E = 1` em todo P, com `andar` = 0 |
| **T-E4** | uma classe fora de `d_max` não entra em `A(P)`; no limite exato, entra |
| **T-E5** | o G-S0 numa semente dos testes: o log igual com e sem o coletor |
| **T-E6** | o G-S1: as rngs iguais antes e depois |

## 8. As decisões do Matheus

| id | pergunta | recomendação | custo de errar |
|---|---|---|---|
| **D-F5-2** | quais vidas: (a) os gabaritos dos testes, (b) uma run feita, ou as duas? | (a) primeiro; a (b) só se a (a) não for plana | (b) antes pode custar a conferência do replay de outro commit para nada |
| **D-F5-3** | o horizonte: até n = 2 consumos? | n = 2 (37 sequências) | n = 1 conta quase só o `CONT`; n = 3 sobe para 1 + 6 + 30 + 120 = 157 |
| **D-F5-4** | a mesma classe pode repetir na sequência? | não | com repetição, o `E` passa a medir quanto de cada classe cabe na faixa, não a variedade |
| **D-F5-5** | a faixa: os quartos de S do `_faixa` do M-MEM? | sim, reaproveitar | outra largura muda o `E`; a sonda mostra só uma |
| **D-F5-6** | o código só em `experiments/` e `tests/`, sem tocar no `digilab/`? | sim | se entrar no `digilab/`, vira mecânica e pede G-PAR |
| **D-F5-7** | os limiares da leitura (1/10 e 1/20) | aceitar como PROPOSTOS | um limiar frouxo mantém viva uma frente que devia acabar |
| **D-F5-8** | o plano de análise da run vai num `docs/PLANO_ANALISE_V3_SONDA_EMPOWERMENT.md` próprio, commitado antes do artefato, com a seção 5 desta espec? | sim | sem ele, o CI da categoria experimento reprova o PR da medida |

**Decisão (2026-11-17):** "Aprovo as recomendações". Valem as recomendações da tabela: (a) primeiro, n = 2, sem repetir classe, a
faixa do M-MEM, o código só em `experiments/` e `tests/`, os limiares 1/10 e 1/20 (PROPOSTOS, SEM FONTE) e o plano de análise próprio.

## 9. Fontes

As fontes estão em `docs/referencias/v3_f5_empowerment_referencias_verificadas.csv`. O Dreyfus (2002) vem da rodada Dreyfus do PR #954 e
não entra nesta tabela.
