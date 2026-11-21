# RESULTADO V3 — CORPO V1-a: a triagem do teto baixo no pet v38 (2026-11-21, Claude Code, Fable 5.2)

**O que é:** a triagem do adendo 1 do [PLANO_ANALISE_V3_CORPO_V1.md](PLANO_ANALISE_V3_CORPO_V1.md) (seção 11), APROVADO pelo Matheus em
2026-11-21. São 20 unidades, só para estimar o tamanho do efeito. **Não é a validação:** não tem classe, não tem p, não tem "confirma"
ou "não confirma", e nenhum corte foi aplicado. A run de 200 unidades continua suspensa; rodá-la ou não é decisão do Matheus.

**A estimativa principal:** no pet v38, DTB − CTRL no "Tempo bem" deu **+0,024 [+0,009; +0,038]** nas 12 células e **+0,025 [+0,009; +0,041]** nas 11 distintas,
com 20 unidades.
- **Em relação à margem do plano (δ = 0,032):** o efeito estimado é 0,74 δ nas 12 células e
  0,78 δ nas 11. O intervalo vai de 0,30 δ a
  1,19 δ.
- **Em relação ao corte proposto pela coordenação (2δ = 0,064), ainda não decidido:** o limite de cima do intervalo
  (+0,038) fica abaixo de 0,064.
- **Em relação à C4:** no pet da bancada o mesmo contraste deu +0,062 [+0,058; +0,067]. No pet v38 a estimativa é menos da
  metade disso.
- **Em relação à contagem nas sementes dos testes** (5 unidades, +0,016 [−0,003; +0,035]): a triagem cai dentro daquele intervalo.

## 1. A triagem

