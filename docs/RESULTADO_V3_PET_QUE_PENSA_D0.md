# RESULTADO V3 — PET_QUE_PENSA, D0: onde o planejador poderia decidir (2026-11-21)

Worker: Claude Code, Opus 5.5, sessão lateral da Gerência da V3, branch `v3-pet-que-pensa-d0`. Tarefa:
[TAREFA_V3_PET_QUE_PENSA.md](TAREFA_V3_PET_QUE_PENSA.md) (APROVADA em 2026-11-21, D-PQ3-1 a D-PQ3-9), a etapa P1. O D0 é descritivo: sem
gate, sem classe e sem pré-registro (a seção 4 da tarefa). Código: `e075a189`, a `main` `4553cda7` com a medida e o replay,
`git_limpo` verdadeiro. O `pre_run` respondeu "pode rodar". O replay rodou uma vez, com 4 processos, de 13:01 a 13:17 (973 s):

    python experiments/run_v3_pet_que_pensa_d0.py --config experiments/configs/v3_pet_que_pensa/d0.json --processos 4 \
        --vidas D:\Trab\digilab\guarda_vidas\pv2_run\vidas.tar.gz

Os artefatos ficam em `artifacts_v3_pet_que_pensa/d0/run/`: `meta.json` (os sha256 do código, da tarefa, da config, da fonte e dos
artefatos), `resultado.json` (os resumos) e `medidas.json.gz` (as medidas por vida). O `medidas.json` cru (3 MB) fica só no sha256 do
`meta.json`: o `.gz` tem o mesmo conteúdo. **Todo número abaixo sai do `resultado.json`**, pela média dos donos por unidade e o IC95 pelo t
sobre as unidades (como no R-sono); os donos vão separados, sem IC.

**Nenhuma vida nova:** são as vidas do R1, do R-a e do R-sono, o HOJE da run do PV-2 (2 400, o corpo de hoje) e o HOJE da checagem do v38
(320), rejogadas pelo log com a `ConfigRastro` ligada. A cópia só de leitura é `D:\Trab\digilab\guarda_vidas\pv2_run\vidas.tar.gz`, com o
sha256 do `meta.json` da run do PV-2 (a C-FONTE). O OLF-0 fica de fora: a tarefa pede o corpo de hoje e o v38.

## 1. A resposta curta

- **O planejador não fica sem acesso.** Com o reflexo de hoje, **de 75 % a 85 %** das decisões do corpo de hoje já estão abertas (nem
  reflexo, nem sono que segura, nem escolha segurada), e **59 % a 60 %** no v38. Quase todas passam pelo sorteio (99 %).
- **Com o desenho (o reflexo suave e o piso em S/8), quase tudo abre no corpo de hoje: 99,9 %.** A faixa do reflexo suave cobre quase
  todo o reflexo de hoje: abaixo do piso ficam de **0,06 % a 0,08 %** das decisões. No v38, o sono que segura segue fora (24 % a 29 %), e as
  abertas ficam entre **70 % e 76 %**.
- **O conflito existe e depende muito do dono e do lugar.** A fome urgente com a energia na faixa do reflexo suave está em **8 %
  (comedouro) a 21 % (longe)** das decisões do corpo de hoje, e em **10 % a 16 %** no v38. Com o dono atencioso no `comedouro`, quase não há
  (0,7 %); com o aleatório e o relapso, de 13 % a 30 %.
- **Leitura para o desenho:** o R-1 da tarefa ("o planejador decide pouco por falta de acesso") não aparece aqui. O D0 não diz se o termo
  `plano` vai ter peso para decidir; isso é o D1.

## 2. As conferências

