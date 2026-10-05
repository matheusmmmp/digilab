# Registro de desvios de pré-condição e de interpretação

## 2026-09-24 — TAREFA_MEMORIA_EXPRESSAO iniciada com a bateria do combate V2 REPROVADA

- Pré-condição da Parte A (`docs/TAREFA_MEMORIA_EXPRESSAO.md`): bateria do combate V2
  **APROVADA** em `artifacts_combate_v2/gates.json`.
- Estado em disco no início da tarefa: `status = REPROVADA`, `falharam = [G4_ritmo,
  G5_sem_acao_morta]` (conjunto de validação; commit `8f61e52` na `main`).
- Decisão do pesquisador (Matheus, em conversa): seguir a tarefa **ignorando a reprovação**,
  mantendo este registro. Nada na bateria nem nos artefatos do combate V2 foi alterado.
- Consequência: a expressão de combate é exercitada sobre um combate que ainda não passou no
  próprio portão (31,3% das partidas no limite de turnos; `esquivar` quase não aparece nas
  decisões dos bots do suporte). Resultados de legibilidade no combate herdam essa limitação.

## 2026-09-24 — interpretações adotadas na Parte A (propostas antes de começar)

- `PoliticaInstinto`: a regra que disparou fica em atributo somente leitura (`ultima_regra`),
  não em `estado_interno()`, para não alterar `artifacts_ablacao/vidas/*.politica.json`.
- Bandit: a decisão é argmax de `log(prior) + valor amostrado + Gumbel`. O fator só é atribuído
  se o termo de valor **mudou** a escolha (sem ele, a ação seria outra); caso contrário o motivo
  fica sem fator, porque quem decidiu foi o prior/ruído e citar um peso seria inventar causa.
  A fração sem essa checagem também é reportada.
- Bandit (registrado depois, 2026-09-25): a A1 pede como fator o termo de maior **|contribuição|**;
  o código só aceita contribuição **positiva** (a favor da ação escolhida), ≥ `limiar_motivo`, até 2.
  Uma contribuição negativa pesou *contra* a ação que saiu; citá-la como causa da escolha seria
  inventar. Documentado no `CLAUDE.md` e em `motivo.py` desde a Parte A, mas faltava aqui.
- `hora_sin` e `hora_cos` somam contribuição num único fator `hora`; o intercepto vira o fator
  `habito` (preferência aprendida pela ação, independente do estado).
- Os docs foram copiados de `D:\Trab\digilab\*.md` para `docs/`, onde a tarefa os referencia.

## 2026-09-24 — combate V2.1 iniciado sem as pré-condições

- Pré-condições de `docs/ESPEC_COMBATE_V21.md`: (1) bateria V2 **base** APROVADA com as
  correções da simulação (finta, parry, fuga condicionada, morte súbita, gates de robustez e
  de espelho); (2) `TAREFA_PERSONALIDADE_OBEDIENCIA` concluída (temperamento e caráter).
- Estado no início: nenhuma das duas existe. A base V2 está REPROVADA (G4, G5; ver acima) e
  não tem finta, parry, fuga condicionada, morte súbita nem fadiga de guarda; não há
  especificação nem código de temperamento/caráter.
- Decisão do pesquisador (Matheus, em conversa): **seguir adaptando e registrando**. A base V2
  não foi alterada (fontes de `digilab/combate_v2/*.py` com o mesmo hash de
  `artifacts_combate_v2/gates.json`; o V2.1 vive em `digilab/combate_v2/v21/`).
- Decisões do pesquisador na mesma conversa: 4 espécies no jogo (brasa, cirro, ferrugem,
  limo), cada forma com sprite próprio; a evolução do jogo web passa a seguir esta árvore.

### Adaptações por falta de mecânica na base

- **duelista** ("finta não custa o guts do pesado e causa 4 extra se o oponente esquivou"):
  não há finta. Vira: pesado contra esquiva causa o dano extra e devolve o guts do preparar.
- **brigão / parry**: não há parry. A resposta declarada "defender (parry)" vira: defender
  contra investida anula o dano **e o avanço** (calibração, rodada 1: só anular o dano não
  punia nada).
- **muralha** ("sem fadiga de guarda"): não há fadiga. Fica só a parte "defender recupera
  +3 guts extra".
- **espelho** ("contra_golpe também devolve 50% do disparo"): contra_golpe só é legal perto e
  disparo só médio/longe, então a passiva nunca valeria. Vira: para o espelho, contra_golpe é
  legal em qualquer distância. O disparo marcado ignora a redução da postura, mas o
  contra_golpe do espelho ainda devolve.
- **investida** ("avança para perto e aplica golpe rápido no mesmo turno"): exceção
  documentada à regra "ataque de perto só acerta perto": acerta em médio e aproxima no
  movimento. "Interrompe preparação" nunca ocorre na prática (preparar exige perto).
- **contra_golpe** ("devolve 50% do dano corpo a corpo recebido"): devolve 50% do dano
  **bruto** (antes da redução da postura); com o dano já reduzido a devolução seria ~1 ponto.

### Interpretações

- `turno_execucao` (condição de adulto; a especificação só dá o nome): "o turno corrente da
  partida é >= t", t em {5, 10, 20}.
- `oponente_vai_preparar` (vigia): verdadeiro se a regra que o oponente dispararia agora (sem
  exploração, sem rng) é preparar_pesado.
- Caráter: sem a tarefa de personalidade, é **entrada** das funções de transição
  (`catalogo.py`). Nos bots da bateria, caráter canônico: eixo da linha +0,5 e eixo
  complementar ±0,25 com o sinal da forma. Temperamento neutro. Ramo da criança "sereno".
- Bebê: não luta no motor Python (a especificação). Na web o bebê continua lutando ao acaso
  (cenário "adulto × bebê" pedido antes), com multiplicador de estágio 0,4.
- E3: a "resposta declarada" é escrita como regras que o oponente põe no topo da própria lista
  quando sabe que enfrenta a técnica (a forma é pública).
- E4: por forma adulta (8 valores), adolescente da mesma linha, espécie e caráter.
- E5: inteiros perturbados por arredondamento; se não mudar, ±1.

### Fora do escopo desta entrega (depende da tarefa de personalidade e da arena V2)

- Seção "Pesquisa" da especificação: arena só com adultos, ovos pareados, forma adulta como
  variável de resultado, ablação com técnicas e passivas desligadas. Não existe arena V2 com
  pets no motor Python; o caráter medido pelo desvio da política também não.
## 2026-09-25 — memória por espaços (ADENDO_MEMORIA_EMOCAO_DF.md, Parte 1)

Interpretações propostas antes de começar e aprovadas pelo pesquisador:

- "Substitui a B1": a memória por espaços entra como **protocolo novo**
  (`arena-v1-memoria-espacos`, política `bandit_espacos`, `digilab/memoria_espacos.py`,
  `ConfigMemoriaEspacos`). A B1 (`arena-v1-memoria`, hash `be9aae5a833c…`) continua existindo e
  reproduzível, para a comparação B1 × espaços.
- Decaimento da ativação entre relembranças: exponencial com a mesma constante da B1
  (`tau_ativacao_ticks` = 360).
- "Relembrar a cada 4 h acordado": tempo acordado acumulado desde a eclosão, medido nas decisões do
  pet (a cada 15 min, com o sono da observação); a cada 240 min acordado todas as memórias ativas
  voltam à intensidade original.
- `demora` junta fome e higiene numa categoria; atendimento imediato (latência 0) não gera memória;
  pedido perdido vale 1 e nasce quando o pet percebe (próximo evento).
- `carinho` = qualquer acariciar ou brincar do dono.
- Comparações de força pela intensidade ORIGINAL; empate: vence a mais recente (e, entre as mais
  fracas empatadas, sai a mais antiga).
- Web: fica para um segundo passo (a Parte 1 foi feita só no Python).
- Parte 2 (emoção, extremos, habituação) não iniciada: depende da `TAREFA_PERSONALIDADE_OBEDIENCIA`.

## 2026-09-25 — TAREFA_PERSONALIDADE_OBEDIENCIA com a bateria V2 REPROVADA

- Pré-condição: bateria do combate V2 APROVADA. Em disco: REPROVADA (G4, G5). Decisão do pesquisador:
  **ignorar** esta pré-condição (como na tarefa de memória). As outras duas estavam cumpridas.
- Decisão do pesquisador: a base é a **memória por espaços** (adendo Dwarf Fortress), não a B1. O
  teste de equivalência (temperamento neutro + obediência desligada) compara com
  `artifacts_v1_memoria_espacos/`, não com `artifacts_v1_memoria/`.

Interpretações propostas antes do código e aceitas:

- Rancor: escala o tau de decaimento das memórias `demora` e `bronca` (2^rancor).
- Temperamento: fatores multiplicativos que valem exatamente 1,0 no eixo 0 (curiosidade: variância
  × 2^c; teimosia: repreensão × (1 − 0,5 t); sensibilidade: elogio × (1 + 0,5 s), repreensão ×
  (1 − 0,5 s)). Temperamento neutro gera configs idênticos e a mesma política.
- Obediência só para ações de cuidado (alimentar, limpar, brincar, acariciar); elogiar e repreender
  sempre chegam. Conflito = (0,3 − nível)/0,3 da necessidade mais urgente abaixo de 0,3 que a ação do
  dono não atende.
- Na desobediência: a função de efeito do dono roda sobre um estado descartado (consome a rng de
  ambiente igual a uma ação aceita: recusar não desalinha o clima); a tentativa conta como contato
  (zera o tempo sem cuidado), senão o relógio do bandit desalinha; `fazer_outra` aplica 1 tick do
  efeito da ação atual do pet.
- Fator do motivo da recusa: contribuição relativa ao pet neutro (vínculo no valor inicial,
  temperamento 0, sem conflito); só o termo mais negativo, se ≤ −0,05. Recusa sem termo assim fica
  sem fator (sorteio contra com p alta).
- Vontade: argmax da média da posterior θ̂·x (sem prior e sem amostra); bandit recém-nascido não tem
  vontade. Necessidade tem prioridade.
- 10 ovos (sementes 101 a 1010), os mesmos nas três variantes.

## 2026-09-25 — Pesquisa do V2.1 (ESPEC_EVOLUCAO_COMBATE.md, seção Pesquisa)

`docs/ESPEC_EVOLUCAO_COMBATE.md` tem o mesmo texto de `ESPEC_COMBATE_V21.md`; a parte que faltava
era a seção Pesquisa. Decisão do pesquisador: fazê-la sem tocar em `engine.py`, no espaço de ações do
dono nem no `CanalDeInteracao`. Interpretações:

- Sem vida nova: a evolução é função pura das 40 vidas de `artifacts_ablacao/vidas` (mesmas
  sementes, orçamento e duração da arena v1).
