# PLANO DE ANÁLISE V3 — GOSTO_VISUAL, adendo 2 (GV3b): a GV3b de novo, com uma regra para as duas TVs sem lugar (2026-11-12, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-12, nesta forma: "Adendo e faixa nova".** Ele escolheu a opção (b) depois da falha da run do
adendo 1 (D-GV-GV3B-12): um adendo novo com uma regra para o caso que falhou, uma faixa nova e uma run nova. O texto foi escrito depois
da resposta. As escolhas que ele teve de fazer (a regra, o teto e o processo; as GV3B2-1 a GV3B2-7, seção 9) vão ao Matheus no PR, cada
uma com a recomendação e o custo de errar; se ele discordar de alguma, o adendo muda antes da primeira vida. Os números seguem PROPOSTOS
e SEM FONTE.
**Nenhuma vida da faixa roda antes de quatro coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus" (o orquestrador confere; feito);
2. a faixa 91101…91505 em `experiments/bancada/faixas.py` (feito, confirmada pelo coordenador, 2026-11-12);
3. este adendo, as configs novas e o código na `main` (o hook H10 e o `tools/pre_run.py` conferem o adendo no `origin/main`);
4. o registro da run (seção 8) num commit empurrado antes da primeira vida.

**Este adendo vale sobre o adendo 1** (`docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1.md`, as GV3B-1 a 8 DECIDIDAS, D-GV-GV3B-11), **que vale
sobre o plano** (`docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md`). Ele não muda o texto de nenhum dos dois. Onde este adendo não diz nada, vale o
adendo 1, e onde o adendo 1 não diz nada, vale o plano. O orquestrador confere as três marcas.

**O que este adendo não afirma:** que o pet "gosta", "enjoa" ou sente tédio; são nomes de mecanismo e de medida. **Nenhuma alegação de
novidade.** Nenhuma referência nova.

## 0. O que muda e o que fica fixo, antes de qualquer vida

| o quê | no adendo 2 | de onde |
|---|---|---|
| **as duas TVs sem lugar** | **a réplica fica sem sonda e é contada**, com um teto de 5 % (seção 2) | GV3B2-1, GV3B2-2 |
| **o processo** | **a pasta do piloto é commitada antes da run**, e o orquestrador recusa a run sem ela, com o git sujo ou com o piloto reprovado (seção 7) | GV3B2-4 |
| **a faixa** | **nova**: 91101…91505 (o piloto 91101 e 91202, a run 91303, 91404 e 91505); a 90101…90505 vai para `FAIXAS_QUEIMADAS` | seção 6; GV3B2-5 |
| as pastas | `piloto_enjoo2` e `gosto_visual_enjoo2`; a fase `gosto_visual_enjoo2` | GV3B2-6 |
| o enjoo | o mesmo: a `CONFIG_ENJOO_TELA_LIGADA` no corpo e no cérebro, sem mudar número | adendo 1, seção 0; GV3B-2 |
| o desenho, a vida, a familiarização | os mesmos: 2 genomas × 3 donos, 14 dias, os dias 0 a 6, o critério 0,05 | adendo 1, seção 0 |
| a sonda | a mesma: os dias 7 a 13, as 10 h, 3 réplicas, 240 ticks, as duas TVs a 3 células, em direções opostas, 16 direções tentadas | adendo 1, seção 0; D-GV-P1e-3 |
| os perfis A e B | os mesmos: A = C/5, B = 4C/5 | adendo 1, seção 3; GV3B-3 |
| as medidas e a análise | as mesmas: a escolha, o tempo relativo, o tempo total, Δ_I, Δ_agora; a função `analisar` sem mudança; 2000 reamostras | adendo 1, seção 0 |
| a regra da GVP-7 | a mesma: no piloto, a fração das réplicas com uma olhada ≥ 0,25, sobre as réplicas com sonda | adendo 1, seção 6 |
| as expectativas | as mesmas: E1, E2, E3, E3b e E4 | adendo 1, seção 4 |
| o tamanho | o mesmo: o piloto 2 bases × K = 2 (24 vidas), a run 3 bases × K = 12 (216 vidas) | adendo 1, seção 6 |
| a derivação das unidades | a mesma regra (`gosto-visual`, …); com as bases novas, unidades novas | GV3B-6 |

