# Pré-registro: o índice dos experimentos com resultado

**O que é:** uma página por onde um terceiro acha, para cada experimento com resultado registrado, o que foi dito **antes** da run e
onde estão o resultado e os artefatos. Tudo aponta para arquivos do repositório. O vault não é preciso. Esta página é um índice, não um
plano novo: o texto que vale é o do plano, no commit citado. Ela não muda nenhuma regra, nenhum número e nenhuma leitura. Criada na
EVIDENCIA A3 (2026-11-16, Claude Code, Opus 5.5); a fonte de cada linha é a [auditoria da A0](AUDITORIA_EVIDENCIA.md) e o plano.

**Como ler cada seção:**
- **Plano:** o link permanente para o plano no commit em que ele entrou, antes da primeira vida, e a seção que vale.
- **Regra de parada:** o que o plano diz sobre rodar uma vez, não repetir e o que acontece se algo falhar. "Não declarada" quer dizer que o
  plano não escreve uma; a frase mais perto vai junto.
- **O que refutaria:** o texto do plano. Quando o plano não o escreve, a linha diz "pela regra de leitura" e deriva só dela.
- **A classe de A6.6** (C1 a C4, AN4 e A1), com δ a margem de cada um:
  - **"≈ 0":** o IC95 do t inteiro dentro de (−δ; +δ);
  - **"> 0":** o limite inferior > 0, e o IC fora de (−δ; +δ);
  - **"< 0":** o limite superior < 0, e o IC fora de (−δ; +δ);
  - **"indeterminado":** qualquer outro caso.

**No PR:** o relato de um experimento cita a seção dele no campo `Pré-registro:` (o `.github/pull_request_template.md`), e o
`tools/verificar_relato.py` reprova se a seção não existir. Um experimento novo ganha aqui uma seção `## PR-<id>` antes da run, com o
link para o plano commitado.

