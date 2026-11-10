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
