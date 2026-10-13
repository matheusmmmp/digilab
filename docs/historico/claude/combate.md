# O combate: V2, V2.1, correções, equilíbrio e treino

Seções movidas inteiras do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13). Os números vêm dos
artefatos citados em cada seção.

## Combate V2 (2026-09-24, `artifacts_combate_v2/`, branch `combate-v2`)

Números abaixo vêm de `artifacts_combate_v2/gates.json`, `matriz.json` e `equilibrio.json`
(sementes de validação 2101…2505, 200 partidas por par por semente, 28.000 partidas; hash das
regras `c26aa2813e23…`, da config `86a28a8adbd1…`). Tudo PROPOSTO. Não substitui a arena v1.

- Bateria **REPROVADA**: G1, G2, G3, G6, G7 ok; **G4 e G5 falham**.
  - G4: mediana 25 turnos (ok), mas 31,3% das partidas acabam no limite de turnos (limiar 20%).
    Vem de pares de bots passivos (tartaruga, contragolpe) que só atacam com o oponente sem guts.
  - G5: `esquivar` em 0,8% das decisões dos bots do suporte (limiar 3%).
- Equilíbrio dos fixos: agressivo 0,327, atirador 0,335, tartaruga 0,338 (ciclo agressivo >
  tartaruga > atirador > agressivo). Aleatório e contragolpe fora do suporte.
- G2: adaptativo × aleatório 0,999, IC95 [0,997, 1,000]; oráculo 0,946 × adaptativo 0,913 contra os fixos.
- **Atenção**: o adaptativo vence todos, inclusive o oráculo (0,962 no confronto direto); no
  equilíbrio com ele incluído (informativo) ele vira estratégia pura. Um único estilo domina.
- G6: condição (HP ±10%, guts ±10) move a taxa no máximo 0,197 (atirador); estilo move 0,388.
- G7 passa pela média (0,705), mas uma das 5 permutações (`02416357`) bate o original (0,009 para o
  original): a ordem importa, e a ordem escrita à mão não é a melhor.
- Calibração (só sementes de calibração, 3 rodadas, `experiments/configs/calibracao_combate_v2.json`):
  `custo_disparo` 15 → 20 (G1), `hp_neutro` 100 → 70 (mediana de turnos). Nenhum número resolveu G4
  (limite) nem G5 (esquiva): são desenho dos bots/regras, não calibração.
- Limites da linguagem de gambits encontrados: não há "última ação do oponente foi X" (k só 2 ou 3),
  nem condição sobre a própria ação anterior, nem negação. Catálogo NÃO foi ampliado.
- G3 mede viés de posição (pontos do lado 0 nos espelhos), porque com lados trocados na metade a
  média do espelho é 0,5 por construção.

## Combate V2.1 — árvore de evolução no combate (2026-09-24, `artifacts_combate_v21/`)

**Pré-condições não cumpridas** (base V2 REPROVADA e sem finta/parry/fuga/morte súbita; tarefa de
personalidade inexistente). O Matheus mandou seguir adaptando; adaptações e interpretações em
`docs/REGISTRO_DESVIOS.md`. Números abaixo vêm de `artifacts_combate_v21/gates.json`,
`matriz_arquetipos.json`, `equilibrio.json`, `matriz_especie_arquetipo.json`, `uso_tecnicas.json` e
`robustez_e5.json` (sementes de validação 4101…4505, 100 partidas por par por semente; E1 = 72.000
partidas; hash das regras `ced939707380…`, config `b860ec4acaf7…`). Tudo PROPOSTO.

- Bateria **REPROVADA**: E1, E2, E3, E4 e E5 falham. Base V2 intacta (hash dos fontes igual).
- **E1**: nenhum arquétipo vence todos, mas o suporte do equilíbrio tem 3 (espelho 0,443, furioso
  0,435, emboscador 0,120), precisa de 4. Ciclo furioso > caçadores > espelho > furioso. Colossos
  fracos (vigia e titã perdem de quase todos).
- **E2**: ferrugem vence as outras três (média 0,629; cirro 0,343). 6 dos 8 arquétipos lutam de
  perto e a soma de stats não gera ciclo entre espécies.
