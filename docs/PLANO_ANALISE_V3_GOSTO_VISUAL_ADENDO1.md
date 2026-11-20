# PLANO DE ANÁLISE V3 — GOSTO_VISUAL, adendo 1 (GV3b): a GV3 de novo, com o enjoo da imagem ligado (2026-11-12, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-12, repassado pela sessão coordenadora.** À pergunta "Libera os três merges e aprova o resto
pela recomendação? (sim a tudo, inclusive repetir a GV3 / ...)", a resposta foi "Sim a tudo". O que está aprovado é repetir a GV3 com o
enjoo ligado, pela recomendação. Este texto foi escrito depois da resposta e só fixa o que a recomendação dizia: tudo igual à GV3, com o
enjoo ligado. As escolhas que o texto teve de fazer (as GV3B-1 a GV3B-8, seção 10) vão ao Matheus no PR, cada uma com a recomendação e o
custo de errar; se ele discordar de alguma, o adendo muda antes da primeira vida. Os números seguem PROPOSTOS e SEM FONTE.
**Nenhuma vida da faixa roda antes de quatro coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus" (o orquestrador confere; feito);
2. a faixa 90101…90505 em `experiments/bancada/faixas.py` (feito, confirmada pelo coordenador, 2026-11-12);
3. este adendo, as configs novas e o código do orquestrador na `main` (o hook H10 e o `tools/pre_run.py` conferem o adendo no `origin/main`);
4. o registro da run (seção 9) num commit empurrado antes da primeira vida (feito neste branch; ver a seção 9).

**De onde vem:** o resultado da GV3 (`docs/RESULTADO_V3_GOSTO_VISUAL.md`, seção 4) leu o negativo com a D-GV-ENJOO-PY-1 (o pet não enjoa e
olha em rajadas curtas) e a D-GV-ENJOO-PY-2 (três efeitos da sonda que não vêm do gosto). O conserto D-GV-ENJOO-PY-3 entrou atrás da
`ConfigEnjooTela`, desligada (D-GV-ENJOO-CER-1 a 16, ajustado ao diagnóstico com as mídias reais, D-GV-VIDEO-9 a 13). Tudo no
`docs/registro/2026-11.md`.

**Este adendo vale sobre o `docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md`** (APROVADO em 2026-11-11, GVP-1 a GVP-8 DECIDIDAS) e não muda o texto
dele nem a leitura da GV3, que fica como está. Onde este adendo não diz nada, vale o plano. O orquestrador confere as duas marcas.

**O que este adendo não afirma:** que o pet "gosta", "enjoa" ou sente tédio. Enjoo, tédio, agrado, escolha e tempo olhando são nomes de
mecanismo e de medida. **Nenhuma alegação de novidade.** Nenhuma referência nova; as do plano seguem como estão (seção 4.1 dele).

## 0. O que muda e o que fica fixo, antes de qualquer vida

| o quê | na GV3b | de onde |
|---|---|---|
| **o enjoo** | **ligado**: a `CONFIG_ENJOO_TELA_LIGADA` no corpo (pelo motor) e no cérebro (pelo DigiBrain), com os números da `ConfigEnjooTela` como estão | D-GV-ENJOO-CER-1 a 11 |
| o desenho genoma × dono | o mesmo: 2 genomas (o próprio e o vazio) × 3 donos (`nenhum`, `calmo`, `agitado`), iguais no cuidado | plano, 2.1 e 2.3 |
| a vida | a mesma: o laboratório com o olhar, o mundo do produto, o corpo do v11 com a tela, a TV do jogo (fonte "grade"), o agrado só no sinal (GVP-5), 14 dias | plano, 2.4 |
| a familiarização | a mesma: os dias 0 a 6, o critério 0,05, a análise principal com todas as vidas e a "só estáveis" ao lado | plano, 2.2; GVP-2 |
| a sonda | a mesma: os dias 7 a 13, as 10 h, 3 réplicas, 240 ticks, as duas TVs a 3 células, em direções opostas | plano, 3; GVP-6 |
| os perfis A e B | **os mesmos**: A = C/5 e B = 4C/5 em todos os canais (a GV3B-3 diz por quê) | plano, 3; GVP-3 |
| as medidas | as mesmas: a escolha, o tempo relativo, o tempo total, Δ_I e Δ_agora (o agrado sem o tédio, como na GV3) | plano, 4 |
| a análise | a mesma: a função `analisar` do orquestrador, sem mudança; o bootstrap por unidade, 2000 reamostras | plano, 5 |
| a regra da GVP-7 | a mesma: o piloto só mede o custo e confere que o pet olha; abaixo de 1 réplica em 4 com uma olhada, a run não roda e volta ao Matheus | plano, 6; GVP-7 |
| o tamanho | o mesmo: o piloto 2 bases × K = 2 (24 vidas) e a run 3 bases × K = 12 (216 vidas) | plano, 6 |
| a faixa | **nova**: 90101…90505 (o piloto 90101 e 90202, a run 90303, 90404 e 90505) | seção 6 |
| a derivação das unidades | a mesma regra (`gosto-visual`, `gosto-visual-genoma`, `gosto-visual-politica`, `gosto-visual-boot`); com as bases novas, unidades novas | plano, 2.1; GV3B-6 |

