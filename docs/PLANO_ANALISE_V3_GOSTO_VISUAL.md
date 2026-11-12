# PLANO DE ANÁLISE V3 — GOSTO_VISUAL, GV3: a run descritiva genoma × dono com a sonda das duas TVs (2026-11-11, Claude Code, Opus 5.5)

**Status: PROPOSTO, à espera do Matheus.** Todos os números deste plano são PROPOSTOS; as decisões GVP-1 a GVP-8 (seção 10) são dele.
**Nenhuma vida da faixa roda antes de quatro coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus" (o orquestrador confere);
2. a faixa 89101…89505 em `experiments/bancada/faixas.py` (já está, confirmada pelo coordenador, 2026-11-11);
3. o código da P1e na `main`: a segunda TV no motor, a sonda, as medidas em `digilab/metrics.py` e o orquestrador
   `experiments/run_v3_gosto_visual.py`, com a fumaça nas sementes dos testes (101…505);
4. o registro da run (seção 11) preenchido num commit empurrado antes da primeira vida.

**De onde vem:** a seção 7 e a linha P1e da `docs/ESPEC_GOSTO_VISUAL_P1.md`; a seção 5 da `docs/futuro/gosto_visual_pet.md` (a medida
em duas partes e a familiarização); as GV-5, GV-6 e GV-11. A frente é a `docs/TAREFA_V3_GOSTO_VISUAL.md` (a etapa GV3).

**Este plano é descritivo.** Não há gate, previsão com IC que decida nem contraste confirmatório. A run mede quanto da preferência entre
duas TVs que o pet nunca viu vem do genoma da visão e quanto vem do que o dono mostrou, no DigiBrain modular de hoje com o olhar (P1d). O
que ela devolve ao Matheus: a tabela das seis células, a parte do genoma, a parte do dono, a divergência entre as duas medidas e o custo.

**O que este plano não afirma:** que o pet "gosta", sente prazer ou tem um gosto estético. Agrado, escolha e tempo olhando são nomes de
medida (o vocabulário da F2, `docs/DEFINICOES_FRUTAS_V2.md`, 2.2). **Nenhuma alegação de novidade.**

**As referências** são só as da nota do vault `BUSCA_GOSTO_VISUAL_2026-11-10.md` que a espec e a proposta já citam (elas ainda não
estão nas tabelas `docs/referencias/*_verificadas.csv`: a GV-12 não foi feita). Elas sustentam a forma da medida, não os números: **todo
número deste plano é SEM FONTE**.

## 0. O que existe hoje (os fatos que o desenho usa)

- **A TV da vida** (P1c): um objeto na célula (4, 10), a 5 células do ninho, com a grade de quatro programas sorteados pela rng
  `tv-programas` (só depende da semente). O dono troca o canal com o evento `trocar_canal`, que vale até o fim do programa da grade.
- **O olhar** (P1d, D-GV-P1d-1): um comportamento do modular, entregue ao motor como o ocioso. O pet só olha a TV que já está no raio da
  visão (6 células), parado e acordado; não anda até ela. A opção de olhar dura uma decisão (15 ticks); o fim é o sorteio seguinte.
- **O que o cérebro sabe da TV antes de olhar:** só a linha da classe `tela` (a distância e a novidade da classe). O agrado do programa só
  entra depois de olhar, pelo termo `gosto` da unidade da TV que ele já olhava (D-GV-P1d-4) e pelo canal `gosto_visual` no r.
  **Consequência para a medida:** a primeira olhada entre duas TVs à mesma distância não pode ler o agrado; ela é sorteio (seção 7.3, E1).
- **O genoma da visão** (`digilab/genoma_visao.py`): o ótimo e a largura do pico por canal, rng `visao-ovo`. O genoma vazio (o ótimo em
  C/2 em todo canal) é o controle.
- **A segunda TV e a sonda** (P1e, esta etapa): o `MotorMundo.ligar_duas_tvs` (a `ConfigDuasTVs`, desligada) e a
  `experiments/sonda_duas_tvs.py`. A sonda só lê; o G2 está em `tests/test_gosto_visual_sonda.py`.
