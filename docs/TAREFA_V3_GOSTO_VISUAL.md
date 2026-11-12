# TAREFA V3 — GOSTO_VISUAL (2026-11-11)

Coordenador: Matheus (pela sessão que pediu a frente). Worker da proposta: Claude Code, Opus 5.5, worktree `v3-gosto-visual`. Worktree e
branch: `v3-gosto-visual` (as etapas seguintes com sufixo, como `v3-gosto-visual-gv1`). Status: **ABERTA; a proposta em revisão; as
GV-1 a GV-14 PROPOSTAS; o protótipo P0 no jogo web pedido pelo Matheus antes da espec (D-GV-P0-1).**

Categoria: documentacao. Origem: Matheus, 2026-11-11: depois da busca bibliográfica de 2026-11-10 sobre o pet observar a tela
compartilhada e ter um gosto visual, transformar o levantamento numa proposta de frente para revisão.

## 1. Pergunta

**Um pet que vê uma TV (do jogo ou a tela real) forma um gosto visual próprio, estável e diferente do de outros pets, e quanto dele vem
do genoma, do dono e da interação?** É uma pergunta nova da trilha C (o cérebro) do `docs/PLANO_V3.md`, sem hipótese herdada do
`docs/PLANO_V2_PESQUISA.md`; ela se liga à pergunta da INDIVIDUALIDADE (`docs/TAREFA_V3_INDIVIDUALIDADE.md`) como mais um traço. A
proposta inteira está em `docs/futuro/gosto_visual_pet.md`.

## 2. Depende de

- Na `main`: nada além do que já está.
- Do Matheus: as GV-1 a GV-14 (`docs/futuro/gosto_visual_pet.md`, seção 10), antes da GV0.
- Nenhuma etapa depende do I7 da INDIVIDUALIDADE, nem toca a worktree `v3-individualidade`.

## 3. Mudança mínima

Esta etapa só escreve documentos: a proposta em `docs/futuro/gosto_visual_pet.md` e esta tarefa. Não mudam `engine.py`, o modular, o
cérebro A, a web, o genoma de hoje, a bateria de sondas da INDIVIDUALIDADE (IN-2) nem o `config.py`.

## 4. Experimento e gate (se houver run)

Nenhum nesta etapa. A GV3 terá o plano em `docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md`, commitado antes da primeira vida, e uma faixa pedida
ao coordenador. Nenhum número é decidido aqui. GPU: não.

## 5. Entrega

- Testes: não se aplicam (só documentos).
- Registro: nenhum desvio nesta etapa; nas seguintes, seção própria no fim de `docs/registro/AAAA-MM.md`. **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge.
- PR contra a `main` com o relato no modelo (`.github/pull_request_template.md`, categoria documentacao). Merge só pelo Matheus.

### As etapas propostas

| etapa | o quê | entrega |
|---|---|---|
| **P0** | o protótipo no jogo web (a janela flutuante, a captura da tela e do som, o gosto num módulo TS fora do motor e do log), atrás de `?gosto_visual=1`; pedido pelo Matheus antes da espec (`docs/futuro/gosto_visual_pet.md`, seção 14) | código e testes do web, PR próprio |
| **GV0** | a espec (as contas do vetor, o pico, as meias-vidas, a ação "olhar", a TV do jogo, a sonda, a privacidade) e as 56 referências da nota do vault em `docs/referencias/`; **revisada pelo Matheus antes de qualquer protótipo** | documentos, PR próprio |
| **GV1** | o Python atrás de chave desligada: a TV do jogo, o vetor, o gosto (genoma e estado), a ação "olhar" num módulo do modular; o gabarito das vidas de hoje num commit próprio, antes | código e testes, PR próprio |
| **GV2** | a sonda das duas TVs como ferramenta, só leitura, com o G2 (a vida com e sem a sonda sai byte a byte) | código e testes, PR próprio |
| **GV3** | o plano de análise e a faixa; a run descritiva genoma × dono, depois da familiarização; o `RESULTADO_V3_GOSTO_VISUAL.md` | plano, run, resultado |
| **GV4** | a web: a TV do jogo, com paridade contra os gabaritos do Python | código e testes, PR próprio |
| **GV5** | a tela real (`getDisplayMedia`) no modo livre gravado, depois de uma revisão de privacidade própria | código e testes, PR próprio |

## 6. Fora desta tarefa

Qualquer código, protótipo, faixa ou vida; a TV como enfeite do layout (a `docs/TAREFA_V3_MUNDO_ENFEITES.md`); o desenvolvimento do
gosto ao longo da vida (GV-9); o teste de força pelo custo de olhar (GV-5); a sonda das duas TVs dentro da bateria da INDIVIDUALIDADE
(GV-11).

