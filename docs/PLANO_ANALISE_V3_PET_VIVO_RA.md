# PLANO DE ANÁLISE V3 — PET_VIVO, R-a: a linha de base do intervalo (2026-11-19, Claude Code, Fable 5.2)

**Status: APROVADO pelo Matheus em 2026-11-19.** À pergunta "Aprova o plano do R-a e as RB-1 a RB-5 pela recomendação?", nesta
sessão, a resposta foi "Aprovo todas" (D-RB-4). As decisões RB-1 a RB-5 da seção 9 estão DECIDIDAS pela recomendação. Os cortes e os
pisos seguem SEM FONTE. **Nenhum replay e nenhuma conta deste plano rodam antes de quatro coisas:**
1. a marca "APROVADO pelo Matheus" neste cabeçalho (feita acima);
2. o código da seção 7 na `main`, com os testes dele;
3. a run da C3 da CORPO terminada e o `pre_run` respondendo "pode rodar";
4. as conferências da seção 3, que falham alto antes de qualquer medida.

**De onde vem:**
- o [resultado do R1](RESULTADO_V3_PET_VIVO_R1.md): "a maior parte do sinal está fora do r" e "o sinal do intervalo é o sono, e a
  linha de base por contexto o apaga". O plano do R2 recebe "propor outra linha de base, ou outro contexto, antes do código";
- o planejamento das próximas runs, aprovado pelo Matheus em 2026-11-19 ("Aprovo, repasse", pela sessão coordenadora): o R-a é um
  replay sem vida nova, com plano curto, e todo plano traz os quatro itens da seção 2 daqui.

**O que o R-a é:** outra leitura das mesmas vidas. Nada é creditado, nada muda no cérebro, e nenhuma vida nova roda. **O R-a não é o
R2** e não escolhe a linha de base do R2: ele diz quais candidatas preservam o sono e se sobra algo entre as ações acordadas.

**Este plano não calcula nenhum número de resultado.** Os números que ele cita saem do `artifacts_v3_pet_vivo/r1/run/` (já na
`main`) ou são fatos do código. Os cortes e os pisos são PROPOSTOS e SEM FONTE. **Nenhuma alegação de novidade.**

## 1. A pergunta e as hipóteses, escritas antes

- **Q-SONO:** que linha de base, das que não dependem da ação escolhida, deixa o dormir com o resto positivo?
- **Q-ALÉM:** tirado o sono, o intervalo distingue as ações acordadas?

| hipótese | o que diz | de onde vem |
|---|---|---|
| H-MÓVEL | a média móvel curta apaga o sono, porque o pet dorme em blocos; a longa o preserva | o reflexo do sono segura o pet várias decisões seguidas (R1, M-TROCA) |
| H-ESTADO | o que sobra para o ocioso no R1 (+106 a +120 pela linha de base por contexto) encolhe quando a linha de base conta o estado do corpo | o r é quadrático na falta: o mesmo decaimento custa mais com a falta alta |
| H-ALÉM | o η² entre as ações acordadas fica abaixo de 0,05 em toda linha de base: "só o sono" | o η² por contexto do R1 (0,011 a 0,019) já mede isso com a média do acordado |

**O desfecho esperado é "só o sono".** Se ele sair, o R2 nasce como "ensinar o valor de dormir", e não como um crédito geral do
intervalo.

## 2. Os quatro itens da ficha de entrada

### 2.1 O que as vidas gravadas já respondem, e por que não bastam

- **Já respondem:** pela linha de base global, o resto do dormir é +156 a +159; pela de contexto (acordado e dormindo), é 0 por
  construção; entre as ações acordadas, com a média do acordado, o η² é 0,011 a 0,019.
- **Não bastam:** o `medidas.json.gz` do R1 guarda, por vida, só a média por comportamento com essas duas linhas de base. Uma linha
  de base nova precisa do `r_int_n` de cada decisão, que não foi gravado.
- **Por isso o R-a rejoga as mesmas vidas pelo log,** com a `ConfigRastro` ligada, como o R1. Nenhuma vida nova e nenhuma faixa
  nova.

### 2.2 A contagem do evento da premissa, com o piso

O evento é a decisão de cada comportamento. A contagem sai do `medidas.json.gz` do R1 (o HOJE da run, 800 vidas por lugar, 1 343
decisões por vida, cerca de 715 acordadas):

| comportamento | decisões por vida (média): comedouro, longe, longe_fixo | vidas com menos de 5 |
|---|---|---|
| dormir | 629, 627, 619 | 0 |
| explorar | 435, 350, 361 | 0 |
| chamar atenção | 172, 222, 231 | 0 |
| comer | 69, 86, 77 | 0, 0, 0,6 % |
| brincar | 21, 29, 30 | 12 %, 10 %, 4 % |
| emburrar | 6,5, 20,9, 15,2 | 42 %, 9 %, 28 % |
| ocioso | 9,7, 8,3, 8,6 | 16 %, 25 %, 25 % |

