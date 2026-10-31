# POC: órgãos digitais e genética (exploratória, isolada)

Status (2026-10-31): **POC para revisão.** Não integra o jogo, não é tarefa formal, não antecipa decisão da pesquisa principal. Todos
os números e relações fisiológicas aqui são **exemplos da POC, SEM FONTE**, e não se alegam biologicamente validados.

## Arquivos

| arquivo | o quê |
|---|---|
| `genoma.py` | 6 genes inteiros com faixa; `sortear`, `cruzar` (média por gene + mutação pequena) e o sha256 do genoma |
| `fisiologia.py` | o órgão digestivo (estômago → energia e fome) e o hormônio `saciedade`, em inteiros |
| `replay.py` | o log (origem, comer, tick), o replay com sha256 da trajetória, as entradas sintéticas e uma demonstração |
| `verificar_poc.py` | 18 verificações pequenas, fora da suíte principal |

```bash
python -m pytest poc/orgaos_genetica/verificar_poc.py -q
```

A demonstração (`cd poc` e depois `python -m orgaos_genetica.replay`) cruza dois genomas sorteados e refaz uma vida sintética de 141 ticks.

## 1. O que a POC demonstra

- **Órgão digestivo:** a comida entra no estômago, a digestão passa até `taxa_digestao` por tick, tira a mesma quantidade da fome e põe
  `conversao_pct` dela na energia; sem comida, a energia cai pelo `gasto_basal` e a fome sobe pelo `ganho_fome`. A conservação fecha
  (ingerido = estômago + digerido + descarte), e o que passa do teto é contado, não some.
- **Hormônio:** a digestão emite `saciedade`, que decai 1/`decaimento_saciedade` por tick; um receptor com ganho
  `sensibilidade_saciedade` corta parte do ganho de fome. Sensibilidade 0, 500 e 1000 dão fome final estritamente decrescente após a mesma
  refeição; com receptor 0 o hormônio não tem efeito.
- **Genes como parâmetros inatos:** os seis números do órgão e do hormônio vêm do genoma; trocar um gene muda o fenótipo (a taxa de
  digestão muda o estômago e a energia no mesmo tick). Gene fora da faixa, não inteiro ou desconhecido falha alto.
- **Cruzamento com mutação pequena:** média inteira por gene (empate para o par, sem float) e, com chance de 150/1000 por gene, um passo
  de mutação cortado na faixa, numa rng própria derivada da semente do cruzamento e dos sha256 dos pais. Mesma semente → mesmo filho;
  sem mutação → a média exata; cada mutação é registrada e limitada ao passo do gene.
- **O aprendido não se herda:** o `Genoma` só tem a tupla de genes; `cruzar` recusa qualquer outra coisa (`TypeError` com uma
  `Fisiologia` vivida); viver não muda o sha256 do genoma.
- **Replay determinístico:** o log refaz a vida tick a tick; o mesmo log dá a mesma trajetória e o mesmo sha256, também em outro processo
  com outro `PYTHONHASHSEED`, e bate com um gabarito gravado. A origem traz o cruzamento (pais, semente, chance), e o replay o refaz e
  confere o filho. Evento desconhecido, segunda origem, genoma adulterado ou filho trocado levantam erro.
- Três rngs separadas, como manda o projeto: `poc-genoma-ovo`, `poc-heranca`, `poc-entradas`.

## 2. O que a POC não demonstra

- Nada sobre comportamento ou aprendizado: não há cérebro, política, mundo nem dono; as refeições são sintéticas.
- Nada sobre herdabilidade (h²), variância genética útil, seleção ou evolução; não há população nem gerações.
- Nenhuma validade biológica, nem calibração: os números foram escolhidos para ter dinâmica visível. Na demonstração a energia **bate no
  teto** (descarte de 1 938), sinal de que os números não estão equilibrados.
- Não testa integração com o `Corpo` real (`digilab/corpo.py`), com o grafo validado do corpo (`corpo_grafo.py`), com o `Grupo` ou com a
  paridade Python × TypeScript.
- Não toca topologia nem estrutura do cérebro (fora do escopo por regra).

## 3. Dificuldades e decisões de arquitetura

- **Isolamento × reaproveitar:** a POC **não importa `digilab`**; copiei a `derivar_semente` (sha256 dos rótulos) para não criar
  dependência do pacote principal. O preço é duplicar uma função de 3 linhas.
- **Inteiros em tudo**, como o corpo de hoje, para o replay bit a bit. O decaimento do hormônio é `q // d` (com mínimo 1), não meia-vida
  exata: evita float. Por isso o gene se chama `decaimento_saciedade`, não meia-vida.
- **Ordem do tick declarada e fixa** (digestão → emissão → receptor → decaimento → gasto). Mudar a ordem muda a trajetória; numa tarefa
  formal, a ordem teria de entrar no grafo do corpo.
- **Arredondamento da média:** empate para o par, sem float; e o cruzamento sorteia sempre dois números por gene, para que o fluxo da
  rng não dependa de ter havido mutação (senão um gene mudaria o sorteio dos seguintes).
- **O filho no log** carrega os genomas dos pais por inteiro, não só os sha256: o replay refaz o cruzamento sozinho. No projeto, a
  origem da v1 guarda os sha256 dos logs dos pais; a escolha entre os dois é decisão de uma tarefa formal.
- **Escala própria** (`ESCALA = 10000`), não o C = 450000 do corpo, para não sugerir que os números são os do projeto.
- **Fora da suíte:** o arquivo de testes chama-se `verificar_poc.py` e fica em `poc/`; o CI roda só `tests/`, então nada disso é coletado.

## 4. O que poderia ser aproveitado numa tarefa formal

- O **padrão do cruzamento**: média inteira com empate para o par, consumo fixo da rng por gene e o registro das mutações (para a EG-4).
- O **evento de origem com o genoma e o sha256 conferidos no replay**, e o refazer do cruzamento no replay (para o G0).
- O **corte do receptor em milésimos** como forma de um hormônio alterar uma taxa em inteiros (candidato a um emissor/receptor do grafo
  do corpo, camada 2 da `fisiologia_especies.md`).
- As verificações de conservação e de "aprendido não entra no genoma" como modelo de teste.
- O que **não** aproveitar sem revisão: os seis genes e os números (exemplos), a escala e a ordem do tick.

## 5. Isolamento: o código principal e a pesquisa não foram afetados

- Worktree própria `D:\Trab\digilab\v3-poc-orgaos-genetica`, branch local `v3-poc-orgaos-genetica`, criada de `origin/main` (ea15189b).
  O commit só acrescenta `poc/orgaos_genetica/`; nenhum arquivo existente mudou (`git diff --stat origin/main`).
- Não mexi em `digilab/engine.py`, `digilab/digibrain/`, `digilab/corpo.py`, configurações, `web/`, `experiments/`, faixas de sementes
  nem experimentos registrados. Nenhum import do pacote `digilab`.
- Sementes só 1 a 9, locais desta POC, fora de `FAIXAS_RESERVADAS`. Nenhuma vida de pesquisa; a execução inteira leva ~1,5 s.
- Antes de começar não havia processo Python rodando na máquina (nenhuma run de pesquisa em andamento).
- Sem push, sem PR, sem merge.