## 7. Critérios de aceitação

- `docs/futuro/gosto_visual_pet.md` existe, com a resposta à pergunta do Matheus (seção 12), o som (seção 13), o P0 (seção 14), a ideia do vetor, o gosto inato e aprendido em pico com a habituação, a ação "olhar", a
  medida em duas partes depois da familiarização, o risco do dono, a privacidade, a ligação com a INDIVIDUALIDADE, os passos GV0 a GV5 e
  as GV-1 a GV-14, cada uma com a recomendação e o custo de errar.
- Toda referência citada está na nota do vault `BUSCA_GOSTO_VISUAL_2026-11-10.md` ou em `docs/referencias/referencias_verificadas.csv`;
  o resto está escrito SEM FONTE. Nenhuma alegação de novidade.
- Os links relativos dos documentos mudados resolvem (o CI da categoria documentacao).

## 8. Precisa do Matheus

As GV-1 a GV-14, todas PROPOSTAS. O texto completo, com o apoio de cada uma, está em `docs/futuro/gosto_visual_pet.md`, seção 10.

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **GV-1** | A TV do jogo ou a tela real primeiro. | **A TV do jogo**; a tela real só no fim (GV5), no modo livre gravado. | Com a tela real primeiro, nada vale para resultado e o risco de privacidade vem antes de se saber se o gosto funciona. Com a TV primeiro, adia-se a parte mais vistosa. |
| **GV-2** | O vetor de quatro números ou outro. | **Os quatro (cor, brilho, movimento, complexidade), inteiros em [0, C].** | Um escalar só (a complexidade) faz os pets diferirem só no ponto ótimo; mais componentes diluem a medida. Trocar depois refaz o gabarito e a sonda. |
| **GV-3** | De quem é o gosto: do pet ou do dono. | **Do pet**; o dono só influencia pela exposição e pela consequência, sem comparação por pares. | Gosto do dono vira preditor da preferência do dono e tira o sentido da ligação com a INDIVIDUALIDADE. Gosto do pet pode parecer ao dono que o pet "não aprende". |
| **GV-4** | Se a parte inata entra no genoma. | **Sim, numa seção própria (rng `visao-ovo`), fora do Temperamento e do G0**, como o `GenomaFrutas`; o genoma vazio é o controle. | Sem parte inata, a parte do genoma sai zero por construção. Dentro do G0, mexe num genoma decidido. |
| **GV-5** | A medida principal. | **A escolha entre dois (agrado) e o tempo relativo (interesse), separados**; o teste de força depois. | Só o tempo faz o pet "gostar" do novo; só a escolha perde a habituação. |
| **GV-6** | A familiarização antes de medir. | **Obrigatória**, com a duração e o critério no plano de análise, antes da primeira vida. | Sem ela, mede-se a novidade da TV. Critério fixado depois dos dados convida a escolher o resultado. |
| **GV-7** | A forma do agrado. | **O pico sobre a distância ao esperado**, em inteiros. | A literatura é inconsistente: um pico ausente é resultado a registrar. Uma forma monotônica perde a habituação. |
| **GV-8** | O sinal da consequência de olhar. | **O canal da consequência do corpo que o cérebro já tem**, numa janela curta. | Janela larga lê ruído como gosto; sem consequência, o aprendido é só exposição. |
| **GV-9** | O desenvolvimento (familiar → novo com a idade). | **Fora da primeira versão.** | Com ele, a idade confunde a primeira medida; sem ele, bebê e adulto gostam igual. |
| **GV-10** | O que da tela real fica guardado. | **Só os quatro inteiros, numa taxa baixa, no log local; nada à rede, ao servidor ou à LLM; captura ligada a cada sessão e anunciada.** | Guardar mais faz do log um registro do uso do computador; guardar menos pode cegar o pet ao movimento. |
| **GV-11** | A sonda das duas TVs na bateria da INDIVIDUALIDADE. | **Não: sonda própria, com a mesma maquinaria.** | Entrar muda a IN-2 e o custo das runs de lá; separada, a comparação entre traços pede um passo a mais. |
| **GV-12** | As 56 referências da nota no repositório. | **Sim, na GV0**, com o status e os rótulos da nota. | Sem isso, a frente cita fontes só do vault; o custo é um PR a mais. |
| **GV-13** | O som: um vetor de áudio ao lado do visual. | **Sim, três inteiros (o volume, a variação e o brilho do timbre)**, local, com a regra da GV-10; antes da GV0, a busca dirigida da seção 13 da proposta. | Sem o som, a pergunta do Matheus tem só metade da resposta; com o som sem a busca, o desenho do áudio fica SEM FONTE inteiro. |
| **GV-14** | O gosto aprendido ser só o gosto do dono, por exposição; como o painel separa as partes. | **O painel mostra o inato (fixo), o da exposição e o da consequência separados**; nada premia o acerto; a medida usa estímulos que o dono nunca mostrou; o genoma × dono mede a parte do dono. | Sem a separação, o dono vê o próprio gosto devolvido como se fosse do pet; separado demais, o painel perde o tom de jogo. |

