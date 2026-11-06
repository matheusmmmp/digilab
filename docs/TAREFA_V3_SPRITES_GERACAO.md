# TAREFA V3 — SPRITES_GERACAO (2026-11-05)

Coordenador: o Gerente da missão (sessão Claude Code, worktree `v3-sprites-geracao`), dentro da frente SPRITES_ACOES
(`docs/TAREFA_V3_SPRITES_ACOES.md`). Worker: uma sessão por etapa (seção 3.5). Worktree e branch: `v3-sprites-geracao`. Status: ABERTA,
tudo PROPOSTO até o Matheus decidir a seção 8.

Categoria: arquitetura. Origem: Matheus, 2026-11-05: pipeline híbrido (still mestre, Agent Sprite Forge, Aseprite pelo pixel-mcp) para
gerar os clipes de ação do pet, começando pelo Comer, no formato do atlas de clipes.

Esta etapa é só de planejamento: nada foi instalado, nenhuma imagem foi gerada e nenhuma cota foi gasta.

## 1. Pergunta

Um clipe `Comer` gerado pelo pipeline híbrido fica igual ou melhor que o `Comer` derivado do UP (missão M1 da SPRITES_ACOES, PR #572)?
O julgamento vem por duas vias: a leitura cega do dono (seção 4.2) e os gates numéricos por clipe (seção 4.1).

- **Não vem de hipótese de pesquisa.** É produto (`docs/PRODUTO_VISAO.md`), como a frente SPRITES_ACOES inteira (seção 1 dela).
- **"Igual ou melhor" quer dizer duas coisas ao mesmo tempo:**
  - o clipe gerado passa em todos os gates da seção 4.1;
  - o Matheus, sem saber qual é qual, marca o gerado como "melhor" ou "igual" ao derivado.
  - Se faltar uma das duas, a resposta é "pior", e ela é registrada como está.
- **Por que importa:** o catálogo das bocas da M1 achou o par de boca aberta e fechada do UP em só 11 dos 60 Digimon (SA-9). Os outros
  vão de prova 1 (inclinar sem abrir a boca) ou com a boca pintada à mão. Um gerador que passa aqui é o caminho para os 49 fracos e
  para as ações sem pose no UP (seção 3.3 da SPRITES_ACOES: deitado, mastigar, expressão nova).

## 2. Depende de

- **Os PRs #568, #569 e #572: todos na `main`.** Conferido com `gh pr view` em 2026-11-05:
  - o #569 (a tarefa SPRITES_ACOES) entrou às 19:25 UTC;
  - o #568 (M2, o `Comer` no `atlas.ts`) entrou às 21:30 UTC;
  - o #572 (M1, `tools/sprites_acoes/`) entrou às 22:10 UTC;
  - também já entraram a M3 (#583) e a M4 (#585);
  - esta worktree saiu do `389f3893`, o merge do #572.
- **O que eles fixam e esta missão não muda:**
  - `web/app/src/atlas.ts`: `CLIPES_ACOES = ["Comer", "Comer_objeto"]`. O `juntarClipes` falha alto quando:
    - um clipe não tem quadros;
    - os `ms` não casam com os quadros;
    - um `<Tag>_objeto` não casa com o clipe dele em quadros e `ms`;
    - uma ação existe numa forma e falta em outra.
  - `Assets/gerar_atlas_up_clipes.py` (fora do git): a opção `--acoes DIR` lê outro diretório de export. Ele falha alto quando:
    - a caixa difere da caixa do export do UP;
    - aparece uma tag fora de `CLIPES_ACOES` (hoje, só o `Comer`);
    - um quadro tem trim ou rotação;
    - uma forma do catálogo fica sem a ação.
  - Sobre o `--acoes DIR`:
    - com `--saida` fora de `Assets` e com `--prova`, ele aceita um lote parcial;
    - **esta missão usa essas duas opções e não muda o script.**
  - `tools/sprites_acoes/`: o `gerar.lua`, as âncoras dos 60 Digimon (`ancoras.json`: caixa, `pe_idle`, boca, carne) e o
    `visualizador.py`. Esta missão lê esses arquivos e não os muda.
- **Colisão com o lote 1 (ativo):**
  - a worktree `v3-sprites-lote1` (branch `v3-sprites-lote1`, sem PR aberto em 2026-11-05) gera Feliz, Sacudir, Chamar e Emburrar do
    Agumon pela receita derivada;
  - essas tags já estão em `remaster/acoes/export/Agumon.json`, e o `gerar_atlas_up_clipes.py` atual levantaria erro com elas;
  - **regra desta missão:**
    - ela nunca escreve em `remaster/acoes/`;
    - tudo dela vai para `remaster/geracao/` (seção 3.2);
    - o atlas candidato lê só a tag `Comer` do derivado (seção 3.4, etapa E6).
- **As decisões D-SG-1 a D-SG-5** (seção 8). A etapa G1 (seção 3.5) não gasta nada e pode começar só com a D-SG-4. A G2 gasta dinheiro
  e não sai sem a D-SG-1, a D-SG-2 e a D-SG-5.
- **Os sprites são os do Digimon UP do projeto.** A decisão é definitiva (`docs/UI_GUIDELINES.md` 5.1) e não volta como pergunta.
  - Um clipe gerado a partir de um quadro do UP é derivado dele e herda a procedência e o crédito.
  - Por isso fica fora do git, como os quadros da M1.
  - Os termos de cada provedor de API se somam a isso. Quem confere é o worker da G2, antes do primeiro envio.

## 3. Mudança mínima

### 3.1 O que muda

- **Nenhum código do motor.** `git diff origin/main -- web/app/motor web/app/test/gabaritos digilab experiments` sai vazio em todas
  as etapas.
- **Também não mudam:** `engine.py`, as versões de pet, o log, o save e o replay.
- **Versionado: só os scripts de geração e conversão,** em `tools/sprites_geracao/` (é a etapa G1):
  - `ficha.py`: lê o export do UP (`remaster/export/<Nome>.png/.json`) e as âncoras da M1, e grava a ficha do sprite:
    - a caixa W×H;
    - o `pe_idle`;
    - a paleta, com todas as cores RGB opacas do export inteiro do Digimon, como `.gpl` do Aseprite e em JSON;
    - a faixa de área;
    - os `ms` do derivado, que servem de alvo;
  - `converter.py`: o resultado do gerador (quadros PNG e o JSON do Sprite Forge) vira um export no formato do `remaster/acoes/export`:
    - `json_array` e `frameTags`, sem trim, na caixa do UP;
    - a tag `Comer` e o `<Nome>_objeto` nas mesmas tags e `ms`;
    - o snap à paleta e o export passam pelo pixel-mcp, com o Aseprite em linha de comando como reserva (seção 3.4, E3);
  - `gates.py`: os gates da seção 4.1 sobre um export, que gravam o `gates.json`. Rodam também sobre o `Comer` derivado, que é a linha
    de base;
  - `montar_candidato.py`: monta o diretório do atlas candidato (seção 3.4, E6);
  - `tests/test_sprites_geracao.py`: os gates sobre arte sintética própria. Cada gate tem um caso que passa e um que falha alto.
- **Fora do git, em `remaster/geracao/`:** a ficha, os takes, os vídeos, os quadros, o `.aseprite`, o export, o `gates.json`, o
  ledger de custo, o atlas candidato e as capturas.
- **Uma mudança de teste no web, só se a E6 precisar:**
  - uma variável de ambiente no `web/app/e2e_capturas/sprites_comer.spec.ts`, que aponta a rota do atlas de clipes para o candidato;
  - hoje ele lê fixo `Assets/digilab_atlas_up_clipes.json`;
  - sem a variável, o teste sai igual a hoje;
  - não é código do jogo.
- **O `Assets/digilab_atlas_up_clipes.json` do jogo não muda nesta missão.** Ele só seria regerado com o clipe gerado depois de o
  Matheus aprová-lo no visualizador e decidir trocar. Esse é o portão da seção 3.3, passo 5, da SPRITES_ACOES, e fica para outra tarefa.

### 3.2 Onde fica cada coisa (fora do git)

```text
D:\Trab\digilab\remaster\geracao\<Nome>\
  ficha.json, paleta.gpl                     E0
  still\take_0.png (o quadro do UP), take_1..N.png, master.json   E1
  forge\  (o projeto do Sprite Forge: clipes, .forge\ledger.jsonl)  E2
  aseprite\<Nome>_comer.aseprite             E3
  export\<Nome>.png/.json, <Nome>_objeto.png/.json   E4
  gates.json, gates_derivado.json, contato_x4.png    E5
  revisoes\E0..E7.md                         o veredito de cada revisor
D:\Trab\digilab\remaster\geracao\candidato\export\   E6 (os 60, só o Comer)
D:\Trab\digilab\remaster\geracao\candidato\atlas\    E6 (o atlas gerado com --saida)
D:\Trab\digilab\remaster\geracao\capturas\           E6
```

### 3.3 Os papéis

| papel | quem | o que faz | o que não faz |
|---|---|---|---|
| diretor | o worker (Claude Code) | escreve a ficha e o prompt do clipe, chama as ferramentas, roda os gates, chama o revisor, registra o custo | não desenha e não aprova o próprio trabalho |
| gerador do still e do clipe | **Agent Sprite Forge** (0x0funky, MIT; `master_still.py`, `sprite_set.py`) | faz os takes do still; faz o clipe imagem para vídeo da ação com os gates dele (área, pés, identidade, zoom, virada, bordas, fundo, objetos extras, movimento, pose final, sangramento de cor, timing) e até 3 retakes | não decide a paleta final; o acabamento "pixel" dele é rascunho, e a paleta que vale é a do sprite (E3) |
| mãos no Aseprite | **pixel-mcp** (willibrandon, MIT, Go, Aseprite em modo batch) | importa os quadros, faz o snap à paleta do sprite (distância em LAB), o alfa binário, as tags e os `ms`, e o `export_spritesheet` com JSON | não inventa cor nem pose |
| conversão | `tools/sprites_geracao/converter.py` | põe na caixa do UP com o pé no `pe_idle`, junta a sombra do `Idle` e a camada `comida`, grava no formato que `atlas.ts` lê | não muda o `gerar_atlas_up_clipes.py` |
| gates | `tools/sprites_geracao/gates.py` | os números da seção 4.1, no derivado e no gerado | não aprova anatomia nem movimento (o próprio Sprite Forge avisa: "numeric QA never approves anatomy or motion alone") |
| revisor | um agente novo a cada etapa, que recebe só o artefato | aponta erro, não edita; escreve "talvez" na dúvida; termina com "aprovado" ou "reprovado"; aprova antes de qualquer envio pago | não recebe a conclusão do diretor |
| dono | Matheus | aprova o still mestre, o teto de gasto e a leitura cega final | — |

**Os prompts de revisão** são os de `04_PROMPTS_REVISAO.md` (vault `DigiLab Research/40 Produção e divulgação/`, rev. 5), adaptados a
sprite. A regra de uso não muda: agente novo, só o artefato, só aponta. O que muda em cada um:

- **R-ficha (do 2a), depois da E0.**
  - **Material:** a ficha, a paleta em amostras, o quadro do `Idle` a 4× e o `Comer` derivado em tira a 4×.
  - **Perguntas:**
    1. A ficha pede algo que o UP não tem (pose, objeto, mão segurando)?
    2. A ação do meio (inclinar, abrir, fechar duas vezes, voltar) está toda descrita?
    3. O início e o fim são o mesmo quadro parado?
    4. Lados escritos como lados da tela?
    5. O que um modelo de vídeo erra aqui (boca em 94×68, cauda, braço curto, sombra que se move)?
- **R-still (do 2b), depois da E1.**
  - **Material:** os takes reduzidos à caixa do UP a 4×, o quadro do UP ao lado e as medidas da E1 (caixa, pé, cores fora da paleta
    antes do snap).
  - **Perguntas:**
    1. É o mesmo Digimon (cor, chifre, garra, olho)?
    2. Algo a mais (objeto, contorno, fundo)?
    3. O pé no mesmo lugar?
    4. Em miniatura, ainda se lê?
- **R-envio (do 3), antes de cada envio pago da E2.**
  - **Material:** o prompt do clipe, o still aprovado, o `Comer` derivado como referência de tempo, a estimativa da chamada e o saldo do
    teto.
  - **Perguntas:**
    1. Cada frase do prompt bate com o still?
    2. A ação tem causa e começo e fim parados?
    3. Está escrita como o que deve acontecer, não como o que não deve? Só a negação dos fechos padrão é aceita (sem fundo, nenhum outro
       personagem, sem texto).
    4. A estimativa cabe no teto?
- **R-clipe (do 2b e do 4), depois da E5.**
  - **Material:** a folha de contato do gerado e a do derivado (a 4×, quadro a quadro, com os `ms`) e o `gates.json` dos dois. Os dois
    vão sem dizer qual é qual.
  - **Perguntas:**
    1. Quadro duplicado ou salto?
    2. Cor estranha?
    3. O pé ou a caixa mexendo?
    4. A boca abre e fecha?
    5. A carne casa com a boca?
    6. A volta ao primeiro quadro emenda?
- **R-final (do 4), depois da E6.**
  - **Material:** só o JSON do atlas candidato, as capturas de 390 e 1280 px e o resultado do e2e.
  - **Perguntas:**
    1. O jogo caiu no gesto de reserva?
    2. O recorte da ilha corta o pet?
    3. A carne aparece no lugar?

### 3.4 O pipeline, etapa a etapa (um Digimon, a ação Comer)

| etapa | o que faz | ferramenta | sai | revisão e portão | custo |
|---|---|---|---|---|---|
| **E0 ficha** | caixa, `pe_idle`, paleta do sprite (todas as cores opacas do export do UP), faixa de área e `ms` alvo; o texto da ação: inclina para a comida, abre e fecha a boca duas vezes, volta ao quadro inicial | `ficha.py` | `ficha.json`, `paleta.gpl` | R-ficha | zero |
| **E1 still mestre** | o take 0 é o quadro do `Idle` do UP, ampliado por vizinho mais próximo; os takes 1..N saem do Sprite Forge (`master_still.py`) com o take 0 como referência; cada take é reduzido à caixa e medido (caixa, pé, cores fora da paleta) | Sprite Forge e `gates.py` (modo still) | `still/`, `master.json` | R-still, e depois **o Matheus aprova um take** (o único checkpoint de atenção dele antes do fim) | N imagens (seção 4.3) |
| **E2 clipe** | um clipe imagem para vídeo do still aprovado, com o último quadro preso ao primeiro (o Comer repete); o Sprite Forge faz o keying, o registro e o corte do laço pelos gates dele, e o `retime` leva o clipe a cerca de 0,9 s (o derivado tem 0,87 a 0,93 s); no máximo 3 takes, com `--budget-usd` e `--max-calls` no teto da D-SG-5 | Sprite Forge (`sprite_set.py run`) | `forge/`, com o ledger | **R-envio antes de cada envio pago**; reprovado não envia | 1 a 3 vídeos |
| **E3 limpeza** | importa os quadros do clipe, faz o snap à `paleta.gpl` (LAB), alfa 0 ou 255 acima do pé, redução à escala da caixa por vizinho mais próximo, a tag `Comer` e os `ms` inteiros | pixel-mcp; reserva: o MCP do Aseprite já usado na M1 (`load_palette_file`, `remap_colors_in_cel_range`) ou o Aseprite em linha de comando, como em `tools/sprites_acoes/gerar_acoes.py` | `aseprite/<Nome>_comer.aseprite` | — | zero |
| **E4 conversão** | põe na caixa do UP com o pé na linha `pe_idle`, junta a sombra do quadro do `Idle` (sem mudança, como na M1) e a camada `comida` (a carne de arte própria da M1, pela `carne_regra` de `ancoras.json`), e exporta no formato do `remaster/acoes/export` | `converter.py` e o Aseprite em linha de comando | `export/<Nome>.png/.json` e `_objeto` | — | zero |
| **E5 gates** | os gates da seção 4.1 no gerado e no derivado; a folha de contato dos dois | `gates.py` | `gates.json`, `gates_derivado.json`, `contato_x4.png` | R-clipe; um gate que falha volta à E2 (enquanto houver take e teto) ou fecha como "pior" | zero |
| **E6 atlas e jogo** | `montar_candidato.py` copia os 60 do `remaster/acoes/export` só com a tag `Comer` (sem o lote 1) e troca o Digimon da prova pelo gerado; `python Assets/gerar_atlas_up_clipes.py --acoes remaster/geracao/candidato/export --saida remaster/geracao/candidato/atlas` (as 60 formas, sem `--prova`); o e2e e as capturas de 390 e 1280 px com a rota apontando o candidato; a leitura cega no visualizador (seção 4.2) | o script do atlas sem mudança, Playwright, `tools/sprites_acoes/visualizador.py` | `candidato/`, `capturas/` | R-final, e depois **a leitura cega do Matheus** | zero |
| **E7 lições** | o custo real (ledger), o que errou e o que deu certo, o resultado da pergunta 1 | — | a seção 9 desta tarefa e `docs/registro/2026-11.md` | — | zero |

### 3.5 As etapas de entrega

Cada etapa é uma sessão e um PR, com o merge pelo Matheus.

- **G1 — os scripts, sem gasto (branch `v3-sprites-geracao-g1`):**
  - o que faz: `ficha.py`, `gates.py`, `converter.py`, `montar_candidato.py` e o teste;
  - a E0 e a E5 rodadas sobre o `Comer` derivado do Digimon da D-SG-4. É a linha de base: o derivado tem de passar nos gates. Se não
    passa, a faixa está errada e volta ao Matheus antes de qualquer gasto;
  - não instala o Sprite Forge nem o pixel-mcp; o converter é testado com quadros sintéticos;
  - **entrega:** `python -m pytest tests/test_sprites_geracao.py -q` e o `gates_derivado.json` com o caminho no PR.
- **G2 — a geração, com gasto (branch `v3-sprites-geracao-g2`):**
  - antes de tudo, a instalação com o ok do Matheus (D-SG-1): o Sprite Forge e as dependências dele (Python com numpy, Pillow e scipy
    numa venv fora do pacote `digilab/`; ffmpeg 5.1 ou mais novo), o pixel-mcp e a chave da API no ambiente, nunca no repositório;
  - depois, a E1 a E7.
  - **entrega:** os critérios da seção 7.

## 4. Experimento e gate

Não há run de pesquisa: não há vida, semente nem plano de análise. Os gates são de asset, por clipe. Todos os números abaixo são
PROPOSTOS, SEM FONTE, até o Matheus decidir.

### 4.1 Os gates numéricos por clipe

O `gates.py` roda cada gate no clipe gerado e no derivado, quadro a quadro. Um gate falha alto se qualquer quadro falhar.

| gate | regra | de onde vem |
|---|---|---|
| **G-PAL** paleta | todo pixel com alfa 255 do personagem é uma cor da paleta do sprite: o conjunto das cores RGB opacas do export inteiro do UP daquele Digimon (`remaster/export/<Nome>.png`). Pode haver **0** pixels fora. A camada `comida` confere contra a paleta da carne da M1 | pedido do Matheus; o snap da E3 deve garantir |
| **G-CAIXA** caixa | todos os quadros com `sourceSize` igual à caixa do UP (`ancoras.json`), sem trim e sem rotação, e nenhum pixel opaco cortado pela borda | `gerar_atlas_up_clipes.py` (`ler_folha`) |
| **G-PE** âncora dos pés | a última linha opaca do personagem acima da sombra é a `pe_idle` em todos os quadros (diferença 0); nenhum pixel do personagem abaixo dela; o centro x das 3 linhas de baixo do personagem fica a no máximo 2 px do mesmo centro no quadro 0 do `Idle`; a sombra é a do `Idle`, byte a byte | SPRITES_ACOES 3.4 ("o pé"); o achado da M4 (o WereGarurumon pulando a cada mordida) |
| **G-ALFA** alfa binário | acima da linha do pé, no máximo 2 pixels por quadro com alfa diferente de 0 e 255 (D-SG-E, Matheus, 2026-11-06; antes: 0), e a carne com 0. A sombra fica fora do gate (desvio D-SG-A, seção 9) | pedido do Matheus |
| **G-AREA** área | os pixels opacos do personagem em cada quadro ficam em [0,90 × a menor área do `Idle`; 1,10 × a maior área do `Idle`] do mesmo Digimon. A carne conta à parte e não pode passar de 15 % da área do `Idle` | PROPOSTO; conferido primeiro no derivado (G1) |
| **G-MS** duração | os `ms` são inteiros e maiores que 0, um por quadro; a tag `Comer` é `forward` com laço; o `Comer_objeto` tem os mesmos quadros contados e os mesmos `ms`; o ciclo dura de 800 a 1 000 ms; cada quadro dura no máximo 200 ms | `atlas.ts` (`juntarClipes`); SPRITES_ACOES 3.2 (~0,9 s) |
| **G-CARGA** o jogo carrega | o `gerar_atlas_up_clipes.py` roda sem erro sobre o candidato, e o `juntarClipes` (no e2e) não levanta | seção 7 |

**Os gates do Sprite Forge** (área, pés, identidade, bordas, objetos extras, pose final, sangramento de cor, timing) rodam antes, na
E2, para decidir o retake. Eles não substituem os da tabela, que são os do formato do DigiLab.

### 4.2 A leitura cega do dono

- **Como funciona:**
  - no visualizador da M1 (`http://localhost:8802`), o Digimon da prova aparece com dois clipes lado a lado, "A" e "B", quadro a quadro
    e em laço, na escala 4×;
  - a ordem é sorteada uma vez e gravada em `remaster/geracao/<Nome>/cego.json`, que o Matheus não vê antes de responder;
  - o Matheus responde **A melhor, B melhor ou iguais**, mais uma frase;
  - a chave se abre depois da resposta;
  - a resposta e a frase vão literais para a seção 9.
- **O que conta:** a leitura vale uma vez. Mexer no clipe depois dela é uma prova nova, registrada como tal.

### 4.3 O custo estimado por clipe

O câmbio usado é **US$ 1 = R$ 5,50, A CONFIRMAR**. É um valor de referência deste planejamento, não uma cotação do dia. Os preços em
dólar foram pesquisados na web em 2026-11-05 (página de exploração do fal.ai e agregadores). As fontes divergem entre si, então são
estimativas: o worker confere a página do modelo antes do primeiro envio.

| item | quantidade por clipe | preço unitário (US$) | US$ | R$ (5,50) |
|---|---|---|---|---|
| takes do still (uma vez por Digimon, não por ação) | 3 imagens | ~0,04 a 0,15 | 0,12 a 0,45 | 0,66 a 2,48 |
| clipe de vídeo, Kling 3.0 Pro no fal.ai, sem áudio | 5 s por take, 1 a 3 takes | ~0,112 por s | 0,56 a 1,68 | 3,08 a 9,24 |
| clipe de vídeo, Seedance 2.0 Fast no fal.ai (alternativa) | 5 s por take, 1 a 3 takes | ~0,24 por s | 1,21 a 3,63 | 6,66 a 19,97 |
| **o primeiro clipe (still e Comer), pelo Kling** | | | **0,68 a 2,13** | **3,74 a 11,72** |
| **um clipe a mais do mesmo Digimon (só o vídeo)** | | | **0,56 a 1,68** | **3,08 a 9,24** |

- **Os modelos geram pelo menos 4 a 5 s, e o Comer usa ~0,9 s.** O resto é cortado no `retime`, mas cobrado.
- **A conta para os 60, só como ordem de grandeza:** 60 × (0,68 a 2,13) dá US$ 41 a 128, ou R$ 224 a 703, por ação. Isso não é
  pedido desta tarefa.
- **A rota sem dinheiro:** a CLI local do Codex ou do Grok gasta a cota da assinatura, não reais. Pelo README do Sprite Forge, o Codex
  só faz imagem; o vídeo local é do Grok (6 ou 10 s).
- **O tempo de pessoa:**
  - a aprovação do still: ~10 min;
  - a leitura cega: ~5 min;
  - as revisões são de agentes.

## 5. Entrega

- **Testes:**
  - G1: `python -m pytest tests/test_sprites_geracao.py -q`;
  - G2 e a mudança de teste da E6: em `web/app`, `npm test`, `npm run tipos` e `npm run e2e` (as falhas que já existem na `main`,
    listadas).
- **Registro:**
  - os números escolhidos e os desvios vão numa seção própria no fim de `docs/registro/2026-11.md`, com uma linha no fim do
    `docs/REGISTRO_DESVIOS.md`;
  - o resumo de cada etapa vai no corpo do PR e na seção 9 desta tarefa;
  - o custo real (soma do ledger, em US$ e em R$ com o câmbio do dia) vai no PR da G2.
- **PR:** contra a `main`, com o relato pelo `.github/pull_request_template.md` (o CI confere). Merge só pelo Matheus.

## 6. Fora desta tarefa

- **As outras ações:**
  - o Feliz, o Sacudir, o Chamar e o Emburrar estão no lote 1 derivado (`v3-sprites-lote1`);
  - esta tarefa não os gera, salvo a D-SG-3.
- **Trocar o `Comer` do jogo pelo gerado:** é o portão da SPRITES_ACOES (seção 3.3, passo 5) e precisa de outra decisão.
- **Os outros 59 Digimon e o lote dos 49 fracos.**
- **Mudar o `atlas.ts`, o `gerar_atlas_up_clipes.py` ou o `tools/sprites_acoes/`.**
- **Treinar LoRA de estilo, o Retro Diffusion e o Pixel Art Studio:** são alternativas do vault (`07_PIPELINE_PIXEL_ART_ASEPRITE.md`,
  seção 3), não escolhidas aqui.
- **Sprites de arte própria** (pet novo, frutas, bola). Têm outra procedência e são outra tarefa.
- **O som.**

## 7. Critérios de aceitação

- **G1:**
  - `tools/sprites_geracao/` tem `ficha.py`, `gates.py`, `converter.py` e `montar_candidato.py`;
  - `python -m pytest tests/test_sprites_geracao.py -q` passa, com um caso que falha alto para cada gate da seção 4.1;
  - o `gates_derivado.json` do Digimon da prova existe no caminho dado no PR e passa em todos os gates;
  - `git diff origin/main -- web/app digilab experiments` sai vazio.
- **G2:**
  - **o jogo carrega o atlas candidato sem cair na reserva:**
    - o e2e com a rota no candidato mostra `__digilab.comer() === "clipe"` (o campo da M3) em 390 e 1280 px;
    - nenhum "atlas não carregou" aparece;
  - em `web/app`, `npm test` e `npm run tipos` passam;
  - **o e2e com o clipe novo tem referência aprovada:** as capturas de 390 e 1280 px estão em `remaster/geracao/capturas/`, com o
    caminho no PR, e o Matheus as aprovou (a resposta dele vai citada no PR);
  - o `gates.json` do gerado existe e diz, gate por gate, passou ou falhou;
  - a leitura cega está registrada (seção 4.2) com a chave;
  - o ledger do Sprite Forge soma no máximo o teto da D-SG-5, e o PR traz o custo real;
  - `git diff origin/main -- web/app/motor web/app/test/gabaritos web/app/src digilab experiments` sai vazio. Só o
    `e2e_capturas/sprites_comer.spec.ts` pode mudar, e só pela variável da seção 3.1.

## 8. Precisa do Matheus

Cada decisão vem com a recomendação e o custo de errar. A D-SG-4 está decidida (2026-11-06). As D-SG-1, D-SG-2, D-SG-3 e D-SG-5 foram decididas pelo Matheus em 2026-11-06 ("Continue com o
recomendado": as recomendações abaixo valem como estão; registro D-SG-H).

- **D-SG-1. Qual gerador. DECIDIDA pelo Matheus em 2026-11-06: o Agent Sprite Forge, pela rota fal.ai com o Kling 3.0 Pro sem áudio, e o
  pixel-mcp para o snap**, com o ok para instalar o Sprite Forge, as dependências dele e o ffmpeg (registro D-SG-H).
  - **Recomendação:** o **Agent Sprite Forge** primeiro, pela leitura do levantamento (`05_ARQUITETURAS_ORQUESTRACAO.md` 2.3: "o item mais
    próximo do que o DigiLab precisaria"). Ele é o único da lista com o fluxo still, vídeo e quadros, mais gates por clipe, retake
    limitado, ledger e teto em dólar.
  - **A rota:** fal.ai, com o Kling 3.0 Pro no vídeo, o mais barato por segundo entre os que ele lista com o último quadro preso.
  - **As mãos:** o pixel-mcp, que só roda local e não gasta. Escolher isso inclui o ok para instalar os dois e pôr a chave da API no
    ambiente.
  - **As alternativas:**
    - o Retro Diffusion mostra o preço antes (`check_cost`), mas anima a partir de um quadro, não de vídeo;
    - a rota local do Grok, sem reais.
  - **Custo de errar:**
    - no máximo o teto da D-SG-5 e uma sessão;
    - nada entra no jogo, porque o atlas candidato fica fora de `Assets`;
    - trocar de gerador depois aproveita a G1 inteira (ficha, gates, conversão).
- **D-SG-2. Quantos takes do still. DECIDIDA pelo Matheus em 2026-11-06: 3 takes gerados, mais o take 0** (registro D-SG-H).
  - **Recomendação:** **3 takes gerados, mais o take 0**, que é o próprio quadro do `Idle` do UP e não custa nada. O take 0 serve de
    controle: se nenhum gerado for tão fiel quanto ele, o Matheus escolhe o take 0, e a E2 parte dele. O vault pede de 3 a 6. O exemplo
    do Sprite Forge usa 3.
  - **Custo de errar:**
    - com poucos takes, um still fraco contamina todos os clipes daquele Digimon, porque tudo deriva dele;
    - com muitos, cada take a mais custa ~US$ 0,04 a 0,15 e mais tempo de olho na aprovação.
- **D-SG-3. Feliz e Emburrar: depois do Comer ou junto. DECIDIDA pelo Matheus em 2026-11-06: depois** (registro D-SG-H).
  - **Recomendação:** **depois.** Só depois de a pergunta 1 dar "igual ou melhor" no Comer, como a SA-1 fez com o derivado.
  - **Duas observações:**
    - o Feliz e o Emburrar já estão sendo feitos pela receita derivada no lote 1 (`v3-sprites-lote1`), e gerá-los junto disputa o
      mesmo Digimon e a mesma pasta;
    - o pedido dizia "Feliz e Acalmar"; o Matheus esclareceu em 2026-11-05 que o "Acalmar" é o **Emburrar** (registro D-SG-B).
  - **Custo de errar:**
    - junto, dobra o gasto antes de saber se o pipeline serve, e colide com o lote 1;
    - depois, atrasa as duas ações em uma etapa.
- **D-SG-4. O Digimon da prova. DECIDIDA pelo Matheus em 2026-11-06: o Agumon** (a recomendação foi aceita; registro D-SG-D).
  - **Recomendação:** o **Agumon.**
    - É o derivado mais forte (par de boca real do UP, perfil, aprovado na prova 2), então "igual ou melhor" ali é a barra mais
      exigente.
    - Tem a carne, as âncoras e as capturas da M4 prontas.
  - **A alternativa:** um dos 26 sem boca (por exemplo o Angemon, de frente), onde o gerado tem mais a ganhar, mas a comparação diz
    menos sobre a qualidade.
  - **Custo de errar:** com o Agumon, um "igual" ainda não prova que o gerado salva os 49 fracos. A próxima prova seria num sem boca, a
    mais 3,08 a 9,24 reais pelo vídeo.
- **D-SG-5. O teto de gasto e o câmbio. DECIDIDA pelo Matheus em 2026-11-06: US$ 5, com `--budget-usd 5 --max-calls 8`**; o câmbio do
  dia do gasto vai no PR, com a fonte (registro D-SG-H).
  - **Recomendação:** um teto de **US$ 5 (R$ 27,50 a 5,50)** para a G2 inteira, passado ao Sprite Forge por `--budget-usd 5` e
    `--max-calls 8`. O câmbio do dia é confirmado pelo Matheus no momento do ok.
  - A estimativa do primeiro clipe é de US$ 0,68 a 2,13, então o teto cobre o pior caso com folga para um retake de still.
  - **Custo de errar:**
    - baixo demais, a G2 para no meio, com o ledger dizendo onde;
    - alto demais, nada muda, porque o teto é teto e não meta, e cada envio ainda passa pelo R-envio.

## 9. Resumo das etapas

- **2026-11-05, a tarefa (Gerente da missão, Claude Code, Opus 5.5):**
  - **O levantamento:**
    - os #568, #569 e #572, e também a M3 (#583) e a M4 (#585), estão na `main`;
    - o `gerar_atlas_up_clipes.py` já aceita `--acoes`, `--saida` e `--prova`, então a missão não muda o script;
    - o lote 1 escreve no `remaster/acoes/export`, e por isso esta missão vai para o `remaster/geracao/`.
  - **O achado do alfa:** o export do UP do Agumon não tem alfa binário (170 valores de alfa na folha). Numa medida em 3 quadros do
    `Idle` e 3 do `Comer` derivado, a semitransparência está quase toda abaixo do pé (a sombra, 108 a 148 pixels por quadro), com 0 a 2
    pixels acima. Daí o G-ALFA só acima do pé (desvio D-SG-A em `docs/registro/2026-11.md`).
  - **O plano:** os papéis, o pipeline E0 a E7, os gates, o custo e as D-SG-1 a D-SG-5. Nada instalado, gerado ou gasto.
- **2026-11-06, a etapa G1 (worker, Claude Code, Sonnet 5.5, branch `v3-sprites-geracao-g1`):**
  - **O que entrou:** `tools/sprites_geracao/` (`ficha.py`, `gates.py`, `converter.py`, `montar_candidato.py`) e
    `tests/test_sprites_geracao.py` (35 testes, um caso que falha alto por gate da seção 4.1, o conversor com quadros sintéticos, e três
    testes que leem o `remaster/` e pulam sem ele). Nada instalado, gerado ou gasto; `web/app`, `digilab` e `experiments` sem mudança.
  - **A E0 e a E5 sobre o `Comer` derivado do Agumon (35 testes)** (`D:\Trab\digilab\remaster\geracao\Agumon\gates_derivado.json`, fora do git): passam
    G-PAL (0 fora da paleta; 3 684 cores de paleta), G-CAIXA, G-PE (desvio do centro x até 2,00 px, no limite), G-AREA (1 394 a 1 429
    contra a faixa [1 253,7; 1 556,5]; carne 40 a 62 contra 208,95), G-MS (866 ms) e G-CARGA (fumaça sobre o candidato só com derivados).
  - **O derivado reprovava o G-ALFA (a regra era 0 pixels):** nos quadros 2, 4 e 5 do `Comer` (os de boca aberta, quadros 12 e 14 do UP) há 2 pixels
    semitransparentes acima do pé, em (56,56) com alfa 238 e (57,57) com alfa 243, que vêm do próprio UP. A faixa PROPOSTA "0 pixels"
    está errada para o derivado. **Não foi ajustada**: o Matheus decidiu em 2026-11-06 tolerar até 2 px por quadro (registro D-SG-E; D-SG-E DECIDIDA). Com a regra nova
    o derivado passa em todos os gates e o `gates_derivado.json` foi regravado (G-ALFA com limite 2, medido 0 a 2).
  - **O que o conversor assume (contrato PROPOSTO, SEM FONTE):** os quadros do gerador chegam já na paleta e com alfa binário (o snap é
    do pixel-mcp), sem sombra, num `quadros.json` próprio; o JSON real do Sprite Forge é adaptado na G2. O conversor grava o export no formato
    do Aseprite direto (sem chamar o Aseprite) e a carne de arte própria é a porta do `gerar.lua`, que reproduz byte a byte a camada
    `comida` do Agumon derivado (testado).
- **2026-11-06, a etapa G2, primeira parte (worker, Claude Code, Opus 5.5, branch `v3-sprites-geracao-g2`):**
  - **As decisões:** D-SG-1, D-SG-2, D-SG-3 e D-SG-5 registradas como DECIDIDAS (registro D-SG-H).
  - **A instalação (fora do repositório, em `D:\Trab\digilab\ferramentas\`):**
    - o Agent Sprite Forge, clonado em `agent-sprite-forge` (commit `72fa5ad`), com a venv `venv-forge` (Python 3.13; numpy 2.5.4,
      Pillow 13.0.0, scipy 1.18.1);
    - o ffmpeg 9.0.2 (`winget install Gyan.FFmpeg`), com libvpx-vp9 e libx264;
    - o pixel-mcp 0.5.0 (willibrandon), binário oficial do release com o sha256 conferido contra o `checksums.txt`, em `pixel-mcp`. O
      MCP do Aseprite que já existia (`aseprite-mcp`, pacote npm `@letsagents/aseprite-mcp`) **não é** o pixel-mcp.
  - **Os preços, conferidos nas páginas dos modelos no fal.ai em 2026-11-06:** o Kling 3.0 Pro image-to-video custa US$ 0,112 por
    segundo sem áudio (5 s = US$ 0,56; o mínimo do modelo é 3 s); o Nano Banana 2 edit (a imagem padrão do Sprite Forge no fal.ai) custa
    US$ 0,08 por imagem em 1K. A estimativa da seção 4.3 se confirma: 3 takes do still a US$ 0,24 e 1 a 3 vídeos de 5 s a US$ 0,56 a 1,68.
  - **O achado dos termos (D-SG-I), que para a geração:** os Termos de Serviço do fal.ai (`https://fal.ai/legal/terms-of-service`,
    seção 6, lidos em 2026-11-06) dizem que o cliente garante ter todos os direitos sobre o que envia e que não envia material protegido
    por direito autoral sem a permissão do dono. O take 0 e o still são quadros do Digimon UP, cujos direitos não são do Matheus. Enviar
    contraria os termos do provedor. **Nenhum envio foi feito**; a decisão volta ao Matheus (D-SG-6, abaixo).
  - **A chave:** a `FAL_KEY` não está no ambiente (nem na sessão, nem como variável de usuário).
  - **O take 0:** `remaster/geracao/Agumon/still/take_0.png` (o `Idle_00` do UP a 10×, vizinho mais próximo, 940×680), mais a versão na
    caixa e a versão em fundo magenta. Custo zero.
  - **O que não rodou:** os scripts do Sprite Forge (o `forge_doctor.py` foi barrado pelo classificador de permissões da sessão); a E1 a
    E7. Gasto: US$ 0,00 (não há ledger).
  - **D-SG-6, DECIDIDA pelo Matheus em 2026-11-06: a opção (b), enviar sob a responsabilidade dele** (registro D-SG-L). Ele respondeu
    "envie b" na sessão de planejamento e confirmou nesta sessão da G2 ("Confirmo, envie"), depois de ver o achado D-SG-I. O que estava
    em jogo:
    - **Recomendação:** não enviar quadros do UP ao fal.ai. A rota que respeita os termos é a prova com arte própria (fora desta
      tarefa, seção 6), ou um provedor cujos termos o Matheus confira e aceite para esse uso.
    - **Alternativas:** (a) o Matheus pede permissão ao dono dos direitos; (b) o Matheus lê os termos e decide enviar assim mesmo, sob a
      responsabilidade dele; (c) a rota local do Codex ou do Grok, cujos termos também precisam ser lidos antes.
    - **Custo de errar:** enviar contra os termos arrisca a suspensão da conta do fal.ai e o uso do material fora do que o provedor
      permite; não enviar deixa a pergunta 1 sem resposta nesta tarefa.
  - **A E1, primeira tentativa (2026-11-06), parou por falta de saldo:**
    - **O que rodou:**
      - o `master_still.py prompt` (local);
      - o `route_media.py --dry-run`, que resolveu a rota `api:fal` com o `fal-ai/nano-banana-2/edit` a US$ 0,08 por take;
      - o `master_still.py generate --takes 3`, com `--budget-usd 5 --max-calls 8`.
    - **O resultado:** os 3 takes falharam no upload da referência, antes do pedido pago. O fal.ai respondeu "API HTTP 403: User is
      locked. Reason: Exhausted balance".
    - **O ledger** (`remaster/geracao/Agumon/forge/.forge/ledger.jsonl`, `media_ledger.py summary`): 0 chamadas, US$ 0,00.
    - **Os arquivos:** a ficha do still em `forge/refs/spec_agumon.json` e a referência em `forge/refs/agumon_up_idle0.png`, só os
      pixels de alfa 255 acima do pé, a 10× sobre magenta.
    - **Pela instrução da missão,** nenhuma outra rota foi tentada. A E1 volta a rodar depois que o Matheus puser crédito na conta.
  - **O `forge_doctor.py`, liberado pelo Matheus nesta sessão:**
    - as dependências estão OK;
    - o ffmpeg não aparece no PATH de um processo aberto antes da instalação, então a E2 passa o caminho do winget explicitamente.
  - **A E1 rodada (2026-11-06), depois do crédito no fal.ai:**
    - **A geração:** `master_still.py generate --takes 3` pela rota `api:fal` (`fal-ai/nano-banana-2/edit`), com
      `--budget-usd 5 --max-calls 8`. O ledger registra 3 chamadas pagas e **US$ 0,24**.
    - **As medidas** (`remaster/geracao/Agumon/still/master.json`, PROPOSTO), com os takes reduzidos à caixa de 94×68:

      | take | silhueta XOR | pé | fora da paleta antes do snap | distância RGB média |
      |---|---|---|---|---|
      | take 0 | 0 | 58 | 0 | 0 |
      | take 1 | 0 | 58 | 917 de 1 410 | 4,46 |
      | take 2 | 0 | 58 | 927 de 1 410 | 4,62 |
      | take 3 | 0 | 58 | 945 de 1 410 | 4,87 |

      O gerador reproduziu a silhueta do take 0 e só deslocou as cores. A escala estimada é 10,04×.
    - **O R-still** (`remaster/geracao/Agumon/revisoes/E1.md`): os 3 takes estão aprovados, e a recomendação é o take 1.
    - **A folha de contato** (`still/contato_still_x4.png`) foi enviada ao Matheus.
