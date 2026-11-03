# Pranchas do laboratório do modular (LM5a, 2026-11-03)

Só desenho, para o Matheus aprovar (LAB-4 e LAB-5) **antes** de qualquer código de tela (a LM5b). Nenhum código em `web/app/`. Etapa da
`docs/TAREFA_V3_LAB_MODULAR.md`. Os números das telas são **exemplos inventados** para o desenho, coerentes com a conta do
`digilab/digibrain/`; nenhum vem de uma vida.

## O que tem

| tela | 390 px | 1280 px |
|---|---|---|
| Ajustes › Laboratório: o que é, a chave, chocar o ovo de teste, o aviso | `ajustes_390.html` | `ajustes_1280.html` |
| a tela Pet com o pet de teste (o selo "experimental"; o resto do HUD é o de hoje, só esboçado) | `pet_390.html` | `pet_1280.html` |
| o painel DigiBrain do modular | `painel_390.html` | `painel_1280.html` |

- Peles: `?pele=vidro` (Holográfico, o padrão) e `?pele=xcom` (Militar). `?sem` tira as notas amarelas e as linhas de fonte.
- Capturas em `capturas/<tela>_<largura>_<vidro|militar>.png` (12). O painel no celular é a folha inteira desenrolada (1 420 px de altura).
- Tokens: cópias dos de `tokens.css`, como na B3; nenhum token novo. Sprites e mapas vêm de `..\Assets`, fora do git (o mapa é só um
  cenário de apoio; o habitat real é o 3D de hoje, não desenhado aqui).
- Para regerar: `python gerar.py` e `sh capturar.sh` (servidor `python -m http.server 8765 --bind 127.0.0.1` em `D:\Trab\digilab`).

## De onde vem cada barra e cada texto do painel

O "motivo" é `motivos[k]` de `digilab/digibrain/adapt.py` (linhas 187 a 221), o que o M-ADAPT guarda por decisão. A unidade escolhida é
`unidades[i]` com `chave == motivo.escolha`. A tela do jogo lê o espelho TS do mesmo registro (LM4); nada aqui é calculado pela tela.

| o que a tela mostra | campo do motivo | observação |
|---|---|---|
| **Agora**: "Explorar o lugar lembrado" | `acao`, `escolha`, `tipo_escolha` | o rótulo sai da chave da unidade: `[acao, tipo, id]` |
| "Sem o lugar lembrado, teria explorado pelo cheiro" | `sondas.sem_memoria` (a unidade) e `sondas.memoria_decidiu` | a sonda é de leitura, mesmo `u`; só aparece quando `*_decidiu` é verdadeiro |
| barra **Inato** | `unidades[i].termos.inato` ÷ `unidades[i].soma` | os pesos de partida (`ConfigDigibrainInatos`) |
| barra **Objeto à vista** (não aparece no exemplo: unidade sem objeto) | `termos.prox` + `termos.nov` | só nas unidades com objeto (comida, bola) |
| barra **Incentivo (P1)** | `termos.incentivo` | só `comer` e `brincar` com objeto |
| barra **Hábito (P2)** | `termos.habito` | negativa no exemplo |
| barra **Lugar lembrado** | `termos.memoria` | só na unidade `ponto` (o M-MEM recuperou um lugar) |
| barra **Lembrança** | `termos.lembranca` (é o `L`) | só nas unidades que casam com o episódio lembrado; existe com a `memoria_autobio` |
| barra **Persistência** | `termos.persistencia` | só na unidade da intenção em curso |
| (sem barra) faceta | `termos.faceta` | a `facetas_mem` fica desligada (LAB-1): o termo nem existe |
| "**Lembrou do lugar (14, 9)**" | `alvo` (`tipo == "ponto"`, `x`, `y`, `do_mem`) | o lugar sai do alvo; o motivo não guarda a região do episódio (LM5-4) |
| "memória duradoura · semelhança 72% · peso na escolha +17%" | `lembranca.memoria` (`recente`/`duradoura`/`central`), `lembranca.sim`, `lembranca.L` | `sim` e `L` estão na escala S = 1024; o % é ÷ S. Sem episódio: `lembranca.recuperado == None` |
| **Intenção em curso**: a ação e o alvo | `estado.I` (a chave) | |
| Compromisso, Frustração, Passos sem avançar | `estado.C`, `estado.F`, `estado.n_sp` | C e F na escala S |
| "desde a decisão 41" | `estado_interno().modulos.estado.I.inicio` | **não está no motivo**; é uma leitura do estado, que a LM5b pode pedir ao motor |
| **As opções e a chance de cada uma** | `unidades[j].w` ÷ a soma dos `w` | com o reflexo do sono (`reflexo`) ou uma opção só, não há sorteio e a lista tem uma linha |
| **O que mudaria a escolha** | `sondas.{sem_memoria, sem_lembranca, sem_habito, sem_incentivo, sem_persistencia, so_inato}` e os `*_decidiu` | `sem_afeto` e `so_inato` existem; no reflexo nenhuma sonda decide |
| **Últimas ações** | `Motor.historico` (`quem == "pet"`) | o mesmo do painel do A v11 |

