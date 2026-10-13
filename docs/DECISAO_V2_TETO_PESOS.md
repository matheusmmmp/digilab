# Decisão — V2: o teto de pesos do cérebro A (2026-10-12)

Status: **DECIDIDA** pelo Matheus em 2026-10-12, TP-1 e TP-2 pela recomendação (seção 5): o teto por plano, com o limite de 2000. Pedido do
Gerente ao worker C, só papel; a implementação é a seção "V2, TETO-POR-PLANO" do `CLAUDE.md`.

## 1. O problema

**O teto.** O cérebro A recusa nascer com 1000 pesos ou mais (`ConfigLobos.maximo_pesos` = 1000, PROPOSTO).
- **A fonte declarada:** "PLANO_V2_PESQUISA, fase 1b: abaixo de mil pesos, para o replay" (`digilab/policies/lobos.py`, linha 128). Na
  origem, era uma decisão de desenho da L0 (`docs/TAREFA_V2_L0_LOBOS.md`, linha 26: "< 1000 pesos").
- **O que nunca foi medido:** o custo do replay em função do número de pesos. O "para o replay" é **SEM FONTE**: um motivo, não um
  número.
- **Os cérebros B e C** copiam o mesmo teto ("o teto do plano da V2, como o A"). A rede de si (o Digicorpo) tem um teto próprio de 1000
  (`ConfigRedeDeSi`), fora desta decisão.

**Onde o A está hoje.** A conta foi feita com o código da `main` `930037b`, com o teto aberto só para contar (`n_pesos()`). Os três
números com teste citam o teste; os outros saem do comando da seção 6, sem artefato:

| cérebro | pesos | conferido em |
|---|---|---|
| o da V2 validada (as frutas, o ponto da K2, a montagem completa) | 763 | a validação única e a comparação A × C (`docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, contrato 1.3) |
| o mundo físico, sem extras | 756 | a conta |
| o mundo físico com o corpo (os drives novos e os gestos) | 882 | a conta |
| o mundo físico com o corpo e o banheiro | **998** | `tests/test_banheiro_cerebros.py`, linha 198 |
| os dois pets, degrau 1 (o alvo aprendido, as entradas sociais, o modelo dos outros, a presença da fruta) | **990** | `tests/test_canal_fruta_mundo.py`, linha 61 |
| os dois pets com o corpo | **1116** | a conta: **passa do teto** |
| os dois pets com o corpo e o banheiro | **1277** | a conta: **passa do teto** |

**O que o teto já custou ou vai custar:**
- **o banheiro** teve de pôr o `aliviar` só nas regras em que é candidato. Uma regra nova do instinto (a da ida que continua) não coube
  (REGISTRO, banheiro);
- **o metabolismo** saiu sem receptor (ME-2);
- **os próximos que não cabem:**
  - cada receptor novo nas entradas do corpo custa 24 pesos, e o nariz (DP-13, duas narinas) e o ouvido (DP-14) são receptores;
  - o degrau 3 dos dois pets junta o corpo e o social (1116 a 1277).

## 2. O que o teto toca, e o que não toca

- **As vidas: nada.** O teto só faz o cérebro falhar alto na construção. Nenhuma conta da vida o lê, então mudá-lo não muda nenhum log,
  estado, rng ou peso.
- **O G2: nada,** pelo mesmo motivo. Os gabaritos guardam o sha256 das vidas, não o teto.
- **O `meta.json` das runs: sim.** Ele grava a `ConfigLobos` inteira, e o teto vai junto (por exemplo, os `meta.json` dos blocos de
  `artifacts_v2_validacao_unica/`). Uma run antiga refeita com outro teto padrão grava outro número no meta, com as mesmas vidas.
- **A V2 validada: nada.** O cérebro dela tem 763 pesos. O contrato de capacidade da comparação A × C (B e C entre 0,9× e 1,1× da
  capacidade do A no ponto da K2) é sobre 763, e não sobre o teto.

## 3. As opções

| opção | o que faz | o G2 | a comparação com a V2 validada | custo |
|---|---|---|---|---|
| **(a) subir o teto padrão** (para 1500 ou 2000) em todos os cérebros | o campo muda no `config.py` | intacto | intacta; os `meta.json` de runs refeitas mudam o número do teto | uma linha e o registro. Mexe num número que vale para todo cérebro, inclusive os que não precisam |
| **(b) teto por plano** | o padrão fica 1000; o plano que precisa de mais declara o teto dele na config (`"lobos": {"maximo_pesos": N}`), com o motivo e o número de pesos | intacto | intacta, inclusive os `meta.json` | o campo já existe. Cada plano novo que passa de 1000 escreve o seu teto e justifica |
| **(c) cortar ou compartilhar entradas** | por exemplo, as entradas do corpo com um peso por (ação, receptor) nas três regras de tempo livre, e não por (regra, ação, receptor): 192 → 64, e o cérebro com o corpo e o banheiro cai de 998 para 870 | **quebra** para os braços com o corpo e o social: o cérebro muda, e os gabaritos desses braços são regravados | intacta (o cérebro das frutas não muda); muda o cérebro dos planos do corpo e dos dois pets antes da validação deles | um PR de código do B, com testes novos e um adendo em cada plano. O cérebro aprende uma função diferente (as regras de tempo livre passam a dividir o que aprendem do corpo) |
| **(d) um cérebro por regime** | classes ou configs separadas (o A do mundo, o A do corpo, o A social), cada uma com o seu teto | intacto | intacta | a refatoração não traz nada que a (b) não traga |
| **(e) manter 1000 e recusar o que passa** | nada muda | intacto | intacta | bloqueia o nariz e o ouvido com o corpo, o degrau 3 dos dois pets e qualquer receptor novo. Empurra mais desenhos para "sem receptor" |

## 4. A recomendação

**(b) o teto por plano, com um limite de 2000 (PROPOSTO, SEM FONTE).**
- **O padrão fica 1000.** Nada do que existe muda, nem os `meta.json`.
- **O plano que precisar de mais** declara na config o teto e o número de pesos do cérebro dele, e escreve no texto por quê.
- **O limite de 2000** cabe o maior caso contado hoje (1277), com folga para o nariz, o ouvido e os sons do degrau 1b. Passar de 2000 pede
  decisão nova.
- **Antes do primeiro plano acima de 1000,** o PR que o fizer mede o custo do replay com o cérebro maior: o tempo de CPU por vida e o
  tamanho do estado interno, contra o mesmo braço com 1000 ou menos. Hoje há só a referência de custo da calibração do mundo (#278: 3,9 a
  7,9 s de CPU por vida), que não separa o efeito dos pesos.
- **Os cérebros B e C** seguem com 1000. Eles só voltam numa comparação nova, que traria o contrato de capacidade dela.

## 5. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| TP-1 | O que fazer com o teto | **(b) teto por plano**: o padrão fica 1000, e o plano que precisar declara o seu | **(a):** muda um número de todos os cérebros sem necessidade e os `meta.json` de runs refeitas. **(c):** muda o cérebro do corpo e dos dois pets antes da validação deles, regrava gabaritos e reduz o que o pet aprende. **(e):** bloqueia o nariz, o ouvido e o degrau 3 |
| TP-2 | O limite de um teto por plano | **2000**, com a medida do custo do replay no primeiro plano que passar de 1000 | **1500:** cabe o 1277 de hoje, mas não o degrau 3 com o nariz e o ouvido. **Sem limite:** o cérebro cresce sem que ninguém olhe o custo. **Sem a medida do custo:** o motivo "para o replay" segue sem número |

## 6. A conta, para refazer

Com o código da `main` `930037b`, na raiz do repositório:

```python
from dataclasses import replace
from digilab.config import (CONFIG_PADRAO, CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA as CM,
                            CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_BANHEIRO_LIGADA as CB)
from digilab.policies.lobos import PoliticaLobos
n = lambda cl, **kw: PoliticaLobos(CONFIG_PADRAO, replace(cl, maximo_pesos=2000), **kw).n_pesos()   # 2000: o limite (TP-2)
d1 = replace(CONFIG_LOBOS_APRENDIZ, alvo_aprendido=True, entradas_sociais=True, modelo_outros=True, presenca_fruta_mundo=True)
n(CONFIG_LOBOS, cfg_mundo=CM)                                                          # 756
n(CONFIG_LOBOS, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_DRIVES)                           # 882
n(CONFIG_LOBOS, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_BANHEIRO, cfg_banheiro=CB)        # 998
n(d1, cfg_mundo=CM)                                                                    # 990
n(d1, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_DRIVES)                                     # 1116
n(d1, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_BANHEIRO, cfg_banheiro=CB)                  # 1277
```