- **O piso (RB-3):** um comportamento entra no η² de uma vida com 5 decisões ou mais nela. Abaixo disso, fica fora daquela vida.
- **O ocioso e o emburrar ficam só como descritivo.** Mais de 94 % das vidas têm menos de 20 decisões de ocioso. O "ocioso sobra" do
  R1 se apoia em cerca de 9 decisões por vida, e o resultado do R-a repete esse aviso.
- **Q-SONO e Q-ALÉM não dependem deles:** o dormir, o explorar, o chamar atenção e o comer passam do piso em quase toda vida.

### 2.3 A precisão, calculada antes

- No R1, o desvio-padrão do η² por contexto entre as 200 unidades é 0,010, 0,004 e 0,006 (comedouro, longe, longe_fixo). A
  meia-largura do IC95 fica em 0,0014, 0,0005 e 0,0009.
- O corte é 0,05, e os valores do R1 ficam a 0,03 dele. **A margem é 20 vezes maior que a meia-largura.** "Indeterminado" por falta
  de n não é o desfecho provável.
- Uma linha de base nova pode ter dp maior. Se a meia-largura de alguma passar de 0,01, o resultado diz isso ao lado do número.

### 2.4 O corpo e os donos

- **O corpo é o de hoje (o CTRL):** a `CONFIG_CORPO_METABOLISMO` com o mundo, como na run do PV-2. Sem a D, sem a E e sem o teto da
  ponte. As vidas já estão gravadas, então o resultado da C3 não as muda.
- **Se o corpo mudar depois do CHECKPOINT da C3, a leitura do R-a vale só para o corpo de hoje,** e o plano do R2 tem de dizer se
  mede de novo no corpo novo.
- **Os donos distintos, contados no `medidas.json.gz` do R1:** no comedouro, as medidas da vida do incoerente saem iguais às do
  atencioso em 200 de 200 unidades; no longe, em 0 de 200; no longe_fixo, em 1 de 200. O comedouro tem 3 donos distintos, e o
  atencioso pesa em dobro na média dele. Os donos saem também separados.

## 3. A fonte e as conferências

- **As vidas:** as do R1. O HOJE da run do PV-2 (2 400) dá a leitura; o OLF-0 (2 400) e o HOJE do v38 (320) saem ao lado. São 5 120
  replays.
- **Onde estão:** `D:\Trab\digilab\v3-pet-vivo-pv2-run\artifacts_v3_pet_vivo\pv2\run\vidas.tar.gz` (72 MB, com o sha256 no
  `meta.json` da run do PV-2). **Esse arquivo não pode ser limpo antes do R-a** (RB-5).
- **As conferências que falham alto,** antes de qualquer medida: a C-FONTE, a C-G1, a C-FECHO e a C-UMA-VEZ do R1, e uma nova:
  - **C-IGUAL-R1:** as linhas de base global e por contexto, recalculadas por decisão, dão as mesmas medidas do
    `medidas.json.gz` do R1, vida a vida.

## 4. As linhas de base candidatas (RB-1)

Cada uma dá, por decisão, `resto = r_int_n − linha de base`. Nenhuma olha a ação escolhida.

| nome | a linha de base da decisão | o que testa |
|---|---|---|
| GLOBAL | a média da vida | a referência do R1 |
| CTX | a média do contexto (acordado ou dormindo) na vida | a do R1, só para a C-IGUAL-R1; é a única que olha a ação |
| **FASE** | a média da fase do dia (dia ou noite, pelo tick do começo do intervalo) na vida | se a hora explica o sono |
| **ESTADO** | a média do quartil da carga do corpo na vida; a carga é a soma dos quadrados das faltas dos 11 receptores logo depois da ação | se o estado do corpo explica o que sobra |
| **MÓVEL-k** | a média móvel exponencial dos `r_int_n` anteriores da vida, sem o atual, com k = 4, 16 e 96 decisões (1 h, 4 h e 1 dia) | a forma causal, que um R2 conseguiria usar ao vivo |

- A GLOBAL, a FASE e a ESTADO usam a vida inteira: servem à leitura, e não a um cérebro ao vivo. Só a MÓVEL é causal.
- **Os k são só três pontos para ver a forma (RB-2).** O R-a não escolhe o k do R2.

## 5. As medidas (no `digilab/metrics.py`, uma vez só)

A unidade é a vida, e os IC95 são por lugar, sobre as 200 unidades, com a média dos 4 donos, como no R1. Para cada linha de base:

