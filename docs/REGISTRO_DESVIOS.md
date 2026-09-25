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