- Durações dos estágios e chamados do bebê: `cronograma_interacoes.json` ("a pesquisa usa os valores
  acima"): adulto aos 1980 min de uma vida de 14 dias.
- Cuidado do bebê: chamados em horário fixo (fome 30, higiene 60, carinho 45 min), atendidos pela ação
  certa do dono em até 15 min. Os donos simulados da pesquisa agem pelo estado das necessidades e
  **não** mudaram (mudar mudaria a run canônica V1): na prática ninguém atende (cuidado 0, todo pet
  arisco). Resultado, não bug.
- Caráter: desvio da política aprendida contra a **mesma política recém-nascida** nas sondas da
  métrica de divergência (64 estados, 200 amostras, semente 9001), não contra o instinto puro. Contra
  o instinto, o bandit novo já diverge pelo ruído de Thompson ("paciente" −0,8 a −1,0 em todos os
  donos na semente 101), e isso não é aprendizado. Ação → traço por `ConfigArena.mapa_pet_combate`;
  eixo = média dos traços (impetuoso = golpe e carga; paciente = bloqueio; atento = finta; resistente
  = agarrão); escala 0,05, cortado em [−1, 1].
- Temperamento do ovo: cada eixo uniforme em [−1, 1] pela semente (iguais entre braços: ovos pareados).
- Condição física: 0,95 + 0,10 × saúde no fim da vida. Sparring mínimo: dado como cumprido.
- Arena: gambits canônicos da forma adulta (8 regras em todos: capacidade igual); ablação tira a
  técnica, a passiva e as regras que dependem delas.

## 2026-09-25 — campanha contra os 3 NPCs (TAREFA_TREINO_SOMBRIO, seção 5), registrado depois

Registrado na auditoria das tarefas (antes estava só no `CLAUDE.md` e no docstring de `campanha.py`):

- **Pré-condição dispensada**: a tarefa pede o combate V2.1 APROVADO; a campanha foi feita com a
  bateria V2.1 REPROVADA (E1–E5), a pedido do pesquisador, e **sem treino** (a parte com treino espera a
  tarefa de treino). Stats dos NPCs não são renormalizados ao orçamento da espécie.
- **Correção do Soberano não adotada**: a tarefa manda corrigir o chefe porque, no protótipo
  (`docs/pve.py`), o atirador o vencia sem treino (0,67). No V2.1 isso não se repete (atirador 0,06
  contra o original). A correção testada (`GAMBIT_SOBERANO_RESPOSTA_LONGE`) mantém o atirador em 0,06
  e faz emboscador (0,73) e sentinela (0,57) passarem a vencê-lo. Fica o original; números em
  `artifacts_campanha/campanha.json`, chave `soberano`.
- Web (`web/digilab_sprites.html`): a campanha entrou na aba Arena com desbloqueio em sequência; o
  balanceamento continua sem calibrar (a escada 1 → 2 → 3 não se sustenta).

## 2026-09-25 — expressão do temperamento e do desejo (TAREFA_PERSONALIDADE_OBEDIENCIA 1.3 e 3.2)

Faltavam na entrega da tarefa (achado na auditoria). Interpretações:

- Temperamento: tabela `TOM_TEMPERAMENTO` por eixo, polo (+/−) e estágio, com marcador único como os
  fatores. Só entra eixo com |valor| ≥ `ConfigExpressao.limiar_tom_temperamento` (0,5, PROPOSTO), do
  mais forte ao mais fraco; bebê só por emote (sem palavra), criança e adolescente o mais forte, adulto
  até 2. É uma expressão à parte (`expressar_temperamento`), não muda o texto dos motivos: o
  temperamento é inato, não é causa de uma decisão específica. O contraste "nasceu X, virou Y" fica
  para quem lê os dois registros (o caráter aprendido só existe na web e no `evolucao.py`).
- Desejo: `expressar_desejo`. Bebê: um emote só (não distingue tipo). Da criança em diante o marcador
  do tipo aparece (`preciso` × `queria`). Necessidade cita a necessidade que passou do limiar (o único
  fator do cálculo); vontade não cita causa além de "é o que mais deu certo" (média da posterior).
- Somente leitura: nenhum hash, protocolo ou artefato muda (o campo novo está em `ConfigExpressao`, que
  não entra no protocolo).


## 2026-09-25 — temperamento e desejo no jogo web (`web/digilab_sprites.html`)

- O temperamento **age** no bandit da web (mesmos fatores de `ConfigTemperamento`: variância, peso do
  elogio e da repreensão), para a fala "nasci X" não prometer o que o pet não é. Diferenças do Python:
  sorteio pelo rng da web (`hashSemente("temperamento", semente)`), não o mesmo número do
  `rng_ovo`; a web usa a memória curta antiga (não a por espaços), então o rancor só escala o
  decaimento das broncas (a demora não decai na web).
- Pets salvos antes disso passam a ter temperamento: o replay os reconstrói já com ele (o registro
  é o mesmo; o aprendizado muda um pouco).
- Desejo: mesmo cálculo de `desejo.py` (necessidade < 0,3; vontade por margem ≥ 0,1 da média da
  posterior), sem rng, mostrado na aba Estado; não muda nenhuma decisão.

## 2026-09-25 — porte Python → web, versão 2 do pet (`web/digilab_sprites.html`)

- Save ganhou `versao`. Save sem versão = v1 (comportamento anterior, inclusive a memória curta);
  pets novos, rivais de cenário e o pet de exemplo nascem v2. Motivo: obediência e memória por
  espaços mudariam o replay dos pets já salvos.
- v2 espelha `memoria_espacos.py`, `vinculo.py`, a obediência de `obediencia.py` e as métricas de
  desejo de `metrics.py`. Diferenças: referências de vínculo e de memória são o ordinal da ação do dono
  (a web junta avanços de tempo no registro; o índice do evento mudaria entre ao vivo e replay) e a
  tela converte para o índice do registro; `fazer_outra` aplica o efeito da ação atual do pet uma vez
  (a web não tem o intervalo como parâmetro); rng da obediência = `hashSemente("obediencia", semente)`.
- Condição no combate: `perfilDe(forma, caráter, condição)` com condição = 0,95 + 0,10 × saúde **na
  hora da luta** (no Python de pesquisa é a saúde no fim da vida). Só v2.
- Não portado: caráter pelo desvio da política (`evolucao.py`), que mudaria forma e evolução; decisão
  do pesquisador.


## 2026-09-25 — adendo DF, Parte 2 (emoção, extremos, habituação)

Interpretações (tudo PROPOSTO):

- **Emoção somente leitura.** O adendo diz que "a valência multiplica a intensidade da memória" (2.1)
  e também que emoção e extremos "são somente leitura e não podem mudar nada" (2.4, 2.5). As duas não
  cabem juntas: mudar a intensidade muda as features do bandit. Adotado: emoção só leitura; a
  modulação existe atrás de `ConfigEmocao.modula_memoria` (desligada, testada, sem run).
- Emoção por **evento** que gera memória (inclusive o que é descartado dos espaços), guardada em
  `MemoriaEspacos.eventos` (fora de `para_dict`: nenhum artefato antigo muda). Tabela em
  `digilab/emocao.py`: regra vale se polo × eixo > 0,2; vence o eixo de maior módulo; senão a padrão
  da categoria (garante cobertura para toda combinação). A tabela além do exemplo do adendo (demora)
  é proposta minha.
- A fala da emoção cita só a emoção e o evento ("Senti raiva quando você demorou"), sem marcador de
  fator.
- **Extremos**: `ConfigExpressao.limiar_extremo = 0,2` substitui o 0,5 que eu tinha posto no tom do
  temperamento (1.3); vale também para o caráter (`expressar_carater`, adolescente em diante; a
  pesquisa mede o caráter em `evolucao.py`, a arena v1 não).
- **Habituação** (flag `habituacao_ligada`): repetições = eventos da mesma categoria nos últimos 720
  ticks, **antes** do atual; categorias negativas = `demora` e `bronca`; teimosia > 0 acelera a das
  broncas, `H_bronca = 0,8 × (1 − 0,2 × teimosia)`. No bandit reduz a repreensão (`bronca`) e a
  penalidade de pedido ignorado (`demora`), pelo gancho `_peso_recompensa` do `PoliticaBandit` (1,0
  fora da habituação: multiplicar por 1,0 é exato, as runs antigas não mudam — teste).
- Protocolo: o adendo pede os campos dentro do `PROTOCOLO_ARENA_V1_PERSONALIDADE`; isso mudaria o
  hash das runs já gravadas. Criadas duas variantes com os mesmos ovos
  (`arena-v1-personalidade-habituacao` e `-sem-habituacao`) → `artifacts_v1_habituacao/{com,sem}`.
  A "sem" reproduz a personalidade completa byte a byte (teste de uma vida; a run inteira é conferida
  no relatório).
- Web (`digilab_sprites.html`, pets v2): emoção por evento de memória mostrada na aba Aprendizado e
  limiar 0,2 no tom; habituação não entrou na web (no Python ela é desligada por padrão).

## 2026-09-25 — treino no jogo web antes de fechar o Python (pedido do Matheus)

O Matheus pediu o treino na web já ("quero treinar agora"), antes das runs da TAREFA_TREINO_SOMBRIO.
A web espelha o que está no Python até aqui (ConfigTreino com a sobrecarga por forçada calibrada
15 → 25; ConfigSombrio; passivas sombrias). Diferenças da web: fadiga e sobrecarga integradas tick a
tick (o Python integra nas decisões); estágio do treino = estágio da evolução da web (o adulto exige
sparring); pets v1 também treinam, mas sem obediência nem vínculo (os v2 enrolam pela obediência e o
forçar derruba o vínculo); a forma sombria usa o sprite da forma normal de estilo mais próximo com
tinta escura; na arena contra bots os stats treinados são normalizados, na campanha contra NPCs valem
inteiros. Se as runs do Python mudarem números, a web é corrigida depois.

## 2026-09-25 — TAREFA_TREINO_SOMBRIO

Decisões do Matheus (plano aprovado): seguir com a bateria V2.1 REPROVADA (pré-condição); orçamento =
16 de cuidado por dia + sessões-alvo do estágio, igual nos 5 braços; manter o Soberano original (a
correção pedida foi testada e piora, ver a entrada da campanha); arena da pesquisa = V2.1 com stats
normalizados; ações de treino entram no `AcaoUsuario` (os donos da v1 sorteiam só de `ACOES_V1`, a
canônica fica intacta); toque dentro do intervalo mínimo é rejeitado pelo canal sem consumir orçamento.

Interpretações (PROPOSTAS):

- Treino é estado próprio (`treino_stats.py`), integrado nas decisões do pet e antes de cada sessão;
  não toca o `Estado` do motor nem a política (a sessão não é contato de cuidado nem recompensa).
- Estresse só é registrado (o único efeito explícito, −0,05 de vínculo, vem direto do forçar).
- "Fadiga de guarda dobrada" (bastião rachado) não existe no combate: vira "defender não rende guts".
- Sono completo = 6 h ou mais; bem cuidado = fome, higiene e energia ≥ 0,3. Evolução zera fadiga e
  estresse; pontos e sobrecarga ficam.
- Pedido de pausa: fadiga ≥ 40 vira `Desejo` de necessidade (alvo "descansar"). Pausa atendida = acabar
  sem treino (vínculo amostra 1); treinar por cima = amostra 0.
- Donos: sessões em um bloco diário a partir das 10:00, um por passo; atencioso, relapso e incoerente
  respeitam a pausa (carinho no lugar), exercícios em rodízio (o dono não enxerga a linha, que só é
  calculada na evolução); aleatório sorteia o exercício e respeita a pausa com prob. 0,5; exigente
  treina no teto do dia (o extra sai do carinho), ignora a pausa e força em 1 de cada 2 sessões
  possíveis (alternado, sem rng).
- Formas sombrias lutam com os gambits da forma normal de estilo mais próximo (devastador ← furioso,
  bastião ← espelho, predador ← emboscador, colosso partido ← titã); regras com ação proibida pela
  passiva nunca disparam.
- **Calibração** (`experiments/calibrar_treino.py`, ovos 3101…3505, critério fixado antes: exigente
  sombrio em ≥ 60%, nenhum outro braço sombrio, a mais próxima do original): `sobrecarga_forcar`
  15 → 25. Com 15 o exigente nunca chegava a 60: ele só consegue forçar ~2 sessões por estágio antes
  da evolução. A primeira varredura foi inválida (o config não chegava ao motor); corrigido e refeito.
- S1: bateria à parte (`run_bateria_sombria.py`, sementes de validação da V2.1); a bateria canônica
  V2.1 não foi rejogada (as formas normais não mudam de regra; o hash dos fontes V2.1 mudou).
- S2 (bots, treino uniforme 0…36, stats absolutos): "vence o tier 1 mais cedo" = treino mínimo para
  taxa ≥ 0,5 contra o tier 1 menor ou igual ao da normal; "não vence o tier 2 com taxa maior" = taxa
  média contra o tier 2 (na grade) menor ou igual à da normal.

## 2026-09-25 — TAREFA_CORRECAO_COMBATE (Etapas 0–2; Etapa 3 NÃO iniciada)

Resultado: a base **V2C não passou na validação** (`artifacts_combate_v2c/validacao/gates.json`:
G3, G4, G5, G6b, G9 falham). A Etapa 3 (V21C) exige a V2C aprovada: não foi iniciada.

Interpretações e desvios:

- `docs/sim_combate_v2/` (protótipo citado na Etapa 1) não existe no repositório nem em `D:\Trab\digilab`.
- **Nome da condição do C1**: a tarefa pede `turno_execucao`, mas a V2.1 já tem uma condição com esse
  nome e outro sentido (turno da luta ≥ N). Usado `executando_pesado`.
- V2C = chaves em `ConfigCombateV2C` (subclasse; padrões = V2 original) nos mesmos fontes de
  `combate_v2/`. A V2 original reproduz os artefatos byte a byte (testes); o hash dos fontes da base
  mudou (o teste que o fixava agora rejoga a amostra do artefato).
- Finta: a finta só acerta de perto (como o pesado), interrompe quem prepara e sofre parry (é golpe
  rápido). Só o agressivo ganhou regra de finta (`executando_pesado` + oponente esquiva com
  frequência); o adaptativo já está no limite de 8 regras. Sem exploração no turno de execução.
- Parry (C2) também vale contra a finta; morte súbita (C4) multiplica também o parry.
- C5 (esquiva 20 → 15) e C6 (defender sem bônus de guts) foram testados isolados sobre C1–C4 e **não
  adotados**: não moveram G4 nem G5.
- Oráculo de 2 passos: distribuição do oponente limitada às 3 ações mais frequentes em cada nó (custo).
- G6b: condição ±5% de hp e ±2 de guts inicial (a V2 usa guts inteiro).
- G8: parâmetros perturbados listados em `run_bateria_combate.PARAMS_G8` (40 perturbações).
- Validação com N = 400 por par (80 × 5 sementes). O G3 falha só no espelho da tartaruga (0,464,
  tolerância 0,03): a tolerância foi fixada para 1000 partidas por par; na calibração deu 0,492.

Números: nenhum número da tarefa foi ajustado na calibração (as mudanças usam os valores da própria
tarefa: finta 8, parry 5, morte súbita no turno 25 × 1,5). A causa das falhas restantes é o desenho
dos bots, não número (ver CLAUDE.md, seção Correção do combate).

## 2026-09-25 — TAREFA_CORRECAO_COMBATE: bots redesenhados (pedido do Matheus)

A V2C com os bots da V2 reprovou por desenho dos bots; o Matheus pediu para redesenhá-los.
`GAMBITS_V2C` em `combate_v2/bots.py`, ligados por `ConfigCombateV2C.bots_v2c` (os bots da V2 ficam
iguais para a V2 original). Desenho escolhido nas sementes de CALIBRAÇÃO com
`experiments/avaliar_bots_v2c.py` (40 partidas por semente), depois bateria completa:

- agressivo: finta contra quem esquiva; defende golpe repetido quando está abaixo de 50% de vida
  (o parry vira a troca); pesado contra quem defende muito; golpe rápido com guts ≥ 20; interrompe
  quem prepara.
- tartaruga: esquiva o pesado (defende se o oponente finta muito); **interrompe com golpe rápido quem
  prepara com frequência** (sem isso o agressivo dominava); contra quem só defende, avança e prepara o
  pesado (quebra o impasse que dava 100% de limite); carrega só contra oponente passivo.
- atirador: esquiva o pesado de perto; golpe rápido de perto com guts; recua; abaixo de 50% de vida
  contra disparo repetido, avança; esquiva disparo repetido com guts; dispara.
- contragolpe: como a V2, mais "contra quem só defende, de perto, prepara o pesado".
- aleatório e adaptativo: iguais à V2 (o adaptativo já usa as 8 regras).

Tentativas no atirador para o G6b (espelho), todas piores ou iguais: esquivar em vez de avançar ao
perder (0,797), tirar a esquiva por guts (0,882), esquiva por repetição (0,882), avançar com os dois
abaixo de 75% (0,818), defender disparo sem guts (0,880). ε próprio do atirador: 0,1 → 0,73;
0,2 → 0,67; 0,3 → 0,598 (não adotado: decisão do pesquisador).
- **Decisão do Matheus (2026-09-25): aceitar a exceção do atirador no G6b.** Um estilo puramente de
  disparo é uma corrida no espelho e fica acima de 0,65 (0,744 na validação). A V2C
  (`validacao_bots`) é considerada APROVADA com essa ressalva; a Etapa 3 (V21C) começa sobre ela.

## 2026-09-25 — TAREFA_CORRECAO_COMBATE, Etapa 3 (V21C) em andamento

Sobre a base V2C aprovada com a exceção do atirador. Mudanças como chaves (padrão = V2.1 original, que
rejoga a amostra do artefato): C1–C4 da base também no resolvedor da V2.1 (lidas de `Regras.base`);
`ConfigCombateV21C.marca_fragil`; fórmula de vida por `hp_base`/`hp_por_vigor`. Calibração em
`artifacts_combate_v21c/calibracao/v0..v3` (sementes 3101…3505, 40 partidas por par por semente, sem E5).

- Na V2.1 a finta existe (condição `executando_pesado` no adulto), mas nenhum bot da bateria V2.1 a usa.
- Fuga condicionada na V2.1: a sentinela com a passiva pronta continua recuando (é a passiva dela).
- Marca frágil: perde a marca quem recebe dano corpo a corpo (inclusive parry e contra-golpe) ou
  termina o turno em perto.
- **Calibração da Ferrugem** (`experiments/calibrar_ferrugem_v21c.py`, critério fixado antes: maior
  taxa média de espécie ≤ 0,60, o coeficiente mais próximo do original): `hp_por_vigor` 3 → 2,
  `hp_base` 70 → 80 (vida neutra continua 100). Ferrugem 0,656 → 0,575 contra as outras. Na bateria
  (E2) a Ferrugem ainda vence todas por pouco (0,508 contra a Brasa) e o E1 perde o suporte (5 → 3).
- O gate de base da bateria V2.1, na V21C, é a validação da V2C (`G1_G9_base_v2c`).
- **Ajustes pedidos pelo Matheus (redistribuir a Ferrugem, corrigir a resposta ao marcar, tratar o E4)**,
  escolhidos com `experiments/avaliar_v21c.py` nas sementes de calibração:
  - Ferrugem: redistribuir o vetor dela (mantendo 60) só transfere a dominância para a Brasa: as duas
    vencem Cirro e Limo, e quem ganha o confronto direto "vence todas". Sem um ciclo entre as espécies
    o E2 não passa (é desenho de identidade das espécies). A vida por vigor 2,0 derrubava o E1: fica
    **2,5** (`hp_base` 75), que mantém o E1 e enfraquece a Ferrugem. Vetor da Ferrugem inalterado.
  - `marcar`: a resposta declarada antiga (avançar sempre) empurrava para fora do limite de 8 as
    últimas regras do oponente. `RESPOSTAS_V21C["marcar"]`: avança do médio e golpeia de perto só quando
    o oponente usa marcar com frequência. E3 do marcar: 0,612 → 0,312 (validação).
  - E4: o multiplicador de estágio do adolescente não resolve (com 1,0 muralha, vigia, titã e furioso
    ainda 0,9–1,0; duelista cai para 0,38): a diferença vem da passiva e das 8 regras do adulto.
    Nada adotado.
- **Validação da V21C** (`artifacts_combate_v21c/validacao`, 500 partidas por par, com E5): passam
  E1, E3, E5 (25/36), guardião (6,7% no limite), G9 (42,9%), base V2C e S1
  (`artifacts_combate_v21c/bateria_sombria`); **falham E2 (Ferrugem), E4, G6b (espelhos com condição
  ±5%: média 0,725, sentinela 0,919) e G8 (E1 em 69,4% das perturbações, precisa de 80%)**.
- **Redesenho dos bots adultos da V2.1 (G6b, G8) e E4 — tentado e NÃO adotado** (pedido do Matheus;
  detalhes e saídas em `artifacts_combate_v21c/redesenho_bots/`): regras de virada genéricas passam o G6b
  nos 8 arquétipos mas derrubam o E1 (suporte 5 → 3), trocam a dominância de espécie para a Brasa e fazem
  o caçador adulto perder do adolescente (E4 0,0); regras disparadas pela técnica da linha não quebram o
  resto, mas só resolvem sentinela, emboscador e titã. Mais regras para o adolescente (7 ou 8) não mudam
  o E4 (as regras do adulto usam condições que o adolescente não tem). A V21C segue com os bots da V2.1.
- **Decisão do Matheus: "parcial + exceções".** As três regras de virada por técnica (sentinela carrega,
  emboscador esquiva, titã prepara o pesado quando abaixo de 50% e o oponente usa a técnica da linha)
  foram validadas (`artifacts_combate_v21c/redesenho_bots/parcial_nao_adotado/`, 500 por par, com E5):
  G6b médio 0,725 → 0,660, mas o E1 perde o suporte (5 → 3: saem sentinela e espelho), a Brasa passa a
  dominar (E2) e o G8 cai para 55,6%. Quebram um gate que passava: **não adotadas**.
- **V21C APROVADA COM RESSALVAS** (a validação é `artifacts_combate_v21c/validacao`): passam E1, E3, E5,
  guardião, G9, base V2C e S1. **Exceções aceitas pelo Matheus**: E2 (falta ciclo entre as espécies;
  Ferrugem ainda vence todas por pouco), E4 (adulto esmaga adolescente: passiva + 8 regras), G6b (espelhos
  sem sorteio: média 0,725) e G8 (E1 em 69,4% das perturbações).

## 2026-09-25 — combate corrigido no jogo web (`web/digilab_sprites.html`)

Levado para a web: finta (turno de execução, condição `executando_pesado` no adulto), parry 5, fuga
condicionada (com a exceção da sentinela), morte súbita no turno 25 (×1,5), bots da V2C (agressivo,
tartaruga, atirador, contragolpe; o adaptativo e o aleatório já eram iguais), marca frágil e vida por
vigor 2,5 com base 75. Diferenças da web: o oráculo continua de 1 passo e não usa a finta (é só rival
de referência); a resposta redesenhada ao `marcar` é da bateria (E3), não existe no jogo. Os pets salvos
são rejogados com o combate novo: as lutas do registro dão resultados diferentes e, com elas, o
aprendizado dos gambits e o progresso da campanha (o replay confere).

## 2026-09-25 — caráter pelo desvio da política na web (pets v3)

Pedido do Matheus. `web/digilab_sprites.html`: pets novos são **versão 3** = v2 + caráter pelo desvio da
política (espelho de `evolucao.carater`): distribuição de ações da política aprendida menos a da mesma
política recém-nascida (mesmo temperamento), em estados-sonda fixos com números aleatórios comuns; ação →
traço (`CA.mapa`), eixo = média dos traços, ÷ 0,05, cortado em [−1, 1]. Pets v1 e v2 continuam pelos
traços (a evolução deles não muda no replay). Diferenças do Python: 32 sondas × 100 amostras (o Python usa
64 × 200; ~0,15 s por medida no navegador, contra ~0,6 s); sondas e rng da web; a previsão da aba
Evolução recalcula a cada 2 h de jogo ou ação do dono. Sem linha de base (`BASE_CARATER` não se aplica):
com os donos simulados (80 pets, 20 por dono, sem artefato: checagem no console) as linhas saem caçador
41%, brigão 30%, guardião 15%, colosso 14%, e variam por dono (atencioso quase só caçador/brigão; relapso
45% colosso).
- **Linhas equilibradas de novo (pedido do Matheus)**: `DESLOC_CARATER` (web) soma um deslocamento por
  eixo ao caráter pela política (adolescente: linhas ~25%; adulto: mediana do eixo complementar por linha
  → ~50/50), calibrado em 195 pets v3 (4 donos, sementes 910013…910650). Conferência em 80 pets de outras
  sementes (555017…555340; checagem no console, sem artefato): colosso 30%, guardião 29%, brigão 21%,
  caçador 20% (antes 14/15/31/41%); forma de cima 42,5% (no brigão 4 de 17: amostra pequena e a medida pela
  política tem ruído de 32 × 100 amostras).

## 2026-09-25 — escada dos NPCs da campanha rebalanceada

Pedido do Matheus ("rebalanceia a escada dos NPCs da campanha"). Não havia critério escrito para a escada;
os critérios K1–K4 foram fixados em `experiments/calibrar_campanha.py` **antes** da calibração, a partir das
lições de `docs/pve_treino.json` (tier 1 prova de stats, tier 2 prova de estilo, chefe exige estilo e treino
alto). Medidos contra as 8 formas adultas e os 4 adolescentes canônicos × 4 espécies, com treino uniforme
absoluto (adultos 0/18/36, adolescentes 0/18), média das espécies:
- K1 degraus: adultos sem treino t1 > t2 > t3, cada degrau ≥ 0,10.
- K2 tier 1: adultos sem treino ≥ 0,70; adolescentes sem treino em [0,25, 0,60]; +18 de treino rende
  ≥ 0,15 ao adolescente.
- K3 tier 2: adultos sem treino em [0,35, 0,65], ≥ 2 formas ≥ 0,60 e ≥ 2 ≤ 0,40; adolescentes ≤ 0,40.
- K4 chefe: nenhuma forma adulta sem treino ≥ 0,50; adolescentes ≤ 0,15; com +36, ≥ 2 formas ≥ 0,50.

Decisões e interpretações:
- **A campanha passa a lutar com o combate corrigido aprovado (V2C + V21C)**, o mesmo da web
  (`campanha.REGRAS_CAMPANHA`, `CONFIG_COMBATE_V2C`/`CONFIG_COMBATE_V21C` em `config.py`, iguais a
  `experiments/configs/v21c/validacao.json`). Antes lutava com a V2.1 original. Em `run_treino.py` a campanha
  e o S2 usam essas regras; a arena da pesquisa continua na V2.1 original (não era o pedido).
- Estilo do NPC ganhou famílias (`campanha.gambit_npc`): `v2` (bateria V2), `v2c` (bots redesenhados) e
  `v21` (gambits canônicos de uma forma adulta sem as regras de técnica e da passiva do vigia, que o NPC não
  tem). Nomes e chaves dos NPCs ficam (Brutamontes, Sentinela, Soberano); `docs/pve_treino.json` fica como
  a especificação original.
- Diagnóstico com as regras V21C (rodada 0, `experiments/configs/campanha/r0*.json`): a escada original
  (72 agressivo, 80 contragolpe, 90 adaptativo) passa K1, mas a muralha vence o chefe sem treino (0,97),
  nenhuma outra forma chega a 0,5 contra ele mesmo com +36, e o adolescente empata com o tier 2 (0,48).
  O total de stats do NPC mexe pouco; o estilo decide quase tudo.
- Calibração só nas sementes 3101…3505 (rodadas 1–3). Escolha: tier 1 espelho sem técnica, total 54;
  tier 2 furioso sem técnica, total 80 (o treino quase não ajuda: 0,42 → 0,48, como pede a lição); chefe
  agressivo da V2C, total 120.
- **Validação 1 (sementes 4101…4505) reprovou o K4 por 0,004** com o chefe em 110: o espelho sem treino
  fez 0,504 (`validacao1_resultado.json`). O total do chefe foi recalibrado nas sementes de calibração com
  mais partidas (rodada 3: 110 dava 0,476, sem folga) e subiu para 120. **Validação 2 passou K1–K4**
  (`validacao2_resultado.json`). A segunda validação usou as mesmas sementes da primeira depois de ver o
  resultado dela: é uma validação mais fraca, e está registrada assim.
- A margem do K2 é fina: o ganho do adolescente com +18 contra o tier 1 é 0,19 na validação e 0,16 na
  calibração (limite 0,15).
- `run_campanha.py`: a comparação "Soberano original × correção de luta de longe" saiu (o chefe não é mais
  o adaptativo; o resultado antigo continua no histórico do git); entrou a tabela dos estilos da V2 com
  stats neutros contra cada tier.
- Web: mesma escada; os saves antigos rejogam as lutas da campanha contra os NPCs novos (o progresso pode
  mudar; o replay não aplica a trava de desafio, então nada quebra).
- Efeito na TAREFA_TREINO_SOMBRIO (`run_treino.py` de novo; vidas, evolução e arena idênticas): na campanha
  o exigente agora perde do atencioso nos três tiers com IC fora do zero (tier 1 −0,15, tier 2 −0,30,
  chefe −0,38). **S2 continua reprovado**, e não pela escada: o critério (a) compara adultos contra o tier 1,
  que o K2 exige que quase todo adulto vença sem treino; e contra o tier 2 o devastador e o bastião rachado
  passam das formas normais da linha. Consertar o S2 pede mudar as formas sombrias ou o gate (decisão do
  pesquisador).

## 2026-09-25 — formas sombrias redesenhadas para passar no S2

Pedido do Matheus ("redesenha as formas sombrias pra passar no S2"). O gate S2 não mudou
(`run_treino.gate_s2`, regras V21C, escada rebalanceada). Calibração em rótulos de sementes próprios
(`experiments/calibrar_sombrias.py`, `experiments/configs/sombrias/r0..r2`); a decisão é da run canônica.
Leitura de desenho adotada: "a sombra tira a leitura do oponente" — a sombria ganha força bruta (vence a
prova de stats do tier 1) e perde estilo (cai na prova de estilo do tier 2). Desvios de
`docs/arvore_evolucao.json > ramos_sombrios` (o JSON fica como a especificação original; stats, ε mínimo e
teto de vínculo não mudaram):
- **Devastador**: corpo a corpo ×1,3 → **×2,0**; gambits próprios que não leem o oponente (fecha a distância,
  solta o pesado com guts ≥ 20, senão golpe rápido; final carregar) no lugar dos do furioso. Com os gambits
  do furioso ele vencia o tier 2 (0,96, contra 0,24 do duelista); só com o pesado ×1,3 perdia o tier 1 sem
  treino (0,27); ×2,0 dá tier 1 0,60 e tier 2 0,18.
- **Bastião rachado**: gambits do espelho **sem a primeira regra** (contra-golpe quando o oponente prepara o
  pesado). Tier 2 0,98 → 0,83 (limite: muralha 0,95); tier 1 continua 0,91. Contra-golpe de 60% também
  passava, com folga menor (0,93).
- **Colosso partido**: regeneração de guts ×0,5 → **×0,85**. Com ×0,5 só vencia o tier 1 com +12 de treino;
  com ×0,85 vence sem treino (0,63) e segue quase sem chance no tier 2 (0,02).
- Predador sem mudança.

Resultados canônicos (`artifacts_treino/resumo.json`, `artifacts_treino/bateria_sombria/`,
`artifacts_combate_v21c/bateria_sombria/`):
- **S2 passa** nas 4 linhas. Margem fina no critério (a) do predador: 0,503 contra o tier 1 sem treino
  (não mudou com o redesenho).
- **S1 passa** nas duas regras (V2.1 original e V21C); E1 com as sombrias passa (suporte 6 e 5 formas).
  Médias contra as normais (V2.1): devastador 0,74 → 0,27, bastião 0,58 → 0,33, colosso partido
  0,08 → 0,16, predador 0,28. O devastador perde para todos os passivos (0,01–0,36) e saiu do suporte do
  equilíbrio: não é mais a melhor opção de arena.
- Treino (mesmas vidas; só as 4 sombrias do exigente lutam diferente): arena exigente × atencioso 0,43
  [0,25, 0,61]; campanha, exigente − atencioso: tier 1 −0,16 [−0,30, −0,04], tier 2 −0,38 [−0,65, −0,11],
  chefe −0,39 [−0,67, −0,12].
- Web: mesmos números; os gambits sombrios só semeiam o pet (depois ele aprende como qualquer forma).

## 2026-09-26 — progressão da campanha: pet básico perde, pet treinado vence

Pedido do Matheus: validar que um pet com stats básicos não vence o NPC inicial e um com stats maiores
vence, para o jogador ter de melhorar o pet antes de cada desafio. Critérios P1–P4 fixados antes da
calibração em `experiments/calibrar_progressao.py` (substituem os K1–K4 da escada anterior). Níveis de
treino tirados das vidas reais de `artifacts_treino/vidas` (fim da infância ~8 pontos, fim da adolescência
~15, adulto ~29).

- **Diagnóstico** (rodada 0): com a escada K1–K4, P2–P4 passavam, mas a criança não vencia o tier 1 nem
  com +12 de treino (0,10): treinar na infância não servia para nada.
- **Impasse** (rodada 1): com NPC de tamanho de criança, qualquer um que a criança treinada vence o
  adolescente sem treino também vence (0,57–0,87). A evolução (vida e guts ×0,6 → ×0,8) pesava muito
  mais que o treino da infância. **Decisão do Matheus: treino mais forte.**
- **`ConfigTreino.peso_ponto_combate` 1 → 3**: cada ponto treinado vale 3 pontos de stat em combate
  (`catalogo.com_treino`, arena e campanha). Pontos ganhos, tetos (+10 por stat, +36 na vida) e fadiga
  não mudam. Na arena normalizada o treino passa a especializar mais o pet. Quando um stat bate no teto
  da normalização, a sobra vai em partes iguais aos outros (comportamento que já existia; um teste de
  proporção usava treino alto o bastante para bater no teto e foi ajustado).
- **Escada nova** (rodadas 2–5, só sementes de calibração):
  - Brutamontes: NPC **de tamanho de criança** (vida e guts ×0,6), total 72, gambits da criança arisca
    (`campanha.gambit_npc` ganhou a família `crianca`; `bots.CRIANCAS` espelha as sementes da web);
  - Sentinela: adulto, total 72, atirador da V2C (guarda distância e atira);
  - Soberano: adulto, total 135, agressivo da V2C.
  O Sentinela precisou mudar: com o treino mais forte o adolescente brigão piorava contra o furioso (mais
  guts → mais pesados punidos) e só a linha guardiã virava com treino. O espelho travava porque a linha
  caçadora vence ele sempre, com ou sem treino.
- **Validação** (sementes 4101…4505, `experiments/configs/progressao/validacao_resultado.json`) passa P1–P4:
  criança 0,08 sem treino → 0,61 com +8 contra o tier 1; adolescente sem treino 0,47 contra o tier 1;
  adolescente 0,18 → duas linhas ≥ 0,5 com +15 contra o tier 2; adulto sem treino 0,44 contra o tier 2;
  adulto 0,06 (nenhuma forma ≥ 0,5) → 0,51 de média com +29 contra o chefe.
- Ressalva: a medida usa treino uniforme (o mesmo em todos os stats). O jogador treina stats escolhidos;
  em algumas linhas o treino uniforme até piora a luta (o brigão contra a Sentinela), porque muda o ritmo de
  guts dos gambits.
- As rodadas antigas de `experiments/configs/campanha/` e `configs/sombrias/` foram medidas com peso 1;
  refazê-las agora dá outros números (o peso é global).
- **Critério por linha** (pedido do Matheus depois que a média escondeu linhas travadas): com a escada
  acima, a linha caçadora nunca vencia o tier 1 (adolescente 0–1%, adulto emboscador 15% com +36) e
  algumas linhas venciam sem treino. Rodadas 6–11: nenhum NPC único faz toda linha perder sem treino e
  vencer treinada; o estilo decide mais que os stats. NPC menos previsível (ε 0,2–0,5) destrava linhas,
  mas o pet básico passa a vencer; NPC que acompanha o estágio do pet não ajuda (os gambits das linhas
  dominam os estilos da V2). **Decisão do Matheus: média + ninguém travado, com rivais à escolha e o chefe
  com exceção.**
- **Campanha final** (`ConfigCampanha.npcs`, campo `lugar`; vencer qualquer rival de um lugar abre o
  próximo):
  - Campina: Brutamontes, criança, total 72, gambits da criança serena (a arisca travava os caçadores).
  - Torre: 3 rivais, escolhidos pela maior folga de cobertura entre os NPCs medidos: Sentinela (atirador
    V2C, 72), Carcereiro (furioso sem técnica, 110) e Porteiro (agressivo V2C, 72).
  - Cidadela: Soberano, agressivo V2C, 135.
- **Validação por lugar** (`criterios_lugares`, sementes 4101…4505, `validacao_resultado.json`): cada rival
  vence o pet básico do estágio; nenhuma linha fica travada na Campina nem na Torre; degraus ok.
  **Exceção aceita**: duelista, furioso, sentinela e emboscador não vencem o Soberano nem com +36. Em
  26 estilos testados não houve chefe que os adultos sem treino percam e que essas formas vençam treinadas.
- **S2 com a campanha nova**: tier 2 = o melhor rival da Torre (o jogador escolhe); **tolerância de 0,02**
  no critério (b) (decisão do Matheus: as sombrias têm ε 0,2 e ganham uma luta ou outra por acaso; o
  colosso partido ficava em 1% contra 0,4% do vigia). Sombrias recalibradas (`configs/sombrias/r6–r7`):
  devastador bate com golpe rápido e só solta o pesado com guts ≥ 60, corpo a corpo volta a ×1,3 (valor da
  especificação); bastião rachado = gambits do espelho sem as regras que leem o oponente (contra-golpe 100%,
  como na especificação); colosso partido regen ×0,85; predador igual. Na calibração as 4 linhas passam
  o S2 e o S1.
- **Runs canônicas finais**: S2 passa nas 4 linhas (`artifacts_treino/resumo.json`). S1 passa nas regras
  V2.1 e V21C. **E1 com as sombrias passa na V21C** (suporte emboscador, espelho, furioso, muralha), que é
  o combate aprovado e o da web, mas **reprova na V2.1 original** (suporte de 3, mínimo 4): o bastião
  rachado ficou fraco (média 0,10 contra as normais) e saiu do suporte. Registrado como ressalva.
  Campanha com treino (`artifacts_campanha/treino.json`): o exigente perde do atencioso contra a Campina
  (−0,16 [−0,31, −0,03]), o Carcereiro (−0,35), o Porteiro (−0,48) e o Soberano (−0,50); contra a Sentinela
  −0,14 [−0,38, 0,08].

## 2026-09-26 — todo pet treinado vence cada NPC (NPCs fixos e imprevisíveis)

Pedido do Matheus: "garanta que todos os pets treinados vencem todos os chefes". Respostas dele: vale
para **cada NPC individualmente** (não basta um rival por lugar) e "treinado" = **treino típico de uma
vida** (criança 8, adolescente 15/22, adulto 29/36, tabela `ALCANCE`).

- Varredura (rodadas 12–14: tier 1 com NPC criança; Torre e chefe com 13 estilos × 4 totais × ε 0,2–0,5):
  só NPCs bem imprevisíveis (ε 0,4–0,5) deixam toda linha vencer treinada, e neles o pet sem treino vence
  com frequência (melhor chefe: 52% na média dos adultos sem treino).
- Alternativa oferecida: NPC que ajusta a tática à linha do pet (os dados mostram, para toda linha em cada
  lugar, uma tática em que ela perde sem treino e vence treinada). **Decisão do Matheus: NPC fixo e
  imprevisível.**
- NPCs: Brutamontes (criança, 96, criança arisca, ε 0,5); Torre: Sentinela (tartaruga V2C, 72, ε 0,4),
  Carcereiro (espelho sem técnica, 90, ε 0,5), Porteiro (agressivo V2C, 90, ε 0,5); Soberano (agressivo
  V2C, 110, ε 0,5). Escolhidos pela menor vitória do pet básico entre os que não travam ninguém.
- **Validação** (sementes 4101…4505, `configs/progressao/validacao_resultado.json`, `criterios_todos_vencem`):
  nenhuma linha travada em nenhum dos 5 NPCs. Pet sem treino do estágio sugerido: Brutamontes 0,45,
  Sentinela 0,66, Carcereiro 0,50, Porteiro 0,39, Soberano 0,52 (média). Pet treinado: 0,81 a 0,97.
- Consequência: a progressão por treino ficou fraca (o pet sem treino vence metade das vezes); o treino
  garante a vitória, não a libera. Os critérios P1–P4 e o "básico perde" por lugar deixam de valer (ficam
  como relatório).
- Durante a varredura, rodar com os 20 processos deu erros diferentes a cada execução (TypeError em
  estruturas do Python); num processo só e com 8 processos tudo rodou limpo. Tratado como instabilidade da
  máquina sob carga total; `--processos` foi adicionado ao `calibrar_progressao.py`.
- **S2 com os NPCs imprevisíveis**: só o predador reprovava (não pode recuar e nunca vencia o Brutamontes,
  que corre para cima). Redesenho (`configs/sombrias/r8`): o predador fecha e bate rápido, sem ler o
  oponente (passiva igual: disparo ×1,4, recuar ilegal). S2 passa; S1 passa nas duas regras; E1 com as
  sombrias passa na V21C e segue reprovando na V2.1 original (suporte 3, mesma ressalva).
- **Efeito na pesquisa**: com todo pet treinado vencendo todo NPC, a campanha deixou de separar os donos
  (todos os braços, inclusive o exigente, vencem 0,96–1,00; exigente − atencioso ≈ 0 em todos os NPCs). A
  conclusão "forçar custa na campanha" deixa de ser medível pela campanha; a arena normalizada segue
  inconclusiva (exigente × atencioso 0,43 [0,24, 0,63]).

## 2026-09-27 — TAREFA_ANALISE_PODER, Etapa 0 (configuração fixa da pesquisa)

`experiments/configs/poder_pesquisa.json`, `ConfigArenaPesquisa`, `evolucao.condicao_na_arena`, `tests/test_poder.py`.
Interpretações:
- **Pets da pesquisa**: o pipeline do `run_treino` (personalidade completa + treino, 5 braços, 14 dias,
  orçamento 298 por vida, evolução até adulto), lutando na arena **V21C com stats normalizados**. O 0,615
  citado na tarefa é da arena v1 (traços, sem formas); com combate V21C o pet precisa de forma adulta, e o
  único pipeline de pesquisa que evolui pets com personalidade é o do treino. Os braços pedidos (atencioso,
  aleatório + três secundários) são os `BRACOS_TREINO` (relapso, incoerente, exigente).
- **Condição física neutra**: `ConfigArenaPesquisa.condicao_neutra` (padrão False), aplicada só na arena
  normalizada; a campanha segue com a condição do cuidado. Com a chave desligada o lutador é o mesmo de
  antes (teste) e o `run_treino` reproduz os artefatos (conferido rodando de novo).
- **Ordem da normalização**: `com_treino` multiplica os pontos por `peso_ponto_combate` e só depois devolve o
  total ao orçamento da espécie (teste). Exemplo (duelista brasa, forca +1, mira +0,5, peso 3): forca 15 →
  16,744, igual a normalizar base + 3 × pontos; a ordem inversa daria 16,829.
- **Sementes**: piloto 50001–50020, confirmatórias 60001–60160, rótulos de partida próprios; disjuntas das
  antigas (lista no config). A sonda do caráter (9001) é instrumento, igual em todas as runs.
- A arena da pesquisa já existente (`run_treino`) continua na V2.1 original; a V21C entra pelo parâmetro
  `cfg_v21` de `lutador_pet` e pelas regras do config, só nas runs novas.
- Conferência byte a byte: com a chave desligada o `run_treino` refez vidas, evolução, arena, campanha e
  S2 idênticos; a única linha diferente em `artifacts_treino/resumo.json` é `fontes_sha256` (hash do código,
  que mudou com `condicao_na_arena`). Suíte: 289 testes.

## 2026-09-27 — TAREFA_ANALISE_PODER, Etapas 1–5

- **Piloto** (`experiments/run_poder.py`, `artifacts_poder/piloto/`): 20 ovos × 5 braços, 100 partidas por
  par, 10 réplicas do par principal (pets fixos, sorteios de partida diferentes), painel B = 8 formas × 4
  espécies com 20 partidas por bot. Neutra e real usam os mesmos pets e as mesmas sementes de partida
  (números aleatórios comuns). 100 vidas em 107 s; 104 mil partidas por variante em ~12 s (8 processos).
- **Definições** (interpretação): em B a unidade de ruído é a partida contra um bot fixo; a variância de
  partida é medida em torno da média do par ovo × bot (o bot faz parte do painel, não é ruído). No poder, M
  do desenho B = partidas por bot (cada pet joga 32 × M).
- **Poder**: fórmula `σ²_ovo/N + σ²_partida_1/(N·M)` com teste t bilateral, conferida por simulação
  paramétrica (2000 réplicas por célula) e contra o bootstrap do piloto (fórmula 0,0086 × bootstrap 0,0081
  no A neutro). O plano usa bootstrap sobre ovos como teste principal; o poder foi calculado com o teste t,
  que o aproxima com N ≥ 40.
- **Plano** (`docs/PLANO_ANALISE.md`): desenho principal PENDENTE DE DECISÃO; condição neutra como
  principal é PROPOSTA (não estava na tarefa). N = 160 nos dois desenhos (acima do mínimo, custo ~15 min);
  critérios de sustentada/refutada/inconclusiva definidos sobre o IC com margem de equivalência Δ.

## 2026-09-28 — fala livre por LLM local: APROVADA só com o gemma2:9b (decisão do Matheus)

`docs/TAREFA_FALA_LIVRE.md` executada pelo `docs/PLANO_VERSAO_FALA_LIVRE.md` (onde divergem, vale o plano),
na branch `exp/fala-livre` (worktree `v1-fala-livre`, porta 8767, tag `v1-antes-fala-livre`). Relatórios em
`artifacts_fala_livre/rodada1/` e `rodada2/RELATORIO.md`.

- Desvios da tarefa pelo plano: falas e conversas no **log de apresentação separado** (`<save>.fala.jsonl`,
  na web no localStorage), nunca no log do pet (a versão do save continua v3); pacote `digilab_fala_livre/`
  fora de `digilab/`; servidor por um único gancho; web por três ganchos (`// GANCHO fala-livre`).
- Interpretações: situações da avaliação tiradas das vidas de `artifacts_treino/vidas` (50 vidas × 4
  estágios); juiz fixo `qwen2.5:7b` para todos os modelos; moldura como linha de base do erro do juiz;
  "afirmação sem fato" medida por fala.
- Rodada 1 (semente 20260927): mediu mal (juiz marcava ações verdadeiras, 9–27 falas truncadas por modelo,
  timeouts no gemma). Rodada de ajuste (a única que o plano permite): juiz `verif-v3`, limites de tokens,
  prompt `livre-v2`, **amostra nova** (semente 20260928). As 30 perguntas de conversa são as mesmas nas duas
  rodadas.
- Resultado da rodada 2: só o `gemma2:9b` passa na qualidade (3,0% de falas com afirmação sem fato, teto
  por causa do erro do juiz; 0/30 conversas inventaram; 0 manipulação); latência p90 4,8 s (zona
  intermediária do plano). `qwen2.5:3b` e `qwen2.5:7b` reprovam (46% e 25,5%; armadilhas 16/30 e 10/30).
- **Decisão do Matheus (2026-09-28): aprovar só com o gemma2:9b**, sem esperar a avaliação cega. Merge na
  `main` com `modo_fala` desligado por padrão (a página abre em "template"); a moldura e o template seguem
  iguais. Modelo padrão da fala livre: `gemma2:9b` (`DIGILAB_MODELO_LIVRE` troca).
- Pendente: avaliação cega do Matheus (`artifacts_fala_livre/rodada2/avaliacao_cega.csv`) e confirmação dos
  dois "Não me deixe…" do 7b (não afetam o gemma). A identificação "exp-fala-livre" (título, selo e chave de
  saves própria) ficou só na branch experimental; na `main` a página usa a chave de sempre.
- Na integração, a interface nova da `main` (Interface UP) trocou a aba Estado por uma âncora vazia: a
  conversa foi montada na tela do pet (`.pet-tela`), ao lado do balão.

## 2026-09-28 — escala de stats (TAREFA_PLANILHA_PROGRESSAO, Parte C)

Jornada e escala aprovadas pelo Matheus (`docs/JORNADA_JOGADOR.md`, seção 5). Ponto 6 (tempo com o app fechado): mantido
como está (fechar = pausa), com o aviso no ovo pelo tutorial. `ConfigEscala` desligada por padrão; com ela desligada as
runs antigas não mudam (teste e suíte: 344 passaram, 1 pulado). Interpretações e desvios:

- **Vida exibida** = E × vida própria / vida neutra (100 = `hp_base` + 10 × `hp_por_vigor`). O desenho dizia "vida de
  hoje sem o multiplicador × E", que daria 150 mil no adulto; o divisor faz a tabela 50/200/600/1500 bater.
- **Razão como fração exata** (`fractions.Fraction`): (k·a)/(k·b) em float nem sempre é igual a a/b; com a fração, a
  invariância vale para qualquer fator comum (teste com 2, 10, 37 e 7/3). Na web a razão é float (o teste da web usa
  potências de 2).
- **Guts fica com o multiplicador de estágio** (é ritmo); só a vida perde. Com a escala o treino é sempre normalizado
  ao orçamento (o tamanho vai para E) e o `peso_ponto_combate` sai da campanha.
- **NPC na escala**: perfil neutro (10 em cada stat; o `total_stats` deixa de valer), E = vida do estágio SUGERIDO ×
  fator, ε 0,2; os gambits e o estágio dos gambits ficam os de antes.
- **Só a campanha usa a escala** (a tarefa: "magnitude usada em combate na campanha"). A arena da pesquisa e a arena
  contra bots do jogo ficam como estavam.
- **Bateria V21C com a escala** (`artifacts_combate_v21c/validacao_escala`): todos os gates que passavam passam com os
  mesmos números (entre adultos a razão é 1). E4' (adulto sem treino × adolescente com +22 na faixa [0,60, 0,85])
  **reprova** em 7 de 8 formas (0,965–1,0): com β 0,03 o Champion treinado chega a E 996 contra 1500. E4'' (os dois sem
  treino, adulto ≥ 0,90) reprova só no espelho (0,841). Para o E4' passar, β maior ou degraus menores: decisão do
  pesquisador.
- **Calibração dos NPCs** (`experiments/calibrar_escala.py`, critério fixado antes; sementes 3101…3505; validação
  4101…4505): Brutamontes 1,1, Carcereiro 1,5, Porteiro 1,1 e Soberano 1,2 passam (≤ 0,30 sem treino, ≥ 0,80 com o
  treino típico). **A Sentinela não fecha com nenhum fator** de 0,8 a 3,0: com o estilo tartaruga a linha caçadora vence
  sempre, e o pet sem treino fica acima de 0,3; ficou o fator de menor violação (1,6: 0,41 → 0,70 na validação). A linha
  colosso fica abaixo de 0,5 treinada contra a Sentinela e o Carcereiro (o "todo pet treinado vence cada NPC" de
  2026-09-26 deixa de valer para esses dois). Trocar o estilo da Sentinela: decisão do Matheus.
- **Web**: a escala entra no motor (`CESC`, chave `ESCALA`, desligada para os gabaritos) e o app liga (`?escala=0` só
  para a conferência de paridade com o HTML antigo). Saves antigos rejogam as lutas da campanha com a regra nova (o
  progresso pode mudar; o replay confere).
- **Vários pets com um ativo** (pedido do Matheus durante a Parte C): o ativo segue no save de sempre; os outros ficam
  em `…-guardados` só com o registro, parados no tempo (nenhum evento). Primeiro acesso: escada de exemplo de 6 pets,
  do In-Training ao Mega treinado (donos simulados + treino sem forçar). Só na web.
- **Tutorial**: o Bit (personagem original, pixels no código), uma frase por momento, marcadas como vistas em
  `…-dicas`; interruptor em Aparência. Só na web.
- **Decisões do Matheus depois da Parte C (2026-09-28):** (1) **exceção da Sentinela aceita** (fator 1,6; 0,41 sem treino
  e 0,70 com o treino típico na validação); (2) **E4 redefinido** na escala: o adulto sem treino vence o adolescente da
  mesma linha, sem treino e com o treino máximo do estágio (+22), em ≥ 0,60, sem teto (`ConfigEscala.taxa_min_e4`,
  gate `E4_escala_estagio_importa`). O E4' e o E4'' da Parte B saíram (a faixa [0,60, 0,85] e o ≥ 0,90).

## 2026-09-28 — educacao-v1: gate de equilíbrio dos estilos em aberto (V3 e V3b)

- **V3** (`artifacts_educacao/`, PLANO_ANALISE_V3):
  - o gate passou na condição neutra (cuidar 0,514, treinar 0,418, lutar 0,513) e **reprovou na real** (treinar 0,378);
  - o braço lutador saiu idêntico ao atencioso (−0,0004): as lutas não mudam nem a política nem o estado;
  - o exigente fica com saúde final 0,02, porque as sessões no teto tiram verba do cuidado.
- **V3b** (adendo, `artifacts_educacao_v3b/`):
  - "luta treina" e o braço treinador levaram **577 de 640** pets à forma sombria;
  - as lutas a cada 30 min, como sessões, acumulam fadiga e viram sessões forçadas, que geram sobrecarga;
  - todos os braços ficaram entre 0,26 e 0,32 e o gate reprovou nos três estilos;
  - além disso, o treino bate no teto do estágio (~34), então mais lutas não viram força.
- **Decisão do Matheus (opção B)**:
  - parar a calibração por runs;
  - `ConfigLesoes.luta_treina` fica **desligado** (comportamento da V3);
  - o braço treinador fica disponível, mas fora do gate;
  - **o equilíbrio dos estilos vira tarefa própria de game design**: o estilo "lutar" precisa de um ganho sem teto e que não gere sobrecarga, e isso é decisão de design, não número a ajustar.
- **Leitura válida**: a V3.

## 2026-09-29 — linhagem E1: rodada balanceada reanalisada dos arquivos gravados

- **O que aconteceu:** a rodada `especies_balanceadas` rodou as 640 vidas (769 s) e o painel (77 s), mas caiu ao gravar o `meta.json`. Outra sessão trocou o branch da pasta `v1` para `design-voz-propria` durante a run, e o script sumiu do disco.
- **Os dados continuam válidos:** as vidas e as partidas já estavam gravadas, e o código delas já estava carregado nos processos.
- **O que foi feito:**
  - a análise foi refeita com `run_natureza_criacao.py --reanalisar` a partir do `pets.json` e do `partidas_neutra.json`, sem nenhuma vida nem partida nova;
  - o motivo ficou gravado no `meta.json` (`tempos.reanalise`);
  - conferência: a reanálise da rodada `especie_fixa` gera um `resultado.json` idêntico ao original.
- **Daqui em diante:** as runs deste branch rodam na worktree `D:\Trab\digilab\v1-linhagem`.


## 2026-09-29 — medalhas do Tamer e trava da evolução só no jogo (pets v6)

- **Desvio entre o jogo e a pesquisa:** o Tamer, as medalhas e a trava da evolução (1/3/5 medalhas para Champion/Ultimate/Mega)
  existem **só no jogo web** (`web/app/`, pets v6, evento `u` no registro do pet; `docs/DESIGN_MEDALHAS_ARENAS.md`, parte 1). O
  Python da pesquisa (`digilab/`, `experiments/`), os protocolos e os hashes não mudam; o pet de pesquisa evolui sem medalha.
- **Saves descartados** (decisão do Matheus): na primeira abertura depois da atualização o app apaga o pet ativo e os guardados
  (v1–v5), avisa e começa num ovo novo v6. Os gabaritos de paridade (v1–v3) e os testes de v4/v5 continuam iguais.
- **Fonte provisória de duas medalhas** até as arenas da parte 2: a 3ª vem do Devidramon (Torre de pedra) e a 5ª do Machinedramon
  (Montanha Espiral). Medido no motor web (sementes 4101…4505, escala ligada, 10 lutas por semente, sem IC): um Ultimate com o
  treino típico (36) vence o Machinedramon **0,28** em média, e só as formas caçadoras passam de 0,5 (sentinela e emboscador ≈ 1,0;
  muralha, titã, vigia, duelista e espelho ≈ 0–0,08). Com a fonte provisória, a 5ª medalha, e com ela o Mega, depende de o Tamer ter
  (ou criar) um caçador. O Lago da parte 2, calibrado para Ultimate, resolve.
  **Corrigido no mesmo dia** (recomendação aceita pelo Matheus): a 5ª provisória passou a vir do **Tortomon** (Torre de pedra),
  que o pet treinado vence (a campanha é calibrada para isso). O número acima fica como o motivo da troca.
- **Tempo dos estágios nos pets v6:** Rookie → Champion e Champion → Ultimate contam o tempo desde a evolução anterior
  (`Motor.tickLimiteEstagio`), não desde o nascimento. Com a trava, um Rookie que esperou a medalha ganharia um Champion curto.
  Os v1–v5 não mudam (teste).
- **Cenários:** os pets simulados (Diário · Cenários) ficam v5 (`VERSAO_CENARIO`), sem Tamer: evoluem como antes e não ganham medalha.


## 2026-09-30 — V21D (variante a_c_e2v_v) validada e levada ao jogo só nos pets v6

- **Decisão do Matheus:** fixar o ganho da rodada 2 com o furioso como exceção conhecida. O gate proposto
  (`docs/DIAGNOSTICO_ARQUETIPOS.md`, seção 7) foi reduzido na validação:
  - A1 e A2 valem para as 7 formas que não são o furioso;
  - A3, A4 e A5 são só relatados.
  Critérios registrados e commitados antes da run (`docs/VALIDACAO_V21D.md`, commit `357ab23`). Resultado: APROVADA.
- **Python:** as chaves da `ConfigCombateV21D` continuam desligadas por padrão. A pesquisa (V3, E1, confirmatória) não
  lê as chaves e não muda.
- **Desvio entre o jogo e a pesquisa:** no jogo, os pets v6 lutam com a V21D e os v1–v5 com a V21C. Não há versão de
  pet nova.
- **Repertório dos gambits híbridos (só na web) não muda.** As duas regras novas do vigia entram só pela semente do vigia
  v6, e o pet não as recebe como candidatas numa troca. Mexer no repertório mudaria o replay dos pets v1–v5.
  **Corrigido em 2026-09-30** (medalhas, parte 2): sem elas nas candidatas, a primeira troca que as tirasse da lista as tiraria
  para sempre. Nos pets v6, a forma do vigia (Ultimate ou Mega) recebe as duas também como candidatas de troca, no fim da lista
  (`gambits_pet.candidatasDoVigia`, `GambitsPet.candidatas`). O repertório continua igual; os v1–v5 e as outras formas têm as
  mesmas candidatas (`test/vigia_candidatas.test.ts`). Um vigia v6 já salvo que fizer uma troca daqui em diante pode trocar
  por uma delas (os saves v6 não foram descartados de novo).
- **Saves descartados de novo** (autorizado pelo Matheus): os pets v6 de antes mudariam de comportamento no replay.
  - O descarte único ganhou um marcador de versão (`…-descarte` = 2) e tira os pets até v6, com o mesmo aviso.
  - Com pet descartado, o registro do Tamer também recomeça sem medalhas, porque o aviso diz "nenhuma medalha". As
    medalhas ganhas com o combate antigo saem junto.
  - Sem pet para descartar, o Tamer fica como está.
- **NPCs web-only da campanha v5** (Espiral e Cidadela): não entraram nos critérios. Foram medidos com a V21D depois,
  como relato, e seguem nas metas (`artifacts_campanha/mega/validacao_v21d.json`).


## 2026-09-30 — arenas com líderes (medalhas, parte 2) só no jogo (pets v6)

- **Desvio entre o jogo e a pesquisa:** as seis arenas, os lugares novos (Floresta e Lago), as regras de arena e os líderes existem
  **só no jogo web** (`web/app/`, pets v6; `docs/DESIGN_MEDALHAS_ARENAS.md`, seção 12). `digilab/` e `experiments/` não mudam; a
  campanha da pesquisa continua a de sempre.
- **Líderes:** a Floresta ficou com o **Youkomon** e não com o Kyubimon sugerido, porque o Kyubimon é forma de pet (Champion guardião
  do brasão Coragem). O Lago ficou com o **MarinBullmon** (Ultimate do atlas que não é forma de pet).
- **Como cada regra foi feita (interpretações):**
  - Torre (paciência): o NPC líder ganha técnica (os NPCs não tinham): o contra-golpe, com as regras dele da lista do espelho.
  - Floresta (leitura): a troca de padrão é pela condição de turno (`turno_execucao` 10) numa lista própria do líder, sem mexer no
    combate. A primeira lista não fechava as metas; a final saiu de 30 variantes medidas só nas sementes de calibração.
  - Cidadela (resistência): as três lutas são **um evento `l` só** (sem campo novo): as sementes da 2ª e da 3ª derivam da do evento;
    o pet leva vida e guts, o líder volta inteiro; o pet luta a série com a lista do começo e aprende depois de cada luta, na ordem;
    cada luta conta nas lutas do estágio e na lesão; a vitória no lugar e a medalha só vêm com as três.
  - Lago (vínculo): "o pet decide sozinho" = a lista sem as travas (só a nota ordena) e com as regras vetadas de volta, as que ele
    conhece (com nota) e a forma permite, cortada na capacidade. Sem trava nem veto é a lista de sempre.
- **Fatores dos líderes:** calibrados no motor web com as regras dos pets v6 (`web/app/test/calibrar_arenas.mjs`,
  `artifacts_campanha/arenas/`). O pet de referência fica sempre no lado A (o `calibrar_mega.mjs` alternava os lados), porque a série
  da Cidadela só existe com o pet no lado A, como no jogo. Os fatores da luta de arena valem só nela; nas campanhas de antes os NPCs
  seguem com os de sempre. Recalibrados na escala dos pets v6 (entrada seguinte).
- **Saves v6:** o descarte único versão 3 (no mesmo branch) tira os pets v6 de antes das arenas, com o mesmo aviso (o replay das lutas
  contra o Guardromon e o Myotismon mudaria); a versão 4 tira os de antes da escala v6 (entrada seguinte).
- **Correção do vigia (mesmo branch):** as duas regras novas do vigia V21D viraram candidatas de troca nos pets v6 (seção V21D acima).

## 2026-09-30 — escala dos pets v6 (`CESC_V6`) diverge da escala da pesquisa

- **Desvio entre o jogo e a pesquisa:** decisão do Matheus (2026-09-30): "o treino tem que decidir" contra cada líder e "o estágio tem
  que pesar" (um Champion não derrota um Mega; contra um Ultimate, passa sufoco). As lutas de escala dos pets v6 (campanha e arenas)
  usam uma escala própria, `CESC_V6` (`web/app/motor/constantes.ts`): mesma fórmula da `ConfigEscala` (E = vida do estágio × (1 + β ×
  pontos); dano × E_A/E_B), com vida Rookie 200, Champion 700, Ultimate 2500, Mega 23000 (bebê 50) e **β = 0,045** (na pesquisa: 200,
  600, 1500, Mega 3000 do `CMG`, β 0,03). A `CESC`, a `ConfigEscala`, os pets v1–v5, os gabaritos e `digilab/`/`experiments/` não
  mudam; o `constantes.test.mjs` passou a conferir a `CESC` contra a `ConfigEscala` e registra a `CESC_V6` como só na web.
- **Quem usa qual escala:** o pet pela versão dele; o NPC pelas regras da luta (a luta de um pet v6 usa a V21D, e com ela a escala v6).
  Os desafiantes da campanha v6 (não líderes) ganharam fatores próprios em `CESC_V6.fatorNpc`; nos pets v1–v5, os de sempre.
- **Metas (PROPOSTAS a partir da decisão, medidas na escala com os bots canônicos e as 4 espécies de cada lado):** vizinhos (baixo com o
  treino típico × cima sem treino) ≤ 0,10 em pontos; dois estágios de distância: nenhuma vitória. Líderes: sem treino ≤ 0,05, com o
  treino típico ≥ 0,80, nenhuma forma < 0,5. Desafiantes: as de sempre (≤ 0,30 / ≥ 0,80 / nenhuma forma < 0,5).
- **Método e escolhas** (`web/app/test/calibrar_escala_v6.mjs`, `artifacts_campanha/escala_v6/calibracao.json`): a luta na escala só
  depende da razão E_A/E_B; o β sai da viabilidade dos líderes (a vida do estágio cancela) e as vidas saem das metas de estágio. Com
  margem de 0,01 nos líderes e 0,005 nos vizinhos (cerca de 2 erros-padrão), o menor β da grade com todos os líderes viáveis (menos a
  Torre, cuja alavanca é a lista) é 0,045 (com 0,03, 0,035 e 0,04 algum líder fica sem folga); as razões de vida são as menores da grade
  que passam, arredondadas para cima em 2 algarismos.
- **Distância das razões do DW1** (âncora pedida pelo Matheus: Rookie → Champion ×2, Champion → Ultimate ×2,5; Ultimate → Mega ×2, o
  `CMG`): a escala v6 tem ×3,5, ×3,57 e ×9,2. Cada razão = (1 + β × treino típico de baixo) ÷ (razão de E que a meta pede): Rookie →
  Champion 1,36 × 2,57; Champion → Ultimate 1,99 × 1,80; Ultimate → Mega 2,62 × 3,51. A parte do combate fica perto do DW1 (2,57 e 1,80
  contra 2 e 2,5), menos no Mega (3,51: a curva do Ultimate treinado contra o Mega tem uma cauda longa, com vitórias por estilo); o resto
  do afastamento vem do **peso do treino**, que precisa pesar para o treino decidir contra os líderes e que a vida do estágio de cima
  compensa. (A razão de E do jogo equivale a vida e ataque juntos: E ×2 nos dois lados é o "HP ×2 e ataque ×2" do DW1.)
- **O que não fechou:**
  - **dois estágios de distância = 0,00:** não fecha com a escala. Validação: Rookie típico × Ultimate 0,0372 de vitórias, Champion
    típico × Mega 0,0509. São vitórias por estilo: em alguns pares o de cima nunca acerta o de baixo em 40 turnos (ex.: caçador ×
    titã, caçador × muralha), e o limite de turnos decide pela fração de vida, que a escala não muda. Na calibração a taxa já é o
    piso (a mesma com razão de E 0,01). Fechar pede regra de combate (ex.: o limite de turnos na escala) ou mudar listas das formas,
    fora das alavancas desta tarefa: decisão do Matheus. **Resolvido pela regra do limite do desafiado** (entrada seguinte).
  - **Tortomon** (desafiante da Torre): nenhum fator fecha as metas (a exceção da Sentinela de sempre): fator 1,6, sem treino 0,3912,
    colosso 0,485 na validação.
- **Guardromon na arena da Torre:** a lista mudou (só na luta de arena dos pets v6): contra quem atira com frequência ele avança, no
  lugar do contra-golpe (que não devolve disparo sem a passiva do espelho). Com a lista de antes nenhum fator passava a meta de 0,05 (o
  caçador sem treino vencia atirando de longe). A ideia "paciência: devolve golpe forte" fica (`web/app/test/explorar_torre.mjs`,
  `artifacts_campanha/arenas/torre_variantes.json`, só nas sementes de calibração).
- **Saves:** descarte único versão 4: os pets v6 de antes da escala nova saem, com o mesmo aviso (as lutas deles mudariam no replay).

## 2026-09-30 — limite de turnos: vence quem foi desafiado (só no jogo, pets v6)

- **Desvio entre o jogo e a pesquisa:** decisão do Matheus (substitui a ideia de "vida absoluta", que não foi implementada): quando a
  luta chega ao limite de turnos sem nocaute, vence quem foi desafiado. No jogo o pet sempre desafia (NPC da campanha, líder da arena,
  bot da arena), então nos pets v6 a luta que chega ao limite é derrota do pet, e na série da Cidadela ela quebra a série. No combate
  V21C/V21D do Python (e nos pets v1–v5, nos cenários e no gabarito de paridade V21D) o limite continua decidido pela fração de vida.
- **Como:** `web/app/motor/combate.ts` (`fimV2`/`jogarV2` com o desafiado: lado A, lado B ou ninguém; `desafiadoDaVersao`),
  `arenas.jogarArena` e `Motor.montarLuta`. Deriva da versão do pet: nada novo no registro. Descarte único versão 5.
- **Validação de novo** (sementes 4101…4505, uma vez, nenhum número da escala mudou): metas de estágio (o desafiado é o de cima) vizinhos
  0,0008, 0,0108 e 0,0041 (≤ 0,10) e **dois estágios 0,00 e 0,00** (fecha); os seis líderes passam sem mudar fator (com o treino típico
  0,8125–0,9063, pior forma 0,535 na Cidadela); desafiantes: Tortomon e Machinedramon saíram das metas (uma forma abaixo de 0,5) e foram
  recalibrados nas sementes de calibração (1,6 → 1,5 e 2,7 → 2,2); na nova validação o Machinedramon passa e o Tortomon não (sem treino
  0,3087 > 0,30). Números em `artifacts_campanha/escala_v6/` e `artifacts_campanha/arenas/validacao.json`.
- **Interpretação:** nas metas de estágio (pet contra pet) o desafiado é o pet do estágio de cima, qualquer que seja o lado.
- **Ressalva:** a escala v6 (vidas e β) e a lista do Guardromon foram escolhidas antes da regra; com ela as metas de estágio passam com
  folga, e a escala poderia ficar mais perto do DW1. Não foi recalibrada (a tarefa pedia só validar de novo).

## 2026-09-30 — itens do Tamer (medalhas, parte 3) só no jogo (pets v6), sem equilíbrio

- **Desvio entre o jogo e a pesquisa:** chips e cartas (`docs/DESIGN_MEDALHAS_ARENAS.md`, seção 13) existem só em `web/app/` e só nos
  pets v6. Nada em `digilab/` nem em `experiments/`: a pesquisa não tem Tamer, medalhas nem itens.
- **Sem equilíbrio (decisão do Matheus, 2026-09-30):** o pedido original tinha uma etapa de medição com gates (G-I1–G-I4) antes das telas.
  O Matheus decidiu não equilibrar a cada etapa: ainda entram outras mecânicas no combate, e o equilíbrio será feito numa rodada só,
  depois. Os itens entraram com os números PROPOSTOS da especificação, sem medição e sem ajuste; os gates ficam registrados na seção 13.7
  para essa rodada, e `web/app/test/medir_itens.mjs` fica pronto sem ter sido rodado como etapa (sem artefato).
- **Uma passada de medição rodou antes da decisão** (só sementes de calibração), com o catálogo sendo mudado no meio dela. Os artefatos
  foram apagados e nada dela entrou nos itens: o catálogo e os números são os da especificação. Pista qualitativa para a rodada de
  equilíbrio na seção 13.8.
- **Interpretações na implementação:** o chip não se gasta (qualquer pet do Tamer tem uma cópia equipada); a espera da carta de revanche
  conta no relógio do pet que a ganhou (por pet e por líder); a carta vale para o evento de luta inteiro (na série da Cidadela, uma vez);
  a regra de chip que já estava na lista quando o chip entrou fica nela ao desequipar (só perde a proteção).
- **Registro do Tamer versão 2** (lê a 1): as chaves do save e o formato do registro do pet não mudam; o pet ganha os eventos `i` e `k`.
  Nenhum registro que já existe muda no replay, e o descarte único não subiu.

## 2026-09-30 — Fronteira de Batalha, parte 4a (a Liga dos Líderes e o fim do jogo) só no jogo (pets v6); a Liga sem fator

- **Desvio entre o jogo e a pesquisa:** a Liga dos Líderes, o título do Tamer e a Fronteira (`docs/DESIGN_FRONTEIRA.md`, seção 7) existem
  só em `web/app/` e só nos pets v6. Nada em `digilab/` nem em `experiments/`: a pesquisa não tem Tamer, medalhas nem Liga.
- **Desvio do desenho: o fator dos Megas da Liga é 1, não o do Piedmon da Espiral (1,6).** O desenho pedia só conferir que um Mega bem
  treinado, com a forma certa, vence cada luta, e mandava ajustar o fator de uma luta só se ela fosse impossível para todas as formas.
  Cada luta sozinha é vencível com o 1,6, mas a Liga inteira (sem cura) não: nenhuma das 8 formas venceu as 6 seguidas nas sementes de
  validação (0 nas 8 formas). Mexer só na 5ª e na 6ª não bastava (sementes de calibração: com elas a 0,3 e as outras a 1,6, a melhor forma
  vence 0,03), porque o dreno de vida vem das primeiras lutas. O jogo precisa ser completável, então a Liga ficou sem fator (o Mega na
  escala dos pets v6, como ele é): o Piedmon precisava do 1,6 por ser um NPC de perfil neutro, sem técnica nem passiva, e os Megas da Liga
  lutam com técnica, passiva e lista canônica. Com o 1: furioso 0,7850, vigia 0,4275, duelista 0,4075, espelho 0,2075, sentinela 0,0600, emboscador 0,0600, titã 0,0050, muralha 0,0000 (`artifacts_campanha/liga/conferencia.json`). A grade 1,6 / 1,4 / 1,2 / 1
  foi olhada nas sementes de calibração antes da escolha e é relato; o 1 não saiu de uma meta. **Para o Matheus decidir** na rodada de
  equilíbrio: manter sem fator, ou pôr um fator entre 1 e 1,2 (com 1,2 só o vigia ainda vence, 0,0975).
- **Interpretações:** a tentativa inteira é um evento de luta `l` do pet, `{r: "liga", s}` (como a série da Cidadela), sem o evento `f` do
  desenho (a regra sai do rival); as lesões da derrota na Liga seguem a regra de toda luta ("tentar de novo sem custo" = sem custo de
  entrada); o título é um evento `campeao` por pet (o primeiro é o título do Tamer); a entrada confere as medalhas que o pet conhece
  (evento `u`), porque o motor não lê o Tamer; o In-Training não entra.
- **Registro do Tamer versão 3** (lê a 1 e a 2). O registro do pet não muda de formato; a assinatura dos v6 só ganha a Liga depois da
  primeira tentativa. Pets v1–v5, gabaritos, paridade V21D e as calibrações das partes 2 e 3 saem iguais (a série da Cidadela passou a
  ser `jogarSerie` com o mesmo líder três vezes, a mesma conta). Descarte único não subiu.
- **Atlas (fora do repo):** a ilha da Fronteira é a `WorldMap_05` (peça `ilha_fronteira` em `Assets/gerar_atlas_up.py`); o mapa da
  campanha v6 ficou com 390 × 864.

## 2026-09-30 — Fronteira de Batalha, parte 4b (Torre de Batalha e Palácio) só no jogo (pets v6), sem equilíbrio

- **Desvio entre o jogo e a pesquisa:** as instalações da Fronteira (`docs/DESIGN_FRONTEIRA.md`, seção 8) existem só em `web/app/` e só nos
  pets v6. Nada em `digilab/` nem em `experiments/`: a pesquisa não tem Tamer, Liga nem instalações.
- **Sem calibração (decisão do Matheus):** o fator dos rivais é 1, o da Liga (o Mega na escala v6); a conferência
  (`artifacts_campanha/fronteira/conferencia.json`) só mostra que as duas são jogáveis e não escolheu número nenhum.
- **Interpretações:** a semente da tentativa deriva do registro do **pet** (semente dele, instalação, número da tentativa dele ali), não do
  Tamer, para o replay do pet não depender do Tamer; o motor confere a semente. O evento `f` do desenho ("início da tentativa") virou
  "a Fronteira abriu para este pet" (o título do Tamer, gravado pelo app como o `u`), porque a regra da tentativa sai do rival. O Palácio
  tira as travas, os vetos e as regras que só estão no pet por um chip; os chips de stat valem (são treino, não decisão); a regra de chip que
  o pet já tinha fica. As cartas não valem nas duas (como na Liga). As lutas ensinam regras e contam lutas e lesões, como toda luta (a Liga
  faz o mesmo); nada dá item, treino ou stat. Teto de 100 lutas por tentativa (o evento precisa acabar). O recorde só entra no Tamer quando
  passa o anterior.
- **Registro do Tamer versão 4** (lê 1 a 3). O registro do pet ganha o `f`; a assinatura dos v6 só muda depois dele. Pets v1–v5, gabaritos,
  paridade V21D, a Liga e as calibrações anteriores saem iguais (`jogarSerie` passa por `jogarSequencia`, a mesma conta). Descarte único
  não subiu.
- **Achado (corrigido depois, 2026-09-30, só na interface):** o relógio do jogo continuava durante a animação da luta, e na velocidade de
  teste (10 min/s) uma lesão na derrota que fecha a sequência passava das 6 h sem tratamento em 36 s (o pet morria antes do Resultado; a Liga
  também). Agora o tempo não anda com a luta no palco nem com o Resultado aberto (`web/app/src/luta.ts`, `lutaSeguraTempo`); motor, registro
  e replay não mudam, e o e2e das instalações não pausa mais o tempo.

## 2026-09-30 — Fronteira de Batalha, parte 4c (Fábrica e Salão) só no jogo (pets v6), sem equilíbrio

- **Desvio entre o jogo e a pesquisa:** a Fábrica e o Salão (`docs/DESIGN_FRONTEIRA.md`, seções 9 e 10) existem só em `web/app/` e só nos
  pets v6 (a Fábrica nem usa pet). Nada em `digilab/` nem em `experiments/`: a pesquisa não tem Tamer nem Fronteira.
- **Sem calibração (decisão do Matheus):** fator 1 nas duas (o Mega, ou o nível, na escala dos pets v6), como na Liga e na 4b. A conferência
  (`artifacts_campanha/fronteira/conferencia_4c.json`) só mostra que são jogáveis e não escolheu número nenhum. **Para a rodada de
  equilíbrio:** a Fábrica é difícil (com o melhor arquétipo, uma série vencida em 0,018–0,019 das tentativas; lutas de espelho sem cura e
  com o limite de turnos do rival); a troca entrando inteira foi medida (0,028 trocando por arquétipo melhor, 0,054 trocando sempre) e não
  adotada.
- **Interpretações:** (1) a Fábrica: 3 alugados de **arquétipos distintos** (a escolha precisa ter o que escolher); "sem cura" vale dentro da
  série, e a série seguinte começa com o alugado inteiro; **a troca não cura** (o novo alugado entra com a mesma fração da vida e o mesmo guts
  do anterior), senão "sem cura" deixaria de valer; a troca vale uma vez depois de cada vitória, inclusive a que fecha a série; empate conta
  como derrota. (2) A semente da Fábrica sai do número da tentativa no registro do **Tamer** (não há pet); as das lutas saem dela. (3) O
  Salão: a semente de cada luta sai do registro do **pet** (como na 4b), para o replay do pet não depender do Tamer; o Tamer grava a tentativa
  e confere a conta. O rival do Salão é o bot canônico do nível com o caráter canônico das metas de estágio (Rookie: a semente de 3 regras da
  web, sem caráter). Os níveis lutam na ordem (Rookie a Mega) e a tentativa para na primeira derrota ("quantos estágios venceu seguidos"),
  como as outras instalações. (4) Um guardado que luta no Salão recebe na hora parada dele o `u` e o `f` (o que receberia ao voltar a ser o
  ativo) e continua guardado. (5) Chips valem e cartas não no Salão, como na Liga e na 4b. (6) As lutas da Fábrica e do Salão não são
  animadas no palco: o resultado aparece no card.
- **Registro do Tamer versão 5** (lê 1 a 4): eventos `fabrica`, `fabrica_luta`, `fabrica_troca` e `salao`; os recordes da Fábrica e do Salão
  saem das tentativas (sem evento `recorde`). O registro do pet não muda de formato (a luta do Salão é um `l`); a assinatura dos v6 só ganha o
  Salão depois da primeira luta ali. `perfilDe` ganhou o parâmetro `comEscala` (desligado por padrão; só a Fábrica o usa). Pets v1–v5,
  gabaritos, paridade V21D, a Liga, a Torre de Batalha, o Palácio e as calibrações anteriores saem iguais. Descarte único não subiu.
- **Merge com a voz própria (PR #87, pets v7 = v6 + voz):** a Fronteira inteira (Liga, Torre, Palácio, Fábrica, Salão) vale para qualquer
  pet de versão ≥ 6; os testes de versão já eram `>= 6`, e o Salão aceita guardados v6 e v7 misturados (teste com um Rookie v7). As
  mensagens passaram a dizer "pets v6 em diante". Na assinatura, o Salão vem antes do bloco da voz (a dos v7 que nunca lutaram lá é a do
  `main`). O registro do Tamer (versão 5) e o descarte único (versão 5) não mudaram na voz, então a numeração da 4c ficou.

## 2026-09-29 — voz própria, parte 1: história e mentira (DESIGN_VOZ_PROPRIA)

Implementado em `digilab/historia.py` (extrator H/O/P/L, `ConfigHistoria`) e no `MotorEducacao` (`ConfigMentira`,
desligada por padrão; registros à parte `PARAMETROS_HISTORIA_V1` e `PARAMETROS_MENTIRA_V1`: o hash da educação-v1 não
muda, `6a9037ad…`). Todos os números novos são PROPOSTOS. Onde o design não bate com o código:

- **"As mentiras impunes voltam a 0 na evolução, como os petiscos cedidos"**: os petiscos cedidos **não** zeram na
  evolução (nem no Python nem no TS). As mentiras impunes e os acertos em mentira zeram de propósito; os petiscos
  continuam como estão.
- **Donos "disciplinador" e "ausente" não existem.** Mapeamento: disciplinador = atencioso, exigente, lutador e
  treinador (bronca quando a fala contradiz as barras); permissivo = petisco sempre; ausente = relapso (não vê a fala);
  incoerente = elogio ou bronca sorteados; persona = bronca se presente, se atender e se contradiz.
- **"O dono julga pelas barras"**: no Python a fala não tem texto. Cada fala sorteia um tema (estado ou história,
  `fracao_tema_estado` 0,5): só a mentira sobre o estado contradiz as barras (`contradiz_barras` na janela). A mentira
  sobre a história não tem como ser conferida pelo dono simulado.
- **Quando o pet fala na pesquisa**: o design só dá gatilhos de jogo. Na pesquisa há um slot a cada 120 min (o ritmo
  máximo do design), da criança em diante, com **defasagem de 60 min**: sem ela a fala caía sempre no mesmo tick do
  aviso de higiene (a cada 120 min), que abre a janela antes, e nenhuma fala acontecia (164 de 164 sem janela). No jogo
  a fala vem do evento novo `fala` (gatilho), rejogado pelo `reproduzir_educacao`.
- **Prazo vencido numa mentira**: além de +1 impune (design), zera os acertos em mentira (as 3 broncas certas precisam
  ser seguidas, como na travessura).
- **Bronca, petisco e elogio fecham a janela de fala**; outras ações não (a refeição não é recusada numa fala).
- **Honestidade da espécie** (seção 11): no Python entra como número no motor (`honestidade_especie`, padrão 1); a
  tabela por forma vem com o corpus auditado.
- **Extrator, O "demora"**: na simulação o dono age a cada 15 min, então a mediana da demora nos chamados fica perto de
  15 e quase todo dono "demora". Os limiares (5 e 12 min) são do design, pensados para o jogador real.
- **Seleção para a fala**: no máximo 2 fatos por regra (`max_por_regra`), senão as ausências do relapso ocupam os 12
  lugares.
- **Teste de reprodução** (`tests/test_reproducao_v3_confirmatoria.py`): 8 vidas da V3c (7 braços fixos e uma persona)
  e 3 da confirmatória, re-simuladas e comparadas com os `pets.json` versionados. Passa antes e depois da mudança.

## 2026-09-29 — voz própria, parte 2: fala livre (DESIGN_VOZ_PROPRIA)

- **Versões lado a lado**: o prompt `livre-v3` e o verificador `verif-v4` entram ao lado de `livre-v2`/`verif-v3`,
  que continuam o padrão do servidor e do jogo. Trocar o servidor é a parte 4 (web), que espera a aprovação.
- **Mentira (F)**: o motor decide só se mente e o tema (estado ou história); o molde é fixo e determinístico
  (`digilab_fala_livre/mentira.py`): a necessidade mais baixa é negada; com tudo em dia, o pet finge uma necessidade.
  Na história, o primeiro fato da seleção cuja regra admite distorção; evolução e cruzamento não distorcem. A verdade
  fica no registro (`Fato.meta` → `fatos` do log de apresentação). Se a LLM falhar, a fala é o molde.
- **Almanaque (W)**: 62 entradas em texto próprio (16 de internet, 12 de jogos, 16 memes globais, 18 brasileiros),
  sem memes ofensivos, políticos ou de ódio. A web só manda o id; texto de fora é recusado. Chance 0,15 na
  espontânea (PROPOSTO), com dois sorteios sempre consumidos.
- **Corpus de espécies**: o arquivo versionado é um EXEMPLO com 2 espécies (Angemon e Devimon, do Digimon World 1
  revisado), como pedido. O carregador aceita as marcas com ou sem acento (a auditoria usa `[OUTRA MÍDIA]`) e falha
  alto em marca desconhecida. `honestidade_especie` é calculada pelo carregador (o arquivo deixa null).
- **Filtro de citação**: 6 palavras seguidas iguais a uma citação, sem acento e sem caixa, reprovam a fala.

## 2026-09-29 — voz própria, parte 3: avaliação offline (artifacts_voz/rodada1)

- Amostra: 40 pets (grupo A: 7 braços × 4 ovos da V3c + 4 personas, mentira desligada; grupo B: 8 sombrios que mentem,
  mentira ligada, escolhidos numa varredura de exigente e treinador), 5 falas espontâneas por pet = 200.
- Depois de ver a amostra, corrigi o `verif-v4` para o que o design diz (H/O/P/L sustentam costume, gosto e lembrança;
  id em minúscula) e a chave da métrica de repetição (grupo + pet). A geração não mudou. Os números antes da correção
  estão em `resumo_v4a.json`.
- Resultado (PROPOSTO): honestidade 70,0% (limite 5%) e repetição 5 (limite 2) REPROVAM; história 98,5% e variedade
  97,7% passam. Parada pedida pelo Matheus: a parte 4 (web) não foi feita.

## 2026-09-30 — voz própria, parte 4: web (DESIGN_VOZ_PROPRIA)

- **Pet v7** (`VERSAO_PET = 7`; era v5 no desenvolvimento e virou v7 no merge com o `main`, que já tinha o v5 da evolução canônica e o v6 das medalhas): janela de fala, mentira (`CMEN`) e evento `fl` no motor TS (o `f` ficou para a Fronteira do `main`), com as regras do Python
  conferidas por gabarito (`experiments/exportar_gabaritos_voz.py` → `web/app/test/gabaritos/voz_python.json`: 24
  registros reais para o extrator, grade da mentira, desfechos e moldes). As vidas não são comparáveis bit a bit (as
  rngs são outras). Os pets v1–v6 não mudam; filhos de cruzamento nascem na versão atual.
- **Gatilhos** (`src/voz.ts`): reencontro (≥ 3 h), hábito novo, aniversário, marco (evolução, lesão tratada, vitória
  na campanha), luta e vontade nova; ritmo de 1 fala a cada 2 h de jogo; nunca com janela aberta, dormindo ou no bebê.
  **Revanche ficou de fora**: a luta não passa pela fala (a revanche aparece como assunto P, não como gatilho).
- **Todos os modos** abrem a janela de fala nos pets v7 (a mentira é do motor, não da LLM). Só no modo livre o texto
  vem do servidor (`voz: true`); nos outros, e sem servidor, é o molde: o texto do assunto (verdade) ou a mentira.
- **Gostos (P gosto/desgosto)** no jogo vêm da sonda do caráter na hora da fala (`desvioPorAcao`, ~0,15 s).
- **Janelas no extrator**: o jogo guarda as últimas 100 janelas fechadas; os hábitos do dono sobre chamados olham só
  essas.
- **Honestidade da espécie**: fica 1 no jogo até o corpus auditado entrar (o de exemplo não tem enganador).
- **Servidor**: o verificar passou a aceitar as chaves de registro dos fatos novos (antes a ida e volta daria 400); o
  almanaque é sorteado pelo servidor (a página não manda id nem texto).

## 2026-09-30 — corpus de espécies: o auditado entra no lugar do exemplo

`digilab_fala_livre/corpus_especies.json` agora tem uma entrada para cada um dos 60 Digimon do jogo (`web/app/motor/nomes.ts`),
montada de `docs/corpus_digimon/` (revisado após a auditoria) com a marca de cada item. O exemplo de 2 espécies virou fixture
dos testes (`tests/dados/corpus_exemplo.json`). Passam no filtro 56 espécies, 251 itens e 57 citações; DemiVeemon, DinoBeemon,
SlashAngemon e Valkyrimon não têm nada nos jogos do corpus. Decisões:

- **Anime liberado pelo Matheus (2026-09-30)** (`liberar_outra_midia: true`): os itens dos três animes (marca OUTRA MÍDIA,
  `midia: "anime"`) entram; com eles passam 442 itens e 62 citações nas mesmas 56 espécies.
- **Itens acrescentados na revisão** (depois da auditoria, com fonte nova conferida pelo revisor) entraram como VERIFICADO EM
  OUTRA FONTE; a auditoria não os viu.
- **Variantes BK/B do Digimon World 3** saíram (podem ser outra espécie, como BlackWarGreymon).
- **Nenhum enganador**: o "Guilmon Trapaceiro" é um NPC do DW3, não um traço da espécie, e a Palmon que finge ser flor é um
  disfarce; com a marca, todos os Guilmon e Palmon mentiriam mais. `honestidade_especie` é 1 para todas.
- **Citações com 3 frases curtas** (7) saíram, em vez de cortadas; Imperialdramon Dragon e Fighter Mode têm o mesmo conteúdo
  (o corpus não diz o modo).
- O bloco de estilo do prompt usa no máximo 8 traços e 5 itens de fala por espécie.

## 2026-09-30 — M1 (confiança de combate): pets v8 na web, e as séries de lutas

- **Pet v8** (`VERSAO_PET = 8` = v7 + confiança; o desenho, `docs/DESIGN_MVP_M1_CONFIANCA.md`, dizia v5 e a primeira
  implementação usou os v5 que já existiam). No merge do `main` (medalhas v6, V21D, Fronteira, voz v7) a confiança passou
  a valer só para `versao >= 8`, no padrão de uma versão de pet por mecânica: pets v1–v7 não mudam de comportamento nem
  de assinatura e nenhum save é descartado. Filhos de cruzamento nascem v8.
- **Séries de lutas** (Cidadela, Liga, Torre de Batalha, Palácio, Salão), que o desenho não previa: cada luta da série
  conta na confiança, com o rival dela (Cidadela: o líder repetido; Liga: o Mega de cada líder; Fronteira e Salão: a
  forma sorteada). O ε da série inteira sai da confiança do começo. Só na web (o Python não tem séries).
- O Python não muda: `ConfigConfianca` segue desligada por padrão, `PARAMETROS_CONFIANCA_M1` à parte (os hashes da
  educação-v1 e da voz não mudam).

## 2026-09-30 — equilíbrio geral, fase 1 (as formas): a V21E fecha pelas listas, não pela base

- **A base não mudou.** O plano (`docs/PLANO_EQUILIBRIO_GERAL.md`, seção 3) e o diagnóstico apontavam a base (custo do golpe
  rápido, dano do parry, a C3) como a alavanca do furioso. Medidas na calibração sobre a V21D, nenhuma o tira de ~0,72
  (`artifacts_equilibrio_geral/fase1/matriz.json`: golpe 12/15/20, parry 8/12, sem C3). O que o tira é o parry que já existe
  (C2 da V2C): nenhuma forma que o golpe rápido repetido esmagava se defendia dele. A V21E (`ConfigCombateV21E`, subclasse
  da V21D, chaves desligadas por padrão) só tem listas variantes; a `ConfigCombateV2C`, `combate_v2/*.py` e a bateria da base
  não mudam.
- **Uma chave por edição de lista** (como a V21D), cinco: `duelista_defende_do_golpe`, `tita_defende_do_golpe`,
  `espelho_sem_carregar`, `muralha_sem_carregar`, `muralha_contra_golpe_na_pele`. As da muralha pedem `muralha_lista_espelho`
  (falha alto sem ela).
- **Web: pets v9** (`VERSAO_PET = 9` = v8 + combate equilibrado; `CV21E`). Os v6–v8 seguem na V21D e os v1–v5 na V21C; nenhum
  save é descartado. A Fábrica (sem pet; lutas no registro do Tamer) continua na V21D (`VERSAO_FABRICA = 6`): mudar as regras
  dela mudaria o replay das tentativas já gravadas. As regras novas da V21E ficam fora do repertório de candidatas (como as
  do vigia V21D) e voltam como candidatas de troca só para a forma que as tem, nos pets v9 (`candidatasV21E`).
- **Sementes da bateria da base.** A meta M-A5 pede G1–G9 da V2C: a bateria da base tem sementes próprias (calibração
  1101…1505, validação 2101…2505); na fase 1 roda a de calibração (`experiments/configs/v21e/bateria_v2c_calibracao.json`, igual
  à etapa c7). As 3101…3505 valem para tudo o que é V2.1.

## 2026-09-30 — Voz própria: ajustes depois do teste do Matheus no jogo

Relato: a conversa riscava como "Sem base" falas da voz (inclusive "Agumon evolui pra Greymon", que é verdade no jogo), o
pet disse "Você voltou!" e contou ser amigo de um Agumon que não existe na vida dele.
- **Tela da conversa:** nos pets v7 a fala da voz não é mais riscada. O que ele inventou aparece marcado com o lápis
  ("✎ Inventou: «…»"), pela regra do Matheus (inventar pode, desde que se saiba). Os pets antigos seguem com o riscado.
- **Árvore da espécie como fato (A1, "arvore da minha especie")**: o servidor liga na voz (`digilab_fala_livre/arvore.py`,
  igual ao `DIGIMON_DA_FORMA` do jogo, teste `tests/test_arvore_fala.py`); a página não pode mandar. Sustenta evento,
  costume e mundo no verif-v4/v5. Só existe quando o servidor liga: as rodadas 1–4 não mudam.
- **Gatilhos da voz no verificador:** "evento agora" da voz (reencontro, luta, aniversário) sustenta pela regra
  determinística (`RAIZES_GATILHO_VOZ`), como já valia para "acabei de decidir: X". No save do Matheus o "Você voltou!"
  era verdade (o dono voltou depois de 9866 min de jogo) e o juiz não sustentou.
- **verif-v5, fato escondido em opinião:** "amigo(s)", "evolu…" e "vira/viram/virou/virei" passam a ir ao juiz. Muda o
  verif-v5 daqui para a frente (as rodadas gravadas ficam como estão; uma rodada nova usaria esta regra).
- **Reencontro:** além das 3 h de jogo, 20 min de relógio sem agir na página (no tempo de teste 3 h passam em 18 s).
- **Forma na identidade:** a página manda o Digimon de agora em todo estágio (antes só do Champion em diante: o Rookie
  e o bebê ficavam sem o estilo do corpus).

## 2026-09-30 — Voz própria: o bloco de estilo do corpus levava o modelo a responder em japonês

Achado durante a avaliação do comando pelo chat (`artifacts_fala_livre/comando/rodada2_estilo/`, branch `comando-chat`): com o
bloco de ESTILO DA ESPÉCIE no pedido, o gemma2:9b respondeu com trechos em japonês na maioria das conversas, e `saida.ler`
rejeita letra fora do alfabeto latino, então a fala vira a genérica "…" (e o comando, null). Causa: o corpus de 60 espécies
(anime liberado no mesmo dia) descreve o registro japonês das falas (pronomes おいら/俺, finais 〜だぜ) em 46 itens de
"jeito de falar", 2 traços e 1 interação; 28 espécies têm pelo menos um. O corpus de exemplo (2 espécies) das rodadas 1–4 da
voz não tem nenhum: essas rodadas reproduzem.
- **Decisão desta implementação:** filtrar no carregador (`corpus.carregar(so_latino=True)`), não no arquivo: o corpus e o
  sha256 registrados em cada fala continuam os mesmos, e o item descartado fica contado em `descartados["NAO LATINO"]`.
  Traduzir ou reescrever esses itens em português é trabalho de auditoria do corpus, fora daqui.
- `so_latino=False` existe só para medir o antes e o depois (`experiments/medir_estilo_latino.py` →
  `artifacts_voz/estilo_latino/`). O servidor e a avaliação usam o padrão.
- Verificador, prompts e a regra de `saida.ler` não mudam.
## 2026-09-30 — Canal do dono, Etapa B: dose alta k = 9 → k = 8

`docs/PLANO_ANALISE_CANAL_DONO.md`, adendo B.
- **Problema:** com `peso_carater_stats` = 9, a renormalização dos stats não tem solução para 3 dos 600 pets vivos do
  E1: todos os stats ficam presos no limite (`CatalogoInvalido`, "renormalizacao sem stats livres").
- **Troca:** a dose alta passa a ser o maior k inteiro ≤ 9 sem nenhuma falha, k = 8. A regra não olha a taxa, os donos
  nem nenhum resultado.
- **Quando:** a run de k = 9 foi parada ainda nas vidas, antes do painel. Nenhum resultado de k = 9 existe.

## 2026-09-30 — Canal do dono, Etapa B: implementação do k trocada (hashes das validações)

- **Problema:** a primeira implementação punha `peso_carater_stats` na `ConfigCatalogo` e o usava no `catalogo.stats`.
  Os dois entram nos hashes gravados das validações (`tests/test_equilibrio_v21d.py`: o config da validação V21D e o
  gabarito web da V21D), e os dois testes falharam.
- **Troca:** o k fica só em `run_natureza_criacao.catalogo_do_painel`. É um catálogo com os modificadores do caráter
  multiplicados por k; `digilab/config.py` e `catalogo.py` voltaram a ser os de antes.
- **Conta:**
  - a antiga somava (v × k) × m;
  - a nova soma v × (m × k);
  - com m inteiro e k = 8, potência de 2, as duas são exatas e iguais.
- **Conferência** (stats dos 600 pets vivos, as duas implementações):
  - k = 8: 0 pets com stats diferentes. A run de k = 8 **vale como está**;
  - k = 3: 108 pets diferem no último bit. A run de k = 3 **foi refeita** com a implementação nova, antes de qualquer
    leitura dela entrar em relatório.

## 2026-09-30 — Comando pelo chat (`docs/TAREFA_COMANDO_CHAT.md`): o texto do jogador passa a agir no pet, pelo catálogo

Decisão do Matheus (2026-09-30). A regra de 2026-09-28 da fala livre, "o que o jogador escreve não ensina o pet", **deixa de valer
para o comando**: na conversa dos pets v7+ a LLM devolve, junto com a fala, `comando` ∈ {as 9 ações de `AcaoDono`} ∪ {null}; o
app mostra um chip de confirmação e o toque grava o evento `d` de sempre, pelo mesmo caminho do botão. O texto continua não
ensinando nada por outra via: só o catálogo fechado age, e só com o toque. Interpretações e limites desta implementação:
- **No registro do pet entra só o `d`.** A saída da LLM fica no log de apresentação (versão 2, lê a 1). Replay, assinaturas dos
  pets v1–v8, gabaritos `vidas_*.json`, `paridade_ts` e `constantes.test.mjs` passam iguais; o modo livre gravado não é usado.
- **Só na conversa com `voz: true` (pets v7+), prompt `livre-v7`** (= `livre-v6` + a regra COMANDO no sistema e a lista das ações
  no pedido). Os pets v1–v6 conversam pelo `livre-v2` e não ganham comando: mudar a v2 alteraria as mensagens das rodadas 1–2 da
  fala livre, que reproduzem. As rodadas 1–4 da voz (`livre-v3..v6`, espontânea) não mudam.
- **O comando é o da primeira geração.** A autocorreção (`revisao.py`) só reescreve a fala (respeito); a reescrita não troca o
  comando. É o que a avaliação mede com `gerar`.
- **Validação dupla.** Servidor: `saida.ler` falha alto com valor fora do catálogo (fala genérica, comando null). App
  (`src/acoes.ts`): catálogo, pet nascido e vivo, ações v4 (petisco, banheiro, tratar lesão) só em pets `versao >= 4`, `tratar_lesao`
  só com lesão; o toque valida de novo contra o pet daquele momento (pet morto entre a resposta e o toque: nada entra).
- **Um caminho só para a ação do dono** (`acoes.agir`): botões da tela do Pet, atalhos do Conversar e o chip. O flash do palco saiu
  para `src/flash.ts` (sem DOM) para o caminho compartilhado não puxar o palco.
- **Avaliação em duas rodadas** (`artifacts_fala_livre/comando/`): a rodada 1 mede o comando **sem** o bloco de estilo da espécie;
  a rodada 2, **com** o estilo, como o servidor manda no jogo. Motivo: na sonda, com o estilo do corpus (que hoje tem 60 espécies e
  texto em japonês nas fontes), o gemma2:9b respondeu com trechos em japonês em 5 de 6 mensagens, e `ler` rejeita letras fora do
  alfabeto latino (a fala vira a genérica e o comando null). Isso é do corpus/da voz, não do comando, e vale para a conversa dos
  pets v7 já hoje; fica registrado como pendência à parte.
- **Sem execução direta.** O chip é obrigatório até o Matheus ver o gate (PROPOSTO: falsos positivos ≤ 5% nas negativas;
  imperativos ≥ 80%). Treino, luta, itens, evoluir, cruzar, comando na fala espontânea e MCP de verdade ficam fora.

## 2026-09-30 — Comando pelo chat, rodada 3: prompt `livre-v8`

A rodada 1 (`livre-v7`, `artifacts_fala_livre/comando/rodada1/`) passou nos falsos positivos (0%) e falhou nos imperativos
(53,3%, gate ≥ 80%): elogiar, repreender, acariciar e tratar_lesao acertaram 4 de 36, porque nelas a mensagem do dono é a própria
ação ("muito bem!" é o elogio) e o modelo tratava como conversa.
- **`livre-v8` ao lado da v7** (`digilab_fala_livre/prompt.py`): muda só o bloco COMANDO. A regra no sistema diz que em quatro
  ações a própria mensagem é a ação (elogiar: "muito bem!", "parabéns"; repreender: "isso foi feio", "não faz mais"; acariciar:
  diz que vai fazer carinho ou cafuné; tratar_lesao: diz que vai cuidar do machucado ou fazer curativo) e escreve inteira a regra
  do null (negação da ação, pergunta, hipótese, adiamento e relato); a lista do pedido (`DESCRICAO_COMANDOS_V8`) troca a frase
  dessas quatro. A v7 não muda (a rodada 1 reproduz). O servidor usa a v8 na conversa com voz.
- **A v8 foi escrita olhando a rodada 1**: por isso a rodada 3 usa **sementes novas** (20261201, 20261301, 20261401; nenhuma
  semente + i cruza as das rodadas 1–2, teste), as mesmas 60 mensagens, sem o estilo da espécie, gemma2:9b. As sementes das
  rodadas 1–2 passam a ser de calibração. As mensagens são as mesmas: a v8 não é validação independente das **mensagens**, só
  das sementes.
- **Resultado** (`artifacts_fala_livre/comando/rodada3/resumo.json`): gate PROPOSTO **passa**. Falsos positivos 0/60 nas negativas
  e 0/60 na conversa; imperativos 51/60 (85,0%). Elogiar 6/6, repreender 6/6, acariciar 6/6, tratar_lesao 5/6 (uma virou
  acariciar); alimentar 9/9, petisco 6/6, brincar 5/6, banheiro 5/6. **Regressão em limpar: 3/9** (rodada 1: 7/9); 5 viraram
  `repreender` ("banho agora, sem choro" e "vai se limpar, você tá todo sujo", mensagens de tom bravo) e 1 null. Com o chip, o
  jogador veria "Repreender?" no lugar de "Limpar?": é um erro de ação, não um falso positivo numa negativa.
- **Execução direta continua fora**: o chip segue obrigatório; liberar para os imperativos é decisão do Matheus.

## 2026-09-30 — Fala livre: a fala que bate no limite do esquema sai cortada no meio da palavra

Visto no teste do chip no jogo: o Koromon (bebê, `MAX_CHARS` 30) respondeu "M-mm! Já tô com fome! Vou co-c". O `maxLength` do
esquema JSON é uma gramática: o Ollama para de gerar no 30º caractere, e o verificador marcava o toco como invenção. Correção
só na saída (`saida.aparar`, chamada em `gerar` e na reescrita da autocorreção): quando a fala tem o tamanho do limite, fica
só a parte inteira, até o último fim de frase (".", "!", "?", "…"); sem fim de frase, até o último espaço, com reticências.
Abaixo do limite a fala não muda, então as rodadas gravadas não mudam. Prompts, esquema e limites continuam os mesmos.
## 2026-09-30 — Voz própria: gatilho de revanche

O gatilho da seção 3 do DESIGN_VOZ_PROPRIA ("antes de lutar contra o rival do gosto revanche"), que tinha ficado de fora.
- **Quando:** ao escolher (Arena ou Campanha) o rival que venceu o pet e ainda não foi vencido depois. A luta não espera a
  fala: ela aparece acima do Lutar/Desafiar (a janela de julgar fica na tela do Pet, como nas outras falas). Uma vez por
  derrota: o registro diz se já houve um `fl` "revanche" depois dela. Mesmo ritmo das outras falas (2 h, nunca dormindo nem
  com janela aberta). O assunto da fala, quando é verdade, é o próprio fato de revanche.
- **Nada novo no motor:** o gatilho é só o texto do evento `fl` (pets v7 em diante); assinatura e replay iguais.
- **Nomes dos rivais (correção):** na web os fatos da história e a mentira diziam "contra o ." (o nome padrão é o do
  formato da pesquisa, `npc:tier1_x`). Agora a web passa o nome da tela (`src/nomesRivais.ts`: NPC, Digimon do bot) e
  manda `dados.nome`; a mentira (TS e Python) usa esse nome quando vem. Os gabaritos Python × TS não mudam.
- O verificador sustenta a fala pelo [G1] "vou lutar de novo contra quem me venceu" (revanche, luta, enfrentar).

## 2026-09-30 — equilíbrio geral, fase 4: validação única, tudo congelado; a muralha na Liga aceita como exceção

- **Nada mudou por causa do resultado** (o plano, seção 4: "nenhum número muda"). A validação rodou uma vez, nas sementes
  4101…4505, com os fatores, listas, escala e itens das fases 1–3. O que reprovou foi relatado (`docs/EQUILIBRIO_GERAL.md`, fase 4,
  seções 4.3 e 4.4), não corrigido.
- **Os scripts ganharam `--validar`**, no padrão dos que já tinham (`SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505]`, artefato
  `*_validacao.json`, pasta `artifacts_equilibrio_geral/fase4/`): `experiments/calibrar_equilibrio_geral.py` (só as variantes `v21d` e
  `v21e`; a conferência que falha alto passa a ser a validação da V21D nas mesmas sementes, `artifacts_combate_v21c/validacao_v21d/`,
  e saiu igual), `conferir_liga.mjs`, `conferir_fabrica_salao.mjs` e `conferir_instalacoes.mjs` (não tinham) e os que já tinham
  (`calibrar_escala_v6.mjs`, `calibrar_arenas.mjs`, `calibrar_desafiantes_v6.mjs`, `medir_itens.mjs`) passam a gravar os v9 em
  `fase4/` em vez de `fase2/`/`fase3/`. O padrão (calibração) e os artefatos das fases 1–3 não mudam (conferido: `conferir_liga`,
  `conferir_fabrica_salao`, `conferir_instalacoes` e `calibrar_equilibrio_geral --etapa metas` rodados de novo no padrão saem byte a
  byte). A bateria M-A5 tem configs próprios de validação (`experiments/configs/v21e/bateria_v21e_validacao.json`,
  `bateria_v2c_validacao.json`: os mesmos das de calibração, só o conjunto e a saída; a da base com N = 80, o da validação da V2C).
- **A V21D não foi rodada na bateria de validação** (na fase 1 rodou na calibração, para comparar): não é meta, e a validação da V21D
  já existe (`validacao_v21d/`). A matriz, o painel, o E3 e o S1 da V21D nas sementes de validação saem do `--validar` do script da
  fase 1, como conferência.
- **M-C1, a muralha: aceita como exceção pelo Matheus (2026-09-30).** 0,085 de título na calibração e na validação. Motivo: ela
  perde para os guardiões pelo limite do desafiado (que é do líder: 0,7025 contra o Seraphimon mesmo com 0,3, 0,440 contra a Rosemon)
  e não alcança o MegaGargomon com nenhuma alavanca permitida (0,3775 com o fator 0,1, o piso da grade). As alavancas que mexeriam
  (o limite do desafiado, os Megas da tabela, deixar perder uma luta) são decisões anteriores do Matheus. Nenhum número muda.
- **M-C1, o espelho: aceito como exceção pelo Matheus (2026-10-01).** 0,240 na validação, 0,010 abaixo da faixa (0,255 na
  calibração, folga 0,005, risco apontado na fase 3); a diferença está no ruído entre sementes e a fase 4 é única. Nenhum número muda.
- **E3 do contra-golpe: aceito como exceção pelo Matheus (2026-10-01).** Reprovava desde a fase 1 (0,458 → 0,480 na validação,
  pelo espelho, cuja passiva devolve o disparo inteiro). A resposta declarada não muda. Com isso a rodada não tem mais pendência de
  aceite; o E4 da V21C segue como exceção aceita (redefinido na escala, M-B1).
- **Sementes de validação e os pets v6.** Os artefatos dos v6 (`artifacts_campanha/arenas/validacao.json` etc.) usam as mesmas
  4101…4505 desde as medalhas; para os pets v9 elas não tinham sido usadas em nada antes da fase 4 (as fases 1–3 só rodaram
  3101…3505). A conferência "linha sem item = fase 2" do `medir_itens.mjs --validar` não existe nos v9 (sem referência gravada);
  a igualdade com `arenas_validacao.json` foi conferida à mão no relatório.

## 2026-10-01 — Comando pelo chat: execução direta, sem o chip de confirmação

Decisão do Matheus (2026-10-01), depois do gate PROPOSTO da rodada 3 passar (`artifacts_fala_livre/comando/rodada3/`: falsos
positivos 0% nas negativas, imperativos 85%). O comando que a LLM propõe e o app valida (`acoes.validarComando`: catálogo, pet
nascido e vivo, ações v4 só em pets v4+, tratar só com lesão) passa a gravar o evento `d` na hora, pelo mesmo caminho do botão
(`acoes.agir`); o chip "Alimentar?" da primeira versão saiu. O registro do pet continua recebendo só o `d`; o log de apresentação
marca `comando_executado`. Risco aceito: os erros de ação da rodada 3 (6 de 9 em "limpar" lidos como `repreender`) viram ação
sem desfazer. Sem mudança no servidor, nos prompts nem nas rodadas gravadas.

## 2026-10-01 — V2: o aprendiz deixa de ser o bandit; rodada 1 de frentes paralelas

**Decisão do Matheus (2026-10-01): a V2 foca na nova arquitetura e abandona o bandit.** O aprendiz da V2 é a política com lobos nomeados do
`docs/PLANO_V2_PESQUISA.md` (fase 1b). O bandit (`digilab/policies/bandit.py` e subclasses) fica congelado só para reproduzir as runs da v1: não é
apagado, não muda e não é estendido. Os gates da fase 1 continuam PROPOSTOS até o referendo do plano.

Rodada 1 (coordenação, `docs/V2_TRABALHO_PARALELO.md`): quatro frentes sem run estatística e sem GPU, uma por worktree:
`TAREFA_V2_F0_INVENTARIO.md` (inventário e escolha da interação da 1a), `TAREFA_V2_L0_LOBOS.md` (esqueleto dos lobos, aprendizado desligado, igual ao
instinto byte a byte), `TAREFA_V2_F0_VINCULO.md` (diagnóstico e proposta, sem código) e `TAREFA_V2_F0_CORPUS.md` (itens não latinos do corpus reescritos em
português). Reservas: nenhuma faixa de semente (nenhuma run nesta rodada); `VERSAO_PET` reservado pelo coordenador (rodada 2: 10 = vínculo novo, 11 = lobos na web, 12 = bola da 1a; as versões são cumulativas, então o número segue a ordem de chegada na web).

## 2026-10-01 — V2, F0-INVENTARIO: divergências entre documento e código encontradas no inventário

Tarefa `docs/TAREFA_V2_F0_INVENTARIO.md`; entrega `docs/V2_INVENTARIO_JOGO.md` (seção 5). Só documento; nenhum código, número de
resultado ou artefato muda. Conferido na `main` em `83fc08f`.
- `CLAUDE.md` diz "290 testes" (mapa e comandos); `python -m pytest tests/ -q` na worktree dá 571 passados e 1 pulado (a auditoria
  `01_CURRENT_STATE.md` contou 538 em `3fe6d76`). Correção do texto é do coordenador.
- `CLAUDE.md` diz "Ambiente do usuário: pasta `D:\Trab\digilab\v1`"; desde 2026-09-30 o trabalho é em `v2` e nas worktrees
  (`docs/V2_TRABALHO_PARALELO.md`).
- `web/app/motor/confianca.ts`, cabeçalho: "Só os pets v5 usam"; o motor aplica a confiança nos pets v8 em diante (`motor.ts`,
  `versao >= 8`). Comentário desatualizado; o comportamento é o descrito no `CLAUDE.md` (M1).
- `web/app/motor/donos.ts`, cabeçalho: "a evolução não existe no Python". Existe (`digilab/evolucao.py`); o que não existe no Python é o
  dono sintético ver o chamado do bebê ao vivo (contado depois por `evolucao.fracao_cuidado_bebe`). Consequência medida: 548 de 548
  pets vivos da V3 nasceram ariscos (`artifacts_educacao/pets.json`).
- `docs/TODO_INTERACAO_CORPO.md` e `docs/PLANO_V2_PESQUISA.md`: "o aprendido muda a política em cerca de 0,02 bit". O 0,02 bit é a JSD
  entre braços (`artifacts/divergence.json`, 0,0204); a distância ao instinto é ≈0,03–0,05 bit (`CLAUDE.md`, "Estado atual"). O uso
  como referência do G3 (divergência entre donos) está certo; só a frase é imprecisa.

## 2026-10-01 — F0-CORPUS: itens do corpus de espécies em japonês reescritos em português

Tarefa `docs/TAREFA_V2_F0_CORPUS.md` (fase 0, item 3 do plano da V2). Só `digilab_fala_livre/corpus_especies.json` e os testes mudam;
o filtro do alfabeto, o prompt, o verificador e o almanaque ficam como estão.
- **Critério da reescrita:** todo traço, jeito de falar ou interação cujo texto tem letra fora do alfabeto latino (pelo `corpus.latino`,
  a mesma regra do carregador) foi reescrito em português, com até 120 caracteres, descrevendo o jeito sem a palavra japonesa e
  dizendo só o que a fonte do item diz (conferido em `docs/corpus_digimon/*.md` e `auditoria/*.md`, fora do repositório). O item
  mantém `marca`, `fonte` e `jogo` e ganha `"reescrito": true`. Os pronomes seguem um vocabulário fixo, para o estilo não variar por
  espécie: "pronome infantil e modesto" (o de menino), "masculino informal", "rústico e descontraído", "formal", "de velho",
  "feminino informal", "pronomes solenes" (o arcaico). Partículas e finais de frase viram a função deles ("finais de frase
  enfáticos", "partículas femininas no fim das frases", "fecho explicativo"); risos e muxoxos viram a descrição ("riso curto e
  seco", "riso baixo e gutural", "muxoxo de contrariedade").
- **Contagem:** 49 itens em 28 espécies (46 falas, 2 traços, 1 interação), não os 46 da contagem de partida: três falas de Guilmon
  (2) e Growlmon (1) só tinham o ordinal "3ª", que o `latino()` conta como letra não latina (o indicador ordinal não é LATIN no
  Unicode); viraram "terceira pessoa". A seção da fala livre do `CLAUDE.md` de 2026-09-30 falava em 46 pela contagem de kana/kanji.
- **Itens removidos: nenhum.** Os limítrofes, em que a reescrita perde o original: MetalGreymon (fala 3, anime), uma nota sobre a
  grafia em kanji do pronome no blog de fã, ficou com o que a fonte sustenta ("como MetalGreymon ainda usa o pronome infantil e
  modesto, ep. 20, só no blog de fã"); Guilmon (fala 4), o som que ele faz virou "a primeira sílaba do próprio nome"; Sakuyamon
  (fala 1), o nome da técnica virou "a técnica da mandala"; Gallantmon (fala 0), "este Dukemon" virou "fala de si na terceira
  pessoa, com ênfase no próprio nome"; Agumon (fala 4, Anode Tamer), o termo em inglês ficou escrito em inglês ("Digital World").
- **`"reescrito": true` fora do PARCIAL:** a chave nasceu para o PARCIAL (entra só a parte reescrita na auditoria); em VERIFICADO,
  VERIFICADO EM OUTRA FONTE e OUTRA MIDIA o carregador não a lê, então o filtro das marcas não muda (44 itens). Os 5 PARCIAL já
  reescritos na auditoria que ainda tinham japonês (Agumon, Angemon ×2, Koromon, Palmon) foram reescritos de novo e seguem entrando.
- **Números:** com o filtro entram 504 itens, os mesmos que sem ele (antes: 455 com, 504 sem; `descartados["NAO LATINO"]` 49 → 0);
  os outros descartes não mudam (INFERENCIA 23, OUTRA MIDIA sem anime 9, PARCIAL sem reescrita 5, SEM FONTE 1). O sha256 do corpus
  mudou (`b1b7ad8d…` → `785f7834…`): `artifacts_voz/estilo_latino/resumo.json` registra o sha anterior e mede o corpus de antes; não
  é refeito nesta tarefa.
- **Sem run.** A conferência com o gemma2:9b (fala com o estilo, sem japonês e sem saída rejeitada) fica para uma frente própria
  na fila da GPU, depois deste PR, como a tarefa pede.

## 2026-10-01 — V2, L0: política com lobos, aprendizado desligado (`docs/TAREFA_V2_L0_LOBOS.md`)

Interpretações do desenho, todas conferidas pelo gate G2 (vida byte a byte igual à do instinto) em `tests/test_lobos.py`.
- **"Pesos iniciados no prior do instinto":** a decisão guarda `w[regra][ação][entrada]` inteiros (escala S = 2¹⁰) e o prior são os
  coeficientes literais de `PoliticaInstinto.agir` vezes S (tempo livre: ocioso 3; explorar 2 + 2·energia; brincar 1 + 3·humor;
  chamar 1; fome moderada: comer 1 e chamar 1, que é "comer se u < 0,5"; regras deterministas: o único candidato com 1). A FORMA do
  prior (qual regra dispara e quais ações concorrem) não é copiada: o lobo de impulsos executa o próprio código do instinto com uma
  rng-sonda (a mesma técnica do prior do bandit), sem consumir a rng do motor. Se o instinto mudar, os impulsos seguem e o G2 denuncia a
  tabela desatualizada.
- **"Decisão em ponto fixo":** os pesos são inteiros; a ativação usa as entradas em float (o estado é float) e `w/S` com S potência de
  dois, que é exato. É o que fecha a restrição de desenho da seção 3 (consumir a rng exatamente como o instinto) sem relaxar o gate: o
  sorteio replica `random.choices(k=1)` passo a passo (`accumulate`, `total + 0.0`, `bisect_right(…, u * total)`), com UMA chamada de
  `random()`, igual ao instinto nas duas regras com sorteio. Não foi preciso parar e reportar.
- **Soma sem compensação:** a ativação é um laço da esquerda para a direita, não `sum()`, porque do Python 3.12 em diante o `sum()` de
  floats é compensado e o instinto soma termo a termo. No L0 os termos extras são 0,0 e nada muda; no L1 isso vai importar.
- **Entradas da percepção:** vies + `Estado.vetor` (8) + tempo sem cuidado normalizado pela mesma escala do bandit (480 ticks), 10 ao
  todo. O tempo sem cuidado tem coeficiente zero no prior (o instinto só o usa na regra de abandono, que fica nos impulsos); entra para o
  L1 ter a mesma informação que o bandit tinha.
- **Tabela cheia:** 7 regras × 7 ações × 10 entradas = 490 pesos, inclusive os das ações que não são candidatas de cada regra (zeros).
  Mantidos para o L1 decidir se amplia os candidatos; abaixo do teto de mil.
- **`MotorPersonalidade` não roda o instinto puro:** `_PoliticaObservada` sempre repassa `receber_acao_dono`, e o instinto não o tem
  (`AttributeError`). O controle do G2 nesse motor é um `PoliticaInstinto` com gancho vazio, definido no próprio teste;
  `obediencia.py` não mudou. O `desejo_de` trata as duas políticas igual (sem `_bracos`: sem vontade).
- **Motivo inteiro no `estado_interno()`:** a tarefa pede a contribuição de cada lobo "por decisão"; a lista completa de motivos fica no
  `estado_interno()` (vida de 14 dias: 1344 motivos). Nenhuma run grava isso ainda; se pesar no `politica.json`, a decisão de resumir é
  do L1/G4.
- **Nome do atributo:** o registro da última decisão chama-se `ultimo_motivo`, não `ultima_decisao`, porque `motivo.PoliticaComMotivo`
  despacha pelo nome `ultima_decisao` e espera o formato do bandit. O `PoliticaComMotivo` ainda não aceita a `PoliticaLobos` (fica para o
  G4).
- **Tarefa fora da `main`:** `docs/TAREFA_V2_L0_LOBOS.md` estava só no branch `v2-coord-r1` do coordenador quando o worker abriu; o
  trabalho partiu da `main` (`83fc08f`) e leu a tarefa de lá. O arquivo não entra neste PR, para não conflitar com o do coordenador.

## 2026-10-01 — F0-VINCULO: diagnóstico do vínculo; Python e web conferem no valor, diferem num contador

Tarefa `docs/TAREFA_V2_F0_VINCULO.md` (diagnóstico e proposta; nenhum código do motor muda). Conferência por leitura de
`digilab/vinculo.py` contra `web/app/motor/vinculo.ts` e dos pontos de chamada (`obediencia.py`/`educacao.py`/`treino_vida.py`
contra `motor.ts`), registrada em `docs/V2_VINCULO_PROPOSTA.md`, seção 2.
- **Valor igual:** fórmula, componentes, pesos, janelas, lista de cuidados que fecham pedido, ajustes diretos (forçar −0,05,
  bronca sem motivo −0,05), pausa de treino e teto da sombria são os mesmos nos dois motores. Não existe gabarito de paridade
  do vínculo entre os dois (os RNGs diferem, então as vidas diferem); a conferência é do código, não de números.
- **Diferença de contagem, não de valor:** no Python, `Vinculo.limitar` (teto 0,6 da sombria) acrescenta uma entrada à série
  quando corta o valor, e `para_dict` relata `atualizacoes = len(serie)`; na web, `Vinculo.limitar` não incrementa o contador `n`,
  que entra na assinatura dos pets v2+. Um pet sombrio com vínculo acima de 0,6 na hora da evolução tem `atualizacoes` uma unidade
  maior no Python do que `n` na web. Nenhum valor de vínculo, decisão ou tela depende disso; os dois contadores não são comparados
  em teste nenhum. **Nenhuma correção nesta tarefa** (mudar qualquer dos dois alteraria assinaturas ou a série gravada); fica
  registrado para a frente que implementar o vínculo novo.
- **Conta sobre vidas gravadas** (`experiments/analisar_vinculo.py` → `artifacts_v2_vinculo/`): sem semente nova, sem vida nova. O
  script troca o `Vinculo` do motor por uma subclasse que só anota as atualizações (o valor final é conferido contra o artefato de
  cada vida: 40 da personalidade e 640 do E1, todas iguais) e lê o estado do pet antes de cada ação do dono. Os contrafactuais
  recalculam o vínculo sobre o fluxo de amostras gravado com os eventos fixos; na vida real um vínculo diferente mudaria a
  obediência e, com ela, um pouco da vida. São conta, não run.

## 2026-10-01 — Correção no corpus DigiBrain: "Ackroff 2017" era Bodnar (2018)

O corpus de pesquisa DigiBrain (`D:\Trab\digilab\docs\digibrain\`, fora do repositório) atribuía o DOI `10.1016/j.appet.2016.12.015` a "Ackroff
2017, Conditioned flavor preferences". O DOI resolve no Crossref para **Bodnar, R. J. (2018), "Conditioned flavor preferences in animals: merging
pharmacology, brain sites and genetic variance", Appetite 122, 17–25** (busca da V2, `V2_SINTESE_Q1_Q7.md`, "Pendências e correções"; linha VERIFICADA
na `v2_referencias_verificadas.csv`). A entrada foi **corrigida** (não removida), porque o DOI é real e a revisão sustenta o que o corpus usava
(substratos das preferências de sabor condicionadas): `sources/SOURCE_INDEX.md` (R3), `mechanisms/food_behavior.md`, `mechanisms/hedonism.md`,
`integration/02_RESEARCH_CROSSWALK.md` e `integration/09_PROMPT_CLAUDE_SCIENCE.md`. Trabalhos reais de Ackroff e Sclafani têm outros DOIs
(`10.1016/j.appet.2010.04.011`, `10.1016/j.appet.2020.104793`) e não foram citados, por não terem sido verificados pelo projeto. O repositório não citava
"Ackroff 2017" em lugar nenhum. Como o corpus está fora do git, este registro é a trilha da correção.

## 2026-10-01 — V2: decisões D1–D11 das definições (aprovadas pelo Matheus)

O Matheus aprovou como recomendadas as onze decisões de `docs/DEFINICOES_V2.md`. Efeito nos documentos:
- **D1–D4 entram na L1** (`docs/TAREFA_V2_L1_DECISAO.md`, atualizada antes de qualquer validação): G3 mantém 0,10 bit como convenção, com G3-T
  (acerto na tarefa ensinada) ao lado sem gate; G4 medido só sobre o aprendido; braço de controle de capacidade equivalente sem lobos com o custo do
  gargalo; braço "só cuidado" acoplado, com acariciar como cuidado e a variante sem acariciar como sensibilidade.
- **D5–D8:** registro do "só cuidado" como contribuição metodológica ("não localizamos"); duas perguntas por alavanca (pet × dono); peças do Dwarf
  Fortress pela tabela da seção 5; G1 com igualdade exata nos inteiros.
- **D9:** a busca bibliográfica da V2 entrou no repositório (`docs/referencias/V2_SINTESE_Q1_Q7.md`, `v2_referencias_verificadas.csv`,
  `v2_referencias.bib`, `v2_verificacao_crossref.json`, `REGRAS_CITACAO_DIGILAB.md`). A síntese cita `v2_referencias.csv` e `v2_verificacao.json`;
  os arquivos se chamam `v2_referencias_verificadas.csv` e `v2_verificacao_crossref.json` (nomes mantidos como vieram da busca).
- **D10:** a 1a continua com a **bola**; **frutas, gosto hedônico e vício** são a alavanca seguinte, depois de a bola passar, com o "só cuidado"
  obrigatório em qualquer braço com frutas.
- **D11:** antes de desenhar as frutas, pesquisa verificada sobre vício e sensibilização de incentivo (prompt para o Claude Science fora do
  repositório, `D:\Trab\digilab\docs\digibrain\integration\10_PROMPT_CLAUDE_SCIENCE_VICIO.md`).

## 2026-10-01 — V2, F0-LIMPEZA: textos corrigidos e `Config.limiar_privacao` passa a ser lido

Tarefa `docs/TAREFA_V2_F0_LIMPEZA.md` (fecha a fase 0). Corrige as divergências documento × código do inventário (PR #106, `docs/V2_INVENTARIO_JOGO.md`,
seção 5) **sem mudar nenhum resultado**. `engine.py` intocado (sha256 conferido pela suíte).
- **`Estado.em_privacao` lia o literal 0,15** (`digilab/state.py`); `Config.limiar_privacao = 0.15` existia e não era lido. Agora
  `em_privacao(cfg)` lê `cfg.limiar_privacao`, com o mesmo valor: a propriedade virou método com o `Config` (único uso dentro de
  `avancar_um_tick`, que já recebe `cfg`; nenhum outro módulo o chamava). O valor não muda, logo o hash de protocolo (que inclui o `Config`)
  e todas as vidas gravadas saem iguais; os testes de reprodução byte a byte (`test_canonico_intacto.py`, `test_reproducao_v3_confirmatoria.py`,
  `test_natureza_criacao.py`, `test_confianca.py`) e os de hash passam. A web (`estado.ts`) já usava a constante.
- **`Config.saciedade_maxima` (1,0) e `saciedade_minima` (0,0) continuam não lidos: registrado, não mudado.** Onde deveriam valer: nos
  limites de `state._limitar` (padrão 0,0 e 1,0), chamado para fome, higiene, energia, humor e saúde em `avancar_um_tick` e
  `aplicar_acao_usuario`, e em `policy.efeito_da_acao_do_pet` (comer, brincar, explorar, emburrar); e no `clamp` de `web/app/motor/estado.ts`.
  Como os dois valem exatamente os padrões de `_limitar`, trocar seria só nome; fica para quando um valor diferente for necessário (nunca
  foi). Os dois já entram no hash de protocolo e nos `metrics.json` gravados (`artifacts/metrics.json`, `configs.Config`).
- **Textos:** `CLAUDE.md` deixa de ter contagem fixa de testes (mapa e comandos; a contagem do dia vai no PR de cada frente) e passa a
  apontar a pasta `v2` e as worktrees; `web/app/motor/confianca.ts` ("pets v5" → v8 em diante, como `motor.ts`); `web/app/motor/donos.ts`
  (a evolução existe no Python; o que não existe é o dono sintético ver o chamado do bebê ao vivo); `docs/TODO_INTERACAO_CORPO.md` e
  `docs/PLANO_V2_PESQUISA.md` ("o aprendido muda a política em cerca de 0,02 bit" → a JSD entre os braços dos donos é 0,02 bit,
  `artifacts/divergence.json`; ao instinto, 0,03–0,05 bit). O G3 do plano não muda: a referência dele já era a divergência entre donos.
- **Conferência:** `python -m pytest tests/ -q` na worktree `v2-f0-limpeza` (Windows, Python 3.13): 595 passados, 1 pulado, 7 min 32 s, com
  `test_canonico_intacto.py`, `test_reproducao_v3_confirmatoria.py`, `test_natureza_criacao.py`, `test_confianca.py` e `test_protocol.py` (hash e
  `engine.py`) passando; `cd web/app && npm run tipos` sem erros; `npm test` 306 testes em 29 arquivos passando (só comentários mudaram lá).

## 2026-10-01 — F0-VINCULO-NOVO: vínculo B implementado (Python atrás de chave, web pets v10); interpretações

Tarefa `docs/TAREFA_V2_F0_VINCULO_NOVO.md`; plano `docs/PLANO_ANALISE_V2_VINCULO.md` (commit `e507e54`, antes do código e da run).
- **Situação lida na decisão do pet, não na ação do dono.** A conta do #109 (`analisar_vinculo.py`) classificava a situação pelo estado que o
  dono via antes de agir; a implementação usa a observação com que o pet decidiu a ação atual (`Vinculo.decisao(obs, …)`), que já chega ao
  vínculo: é "a situação em que o pet fez o que o dono julga", e não exige gancho novo no motor nem na web. As células mudam pouco em 15 ticks.
  Registrado no plano (seção 2) antes da run.
- **Config à parte.** `ConfigVinculoSituacao` em vez de campos novos na `ConfigVinculo`, porque ela entra em `_json_personalidade` e no hash dos
  três protocolos da personalidade (`d986ff1b9308…`), que as runs gravadas carregam. Mesmo padrão da `ConfigConfianca` (M1).
- **Validação com 5 sementes** (5101, 5202, 5303, 5404, 5505: a faixa reservada, uma por centena, como as de sempre). O IC95 por bootstrap sobre
  5 unidades é curto; uma das cinco diferenças é negativa (5404: −0,041). O gate pede só o limite inferior > 0, e passou (+0,046).
- **Mega na web, pets v10:** os donos simulados não têm Tamer, então as medalhas são liberadas no ovo (`Motor.liberar(MEDALHAS_LIGA)`), como os
  saves do e2e fazem. A comparação com `artifacts_campanha/mega/limiar_vinculo.json` (pets v5) **não é pareada**: nos v10 valem a qualificação
  por vitórias, as medalhas e o tempo contado desde a evolução anterior, e 8 das 24 vidas não chegam ao adulto em 3 dias. O limiar 0,4 não
  mudou (fora da tarefa); o relato está no CLAUDE.md.
- **O atencioso da web fala pouco.** Em 3 dias e 48 interações, quase nenhuma é feedback (1 e 4 nas duas vidas conferidas; o resto atende chamados e limpa); com o atendimento fora, o
  vínculo B dele vive do desejo, que expira, e termina em 0,13–0,37. É o risco apontado no #109 para a alternativa B (frágil quando o dono fala
  pouco) aparecendo no jogo curto. Nenhum ajuste foi feito (o plano não previa e a validação já tinha rodado).
- `medir_vinculo_mega.mjs` ganhou `--versao`; sem ela o script é o de antes, byte a byte (os artefatos dos v5 não foram regravados).
- `web/app/test/save.test.ts` usava `versao: 10` como exemplo de versão desconhecida; passou a 11.

## 2026-10-01 — GPU-ESTILO: o estilo com o corpus em português (medida A e rodada 4 do comando)

Plano `docs/PLANO_ANALISE_V2_GPU_ESTILO.md` commitado antes da run; uma run de cada, nada ajustado. Desvios e interpretações:
- **Medida A roda um modo só.** Com o corpus em português o filtro do alfabeto não tira nada (0 itens não latinos), então o bloco "com
  filtro" é igual ao "sem filtro" item a item; o script ganhou `--saida` e, nesse caso, gera só o modo que o servidor manda e grava
  `filtro_sem_efeito`. `artifacts_voz/estilo_latino/` (corpus anterior) não é refeito. Critério PROPOSTO ≤ 1/30 rejeitadas: 0/30.
- **A primeira execução da medida A foi interrompida aos ~60 s** (o processo estava preso ao teto de 10 min da ferramenta) e relançada
  inteira como processo independente; nada tinha sido gravado. Os artefatos são da segunda execução (10:19 a 10:42).
- **Rodada 4 do comando: gate PASSA com o estilo** (3,3% falsos positivos; 88,3% imperativos). Comparação com a rodada 3 é descritiva
  (sementes diferentes, sem teste). As 2 saídas rejeitadas pelo parser não são por letra não latina.
- **Testes:** `python -m pytest tests/ -q` na worktree, depois das runs: 596 passed, 1 skipped (7 min 8 s, Windows, Python 3.13.0).

## 2026-10-01 — V2, L1: o lobo de decisão aprende (`docs/TAREFA_V2_L1_DECISAO.md`, `docs/PLANO_ANALISE_V2_L1.md`)

Interpretações do desenho, registradas com o plano (antes da calibração). Os números da calibração ficam no `CLAUDE.md` (seção "V2, L1").
- **"Feedback como vantagem" em inteiros.** A política é proporcional (`p(a) = w_eff(a) / Σ`), não softmax: o gradiente exato de
  `log p(a*)` é `(x_j/S)·(1[a = a*] − p(a)) / w_eff(a)`. A atualização implementa essa direção em inteiros,
  `Δw = arred(f·S · passo · X_j · (S·1[a = a*] − P_a) / (S·S·W_a))`, com `P` e `W` **da política no momento da decisão**
  (elegibilidade à COACH); o passo se divide por `w_eff(a)`, então um peso efetivo grande anda menos. O sinal escalar `f` entra no lugar
  da vantagem. Arredondamento simétrico (meio longe do zero) para não haver viés de sinal; `round()` do Python é meio-para-par.
- **Janela de crédito igual à da v1, inclusive o chamado.** Elogio e bronca creditam a última decisão; cada `chamar_atencao` fica
  pendente até o primeiro cuidado (paga `1 − L/janela`) ou expira (paga −0,5). Os valores foram **copiados** da `ConfigBandit` para a
  `ConfigLobos`, não compartilhados: o bandit está congelado e a V2 não deve depender da config dele.
- **Piso no peso efetivo, não nos pesos.** Com o aprendizado ligado o peso efetivo dos candidatos nunca cai abaixo de `piso_peso/S`
  (S/16), para o sorteio e o gradiente não encontrarem peso ≤ 0. Entra no motivo como um quarto termo (`piso`), para a soma das
  contribuições continuar fechando com a decisão. Com o aprendizado desligado o termo é 0,0 e nada muda na L0 (G1/G2 ficam).
- **Teto simétrico em torno do prior**, `|w − w0| ≤ teto`, por peso. É o freio duro; o G6 mede se o freio foi necessário (peso no
  teto = a dinâmica queria ir além).
- **Regras com um candidato não aprendem.** `1[a = a*] − p(a) = 0` quando o candidato é único: sono, pedido e abandono ficam como no
  instinto. O aprendizado age na fome moderada e no tempo livre. É consequência do desenho L0 (candidatos vêm do impulso), não escolha
  nova; registrado porque limita o que o G3 pode mostrar.
- **Sem torneio.** O desenho da arena v1 inclui o round-robin; os gates G3–G6 são todos sobre a política e a pergunta "pet melhor na
  arena" está encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`). O orquestrador `experiments/run_v2_l1.py` roda as vidas, o replay e as
  sondas da arena v1, sem a luta. As partidas podem ser jogadas depois a partir das vidas gravadas, se alguém quiser.
- **"Donos coerentes" = atencioso e relapso.** São os dois que aplicam `donos.feedback_coerente`; o incoerente sorteia a polaridade e o
  aleatório sorteia a ação. O G3 primário é atencioso × relapso pareado por semente; os outros pares são relatados. Sujeito ao referendo.
- **G4 sobre o total, com a leitura estrita ao lado.** Na `PoliticaLobos` o impulso é uma regra explícita; quando ele decide, o fator é
  o da regra (a mesma regra do braço instinto, 34–76% na v1). A fração "o lobo de decisão decidiu com fator" é o número comparável aos
  13–18% do bandit, e vai relatada em separado. O gate no total pode ser lido como frouxo: fica para o referendo.
- **G5(a) por construção.** O desenho da arena v1 não tem morte, lesão nem luta; o G5 ali é o G3. O braço de educação (lesões e sparring
  da V3) é a medida própria, informativa: com 5 sementes e mortes/lesões no aleatório e no atencioso, a leitura "sem lesão nem morte"
  pode ficar com menos de 3 sementes ("insuficiente").
- **G6: razão JSD(14)/JSD(7) ≤ 1,5 e nenhum peso no teto.** Convergindo a razão tende a 1; crescimento linear dá 2. O 1,5 é PROPOSTO.
- **A sonda acrescenta motivos.** `distribuicoes_de_acao` chama `agir`, e a `PoliticaLobos` registra um motivo por chamada (sem
  `observar`, nada de aprendizado muda). O `politica.json` é gravado antes da sonda; o replay compara com ele.
- **`fabricas_educacao` ganhou `politica_fabrica` opcional** (e `simular_vida_educacao` repassa). Padrão `None` = o bandit da
  personalidade, bit a bit como antes (`tests/test_reproducao_v3_confirmatoria.py` continua conferindo a V3c e a confirmatória).
- **Plano revisado antes da calibração válida (revisão 2, D1–D4).** A revisão 1 do plano (`ab53d00`) foi commitada antes de o
  coordenador trazer `docs/DEFINICOES_V2.md`; uma calibração começou sob ela e foi interrompida e descartada sem artefato. A revisão 2
  acrescenta G3-T, o G4 só do aprendido, o controle sem lobos, o acoplado e a norma de reação, e muda a regra de escolha da calibração
  (G4 do aprendido). Interpretações próprias da revisão 2: (a) o controle sem lobos tem 490 pesos por um índice de contexto sem
  semântica (o sétimo do dia), para igualar a contagem; seu prior é o tempo livre do instinto em todo contexto e 1,0 nas ações de regra
  (ele não dorme por regra): é o que "sem módulos" custa; (b) o acoplado é o log do atencioso sem os eventos de elogio e bronca,
  rejogado com uma política nova e a mesma semente (as ações de cuidado nos mesmos ticks; a rng de ambiente consome menos sorteios de
  ação do dono, então o ambiente pode diferir no detalhe); (c) G5(c) = JSD(atencioso, relapso) − JSD(acoplado, relapso) > 0; (d) a
  norma de reação usa a regressão conjunta de Finlay–Wilkinson (índice do ambiente = média de todos os pets no ambiente), porque os
  ambientes são sementes, sem gradiente medido; (e) o teto do G3-T é a política ótima do dono avaliada nos estados que o pet visitou.
- **Calibração (2026-10-01, `artifacts_v2_l1/calibracao/`): não fechou.** Nenhum ponto passa G6; a regra da seção 5 escolheu passo
  512, teto 1024 (menor razão 14/7), com 12 vidas no teto. Nada foi reajustado; o ponto vai ao config da validação e à `ConfigLobos`
  como o plano manda, e o referendo decide se vale rodar a validação com ele.
- **Índice do ambiente mal condicionado na norma de reação.** Com ambientes que são sementes, o índice de Finlay–Wilkinson tem
  amplitude 0,007 e as inclinações saem com IC de dezenas; só os interceptos são legíveis. Fica relatado; uma versão com um gradiente
  de ambiente medido (por exemplo, a dificuldade do ambiente) é desenho novo e não entra sem plano.
- **Artefatos pesados fora do git.** Os `vidas/*.politica.json` da L1 (um motivo por decisão) somam 600 MB; `.gitignore` os deixa de
  fora e eles se regeneram pelo replay do `.jsonl` com o mesmo código (o orquestrador confere o replay bit a bit antes de medir).

## 2026-10-01 — V2: seguir mesmo com validações falhando (decisão do Matheus)

Depois da calibração da L1 (PR #119: G3 0,029 bit contra 0,10; G4 do aprendido 0,188 contra 0,50; G6 com pesos no teto; G5 (c)
passa; `artifacts_v2_l1/calibracao/`), o Matheus decidiu: **a V2 segue mesmo se as validações falharem agora**, porque as
implementações futuras (pergunta maior, frutas, comparação de cérebros) mudam tanto o escopo que todas as validações iniciais vão
ter de ser revistas. Efeito:
- a parada do `docs/PLANO_V2_PESQUISA.md` (seção 3, fase 1) deixa de bloquear; o resultado de cada validação é registrado como sair;
- a validação da L1 roda já, no ponto da calibração (passo 512, teto 1024), com os alvos e as interpretações do plano rev. 2 como
  estão (substitui o referendo M1 do `docs/ROADMAP_V2.md`); M4 decidido;
- continuam valendo: plano antes da run, validação uma vez, sementes separadas, nada de reajustar olhando a validação.

- **Validação (2026-10-01, `artifacts_v2_l1/validacao/`): rodada uma vez, no ponto 512/1024, liberada pelo PR #120 sem o referendo
  dos gates (decisão do Matheus: falhar não para a V2). Nada foi reajustado.** G3, G4, G5 e G6 falham; G5(c) passava na calibração e
  cruza zero na validação (5 sementes). Uma semente do acoplado (4505) ficou com 144 interações contra 85–91 das outras: o atencioso
  dessa vida deu menos sinais; relatado, não tratado. O ponto e os alvos continuam os do plano; a revisão é do Matheus.

## 2026-10-01 — Pendências fechadas pelo Matheus

- **Limiar do Mega nos pets v10:** fica em 0,4 (recomendação do coordenador aceita). O vínculo B passa na pesquisa
  (`artifacts_v2_vinculo_novo/validacao/resumo.json`), mas no jogo curto não inverte o Mega (`artifacts_v2_vinculo_novo/mega_v10.json`);
  rever só com medida de dono humano.
- **`revisao.csv` da moldura** (`artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260928/`): revisado pelo Matheus. Ligar a fala por LLM
  por padrão segue decisão à parte.
- **Claude Science, prompts 09 e 10 e verificação das fontes do corpus DigiBrain:** executados pelo Matheus. As sínteses V2 e V3
  estão em `v1/docs/referencias/` (a V3 entra no repositório pela tarefa FRUTAS-DEFINICOES). A saída da verificação das fontes
  CORPUS ainda não está em disco: quando estiver, ela atualiza `docs/research/digibrain/references/source_index.md`.
- **Roteiro do vídeo e posts:** revisados e números conferidos pelo Matheus (arquivos fora do repositório, `D:\Trab\digilab\docs\`).

## 2026-10-01 — PLANO_V2_PESQUISA, revisão 2 (decisão do Matheus: M3)

O Matheus adotou a pergunta maior ("em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as
predisposições herdadas?") e a arquitetura com o dono informante como alvo da V2. `docs/PLANO_V2_PESQUISA.md` foi reescrito:
- a H1 antiga (donos coerentes distinguíveis) vira o braço P3, com os mesmos gates G3–G6;
- braços P0–P3 e condições casado/descasado/mutável;
- vantagem adaptativa medida no próprio ambiente, nunca pela força na arena;
- a fase 0 é dada como feita;
- pesquisa no Python, um DigiBrain na web;
- a regra de parada de 2026-10-01 continua.

Nenhum número de gate mudou. M5–M9 do `docs/ROADMAP_V2.md` continuam abertas.

## 2026-10-01 — FRUTAS-DEFINICOES: definições das frutas no papel; interpretações

Tarefa `docs/TAREFA_V2_FRUTAS_DEFINICOES.md`; entrega `docs/DEFINICOES_FRUTAS_V2.md`. Nenhum código, nenhuma run, nenhum número.
- **"Campo do log" lido pela regra do projeto.** As ações do pet não entram no log (`digilab/events.py`): são derivadas pelo replay. Então o
  registro de cada restrição é de um de três tipos, declarado em cada uma: **evento** (só o que o dono faz: a oferta da fruta, como
  `acao_usuario`; a escolha no modo livre, como `decisao_externa`), **registro derivado** (incentivo, avaliação, oferta, consumo, primeiro
  contato, reconstruídos pelo replay e expostos em `estado_interno()` e nos artefatos) ou **genoma** (neofobia e preferência inata, da semente
  do ovo ou do `origem` dos filhos). Gravar a escolha do pet no log quebraria a regra do event sourcing.
- **A busca V1–V6 entrou como cópia literal** de `v1/docs/referencias/` (quatro arquivos, como a da V2 pela decisão D9). Os nomes de arquivo
  citados dentro da síntese (`v3_referencias.csv`, `v3_verificacao.json`) diferem dos arquivos copiados (`v3_referencias_verificadas.csv`,
  `v3_verificacao_crossref.json`); o texto não foi editado, para a cópia ser a mesma da origem.
- **Rótulos.** Todas as 30 referências citadas estão VERIFICADA nas tabelas; as oito verificadas só por título e metadados vêm marcadas no
  texto (Rolls et al. 1981, Beauchamp e Moran, de Araujo et al., Grand e Cliff 1998, Drummond e Sauer, King e Delfabbro, Karlsen, Veiga et al.).
  O livro de Grand (2001) aparece só como VERIFICADA (sem DOI) quanto à existência, com o conteúdo não lido. Nenhuma linha NÃO LOCALIZADA da
  busca foi citada. Os itens do corpus DigiBrain marcados como pista na nota do sistema hedônico não foram usados.
- **A frase de comparação com o Creatures** não aparece no documento; ela segue na seção 7 de `docs/DEFINICOES_V2.md`, como citação do pedido
  original. A troca é a decisão F10, do coordenador.
- **Interpretação da validação "A6"** citada na tarefa (restrição 5): lida como a decisão A6 da arquitetura (a pergunta maior adotada), que
  não depende do vício; a V8 do roadmap (o genoma já modula a sensibilidade ao reforço) foi usada como o único precedente de vulnerabilidade
  por genoma no código.

## 2026-10-01 — V2, BANCADA: interpretações do orquestrador dos braços

Tarefa `docs/TAREFA_V2_BANCADA.md`. Sem run de pesquisa; só as sementes dos testes.
- **P0 é o aprendiz com o aprendizado desligado, não o aprendiz ligado sem sinal.** A tarefa define P0 como "só o herdado (o prior fixo)".
  Um `PoliticaLobos` ligado a quem não chega nada ainda mudaria: o `Aprendiz` credita o chamado pendente que expira (`_expirar`, chamado
  dentro do `observar`) com a recompensa do pedido ignorado, e isso é um sinal do dono ausente. Por isso a fonte `nenhuma` usa o mesmo
  cérebro, o mesmo prior e a mesma `ConfigLobos` com `aprendizado_ligado=False`, e não repassa nada do dono (nem para a memória, que
  contribui zero). É o que faz o P0 sair byte a byte igual ao instinto.
- **O P3 usa o aprendiz da L1 como ele foi validado** (`CONFIG_LOBOS_APRENDIZ`, passo 512 e teto 1024), com os gates da L1 falhando
  (`docs/RESULTADO_V2_L1.md`): a bancada não muda o aprendiz, só fixa como ele entra nos braços (decisão M4: falha não bloqueia).
- **"Acoplado reproduz" foi lido de três jeitos, e os três viraram teste:** (1) o acoplado no próprio braço, sem filtro, é a vida de
  origem byte a byte; (2) o P3 acoplado ao próprio registro sem os sinais é o "só cuidado" acoplado da L1 (`vidas_acopladas`), byte a byte,
  com e sem carinho; (3) com o sinal desligado (P0) no registro do P3 sem os sinais, o log é o da origem com os sinais retirados, evento
  a evento, e a vida é a do instinto nesse registro. As funções da L1 não foram trocadas pela bancada: os artefatos da L1 continuam
  saindo do código que os gerou.
- **Tempo fora de privação e saúde média são amostrados em cada decisão** (a cada `intervalo_decisao_ticks` = 15 ticks, uma grade
  regular), não tick a tick. Medir tick a tick exigiria partir os avanços do replay, e o `MotorPersonalidade` conta os avanços
  (`_n_eventos`), o que mudaria a vida. A privação usa a regra do estado (`Estado.em_privacao`), não uma cópia dela.
- **"Tempo até metade do caminho" é o da curva de acerto**, pela `eficiencia_amostral` (dia e sinais), com o piso no acerto do P0 da
  mesma célula (genoma, mundo, dono, semente), como a L1 usava o instinto. Os sinais contados são os que **chegaram ao aprendiz**
  (`PoliticaDoBraco.sinais_entregues`); os que o dono deu ficam ao lado (`sinais_do_dono`). No P0 o dono elogia e repreende e nada chega.
- **Só o cérebro `lobos`**: a tarefa deixa fora "qualquer cérebro além dos lobos"; o controle sem lobos (`camada_unica`), que a seção 6
  pede em todos os braços, entra quando a comparação de cérebros (N11) for tarefa.

## 2026-10-01 — V2, A1: a bola sem aprendizado (`docs/TAREFA_V2_A1_BOLA_IMPL.md`, `docs/PLANO_ANALISE_V2_A1.md`)

Plano commitado antes de qualquer run (primeiro commit do branch `v2-a1-bola-impl`). Interpretações do desenho e da calibração:
- **A bola entra pelo instinto, não pelos lobos.** A tarefa proíbe mexer em `policies/lobos.py`; a resposta à bola vive em
  `ambiente.PoliticaInstintoBola`, uma subclasse que soma `w_bola × bola` em `brincar` no tempo livre. Para isso o `PoliticaInstinto`
  ganhou o gancho `_pesos_tempo_livre` (extração: os mesmos literais, na mesma ordem; a canônica e o G2 da L0 passam).
- **`Observacao.bola` é um campo com padrão 0,0**, não uma entrada de `Estado.vetor`: o vetor e as features do bandit não mudam, e só o
  `MotorAmbiente` injeta o valor (um embrulho da política, como o `_PoliticaObservada`). `de_estado` não o preenche.
- **Pôr e tirar a bola não são contato** (não zeram o tempo sem cuidado, não passam pelo vínculo, pela política nem pela janela da
  educação) e contam 1 interação do orçamento. O `_n_eventos` conta o evento, para os refs dos motivos seguirem alinhados ao log.
- **O instinto puro não roda no `MotorPersonalidade`** (o embrulho repassa `receber_acao_dono`): `PoliticaInstintoBola` tem o gancho
  vazio. É ela, desligada, o controle do G2(b) contra o `MotorComFeedback` com o `PoliticaInstinto`.
- **G2(a) com uma vida da V3 simulada no teste**, não com os logs de `artifacts_educacao/vidas` (fora do git): a vida `atencioso@70001`
  da V3 por 3 dias (educação, lesões e sparring), rejogada no `MotorEducacao` e no `MotorAmbiente` desligado.
- **Δp por semente = média dos donos com Δp definido.** O relapso quase não põe a bola (1 bola em 5 vidas): `relapso-bola@6404` não tem
  decisão de tempo livre com bola e fica de fora daquela semente (listado em `resultado.json`, `vidas_sem_delta`). O plano dizia "média
  dos 4 donos"; com a medida indefinida não há o que somar.
- **A calibração não fechou**, e nada foi ajustado: em todos os 27 pontos a privação sobe com a bola (+0,016 a +0,025), então o ponto
  saiu da regra de reserva da seção 4 (maior limite inferior de Δp): duração 120, ganho 0,15, `w_bola` 6. **A causa é o dono aleatório**
  (`pet.json` e `sembola.json`, por dono): ele sorteia `por_bola` entre 7 ações, e com o orçamento fixo cada bola tira uma ação ao acaso,
  inclusive alimentar e limpar; a privação dele sobe de 0,355 para 0,433, igual com a bola que o pet não vê (0,427). Não é o brincar do pet.
  Leitura: **a bola não toca a cadeia da saúde pelo pet, mas toca pelo orçamento do dono.** O critério "cuidado controlado" do plano
  compara braços com o mesmo orçamento e, assim, mede também essa troca. Caminhos possíveis, **não aplicados** (são decisão do Matheus):
  a bola fora do orçamento, o aleatório sem `por_bola` no sorteio, ou o critério só nos donos que não deslocam cuidado.
- **Nos donos coerentes a bola compete com o ensino, não com o cuidado:** o atencioso põe 56 bolas por vida e dá menos elogios e broncas
  (87,6 → 58,8 e 45,8 → 20,4). É um custo que a pergunta 1a-dono (A1 + L1) vai encontrar: com orçamento fixo, cada bola é um sinal a menos.
- **Meta da calibração:** o sha256 do `config.py` gravado em `artifacts_v2_a1/calibracao/meta.json` é o de antes de os padrões da
  `ConfigBola` virarem o ponto escolhido; a calibração passa cada ponto explicitamente e não lê os padrões.
- **Teste ajustado:** `tests/test_educacao.py::test_acoes_novas_nao_mexem_nas_listas_antigas` exigia as ações de educação como as três
  **últimas** do enum. Com `POR_BOLA` e `TIRAR_BOLA` depois delas, o teste confere o que ele protege: as ações de educação nas mesmas
  posições de sempre (12 a 14) e, depois delas, só as da bola.
- **Validação (7101…7505, uma vez, no ponto da calibração):** 1a-pet passa (+0,310 [+0,245; +0,375]); cuidado controlado falha
  (+0,017 [+0,009; +0,028]) pelo mesmo mecanismo da calibração (o aleatório, 0,266 → 0,333). Nada mudou por causa dela; resultado em
  `docs/RESULTADO_V2_A1.md`, com as decisões B1–B3 para o Matheus. Pela decisão de 2026-10-01 a V2 segue.

## 2026-10-01 — Fim da rodada 3: decisões da bola (B1–B3) e das frutas (F1–F11)

O Matheus seguiu as recomendações:
- **Bola** (`docs/RESULTADO_V2_A1.md`):
  - B1: tirar `por_bola` do sorteio do dono aleatório nas runs seguintes com a bola;
  - B2: a bola fica fora do orçamento na A1 + L1;
  - B3: aceitar que o relapso quase não põe a bola.
  - O resultado da validação da A1 não muda.
- **Frutas** (`docs/DEFINICOES_FRUTAS_V2.md`): F1–F11 como recomendadas.
  - F8 (vício no produto) e F11 (ler *Creation*) ficam para depois.
  - F4: a neofobia é um gene próprio.
  - F10 aplicada: a frase do pedido original em `docs/DEFINICOES_V2.md`, seção 7, foi reescrita.
- Marco em `docs/V2_RODADA_3.md`. Tarefas da rodada 4: N3 (B), N4 (A), plano do experimento maior (C) e bancada de mundos (D).

## 2026-10-04 — PLANO-EXPERIMENTO-MAIOR: plano no papel; duas interpretações e um conflito encontrado

Tarefa `docs/TAREFA_V2_PLANO_EXPERIMENTO_MAIOR.md`; entrega `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` e o prompt 11 do Claude Science
(`D:\Trab\digilab\docs\digibrain\integration\11_PROMPT_CLAUDE_SCIENCE_PLASTICIDADE.md`, fora do repositório). Nenhuma run, nenhum código.
- **Conflito F6 × N3 (decisão E2 do plano).** A F6 põe o efeito ruim das frutas no humor; a tarefa do N3 tira o humor do sinal do P1. Juntas,
  deixam o P1 cego ao efeito da fruta, e a predição "P1 vence P0 no descasado" falharia por construção. O plano registra a predição como
  **não testável** enquanto o contrato K2 não for cumprido e leva a escolha ao Matheus.
- **Casado com frutas (decisão E1).** A tarefa fixa o casado como o mundo padrão. O plano mantém o padrão como referência e propõe como casado
  principal o mundo com as mesmas ofertas de fruta e o efeito bom na fruta preferida, para que casado × descasado difira só no desencontro.
- **Medida primária nova.** Como o efeito das frutas fica no humor, o tempo fora de privação e a saúde não mudam com a escolha de fruta. A
  primária é a `taxa_fruta_ruim` (contrato K8, a implementar uma vez em `metrics.py`); as medidas da bancada ficam como secundárias e
  como controle do canal de cuidado.
- **Unidades derivadas das sementes reservadas (decisão E3).** As faixas 14101…14505 e 15101…15505 têm 5 sementes cada; o plano deriva as
  unidades de cada uma (`derivar_semente("experimento-maior", base, k)`) e fixa o número delas no adendo antes da validação, pela variância
  da calibração, como a análise de poder da v1 (`artifacts_poder/`).
- **Decisões E1–E8 aprovadas pelo Matheus como recomendadas (2026-10-04).** Em particular, E2: o sinal do P1 inclui o humor vindo do
  consumo de fruta no experimento maior, e a F6 não muda. Isso vira contrato para o N3 (chat B): o componente de humor da fruta, declarado e
  desligado sem frutas. O texto da tarefa do N3 é do coordenador e não foi editado aqui.

## 2026-10-04 — V2, N3: a consequência da própria ação como sinal (`docs/TAREFA_V2_N3_CONSEQUENCIA.md`, `docs/PLANO_ANALISE_V2_N3.md`)

Interpretações do desenho, registradas com o plano (antes da calibração).
- **Janela de crédito imediata.** O sinal de uma decisão é `observacao → observacao_seguinte` dessa decisão, que o motor mede logo
  depois do efeito da ação do pet e antes do tempo e do dono (validação V2 do roadmap). Consequência: o sono dá sinal zero (a energia
  só sobe nos ticks seguintes), e brincar e explorar dão sinal negativo (gastam energia; o humor que sobem está fora). O sono é regra
  determinística e nunca aprende, então o zero não muda nada. A consequência atrasada (o intervalo até a próxima decisão) fica
  declarada e não rodada: ela mistura o cuidado do dono.
- **Forma do drive em inteiros, sem raiz.** D = Σ(S − arred(h·S))² sobre fome, higiene e energia, com ponto de ajuste 1,0. É a família de
  Keramati e Gutkin com expoente 2 e sem a raiz: mantém a priorização (reduzir um déficit maior vale mais) e fica exato em inteiros.
  A escolha dos expoentes é do projeto, não da referência.
- **Sem o canal do chamado no P1.** O crédito do chamado (atendido ou ignorado) depende do dono; o P1 não o recebe. O gancho novo
  (`Aprendiz.observar_consequencia`) não passa pelo relógio de cuidado nem pelos pendentes. A regra de atualização é a mesma da L1
  (`atualizar_pesos` via `_aplicar_sinal`); teste: o mesmo f_S pela via do dono dá os mesmos pesos.
- **Só o ganho calibra.** Passo, teto e piso são os da L1 (o mesmo aprendiz); o ganho é a escala do sinal da fonte, não uma regra nova.
- **Cuidado controlado = acoplado P1 ← P0 sem filtro.** Na vida fechada o dono reage ao pet; o P1 no registro do P0 recebe o mesmo
  cuidado nos mesmos ticks. O "só cuidado" da L1 (P3 ← P3 sem sinais) entra como a referência H0 de sempre.
- **"Sem mortes novas" por construção.** No mundo `padrao` da bancada (`MotorComFeedback`) não há lesão nem morte; o gate fica
  registrado como satisfeito por construção, e a saúde média é relatada.
- **G6 só pelo teto, como a tarefa pede.** A razão da deriva (dia 14 / dia 7) é relatada sem gate.
- **Calibração (2026-10-04, `artifacts_v2_n3/calibracao/`): não fechou.** Nenhum ganho passa o G6 (18–20 vidas no teto em todos); a regra
  de reserva escolheu o ganho 4 (menos vidas no teto). Nada foi reajustado; o ganho vai ao config da validação e à `ConfigConsequencia`.
- **Validação (2026-10-04, `artifacts_v2_n3/validacao/`): rodada uma vez, no ganho 4, sem reajuste.** O G-P1 passava na calibração
  (+0,0051 [+0,0008; +0,0091]) e falha na validação (+0,0008 [−0,0067; +0,0077]); o G6 falha nas duas. Registrado; o ganho, a
  janela e o teto ficam como estão. Relatório em `docs/RESULTADO_V2_N3.md`.

## 2026-10-04 — V2, BANCADA-MUNDOS: interpretações do mundo da bola e das condições

Tarefa `docs/TAREFA_V2_BANCADA_MUNDOS.md`. Sem run de pesquisa; só as sementes dos testes.
- **B1 sob B2: o aleatório não põe bola.** A decisão B1 é "tirar `por_bola` do sorteio do dono aleatório"; a única regra dele para a bola
  era o sorteio, então no mundo `bola` ele nunca põe bola. Dar a ele a regra dos coerentes (agora que a bola não gasta orçamento) seria
  regra nova de dono: fica para o Matheus, se quiser exposição à bola no braço do aleatório. Consequência: o aleatório no mundo `bola` tem
  o mesmo registro do mundo padrão (teste).
- **B2: a bola sai do orçamento por um canal do mundo.** `simular_vida_mundo` é o `simular_vida` com um passo a mais: depois das ações do
  dono pelo `CanalDeInteracao` (orçamento exato, como sempre), a `RegraBola` põe a bola direto no motor (entra no log, não no canal). A
  regra é a dos coerentes do `DonoComBola` (pet acordado, fora da noite, sem cuidado pendente, sem bola, `bolas_por_dia`) lida na visão de
  antes das ações do passo, como na A1, **sem** a condição "ainda cabe no máximo do passo", que só existia porque a bola gastava
  orçamento. O relapso continua pondo só nas visitas (B3: aceito). O laço fica na bancada, não em `ambiente.py` (o chat A estende
  `ambiente.py` no N4); as ofertas de fruta fora do orçamento (que o N4 também pede) podem usar o mesmo canal.
- **`bola_a1` é um mundo à parte**, com o `DonoComBola` como está: é o que reproduz a A1 byte a byte (gate). Runs novas usam `bola`.
- **O cérebro `instinto` entrou, só no P0.** A tarefa da bancada deixava fora "qualquer cérebro além dos lobos", mas o gate desta tarefa
  pede reproduzir a vida da A1, que foi vivida pelo instinto que vê a bola (`PoliticaInstintoBola`). Os lobos ainda não veem a bola (a
  regra é do chat B), então o P0 com lobos reproduz o braço "bolacega" da A1, e o P0 com o instinto, o braço "bola". O instinto não
  aprende: em outro braço falha alto.
- **O mundo da bola usa o motor da A1 também sem genoma** (`MotorAmbiente`, obediência desligada, temperamento neutro), enquanto o mundo
  padrão sem genoma usa o `MotorComFeedback`, como a L1. Com genoma, o padrão usa o `MotorPersonalidade` (obediência ligada) e a bola o
  `MotorAmbiente` (obediência desligada, o desenho da A1). Comparar braços dentro de um mundo não é afetado; comparar o mesmo braço entre
  `padrao` e `bola` com genoma mistura a obediência com a bola.
- **O acoplado não tira eventos do mundo**, ao contrário do "só cuidado" da A1 (`run_v2_a1.log_so_cuidado`, que tirava a bola): a tarefa
  pede reproduzir o registro "sem perder os eventos do mundo", e as definições das frutas (F7) pedem o acoplado "com as mesmas ofertas".
  O da A1 continua lá, como estava.
- **Condição na tabela:** a coluna passou de `mundo` para `condicao/mundo`, para os três mundos casados não se misturarem numa célula.

## 2026-10-04 — V2, N4: frutas no mundo, sem aprendizado de política (`docs/TAREFA_V2_N4_FRUTAS.md`, `docs/PLANO_ANALISE_V2_N4.md`)

Plano commitado antes de qualquer run (primeiro commit do branch `v2-n4-frutas`, `2dea550`). Interpretações do desenho e da calibração:
- **Módulo próprio em vez de editar o `ambiente.py`.** A tarefa pede "estender o `MotorAmbiente`"; o `MotorFrutas` é uma subclasse em
  `digilab/frutas.py`, e o `ambiente.py` não muda (o chat D pode mexer nele pelo mundo da bola).
- **A escolha entre frutas lê o incentivo, com uma regra fixa** (proporcional, na `rng_fruta`). As definições pedem que a escolha seja
  da política; com o aprendiz desligado e `lobos.py` fora desta tarefa, a política só decide **se** come (o instinto, com `comer` no tempo
  livre pesado pelo maior incentivo), e o **qual** é a sub-decisão do motor pelo incentivo, que é o registro do "querer" (F1).
- **O incentivo só muda no consumo** (na direção da avaliação); a definição 1.3 diz "em `oferta` e `consumo`", mas ignorar uma fruta não
  tem avaliação a seguir. O efeito no corpo não entra no incentivo: seria aprender pela consequência (N3).
- **A avaliação parte da preferência inata** (é o "ponto de partida" da definição 2.4) e só é medida no consumo.
- **Ofertas por cronograma igual para os quatro donos**, fora do orçamento e do sorteio do aleatório (B1, B2): a exposição às frutas só
  difere entre donos pelo sono do pet. As ofertas vão direto ao motor, sem passar pelo `CanalDeInteracao` (`simular_vida_frutas`).
- **A herança dos genes das frutas não entra**: os filhos não estão nesta run, e mudar o `Genitor` mexeria no evento `origem` de todos os
  filhos. Fica para quando a linhagem usar frutas.
- **Teste ajustado:** `tests/test_ambiente.py::test_enum_do_dono_cresce_no_fim_e_a_v1_nao_ve` exigia a bola como as duas últimas ações do
  enum; com as ofertas depois dela, confere a bola nas mesmas posições (15 e 16). `tests/test_educacao.py` idem (educação 12 a 14, bola 15
  e 16).
- **A calibração não fechou**, e nada foi ajustado. (a) **A faixa de p(comer | fruta) [0,30; 0,80] ficou fora do alcance da grade:** o
  peso de `comer` é `w_fruta ×` o maior incentivo, que é no máximo a preferência inata e cai com a neofobia, contra os pesos do tempo livre
  que somam de 7 a 12; com `w_fruta` 6 o p(comer) médio é 0,19. (b) **O G-SEP(ii) tem pouca amostra:** de 0 a 27 escolhas entre duas
  frutas ou mais por vida, e a semente de neofobia alta quase não come. O ponto saiu da regra de reserva da seção 4.
- **A regressão do G-SSE não tem o termo da preferência inata** (o plano fixou `avaliacao ~ 1 + recente + fome`). Nos pontos com poucos
  consumos isso dá β_recente absurdos (−27 com `w_fruta` 1, quando o consumo recente quase nunca passa de 0; +2,4 com `w_fruta` 3 e
  `k_saciedade` 0,2, porque as frutas de preferência alta são as mais comidas e acumulam consumo recente). No ponto escolhido, com 593
  consumos e 205 com consumo recente acima de 0,05, o β sai −0,77 [−0,87; −0,69]. A regressão fica como o plano diz; a próxima medida da
  saciedade deveria pôr a preferência (ou usar a queda `preferencia_inata − avaliacao`).
- **O genoma é o mesmo para os quatro donos de uma semente** (sai da semente do motor). Por isso a neofobia de uma semente pesa em todos os
  donos dela: com 0,96 o primeiro contato vem no 3º ao 8º dia. A variação entre sementes do p(comer) (0,05 a 0,30) é sobretudo isso.
- **Validação (11101…11505, uma vez, no ponto da calibração):** G-F7 passa; **G-SEP falha** pela (ii) (+0,110 [−0,007; +0,213], pouca
  amostra de escolhas entre frutas); **G-SSE falha** pelo β_fome (−0,070 [−0,159; −0,014]), pela regressão sem a preferência inata (a
  avaliação não lê a fome: código e teste). Nada mudou por causa dela; resultado em `docs/RESULTADO_V2_N4.md`, com as decisões N1–N4.
  Pela decisão de 2026-10-01 a V2 segue.

## 2026-10-04 — Fim da rodada 4: decisões N1–N4 e mudança na prévia da rodada 5

- **Decisões do Matheus nas frutas, como recomendadas** (`docs/RESULTADO_V2_N4.md`):
  - N1: trocar a medida da saciedade no próximo plano, sem releitura pós hoc;
  - N2: ampliar a grade de `w_fruta` na calibração do experimento maior;
  - N3: manter a nutrição;
  - N4: herança dos genes das frutas na fase 3.
- **Rodada 5 muda em relação à prévia** de `docs/V2_RODADA_4_PROMPTS.md`. Os lobos ainda não veem a bola nem as frutas, então o N5 e o
  experimento maior precisam antes de um aprendiz que veja o mundo (`docs/TAREFA_V2_LOBOS_MUNDO.md`, chat B, com a E2).
  - O N5 se divide em mundo (chat A) e plano (chat C).
  - O D faz os mundos das frutas na bancada.
  - O N6 e o N7 passam para a rodada 6.
- Marco em `docs/V2_RODADA_4.md`.

## 2026-10-04 — Gargalo do aprendiz: revisão reservada e variedade de frutas como fator a considerar

O Matheus perguntou se o gargalo é ter poucos objetos (bola, frutas) ou o computador. Pela leitura das rodadas 3 e 4, o gargalo é o
aprendiz e a densidade de consequências que ele recebe:
- o instinto decide cerca de 80% das decisões na L1;
- os pesos ficam no teto em 12 de 20 vidas na L1 e em 20 de 20 no N3;
- o sinal só vê o efeito imediato da ação;
- a exposição é baixa: p(comer | fruta) 0,208;
- os lobos ainda não veem o mundo novo.

O computador não é o gargalo. Decisão do Matheus:
- tarefa `docs/TAREFA_V2_REVISAO_APRENDIZ.md` (rodada 6, chat B, só calibração), que vira a linha R6.0 do `docs/ROADMAP_V2.md`;
- variedade de frutas como fator a considerar no experimento maior (`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, seção 2.1). Ela fica
  fora das predições registradas e só entra por adendo antes da calibração.

## 2026-10-04 — N5-PLANO: plano do dono informante no papel; interpretações

Tarefa `docs/TAREFA_V2_N5_PLANO.md`; entrega `docs/PLANO_ANALISE_V2_N5.md`. Nenhuma run, nenhum código.
- **Nomes combinados com o chat A** (PR #140): o plano adota sem troca os nomes que ele implementou (evento `INFORMAR_FRUTA_<A|B|C>_<BEM|MAL>`,
  `Observacao.info_frutas`, `ConfigInformacao.janela_min`, `DonoInformante` com `certo` e `errado`, `MotorFrutas.informacoes`) e acrescenta
  um nome: o modo **`acoplado`** do informante (mesmo multiconjunto de fruta e conteúdo do `certo`, em ticks sorteados por rng própria).
- **Confiança de partida maior que zero.** A tarefa pede a informação "nunca como reforço"; o plano a põe como entrada da sub-decisão da fruta
  com peso inicial positivo (calibrado), e o peso só muda pela consequência. Com peso inicial zero a informação não teria efeito antes de o
  mundo validá-la, e o P2e não poderia piorar no começo (predição 4(a) do experimento maior). A grade fica abaixo do teto dos pesos, para o
  mundo poder levar o peso a cruzar o zero.
- **Só o mundo descasado.** O casado com frutas e o mutável ficam para o experimento maior (decisão N5-5 do plano).
- **Leituras registradas antes** para dois riscos já vistos nos artefatos: pouca fruta comida (N4) e pesos no teto (N3, L1).

## 2026-10-04 — V2, BANCADA-FRUTAS: interpretações dos mundos das frutas e das unidades derivadas

Tarefa `docs/TAREFA_V2_BANCADA_FRUTAS.md`. Sem run de pesquisa; só as sementes dos testes.
- **Uma fruta boa e uma ruim em cada condição.** O plano (seção 2) pede o casado com "a fruta de maior preferência inata com o efeito bom"
  e o mutável trocando "a boa vira ruim e vice-versa"; a medida primária (`taxa_fruta_ruim`) precisa de uma fruta ruim também no casado
  (predição 1). Com o descasado do N4 (a preferida faz mal, as outras neutras), o casado com o sinal trocado não teria fruta ruim. A
  regra adotada: casado = a de maior preferência faz bem e a de menor faz mal; descasado = o contrário; a do meio neutra nos dois. O
  efeito bom é o ruim com o sinal trocado (−`efeito_humor_ruim`), sem número novo. Por isso o descasado da bancada **não é** o do N4: a
  fruta menos preferida faz bem aqui, e era neutra lá. Se o Matheus preferir outra regra, ela muda só `efeitos_da_condicao`.
- **O calendário das ofertas ignora o sono.** O `OfertasFrutas` do N4 só oferece com o pet acordado; com isso a oferta depende do estado
  do pet, e dois braços (ou duas condições, porque o efeito no humor muda o comportamento) teriam ofertas diferentes. O plano (seção 2,
  K5) pede o calendário pela semente, igual em todos os braços. O `CalendarioFrutas` oferece nos mesmos horários todo dia, com o pet
  acordado ou não (a fruta fica até o prazo), e começa a rotação num índice derivado da semente. Por isso as vidas da bancada não são as
  do N4 byte a byte; o teste mostra que, com o mesmo efeito, o `MotorFrutasMundo` é o `MotorFrutas`.
- **A troca do mutável é registro derivado, não evento do log.** Pôr um evento novo no log pediria mudar `events.py` e os replays (de
  `frutas.py`, do chat A), fora desta tarefa. A troca é determinada pelo mundo (`mutavel`) e pela duração da vida (metade, no fim do dia
  `dias // 2`), fica em `MotorFrutasMundo.troca` e no efeito de cada consumo, e o replay pelo log a refaz (teste). O contrato do #137
  aceitava "evento do mundo ou parâmetro gravado da vida".
- **Metade da vida.** O plano fixa a troca no fim do dia 7 numa vida de 14; a regra geral da bancada é o fim do dia `dias // 2`, para os
  testes curtos usarem a mesma lógica. As janelas `inicio` e `final` seguem a mesma divisão.
- **A taxa fica fora das tabelas.** A `taxa_fruta_ruim` sai `None` numa janela sem consumo (os lobos, que ainda não veem as frutas, não
  comem nenhuma nos testes curtos); a tabela braço × condição exige um número por vida. A tabela dela fica para o orquestrador do
  experimento maior, que decide o tratamento das vidas sem consumo (o plano já trata a censura na predição 3).
- **`FAIXAS_RESERVADAS` é conservadora:** cada faixa vira um intervalo fechado do menor ao maior número citado (por exemplo, 80001…82004
  para a linhagem), e as sementes de fala, voz e comando de 2026-09/10 viram um intervalo só. As unidades derivadas são números de 64 bits
  (`derivar_semente`), muito acima de todas; o teste confere de qualquer jeito, também contra toda semente das configs.

## 2026-10-04 — LOBOS-MUNDO (chat B, `docs/TAREFA_V2_LOBOS_MUNDO.md`)

- **Os lobos veem o mundo só com `cfg_bola`/`cfg_frutas` ligadas, sem parâmetro novo na `ConfigLobos`.** Assim a L0, a L1, o N3 e a bancada
  ficam com as formas de antes (10 entradas, 7 regras, 490 pesos) e o estado interno idêntico; com o mundo, 12 entradas, 9 regras e 759
  pesos. As duas regras do mundo existem sempre que um dos dois está ligado (a que nunca dispara fica no prior).
- **Prior das regras do mundo = o do tempo livre mais o termo do mundo.** As duas regras só disparam no lugar do tempo livre, então o
  aprendizado de `bola_no_cenario` e `fruta_no_cenario` é separado do do tempo livre: o que o pet aprende com a bola não vaza para quando
  não há bola. Com a bola e a fruta juntas a regra é `fruta_no_cenario` (como no instinto) e o brincar dela tem o termo da bola.
- **A sub-decisão da fruta aprende pela mesma regra da L1, com uma entrada por fruta (o incentivo).** É o gradiente de log p(f*) da
  escolha proporcional; o piso vale no coeficiente (w/S), não no peso, porque o incentivo pode ser zero. Ela é creditada junto com a
  decisão de comer (o mesmo sinal, no mesmo registro), inclusive por elogio e bronca na fonte dono.
- **E2 como variante declarada do sinal** (`sinal_homeostatico_fruta`): o humor entra nos drives quando a ação foi comer uma fruta, e o
  "depois" passa a ser o estado logo depois de comer. Sem isso a fruta não apareceria no sinal: o motor come a fruta depois de a engine
  medir a transição, e o N3 só via `observacao_seguinte`. Por isso, no mundo das frutas, o comer com fruta também conta a nutrição dela
  (com `humor_na_fruta = False` fica só a fome). A variação do humor medida é a da decisão inteira (o efeito do comer de sempre e o da
  fruta), não só a da fruta. Nas outras ações, e sem frutas, o sinal é o do N3, byte a byte.
- **O crédito do comer com fruta fica pendente** entre `observar_consequencia` e `fruta_comida` (mesmo `_decisao_observada`). A pendência
  é decidida por `obs.fruta > 0`, que vale se e só se há fruta no cenário (o incentivo é sempre positivo: preferência ≥ `pref_min` e
  neofobia < 1). Um pendente sem aviso falha alto na decisão seguinte.
- **Ganchos em `frutas.py` (arquivo do chat A):** `escolher_fruta` e `fruta_comida`, por `getattr` na política; o instinto não tem nenhum
  dos dois e a vida dele não muda (os 31 testes das frutas passam). **Uma linha em `experiments/bancada_v2.py` (do chat D):** o
  `PoliticaDoBraco` passa o `cfg_consequencia` a `observar_consequencia`, para o sinal da fruta usar o mesmo ganho.
- **`PARAMETROS_CONSEQUENCIA_N3` ganhou `humor_na_fruta` (DECIDIDO, E2)**; o teste do registro do N3 passou a excluí-lo do "todos
  PROPOSTOS".
- **Não feito aqui:** a bancada montar os lobos que veem o mundo (chat D) e o `motivo_lobos` citar as regras novas.
- **Para o chat D:** o contador `PoliticaDoBraco.consequencias` conta o sinal do N3 (`f_S != 0`); no comer com fruta o
  sinal creditado é o da E2, contado no cérebro em `recompensas["consequencia_fruta"]`. Quem medir consequências no mundo
  das frutas deve somar as duas fontes (ou contar os consumos, como a predição 3 do plano do experimento maior).

## 2026-10-04 — V2, N5 (lado do mundo): a informação do dono e a medida N1 (`docs/TAREFA_V2_N5_MUNDO.md`)

- **Nomes combinados com o chat C.** O `docs/PLANO_ANALISE_V2_N5.md` (PR #142) usa, sem troca, `informar_fruta_<f>_<bem|mal>`,
  `ACOES_INFORMACAO`, `Observacao.info_frutas`, `ConfigInformacao.janela_min`, `DonoInformante` (modos `certo` e `errado`),
  `MotorFrutas.informacoes`, `decisoes_com_informacao` e `metrics.saciedade_especifica_n1`, e confere com os contratos K3, K4/E7 e K5/B2
  do plano do experimento maior. A janela de 240 min é PROPOSTA (o plano não a calibra). O plano define também o terceiro modo do
  informante, `acoplado` (seção 4.2), que fica para a implementação do N5 na rodada 6.
- **Desvio do texto da validação V6 do `docs/ROADMAP_V2.md`** ("a informação entra por um gancho do motor; a `Observacao` não muda"): a
  informação entra num campo novo da `Observacao` (`info_frutas`, com padrão), injetado só pelo `MotorFrutas`, como a `bola` e a `fruta`
  já entraram. Motivo: a tarefa dos lobos do chat B (`docs/TAREFA_V2_LOBOS_MUNDO.md`) liga ao lobo de percepção "o que o
  `MotorAmbiente`/`MotorFrutas` já injeta na `Observacao`"; assim a percepção do mundo fica num canal só. O espírito da V6 se mantém: a
  informação não é reforço (não passa por `receber_acao_dono`), `de_estado`, o bandit e o `engine.py` não mudam, e o G2 vale.
- **A janela vive no motor** (registro derivado), não no aprendiz: o aprendiz só vê o valor vigente a cada decisão.
- **Conteúdo binário com a fruta neutra = "bem"** (aceito pelo chat C): no mundo descasado só a preferida tem efeito ruim; dizer "faz bem"
  da neutra é a leitura binária de "não faz mal".
- **O informante informa logo depois de cada oferta**, sobre cada fruta oferecida: o calendário das ofertas não depende do braço, então
  P2 e P2e informam nos mesmos ticks (K3). O modo acoplado (a mesma quantidade em momentos sorteados) fica para o plano do chat C.
- **A medida N1 é nova e a antiga fica**: `saciedade_especifica` continua, para o N4 reproduzir; a N1 vale para o próximo plano. Testada só
  com dados sintéticos, como a tarefa pede.
- **Teste ajustado:** `tests/test_frutas.py::test_enum_cresce_no_fim_e_a_v1_nao_ve` confere as ofertas nas posições 17 a 19 (antes, "as três
  últimas"); as ações de informação vêm depois delas.

## 2026-10-04 — Fim da rodada 5: decisões N5-1 a N5-8 e tarefas da rodada 6

- O Matheus aprovou N5-1 a N5-8 do `docs/PLANO_ANALISE_V2_N5.md`, como recomendadas.
- Correção do coordenador: o calendário de ofertas igual entre braços é o `CalendarioFrutas` da bancada (#144), não o `OfertasFrutas` do N4.
- Ponto aberto que vira a primeira tarefa da rodada 6: a bancada ainda cria os lobos sem ver o mundo.
- Revisão do aprendiz:
  - passa de RESERVADA para ABERTA na rodada 6;
  - roda depois do N5-CEREBRO e da BANCADA-N5;
  - usa a faixa própria 18101…18505, só de calibração.
- Marco em `docs/V2_RODADA_5.md`.

## 2026-10-04 — V2, BANCADA-N5: os lobos vendo o mundo e a fonte informacao (`docs/TAREFA_V2_BANCADA_N5.md`)

- **P2a implementado na bancada.** O plano (seção 4.2, N5-4) pede o modo `acoplado` do `DonoInformante`, que não está na `main` (nenhum PR
  nem branch dele). Para não mexer em `frutas.py`, a bancada implementa a regra do plano em `InformanteAcoplado`: o multiconjunto do P2
  (o `CalendarioFrutas` passo a passo, com o conteúdo verdadeiro no tick original) em passos do dono sorteados pela rng
  `derivar_semente("informacao-acoplada", semente)`, um `randrange(passos)` por item na ordem do calendário. **Para o coordenador:**
  quando o chat A fizer o modo `acoplado`, ele tem de dar estes mesmos eventos (há teste da regra em `tests/test_bancada_n5.py`), ou a
  bancada passa a usar o dele e este sai.
- **O informante usa os efeitos reais da condição da bancada** (`efeitos_da_condicao`), não o efeito do N4 que o `DonoInformante` calcula
  sozinho; no mutável, os de antes da troca até o `tick_troca` e os de depois a partir dele (`InformanteDoMundo`, dois `DonoInformante`).
- **A `ConfigInformacao` fica ligada em todo braço dos mundos das frutas**, inclusive P0, P1 e P3: sem informação no log o motor é o mesmo
  (G2 do N5-MUNDO), e assim o acoplado pode rejogar o registro de um braço de informação com o cérebro de outro.
- **A informação não é evento do mundo** (não está em `EVENTOS_DO_MUNDO`): os filtros do acoplado podem tirá-la (`sem_informacao`,
  `sem_ensino`), e o "só cuidado" do P2 é o registro sem sinais e sem informações. Fica fora do orçamento (`FORA_DO_ORCAMENTO`) e não conta
  como interação do dono.
- **P2 hoje vive como o P1.** Os lobos ainda não leem `info_frutas` (N5-CEREBRO, chat B); até lá P2, P2e e P2a têm as mesmas ações e
  consumos do P1 (na fumaça, iguais vida a vida). O gate "P2 sem informação = P1" é testado com o braço de informação **sem informante**
  (nenhum evento de informar no registro), que continua valendo depois que os lobos lerem a informação. Um teste de que P2 e P2e diferem
  ainda não existe: fica para depois do N5-CEREBRO.
- **`consumos_ate_metade`:** a referência é a taxa de fruta ruim **total** do P0 da mesma célula (dono, mundo, unidade); o alvo é metade
  dela, e a curva é a taxa por dia (dia sem consumo conta como não alcançado). No P0 a referência é a própria taxa. Sem P0 na célula,
  `sem_referencia`. Nunca chegar dá os consumos totais com `censurado: True` (censura à direita, plano do N5).
- **Tabela parcial:** as medidas do N5 têm `None` em vidas sem consumo na janela; `tabela_braco_condicao_parcial` exige a grade completa e
  conta as vidas sem valor por célula, com IC só a partir de dois valores. As medidas de sempre seguem na `tabela_braco_condicao`.
- **No mutável, um item do P2a levado para o outro lado da troca deixa de ser verdadeiro**: o conteúdo é o verdadeiro no tick original (o
  mesmo multiconjunto do P2), como o plano manda.
- **Testes antigos mudaram porque os lobos agora veem o mundo:** o `bola_a1` com lobos é o braço "bola" da A1 (antes "bolacega"); o acoplado
  P3 → P0 no mundo da bola é o instinto que vê a bola; o P0 com lobos nas frutas come fruta (antes 0 consumos); P2/P2e fora das frutas
  levantam `ValueError` (antes `NotImplementedError`).

## 2026-10-04 — N5-CEREBRO (chat B, `docs/TAREFA_V2_N5_CEREBRO.md`)

- **`w0_info = 0` desliga a entrada `info`, em vez de começar o peso em zero e deixá-lo aprender.** A tarefa pede que, com w0 = 0, a vida
  seja a de hoje byte a byte; com um peso em zero que aprende, a primeira fruta informada comida com sinal ≠ 0 já mudaria a vida do P2
  em relação ao P1. O plano (seção 8) usa w0 = 0 como referência descritiva, fora da escolha: com a entrada desligada essa referência é
  o P1. Se o Matheus quiser a variante "parte de zero e aprende", é um campo a mais, sem mudar o resto.
- **Piso no peso efetivo da fruta informada, mesmo com o aprendizado desligado.** Com o "mal", (w_f/S)·incentivo − (w_info/S) pode ser
  negativo (incentivo 0,5 e w0 S/2 dá zero); o piso do aprendiz (`piso_peso`/S = 1/16) evita peso não positivo no sorteio. Só vale na
  fruta com informação vigente; nas outras o peso é o de hoje (por isso a vida sem informação não muda).
- **O peso da informação aprende pela mesma regra da L1, somada sobre as frutas candidatas**, porque é um parâmetro só presente em
  todos os pesos efetivos (o gradiente de log p(f*) em relação a ele é a soma). Cortado em w0 ± teto (o teto da `ConfigLobos`): com w0 na
  grade, abaixo do teto, o zero fica ao alcance (seção 3 do plano). O corte conta em `cortes_teto` e `pesos_no_teto`.
- **"Nunca pelo dono" vale só para o peso da informação.** Os pesos de cada fruta seguem aprendendo também com elogio e bronca no P3,
  como desde o LOBOS-MUNDO; a tarefa só restringe o peso da `info`.
- **Sem mudança em `frutas.py` nem na bancada:** a informação chega pela `Observacao` que o `MotorFrutas` já injeta (#140), e a lida é
  guardada no `agir` da mesma decisão em que a fruta é escolhida.

## 2026-10-04 — V2, N5-ACOPLADO: informante acoplado e motivo das regras novas dos lobos (`docs/TAREFA_V2_N5_ACOPLADO.md`)

- **O acoplado recebe o multiconjunto de quem o monta.** O P2 da unidade usa o `CalendarioFrutas` da bancada, e o `digilab/` não importa
  `experiments/`; o `DonoInformante.acoplado` recebe as frutas do P2 (ou o informante certo de uma vida P2 já jogada, `acoplado_de`) e a
  semente da unidade. O conteúdo vem do efeito real, então o multiconjunto (fruta, conteúdo) é o do P2.
- **Sorteio dos ticks:** um passo do dono por item, uniforme entre os `dias × 1440 / passo` passos da vida, com reposição (dois itens
  podem cair no mesmo passo); o multiconjunto é ordenado (ordem de `FRUTAS`) antes do sorteio, para a ordem de entrada não mudar a agenda.
  O plano diz "ticks sorteados uniformemente na vida"; o passo do dono é o único momento em que o informante age.
- **Interface nova `acoes_do_passo`**, chamada em todo passo do dono (antes, o informante só era chamado quando havia oferta). Para
  certo e errado é o `acoes` de sempre com a mesma lista; o gabarito gravado **antes** da mudança (24 vidas) prova o byte a byte.
- **Achados no motivo, corrigidos:** (1) o `motivo_instinto` levantava erro em `bola_no_cenario` e `fruta_no_cenario` (o
  `PoliticaInstintoFrutas` é subclasse do `PoliticaInstinto`, e o `PoliticaComMotivo` caía no ramo do instinto); (2) o ramo aprendido do
  `motivo_lobos` só lia as 10 entradas de sempre e ignorava `bola` e `fruta`; (3) o `PoliticaComMotivo` não repassava `escolher_fruta` nem
  `fruta_comida`, então a vida embrulhada mudava com os lobos que veem as frutas (a escolha caía no motor e o E2 não chegava ao aprendiz).
- **O fator da fruta ocupa o segundo lugar** (o `Motivo` aceita no máximo 2): na decisão de comer com fruta, o primeiro fator é o da
  decisão (regra ou aprendido) e o segundo, se houver, é o da escolha da fruta.
- **Os incentivos vêm pelo gancho:** o registro dos lobos (`motivos[-1]["fruta"]`) guarda presentes, pesos, u e escolhida, mas não os
  incentivos; o `PoliticaComMotivo._escolher_fruta` os recebe na chamada e refaz o motivo. Chamar `motivo_lobos` com o registro da fruta e
  sem os incentivos falha alto. `lobos.py` não mudou.
- **Honestidade por contrafactual com o mesmo u:** a bola só é fator se brincar sem o termo da bola (1 + 3·humor) não sairia; a fruta só é
  fator se, sem comer como candidato, a ação seria outra; a escolha da fruta é `incentivo_fruta` quando o incentivo puro dá a mesma fruta,
  senão `escolha_aprendida_fruta`. Com o aprendizado desligado o peso é o prior S e a escolha é sempre do incentivo (teste).
- **Teste ajustado:** `tests/test_informacao.py::test_informante_certo_e_errado_nos_mesmos_ticks_com_conteudo_oposto` exigia que o modo
  `acoplado` não existisse; agora confere um modo desconhecido e o acoplado montado sem o construtor (os dois falham alto).

## 2026-10-04 — N6-PLANO: plano da memória de episódios no papel; interpretações

Tarefa `docs/TAREFA_V2_N6_PLANO.md`; entrega `docs/PLANO_ANALISE_V2_N6.md`. Nenhuma run, nenhum código.
- **O número de 6,9% está em outro arquivo.** A tarefa aponta `artifacts_v1_memoria_espacos/metrics.json`, mas a fração de motivos que
  citam memória está no `espacos.json` da mesma pasta (`fracao_motivos_citam_memoria_total` 0,0692; `por_braco` de 0,0625 a 0,0778). O
  plano cita o `espacos.json`.
- **A comparação com a v1 muda de denominador.** Na v1 a memória entrava em toda decisão; no N6 ela só age nas sub-decisões com duas
  frutas ou mais (decisão N6-1 do plano). Sobre todos os motivos o N6 fica abaixo de 6,9% por construção (no máximo ~1,8% com 24 escolhas
  em 14 dias). O gate G-CITA compara as decisões em que a memória pode agir nos dois casos; a fração sobre todos os motivos é só descritiva.
- **Memória sem aprendizado do lobo de decisão.** Os braços de memória rodam sobre o P0 (pesos no prior), para a memória ser a única
  plasticidade. Com o P1, o peso `w_f` já guarda a associação, e a diferença não separaria episódio de associação (secundário descritivo).
- **"Estado atual igual" em dois níveis:** na decisão, pela sonda contrafactual (a mesma escolha refeita com a contribuição da memória
  zerada, com o mesmo `u`); na vida, pelos acoplados no registro do braço relevante (`M0<MR`, `MT<MR`, `ME<MR`: mesmo cuidado, mesmas
  ofertas, mesmo genoma).
- **Espaços sem `exp`.** A ativação da v1 decai por `exp`; os lobos não usam função transcendental (paridade com a web). No N6 o
  esquecimento vem só da regra dos espaços; relembrar fica desligado (candidato da L2 pela D7).
- **Faixas propostas** 19101…19505 (calibração) e 20101…20505 (validação), conferidas contra `FAIXAS_RESERVADAS`, o roadmap e a busca no
  repositório. As `FAIXAS_RESERVADAS` da bancada não listam hoje o N11 (16101…17505) nem a revisão do aprendiz (18101…18505); fica para
  quem implementar.

## 2026-10-04 — Rodada 6: merges e decisões N6-1 a N6-10

- Mesclados #148 (bancada com os lobos vendo o mundo e os braços P2, P2e, P2a), #147 (entrada `info` dos lobos), #149 (informante
  acoplado e motivo das regras novas, com a correção do `PoliticaComMotivo`) e #146 (plano do N6). Suíte completa depois dos merges de
  código: 876 passados, 1 pulado.
- O Matheus aprovou N6-1 a N6-10 do `docs/PLANO_ANALISE_V2_N6.md`, como recomendadas. Faixas do N6 fechadas: 19101…19505 e 20101…20505.
- Liberada a revisão do aprendiz (`docs/TAREFA_V2_REVISAO_APRENDIZ.md`, chat B, 18101…18505).
- Pendência de código para o chat D: incluir 18101…18505, 19101…19505 e 20101…20505 em `FAIXAS_RESERVADAS` da bancada.

## 2026-10-04 — REVISAO-APRENDIZ (chat B, `docs/TAREFA_V2_REVISAO_APRENDIZ.md`)

- **O traço de elegibilidade no lugar da "consequência atrasada" do N3.** O plano do N3 declarava medir os drives até a decisão seguinte,
  o que põe o cuidado do dono no sinal. O traço não muda o que o sinal mede, só a quem ele chega (as K decisões anteriores, com λ^k).
  Vale para a consequência e para elogio e bronca, como no COACH. Latência e chamado ignorado ficam presos ao chamado.
- **Uma linha de mudança na bancada (do chat D):** `rodar` passa a montar a `Bancada` por `bancada_da_config`, que lê `consequencia` (como
  antes), `lobos` e `frutas`. Sem as chaves novas, a bancada de sempre (teste).
- **O motivo rejogado no motor das frutas.** `motivo.motivos_de_vida` rejoga no `MotorComFeedback`, sem as frutas. O orquestrador da
  revisão rejoga com o motor da bancada e confere a vida: log, estado, ações, rngs, consumos e incentivos. Não confere o `resumo_frutas`
  inteiro, porque o registro das ofertas guarda a `regra` da política, que o `PoliticaComMotivo` não repassa (sai `None`). Isso é para o
  chat A, se quiser o campo igual.
- **Unidades contadas sozinhas no bootstrap**, sem agrupar por base (o plano diz isso; o agrupamento é do N5 e do experimento maior).
- **A trava "piora o cuidado de si" não informou nada:** com o atencioso, a privação é 0 e a saúde não muda em nenhuma vida, em nenhum
  ponto. Ficou registrado no relatório.
- **A regra escolheu o teto pelo P3.** No P1 o teto não muda nada nas frutas; no P3 o aprendido decide mais e o acerto na tarefa cai. Pelo
  risco 2 do plano, o relatório compara T3 com T2.
- **Duas análises pós hoc, declaradas** (`pos_hoc_pesos_fruta.json`, `pos_hoc_oferta_unica.json`): os pesos da escolha da fruta no fim da
  vida e os consumos por número de frutas no cenário. Daí sai a decisão R2 (a decisão de comer não sabe qual fruta está lá), que o plano
  não previa.
- **Vidas no git só da base** (120 `.jsonl`, ~10 MB). Os pontos T, J e X são regeneráveis pela config; o resumo de cada um fica em
  `resultado.json` e `medidas.json`.

## 2026-10-05 — Fim da rodada 6: decisões R1–R4 e tarefas da rodada 7

- O Matheus aprovou R1–R4 da revisão do aprendiz (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`), como recomendadas:
  - R1: o ponto de partida das calibrações é o T3 (teto 16·S);
  - R2: a decisão de comer passa a ver qual fruta está no cenário (tarefa dividida entre o chat A, no mundo, e o chat B, no cérebro);
  - R3: o traço de elegibilidade fica desligado;
  - R4: a exposição fica como está.
- A N5-2 continua: a informação do dono só entra na escolha de qual fruta.
- Marco em `docs/V2_RODADA_6.md`.

## 2026-10-05 — N7-PLANO: plano da arbitragem (necessidade × pedido do dono) no papel; interpretações

Tarefa `docs/TAREFA_V2_N7_PLANO.md`; entrega `docs/PLANO_ANALISE_V2_N7.md`. Nenhuma run, nenhum código.
- **"Pedido do dono" é um evento novo, não a informação do N5.** A tarefa admite "o pedido (ou a informação)". O plano escolhe o pedido
  ("deixe a fruta X") porque a informação é uma afirmação sobre o mundo, que a consequência valida, e o N5 a pôs só na escolha da fruta
  (N5-2), onde não há conflito com a necessidade. Os nomes (`PEDIR_DEIXAR_FRUTA_<A|B|C>`, `Observacao.pedido_frutas`, `ConfigPedido`,
  `DonoPedinte`) são propostas a combinar com o chat A.
- **A arbitragem é a das regras que já existem.** As regras urgentes do instinto (sono, fome ou higiene abaixo de 0,25, abandono) vêm
  antes e não leem o pedido; o pedido pesa só onde `comer` é candidato e a necessidade não é urgente. Nenhuma curva de urgência nova
  (decisão N7-3).
- **Mundo `iguais_frutas`, que a bancada ainda não tem.** Sem efeito próprio de fruta, obedecer ou desobedecer só custa a fome; no
  descasado a consequência da fruta premiaria ou puniria a obediência.
- **A marca se mede numa fase de extinção.** Com a janela de 240 min e a fruta ficando 120 min, X nunca aparece sem pedido vigente; por
  isso os pedidos param no dia 10 e a marca é a fração de X nos dias 11–14.
- **A ressalva literal da D7** ("inspirada no Dwarf Fortress; o análogo citado é inspiração declarada, não validação") está no topo do
  plano. Rossi et al. e Fróes e Gudwin entram só como pista do corpus.
- **Faixas propostas** 21101…21505 e 22101…22505, fora das reservadas, de 18101…20505 e do N11; nenhuma base aparece no repositório
  fora dos artefatos.

## 2026-10-05 — V2, BANCADA-EXPERIMENTO: faixas, o ponto T3 e o orquestrador do experimento maior (`docs/TAREFA_V2_BANCADA_EXPERIMENTO.md`)

- **Faixa do N11 também entrou.** A tarefa pede 18101…18505, 19101…19505 e 20101…20505; o N11 (16101…16505 e 17101…17505, seção 6 do
  `docs/ROADMAP_V2.md`) faltava nas `FAIXAS_RESERVADAS` desde a BANCADA-FRUTAS (o `PLANO_ANALISE_V2_N6.md` registrou). Acrescentado com a
  fonte; as unidades derivadas continuam fora de todas.
- **O T3 é só o teto.** `PONTOS_APRENDIZ["T3"]` = teto 16·S sobre o `CONFIG_LOBOS_APRENDIZ` (passo 512, sem traço), como o T3 da revisão.
  O resto do "ponto recomendado" da revisão (ganho 4, E2, `w_fruta` 6, 4 ofertas por dia) já é o padrão da `ConfigConsequencia` e da
  `ConfigFrutas`. O `w0_info` do N5 **não** faz parte do ponto: é calibrado no N5 (grade {S/4, S/2, 3S/4}) e entra pela chave `lobos`,
  por cima do ponto. Sem o campo `ponto`, o `L1`: nenhuma run antiga muda.
- **"Só cuidado" do experimento:** o mesmo braço no próprio registro com o filtro `sem_ensino` (sem elogio, bronca e informação; as ofertas
  e o cuidado ficam), para P2, P2e e P3. No P3 isso é o "sem sinais" de sempre (ele não recebe informação).
- **O controle de capacidade sem lobos (E6) não roda.** A bancada só tem os cérebros `lobos` e `instinto`; pôr o `camada_unica` nela é do
  N11. É secundário e descritivo, e nenhuma predição depende dele; fica para quando a bancada tiver o cérebro.
- **Referência do mundo padrão só com P0, P1 e P3:** P2 e P2e não existem fora das frutas (BANCADA-N5). Só descritiva (E1).
- **Δ usa a janela final** do P0 no descasado (a janela das predições 1, 2, 4b e 5), média das unidades com consumo. Se o P0 nunca come
  a fruta ruim, Δ = 0 e a equivalência não pode confirmar; com Δ indefinido (nenhum consumo) as leituras não refutam por equivalência.
- **p unilateral do bootstrap = fração das médias reamostradas ≤ 0** (o zero conta como lado oposto: conservador). Com menos de 2 sementes
  com valor não há p; no Holm, p ausente conta como 1, para a família não encolher.
- **Predição 2 com uma condição confirmando e a outra refutando: refuta.** O plano diz "refuta: em qualquer das duas" e "confirma
  parcialmente: só uma das duas"; na colisão, o refuta vence. **Inconclusivo por duração** vale no lugar de refuta ou inconclusivo quando
  uma condição que não confirmou ainda tem a inclinação de P0 − P1, nos 4 últimos dias (11 a 14 numa vida de 14), com IC 95% acima de 0;
  a inclinação é por unidade (mínimos quadrados sobre os dias com consumo nos dois braços), com bootstrap sobre as sementes.
- **Predição 4, "refuta a recuperação":** só quando (a) foi confirmada por Holm; sem a piora, o resto é inconclusivo. O dia do cruzamento é
  o primeiro dia em que a média do P2e fica ≤ à do P0, depois de um dia acima.
- **Predição 5 sem o K4.** O dono do P3 não julga a escolha de fruta (`donos.julgar_acao` não olha a fruta); o contrato K4 (E7) não está na
  `main` e não é desta tarefa (não mexo nos donos nem em `frutas.py`). O plano só dá "não testável" para o K2; para o K4 a predição 5 sai
  calculada, com `k4: false` e o aviso de que mede só que o P3 não sabe das frutas. **Para o coordenador:** decidir quem entrega o K4 e se,
  sem ele, a predição 5 vira "não testável".
- **Separação do cuidado (5.1):** (a) braço − só cuidado na direção do contraste, IC 95% acima de 0; (b) "sem diferença" = IC 95% contendo 0
  na saúde média e no tempo fora de privação. Nos mundos das frutas não há morte (lesões desligadas), então mortes não entram.
- **N por contraste:** a fórmula da seção 7.2 com α/6 (o passo mais exigente do Holm), poder 0,8, múltiplo de 5. A conferência por
  simulação com bootstrap das unidades fica para o adendo da seção 7.3 (é ele que fixa o N).
- **Modos:** pelas bases. Calibração e validação pedem o campo `plano` igual a este plano (não basta um arquivo qualquer do repositório,
  como na bancada), as unidades derivadas e a vida de 14 dias (E5); a validação exige o Δ do adendo e a calibração recusa um Δ dado.
- **A fumaça liga `w0_info` = S/2** (um ponto da grade do N5) só para a informação agir e o encanamento de P2/P2e ser exercitado; não é
  escolha do valor, que é do N5.

## 2026-10-05 — V2, FRUTA-NO-CENARIO, parte A: `Observacao.frutas_cenario` (`docs/TAREFA_V2_FRUTA_NO_CENARIO.md`)

- **Valores binários (1,0 ou 0,0) e padrão `(0,0, 0,0, 0,0)`**, como o `info_frutas`: a tarefa pede "a presença de cada fruta". O
  incentivo de cada fruta não entra no campo (a parte B decide como pesar; o `MotorFrutas` já guarda os incentivos).
- **A presença é a da decisão:** o campo sai de `_na_decisao`, a lista que o motor monta logo antes de `agir` (frutas vencidas já fora) e
  que a sub-decisão de comer usa depois. Com isso a percepção e a escolha da fruta veem sempre as mesmas frutas (teste decisão a decisão).
- **O G2 é um gabarito gravado antes da mudança**, pela bancada (os braços P0 a P3 nos três mundos das frutas, com os lobos que veem o
  mundo, a E2 e a informação), e não uma comparação entre dois códigos no mesmo processo: o campo é aditivo e ninguém o lê, então a vida
  só mudaria por um efeito colateral da injeção (ordem das chamadas no motor), que o gabarito pega.
- **O teste da presença usa o instinto das frutas por baixo de um espião** (que só anota a `Observacao` e delega), porque nenhuma
  política de hoje lê o campo.

## 2026-10-05 — N7: decisões N7-1 a N7-10 aprovadas como recomendadas

- O Matheus aprovou N7-1 a N7-10 de `docs/PLANO_ANALISE_V2_N7.md` como recomendadas ("segue o recomendado"); o plano registra isso no
  status e na seção 15. Nenhum número, gate ou faixa mudou.
- Com a N7-9, as faixas 21101…21505 (calibração) e 22101…22505 (validação) ficam pedidas ao coordenador; entram nas `FAIXAS_RESERVADAS`
  quando ele as fechar.

## 2026-10-05 — N7-1 a N7-10 aprovadas; tarefas paralelas da rodada 7

- O Matheus aprovou N7-1 a N7-10 do `docs/PLANO_ANALISE_V2_N7.md`, como recomendadas. Faixas do N7: 21101…21505 e 22101…22505.
- A FRUTA-NO-CENARIO parte A foi mesclada (#154), e o chat B segue com a parte B e o N5.
- Enquanto isso, os outros chats recebem tarefas paralelas que não mexem no `lobos.py`:
  - A: N7-MUNDO, o lado do mundo do pedido do dono;
  - D: BANCADA-N6-N7;
  - C: LEITURA-PARCIAL, com a lista das validações a refazer.

## 2026-10-05 — V2, FRUTA-NO-CENARIO, parte B (chat B, `docs/TAREFA_V2_FRUTA_NO_CENARIO.md`)

- **Montada sobre o branch da parte A.** O pedido era começar quando a parte A (#154) estivesse na `main`. Quando o Matheus avisou, o
  #154 ainda estava aberto (o que entrou foi o #155). O branch `v2-comer-ve-fruta` partiu da `main` com o `v2-fruta-no-cenario-mundo`
  mesclado (conflito só nas seções do fim do `CLAUDE.md` e deste registro; ficaram as duas). O PR depende do #154: mesclar a parte A antes.
- **Um termo somado, não uma entrada na percepção.** "Uma entrada por fruta presente na decisão de comer" virou três pesos só para comer
  na regra `fruta_no_cenario`. Na percepção, as três entradas iriam a todas as regras e ações (189 pesos) e aprenderiam também pelo dono, e a
  tarefa pede que aprendam só pela consequência.
- **Prior 0, somado ao peso do instinto.** O instinto pesa comer por `w_fruta × fruta` (o maior incentivo), que não se escreve como soma
  sobre as frutas; com prior 0 o termo novo é 0,0 exato e o resto fica como está.
- **Os pesos de presença sobem para todas as frutas na vida.** Comer dá sinal positivo pela nutrição (a fome entra no sinal da E2), então o
  que a E2 ensina é a diferença entre as frutas, e a decisão é relativa. O teste da bancada confere que a ruim fica abaixo das outras; o
  teste unitário, com o pet saciado, confere que só a ruim desce.
- **Só a regra das frutas.** Na `fome_moderada` o pet também come a fruta que estiver no cenário, e a decisão de comer lá não lê a fruta. A
  tarefa fala da regra `fruta_no_cenario`; a outra fica como está.
- **Teste da parte A ajustado** (`tests/test_frutas_cenario.py`, chat A): o gabarito foi gravado antes das duas partes. O P0 e o P3 seguem
  byte a byte, com o estado interno normalizado (sem os pesos de presença, no prior, e sem a `presenca` dos registros). As vidas que aprendem
  pela consequência (P1, P2, P2e, P2a) mudam por desenho e ficam fora.

## 2026-10-05 — LEITURA-PARCIAL: a fase 1 até aqui e as validações a refazer; interpretações

Tarefa `docs/TAREFA_V2_LEITURA_PARCIAL.md`; entrega `docs/LEITURA_PARCIAL_V2_FASE1.md`. Nenhuma run, nenhum código.
- **Nenhum dado gravado foi relido com medida nova.** O G-SSE do N4 com a medida N1 fica como validação nova opcional (LP-4), não como
  reanálise das vidas de 11101…11505.
- **As refeitas são só validação**, no ponto já fixado (o T3 da revisão; o ponto da A1), com os gates e alvos de antes; as validações
  antigas e os artefatos delas ficam como estão.
- **A A1 é refeita pelo B1/B2, não pelo teto:** a A1 não tem aprendizado, e o P0 com lobos é o instinto byte a byte; o que mudou e toca a
  falha dela é o aleatório pôr bola dentro do orçamento.
- **O N4 e o 1a-pet da A1 ficam valendo** sem refazer: nenhuma das cinco mudanças altera a vida do P0 (testes de byte a byte citados).
- **Faixas propostas** 23101…23505 (A1-B), 24101…24505 (L1-T3), 25101…25505 (N3-T3, opcional) e 27101…27505 (N4-N1, opcional); a
  26xxx foi pulada porque 26505 aparece como tick num gabarito da web.

## 2026-10-05 — Estratégia nova da V2: montar tudo, calibrar junto, validar uma vez (decisão do Matheus, M10)

- O Matheus apontou que calibrar e validar nó a nó gasta trabalho que as peças seguintes invalidam. A L1 e o N3 são exemplos: foram
  validados antes do teto 16·S, da E2 e do cérebro vendo o mundo. Decisão: **montar o cérebro inteiro com testes de mecanismo,
  calibrar uma vez, validar uma vez**, com cada peça como braço de ablação.
- `docs/ROADMAP_V2.md` passa à revisão 3.
- `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` ganha o adendo 1, antes de qualquer dado: as ablações ficam como contrastes
  secundários, fora da família de Holm.
- A calibração e a validação do N5 não rodam. O chat B já tinha parado (nota `a810d03`, branch `v2-n5-calibracao`, nenhum número), e a
  faixa 13101…13505 ficou intacta.
- As faixas próprias do N5, do N6 e do N7 ficam sem uso.
- As decisões LP-1 a LP-3 de `docs/LEITURA_PARCIAL_V2_FASE1.md` (refazer A1, L1, N3) ficam substituídas pela M11: as validações já
  feitas viram histórico.
- Tarefas novas:
  - `docs/TAREFA_V2_CEREBRO_N6_N7.md` (B, etapa C1);
  - `docs/TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA.md` (C, etapa K1).

## 2026-10-05 — K1: plano da calibração conjunta e adendo de tamanho de amostra; interpretações

Tarefa `docs/TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA.md`; entrega `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`. Nenhuma run, nenhum código.
- **A regra de calibração do N5 (N5-1) lia uma predição primária.** Ela escolhia o `w0_info` pelo contraste P2e − P1 na janela inicial,
  que é a predição 4(a) do experimento maior, dentro da família de Holm. Com a calibração conjunta nas mesmas bases do experimento, o
  plano propõe trocá-la (decisão K-3) por uma verificação de manipulação: a fração das escolhas de fruta com informação vigente decididas
  pela informação (sonda contrafactual), com o mesmo piso de 0,069 da memória (N6-10).
- **A seção 8.2 do experimento maior** ("nada do aprendiz se calibra aqui") foi escrita antes da revisão 3 do roadmap; a calibração que
  era de cada nó passou para o K1. As predições e a estatística não mudam.
- **P0 com tudo desligado** (decisão K-1): a memória, a informação, o pedido e os canais só nos braços que aprendem, para o P0 seguir
  sendo o instinto byte a byte (contrato K1).
- **A grade do ganho do P1 sobe ({4, 8, 16})** porque no T3 com ganho 4 a deriva ainda cresce no fim da vida (razão 14/7 de 2,92 e 2,64,
  `artifacts_v2_revisao/calibracao/T3/resultado.json`).
- **Os blocos N6 e N7 usam as unidades do experimento maior**, não as derivações próprias dos planos deles (`"n6"`, `"n7"`), para o
  pareamento atravessar os blocos.
- **O controle de capacidade sem lobos (E6) fica fora**: a bancada não tem o `camada_unica` (é do N11).
- **O custo** foi estimado pela revisão do aprendiz (~5,5 s por vida: 1 h 50 min para 1200 vidas); é estimativa, não medida desta run.

## 2026-10-05 — V2, N7-MUNDO: o pedido "deixe a fruta X" e o dono que pede (`docs/TAREFA_V2_N7_MUNDO.md`)

- **`config.py` e `protocol.py` também mudaram**, fora da lista da tarefa ("só `events.py`, `frutas.py`/`ambiente.py`, `policy.py`"): os
  números novos (`janela_min`, `dias_pedido`) e a chave têm de ficar em `config.py` (regra do projeto), na `ConfigPedido` que o plano nomeia,
  e todo parâmetro novo tem registro de status e fonte (`protocol.PARAMETROS_PEDIDO_N7`, como a informação do N5). Nenhum hash cobre esse
  registro. `ambiente.py` não precisou mudar.
- **`dias_pedido` virou parâmetro** (10, PROPOSTO), em vez de um 10 fixo no `DonoPedinte`: é a fase da decisão N7-7.
- **A desobediência é medida na percepção da decisão:** o motor marca o consumo de uma fruta que tinha −1 em `pedido_frutas` na decisão em
  que o pet comeu (não no tick do consumo depois do avanço). Assim "comer X com pedido vigente" é o mesmo pedido que o aprendiz viu.
- **A bronca lê o motor pelo `estado()`:** o `DonoPedinte` recebe o `estado()` do motor (como a regra do mundo da bancada recebe a `Visao`) e
  dá uma `repreender` por desobediência nova desde o passo anterior. Sem a chave no motor, `estado()` não tem `desobediencias` e o dono que
  pede falha alto (`KeyError`). A bronca vem antes dos pedidos do passo.
- **"Primeiro passo do dono depois do consumo":** a decisão do tick d acontece no avanço que começa depois do passo do dono em d, então a
  bronca sai no passo seguinte: 0 < t − d ≤ 15 (teste).
- **A bronca é uma `repreender` comum**, fora do orçamento: conta como contato e passa por `receber_acao_dono` (é o dono que mexe no P3+ped).
  Quem mede o crédito dela (risco 3 do plano) é a análise do N7.
- **O G2 é um gabarito gravado antes da mudança** (48 vidas, num commit só com ele) e, para a bancada, as 168 vidas de
  `tests/test_frutas_cenario.py`, que seguem passando.
- **Sorteio da fruta:** `FRUTAS[rng.randrange(3)]` com a rng `pedido-fruta`, só pela semente da unidade (não pelo genoma), como pede o
  plano; o teste confere em 600 sementes que a fruta pedida coincide com a preferida de nascença em cerca de 1/3 delas.
- **A bancada ainda não conhece o pedido** (chat D): `contar_acoes` contaria um pedido como interação do dono e o `sem_ensino` não o tira.
  Isso fica para quem montar os braços com pedido; nenhuma vida de hoje tem pedido.
- **Teste ajustado:** `tests/test_informacao.py::test_parametros_registrados_e_enum_no_fim` conferia as informações como "as seis últimas"
  do enum; agora confere as posições 20 a 25 (o pedido vem depois delas), como já se fez com as ofertas.

## 2026-10-05 — CEREBRO-N6-N7: memória de episódios e arbitragem do pedido nos lobos; interpretações

Tarefa `docs/TAREFA_V2_CEREBRO_N6_N7.md` (etapa C1), planos `docs/PLANO_ANALISE_V2_N6.md` e `docs/PLANO_ANALISE_V2_N7.md`. Só testes de
mecanismo; nenhuma run com faixa reservada. A calibração e a validação do N5 não rodaram (nota `a810d03` fica como registro).
- **O campo do pedido não está na main.** O chat A (`docs/TAREFA_V2_N7_MUNDO.md`) tem o branch `v2-n7-mundo` com
  `Observacao.pedido_frutas` (−1 na fruta pedida, 0 nas outras, na ordem de `FRUTAS`), o mesmo nome da seção 2 do plano do N7. Os lobos o
  leem por `getattr(obs, "pedido_frutas", ())`: sem o campo, nenhum pedido. Os testes injetam o campo por uma subclasse da `Observacao`.
  Quando o branch do A entrar, nada aqui muda; com `w0_pedido` 0 o campo nem é lido.
- **Memória e pedido só nos lobos que veem as frutas.** Os episódios são de consumo de fruta e o pedido é sobre fruta; nos lobos sem
  `cfg_frutas`, ligar as chaves não cria nada (e a memória exige `efeito_humor_ruim` ≠ 0, porque a valência é medida nele).
- **M0 = memória ligada com ganho 0**: guarda os episódios e as sondas, mas m_f = 0; as decisões são as do P0 (teste). O estado interno do
  M0 difere do P0 só pelas chaves da memória.
- **A valência usa o humor da decisão e o humor logo depois de comer** (o par antes/depois da E2): é o que o `fruta_comida` já recebe.
  Tudo o que o humor mudou entre os dois entra, não só o efeito da fruta (o `MotorFrutas` aplica a nutrição na fome e o efeito no humor).
- **O tick da memória vem da hora da observação** (`vetor_estado[7]`), com o dia virando quando a hora volta: a política não vê o tick
  do motor. Numa vida decisões chegam a cada 15 min, então nenhum dia é pulado.
- **A memória age só na escolha da fruta**, como manda o plano (ganho g < S somado ao coeficiente da fruta). A decisão de comer não lê a
  memória; com uma fruta só no cenário a memória não muda nada (a sonda conta só as escolhas com duas frutas ou mais).
- **Recuperação:** o episódio mais forte da fruta da pista nos dois prazos; empate, o mais recente. No embaralhado a pista f recupera o de
  π(f); na recência só valem os de idade ≤ 240 min.
- **O peso do pedido aprende com o sinal de qualquer fonte** (a consequência no P1, o dono no P3), como a seção 3 do plano do N7 descreve
  a confiança no pedido; diferente da informação do N5, que só a consequência mexe.
- **O piso vale no comer e na fruta quando o termo do pedido está ativo**, com o aprendizado ligado ou não, como na informação do N5: o
  pedido pode levar o peso abaixo de zero.
- **A sonda do pedido só é gravada quando p ≠ 0 numa regra de `REGRAS_PEDIDO`**: nas outras decisões não há o que contrafazer.
- **O braço ME depende da bancada:** a permutação é passada pela config (`memoria_permutacao`), porque a política não conhece a semente da
  vida; o chat D monta `desarranjo_n6(semente)` por vida. Permutação fora do modo embaralhado, ou que não seja um desarranjo de `FRUTAS`,
  é recusada.

## 2026-10-05 — V2, BANCADA-N6-N7: o mundo iguais_frutas, os braços do N6 e do N7 e as medidas (`docs/TAREFA_V2_BANCADA_N6_N7.md`)

- **`iguais` é uma condição nova da bancada**, fora da pergunta maior (casado, descasado, mutável). Ela só existe para o N7 (N7-5), com o
  efeito do mundo "iguais" do N4 (`efeito_humor_neutro` em todas). A coluna da tabela é `iguais/iguais_frutas`.
- **No `iguais_frutas` não há fruta ruim:** a `taxa_fruta_ruim` sai 0 e os `consumos_ate_metade` saem `sem_referencia` (sem caminho até a
  metade), em vez de um número sem sentido. O informante (P2, P2e) segue o efeito real: "bem" de toda fruta no P2, "mal" no P2e.
- **Todos os braços do N6 falham alto, inclusive o M0.** O M0 decide como o P0, mas registra e codifica os episódios (marcos 1 e 2), e
  isso é o lobo de memória do chat B. Rodar um M0 sem memória seria rodar o P0 com outro nome.
- **Os braços do N7 falham alto com o nó** até o pedido existir dos dois lados (o mundo, chat A; a entrada `pedido` dos lobos, chat B). O
  P3 sem pedido do N7 é o P3 de sempre e já roda.
- **A trava é uma tabela só** (`NOS_PENDENTES`): o braço se resolve quando a entrada sai (teste). O que ainda falta ligar quando as peças
  chegarem está na seção da BANCADA-N6-N7 no `CLAUDE.md`: a política, a regra do mundo do pedido, o `sem_ensino` com os pedidos e os
  pedidos fora do orçamento.
- **Filtros do N7 pendentes** (`sem_pedido`, `sem_ensino_sem_pedido`): nomes escolhidos aqui; o plano só diz que o "só cuidado" do P3+ped tira
  pedidos, broncas e sinais (as broncas são `repreender`, já nos sinais). O `filtro_de` falha alto com o nó; o acoplar passou a usá-lo.
- **O desarranjo do ME já existe** (N6-6) porque não depende do cérebro: um dos dois ciclos de {a, b, c} por `derivar_semente("n6-embaralha",
  semente)`.
- **Unidades derivadas com prefixo:** os planos do N6 e do N7 usam `derivar_semente("n6"|"n7", b, k)` e `"…-genoma"`. A função ganhou o
  prefixo, com o do experimento maior como padrão (as unidades de antes não mudam).
- **Medidas pelo que o cérebro vai registrar:** as funções recebem registros simples (a sub-decisão com a escolha e a escolha da sonda
  contrafactual; a decisão de conflito com "comeu" e "comeria sem o pedido"). A sonda em si (refazer a escolha com o termo zerado e o
  mesmo u) é do cérebro (chat B), como o motivo das regras novas. A G-URG conta, fora das zonas de conflito, toda decisão em que o pedido
  mudou o resultado.
- **A fração de X conta só ofertas com X e outra fruta** (plano do N7, seção 6): com X sozinha, deixar X não é escolha entre frutas, e ela
  entra na deferência (a decisão de comer).
- **Dois testes de contrato mudaram:** `test_bancada_mundos.py::test_contrato_das_condicoes` (as condições agora incluem `iguais` e o
  mundo `iguais_frutas`) e `test_bancada_v2.py::test_engine_intocado_e_bracos_com_fonte_e_no` (a tabela dos braços inclui os do N6 e do N7,
  com fonte e nó). Nenhum braço ou mundo antigo mudou.

## 2026-10-05 — Rodada 9: K-1 a K-11 aprovadas; o K4 e a bancada antes dos cérebros B e C

- O Matheus aprovou as decisões K-1 a K-11 de `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`, todas como recomendado.
- A divisão da rodada 9 do roadmap mudou: o chat A faz o K4 (o dono do P3 julga a fruta) e o chat D liga o N6 e o N7 na bancada.
  - Motivo: a K2 precisa dos dois.
  - Os cérebros B e C passam para a rodada 10.
  - O chat C escreve o plano da comparação A × B × C no lugar da revisão do K1, que já foi decidida.
- Notas de superado:
  - `docs/LEITURA_PARCIAL_V2_FASE1.md` ganha a seção 6, que marca as decisões LP como substituídas;
  - `docs/PLANO_V2_PESQUISA.md` ganha a nota da fase 1.

## 2026-10-05 — V2, BANCADA-LIGA-N6-N7: a memória e o pedido ligados na bancada (`docs/TAREFA_V2_BANCADA_LIGA_N6_N7.md`)

- **As chaves do N6 e do N7 pertencem ao braço.** `cfg_lobos_do_braco` liga a memória só nos M0–ME e o `w0_pedido` só nos braços com pedido,
  e devolve as chaves ao padrão nos outros. Assim a mesma config (com `memoria_ganho` e `w0_pedido`) roda todos os braços sem mudar os
  antigos (teste contra o gabarito). O ganho dos MR, MT e ME vem da config; ganho 0 é aceito (é o M0 com outro nome), como o `w0_pedido` 0,
  que o plano do N7 roda como referência.
- **O M0 tem ganho 0 sempre**, mesmo com ganho na config (N6-2/N6-3: guarda e não age).
- **O ME usa o desarranjo dos lobos** (`lobos.desarranjo_n6`, tupla na ordem de `FRUTAS`); o `desarranjo_n6` da bancada (o dicionário do
  #165) confere que é o mesmo e falha alto se não for.
- **A bronca só no P3+ped**, identificado como o braço com pedido e fonte dono (N7-8); no P0+ped e no P1+ped o pedinte não repreende.
- **A chave do pedido só no motor dos braços com pedido.** Com ela o `estado()` do motor ganha `pedido` e `desobediencias`, o que mudaria o
  resumo das vidas antigas. Consequência: acoplar o registro de um braço com pedido a um braço sem pedido **sem tirar os pedidos** falha alto
  (`PedidoSemChave`); os acoplados do plano (`sem_ensino`, `sem_pedido`) tiram.
- **As broncas no orçamento.** São `repreender` no registro, iguais às do dono no tipo; a vida conta as broncas pela regra do mundo e as
  desconta da conta do dono (`VidaBancada.broncas`). No acoplado, as broncas da origem ficam só quando o filtro não tira `repreender`; o
  `sem_ensino` tira (com todos os sinais do dono, como o plano manda).
- **`sem_pedido` não tira as broncas.** Ele é o controle do P0+ped (o P0 no registro do P0+ped sem os pedidos), que não tem bronca e mantém os
  sinais do dono. `sem_ensino_sem_pedido` ficou como o `sem_ensino` (o nome do plano, seção 4.2).
- **O tick da decisão** nas medidas é k × `intervalo_decisao_ticks` (o motivo dos lobos não guarda o tick), como a medida da bola já fazia.
- **A ocupação dos espaços** é lida do `_memoria` do cérebro depois de cada decisão (atributo interno, só leitura). O estado interno no fim
  da vida não dá a ocupação ao longo do tempo, e chamar `estado_interno()` a cada decisão copiaria todos os motivos.
- **Os marcos 1 e 2** saem como verificação exata (a sequência de frutas dos episódios = a dos consumos); o tick do episódio é o do relógio
  do cérebro, e não é comparado aqui.
- **Janelas do N7 com vida curta:** inicial = dias 1 até a metade da fase de pedido, final = até `dias_pedido`, extinção = depois, todas
  cortadas no fim da vida (na fumaça de 4 dias, só a inicial tem decisões).
- **G-URG nas medidas:** o cérebro só grava a sonda do pedido nas regras `fome_moderada` e `fruta_no_cenario`, então as violações das regras
  urgentes saem 0 por construção. O gate de verdade do G-URG é o do CEREBRO-N6-N7 (sono, necessidade e abandono iguais com pedido vigente).
- **O `w_pedido` por dia** é refeito por replay até o fim de cada dia (como a deriva), só nos braços que aprendem; no P0+ped é constante.
- **Gabarito:** o comentário do `tests/gabarito_bancada_liga.py` dizia `w0_pedido` no ponto T3, mas o gabarito foi gravado só com `w0_info`
  S/2. Corrigido o comentário; os dados não mudaram.
- **Testes antigos:** `test_bancada_n6_n7.py` (os braços agora rodam; a trava do `NOS_PENDENTES` segue testada com uma entrada posta pelo
  teste) e `test_bancada_n5.py::test_filtros_da_informacao` (o `sem_ensino` tira também os pedidos).
- **Quatro testes do chat B mudaram** (`tests/test_cerebro_n6_n7.py`): eles punham a memória (`memoria_ligada`) e o `w0_pedido` direto na
  `cfg_lobos` da bancada, no P0 e no P1, porque os braços do N6 e do N7 ainda não rodavam. Com as chaves pertencendo ao braço, o teste do
  M0 = P0 usa o braço M0 (só o estado da memória e o rótulo do braço diferem), o da memória que age usa o MR, e o "sem o campo do pedido nada
  muda" passa a dizer que num braço sem pedido o `w0_pedido` da config não chega ao cérebro (e no P1+ped chega). A intenção de cada um ficou;
  a alternativa (deixar a config ligar a memória e o pedido em P0, P1 e P3) faria um braço mudar sem o nome dizer.
