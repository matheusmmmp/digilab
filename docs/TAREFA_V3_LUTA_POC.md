# TAREFA V3 — LUTA_POC (2026-11-08)

Coordenador: o Gerente de sprites e luta (Claude Code, Opus 5.5). Worker da LP0: o próprio Gerente, a pedido do Matheus ("Sim, faz
aqui"). Worktree e branch: `v3-luta-poc`. Status: LP0 entregue; as decisões LP-1 a LP-10 DECIDIDAS (Matheus, 2026-11-08: "Aprovo as 10").

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
4. **A entrada do DigiLab** (a LP-3, revista): a IA é a mesma para os dois lados (a dificuldade "normal" da POC); o que muda de um
   lutador para o outro são os stats e o golpe. Os números da luta saem dos 6 stats do pet (vigor, fôlego, recuperação, força,
   mira e guarda: a espécie, o caráter, a forma, o treino, os chips de stat e a condição do cuidado, pelo `perfilDe`), e o golpe, o
   tempo e o projétil saem do Digimon da forma (a LP-2).

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
semente e os stats de cada lado na hora da luta), e o replay refaz a luta. A troca de `hypot` e `sin` pode mudar os últimos dígitos; por isso o
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

### 3.3a Os efeitos visuais que ficam

O Matheus, em 2026-11-08: "aquelas questões visuais que tem em batalha agora, quero que mantenham: quando dá um hit, ele brilha, dá uma
numeração, quando ele solta uma investida e é empurrado para trás … ainda quero que permaneça todas as questões que foram implementadas e
que podem ser reaproveitadas em tempo real". Os efeitos da LUTA_EFEITOS (E1 a E5) são só vista e vão para o palco 2D na LP3, cada um
ligado ao evento equivalente da simulação da POC:

| efeito de hoje | etapa | na luta nova, disparado por |
|---|---|---|
| a pausa curta no acerto, o clarão branco no alvo, a tremida do palco, a faísca no ponto do golpe | E1 | cada acerto da POC (corpo a corpo ou projétil) |
| o empurrão visual do alvo e o recuo de quem leva a investida | E1 e a v18 | o empurrão da própria POC (`ACAO.empurrao`, o dobro no Ringue), que já move o lutador na simulação; o desenho do recuo da v18 é portado para ele |
| os números de dano em fonte de pixel; o golpe forte maior e amarelo | E1 | o dano de cada acerto; o maior e amarelo passa a ser o crítico e a habilidade |
| a cor, a forma, o rastro e o brilho do projétil por elemento | E2 | os projéteis da POC em voo, por cima do desenho do jogo quando há prefab, e sozinho quando não há (LP-8) |
| a elipse que se fecha antes do golpe forte, a onda de choque, a poeira nos pés, a marca no piso | E3 | a preparação da habilidade (do início do ataque até o instante do golpe), o acerto da habilidade e a corrida |
| o escudo, a imagem fantasma, a aura, o clarão do contra-golpe, o brilho da pele dura | E4 | a imagem fantasma no desvio (o dash da POC); a aura com a habilidade pronta e na runa do Castelo; o escudo, o contra-golpe e a pele dura não têm ação equivalente na POC e ficam fora, a menos que voltem como regra |
| a barra de vida com o dano atrasado, a câmera lenta e o "K.O." no nocaute, a câmera que acompanha os dois | E5 | o fim da luta da POC; a câmera passa a acompanhar os dois no chão 2D |

O código vem do `palcoTR/` (`efeitosTR.ts`, `elementosTR.ts`, `projeteisTR.ts`, `chaoTR.ts`, `desenhoTR.ts`): o que é desenho se
reaproveita, e só a leitura do estado muda (do `EstadoTR` para o estado da POC). Os testes `luta_efeitos_e1…e5` são portados junto, no
lugar de apagados.

### 3.4 O inventário: onde o combate por turnos vive

O levantamento foi feito em 2026-11-08 na `origin/main` (`e654891`), por nome de símbolo, porque tudo fora do motor importa pelo
`web/app/motor/index.ts`. As contagens são aproximadas. O destino de cada linha segue a seção 5.1 e as decisões da seção 8.

**O núcleo e as regras por turnos (web, 11 arquivos): saem na LP4.**

| arquivo | o que tem | destino |
|---|---|---|
| `motor/combate_tr/` (`luta.ts`, `controlador.ts`, `adaptador.ts`, `constantes_tr.ts`, `index.ts`, 652 linhas) | o núcleo de 2 s por ação: `criarLutaTR`, `passoTR`, `jogarTR`, `decidirTR`, `jogarLuta`, `RELOGIO_V13/14/18`, `FATORES_V14`, `APRENDIZADO_V14`, `LISTAS_LIDER_V14`, `CARTAS_V14`, `CHIP_ANTES_V14` | **apagar**, trocado pelo `motor/arena/` |
| `motor/combate.ts` (130) | `ACOES_V2`, `regrasDaVersao`, `ehV14`, `Lutador`, `ResultadoLuta`, `comCarta`, `CONDICOES_ESTAGIO`, `Desafiado` | **apagar** as regras; o `ResultadoLuta` vira o resultado da luta nova |
| `motor/gambits_pet.ts` (447) | o `GambitsPet` (as notas por regra, os disparos, as travas, os vetos, os chips, a reserva, o `aprendizadoTR`), o `lutadorPet`, o `estiloDoPet` | **apagar** as regras (LP-3); os stats do pet (`perfilDe`) entram no lugar |
| `motor/bots.ts` (327) | as listas de regras dos rivais (`BOTS_V2/V21/V21D/V21E`, `LISTAS_V14`, `GAMBITS_ARENA/SOMBRIA`), os NPCs, a `CAMPANHA*` e os `LUGARES*` | **adaptar**: os rivais passam a ser um Digimon, um nível e um mapa; as listas de regras saem |
| `motor/constantes.ts` (532), `catalogo.ts` (125), `tipos.ts` (122) | `CV`, `CV21`, `CV21E_TR*` e as `VERSAO_V14…V19`; o `CATALOGO_V2` das formas; os eventos `"l"` e `"pl"` | **adaptar**: saem os números das regras por turnos; ficam o catálogo das formas (a evolução lê dele) e os eventos |

**Os consumidores no motor (web, 15 arquivos).**

| arquivo | o que usa | destino |
|---|---|---|
| `motor/motor.ts` (1 292) | `lutar`, `_lutar`, `montarLuta`, o `gp.aprender`, os chips, as cartas, o resumo da luta para a ponte; o evento `"l"` (linha 525) e o replay (linha 1243) | **adaptar** na LP2: a luta do pet chama o núcleo novo; saem os chips, as cartas e o `gp` |
| `motor/arenas.ts` (138) | `jogarLuta`, `GAMBITS_ARENA`, `comCarta`, `FATORES_V14` | **adaptar** (a Campanha e os líderes, LP-5) |
| `motor/medalhas.ts`, `nomes.ts`, `expressao.ts`, `motivo.ts` | a `CAMPANHA_V6`, os NPCs, o `NOME_V2` e o `CATALOGO_V2` | **adaptar** só o que cita as regras; os nomes e o catálogo ficam |
| `motor/liga.ts`, `fabrica.ts`, `salao.ts`, `instalacoes.ts` | `jogarLiga`, `jogarLuta`, `gambitsAdulto` | **portar** na LP2b: a sequência de lutas fica, as regras por turnos saem; o Palácio junta-se à Torre (LP-5) |
| `motor/itens.ts` | os chips de stat, os chips de regra e as cartas | **adaptar**: os chips de stat ficam (são treino); os chips de regra e as cartas saem (LP-5) |
| `motor/corpo.ts`, `motor_corpo.ts`, `digibrain/adapt.ts`, `digibrain/mem.ts` | a dor da luta (`ConfigLutaCorpo`, `aplicarResumoLuta`), o `receber_luta` e os episódios da luta (PONTE_LUTA) | **adaptar** na LP2: o resumo passa a sair do resultado novo (o dano recebido, o fim, a duração) |

**As telas (web, ~40 arquivos).**
- `src/telas/lutar/palcoTR/` (10 arquivos, o palco 1D com os efeitos E1–E5): **portar** na LP3 para o palco 2D; os efeitos ficam
  (seção 3.3a).
- `src/luta.ts` (551), o motor das telas de luta (`lutarAnimado`, o replay pelo `res.tr.entrada`): **adaptar**.
- `src/telas/lutar/` (`TelaLuta`, `TelaArena`, `TelaCampanha`, `TelaMedalhas`, `ModalResultado`): **adaptar**. `EditorRegras`,
  `PainelAprendizado` e `src/aprendizadoLuta.ts`: **apagar** (LP-3). `TelaFronteira` e `FabricaSalao`: **adaptar** na LP2b (LP-5).
- `src/fronteira.ts`, `src/tamer.ts` (os eventos `fabrica`, `fabrica_luta`, `fabrica_troca` e `salao` do Tamer): **adaptar** na LP2b; o
  Tamer guarda as medalhas e os recordes (LP-6).
- Os outros que citam a luta: `EscolhaCarta` (as cartas: **apagar**); `TelaItens` (só os chips de stat ficam: **adaptar**); `TelaEvolucao`, `TelaCatalogo`,
  `TelaRegistro`, `MeusPets`, `TelaPet`, `LinhaAgora`, `Jornada`, `DigiBrainLab`, `TelaCenarios` e os lugares da ilha (`lugares`,
  `marcadoresLugar`, `vista`, `CadeadosDaIlha`, `ObjetosDaIlha`): **adaptar** o que lê as regras ou a duração da luta.

**Os testes e os scripts (web).**
- Unidade (~45): `combate_tr*`, `luta_empurrao*` (a regra), `luta_tela`, `luta_tr_hoje`, `limite_desafiado`, `listas_v14`,
  `pet_v14`, `aprendizado_luta`, `vigia_candidatas`, `progressao_v9`, `liga`, `fabrica_salao`, `fronteira_itens_v9`, `instalacoes`,
  `itens`: **apagar** com o que testam. Os `luta_efeitos_e1…e5`: **portar** na LP3. `arenas`, `lab_cenarios`, `confianca`, `lobos_v11`, `evolucao_canonica`, `pet_lab`, os
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
| **LP2: o pet luta no núcleo novo** | uma `VERSAO_PET` nova; a entrada da luta no log; os stats do pet na luta (LP-3); a Arena e a Campanha lutam no núcleo novo; a ponte com o DigiBrain (a dor e o episódio da luta, PONTE_LUTA) lê o resultado novo; o aviso dos pets antigos (LP-6); a medida do custo do replay | o caminho do `combate_tr` para a versão nova; a Liga, a Torre, a Fábrica e o Salão ficam fechados até a LP2b |
| **LP2b: o torneio no núcleo novo** | a Liga, a Torre (com o Palácio junto), a Fábrica e o Salão, com as regras de sequência deles, sobre o núcleo novo; os chips de stat no `perfilDe` | as cartas e os chips de regra |
| **LP3: a tela** | o palco novo em 2D, a partir do desenho do #446/#448 (`web/app/src/telas/lutar/arena_tr/desenho.ts` em `efb2ded`): os 8 mapas, os projéteis com o desenho do jogo (os prefabs de `Assets/arena_up/efeitos`), o projétil do Gabumon e dos outros sem projétil (LP-8), todos os efeitos da LUTA_EFEITOS que têm evento equivalente (seção 3.3a), com os testes deles; capturas no desktop e no celular, para aprovação | o palco 1D do `palcoTR/` (os efeitos e o desenho são portados, não apagados) |
| **LP4: a limpeza** | os documentos de cada coisa que saiu marcados como SUBSTITUÍDOS, com o link para esta tarefa | o `combate_tr/`, as regras por turnos e o que só servia a elas (o inventário da seção 3.4), os testes e os scripts de equilíbrio delas |
| **LP5: o equilíbrio** | uma rodada só, no fim, com plano de análise e faixas novas (a regra "equilíbrio só no fim") | as metas R2 e R3 |

