# Plano da interação direta: o gesto no mundo, o arco de comandos e a entrada sem pausa (2026-11-12)

**Status:** APROVADO, sem código. O Matheus decidiu as IN-1 a IN-8, as EN-1 a EN-8 e as TU-1 a TU-9 (seção 3) **pela recomendação** em
2026-11-12 ("Sim, pela recomendação"), e a EN-9 no mesmo dia. Os números (tempos do anel, janelas, quantidades) continuam **PROPOSTOS, SEM FONTE**, e se acertam
na rodada de equilíbrio do fim ("equilíbrio só no fim").

**Origem:** três pedidos do Matheus em 2026-11-12:
- **a interação direta no mapa:** "não ter um botão escrito limpar", e sim segurar o objeto 3D com um círculo que se completa; soltar na
  hora certa rende mais Bits; comprar objetos que automatizam, como "um coletor de cocô". A ideia: "deixar o jogo mais interativo [...] que
  o jogador realmente sinta que ele tem um controle, não só observando aquele ser";
- **o arco de comandos:** "quando clica, segura no pet, vai ter um arco de comandos [...] se ele vai fazer ou não já é uma outra questão
  [...] ele diz que não. Daí você pode repreender ou elogiar";
- **a entrada do jogador:** como cada mecânica é apresentada, ensinada e destravada, comparada com o tutorial do Wobbledogs, mas "mais
  intuitiva" do que pausar o jogo e apontar onde clicar.

**As análises, com as fontes e as referências de outros jogos, ficam no vault** (`DigiLab Research/20 Temas/`):
- `Interação direta e automação.md`;
- `Entrada do jogador e comandos ao pet.md`;
- `Tutorial — Wobbledogs × DigiLab.md`.

As referências (Weedcraft, Wobbledogs) são de sensação: **NÃO VERIFICADO EM FONTE PRIMÁRIA**, nada copiado, nenhuma alegação de novidade.

**Só no jogo web.** O pedido ao pet (EN-4) segue o PAR-14 do parceiro (`docs/GDD_V3_PARCEIRO.md`): fica no TS, atrás de chave, e um pet
que recebeu pedidos não se refaz no Python. Os gestos e o anel são vista e Tamer, e o Python não muda.

## 1. O que existe hoje (conferido na `main`, 2026-11-12)

| peça | onde | o que pesa |
|---|---|---|
| a sujeira é uma contagem; o cocô 3D é só vista; o Limpar tira todos os cocôs | `web/app/motor/mundo.ts` (`EstadoNoMundo.sujeira`); `web/app/src/telas/pet/ilha/cocos.ts` | o limpar no mapa não precisa de motor novo |
| o banheiro existe só no Python | `web/app/motor/constantes.ts` ("a quimica em TS e a etapa 4 do banheiro"); `docs/TAREFA_V2_BANHEIRO.md` | fica de fora: não há xixi (IN-5) |
| os Bits no registro do Tamer; "a moeda paga o feito, não o clique"; o chamado paga 2, com teto de 20 por dia de pet | `docs/PLANO_V3_MOEDA.md`, seções 2 e 6 | o "perfeito" só multiplica um feito que já paga |
| o toque curto no pet é o Elogiar; "um toque longo não conta" | `web/app/src/telas/pet/ToquePet.tsx` | o segurar parado está livre para o arco |
| segurar e arrastar o pet é pegar (o "lp") | `web/app/src/telas/pet/PegarPet.tsx` | o arco abre antes do limiar do arrasto |
| a obediência antiga (v2 a v10) saiu no v11 | `web/app/motor/constantes.ts`; `motor.ts` (`obed`) | o pedido não volta como sorteio |
| "o pedido [...] entra pela percepção, nunca como nota" | `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md` | o pedido é algo que o pet percebe e pesa |
| o tapa credita a última decisão | o traço do cérebro A e o espelho TS | repreender depois de um "não" pune a decisão de recusar |
| a progressão por nível do Tamer e o cartão de destrave | `docs/PLANO_V3_PROGRESSAO_TUTORIAL.md` (P-1 a P-11 DECIDIDAS) | este plano só acrescenta linhas |
| as dicas do Professor Agumon, "Mostrar dicas", "Rever o tutorial", "Já conheço o jogo" | `web/app/src/dicas.ts`; o plano de progressão, seção 4 | o canal do ensino já existe |
| a luta sem botão | LP-3 e LP-10 (`docs/TAREFA_V3_LUTA_POC.md`) | **a luta fica fora deste plano** |

## 2. Os princípios

