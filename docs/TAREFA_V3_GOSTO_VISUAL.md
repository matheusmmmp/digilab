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
