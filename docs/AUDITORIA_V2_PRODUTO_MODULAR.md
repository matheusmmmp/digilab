# Auditoria do estado real: o pet jogável e o DigiBrain modular (2026-10-24)

Status: **auditoria, só leitura do código**. Ela foi feita na `main` `a06e19d` e conferida de novo em `644309c`, depois do merge do #396
(a validação da competição) e do #398 (o ovo no 3D). Foi pedida pelo PROMPT MESTRE do Matheus (2026-10-24), repassado pelo Gerente. O
texto integral do pedido fica fora do repositório, em `_ref/TAREFA_PROMPT_MESTRE_MODULAR.md`. Nada aqui mudou código, e nada rodou.

**A classificação** usada em cada linha:

| marca | quer dizer |
|---|---|
| **[T]** | implementada e testada na `main` (o código e o teste existem; o teste vai citado) |
| **[S]** | implementada, sem validação científica (ou com a validação falhando) |
| **[R]** | resultado experimental observado, com artefato em disco |
| **[P]** | proposta ou tarefa, ainda não implementada (só documento) |
| **[X]** | inexistente ou bloqueada |

**Regra de leitura:** código, teste de mecanismo, experimento e funcionalidade do produto são coisas diferentes. Um documento ou um PR
não comprova integração no jogo. "No jogo" quer dizer `web/app/src/` usando o motor TS (`web/app/motor/`); "na pesquisa" quer dizer
`digilab/` e `experiments/`.

## 1. Respostas curtas

| pergunta | resposta | marca |
|---|---|---|
| O que é o cérebro A? | uma tabela de pesos inteiros (S = 1024), com um escore linear por (regra, ação, entrada) e um sorteio proporcional, sobre os candidatos que a regra do instinto propõe (`digilab/policies/lobos.py:405-485`, `962-1026`). Os "lobos" são estágios com nome dentro de uma classe só, não módulos que se trocam (`lobos.py:3-4`). **Não é rede neural e não tem estado recorrente** (`tools/connectome_cerebro_a.py:3`) | [T] código; [S] ciência |
| Que cérebro roda no jogo web? | o A **v11** para os ovos novos (`web/app/motor/constantes.ts:47`; `motor.ts:223-239`; `pet_v11.ts:8-16`), sem as chaves do mundo, das frutas, do plano, do paladar, do social e do banheiro (`lobos.ts:411`). Os pets v1 a v10 seguem com o bandit | [T] |
| A arquitetura modular existe? | **não como arquitetura.** Existem peças: o corpo químico com receptores, a memória de episódios N6 (só na escolha da fruta), o planejador do J5, a competição entre regras (V3-3/4). O único estado recorrente do repositório é o do cérebro B (CfC), que **não aprendeu** (`docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`) | peças [T]/[R]; a arquitetura [P] |
| O mundo físico está no jogo? | **não.** O `Mundo` TS (`web/app/motor/mundo.ts:339`) só é usado em testes de paridade (`test/mundo.test.ts`, `test/contrato.test.ts`) | [T] componente; [X] no jogo |
| Pôr comida num lugar causa percepção, decisão, deslocamento, consumo e corpo no jogo? | **não.** Alimentar é um botão sem posição (`src/telas/pet/TelaPet.tsx:393` → `motor.ts:679-690` → `motor_corpo.ts:185-203`); o log do jogo não tem evento de comida com lugar (`motor.ts:1233-1249`). O laço inteiro existe só no POC 3D, com um cérebro de teste por regras (`web/app/poc/mundo3d/cerebro.ts:1-5`), e o POC não deixa pôr comida (`pagina.ts:123-158`) | [X] no jogo; [T] no POC |
| A cena 3D do Pet reflete o motor? | **não: é decoração.** Pet parado no meio, sem bola nem comida, "Nada aqui decide o jogo" (`src/telas/pet/cena3d.ts:1-10, 25`). Um e2e confere só que o canvas desenha e que, sem WebGL, aparece a reserva (`e2e/jogo.spec.ts:1255-1284`) | [T] como decoração; [X] como reflexo |
| Há multiplayer, luta online ou ranking? | **não.** Vários pets locais, cruzar e importar `.digilab` existem; dois pets no mesmo mundo só na pesquisa (J7, inconclusivo por premissa) | [X] online; [T] local |
| A memória autobiográfica afeta decisões ou personalidade? | **não.** A história (`digilab/historia.py`) só alimenta a fala. Só o N6 decide (a fruta), e ele não existe no jogo. Nenhuma memória escreve na personalidade. Não há memória nuclear | [X] |
| Algum gene afeta o cérebro, a plasticidade ou a bioquímica? | **não no cérebro A nem no corpo.** Só o paladar (`h_q`, o sinal do canal `gosto`, atrás de chave) e o temperamento, que só modula o bandit da v1. O genoma único (G0) não existe | [X] |
| O decodificador de conceitos existe? | não: só documento (`docs/futuro/decodificador_conceitos.md:3-4`) | [P] |

