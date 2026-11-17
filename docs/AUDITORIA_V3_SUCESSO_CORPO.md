# Auditoria V3: de onde vem o "sucesso" que faz o pet aprender (2026-11-17)

Tarefa: `docs/TAREFA_V3_LEGIBILIDADE.md`, pergunta (a). Código lido: `origin/main` 136e6088, só leitura. Nada foi rodado.
Os números de linha valem nesse commit.

**A pergunta** vem de Dreyfus (2002, p. 376; VERIFICADA, `docs/referencias/v3_dreyfus_referencias_verificadas.csv`): no aprendizado por
reforço, quem define o sucesso é o pesquisador; num agente com corpo, o sucesso deveria ser a satisfação do próprio agente. Aqui se
pergunta, sinal por sinal, de onde vem o que faz cada cérebro aprender.

**As classes:**
- **CORPO:** sai de uma variação dos receptores do corpo químico;
- **MUNDO:** um evento do mundo sem passar pelo corpo;
- **DONO:** um gesto do dono;
- **PROJETISTA:** uma constante ou tabela nossa, sem origem no estado do corpo;
- **MISTO:** a composição vai descrita na linha.

**O método:**
- A tabela foi levantada por um subagente de leitura (Opus 5.5).
- As linhas centrais foram conferidas à mão: `adapt.py:622-625`, `adapt.py:769-771`, `afeto.py:139-147`, `lobos.py:1110-1116`,
  `config.py:1182` e `config.py:2799`.
- As demais linhas são do levantamento e não foram reconferidas uma a uma.
- A paridade Python × TypeScript não foi conferida além das constantes do jogo.

## 1. A resposta curta

- **No modular, o sucesso vem do corpo.**
  - Todo parâmetro aprendido no modular é movido pela variação dos receptores do corpo, numa janela que vai da percepção da decisão até
    logo depois dos estímulos da ação, no mesmo tick (`motor_corpo.py:412-447`).
  - O sinal central é `r = ganho_r · Σ (falta(antes)² − falta(depois)²)` sobre fome, higiene, energia, humor, saúde, tédio, curiosidade,
    solidão, estresse e dor (`afeto.py:139-146`).
  - O mundo decide só **quando** e **em que classe** gravar.
- **O dono não é sinal de aprendizado no modular.** O `receber_acao_dono` só registra o gesto (`adapt.py:622-625`). O carinho e o tapa
  acontecem entre decisões, fora da janela do r. A exceção é a subchave `fala_unidades`, que só o pet de teste "fu" liga.
- **Mas a direção da variação do corpo é nossa.** Isto é o que Dreyfus apontaria.
  - O quanto cada ação muda o corpo sai de tabelas fixas: comer ração dá fome +0,45; explorar, humor +0,01; emburrar, humor −0,01
    (`corpo.py:427-471` e os emissores `corpo.py:561-603`). Essas tabelas são PROPOSTAS e SEM FONTE (`corpo.py:219-245`).
  - O único pedaço que é do estado do pet é o peso que a falta de agora dá a essa mudança.
  - **A satisfação é do pet; o que satisfaz, decidimos nós.**
- **O A sai do jogo.** O Matheus avisou em 2026-11-17 que o cérebro A está fora do jogo e que outra frente o retira e deixa só o
  modular (a LIMPEZA, `docs/TAREFA_V3_LIMPEZA.md`). Na `main` 136e6088 o código ainda existe (`web/app/motor/pet_v11.ts`), por isso a
  seção 4 fica como registro histórico, e a conclusão desta auditoria vale para o modular, o único cérebro do jogo.
- **O A do jogo (o v11, em Ajustes, de saída) misturava:**
  - aprende pelo corpo (o sinal dos drives);
  - aprende pelo carinho medido no corpo;
  - aprende pelo tapa como **constante −S**, um valor do projetista que ignora de propósito o que o tapa faz no corpo (`lobos.py:1110-1116`).
- **No Python, o A não aprende no padrão** (`aprendizado_ligado=False`, `config.py:1182`). O modular também está desligado no padrão do
  Python (`ConfigDigibrain.ligada=False`, `config.py:2799`): ele só existe ligado na bancada e no jogo.

## 2. A contagem nos sinais ligados

