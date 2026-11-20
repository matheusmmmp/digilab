# Plano de análise — V2, A1: a bola como primeiro objeto do mundo com consequência

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status: **registrado antes de qualquer run** (2026-10-01). Nada foi rodado para escrever este plano. Tarefa
`docs/TAREFA_V2_A1_BOLA_IMPL.md`; desenho aprovado `docs/V2_A1_BOLA_DESENHO.md` (PR #113, opção A); nó N2 de
`docs/ARQUITETURA_V2_VALIDACAO.md`; definições D4 e D6 de `docs/DEFINICOES_V2.md`. Todo número abaixo é PROPOSTO, sem fonte, salvo quando
aponta um artefato ou um símbolo de `digilab/config.py`.

**Pergunta (1a-pet).** Com a bola no cenário, o comportamento do pet muda, com o cuidado controlado? Aqui **sem aprendizado**: a bola
entra pelo instinto, com a chave (`ConfigBola.ligada`), e o dono muda a situação, não o pet. A pergunta 1a-dono (a bola aumenta o
efeito do dono) é **registrada como sem apoio na literatura (D6) e não é testada nesta tarefa**: exige o aprendiz (A1 + L1, chat B).

## 1. O que entra no código (sem mudar nenhum resultado da v1)

| peça | onde | regra |
|---|---|---|
| ações do dono `por_bola`, `tirar_bola` | fim de `events.AcaoUsuario`; `ACOES_BOLA` | só o `MotorAmbiente` aceita; os outros motores levantam erro (como `ACOES_EDUCACAO`). Os donos da v1 sorteiam de `ACOES_V1` (tupla fixa): o enum crescer não muda a canônica; o bandit usa `tuple(AcaoPet)` (teste confirma) |
| entrada `bola` na percepção | `policy.Observacao.bola: float = 0.0` (campo com padrão; `de_estado` não o preenche) | o `MotorAmbiente` embrulha a política (como `_PoliticaObservada`) e passa `replace(obs, bola=1.0 ou 0.0)` em `agir`; `features` do bandit e sondas não leem o campo |
| instinto com a bola | `policy.PoliticaInstinto._pesos_tempo_livre(...)` (extração sem mudar valor nem ordem das contas); subclasse `ambiente.PoliticaInstintoBola` | com `ligada` e `obs.bola > 0`, na regra de tempo livre, `brincar` ganha `+ w_bola × bola` e a regra vira `bola_no_cenario`; nenhuma chamada de rng a mais (o mesmo `rng.choices`). Hook vazio `receber_acao_dono` para rodar no `MotorPersonalidade` |
| `MotorAmbiente(MotorEducacao)` | `digilab/ambiente.py` | estado da bola fora do `Estado`: `{tick_posta, prazo}`; pôr renova; tirar sem bola levanta erro; **pôr não é contato** (não zera `tick_ultimo_cuidado`, não passa pela política, vínculo nem janela da educação); no `_decisao_observada`: expira no prazo; `brincar` com bola presente = consequência (humor `+ ganho_humor_bola`, cortado em 1) e a bola some; contadores (postas, usadas, expiradas, renovadas, decisões com bola, ignoradas). `estado()` ganha `"bola"` |
| replay | `ambiente.reproduzir_ambiente` = `educacao.reproduzir_educacao` com a fábrica do `MotorAmbiente` (os eventos são `acao_usuario` de sempre) | divergência no replay para tudo |
| `ConfigBola` | `digilab/config.py`; registro `protocol.PARAMETROS_BOLA_A1` (à parte de todo hash) | `ligada False`; `duracao_min 60`; `ganho_humor_bola 0,15`; `w_bola 3,0`; `bolas_por_dia 4` |
| donos com bola | `ambiente.DonoComBola` embrulha o dono da v1 | atencioso e incoerente: pet acordado, fora da noite, sem cuidado pendente (`cuidados_necessarios` vazio), sem bola no cenário, no máximo `bolas_por_dia` → `por_bola` no fim das ações do passo, dentro do máximo permitido; relapso: só nos passos em que a base devolveu ação; aleatório: `por_bola` entra no sorteio uniforme (`ACOES_V1 + por_bola`); ninguém usa `tirar_bola`. A bola consome 1 interação do orçamento |
| não muda | `engine.py` (sha256), `AcaoPet`, o bandit, `policies/lobos.py`, protocolos e runs da v1, a web | — |

## 2. Gates (PROPOSTOS)

| gate | definição operacional | passa se |
|---|---|---|
| **G1 replay** | cada vida gravada (`vidas/*.jsonl`) é reconstruída do disco: estado, ações, rngs de ambiente, política e obediência e `estado()["bola"]` iguais | igualdade exata (teste e orquestrador) |
| **G2 equivalência** | (a) `MotorAmbiente` com `ligada=False` × `MotorEducacao`, nas vidas da V3 rejogadas do disco (`artifacts_educacao/vidas`, as do `test_reproducao_v3_confirmatoria`); (b) `MotorAmbiente` (obediência desligada, educação e lesões desligadas, temperamento neutro) com `PoliticaInstintoBola` desligada × `MotorComFeedback` com `PoliticaInstinto`, 4 donos × 5 sementes × 3 dias; (c) ligada, sem `por_bola` no log = desligada | byte a byte nas três |
| **1a-pet** (sem gate numérico de magnitude; D6) | por semente, no braço `bola`: `Δp = p(brincar \| bola presente) − p(brincar \| bola ausente)` nas decisões de tempo livre, média dos 4 donos; IC95 bootstrap sobre sementes (10 000, semente 20261001) | limite inferior do IC **> 0** |
| **cuidado controlado** (G5 descritivo, D4) | por semente e dono: fração das decisões em privação (`Estado.em_privacao(cfg)` no tick da decisão), saúde final e mortes, no braço `bola` menos no braço `sembola`; e o acoplado (seção 3) ao lado | mortes **= 0** em todos (sem lesão no desenho: por construção) **e** o IC da diferença de privação contém 0 |
| descritivos | bolas postas, usadas, expiradas e ignoradas por dono; humor médio nas decisões (bola − sembola); p(brincar \| bola) por dono; orçamento gasto em bolas | — |

Parada: 1a-pet ou o cuidado controlado falhando na validação = **resultado negativo registrado**; nada se reajusta olhando a validação.

## 3. Desenho

- **Vidas:** o da arena v1 (`PROTOCOLO_ARENA_V1`: 4 donos, 224 = 16/dia × 14 dias), `simular_vida` com `fabrica_motor` = `MotorAmbiente`
  (obediência desligada, educação e lesões desligadas, temperamento neutro, espécie `brasa`), `rotulo_dono` fixo por dono. Braços:
  - **`<dono>-bola`**: `ConfigBola` ligada, `PoliticaInstintoBola`, `DonoComBola(dono)`;
  - **`<dono>-sembola`**: chave ligada, dono da v1 (nunca põe): é a vida do instinto da v1 (serve ao G2 b);
  - **`<dono>-bolacega`**: dono põe, política com `w_bola = 0` (o instinto não vê): isola o efeito do ambiente sem resposta da política;
  - **`atencioso-cuidado`** (acoplado, D4): o log de `atencioso-bola` sem `elogiar`, `repreender`, `por_bola` e `tirar_bola`, rejogado
    (`run_v2_l1.log_so_cuidado` + filtro das ações da bola); variante `-semcarinho`. Volume relatado.
- **Medidas** com um gravador no replay (como `run_v2_l1._Gravadora`): por decisão, tick, bola presente, regra do instinto, ação, humor,
  energia, privação. Funções novas em `digilab/metrics.py`: `resposta_a_bola(decisoes)` e `privacao_nas_decisoes(decisoes)`, com teste.
- **Sementes:** calibração **6101, 6202, 6303, 6404, 6505**; validação **7101, 7202, 7303, 7404, 7505**, uma vez. Nenhuma outra.
- **Meta da run:** sha256 de `digilab/ambiente.py`, `policy.py`, `config.py`, `metrics.py`, `engine.py`; Python e plataforma; a
  `ConfigBola` usada.

## 4. Calibração (6101…6505)

Grade: `duracao_min` {30, 60, 120} × `ganho_humor_bola` {0,05; 0,15; 0,30} × `w_bola` {1, 3, 6} = 27 pontos; `bolas_por_dia` fixo em 4,
com sensibilidade {2, 8} só no ponto escolhido. Em cada ponto: os braços `bola` e `bolacega` (o `sembola` não depende do ponto).
**Escolha, decidida aqui:** entre os pontos com `p(brincar | bola)` médio em **[0,30; 0,80]** (uma decisão, não um reflexo nem indiferença) e
o IC da diferença de privação contendo 0, o de **maior limite inferior do IC de Δp**; empate → menor `ganho_humor_bola`, depois menor
`w_bola`, depois menor `duracao_min`. Sem ponto na faixa: o de maior limite inferior de Δp, e o relatório diz que a calibração não fechou.
O ponto vai para `experiments/configs/v2_a1/validacao.json` e para os padrões de `ConfigBola`. Só nele rodam o acoplado e a sensibilidade.

## 5. Validação (7101…7505, uma vez)

Os mesmos scripts (`experiments/run_v2_a1.py --config experiments/configs/v2_a1/validacao.json`): todos os braços, G1, G2 (testes),
1a-pet, cuidado controlado, acoplado e descritivos em `artifacts_v2_a1/validacao/` (`resultado.json`, `pet.json`, `so_cuidado.json`,
`vidas/`). Resultado em `docs/RESULTADO_V2_A1.md` e seção própria no `CLAUDE.md`. Se falhar, registra-se e a V2 segue (decisão de 2026-10-01).

## 6. O que não entra

A regra `bola_no_cenario` e os pesos do lobo de decisão (`policies/lobos.py`, chat B, A1 + L1); 1a-dono; frutas; web (pets v12 só se
a bola for para o produto, `ROADMAP_V2.md` M8); corpo 2D; `tirar_bola` nos donos sintéticos; sorteio na bola (sem rng nova).