As que falham alto passaram nas 2 720 vidas: a C-FONTE, a C-G1 (o log rejogado igual ao do disco e as medidas iguais às gravadas), a
C-FECHO e a C-UMA-VEZ do R1, a C-REFLEXO e a C-SOMA do R-sono (`run_v3_pet_vivo_sono.rejogar` e `conferir_caminhos`) e a C-D0, nova (o D0
conta as mesmas decisões do caminho do sono, o reflexo dele é o REFLEXO mais o SEGURA do caminho do sono, e as abertas mais as de fora
somam as decisões). O replay terminou com saída 0. Cada vida tem 1 343 decisões com o rastro (a última não fecha).

## 3. O que se conta (a `metrics.medidas_d0_plano`)

Por decisão com o rastro:
- **fora da disputa hoje:** o REFLEXO (o reflexo com a energia abaixo de `lambda_sono`), o SEGURA (o reflexo com a energia em
  `lambda_sono` ou acima: o sono que segura) e a SEGURADA (a escolha segurada da C3; nenhuma destas vidas a liga);
- **aberta hoje:** as outras;
- **a faixa:** a energia em [`piso`, `lambda_sono`), com o piso em `lambda_sono / 2` (S/8, a PQ3-4);
- **o conflito:** a faixa com a fome urgente (a urgência da fome acima do `urgencia_lambda` dos inatos da vida; o v38 tem o do E1);
- **as abertas com o desenho:** as de hoje mais a faixa que hoje é reflexo (`F_ABERTAS_PLAN_TETO`). Sem o sono que segura, é a conta
  certa. No v38, parte da faixa (o pet dormindo sem a fome urgente) segue segura, e o motivo não tem o `dormindo`: o certo fica entre o
  piso, as de hoje mais o conflito (`F_ABERTAS_PLAN_PISO`, porque a fome urgente nunca é segura), e o teto.

## 4. Os números (n 200 unidades por lugar no corpo de hoje, 40 no v38; IC95)

### 4.1 O corpo de hoje (o HOJE da run do PV-2)

| medida | comedouro | longe_fixo | longe |
|---|---|---|---|
| abertas hoje | 0,847 [0,845; 0,849] | 0,811 [0,804; 0,818] | 0,752 [0,749; 0,755] |
| fora: REFLEXO | 0,153 [0,151; 0,155] | 0,189 [0,182; 0,196] | 0,248 [0,245; 0,251] |
| fora: SEGURA e SEGURADA | 0 | 0 | 0 |
| abertas com o desenho | 0,9994 [0,9993; 0,9994] | 0,9993 [0,9993; 0,9994] | 0,9992 [0,9991; 0,9992] |
| abaixo do piso | 0,0006 | 0,0007 | 0,0008 |
| a faixa | 0,153 [0,151; 0,155] | 0,189 [0,182; 0,196] | 0,247 [0,244; 0,251] |
| **o conflito** | **0,081 [0,079; 0,082]** | **0,147 [0,139; 0,155]** | **0,212 [0,209; 0,216]** |
| o conflito dentro da faixa | 0,392 [0,387; 0,397] | 0,615 [0,596; 0,634] | 0,831 [0,824; 0,838] |

Nas abertas de hoje (frações das abertas):

| medida | comedouro | longe_fixo | longe |
|---|---|---|---|
| com sorteio (dois candidatos ou mais) | 0,993 | 0,991 | 0,992 |
| nada a fazer | 0,0002 | 0,0001 | 0,0003 |
| com a fome urgente | 0,147 [0,143; 0,152] | 0,279 [0,262; 0,296] | 0,381 [0,375; 0,388] |
| dormiu | 0,368 | 0,327 | 0,284 |

### 4.2 O v38 (com o sono que segura)

