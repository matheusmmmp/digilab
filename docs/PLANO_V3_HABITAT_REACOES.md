# Plano do Digimon no habitat: a reação e o som de cada cuidado (2026-11-11)

**Status:** planejamento, sem código. As decisões HR-1 a HR-8 (seção 6) são PROPOSTAS e esperam o Matheus. Todo número é PROPOSTO, SEM
FONTE, e se acerta na rodada de equilíbrio do fim.

**Origem:** o Matheus, em 2026-11-10: "depois a gente planeja o que a gente faz com o Digimon no habitat, por exemplo. Quando você dá
comida, a reação dele e tal". Em 2026-11-11: "Pode começar no que ficou pendente ali". O som do que o Digimon UP tem já está na `main`
(SOM_UP, #781). Este plano cobre o resto: a reação que o jogador vê e ouve quando cuida do pet na ilha.

**Só apresentação.** Nada entra no motor, no log, no save nem na RNG do motor. A reação lê o que o motor já decidiu (comeu, recusou,
relaxou, teve medo) e só mostra. Vale a regra da vida do pet: o treino nunca vem de clicar carinho ou tapa. Vale também a regra das poses:
só os clipes que já existem, sem acrescentar partes ao desenho.

## 1. O que o pet faz hoje

Levantamento de 2026-11-11 no código da `main` (`web/app/src`).

**O som:** na ilha, só o comer toca (`emitirSom("comer")`, `telas/pet/cenaAcao.ts`). O `comer_fim` está na lista de efeitos, mas nada o
emite.

**A vista:** quase todo cuidado já tem uma reação. Ela aparece como a cara do pet, o emote e o flash de 1,4 s do ícone do dono. Todas as
ações do dono passam por `acoes.ts`, em `agir()`.

| Momento | Onde o instante está | O que se vê hoje | Som hoje |
|---|---|---|---|
| Pôr a ração | `PorRacao.tsx`; `agir("alimentar")` | o monte na tigela; o flash da carne | nenhum |
| O pet come | `cenaAcao.ts`, `escolherComer` | o clipe Comer virado para a comida, ou o achatar com migalhas | **comer** |
| A fruta boa ou podre | só a cor do item (`ilha/itens.ts`) | nada no pet | nenhum |
| Recusa a comida | `reacao.ts` (fome acima de 0,45) | a cara Recusa e o "x" por 3 s | nenhum |
| Carinho (botão ou toque) | `ToquePet.tsx`; `cenaAcao.ts`, `reacaoDoCorpo` | relaxou: pulinho e corações. Calmo: um leve achatar. Medo da mão: um passo atrás e a gota | nenhum |
| Tapa | `reacao.ts` | Triste com lágrima; dois em 20 s viram Medo | nenhum |
| O cocô aparece | `cenaAcao.ts`, `vigiarCoco` | agachar, tremer 1,8 s e o cocô 3D no chão | nenhum |
| Limpar | `agir("limpar")` | o flash de brilho; os cocôs somem | nenhum |
| Dormir | `papel.ts` | o quadro de dormir ou a respiração; o "zz" | nenhum (a música para) |
| Acordar | **não é detectado** | volta ao Idle | nenhum |
| Pegar e soltar | `PegarPet.tsx`; `ilha/mao.ts` | o pêndulo e o tremor na mão; a queda e o quique | nenhum |
| Pegar o pet dormindo | `PegarPet.tsx`, `podePegar` | **nada** (o toque é ignorado) | nenhum |
| A bola | `PorBola.tsx`; `ilha/vista.ts`, `bateBola` | o clipe Attack_1 e a bola rolando | nenhum |
| Brincar | `cenaAcao.ts` | pulinhos e a nota | nenhum |
| O chamado do bebê abre | `hudPet.ts`, `chamadosVisiveis` | o cartão com a barra da janela; a seta fora da tela | nenhum |
| O chamado fica urgente | `TelaPet.tsx` (último terço da janela) | o cartão grande "Chamando você"; pulinhos | nenhum |
| O chamado atendido | `acoes.ts` | o cartão some | nenhum |
| O chamado perdido | **não é detectado na vista** | nada | nenhum |
| A lesão e tratar | `papel.ts`; `agir("tratar_lesao")` | Doente com a espiral; o kit ao lado do ninho | nenhum |
| Emburrar | `papel.ts` | o clipe Emburrar e a raiva | nenhum |
| A morte | `TelaPet.tsx` | o cartão "se foi" e o cinza; o clipe Die não é usado | nenhum |
| O ovo choca | `jogo.ts`, `passarQuadroOvo` | o ovo balança | a música do nascimento; o instante da casca, nenhum |

**Clipes que existem e nada dispara** (`src/atlas.ts`): Feliz, Sacudir, Chamar, Envergonhado e Die.

## 2. O que fazer: cada momento com a reação e o som

O princípio é um só, nas três camadas: **a cara diz o que o pet sentiu, o som confirma o que o dono fez, e a voz é do pet.**

- **A cara:** o clipe ou a reação do pet.
- **O som do gesto:** o som do que o dono fez (a ração caindo, a água do banho). Responde sempre, para o toque nunca parecer perdido.
- **A voz:** um som curto do próprio pet, só quando ele sente algo (contente, medo, chamando). Hoje é o `sfx_digimon_voice` do UP com o tom
  variado por espécie e por tamanho (HR-3). Depois vira o cry sintetizado pelo genoma (S7).

| Momento | A cara (nova em **negrito**) | O som do gesto | A voz do pet |
|---|---|---|---|
| Pôr a ração | como hoje | a ração caindo (CC0) | — |
| Comer e acabar de comer | como hoje; **Feliz** no fim, se a fome subiu bem | `digimon_eating` (já toca); **`digimon_eatend` no fim** | contente, baixo |
| A fruta boa | **Feliz** | `minigame01_success`, baixo | contente |
| A fruta podre | **Recusa** e o "x" | `minigame01_fail`, baixo | resmungo (tom grave) |
| Recusa a comida | como hoje | `btn_x` | resmungo |
| Carinho: relaxou | como hoje, e **Feliz** no fim do pulinho | `touch` | contente |
| Carinho: calmo | como hoje | `touch`, mais baixo | — |
| Carinho: medo da mão | como hoje | `touch` | susto (tom agudo e curto) |
| Tapa | como hoje | um tapa seco (CC0) | choro curto |
| O cocô aparece | como hoje | um "plop" (CC0) | — |
| Limpar | **Sacudir** depois do brilho | `farm_water` | contente |
| Dormir | como hoje | — | um bocejo (a voz lenta e grave) |
| O ronco | o "zz" como hoje | o ronco suave em laço, só com a câmera perto (CC0 ou a voz bem lenta) | — |
| Acordar | **novo instante:** o fim do sono vira Cansado por 1,5 s | — | um bocejo curto |
| Pegar | como hoje | um "vupt" (CC0) | susto, se tiver Medo na mão |
| Soltar e pousar | como hoje | o baque do quique (CC0) | — |
| Pegar o pet dormindo | **novo:** o "zz" pisca e o pet se vira | `btn_x`, baixo | — |
| A bola | como hoje | o quique da bola (CC0) | contente na batida |
| Brincar | **Feliz** | — | contente |
| O chamado abre | **Chamar** | o bipe do V-pet (síntese, SD-8), três toques | a voz chamando |
| O chamado urgente | Chamar mais rápido | o bipe mais insistente | a voz chamando, mais alta |
| O chamado atendido | **Feliz** curto | `quest_complete_battle`, baixo | contente |
| O chamado perdido | **novo instante:** Triste por 2 s | um bipe descendo (síntese) | — |
| A lesão | como hoje | um impacto abafado (CC0) | choro curto |
| Tratar | **Feliz** | `digimon_supporter_level_up` | contente |
| Emburrar | como hoje | — | resmungo |
| A casca do ovo quebra | **novo instante:** o estalo, e o pet aparece | `creation_intro` ou `GrowingStartActionn` | a primeira voz |
| A morte | **Die** antes do cartão | silêncio; a música para | — |

Os nomes `sfx_ui_*` e `sfx_*` são do acervo do Digimon UP, que já está no disco. Foram escolhidos pelo nome, sem ouvir, como no SOM_UP; a
troca é uma linha no `Assets/gerar_sons_up.py`.

**Quanto toca.** O som do gesto toca sempre. A voz tem uma pausa mínima de 4 s entre duas falas, para o pet não ficar tagarela
(PROPOSTO). Com o tempo acima de `momentoVelMax`, só tocam os instantes raros: o chamado, a casca e a morte. No replay e ao carregar o save,
nada toca (o silêncio obrigatório do sound design, seção 2.6).

## 3. De onde vem cada som

| Fonte | O que cobre | Custo |
|---|---|---|
| **O Digimon UP** (no disco, fora do git, D3) | eatend, success e fail, btn_x, touch, farm_water, quest_complete, supporter_level_up, creation_intro e a voz genérica | nenhum: só entra no `gerar_sons_up.py` |
| **CC0** (Kenney, Freesound só com o filtro CC0) | a ração caindo, o tapa, o plop, o vupt, o baque, o quique da bola, o impacto da lesão e o ronco | é preciso **baixar** de 8 a 10 arquivos, com a página da licença guardada num `procedencia.json` (SD-2). Baixar pede o ok do Matheus (HR-5) |
| **Síntese no `som.ts`** (osciladores da Web Audio, sem dependência, SD-4) | o bipe do chamado, nos três níveis, e o bipe descendo do chamado perdido | código, sem arquivo |
| **A voz** | `sfx_digimon_voice` com o tom pela espécie e pelo tamanho, e com o humor (contente, resmungo, susto, choro, bocejo) | código. Mudar o tom de um único arquivo pode soar repetido, e esse é o risco que a S7 resolve |

## 4. As etapas (um PR por etapa)

| Etapa | O que entra | Depende de |
|---|---|---|
| **HR1. As reações que faltam na vista** | os clipes Feliz, Sacudir, Chamar e Die nos momentos da tabela; os instantes novos (acordar, o chamado perdido, o pet dormindo recusando a mão, a casca quebrando); a fruta boa ou podre no pet | nada |
| **HR2. O som do UP e a voz** | os efeitos do UP da seção 3; a voz pelo tom; a pausa da voz; o `comer_fim` emitido | HR1, porque usa os mesmos instantes |
| **HR3. O bipe do chamado** | a síntese no `som.ts` (abrir, urgente e perdido) | nada; pode ir junto da HR2 |
| **HR4. O foley CC0** | de 8 a 10 arquivos baixados, com a procedência; o ronco em laço perto da câmera | o ok de baixar (HR-5) |
| **HR5. A voz por espécie (S7)** | o cry gerado pelo genoma no lugar do arquivo genérico | frente própria; liga com a fala e a individualidade |

Cada etapa traz:

- o teste de unidade de cada instante novo (o instante, o clipe e o som pedido);
- o e2e de "o cuidado X pede o som Y", que se pula sem `Assets/sons`;
- o teste de replay intacto;
- a prévia, com a captura de cada reação nova.

## 5. O que não muda

- O motor, o log, o save, o replay e a RNG do motor.
- A decisão do pet: se ele recusa, relaxa ou tem medo, isso continua vindo do corpo e do cérebro, como hoje. A vista só mostra.
- Elogiar e repreender continuam fechados para os pets v11 em diante.

## 6. Decisões para o Matheus

| | Pergunta | Recomendação | Custo de errar |
|---|---|---|---|
| **HR-1** | As três camadas (a cara, o som do gesto, a voz do pet) como regra de toda reação? | Sim | Baixo |
| **HR-2** | Usar os clipes parados (Feliz, Sacudir, Chamar, Die) nos momentos da tabela da seção 2? | Sim. Já existem e não acrescentam partes | Baixo: troca de clipe |
| **HR-3** | A voz, até a S7, é o `sfx_digimon_voice` do UP com o tom pela espécie e pelo humor? | Sim, como ponte. A S7 substitui depois | Médio: pode soar repetido |
| **HR-4** | A pausa mínima de 4 s entre duas falas do pet | 4 s, PROPOSTO | Baixo |
| **HR-5** | Baixar de 8 a 10 sons CC0 (Kenney e Freesound) para o foley que o UP não tem | Sim, na HR4, com a procedência | Baixo: CC0 |
| **HR-6** | O ronco em laço só com a câmera perto do pet? | Sim. Longe, só o "zz" | Baixo |
| **HR-7** | A morte em silêncio, com a música parada e o clipe Die? | Sim | Médio: momento único |
| **HR-8** | A ordem HR1 → HR2 com HR3 → HR4 → HR5 | Sim. A HR1 sozinha já melhora o jogo sem nenhum arquivo novo | Baixo |

## 7. Fora deste plano

- O ambiente da ilha: o mar, os grilos e os passos (S5 do sound design).
- Os sons dos Bits e da loja (S6, com a MO2).
- A cooperação entre dois pets (CO) e a roda dos deuses (E0): as reações de lá usam esta mesma regra das três camadas quando chegarem.
