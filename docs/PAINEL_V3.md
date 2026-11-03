# PAINEL V3: onde a V3 está, em uma página

**Atualizado em 2026-11-03** (`main` `6b54b48`, depois do #549), pelo Gerente da V3. O plano é o `docs/PLANO_V3.md`; o
fechamento da V2, o `docs/FECHAMENTO_V2.md` (tag `v2-final`).

- Quem atualiza: o coordenador de cada trilha, uma linha por PR mergeado.
- Regra (herdada do `PAINEL_V2.md`): cada linha cita o documento ou o PR de onde veio; aqui não entra número novo.

## 0. A V3 em uma frase por trilha

| trilha | a pergunta | terminou quando |
|---|---|---|
| **C · cérebro** | os mecanismos que a triagem de 2026-10-30 aponta explicam ou corrigem as falhas do modular no longe e no hábito, testados com controle? | C1 e C2 rodaram uma vez; C3 e C4 com espec, código e plano; a espec do modular revista com [MECANISMO], [HIPÓTESE] e [EXISTE] |
| **L · layout** | o jogo fica inteiro no layout habitat, nas duas peles, com a primeira peça do modular com paridade? | M7 e T1–T3 na `main` com as capturas aprovadas; L3 na `main`, ou a decisão de não levar peça ainda |
| **B · batalha** | o combate em tempo real fecha as metas com o candidato v14, a ponto de ligá-la? | a conferência da rodada 2 rodou uma vez, e o Matheus decidiu ligar ou não a v14 |

## 1. As missões

| missão | o que é | estado | onde |
|---|---|---|---|
| infra · o prefixo V3 | o CI e as ferramentas aceitam `TAREFA_V3_*` e `PLANO_ANALISE_V3_*` | **na `main`** (#478) | `docs/TAREFA_V2_INFRA_PREFIXO_V3.md` |
| congelamento · V3-D5 | o cabeçalho "V2, congelado" e a última linha do `PAINEL_V2.md` | **na `main`** (#483) | `docs/PLANO_V3.md`, seção 7 |
| **C0** literatura | as fontes da triagem verificadas, a síntese e a alegação proibida nova | **na `main`** (#482) | `docs/TAREFA_V3_LITERATURA.md` |
| **C1** longe regular | o longe com lugares fixos; LR-1 a LR-7 e C1-E1/E2 DECIDIDAS (2026-10-30, pela recomendação) | **rodou uma vez, na `main`** (#510): o primário passa (M3\* − M2 por episódio no `longe_fixo`, IC95 > 0); o sorteado sai "indeterminado", então a L-3 fica fora (C1-E2); a primeira run caiu por um fim desconhecido no orquestrador (#507), consertado no #508, e a repetição deu os mesmos logs. Antes: o `longe_fixo` (#503), o adendo 6 (#497), o orquestrador e a C5 (#506) | `docs/TAREFA_V2_LONGE_REGULAR.md` |
| **C2** o hábito com crédito na intenção | o crédito do P2 na corrida do comportamento (M2c) contra o passo; HI-1 a HI-8 DECIDIDAS (2026-10-31, pela recomendação) | **rodou uma vez, na `main`** (#517): as premissas passam; o P-A, M2c − M2, sai "≈ 0" (+0,0028 [−0,0003; +0,0060]), e o S1 "< 0"; linha 4 do adendo 7: a unidade de crédito não é a causa. As D-C2-4-1 a 4, decididas pelo Matheus em 2026-10-31: a C2 registrada como negativa, sem mecanismo novo no P2, a C3 em separado, nenhuma combinação C2+C3. Antes: a tarefa (#512), a corrida atrás de chave (#513), o adendo 7 e o orquestrador (#515) | `docs/TAREFA_V3_HABITO_INTENCAO.md`; `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, seção 14 |
| **C3** redecidir por evento | a escolha só é refeita num evento (receptor, reflexo, mundo, fim, teto), contra o sorteio a cada decisão; M3\*R − M3\* por episódio no `longe_fixo` | **rodou uma vez, na `main`** (#527): as premissas passam; o P-R, M3\*R − M3\*, sai "indeterminado" (+0,0124 [−0,0060; +0,0308]), a guarda do comedouro não falha; linha 6 do adendo 8: nada se decide, a `redecidir_evento` fica desligada. As D-C3-4-1 a 3, decididas pelo Matheus em 2026-11-01: sem repetir na 76xxx, a próxima é a C4, os testes do `conferir_saude` à parte (#528). Antes: a tarefa (#519), a espec e o código atrás de chave (#521), o adendo 8 e o orquestrador (#526) | `docs/TAREFA_V3_REDECIDIR_EVENTO.md`; `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, seção 15 |
| **C4** memória autobiográfica | ME-1 a ME-7 DECIDIDAS (2026-10-30, pela recomendação), com as entradas da C0 e as C4-E1 a C4-E3 | a espec das M0 a M7 APROVADA (#529), com as MA-1 a MA-8 e os valores DECIDIDOS pelo Matheus em 2026-11-01, pela recomendação; a M0 e a M1 **na `main`** (#530), atrás da `memoria_autobio` desligada; o afeto pela subida no lugar do nível e o registro reconciliado **na `main`** (#532; o `theta_afeto` sem uso vai ao Matheus); a M2 e a M3 (a lembrança, o lugar pela soma, a consolidação) **na `main`** (#533); a M4 (o termo da lembrança e a sonda `sem_lembranca`) **na `main`** (#534); a M5 (as três facetas atrás da `facetas_mem`, a sonda `sem_faceta`, a `cautela_comida` no sentido natural) **na `main`** (#535); a M6 (a fala só alega memória, causa e faceta que o registro sustenta, Python e web com paridade; o motivo do N6 consulta a sonda) **na `main`** (#536); o `controle_mem` (os braços REL, SEM, REC, EMB e REL sem negativos) **na `main`** (#539); o adendo 9 APROVADO **na `main`** (#540); **a run única rodou, na `main`** (#541): as premissas passam, o Holm rejeita os três contrastes do primário (REL − SEM +0,0646 [+0,0515; +0,0778]) e a guarda não falha; a linha 3 de A9.7, a `memoria_autobio` REL candidata; as D-C4-1 a D-C4-4 DECIDIDAS pelo Matheus (2026-11-01, pela recomendação); o porte ao jogo é a L3 | `docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md`; `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`, seções 8 a 11 |
| **C5** viabilidade do corpo | as medidas do corpo fora da faixa, do replay | medidas na `main` (#506) e lidas na C1 (#510), nos termos do AD6-4 | `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, adendo 6 |
| **L1** M7 do layout | o fechamento do layout habitat | **na `main`** (#477) | `docs/TAREFA_V2_LAYOUT_HABITAT.md` |
| **L2** tema dos menus T1–T3 | a pele Vidro como padrão, a escolha em Ajustes, as capturas nas duas peles | T1 (#486), T2 (#499) e T3 (#505) **na `main`** | `docs/TAREFA_V2_TEMA_MENUS.md`, seção 5 |
| **L3** o modular no jogo, em modo laboratório | o DigiBrain modular inteiro na configuração validada (o M3\* da C1 e a `memoria_autobio` REL da C4), atrás de uma chave desligada, num pet de teste (a **v16**: a v15 é do #525); o A v11 segue o padrão. Substitui a L3 de uma peça só (Matheus, 2026-11-01) | a tarefa e as LAB-1 a LAB-5 **na `main`** (#542); o motor inteiro em TS com paridade **na `main`**: o gabarito (LM0, #543), sens, afeto e impulso (LM1, #545), estado, arb e plast (LM2, #546), a memória (LM3, #547), o adapt e o laço com o pet v16 (LM4, #548: o G-PAR-VIDA em 5 376 decisões, o G1 e o G2); as pranchas **na `main`** (LM5a, #544; o pet já nascido e o Descartar, #549), com as LM5-1 a LM5-9 DECIDIDAS; a tela (LM5b) **em voo**, antes da B3 por pedido do Matheus (2026-11-03). Sem G-PAR: o `sumiu` e o `desistiu` das intenções com alvo, que não ocorreram nas vidas tentadas | `docs/TAREFA_V3_LAB_MODULAR.md` |
| **L4** habitat como ilha 3D | a cena do modo mundo (v12) como ilha 3D, com o pet em papel; só vista | H0 a H5 **na `main`** (#488 a #494; a H1b liga o `CLIPES_UP`); faltam as capturas aprovadas e a M3 | `docs/TAREFA_V3_HABITAT_ILHA_3D.md` |
| **B1** rodada 2 do equilíbrio | as fases do `PLANO_EQUILIBRIO_COMBATE_TR_R2.md` | **na `main`**, com a conferência única (R2-5, #502): 13 metas passam, 14 falham | `docs/EQUILIBRIO_COMBATE_TR.md` |
| **B2** ligar a v14 | o pet v14 com o candidato da conferência; a v13 viva (CV14-1) | **na `main`** (#504); o Matheus decidiu ligar já (2026-10-30), contra a recomendação de esperar a rodada 3 | `docs/TAREFA_V3_COMBATE_V14.md` |
| **B3** a luta no layout novo | o HUD e o palco na pele dos menus | a tarefa e as pranchas **na `main`** (#537), com as B3-1 a B3-5 aprovadas; o código não começou e vai partir da tela que a LM5b deixar | `docs/TAREFA_V3_LUTA_LAYOUT.md` |
| **L** balões e HUD (fora do plano, sessões próprias) | os balões soltos vão ao painel Estado; o HUD da tela Pet | **na `main`** (#498, #501) | `docs/TAREFA_V2_LAYOUT_HABITAT.md`, `docs/TAREFA_V3_LAYOUT_HUD.md` |

## 2. Decisões abertas do Matheus

- **A L4:** aprovar as capturas da ilha (390 e 1280; claro, escuro e noite) e medir a M3 com `?medir3d=1` no desktop e num celular.
- **A D-C1-3:** de onde vem o ganho do M3\* no `longe_fixo` (nenhuma visita ao lugar lembrado achou ração): questão aberta, sem run; um descritivo com plano próprio antes de o modular virar o cérebro padrão (o laboratório da L3 não espera por ela).
- **Os hooks** (`.claude/hooks/` e `.claude/settings.json`) apagados pelo `2586b0e` (a H2): 43 falhas na suíte; um card proposto para restaurar.
- **A CV14-1:** a v13 continua viva (pela recomendação, até o Matheus dizer outra coisa); um pet v13 enfrenta a Fábrica v14, que é da conta.

### 2.1 Pendências (2026-11-03)

Cada uma com a recomendação do Gerente e o custo de errar.

- **O PR #525 (habitat: o saco de pancada, o treino e a bola, pet v15) em conflito** com a LM4 (`motor.ts`, `motor_corpo_mundo.ts`,
  `constantes.ts`, `tipos.ts`, `combate.ts`) e, depois da LM5b, com a tela Pet. Recomendação: a sessão dona junta a `main` depois do merge da
  LM5b, uma vez só. Custo de errar: juntar antes obriga a juntar de novo quando a LM5b entrar.
- **A cobertura do `sumiu` e do `desistiu` nas intenções com alvo** (ir à comida, à bola, ao lugar): portados, sem G-PAR-VIDA (LM4).
  Recomendação: deixar como está até um cenário que os produza; registrado na tarefa. Custo de errar: um erro nesses ramos só aparece jogando.
- **O rótulo `livre-v9`** quando a fala de memória for gravada no modo livre. Recomendação: entra junto da primeira fala de memória gravada
  (a LM5b diz se liga a fala). Custo de errar: uma fala livre gravada sem rótulo de versão não se separa das antigas no log.
- **As worktrees antigas no `D:`:** seis não foram removidas na limpeza de 2026-11-01 (duas sem merge, `v3-habitat-objetos` e
  `v3-poc-orgaos-genetica`; duas com mudanças, `v3-habitat-mapas` e `v3-c4-proveniencia`; duas destacadas, `v3-capturas-peles` e
  `v3-habito-intencao-run`), e duas pastas vazias travadas em `v3\.claude\worktrees\` (`agitated-rubin-b2128e`, `cool-panini-6f93b7`).
  Recomendação: o Matheus olha as quatro primeiras; as duas destacadas e as pastas vazias saem quando nada as segurar. Custo de errar: apagar
  uma worktree com mudança perde trabalho que não está no git.
- **As worktrees das etapas do laboratório** (`v3-lab-modular`, `v3-lab-modular-lm0` a `lm4`, `lm5a`, `lm5a2`), já na `main`: removíveis com
  `git worktree remove`, sem força, quando o Matheus disser.

## 3. Riscos

| risco | o que se vê | onde |
|---|---|---|
| o aprendiz no mundo físico | o P1 perde do instinto (J1); o modular fecha 0,41 no longe só no cheiro contra 0,74 no comedouro | `docs/FECHAMENTO_V2.md`; `docs/TAREFA_V2_LONGE_REGULAR.md`, seção 1.1 |
| a alegação de novidade | a combinação corpo + aprendizado + memória já foi publicada; o ponto defensável é o teste causal com controle | `docs/PLANO_V3.md`, seção 2.2 |
| a máquina | WHEA 19 e o access violation de 2026-10-28; ≤ 4 processos, uma run por vez (V3-D8) | `docs/PLANO_V3.md`, seção 7 |
| arquivos disputados | `App.tsx`, `tokens.css`, `pet.css`, `Nav.tsx` (L2, L4, B3) e `digilab/digibrain/` (C2, C3, C4): uma missão por vez | `docs/PLANO_V3.md`, seção 5 |