## Resultado do protótipo P0 (2026-11-11, Claude Code, Opus 5.5, branch `v3-gosto-visual-p0`)

O P0 (`docs/futuro/gosto_visual_pet.md`, seção 14) está no `web/app/src/gostoVisual/`, atrás de `?gosto_visual=1`, fora do motor, do log
e do save do pet:
- `chave.ts` (a chave desligada), `sentidos.ts` (o quadro e o áudio viram 4 + 3 números), `gosto.ts` (o pico inato da semente, a
  exposição, o carinho, a habituação, o "gosta mais de" e o estado guardado), `captura.ts` (o `getDisplayMedia` com vídeo e áudio, um vetor
  por segundo), `janelaPequena.ts` (a Document Picture-in-Picture, com erro alto sem a API), `tvDoJogo.ts` (quatro programas sintéticos,
  para ver as reações sem compartilhar a tela) e `GostoVisual.tsx` (o cartão, a janela pequena, as reações, o painel e o tempo junto);
- `src/App.tsx` só monta o componente, que não renderiza nada com a chave desligada;
- o teste é o `web/app/test/gosto_visual_p0.test.ts`.

**Visto no navegador do app** (sem artefato, medida única): com a TV do jogo, o pet olha, o balão muda, o tempo junto conta e três carinhos
deslocam o "hoje" do "de nascença". O navegador do app bloqueia a captura da tela e a janela flutuante: os dois erros aparecem na tela,
como pedido ("a tela não foi compartilhada: Permission denied"; "a janela pequena não abriu: … no window"). A captura real e a janela
pequena ficam para o Matheus conferir no Chrome ou no Edge.

## A espec do P1, a integração no cérebro e no corpo (2026-11-11, Claude Code, Opus 5.5, branch `v3-gosto-visual-p1-espec`)

O pedido do Matheus, depois de ver o P0 rodando com um clipe de música: "quero que ele acesse o cérebro para ter esses feedbacks e isso
afetar de forma biológica e química". A espec é a `docs/ESPEC_GOSTO_VISUAL_P1.md`, só documento e PROPOSTA:
- a TV do jogo e o evento `sentido_tela` do modo livre;
- um órgão da tela no molde da Audição, com a habituação como adaptação;
- os emissores sobre químicos que já existem (o tédio, a curiosidade, a tristeza, o estresse e o susto);
- o `GenomaVisao`, no molde do paladar;
- o comportamento `olhar` no M-ARB e no M-PLAST;
- a sonda das duas TVs no desenho genoma × dono;
- as etapas P1a a P1f.

**As decisões novas, GV-15 a GV-23, todas PROPOSTAS** (a tabela completa está na seção 10 da espec):

| id | a decisão | a recomendação |
|---|---|---|
| GV-15 | a frequência do vetor da tela real no log | a média de 10 s, em 16 níveis, só quando muda (até ~27 KB por hora) |
| GV-16 | o agrado no corpo ou só no sinal | os dois, cada um atrás da sua sub-chave; nenhum químico de prazer |
| GV-17 | o som alto e o movimento demais como estressores | sim: o estresse acima de um corte alto, e o susto num salto de volume |
| GV-18 | onde fica a habituação | no corpo, no molde do Ouvido |
| GV-19 | o olhar como comportamento novo | sim, no fim da lista, atrás da sub-chave |
| GV-20 | o que o pet vê na pesquisa | só a TV do jogo |
| GV-21 | olhar tira tédio | sim, como atividade, com a variedade de hoje |
| GV-22 | assistir junto tira solidão | fora da primeira versão |
| GV-23 | a novidade da tela tira curiosidade | sim, pelo `estimulo_novidade` de hoje |

Nenhum código do P1 antes da revisão do Matheus.

## Resultado da etapa P1b (2026-11-11, Claude Code, Opus 5.5, branch `v3-gosto-visual-p1b`)

