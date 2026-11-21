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

**Os genes** (15, PROPOSTOS; todos são campos inteiros da `ConfigDigibrainInatos`, PE-3):

| grupo | campos |
|---|---|
| a plasticidade | `eta_d`, `eta_h`, `h_max` |
| o incentivo | `c_g`, `g_max_incentivo` |
| o ganho do aprendizado e do afeto | `g0`, `beta_e`, `g_min`, `g_max` |
| os pesos dos termos | `w_pers`, `w_mem`, `w_lem` |
| a disputa | `tau_hab`, `epsilon`, `lambda_sono` |

**As configs:** a de hoje, e cada gene na metade e no dobro do valor de hoje, um por vez (cortado nos limites que a config já valida):
31 configs.

**Os dois braços de cada config** (PE-2):
- **APRENDE:** o pet com as subchaves do aprendizado ligadas, como hoje;
- **CONGELADO:** o mesmo pet, as mesmas sementes, com as subchaves `p1` e `p2` desligadas (o desfecho e o hábito ficam em 0).

**As medidas, por config:**
- **o bem-estar:** o "Tempo bem" do APRENDE (`digilab.metrics.tempo_bem_nas_decisoes`, dias 1 a 14);
- **o valor do aprendizado:** o "Tempo bem" do APRENDE menos o do CONGELADO, pareado por unidade;
- **ao lado:** a saúde dos dias 8 a 14, a exaustão e a fração `aprendido_decidiu` das sondas.

**O pet e as células** (PE-4): o pet v38 do jogo, no Python (o da PET_VIVO e da V1-a). Seis células: os donos atencioso e relapso × os
três lugares. Dez unidades, 14 dias.

**O tamanho:** 31 configs × 2 braços × 6 células × 10 unidades = **3 720 vidas**. A cerca de 4 s de processo por vida (a conta da run
da recompensa: 9 600 vidas em 2 h 45 min com 4 processos), dá perto de **1 h** com 4 processos. É estimativa, sem medida.

**As sementes** (PE-5): 10 bases de uma faixa pedida à coordenadora antes da run. Todas as configs vivem as mesmas sementes.

## 3. A leitura do E0, escrita antes

É descritiva: não há gate nem classe. A tabela final ordena os genes pelo efeito.

| o que sai | a leitura | o que segue |
|---|---|---|
| nenhum gene muda o "Tempo bem" nem o valor do aprendizado além do ruído entre unidades | "estrutural: os números do aprendizado não decidem" | a busca (E1) não se abre; a aposta fica no pet que pensa |
| algum gene muda o valor do aprendizado, e ele fica acima de 0 em alguma config | "há por onde buscar" | o plano do E1 (a busca do nível A), com os genes que mexeram |
| só os genes da disputa mexem (`lambda_sono`, `epsilon`, `tau_hab`), e o valor do aprendizado segue em 0 | "a busca afinaria os reflexos, não o aprendizado" | a busca não se abre como plasticidade; o achado vai para a frente do corpo |

**"Além do ruído":** o IC95 do contraste pareado contra a config de hoje não contém 0. Com 10 unidades e 30 contrastes, alguns passam por
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
| PE-3 | os 15 genes da seção 2 | **estes,** um por vez, na metade e no dobro | uma lista maior: mais vidas; menor: um gene que importa fica de fora |
| PE-4 | o pet e as células | **o v38, 2 donos × 3 lugares, 10 unidades** | o pet da bancada: o resultado não vale para o pet do jogo (a lição da V1-a) |
| PE-5 | as sementes | **10 bases de uma faixa pedida à coordenadora** | as sementes dos testes: são só 5 bases, e já foram vistas |
| PE-6 | quem executa | **uma sessão lateral, com a revisão do Gerente;** o merge e o ok para rodar são do Matheus | — |

## 8. O que esta tarefa não afirma

- Nada sobre a plasticidade evoluída funcionar no DigiBrain: o E0 só diz se há por onde buscar.
- Nada sobre o jogo: nenhum número da config muda.
- Nenhum número de resultado.
