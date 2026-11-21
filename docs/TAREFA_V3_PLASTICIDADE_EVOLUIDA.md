# Tarefa V3: a plasticidade evoluída (a busca dos números do aprendizado)

**Status: APROVADO pelo Matheus em 2026-11-21** ("Aprovo todas", à pergunta "Aprova as PE-1 a PE-6 pela recomendação?"). **Só papel.** Escrito pelo Gerente da V3 (Claude Code, Fable 5.2) em 2026-11-21. O pedido é do Matheus: depois do
levantamento de tecnologia recente, ele escolheu aprofundar a "Plasticidade evoluída" e, à pergunta "Transformo o teste de sensibilidade
(E0) em tarefa no repositório?", respondeu "Sim, vira tarefa". **Esta tarefa abre só o E0. As PE-1 a PE-6
(seção 7) estão DECIDIDAS pela recomendação. Nenhuma vida roda antes do código do E0 na `main`, da faixa de sementes e do ok do Matheus.**

**Regras desta tarefa:**
- Os números novos são PROPOSTOS e SEM FONTE, salvo onde citam um artefato.
- **Nenhuma alegação de novidade.** Buscar por evolução as regras de plasticidade é a linha de Najarro e Risi (2020) e de Soltoggio,
  Stanley e Risi (2018). Herdar o jeito de aprender sem herdar o aprendido é o efeito Baldwin computacional (a regra 2 da skill de
  literatura).
- A pausa de 2026-11-21 vale aqui: o E0 é uma triagem, não uma run confirmatória, e nada confirmatório sai dele.
- O desenho completo (os níveis A, B e C, os riscos) está no vault, em `10 Auditoria/Desenho plasticidade evoluída 2026-11-21.md`.

## 0. Por que agora

- **Os números do aprendizado são escolhidos à mão.** A `ConfigDigibrainInatos` tem 60 campos, 55 deles inteiros, e a marca SEM FONTE
  aparece 56 vezes nela (contagem no `digilab/config.py` da `origin/main`).
- **As runs de 2026-11-17 a 20 mostraram que o aprendizado do modular quase não decide o comportamento** (`docs/TAREFA_V3_PET_QUE_PENSA.md`,
  seção 0). Há duas leituras possíveis:
  - **é estrutural:** o reflexo e o corpo decidem, e nenhum número do aprendizado muda isso;
  - **é de calibração:** os números à mão estão num canto ruim, e outros valores dariam ao aprendizado um papel.
- **O E0 separa as duas leituras, barato.** Se nenhum número do aprendizado mexer no resultado, a busca evolutiva não tem o que achar, e a
  aposta fica toda no pet que pensa. Se algum mexer, a busca tem por onde começar.

## 1. A literatura

Conferida no arXiv e no Crossref em 2026-11-21. Dos dois primeiros, o método e os resultados foram lidos no PDF; dos outros, só o resumo.
Ainda não estão em `docs/referencias/`: entram num CSV próprio com o PR do E0.

| referência | registro | o que sustenta |
|---|---|---|
| Najarro e Risi (2020), NeurIPS | arXiv `2007.02686` | a busca otimiza os coeficientes de uma regra hebbiana por sinapse (`Δw = η·(A·oi·oj + B·oi + C·oj + D)`), e não os pesos; estratégia evolutiva, população de 200 e de 500. **Ressalva do próprio artigo:** na condição vista no treino, a rede de pesos fixos anda mais que a hebbiana (1 604 ± 171 contra 1 051 ± 113); o ganho aparece na adaptação a um dano não visto |
| Miconi, Clune e Stanley (2018), ICML | arXiv `1804.02464` | a plasticidade de cada conexão pode ser otimizada por gradiente; precedente, não método (o DigiBrain é em inteiros, sem gradiente) |
| Soltoggio, Stanley e Risi (2018), *Neural Networks* | `10.1016/j.neunet.2018.07.013` | revisão das redes plásticas evoluídas (só o registro) |
| Salimans et al. (2017) | arXiv `1703.03864` | estratégias evolutivas como alternativa ao RL, escalando com o número de CPUs |
| Mouret e Clune (2015) | arXiv `1504.04909` | MAP-Elites: a busca devolve um mapa de soluções diversas e boas |