- **O custo:** uma vida de 14 dias com a sonda de 7 dias × 3 réplicas levou cerca de 16 s de parede numa semente de teste (medida única,
  sem artefato; o piloto mede o custo de verdade).

## 1. A pergunta, escrita antes

**Q:** depois de 7 dias com a TV da vida, entre duas TVs com programas que o dono nunca mostrou, (a) qual o pet olha primeiro e (b) que
fração do tempo olhando vai para cada uma; e quanto disso acompanha o agrado inato do genoma, quanto acompanha o programa que o dono pôs?

Não há hipótese herdada do `docs/PLANO_V2_PESQUISA.md`. As expectativas da seção 7.3 são escritas para serem conferidas, não para decidir.

## 2. O desenho

### 2.1 As unidades e os genomas

- **A unidade** (base, k) tem uma semente s = `derivar_semente("gosto-visual", b, k)` (o mundo, a grade da TV e a política) e um genoma
  g = `derivar_semente("gosto-visual-genoma", b, k)` (a regra E3, sem prefixo novo na bancada).
- **Dois genomas por unidade:** o **próprio** (`genoma_visao(g)`) e o **vazio** (o controle, igual em todas as unidades). Com o mesmo s,
  os dois vivem o mesmo mundo e a mesma grade; só o pico da visão muda.

### 2.2 A familiarização (GV-6): a duração e o critério

- **A duração:** os dias 0 a 6 da vida (7 dias, PROPOSTO, SEM FONTE). Nenhuma sonda antes do dia 7.
- **A medida da familiarização:** por dia, a fração das decisões acordadas em que o cérebro escolheu olhar a TV da vida.
- **O critério** (`metrics.familiarizacao_tv`): a média dos dias 5 e 6 difere da média dos dias 3 e 4 em no máximo **0,05** (PROPOSTO, SEM
  FONTE). A conta do número: o pet olha em poucas decisões por dia (na ordem de algumas em cerca de 60 acordadas), e a diferença de duas
  médias de dois dias com uma fração perto de 0,05 tem um erro-padrão binomial perto de 0,03; 0,05 é cerca de dois erros-padrão. Com 0,02,
  metade das vidas estáveis falharia só pelo ruído.
- **O que se faz com o critério:** a análise principal usa **todas** as vidas (a duração é a familiarização); a análise "só estáveis"
  repete tudo com as vidas que passam no critério (GVP-2). Se menos da metade das vidas passar, o resultado registra **"a familiarização
  não estabilizou em 7 dias"** como está, e as duas análises saem assim mesmo (o orquestrador marca `nao_estabilizou`).

### 2.3 Os donos

Três personas sintéticas, iguais no cuidado e diferentes só na TV (o desenho genoma × dono da espec, seção 7; a GV-22 deixa a companhia
fora):
- **o cuidado, igual nos três** (PROPOSTO, SEM FONTE; o dono do gabarito da P1f sem o tapa): a ração no comedouro a cada 3 horas e o
  carinho a cada 5 horas, se o pet está acordado;
- **`nenhum`**: nunca troca o canal (só a grade);
- **`calmo`**: a cada hora, se o programa da grade não é o dele, troca o canal para o programa da grade mais perto (L1) do perfil A da
  sonda (o menor índice no empate);
- **`agitado`**: o mesmo, com o perfil B.

Assim o `calmo` expõe o pet a um programa parecido com o A, o `agitado` a um parecido com o B, e o par da sonda continua novo: nenhum
programa da grade é igual a A ou B (a sonda confere).

### 2.4 A vida

O laboratório com o olhar (o REL da C4 com a subchave `olhar`, o mesmo do gabarito da P1f), o mundo do produto, o corpo do v11 com a tela
(`ConfigTela`), a TV do jogo (`ConfigTV`, fonte "grade"), o agrado só no sinal (`agrado_no_corpo` desligada, GVP-5), 14 dias. Cada
unidade vive seis vidas: 2 genomas × 3 donos. Toda vida é gravada, rejogada do disco (G1) e conferida.