A LP3 pode correr ao lado da LP2 numa worktree própria, porque só toca a tela; a LP4 espera a LP2, a LP2b e a LP3.

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

**DECIDIDAS em 2026-11-08** (Matheus, "Aprovo as 10"): as dez valem como recomendadas abaixo, a LP-3 e a LP-5 na forma revista,
aprovada em seguida ("Aprovo as duas"). Os números da POC continuam
PROPOSTOS até a LP5.

| # | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **LP-1** | O núcleo da luta passa a ser a simulação da POC, de volta do `efb2ded` para o motor, e o `combate_tr` sai | **Sim.** Volta o `web/app/arena/` como `web/app/motor/arena/`, com só as quatro mudanças da seção 3.2 | Reescrever do zero perde a paridade com o harness, que é a prova de que é a POC; manter os dois núcleos dobra os testes e o equilíbrio |
| **LP-2** | Os dados que a luta lê (o status, o golpe, o tempo do clipe, o projétil, o atributo) entram no git | **Como números, para as formas do jogo** (as 60 do atlas): uma tabela gerada por script a partir de `Assets/arena_up/dados`, com a procedência no cabeçalho, como na regra 5.1 das UI_GUIDELINES. Os desenhos (sprites e efeitos) continuam fora do git | Sem os números no git, o replay depende de uma pasta fora do repositório, e um pet abre diferente em outra máquina; com a tabela, uma troca nos dados do jogo exige gerar de novo e mudar a versão |
| **LP-3** (revista) | Quem decide a luta do pet, e o que ele traz para ela | **A IA da arena é a mesma para os dois lados; o que o pet traz são os stats dele.** Revista pelo Matheus em 2026-11-08: "A ideia é cada pet ter os stats, o treinamento. Evoluir isso, não o nível de luta em si." Os 6 stats do pet (vigor, fôlego, recuperação, força, mira e guarda), que já saem da espécie, do caráter, da forma, do treino, dos chips de stat e da condição do cuidado (`perfilDe` em `motor/catalogo.ts`), viram os números da luta da POC. A proposta: vigor → vida; força → ataque; guarda → defesa; fôlego → movimento; recuperação → o ciclo do ataque e a recarga da habilidade; mira → o crítico e o erro de mira. Do Digimon da forma vêm só o golpe, o tempo, o projétil e o atributo (LP-2), e não os status do UP, para não contar a espécie duas vezes. O treino e a evolução sobem os stats, e a luta sobe com eles. Os gambits, o editor de regras e o "o que o pet aprendeu" por regra saem | Usar os status do UP por cima dos stats do pet conta a espécie duas vezes e tira o peso do treino; sem os stats, o treino não muda a luta. O mapeamento é PROPOSTO, SEM FONTE, e se acerta na LP5 |
| **LP-4** | Que mapa cada lugar de luta usa | **A Arena do portão deixa escolher entre os 8; cada lugar da Campanha e de medalha tem um mapa fixo**, numa tabela da LP2. A proposta: Campina → Campo de treino; Torre de pedra → Coliseu; Cidadela → Castelo Midnight; Montanha Espiral → Caverna Blackheart; Floresta → Floresta Green Shade; Lago → Praia Shellfish. O Deserto e o Ringue ficam para a Arena | Um mapa sorteado esconde a regra dele do jogador; um mapa só deixa as 7 regras sem uso |
| **LP-5** (revista) | O que fica dos lugares de luta | **Fica tudo o que é uma sequência de lutas, portado para o núcleo novo numa etapa própria (LP2b):** a Arena, a Campanha com os líderes e as medalhas, a Liga (os 6 líderes em sequência, sem cura), a Torre (a sequência contra Megas, sem cura), a Fábrica (os 3 alugados e a troca pelo derrotado) e o Salão (um pet de cada estágio). Revista pelo Matheus em 2026-11-08, que perguntou se nada disso podia ser reaproveitado: pode, porque essas regras são do torneio, não do turno. **O Palácio se junta à Torre:** a única diferença dele era o pet decidir sem as regras do dono, e na luta nova todo pet decide sozinho. **Os chips de stat ficam** (são treino). **Saem as cartas e os chips de regra:** eles mudam regras e escolhas que deixam de existir | Portar tudo de uma vez atrasa a primeira luta jogável; por isso a LP2 entrega a Arena e a Campanha, e a LP2b o resto. As cartas podem voltar depois como efeito de uma luta (um bônus de stat), se o Matheus quiser |
| **LP-6** | Os pets das versões de hoje (v14 a v19) | **Saem com aviso na tela**, como no descarte 6 da COMBATE_TR: o ovo novo nasce na versão nova; o Tamer guarda medalhas e recordes | Manter os antigos obriga a guardar o `combate_tr` inteiro só para o replay deles, o contrário de "apaga"; o custo é perder os pets salvos hoje |
| **LP-7** | O combate do Python | **Fica congelado, sem paridade com a luta nova**; os testes de paridade da luta saem da web | Apagar o Python quebra a reprodução dos resultados da v1 e da V2 que dependem dele; manter a paridade obrigaria a portar a POC para o Python, sem uso na pesquisa de hoje |
| **LP-8** | Os golpes de longe sem projétil nos dados do UP (o Gabumon e outros) | **Uma lista curta, no git, dos golpes que são de longe na série** (a rajada do Gabumon é o primeiro), com um projétil nosso: o próprio efeito de acerto do Digimon voando como projétil, e um procedural (como a bola de fogo do Agumon no mapa AC) quando ele não ler. A regra da luta passa a ser a de um golpe de longe | Sem a lista, o Gabumon continua corpo a corpo, que é o que o Matheus apontou; inventar projétil para todos os 95 sem projétil muda a luta de quem é corpo a corpo de verdade |
| **LP-9** | O equilíbrio | **Só na LP5**, uma rodada, com faixas novas; a R3 (#720) fecha sem merge, e as metas R2 e R3 deixam de valer | Equilibrar antes de o Matheus jogar a luta nova repete o que aconteceu com a R2 e a R3: calibrar um núcleo que depois sai |
| **LP-10** | As decisões antigas que caem | **Caem:** a D-1 (o tempo do DigiLab), a D-3 (a `arena/` sai), a D-5 (T = 2 s), a D-8 (o recuo a 80 %), as DE e DR2 do equilíbrio, as D-R3-1 a D-R3-9, a regra do empurrão da v18 no motor (a POC tem o empurrão dela; o desenho do recuo fica) e, da E4, o escudo, o contra-golpe e a pele dura, que não têm ação na POC. **Ficam:** os efeitos da LUTA_EFEITOS que têm evento equivalente (seção 3.3a), a D-2 (o replay refaz sempre), a D-7 (a aritmética), a D-9 (as versões antigas não abrem) e o "nenhum botão durante a luta" | Deixar uma decisão antiga valendo sem dizer faz um worker futuro reconstruir o turno |

## 9. Decisões tomadas

- Matheus, 2026-11-08: o combate por turnos sai, e a luta é em tempo real, como a da POC; os lugares por cima dela (ligas, fábricas)
  podem sair; os mapas da POC entram. A R3 do equilíbrio fica pausada.
- Matheus, 2026-11-08, "Aprovo as 10": a LP-1 a LP-10 como recomendadas na seção 8. A LP1 pode começar.
- Matheus, 2026-11-08, depois do "Aprovo as 10": a LP-3 e a LP-5 revistas (os stats do pet e o treino no lugar do "nível de luta";
  a Liga, a Torre, a Fábrica e o Salão reaproveitados). Aprovadas na forma revista ("Aprovo as duas", 2026-11-08).
- Matheus, 2026-11-08, "Aprovo as 6" (repassado pelo Gerente de sprites e luta): as seis decisões da LP2 (LP2-1 a LP2-6), DECIDIDAS como
  recomendadas pelo worker:
  - **LP2-1:** a versão do pet da luta nova é a **v21**; a v20 fica para o #694 (a árvore);
  - **LP2-2:** o mapeamento dos 6 stats: o pet neutro (10 em cada stat) recebe os STATS_PADRAO da POC (vida 900, ataque 100, defesa 50,
    movimento 70, ciclo 2 000 ms, recarga 8 s, crítico 10 %, erro de mira 18 px), e cada número escala na razão do stat (vigor, força,
    guarda, fôlego, mira) ou na razão inversa (recuperação no ciclo e na recarga, mira no erro); a vida leva também o multiplicador do
    estágio e a condição. O erro de mira passa a ser de cada lutador. PROPOSTO, SEM FONTE, até a LP5;
  - **LP2-3:** os 10 NPCs da Campanha entram na tabela pelo mesmo gerador, com os números pelo perfilNPC e o mesmo mapeamento;
  - **LP2-4:** o rival da Arena é uma das 60 formas, do estágio do pet, com o perfil canônico e sem treino; o evento "l" guarda a forma, a
    semente e o mapa; os bots clássicos saem da v21;
  - **LP2-5:** das regras das arenas dos líderes, fica só a série da Cidadela (3 lutas sem cura para o pet); o mapa fixo da LP-4 vira a regra
    do lugar;
  - **LP2-6:** na v21 saem os gambits (o gp, o aprender e o "g"), as cartas ("k") e os chips de regra; ficam os chips de stat, a confiança,
    a lesão, o sparring, as contagens e as medalhas.
- Matheus, 2026-11-09, repassado pelo Gerente de sprites e luta: "siga aí até implementar o combate do jogo" (a LP3 liga o palco aos lugares de
  luta da v21) e, depois das capturas, "Aprovo, abre a LP3b" (as capturas da LP3 aprovadas; a LP3b, o golpe de longe da LP-8 no núcleo,
  liberada).
- Matheus, 2026-11-09, repassado pelo Gerente de sprites e luta: "deixa os mesmos botões que tinha no loop anterior, que era de deixar a
  luta mais rápida, coisa assim". O dock da tela de antes (pausar, ×2, Desistir e, no replay, Sair do replay) volta na luta da POC. Troca o
  "sem botão durante a luta" do item 3 da seção 3.2 e o que a LP-10 deixava valendo (D-LP3-11).

## Resultado da LP1 (2026-11-08)

Worker: Claude Code (Opus 5.5), worktree e branch `v3-luta-poc-lp1`, a pedido do Gerente de sprites e luta. Os desvios e as interpretações
estão em `docs/registro/2026-11.md`, seção "LUTA_POC, LP1".

**O que entrou.** O núcleo da luta da POC voltou do `efb2ded` para `web/app/motor/arena/`, sem DOM, atrás da chave `LUTA_POC_LIGADA`
(desligada). Nada do jogo importa dele: o `combate_tr`, as telas e os gabaritos de hoje não mudaram (o diff só tem arquivos novos). As
quatro mudanças da seção 3.2:
1. **A aritmética da D-7.** Todo `Math.hypot` virou `dist(dx, dy) = Math.sqrt(dx*dx + dy*dy)`; o `Math.sin` virou `seno`, um polinômio
   fixo (Taylor de grau 19 depois de reduzir por 2π em três partes); o `x ** 2` virou `x * x`; o `Math.pow` do `fatorRitmo` saiu do
   núcleo (o `fr` vem pronto na tabela). O teste `arena_aritmetica` confere pela fonte que só há `sqrt`, `min`, `max`, `floor`, `ceil`,
   `round` e `abs`, sem `**`.
2. **A tabela das 60 formas no git** (`motor/arena/formas.ts`, LP-2), gerada por `tools/gerar_tabela_arena.py` a partir de
   `Assets/arena_up/dados` (o sha256 de cada JSON está no cabeçalho; `--conferir` refaz e compara). Por forma: o Digimon no atlas, o
   atributo, o golpe e a habilidade (a animação, o `t`, o projétil com prefab, tipo e velocidade, os impactos e o `fr`) e a duração dos
   clipes. Os status do Digimon UP não entram (LP-3): a entrada aceita os `Stats` prontos (hp, atk, def, vel, cad, crit, hcd, hpot,
   esquiva, atordoa). Os desenhos continuam fora do git.
3. **Só 1 contra 1, os dois pela IA "normal".** Saíram o modo jogador, a entrada, as equipes e as trocas.
4. **Nenhuma ligação com o pet** (a LP2).

**A fidelidade** (`web/app/scripts/arena_fidelidade.ts` → `web/app/scripts/medicoes/arena_fidelidade_lp1.json`):
- **A âncora:** a POC do `efb2ded`, com as equipes de 3 e a sequência única, reproduz o gabarito do harness
  (`arena_gabarito_prototipo.json`) sem nenhuma diferença.
- **O controle:** o núcleo novo com a aritmética da POC de volta (`hypot` e `sin`) dá a mesma luta que a POC 1 contra 1 em **3 276 de
  3 276** lutas, em todos os bits (vencedor, relógio, vidas e posições finais). O porte só mudou a aritmética.
- **A diferença da aritmética:** o núcleo novo contra a POC 1 contra 1, nas tabelas do harness (arenas nas sementes 7 e 42, rodízio dos 5
  estágios, estágios cruzados, níveis): **o mesmo resultado (vencedor, relógio e vidas) em 3 276 de 3 276 lutas**; as posições finais
  são iguais em todos os bits em 184. **Todas as tabelas saem iguais** (diferença 0 em todas as células); nenhum alerta pelo critério
  de ±5 pp ou ±5 % (PROPOSTO, SEM FONTE).
- **No CI:** `test/gabaritos/arena_poc_1x1.json` (480 lutas da POC 1 contra 1: as 60 formas nos 8 mapas, stats genéricos da POC) e o
  teste `arena_luta` (o núcleo novo dá o mesmo resultado nas 480).
- O harness compara no 1 contra 1, porque as equipes de 3 não são do jogo; o gabarito de 3 contra 3 serve de âncora da POC.

**O custo** (`web/app/scripts/medir_arena_lp1.ts` → `web/app/scripts/medicoes/arena_custo_lp1.json`): ~0,6–0,7 ms por luta no Node
(Node 24, i7-14700KF, um processo; a mediana de 5 repetições das 480 lutas do gabarito), 19,1 s de jogo e 1 192 passos em média, ~0,55 µs
por passo. Uma vida com 1 000 lutas refaria em ~0,7 s no Node. O valor exato de cada rodada está no JSON. O celular segue SEM FONTE (a
LP2 mede o replay).

**Os testes novos:** `arena_luta.test.ts` (a tabela, o replay bit a bit nos 8 mapas, os 8 mapas até o fim com a regra de cada um
aparecendo, os fluxos, a entrada que falha alto, a fidelidade), `arena_sem_dom.test.mjs` (sem DOM, só importa do motor, a chave
desligada e ninguém importando o núcleo) e `arena_aritmetica.test.mjs` (a aritmética pela fonte, o seno perto do `Math.sin`, o `fr`
igual ao `fatorRitmo` com o `EQ` e o gerador com as mesmas constantes).

## Resultado da LP2 (2026-11-08)

Worker: Claude Code (Opus 5.5), worktree e branch `v3-luta-poc-lp2`, a pedido do Gerente de sprites e luta. As decisões LP2-1 a LP2-6 estão na
seção 9; os desvios e as interpretações, em `docs/registro/2026-11.md`, seção "LUTA_POC, LP2".

**A chave.** Tudo fica atrás da `LUTA_POC_LIGADA` (desligada). Desligada, o jogo de hoje sai byte a byte: os ovos nascem v19, a
`VERSOES_PET` não muda, e as vidas de hoje com lutas (`test/gabaritos/lp2_vidas_hoje.json`, gravado num commit próprio antes da mudança:
40 vidas de v13 a v19 e do pet de teste v16, 800 lutas) saem iguais, com o replay também. No app, `?luta_poc=1` liga a chave só naquela
aba (`src/lutaPoc.ts`).

**A v21 no motor** (`motor/luta_poc.ts`, `Motor.lutarPoc`):
- **A luta:** a simulação de `motor/arena/`, 1 contra 1, os dois lados pela IA "normal". O evento `"l"` guarda o rival, a semente e o mapa
  (`{r, s, m}`), e o replay refaz a luta.
- **Os números do pet:** saem dos 6 stats do `statsDe` (espécie, caráter e forma), mais o treino e os chips de stat (os `pontosDeLuta`) com o
  peso de combate de sempre, e da condição do cuidado, pelo mapeamento da LP2-2. Os do rival saem do perfil canônico da forma (Arena) ou do
  perfilNPC no estágio do lugar (Campanha). O golpe, o tempo, o projétil e o atributo vêm da tabela das formas (agora com os 10 NPCs).
- **Os lugares:**
  - a Arena: uma forma do estágio do pet, num dos 8 mapas, à escolha;
  - a Campanha: o NPC, no mapa fixo do lugar (LP-4), com a série de 3 lutas sem cura na Cidadela;
  - a Liga, a Torre, a Fábrica e o Salão respondem "fechado até a LP2b".
- **O que conta:** a luta conta como as de sempre (as contagens, a lesão, a confiança, o sparring, a campanha e o histórico).
- **O que sai:** os gambits (o pet v21 não tem `gp`), as cartas e os chips de regra. Os eventos `"g"` e `"k"` num pet v21 levantam erro.
- **A ponte com o DigiBrain:** lê o resultado novo. O dano é a vida do começo da luta menos a do fim, a vida máxima é a dos stats, e o
  resultado é a vitória, a derrota ou o empate. O formato do resumo (rival, resultado, vida perdida em S) não muda.
- **O núcleo:** ganhou o erro de mira por lutador e a vida inicial de um lado (a série sem cura). A fidelidade da LP1 continua: 3 276 de
  3 276 lutas com o mesmo resultado, as tabelas iguais.

**O app com a chave ligada:**
- **O descarte 7:** tira os pets v13 a v19 (o ativo e os guardados) com o aviso da luta nova (LP-6). Os saves descartados ficam para baixar,
  e o Tamer fica inteiro.
- **Os ovos:** os ovos novos e o pet de exemplo nascem v21, e a escada de exemplo não é semeada.
- **O Importar:** abre só a v21.
- **As telas:** a Arena, a Campanha e a Fronteira dizem que a tela da luta nova ainda vem (a LP3), em vez de abrir as telas do combate de
  antes. O registro de lutas lê as lutas v21.

**O custo do replay** (`web/app/scripts/medir_replay_lp2.ts` → `web/app/scripts/medicoes/replay_lp2.json`): ~0,3 ms por luta acrescentados
ao replay (Node 24, i7-14700KF, um processo), com vidas de 166 a 234 lutas. Uma vida assim refaz em ~70 ms, e 1 000 lutas somariam ~0,3 s no
Node. As vidas que lutam sem parar morrem por lesão (20 num estágio) antes das 1 000 lutas. O celular segue SEM FONTE.

**Os testes novos:**
- `lp2_vidas_hoje.test.ts`: as vidas de hoje com a chave desligada;
- `luta_poc_pet.test.ts`: a chave e a versão, o mapeamento, os rivais e os mapas, a luta, o que sai, os lugares fechados, a ponte e o gabarito
  da vida nova (`test/gabaritos/lp2_vidas_v21.json`, 10 vidas v21, 200 lutas) com o replay bit a bit;
- `tamer.test.ts`: o descarte 7;
- `e2e/luta_poc_lp2.spec.ts`: a chave no app.

## Resultado da LP2b (2026-11-08)

Worker: Claude Code (Opus 5.5), worktree e branch `v3-luta-poc-lp2b`, a pedido do Gerente de sprites e luta. Os desvios estão em
`docs/registro/2026-11.md`, seção "LUTA_POC, LP2b". Nenhuma decisão nova foi levada ao Matheus. Os três mapas dos torneios sem lugar são
PROPOSTOS, como o Gerente pediu.

**Os torneios na v21** (`Motor.lutarPoc`, atrás da `LUTA_POC_LIGADA`):
- **O evento:** cada tentativa é um evento `"l"` `{r, s}`, sem mapa, porque cada luta tem o dela. As entradas de sempre valem: as 6
  medalhas na Liga, o título na Torre e no Salão e a semente da tentativa, que sai do registro do pet.
- **A Liga:** os 6 líderes em sequência, sem cura entre as lutas. Cada um é o Mega da tabela da Liga, com o perfil canônico pelo mapeamento
  da LP2-2, no mapa do lugar do líder (LP-4: Campo, Coliseu, Floresta, Castelo, Praia e Caverna). O título vem com as 6 vitórias.
- **A Torre de Batalha:** os Megas sorteados da semente da tentativa, sem cura, até a primeira que não for vitória ou até o teto de 100, no
  Ringue (PROPOSTO). O recorde do pet fica ali. O **Palácio juntou-se à Torre**: na v21 ele responde que a luta é na Torre.
- **O Salão:** um rival sorteado do estágio do pet, com o perfil canônico de antes, no Coliseu (PROPOSTO).
- **Os chips de stat** valem pelos stats do pet, como na LP2. As cartas e os chips de regra continuam fora.

**A Fábrica da luta da POC** (`motor/fabrica.ts`, regras `v: 21`, no registro do Tamer):
- os 3 alugados e os rivais são os Megas sorteados de antes, com os números do perfil canônico pelo mapeamento, sem o fator dos rivais (o
  mapeamento não tem escala), no Campo de treino (PROPOSTO);
- ficam as séries de 3 sem cura dentro da série e a troca pelo derrotado, que entra inteiro;
- os eventos do Tamer não mudam de forma (`"fabrica"`, `"fabrica_luta"`, `"fabrica_troca"`); o `v: 21` entra nas versões conhecidas;
- com a chave ligada, a tentativa nova grava `v: 21`; com ela desligada, a de hoje (`v: 14`).

**O que não muda.** Com a chave desligada, as vidas de hoje (`lp2_vidas_hoje`), a vida v21 da LP2 (`lp2_vidas_v21`) e os gabaritos saem
iguais. A dor e a memória da luta seguem como na LP2, e a confiança conta por rival como antes. As telas dos torneios e da Fábrica na luta
nova são da LP3: com a chave ligada, a Fronteira de um pet v21 segue dizendo que a tela vem.

**Os testes novos:** `luta_poc_torneios.test.ts`:
- as entradas;
- a Liga, a Torre e o Salão, com o rival, o mapa e a vida que passa de uma luta para a outra;
- a Fábrica v21, com as séries, a troca e o Tamer que refaz a tentativa;
- o gabarito `test/gabaritos/lp2b_torneios_v21.json` (5 vidas muito treinadas, 71 lutas de torneio; 5 tentativas da Fábrica) e o replay bit
  a bit.

## Resultado da LP3 (2026-11-09)

Worker: Claude Code (Opus 5.5), worktree e branch `v3-luta-poc-lp3`, a pedido do Gerente de sprites e luta. Os desvios estão em
`docs/registro/2026-11.md`, seção "LUTA_POC, LP3". As capturas foram aprovadas pelo Matheus (seção 9).

**O palco** (`web/app/src/telas/lutar/palcoPoc/`, só vista):
- **o chão:** a elipse 2D da POC, no mundo de 480 × 280, com os 8 mapas do UP e a regra de cada um à vista:
  - a área que fecha no Coliseu;
  - a maré na Praia;
  - a areia e a tempestade no Deserto;
  - a runa e os pilares que quebram no Castelo;
  - a lava e as erupções na Caverna;
  - as árvores e as moitas na Floresta;
  - o Ringue sem cerca.
  O cartão "O mapa" diz a regra e os avisos dela (a arena fecha, a tempestade, a runa);
- **os lutadores:** os sprites do atlas em escala inteira, com os clipes `Idle`, `Run`, `Attack_1`, `Stun` e `Die` pelo estado da simulação,
  sem nada acrescentado às poses;
- **os projéteis:** em voo, com o prefab do jogo (`Assets/arena_up/efeitos`, fora do git) por cima do rastro e do brilho do elemento (E2);
- **o projétil nosso da LP-8:** só desenho nesta etapa (D-LP3-3; a regra é a LP3b);
- **os efeitos da seção 3.3a,** de E1 a E5 (D-LP3-4);
- **o dock da tela de antes** (decisão do Matheus de 2026-11-09, D-LP3-11; no lugar do "nenhum botão" das capturas aprovadas): pausar,
  ×2 e Desistir com a confirmação; no fim, Ver replay e Continuar; no replay, Sair do replay e Ver de novo. No desktop e no celular, nas
  duas peles. Nada disso muda o resultado nem o registro.

**O jogo** (com `?luta_poc=1`, os pets v21):
- **a Arena:** o rival do estágio e um dos 8 mapas;
- **a Campanha:** o mapa do lugar (LP-4), com a série da Cidadela;
- **a Fronteira:** a Liga (6 lutas sem cura), a Torre, o Salão e a Fábrica.
O motor grava a luta, e o palco a refaz da mesma entrada e confere o fim (D-LP3-2). Uma luta montada direto no núcleo
(`?luta_poc=1&palco_poc=<mapa>,<forma>,<forma>,<semente>`) serve às capturas e ao e2e e não grava nada.

**Os testes:**
- `test/luta_poc_lp3.test.ts` (14): os E1–E5 portados para o palco 2D (o determinismo dos efeitos, o fim igual ao da luta sem tela, cada
  efeito no seu evento, o movimento reduzido) e o palco refazendo as lutas do motor (a Arena, a Liga, a Torre e o Salão de um pet v21);
- `e2e/luta_poc_lp3.spec.ts` (4): a luta montada até o fim com o dock, a luta da Arena no registro, o movimento reduzido sem tremida e o
  dock (pausar para o relógio, Desistir com a confirmação, Ver replay, Sair do replay, o registro igual);
- o `e2e/luta_poc_lp2.spec.ts` passou a esperar as telas novas;
- as capturas: `e2e_capturas/luta_poc_lp3.spec.ts` (as 8 lutas montadas), `luta_poc_lp3_jogo.spec.ts` (o jogo com um pet v21 treinado)
  e `luta_poc_lp3_dock.spec.ts` (o dock em cada estado).

**O que fica:**
- a regra da LP-8 (a LP3b);
- ligar a chave por padrão, proposto para o PR da LP4 (o descarte 7 é de mão única);
- os achados D-LP3-7 a D-LP3-9.

## Resultado da LP3b (2026-11-09)

Worker: Claude Code (Opus 5.5), worktree e branch `v3-luta-poc-lp3b`, a pedido do Gerente de sprites e luta, com a liberação do Matheus
("Aprovo, abre a LP3b", 2026-11-09, repassado). Os desvios estão em `docs/registro/2026-11.md`, seção "LUTA_POC, LP3b".

**A regra da LP-8 no núcleo** (`tools/gerar_tabela_arena.py` → `web/app/motor/arena/formas.ts`):
- o Gabumon, o Garurumon, o MetalGarurumon, o Angemon e o Gargomon atiram o próprio efeito de acerto, com a velocidade 30 e o tipo
  "Guide" (PROPOSTOS, SEM FONTE);
- a simulação não mudou: com projétil na tabela, a forma passa a ter o alcance de quem atira (150 px) e o voo de verdade, que acerta o
  primeiro inimigo que cruza, some fora do alcance, bate nas árvores, nas rochas e nos pilares e pode ser desviado;
- o golpe da POC fica no git (`GOLPES_DA_POC`, `FORMAS_ARENA_POC`) para a fidelidade da LP1, que continua com 480 de 480 lutas iguais
  ao gabarito do harness.

**Os gabaritos:** os v21 foram regravados num commit próprio, com o motivo (D-LP3b-4). As vidas de hoje não mudam, e a chave segue
desligada.

**O efeito** (`scripts/medicoes/lp3b_lp8.json`): as vitórias das cinco formas mudam de −0,4 a +3,5 pontos e as lutas ficam de 0,2 a 1,3 s
mais longas. O equilíbrio é da LP5.

**A tela:** o desenho da LP3 não muda. O voo das cinco formas passa a ser o da simulação; o projétil só desenhado da LP3 saiu neste PR,
depois do merge da LP3 na `main` (D-LP3b-6).


## Resultado da LP4 (2026-11-10)

Worker: Claude Code (Opus 5.5), worktree e branch `v3-luta-poc-lp4`, a pedido do Gerente de sprites e luta, com a liberação do Matheus
("Sim, abre a LP4", 2026-11-10, repassado). Os desvios estão em `docs/registro/2026-11.md`, seção "LUTA_POC, LP4". Três escolhas que perdem
ou escondem dado foram DECIDIDAS pelo Matheus em 2026-11-10 ("Aprovo tudo", repassado pelo Gerente, junto com as capturas): a D-LP4-1, a
D-LP4-2 e a D-LP4-3. O risco do Gazimon (D-LP4-6) fica para a LP5.

**A chave ligada.** `LUTA_POC_LIGADA = true` (`web/app/motor/arena/constantes.ts`). Com isso, para todos e sem `?luta_poc=1`:
- os ovos novos e o pet de exemplo nascem v21 (`VERSAO_PET = 21`);
- só a v21 abre (`VERSOES_PET = [21]`), e o pet de teste v16 segue no laboratório;
- o Importar só abre a v21;
- a Arena, a Campanha e a Fronteira são as do palco novo.

**O descarte 8 (DECIDIDO, Matheus, 2026-11-10, D-LP4-2).** Roda uma vez, também onde o 7 já rodou pelo `?luta_poc=1`:
- os pets v13 a v19 saem, o ativo e os guardados, com o aviso "A luta agora é na arena" e o arquivo para baixar;
- no Tamer, sai a Fábrica do combate por turnos (v13 e v14), que não se refaz mais, com o registro de antes guardado no mesmo arquivo; o
  recorde da Fábrica recomeça. O resto do Tamer fica byte a byte;
- o registro do Tamer passa à versão 8.

**O que saiu** (o inventário da seção 3.4):
- o motor: `motor/combate_tr/`, `motor/combate.ts`, `motor/gambits_pet.ts`, as listas de gambits de `motor/bots.ts`, os fatores das arenas,
  da Liga, do Salão e da Fábrica, as regras das arenas (fica a série da Cidadela), o `CV`, o `CV21E` e o `GA`, o `Motor.lutar`, o
  `montarLuta`, os gambits (`"g"`), as cartas (`"k"`) e os chips de regra. Os eventos `"g"` e `"k"` no registro levantam erro;
- as telas: `src/luta.ts`, o palco 1D (`palcoTR/`; os geradores de desenho que o palco 2D usa foram para `palcoPoc/`), a `TelaLuta`, a
  `TelaArena`, a `TelaCampanha`, o `ModalResultado`, o `EditorRegras`, o `PainelAprendizado`, o `aprendizadoLuta.ts`, a `EscolhaCarta`, o mapa
  3D da Exploração e o "Ver replay" do Diário. Os Cenários do Diário lutam na luta da POC; o Nv 6 da progressão passou a ser o Forçar;
- os itens: só o chip de stat faz efeito. Os chips de regra e as cartas ficam no catálogo, sem efeito, porque o registro do Tamer os guarda,
  e as medalhas e as revanches não os dão mais;
- os testes e os scripts: os do combate por turnos, os gabaritos das versões antigas, `scripts/equilibrio_tr/` e
  `scripts/gerar_gabarito_vidas_v13.ts`; no e2e, os specs das telas de antes, e os saves regerados na v21.

**O pet de teste (DECIDIDO, Matheus, 2026-11-10, D-LP4-3).** Ele não luta mais. Um save v16 com luta não abre e fica no armazenamento, com o erro visível.

**O que não mudou.** As vidas v21 dos gabaritos da LP2 e da LP2b, com o replay bit a bit: o lugar dos gambits e das cartas na assinatura
ficou. O Python ficou (LP-7). Os registros não se apagaram, e o G-NADA-PERDIDO passa.

**Os documentos.** Os do combate por turnos levam a marca SUBSTITUÍDO, com o link para esta tarefa:
- a `ESPEC_COMBATE_TR`, a `TAREFA_V2_COMBATE_TR` e a `TAREFA_V3_COMBATE_V14`;
- os três `PLANO_EQUILIBRIO_COMBATE_TR*` e o `EQUILIBRIO_COMBATE_TR`;
- a `TAREFA_V3_LUTA_EMPURRAO` e, no palco 1D, a `TAREFA_V3_LUTA_EFEITOS`.
A `PLANO_V3` (a trilha B), a `TAREFA_V3_PONTE_LUTA`, o `DESIGN_MEDALHAS_ARENAS` e o `MAPA_REPOSITORIO` ganharam a nota do que mudou.

**Os achados.**
- O Mega da v21 quebrava (D-LP4-5): o conserto saiu junto com o `gp`.
- A progressão pode travar (D-LP4-6, para a LP5; `web/app/scripts/medicoes/lp4_gazimon.json`):
  - um Rookie sem treino não vence o Gazimon;
  - com o treino típico, vence de 0 a 32 %;
  - o dono simulado que luta contra o próprio estágio não chega à taxa do Ultimate.

**Os testes novos:** `test/luta_poc_lp4.test.ts`:
- a chave e as versões;
- pela fonte, que nada do combate por turnos existe nem é importado;
- os itens;
- a Fábrica só v21.
Também `test/tamer.test.ts`, com o descarte 8 e a Fábrica de antes, e `e2e_capturas/luta_poc_lp4.spec.ts`, com as capturas.

## Resultado da LP5-0 (2026-11-10)

Worker: Claude Code (Opus 5.5), worktree `D:\Trab\digilab\v3-luta-poc-lp5`, branch `v3-luta-poc-lp5-0`, a pedido do Gerente de sprites e
luta. O plano é o `docs/PLANO_EQUILIBRIO_LUTA_POC.md`, APROVADO: as D-LP5-1 a D-LP5-10 foram decididas como recomendadas ("Tá, então faz toda a
recomendação aí que você deu", o Matheus, 2026-11-10, repassado). Os desvios estão em `docs/registro/2026-11.md`, seção "LUTA_POC, LP5-0".
Nenhum número do jogo mudou.

**O que entrou:**
- as faixas `86101…86505` (calibração) e `87101…87505` (conferência) na `FAIXAS_RESERVADAS`, num commit próprio;
- o H10 e o `pre_run --medicao` reconhecem `scripts/equilibrio_poc/`;
- a bancada nova `web/app/scripts/equilibrio_poc/`:
  - o candidato e o `CANDIDATO_V21`, que refaz os números do jogo (`web/app/test/equilibrio_poc_bancada.test.ts`);
  - o treino típico pelo `TreinoPet.sessao`;
  - os 10 grupos das metas;
  - o `medir_tudo`, em até 4 processos;
  - o `resumo_metas`;
  - a prova de reprodução, que refaz o `lp4_gazimon.json` campo a campo;
  - a sonda das formas do Motor.

**O ponto de partida** (a calibração, o candidato v21: 1 427 674 lutas;
`web/app/scripts/medicoes/equilibrio_poc/lp5_0/calibracao/resumo.json` e `resumo.md`). Passam 5 das 20 metas: P3, P4, P5, D3 e V2.

- **O treino decide tudo.** O pet típico vence o mesmo pet sem treino em 1,00 de cada estágio (T1). Contra as formas do estágio, 2 pontos
  levam o Rookie de 0,51 a 0,91, e do Champion em diante a curva chega a 1,00 aos 12 pontos (T3). O típico de um estágio vence as formas do
  estágio seguinte de 0,94 a 1,00, e o Rookie típico vence 0,92 contra os Ultimates (E1). A evolução não pesa contra o treino.
- **Os stats não pesam igual (T2).** Com 8 pontos num stat só, o fôlego dá 0,50 no Rookie e 0,60 no Ultimate, e a mira dá 0,74 e 0,81. O
  vigor, a força, a guarda e a recuperação dão de 0,96 a 1,00.
- **Os líderes (P1, P2).** O Gazimon trava: o Rookie típico vence 0,30. Por espécie, a brasa vence 0,55, o limo 0,47, a ferrugem 0,01 e o
  cirro 0,00. A Cidadela (o Myotismon, a série de 3) dá 0,72, com a pior espécie a 0,48. Os outros quatro líderes vencem de 0,97 a 1,00
  com o típico e perdem sem treino.
- **Os desafiantes, o sparring e a vida passam (P3, P4, P5).** O dono simulado que treina chega ao Mega nas 100 vidas.
- **As formas (V1, A1).** Sem treino, uma forma contra as outras do estágio vai de 0,10 a 0,77 no Rookie e de 0,001 a 0,97 nos outros
  estágios. As que atiram vencem as de perto de 0,26 a 0,44.
- **A duração (D1).** A mediana vai de 11,1 s a 16,2 s, abaixo dos 15 s em três estágios. O p90 fica entre 19,8 e 47,8 s, e 7 formas têm
  mediana abaixo de 8 s.
- **Os empates (D2).** Passam de 2 % em 4 Rookies, também fora do espelho (até 5,9 %).
- **Os torneios.**
  - A Liga sai em todas as tentativas (G1). A Torre tem o recorde mediano de 35 (G2).
  - A Fábrica, de Mega canônico contra Mega canônico, vence uma série em 0,018 (G3).
  - O Salão vence de 0,97 a 1,00 (G4).
- **O espelho (S1) reprova pelos empates, não pelo lado** (D-LP5-0-6). Sem os empates, o lado A fica em 0,48 a 0,51. Pela regra do plano,
  a rodada para aqui, e o achado vai ao Gerente antes de qualquer ajuste.

**As hipóteses da seção 1 do plano:**
- o treino que compõe: confirmada, a curva satura em poucos pontos;
- a mira que pesa pouco: confirmada em parte, porque o fôlego pesa menos ainda;
- o Gazimon que ficou forte sem o `eps`: o único líder que trava.

A calibração (LP5-1) espera a leitura do S1 pelo Matheus.

## Resultado da LP5-1 (a rodada 1 do mapeamento, parada pelo S1)

**A régua do S1** passou a contar só as lutas com vencedor (a D-LP5-11, decidida pelo Matheus em 2026-11-10). **A rodada 1** foi uma
grade em quatro partes (r1a a r1d, 49 pontos, `web/app/scripts/medicoes/equilibrio_poc/lp5_1/r1*/tabela.md`) e a medida inteira do
candidato escolhido, o `lp5_1_r1` (1 364 118 lutas em 252 s, 4 processos; `lp5_1/calibracao/resumo.md`). Os desvios são o D-LP5-1-1 a 6
(`docs/registro/2026-11.md`).

**Passam 4 das 20 metas: T3, E1, D1 e D3** (na LP5-0 passavam P3, P4, P5, D3 e V2).

- **O treino ganhou teto (T1, T3).** O expoente baixo com o ponto mais pesado satura a curva. O típico contra o mesmo pet sem treino fica
  em 0,77 no Rookie, 0,89 no Champion, 0,93 no Ultimate e 0,94 no Mega (o T1 pede de 0,80 a 0,97). No teto, contra as formas do estágio,
  fica de 0,72 a 0,86, e o maior degrau de 4 pontos é 0,17.
- **A evolução pesa mais que o treino (E1).** O típico contra o estágio seguinte fica de 0,13 a 0,16 (o teto, de 0,12 a 0,17), e dois
  estágios acima fica em 0.
- **A duração (D1):** a mediana fica de 16,4 a 17,3 s em todos os estágios, com o p90 abaixo de 20 s.
- **O que não fecha com o mapeamento** (o D-LP5-1-5):
  - o fôlego não pesa (T2): de 0,47 a 0,49;
  - a variedade vem da tabela das formas (V1): a amplitude fica de 0,41 a 0,43 do Champion ao Mega;
  - a espécie pesa (V2): a amplitude entre as espécies fica de 0,09 a 0,25, e a brasa é a pior no Rookie, no Champion e no Mega;
  - o sparring trava (P4): de 0,69 a 0,87 de média. Por isso só 15 de 100 vidas chegam ao Mega (P5), e 72 ficam no Champion;
  - os dois últimos passaram na LP5-0 só porque o pet típico vencia tudo.
- **De longe x de perto (A1):** o movimento base de 60 aproxima a soma de 0,50 (0,48 a 0,58; o A1 pede de 0,45 a 0,55).
- **Os líderes e os torneios** ficam para a LP5-2 e a LP5-3: os NPCs e os rivais dos torneios ainda têm os números da v21.

**A rodada para pelo S1** (D-LP5-1-4). Na Praia, o lado A fica de 0,42 a 0,46. Com o v21 (a LP5-0 relida pela régua nova) isso vale em
todos os estágios, e com o `lp5_1_r1` do Champion ao Mega. É o núcleo, não o candidato. A LP5-2 espera a decisão do Matheus sobre o S1 e sobre as metas que o
mapeamento não fecha.

### A distância do tiro (D-LP5-12)

O núcleo ganhou o `Tiro` desligado. A luta de hoje sai igual: o teste confere, e a fidelidade da LP1 dá 3276 de 3276. O candidato da
bancada leva o tiro, e a meta nova é o A2 (PROPOSTA, SEM FONTE). Os desvios são o D-LP5-1-7 a 10.

- **O ponto de partida do A2** (o v21, as 5 bases): contra quem luta de perto, a mediana da distância no tiro é 48 a 52 px, e de 26 % a
  46 % dos tiros saem a 48 px ou menos. Contra quem atira, a mediana é 132 px. O A2 pede pelo menos 90 px e no máximo 15 %.
- **As grades:** o recuo na preparação do tiro é a alavanca que move. A 2 vezes o movimento, o A2 passa (100 a 108 px, 6 % a 8 %).
  Mas as que atiram passam a vencer as de perto de 0,67 a 0,92 (o A1), e o S1 na Praia não muda.
- **A ordem das fases não muda:** o tiro é parte do mapeamento (LP5-1), antes dos NPCs. Mas o ponto de partida ganha o A2, e o
  `lp5_1_r1` precisa ser medido de novo com o tiro, nas rodadas 2 e 3 da LP5-1.

### As rodadas 2 e 3 e o fim da LP5-1

O Matheus aprovou as 4 decisões ("Aprovo as 4"; a D-LP5-13). **O candidato da LP5-1 é o `lp5_1_r2`:**
- o mapeamento da rodada 1;
- o tiro: distância mínima 110 px, recuo na preparação a 2 vezes o movimento;
- o dano do projétil a 0,7.

A medida inteira está em `web/app/scripts/medicoes/equilibrio_poc/lp5_1_r2/calibracao/resumo.md` (1 412 931 lutas). Os desvios são o
D-LP5-1-11 a 16.

- **Passam 6 das 21 metas: T1, T3, E1, D1, D3 e A2.**
  - **O treino:** o T1 dá 0,81, 0,86, 0,93 e 0,94, do Rookie ao Mega.
  - **A evolução (E1):** o típico contra o estágio seguinte dá de 0,15 a 0,17.
  - **A duração (D1):** a mediana fica de 21 a 24 s.
  - **O tiro (A2):** a mediana fica de 100 a 108 px, com 7 % a 9 % dos tiros a 48 px ou menos.
- **O que fica para o Matheus** (o D-LP5-1-16):
  - o V2: a amplitude fica de 0,07 a 0,22, e a rodada 3 não a move;
  - o A1: a soma fica de 0,45 a 0,56, mas os mapas vão de 0,11 a 0,77, pelas regras dos mapas;
  - o D2: os empates ficam em 3,6 %;
  - o S1: o Ringue do Rookie fica em 0,449.
- **A rodada 3** (16 pontos) não mudou nenhum número.

A LP5-1 fecha pela regra das 3 rodadas. A LP5-2 (os NPCs, o sparring e a vida) parte do `lp5_1_r2`. Nele, o P4 dá de 0,69 a 0,86 de
média, e só 10 de 100 vidas chegam ao Mega.

### A esquiva ligada (D-LP5-16)

O Matheus: "pode ligar esquiva nova e fazer o merge". O candidato `lp5_1_esq` é o `lp5_1_r2` com a esquiva da D-LP5-14 ligada, no
ponto `m6_f6_p0` da grade `lp5_1/r4e`, o único da grade com 6 metas. A leitura do golpe de perto fica desligada: ligada (0,35), o E1
reprova e o A1 pende para quem atira. A medição inteira (`lp5_1_esq/calibracao`, commit `dea4e71c`, 1 412 957 lutas) dá 8 de 21 metas,
contra 6 do `lp5_1_r2`:

- **passam a mais o P4 e o S1.** O P4: a fração dos pets a 0,8 ou mais vai de 0,45/0,46 a 0,85/0,98 no Champion e no Ultimate. O S1:
  o Ringue do Rookie vai de 0,449 a 0,451, na beira da faixa;
- **a mira ganha peso:** no T2, de 0,53 a 0,62 no Rookie e de 0,53 a 0,60 no Ultimate. O fôlego segue morto (0,48 e 0,49);
- **o P5 sobe, mas reprova:** 19 de 100 vidas chegam ao Mega, contra 10;
- **nenhuma meta que passava cai:** o T1 dá 0,83/0,90/0,94/0,96, o E1 0,17, a mediana do D1 de 21,6 a 24,7 s;
- **o que piora um pouco:** o V2 do Rookie (de 0,21 a 0,25, aceito como reprovado na D-LP5-15) e o A1 do Ultimate (de 0,56 a 0,58).

No jogo, a luta segue no v21: a esquiva só entra com o v22, na LP5-5. A LP5-2 parte do `lp5_1_esq`.

## Resultado da LP5-2 (as rodadas 1 e 2 do total dos NPCs, paradas num ponto de decisão)

O Matheus: "Sim, segue". A LP5-2 parte do `lp5_1_esq`. Pela D-LP5-9, o total de cada NPC vem primeiro, e a divisão dos stats só entra
se o total não fechar o P1 a P3 em 2 rodadas. As duas grades (`lp5_2/r1` e `lp5_2/r2`) multiplicam os 10 totais pelo mesmo fator. Cada
NPC só depende do total dele, então uma grade dá a curva de cada um. As grades rodam só o grupo `lideres`, com 2 bases da calibração
(86101, 86201), cerca de 18 000 lutas por ponto e 4 processos.

- **A rodada 1** (de 0,5 a 1,3 vez o total de hoje) quase não move nada. O Gazimon sem treino vai de 0,43 a 0,30, e o típico de 0,61 a
  0,50.
- **A rodada 2** (de 0,1 a 8 vezes) também não fecha. Nenhuma das metas P1, P2 e P3 passa em nenhum ponto. Dois NPCs passam sozinhos:
  - **o MarinBullmon** com 1,3 vez o total (143): sem treino 0,18, típico 0,74, pior espécie 0,64;
  - **o Tortomon** com 3 vezes o total (216): sem treino 0,31, típico 0,77.
- **Por que o total não fecha:**
  - **a alavanca ficou fraca.** Com os expoentes da LP5-1 (0,02 no vigor e na força, 0,14 na mira e no fôlego), mesmo 8 vezes o total
    move pouco cada razão;
  - **a distância entre o pet sem treino e o típico é curta.** Ela fica em 0,45 ou menos contra qualquer NPC. O T1 (o típico contra o
    mesmo pet sem treino) é 0,83 no Rookie, e com ele a conta logística dá uns 0,55 para o típico quando o pet sem treino fica em 0,20.
    O P1 pede 0,70: só fecharia com o T1 perto de 0,93;
  - **a pior espécie é a forma, não o total.** O cirro do Rookie fica de 0,00 a 0,16 contra o Gazimon em todo o caminho, e a brasa
    passa de 0,85. É o mesmo achado do V2, aceito como reprovado na D-LP5-15.

A divisão dos stats (a D-LP5-9) mexe no mesmo lado do NPC e não encurta a distância do pet, nem muda a forma. Por isso a fase parou
aqui, com a decisão levada ao Matheus no PR. Nenhum número do candidato mudou.

### O critério novo e a rodada 3 (D-LP5-17)

O Matheus: "Segue sua recomendação". O critério do P1 a P3 passou a sair do T1 do `lp5_1_esq`: o líder fica no meio do caminho entre o
pet sem treino e o típico, na escala logística, com 0,10 de folga. Os limites são 0,41/0,59, 0,35/0,65, 0,30/0,70 e 0,27/0,73, do
Rookie ao Mega, e o desafiante tem +0,15 e +0,05. A pior espécie vai só à leitura. O código está em
`web/app/scripts/equilibrio_poc/criterios.ts`, com teste.

- **A rodada 3** (`lp5_2/r3`): 7 pontos, cada NPC com a própria faixa de totais, 3 bases (86101, 86201, 86301), cerca de 28 000 lutas
  por ponto.
  - **o Gazimon** passa de 0,65 a 0,8 vez o total. Pela regra de escolha (a maior folga), fica em 0,8 vez: 76,8;
  - **o MarinBullmon e o Tortomon** já passam com o total de hoje, então não mudam;
  - **os outros 7** (o Guardromon, o Youkomon, o Myotismon, o Piedmon, o Devidramon, o Puppetmon e o Machinedramon) não passam em
    nenhum total. A distância entre o pet sem treino e o típico contra eles fica de 0,10 a 0,25, e o critério pede de 0,20 a 0,46;
  - **com 3 bases, o Puppetmon e o Machinedramon dão uns 0,09 a mais no sem treino** que com 2, no mesmo total. A mistura das formas
    Mega muda de uma base para outra, e o erro passa do binomial.
- **A medida inteira do `lp5_2`** (`lp5_2/calibracao`, commit `9270f774`, 1 412 957 lutas) dá **9 de 21 metas**: as 8 do `lp5_1_esq` e
  o P1 (o Gazimon: sem treino 0,380, típico 0,627). O P2 e o P3 reprovam pelos 7 NPCs de cima.
- **O P5 não lê as alavancas da LP5-2.** O dono simulado só luta na Arena, então o total dos NPCs não entra na vida. O treino dos
  rivais da Arena está em 0 e só sobe, o que deixaria os rivais mais fortes. O P5 segue em 19 de 100 vidas no Mega: 73 param no
  Champion. Lá, o pet da vida faz as 10 lutas de sparring e vence 0,67 delas (670 de 1 000), contra 0,85 do pet típico na bancada
  `sparring`. A causa provável é a vida, não o rival (a condição pela saúde, o caráter, o treino perto de 21 pontos e não 22), mas ela
  não foi medida.

### A divisão dos stats e a leitura da vida (D-LP5-18)

O Matheus aprovou as duas recomendações ("Aprovo como recomendadas.").

**A divisão dos stats dos 7 NPCs não fecha nenhum deles.**
- A grade `lp5_2/r4` cruzou 12 divisões com 4 totais.
- O mais perto foi o Devidramon: 0,513 sem treino e 0,686 com o típico (`fol_t2`), contra ≤ 0,50 e ≥ 0,70; falta 0,014.
- Depois vêm o Guardromon (falta 0,039), o Youkomon (0,070), o Myotismon (0,109), o Piedmon (0,111), o Machinedramon (0,176) e o
  Puppetmon (0,186).
- Os 7 ficam reprovados e vão à investigação do núcleo e à tarefa da tabela das formas. O `lp5_2` não muda.

**A leitura da vida explica o P5.**
- As 100 vidas chegam ao Champion como colosso. O colosso típico vence 0,712 do sparring, contra 0,885 a 0,899 das outras formas, e o
  0,85 da bancada é a média das quatro.
- O dono luta com o treino em ~14 pontos, não em 22; com os 22, a taxa sobe só +0,05.
- A condição é 1,05, um bônus, e o caráter quase não pesa.
- Com 0,67 por luta, a chance de ≥ 8 de 10 é de 0,31, perto das 27 vidas que passam.
- Os números estão em `web/app/scripts/medicoes/equilibrio_poc/lp5_2/leitura_vida/` e no registro (D-LP5-18-1 a 5).

## Resultado da LP5-3 (os torneios, parada num ponto de decisão)

A LP5-2 fechou com o `lp5_2` (a D-LP5-19: "Sim, segue"). A LP5-3 parte dele, e a alavanca dela é o treino dos rivais dos torneios.

**A grade `lp5_3/r1`** pôs o treino dos rivais do Salão, da Liga, da Torre e da Fábrica em 0, 5, 10 e 20 pontos.

| ponto | G1 títulos | a Liga, o máximo de vitórias | G2 recorde mediano | G3 séries | G4 (Rookie/Champion/Ultimate/Mega) |
|---|---|---|---|---|---|
| 0 | 0 | 4 de 6 | 1 | 0,002 | 0,678/0,838/0,927/0,832 |
| 5 | 0 | 4 | 1 | 0,001 | 0,532/0,760/0,843/0,785 |
| 10 | 0 | 4 | 2 | 0,003 | 0,414/0,617/0,753/0,735 |
| 20 | 0 | 4 | 2 | 0,002 | 0,330/0,438/0,629/0,623 |

**A alavanca só deixa os rivais mais fortes,** e o G1, o G3 e o G4 pedem rivais mais fracos.
- Na Liga, o pet vence a 1.ª luta, mas a vida passa sem cura, e ele não chega à 6.ª.
- Na Fábrica, o alugado e os rivais são Megas sem treino, e o treino só entra nos rivais.
- A Torre melhora um pouco com o treino dos rivais, mas não chega ao recorde 3, e a causa não foi medida (D-LP5-3-3).

Nenhum número muda, e a decisão está no PR #784.

### O fator dos rivais dos torneios (D-LP5-20)

O Matheus aprovou a (a): "Sim, roda". A grade `lp5_3/r2` pôs um fator abaixo de 1 nos stats dos rivais dos quatro torneios, sem mexer
no alugado da Fábrica.
- **O Salão (G4) fecha em 0,8.** O candidato `lp5_3` é o `lp5_2` com esse fator, e passa em 10 de 21 metas.
- **A Liga, a Torre e a Fábrica não fecham nem com 0,1.** Em 0,1, a Liga para na Floresta ou na Praia, e a Torre perde a 1.ª luta no
  Ringue em 0,53 das tentativas. Quem decide as séries são as regras dos mapas e a vida sem cura, não os stats do rival.
- A (b), aceitar o G1 a G3 como reprovados, volta ao Matheus no PR #789 antes de valer.

## Resultado da LP5-4 (a conferência)

A calibração fechou com o `lp5_3` (a D-LP5-21: "Sim, segue"). A conferência rodou uma vez, nas sementes 87xxx, no commit `d4debac3`.
A tabela inteira está em `web/app/scripts/medicoes/equilibrio_poc/lp5_4/conferencia/comparacao.md`.

| | calibração | conferência |
|---|---|---|
| metas que passam | 10 de 21 | 9 de 21 |
| P1, o Gazimon (sem treino / típico) | 0,380 / 0,627 | 0,391 / 0,611 |
| P4, os pets do Champion acima de 0,8 | 0,85 (passa) | 0,78 (falha) |
| P5, as vidas no Mega | 0,19 | 0,22 |
| G4, o Salão | 0,740/0,852/0,940/0,844 | 0,722/0,865/0,927/0,840 |

**O P4 é a única meta que muda de lado,** por uma diferença que cabe no erro de 100 pets. As outras ficam no mesmo lado. A medida rodou
duas vezes, com os mesmos dados, por um arquivo escrito no meio da primeira (D-LP5-4-2). Nenhum número muda; o próximo passo é a LP5-5
(o candidato no jogo, pela D-LP5-7), com a decisão do Matheus.

## Resultado da LP5-5 (o `lp5_3` no jogo, como a v23)

O Matheus: "Sim, liga". Os ovos novos nascem v23: a v22 (a ilha com água) com a luta da rodada de equilíbrio.

- **O que entra na v23:** o mapeamento dos stats com os expoentes, a esquiva, a distância do tiro, o Gazimon em 76,8 e o rival do
  Salão com o fator 0,8 (`motor/luta_poc.ts`, `LUTA_V23`; PROPOSTOS, SEM FONTE).
- **O que fica:** os pets v21 e v22 lutam com os números deles; o gabarito da v22, gravado antes num commit próprio, sai igual depois
  da mudança. A Fábrica, que é do Tamer, fica com os números da v21 (D-LP5-5-5).
- **A prova:** o Motor v23 e a bancada com o `lp5_3` dão os mesmos números e a mesma luta. A suíte do web passa inteira.
- **O que segue reprovado:** a Liga, a Torre, a Fábrica e o P5, para a tarefa do núcleo e da tabela das formas.
- **Um aviso:** o plano da ilha grande (#796) também reserva a v23 (D-LP5-5-7).

## Resultado da LP3c (2026-11-10)

Worker: Claude Code (Opus 5.5), worktree e branch `v3-luta-poc-lp3c`, a pedido do Gerente de sprites e luta. O pedido seguiu a revisão dos
sprites da luta (Fable 5.2) e a decisão do Matheus "Desenho agora, motor na LP5". O Matheus aprovou as capturas em 2026-11-10 ("Aprovo,
abre o PR"; o recado chegou pelo Gerente). Os desvios estão em `docs/registro/2026-11.md`, seção "LUTA_POC, LP3c".

**Só o desenho.** Mudaram só `src/telas/lutar/palcoPoc/desenhoPoc.ts`, `visualPoc.ts`, `src/lutaPocTela.ts` e `src/estilo/luta_poc.css`.
O motor (`motor/arena/`), o replay e os gabaritos ficaram byte a byte. A distância do tiro, que deixa o atirador encostar no alvo, é da
LP5.

**O que mudou:**
1. **A origem do tiro:** o tiro nasce na frente do sprite, no quadro do disparo. A frente é lida nos pixels do `Attack_1`: de 20 a 108 px
   do sprite a partir do meio do corpo, com mediana 50, em 53 formas e habilidades que atiram. Antes, o tiro nascia a 18 px do mundo do
   centro. O acerto cai na borda do corpo do alvo. No meio do voo, o desenho segue o caminho do motor, com a diferença das duas pontas
   repartida pela fração do voo (`VooPoc.f`). O tiro que nasce e acerta no mesmo passo, que a simulação nunca põe em `L.projeteis`,
   ganha um voo montado do dano.
2. **O voo visível:** a até 3 passos do disparo ou do acerto, a tela anda 1 passo por quadro (`RITMO_TIRO`, `passosDoTiro`). Os passos e
   o fim são os mesmos, e o movimento reduzido fica como antes.
3. **O projétil das 5 formas da LP-8:**
   - o efeito que voa fica 2,2× maior e é somado ao fundo duas vezes;
   - ganha o brilho e a cabeça do elemento.
4. **A câmera e a escala:**
   - a escala inteira dos sprites é fixa na luta;
   - a câmera conta a altura do corpo (Idle, Run, Stun e `Attack_1`);
   - no deitado, os corpos ficam centrados entre o HUD e o dock.
   WarGreymon × SlashAngemon cabe inteiro em 1920×950.
5. **O sprite pelo corpo:** a caixa é posta pelo meio do primeiro quadro do Idle, não pelo meio da caixa. Os pés ficam na linha do corpo.
6. **O fim:** o `Die` segura o último quadro com corpo, e o vencedor vai ao `Idle`.
7. **Os menores:**
   - o número do dano e o estouro ancoram no corpo;
   - no celular, o nome do HUD vai em até duas linhas, a 10 px, sem reticências.

**Os números novos** são PROPOSTOS, SEM FONTE: `DESENHO_POC` (pes 4, margem [70, 24], nivelSprite 0,5, hud 84, dock 96), `TIRO_POC` e
`RITMO_TIRO`.

**As capturas:** 5 pares, em 1920×950 e em 390 px, com o antes e o depois e as tiras de tiro. Ficam fora do git, na pasta de notas do
Gerente (`lp3c_capturas/`), com os scripts que as refazem.

**O teste novo:** `web/app/test/luta_poc_lp3c.test.ts`. Ele confere:
- que o ritmo dos tiros não muda o fim dos 5 pares;
- a fração do voo;
- que todo dano de tiro tem um voo;
- a posição pelo corpo;
- o `Die` segurado e o `Idle` do vencedor.

**O que fica de fora:**
- **A distância do tiro:** é do motor, na LP5.
- **A sobreposição no golpe de perto:** o que resta vem do avanço desenhado no próprio `Attack_1` (o Veemon), e não sai sem mexer na
  pose.
- **O HerculesKabuterimon:** com 19 letras, o nome ainda quebra no meio da palavra no celular.
- **O atlas novo `digilab_atlas_up_luta`:** ligá-lo é decisão do Matheus. Ele daria `Hurt_1` e `Hurt_2`, `Knockback`, `Win` e `Lose`
  nos 262 sprites.

## Resultado da LP6-1 (2026-11-11: o núcleo do golpe de apoio e da elipse por estágio)

O plano é o `docs/PLANO_LP6_SEGUNDO_GOLPE.md`; as interpretações estão no `docs/registro/2026-11.md` (D-LP6-1-1 a 9). Nada liga no jogo:
o jogo segue na v23.

- **O golpe de apoio** (a chave `apoio` da entrada da luta, desligada):
  - a tabela `web/app/motor/arena/formas.ts` ganha o `apoio` e o `msApoio` de cada forma, gerados pelo `tools/gerar_tabela_arena.py`;
  - em `sim.ts`, o apoio de perto de quem atira sai abaixo da `distMin` do tiro, e o tiro fraco de quem bate de perto sai com o alvo
    além do alcance por 1,5 s;
  - o dano é 0,6 do golpe principal, e a recarga é 2 vezes o ciclo do ataque;
  - a esquiva lê o apoio de perto como o golpe de perto.
- **A elipse por estágio** (a chave `arenaPorEstagio`, desligada): o fator é 1,15 no Ultimate e 1,3 no Mega, pelo maior estágio dos dois.
  A cena escala junto, e os corpos não.
- **Os números** são PROPOSTOS, SEM FONTE: `APOIO_LP6`, `APOIO_TABELA` e `ARENA_POR_ESTAGIO_LP6`, em `constantes.ts`.
- **Os testes:**
  - `test/arena_lp6_gabarito.test.ts`: com as chaves desligadas, 384 lutas da v21 e da v23 saem byte a byte iguais ao gabarito,
    gravado antes da mudança;
  - `test/arena_lp6.test.ts`: a tabela, o replay bit a bit com as chaves ligadas, cada regra do apoio e a escala da elipse.
- **O que fica para depois:** o palco (LP6-2), a calibração (LP6-3) e a versão nova do pet (LP6-4).

## Resultado da LP6-2 (2026-11-11: o golpe de apoio e a elipse maior no palco)

Só desenho, em `web/app/src/telas/lutar/palcoPoc/` (`desenhoPoc.ts` e `visualPoc.ts`) e `web/app/src/lutaPocTela.ts`; o núcleo não
muda. As interpretações estão no `docs/registro/2026-11.md` (D-LP6-2-1 a 8). O Matheus aprovou as capturas ("Aprovo, conserta"), com o
conserto da borda cortada antes do PR.

- **O apoio de perto do atirador:** o `Attack_1` inteiro, mais rápido, com um avanço curto do corpo; o acerto é o do núcleo.
- **O tiro fraco de quem bate de perto:** o projétil genérico, com metade do pixel e do rastro do tiro de verdade, saindo da frente do
  sprite.
- **A elipse maior:** o palco desenha a elipse do núcleo, e o mapa cresce junto. O nível 0 da câmera mostra a arena inteira; de perto, o
  zoom e os sprites são os de sempre.
- **A borda cortada do export:** a explosão do golpe do Gallantmon terminava numa linha reta já na v23. O palco esfuma a borda onde o
  quadro encosta na caixa (`BORDA_CORTADA`), sem inventar a arte.
- **As capturas:** `&palco_lp6=ligadas|desligadas` na luta montada; os vídeos ficam fora do repositório.
- **Os testes:** `test/luta_poc_lp6_palco.test.ts`.

## Resultado da LP6-3 (2026-11-11: a calibração do golpe de apoio e da elipse por estágio)

PR #834, em rascunho. O plano e a régua estão na seção 8 do `docs/PLANO_LP6_SEGUNDO_GOLPE.md`, e os desvios são os D-LP6-3-1 a 9 em
`docs/registro/2026-11.md`. Nenhuma versão de pet liga as chaves: isso é a LP6-4.

- **O candidato:** o `lp6_3_u120`, que é o `lp5_3` com duas mudanças.
  - **O apoio** só existe na luta em que o maior estágio dos dois é Ultimate ou Mega. Ele tem dano 0,6, recarga de 3 vezes, espera do
    tiro fraco de 1 500 ms, clipe de 0,6 e não tem o recuo.
  - **A elipse** é 1,2 no Ultimate e 1,4 no Mega.
  - Os números são PROPOSTOS, SEM FONTE.
- **Na calibração:** 10 de 21, as mesmas 10 do `lp5_3` (commit `c0b99b68`).
- **Na conferência, uma vez, nas 87xxx:** 9 de 21, as mesmas 9 do `lp5_3` na LP5-4 (commit `a52fa0cf`).
  - Só o P4 muda de lado: os pets do Champion acima de 0,8 vão de 0,85 a 0,78, como na LP5-4.
- **O que a LP6 move:**
  - **O A1 do Ultimate e do Mega** fica em 0,526 e 0,465 na conferência, contra 0,577 e 0,477 do `lp5_3`.
  - **Os mapas fora da faixa do A1:** no Ultimate, caem de 5 para 2, o Deserto e o Ringue. No Mega, fica só o Ringue.
  - **O S1** passa em todos os estágios.
  - **No Rookie e no Champion,** a luta é a mesma do `lp5_3`.
- **O caminho até ele:**
  - **R0:** o apoio em todos os estágios dá 6 de 21. O apoio de perto prende quem atira junto do inimigo.
  - **R1:** a regra do recuo (D-LP6-3-4) e a grade do apoio também dão 6 de 21. 83 % dos recuos acabam pelo tempo.
  - **R2:** o apoio só no Ultimate e no Mega (D-LP6-3-7) dá 9 de 21 nas grades de 3 bases.
  - **A escolha:** três finalistas medidos inteiros, pelo critério registrado antes (D-LP6-3-8). O `lp6_3_u115`, com a elipse do plano,
    reprova o S1 no Deserto do Ultimate.
- **Decisões que mudaram:**
  - **a decisão 2 (seção 7):** nenhum Digimon tem o apoio no In-Training, no Rookie e no Champion;
  - **a decisão 4, nos números:** a elipse de 1,15 e 1,3 passa a 1,2 e 1,4 (D-LP6-3-9), PROPOSTO até o Matheus decidir.
- **No núcleo, atrás da chave do apoio:**
  - o `desde`, o apoio pelo estágio;
  - o `recua`, a regra do recuo, desligada;
  - testes em `web/app/test/arena_lp6_recuo.test.ts`.
- **Ficam para depois:**
  - o A1 do Rookie e do Champion por mapa (o Castelo e o Ringue) e o Ringue de todos os estágios, com a investigação do núcleo;
  - o V1, o V2, o T2, o D2, o G1 a G3, o P2, o P3 e o P5, como na LP5;
  - as capturas do palco com a elipse 1,2/1,4, antes da LP6-4.

## Resultado da LP6-4 (2026-11-11: a luta da LP6 no jogo, a v29)

- **As capturas** do palco com a elipse 1,2/1,4 (32 lutas, desktop 1920×950 e celular 390×844, em `D:\Trab\digilab\capturas_lp6_4`, fora
  do git) foram aprovadas pelo Matheus: "Aprovo, segue" (2026-11-11, repassado pelo Gerente).
- **A versão é a v29: a v28 (o grupo de dois com o sono que segura, #861) com a luta da LP6.**
  - A tabela `LUTA_V29` (`web/app/motor/luta_poc.ts`) é a `LUTA_V23` com o apoio só no Ultimate e no Mega, sem o recuo (`APOIO_LP6_3`),
    e a elipse 1,2 no Ultimate e 1,4 no Mega (`ARENA_POR_ESTAGIO_LP6_3`). São os números do `lp6_3_u120`, PROPOSTOS, SEM FONTE.
  - O ovo do brasão choca o grupo v29 (`VERSAO_GRUPO`, `src/jornada.ts`). O ovo de um pet só segue na v27, com a luta da v23.
  - A v27 e a v28 são do sono que segura (#855, #861); a LP6 ficou com a v29, em cima da v28 (D-LP6-4-1). O PR depende do #861.
- **Os pets vivos não mudam:** os v21 a v28 seguem com a luta deles. Os gabaritos foram gravados antes da mudança
  (`test/lp6_4_gabaritos.test.ts`): as vidas e os torneios da LP2 na v24, v25 e v27, e a vida que chega ao Ultimate e ao Mega e luta neles
  (`test/lp6_4_luta_alta.ts`) na v24 a v28, a v26 e a v28 pelo primeiro pet do grupo.
- **Os testes da v29** (`test/lp6_4_v29.test.ts`): a tabela; os grupos v26 e v28 de antes abrem pelo save como eram; a vida do grupo v29
  igual à do v28 até a primeira luta no Ultimate e diferente depois; o palco refaz as lutas do Mega com o apoio e a arena da tabela (o
  `ResultadoLutaPoc` os guarda); o gabarito da vida alta e o replay.

## A investigação do núcleo, N0: o plano (2026-11-12)

O plano é o `docs/PLANO_LUTA_NUCLEO.md`, PROPOSTO, com as decisões D-N-1 a D-N-7. Ele cobre as metas que a LP5 e a LP6 não fecharam e
separa cada uma pela causa: o núcleo, o mapa, a série sem cura, a tabela das formas ou a régua. As etapas vão da N1 à N5: as releituras e as
contas, as lutas fixas, as chaves desligadas com o gabarito das versões vivas, os contrafactuais e o relatório. Nenhum número do jogo muda.
Os desvios estão em `docs/registro/2026-11.md`, seção "LUTA_POC, N0".

## Resultado da N1 e da N2 da investigação do núcleo (2026-11-12)

O plano é o `docs/PLANO_LUTA_NUCLEO.md`, APROVADO (D-N-1 a D-N-7). Os desvios são o D-N12-1 a 6, em `docs/registro/2026-11.md`. Nenhum
número do jogo mudou, nenhuma chave entrou no núcleo e nenhuma grade rodou.

**Os artefatos:**
- **a N1:** `web/app/scripts/medicoes/luta_nucleo/n1/leitura.json` e `leitura.md`, feitos pelo `scripts/equilibrio_poc/leitura_nucleo.ts`;
- **a N2:** `web/app/scripts/medicoes/luta_nucleo/n2/<candidato>.json`, feitos pelo `scripts/equilibrio_poc/lutas_fixas_nucleo.ts`.

A N2 rodou com a luta da v21 (`v21`), a da v23 (`lp5_3`) e a da v29 (`lp6_3_u120`): 95 280 lutas por luta, de 56 a 61 s cada, em 1
processo, nas bases 92101 a 92505.

### A N1: o atributo (as releituras)

**O atributo decide quase toda luta.** A leitura preliminar do plano se repete com artefato:
- na v23 e na v29, a forma com vantagem vence de 0,991 a 0,999 dos pares, e a com desvantagem de 0,001 a 0,009;
- na v21, de 0,82 a 0,99 e de 0,01 a 0,12.

**O V1 é quase todo o atributo.** A taxa de cada forma, prevista só pela classe dos pares dela, explica de 0,83 a 0,97 da variância do V1 na
v23 e na v29 (o R²). Na v21, de −0,18 a 0,19.

**Os NPCs.** Pela H-ATR, o "sem treino" tem um piso igual à fração de pets com vantagem, e o típico tem um teto igual a 1 menos a fração com
desvantagem.
- **Não cabem pelo atributo,** qualquer que seja o total: o Guardromon (o piso 0,42 contra o limite 0,35), o Piedmon (0,48 contra 0,27), o
  Puppetmon e o Machinedramon (0,48 contra 0,42) e o Youkomon (o teto 0,58 contra 0,65).
- **O Devidramon cabe,** mas o típico nos pares neutros fica em 0,66.
- **O Myotismon não é o atributo:** com vantagem, o típico vence a série de 3 do Castelo só em 0,515.

**O A1 nos pares neutros** não muda o Ringue e o Castelo. No Ringue fica de 0,04 a 0,17, e no Castelo de 0,12 a 0,47. Os dois são do mapa,
não do atributo: a alternativa H-ATR do A1 cai.

**O colosso (P5):**
- o Growlmon (Virus) tem 0,50 dos rivais do Champion com vantagem sobre ele, e vence 0,52;
- os três colossos Vaccine têm 0,19 e vencem de 0,63 a 0,78;
- o Gatomon, o único de perto, fica em 0,63, contra 0,76 e 0,78 dos outros dois Vaccine.

### A N2: as lutas fixas

| pergunta | v21 | v23 | v29 | a leitura |
|---|---|---|---|---|
| **a série (G1):** a soma das perdas da vida nas 6 lutas da Liga, com a vida cheia em cada | 0,22 | 3,30 | 3,48 | na v23, o vencedor fica com 0,42 a 0,58 da vida. A Liga pede menos de 1 |
| a mesma, com o fator 0,1 nos rivais | 0,001 | 2,62 | 2,72 | o fator tira 4,5 % da vida do rival (2 627 → 2 509) |
| **a Torre (G2):** o Mega típico vence a 1.ª luta do Ringue | 1,00 | 0,36 | 0,31 | 98 % e 96 % das derrotas têm a queda do pet |
| as quedas do pet na Torre pelo pulo da esquiva | — | 77 % | 90 % | o rival sem treino quase não cai |
| **o Ringue (A1):** as quedas de quem atira, por luta | 0,46 a 0,89 | 3,10 a 3,35 | 1,56 a 3,20 | na v23, 54 % a 61 % pelo recuo na preparação do tiro e o resto pela habilidade. Na v21, todas pela habilidade |
| **o Castelo (A1):** a runa pega por luta | 0,34 a 0,58 (de perto) | 0,001 a 0,003 | 0,002 a 0,1 | ninguém pega a runa na v23, e o A1 fica em 0,17 a 0,39 assim mesmo |
| os tiros no pilar, por luta | 0,05 a 0,41 | 0,43 a 0,50 | 0,15 a 0,50 | pouco para explicar o A1 |
| **os empates (D2):** os que vêm do tiro de quem já caiu | 65 % a 82 % | 77 % a 92 % | 77 % a 93 % | o resto são os dois no mesmo passo; o dano do mapa quase nunca |
| **o fôlego (T2):** 8 pontos no fôlego contra o mesmo pet sem treino | 0,53 e 0,59 | 0,49 e 0,44 | 0,49 e 0,44 | Rookie e Ultimate |
| o pulo médio da esquiva do pet com o fôlego | 46 e 48 px | 99 e 98 px | 99 e 118 px | o maior pulo chega a 312 px |
| os pulos que acabam na cerca | 25 % e 31 % | 99,5 % | 99,5 % | |
| **o espelho (S1):** o lado A, nas lutas com vencedor, no Campo | 0,49 a 0,51 | 0,47 a 0,50 | 0,43 a 0,50 | sem lado claro |
| o mesmo, na Praia | 0,41 a 0,45 | 0,45 a 0,53 | 0,44 a 0,53 | na Praia, o lado A bate mais na rocha da direita |

### As hipóteses depois da N1 e da N2

| hipótese | o que ficou | as metas |
|---|---|---|
| **H-ATR** (o atributo) | **confirmada** pela N1 | V1, V2, P2, P3 (6 dos 7 NPCs), P5 (o Growlmon) |
| **H-SÉRIE** (a série sem cura) | **confirmada.** A causa é o mapeamento da v23: o pet típico é uns 5 % mais forte que o rival canônico, e cada vitória custa metade da vida. Não é o mapa | G1, G3, a Cidadela (o Myotismon) |
| **H-RINGUE** (a borda) | **confirmada.** O recuo na preparação do tiro (o `recuaNaPrep` 2 da v23) e a habilidade (o empurrão 7) jogam quem atira para fora | A1 no Ringue, G2 |
| **H-PULO** (a agilidade sem teto) | **confirmada.** Com o fôlego treinado, o pulo bate na cerca quase sempre, e no Ringue leva o pet para fora | T2, G2 |
| **H-TIRO-MORTO** | **confirmada** | D2 |
| **H-PILAR** (o Castelo) | **não confirmada.** Na v23 a runa quase não é pega, e os tiros no pilar são poucos. A causa do Castelo fica aberta | A1 no Castelo |
| **H-ORDEM** (o lado A primeiro) | **não confirmada.** No Campo o lado A fica perto de 0,5 | S1 |
| **H-ROCHA** (a Praia) | **fraca.** O lado A bate mais na rocha da direita, mas o sinal do S1 muda de estágio para estágio na v23 | S1 na Praia |

### As chaves que a N2 confirma (para a D-N-5)

**DECIDIDA (2026-11-12):** o Matheus, "As 4 (Recommended)" (repassado pelo Gerente). As 4 entram na N3, todas desligadas no jogo.

São PROPOSTAS, SEM FONTE. Cada uma iria atrás de uma chave desligada na `EntradaLuta`, com o gabarito das versões vivas antes (a seção 4
do plano):

1. **`forcaAtr`:** o `forca` do atributo na entrada. A N4 mede 1,0, 1,15 e 1,25. Ela move o V1, o V2, os NPCs e o P5.
2. **`tiroDoMorto`:** o projétil de quem caiu não causa dano. Ela move o D2.
3. **`puloMax`:** um teto para o pulo da esquiva, em px. Ela move o T2 e a Torre.
4. **`bordaRingue`:** no Ringue, o recuo (também o da preparação do tiro) e o pulo param antes da borda. Ela move o A1 do Ringue e a Torre.

**Ficam fora:** a `ordemAlterna` (não confirmada) e as chaves de mapa da Praia e do Castelo, porque a causa do Castelo não foi achada.
**A série sem cura não tem chave do núcleo.** A causa é o mapeamento (o `gama`), que é da calibração geral. A regra das séries sem cura
(a decisão 5 da LP2) fica.

## Resultado da N3 da investigação do núcleo: as 4 chaves (2026-11-12)

A D-N-5 foi decidida pelo Matheus: "As 4 (Recommended)". As chaves entraram no núcleo (`web/app/motor/arena/`), cada uma num commit
próprio, com os testes dela, e todas desligadas. **Nenhuma versão de pet liga uma delas:** a luta do jogo não muda. Os números são
PROPOSTOS, SEM FONTE. Os desvios são o D-N3-1 a 4, em `docs/registro/2026-11.md`.

**O gabarito**, num commit próprio antes da primeira chave (`77296829`):
- 576 lutas: os 8 mapas × os 12 pares da LP6-1 × 2 sementes × as 3 tabelas da luta. São a `LUTA_V21` (a v21 e a v22), a `LUTA_V23` (a v23
  à v28, a v30, a v32 e a v35) e a `LUTA_V29` (a v29, a v31 e a v36), com o tiro, a esquiva, o apoio e a elipse de cada uma;
- a tabela de cada versão viva, da v21 à v36;
- o gabarito está em `web/app/test/gabaritos/luta_nucleo_n3.json`, gravado pelo `scripts/arena_gabarito_n3.ts`. O
  `test/luta_nucleo_n3_gabarito.test.ts` confere que, com as chaves fora da entrada, as lutas saem byte a byte iguais (o sha256 dos eventos
  e do estado final).

**As chaves** (campos da `EntradaLuta`, `motor/arena/luta.ts`; sem o campo, a configuração é a de antes):

| chave | o que faz ligada | a faixa (PROPOSTA, SEM FONTE) |
|---|---|---|
| `forcaAtr` | a vantagem do atributo vem na entrada, no lugar do `OPCOES_PADRAO.forca` (1,5) | de 1 a 3 (`FORCA_ATR_MAX`) |
| `tiroDoMorto` | `true`: o projétil de quem já caiu some no ar, sem dano (o evento `tiro_errou`) | só `true` |
| `puloMax` | a velocidade do pulo da esquiva fica até o teto / a duração do pulo em passos (`MS_DO_PULO`, 192 ms) | de 10 a 400 px (`PULO_MAX_FAIXA`) |
| `bordaRingue` | só no Ringue: o recuo (também o da preparação do tiro e o do apoio) e o pulo da esquiva não passam do limite; o empurrão e a investida não mudam | de 0,5 a 1 do raio (`BORDA_RINGUE_FAIXA`) |

**Os testes** (`web/app/test/luta_nucleo_n3.test.ts`), para cada chave:
- desligada, a luta de antes;
- a regra ligada:
  - com o `forcaAtr` 1, todo dano sai com o multiplicador 1;
  - com o `tiroDoMorto`, nenhum dano vem de quem caiu, e as lutas desses tiros empatam menos;
  - com o `puloMax` 80, nenhum pulo passa de 80 px;
  - com a `bordaRingue` 0,9, as quedas sem golpe de quem atira caem a menos de um quarto, e fora do Ringue nada muda;
- a faixa, que falha alto;
- o replay bit a bit, com cada chave e com as 4 juntas.

**O que vem depois:** a N4, os contrafactuais na faixa 92xxx, em até 4 processos. Para ela, a bancada (`scripts/equilibrio_poc/`) ganha os
4 campos no candidato.