1. **O gesto acontece no mundo.** O jogador toca, segura e arrasta o objeto 3D, e o botão fica como reserva (IN-1).
2. **A habilidade rende Bits, nunca muda o pet.** O "perfeito" vai para o registro do Tamer. O pet vive a mesma vida com ou sem ele, e o
   log do pet só ganha o mesmo `"d"` de hoje.
3. **O pedido é uma tentativa.** O pet percebe, decide e pode dizer não. A resposta do dono é o Elogiar e o Repreender que já existem.
4. **Aprender fazendo, sem pausa.** O tempo desacelera para 1x, a mão fantasma mostra o gesto no próprio objeto, e nada trava.
5. **Nunca a "resposta certa".** Nenhum texto diz que elogiar ou repreender é o certo (a decisão de 2026-10-07).

## 3. As decisões (DECIDIDAS pelo Matheus, 2026-11-12, pela recomendação)

### 3.1 A interação direta (IN)

| # | decisão |
|---|---|
| IN-1 | o botão Limpar **fica** até o gesto no mapa estar provado no celular; depois sai |
| IN-2 | o "perfeito" paga só como multiplicador de um feito que já paga, dentro do teto do dia |
| IN-3 | a opção "sem tempo" (acessibilidade) dá o bônus "bom" (PROPOSTO: a metade do perfeito) |
| IN-4 | limpar um cocô por vez (a sujeira com lugar no motor) só depois do limpar no mapa, se ele agradar |
| IN-5 | **não há xixi** (revista pelo Matheus em 2026-11-12: "Não precisa ter xixi"); a sujeira do jogo é o cocô e a terra cavada |
| IN-6 | a automação **não** conta como cuidado do dono: não paga Bits, não conta chamado, não soma vínculo |
| IN-7 | os tempos do anel (PROPOSTO: de 1,5 a 3 s) e a faixa perfeita se acertam na rodada de equilíbrio |
| IN-8 | o bônus em Bits espera a rodada de equilíbrio do cuidado em curso (a E1); o gesto pode entrar antes, com o bônus desligado |

### 3.1b As mecânicas novas pedidas em 2026-11-12 (MN)

Decididas pelo Matheus na direção; o como e os números são **PROPOSTOS**. Cada uma é mecânica nova no motor do jogo: chave desligada,
versão de pet nova e gabarito antes.

| # | decisão | o que existe hoje | o que falta (PROPOSTO) |
|---|---|---|---|
| MN-1 | **o pet pode gostar ou não de ser arrastado.** Ele solta um emoji, e isso afeta o estado dele | pegar o pet muda só a posição (PP-1, "nesta versão"); a careta é só vista (PP-3) | um traço **de nascença** (DECIDIDO pelo Matheus, 2026-11-12: "De nascença"), sorteado pelo genoma, que diz se o colo acalma ou assusta; a vida pode mexer nele (o medo da mão o piora); o efeito entra pelo corpo (alívio da solidão ou susto e estresse), como o carinho e o tapa; o emoji lê o corpo. **Revê a PP-1** |
| MN-2 | **a digidoença: a fratura.** Depois de uma derrota muito séria, o pet fica fraturado, e a vida e o esforço dele caem por um tempo | a lesão: 20 % de chance ao perder sem pontuar (`CLE.probLesao`), tratar em até 6 h ou o pet morre (`web/app/motor/constantes.ts`); o rosto Doente | uma **condição com nome e prazo**: a fratura reduz o vigor (a vida) e o fôlego (o esforço) enquanto dura e some com o tempo e o tratamento; a lista de condições pode crescer (outras digidoenças) |
| MN-3 | **cavar deixa terra por cima do chão**, um modelo 3D, que o dono limpa ou não, do mesmo jeito do cocô | cavar não existe; a sujeira é uma contagem e o cocô 3D é só vista | a ação de cavar; a terra cavada como uma sujeira com lugar no mapa; o limpar por toque ou anel (TU-4); o modelo 3D em cartoon |
| MN-4 | **a comida jogada no chão:** o dono a deixa perto do pet e ele come, ou o dono pede "Come" e o pet aceita ou recusa | o "Por ração" põe a comida no chão e o pet decide ir comer | o arrasto da comida (IT4) e o comando Come (EN-9) |

### 3.2 A entrada e o arco (EN)

