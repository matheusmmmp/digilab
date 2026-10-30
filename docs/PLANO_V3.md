# PLANO DA V3: cérebro pelas referências, layout novo e batalha em tempo real (2026-10-30)

**PROPOSTO** pelo Gerente da transição V2 → V3 (`docs/TAREFA_V2_TRANSICAO_V3.md`), sobre a `main` em `b3643bb`. A definição da V3 em três
trilhas é do Matheus (2026-10-30). As missões, a ordem e as decisões V3-D1 a V3-D8 (seção 7) esperam o Matheus. O estado em que a V2
fecha está em `docs/FECHAMENTO_V2.md`.

**A direção de 2026-10-24 continua:** o produto jogável vem primeiro; o DigiBrain é modular; o cérebro A é a linha de base, o controle e
o fallback condicionado.

## 1. As perguntas e o fim de cada trilha

| trilha | a pergunta, em uma frase | a trilha terminou quando |
|---|---|---|
| **C · cérebro** | Os mecanismos que a triagem de literatura de 2026-10-30 aponta (o cenário com regularidade, o crédito na intenção, redecidir por evento e a memória que decide) explicam ou corrigem as falhas do modular no longe e no hábito, quando cada um é testado com controle? | a C1 e a C2 rodaram uma vez cada, com o resultado registrado como saiu; a C3 e a C4 têm espec, código atrás de chave e plano (a run só se o Matheus mandar); a `docs/ESPEC_DIGIBRAIN_MODULAR.md` está revista com cada peça marcada [MECANISMO] (com fonte verificada), [HIPÓTESE] ou [EXISTE] |
| **L · layout** | O jogo web fica inteiro no layout habitat em tela cheia, com os menus nas duas peles, e recebe a primeira peça do modular com paridade? | a M7 e as T1 a T3 estão na `main`, com as capturas aprovadas pelo Matheus nas duas peles; a L3 está na `main` com a paridade Python × TS, ou o Matheus decidiu que nenhuma peça vale levar ainda |
| **B · batalha** | A batalha em tempo real fecha as metas de equilíbrio com o candidato v14, a ponto de a v14 poder ser ligada? | a conferência da segunda rodada rodou uma vez, e o Matheus decidiu ligar ou não a v14; a luta aparece na pele dos menus sem mudar o motor da luta |

## 2. Trilha C, o cérebro (a partir das recomendações R1 a R7)

A fonte das R1 a R7 é a análise da triagem de 2026-10-30 (`triagem_texto_completo/ANALISE_LACUNAS_E_ROADMAP.md`, fora do repositório; a
síntese entra pela C0). **Até a C0, nenhuma fonte nova da triagem é citada:** os nomes abaixo valem como pistas, SEM FONTE.