| medida | longe_fixo | longe |
|---|---|---|
| abertas hoje | 0,596 [0,592; 0,599] | 0,589 [0,587; 0,591] |
| fora: REFLEXO | 0,114 [0,097; 0,132] | 0,168 [0,159; 0,177] |
| fora: SEGURA | 0,290 [0,275; 0,304] | 0,243 [0,236; 0,250] |
| abertas com o desenho, piso e teto | 0,700 [0,685; 0,715] a 0,710 [0,695; 0,724] | 0,746 [0,739; 0,753] a 0,756 [0,749; 0,763] |
| abaixo do piso | 0,0005 | 0,0007 |
| a faixa | 0,114 [0,097; 0,131] | 0,167 [0,158; 0,176] |
| **o conflito** | **0,104 [0,087; 0,122]** | **0,157 [0,148; 0,166]** |
| o conflito dentro da faixa | 0,629 [0,575; 0,684] | 0,918 [0,895; 0,940] |
| abertas com a fome urgente | 0,255 [0,218; 0,291] | 0,357 [0,340; 0,375] |
| abertas que dormiram | 0,097 | 0,087 |

### 4.3 Por dono (a média, sem IC)

O conflito:

| dono | comedouro | longe_fixo | longe | v38 longe_fixo | v38 longe |
|---|---|---|---|---|---|
| atencioso | 0,007 | 0,079 | 0,140 | 0,055 | 0,096 |
| incoerente | 0,007 | 0,087 | 0,130 | 0,052 | 0,077 |
| relapso | 0,126 | 0,190 | 0,278 | 0,126 | 0,211 |
| aleatorio | 0,183 | 0,232 | 0,300 | 0,184 | 0,244 |

As abertas hoje:

| dono | comedouro | longe_fixo | longe | v38 longe_fixo | v38 longe |
|---|---|---|---|---|---|
| atencioso | 0,908 | 0,884 | 0,831 | 0,622 | 0,631 |
| incoerente | 0,908 | 0,878 | 0,841 | 0,629 | 0,636 |
| relapso | 0,804 | 0,758 | 0,676 | 0,568 | 0,546 |
| aleatorio | 0,767 | 0,723 | 0,659 | 0,564 | 0,544 |

## 5. O que isto diz ao desenho

- **O acesso não é o gargalo.** Fora do reflexo, o pet de hoje já sorteia na maior parte das decisões: as abertas são de 75 % a 85 %, e 99 % delas têm sorteio. Que o aprendizado "quase não
  decida" (as runs de 2026-11-17 a 20) não vem da falta de decisões abertas: vem do tamanho dos termos aprendidos ante o inato. O D1 é que
  diz se o termo `plano`, com o `g_plano` do PLAN, pesa onde o aprendizado não pesou.
- **O piso quase não dispara nestas vidas.** O reflexo de hoje segura o pet em S/4, e a energia quase nunca chega a S/8. Com o reflexo
  suave, o pet pode descer mais: o piso é a guarda (o R-3), e o D1 mede a exaustão.
- **O conflito é a parte da faixa em que o desenho muda algo de que o pet precisa,** e ela é grande com os donos que cuidam pouco e longe da
  comida (de 19 % a 30 % das decisões com o relapso e o aleatório no `longe_fixo` e no `longe`). Com o dono atencioso no `comedouro`, o
  conflito quase não existe (0,7 %). A fração dos sonos que começam com a fome urgente, o descritivo do D1, vai ler essa parte.
- **No v38, o sono que segura tira de 24 % a 29 % das decisões,** e ele fica fora da primeira versão (PQ3-4). Mesmo assim, 70 % a 76 % das
  decisões ficam abertas com o desenho.

## 6. O que este D0 não mostra

- Nada sobre o planejador decidir: o D0 conta onde ele poderia entrar, nas vidas de hoje, sem ele.
- Nada sobre o "Tempo bem", a saúde ou a exaustão: só o D1 mede.
- No v38, as abertas com o desenho são só os limites (o piso e o teto): o `dormindo` não está no motivo.
- Nada fora dos 14 dias, do mundo do MVP e dos lugares da C4, nem sobre o jogo web.
- O piso em `lambda_sono / 2` e a fome urgente pelo `urgencia_lambda` são PROPOSTOS, SEM FONTE.
