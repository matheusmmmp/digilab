# TAREFA V3 — SPRITES_ACOES (2026-11-04)

Coordenador: o Gerente da frente (sessão Claude Code, worktree `v3-sprites-acoes`). Worker: uma sessão por missão (seção 3.6).
Worktree e branch: `v3-sprites-acoes` (esta tarefa); as missões em `v3-sprites-<missao>`. Status: ABERTA. SA-1 a SA-8 DECIDIDAS pelo Matheus em 2026-11-04 (seção 8): o Comer vai primeiro, de ponta a ponta.

Categoria: arquitetura. Origem: Matheus, 2026-11-04: pedido do Matheus ao Gerente da frente: uma animação própria para cada ação do pet
e do dono, para o dono ler o estado do pet olhando para ele (passo 2 da Vida do pet).

## 1. Pergunta

Que animação o pet mostra em cada ação dele, em cada ação do dono e em cada momento da vida, para o dono ler o estado do pet só de
olhar para ele, sem mudar o motor? É o passo 2 da frente "Vida do pet": cada ação com uma cena visível, só na vista. O passo 1 é o
movimento (PR #561) e o passo 3 são as ações novas (`docs/TAREFA_V3_ACOES_NOVAS.md`, PR #565). Não vem de hipótese de pesquisa: é
produto (`docs/PRODUTO_VISAO.md`).

## 2. Depende de

- **As decisões SA-1 a SA-8 do Matheus** (seção 8). Sem elas nenhuma missão sai.
- **A M3 (tocar na ilha) dependia do PR #561, que já entrou; agora depende do #568 (o `Clipe`) e parte do `cenaAcao.ts` da "Vida do pet" (seção 3.6).** Antes, a frase era: a M3 depende do PR #561 na `main`. O #561 mexe em `ilha/vista.ts` e `vistaMundo.ts`, e a M3 também. A M1 e a
  M2 não dependem dele.
- **O passo 3 (#565) não cria membro novo no `AcaoPet`.** O passeio usa o `explorar`, então a tabela abaixo já cobre o que ele traz.
- **Os sprites são os do Digimon UP do projeto.** A decisão é definitiva (2026-10-24, `docs/UI_GUIDELINES.md` 5.1). Os quadros
  derivados deles ficam fora do git, junto do atlas, e o script que os gera é versionado.

## 3. Mudança mínima

### 3.1 O que o motor dá (levantado em `origin/main` deb96a82, 2026-11-04)

- **Uma decisão do pet a cada 15 ticks** (`C.intervalo`, `motor/constantes.ts:20`). Um tick é um minuto de jogo.
  - Na velocidade padrão (10 min/s), cada ação dura cerca de 1,5 s.
  - A 1 h/s, cerca de 0,25 s.
  - A 6 h/s, a tela só vê a última ação de cada passo de 100 ms.
  - Não há um campo `acaoDesde`: o início sai de `m.prox - C.intervalo` ou do último item de `m.historico`.
- **Todo pet que abre hoje tem mundo** (v13 em diante; `Habitat.tsx:20`).
  - Com WebGL, ele vai para a ilha (`ilha/vista.ts`, `papel.ts`).
  - Sem WebGL, vai para a reserva em CSS (`MundoReserva.tsx`), que mostra o primeiro quadro parado.
  - A sala 2D antiga (`cena3d.ts` `VistaPet` e o `PalcoPet` completo) só existe para os pets sem mundo (v1–v11), hoje só nos saves
    dos e2e.
- **A ração é comida no instante de uma decisão.** Não há um "comendo agora".
  - O que fica é a entrada nova em `mundo.consumos` (`{tick, id, tipo, como, fome_antes, fome_depois}`, `motor/mundo.ts:639`).
  - Também fica o `comeu` em `mundo.decisoes[last]`.
- **O chute na bola** é a entrada nova em `mundo.rolagens` (`mundo.ts:656`). Ele já toca o `Attack_1` por 450 ms (`vista.ts:178`).
- **A ação do dono** (`m.observar`) não devolve nada.
  - O que dá para ler depois: o último item de `m.historico` (`quem: "dono"`), a emoção em `m.pol.mem.emocoes[last]`, o `m.e`
    mudado e o chamado fechado.
- **A recusa não existe nos pets de hoje.** O `obed` é sempre 0 e o `motivo.recusa` nunca é preenchido (`motor.ts:870`). O caminho
  em `fala.ts:95` está morto.
  - **Questão Q-1:** sem um dado do motor não há animação de recusa. Esta frente não a inventa.
- **O treino:** `m.treinar(ex)` é instantâneo.
  - A vista faz a mesma coreografia do saco para os 6 exercícios (`vista.ts:186`, por `CENA.treino`).
  - **Achado A-1:** a coreografia toca também quando o resultado é `enrolou`, porque o `CENA.treino` é posto antes de o resultado ser
    lido (`TelaTreinar.tsx:170`). Fica fora desta frente, como questão.
- **Os clipes de hoje** (`atlas.ts` `Clipe`) são `Idle`, `Run`, `Attack_1`, `Stun` e `Die` nos 76 sprites, e `Evol` em 57.
  - O pet só usa as **60 formas**, que são 60 Digimon diferentes. Os outros 16 sprites são NPCs e bots da luta e não precisam das
    ações.
  - O esqueleto Spine do UP tem só 7 ossos (`root`, `Head_PVP`, `Center`, `Fx_OverHead`, `Shadow`, `Fx`, `Weapon_sec_0_5`). A
    animação é troca de quadro, não rig, então não há pose nova para tirar do Spine. O `Fx_OverHead` pode dar o ponto da cabeça
    (a conferir na M1).

### 3.2 Os casos de uso

Prioridade: **1** é a mais alta. Uma camada de prioridade maior substitui o corpo do pet. Os **sobrepostos** (S) desenham por cima
de qualquer corpo e nunca o trocam. "Novo" é um clipe a gerar no Aseprite (seção 3.3); "vista" é só código da vista, sem quadro novo.
Todas as durações e todos os ms são PROPOSTOS, SEM FONTE.

| ação ou momento | gatilho (campo e valor) | animação proposta | duração | prio | clipe que já serve |
|---|---|---|---|---|---|
| nascer do ovo | `nascendo > 0` (`jogo.ts:148`) | o ovo balança (já existe) | ~4,8 s | 1 | sim (peça `ovoN`) |
| evolução | `m.evolucoes.length` sobe | `CenaEvolucao` (já existe) | a do `Evol` | 1 | `Evol` (57) |
| morte | `m.morte !== null` | `Die` uma vez, segura o último quadro (hoje o sprite não muda) | ~1,2 s e fica | 1 | `Die` |
| tapa (dono) | último `historico` = dono `tapa` | `Stun` uma vez | 200 ms + 400 ms parado | 2 | `Stun` |
| carinho (dono) | dono `acariciar` | **Feliz**: um pulinho com amassado na volta, coração por cima | ~0,8 s | 2 | não (novo, programático) |
| brincar (dono) | dono `brincar` | **Feliz** com nota por cima | ~0,8 s | 2 | não (o mesmo Feliz) |
| limpar (dono) | dono `limpar` | **Sacudir**: oscila de lado, brilho e bolhas por cima | ~0,8 s | 2 | não (novo, programático) |
| tratar (dono) | dono `tratar_lesao` | `Idle` com brilho verde por cima | ~1 s | 2 | vista (`Idle` + S) |
| alimentar (dono) | dono `alimentar` (a ração vai ao comedouro) | olha para o comedouro, depois `Idle` | ~0,6 s | 2 | vista (virar para o alvo) |
| elogiar, repreender, petisco, banheiro (pets antigos) | dono `elogiar`… | Feliz, `Stun`, Comer e Sacudir | as mesmas | 2 | os mesmos |
| comeu a ração (mundo) | entrada nova em `mundo.consumos` | **Comer** uma vez (2 mordidas), virado para onde estava a ração | ~0,9 s | 3 | não (novo, a prova abaixo) |
| chutou a bola (mundo) | entrada nova em `mundo.rolagens` | `Attack_1` (já existe) | 450 ms | 3 | `Attack_1` |
| treino (6 exercícios) | `CENA.treino` | hoje: a coreografia do saco para todos. Proposta: levantar pedra e alvo com `Attack_1`; corrida com `Run`; esquiva com `Run` de lado mais pulinho; meditar com `Idle` lento e aura; resistência com `Stun` em laço | 4,2 s (a de hoje) | 3 | quase todos (vista) |
| andando (mundo, passeio) | a posição do motor mudou (`ANDANDO_MS`) | `Run` com pulinho (já existe) | enquanto anda | 4 | `Run` |
| dormir | `m.acao === "dormir"` | o achatado com "zz" (já existe, `sono.ts`) | enquanto dura | 5 | vista |
| comer (ação do pet) | `m.acao === "comer"` | **Comer** em laço (os pets sem a ração no chão) | enquanto dura, mínimo 1 ciclo | 5 | não (o mesmo Comer) |
| brincar (ação do pet) | `m.acao === "brincar"` | **Brincar**: `Run` no lugar com pulinho mais alto, nota por cima | enquanto dura, mínimo 1 ciclo | 5 | quase (`Run` + vista) |
| chamar atenção | `m.acao === "chamar_atencao"` | **Chamar**: pulinhos curtos virado para a câmera, `!` por cima | enquanto dura, mínimo 1 ciclo | 5 | não (novo, programático) |
| explorar | `m.acao === "explorar"` | `Run` até o ponto e, parado, vira de um lado para o outro (olhar) com `?` | enquanto dura | 5 | vista (`Run` + virar) |
| emburrar | `m.acao === "emburrar"` | **Emburrar**: de lado para a câmera, abaixado 1–2 px, tom mais escuro, `Idle` mais lento, nuvem de raiva por cima | enquanto dura, mínimo 1 ciclo | 5 | não (novo, programático) |
| à toa | `m.acao === "ocioso"` | `Idle` com os passinhos do #561 | enquanto dura | 6 | `Idle` |
| chamado do bebê (fome, higiene, carinho) | `m.chamadosAbertos()` | o corpo do **Chamar** mais o emote do pedido (carne, gota, coração) | enquanto aberto | 5 | o Chamar |
| fome abaixo de 50 % | `fomeNoEmote(m)` (`e.fome < .5`) | a carne sobre a cabeça (já existe) | enquanto vale | S | sim |
| saúde crítica | `e.saude < .3` | **Fraco**: tom pálido e `Idle` 1,5× mais lento (hoje é só o quadrado vermelho) | enquanto vale | S | vista (tom + ms) |
| lesão | `m.lesionadoDesde !== null` | andando, o `Run` manca (1 px a mais num passo sim, outro não); parado, uma faixa por cima | enquanto vale | S | vista |
| sujeira | `e.sujeira > 0` | o cocô ao lado (já existe), mais 2 moscas por cima a partir de 3 sujeiras | enquanto vale | S | vista |
| emoção registrada | `m.pol.mem.emocoes[last]` novo | o emote da emoção por 1,4 s (como o flash de hoje) | 1,4 s | S | sim (`emoji_*`) |

**Quando duas coincidem** (a proposta da SA-5):

- **Ação do dono durante uma ação do pet:** a reação ocupa um ciclo e o pet volta ao que fazia. Exemplo: o pet comendo e o dono faz
  carinho. O Feliz toca uma vez (~0,8 s) e o Comer volta.
- **Pet dormindo:** só o tapa (`Stun`) e a morte trocam o corpo. As outras ações do dono viram só o ícone sobreposto, e o pet segue
  achatado. O motor é que diz se ele acordou.
- **Duas ações do dono seguidas:** a segunda recomeça a reação.
- **Um momento do mundo** (comeu, chutou) não interrompe uma reação do dono: espera ela acabar, até 1 s. Depois disso é descartado.
- **Duração mínima:** toda animação de estado toca pelo menos um ciclo inteiro, mesmo que o motor já tenha trocado a ação.
- **Acima de 1 h/s:** os momentos do mundo saem, porque se atropelam. Ficam os laços de estado e os sobrepostos.

**O que é do motor e o que é só vista:** todo gatilho acima é um campo que o motor já grava. Nenhuma animação escreve no motor, no
log, no save nem no replay. A escolha do clipe é uma função pura da vista: (motor, eventos novos desde o último quadro, relógio da
vista) → clipe. Ela fica em `src/`, nunca em `motor/`.

### 3.3 O Aseprite: o que sai por programa e o que exige desenho

**A prova (2026-11-04):** o **Comer do Agumon**.

- **O que foi feito:** gerado pelo MCP do Aseprite com um script Lua (`remaster/acoes/prova/gerar_comer.lua`, fora do git, como o
  resto do `remaster/`).
- **De onde parte:** do `.aseprite` do export, `remaster/aseprite/Agumon_v04.aseprite`, com as camadas sombra, personagem e
  efeitos e as tags do UP.
- **A receita:**
  - 8 quadros tirados dos 6 do `Idle`;
  - o personagem inclinado para a frente (cisalhamento: o topo anda até 8 px e o pé fica parado);
  - achatado até 0,90 na mordida, com a escala ancorada no pé;
  - a carne (arte própria, numa camada `comida`) encostada na ponta do focinho, perdendo 2 mordidas;
  - um farelo nas duas mordidas.
- **Resultado:**
  - os ms são 133, 100, 100, 133, 100, 133, 100 e 133 (~0,93 s por ciclo);
  - a caixa é a mesma do export (94×68), e o pé fica na linha 58 em todos os quadros;
  - prévias: `remaster/acoes/prova/Agumon_comer_x4.gif` e `Agumon_comer_tira_x4.png`.
- **A mesma receita sem ajuste em outros 4 Digimon:** Tanemon, Garurumon, Seadramon e Gatomon (`comparacao_5.png`).
  - O tempo de máquina foi de 0,43 a 0,99 s por Digimon e por ação.
  - A ponta do focinho achada sozinha acerta no Agumon, no Garurumon e no Seadramon.
  - Erra no Tanemon e no Gatomon, que estão de frente: pega a folha e a orelha.
  - **Logo, cada Digimon precisa de um ponto de boca conferido à mão.** É uma tabela de 60 pares de números, versionada.
- **O Matheus olhou a prova 1:** "tem que fechar e abrir" a boca. Só inclinar o `Idle` não abre a boca.
- **A prova 2 (`gerar_comer2.lua`, `Agumon_comer2_x4.gif`):** a boca abre e fecha com os quadros do próprio UP, sem desenho.
  - O `Attack_1` do Agumon tem a boca aberta nos quadros 9 a 14 e fechada no 15 e no 16, na mesma pose inclinada.
  - O Comer alterna 15 (fechada), 11 e 12 (aberta), 15 com uma mordida, 13 e 14 (aberta), e 16 com uma mordida.
  - Os ms são 133, 100, 67, 133, 100, 67, 133 e 133 (~0,87 s). A carne perde um pedaço a cada vez que a boca fecha.
- **Logo, a receita do Comer é escolher quadros, não deformar.**
  - Por Digimon, a tabela de âncoras ganha a sequência de quadros com a boca aberta e fechada, tirada do `Attack_1`, do `Evol` ou do
    `Stun`, além da ponta do focinho.
  - **Não se sabe ainda quantos dos 60 têm um par aberta e fechada na mesma pose.** Um Digimon que golpeia com as mãos pode não ter.
    A M1 faz esse catálogo primeiro (seção 3.6).
  - Onde não houver, a queda é a prova 1 (inclinar e morder sem abrir). O Matheus decide se desenha à mão os que sobrarem (SA-9).

**O que dá para gerar por programa a partir dos clipes que existem:**

| técnica | ferramenta do MCP ou Lua | serve para |
|---|---|---|
| deslocar quadros (pulinho, abaixar, mancar) | `tween_cel_positions_eased`, `offset_cel_positions` | Feliz, Chamar, Emburrar, lesão |
| oscilar de lado | `oscillate_cel_positions` | Sacudir, Brincar |
| inclinar e achatar ancorado no pé | Lua (cisalhamento e escala por linha, vizinho mais próximo; a `tween_cel_scale` reamostra pelo centro e tira o pé do lugar) | Comer, a volta do pulo |
| girar | `tween_cel_rotation` | **evitar**: rotação pequena em pixel art serrilha o contorno. O cisalhamento faz o mesmo papel |
| recolorir e escurecer | `adjust_colors`, `remap_colors_in_cel_range` | Emburrar, Fraco (ou só um tom na vista) |
| sobrepor um objeto ou emote numa camada própria | `add_layer` + Lua | a carne, o coração, as bolhas, a nuvem, a nota |
| tempo por quadro | `set_frame_duration` | todos |
| tag e exportação | `set_tag`, `spritesheet_export` (`json_array` com `frameTags`) | todos |

**O que exige desenho quadro a quadro:** qualquer pose que o UP não tem.

- um deitado de verdade para dormir;
- a boca abrindo e mastigando;
- as mãos segurando um objeto;
- de costas;
- a cabeça até o chão nos Digimon altos;
- uma expressão nova (olho fechado de alegria).

O custo estimado é de 30 a 90 min por Digimon e por ação, ou seja 30 a 90 h para os 60 (SEM FONTE). Desenhar pixel a pixel pelo
`draw_pixels` do MCP não chega à qualidade do UP. **Proposta: nada quadro a quadro nesta frente.** O retoque à mão fica possível
depois, porque a fonte é um `.aseprite` (SA-3).

**Custo por programa:**

- **Máquina:** ~1 s por Digimon e por ação, medido na prova. Os 60 Digimon com as 5 ações novas do lote 1 dão ~5 min.
- **Pessoa:**
  - a tabela de âncoras (boca e topo da cabeça): ~1 h para os 60, conferida numa folha de contato;
  - o acerto de cada receita com o Matheus: 1 a 2 h por ação;
  - a aprovação da folha de contato de cada lote pelo Matheus.

**O fluxo:**

1. Para cada Digimon, a receita parte do `remaster/aseprite/<Nome>_v0N.aseprite`, a versão que gerou o `remaster/export/<Nome>.json`
   de hoje (por exemplo `Agumon_v04`).
2. Ela lê a tabela de âncoras e grava `remaster/acoes/aseprite/<Nome>_acoes.aseprite`: as mesmas camadas, uma tag por clipe novo e o
   objeto na camada própria.
3. O Aseprite em linha de comando exporta (`Aseprite.exe -b --script-param ... --script tools/sprites_acoes/gerar.lua`, o mesmo Lua
   da prova; está instalado em `C:\Program Files (x86)\Steam\steamapps\common\Aseprite\`), sem depender do MCP:
   - `remaster/acoes/export/<Nome>.png` e `.json` (`json_array`, `frameTags`, sem trim, caixa igual à do export do UP);
   - uma folha `<Nome>_objeto.png`/`.json` com só a camada do objeto, nas mesmas tags e nos mesmos ms.
4. O `Assets/gerar_atlas_up_clipes.py` (fora do git) lê também o `remaster/acoes/export/` e junta as tags novas a cada sprite do
   `digilab_atlas_up_clipes.json`, com o mesmo empacotamento.
5. **O portão (o Matheus, 2026-11-04: "eu não quero que essas sprites vão direto para o jogo. Eu quero poder ver ele no Atlas, ver
   como é que ficou").** Antes do passo 4, as ações entram no **visualizador do atlas**, uma cópia local da página
   `remaster/fonte/site/atlas_digimon_up.html` com os 60 Digimon das formas:
   - cada Digimon mostra as animações do UP mais `Comer` (com a comida) e `Comer_sem_objeto`, quadro a quadro e com os ms;
   - o visualizador é gerado por `remaster/acoes/visualizador/gerar_site.py` e servido em `http://localhost:8802` (a configuração
     `atlas-acoes` do `.claude/launch.json`);
   - tudo fica fora do git, por serem quadros do UP.

   **O `Assets/digilab_atlas_up_clipes.json` do jogo só é regerado com as ações depois que o Matheus as aprova no visualizador.** Até
   lá ele fica como está hoje, sem `Comer`. Conferido em 2026-11-04.
6. O jogo carrega o atlas como hoje.

### 3.4 O formato de saída

- **As tags novas** no `Clipe` (`atlas.ts`), PascalCase como as do UP:
  - `Comer`, `Feliz`, `Sacudir`, `Chamar` e `Emburrar` no lote 1 (a SA-1 decide);
  - `Brincar` no lote 2, se a vista não bastar.
  - O objeto, quando há, é o clipe `<Tag>_objeto` (por exemplo `Comer_objeto`): os mesmos quadros contados e os mesmos `ms`.
- **Laço:** `Comer`, `Chamar`, `Emburrar` e `Brincar` repetem (`loop: true`). `Feliz` e `Sacudir` tocam uma vez (`loop: false`).
  O Comer do "comeu a ração" é o mesmo clipe tocado uma vez pela vista.
- **Os ms são inteiros e maiores que 0, um por quadro.** O carregador (`juntarClipes`) já falha alto quando `ms.length` difere de
  `quadros.length`. A M2 acrescenta:
  - a falha alto quando um `<Tag>_objeto` não casa com o clipe dele em quadros e em ms;
  - a falha quando uma tag nova aparece num sprite das formas e falta em outro. Ou todas as 60 formas têm o clipe, ou nenhuma; os
    NPCs não precisam.
- **A caixa:** a mesma W×H do export do UP. O gerador já falha quando os quadros de um Digimon têm tamanhos diferentes. A receita
  falha alto se algum pixel opaco cairia fora da caixa (o pulo e a carne precisam caber na folga que o export já tem).
- **O pé:**
  - a receita ancora a escala e o cisalhamento na última linha opaca do `Idle`;
  - nenhum quadro novo tem pixel opaco do personagem abaixo dela;
  - a sombra é a do quadro do `Idle` de origem, sem mudança;
  - um teste do gerador confere as duas coisas.
- **O corte na ilha (`papel.ts`, `Corte`):**
  - o corte de cada sprite continua sendo o do `Idle` mais o do `Run`;
  - os clipes novos usam um corte alargado com o mesmo centro e o mesmo pé, como o `corteGolpe` faz hoje para o `Attack_1`;
  - a M3 generaliza o `corteGolpe` para qualquer clipe fora da locomoção.
  - Assim o papel não pula ao trocar de clipe, e um teste confere: mesmo centro e mesmo pé em todos os clipes do sprite.
- **Sem o atlas** (os e2e e as capturas):
  - um clipe novo cai explicitamente no `Idle` da grade de reserva (`fontePet.ts`);
  - os movimentos que são só vista (pulinho, oscilar, virar) e os sobrepostos de arte própria (grades em `grades.ts`) continuam
    valendo;
  - nada cai calado: a escolha do clipe devolve o clipe pedido, e o desenho registra a queda num campo que o teste lê.

### 3.5 O que não muda

- Nada em `web/app/motor/`, nos gabaritos, no log, no save, no replay nem no Python.
- `git diff origin/main -- web/app/motor web/app/test/gabaritos digilab` vazio em todas as missões.
- O `engine.py` e as versões de pet antigas não mudam.
- A sala 2D dos pets sem mundo (v1–v11) e a reserva sem WebGL (`MundoReserva.tsx`) ficam como estão. A SA-8 decide se a reserva
  ganha os clipes.

### 3.6 As missões

Uma sessão e um PR por missão, em `D:\Trab\digilab\v3-sprites-<missao>`, no branch `v3-sprites-<missao>`, de `origin/main`. Cada
missão tem escopo fechado e entrega verificável.

- **M1 — o Comer no Aseprite (`v3-sprites-receitas`):**
  - **Primeiro, o catálogo das bocas:** para cada um dos 60 Digimon das formas, uma folha com todos os quadros do `.aseprite`
    numerados. A sessão propõe o par aberta e fechada de cada um e marca os que não têm. O Matheus aprova a lista antes da receita
    rodar nos 60.
  - **O que faz:**
    - `tools/sprites_acoes/gerar.lua`: a receita do Comer, a partir da prova 2, versionado. É só código e lê os arquivos do UP pelo
      caminho;
    - `tools/sprites_acoes/ancoras.json`: por Digimon, a sequência de quadros do Comer (boca aberta e fechada) e a ponta do focinho,
      versionado. São números, não imagem;
    - `tools/sprites_acoes/gerar_acoes.py`: chama o Aseprite em linha de comando para os 60, no máximo 4 processos ao mesmo tempo;
    - um teste em Python que confere o pé, a caixa e os ms sobre o export gerado (pula com aviso se o `remaster/` não existe).
  - **Sai fora do git:** `remaster/acoes/aseprite`, `remaster/acoes/export` e as folhas de contato (os 60 × as tags, em 2×).
  - **Entrega:** a folha de contato aprovada pelo Matheus, com o caminho no PR. A M2 só começa depois.
- **M2 — atlas (`v3-sprites-atlas`):**
  - **O que faz:**
    - o `Assets/gerar_atlas_up_clipes.py` (fora do git) junta o `remaster/acoes/export/`. O diff dele vai no corpo do PR, e o
      sha256 do JSON gerado também;
    - `atlas.ts`: as tags novas no `Clipe` e as validações novas do `juntarClipes` (seção 3.4);
    - um teste do carregador com um atlas sintético de arte própria (`test/`), com os casos que passam e os que falham alto.
  - **Entrega:** `npm test` e `npm run tipos`.
- **M3 — tocar o Comer na ilha (`v3-sprites-ilha`; depois do #568 e do #569 na `main`; o #561 já entrou):**
  - **O que mudou na `main` (2026-11-04):** a frente "Vida do pet" pôs o passo 2 como gestos da vista, em
    `src/telas/pet/cenaAcao.ts`:
    - o `gestoAgora` faz o comer achatar e soltar migalhas, com a carne sobre a cabeça;
    - há pulinhos e tremidas por ação;
    - há a reação ao toque (`reacaoAtual`, `ToquePet.tsx`);
    - o `papel.ts` aplica o gesto sobre a folha.

    A M3 parte disso. Ela não cria a `clipePet.ts` paralela, e as regras da SA-5 entram no `cenaAcao.ts`.
  - **O que faz:**
    - no `papel.ts` (`folhaAgora`), com o atlas tendo `Comer`, o pet com `m.acao === "comer"` toca o clipe em laço. A entrada nova em
      `mundo.consumos` toca o clipe uma vez, virado para onde estava a ração (SA-4). O gesto do comer (`estica`) e a carne sobre a cabeça
      saem enquanto o clipe toca, porque o clipe já morde e já traz o `Comer_objeto`;
    - sem o atlas, ou com um sprite sem `Comer`, fica o gesto de hoje: é a queda explícita, e um campo lido pelo teste diz qual dos
      dois tocou;
    - o corte do `Comer` e do `Comer_objeto` é o alargado, com o mesmo centro e o mesmo pé (o `corteGolpe` generalizado);
    - a reação ao dono (a `reacaoAtual` e o `flash`) ocupa um ciclo por cima do Comer e depois volta (SA-5). O mínimo é um ciclo
      inteiro do Comer, mesmo que a ação troque. Acima de 1 h/s, o "comeu a ração" sai;
    - os números novos vão em `ilha/constantes.ts` ou no `CENA_ACAO`, PROPOSTOS.
  - **Testes:**
    - o gesto e o clipe nunca juntos;
    - a queda sem o atlas;
    - o um-ciclo-mínimo e a reação por cima;
    - o corte com o mesmo centro e o mesmo pé.
  - **Entrega:** `npm test`, `npm run tipos`, e o diff do motor vazio.
- **M4 — e2e e capturas (`v3-sprites-e2e`):**
  - **O que faz:**
    - e2e sem o atlas: a queda para o `Idle` e os sobrepostos;
    - e2e com um atlas de clipes sintético servido pela rota (arte própria, com as tags novas), para exercitar os clipes;
    - as capturas locais com o atlas de verdade, 390 e 1280 px: uma por linha do lote 1, guardadas fora do git (são quadros do UP),
      com o caminho no PR.
  - **Entrega:** `npm run e2e` e as capturas para o Matheus aprovar.

**Pela SA-1, a primeira rodada da M1 a M4 é só o Comer.** As outras ações repetem a M1 a M4 depois que o Comer estiver no jogo e
aprovado. A M3 já monta a escolha do clipe com as regras da SA-5, mas só com o Comer e os clipes que existem. A M1 e a M2 podem correr juntas se a M2 usar a prova do Agumon
como entrada. A M3 espera o #561.

## 4. Experimento e gate (se houver run)

Não há run. É só vista. Não há sementes nem plano de análise.

## 5. Entrega

- **Testes:**
  - `python -m pytest tests/test_sprites_acoes.py -q` (a M1);
  - em `web/app`, `npm test`, `npm run tipos` e `npm run e2e` (a M2 a M4).
- **Registro:**
  - os números escolhidos e os desvios vão numa seção própria no fim de `docs/registro/2026-11.md`, com uma linha no fim do
    `docs/REGISTRO_DESVIOS.md`;
  - o resumo de cada missão vai no corpo do PR e numa seção no fim deste documento.
- **PR:** contra a `main`, com o relato pelo `.github/pull_request_template.md` (o CI confere). Merge só pelo Matheus.

## 6. Fora desta tarefa

- **Desenho quadro a quadro:** o deitado, a mastigação e as expressões novas.
- **A recusa (Q-1):** o motor não a dá.
- **O conserto do treino que toca com `enrolou` (A-1):** é uma questão para a frente do treino.
- **As ações novas do cérebro:** são o passo 3 (#565).
- **O som:** os sons do UP são outra frente.
- **Os NPCs e os bots da luta.**
- **A sala 2D dos pets sem mundo.**

## 7. Critérios de aceitação

- **M1:**
  - `tools/sprites_acoes/` com o Lua, as âncoras dos 60 e o orquestrador, versionados;
  - o teste do pé, da caixa e dos ms passa;
  - a folha de contato do lote existe no caminho dado no PR, e o Matheus a aprovou.
- **M2:**
  - o atlas de clipes tem as tags novas nas 60 formas;
  - o `juntarClipes` falha alto nos 3 casos novos, com um teste;
  - o sha256 do JSON gerado está no PR.
- **M3:**
  - cada linha da tabela 3.2 do lote tem um teste da `clipePet`;
  - o teste do corte confere o mesmo centro e o mesmo pé em todos os clipes;
  - o diff de `web/app/motor` e `test/gabaritos` é vazio.
- **M4:**
  - o `npm run e2e` passa, salvo as falhas que já existem na `main`, listadas;
  - as capturas de 390 e 1280 px de cada linha do lote estão no caminho dado no PR.

## 8. Precisa do Matheus

**Decididas em 2026-11-04** (Matheus, nesta sessão):

- **SA-1: "Só o Comer primeiro".** O Comer passa pela M1 a M4 inteira antes das outras ações. Depois vão Feliz, Chamar, Emburrar,
  Sacudir e o `Die` na morte; depois o lote 2 de baixo; por último o treino.
- **SA-3: "Aseprite, no atlas".**
- **SA-5: "Reação por 1 ciclo".**
- **SA-2, SA-4, SA-6, SA-7 e SA-8: "Aprovo todas"**, pela recomendação.
- **Sobre a prova 1:** "tem que fechar e abrir" a boca. Por isso veio a prova 2 (seção 3.3) e a receita por escolha de quadros.

**Aberta:**

- **SA-9 (decidida em 2026-11-04, depois do catálogo da M1).** O catálogo da M1 achou o par de boca aberta e fechada em 11 dos 60
  Digimon. Os outros 49 se dividem assim: 26 sem boca visível, 5 sempre de boca aberta e 18 que só abrem a boca numa pose sem versão
  fechada.
  - **O Matheus decidiu:**
    - "os 8; fracos na prova 1": Agumon, Guilmon (com a carne 2 px à esquerda), MetalSeadramon, Togemon, Gomamon, Patamon, Tanemon e
      Tsunomon abrem a boca. Aquilamon, Garurumon e Palmon vão de prova 1;
    - "desenhar a boca dos 23" (os 18 e os 5): um quadro por Digimon, a pose aberta com a boca fechada pintada por cima, num
      `.aseprite` derivado fora do git (`remaster/acoes/bocas/`);
    - os 26 sem boca vão de prova 1.
  - **Como entra:** os 23 começam com a prova 1 provisória, para o atlas ter as 60 formas. Duas amostras (Greymon e Seadramon) vão ao
    Matheus antes dos outros; se ficarem ruins, ele decide se desenha ele mesmo.

Registro das propostas, como foram levadas ao Matheus:

- **SA-1. Quais ações primeiro.**
  - **Recomendação:**
    - lote 1: Comer (ação comer e "comeu a ração"), Feliz (carinho e brincar do dono), Chamar (chamar atenção e os chamados do
      bebê), Emburrar, Sacudir (limpar), e o `Die` na morte;
    - lote 2: o explorar com o olhar, o Brincar, o Fraco, a lesão e as moscas;
    - lote 3: os 6 exercícios do treino.
  - **Custo de errar:** baixo. É só a ordem.
- **SA-2. Animação por sprite ou genérica por estágio.**
  - **Recomendação:** por sprite, gerada pela mesma receita para os 60.
  - **Por quê:** uma genérica por estágio teria um corpo desenhado por estágio, que não é a cara do pet.
  - **Custo de errar:** a tabela de âncoras (~1 h) se perde se a escolha virar genérica.
- **SA-3. Assar os quadros no Aseprite ou transformar na vista.**
  - **Recomendação:** assar no Aseprite, para o atlas.
    - A fonte é um `.aseprite` que dá para retocar à mão num Digimon que saiu ruim.
    - A prévia é o jogo.
    - O carregador confere.
    - Na vista ficam só o tom e a velocidade (Fraco, Emburrar mais escuro), que não são quadros.
  - **A alternativa** é a mesma receita em TS sobre o quadro do `Idle`, na hora de montar a folha do papel:
    - não mexe no atlas e já vale para a grade de reserva;
    - mas não permite retoque à mão.
  - **Custo de errar:** médio. Trocar depois refaz a M2 e parte da M3, mas as receitas e as âncoras valem para os dois.
- **SA-4. O pet olhando para o objeto.**
  - **Recomendação:** sim para os objetos do mundo (o comedouro ao comer e ao alimentar, a bola), com a mesma regra de lado do golpe
    (`golpe.alvo`). Não para as ações do dono, que seguem de frente para o lado em que estava.
  - **Custo de errar:** baixo.
- **SA-5. A reação ao dono separada da ação do pet, e como coincidem.**
  - **Recomendação:** separadas, a reação por cima. Ela ocupa um ciclo (~0,8 s) e o pet volta ao que fazia. Dormindo, só o tapa e a
    morte trocam o corpo. A duração mínima é de um ciclo. Acima de 1 h/s, saem os momentos do mundo.
  - **Custo de errar:** se a reação for curta demais, o dono não sente o toque; se for longa, o estado do pet some atrás dela. É uma
    constante só.
- **SA-6. A carne na frente da boca no "comeu a ração" da ilha.**
  - **Recomendação:** sim, a camada do objeto com um pedaço da ração. O item 3D some no mesmo instante, e o pedaço continua a cena.
  - **A alternativa:** sem objeto, só a inclinação e a mordida.
  - **Custo de errar:** baixo. É um sobreposto que se liga e desliga.
- **SA-7. A morte com o `Die`.**
  - **Recomendação:** tocar o `Die` uma vez e segurar o último quadro no habitat. Hoje o sprite não muda e só o cartão diz.
  - **Custo de errar:** baixo.
- **SA-8. A reserva sem WebGL (`MundoReserva.tsx`) ganha os clipes?**
  - **Recomendação:** não nesta frente. Ela fica com o primeiro quadro parado e os sobrepostos. Animá-la é trocar o `<img>` por um
    canvas, um trabalho próprio para poucos aparelhos.
  - **Custo de errar:** o dono sem WebGL não vê as ações, como hoje.
- **Q-1 (questão, não decisão):** a recusa não existe nos pets de hoje. A animação dela espera um dado do motor.

## 9. Resumo das etapas

- **2026-11-04, a tarefa (Gerente):**
  - o levantamento em `origin/main`, a tabela 3.2 e as duas provas do Comer do Agumon;
  - as SA-1 a SA-8 decididas, e a SA-9 aberta até o catálogo das bocas da M1.
