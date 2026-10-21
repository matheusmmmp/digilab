# TAREFA V2 — GATE_I: o pet integrado (corpo químico, mundo, aprendizado na vida e replay no mesmo pet) (2026-10-21)

Coordenador: Gerente (Claude Code). Worker da tarefa e do plano: Claude Code (worktree `v2-gate-i`). Worker da execução: a definir.
Worktree e branch da execução: `v2-gate-i-<etapa>`. Status: **ABERTA** (a tarefa e o plano entregues, #382; as GT-1 a GT-7 DECIDIDAS pelo Matheus em
2026-10-21, pela recomendação; a GT-8 aberta; nenhuma etapa de código começou; **o Gate I não está implementado**).

Categoria: implementacao (a tarefa, com o piloto e a validação como experimento); o PR desta tarefa é só de documento. Origem: Matheus,
2026-10-21: as GI-1 a GI-5 de `docs/futuro/gate_integracao_pet.md`, DECIDIDAS pela recomendação.

## 1. Pergunta

**O mesmo pet, numa configuração só e nas mesmas vidas, recebe o corpo químico, percebe e age no mundo, aprende na vida pela
consequência e refaz a vida pelo log?** É o Gate I do `gate_integracao_pet.md`, o marco do pet integrado no `docs/ROADMAP_V2.md` (seção
8). O plano é `docs/PLANO_ANALISE_V2_GATE_I.md`.

**As decisões que valem** (2026-10-21):
- **GI-1:** tudo ao redor do cérebro A. Uma rede recorrente ou outro modelo só como pergunta própria, depois do Gate I;
- **GI-2:** a linha de base é a configuração da validação do J5 com o adendo 8, no mundo 2D;
- **GI-3:** o I-APRENDE por uma validação nova, com controle (o sinal embaralhado ou o braço sem aprendizado);
- **GI-4:** depois do Gate C em parte, em paralelo à P4, no 2D, antes do G1 e do G2 genéticos (o G0 pode vir antes);
- **GI-5:** a genética com o escopo de hoje, sem a topologia.

## 2. Depende de

