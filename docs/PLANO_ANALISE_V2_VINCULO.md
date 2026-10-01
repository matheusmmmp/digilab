# Plano de análise — vínculo B (previsibilidade + desejo) em vidas novas

Status: **registrado antes de qualquer run** (2026-10-01). Nada foi rodado para escrever este plano. Tarefa
`docs/TAREFA_V2_F0_VINCULO_NOVO.md`; decisão do Matheus (2026-10-01): **alternativa B** de `docs/V2_VINCULO_PROPOSTA.md`.
Os números citados vêm de artefatos em disco, cada um com o arquivo; valores sem fonte estão marcados PROPOSTO.

## 1. Pergunta

O vínculo redesenhado pela alternativa B deixa de premiar o dono aleatório **em vidas novas**? Os números do #109 são
contrafactuais sobre o fluxo gravado (eventos fixos); aqui o vínculo novo entra na obediência e a vida muda com ele.

| ponto de partida | número | artefato |
|---|---|---|
| vínculo de hoje, atencioso − aleatório (personalidade, 10 ovos) | −0,069 [−0,206; +0,074] | `artifacts_v1_personalidade/completa/metrics.json` |
| vínculo de hoje, atencioso − aleatório (E1, 640 vidas) | −0,176 [−0,291; −0,061] | `artifacts_linhagem/sinal_dono/resultado.json` |
| contrafactual B (coerência por situação + desejo, sem atendimento), personalidade | +0,186 | `artifacts_v2_vinculo/resultado.json` → `personalidade.contrafactuais` |
| contrafactual B, E1 | +0,051 | idem → `e1.contrafactuais` |
| Megas em 6 vidas com o limiar 0,4, vínculo de hoje (web, pets v5): atencioso 3, aleatório 5 | | `artifacts_campanha/mega/limiar_vinculo.json` |

A hipótese é que, em vidas novas com os cinco donos sintéticos do treino, atencioso − aleatório no vínculo final seja positivo.
O contrafactual do E1 (+0,051) avisa que o efeito pode ser pequeno quando o dono dá pouco feedback.

## 2. A mecânica (chave desligada por padrão)

- **Python:** `ConfigVinculoSituacao` (`digilab/config.py`, tudo PROPOSTO): `ligada = False`; `limiar_necessidade = 0,5` (o
  limiar do pedido, `ConfigMemoriaEspacos.limiar_necessidade_pedido`); `limiar_energia = 0,25` (a regra de exaustão do
  instinto, `PoliticaInstinto`); noite por `ConfigPadrao.e_noite`. Registro à parte em `protocol.PARAMETROS_VINCULO_B`
  (como `PARAMETROS_CONFIANCA_M1`): a `ConfigVinculo` e os protocolos da personalidade não mudam, e o hash
  `d986ff1b9308…` continua.
- **Ligada:** o pedido não abre (o atendimento sai do vínculo); a coerência agrupa o histórico por **(ação do pet, situação
  do pet)**, com a situação = (necessidade baixa, cansado, noite) lida da **observação com que o pet decidiu a ação atual**
  (`Vinculo.decisao(obs, …)`), não do estado na hora do feedback (desvio pequeno em relação à conta do #109, que lia o
  estado antes da ação do dono: as células mudam pouco em 15 ticks, e assim o motor não precisa de gancho novo); o desejo,
  os ajustes diretos (forçar, bronca sem motivo), a pausa de treino e o teto da sombria ficam como estão.
- **Desligada:** nada muda. Teste: vidas com a config padrão e sem ela saem byte a byte iguais; os testes de reprodução
  da v1 (canônica, V3, confirmatória, gabaritos) seguem.
- **Web:** pets **v10** (`VERSAO_PET = 10` = v9 + vínculo B), `CVB` em `constantes.ts` conferida contra o Python
  (`mapa_constantes.json`); os v1–v9 não mudam (assinaturas e gabaritos). Paridade Python → web por gabarito de chamadas
  (`experiments/exportar_gabarito_vinculo.py` → `web/app/test/gabaritos/vinculo_python.json` →
  `web/app/test/vinculo.test.ts`, tolerância 1e−12), no modo B e no modo de hoje.

