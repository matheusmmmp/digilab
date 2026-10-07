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

## 2026-10-05 — K3/V2: plano da comparação A × B × C no papel; interpretações

Tarefa `docs/TAREFA_V2_PLANO_COMPARACAO_CEREBROS.md`; entrega `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`. Nenhuma run, nenhum código;
B e C ainda não existem.
- **O herdado é comum aos três** (decisão C-1): o instinto entra como prior em todos, e cada cérebro aprende por cima; desligado = instinto
  byte a byte. Sem isso, "aprende melhor" se mistura com "nasceu melhor", e o P0 deixa de ser um só.
- **A comparação é uma família própria**, com quatro contrastes bilaterais (B − A e C − A, P1, descasado e mutável); as predições do
  experimento maior ficam com o A e com a família delas.
- **Os blocos N6 e N7 ficam fora**: são mecanismos do A; exigi-los de B e C imporia a arquitetura do A.
- **As faixas do N11 (16101…17505) não são usadas**: a tarefa pede faixas novas fora da seção 6 do roadmap. O plano propõe 28101…28505 e
  29101…29505 e pede ao coordenador marcar as do N11 como substituídas. As faixas 23101…27505, propostas pela leitura parcial e superadas
  pela M11, também ficaram de fora, para não confundir.
- **CfC, NCP, FlyWire e NORNBRAIN** entram só como pista (CORPUS ou software não revisado): nenhum deles está na tabela verificada do
  projeto. As fontes do *Creatures* citadas são as VERIFICADA da tabela e descrevem só a família de origem do A.
- **Legibilidade** é medida pela fração decidida pelo aprendido; compreensão humana fica para a fase 2 (Anderson et al. 2019).

## 2026-10-05 — V2, K4-DONO-JULGA-FRUTA: o dono do P3 julga a fruta (`docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md`)

- **Orçamento: escolhi o julgamento no orçamento** (`ConfigJulgamentoFruta.no_orcamento = True`, o padrão), como a tarefa pede; a
  alternativa, fora do orçamento, fica atrás da opção. **Quanto tira da tarefa** (`artifacts_v2_k4/orcamento.json`; P3 atencioso, ponto
  T3, 14 dias, orçamento 224, sementes 101…505, só mecanismo): o feedback da tarefa cai de 151,4 para 124,0 (casado), de 150,8 para 119,4
  (descasado) e de 150,6 para 126,6 (mutável), cerca de um sexto a um quinto. O atencioso só dá feedback quando está atrasado no ritmo do
  orçamento, e o julgamento gasta esse ritmo antes.
- **O cuidado de necessidade também cai** (alimentar, limpar e brincar: 72,6 → 67,2, 73,2 → 65,0, 73,4 → 67,6), mas não por falta de vaga:
  numa conferência à parte, em nenhum passo o julgamento tomou a vaga de um cuidado desejado (o máximo do passo é 6) e nada foi descartado.
  O pet elogiado pela fruta boa come mais fruta (ex.: 39 → 70 consumos no descasado, semente 202) e fica menos com fome; o atencioso
  alimenta menos porque precisa menos. O G5 do experimento maior (saúde e privação contra o "só cuidado") é o que confere se isso pesa.
- **Recomendação para o Matheus:** fora do orçamento. Motivos: a informação do P2 já é fora do orçamento, então P2 × P3 compararia o
  canal com o mesmo gasto; e no orçamento a tarefa do P3 perde um sexto do feedback, o que mistura o K4 com menos ensino da tarefa no P3.
  Contra: fora do orçamento o P3 recebe mais sinal que antes. Fica como decisão.
- **Neutra = 0, ruim = efeito < 0:** a mesma divisão do P2 (`DonoInformante`: "mal" se o efeito é negativo). O P3 repreende exatamente o
  que o P2 diz que faz mal (teste); a diferença é que o P2 diz "bem" da neutra e o P3 não diz nada dela, como a tarefa pede.
- **O dono vê os consumos pelo `estado()`**, e só com a chave (`consumos_frutas`). Sem ela o `estado()` é o de hoje e o dono que julga
  falha alto (`KeyError`). O julgamento é do dono (o motor não sabe do julgamento).
- **O crédito é exato:** a decisão cai a cada 15 ticks e o dono age a cada 15, então a decisão anterior ao julgamento é sempre a de comer
  a fruta julgada (teste). Se outro feedback da tarefa sair no mesmo passo, ele credita a mesma decisão (a janela da v1).
- **O descarte:** se os julgamentos de um passo passarem do máximo do passo, os que sobram vão para `julgador.descartados` e não voltam.
  Na medida, nenhum.
- **Arquivos fora da lista da tarefa:** `config.py` e `protocol.py` (a chave e o registro de status e fonte, como o pedido do N7), e
  `experiments/medir_k4_orcamento.py`, com a medida do orçamento e a receita do P3 com julgamento pela bancada sem mudar `bancada_v2.py`.
- **Fora do orçamento na bancada** pede o chat D: o `simular_vida_mundo` só aceita da regra do mundo os eventos de `FORA_DO_ORCAMENTO`, e
  elogio e bronca não estão lá (nem devem estar para os outros braços).

## 2026-10-05 — CANAIS-REFORCO: o sinal da consequência por canal, com o mesmo total; interpretações

Tarefa `docs/TAREFA_V2_CANAIS_REFORCO.md` (etapa C4), H-R2 de `docs/research/digibrain/mechanisms/reinforcement.md`, decisão K-6 de
`docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`. Só testes de mecanismo; nenhuma run com faixa reservada.
- **"Mesmo total de sinal" = a soma inteira dos canais é o escalar da mesma decisão.** Arredondar cada canal sozinho
  (div_arred(g·Δ_i, S)) não fecha a soma; o arredondamento telescópico sobre as somas parciais fecha sempre, e cada canal fica a no máximo
  1 da conta isolada. A ordem dos canais é a dos drives (fome, higiene, energia, humor); o resto de arredondamento vai ao canal em que a
  soma parcial cruza o meio. O aprendiz confere a soma contra o escalar que a bancada calculou e falha alto se diferir.
- **"Cada um com o próprio peso de crédito" = cada canal credita o seu grupo de pesos**, não um multiplicador por canal: um multiplicador
  mudaria o total (é a sensibilidade da H-R4, que fica para depois, com o ponto de entrada nomeado e sem uso).
- **A rota é por grupo de pesos, uma por canal:** o corpo (fome, higiene, energia) → a tabela da regra; o humor → os pesos que leem a fruta
  (escolha, informação, pedido, presença). No escalar o mesmo f_S vai a todos esses grupos ao mesmo tempo; nos canais cada grupo recebe só a
  soma dos canais dele, e nenhum canal é creditado em dois grupos. A rota é constante do código: outra rota é desenho novo e, pela K-6,
  entraria por adendo 2 do plano da calibração, varrida com o ganho. **Nenhum parâmetro novo além da chave.**
- **A presença (FRUTA-NO-CENARIO) vai com a fruta, não com o corpo:** o peso de presença de uma fruta lê qual fruta está no cenário; o que
  separa uma fruta da outra é o efeito no humor (a nutrição é igual em todas, F6). Consequência: pelos canais, deixar de comer com fruta no
  cenário não mexe na presença (o humor não muda), e comer a fruta ruim sozinha baixa a presença dela mesmo quando a fome melhora.
- **A informação (N5) e o pedido (N7) vão com a fruta:** os dois leem a identidade da fruta. O pedido do N7 aprende também com o dono (P3),
  que continua escalar; os canais só mudam o que vem da consequência.
- **Decisão com total zero e canais não zero:** fome +k e energia −k, por exemplo, somam 0. O escalar não credita nada; pelos canais o
  corpo também recebe 0 (os dois são do corpo). Só quando os canais de grupos diferentes se cancelam um grupo recebe +k e o outro −k, com
  total 0: é o caso que a H-R2 quer separar, e fica dentro do contrato.
- **Canais e traço não andam juntos** (falha alto): o traço espalha o sinal às decisões anteriores com arredondamento próprio, e o total
  por decisão deixaria de ser o do escalar. O T3, o ponto da calibração conjunta, não tem traço (R1).
- **Só o sinal da consequência:** elogio, bronca, latência e chamado ignorado (o dono) seguem escalares.

## 2026-10-05 — Rodada 10: o K4 fora do orçamento; C-1 a C-10 aprovadas

- **O julgamento da fruta do dono do P3 fica fora do orçamento.** Era a recomendação do #170; o padrão do PR era dentro do orçamento.
  - A medida que embasou a decisão está em `artifacts_v2_k4/orcamento.json`.
  - Com isso, P2 e P3 diferem só no canal, com o mesmo gasto.
  - A bancada liga o K4 assim na rodada 10 (`docs/TAREFA_V2_BANCADA_K4_CANAIS.md`).