**A lição para o desenho:** não esperar ganho na média das condições vistas. O lugar da plasticidade é o que não foi visto na busca.

## 2. O E0: o teste de sensibilidade

**A pergunta:** algum número do aprendizado, mexido sozinho, muda o bem-estar do pet ou o valor de aprender?

**Os genes** (12, PROPOSTOS; todos são campos inteiros da `ConfigDigibrainInatos`, PE-3). Eram 15: o `beta_e`, o `g_min` e o `g_max`
saíram por decisão do Matheus em 2026-11-21 (D-PE-7), por serem inertes no pet v38, que tem a subchave `modula_g_apr` desligada:

| grupo | campos |
|---|---|
| a plasticidade | `eta_d`, `eta_h`, `h_max` |
| o incentivo | `c_g`, `g_max_incentivo` |
| o ganho do aprendizado | `g0` |
| os pesos dos termos | `w_pers`, `w_mem`, `w_lem` |
| a disputa | `tau_hab`, `epsilon`, `lambda_sono` |

**As configs:** a de hoje, e cada gene na metade e no dobro do valor de hoje, um por vez (cortado nos limites que a config já valida):
25 configs.

**Os dois braços de cada config** (PE-2):
- **APRENDE:** o pet com as subchaves do aprendizado ligadas, como hoje;
- **CONGELADO:** o mesmo pet, as mesmas sementes, com as subchaves `p1` e `p2` desligadas (o desfecho e o hábito ficam em 0).

**As medidas, por config:**
- **o bem-estar:** o "Tempo bem" do APRENDE (`digilab.metrics.tempo_bem_nas_decisoes`, dias 1 a 14);
- **o valor do aprendizado:** o "Tempo bem" do APRENDE menos o do CONGELADO, pareado por unidade;
- **ao lado:** a saúde dos dias 8 a 14, a exaustão e a fração `aprendido_decidiu` das sondas.

**O pet e as células** (PE-4): o pet v38 do jogo, no Python (o da PET_VIVO e da V1-a). Seis células: os donos atencioso e relapso × os
três lugares. Dez unidades, 14 dias.

**O tamanho:** 25 configs × 2 braços × 6 células × 10 unidades = **3 000 vidas** (eram 31 configs e 3 720 vidas, com os 15 genes). A cerca de 4 s de processo por vida (a conta da run
da recompensa: 9 600 vidas em 2 h 45 min com 4 processos), dá perto de **1 h** com 4 processos. É estimativa, sem medida.

**As sementes** (PE-5): 10 bases de uma faixa pedida à coordenadora antes da run. Todas as configs vivem as mesmas sementes.

## 3. A leitura do E0, escrita antes

É descritiva: não há gate nem classe. A tabela final ordena os genes pelo efeito.

| o que sai | a leitura | o que segue |
|---|---|---|
| nenhum gene muda o "Tempo bem" nem o valor do aprendizado além do ruído entre unidades | "estrutural: os números do aprendizado não decidem" | a busca (E1) não se abre; a aposta fica no pet que pensa |
| algum gene muda o valor do aprendizado, e ele fica acima de 0 em alguma config | "há por onde buscar" | o plano do E1 (a busca do nível A), com os genes que mexeram |
| só os genes da disputa mexem (`lambda_sono`, `epsilon`, `tau_hab`), e o valor do aprendizado segue em 0 | "a busca afinaria os reflexos, não o aprendizado" | a busca não se abre como plasticidade; o achado vai para a frente do corpo |

**"Além do ruído":** o IC95 do contraste pareado contra a config de hoje não contém 0. Com 10 unidades e 24 contrastes, alguns passam por
acaso: o resultado diz quantos seriam esperados (1 ou 2) e não trata um gene isolado como achado.

**O que o E0 não diz:** nada sobre interações entre genes (ele mexe um por vez), nada sobre donos e lugares fora das seis células, e nada
confirmatório.

## 4. O que vem depois, só se o E0 abrir

| etapa | o quê | condição |
|---|---|---|
| **E1** | a busca curta do nível A: uma estratégia evolutiva sobre os genes que mexeram, com o objetivo de duas partes (o bem-estar e o valor do aprendizado) | plano próprio; depois da triagem D1 do pet que pensa, com o `g_plano` entre os genes |
| **E2** | a melhor config contra a de hoje, em triagem, com um dono e sementes que a busca não viu | o E1 feito |
| **E3** | a confirmação | a E2 passando do corte da triagem |
| **níveis B e C** | a forma da regra do hábito; a herança do jeito de aprender | planos próprios; o C é decisão de produto |