## 3. A sonda das duas TVs (GV-11)

- **O momento:** nos dias 7 a 13, a primeira decisão acordada da vida real a partir das 10 h, até as 18 h (a regra das sondas da
  INDIVIDUALIDADE); sem nenhuma, o dia fica sem sonda.
- **A cópia:** o replay do log até o momento, com as fábricas da vida; três réplicas por dia (cópias profundas, a rng de política derivada
  `gosto-visual-politica`).
- **As duas TVs:** a TV da vida sai de cena; a TV A (id 2) passa o perfil A, C/5 em todos os canais, e a B (id 3) o perfil B, 4C/5 (PROPOSTO,
  SEM FONTE). As duas ficam a 3 células do pet, em direções opostas; a direção da A é sorteada pela rng própria `duas-tvs-posicao` (a
  semente, o tick e a réplica). Os perfis são simétricos em volta de C/2: no genoma vazio o agrado inato das duas é igual.
- **A janela:** 240 ticks (16 decisões), lida tick a tick (`MotorMundo.tv_olhada`).
- **O que a sonda grava:** a sequência das olhadas, os ticks em cada TV, a primeira, o agrado dos dois perfis no cérebro da cópia (o inato
  e o de agora, com a exposição), as decisões e as posições. O termo `gosto` fica fora da sonda (D-GV-P1d-4): ela só lê.

## 4. As medidas (moram em `digilab/metrics.py`)

### 4.1 Por réplica (`metrics.medidas_duas_tvs`), sempre separadas (GV-5)

| medida | conta | o que lê |
|---|---|---|
| **escolha** | 1 se a primeira TV olhada foi a A, 0 se foi a B; inválida se não olhou nenhuma | a direção (o agrado), se o cérebro pudesse lê-lo antes de olhar |
| **tempo relativo** | ticks na A / ticks nas duas; inválido se não olhou nenhuma | o interesse: a novidade, a habituação e o agrado misturados |
| **tempo total** | ticks nas duas / 240 | o efeito colateral (a TV virar o melhor lugar) |

O precedente das duas medidas separadas e da divergência entre elas é Gustafsson et al. 2021 (`10.3758/s13420-021-00484-3`); vários testes
binários em vez de muitas opções juntas, Pfefferle et al. 2025 (`10.3758/s13428-025-02668-5`); a familiarização, Hirskyj-Douglas e Webber
2021 (`10.1145/3493842.3493893`). As três são da nota do vault.

### 4.2 Por pet

A média de cada medida sobre as réplicas válidas dos 7 dias de sonda. O **agrado inato** do pet é Δ_I = agrado inato(A) − agrado inato(B)
(fixo na vida; o vazio tem Δ_I = 0). O agrado de agora, Δ_agora, é a média do mesmo contraste com a exposição; Δ_agora − Δ_I é a parte da
exposição no momento (descritivo).

## 5. A análise (descritiva; `experiments/run_v3_gosto_visual.py`, `analisar`)

O bootstrap reamostra **unidades inteiras** (a unidade leva as seis vidas), 2000 vezes (PROPOSTO, SEM FONTE), sementes
`derivar_semente("gosto-visual-boot", ...)`, IC95 percentil; as reamostras indefinidas ficam fora dos percentis e são contadas.

1. **As células** (5.1): por genoma × dono, a média das médias dos pets de cada medida, com o n e quantos pets ficaram sem sonda válida.
2. **A parte do genoma** (5.2): dentro de cada dono, nos genomas próprios, o Spearman entre Δ_I e a escolha média, e entre Δ_I e o tempo
   relativo médio, com o IC95.
3. **A parte do dono** (5.3): dentro da unidade e do genoma, as diferenças `calmo − agitado`, `calmo − nenhum` e `agitado − nenhum` na
   escolha e no tempo relativo; a média sobre as unidades com o IC95, separado no próprio e no vazio. O vazio é o dono sem o genoma.