- **E3**: todas as técnicas acima de 5% (16–43%). Resposta declarada reduz o usuário em investida
  (0,625 → 0,606), contra_golpe (0,485 → 0,467) e pele_dura (0,259 → 0,003); **marcar não**:
  "avançar e pressionar" sobe o caçador de 0,625 para 0,953 (quem recua anula quem avança).
- **E4**: duelista 0,785, emboscador 0,788, espelho 0,629 dentro de [0,6, 0,85]; furioso, muralha,
  sentinela, titã e vigia esmagam o adolescente (0,95–1,0): a diferença vem dos gambits e da passiva.
- **E5**: E1 se mantém em 2/36 perturbações (já falha sem perturbar).
- Calibração (só sementes 3101…3505, 2 rodadas, `experiments/configs/calibracao_v21.json`):
  `fracao_espelho_disparo` 0,5 → 1,0; regras do parry e do disparo marcado revisadas; bots do colosso,
  da muralha e as respostas do E3 reescritos. Conversão de stats, custo da pele e multiplicador do
  adolescente testados e não adotados (trocam a espécie dominante ou derrubam o E1).
- A seção "Pesquisa" da especificação foi feita depois (2026-09-25): ver a seção abaixo.

## Pesquisa do V2.1 — pet de pesquisa evolui e luta (2026-09-25, `artifacts_v21_pesquisa/`)

`python experiments/run_pesquisa_v21.py`: evolui as 40 vidas de `artifacts_ablacao/vidas` até adulto
(`digilab/evolucao.py`, `ConfigEvolucaoPesquisa`, tudo PROPOSTO; interpretações em
`docs/REGISTRO_DESVIOS.md`) e luta na arena V2.1 só com adultos, com ablação sem técnicas e passivas.
Números de `artifacts_v21_pesquisa/resumo.json` e `formas.json`; 5 sementes, sem teste estatístico
da distribuição de formas: descritivo.

- **Cuidado não distingue donos**: nenhum dono simulado atende os chamados do bebê; todo pet é arisco.
- **Formas adultas diferem por dono (bandit)**: atencioso 4/5 caçador (3 emboscador); incoerente 4/5
  guardião (3 muralha); aleatório brigão 3/5 e caçador 2/5; relapso espalhado. Instinto (controle,
  sem aprendizado): 20/20 duelista. Nenhuma semente teve a mesma linha nos 4 donos. Caráter adulto do
  bandit: |eixo| máximo com mediana 0,38. Com 5 sementes não dá para separar sinal do dono de ruído
  de vida.
- **Arena (atencioso × aleatório, IC95 bootstrap)**: bandit 0,379 [0,130, 0,638]; bandit sem técnicas
  e passivas 0,741 [0,341, 1,000]; instinto (mesma forma, só a condição difere) 0,585 [0,411, 0,770];
  instinto sem técnicas 0,665 [0,549, 0,785]. Por semente o bandit vai de 0,01 a 0,80: o confronto de
  arquétipos decide. Inconclusivo; a bateria V2.1 reprovada pesa aqui.

## Campanha contra os NPCs (`artifacts_campanha/`) — progressão por lugar (2026-09-26)

`python experiments/run_campanha.py` (`digilab/campanha.py`, `ConfigCampanha`), combate corrigido
(V2C + V21C, `campanha.REGRAS_CAMPANHA`). NPC = stats uniformes, sem técnica nem passiva, estilo
`"<familia>:<nome>"` (`v2`, `v2c`, `v21` sem regras de técnica, `crianca`), campos `estagio` (vida e guts
pelo multiplicador do estágio), `lugar` e `epsilon` opcional. Decisões em `docs/REGISTRO_DESVIOS.md`
(2026-09-25 escada K1–K4; 2026-09-26 progressão). Tudo PROPOSTO.

- **Treino vale 3** em combate (`ConfigTreino.peso_ponto_combate`, `catalogo.com_treino`; arena e campanha).
- **Todo pet treinado vence cada NPC** (decisão do Matheus, 2026-09-26: NPCs fixos e imprevisíveis; treino
  típico de uma vida, tabela `ALCANCE`). Lugares (vencer qualquer rival abre o próximo): Campina —
  Brutamontes (criança, 96, criança arisca, ε 0,5); Torre — Sentinela (tartaruga V2C, 72, ε 0,4), Carcereiro
  (espelho sem técnica, 90, ε 0,5), Porteiro (agressivo V2C, 90, ε 0,5); Cidadela — Soberano (agressivo V2C,
  110, ε 0,5).
