# RESULTADO V3 — CONVERSA_PET, F2: a espera da voz no jogo (2026-11-18, Gerente das cinco frentes, Claude Code, Opus 5.5)

**O plano:** `docs/PLANO_ANALISE_V3_CONVERSA_ESPERA.md`, APROVADO (D-ES-1 a D-ES-3, 2026-11-17). **O código:** o PR #963, na `main`.
**A leitura:** descritiva, sem gate. Nada aqui é sobre outra GPU, outro modelo, o jogador de verdade ou a fidelidade da fala (seção 5 do plano).

## 0. Em uma frase

Hoje o pet leva cerca de **12 s** para responder a cada frase com a voz local e cerca de **8 s** com o Claude Haiku. **Mais da metade da
espera do H, e mais de um terço da do G, não é a voz:** pelo caminho da rede, o servidor verifica a fala **antes** de devolvê-la, e o jogo
pede a mesma verificação de novo depois do balão.

## 1. As execuções

| pasta | braço | máquina | conta |
|---|---|---|---|
| `artifacts_v3_conversa_espera/G` | G, voz local `gemma2:9b` | livre (nenhuma run, a GPU com menos de 2,5 GB em uso por 10 min antes do início) | a medida |
| `artifacts_v3_conversa_espera/H` | H, voz `claude-haiku-5-5`, verificador local `gemma2:9b` | livre | a medida; gasto em `H/gasto_fala_livre.json` |
| `artifacts_v3_conversa_espera/G_conferencia_sob_carga` | G | carregada (desvio D-ES-D) | só conferência; não entra na leitura |

Cada pasta tem `turnos.jsonl`, `meta.json` (commit `d2c71463`, sha256 do build e do servidor, GPU, `ollama ps`) e `resumo.json`, que sai de
`python experiments/resumo_espera_f2.py --pasta <pasta>`. Os 120 turnos de cada braço saíram **sem nenhum erro**, todos pela voz da rede
(`rede` verdadeiro). A RTX 2060 tem 6 GB.

## 2. Os números (quente, n = 114; frio, n = 6; em segundos)

FATO VERIFICADO (os `resumo.json`):

| medida | G p50 | G p95 | H p50 | H p95 |
|---|---|---|---|---|
| **T1**, do envio ao balão (quente) | 11,88 | 13,39 | 7,97 | 10,68 |
| T1 acima de 8 s (quente) | 114 / 114 | | 56 / 114 | |
| **T1 frio** (a primeira conversa) | 9,99 | 28,40 | 6,98 | 28,66 |
| **T3**, do balão ao aviso (quente) | 4,09 | 4,32 | 4,58 | 5,99 |
| **T4**, a fila no jogo (quente) | 0,00 | 0,00 | 0,00 | 0,00 |

- **O T2 é igual ao T1:** a fala chega inteira, sem streaming (seção 0 do plano).
- **O T5:** uma espontânea disparada em cada braço, nenhuma descartada. O n é pequeno demais para ler.
- **O frio:** no H também é de 28 s, embora a voz não precise carregar nada. Quem carrega é o verificador local (seção 3).
- **A curva** de 2, 5, 8 e 15 s está nos `resumo.json`. No quente, nenhuma resposta do G passou de 15 s. No H, uma passou.
- **O modelo não coube na GPU:** no fim das duas execuções, o `ollama ps` mostra o `gemma2:9b` com 7,1 GB, 46 % na CPU e 54 % na GPU. É assim
  que o jogo roda hoje nesta máquina, e não um defeito da medida.
- **O custo do H:** US$ 0,0477 em 121 chamadas (as 120 conversas e a espontânea), dentro da estimativa de US$ 0,04 da D-ES-3.
- **A linha de base fora do jogo** (seção 0 do plano): a voz do G tem p50 de 6,4 a 7,3 s; aqui a geração do G deu 7,42 s (seção 3). O
  turno com o verificador, de 10 a 13 s fora do jogo, bate com o T1 do G.

## 3. Para onde vai a espera

FATO VERIFICADO (leitura do código na `main` `34894b50`):
- **Pelo caminho da rede, o servidor verifica antes de responder.** `_fala_conceitos` (`servidor/fala_livre.py:249-272`) gera a fala e
  chama `verificar_conceitos` dentro da mesma trava (`:261-268`), com a semente `semente + 7919`, e devolve a fala com a `verificacao`.
