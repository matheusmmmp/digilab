# Ilha A, "Objetos que falam": perguntas ao Matheus

Prancha da direção A da ilha interativa (UX_TELA_PET, 2026-11-07). O pedido foi "Siga com as recomendações": a A primeiro, a C depois, a B
como pesquisa no Python; tocar no objeto acompanha a barra de ações; o fio aparece só no toque e quando o pet vai até um objeto.
Cada pergunta vem com a recomendação e o custo de errar. As medidas novas da prancha são PROPOSTO, SEM FONTE. O que cada elemento lê do
motor está no [LEIA.md](LEIA.md).

**I1-1. O toque no pet já é o carinho. O fio entra junto?**
Hoje tocar no pet grava um `acariciar` (o mesmo evento do botão Carinho; `e2e/vida_pet_cena.spec.ts`). O fio da intenção é só vista.
- **Recomendação:** o toque continua sendo o carinho e também mostra o fio por 3 s (PROPOSTO, SEM FONTE). Não nasce gesto novo e o registro
  não muda.
- **Alternativa:** o fio sai do carinho e vai para um toque longo, ou para o ícone do DigiBrain.
- **Custo de errar:** com o fio no toque, quem só quer ver a intenção também faz carinho, e o carinho conta para o vínculo e o cérebro.
  Corrigir depois é mudar só a vista.

**I1-2. Ler o alvo do cérebro pede um getter só de leitura no `Mundo` do TS. Pode?**
A chance já sai de `Motor.digibrain().decisao.chances`. O alvo escolhido (a tigela, a bola, o ponto de vagar) fica no `pendente`, que é
privado em `web/app/motor/mundo.ts`. Hoje a vista só tem o tipo (`percepcao.alvo_pendente`) e os candidatos (`ultimosCandidatos`).
- **Recomendação:** um getter `alvoAtual` só de leitura no `Mundo` do TS, como o `digibrain()`. Não muda o log, o replay, a rng nem os gabaritos.
  Entra com um teste de que a leitura não altera a assinatura.
- **Custo de errar:** sem ele, a vista teria de adivinhar o alvo pela direção do passo, e o fio poderia apontar para o objeto errado.

**I1-3. A árvore não dá frutas no jogo. O que o toque na árvore faz?**
O jogo roda o mundo `CMU_MVP`, sem árvores e só com a ração do jogador (`web/app/motor/motor.ts`, a opção 1 de 2026-10-24). As frutas, a
queda e a recarga só existem no Python (`digilab/frutas.py`, `digilab/mundo.py`). Nem lá existe gesto de sacudir. As árvores da ilha são
enfeites.
- **Recomendação:** nesta etapa o toque na árvore só mostra o nome e "sem frutas nesta ilha", como na prancha. "Sacudir para cair uma fruta"
  fica para uma tarefa de motor própria (o `trocar_arvores` e o `dar_fruta` do Python mostram o caminho).
- **Alternativa:** a árvore não reage ao toque.
- **Custo de errar:** um gesto de sacudir sem motor seria uma mecânica falsa, sem efeito no pet. É o pior caso.

**I1-4. Quando aparece a etiqueta curta dos objetos?**
- **Recomendação:** no hover (só no desktop), no toque e quando o objeto é o alvo atual. Fora disso a ilha fica limpa, como no estado
  "nada tocado". O cartão aberto fecha no ×, num toque fora ou depois de 6 s sem mexer (PROPOSTO, SEM FONTE).
- **Custo de errar:** com as etiquetas sempre à vista, a ilha vira um painel, contra a regra de pouco texto.

**I1-5. O "diário novo" na barraca: guardar onde?**
Não existe no jogo a ideia de "lido". Guardar isso no save fica fora desta frente (não tocar o save).
- **Recomendação:** o ponto rosa aparece quando o registro tem uma linha "aprendido" ou uma evolução depois da última vez que o Diário foi
  aberto. A marca da última abertura fica num `localStorage` só da vista, ao lado da pele, fora do save e do replay.
- **Alternativa:** a barraca fica sem selo nesta etapa.
- **Custo de errar:** o ponto pode aparecer de novo em outro navegador. Não muda o pet.

**I1-6. O selo do lugar e o balão do pet no mesmo lugar: quem cede?**
A 390, de noite, o balão "26 %" do pet cobre o saco (o estado "indo até a tigela").
- **Recomendação:** o balão do pet tem prioridade, e o selo do lugar some enquanto se sobrepõe.
- **Custo de errar:** o selo pode sumir num momento em que o dono queria ver o treino. É pouco: o Crescer mostra tudo.

**I1-7. O selo do saco: o que mostrar?**
- **Recomendação:** os treinos de hoje (os eventos `tr` do registro no dia do jogo) e um visto quando já pode treinar
  (`TreinoPet.podeTocar`). Quando ainda não pode, o visto vira o relógio da próxima vez, como o "Corrida 07:31" do Treinar. A fadiga fica no
  Treinar.
- **Custo de errar:** com a fadiga no selo, fica mais um número a ler na ilha.

**I1-8. "Gosta" e "evita" vêm do desvio aprendido da ação, não do objeto. Serve?**
O paladar ainda não existe no TS (`web/app/motor/corpo.ts`, "etapa 5 do paladar"). O que existe é `digibrain().aprendido`, o desvio
aprendido por ação. A vista liga a ação ao objeto: comer → tigela, brincar → bola.
- **Recomendação:** usar assim, com "brinca menos" ou "brinca mais" (comparado ao que nasceu). Quando a ação não está entre as 3 maiores,
  aparece "nada novo sobre comer". O paladar por fruta entra quando o motor tiver.
- **Custo de errar:** "gosta da bola" pode soar mais forte do que o número é (o desvio desta prancha é −0,11). Por isso o texto é "brinca
  menos", não "evita a bola".

**I1-9. O gesto no cartão: igual ao da barra?**
- **Recomendação:** sim. "Servir ração" no cartão da tigela é o mesmo `observar("alimentar")` do botão Alimentar (a ração no comedouro). O
  cartão da bola teria "Mover a bola", que é o mesmo arrasto do "Pôr bola" (`deixarBola`). A barra de baixo continua igual nas duas larguras.
- **Custo de errar:** com dois caminhos diferentes para a mesma ação, o registro ficaria ambíguo. Por isso é um caminho só (`acoes.ts`).

**I1-10. O fio sem alvo.**
Dormir, descansar e chamar não têm alvo (só `ACOES_COM_ALVO`: comer, explorar, brincar).
- **Recomendação:** com o toque no pet numa ação sem alvo, não há fio. Aparece só a etiqueta da ação com a chance acima do pet (ex.: "Dormir
  100 %").
- **Custo de errar:** pouco. É só a vista.