- **Validação** (`calibrar_progressao.py --validar`, `criterios_todos_vencem`): nenhuma linha travada em
  nenhum dos 5 NPCs; pet treinado 0,81–0,97. **Custo**: o pet sem treino do estágio sugerido vence 0,39–0,66
  (média); o treino garante a vitória, não a libera. Os critérios anteriores (P1–P4, "básico perde" por
  lugar) ficam só como relatório.
- A medida usa treino uniforme; em algumas linhas ele até piora a luta (muda o ritmo de guts dos gambits).
- Campanha com treino e S2: seção do treino abaixo.

## Reequilíbrio dos arquétipos: V21D validada e nos pets v6 (2026-09-29/30)

`docs/DIAGNOSTICO_ARQUETIPOS.md` → `docs/EQUILIBRIO_RODADA1.md` e `EQUILIBRIO_RODADA2.md` (calibração) →
`docs/VALIDACAO_V21D.md`. Números de `artifacts_combate_v21c/validacao_v21d/criterios.json`.

- **Python:** `ConfigCombateV21D` (subclasse da V21C) tem 7 chaves, todas **desligadas por padrão**. A V21C, a pesquisa
  (V3, E1, confirmatória) e as baterias reproduzem. A variante escolhida, `a_c_e2v_v`
  (`experiments/configs/v21d/validacao.json`), liga quatro chaves:
  - `preparo_sob_pele_oculto`;
  - `muralha_lista_espelho`;
  - `vigia_bate_em_quem_recua`;
  - `vigia_recua_do_preparo_sob_pele`.
- **Validação APROVADA** (`python experiments/validar_v21d.py --conjunto validacao`, uma run, registro commitado antes),
  com o furioso como exceção declarada (decisão do Matheus):
  - 7 formas em [0,40; 0,60]: força de 0,407 (titã) a 0,562 (sentinela), painel de 0,432 a 0,549;
  - A6 passa (mínimo 2 vitórias, o titã);
  - S1, E4 na escala (menor 0,8355), campanha na escala (4 de 5, Sentinela exceção) e E3 da pele dura passam.
- **Relatados:**
  - furioso: força 0,722, painel 0,675;
  - A3: suporte 4;
  - A4: 9 e 7 pares extremos;
  - A5: amplitude 0,316 e 0,424;
  - E3 do contra-golpe não reduz (pelo espelho).
- **Web:** só os pets v6 lutam com a V21D (`CV21D`, `Motor.regras`, `jogarV2(..., R)`); os v1–v5 seguem na V21C.
  - paridade com o Python: `test/paridade_v21d.test.ts`, 272 partidas iguais;
  - descarte único dos saves, versão 2: os v6 de antes saem com o mesmo aviso.
- **Aberto:** o furioso (rodada 3, pela base V2C: C3 contra o avanço ou custo do golpe rápido, com G1–G9 de novo); E2,
  E5, G6b, G8 e G9 não medidos; a pesquisa não usa a V21D.

## Equilíbrio geral, fase 1: as formas (2026-09-30, `docs/PLANO_EQUILIBRIO_GERAL.md`, `docs/EQUILIBRIO_GERAL.md`)

Branch `equilibrio-geral` (o PR é no fim da fase 4). Fases 1–3 só com sementes de calibração; **a fase 4 (validação única, sementes
4101…4505) está feita** (último item desta seção).
- **Python:** `ConfigCombateV21E` (subclasse da V21D) com cinco chaves de lista, **desligadas por padrão**:
  `duelista_defende_do_golpe`, `tita_defende_do_golpe` ("de perto, contra golpe rápido frequente → defender", sai o carregar),
  `espelho_sem_carregar`, `muralha_sem_carregar` e `muralha_contra_golpe_na_pele`. Edições em `bots._lista_v21e`, por cima da
  V21D. A base (custo do golpe rápido, parry, C3) foi medida e **não mudou**: nenhum valor tirou o furioso de ~0,72; o que o
  tira é o parry que já existe, usado pelas formas que o golpe repetido esmagava. Config `experiments/configs/v21e/calibracao.json`;
  `python experiments/calibrar_equilibrio_geral.py --etapa todas` → `artifacts_equilibrio_geral/fase1/` (V21D reproduz a rodada 2).