| cérebro | CORPO | MUNDO | DONO | PROJETISTA | MISTO |
|---|---|---|---|---|---|
| modular, ligado na bancada do Python (`p1`, `p2`, `m_mem`, `persistencia`) | 4 | 1 | 0 | 0 | 3 |
| modular do jogo (`VERSAO_PET` 38, `web/app/motor/constantes.ts:71-90`, `:124`) | 6 | 2 | 0 | 0 | 4 |
| A, padrão do Python (sai na LIMPEZA) | 0 | 0 | 0 | 0 | 0 |
| A do jogo (v11, `web/app/motor/pet_v11.ts:8-15`; fora do jogo, retirada em curso) | 1 | 0 | 1 (valor do PROJETISTA) | 0 | 1 (o DONO dispara, o CORPO mede) |

## 3. O modular, sinal por sinal

| # | sinal (cálculo → atualização) | o que muda | origem |
|---|---|---|---|
| M1 | r e r_n: `afeto.py:139-146`, chamado de `adapt.py:729` | alimenta M2, M3, M6, M7, M8 e M14 | **CORPO**. `ganho_r`=4 é PROPOSTO ("o do A"); `r_norm`=2 é PROPOSTO, SEM FONTE |
| M2 | valência V: `afeto.py:147` | V, que entra no estado z | **CORPO** (pelo r_n). `tau_v` é PROPOSTO, SEM FONTE |
| M3 | excitação E: `afeto.py:148-149` | E, no estado z | **CORPO** |
| M4 | P1, o desfecho: `plast.py:126-137`, chamado de `adapt.py:744-750` | o modelo do que cada consumo faz (`d[classe, receptor]`) | **MISTO**: o alvo é a variação dos receptores (CORPO); a classe e o gatilho são o "comeu" e o "brincou com a bola" (MUNDO, `plast.py:4-8`) |
| M5 | P1, o custo de andar: `plast.py:106-109` | `andar` | **MISTO**: energia (CORPO) e distância (MUNDO) |
| M6 | P2, o hábito: `estado.py:355` e `plast.py:140-155` | `H[comportamento, j]` | **CORPO** (r_n). O fim da opção é uma regra nossa, mas não soma recompensa (`estado.py:350-377`) |
| M7 | M-MEM, o lugar lembrado: `adapt.py:764-771` → `mem.py:213-227` | episódio e valor do lugar | **MISTO**: no consumo, r_n (CORPO); a visita vazia leva **r = 0 por regra** (`adapt.py:769-771`, PROJETISTA) |
| M8 | memória autobiográfica: `mem.py:88-121` → `mem.py:240-260` | episódio e σ | **CORPO**. Na visita vazia vale σ = min(0, r_ida), por regra (`mem.py:100`, PROJETISTA) |
| M9 | facetas: `adapt.py:553-565` → `pers.py:44-61` | cautela, apego, ousadia | **MISTO**: σ (CORPO), sentido da tabela `SENTIDO` (`pers.py:22`, PROPOSTO, SEM FONTE). Desligada nos dois padrões |
| M10 | luta: `afeto.py:153-158` e `adapt.py:538-551` | episódio de luta | **CORPO**. No jogo, não foi confirmado em que pets liga |
| M11 | habituação por classe: `sens.py:355-361` | novidade | **MUNDO**, sem valência |
| M12 | `gosto_visual`: `adapt.py:722` e `:725`, somado ao r em `afeto.py:141-145` | o r da opção de olhar | **MISTO**: um pico contra o ótimo do genoma da visão (`sens.py:217-226`), calculado **dentro do cérebro**, não por receptor. Com `agrado_no_corpo`, entra também pelo humor e pesa duas vezes (leitura do código, não medido) |
| M13 | exposição: `sens.py:233-250` | o deslocamento do gosto | **MUNDO** |
| M14 | gosto por conceito: `sens.py:155-164` | `gosto_conceito` | **MISTO**: exposição (MUNDO) mais consequência (CORPO). O órgão está desligado |
| M15 | habituação por conceito: `sens.py:387-391` | `hab_conceito` | **MUNDO** |
| M16 | enjoo lembrado da TV: `adapt.py:470-477` | `enjoo_tv` | **CORPO** (o receptor `enjoo_tela`) |

**Ligados:**
- na bancada do Python: M1-M7 e M11;
- no jogo (v38): M1-M8, M11, M12, M13 e M16.

O ganho do aprendizado fica constante (`modula_g_apr=False`, g0 = S, `afeto.py:119-120`).

