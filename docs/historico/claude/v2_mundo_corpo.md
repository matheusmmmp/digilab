# V2, de 2026-10-07 a 2026-10-13: o mundo físico, o corpo, o banheiro, os dois pets e o pet que pensa

Seções movidas inteiras do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13), da prancha do mapa
à bancada do pet que pensa, na ordem em que entraram. Arquivo fechado: o resumo de uma etapa nova vai no documento da frente (a regra
está no `CLAUDE.md` da raiz).

## V2, W-PRANCHA-MAPA — a prancha do mapa do mundo físico (2026-10-07, rodada 16, `docs/V2_RODADA_16.md`) — SÓ PRANCHA

Proposta de `docs/futuro/mundo_fisico.md` (seções 2.3 e 2.6), seguindo o protótipo `docs/futuro/mundo_fisico_vistas.html`. Nenhum código
do motor nem do app.
- **Pranchas:** `docs/estilo_up/pranchas/MapaDesktop.html` (1280×720) e `Mapa390.html` (390×844), com placeholders originais e os tokens e
  componentes de `docs/estilo_up/dl-up.css`. A cópia com os sprites fica em `Assets/Pranchas_UP/`, fora do repositório, listada no
  `index.html` de lá.
- **O que mostram:**
  - a vista inclinada (a projeção do protótipo);
  - as quatro regiões (M-4): casa com o ninho e o comedouro, jardim, campo e mata;
  - as árvores com frutas caídas e uma caindo, a comida deixada no comedouro, a bola quicando e o pet de pé com sombra;
  - o estado "comida solta aqui" depois do drop, com o aviso e **Desfazer**.
- **No desktop:** a câmera segue o pet, com botões de seguir, aproximar e afastar; a bandeja e a bola ficam na lateral, com o mapa de cima
  e o card "Agora".
- **No celular:** o mapa na tela inteira e a bandeja aberta embaixo. O arrasto da carne começa na bandeja; um dedo no mapa move a câmera,
  e dois dedos dão zoom.
- **Registrada** em `docs/PENDENCIAS_PRANCHAS.md` como "não existe" no app. Interpretações em `docs/REGISTRO_DESVIOS.md`.

## V2, W-FAIXAS-R17 — as faixas e os prefixos do mundo físico e do corpo (2026-10-07, rodada 17, `docs/V2_RODADA_17.md`)

- **`FAIXAS_RESERVADAS`** (`experiments/bancada_v2.py`) ganha quatro faixas, cada uma com a fonte:
  - mundo físico (`PLANO_ANALISE_V2_MUNDO_FISICO`, seção 11): 31101…31505 (calibração e piloto do N) e 32101…32505 (validação);
  - corpo e drives (`PLANO_ANALISE_V2_CORPO_DRIVES`, seção 10): 33101…33505 (calibração e piloto) e 34101…34505 (validação).
- **`PREFIXOS_UNIDADES`** ganha `"mundo"` e `"corpo"` (seção 4 de cada plano).
- **`tests/test_faixas_r17.py`** confere:
  - que as faixas novas não colidem com as de antes, com as queimadas nem com as sementes das configs;
  - que as unidades dos seis prefixos (K = 40, as duas fases) não colidem entre si e as novas ficam fora das faixas, das configs e das
    sementes dos testes.

## V2, W-GABARITOS — as vidas de hoje do mundo físico e do corpo (2026-10-07, rodada 17, `docs/V2_RODADA_17.md`) — GABARITOS GRAVADOS

Passo 1 do A, antes de qualquer mudança do mundo físico (`docs/TAREFA_V2_MUNDO_FISICO.md`, seções 9 e 10) ou do corpo
(`docs/TAREFA_V2_CORPO_DRIVES.md`, seção 12, G2). Nenhum código do motor mudou; só as sementes dos testes. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Mundo** (`tests/gabarito_mundo.py` → `tests/gabaritos/mundo_vidas_de_hoje.json`, 96 vidas):
  - P0, P1 e P3, nos mundos `padrao`, `bola`, `descasado` e `iguais_frutas`;
  - atencioso e aleatório, nas sementes 101 (sem genoma) e 202 (genoma 202: no `padrao`, o `MotorPersonalidade`);
  - na bancada simples (L1) e na completa (T3 com as peças da K2, K4 e canais).
- **Corpo** (`tests/gabarito_corpo.py` → `tests/gabaritos/corpo_vidas_de_hoje.json`, 156 vidas):
  - os três motores que o corpo vai tocar: `MotorComFeedback`, `MotorAmbiente` e `MotorFrutasMundo`;
  - P0 a P3 (o P2 só nos mundos das frutas), nos mundos `padrao`, `bola`, `descasado`, `mutavel` e `iguais_frutas`;
  - as montagens simples (T3 com as peças da K2) e completa;
  - o só cuidado do P3 (`sem_ensino`) na completa;
  - sementes 101 e 202, sem genoma.
- **O que se confere:** sha256 do log, do estado final, do `estado()`, das ações, das rngs, do registro do mundo e do estado interno da
  política.
- **Teste:** `tests/test_gabaritos_mundo_corpo.py`, 6 testes, ~31 s. Os dois gabaritos são conferidos byte a byte contra o código atual, e
  o teste verifica a cobertura (motores, mundos, braços, montagens) e as sementes.
- **Regravar só com o código de antes.** Depois da mudança do mundo ou do corpo, estas vidas têm de sair iguais com a chave desligada.

## V2, W-CORPO-QUIMICA — a química dos drives de hoje, sem órgão (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, etapa 1) — GATES PASSAM

Rodada 17 (`docs/V2_RODADA_17.md`). Etapa 1 da seção 14 da tarefa do corpo (CD-1 a CD-10 decididas). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/corpo.py` (novo) e `digilab/config.py` (`ConfigCorpo` no fim). Motor, `engine.py`, `lobos.py` e a
web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`ConfigCorpo`** (desligada por padrão; registro `corpo.PARAMETROS_CORPO`):
  - `ligada` liga a química dos drives de hoje;
  - `digestao`, `vida`, `drives_novos` e `gestos` falham alto se ligadas (etapas 3, 4 e 6). Cada uma exige a anterior;
  - C = 450000 (CD-1) e S = 1024;
  - os efeitos da ação do pet já em C;
  - as constantes de meia-vida (k 1497, 753 e 32).
- **`Corpo`** (componente puro: sem motor, sem rng; só importa `config`, `events` e `state`):
  - **os químicos:** `fome`, `desconforto`, `cansaco`, `tristeza` e `dano` guardam a falta em inteiros de [0, C]. O drive é
    (C − q) / C;
  - **as taxas** (`taxas_de`) saem de `Config` e da `ConfigCorpo`, cada uma conferida na grade de C;
  - **o tick** (`passo(estado_antes)`) segue a ordem de `state.avancar_um_tick`, com o dano pelo receptor de privação (algum de fome,
    desconforto e cansaço acima de C − 67500);
  - **os estímulos de hoje:** `acao_dono` (as seis ações de `state.aplicar_acao_usuario`), `acao_pet`, `estimulo_bola` e
    `estimulo_fruta`;
  - **as leituras:** `drives`, `no_estado`, `falta` e `receptores`, estes na escala S;
  - **os passos inteiros:** `k_meia_vida` (só para derivar), `passo_meia_vida` (com decremento mínimo de 1) e `div_arred`.
- **Paridade:** `experiments/exportar_gabarito_corpo.py` → `tests/gabaritos/corpo_quimica_python.json`, com:
  - as taxas;
  - uma grade de casos;
  - a meia-vida e o `div_arred`;
  - 3 vidas em malha aberta, com o sha256.

  Só inteiros: o TS da etapa 7 confere igual.
- **Gates** (`tests/test_corpo_quimica.py`, 29 testes, ~3 s):
  - **G-HOJE (a) em malha aberta:** 4 donos × 5 sementes × 3 dias, com as ações forçadas. Fome, higiene, energia e humor ficam a até 1e−9
    do float de hoje em todo tick; a saúde, até 1e−9 mais as viradas de privação. Toda virada é um químico exatamente no limiar.
    O `Estado` e a rng de ambiente de hoje são reproduzidos;
  - **o exemplo do tick 660:** 0,25 exato em inteiros, contra 0,24999999999998737 no float;
  - **as constantes:** a derivação dos k_h e a meia-vida efetiva; C é o menor que deixa as taxas inteiras;
  - **as conversões na grade:** as ações do dono e do pet, a bola, a fruta e o tick;
  - **os receptores:** na escala S, e o `div_arred` igual ao dos lobos;
  - **as falhas altas:** fora da grade, a sub-chave das etapas seguintes e o corpo com a chave desligada;
  - **o isolamento:** o AST sem motor e sem rng;
  - **a paridade:** o gabarito reproduz.

## V2, W-MUNDO-FISICO — o motor do mundo físico, etapa 2 (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`) — GATES PASSAM

Rodada 17, passo 2 do A. As seções 2 a 8 da tarefa (MF-1 a MF-4 decididas), sem run e só com as sementes dos testes. O instinto e os
cérebros no mundo são a etapa 3 (B); a web, a etapa 5; a bancada, a etapa 4 (D).
- **O que mudou:**
  - `digilab/mundo.py`, arquivo novo;
  - a `ConfigMundo`, o `LayoutMundo` e os layouts padrão e afastado, no fim de `config.py`;
  - os eventos `deixar_comida` e `deixar_bola`, como funções novas em `events.py`;
  - o campo `Observacao.mundo`, com padrão None.
  - `engine.py`, `ambiente.py`, `frutas.py`, os cérebros, a bancada e a web não mudaram.
- **`MotorMundo`:**
  - é subclasse do `MotorFrutas`. Desligado, não tem rng, registro, chave em `estado()` nem embrulho;
  - ligado, substitui o cenário do N4 e da A1: frutas e bola ligadas, educação e lesões levantam erro, e `alimentar`, `oferecer_fruta_*`,
    `por_bola` e `tirar_bola` também;
  - o mapa tem 64 × 30 células de 16 subunidades, com posições inteiras, distância por `isqrt` e direções pela tabela inteira `DIR16`;
  - as árvores, a comida que amadurece, apodrece e some, e a bola que rola usam os fluxos `mundo-arvores`, `mundo-bola` e
    `mundo-sujeira`, nunca a `_rng_ambiente` nem a rng do pet (MF-4);
  - o alvo de explorar, comer e brincar sai do gancho `escolher_alvo` ou do padrão do motor, com um `u` da rng `alvo` sorteado sempre;
  - o pet anda de uma vez na decisão e paga energia pela distância. Explorar tem o "achou e comeu" (MF-1), e comer sem comida não dá
    fome (MF-2);
  - a percepção vai em `Observacao.mundo` (`PercepcaoMundo`, com a posição: MF-3);
  - a consequência chega ao cérebro com tudo aplicado, mais os ganchos `fruta_comida` e `consequencia_mundo`.
- **Peças para a bancada:**
  - `deixar_comida` conta como contato e `deixar_bola` não;
  - `reproduzir_mundo`, `fabricas_mundo` e `DonoComLugar` (comedouro, perto, longe, com a rng `dono-lugar` sem o braço);
  - `CanalMundo` e `simular_vida_mundo`.
- **Registros para as medidas do plano** (A1.8): `decisoes_mundo`, `regioes`, `visitas` às manchas, `quedas`, `consumos_mundo`,
  `deixadas` e `sumidas`. O replay refaz todos.
- **Gates** (`tests/test_mundo.py`, ~22 s):
  - **G1:** replay bit a bit com o instinto, um cérebro aleatório que escolhe alvos e os lobos aprendendo, para 4 donos, 3 lugares e 2
    sementes;
  - **G2:** as 96 vidas de `mundo_vidas_de_hoje.json`, com o `MotorMundo` desligado no lugar do motor da bola e das frutas;
  - **G-ENGINE:** o sha256 de `engine.py`, `ambiente.py` e `frutas.py`;
  - **G-MEC:** os mecanismos;
  - **G-NUMS:** as mesmas quedas em qualquer cérebro e dono;
  - **G-V1-V10:** a suíte de sempre passa.
- Uma vida de 14 dias leva ~0,3 s, e o replay outros ~0,3 s. Interpretações e os números PROPOSTOS escolhidos aqui estão em
  `docs/REGISTRO_DESVIOS.md`.

## V2, W-CORPO-DIGESTAO — os órgãos 1 e 2 do corpo: a digestão e a Vida (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, etapas 3 e 4) — GATES PASSAM

Rodada 17. Etapas 3 e 4 da seção 14, um commit cada (o órgão 1 primeiro). Infraestrutura, sem run; só as sementes dos testes. Mudaram
`digilab/corpo.py` e a `ConfigCorpo`; motor, `engine.py`, `lobos.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Órgão 1, a digestão** (sub-chave `digestao`; `ConfigCorpo.taxa_digestao` = C, CD-3):
  - **o estômago:** a ração, o comer e a nutrição da fruta vão ao químico `alimento`;
  - **a reação:** `t = min(alimento, fome, o que resta da taxa no tick)` roda na hora da ingestão e no começo de cada tick;
  - **o excesso:** com a fome em 0, o resto é descartado (o corte de hoje);
  - **o exposto:** `digerido_no_tick` (para a vontade do banheiro), `digerido_total` e `descartado_total`;
  - **sem receptor** para o cérebro.
- **Órgão 2, a Vida** (sub-chave `vida`; `ConfigCorpo.vida_decaimento` = 11 = C // (28 × 1440)):
  - **o relógio:** `vida` começa em C e decai v por tick; o `de_estado` usa o tick do `Estado`;
  - **os receptores de estágio:** `estagio()`, nos limiares C − v × T, com os ticks de `treino_stats.estagio_no_tick` da `cfg_evo` do
    corpo;
  - **sem morte:** a Vida não mata;
  - **sem receptor** para o cérebro.
- **As outras sub-chaves:** `drives_novos` e `gestos` continuam falhando alto.
- **Paridade:** o gabarito `tests/gabaritos/corpo_quimica_python.json` passa à versão 2, com a digestão (na taxa C e numa taxa lenta só
  para a paridade) e a Vida (limiares, grade e vidas com os ticks de estágio).
- **Gates:**
  - **`tests/test_corpo_digestao.py`:**
    - o G-HOJE (a) de novo, com a digestão na taxa C, em 4 donos × 5 sementes;
    - a química igual à da etapa 1, químico a químico;
    - a composição da seção 5, a reação com a taxa lenta, o descarte e a conservação da comida.
  - **`tests/test_corpo_vida.py`:**
    - o estágio pela Vida igual ao de hoje tick a tick, nas três durações, até depois do fim da Vida;
    - os ticks das transições do `MotorEducacao` (teste e canônica) e do `MotorTreino` iguais aos cruzamentos da Vida;
    - o G-HOJE (a) com os dois órgãos.

## V2, W-MEDIDAS-R17 — as medidas do mundo físico, do corpo e do banheiro (2026-10-07, rodada 17, `docs/V2_RODADA_17.md`) — TESTADAS EM DADOS SINTÉTICOS

Funções puras no fim de `digilab/metrics.py`, sobre listas simples de eventos. O motor do mundo e o corpo novo ainda não estão na `main`,
então o docstring de cada função diz o que o motor precisa fornecer. Nenhuma run; nada mais mudou. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Comuns:** `janela_dias(primeiro, ultimo)` e `JANELA_8_14` (ticks [10080, 20160)); posições em subunidades (`SUBUNIDADES_POR_CELULA` 16).
- **Mundo físico** (`PLANO_ANALISE_V2_MUNDO_FISICO`, seção 5.1 e adendo 1, A1.8):
  - `deficit_fome_energia` (o `D_FE`, entrada (tick, fome, energia) por decisão);
  - `visitas_manchas` (entrada: a trajetória (tick, x, y), uma por decisão, e os troncos), com `custo_viagem` e `taxa_recente` (as quedas);
  - `inclinacao_permanencia` (G-PERM sobre o custo, G-OPORT sobre a taxa recente), `taxa_no_abandono` (a medida 2), `permanencia_media`
    e `contraste_distancia` (G-DIST).
- **Corpo** (`PLANO_ANALISE_V2_CORPO_DRIVES`, seção 5 e adendo 1): `tempo_livre_be` (`BE` e `OC`), `cuidado_preservado`, `drives_novos`,
  `variedade_recente` (A1.2), `p_comer_so_fruta` e `inclinacao_generalizacao` (A1.1).
- **Banheiro** (`PLANO_ANALISE_V2_BANHEIRO`, seções 4 e 8): `alivios_por_dia` (a fração no banheiro e os acidentes), `dia_do_criterio`
  (com censura e T*), `alivios_ate_criterio` e `curva_sobrevivencia` (Kaplan–Meier e RMST).
- **Testes:** `tests/test_medidas_r17.py`, 19, cada um com a resposta conhecida.

## V2, W-CORPO-MOTOR — o corpo por baixo dos drives, no motor (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, etapa 2) — GATES PASSAM

Rodada 17. Etapa 2 da seção 14: o `Corpo` do B (química, digestão e Vida) por baixo dos drives do `Estado`. Sem run; só as sementes dos
testes. Mudaram `digilab/motor_corpo.py` (novo) e o campo `Observacao.corpo` (com padrão None). `engine.py`, `corpo.py` e as classes do
meio não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`MotorCorpo`:**
  - é um mixin por `com_corpo(base)`: `com_corpo(MotorComFeedback)`, `com_corpo(MotorAmbiente)` e `com_corpo(MotorFrutasMundo)`;
  - a chave é `cfg_corpo` (`ConfigCorpo`, com as sub-chaves `digestao` e `vida`);
  - desligado, é o motor de baixo byte a byte.
- **Ligado:**
  - os cinco drives do `Estado` são a leitura da química, a cada tick e depois de cada estímulo. O laço do tick é refeito no mixin, com o
    `Corpo.passo` (o tick e a sujeira de hoje, na mesma rng);
  - os escritores de hoje viram estímulo: a ação do dono, a ação do pet, a bola e a fruta (antes do gancho `fruta_comida`);
  - **G-BYPASS:** um drive mudado por fora do corpo falha alto;
  - a percepção vai em `Observacao.corpo` (`PercepcaoCorpo`, os receptores na escala S);
  - o gancho `consequencia_corpo(acao, ocorrido, obs_depois)` é chamado uma vez por decisão;
  - com a Vida, o estágio é conferido contra o de hoje a cada tick.
  - Educação, lesões, obediência, treino e **o mundo físico ligado** falham alto; o andar e as comidas do mapa ainda não têm estímulo no
    corpo.
- **Gates** (`tests/test_corpo.py`, 28, ~1 min):
  - **G2:** as 156 vidas de `corpo_vidas_de_hoje.json` com o `MotorCorpo` desligado na frente dos três motores;
  - **G-HOJE (a):** malha aberta contra o motor de hoje, tick a tick, nos três mundos, com a química sozinha e com os dois órgãos. Os
    drives ficam a até 1e−9, a saúde a até 1e−9 mais as viradas no limiar, e sujeira, sono, rngs e estágio são iguais. O sinal do N3 sai
    igual em ≥ 99% das decisões;
  - **G-BYPASS** e **G-RECEPTOR**;
  - **G-ENGINE:** `engine.py` e as classes do meio sem mudança;
  - **o gancho e o G1:** o gancho é chamado uma vez por decisão e já vê tudo aplicado; o replay é bit a bit com o corpo.
- **Achado:** em malha fechada, 17 a 19 de 20 vidas por mundo divergem cedo, porque os pesos do tempo livre são contínuos nos drives. O
  G-HOJE (b) tem de ser pela distribuição.

## V2, W-BANCADA-MUNDO — as faixas do banheiro e o mundo físico na bancada (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 4) — GATES PASSAM

Rodada 17. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Só `experiments/` mudou (a bancada e `configs/v2_mundo/`) e três
testes antigos (a tabela de braços, a de condições e o `NOS_PENDENTES`). `engine.py`, `mundo.py`, `metrics.py`, os cérebros e a web não. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Banheiro:** as faixas 37101…37505 (calibração e piloto) e 38101…38505 (validação) em `FAIXAS_RESERVADAS`, com a fonte
  (`PLANO_ANALISE_V2_BANHEIRO`, seção 10), e o prefixo `"banheiro"` em `PREFIXOS_UNIDADES`.
- **Os mundos `fisico` e `fisico_afastado`:** o `MotorMundo` da main, condição `iguais` (PMF-7); o afastado troca só o layout
  (`LAYOUT_MUNDO_AFASTADO`, o G-DIST da A1.8). A chave `"mundo"` da config troca campos da `ConfigMundo` (o `mult_queda` da calibração).
- **O lugar** (comedouro, perto, longe; PMF-4) é um fator da vida: `EspecVida.lugar` e a chave `"lugares"`, obrigatória com o mundo
  físico e proibida fora dele. A célula é dono × lugar, e a coluna da tabela vira `condicao/mundo/lugar`.
- **O dono só com o cuidado (PMF-3):** o `DonoComLugar` (o `alimentar` vira `deixar_comida` no lugar) com o filtro `sem_ensino` aplicado
  ao vivo (`CanalSemEnsino`, `simular_vida_fisico`). O elogio e a bronca gastam o orçamento do dono como sempre, mas não chegam ao motor
  nem ao log; ficam contados em `VidaBancada.retirados`. Os gestos do mundo entram na contagem (`contar_gestos_mundo`).
- **O replay** é o `reproduzir_mundo`: no G1 de toda vida e acoplado, na medição e na deriva (com o mesmo corte por tick). O
  `resumo_motor` ganha o `resumo_mundo_fisico()`.
- **As medidas do plano** (`Bancada.medidas_mundo`, bloco `mundo_fisico` no `medidas.json`), todas de `metrics.py`, nos últimos sete dias
  (os dias 8 a 14 numa vida de 14):
  - o `D_FE` (e o da vida toda) e o cuidado preservado;
  - as visitas às manchas, recontadas da trajetória do motor e conferidas contra as `visitas` dele (uma diferença falha alto);
  - as inclinações da permanência sobre o custo de viagem e sobre a taxa recente (G-PERM, G-OPORT), a taxa no abandono e a permanência
    média (G-DIST, entre os dois layouts).
  - Nas tabelas: `d_fe`, `privacao_janela` e `permanencia_media`.
- **Pendente do instinto do mundo** (`NOS_PENDENTES["instinto_mundo"]`, a etapa 3 do B), falhando alto com o nó:
  - o braço **P0z** (o P0 `sem_explorar`), e com ele os acoplados P0^ac e P1^ac, que saem do registro dele;
  - o cérebro `instinto` no mundo físico;
  - qualquer config do mundo físico com sementes fora das dos testes.
- **O que roda hoje:** os lobos (P0, P1, P3) no mundo, cegos a ele até a etapa 3, e o acoplado P1 ← P0 (o encanamento do P1^ac).
- **Testes:** `tests/test_bancada_mundo_fisico.py`, 15 (~30 s). **Fumaça** (`experiments/configs/v2_mundo/fumaca.json`, NÃO canônica):
  96 vidas rejogadas bit a bit em ~1,5 min; sem artefato.

## V2, W-MUNDO-WEB — o motor do mundo físico em TypeScript (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 5) — G-PAR PASSA

Rodada 17, etapa 5 da seção 9 da tarefa: só o motor e a paridade. Não entram tela nem versão de pet nova. Mudaram `web/app/motor/mundo.ts`
(novo), o `motor/index.ts` (exporta o mundo), `motor/constantes.ts` (a `ConfigMundo` e os layouts no fim),
`experiments/exportar_gabarito_mundo.py` (novo) e o gabarito `web/app/test/gabaritos/mundo_python.json`. `digilab/`, o app, os pets e os
gabaritos de antes não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Caminho:** o motor do app fica em `web/app/motor/` (sem DOM) e os testes em `web/app/test/`. Por isso os arquivos são
  `web/app/motor/mundo.ts` e `web/app/test/mundo.test.ts`, e não o `web/app/src/motor/` que a tarefa citava.
- **`motor/mundo.ts`** é o porte de `digilab/mundo.py`, com os registros nos nomes do Python:
  - a conta inteira (`divArred`, `distancia`, `noMapa`, `deslocar`, `passoAte`, `regiaoDe`, `cheiroEm`, `direcaoDoCheiro`, `DIR16`);
  - os eventos `deixar_comida` e `deixar_bola` (`{tick, tipo, valor}`, com a mesma validação);
  - a classe `Mundo`: as árvores, a comida que amadurece, apodrece e some, a bola que rola, a percepção, os candidatos, o alvo padrão e
    a consequência de andar, comer e brincar, com o MF-1 e o MF-2.
- **O mundo é um componente:** recebe o estado do pet (fome, energia, humor, sujeira) depois do efeito da ação e devolve o estado
  depois. O engine, a política e o dono ficam com quem o usa.
- **Os sorteios do Python, número a número:** cada fluxo é um `random.Random` semeado por `derivar_semente`. O arquivo traz:
  - o sha256 (puro, com o próprio UTF-8);
  - o `derivarSemente` (bigint);
  - o `RandomPy`: o Mersenne Twister do CPython com o `init_by_array` e `random`, `getrandbits`, `randrange` e `randint`.
  - O `mulberry32` do jogo não entra.
- **Gabarito** (`python experiments/exportar_gabarito_mundo.py`):
  - a config;
  - a grade: as sequências do `random.Random` de 8 sementes de 0 a 64 bits, as derivações, 400 casos de cada conta, 150 de cheiro e
    direção e os eventos válidos e inválidos;
  - **4 vidas inteiras de 3 dias** (instinto; um cérebro que escolhe qualquer alvo, inclusive a podre e um ponto; os lobos aprendendo no
    layout afastado com o dobro de quedas; o cérebro aleatório com o dono que deixa a bola perto). Cada uma tem o traço por decisão, o
    resumo do mundo e os próximos sorteios de cada fluxo.
  - `tests/test_gabarito_mundo_web.py` confere que o arquivo está em dia com o Python.
- **G-PAR** (`web/app/test/mundo.test.ts`, 18 testes, < 1 s):
  - a config, os layouts e os números do estado são os do Python, campo a campo;
  - as sequências, o `derivar_semente`, as contas e os eventos saem iguais;
  - as 4 vidas são rejogadas decisão a decisão: percepção, candidatos, ocorrido (o `u`, o alvo, o deslocamento, a energia gasta, o
    consumo, a rolagem), o estado e a percepção depois, o resumo do mundo e os 6 próximos sorteios dos 4 fluxos saem iguais.
  - Os floats são comparados com igualdade exata.
  - Uma mutação no efeito da podre faz a vida 4 falhar.
- **A única diferença**, da língua: o Python recusa `deixar_bola(9, 3.0, 4)` (`type(x) is not int`), e no JS 3.0 é o mesmo número que 3. O TS
  aceita, com o mesmo texto no log (`"3|4"`); o teste a declara.

## V2, MUNDO-CEREBROS — o instinto do mundo e os ganchos nos cérebros (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 3) — GATES PASSAM

Rodada 17, etapa 3 do mundo físico (B). Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/instinto_mundo.py` (novo),
`digilab/policies/lobos.py` (atrás de `cfg_mundo`) e `digilab/motivo.py`, mais `experiments/analisar_empates_cheiro.py`. `mundo.py`,
`engine.py`, a bancada, os cérebros B e C e a web não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`PoliticaInstintoMundo`** (o P0 do plano), igual ao instinto de hoje fora de três pontos:
  - **a fome urgente** (`pedido_necessidade`): com a fome abaixo de 0,25 e para onde ir comer (comida boa vista, ou cheiro com direção),
    come; sem isso, chama. A higiene baixa continua chamando;
  - **o tempo livre:** `comer` ganha `w_fruta` com comida boa vista e `brincar` ganha `w_bola` com a bola vista (os `w` do N4 e da A1, a
    mesma chamada de `rng.choices`, as regras `fruta_no_cenario` e `bola_no_cenario`);
  - **`sem_explorar`** (o P0z): o peso do explorar vai para o ocioso.
  - Sem `obs.mundo`, é o `PoliticaInstinto` byte a byte.