- **Metas na calibração (V21E):** M-A1–M-A4 passam com as 8 formas, furioso incluído (força 0,450–0,579, painel 0,446–0,554,
  amplitude 0,129, toda forma vence ≥ 3). M-A5 e o que não fechou: `docs/EQUILIBRIO_GERAL.md`, fase 1.
- **Web: pets v9** (`VERSAO_PET = 9` = v8 + combate equilibrado; `CV21E`, `regrasDaVersao`, `BOTS_V21E`, `candidatasV21E`). Os
  v6–v8 seguem na V21D e os v1–v5 na V21C (assinaturas e gabaritos iguais; nenhum save descartado). A Fábrica (sem pet) segue
  na V21D. Paridade: `experiments/exportar_gabarito_v21e.py` → `test/paridade_v21e.test.ts` (136 partidas iguais).
- **Fase 2, a progressão (M-B1–M-B3, calibração):** os scripts `calibrar_escala_v6.mjs`, `calibrar_arenas.mjs`,
  `calibrar_desafiantes_v6.mjs` e `explorar_torre.mjs` medem os pets v9 por padrão (`--v6`: a medição de antes, que reproduz os
  artefatos gravados) → `artifacts_equilibrio_geral/fase2/`. Escala dos v9 = `CESC_V9` (mesma vida e β da `CESC_V6`; as metas de
  estágio passam), fatores dos líderes dos v9 em `arenas.FATOR_LIDER_V9` (Torre 1,5 e Espiral 1,4; os outros iguais) e dos
  desafiantes em `CESC_V9.fatorNpc` (Tortomon 1,53, fecha na grade de 0,01; Puppetmon 1,8; Machinedramon 2,3). Os v6–v8 não mudam.
  Detalhes em `docs/EQUILIBRIO_GERAL.md`, fase 2.
- **Fase 3, o fim de jogo e os itens (M-C1–M-C3, M-D1–M-D3, M-E1, calibração):** `conferir_liga.mjs`, `conferir_instalacoes.mjs`,
  `conferir_fabrica_salao.mjs` e `medir_itens.mjs` medem os pets v9 por padrão (`--v6`: a conferência de antes, byte a byte; `--calibrar`
  na Liga, na Fábrica e no Salão) → `artifacts_equilibrio_geral/fase3/`. Só nos v9: Liga com fator por líder (`liga.FATOR_LIGA_V9`; a cura
  entre as lutas foi medida e ficou 0), Fábrica com as regras gravadas na tentativa (campo `v` do evento `fabrica`, registro do Tamer
  versão 6: V21E, rivais × 0,6, a troca entra inteira; tentativas sem `v` se refazem como antes), Salão com fator por nível
  (`salao.FATOR_SALAO_V9`), Torre e Palácio sem mudança, e os itens (`CIT_V9`): valem só com metade do treino típico do nível, a carta só
  contra NPC da campanha, o chip de regra vai para o fim da lista sem tirar regra, o chip de stat vale a metade. Passam M-C2, M-C3, M-D1–M-D3
  e M-E1; **M-C1 não fecha** (a muralha, 0,085). Detalhes e o que ficou aberto em `docs/EQUILIBRIO_GERAL.md`, fase 3.
- **Fase 4, a validação única (2026-09-30, sementes 4101…4505, tudo congelado; `artifacts_equilibrio_geral/fase4/`):** os scripts das
  fases 1–3 ganharam `--validar` (`calibrar_equilibrio_geral.py --validar`, só `v21d` e `v21e`, conferido contra
  `artifacts_combate_v21c/validacao_v21d/`; `configs/v21e/bateria_v21e_validacao.json` e `bateria_v2c_validacao.json`; os sete `.mjs`
  com `--validar` → `*_validacao.json`), sem mudar o padrão nem os artefatos das fases 1–3. **Passam** M-A1–M-A4 (força 0,451–0,576,
  painel 0,449–0,551, amplitude 0,125, toda forma vence ≥ 3), M-B1–M-B3 (o Tortomon por 0,0062), M-C2 (0,390), M-C3 (0,760–0,8725),
  M-D1–M-D3 (emboscador 0,595) e M-E1 (pior 0,580). **Reprovam:** M-C1 (muralha 0,085, **exceção aceita pelo Matheus em 2026-09-30**:
  perde para os guardiões pelo limite do desafiado e não alcança o MegaGargomon com nenhuma alavanca permitida; **espelho 0,240**, 0,010
  abaixo da faixa, **exceção aceita em 2026-10-01**: a diferença está no ruído entre sementes) e, em M-A5, só o E3 do contra-golpe (0,458 → 0,480; E1, E5, G8, G9 e o guardião passam; E2, E4 e G6b são as exceções de sempre; a base V2C sai byte a byte igual a `validacao_bots/`). O E3 do contra-golpe foi **aceito como exceção em 2026-10-01**; não há mais pendência de aceite na rodada. Nenhum número mudou por causa da validação. Tabela completa, o que reprovou e as exceções em
  `docs/EQUILIBRIO_GERAL.md`, fase 4. PR #96 mergeado em 2026-10-01.