## 1. A pergunta

A mesma Q do plano (seção 1), com o enjoo ligado: depois de 7 dias com a TV da vida, entre duas TVs com programas que o dono nunca
mostrou, (a) qual o pet olha primeiro e (b) que fração do tempo olhando vai para cada uma; e quanto disso acompanha o agrado inato do
genoma, quanto acompanha o programa que o dono pôs. A diferença é o mecanismo: agora o pet tem a habituação presa ao estímulo, a memória
curta do que viu, o enjoo lembrado de cada TV e a exposição que satura (D-GV-ENJOO-CER-2 a 8).

## 2. O que o enjoo faz na vida e na sonda (os fatos que as expectativas usam)

- **Na vida:** olhar a TV da vida sobe o enjoo do protótipo do programa visto, e o enjoo lembrado da TV entra na unidade de olhar como o
  termo `enjoo` (D-GV-ENJOO-CER-3 e 4). O dono `calmo` e o `agitado` trocam o canal a cada hora para o programa dele: o pet olha esse
  programa mais vezes e enjoa dele.
- **Na sonda:** as duas TVs têm ids novos (2 e 3), então o cérebro começa a janela sem enjoo lembrado delas, como na GV3 começava sem o
  termo `gosto` (D-GV-P1e-2). A memória do corpo, não: se o perfil A ou o B fica a até `raio_mesmo` (0,15 C, a distância média por canal)
  de um protótipo que a vida enjoou, o pet já chega enjoado daquele perfil. Os perfis não estão na grade (a sonda confere), mas um programa
  da grade pode estar perto.
- **Dentro da janela:** o pet que olha uma TV enjoa dela (um olhar leva o enjoo à metade do que falta) e o termo `enjoo` empurra para a
  outra; o agrado efetivo (o agrado menos o tédio) entra no termo `gosto`.
- **Os efeitos da sonda que não vêm do gosto, com o enjoo:**
  - **a assimetria da novidade sai:** a novidade conta a mudança nos dois sentidos (D-GV-ENJOO-CER-5);
  - **o falso susto sai, o salto real fica:** o salto de volume é medido contra o último estímulo visto, e não contra os zeros de quando o
    pet não olhava (D-GV-ENJOO-CER-6). Passar de A (C/5) para B (4C/5) ainda sobe o volume em mais que C/2 e dá susto; de B para A, não. O
    primeiro olhar a B pode dar susto ou não, conforme o volume do último programa da vida que o pet viu;
  - **o estresse de B fica:** o volume e o movimento de B (0,8 C) passam do `estresse_corte` (0,75 C), a GV-17 (D-GV-ENJOO-CER-7).

  Os dois que ficam valem para todo pet, inclusive o vazio (Δ_I = 0), e a leitura os cita ao interpretar qualquer diferença entre A e B.

## 3. Os perfis A e B (decididos agora; GV3B-3)

Ficam A = C/5 e B = 4C/5 em todos os canais. O diagnóstico com as mídias reais (D-GV-VIDEO-12) achou o volume no máximo no nível 6 de 15
(perto de 0,4 C) e o movimento no máximo em 11 de 15 (perto de 0,73 C), e a D-GV-VIDEO-13 sugeriu perfis dentro dessa faixa. Isso não cabe
no desenho:
- a GVP-3 pede A e B simétricos em volta de C/2 (o ótimo do genoma vazio), para o controle ter Δ_I = 0 por construção. Com o volume das
  duas abaixo de 0,4 C, a soma fica abaixo de 0,8 C e não chega a C; nenhum par simétrico cabe na faixa real do volume;
