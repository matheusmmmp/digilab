# Resultado — V2: o diagnóstico do DigiBrain modular depois da avaliação única (2026-10-26)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Proposta: `docs/PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR.md`, seção 3, aprovada pelo Matheus em 2026-10-26 ("Aprovo a proposta, com replay
no piloto"). Executor: worker D (Claude Code, Opus 5.5), worktree `v2-modular-diagnostico`.

## Antes dos números

- **Nenhuma vida nova:**
  - nenhuma semente das faixas 64xxx, 65xxx ou 66xxx foi usada;
  - o orquestrador não rodou;
  - nada mudou em `digilab/`.
- **O resultado do #420 fica como está.** Nenhum veredito é refeito, e nenhum número daqui é gate.
- **O replay é descritivo:**
  - o piloto tem 24 vidas por braço e lugar (K = 2, as bases 63303 a 63505) e 8 por célula, sem IC;
  - os números servem para escolher entre as hipóteses, não para testar nada.
- **O diagnóstico termina neste relato.** As mudanças DX-1 a DX-7 só vêm no adendo 3, depois da decisão do Matheus.

## Como rodou

- **§3.1:** `experiments/diagnostico_avaliacao_digibrain.py` só lê `artifacts_v2_digibrain_prototipo/avaliacao/medidas.json` (5 400
  vidas, no git) e grava `artifacts_v2_digibrain_prototipo/diagnostico/avaliacao.json`.
- **§3.2:** `experiments/diagnostico_replay_digibrain.py <pasta>` rejoga as 576 vidas do piloto. As vidas são as regeradas pelo
  Gerente no `c3a4d82`, em `D:\Trab\digilab\v2-regera-piloto\...\piloto\vidas`, fora do git e só lidas. A saída vai para
  `artifacts_v2_digibrain_prototipo/diagnostico/replay_piloto.json`.
  - **A instrumentação** embrulha três métodos na instância do cérebro do replay: o `codificar` do M-SENS, o `unidades` do M-IMPULSO e o
    `creditar` do M-PLAST. Ela guarda o que entra e sai e devolve o mesmo objeto.
  - **O tempo:** 8 processos, 98 s.
- **G1 no replay:** cada vida rejogada refaz o log do disco, passa nas falhas altas do mecanismo e refaz as medidas gravadas no
  `medidas.json` regerado, fora do campo de relógio `custo`.
  - **576 de 576** conferidas, nas três execuções do script:
    - a segunda acrescentou a contagem de onde o pet come;
    - a terceira veio depois de tirar do script um nome que o G2 só permite no config e no orquestrador (o teste
      `test_nada_fora_do_pacote_e_do_orquestrador_le_a_chave`). Ela deu os mesmos números da segunda, e o artefato é o dela.
  - Na mesma vida, o índice "ganhou, fica" refeito por ação, somado, dá o índice gravado.
  - As rações elegíveis e as fechadas contadas pelo replay são as da cadeia gravada.
- **A regeração do piloto,** do Gerente: `artifacts_v2_digibrain_prototipo/diagnostico/conferencia_regera_piloto.txt`, com os sha256.
  Conferi de novo: os dois `medidas.json` têm esses sha256 e diferem em 0 das 576 vidas fora do `custo`.

## 1. As tabelas da seção 1 da proposta (§3.1)

O script refaz todos os números da seção 1 a partir do artefato, e eles batem com a proposta. Por exemplo:

| célula (M3, avaliação) | refeições por dia | privação | rações elegíveis | fechadas | taxa | com a cadeia |
|---|---|---|---|---|---|---|
| comedouro, atencioso | 6,47 | 0,087 | 109,6 | 21,0 | 0,196 | 0 % |
| perto, atencioso | 4,02 | 0,000 | 57,7 | 34,9 | 0,607 | 96 % |
| comedouro, aleatório | 2,55 | 0,465 | 20,7 | 14,1 | 0,686 | 96 % |
| longe, aleatório | 1,87 | 0,591 | 28,5 | 3,6 | 0,132 | 0 % |