| # | decisão |
|---|---|
| EN-1 | o pedido entra no cérebro como percepção, e o pet decide (faz, faz outra coisa ou diz não) |
| EN-2 | o arco abre no Rookie; no bebê, só o toque e o arrasto |
| EN-3 | um gesto pode existir no motor antes de o tutorial apresentá-lo; funciona se o jogador o achar |
| EN-4 | o pedido fica só no jogo web, atrás de chave; um pet que recebeu pedidos não se refaz no Python |
| EN-5 | um pedido por vez, com uma janela curta (PROPOSTO: alguns minutos de pet); pedir de novo substitui, não empilha |
| EN-6 | no celular, o arco junta as ações do dono e os pedidos; no desktop, o dock fica e o arco tem os pedidos e o Elogiar e Repreender |
| EN-7 | o primeiro passo é o arco só com as ações de hoje (só vista); os pedidos vêm depois (motor) |
| EN-8 | a frase da primeira recusa é neutra ("Ele disse não. A escolha é sua.") |
| EN-9 | os quatro primeiros comandos são **cavar, dormir, comer e brincar** (Matheus, 2026-11-12); o pet escolhe fazer ou não, e o dono elogia ou repreende |

### 3.3 O tutorial (TU)

| # | decisão |
|---|---|
| TU-1 | o tutorial **desacelera para 1x, nunca pausa** |
| TU-2 | o passo guiado **não trava**: a mão volta no próximo momento natural |
| TU-3 | um "?" no canto repete a última dica e a do lugar aberto |
| TU-4 | o cocô: o toque abre um arco pequeno com Limpar; o segurar faz o anel direto |
| TU-5 | as boas-vindas dizem, numa frase e sem susto, que o pet pode morrer |
| TU-6 | a dica da câmera só aparece quando o pet sai da tela |
| TU-7 | nenhum menu de metas novo |
| TU-8 | um presente pequeno ao fim do primeiro dia, quando o bebê vira Rookie (PROPOSTO: um enfeite ou alguns Bits) |
| TU-9 | o pet de exemplo é onde se aprendem os gestos do cuidado |

## 4. O mapa dos gestos (desktop e celular)

| gesto | sobre o quê | o que faz |
|---|---|---|
| toque curto | o pet | Elogiar (`acariciar`), como hoje |
| segurar parado (PROPOSTO: cerca de 0,4 s) | o pet | abre o arco (do Rookie em diante, EN-2) |
| segurar e arrastar | o pet | pegar e soltar (o "lp"), como hoje; o movimento antes do arco abrir decide que é o pegar |
| toque curto | o cocô | abre o arco pequeno com Limpar (TU-4) |
| segurar com o anel | o cocô, o ovo, a ferida, a árvore | a ação do objeto, com o "perfeito" |
| arrastar | a comida, a bola | levar até o pet ou lançar |
| clique direito (só no desktop) | o pet | o arco direto |

## 5. As etapas (um PR por etapa)

| etapa | o que entrega | depende de | motor? |
|---|---|---|---|
| **IT1, o anel** | o componente de segurar, completar e soltar, com a faixa perfeita, a opção "sem tempo" (IN-3) e o "reduzir movimento" | — | não |
| **IT2, o limpar no mapa** | o toque no cocô abre o arco com Limpar, e o segurar faz o anel (TU-4); os dois fazem o `limpar` de hoje; o botão fica (IN-1); o "perfeito" grava o multiplicador no `"bits"` do Tamer, **desligado** até o fim da E1 (IN-8) | IT1 | não (vista e Tamer) |
| **IT3, o arco do pet** | o segurar parado abre o arco com as ações de hoje (EN-7), do Rookie em diante (EN-2); o clique direito no desktop; no celular o arco junta tudo, e no desktop o dock fica (EN-6) | IT1 | não |
| **IT4, os gestos do cuidado** | o Elogiar acariciando, o banho esfregando, o tratar com o anel, o Repreender com um toque curto e sem bônus; arrastar a comida; sacudir a árvore | IT1, IT3 | não |
| **IT5, a entrada sem pausa** | a mão fantasma e o contorno no objeto; o tempo a 1x no passo guiado (TU-1); nada trava (TU-2); os passos no pet de exemplo (TU-9); a frase da morte nas boas-vindas (TU-5); o "?" (TU-3); a dica da câmera (TU-6); o presente do Rookie (TU-8); as linhas novas na tabela de níveis do plano de progressão | IT2, IT3, IT4 | não |
| **IT6, os pedidos** | o evento do pedido (nome a fechar, por exemplo `"pd"`), a percepção no cérebro com a janela (EN-5), a recusa visível, a frase neutra (EN-8); uma `VERSAO_PET` nova e a chave desligada, com o gabarito byte a byte antes (EN-4) | IT3 | **sim** (só TS) |
| **IT7, o coletor de cocô** | o primeiro mecanismo na loja do carro, que não conta como cuidado (IN-6) | a loja (MO3 do plano da moeda); a IT2 | **sim** |
| **IT8, cavar e a terra** | a ação de cavar, a terra cavada no mapa e o limpar (MN-3) | IT2, IT6 | **sim** |
| **IT9, o colo** | o pet gosta ou não de ser arrastado, com o emoji e o efeito no corpo (MN-1) | — | **sim** |
| **IT10, a fratura** | a condição depois da derrota séria, com a queda temporária da vida e do esforço (MN-2) | o núcleo da luta fechado | **sim** |
| **depois** | o cocô um a um (IN-4); a horta; os pedidos da jornada (a J4 do roadmap do parceiro) | cada um com a sua espec | sim |