## 5. Riscos

| risco | o que o desenho faz |
|---|---|
| a busca zera o aprendizado e afina os reflexos (a lição da A1) | o valor do aprendizado é medido desde o E0, pelo braço CONGELADO |
| o resultado só vale para os donos sintéticos | no E2, um dono e sementes de fora |
| vira a "calibração a cada mecânica" que o projeto evita | o E0 não muda nenhum número do jogo; a busca roda uma vez, depois das mecânicas do cérebro |
| a máquina | no máximo 4 processos, uma run por vez, com o `pre_run` |
| o braço CONGELADO muda mais que o aprendizado | a subchave desligada zera o termo e o estado dele; o teste confere que, ligada, o log é o de hoje |

## 6. A relação com as outras frentes

- **O pet que pensa** (`docs/TAREFA_V3_PET_QUE_PENSA.md`): não compete. O E0 pode rodar antes da D1 e informa quais números importam. A
  busca (E1) vem depois da D1.
- **CORPO, cadeia e VALUATION (a coordenadora):** pausadas para o cérebro. O E0 pede a ela só a faixa de sementes.
- **A máquina:** o E0 entra na fila depois do D0 do pet que pensa e da triagem da V1-a.

## 7. As decisões do Matheus (DECIDIDAS em 2026-11-21, "Aprovo todas", pela recomendação)

| nº | decisão | recomendação | custo de errar |
|---|---|---|---|
| PE-1 | rodar o E0 antes de qualquer busca | **sim** | pular: cerca de 9 h de busca sem saber se há o que achar |
| PE-2 | os dois braços (APRENDE e CONGELADO) | **sim:** dobra as vidas, mas mede o valor de aprender | só o APRENDE: não separa "o número mexeu no reflexo" de "mexeu no aprendizado" |
| PE-3 | os 15 genes da seção 2; **12 desde 2026-11-21:** o `beta_e`, o `g_min` e o `g_max` saíram por decisão do Matheus ("Sim, tira os três", D-PE-7), inertes no v38 com a `modula_g_apr` desligada | **estes,** um por vez, na metade e no dobro | uma lista maior: mais vidas; menor: um gene que importa fica de fora |
| PE-4 | o pet e as células | **o v38, 2 donos × 3 lugares, 10 unidades** | o pet da bancada: o resultado não vale para o pet do jogo (a lição da V1-a) |
| PE-5 | as sementes | **10 bases de uma faixa pedida à coordenadora** | as sementes dos testes: são só 5 bases, e já foram vistas |
| PE-6 | quem executa | **uma sessão lateral, com a revisão do Gerente;** o merge e o ok para rodar são do Matheus | — |

## 8. O que esta tarefa não afirma

- Nada sobre a plasticidade evoluída funcionar no DigiBrain: o E0 só diz se há por onde buscar.
- Nada sobre o jogo: nenhum número da config muda.
- Nenhum número de resultado.

## 9. O código do E0 (etapa de código, 2026-11-21)

Escrito por uma sessão lateral da Gerência da V3 (Claude Code, Fable 5.2). **Nenhuma vida de pesquisa rodou.** Os desvios estão em
`docs/registro/2026-11.md` (D-PE-7 a D-PE-15).

- **O orquestrador:** `experiments/run_v3_plasticidade_e0.py`, com as configs em `experiments/configs/v3_plasticidade_e0/` (`run.json` e
  `fumaca.json`). As 31 configs, os dois braços, as seis células (`comedouro`, `longe`, `longe_fixo` × atencioso e relapso), o pet v38
  montado como no `experiments/pv2.py`.
- **A medida:** `digilab.metrics.sensibilidade_um_por_vez` (o nível de cada braço, o valor do aprendizado pareado por unidade, os
  contrastes contra a config de hoje com o IC95 e a conta do acaso) e `saude_nas_decisoes`.
