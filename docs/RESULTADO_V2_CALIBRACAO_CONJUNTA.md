# Resultado — calibração conjunta do cérebro A (K2)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Tarefa `docs/TAREFA_V2_K2_CALIBRACAO_CONJUNTA.md`; plano `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` (K-1 a K-11). Run única em 2026-10-06,
commit `5f288d6` (montagem completa da BANCADA-MONTAGEM, #178), sementes de calibração 14101…14505 com K = 4 (20 unidades), 14 dias,
dono atencioso, ponto T3. Tempo: 4 h 12 min (a suíte inteira rodou ao mesmo tempo na máquina). Todo número abaixo vem de
`artifacts_v2_calibracao_conjunta/` (`{A1,A2,B,C,D}/resultado.json`, `escolha.json`, `adendo.json`, `alternativas_n.json`, `run.log`);
as vidas (2,1 GB) ficam fora do git e se regeneram da config e do código.

**Status: o N da validação passa do teto de 12 h (K-10).** Pela regra da seção 5.3.6 do plano, a validação não roda sem decisão do Matheus.

## 1. O ponto escolhido

| etapa | parâmetro | grade | escolhido | a regra fechou? | medida no escolhido (IC 95%) |
|---|---|---|---|---|---|
| A1 | `g` (ganho da memória) | 256, 512, 768 | **512** (S/2) | sim | fração decidida pela memória 0,159 [0,128; 0,190]; o 256 deu 0,088 [0,058; 0,121] |
| A2 | `w0_pedido` | 256, 512, 768 | **256** (S/4) | **não** | nenhum conflito na `fome_moderada` em nenhuma das 20 unidades, nos três pontos |
| B | ganho do P1 | 4, 8, 16 | **4** | **não** | todo ganho teve vida do P1 no teto: 2, 10 e 33 de 60; razão da deriva 2,72, 1,15 e 1,06 |
| C | `w0_info` | 256, 512, 768 | **256** (S/4) | sim | fração decidida pela informação 0,200 [0,146; 0,259] |

- **A2:** a regra do N7-4 pede a deferência na zona `fome_moderada`, e nessa zona não houve nenhuma decisão de conflito (todas as frutas
  no cenário com pedido vigente) nas 20 unidades. Por que não houve não foi investigado. A deferência fica sem denominador, então vale a
  reserva: o menor valor (sem IC em nenhum ponto). G-URG: nenhuma violação das regras urgentes.
- **B:** pela regra, só entram os ganhos sem nenhuma vida no teto, e não houve nenhum. A reserva registrada antes da run (a do N3:
  menos vidas no teto, depois a menor razão) escolhe o 4: 2 vidas no teto, ambas no descasado. A razão da deriva do 4 é 2,72: o
  aprendizado ainda cresce no fim da vida, o risco 1 da seção 6 do plano.

## 2. O piloto (etapa D)

- 880 vidas (44 por unidade, seção 4), todas gravadas e rejogadas do disco bit a bit (K9). 12,3 s por vida, com a suíte rodando junto.
- **Contratos K1–K9: todos passam** em vida real. O P0 é o instinto byte a byte; P2 e P2e informam nos mesmos ticks com conteúdo
  oposto; as ofertas são as mesmas em todo braço e acoplado; casado e descasado têm efeitos opostos; o K4 está ligado.
- **Δ = 0,199** (regra 6.3: metade da `taxa_fruta_ruim` final do P0 no descasado, 0,397). Δ do bloco N6 0,194; Δ do bloco N7 0,202.
- Os contrastes do piloto ficam no artefato, como piloto, e não são lidos aqui (seção 3.5 do plano).

## 3. O N da validação: por que passa do teto

| contraste | σ_d | N (fórmula, α/6, poder 0,8) | poder simulado com esse N |
|---|---|---|---|
| p1_casado | 0,061 | 5 | 0,99 |
| p2_descasado | 0,092 | 5 | 0,74 |
| p2_mutavel | 0,097 | 5 | 0,73 |
| **p3_consumos** | **26,9** | **191.815** | 0,83 |
| p4a_piora | 0,035 | 5 | 1,00 |
| p4b_recupera | 0,095 | 5 | 0,77 |

**N = 191.815 unidades, cerca de 28.760 h.** O N vem todo do `p3_consumos`. Esse contraste é medido em **consumos** (consumos até a taxa
cair à metade), mas recebe o Δ da regra 6.3, que está em **taxa** (0,199). Com σ_d de 26,9 consumos contra uma margem de 0,2, o N
explode. É um problema de escala na regra: a seção 6.3 do experimento maior define um Δ só, e a seção 5.3 do plano da calibração o aplica
aos seis contrastes.

Dois pontos a mais:
- **Os outros cinco ficam no piso de 5 unidades** (o múltiplo de 5). Nesse N a aproximação normal da fórmula é otimista: o poder simulado
  (bootstrap das 20 unidades centradas no Δ, teste t) fica entre 0,73 e 0,77 em três deles.
- **O poder dos secundários no adendo foi calculado com o N de 191.815** e sai 1,0 em todos; precisa ser refeito com o N decidido.

## 4. Para o Matheus decidir (antes da validação, seção 5.3.6)

Alternativas calculadas das mesmas 20 unidades (`alternativas_n.json`; cada uma é cálculo de tamanho de amostra, não leitura de predição):

| opção | o que muda | N | tempo estimado |
|---|---|---|---|
| **A (recomendada)** | Δ do p3 na escala dele, pela mesma convenção de "metade": metade dos consumos até a metade do P1 no descasado (35,0 → Δ_p3 = 17,5; 3 de 20 vidas do P1 censuradas). N pelo maior N **simulado** com poder ≥ 0,8 | **30** | ~4,5 h |
| B | o p3 fica fora de quem puxa o N (vira secundário com o poder declarado); os outros pelo N simulado | 10 | ~1,5 h |
| C | como está | 191.815 | ~28.760 h (inviável) |

A opção A mantém os seis contrastes primários e só põe cada Δ na escala da sua medida. Ela também troca o N da fórmula pelo da simulação
nos contrastes em que a fórmula fica otimista no N pequeno. As duas mudanças são do plano (seções 5.3 e 6.3) e entrariam pelo adendo,
antes da validação.

Também pedem decisão:
- **A2 não fechou** porque a zona `fome_moderada` não teve conflito. Ficar com o 256 pela reserva, ou rever a regra.
- **B não fechou** e a razão da deriva do 4 é alta, 2,72. A predição 2 já prevê a leitura "inconclusivo por duração" para esse caso.

## 5. Interpretações e desvios

`docs/REGISTRO_DESVIOS.md`, seção K2-CALIBRACAO-CONJUNTA:
- as interpretações registradas antes da run;
- a run interrompida antes da opção 1, apagada sem leitura;
- o que a run mostrou: A2 sem conflitos, B na reserva, a escala do Δ no p3.
