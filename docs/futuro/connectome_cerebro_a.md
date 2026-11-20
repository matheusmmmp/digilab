# O cérebro A como connectome: o desenho

Status (2026-10-18): **as decisões CN-1 a CN-9 estão DECIDIDAS pelo Matheus, todas pela recomendação** (seção 9). Continua só papel e um
protótipo fora do pacote: pela CN-1, o connectome é ferramenta de pesquisa até o J5, e nada vai ao jogo web nem ao `digilab/`. O porte do
cérebro A para a web saiu da pausa em 2026-10-17 (`docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, #320), sem o connectome.

**O pedido:** o Matheus perguntou se dá para visualizar a rede do cérebro A como o connectome do FlyWire. Dá, como **grafo dos pesos e dos
motivos de cada decisão**. O que se desenha é uma tabela de pesos, não uma rede de neurônios, e a tela diz isso.

**Regras deste desenho:**
- nenhum número novo de mecânica; os números de vida citados saem dos arquivos de contagem que o protótipo grava (seção 6);
- nenhuma alegação de novidade e nenhuma correspondência com a mosca (`docs/research/digibrain/sources/drosophila.md`, "O que não
  mostra"): a imagem do FlyWire é só a referência visual;
- nada aqui muda `engine.py`, a `PoliticaLobos` ou o jogo web.

## 1. O que é e o que não é

| | o connectome do FlyWire | o grafo do cérebro A |
|---|---|---|
| o nó | um neurônio reconstruído do tecido | uma entrada da percepção, uma regra do instinto, uma ação, uma classe de alvo |
| a aresta | uma sinapse observada | um peso inteiro `w` de uma tabela, iniciado no prior do instinto |
| o tamanho | cerca de 139 mil neurônios e 54,5 milhões de sinapses (Dorkenwald et al. 2024, `10.1038/s41586-024-07558-y`, CORPUS) | 54 nós e 831 posições de peso, 203 não nulas no fim da vida de exemplo (seção 6) |
| a dinâmica | não está no mapa (conectoma ≠ dinâmica ≠ comportamento) | está no código: a ativação linear Σ (w/S)·x e um sorteio proporcional |

São seis ordens de grandeza de distância nas arestas. O grafo do A é pequeno o bastante para ler peso por peso, e é isso que ele oferece
de útil: ver **de onde veio cada decisão**, não a forma de um cérebro.

## 2. O grafo

### 2.1 Os nós

Quatro grupos, nas colunas da esquerda para a direita (a mesma ordem do fluxo da decisão em `lobos.py`):

1. **As entradas da percepção** (`PoliticaLobos.entradas` e as tabelas vizinhas):
   - o viés e o estado: `vies`, `sujeira`, `dormindo`, `hora`, `ticks_sem_cuidado`;
   - os **receptores de hoje**: `fome`, `higiene`, `energia`, `humor`, `saude`. Com o corpo químico ligado, são a leitura dos receptores
     dele (`RECEPTORES_HOJE`), na ordem do `Estado.vetor`;
   - o mundo: `bola` e `fruta` (as entradas do mundo físico, `ENTRADAS_MUNDO`);
   - a **presença da fruta** (`fruta a/b/c à vista`, a FRUTA-NO-CENARIO no mundo físico, `presenca_no_mundo`);
   - as **entradas sociais**, com os dois pets (`ENTRADAS_SOCIAIS`: `outro_a_vista`, `viu_comer`, a ação visível do outro, o toque);
   - os **receptores novos do corpo** (`RECEPTORES_NOVOS`: tédio, curiosidade, solidão, estresse, dor, susto, vontade, conforto), só com os
     drives novos ligados. Nenhuma das duas vidas de exemplo os tem; o protótipo já os desenha quando existirem.
2. **As regras do lobo impulsos** (`REGRAS` e `REGRAS_MUNDO`): as nove que o instinto testa, de `sono_exaustao` a `fruta_no_cenario`.
3. **As ações candidatas** (`AcaoPet`): as sete de sempre; o `aliviar` entra só com o banheiro.
4. **As classes de alvo** (`CLASSES_ALVO`, `CLASSES_COMER_PALADAR` e as `arvore:<id>` do pet que pensa): onde a ação vai no mapa.

Mais dois nós que **não são pesos**: o lobo memória/emoção e, com `g_plano > 0`, o lobo planejamento (os modelos do mundo). Eles só
aparecem como ligações tracejadas na atividade de cada decisão (seção 3).

### 2.2 As arestas

Cada aresta é **um peso**, e o grafo tem uma aresta por posição de peso do cérebro (`n_pesos()`):

| tipo | a tabela em `lobos.py` | o desenho |
|---|---|---|
| `t` | `w[regra][acao][entrada]`, a tabela do lobo decisão | entrada → regra → ação |
| `s` | `_pesos_social[regra][acao][entrada social]` | entrada social → regra → ação |
| `c` | `_pesos_corpo[regra][acao][receptor novo]` | receptor novo → regra → ação |
| `m` | `_pesos_alvo_mundo["regra:acao"][classe]`, o alvo aprendido | ação → classe (uma curva por regra) |
| `f` | `_pesos_comer_fruta[fruta]`, a presença da fruta em comer | fruta à vista → comer |

**O peso tem três índices, e o desenho não esconde isso:** a curva de `w[regra][acao][entrada]` sai da entrada, **passa pelo nó da regra**
e chega na ação. Assim o mesmo par (entrada, ação) aparece uma vez por regra, como é no código, e o feixe que passa por uma regra é a
tabela dela. Somar as regras numa aresta só (entrada → ação) daria um grafo mais limpo e falso: o cérebro nunca soma duas regras (CN-2).

**A codificação:**
- a **espessura** é √|w|/S (a raiz deixa ver os pesos pequenos ao lado do `vies` do prior);
- a **cor** separa o prior do aprendido: cinza onde `w = w0` (o prior do instinto), vermelho onde `w > w0` e azul onde `w < w0`, mais forte
  quanto mais perto do `teto`;
- **tracejado** é peso negativo;
- um seletor mostra o peso inteiro (`w`), só o aprendido (`w − w0`) ou só o prior (`w0`).

### 2.3 As regiões

Os lobos (`LOBOS_TODOS`) são as regiões coloridas, como as neurópilas nas imagens do FlyWire: **percepção** (as entradas), **impulsos**
(as regras), **memória/emoção**, **planejamento** (só com `g_plano > 0`) e **decisão** (as ações e as classes de alvo, porque os pesos do
alvo aprendido também são do lobo decisão). As cores das regiões passaram no validador de paleta da skill de visualização (pares vizinhos,
nos dois temas; no escuro, com um aviso de separação para daltonismo que o rótulo escrito em cada região cobre).

## 3. A atividade ao vivo

A fonte é `estado_interno()["motivos"]`: um registro por decisão, com a regra que disparou, os candidatos, a percepção `x`, a contribuição
de cada lobo por candidato (`impulsos`, `decisao`, `memoria_emocao`, `planejamento`, `piso`), o peso efetivo, o `u` do sorteio, a ação, o
lobo decisivo e, no mundo físico, o alvo aprendido e o plano.

A cada decisão a rede acende:
- o nó da regra que disparou, os candidatos e a ação escolhida;
- **as arestas pelo termo de cada uma**, `w·x/S`, nos candidatos da regra (a ação escolhida mais forte; o termo negativo em azul);
- a classe de alvo escolhida, com os pesos das classes que o motor ofereceu;
- a presença da fruta em comer;
- as ligações tracejadas da memória/emoção e do plano, com a contribuição deles no motivo;
- as entradas pelo valor de `x`.

O painel do lado mostra a contribuição de cada lobo por candidato em barras empilhadas com sinal (a soma é o peso efetivo, como no
`_pesos_efetivos`) e as dez arestas mais acesas. Abaixo do grafo fica o **tocador** (anterior, tocar, próxima, velocidade, cursor). Há
também uma faixa da vida inteira com o lobo decisivo de cada decisão, com as viradas do dia marcadas. **Os pesos estáticos acompanham o
cursor:** o grafo mostra os pesos do momento da decisão, então tocar a vida mostra o aprendizado engrossando e mudando de cor.

**O que a vida de exemplo já mostra** (os `dados.json` que o protótipo grava, seção 6): na vida do J5, o lobo decisivo é o impulsos em 913
das 960 decisões e o decisão em 47. A memória/emoção contribui 0 em toda decisão, como o `MemoriaEmocao.contribuicao` diz. O plano mudou
a ação em 7 decisões e o alvo em 16, e nenhuma delas tem o planejamento como o maior termo da ação escolhida. É um retrato do cérebro A
de hoje: o prior do instinto pesa mais que o aprendido.

## 4. Opcional: a segunda camada, o corpo químico

O corpo já tem o próprio grafo: `corpo_grafo.Grafo`, montado por `corpo.grafo_do_corpo`, com químicos, reações, emissores (os estímulos e
os gatilhos), leituras e órgãos. Na vida do J5 de exemplo ele tem:

| peça | quantas |
|---|---|
| químicos | 17 |
| químicos com receptor | 9 (os cinco de hoje e os quatro do paladar) |
| reações | 3 |
| emissores | 32 |
| arestas emissor → químico | 45 |
| arestas de leitura (químico → emissor) | 8 |
| arestas das reações (consumo e produção) | 7 |

A ponte entre as duas camadas são os receptores. Cinco deles são entradas da percepção (os nós `receptor` da seção 2.1). Os quatro do
paladar **não são entradas**: entram só no sinal da consequência, pelo canal `gosto`. Desenhar a camada é empilhar um segundo grafo
abaixo do primeiro, com os receptores ligados às entradas de mesmo nome e os do paladar ligados ao sinal. O protótipo só conta essa
camada; desenhá-la é a CN-6.

## 5. O tamanho real do grafo

As contagens são das duas vidas de exemplo (seção 6). "Posições de peso" é o `n_pesos()` do cérebro, e cada uma é uma aresta possível.

| | J5 (`P1-plan~T1@101`, pet A, 10 dias) | dois pets (`B+Ainf`, K = 2, pet B, 4 dias) |
|---|---|---|
| nós | 54 (15 entradas, 9 regras, 7 ações, 21 classes, 2 lobos) | 56 (30 entradas, 15 delas sociais; 9 regras, 7 ações, 9 classes, 1 lobo) |
| posições de peso | 831 (756 `t`, 72 `m`, 3 `f`) | 990 (756 `t`, 195 `s`, 36 `m`, 3 `f`) |
| não nulas no prior | 102 | 66 |
| não nulas no fim | **203** | **237** |
| não nulas em algum momento | 204 | 240 |
| aprendidas no fim (`w ≠ w0`) | 138 | 203 |
| arestas `t` acesas em alguma decisão | 122 | 115 |
| decisões | 960 | 384 |

As 30 não nulas do prior na tabela `t` são as que estão em `PRIOR_INSTINTO` e no prior do mundo (a bola e a fruta). As outras 72 do J5 são
os pesos iniciais das classes de alvo. **A tabela `t` é quase toda zero:** das 756 posições, 130 estão vivas no fim. Os candidatos de cada
regra são poucos, e as regras deterministas (sono, pedido, abandono) não aprendem, porque `1[a = a*] − p(a) = 0` com um candidato só.

## 6. O protótipo

`tools/connectome_cerebro_a.py`, fora do pacote `digilab/`, só a biblioteca padrão. O modelo da página é `tools/connectome_cerebro_a.html`,
com o d3 7.9.0 do cdnjs na versão fixa.

```bash
python tools/connectome_cerebro_a.py --vida pqp --semente 101          # a vida do J5
python tools/connectome_cerebro_a.py --vida dois_pets --semente 101    # o pet B, com o A informativo
```

A saída padrão é `artifacts_connectome/<vida>-<semente>/`, ignorada pelo git: o `log.jsonl` (ou o `registro.jsonl` do grupo), o
`dados.json`, o `contagem.json` e o `connectome.html`. As duas páginas de exemplo, as contagens e as capturas estão em
`docs/futuro/connectome_cerebro_a/`.

**Como ele lê a vida:**
1. **A semente.** Ele só aceita 101, 202, 303, 404 e 505, e confere na tabela das faixas que é a dos testes. As faixas de pesquisa são
   recusadas.
2. **A vida.** Ela é vivida pela bancada (`BancadaPQP.vida`, ou `Bancada.grupo`), que já confere o replay (G1):
   - a do J5 usa a config de fumaça do paladar com os números calibrados do adendo 3 (`ganho_gosto` S/2 e `g_plano` S,
     `docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR.md`), o braço `P1-plan` e o T1 com D_a = 7 e janela 3;
   - a dos dois pets usa a config da calibração dos dois pets sem as unidades de pesquisa, com o braço `B+Ainf`, K = 2 e 4 dias.
3. **O log vai para o disco e é rejogado do texto do disco.** Durante o replay, um gravador embrulha `PoliticaLobos.agir` e lê os pesos
   antes de cada decisão; ele não consome rng nem muda estado. A vida rejogada é conferida contra a vida, bit a bit (`resumo_motor` e o
   estado interno, ou `_resumo_grupo`).
4. **As conferências falham alto:**
   - o termo aprendido de cada motivo tem de ser exatamente `(w − w0)/S · x` com os pesos gravados;
   - os pesos achatados no fim têm de ser os do `estado_interno()`;
   - uma tabela que o protótipo não desenha (a sub-decisão da fruta, a informação, o pedido, o alvo do banheiro, a memória N6) levanta
     erro em vez de sumir do grafo.

**O que ele lê de privado:** os atributos `_pesos*` e `_prior*` da `PoliticaLobos`, porque o `estado_interno()` público não traz a tabela
das entradas sociais com o prior nem a presença da fruta na decisão. Para um protótipo serve. Uma ferramenta permanente pede um método
público de leitura no cérebro (CN-5).

`tests/test_connectome_cerebro_a.py` confere três coisas: a recusa das sementes de pesquisa, a página das duas vidas e o fecho das
contagens.

## 7. O que fica fora

- **O jogo web.** Nada aqui vai à web; o porte do A está pausado até o J5 (CN-1).
- **As tabelas não desenhadas** (seção 6, item 4) falham alto. Elas não estão nas vidas do J5 nem dos dois pets.
- **O layout é fixo por colunas,** sem força nem física. Com 30 entradas (os dois pets) a coluna da percepção fica cheia; acima de umas
  50 entradas, pediria rolagem ou agrupamento.
- **A atividade dos lobos que não são pesos** (memória/emoção, plano) é a contribuição do motivo. O modelo do mundo do plano não vira grafo.
- **O canal do crédito** (corpo, fruta, gosto) não colore a aresta: o motivo guarda o sinal, não por qual canal cada peso mudou (CN-4).

## 8. Riscos

- **Ler o grafo como cérebro.** A imagem lembra um connectome, e isso convida a ler mais do que ela diz. O aviso fixo no topo da página
  (o que é, o tamanho, a distância da mosca) é a mitigação; a CN-9 pergunta se o nome deve mudar.
- **O privado mudar.** Se `lobos.py` renomear um atributo, o protótipo quebra alto (as conferências), não em silêncio.
- **O tamanho do HTML.** A vida do J5 dá cerca de 1 MB, quase tudo das 960 decisões. Vidas de 30 dias passariam de 3 MB.

## 9. Decisões para o Matheus

**DECIDIDAS em 2026-10-18: CN-1 a CN-9, todas como recomendado** (a coluna da recomendação é o que vale).

Cada uma vem com a recomendação e o custo de errar.

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **CN-1** | Onde o connectome vive: só como ferramenta de pesquisa (Python + HTML estático) ou também no jogo web. | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** Só ferramenta de pesquisa até o J5; a web espera o porte do A. | Baixo se esperar (a ferramenta segue igual). Ir à web agora duplica o trabalho do porte e arrisca a paridade. |
| **CN-2** | A aresta de três índices passa pela regra (entrada → regra → ação) ou soma as regras (entrada → ação). | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** Pela regra, como está. | Somar dá um grafo mais limpo, mas mostra pesos que o cérebro nunca soma: um leitor tira conclusão errada do aprendizado. |
| **CN-3** | Espessura √\|w\| ou linear. | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** √\|w\|. | Linear apaga os pesos aprendidos pequenos ao lado dos grandes do prior (a entrada `fruta` em comer passa de 6 S); só estética, fácil de trocar. |
| **CN-4** | Colorir o aprendido pelo canal do crédito (corpo, fruta, gosto). | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** Não agora. | Pede registrar o canal por peso, uma mudança na política, atrás de chave e com gabarito. Sem ela a cor fica só prior × aprendido. |
| **CN-5** | Ler os pesos pelos privados (como o protótipo) ou por um método público de leitura em `lobos.py`. | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** Privados enquanto for protótipo; o método público só se a ferramenta ficar. | O método público mexe na política (pouco, só leitura, mas com teste e gabarito). Os privados quebram alto se mudarem. |
| **CN-6** | Desenhar a camada do corpo químico. | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** Sim, numa segunda etapa, numa aba à parte e ligada pelos receptores. | Pequeno: o grafo do corpo já existe. Fazer junto incha o primeiro passo. |
| **CN-7** | Versionar as páginas geradas (cerca de 2,5 MB com as capturas em `docs/futuro/connectome_cerebro_a/`) ou só o gerador. | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** Versionar só as duas de exemplo deste PR; as próximas ficam em `artifacts_connectome/`, ignoradas. | Versionar toda página incha o repositório; não versionar nenhuma tira do PR a prova olhável. |
| **CN-8** | A vida de exemplo padrão: o J5 `P1-plan` T1 com os números calibrados, ou outra. | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** A do J5, que é a pergunta aberta (o pet que pensa). | Baixo: a escolha é um argumento da linha de comando. |
| **CN-9** | O nome na tela: "como connectome" com o aviso fixo, ou um nome que não lembre neurônio ("mapa dos pesos do cérebro A"). | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** Manter "como connectome" no título, com o aviso fixo e o tamanho ao lado da mosca. | Com o nome, alguém pode ler o grafo como cérebro biológico; sem ele, perde-se a ponte com o pedido. O aviso reduz o primeiro risco. |