- **A leitura da seção 3** está no `ler` do orquestrador. Um caso que a tabela não previu sai como "fora da tabela da seção 3".
- **As sementes:** a coordenadora reservou 110001…110200 para a tarefa; o E0 usa 110001…110010.
- **Os testes:** `tests/test_run_v3_plasticidade_e0.py`.
- **As referências:** `docs/referencias/v3_plasticidade_evoluida_referencias_verificadas.csv`.
- **O custo medido na fumaça** (60 vidas de 14 dias, a semente 101, 2 processos, com a suíte de outra sessão rodando ao mesmo tempo):
  6,9 s de parede e 3,7 s de CPU por vida, com o replay e as conferências. Para as 3 720 vidas com 4 processos, isso projeta 1,8 h pela
  parede medida e cerca de 1 h pela CPU. A fumaça só serve ao custo; o artefato dela não foi commitado.
- **Achado para decidir antes da run (D-PE-7):** o `beta_e`, o `g_min` e o `g_max` não chegam a nenhuma conta no pet v38, porque a
  subchave `modula_g_apr` está desligada nele. As 6 configs deles repetem a de hoje (720 das 3 720 vidas). A lista da PE-3 não foi mudada.
- **Falta para rodar:** a vez na máquina (depois do D0 do pet que pensa e da triagem da V1-a) e o ok do Matheus.
- **Depois do PR do código (2026-11-21):** o Matheus decidiu tirar os três genes inertes ("Sim, tira os três", D-PE-7). O E0 ficou com 12
  genes, 25 configs e 3 000 vidas; os números desta seção que falam em 31 configs e 3 720 vidas são os de antes. Pelo custo medido na
  fumaça, as 3 000 vidas com 4 processos projetam 1,4 h pela parede e cerca de 0,8 h pela CPU.

## 9. Adendo 1: o crítico e a entropia da decisão (APROVADO pelo Matheus em 2026-11-21 ("Aprovo todas", à pergunta "Aprova as PQ3-10, PQ3-11 e PE-8 a PE-11 pela recomendação?"))

**De onde vem.** O Matheus pediu a leitura das notas do vault sobre Bennett (2023) e Gleick (2011), em `20 Temas`, e escolheu levar às
tarefas os três pontos que mexiam na etapa atual ("Os três"). Dois são desta tarefa:
- o crítico (Bennett, saltos 1, 2 e 3);
- a entropia por decisão (Gleick, parte C).

O portão de "quando pensar" entra na `docs/TAREFA_V3_PET_QUE_PENSA.md`. **O Bennett é moldura, não citação:** o adendo se apoia na fonte
primária.

### 9.1 O crítico (uma triagem nova, o C0, antes do E0)

- **O problema:** o hábito (P2) aprende com a recompensa crua: `H ← H + g_apr·η_h·(r_n·e)` (`digilab/digibrain/plast.py`). Não há um valor
  esperado aprendido, e por isso não há erro de previsão de recompensa. O pet aprende "isto foi bom", e não "isto foi melhor do que eu
  esperava".
- **Por que importa para o E0:**
  - o E0 mede o valor de aprender (APRENDE − CONGELADO) de um aprendiz sem crítico;
  - se sair "nada mexe", a leitura "o problema é estrutural" pode estar certa pelo motivo errado: falta a peça, e não os números;
  - os achados da cadeia são o sintoma esperado da falta dessa peça: o crédito dominado pelo sono (R1 e R-a) e a linha de base por contexto
    que apaga o sinal do intervalo.
- **A fonte:** o erro de diferença temporal (Sutton, 1988, já no projeto) e o sinal da dopamina como erro de previsão (Schultz, Dayan e
  Montague, 1997, `10.1126/science.275.5306.1593`, conferido pelo resumo nas notas do vault).
- **O C0, uma troca só:**
  - no lugar do `r_n` cru, o P2 recebe `δ = r_n + γ·V̂(z′) − V̂(z)`;
  - `V̂(z)` é linear nas características `z` que o P2 já usa;
  - o aprendizado é TD(0) local, em inteiros, com o passo `eta_v` e o `gamma` PROPOSTOS, SEM FONTE;
  - tudo fica atrás de uma subchave nova (`critico`), desligada por padrão;
  - o G2: com a subchave desligada, o log sai igual ao de hoje, bit a bit.
