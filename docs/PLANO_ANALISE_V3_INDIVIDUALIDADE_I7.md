# PLANO DE ANÁLISE V3 — INDIVIDUALIDADE, I7: o desenvolvimento contrafactual (2026-11-10, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-10 ("Aprovo todas").** As decisões IR-1 a IR-9 (seção 11) estão DECIDIDAS, todas pela
recomendação. **Nenhuma conta do I7 roda antes de cinco coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus" (feito);
2. o I5a na `main` (o #751, `f628105`): o I7 usa os perfis de hábito do `digilab/metrics.py` (feito);
3. o código do I7a na `main` (seção 9), com os testes e a trava;
4. a fumaça do orquestrador com as sementes dos testes (101…505), com o custo medido;
5. o registro da análise (seção 10), num commit empurrado antes da primeira vida.

**De onde vem:** a conversa de 2026-11-10 sobre como tirar da frente um achado e não só uma implementação organizada. Dela saíram as
perguntas Q1 a Q4, e o Matheus escolheu começar pela Q3, o desenvolvimento contrafactual ("Segue a recomendação").
- **Por que esta pergunta:** o motor é determinístico e guarda o log. Dá para viver de novo a vida de um pet com uma única coisa diferente
  num dia escolhido, com o mesmo mundo, o mesmo dono e a mesma história até ali, e medir o quanto o pet de dias depois se afasta do
  original. Num animal isso não se faz, porque o mesmo indivíduo não vive duas vezes.
- **A regra da IN-7 e da D-C2-4-2 vale:** nenhum mecanismo novo no P2. O I7 é uma medida, feita com perturbações que o motor já tem.

**O que a biologia diz e o que este plano usa dela:**
- **Stamps e Groothuis (2010),** *Biological Reviews*, VERIFICADA: a personalidade animal se desenvolve na interação entre o estado
  inicial e a experiência.
- **Pigliucci, Murren e Schlichting (2006),** *J. Exp. Biol.*, `10.1242/jeb.02070`, VERIFICADA quanto aos metadados e ao resumo: a
  canalização e a assimilação genética.
- **O uso aqui:** elas dão o vocabulário das hipóteses rivais (seção 1). Nenhuma delas mede o que o I7 mede, e a comparação com animais
  não é direta. A leitura do caos determinístico como hipótese de personalidade é SEM FONTE.

**O que este plano não afirma:** que o pet tem um período sensível no sentido da biologia, que a medida é canalização no sentido de
Waddington, nem que o modular supera o A. Os nomes das hipóteses são os nomes das leituras. **Nenhuma alegação de novidade:** a busca
dirigida (perturbação contrafactual e canalização em agentes que aprendem) não foi feita, e até ela nada se diz sobre ser o primeiro.
Todos os números novos deste plano são PROPOSTOS e SEM FONTE como escolha.

## 0. O que existe hoje (os fatos que o desenho usa)

- **As vidas do I2** (#718), em `artifacts_v3_individualidade/vidas.tar.gz`: o log de cada vida, 2 braços (REL e REL+F) × 3 donos
  (atencioso, relapso, aleatório; o incoerente sai, D-IND-I2c-2) × 60 sementes da faixa 85101…85505, 14 dias no `comedouro`, com o
  orçamento de 16 por dia.
- **Viver é barato:** uma vida de 14 dias pelo `run_v2_memoria_autobio.viver`, sem a bateria das sondas, levou 1,2 s (REL e REL+F, dono
  atencioso, semente 101, medido nesta sessão, em 2026-11-10; uma medida só, sem artefato em disco: a fumaça do I7a mede de novo e grava).
  O I2 levou 81 s por vida por causa da bateria.
- **O dono reage ao pet:** a vida é o laço do `simular_vida_fisico` (`experiments/bancada/regras_mundo.py`). A cada passo de 15 ticks o
  motor avança, o dono olha o estado e decide, com a rng `derivar_semente("dono", semente, dono)`. Por isso o ramo é a vida **vivida de
  novo**, e não o log do I2 com um evento a mais: o dono do ramo responde ao pet do ramo.
- **A rng de política** é a `motor._rng_politica` (`digilab/engine.py`), trocada nas cópias pelas sondas do I1 sem tocar o `digilab/`.
- **O tapa** existe como gesto do dono (`AcaoUsuario.TAPA`) e é o susto das sondas. As vidas do I2 nunca recebem o tapa.
- **Os perfis de hábito do I5** (SEQ, LUGAR e HORA de um dia, com a distância de variação total) estão no I5a (#751), na seção do I5
  do `digilab/metrics.py`.
- **O registro de cada decisão:** o `decisoes_mundo` do `MotorMundo` dá o tick, a ação e a posição de cada uma das 96 decisões do dia.

## 1. A pergunta e as hipóteses rivais, escritas antes

**Q-I7: quando uma única coisa muda num dia da vida de um pet do modular, o pet dos dias seguintes volta a ser o mesmo, se afasta cada
vez mais, ou vira outro pet de vez? E a resposta muda com a idade em que a coisa acontece?**

As três hipóteses preveem resultados diferentes:

| hipótese | o que prevê | a leitura se ela vencer |
|---|---|---|
| **H-CAN, canalização** | a diferença do ramo cai com os dias depois da perturbação (γ < 0), e o pet com outro acaso continua mais perto do original que um gêmeo (Φ_A < 1) | a individualidade que existe é estável: vem do que é comum (o mundo, o dono, a história longa), e um evento não a muda |
| **H-AMP, o ciclo que se reforça** | a diferença cresce com os dias depois da perturbação (γ > 0), e a perturbação cedo afasta mais que a tarde (β < 0) | a história faz o indivíduo, e a idade importa: há uma janela cedo em que uma experiência pesa mais |
| **H-CAOS, sem estrutura** | o ramo vira um gêmeo logo no primeiro dia depois da perturbação (Φ perto de 1, γ perto de 0), em toda idade | o que parece individualidade é o acaso dos últimos dias; a história não deixa marca |

Um resultado misturado (por exemplo, a diferença cresce mas a idade não importa) se escreve como está, pelas frases da seção 7.

**A expectativa, escrita antes e sem gate:** E-I7. O I2 achou o R_pet baixo e o dono dominando; o adendo 1 achou as facetas no teto (192)
dentro do dono. Por isso a expectativa é a H-CAN no LUGAR e na HORA, e nenhuma diferença entre o REL e o REL+F (as facetas, no teto, não
reforçam nada).

## 2. O desenho

### 2.1 Os pets e as idades

- **Os pets (IR-1):** os 360 do I2 (2 braços × 3 donos × 60 sementes). Cada pet é vivido de novo com as mesmas sementes e as mesmas
  fábricas do `ma.viver`.
- **As idades (IR-3):** a perturbação no dia t ∈ {2, 4, 6, 8, 10} (o dia 1 é o do nascimento, como na `janela_dias`).
- **O momento:** a regra das sondas (`momentos` em `experiments/sondas_individualidade.py`): o passo do dono da primeira decisão acordada
  da vida a partir das 10 h do dia t, em até 8 h. Sem nenhuma, aquele (pet, t) fica sem ramo e é contado à parte.

### 2.2 Os ramos (por pet)

| ramo | o que muda | para quê |
|---|---|---|
| **N, o nulo** | nada: a vida vivida de novo pelo mesmo laço, com o embrulho do ramo ligado e sem perturbação | a conferência do instrumento: tem de sair igual ao log do I2, byte a byte |
| **G, o gêmeo** | a rng de política trocada no nascimento, por `derivar_semente("individualidade-i7-gemeo", semente, braço, dono)` | a régua: o mesmo mundo, o mesmo dono e o mesmo genoma, com outro acaso desde o começo |
| **A(t), o acaso** | a rng de política trocada no momento do dia t, por `derivar_semente("individualidade-i7-acaso", semente, braço, dono, t)` | quanto da história até t sobrevive a outro acaso dali em diante |
| **E(t), o evento** | um tapa no momento do dia t; a rng de política continua a mesma | quanto uma única experiência muda o pet |
| **E°(t), o evento em malha aberta** (IR-5) | o tapa no momento do dia t, e o dono repete os gestos do log original em vez de reagir (o log do I2 com o tapa inserido, rejogado) | quanto do efeito do evento passa pelo dono que reage |

**O embrulho do ramo** fica no orquestrador, em volta do dono (`DonoComLugar`): no passo do momento, ele aplica a perturbação no motor e
depois deixa o dono decidir. Nada no `digilab/`, no `engine.py`, no cérebro nem no `simular_vida_fisico` muda. O tapa entra no log
como gesto do dono, fora do orçamento, como o carinho do banheiro. A troca de rng não é evento do log (como nas sondas): o ramo A e o G
se refazem pelo log mais a descrição do ramo (o tick e o rótulo da rng).

### 2.3 O que entra de cada dia

Os três perfis do I5 (SEQ, LUGAR e HORA, `perfis_habito_dia`), sobre as decisões acordadas do dia. Um dia fora no I5 (menos de 16
acordadas) fica fora aqui também, no par em que ele aparece.

## 3. As medidas

### 3.1 A distância do ramo

Para o pet p, o ramo b, o perfil X e o dia d: **D_b(d) = TV(X do ramo b no dia d, X do original no dia d)**, a variação total do I5
(`distancia_tv`). O original é o ramo N, que é o pet do I2.

### 3.2 O afastamento Φ (IR-4)

**Φ_b(t) = Σ D_b(d) / Σ D_G(d)**, as somas sobre os pets do braço e sobre os dias d de t+1 a t+4 (a janela de quatro dias inteiros
depois do dia da perturbação). Φ = 0: o ramo é o original. Φ = 1: o ramo está tão longe do original quanto um gêmeo com outro acaso
desde o nascimento.
- **A razão é de somas, não média de razões,** porque um D_G de um dia pode ser 0.
- **O gêmeo é a régua certa:** ele tem o mesmo mundo, o mesmo dono e o mesmo genoma. Um estranho de outra semente misturaria o mundo.

### 3.3 As inclinações

- **γ_b, a trajetória:** a inclinação de mínimos quadrados de r_b(k) = Σ D_b(t+k) / Σ D_G(t+k) contra k = 1, 2, 3, 4 (os dias depois
  da perturbação), com as cinco idades juntas. γ > 0: a diferença cresce. γ < 0: ela some.
- **β_b, a idade:** a inclinação de Φ_b(t) contra t ∈ {2, 4, 6, 8, 10}, por dia de idade. β < 0: cedo afasta mais.

### 3.4 O efeito imediato (a condição da leitura do E)

**Φ_E⁰(t) = Σ D_E(t) / Σ D_G(t)**, no próprio dia da perturbação (as decisões depois do momento). Se o IC95 dele contém 0 em todas as
idades, o tapa não pegou, e a leitura do E é "o evento não mudou o dia", não a canalização.

### 3.5 O reencontro (descritivo)

O ramo E usa a mesma rng de política. Se o estado do pet volta a ser o do original, as decisões voltam a ser as mesmas. **O reencontro**
é a fração dos ramos E(t) cujas decisões do dia 14 (ação e posição) são todas iguais às do original. Entra só no descritivo, porque o
quanto a rng se gasta por decisão não foi conferido (a fumaça do I7a conta).

### 3.6 Os ICs

O bootstrap percentil sobre as sementes, 2 000 reamostras. A semente leva os três donos juntos, como no I5, e a rng é
`derivar_semente("individualidade-i7-boot", braço, perfil, medida)`. São 3 perfis × 2 braços, sem correção de multiplicidade, porque o
plano é de leitura e não de gate; a tabela diz isso ao lado.

## 4. Os contrastes secundários (descritivos, com IC)

- **As facetas, REL+F − REL:** ΔΦ_E, Δγ_E e Δβ_E. É o único mecanismo que se reforça já ligado num braço. Pelo adendo 1 (as facetas no
  teto), a expectativa é Δ perto de 0.
- **O dono que reage, E − E°:** ΔΦ = Φ_E − Φ_E°. Positivo: o dono que reage aumenta o efeito do evento. Negativo: ele amortece.
- **Por dono:** Φ_A, Φ_E, γ e β por dono (atencioso, relapso, aleatório), só no descritivo.

## 5. As conferências (falham alto)

- **G-I7-0, o nulo:** o log do ramo N de cada pet sai igual, byte a byte, ao log do mesmo pet no `vidas.tar.gz`, e o `decisoes_mundo` tem
  96 decisões por dia. Um nulo diferente para a run inteira: o instrumento está quebrado.
- **G-I7-1, o ramo se refaz:** cada ramo vivido duas vezes dá o mesmo log e as mesmas decisões (IR-6).
- **G-I7-2, o prefixo:** as decisões de cada ramo A(t), E(t) e E°(t) antes do momento são iguais às do original.
- **G-I7-3, o tapa:** o log de cada ramo E(t) tem exatamente um tapa a mais que o do original, no tick do momento.

## 6. O que a análise grava

`artifacts_v3_individualidade_i7/`:
- `meta.json`: o commit, os sha256 (o orquestrador, o `metrics.py`, o `vidas.tar.gz` lido) e o comando;
- `ramos.jsonl`: uma linha por (pet, ramo, idade), com o tick do momento, o sha256 do log e as conferências;
- `perfis.jsonl`: uma linha por (pet, ramo, idade, dia, perfil), com as contagens;
- `analise.json`: Φ, γ, β e Φ⁰ com os ICs, os contrastes da seção 4, o reencontro, os (pet, t) sem ramo e os dias fora;
- `custo.json`: o tempo por vida e por ramo.

## 7. A leitura

### 7.1 A tabela

Por braço e por perfil: Φ_A(t) e Φ_E(t) nas cinco idades, γ_A, γ_E, β_A e β_E, o Φ_E⁰, cada um com o IC95.

### 7.2 As frases que a leitura pode escrever

- **"a diferença do evento cresce com os dias"** só se o IC95 de γ_E ficar inteiro acima de 0; **"some com os dias"** só se ficar inteiro
  abaixo de 0;
- **"o evento cedo afasta mais que o tarde"** só se o IC95 de β_E ficar inteiro abaixo de 0 (e o inverso, se acima);
- **"a história até o dia t sobrevive a outro acaso"** só se o IC95 de Φ_A(t) ficar inteiro abaixo de 1;
- **"o ramo vira um gêmeo"** só se o IC95 de Φ ficar inteiro acima de 0,8 (IR-7);
- **a hipótese que vence:**
  - **H-CAN** se γ_E < 0 e Φ_A < 1 em todas as idades, pelos ICs;
  - **H-AMP** se γ_E > 0 e β_E < 0;
  - **H-CAOS** se Φ_A e Φ_E ficarem acima de 0,8 em todas as idades e γ_E não se distinguir de 0;
  - fora dessas, "nenhuma das três hipóteses descreve o X do braço sozinha", com a tabela;
- fora disso, "não se distingue de zero nesta análise" (ou de 1, para o Φ). Nada vira "o pet não tem história".
- **A condição do evento:** sem Φ_E⁰ acima de 0 em nenhuma idade, as frases do E não se escrevem, e a leitura diz "o tapa não mudou o dia".

### 7.3 A expectativa E-I7

Relida contra a tabela, sem nenhum ajuste.

## 8. O custo

Por pet: o N, o G, os cinco A e os cinco E vividos duas vezes (24 vidas de 1,2 s) e os cinco E° rejogados (5 replays de cerca de 3,1 s,
a medida da fumaça do I5a). São cerca de 45 s por pet, 4,5 h num processo e **cerca de 1 h 10 min com 4 processos** (V3-D8), para os
360. Estimativa SEM FONTE até a fumaça do I7a medir; ela vai no registro (seção 10). Se a fumaça der mais que o dobro, o registro diz e
a IR-6 volta ao Matheus antes da run.

## 9. As missões (cada uma num PR)

| missão | o quê |
|---|---|
| **I7-plano** | este documento (APROVADO) e as IR-1 a IR-9 |
| **I7a** | as medidas (Φ, as inclinações, o reencontro) no `digilab/metrics.py`, com testes contra casos feitos à mão; o orquestrador `experiments/run_v3_individualidade_i7.py`, com o embrulho do ramo, as conferências G-I7-0 a 3 e a trava (o cabeçalho APROVADO, o registro, no máximo 4 processos, nada por cima de uma pasta); a fumaça com as sementes dos testes |
| **I7b** | o registro, a run uma vez e a seção do I7 no `docs/RESULTADO_V3_INDIVIDUALIDADE.md` |

**A ordem:** o I7b roda depois do I5b, para ficar uma run de pesquisa por vez.

## 10. O registro da análise

Antes da primeira vida, numa seção nova no fim deste plano, ficam:
- o commit e os sha256 do orquestrador, do `metrics.py` e do `vidas.tar.gz`;
- o custo da fumaça por pet;
- o comando e a contagem da suíte do dia.

## 11. As decisões (DECIDIDAS pelo Matheus em 2026-11-10, todas pela recomendação; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **IR-1** | os pets | **os 360 do I2, vividos de novo com as sementes da faixa 85101…85505**, sem faixa nova; a linha da faixa em `experiments/bancada/faixas.py` ganha a fonte do I7 (feito no PR do plano) | uma faixa nova perde o laço com o I2 e o I5 (o original deixa de ser o pet já medido) e pede vidas de base novas; reusar exige o ok do Matheus, porque a linha da faixa diz "a run única" do I2 |
| **IR-2** | os braços | **o REL e o REL+F** do modular, como no I2; o cérebro A fica para a Q4 | o A agora pede vidas de base novas e uma faixa; sem ele, a frase vale só para o modular |
| **IR-3** | as idades | **os dias 2, 4, 6, 8 e 10**, com a janela de quatro dias depois | idades demais custam sem ganho; o dia 1 é do bebê ainda sem o laço com o dono; depois do dia 10 a janela de quatro dias não cabe nos 14 |
| **IR-4** | a régua | **o gêmeo G** (outra rng de política desde o nascimento) | um estranho de outra semente misturaria o mundo e inflaria o denominador, e todo Φ pareceria pequeno |
| **IR-5** | a malha aberta | **o E° entra**, só no descritivo (seção 4) | sem ele não se separa o pet do dono que reage; com ele, cinco replays a mais por pet |
| **IR-6** | a conferência do ramo | **todo ramo vivido duas vezes** (G-I7-1) | só numa amostra, a run fica cerca de 40 % mais barata, e um ramo que não se refaz passaria sem ser visto |
| **IR-7** | o limiar do "vira um gêmeo" | **0,8**, PROPOSTO, SEM FONTE | mais baixo, a H-CAOS ganha fácil; 1 exato nunca se afirma com IC |
| **IR-8** | o evento | **o tapa**, o susto das sondas | o carinho é um gesto que o I2 já tem todo dia, e mais um não seria uma experiência nova; a comida a mais mexe no corpo e no lugar ao mesmo tempo |
| **IR-9** | o perfil da leitura | **os três perfis do I5, cada um com as frases dele**, sem um primário | um primário escolhido agora seria escolhido sem o I5b; os três sem correção de multiplicidade pedem cautela na leitura, e a tabela diz isso |