- um par assimétrico daria ao vazio um Δ_I diferente de 0 e tiraria o controle do dono sem o genoma (plano, 5.3);
- mudar os perfis junto com o enjoo poria duas mudanças numa run que quer ler uma.

O preço: o estresse de B e o salto real de A para B ficam na sonda (seção 2), e a leitura os cita, como a D-GV-ENJOO-CER-7 já pedia.

## 4. As expectativas, escritas antes (para conferir, não para decidir)

- **E1 (a mesma):** a escolha média fica perto de 0,5 em todas as células. O cérebro começa a janela sem o enjoo lembrado das duas TVs, e a
  linha da classe `tela` não lê o agrado (D-GV-P1e-4). Uma memória do corpo enjoada de A ou de B não muda a primeira olhada, porque o pet
  só a lê depois de olhar.
- **E2 (a da GV3, agora com o mecanismo):** o tempo relativo acompanha Δ_I no genoma próprio. Com o enjoo, o tempo relativo passa a ter a
  habituação que a E2 do plano contava: o pet sai mais cedo da TV de agrado efetivo baixo e fica mais na de agrado alto. O efeito pode ser
  pequeno, porque o enjoo também empurra o pet de uma TV para a outra e puxa o tempo relativo para 0,5.
- **E3 (a mesma):** a parte do dono é menor que a do genoma. A exposição agora satura (o U invertido), então o deslocamento do agrado pelo
  dono deve ficar menor que na GV3.
- **E3b (nova):** com o enjoo, a parte do dono pode sair com o sinal trocado. O pet do `calmo` olhou muitas vezes um programa perto de A e
  pode chegar à sonda enjoado de A, se o programa estiver a até 0,15 C de A; o mesmo para o `agitado` e B. Então `calmo − agitado` no tempo
  relativo pode ficar abaixo de 0. A E3b é escrita antes para a leitura poder citá-la; ela não muda a regra das frases (seção 5).
- **E4 (nova, descritiva):** o tempo total na sonda e a fração olhando a TV da vida ficam menores que na GV3, porque o pet enjoa. É só uma
  expectativa de leitura lado a lado (seção 7), sem teste.

## 5. As frases que a leitura pode escrever

As mesmas da 7.2 do plano, sem mudança:
- "**A parte do genoma aparece** no tempo relativo com o dono X" só se o IC95 do Spearman(Δ_I, tempo relativo) ficar todo acima de 0.
- "**A parte do dono aparece** no genoma G" só se o IC95 de `calmo − agitado` no tempo relativo ficar todo acima de 0.
- "**Não aparece com 36 unidades**" quando o IC95 contém 0. Nunca "não existe".
- Um IC95 todo **abaixo** de 0 é escrito como está ("o contrário do esperado") e não vira acerto. Na parte do dono, a leitura pode citar a
  E3b como a explicação escrita antes, sem trocar a frase.
- Nenhuma frase compara com animais, diz que o pet gosta ou enjoa, ou diz que o modular supera o A.
- Toda diferença entre A e B é lida com o estresse de B e o salto de A para B (seção 2); a leitura não atribui ao gosto nenhuma diferença
  que esses dois efeitos expliquem.

## 6. As sementes, o tamanho e a máquina

- **A faixa:** 90101…90505, em `FAIXAS_RESERVADAS` (confirmada pelo coordenador, 2026-11-12), no molde da 89xxx. Ela não cruza as
  reservadas nem as queimadas (o `tests/test_gosto_visual_gv3b.py` confere), e as unidades dela não colidem com as da GV3.
  - **90101…90202, o piloto:** as bases 90101 e 90202, K = 2 (4 unidades, 24 vidas). Só mede o custo e confere que o pet olha nas sondas
    (a GVP-7: a fração das réplicas com uma olhada ≥ 0,25). **Nada se ajusta olhando para ele.** Se a conferência falhar (o enjoo pode
    fazer o pet olhar menos), a run não roda, o piloto é registrado como está e o caso volta ao Matheus com um adendo novo.
  - **90303…90505, a run:** as bases 90303, 90404 e 90505, K = 12 (36 unidades, 216 vidas), **uma vez**.
- **O custo** (PROPOSTO, SEM FONTE): a GV3 levou 23,5 s por vida em média e 1273,7 s de parede com 4 processos
  (`docs/RESULTADO_V3_GOSTO_VISUAL.md`, seção 0). O enjoo põe poucas contas por tick; a estimativa é a mesma ordem, e o piloto mede.
