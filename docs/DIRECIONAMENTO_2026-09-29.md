# Direcionamento — o que aprendemos, o que está aberto e para onde ir

Status: **análise para decisão** (pedido do Matheus, 2026-09-29). Nada aqui muda código. Os números vêm dos artefatos citados no `CLAUDE.md`; se for usar um, confira no artefato.

## 1. O que a pesquisa nos ensinou (consolidado)

Sete resultados, todos EXECUTADOS com artefato em disco. Eles mudam o rumo:

| # | achado | artefato | consequência |
|---|---|---|---|
| 1 | **A hipótese central foi refutada.** Treino por dono coerente não produz pet melhor que o feedback aleatório com o mesmo volume de interação: −0,034 [−0,072; +0,006] na condição neutra, 160 ovos. | `artifacts_confirmatoria/` | O projeto não sustenta mais "ensinado pelo dono" como resultado. A revisão bibliográfica de 2026-09-29 também derruba isso como novidade (Black & White, 2001). |
| 2 | **O que separa donos é o cuidado, não o ensino.** Com educação, lesões e morte, atencioso − aleatório vira +0,121, e cerca de metade vem das mortes do aleatório. Entre 24 personas, só o limiar de cuidado tem efeito. | `artifacts_educacao/`, `_v3c/` | A pergunta de pesquisa viva é sobre **cuidado**, não sobre feedback. |
| 3 | **O aprendizado mexe pouco no comportamento** (JSD ≈ 0,02 bit, no limiar) e só 13–18% das decisões têm fator explicável. | `artifacts/`, `artifacts_expressao/` | Personalidade sutil demais fica invisível ao jogador. Tudo que for de jogo precisa ser **legível**. |
| 4 | **Os ovos dominam a variância** (ICC 0,74), mas **o genoma pesa 4,9%** quando se separa a semente do genoma da do ambiente; a espécie explica 32% da diferença entre genomas. | `artifacts_poder/`, `artifacts_linhagem/` | A "sorte do ovo" era sorte do **ambiente**. A linhagem como pesquisa foi encerrada (decisão de 2026-09-29). |
| 5 | **Dono × ambiente explica 22%** da variância no E1: o efeito do dono depende do ambiente (as mortes do aleatório dependem de onde ele cai). | `artifacts_linhagem/natureza_criacao/` | É a pergunta aberta mais promissora. |
| 6 | **Batalha que treina vira espiral.** "Luta treina" levou 577 de 640 pets à forma sombria. | `artifacts_educacao_v3b/` | Qualquer efeito da luta sobre o pet precisa de freio próprio, fora da via do treino. |
| 7 | **O vínculo mede frequência, não coerência.** O aleatório termina com vínculo maior que o atencioso. | `artifacts_v1_personalidade/` | O vínculo não serve como medida de coerência até ser redesenhado. |