## 1. De onde vem: a falha da run do adendo 1

A run do adendo 1 (90303…90505) parou na vida 213 de 216, com o erro alto da D-GV-P1e-3: as duas TVs, a 3 células do pet em (25, 478),
não couberam em nenhuma das 16 direções (D-GV-GV3B-12). O plano não tinha regra para esse caso: a D-GV-P1e-3 escolheu falhar alto, e na
GV3 o caso nunca aconteceu. Um segundo problema: o `meta.json` da run gravou `git_limpo: false`, porque a pasta do piloto ficou fora do
git. **Nenhum número da run parcial foi lido**, nem para escrever este adendo: a regra da seção 2 foi decidida sem abrir as vidas dela.

## 2. A regra nova: a réplica sem lugar fica sem sonda (GV3B2-1) e é contada contra um teto (GV3B2-2)

**A regra.** Quando as duas TVs não cabem (as 16 direções tentadas, como antes), a réplica fica **sem sonda**: a cópia não anda, e a
sonda grava só o registro do caso (a réplica, o lugar do pet e a direção sorteada). A réplica sem sonda não entra nas medidas (não é uma
réplica "sem olhada": é uma réplica que não houve). As réplicas que cabem saem iguais, byte a byte, às da regra antiga; o teste confere.
A vida segue, e as outras réplicas e os outros dias da mesma vida também.

**A contagem.** O `analise.json` grava, no total e em cada uma das seis células genoma × dono, as réplicas tentadas, as sem lugar e a
fração (sem lugar sobre tentadas), e cada vida lista as dela (`replicas_sem_lugar`, com o dia). A leitura relata a contagem sempre,
mesmo quando for 0.

**O teto: 5 % (PROPOSTO, SEM FONTE),** no total e em cada célula. O motivo: as medidas lidas (a escolha e o tempo relativo) ficam entre 0
e 1, então uma fração f de réplicas ausentes só pode mover a média de uma célula em até f, no pior caso (todas as ausentes no extremo
oposto). Com f ≤ 0,05, o desvio possível fica na ordem da tolerância da familiarização (0,05), já aceita pelo plano. O teto vale assim:
- **no piloto:** passar do teto (no total ou numa célula) segura a run, como a GVP-7 (`conferencia.a_run_pode_rodar` fica falso); o piloto
  é registrado como está e o caso volta ao Matheus com um adendo novo. **Nada se ajusta olhando para ele;**
- **na run:** passar do teto não para nada; a leitura escreve, junto de cada frase da seção 5 que toca a célula, "com N de M réplicas sem
  sonda nesta célula, acima do teto de 5 %", e não escreve nenhuma frase sem essa ressalva.

**As alternativas, com o custo de errar** (registradas, não escolhidas):

| opção | o que faz | o custo de errar |
|---|---|---|
| **(ii) sem sonda, contada (a escolhida)** | a réplica sem lugar não entra; a contagem e o teto vão na leitura | a falta pode não ser ao acaso: o lugar do pet depende do caminho, que depende do genoma e do dono. Uma célula com mais faltas fica com menos réplicas e pode ficar enviesada. O teto limita o viés possível a 0,05 nas medidas entre 0 e 1, e a contagem por célula mostra se a falta se concentrou. Não muda a medida das réplicas que cabem. |
| (i) as distâncias seguintes (3, depois 4, depois 2…) | mais réplicas com sonda | a distância é parte do estímulo (a proximidade da linha de objeto, o raio da visão): as réplicas medidas a 4 ou a 2 células seriam de uma sonda diferente, misturadas às de 3 sem como separar o efeito. E pode ainda não caber. |
| (iii) mover o pet de lugar na cópia | mais réplicas com sonda | a cópia deixa de ser o pet no momento da vida: o lugar, o que está perto (a água, a comida, a TV da vida) e o caminho mudam, e a regra de para onde mover seria um número novo, escolhido agora, sem fonte. A medida dessas réplicas é de outro pet. |