- **A máquina (V3-D8):** no máximo 4 processos (o orquestrador recusa mais) e uma run de pesquisa por vez (o `tools/pre_run.py` confere).
- **A calibração separada da validação:** não se aplica, como no plano: nada é calibrado.

## 7. A comparação com a GV3 original (só descritiva)

As duas runs têm faixas diferentes (36 unidades diferentes) e configs diferentes (o enjoo). Uma diferença entre os números das duas mistura
o mecanismo com o sorteio das unidades, e o plano não previa um teste de diferença entre runs. Por isso:
- o `docs/RESULTADO_V3_GOSTO_VISUAL_ENJOO.md` (ou uma seção nova do resultado da GV3) põe as duas tabelas lado a lado: as seis células, a
  parte do genoma, a parte do dono, a interação, a divergência, a familiarização e o custo, cada número com o IC95 da própria run;
- a leitura compara só o que cada run diz pela regra da seção 5 ("aparece" ou "não aparece com 36 unidades" numa e na outra);
- não há teste de diferença entre as runs, não se juntam as 72 unidades numa análise só, e nenhuma diferença entre as duas tabelas é
  atribuída ao enjoo. Uma frase como "na GV3 o IC95 contém 0; na GV3b fica todo acima de 0" é permitida; "o enjoo fez aparecer" não é;
- a GV3 não é relida nem refeita, e nada da GV3b se ajusta olhando a GV3.

## 8. O negativo

Todo resultado é registrado como está: nenhuma parte aparecer de novo, a familiarização não estabilizar, uma medida sem variância, o pet
quase não olhar, o piloto falhar a GVP-7. Nada se reroda com outro número do enjoo, outra janela, outro perfil ou outra faixa para "achar" o
efeito; uma mudança depois da run é um adendo novo, com faixa nova e o ok do Matheus.

## 9. O registro da run

