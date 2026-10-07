# V2, rodada 16: o mundo físico, o pet sem botões e o corpo (planejamento, 2026-10-07)

Coordenador: chat "Principais jogos Digimon com diálogo". **Só papel.** Nenhuma run, nenhum código nesta entrega.

**Parte das decisões do Matheus de 2026-10-07:**
- **mundo físico:** `docs/futuro/mundo_fisico.md` (PR #204, na `main`), com o protótipo `docs/futuro/mundo_fisico_vistas.html`;
- **sem elogiar e repreender nos pets novos:** PR #203, `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, aberto;
- **o ego do pet:** PR #202, `docs/futuro/ego_existencia.md`, aberto;
- **o cérebro da web é o A:** M6, no `REGISTRO_DESVIOS`.

## 1. O que já está decidido (não se reabre)

| tema | decisão |
|---|---|
| mapa | 2D contínuo, com regiões como os cômodos do Creatures 3, sem portas (M-1) |
| tela | vista inclinada do Animal Crossing (M-2); Animal Crossing e Nintendogs só como referência de desenho |
| comida | o jogador **arrasta e solta** a comida em qualquer ponto do mapa (M-3); nos pets novos, substitui o "alimentar" |
| passeio | ao explorar, o pet acha a comida deixada, a que cai das árvores e a bola, que é objeto físico |
| botões | elogiar e repreender saem dos pets novos; acariciar fica; o **tapa** entra como desaprovação **pelo corpo** (S-2) |
| aprendizado do v11 | pela consequência, como no Creatures 3 (#203, seção 7) |
| corpo | os conceitos do Creatures 3 (E-7) |
| automodelo | um corpo e uma rede de si que aprende por erro de previsão (E-1) |
| cérebro | o A (M6, E-3) |

## 2. A ordem de merge (o Matheus faz os merges)

1. **#203**, a decisão sem elogiar e repreender. Ela vem primeiro porque a seção 7 dela muda o plano do porte.
2. **#201, revisado**, o plano do porte. O worker A revisa o próprio branch (`v2-w-plano-porte`) conforme a seção 7 do #203, e o Matheus
   mescla depois da revisão (prompt W-REV-PORTE abaixo). **Não mesclar o #201 antes da revisão.**
3. **#202**, o ego do pet. Depois do #203, porque o corpo do #202 é o pré-requisito da consequência no v11 (#203, seção 5).

**Os conflitos esperados** são só nas seções do fim do `CLAUDE.md`. O coordenador resolve se o Matheus pedir.

## 3. Os prompts da rodada

Cada worker trabalha numa worktree própria, criada de `origin/main` depois dos merges indicados. Ele entrega um PR, com o relato no corpo, e
para. O merge é só do Matheus.

**Quem depende de quê:**

| prompt | worker | começa quando | entrega |
|---|---|---|---|
| W-REV-PORTE | A | depois do merge do #203 | o #201 revisado |
| W-TAREFA-MUNDO | C | já (o #204 está na `main`) | uma tarefa e um plano de análise |
| W-TAREFA-CORPO | B | depois do merge do #202 | uma tarefa |
| W-PRANCHA-MAPA | D | já | uma prancha |

### 3.1 W-REV-PORTE (chat A)

```
Você é o worker A da V2 do DigiLab. Revise o seu PR #201 (docs/PLANO_PORTE_V2_WEB.md) depois do merge do #203. Na worktree
D:\Trab\digilab\v2-w-plano-porte: git fetch origin; git merge origin/main. Leia docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md (seções 4 a 7)
e docs/futuro/ego_existencia.md (seção 2, ainda no PR #202, branch origin/futuro-ego-existencia). Mude o plano assim:
- Seção 1.2: o aprendizado da L1 pelo dono (elogio, bronca e chamado como sinal) SAI dos pets v11. Acariciar fica como gesto no corpo; o
  tapa entra como desaprovação pelo corpo, e não como sinal direto ao cérebro.
- Seção 1.3 e D-W1: a consequência passa a ser O aprendizado do v11. Ela fica atrás de chave e só liga depois dos drives de tédio e
  curiosidade (S-3; tarefa W-TAREFA-CORPO, do chat B). Até lá, o v11 sai com o aprendizado desligado.
- Seção 3: os gabaritos e os gates de paridade passam a usar a fonte consequência, e não a fonte dono. O P3 continua como braço de
  referência só no Python.
- Seção 6: a ordem das tarefas de código passa a ter o corpo (drives) antes de ligar o aprendizado. Anote também o que muda na tela
  (os botões saem nos pets novos) e no catálogo do comando pelo chat (elogiar e repreender saem nos pets novos).
- Seção 8: reescreva o D-W1 e marque o que mudou por causa do #203. As outras decisões D-W ficam, salvo o que a revisão tornar sem sentido.
  Registre isso.
Os pets v1 a v10 continuam byte a byte. Nenhum código. Atualize o PR #201 com o relato da revisão no corpo e pare.
```

### 3.2 W-TAREFA-MUNDO (chat C)

```
Você é o worker C da V2 do DigiLab. Em D:\Trab\digilab\v2: git fetch origin; git worktree add ..\v2-tarefa-mundo -b v2-tarefa-mundo
origin/main. Leia docs/futuro/mundo_fisico.md (decisões M-1 a M-3, seção 6 item 1, seção 7), o protótipo
docs/futuro/mundo_fisico_vistas.html, docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md (no PR #203 até o merge) e docs/RESULTADO_V2_N3.md. Só papel.
Escreva duas coisas:
(1) docs/TAREFA_V2_MUNDO_FISICO.md, a tarefa do mundo físico mínimo, com:
    - o mundo atrás de chave, entrando por subclasse do motor (engine.py congelado), como as frutas e a bola;
    - posições inteiras (grade com subunidades, distância em inteiros) e todo sorteio do mundo pela rng de ambiente;
    - o motor anda até o alvo que o cérebro escolhe, com velocidade fixa e gasto de energia por distância; o AcaoPet não ganha membros:
      explorar, comer e brincar ganham sub-decisões de alvo;
    - o evento deixar_comida(tipo, x, y), com a posição arredondada para a grade;
    - as árvores que derrubam frutas, a recarga, a fruta que apodrece e a bola que rola;
    - a visão por raio e o cheiro somado em inteiros, sem acesso privilegiado;
    - a fome urgente indo à comida mais próxima vista ou cheirada;
    - a paridade Python × TypeScript (movimento, cheiro e o evento);
    - os gates: G1; chave desligada = vidas de hoje byte a byte; os pets v1 a v10 iguais;
    - o dono de cada arquivo: mundo com o A, cérebro com o B, bancada com o D, web com o A.
(2) docs/PLANO_ANALISE_V2_MUNDO_FISICO.md, o plano de análise, commitado antes de qualquer run. A pergunta: o P1 (aprender pela
    consequência) ganha do P0 num mundo em que explorar compensa? O plano traz:
    - a medida (por exemplo, a energia líquida ganha por hora de busca, a fome média, o tempo até achar comida);
    - os braços P0 e P1, com o "só cuidado" acoplado;
    - o lugar onde o dono solta a comida como variável do cuidado;
    - as sementes de calibração e de validação separadas, em faixas novas, fora de FAIXAS_RESERVADAS;
    - o gate e a regra de decisão;
    - os riscos.
    O teorema do valor marginal de Charnov entra só como PISTA para "quando sair de um lugar" (confira os metadados no Crossref antes de
    citar; nenhuma alegação de novidade).
As decisões abertas M-4 (quatro regiões) e M-5 (a ordem da seção 6) ficam no fim, com a recomendação do documento. Entregue um PR e pare.
```

### 3.3 W-TAREFA-CORPO (chat B)

```
Você é o worker B da V2 do DigiLab. Depois do merge do #202, em D:\Trab\digilab\v2: git fetch origin; git worktree add
..\v2-tarefa-corpo -b v2-tarefa-corpo origin/main. Leia docs/futuro/ego_existencia.md (seção 2: o corpo do Creatures 3; seção 9: etapas 1
e 1b), docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md (seções 4 e 5) e as seções N3 e LOBOS-MUNDO do CLAUDE.md. Só papel.
Escreva docs/TAREFA_V2_CORPO_DRIVES.md, a tarefa dos drives de tédio e curiosidade (e da solidão, se a seção 5 pedir) com a química
mínima do corpo do Creatures 3. É o pré-requisito para ligar a consequência no v11 (S-3).
- Químicos por baixo dos drives de hoje, um órgão por vez (E-9, recomendado); o tamanho mínimo da E-10 fica para o Matheus. Concentrações,
  meias-vidas e taxas em inteiros.
- Os drives novos e o que os reduz: brincar com a bola reduz o tédio; explorar e achar coisa nova reduz a curiosidade; acariciar reduz o
  estresse e a solidão.
- O tapa como estímulo no corpo (dor leve, susto, estresse), e não como sinal ao cérebro. O medo da mão, o estresse acumulado e o vínculo
  ficam como efeitos medidos.
- O sinal da consequência passa a sair da redução dos drives pelo corpo. Os canais por drive já existem e ficam como opção.
- O pet sente só pelos receptores (sem acesso privilegiado).
- Gates: G1; chave desligada = vidas de hoje byte a byte; ligada sem os drives novos = os drives de hoje dentro da tolerância do plano; os
  pets v1 a v10 iguais; paridade Python × TS.
- O risco do #203, seção 5: com o corpo ligado, brincar e explorar deixam de dar só sinal negativo. Isso precisa de um teste de mecanismo,
  e o efeito é medido por plano próprio.
- Os donos de arquivo (cérebro e corpo com o B, motor com o A, bancada com o D) e o que é pesquisa e o que é produto.
As decisões abertas S-3 e S-4 (a base nova do vínculo) e E-9 e E-10 ficam no fim, com a recomendação dos documentos. Entregue um PR e pare.
```

### 3.4 W-PRANCHA-MAPA (chat D)

```
Você é o worker D da V2 do DigiLab. Em D:\Trab\digilab\v2: git fetch origin; git worktree add ..\v2-prancha-mapa -b v2-prancha-mapa
origin/main. Leia docs/futuro/mundo_fisico.md (seções 2.3 e 2.6), o protótipo docs/futuro/mundo_fisico_vistas.html,
docs/UI_GUIDELINES.md e as pranchas *Desktop e de 390 px que o jogo já usa. Faça a prancha do mapa na vista inclinada, seguindo o
protótipo, em duas versões:
- Desktop: o mapa na área principal com a câmera seguindo o pet; a bandeja de comida e a bola na lateral, para arrastar.
- Celular, 390 px: o mapa na tela inteira, arrastável com o dedo; a bandeja abrindo embaixo; gestos que não se confundam (o arrasto da
  comida começa na bandeja).
Mostre as quatro regiões do exemplo (casa com o ninho e o comedouro, jardim, campo, mata), as árvores com frutas caídas, a comida deixada,
a bola, o pet de pé com sombra, e o estado "comida solta aqui" depois do drop.
Siga o formato das pranchas de D:\Trab\digilab\Assets\Pranchas_UP e as regras de docs/estilo_up/DIRETRIZES_REPLICAR.md, com os tokens
--dl-* e os componentes dl-* da interface.
- **A versão versionada usa placeholders:** vai em docs/estilo_up/pranchas/ (MapaDesktop e Mapa390).
- **Sprites da Bandai só na cópia em Assets/Pranchas_UP,** fora do repo, pela regra de Assets.
É só prancha: nenhum código do motor nem do app. Registre a prancha nova em docs/PENDENCIAS_PRANCHAS.md como "não existe" no app.
Entregue num PR e pare. O M-4 (quatro regiões) ainda está aberto: a prancha usa quatro, como
exemplo.
```

## 4. Decisões que o Matheus ainda tem de tomar

| # | decisão | recomendação do documento | fonte |
|---|---|---|---|
| M-4 | Quantas regiões no começo | **quatro:** casa, jardim, campo, mata | `docs/futuro/mundo_fisico.md`, seção 8 |
| M-5 | A ordem da seção 6 | **como está:** mundo mínimo → tédio e curiosidade no corpo → fruta podre e praga → dispensador com botão → casa, ninho e saudade → cultivo e palavras | idem |
| S-1 | Os pets v1 a v10 continuam com os botões? | **sim:** só os pets novos ficam sem; tirar dos antigos muda o jogo deles no meio da vida | `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, seção 8 |
| S-3 | A consequência liga no v11 antes do corpo do Creatures 3? | **não:** primeiro os drives que recompensam brincar e o contato; sem eles, o pet aprende a ficar parado | idem |
| S-4 | A base nova do vínculo | **o desejo atendido e o cuidado no tempo certo**, numa tarefa própria; sem os botões, a coerência do vínculo B perde a base | idem |
| E-9 | Química por baixo dos drives, um órgão por vez, ou trocar tudo de uma vez | **por baixo e um órgão por vez:** trocar de uma vez muda todos os braços juntos | `docs/futuro/ego_existencia.md`, seção 9 |
| E-10 | O tamanho do corpo na primeira versão | **o mínimo que reproduz os drives de hoje, mais a digestão e a Vida** (o Creatures 3 tem 21 órgãos e 811 genes) | idem |

As outras decisões abertas do #202 (E-2, E-4, E-5, E-6, E-8) não bloqueiam esta rodada. Ficam para quando a rede de si entrar (etapa 2 do
#202).

## 5. Regras de sempre

- O plano de análise é commitado antes de qualquer run.
- As sementes de calibração e de validação ficam separadas, em faixas novas, fora de `FAIXAS_RESERVADAS`; a 15101…15505 está queimada.
- Os pets v1 a v10 reproduzem byte a byte, e a chave desligada dá a vida de hoje.
- O `engine.py` está congelado; o mundo entra por subclasse do motor.
- Todo número sai de um artefato, e nenhuma alegação de novidade é feita.
- Os merges são só do Matheus, e o relato de cada worker vai no corpo do PR.