- **O sono:** dormir é 0,459 das decisões no A11, 0,474 no M0 e 0,469 no M3. O reflexo decide 0,190 das decisões do M3 (255 por vida).
- **O índice "ganhou, fica":** −0,080 no M0. No M2 − M1, por lugar: +0,008 no comedouro, +0,004 no perto e −0,046 no longe.
- **A persistência:** as intenções com meta são 0,927 no M3-sp e 0,934 no M3. O M3 tem, por vida, 81 fins com a meta e 29 por troca.
- **As visitas:** 32,2 por vida no M3, todas contadas como vazias, em todo braço com memória.

As 12 células e todos os braços estão no `avaliacao.json`.

## 2. A leitura de código (§3.1)

### O caminho do cheiro até a unidade

1. **O motor** calcula a intensidade e a direção do cheiro das comidas maduras: `digilab/mundo.py:919`, com raio de 24 células
   (`config.py:1753`).
2. **O M-SENS** lê só se há cheiro, `ha_cheiro = direcao_cheiro != 0` (`digibrain/sens.py:96`). A intensidade e a direção não entram no
   cérebro (o G-SEM-DIRECAO).
3. **O M-IMPULSO** cria, com cheiro, as unidades `comer/cheiro` e `explorar/cheiro` (`digibrain/impulso.py:70-71` e `80-81`). O que
   entra na ativação delas:
   - **o inato** é só o do comportamento: o `W0_tipo` não tem a linha `cheiro` (`config.py:2429`; `impulso.py:102`). Com a mesma fome,
     a unidade `comer/cheiro` fica S/4 abaixo da `comer/ração`, que ainda soma o termo de proximidade e, com o P1, o incentivo;
   - **o prox, o nov e o incentivo** ficam em 0, porque a unidade não tem objeto (`impulso.py:103`);
   - **o hábito** é o do comportamento, igual para toda unidade de `comer` (`impulso.py:95` e `111`);
   - **a persistência** fica em 0, porque o cheiro não é intenção (`digibrain/estado.py:24`).
4. **O alvo:** o M-ADAPT entrega o candidato `cheiro` do motor (`digibrain/adapt.py:188`). É um ponto 8 células à frente, na direção do
   cheiro (`mundo.py:1340`; `config.py:1756`). O pet anda 60 subunidades por decisão, 3,75 células (`config.py:1743` e `1745`).

### As hipóteses do hábito

- **H-P2a, a medida:**
  - **o índice** (`digilab/metrics.py:2108`) é P(a mesma ação | r > 0) − P(a mesma ação | r ≤ 0), sobre pares de decisões seguidas no
    mesmo contexto;
  - **o r** é o da consequência da primeira decisão, o `sinal_corpo` entre o corpo da decisão e o corpo logo depois do gancho
    (`adapt.py:266`);
  - **o termo do hábito,** `sum_j H[b,j] z_j`, soma-se a toda unidade do comportamento b sem olhar o r da última decisão
    (`impulso.py:95` e `111`; `plast.py:63-71`). Ele sobe a repetição de b nos contextos z, ganhe ou não ganhe, e por isso pode baixar o
    índice.
- **H-P2b, o crédito por opção:**
  - **a elegibilidade** é o z da decisão que começou a opção (`estado.py:76`), e o r_n é a soma das consequências dela (`estado.py:91`);
  - **as unidades que não são intenção** (o cheiro, o vagar e as sem alvo) fazem opções de uma decisão só (`estado.py:93`);
  - **o P2** só mexe na linha do comportamento da opção (`plast.py:110-127`);
  - **a consequência:** a caminhada pelo cheiro é creditada decisão a decisão, cada uma com o seu z e o seu r_n. Ela não entra numa opção
    longa com a refeição.
- **H-P2c, os contextos:** o contexto da medida é o drive mais urgente, a comida à vista e a noite (`adapt.py:161`;
  `run_v2_digibrain_prototipo.py:295`). O H aprende sobre as 22 características do z (`impulso.py:48`).

