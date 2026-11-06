# TAREFA V3 — LUTA_EFEITOS (2026-11-06)

Coordenador: o Gerente da missão SPRITES_GERACAO (Claude Code, Opus 5.5). Worker: a definir por etapa. Worktree e branch: `v3-luta-efeitos`.
Status: PROPOSTA (a seção 8 fica com o Matheus).

Categoria: arquitetura. Origem: Matheus, 2026-11-06. O pedido foi deixar a luta em tempo real com os efeitos e o visual do Poké 2D Arena,
um jogo de fã, comparando com o trailer de gameplay: "Veja algum trailer de gameplay dele e veja e compare o que pode ser implementado. E
daí já prepare para começar a implementar."

## 1. Pergunta

O que do visual do Poké 2D Arena cabe na luta em tempo real do DigiLab, só na vista, sem mudar a luta, o log nem o replay? E em que ordem
isso deve entrar, para a luta passar a "se sentir" no golpe, no projétil, na postura e no nocaute?

A tarefa é de produto (a trilha B, batalha), não uma hipótese de pesquisa.

## 2. Depende de

- **A luta em tempo real que está na `main`:** `web/app/src/telas/lutar/palcoTR/` (`PalcoTR.tsx`, `cenasTR.ts`, `desenhoTR.ts`), o motor
  `web/app/motor/combate_tr/` e os clipes do UP no atlas (`Idle`, `Run`, `Attack_1`, `Stun`, `Die`).
- **Nenhuma decisão do Matheus para começar a E1.** As da seção 8 valem a partir da E2.

## 3. Mudança mínima

### 3.1 A referência: o trailer do Poké 2D Arena

**A fonte.** O jogo é do estúdio Big Kid Nation (também Fabled Apps) e ainda não pode ser jogado; há uma lista de espera para a beta. Os
textos de imprensa só descrevem o jogo por alto (Held Games, Retro Dodo e Androidphoria, lidos em 2026-11-06). O que segue sai do **clipe de
gameplay de 36 s, em 1920×1080, que a Retro Dodo publica** com crédito ao Big Kid Nation, visto quadro a quadro pelo Gerente aos 3, 6, 10,
14, 18, 21, 25, 29 e 33 s. É uma observação, SEM FONTE além do vídeo.

| o que se vê no trailer | como é |
|---|---|
| a câmera | **de cima**, com o campo inteiro na tela e até 5 lutadores; sem HUD visível no clipe |
| os sprites | pixel art pequena, com sombra no chão |
| os golpes | **por elemento**: um feixe de fogo com rastro de partículas e brasas; uma espiral de água em vórtice; um raio de gelo que congela o chão por onde passa; raios elétricos em zigue-zague; uma esfera psíquica que deixa um rastro de pontos |
| o brilho | os golpes brilham, com mistura aditiva (luz sobre o fundo) e um halo |
| a telegrafia | um **círculo no chão** marca onde o golpe vai cair, antes do impacto; as pedras que caem do céu têm a sombra antes da pedra |
| o impacto | uma explosão de luz no ponto do golpe, com fumaça e poeira |
| o chão | o golpe deixa marca: buraco de cavar, cratera, gelo |
| o golpe especial | o fundo escurece e ganha a cor do golpe (o roxo psíquico, com anéis em órbita) |

### 3.2 A nossa luta hoje (vista no navegador em 2026-11-06: Guilmon contra Monochromon, Arena, 1280 px)

- **Boa base:** o cenário do UP (o ringue com holofotes), o HUD com vida, Guts e relógio, o cartão da regra em uso e os clipes trocando
  com a ação.
- **O golpe não se sente.** Num acerto, só um número pequeno sobe. Não há faísca, tremida, clarão nem empurrão.
- **Os projéteis são um círculo liso,** azul ou vermelho.
- **As posturas são uma etiqueta de texto** ("defender", "pesado!") numa caixinha branca de 11 px.
- **Os lutadores ficam pequenos** no palco grande (escala 2 ou 3) e quase parados entre os golpes.
- **O nocaute não tem peso:** sem pausa, sem "K.O." e sem câmera.

### 3.3 O que cabe e o que não cabe

O motor da luta é **de lado, numa linha** (`x` de 240 ± 190 px), com 2 lutadores. Isso não muda: a câmera de cima, os 5 lutadores e o
terreno que se deforma de verdade ficam fora (seção 6). O que cabe é a **linguagem dos efeitos**, traduzida para a vista de lado:

| do trailer | na nossa luta (de lado) |
|---|---|
| o golpe por elemento | o projétil e o impacto com a cor e a forma do **elemento da linhagem** do lutador (D-LE-1) |
| o rastro e o brilho | o projétil com rastro de partículas e halo, desenhado com `globalCompositeOperation = "lighter"` |
| o círculo no chão | no `preparar_pesado` e no `carregar`, uma elipse no chão sob o lutador que se fecha até o golpe sair |
| a explosão de luz no impacto | uma faísca em pixel no ponto do acerto, com clarão branco no alvo |
| a poeira | uma nuvem de poeira nos pés na corrida, na arrancada e no empurrão |
| a marca no chão | uma marca temporária no piso no impacto do pesado (some em ~2 s) |
| o fundo que escurece no especial | o fundo escurece um pouco, na cor do elemento, enquanto o pesado sai |

E o que o gênero tem, mas o trailer não mostra (porque não tem HUD), e que falta à nossa luta: a pausa no impacto, a tremida, os números de
dano em pixel, a barra de vida com o dano atrasado e o "K.O." no fim.

### 3.4 As etapas

Cada etapa é uma sessão e um PR, com capturas aprovadas pelo Matheus antes do PR e o merge por ele.

