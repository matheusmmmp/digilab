# Design — educação, herança, lesões e donos gerados (Fase 1)

Status: **para aprovação**. Nada foi implementado. Cada parâmetro está marcado como:

- **DECIDIDO**: vem do Matheus ou de regra que já existe;
- **PROPOSTO**: escolha minha, com a fonte ou "sem fonte".

Os valores PROPOSTOS entram em `protocol.py` com esse status. Uma run que use qualquer um deles grava aviso, como já acontece hoje.

## 0. Ponto de partida: a confirmatória

`artifacts_confirmatoria/resultado.json`, commit 89738ab. Desenho B, condição neutra, N = 160 ovos:

- atencioso − aleatório = **−0,034**, IC95 [−0,072; +0,006], p = 0,095;
- pela seção 5 do plano, a hipótese central foi **REFUTADA**: o IC ficou inteiro dentro de ±0,10;
- os donos com estilo marcado ficaram **abaixo** do aleatório (Holm): relapso −0,047, incoerente −0,070, exigente −0,129;
- a vantagem do atencioso só aparece na condição real (saúde física), no desenho A: 0,581, IC95 [0,521; 0,639].

O que isso significa para o design: hoje o cuidado só chega à luta pela saúde física. O que o pet aprende com o dono não o torna melhor lutador. Os sistemas A e C abaixo criam dois caminhos explícitos e mensuráveis do cuidado até a luta:

- **disciplina**, que diz se o pet obedece em momentos críticos;
- **histórico de lutas e lesões**, que decide a forma adulta e a sobrevivência.

A hipótese nova (seção 7) é registrada **antes** de qualquer run. A confirmatória não é refeita nem reinterpretada.

## 1. Regras que continuam valendo

- `engine.py` congelado. Tudo entra por uma subclasse nova, **`MotorEducacao(MotorTreino)`**, que guarda a disciplina, as janelas de travessura e as lesões. O `Estado` v0 não muda.
- Parâmetros ficam em `config.py`, numa dataclass nova `ConfigEducacao` e em `ConfigLesoes`.
- RNGs separadas, cada uma derivada da semente do motor com o seu próprio rótulo:
  - `rng_travessura`: sorteia **quando** uma travessura acontece. É ambiente: não depende do dono, então trocar de dono não muda o clima;
  - `rng_heranca`: mistura e ruído da herança;
  - a RNG de política dos donos continua a de hoje.
- **Modo livre gravado** (exceção do CLAUDE.md de 2026-09-28): toda saída de LLM entra no log como evento `decisao_externa`. O modo determinístico é o padrão.
- A arena de pesquisa (`run_arena.py` / `run_poder.py`) **não gera lesões nem conta para a evolução**.
- A resolução do combate não muda.

## 2. Sistema A — travessuras e educação

### 2.1 Estado novo (em `MotorEducacao`, não no `Estado`)

| Campo | Faixa | Observação |
|---|---|---|
| `disciplina` | 0–100 | começa em 0 no ovo |
| `janela` | — | travessura aberta: tipo, tick de início, prazo |
| `acertos_consecutivos` | por tipo | serve ao aprendizado por N acertos |
| `reforco_falso` | 0 ou mais | quantas vezes o dono cedeu com petisco a um chamado falso |

### 2.2 Travessuras que exigem o dono

Todas abrem uma janela. O pet **não resolve sozinho**: sem a resposta do dono, vence o prazo e acontece a consequência.

| Travessura | Resposta certa | Resposta errada | Se ignorar |
|---|---|---|---|
| **Chamado falso**: chama sem necessidade real; se oferecem refeição, recusa, mas aceita petisco | `repreender` → disciplina +passo | `petisco` → cede, `reforco_falso` +1 (mais chamados falsos depois) | disciplina −passo |
| **Mau humor legítimo**: humor baixo de verdade | `elogiar` / `acariciar` → humor sobe | `repreender` → "bronca sem motivo": vínculo cai | humor continua caindo |
| **Aviso antes de sujar** | `levar_ao_banheiro` (ação nova) → sem sujeira; disciplina +`disciplina_por_banheiro` (**0**, desvio da Fase 2 parte 3: com +passo o permissivo chegava a disciplina 100 só pelo banheiro e o chamado falso sumia; aguarda decisão do Matheus) | — | vira sujeira, como hoje |