## M1 — confiança de combate e desgaste por rival repetido (2026-09-29, `docs/DESIGN_MVP_M1_CONFIANCA.md`)

Mecânica de jogo (exceção de escopo do MVP), Python e web juntos. Um **estado** derivado das lutas que já estão no log
(nenhum evento novo; o replay recalcula; o save não muda): por rival, um contador de encontros que decai (`novidade =
exp(−λ·m)`: 1 na primeira luta, ≈0,25 na 3ª seguida, ≈0,06 na 5ª); a confiança `c ∈ [−1, 1]` decai para 0 entre as lutas e
é empurrada por `η·novidade·sinal` (a derrota pesa mais pela sensibilidade do temperamento). Só o ε do lutador do pet muda
(`+ κ·max(0, −c)`: a confiança positiva não reduz); a experiência de combate soma a novidade em vez de 1; na web o passo dos
gambits híbridos é `GA.alfa·novidade`. Quatro frases de estado com limiar 0,4 e histerese de 2 h (confiante, inseguro,
entediado do rival, neutro sem frase), ancoradas nas lutas do registro (tela do Pet e linha "Confiança" no Aprendizado).
- **Chave desligada por padrão** (`ConfigConfianca.ligada`, `CONFIG_CONFIANCA_LIGADA` para ligar). Desligada, nada é
  calculado e o resumo é o de antes (V3, E1, confirmatória e voz reproduzem).
- **Web: pets v8** (`VERSAO_PET = 8` = v7 + confiança; uma versão de pet por mecânica). Só eles têm `Motor.conf`, o termo no
  ε de `estiloDoPet`, a novidade na experiência e no passo dos gambits, a frase na tela do Pet e a linha no Aprendizado; a
  assinatura dos v8 inclui a confiança e a dos v1–v7 não muda. Arena, Cidadela (3 lutas seguidas: o mesmo rival repetido),
  Liga (o Mega de cada líder, `liga:<líder>`), Torre/Palácio e Salão (a forma sorteada do rival, `forma:…`) contam como
  qualquer luta, uma entrada por luta da série (`rivalDaConfianca`; `Motor.confEvento` liga cada uma ao evento `l`). Medalhas,
  itens, Fronteira e voz valem para v8 (testes `>= 6`/`>= 7`).
- **Parâmetros**: `ConfigConfianca` em `digilab/config.py` (10 números, todos PROPOSTOS, sem fonte) e `CCF` em
  `web/app/motor/constantes.ts`; registro em `protocol.PARAMETROS_CONFIANCA_M1` (à parte do educacao-v1, então
  `hash_parametros_educacao` das runs V3/E1 não muda); nenhum referendado (`confianca_nao_referendados`).
- **Testes**: `tests/test_confianca.py` (curvas, corte, decaimento, histerese, replay, e o **gate G1**: a vida
  `atencioso@69001` de `run_educacao._vida` byte a byte com `tests/gabaritos/confianca_g1_69001.json`, gerado antes do M1);
  `web/app/test/confianca.test.ts` (**gate G2**: 200 lutas do gabarito `confianca_python.json`, `c` e novidade iguais até
  1e−12, frases de estado iguais); `constantes.test.mjs` confere `CCF` contra o Python; gabaritos v1–v3 e assinaturas v1–v7 intactos.
- **Pendência**: os gates **G3–G5** (teto de efeito, freio de repetição, sem poço nem espiral) e G6 **não foram rodados**:
  pedem o plano de análise registrado antes (`docs/PLANO_ANALISE_M1.md`, sementes de calibração separadas). Até lá a
  chave fica desligada nas runs de pesquisa.