- **As decisões C-1 a C-10 de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md` foram aprovadas como recomendado.**
  - As faixas 28101…28505 e 29101…29505 ficam reservadas.
  - As faixas do N11 (16101…17505) ficam substituídas, sem uso.
- **Os cérebros B e C** vão para o chat D (depois da bancada) e para o chat A.
- **A K2** fica com o chat B: ele escreve o orquestrador agora e roda depois do PR do D.

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

## 2026-10-05 — V2, BANCADA-K4-CANAIS: o K4 fora do orçamento, os canais por braço e as ablações da K-7 (`docs/TAREFA_V2_BANCADA_K4_CANAIS.md`)

- **O K4 é uma chave da bancada** (`julgamento_fruta`, desligada por padrão), não um braço novo: com ela o P3 julga a fruta, e "o P3 sem o
  julgamento" segue sendo o P3 de hoje (gabarito). Vale para todo braço com fonte dono nos mundos das frutas, então também para o P3+ped
  (o dono que pede também sabe o efeito real); fora das frutas a chave não faz nada.
- **Ordem no passo:** o julgamento vem primeiro na regra do mundo (logo depois das ações do dono, com o estado do passo), antes das ofertas,
  da informação e do pedido, a mesma ordem do `simular_vida_frutas` do #170.
- **Contagem:** os julgamentos são `elogiar`/`repreender` no registro, iguais em tipo ao feedback do dono; a vida conta pela regra
  (`RegraFrutasComJulgador.feitos`) e desconta da conta do dono, como as broncas do pedido. No acoplado, os julgamentos (e as broncas) da
  origem ficam só se o filtro não tira nenhum dos dois sinais; um filtro que tirasse só um falha alto (hoje nenhum faz isso).
- **O motor dos braços com o K4 expõe os consumos** (`estado()["consumos_frutas"]`): o resumo dessas vidas difere do P3 de hoje por isso
  também, além dos julgamentos. O replay usa a mesma fábrica, então o G1 vale.
- **Os nomes das ablações** (`P1c`, `P1c-mem`, `P1c-can`) são escolha desta tarefa. O "P1 completo" segue a tabela da seção 1 do plano
  (memória com o ganho da config e canais ligados). O "sem memória" é a memória ligada com ganho 0 (o "g = 0" literal do plano: guarda e não
  age, como o M0), não a memória desligada; nas decisões é o mesmo.
- **Os canais fixos do braço vencem a config**: com `canais_ligados` na config, o `P1c-can` continua escalar. Os braços sem canal fixo (todos
  os de antes) seguem a config, como no #169.
- **Faixas da C-8:** 28101…28505 e 29101…29505 reservadas; as do N11 continuam na tabela, com a fonte marcando que foram substituídas, para
  nenhuma run usá-las por engano.
- **Ponto aberto para o coordenador:** a tabela da seção 1 do plano da calibração conjunta põe memória em P1, P2 e P3 e canais em P1 e P2 no
  bloco principal. Na bancada as chaves são do braço (desde a BANCADA-LIGA-N6-N7), e os P1, P2 e P3 de hoje não têm memória; os braços da
  K-7 cobrem só o P1. A K2 precisa de braços nomeados para o cérebro A montado (P1c já é o P1 completo) ou de uma decisão sobre isso.
- **Testes ajustados:** `tests/test_bancada_v2.py::test_engine_intocado_e_bracos_com_fonte_e_no` (a tabela dos braços inclui as ablações). `tests/test_experimento_maior.py` passa a esperar `K4_dono_julga_fruta = True` e confere, na fumaça, o
  orçamento do P3 e o só cuidado sem julgamentos.

## 2026-10-05 — V2, CEREBRO-C: o DigiBrain C, Fly-like (`docs/TAREFA_V2_CEREBRO_C.md`)

- **`config.py` também mudou** (a `ConfigCerebroC`): os parâmetros ficam em `config.py` pela regra do projeto. O registro de status fica no
  próprio `cerebro_c.py` (`PARAMETROS_CEREBRO_C`), como o do A fica no `lobos.py`.
- **A ligação na bancada ficou fora de `bancada_v2.py`:** `experiments/cerebro_c_bancada.py` estende a `Bancada` por subclasse só para os
  testes e como receita para o chat D. Não combinei por mensagem com o chat D (as mensagens entre sessões expiram); a receita vai no PR.
- **O que é "inspirado na Drosophila" aqui:** circuitos por classe de estímulo (corpo, social, objeto), células binárias esparsas
  (faixas e conjunções fixas, o papel das "Kenyon cells"), compartimentos apetitivo e aversivo separados, plasticidade de três fatores
  (célula ativa × ação executada × sinal do canal) e a expressão da memória apetitiva de comer pela fome. Nada disso diz algo da mosca
  (problema 4 de `brain_comparison.md`). O mundo não tem ameaça: o circuito de ameaça não existe (risco 1 do plano).
- **Os canais do C são a arquitetura**, sempre ligados; a `ConfigConsequencia.canais_ligados` (a chave do A) não muda o C. O total por
  decisão é o escalar da bancada, conferido em toda decisão (falha alto se não), então o contrato K-6 vale também no C.
- **As faixas de necessidade usam os limiares do instinto** (0,25 urgente; 0,5 o pedido do dono). Os cortes são estrutura (quantas
  células existem), não parâmetros livres; mudar a estrutura muda a capacidade e pede um PR.
- **O gate de fome só no apetitivo de comer:** a memória aversiva se expressa sempre (não comer uma fruta que fez mal não depende da fome).
  As outras ações não têm gate.
- **Capacidade:** conto toda sinapse de saída declarada, inclusive as de ações que nunca são candidatas daquela célula, como o A conta os
  756 pesos da tabela inteira. As células e o prior não contam (herdados).
- **A resposta inata à informação (`w0_info`) é parâmetro livre do C**, como o `w0_info` do A na K-3; com 0, a informação só pesa pelo
  que o C aprendeu nas células `info_bem`/`info_mal`.
- **Fora (decisão C-2):** a memória de episódios (N6) e o pedido (N7). A `BancadaComC` recusa os braços deles.

## 2026-10-05 — V2, BANCADA-MONTAGEM: a chave `montagem` da bancada (`docs/TAREFA_V2_BANCADA_MONTAGEM.md`)

- **A tabela vai pela fonte do braço**, não pelo nome: nenhuma (P0), consequência (P1), informação (P2, P2e, P2a) e dono (P3). Assim os
  braços dos blocos e as ablações recebem as peças da fonte deles sem uma linha própria; o que o braço fixa (a memória do N6 e das ablações,
  os canais das ablações) vence. É o que garante as ablações: o `P1c-mem` e o `P1c-can` diferem do P1 montado em exatamente uma peça (teste
  pelo `braco_montado` e pelas vidas).
- **`w0_pedido` "só onde há pedido":** fica nos braços com pedido (o motor deles é o único com a `ConfigPedido` e o pedinte). Os P1 a P3 do
  bloco principal não têm pedido no mundo, então o `w0_pedido` deles é 0. Nos +ped a montagem não muda o pedido (já era assim).
- **`w0_info` só nos P2:** na completa os outros braços zeram o `w0_info` da config, também os do N6 e o P0+ped. Na simples continua como
  antes (o `w0_info` da config em todo braço, o que punha o peso da informação no estado interno do P1 e do P3 sem informante).
- **A memória só nos mundos das frutas:** a bancada recusa memória fixa fora deles; a montada simplesmente não liga no padrão e na bola (o
  cérebro também não a teria). Os canais ficam ligados no P1 de todo mundo.
- **O P0 é o instinto pela vida (resumo do motor)**, não pelo estado interno: o P0 com lobos tem o estado interno dos lobos. O gate confere
  também que esse estado é o do P0 de uma config sem as peças.
- **As medidas do N6 seguem o braço montado:** na completa o bloco `n6` aparece no P1 a P3 dos mundos das frutas (antes só no N6 e nas
  ablações), lido das mesmas sondas.
- **O gabarito da simples** cobre três bancadas pela config (L1; T3 com `w0_info`, `memoria_ganho` e `w0_pedido` S/2; e o mesmo com os
  canais e o K4), o dono aleatório só na L1 para o teste caber na suíte; sem a chave confere as 120 primeiras vidas.
- **Teste de outra frente ajustado:** `tests/test_experimento_maior.py` passa a esperar `"montagem": "completa"` nos contratos do resumo.

## 2026-10-06 — V2, CEREBRO-B: o DigiBrain B, CfC + ator-crítico + elegibilidade (`docs/TAREFA_V2_CEREBRO_B.md`)

- **`config.py` também mudou** (a `ConfigCerebroB`), pela regra do projeto; o registro de status fica no `cerebro_b.py`
  (`PARAMETROS_CEREBRO_B`), como no A e no C.
- **A ligação na bancada ficou fora de `bancada_v2.py`:** `experiments/cerebro_b_bancada.py` (`BancadaComB`), a mesma receita do C.
- **O herdado entra multiplicando:** o peso do candidato é o do instinto vezes exp(z), isto é, log w = log w_instinto + z, como o plano
  descreve (seção 1.1). Não tirei o logaritmo do instinto: multiplicar por exp(0) = 1,0 devolve o mesmo float, o que fecha o byte a byte
  sem mexer na conta do instinto.
- **O que é "CfC" aqui:** a forma fechada h = σ(−F·dt)·G + (1 − σ(−F·dt))·K com F, G, K de uma camada (tanh) sobre (x, h anterior). Não é
  o CfC com a cabeça NCP nem o NORNBRAIN; é a família, no tamanho do contrato (9 ocultos). dt = 1 por decisão (as decisões são a cada 15
  ticks; o relógio não muda o dt).
- **O gradiente é truncado em um passo:** a célula é retropropagada só até o estado oculto anterior, que fica como dado. O que leva o
  crédito para trás no tempo é o traço de elegibilidade (λ). Retropropagar pela vida inteira custaria guardar todos os estados e mudaria o
  custo por decisão; fica registrado como escolha.
- **O traço é um só, para o ator inteiro** (célula e cabeças). Elogio, bronca, consequência e a E2 creditam pelo traço (a decisão mais
  recente com peso 1 e as anteriores decaídas por λ). O chamado credita a decisão do chamado pelo gradiente dela, porque quando a latência
  chega o traço já andou várias decisões.
- **O crítico é linear no estado oculto, sem desconto (γ = 0):** δ = r − V(h). Os sinais da bancada são imediatos (a consequência e o
  julgamento do dono são da própria decisão); a parte do futuro fica com o traço. É a forma mais simples que cabe nos 4 parâmetros livres.
- **Os logits aprendidos são cortados em ±20** (`limite_logit`, estrutura, contra estouro do exp); o gradiente não vê o corte.
- **A informação do N5 só na escolha da fruta**, como no A (N5-2): θ_info × info_f no logit da fruta, inato em `w0_info` (livre do adendo,
  em unidades de logit, não na escala S do A).
- **Capacidade:** conto todo parâmetro do ator (a célula inteira, as cabeças) e do crítico; o estado oculto, o traço e o prior não contam
  (contrato 1.3). 759 = 0,995 × 763.
- **Fora (decisão C-2):** a memória de episódios (N6) e o pedido (N7); o B tem a memória recorrente própria. A `BancadaComB` recusa os
  braços deles.

## 2026-10-06 — Adendos de calibração dos cérebros B e C registrados no plano da comparação

- Os adendos estavam só no corpo dos PRs #179 (B) e #176 (C). A seção 1.4 do plano pede um adendo ao documento, commitado antes de
  qualquer run. O coordenador os copiou sem mudar o conteúdo para o adendo 1 de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`.
- Conferidos contra a seção 1.4:
  - B: 4 parâmetros livres, 10 pontos de grade e ~660 vidas;
  - C: 3 parâmetros livres, 9 pontos e 480 a 540 vidas.
- Falta conferir o teto de vidas (as vidas da K2 do A) no artefato da K2, antes de calibrar B ou C.

## 2026-10-05 — K2-CALIBRACAO-CONJUNTA: interpretações do plano, registradas antes da run

Tarefa `docs/TAREFA_V2_K2_CALIBRACAO_CONJUNTA.md`; plano `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` (K-1 a K-11). Orquestrador
`experiments/run_v2_calibracao_conjunta.py`. **Escrito e commitado antes de qualquer vida das sementes 14101…14505.**
- **Pasta:** `artifacts_v2_calibracao_conjunta/{A1,A2,B,C,D}/`, como a tarefa pede (a seção 7 do plano dizia
  `artifacts_v2_experimento_maior/calibracao/`). As vidas (`vidas/`) ficam fora do git: são regeneráveis da config e do código.
- **IC das regras (A1, A2, C):** bootstrap percentil 95% (`metrics.bootstrap_ic`, reamostragens, semente e nível do `PROTOCOLO_ARENA_V1`)
  sobre as unidades com valor, unidade = vida (o mesmo das regras da revisão do aprendiz). Unidade sem denominador (nenhuma sub-decisão
  elegível, nenhum conflito) fica fora e é contada (`sem_valor`). "Limite inferior > limiar" é estrito.
- **Reserva das regras A1, A2 e C:** o ponto de maior limite inferior; empate, o menor valor; nenhum ponto com IC, o menor valor.
- **A2:** a deferência na `fome_moderada` nos dias 1…`dias_pedido` (as janelas "inicial" e "final" do bloco N7 somadas, isto é, o G-ARB do
  plano do N7 restrito à zona), por unidade = decididas pelo pedido / conflitos. O P0 sem pedido no `iguais_frutas` roda como referência
  descritiva (a 4ª vida por unidade da tabela 5.2) e não entra na regra.
- **B, a razão da deriva:** por condição, a média da deriva no fim do dia 14 sobre a média no fim do dia 7 (a conta de
  `run_revisao_aprendiz.celulas`); a razão do ganho é a média das três condições. "Vida no teto" = vida do P1 com algum peso em `|w − w0| =
  teto` (`pesos_no_teto() > 0`).
- **B, regra de reserva (o plano não a escreve):** se todo ganho tem vida no teto, o de menos vidas no teto, depois a menor razão, depois o
  menor ganho (a regra de reserva do N3, seção 6 do plano dele).
- **C, a sonda da informação:** `PoliticaLobos.escolha_sem_info` (nova, só lê: não muda peso, motivo, registro nem contagem; os gabaritos
  byte a byte das frentes do cérebro passam) refaz a escolha da fruta com o mesmo u e o termo da informação zerado. O orquestrador rejoga
  cada vida do P2 com um embrulho que a chama antes de cada `escolher_fruta` e confere que a vida e o estado interno saem iguais.
  **Elegíveis:** as sub-decisões com duas frutas ou mais e informação vigente em pelo menos uma fruta presente, nos dias 1–7 (a decisão
  k no tick k × 15). As duas frutas ou mais vêm da A1, para "a mesma régua" das duas entradas: com uma fruta só nenhuma entrada muda a escolha.
- **D, as ablações (K-7):** "P1 sem memória" = o braço P1 da bancada sem a chave da memória, com o resto do ponto; "P1 escalar" = o P1
  completo com `canais_ligados` False, numa config de bancada à parte. Os dois no `descasado` e no `mutavel`.
- **D, os Δ dos blocos:** Δ_N6 = metade da `taxa_fruta_ruim` final do `M0<MR` (plano do N6, seção 7); Δ_N7 = metade da fração de X na
  extinção do `P0<P3+ped:sem_ensino` (plano do N7, seção 7). A fração de X é calculada dos motivos de toda vida do bloco N7, com ou sem
  pedido (o P3 sem pedido não tem o bloco `n7` nas medidas da bancada e o G-MARCA-E precisa dele). O poder do G-EROSAO (deferência) é dado
  com o Δ_N7, que o plano do N7 define pela fração de X: é o único Δ do bloco.
- **D, o N e o poder:** N por contraste primário pela fórmula da seção 5.3 (α/6, poder 0,8, múltiplo de 5; `run_v2_experimento_maior.tamanhos`).
  A conferência por simulação reamostra as diferenças das 20 unidades **centradas no Δ** (a alternativa), N por réplica, teste t pareado
  unilateral a α/6, 2000 réplicas; fica no adendo ao lado do N da fórmula, que não é trocado por ela. A equivalência da predição 5 leva o N
  da mesma fórmula com α = 0,05 (IC 90%). Os secundários: poder pela aproximação normal com o N escolhido, α/3 nas famílias do N6 e do N7
  (o passo mais exigente de Holm de cada uma) e α = 0,05 nas ablações; abaixo de 0,5, subpotenciado.
- **D, o tempo da validação:** 44 vidas por unidade × N × os segundos por vida medidos na própria etapa D (vida, replay do disco e medidas,
  como a validação vai rodar). Acima de 12 h (K-10), a run para e o PR pergunta ao Matheus.
- **D, os contratos K1–K9 em vida real:** K1, o P0 de cada unidade e condição contra o instinto das frutas, byte a byte; K3, P2 e P2e com as
  mesmas (tick, fruta) e conteúdo oposto; K5 e K7, as mesmas ofertas em todo braço e acoplado da unidade e do mundo; K6, casado e descasado
  com efeitos opostos fruta a fruta por genoma; K8, um registro de consumo por consumo contado; K2 e K4 pela config e pelo orquestrador do
  experimento maior; K9 pela bancada (toda vida rejogada do disco).
- **Os braços "completos" (seção 1): pela montagem da bancada** (decisão do Matheus de 2026-10-05, opção 1,
  `docs/TAREFA_V2_BANCADA_MONTAGEM.md`). Os braços continuam P0 a P3, e toda config de bancada da K2 leva `"montagem": "completa"`, que
  liga em cada um as peças da tabela da seção 1 com os valores da config (o `g`, o `w0_info`, o `w0_pedido`). As ablações da K-7 são o
  `P1c-mem` e o `P1c-can` da bancada (o P1 completo menos uma peça). O orquestrador recusa a calibração enquanto a bancada não tiver a chave
  ou um braço P1–P3 não tiver a memória (`pecas_pendentes`). Os braços `P2c`, `P2ec`, `P2ac` e `P3c` que esta tarefa tinha acrescentado à
  bancada antes da decisão saíram do branch.
- **Uma run começou e foi interrompida antes do fim** (2026-10-05), com os braços próprios desta tarefa, antes da decisão da opção 1: por
  ordem do Matheus, a run da K2 passa a esperar o PR da BANCADA-MONTAGEM. A run parou durante as etapas A2 e B. **Nenhum resultado dela foi
  lido**: nem `resultado.json`, nem medidas, nem escolha. As vidas foram apagadas (a worktree da run foi removida). A run que vale é a única
  feita depois do merge da BANCADA-MONTAGEM, nas mesmas sementes de calibração. Por isso a regra "uma vez" se aplica a ela, e as sementes
  de validação não foram tocadas.
- **K4:** a chave `julgamento_fruta` da bancada fica ligada em toda config da K2 (age só nos braços com fonte dono nos mundos das frutas;
  no `iguais_frutas` não há fruta não neutra, então não há julgamento no bloco N7).
