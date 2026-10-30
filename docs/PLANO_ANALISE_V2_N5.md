# Plano de análise — N5: o dono informa, o mundo valida ou refuta (braços P2 e P2e)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status: **registrado antes de qualquer dado** (2026-10-04). Tarefa `docs/TAREFA_V2_N5_PLANO.md`; nó N5 do `docs/ROADMAP_V2.md`; definição D-A
de `docs/ARQUITETURA_V2_VALIDACAO.md`; predições 3 e 4 de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`. **Só papel:** nenhuma run, nenhum
código. Todo número citado aponta o artefato; os números de desenho sem fonte estão marcados PROPOSTO; o resto é decisão do Matheus (seção 12).

**A pergunta.** Um pet que aprende pela consequência no mundo (o P1, com o humor das frutas no sinal: decisão E2) usa a **informação** do dono
de um jeito que (a) o faz chegar mais depressa à escolha certa quando o dono informa certo, e (b) é corrigido pelo mundo quando o dono informa
errado? É o braço P2 e o P2e da pergunta maior, testados aqui sozinhos, antes de entrarem no experimento maior.

**O que sustenta ter o braço, e o que não sustenta.** Pessoas que ensinam agentes tentam **guiar**, não só avaliar (Thomaz e Breazeal 2008,
`10.1016/j.artint.2007.09.009`, VERIFICADA): isso apoia testar o dono como fonte de informação, separado do dono avaliador (o P3, que segue o
feedback como vantagem: MacGlashan et al. 2017, arXiv:1701.06049, VERIFICADA). Nada na literatura verificada do projeto diz que um pet com
este aprendiz vai usar a informação, nem que o mundo vai corrigi-la: as duas coisas são hipóteses do Digilab. **Nenhuma alegação de novidade**;
a decomposição da plasticidade por fonte só se diz "não localizada" depois da busca do prompt 11 (decisão D5).

**Não reabre nada.** A v1 e a pergunta do dono neste motor seguem encerradas; o N3 e o N4 entram com os resultados que tiveram
(`docs/RESULTADO_V2_N3.md`, `docs/RESULTADO_V2_N4.md`).

---

## 1. Pré-requisitos (nada roda antes de estarem na `main`)

| # | o quê | quem | estado em 2026-10-04 |
|---|---|---|---|
| R1 | o mundo do N5: o evento de informar, a janela, o `DonoInformante` (`certo`, `errado`) | chat A, `docs/TAREFA_V2_N5_MUNDO.md` | PR #140 aberto |
| R2 | os lobos percebem as frutas e escolhem a fruta pelo lobo de decisão; a E2 (humor no sinal do P1 quando a ação foi comer fruta) | chat B, `docs/TAREFA_V2_LOBOS_MUNDO.md` | aberta |
| R3 | o mundo `descasado` pela bancada, as unidades derivadas (E3) e a `taxa_fruta_ruim` por janela em `metrics.py` | chat D, `docs/TAREFA_V2_BANCADA_FRUTAS.md` | aberta |
| R4 | a fonte `informacao` na bancada (P2, P2e e o acoplado desta seção 4), a entrada da informação nos lobos (seção 3) e o modo `acoplado` do informante (seção 4.2) | a implementação do N5 (rodada 6) | depois deste plano |

## 2. O que é informar

**Nomes (combinados com o chat A; este plano os torna definitivos):**

| peça | nome | onde |
|---|---|---|
| evento | `AcaoUsuario.INFORMAR_FRUTA_<A\|B\|C>_<BEM\|MAL>` (`informar_fruta_a_bem`, …), no fim do enum; tupla `ACOES_INFORMACAO` | `digilab/events.py` (#140) |
| percepção | `Observacao.info_frutas = (a, b, c)`: +1 "bem", −1 "mal", 0 sem informação vigente | `digilab/policy.py` (#140) |
| janela | `ConfigInformacao.janela_min` (240 min, PROPOSTO); informar de novo renova; o conteúdo contrário troca o valor | `digilab/config.py` (#140) |
| dono | `DonoInformante`, modos `certo` (P2), `errado` (P2e) e **`acoplado`** (seção 4.2, nome novo deste plano) | `digilab/frutas.py` (#140; o acoplado em R4) |
| registro derivado | `MotorFrutas.informacoes` (tick, fruta, conteúdo, prazo) e `decisoes_com_informacao`, no `resumo_frutas` | `digilab/frutas.py` (#140) |

**O evento é causa externa, como toda ação do dono.** O que o pet faz com a informação é derivado pelo replay; nada da escolha do pet entra
no log (`digilab/events.py`).

**O que o dono diz e quando.**
- **Conteúdo binário:** "mal" se o efeito real da fruta no humor é negativo, "bem" caso contrário (fruta neutra = "bem").
- **O que ele sabe (E7):** o efeito real de cada fruta no mundo daquele genoma, o mesmo que o motor aplica. No `certo` diz a verdade; no
  `errado`, o contrário; no `acoplado` (seção 4.2), a verdade, fora de hora.
- **Frequência:** sobre **cada fruta oferecida, logo depois da oferta**. Como o calendário das ofertas sai da semente e é o mesmo em todos os
  braços (`OfertasFrutas` em `digilab/frutas.py`; `ConfigFrutas.horarios_oferta` 9h, 12h, 15h e 18h e `rotacao_ofertas`), `certo` e `errado` informam nos mesmos
  ticks, sobre as mesmas frutas, com conteúdo oposto.
- **Não é cuidado, não é contato, não é reforço** (D-A): não mexe no estado, não zera o tempo sem cuidado, não passa por `receber_acao_dono`,
  fica fora do orçamento (o canal das ofertas, B2). O dono principal do cuidado é o **atencioso** (E7), como no experimento maior.

## 3. Como a informação entra no aprendiz

**Pela percepção, por uma janela, nunca como reforço.** Quem reforça é a consequência (o sinal do P1 com a E2). A informação só muda o **peso
efetivo** de uma fruta na hora da escolha; o que a torna útil ou inútil é a consequência que vem depois.

- **Onde:** na **sub-decisão da fruta** (qual fruta comer), que com R2 passa a ter pesos no lobo de decisão. Cada fruta candidata recebe uma
  entrada a mais, **`info`**, igual ao valor de `Observacao.info_frutas` para ela (+1, −1 ou 0). A escolha entre comer ou não (a regra
  `fruta_no_cenario`) **não** lê a informação (decisão N5-2).
- **Um peso só para a entrada `info`, compartilhado entre as frutas** (decisão N5-3): o pet aprende "o que o dono diz vale ou não vale", não
  "o que o dono diz sobre a fruta b". É o que permite a informação **generalizar**: a mesma confiança vale para uma fruta que o pet nunca
  comeu, e é aí que a predição de eficiência (seção 6) tem de onde vir.
- **Peso inicial (confiança de partida, `w0_info`):** maior que zero, a calibrar (seção 8; decisão N5-1). Com `w0_info` = 0 a informação não
  teria efeito antes de o mundo a validar, e o P2e não teria como piorar no começo: a predição 4(a) do experimento maior não seria testável.
- **O mundo pode desmentir o dono:** o peso da `info` aprende pela mesma regra da L1 (`Aprendiz.atualizar_pesos`), creditado pelo sinal de
  consequência da decisão de comer. Para o P2e poder se recuperar, o peso precisa conseguir **cruzar o zero**: a calibração só usa valores
  com `w0_info` < `teto` (o teto da `ConfigLobos`, 1·S). Com o teto, o peso fica em [w0 − teto, w0 + teto], e o zero só está dentro se
  w0 < teto.
- **Sem informação, nada muda:** sem evento de informar, a entrada `info` vale 0 em toda decisão, `w × 0` soma 0 exato em inteiros, e o P2 é o
  P1 byte a byte (G2).

## 4. Braços e controles

Todos com o mesmo aprendiz (lobos com R2), o mesmo dono de cuidado (atencioso), o mundo **descasado** (a fruta de maior preferência inata faz
mal no humor; F5, F6) e as mesmas ofertas nos mesmos ticks. Só a fonte do sinal e a informação mudam.

| braço | sinal de aprendizado | informação | para quê |
|---|---|---|---|
| **P0** | nenhum (aprendizado desligado) | nenhuma | o piso: a predisposição herdada |
| **P1** | consequência (N3 + E2) | nenhuma | a referência do P2: só o mundo ensina |
| **P2** | consequência | `certo`, logo depois de cada oferta | o dono informa certo |
| **P2e** | consequência | `errado`, nos mesmos ticks | o dono informa errado; o mundo tem de refutar |
| **P2a** (acoplado) | consequência | `acoplado`: a mesma informação do P2, em momentos sorteados | separa **ter** a informação de tê-la **na hora** |

**"Só cuidado" acoplado** (D4, F7): para o P2 e o P2e, o registro da vida sem a informação e sem os sinais de ensino, com as mesmas ações de
cuidado e as mesmas ofertas nos mesmos ticks, rejogado em malha aberta (modo acoplado da bancada). É o controle do G5.

### 4.1 Mundo

Só o **descasado**. O casado com frutas e o mutável são do experimento maior; aqui a pergunta é se a informação ajuda a sair da predisposição
errada, e só o descasado tem predisposição errada (decisão N5-5).

### 4.2 O modo `acoplado` do informante (definição deste plano)

Para cada unidade, o P2a recebe **exatamente o mesmo multiconjunto de (fruta, conteúdo)** que o P2 daquela unidade recebeu, com o conteúdo
verdadeiro, mas em **ticks sorteados** uniformemente ao longo da vida, por uma rng própria (`derivar_semente("informacao-acoplada",
semente)`), consumida igual em todos os braços que a usam. A quantidade e o conteúdo são os do P2; só a **contingência** com a oferta some: a
informação muitas vezes chega sobre uma fruta que não está no cenário, ou expira antes de ela aparecer. É a "informação acoplada" de D-A.

## 5. Medidas

| medida | o que é | onde |
|---|---|---|
| **`taxa_fruta_ruim`** (primária) | fração dos consumos de fruta na fruta de efeito ruim, por janela (inicial: dias 1–7; final: dias 8–14) | `metrics.py` (R3) |
| **consumos até a metade do caminho** | consumos de fruta até o primeiro dia em que a `taxa_fruta_ruim` chega à metade do caminho entre o P0 da mesma unidade e 0, pela `eficiencia_amostral`; unidade que nunca chega conta com o total da vida (censura à direita, fração reportada) | `metrics.py` (já existe) |
| **trajetória de `w_info`** | o peso da entrada `info` no fim de cada dia; o dia em que cruza o zero (P2e) | `estado_interno()` dos lobos (R4) |
| **decisões com informação** | quantas escolhas de fruta tiveram informação vigente (o quanto a informação estava lá para ser usada) | `MotorFrutas.decisoes_com_informacao` (#140) |
| saúde média, tempo fora de privação, mortes | o canal de cuidado (G5) | `desempenho_no_ambiente` |
| humor médio | o efeito agregado das frutas | (amostrado como a saúde; R3) |
| G4 do aprendido, G6 (pesos no teto, razão da deriva) | quanto decide o aprendido; se o aprendizado ficou preso | como na L1 e no N3 |

## 6. Gates (PROPOSTOS)

Contrastes **pareados por unidade** (o mesmo pet, mesma semente e genoma, em braços diferentes). Δ = metade da distância entre a
`taxa_fruta_ruim` final do P0 e 0, medida na calibração (a regra da decisão E4 do experimento maior).

| gate | medida e contraste | passa se |
|---|---|---|
| **G1** | replay de toda vida, de todos os braços e acoplados | bit a bit |
| **G2** | P2 com a informação desligada (`ConfigInformacao.ligada` False ou nenhum evento de informar) contra o P1 | byte a byte |
| **G-EF** (eficiência) | consumos até a metade do caminho: P1 − P2 | positivo pelo teste da seção 7 |
| **G-PIORA** | `taxa_fruta_ruim` inicial: P2e − P1 | positivo pelo teste da seção 7 |
| **G-REC** (recuperação) | `taxa_fruta_ruim` final: P0 − P2e | positivo pelo teste da seção 7 |
| **G5** | P2 − P1 e P2e − P1 em saúde média e tempo fora de privação; mortes | IC 95% contém 0 nos dois, e mortes iguais nos três braços |

**Como ler G-PIORA e G-REC juntos:**
- **G-PIORA passa e G-REC passa:** o pet seguiu o dono errado e o mundo o corrigiu. O "mundo valida ou refuta" da arquitetura se sustenta com
  este aprendiz.
- **G-PIORA passa e G-REC refuta** (IC 95% de P0 − P2e inteiro abaixo de 0, ou IC 90% inteiro dentro de (−Δ, +Δ)): o pet obedece ao dono
  contra o mundo. O diagrama **não se sustenta** com este aprendiz; isso é registrado como resultado, não como falha de execução.
- **G-PIORA falha:** a informação não teve efeito inicial; G-REC não informa nada sobre correção (não houve o que corrigir).

**Descritivos (sem gate):**
- **P2 − P2a**, em G-EF e na `taxa_fruta_ruim`: quanto da vantagem do P2 vem de a informação chegar na hora.
- **P2 − P0** e **P1 − P0** na `taxa_fruta_ruim` final.
- O dia em que o `w_info` do P2e cruza o zero, e a fração de unidades em que cruza.
- G4, G6 e o "só cuidado" acoplado.

## 7. Estatística

- **Unidade:** a vida de um par (genoma, semente) num braço. As unidades de uma mesma semente-base ficam juntas no bootstrap (a variância do
  ambiente domina: E1, dono × ambiente 22%, `artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json`).
- **"Positivo pelo teste":** p unilateral na direção predita pelo bootstrap sobre unidades (`metrics.bootstrap_ic`, com as reamostragens, a
  semente e o nível do `PROTOCOLO_ARENA_V1`: a proporção das médias reamostradas do lado oposto de 0), abaixo do limiar de **Holm** sobre a
  família {G-EF, G-PIORA, G-REC}, α = 0,05. O teste t pareado é conferência.
- **G5** usa IC 95% bilateral (é teste de "não há diferença", lido junto com as mortes).
- Tudo fora da família é descritivo.

## 8. Calibração (12101, 12202, 12303, 12404, 12505)

**O que se calibra: só `w0_info`**, a confiança de partida.

- **Grade (PROPOSTA):** `w0_info` ∈ {S/4, S/2, 3S/4}, em unidades do S dos lobos (2¹⁰). Todos abaixo do teto (1·S), para o zero ficar ao
  alcance (seção 3). `w0_info` = 0 roda junto, como referência descritiva, fora da escolha.
- **O resto fica como está:** o aprendiz no ponto da L1 (passo 512, teto 1024), o ganho do sinal de consequência do N3 (4), a E2 como o chat
  B implementar, a janela de 240 min, as frutas com os padrões da `ConfigFrutas` (ou os da recalibração do `w_fruta`, decisão N2 da rodada 4,
  se ela entrar antes; o que estiver na `main` na hora da calibração vale para a validação).
- **Regra de escolha (registrada agora):** o **menor** `w0_info` em que a informação tem efeito: P2e − P1 na `taxa_fruta_ruim` inicial com o
  limite inferior do IC 95% acima de 0 (o pet usa a informação, para o bem e para o mal). Empate ou nenhum: o de maior limite inferior desse
  IC, e o relatório diz que a calibração não fechou. G-EF e G-REC **não** entram na escolha (são o que a validação testa).
- **Δ** sai da calibração, pela regra da seção 6.

## 9. Validação (13101, 13202, 13303, 13404, 13505), uma vez

- Com o `w0_info` escolhido, o Δ e o número de unidades do **adendo** (seção 10), commitados neste arquivo antes da run.
- Análise única, sem olhada intermediária. Refeita do zero, com sementes novas registradas antes, só por erro de execução, nunca pelo resultado.
- Falha registrada não para a V2 (decisão de 2026-10-01).

## 10. Unidades e tamanho da amostra

- **Unidades derivadas** das sementes reservadas (a regra E3 do experimento maior): semente da unidade k da base b =
  `derivar_semente("n5", b, k)`; genoma `derivar_semente("n5-genoma", b, k)`; o mesmo K em todas as bases.
- **K da calibração (PROPOSTO):** o mesmo da calibração do experimento maior, quando a bancada de frutas (R3) o fixar; se o N5 calibrar antes,
  K = 4 por base (20 unidades), só para estimar a variância.
- **K da validação:** pela regra da seção 7.2 do plano do experimento maior: N = ((z₁₋α + z₀,₈) × σ_d / Δ)² por contraste da família, com α do
  passo mais exigente de Holm (α/3), poder 0,8; o maior N dos três, arredondado ao múltiplo de 5; conferido por simulação com as unidades da
  calibração. Entra no adendo.
- **Por quê:** a análise de poder da v1 mostrou que a variância entre unidades domina (ICC 0,745; com M = 100 partidas, só 0,34% da variância
  do estimador vinha das partidas: `artifacts_poder/variancia.json`, `neutra.A`), e a L1 com 5 sementes deu ao braço que aprende um IC de
  0,532 a 0,734 no acerto (`artifacts_v2_l1/validacao/ponto/tarefa.json`). Mais unidades, não vidas mais longas.

## 11. Riscos registrados antes

1. **O pet come pouca fruta.** No N4, p(comer | fruta no cenário) não passou de 0,189 em nenhum ponto da calibração
   (`artifacts_v2_n4/calibracao/varredura.jsonl`, `resumo.p_comer`, máximo com `w_fruta` 6), e na validação houve de 4 a 24 escolhas com duas frutas ou mais por vida (`artifacts_v2_n4/validacao/`).
   Com poucas escolhas, a informação tem poucas chances de agir e G-EF pode sair censurado em muitas unidades. A fração censurada é
   reportada por braço; se passar de metade das unidades num braço, G-EF é lido como **inconclusivo por exposição**, não como refutado.
2. **O teto dos pesos.** No N3, 20 de 20 vidas prenderam peso no teto (`artifacts_v2_n3/validacao/`); na L1, 12 de 20. Se o `w_info` do
   P2e bater em w0 − teto antes de cruzar o zero, a recuperação fica impedida pelo teto, não pelo mundo. A fração de vidas com `w_info` no
   teto é reportada; G-REC refutado com `w_info` preso no limite é lido como **limitado pelo teto**. A revisão do teto é decisão pendente do
   Matheus e fica fora deste nó.
3. **Ofertas de uma fruta só.** Com uma fruta no cenário, a informação não muda a escolha (ela não entra em comer ou não, N5-2): o efeito só
   pode vir das ofertas com duas frutas ou mais (os conjuntos da `rotacao_ofertas` com duas frutas ou mais). A taxa por tipo de oferta é reportada.

## 12. Fora deste plano

O código (R1–R4), o casado e o mutável (experimento maior), o feedback do dono no P2 (o P3 é outro braço), a informação na escolha de comer ou
não, informar sobre outra coisa que não fruta, a web, humanos.

## 13. Decisões que só o Matheus pode tomar

**Decididas pelo Matheus em 2026-10-04: todas como recomendadas (N5-1 a N5-8).** Correção do coordenador na mesma data: o calendário
de ofertas igual entre braços é o `CalendarioFrutas` da bancada (#144), não o `OfertasFrutas` do N4, que depende do sono do pet.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| N5-1 | Confiança de partida `w0_info` > 0, calibrada na grade {S/4, S/2, 3S/4} pela regra da seção 8, com 0 como referência | Sim | Com 0, a informação não age antes de o mundo validar e o P2e não piora: a predição 4(a) do experimento maior não fica testável; acima do teto, o P2e nunca se recupera por construção |
| N5-2 | A informação entra só na sub-decisão da fruta (qual comer), não na escolha de comer ou não | Sim | Na escolha de comer, a informação passa a mexer no consumo total, e o efeito pode vir de comer menos fruta (nutrição, canal de cuidado), não de escolher melhor |
| N5-3 | Um peso só para a entrada `info`, compartilhado entre as frutas | Sim | Com um peso por fruta, a informação não generaliza, o pet precisa provar cada fruta para confiar no dono sobre ela, e o P2 vira o P1 com rótulos: G-EF perde o mecanismo |
| N5-4 | O acoplado (P2a) = o mesmo multiconjunto (fruta, conteúdo) do P2, com conteúdo verdadeiro, em ticks sorteados por rng própria | Sim | Com conteúdo sorteado, o acoplado mistura "fora de hora" com "às vezes errado" e o contraste P2 − P2a não isola a contingência |
| N5-5 | O N5 roda só no mundo descasado; casado e mutável ficam para o experimento maior | Sim | No casado a informação certa coincide com a predisposição e não há o que medir; rodar os três dobra o custo sem gate novo |
| N5-6 | Família de Holm = {G-EF, G-PIORA, G-REC}; G5 bilateral fora da família | Sim | Sem correção, uma das três passa por acaso com probabilidade alta; com G5 dentro, um teste de "não diferença" entra numa família de testes de diferença |
| N5-7 | Leituras "inconclusivo por exposição" (G-EF com mais da metade censurada) e "limitado pelo teto" (G-REC com `w_info` preso) registradas antes | Sim | Sem elas, um resultado negativo vindo de pouca fruta comida ou do teto seria lido como "a informação não ajuda" ou "o mundo não corrige" |
| N5-8 | A janela de 240 min fica como está (PROPOSTO), sem calibrar | Sim | Calibrar a janela junto com o `w0_info` dobra a grade e mistura duas alavancas na mesma escolha |
