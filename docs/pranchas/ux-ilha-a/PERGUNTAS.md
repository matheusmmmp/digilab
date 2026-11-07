# Ilha A, "Objetos que falam": perguntas ao Matheus

Esta é a prancha da direção A da ilha interativa (UX_TELA_PET, 2026-11-07). O pedido foi "Siga com as recomendações": a A primeiro, a C
depois e a B como pesquisa no Python. O que cada elemento lê do motor está no [LEIA.md](LEIA.md). As medidas novas são PROPOSTO, SEM FONTE.

## A resposta do Matheus (2026-11-07, rodada 2)

> "Que fio, eu pedi pra ser drag and drop. Quando o jogador segura no patch, se ele clica, ele faz carinho. Se ele segura, ele agarra o
> patch e daí eu posso arrastar ele pra qualquer lugar do mapa. Então, é isso. Não tem fio nenhum. Acredito que a ideia de clicar na
> árvore, ela sacudir, é interessante para cair a flor, né? A fruta. Daí segue a recomendação para as outras opções."

Isso mudou três coisas na prancha:
- **O fio da intenção saiu por inteiro,** dos estados, das notas e do LEIA. A I1-2 (o getter `alvoAtual`) e a I1-10 (o fio sem alvo)
  caíram junto com ele.
- **O estado "fio ao tocar no pet" virou "segurar e arrastar o pet",** desenhado como o jogo já faz. O estado "indo até a tigela" ficou
  sem fio.
- **O toque na árvore agora a sacode e faz cair uma fruta.** Isso pede motor novo (I1-3).

## As decisões

**I1-1. Clicar no pet e segurar o pet. DECIDIDA.**
Clicar no pet é carinho (um `acariciar`, como o botão Carinho). Segurar agarra o pet, e o jogador o arrasta e solta em qualquer lugar do
mapa (`Motor.levarPet`, o evento `lp`). Isso já existe no jogo: PEGAR_PET P1 (#673) e P2 (#674). A prancha desenha o pet na mão como o
jogo já o mostra e não acrescenta nada. Não há fio.

**I1-2. O getter só de leitura do alvo no `Mundo` do TS. CAIU com o fio.**
Sem o fio, nada precisa saber para onde o pet vai. A etiqueta do alvo atual (I1-4) usa o que a vista já lê: o tipo do alvo pendente da
percepção (`alvo_pendente = "comida"`) e a ração na tigela. No `CMU_MVP`, a comida só vem do dono, então não há getter novo.

**I1-3. Tocar na árvore a sacode e faz cair uma fruta. DECIDIDA. PEDE MOTOR NOVO.**
Hoje o jogo roda o mundo `CMU_MVP`, sem árvores e sem frutas no TS (`web/app/motor/motor.ts`). O Python tem as árvores, as quedas, a
recarga e as frutas com gosto (`digilab/frutas.py`, `digilab/mundo.py`), mas não o gesto de sacudir. A prancha só desenha o sacudir e a
fruta no chão. Nenhum código de motor entra nesta etapa.

O que a mecânica vai precisar, como tarefa própria (`docs/TAREFA_V3_<FRENTE>.md`, pelo `tools/nova_tarefa.py`):
1. **Python primeiro:**
   - um evento do dono `sacudir_arvore(id)` em `digilab/events.py`, que o replay refaz e que levanta erro se for desconhecido;
   - no `MotorFrutas` ou no `MotorMundo`, o efeito: uma fruta madura da árvore cai no chão, perto dela. Ou nada, se a árvore estiver vazia
     ou em recarga;
   - uma rng própria derivada por `derivar_semente` (por exemplo, `"mundo-sacudir"`), para não mexer na rng do ambiente nem na da
     política;
   - uma chave desligada numa `Config` nova em `digilab/config.py`, com os números PROPOSTO, SEM FONTE (quantas frutas por sacudida, o
     intervalo entre sacudidas, se o sacudir conta como contato ou cuidado);
   - desligada, a vida de hoje sai byte a byte, com o gabarito gravado num commit antes da mudança e um teste que confere;
   - a pergunta de método antes: o sacudir é contato do dono? Se for, mexe no vínculo e no aprendizado, e isso pede uma decisão.
2. **Depois o TS, com paridade:**
   - as árvores e as frutas no mundo do jogo, que hoje é o `CMU_MVP` sem árvores (a opção 1 de 2026-10-24 muda aqui);
   - o evento no `Motor` e no `aplicarEvento`;
   - um gabarito exportado por `experiments/exportar_*.py` em `web/app/test/gabaritos/` e o teste de paridade;
   - uma constante nova conferida por `constantes.test.mjs`.
3. **Uma versão de pet nova** (`VERSAO_PET` 20 ou a próxima livre): os pets v19 e anteriores não mudam, nem as assinaturas, nem os gabaritos.
4. **Só então a vista:** o toque na árvore, o tremor da copa, a fruta que cai (o modelo de hoje de `ilha/itens.ts`) e a etiqueta da árvore
   com quantas frutas ela tem.

**I1-4. Quando aparece a etiqueta curta. DECIDIDA (a recomendação).**
Aparece no hover (só no desktop), no toque e quando o objeto é o alvo atual. Fora disso, a ilha fica limpa. O cartão aberto fecha no ×,
num toque fora ou depois de 6 s sem mexer (PROPOSTO, SEM FONTE).

**I1-5. O "diário novo" na barraca. DECIDIDA (a recomendação).**
O ponto rosa aparece quando o registro tem uma linha "aprendido" ou uma evolução depois da última abertura do Diário. A marca da última
abertura fica num `localStorage` só da vista, ao lado da pele, fora do save e do replay.

**I1-6. O selo do lugar e o balão do pet no mesmo lugar. DECIDIDA (a recomendação).**
O balão do pet tem prioridade, e o selo do lugar some enquanto se sobrepõe.

**I1-7. O selo do saco. DECIDIDA (a recomendação).**
Mostra os treinos de hoje (os eventos `tr` do registro no dia do jogo) e um visto quando já pode treinar (`TreinoPet.podeTocar`). Quando
ainda não pode, o visto vira o relógio da próxima vez. A fadiga fica no Treinar.

**I1-8. "Gosta" e "evita" pelo desvio aprendido da ação. DECIDIDA (a recomendação).**
A linha usa `digibrain().aprendido`, e a vista liga a ação ao objeto: comer vira a tigela, brincar vira a bola. O texto é "brinca menos"
ou "brinca mais", comparado ao que nasceu. O paladar por fruta entra quando o motor tiver; ele vem com a I1-3.

**I1-9. O gesto no cartão é o mesmo da barra. DECIDIDA (a recomendação).**
"Servir ração" é o mesmo `observar("alimentar")` do botão Alimentar. "Mover a bola" é o mesmo arrasto do "Pôr bola" (`deixarBola`). A barra
de baixo continua igual.

**I1-10. O fio sem alvo. CAIU com o fio.**