## 2. O cérebro A e o que existe de cérebro no código

| peça | o que é | marca | evidência |
|---|---|---|---|
| percepção (lobo) | x = viés, as 8 entradas do `Estado.vetor` e o tempo sem cuidado; mais `bola`, `fruta`, os receptores novos e as entradas sociais quando as chaves estão ligadas | [T] | `lobos.py:120, 405-410, 2306-2329` |
| memória/emoção (lobo `MemoriaEmocao`) | contadores; **contribuição sempre 0** | [T], sem efeito | `lobos.py:516-547` |
| impulsos | o próprio instinto (7 regras) com uma rng-sonda; o prior `PRIOR_INSTINTO` | [T] | `lobos.py:277-342` |
| decisão | prior + aprendido + planejamento + piso; sorteio proporcional | [T] | `lobos.py:962-1026, 2318-2407` |
| aprendizagem L1 | gradiente de log p(a*) com o sinal no lugar da vantagem (a forma do COACH), corte em w0 ± teto | [T]; [R] os gates G3 a G6 falham | `lobos.py:459-485`; `docs/RESULTADO_V2_L1.md` |
| canais do sinal | soma por canal = o escalar (K-6); `_sensibilidade_canal` devolve sempre S | [T]; sem efeito visível na ablação | `lobos.py:1432-1470`; `docs/RESULTADO_V2_VALIDACAO_UNICA.md` §2 |
| alvo aprendido | classes de alvo e por árvore | [T]; [R] **atrapalha** (#296) | `lobos.py:2011-2120`; `docs/RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md` |
| planejador (J5) | `ModeloMundo`: desfecho, custo de andar, mapa; termo `g_plano` | [T]; [R] o G-T1 passa (#370), o G-T1-CONG não | `digilab/modelo_mundo.py`; `docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md` |
| competição entre regras (V3-3/4) | disputa das regras urgentes, `ConfigCompeticao` | [T]; [R] a validação passa em todos os gates (#396, mergeada em 2026-10-24) | `lobos.py:345-399, 2411-2467`; `docs/RESULTADO_V2_VALIDACAO_COMPETICAO.md` |
| memória de episódios N6 | episódios de consumo de fruta, recuperação pela fruta presente | [T]; [R] G-CAUSAL +0,028 [+0,009; +0,048], efeito pequeno; desligada por padrão; fora do jogo | `lobos.py:582-625`; `docs/RESULTADO_V2_VALIDACAO_UNICA.md` |
| cérebro B | célula recorrente de tempo contínuo (CfC) com ator-crítico, em ponto flutuante | [T]; [R] **não aprende** (0,0077 das decisões) | `digilab/policies/cerebro_b.py`; `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md` |
| cérebro C | circuitos binários esparsos com plasticidade de três fatores | [T]; [R] empate com o A (#197) | `digilab/policies/cerebro_c.py`; `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md` |
| controle `camada_unica` | capacidade igual sem lobos | [T]; [R] mais legível que os lobos na L1, mas acerta menos | `digilab/policies/camada_unica.py`; `docs/RESULTADO_V2_L1.md` |
| Digicorpo (rede de si, J6) | automodelo que prevê os receptores; só observa | [T]; [R] margem negativa na calibração | `digilab/rede_de_si.py`; `docs/RESULTADO_V2_CALIBRACAO_REDE_DE_SI.md` |
| o E0 do V3 | 55,3% das decisões têm um candidato só; o aprendido decide 15,6% de todas | [R] | `docs/futuro/digibrain_v3_e0.md` §1 |

**No jogo:** o A v11 decide os pets novos, com o corpo químico e os gestos. **Uma lacuna achada no código, sem execução:** nos v11, o
`m.motivo` não é atualizado pelas decisões do cérebro (`motor.ts:980-997`, contra `:938` nos v1 a v10), então o balão e a causa da Tela
Pet ficam sem o motivo da vida. Precisa de conferência no navegador antes de virar defeito.

## 3. O produto web

| capacidade | marca | evidência |
|---|---|---|
| o cérebro A v11 decide, com o corpo químico (digestão, Vida, drives novos, gestos, metabolismo) | [T] código; [S] ciência | `constantes.ts:468-472`; `test/lobos_v11.test.ts`, `laco_v11.test.ts`, `pet_v11.test.ts` |
| o mundo físico, a percepção, o andar e o comer no jogo | [X] | `mundo.ts` só em `test/` |
| o laço inteiro comida → corpo | [X] no jogo; [T] no POC com o cérebro de teste | `poc/mundo3d/simulacao.ts`; `test/poc_mundo3d.test.ts` |
| arrastar a comida | [P] | `docs/futuro/mundo_fisico.md:66, 210`; o #399 (aberto) |
| alimentar por botão | [T] | `TelaPet.tsx:393`; `pet_v11.test.ts` |
| a cena 3D e a reserva CSS/SVG | [T] como decoração | `cena3d.ts`; `CenarioPet.tsx`; `e2e/jogo.spec.ts:1255-1284` |
| o treino (aba Crescer › Treinar) | [T]; o treino não toca o cérebro nem o corpo | `motor/treino.ts:1-2`; `TelaTreinar.tsx`; `docs/TAREFA_V2_TREINO.md` |
| crescimento, evolução, caráter v11 | [T] | `test/evolucao_canonica.test.ts`, `carater_v11.test.ts` |
| luta local, arenas, Liga, campanha e jornada | [T]; o equilíbrio tem resultado (v1) | `test/paridade_v21d.test.ts`, `arenas.test.ts`, `jornada.test.ts` |
| vários pets, cruzar, importar | [T] | `src/pets.ts`; `test/heranca.test.ts`, `importar.test.ts` |
| dois pets no mesmo mundo | [X] no jogo; [S]/[R] na pesquisa (J7 inconclusivo) | `digilab/grupo.py` |
| multiplayer, luta online, ranking | [X] | nenhum código |
| a fala por LLM (moldura, fala livre, comando pelo chat) | [T] + [R] (a fala livre aprovada só com o `gemma2:9b`) | `servidor/`; `src/fala.ts`, `falaLivre.ts`; `artifacts_fala*` |
| o save e o replay | [T] event sourcing, falha alto em evento desconhecido | `test/save.test.ts`; `motor.ts:1228-1256` |
| a paridade com o Python | [T] por componente; o `Motor` v11 inteiro (treino, evolução) **não tem gabarito Python de vida inteira** | `test/gabaritos/*_python.json`; `laco_v11.test.ts:1-16` |

## 4. A memória

| tipo | o que guarda | recuperação | decide? | muda a personalidade? | marca |
|---|---|---|---|---|---|
| `MemoriaCurta` (v1, B1) | latências e broncas/elogios decaídos | todas as features, sempre | sim, no bandit, só no protocolo `arena-v1-memoria`; sem evidência de efeito | não | [T]; [R] |
| `MemoriaEspacos` (v1; web v2 a v10) | categoria, intensidade, criada, relembrada, ref do dono; **sem corpo, contexto nem consequência** | soma por categoria; relembrar a cada 4 h, por cronograma, **não por contexto** | sim, no bandit (6,9% dos motivos citam memória, `artifacts_v1_memoria_espacos/espacos.json`); **no v11 não decide** | não (o temperamento a modula; o contrário não) | [T]; [R] efeito pequeno, central INCONCLUSIVO |
| `MemoriaEpisodios` (N6) | tick, fruta, valência = Δhumor | **contextual**: a fruta presente é a pista; controles de recência e embaralhado | sim, só em qual fruta comer; desligada por padrão; fora do jogo | não | [T]; [R] G-CAUSAL +0,028 |
| `MemoriaEmocao` | contadores | — | não | não | [T] |
| `historia.py` (H/O/P/L) | fatos por molde do registro | rodízio, para não repetir | **não: só a fala** (`docs/ARQUITETURA_V2_VALIDACAO.md:36`) | não | [T] |
| emoção | emoção por evento × temperamento | a última, para a fala | não (a modulação está desligada) | não | [T] |

- **Consolidação:** só a promoção do curto (12 h) para o longo por intensidade (`memoria_espacos.py:153-159`; N6 em `lobos.py:598-604`).
  **Não existe memória nuclear ou central** (`docs/futuro/dwarf_fortress.md:97-98`).
- **Episódio registrado, codificado, recuperado e causal:** na v1, registrado e codificado sem corpo; recuperado por cronograma; causal no
  bandit. No N6, os quatro, mas só para a fruta.
- **Sinais do corpo no episódio:** o N6 guarda só a variação do humor. A v1, nenhum.
- **O adendo DF põe fora de escopo** "Memórias mudando o temperamento ao longo da vida (reabre o confundidor cuidado × treino; exige
  desenho próprio)" (`docs/ADENDO_MEMORIA_EMOCAO_DF.md:149-153`, texto de 2026-09-25; adiado para a V2 em 2026-10-01). A seção 5 da
  `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` confronta isso com a direção nova.
- **Fidelidade da fala,** três lacunas no código:
  - o prompt `livre-v6` deixa inventar lembranças e causas; o verificador só marca, não troca (`digilab_fala_livre/prompt.py:22-25`;
    `verificador.py:12`);
  - o verificador aceita uma causa apoiada num fato de memória ou de história (`verificador.py:82-93`), e os fatos M da web são só
    categoria e tempo (`src/falaLivre.ts:83-84`). No v11 a memória nunca decide, então "fiz X porque lembro Y" passa sem ser verdade.
    **Não há checagem entre episódio lembrado e decisão;**
  - quando o N6 muda a fruta, o motivo diz "porque aprendi a escolher essa", e a sonda da memória não é consultada (`digilab/motivo.py:217-229`).
- **Um teste vazio:** `tests/test_memoria_espacos.py:118` termina em `assert vistos >= 0`.

## 5. Os órgãos e a fisiologia

O inventário com os sete campos por sistema está na seção 7 de `docs/DEFINICOES_CORPO_V2.md` (atualizada neste PR). O resumo:

| estado | sistemas |
|---|---|
| implementado e ligado ao comportamento, **no jogo (v11) e na pesquisa** | o Sistema neuroquímico (fome, desconforto, cansaço, tristeza, dano); a homeostase (`sinal_corpo`); o Tato cutâneo (carinho e tapa); a dor; o susto; o sono e o cansaço; o tédio, a solidão e o estresse; a saúde (como entrada); o Metabolismo energético e a digestão (de forma indireta) |
| implementado e ligado **só na pesquisa** | a visão (ambiental e social); o Olfato alimentar pela leitura pronta; o paladar; o Tato social; a curiosidade (exige o mundo); o Sistema excretor (sem run) |
| implementado, **não integrado** ao cérebro nem ao produto | o órgão do Olfato (as narinas, DP-13); a Audição (leitura e órgão, DP-14); o olfato social; a Vida (o relógio só é conferido); o Digicorpo (só observa) |
| proposto ou futuro | os hormônios H1 a H3; o proprioceptivo; a termorregulação; o imune e toxicológico; o reparo, a força vital e a morte por órgão (J10) |

**A validação do corpo não rodou** (34101…34505; `docs/PAINEL_V2.md`).

## 6. A genética

- **No código:** o temperamento (4 eixos) e a espécie, herdáveis (`digilab/heranca.py`; web `motor.ts:305-342`); o `GenomaFrutas` e o
  `GenomaPaladar`, não herdáveis.
- **Nenhum gene** muda o prior do A, os pesos, o passo do aprendizado do A ou as taxas do corpo. O ponto de entrada da H-R4
  (`_sensibilidade_canal`) existe, não é usado e devolve S (`lobos.py:1432-1438`).
- **O paladar** muda o sinal de reforço (o canal `gosto`), não o prior nem o passo.
- **O genoma único da V2 (G0) não existe;** o desenho está em `docs/futuro/ecossistema_genetico.md`.
- **O E1 da v1 falhou:** o genoma explicou 4,9% da variância (`docs/historico/claude/v1_pesquisa.md:114`).
- **O desenho** propõe genes do prior e da plasticidade, mas escreve "o prior do cérebro A". A seção 9 da
  `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` generaliza isso para os parâmetros inatos de qualquer módulo.

## 7. Sprites, Bandai e assets

**Não há proibição genérica nos arquivos de instrução.** A seção "Assets da Bandai" saiu do `CLAUDE.md` e do `web/app/CLAUDE.md` em
2026-10-13 (`docs/registro/2026-10.md`, na rodada de saúde). Hoje nenhum dos dois cita Bandai, sprite, atlas nem túnel.

**A decisão do Matheus,** relatada pelo Gerente (não está no repositório):
- em 2026-10-22, no chat da sessão do Gerente: "rETIRE ESSA REGRA SOBRE OS SPRITES DA BANDAI E PUBLIQUE UMA VERSAO, UTILIZE O CLOUDEFLARE
  QUE JA TEMOS";
- em 2026-10-24, no mesmo chat: "Porem EU AUTORIZO A POSTAR OS SPRITES, SEM PROBLEMAS".

**O que ainda diz "uso pessoal", "não publicar" ou "repositório privado":**

| onde | o que diz | o que este PR faz |
|---|---|---|
| `servidor/servidor_local.py:36` (docstring) | "nao compartilhar (CLAUDE.md)" | corrige (só a docstring) |
| `servidor/CLAUDE.md:18` | "O link é de uso pessoal" | **pede o ok do Matheus**, porque é um arquivo de instruções |
| `docs/UI_GUIDELINES.md:148-149` | "uso pessoal e local" | corrige para a regra de procedência |
| `docs/TAREFA_INTERFACE_UP.md:27-29`, `docs/TAREFA_FRONT_TS.md:43-45`, `docs/ASSETS_UP.md:3-4` | "uso pessoal" | corrige |
| `docs/PLANO_V2_PESQUISA.md:135-136` | "não podem sair do uso pessoal" | corrige |
| `docs/historico/claude/jogo_web.md:193-214` e `:4` | a regra antiga (repositório privado, não publicar) e "a regra continua no `CLAUDE.md`" (falso) | nota de superação no topo; o histórico não é reescrito |
| `docs/referencias/CONTEXTO_DIGILAB_2026-09-29.md:14-15, 162` | "Tem que continuar privado" | nota de superação |
| `web/app/src/telas/config/TelaConfig.tsx:184-185` (texto na tela), `web/digilab_sprites.html:1034, 2925-2927`, os comentários de `web/app/src/atlas.ts:1` e `decoracao.ts:1-2`, `web/app/package.json:5` ("repositório privado") | "Não publicar nem distribuir", "Uso pessoal; repositorio privado" | **não muda aqui** (é código ou texto de tela); vai para a tarefa do MVP |

**A regra de procedência** está na seção 5.1 de `docs/UI_GUIDELINES.md`, e é a que vale daqui em diante.

**O que continua:**
- o atlas fora do git (ele mora em `D:\Trab\digilab\Assets`, fora da árvore);
- o e2e e as capturas com o sprite de reserva;
- os avisos de procedência e crédito.

**Achado à parte:** o repositório é público (`.github/workflows/verificar-pr.yml:2`), e três textos dizem que ele tem de ser privado.
Eles são corrigidos ou recebem a nota de superação. **Nenhum asset foi adicionado,** e este trabalho não publicou nada.

## 8. Os PRs abertos e o efeito de cada um

| PR | o que é | efeito concreto | recomendação |
|---|---|---|---|
| **#395** | P4, etapa 4: o adendo 1, parte A, do plano da replicação do T1 com o contrato; nenhuma vida | fixa as regras do piloto (a orientação como PC-8). Nada roda sem o sim | **muda:** o contrato no motor (as etapas 1 a 3, já na `main`) serve ao MVP. O piloto e a validação do G-T1 corporificado só testam o A, e ficam **pausados** até o Matheus dizer se servem de baseline (seção 9). O documento pode entrar como registro, sem autorizar run |
| **#399** | `docs/futuro/comida_arrastar.md`, a ideia da comida de arrastar | o texto amarra o mundo no jogo à P4 ("o jogo não muda até lá"), o desvio que o prompt corrige; **não foi mergeado** por revisão do Matheus (relato do Gerente, 2026-10-24) | **absorver e fechar:** o conteúdo (o `deixar_comida` com replay, o `DonoComLugar`, o gesto e o caminho acessível, as perguntas CA-1 a CA-3) entra na `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`, com dependências próprias e sem a P4 |
| #396 | a validação da competição V3-3/4 | **mergeado** em 2026-10-24: todos os gates passam | resultado sobre o A, que fica |
| #398 | o ovo não chocava com a cena 3D | **mergeado** em 2026-10-24 | correção do jogo, que fica |

## 9. As rodadas do A: mantidas, pausadas ou úteis como baseline

| rodada | o que pergunta | estado | o que fazer |
|---|---|---|---|
| P4, piloto e validação (G-T1 com o contrato) | se o planejador do A ainda revaloriza com o cone e o controlador | etapas 0 a 3 na `main`; #395 aberto; nada rodou | **pausar** o piloto e a validação; manter o contrato (as etapas 1 a 3) para o MVP |
| Gate I (o pet integrado ao redor do A) | se o mesmo pet junta corpo, mundo, aprendizado e replay | tarefa e plano decididos (GI-1 a GI-5, GT-1 a GT-8); nenhum código | **repensar:** os critérios (I-CORPO, I-MUNDO, I-APRENDE, I-REPLAY) servem ao cérebro modular. A run com o A só vale como baseline do protótipo modular. A GI-1 ("ao redor do A") fica SUPERADA |
| V3-3/4, a competição | se a disputa entre regras ajuda | validada (#396) | **encerrada**; o resultado fica como evidência sobre o A e como mecanismo candidato à arbitragem modular |
| V3-9, o crédito por canal | — | parada (#376) | continua parada |
| J5, o T2 (a busca, o mapa) | se o mapa do planejador funciona | sem tarefa | **não abrir** só para o A |
| J7, dois pets | — | inconclusivo por premissa | fica para depois do MVP (fases posteriores) |
| o porte do A para a web (W) | — | o v11 no jogo | **manter** como o cérebro atual do jogo até o modular entrar (a fallback condicionada, seção 6 da arquitetura) |
| connectome do A | — | ferramenta | manter como ferramenta |

## 10. Conflitos entre documentos

**Nenhum documento registrava a decisão de 2026-10-24.** Os conflitos, agrupados. O detalhe linha a linha está no registro deste PR
(`docs/registro/2026-10.md`, a seção "PROMPT-MESTRE").

| grupo | onde | o conflito | o que este PR faz |
|---|---|---|---|
| **"a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15)** | `CLAUDE.md:9-11, 50, 85`; `PLANO_V2_PESQUISA.md:11-12, 80-82, 108, 114, 137, 159-160, 166-167`; `ROADMAP_V2.md:7, 19-20, 59, 81, 118, 124, 152-153`; `ARQUITETURA_V2_VALIDACAO.md:81-84, 201`; `PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md` e `RESULTADO_V2_COMPARACAO_CEREBROS.md` (o propósito: escolher o cérebro da web); `docs/research/digibrain/README.md:65-67` e outros | superados pela direção modular | **registradas como SUPERADAS com data, sem apagar:** uma nota no topo dos documentos de plano, roadmap e comparação; o `CLAUDE.md` só com o ok do Matheus (seção 11) |
| **"a pesquisa primeiro; o produto depois"** | `PLANO_V2_PESQUISA.md:1-5, 152-154` | o inverso da direção | nota de status: o produto jogável vem primeiro |
| **o Gate I "ao redor do A" (GI-1)** | `docs/futuro/gate_integracao_pet.md:114-116, 141`; `TAREFA_V2_GATE_I.md:17, 95` | o cérebro alvo mudou | nota: os critérios do gate valem para o modular; a run com o A só como baseline; a GI-1 SUPERADA |
| **a P4 como validação do A, e o mundo no jogo esperando a P4** | `TAREFA_V2_P4_CEREBRO_MUNDO.md:145`; `PLANO_ANALISE_V2_P4_CORPORIFICADO.md:46, 180`; `docs/futuro/mundo_3d.md:5, 42, 254, 298` (W-5); o texto do #399 | o produto ficava esperando a pesquisa | nota: o contrato serve ao MVP; o piloto e a validação pausados (DM-8); o mundo vai ao jogo pela `TAREFA_V2_MVP_MUNDO_PRODUTO.md`, sem a P4 |
| **o genoma preso ao prior do A** | `docs/futuro/ecossistema_genetico.md:55, 59-62` | limita os genes do cérebro ao A | nota: os parâmetros inatos de cada módulo (`ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 9) |
| **a memória que muda o temperamento fora de escopo** | `ADENDO_MEMORIA_EMOCAO_DF.md:149-153` | a direção planeja a influência gradual | nota: a influência vai nas facetas adquiridas, não no temperamento (DM-6) |
| **o `AcaoPet` não pode ganhar membros** | `PLANO_V2_PESQUISA.md:77`; `ROADMAP_V2.md:37`; `V2_INVENTARIO_JOGO.md:179-182, 210` | desatualizado: o `ALIVIAR` entrou no fim do enum (`events.py:211-222`) | nota no plano e no roadmap |
| **o estado do porte W desatualizado** | `TAREFA_V2_W_PORTE_CEREBRO_A.md:4` ("Nenhum código foi escrito"); `PAINEL_V2.md:23`; `ROADMAP_V2.md:82` ("a 3 em curso") | as etapas 1 a 5 e o mapa já foram entregues | o status da tarefa e a linha do painel |
| **o V3 só sobre o A** | `docs/futuro/digibrain_v3_e0.md:338` (V3-2) | contra o modular | nota: as peças do V3 viram candidatas a módulo |
| **"uma versão de pet por mecânica"; "só o chat B mexe em `lobos.py`"; "uma alavanca por vez"** | `web/app/CLAUDE.md:11`; `ROADMAP_V2.md:99`; `V2_TRABALHO_PARALELO.md:42-43` | o custo de trocar módulos; frentes paralelas | as rotas da seção 6 da arquitetura (DM-4, DM-5) |
| **os textos de sprites** | seção 7 desta auditoria | a regra antiga | seção 7 |
| **documentos datados** | `docs/futuro/connectome_cerebro_a.md:4-5, 204` (o porte "pausado"); `TAREFA_V2_PET_QUE_PENSA.md:23, 118` (o v11 "pausado"); `TAREFA_V2_DOIS_PETS.md:46`; `DEFINICOES_CORPO_V2.md`, seções 7 e 8.1 (atrás do código); `TAREFA_V2_CORPO_DRIVES.md:464`; `MAPA_REPOSITORIO.md` (faltam `cerebro_b.py`, `cerebro_c.py`, `lobos.ts`, `contrato.py`) | desatualizados | o `DEFINICOES_CORPO_V2.md` (seção 7) é corrigido aqui; os outros ficam no índice como "datados", para a rodada de saúde |

**Uma evidência que pesa no desenho:** a L1 mostrou que "a modularidade não compra legibilidade" pela medida dela (`docs/RESULTADO_V2_L1.md:49`).

## 11. O que este PR não fez, e por quê

- **Não mudou código** (motor, cérebro, telas, testes) nem assets. A única linha fora de `docs/` é a docstring de
  `servidor/servidor_local.py`.
- **Os arquivos de instrução** (`CLAUDE.md`, `AGENTS.md`, `web/app/CLAUDE.md`, `servidor/CLAUDE.md`) só mudam com o ok do Matheus
  (`CLAUDE.md`, "Este arquivo só muda com o ok do Matheus"). O texto proposto e a resposta estão no corpo do PR.
- **Nada rodou:** nenhum piloto, validação ou calibração. As conferências feitas estão no corpo do PR.