## Correção do combate V2 (2026-09-25, `docs/TAREFA_CORRECAO_COMBATE.md`) — V2C e V21C aprovadas com ressalvas

**Com os bots redesenhados** (`GAMBITS_V2C`, `ConfigCombateV2C.bots_v2c`; configs `v2c/c7.json` e
`v2c/validacao_bots.json`), a validação (`artifacts_combate_v2c/validacao_bots/gates.json`) passa
G1–G9 **exceto G6b**, só pelo atirador: espelho com +5% de condição vence 0,744 (limite 0,65; os outros
estilos 0,54–0,62). G4 11,3% no limite; G5 todas as ações ≥ 3%; G9 28,6% decisivos com ε 0,2; G8 100%.
O Matheus aceitou a exceção do atirador: V2C considerada aprovada. **V21C APROVADA COM RESSALVAS** (exceções aceitas pelo Matheus: E2, E4, G6b, G8; redesenho dos bots adultos tentado e não adotado, `artifacts_combate_v21c/redesenho_bots/`). Validação
(`artifacts_combate_v21c/validacao`, config `v21c/validacao.json`: base V2C, vida por vigor 3 → 2,5 com
`hp_base` 75, marca frágil, resposta ao `marcar` redesenhada). Passam E1, E3 (marcar com resposta 0,612 →
0,312), E5, guardião (6,7% no limite), G9 e S1. Falham **E2** (Ferrugem vence todas por pouco; enfraquecê-la
passa a dominância para a Brasa: falta ciclo entre espécies), **E4** (adulto esmaga adolescente, 0,94–1,0;
o multiplicador de estágio não resolve), **G6b** (espelhos com condição ±5%: média 0,725, sentinela 0,919)
e **G8** (E1 em 69,4% das perturbações). Etapas em `artifacts_combate_v21c/calibracao/v0..v4`. Detalhes da
V2C abaixo (primeira rodada, bots da V2).

Etapas 0–2 feitas; **a V2C não passou na validação** e a Etapa 3 (V2.1 corrigida) não foi iniciada.
`ConfigCombateV2C` (chaves C1–C4 desligadas por padrão: a V2 original reproduz os artefatos),
`experiments/diagnostico_combate.py`, `experiments/configs/v2c/*.json`, gates G6b/G8/G9 e oráculo de N
passos em `run_bateria_combate.py`. Números de `artifacts_combate_v2c/` (`relatorio.json`,
`diagnostico/`, `calibracao/<etapa>/`, `validacao/`). Desvios em `docs/REGISTRO_DESVIOS.md`.

- **Validação (N = 400/par)**: falham G3 (espelho da tartaruga 0,464; ruído com N menor), G4 (20,4% no
  limite), G5 (esquivar e golpe rápido < 3%), G6b (atirador favorecido 0,924) e G9 (57,1% decisivos
  com ε 0,2). Passam G1, G2 (oráculo de 2 passos 0,882 × adaptativo 0,809), G6, G7 e **G8 (100% das
  40 perturbações)**.
- Mudança × gate (calibração): C1 finta: limite 31,2% → 27,7%; C2 parry: 24,9% e **golpe rápido morre**
  (G5); C3 fuga: 24,5%; C4 morte súbita: 22,3%; C5 e C6: nenhum efeito (não adotados); oráculo de 2
  passos: 20,1%. G1 passa em todas.
- **Causa das falhas restantes: os bots, não os números.** Tartaruga × contragolpe e seus espelhos
  terminam 100% no limite (nunca se atacam: morte súbita multiplica zero); os bots do suporte não têm
  regra de esquiva (G5); o espelho do atirador é uma corrida determinística de disparos (G6b).
- Diagnóstico (Etapa 0): Ferrugem 0,67 contra as outras espécies no mesmo arquétipo; vigor 13 → 10 cai
  para 0,56 e zerar `hp_por_vigor` para 0,46: a causa é a conversão vigor → vida. `marcar`: o caçador
  recua e o oponente avança, os passos se anulam e o caçador atira de graça (C3 resolveria na V2.1).

## Treino, sobrecarga e formas sombrias (2026-09-25, `docs/TAREFA_TREINO_SOMBRIO.md`)