- **Blocos N6 e N7, na montagem completa:** o MR fixa a própria memória (com o aprendizado do lobo de decisão desligado, N6-2), e o M0, o
  MT e o ME são os acoplados dele. No bloco N7 a montagem liga a memória no P1+ped (com canais) e no P3+ped, como nos outros braços com a
  mesma fonte; o P0+ped fica sem nada. A referência do mundo padrão usa o P0, o P1 e o P3: sem frutas a montagem não liga a memória.

## 2026-10-06 — K2-CALIBRACAO-CONJUNTA: o que a run mostrou (depois da run)

- **A run única** foi feita no commit `5f288d6`, com a montagem completa do #178, e terminou sem erro (4 h 12 min). A suíte inteira rodou ao
  mesmo tempo, então os 12,3 s por vida da estimativa da validação são pessimistas.
- **A2 sem conflitos:** a deferência na `fome_moderada` ficou sem denominador nas 20 unidades e nos três pontos. Valeu a reserva registrada
  (o menor valor). Por que não houve conflito não foi investigado.
- **B na reserva:** todo ganho teve vida do P1 no teto (4: 2; 8: 10; 16: 33). A reserva registrada antes da run escolheu o 4.
- **A escala do Δ no p3:** a seção 5.3 do plano aplica o Δ da regra 6.3 (taxa) aos seis primários, mas o `p3_consumos` é medido em
  consumos. O N dele (191.815) é artefato de escala, não de variância. O orquestrador seguiu o plano como está. As alternativas
  (`alternativas_n.json`) foram calculadas depois, das mesmas 20 unidades, só como tamanho de amostra: nenhum parâmetro mudou por elas.
- **O N pequeno nos outros cinco:** no piso de 5 unidades a fórmula normal é otimista (poder simulado de 0,73 a 0,77 em três). A
  conferência por simulação está no adendo ao lado do N da fórmula, como o plano pede, sem trocar o N.
- **O poder dos secundários** no `adendo.json` usa o N de 191.815 e precisa ser refeito com o N que o Matheus decidir.

## 2026-10-06 — Rodada 11: opção A da K2 (N 30, Δ do P3 em consumos); a validação espera os adendos das predições

- **A opção A foi aprovada pelo Matheus** e está registrada como adendo 2 de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`.
  - Ela corrige a escala do Δ do P3, que estava em taxa e passa a consumos.
  - O N passa a vir da simulação de poder.
  - Números em `artifacts_v2_calibracao_conjunta/adendo_opcao_a.json`.
- **A ordem da rodada 11 mudou.** A run da validação única espera os adendos de `docs/PREDICOES_V2.md`, entre eles a medida em pelo
  menos três durações de vida. Esse documento depende de uma síntese de literatura que ainda não está no disco.
- **A calibração dos cérebros vai para quem os construiu:** a do B para o chat D e a do C para o chat A.
  - Sementes 28101…28505, K = 4.
  - Adendos já conferidos (adendo 1 do plano da comparação).
  - Teto de vidas conferido: o A gastou 1260 na K2, contadas nos logs de vida de `artifacts_v2_calibracao_conjunta/`.
## 2026-10-06 — Validação única do experimento maior (V1): interpretações, registradas antes da run

Tarefa `docs/TAREFA_V2_V1_VALIDACAO_UNICA.md`. Vale o adendo 2 do coordenador, que está no `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`
(#182; o que este branch tinha escrito com o mesmo conteúdo saiu na fusão com a main). Orquestrador: `experiments/run_v2_experimento_maior.py`, com a chave nova `"blocos": true`. Config:
`experiments/configs/v2_experimento_maior/validacao.json`, com 30 unidades derivadas das bases 15101…15505 (K = 6).
- **Os blocos** (seção 4 do plano da calibração conjunta) rodam em runs próprias da bancada, nas mesmas unidades:
  - o P2a nos três mundos;
  - as ablações `P1c-mem` e `P1c-can` no descasado e no mutável;
  - o bloco N6: o MR, e o M0, o MT e o ME acoplados a ele;
  - o bloco N7: P0, P0+ped, P1+ped, P3+ped e P3, mais o só cuidado do P3+ped.

  Com o bloco principal e a referência do padrão, são os 44 por unidade (teste). O bloco principal é o de antes, intocado.
- **O "só cuidado" acoplado** é o próprio braço no registro sem o ensino (`P2<P2:sem_ensino`), como a seção 5.1 deste plano e o
  orquestrador o leem. A tabela da seção 4 do plano da calibração escrevia `P0<P2:sem_ensino`, e o piloto da K2 rodou assim.
- **Cada contraste com o Δ na sua escala:** 0,1986 nas taxas e 17,5 consumos no p3. O p3 não se lê por equivalência, então o Δ dele só
  entra no tamanho de amostra.
- **Bloco N6:**
  - G-CAUSAL, G-REC e G-EMB são o acoplado menos o MR na `taxa_fruta_ruim` final, com Holm de três (α = 0,05) e equivalência pelo Δ_N6;
  - G-CITA é a média da fração decidida pela memória no MR, com IC 95% inferior > 0,069;
  - G5 é MR − P0 no descasado, em saúde e privação (o M0 em malha fechada é o P0 do principal);
  - G-M1 e G-M2 pelos marcos das medidas `n6`;
  - **G-M3 não é medido pela bancada** e fica registrado assim.
- **Bloco N7:**
  - G-EROSAO é a deferência total na janela "final" (dias 6–10), P0+ped − P1+ped;
  - G-MARCA e G-MARCA-E usam a fração de X na extinção, tirada dos motivos de toda vida do bloco, com Holm de três e equivalência do
    G-MARCA pelo Δ_N7;
  - G-ARB é a deferência total dos dias 1–10 do P0+ped, com IC inferior > 0;
  - G-URG conta as violações nos braços com pedido (tem de ser 0);
  - G5: P0+ped − P0 e P3+ped − o só cuidado dele.
- **Ablações:** a peça tirada menos o P1 completo, na taxa final no descasado e depois da troca no mutável. São descritivas, fora de
  qualquer Holm, com IC 95% e o p unilateral.
- **N5, descritivo:** P2a − P2 no descasado, nos consumos até a metade e na taxa no início e no final.
- **O N pelo poder simulado (adendo 2):** o `tamanhos` do orquestrador ganhou a simulação. Por contraste, ele dá o menor N (múltiplo de
  5, até 200) com poder simulado ≥ 0,8 em α/6, e o poder simulado no N da run. O N da validação passa a ser o maior N simulado; o da
  fórmula fica ao lado (`n_validacao_formula`).
  - A conta é a da K2: bootstrap das unidades centradas no Δ, teste t unilateral, 2000 réplicas, a mesma rng. A função passou da K2 para
    o orquestrador do experimento maior, e a K2 a chama de lá.
  - Das 20 unidades do piloto da K2, a simulação dá **N = 30**, com o p3 a 0,862 no N 30, os números do `adendo_opcao_a.json` (teste). A
    fórmula dava 25: três primários, que ela punha em 5, pedem 10 pela simulação.
  - Na validação, o `resumo.json` grava o poder simulado de cada primário no N 30, a partir das unidades da própria validação. É
    descritivo e não muda nenhuma leitura.
  - Sem a simulação, a K2 chama o `tamanhos` como antes: só a fórmula.
- **Uma run nas sementes de validação começou e foi parada** (2026-10-06, das 09:49 às 10:12, commit `1140fc9`). Ela foi lançada pela ordem
  "rode a validação" do Matheus, antes da tarefa V1, que manda esperar o sinal verde do coordenador por causa dos adendos do
  `docs/PREDICOES_V2.md`. Foi parada assim que a tarefa chegou.
  - O que ela gerou: só as vidas do bloco principal (720: 30 unidades × 24, os logs e os estados internos). Os blocos ainda não tinham
    rodado e as medidas ainda não tinham sido calculadas: nenhum `medidas.json`, `contrastes.json`, `resumo.json` ou `blocos.json` existia.
  - **Nada foi lido** (só a contagem de arquivos) e tudo foi apagado.
  - Uma primeira tentativa às 09:47 (20 arquivos) foi parada em segundos pelo mesmo motivo de execução e também apagada sem leitura.
  - Se as sementes 15101…15505 continuam valendo para a validação única é decisão do coordenador e do Matheus. Nenhum número delas foi
    visto, então nada pôde puxar uma escolha.

## 2026-10-06 — Decisão do Matheus: o cérebro B "não fecha", aceito sem recalibrar

- **O resultado.** A calibração do cérebro B (PR #184, `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`) fechou as quatro regras, mas o piloto
  dispara o critério "não aprende" da seção 7 de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`. A parte aprendida muda 0,0077
  [0,0065; 0,0089] das decisões, contra o limite de 0,01.
- **A decisão (2026-10-06): fica como está.**
  - O B sai da escolha do M6 com esse motivo registrado (C-7).
  - Ele não é recalibrado e a regra não muda. A regra de estabilidade (K-4) foi escrita antes dos dados e é a mesma do cérebro A.
    Trocá-la depois de ver o resultado seria ajustar a regra para o B passar.
- **Limitação declarada da comparação.** A regra de estabilidade empurrou a cadeia para o ponto em que o B menos aprende. A fração das
  decisões decidida pelo aprendido no P1 foi 0,203 com a taxa do ator em 0,1 e de 0,024 a 0,008 com 0,01
  (`artifacts_v2_comparacao_cerebros/calibracao_B/`). Um olhar do B num ponto em que ele aprende só pode entrar como **descritivo**, nunca
  na escolha.

## 2026-10-06 — Adendo 3 do experimento maior: a literatura antes da validação (P-1 a P-7)

- **De onde vem.** Saiu de uma revisão de literatura do Claude Science, salva em `docs/referencias/E_SINTESE_VALOR_APRENDIZADO.md`, lida
  em `docs/PREDICOES_V2.md`. O Matheus aprovou P-1 a P-7.
- **O que entra no desenho:**
  - o bloco de três durações, secundário;
  - o mutável como limitação declarada;
  - os braços P2d e P3i;
  - a passada de literatura antes da leitura.
- **Correção antes de qualquer código.** A primeira versão propunha só o P3i, como isolador do momento. Ele não isola, porque o P2 aprende
  pela consequência e o P3, pelo dono. Ficaram duas variantes:
  - o P2d isola o momento;
  - o P3i isola a interpretação.
- **O que não muda:** as predições 1 a 5, os primários, o Holm, o N e o Δ.
- **A validação** espera os braços novos e o bloco de durações.


## 2026-10-06 — V2, CALIBRACAO-CEREBRO-B: a calibração do cérebro B (`docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md`)

- **O B mudou antes da run** (`cerebro_b.py`, arquivo do próprio cérebro): o estado oculto e o traço passam a andar só quando a decisão é
  observada (`observar`/`observar_consequencia`). A sonda da deriva (`metrics.distribuicoes_de_acao`) sorteia várias decisões no mesmo
  estado de fim de dia; antes, cada uma movia a memória recorrente do B, e a distribuição medida dependia da ordem das sondas. Nas vidas
  é o mesmo (toda decisão é observada antes da próxima); no motor das frutas a escolha da fruta vem depois do `observar`, e o gradiente
  dela entra no traço já andado, como antes. Teste novo: a sonda não move a memória.
- **A deriva só no meio e no fim da vida** (dias 7 e 14 na calibração; `dias // 2` e `dias` na fumaça), não em todo dia: são os dias que a
  regra de estabilidade (a razão 14/7 da K2) e o piloto (o dia 14) leem. A conta da deriva é a da `Bancada.deriva`, com o prior de cada
  mundo guardado.
- **A regra de manipulação pela régua da K-3:** limite inferior do IC 95% > 0,069, sobre as escolhas com duas frutas ou mais e informação
  vigente (a sonda `fruta.sonda.info_decidiu` do B), a vida inteira e as três condições juntas por unidade (o adendo do B não tem a janela
  de dias 1–7 da etapa C do A). O "passa de 0,069" do adendo foi lido como o limite inferior, como na K-3.
- **O "logit no limite" de uma vida:** alguma decisão real (ou escolha de fruta) com um logit aprendido cortado em ±20 (`cortes_limite` do
  estado interno). Nenhuma vida chegou lá.
- **O piloto reaproveita** as 60 vidas do P1 no ponto escolhido (rodadas na B-C; o `w0_info` não age no P1); IC por unidade, as três
  condições juntas. O P2 no ponto escolhido sai como descritivo.
- **Empates** de razão: o menor valor da grade, como na K2. Uma razão sem deriva no dia 7 conta como infinita.
- **Resultado registrado sem reajuste:** o B não fecha pelo "não aprende"; a observação de que a regra de estabilidade empurra a cadeia ao
  ponto de menor aprendizado fica como descritivo, para o coordenador e o Matheus.

## 2026-10-06 — V2, CALIBRACAO-CEREBRO-C: a calibração do cérebro C (`docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md`, adendo 1.2)

- **O prefixo das unidades fica no orquestrador.** A bancada só aceita os prefixos dos planos dela (`PREFIXOS_UNIDADES`), e ela não muda
  nesta tarefa. Por isso `run_v2_calibracao_cerebro_c.unidades_comparacao` aplica a mesma regra E3 com `comparacao-cerebros`:
  `derivar_semente(prefixo, b, k)` e `prefixo + "-genoma"`. A função falha alto com colisão ou com um valor numa faixa reservada. O teste
  confere que as unidades não colidem com as da validação da comparação nem com as do experimento maior.
- **A ligação do C é a `BancadaComC`** (`experiments/cerebro_c_bancada.py`), com um laço próprio: o `bv.rodar` só monta os lobos.
  - Cada vida é gravada, rejogada do disco (`Bancada.conferir_replay`) e medida por `Bancada.medir`, cujo replay também confere.
  - O `*.politica.json` (o estado interno, enorme) não é gravado: o replay já compara o estado interno inteiro.
  - As vidas ficam fora do git, como na K2.