**A ordem do arco, passo a passo (IT6):**
1. O dono escolhe um pedido. O registro do pet ganha o evento, com o tick.
2. O pedido entra na percepção do cérebro pela janela curta. Não é uma ordem nem uma nota.
3. O pet decide e a vista mostra: faz, faz outra coisa ou diz não (o rosto Recusa e, quando houver, a fala do gatilho "recusar").
4. O dono pode responder com o Elogiar ou o Repreender, ou deixar. O tapa credita a última decisão pelo traço, e o carinho chega pelo corpo.

**O comando Cavar (EN-9):** cavar é uma **ação nova**: o motor de hoje não tem (conferido na `main`, 2026-11-12). Pede uma ação do pet
no motor, o que fica enterrado no mapa e uma pose de cavar por forma, sem acréscimo ao desenho. O que o pet acha ao cavar (uma fruta, uma
peça da mitologia, só o buraco) fica PROPOSTO. Como é mecânica nova, entra atrás de chave e numa versão de pet nova, na IT6 ou numa etapa
própria logo depois dela.

**Os pedidos por estágio (PROPOSTO):**
- **no bebê, nenhum:** só as ações do dono;
- **no Rookie:** Come, Dorme, Brinca, Cava e Vem cá;
- **no Champion:** Fica e Explora;
- **na jornada:** Segue, Espera, Ajuda.

## 6. A entrada, momento a momento

Acrescenta linhas à tabela de níveis do plano de progressão (seção 3.3), sem mudar as que estão decididas.

| quando | o mundo mostra | o gesto ensinado | termina quando | se o jogador ignorar |
|---|---|---|---|---|
| as boas-vindas | uma frase: o pet vive com o jogo aberto e pode morrer (TU-5); "Começar" ou "Já conheço o jogo" | — | o clique | — |
| o pet de exemplo (TU-9) | a mão toca nele | o toque (Elogiar) | o `acariciar` no registro | a mão volta uma vez |
| o pet de exemplo | uma fruta no chão; a mão a arrasta | arrastar a comida | a comida comida | volta na próxima fome |
| o pet de exemplo | um cocô com contorno; a mão faz o toque e depois o segurar | o arco do cocô e o anel | o `limpar` no registro | volta no próximo cocô |
| a escolha do brasão | como hoje | — | a escolha | — |
| o ovo | a mão segura sobre o ovo | o anel, sem o "perfeito" | o ovo choca | o ovo espera |
| o bebê chama (nível 1) | o tempo a 1x; o contorno no que resolve | — | o chamado atendido | a dica `chamado` de hoje |
| o Rookie (nível 3) | o cartão de hoje e o segurar parado | o arco | o primeiro uso do arco | volta no próximo cartão |
| a primeira recusa (com a IT6) | o rosto Recusa; o Elogiar e o Repreender destacados uma vez | — | — | — |
| a câmera | o pet sai da tela; o ícone de arrastar pisca no canto (TU-6) | arrastar a câmera | o pet de volta na tela | — |
| o presente do Rookie (TU-8) | o cartão do presente | — | — | — |

## 7. O que não muda

- **A luta:** continua sem botão (LP-3, LP-10).
- **O treino:** nunca vem de um gesto ou do "perfeito" ("o treino nunca vem de clicar carinho").
- **O Repreender** nunca paga Bits e nunca tem "perfeito".
- **O cuidado básico** continua de graça (M-7); os Bits nunca são vendidos (CN-11/12).
- **O Python, o `engine.py` e os pets antigos:** só a IT6 e a IT7 mudam o motor, e cada uma com versão nova e chave desligada.

## 8. Aceite de cada etapa

- capturas no desktop (1920×950) e no celular (390×844);
- um e2e do gesto ou do passo;
- o Vitest passando;
- nas etapas com motor (IT6, IT7): o gabarito byte a byte das vidas de hoje gravado antes, num commit próprio, e a chave desligada.