A (ii) é a mais simples (nada muda nas réplicas que cabem, e o caso é só contado) e a única que não põe uma sonda diferente dentro das
medidas. O preço dela é a perda de réplicas, que o teto e a contagem tornam visível.

## 3. Os artefatos da falha (registro, não resultado; GV3B2-3)

O piloto do adendo 1 (`artifacts_v3_gosto_visual/piloto_enjoo/`) e a run parcial (`artifacts_v3_gosto_visual/gosto_visual_enjoo/`) ficam
no git como registro da falha, no padrão da GV3 (o `vidas.tar.gz` no lugar da pasta `vidas/`), cada pasta com um `LEIA.md`:
- o piloto inteiro: `meta.json`, `medidas.json`, `analise.json`, `custo.json` e o `vidas.tar.gz` (24 vidas e 24 sondas);
- a run parcial: o `meta.json` como ficou (sem `fim`, com `git_limpo: false`) e o `vidas.tar.gz` (213 vidas e 212 sondas). Não há
  `medidas.json`, `analise.json` nem `custo.json`.

**Nada disso é resultado, e nada disso é lido como resultado:** nem as medidas do piloto, nem as vidas da run parcial. O piloto só serviu à
GVP-7 do adendo 1 (D-GV-GV3B-12). As vidas da run parcial não são abertas para medir nada, nem para calibrar o teto, nem para comparar com a
run do adendo 2.

## 4. O resto, como no adendo 1

O enjoo ligado (a `CONFIG_ENJOO_TELA_LIGADA` inteira), os perfis A e B, as medidas, a análise, a GVP-7, as expectativas E1 a E4 (com a E3b)
e a comparação só lado a lado com a GV3 (adendo 1, seções 2 a 7) valem sem mudança. A comparação lado a lado é com a GV3 original; a run
parcial do adendo 1 não entra nela.

## 5. As frases que a leitura pode escrever

As mesmas da seção 5 do adendo 1, sem mudança, mais uma regra: uma célula acima do teto da seção 2 leva a ressalva em toda frase que a
toca. Cada IC95 é o da run do adendo 2, com as réplicas que tiveram sonda.

## 6. As sementes, o tamanho e a máquina

- **A faixa:** 91101…91505, em `FAIXAS_RESERVADAS` (confirmada pelo coordenador, 2026-11-12), no molde da 89xxx e da 90xxx. Ela não cruza
  as reservadas nem as queimadas (o `tests/test_gosto_visual_gv3b2.py` confere), e as unidades dela não colidem com as da GV3 nem com as
  do adendo 1.
  - **91101…91202, o piloto:** as bases 91101 e 91202, K = 2 (4 unidades, 24 vidas). Só mede o custo, confere que o pet olha (a GVP-7) e
    conta as réplicas sem lugar contra o teto. Se uma das duas conferências falhar, a run não roda, e o caso volta ao Matheus.
  - **91303…91505, a run:** as bases 91303, 91404 e 91505, K = 12 (36 unidades, 216 vidas), **uma vez**.
- **A faixa 90101…90505 vai para `FAIXAS_QUEIMADAS`** (o coordenador concordou, 2026-11-12), com o motivo: a run do adendo 1 parou na vida
  213 por um erro do código (D-GV-GV3B-12). Ela continua reservada, com a marca QUEIMADA, e as configs do adendo 1 passam a ser recusadas
  pela trava. O piloto 90101…90202 entra junto: ele foi rodado e não volta.