- **Os braços:** HOJE, CRÍTICO (a subchave ligada) e CONGELADO (como no E0), no pet v38, nas mesmas 6 células e 10 unidades do E0. São 360
  vidas, cerca de 10 min com 4 processos (estimativa pela fumaça do E0).
- **As medidas:**
  - o "Tempo bem";
  - o valor do aprendizado (APRENDE − CONGELADO) com e sem o crítico;
  - a fração `aprendido_decidiu`;
  - a fração do crédito que vai ao sono (a medida do R1).
- **A leitura:**
  - **o crítico aumenta o valor do aprendizado:** o E0 roda com o crítico ligado nos dois braços, e o `eta_v` entra entre os genes;
  - **nada muda:** o E0 roda como está, e a leitura "estrutural" ganha força.

  É triagem, sem gate. O corte para uma confirmação é o da PQ3-9 do pet que pensa.
- **A ordem:** o C0 roda antes do E0. O código do crítico é pequeno (uma subchave no P2) e vai num PR próprio.

### 9.2 A entropia da decisão (um descritivo novo no E0 e no C0)

- **A medida:** a entropia do sorteio `H(w/T)` em bits, por decisão, e a fração das decisões com `H` abaixo de 0,1 bit. Sai do motivo do
  M-ARB, sem simulação a mais. Fonte: Shannon (1948).
- **Por que:** diz, para cada gene mexido, se ele torna a escolha mais concentrada ou mais espalhada, além do efeito no "Tempo bem".
- **A previsão, escrita antes de calcular (D-RB-13):** os genes da disputa (`epsilon`, `tau_hab`) mexem em `H`; os da plasticidade mexem
  pouco. É descritiva.

### 9.3 As decisões do adendo (DECIDIDAS em 2026-11-21, pela recomendação)

| nº | decisão | recomendação | custo de errar |
|---|---|---|---|
| PE-8 | o C0, a triagem do crítico, antes do E0 | **sim:** 360 vidas, uma subchave nova, e o E0 passa a medir o aprendiz certo | sem o C0: o E0 pode dar "estrutural" por falta da peça |
| PE-9 | o `eta_v` e o `gamma` do crítico | **PROPOSTOS, SEM FONTE,** fixados no PR do código; o `eta_v` entra como gene do E0 se o C0 abrir | — |
| PE-10 | a entropia da decisão como descritivo do E0 e do C0 | **sim** | — |
| PE-11 | quem executa o C0 | **a sessão lateral do E0, com a revisão do Gerente;** a frente do crédito da cadeia, da coordenadora, segue pausada, e o crítico fica nesta tarefa | abrir na cadeia: reabre uma frente pausada pelo Matheus |

## 10. O código do C0 e da entropia (etapa de código, 2026-11-21)

Escrito pela sessão lateral do E0 (Claude Code, Fable 5.2). **Nenhuma vida de pesquisa rodou.** Os desvios estão em
`docs/registro/2026-11.md` (D-PE-C0-1 a D-PE-C0-9).

- **O crítico:** a `ConfigCritico` no `digilab/config.py` (desligada por padrão; `eta_v` = S/16 e `gamma` = 15S/16, PROPOSTOS, SEM FONTE)
  e a conta no `digilab/digibrain/plast.py`. Ficou numa config própria, e não como campo da `ConfigDigibrain`, para o dump de paridade com
  o jogo web não mudar (D-PE-C0-1).
- **O G2:** `tests/gabaritos/critico_de_hoje.json`, gravado num commit próprio antes da mudança; desligada, as vidas saem iguais.
- **O orquestrador:** `experiments/run_v3_plasticidade_c0.py`, com as configs em `experiments/configs/v3_plasticidade_c0/`. Os braços HOJE,
  CRÍTICO e CONGELADO, nas 6 células e nas bases 110001…110010.
- **A conta das vidas:** três braços × 6 células × 10 unidades = **180 vidas**. A seção 9.1 fala em 360 (D-PE-C0-5).
- **As medidas novas no `digilab/metrics.py`:** `entropia_do_sorteio` (PE-10) e `credito_do_habito_por_linha` (a parte do crédito do
  hábito que vai à linha do dormir). As duas entram também nas medidas de cada vida do E0.
- **Os testes:** `tests/test_plasticidade_c0.py`.
- **Falta para rodar:** a vez na máquina e o ok do Matheus. O C0 roda antes do E0.