- **A regra que liga a percepção às entradas do cérebro A** (`instinto_mundo.entradas_mundo`): `bola` = 1 com a bola vista; `fruta` = 1
  com comida boa vista (ração ou fruta madura). Com elas, o prior do A repete o instinto do mundo.
- **O cérebro A no mundo:** `PoliticaLobos(cfg, cfg_lobos, cfg_mundo=CONFIG_MUNDO_LIGADA)`. Sem a chave, os lobos de hoje.
  - A sonda roda o `PoliticaInstintoMundo`; o prior ganha `comer` na linha `pedido_necessidade`. 10 regras × 7 ações × 12 entradas, sem
    as peças das frutas.
  - **`escolher_alvo`** devolve None (o padrão do motor) e anota os candidatos no motivo. O alvo aprendido é de adendo.
  - **`consequencia_mundo`:** na fonte consequência, o crédito de explorar, comer e brincar espera o gancho. A E2 só vale no comer que
    comeu fruta; o resto usa o sinal do N3. Com canais e fruta que mexe no humor, falha alto (rota de adendo).
- **`PoliticaComMotivo`** repassa os dois ganchos (só se a política os tem), pede o termo do mundo ao instinto do mundo e recusa o
  `sem_explorar`.
- **Gates** (`tests/test_mundo_cerebros.py`):
  - os lobos com o mundo e o aprendizado desligado = o instinto do mundo byte a byte (4 donos × 3 lugares × 2 sementes; decisão a
    decisão em 3000 observações); o P1 com ganho 0 = o P0;
  - G1 do instinto (P0, P0z) e dos lobos (P0, P1 com e sem canais, P3), estado interno incluído;
  - a fome urgente, o tempo livre e o `sem_explorar` em casos com resposta conhecida;
  - o crédito no gancho, conta exata (E2 no comer de fruta; o f_S da transição no resto);
  - a `PoliticaComMotivo` não muda a vida;
  - G2 (chave desligada = as vidas de hoje): os gabaritos de sempre, na suíte.
- **Os empates do cheiro** (`python experiments/analisar_empates_cheiro.py` → `artifacts_v2_mundo_cerebros/empates_cheiro.json`; só
  geometria, mais as vidas do P0 nas sementes dos testes):
  - com a fruta fora da visão e dentro do raio do cheiro, o máximo empata em 79% das posições (a ração, 58%);
  - a ordem fixa erra o rumo em 27,8° em média e puxa sempre para o sentido horário (−18°); o comer pelo cheiro gasta 0,84 decisão a mais
    que a reta;
  - desempatar pelo cheiro a 2 células: 15,4° e 0,25 decisão; o limite de qualquer desempate (o rumo verdadeiro): 11,3° e 0,17;
  - nas vidas, 41% das decisões com direção de cheiro saem de um empate, e o desempate a 2 células mudaria 16%.
  - A recomendação (trocar no motor, A, antes da calibração do mundo) está no PR.

## V2, W-DOMINANCIA — a dominância de um drive no sinal e o braço P1-cw (2026-10-07, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, adendo 2) — GATES PASSAM

Rodada 18. A parte do D no adendo 2 (A2.2 a A2.6; decisão D-4). Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram
`digilab/metrics.py`, `experiments/bancada_v2.py` e a tabela de braços de `tests/test_bancada_v2.py`. `engine.py`, `lobos.py`, o corpo e a
web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A medida** (`metrics.py`, só descritiva e fora do Holm):
  - `contribuicao_drives`: c_d = w_d · (falta_antes² − falta_depois²), em inteiros na escala S;
  - `parcelas_drives`: p_d = |c_d| / Σ|c|;
  - `dominancia_decisoes`: por vida, as decisões com sinal, separadas em tempo livre e o resto. Sai quantas cada drive lidera
    (p_d ≥ `LIMIAR_LIDERA`, 0,80), f_d, a parcela agregada e a contribuição com sinal;
  - `leitura_dominancia`: a regra de leitura da A2.3. "Domina" quando o IC95 inferior de f_d (10.000 reamostragens, semente 4242) passa
    de `LIMIAR_DOMINA` (0,50).
- **Na bancada:**
  - **o registro:** o `_Registro` anota, por decisão, o tick, a regra e o estado antes e depois da ação. Na fruta, o depois é o estado
    logo depois de comer, com o humor (E2), pelo gancho `fruta_comida`;
  - **por vida:** `Bancada.medidas_dominancia`, no bloco `dominancia` do `medidas.json`, na janela dos últimos sete dias e na vida toda;
  - **por grupo:** `tabela_dominancia` grava o `dominancia.json`, por braço × condição × tipo de decisão, com f_d por unidade (os donos
    somados) e a leitura.
- **Os drives,** pelos nomes do corpo (`NOMES_DRIVES`): fome, desconforto e cansaço, os de `ConfigConsequencia.drives`, mais a tristeza
  (o humor) na fruta com a E2. Os drives novos (tédio, solidão, estresse, dor) entram quando o corpo os tiver.
- **`origem`:**
  - nos braços que aprendem pela consequência, a medida é o sinal deles (`"sinal"`);
  - nos outros (o P0, o P3), é a mesma conta como sonda (`"sonda"`).
- **A conferência:** com os canais e o aprendizado ligados, a soma por canal dos sinais recalculados (`lobos.sinal_por_canal`) tem de
  ser o total que o cérebro guardou; se não for, falha alto.
- **O braço P1-cw** (`Braco.pesos_janela`, nó `corpo-A2.4`):
  - está declarado e falha alto com o nó (`NOS_PENDENTES["pesos_janela"]`) até o B pôr a chave `pesos_janela` na `ConfigConsequencia`;
  - ele também depende dos braços do corpo (P1-c), que a bancada ainda não tem.
- **Testes:** `tests/test_dominancia.py`, 17 (~5 s). As funções são conferidas em dados sintéticos com a resposta conhecida; a conferência
  com os canais em quatro mundos, e ela falha alto quando os dois lados diferem.

## V2, W-LIGA-MUNDO — o instinto do mundo ligado na bancada (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 3) — GATES PASSAM

Rodada 18. Os quatro passos listados no #231, com a etapa 3 do B (#232) na `main`. Infraestrutura, sem run de pesquisa; só as sementes
dos testes. Mudaram `experiments/bancada_v2.py`, a fumaça `experiments/configs/v2_mundo/fumaca.json`, o
`tests/test_bancada_mundo_fisico.py` (a seção 3 e a contagem da fumaça) e o teste novo. `engine.py`, `mundo.py`, `instinto_mundo.py`,
`lobos.py`, `metrics.py` e a web não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Sem o `NOS_PENDENTES["instinto_mundo"]`:**
  - a entrada saiu, e a checagem da run com plano em `validar_config` também;
  - fica só a `pesos_janela` (o P1-cw).
- **O cérebro `instinto` no mundo físico** é a `PoliticaInstintoMundo`, só no P0 e no P0z.
- **O P0z** é a `PoliticaInstintoMundo` com `sem_explorar=True`, **em qualquer cérebro da config**, porque os lobos não têm o modo.
  - O rótulo segue o cérebro da espécie (`P0z` ou `P0z~instinto`), mas a vida é a mesma (teste).
  - Fora do mundo físico, o P0z continua um `ValueError`.
- **Os lobos no mundo físico:** `PoliticaLobos(..., cfg_mundo=self.cfg_mundo_de(mundo))`.
  - `Bancada.pesos_do_mundo()` dá a `ConfigBola` e a `ConfigFrutas` da bancada com a chave desligada. Elas só levam os pesos `w_bola` e
    `w_fruta` ao instinto do mundo e ao prior dos lobos, e o `MotorMundo` e os lobos exigem as duas desligadas.
  - O `escolher_alvo` dos lobos devolve None, o alvo padrão do motor: o cérebro A aprende **quando** agir, não **para onde** ir.
- **Gates** (`tests/test_bancada_liga_mundo.py`, ~2 min):
  - **o P0 com lobos é o instinto do mundo byte a byte** (o `resumo_motor`: log, estado, ações, rngs e o registro do mundo). Vale nos
    dois layouts, 4 donos × 3 lugares × 2 sementes, nas montagens simples e completa;
  - **os lobos veem o mundo:** a regra `fruta_no_cenario` dispara, e o gancho do alvo anota os candidatos;
  - **o P0z:**
    - nenhuma ação explorar;
    - a mesma vida com os dois cérebros;
    - G1;
    - o P0 explora na mesma semente;
  - **os acoplados P0^ac (P0 ← P0z) e P1^ac (P1 ← P0z):** os mesmos gestos do dono nos mesmos ticks e lugares, e G1;
  - **o P1 aprende pela consequência no mundo**, e a dominância sai com `origem` `"sinal"`;
  - a config com plano (bases 31101, prefixo `mundo`) valida.
- **Fumaça** (`experiments/configs/v2_mundo/fumaca.json`, NÃO canônica):
  - os braços P0, P0z, P1 e P3;
  - os acoplados P1 ← P0, P0 ← P0z e P1 ← P0z;
  - sem artefato.

## V2, CORPO-MUNDO e PESOS-JANELA — os estímulos do mundo físico no corpo e o peso pela janela no cérebro A (2026-10-07) — GATES PASSAM

Pedido do Gerente depois da etapa 3 do mundo. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/corpo.py`,
`digilab/policies/lobos.py` (atrás da chave), a `ConfigConsequencia`, o exportador e o gabarito da paridade do corpo. `engine.py`,
`mundo.py`, o motor do corpo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Os estímulos do mundo no `Corpo`** (para o A ligar o `MotorMundo` no `MotorCorpo`):
  - `estimulo_andar`: cansaço + 75 por subunidade;
  - `estimulo_consumo_mundo`: a ração madura (a do alimentar), a fruta madura (67500 e o efeito dela) e a podre (só o humor);
  - `acao_pet(..., com_mundo=True)`: a MF-2, comer sem comida não dá fome;
  - a bola do mundo é o `estimulo_bola` de sempre.
- **G-HOJE contra o float do `mundo.py`** (`tests/test_corpo_mundo.py`): a grade de cada comida pelo `_comer_mundo` do mundo e vidas
  decisão a decisão (os drives a até 1e−9, com e sem a digestão, todos os estímulos cobertos).
- **O gabarito da paridade** do corpo foi à versão 3 (a seção `mundo`); as seções de antes saem idênticas.
- **`ConfigConsequencia.pesos_janela`** (A2.4, o braço P1-cw; desligada por padrão) e `janela_pesos` (J = 32):
  - o peso de cada drive é `max(div_arred(S, 4), S − div_arred(3 · m_d, 4))`, com m_d a falta média nas J decisões anteriores;
  - é o mesmo no antes e no depois, e a janela anda depois da decisão;
  - o sinal com os pesos é calculado no cérebro (`sinal_homeostatico(..., pesos)`, e as variantes da E2 e dos canais), na E2 e no
    `consequencia_mundo`;
  - os pesos ficam no motivo de cada decisão;
  - desligada, o sinal e a vida de hoje.
- **Testes:** `tests/test_pesos_janela.py`. A conta exata do peso e do sinal (a fome 0,4 → 0,7 com peso de um quarto dá 276 no lugar de
  1104); a janela refeita por fora decisão a decisão numa vida; a E2 e os canais nas frutas; o mundo físico; o G1.

## V2, W-LIGA-PESOS-JANELA — o braço P1-cw ligado na bancada (2026-10-07, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, adendo 2, A2.4) — GATES PASSAM

Rodada 18. A chave `pesos_janela` do B (#236) na `main`. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram
`experiments/bancada_v2.py`, o teste do P1-cw em `tests/test_dominancia.py`, um comentário de `tests/test_bancada_v2.py` e o teste novo.
`engine.py`, `lobos.py`, o corpo e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O `NOS_PENDENTES` ficou vazio:** a entrada `pesos_janela` saiu.
- **O P1-cw** é o P1 com `ConfigConsequencia.pesos_janela` ligada (`Bancada.politica`; J = `janela_pesos`, 32). O resto vem do P1, inclusive as
  peças da montagem completa e os canais da config.
- **A dominância do P1-cw** (A2.2: c_d = w_d · Δ_d):
  - o w_d é o peso da janela que o cérebro usou na decisão, lido do motivo (`pesos_janela`);
  - na decisão sem fruta entram só os drives do N3, porque o cérebro pesa também o humor em toda decisão;
  - a conferência com os canais recalcula o sinal com os mesmos pesos (`sinal_por_canal(..., pesos)`);
  - uma decisão sem os pesos no motivo falha alto;
  - o `_Registro` anota o índice da decisão (`k`) em cada passo.
- **Gates** (`tests/test_bancada_pesos_janela.py`):
  - **com a chave desligada, o P1-cw é o P1 byte a byte** (o `resumo_motor` e o estado interno, fora o rótulo do braço). Os braços do corpo
    (P1-c) ainda não existem na bancada, então o gate é contra o P1. Vale em `padrao`, `bola`, `descasado`, `mutavel`, `fisico` e
    `fisico_afastado`, com 2 donos × 2 sementes, nas montagens simples e completa, com os canais;
  - **ligada:** a chave chega ao cérebro, a vida muda em todo mundo e passa o G1;
  - **o peso pela falta média:** a janela é refeita por fora, decisão a decisão (`pesos_da_janela` das faltas das J decisões anteriores,
    igual ao motivo). Algum peso cai abaixo de S, e todos ficam entre S/4 e S;
  - **a dominância** confere com os canais nos três mundos. Com o sinal recalculado sem os pesos, ela falha alto.
- **Fumaça do corpo:** não existe ainda em `experiments/configs/`, então o P1-cw não entrou em nenhuma.

## V2, MUNDO-CORPO — o MotorMundo no MotorCorpo (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seções 2, 9 e 12) — GATES PASSAM

Pedido do Gerente depois do #236 (os estímulos do mundo no `corpo.py`) e do #235 (o instinto do mundo na bancada). Infraestrutura, sem run;
só as sementes dos testes. Mudaram `digilab/motor_corpo.py` e `digilab/mundo.py` (um gancho, mesma conta), mais o teste antigo que esperava
a falha. `engine.py`, `corpo.py`, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A trava saiu:** `com_corpo(MotorMundo)` com o mundo ligado roda.
- **Os estímulos, na ordem do Gerente:**
  1. **a MF-2:** `Corpo.acao_pet(acao, com_mundo=True)`, na decisão;
  2. **o andar:** `estimulo_andar(deslocamento, custo_energia_por_subunidade)`;
  3. **a comida do mapa** (o comer e o achou e comeu): `estimulo_consumo_mundo(tipo, situacao, cmf, efeito_frutas[tipo])`;
  4. **a bola:** `estimulo_bola(ganho_humor_bola)`.
  - Os três últimos vêm do `MotorCorpo._consequencia`, que envolve a do `MotorMundo`.
  - **G-BYPASS:** só a energia (o andar), a fome e o humor (a comida) e o humor (a bola) podem mudar no float de baixo; fora disso, falha
    alto.
  - Depois, o Estado volta a ser a leitura do corpo, e os estímulos entram no `ocorrido` do `consequencia_corpo` (`("andar", d)`,
    `("comida", tipo, situacao)`, `("bola",)`).
- **Os ganchos:**
  - o `obs_depois` do mundo sai de `MotorMundo._observacao_depois_mundo`, e o `MotorCorpo` põe o `obs.corpo` por cima. O
    `consequencia_mundo` recebe os receptores já com os estímulos da própria ação, só nas decisões de explorar, comer e brincar, como hoje;
  - o `consequencia_corpo` continua com uma chamada por decisão, sempre, depois do `consequencia_mundo`.
- **Gates** (`tests/test_corpo_no_mundo.py`, 11 testes, ~1 min):
  - **G2:** as 144 vidas do mundo físico de hoje, pela bancada, iguais a `tests/gabaritos/corpo_mundo_vidas_de_hoje.json` byte a byte, com o
    `MotorCorpo` desligado na frente do `MotorMundo` e sem ele. O gabarito foi gravado antes, de um snapshot de origin/main
    (`tests/gabarito_corpo_mundo.py`, commit próprio);
  - **G-HOJE (a) no mundo físico:** malha aberta contra o `MotorMundo` de hoje, tick a tick, em 4 donos × 3 lugares × 2 sementes, com a
    química sozinha e com os dois órgãos. Os drives ficam a até 7e−14, e as 5 viradas de privação são todas um químico exatamente no
    limiar. A posição, as comidas, os consumos, as quedas, a bola e as rngs do mundo saem iguais. O sinal do N3 sai igual em 6912 de 6912
    decisões;
  - **a conta exata:** o cansaço sobe 75 por subunidade andada; a ração tira 202500 da fome, a fruta 67500, a podre põe 45000 de tristeza
    e a bola tira 67500;
  - **a MF-2:** o comer sem comida não mexe na fome do corpo;
  - **os ganchos, o bypass no mundo e o G1** (instinto do mundo e lobos aprendendo, estado interno e registro do mundo incluídos);
  - **a bancada monta o mundo físico com o corpo:** sem mudar a bancada, com o `MotorMundo` dela trocado pelo com corpo. P0 (lobos e
    instinto), P0z, P1 e P3 rodam nos dois layouts, e o G1 da bancada passa.
- **Para o D:** a chave do corpo na bancada (o `cfg_corpo` na fábrica do mundo físico) fica com ele.

## V2, CORPO-CEREBRO — o cérebro A no corpo, etapa 5 (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`) — GATES PASSAM