## 3. O replay do piloto (§3.2)

### 3.1 O hábito por ação e por contexto (H-P2a, H-P2c)

- **O piloto refaz o padrão da avaliação.** No M2 − M1 com o contexto da medida, o comedouro dá −0,009, o perto +0,008 e o longe
  −0,046.
- **Dormir, chamar a atenção e ocioso têm sempre r = 0,** em todas as opções dos 8 braços (seção 3.2). Elas só entram no lado "sem
  alívio" do índice.
  - **O dormir** dá 22 920 pares no M1 e repete em 0,40 deles. É ele que puxa o índice para baixo em todo braço: com o contexto da
    medida, M0 −0,075 e M1 −0,075.
  - **Sem as ações de consumo** (comer e dormir, o índice da DX-5), a linha de base fica positiva: M0 +0,051 e M1 +0,048.
- **Por ação, no contexto da medida** (pares; p de repetir com r > 0; p com r ≤ 0; o índice):

| lugar | ação | M1 | M2 |
|---|---|---|---|
| comedouro | comer | 700; 0,069; 0,100; **−0,031** | 1 099; 0,241; 0,116; **+0,125** |
| comedouro | explorar | 4 730; 0,359; 0,338; +0,021 | 4 289; 0,309; 0,303; +0,006 |
| perto | comer | 531; 0,080; 0,200; **−0,120** | 680; 0,239; 0,230; **+0,009** |
| perto | explorar | 4 976; 0,342; 0,314; +0,029 | 4 241; 0,317; 0,264; +0,053 |
| longe | comer | 715; 0,083; 0,096; −0,013 | 913; 0,106; 0,079; +0,027 |
| longe | explorar | 2 951; 0,256; 0,201; **+0,055** | 3 415; 0,193; 0,283; **−0,091** |

- **No comer, o hábito faz o que se previa** em todo lugar: o "ganhou, fica" sobe do M1 para o M2.
- **O sinal contrário do longe vem do explorar.** No M2, o explorar repete menos depois do alívio (de 0,256 para 0,193) e mais sem ele
  (de 0,201 para 0,283).
- **A sonda mostra onde o hábito decide** (M2, janela dos dias 8 a 14, decisões que o hábito mudou):
  - no longe, 1 804 no explorar, 625 no brincar, 424 no comer e 357 no chamar a atenção;
  - no perto, 797 no explorar e 398 no comer.
- **No fim da vida do M2,** a linha do H do explorar é a maior no longe e menor no perto:
  - os pesos médios no longe: o viés 171, o E 160, o estresse 158 e o "sem comida" 149;
  - no perto, o viés fica em 56.
- **Os índices médios por vida, no M2 − M1:**

| contexto | todas as ações | sem consumo |
|---|---|---|
| o da medida | −0,016 | −0,044 |
| o do z (cada característica em −1, 0 ou +1 pelo corte S/2) | −0,014 | −0,033 |
| nenhum | −0,025 | −0,041 |

  - **No longe, com o contexto do z,** o M2 − M1 vai de −0,046 para −0,007 em todas as ações, e para +0,024 sem consumo. Nos outros
    lugares, o contexto do z não muda o sinal.
  - **Sem consumo,** o M2 − M1 fica negativo nos três lugares: −0,046 no comedouro, −0,035 no perto e −0,050 no longe.

### 3.2 As opções creditadas no longe (H-P2b)

M2, por vida (24 vidas por lugar). As colunas são as opções por vida, o r_n médio, a fração com r_n > 0 e as decisões por opção.