| missão | o que é | depende de | arquivos que toca | categoria |
|---|---|---|---|---|
| **C0 · literatura** | verificar no Crossref, pela skill `literatura-digilab`, as fontes da lista 2.1 e acrescentá-las a `docs/referencias/`; trazer a síntese da triagem (sem os PDFs); acrescentar à lista de alegações proibidas a da seção 2.2; rodar as strings de busca que faltaram (R6) | nada | só `docs/referencias/` e a skill | literatura |
| **C1 · longe regular (R1)** | a `docs/TAREFA_V2_LONGE_REGULAR.md` como está: as LR-1 a LR-7 com o Matheus; o gabarito dos três estilos num commit próprio; o estilo `longe_fixo`; o adendo 6 ao plano do protótipo; a run uma vez. Faixa proposta 71101…71505 (livre na `main` e no branch da rodada 2 do combate em 2026-10-30) | a C0 (a tarefa cita Ho e Giannakakis como pistas); as LR | `digilab/mundo.py`, `digilab/config.py`, `experiments/bancada/`, `experiments/run_v2_longe_regular.py`, `tests/` | implementacao, depois experimento |
| **C2 · o hábito com crédito na intenção (R2)** | a tarefa do hábito (o P2 ao contrário), com um braço em que a atualização acontece na intenção ou na opção composta, contra a atualização no passo; reabre a DX-6 como hipótese com fonte (Gadanho e Hallam, se verificado na C0) | a C1 (o cenário em que o hábito é lido) | `digilab/digibrain/`, `digilab/config.py`, `experiments/`, `tests/` | implementacao, depois experimento |
| **C3 · redecidir por evento (R3)** | espec no formato da L-2 (`docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md`), atrás de subchave desligada: a intenção só é refeita quando um receptor cruza um limiar ou surge um evento sensorial novo. As medidas aplicam a lição LP-2 (a retomada de uma busca não conta como troca) | a C1 | primeiro só `docs/`; depois `digilab/digibrain/`, `tests/` | arquitetura, depois implementacao |
| **C4 · a memória autobiográfica com as entradas da literatura (R4)** | as ME-1 a ME-7 da `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`, com três propostas novas para o Matheus: na ME-1, a significância do episódio é a variação do corpo; na ME-3, guardar o mais significativo de cada categoria; na validação, o braço "REL sem episódios negativos". Do PEPE: a recuperação roda a cada decisão (já cabe na M2) | a C0; as ME | primeiro só `docs/`; depois `digilab/digibrain/`, `tests/` | arquitetura, depois implementacao |
| **C5 · a viabilidade do corpo (R5)** | a fração do tempo com alguma variável do corpo fora da faixa e a menor necessidade, como medidas secundárias descritivas, do replay das vidas já gravadas, sem vida nova | nada (as medidas entram no adendo 6 da C1, que já as pede) | `digilab/metrics.py`, `experiments/`, `tests/` | implementacao |
| **fim da trilha · a espec revista** | `docs/ESPEC_DIGIBRAIN_MODULAR.md` com cada peça marcada [MECANISMO] (fonte verificada), [HIPÓTESE] ou [EXISTE] | C0 a C4 | só `docs/` | arquitetura |

### 2.1 As fontes que a C0 verifica

- **A verificar (nenhuma está em `docs/referencias/` hoje):** Gadanho e Hallam 2001; Ho, Dautenhahn e Nehaniv (CEC 2005, AISB 2006,
  Connection Science 2008, a tese de 2005); Khan e Cañamero 2018; Yoshida et al. 2024; Strannegård et al. 2017/2018; Giannakakis et al.
  2023/2025; Goertzel et al. 2008; Francis, Mehta e Ram (PEPE; S0519 e S0547 são o mesmo estudo); Blumberg et al. 2002; Yoon et al. 2000;
  Curtis et al. 2022; Maroto-Gómez et al. 2025.
- **Já no projeto (conferido em 2026-10-30):** Creatures (Grand e Cliff, em `docs/referencias/referencias_verificadas.csv`); Keramati e
  Gutkin (em `referencias_verificadas.csv` e `dm_referencias_verificadas.csv`); Cañamero 1997 (em `dm_referencias.bib`); Maroto-Gómez et
  al. 2023 (`10.1002/aisy.202200288`, em `docs/referencias/G_REVISAO_CORPO_QUIMICO.md`, lido pelo resumo).
- **As ressalvas da própria triagem, que a C0 carrega:** quatro fontes foram lidas em versão-irmã (Gadanho pela tese de 1999, Ho 2008
  pela tese de 2005, Zamin pelo Zamin II, Nahodil pela dissertação); Ho et al. não fazem teste de hipótese e usam 10 a 50 execuções por
  condição. Servem como direção, não como tamanho de efeito.

### 2.2 A alegação proibida nova (a C0 a escreve na lista)

**Nunca afirmar que juntar corpo com homeostase, aprendizado em vida e memória episódica num agente é novo.** A triagem achou essa
combinação em Creatures, Gadanho e Hallam, Ho et al., Goertzel et al., Zamin e Rity. O que se pode dizer, sem alegar novidade, é o que o
projeto faz: teste causal com braço de controle, num pet persistente, com replay determinístico.

### 2.3 O backlog da trilha C (R7, sem pressa)

- **J7:** prever no plano a perspectiva dos episódios trocados entre pets (o problema do deslocamento, em Ho).
- **Hormônios:** o desenho de Khan e Cañamero, com três níveis de dificuldade, quando os hormônios entrarem (o J10).
- **Produto:** um estudo pequeno de legibilidade com jogador, depois do modular no jogo (Anderson et al. já verificado; o questionário de
  Curtis, a verificar). Não reabre a pergunta do dono.