Travessuras que se resolvem sozinhas (sem janela):

- **acordar dormindo**: sono interrompido, energia cai;
- **superalimentação**: comer demais faz mal à saúde.

Fora do escopo desta versão: **presente maldoso**.

Ações novas do dono (`AcaoUsuario`): `petisco`, `levar_ao_banheiro` e `tratar_lesao` (sistema C). Cada uma consome **1 interação do orçamento**, como qualquer outra ação.

### 2.3 Parâmetros

| Parâmetro | Valor | Status | Fonte |
|---|---|---|---|
| janela da travessura | 15 min | DECIDIDO | `janelas.chamado_min` em `docs/cronograma_interacoes.json` |
| chamados a partir de | criança | DECIDIDO | Fase 0, item 6 |
| intervalo médio dos chamados por estágio | o `intervalos_min` de cada estágio no cronograma | DECIDIDO | cronograma (hoje só o bebê usa) |
| fração de chamados que são falsos | 0,25 × (1 − disciplina/100), mais 0,05 por `reforco_falso` (teto 0,5) | PROPOSTO | sem fonte. No Tamagotchi o chamado falso some com a disciplina cheia; a forma da curva é minha |
| chamado real × falso (Fase 2, parte 2) | o chamado é **real** se a necessidade pedida (fome, higiene ou humor) está abaixo de 0,35, o mesmo `limiar_necessidade_pedido_adequado` dos donos. Se a necessidade está em dia, o slot vira **falso** com a chance da linha acima (0 com disciplina cheia ou depois de 3 acertos seguidos no estágio). O dono vê o pedido, nunca se é falso | DECIDIDO (limiar) / PROPOSTO (regra) | a regra imita o Tamagotchi: o dono descobre olhando os medidores |
| petisco | 0,5 do ganho de alimentar, sem sorteio de sujeira e sem obediência. Conta como cuidado que atende: ceder **reforça o chamar_atencao** também na política aprendida | PROPOSTO | sem fonte |
| passo de disciplina por bronca certa | +25 (4 broncas certas enchem) | PROPOSTO | comunidade Tamagotchi: o medidor tem 4 barras. Fonte não verificada; confirmar link |
| disciplina cheia acaba com o chamado falso | sim | DECIDIDO | enunciado da tarefa |
| aprendizado: o pet para de repetir uma travessura depois de N acertos seguidos | N = 3 | PROPOSTO | Digimon Pendulum/4U, pela comunidade. Fonte não verificada |
| disciplina ao evoluir | cai para 50% do valor | PROPOSTO | sem fonte (valor que propus na Fase 0) |
| efeito da disciplina na luta | chance de obedecer a ordem do dono em cada turno crítico. **Nenhuma** mudança no dano ou nas regras | PROPOSTO | sem fonte. Liga à obediência que já existe (`obediencia.py`), sem mexer no combate |

### 2.4 Dono novo: **permissivo**

- Sempre atende a chamados e travessuras dentro da janela.
- Responde com `petisco` ou `acariciar`, nunca com `repreender`.
- Gasta o mesmo orçamento, como todos os donos.

É o contraste com o atencioso: presença alta e educação zero.

## 3. Sistema B — gerações e herança

- **Herdado**:
  - temperamento: média dos pais mais ruído N(0; σ) na `rng_heranca`, cortado na faixa;
  - espécie: sorteada entre as espécies dos pais.