| opção | comedouro | perto | longe |
|---|---|---|---|
| `comer/cheiro` | 18,8; −28,8; 0,00; 1,00 | 7,1; −28,4; 0,00; 1,00 | **52,2; −28,9; 0,00; 1,00** |
| `comer/comida` | 67,8; 290,8; 0,92; 1,006 | 48,5; 449,2; 0,95; 1,007 | 36,3; 514,7; 0,87; 1,024 |
| `explorar/vagar` | 303,3; 22,4; 0,61; 1,00 | 328,6; 15,1; 0,61; 1,00 | 222,2; 57,2; 0,68; 1,00 |
| `explorar/cheiro` | 83,2; 69,4; 0,67; 1,00 | 51,9; 15,5; 0,64; 1,00 | 89,1; 94,6; 0,74; 1,00 |

- **As opções são de uma decisão.** No longe, só 21 das 871 opções `comer/comida` do M2 duram mais de uma decisão. Nelas, a distância
  entre o z do começo e o da última decisão é de 1,85 S, somada sobre as 22 características.
- **A caminhada pelo cheiro sai sempre negativa.** A opção `comer/cheiro` nunca come e tem r_n < 0 em 100 % dos casos, em todo braço
  (−28,6 a −29,0). No longe são 52 por vida, contra 7 no perto.
- **O explorar quase nunca come:** de 0 a 2 % das decisões, em todo lugar. O r_n positivo dele, maior no longe, não vem da refeição. Não
  investiguei de qual canal ele vem.
- **A H-P2b, como a proposta a escreveu,** não se sustenta: a opção longa que soma a caminhada e a refeição não existe aqui. O que existe
  é a caminhada creditada à parte, negativa, na linha do comer.

### 3.3 O sono dentro da janela das rações elegíveis

M3, todas as células. As colunas são a fração de dormir e a do reflexo nas 8 decisões da janela.

| rações | n | dormir | reflexo do sono | já dormindo na posta | janela toda dormindo |
|---|---|---|---|---|---|
| fechadas | 1 278 | 0,510 | 0,209 | 0,443 | 0,000 |
| não fechadas | 3 693 | 0,525 | 0,323 | 0,507 | 0,001 |

- **O sono ocupa metade da janela,** fechem ou não as rações. A diferença no dormir é de 0,015.
- **O reflexo pesa mais nas que não fecham** (0,32 contra 0,21).
- **Quase nenhuma janela é só de sono.**
- **No longe,** o dormir é 0,512 nas fechadas e 0,530 nas não fechadas.
- **O M0 dá o mesmo:** 0,529 nas fechadas e 0,517 nas não fechadas.

### 3.4 A distância do cheiro nas rações longe que não fecharam

M3, longe, em células. Na mediana e na média, a distância vai da posição do pet na decisão da posta até a ração.

| rações longe | n | d na posta, mediana | menor d na janela, média | até 6 (visão) | 6 a 12 | 12 a 24 | além de 24 | vista na janela | decisões ao cheiro por ração |
|---|---|---|---|---|---|---|---|---|---|
| fechadas | 140 | 4,7 | 0,4 | 0,60 | 0,33 | 0,07 | 0,00 | 0,99 | 1,06 |
| não fechadas | 2 197 | **20,5** | **17,1** | 0,02 | 0,13 | 0,60 | **0,25** | **0,06** | 1,04 (0,65 no comer) |

- **A ração longe que fecha é a que o pet já tinha perto.**
- **A que não fecha** começa a 20 células em média, e um quarto delas fica além do raio do cheiro.
  - **O cheiro na posta é o da comida madura mais forte,** não necessariamente o desta ração. Por isso ele aparece em 0,95 das postas,
    até nas de além de 24 células.
- **A conta do alcance:**
  - a 3,75 células por decisão, sair de 20 células e chegar à visão (6 células) pede 4 decisões seguidas indo ao cheiro;
  - a janela tem 8 decisões, metade delas de sono, e só cerca de 1 decisão por ração vai ao cheiro;
  - só 6 % dessas rações entram na visão dentro da janela.
- **O M0, sem aprendizagem,** dá o mesmo: a mediana de 20,5 células e 5 % vistas.

## 4. O que o diagnóstico diz das hipóteses