- **A 92101…92505 não é desta frente** (está PROPOSTA no #884, de outra frente).
- **O custo** (PROPOSTO, SEM FONTE): o do adendo 1; o piloto mede.
- **A máquina (V3-D8):** no máximo 4 processos e uma run de pesquisa por vez.
- **A calibração separada da validação:** não se aplica: nada é calibrado.

## 7. O processo: o piloto no git antes da run (GV3B2-4)

1. O piloto roda numa pasta nova, `artifacts_v3_gosto_visual/piloto_enjoo2/`.
2. **Antes da run, a pasta do piloto é commitada** (os quatro JSON e o `vidas.tar.gz`, no padrão do `.gitignore` da GV3), num commit que
   só a traz, e esse commit vai com push.
3. A run só começa com o git limpo. **O orquestrador confere** (antes de criar a pasta da run e antes de qualquer vida): os cinco arquivos
   do piloto estão no git, o `git status --porcelain` está vazio e o `analise.json` do piloto diz `conferencia.a_run_pode_rodar: true`.
   Senão, ele falha alto. Assim, o `git_limpo` do `meta.json` da run sai verdadeiro.
4. Depois da run, a pasta dela é commitada do mesmo jeito.

## 8. O registro da run

Escrito em 2026-11-12, antes de qualquer vida da faixa, no branch `v3-gosto-visual-gv3b-resultado` (o branch do registro da falha,
D-GV-GV3B-12). Este registro é completado num commit próprio por cima do commit do código, que só muda documentos.
- **O ok do Matheus:** 2026-11-12, nesta sessão: "Adendo e faixa nova" (D-GV-GV3B2-1 no registro).
- **O commit do código:** `0f0c2019` (a sonda, a exceção, o orquestrador, a faixa, as configs, os testes e este adendo, com os campos
  deste registro ainda vazios). Depois dele veio o merge da `origin/main` (`7614ebb7`), que não mudou nenhum dos arquivos abaixo. Antes do
  piloto, quem roda confere que os sha256 abaixo são os da `main`; se um merge mudar algum, a diferença é registrada antes da primeira
  vida, e o `meta.json` de cada pasta grava o `git_head` e os sha256 de novo.
- **Os sha256** (o conteúdo no commit do código):
  - o orquestrador `experiments/run_v3_gosto_visual.py`: `00291ed9e35689a873ef21c0b4e498c0b12aa9578e82ec1acc123c5bd1e07253`;
  - a sonda `experiments/sonda_duas_tvs.py`: `45b012ae22f0fcffae85f3f6303f75e0f65759e3a188afd369148935f26e7cd2`;
  - o `digilab/mundo.py` (o `ligar_duas_tvs` com a exceção): `a656fd5d291ae0b035449a5e5c84c7427fdf7fc64610cb6b3a236a0f97a7023e`;
  - o `digilab/tv.py` (a `DuasTVsSemLugar`): `0e9f2041f634c461c54512cee385d6e1bfef11270f60e3d8c7d6972c164613ec`;
  - o `digilab/metrics.py` (sem mudança desde o adendo 1): `7d6eed8b6f4134bde4b37f367fef1d256fdc9b73b8cfcd9c834c544d2b0d94fd`;
  - o `digilab/config.py`: `74bbe7fafd278f7f8e389d99180d07ceaaae01573fdec6fcace7427cd42049c9` (mudou desde o adendo 1 pelos merges da
    `main` de outras frentes; este adendo não o toca, e a `ConfigEnjooTela` e a `ConfigDuasTVs` são as mesmas: o `meta.json` grava a
    config do enjoo inteira);
  - o `digilab/corpo.py` (sem mudança desde o adendo 1): `ed198a4a664f4d451b88d63ef625fe63006a9996869bbd4b33ddf1ef4c5e256f`;
  - a config do piloto `experiments/configs/v3_gosto_visual/piloto_enjoo2.json`:
    `4e9710e9315a98a0967dd5e4733b1a07ca4947d5191a203e3c7c708d613485c8`;
  - a config da run `experiments/configs/v3_gosto_visual/gosto_visual_enjoo2.json`:
    `b62fbd0d73785b8d8a9b589b735b57a83aff6415b663552f8df07ef80918077a`;
  - o sha256 deste adendo não cabe nele mesmo e fica no `meta.json` de cada pasta (`plano_sha256`), com o do adendo 1
    (`plano_adendo1_sha256`) e o do plano da GV3 (`plano_base_sha256`).
- **As configs:** `experiments/configs/v3_gosto_visual/piloto_enjoo2.json` (bases 91101 e 91202, K = 2, 14 dias: 4 unidades, 24 vidas) e
  `experiments/configs/v3_gosto_visual/gosto_visual_enjoo2.json` (bases 91303, 91404 e 91505, K = 12, 14 dias: 36 unidades, 216 vidas),
  as duas com a fase `gosto_visual_enjoo2` e este adendo como `plano`.
- **Os comandos**, 4 processos (V3-D8), cada um numa pasta nova, só depois deste adendo e do código na `main`:
  - o piloto: `python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/piloto_enjoo2.json --processos 4`,
    em `artifacts_v3_gosto_visual/piloto_enjoo2/`;
  - o commit da pasta do piloto (seção 7), com push;
  - a run, só se o piloto passar nas duas conferências, uma vez:
    `python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/gosto_visual_enjoo2.json --processos 4`, em
    `artifacts_v3_gosto_visual/gosto_visual_enjoo2/`.
- **A faixa:** 91101…91505, em `FAIXAS_RESERVADAS`; conferido em 2026-11-12, depois de um `git fetch`, que nem a `origin/main`
  (`7614ebb7`) nem nenhum dos 576 branches remotos com um `experiments/bancada/faixas.py` registra uma faixa que a cruze (D-GV-GV3B2-5).
- **A máquina:** conferir antes do piloto que nenhuma outra run de pesquisa roda (o `tools/pre_run.py` confere).

## 9. As escolhas deste adendo (com a recomendação e o custo de errar)

O adendo e a faixa nova estão aprovados ("Adendo e faixa nova"). Estas são as escolhas que o texto teve de fazer; cada uma segue a
recomendação e vai ao Matheus no PR.

| id | a escolha | a recomendação (a seguida) | o custo de errar |
|---|---|---|---|
| **GV3B2-1** | A regra para as duas TVs sem lugar: a réplica fica sem sonda e é contada (a (ii)). | **Sim** (seção 2): não muda a medida das réplicas que cabem. | Se a falta se concentrar numa célula, a célula perde réplicas e pode ficar enviesada; o teto e a contagem mostram isso. A (i) e a (iii) poriam uma sonda diferente dentro das medidas. |
| **GV3B2-2** | O teto de 5 %, no total e por célula; no piloto segura a run, na run vira ressalva. | **Sim**: o desvio possível fica em até 0,05 nas medidas entre 0 e 1, a ordem da tolerância da familiarização. | Alto demais deixa passar um viés de até o teto; baixo demais seguraria a run por uma perda pequena. O número é PROPOSTO, SEM FONTE. |
| **GV3B2-3** | O piloto e a run parcial do adendo 1 no git como registro, com um `LEIA.md`, sem leitura. | **Sim**: "nenhum número sem artefato" vale também para o que falhou, e o registro fica conferível. | Ler a run parcial seria olhar um resultado antes da run nova; o `LEIA.md` e a seção 3 o proíbem. |
| **GV3B2-4** | O piloto commitado antes da run, conferido pelo orquestrador (os arquivos no git, o git limpo, a conferência do piloto). | **Sim**: o `git_limpo` da run sai verdadeiro, e a run não roda com o piloto reprovado. | Uma trava a mais pode segurar a run por um arquivo solto na worktree; o erro diz qual. |
| **GV3B2-5** | A 90101…90505 em `FAIXAS_QUEIMADAS`, o piloto junto, e reservada com a marca QUEIMADA. | **Sim**: as faixas queimadas não voltam (o CLAUDE.md). | Queimar só a 90303…90505 deixaria o piloto 90101…90202 parecer reutilizável. |
| **GV3B2-6** | A fase `gosto_visual_enjoo2` escolhe a regra; as fases antigas ficam com a regra "falha". | **Sim**: o parâmetro da config é a fase, como na GV3b (D-GV-GV3B-5); as `CHAVES_CONFIG` não mudam, e a GV3 e a GV3b saem iguais. | Uma chave nova na config mudaria a validação das configs antigas. |
| **GV3B2-7** | A exceção `DuasTVsSemLugar`, um `RuntimeError` com a mensagem de antes, e só ela tratada pela regra nova. | **Sim**: quem não trata o caso falha como antes, e nenhum outro erro vira "sem sonda". | Pegar um `RuntimeError` qualquer esconderia outro erro como réplica sem lugar. |
