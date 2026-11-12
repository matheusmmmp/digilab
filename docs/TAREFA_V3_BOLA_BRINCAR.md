# TAREFA_V3_BOLA_BRINCAR: o Brincar joga a bola

Fase: V3. Trilha: C (o cérebro e o mundo do pet). Coordenador: o Gerente da V3. Data: 2026-11-11. Estado: **plano, com as decisões BB-1 a
BB-9 PROPOSTAS**; nenhum código antes da aprovação do Matheus.

## 1. Pergunta

O Matheus, em 2026-11-11: "a bola não tem muito propósito". Ele clicou em Brincar com a bola do lado do pet, e o pet "não brincou com a
bola, ele não fez nada, ele só gerou um emote". Entre as duas saídas propostas, ele escolheu "Brincar joga a bola".

**O que acontece hoje** (lido no código e medido no motor do jogo, a `main` de 2026-11-11):
- **O Brincar do dono não usa a bola.** O botão é o evento do dono "brincar":
  - no corpo, ele é a atividade `dono_brinca` (o tédio e o humor; `motor/corpo.ts`, `acaoDono`);
  - no cérebro, ele é a ação do dono de sempre;
  - a bola não muda de lugar, e o pet não escolhe nada por causa dela.
- **O pet só chuta a bola quando ele mesmo escolhe brincar** e a bola está à vista, uma célula perto (`mundo.ts`, o `brincou_com_bola`). Daí
  ela rola pelo fluxo `mundo-bola`.
- **A medida:** um pet v27 com o modular, sementes 101, 202 e 303, a bola posta a uma célula dele a cada 2 h de jogo, 2 dias:
  - ele escolheu brincar em 10 a 13 de 191 decisões e chutou de 9 a 10 vezes, cerca de um chute a cada 5 h de jogo;
  - dormir e explorar ganham quase sempre;
  - a medida foi um teste temporário, que não ficou no repositório; a etapa BB1 grava um teste com ela.

**A pergunta:** como fazer o clique em Brincar virar uma brincadeira com a bola que o jogador vê na hora, sem tirar a escolha do cérebro?

## 2. Depende de