| hipótese | o que o replay mostra | leitura |
|---|---|---|
| **H-P2a** (a medida mistura saciedade e hábito) | a linha de base negativa vem de dormir, chamar a atenção e ocioso com r = 0 sempre; no comer, o hábito sobe o índice em todo lugar; no explorar do longe, o hábito repete mais sem alívio | **sustentada em parte:** o índice mede bem o comer; a parte negativa vem das ações sem r e do explorar habitual |
| **H-P2b** (a opção longa soma caminhada e refeição) | as opções têm uma decisão; a caminhada pelo cheiro é creditada à parte, sempre negativa, 52 vezes por vida no longe | **não sustentada como escrita;** o que aparece é o crédito negativo do `comer/cheiro`. A DX-6 não está apontada |
| **H-P2c** (os contextos da medida não são os do z) | com o contexto do z, o M2 − M1 total muda pouco (−0,016 para −0,014); no longe, ele vai de −0,046 para −0,007 | **fraca:** muda o longe, mas não o sinal geral |
| **o sono** | metade da janela em sono nas fechadas e nas não fechadas; o reflexo é mais alto nas não fechadas (0,32 contra 0,21) | **não separa;** confirma a DX-7 "não" |
| **o cheiro** | a ração longe que não fecha está a 20 células, e só 6 % entram na visão na janela; o pet vai ao cheiro cerca de 1 vez por ração; a unidade do cheiro não tem peso de tipo nem proximidade, e não é intenção | **sustenta a DX-3 e a DX-4** como o lugar do conserto do longe |

**Uma observação para a DX-5:** o índice sem consumo, como a proposta o define, deixa o M2 − M1 negativo nos três lugares (−0,044 no
total). Ele tira o dormir, mas deixa o chamar a atenção e o ocioso, que também nunca têm r > 0. Se ele for a secundária, é bom saber
disso antes de pré-registrar o sinal esperado.

## 5. Achados (sem conserto)

- **Dormir, chamar a atenção e ocioso têm r = 0 em toda decisão.** O r de uma decisão é a diferença do corpo entre a decisão e o gancho de
  consequência. Nessas ações, a diferença é zero em todos os canais. O efeito do tempo que passa (o sono recuperando a energia, por
  exemplo) não aparece no r de nenhuma decisão.
  - Vi isso nos números e nos canais de uma vida.
  - **Não investiguei** no motor onde o tempo da decisão passa.
- **O `comer/cheiro` nunca come e tem sempre r_n < 0** (cerca de −29). Com o P2, ele só tira peso da linha do comer nos contextos da fome.
- **O cheiro "presente" na posta não é o da ração:** o pet lê só se há algum cheiro (G-SEM-DIRECAO), e o mais forte pode ser de uma
  fruta.

## 6. O que fica para o Matheus

Escolher as mudanças DX-1 a DX-7 para o adendo 3, agora com o diagnóstico. A recomendação, com o custo de errar:

- **DX-3 e DX-4 (o cheiro): sim.** São o que o replay aponta para o longe. **Custo de errar:** se o pet de fato não alcança a ração em 8
  decisões, nem a intenção no cheiro fecha a cadeia no longe. A janela W fica como está, e o longe pode continuar sem fechar.
- **DX-1 (as visitas vazias) e DX-2 (o episódio de fome, como secundária): sim,** sem mudança em relação à proposta.
- **DX-5:** como secundária, com a observação da seção 4, isto é, com o sinal esperado escrito antes. Ou tirar também as ações sem r
  possível (o chamar a atenção e o ocioso). **Custo de errar:** pré-registrar uma secundária que já se sabe que sai negativa.
- **DX-6 (o crédito pela última consequência): não.** O replay não aponta para ela: as opções são de uma decisão.
- **DX-7 (o limiar do sono): não.** O sono não separa as rações fechadas das não fechadas.
- **Fora da lista da proposta, só como pergunta:** o r = 0 das ações cujo efeito vem com o tempo (o sono). Mexer nisso é mexer no corpo
  ou no motor, e pelo critério de parada da proposta (seção 5) volta ao Matheus.

O diagnóstico para aqui.
