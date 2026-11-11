# PLANO DE ANÁLISE V3 — INDIVIDUALIDADE, I7: o desenvolvimento contrafactual (2026-11-10, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-10 ("Aprovo todas").** As decisões IR-1 a IR-9 (seção 11) estão DECIDIDAS, todas pela
recomendação. **Nenhuma conta do I7 roda antes de cinco coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus" (feito);
2. o I5a na `main` (o #751, `f628105`): o I7 usa os perfis de hábito do `digilab/metrics.py` (feito);
3. o código do I7a na `main` (seção 9), com os testes e a trava;
4. a fumaça do orquestrador com as sementes dos testes (101…505), com o custo medido;
5. o registro da análise (seção 10), num commit empurrado antes da primeira vida.

**O adendo 1 (seção 12) está DECIDIDO pelo Matheus em 2026-11-10** ("E daí a gente parte para seguir as recomendações", depois da conferência das
referências): uma quarta hipótese, a régua crua e a forma em U nas frases, e dois descritivos. Ele vale junto com as seções 0 a 11.

**O adendo 2 (seção 14) está DECIDIDO pelo Matheus em 2026-11-11** ("Aprova as recomendações e segue"): a pergunta "história ou sorteio" da 9.8 do resultado, com um ramo de sorteio
amarrado, em 360 pets novos. Ele não muda as seções 0 a 13; as AD2-1 a AD2-7 estão decididas pela recomendação.

**O adendo 3 (seção 16) está DECIDIDO pelo Matheus em 2026-11-11** ("Aprovo as questões e pode seguir com as recomendações"): o que separa o pet que absorve o tapa do que se afasta, descoberto nas vidas do
adendo 2 e conferido nas do I7b, sem vidas novas. Ele não muda as seções 0 a 15; as AD3-1 a AD3-6 estão decididas pela recomendação.

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

## 12. Adendo 1: a transição, a régua crua e a forma em U (2026-11-10, DECIDIDO, Claude Code, Opus 5.5)

**Status: DECIDIDO pelo Matheus em 2026-11-10** ("E daí a gente parte para seguir as recomendações"), as A1-1 a A1-5 pela
recomendação. Nada do I7 rodou: o I7a (o código) não começou, e nenhuma vida foi vivida. O adendo muda só as regras de leitura
(seção 7) e acrescenta medidas descritivas, antes do registro (seção 10).

**De onde vem:** a busca dirigida de 2026-11-10, que o cabeçalho dava como não feita. Ela está no vault, na nota
`DigiLab — Revisão de escopo/BUSCA_I7_CONTRAFACTUAL_2026-11-10.md`, seções 0 a 8.
- **A busca não muda o desenho:** a régua do gêmeo, a bifurcação de cópias exatas e a variação total já têm precedente em agentes e em
  redes que aprendem. Cada peça do I7 tem precedente separado, e o que sobra é a junção num pet com corpo, mundo e dono. Isso é uma
  contribuição de aplicação e de desenho, não de método. **A regra de não alegar novidade continua.**
- **As referências do adendo são cinza:** preprints de 2025 e 2026, conferidos nos metadados e no resumo, fora do
  `docs/referencias/referencias_verificadas.csv`. A conferência das 29 referências recentes e o texto completo dos cinco mais próximos
  estão nas seções 9 e 10 da nota do vault: todas existem, nenhuma foi retratada, e as ressalvas abaixo vêm do texto completo.
  - **Kwok, Altıntaş, Raffel e Rolnick (2025),** arXiv:2506.13234, ICML 2025: a mesma perturbação deixa menos divergência final quanto
    mais tarde é aplicada. **Três ressalvas:**
    - depois de aplicada, a divergência sempre cresce, então a fase tardia não é canalização no sentido de Waddington, só "a mesma bacia";
    - os autores negam que a divergência cresça de forma exponencial, e "caos" só cabe entre aspas;
    - os modelos são supervisionados, sem agente e sem a régua de outra semente.
  - **Igarashi (2026),** `10.5281/zenodo.21439958`, preprint, um autor só (Kimiyasu Igarashi): gêmeos exatos bifurcados de um agente que
    aprende em vida só ficam diferentes de forma persistente quando as ações mudam o mundo e a consequência volta para o agente. Com o
    agente congelado, não.
  - **Speck e Shepard (2026),** arXiv:2608.19168, preprint: um único exemplo contra um gêmeo sem ele. O efeito some do desempenho, mas o
    deslocamento dos pesos continua mensurável.
- **Ali Nasser, Harel e Stern (2023),** *eLife*, `10.7554/elife.84312`, revisado por pares: em *C. elegans*, a fome precoce pesa nas
  fases inicial e tardia e é amortecida nas intermediárias. É o precedente biológico da forma em U (A1-3).
- **Duas cautelas para o Φ** (vault, seção 9):
  - em Qin (2026), uma história inteira diferente rendeu só 1,14 vez a distância entre sementes, então um Φ pequeno para um único tapa
    é o esperado, e não um defeito da medida;
  - um D_G perto do teto da variação total satura a régua. A régua crua (12.2) mostra o D_G em nível e deixa ver isso.
- **O I5b** (o #768) é contexto, não motivo: o pet varia 0,34 a 0,50 de um dia para o outro, e o dono separa os pets (D-IND-I5b-1).

### 12.1 A quarta hipótese, H-TRANS (A1-1)

| hipótese | o que prevê | a leitura se ela vencer |
|---|---|---|
| **H-TRANS, caos cedo e canalização depois** | o outro acaso cedo faz do ramo um gêmeo, e o mesmo acaso tarde não: Φ_A cai com a idade (β_A < 0), sem a diferença crescer com os dias (γ_E não positivo) | a história só começa a pesar depois de uma idade: antes dela o pet é o acaso, depois dela ele é o que viveu |

**A regra (soma-se à seção 7.2):**
- **H-TRANS** vale se:
  - o IC95 de Φ_A(2) ficar inteiro acima de 0,8 (IR-7);
  - o IC95 de Φ_A(10) ficar inteiro abaixo de 0,8;
  - o IC95 de β_A ficar inteiro abaixo de 0;
  - o IC95 de γ_E não ficar inteiro acima de 0.
- **A ordem:** quando as condições da H-TRANS valem, ela se escreve no lugar da H-CAN, porque as duas podem valer juntas e a H-TRANS é a
  mais específica. A H-CAOS e a H-AMP não valem junto com ela: a H-CAOS pede Φ_A acima de 0,8 em toda idade, e a H-AMP pede γ_E positivo.
- **O mesmo para o evento, só no descritivo:** Φ_E(2), Φ_E(10) e β_E, lidos do mesmo jeito, sem frase.

**Por que é escrita antes:** com as regras de hoje, esse resultado cai em "nenhuma das três hipóteses descreve sozinha". É verdade, mas
perde o padrão que Kwok et al. (2025) descrevem em redes supervisionadas: a mesma perturbação pesa menos quanto mais tarde.

**O que a H-TRANS não afirma:** que a fase tardia é canalização no sentido de Waddington, nem que a fase cedo é caos no sentido
matemático. "Caos cedo" quer dizer que o ramo vira um gêmeo, e "canalização depois" quer dizer que ele fica abaixo do gêmeo. Os nomes
são os da leitura, como na seção 1.

### 12.2 A régua crua (A1-2)

Φ e γ são razões contra o gêmeo. **Se o D_G muda com a idade ou com os dias, a razão muda sem o ramo mudar.** Um D_b parado com o D_G
crescendo, por exemplo, dá γ < 0, e isso pareceria canalização.
- **As medidas novas:** γ_b^cru é a inclinação de Σ D_b(t+k) contra k = 1 a 4, e β_b^cru é a inclinação de Σ_{d=t+1..t+4} D_b(d)
  contra t, as duas sem dividir pelo gêmeo. O gêmeo tem as dele, γ_G^cru e β_G^cru. Todas levam o IC95 pelo bootstrap da seção 3.6.
- **A regra (soma-se à seção 7.2):** as frases do γ ("cresce", "some") e do β ("cedo afasta mais") só se escrevem quando o IC95 da
  inclinação crua do mesmo ramo também ficar inteiro do mesmo lado de 0. Se a razão passa e a crua não, a frase é "a inclinação vem da
  régua: o D_b cru não se distingue de parado", e a hipótese que pede aquela inclinação não se declara.
- **A tabela (soma-se à seção 7.1):** o Σ D_b e o Σ D_G crus por idade e por dia depois da perturbação.

### 12.3 A forma em U (A1-3)

O β é uma reta. Um Φ(t) que desce e sobe (U), ou o contrário (∩), dá β perto de 0 e esconde o efeito da idade.
- **A medida nova:** as diferenças Φ_b(2) − Φ_b(6) e Φ_b(10) − Φ_b(6), com o IC95 pelo mesmo bootstrap.
- **A regra:**
  - se as duas diferenças ficarem com o IC95 inteiro acima de 0, a forma é U; se ficarem inteiro abaixo de 0, é ∩;
  - com U ou ∩, as frases do β não se escrevem, e a H-AMP e a H-TRANS não se declaram;
  - a leitura escreve então "o afastamento muda com a idade sem ser em linha (U)", ou "(∩)";
  - a H-CAN e a H-CAOS não usam o β e não mudam.

### 12.4 A expectativa da malha fechada (A1-4)

**E-I7b, escrita antes e sem gate:** Φ_E > Φ_E°, isto é, o dono que reage aumenta o efeito do tapa (ΔΦ > 0, seção 4). Ela vem de
Igarashi (2026), com uma diferença de desenho que se diz ao lado: lá a malha aberta é o agente congelado, e aqui é o dono que repete o log,
com o pet ainda aprendendo. Esse E° não tem par nos trabalhos lidos. A expectativa é relida contra a tabela, sem ajuste.

### 12.5 Dois descritivos (A1-5)

Os dois ficam só no descritivo, sem frase de leitura.
- **O estado interno contra o gêmeo:** Φ_b^est é a mesma razão de somas da seção 3.2, sobre uma distância entre o `estado_interno` do ramo
  e o do original no fim de cada dia. Ele mede se o evento some do comportamento e fica no cérebro, como no Speck e Shepard 2026.
  - **A distância exata** (quais campos, e como normalizar) é escrita pelo I7a no `digilab/metrics.py`, com teste, e entra no registro
    antes da run. Até lá, ela é PROPOSTA.
- **O efeito comum do tapa:** C_E(t) = TV(o perfil somado de todos os ramos E(t) do braço, o perfil somado de todos os originais) / a média
  dos D_E dos pets, por perfil e por dia.
  - Perto de 1: o tapa empurra todos os pets para o mesmo lado.
  - Perto de 0: cada pet muda para um lado, e o efeito é individual.

### 12.6 O que muda no resto do plano

- **Seção 6:** o `analise.json` ganha as inclinações cruas, as diferenças do U, o Φ^est e o C_E, e o `ramos.jsonl` ganha o sha256 do
  `estado_interno` do fim de cada dia.
- **Seção 9, o I7a:** as medidas novas vão para o `digilab/metrics.py`, com teste contra casos feitos à mão.
- **Seção 8, o custo:** não há vida a mais, porque o estado interno sai das mesmas vidas.

### 12.7 As decisões do adendo (DECIDIDAS pelo Matheus em 2026-11-10, todas pela recomendação; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **A1-1** | a H-TRANS | **entra**, com a regra da 12.1 | sem ela, o padrão "caos cedo, canalização depois" sai como "nenhuma das três"; com ela, há uma frase a mais declarada por quatro ICs sem correção de multiplicidade |
| **A1-2** | a régua crua | **entra como condição** das frases do γ e do β | sem ela, uma régua que se mexe fabrica uma H-CAN ou uma H-AMP; com ela, uma inclinação real e pequena pode deixar de ser escrita |
| **A1-3** | a forma em U | **entra**, com as duas diferenças | sem ela, um U vira "a idade não importa"; com ela, o Φ(6) pesa mais que as outras idades na leitura do β |
| **A1-4** | a E-I7b | **entra como expectativa**, sem gate | nenhum, porque é só escrita antes; sem ela, a leitura do E − E° fica sem expectativa |
| **A1-5** | o estado interno e o efeito comum | **entram só no descritivo**, com a distância do estado escrita pelo I7a | como leitura, pediriam regras sem base; fora do plano, perde-se o caso do evento que some do comportamento e fica no cérebro |

## 13. O registro da análise

Escrito em 2026-11-10 (Claude Code, Opus 5.5, branch `v3-individualidade-i7b`), antes da primeira vida do I7b, como a seção 10 manda.

- **O código:** o commit `3e22ad45` da `main` (o merge do #775, o I7a). O I7b não muda o código; este registro entra num commit próprio,
  empurrado antes da run.
- **Os sha256:**
  - o orquestrador `experiments/run_v3_individualidade_i7.py`: `ddbdab3b293038bda548514570bc266648b2dd478b717acaeb3473069731e7f2`;
  - o `digilab/metrics.py`: `cf2feb8fdeaa0abebb1dd6b43e449ca892ed5eb146c74db9578624235f49e93e`;
  - as vidas do I2, `artifacts_v3_individualidade/vidas.tar.gz`: `f07fb6ce2a5db78c494e34b00e364b12e08687b776d4bda5fc3d62e1409dd100`;
  - a config `experiments/configs/v3_individualidade/individualidade_i7.json`:
    `988ee4737679958364c954eecfbbe3faea4682f88404ccdad96179dcc306803a`.
- **O custo da fumaça** (as sementes 101 e 202, K = 1, 14 dias, 12 pets, 4 processos):
  - uma pet sozinha, num processo, levou 93 s (cada ramo, vivido duas vezes, cerca de 5 s);
  - a fumaça levou 12 min 20 s de parede, 62 s por pet com 4 processos, com a suíte inteira de outra sessão rodando ao lado;
  - a projeção para as 360 pets é de cerca de 6 h com 4 processos, contra 1 h 10 min da seção 8. Passou do dobro.
- **A IR-6 mantida:** levada ao Matheus pela seção 8, ela fica como está, todo ramo vivido duas vezes ("Sim, mantém e mergeia",
  2026-11-10).
- **A distância do estado interno (12.5) fixada:** a D-IND-I7a-4 do registro de 2026-11 (a fração das folhas do
  `estado_interno()["modulos"]` que diferem ou só existem num dos dois, no fim de cada dia; os `motivos` fora). PROPOSTA, SEM FONTE.
- **O comando:**

  ```bash
  python experiments/run_v3_individualidade_i7.py --config experiments/configs/v3_individualidade/individualidade_i7.json --processos 4
  ```

  A saída vai para `artifacts_v3_individualidade_i7/`, que não existe antes da run.
- **A suíte do dia** (`python -m pytest tests/ -q`, na branch `v3-individualidade-i7b` sobre `3e22ad45`): 5 249 passaram, 9 pulados e 3
  falharam, em 2 h 35 min (com outra run ao lado). As três falhas são das listas do G2 de outras frentes e não tocam o I7:
  - `test_digibrain_etapa0.py::test_nada_fora_do_pacote_e_do_orquestrador_le_a_chave` e
    `test_digibrain_vidas.py::test_t_ponto_3_so_o_orquestrador_do_prototipo_monta_o_digibrain` pedem o `experiments/entradas_dc4.py`;
  - `test_redecidir_evento.py::test_g2_separado_nada_fora_do_pacote_e_do_orquestrador_le_a_chave` pede o
    `experiments/auditoria_pet_vivo.py`.

## 14. Adendo 2: história ou sorteio (2026-11-11, DECIDIDO, Claude Code, Opus 5.5)

**Status: DECIDIDO pelo Matheus em 2026-11-11** ("Aprova as recomendações e segue"), as AD2-1 a AD2-7 pela recomendação. O Matheus pediu em 2026-11-11 que a pergunta da 9.8 do `docs/RESULTADO_V3_INDIVIDUALIDADE.md` virasse um adendo a
este plano ("Escrever como adendo"), e não um I8. **Nada deste adendo roda antes de cinco coisas:**
1. as decisões AD2-1 a AD2-7 (14.9) decididas pelo Matheus e este cabeçalho marcado DECIDIDO (feito);
2. o I7b (o #786) na `main`;
3. a faixa da AD2-1 conferida pelo Gerente da V3 e posta em `experiments/bancada/faixas.py` com a fonte;
4. o código do I7c na `main` (14.8), com os testes e a fumaça medida;
5. o registro do adendo (14.7), num commit empurrado antes da primeira vida.

O adendo não muda nada das seções 0 a 13 nem a leitura do I7b, que fica como está.

**De onde vem:** o exploratório da 9.6 do resultado, que ficou fora do plano e foi feito depois da análise.
- **O tapa é tudo ou nada, pet a pet:**
  - em cerca de 2/3 dos ramos E, o comportamento volta inteiro ao do original já no dia seguinte, e o tapa fica só na `mem.autobio`;
  - em cerca de 1/3, o ramo se afasta nos quatro dias e chega perto de um gêmeo.
- **O que separa os dois grupos:** em 20 ramos relidos, 10 de cada grupo, a contagem `arb.sorteios` do fim do dia t separou os grupos
  em 18. A leitura proposta foi esta:
  - quando o tapa muda quantas decisões sorteiam (por exemplo, quando dispara o reflexo do sono, que decide sem rng), o fluxo da rng de
    política se desloca;
  - o resto da vida passa a ser outro acaso, e o pet vira quase um gêmeo, como no ramo A.
- **O porquê da leitura, no código:** o modular nos braços REL e REL+F tem uma única chamada à rng de política, a `rng.random()` do
  `M-ARB` (`digilab/digibrain/arb.py`). Ela é feita só quando a decisão tem dois candidatos ou mais e nenhum reflexo. A rng do braço EMB
  (`mem_emb`) não existe nesses dois braços.
  - Por isso, qualquer decisão que deixa de sortear, ou que passa a sortear, desloca todos os sorteios seguintes.
  - Isso é o motor funcionando como foi escrito, e não um defeito. A pergunta é o que esse deslocamento responde do I7.

**A pergunta, Q-AD2: a parte do efeito do tapa que dura vem do que o pet viveu (a história) ou do deslocamento do fluxo da rng (o
sorteio)?**

A resposta muda o que a frente pode dizer:
- se for a história, o I7 mediu experiência, e um tapa muda um pet em um terço das vezes;
- se for o sorteio, o I7 mediu sobretudo a sensibilidade do fluxo da rng. A individualidade que um evento deixa é então só a da `mem.autobio`,
  e a pergunta da Q-I7 fica por responder com o sorteio amarrado.

**O que este adendo não afirma:** que o sorteio é ruído e a história é sinal no sentido de um animal, nem que um pet com o sorteio
amarrado é mais real que o pet do jogo. O ramo amarrado é um instrumento de medida e não muda o motor. A regra da IN-7 vale: nenhum
mecanismo novo no pet. Todos os números novos deste adendo são PROPOSTOS e SEM FONTE como escolha, e não há alegação de novidade.

### 14.1 Os pets (AD2-1)

**360 pets novos:** os mesmos 2 braços (REL e REL+F), os 3 donos (atencioso, relapso, aleatório) e 14 dias no `comedouro`, com o
orçamento de 16 por dia, como no I2. As sementes vêm da faixa **88101…88505** (bases 88101, 88202, 88303, 88404 e 88505, K = 12, o
prefixo `digibrain_prototipo`).
- **A faixa** está livre no `FAIXAS_RESERVADAS` hoje. Ela entra na tabela com a fonte só depois do ok do Gerente da V3.
- **O original de cada pet** é a vida de base vivida pelo laço do dono, sem ramo, como na fumaça do I7a (`viver_fumaca`). Ela vai para
  `artifacts_v3_individualidade_i7_ad2/vidas.tar.gz`.
- **Por que pets novos:** a leitura do sorteio nasceu olhando as vidas do I7. Testá-la nas mesmas sementes seria testar a hipótese na
  amostra que a sugeriu. Os pets novos também repetem o ramo E do I7 numa amostra que ele não viu (14.5).

### 14.2 Os ramos (por pet)

| ramo | o que muda | para quê |
|---|---|---|
| **N, o nulo** | nada, vivido de novo com os gravadores ligados (14.3) | a conferência: sai igual à vida de base, byte a byte |
| **G, o gêmeo** | a rng de política trocada no nascimento, como na seção 2.2 | a régua do Φ |
| **E(t), o evento** | o tapa no momento do dia t, como na seção 2.2 | o efeito do tapa, repetido nos pets novos |
| **R(t), o evento com o sorteio amarrado** (AD2-2) | o tapa no momento do dia t, e cada decisão do ramo recebe o mesmo número sorteado que o original recebeu no mesmo tick | o efeito do tapa sem o deslocamento do fluxo |
| **R°, o amarrado sem evento** | o sorteio amarrado desde o nascimento, sem tapa | a conferência do amarrado: sai igual a N, byte a byte |
| **S(t), o deslocamento sozinho** (AD2-3) | no momento do dia t, um sorteio da rng de política é jogado fora, sem tapa | se deslocar o fluxo em um número basta para fazer um gêmeo |

As idades são as do I7: t = 2, 4, 6, 8 e 10, com a janela de quatro dias. **O A(t) e o E°(t) não entram (AD2-5):** o I7b já os mediu
nas 360 vidas do I2, e o Φ_A ficou de 0,96 a 1,00 em todas as células.

### 14.3 O sorteio amarrado

O amarrado fica no orquestrador, como o embrulho do ramo. Nada no `digilab/`, no `engine.py`, no cérebro nem no `simular_vida_fisico`
muda.
- **O gravador:** no ramo N, a rng de política do motor é trocada por uma subclasse de `random.Random` com a mesma semente. A subclasse
  devolve os mesmos números e grava cada `random()` com a chave (tick do motor, ordem da chamada no tick). A rng do dono, a que o laço
  passa ao `decidir`, ganha um gravador igual.
- **O amarrado:** no ramo R, a chamada com a chave (tick, ordem) devolve o número que o original gravou com a mesma chave.
  - **A chave que o original não tem** (o ramo sorteia onde o original não sorteou) recebe um número de uma rng própria, a
    `derivar_semente("individualidade-i7-amarrado", semente, braço, dono, t)`, na ordem em que essas chaves aparecem.
  - A fração dessas chaves vai no descritivo (14.5). Se ela for grande, o R não é "o mesmo sorteio", e a leitura diz isso.
  - Qualquer método da rng que não seja `random()` levanta erro, porque o braço não usa outro (`arb.py`).
- **A rng do dono também é amarrada (AD2-4):** se só a do pet fosse, um dono que passa a sortear num passo diferente deslocaria o fluxo
  dele, e a diferença do R ainda poderia vir de um sorteio. O dono continua reagindo ao pet: com o mesmo número e um pet diferente, ele
  pode decidir outra coisa, e isso conta como história.
- **O deslocamento do S:** no passo do momento, antes da decisão do pet, o embrulho chama `random()` uma vez na rng de política e joga o
  número fora. Nada mais muda.

### 14.4 As medidas e as hipóteses, escritas antes

As medidas são as da seção 3, sobre os pets novos: D_b(d), Φ_b(t) contra o gêmeo, a régua crua e o bootstrap da 3.6, com a rng
`derivar_semente("individualidade-i7-ad2-boot", braço, perfil, medida)`.

**A medida nova é a fração amarrada ρ = Σ D_R / Σ D_E**, a razão de somas sobre os pets do braço, as cinco idades e os quatro dias de cada
janela, por perfil.
- ρ = 0: amarrar o sorteio apaga o efeito do tapa, e o que durava era o deslocamento.
- ρ = 1: amarrar não muda nada, e o que dura é o que o pet viveu.
- ρ(t), por idade, vai só no descritivo.

| hipótese | o que prevê | a leitura se ela vencer |
|---|---|---|
| **H-SORT, o sorteio** | o IC95 de ρ inteiro abaixo de 0,2 | quase todo o efeito do tapa que dura vem do deslocamento do fluxo da rng; com o sorteio amarrado, o tapa fica na memória e quase não no comportamento |
| **H-HIST, a história** | o IC95 de ρ inteiro acima de 0,8 | o deslocamento quase não pesa; o efeito que dura é o que o pet viveu |
| **os dois pesam** | o IC95 de ρ inteiro entre 0,2 e 0,8 | uma parte vem de cada um, e a leitura dá ρ com o IC |

**As frases que a leitura pode escrever:**
- **a hipótese** de cada célula (braço × perfil), pela tabela acima. Um IC que cruza 0,2 ou 0,8 dá "ρ não se separa do limiar nesta
  análise", com o valor;
- **"deslocar o fluxo em um sorteio faz do pet um gêmeo"** só se o IC95 de Φ_S(t) ficar inteiro acima de 0,8 (IR-7) em todas as
  idades; **"não basta para um gêmeo"** só se ficar inteiro abaixo de 0,8 em todas;
- **"o efeito amarrado cresce com os dias"** pelas regras do γ da 7.2, com a régua crua da 12.2, para o ramo R;
- **a condição do evento:** a da 3.4, aplicada ao R. Sem Φ_R⁰ acima de 0 em nenhuma idade, a frase é "com o sorteio amarrado, o tapa não
  mudou o dia", e a H-SORT pode valer junto;
- fora disso, "não se distingue nesta análise". São seis células sem correção de multiplicidade, e a tabela diz isso, como no I7.

**A expectativa E-AD2, escrita antes e sem gate:** a H-SORT ou "os dois pesam" com ρ abaixo de 0,5, e Φ_S acima de 0,8. É o que o
exploratório da 9.6 sugere. Ela é relida contra a tabela, sem ajuste.

### 14.5 Os descritivos

- **O tudo ou nada:** a fração dos ramos E(t) e R(t) com D = 0 nos quatro dias da janela, com D > 0 nos quatro, e com os dois, por
  braço, perfil e dono. É a peça 1 do exploratório da 9.6, agora escrita antes. A leitura proposta lá prevê que a fração "D > 0 nos
  quatro" cai do E para o R.
- **A separação pelo sorteio,** nos ramos E(t), em todos e não em 20:
  - a contagem `arb.sorteios` e `arb.reflexos` do fim do dia t igual ou diferente à do original;
  - a tabela cruzada com o grupo do tudo ou nada.
- **A fração de chaves sem par** do R (14.3), por braço e por dono.
- **O Φ^est do R e do E**, a distância do estado interno da 12.5 (a D-IND-I7a-4), contra o gêmeo.
- **A réplica do E:** o Φ_E, o γ_E e o reencontro do dia 14 nos pets novos, ao lado dos números do I7b. Aqui não há frase: uma diferença
  entre as duas amostras se escreve como diferença, sem leitura.

### 14.6 As conferências (falham alto)

- **G-AD2-0, o nulo:** o log do N sai igual à vida de base byte a byte, com os gravadores ligados, e há 96 decisões por dia.
- **G-AD2-1, o amarrado sem evento:** o log do R° sai igual ao do N byte a byte, e nenhuma chave fica sem par. Um R° diferente do N quer
  dizer que o amarrado está quebrado, e a run para.
- **G-AD2-2, o ramo se refaz:** cada ramo vivido duas vezes dá o mesmo log e as mesmas decisões, como na IR-6 (AD2-6).
- **G-AD2-3, o prefixo:** as decisões de cada E(t), R(t) e S(t) antes do momento são as do original.
- **G-AD2-4, a perturbação:** o E(t) e o R(t) têm exatamente um tapa a mais que o original, no tick do momento. O S(t) não tem tapa, e o
  sorteio jogado fora acontece uma vez.

### 14.7 O que a análise grava, o custo e o registro

- **A pasta:** `artifacts_v3_individualidade_i7_ad2/`, com os mesmos arquivos da seção 6. O `analise.json` ganha o ρ, o Φ_S, o Φ_R e
  os descritivos da 14.5. O `ramos.jsonl` ganha a fração das chaves sem par de cada R.
- **O custo:** por pet, são 18 ramos (N, G, R°, e o E, o R e o S nas cinco idades), cada um vivido duas vezes, mais a vida de base. O I7b
  levou 27 s de parede por pet com 4 processos, com 17 ramos, dos quais 5 eram replays mais baratos. A estimativa é de **cerca de 3 h com 4
  processos** (V3-D8). Ela é SEM FONTE até a fumaça do I7c medir. Se a fumaça der mais que o dobro, o registro diz, e a AD2-6 volta ao
  Matheus antes da run.
- **O registro:** antes da primeira vida, numa seção nova no fim deste plano, ficam o commit e os sha256 do orquestrador, do
  `metrics.py` e da config, o custo da fumaça, o comando e a contagem da suíte do dia.

### 14.8 As missões (cada uma num PR)

| missão | o quê |
|---|---|
| **I7-adendo2** | este adendo e as AD2-1 a AD2-7 |
| **I7c** | o ρ no `digilab/metrics.py`, com teste contra casos feitos à mão; no orquestrador do I7, ou num irmão dele se o diff passar de um terço do arquivo, o gravador, o amarrado, os ramos R, R° e S e as conferências G-AD2-0 a 4; a trava, como a do I7, com a config da faixa 88101…88505; a fumaça com as sementes dos testes |
| **I7d** | o registro, a run uma vez e a seção do adendo 2 no `docs/RESULTADO_V3_INDIVIDUALIDADE.md` |

**A ordem:** o I7c só começa depois do I7b na `main`, e o I7d é a única run de pesquisa da máquina enquanto roda.

### 14.9 As decisões do adendo (DECIDIDAS pelo Matheus em 2026-11-11, todas pela recomendação; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **AD2-1** | os pets | **360 novos, da faixa 88101…88505**, com o ok do Gerente | nas vidas do I2, a run reaproveita o original e sai cerca de 3 % mais barata (uma vida de base a menos por pet), mas testa a hipótese na amostra que a sugeriu; com pets novos, o laço com o I2 e o I5 se perde, e o E repetido serve de ponte |
| **AD2-2** | o controle do sorteio | **o amarrado pelo tick** (14.3) | ressincronizar a rng só no fim do dia t deixaria o resto do dia do tapa com o fluxo deslocado e misturaria as duas coisas; amarrar pela ordem dos sorteios (o n-ésimo do ramo recebe o n-ésimo do original) é o fluxo de hoje, e não separa nada |
| **AD2-3** | o S(t) | **entra** | sem ele, a H-SORT diz que o deslocamento pesa, mas não se ele sozinho basta; com ele, são cinco ramos a mais por pet, cerca de 30 % do custo |
| **AD2-4** | a rng do dono | **amarrada junto** | só a do pet deixaria um resto de sorteio do dono dentro do ρ, e a H-HIST poderia ganhar por ele; amarrar o dono tira do ρ a parte do dono que vem do sorteio, mas não a que vem de ele reagir |
| **AD2-5** | o A e o E° | **saem** | sem eles, a malha aberta não se repete nos pets novos; com eles, são dez ramos a mais por pet para medidas que o I7b já deu |
| **AD2-6** | a conferência do ramo | **todo ramo vivido duas vezes**, como na IR-6 | só numa amostra, a run fica perto da metade, e um amarrado que não se refaz passaria sem ser visto |
| **AD2-7** | os limiares do ρ | **0,2 e 0,8**, PROPOSTOS, SEM FONTE; o 0,8 é o da IR-7 e o 0,2 é o espelho dele | mais estreitos, uma das duas hipóteses ganha fácil; mais largos, quase tudo cai em "os dois pesam" |

## 15. O registro do adendo 2

Escrito em 2026-11-11 (Claude Code, Opus 5.5, branch `v3-individualidade-i7d`), antes da primeira vida do I7d, como a 14.7 manda.

- **O código:** o commit `c9c56584` da `main` (o merge do #794, o I7c). O I7d não muda o código: este registro entra num commit próprio,
  empurrado antes da run, sobre os commits do registro de 2026-11 (a D-IND-I7c-1 confirmada e a D-IND-I7d-1).
- **Os sha256:**
  - o orquestrador `experiments/run_v3_individualidade_i7_ad2.py`: `a2b9170c3f6697409fcfef573a9ce74c9b3e2037dff29d41f1d40666ee23a7b4`;
  - o orquestrador do I7, que ele importa: `ddbdab3b293038bda548514570bc266648b2dd478b717acaeb3473069731e7f2` (o mesmo da seção 13);
  - o `digilab/metrics.py`: `af0762b501910dfb953e0eecafc5325c7644270aaec1b7fa886f3b31e58913e5`;
  - a config `experiments/configs/v3_individualidade/individualidade_i7_ad2.json`:
    `a6719dd18287627c0aaac3a11ac01868a94a0d28a62359cde7c6f90b9f14f2b5`.
- **O custo da fumaça** (as sementes 101 e 202, K = 1, 14 dias, 12 pets, 4 processos): 7 min 10 s de parede, 35 s por pet com 4 processos,
  136 s por pet dentro de cada processo. A projeção para as 360 pets é de cerca de 3 h 30 min, contra cerca de 3 h da 14.7: não passa do dobro,
  e a AD2-6 fica como está.
- **A faixa:** 88101…88505, na tabela desde o #794, liberada pelo Matheus sem o ok do Gerente (D-IND-I7d-1).
- **O comando:**

  ```bash
  python experiments/run_v3_individualidade_i7_ad2.py --config experiments/configs/v3_individualidade/individualidade_i7_ad2.json --processos 4
  ```

  A saída vai para `artifacts_v3_individualidade_i7_ad2/`, que não existe antes da run.
- **A suíte do dia** (`python -m pytest tests/ -q`, na branch `v3-individualidade-i7d` sobre `c06d5093`): 5 323 passaram, 9 pulados e 4
  falharam, em 2 h 11 min.
  - Três falhas são as listas do G2 de outras frentes, que já falham na `main` e não tocam o I7: duas pedem o
    `experiments/entradas_dc4.py`, e a do `test_redecidir_evento.py` pede o `experiments/auditoria_pet_vivo.py`.
  - A quarta, `test_credito_canal_etapa0.py::test_o_artefato_se_refaz_igual`, passou rodada sozinha logo depois (1 passed). Ela caiu com a
    máquina carregada por outro trabalho ao lado e não toca o I7.

## 16. Adendo 3: o que separa absorver de se afastar (2026-11-11, DECIDIDO, Claude Code, Opus 5.5)

**Status: DECIDIDO pelo Matheus em 2026-11-11** ("Aprovo as questões e pode seguir com as recomendações"), as AD3-1 a AD3-6 pela recomendação. O Matheus pediu em 2026-11-11 que a frente seguisse as recomendações da 10.6 do resultado ("faça o merge e siga com
as recomendações"). Este adendo é a primeira delas. **Nada dele roda antes de três coisas:**
1. as decisões AD3-1 a AD3-6 (16.7) decididas pelo Matheus e este cabeçalho marcado DECIDIDO (feito);
2. o código do I7e na `main` (16.6), com os testes e a fumaça;
3. o registro do adendo, numa seção nova no fim deste plano, empurrado antes da primeira leitura.

**De onde vem:** o adendo 2 (a seção 10 do resultado) mostrou que o tapa é tudo ou nada pela história, e não pelo sorteio:
- em cerca de 69 % dos ramos o pet volta ao original no dia seguinte;
- em cerca de 29 % ele se afasta nos quatro dias;
- a fração quase não muda com o sorteio amarrado.

O que decide o lado de cada pet não foi medido. O único sinal visto é descritivo: com o dono relapso, 43 % a 47 % dos ramos se afastam, contra
18 % a 27 % com os outros donos.

**A pergunta, Q-AD3: o que, no momento do tapa, separa o ramo que absorve o tapa do ramo que se afasta?**

**O que este adendo não afirma:** causa. Os candidatos são lidos no original, no momento do tapa, e a medida é de associação. Um candidato
que separa nas duas amostras é um bom suspeito para um desenho causal depois (por exemplo, o tapa dado só quando a condição vale). Não há
mecanismo novo no pet (IN-7). Todos os números novos são PROPOSTOS e SEM FONTE como escolha, e não há alegação de novidade.

### 16.1 As duas amostras (AD3-2)

- **A descoberta: as vidas do adendo 2** (os 360 pets da faixa 88101…88505), com os ramos E e os ramos R. O R mostra o efeito do tapa sem
  o deslocamento do sorteio, e o E é o tapa de sempre. Os dois entram como dois conjuntos, cada um com a sua tabela.
- **A confirmação: as vidas do I7b** (os 360 pets do I2, faixa 85101…85505), com os ramos E. São pets diferentes, com outras sementes. Até
  aqui, nenhum candidato foi lido nelas: o exploratório da 9.6 contou o tudo ou nada e o `arb.sorteios`, que não está entre os candidatos
  (16.3).
- **Nenhuma vida nova:** os candidatos saem do replay do log do original até o momento (o `copia_em` da bateria do I1). Os grupos saem dos
  `perfis.jsonl.gz` já gravados, que são artefatos locais com os sha256 nos `meta.json` das duas runs.

### 16.2 Os grupos (AD3-3)

Por ramo (o pet, o ramo e a idade t), a trajetória da janela de quatro dias no SEQ (a `trajetoria_janela`):
- **absorve:** D = 0 nos quatro dias;
- **se afasta:** D > 0 nos quatro;
- **misto:** fica fora, porque são 2 % a 3 % dos ramos.

O SEQ basta: um ramo com D = 0 num perfil tem as decisões do dia iguais às do original, e por isso D = 0 nos outros.

### 16.3 Os candidatos, escritos antes (AD3-4)

Todos são lidos no original, no tick do momento, antes do tapa. A divisão em dois níveis está escrita aqui e vale igual nas duas amostras.

| candidato | o que é | os dois níveis |
|---|---|---|
| **C-DONO** | o dono | relapso × os outros dois |
| **C-ENERGIA** | a energia do pet no momento | abaixo × acima da mediana da amostra de descoberta |
| **C-FOME** | a fome no momento | acima × abaixo da mediana da descoberta |
| **C-HUMOR** | o humor no momento | abaixo × acima da mediana da descoberta |
| **C-ACAO** | a ação do pet no passo do momento (`acao_atual`) | a mais comum na descoberta × as outras (a escolhida vai no registro antes da leitura da confirmação) |
| **C-IDADE** | a idade do tapa | t ≤ 4 × t ≥ 6 |
| **C-BRACO** | o braço | REL+F × REL |

- **A mediana** de cada drive é calculada uma vez na descoberta (o E e o R juntos, todos os ramos com grupo). Ela entra no registro antes
  da leitura da confirmação.
- **A medida:** para cada candidato, Δ = a fração "se afasta" no primeiro nível menos a fração no segundo. O IC95 vem do bootstrap sobre as
  sementes, com 2 000 reamostras e a rng `derivar_semente("individualidade-i7-ad3-boot", amostra, conjunto, candidato)`.

### 16.4 A leitura

- **"O candidato separa"** só se o IC95 do Δ ficar inteiro do mesmo lado de 0 na descoberta (nos dois conjuntos, o E e o R) e na
  confirmação (o E do I7b).
- **"Só na descoberta"** quando ele separa na descoberta e não na confirmação. A frase é "não se confirma nos pets do I7b".
- **Fora disso,** "não separa nesta análise".
- **O C-DONO** foi visto na descoberta antes deste plano. Para ele, a frase depende só da confirmação.
- **A multiplicidade:** são sete candidatos sem correção, e a exigência de repetir numa amostra independente faz esse papel. A tabela diz
  isso ao lado.

### 16.5 Os descritivos

- **A tabela cruzada** dos candidatos que separam, dois a dois, com a fração "se afasta" em cada célula, para ver se um explica o outro (por
  exemplo, se o relapso deixa o pet com fome no momento).
- **O efeito imediato:** a fração "se afasta" entre os ramos cujo D do resto do dia t foi 0 (o tapa não mudou o resto do dia) e entre os
  que não. Fica só no descritivo, porque é parte do efeito e não uma condição anterior a ele.
- **Os drives em nível:** a média e os quartis de cada drive nos dois grupos, por amostra.

### 16.6 A missão, o custo e o que se grava

- **O I7e:**
  - o leitor dos candidatos: o replay até cada momento, só de leitura, num orquestrador irmão do do adendo 2, sem tocar no `digilab/`;
  - o Δ e o bootstrap, e a regra da 16.4;
  - os testes contra casos feitos à mão e a fumaça com as sementes dos testes.
- **A leitura:** depois do registro, no mesmo PR do resultado.
- **O custo:** um replay até cada momento custa de 1 a 3 s. São cerca de 720 pets × 5 idades, perto de 30 min com 4 processos. É uma
  estimativa SEM FONTE até a fumaça.
- **A pasta:** `artifacts_v3_individualidade_i7_ad3/`, com:
  - o `meta.json`, com os sha256 dos artefatos lidos das duas runs;
  - o `candidatos.jsonl`, uma linha por ramo, com o grupo e os candidatos;
  - o `analise.json`.

### 16.7 As decisões do adendo (DECIDIDAS pelo Matheus em 2026-11-11, todas pela recomendação; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **AD3-1** | a forma | **um adendo ao I7** (a seção 16), como o adendo 2 | um I8 separado deixaria o plano do I7 mais curto, mas repetiria as medidas, as amostras e as regras que já estão aqui |
| **AD3-2** | as amostras | **a descoberta nas vidas do adendo 2 e a confirmação nas do I7b**, sem vidas novas | uma run nova com outra faixa daria uma confirmação limpa, a cerca de 2 h de vidas e com uma faixa a pedir; as vidas do I7b já foram olhadas no tudo ou nada (9.6), mas não nos candidatos |
| **AD3-3** | os grupos | **pelo SEQ, com o misto fora** | outro perfil daria quase os mesmos grupos; incluir o misto pediria uma terceira categoria para 2 % a 3 % dos ramos |
| **AD3-4** | os candidatos e as divisões | **os sete da 16.3, com as medianas da descoberta** | candidatos demais aumentam os falsos positivos na descoberta, e a confirmação os filtra; um candidato que fica de fora agora só volta num plano novo |
| **AD3-5** | a regra | **separar nas duas amostras, do mesmo lado**, sem correção de multiplicidade | uma correção (Bonferroni nos sete) deixaria a regra mais dura do que a repetição já deixa; sem a repetição, um achado da descoberta valeria sozinho |
| **AD3-6** | a causa | **fica para depois:** este adendo só mede associação | um desenho causal agora (o tapa só quando a condição vale) pediria vidas novas e um palpite de candidato sem dados |

## 17. O registro do adendo 3

Escrito em 2026-11-11 (Claude Code, Opus 5.5, branch `v3-individualidade-i7e`), antes da fase 1 do I7e, como a 16.6 manda.

- **O código:** o commit `442b12c2` (o I7e), sobre a `main` com o adendo 3 DECIDIDO.
- **Os sha256:**
  - o orquestrador `experiments/run_v3_individualidade_i7_ad3.py`: `7b3aa97767f26e1e0a338cf58f21ea581defeed231ea82e58639077afce9aa75`;
  - o do adendo 2, que ele importa (os grupos pelo `distancias_do_pet` com o perfil zerado fora):
    `b1768c4d91346ee739b702c73e4e19195b347e8b9f1ba05143597388d05bfc98`;
  - o `digilab/metrics.py`: `086ec5f4c2b26e1283926b3806aa4da3ff2918dfe5caeb108e7e4590b06dce57`.
- **Os artefatos lidos:** os sha256 dos `perfis.jsonl.gz`, dos `ramos.jsonl` e das vidas das duas amostras vão no `meta.json` da fase 1, e são
  os das runs do adendo 2 e do I7b, que não mudam.
- **A fumaça** (as vidas da fumaça do adendo 2, as sementes 101 e 202, usadas como as duas amostras): a fase 1 leu 120 momentos de 12 pets em 14
  s com 4 processos, e a fase 2 levou 2 s. A projeção para as 720 pets é de cerca de 15 min com 4 processos.
- **Uma leitura da 16.3 (D-IND-I7e-1):** a `acao_atual` no tick do momento é a ação da última decisão antes dele. O momento é a primeira
  decisão acordada da janela (a regra das sondas), então o C-ACAO quase sempre compara "estava dormindo até agora" com as outras. Na fumaça,
  a mais comum foi `dormir`.
- **Os comandos:**

  ```bash
  python experiments/run_v3_individualidade_i7_ad3.py --fase candidatos --processos 4
  python experiments/run_v3_individualidade_i7_ad3.py --fase leitura
  ```

  A saída vai para `artifacts_v3_individualidade_i7_ad3/`, que não existe antes da fase 1. Entre as duas fases, os níveis da descoberta entram
  nesta seção, num commit empurrado antes da leitura.
- **A suíte:** esta etapa não rodou a suíte inteira. A do dia é a da seção 15 (5 323 passaram). Os testes da frente estão no corpo do PR.