## 3. Trilha L, o layout

| missão | o que é | depende de | arquivos que toca | categoria |
|---|---|---|---|---|
| **L1 · a M7 do layout habitat** | **em voo** (worktree `v2-layout-fecho`, mudanças não commitadas em 2026-10-30). O que falta: e2e com os seletores novos; as capturas regeneradas depois da aprovação do Matheus; 360/390/1280, claro e escuro; a lista da seção 6 da `docs/TAREFA_V2_LAYOUT_HABITAT.md` (D8, o dock flutuante, o CSS morto) | nada; segue na sessão dela | `web/app/src/App.tsx`, `web/app/src/estilo/*.css`, `web/app/e2e/` | implementacao |
| **L2 · as T1 a T3 do tema dos menus** | a pele Vidro (Holográfico) como padrão; os nomes Militar e Holográfico; a escolha em Ajustes › Aparência; as capturas nas duas peles (`docs/TAREFA_V2_TEMA_MENUS.md`, seção 5) | o merge da L1 (TM6) | `web/app/src/` (`pele.ts`, `tokens.css`, Ajustes), `web/app/e2e/` | implementacao |
| **L3 · o primeiro módulo do modular no jogo** | uma peça do modular no jogo, com paridade Python × TS (`docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`). Proposta: o lugar lembrado do M-MEM. **Só depois** de a C1 e a C2 dizerem qual peça vale levar | a C1, a C2 e o sim do Matheus | `web/app/src/` (o cérebro e o laço), os testes de paridade, gabaritos do Python | implementacao |

## 4. Trilha B, a batalha em tempo real

| missão | o que é | depende de | arquivos que toca | categoria |
|---|---|---|---|---|
| **B1 · a segunda rodada de equilíbrio** | **em voo** (branch `v2-combate-tr-r2-formas`, quatro commits à frente da `main` em 2026-10-30: as DR2-1 a DR2-6 decididas, as faixas 72101…72505 e 74101…74505 e a fase R2-0). As fases seguem `docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md`, com o PR por fase | nada; segue na sessão dela | `web/app/scripts/equilibrio_tr/`, `web/app/scripts/medicoes/`, `experiments/bancada/faixas.py`, `docs/EQUILIBRIO_COMBATE_TR.md` | experimento |
| **B2 · ligar a v14** | trocar os fatores, o relógio e as listas do jogo pelos da v14 | a conferência da B1 e o sim do Matheus | o motor da luta em `web/app/src/` | implementacao |
| **B3 · a luta dentro do layout novo** | o HUD e o palco da luta na pele dos menus; conferência com a trilha L, sem mexer no motor da luta | a L1 e a L2 | `web/app/src/` (as telas da luta), `web/app/src/estilo/` | implementacao |

## 5. As dependências e os arquivos compartilhados

- **A ordem proposta (V3-D6):** C0 agora; a L1 e a B1 seguem em voo; depois a C1 (e a C5 junto do adendo 6); depois a C2, a L2 e a C3; a
  C4 depois da C0 e das ME; a B2 depois da conferência da B1; a B3 depois da L2; a L3 por último.
- **Uma missão por vez, na mesma worktree, em cada um destes arquivos:** `web/app/src/App.tsx`, `web/app/src/estilo/tokens.css`,
  `web/app/src/estilo/pet.css`, `web/app/src/componentes/Nav.tsx`, `digilab/mundo.py` e `digilab/digibrain/`. Hoje: a L1 tem `App.tsx` e os CSS; a
  B3 e a L2 esperam por ela; a C1 tem `digilab/mundo.py`; a C2, a C3 e a C4 se alternam em `digilab/digibrain/`.
- **As runs (V3-D8):** uma run de pesquisa por vez, com no máximo 4 processos. As medições da B1 contam nesse limite.

### 5.1 O backlog da V3 (o que o fechamento marcou ADIADA)

