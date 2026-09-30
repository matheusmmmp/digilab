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
