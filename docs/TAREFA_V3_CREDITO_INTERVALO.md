# TAREFA V3 — CREDITO_INTERVALO (2026-11-19)

Coordenador: o Gerente da V3. Worker: a definir. Worktree e branch: `v3-credito-intervalo`. Status: ABERTA; nenhuma etapa começada.

Categoria: implementacao. Origem: Matheus, 2026-11-19: "Sim, escreva", a tarefa do R1 (o rastro da cadeia) e do R2 (o crédito do
intervalo com o ELOGIO), pela INT-1 da análise da cadeia ([integracao_cadeia_digibrain.md](futuro/integracao_cadeia_digibrain.md),
#976, na `main`). A pergunta veio do Matheus: como resolver o paladar, o banheiro, o olfato, a digestão instantânea, a saciedade e os
gestos do dono que não entram no cérebro. A resposta (D-CI-1) é que todos dependem destas duas etapas.

## 1. Pergunta

O que acontece no corpo entre duas decisões do DigiBrain modular pode ensinar o pet sem tirá-lo da comida? Hoje não ensina nada. O r é
medido no mesmo tick da ação (`motor_corpo.py:444-447`). O decaimento, o sono, os gestos do dono e uma digestão lenta caem no intervalo
de 15 ticks até a decisão seguinte e não chegam ao aprendizado (análise, seção 1.3). A etapa vem da trilha C (o cérebro) do
`PLANO_V3.md` e é a sequência decidida da INT-1, depois do R0 (o PV-2, registrado como "não levar", D-PV2R-13).

A tarefa tem duas etapas, em ordem:
- **R1, o rastro:** medir o tamanho do que fica fora, sem mudar nenhuma decisão.
- **R2, o crédito:** creditar esse intervalo por um traço curto, na mesma estrutura da janela do ELOGIO (INT-5).

## 2. Depende de

- **Na `main`:** a análise da cadeia (#976), o código do PV-2 (#981, #984) e o resultado dele (#997), e o ELOGIO, com o código (#985) e
  o resultado (`RESULTADO_V3_ELOGIO.md`, "Sim, registre assim", 2026-11-18).
- **As decisões que já valem:** as INT-1 a INT-9 ("Aprovo as INT-1 a INT-9 pela recomendação", Matheus, 2026-11-17, D-INT-9). Delas
  vêm a ordem (INT-1), uma estrutura de traço só (INT-5), a calibração do `tau_c` no fim (INT-6) e a checagem descritiva com a config do
  v38 (INT-8).
- **Para o R2:** o R1 na `main`, com os números do intervalo, e o plano de análise do R2 aprovado pelo Matheus antes de qualquer vida.
- **A conversa com a CORPO** (`TAREFA_V3_CORPO.md`) antes do merge de qualquer código.
  - A C3 dela não mexe na digestão: a chave E ficou fora pela D-C3-3 (`PLANO_ANALISE_V3_CORPO_C3.md`).
  - O que ela muda, tick a tick, é a ponte da falta de combustível. Com a D, a falta sobe a fome em vez do cansaço, e um teto novo
    (`ConfigTetoFomeCorpo`, desligado por padrão) para essa subida.
  - Isso muda o que o corpo faz entre as decisões, no caminho da fome, e é exatamente o que o R2 credita. O R1 e o R2 têm de saber se o
    corpo das vidas tem a C3 ligada ou não, e o plano do R2 diz qual dos dois corpos usa.

## 3. Mudança mínima

**Regras que valem para as duas etapas:**
- uma subchave nova, desligada;
- o gabarito das vidas de hoje num commit próprio, antes da mudança;
- desligada, a vida sai igual byte a byte, e o G1 do replay passa ligado;
- nenhuma rng nova e nenhum evento novo no log: tudo é estado do cérebro, refeito pelo replay;
- inteiros na escala S;
- cada parâmetro no `config.py` com o status e a fonte;
- as medidas no `metrics.py`;
- a web só depois da validação.

**R1, o rastro (só leitura, Python e TS).** A análise, seções 3.6 e 7, linha R1.
- **Arquivos:**
  - `digilab/digibrain/adapt.py`: o `_fechar` e o registro;
  - `digilab/digibrain/afeto.py`: uma função `r_intervalo`, só o cálculo;
  - `digilab/metrics.py`: a fração do corpo que fica fora do r;
  - `web/app/motor/digibrain/leitura.ts` e `adapt.ts`.
- **O campo:** `registro["cadeia"] = {id, r_mesmo_tick, r_intervalo, atualizacoes, pesou}`, atrás da subchave `rastro` da
  `ConfigDigibrain`.
- **O r do intervalo:** `r_int = div_arred(ganho_r · Σ (falta(pc1_k)² − falta(pc0_{k+1})²), S)`, sobre os mesmos receptores do r.
  Ele é medido e registrado por canal, e não é creditado.
- **A medida:** a fração do corpo fora do r, por canal (a fome, a energia, o tédio e os outros), nas vidas da 0b e da C4 por replay.
  Não precisa de vida nova nem de faixa.
- **O que ela responde:** quanto o sono, o decaimento e os gestos do dono pesam no intervalo. Sem esse número não se escolhem o K e o λ
  do R2, e não se sabe se a digestão lenta teria o que ensinar.

**R2, o crédito do intervalo, com o ELOGIO.** A análise, seção 3.3.
- **Arquivos:**
  - `digilab/digibrain/estado.py`: o traço;
  - `digilab/digibrain/plast.py`: o `creditar_traco`;
  - `digilab/digibrain/adapt.py`: o `_fechar`;
  - `digilab/digibrain/afeto.py`: a linha de base.
- **A chave:** `ConfigDigibrain.traco_intervalo`. Os inatos `k_traco` (PROPOSTO = 4), `lambda_traco` (PROPOSTO = S/2), `eta_int`
  (PROPOSTO, menor que o η_h) e `k_base` (PROPOSTO) são todos SEM FONTE até o plano.
- **O que fica elegível:** as últimas K opções, cada uma com o `e = z` dela, o comportamento e a classe consumida.
  - Cada uma nasce com `τ = S` e decai por `τ ← mul(λ, τ)` a cada decisão.
  - Quando a mesma opção volta, o peso volta a S, sem somar.
- **A linha de base:** `b[ctx]`, com `ctx` ∈ {acordado, dormindo}.
  - O crédito é `δ = clamp(div_arred(r_int − b[ctx], R_n), −S, S)`.
  - A atualização é `H[b_i, j] += mul(mul(g_apr, η_int), mul(mul(τ_i, δ), e_ij))`, com o corte em ±H_max.
- **Cada intervalo conta uma vez só:** o par (tick de `pc1_k`, tick de `pc0_{k+1}`) fica registrado, e um teste confere que nenhum par se
  repete. O r do mesmo tick continua indo à opção como hoje, então o imediato e o do intervalo cobrem trechos disjuntos do tempo.
- **A INT-5, uma estrutura de traço só:** a janela W do ELOGIO (`ConfigElogio.janela`, a forma linear S − j·S/W) vira um caso
  particular do traço. O carinho entra pelo corpo, no intervalo, e é creditado pelo mesmo traço.
  - O R2 não cria um segundo mecanismo de crédito no mesmo cérebro.
  - O registro separa os sinais: o r do intervalo e o sinal do carinho.
  - A `ConfigElogio` desligada continua dando o gabarito `tests/gabaritos/elogio_de_hoje.json` byte a byte.
- **A guarda de forrageio (PV-0-10) é obrigatória:** creditar a energia do sono pode reforçar o dormir com a energia baixa e tirar o pet
  da comida. A VALUATION já mostrou que o sono disputa com a fome.

**O que não muda:**
- o `engine.py`;
- os saves e os logs de hoje, e a `VERSAO_PET`, que só muda quando o jogo ligar uma etapa;
- a chave do PV-2, que fica desligada (D-PV2R-13);
- a ELOGIO desligada por padrão;
- o reflexo do sono;
- o `tau_c` (INT-6);
- o corpo: a digestão, a saciedade e os órgãos de dentro ficam como estão (seção 6).

## 4. Experimento e gate (se houver run)

- **O R1 não tem run:** só replay de vidas que já existem, nas sementes delas. Não pede faixa.
- **O R2:**
  - **Plano de análise:** `docs/PLANO_ANALISE_V3_CREDITO_INTERVALO.md`, commitado e aprovado antes da primeira vida.
  - **Sementes reservadas:** a calibração do K e do λ, e a validação, uma vez. As faixas são pedidas ao coordenador quando o plano
    existir.
  - **Métrica e gate (a forma, PROPOSTA; os números saem do plano):**
    - o G principal é a **T4** da análise: com um efeito atrasado e uma ação irrelevante no meio, o H do `comer` cresce mais que o do
      `brincar`, e o placebo do tempo sorteado não dá o mesmo H;
    - junto vai a **T5**: o tapa do dono num horário independente da comida não derruba o H nem o d̂ das comidas;
    - a **guarda de forrageio**: a taxa por episódio de fome (o G-MVP-EP) e a exaustão (o G2 da VALUATION) não pioram além de um corte
      do plano;
    - **a checagem do v38** (INT-8), descritiva, sem gate.
  - **GPU:** não.
  - **A máquina (V3-D8):** uma run de pesquisa por vez e no máximo 4 processos.

## 5. Entrega

- **Testes:** `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos` e `npm run e2e` (o R1 toca a web, no registro).
- **Registro:** uma seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2).
  - **Não edite o índice `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge.
  - Um conflito nele se resolve rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`).
