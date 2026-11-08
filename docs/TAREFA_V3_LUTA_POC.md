# TAREFA V3 — LUTA_POC (2026-11-08)

Coordenador: o Gerente de sprites e luta (Claude Code, Opus 5.5). Worker da LP0: o próprio Gerente, a pedido do Matheus ("Sim, faz
aqui"). Worktree e branch: `v3-luta-poc`. Status: PROPOSTA (a seção 8 fica com o Matheus).

Categoria: arquitetura. Origem: Matheus, 2026-11-08. Ele olhou a luta do jogo e escreveu:
- "ele não tá como se fosse um sistema de batalha em tempo real, ele parece um por turno camuflado";
- "os golpes que são à distância … parecem todas corpo a corpo. Eu quero que tenha realmente um projétil e vá atacar e acertar o inimigo.
  Por exemplo, a rajada do Gabumon";
- "Eu não quero esse combate por turno, eu quero o combate em tempo real, igual o da POC. Revisa em todos os lugares onde está citando
  esse combate por turno e apaga";
- "Não tem problema que o sistema de batalha tá impregnado dentro do motor. Da tela, as ligas e fábricas. Qualquer coisa a gente tira
  essas questões. Mas o combate em tempo real é mais importante";
- "Combate em tempo real, incluía até diversos mapas".

## 1. Pergunta

Como a luta do jogo passa a ser a simulação em tempo real da POC da arena, com o golpe e o tempo próprios de cada Digimon, projéteis de
verdade, o chão 2D e os 8 mapas? E como o combate por turnos (as regras V2.1 com o relógio de 2 s) sai do motor, das telas e dos
documentos, sem quebrar o replay nem o resto do pet?

A tarefa é de produto (a trilha B, batalha), não uma hipótese de pesquisa. Esta etapa, a **LP0**, é só papel: o diagnóstico, o
inventário, a espec e as etapas. Nenhum código muda nela.

## 2. Depende de

- **A POC original:** `D:\Trab\digilab\remaster\fonte\scripts_arena\arena_pub.html` (fora do git), com os dados do Digimon UP ao lado:
  `golpes.json` (270 Digimon), `golpes_prefabs.json`, `ataques.py`, `harness_equilibrio.js` e `harness_equilibrio_resultados.txt`. Os
  dados de jogo gerados ficam em `D:\Trab\digilab\Assets\arena_up\` (`Assets/gerar_arena_up.py`, 512 arquivos, com o `manifesto.json`).
- **O porte da POC, no histórico do git:** a pasta `web/app/arena/` (11 arquivos, 1 030 linhas) do #446 e do #448, apagada no #456. O
  commit `efb2ded` ainda a tem inteira, com `arena_gabarito_prototipo.json`, `medir_arena.ts` e os testes `arena*.test.ts`.
- **As decisões da seção 8.** A LP1 só começa com a LP-1 a LP-4 decididas.
- **A rodada 3 do equilíbrio fica PAUSADA** (Matheus, 2026-11-08: "Sim, pausa a R3"), depois da R3-0 (#720, aberto).

## 3. O diagnóstico, a espec e o inventário

### 3.1 Por que a luta de hoje parece por turnos

A arena da POC entrou no jogo em 2026-10-29, atrás da chave `ARENA_TEMPO_REAL` (#446), e o pet passou a lutar sozinho nela (#448). No
mesmo dia, a espec da COMBATE_TR (#449, `docs/ESPEC_COMBATE_TR.md`) escolheu **não** usar a simulação da POC no jogo. Ela manteve as regras
do combate por turnos V2.1 e trocou só o relógio. O núcleo que saiu disso é o `web/app/motor/combate_tr/` (652 linhas). Nele:

| o que | na luta de hoje (`combate_tr`) | na POC (`arena_pub.html` e `web/app/arena/`) |
|---|---|---|
| a duração da ação | **2 s para todos** (`T_TR` = 125 passos, a D-5): é o turno com outro nome | o ciclo de cada Digimon (`cad`) e a duração do clipe dele |
| o instante do golpe | **400 ms para todos** (`CTR_TR.instante`, a D-1) | o do script do Digimon (`golpes.json`, `t` de 0,4 a 0,6 s) |
| o que se escolhe | as ações genéricas do combate por turnos (`golpe_rapido`, `fintar`, `pesado`, `disparo`, `investida`, `esquivar`…) pelas regras do `decidirV2` e pelos gambits | andar, mirar, atacar com o golpe próprio, usar a habilidade quando a recarga deixa, desviar dos projéteis, contornar obstáculos |
| o chão | uma linha reta (1D) | uma elipse 2D, com obstáculos que bloqueiam corpos e tiros |
| os projéteis | só a ação genérica `disparo` cria um, e a vista pinta a cor do elemento; os outros golpes ganham um brilho de 4 quadros no acerto (a "rajada" da E2) | 175 dos 270 golpes têm o projétil do próprio jogo (o prefab, o tipo e a velocidade); o voo é simulado e pode errar ou ser desviado |
| os mapas | o mapa do lugar só como fundo, sem regra (E7) | 8 cenas com regras próprias (seção 3.3) |
| o equilíbrio | 27 metas das rodadas R2 e R3, calibradas sobre as regras por turnos | os números do `arena_equilibrio.md` (duas rodadas, 2026-10-29) |

**O Gabumon.** Nos dados do Digimon UP, o golpe do Gabumon não tem projétil (`proj: null`): o fogo aparece só no alvo
(`Fx_Gabumon_Attack_Hit`), e a habilidade é o mesmo golpe. Para a rajada dele voar até o inimigo, o projétil precisa ser feito por nós
(a LP-8).

### 3.2 A espec da luta nova

**O núcleo é a simulação da POC.** A pasta `web/app/arena/` volta do commit `efb2ded` para dentro do motor (`web/app/motor/arena/`, a
LP-1), com quatro mudanças e nada mais:
1. **A aritmética do replay** (a D-7, que continua valendo): hoje a POC usa `Math.hypot` (25 vezes) e `Math.sin` (3 vezes), que podem dar
   resultados diferentes entre navegadores. O `hypot` vira `Math.sqrt(dx*dx + dy*dy)`, e o `sin` vira uma tabela fixa no código (ou um
   polinômio). Um teste pela fonte confere que o núcleo não usa outra função de `Math` além de `sqrt`, `min`, `max`, `floor`, `ceil`,
   `round` e `abs`.
2. **Os dados que a luta lê entram no git como números** (a LP-2): o replay não pode depender da pasta `Assets/`.
3. **O pet é o lado azul, sozinho, 1 contra 1**, pela IA da arena (como no #448), sem botão durante a luta. O modo "Você × CPU", o
   teclado, o mouse e as equipes de 3 não voltam.
4. **A entrada do DigiLab** (a LP-3): a dificuldade da IA de cada lado deixa de ser um botão e passa a sair do pet (o treino, a
   experiência de luta, o estágio).

**O que vem da POC sem mudar a regra:**
- o golpe e o tempo próprios de cada Digimon (o `t` do golpe, a duração do clipe `Attack_1`, a habilidade com recarga `hcd` e força
  `hpot`);
- os projéteis em voo, que acertam o primeiro inimigo que cruzam, somem fora do alcance, são bloqueados por árvores e rochas e podem ser
  desviados (a IA desvia com a chance e o tempo de reação da dificuldade);
- o movimento 2D: aproximar, recuar quem atira de perto, rodear o alvo, contornar obstáculos, fugir das zonas de perigo;
- o empurrão de cada golpe, o atordoamento, o crítico, a esquiva, o triângulo de atributos (Vaccine, Virus, Data);
- os 8 mapas, com as regras deles (seção 3.3).

**O determinismo e o replay.** A POC já foi portada com passo fixo de 16 ms, um fluxo de RNG por uso e o resultado igual para a mesma
semente (o #446 reproduziu exatamente todas as tabelas do harness). O log do pet guarda a entrada da luta (o pet, o rival, o mapa, a
semente e o "nível de luta" de cada lado), e o replay refaz a luta. A troca de `hypot` e `sin` pode mudar os últimos dígitos; por isso o
teste de fidelidade da LP1 compara o núcleo novo com o gabarito do harness em distribuição (as mesmas tabelas, com a diferença
registrada), e o teste de replay passa a ser bit a bit sobre o núcleo novo.

**O custo do replay.** Na medida da R0 da COMBATE_TR (#449, `web/app/scripts/medicoes/replay_tr.json`, que saiu no #456 e está no
`efb2ded`), a simulação da POC custou 1,19 ms por luta 1 contra 1 no Node (29,6 s de jogo), e a luta de 100 s do desenho por turnos,
4,66 ms. Uma vida com 1 000 lutas refaria em ~1,2 s no Node, SEM FONTE no celular. A medida volta na LP2, com o núcleo novo.

### 3.3 Os mapas

A POC tem 8 mapas (`web/app/arena/cenas.ts` em `efb2ded`), cada um com uma regra:

| mapa | a regra (da POC) |
|---|---|
| Campo de treino | sem regras: os dois lutadores e o chão |
| Coliseu | a partir de 30 s, a área segura encolhe até 50 % em 30 s; fora dela, 5 % da vida máxima por segundo |
| Floresta Green Shade | árvores bloqueiam corpos e projéteis; dentro de uma moita, o lutador fica escondido e a mira erra 4 vezes mais |
| Praia Shellfish | a maré sobe e desce a cada 18 s; na água, o movimento cai para 70 %; as rochas bloqueiam |
| Deserto Endless | o centro puxa e deixa lento; a cada 20 s, uma tempestade de 6 s (projéteis a 60 %, mira 3 vezes pior) |
| Castelo Midnight | 4 pilares bloqueiam projéteis e quebram com 3 golpes; 1,2 s na runa do centro dá +30 % de dano por 8 s |
| Caverna Blackheart | lava custa 6 % da vida máxima por segundo; a cada 7 s, duas erupções (10 % da vida máxima perto) |
| Ringue D-1 Grand Prix | sem cerca; os golpes empurram o dobro; quem sai perde 15 % da vida máxima e volta atordoado |

Cada lugar de luta do jogo usa um desses mapas (a LP-4). Os números são os da POC, PROPOSTOS, SEM FONTE de medição além do
`arena_equilibrio.md`.

### 3.4 O inventário: onde o combate por turnos vive

O levantamento foi feito em 2026-11-08 na `origin/main` (`e654891`), por nome de símbolo, porque tudo fora do motor importa pelo
`web/app/motor/index.ts`. As contagens são aproximadas. O destino de cada linha segue a seção 5.1 e as decisões da seção 8.

**O núcleo e as regras por turnos (web, 11 arquivos): saem na LP4.**

| arquivo | o que tem | destino |
|---|---|---|
| `motor/combate_tr/` (`luta.ts`, `controlador.ts`, `adaptador.ts`, `constantes_tr.ts`, `index.ts`, 652 linhas) | o núcleo de 2 s por ação: `criarLutaTR`, `passoTR`, `jogarTR`, `decidirTR`, `jogarLuta`, `RELOGIO_V13/14/18`, `FATORES_V14`, `APRENDIZADO_V14`, `LISTAS_LIDER_V14`, `CARTAS_V14`, `CHIP_ANTES_V14` | **apagar**, trocado pelo `motor/arena/` |
| `motor/combate.ts` (130) | `ACOES_V2`, `regrasDaVersao`, `ehV14`, `Lutador`, `ResultadoLuta`, `comCarta`, `CONDICOES_ESTAGIO`, `Desafiado` | **apagar** as regras; o `ResultadoLuta` vira o resultado da luta nova |
| `motor/gambits_pet.ts` (447) | o `GambitsPet` (as notas por regra, os disparos, as travas, os vetos, os chips, a reserva, o `aprendizadoTR`), o `lutadorPet`, o `estiloDoPet` | **apagar** (LP-3); o "nível de luta" do pet entra no lugar |
| `motor/bots.ts` (327) | as listas de regras dos rivais (`BOTS_V2/V21/V21D/V21E`, `LISTAS_V14`, `GAMBITS_ARENA/SOMBRIA`), os NPCs, a `CAMPANHA*` e os `LUGARES*` | **adaptar**: os rivais passam a ser um Digimon, um nível e um mapa; as listas de regras saem |
| `motor/constantes.ts` (532), `catalogo.ts` (125), `tipos.ts` (122) | `CV`, `CV21`, `CV21E_TR*` e as `VERSAO_V14…V19`; o `CATALOGO_V2` das formas; os eventos `"l"` e `"pl"` | **adaptar**: saem os números das regras por turnos; ficam o catálogo das formas (a evolução lê dele) e os eventos |

**Os consumidores no motor (web, 15 arquivos).**

| arquivo | o que usa | destino |
|---|---|---|
| `motor/motor.ts` (1 292) | `lutar`, `_lutar`, `montarLuta`, o `gp.aprender`, os chips, as cartas, o resumo da luta para a ponte; o evento `"l"` (linha 525) e o replay (linha 1243) | **adaptar** na LP2: a luta do pet chama o núcleo novo; saem os chips, as cartas e o `gp` |
| `motor/arenas.ts` (138) | `jogarLuta`, `GAMBITS_ARENA`, `comCarta`, `FATORES_V14` | **adaptar** (a Campanha e os líderes, LP-5) |
| `motor/medalhas.ts`, `nomes.ts`, `expressao.ts`, `motivo.ts` | a `CAMPANHA_V6`, os NPCs, o `NOME_V2` e o `CATALOGO_V2` | **adaptar** só o que cita as regras; os nomes e o catálogo ficam |
| `motor/liga.ts`, `fabrica.ts`, `salao.ts`, `instalacoes.ts`, `itens.ts` | `jogarLiga`, `jogarLuta`, `gambitsAdulto`, as cartas e os chips | **apagar** na LP4 (LP-5) |
| `motor/corpo.ts`, `motor_corpo.ts`, `digibrain/adapt.ts`, `digibrain/mem.ts` | a dor da luta (`ConfigLutaCorpo`, `aplicarResumoLuta`), o `receber_luta` e os episódios da luta (PONTE_LUTA) | **adaptar** na LP2: o resumo passa a sair do resultado novo (o dano recebido, o fim, a duração) |

**As telas (web, ~40 arquivos).**
- `src/telas/lutar/palcoTR/` (10 arquivos, o palco 1D com os efeitos E1–E5): **trocar** na LP3 pelo palco 2D; o que couber dos efeitos é
  portado.
- `src/luta.ts` (551), o motor das telas de luta (`lutarAnimado`, o replay pelo `res.tr.entrada`): **adaptar**.
- `src/telas/lutar/` (`TelaLuta`, `TelaArena`, `TelaCampanha`, `TelaMedalhas`, `ModalResultado`): **adaptar**. `EditorRegras`,
  `PainelAprendizado`, `TelaFronteira`, `FabricaSalao` e `src/aprendizadoLuta.ts`: **apagar** (LP-3, LP-5).
- `src/fronteira.ts`, `src/tamer.ts` (os eventos `fabrica`, `fabrica_luta`, `fabrica_troca` e `salao` do Tamer): **apagar** a Fábrica e
  o Salão; o Tamer guarda as medalhas e os recordes (LP-6).
- Os outros que citam a luta: `TelaItens` e `EscolhaCarta` (os chips e as cartas: **apagar**); `TelaEvolucao`, `TelaCatalogo`,
  `TelaRegistro`, `MeusPets`, `TelaPet`, `LinhaAgora`, `Jornada`, `DigiBrainLab`, `TelaCenarios` e os lugares da ilha (`lugares`,
  `marcadoresLugar`, `vista`, `CadeadosDaIlha`, `ObjetosDaIlha`): **adaptar** o que lê as regras ou a duração da luta.

**Os testes e os scripts (web).**
- Unidade (~45): `combate_tr*`, `luta_efeitos_e1…e5`, `luta_empurrao*`, `luta_tela`, `luta_tr_hoje`, `limite_desafiado`, `listas_v14`,
  `pet_v14`, `aprendizado_luta`, `vigia_candidatas`, `progressao_v9`, `liga`, `fabrica_salao`, `fronteira_itens_v9`, `instalacoes`,
  `itens`: **apagar** com o que testam. `arenas`, `lab_cenarios`, `confianca`, `lobos_v11`, `evolucao_canonica`, `pet_lab`, os
  `ponte_luta_pe0/pe3/pe4` e o `digibrain_modular_vida`: **adaptar** e **regravar o gabarito na versão nova**; os gabaritos das versões
  antigas saem com elas (LP-6).
- A paridade com o Python: o `constantes.test.mjs` deixa de comparar `CV` e `CV21` (LP-7); os gabaritos `combate_v21d_python.json` e
  `combate_v21e_python.json` já não são lidos por nenhum teste da web.
- e2e: os 7 `luta_*.spec.ts`, o `ponte_luta.spec.ts`, o `jogo.spec.ts` e os `gerar_save_*` que gravam lutas nos saves: **adaptar** na LP2 e
  na LP3.
- Scripts: `scripts/equilibrio_tr/` (8) e `scripts/gerar_gabarito_vidas_v13.ts`: **apagar** na LP4; as saídas em
  `scripts/medicoes/equilibrio_tr/` ficam no histórico do git.

**O log e o replay.**
- O evento `"l"` guarda só o rival e a semente (`{r, s}`); o resultado nunca é salvo, ele é refeito. Por isso qualquer mudança no núcleo
  muda o replay e a assinatura dos pets que já lutaram, e o núcleo novo precisa de uma versão nova (LP-6).
- Os eventos `"k"` (as cartas), `"g"` (as intervenções nas regras) e `"i"` (os itens e os chips) saem com o que registram, numa versão
  que não os aceita: evento desconhecido levanta erro.
- Os ramos por versão: `regrasDaVersao` (a v13 no `CV21E_TR`, a v14–v17 no `CV21E_TR14`, a v18–v19 no `CV21E_TR18`), `ehV14`,
  `relogioDe` e os `m.versao >= …` do `gambits_pet.ts`. Saem com as versões antigas.

**O Python (fica, congelado: LP-7).** O `digilab/combate_v2/` e o `v21/` (~2 400 linhas) espelham o combate por turnos V2.1, que a web
tirou no #456. Ninguém espelha o `combate_tr` no Python. O combate do Python é usado pela pesquisa (`campanha.py`, `educacao.py`) e o
catálogo das formas dele pela evolução (`evolucao.py`, `expressao.py`, `memoria.py`, `vinculo.py`); 22 arquivos de `tests/` e ~15 de
`experiments/` dependem dele. A ponte da luta no Python (`corpo.py`, `motor_corpo.py`, `mundo.py`, `digibrain/`) recebe só um resumo, e o
formato do resumo fica. O `digilab/arena.py` é a arena antiga da Etapa 4 (pedra, papel e tesoura) e não tem relação com esta tarefa.

**Os documentos.** Os registros (`docs/registro/`, `docs/historico/`) não se apagam: o G-NADA-PERDIDO os protege. Na LP4 recebem, no
topo, a linha "SUBSTITUÍDO pela `docs/TAREFA_V3_LUTA_POC.md` (2026-11-08): a luta do jogo é a simulação da POC":
- `docs/ESPEC_COMBATE_TR.md`, `docs/TAREFA_V2_COMBATE_TR.md`, `docs/TAREFA_V3_COMBATE_V14.md`;
- `docs/PLANO_EQUILIBRIO_COMBATE_TR.md`, `_R2.md`, `_R3.md` e `docs/EQUILIBRIO_COMBATE_TR.md`;
- `docs/TAREFA_V3_LUTA_EMPURRAO.md` e, só na parte do palco 1D, `docs/TAREFA_V3_LUTA_EFEITOS.md`.

São **reescritos** onde descrevem o jogo de hoje: a linha B do `docs/PAINEL_V3.md`, a trilha B do `docs/PLANO_V3.md` (seção 4), a
`docs/TAREFA_V3_PONTE_LUTA.md` (o resumo que a luta nova entrega), o `docs/DESIGN_MEDALHAS_ARENAS.md` e o `docs/MAPA_REPOSITORIO.md`. O
`ESPEC_COMBATE_V2.md` e o `ESPEC_COMBATE_V21.md` ficam como estão: descrevem o Python.

## 4. Experimento e gate

Não há run nesta etapa. A medida de fidelidade da LP1 (o núcleo novo contra o gabarito do harness) e o custo do replay da LP2 são
medições de engenharia, com os testes de 101…505. O equilíbrio fica para o fim (a LP-9).

## 5. Entrega

- **LP0 (esta):** este documento, uma seção em `docs/registro/2026-11.md` e um PR contra a `main` no modelo
  `.github/pull_request_template.md`. Nenhum código muda. O merge é do Matheus.
- **Cada etapa LP1…LP5:** um PR, com `npm test`, `npm run tipos` e `npm run e2e` em `web/app` e as contagens no corpo; as capturas da LP3
  vão para a aprovação do Matheus antes do PR.

### 5.1 As etapas

| etapa | o que entra | o que sai |
|---|---|---|
| **LP1: o núcleo** | `web/app/motor/arena/`, de volta do `efb2ded`, sem DOM, com a aritmética da D-7 e a tabela de números da LP-2 (o script que a gera fica em `Assets/` ou `tools/`); o teste de fidelidade contra o gabarito do harness, o teste pela fonte da aritmética, o replay bit a bit. Atrás de chave desligada: o jogo não muda | nada |
| **LP2: o pet luta no núcleo novo** | uma `VERSAO_PET` nova; a entrada da luta no log; o "nível de luta" do pet (LP-3); a Arena e a Campanha lutam no núcleo novo; a ponte com o DigiBrain (a dor e o episódio da luta, PONTE_LUTA) lê o resultado novo; o aviso dos pets antigos (LP-6); a medida do custo do replay | o caminho do `combate_tr` para a versão nova; os lugares cortados pela LP-5 somem da navegação |
| **LP3: a tela** | o palco novo em 2D, a partir do desenho do #446/#448 (`web/app/src/telas/lutar/arena_tr/desenho.ts` em `efb2ded`): os 8 mapas, os projéteis com o desenho do jogo (os prefabs de `Assets/arena_up/efeitos`), o projétil do Gabumon e dos outros sem projétil (LP-8), o que couber da LUTA_EFEITOS (o impacto da E1, o nocaute e a câmera da E5); capturas no desktop e no celular, para aprovação | o `palcoTR/` (o palco 1D) |
| **LP4: a limpeza** | os documentos de cada coisa que saiu marcados como SUBSTITUÍDOS, com o link para esta tarefa | o `combate_tr/`, as regras por turnos e o que só servia a elas (o inventário da seção 3.4), os testes e os scripts de equilíbrio delas, os lugares cortados pela LP-5 |
| **LP5: o equilíbrio** | uma rodada só, no fim, com plano de análise e faixas novas (a regra "equilíbrio só no fim") | as metas R2 e R3 |

A LP3 pode correr ao lado da LP2 numa worktree própria, porque só toca a tela; a LP4 espera as duas.

## 6. Fora desta tarefa

- O combate do Python (`digilab/combate_v2`, `arena.py`, `campanha.py`): é a pesquisa da v1 e da V2, com resultados publicados no
  repositório sobre ele. Fica congelado como está (a LP-7); a luta nova é só da web, como a D2 da UP-ARENA.
- O controle do jogador durante a luta: "é o pet lutando sozinho" (#448).
- As equipes de 3 e as trocas da POC: o pet luta sozinho.
- Os números de equilíbrio: só na LP5.

## 7. Critérios de aceitação (da LP0)

- Este documento está no PR, com o inventário da seção 3.4, a espec da seção 3.2, as etapas da seção 5.1 e a tabela de decisões da
  seção 8.
- `git diff origin/main --stat` só mostra documentos.
- `python tools/conferir_saude.py` passa.

## 8. Precisa do Matheus

Tudo PROPOSTO. Cada linha tem a recomendação e o custo de errar.

| # | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **LP-1** | O núcleo da luta passa a ser a simulação da POC, de volta do `efb2ded` para o motor, e o `combate_tr` sai | **Sim.** Volta o `web/app/arena/` como `web/app/motor/arena/`, com só as quatro mudanças da seção 3.2 | Reescrever do zero perde a paridade com o harness, que é a prova de que é a POC; manter os dois núcleos dobra os testes e o equilíbrio |
| **LP-2** | Os dados que a luta lê (o status, o golpe, o tempo do clipe, o projétil, o atributo) entram no git | **Como números, para as formas do jogo** (as 60 do atlas): uma tabela gerada por script a partir de `Assets/arena_up/dados`, com a procedência no cabeçalho, como na regra 5.1 das UI_GUIDELINES. Os desenhos (sprites e efeitos) continuam fora do git | Sem os números no git, o replay depende de uma pasta fora do repositório, e um pet abre diferente em outra máquina; com a tabela, uma troca nos dados do jogo exige gerar de novo e mudar a versão |
| **LP-3** | Quem decide a luta do pet, e o que ele aprende | **A IA da arena decide os dois lados.** O que o pet traz é um "nível de luta" contínuo, que interpola entre o "fácil" e o "difícil" da POC (a chance de desviar, o tempo de reação, o erro de mira) e sobe com o treino e com as lutas. Os gambits, o editor de regras e o "o que o pet aprendeu" por regra saem | Sem o nível, o pet não melhora lutando, e o treino perde sentido na luta; com regras escritas pelo dono, voltaria o combate por ações genéricas que o Matheus rejeitou. Um aprendizado mais rico (o pet preferir distância ou corpo a corpo, usar a habilidade cedo ou tarde) pode vir depois, pelo DigiBrain |
| **LP-4** | Que mapa cada lugar de luta usa | **A Arena do portão deixa escolher entre os 8; cada lugar da Campanha e de medalha tem um mapa fixo**, numa tabela da LP2. A proposta: Campina → Campo de treino; Torre de pedra → Coliseu; Cidadela → Castelo Midnight; Montanha Espiral → Caverna Blackheart; Floresta → Floresta Green Shade; Lago → Praia Shellfish. O Deserto e o Ringue ficam para a Arena | Um mapa sorteado esconde a regra dele do jogador; um mapa só deixa as 7 regras sem uso |
| **LP-5** | O que fica dos lugares de luta | **Ficam a Arena (o rival do estágio, como no #448) e a Campanha com os líderes e as medalhas.** Saem na LP4 a Liga, a Torre, o Palácio, a Fábrica, o Salão, as cartas, os chips e os itens de luta, que eram regras por cima do combate por turnos ("qualquer coisa a gente tira essas questões") | Tirar demais deixa pouco a fazer depois do estágio adulto; manter exige portar cada regra para o núcleo novo antes de ter jogado a luta nova. Qualquer um volta depois, como tarefa própria |
| **LP-6** | Os pets das versões de hoje (v14 a v19) | **Saem com aviso na tela**, como no descarte 6 da COMBATE_TR: o ovo novo nasce na versão nova; o Tamer guarda medalhas e recordes | Manter os antigos obriga a guardar o `combate_tr` inteiro só para o replay deles, o contrário de "apaga"; o custo é perder os pets salvos hoje |
| **LP-7** | O combate do Python | **Fica congelado, sem paridade com a luta nova**; os testes de paridade da luta saem da web | Apagar o Python quebra a reprodução dos resultados da v1 e da V2 que dependem dele; manter a paridade obrigaria a portar a POC para o Python, sem uso na pesquisa de hoje |
| **LP-8** | Os golpes de longe sem projétil nos dados do UP (o Gabumon e outros) | **Uma lista curta, no git, dos golpes que são de longe na série** (a rajada do Gabumon é o primeiro), com um projétil nosso: o próprio efeito de acerto do Digimon voando como projétil, e um procedural (como a bola de fogo do Agumon no mapa AC) quando ele não ler. A regra da luta passa a ser a de um golpe de longe | Sem a lista, o Gabumon continua corpo a corpo, que é o que o Matheus apontou; inventar projétil para todos os 95 sem projétil muda a luta de quem é corpo a corpo de verdade |
| **LP-9** | O equilíbrio | **Só na LP5**, uma rodada, com faixas novas; a R3 (#720) fecha sem merge, e as metas R2 e R3 deixam de valer | Equilibrar antes de o Matheus jogar a luta nova repete o que aconteceu com a R2 e a R3: calibrar um núcleo que depois sai |
| **LP-10** | As decisões antigas que caem | **Caem:** a D-1 (o tempo do DigiLab), a D-3 (a `arena/` sai), a D-5 (T = 2 s), a D-8 (o recuo a 80 %), as DE e DR2 do equilíbrio, as D-R3-1 a D-R3-9, a v18 do empurrão (a POC tem o empurrão dela) e a parte da LUTA_EFEITOS presa ao palco 1D. **Ficam:** a D-2 (o replay refaz sempre), a D-7 (a aritmética), a D-9 (as versões antigas não abrem) e o "nenhum botão durante a luta" | Deixar uma decisão antiga valendo sem dizer faz um worker futuro reconstruir o turno |

## 9. Decisões tomadas

- Matheus, 2026-11-08: o combate por turnos sai, e a luta é em tempo real, como a da POC; os lugares por cima dela (ligas, fábricas)
  podem sair; os mapas da POC entram. A R3 do equilíbrio fica pausada.