## 4. O A, sinal por sinal (registro histórico)

O A está saindo do jogo (seção 1). A tabela fica porque o código ainda está na `main` 136e6088 e porque o tapa constante (A6) é o
exemplo mais claro de sucesso definido pelo projetista. Nada desta seção vale para o pet do jogo depois da retirada.

Todos os sinais do A caem em `_creditar` (`lobos.py:1492-1501`), com a mesma regra de atualização dos pesos (`lobos.py:461-512`).

| # | sinal | origem | ligado no v11 do jogo? |
|---|---|---|---|
| A1 | N3 sem corpo: `lobos.py:2719-2732` | **CORPO** (o vetor de estado) | não (só sem o corpo químico) |
| A2 | sinal pelo corpo: `lobos.py:1397-1430` | **CORPO**, sem humor e sem saúde | **sim** |
| A3 | E2, humor da fruta: `lobos.py:2735-2749` | **MISTO**: humor (CORPO) só quando comeu fruta (MUNDO); DECIDIDO pelo Matheus em 2026-10-04 | não (a fruta chega como ração) |
| A4 | paladar: `lobos.py:2864-2873` | **MISTO**: receptores do paladar (CORPO) com os pesos do genoma | não |
| A5 | carinho ("Elogiar" na tela): `lobos.py:1130-1157` | **MISTO**: o DONO dispara, o CORPO mede, creditado à última decisão por regra nossa | **sim** |
| A6 | tapa ("Repreender" na tela): `lobos.py:1110-1116` | **DONO**, com valor constante −S do **PROJETISTA**; a dor e o susto ficam fora de propósito | **sim** |
| A7 | elogio e bronca diretos: `lobos.py:1101-1109` | **DONO**, ±S constantes (PROJETISTA) | não |
| A8 | latência do chamado: `lobos.py:1121-1128` | **MISTO**: tempo do dono, fórmula nossa | não |
| A9 | chamado ignorado: `lobos.py:1159-1168` | **PROJETISTA**, constante −S/2 | não |
| A10 | traço de elegibilidade: `lobos.py:1495-1501` | herda a origem | não (`traco=0`) |
| A11 | N6, valência da fruta: `lobos.py:1240-1244` | **CORPO** (humor) | não |
| A12 | ModeloMundo do pet que pensa: `lobos.py:1285-1286` | **MISTO**, como M4 | não (`g_plano=0`) |

## 5. Onde o sucesso é regra nossa mesmo parecendo vir do corpo

1. **As tabelas de ação** (seção 1): o r do modular e o A2 do A leem uma mudança do corpo cuja direção e cujo tamanho nós escrevemos.
2. **O `gosto_visual`** (M12) não passa por receptor.
3. **A visita vazia tem valor fixado** (M7: r = 0; M8: σ ≤ 0).
4. **O tapa era constante no A** (que sai do jogo), e o carinho medido no corpo. O modular não aprende com nenhum dos dois.
5. **O A escolhia o que conta:** humor e saúde ficavam fora dos drives, salvo a fruta no E2. O modular inclui os dois.
6. **No P1 (M4), o mundo escolhe o que se aprende:** só o comer e a bola atualizam o desfecho.

## 6. O que isto autoriza dizer, e o que não

- **Autoriza:**
  - No modular do jogo, nenhum sinal de aprendizado é uma recompensa fixa por ação.
  - Todos passam pela variação dos receptores do corpo, menos o `gosto_visual` e os sinais de exposição e de habituação, que não
    têm valência.
  - O dono não ensina o modular diretamente. Ele muda o corpo e o mundo do pet.
- **Não autoriza:** dizer que o sucesso é "do pet" sem a ressalva da seção 5.1. As tabelas que dizem o que cada ação faz ao corpo são
  nossas, PROPOSTAS e SEM FONTE. É exatamente a objeção de Dreyfus deslocada um passo: em vez de definirmos a recompensa, definimos o
  corpo que a produz.
- **Consequência para o plano de legibilidade** (`docs/PLANO_ANALISE_V3_LEGIBILIDADE.md`): como o modular não aprende com o gesto do
  dono, a pergunta aos avaliadores não pode dizer "aprendeu com o dono". O plano usa "aprende com o que acontece com ele".
- **O que esta auditoria não decide:** se alguma tabela deve mudar. Isso é desenho e fica para o Matheus. Não há nenhuma decisão
  pendente aqui.
