# RESULTADO V3 — CORPO_ACOPLAMENTO: a opção D numa run (2026-11-18, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md](PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md), APROVADO pelo Matheus em 2026-11-18 ("Aprovo,
siga" e "Aprovo todas"), na `main` antes da primeira vida (#996). A tarefa: [TAREFA_V3_CORPO_ACOPLAMENTO.md](TAREFA_V3_CORPO_ACOPLAMENTO.md).

**A leitura, pela regra da seção 5 do plano: passa.** Com a chave D ligada, isto é, com a falta de combustível subindo a fome em vez do
cansaço:
- **a P passa:** os conflitos caem de 0,147 para 0,099 das decisões;
- **a privação** fica em "≈ 0";
- **a exaustão** cai, "< 0";
- **a taxa por episódio** sobe, "> 0".

As três guardas valem no `longe_fixo` e nas 12 células, e nenhuma reprova. A chave continua desligada no jogo, como decidido na D-CA-7. Ligá-la num pet espera o Matheus e uma rodada nova do cuidado.

## 1. A run

| comando (o do `meta.json`) | commit, árvore | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_corpo_acoplamento.py --config experiments/configs/v3_corpo_acoplamento/run.json --processos 4` | `43815734`, limpa | 4 800 (REL e D × 12 células × 200 unidades) | 100101…100505, K = 40, derivação `digibrain_prototipo` | 1 h 27 min (16:22–17:49 de 2026-11-18) |

- **O ambiente:** Python 3.13.0 e Node v24.19.0; o Node só fica gravado.
- **O pre_run:** antes de soltar a run, o `tools/pre_run.py` não deu motivo de recusa. Ele conferiu que o plano estava igual ao da
  `origin/main`, que a faixa estava reservada e que nenhuma outra run rodava.
- **A saída:** código 0, sem falha alta. As conferências rodaram vida a vida:
  - o replay;
  - o T-CENARIO-1;
  - as conferências da C4;
  - a do conserto, desligado no REL;
  - a do corpo: o corpo de cada braço tem a ponte do braço, e no D nenhum tick sobe o cansaço pela falta.
- **"Desliga não muda" (a D da seção 5 do plano):** o gabarito `tests/gabaritos/corpo_acoplamento_de_hoje.json` passa byte a byte.

**Uma tentativa anterior foi interrompida** (desvio no registro):
- **O que houve:** a primeira tentativa começou às 15:54 e morreu às 16:21, junto com a sessão do Claude Code que a tinha lançado.
- **O que ela deixou:** 1 864 vidas e nenhum `resultado.json`. Nenhum número dela foi lido.
- **O que foi feito:** as vidas parciais saíram da pasta da run, porque o orquestrador recusa gravar por cima. A run recomeçou do zero, num processo separado.
- **O determinismo:** as 1 864 vidas parciais saíram iguais byte a byte às mesmas vidas da run completa (a seção 5).

**Os artefatos,** em `artifacts_v3_corpo_acoplamento/run/`. O sha256 de cada arquivo no disco é igual ao do `meta.json`:

| arquivo | sha256 | tamanho |
|---|---|---|
| `resultado.json` | `20136834…` | |
| `medidas.json` | `09a5387c…` | 51,6 MB |
| `vidas.tar.gz` | `81732828…` | 22,3 MB, determinístico |
| `meta.json` | | |

## 2. Os critérios (seção 5 do plano)

O contraste é D − REL, pareado por unidade (n = 200), com o IC95 pelo t e as classes da A6.6, com δ = 0,032.

| critério | medida | D − REL | IC95 | classe | **passa** |
|---|---|---|---|---|---|
| **P** | os conflitos, a média das 12 células (REL 0,147; D 0,099) | **−0,048** | [−0,050; −0,046] | REL − D "> 0", p = 1,5 × 10⁻¹⁰⁴ | **sim** |
| G1 | a privação, `longe_fixo` (REL 0,332; D 0,329) | −0,004 | [−0,018; +0,010] | ≈ 0 | sim |
| G1 | a privação, 12 células (REL 0,344; D 0,364) | +0,020 | [+0,013; +0,026] | ≈ 0, sinal + | sim |
| G2 | a exaustão, `longe_fixo` (REL 0,216; D 0,140) | **−0,076** | [−0,083; −0,070] | < 0 | sim |
| G2 | a exaustão, 12 células (REL 0,231; D 0,153) | **−0,078** | [−0,081; −0,075] | < 0 | sim |
| G3 | a taxa por episódio, `longe_fixo` (REL 0,586; D 0,702) | **+0,115** | [+0,102; +0,129] | > 0 | sim |
| G3 | a taxa por episódio, 12 células (REL 0,634; D 0,725) | **+0,091** | [+0,085; +0,098] | > 0 | sim |

- **O efeito da P não é trivial:** o IC inteiro fica abaixo de −δ.
- **O bootstrap** sobre as 5 bases dá um IC95 de [+0,047; +0,048] para REL − D, com o rótulo da VALUATION: é anticonservador com 5 bases.
- **O g1** é 0,47.

## 3. Ao lado, sem classe (o IC95 do D − REL)

| medida | lugar | REL | D | D − REL [IC95] |
|---|---|---|---|---|
| a fome urgente na energia baixa (a fração que motivou a tarefa) | 12 células | 0,613 | 0,606 | −0,007 [−0,012; −0,001] |
| | `longe_fixo` | 0,617 | 0,587 | −0,030 [−0,044; −0,017] |
| a fome urgente na energia boa | 12 células | 0,268 | 0,331 | +0,063 [+0,059; +0,066] |
| a fração das decisões com a energia baixa | 12 células | 0,196 | 0,131 | −0,065 [−0,067; −0,063] |
| a fração dos ticks dormindo | 12 células | 0,465 | 0,376 | −0,089 [−0,090; −0,089] |
| os ticks com o combustível abaixo de C/4 | 12 células | 0,517 | 0,403 | −0,113 [−0,116; −0,111] |
| os reflexos por vida | 12 células | 264 | 177 | −87 [−90; −85] |
| o comer trocado pelo reflexo, por vida | 12 células | 13,3 | 8,3 | −5,0 [−5,2; −4,8] |
| as refeições por dia | 12 células | 3,19 | 3,70 | +0,51 [+0,48; +0,53] |
| o comer no episódio | 12 células | 0,193 | 0,263 | +0,070 [+0,067; +0,073] |
| o dormir no episódio | 12 células | 0,442 | 0,283 | −0,159 [−0,162; −0,157] |
| a `janela_vencida` | 12 células | 0,363 | 0,271 | −0,092 [−0,098; −0,085] |
| **a privação no comedouro** | comedouro | 0,159 | 0,231 | **+0,072 [+0,068; +0,076]** |

**O cansaço por fonte, somado nas vidas:** no D, a falta de combustível põe 0 de cansaço, contra 12,5 × 10⁹ no REL. As outras fontes sobem
um pouco no D: o andar, as atividades e o basal do dia e da noite. O pet fica mais tempo acordado (`cansaco_por_fonte_somado`).

## 4. A leitura

- **A D tira a ponte e o pet troca dormir por comer.** O cansaço do jejum some. A energia baixa cai de 0,196 para 0,131 das decisões, e os
  reflexos caem um terço. O pet come mais (de 3,19 para 3,70 refeições por dia) e fecha mais episódios de fome. É o que a predição da
  opção D dizia (a seção 10 da tarefa).
- **A fração condicional quase não se mexe:** a fome urgente na energia baixa vai de 0,613 para 0,606, como na sonda da etapa 2. O que cai é
  o número de vezes que o pet chega cansado, e não a parte dessas vezes com fome. A D-CA-9 tinha previsto isso, e o primário mede o que o
  pet vive.
- **A fome urgente sobe na energia boa** (de 0,268 para 0,331). Agora o jejum aparece como fome, e não como cansaço: é o efeito pedido.
- **A privação sobe no comedouro** (+0,072), e por isso as 12 células saem com o sinal +. As guardas da regra são o `longe_fixo` e as 12
  células, e as duas ficam em "≈ 0". O comedouro foi lido depois, como descritivo, e não muda a leitura. Fica como questão aberta: perto da
  comida, a fome sobe mais cedo, e a privação conta a fome alta.
- **Uma comparação entre runs, só descritiva:** na A1 (97xxx), a TRIV teve 0,645 na taxa por episódio do `longe_fixo`. O D aqui tem 0,702,
  com outras sementes e sem um teste. A pergunta "o D com o modular bate a baseline trivial" é a validação C4 do programa do corpo, que
  ainda não rodou.

## 5. O determinismo

As 1 864 vidas da tentativa interrompida foram comparadas, arquivo a arquivo, com as mesmas vidas da run completa: são iguais byte a byte
(o `cmp`; a seção do registro).

## 6. O que a run não demonstra

- **o jogo web:** a chave fica desligada nele (D-CA-7);
- **o I-PAD da LONGE_GEOMETRIA:** o sono muda, e o I-PAD vem do sono. Medir de novo é outra run;
- **a calibração do cuidado** (E1 e E2);
- **outros valores e combinações:** nenhum `falta_fome` além do 500, e nada com o conserto da VALUATION ou com o sono que segura ligados;
- **fora do desenho:** nada além dos 14 dias e do mundo do MVP;
- **a comparação com a TRIV** (a seção 4) é só descritiva.

## 7. O próximo passo

- **O programa do corpo:** a D passou, e pela regra da seção 8 do `docs/MAPA_CORPO.md` os braços da C1 são D, D + E e D + C5
  (o plano da C1, num PR empilhado no #999).
- **O jogo:** ligar a D num pet do jogo é decisão do Matheus, depois de uma rodada nova do cuidado (D-CA-7).