| item | por quê espera | de onde vem |
|---|---|---|
| J2 corpo químico (a calibração final e a validação) e o metabolismo | a calibração final espera a estrutura completa | `docs/FECHAMENTO_V2.md`, seção 1.2 |
| J4 banheiro | as saídas sem decisão até haver dado | idem |
| J5, a busca (T2) | espera um plano próprio | idem |
| J6 ego (a bancada da rede de si) e J6a | fora das três trilhas | idem |
| J7 dois pets, J8, J9 | inconclusivo por premissa; com a R7 | idem |
| J10 órgãos e hormônios | SEM FONTE primária; com a R7 | idem |
| a P4 e o Gate I | pausa pela DM-8 | idem, seção 1.1 |
| o ecossistema genético, a fisiologia por espécie (FE-3), as fases posteriores | fora das três trilhas | idem |
| a seção 6 da rodada de saúde (os hooks de 2026-10-14) | um registro de documento | `docs/TAREFA_V2_SAUDE.md` |

## 6. As regras que continuam

**Todas as do `CLAUDE.md` valem na V3, sem exceção.** As que mais pesam aqui:
- **determinismo:** mesma semente e mesmo log dão o mesmo resultado; se um teste de replay ou de paridade quebrar, parar e avisar;
- **plano antes da run;** a faixa de sementes na `FAIXAS_RESERVADAS` num commit próprio; **uma validação por pergunta,** rodada uma vez;
- **chave desligada sai byte a byte,** com o gabarito num commit próprio antes da mudança;
- **`digilab/engine.py` não muda;**
- **referência só verificada** (fora disso, SEM FONTE); **nunca alegar novidade;** números novos são PROPOSTOS;
- **toda mudança de jogo vai também para a web,** com paridade; os nomes Digimon na tela, nenhum id interno, nenhum caractere japonês,
  português do Brasil, só o que o motor registra; os sprites do Digimon UP autorizados, com o atlas fora do git; acessibilidade (44 px,
  4,5:1, foco visível, `prefers-reduced-motion`);
- **worktree própria por missão,** um PR por missão com o relato no corpo; **o merge é só do Matheus.**

### 6.1 Um achado do G0 que pede uma decisão (vai na V3-D1)

O CI do relato (`tools/verificar_relato.py`) só aceita, no campo `Tarefa`, um `docs/TAREFA_V2_*.md`, e na categoria experimento só
reconhece um `docs/PLANO_ANALISE_V2_*.md`. O modelo de tarefa (`docs/modelos/TAREFA_V2_MODELO.md`), o `tools/nova_tarefa.py` e o
`tools/gerar_estado_atual.py` também só olham o prefixo `V2`. **Uma tarefa `TAREFA_V3_*` reprova no CI** até essas expressões aceitarem
`V[23]`. Por isso este PR usa `docs/TAREFA_V2_TRANSICAO_V3.md`.