- **Na `main`, já:**
  - o corpo químico (J2);
  - o mundo 2D (J1);
  - o cérebro A com o planejador e o mundo do J5 com o adendo 8 (#289, #290, #294, #295, o código do adendo 8);
  - a config `experiments/configs/v2_pet_que_pensa/validacao_adendo8.json`.
- **As decisões da seção 8:** as GT-1 a GT-7 DECIDIDAS em 2026-10-21; a GT-8 (o prefixo) aberta, e ela precisa estar decidida antes
  da etapa 1.
- **Não depende** da P4, do mundo 3D, da web nem da genética.

## 3. Mudança mínima

**A linha de base integrada** (GI-2, GT-1, GT-2): a configuração da validação do J5 com o adendo 8 (o corpo químico com o passo 0, o
mundo 2D com a fruta ao lado e o paladar, o dono atencioso no comedouro, o cérebro A no ponto T3 com a montagem completa, o `ganho_gosto`
= S/2 e o `g_plano` = S), **sem o protocolo do J5:** sem `T_m`, sem a fruta na mão, sem a troca de efeito e sem a parada das árvores.
Uma vida de 12 dias, a mesma duração. O pet é o do braço **P1-plan**.

**O que muda no código** (a etapa 1; tudo atrás de chave desligada, com o gabarito antes):
- **a bancada:** um tipo novo de vida, a linha de base sem o protocolo, que lê a config do adendo 8 e recusa as chaves do protocolo;
- **o braço sem aprendizado (S):** o mesmo pet com os pesos do A sem mudar e os modelos do mundo congelados no nascimento
  (`ModeloMundo.congelar("desfecho", "mapa")` antes da primeira decisão). A forma exata de desligar a L1 é da etapa 1, com o
  G-SEM-APRENDER (seção 4);
- **o braço do sinal embaralhado (E)** (GT-4), uma mecânica nova atrás de chave:
  - a consequência que o A credita em cada decisão (o vetor dos canais inteiro) é trocada por uma sorteada entre as já vividas na
    mesma vida, incluída a da própria decisão;
  - a amostra que o modelo do desfecho aprende em cada consumo é trocada por uma sorteada entre as já vividas, de qualquer tipo;
  - o sorteio usa uma rng própria, `derivar_semente("embaralhar", s)`, do lado da política. Ela não toca o mundo;
  - a chave desligada dá a vida de hoje, byte a byte;
- **as medidas,** em `digilab/metrics.py`: a escolha da x lado a lado por janela (a oportunidade da `oportunidade_ao_lado`, sem a
  condição da fruta na mão) e as conferências do I-CORPO e do I-MUNDO (seção 4);
- **o orquestrador** `experiments/run_v2_gate_i.py`, com as configs em `experiments/configs/v2_gate_i/` e a recusa de sempre.

**O que NÃO muda:**
- o `digilab/engine.py`;
- o cérebro A, os números do adendo 9 e o mundo;
- o J5 e os planos dele, a P4, o jogo web e as versões de pet antigas.

## 4. As etapas e os gates

| etapa | o que | gate (falha para a tarefa) | onde |
|---|---|---|---|
| **0, gabaritos** | num commit próprio, antes de tudo: as vidas do P1-plan na config do adendo 8 (a fumaça), com as chaves novas desligadas: o sha do estado interno e do log de cada vida | **G2:** um teste confere os gabaritos byte a byte | `tests/gabaritos/` |
| **1, o código** | a seção 3, e as faixas da GT-6 na `FAIXAS_RESERVADAS` | G2; **G1** (o replay bit a bit); **G-SEM-APRENDER:** no braço S, nenhum peso do A muda e o termo do plano é zero em toda decisão; **G-EMB:** no braço E, o sinal creditado em cada decisão é um dos já vividos naquela vida, e a rng `embaralhar` não toca o mundo; os testes do I-CORPO e do I-MUNDO com respostas conhecidas | PR `implementacao` |
| **2, o piloto** | as premissas, a margem, o N e o custo, nas sementes do piloto, com o sim do Matheus; o adendo 1 do plano | os do plano | PR `experimento` |
| **3, a validação** | **uma vez**, com outro sim; o `docs/RESULTADO_V2_GATE_I.md`, com o veredito do Gate I | os do plano | PR `experimento` |

**Os quatro critérios do gate,** pelo plano (seção 7 dele):
- **I-CORPO, de mecanismo:**
  - a G-RECEPTOR (`tests/test_corpo.py`) e o G-SEM-DIRECAO (`tests/test_cheiro_orgao.py`) passam no commit da run;
  - em toda vida do braço I, há ao menos uma atualização de peso com a parte do corpo diferente de zero.
- **I-MUNDO, de mecanismo,** em toda vida:
  - toda decisão com alvo escolhe um dos candidatos que o motor ofereceu naquela decisão, e a consequência do mundo chega ao cérebro;
  - no braço I, os pesos das classes de alvo mudam ao menos uma vez.
- **I-APRENDE:** os dois primários do plano passam, contra o braço S e contra o braço E (GT-3).
- **I-REPLAY:** o G1 em toda vida, e o G2 das chaves novas.

**O veredito:** o Gate I **passa** só com os quatro. Se um falhar, ele fica **"medido, não passou"**, com o que falhou. A V2 segue, e o
G1 e o G2 genéticos continuam esperando (GI-4).

## 5. Entrega

- **Os testes:** `python -m pytest tests/test_gate_i.py -q` (PROPOSTO) e a suíte inteira, com a contagem no corpo do PR. A web não muda.
- **O registro:** uma seção no fim de `docs/registro/AAAA-MM.md` e uma linha no índice `docs/REGISTRO_DESVIOS.md`, em cada etapa. O resumo
  vai no corpo do PR e na seção 9 deste arquivo; o do piloto e o da validação, no `RESULTADO_V2_GATE_I.md`.
- **O PR** segue `.github/pull_request_template.md`. O merge é só do Matheus.

## 6. Fora desta tarefa

- a genética: o G0 a G5 do `ecossistema_genetico.md` (o G0 pode andar em paralelo, como infraestrutura);
- o contrato sensório-motor, a P4 e o mundo 3D;
- o jogo web e a paridade TS (o `lobos.ts` continua sem as chaves do mundo e do plano);
- o T1 e o T2 do J5 (a revalorização e a busca);
- uma rede recorrente ou outro modelo de cérebro (GI-1: pergunta própria, depois do Gate I);
- os dois pets (J7);
- qualquer gene, mecanismo ou medida além dos da seção 3.

## 7. Critérios de aceitação

- **Etapa 0:** o commit dos gabaritos vem antes de qualquer commit de código, e um teste os confere.
- **Etapa 1:**
  - os testes novos passam, e a suíte inteira passa;
  - com as chaves novas desligadas, os gabaritos saem iguais;
  - a chave do embaralhado tem status em `digilab/config.py`;
  - as faixas estão na `FAIXAS_RESERVADAS`.
- **Etapas 2 e 3:**
  - o plano e o adendo 1 estão commitados antes das vidas de cada uma;
  - os artefatos existem e se refazem;
  - a validação rodou uma vez.
- **O veredito do Gate I** está no `RESULTADO_V2_GATE_I.md`, com cada critério, e o `ROADMAP_V2.md` só muda o estado do marco depois
  dele.

## 8. Precisa do Matheus

**As GT-1 a GT-7 DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação** (pelo Gerente):
- **GT-1:** a linha de base é o pet do P1-plan;
- **GT-2:** a vida do adendo 8 sem o protocolo do J5, com 12 dias;
- **GT-3:** os dois controles (S e E), e o I-APRENDE só passa contra os dois, com o Holm de 2;
- **GT-4:** embaralhar trocando a consequência e a amostra do desfecho por outras já vividas na mesma vida;
- **GT-5:** a medida é o `Δf` da x lado a lado, do primeiro ao último terço;
- **GT-6:** as faixas 63101…63505 (o piloto) e 64101…64505 (a validação), registradas na etapa 1;
- **GT-7:** o I-CORPO e o I-MUNDO como gates de mecanismo.

**A GT-8 (o prefixo das unidades) continua aberta:** a decisão de 2026-10-21 não a citou. A tabela abaixo é a que foi levada ao
Matheus. As do plano (as medidas, o N, as faixas) estão na seção 12 dele e repetem a numeração.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **GT-1** (DECIDIDA) | qual pet é a linha de base | **o do braço P1-plan** (o A com o planejador): é o que tem o resultado validado (o G-T1) | o P1 (sem o planejador): uma linha de base sem a peça que passou no Gate C; a genética mediria o pet do J1, que perde do instinto |
| **GT-2** (DECIDIDA) | a vida | **a do adendo 8 sem o protocolo do J5** (sem `T_m`, sem a mão, sem a troca nem a parada das árvores), com 12 dias | com o protocolo: a mudança do efeito da x no meio da vida mistura o aprendizado com a revalorização, e a medida do I-APRENDE fica confusa |
| **GT-3** (DECIDIDA) | os controles do I-APRENDE | **os dois, o braço sem aprendizado (S) e o do sinal embaralhado (E), e o I-APRENDE só passa contra os dois** (o Holm de 2) | só o S: o pet "aprende", mas não se sabe se foi pela consequência ou por receber qualquer sinal. Só o E: não se sabe quanto o pet muda sem aprender nada |
| **GT-4** (DECIDIDA) | como embaralhar | **trocar a consequência creditada pelo A e a amostra do desfecho por outras já vividas na mesma vida,** sorteadas por uma rng própria. Não há número novo | embaralhar só o A: o planejador continua aprendendo o efeito real pelo desfecho, e o braço E ainda aprende pela consequência. Embaralhar entre vidas: quebra o replay de cada vida sozinha |
| **GT-5** (DECIDIDA) | a medida do I-APRENDE | **a mudança na escolha da x lado a lado** (a favorita, que faz bem), no último terço menos no primeiro terço da vida, por unidade | o nível no fim: confunde o aprender com a atração que o pet já tem ao nascer. Outra medida (o `D_FE`): o J1 mostrou que ela não separa o aprendiz do instinto |
| **GT-6** (DECIDIDA) | as faixas | **pedir ao coordenador 63101…63505 (o piloto) e 64101…64505 (a validação),** registradas na etapa 1 | uma faixa já usada: as unidades já foram vistas |
| **GT-7** (DECIDIDA) | o I-CORPO e o I-MUNDO | **gates de mecanismo,** conferidos em toda vida e falhando alto, e não contrastes com IC | contrastes: mais primários, menos poder, e uma pergunta que o código já responde por construção |
| **GT-8** (ABERTA) | o prefixo das unidades | **`"pet_que_pensa"`, o do J5,** com as bases novas | um prefixo novo: uma linha na `PREFIXOS_UNIDADES` e unidades que não se comparam com as do J5 |

## 9. Resumo da etapa

(vazio: nenhuma etapa começou)