O corpo ganhou o órgão da tela, atrás da `ConfigTela` (desligada; `digilab/config.py`, status em `corpo.PARAMETROS_TELA`, todos PROPOSTOS,
SEM FONTE). Ligada (só com o mundo físico, `drives_novos` e `gestos`; falha alto sem eles): sete canais (`CANAIS_TELA`) com os químicos
`adaptacao_tela_<canal>`, os receptores `tela_<canal>` (o nível) e `novidade_tela` (a soma das partes adaptadas, saturada), o
`sentir_tela` exigido a cada tick, e os emissores da seção 4 da espec: o `atividade("assistir")` no tédio, o estresse acima do corte de
volume e movimento, o susto no salto de volume e o `estimulo_agrado_tela` na tristeza. O grafo os declara (o sentido "tela", o
`ReceptorSoma` e o gatilho `tela_acima`), e a `PercepcaoCorpo` tem os oito campos novos no fim. Desligada, as vidas do gabarito do P1a
saem byte a byte. Testes novos em `tests/test_gosto_visual_corpo.py`. As escolhas estão em `docs/registro/2026-11.md`, D-GV-P1b-1 a 6; a D-GV-P1b-7 é o conserto do exportador do gabarito web do
modular, que deixa de fora os campos vazios da tela na `PercepcaoCorpo` (os gabaritos da web saem byte a byte, sem regravar).
Fica para a P1c: a TV, o motor chamando o `sentir_tela` (zeros sem olhar), o assistir e a novidade pelo corte.

## Resultado da etapa P1c (2026-11-11, Claude Code, Opus 5.5, branch `v3-gosto-visual-p1c`)

O mundo ganhou a TV, atrás da `ConfigTV` (desligada; `digilab/config.py`, status em `config.PARAMETROS_TV`, todos PROPOSTOS, SEM FONTE),
passada ao `MotorMundo` como `cfg_tv`, e o `MotorCorpo` ganhou a `cfg_tela` (a `ConfigTela` do P1b). As duas vão juntas, só com o mundo
físico, um pet fora do grupo e o corpo na frente; com uma só, falha alto. A TV é um objeto do `Mundo` numa célula da casa (`digilab/tv.py`)
com duas fontes, uma por vida: a **grade** (a TV do jogo, a única da pesquisa): os perfis e a grade sorteados pela rng própria
`tv-programas`, que só depende da semente; e o **evento** (o modo livre gravado): o último `sentido_tela` até o tick, desligada antes do
primeiro. Dois tipos novos no log, `trocar_canal` (o programa vale até o fim do programa da grade) e `sentido_tela` (`fonte|n1|…|n7`, 16
níveis), que o `reproduzir_mundo` refaz; mal formados, sem a chave ou com a fonte errada, levantam erro. O motor entrega ao corpo, a cada
tick e a cada percepção, o que a TV passa se o pet olha (zeros se não); chama o `atividade("assistir")` em cada decisão em que o pet olha e
o `estimulo_novidade(1)` a cada subida do `novidade_tela` acima do corte. O `ResumoTela` (`digilab/tv.py`) é a referência do GV-15 para o
P1f: a média de 10 amostras em 16 níveis, o evento só na mudança. Desligada, as vidas do gabarito do P1a saem byte a byte. Testes novos em
`tests/test_gosto_visual_mundo.py`. As escolhas estão em `docs/registro/2026-11.md`, D-GV-P1c-1 a 10; a D-GV-P1c-4 ("o pet olha" é
provisório: acordado, no ocioso e com a TV no raio da visão) é a que a P1d troca.
Fica para a P1d: o comportamento `olhar` no lugar do ocioso na regra de quem olha, a TV nos `vistos` (a classe `tela` do M-SENS), o
`GenomaVisao`, o canal `gosto_visual` e quem chama o `estimulo_agrado_tela`.

## Resultado da etapa P1d (2026-11-11, Claude Code, Opus 5.5, branch `v3-gosto-visual-p1d`)

O DigiBrain modular ganhou o gosto visual, atrás da subchave `olhar` da `ConfigDigibrain` (desligada), com os números numa `ConfigOlhar`
própria (`digilab/config.py`, `PARAMETROS_OLHAR`, todos PROPOSTOS, SEM FONTE):
- **o genoma** (`digilab/genoma_visao.py`): o ótimo e a largura do pico por canal, pela rng própria `visao-ovo`; o genoma vazio é o
  controle; nenhuma outra rng muda;
- **o M-SENS**: a classe `tela` (as TVs à vista, do gancho novo `ver_tela`, fora dos `objetos`), os receptores da tela lidos à parte, o
  agrado (o pico em inteiros contra o alvo) e o alvo aprendido pela exposição, com teto;