- **O jogo ignora essa verificação** e pede outra depois do balão (`web/app/src/falaLivre.ts:183`), com a semente `semente`. É essa a que
  o jogador vê, e é ela que o T3 mede.
- **O servidor atende uma chamada por vez** (`self.trava`). A verificação repetida de um turno ainda está em curso quando a frase seguinte
  sai (a pausa é de 3 s e o T3 é de 4 a 5 s), e a voz seguinte espera por ela no servidor. O T4 não vê isso, porque mede só a fila da
  página.
- **Isso corrige a seção 0 do plano,** que dizia que o verificador não segura a fala (desvio D-ES-C). Para o caminho de sempre, sem a rede,
  continua valendo. Para a voz da rede, que é a que o jogo usa com a `FALA_REDE`, não vale.

A divisão do T1 quente (`decomposicao_quente` nos `resumo.json`; a conta está na docstring de `decomposicao`):

| parte | G p50 | G p95 | H p50 | H p95 |
|---|---|---|---|---|
| a geração da voz (`latencia_s` do servidor) | 7,42 | 7,93 | 1,59 | 2,09 |
| a espera pela verificação repetida do turno anterior (trava) | 0,90 | 1,22 | 1,48 | 2,85 |
| o resto: a verificação dentro da chamada, mais o HTTP | 4,36 | 4,69 | 5,09 | 6,48 |

- A espera pela trava aparece em 59 dos 114 turnos do G e em 78 do H.
- **O que é conta e o que é medida:** a geração é medida pelo servidor. A trava e o resto são contas sobre os tempos da página. O registro
  não tem o tempo da verificação dentro da chamada. O resto bate com o T3 (4,09 e 4,58 s), que é a mesma verificação, com o mesmo modelo,
  e isso sustenta a leitura. Mesmo assim, ela é inferida, e não medida peça por peça.

NÃO CONFIRMADO: as duas verificações da mesma fala usam sementes diferentes e podem dar veredictos diferentes. A medida não grava o
veredicto de dentro da chamada, então não se sabe com que frequência isso acontece.

## 4. O que isso diz sobre as saídas (D-ES-4)

O levantamento da seção 6 do plano não tinha esta saída, porque partia de um fato que não vale para a rede.

**A saída nova, (0): o balão sai sem esperar a verificação.**
- Uma opção no pedido, só do jogo, faz o `_fala_conceitos` devolver a fala sem verificar. O jogo continua com a verificação de depois do
  balão, que já existe, e o aviso chega como chega hoje.
- O caminho da DC5 não muda, porque o orquestrador não manda a opção. A regra de não alterar a DC5c registrada continua de pé.
- **A estimativa** (PROPOSTO, SEM FONTE), tirando o resto da seção 3 e mantendo a trava: o T1 quente ficaria perto de **8 s no G** e
  **3 s no H**. É uma estimativa. Só a medida de novo diz.
- Ela também acaba com as duas verificações de sementes diferentes: fica uma só, a que o jogador já vê.

**D-ES-4, DECIDIDA pelo Matheus em 2026-11-18:** a pergunta foi "D-ES-4: do I take option (0), the balloon not waiting for the verification, first?", e a resposta, "Yes, option (0)" (no chat da Gerente das cinco frentes). A ordem abaixo fica como estava.

RECOMENDAÇÃO (D-ES-4):
1. **(0) primeiro,** atrás de uma chave e com a medida do G e do H de novo. Ela é barata, local, e não troca o modelo nem a fidelidade.
2. **A API em Ajustes,** depois da DC5d, se ela disser que o H é fiel. Com a (0), o H ficaria perto de 3 s.
3. **A pré-geração** para a espontânea e para a primeira fala da conversa, como no plano. Ela não resolve a resposta a uma frase do jogador.
4. **O streaming** por último.
5. **O modelo menor** fora. A geração do G já é 7,4 s com o modelo meio na CPU, e um modelo menor que caiba na GPU só seria avaliado com uma
   calibração e uma validação novas.

**O custo de errar na (0):** pequeno. O aviso já chega depois do balão hoje. O risco é a opção vazar para o caminho da DC5. Por isso o código
dela teria de vir com um teste do servidor que confira que, sem a opção, a resposta sai igual à de hoje.

## 5. O que fica de fora