- **E1, o impacto** (sem decisão pendente):
  - a pausa curta no acerto, de ~70 ms;
  - o clarão branco no alvo, por 2 quadros;
  - a tremida do palco proporcional ao dano, de no máximo 4 px;
  - a faísca em pixel no ponto do golpe;
  - o empurrão visual de alguns px no alvo;
  - os números de dano em fonte de pixel com contorno; o pesado sai maior e amarelo.
- **E2, os projéteis e os golpes por elemento:** a cor, a forma, o rastro e o brilho, pela tabela da D-LE-1.
- **E3, a telegrafia e o chão:** a elipse que se fecha no `preparar_pesado` e no `carregar`, a onda de choque no impacto do pesado, a
  poeira nos pés e a marca temporária no piso.
- **E4, as posturas como efeito:** o escudo no `defender`, a imagem fantasma na `esquiva`, a aura no `carregar`, o clarão no
  `contra_golpe` e o brilho na `pele_dura`. A etiqueta de texto vira um ícone pequeno em grade de pixel, com o nome no `title` e no
  leitor de tela.
- **E5, o nocaute e a câmera:**
  - a barra de vida com o dano atrasado (o pedaço vermelho que esvazia depois do branco);
  - no nocaute, a câmera lenta só na vista, o "K.O." grande e o fundo escurecido;
  - a câmera que acompanha a distância entre os dois, com zoom em escala inteira, para eles ocuparem mais o palco.

### 3.5 As regras de todas as etapas

- **Só vista.** Os efeitos saem dos eventos (`EventoTR`: `acao`, `dano`, `erro`, `interrompe`, `cura`, `fim`) e do `passo` da luta,
  nunca do relógio do navegador. A mesma luta desenha os mesmos efeitos, como os clipes já fazem. Nada muda em `web/app/motor`, nos
  gabaritos, no log, no replay nem em `digilab/`.
- **A pausa no impacto e a câmera lenta são do desenho, não da luta.** O relógio da luta (`luta.ts`) e o resultado não mudam.
- **Pixel art:** os efeitos em grade de pixel ou em formas de pixel inteiro, na escala do sprite. Sem desfoque nem escala fracionária
  nos sprites (a lição do Dormir).
- **Acessibilidade:** com `prefers-reduced-motion`, sem tremida, clarão nem câmera lenta; os números, os ícones e o "K.O." ficam.
- **Custo:** zero no fal.ai. Nenhum sprite novo é gerado.

## 4. Experimento e gate

Não há run de pesquisa. O gate de cada etapa tem três partes:
- `npm test` e `npm run tipos` passam;
- um teste novo confere que o desenho dos efeitos é o mesmo para a mesma luta, passo a passo, e que nenhum efeito muda o `ResultadoLutaTR`;
- as capturas em 390 e 1280 px, nas duas peles, aprovadas pelo Matheus.

## 5. Entrega

- **Testes:** em `web/app`, `npm test`, `npm run tipos` e o e2e `e2e/luta_layout.spec.ts`, mais um e2e de capturas da etapa.
- **Registro:** uma seção no fim de `docs/registro/2026-11.md` e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`, na ordem das
  seções (o `tools/conferir_saude.py` confere). O resumo de cada etapa vai no corpo do PR e numa seção no fim deste documento.
- **PR:** contra a `main`, com o corpo no modelo de `.github/pull_request_template.md`. O merge é só do Matheus.

## 6. Fora desta tarefa

- a câmera de cima, os 5 lutadores, o campo 2D e o terreno que se deforma de verdade: mudariam o motor (`combate_tr`), que é 1D e de 2
  lados;
- regras de ambiente (maré, lava, área que fecha), que já estão fora no `cenasTR.ts`;
- sprites ou clipes novos e qualquer gasto no fal.ai;
- som.

## 7. Critérios de aceitação

- **Desta proposta:** este documento na `main`, com a comparação, as etapas e a seção 8 respondida.
- **De cada etapa:**
  - o teste de determinismo dos efeitos passa;
  - `git diff origin/main -- web/app/motor digilab` sai vazio;
  - as capturas foram aprovadas pelo Matheus;
  - com `prefers-reduced-motion`, a tremida, o clarão e a câmera lenta não aparecem (um e2e confere).

## 8. Precisa do Matheus

- **D-LE-1, o elemento de cada lutador (vale da E2 em diante).** O motor da luta não tem elemento.
  - **Recomendação:** o elemento sai da **linhagem** (a espécie e o brasão) e é só da vista:
    - brasa (Coragem): fogo, laranja e vermelho;
    - cirro (Amizade): gelo e vento, azul-claro e branco;
    - ferrugem (Conhecimento): raio e metal, amarelo e cinza;
    - limo (Sinceridade): água e planta, azul-esverdeado e verde.

    Os bots e os NPCs ganham um elemento cada, numa tabela à parte.
    Conferido no atlas em 2026-11-06: brasa tem o Agumon, o Guilmon e o Koromon; cirro tem o Gabumon, o Patamon e o Tsunomon; ferrugem
    tem o Armadillomon, o Veemon e o Demiveemon; limo tem o Gomamon, o Palmon e o Tanemon.
  - **Custo de errar:** a cor de um Digimon pode não bater com o golpe dele no anime (o Patamon não é de gelo). Trocar depois é só a
    tabela, ou uma exceção por Digimon.
- **D-LE-2, a força do impacto.**
  - **Recomendação:** pausa de ~70 ms e tremida de no máximo 4 px, PROPOSTOS e SEM FONTE, ajustados nas capturas da E1.
  - **Custo de errar:** forte demais cansa numa luta de 80 s; fraco demais não muda nada.
- **D-LE-3, a ordem.**
  - **Recomendação:** E1, E2, E3, E4 e E5. A E1 sozinha já muda a sensação da luta.
  - **Custo de errar:** só a ordem.