**Fora do painel, de propósito:** o afeto (`afeto.g_exp`, `afeto.g_apr`) entra no peso `w = a + mul(g_exp, epsilon)`, não na soma das
barras, e fica sem barra; os `fins` e os `creditos` da consequência são o fechamento da decisão anterior, não a escolha de agora; a fala de
memória (`falaMemoria.ts`) entra na LM5b pela conferência que já existe, sem desenho novo; `redecidir_evento`, `credito_corrida` e
`intencao_suspensa` ficam desligados (LAB-1).

**Os rótulos:** nenhum diz "pensando", "sentindo" ou "querendo". Dizem o módulo ("Lugar lembrado", "Hábito (P2)") ou o que o motivo
guarda ("Compromisso", "Frustração"). As barras são a **parte de cada termo na soma da unidade escolhida**; a ativação que entra no peso
é a soma limitada por `phi(soma, a_max)`, então uma soma acima do teto não é o mesmo que a chance (por isso a chance vem dos `w`, numa
seção à parte).

## Decisões para o Matheus (LM5-1 a LM5-6)

**DECIDIDAS pelo Matheus em 2026-11-03, as seis pela recomendação** ("Sim, tudo", no chat com o Gerente da V3). A LM5-5 pede uma
prancha curta a mais (o pet de teste já nascido, com Abrir e Descartar com confirmação) antes da LM5b.

- **LM5-1, onde fica o painel no celular.** Recomendação: a folha que sobe de baixo, até 85% da altura, com rolagem, aberta pelo botão
  Cérebro, como o painel do A v11 (a prancha `painel_390`). No desktop, a coluna à direita. Alternativa: uma página própria com rota
  (`#/cerebro`). **Custo de errar:** a folha cobre o pet enquanto se lê; a página tira o pet da tela. Trocar depois é refazer o
  contêiner, não o conteúdo.
- **LM5-2, quantas barras.** O motivo tem 8 termos (inato, prox, nov, incentivo, hábito, memória, persistência, lembrança). Recomendação:
  7 linhas possíveis (prox e nov juntas em "Objeto à vista"), **só as de valor diferente de zero**, e uma linha "Sem contribuição agora:
  …" com as outras. O exemplo mostra 5. **Custo de errar:** mostrar todas sempre enche a tela de barras vazias (no celular, ~7 linhas
  a mais); mostrar só as não nulas faz o painel mudar de forma a cada decisão.
- **LM5-3, como mostrar a barra negativa.** Recomendação: barra divergente com a linha do zero no meio, o negativo para a esquerda e na
  cor de perigo, mais o sinal "−" no número (não depender só da cor). Alternativa: tudo para a direita, com "contra" escrito (o desenho do
  A v11, que usa "a favor" e "contra" nos chips). **Custo de errar:** a barra de uma ponta só é mais simples de ler, mas esconde que o
  hábito pode puxar contra; a divergente pede mais largura (a coluna fica 132 + barra + 50 px).
- **LM5-4, o nome do lugar lembrado.** O motivo traz só o ponto `(x, y)` (`alvo`), não o nome da região. Recomendação: mostrar as
  coordenadas na LM5b, sem inventar nome. Alternativa: a região do episódio (`episodio.regiao`), que está no estado da memória e não no
  motivo; custa uma leitura nova no motor TS. **Custo de errar:** "(14, 9)" diz pouco ao jogador; um nome de região é mais legível, mas
  pede a leitura extra e a LM3/LM4 já estão em curso.
- **LM5-5, o pet de teste que já existe.** A prancha desenha só o estado sem pet (o ovo ainda não chocado). Falta a lista com um pet
  vivo, com Abrir e Descartar. Recomendação: uma prancha curta a mais antes da LM5b, com o descarte pedindo confirmação (apagar save só com
  decisão do Matheus e aviso na tela, `web/app/CLAUDE.md`). Alternativa: a LM5b desenha com as regras de Meus pets. **Custo de errar:**
  descartar um pet de teste sem confirmação perde o save dele.