Escrito em 2026-11-12, antes de qualquer vida da faixa, no branch `v3-gosto-visual-gv3b` (criado de `origin/v3-gosto-visual-enjoo-cerebro`,
o PR #875, porque o #875 ainda não estava na `main`).
- **O ok do Matheus:** 2026-11-12, repassado pela sessão coordenadora: "Sim a tudo", à pergunta "Libera os três merges e aprova o resto pela
  recomendação? (sim a tudo, inclusive repetir a GV3 / ...)" (D-GV-GV3B-1).
- **O commit do código:** `0db18119` (o orquestrador, as configs, a faixa e o teste; este adendo entrou junto, com os campos deste
  registro ainda vazios). Este registro foi completado num commit próprio por cima dele, que só muda documentos. Antes do piloto, quem roda
  confere que os sha256 abaixo são os da `main`; se o merge do #875 ou desta etapa mudar algum desses arquivos, a diferença é registrada
  antes da primeira vida, e o `meta.json` de cada pasta grava o `git_head` e os sha256 de novo.
- **Os sha256** (o conteúdo no commit do código):
  - o orquestrador `experiments/run_v3_gosto_visual.py`: `0b8e150f079b5125cbc76c9a319e9dbef6ef21328919d130b6e799373a6364ec`;
  - a sonda `experiments/sonda_duas_tvs.py` (sem mudança desde a GV3): `d3eee15766dc1cbfa616854997dd55ae4571c1ec94a6a327464c8dad7067b5d3`;
  - o `digilab/metrics.py`: `7d6eed8b6f4134bde4b37f367fef1d256fdc9b73b8cfcd9c834c544d2b0d94fd`;
  - o `digilab/config.py` (a `ConfigEnjooTela`): `a5371d3e68b255c331debbad6b85836681b4495cfb7df8ee9da88a90379c094d`;
  - o `digilab/corpo.py`: `ed198a4a664f4d451b88d63ef625fe63006a9996869bbd4b33ddf1ef4c5e256f`;
  - a config do piloto `experiments/configs/v3_gosto_visual/piloto_enjoo.json`: `8cd1ab9e3d63533d279384f51facefa76bab0dd7c43db7372905fba52e6c1037`;
  - a config da run `experiments/configs/v3_gosto_visual/gosto_visual_enjoo.json`: `694ac4c6412a288c0a384da31d16a9b770dea8e7fbdd7fb590f57d12deb20edb`;
  - o sha256 deste adendo não cabe nele mesmo e fica no `meta.json` de cada pasta (`plano_sha256`), com o do plano da GV3
    (`plano_base_sha256`) e a config do enjoo inteira (`enjoo_tela`).
- **As configs:** `piloto_enjoo.json` (bases 90101 e 90202, K = 2, 14 dias: 4 unidades, 24 vidas) e `gosto_visual_enjoo.json` (bases 90303,
  90404 e 90505, K = 12, 14 dias: 36 unidades, 216 vidas), as duas com a fase `gosto_visual_enjoo` e este adendo como `plano`.
- **Os comandos**, 4 processos (V3-D8), cada um numa pasta nova (o orquestrador recusa gravar por cima), só depois deste adendo e do código
  na `main`:
  - o piloto: `python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/piloto_enjoo.json --processos 4`,
    em `artifacts_v3_gosto_visual/piloto_enjoo/`;
  - a run, só se o piloto passar na conferência da GVP-7 (`analise.json`, `conferencia.a_run_pode_rodar`), uma vez:
    `python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/gosto_visual_enjoo.json --processos 4`, em
    `artifacts_v3_gosto_visual/gosto_visual_enjoo/`.
- **A faixa:** 90101…90505, em `FAIXAS_RESERVADAS`; conferido em 2026-11-12, depois de um `git fetch`, que nem a `origin/main` nem nenhum
  branch remoto registra uma faixa que a cruze.
- **A máquina:** conferir antes do piloto que nenhuma outra run de pesquisa roda (o `tools/pre_run.py` confere).

## 10. As escolhas deste adendo (com a recomendação e o custo de errar)

A repetição está aprovada pela recomendação (o cabeçalho). Estas são as escolhas que o texto teve de fazer; cada uma segue a recomendação
e vai ao Matheus no PR.

| id | a escolha | a recomendação (a seguida) | o custo de errar |
|---|---|---|---|
| **GV3B-1** | Ler o "Sim a tudo" como a aprovação de repetir a GV3 com o enjoo ligado, com tudo o mais fixo. | **Sim**, e marcar o adendo APROVADO com a citação. | Se o Matheus queria mudar mais coisas, a run responde a outra pergunta; o PR leva as escolhas antes da primeira vida. |
| **GV3B-2** | A `CONFIG_ENJOO_TELA_LIGADA` como está, sem mexer nos números. | **Sim**: os números foram escolhidos antes da run, no conserto, ajustados ao diagnóstico com as mídias reais. | Mexer agora, sem dado novo, é ajustar no escuro; deixar como está pode dar um enjoo forte ou fraco demais, e o resultado fica registrado como está. |
| **GV3B-3** | Os perfis A = C/5 e B = 4C/5, os mesmos. | **Sim** (seção 3): nenhum par simétrico cabe na faixa real do volume, e mudar os perfis junto com o enjoo poria duas mudanças numa run. | Os perfis fora da faixa real deixam o estresse de B e o salto de A para B na sonda; a leitura os cita. |
| **GV3B-4** | A E3b (a parte do dono com o sinal trocado pelo enjoo) escrita antes, sem mudar as frases. | **Sim**. | Sem ela, um IC abaixo de 0 pareceria inexplicado; com ela mudando as frases, viraria acerto depois do fato. |
| **GV3B-5** | A comparação com a GV3 só lado a lado, sem teste de diferença e sem juntar as runs. | **Sim** (seção 7). | Um teste novo depois de ver a GV3 seria análise não registrada; juntar as runs misturaria dois mecanismos. |
| **GV3B-6** | A mesma regra de derivação das unidades, com as bases novas. | **Sim**: unidades novas e sem colisão com as da GV3 (o teste confere). | Um prefixo novo mudaria a bancada sem ganho; reusar as bases da GV3 queimaria a faixa dela. |
| **GV3B-7** | A fase `gosto_visual_enjoo` na config escolhe o enjoo, e as pastas `piloto_enjoo` e `gosto_visual_enjoo`. | **Sim**: as configs antigas ficam como estão, e a GV3 não é gravada por cima. | Uma chave nova na config mudaria a validação das configs antigas. |
| **GV3B-8** | O Δ_agora com a mesma definição da GV3 (o agrado sem o tédio). | **Sim**: "as mesmas medidas"; o agrado efetivo na cópia seria medida nova. | O Δ_agora não mostra o tédio; o tédio aparece no comportamento (o tempo relativo), que é o que se lê. |