## 7. As decisões V3-D1 a V3-D8 (todas PROPOSTAS, com a recomendação primeiro)

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **V3-D1** | o nome e o prefixo | **V3, com o prefixo `V3` nos documentos novos** (`docs/PAINEL_V3.md`, `docs/TAREFA_V3_<FRENTE>.md`, `docs/PLANO_ANALISE_V3_<FRENTE>.md`, `docs/modelos/TAREFA_V3_MODELO.md`); os V3 antigos ficam, com o glossário da seção 8. **E um PR pequeno de infraestrutura** (antes da primeira tarefa V3) que faz o CI, o modelo, o `nova_tarefa.py` e o `gerar_estado_atual.py` aceitarem `V2` e `V3` (seção 6.1) | renomear o que existe: links e registro quebrados; sem glossário: "V3-9" lido como fase nova; sem o PR de infraestrutura: toda tarefa V3 reprova no CI ou volta a nascer `TAREFA_V2_*` |
| **V3-D2** | a pasta de trabalho | **um clone novo `D:\Trab\digilab\v3`,** como na passagem v1 → v2; as worktrees passam a `D:\Trab\digilab\v3-<frente>`; a pasta `v2` fica como referência congelada da `main` no dia da tag. **As duas frentes em voo (L1, B1) terminam nas worktrees `v2-*` delas** | continuar na `v2`: as 48 worktrees da V2 e as da V3 misturadas; clone novo sem `.venv` e `node_modules`: uma tarde de preparo |
| **V3-D3** | o marco do congelamento | **a tag `v2-final` na `main` depois do merge deste PR,** sem esperar as frentes em voo; o `PAINEL_V2.md` ganha a última atualização e o aviso "congelado" | esperar a M7, a T3 e a B1: a V3 não começa nunca |
| **V3-D4** | as frentes em voo | **herdadas pela V3, sem reabrir:** layout M7 → L1; tema T1–T3 → L2; combate rodada 2 → B1; LONGE-REGULAR → C1; memória autobiográfica → C4. Os documentos delas continuam `TAREFA_V2_*` | reabrir como tarefas novas: o histórico se espalha em dois lugares |
| **V3-D5** | os documentos da V2 | **ficam onde estão,** com um cabeçalho "V2, congelado em <data>" (num PR depois da tag; as tarefas herdadas não recebem o cabeçalho). Os novos nascem `*_V3_*`. Nada vai para `historico/` agora | mover: quebra o G-NADA-PERDIDO, os links e o registro por mês |
| **V3-D6** | a ordem das trilhas | **C0 agora; a L1 e a B1 seguem em voo** (já começaram, sem arquivos em comum com a C0); depois a C1 (com a C5) e a B2 quando a B1 conferir; depois a C2, a L2 e a C3; a C4 depois da C0 e das ME; a L3 por último | C1 antes da C0: a tarefa cita fontes não verificadas; L3 antes da C2: leva ao jogo uma peça sem evidência |
| **V3-D7** | o `CLAUDE.md` | **um PR próprio, depois da tag,** trocando "Onde a V2 está" por "Onde a V3 está" (o `PAINEL_V3.md`) e acrescentando o glossário e o prefixo `V3`. Muda só com o ok do Matheus | editar junto do G0: mistura proposta com regra |
| **V3-D8** | a máquina | **no máximo 4 processos por run** até o teste da BIOS FP; **uma run de pesquisa por vez** (as medições da B1 contam) | 20 processos: o access violation de 2026-10-28 |

## 8. O glossário V2 × V3

**"V3" já tem vários sentidos no repositório. Nenhum é renomeado.** Desde este plano, "a V3" sem mais nada quer dizer a fase nova.

| o que se lê | o que é | de quando |
|---|---|---|
| **a V3** (`docs/PLANO_V3.md`, `docs/PAINEL_V3.md`, `docs/TAREFA_V3_*`) | a fase nova: cérebro pelas referências, layout novo e batalha em tempo real | 2026-10-30 |
| `docs/PLANO_ANALISE_V3.md`, `artifacts_educacao_v3b/`, `artifacts_educacao_v3c/` | a análise exploratória da v1 (educação, lesões e evolução por vitórias) | v1, 2026-09-28 |
| `docs/TAREFA_V2_V3.md`, `docs/futuro/digibrain_v3_e0.md`, `docs/futuro/v3_espaco_acoes.md`, `artifacts_v2_v3/` | o "DigiBrain V3" da V2: a auditoria E0 do cérebro A e o desenho do espaço de ações (#332), superados pela direção modular | V2, 2026-10-19 |
| V3-9, `docs/TAREFA_V2_V3_CREDITO_CANAL.md` | o crédito do "querer" por canal, parado na G0-PODE-MUDAR | V2, 2026-10-19 a 2026-10-21 |
| V3-3/4, `docs/TAREFA_V2_V3_COMPETICAO.md`, `docs/PLANO_ANALISE_V2_V3_COMPETICAO.md` | a competição entre as regras urgentes, validada (#396) | V2, 2026-10-21 a 2026-10-22 |
| `docs/referencias/V3_SINTESE_FRUTAS_VICIO_V1_V6.md`, `v3_referencias.*`, `v3_verificacao_crossref.json` | a terceira busca de literatura (frutas, gosto e vício), de 2026-10-01 | V2, 2026-10-01 |
| `artifacts_combate_v21c/calibracao/v3/` | a terceira rodada de calibração do combate V2.1 | v1 |
| `artifacts_fala/*fala-v3*` | a terceira versão do prompt da fala por LLM | v1 |
| a v13, a v14 | versões do pet e do candidato de combate, não fases | V2 |

**Para quem lê um documento antigo:** "V3-9", "V3-3/4" e "digibrain_v3" são da V2; "Plano de análise V3" é da v1.
