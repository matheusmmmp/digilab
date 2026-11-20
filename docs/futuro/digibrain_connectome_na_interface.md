# O DigiBrain e o connectome na interface nova: o plano

Status (2026-10-18): **PROPOSTO, só papel.** O pedido veio do Matheus em 2026-10-18, durante a TAREFA_V2_UI_DESKTOP: visualizar a rede do
cérebro através de um connectome. A referência é o quadro "DigiBrain" que ele mandou: o mapa colorido, as barras por lobo, o "ao vivo" e
o "Estado atual". Este documento não autoriza código: depende das decisões da seção 5.

Ele junta duas frentes que já existem, sem repetir o que elas decidem:
- **o connectome:** o desenho e o protótipo estão em `docs/futuro/connectome_cerebro_a.md` (worktree `v2-connectome-cerebro-a`, ainda
  fora da `main`), com as decisões CN-1 a CN-9;
- **o painel DigiBrain:** é a etapa 5 do porte do cérebro A (`docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seção 4), só nos pets v11 (PW-7), com
  as decisões PW-3 a PW-8.

## 1. O que a tela mostra, e de onde cada coisa vem

Tudo sai do motor por `useJogo()`. A fonte é a mesma do protótipo: os pesos da `PoliticaLobos` e o `motivo` de cada decisão
(`estado_interno()["motivos"]`).

| na referência | na interface | a fonte | observação |
|---|---|---|---|
| o mapa colorido | o **mini-connectome**: o grafo do cérebro A em miniatura (as quatro colunas, os lobos como regiões) com as arestas da última decisão acesas | os pesos `w`, `w0` e o motivo da decisão | é o grafo dos pesos, não uma rede de neurônios (connectome, seção 1) |
| Percepção (barra) | **as 2 ou 3 entradas que mais pesaram** na ação escolhida ("fome alta", "tédio") | a percepção `x` e `w·x/S` | **não é barra** (PW-5): a percepção não soma no peso efetivo |
| Memória, Emoção | **uma barra, a do lobo memória/emoção**, e a emoção de hoje como selo à parte, com a fonte | `memoria_emocao` no motivo; a emoção da memória do pet | duas barras seriam uma inventada (PW-6) |
| Impulsos, Decisão | **a contribuição de cada lobo na ação escolhida**, em barras com sinal; a soma é o peso efetivo | `impulsos`, `decisao`, `memoria_emocao`, `planejamento`, `piso` do motivo | é o `_pesos_efetivos`; o lobo decisivo fica destacado |
| ao vivo | o ponto acende quando o relógio do jogo anda | o tempo do app | parado (pausa, luta, Resultado): "pausado" |
| Estado atual | **o que ele faz agora** (o `hab-agora` do habitat) | `m.acao` | já está na interface nova |

## 2. Onde fica na interface nova

- **No Pet (desktop):** o cartão **DigiBrain** entra na coluna da direita, acima de "Atividades recentes". Ele tem o mini-connectome, a
  lista da percepção e as barras dos lobos. A coluna já rola sozinha (`.lado-cards`), então o habitat não encolhe. **No celular:** uma gaveta
  aberta por um botão no palco (as pranchas da etapa 5 do porte).
- **A tela inteira do connectome:** uma aba **DigiBrain** no Diário, junto do Registro, porque as duas leem o mesmo log. Ela tem:
  - o grafo do protótipo em tamanho grande;
  - o tocador da vida (anterior, tocar, próxima, cursor), com os pesos acompanhando o cursor, para ver o aprendizado engrossar e mudar de cor;
  - a faixa da vida com o lobo decisivo de cada decisão;
  - o painel lateral com as dez arestas mais acesas.

  Clicar no mini-connectome do Pet abre essa aba na decisão de agora.
- **O aviso fixo do connectome** fica no topo da aba: o que o grafo é, o tamanho dele ao lado da mosca e "não é um cérebro biológico".

## 3. Como o jogo calcula o grafo (sem estado salvo)

O save continua só o log. A aba rejoga o log no motor TS e grava os pesos antes de cada decisão, como o protótipo faz no Python. A
gravação só lê: não consome rng nem muda estado. Isso pede:
1. **o cérebro A em TS com paridade** (o porte, etapas 2 a 4): o motivo e os pesos têm de sair iguais aos do Python;
2. **uma leitura pública dos pesos no cérebro A** (CN-5): a web não deve ler os privados;
3. **um teste de paridade do grafo**: para uma vida de teste (101…505), o `dados.json` do protótipo e o grafo da web têm de bater, peso a
   peso e decisão a decisão.

O tamanho cabe: a vida do J5 de exemplo tem 54 nós, 831 posições de peso e 960 decisões em 10 dias (connectome, seção 5).

## 4. A ordem

| passo | o quê | depende de |
|---|---|---|
| 1 | entra na `main` o desenho e o protótipo do connectome (a worktree `v2-connectome-cerebro-a`), como ferramenta de pesquisa | CN-1, CN-7 |
| 2 | o porte do cérebro A chega ao pet v11 (etapas 2 a 4) | PW-3, PW-4 |
| 3 | as pranchas do cartão DigiBrain e da aba, no visual limpo da TAREFA_V2_UI_DESKTOP | este plano aprovado |
| 4 | o cartão DigiBrain no Pet (a etapa 5 do porte, com este desenho) | passos 2 e 3, PW-5, PW-6 |
| 5 | a aba DigiBrain no Diário, com o tocador e o teste de paridade do grafo | passo 4, CN-5 |
| 6 | opcional: a camada do corpo químico numa aba à parte (CN-6) | passo 5 |

## 5. Decisões para o Matheus

Cada uma vem com a recomendação e o custo de errar.

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **DC-1** | O connectome vai ao jogo (é a CN-1, agora com o pedido de hoje). | Sim, mas só depois do porte (passo 2): antes disso a web não tem o cérebro A para desenhar. | Fazer antes desenha o bandit com os nomes dos lobos, outro cérebro na mesma tela (PW-7). |
| **DC-2** | A percepção como barra (a referência) ou como lista (PW-5). | Lista. | Uma barra de percepção não corresponde a conta nenhuma do cérebro: seria um número inventado na tela. |
| **DC-3** | Onde mora a tela inteira: aba no Diário ou destino novo "Laboratório" no menu. | Aba no Diário. | Um destino novo muda a navegação do celular e das rotas; a aba usa o que existe. |
| **DC-4** | O nome na tela: "DigiBrain" no cartão e "connectome" na aba (CN-9). | "DigiBrain" no cartão; "como connectome" na aba, com o aviso fixo. | Sem o aviso, alguém lê o grafo como cérebro biológico. |
| **DC-5** | O cartão DigiBrain nos pets v1 a v10. | Não (é a PW-7): ali o cartão não aparece. | Mostrar o bandit como se fosse o A. |