- **o comportamento `olhar`** no fim da lista: o inato (o tédio e a curiosidade), a proximidade e a novidade da linha, o incentivo da
  classe `tela` (P1), a linha H[olhar] (P2) e o termo `gosto` (o agrado do que ele já olhava); o motor o executa como o ocioso, parado;
- **o canal `gosto_visual`** no r da consequência de olhar; a exposição e o P1 da classe `tela` na mesma consequência;
- **o motor**: só olha (o `sentir_tela`, o assistir, a novidade) quem o cérebro mandou olhar, pelo gancho `olhando_tela`; sem o gancho (o
  A, os instintos), a regra provisória da P1c; o agrado no corpo (GV-16) pelo gancho `agrado_tela`, só com a sub-chave `agrado_no_corpo`.
Desligada, as vidas do gabarito do P1a e os gabaritos do modular para a web saem byte a byte (nada regravado); o A não muda. Testes novos
em `tests/test_gosto_visual_cerebro.py` (o genoma, o olhar escolhido e reforçado, o genoma × programa, o replay e a chave desligada). As
escolhas estão em `docs/registro/2026-11.md`, D-GV-P1d-1 a 11; a D-GV-P1d-1 (o `olhar` sem `AcaoPet` novo: o pet só olha a TV que já vê)
e a D-GV-P1d-4 (o termo `gosto` na ativação, que a espec não tem) são as que pedem o olho do Matheus.
Fica para a P1e: a sonda das duas TVs (o gancho já aceita várias linhas; o motor só tem uma TV, `ID_TV`) e o plano de análise. Fica para a
P1f: o porte do olhar ao motor TS (a classe `tela`, a unidade, o termo `gosto`, o canal `gosto_visual`, a exposição, o genoma `visao-ovo` e
os três ganchos), o exportador `experiments/exportar_gosto_visual.py` e a chave `olhar` nas constantes do modular (D-GV-P1d-7).

## Resultado da etapa P1f (2026-11-11, Claude Code, Opus 5.5, branch `v3-gosto-visual-p1f`)

O motor TS ganhou o gosto visual com paridade bit a bit no Node, atrás de chaves desligadas por padrão (a opção `tela` do
`MotorCorpoMundo`, a subchave `olhar` da `ConfigDigibrainModular` e as `OpcoesOlhar` do `DigiBrain`; D-GV-P1f-3):
- **o mundo** (`web/app/motor/tv.ts`): a `ConfigTela`, a `ConfigTV`, os eventos `trocar_canal` e `sentido_tela`, a TV (a grade pela rng
  `tv-programas` e o modo livre gravado) e o `ResumoTela` (GV-15);
- **o corpo** (`motor/corpo.ts`): o órgão da tela (as sete adaptações, os receptores `tela_<canal>` e `novidade_tela`, o `sentirTela`, o
  gatilho `tela_acima`, o susto do salto, o assistir e o `estimuloAgradoTela`), com o grafo conferido na carga;
- **o laço** (`motor/motor_corpo.ts`, `motor/motor_corpo_mundo.ts`): a tela entregue ao corpo em cada percepção e em cada tick (D-GV-P1f-4),
  a novidade pelo corte, o assistir e o agrado na decisão em que o pet olha, os ganchos `verTela`, `olhandoTela` e `agradoTela` com a regra
  de quem olha, e os dois eventos no replay;
- **o cérebro** (`motor/digibrain/`): o genoma `visao-ovo` (`genoma_visao.ts`), a classe `tela` do M-SENS, a unidade de olhar no fim da
  lista, o termo `gosto`, o canal `gosto_visual`, a exposição, a linha H[olhar] e o desfecho `tela`.
O exportador é o `experiments/exportar_gosto_visual.py` (o gabarito `web/app/test/gabaritos/gosto_visual.json.gz`: as constantes, os
genomas, a grade, o resumo, o grafo e 6 vidas de 288 decisões, a TV do jogo e o modo livre gravado; D-GV-P1f-5). O TS confere tudo em
`web/app/test/gosto_visual_paridade.test.ts`; o Python confere o gravado contra uma execução nova e duas execuções entre si em
`tests/test_gabarito_gosto_visual_web.py`. Desligado, o motor TS, o log, o save e os gabaritos de hoje saem iguais (a suíte do web inteira
passa sem regravar nada; D-GV-P1f-2).
O achado: o `olhar` da P1d não rodava com a `memoria_autobio`; o conserto mínimo, no Python e no TS, está na D-GV-P1f-1.
Fica de fora: a chave do web `?gosto_cerebro=1` (proposta) e a ligação do P0 ao cérebro (o `sentido_tela` gravado no registro do jogo e o
painel lendo o cérebro), que pedem uma versão de pet nova e a decisão do Matheus (D-GV-P1f-6).