- **K-4, "nas três condições juntas":** li como a regra da K2 (plano da calibração conjunta, seção 3.3), ou seja, a razão da deriva de
  cada condição e a média das três. A razão com as 60 vidas numa conta só fica no resultado, só descritiva. Empate, o menor valor (no
  adendo isso não está escrito para o caso sem teto); foi o que decidiu a C-B (4S e 16S com as mesmas vidas).
- **K-3, como a medi:**
  - O "passa de 0,069" é o limite inferior do IC 95%, como na K-3 do plano da calibração conjunta (seção 3.4).
  - Contam as sub-decisões com duas frutas ou mais e informação vigente nos dias 1–7.
  - As três condições são as do adendo (a K2 usava só o descasado), juntas por unidade: decididas somadas sobre elegíveis somadas,
    bootstrap sobre as 20 sementes.
  - A reserva é a do texto do adendo ("o de maior fração"), não a da K2 ("o de maior limite inferior"). Ela não foi usada: os três
    pontos passaram.
- **A C-B reusa as vidas do 4S da C-A,** como o adendo conta ("120 novas"): é o mesmo ponto, e as vidas seriam as mesmas byte a byte.
- **O piloto do "não aprende" reusa as 60 vidas do P1 no ponto escolhido** (as da C-B no teto escolhido). O `w0_info` não age no P1, que
  não tem informante, então essas vidas são as do ponto final. A unidade é a semente, com as três condições juntas.
- **O ganho comum vem de `artifacts_v2_calibracao_conjunta/escolha.json` (4).** A montagem e a chave `canais_ligados` são do A; o C não
  as lê (no C os canais são a arquitetura).
- **O teto de vidas (1260) é contado antes de rodar:** 540 previstas e 540 gastas. Um `Contador` também falha alto se a run passar dele.
- **O passo escolhido é a ponta da grade (S/8).** A razão da deriva cai com o passo (3,00, 1,89, 1,61), e com 1,61 a deriva ainda cresce
  na segunda semana. A K-4 não pede razão máxima, então a escolha fica, e a grade não foi estendida.

## 2026-10-06 — V2, P2D-P3I, parte A: o julgamento da fruta como informação (`docs/TAREFA_V2_P2D_P3I.md`, seção 2)

- **Um modo do `JulgadorFruta`, não um informante novo.** O P2d e o P3i precisam do mesmo conhecimento e do mesmo momento do K4: o efeito
  real vigente (a troca do mutável incluída), avaliado no primeiro passo do dono depois do consumo. O julgador já faz isso. Por isso a
  saída virou um parâmetro (`saida="feedback"`, o padrão, ou `"informacao"`). O mesmo objeto serve aos dois braços: no P3i fica ao lado do
  dono (fonte `dono`); no P2d, sem o informante da oferta (fonte `informacao`).
- **O parâmetro fica no construtor, não na `ConfigJulgamentoFruta`.** Um campo novo na config pediria mexer no registro
  `protocol.PARAMETROS_JULGAMENTO_K4`, e a tarefa limita a mudança a `frutas.py` e `config.py`. Também não é um número a calibrar: é a
  escolha do braço. `config.py` não mudou.
- **A neutra também é informada, como "bem".** Confirmo a leitura da tarefa: o conteúdo segue o do `DonoInformante` do P2 ("mal" se o
  efeito vigente é negativo, senão "bem"). Então, no P3i, os consumos da fruta do meio ganham uma informação, e o K4 de hoje não daria
  sinal nenhum para eles. No P2d isso mantém o conteúdo do P2.
- **Só fora do orçamento.** A saída `"informacao"` exige `ConfigJulgamentoFruta(no_orcamento=False)`; o `DonoJulgaFruta` (o K4 no
  orçamento) recusa um julgador assim. No motor, a informação precisa do canal ligado (`ConfigInformacao`); sem ele, o primeiro
  `informar_*` falha alto (`InformacaoSemChave`).
- **Contagem no `simular_vida_frutas`:** as informações do julgador contam em `Vida.informacoes`, não em `julgamentos_fora`.
- **Nenhuma run.** Só as sementes dos testes (11, 22, 101, 202).

## 2026-10-06 — LITERATURA-P7: segunda passada nas pistas de prioridade 1; interpretações

Tarefa `docs/TAREFA_V2_LITERATURA_P7.md`; entrega `docs/referencias/E2_SINTESE_PISTAS_P7.md`. Nenhuma run, nenhum código, nenhuma mudança
no desenho (congelado até a validação).
- **As três pistas resolvem no Crossref**, sem correção nem retratação. O Liedtke e Fromhage 2019 foi lido em texto completo (acesso
  aberto, Europe PMC); o Dunlap, Austin e Figueiredo 2019 e o Eliassen et al. 2009 só pelo resumo (textos fechados).
- **O Liedtke e Fromhage não contraria a predição 2 como ela está escrita:** trata a evolução da velocidade de aprender, com custo na
  fecundidade, não o ganho de um aprendiz de taxa fixa dentro de uma vida. O que muda é a leitura: a forma da curva das durações pode ter
  um limiar, e um resultado em vida curta vale para a taxa da calibração.
- **Correção à síntese anterior:** a relação do Dunlap e Stephens 2014 no Crossref é uma recomendação do Faculty Opinions, não uma
  contestação; a carta que contesta é a de Dwyer 2015 (`10.1073/pnas.1420871112`), conferida só por título e metadados.
- **Ackley e Littman:** existência confirmada em duas listas de referências revisadas por pares (Kozielska e Weissing 2024; Nolfi e
  Floreano 1999), com o ano divergente (1992 e 1991); o texto não foi lido. A mudança de status na skill e no CSV fica para o Matheus
  (decisão L-2); nada foi editado na skill.

## 2026-10-06 — V2, V1-ADENDO3: o orquestrador da validação com o adendo 3 (`docs/TAREFA_V2_V1_ADENDO3.md`)

Tarefa `docs/TAREFA_V2_V1_ADENDO3.md`; adendo 3 do `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`. Só fumaça nas sementes dos testes; nada
rodou nas sementes 15101…15505. Interpretações, registradas antes da run:
- **O custo e a duração maior: 28 dias** (`experiments/custo_adendo3.py` → `artifacts_v2_v1_adendo3/custo.json`).
  - O tempo por vida de 14 dias é o da calibração conjunta, 12,27 s (o piloto de 880 vidas, a mesma composição de 44 por unidade).
  - A razão entre durações foi medida nas sementes dos testes (bases 101 e 202, P0 e P1, descasado e mutável, pela bancada inteira): 7
    dias custam 0,42 × os 14, 21 dias 1,71 × e 28 dias 2,57 ×. O custo cresce um pouco mais que a duração.
  - O P2d e o P3i contam como vidas de 14 dias (4 por unidade).
  - Total: 4,91 h sem o bloco de durações; 6,13 h com 28 dias e 5,78 h com 21. O 28 cabe no teto de 12 h e fica.
- **As vidas de outra duração têm as mesmas interações por dia** (16): orçamento 112 com 7 dias e 448 com 28. O adendo não diz; manter o
  dono igual por dia é o que deixa só a duração mudar.
- **A medida do bloco de durações é a da predição 2:** a `taxa_fruta_ruim` na janela `final` no descasado e `depois_da_troca` no mutável.
  As janelas acompanham a duração (a segunda metade da vida), e a troca do mutável também.
- **A forma da curva tem regra escrita antes da run, só descritiva** (`forma_da_curva`). Os dois passos pareados por unidade são a =
  y(14) − y(7) e b = y(D) − y(14), com o valor orientado (taxa menor = melhor; ganho P0 − P1 maior = melhor). As formas:
  - crescente: IC 95% de b acima de 0;
  - ótimo interior: a acima de 0 e b abaixo de 0;
  - decrescente: b abaixo de 0 sem a acima de 0;
  - platô: IC 90% de b dentro de ±Δ (o Δ 0,1986 do adendo 2);
  - indeterminado: o resto.

  Sai para o P0, o P1 e o ganho P0 − P1, por mundo.
- **O P2d e o P3i:** a validação pede `"p2d_p3i": true`, e o orquestrador falha alto antes de qualquer vida enquanto a bancada não tem os
  dois braços (`docs/TAREFA_V2_P2D_P3I.md`, chat D). Depois do merge desse PR, este branch se atualiza e os liga.
  - Os contrastes são P2 − P2d e P3 − P3i na taxa `final` (descasado e mutável) e nos consumos até a metade (descasado), com IC 95% e sem
    Holm.
  - O número e o multiconjunto das informações por braço vêm do registro do motor nas medidas da bancada.
- **Correção do #183: a referência do P0 nos blocos.** Os blocos rodam sem o P0 na mesma run da bancada, e lá os consumos até a metade
  saem sem referência. O descritivo do N5 (P2a − P2) teria saído sem nenhum valor.
  - Agora a conta é refeita das taxas por dia gravadas, com a referência do P0 da unidade no bloco principal (`consumos_com_referencia`).
  - Um teste confere que dá o mesmo número que a vida daria rodando com o P0. Nas vidas do principal, a conta tem de bater com o valor
    gravado, ou falha alto.
  - Vale para o P2a e para o P2d e o P3i.
- **O apoio teórico de cada predição e a limitação do mutável** vão na leitura do `resumo.json`, como texto fixo (`APOIO_TEORICO`,
  `LIMITACAO_MUTAVEL`); a regra de decisão não muda.

## 2026-10-06 — Faixa de validação trocada para 30101…30505; decisões L-1 a L-4