| comando (o do `meta.json`) | commit | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_corpo_v1.py --config experiments/configs/v3_corpo_v1/triagem.json --processos 4` | `e5d95bfc` (a `main`) | 480 (2 braços × 12 células × 20 unidades) | 109001…109020, k = 1, derivação `digibrain_prototipo` | 9 min 11 s (13:49–13:58 de 2026-11-21) |

- **A autorização:** o Matheus confirmou nesta sessão ("Sim, solte"). A coordenadora tinha repassado antes um ok dele ("Sim, rodar");
  a triagem só saiu com a confirmação direta.
- **O pre_run:** "pode rodar": o plano igual ao da `origin/main`, a faixa reservada e nenhuma outra run. O script de lançamento
  conferiu também que o orquestrador, a config e o `digilab/` eram os da `main`, e que a árvore estava limpa.
- **A saída:** código 0, o log de erros vazio. As conferências rodaram vida a vida (o replay, o T-CENARIO-1, as do mecanismo, as da
  memória, as do corpo do braço e a do pet v38). O `meta.json` grava `git_limpo = true`.
- **O ambiente:** Python 3.13.0; 48,2 GB livres no `D:`.
- **A duração** ficou acima dos 7 minutos estimados no adendo.
- **Rodou uma vez.** As 20 bases não voltam para uma run confirmatória.

**Os artefatos,** em `artifacts_v3_corpo/v1a_triagem/`. O sha256 de cada arquivo no disco é igual ao do `meta.json`:

| arquivo | sha256 |
|---|---|
| `resultado.json` | `02a9e2f0…2887` |
| `medidas.json` | `937dad3e…01be` |
| `custos.json` | `01ba97bf…344f` |
| `vidas.tar.gz` | `8b4d9a3a…d491`, as 480 vidas; o pacote foi conferido contra a pasta crua, que foi apagada |

## 2. As estimativas

DTB − CTRL, pareado por unidade, com o IC95 pelo t sobre as 20 unidades. Os braços são o pet v38 de hoje (CTRL) e o mesmo pet com o
teto baixo (DTB). A última coluna traz a C4, no pet da bancada e em outras sementes: o par não é um contraste.

| medida | CTRL | DTB | DTB − CTRL [IC95] | dp | na C4 (pet da bancada, 200 unidades) |
|---|---|---|---|---|---|
| **"Tempo bem", 12 células** | 0,728 | 0,752 | +0,024 [+0,009; +0,038] | 0,031 | +0,062 [+0,058; +0,067] |
| **"Tempo bem", 11 células distintas** | 0,705 | 0,730 | +0,025 [+0,009; +0,041] | 0,034 | +0,064 [+0,059; +0,068] |
| "Tempo bem", comedouro | 0,843 | 0,838 | −0,005 [−0,009; −0,001] | 0,009 | +0,029 [+0,027; +0,031] |
| "Tempo bem", longe | 0,611 | 0,646 | +0,036 [+0,008; +0,064] | 0,060 | +0,070 [+0,062; +0,078] |
| "Tempo bem", `longe_fixo` | 0,730 | 0,770 | +0,041 [+0,008; +0,073] | 0,070 | +0,088 [+0,078; +0,098] |
| saúde, 12 células | 0,655 | 0,691 | +0,036 [+0,005; +0,067] | 0,066 | +0,056 [+0,049; +0,064] |
| saúde, o relapso e o aleatório (6 células) | 0,479 | 0,501 | +0,022 [−0,004; +0,048] | 0,056 | +0,013 [+0,005; +0,022] |
| a taxa por episódio de fome, `longe_fixo` | 0,528 | 0,641 | +0,113 [+0,062; +0,163] | 0,108 | +0,126 [+0,112; +0,140] |

**A saúde nas células dos donos que deixam faltar comida:**

| célula | CTRL | DTB | DTB − CTRL [IC95] | dp | na C4 |
|---|---|---|---|---|---|
| relapso, comedouro | 0,971 | 0,960 | −0,011 [−0,016; −0,005] | 0,011 | −0,008 [−0,010; −0,006] |
| relapso, longe | 0,430 | 0,520 | +0,090 [−0,045; +0,225] | 0,288 | +0,089 [+0,051; +0,126] |
| relapso, `longe_fixo` | 0,788 | 0,832 | +0,044 [−0,034; +0,121] | 0,166 | +0,039 [+0,020; +0,059] |
| aleatório, comedouro | 0,333 | 0,304 | −0,030 [−0,047; −0,013] | 0,037 | −0,049 [−0,061; −0,038] |
| aleatório, longe | 0,148 | 0,146 | −0,001 [−0,055; +0,053] | 0,115 | +0,015 [−0,001; +0,032] |
| aleatório, `longe_fixo` | 0,206 | 0,246 | +0,040 [−0,024; +0,105] | 0,139 | −0,006 [−0,022; +0,010] |

**O que as tabelas mostram, sem leitura:**
- **O "Tempo bem" sobe pouco no pet v38.** O pet de hoje já parte de 0,728 (na C4, o da bancada partia de 0,633).
- **No comedouro o sinal é negativo,** e pequeno: −0,005 [−0,009; −0,001]. Na C4 era positivo.
- **A taxa por episódio sobe** quase como na C4.
- **A saúde no aleatório do comedouro cai** (−0,030 [−0,047; −0,013]), como na C3 e na C4, e a do relapso no
  comedouro também, em tamanho menor.
- **Os intervalos por célula são largos.** Com 20 unidades, a saúde do relapso no longe vai de
  −0,045 a +0,225.

## 3. O descritivo

**Por lugar:**

| medida, DTB − CTRL [IC95] | comedouro | longe | `longe_fixo` | 12 células |
|---|---|---|---|---|
| "Tempo bem", dias 8 a 14 | −0,002 [−0,011; +0,007] | +0,059 [+0,008; +0,110] | +0,051 [−0,007; +0,110] | +0,036 [+0,007; +0,065] |
| privação, a vida toda | +0,008 [+0,004; +0,012] | −0,033 [−0,061; −0,005] | −0,038 [−0,070; −0,005] | −0,021 [−0,035; −0,007] |
| exaustão, a vida toda | −0,018 [−0,021; −0,015] | −0,071 [−0,084; −0,058] | −0,049 [−0,066; −0,033] | −0,046 [−0,054; −0,038] |
| saúde média, dias 8 a 14 | −0,008 [−0,013; −0,004] | +0,057 [−0,003; +0,116] | +0,060 [+0,002; +0,117] | +0,036 [+0,005; +0,067] |
| a taxa por episódio de fome | +0,120 [+0,085; +0,155] | +0,080 [+0,040; +0,120] | +0,113 [+0,062; +0,163] | +0,104 [+0,081; +0,127] |
| episódios de fome por vida | +3,3 [+2,7; +4,0] | +2,7 [+1,8; +3,6] | +3,1 [+2,3; +3,9] | +3,0 [+2,5; +3,6] |
| refeições por dia | +0,63 [+0,54; +0,71] | +0,32 [+0,20; +0,44] | +0,57 [+0,40; +0,73] | +0,50 [+0,43; +0,58] |
| fração dos ticks dormindo | −0,079 [−0,081; −0,077] | −0,090 [−0,093; −0,088] | −0,084 [−0,088; −0,080] | −0,085 [−0,087; −0,083] |
| chutes na bola por vida | −4,6 [−6,5; −2,7] | −1,5 [−3,4; +0,4] | −2,4 [−4,0; −0,8] | −2,8 [−3,8; −1,9] |
| "brincar" por vida | +5,8 [+3,3; +8,2] | +5,8 [+1,7; +10,0] | +12,5 [+8,2; +16,8] | +8,0 [+5,8; +10,2] |
| a fome média | +0,004 [−0,000; +0,007] | −0,022 [−0,045; +0,001] | −0,033 [−0,058; −0,009] | −0,017 [−0,028; −0,006] |
| o tempo com a fome acima de 0,5 | +0,036 [+0,030; +0,043] | −0,006 [−0,036; +0,024] | −0,018 [−0,049; +0,014] | +0,004 [−0,010; +0,019] |
| vidas com o "Tempo bem" acima de 0,99 | +0,175 [+0,038; +0,312] | −0,025 [−0,061; +0,011] | +0,113 [+0,016; +0,209] | +0,087 [+0,032; +0,143] |

**O "Tempo bem" por célula:**

| célula | CTRL | DTB | DTB − CTRL [IC95] |
|---|---|---|---|
| atencioso, comedouro | 0,983 | 0,994 | +0,011 [+0,003; +0,020] |
| atencioso, longe | 0,731 | 0,765 | +0,034 [−0,056; +0,124] |
| atencioso, `longe_fixo` | 0,832 | 0,937 | +0,105 [+0,033; +0,177] |
| incoerente, comedouro | 0,983 | 0,994 | +0,011 [+0,003; +0,020] |
| incoerente, longe | 0,780 | 0,826 | +0,046 [−0,021; +0,113] |
| incoerente, `longe_fixo` | 0,944 | 0,970 | +0,027 [−0,038; +0,091] |
| relapso, comedouro | 0,880 | 0,852 | −0,028 [−0,033; −0,022] |
| relapso, longe | 0,552 | 0,593 | +0,042 [+0,001; +0,082] |
| relapso, `longe_fixo` | 0,716 | 0,726 | +0,010 [−0,018; +0,038] |
| aleatório, comedouro | 0,529 | 0,513 | −0,016 [−0,023; −0,008] |
| aleatório, longe | 0,380 | 0,402 | +0,021 [−0,006; +0,049] |
| aleatório, `longe_fixo` | 0,426 | 0,448 | +0,021 [−0,001; +0,043] |

- **De onde vem o pouco que sobe:** a exaustão ainda desce (nas 12 células, −0,046 [−0,054; −0,038]),
  mas o pet v38 já tem pouca exaustão (0,115 da vida, contra 0,202 na C4).
- **O teto da medida pesa.** Com os donos que alimentam no comedouro, o "Tempo bem" do pet de hoje já é
  0,983. Nas 12 células,
  19 % das vidas do CTRL e
  28 % das do DTB ficam acima de 0,99.
- **O pet com o DTB chuta menos a bola:** −2,8 [−3,8; −1,9] chute por vida nas 12 células
  (de 22,8 para 19,9),
  embora escolha "brincar" mais vezes. Na C4, no pet da bancada, ele chutava mais.
- **O pet dorme menos e come mais,** como na C4.
- **O incoerente no comedouro** sai igual ao atencioso em 20 de 20 vidas, nos dois braços.

**Os eventos das premissas** (só os valores; a triagem não aplica pisos):
- vidas com o "Tempo bem" em exatamente 0 ou 1: 1 de 240 no CTRL e 8 de 240 no DTB
  (3,3 %; o piso da run seria 5 %);
- a ponte cortada pelo teto: 0,27 dos ticks no comedouro, 0,46 no longe e
  0,33 no `longe_fixo`;
- episódios de fome por vida no `longe_fixo`: 14,3 no CTRL e
  17,4 no DTB, nenhuma vida sem episódio;
- chutes por vida do CTRL no `longe_fixo`: 19,8, com 99 %
  das vidas com chute.

## 4. O que fica para o Matheus

- **Se a run de 200 roda.** A triagem só dá o tamanho: +0,024 no "Tempo bem", com o intervalo de
  +0,009 a +0,038. Nenhum corte foi aplicado. O corte (2δ ou δ) não foi decidido.
- **O que a regra do plano faria com um efeito desse tamanho:** com 200 unidades e o desvio-padrão desta triagem (0,031), a
  meia largura do IC95 seria cerca de 0,004. Um efeito verdadeiro perto de +0,024 sairia "≈ 0", e a regra da seção 6 leria
  "não confirma". Isso é uma conta com a estimativa da triagem, não um resultado.
- **Se a run rodar,** usa as 180 bases que sobram (109021…109200), pela D-V1A-13.

**O que esta triagem não demonstra:** não é a validação (20 unidades, sem regra de leitura); nada sobre o jogo web, nem sobre o pet
v38 com a TV, a ilha grande e a memória de 128 células; nada sobre outro teto além de C/2, nem sobre os pares e o social.