## 3. Desenho da run

- **Vidas novas** pelo pipeline do treino (`digilab/treino_vida.simular_vida_treino`, o mesmo de `experiments/run_treino.py`):
  5 braços (atencioso, relapso, aleatório, incoerente, exigente), 14 dias, orçamento igual em todos (cuidado 16/dia +
  sessões-alvo), espécie e temperamento do ovo pela semente (`evolucao.ovo`, `temperamento.sortear`).
- **Pareado por semente:** cada (braço, semente) roda **duas vezes**, com o vínculo de hoje (desligada) e com o vínculo B
  (ligada). A semente fixa o ovo, o ambiente e a rng do dono; as duas vidas divergem só porque o vínculo entra na
  probabilidade de obedecer. A de hoje é o controle "o que seria nas mesmas sementes".
- **Sementes** (reservadas pelo coordenador): **calibração** 3101, 3202, 3303, 3404, 3505, para a fumaça do pipeline e para
  um eventual ajuste dos limiares da situação (hoje não previsto: se houver, fica registrado aqui antes da validação);
  **validação** 5101, 5202, 5303, 5404, 5505, **uma vez**, depois do commit deste plano e do código. Nada se ajusta
  olhando a validação.
- **Script:** `experiments/run_vinculo_novo.py --conjunto calibracao|validacao` → `artifacts_v2_vinculo_novo/<conjunto>/`
  (`resumo.json`, `vidas/<braco>@<semente>[.b].jsonl` e `.treino.json`). Cada vida é rejogada do disco e conferida (série do
  vínculo, estado, treino), como no `run_treino`. Sem GPU.
- **Web:** `web/app/test/medir_vinculo_mega.mjs --versao 10` → `artifacts_v2_vinculo_novo/mega_v10.json`: as mesmas 6 vidas
  de 3 dias (sementes 2001…2006, 16/dia, donos da web) do artefato antigo, agora em pets v10 com as medalhas do Tamer
  liberadas no ovo (`Motor.liberar(6)`: a evolução dos v6+ pede medalhas); Megas por dono com o limiar 0,4 e varredura de
  limiares, só relato. **O limiar não muda.**

## 4. Métricas e gate

Bootstrap sobre sementes com os parâmetros do `PROTOCOLO_ARENA_V1` (`bootstrap_reamostragens`, `bootstrap_semente`,
`nivel_confianca`), `metrics.bootstrap_ic`, como no `run_treino`.

- **Primária (gate PROPOSTO):** vínculo final **atencioso − aleatório** por semente, nas vidas com o vínculo B; média e IC95
  por bootstrap sobre as 5 sementes de validação. **Passa se o limite inferior do IC for > 0.**
- **Secundárias (descritivas, sem gate):**
  - vínculo final por braço, B × hoje, e a mesma diferença atencioso − aleatório nas vidas de hoje (controle pareado);
  - exigente − atencioso em B (o ajuste do forçar deve continuar separando: hoje −0,347 [−0,421; −0,265],
    `artifacts_treino/resumo.json`);
  - obediência (1 − recusas/pedidos) por braço, B × hoje;
  - amostras por componente do vínculo por braço (coerência, desejo, pausa, ajustes), para conferir a mecânica;
  - Megas por dono com o limiar 0,4 nos pets v10 (web), lado a lado com `limiar_vinculo.json`.
- **Conferências que precisam passar:** replays do disco iguais; `engine.py` com o sha congelado; hash do protocolo da
  personalidade intacto; desligada = byte a byte; paridade do gabarito ≤ 1e−12; v1–v9 iguais na web.

## 5. Regras de decisão

- Gate passa: o vínculo B fica implementado (chave desligada no Python, v10 na web) e a pendência do vínculo fecha; o limiar
  do Mega segue 0,4, com o relato do que acontece nos v10.
- Gate falha: relatar com os números; **nenhum ajuste pós-hoc** nos limiares ou pesos; a decisão volta ao Matheus.
- Fora: a alternativa A, mudar o limiar do Mega, a obediência, `engine.py`, as runs e os protocolos da v1.