- **Não herdado**: nada aprendido (posterior do bandit, memória, caráter aprendido, disciplina, vínculo) e nenhum traço da camada 3.
- **Log do filho**: começa com um evento-cabeçalho `origem`, que traz:
  - o sha256 dos logs dos dois pais;
  - a semente da herança;
  - a identidade de quem cruzou.

  O replay do filho confere os hashes quando os logs dos pais estão disponíveis, e falha alto se não baterem.
- **Pais de donos diferentes**: permitido. O cabeçalho guarda os dois hashes. Não há troca de log por rede nesta tarefa (não é multiplayer): o cruzamento é local, a partir dos dois arquivos de log.

| Parâmetro | Valor | Status | Fonte |
|---|---|---|---|
| σ do ruído do temperamento | 0,1 | PROPOSTO | sem fonte |
| idade mínima dos pais | adulto | PROPOSTO | sem fonte |

## 4. Sistema C — vitórias, lesões e evolução (camada Digimon Color)

Nenhuma dessas regras toca a resolução do combate. Elas leem o resultado da luta.

- **Evento novo no log de vida**: `luta` com o rival e a semente da partida.
  - O resultado e a lesão **não** vão para o log. O replay os reconstrói, rodando a partida pela semente.
  - Assim o log continua pequeno e à prova de adulteração.
- **Contam para a evolução**: lutas contra NPC e da arena do jogo. A arena de pesquisa não conta.
- **Taxa de vitória** só vale na transição **adolescente → adulto**:
  - no mínimo 10 lutas, o mesmo número do sparring de hoje;
  - com taxa ≥ 0,8, a forma adulta "de vitória" fica disponível;
  - abaixo disso, vale a regra atual de forma.
- **Contadores** de vitória, derrota e lesão **zeram ao evoluir**.
- **Lesão**: sorteada ao fim de cada derrota, na `rng_travessura`.
  - Lesão sem tratar (`tratar_lesao`) derruba a saúde a cada hora.
  - Morte com lesões acumuladas demais **ou** com tempo demais sem tratar.
- **Treino forçado não causa lesão** (Fase 0).

| Parâmetro | Valor | Status | Fonte |
|---|---|---|---|
| lutas mínimas para a taxa contar | 10 | DECIDIDO | Fase 0; igual a `sparring_minimo_adulto` |
| limiar da taxa de vitória | 0,8 | PROPOSTO | Digimon V-Pet Color, pela comunidade. Fonte não verificada |
| chance de lesão por derrota | 0,2 | PROPOSTO | sem fonte |
| lesões acumuladas até a morte | 20 | PROPOSTO | Digimon Ver.20th, pela comunidade. Fonte não verificada |
| tempo máximo com lesão sem tratar | 6 h | PROPOSTO | Digimon Ver.20th, pela comunidade. Fonte não verificada |

## 5. Sistema D — ajustes

- **Duas configs de duração dos estágios**:
  - `teste`: 3/12/18 h (os valores de hoje, para simular rápido);
  - `canonica`: 6/24/36 h (os v-pets citados no cronograma).
  - As duas ficam em `config.py`. O protocolo novo registra qual delas usa.
- **Relapso**: o orçamento **continua igual** entre os donos (DECIDIDO, é o que torna a comparação justa). **Nada muda** (correção na Fase 2, parte 6):
  - as 3 visitas por dia **já eram** sorteadas pela RNG de política dele (`DonoRelapso._planejar_dia`), e não fixas como este documento dizia;
  - com as janelas de 15 min, quem as perde é o relapso: na vida de teste de 3 dias ele atende 1 de 19 avisos e 0 de 2 chamados reais. É exatamente isso que o distingue.
- **O pet não cuida de si mesmo**: travessuras e chamados só se resolvem pela ação do dono (seção 2.2). É um teste de regressão.

## 6. Sistema E — LLM (liberado em 2026-09-28)

Custo e capacidade estão em `artifacts_custo_llm/`, gerados por `tools/estimar_custo_llm.py`.