**A revisão bibliográfica de 2026-09-29** (79 referências, fora do repo em `D:\Trab\digilab\docs\revisao_alife_2026-09-29\`) acrescenta duas coisas: a lacuna real que o projeto pode ocupar é **separar o efeito da criação pelo usuário do efeito da seleção pelo usuário** (ninguém publicou), e três afirmações de novidade estão bloqueadas (instinto × aprendido, herdar o prior, "ensinado pelo dono").

**O que isso quer dizer em uma frase:** o Digilab virou dois projetos que dividem um motor. Um é **pesquisa**, cuja pergunta original morreu e precisa ser reescrita em torno do cuidado e do ambiente. O outro é **jogo**, que já tem mais mecânica do que consegue mostrar.

## 2. O que está em andamento agora (2026-09-29, fim do dia)

| frente | branch / pasta | estado | risco |
|---|---|---|---|
| **Evolução canônica** (Champion → Ultimate → Mega, pets v5, Montanha Espiral) | `design-evolucao-canonica`, `v1-evolucao` | **implementada no jogo**, 5 commits, sem PR | Mexe em `motor.ts`, `VERSAO_PET = 5`, `mapa_constantes.json`, `CLAUDE.md`. |
| **Voz própria** (história, mentira, almanaque, corpus) | `design-voz-propria`, pasta `v1` | **partes 1 e 2 feitas** (Python e fala livre), sem PR; a parte 3 (rodada offline) parece em curso: `artifacts_voz/rodada1/` e edições não commitadas no `verificador.py` | Mexe em `educacao.py` (janela de fala, `ConfigMentira`), `CLAUDE.md`, `REGISTRO_DESVIOS`. |
| **M1: confiança de combate** | `design-m1-confianca`, `v1-pesquisa` | **só desenho**, aguardando aprovação | Também pede pets v5 e mexe em `motor.ts`, `gambits_pet.ts`, `educacao.py`. |
| Corpus de personalidade Digimon | outro chat; `D:\Trab\digilab\docs\corpus_digimon\` | em auditoria | Entra na parte 3 da voz própria quando aprovado. |

**Os três branches vão conflitar** nos mesmos arquivos (`motor.ts`, `educacao.py`, `CLAUDE.md`, `REGISTRO_DESVIOS.md`, `mapa_constantes.json`). Eles precisam entrar em fila, um rebase por vez, e a "versão de pet" tem que ser uma só: **v5 = evolução canônica + voz + M1**, não três v5 diferentes.

## 3. Pendências consolidadas (tudo o que está aberto, em um lugar só)

**Decisões do Matheus que travam trabalho:**
1. Aprovar ou não o **M1** (4 decisões na seção 7 do desenho).
2. **Ordem de merge** dos três branches (recomendação na seção 5).
3. Leitura humana pendente: `revisao.csv` da moldura (s/n) e a avaliação cega da fala livre (`avaliacao_cega.csv`).
4. Combate: E2 (espécie dominante) e E4 (adulto esmaga adolescente) são redesenho, não calibração; e a recusa do pet (B2) mexeria no motor.
5. Os dois "Não me deixe…" do qwen2.5:7b contam como manipulação?

**Pesquisa (o que falta para ter uma pergunta viva):**
- Reescrever a hipótese central. Proposta na seção 5.
- A interação dono × ambiente do E1 tem os 1280 registros gravados em `v1-linhagem/artifacts_linhagem/…/vidas/` (fora do git): dá para investigar sem vida nova.
- O vínculo (achado 7) precisa de redesenho antes de qualquer uso como medida.

**Jogo (especificado e não feito):**
- `PENDENCIAS_PRANCHAS.md`: telas e ações das pranchas ainda não implementadas.
- `DESIGN_VOZ_PROPRIA` parte 4 (web) e parte 3 (rodada) em curso.
- Stand-by registrado: combate 1×1 em tempo real; E2 espécies.
- Os passos M2–M4 e as fases 2–3 do `PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md` (economia, arenas, Frontier, equipamento): são **ideia**, não fila.

**Tarefas só no papel (nunca executadas):** `TAREFA_AFINACAO_BANDIT`, `TAREFA_QD_MAP_ELITES`, `TAREFA_CAMPEAO_SECRETO` (todas não versionadas, em `v1/docs/`).

## 4. Limpeza: o que não faz mais sentido manter

### 4.1 Documentos

| arquivo | situação | recomendação |
|---|---|---|
| `docs/IDEIAS_PROGRESSAO_PERSONALIDADE.md` (versionado) | banco de ideias que virou o `PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md` | **apagar** (o git guarda o histórico); a tabela "o que já existe" dele já está na pesquisa |
| `docs/PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md` | cita referências fora da lista verificada (Hsu, Rankin, Maier e Seligman, Spronck, Gosling) e usa Pokémon e Monster Rancher como evidência | **corrigir**: remarcar como "não verificado pela revisão de 2026-09-29" e tirar os jogos da condição de evidência. Não apagar: as seções de arquitetura e MVP continuam válidas |
| `docs/PLANO_LINHAGEM_ALIFE.md` | encerrado como pesquisa | **manter** como registro (já diz "encerrado" no topo) |
| `docs/TAREFA_AFINACAO_BANDIT.md` (não versionado) | queria rodar antes do piloto de poder; o piloto já rodou sem ela, e a hipótese que ela protegia foi refutada | **arquivar fora do repo** (`D:\Trab\digilab\docs\arquivo\`) |
| `docs/TAREFA_QD_MAP_ELITES.md`, `TAREFA_CAMPEAO_SECRETO.md` (não versionados) | nunca executadas; QD continua útil para gerar rivais do Frontier | **manter fora do repo** até existir a fase de arenas; o Campeão depende da QD |
| `docs/TAREFA_FRONT_TS.md`, `TAREFA_INTERFACE_UP.md`, `TAREFA_PLANILHA_PROGRESSAO.md`, `UI_GUIDELINES.md`, `VALIDACAO_VISUAL.md`, `REVISAO_INTERFACE_UP.md`, `ASSETS_UP.md`, `estilo_up/` (não versionados) | são as especificações e o guia de estilo do app **que está no `main`**; hoje só existem na sua pasta | **versionar** os que o `CLAUDE.md` cita (`TAREFA_FRONT_TS`, `TAREFA_INTERFACE_UP`, `TAREFA_PLANILHA_PROGRESSAO`, `UI_GUIDELINES`, `estilo_up/DIRETRIZES_REPLICAR.md`). Se algum tiver pixel da Bandai, fica fora |
| `docs/CONTEXTO_CLAUDE_SCIENCE.md` (não versionado) | contexto para outra LLM, superado pelo `CONTEXTO_DIGILAB_2026-09-29.md` fora do repo | **apagar** |
| `docs/pve.py` e `servidor/pve.py` (não versionados) | script de calibração PvE de 24/09 que importa `combate` e `bots` de um layout antigo; não roda no repo atual | **apagar** (é do v0) |
| `tools/inventario_sprites.py` (não versionado) | ferramenta sua de inventário do atlas | manter fora do repo, ou versionar se não tiver pixel |
| `D:\Trab\digilab\ESPEC_COMBATE_V2.md`, `TAREFA_MEMORIA_EXPRESSAO.md` (soltos na raiz) | cópias dos que já estão em `v1/docs/` | **apagar** as cópias soltas |
| `D:\Trab\digilab\v0\`, `v0.zip`, `digilab-v1.bundle` | versão antiga e um bundle de backup | mover para uma pasta `arquivo\` fora do trabalho diário; o `CLAUDE.md` já diz que o v0 não roda |
| `D:\Trab\digilab\docs\` (CONTEXTO, revisões, corpus) | material de referência **fora** do repo | **trazer para o repo** em `v1/docs/referencias/` a revisão bibliográfica (`.md`, `.csv`, `.bib`) e o contexto; o corpus Digimon entra só depois da auditoria e sem citações longas |

### 4.2 Branches e pastas de trabalho

- **60 branches locais já mergeados** no `main` (todos os `front-ts-*`, `interface-up-*`, `poder-etapa*`, `pendencias-*`, etc.). Apagar todos os locais que já estão no `main`; os remotos podem ficar como histórico ou ser apagados junto (o histórico está nos merges).
- **Só 3 branches não mergeados**, e os 3 estão vivos: `design-evolucao-canonica`, `design-voz-propria`, `design-m1-confianca`.
- **Pastas de trabalho (worktrees):** `v1-linhagem` (só guarda os registros do E1 fora do git: mover os `vidas/` e `partidas_neutra.json` para `arquivo\` antes de apagar), `v1-fundos` e `v1-fala-livre` (branches já mergeados: apagar). Ficam `v1`, `v1-evolucao` e `v1-pesquisa`.

### 4.3 Artefatos

- Os `artifacts_*` de runs canônicas ficam como estão: o que é evidência está versionado (resumos), e as vidas ficam fora do git por tamanho (a `confirmatoria` tem 112 MB, a `v3c` 85 MB).
- `artifacts_combate_v2_calibracao` (0 arquivos versionados) e `artifacts_voz` (em produção): conferir com quem está rodando antes de tocar.
- Nenhum artefato deve ser apagado do disco enquanto o `CLAUDE.md` citar a run.

## 5. Para onde ir: três caminhos e uma recomendação

**Caminho A — fechar o jogo v5.** Colocar em fila e mergear as três frentes, na ordem em que menos se atropelam:
1. **Evolução canônica** primeiro: é a que mais mexe no motor e já está pronta.
2. **Voz própria** em seguida, rebaseada em cima: mexe no Python e na fala, pouco no `motor.ts`.
3. **M1** por último, depois de aprovado: é pequeno e depende dos pets v5 que a evolução cria.

   O resultado é uma versão coerente do jogo, com um único "pet v5", pronta para ser jogada por você por alguns dias antes de qualquer mecânica nova. Custo: baixo, é trabalho de integração.

> **Atualização (mesmo dia, `docs/ANALISE_DONO_AMBIENTE_E1.md`):** a análise dos registros do E1 mostrou que a interação dono × ambiente vem de regras que nós escrevemos (quem trata lesão; a qualificação no sparring) e da loteria de formas: **a forma final explica 96% da taxa no painel**. A V4 proposta abaixo testaria essas regras e **não deve rodar**. O caminho B passa a ser: medir o dono pela distribuição de formas que ele produz, ou equilibrar os arquétipos antes de qualquer nova medida de efeito do dono.

**Caminho B — reescrever a pesquisa.** A hipótese central morreu, e o que sobrou de sinal é o cuidado e o ambiente. A pergunta que os dados apontam:

> *O cuidado coerente reduz a variância de desfecho do pet entre ambientes, e essa redução, não a força na arena, é o que diferencia um bom dono.*

   Ela é testável com o que já existe: o E1 já mede dono × ambiente, a V3 já tem educação e morte, e os 1280 registros do E1 permitem uma análise exploratória sem vida nova. O passo confirmatório seria uma **V4 pré-registrada**: atencioso × aleatório com educação ligada, condição neutra, o tratamento das mortes decidido antes, e 160 ovos com sementes de ambiente separadas. Custo: médio; é o único caminho que devolve ao projeto um resultado de pesquisa positivo e honesto.

**Caminho C — escrever.** Consolidar o que já foi medido num relatório técnico (a confirmatória refutada, a decomposição de variância, a espiral sombria, o vínculo invertido) com a revisão bibliográfica verificada. Isso não depende de nenhuma mecânica nova e é o que a pasta `docs/referencias/` viabiliza.

**Recomendação: A e depois B, com C em paralelo quando houver tempo.**
- Fazer A primeiro porque o custo é baixo e o trabalho já está feito em três lugares que só faltam se encontrar; deixar três branches abertos por mais tempo só aumenta o conflito.
- Fazer B logo depois porque, sem uma pergunta de pesquisa viva, cada mecânica nova do jogo (M2, M3, M4, economia) vai crescer sem critério de parada. A V4 dá esse critério.
- **Não** começar M2–M4, economia, arenas ou Frontier antes de A e B. Elas estão desenhadas e podem esperar; o custo de esperar é zero, e o custo de abrir mais frentes agora é o que a seção 2 mostra.

## 6. Ordem concreta dos próximos passos

1. Limpeza sem risco (hoje): apagar branches locais mergeados; apagar as cópias soltas e o `pve.py`; mover `v0`, `v0.zip` e o bundle para `arquivo\`; guardar as vidas do E1 e apagar `v1-linhagem`, `v1-fundos`, `v1-fala-livre`.
2. Versionar as especificações do app e trazer a revisão bibliográfica para `docs/referencias/` (um PR pequeno, sem código).
3. Corrigir o `PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md` pela lista verificada e apagar o `IDEIAS_*` (mesmo PR).
4. PR e merge da evolução canônica; rebase e PR da voz própria (depois da parte 3 e da sua leitura dos números); decisão sobre o M1.
5. Análise exploratória de dono × ambiente nos registros do E1 (sem vida nova) e o plano da V4, registrado antes da run.
6. Só então: M2 (medalhas) ou M3 (relação), o que a V4 sugerir.