Pré-condição da bateria V2.1 dispensada; decisões e interpretações em `docs/REGISTRO_DESVIOS.md`.
`ConfigTreino`, `ConfigSombrio` (dados de `docs/pve_treino.json` e `arvore_evolucao.json`), ações
`TREINAR_*` no `AcaoUsuario` (donos da v1 usam `ACOES_V1`: canônica intacta), `MotorTreino` sobre a
personalidade, formas e passivas sombrias em `combate_v2/v21/`. Calibração: `sobrecarga_forcar`
15 → 25 (ovos de calibração). Números de `artifacts_treino/resumo.json`,
`artifacts_treino/bateria_sombria/gates.json` e `artifacts_campanha/treino.json` (10 ovos, 14 dias,
298 interações por vida em todos os braços). Tudo PROPOSTO.

- **Forçar não compensa, e custa.** Exigente × atencioso: 4/10 exigentes viram sombrios (0/10 nos
  outros braços); vínculo 0,22 [0,16, 0,27] × 0,56 [0,50, 0,61] (diferença −0,35 [−0,42, −0,27]); na
  arena normalizada (treino ×3) o exigente vence o atencioso em 0,43 [0,24, 0,63] (inconclusivo). Na campanha
  com os NPCs imprevisíveis (todo pet treinado vence) todos os braços vencem 0,96–1,00: a campanha não separa
  mais os donos.
- **S1 passa** nas regras V2.1 e V21C: nenhuma sombria vence os 8 normais. Médias contra as normais:
  devastador 0,39, colosso partido 0,16, predador 0,10, bastião rachado 0,10 (regras V2.1).
- **S2 PASSA** (campanha por lugar, treino ×3): tier 2 = o melhor rival da Torre, tolerância 0,02 no
  critério (b). Sombrias (`bots.SOMBRIOS`, `experiments/calibrar_sombrias.py`): "a sombra tira a leitura do
  oponente" — devastador bate com golpe rápido e só solta o pesado com guts ≥ 60 (×1,3); bastião rachado =
  espelho sem as regras que leem o oponente; predador fecha e bate rápido; colosso partido regen ×0,85. S1 passa (V2.1 e
  V21C); E1 com as sombrias passa na V21C e reprova na V2.1 original (suporte 3; ressalva registrada).
- Formas por braço e o resto em `artifacts_treino/resumo.json`. Atencioso × aleatório nesta run: 0,46
  [0,25, 0,68] (inconclusivo).
- Web: o treino entrou antes das runs (pedido do Matheus), com os mesmos números.

## Planilha de progressão e escala de stats (2026-09-28, `docs/TAREFA_PLANILHA_PROGRESSAO.md`)

`python tools/gerar_planilha_progressao.py` (fora de `digilab/`; openpyxl e matplotlib, Python do sistema) →
`artifacts_progressao/planilha_progressao.xlsx`, `curva_progressao.png` e `docs/PROGRESSAO.md` (`--verificar`: duas
gerações iguais, toda entrada com fonte e status). Jornada e escala aprovadas em `docs/JORNADA_JOGADOR.md`.

- **Escala** (`ConfigEscala`, desligada por padrão; `CONFIG_ESCALA_LIGADA`): perfil = pontos do catálogo (soma zero);
  E = vida do estágio (50/200/600/1500) × (1 + 0,03 × pontos treinados). Na campanha o dano vale × E_A/E_B (fração
  exata: invariante a fator comum, `tests/test_escala.py`), a vida perde o multiplicador de estágio, o NPC tem perfil
  neutro e E = vida do estágio sugerido × fator (ε 0,2). Arenas não usam a escala.
- Bateria V21C com a escala (`artifacts_combate_v21c/validacao_escala`): os gates que passavam passam iguais. E4
  redefinido pelo Matheus: o adulto sem treino vence o Champion (sem treino e com +22) em ≥ 0,60, sem teto.
- Campanha na escala (`experiments/calibrar_escala.py`, `experiments/configs/escala/`): 4 de 5 NPCs nas metas (≤ 0,30
  sem treino, ≥ 0,80 com o treino típico); a Sentinela não fecha com nenhum fator (exceção aceita pelo Matheus).
- Web: a escala no motor (`CESC`), ligada pelo app; vários pets com um ativo (`…-guardados`) e o tutorial do Bit. Os pets v6 têm escala
  própria (`CESC_V6`, seção "Escala dos pets v6").