Etapa 5 da seção 14 (seções 9 a 11). Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás da
chave), `digilab/motivo.py` (o embrulho) e a `ConfigConsequencia`. `engine.py`, `corpo.py`, `motor_corpo.py`, a bancada e a web não.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `PoliticaLobos(..., cfg_corpo=ConfigCorpo)`, ligada. Sem ela, o cérebro de hoje, inclusive num `MotorCorpo`.
- **`lobos.sinal_corpo`** sobre os receptores:
  - D = Σ w_d · falta_d², com a falta = S − leitura nos drives de hoje e a leitura nos novos, e f = div_arred(ganho · ΔD, S);
  - os drives: os do N3, o humor só no comer de fruta (E2) e os drives novos que o corpo tiver (o susto fora);
  - `w_d` em `ConfigConsequencia.pesos_drives_corpo`, todos 1; compõe com a `pesos_janela` (A2.4), que passa a ler os receptores.
- **O gancho:** o crédito espera `consequencia_corpo`, ou `consequencia_mundo` no mundo físico (explorar, comer e brincar), uma chamada por
  decisão em toda fonte, conferida (falha alto). O `f_S` da transição é conferido e não creditado.
- **As entradas novas:** as leituras dos receptores novos, só nas regras de tempo livre, um peso por (regra, ação, receptor), prior 0.
  Nas frutas, 763 → 868 pesos; com o mundo físico, +126.
- **Os canais novos:** um por drive novo, todos ao corpo, na mesma soma telescópica.
- **O embrulho:** o `PoliticaComMotivo` repassa `consequencia_corpo` e `mudanca_no_corpo`. Uma entrada nova aprendida que pese na decisão
  faz o motivo falhar alto (sem fator na expressão até a etapa 6).
- **Gates** (`tests/test_corpo_cerebros.py`, 42):
  - **G-HOJE (a) do sinal, malha aberta:** iguais 20.736 de 20.736 decisões, nos 3 mundos, com a química sozinha e com os dois órgãos;
  - **malha fechada:** o P1 com a chave do corpo e o P1 de hoje, no mesmo motor com o corpo, são a mesma vida byte a byte (padrão, bola e
    frutas; escalar, canais e janela);
  - **mundo físico:** as chamadas de uma vida do P1 rejogadas num cérebro com o corpo dão as mesmas decisões e os mesmos pesos;
  - **as contas exatas:** a conta da seção 9 (+1440 contra −34), as entradas novas pela regra da L1 e os canais;
  - **as entradas novas no prior** não mudam a decisão (3000 observações);
  - o G1, o embrulho e as falhas altas do gancho.

## V2, CORPO-DRIVES — o grafo do corpo e a etapa 6 (química e cérebro) (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seções 7, 8, 17 e 18) — GATES PASSAM

Infraestrutura, sem run; só as sementes dos testes. Mudaram:
- `digilab/corpo.py`;
- `digilab/corpo_grafo.py` (novo);
- a `ConfigCorpo` e a `ConfigLobos.recompensa_tapa`;
- `digilab/policies/lobos.py` e `digilab/motivo.py`;
- o exportador e o gabarito da paridade do corpo (versão 4).

`engine.py`, `motor_corpo.py`, `mundo.py`, a bancada e a web não mudaram. O motor da etapa 6 é do A. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **A combinação #238 + #239:** o cérebro com `cfg_corpo` no `MotorCorpo` com o mundo físico falhava alto, porque o motor chama os dois
  ganchos na mesma decisão. Agora o `consequencia_mundo` credita, e o `consequencia_corpo` fecha a decisão. Entrou o G1.
- **O grafo (seção 18):** `corpo.grafo_do_corpo` monta a tabela única (químicos, reações, emissores, receptores, meias-vidas, tetos), e o
  `Corpo` a usa (tick em fases, receptores, meias-vidas) e a confere na carga. As checagens de `corpo_grafo.checar` falham alto:
  - fechado;
  - sumidouro;
  - automantido;
  - laço de ganho ≥ 1.
  - O relato traz os pares com meias-vidas na mesma ordem (hoje, dor e susto). As vidas de hoje não mudam (G2).
- **Os drives novos** (`drives_novos`):
  - o tédio pela variedade (DS-4, `atividade`);
  - a curiosidade (só com `com_mundo`, `estimulo_novidade`);
  - a solidão;
  - o estresse (o limiar 0,75, o divisor 256, a meia-vida 1440).
- **Os gestos** (`gestos`):
  - o tapa (dor, susto, estresse);
  - as meias-vidas da dor (60) e do susto (30);
  - o medo da mão no carinho (CD-5).
- **O cérebro A:**
  - o tapa credita `recompensa_tapa` à última decisão, em quem aprende;
  - o `mudanca_no_corpo` credita o carinho pelo corpo, acerta o relógio do cuidado e paga os chamados;
  - o embrulho anda o relógio.
- **Gates:**
  - `tests/test_corpo_grafo.py`: as checagens passam em toda combinação de sub-chaves e falham alto nas tabelas feitas para falhar, e o
    `Corpo` usa a tabela;
  - `tests/test_corpo_drives.py`: o G-MEC do corpo;
  - `tests/test_corpo_risco.py`: o G-RISCO e o G-MEC do cérebro, o tapa e o carinho na última decisão e o G1 com os drives novos;
  - `tests/test_corpo_cerebros.py`: o G1 do cérebro com o corpo no mundo físico.
- **Achado:** com os números PROPOSTOS o tédio do P1 no mundo da bola não passa de ~0,3. A vida curta do G-RISCO roda no ponto (2, ½) da
  grade do plano, e a direção vale por pouco (0,57 → 0,61).

## V2, W-BANCADA-CORPO — o corpo na bancada, etapa 8 (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seção 14) — GATES PASSAM

Rodada 21. A etapa 8 do corpo: o que dá para rodar sem a etapa 6, e o resto declarado. Infraestrutura, sem run de pesquisa; só as sementes
dos testes. Mudaram `experiments/bancada_v2.py`, a fumaça nova `experiments/configs/v2_corpo/fumaca.json`, os testes do P1-cw
(`tests/test_bancada_pesos_janela.py`, `tests/test_dominancia.py`), a tabela de braços de `tests/test_bancada_v2.py` e o teste novo.
`engine.py`, `corpo.py`, `motor_corpo.py`, `lobos.py`, `metrics.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O regime é um campo do braço** (`Braco.regime`), com os nomes do plano:
  - **"hoje":** a chave do corpo desligada;
  - **"química":** a `ConfigCorpo` da bancada (`CONFIG_CORPO_QUIMICA`: ligada, a digestão na taxa C e a Vida, sem os drives novos);
  - **"corpo":** a química mais `drives_novos` e `gestos`.
  - Com o regime, o motor é o `com_corpo(...)` do mundo, e o cérebro A recebe `cfg_corpo`. Os braços sem regime (os de antes) não mudam.
  - **A chave `corpo` da config** troca os números da `ConfigCorpo` (por exemplo a `taxa_digestao`), nunca as sub-chaves.
  - No `padrao` com genoma, os braços do plano usam o `MotorPersonalidade` com a obediência desligada nos dois regimes, como os mundos da
    bola e das frutas.
- **Os braços do plano** (`BRACOS`, seções 3.1 a 3.3 e adendos 1 e 2):
  - **rodam:** o bloco G-HOJE (P0, P1 e P3 em "hoje" e em "química");
  - **esperam a etapa 6 e falham alto com o nó** (`NOS_PENDENTES`):
    - P0-q e P1-q (o `DonoComGestos`);
    - P0-c e P1-c (os drives novos e os gestos);
    - P0-c-tapa, P1-c-tapa e P1-c-tapaX (também o tapa);
    - P1-c-frutas;
    - o **P1-cw**, que passou a ser o P1-c com a `pesos_janela`, como o plano pede (A2.4);
  - o filtro `sem_gestos` também espera o tapa.
- **O corpo no mundo físico fica pendente** (`NOS_PENDENTES["corpo_mundo"]`): o `MotorCorpo` chama `consequencia_corpo` em toda decisão (#238),
  e o `PoliticaLobos` com `cfg_corpo` recusa esse gancho em explorar, comer e brincar no mundo físico (#239). O regime "hoje" roda no mundo
  físico.
- **As medidas** (bloco `corpo` do `medidas.json`, nas vidas com o corpo ligado; seção 5 do plano, funções do #224), nos últimos sete dias:
  - `BE` e `OC` (`tempo_livre_be`; a vida toda ao lado);
  - o cuidado preservado (`cuidado_preservado`);
  - os drives novos (`drives_novos`), indisponíveis com o nó até a etapa 6;
  - o corpo no fim.
- **A dominância pelos receptores:**
  - com o corpo ligado, ela usa a conta do cérebro (`lobos.contribuicoes_corpo`), sobre os receptores da decisão e os de depois (o gancho
    `consequencia_corpo`, anotado pelo `_Registro`);
  - os w_d são os da `pesos_drives_corpo` e, com a `pesos_janela`, os da janela do motivo;
  - nos braços que aprendem pela consequência, a conta é conferida contra o motivo (`sinal_corpo`) e contra os canais; se divergir, falha
    alto.
- **A deriva com o corpo:** as sondas ganham os receptores do próprio estado (`percepcao_da_sonda`, a conta do corpo), e o prior é o P0 do
  mesmo regime.
- **Gates** (`tests/test_bancada_corpo.py`):
  - **o "hoje" é a vida de antes byte a byte** (P0, P1 e P3, sete mundos com o físico, duas montagens);
  - **a química** liga o corpo no motor e no cérebro, passa o G1 e o acoplado, e o P1-química aprende pelo sinal do corpo;
  - **a chave `corpo`** troca os números e não as sub-chaves;
  - **as medidas e a dominância** batem com o motivo e os canais nos três braços, e falham alto quando a conta diverge;
  - **o que espera a etapa 6, o filtro e o corpo no mundo físico** falham alto com o nó, e a trava é só a tabela;
  - a config com o plano (bases 33101, prefixo `corpo`) valida;
  - o `rodar` da fumaça.
- **O mecanismo do P1-cw** (`tests/test_bancada_pesos_janela.py`) é conferido em dois braços de teste no lugar dele: o P1 com a chave e o
  P1-química com a chave. Os dois passam o gate (chave desligada = a origem byte a byte), mudam a vida, passam o G1 e têm a janela refeita
  por fora (pelo vetor e pelos receptores). A dominância confere com os pesos.
- **Fumaça** (`experiments/configs/v2_corpo/fumaca.json`, NÃO canônica):
  - o bloco G-HOJE nos mundos `bola` e `padrao`;
  - os acoplados P1-química ← P0-química e P1-hoje ← P0-hoje;
  - sem artefato.

## V2, CORPO-GESTOS — a etapa 6 do corpo, a parte do motor (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seções 7, 8 e 14) — GATES PASSAM

Etapa 6 da seção 14, o lado do A. A química dos drives novos e dos gestos, o sinal do tapa e o grafo validado (seção 18) são do B, em
paralelo. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/events.py` (o fim do enum), `digilab/motor_corpo.py`,
`digilab/mundo.py` (o canal do `simular_vida_mundo`), `digilab/gestos.py` (novo) e o teste do enum do N7. `engine.py`, `corpo.py`,
`lobos.py`, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O contrato com o B**, combinado antes do código. O motor chama, no `Corpo`:
  - `acao_dono(TAPA)`: dor, susto e estresse; nenhum drive do Estado muda;
  - `acao_dono(ACARICIAR)`: solidão e estresse com o medo da mão, dentro do corpo;
  - `atividade(nome)`: o tédio pela variedade (DS-4), com `"bola"`, `"brincar"` ou `"explorar"`;
  - `estimulo_novidade(n)`: a curiosidade, com a contagem crua;
  - `de_estado(..., com_mundo)`: a curiosidade só existe com o mundo físico (CD-8);
  - e lê `ConfigCorpo.janela_novidade`.