| id | experimento | status | replicado |
|---|---|---|---|
| [PR-C1](#pr-c1--o-longe-regular) | o longe regular | positivo no `longe_fixo`; indeterminado no sorteado | repetição interna, mesma máquina |
| [PR-C2](#pr-c2--o-crédito-na-intenção) | o crédito na intenção | negativo | não |
| [PR-C3](#pr-c3--redecidir-por-evento) | redecidir por evento | indeterminado | não |
| [PR-C4](#pr-c4--a-memória-autobiográfica) | a memória autobiográfica | positivo, com a ressalva do M-MEM | [a réplica da A3](#pr-replicacao-c4--a-réplica-da-c4): divergiu; o `resultado.json` igual byte a byte, o `medidas.json` não (causa provável: os tempos por vida) |
| [PR-AN4](#pr-an4--o-passeio) | o passeio | negativo | não |
| [PR-GVN2](#pr-gvn2--o-gosto-visual-a-leitura) | o gosto visual, a leitura | descritivo | a leitura sai igual byte a byte (teste) |
| [PR-PET-VIVO](#pr-pet-vivo--a-auditoria-da-escolha) | a auditoria da escolha | descritivo, pós hoc | não |
| [PR-COOP-A1](#pr-coop-a1--a-cooperação-com-o-irmão-aleatório) | a cooperação com o irmão aleatório | EMERGE e DOSE não confirmam; CUSTO confirma | não |
| [PR-BASELINE](#pr-baseline--o-modular-contra-a-baseline-trivial) | o modular contra a baseline trivial | negativo ("< 0") | não |
| [PR-ABLACAO](#pr-ablacao--a-ablação-do-aprendizado-no-jogo) | a ablação do aprendizado no jogo | "muda" | não |
| [PR-SOCIAL-PAR-S](#pr-social-par-s--o-substrato-do-social) | o substrato do social (S3) | "nulo com um instrumento que vê" nos três braços | não |
| [PR-SOCIAL-PAR-MD](#pr-social-par-md--a-medida-do-m1-e-do-m2) | a medida do M1 e do M2 | a rodar | não |

## PR-C1 — o longe regular

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, adendo 6](https://github.com/matheusmmmp/digilab/blob/7683c0e1f83a9526421208b4a23d90cd476148ff/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md), commit `7683c0e1f83a9526421208b4a23d90cd476148ff` (2026-10-31 13:10), que é também o código da run (início 14:18:10, árvore limpa) |
| hipótese | M3\* − M2 na taxa por episódio de fome é "> 0" no `longe_fixo` (o primário) e "≈ 0" no `longe` sorteado (descritivo). "A previsão do sorteado não se afrouxa até passar" (A6.1) |
| células | 8: 4 donos × `longe_fixo` e `longe`; braços M0, M2, M3\*; 14 dias, orçamento 16 (A6.2) |
| sementes | 71101…71505, bases 71101, 71202, 71303, 71404 e 71505, K = 30: 150 unidades, 3 600 vidas (A6.3) |
| contraste primário | M3\* − M2 nas 4 células do `longe_fixo`, a média por unidade (base, semente); IC95 pelo t sobre as 150; passa se o limite inferior > 0 (p unilateral ≤ 0,025); sem Holm. Premissas G-PESA e G-ELEGIVEL-EP (A6.4) |
| regra de leitura | a classe de A6.6 com δ = 0,022 (AD6-1, AD6-2); a tabela de A6.7 cruza o fixo e o sorteado para decidir a L-3 |
| regra de parada | "A run roda uma vez", e "a run não se repete"; uma faixa nova só vem com um adendo novo; sem calibração nem piloto (A6.3, A6.7, A6.10) |
| o que refutaria | pela regra de leitura: o primário fora do "> 0" refuta a previsão do fixo; o sorteado "> 0" ou "< 0" refuta o "≈ 0" |
| resultado | [RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, seção 13](RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): +0,0489 [+0,0355; +0,0624], n = 150, "> 0"; o sorteado −0,0106 [−0,0236; +0,0024], "indeterminado" |
| artefatos | [`artifacts_v2_digibrain_prototipo/longe_regular/run/`](../artifacts_v2_digibrain_prototipo/longe_regular/run/): `resultado.json` `b1872745…`, `medidas.json` `5a4fb207…`, `vidas.tar.gz` `a1fb0010…` (commit `9a1fdfcf`) |

## PR-C2 — o crédito na intenção

| campo | valor |
|---|---|
| plano | [o mesmo arquivo, adendo 7](https://github.com/matheusmmmp/digilab/blob/4be65a03bcefa20bb9e51f3e6fae9da5ef0cb210/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md), commit `4be65a03bcefa20bb9e51f3e6fae9da5ef0cb210` (2026-10-31 22:10:47), o código da run (início 22:11:09, árvore limpa) |
| hipótese | P-A: M2c − M2 no índice "ganhou, fica" é "> 0"; S1 (M2c − M1) "> 0"; S2 sem previsão de sinal (A7.1) |
| células | 12: 4 donos × `longe_fixo`, `comedouro` e `longe`; o primário nas 8 do `longe_fixo` e do `comedouro`; braços M1, M2, M2c (A7.2) |
| sementes | 75101…75505, bases 75101, 75202, 75303, 75404 e 75505, K = 30: 150 unidades, 5 400 vidas (A7.3) |
| contraste primário | M2c − M2, a média das 8 células por unidade, IC95 pelo t; passa se o limite inferior > 0; sem Holm. Premissas P-CORRIDA e G-PESA do hábito (A7.4, A7.5) |
| regra de leitura | a classe de A6.6 com δ = 0,011; a tabela de A7.7 em ordem (premissa, P-A × S1, "≈ 0", "< 0", indeterminado) |
| regra de parada | "A run roda uma vez", "a run não se repete"; sem calibração nem piloto (A7.3, A7.7, A7.10) |
| o que refutaria | pela regra de leitura: P-A "≈ 0", "< 0" ou indeterminado; o "≈ 0" lê-se "a unidade de crédito não é a causa" |
| resultado | [o mesmo RESULTADO, seção 14](RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): P-A +0,0028 [−0,0003; +0,0060], n = 150, "≈ 0"; S1 "< 0" |
| artefatos | [`artifacts_v2_digibrain_prototipo/habito_intencao/run/`](../artifacts_v2_digibrain_prototipo/habito_intencao/run/): `resultado.json` `5c7e51a5…`, `medidas.json` `93b136d6…`, `vidas.tar.gz` `261d1fbc…` (commit `6b5d7e3d`) |

## PR-C3 — redecidir por evento

| campo | valor |
|---|---|
| plano | [o mesmo arquivo, adendo 8](https://github.com/matheusmmmp/digilab/blob/d0aff83e6cf9c4f23b8c2783f51a5b455a2e2fe9/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md), commit `d0aff83e6cf9c4f23b8c2783f51a5b455a2e2fe9` (2026-11-01 01:21), o código da run (início 01:45:19, árvore limpa) |
| hipótese | P-R: M3\*R − M3\* na taxa por episódio no `longe_fixo` é "> 0"; a guarda G-COMEDOURO "não '< 0'"; "um nulo é plausível e fica escrito antes" (A8.1) |
| células | 12: `longe_fixo` (o primário), `comedouro` (a guarda) e `longe` (S2), 4 donos cada; braços M3\*, M3\*R, M2, M2R (A8.2) |
| sementes | 76101…76505, bases 76101, 76202, 76303, 76404 e 76505, K = 30: 150 unidades, 7 200 vidas (A8.3) |
| contraste primário | M3\*R − M3\* nas 4 células do `longe_fixo`, IC95 pelo t; passa se o limite inferior > 0; sem Holm; a guarda falha só com "< 0" (A8.4, AD8-5). Premissas P-SEGURA, P-EVENTO e G-ELEGIVEL-EP (A8.5) |
| regra de leitura | a classe de A6.6 com δ = 0,025 (AD8-1); a tabela de A8.7 em ordem |
| regra de parada | "A run roda uma vez", "a run não se repete"; o registro da run é um commit empurrado antes da primeira vida (A8.7, A8.10, A8.13) |
| o que refutaria | pela regra de leitura: P-R "≈ 0", "< 0" ou indeterminado. O plano avisa antes que um efeito de um quarto do da memória (≈ 0,012) também sai "indeterminado" (A8.12) |
| resultado | [o mesmo RESULTADO, seção 15](RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): P-R +0,0124 [−0,0060; +0,0308], n = 150, "indeterminado"; a guarda "indeterminado" (não falha) |
| artefatos | [`artifacts_v2_digibrain_prototipo/redecidir_evento/run/`](../artifacts_v2_digibrain_prototipo/redecidir_evento/run/): `resultado.json` `41869752…`, `medidas.json` `d5b7c974…`, `vidas.tar.gz` `217add77…` (commit `7747485b`) |

## PR-C4 — a memória autobiográfica

| campo | valor |
|---|---|
| plano | [o mesmo arquivo, adendo 9](https://github.com/matheusmmmp/digilab/blob/a287ba20fafdc1fbbf9be7100f89d9c90f466948/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md), commit `a287ba20fafdc1fbbf9be7100f89d9c90f466948` (2026-11-01 18:45:24), o código da run (início 18:45:37, árvore limpa) |
| hipótese | REL − SEM, REL − REC e REL − EMB no `longe_fixo` são "> 0" (o primário, com Holm); a guarda G-COMEDOURO (REL − SEM no `comedouro`) "não '< 0'"; "um nulo no REL − REC é plausível e fica escrito antes"; a direção do REL − REC e do REL − EMB é SEM FONTE (A9.1) |
| células | 12: 4 donos (atencioso, relapso, aleatório, incoerente) × `longe_fixo`, `comedouro` e `longe`; braços REL, SEM, REC, EMB, RELsN e REL+F (A9.2) |
| sementes | 77101…77505, bases 77101, 77202, 77303, 77404 e 77505, K = 40: 200 unidades, 14 400 vidas (A9.3) |
| contraste primário | a família de 3 nas 4 células do `longe_fixo`, a taxa por episódio; o t sobre as unidades e Holm com α = 0,025 na família; cada um passa se o Holm o rejeita. Premissas P-PESA e G-ELEGIVEL-EP (A9.4, A9.5) |
| regra de leitura | a classe de A6.6 com δ = 0,032 (AD9-5); o Holm manda; a tabela de A9.7 em ordem, e "o REL − SEM é a porta" |
| regra de parada | "A run roda uma vez", "a run não se repete"; sem calibração nem piloto; a trava do "APROVADO pelo Matheus" e da faixa reservada (A9.3, A9.7, A9.10) |
| o que refutaria | pela regra de leitura: o REL − SEM "≈ 0", "< 0" ou indeterminado refuta o efeito da memória; o REL − REC ou o REL − EMB fora do "> 0" refuta só a relevância pelo contexto |
| resultado | [o mesmo RESULTADO, seção 16](RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): REL − SEM +0,0646 [+0,0515; +0,0778]; REL − REC +0,0560 [+0,0427; +0,0693]; REL − EMB +0,0636 [+0,0507; +0,0764]; n = 200 cada; o Holm rejeita os três; a guarda +0,1981 [+0,1861; +0,2101], n = 200. Ressalva registrada: o REL inclui o lugar lembrado do M-MEM (a D-C1-3, descritiva) |
| artefatos | [`artifacts_v2_digibrain_prototipo/memoria_autobio/run/`](../artifacts_v2_digibrain_prototipo/memoria_autobio/run/): `resultado.json` `6f8c91d8…`, `medidas.json.gz` `8b48d0a2…` (o conteúdo `869ff397…`, o do meta), `vidas.tar.gz` `aa0c3987…` (commit `1df2e328`) |

## PR-AN4 — o passeio

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_ACOES_NOVAS.md`](https://github.com/matheusmmmp/digilab/blob/d3d993ba0ad3168448c8814e7a66ce3338a5d070/docs/PLANO_ANALISE_V3_ACOES_NOVAS.md), commit `d3d993ba0ad3168448c8814e7a66ce3338a5d070` (2026-11-05 13:19), ancestral do código `cff554fd` (início 15:59:31, árvore limpa); o registro da run na seção 14 |
| hipótese | a guarda G-COMEDOURO-AN (LAB+P − LAB no `comedouro`) "não '< 0'", o único gate; o MOV "> 0", "com um nulo plausível" (seção 1) |
| células | 8: 4 donos × `comedouro` e `longe_fixo`; braços LAB e LAB+P (seção 2) |
| sementes | 78101…78505, bases 78101, 78202, 78303, 78404 e 78505, K = 40: 200 unidades, 3 200 vidas (seção 3) |
| contraste primário | a guarda: LAB+P − LAB na taxa por episódio, nas 4 células do `comedouro`, IC95 pelo t, um contraste só; o MOV: a fração das decisões que saem do lugar, sem limiar. Premissas P-PASSEIO e G-ELEGIVEL-EP (seções 7.1 a 7.3) |
| regra de leitura | a classe de A6.6 com δ = 0,018 (AN3-2); a guarda falha só com "< 0"; a tabela de 7.4 em ordem |
| regra de parada | "A run roda uma vez", "a run não se repete, nada se ajusta olhando para ela"; sem calibração nem piloto (seções 3, 7.4, 11) |
| o que refutaria | o plano, 7.4: a guarda "< 0" desliga a `passeio`; o MOV sem limite inferior > 0 refuta só o MOV, e "não diz que o passeio 'não funciona'" |
| resultado | [RESULTADO_V3_ACOES_NOVAS.md](RESULTADO_V3_ACOES_NOVAS.md): a guarda −0,0263 [−0,0362; −0,0164], n = 200, "< 0", falha; o MOV +0,0236 [+0,0203; +0,0269], n = 200 |
| artefatos | [`artifacts_v3_acoes_novas/run/`](../artifacts_v3_acoes_novas/run/): `resultado.json` `70b7fc96…`, `medidas.json` `9f992e9c…`, `vidas.tar.gz` `3fe40da4…` (commit `a1399c05`) |

## PR-GVN2 — o gosto visual, a leitura

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md`](https://github.com/matheusmmmp/digilab/blob/cb9803321bf0a50ca146a9b9c4618c167bdeeb08/docs/PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md), commit `cb9803321bf0a50ca146a9b9c4618c167bdeeb08` (2026-11-12 16:20:28), ancestral do commit da leitura `5b4c0fa3` (16:49:26); o plano diz que foi empurrado antes de abrir os `.tar.gz` |
| hipótese | **nenhuma própria:** "descritivo, não confirmatório". As frases permitidas dizem só se algo "é / não é o que a H5 (ou a H4) prevê"; as H4 e H5 estão em [`docs/futuro/gosto_visual_porque_negativo.md`](futuro/gosto_visual_porque_negativo.md), seção 2 (seções 1 e 4 do plano) |
| células | nenhuma vida nova: os dois `vidas.tar.gz` (a GV3 e a GV3b), só os `*_sonda.json`, cada run separada, por genoma (próprio e vazio) (seções 1 e 3) |
| sementes | nenhuma faixa nova; o bootstrap com 2 000 reamostras das unidades inteiras, semente 20261112 (seção 3) |
| contraste primário | **nenhum:** as medidas M1 a M4; a principal é a M2, Spearman(Δ_I, `dif_fica`) no próprio, com IC95 percentil (seção 3) |
| regra de leitura | só as 8 frases da seção 4, por run, sem juntar as duas; "um IC95 que não contém 0 não é 'o efeito apareceu'"; sem correção para comparações múltiplas |
| regra de parada | não declarada. A mais perto: "Nenhuma vida nova", e os dois negativos ficam como estão (seção 1); a conferência C0 falha alto (seção 3) |
| o que refutaria | nada: o plano é descritivo e proíbe as palavras "confirmada" e "refutada" |
| resultado | [`gosto_visual_porque_negativo.md`, seção 6](futuro/gosto_visual_porque_negativo.md): Spearman 0,823 [0,694; 0,886] na GV3 e 0,645 [0,485; 0,743] na GV3b; as GV3 e GV3b seguem negativas |
| artefatos | [`artifacts_v3_gosto_visual/gvn2/`](../artifacts_v3_gosto_visual/gvn2/): `leitura.json` `67eb6e8b…`, `leitura.py` `92c0eeaa…`; o teste `tests/test_gosto_visual_gvn2.py` confere que a leitura sai igual byte a byte |

## PR-PET-VIVO — a auditoria da escolha

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_PET_VIVO.md`](https://github.com/matheusmmmp/digilab/blob/545a4a8624ad8b6f3783923f76644db2ebb4d4cd/docs/PLANO_ANALISE_V3_PET_VIVO.md), com o registro da run na seção 11, commit `545a4a8624ad8b6f3783923f76644db2ebb4d4cd` (2026-11-08 10:43), ancestral do branch da run `58c28277` |
| hipótese | as perguntas Q-0b e Q-0c; as HA, HC e HP foram escritas depois de olhar as vidas. "A leitura é descritiva e gera hipótese"; "nenhuma causa fica provada" (seções 1 e 6) |
| células | as vidas da C4 (REL e SEM × 3 lugares) e da AN0, por (fonte, braço, lugar); o contrafactual A-4 numa subamostra fixada antes, k = 0 a 7 de cada base (seções 3 e 8) |
| sementes | nenhuma nova: as da C4 (77101…77505, 4 800 vidas nos braços REL e SEM) e as da AN0; `K_SUBAMOSTRA = 8` (seções 3, 8 e 11) |
| contraste primário | **nenhum:** IC95 da A-4 por (fonte, braço), lido lado a lado, "sem teste entre elas" (seções 3 e 5) |
| regra de leitura | os cortes da seção 5 (PV-0-8, PROPOSTOS e SEM FONTE) para a HA, a HC e a HP; nenhuma aponta: "indeterminado"; duas ou mais: mistura, sem escolher |
| regra de parada | "Roda uma vez. Nada se ajusta olhando o resultado" (seção 10); as três conferências falham alto antes de qualquer medida (seção 2.3); a parede acima de 8 h para a run e avisa o Gerente (seção 11) |
| o que refutaria | nada: é pós hoc. Pela regra de leitura, "indeterminado" quando nenhuma das três atinge o corte |
| resultado | [RESULTADO_V3_PET_VIVO.md](RESULTADO_V3_PET_VIVO.md): a linha "indeterminado" nos 6 grupos da C4 |
| artefatos | [`artifacts_v3_pet_vivo/auditoria/`](../artifacts_v3_pet_vivo/auditoria/): `auditoria.json` `3bb42d95…` (no git, LF), `auditoria_vidas.json.gz` `14a4b75f…` (commit `b3aead22`); não há `meta.json` (a A0, seção 1.7) |

## PR-COOP-A1 — a cooperação com o irmão aleatório

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_COOPERACAO.md`, seção 12 (adendo 1)](https://github.com/matheusmmmp/digilab/blob/c3b930fc9801750d6d21b6c97f93484b52f1d402/docs/PLANO_ANALISE_V3_COOPERACAO.md), aprovado no commit `c3b930fc9801750d6d21b6c97f93484b52f1d402` (2026-11-12 16:19:29); o registro da análise (A1-CB3, N = 80) no `0eb511d4`, em `docs/registro/2026-11.md` (D-CB-22 a D-CB-25) |
| hipótese | A1-EMERGE: com a CO7 no A, o irmão aflito come a comida disputada mais vezes (a P1 do A, B1 − B0); A1-DOSE: o efeito cresce com o `k`; A1-CUSTO: o A não passa mais fome por dever (a P3); a leitura só sobre o mecanismo, nunca sobre os gêmeos (seção 12.2, AD1-2) |
| células | 7 braços (B0, B1, D0, DM, B1E, B1U, B1A), a CO7 só no A, o B sempre o irmão aleatório; o dono atencioso, `comedouro`, 8 dias (seções 12.1 e 12.3) |
| sementes | o piloto 92101…92140; a principal 92201…92280, N = 80, "na ordem e sem pular", 560 vidas; `n_min` = 30; o bootstrap com 10 000 reamostras, semente 91000 (seção 12.5, D-CB-24) |
| contraste primário | a P1 do A, IC95 por bootstrap pareado por semente: a A1-EMERGE passa se o IC de B1 − B0 fica todo acima de δ = 0,10; a A1-DOSE se a inclinação tem IC todo acima de 0 e D0 ≤ D½ ≤ B1; a A1-CUSTO se o IC de B1 − B0 na P3 fica todo abaixo de ε = 0,02; sem correção (seções 3.3, 4 e 12.4) |
| regra de leitura | CONFIRMA, NÃO CONFIRMA (o IC cruza o limiar) ou INCONCLUSIVO POR PREMISSA (menos de 30 vidas com oportunidade); sem classe "≈ 0" (seção 4) |
| regra de parada | não declarada como "roda uma vez". As mais perto: o piloto abaixo de 1 oportunidade por vida volta ao Matheus (deu 12,1, D-CB-22); "depois desse commit, nada da seção 4 muda" (seção 10); "nada da seção 12.2 muda depois daqui" (D-CB-24) |
| o que refutaria | pela regra de leitura: NÃO CONFIRMA em cada uma (o IC cruza δ, 0 ou ε, ou a ordem das médias falha) |
| resultado | [`cooperacao_bancada_resultado.md`, seção 5](futuro/cooperacao_bancada_resultado.md): A1-EMERGE +0,0008 [−0,0014; +0,0039], n = 69, NÃO CONFIRMA; A1-DOSE +0,0008 [−0,0014; +0,0039], n = 69, NÃO CONFIRMA; A1-CUSTO +0,0009 [−0,0012; +0,0034], n = 80, CONFIRMA |
| artefatos | [`artifacts_v3_cooperacao_bancada/`](../artifacts_v3_cooperacao_bancada/): `resultado_ad1.json` `d693f046…`, `manifesto_ad1.json` (commit `98b48241`). As vidas não estão no git: `experiments/runs/cooperacao_bancada/principal_ad1.jsonl`, sha256 `d9c0b5c4…` no manifesto (a decisão de versioná-las segue aberta desde a A0) |

## PR-BASELINE — o modular contra a baseline trivial

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_BASELINE_TRIVIAL.md`](PLANO_ANALISE_V3_BASELINE_TRIVIAL.md): PROPOSTO com o código no commit `25f0a5f33aab56effa69e99620a04b0a2d887473`, APROVADO no `da842240d1607d9097ccfd63e63353a4d923b189` (2026-11-16), antes da calibração (`98dde8b1`) e da validação (`af1a52e5`) |
| hipótese | o modular (o REL da C4) fecha uma fração maior dos episódios de fome no `longe_fixo` do que a baseline de quatro regras: REL − TRIV "> 0"; "a previsão não se afrouxa até passar" (seção 1) |
| células | as 12 da C4 (4 donos × 3 lugares); braços REL e TRIV (seções 2.2 e 2.4) |
| sementes | a calibração de X, Y e Z em 96101…96505 (K = 5, só a baseline, só o `longe_fixo`); a validação em 97101…97505 (K = 40, 200 unidades) (seção 2.3). A 96xxx colide com a LONGE_GEOMETRIA (D-EV-A1-8, aberta) |
| contraste primário | REL − TRIV na taxa por episódio, nas 4 células do `longe_fixo`, a média por unidade, IC95 pelo t (seção 5.1) |
| regra de leitura | a classe de A6.6 com δ = 0,032 (BT-8), na tabela da seção 5.3: "≈ 0" refuta; "> 0" com o inferior ≥ 0,032 confirma; "> 0" com o inferior < 0,032 confirma só no sinal; "< 0" refuta; indeterminado não decide |
| regra de parada | a validação roda uma vez, e nada se ajusta olhando para ela; a calibração só nas sementes dela (seções 4 a 6); um critério que falha para e reporta (seção 7) |
| o que refutaria | o plano, 5.3: um IC95 de REL − TRIV dentro da margem ("≈ 0") ou todo abaixo do 0 ("< 0") |
| resultado | [RESULTADO_V3_BASELINE_TRIVIAL.md](RESULTADO_V3_BASELINE_TRIVIAL.md): REL − TRIV −0,083 [−0,128; −0,038], n = 200, "< 0": a baseline vence. H refutada |
| artefatos | [`artifacts_v3_baseline_trivial/validacao/`](../artifacts_v3_baseline_trivial/validacao/): `resultado.json` `706a687a…`, `medidas.json` `cdaa5170…`, `vidas.tar.gz` `7e0a7028…`; a calibração em [`artifacts_v3_baseline_trivial/calibracao/`](../artifacts_v3_baseline_trivial/calibracao/) |

## PR-ABLACAO — a ablação do aprendizado no jogo

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md`](PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md): PROPOSTO sozinho no commit `2481e33e30e6a13e1e5490905dde89cbb3746e19`, APROVADO com o código no `ecbe03206fce669365bee18ba2b7949000708c99` (2026-11-16), o `git_head` da run (árvore limpa) |
| hipótese | com o P1 e o P2 ligados (o braço A), a distribuição das ações e a do motivo diferem das do mesmo pet com o aprendido zerado a cada decisão (o braço B); o sinal de cada categoria é SEM FONTE (seção 1) |
| células | o ovo v38 do jogo, no motor TS no Node; 3 donos sintéticos (atencioso, relapso, incoerente), 3 dias, sem luta; braços A e B, o mesmo código (seção 2) |
| sementes | 98101…98300 (200 unidades) da faixa 98101…98505; 1 200 vidas (seção 2.3) |
| contraste primário | 15 medidas (7 de ação, 8 de motivo), A − B por unidade, IC95 pelo t (gl 199), p bilateral, Holm sobre a família de 15, α = 0,05 (seção 5.1) |
| regra de leitura | seção 5.3: "muda" se ao menos uma passa no Holm; "nula" se o IC95 de todas inclui o 0; "indeterminado" no resto |
| regra de parada | roda uma vez, com um comando; o orquestrador se recusa a gravar por cima (seção 6); um critério que falha para e reporta (seção 7) |
| o que refutaria | o plano, 5.3: as distribuições iguais, com o IC95 de toda diferença A − B incluindo o 0 ("nula") |
| resultado | [RESULTADO_V3_ABLACAO_APRENDIZADO.md](RESULTADO_V3_ABLACAO_APRENDIZADO.md): "muda", 9 das 15 no Holm; todas com \|A − B\| abaixo de 0,01; a distância de variação total das ações 0,0084 (descritivo), n = 200 |
| artefatos | [`artifacts_v3_ablacao_aprendizado/run/`](../artifacts_v3_ablacao_aprendizado/run/): `resultado.json` `ced7c793…`, `medidas.json` `f2adac98…` |

## PR-REPLICACAO-C4 — a réplica da C4

| campo | valor |
|---|---|
| o que é | não é um experimento novo: a C4 refeita do zero a partir do snapshot do código, para conferir que os artefatos versionados saem iguais |
| critério, escrito antes de rodar | o `docs/registro/2026-11.md`, D-EV-A3-2, no commit `9d9e8996` (2026-11-16), empurrado antes de a réplica começar: "confirmou byte a byte" se o sha256 do `resultado.json` da réplica for o do blob versionado (`6f8c91d8…`) e o do `medidas.json` for o do conteúdo do `medidas.json.gz` versionado (`869ff397…`); qualquer outra saída é "divergiu", reportada com os dois sha256, o ambiente e a causa. O `vidas.tar.gz` não entra (foi feito fora do orquestrador) |
| comando | `python tools/replicar_run.py c4 a287ba20fafdc1fbbf9be7100f89d9c90f466948 --relatorio artifacts_v3_evidencia_a3/replica_c4.json` |
| resultado | a seção "A réplica da C4" abaixo |

## PR-PET-VIVO-RA — a linha de base do intervalo (replay)

**Esta seção entrou depois do replay** (D-RB-13): o plano estava commitado e APROVADO antes, mas a seção do índice só foi escrita com
o resultado. O texto que vale é o do plano, no commit citado.

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_PET_VIVO_RA.md`](https://github.com/matheusmmmp/digilab/blob/4492a0f6070911602a8848043f8ad7c0f298643a/docs/PLANO_ANALISE_V3_PET_VIVO_RA.md), commit `4492a0f6070911602a8848043f8ad7c0f298643a` (2026-11-19 18:38, o APROVADO), ancestral do commit do replay `1688bca9` (2026-11-19 21:18) |
| hipótese | as perguntas Q-SONO e Q-ALÉM; H-MÓVEL (a média móvel curta apaga o sono, a longa o preserva), H-ESTADO (o resto do ocioso encolhe com o estado do corpo) e H-ALÉM (o η² do acordado abaixo de 0,05 em toda linha de base). "O desfecho esperado é 'só o sono'" (seção 1) |
| células | as mesmas 5 120 vidas do R1, rejogadas: o HOJE e o OLF-0 da run do PV-2 (3 lugares, n 200) e o HOJE da checagem do v38 (2 lugares, n 40); 7 linhas de base (GLOBAL, CTX, FASE, ESTADO, MÓVEL com k 4, 16 e 96) (seções 3 e 4) |
| sementes | nenhuma nova e nenhuma faixa nova: as da run do PV-2 (bases 26101…26505, k 40) (seção 3) |
| contraste primário | **nenhum:** "nenhuma medida é gate"; o IC95 por lugar contra os cortes da regra (seção 6) |
| regra de leitura | L-SONO, por linha de base: o limite de baixo do resto do dormir > 0 nos 3 lugares, "preserva o sono"; o de cima ≤ 0 em algum, "apaga". L-ALÉM: o limite de baixo do η² do acordado > 0,05 em 2 lugares na ESTADO, "há o que creditar além do sono"; o de cima < 0,05 nos 3 lugares na GLOBAL, FASE, ESTADO e MÓVEL, "só o sono"; senão "indeterminado". O corte de 0,05 é SEM FONTE (seção 6) |
| regra de parada | roda uma vez; as conferências (C-FONTE, C-G1, C-FECHO, C-UMA-VEZ, C-IGUAL-R1) falham alto antes de qualquer medida; com a projeção da fumaça acima de 2 h o replay não roda e o plano volta ao Matheus (seções 3 e 8) |
| o que refutaria | pela regra de leitura: "há o que creditar além do sono" ou "indeterminado" na L-ALÉM contrariam o desfecho esperado; "apaga o sono" numa candidata a tira do R2 |
| resultado | [RESULTADO_V3_PET_VIVO_RA.md](RESULTADO_V3_PET_VIVO_RA.md): L-SONO "preserva o sono" nas cinco candidatas; L-ALÉM "só o sono"; a H-MÓVEL não se confirma |
| artefatos | [`artifacts_v3_pet_vivo/ra/run/`](../artifacts_v3_pet_vivo/ra/run/): `meta.json`, `resultado.json` `4c645a0a…`, `medidas.json.gz` `605d64c0…` |

## PR-SOCIAL-PAR-S — o substrato do social

**Esta seção entrou depois da run** (a regra do D-RB-13 chegou à `main` depois dela): o plano estava commitado e APROVADO antes. O texto
que vale é o do plano, no commit citado.

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_SOCIAL_PAR_S.md`](https://github.com/matheusmmmp/digilab/blob/4e54244e15223ec10c716968be4ea4bfcbe062b7/docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md), commit `4e54244e15223ec10c716968be4ea4bfcbe062b7` (2026-11-18 17:43, com o adendo 1 APROVADO), ancestral do commit da run `e9f4368e` (2026-11-19 00:52) |
| hipótese | as previsões PROPOSTAS da seção 7: no B1, o G-DET passa e o D_A dos pets de hoje dá ≈ 0; no C, o G-DET passa por pouco ou falha; no B2, a PB-1 passa ou fica perto. "Nada disso muda a leitura" |
| células | 3 braços (C, B1 fora da casa, B2 a bola perto) × 1 dono (atencioso) × 1 lugar (comedouro); cinco vidas por par (base, base-OUTRA, VIVO, GRAV, OUTRA); d0 = 5 (adendo 1) (seções 2, 4 e 11) |
| sementes | 103001…103200 (200 bases, k = 1, prefixo `social_par_s`) e o G-DET em 103301…103350 (`social_par_s_det`): 750 pares (seção 4) |
| contraste primário | D_A = T\*c_VIVO − T\*c_GRAV (o tempo até o contato), IC95 pelo t sobre as bases, δ_A = 4 (SEM FONTE); o G-DET com o `SeguidorPuro` no lugar de P, que passa com o IC todo abaixo de −δ_A (seções 3, 5 e 6) |
| regra de leitura | a tabela da seção 7, em ordem: o G-DET falha, "o substrato não deixa ver"; passa e D_A ≈ 0, "nulo com um instrumento que vê"; passa e fora de ±δ_A, "o social aparece"; indeterminado, registrado como está. O conjunto decide pelo B1 |
| regra de parada | não declarada no plano; a mais perto: os gates do código (seção 8), e o orquestrador para no primeiro par em que o G-INSTR ou o G1 falha |
| o que refutaria | pela regra de leitura: o G-DET falhando no B1, ou o D_A do B1 fora do ≈ 0, contrariam a previsão do B1 |
| resultado | [RESULTADO_V3_SOCIAL_PAR_S.md](RESULTADO_V3_SOCIAL_PAR_S.md): o G-DET passa nos três braços; o D_A ≈ 0 nos três (B1 −0,815 [−1,775; +0,145], n = 200); "nulo com um instrumento que vê"; o B inconclusivo por premissa nos três |
| artefatos | [`artifacts_v3_social_par_s/run/`](../artifacts_v3_social_par_s/run/): `meta.json`, `resultado.json` `9c74ebc2…`, `medidas.json` `5fa7767d…`, os 750 pares em `vidas/` |

## PR-SOCIAL-PAR-MD — a medida do M1 e do M2

**Esta seção entrou antes da run** (D-RB-13).

| campo | valor |
|---|---|
| plano | [`PLANO_ANALISE_V3_SOCIAL_PAR_MD.md`](https://github.com/matheusmmmp/digilab/blob/523089d60ee7ee96f4e7c5ce9825c5d6d2f2acdc/docs/PLANO_ANALISE_V3_SOCIAL_PAR_MD.md), commit `523089d60ee7ee96f4e7c5ce9825c5d6d2f2acdc` (2026-11-19 18:35, o APROVADO, "Aprovado"); o código da medida aprovado em 2026-11-20 (#1034) |
| hipótese | as previsões PROPOSTAS da seção 7: o M1 e o M1-inc0 dão D_A ≈ 0 no C e no B1 (no B1, o M1 pode sair de ≈ 0 pelo `onde_comeu`); o M1+M2 passa a PM-1 e dá D_A < 0 no B1, com o C-APR < 0; o M1-inc0+M2 dá ≈ 0. "Nada disso muda a leitura" |
| células | 8: 4 mecanismos (M1, M1-inc0, M1+M2, M1-inc0+M2) × 2 substratos (B1, o principal, e C); o instrumento da S3 sem mudança; o G-DET em cada célula (seções 2 e 3) |
| sementes | 105001…105200 (200 bases, k = 1, prefixo `social_par_md`, as mesmas nas oito células) e o G-DET em 105301…105350 (`social_par_md_det`) (seção 4) |
| contraste primário | o D_A de cada célula, como na S3 (δ_A = 4, SEM FONTE); a atribuição pelos contrastes pareados C-APR = D_A(M1+M2) − D_A(M1-inc0+M2) e C-APR1 = D_A(M1) − D_A(M1-inc0); a premissa PM-1 nos braços com o M2 (o limiar de 50 % SEM FONTE) (seções 5 a 7) |
| regra de leitura | a tabela da seção 7, em ordem: o G-DET falha, "o substrato não deixa ver"; a PM-1 falha e ≈ 0, "inconclusivo por premissa"; ≈ 0, "nulo com um instrumento que vê"; fora de ±δ_A, "o parceiro responde"; indeterminado, registrado como está. A atribuição e o conjunto pelo B1 |
| regra de parada | não declarada no plano; a mais perto: o código (MD1) e a run (MD2) em PRs separados (MD-8), e o orquestrador para no primeiro par em que o G-INSTR ou o G1 falha |
| o que refutaria | pela regra de leitura: no B1, o M1+M2 em "nulo com um instrumento que vê", ou o C-APR ≈ 0, contrariam a previsão |
| resultado | a rodar |
| artefatos | a rodar (`artifacts_v3_social_par_md/run/`) |

## Como replicar uma run (`tools/replicar_run.py`)

```bash
python tools/replicar_run.py --listar
python tools/replicar_run.py c4 a287ba20fafdc1fbbf9be7100f89d9c90f466948 --relatorio replica_c4.json
```

1. A ferramenta lê o `meta.json` versionado da run (na HEAD, ou na ref de `--artefatos`) e falha alto se o `git_head` gravado não for o SHA
   dado, ou se a run não foi gravada com a árvore limpa.
2. Cria uma worktree destacada no SHA, ao lado do repositório (`../v3-replica-<run>-<sha8>`), sem tocar na árvore de trabalho.
3. Roda o comando do `meta.json`, com o mesmo Python desta execução e `--saida` numa pasta nova da worktree. Quando o meta não gravou o
   comando (a C4), usa o do plano, que fica na tabela `RUNS` da ferramenta com a fonte.
4. Compara o sha256 de cada artefato da réplica com o do blob versionado; um `.gz` versionado é descomprimido antes, porque o cabeçalho do
   gzip leva a data.
5. Grava o relatório JSON (o comando, as versões do Python, do Node, do git e do SO, a parede e cada comparação), apaga a worktree (a menos
   que `--manter`) e sai com 0 se tudo saiu igual, 1 se algo divergiu.

As runs na tabela hoje: `c4`, `a1_validacao` e `a2`. Uma run nova entra com a pasta dos artefatos e, se o meta não gravar o comando, o
comando com a fonte. A ferramenta não conserta nada: uma divergência é reportada como está. `--so-comparar <pasta>` refaz só a comparação
de uma réplica já rodada. O teste é o `tests/test_replicar_run.py`.

**O custo da C4:** 14 400 vidas com 4 processos, cerca de 3,2 h de parede na máquina do projeto (a run original: 11 609 s).

## A réplica da C4

**Resultado: divergiu** (pelo critério D-EV-A3-2, escrito antes). A causa provável está abaixo e não foi provada; o Matheus decidiu
registrá-la como provável, sem nova réplica (2026-11-17, "Registre como provável").

- **O comando:** `PYTHONIOENCODING=utf-8 python tools/replicar_run.py c4 a287ba20fafdc1fbbf9be7100f89d9c90f466948 --relatorio replica_c4.json`,
  de 2026-11-16T20:40:14 a 2026-11-17T00:47:21, 14 826 s de parede, 4 processos. O orquestrador saiu com 0; a ferramenta saiu com 1.
- **O ambiente:** Python 3.13.0 (o mesmo da run original), Node v24.19.0, git 2.45.1.windows.1, Windows-11-10.0.26300-SP0.
- **A saída:** o relatório inteiro em
  [`artifacts_v3_evidencia_a3/replica_c4.json`](../artifacts_v3_evidencia_a3/replica_c4.json), e o que a ferramenta imprimiu em
  [`replica_c4_saida.txt`](../artifacts_v3_evidencia_a3/replica_c4_saida.txt).

| artefato | sha256 versionado (conteúdo) | sha256 da réplica | bytes versionado → réplica | igual |
|---|---|---|---|---|
| `resultado.json` | `6f8c91d8e2b8…` | `6f8c91d8e2b8…` | 290 719 → 290 719 | **sim** |
| `medidas.json` | `869ff3971b91…` | `479fecf097c2…` | 138 153 669 → 138 151 421 | **não** |

- **A causa provável:** o orquestrador da C4 grava em cada vida o tempo de CPU e de relógio dela
  (`"custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}`, `experiments/run_v2_memoria_autobio.py:298`
  e `:312` no `a287ba20`). Esses dois campos aparecem 14 400 vezes cada no `medidas.json` versionado (um por vida) e mudam a cada execução.
  São os únicos campos do `medidas.json` que vêm do relógio: os outros usos de `time` no orquestrador (`:554-581`) vão para o `meta.json`.
  A diferença de tamanho (−2 248 bytes em 138 MB) é do tamanho que a troca de 28 800 números de ponto flutuante dá.
- **O que apoia:** o `resultado.json`, que sai das medidas pela análise, saiu idêntico byte a byte. A análise não lê o `custo`.
- **A lacuna:** a ferramenta apagou a worktree da réplica no fim (sem `--manter`), e o `medidas.json` da réplica se perdeu. Por isso não
  dá para mostrar que, tirando o `custo`, os dois `medidas.json` são iguais; outra fonte de não determinismo nas medidas não está
  excluída. **Para fechar:** rodar de novo com `--manter` (cerca de 4 h) e comparar os dois `medidas.json` sem a chave `custo`.
- **O que isto autoriza dizer:** o resultado da C4 (o `resultado.json`) se reproduz byte a byte a partir do snapshot do código. Não
  autoriza dizer que a run inteira se reproduz byte a byte.
- **Para runs novas:** um campo de relógio dentro do artefato comparado faz toda réplica "divergir". Isto é um achado, não uma mudança:
  o orquestrador da C4 não muda.
