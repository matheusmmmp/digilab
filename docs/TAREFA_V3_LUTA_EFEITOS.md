# TAREFA V3 — LUTA_EFEITOS (2026-11-06)

> **SUBSTITUÍDO, na parte do palco 1D**, pela [`docs/TAREFA_V3_LUTA_POC.md`](TAREFA_V3_LUTA_POC.md) (2026-11-08): a luta do jogo é a simulação da POC. Os efeitos E1 a E5 foram portados para o palco 2D na LP3 (seção 3.3a da tarefa); o palco 1D (`palcoTR/`) saiu na LP4 (2026-11-10), e os geradores de desenho dele foram para `web/app/src/telas/lutar/palcoPoc/`. O escudo, o contra-golpe e a pele dura da E4 não têm ação na luta nova e saíram (LP-10).

Coordenador: o Gerente da missão SPRITES_GERACAO (Claude Code, Opus 5.5). Worker: a definir por etapa. Worktree e branch: `v3-luta-efeitos`.
Status: ENTREGUE (E1 a E5 na `main`; a E5 no #690, 2026-11-07). Era PROPOSTA (a seção 8 ficou com o Matheus); o status foi atualizado na
organização de 2026-11-10.

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

## 9. Resumo da E1, o impacto (2026-11-06)

- **Feito:** `web/app/src/telas/lutar/palcoTR/efeitosTR.ts` (estado e funções puras dos efeitos: pausa, tremida, clarão, empurrão, faísca, fonte de
  pixel) e o desenho em `desenhoTR.ts`; a pausa e a espera do fim em `src/luta.ts`. Tudo sai dos eventos `dano` e `acao` e do `passo`.
- **Força (D-LE-2, DECIDIDA pelo Matheus em 2026-11-06, "Aprovo a E1", repassado pela sessão de planejamento; SEM FONTE):** pausa 70 ms (35 no leve), tremida ≤ 4 px, clarão 2 quadros, empurrão 2–5 px; constante `IMPACTO`.
- **Testes:** `test/luta_efeitos_e1.test.ts` (mesmo estado visual para a mesma luta, fim igual ao do motor), `e2e/luta_efeitos_e1.spec.ts`
  (tremida aparece; com `prefers-reduced-motion` não aparece). `git diff origin/main -- web/app/motor digilab` vazio.
- **Próxima:** E2, os projéteis por elemento (depende da D-LE-1).

## 10. Resumo da E2, os projéteis e os golpes por elemento (2026-11-07)

- **O defeito que o Matheus viu.** Na luta do GIF do empurrão ninguém dispara. O "sopro" do Gabumon é o clipe do golpe rápido, corpo a
  corpo. O sprite largo do Zudomon fica longe na tela, e nada ligava a boca ao rival (registro de 2026-11, D-LE-E2-1).
  - **O Vigia** só tem golpes corpo a corpo (D-LE-E2-3).
  - **O projétil de verdade** (o do Tankmon) também quase não aparecia: era um círculo azul ou vermelho de 5 px, perto dos pés. O voo dura
    de 5 a ~20 passos, e a tela desenha 1 quadro a cada 3 (D-LE-E2-2).
- **Feito:**
  - `palcoTR/elementosTR.ts`: o elemento pela linhagem, a tabela dos bots e dos NPCs e a exceção por Digimon, vazia (D-LE-1).
  - `palcoTR/projeteisTR.ts`, puro: o voo de cada projétil, lido do `S.projeteis` a cada passo; a geometria do palco; os pixels da cabeça,
    do rastro, da rajada e do estouro de cada elemento.
  - `desenhoTR.ts`: desenha esses pixels na grade do sprite. O halo, o rastro e o brilho saem com `lighter`; o núcleo e o anel, sólidos.
- **O desenho:**
  - **o projétil:** vai da boca do atirador à frente do alvo, na altura do peito, e fica na tela pelo menos 12 passos;
  - **a rajada:** no golpe rápido, na finta e no pesado que acertam, um feixe curto na cor do elemento vai da boca à frente do alvo
    (D-LE-E2-4, interpretação, para a aprovação do Matheus);
  - **as formas:** fogo (bola com língua de chama e brasas que sobem), gelo (lasca), raio (zigue-zague amarelo) e água e planta (gota
    com respingos que caem);
  - **o estouro:** sai na cor de quem bateu, por cima da faísca da E1.
- **Movimento reduzido:** o halo e a chama não piscam, o rastro tem 2 passos e o estouro não clareia. O projétil continua na tela.
- **Números:** `VOO` e `ELEMENTO_SEM_LINHAGEM` são PROPOSTOS e SEM FONTE (D-LE-E2-5 e D-LE-E2-8).
- **Testes:**
  - `test/luta_efeitos_e2.test.ts`:
    - o projétil desenhado entre o atirador e o alvo em todo passo em que existe;
    - a rajada entre os dois;
    - o determinismo, com o fim igual ao do `ResultadoLutaTR`;
    - o elemento de todo rival;
    - a grade de pixel e o movimento reduzido.
  - `e2e/luta_efeitos_e2.spec.ts`: o disparo do Tankmon aparece no palco, também com o movimento reduzido.
  - `git diff origin/v3-luta-empurrao-motor -- web/app/motor digilab` sai vazio.
- **Capturas:** `e2e_capturas/luta_efeitos_e2.spec.ts`, no servidor do Vite: o Gabumon contra o Vigia, o Agumon contra o Gabumon e o
  Gabumon contra o Tankmon, em 390 e 1280 px, nas duas peles. Os Cenários do Lab não abrem a luta em tempo real (D-LE-E2-9).
- **Próxima:** E3, a telegrafia e o chão.

## 11. Resumo da E3, a telegrafia e o chão (2026-11-07)

- **Feito:** `web/app/src/telas/lutar/palcoTR/chaoTR.ts`, puro, com o desenho em `desenhoTR.ts` e as marcas em `VisualTR.marcas`
  (`efeitosTR.ts`). Tudo sai do estado da luta (a ação, o preparo e o deslize de cada lado), dos eventos `dano` e `empurrao` e do `passo`.
- **O desenho, no chão e por baixo dos lutadores, na grade do sprite:**
  - **a elipse:** no `preparar_pesado`, na cor do elemento, fecha do começo ao fim do preparo sobre o anel-alvo apagado; pronta, pisca em
    branco até o pesado ou a finta sair. No `carregar`, tracejada, fecha até o fim do carregar;
  - **a onda de choque:** no acerto do pesado, dois anéis que abrem dos pés do alvo, brancos no começo e na cor de quem bateu depois;
  - **as marcas no piso:** a cratera do pesado e o arrasto dos pés no deslize do empurrão (a v18), presas ao chão, somem em 2 s;
  - **a poeira:** na corrida, na arrancada, no deslize, no pouso da queda e no acerto do pesado.
- **Movimento reduzido:** sem tremida nem poeira; o pronto não pisca; a onda é um anel só, sem luz (D-LE-E3-3).
- **Números:** `CHAO`, PROPOSTOS, SEM FONTE (D-LE-E3-6).
- **Testes:**
  - `test/luta_efeitos_e3.test.ts`: a elipse fechando e pronta até o golpe, o carregar, a cratera no x do alvo, o arrasto do deslize, o
    sumiço das marcas, as fontes de poeira, o determinismo com o fim igual ao do `ResultadoLutaTR`, a grade de pixel e o movimento reduzido;
  - `e2e/luta_efeitos_e3.spec.ts`: contra o Zudomon, a elipse, a onda e a marca aparecem no palco; com o movimento reduzido, a elipse
    aparece, sem tremida nem poeira;
  - `git diff origin/main -- web/app/motor digilab` sai vazio.
- **Capturas:** `e2e_capturas/luta_efeitos_e3.spec.ts`, no servidor do Vite: o Gabumon v18 contra o Vigia (D-LE-E3-2), em 390 e 1280 px,
  nas duas peles, com GIF em cada combinação. Aprovadas pelo Matheus em 2026-11-07 ("Aprovo as duas", repassado pela sessão de
  planejamento), com os achados D-LE-E3-1 a 3.
- **Próxima:** E4, as posturas como efeito.

## 12. Resumo da E4, as posturas como efeito (2026-11-07)

- **Feito:** `web/app/src/telas/lutar/palcoTR/posturasTR.ts`, puro, com o desenho em `desenhoTR.ts` e as batidas no escudo e no
  contra-golpe em `VisualTR.batidas` (`efeitosTR.ts`). Tudo sai do estado da luta (a ação, o preparo e o `peleAte` de cada lado), dos
  eventos `dano` e do `passo`. As posturas não empurram (D-EMP-9/11).
- **O desenho, na grade do sprite:**
  - **defender:** um escudo em arco na frente do corpo, que acende quando o golpe bate nele;
  - **esquiva:** duas cópias do sprite, na cor do elemento e apagadas, que abrem para trás;
  - **carregar:** faíscas que sobem pelos lados do corpo, sem nada no chão; a elipse tracejada continua só a da E3 (D-LE-E4-1);
  - **contra-golpe:** em guarda, um brilho pequeno na frente; no golpe devolvido, uma cruz amarela e vermelha com contorno escuro
    (D-LE-E4-3);
  - **pele dura:** a cor do metal e uma faixa de luz que corre pelo sprite enquanto a pele vale (D-LE-E4-2);
  - **o ícone:** a etiqueta de texto virou um ícone 7 × 7 em placa escura, com um elemento transparente por cima que leva o nome no
    `title` e no leitor de tela ("Gabumon: carregar"); o pesado pronto ganhou o `!!` (D-LE-E4-6).
- **Movimento reduzido:** o escudo não acende, não há clarão nem faixa, as faíscas e as cópias ficam paradas; os ícones continuam.
- **Números:** `POSTURA`, PROPOSTOS, SEM FONTE; o pixel mínimo de 2 px de CSS no celular (D-LE-E4-4).
- **Testes:**
  - `test/luta_efeitos_e4.test.ts`: o ícone de cada postura e os ícones distintos, o escudo aceso e a batida do contra-golpe, o fantasma, a
    aura fora do chão e a pele além da ação, o determinismo com o fim igual ao do `ResultadoLutaTR`, nada empurra, a grade de pixel e o
    movimento reduzido;
  - `e2e/luta_efeitos_e4.spec.ts`: contra o Zudomon, a aura e a pele aparecem, com o ícone nomeado no `title` e no leitor de tela; com o
    movimento reduzido, os ícones ficam, sem tremida, escudo aceso nem clarão;
  - `git diff origin/main -- web/app/motor digilab` sai vazio.
- **Capturas:** `e2e_capturas/luta_efeitos_e4.spec.ts`, no servidor do Vite: o Gabumon v18 contra a Lillymon (escudo, contra-golpe), o
  WarGrowlmon (pele dura, preparo, pronto), o Kuramon (esquiva) e o Silphymon (marcar), em 390 e 1280 px, nas duas peles, com GIF nos três
  primeiros. Aprovadas pelo Matheus em 2026-11-07 ("Faça o merge e siga cm o resto", repassado pela sessão que coordena a frente).
- **Próxima:** E5.

## 13. Resumo da E5, o nocaute e a câmera (2026-11-07), e o fecho da tarefa

- **Feito:** `palcoTR/nocauteTR.ts` e `palcoTR/cameraTR.ts`, puros; o desenho em `desenhoTR.ts`; a barra em `PalcoTR.tsx`; a câmera lenta e
  a espera do fim em `src/luta.ts`; `geometriaTR` com a câmera opcional (sem ela, a de antes). Tudo sai dos eventos `dano` e `cura` e do
  `passo` (mais a espera do fim, `visual.extra`).
- **O desenho:**
  - **a barra:** o pedaço da vida que saiu fica branco (~0,2 s), segura (~0,5 s) e esvazia em vermelho até a vida;
  - **o nocaute:** os últimos 36 passos a um terço da velocidade, o cenário escurece, o "K.O." em pixel sai uma vez e meia maior e encolhe
    até o final; o Die anda na espera, que no nocaute é de 1,8 s;
  - **a câmera:** segue a distância com histerese, no passo da luta; o zoom é uma escala inteira do sprite em pixels da tela (em 1280 px,
    1,33 e 1,67); os dois lutadores ficam sempre na tela (o empurrão da v18 e a cerca); os efeitos da E1 à E4 vão junto. Em 390 px não há
    zoom (D-LE-E5-2).
- **Movimento reduzido:** sem câmera lenta, sem tremida, sem a passagem do zoom e sem o "K.O." encolher; o "K.O." e a barra ficam.
- **Números:** `BARRA`, `NOCAUTE`, `CAMERA` e `PAUSA_FIM_KO`, PROPOSTOS, SEM FONTE (D-LE-E5-8).
- **Testes:**
  - `test/luta_efeitos_e5.test.ts` (16): a barra, a câmera lenta com o fim igual ao do `ResultadoLutaTR`, o escuro e o "K.O.", a histerese,
    a escala inteira, os dois na tela no zoom e no deslize, o mundo junto com o zoom, o determinismo e o movimento reduzido;
  - `e2e/luta_efeitos_e5.spec.ts` (2): contra o Monochromon, a barra atrasada, o escuro, o "K.O." e o zoom em 1280 px; com o movimento
    reduzido, o "K.O." e a barra sem tremida nem encolher;
  - `git diff origin/main -- web/app/motor digilab` sai vazio.
- **Capturas:** `e2e_capturas/luta_efeitos_e5.spec.ts`, no servidor do Vite: o Gabumon v18 contra o Monochromon (a luta inteira até o
  nocaute e a folha com sete momentos) e contra o Zudomon (a câmera longe e perto, com o empurrão), em 390 e 1280 px, nas duas peles.
  Aprovadas pelo Matheus em 2026-11-07 ("Aprovo e mergeia", repassado pela sessão que coordena a frente), com D-LE-E5-1 a 9.
- **A tarefa LUTA_EFEITOS fecha aqui:** as cinco etapas (o impacto, os projéteis por elemento, a telegrafia e o chão, as posturas, o
  nocaute e a câmera) estão feitas, só na vista. Ficam para depois: D-LE-E3-1 (o cartão sobre os pés no 390), D-LE-E4-5 (o ícone alto
  nos sprites com vão em cima) e a calibração dos números PROPOSTOS na rodada de equilíbrio visual.