- O jogador de verdade, outra pausa, outro roteiro, outra GPU: o roteiro é o da calibração da DC5 e a pausa é fixa em 3 s.
- A fidelidade da fala do H no jogo: isso é da DC5d.
- O T5 com n útil: só uma espontânea por braço.

## 6. Adendo: a medida de novo com a saída (0) ligada (2026-11-18)

**O código:** o commit `c2230891` (o pedido com `verificar_na_chamada: false` atrás da chave `-fala-verif-depois`, desligada por
padrão). **A medida:** a mesma da seção 1, com `MEDIR_ESPERA_VERIF_DEPOIS=1`, na máquina livre (nenhuma run e a GPU abaixo de 2,5 GB por
10 min antes de cada braço), em `artifacts_v3_conversa_espera/G_verif_depois` e `H_verif_depois`. Os 120 turnos de cada braço saíram sem
erro, todos pela rede.

FATO VERIFICADO (os `resumo.json`; quente, n = 114; em segundos):

| medida | G antes | G com (0) | H antes | H com (0) |
|---|---|---|---|---|
| **T1 p50** | 11,88 | **8,60** | 7,97 | **2,93** |
| T1 p95 | 13,39 | 9,17 | 10,68 | 4,44 |
| T1 acima de 8 s | 114 / 114 | 69 / 114 | 56 / 114 | 0 / 114 |
| T1 frio p50 / p95 | 9,99 / 28,40 | 6,96 / 24,02 | 6,98 / 28,66 | 2,68 / 22,72 |
| T3 p50 (o aviso depois do balão) | 4,09 | 4,30 | 4,58 | 4,65 |
| a geração (p50) | 7,42 | 7,43 | 1,59 | 1,45 |
| a trava (p50; turnos com ela) | 0,90 (59) | 1,22 (96) | 1,48 (78) | 1,56 (112) |
| o resto (p50) | 4,36 | 0,00 | 5,09 | 0,00 |

- **O resto foi a zero nos dois braços.** Isso confirma a leitura da seção 3: o resto era a verificação dentro da chamada.
- **A estimativa da seção 4** (perto de 8 s no G e de 3 s no H) bateu: 8,60 e 2,93.
- **O que sobra além da voz é a trava:** a verificação de depois do balão, agora a única, ainda está em curso quando a frase seguinte sai,
  porque a pausa do roteiro é de 3 s e o T3 é de 4,3 a 4,7 s. Ela aparece em mais turnos que antes (96 e 112 de 114) porque a frase
  seguinte sai mais cedo. É um efeito da pausa fixa do roteiro: um jogador que leva mais de 4 s para escrever não a encontraria. Isto é
  uma inferência, e não foi medido com outra pausa.
- **O frio** continua alto no p95 (24 e 23 s). No G, o primeiro turno esperou 14,2 s na fila da página (o T4 frio), atrás da espontânea
  do começo, que levou 14,8 s com o modelo frio. O frio tem n = 6 e não dá para ler mais que isso.
- **O aviso não mudou:** o T3 ficou onde estava, como esperado, porque a verificação de depois do balão é a mesma.
- **O custo do H com (0):** US$ 0,0476 em 121 chamadas (o acumulado de US$ 0,0953 no `H_verif_depois/gasto_fala_livre_acumulado.json`,
  menos os US$ 0,0477 da seção 2).

**D-ES-5, DECIDIDA pelo Matheus em 2026-11-19:** a pergunta foi "D-ES-5: a chave da opção (0) passa a vir ligada de fábrica?", e a
resposta, "Sim, ligar" (no chat da Gerente das cinco frentes). A chave agora vem ligada; `"0"` em `-fala-verif-depois` desliga. A
medida desta seção foi feita antes, com a chave ligada à mão, e o código não mudou além do padrão.

A pergunta, como foi levada: se a chave passa a vir ligada de fábrica. Hoje não há botão em Ajustes; ela só liga pelo
`localStorage`.
- RECOMENDAÇÃO: ligar de fábrica no caminho da rede. O ganho é de 3,3 s no G e de 5,0 s no H, e o aviso chega como antes.
- O custo de errar: pequeno. O balão sai antes de a fala ser verificada, como já acontece fora da rede. O que se perde é só a
  verificação de dentro da chamada, que o jogo ignorava. A DC5 não muda, porque o orquestrador não manda o campo.