- **o resto do dormir:** a média do resto nas decisões de dormir;
- **η² de todas:** a fração da variância do resto que fica entre os 7 comportamentos;
- **η² do acordado:** a mesma fração, só nas decisões acordadas, entre os comportamentos acordados que passam do piso;
- **o resto por comportamento acordado,** com o número de decisões ao lado.

## 6. A regra de leitura, escrita antes

Nenhuma medida é gate. A regra diz o que o plano do R2 recebe. Ela se lê no HOJE, nos 3 lugares, pelo limite do IC95. O corte de
0,05 é o da RA-5, SEM FONTE (RB-4).

**L-SONO, por linha de base** (FASE, ESTADO e cada MÓVEL-k):

| o que sai | a leitura |
|---|---|
| o limite de baixo do resto do dormir > 0 nos 3 lugares | "preserva o sono" |
| o limite de cima ≤ 0 em algum lugar | "apaga o sono" |
| outro caso | "indeterminado", com os números |

**L-ALÉM, pelo η² do acordado:**

| o que sai | a leitura | o que o plano do R2 recebe |
|---|---|---|
| o limite de baixo > 0,05 em pelo menos 2 lugares, na ESTADO | "há o que creditar além do sono" | o R2 pode ser um crédito geral do intervalo, com a linha de base que preserva o sono |
| o limite de cima < 0,05 nos 3 lugares, na GLOBAL, na FASE, na ESTADO e nas MÓVEL | "só o sono" | o R2 se reduz a ensinar o valor de dormir; o resto do intervalo é decaimento igual para toda ação acordada |
| outro caso | "indeterminado", com os números | o plano do R2 mede de novo nas sementes dele |

**O que a regra não decide:** se creditar o sono melhora a vida do pet, que k o R2 usa, nem qual é a medida de bem-estar.

## 7. O que falta antes do replay (o PR do código, depois do APROVADO)

- `metrics.medidas_linha_base(motivos)`, que lê o `motivo["cadeia"]` que o R1 já grava. **Nada muda no cérebro, no corpo nem no
  motor.**
- `experiments/run_v3_pet_vivo_ra.py`, que reusa a leitura da fonte e as conferências do R1, e a config
  `experiments/configs/v3_pet_vivo/ra.json`.
- Os testes: a C-IGUAL-R1 numa vida das sementes dos testes, e cada linha de base conferida à mão numa vida curta.
- A fumaça da C-G1 em 2 vidas reais, como no R1, antes do replay inteiro.

## 8. O custo e a máquina

- **O tempo:** o R1 levou 38 min com 4 processos nas mesmas 5 120 vidas. O R-a faz a mesma coisa com mais contas por vida. Se a
  projeção da fumaça passar de 2 h, o replay não roda e o plano volta ao Matheus.
- **O disco:** o D: tinha 89 GB livres em 2026-11-19. O replay grava cerca de 40 MB. O worker confere de novo antes de soltar; o
  piso é 10 GB.
- **A vez:** uma run por vez, até 4 processos (V3-D8). O R-a só roda depois da C3 da CORPO e com o `pre_run` liberando.

## 9. As decisões com o Matheus (DECIDIDAS pela recomendação em 2026-11-19, "Aprovo todas"; D-RB-4)

| nº | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| RB-1 | quais linhas de base entram | FASE, ESTADO e MÓVEL, mais a GLOBAL e a CTX como referência | baixo: outra linha de base custa outro replay de 40 min |
| RB-2 | os k da média móvel | 4, 16 e 96 decisões, só para ver a forma | baixo: o k do R2 é do plano do R2 |
| RB-3 | o piso de decisões por comportamento numa vida | 5; o ocioso e o emburrar só como descritivo | médio: um piso baixo deixa o η² do acordado ser puxado por 5 a 9 decisões |
| RB-4 | o corte do η² | 0,05, o mesmo do R1, SEM FONTE | médio: ele separa "crédito geral" de "só o sono" |
| RB-5 | a fonte | o `vidas.tar.gz` da run do PV-2 fica na máquina até o R-a rodar | alto se for apagado: as vidas teriam de ser regeneradas, 4 h de máquina |

## 10. O que este plano não demonstra, mesmo depois do replay

- **Nada sobre o crédito.** Uma linha de base que preserva o sono não mostra que ensinar o sono ajuda.
- **Nada sobre o corpo depois da C3,** nem sobre o jogo web, nem fora dos 14 dias e dos lugares da C4.
- **A medida primária de bem-estar segue em aberto.** É decisão do Matheus e vem antes de qualquer plano do R2. O R-a não a usa.
- **A FASE e a ESTADO são leituras com a vida inteira,** e não mecanismos que o cérebro teria ao vivo.