- **O resumo da etapa** vai no corpo do PR e numa seção no fim do documento da frente (o `RESULTADO_V3_*.md` da run ou o
  `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- **Um PR por etapa:** o R1; o gabarito e o código do R2; o plano do R2; a run do R2; o resultado. Cada um vai contra a `main`, com o
  resumo e os números, cada número com o seu artefato.
- **Depois do PR:** aviso ao coordenador. O merge é só do Matheus.
- **O corpo do PR** segue o `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da
  categoria.

## 6. Fora desta tarefa

Fica fora de propósito, e cada item tem dono ou espera esta tarefa (D-CI-1):
- **A digestão lenta** (`taxa_digestao`, `config.py:1554`): só depois do R2 validado. Sem o crédito do intervalo, ligar a digestão lenta
  tira o alívio imediato de comer e põe o pet em privação. A chave E da CORPO (a digestão inteira) é outra coisa, ficou fora da C3
  (D-C3-3) e é da CORPO.
- **A saciedade, o paladar e o banheiro no modular:** o R6 da análise, com uma tarefa de corpo própria.
  - A saciedade é um receptor novo, que integra o que foi comido.
  - O paladar entra no M-SENS por um caminho próprio, como a tela.
  - O banheiro é um drive comum, que precisa de uma unidade de comportamento.
  - Hoje o paladar e o banheiro falham alto no M-SENS, e o ELOGIO parou no paladar (D-EL-9).
- **O olfato:** o PV-2 está registrado como "não levar" e não se religa aqui. O R1 mede o intervalo também nas vidas do PV-2. Se a leitura
  disser algo sobre o "custa perto de casa", ela vira um adendo da PET_VIVO, e não desta tarefa.
- **O R3** (a interrupção), **o R4** (os desfechos com contexto, a aversão e a memória reavaliada) e **o R5** (o sorteio em dois
  estágios), na ordem da INT-1.
- **A vontade do cérebro A no balão:** é da LZ3 da LIMPEZA (INT-7).
- **A calibração do `tau_c` e de qualquer número já decidido:** fica para a calibração no fim.
- **A web do R2:** só depois da validação.

## 7. Critérios de aceitação

- **R1:**
  - o gabarito de hoje num commit próprio, e o `tests/` conferindo que, com o `rastro` desligado, a vida sai igual byte a byte;
  - com o `rastro` ligado, a escolha é idêntica decisão a decisão às vidas sem ele (um teste compara as unidades escolhidas);
  - a paridade do `registro["cadeia"]` no TS, contra um gabarito do Python;
  - a fração do corpo fora do r, por canal, num artefato em disco, com o script que o produz, nas vidas da 0b e da C4.
- **R2:**
  - o gabarito de hoje num commit próprio, e o byte a byte com o `traco_intervalo` desligado;
  - a `ConfigElogio` desligada reproduzindo o `elogio_de_hoje.json`;
  - um teste de que nenhum intervalo é creditado duas vezes;
  - um teste de que a janela do ELOGIO, ligada, sai da estrutura do traço, e não de um caminho paralelo;
  - o plano commitado antes da primeira vida e as faixas na tabela antes da run;
  - o resultado com a T4, a T5, a guarda de forrageio e a checagem do v38, cada número com o seu artefato.

## 8. Precisa do Matheus

- **Abrir o worker do R1.** A recomendação é um Sonnet, porque o R1 é só leitura e tem escopo claro. Custo de errar: baixo, porque o R1
  não muda nenhuma decisão do pet e o byte a byte confere.
- **Depois do R1, o CHECKPOINT do R2:** seguir para o código do R2 com os números do intervalo na mão, ou parar.
  - A recomendação é seguir só se algum canal tiver uma fração relevante fora do r. O corte é PROPOSTO no PR do R1.
  - Custo de errar: seguir sem um canal relevante gasta uma run num crédito sem sinal; parar com um canal relevante deixa o sono, os
    gestos e a digestão sem caminho até o aprendizado.
- **O plano do R2,** com os números da T4, da T5 e da guarda. Os números ficam PROPOSTOS até a aprovação.