4. **A interação** (5.4): (calmo − agitado no próprio) − (calmo − agitado no vazio), na mesma unidade.
5. **A divergência** (5.5): quantos pets têm a escolha e o tempo relativo de lados opostos de 0,5, e o Spearman entre as duas medidas por
   pet. A divergência é dado (o padrão de Gustafsson et al. 2021), não erro.
6. **As medidas sem variância** (5.6): se, numa célula, todos os valores de uma medida forem iguais, ela é registrada como "sem
   variância" e nenhuma correlação ou diferença dela é lida (um Spearman com um lado constante sai indefinido, e o bootstrap o conta).
7. **A repetibilidade** (5.7): o ICC(1) entre os pets das médias por dia (`metrics.icc1_estatisticas`), por genoma e medida; só o ponto,
   descritivo.
8. **O efeito colateral:** o tempo total na sonda e a fração olhando a TV da vida por dia, por célula.

## 6. As sementes, o tamanho e a máquina

- **A faixa:** 89101…89505, em `FAIXAS_RESERVADAS` (confirmada pelo coordenador, 2026-11-11). Ela não cruza as reservadas nem as queimadas
  (o teste confere); fica longe da 73xxx (fora do registro) e da 64xxx (queimada).
  - **89101…89202, o piloto:** as bases 89101 e 89202, K = 2 (4 unidades, 24 vidas). **Só** mede o custo e confere que o pet olha nas
    sondas; **nada se ajusta olhando para ele** (não há calibração neste plano: nenhum parâmetro é estimado). Se em menos de 1 réplica em
    cada 4 o pet olhar alguma TV (PROPOSTO, SEM FONTE), a run não roda e o caso volta ao Matheus com um adendo.
  - **89303…89505, a run:** as bases 89303, 89404 e 89505, K = 12 (36 unidades, 216 vidas), **uma vez**.
- **O tamanho** (PROPOSTO, SEM FONTE): 36 unidades por genoma × dono. É o K = 12 das runs da INDIVIDUALIDADE, por três bases; não há conta
  de poder (a run é descritiva).
- **A máquina (V3-D8):** no máximo 4 processos (o orquestrador recusa mais) e uma run de pesquisa por vez. Com cerca de 16 s por vida, a
  run cabe em cerca de 15 minutos com 4 processos (estimativa da fumaça, sem artefato).
- **A calibração separada da validação:** não se aplica, porque nada é calibrado; o piloto e a run usam sub-faixas separadas.

## 7. O que conta como resultado

### 7.1 A tabela

As seis células com as três medidas, a parte do genoma, a parte do dono, a interação, a divergência, a familiarização e o custo, na análise
principal (todas as vidas) e na "só estáveis".

### 7.2 As frases que a leitura pode escrever

- "**A parte do genoma aparece** no tempo relativo com o dono X": o IC95 do Spearman(Δ_I, tempo relativo) fica todo acima de 0.
- "**A parte do dono aparece** no genoma G": o IC95 de `calmo − agitado` no tempo relativo fica todo acima de 0.
- "**Não aparece com 36 unidades**": o IC95 contém 0. Nunca "não existe".
- Um IC95 todo **abaixo** de 0 é escrito como está ("o contrário do esperado") e não vira acerto.
- Nenhuma frase compara com animais, diz que o pet gosta ou diz que o modular supera o A.

### 7.3 As expectativas, escritas antes (para conferir, não para decidir)

- **E1:** a escolha média fica perto de 0,5 em todas as células, porque a primeira olhada não pode ler o agrado (seção 0). Se a escolha se
  afastar de 0,5 com o genoma, é um achado do mecanismo, e o achado é registrado.
- **E2:** o tempo relativo acompanha Δ_I no genoma próprio (o termo `gosto` segura o pet mais tempo na TV de agrado alto), com um efeito
  pequeno: o pet olha pouco e por poucas decisões seguidas.
- **E3:** a parte do dono é menor que a do genoma (a exposição tem teto S/8 e o pet olha pouco a TV da vida).

## 8. O negativo