- A bola do mundo (o `deixar_bola` do Python e o `Motor.deixarBola` do jogo) e o chute com a direção do golpe (a `bolaNoGolpe`).
- O padrão do `decidirNaComida`: a ração posta pelo dono faz o pet decidir no mesmo tick, em `motor_corpo_mundo.ts`.
- A v27 (um pet) e a v28 (o grupo, PR #861), por causa do número da versão.

## 3. Mudança mínima: as decisões propostas

- **BB-1, o lance.**
  - Com o mundo ligado, o Brincar do dono pega a bola onde ela estiver e a joga a uma distância curta do pet: o "lance do dono".
  - A bola do mundo existe sempre, então não há o caso "sem bola".
  - A direção sai de uma rng nova, `dono-bola`, derivada por `derivar_semente`.
  - A distância é de 2 a 3 células (PROPOSTO, SEM FONTE).
  - A bola cai em terra, como no `deixar_bola` de hoje.
- **BB-2, o Brincar de sempre continua.** O lance soma ao efeito de hoje: a atividade `dono_brinca` no corpo e a ação do dono no cérebro. Só a
  bola muda de lugar a mais.
- **BB-3, o pet decide na hora.** Como no `decidirNaComida`, o lance faz o pet decidir no mesmo tick, sem esperar até 15 min de jogo.
- **BB-4, o convite, não a ordem.**
  - O cérebro modular ganha uma entrada nova, `bola_do_dono`: 1 por uma janela curta depois do lance, 30 ticks (PROPOSTO, SEM FONTE).
  - A entrada pesa a favor de brincar, com um peso inicial que faz o brincar com a bola vencer quase sempre num pet acordado e sem fome
    urgente (o número sai da medida da BB1; PROPOSTO).
  - O reflexo do sono e a fome urgente continuam ganhando. Um pet emburrado ou muito cansado pode recusar, e a tela mostra a recusa.
  - Assim, a escolha continua do cérebro, e a plasticidade de hoje aprende com o resultado: o `brincou_com_bola` já vai ao P1.
- **BB-5, o chute de volta.**
  - O pet corre até a bola e a chuta pelo caminho de hoje (o `rolarBola` com a direção do golpe).
  - Cada clique é um passe; não há troca automática de vários passes.
- **BB-6, o cérebro A.** O A não vê o mundo. Com ele, o lance mexe a bola, e o pet não muda: ele segue com o Brincar de sempre.
- **BB-7, a versão.**
  - A v29 é a v27 com o lance, e a v30 é a v28 (o grupo) com o lance.
  - O ovo de um pet nasce v29, e o ovo do brasão choca o grupo v30.
  - Os pets das versões de antes ficam com o Brincar de hoje.
- **BB-8, a ordem do código.**
  - Primeiro no Python, atrás da chave `ConfigLanceDono`, desligada: o gabarito das vidas de hoje é gravado num commit próprio antes da
    mudança, e com a chave desligada as vidas saem byte a byte.
  - Depois, no motor TS com a paridade bit a bit.
- **BB-9, a vista e o som.**
  - A bola faz um arco do lado da câmera até o ponto do lance.
  - O pet corre e chuta, com os clipes que já existem (o golpe e o Feliz).
  - O som do chute e a voz contente já existem no barramento.
  - Se o pet recusar, o rosto mostra a recusa com o momento de hoje, emburrar ou cansado.

## 4. Experimento e gate

Não há run de pesquisa, só medidas em teste, com as sementes dos testes.
- **G-BB-1,** o pet v29 com o modular, acordado e sem fome urgente: depois do lance, ele chuta a bola dentro da janela em pelo menos 8 de cada
  10 lances (PROPOSTO, SEM FONTE).
- **G-BB-2,** o pet dormindo ou com a fome urgente não chuta: o reflexo ganha.
- **G-BB-3,** o replay refaz a vida, e a paridade Python × TS bate bit a bit.

## 5. Entrega

São três PRs, cada um com o relato no corpo:
- **BB1, o Python atrás da chave:**
  - o gabarito de hoje no commit próprio;
  - o lance, a entrada `bola_do_dono` e o decidir na hora;
  - a medida do G-BB-1 e do G-BB-2;
  - o exportador do gabarito.
- **BB2, o motor TS:** a paridade, a v29 e a v30, os testes e a medida no jogo.
- **BB3, a vista e o som:** o arco da bola, o clipe do chute, a recusa, um e2e de "Brincar faz o pet chutar a bola", e as capturas.

## 6. Fora desta tarefa

- O pet que quer a bola nova sozinho, sem o clique. Ele mexe em pesos do cérebro e fica para a rodada de equilíbrio.
- Vários passes seguidos, jogar a bola num lugar escolhido por arrasto, e outros brinquedos.

## 7. Critérios de aceitação

- O G-BB-1, o G-BB-2 e o G-BB-3 passam.
- Os pets v21 a v28 saem byte a byte.
- O CI fica verde.
- No jogo, clicar em Brincar faz a bola cair perto do pet, e ele corre e chuta.

## 8. Precisa do Matheus

Aprovar ou mudar as decisões BB-1 a BB-9. **Recomendo aprová-las como estão.** O custo de errar é baixo: a chave fica desligada até a BB2, e
os números ficam PROPOSTOS para a rodada de equilíbrio.

Para mudar depois, se for o caso:
- **BB-4 (convite × ordem):** a ordem, em que o pet sempre chuta, é mais simples, mas tira a escolha do cérebro e não deixa ver o pet
  emburrado recusar.
- **BB-5 (um passe por clique × vários passes):** vários passes deixam a brincadeira mais longa, mas exigem decidir quando ela acaba.