- **Donos-persona**:
  - `tools/gerar_personas.py` pede à LLM N personas em JSON (horários, chance de ceder com petisco, atraso típico, estilo de bronca…);
  - o JSON é validado por esquema, congelado no repo e tem hash no protocolo;
  - `DonoPersona` roda esse JSON de forma determinística, sem chamar a LLM de novo;
  - custo de uma geração: centavos.
- **Modo livre gravado**:
  - a LLM decide ao vivo no lugar do dono ou do pet, só em **eventos** (travessura, janela aberta), nunca a cada passo;
  - cada resposta vira um evento `decisao_externa` no log;
  - numa run do tamanho da confirmatória, isso dá 84 a 102 h de GPU local (os modelos qwen), ou cerca de US$ 273 no Haiku.
- **Travessuras sugeridas pela LLM**: entram só como propostas neste documento, e cada uma passa pela aprovação do Matheus.
- **A LLM fica fora de `digilab/`**, que continua só com stdlib. O cliente mora em `servidor/` ou `tools/` e chega ao motor por uma interface injetada.
- **Análises com LLM são exploratórias**. Nunca confirmatórias.

## 7. Onde medir a hipótese

- **Onde**: a arena de pesquisa V21C, desenho B, condição neutra, o mesmo encanamento da confirmatória. Esse é o único "chão" sem lesão e sem efeito de evolução.
- **Hipótese exploratória nova**, com plano próprio (`docs/PLANO_ANALISE_V3.md`, registrado antes da run):
  - *com educação e evolução por vitórias ligadas, o atencioso passa o aleatório e o permissivo no painel B*;
  - o efeito tem que vir pela forma adulta alcançada e pela disciplina, não pelo aprendizado de luta, que a confirmatória já mostrou que não conta.
- **Braços**: atencioso, aleatório, relapso, incoerente, exigente, **permissivo** e, opcionalmente, uma população de personas geradas.

## 8. Critério de equilíbrio dos estilos de jogo

Um critério de aceite da Fase 3, que vira um gate novo na bateria:

- os três estilos (**cuidar**, **treinar** e **lutar**) têm que chegar a adulto com taxa contra o painel entre 0,40 e 0,60 — PROPOSTO, sem fonte;
- nenhum estilo pode vencer os outros dois por mais de 0,15 — PROPOSTO, sem fonte;
- nenhum dono sintético pode dominar todos os outros, no mesmo espírito do E1 "sem arquétipo dominante".

## 9. Eventos novos no log e impacto no hash

| Evento | Quando | Conteúdo |
|---|---|---|
| `acao_usuario` com `petisco`, `levar_ao_banheiro` ou `tratar_lesao` | ação do dono | como hoje |
| `luta` | luta fora da arena de pesquisa | rival, semente |
| `origem` | primeiro evento do filho | hashes dos pais, semente da herança |
| `decisao_externa` | só no modo livre | fonte (modelo), resposta, versão do prompt |

- **Replay**: um evento desconhecido continua levantando erro. Os logs antigos (sem os eventos novos) rejogam **iguais**, bit a bit, porque o `MotorEducacao` só liga com config explícita. Isso vira teste.
- **Protocolo**: um protocolo novo `educacao-v1`, com hash próprio. Os protocolos `arena-v1` e da confirmatória **não mudam**, e os hashes deles continuam conferidos.
- **Web**: só na Fase 4. O save ganha os eventos novos, e a paridade Python/web é testada pelo mesmo log.

## 10. Plano da Fase 2 (partes pequenas, um commit cada)

1. `ConfigEducacao` e `ConfigLesoes`, as ações novas e o `MotorEducacao` vazio, com o teste de que logs antigos rejogam iguais.
2. Disciplina e chamado falso, o dono permissivo e os testes de janela.
3. Mau humor, aviso antes de sujar e as travessuras que se resolvem sozinhas.
4. Evento `luta`, lesões e evolução por vitórias.
5. Herança e evento `origem`.
6. Configs de duração e o ajuste do relapso.
7. `DonoPersona`, o gerador de personas e o modo livre gravado.

Cada parte traz testes de replay e de determinismo.