- **LM5-6, mostrar C, F e n_sp.** Recomendação: mostrar os três em "Intenção em curso", porque são campos do motivo. Alternativa: só a ação
  e o alvo, escondendo C e F. **Custo de errar:** o compromisso e a frustração são nomes do M-ESTADO que o jogador não conhece; escondê-los
  faz o painel mostrar menos do que o modular tem, e mostrá-los pede uma linha de explicação curta.

## Desvios e o que ficou aberto

- A tarefa pede "o selo experimental, sem mudar o resto do HUD": o resto do HUD da tela Pet é esboçado só como contexto, não redesenhado.
- O mapa de fundo é um cenário de apoio do `arena_up`, não o habitat 3D.
- Nenhum campo novo no motivo é pedido, mas o "desde a decisão N" e o nome da região (LM5-4) dependem de leituras do estado que o
  motivo não traz; ficam para a LM5b só se o Matheus aceitar.

## LM5a2 (2026-11-03): o pet de teste já nascido e o Descartar (LM5-5, aprovada)

Mais duas telas, nas mesmas 4 variantes (390 e 1280 px, Vidro e Militar), 8 capturas: `ajustes_vivo_*` (Ajustes › Laboratório com o pet de teste vivo) e
`ajustes_descartar_*` (a confirmação do Descartar). O pet de teste é a **v16** (`VERSAO_PET_LAB`, LM4), não a v15, que o #525 usa; as pranchas da LM5a não citam a versão,
então nada precisou ser corrigido nelas.

| o que a tela mostra | de onde vem |
|---|---|
| nome "Agumon" | `nomeForma(m.forma)` do pet de teste (`motor/pet_lab.ts` devolve um `Motor` v16), como na lista de Meus pets |
| "Rookie" | `nomeEstagio(m.forma)` |
| "dia 3" | `diaDe(m.e.tick)`, o mesmo de Meus pets |
| "cérebro modular · versão 16" | `VERSAO_PET_LAB` (`motor/constantes.ts`) |
| selo "experimental" | o mesmo da tela Pet; vem de a versão do pet ser a do laboratório |
| Abrir | mostra o pet de teste na tela Pet (LM5-7) |
| Descartar | abre o diálogo; só o diálogo apaga o save do pet de teste |
| diálogo: "o save do Agumon de teste é apagado… Não volta" | o save do pet de teste (seu espaço próprio do save); o "do ovo ao dia 3" sai do log e do `diaDe` |
| diálogo: "seus pets de hoje não são tocados" | a regra do `web/app/CLAUDE.md` (apagar save só com decisão do Matheus e aviso na tela): o descarte só alcança o espaço do pet de teste |

O diálogo copia o formato do "Começar a geração" de `componentes/Heranca.tsx` (`alertdialog`, três linhas, "Não dá para desfazer.", Cancelar e a ação). Os números ("dia 3")
são de exemplo. Sem pet de teste, vale a prancha `ajustes_*` da LM5a (o ovo e o botão Chocar); com um vivo, o botão Chocar some e aparece a nota "só um por vez".

**Decisões novas (propostas, ao Matheus):**

- **LM5-7, o que o Abrir faz.** Recomendação: fecha Ajustes e mostra o pet de teste na tela Pet, com o selo "experimental"; o pet de hoje continua o ativo em Meus pets e
  volta pelo caminho de hoje. Alternativa: Abrir também troca o pet ativo do jogo. **Custo de errar:** trocar o ativo mistura os saves e faz o jogador achar que o pet
  de hoje sumiu; não trocar obriga a LM5b a mostrar qual dos dois está na tela.
- **LM5-8, a força da confirmação.** Recomendação: o diálogo como desenhado, foco em Cancelar, sem pedir para digitar o nome. Alternativa: digitar "descartar". **Custo
  de errar:** sem digitar, um toque duplo apaga o save (só o do teste, que se rechoca); digitar irrita para um pet experimental.
- **LM5-9, baixar o log antes.** O jogo já sabe baixar saves (`AvisoCombateTR`, `.digilab`). Recomendação: não oferecer no diálogo agora. Alternativa: um link "Baixar o
  log antes de descartar". **Custo de errar:** sem o link, um log curioso se perde (o pet de teste não gera medida de pesquisa); com o link, o diálogo ganha uma saída a mais.