- **A run indevida.** Uma run foi disparada nas sementes de validação 15101…15505 antes de a tarefa chegar (das 09:47 às 10:12; PRs #183 e
  #189). Ela foi parada, apagada e nada foi lido.
- **A troca.** Decisão do Matheus: trocar a faixa para 30101…30505 (adendo 4 do experimento maior). A 15101…15505 fica queimada e
  reservada. A troca no código (`BASES_EXPERIMENTO_MAIOR`, a config da validação e os testes) é do chat B, junto com a ligação do P2d e do
  P3i.
- **L-1 a L-4** (`docs/referencias/E2_SINTESE_PISTAS_P7.md`) aprovadas como recomendado:
  - **L-1:** o texto completo do Eliassen fica pendente, para antes da leitura;
  - **L-2:** o status do Ackley e Littman atualizado no CSV de `docs/referencias/` e na skill de literatura;
  - **L-3 e L-4:** entram como leitura no adendo 4.

## 2026-10-06 — V2, P2D-P3I, parte D: os braços P2d e P3i na bancada (`docs/TAREFA_V2_P2D_P3I.md`)

- **O P2d julga sempre nos mundos das frutas**, sem depender da chave `julgamento_fruta`: o julgador com saída informação é o informante
  dele (o que o P2 tem pela oferta). O P3i segue a chave, como o P3 (com ela desligada o P3i é o P3, gate).
- **Um campo novo no braço** (`Braco.julgamento`, só no P3i) e um valor novo de `Braco.informacao` (`"depois"`, só no P2d), em vez de
  braços tratados pelo nome. Pedir `Bancada.informante` do P2d falha alto: o informante dele é o julgador.
- **Contagem:** as informações do P2d e do P3i são informações (contam em `informacoes`, saem no `sem_ensino`), não julgamentos: o
  `VidaBancada.julgamentos` só conta o julgamento como feedback. A `RegraFrutasComJulgador` só põe `elogiar`/`repreender` em
  `extras_fora_do_orcamento` quando a saída é o feedback; com a saída informação, os eventos já são `FORA_DO_ORCAMENTO`.
- **O multiconjunto por vida** fica em `frutas.multiconjunto_informacoes` das medidas, pela função nova `metrics.multiconjunto_informacoes`
  (sobre o registro `MotorFrutas.informacoes`). O orquestrador do adendo 3 (`run_v2_experimento_maior.multiconjunto_informacoes`) não foi
  tocado: lê o mesmo registro e dá o mesmo resultado (teste).
- **"P3 e P3i com os mesmos ticks de julgamento"**, lido como a mesma regra de tempo: as vidas do P3 e do P3i divergem depois do primeiro
  julgamento (o elogio e a bronca ensinam o P3; a informação não ensina o P3i, só entra na percepção), então os ticks da vida inteira não
  podem ser os mesmos. O gate confere que os dois julgam pelo mesmo conhecimento (o mesmo `JulgadorFruta`, só a saída muda) e, em cada
  vida, no primeiro passo do dono depois de cada consumo: o P3 os não neutros, o P3i todos.
- **"O P2d sem informante = o P1 completo" e "o P3i com o julgamento desligado = o P3"**: o log, as decisões e tudo o que é aprendido são
  iguais; na montagem completa o estado interno difere só no que o `w0_info` põe nele (o peso da informação, que não anda sem
  informação, a contagem dos parâmetros e a informação vigente, zero, no motivo da escolha da fruta). O gate compara o estado interno
  sem essas chaves, por sha256.
- **Testes lentos ao falhar:** na primeira rodada os dois gates acima compararam o texto inteiro do estado interno, falharam pelas chaves
  da informação, e o pytest levou 34 min montando o diff de ~60 mil caracteres. Agora a comparação é por sha256; o arquivo roda em ~2,5 min.
- **Teste de outra frente ajustado:** `tests/test_bancada_v2.py` (a tabela de contrato dos braços) ganhou o P2d e o P3i. O
  `tests/test_adendo3.py::test_p2d_p3i_falha_alto_...` passa a ser pulado (ele mesmo se pula quando os braços existem).

## 2026-10-06 — V2, V1-LIGAR: a faixa de validação nova e a leitura do adendo 4 (`docs/TAREFA_V2_V1_LIGAR.md`)

Tarefa `docs/TAREFA_V2_V1_LIGAR.md`; adendo 4 do `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`. Só fumaça nas sementes dos testes; nada rodou
na faixa nova nem na antiga.
- **A faixa nova (4.1):**
  - `BASES_EXPERIMENTO_MAIOR["validacao"]` é 30101…30505, na bancada, na config da validação e nos testes; a regra das unidades não muda.
  - A 30101…30505 entra em `FAIXAS_RESERVADAS`. A 15101…15505 continua lá, marcada como **QUEIMADA**, com a fonte (#183).
- **A faixa queimada é recusada em toda a bancada, mesmo com o campo `plano`** (`bancada_v2.FAIXAS_QUEIMADAS`, conferida no
  `validar_config`: bases, sementes e genomas). O adendo diz "não pode ser usada para nada"; antes, com um plano qualquer, a bancada
  aceitava a faixa. O orquestrador do experimento maior já a recusava, por ela não ser mais a faixa da validação.
- **A leitura do 4.2**, só texto e medidas descritivas; nenhum teste nem regra de decisão muda:
  - **L-3:** o limiar entra como forma possível na leitura do bloco de durações (`leitura_limiar` em `duracoes.json` e no resumo). A regra
    `forma_da_curva` do #189 fica igual.
  - **Predição 2:**
    - os componentes da mudança de cada condição (`componentes_da_mudanca`);
    - no mutável, valor e eficiência lidos separados (`mutavel_valor_e_eficiencia`). O valor é o p2_mutavel (P0 − P1). A eficiência é a
      taxa da fruta ruim do P1 depois da troca, com IC: a distância ao ótimo 0.
  - **L-4:** a trajetória do `w_info` do P2e no descasado (`w_info_p2e.json` e a predição 4 no resumo). São o peso no fim de cada dia, o
    dia em que cruza o zero, a fração de unidades que cruza e a fração com o peso no limite de baixo (w0 − teto, a leitura "limitada pelo
    teto" do plano do N5).
- **Como a trajetória é medida:** um replay só por vida (`serie_no_fim_de_cada_dia`), que lê o peso no fim de cada dia e corta o avanço que
  atravessa a meia-noite, como o `politica_no_tick`.
  - Um teste confere a série, dia a dia, contra o `politica_no_tick` (o replay até cada dia, o que a bancada usa para o `w_pedido`).
  - O orquestrador confere o último dia contra o peso da vida e falha alto se diferir.
  - Rejogar uma vez por dia custaria cerca de 7,5 vidas por vida do P2e: perto de 46 min a mais na validação (30 vidas × 7,5 × 12,27 s).
- **O P2d e o P3i:** o PR da bancada do chat D (`docs/TAREFA_V2_P2D_P3I.md`, parte D) ainda não existe. A validação continua pedindo
  `"p2d_p3i": true` e falha alto antes de qualquer vida até lá. Depois do merge dele, este branch se atualiza e confere na fumaça.

## 2026-10-06 — V2, VALIDACAO-UNICA: a run da validação única do experimento maior (registro antes da run)

Sinal verde do coordenador, autorizado pelo Matheus, depois do #191 e do #192 (main `2660170`). Plano
`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, adendos 1 a 4.
- **Fumaça antes da run:** a config da validação, trocando só as unidades (bases 101 e 202, K = 1), o bootstrap (200 reamostragens) e as
  réplicas do poder (100). Gerou e rejogou do disco 112 vidas, sem falhar, em 15 min:
  - frutas 48, padrão 6, blocos 34;
  - durações 16, P2d e P3i 8.

  As leituras da fumaça não são resultado e não foram usadas para nada.
- **A run:** uma vez, `experiments/configs/v2_experimento_maior/validacao.json` sem mudança (bases 30101…30505, K = 6, N = 30), saída em
  `artifacts_v2_validacao_unica/`, do commit deste registro. Nada se ajusta olhando o resultado.
- **A run (depois):** 2026-10-06, das 19:58 às 23:22 (3 h 24 min), do commit `f1c32ab`, 1680 vidas rejogadas do disco, sem erro. A
  estimativa de 6,2 h vinha do tempo por vida da K2, medido com a suíte rodando junto; aqui a máquina estava livre. Resultado em
  `docs/RESULTADO_V2_VALIDACAO_UNICA.md`. Nada foi ajustado olhando o resultado.
- **O que a leitura registra ao lado da regra do orquestrador:** a leitura de cada predição no `resumo.json` é a da seção 5 e não junta a
  separação do cuidado (5.1). O relatório põe as duas lado a lado.
  - Nas predições 3, 4 e 5 o braço com dono não difere do próprio só cuidado (a condição (a) falha), e o cuidado do acoplado é pior (a (b)
    falha).
  - Pela seção 5.1, o efeito da predição 3 não conta como ensino.
- **Os descritivos não mudam nada:** o poder simulado no N da run e o N que a simulação daria nestes dados (35) ficam como descrição. O N
  da run é o do adendo 2.
- **As vidas** (3 GB) ficam fora do git (`.gitignore`); os resultados, as medidas e os metas (~15 MB) entram.

## 2026-10-06 — Validação única: o controle "só cuidado" fica como limitação declarada

- **O problema.** Na validação única (PR #193, `docs/RESULTADO_V2_VALIDACAO_UNICA.md`), a separação do cuidado (seção 5.1 do plano) falha
  nos braços com dono:
  - **condição (a):** P2, P2e e P3 não diferem do próprio só cuidado;
  - **condição (b):** o só cuidado acoplado cuida pior que o original, porque rejoga o cuidado em malha aberta, sem reagir ao pet.
- **Decisão do Matheus (2026-10-06): o resultado fica como está, com a limitação declarada.**
  - As predições 3 e 5 confirmam pelo contraste. Pelo critério registrado, não contam como ensino.
  - O controle acoplado em malha aberta pode não ser o controle certo nesta montagem.
  - Nada é refeito nestas sementes. Um controle melhor do cuidado (em malha fechada, ou pareado de outro jeito) fica para uma pergunta
    nova, com plano próprio.
- **Pendente antes da leitura final:** o texto completo do Eliassen et al. 2009 (L-1).

## 2026-10-07 — Comparação A × C (COMPARACAO-A-C, rodada 13): interpretações, o piloto, o adendo 2 e a validação

Tarefa `docs/TAREFA_V2_COMPARACAO_A_C.md`; plano `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, adendo 2. Resultado em
`docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`.

- **O B fora da família:**
  - família de dois (CC-1, CC-2), Holm bilateral, α = 0,05; CB-1 e CB-2 não testáveis;
  - o N com α/2 (o passo mais exigente);
  - o p bilateral do bootstrap: 2 × a menor cauda das médias reamostradas.
- **A margem antes do teste.**
  - A primeira versão do orquestrador lia "C melhor/A melhor" pelo Holm antes de olhar o IC 90%.
  - A seção 4 e o passo 1 do M6 dizem que dentro de ±Δ é empate. A leitura foi corrigida no piloto, refeita pelo `--reanalisar` sobre as
    medidas gravadas, antes do adendo 2.
  - Nada mudou nas vidas.
- **O reaproveitamento das vidas do C:** elas ficaram fora do git, numa worktree já apagada.
  - O piloto as refez e conferiu contra `calibracao_C/piloto.json`: médias e ICs idênticos.
  - A primeira conferência deu diferente só nos ICs, porque as unidades estavam em outra ordem no bootstrap. Com a ordem da calibração
    (por semente), sai igual.
- **O mundo do C é o do A, incluído o K4** (o dono do P3 julga a fruta).
  - O C não lê a montagem nem a chave dos canais.
  - No P1 a vida do C é a da calibração dele (teste).
- **Legibilidade:**
  - a mesma regra nos dois, a sonda do aprendido (contrato 1.1);
  - "com motivo honesto" fica como o próprio teste da sonda, porque o C não tem a expressão do fator;
  - o G4 com fator do A sai só descritivo.
- **Custo:** o tempo de `Bancada.vida` por decisão (sem o replay e as medidas) e os bytes de log por dia, média por unidade das vidas
  fechadas. A validação rodou com a máquina livre: a suíte só rodou depois.
- **O N do adendo:** o maior entre a fórmula e o N simulado, ao múltiplo de 5. Deu N = 5 (K = 1): o piso, porque σ_d ≈ 0,035 contra
  Δ = 0,199. O que isso implica (o M6 decide no passo 2, ICs largos nos secundários) foi registrado no adendo 2.5, antes da validação.
- **Validação:** uma vez (`validacao_ac.json`, do commit `dcda45f`), 235 vidas, sem erro, 22 min. Nada se ajustou olhando o resultado.
- **Fora da regra, para o Matheus:**
  - no P3 o C generaliza a bronca do dono para toda fruta e come pouca fruta;
  - o A aprende qual evitar.
  - A seção 4 põe o P3 nos secundários, então isso não muda a recomendação do M6 (o C); fica no relatório como a "alternativa
    registrada" da seção 5.

## 2026-10-06 — LEITURA-VALIDACAO: a leitura da validação única; interpretações

Tarefa `docs/TAREFA_V2_LEITURA_VALIDACAO.md`; entrega `docs/LEITURA_V2_VALIDACAO_UNICA.md`. Nenhuma run, nenhum código, nenhuma estatística
nova (os números são os de `artifacts_v2_validacao_unica/`, conferidos no commit `4dd962d`).
- **As regras das predições 1 e 2 se sobrepõem.** O contraste é positivo pelo teste (o "confirma") e o IC 90% fica inteiro dentro de ±Δ
  (um dos "refuta" registrados). O plano não diz qual vale quando os dois acontecem; o orquestrador gravou "confirma". A leitura propõe
  "confirma na direção, abaixo da margem de relevância" e deixa o rótulo para o Matheus (V-1). Nada foi recalculado.
- **Os braços que aprendem terminam perto de 1/3 da fruta ruim em todo mundo** (P1, P2, P2e e o só cuidado do P2; `frutas/tabelas.json`),
  o que seria comer as três frutas por igual. Isso é compatível com o aprendiz apagar a preferência inata; não foi testado. Fica como
  pergunta (Q-1, V-3), não como conclusão.
- **L-1:** o Eliassen et al. 2009 não tem acesso aberto (Unpaywall, Semantic Scholar, OpenAlex, o repositório NVA da Noruega sem arquivo, e
  o PDF do editor com 403). Fica só pelo resumo.
- **A worktree desta tarefa só tem `docs/`** (checkout parcial, configurado só nela): o disco D: estava cheio (cerca de 200 MB livres) e o
  checkout completo falhou. O branch e o PR não mudam por isso; os números foram lidos pelo `git show` dos artefatos versionados.

## 2026-10-07 — Leitura da validação (V-1 a V-6) aprovada; escolha do cérebro da web (M6) adiada para depois do descritivo do platô

- **V-1 a V-6** de `docs/LEITURA_V2_VALIDACAO_UNICA.md` foram aprovadas como recomendado:
  - **V-1:** as predições 1 e 2 são "confirma na direção, abaixo da margem de relevância";
  - **V-2:** o controle de cuidado em malha fechada vira pergunta nova;
  - **V-3:** o descritivo do platô de 1/3 (Q-1);
  - **V-4:** Q-1 primeiro, depois Q-3 e o controle;
  - **V-5:** o L-1 fecha como "sem acesso aberto; só resumo";
  - **V-6:** a leitura consolidada leva só o que os dados sustentam.
- **A comparação A × C** (`docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`, PR #197) recomenda o C pela ordem do M6. O desempenho empata, e a
  legibilidade é do C. Mas no P3, o braço do produto, o C generaliza a bronca e o A aprende qual fruta evitar.
- **Decisão do Matheus (2026-10-07):** o M6 só fecha depois do descritivo do platô (`docs/TAREFA_V2_DESCRITIVO_PLATO.md`). Se os dois
  cérebros só apagam a preferência inata, a vantagem do C em legibilidade pesa menos que a fraqueza dele no P3.

## 2026-10-07 — Descritivo do platô de ~1/3 (DESCRITIVO-PLATO, rodada 14): interpretações

Tarefa `docs/TAREFA_V2_DESCRITIVO_PLATO.md` (V-3, Q-1). **Pós hoc descritivo:** nenhuma leitura registrada muda. Relatório:
`docs/DESCRITIVO_V2_PLATO.md`.

- **"Regeneradas por replay":** cada vida foi refeita pela bancada a partir da espec (config, unidade, braço, condição), que é
  determinística. Depois foi rejogada do próprio log, bit a bit (G1), e conferida contra o `medidas.json` gravado: interações, consumos,
  contagem das frutas e a taxa da fruta ruim em toda janela. As vidas gravadas não estavam no git.
- **Os bracos:**
  - P0, P1, P2 e P3, como pede a tarefa, mais o P2e, que custa pouco e mostra a informação errada;
  - os só cuidado ficaram de fora.
- **A classe da fruta é pelo efeito vigente no tick:** no mutável muda na troca, e a classe dos pesos no fim é a do último tick. A regra
  foi conferida contra o efeito aplicado em cada consumo.
- **"Comer com uma fruta só"** é p(comer) bruto em toda decisão com uma fruta no cenário, sem controle de fome nem de regra.
- **"Herdado" na escolha:** a probabilidade da ruim pelo incentivo do genoma (o sorteio do instinto), calculada com os incentivos que o
  motor grava em cada oferta.
- **Pesos do C:**
  - para comer, a soma das células do objeto daquela fruta (presença e fome × presença), na ação comer;
  - para a escolha, a célula de identidade.
- **O que pode virar plano** (não aberto): a decisão de comer com uma fruta só aprende pouco o efeito da fruta.

## 2026-10-07 — M6: o cérebro A é o DigiBrain da web (fora da ordem registrada, por evidência descritiva posterior)

- **O que a regra registrada dava.** Pela ordem do M6 (`docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, seção 5) e pelo resultado da
  comparação (`docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`, #197), o escolhido seria o **C**. O desempenho no P1 empatou, e a legibilidade
  deu C 0,327 contra A 0,262.
- **A decisão do Matheus (2026-10-07): o cérebro A.** O motivo é o descritivo pós hoc do platô (`docs/DESCRITIVO_V2_PLATO.md`, #199):
  - com duas frutas ou mais, o A aprende qual fruta evitar: escolhe a ruim de 2% a 11% das vezes, contra 29% a 65% do herdado;
  - o A resiste à informação errada: no P2e escolhe a ruim de 2% a 4% das vezes, e o C de 77% a 83%;
  - o C fica perto do herdado no comportamento;
  - no P3, o braço do dono e do produto, o C quase não come e o A aprende a evitar a ruim.
- **Por que é declarado assim.** O empate no passo 1 escondia uma diferença que a medida primária (a taxa final, com o platô de 1/3) não
  via. Decidir assim desvia da regra. A evidência é pós hoc e de poucas unidades no C (5), e fica declarada desse jeito:
  **"pela regra seria o C; escolhido o A por evidência descritiva posterior"**.
- **Limite conhecido do A:** a decisão de comer não aprende o efeito de uma fruta quando ela está sozinha. É a origem do platô e fica como
  pergunta para um plano próprio (Q-8).
- **Próximo:** o plano do porte para a web, pets v11 (`docs/TAREFA_V2_W_PLANO_PORTE.md`, chat A).

## 2026-10-07 — W-TAREFA-MUNDO (rodada 16, worker C): a tarefa e o plano do mundo físico mínimo

Só papel: `docs/TAREFA_V2_MUNDO_FISICO.md` e `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`. Nenhuma run, nenhum código.

- **"Todo sorteio do mundo vem da rng de ambiente".** Lido como o lado do ambiente, em fluxos próprios por `derivar_semente`
  (`mundo-arvores`, `mundo-bola`, `mundo-sujeira`), e **não** o `_rng_ambiente` do `engine.py`. Sortear no do engine faria o comportamento
  do cérebro mudar o clima, e os braços deixariam de ser comparáveis. Fica como a decisão MF-4 da tarefa, com essa recomendação.
- **Coisas que a tarefa acrescenta ao pedido** (cada uma justificada no texto):
  - o evento `deixar_bola(x, y)`, ao lado do `deixar_comida`, pela seção 2.3 do `mundo_fisico.md`;
  - desfazer o `+0,05` do comer sem comida (MF-2). Sem isso, comer parado cobre 4 vezes a fome perdida numa decisão, e nenhuma busca
    compensa;
  - o "achou e comeu" no explorar (MF-1), para a consequência imediata poder ligar explorar à comida;
  - o gancho `consequencia_mundo`, para qualquer cérebro ver o estado depois de andar e comer;
  - o braço de controle P0z (`sem_explorar`), para conferir a premissa "explorar compensa" antes de ler o P1.
- **A calibração do plano é só do mundo, e não do cérebro.** O M10 (sem calibração por nó) vale: o P1 roda no ponto da validação única. A
  calibração escolhe só o multiplicador das quedas das árvores, e só com o P0 e o P0z. O piloto do P1 serve só para o N.
- **M-4 e M-5.** O prompt da rodada (`docs/V2_RODADA_16.md`, 3.2) pedia as duas no fim, com recomendação, mas elas já foram decididas em
  2026-10-07 (seção 4 do mesmo documento). Os dois documentos as tratam como decididas e não as reabrem.
- **Charnov 1976** (`10.1016/0040-5809(76)90040-x`). Os metadados foram conferidos no Crossref em 2026-10-07: título, autor, revista
  Theoretical Population Biology 9(2), páginas 129–136 e data de abril de 1976. O resumo não foi lido, e a referência **não** foi posta
  nas tabelas de `docs/referencias/`. Entra como PISTA e só num descritivo sem gate.
- **Donos de arquivo.** Os três que o prompt deu valem: mundo com o A, bancada com o D, web com o A. Dois foram acrescentados:
  - o instinto do mundo (`PoliticaInstintoMundo`, a fome urgente) fica com o B, como cérebro;
  - o campo novo da `Observacao` fica com o A, como parte do mundo.
- **Os números do mundo** (mapa, raios, velocidade, custos, prazos) são PROPOSTOS, sem fonte. O layout segue as proporções do protótipo
  `mundo_fisico_vistas.html`.

## 2026-10-07 — Prancha do mapa do mundo físico (W-PRANCHA-MAPA, rodada 16): interpretações

Proposta em `docs/futuro/mundo_fisico.md`, 2.3 e 2.6. As pranchas estão em `docs/estilo_up/pranchas/` (placeholders) e em
`Assets/Pranchas_UP/` (sprites, fora do repositório). Só prancha.

- **Onde o mapa fica na navegação:** desenhei com o destino **Pet** ativo e o título "Mapa", marcado como "proposta". O mapa pode
  substituir o palco do Pet ou virar um destino próprio. É decisão do Matheus, e a prancha não a toma.
- **"Tela inteira" no celular:** o mapa ocupa a tela toda, por trás do cartão do pet e da bandeja, e a barra de navegação fica. Desenhei
  como página, não como tela cheia (a luta é tela cheia).
- **Gestos que não se confundem:**
  - arrastar que começa num item da bandeja solta comida ou bola;
  - um dedo no mapa move a câmera, que deixa de seguir o pet, e o botão do alvo volta a segui-lo;
  - dois dedos aproximam e afastam.
  - O cartão da bandeja diz isso em três linhas.
- **"Comida solta aqui":**
  - o ponto no chão com dois anéis amarelos (a cor de destaque, uma por tela) e a plaquinha;
  - o aviso "Carne solta no campo", com **Desfazer**;
  - o caminho tracejado que o pet vai fazer.
  - O Desfazer é proposta: a comida solta vira um evento `deixar_comida(tipo, x, y)` no registro, e desfazer pediria um evento de retirar
    ou uma janela antes de gravar. Fica para a tarefa do motor.
- **Arte:** chão, árvores, ninho, comedouro, frutas, carne e bola são desenho vetorial de placeholder, no traço do protótipo. O guia pede
  pixel art. Fica registrado como asset pendente em `docs/PENDENCIAS_PRANCHAS.md`.
- **Na cópia com sprites,** o pet é o sprite do jogo em 2× (escala inteira), sem encolher com a profundidade. A vista pede escala pela
  profundidade, e sprite só aceita inteiro; a regra de escala do pet no mapa fica para a tarefa da web.
- **O gerador** das duas pranchas (projeção do protótipo, saída em SVG estático) ficou fora do repositório: as pranchas são o artefato,
  como as do canvas.

## 2026-10-07 — Tarefa do corpo e dos drives (W-TAREFA-CORPO, rodada 16): interpretações

Só papel: `docs/TAREFA_V2_CORPO_DRIVES.md`. Nenhum código, nenhuma run.

- **A solidão entra.** O pedido diz "e da solidão, se a seção 5 pedir". A seção 5 do #203 pede drives que recompensem brincar, explorar
  **e o contato** e nomeia a solidão. O estresse entra junto, porque o pedido diz que acariciar reduz o estresse.
- **"Um órgão por vez" (E-9):**
  - a química dos drives de hoje entra sem órgão: são produções por tick e estímulos;
  - os dois órgãos da E-10 são a digestão e a Vida, cada um com sub-chave e PR próprios;
  - os drives novos são químicos sem órgão.
  - Força vital, dano e cura dos órgãos ficam para a 1b, como no `ego_existencia.md`.
- **O G-HOJE não pode ser byte a byte em malha fechada.** Os limiares de hoje caem sobre a grade inteira (a fome chega a 0,25 exato no
  tick 660), enquanto o float de hoje passa um pouco abaixo (0,24999999999998737; conferido no Python). Uma decisão vira e a vida segue
  outra. Por isso o gate tem duas partes:
  - em malha aberta, por tick, com números desta tarefa;
  - em malha fechada, pela distribuição, com a margem do plano.

  É o "dentro da tolerância do plano" do pedido.
- **C = 450000** é o mínimo múltiplo comum dos denominadores das taxas de hoje. Com ele, todo número de hoje vira inteiro exato, e a
  paridade com o TS é exata. É a decisão CD-1.
- **O carinho chega ao cérebro só pelos receptores.**
  - O crédito à última decisão (a janela da v1) é a leitura de "o reforço sai do mesmo ciclo da consequência" (#203, seção 4).
  - Restringir o crédito ao carinho, sem o cuidado do dono, segue o N3 e fica como decisão CD-4.
- **Revisão do Matheus (2026-10-07, no PR #209): o tapa também manda sinal direto ao cérebro.** A primeira versão seguia a S-2 e o #203,
  seção 4 ("não uma nota direta ao cérebro"); a revisão muda isso.
  - O tapa passa por `receber_acao_dono` e é creditado como a bronca, com `ConfigLobos.recompensa_tapa`.
  - Ele chega em toda fonte que aprende, para que o pet do produto, que aprende pela consequência, também o receba.
  - Ele continua sendo estímulo no corpo.
  - Não soma a mudança no corpo como segundo sinal (CD-9). O valor e o alcance do sinal são a CD-10.
  - O registro da decisão (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, seções 4 e 8) não foi editado aqui: fica para o coordenador.
- **O medo da mão** é um receptor do susto sobre a taxa do carinho: o conceito do manual de "um receptor controla a taxa de uma reação".
  O pedido o põe como efeito medido; a medida está na seção 8 e o mecanismo mínimo é a decisão CD-5.
- **O vínculo** depende da S-4 (tarefa própria). Até ela entrar, a medida sai "não disponível".
- **O instinto não lê os drives novos** (CD-2): o P0 fica o de hoje, e o que muda o comportamento é o aprendizado pelo corpo.
- **Os números dos drives novos** (taxas, estímulos, meias-vidas, pesos do sinal) são PROPOSTOS, sem fonte. O plano os calibra. Do manual
  do Creatures 3 só vêm os conceitos.
- **Donos de arquivo:** pelo pedido, o cérebro e o corpo ficam com o B (`digilab/corpo.py`, `lobos.py`), o motor com o A (`MotorCorpo`, o
  evento do tapa, o campo da `Observacao`, o TS da web) e a bancada com o D.

## 2026-10-07 — W-PLANO-CORPO (worker C): o plano de análise do corpo e dos drives novos

Só papel: `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`. Nenhuma run, nenhum código.

- **O `recompensa_tapa` não se calibra.** O pedido incluía o `recompensa_tapa` (CD-10) na calibração. A CD-10, já decidida, fixa o valor no
  da bronca, para o tapa continuar comparável com a bronca da pesquisa. O plano o deixa fixo e só o mede em ½× e 2× como sensibilidade
  descritiva. Mudar o valor fica como decisão (PCD-6).
- **A calibração conjunta roda só o P0-c.** A M10 pede uma calibração conjunta, não por nó, e a regra não pode olhar o primário. A grade
  (multiplicadores das subidas e das reduções, e o peso dos drives novos no sinal) roda só no instinto com o corpo, que não aprende e decide
  igual ao P0 com a química (CD-2, CD-7). O peso do sinal sai de uma sonda sobre essas vidas. As faixas da regra são PROPOSTAS, SEM FONTE.
- **O acoplado.** O achado da validação única (o acoplado em malha aberta cuidou pior) é tratado assim:
  - nenhum acoplado é comparado com malha fechada;
  - os dois lados do contraste do cuidado fixo são acoplados à mesma fonte (o P0-q da célula);
  - o cuidado preservado só se lê em malha fechada.
- **A distribuição do tempo livre no G-HOJE (b).** A tarefa pede "a distribuição das ações no tempo livre". O gate usa a fração em brincar e
  explorar, que tem a margem do efeito principal. As quatro ações saem uma a uma como descritivo.
- **Donos.** O bloco G-HOJE usa os donos de sempre, para comparar com a vida de hoje. Os blocos do corpo e do tapa usam o `DonoComGestos`:
  - o contraste primário roda no modo sem tapa nos dois lados, porque o tapa exige os drives novos;
  - o P3 fica fora desses blocos, porque o pet do produto não tem botões.
- **A curiosidade.** Ela exige o `MotorMundo` (CD-8). Um braço com ela só entra por adendo antes da calibração, se o mundo físico estiver na
  `main`; senão, vira plano próprio.
- **As faixas 33101…33505 e 34101…34505** foram conferidas fora de `FAIXAS_RESERVADAS` e sem uso no repositório nem nos branches remotos.
  Notei que a 31101…32505 (mundo físico) ainda não está registrada em `FAIXAS_RESERVADAS`: é a etapa 4 da tarefa do mundo, do chat D.

## 2026-10-07 — W-ADENDO-PMF2 (rodada 17, worker C): o adendo 1 do plano do mundo físico

Só papel: o adendo 1 de `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`. Nenhuma run, nenhum código.

- **A PMF-2 decidida no #212 (P0 − P1ac) é revista por adendo, antes de qualquer run.** O motivo é o achado da validação única: o acoplado
  em malha aberta cuidou pior que o original. O primário proposto é P0 − P1 em malha fechada. A PMF-2 de antes vale até o Matheus decidir a
  PMF-2r.
- **A fonte dos acoplados é o P0z,** e não um dos dois lados. O P0 no próprio registro é ele mesmo byte a byte e não teria a desvantagem da
  malha aberta. O P0z já roda em toda célula. Declarado: o cuidado dele foi gerado para um pet que não explora.
- **Vidas por unidade:** 60, contra 48 (+25%). O P1ac sai; entram o P0^ac e o P1^ac.
- **As referências da revisão P2:**
  - Church (1964), `10.1037/h0042733`: só metadados;
  - Kimmel e Terrant (1968), `10.3758/BF03209860`: só a página 1 de 4.

  Nenhuma está nas tabelas de `docs/referencias/*.csv`; as duas são citadas no nível que a revisão leu. O tamanho do viés e o custo em vidas
  do acoplado recíproco ficam SEM FONTE.
- **DS-5 no mesmo adendo (A1.8):** as medidas 1 e 3 de forrageio e a previsão da distância entram no Holm; a medida 2 entra só como
  descritiva. O A não estima a taxa média, então a medida 3 é lida pelo comportamento: a permanência contra a taxa recente do ambiente.
  O layout afastado custa 24 vidas por unidade e é o primeiro bloco a sair se o custo passar do teto. Ele depende de um segundo layout na
  `ConfigMundo` (chat A).

## 2026-10-07 — W-ADENDO-DS6 (worker C): o adendo 1 do plano do corpo

Só papel: o adendo 1 de `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md` (DS-6 e DS-4, decididas pelo Matheus em 2026-10-07). Nenhuma run, nenhum código.

- **A generalização do tapa** entra como bloco descritivo novo, fora do Holm: o P1-c com tapa numa fruta X sorteada (rng `tapa-fruta`), no
  `iguais_frutas`, contra o P1-c sem tapa. A medida é a inclinação, 0 específico e 1 generaliza tudo. São 8 vidas por unidade. O cérebro C
  só entra se tiver os ganchos do corpo.
- **A `janela_tedio` fica fixa em 8.** O objetivo da calibração (a faixa dos drives no P0-c) não separa a janela do `m_reduz`, e calibrar
  pela variedade pediria olhar o P1 (PCD-4). A janela em 4 e em 16 sai só como sensibilidade descritiva.
- **A conta de exemplo** com a bola repetida foi refeita em Python: +1440, +1298, +798, +189 e −34 para 0, 1, 4, 7 e 8 repetições.
- **O R-2** do plano estava desatualizado pela DS-4: explorar passou a reduzir o tédio. Ficou corrigido no adendo, junto com o risco novo
  R-13 (alternar só por alternar).

## 2026-10-07 — W-PLANO-TRANSFERENCIA (worker C, DS-3): o plano do teste de transferência da rejeição

Só papel: `docs/PLANO_ANALISE_V2_TRANSFERENCIA_REJEICAO.md`. Nenhuma run, nenhum código.

- **As vidas que já existem não respondem ao teste limpo.** O calendário oferece cada fruta sozinha desde o dia 1, então a transferência
  se mistura com a reexperiência, e a fome na oferta não é controlada. O plano pede run nova; o descritivo por faixa de fome nessas vidas
  fica como parte 0, só ordem de grandeza.
- **As sondas olham o estado** (a fome), de propósito, ao contrário do `CalendarioFrutas`, que só olha a semente. A diferença está
  declarada (R-3).
- **A margem `Δ_T`** é medida na própria run: metade da aversão aprendida na escolha, nos dias 6 a 10. Não há calibração, porque o ponto
  do A é o da K2. As sementes 35101…35505 são piloto, e a 36101…36505 é a validação; as duas foram conferidas livres.
- **O limiar de fome baixa (0,70)** é PROPOSTO, SEM FONTE. Ele só pode ser trocado no adendo, pelas sondas perdidas no piloto, sem olhar o
  índice.

## 2026-10-07 — W-PLANO-BANHEIRO (worker C): o plano de análise do banheiro

Só papel: `docs/PLANO_ANALISE_V2_BANHEIRO.md` (etapa 0 de `docs/TAREFA_V2_BANHEIRO.md`). Nenhuma run, nenhum código.

- **A medida primária é a média restrita (RMST) do dia até o critério, até o fim da vida, e não a mediana de Kaplan–Meier.** A censura
  é só administrativa e igual para todas as vidas. Assim a RMST é exatamente a média de min(T, τ), pareada por unidade. A mediana
  ficaria indefinida com mais da metade censurada.
- **Testa-se só se o carinho e o limpador ensinam** (B00 − B0C e B00 − BL0, com Holm). A ordem B0C antes de BL0 é requisito de desenho
  (G-CAR, seção 5b da tarefa) e sai só relatada.
- **A duração sai do piloto de 28 dias, cortado em 14 e 21.** O critério do dia d só depende dos dias até d + 2, e o orçamento por dia é
  o mesmo. A margem `Δ_B` é metade da distância P0 − P1 no B0C.
- **A calibração do conforto (BN-6) é uma conta sem vida:** o menor aumento que passa o G-CAR. A da vontade e do desconforto roda só no
  P0-B00. As faixas (2 a 5 alívios por dia, acidentes ≤ 25%) são PROPOSTAS, SEM FONTE.
- **As faixas 37101…37505 e 38101…38505** foram conferidas livres na `main` e em todos os branches remotos.

## 2026-10-07 — W-FAIXAS-R17 (rodada 17, worker D): as faixas e os prefixos do mundo físico e do corpo

- **Nenhum desvio.** As quatro faixas e os dois prefixos são os dos planos, sem mudança.
- **A fase na fonte.** A faixa de calibração de cada plano leva "calibracao" na fonte, e o teste confere que cada base cai na faixa da sua
  fase (a fonte é o que `na_faixa_reservada` devolve).
- **O K do teste de colisão** é 40 por base, acima do que os planos pedem, para folga. Os planos de antes entram com as bases que já estão
  na bancada (`BASES_EXPERIMENTO_MAIOR`, `BASES_N6`, `BASES_N7`, `BASES_COMPARACAO`); as bases dos dois planos novos ficam só no teste,
  porque a tarefa não pede constantes novas na bancada.
- **Resolve a pendência** anotada em W-PLANO-CORPO: a 31101…32505 (mundo físico) agora está em `FAIXAS_RESERVADAS`.

## 2026-10-07 — W-GABARITOS (worker A, rodada 17): as vidas de hoje do mundo físico e do corpo

Só o passo 1 do A (`docs/V2_RODADA_17.md`): dois gabaritos gravados com o código da main, num commit próprio, antes de qualquer mudança do
mundo ou do corpo, e um teste que os confere. Nenhum código do motor mudou.

- **Sementes:** só 101 e 202, das dos testes. A tarefa diz "só as sementes dos testes (101…505)"; as cinco dobrariam o tempo do teste
  (~31 s hoje) sem cobrir motor ou caminho novo.
- **Genoma no gabarito do mundo:** a semente 101 vai sem genoma e a 202 com o genoma 202. No `padrao` isso troca o motor: 101 roda no
  `MotorComFeedback`, 202 no `MotorPersonalidade`. Assim o G2 do mundo cobre os dois motores do mundo padrão.
- **Genoma no gabarito do corpo:** nenhuma vida tem genoma. A seção 2 da tarefa do corpo recusa o `MotorPersonalidade`, e com genoma o
  `padrao` cairia nele. Os três motores que o corpo vai tocar saem no gabarito: `MotorComFeedback` (padrão), `MotorAmbiente` (bola) e
  `MotorFrutasMundo` (descasado, mutável, iguais_frutas). O teste confere os três.
- **Montagem "simples":**
  - no gabarito do mundo, é a bancada padrão (ponto L1), a vida de hoje sem nada ligado;
  - no do corpo, é o ponto T3 com as peças da K2 na config, porque o corpo vai rodar no ponto da validação.
  - A "completa" é a mesma nos dois: T3, K4, canais e a montagem completa.
- **P2 e o só cuidado:**
  - o P2 só existe nos mundos das frutas, então o gabarito do corpo o tem só lá;
  - o só cuidado (`P0 <- P3`, `sem_ensino`) entra só no do corpo, na completa e nos mundos das frutas, onde a tarefa do corpo o usa;
  - o do mundo não pede o acoplado.
- **O que fica igual:** sha256 do log, do estado final, do `estado()` do motor, das ações, das rngs (política, ambiente e, quando o motor
  tem, fruta e obediência), do que o mundo registra (frutas e bola) e do estado interno da política, mais o número de interações.
- **A auditoria da seção 2 do corpo** vai no corpo do PR. Um achado entra aqui: os efeitos das ações do pet
  (`policy.efeito_da_acao_do_pet`: brincar, explorar, comer, emburrar) são literais no código, não parâmetros de `config.py`. Fica como
  achado, sem mudança: tirar os literais é tarefa do B.

## 2026-10-07 — A química dos drives de hoje (W-CORPO-QUIMICA, rodada 17, etapa 1 do corpo): interpretações

Tarefa `docs/TAREFA_V2_CORPO_DRIVES.md` (CD-1 a CD-10 decididas), etapa 1 da seção 14. Só `digilab/corpo.py` (novo), `ConfigCorpo` no fim
de `config.py`, o exportador e os testes. Motor, `engine.py`, `lobos.py` e a web não mudaram. Só as sementes dos testes.

- **O corpo não sorteia.** O `Corpo.passo(antes)` lê do `Estado` do começo do tick a sujeira, o sono e a hora. O sorteio da sujeira
  continua com o motor, na mesma posição de hoje. Ele não muda a química do tick: o desconforto usa a sujeira de antes.
- **Os literais do efeito da ação do pet** (`policy.efeito_da_acao_do_pet`: 0,02, 0,015, 0,01, 0,05, 0,01) viraram campos inteiros da
  `ConfigCorpo` (pela regra "parâmetros em `config.py`"). Um teste confere cada um contra a função de hoje, numa grade de estados. O humor
  do brincar do pet vem de `Config.humor_por_tick_brincando × intervalo_decisao_ticks`, não de um literal.
- **As conversões conferem a grade.** Todo número de hoje vezes C tem de cair num inteiro (até 1e−6, só erro de float), senão falha alto.
  O acariciar (`ganho_elogiar × 0,6` = 0,06000000000000001 em float) vira 27000. Um teste confere que tirar qualquer fator primo de C tira
  algum número de hoje da grade: 450000 é o menor.
- **A bola e a fruta** recebem o número de hoje (`ganho_humor_bola`, `nutricao`, o efeito da condição) e o convertem com a mesma
  conferência, sem importar `ConfigBola` nem `ConfigFrutas`. Sem a digestão (etapa 3), a nutrição da fruta vai direto à fome.
- **O G-HOJE (a)** é a seção 12 sem o estágio e sem o sinal do N3. O estágio é a Vida (etapa 4) e o sinal é o cérebro (etapa 5), e
  nenhum dos dois existe nesta etapa.
  - A malha aberta reproduz o `Estado` de hoje e a rng de ambiente (conferido no teste).
  - A fome, a higiene, a energia e o humor ficam a até 1e−9 do float de hoje em todo tick.
  - A saúde fica a até 1e−9 mais as viradas de privação.
  - Toda virada é um químico exatamente no limiar de 0,15, o caso que a seção 3 previa.
  - As viradas só aparecem nas vidas do relapso e do aleatório; o atencioso e o incoerente não chegam perto da privação.
- **O gabarito da paridade** vai para `tests/gabaritos/corpo_quimica_python.json`, não para `web/app/test/gabaritos/`: a web estava fora
  desta tarefa. O TS (etapa 7, do A) lê de lá ou o copia. Ele traz:
  - as taxas;
  - uma grade de casos com cada operação;
  - os passos de meia-vida e de `div_arred`;
  - três vidas em malha aberta, com a entrada de cada tick num caractere e o sha256 das concentrações depois de cada operação.

  Um teste confere que o arquivo é o que o exportador gera hoje.
- **As constantes das meias-vidas** (k 1497, 753 e 32) já ficam na `ConfigCorpo`, com a derivação conferida por teste. Nenhum químico desta
  etapa decai por meia-vida; elas servem à etapa 6.
- **O registro dos parâmetros** fica em `corpo.PARAMETROS_CORPO`, como o dos lobos, conferido contra os campos da `ConfigCorpo`, e não em
  `protocol.py`: nenhuma run de protocolo usa o corpo.

## 2026-10-07 — W-MUNDO-FISICO (worker A, rodada 17): o motor do mundo físico, etapa 2

Etapa 2 da seção 9 de `docs/TAREFA_V2_MUNDO_FISICO.md` (MF-1 a MF-4 decididas). Sem run; só as sementes dos testes.

- **Números que a tarefa não deu** (PROPOSTOS, SEM FONTE, escolhidos aqui):
  - a velocidade, 4 subunidades por tick, dá 60 por decisão, ~3 h da casa ao fundo da mata;
  - o custo de energia, 1/6000 por subunidade, faz uma decisão andando inteira custar 0,01, menos que o −0,015 do explorar;
  - o `atrito`, 8 subunidades por tick;
  - o `limiar_cheiro_explorar`, 16;
  - o passo do mundo, 15 min, o da tarefa.
- **O layout:** as 2 árvores do jardim e as 4 da mata do protótipo ficam onde estão (10 px por célula). Entram J3, M5 e M6 para chegar às
  3 + 6 da tarefa. As frutas a, b e c se alternam pelas árvores.
- **O layout afastado** do G-DIST (plano, adendo 1, A1.8) entrou como `LAYOUT_MUNDO_AFASTADO`:
  - centro da região = ((x0 + x1 + 1) // 2, 15), em células;
  - o tronco vai a 2 × a distância, cortado para dentro da região e do mapa.
- **Interpretações da seção 6:**
  - **a fruta cai** num ponto a uma direção entre 16 e uma distância uniforme de 0 a 2 células do tronco;
  - **o limite de 4 no chão** conta as frutas daquela árvore maduras ou podres no passo da queda. Todo sorteio acontece mesmo quando o
    excesso não cai;
  - **"perde `atrito` subunidades por tick até parar"** virou: a distância que falta cai `atrito` por tick. A bola anda a velocidade
    constante até o ponto final, e a posição num tick é interpolada em inteiros. O ponto final é sorteado e cortado ao mapa na hora do
    chute.
- **O DonoComLugar:**
  - "perto" é uma direção entre 16 e uma distância uniforme de 0 a 2 células;
  - "longe" é uma direção entre 16 e uma distância uniforme de 20 a 30 células, cortada ao mapa, então perto da borda fica mais perto;
  - o comedouro não sorteia.
- **O contato do `deixar_comida`** passa pelo `_contato` do `MotorEducacao` com `alimentar`. O vínculo e o `receber_acao_dono` do cérebro
  recebem `alimentar`, como hoje, sem a obediência: a recusa não existe no mundo.
- **O mundo exige educação e lesões desligadas.** É o desenho do plano (seção 2, morte desligada). Os eventos `luta`, `origem`, `fala` e
  `decisao_externa` levantam erro no `reproduzir_mundo`.
- **A ordem dos ganchos numa decisão de explorar, comer ou brincar:**
  1. o mundo aplica tudo, inclusive desfazer o +0,05 do comer (MF-2);
  2. o cérebro observa a transição, com a observação seguinte refeita;
  3. vem o `fruta_comida` (E2), se comeu fruta, madura ou podre;
  4. por último, o `consequencia_mundo`.
- **O cheiro empata muito em inteiros.** Com A = 32 e R = 24 células, andar 1 célula muda o cheiro de uma fruta em no máximo ~1,3. A
  direção medida a 1 célula empata com frequência, e no empate vence a ordem fixa. Exemplo: com uma fruta a 90 ao norte, N e NE dão 25
  cada, e o pet vai para NE. Fica como a tarefa manda. Os números do cheiro são PROPOSTOS; vale olhar antes da calibração do mundo.
- **Registros para as medidas do plano** (adendo 1, A1.8; as medidas são do D). O motor não calcula as medidas, só registra:
  - **`decisoes_mundo`**, por decisão:
    - posição antes e depois, e a região;
    - o alvo e se chegou;
    - o deslocamento e a energia gasta;
    - o que comeu e se brincou com a bola;
    - as manchas em que o pet está;
  - **`regioes`**: as chegadas e saídas de região;
  - **`visitas`**: a mancha de 3 células de cada árvore, com a chegada, a saída e as decisões tomadas de dentro;
  - **`quedas`**: as sorteadas, os pontos e as colocadas, do fluxo que não depende do pet;
  - **`consumos_mundo`, `deixadas` e `sumidas`**.

## 2026-10-07 — Os órgãos 1 e 2 do corpo: a digestão e a Vida (W-CORPO-DIGESTAO, rodada 17, etapas 3 e 4): interpretações

Tarefa `docs/TAREFA_V2_CORPO_DRIVES.md`, seções 5, 6 e 14 (CD-1 a CD-10 decididas). Só `digilab/corpo.py`, a `ConfigCorpo`, o exportador e os
testes. Motor, `engine.py`, `lobos.py` e a web não mudaram. Só as sementes dos testes.

- **O que sobra no estômago quando a fome chega a 0 é descartado.** A seção 5 dá a reação `t = min(alimento, fome, taxa)`, mas não diz o
  que acontece com o resto.
  - Hoje a fome é cortada em 1 e o excesso da comida se perde; o descarte reproduz esse corte.
  - Sem ele, a comida a mais ficaria no estômago e seguraria a fome depois, mudando os drives de hoje na taxa C (o G-HOJE falharia).
  - Com a digestão lenta, o descarte também vale: o pet saciado não aproveita o que sobra.
  - É uma decisão de desenho, registrada aqui. O total descartado fica exposto (`descartado_total`).
- **A taxa é por tick, e a comida é digerida na hora em que entra,** com o que resta da taxa naquele tick. Na taxa C isso é o "tudo no
  mesmo tick" da CD-3: a fome lida depois do alimentar é a de hoje, também na decisão que vem logo depois, no mesmo tick.
  - Se a comida esperasse o próximo tick, a decisão logo depois do alimentar veria a fome de antes, e o G-HOJE falharia.
  - **O limite de C por tick só morde se a fome subir dentro do próprio tick depois de zerar** (por exemplo, três refeições, o brincar do
    dono e uma quarta refeição no mesmo passo). Nas vidas do G-HOJE isso não acontece: o estômago fica vazio depois de toda operação, e a
    química com a digestão é a da etapa 1, químico a químico (testes).
- **O que é comida:** a ração do alimentar, o comer do pet e a nutrição da fruta. O custo de fome do brincar do dono não é comida; ele
  continua mexendo direto na fome. O efeito da fruta no humor vai direto à tristeza, não pelo estômago.
- **O digerido do tick** (`digerido_no_tick`) é o do último tick fechado, ingestões e passo juntos. É o que a vontade do banheiro vai ler
  (`docs/TAREFA_V2_BANHEIRO.md`, seção 3).
- **v = 11** = C // (28 × 1440): a Vida dura a vida mais longa da pesquisa, os 28 dias do bloco de durações do adendo 3. A seção 6 diz que
  o v "sai da duração máxima de vida da pesquisa"; a leitura foi essa.
- **Os ticks de estágio de hoje** são os de `treino_stats.estagio_no_tick`, com a `ConfigEvolucaoPesquisa` do motor (a de hoje e a
  canônica da `ConfigDuracoes`). O `Corpo` recebe a `cfg_evo`.
  - O teste confere tick a tick, nas três durações, do nascimento até depois do fim da Vida.
  - Nos motores com estágio (o `MotorTreino` e o `MotorEducacao`), os ticks das transições gravadas no motor batem com os cruzamentos da
    Vida.
  - O motor só troca de estágio num checkpoint. Os ticks de estágio (180, 900, 1980; 360, 1800, 3960) caem em decisões, então batem
    exatos.
- **A Vida não mata:** em 0, fica em 0, e o estágio fica adulto. Um limiar que não fica acima de 0 (a Vida acabaria antes do estágio)
  falha alto ao montar o corpo.
- **Sem receptor para o cérebro:** nem o `alimento` nem a `vida` entram nos `receptores()`. O `estagio()` é do motor.
- **O gabarito da paridade** (`tests/gabaritos/corpo_quimica_python.json`, versão 2) ganhou:
  - a digestão na taxa C;
  - a grade com uma taxa lenta (1000), que é só para a paridade da reação, não um valor de pesquisa;
  - a Vida, com os limiares nas duas durações, a grade em volta deles e as vidas com os ticks de estágio.

  As partes da etapa 1 não mudaram.

## 2026-10-07 — W-MEDIDAS-R17 (rodada 17, worker D): as medidas do mundo físico, do corpo e do banheiro

As escolhas abaixo são de formato e de borda; nenhuma muda uma definição dos planos.
- **A trajetória é uma entrada por decisão,** mesmo sem deslocamento: a posição depois do passo daquela decisão, que vale até a seguinte
  (o motor anda de uma vez, na decisão). Com isso:
  - a visita vai do tick da primeira entrada dentro da mancha ao da primeira fora;
  - "ao menos uma decisão dentro" conta as entradas da visita depois da primeira, mais a de saída. Só uma visita que começa na última
    decisão da vida fica com zero;
  - a visita entra na janela pelo tick de início.
- **Manchas que se sobrepõem** contam uma visita em cada árvore. O plano não diz; a alternativa (uma visita por posição) pediria uma regra
  de desempate.
- **A mancha** é `isqrt(dx² + dy²) ≤ 3 × 16` em subunidades, e o custo de viagem é a mesma distância dividida por 16 (em células, com
  fração). Os troncos entram em subunidades, convertidos do layout pelo motor.
- **A visita censurada** (não termina até o fim da vida) fica fora das inclinações, da taxa no abandono e da permanência média, contada à
  parte.
- **A taxa recente** é `None` quando as 24 h começam antes do nascimento (não acontece nos dias 8 a 14).
- **A taxa no abandono** usa os ganhos em [fim − 30, fim): o consumo no tick da saída não conta.
- **Os drives:** a média entra com todas as decisões da janela; a fração acima de 0,75 só com as acordado e com `≥` (o "≥ 0,75" do adendo).
- **A variedade** conta as atividades estritamente antes da decisão, e com menos de 8 na janela, as que houver.
- **A inclinação da generalização:** uma fruta não punida sem valor num dos lados fica fora da média, contada em `faltam`; sem nenhuma
  não punida com valor, a unidade sai "indefinida", como quando a queda na punida não é positiva.
- **O dia do critério** generaliza o horizonte como τ = D − seguidos + 2, que é o D − 1 do plano com 3 dias seguidos.
- **Fica de fora, por não ser desta tarefa:** as faixas 37101…38505 e o prefixo `"banheiro"` na bancada (seção 10 do plano do banheiro, a
  etapa 5 da tarefa) e os descritivos da seção 5.3 do mundo e 5.4 do corpo, que a tarefa não listou.

## 2026-10-07 — W-ADENDO-CORPO-D4 (worker C): o adendo 2 do plano do corpo, a dominância de um drive

Só papel: o adendo 2 de `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md` (D-4 de `docs/DEFINICOES_CORPO_V2.md`). Nenhuma run, nenhum código.

- **A parcela de cada drive usa o valor absoluto da contribuição.** Brincar reduz o tédio e aumenta o cansaço; com o sinal, a soma pode
  ficar perto de 0 e a fração explodir. A contribuição com o sinal sai ao lado.
- **"Domina" é por decisão e por maioria:** o drive lidera uma decisão com parcela ≥ 0,80, e domina se lidera mais da metade das
  decisões de tempo livre (limite inferior do IC95 acima de 0,50), no P1-c do mundo `bola`. É normal um drive liderar uma decisão,
  porque cada ação mexe em poucos drives; o que não é normal é um só liderar a maioria. Os limiares são PROPOSTOS, SEM FONTE.
- **O braço P1-cw (peso pela janela recente, J = 32, piso de um quarto) roda sempre na validação,** como descritivo qualificado.
  Assim o desenho não depende de dado do P1 (PCD-4). São 8 vidas por unidade a mais.
- **As citações:** Keramati e Gutkin 2014 e Roijers et al. 2013 só pelo resumo. Hulme et al. 2019 não é citado.

## 2026-10-07 — W-CORPO-MOTOR (worker A, rodada 17): o corpo no motor, etapa 2

Etapa 2 da seção 14 de `docs/TAREFA_V2_CORPO_DRIVES.md`. Sem run; só as sementes dos testes.

- **O `MotorCorpo` é um mixin.** Ele vai na frente de cada motor de hoje por `com_corpo(base)`: `MotorComFeedback`, `MotorAmbiente` e
  `MotorFrutasMundo` (este, da bancada). Um motor só não caberia: o `MotorComFeedback` do mundo `padrao` não está na cadeia do
  `MotorAmbiente`.
- **O laço do tick é refeito no mixin** (seção 2, o caminho recomendado). Os efeitos por avanço das classes do meio ficam: o contador de
  eventos do `MotorPersonalidade` e a morte do `MotorEducacao`.
  - Uma classe nova na cadeia que sobrescreva `_avancar` falha alto, porque o laço não a refaria.
  - O `state.avancar_um_tick` continua sendo chamado para o tick e para a sujeira (a mesma rng, na mesma ordem); os drives float que ele
    calcula são trocados pela leitura.
- **Os escritores de hoje viram estímulo assim:**
  - a ação do dono: o `_aplicar_acao_usuario` de baixo roda inteiro (sujeira, sono, contato, vínculo, cérebro), e depois os drives vêm do
    `Corpo.acao_dono`;
  - a fruta: o `_comer` do `MotorFrutas` é sobrescrito, então o estímulo entra antes do gancho `fruta_comida` da E2. O cérebro vê a
    fruta já na grade;
  - a bola: ela escreve o humor dentro do `observar`, então o estímulo entra logo depois.
- **O G-BYPASS confere em dois lugares:**
  - no começo de cada tick e antes de cada ação do dono, o `Estado` tem de ser a leitura da química, exato;
  - depois de cada escritor de hoje, só os drives do estímulo podem ter mudado. A conferência vem antes do estímulo: depois dele o float
    de baixo e a leitura podem diferir no último bit (0,8775000000000001 × 0,8775 com a bola), e a leitura é o que vale.
- **O que falha alto com o corpo** (seção 2):
  - a obediência ligada, a educação e as lesões;
  - uma ação de treino: o "treino ligado" da tarefa, porque o motor de treino está sempre na cadeia;
  - o petisco e qualquer outro escritor sem estímulo, pelo G-BYPASS;
  - **o mundo físico ligado**: o andar, as comidas do mapa e o MF-2 ainda não têm estímulo no corpo. O custo de andar vira um inteiro
    exato de C: 1/6000 × 450000 = 75 por subunidade, então não precisa de arredondamento. Falta o estímulo no `corpo.py` (do B) e a
    ligação aqui.
- **A Vida:** com o órgão 2 e um motor com estágio, o estágio pelos receptores da Vida é conferido contra o de hoje
  (`treino_stats.estagio_no_tick`, com a `cfg_evo` do `TreinoPet`) a cada tick, e falha alto se diferir. O estágio do motor continua o de
  hoje; a Vida não o substitui nesta etapa.
- **O gancho `consequencia_corpo`:**
  - é uma chamada por decisão, logo depois dos estímulos da própria ação e antes do tempo e do dono;
  - o `ocorrido` traz a ação e a lista de estímulos, `("pet", ação)`, `("bola",)` e `("fruta", f)`;
  - o `obs_depois` traz o `obs.corpo`.
- **A `PercepcaoCorpo`** fica em `digilab/motor_corpo.py`, para nenhum cérebro precisar de `digilab/corpo.py` (G-RECEPTOR). Os campos dos
  drives novos e dos gestos ficam `None` até a etapa 6.
- **Achado para o G-HOJE (b) do plano.** Em malha fechada a vida com o corpo diverge cedo, e não só pelos limiares da seção 3:
  - os pesos do tempo livre são contínuos nos drives (`1 + 3·humor`, por exemplo), e uma diferença no último bit muda o sorteio quando o
    `u` cai perto da fronteira;
  - na medida informal (instinto, 4 donos × 5 sementes, 3 dias, sem artefato) divergem 18 de 20 vidas no `padrao`, 19 na `bola` e 17
    nas frutas, a maioria entre a decisão 24 e a 30 (de 288).
  - O G-HOJE (b) é pela distribuição, como o plano já diz. Esperar vidas iguais em malha fechada não vale nem para o dono atencioso.