- **Sobre o corpo real do B (#247):** os testes usam um espião do `Corpo` real, que só anota as chamadas do motor, com as sub-chaves de
  verdade (cada uma exige a anterior: `drives_novos` precisa da digestão e da Vida, e `gestos` precisa de `drives_novos`).
- **`AcaoUsuario.TAPA = "tapa"`** no fim do enum, com `ACOES_CORPO`. Nos motores de hoje e no `reproduzir` de hoje, o tapa falha alto; no
  `MotorCorpo` sem `gestos`, falha alto com `GestoSemChave`.
- **Os gestos (`gestos`):** o tapa e o carinho viram só o estímulo do corpo e contam como contato (CD-6), com os efeitos das classes do
  meio na ordem delas (a janela da educação, o índice do evento e o vínculo do `MotorPersonalidade`).
  - **o tapa** vai ao cérebro por `receber_acao_dono`, o sinal direto, e não chama o `mudanca_no_corpo` (CD-9);
  - **o carinho** não é repassado: o cérebro o vê só pelo `mudanca_no_corpo(obs_antes, obs_depois)`, com o `obs.corpo` (e o `obs.mundo`
    no mundo físico). O gancho não diz que gesto foi.
- **Os drives novos (`drives_novos`):**
  - `atividade` uma vez por decisão de brincar ou explorar, depois dos estímulos da ação. No mundo físico ela vem na consequência dele,
    antes do `obs_depois`;
  - **no mundo físico, a novidade:** o motor guarda o que o pet viu e quando, ao decidir e depois de cada decisão com alvo. Uma novidade
    é um objeto dos `vistos` não visto nas últimas `janela_novidade` ticks, achado ao explorar. O `ocorrido` do mundo ganha
    `vistos_novos` (`[[id, tipo], ...]`, vazio fora do explorar), e o corpo recebe a contagem;
  - sem `drives_novos`, o `ocorrido` do mundo é o de hoje.
- **`digilab/gestos.py`:**
  - **`DonoComGestos(base, modo)`:** o `elogiar` vira `acariciar`, e o `repreender` vira `tapa` (modo `"tapa"`) ou `SemGesto` (modo
    `"sem_tapa"`). O `SemGesto` gasta a interação do orçamento sem chegar ao motor, então o orçamento fica igual;
  - **os canais:** `CanalComGestos` e `CanalMundoComGestos`;
  - **as vidas:** `simular_vida_gestos`, e o `mundo.simular_vida_mundo(..., canal_classe=)`.
- **Gates** (`tests/test_corpo_gestos.py`, 22 testes, ~5 s):
  - **G2:** a suíte confere os gabaritos de sempre com o corpo desligado (`test_corpo`, `test_corpo_no_mundo`, `test_mundo` e os demais);
  - o enum, o tapa sem a chave e o carinho de hoje sem `gestos`;
  - o tapa e o carinho nos mundos `padrao`, `bola` e `mundo`: o repasse, o gancho, o contato e o orçamento. O tapa não muda drive;
  - o vínculo e o índice do evento no `MotorPersonalidade`;
  - o `DonoComGestos` nos 4 donos e nos dois modos, com o orçamento inteiro;
  - a atividade por decisão; os `vistos_novos` e a novidade refeitos por fora, com a janela de 1440 e de 60;
  - **G1** com os gestos e os drives novos, nos três mundos e nos dois modos.
- **O `test_corpo_risco` do B:** a vida curta passou a usar o `com_corpo(MotorAmbiente)`. O motor de teste dele avisava a atividade de novo, por
  cima do meu, e o tédio caía em dobro (o `ZeroDivisionError`). A contagem saiu igual à dele: 4/7 → 23/38.
- **Para o D:** na bancada, o `cfg_corpo` com as sub-chaves, o tapa passando pela `PoliticaDoBraco`, o `SemGesto` nos canais dela e o
  filtro `sem_gestos` do acoplado ficam com ele.

## V2, CORPO-WEB — o corpo em TypeScript, etapa 7 (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seção 14) — G-PAR PASSA

Etapa 7 da seção 14: só o motor e a paridade, sem tela e sem versão de pet nova (como no mundo). Mudaram `web/app/motor/corpo.ts` (novo), o
`motor/index.ts` (exporta o corpo), `motor/constantes.ts` (a `ConfigCorpo` no fim), o exportador e o gabarito do corpo (versão 5) e o teste
dele em `tests/test_corpo_quimica.py`. `digilab/`, o app, os pets e os gabaritos da web não mudaram. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **`motor/corpo.ts`** é o porte de `digilab/corpo.py` e de `digilab/corpo_grafo.py`, com os nomes do Python nos registros:
  - **a química e as taxas:** `configCorpo` (a `ConfigCorpo` com a checagem do `__post_init__`), `taxasDe` (a `Config` de hoje pelo espelho
    `C`), `quimicosDe`, `naGrade`, `passoMeiaVida` e `kMeiaVida`; o `divArred` é o de `motor/mundo.ts`;
  - **o grafo (seção 18):** `grafoDoCorpo` monta a tabela única e `checarGrafo` faz as quatro checagens (fechado, sumidouro,
    automantido, laço de ganho ≥ 1, o produto em `BigInt`) e o relato, falhando alto com `GrafoInvalido`;
  - **a classe `Corpo`:** o tick em fases pelos emissores da tabela, a digestão com o descarte, a Vida e o estágio, os drives novos (o
    tédio pela janela, a curiosidade só com `comMundo`, a solidão, o estresse), os gestos (o tapa, a dor, o susto, o medo da mão no
    carinho), os estímulos de hoje e os do mundo físico (a MF-2, o andar, as comidas do mapa) e as leituras (`receptores`, `drives`,
    `estagio`, `paraDict`).
  - O corpo não tem rng: a sujeira e o sono vêm do estado no começo do tick, como no Python.
- **O gabarito, versão 5** (`python experiments/exportar_gabarito_corpo.py`), com quatro seções novas; as da versão 4 saem idênticas
  (conferido):
  - `config`: a `ConfigCorpo` padrão, campo a campo;
  - `grafo`: a tabela e o relato do `checar` em 6 combinações de sub-chaves (com e sem o medo da mão), com e sem o mundo;
  - `de_estado`: o corpo que nasce de 3 Estados em cada combinação;
  - `etapa6_mundo`: os estímulos do mundo físico no corpo da etapa 6.
- **G-PAR** (`web/app/test/corpo.test.ts`, 27 testes, ~1 s). A web lê o próprio `tests/gabaritos/corpo_quimica_python.json`, sem cópia:
  - a config, as taxas, os químicos, os ticks de estágio e os limiares saem iguais;
  - o `div_arred` e a meia-vida;
  - o grafo: a tabela e o relato iguais nas 12 combinações, e as tabelas do `tests/test_corpo_grafo.py` falham alto pela mesma checagem;
  - o corpo que nasce de um Estado (q, receptores, drives, `para_dict`);
  - as grades de casos de cada etapa: a química, a digestão, a digestão lenta, a Vida, o mundo físico sem e com a digestão, a etapa 6 e o
    mundo na etapa 6;
  - as 9 vidas em malha aberta, com o sha256 de q depois de cada operação, os pontos, o digerido e os estágios;
  - a sequência de 3000 operações da etapa 6, com o sha256 de q e da janela.
  - Quatro mutações no `corpo.ts` (a meia-vida sem o mínimo de 1, o carinho sem o medo, a janela do tédio, a sujeira no tick) fazem o
    teste falhar.

## V2, W-LIGA-GESTOS — a etapa 6 do corpo ligada na bancada (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seção 14, etapa 8) — GATES PASSAM

Rodada 22, com o #245 (o motor dos gestos e o `DonoComGestos`, do A) e o #247 (a química dos drives novos e dos gestos e o cérebro, do B)
na `main`. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, a fumaça
`experiments/configs/v2_corpo/fumaca.json`, três testes antigos e o teste novo. `engine.py`, `gestos.py`, `corpo.py`, `motor_corpo.py`,
`lobos.py`, `metrics.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Sem nós pendentes:** saíram `corpo`, `dono_gestos`, `tapa` e o `corpo_mundo` (o #247 resolveu o mundo físico; conferido por teste). O
  `NOS_PENDENTES` e o `FILTROS_PENDENTES` ficaram vazios.
- **Rodam todos os braços do plano:**
  - o bloco G-HOJE;
  - o bloco do corpo: P0-q, P1-q, P0-c e P1-c;
  - o bloco do tapa: P0-c-tapa e P1-c-tapa;
  - o bloco G: P1-c-tapaX e P1-c-frutas;
  - o P1-cw.
- **O dono dos braços com gestos** é o `DonoComGestos(criar_dono(...), modo)`. No P1-c-tapaX ele vem ainda dentro do `DonoTapaFruta`: um
  tapa por consumo da fruta X (`fruta_tapa`, rng `tapa-fruta`) no passo do dono seguinte, dentro do orçamento, no modelo do
  `DonoJulgaFruta`.
- **A bronca do modo sem tapa nos canais:** o `simular_vida_mundo` da bancada aceita `canal_classe` (o `CanalComGestos`), e o mundo padrão
  usa o `simular_vida_gestos`. O `SemGesto` gasta o orçamento fora do log e é contado em `VidaBancada.retirados`. Os gestos ficam fora do
  mundo físico e do `bola_a1` (falha alto).
- **O tapa e o carinho no cérebro:**
  - o tapa passa pela `PoliticaDoBraco` em toda fonte que aprende (CD-10);
  - o carinho (`mudanca_no_corpo`, CD-4) chega nas mesmas fontes;
  - no P0, nenhum dos dois;
  - o `_Registro` acerta o relógio do cuidado no carinho.
- **O filtro `sem_gestos`** do acoplado tira o tapa e o carinho.
- **As medidas:** os drives novos (tédio, solidão, estresse e dor) saem disponíveis no bloco `corpo` dos braços do regime corpo, com os
  gestos da vida. A sonda da deriva ganhou os receptores novos, uniformes em [0, S] pela rng `sonda-corpo` (`percepcao_da_sonda`,
  `receptores_novos_de`).
- **Gates** (`tests/test_bancada_liga_gestos.py`, 39 testes, ~40 s):
  - **os braços do plano rodam e medem**, com o G1 de toda vida;
  - **G-P0C:** o P0-c decide igual ao P0-q, decisão a decisão e com o mesmo log (4 donos × 2 sementes, em `bola`, `padrao` com e sem
    genoma e `iguais_frutas`);
  - **o P1-c-frutas é o P1-c byte a byte**, fora o rótulo;
  - **o orçamento fecha com o `SemGesto`;** no P0, com o aleatório e o relapso, o tapa entra onde a bronca sumia;
  - **o tapa e o carinho chegam ao P1 e não ao P0** (as contagens do cérebro e da memória), e o tapa chega também à fonte informação;
  - **o tapa na fruta X:** a fruta é uniforme pela rng própria, e há um tapa por consumo de X no passo seguinte, com o descarte no passo
    cheio;
  - **os acoplados:** o filtro `sem_gestos`, e o P1-q^ac e o P1-c^ac do P0-q;
  - **as medidas:** os drives novos na medida e os receptores novos na sonda;
  - **o mundo físico:** o corpo roda nele, e os gestos falham alto lá;
  - a config do plano com todos os braços;
  - o replay do disco.
- **Testes antigos:**
  - `tests/test_bancada_pesos_janela.py`: o P1-cw contra o P1-c (a chave desligada sai byte a byte; ligada muda a vida, com o G1; a janela
    é refeita por fora com os receptores novos; a dominância bate com os canais);
  - `tests/test_bancada_corpo.py`: os braços se resolvem, a trava é só a tabela, e o corpo roda no mundo físico;
  - `tests/test_dominancia.py`: o P1-cw.
- **Não entrou:** as medidas descritivas dos efeitos do tapa (plano, seção 5.4).

## V2, BANHEIRO, etapa 2 — a vontade, o conforto, o `aliviar`, o instinto e o alvo (2026-10-07, `docs/TAREFA_V2_BANHEIRO.md`) — GATES PASSAM

Etapa 2 da seção 9 (BN-1 a BN-6 decididas), o lado do corpo e do cérebro. Infraestrutura, sem run; só as sementes dos testes. O banheiro no
mapa, a necessidade como objeto, o limpador, o `limpar` e o `DonoCarinhoBanheiro` são da etapa 3 (A); a web é a etapa 4; a bancada, a 5
(D). `engine.py`, `motor_corpo.py` (só dois campos novos na `PercepcaoCorpo`), `mundo.py`, a bancada e a web não mudaram. Interpretações
em `docs/REGISTRO_DESVIOS.md`.
- **A etapa 1 não existia:** o gabarito das vidas de hoje (`tests/gabarito_banheiro.py` → `tests/gabaritos/banheiro_vidas_de_hoje.json`,
  176 vidas) foi gravado antes de qualquer mudança, num commit próprio:
  - pela bancada, os regimes "hoje" e "química" do corpo e o mundo físico;
  - direto, a etapa 6 inteira com o `DonoComGestos` nos quatro mundos.
- **`AcaoPet.ALIVIAR`** no fim do enum (BN-1). Toda iteração de hoje usa `events.ACOES_PET_HOJE` (as sete de sempre): o bandit, as
  métricas, os traços, a arena, o desejo, a expressão, o cérebro A sem o banheiro, os exportadores e a bancada.
- **O corpo** (`ConfigCorpo.banheiro`, sub-chave depois de `gestos`; `CONFIG_CORPO_BANHEIRO`):
  - a `vontade` (concentração): +150 por tick acordado, mais 1/3 do alimento digerido (com o resto guardado), zerada por
    `estimulo_aliviar`. Acima de 0,75, o desconforto sobe +150 por tick (o gatilho novo `acima` do grafo);
  - a necessidade: `estimulo_necessidade` (+22500 de desconforto) e `passo(..., necessidades=n)` (+100 por tick por necessidade na
    região, até 3);
  - o `conforto` (BN-6): o carinho o sobe +45000 (com o medo da mão), meia-vida 60. O cérebro lê a falta de conforto, S − leitura;
  - os receptores `vontade` e `conforto` (os campos novos da `PercepcaoCorpo`). O grafo passa as quatro checagens.
- **`ConfigBanheiro`** (fim do `config.py`, desligada; registro `instinto_banheiro.PARAMETROS_BANHEIRO`): `ligada`, `limpador`,
  `w_vontade` 4,0, `limiar_urgente` 0,90, `limiar_moderada` 0,50, `w_banheiro_0` S/4, `w_aqui_0` S.
- **O instinto** (`digilab/instinto_banheiro.py`, `PoliticaInstintoBanheiro`, sobre o instinto do mundo):
  - a regra `alivio_urgente`, sem sorteio, logo depois do sono;
  - o `aliviar` no tempo livre com peso w_vontade × vontade;
  - o alvo herdado pelo `escolher_alvo`: `banheiro` S/4 contra `aqui` S, com u / 2^16; na urgência, `aqui`.
- **O cérebro A** (`PoliticaLobos(..., cfg_banheiro=)`, que exige o mundo físico e o corpo com o banheiro):
  - o `aliviar` só nas tabelas em que é candidato (as três de tempo livre e a urgente): **998 pesos de 1000**;
  - o prior da vontade no termo de impulsos;
  - o alvo aprendido, um peso por alvo, pela regra da fruta e com o canal do corpo, pela consequência e pelo carinho;
  - a vontade e o conforto nos drives do sinal.
- **Gates** (`tests/test_banheiro_g2.py`, `tests/test_banheiro_corpo.py`, `tests/test_banheiro_cerebros.py`):
  - **G2:** as 176 vidas de hoje byte a byte;
  - **G-MEC do corpo;**
  - **G-CONS:** com o limpador, o sinal do aliviar no banheiro é maior que fora; sem ele, igual;
  - **G-CAR:** o carinho vale 940, 1759 e 2739 contra 132 do limpador (7 a 21 vezes). Sem o conforto, a solidão em 0,2 daria 164 e
    falharia;
  - **o cérebro no prior é o instinto byte a byte** (3000 observações, a decisão e o alvo);
  - **o aprendizado do alvo em conta exata** (pela consequência e pelo carinho);
  - **o G1 do cérebro pelas chamadas.**
- **Paridade:** o gabarito do corpo foi à versão 5 (a seção `banheiro`). As seções da versão 4 saem idênticas.
- **Para o A (etapa 3):** o `aliviar` é uma ação com alvo.
  - **O alvo:** u da rng `alvo` e os dois candidatos (`banheiro` e `aqui`) no `escolher_alvo`.
  - **Os ganchos:** o `consequencia_mundo` e depois o `consequencia_corpo`.
  - **Os estímulos:** `estimulo_aliviar`, `estimulo_necessidade` e `passo(..., necessidades=n)`.
  - **O motivo do `aliviar`** ainda falha alto no `PoliticaComMotivo`: não há texto na expressão.

## V2, DOIS-PETS, etapas 0 e 1 — o gabarito de hoje e o `Mundo` como componente (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

As duas primeiras etapas do motor da frente dos dois pets (desenho `docs/futuro/dois_pets.md`, seções 2 e 10). Infraestrutura, sem run; só
as sementes dos testes. Mudaram `digilab/mundo.py` e os testes novos. `engine.py`, `motor_corpo.py`, os cérebros, a bancada e a web não.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Etapa 0, num commit próprio, antes de mudar o código:** `tests/gabarito_dois_pets.py` → `tests/gabaritos/dois_pets_vidas_de_hoje.json`,
  276 vidas do mundo físico de hoje, com e sem o corpo, nos dois layouts:
  - **pela bancada**, nos mundos `fisico` e `fisico_afastado`: o P0 com lobos e com o instinto do mundo, o P0z, e P0, P1 e P3 nos
    regimes "hoje" e "química", 2 donos, os 3 lugares e 2 sementes; mais o P1 e o P3 na montagem completa;
  - **direto pelo `simular_vida_mundo`**, o que a bancada não monta no mundo físico: o corpo inteiro da etapa 6 (com a curiosidade e a
    novidade) e a bola deixada perto do pet, com o instinto do mundo e com os lobos aprendendo;
  - a impressão inclui o `resumo_mundo_fisico` inteiro (as rngs do mundo) e o registro da novidade (`_vistos_em`).
- **Etapa 1, a classe `Mundo`** (`digilab/mundo.py`): guarda o que é do mundo e não sabe de pet:
  - as árvores, as comidas, a bola e os fluxos `mundo-arvores` e `mundo-bola`;
  - os registros do mundo: as quedas, as comidas que sumiram, as bolas deixadas e as rolagens;
  - a percepção (`perceber(x, y, tick, pendente)`), as comidas maduras perto, `retirar_comida`, `rolar_bola`, `deixar_comida`,
    `deixar_bola` e o `resumo`.
- **O `MotorMundo` ligado é dono do próprio `Mundo`** (`self.mundo`, com a semente do pet). Guarda o que é do pet: a posição, o alvo
  pendente, a percepção da decisão, os fluxos `alvo` e `mundo-sujeira`, os consumos, as decisões, as regiões, as visitas e as comidas
  deixadas pelo dono. Os atributos e métodos de antes (`comidas`, `arvores`, `bola_mundo`, `quedas`, `situacao`, `bola_em`,
  `_nova_comida`...) leem do `Mundo`, e o `resumo_mundo_fisico` tem as mesmas chaves.
- **A atualização é idempotente por tick** (`Mundo.atualizar`): a segunda chamada no mesmo tick não faz nada, e um tick para trás falha
  alto. O resultado só lê o tick e o fluxo `mundo-arvores`.
- **Gates** (`tests/test_mundo_componente.py`, 18 testes, ~45 s):
  - **G2:** as 276 vidas da etapa 0, byte a byte; os gabaritos `mundo_vidas_de_hoje.json` (96) e `corpo_mundo_vidas_de_hoje.json` (144)
    passam pelos testes de sempre, na suíte;
  - **G-ENGINE:** o sha256 de sempre;
  - **o componente:** o motor é dono do próprio `Mundo` (os mesmos objetos, os fluxos pela semente do pet), e o `Mundo` não guarda
    nada do pet;
  - **a idempotência:** duas chamadas no mesmo tick dão o mesmo resumo (as rngs incluídas), o tick para trás falha alto, e atualizar só
    em alguns ticks dá as mesmas quedas e o mesmo chão que atualizar em todos;
  - **G1 com o `Mundo`:** o replay refaz o resumo do mundo, nos dois layouts, sem e com o corpo.
- **Fora:** o `Grupo` (N motores sobre um `Mundo`, a vez sorteada, o registro do grupo) é a etapa 2, no PR seguinte. O `mundo.ts` não mudou
  (etapa 9).

## V2, W-BANCADA-BANHEIRO — as faixas dos dois pets e a bancada do banheiro, só o que já dá (2026-10-08, `docs/TAREFA_V2_BANHEIRO.md`, etapa 5) — GATES PASSAM

Rodada 25. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, dois testes antigos (a
tabela de braços e o nó do corpo) e o teste novo. `engine.py`, `mundo.py`, `corpo.py`, `lobos.py`, `metrics.py` e a web não.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **As faixas dos dois pets (PDP-6)** em `FAIXAS_RESERVADAS`, com a fonte (`PLANO_ANALISE_V2_DOIS_PETS`, seção 8):
  - 39101…39505: calibração do K e piloto;
  - 40101…40505: validação;
  - 41101…41505 e 42101…42505: os adendos previstos (o degrau 1b e os dois donos).
  - O prefixo `"dois_pets"` entrou em `PREFIXOS_UNIDADES`.
- **Os braços do banheiro** (`PLANO_ANALISE_V2_BANHEIRO`, seções 1 a 3): o 2 × 2 (limpador × carinho depois do banheiro) no P0 e no P1,
  `P0-B00` … `P1-BLC`, nó `banheiro`. O campo novo é `Braco.banheiro`, e `BRACOS_BANHEIRO` dá o limpador e o carinho de cada um.
- **Falham alto com o nó** `NOS_PENDENTES["banheiro"]`: o banheiro no `MotorMundo` (a área, a necessidade como objeto, o limpador, o
  `limpar` que recolhe, o `aliviar` com alvo) e o `DonoCarinhoBanheiro` são da etapa 3, do A.
- **Já montado, atrás do nó:**
  - o corpo com os gestos e a sub-chave `banheiro` (`cfg_corpo_de`);
  - a `ConfigBanheiro` ligada, com o limpador do braço (`cfg_banheiro_de`);
  - o cérebro A com `cfg_banheiro` (o P0 com o aprendizado desligado), ou a `PoliticaInstintoBanheiro` no cérebro `instinto`;
  - o banheiro só no mundo físico, na vida e na config.
  - **A fiação do motor e do dono espera a etapa 3:** o `fabrica_motor` dos braços do banheiro falha alto com o nó, mesmo sem a tabela.
- **As medidas** (seções 4 e 8 do plano, pelas funções do #224):
  - `medidas_banheiro_de` dá a fração diária e os acidentes (`alivios_por_dia`), o dia do critério com a censura e T*
    (`dia_do_criterio`), os alívios até o critério e o cuidado preservado;
  - também dá, por dia: os carinhos (a solidão antes e o sinal pelo corpo), o sinal do alívio recolhido pelo limpador e o peso do alvo
    `banheiro` contra o de `aqui`;
  - e o "chegou tarde" (R-2).
  - `tabela_banheiro` dá a curva de Kaplan–Meier e a RMST por braço (`banheiro.json` no `rodar`).
  - `Bancada.medidas_banheiro` lê o contrato do motor (`motor.alivios`, um dict por `aliviar` com `tick`, `dentro`, `urgente`, `alvo`,
    `distancia` e `recolhido`), conferido e falhando alto. O resto vem do registro de medição e do cérebro no fim de cada dia.
  - O `_Registro` agora anota cada carinho (o tick e os receptores antes e depois).
- **Gates** (`tests/test_bancada_banheiro.py`, 21 testes, ~2 s):
  - **as faixas:** com a fonte, disjuntas, fora das queimadas e das configs; as unidades dos oito prefixos sem colisão entre planos e
    fases; a config com o prefixo pede o plano;
  - **os braços:** declarados como o plano pede; falham alto com o nó; a trava é só a tabela;
  - **as medidas:** em dados com a resposta conhecida; a tabela por braço; o contrato do motor conferido;
  - **o registro** anota cada carinho no tick do `acariciar`.
- **Fora:** os contrastes do plano (G-CARINHO e G-LIMPADOR, com Holm) são do orquestrador; a run só depois das etapas 3 e 4 do banheiro.

## V2, DOIS-PETS, etapa 4, primeira metade — o alvo aprendido no cérebro A (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A parte da etapa 4 que não depende da percepção social (`docs/futuro/dois_pets.md`, seção 8, DP-8). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás da chave), a `ConfigLobos` e `digilab/mundo.py` (o alvo padrão virou uma
função pura, a mesma conta). `engine.py`, o corpo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `ConfigLobos.alvo_aprendido` (desligada) e `w0_alvo` (S/16, PROPOSTO, SEM FONTE; registro
  `lobos.PARAMETROS_LOBOS_DOIS_PETS`). Só no mundo físico; sem ele, falha alto.
- **As classes** (`lobos.CLASSES_ALVO`):
  - comer: `comida`, `comida_podre`, `cheiro`, `continuar`;
  - explorar: `cheiro`, `vagar`, `casa`, `continuar`, e o lugar de `seguir` e `onde_comeu`, que o motor oferece a partir da etapa 3 do A;
  - brincar: `bola`, `continuar`.
- **Um peso por (regra, ação, classe)**, nas regras em que a ação com alvo é candidata (`lobos.REGRAS_ALVO`): **36 pesos**, 792 no
  mundo físico sem o corpo. Com o corpo e o banheiro (998), falha alto pelo teto.
- **A escolha** (`PoliticaLobos._alvo_aprendido`):
  - cada classe presente tem um representante, o primeiro candidato dela na ordem do motor;
  - o peso efetivo é max(0, w) / S, mais 1 na classe do alvo padrão do motor (`mundo.alvo_padrao_de`, o herdado);
  - o sorteio é o de sempre, com u / 2^16;
  - sem alvo padrão, None, como hoje.
- **O aprendizado:** só pela consequência (o crédito do `consequencia_mundo`, ou do corpo no mundo físico), pela regra da sub-decisão da
  fruta (X = S), com o sinal inteiro da decisão. O dono (elogio, bronca, carinho) não mexe no alvo.
- **O P0 usa o padrão do motor:** com o aprendizado desligado, o gancho devolve None, e o P0 com lobos continua o instinto do mundo
  byte a byte.
- **Gates** (`tests/test_alvo_aprendido.py`, 12):
  - **G2:** com a chave desligada, o gancho devolve None (e os gabaritos do mundo, na suíte);
  - **o P0 com a chave é o instinto do mundo byte a byte** (2 donos × 3 lugares × 2 sementes);
  - **G1 do P1 com a chave:** rejogado do log, estado interno incluído; ele aprende e tenta classes fora do padrão;
  - **a conta exata** pela consequência; o dono não ensina o alvo;
  - a comida podre como classe própria, e as classes da etapa 3 já aceitas;
  - o motor usa a mesma função pura do alvo padrão (espião), e as falhas altas.
- **Fica para a etapa 3 do A na `main`:** as entradas sociais (visão e toque), o modelo dos outros (só registrado) e o gate "também com
  o outro à vista".

## V2, DOIS-PETS, etapa 2 — o `Grupo`: N pets de verdade no mesmo `Mundo` (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A etapa 2 do motor da frente dos dois pets (desenho `docs/futuro/dois_pets.md`, seções 2 a 4; DP-1 a DP-3 e DP-7). Infraestrutura, sem
run; só as sementes dos testes. Mudaram `digilab/grupo.py` (novo), `digilab/mundo.py` (o `MotorMundo` aceita o `Mundo` do grupo e a
entrada, e o laço partido), `digilab/motor_corpo.py` (o `_um_tick`) e a `ConfigGrupo` no fim de `config.py`. `engine.py`, os cérebros, a
bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`ConfigGrupo`** (`ligada` False; `CONFIG_GRUPO_LIGADA`): `ids` ("A", "B"; distintos, em ordem, no máximo dois) e `orcamento_por_dia`
  (16, por pet; DP-7). Desligada, o `Grupo` falha alto (`GrupoSemChave`): o `MotorMundo` de um pet continua dono do próprio `Mundo`.
- **As sementes (seção 2):** o mundo e o pet A usam a semente do grupo, s (o A sozinho é a vida de hoje de s); o B usa
  `derivar_semente("segundo-pet", s)` (`sementes_do_grupo`). Os fluxos de cada pet (`alvo`, `mundo-sujeira`, `dono`, `dono-lugar`) saem
  da semente dele.
- **O `Grupo`** (`Grupo(cfg_mundo, semente)`): um `Mundo` e os motores dos pets presentes, num relógio só (`Grupo.tick`, o do mundo). Não
  decide nada.
  - **`entrar(id, politica, fabrica_motor, cerebro, dono)`:** só num início de dia do mundo. A fábrica recebe `mundo=` e `entrada_mundo=`,
    e o motor é conferido (o `Mundo` do grupo, a semente, a entrada, o mesmo `efeito_frutas` dos outros, recém-nascido).
  - **`avancar(n)`:** um evento de avanço do grupo; cada pet presente ganha o avanço no próprio log e os ticks andam intercalados. Em cada
    tick, os pets que decidem agem na ordem sorteada e depois os outros andam o tick deles.
  - **A vez (DP-2):** com dois ou mais pets decidindo no mesmo tick, um sorteio no fluxo `mundo-ordem` (`derivar_semente("mundo-ordem",
    s)`), sobre a lista ordenada pelo id: o `random.shuffle` do CPython escrito com `randrange`. O primeiro age inteiro, e o segundo
    percebe o mundo como ficou. Com um pet só não há sorteio, e o fluxo nem é criado. As vezes ficam em `Grupo.ordens` (derivadas).
  - **O dono:** `acao_dono`, `deixar_comida` e `deixar_bola` por pet (o orçamento e o contato são do pet). O `PetNoGrupo` é a porta do
    `CanalMundo` para um pet.
- **O laço partido:** o `_avancar(n)` da cadeia do `MotorMundo` virou três partes, `_abrir_avanco` (o índice do evento do
  `MotorPersonalidade`), `_um_tick` n vezes (o laço do engine, ou o `_laco(1)` do `MotorCorpo`) e `_fechar_avanco` (a morte conferida do
  `MotorEducacao`). Um teste confere a MRO de `_avancar`, para uma classe nova na cadeia não passar despercebida.
- **A entrada depois do tick 0** (o A vive K dias antes do B; "B só" e "B + Aing" do plano): o relógio do pet (o `Estado`, o log, o
  corpo e a Vida) começa em 0 na entrada, com `MotorMundo.entrada_mundo` = o tick do mundo. O `Mundo` e os registros do mundo físico do
  pet (consumos, decisões, regiões, visitas, comidas deixadas) usam o relógio do mundo. A hora do dia é a mesma nos dois. O mundo pode
  passar dias sem pet: o `Grupo` só anda o relógio, e as quedas desses dias saem na primeira decisão (a atualização idempotente da etapa 1).
- **O registro do grupo (DP-3, `RegistroGrupo`):**
  - JSONL com o cabeçalho na primeira linha: a versão, a semente, os ids, o layout e, por pet, a semente, a entrada e os rótulos do
    cérebro e do dono;
  - os eventos no relógio do mundo, cada um com o `destino` (`grupo` para a entrada e o avanço; `mundo` para deixar a comida e a bola;
    `pet:<id>` para as ações do dono), o `pet` (o do orçamento e do contato) e a `origem` (`dono`; `dono:<id>` na etapa 7);
  - um avanço só, do grupo; o que os pets fazem não entra (sai do replay);
  - `projecao(id)` é o log de hoje do pet, no relógio dele, igual ao log do motor (conferido).
- **`reproduzir_grupo(registro, fabricas, cfg_mundo)`:** refaz o grupo do cabeçalho e rejoga os eventos no mesmo relógio, com o mesmo
  sorteio. Falha alto com evento desconhecido, fora do tick, de pet que não entrou, com o cabeçalho de outra config ou com um registro
  refeito diferente do lido.
- **`simular_grupo(cfg_mundo, s, pets, dias)`** (DP-7, a validação inicial): o `simular_vida_mundo` do grupo. A cada passo do dono o grupo
  anda o passo; depois, para cada pet presente na ordem dos ids, o dono decide pelo que vê daquele pet, com o orçamento dele (16 por dia
  vivido) e a rng `dono` dele (`derivar_semente("dono", semente do pet, rótulo)`). Os pets (`PetDoGrupo`) entram no começo de um passo.
  `dono=None` é o pet sem dono (o parceiro passivo dos testes).
- **Gates** (`tests/test_grupo.py`, 35 testes, ~17 s):
  - **G2 com um pet no grupo:** as 48 vidas diretas de `dois_pets_vidas_de_hoje.json` (o corpo inteiro da etapa 6 incluído) e o
    `simular_vida_mundo` de hoje com os quatro donos, os três lugares, os dois cérebros e as duas sementes, byte a byte; o canal dos
    gestos (o tapa e o carinho) também; nenhum sorteio com um pet; o grupo desligado recusa;
  - **G1-GRUPO:** o replay do texto do registro refaz o grupo bit a bit (os pets, o mundo, as vezes e a rng da ordem), com o B entrando no
    dia 0, 1 e 2, com o corpo e nos dois layouts; a projeção é o log de cada motor; e o replay falha alto com o registro errado;
  - **G-ORDEM:** a ordem da lista dos pets e a ordem de entrada no código não mudam o grupo; o sorteio é o `random.shuffle` do CPython; um
    sorteio só nos ticks com os dois pets decidindo;
  - **G-NUMS-GRUPO:** um B passivo (só ocioso e dormir, sem dono) deixa o A e o mundo iguais aos do A sozinho; com um B que age (instinto,
    lobos ou passivo), as quedas e as vezes sorteadas são as mesmas, e o rastro do A (decisões, consumos, regiões) é o do A sozinho até o
    primeiro evento físico do B (ele come, brinca com a bola, ou o dono dele deixa algo), e muda depois;
  - **a entrada tardia:** o relógio do B, a hora do dia, os registros no relógio do mundo e o orçamento por dia vivido; "B só" e "B + Aing"
    com as quedas do grupo com o A;
  - **a guarda da MRO** do `_avancar`.
- **Fora:** a visão, o toque e a disputa entre os pets são a etapa 3 (o PR seguinte); nesta etapa um pet só muda o mundo do outro pelo
  que faz fisicamente. A troca do `efeito_frutas` no dia K ("B + Aemb") e o efeito por tipo de árvore são da etapa 5 (o D): hoje o grupo
  exige o mesmo `efeito_frutas` em todos os pets. O `mundo.ts` não mudou (etapa 9).

## V2, BANHEIRO, etapa 3 — o banheiro no mapa, a necessidade, o limpador, o `limpar` e o `DonoCarinhoBanheiro` (2026-10-08, `docs/TAREFA_V2_BANHEIRO.md`) — GATES PASSAM

Seções 2 a 5 e 8 da tarefa, o lado do motor (A). Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/mundo.py`,
`digilab/motor_corpo.py`, a `ConfigBanheiro` (a área), o registro `PARAMETROS_BANHEIRO` e uma linha de `digilab/donos.py`. `engine.py`,
`corpo.py`, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `MotorMundo(..., cfg_banheiro=ConfigBanheiro)`, só com o mundo ligado e com o corpo com a sub-chave `banheiro` na frente
  (`com_corpo(MotorMundo)`); o corpo com a sub-chave exige o banheiro no mapa. Falta de uma das duas falha alto (`BanheiroSemMundo`).
  Desligada, nada muda: nenhuma rng, nenhum registro, nenhuma chave em `estado()`, nada no resumo do `Mundo`.
- **O banheiro:** um retângulo de células da casa, `ConfigBanheiro.celulas_x` (0 a 3) e `celulas_y` (0 a 5), PROPOSTOS; funções puras
  `faixa_do_banheiro`, `no_banheiro`, `ponto_do_banheiro` e `zona_da_necessidade` (o banheiro é uma zona própria, `ZONA_BANHEIRO`).
- **O `aliviar` com alvo:** o motor sorteia o u da rng `alvo` e oferece `banheiro` (o ponto mais perto) e `aqui`; sem o gancho do cérebro,
  `aqui`. O pet anda até o alvo (o alcance e o custo de energia de sempre) e alivia onde parou (chegou tarde). Urgente (a vontade da
  observação acima de `limiar_urgente`) com o alvo `banheiro` falha alto.
- **A necessidade** é um objeto do `Mundo` (contador próprio; fora dos `vistos`). O limpador a recolhe na hora dentro do banheiro; fora,
  ela fica. O `limpar` do dono recolhe as da zona do pet.
- **No corpo** (`MotorCorpo`): o aliviar vira `estimulo_aliviar` e, quando a necessidade fica, `estimulo_necessidade`, depois do andar; a
  cada tick, `passo(..., necessidades=n)` com as necessidades na zona do pet (`MotorMundo.necessidades_na_zona`).
- **Os registros:** `motor.alivios` no contrato da bancada (`tick` do mundo, `dentro`, `urgente`, `alvo`, `distancia` ao banheiro na
  decisão, `recolhido`), `motor.recolhas` (o limpar) e `Mundo.recolhidas`; `estado()["banheiro"]` (alívios, dentro, necessidades no chão,
  na zona) e o resumo do mundo físico, só com a chave.
- **`DonoCarinhoBanheiro`:** um `acariciar` no primeiro passo do dono depois de cada alívio dentro do banheiro, fora do orçamento, por
  `simular_vida_mundo(..., carinho=)`. O dono sintético não julga o `aliviar` (`julgar_acao` devolve 0).
- **Gates** (`tests/test_banheiro_mundo.py`, 30 testes, ~6 s):
  - **G2:** a chave explícita desligada é a vida de hoje; os gabaritos de sempre (banheiro, dois pets, corpo no mundo, mundo) na suíte;
  - **as chaves** vão juntas e falham alto;
  - **G-MEC:** a vontade a zero e o cheiro; o limpador só no banheiro; o desconforto pela zona (o banheiro à parte, até 3); o `limpar` da
    zona; o urgente alivia aqui; o alvo `banheiro` leva o pet até lá ou alivia no caminho; sem gancho, `aqui`;
  - **G-CONS:** com o limpador, o sinal pelo corpo do aliviar dentro é maior que fora; sem ele, igual;
  - **G-CRED:** cada carinho no passo seguinte a um alívio dentro, creditado à decisão de aliviar, fora do orçamento;
  - **G1:** o replay bit a bit com o instinto e com os lobos aprendendo (P1), com e sem o limpador, com o carinho, nos dois layouts, e no
    grupo de dois pets (as necessidades são do mundo de todos);
  - as quedas iguais com e sem o banheiro; os `alivios` no contrato da bancada (`medidas_banheiro_de`).
- **Achado (fumaça descritiva, sementes dos testes):** com o banheiro nas células 0 a 3 e 0 a 5, o pet alivia a 185–260 subunidades dele
  (mediana) e o alcance de uma decisão é 60: em 5 vidas de 7 dias, 1 alívio dentro no P0 e 0 no P1 (que escolheu o `banheiro` 12 vezes).
  O 2 × 2 do plano quase não teria carinho nem limpador para medir. Fica para o Matheus e o plano.
- **Para o D (destravar `NOS_PENDENTES["banheiro"]`):** a fábrica dos braços do banheiro é o `com_corpo(MotorMundo)` com o `cfg_corpo_de`
  e o `cfg_banheiro_de` que a bancada já monta; o `simular_vida_fisico` passa `carinho=DonoCarinhoBanheiro()` nos braços com carinho
  (B0C, BLC) depois das ações do dono do passo; o `medidas_banheiro` já lê o `motor.alivios` deste contrato.

## V2, REDE-DE-SI, etapas 0, 1 e 2 — o automodelo em observação (2026-10-08, `docs/TAREFA_V2_REDE_DE_SI.md`) — GATES PASSAM

Etapa 2 do ego (`docs/futuro/ego_existencia.md`), com RS-1 a RS-7 pela recomendação. Infraestrutura, sem run de pesquisa; só as sementes dos
testes. Mudaram `digilab/rede_de_si.py` (novo) e a `ConfigRedeDeSi` no fim de `config.py`. `engine.py`, o `AcaoPet`, o cérebro, o corpo,
o motor, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A regra de quem aprende (E-6, RS-7):** a Decisão aprende por reforço, a rede de si por erro de previsão, e nenhuma outra peça aprende.
  A regra antiga ("só a Decisão aprende") fica revista por esta.
- **Etapa 0, num commit próprio, antes da rede:** `tests/gabarito_rede_de_si.py` → `tests/gabaritos/rede_de_si_vidas_de_hoje.json`, 40
  vidas: o P1-c, o P0-c e o P1-c-tapa na bola; o P1-c e o P1+ped (ainda sem o corpo) no `iguais_frutas`; montagens simples e completa
  (T3); o atencioso e o aleatório; sementes 101 e 202.
- **A rede (`RedeDeSi`, etapa 1):**
  - **as entradas:** só os receptores da `PercepcaoCorpo` (todos os presentes, na ordem dos campos), a ação escolhida, o contexto da
    observação (a bola, a comida boa e o pedido vigente, 0 ou S, também pelos `vistos` do mundo físico) e a idade em faixas pelas decisões
    vividas (limites 96, 288 e 672). Nada de químico, `Estado`, pesos do cérebro, regra do instinto ou sonda;
  - **a cabeça do corpo:** por horizonte (1, 4 e 16 decisões, RS-1) e receptor, `corte(div_arred(Σ w x, S), 0, S)`. O prior é a
    persistência (RS-2). O LMS em inteiros chega quando a leitura real chega, cortado em w0 ± teto;
  - **a cabeça da autoria:** por ação, a mesma forma, com o alvo um-quente da ação escolhida, aprendido na hora. O prior é uniforme
    (S / 8). As contrafactuais "sem o pedido" (pedido = 0) e "ao nascer" (a primeira faixa) são a mesma conta;
  - **o erro exposto (E-11, sem leitor):** por receptor e horizonte, o erro absoluto recente (uma média em inteiros) e a surpresa;
  - **os registros:** por decisão, as leituras, as previsões, a autoria e as duas contrafactuais, e a surpresa (para a bancada, etapa 3);
  - **os números:** `passo` S/16, `teto` 4 S, `fator_erro` S/16 (PROPOSTOS; registro `rede_de_si.PARAMETROS_REDE_DE_SI`). **804 pesos** com
    o corpo da bola e das frutas (10 receptores) e 911 com a curiosidade do mundo físico. Com o banheiro no mundo físico (13 receptores),
    passa de mil e falha alto.
- **O embrulho (`PoliticaComRede`, etapa 2):** entrega à rede a observação e a ação depois que o cérebro escolheu, e repassa todo o resto
  ao cérebro por `__getattr__` (o que existe nele existe no embrulho, e o que não existe também não).
- **Gates** (`tests/test_rede_de_si.py`, 61):
  - **G-INT:** pela AST, nenhuma constante float, nenhuma divisão `/`, nenhum `math`, `random`, `float` ou `round`;
  - **G-PESOS:** a contagem e o teto que falha alto;
  - **a conta exata** de um passo do LMS (corpo e autoria); **com `passo` 0, a persistência para sempre**;
  - as contrafactuais e o erro exposto em contas exatas; o contexto do mundo físico e das frutas;
  - **G-OBS:** as 32 vidas com corpo da etapa 0 saem byte a byte com a rede observando (log, estado, `estado()`, ações, rngs, registro do
    mundo e o estado interno do cérebro); as 8 sem corpo falham alto;
  - **G-RECEPTOR:** a rede só importa `config` e `events`; um químico sem receptor (o `alimento`, a `vida`) não muda a percepção; o
    `Estado`, o relógio do cuidado e a informação do dono não mudam a rede;
  - **G1-REDE:** o replay refaz o estado da rede bit a bit.
- **Fica para a etapa 3 (D):** a chave `rede_de_si` da bancada, a rede congelada e o oráculo por replay, os braços P1-c-lenta e P1+ped-c, as
  medidas e as faixas. A troca da digestão (2b) é do A.

## V2, DOIS-PETS, etapa 3 — visão, toque e disputa, o degrau 1 (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A etapa 3 do motor dos dois pets (desenho `docs/futuro/dois_pets.md`, seções 3, 5 e 6; DP-4 e DP-11). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/mundo.py`, `digilab/grupo.py`, o campo `Observacao.social` em `digilab/policy.py`, a
`ConfigGrupo.raio_toque_celulas`, uma linha de `digilab/motor_corpo.py` (o `obs.social` na observação do gesto) e o G-NUMS-GRUPO de
`tests/test_grupo.py`. `engine.py`, o `AcaoPet`, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`Observacao.social`** (padrão None): a `PercepcaoSocial` (`mundo.py`), que o `MotorMundo` injeta só dentro de um `Grupo` com outro pet
  presente. Sem o grupo, ou sozinho nele, fica None, e a vida é a de hoje. Os três campos, só com o que é físico:
  - `outros`: `(id, dx, dy, d, acao_visivel)` dos pets no raio da visão do mundo, em ordem de d e de id. A ação visível é a da última
    decisão do outro (a deste tick, se ele veio antes na vez);
  - `onde_comeu`: `(id, x, y, idade)` do último ponto em que este pet **viu** cada outro comer (o comedor dentro do raio, no momento do
    consumo), com a idade em ticks;
  - `toque`: `(id, tipo, direcao, idade)` do último contato com cada outro.
- **A visão e o toque são do grupo** (`Grupo.perceber_social`, `Grupo.viu_comer`), por funções puras do `mundo.py` (`perceber_social`,
  `em_contato`, `direcao_vizinha`, `tipos_do_contato`) que só recebem posição, ação visível, consumo visto e contato. Nunca o estado
  interno do outro.
- **O toque (5.2):** no fim de cada tick com decisão, com dois pets ou mais, depois da vez sorteada: contato com as células a até
  `raio_toque_celulas` (1) em Chebyshev, um por par e por tick. O tipo sai do que aconteceu: `disputa_ganhou`/`disputa_perdeu`, depois
  `encostou`/`encostaram` (quem seguiu o outro neste tick), depois `esbarrou`. A direção é a da tabela do cheiro (1 a 8), 0 na mesma
  célula. O toque não mexe no corpo (degrau 3).
- **A disputa:** a comida que um comeu neste tick e que o outro tinha como alvo neste tick, ou trazia da decisão anterior. O primeiro na
  vez come; o segundo não acha (o alvo some, e o comer sem comida não dá fome, MF-2). Fica registrada com ou sem contato.
- **Os candidatos do explorar** (seção 6), depois dos de hoje: `seguir` (onde está cada outro visto) e `onde_comeu` (cada ponto da
  memória do consumo visto). O padrão do motor e o instinto nunca os escolhem; o `continuar` deles leva ao ponto antigo.
- **Os registros** (derivados; o replay refaz; no `Grupo.resumo`, que o G1 compara):
  - no grupo: `contatos` (os tipos, as direções e as células) e `disputas` (o vencedor, se ele veio primeiro na vez, a distância de cada
    um à comida, se o perdedor decidiu no tick e se houve contato);
  - em cada motor (`resumo_social`): os consumos vistos (`vistos_comer`), as idas a `onde_comeu` (chegou, comeu, comidas boas à vista na
    chegada), o tempo à vista (`a_vista`, decisões com cada outro visto) e as decisões no grupo.
- **Gates** (`tests/test_grupo_social.py`, 27 testes, ~3 s):
  - **G-RECEPTOR-SOCIAL:** a `PercepcaoSocial` só tem os três campos, com números e nomes; nenhum cérebro importa o grupo, o engine ou um
    motor (só as funções puras do mundo); mudar a fome, o humor, os pesos, a memória e o toque do B, no mesmo lugar e fazendo o mesmo, não
    muda o que o A percebe, e mudar a posição ou a ação muda;
  - **G-SENTIDOS (visão e toque):**
    - o toque nos casos da seção 5.2 (disputa, encostar, esbarrar), o contato na mesma célula ou na vizinha e nenhum a duas células,
      também numa vida tick a tick, e a direção;
    - a visão só no raio, em ordem, com a ação da última decisão do outro, conferida decisão a decisão pela vez sorteada;
    - o consumo visto só com o comedor no raio, no momento;
  - **G-MEC-SOCIAL:**
    - a disputa em 4 sementes: o primeiro na vez come, e o outro não come e não acha;
    - o `onde_comeu` só depois de um consumo visto, no ponto da memória;
    - os candidatos sociais só no explorar, o `seguir` só com o outro visto e no lugar dele, depois dos de hoje;
    - o padrão do motor nunca os escolhe;
    - as idas e o tempo à vista registrados;
  - **G2:** sem o grupo, ou com um pet só nele, o `obs.social` é None e não há candidato a mais; com o B entrando no dia 1, o A só tem a
    percepção social depois disso. Os gabaritos de sempre passam na suíte (o grupo com um pet, as 276 vidas da etapa 0, o mundo e o
    corpo);
  - **G1-GRUPO com os sentidos:** o replay do registro refaz o grupo bit a bit (contatos, disputas e registros sociais incluídos), com os
    cérebros que seguem, que vão onde viram comer, que comem tudo, e com os lobos do alvo aprendido;
  - **os lobos no grupo:** com o alvo aprendido (#255), eles escolhem o `seguir`; no prior, o P0 com lobos é o instinto do mundo byte a
    byte, com os dois pets se vendo e se tocando.
- **O G-NUMS-GRUPO da etapa 2:** com um B passivo, a vida do A segue igual à do A sozinho. Os lobos agora anotam no motivo o candidato
  `seguir` a mais (o A vê o B); o teste confere o estado interno sem essa anotação.
- **Fora:** a audição e o cheiro (o degrau 1b, etapa 8); as entradas sociais e o modelo dos outros no cérebro A (a segunda metade da
  etapa 4, o B); a bancada do grupo (etapa 5, o D); o grupo em TypeScript (etapa 9).

## V2, W-BANCADA-DOIS-PETS — as faixas da rede de si, a bancada do grupo e o banheiro destravado (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`, etapa 5) — GATES PASSAM

Rodada 26, com o `Grupo` do #257, o alvo aprendido do #255, a etapa 3 dos dois pets (#263: visão, toque e disputa) e a etapa 3 do banheiro
(#265) na `main`. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, `digilab/metrics.py`
(`vez_no_grupo`), a fumaça nova `experiments/configs/v2_dois_pets/fumaca.json`, os testes do banheiro e do `NOS_PENDENTES` e o teste novo.
`engine.py`, `grupo.py`, `mundo.py`, `lobos.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **As faixas da rede de si (RS-6)** em `FAIXAS_RESERVADAS`, com a fonte (`PLANO_ANALISE_V2_REDE_DE_SI`, seção 8): 43101…43505
  (calibração e piloto) e 44101…44505 (validação). O prefixo `"rede_de_si"` entrou em `PREFIXOS_UNIDADES` (o plano o pede ao D).
- **O banheiro destravado** (o nó `banheiro` saiu, com o #265): a fábrica dos braços do banheiro é o `com_corpo(MotorMundo)` com o
  `cfg_banheiro_de`; nos braços com carinho (B0C, BLC) o `simular_vida_fisico` passa o `DonoCarinhoBanheiro`, fora do orçamento
  (`VidaBancada.carinhos`); o `medidas_banheiro` lê o `motor.alivios` do #265 (no cérebro `instinto`, sem os pesos do alvo).
- **O mundo da unidade** (plano, seções 2 e 3): `tipo_ruim(s)` (uniforme, rng `dois-pets-ruim`), `efeito_dois_pets` (o ruim com o
  `efeito_humor_ruim`, os outros neutros) e `desarranjo_dois_pets(s)` (rng `dois-pets-embaralha`, como o `desarranjo_n6`).
- **O A embaralhado** é o `MotorMundoTroca` (subclasse do `MotorMundo`, só no grupo): o efeito desarranjado nos K dias e o verdadeiro a
  partir do dia K, trocado no fim do avanço que chega ao tick (um avanço que passasse falha alto). A troca fica em `troca`, e o replay a
  refaz.
- **Os braços** (`BRACOS_GRUPO`, `EspecGrupo`): `B-so`, `B+Ainf`, `B+Aemb`, `B+Aing` e o `A-so` da calibração do K. O B é sempre P1 e entra no
  dia K; o A é P1 no tick 0 (informativo, embaralhado) ou P0 junto com o B (ingênuo). O grupo vive K + `dias` (o `A-so`, os `dias`). Sem
  genoma (temperamento neutro).
- **A fábrica do grupo** (`Bancada.grupo`): o `simular_grupo`, com um dono para todos (o atencioso, `DonoComLugar`, com a semente de cada
  pet), o orçamento por dia vivido de cada pet e só o cuidado (o `CanalSemEnsino` ao vivo, PMF-3). O cérebro é o da bancada com o **alvo
  aprendido** (`bancada_grupo`). O G1 é conferido em todo grupo (`conferir_replay_grupo`).
- **As medidas** (`Bancada.medir_grupo`, do replay de medição conferido):
  - a R de cada pet pela `taxa_fruta_ruim` (fruta madura, efeito vigente do tipo no tick): no B, os 7 primeiros dias, a vida toda e por
    dia; no A, por dia, até o dia K e depois;
  - o D_FE e a privação; os pesos do alvo aprendido no fim de cada dia; a vez no tick (R-5); o chão no dia K (R-3);
  - **as sociais** (`Bancada.medidas_sociais`, dos registros do #263): o uso do `seguir` e do `onde_comeu` por dia, o que o pet viu comer
    (por tipo, e quantos do tipo ruim), a disputa (quantas, quantas ganhou, as distâncias), o toque por tipo e dia, o tempo à vista e as
    idas a `onde_comeu`.
- **Atrás de `NOS_PENDENTES`, falhando alto:**
  - `cerebro_social` (as entradas sociais e o modelo dos outros, a segunda metade da etapa 4, do B): trava o modelo dos outros
    (`Bancada.modelo_dos_outros`) e a run com as sementes do plano (`validar_config_grupo`), porque o cérebro do plano os tem;
  - `canais_fruta_mundo`: com os canais (a montagem completa liga no P1), comer a fruta que mexe no humor falha alto no cérebro do mundo
    físico (CANAIS-REFORCO, a "rota de adendo" do MUNDO-CEREBROS). Trava a config e o grupo; sem a tabela o cérebro falha (teste: o `A-so`
    na semente 505). Fica até o Matheus decidir.
- **Gates:**
  - `tests/test_bancada_dois_pets.py` (56): as faixas e o prefixo; o mundo da unidade e os braços; o G1 de todo grupo; **o pet sozinho do
    grupo é a vida de hoje** da bancada byte a byte; as mesmas vezes sorteadas nos braços com dois pets; as mesmas quedas; o chão do dia K;
    a troca; o orçamento e o cuidado só; o alvo aprendido; as medidas, e as sociais conferidas contra os registros (com uma disputa, no
    B + Aing semente 303); os nós e as travas; a config e o `rodar_grupo`;
  - `tests/test_bancada_banheiro.py`: os oito braços do banheiro rodam e medem (com o banheiro maior só no teste, para haver alívio dentro:
    o carinho só no B0C e no BLC, o limpador só no BL0 e no BLC, o orçamento, as medidas), e o instinto do alívio mede sem os pesos.
- **Fumaça** (`experiments/configs/v2_dois_pets/fumaca.json`, NÃO canônica): os cinco braços do grupo, K = 1, 2 dias; sem artefato.

## V2, DOIS-PETS, etapa 4, segunda metade — as entradas sociais e o modelo dos outros no cérebro A (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A parte da etapa 4 que dependia da percepção social do #263 (`docs/futuro/dois_pets.md`, seção 8, DP-8). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás das chaves), a `ConfigLobos` e uma checagem em `digilab/motivo.py`.
`engine.py`, o mundo, o grupo, o corpo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **As chaves** (`ConfigLobos`, PROPOSTAS; registro `lobos.PARAMETROS_LOBOS_DOIS_PETS`): `entradas_sociais` e `modelo_outros` (desligadas,
  só no mundo físico; fora dele falham alto), `janela_social_ticks` (240, o "recente") e `fator_familiaridade` (S/64).
- **As entradas sociais** (`lobos.ENTRADAS_SOCIAIS`, `lobos.entradas_sociais`), 15, todas 0 ou 1, só do que `Observacao.social` traz:
  - `outro_a_vista`;
  - `viu_comer`: viu algum outro comer há no máximo a janela;
  - `acao_<a>`: a ação visível do outro mais perto, um-quente sobre as 8 do `AcaoPet`;
  - `toque_<tipo>`: o tipo do último contato na janela, um-quente sobre os 5 tipos (`mundo.TIPOS_TOQUE`, conferido na carga).
  - Sem o grupo, ou sozinho nele, todas 0.
- **No cérebro:** nas regras de tempo livre (`tempo_livre`, `bola_no_cenario`, `fruta_no_cenario`), um peso por (regra, ação, entrada),
  **prior 0**, só nas ações que o instinto propõe em cada regra (4, 4 e 5): um candidato fora delas falha alto. O termo vai ao lobo de
  decisão; aprende pela regra da L1, com o canal do corpo, de toda fonte que ensina a tabela da regra. O outro pet não manda sinal.
- **Os pesos (PDP-1, o degrau 1 sem o corpo):** 951 com as entradas sociais e **987 com o alvo aprendido**. Com o corpo dos drives novos
  passa de mil e falha alto.
- **O modelo dos outros** (`lobos.ModeloOutros`), **só registrado** (`estado_interno()["modelo_outros"]`), por pet conhecido:
  - **familiaridade:** a média móvel do outro à vista, em inteiros, a cada decisão;
  - **confiança na comida:** as idas a `onde_comeu` dele que chegaram e, delas, as que acharam comida boa (comeu, ou comida boa à vista
    na chegada);
  - **afinidade:** `divididas` (o pet comeu e viu o outro comer no mesmo intervalo entre decisões, sem disputa) e `perdidas` (cada toque
    novo de `disputa_perdeu`), com o saldo. Confiança e afinidade nunca se somam, e nada tem rótulo.
  - Os eventos são identificados pelo tick no relógio do pet (a hora do dia, como o do N6) menos a idade: o mesmo evento conta uma vez.
- **O motivo:** um termo social aprendido que pese na decisão faz o `motivo_lobos` falhar alto, como as entradas do corpo (sem fator na
  expressão).
- **Gates** (`tests/test_entradas_sociais.py`, 29):
  - **G2:** com as chaves e um pet só no grupo, a vida de hoje (o resumo do grupo e os pesos de sempre); os sociais ficam em zero;
  - **no prior, o P0 com lobos (alvo aprendido e as duas chaves) é o instinto do mundo byte a byte, com o outro à vista** (sementes 101 e
    202);
  - **G1:** o replay do registro do grupo refaz os dois cérebros bit a bit, com o B entrando no dia 0 e no dia 1;
  - **a conta exata:** o termo no peso efetivo e um passo da regra nos pesos sociais;
  - **o modelo dos outros não muda a decisão:** a vida com ele e sem ele é a mesma (3 sementes); pela AST, só o `agir` (antes de decidir),
    o `consequencia_mundo` e a serialização o tocam;
  - **as contas do modelo:** em casos montados e numa vida, onde as idas e os acertos batem com o registro do motor (`idas_onde_comeu`) e a
    familiaridade é refeita da percepção.
- **Fica para depois:** a bancada do grupo (etapa 5, D), que tem de repassar o `consequencia_mundo` ao cérebro para o modelo contar as
  idas; a audição e o cheiro como entradas (etapa 8); o modelo decidindo (degrau 3).

## V2, W-BANCADA-MODELO — as entradas sociais e o modelo dos outros na bancada do grupo (2026-10-11, `docs/TAREFA_V2_DOIS_PETS.md`, etapa 5) — GATES PASSAM

Rodada 27, com o #266 (as entradas sociais e o modelo dos outros no cérebro A, do B) na `main`. Infraestrutura, sem run de pesquisa; só as
sementes dos testes. Mudaram `experiments/bancada_v2.py`, o teste do grupo e o do `NOS_PENDENTES`. `engine.py`, `grupo.py`, `mundo.py`,
`lobos.py`, `metrics.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O repasse do `consequencia_mundo`:** a `PoliticaDoBraco` o repassa explicitamente ao cérebro, em toda fonte (o P0 também). O cérebro
  anota o motivo e o modelo dos outros conta as idas a `onde_comeu` e o que o pet comeu; só na fonte consequência há sinal pendente para
  creditar. O cérebro sem o gancho (o instinto do mundo) não recebe nada. Antes o repasse já acontecia pelo `__getattr__`; agora é um
  método da classe, testado.
- **O cérebro do grupo** (`Bancada.bancada_grupo`): o da bancada com o alvo aprendido, as `entradas_sociais` e o `modelo_outros` (#266). No
  prior, o P0 é o instinto do mundo byte a byte, também com o outro à vista.
- **O nó `cerebro_social` saiu.** Fica só o `canais_fruta_mundo` (a rota do humor no cérebro, do B; o Matheus decidiu manter a montagem
  completa).
- **A run do plano** (`validar_config_grupo`, sementes fora das dos testes) agora pede a montagem completa (o cérebro da seção 2), e por isso
  falha alto com o nó dos canais até o PR do B.
- **As medidas do modelo** (plano, seção 4: a familiaridade, a confiança por atividade e a afinidade, só registradas):
  - `Bancada.modelo_dos_outros(vida)`: o modelo no fim da vida, por pet, como o cérebro o serializa (um cérebro sem ele falha alto);
  - em cada pet do `medir_grupo`, `modelo_outros_por_dia`: o modelo no fim de cada dia vivido, pelo replay de medição.
- **Gates** (`tests/test_bancada_dois_pets.py`, 67):
  - o cérebro do grupo com as três chaves nos dois pets; o modelo de um pet sozinho não conhece ninguém;
  - **o modelo conta as idas e os acertos que o motor registra** (as idas a `onde_comeu` que chegaram, por outro), nos três braços com
    dois pets, em três sementes, inclusive no P0 do B + Aing;
  - o repasse explícito em toda fonte, e o cérebro sem o gancho;
  - **o modelo não muda a vida do grupo** (o registro e cada pet iguais sem ele, fora o modelo no estado interno);
  - o modelo por dia nas medidas, e o do último dia é o do fim;
  - a run do plano pede a montagem completa e falha alto com os canais; sem o nó, valida;
  - os gates de antes (o pet sozinho é a vida de hoje, as vezes, as quedas, a troca, o orçamento, as sociais).

## V2, CANAL-FRUTA-MUNDO — a rota do canal do humor no mundo físico (2026-10-11, decisão do Matheus) — GATES PASSAM

A falha que o D guardou no nó `canais_fruta_mundo` (o A só, semente 505): com os canais, comer a fruta que mexe no humor falhava alto no
cérebro do mundo físico, porque o canal do humor (a E2) vai aos pesos que leem a identidade da fruta e o cérebro do mundo não tinha nenhum.
Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás da chave) e a `ConfigLobos`. `engine.py`, o
mundo, o grupo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `ConfigLobos.presenca_fruta_mundo` (desligada, PROPOSTA; só no mundo físico, fora dele falha alto).
- **A rota:** a decisão de comer lê a fruta madura à vista (`lobos.presenca_no_mundo`, pelos `vistos` da percepção do mundo; a podre não
  conta), um peso por fruta, **prior 0**, em toda regra em que comer é candidato. É a FRUTA-NO-CENARIO parte B no mundo físico, com os
  mesmos pesos (`pesos_comer_fruta`) e a mesma regra de aprendizado (`atualizar_comer_fruta`, só pela consequência). Pela `ROTA_CANAIS`, o
  canal do humor vai a eles; no escalar, o sinal inteiro, como no mundo das frutas.
- **Os pesos:** +3; o degrau 1 dos dois pets (o alvo aprendido e as entradas sociais) fica em **990**, abaixo de mil.
- **Um conserto no caminho:** o registro da decisão lia a presença de `obs.frutas_cenario` e passou a ler a mesma presença do peso efetivo
  (no mundo das frutas são o mesmo valor; nada muda lá).
- **Gates** (`tests/test_canal_fruta_mundo.py`, 10):
  - **G2:** a chave desligada é a vida de hoje (os gabaritos, na suíte); **com a chave e os canais no mundo `iguais`** (o humor da fruta é
    zero), **o P0 e o P1 da montagem completa saem byte a byte** iguais aos de sem a chave, com os pesos novos em zero e o pet comendo fruta;
  - **a conta exata:** a presença pela percepção; o termo no peso efetivo na `fruta_no_cenario` e na `fome_moderada`; um passo pelo canal do
    humor só na fruta presente, e o canal do corpo não mexe na presença;
  - **a falha real do D:** sem a chave, o A só da semente 505 falha alto (CANAIS-REFORCO); com ela roda (o G1 do grupo, conferido pela
    bancada), o peso do tipo ruim desce e os outros ficam em zero;
  - a contagem dos pesos e as falhas altas da chave.
- **Para o D:** destravar o nó `canais_fruta_mundo` é ligar a chave nos braços do mundo físico com os canais (a montagem completa), pela
  chave `"lobos"` da config ou na bancada do grupo.

## V2, BANHEIRO-CONTINUAR — a ida ao banheiro continua, e o `_tick_social` do aliviar no grupo (2026-10-11, decisão do Matheus) — GATES PASSAM

Pedido do Gerente depois do #265. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `digilab/mundo.py`,
`digilab/instinto_banheiro.py`, o G-MEC antigo de `tests/test_banheiro_mundo.py` e os testes novos. `engine.py`, os lobos, o corpo, a
bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A continuação** (atrás da chave do banheiro):
  - com o alvo `banheiro` fora do alcance, o pet anda o alcance e segura a vontade: nada vai ao corpo além do andar, e não há necessidade
    nem registro em `alivios`;
  - o alvo fica pendente, como o `continuar`, e a percepção mostra `alvo_pendente` "banheiro" na decisão seguinte;
  - a ida segue se o cérebro escolher `aliviar` de novo; outra ação a desfaz, e com `aqui` o pet alivia onde está;
  - a regra urgente segue aliviando `aqui`, com ou sem a ida pendente;
  - o registro novo é `idas_banheiro`, no resumo do mundo físico. O `estado()` e o contrato dos `alivios` não mudam.
- **O instinto** escolhe `banheiro` sem sorteio com a ida pendente, fora da urgência. Não ganhou regra nova (os lobos rodam a sonda dele e
  não têm peso para outra tabela). **Os lobos não leem a ida:** sorteiam o alvo pelos pesos de sempre.
- **O `_tick_social` do aliviar no grupo:** o ramo do ALIVIAR passa a preenchê-lo como os outros ramos (o alvo do aliviar, sem `social` e
  sem `comeu`). Antes, a disputa e o toque do fim do tick liam o de uma decisão velha.
- **Gates** (`tests/test_banheiro_continuar.py`):
  - **G2:** a chave desligada é a vida de hoje (os gabaritos de sempre, na suíte). Com o banheiro ligado, as 34 vidas de
    `tests/gabaritos/banheiro_ligado_antes.json`, gravado com o código de antes (`tests/gabarito_banheiro_ligado.py`):
    - sem alívio no caminho, a vida inteira sai igual;
    - com um, tudo sai igual até a primeira decisão que aliviava no caminho, e nela o pet está no mesmo ponto, com o mesmo alvo, segurando;
    - no grupo, o corte é o primeiro desses ticks entre os dois pets;
  - **G-MEC:**
    - a ida de três decisões (60, 60, 17) alivia dentro só na chegada;
    - a vontade sobe enquanto o pet segura e zera ao aliviar;
    - `aqui` no meio alivia onde está; outra ação desfaz a ida;
    - a urgência alivia `aqui`;
    - ao alcance, nada muda;
  - **o instinto** segue a ida, e a urgência vence;
  - **G1:** o replay com a ida que continua (o instinto) e com os lobos aprendendo;
  - **o grupo:** todo pet que decidiu tem o `_tick_social` do tick, com o alvo do aliviar.
- **Fumaça descritiva** (a do #265, sementes 101…505, 7 dias, atencioso no comedouro, com o carinho):

  | braço | alívios dentro, antes → depois | idas que seguraram | continuações | como as idas acabaram |
  |---|---|---|---|---|
  | P0 (instinto) | 1 → 0 | 6 | 1 | 5 trocaram de ação (4 comeram, 1 ficou ociosa) |
  | P1 (lobos, T3) | 0 → 0 | 2 | 0 | 1 trocou de ação, 1 aliviou `aqui` |

  A continuação sozinha não leva o pet ao banheiro: no meio da ida ele quase sempre come a fruta à vista. O P1 também passou a escolher o
  banheiro menos (12 alívios com esse alvo antes, 2 idas agora).

## V2, METABOLISMO, etapas 0 e 1 — o combustível e a reserva por baixo do cansaço (2026-10-11, `docs/TAREFA_V2_METABOLISMO.md`) — GATES PASSAM

As ME-1 a ME-7 pela recomendação (decisão do Matheus, 2026-10-11). Infraestrutura, sem run; só as sementes dos testes. Mudaram
`digilab/corpo.py`, `digilab/corpo_grafo.py`, a `ConfigCorpo` (a sub-chave e os números no fim), uma linha de `digilab/motor_corpo.py`, o
exportador e o gabarito da paridade do corpo e o espelho dos números em `web/app/motor/constantes.ts`. `engine.py`, o `AcaoPet`, o mundo, os
cérebros (sem receptor novo, ME-2) e a bancada não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Etapa 0, num commit próprio, antes de mudar o código:** `tests/gabarito_metabolismo.py` → `tests/gabaritos/metabolismo_vidas_de_hoje.json`,
  176 vidas: o bloco do corpo pela bancada (P0-q, P1-q, P0-c, P1-c, P1-c-tapa e P1-cw nos mundos `padrao`, `bola` e `iguais_frutas`), o
  `fisico` (o P1-quimica e o 2 × 2 do banheiro) e as vidas diretas da etapa 6 do gabarito do banheiro.
- **A sub-chave:** `ConfigCorpo.metabolismo` (exige a `digestao`; `CONFIG_CORPO_METABOLISMO` = a etapa 6 com ela). Desligada, a vida de hoje.
- **Os químicos** `combustivel` (C/2 ao nascer) e `reserva` (C/4), concentrações com teto C, **sem receptor**:
  - **a conversão:** a reação `digestao` produz combustível, `conversao_num/conversao_den` (1/1) do que digeriu, com o resto guardado como
    a vontade; o que passa do teto é descartado e contado;
  - **o gasto basal:** 375 por tick acordado e 187 dormindo (fase 1);
  - **as atividades:** o brincar do pet e o do dono, o explorar e o andar tiram do combustível o mesmo número que somam ao cansaço (ME-3);
    o cansaço de hoje não muda;
  - **o armazenamento** (acima de 3C/4) **e a mobilização** (abaixo de C/2), até 375 por tick: transferências 1 por 1, depois da fase 1 e
    antes da fase 2;
  - **a falta:** abaixo de C/4 o cansaço sobe 500 por tick (fase 2). É a única ponte para o pet (ME-1).
  - A fome não lê o combustível (ME-5); o excedente do estômago segue descartado (ME-4).
  - `Corpo.contas_metabolismo` guarda o que entrou e saiu, em totais.
- **O grafo:** a `Reacao` ganhou `fracoes` (a produção com fração e resto, a vontade e o combustível), e a reação com limiar (`le`, `lado`,
  `limiar`: uma transferência 1 por 1). O gatilho novo `abaixo` é o espelho do `acima`. Duas checagens a mais, que só mordem nas
  transferências:
  - **2b:** todo químico que elas tocam chega a um sumidouro de verdade (nem o teto nem outra transferência);
  - **3b:** o que elas consomem tem fonte, e o teto não desculpa.
  - As transferências entram no laço de ganho com o sentido do lado; as duas retroalimentações do metabolismo são negativas e não
    viram aresta.
- **O motor:** uma linha. A conferência do estímulo do dono passou a ignorar o combustível, que não é drive.
- **A web:** só o espelho dos números na `ConfigCorpo` de `constantes.ts`. O `configCorpo` do TS falha alto com `metabolismo`: a química em
  TS é a etapa 4 (do A). O gabarito da paridade ganhou a seção `metabolismo` (as reações inteiras, uma grade com os limiares, a conversão 2/3 e
  uma sequência longa); as seções de antes saem idênticas.
- **Gates** (`tests/test_metabolismo.py`, 45):
  - **G2:** as 176 vidas da etapa 0 byte a byte;
  - **G-GRAFO:** as checagens em 7 combinações × com e sem o mundo, sem laço novo; o combustível sem gasto e a reserva sem armazenamento
    falham alto;
  - **G-MEC-M:** as contas exatas: a conversão com o resto e o teto, o basal, cada atividade igual ao cansaço dela, as transferências nos
    limiares, a falta só abaixo de C/4;
  - **G-HOJE-M:** com o corpo cheio, em vidas de 2 dias (o combustível acima de C/4, conferido), todo químico de antes é o de sem o
    metabolismo, tick a tick, nos três mundos e no físico, com o instinto e o P1; com os números PROPOSTOS a falta dispara, e até o tick
    dela tudo é igual, e nele só o cansaço sobe 500;
  - **G-CONS-M:** a contabilidade fecha a cada tick, nas vidas e numa sequência longa com a conversão 2/3 e o teto;
  - **G-RECEPTOR-M:** pela AST, nenhum cérebro, a rede de si, os instintos e o motor leem os químicos novos; o espião vê a mesma
    `PercepcaoCorpo`; o `n_pesos` é o de sem ele (998 com o banheiro); só a falta é emissor novo do cansaço;
  - **G1:** o replay refaz o combustível, a reserva e as contas.
- **Achado (descritivo, sementes dos testes):** com os números PROPOSTOS, em vidas de 3 dias, a falta fica ligada em 18% a 58% dos ticks.
  As atividades gastam ~240 por tick, e a conversão não as cobre. É o que o passo 0 da calibração (ME-7) escala.
- **Para o D (etapa 2):** o metabolismo nos regimes do bloco do corpo (ME-6). O `SUBCHAVES_CORPO` da bancada ainda não tem a `metabolismo`:
  hoje a chave `"corpo"` da config a ligaria em todo braço com corpo, o G-HOJE do plano inclusive.

## V2, BN-8 — o banheiro perto de onde o pet passa o dia (2026-10-11, decisão do Matheus) — GATES PASSAM

Pedido do Gerente depois da fumaça do #270 (0 alívios dentro). Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram o
padrão da área na `ConfigBanheiro`, o registro `PARAMETROS_BANHEIRO`, a `docs/TAREFA_V2_BANHEIRO.md` (seções 3 e 10) e os testes. O motor,
o instinto, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A área (PROPOSTA, SEM FONTE):** células x 8 a 12, y 18 a 20, dentro da casa.
  - O ponto do banheiro mais perto do comedouro (10, 15), onde o pet passa o dia, fica a 40 subunidades: ao alcance de uma decisão (60).
  - A área não cobre o comedouro nem o ninho.
  - A de antes (#265) era x 0 a 3, y 0 a 5, no canto da casa.
  - A ida que continua (#270) fica; o contrato de decisão e o teto de pesos não mudam.
- **Os testes e gabaritos de antes** usam a área de antes, dada explicitamente: `CB_CANTO`, e `canto()` para a bancada. São eles os
  testes de mecanismo do #265 e do #270 e os gabaritos do banheiro ligado e do metabolismo.
- **Gates** (`tests/test_banheiro_perto.py`):
  - **G2:** a chave desligada é a vida de hoje (os gabaritos de sempre, na suíte). Com o banheiro ligado, as vidas de
    `tests/gabaritos/banheiro_perto_antes.json` (32 casos, gravados antes com a main 8cdb70f, `tests/gabarito_banheiro_perto.py`) saem
    iguais byte a byte com a área de antes dada explicitamente: só a área mudou;
  - **a geometria:** a área dentro da casa, a 40 do comedouro (alcance 60), fora do comedouro e do ninho (a zona deles não é a do
    banheiro);
  - **o motor:** o pet no comedouro que escolhe o banheiro chega e alivia dentro na mesma decisão, sem ida pendente.
- **Fumaça descritiva** (P0 e P1, sementes 101…505, 7 dias, atencioso no comedouro, com o carinho; antes = main, depois = o branch):

  | braço | alívios | dentro, antes → depois | carinhos | recolhidos pelo limpador | distância mediana ao banheiro |
  |---|---|---|---|---|---|
  | P0 (instinto) | 37 → 35 | 0 → 5 | 0 → 5 | 0 → 5 | 185 → 40–45 |
  | P1 (lobos, T3) | 36 → 39 | 0 → 8 | 0 → 8 | 0 → 8 | 308 → 130 |

  Há um carinho por alívio dentro, e o limpador recolhe todos.

## V2, W-BANCADA-METABOLISMO — a rota do humor no grupo, o metabolismo no bloco do corpo e o passo 0 montado (2026-10-11, `docs/TAREFA_V2_METABOLISMO.md`, etapa 2) — GATES PASSAM

Com o #269 (a rota do canal do humor no mundo físico, do B) e o #271 (o metabolismo no corpo, do B) na `main`. Infraestrutura, sem run;
só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, `digilab/metrics.py` (duas medidas no fim), a config nova
`experiments/configs/v2_corpo/calibracao_passo0.json` e alguns testes antigos (abaixo). `engine.py`, `corpo.py`, `lobos.py`, o mundo e a
web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O nó `canais_fruta_mundo` saiu.** O cérebro do grupo (`Bancada.bancada_grupo`) liga `ConfigLobos.presenca_fruta_mundo` em todo
  braço, ao lado do alvo aprendido, das entradas sociais e do modelo dos outros. A run do plano dos dois pets valida com a montagem
  completa (sem ela, segue falhando alto), e o A só da semente 505, que falhava alto, passa.
- **O metabolismo no bloco do corpo (A3.1, ME-6):**
  - `Braco.metabolismo` está ligado no P0-q, P1-q, P0-c, P1-c, P0-c-tapa, P1-c-tapa, P1-c-tapaX, P1-c-frutas e P1-cw; os acoplados
    herdam pelo braço de destino;
  - o G-HOJE e o banheiro ficam sem ele; fora do regime "química" ou "corpo", falha alto;
  - a chave `corpo` da config e a `cfg_corpo` da bancada não o ligam (`SUBCHAVES_CORPO`);
  - `Bancada(metabolismo=False)`, fora da config, refaz as vidas de antes (os gabaritos do G2 do metabolismo e da rede de si).
- **A medida (A3.3, bloco `corpo.metabolismo` do `medidas.json`):** uma sonda só de leitura no `passo` do corpo, no replay de medição
  (`sondar_metabolismo`), e `metrics.metabolismo_da_vida`: a fração do tempo acordado com a falta, os disparos, e o combustível e a
  reserva no fim de cada dia. Saem também `metrics.tempo_comer_brincar` e as contas do corpo.
- **O passo 0 (A3.2, ME-7), montado sem rodar:**
  - a config: o P0-q, as 20 unidades (bases 33101…33505, K = 4, prefixo `corpo`) e as 8 células (4 donos × `bola` e `padrao`);
  - `pontos_passo0` monta os três pontos do basal (188/94, 375/187, 750/374);
  - `fracao_falta_passo0` junta as 8 células, e `escolha_passo0` aplica a regra (a faixa [0,05; 0,30], o mais perto de 1, o empate no
    menor gasto, "não fechou");
  - **trava no nó `gasto_atividades`**: a `ConfigCorpo` não tem o fator do gasto das atividades sobre o combustível (é do B).
- **Testes:**
  - `tests/test_bancada_metabolismo.py` (35);
  - `tests/test_bancada_dois_pets.py`: os canais rodam no grupo, e o A só 505 passa;
  - `tests/test_canal_fruta_mundo.py`: a falha antiga com o cérebro do grupo de antes;
  - `tests/test_bancada_liga_gestos.py`: o `NOS_PENDENTES` e, com a bancada de sempre, o G-P0C e os acoplados P1-q^ac e P1-c^ac com o
    metabolismo.
  - `tests/test_faixas_r17.py`: a faixa de calibração do corpo pode estar nas configs do próprio plano.

## V2, GASTO-ATIVIDADES — o fator do gasto das atividades sobre o combustível (2026-10-12, `docs/TAREFA_V2_METABOLISMO.md`, ME-3 e ME-7) — GATES PASSAM

Destrava o nó `gasto_atividades` do #273: o passo 0 da calibração do corpo escala o gasto basal **e o das atividades** (A3.2). Infraestrutura,
sem run; só as sementes dos testes. Mudaram `digilab/corpo.py`, a `ConfigCorpo`, o exportador e o gabarito da paridade do corpo e o espelho
em `web/app/motor/constantes.ts`. `engine.py`, o motor, os cérebros e a bancada não (a fiação é do D). Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **O fator:** `ConfigCorpo.gasto_atividades_num/gasto_atividades_den` (PROPOSTOS; padrão 1/1, o mesmo número do cansaço, ME-3). O
  brincar do pet e o do dono, o explorar e o andar tiram do combustível `div_arred(o que somam ao cansaço × num, den)`
  (`corpo.gasto_da_atividade`). O cansaço nunca muda. O andar arredonda uma vez por decisão, sobre o andar inteiro. Um fator que zera o
  gasto falha alto.
- **Etapa 0, num commit próprio, antes do fator:** `tests/gabarito_metabolismo_ligado.py` → `tests/gabaritos/metabolismo_ligado_vidas_de_hoje.json`,
  104 vidas com o metabolismo ligado: o bloco do corpo pela bancada (P0-q, P1-q, P0-c, P1-c, P1-c-tapa e P1-cw nos mundos `padrao`, `bola`
  e `iguais_frutas`) e, direto, a etapa 6 com o metabolismo nos quatro mundos (o físico tem o andar), com o corpo inteiro (q, resto e
  contas).
- **Gates** (`tests/test_gasto_atividades.py`, 36):
  - **G2:** com o fator no padrão, as 104 vidas saem byte a byte; desligado, o gabarito da etapa 0 do metabolismo (no teste dele);
  - **a conta exata:** cada atividade × {½, 1, 2}, o arredondamento do andar (37 × 75 × ½ = 1388) e as falhas altas;
  - **o grafo:** as quatro checagens (e a 2b e a 3b) passam com ½ e 2, com o mesmo relato do padrão, em 3 combinações × com e sem o mundo;
  - **G-HOJE-M com o fator:** até a falta, só o combustível muda; a contabilidade fecha;
  - **G1:** o replay refaz o corpo com o fator, no padrão e no físico.
- **A web:** só o espelho dos dois números. O gabarito da paridade ganhou a seção `metabolismo_gasto` (as taxas e a grade com ½ e 2); as
  outras saem idênticas.
- **Para o D:** a fiação no `pontos_passo0` é pôr o fator na chave `"corpo"` junto do basal (os mesmos num/den), e tirar o nó.

## V2, W-BANCADA-PASSO0 — o fator das atividades no passo 0 e a grade da PCD-9 (2026-10-12, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, A3.2b) — PRONTO, NÃO RODADO

Com o #274 (a grade da PCD-9, do C) e o #275 (o fator do gasto das atividades na `ConfigCorpo`, do B) na `main`. Infraestrutura, sem run
da calibração; só a fumaça nas sementes dos testes. Mudaram `experiments/bancada_v2.py`, a config do passo 0, a fumaça nova e dois testes.
`engine.py`, o corpo, os cérebros e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O nó `gasto_atividades` e a segunda trava saíram:** o `NOS_PENDENTES` ficou vazio.
- **A grade (PCD-9):** um `m_gasto` em {¼, ½, 1}, o mesmo no basal (94/47, 188/94, 375/187) e no fator das atividades
  (`gasto_atividades_num/den`). O cansaço não muda. `pontos_passo0` dá as três configs pela chave `corpo` e falha alto se a config já
  trouxer um dos quatro campos.
- **O orquestrador:** `python experiments/bancada_v2.py --passo0 --config experiments/configs/v2_corpo/calibracao_passo0.json --saida <pasta>`
  (`rodar_passo0`). Ele roda cada ponto pela `rodar` de sempre em `<pasta>/gasto_<num>_<den>/`, junta a fração das 8 células e aplica
  a regra; o resultado vai para `<pasta>/passo0.json`. A calibração tem 20 unidades × 8 células × 3 pontos = 480 vidas e é disparada
  pelo coordenador depois do merge.
- **A fumaça** (`experiments/configs/v2_corpo/fumaca_passo0.json`, NÃO canônica: sementes 101 e 202, 2 dias, 48 vidas em ~19 s; sem artefato).
- **Testes:** `tests/test_bancada_metabolismo.py` (a grade, o m_gasto no corpo da vida, a regra na grade nova, o passo 0 inteiro numa
  fumaça pequena); o `NOS_PENDENTES` vazio em `tests/test_bancada_liga_gestos.py`.

## V2, MUNDO-CALIBRACAO — a calibração do mundo físico (2026-10-12, `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seção 6, A1.4 e A1.9) — m = 1, N = 40

Autorizada pelo Matheus em 2026-10-12. Uma run nas bases 31101…31505 (K = 4, prefixo `mundo`, 20 unidades), 30 min com 8 processos.
Números de `artifacts_v2_mundo/calibracao/` (as vidas ficam fora do git); relatório `docs/RESULTADO_V2_CALIBRACAO_MUNDO.md`.
Interpretações em `docs/REGISTRO_DESVIOS.md`. **A validação (32101…32505) não rodou: precisa de outro sim.**
- **Código:**
  - `experiments/run_v2_calibracao_mundo.py`: a grade (P0 e P0z em `m` ∈ {½, 1, 2}), a regra do menor `m`, o piloto (P1, P0^ac e
    P1^ac), o `Δ_MF`, o K pelo poder simulado e o custo. Toda vida tem o replay do disco conferido. O `meta.json` traz os sha256. A run
    recusa uma pasta existente e as sementes da validação;
  - as configs `experiments/configs/v2_mundo/calibracao.json` e `fumaca_calibracao.json` (a mesma, nas sementes dos testes);
  - na bancada, a dominância só põe o humor (E2) na decisão de comer (`comeu_fruta_e2`). No mundo físico o motor avisa `fruta_comida`
    também no explorar, e a conferência com os canais falhava alto (achado da fumaça);
  - testes: `tests/test_calibracao_mundo.py` (10).
- **O mundo: `m` = 1.** A premissa P0z − P0 em `D_FE`:
  - em ½, −0,00006 [−0,0085; +0,0087]: não passa;
  - em 1, **+0,0154 [+0,0093; +0,0209]**;
  - em 2, +0,0196 [+0,0127; +0,0264].
- **`Δ_MF` = 0,00768. K = 8 por base (N = 40),** com poder de 0,802 no G-MF1r. No relato:
  - o G-MF2r tem poder de 0,92 a 0,99;
  - o G-MF3r, na privação, fica subpotenciado (0,03 a 0,11).
- **Custo:** 3,9 a 7,9 s de CPU por vida.
  - A validação com K = 8: 4,3 h de CPU, ou 6,3 h com o layout afastado;
  - com 8 processos, ~0,8 h de parede.
- **O piloto não é evidência sobre o P1.** P0 − P1 em `D_FE` deu −0,012 [−0,020; −0,005].
- **Achado:** o desempate do cheiro do #232 não está no motor. A calibração rodou com a ordem fixa.

## V2, TETO-POR-PLANO — o teto de pesos do cérebro A por plano (2026-10-13, `docs/DECISAO_V2_TETO_PESOS.md`, TP-1 e TP-2) — GATES PASSAM

TP-1 e TP-2 foram decididas pelo Matheus em 2026-10-12, pela recomendação. Infraestrutura, sem run; só as sementes dos testes. Mudaram a
`ConfigLobos` (a checagem) e o `LIMITE_TETO_PESOS_PLANO` no `config.py`, o registro do `maximo_pesos` em `lobos.py`, a bancada, a receita e o
status da decisão. `engine.py`, a conta dos pesos, os cérebros B e C, a rede de si e a web não mudaram. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **O padrão fica 1000** (`ConfigLobos.maximo_pesos`). A `ConfigLobos` recusa um teto que não seja inteiro de 1 a
  `LIMITE_TETO_PESOS_PLANO` (2000, DECIDIDO pela TP-2, SEM FONTE). A contagem e a falha alta do cérebro (n ≥ teto) não mudaram.
- **O plano declara** na config da bancada (a de vidas e a do grupo):
  - a forma é `"teto_pesos": {"maximo": N, "pesos": n}`, com N acima de 1000 e até 2000, e n de 1000 a N − 1 (um cérebro que cabe no
    padrão não precisa de teto próprio);
  - a config precisa do campo `plano`, com o arquivo que diz por quê;
  - **o teto só entra por aí:** `"lobos": {"maximo_pesos": ...}` falha alto (`validar_teto_pesos`, chamada pelas duas validações e pelo
    `bancada_da_config`).
- **A run confere os pesos declarados** antes de qualquer vida (`conferir_teto_pesos`): n tem de ser o maior cérebro A dos braços da
  config, montado pela bancada (no grupo, os pets de cada braço). Se não for, a run falha alto. O teto conferido vai ao `meta.json`
  (`teto_pesos`).
- **G2:** sem nada declarado, a bancada é a de hoje. Isso vale para a `ConfigLobos` de toda config de `experiments/configs/`, para o
  `meta.json` sem a chave nova e para os gabaritos de sempre, na suíte.
- **O que falta para o primeiro plano acima de 1000:** a medida do custo do replay com o cérebro maior (a TP-2 pede no PR que o fizer).
  Os cérebros B e C seguem com 1000.
- **Testes** (`tests/test_teto_por_plano.py`, 9):
  - o limite;
  - os cérebros de 1116 e 1277, que falham no padrão e nascem com o teto do plano;
  - o teto não muda nada abaixo de 1000;
  - o G2;
  - as recusas;
  - a conferência dos pesos, também na run de vidas e na do grupo.

## V2, DOIS-PETS-CALIBRACAO — a config e o orquestrador da calibração do K e do piloto (2026-10-12, `docs/PLANO_ANALISE_V2_DOIS_PETS.md`, seções 5, 6, 8 e 11) — PRONTO, NÃO RODADO

Aprovado pelo Matheus em 2026-10-12, para rodar **depois** que a validação do mundo físico passar; quem dispara é o Gerente. Só fumaça nas
sementes dos testes. Mudaram `experiments/run_v2_calibracao_dois_pets.py` (novo), as configs `experiments/configs/v2_dois_pets/calibracao.json`
e `fumaca_calibracao.json`, duas funções no fim de `digilab/metrics.py`, o `.gitignore` e a exceção da faixa de calibração em
`tests/test_bancada_banheiro.py`. `engine.py`, a bancada, o grupo, o mundo, os cérebros e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A run** (`python experiments/run_v2_calibracao_dois_pets.py --config experiments/configs/v2_dois_pets/calibracao.json --processos 6`
  → `artifacts_v2_dois_pets/calibracao/`; recusa a pasta que existe, as bases da validação 40101…40505 e qualquer faixa fora do plano):
  - **K:** o A-so (o A informativo sozinho, P1), 10 dias, nas 20 unidades (bases 39101…39505, K_u = 4, prefixo `dois_pets`). A regra
    G-K pega o menor K de {3, 5, 7} com o limite superior do IC95 de R_A no dia K abaixo de metade da R_A do dia 1 → `k.json`. Se nenhum
    K passa, a run para sem piloto;
  - **piloto:** os quatro braços no K escolhido, com o B vivendo 14 dias. A run confere que o A do B + Ainf até o dia K é o A-so da mesma
    unidade, e falha alto se não for → `piloto/`;
  - **margem e N:** `Δ_S`; a validação não roda se a distância ficar ≤ 0,05. O K_u de 4 a 10 sai pelo poder simulado no G-SOCIAL (a
    conta do A1.4 do mundo); o poder do G-COMPANHIA e do G-INGENUO sai só como relato; o custo → `resultado.json`.
- **A config:**
  - o cérebro A no ponto da K2 (T3, `g` S/2, `w0_pedido` S/4, `w0_info` S/4, ganho 4, canais), com a montagem completa;
  - o que a bancada do grupo liga (o alvo aprendido, as entradas sociais, o modelo dos outros e a rota do humor);
  - o `m` da calibração do mundo (1,0);
  - um teste confere a config contra os dois artefatos.
  - **Fora do plano, a decidir:** `taxa.modo` (a agregação da R entre unidades), `taxa.n_minimo` (o consumo mínimo nas janelas da regra)
    e `calibracao_k.janelas` (a letra, ou `dois_dias` só com o adendo).
- **`metrics.taxa_agregada` e `bootstrap_taxa_agregada`:** a R de um grupo de unidades por razão das somas ou média das unidades; a unidade
  sem consumo não tem taxa. O IC reamostra as unidades; com reamostra sem consumo, o IC sai None com a contagem.
- **O teto:** o degrau 1 tem 990 pesos em todo pet de todo braço (teto 1000). Os canais estão só nos P1, e a memória não existe no mundo
  físico.
- **Achado da fumaça (só a contagem, sementes dos testes):** o A sozinho come de 0 a 9 frutas maduras por dia (no dia 1, 1 em 5
  unidades). Na letra da seção 5, a regra para por "exposição baixa".
- **Testes:** `tests/test_calibracao_dois_pets.py`, 16, ~25 s: a config, as recusas, o teto, a taxa agregada, a regra, a margem e o
  contraste em dados com a resposta conhecida, a fumaça inteira e o piloto num K da grade (a rota do humor credita a fruta ruim no A com
  os canais).

## V2, CORPO-CALIBRACAO — a calibração do corpo (2026-10-12/13, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, seções 6 e 7, adendos 3 e 4) — PONTO E N CONGELADOS; DUAS FAIXAS NÃO FECHARAM

Autorizada pelo Matheus em 2026-10-12. Sementes 33101…33505 (K = 4, prefixo `corpo`, 20 unidades). Números de
`artifacts_v2_corpo/calibracao/` (as vidas ficam fora do git); relatório `docs/RESULTADO_V2_CALIBRACAO_CORPO.md`. Interpretações em
`docs/REGISTRO_DESVIOS.md`. **A validação (34101…34505) não rodou: precisa de outro sim.**
- **Código:**
  - `experiments/run_v2_calibracao_corpo.py`: a grade da 6.1 (só o P0-c), a regra da 6.2 (a faixa, o mais perto de (1, 1), o `w_novos`),
    o piloto da 6.3 (os blocos G-HOJE, corpo com os acoplados, tapa, G e P1-cw: 120 por unidade), as sensibilidades da 6.4 e da A1.2, as
    margens e o N da seção 7 (os efeitos pelo `poder_simulado`; a não inferioridade e a equivalência com os contrastes juntos) e o custo.
    Recusa a pasta existente e as sementes da validação; o corpo da config tem de ser o do passo 0;
  - na bancada: o bloco `comportamento` em toda vida (a `BE` e o cuidado, também no "hoje"), as parcelas dos drives novos por decisão de
    tempo livre (`novos_livres`, para o `w_novos`) e os efeitos do tapa da 5.4 (`metrics.efeitos_do_tapa`, bloco `corpo.tapa`); o
    `meta.json` ganhou o sha256 do `corpo.py` e do `motor_corpo.py`, e o passo 0 recusa a pasta existente;
  - configs `experiments/configs/v2_corpo/calibracao.json` e `fumaca_calibracao.json`; testes `tests/test_calibracao_corpo.py` (9).
- **O passo 0 (A3.2c):** `m_gasto` = ½, **"não fechou"**: a falta de combustível em 0,000 (¼), 0,0004 (½) e 0,49 (1) do tempo acordado.
- **O corpo (A4.1):** (`m_sobe`, `m_reduz`) = (2, 1), **"não fechou"**: a solidão não chega a 0,10 sem o tédio e o estresse passarem do
  teto. `w_novos` = 2 (fechou: mediana da parcela 0,394).
- **Margens (A4.2):** `Δ_BE` 0,2235, `Δ_priv` 0,0295, `Δ_saude` 0,0334, `Δ_TED` 0,1633. **N = 20 (K = 4)**, todo gate com poder ≥ 0,968.
  A validação: 2.400 vidas, 3,6 h de CPU, ~0,6 h com 6 processos (com 12 o pool caiu).
- **O piloto não é evidência:** P1-c − P1-q em `BE`, `bola`, +0,67, com o cuidado igual; o G-P0C vale nas 160 células.

## V2, MUNDO-VALIDACAO — a validação do mundo físico (2026-10-13, `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seções 7 e 8, A1.2–A1.9) — G-MUNDO PASSA; O P1 PERDE (resultado negativo registrado)

Autorizada pelo Matheus em 2026-10-12. Uma run nas bases 32101…32505 (K = 8, N = 40, prefixo `mundo`), `m` = 1 e `Δ_MF` da A1.9, o
mundo da calibração; 3.360 vidas rejogadas do disco, 50 min com 8 processos (6,5 h de CPU). Números de `artifacts_v2_mundo/validacao/`
(as vidas fora do git); relatório `docs/RESULTADO_V2_VALIDACAO_MUNDO.md`. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Código:** `experiments/run_v2_validacao_mundo.py`, com:
  - por unidade, as 84 vidas: P0, P0z e P1; os acoplados P0^ac e P1^ac ao P0z; e o P0 e o P1 no layout afastado;
  - os gates G-MUNDO e G-MF1r (as categorias da seção 8);
  - o Holm dos cinco secundários, com o p do bootstrap orientado;
  - a leitura da A1.5 e os descritivos;
  - a recusa de rodar de novo e a config presa à calibração.
  - Configs `experiments/configs/v2_mundo/{validacao,fumaca_validacao}.json`; testes `tests/test_validacao_mundo.py` (17).
- **G-MUNDO passa:** P0z − P0 em `D_FE` +0,0105 [+0,0048; +0,0159].
- **G-MF1r: o P1 perde.** P0 − P1 em `D_FE` −0,0097 [−0,0149; −0,0046]: o P1 sustenta fome e energia pior que o instinto.
- **G-MF2r não passa** (−0,0088 [−0,0123; −0,0051]): a perda aparece com o cuidado fixo, então é do pet. G-MF3r e G-OPORT não passam.
- **G-PERM e G-DIST passam no Holm** (sem Δ nem poder): o P1 fica mais nas manchas (352 contra 191 min), mais com o custo de viagem e
  mais no layout afastado, mas ficar não paga.
- **Leitura (A1.5, terceira linha):** a consequência imediata não aprende a procurar neste mundo. Por dono, a perda vem do atencioso e do
  incoerente; com o relapso o P1 ganha um pouco (descritivo).

## V2, DOIS-PETS-CALIBRACAO, a run — o K não fecha (2026-10-13, `docs/PLANO_ANALISE_V2_DOIS_PETS.md`, seção 5 e adendo 1) — O PLANO VOLTA AO MATHEUS

Decisão do Matheus (2026-10-13): a PDC-1 pela recomendação. O adendo 1.1 (as janelas de dois dias da regra do K) foi commitado antes da
run (`24f0b6d`), e a calibração rodou uma vez. Números de `artifacts_v2_dois_pets/calibracao/` (`k.json`, `resultado.json`,
`k/medidas.json`, `meta.json`; os registros dos grupos ficam fora do git, regeneráveis). Eles estão congelados no adendo 1.2 do plano.
- **A run:**
  - 20 grupos A-so (o A informativo sozinho, P1, 10 dias), nas bases 39101…39505 (K_u = 4), cada um gravado e rejogado do disco bit a
    bit;
  - 9 s de parede com 8 processos.
- **G-K:** a R_A dos dias 1 e 2 é 0,485 (33 consumos). Nos dias K − 1 e K, a R_A é 0,358 (K = 3), 0,338 (K = 5) e 0,366 (K = 7). O limite
  superior do IC95 fica entre 0,52 e 0,57, contra o limiar de 0,242. **Nenhum K passa, e não é por exposição:** toda janela tem 53 a 77
  consumos.
- **O plano para (seção 5):** sem piloto, sem `Δ_S`, sem N; a validação não roda. O plano volta ao Matheus.
- **Descritivo:** a R_A da vida toda é 0,343 em 300 consumos, perto de 1/3, a fração de um tipo entre três. Cada A come em média 15
  frutas maduras e 83 rações em 10 dias.

## V2, PET-QUE-PENSA, etapas 0 e 1 — os modelos do mundo, só observando (2026-10-13, `docs/TAREFA_V2_PET_QUE_PENSA.md`) — GATES PASSAM

J5, com PP-1 a PP-9 decididas pela recomendação. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/modelo_mundo.py`
(novo) e a `ConfigModeloMundo` no fim de `config.py`. `engine.py`, os cérebros, o corpo, o mundo, a bancada e a web não mudaram.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Etapa 0, num commit próprio, antes do módulo:** `tests/gabarito_pet_que_pensa.py` → `tests/gabaritos/pet_que_pensa_vidas_de_hoje.json`,
  136 vidas:
  - pela bancada, P0, P1 e P3 no regime química e o P0 do instinto do mundo, nos dois layouts, nas montagens simples e completa, com o
    alvo aprendido e a presença da fruta;
  - direto, vidas com o metabolismo (PP-3).
- **`ModeloMundo`** (só inteiros, sem rng; importa só `config` e `events`):
  - **o desfecho:** por tipo (`racao`, `a`, `b`, `c`, `podre`) e receptor, a mudança esperada da leitura ao comer. Aprende nos consumos
    do `comer`, com a energia corrigida pelo andar previsto; o "achou e comeu" só é contado;
  - **o custo de andar:** a mudança da energia por subunidade, vezes S, aprendida nos `comer` com deslocamento percebido;
  - **o mapa:** por árvore do layout e pelo comedouro, a frequência do tipo maduro visto a até 2 células. Um lugar só entra depois de o
    pet vê-lo (o raio da visão), e a fruta de cada árvore no layout nunca é lida;
  - os números são PROPOSTOS (PP-6): `passo_desfecho` S/4, `passo_mapa` S/8, `raio_ancora_celulas` 2, `teto_modelo` 200; registro
    `modelo_mundo.PARAMETROS_MODELO_MUNDO`;
  - **76 inteiros** no regime química (5 tipos × 5 receptores + 1 + 10 lugares × 5 tipos); 101 com os drives novos.
- **`PoliticaComModelo`:** o embrulho somente leitura. Entrega aos modelos a observação de cada decisão e a consequência do mundo, e
  repassa o resto ao cérebro. O estado interno é o do cérebro; os modelos ficam em `modelo` (`para_dict`).
- **Gates** (`tests/test_modelo_mundo.py`, 196, ~1 min):
  - **G-INT** (AST) e o módulo só importa `config` e `events`; as contas inteiras são as de sempre (`isqrt`, `div_arred`);
  - **G-TETO-MODELO:** 76, e o teto falha alto;
  - **G-RECEPTOR-MM:** o Estado, o relógio do cuidado, a informação do dono, o resto do `ocorrido` e a fruta do layout não mudam os
    modelos; um químico sem receptor não muda a percepção;
  - **a conta exata** de um passo do mapa (e da âncora), do andar e do desfecho, a podre, o "achou e comeu" e o `comer` sem comida;
  - **G-OBS-MM:** as 104 vidas com corpo da etapa 0 saem byte a byte com os modelos observando; sem o corpo (as 32 do P0 do instinto da bancada), falha alto, e essas saem iguais ao gabarito;
  - **G1:** o replay da bancada refaz os modelos bit a bit.
- **Fica para depois:** o planejador e o lobo `planejamento` (etapa 2), as classes por árvore (2b), a troca de tipo e a fruta na mão
  (etapa 3, A), a bancada (etapa 4, D).

## V2, PET-QUE-PENSA, etapas 3 e 2b — o mundo do J5 e as classes por árvore (2026-10-13, `docs/TAREFA_V2_PET_QUE_PENSA.md`) — GATES PASSAM

A etapa 3 (o mundo, do A) e a 2b (as classes por árvore no alvo aprendido, dada ao A pelo Gerente), com PP-1, PP-2 e PP-5 do
`docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/events.py` (o fim do enum),
`digilab/mundo.py`, `digilab/motor_corpo.py` (o estímulo da mão), `digilab/policies/lobos.py` (atrás da chave), a `ConfigLobos` e a
`ConfigPetQuePensaMundo` no fim de `config.py`. `engine.py`, o `AcaoPet`, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave do mundo:** `MotorMundo(..., cfg_pqp=ConfigPetQuePensaMundo(ligada=True))`, só com o mundo físico e um pet (fora do grupo).
  Desligada, nada muda. Ligada:
  - **os troncos vistos** (`troncos_vistos`: id → o primeiro tick do mundo), a até o raio da visão, na decisão e depois de andar; a
    percepção ganha `troncos` (id, dx, dy, d), com padrão vazio;
  - **os candidatos de árvore lembrada (PP-1):** no explorar, `arvore:<id>` de cada tronco já visto, no tronco, na ordem do layout,
    depois dos de hoje. O padrão do motor e o instinto nunca os escolhem;
  - **a fruta na mão** (`dar_fruta_<f>`, fora do orçamento): o pet come na hora, onde está, com o efeito vigente (a conta da fruta
    madura; com o corpo, o `estimulo_consumo_mundo`), entra em `consumos_mundo` com `como` "mao" e não é contato. O cérebro a recebe só
    pelo gancho opcional `fruta_na_mao(tipo, obs_antes, obs_depois)` (G-SEM-CREDITO). Com o pet dormindo, falha alto;
  - **a troca de tipo** (`trocar_arvores_<x>_<y>`, fora do orçamento): no tick do evento as árvores do x passam a dar y e as do y a dar
    x; as quedas até o tick usam o tipo velho e o chão fica como estava (`Mundo.trocas_tipo`; o replay refaz pelo log).
- **As classes por árvore (PP-2):** `ConfigLobos.alvo_por_arvore` (exige o alvo aprendido): `arvore:J1` … `arvore:M6` nas tabelas do
  explorar, 27 pesos a mais (822 no P1 do plano), w0 = `w0_alvo`, aprendidas só pela consequência. Sem a chave, um candidato de árvore no
  alvo aprendido falha alto.
- **Gates** (`tests/test_pet_que_pensa_mundo.py`, 24):
  - **G2:** as 48 vidas de `tests/gabaritos/pqp_mundo_vidas_de_hoje.json` (`tests/gabarito_pqp_mundo.py`, gravado antes num commit
    próprio), byte a byte;
  - os eventos no fim do enum e as recusas (os motores de hoje, sem a chave, sem o mundo, no grupo, dormindo);
  - os troncos vistos refeitos por fora, a percepção deles e os candidatos de árvore na ordem;
  - o instinto nunca vai à árvore, e o P0 com as classes por árvore é o instinto do mundo byte a byte;
  - **G-SEM-CREDITO e a conta exata da mão**, sem e com o corpo (o estado interno do A inteiro igual, nenhum gancho de crédito, o gancho
    da mão com o corpo, não é contato, o orçamento fecha);
  - a troca no tick, com as quedas antes no tipo velho e depois no novo;
  - as classes por árvore: a contagem, as falhas altas e a conta exata pela consequência (o dono não mexe);
  - **G1** com tudo ligado (o P1, a mão e a troca), sem e com o corpo.
- **Para o D (etapa 4):** a fábrica dos braços do J5 passa `cfg_pqp` ao `MotorMundo` e `alvo_por_arvore` ao cérebro A; os eventos da mão e
  da troca entram pelo `observar` do motor no `T_m` do plano, fora do orçamento. O gancho `fruta_na_mao` é do modelo do desfecho do B.

## V2, MUNDO-ALVO — a validação do mundo com o alvo aprendido (2026-10-13, `docs/PLANO_ANALISE_V2_MUNDO_ALVO.md`) — PREMISSAS PASSAM; O ALVO ATRAPALHA (resultado negativo registrado)

PMA-1 a PMA-9 pela recomendação, autorizado pelo Matheus em 2026-10-13, com o desvio D1 (antes do piloto) e o adendo 1 (antes da validação).
Números de `artifacts_v2_mundo_alvo/{piloto,validacao}/` (as vidas fora do git); relatório `docs/RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md`.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Código:**
  - `experiments/bancada_v2.py`: o braço `P1-alvo` (`Braco.alvo`: o P1 com `ConfigLobos.alvo_aprendido` e o `w0_alvo` padrão, S/16, só no
    mundo físico; 792 pesos contra 756 do P1) e as faixas 47101…47505 (piloto) e 48101…48505 (validação);
  - `digilab/metrics.py`: `uso_do_alvo` (G-USO) e `classes_por_dia`;
  - `experiments/run_v2_mundo_alvo.py`: o piloto (o K pelo poder simulado com o `Δ_MF`, o G-USO e o custo) e a validação (G-MUNDO, G-USO,
    G-ALVO e o Holm de G-ALVO-AC, G-INSTINTO, G-PERM-A e G-DIST-A, a leitura da seção 9, os descritivos); o G-USO sai do `u` que o motivo
    já guarda;
  - **desvio D1** (decisão do Matheus, saída 1 do #292): no `_creditar_canais`, o alvo aprendido conta como leitor da comida. Sem ele, o
    P1-alvo que comia comida podre falhava alto (CANAIS-REFORCO). A linha só tira a falha; nenhuma vida de antes muda;
  - configs `experiments/configs/v2_mundo_alvo/`; testes `tests/test_mundo_alvo.py`.
- **Piloto** (47101…47505, K = 4, 1.440 vidas, 19 min): **K = 4, N = 20**, poder 0,920 no G-ALVO; G-INSTINTO subpotenciado (0,41).
- **Validação** (48101…48505, uma vez, 1.920 vidas, 25 min com 10 processos):
  - **G-MUNDO passa:** P0z − P0 em `D_FE` +0,0143 [+0,0065; +0,0216];
  - **G-USO passa:** 0,0877 [0,0798; 0,0954] das decisões com alvo saem diferentes do prior com o mesmo `u`;
  - **G-ALVO: o alvo atrapalha.** P1 − P1-alvo em `D_FE` −0,0063 [−0,0105; −0,0022];
  - **com o cuidado fixo, nada:** G-ALVO-AC −0,0003 [−0,0047; +0,0042]; a perda é só em malha fechada;
  - G-INSTINTO (P0 − P1-alvo) −0,0137 [−0,0208; −0,0063], não passa; G-PERM-A não passa; **G-DIST-A passa no Holm** (+27 min).
- **Para onde o alvo levou o pet** (descritivo): no comer, o alvo aprendeu a fugir do `cheiro` e da `comida_podre`; o explorar com alvo cai
  de 2.476 decisões no dia 1 para 227 no dia 14. A perda se concentra no dono atencioso e no lugar longe.

## V2, CORPO-CALIBRACAO-FINA — o adendo 5: só o passo 0 fino (2026-10-13, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, A5.1 a A5.7) — m_gasto = 4/5, FECHOU; A GRADE DA SOLIDÃO NÃO RODOU

Decisão do Matheus (2026-10-13): uma grade mais fina antes da validação, pelo adendo 5, registrado num commit antes de qualquer vida. Depois,
outra decisão: faixa que não fecha não bloqueia, e do adendo 5 roda só o passo 0. Relatório em `docs/RESULTADO_V2_CALIBRACAO_CORPO.md`
(seção do adendo 5); interpretações em `docs/REGISTRO_DESVIOS.md`. **A validação (34101…34505) não rodou.**
- **Código:**
  - `bancada_v2`: a grade do passo 0 vem da config (`multiplicadores`, `grade_passo0`) ou da PCD-9;
  - com `passo0_anterior`, a regra lê também os pontos de um passo0.json de antes. Um ponto repetido ou uma config diferente fora do gasto
    falham alto;
  - `--processos` roda os pontos em paralelo;
  - `run_v2_calibracao_corpo`: o eixo `m_sol` (A5.2, chave `m_solidao` da grade). Ele multiplica só a subida da solidão, e a regra fica com
    três eixos (o mais perto de (1, 1, 1); no empate, `m_sobe`, depois `m_sol`, depois `m_reduz`). Sem a chave, a calibração de antes;
  - testes em `tests/test_bancada_metabolismo.py` e `tests/test_calibracao_corpo.py`.
- **O passo 0 fino** (P0-q em {3/5, 7/10, 4/5, 9/10}, 640 vidas, com os três pontos da A3.2c): **`m_gasto` = 4/5, fechou**, com a falta em
  0,202 do tempo acordado (7/10: 0,006; 9/10: 0,368). Números em `artifacts_v2_corpo/calibracao/adendo5/passo0/`.
- **Não rodaram (A5.7):** a grade com o `m_sol`, o piloto, as margens, o N e o custo. A config `calibracao_adendo5.json` está pronta e sem
  saída. Os números do adendo 4 seguem registrados, mas foram medidos com o gasto em ½. A calibração final será com a estrutura completa.

## V2, PET-QUE-PENSA, etapa 2 — o planejador de um alvo e o lobo `planejamento` (2026-10-13, `docs/TAREFA_V2_PET_QUE_PENSA.md`) — GATES PASSAM

PQ-1 a PQ-7 e PP-1 a PP-9 decididas. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás de
`ConfigLobos.g_plano`), `digilab/modelo_mundo.py`, `digilab/motivo.py`, `digilab/expressao.py` e a `ConfigLobos` (`g_plano`, `teto_plano`).
`engine.py`, o mundo, o corpo, a bancada e a web não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O gabarito antes do código** (commit próprio): `tests/gabarito_pet_que_pensa_plano.py` → `tests/gabaritos/pet_que_pensa_plano_vidas_de_hoje.json`,
  36 vidas com o mundo do J5 ligado (a mão e a troca no dia 2), o corpo químico com e sem metabolismo, o instinto, o P0 e o P1 do plano, e
  o P1 no `PoliticaComMotivo` (os motivos e as falas).
- **O lobo `planejamento`** (com `g_plano` > 0; exige o mundo físico, o corpo, o alvo aprendido e o aprendizado):
  - **os modelos:** o cérebro guarda os próprios modelos do mundo (`modelo_mundo`), que aprendem na decisão, na consequência e na mão;
  - **V(k):** `Σ_tipo div_arred(p̂(tipo|k) · valor_tipo, S) + valor(andar até k)`. O valor é o `sinal_corpo` da leitura de agora para a
    prevista (agora + Δ̂, cortada em [0, S]), com o ganho e os drives da consequência; o custo de andar é a mesma conta, na energia;
  - **o termo:** `div_arred(g_plano · V, S)`, cortado em ±`teto_plano` (2 S). No alvo, ele vai em cima do alvo aprendido (o
    representante de cada classe é o de maior V); na decisão de comer ou explorar, com o maior V dos alvos que o pet vê ou lembra;
  - **a sonda "quem decidiu":** o mesmo u sem o termo, na decisão e no alvo (`plano` e `alvo_plano` no motivo);
  - **o fator:** só quando a sonda muda a escolha e há o que nomear: `plano_arvore(J2,b)`, `plano_comida(b)` e `plano_evita(a)`, com
    textos de marcador único;
  - **G-PESOS-A:** 0 pesos a mais (822 no P1 do plano, com e sem o planejador).
- **Os modelos** (`modelo_mundo.py`): os troncos da percepção conferidos contra a conta do raio, o tronco visto depois de andar, a fruta na
  mão (`na_mao`, `consumos_mao`), `congelar("mapa")` e `congelar("desfecho", "mapa")` (PP-8), e as consultas do planejador.
- **`PoliticaComMotivo`** refaz o motivo no `escolher_alvo` com a sonda do alvo, e repassa a `fruta_na_mao`.
- **Gates** (`tests/test_planejador.py`, 50, ~1 min):
  - **G2:** as 36 vidas do gabarito, com os motivos e as falas, byte a byte com `g_plano` 0; os gabaritos de sempre, na suíte;
  - **G-PESOS-A**;
  - **a conta exata** de V(k), do valor de cada tipo, do andar e do termo (com o corte), o termo no peso efetivo da decisão (em toda
    decisão de uma vida) e do alvo;
  - **a sonda** reproduz a escolha sem o termo;
  - **o fator e os textos;**
  - **G1:** o replay refaz o planejador e os motivos bit a bit;
  - os troncos iguais aos `troncos_vistos` do motor, a G-SEM-CREDITO da mão e o congelamento.
- **Descritivo, só nas sementes dos testes:** com `g_plano` S, o plano muda o alvo em 8,6% das decisões com alvo. O |termo| mediano é 0,06
  de peso, contra 6 do impulso da fruta: a regra da calibração (PP-6, [0,10; 0,40]) pode não fechar na grade {S/4, S/2, S}.
- **Fica para depois:** a bancada (etapa 4, D) liga o `g_plano` nos braços do plano, passa a `cfg_consequencia` e congela os modelos no
  `T_m` (`do_braco(...).cerebro.modelo_mundo.congelar(...)`).

## V2, W-BANCADA-PQP — a bancada do pet que pensa, etapa 4 (2026-10-13, `docs/TAREFA_V2_PET_QUE_PENSA.md`, `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`) — GATES PASSAM; O PLANEJADOR ESPERA A ETAPA 2

O que dá para rodar com as etapas 1 (os modelos, #289), 2b e 3 (as classes por árvore e o mundo do J5, #291) na `main`. Infraestrutura, sem
run de pesquisa; só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, `digilab/metrics.py` (quatro medidas no fim), a fumaça
`experiments/configs/v2_pet_que_pensa/fumaca.json`, dois testes antigos e o teste novo. `engine.py`, o mundo, o corpo, os cérebros, os
modelos e a web não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **As faixas (PP-9):** 45101…45505 (calibração do `g_plano` e piloto) e 46101…46505 (validação), com a fonte, em `FAIXAS_RESERVADAS`;
  o prefixo `pet_que_pensa` em `PREFIXOS_UNIDADES`; `BASES_PET_QUE_PENSA`.
- **A unidade (seção 2):**
  - a fruta x e a y saem das rngs próprias, `pet-que-pensa-x` e `pet-que-pensa-y`;
  - antes da mudança a x faz bem e as outras duas são neutras;
  - o mundo é o físico, no layout padrão, com o J5 ligado (`ConfigPetQuePensaMundo`);
  - o corpo é o regime química com o metabolismo (PP-3), com o gasto da chave `corpo`;
  - o dono é o atencioso, só com o cuidado, no comedouro;
  - o cérebro A é o do P1 com o alvo aprendido, a presença da fruta no mundo e as classes por árvore.
- **Os braços** (`BRACOS_PQP`): P1, P1-plan, P1-plan-desfecho (o mapa congela na mudança, PP-8) e P1-plan-cong (os dois congelam).
  - **Os três com o planejador falham alto** com `NOS_PENDENTES["planejador"]` (a etapa 2 do B).
  - Sem o nó, a `BancadaPQP.politica` ainda recusa: o `g_plano` entra nela com o planejador, e um braço com o planejador nunca vira, em
    silêncio, o P1 com os modelos congelados.
- **Os protocolos (seção 3):**
  - **o tick da mudança:** `T_m` é o primeiro passo do dono a partir das 8 h do dia `D_a`, com o pet acordado (`RegraMudancaPQP`, fora do
    orçamento, pelo `simular_vida_fisico(..., mudanca=)`);
  - **o T1:** dá a x na mão `n_mao` vezes;
  - **o T2:** troca o tipo das árvores da x e da y;
  - **a fase 1:** os `D_a` dias, sem mudança (a calibração do `g_plano`);
  - **o motor** (`MotorMundoMudanca`) avisa o cérebro (`mudanca_no_mundo`). No T1, a primeira mão troca antes o efeito da x para "faz mal";
    o replay refaz tudo pelo log.
- **Os modelos** (`PoliticaComModeloPQP`, em todo braço):
  - a mão chega ao modelo do desfecho (os receptores depois menos os de antes) e nunca ao crédito do cérebro;
  - o congelamento da PP-8 restaura as partes congeladas depois de cada passo dos modelos;
  - o estado interno ganha `modelo_mundo`, e o G1 o confere.
- **As medidas** (seção 4; `metrics.oportunidade_revalorizacao`, `busca_transicao`, `exposto_transicao`, `mudanca_de_escolha`), do replay de
  medição conferido contra a vida:
  - a oportunidade do T1, a busca e a exposição do T2, o corte da reexperiência, q e m;
  - os descritivos: os modelos por dia contra o real, o `D_FE` na fase 1 e na janela, o humor da janela e o custo.
  - **Não medidos até o planejador:** quanto o plano decide e a legibilidade. A deriva também fica para o orquestrador.
- **Gates** (`tests/test_bancada_pet_que_pensa.py`, 28, ~25 s):
  - as faixas e o prefixo; a x e a y uniformes, sem tocar o `random` global;
  - os braços e as falhas altas;
  - a regra da mudança e o motor (o efeito troca na primeira mão; a troca de tipo; a fase 1 sem nada; o orçamento sem a mudança);
  - o G1 pelo texto do log;
  - **o G-SEM-CREDITO** (o cérebro inteiro igual antes e depois de cada mão) e a mão no desfecho;
  - **o congelamento:** a vida é a mesma com e sem ele; as partes congeladas ficam como no tick da mudança; o gate falha alto se mudarem;
  - as medidas em dados com a resposta conhecida;
  - as recusas da config;
  - a fumaça inteira pelo `rodar_pqp` e pelo `main`.
- **Fumaça descritiva** (P1, sementes 101, 202 e 303, 7 + 3 dias): com o atencioso a fome quase nunca chega a S/2 antes da mudança, e só a
  semente 303 teve 3 oportunidades antes no T1. A G-OPORTUNIDADE do plano decide isso na calibração.