Todo resultado negativo é registrado como está, no `docs/RESULTADO_V3_GOSTO_VISUAL.md`: nenhuma parte aparecer, a familiarização não
estabilizar, uma medida sem variância, o pet quase não olhar. Nada se reroda com outro número, outra janela, outro perfil ou outra faixa
para "achar" o efeito; uma mudança depois da run é um adendo novo, com faixa nova e o ok do Matheus. O piloto que falha a conferência da
seção 6 também é registrado.

## 9. As missões e a trava

1. **P1e (esta etapa, sem vida):** a segunda TV, a sonda, as medidas, o orquestrador, a fumaça nos testes e este plano. Um PR.
2. **O ok do Matheus** neste plano (a marca no cabeçalho) e nas GVP-1 a GVP-8.
3. **O piloto** (`experiments/configs/v3_gosto_visual/piloto.json`), com o registro da seção 11 preenchido antes.
4. **A run** (`experiments/configs/v3_gosto_visual/gosto_visual.json`), uma vez, e o `docs/RESULTADO_V3_GOSTO_VISUAL.md`.

O orquestrador só roda o piloto e a run com a marca "APROVADO pelo Matheus", a faixa em `FAIXAS_RESERVADAS`, a seção 11 presente, as bases,
o K e os 14 dias do plano, no máximo 4 processos e uma pasta nova. A fumaça (101…505) roda sem isso.

## 10. As decisões do Matheus (todas PROPOSTAS)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **GVP-1** | A escolha (a primeira olhada) como medida, sabendo que o cérebro de hoje não lê o agrado antes de olhar. | **Manter, como a espec pede, e lê-la como a conferência do sorteio (E1)**; o agrado se lê no tempo relativo. Uma memória do agrado por TV é mecanismo novo, fora desta etapa. | Ler a escolha como agrado daria uma "ausência de gosto" que é do mecanismo, não do pet. Trocar a medida agora muda a espec sem o mecanismo que a sustenta. |
| **GVP-2** | A familiarização: 7 dias e o critério 0,05; a análise principal com todas as vidas. | **Sim**, com a "só estáveis" ao lado. | Excluir pelo critério com poucos olhares por dia descarta vidas pelo ruído; não ter critério deixa a novidade da TV sem conferência. |
| **GVP-3** | Os perfis da sonda: A em C/5 e B em 4C/5 em todos os canais. | **Sim**: simétricos em volta do ótimo vazio, então o controle tem Δ_I = 0 por construção. | Perfis mais perto do meio dão Δ_I pequenos e nada se lê; perfis em todos os canais juntos não dizem qual canal pesa. |
| **GVP-4** | Os donos: `nenhum`, `calmo`, `agitado`, iguais no cuidado. | **Sim**, com a troca a cada hora para o programa da grade mais perto do perfil. | Donos que também cuidam diferente misturam o cuidado com a exposição; um dono sem `nenhum` perde a linha de base. |
| **GVP-5** | O agrado só no sinal (`agrado_no_corpo` desligada). | **Sim**, como o gabarito da fonte "grade" da P1f; a GV-16 inteira fica para uma run própria. | Com o agrado no corpo, o humor da tela se mistura com o da comida e o efeito do genoma fica mais difícil de separar. |
| **GVP-6** | A janela da sonda (240 ticks), as 3 réplicas e a distância das TVs (3 células). | **Sim**, os números das sondas da INDIVIDUALIDADE. | Janela curta demais e o pet não olha; longa demais e a habituação a uma TV domina o tempo relativo. |
| **GVP-7** | O tamanho: 3 bases × K = 12 e o piloto 2 × K = 2, com a conferência de 1 réplica em 4. | **Sim.** | Menor, e os IC95 cobrem tudo; maior, e o custo sobe sem conta de poder que o justifique. |
| **GVP-8** | A faixa 89101…89505 nas duas sub-faixas. | **Sim** (já confirmada pelo coordenador). | Uma faixa que cruza outra queima as duas. |

## 11. O registro da run

Nenhuma vida ainda. Antes da primeira vida do piloto, esta seção recebe, num commit empurrado: a data, o commit, a config, os 4 processos, o
sha256 deste plano e o ok do Matheus (com a frase dele).
